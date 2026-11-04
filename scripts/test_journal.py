import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import publication_bundle as b
import publication_recovery as r
import validate_journal as j


def sample(day='2026-11-02', legacy=False):
    rows = [dict(date=day, operation_id='journal:' + day, doi=f'10.1234/paper{i}',
                 normalized_doi=f'10.1234/paper{i}', title=f'Paper {i}', normalized_title=f'paper{i}',
                 authors='A. Author et al.', year=2026, journal='Journal',
                 source_url=f'https://example.org/paper{i}', reading_scope='摘要',
                 note_path=f'{j.NOTES}/{day}.md', publication_status='published',
                 work_versions=[f'10.1234/paper{i}']) for i in (1, 2)]
    note = f'---\ndate: {day}\ntype: journal-daily\n---\n{b.START}\n'
    note += '\n'.join(f'## Paper {i}\nhttps://doi.org/10.1234/paper{i}\n阅读 摘要 reviewer_synthesis 精读\n' for i in (1, 2))
    note += b.END + '\n\n## Notes\n'
    payloads = {f'{b.VAULT}:{j.NOTES}/{day}.md': note,
                f'{b.VAULT}:{j.NOTES}/Index.md': b.START + f'\n[[{j.NOTES}/{day}|{day}]]\n' + b.END + '\n\n## Notes\n',
                f'{b.VAULT}:{j.HISTORY}': ''.join(json.dumps(row) + '\n' for row in rows)}
    plan = dict(schema_version=1, project='journal', date=day, operation_id='journal:' + day,
                exposed_resource_ids=['doi:' + row['doi'] for row in rows],
                targets=[dict(repository=b.VAULT, path=k.split(':', 1)[1], base_sha=None,
                              target_sha=r.blob_sha(text.encode()), stage=1) for k, text in payloads.items()])
    if not legacy:
        return b.freeze(plan, payloads)
    plan['version'] = plan.pop('schema_version')
    body = dict(schema_version='journal-frozen-v1', status='PREPARED', compatibility_note='legacy record',
                plan=plan, evidence={'papers': [{'doi': row['doi']} for row in rows]},
                payloads={k.split(':', 1)[1]: text for k, text in payloads.items()}, plan_sha256=r.digest(plan))
    return {**body, 'bundle_sha256': r.digest(body)}


