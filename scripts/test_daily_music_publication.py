import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import music_publication as p
import music_identity as m
import publication_bundle as b
import test_daily_music_recovery as fixtures
from test_daily_music_identity import manifest, write

class MusicProducerTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.MusicRecoveryTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.v,self.mu=self.f.root,self.f.other
        self.remote=patch.object(p,'remote_head',side_effect=lambda root:m.git(root,'rev-parse','HEAD').decode().strip())
        self.remote.start();self.addCleanup(self.remote.stop)
        self.day='2026-03-01'
    def prepare(self,day=None):return p.prepare(self.v,self.mu,day or self.day)
    def draft(self,start=30000):
        doc=manifest(self.day,start);note='\n'.join(x['apple_music']['url'] for x in doc['tracks'])
        return json.dumps(doc),note
    def test_prepare_before_selection_and_freeze(self):
        before={root:m.git(root,'status','--porcelain') for root in (self.v,self.mu)}
        report=self.prepare();self.assertEqual(report['mode'],'ready_before_selection')
        manifest_text,note=self.draft();bundle=p.freeze(report,self.v,self.mu,manifest_text,note);b.verify(bundle)
        self.assertEqual([t['stage'] for t in bundle['plan']['targets']],[1,1,2,2,2])
        self.assertEqual(before,{root:m.git(root,'status','--porcelain') for root in (self.v,self.mu)})
    def test_missing_cli_roots_rejected(self):
        with self.assertRaises(SystemExit) as caught:p.main(['prepare','--date',self.day])
        self.assertEqual(caught.exception.code,2)
    def test_legacy_missing_keywords_stays_blocked(self):
        with self.assertRaisesRegex(ValueError,'music_publication.py prepare'):
            b.freeze(self.f.bundle['plan'],self.f.bundle['payloads'])
    def test_shallow_history_rejected(self):
        (self.v/'.git/shallow').write_text(m.git(self.v,'rev-parse','HEAD').decode())
        with self.assertRaisesRegex(ValueError,'full Git history'):self.prepare()
    def test_remote_local_mismatch_rejected(self):
        with patch.object(p,'remote_head',return_value='a'*40):
            with self.assertRaisesRegex(ValueError,'HEAD differs'):self.prepare()
    def test_remote_moves_during_scan(self):
        heads=[m.git(root,'rev-parse','HEAD').decode().strip() for root in (self.v,self.mu)]
        with patch.object(p,'remote_head',side_effect=heads+['a'*40,heads[1]]):
            with self.assertRaisesRegex(ValueError,'HEAD changed'):self.prepare()
    def test_dirty_and_untracked_inputs_rejected(self):
        path=self.v/m.STATE;old=path.read_bytes();path.write_bytes(old+b'\n')
        with self.assertRaisesRegex(ValueError,'tracked checkout'):self.prepare()
        path.write_bytes(old);write(self.v,'Music/Daily/2026-03-01.md','draft')
        with self.assertRaisesRegex(ValueError,'uncommitted publication'):self.prepare()
    def test_mirror_mismatch_rejected_before_selection(self):
        state=json.loads((self.mu/'state/tracks.json').read_text());state['extra']='changed'
        write(self.mu,'state/tracks.json',state);self.f.commit(self.mu)
        with self.assertRaisesRegex(ValueError,'state differs'):self.prepare()
    def test_stale_preflight_cannot_freeze(self):
        report=self.prepare();write(self.v,'unrelated.md','new main');self.f.commit(self.v)
        with self.assertRaisesRegex(ValueError,'stale'):p.freeze(report,self.v,self.mu,*self.draft())
    def test_repeated_recording_under_new_artist_rejected(self):
        report=self.prepare();doc=manifest(self.day,10000,artist='翻译别名');note='\n'.join(x['apple_music']['url'] for x in doc['tracks'])
        with self.assertRaisesRegex(ValueError,'reuse'):p.freeze(report,self.v,self.mu,json.dumps(doc),note)
    def test_prior_unfinished_prepared_is_excluded(self):
        report=self.prepare()
        with self.assertRaisesRegex(ValueError,'reuse'):p.freeze(report,self.v,self.mu,*self.draft(20000))
    def test_existing_bundle_routes_to_recovery(self):
        report=self.prepare('2026-02-01');self.assertEqual(report['mode'],'resume_existing_bundle')
        self.assertEqual(report['planner']['next_stage'],1)
        with self.assertRaisesRegex(ValueError,'recover an existing'):p.freeze(report,self.v,self.mu,*self.draft())
    def test_stage1_done_routes_to_stage2_not_mirror_failure(self):
        self.f.apply(1);report=self.prepare('2026-02-01')
        self.assertEqual(report['planner']['next_stage'],2)
    def test_completed_is_noop(self):
        self.f.apply(1);self.f.apply(2)
        self.assertEqual(self.prepare('2026-02-01')['planner']['status'],'artifacts_match')
    def test_missing_bundle_with_dated_note_requires_review(self):
        write(self.v,'Music/Daily/'+self.day+'.md','manual note');self.f.commit(self.v)
        with self.assertRaisesRegex(ValueError,'adoption'):self.prepare()
    def test_withdrawal_validation_is_not_skipped(self):
        with patch.object(m,'incident',side_effect=ValueError('missing exact withdrawal evidence')):
            with self.assertRaisesRegex(ValueError,'withdrawal evidence'):self.prepare()
    def test_output_never_overwrites_or_writes_repo(self):
        with self.assertRaisesRegex(ValueError,'outside'):p.write_output(self.v/'new.json',{},[self.v,self.mu])
        path=Path(self.f.tmp.name)/'out.json';p.write_output(path,{},[self.v,self.mu])
        with self.assertRaises(FileExistsError):p.write_output(path,{},[self.v,self.mu])

    def test_located_other_project_corruption_is_warning(self):
        for project in ('english', 'journal', 'news-youtube-reddit'):
            with self.subTest(project=project):
                path='.recommendation/transactions/'+project+'/2026-02-02.json'
                write(self.v,path,'{broken');self.f.commit(self.v)
                report=self.prepare()
                self.assertEqual(report['mode'],'ready_before_selection')
                self.assertEqual(report['bundle_health']['global_bundles']['status'],'failed_other_project_data')
                self.assertEqual(report['bundle_health']['warnings'][0]['path'],path)
                (self.v/path).unlink();self.f.commit(self.v)
    def test_music_corruption_still_blocks(self):
        write(self.v,'.recommendation/transactions/music/2026-02-02.json','{broken')
        self.f.commit(self.v)
        with self.assertRaises(ValueError):self.prepare()
    def test_unattributed_shared_failure_still_blocks(self):
        with patch.object(b,'audit_journal',side_effect=ValueError('shared validator failed')):
            with self.assertRaisesRegex(ValueError,'shared validator'):self.prepare()
    def test_other_project_warning_cannot_hide_music_history_failure(self):
        write(self.v,'.recommendation/transactions/english/2026-02-02.json','{broken')
        write(self.v,'.recommendation/transactions/music/2026-02-02.json','{broken')
        self.f.commit(self.v)
        with self.assertRaises(ValueError):self.prepare()
