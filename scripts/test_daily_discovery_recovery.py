"""Isolated recovery fixtures; never require a live publication to stay absent."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import discovery_recovery as d
import publication_bundle as b
import publication_recovery as r

SOURCE = Path(__file__).resolve().parents[1]


def put(root, path, data):
    target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data if isinstance(data, bytes) else data.encode())


def commit(root):
    d.git(root, 'add', '.')
    d.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')


class DiscoveryRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'; self.root.mkdir()
        d.git(self.root, 'init', '-q')
        self.raw = d.git(SOURCE, 'cat-file', 'blob', d.BAD_BLOB)
        put(self.root, d.TRANSACTION, self.raw)
        put(self.root, d.FAILURE, d.git(SOURCE, 'cat-file', 'blob', d.FAILURE_BLOB))
        original = d.known_original(self.raw)
        self.payloads = {k: value for k, value in original['payloads'].items() if k.endswith('.md')}
        youtube = d.VAULT + 'Resources/YouTube/Daily/' + d.DAY + '.md'
        for old, new in zip(d.OLD_YOUTUBE, d.NEW_YOUTUBE):
            self.payloads[youtube] = self.payloads[youtube].replace(old, new)
        for target in original['plan']['targets']:
            if not target['path'].endswith('.jsonl'): continue
            before = d.git(SOURCE, 'cat-file', 'blob', target['base_sha']).decode()
            put(self.root, target['path'], before)
            if 'reddit' in target['path']:
                appendix = d.recovered_reddit(original)
            else:
                appendix = ''.join(json.dumps({'date': d.DAY, 'operation_id': d.OP,
                    'position': i, 'video_id': identity, 'title': 'TEST FIXTURE'}) + '\n'
                    for i, identity in enumerate(d.NEW_YOUTUBE, 1))
            self.payloads[d.VAULT + target['path']] = before + appendix
        put(self.root, '00-inbox/Journal/fixture.md', 'Journal user Notes\n')
        put(self.root, '.recommendation/history/english.jsonl', '{"fixture":true}\n')
        commit(self.root)
        self.base = d.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.evidence = json.dumps({'operation_id': d.OP, 'youtube_ids': d.NEW_YOUTUBE,
                                   'source_checks': ['TEST FIXTURE, not real source QA']}).encode()
        self.bundle, self.bundle_raw, self.receipt = d.derive(self.root, self.raw, self.payloads, self.evidence)

    def install(self):
        out = Path(self.tmp.name) / 'staged'
        report = d.stage(self.root, self.payloads, self.evidence, out)
        for path in out.rglob('*'):
            if path.is_file(): put(self.root, path.relative_to(out), path.read_bytes())
        return report

    def test_stage_preserves_original_targets_and_failure(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*')
                  if p.is_file() and '.git' not in p.parts}
        report = d.stage(self.root, self.payloads, self.evidence, Path(self.tmp.name) / 'staged')
        self.assertEqual(report['publication_target_writes_performed'], 0)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*')
                                 if p.is_file() and '.git' not in p.parts})

    def test_exact_transition_and_old_bad_archive(self):
        self.install(); result = b.audit_journal(self.root, self.base)
        self.assertEqual(result['content_qa'], 'not_evaluated')
        self.assertEqual((self.root / d.ARCHIVE).read_bytes(), self.raw)
        b.load_prepared(self.root / d.TRANSACTION, self.root)
        with self.assertRaises(ValueError): b.verify(json.loads(self.raw[len(d.PREFIX):]))

    def test_original_bad_blob_tamper(self):
        with self.assertRaises(ValueError): d.derive(self.root, self.raw + b' ', self.payloads, self.evidence)

    def test_original_plan_digest_or_reservations_tamper(self):
        for key in ('plan_sha256', 'bundle_sha256'):
            original = json.loads(self.raw[len(d.PREFIX):]); original[key] = 'a' * 64
            with self.assertRaises(ValueError): d.known_original(d.PREFIX + json.dumps(original).encode())
        original = json.loads(self.raw[len(d.PREFIX):]); original['plan']['exposed_resource_ids'].pop()
        with self.assertRaises(ValueError): d.known_original(d.PREFIX + json.dumps(original).encode())

    def test_input_zip_evidence_is_bound_and_cannot_disappear(self):
        path = '.recommendation/transaction-runs/news-youtube-reddit/2026-11-08/recovery-source-inputs.zip'
        evidence = json.loads(self.evidence)
        evidence.update(input_zip_path=path,
                        input_zip_sha256='70e13ebbacad2db5070fe113024d151e2b93872544d1ecc88c9447cbcd19f6b8')
        raw = json.dumps(evidence).encode()
        put(self.root, path, d.git(SOURCE, 'cat-file', 'blob', '49094730a30c6c85fd52ffcd3a9b26fd34488c81'))
        d.derive(self.root, self.raw, self.payloads, raw)
        put(self.root, path, b'changed input')
        with self.assertRaisesRegex(ValueError, 'archive missing or changed'):
            d.derive(self.root, self.raw, self.payloads, raw)
        (self.root / path).unlink()
        with self.assertRaises(OSError): d.derive(self.root, self.raw, self.payloads, raw)

    def test_failure_tamper(self):
        put(self.root, d.FAILURE, '{}')
        with self.assertRaises(ValueError): d.derive(self.root, self.raw, self.payloads, self.evidence)

    def test_absent_failure(self):
        (self.root / d.FAILURE).unlink()
        with self.assertRaises(OSError): d.derive(self.root, self.raw, self.payloads, self.evidence)

    def test_recovery_selection_union_is_exact(self):
        for key in ('exposed_resource_ids', 'selected_resource_ids'):
            plan = copy.deepcopy(self.bundle['plan']); plan[key].pop()
            with self.assertRaises(ValueError): d.validate_selection(plan, d.ACTIVE_IDS)
        plan = copy.deepcopy(self.bundle['plan']); plan['date'] = '2026-11-09'
        with self.assertRaises(ValueError): d.validate_selection(plan, d.ACTIVE_IDS)

    def test_missing_registered_evidence(self):
        self.install(); (self.root / d.RECEIPT).unlink()
        with self.assertRaises(ValueError): b.audit_journal(self.root, self.base)
        with self.assertRaises(ValueError): b.load_prepared(self.root / d.TRANSACTION, self.root)

    def test_registered_payload_cannot_be_rebound(self):
        self.install(); commit(self.root)
        changed = dict(self.payloads); changed[d.VAULT + 'News/Daily/' + d.DAY + '.md'] += '\nchanged\n'
        bundle, raw, receipt = d.derive(self.root, self.raw, changed, self.evidence)
        put(self.root, d.TRANSACTION, raw); put(self.root, d.RECEIPT, json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, 'committed recovery evidence changed'):
            d.validate_installed(self.root)

    def test_registered_source_evidence_cannot_be_rebound(self):
        self.install(); commit(self.root)
        evidence = json.loads(self.evidence); evidence['source_checks'].append('changed')
        evidence = json.dumps(evidence).encode()
        _, raw, receipt = d.derive(self.root, self.raw, self.payloads, evidence)
        put(self.root, d.EVIDENCE, evidence); put(self.root, d.RECEIPT, json.dumps(receipt))
        with self.assertRaises(ValueError): d.validate_installed(self.root)

    def test_unrelated_history_prefix_change_rejected(self):
        changed = dict(self.payloads); key = d.VAULT + '.recommendation/history/youtube.jsonl'
        changed[key] = changed[key].split('\n', 1)[1]
        with self.assertRaisesRegex(ValueError, 'prefix'): d.derive(self.root, self.raw, changed, self.evidence)

    def test_changed_current_baseline_blocks_stage(self):
        put(self.root, '.recommendation/history/youtube.jsonl', 'third party\n')
        with self.assertRaises(ValueError): d.stage(self.root, self.payloads, self.evidence, Path(self.tmp.name) / 'staged')

    def test_missing_baseline_read_blocks(self):
        with self.assertRaises(ValueError): b.check_baselines(self.bundle, {})

    def test_resume_missing_completed_partial_and_conflict(self):
        baseline = {t['repository'] + ':' + t['path']:
                    {'status': 'ok', 'sha': t['base_sha']} if t['base_sha'] else {'status': 'missing', 'confirmed': True}
                    for t in self.bundle['plan']['targets']}
        result = r.inspect(self.bundle['plan'], baseline, self.bundle['plan_sha256'])
        self.assertEqual((result['status'], result['next_stage']), ('ready_to_resume', 1))
        for t in self.bundle['plan']['targets']:
            baseline[t['repository'] + ':' + t['path']] = {'status': 'ok', 'sha': t['target_sha']}
        self.assertEqual(r.inspect(self.bundle['plan'], baseline, self.bundle['plan_sha256'])['status'], 'artifacts_match')
        baseline[next(iter(baseline))] = {'status': 'ok', 'sha': 'a' * 40}
        self.assertEqual(r.inspect(self.bundle['plan'], baseline, self.bundle['plan_sha256'])['status'], 'blocked')

    def test_same_operation_different_bundle_is_rejected(self):
        self.install(); commit(self.root)
        changed = copy.deepcopy(self.bundle); changed['payloads'][d.VAULT + 'News/Daily/' + d.DAY + '.md'] += 'changed'
        changed, _, _ = d.derive(self.root, self.raw, changed['payloads'], self.evidence)
        with self.assertRaisesRegex(ValueError, 'different frozen'): d.reservation_gate(self.root, changed)

    def test_same_operation_exact_resume_allowed(self):
        self.install(); commit(self.root)
        self.assertEqual(d.reservation_gate(self.root, self.bundle)['status'], 'passed_permanent_discovery_reservations')

    def test_unrelated_original_bundle_change_is_rejected(self):
        from test_publication_bundle import BundleTests
        path = '.recommendation/transactions/english/2026-10-12.json'
        put(self.root, path, json.dumps(BundleTests().sample())); commit(self.root)
        base = d.git(self.root, 'rev-parse', 'HEAD').decode().strip(); self.install()
        (self.root / path).unlink()
        with self.assertRaises(ValueError): b.audit_journal(self.root, base)

    def test_non_music_append_and_user_notes_are_not_frozen(self):
        self.install(); commit(self.root)
        put(self.root, '00-inbox/Journal/fixture.md', 'Journal user Notes\nlegitimate edit\n')
        put(self.root, '.recommendation/history/english.jsonl', '{"fixture":true}\n{"next":true}\n')
        self.assertEqual(b.audit_journal(self.root, self.base)['status'], 'passed_immutable_publication_bundles')

    def test_all_recovery_files_deleted_still_blocks(self):
        import shutil
        self.install(); commit(self.root)
        shutil.rmtree(self.root / d.DIRECTORY); (self.root / d.TRANSACTION).unlink()
        with self.assertRaises(ValueError): b.audit_journal(self.root)

    def test_archived_original_or_original_notes_changed_blocks(self):
        self.install()
        for path in (d.ARCHIVE, d.ORIGINAL_PLAN_FILE, d.ORIGINAL_NOTES['news'], d.ORIGINAL_REDDIT):
            original = (self.root / path).read_bytes(); put(self.root, path, original + b' ')
            with self.assertRaises(ValueError): d.validate_installed(self.root)
            put(self.root, path, original)

    def test_partial_stage_only_missing_targets_and_error_blocks(self):
        observations = {t['repository'] + ':' + t['path']:
                        {'status': 'ok', 'sha': t['base_sha']} if t['base_sha'] else {'status': 'missing', 'confirmed': True}
                        for t in self.bundle['plan']['targets']}
        first = self.bundle['plan']['targets'][0]; key = first['repository'] + ':' + first['path']
        observations[key] = {'status': 'ok', 'sha': first['target_sha']}
        result = r.inspect(self.bundle['plan'], observations, self.bundle['plan_sha256'])
        self.assertEqual(result['status'], 'ready_to_resume')
        observations[key] = {'status': 'error'}
        self.assertEqual(r.inspect(self.bundle['plan'], observations, self.bundle['plan_sha256'])['status'], 'blocked')

    def test_git_grafts_rejected(self):
        put(self.root, '.git/info/grafts', '')
        with self.assertRaisesRegex(ValueError, 'grafts'): d.reservation_gate(self.root, self.bundle)

    def future(self, day, youtube=None):
        yt = youtube or ['newVideo001', 'newVideo002', 'newVideo003', 'newVideo004', 'newVideo005']
        reddit = ['new001', 'new002', 'new003', 'new004', 'new005', 'new006', 'new007', 'new008', 'new009', 'new010']
        op = 'news-youtube-reddit:' + day
        payloads = {}
        for key in b.targets_for('news-youtube-reddit', day):
            if 'YouTube/Daily' in key: text = '\n'.join('https://www.youtube.com/watch?v=' + x for x in yt)
            elif 'Reddit/Daily' in key: text = '\n'.join('https://www.reddit.com/r/test/comments/' + x + '/fixture/' for x in reddit)
            elif key.endswith('youtube.jsonl'): text = ''.join(json.dumps({'date': day, 'video_id': x, 'operation_id': op}) + '\n' for x in yt)
            elif key.endswith('reddit.jsonl'): text = ''.join(json.dumps({'date': day, 'post_id': x, 'operation_id': op}) + '\n' for x in reddit)
            else: text = 'Test fixture news'
            payloads[key] = text
        plan = {'schema_version': 1, 'project': 'news-youtube-reddit', 'date': day, 'operation_id': op,
                'exposed_resource_ids': ['youtube:' + x for x in yt] + ['reddit:' + x for x in reddit],
                'targets': [{'repository': k.split(':', 1)[0], 'path': k.split(':', 1)[1], 'base_sha': None,
                             'target_sha': r.blob_sha(text.encode()), 'stage': 1} for k, text in payloads.items()]}
        body = {'schema_version': 1, 'plan': plan, 'payloads': payloads, 'plan_sha256': r.digest(plan)}
        bundle = {**body, 'bundle_sha256': r.digest(body)}; b.verify(bundle)
        return bundle

    def test_old_and_new_reservations_block_future_reuse(self):
        self.install(); commit(self.root)
        for identity in (d.OLD_YOUTUBE[2], d.NEW_YOUTUBE[2], d.OLD_YOUTUBE[4], d.NEW_YOUTUBE[4]):
            candidate = self.future('2026-11-09', [identity, 'newVideo002', 'newVideo003', 'newVideo004', 'newVideo005'])
            with self.assertRaisesRegex(ValueError, 'another operation'):
                d.reservation_gate(self.root, candidate)

    def test_retired_unpublished_prepared_still_excludes(self):
        earlier = self.future('2026-11-07')
        path = '.recommendation/transactions/news-youtube-reddit/2026-11-07.json'
        put(self.root, path, json.dumps(earlier)); commit(self.root)
        (self.root / path).unlink(); commit(self.root)
        with self.assertRaisesRegex(ValueError, 'another operation'):
            d.reservation_gate(self.root, self.future('2026-11-09'))

    def test_earlier_unpublished_reservation_blocks_recovery(self):
        earlier = self.future('2026-11-07', [d.NEW_YOUTUBE[2], 'newVideo002', 'newVideo003', 'newVideo004', 'newVideo005'])
        put(self.root, '.recommendation/transactions/news-youtube-reddit/2026-11-07.json', json.dumps(earlier))
        commit(self.root)
        with self.assertRaisesRegex(ValueError, 'another operation'):
            d.stage(self.root, self.payloads, self.evidence, Path(self.tmp.name) / 'staged')

    def test_unrelated_future_can_pass(self):
        self.install(); commit(self.root)
        candidate = self.future('2026-11-09')
        self.assertEqual(d.reservation_gate(self.root, candidate)['status'], 'passed_permanent_discovery_reservations')

    def test_freeze_requires_full_history(self):
        with self.assertRaisesRegex(ValueError, 'full history'):
            b.freeze(self.bundle['plan'], self.bundle['payloads'])

    def test_recovered_bundle_requires_installed_evidence_root(self):
        self.install()
        with self.assertRaises(ValueError): b.load_prepared(self.root / d.TRANSACTION)

if __name__ == '__main__': unittest.main()
