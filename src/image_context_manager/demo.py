"""Offline host integration walkthrough; no model/network calls or timing claims."""
import argparse
import base64
import copy
import json
from dataclasses import replace
from pathlib import Path
from PIL import Image, ImageDraw
from . import (AssetStore, HistoricalImages, ImageUse, Lifecycle, Task,
               LOCAL_SCHEMA, RequestPlanError, apply_plan, inspect_images)


def run(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    store = AssetStore(root / "originals")
    uses = {}
    for name, color in [("draft", "white"), ("candidate", "lightblue"), ("pending", "lightyellow")]:
        path = root / (name + ".png")
        image = Image.new("RGB", (320, 100), color)
        ImageDraw.Draw(image).text((12, 12), "Synthetic " + name + " v1", fill="black")
        image.save(path)
        uses[name] = ImageUse(name, store.put(path), frozenset({Task.READ}),
                              Lifecycle.ACTIVE, "v1", name)
    uses["candidate"] = replace(uses["candidate"], tasks=frozenset({Task.COMPARE}), compare_group="review")
    uses["pending"] = replace(uses["pending"], lifecycle=Lifecycle.VERIFY)
    manager = HistoricalImages(store)

    def attachment(use, data):
        return {"type": "input_image", "image_url": "data:" + use.asset.mime + ";base64," + base64.b64encode(data).decode()}

    canonical = [{"role": "user", "content": [{"type": "input_text", "text": "Host-owned synthetic review task"}]}]
    for use in uses.values():
        manager.register(use)
        canonical[0]["content"].append(attachment(use, manager.recall(use)))
    before = copy.deepcopy(canonical)
    manager.bind_request(inspect_images(canonical))
    plan, _ = manager.plan("initial", uses, current_start=0)
    initial = apply_plan(canonical, plan, generation="initial")
    assert len(inspect_images(initial)) == 3  # Current images cannot retire.

    # An explicitly declared completed host task, NOT a model/OCR result.
    manager.commit(uses["draft"], {"review_status": "host_review_finished"},
                   "synthetic host task fixture; not model-read", "demo-turn-1")
    states = dict(uses)
    states["draft"] = replace(uses["draft"], lifecycle=Lifecycle.COMPLETED)
    plan, decisions = manager.plan("next", states, current_start=len(manager.entries))
    retired = apply_plan(canonical, plan, generation="next")
    assert [r["ordinal"] for r in plan["replacements"]] == [0]
    assert len(inspect_images(retired)) == 2
    assert retired[0]["content"][1]["type"] == "input_text"
    assert "host_review_finished" in retired[0]["content"][1]["text"]
    assert canonical == before  # Canonical history preserved for later requests.

    # A later comparison restores the original from canonical history.
    compare_states = dict(states)
    compare_states["draft"] = replace(states["draft"], lifecycle=Lifecycle.ACTIVE,
                                       tasks=frozenset({Task.COMPARE}), compare_group="review")
    compare_plan, _ = manager.plan("compare", compare_states)
    comparison = apply_plan(canonical, compare_plan, generation="compare")
    assert len(inspect_images(comparison)) == 3

    # Host can abort source/version drift instead of sending a guessed substitute.
    wrong_version = dict(states, draft=replace(states["draft"], version="v2"))
    wrong_source = dict(states, draft=replace(states["draft"], asset=uses["candidate"].asset))
    for wrong in [wrong_version, wrong_source]:
        protected_plan, _ = manager.plan("drift", wrong)
        assert protected_plan["replacements"] == []
    corrupt_plan = copy.deepcopy(plan)
    corrupt_plan["replacements"][0]["expected_sha256"] = "0" * 64
    try:
        apply_plan(canonical, corrupt_plan, generation="next")
    except RequestPlanError:
        rejected_bad_hash = True
    else:
        raise AssertionError("Source mismatch was not rejected")

    # Explicit recall resolves ORIGINAL bytes, then registers a fresh occurrence.
    original = manager.recall(uses["draft"])
    assert original == (root / "draft.png").read_bytes()
    assert AssetStore(root / "originals").recall(store.resolve(uses["draft"].asset.sha256)) == original
    current_start = len(manager.entries)
    recalled_use = replace(uses["draft"], lifecycle=Lifecycle.RECALL)
    manager.register(recalled_use)
    canonical.append({"role": "user", "content": [attachment(recalled_use, original)]})
    manager.bind_request(inspect_images(canonical))
    recall_plan, _ = manager.plan("recall", states, current_start=current_start)
    recalled = apply_plan(canonical, recall_plan, generation="recall")
    assert [r["ordinal"] for r in recall_plan["replacements"]] == [0]
    assert len(inspect_images(recalled)) == 3
    assert inspect_images(canonical)[0]["url_sha256"] == inspect_images(canonical)[3]["url_sha256"]
    assert recalled[-1]["content"][0] == attachment(recalled_use, original)

    # Corruption demonstration uses a separate store; never damages the live one.
    broken = AssetStore(root / "corruption-fixture")
    asset = broken.put(root / "draft.png")
    (broken.root / (asset.sha256 + ".original")).write_bytes(b"synthetic corruption")
    try:
        broken.recall(asset)
    except ValueError:
        rejected_corrupt_original = True
    else:
        raise AssertionError("Corrupt original was not rejected")
    requests = {"schema": LOCAL_SCHEMA, "initial": initial, "retired": retired,
                "comparison": comparison, "recall": recalled}
    (root / "requests.json").write_text(json.dumps(requests, indent=2) + "\n")
    report = {"scope": "offline local request construction only; no model/network/latency evidence",
              "receipt_source": "explicit synthetic host completion, not automatic vision/OCR",
              "image_counts": {k: len(inspect_images(v)) for k,v in requests.items() if k != "schema"},
              "retired_ordinals": [r["ordinal"] for r in plan["replacements"]],
              "protected_comparison_and_pending": True, "canonical_history_preserved": True,
              "wrong_version_preserved": True, "wrong_source_preserved": True,
              "bad_request_hash_rejected": rejected_bad_hash,
              "original_recalled_byte_exact": True, "persistent_store_reopened": True,
              "corrupt_original_rejected": rejected_corrupt_original, "decisions": decisions}
    (root / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New output directory; existing paths are not overwritten")
    args = parser.parse_args()
    print(json.dumps(run(args.out), indent=2))


if __name__ == "__main__":
    main()
