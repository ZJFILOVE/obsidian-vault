#!/usr/bin/env python3
"""Synthetic read-only status and routing regressions."""
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_status as status
import test_runtime as fixtures
from test_preflight import snapshot


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def ready(self):
        with contextlib.redirect_stdout(io.StringIO()):
            fixtures.make_project(str(self.root))
        for name in ('source-map.md', 'dependency-map.md'):
            (self.root / name).write_text('Synthetic fixture')
        fixtures.seed_all(str(self.root))
        self.run = fixtures_run = json.loads((self.root / '.pd/run.json').read_text())
        fixtures_run['tasks'] = {s: {'status': 'checked', 'input_digest': status.pdstate.current_input_digest(str(self.root), s, {})} for s in fixtures_run['slices']}
        self.save_run()

    def save_run(self):
        (self.root / '.pd/run.json').write_text(json.dumps(self.run))

    def inspect(self):
        before = snapshot(self.root)
        data = status.inspect(self.root)
        self.assertEqual(snapshot(self.root), before)
        return data

    def test_missing_directory_and_empty_project(self):
        missing = self.root / 'missing'
        result = subprocess.run([sys.executable, '-B', status.__file__, str(missing), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(missing.exists())
        self.assertEqual(self.inspect()['route'], 'new/planning')

    def test_routing_technical_acceptance_and_delivery(self):
        self.ready()
        self.assertEqual(self.inspect()['route'], 'delivery_validation')
        shutil.rmtree(self.root / '.pd/acceptance')
        self.assertEqual(self.inspect()['route'], 'preflight_and_acceptance')
        (self.root / '.pd/reports/build.json').unlink()
        self.assertEqual(self.inspect()['route'], 'technical')

    def test_running_legacy_contract_is_not_migrated(self):
        self.ready()
        self.run['schema_version'] = 1
        self.run['tasks']['sec1']['status'] = 'running'
        self.save_run()
        data = self.inspect()
        self.assertEqual(data['route'], 'writing')
        self.assertIn('在途执行者', data['next_action'])
        self.assertEqual(json.loads((self.root / '.pd/run.json').read_text())['schema_version'], 1)

    def test_checkpoint_artifacts_and_task_staleness(self):
        self.ready()
        artifact = self.root / '.pd/checkpoint-marker'
        artifact.write_text('version one')
        data = self.inspect()
        checkpoint = {'schema_version': 1, 'run_id': self.run['run_id'], 'input_digest': data['input_digest'], 'stage': 'delivery', 'artifacts': {'.pd/checkpoint-marker': status.evidence.sha256_file(str(artifact))}}
        (self.root / '.pd/pipeline-state.json').write_text(json.dumps(checkpoint))
        self.assertTrue(self.inspect()['checkpoint']['bindings_match'])
        artifact.write_text('changed')
        self.assertFalse(self.inspect()['checkpoint']['bindings_match'])
        (self.root / 'source-map.md').write_text('changed source')
        data = self.inspect()
        self.assertEqual(data['route'], 'writing')
        self.assertTrue(all(task['stale'] for task in data['tasks']))

    def test_acceptance_qid_coverage_and_json_cli(self):
        self.ready()
        path = self.root / '.pd/acceptance/chapter.json'
        rec = json.loads(path.read_text())
        rec['reviewed_qids'] = []
        path.write_text(json.dumps(rec))
        before = snapshot(self.root)
        result = subprocess.run([sys.executable, '-B', status.__file__, str(self.root), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['route'], 'preflight_and_acceptance')
        self.assertEqual(snapshot(self.root), before)


if __name__ == '__main__':
    unittest.main()
