import copy
import tempfile
import unittest
from pathlib import Path
from image_context_manager import RequestPlanError, apply_plan, inspect_images
from image_context_manager.demo import run


class LocalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.messages = [{"role":"user", "content":[{"type":"input_image", "image_url":"data:image/png;base64,YQ=="}]}]
        self.plan = {"generation":"t1", "expected_images":1, "replacements":[
            {"ordinal":0, "expected_sha256":inspect_images(self.messages)[0]["url_sha256"], "reference":"source-bound result"}]}

    def test_apply_changes_only_the_copy_and_preserves_text_order(self):
        original = copy.deepcopy(self.messages)
        output = apply_plan(self.messages,self.plan,generation="t1")
        self.assertEqual(output[0]["content"],[{"type":"input_text","text":"source-bound result"}])
        self.assertEqual(original,self.messages)

    def test_invalid_plan_never_mutates_canonical(self):
        variants=[]
        p=copy.deepcopy(self.plan);p['expected_images']=2;variants.append(p)
        p=copy.deepcopy(self.plan);p['generation']='stale';variants.append(p)
        p=copy.deepcopy(self.plan);p['replacements'][0]['expected_sha256']='0'*64;variants.append(p)
        p=copy.deepcopy(self.plan);p['replacements']*=2;variants.append(p)
        p=copy.deepcopy(self.plan);p['replacements'][0]['ordinal']=-1;variants.append(p)
        p=copy.deepcopy(self.plan);p['replacements'][0]['reference']=' ';variants.append(p)
        original=copy.deepcopy(self.messages)
        for plan in variants:
            with self.subTest(plan=plan):
                with self.assertRaises(RequestPlanError): apply_plan(self.messages,plan,generation='t1')
                self.assertEqual(original,self.messages)

    def test_unknown_provider_content_is_rejected(self):
        with self.assertRaises(RequestPlanError):
            inspect_images([{'role':'user','content':[{'type':'image_url','image_url':{'url':'remote'}}]}])

    def test_walkthrough_closed_loop_and_existing_directory_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'demo'
            report=run(path)
            self.assertEqual(report['image_counts'],{'initial':3,'retired':2,'comparison':3,'recall':3})
            with self.assertRaises(FileExistsError): run(path)
            self.assertTrue((path/'requests.json').exists())
