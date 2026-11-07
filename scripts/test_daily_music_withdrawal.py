"""The sole authorized four-track correction must not weaken other publications."""
import copy
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import music_withdrawal as w
import music_identity as m
import publication_bundle as b
import publication_recovery as r
import validate_daily_recommendations as v

ROOT=Path(__file__).resolve().parents[1]
BASE='341767faeee3a06e44b56b97899e93729524ced4'


class WithdrawalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for name in (w.RECORD,w.PREPARED,w.MANIFEST,w.NOTE,w.FAILURE,w.FIRST_MANIFEST,'Music/Daily/state/tracks.json',m.INCIDENT):
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
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
        self.assertEqual(w.count_for(self.root,w.DAY),5)
        with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):v.validate_music()
    def test_four_tracks_not_allowed_on_other_dates(self):
        self.assertEqual(w.count_for(self.root,'2026-11-07'),5)
        p=self.root/'Music/Daily/2026-11-08.md';p.write_text((self.root/w.NOTE).read_text().replace('2026-11-06','2026-11-08'))
        with patch.object(v,'ROOT',self.root),patch.object(v,'MUSIC_DIR',self.root/'Music/Daily'),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):v.validate_music()
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
    def test_actual_original_new_journal_plan_remains_recoverable(self):
        path=ROOT/'.recommendation/transactions/journal/2026-11-07.json'
        bundle=json.loads(path.read_text());b.verify(bundle)
        baselines={};observations={}
        for target in bundle['plan']['targets']:
            file=ROOT/target['path'];key=target['repository']+':'+target['path']
            baselines[key]=file.read_text() if file.exists() else None
            observations[key]={'status':'ok','sha':r.blob_sha(file.read_bytes())} if file.exists() else {'status':'missing','confirmed':True}
        b.check_baselines(bundle,baselines)
        result=r.inspect(bundle['plan'],observations,bundle['plan_sha256'])
        self.assertEqual(result['status'],'ready_to_resume');self.assertEqual(result['next_stage'],1)
        self.assertEqual(len([d for d in result['decisions'] if d['action'] in ('create','update')]),3)
    def test_non_music_files_and_all_original_bundles_unchanged(self):
        names=m.git(ROOT,'ls-tree','-rz','--name-only',BASE).split(b'\0')
        prefixes=('00-inbox/Journal/','50-courses/English/','News/','Resources/',
                  '.recommendation/history/','.recommendation/transactions/',
                  '.recommendation/transaction-runs/','.recommendation/runs/','.github/')
        for raw in filter(None,names):
            name=raw.decode()
            if name.startswith(prefixes):
                self.assertEqual((ROOT/name).read_bytes(),m.git(ROOT,'show',BASE+':'+name),name)

if __name__=='__main__':unittest.main()
