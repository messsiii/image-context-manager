import base64
import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from PIL import Image
from image_context_manager import AssetStore, Budget, Event, ImageUse, Lifecycle, Observation, Policy, RequestAssembler, Task


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        path = self.root / "sample.png"
        Image.new("RGB", (300, 200), "blue").save(path)
        self.store = AssetStore(self.root / "store")
        self.asset = self.store.put(path)
        self.use = ImageUse("a", self.asset, frozenset({Task.READ}), Lifecycle.ACTIVE, "v1", "draft")
        self.assembler = RequestAssembler(self.store)

    def assemble(self, use, baseline=False, budget=None):
        return self.assembler.assemble([Event("user", "read", ("a",))], {"a": use}, budget, baseline)

    def mode(self, use, pressure=True):
        return Policy().choose(use, pressure).mode

    def test_original_recall_after_restart_and_integrity(self):
        reopened = AssetStore(self.store.root)
        asset = reopened.resolve(self.asset.sha256)
        self.assertEqual(reopened.recall(asset), self.store.recall(self.asset))
        (self.store.root / (asset.sha256 + ".original")).write_bytes(b"broken")
        with self.assertRaises(ValueError):
            reopened.recall(asset)

    def test_content_address_rejects_traversal(self):
        with self.assertRaises(ValueError):
            self.store.resolve("../secret")

    def test_history_rebuild_removes_and_restores_old_original(self):
        old = self.assemble(self.use)
        changed = self.assemble(replace(self.use, lifecycle=Lifecycle.INVALIDATED))
        restored = self.assemble(replace(self.use, lifecycle=Lifecycle.RECALL))
        self.assertTrue(any(c["type"] == "image" for c in old.payload["messages"][0]["content"]))
        self.assertFalse(any(c["type"] == "image" for c in changed.payload["messages"][0]["content"]))
        self.assertEqual(old.wire, restored.wire.replace(b'"recalled"', b'"active"'))

    def test_protected_evidence_survives_tiny_budget(self):
        for use in [replace(self.use, tasks=frozenset({Task.COMPARE})),
                    replace(self.use, lifecycle=Lifecycle.VERIFY),
                    replace(self.use, confidence=0.5), replace(self.use, required=True)]:
            result = self.assemble(use, budget=Budget(1))
            self.assertEqual(result.decisions[0]["mode"], "original")
            self.assertTrue(result.over_budget)

    def test_compare_group_protects_invalidated_image(self):
        self.assertEqual(self.mode(replace(self.use, lifecycle=Lifecycle.INVALIDATED, compare_group="x")), "original")

    def test_quality_and_spatial_tasks_keep_original(self):
        for task in [Task.QUALITY, Task.RELATION]:
            self.assertEqual(self.mode(replace(self.use, tasks=frozenset({task}))), "original")

    def test_thumbnail_requires_completed_and_pressure(self):
        completed = replace(self.use, lifecycle=Lifecycle.COMPLETED)
        self.assertEqual(self.mode(completed), "thumbnail")
        self.assertEqual(self.mode(completed, False), "original")
        self.assertEqual(self.mode(self.use), "original")

    def test_roi_exact_native_pixels_and_bounds(self):
        crop_use = replace(self.use, roi=(20, 30, 60, 80), roi_verified=True, region_only=True)
        result = self.assemble(crop_use)
        item = result.payload["messages"][0]["content"][-1]
        image = Image.open(io.BytesIO(base64.b64decode(item["data"])))
        self.assertEqual(image.size, (40, 50))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 255))
        with self.assertRaises(ValueError):
            self.assemble(replace(crop_use, roi=(0, 0, 999, 999)))
        self.assertEqual(self.mode(replace(crop_use, roi_verified=False)), "original")

    def test_text_replacement_requires_verified_source_bound_result(self):
        observation = Observation(self.asset.sha256, "test-verified-annotation", 1, {"state": "draft"}, True)
        use = replace(self.use, lifecycle=Lifecycle.COMPLETED, observation=observation, text_sufficient=True)
        self.assertEqual(self.mode(use), "text")
        for obs in [replace(observation, verified=False), replace(observation, confidence=0.9), replace(observation, source_sha256="0" * 64)]:
            self.assertNotEqual(self.mode(replace(use, observation=obs)), "text")
        self.assertNotEqual(self.mode(replace(use, lifecycle=Lifecycle.ACTIVE)), "text")

    def test_backend_version_binding_required(self):
        with self.assertRaises(ValueError):
            replace(self.use, stage="backend")

    def test_invalid_confidence_and_budget(self):
        for confidence in [float("nan"), -1, 2]:
            with self.assertRaises(ValueError):
                replace(self.use, confidence=confidence)
        with self.assertRaises(ValueError):
            Budget(0)

    def test_wire_bytes_are_actual_utf8(self):
        result = self.assemble(self.use)
        self.assertEqual(json.loads(result.wire), result.payload)
        self.assertGreater(len(result.wire), self.asset.bytes)


if __name__ == "__main__":
    unittest.main()
