import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from PIL import Image
from image_context_manager import AssetStore, ImageUse, Lifecycle, Task
from image_context_manager.history import HistoricalImages


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name); Image.new('RGB',(20,20)).save(root/'a.png')
        self.manager=HistoricalImages(AssetStore(root/'store'))
        asset=self.manager.store.put(root/'a.png')
        self.use=ImageUse('a',asset,frozenset({Task.READ}),Lifecycle.COMPLETED,'v1','draft')
        self.manager.register(self.use)
        self.manager.bind_request([{'ordinal':0,'url_sha256':'a'*64}])
        self.manager.commit(self.use,{'code':'MODEL-READ'},'model','turn-1')

    def test_completed_result_retires_and_recall_is_exact(self):
        plan, _=self.manager.plan('t2',{'a':self.use})
        self.assertEqual([r['ordinal'] for r in plan['replacements']],[0])
        self.assertEqual(self.manager.recall(self.use),self.manager.store.recall(self.use.asset))
        self.assertIn('MODEL-READ',plan['replacements'][0]['reference'])

    def test_current_comparison_uncertain_and_pending_evidence_are_preserved(self):
        for use in [replace(self.use,lifecycle=Lifecycle.ACTIVE),replace(self.use,lifecycle=Lifecycle.VERIFY),
                    replace(self.use,lifecycle=Lifecycle.RECALL),replace(self.use,tasks=frozenset({Task.COMPARE})),
                    replace(self.use,confidence=.5),replace(self.use,required=True),replace(self.use,compare_group='x')]:
            self.assertEqual(self.manager.plan('t2',{'a':use})[0]['replacements'],[])
        self.assertEqual(self.manager.plan('t2',{'a':self.use},current_start=0)[0]['replacements'],[])
        self.assertEqual(self.manager.plan('t2',{'a':self.use},protected_ids=['a'])[0]['replacements'],[])

    def test_conflicting_results_and_source_drift_fail_conservatively(self):
        self.manager.commit(self.use,{'code':'CONFLICT'},'model','turn-2')
        self.assertEqual(self.manager.plan('t2',{'a':self.use})[0]['replacements'],[])
        with self.assertRaises(ValueError): self.manager.bind_request([{'ordinal':0,'url_sha256':'b'*64}])
        with self.assertRaises(ValueError): self.manager.bind_request([])

    def test_version_and_stage_drift_preserve_originals(self):
        for changed in [replace(self.use,version='v2'),replace(self.use,stage='submitted')]:
            self.assertEqual(self.manager.plan('t2',{'a':changed})[0]['replacements'],[])
        self.manager.commit(replace(self.use,version='v2'),{'code':'MODEL-READ'},'model','turn-2')
        self.assertEqual(self.manager.plan('t3',{'a':self.use})[0]['replacements'],[])
