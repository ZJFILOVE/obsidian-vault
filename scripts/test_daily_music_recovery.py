"""Real Git tree regressions for partially committed two-repository publication."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import sys
import music_identity as m
import publication_bundle as b
import publication_recovery as r
from test_daily_music_identity import frozen, manifest, write


def evidence(root):
    head=m.git(root,'rev-parse','HEAD').decode().strip()
    tree=m.git(root,'rev-parse','HEAD^{tree}').decode().strip(); trees={}
    def visit(oid):
        entries=[]
        for row in m.git(root,'ls-tree','-z',oid).split(b'\0'):
            if not row: continue
            meta,name=row.split(b'\t'); mode,kind,sha=meta.decode().split()
            entries.append({'mode':mode,'type':kind,'sha':sha,'path':name.decode()})
            if kind=='tree':visit(sha)
        trees[oid]={'sha':oid,'truncated':False,'tree':entries}
    visit(tree)
    return {'head_before':head,'head_after':head,'commit':{'sha':head,'tree':{'sha':tree}},'trees':trees}


class MusicRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'vault';self.other=Path(self.tmp.name)/'music'
        self.roots={'ZJFILOVE/obsidian-vault':self.root,'ZJFILOVE/music-daily':self.other}
        old=manifest('2026-01-01'); state={'schema_version':1,'provider':'apple_music',
                                         'recommended':{t['canonical_id']:1 for t in old['tracks']}}
        for root in (self.root,self.other):root.mkdir();m.git(root,'init','-q')
        write(self.root,m.MANIFESTS+'/2026-01-01.json',old)
        write(self.root,'Music/Daily/2026-01-01.md','old note')
        write(self.root,m.STATE,state)
        write(self.other,'recommendations/2026/01/2026-01-01.json',old)
        write(self.other,'state/tracks.json',state)
        self.commit(self.root);self.commit(self.other)
        draft=frozen(manifest('2026-02-01',20000))
        state['recommended'].update({t['canonical_id']:1 for t in manifest('2026-02-01',20000)['tracks']})
        for key in draft['payloads']:
            if key.endswith('state/tracks.json'):draft['payloads'][key]=json.dumps(state)
        for target in draft['plan']['targets']:
            path=self.roots[target['repository']]/target['path']
            target['base_sha']=r.blob_sha(path.read_bytes()) if path.exists() else None
            target['target_sha']=r.blob_sha(draft['payloads'][target['repository']+':'+target['path']].encode())
        snap,heads=self.snapshot()
        self.bundle=b.freeze(draft['plan'],draft['payloads'],music_root=self.root,mirror_snapshot=snap,expected_heads=heads)
        self.bundle_path=self.root/m.PREPARED/'2026-02-01.json'
        write(self.root,m.PREPARED+'/2026-02-01.json',self.bundle);self.commit(self.root)
    def commit(self,root):
        m.git(root,'add','.')
        m.git(root,'-c','user.name=Test','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-qm','fixture')
    def snapshot(self):
        snap={'schema_version':1,'music':evidence(self.other),'vault':evidence(self.root)}
        return snap,{k:snap[k]['head_after'] for k in ('music','vault')}
    def apply(self,stage,predicate=lambda target:True):
        changed=set()
        for target in self.bundle['plan']['targets']:
            if target['stage']==stage and predicate(target):
                root=self.roots[target['repository']];changed.add(root)
                write(root,target['path'],self.bundle['payloads'][target['repository']+':'+target['path']])
        for root in changed:self.commit(root)
    def observations(self):
        result={}
        for t in self.bundle['plan']['targets']:
            path=self.roots[t['repository']]/t['path'];key=t['repository']+':'+t['path']
            result[key]={'status':'ok','sha':r.blob_sha(path.read_bytes())} if path.exists() else {'status':'missing','confirmed':True}
        return result
    def gate(self):
        snap,heads=self.snapshot()
        return m.recovery_gate(self.root,self.bundle,snap,heads,self.observations())
    def test_prepared_without_writes_allows_only_stage1(self):
        result=self.gate();self.assertEqual(result['planner']['next_stage'],1)
        self.assertEqual(len(result['allowed_writes']),2)
        self.assertTrue(all(t['stage']==1 for t in result['allowed_writes']))
    def test_stage1_committed_stage2_missing_can_resume(self):
        self.apply(1); result=self.gate()
        self.assertEqual(result['planner']['status'],'ready_to_resume')
        self.assertEqual(result['planner']['next_stage'],2)
        self.assertEqual(len(result['allowed_writes']),3)
        self.assertEqual(result['mirror_status'],'verified_frozen_transition_not_final_mirror_qa')
        self.assertTrue(all(t['stage']==2 for t in result['allowed_writes']))
    def test_lost_stage1_response_needs_no_receipt(self):
        self.apply(1)
        self.assertFalse((self.root/'.recommendation/transaction-runs').exists())
        self.assertEqual(self.gate()['planner']['next_stage'],2)
    def test_partial_stage1_contents_can_finish_only_stage1(self):
        self.apply(1,lambda t:t['path'].startswith('recommendations/'))
        result=self.gate();self.assertEqual(result['planner']['next_stage'],1)
        self.assertEqual([t['path'] for t in result['allowed_writes']],['state/tracks.json'])
    def test_partial_stage1_state_before_manifest(self):
        self.apply(1,lambda t:t['path']=='state/tracks.json')
        result=self.gate();self.assertEqual(result['planner']['next_stage'],1)
        self.assertEqual([t['path'] for t in result['allowed_writes']],['recommendations/2026/02/2026-02-01.json'])
    def test_partial_stage2_state_before_note_and_manifest(self):
        self.apply(1);self.apply(2,lambda t:t['path'].endswith('state/tracks.json'))
        result=self.gate();self.assertEqual(result['planner']['next_stage'],2)
        self.assertEqual(len(result['allowed_writes']),2)
    def test_partial_stage2_contents_can_finish_only_missing_targets(self):
        self.apply(1);self.apply(2,lambda t:t['path'].endswith('.md'))
        result=self.gate();self.assertEqual(result['planner']['next_stage'],2)
        self.assertEqual(len(result['allowed_writes']),2)
        self.assertTrue(all(not t['path'].endswith('.md') for t in result['allowed_writes']))
    def test_partial_stage2_manifest_before_state(self):
        self.apply(1);self.apply(2,lambda t:'/manifests/' in t['path'])
        self.assertEqual(len(self.gate()['allowed_writes']),2)
    def test_lost_final_response_is_noop_with_full_mirrors(self):
        self.apply(1);self.apply(2);result=self.gate()
        self.assertEqual(result['planner']['status'],'artifacts_match')
        self.assertEqual(result['allowed_writes'],[])
        self.assertEqual(result['mirror_status'],'passed_current_music_mirrors')
        self.assertEqual(result['content_qa'],'not_evaluated')
        snap,heads=self.snapshot()
        final=m.publication_gate(self.root,self.bundle['plan'],self.bundle['payloads'],snap,heads,
                                 bundle_digest=self.bundle['bundle_sha256'])
        self.assertEqual(final['mirror_status'],'passed_current_music_mirrors')
    def test_partial_mirrors_do_not_pass_final_gate(self):
        self.apply(1);snap,heads=self.snapshot()
        with self.assertRaisesRegex(ValueError,'manifest missing'):
            m.publication_gate(self.root,self.bundle['plan'],self.bundle['payloads'],snap,heads,
                               bundle_digest=self.bundle['bundle_sha256'])
    def test_unexpected_target_third_party_edit_blocked(self):
        self.apply(1);write(self.root,'Music/Daily/2026-02-01.md','user notes, do not overwrite');self.commit(self.root)
        with self.assertRaisesRegex(ValueError,'diverged'):self.gate()
    def test_unrelated_manifest_difference_blocked(self):
        self.apply(1);write(self.other,'recommendations/2026/01/2026-01-01.json',manifest('2026-01-01',90000));self.commit(self.other)
        with self.assertRaisesRegex(ValueError,'unrelated'):self.gate()
    def test_stage_order_violation_blocked(self):
        self.apply(2,lambda t:t['path'].endswith('.md'))
        with self.assertRaisesRegex(ValueError,'later stage'):self.gate()
    def test_stale_or_forged_observation_blocked(self):
        before=self.observations();self.apply(1);snap,heads=self.snapshot()
        with self.assertRaisesRegex(ValueError,'observation differs'):
            m.recovery_gate(self.root,self.bundle,snap,heads,before)
    def test_uncommitted_vault_note_change_blocked(self):
        self.apply(1);self.apply(2,lambda t:t['path'].endswith('.md'))
        write(self.root,'Music/Daily/2026-02-01.md','uncommitted manual change')
        snap,heads=self.snapshot()
        with self.assertRaisesRegex(ValueError,'differs'):
            m.recovery_gate(self.root,self.bundle,snap,heads,self.observations())
    def test_missing_snapshot_tree_is_not_confirmed_absence(self):
        self.apply(1);snap,heads=self.snapshot();snap['vault']['trees']={}
        with self.assertRaisesRegex(ValueError,'missing or truncated'):
            m.recovery_gate(self.root,self.bundle,snap,heads,self.observations())
    def test_moving_head_blocked(self):
        self.apply(1);snap,heads=self.snapshot();snap['vault']['head_after']='0'*40
        with self.assertRaisesRegex(ValueError,'head moved'):
            m.recovery_gate(self.root,self.bundle,snap,heads,self.observations())
    def test_reselected_payload_blocked(self):
        modified=copy.deepcopy(self.bundle); key='ZJFILOVE/obsidian-vault:Music/Daily/2026-02-01.md'
        modified['payloads'][key]+='\nchanged'
        for t in modified['plan']['targets']:
            if t['repository']+':'+t['path']==key:t['target_sha']=r.blob_sha(modified['payloads'][key].encode())
        modified['plan_sha256']=r.digest(modified['plan'])
        modified['bundle_sha256']=r.digest({k:v for k,v in modified.items() if k!='bundle_sha256'})
        snap,heads=self.snapshot()
        with self.assertRaisesRegex(ValueError,'exact original'):
            m.recovery_gate(self.root,modified,snap,heads,self.observations())
    def test_cli_stage2_resume_uses_verified_transition(self):
        self.apply(1);snap,heads=self.snapshot()
        snapshot_path=Path(self.tmp.name)/'snapshot.json';snapshot_path.write_text(json.dumps(snap))
        observations_path=Path(self.tmp.name)/'observations.json';observations_path.write_text(json.dumps(self.observations()))
        args=['publication_bundle.py',str(self.bundle_path),'--observations',str(observations_path),
              '--expected-bundle-digest',self.bundle['bundle_sha256'],'--music-root',str(self.root),
              '--mirror-snapshot',str(snapshot_path),'--music-head',heads['music'],'--vault-head',heads['vault']]
        with patch.object(sys,'argv',args),contextlib.redirect_stdout(io.StringIO()) as output:
            code=b.main()
        result=json.loads(output.getvalue());self.assertEqual(code,0)
        self.assertEqual(result['status'],'ready_to_resume');self.assertEqual(result['next_stage'],2)
        self.assertEqual(result['music_gate']['mirror_status'],'verified_frozen_transition_not_final_mirror_qa')

if __name__=='__main__':unittest.main()
