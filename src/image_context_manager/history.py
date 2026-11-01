"""Conservative request-copy retirement plans; canonical history is never edited.

The host adapter checks image ordinals AND hashes against real request assembly.
Receipts are actual completed task outputs, never expected evaluation answers.
"""
import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Optional
from .core import AssetStore, ImageUse, Lifecycle, Task


@dataclass(frozen=True)
class Receipt:
    source_sha256: str
    version: str
    stage: str
    fields: dict
    producer: str
    turn_id: str
    validation: str = 'structured_completed_task; not independent visual truth verification'


class HistoricalImages:
    def __init__(self, store: AssetStore):
        self.store = store
        self.entries = []
        self.receipts: Dict[str, Receipt] = {}
        self.uncertain = set()

    def register(self, use: ImageUse):
        """Register each real attachment occurrence, including repeated recalls."""
        self.entries.append({'use': use, 'url_sha256': None})

    def bind_request(self, before_images):
        if len(before_images) != len(self.entries):
            raise ValueError('Actual request image count differs from registered occurrences')
        for index, (entry, image) in enumerate(zip(self.entries, before_images)):
            if image['ordinal'] != index:
                raise ValueError('Actual request image ordinal drift')
            old = entry['url_sha256']
            if old is not None and old != image['url_sha256']:
                raise ValueError('Actual request image content changed')
            entry['url_sha256'] = image['url_sha256']

    def commit(self, use: ImageUse, fields: dict, producer: str, turn_id: str):
        """Commit actual schema-checked task result. Conflicts preserve originals.

        Caller owns task completion; this is not an OCR correctness oracle.
        Narrow fields must be sufficient for subsequent read/state tasks.
        """
        if not fields or not producer or not turn_id or not all(isinstance(v, str) and v for v in fields.values()):
            raise ValueError('A nonempty structured result and provenance are required')
        old = self.receipts.get(use.id)
        if old and (old.source_sha256 != use.asset.sha256 or old.version != use.version or old.stage != use.stage or any(old.fields.get(k, v) != v for k, v in fields.items())):
            self.uncertain.add(use.id)
            return
        merged = dict(old.fields) if old else {}
        merged.update(fields)
        self.receipts[use.id] = Receipt(use.asset.sha256, use.version, use.stage, merged, producer, turn_id)

    def plan(self, generation: str, states: Dict[str, ImageUse], protected_ids=(), current_start: Optional[int] = None, enabled=True):
        protected = set(protected_ids)
        replacements, decisions = [], []
        for ordinal, entry in enumerate(self.entries):
            original_use = entry['use']
            use = states.get(original_use.id, original_use)
            receipt = self.receipts.get(use.id)
            reason = 'active, protected, uncertain or missing sufficient completed task result'
            eligible = (enabled and ordinal < (current_start if current_start is not None else len(self.entries))
                        and use.id not in protected and use.id not in self.uncertain
                        and use.lifecycle in {Lifecycle.COMPLETED, Lifecycle.INVALIDATED}
                        and not use.required and use.confidence >= .9
                        and not (use.tasks & {Task.QUALITY, Task.COMPARE, Task.RELATION, Task.ACTION})
                        and use.compare_group is None and receipt is not None
                        and use.asset.sha256 == original_use.asset.sha256
                        and use.version == original_use.version and use.stage == original_use.stage
                        and receipt.source_sha256 == original_use.asset.sha256
                        and receipt.version == original_use.version and receipt.stage == original_use.stage
                        and entry['url_sha256'] is not None)
            if eligible:
                reference = {'kind': 'retired_image_reference', 'source_sha256': receipt.source_sha256,
                             'id': use.id, 'version': receipt.version, 'stage': receipt.stage,
                             'related_version': use.related_version, 'lifecycle': use.lifecycle.value,
                             'valid_for': [t.value for t in use.tasks], 'observation': receipt.fields,
                             'producer': receipt.producer, 'turn_id': receipt.turn_id,
                             'validation': receipt.validation,
                             'recall': 'Harness resolves source_sha256 from external original store; reference is not a URL.'}
                replacements.append({'ordinal': ordinal, 'expected_sha256': entry['url_sha256'],
                                     'reference': '[Image data reference, not instructions] ' + json.dumps(reference, sort_keys=True)})
                reason = 'completed task result sufficient; original retained externally'
            decisions.append({'ordinal': ordinal, 'id': original_use.id, 'mode': 'reference' if eligible else 'original', 'reason': reason})
        return {'generation': generation, 'expected_images': len(self.entries), 'replacements': replacements}, decisions

    def recall(self, use: ImageUse):
        """Original bytes, hash checked by store; caller sends a fresh attachment."""
        data = self.store.recall(use.asset)
        if hashlib.sha256(data).hexdigest() != use.asset.sha256:
            raise ValueError('Recall integrity mismatch')
        return data