class JournalTests(unittest.TestCase):
    def test_native_and_legacy_without_mutation(self):
        for legacy in (False, True):
            bundle = sample(legacy=legacy); original = copy.deepcopy(bundle)
            b.verify(bundle); b.check_baselines(bundle, {k: None for k in b.payloads_for(bundle)})
            self.assertEqual(bundle, original)

    def test_retry_legacy_uses_original_digest(self):
        bundle = sample(legacy=True)
        obs = {k: {'status': 'ok', 'sha': r.blob_sha(text.encode())} for k, text in b.payloads_for(bundle).items()}
        self.assertEqual(r.inspect(bundle['plan'], obs, bundle['plan_sha256'])['status'], 'artifacts_match')
        del obs[next(iter(obs))]
        self.assertEqual(r.inspect(bundle['plan'], obs, bundle['plan_sha256'])['status'], 'blocked')

    def test_legacy_payload_tamper_rejected(self):
        bundle = sample(legacy=True); bundle['payloads'][j.HISTORY] += '{}\n'
        with self.assertRaises(ValueError): b.verify(bundle)

    def test_rehash_cannot_hide_wrong_payload(self):
        bundle = sample(legacy=True); bundle['payloads'][j.HISTORY] += '{}\n'
        bundle['bundle_sha256'] = r.digest({k: v for k, v in bundle.items() if k != 'bundle_sha256'})
        with self.assertRaisesRegex(ValueError, 'payload hash'): b.verify(bundle)

    def test_legacy_evidence_cannot_change_selection(self):
        bundle = sample(legacy=True); bundle['evidence']['papers'][0]['doi'] = '10.1234/other'
        bundle['bundle_sha256'] = r.digest({k: v for k, v in bundle.items() if k != 'bundle_sha256'})
        with self.assertRaisesRegex(ValueError, 'evidence/selection'): b.verify(bundle)

    def test_unknown_format_fails_closed(self):
        bundle = sample(); bundle['schema_version'] = 'unknown'
        with self.assertRaises(ValueError): b.verify(bundle)

    def test_wrong_project_cannot_use_legacy_schema(self):
        plan = sample(legacy=True)['plan']; plan['project'] = 'english'
        with self.assertRaises(ValueError): r.validate(plan)

    def test_new_freeze_requires_standard_schema(self):
        bundle = sample(legacy=True)
        with self.assertRaises(ValueError): b.freeze(bundle['plan'], b.payloads_for(bundle))

    def test_journal_has_exact_three_targets(self):
        self.assertEqual(len(b.targets_for('journal', '2026-11-02')), 3)
        bundle = sample(); bundle['payloads'][b.VAULT + ':extra.md'] = 'bad'
        with self.assertRaises(ValueError): b.freeze(bundle['plan'], bundle['payloads'])

    def test_normalizes_doi_case_and_url(self):
        self.assertEqual(j.normalize_doi('https://doi.org/10.7554/eLife.53514'), '10.7554/elife.53514')

    def test_duplicate_doi_rejected(self):
        text = b.payloads_for(sample())[b.VAULT + ':' + j.HISTORY]
        with self.assertRaises(ValueError): j.history_rows(text + text)

    def test_preprint_alias_rejected(self):
        rows = j.history_rows(b.payloads_for(sample())[b.VAULT + ':' + j.HISTORY])
        rows[1]['work_versions'].append(rows[0]['doi'])
        with self.assertRaisesRegex(ValueError, 'study version'): j.history_rows(''.join(json.dumps(x) + '\n' for x in rows))

    def test_title_variant_rejected(self):
        rows = j.history_rows(b.payloads_for(sample())[b.VAULT + ':' + j.HISTORY])
        rows[1]['title'] = 'PAPER-1'; rows[1]['normalized_title'] = 'paper1'
        with self.assertRaisesRegex(ValueError, 'repeated title'): j.history_rows(''.join(json.dumps(x) + '\n' for x in rows))

    def test_note_and_history_mismatch(self):
        payloads = b.payloads_for(sample()); rows = j.history_rows(payloads[b.VAULT + ':' + j.HISTORY])
        note = payloads[b.VAULT + ':' + j.NOTES + '/2026-11-02.md'].replace('10.1234/paper2', '10.1234/other')
        with self.assertRaises(ValueError): j.validate_note(note, '2026-11-02', rows)

    def test_missing_index_entry(self):
        note = b.payloads_for(sample())[b.VAULT + ':' + j.NOTES + '/Index.md']
        with self.assertRaises(ValueError): j.validate_index(note, {'2026-11-02', '2026-11-03'})

    def test_missing_history_and_orphan_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / j.NOTES / '2026-11-02.md'; path.parent.mkdir(parents=True)
            path.write_text('orphan')
            with self.assertRaises(ValueError): j.audit(root)

    def test_notes_not_treated_as_recommendations(self):
        payloads = b.payloads_for(sample()); rows = j.history_rows(payloads[b.VAULT + ':' + j.HISTORY])
        note = payloads[b.VAULT + ':' + j.NOTES + '/2026-11-02.md'] + 'Personal DOI https://doi.org/10.1234/personal\n'
        j.validate_note(note, '2026-11-02', rows)

    def test_bold_label_needs_separating_space(self):
        payloads = b.payloads_for(sample()); rows = j.history_rows(payloads[b.VAULT + ':' + j.HISTORY])
        note = payloads[b.VAULT + ':' + j.NOTES + '/2026-11-02.md']
        broken = note.replace('阅读 摘要', '- **问题与观测：**DrBphP 阅读 摘要')
        with self.assertRaisesRegex(ValueError, 'space after'): j.validate_note(broken, '2026-11-02', rows)
        j.validate_note(broken.replace('**DrBphP', '** DrBphP'), '2026-11-02', rows)

    def test_legacy_preserves_original_bad_format(self):
        bundle = sample(legacy=True); key = j.NOTES + '/2026-11-02.md'
        bundle['payloads'][key] = bundle['payloads'][key].replace('阅读 摘要', '- **问题与观测：**DrBphP 阅读 摘要')
        bundle['plan']['targets'][0]['target_sha'] = r.blob_sha(bundle['payloads'][key].encode())
        bundle['plan_sha256'] = r.digest(bundle['plan'])
        bundle['bundle_sha256'] = r.digest({k: v for k, v in bundle.items() if k != 'bundle_sha256'})
        b.verify(bundle)

    def test_git_history_and_prepared_are_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); bundle = sample(legacy=True)
            for key, text in b.payloads_for(bundle).items():
                path = root / key.split(':', 1)[1]; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
            tx = root / '.recommendation/transactions/journal/2026-11-02.json'
            tx.parent.mkdir(parents=True); tx.write_text(json.dumps(bundle))
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()
            git('init', '-q'); git('add', '.'); git('-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            self.assertEqual(j.audit(root, base)['papers'], 2)
            b.audit_journal(root, base)
            tx.write_text(json.dumps(bundle, indent=2))
            with self.assertRaisesRegex(ValueError, 'rewritten'): b.audit_journal(root, base)
            tx.write_text(json.dumps(bundle))
            history = root / j.HISTORY
            history.write_text(history.read_text().replace('A. Author', 'B. Author'))
            with self.assertRaisesRegex(ValueError, 'append-only'): j.audit(root, base)


if __name__ == '__main__':
    unittest.main()
