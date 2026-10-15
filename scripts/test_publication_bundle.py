import copy
import json
import unittest
import publication_bundle as b
import publication_recovery as r


class BundleTests(unittest.TestCase):
    def sample(self):
        day='2026-10-12'; payloads={}
        for key in b.targets_for('english',day):
            if '/Daily/' in key: payloads[key]='---\nsource_url: https://example.org/a\n---\nLearning material\n'
            elif key.endswith('.jsonl'): payloads[key]=json.dumps({'date':day,'source_url':'https://example.org/a'})+'\n'
            else: payloads[key]='Exercise\n'
        plan={'schema_version':1,'project':'english','date':day,'operation_id':'english:'+day,
              'exposed_resource_ids':['https://example.org/a'],
              'targets':[{'repository':k.split(':',1)[0],'path':k.split(':',1)[1],'base_sha':None,
                          'target_sha':r.blob_sha(value.encode()),'stage':1} for k,value in payloads.items()]}
        return b.freeze(plan,payloads)
    def test_roundtrip(self): b.verify(json.loads(json.dumps(self.sample())))
    def test_all_new_baselines(self):
        x=self.sample();b.check_baselines(x,{k:None for k in x['payloads']})
    def test_corrupt_payload(self):
        x=self.sample(); x['payloads'][next(iter(x['payloads']))]+='changed'
        with self.assertRaises(ValueError): b.verify(x)
    def test_missing_history(self):
        x=self.sample();x['payloads'].pop(b.VAULT+':.recommendation/history/english.jsonl')
        with self.assertRaises(ValueError): b.freeze(x['plan'],x['payloads'])
    def test_recomputed_envelope_cannot_hide_target_change(self):
        x=self.sample();x['payloads'][next(iter(x['payloads']))]+='changed'
        with self.assertRaises(ValueError): b.freeze(x['plan'],x['payloads'])
    def test_source_reselection(self):
        x=self.sample();x['plan']['exposed_resource_ids']=['https://example.org/b']
        with self.assertRaises(ValueError): b.freeze(x['plan'],x['payloads'])
    def test_missing_base_is_not_new_file(self):
        x=self.sample();del x['plan']['targets'][0]['base_sha']
        with self.assertRaises(ValueError): r.validate(x['plan'])
    def test_missing_read_baseline(self):
        with self.assertRaises(ValueError): b.check_baselines(self.sample(),{})
    def test_wrong_stage(self):
        x=self.sample();x['plan']['targets'][0]['stage']=2
        with self.assertRaises(ValueError): b.freeze(x['plan'],x['payloads'])
    def test_unrelated_write_rejected(self):
        x=self.sample();t=x['plan']['targets'][0];t['path']='.github/workflows/unsafe.yml'
        with self.assertRaises(ValueError): b.freeze(x['plan'],x['payloads'])
    def test_same_content_is_noop(self):
        x=self.sample();obs={k:{'status':'ok','sha':r.blob_sha(v.encode())} for k,v in x['payloads'].items()}
        result=r.inspect(x['plan'],obs,x['plan_sha256']);self.assertEqual(result['status'],'artifacts_match')
    def test_weekday_four_targets(self): self.assertEqual(len(b.targets_for('english','2026-10-12')),4)
    def test_saturday_history_required(self):
        keys=b.targets_for('english','2026-10-10');self.assertEqual(len(keys),2);self.assertTrue(any('/TV/' in x for x in keys))
    def test_sunday_history_required(self):
        keys=b.targets_for('english','2026-10-11');self.assertEqual(len(keys),2);self.assertFalse(any('/TV/' in x for x in keys))
    def test_music_all_five_artifacts(self): self.assertEqual(len(b.targets_for('music','2026-10-12')),5)
    def test_discovery_three_notes_two_histories(self): self.assertEqual(len(b.targets_for('news-youtube-reddit','2026-10-11')),5)
    def test_unchanged_manual_note(self): b.preserve_note('personal note','personal note')
    def test_unmarked_note_cannot_change(self):
        with self.assertRaises(ValueError): b.preserve_note('personal note','replacement')
    def test_auto_body_can_change(self): b.preserve_note('head'+b.START+'old'+b.END+'Notes','head'+b.START+'new'+b.END+'Notes')
    def test_manual_tail_cannot_change(self):
        with self.assertRaises(ValueError):b.preserve_note('head'+b.START+'old'+b.END+'Notes','head'+b.START+'new'+b.END+'lost')
    def test_duplicate_marker_cannot_change(self):
        with self.assertRaises(ValueError):b.preserve_note(b.START*2+b.END,b.START+'x'+b.END)
    def test_append_only_cannot_delete_history(self):
        x=self.sample();key=b.VAULT+':.recommendation/history/english.jsonl';old='{"date":"2026-10-01","source_url":"https://example.org/old"}\n'
        for t in x['plan']['targets']:
            if t['path'].endswith('.jsonl'):t['base_sha']=r.blob_sha(old.encode())
        x=b.freeze(x['plan'],x['payloads']);baselines={k:None for k in x['payloads']};baselines[key]=old
        with self.assertRaises(ValueError):b.check_baselines(x,baselines)
    def test_append_only_can_add_history(self):
        x=self.sample();key=b.VAULT+':.recommendation/history/english.jsonl';old='{"date":"2026-10-01","source_url":"https://example.org/old"}\n';x['payloads'][key]=old+x['payloads'][key]
        for t in x['plan']['targets']:
            if t['path'].endswith('.jsonl'):t.update(base_sha=r.blob_sha(old.encode()),target_sha=r.blob_sha(x['payloads'][key].encode()))
        x=b.freeze(x['plan'],x['payloads']);baselines={k:None for k in x['payloads']};baselines[key]=old;b.check_baselines(x,baselines)

if __name__=='__main__':unittest.main()

class JournalTests(unittest.TestCase):
    def test_empty_journal_is_not_content_qa(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            result=b.audit_journal(Path(d));self.assertEqual(result['bundles'],0);self.assertEqual(result['content_qa'],'not_evaluated')
    def test_valid_journal(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'.recommendation/transactions/english/2026-10-12.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps(BundleTests().sample()))
            self.assertEqual(b.audit_journal(Path(d))['bundles'],1)
    def test_wrong_journal_path(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'.recommendation/transactions/english/2026-10-13.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps(BundleTests().sample()))
            with self.assertRaises(ValueError):b.audit_journal(Path(d))
