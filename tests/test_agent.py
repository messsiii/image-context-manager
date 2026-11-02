import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from image_context_manager.agent import Workspace, install
from image_context_manager.cli import main


class AgentToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.image = self.root / 'input.png'
        Image.effect_noise((1000, 800), 70).convert('RGB').save(self.image)
        self.ws = Workspace(self.root / 'workspace')
        with self.ws.transaction() as state:
            self.item = self.ws.add(state, 'draft', self.image, ['read_content'], 'v1', 'draft')

    def result(self):
        return dict(self.item, fields={'title': 'Example'}, producer='test', verified=True, sufficient=True)

    def test_persistence_and_original_integrity(self):
        ws = Workspace(self.ws.root)
        with ws.transaction() as state:
            self.assertEqual(state['draft'], self.item)
            output = ws.prepare(state['draft'])
        self.assertEqual(Path(output['path']).read_bytes(), self.image.read_bytes())
        (ws.store.root / (self.item['source_sha256'] + '.original')).write_bytes(b'broken')
        with self.assertRaises(ValueError):
            ws.prepare(self.item)

    def test_compression_and_small_image_nonincrease(self):
        output = self.ws.prepare(self.item, 'compress', edge=500, allow_lossy=True, max_bytes=1)
        self.assertLess(output['bytes'], output['original_bytes'])
        self.assertFalse(output['budget_met'])
        self.assertEqual(output['coordinates']['scale'], [2, 2])
        small = self.root / 'small.png'
        Image.new('RGB', (10, 10)).save(small)
        with self.ws.transaction() as state:
            item = self.ws.add(state, 'small', small, ['read_content'], 'v1', 'draft')
        self.assertLessEqual(self.ws.prepare(item, 'compress', allow_lossy=True)['bytes'], small.stat().st_size)

    def test_verified_crop_and_alpha(self):
        with self.assertRaises(ValueError):
            self.ws.prepare(self.item, 'crop', roi=[0, 0, 20, 20])
        output = self.ws.prepare(self.item, 'crop', roi=[10, 20, 110, 120], region_verified=True)
        with Image.open(output['path']) as cropped, Image.open(self.image) as original:
            self.assertEqual(cropped.tobytes(), original.crop((10, 20, 110, 120)).tobytes())
        self.assertEqual(output['coordinates']['origin'], [10, 20])
        alpha = self.root / 'alpha.png'
        Image.new('RGBA', (100, 100), (30, 50, 70, 90)).save(alpha)
        with self.ws.transaction() as state:
            item = self.ws.add(state, 'alpha', alpha, ['read_content'], 'v1', 'draft')
        output = self.ws.prepare(item, 'compress', allow_lossy=True)
        with Image.open(output['path']) as im:
            self.assertEqual(im.getpixel((0, 0))[3], 90)

    def test_result_binding_and_conflicts(self):
        with self.ws.transaction() as state:
            wrong = dict(self.result(), source_sha256='0'*64)
            with self.assertRaises(ValueError):
                self.ws.record(state, 'draft', wrong)
            self.ws.record(state, 'draft', self.result())
            state['draft']['lifecycle'] = 'completed'
            self.assertEqual(self.ws.prepare(state['draft'])['mode'], 'text')
            self.ws.record(state, 'draft', dict(self.result(), fields={'title': 'Conflicting'}))
            self.assertEqual(self.ws.prepare(state['draft'])['mode'], 'original')

    def test_protected_tasks_and_incomplete_results(self):
        for task in ['judge_visual_quality', 'compare_changes', 'understand_relations', 'extract_action_information']:
            item = dict(self.item, tasks=[task])
            with self.assertRaises(ValueError):
                self.ws.prepare(item, 'compress', allow_lossy=True)
        with self.assertRaises(ValueError):
            self.ws.prepare(self.item, 'text')
        with self.ws.transaction():
            with self.assertRaises(ValueError):
                with self.ws.transaction():
                    pass

    def test_install_both_and_refuse_overwrite(self):
        project = self.root / 'project with spaces'
        output = install(project, 'both')
        self.assertEqual(len(output['files']), 4)
        skill = project / '.agents/skills/image-context-manager'
        self.assertTrue((skill / 'scripts/icm.py').exists())
        self.assertTrue((skill / '.runtime.json').exists())
        with self.assertRaises(ValueError):
            install(project, 'both')
        self.assertTrue((skill / 'SKILL.md').exists())

    def test_cli_handoff_and_state_task_reset(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(['--workspace', str(self.ws.root), 'delegate', 'draft', '--goal', 'Read title'])
        self.assertEqual(code, 0)
        handoff = json.loads(buf.getvalue())
        self.assertTrue(Path(handoff['handoff']).exists())
        self.assertEqual(handoff['images'][0]['source_sha256'], self.item['source_sha256'])
        with self.ws.transaction() as state:
            self.ws.record(state, 'draft', self.result())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--workspace', str(self.ws.root), 'state', 'draft', 'active', '--task', 'compare_changes']), 0)
        with self.ws.transaction() as state:
            self.assertIsNone(state['draft']['result'])

    def test_pending_handoffs_remain_independent(self):
        outputs = []
        for goal in ['Read title', 'Check status']:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(main(['--workspace', str(self.ws.root), 'delegate',
                                       'draft', '--goal', goal]), 0)
            outputs.append(json.loads(buf.getvalue()))
        self.assertNotEqual(outputs[0]['handoff'], outputs[1]['handoff'])
        for output in outputs:
            saved = json.loads(Path(output['handoff']).read_text())
            self.assertEqual(saved['goal'], output['goal'])
            self.assertEqual(saved['images'], output['images'])

    def test_record_rejects_nonobject_json_without_state_changes(self):
        before = (self.ws.root / 'state.json').read_bytes()
        result_file = self.root / 'result.json'
        for value in [[], None, 'text', 42, True]:
            with self.subTest(value=value):
                result_file.write_text(json.dumps(value))
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = main(['--workspace', str(self.ws.root), 'record',
                                 'draft', '--file', str(result_file)])
                self.assertEqual(code, 2)
                self.assertIn('JSON object', json.loads(buf.getvalue())['error'])
                self.assertEqual((self.ws.root / 'state.json').read_bytes(), before)
