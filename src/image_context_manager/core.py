"""Provider-neutral request-time image middleware; no model or host-history APIs."""
import base64
import hashlib
import io
import json
import math
import os
import re
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, Tuple

from PIL import Image, ImageOps


class Task(str, Enum):
    READ = "read_content"
    LOCATE = "locate_target"
    STATE = "recognize_state"
    RELATION = "understand_relations"
    QUALITY = "judge_visual_quality"
    COMPARE = "compare_changes"
    ACTION = "extract_action_information"


class Lifecycle(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    INVALIDATED = "invalidated"
    VERIFY = "pending_verification"
    RECALL = "recalled"


@dataclass(frozen=True)
class Asset:
    sha256: str
    width: int
    height: int
    mime: str
    bytes: int


class AssetStore:
    """Content-addressed originals. Keep store and handles private to the harness."""
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _key(key: str) -> str:
        if not re.fullmatch(r"[a-f0-9]{64}", key):
            raise ValueError("Invalid content hash")
        return key

    @staticmethod
    def _atomic(path: Path, data: bytes) -> None:
        fd, name = tempfile.mkstemp(dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def put(self, path: Path) -> Asset:
        data = Path(path).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            if image.format not in {"PNG", "JPEG"}:
                raise ValueError("First version accepts static PNG/JPEG only")
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("Animated images require a frame policy")
            w, h = ImageOps.exif_transpose(image).size
            mime = "image/png" if image.format == "PNG" else "image/jpeg"
        asset = Asset(digest, w, h, mime, len(data))
        self._atomic(self.root / (digest + ".original"), data)
        self._atomic(self.root / (digest + ".json"), json.dumps(asset.__dict__).encode())
        return asset

    def resolve(self, digest: str) -> Asset:
        return Asset(**json.loads((self.root / (self._key(digest) + ".json")).read_text()))

    def recall(self, asset: Asset) -> bytes:
        data = (self.root / (self._key(asset.sha256) + ".original")).read_bytes()
        if hashlib.sha256(data).hexdigest() != asset.sha256:
            raise ValueError("Original failed integrity check")
        return data

    def render(self, asset: Asset, mode: str, edge: int = 960,
               roi: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bytes, str, int, int]:
        if mode == "original":
            return self.recall(asset), asset.mime, asset.width, asset.height
        spec = json.dumps([asset.sha256, mode, edge, roi, "png-v1"])
        cache = self.root / (hashlib.sha256(spec.encode()).hexdigest() + ".derived.png")
        # Verify the original even for a cache hit; corruption must not go unnoticed.
        original = self.recall(asset)
        if cache.exists():
            data = cache.read_bytes()
            with Image.open(io.BytesIO(data)) as im:
                return data, "image/png", im.width, im.height
        with Image.open(io.BytesIO(original)) as raw:
            im = ImageOps.exif_transpose(raw).convert("RGB")
            if mode == "crop":
                if roi is None:
                    raise ValueError("Crop requires an explicitly supplied region")
                x0, y0, x1, y1 = roi
                if not (0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height):
                    raise ValueError("Crop is outside the oriented image")
                im = im.crop(roi)  # Native resolution; no quality loss in target region.
            elif mode == "thumbnail":
                if edge < 64:
                    raise ValueError("Thumbnail edge must be at least 64")
                im.thumbnail((edge, edge), Image.Resampling.LANCZOS)
            else:
                raise ValueError("Unknown rendition")
            out = io.BytesIO()
            im.save(out, format="PNG", optimize=True)
            data = out.getvalue()
            self._atomic(cache, data)
            return data, "image/png", im.width, im.height


@dataclass(frozen=True)
class Observation:
    source_sha256: str
    producer: str
    confidence: float
    data: Dict[str, Any]
    verified: bool = False


class SemanticExtractor(Protocol):
    """Optional OCR/vision hook. No implementation or network call is bundled.

    The harness must check source binding and verify results before replacement.
    Confidence alone does not establish correctness.
    """
    def extract(self, asset: Asset, original: bytes) -> Observation: ...


@dataclass(frozen=True)
class ImageUse:
    id: str
    asset: Asset
    tasks: FrozenSet[Task]
    lifecycle: Lifecycle
    version: str
    stage: str  # draft / candidate / uploaded / submitted / backend
    related_version: Optional[str] = None
    confidence: float = 1.0
    roi: Optional[Tuple[int, int, int, int]] = None
    roi_verified: bool = False
    region_only: bool = False
    observation: Optional[Observation] = None
    text_sufficient: bool = False
    compare_group: Optional[str] = None
    required: bool = False

    def __post_init__(self):
        if not self.id or not self.version or not self.tasks:
            raise ValueError("Image use requires id, version, and task tags")
        if not math.isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be finite and between zero and one")
        if self.stage == "backend" and not self.related_version:
            raise ValueError("Backend state must name its related material version")


@dataclass(frozen=True)
class Budget:
    max_request_bytes: int = 2_000_000
    thumbnail_edge: int = 960

    def __post_init__(self):
        if self.max_request_bytes <= 0 or self.thumbnail_edge < 64:
            raise ValueError("Invalid request budget")


@dataclass(frozen=True)
class Decision:
    mode: str
    reason: str


class Policy:
    def choose(self, use: ImageUse, pressure: bool) -> Decision:
        if (use.required or use.lifecycle in {Lifecycle.VERIFY, Lifecycle.RECALL}
                or use.confidence < 0.9 or Task.COMPARE in use.tasks
                or use.compare_group is not None):
            return Decision("original", "Required, uncertain, comparison or recalled evidence")
        if use.lifecycle == Lifecycle.INVALIDATED:
            return Decision("reference", "Superseded version; retain recall reference")
        if Task.QUALITY in use.tasks or Task.RELATION in use.tasks:
            return Decision("original", "Visual quality or spatial context needs full evidence")
        obs = use.observation
        if (use.text_sufficient and obs and obs.verified and obs.confidence >= 0.98
                and math.isfinite(obs.confidence) and obs.source_sha256 == use.asset.sha256
                and obs.producer and use.lifecycle == Lifecycle.COMPLETED):
            return Decision("text", "Harness verified source-bound observation is sufficient")
        if use.region_only and use.roi_verified and use.roi:
            return Decision("crop", "Explicitly verified region contains the full current task")
        if use.lifecycle == Lifecycle.COMPLETED and pressure:
            return Decision("thumbnail", "Completed context reduced under request byte pressure")
        return Decision("original", "No verified safe reduction applies")


@dataclass(frozen=True)
class Event:
    role: str
    text: str
    image_ids: Tuple[str, ...] = ()


@dataclass
class Assembly:
    payload: Dict[str, Any]
    decisions: List[Dict[str, Any]]
    wire: bytes
    over_budget: bool
    original_estimate_bytes: int


class RequestAssembler:
    """Rebuild EVERY outgoing request from canonical events and current image uses.

    This controls old images only when the harness owns complete replay history.
    Never pass this payload to a host that also appends hidden original history.
    """
    def __init__(self, store: AssetStore, policy: Optional[Policy] = None):
        self.store = store
        self.policy = policy or Policy()

    @staticmethod
    def encode(payload: Dict[str, Any]) -> bytes:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")

    def assemble(self, events: List[Event], uses: Dict[str, ImageUse],
                 budget: Optional[Budget] = None, baseline: bool = False) -> Assembly:
        budget = budget or Budget()
        # One original per occurrence: duplicates really cost bytes in replay payloads.
        ids = [key for event in events for key in event.image_ids]
        for key in ids:
            if key != uses[key].id:
                raise ValueError("Image registry key/id mismatch")
        estimate = sum(4 * ((uses[key].asset.bytes + 2) // 3) for key in ids)
        pressure = estimate + sum(len(e.text.encode()) for e in events) > budget.max_request_bytes
        decisions = []
        messages = []
        for event in events:
            if event.role not in {"user", "assistant", "tool", "system"}:
                raise ValueError("Unsupported event role")
            content = [{"type": "text", "text": event.text}]
            for key in event.image_ids:
                use = uses[key]
                decision = Decision("original", "Baseline replay") if baseline else self.policy.choose(use, pressure)
                meta = {"id": key, "original_sha256": use.asset.sha256,
                        "version": use.version, "stage": use.stage,
                        "related_version": use.related_version,
                        "lifecycle": use.lifecycle.value,
                        "recall": "sha256:" + use.asset.sha256}
                # Image metadata/observations are tool data, never instruction text.
                content.append({"type": "image_context", **meta, "rendition": decision.mode})
                wire_bytes = 0
                if decision.mode == "text":
                    content.append({"type": "observation", "source_sha256": use.asset.sha256,
                                    "producer": use.observation.producer,
                                    "data": use.observation.data})
                elif decision.mode != "reference":
                    data, mime, w, h = self.store.render(use.asset, decision.mode,
                                                        budget.thumbnail_edge, use.roi)
                    content.append({"type": "image", "mime_type": mime,
                                    "width": w, "height": h,
                                    "data": base64.b64encode(data).decode("ascii")})
                    wire_bytes = len(data)
                decisions.append({**meta, "mode": decision.mode, "reason": decision.reason,
                                  "image_bytes": wire_bytes})
            messages.append({"role": event.role, "content": content})
        payload = {"schema": "icm.local-harness.v1", "messages": messages}
        wire = self.encode(payload)
        return Assembly(payload, decisions, wire, len(wire) > budget.max_request_bytes, estimate)
