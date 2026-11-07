"""The sole authorized four-track correction must not weaken other publications."""
import copy
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch
import music_withdrawal as w
import music_identity as m
import publication_bundle as b
import publication_recovery as r
import validate_daily_recommendations as v

ROOT=Path(__file__).resolve().parents[1]


class WithdrawalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for name in (w.PREPARED,w.FAILURE,w.FIRST_MANIFEST,'Music/Daily/state/tracks.json',m.INCIDENT):
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        # Build corrected fixture files from immutable evidence. In particular,
        # never pin the live music note's user-owned Notes to an old revision.
        _,old_manifest,old_note=w.original(self.root)
        manifest,note=w.corrected_manifest(old_manifest),w.corrected_note(old_note)
        (self.root/w.MANIFEST).write_text(manifest);(self.root/w.NOTE).write_text(note)
        record=self.root/w.RECORD;record.parent.mkdir(parents=True,exist_ok=True)
        record.write_text(json.dumps(w.expected_record(manifest,note),ensure_ascii=False,indent=2)+'\n')
    def mutate_json(self,name,change):
        p=self.root/name;doc=json.loads(p.read_text());change(doc);p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    def test_exact_withdrawal_retains_original_positions(self):
        self.assertEqual(w.validate(self.root)['retained_positions'],[1,2,4,5])
        self.assertEqual([x['position'] for x in json.loads((self.root/w.MANIFEST).read_text())['tracks']],[1,2,4,5])
    def test_only_one_original_track_removed_without_other_metadata_edits(self):
        _,original,_=w.original(self.root);old=json.loads(original);new=json.loads((self.root/w.MANIFEST).read_text())
        expected=copy.deepcopy(old);del expected['tracks'][2];self.assertEqual(new,expected)
    def test_retained_note_sections_exact_and_notes_untouched(self):
        _,_,old=w.original(self.root);new=(self.root/w.NOTE).read_text()
        # Compare each retained section directly, including all prose and metadata.
        for pos in [1,2,4,5]:
            pattern=rf'(?ms)^## {pos}\. .*?(?=^## |<!-- AUTO:END -->)'
            self.assertEqual(re.search(pattern,old)[0],re.search(pattern,new)[0])
        self.assertEqual(old.split(w.START)[0],new.split(w.START)[0])
        self.assertEqual(old.split(w.END)[1],new.split(w.END)[1])
        self.assertNotIn('714861225',new)
        self.assertNotIn('An Ending (Ascent)',new)
    def test_user_notes_can_still_be_added(self):
        p=self.root/w.NOTE;p.write_text(p.read_text()+'\nPersonal listening note.\n')
        self.assertIsNotNone(w.validate(self.root))
    def test_wrong_record_scope_fails(self):
        for field,value in [('song_id','1'),('position',2),('retained_positions',[1,2,4]),
                            ('date','2026-11-07'),('historical_content_qa','passed'),
                            ('original_manifest_blob','0'*40),('corrected_manifest_blob','0'*40),
                            ('original_bundle_sha256','0'*64),('original_failure_receipt_blob','0'*40)]:
            with self.subTest(field=field):
                p=self.root/w.RECORD;raw=p.read_bytes()
                self.mutate_json(w.RECORD,lambda d:d.update({field:value}))
                with self.assertRaisesRegex(ValueError,'record scope'):w.validate(self.root)
                p.write_bytes(raw)
    def test_removing_second_track_fails(self):
        self.mutate_json(w.MANIFEST,lambda d:d['tracks'].pop(1))
        with self.assertRaisesRegex(ValueError,'corrected manifest'):w.validate(self.root)
    def test_reselection_and_renumbering_fail(self):
        for field,value in [('title','replacement'),('position',3)]:
            p=self.root/w.MANIFEST;raw=p.read_bytes()
            self.mutate_json(w.MANIFEST,lambda d:d['tracks'][2].update({field:value}))
            with self.assertRaisesRegex(ValueError,'corrected manifest'):w.validate(self.root)
            p.write_bytes(raw)
    def test_readding_original_duplicate_fails(self):
        _,old,_=w.original(self.root);(self.root/w.MANIFEST).write_text(old)
        with self.assertRaisesRegex(ValueError,'corrected manifest'):w.validate(self.root)
    def test_failure_receipt_and_prepared_bytes_cannot_change(self):
        for name in (w.FAILURE,w.PREPARED):
            p=self.root/name;raw=p.read_bytes();p.write_bytes(raw+b'\n')
            with self.assertRaises(ValueError):w.validate(self.root)
            p.write_bytes(raw)
    def test_first_occurrence_cannot_be_deleted(self):
        (self.root/w.FIRST_MANIFEST).write_text('{}')
        with self.assertRaisesRegex(ValueError,'first occurrence'):w.validate(self.root)
    def test_permanent_exclusion_cannot_be_deleted(self):
        self.mutate_json('Music/Daily/state/tracks.json',lambda d:d['recommended'].pop('Brian Eno::An Ending (Ascent)'))
        with self.assertRaisesRegex(ValueError,'permanent exclusions'):w.validate(self.root)
    def test_no_success_receipt_for_original_failed_day(self):
        path=self.root/'.recommendation/runs/2026-11-06-music.json';path.parent.mkdir(parents=True);path.write_text('{}')
        with self.assertRaisesRegex(ValueError,'original failure'):w.validate(self.root)
    def test_note_tampering_cannot_hide_behind_manifest(self):
        p=self.root/w.NOTE;p.write_text(p.read_text().replace('Fado Final','replacement'))
        with self.assertRaisesRegex(ValueError,'note selection'):w.validate(self.root)
    def test_four_track_exception_requires_record(self):
        (self.root/w.RECORD).unlink()
        with self.assertRaisesRegex(ValueError,'required music withdrawal evidence'):w.count_for(self.root,w.DAY)
        with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises((SystemExit,ValueError)):v.validate_music()
    def test_missing_record_blocks_current_integrity_even_if_original_five_restored(self):
        import check_daily_integrity as integrity
        bundle,old_manifest,old_note=w.original(self.root)
        (self.root/w.RECORD).unlink()
        for restore_original in (False,True):
            with self.subTest(restore_original=restore_original):
                if restore_original:
                    (self.root/w.MANIFEST).write_text(old_manifest);(self.root/w.NOTE).write_text(old_note)
                # Minimal unrelated fixture histories let the real current
                # integrity audit reach the music evidence gate.
                values={'youtube':('video_id','abcdefghijk'),'reddit':('post_id','abc123'),
                        'english':('source_url','https://example.org/source')}
                for name,(field,value) in values.items():
                    path=self.root/f'.recommendation/history/{name}.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_text(json.dumps({'date':'2026-10-12',field:value})+'\n')
                with self.assertRaisesRegex(ValueError,'required music withdrawal evidence'):
                    integrity.audit(self.root,'2026-09-11')
                import check_publication_health as health
                (self.root/'.recommendation/policy.json').write_text(json.dumps({'strict_from':'2026-09-11'}))
                report=health.audit(self.root)
                self.assertEqual(report['status'],'blocked')
                self.assertIn('required music withdrawal evidence',report['checks']['integrity']['error'])
                self.assertEqual(report['checks']['immutable_bundles']['status'],'passed_immutable_publication_bundles')
                with self.assertRaisesRegex(ValueError,'required music withdrawal evidence'):
                    m.recovery_gate(self.root,bundle,{}, {}, {})
                # Immutable archive verification must not certify current state,
                # but it must still accept the exact original five-track bundle.
                b.verify(bundle)
    def test_missing_record_and_original_five_fail_current_structure(self):
        _,old_manifest,old_note=w.original(self.root);(self.root/w.RECORD).unlink()
        (self.root/w.MANIFEST).write_text(old_manifest);(self.root/w.NOTE).write_text(old_note)
        with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'):
            with self.assertRaisesRegex(ValueError,'required music withdrawal evidence'):v.validate_music()
    def test_four_tracks_not_allowed_on_other_dates(self):
        self.assertEqual(w.count_for(self.root,'2026-11-07'),5)
        p=self.root/'Music/Daily/2026-11-08.md';p.write_text((self.root/w.NOTE).read_text().replace('2026-11-06','2026-11-08'))
        with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises((SystemExit,ValueError)):v.validate_music()
    def test_old_bundle_verification_still_requires_original_five(self):
        bundle,_,_=w.original(self.root);b.verify(bundle)
        self.assertEqual(len(json.loads(bundle['payloads'][w.VAULT+w.MANIFEST])['tracks']),5)
        altered=copy.deepcopy(bundle);altered['payloads'][w.VAULT+w.MANIFEST]=(self.root/w.MANIFEST).read_text()
        with self.assertRaises(ValueError):b.verify(altered)
    def test_old_bundle_replay_explicitly_blocked(self):
        bundle,_,_=w.original(self.root)
        with self.assertRaisesRegex(ValueError,'cannot replay'):
            m.recovery_gate(self.root,bundle,{}, {}, {})
    def test_original_failure_incident_remains_verifiable_after_withdrawal(self):
        self.assertEqual(m.incident(self.root)['content_qa'],'failed')
    def test_future_alias_reuse_still_blocked(self):
        from test_daily_music_identity import manifest
        with self.assertRaisesRegex(ValueError,'reuse'):
            m.check_selection(ROOT,manifest('2026-12-01',714861225,'another alias'))
    def journal_fixture(self):
        from test_journal import sample
        bundle=sample(day='2026-11-06')
        baselines={key:(None if key.endswith('/2026-11-06.md') else
                       '' if key.endswith('.jsonl') else b.START+'\n'+b.END+'\n\n## Notes\n')
                   for key in bundle['payloads']}
        for target in bundle['plan']['targets']:
            key=target['repository']+':'+target['path'];old=baselines[key]
            target['base_sha']=r.blob_sha(old.encode()) if old is not None else None
            if old is not None:
                path=self.root/target['path'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(old)
        bundle=b.freeze(bundle['plan'],bundle['payloads'])
        return bundle,baselines
    def inspect_fixture(self,bundle):
        observations={}
        for target in bundle['plan']['targets']:
            path=self.root/target['path'];key=target['repository']+':'+target['path']
            observations[key]=({'status':'ok','sha':r.blob_sha(path.read_bytes())} if path.exists()
                               else {'status':'missing','confirmed':True})
        # Exercise the real CLI with a Journal operation on the same date as
        # the music withdrawal: no music gate or production files are involved.
        bundle_path=self.root/'fixture-journal-bundle.json';bundle_path.write_text(json.dumps(bundle))
        obs_path=self.root/'fixture-observations.json';obs_path.write_text(json.dumps(observations))
        args=['publication_bundle.py',str(bundle_path),'--observations',str(obs_path),
              '--expected-bundle-digest',bundle['bundle_sha256']]
        with patch('sys.argv',args),contextlib.redirect_stdout(io.StringIO()) as output:
            code=b.main()
        return code,json.loads(output.getvalue())
    def test_journal_fixture_baselines_can_resume(self):
        bundle,baselines=self.journal_fixture();b.check_baselines(bundle,baselines)
        code,result=self.inspect_fixture(bundle)
        self.assertEqual(code,0);self.assertEqual(result['status'],'ready_to_resume')
        self.assertEqual(result['next_stage'],1)
        self.assertEqual([d['action'] for d in result['decisions']],['create','update','update'])
    def test_journal_fixture_completed_is_noop(self):
        bundle,_=self.journal_fixture()
        for key,text in bundle['payloads'].items():
            path=self.root/key.split(':',1)[1];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        code,result=self.inspect_fixture(bundle)
        self.assertEqual(code,0);self.assertEqual(result['status'],'artifacts_match')
        self.assertIsNone(result['next_stage']);self.assertTrue(all(d['action']=='no_op' for d in result['decisions']))
    def test_journal_fixture_conflict_remains_blocked(self):
        bundle,_=self.journal_fixture();path=self.root/'00-inbox/Journal/Index.md'
        path.write_text(path.read_text()+'Personal notes added after freeze.\n')
        original=path.read_bytes();code,result=self.inspect_fixture(bundle)
        self.assertEqual(code,1);self.assertEqual(result['status'],'blocked')
        self.assertIsNone(result['next_stage']);self.assertEqual(path.read_bytes(),original)
    def test_withdrawal_preserves_unrelated_fixture_updates(self):
        paths=['00-inbox/Journal/Index.md','00-inbox/Journal/2030-01-01.md',
               '50-courses/English/Weekly/TV/2030-01-01.md','News/Daily/2030-01-01.md',
               'Resources/YouTube/Daily/2030-01-01.md',
               '.recommendation/history/english.jsonl','.recommendation/history/journal.jsonl',
               '.recommendation/history/youtube.jsonl','.recommendation/history/reddit.jsonl']
        for generation in range(2):
            for name in paths:
                path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('a') as stream:
                    stream.write(json.dumps({'generation':generation})+'\n' if name.endswith('.jsonl')
                                 else f'New index entry or user Notes generation {generation}.\n')
            before={name:(self.root/name).read_bytes() for name in paths}
            self.assertIsNotNone(w.validate(self.root))
            with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'):
                self.assertEqual(v.validate_music(),4)
            self.assertEqual({name:(self.root/name).read_bytes() for name in paths},before)

if __name__=='__main__':unittest.main()
