import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import music_identity as m
import publication_bundle as b
import publication_recovery as r
import check_daily_integrity as h
import check_publication_health as health

ROOT = Path(__file__).resolve().parents[1]


def manifest(day, start=10000, artist='Artist'):
    return {'schema_version': 1, 'provider': 'apple_music', 'date': day,
            'tracks': [{'position': i+1, 'artist': artist, 'title': str(start+i),
                        'canonical_id': artist+'::'+str(start+i),
                        'apple_music': {'song_id': str(start+i), 'storefront': 'cn',
                                        'url': 'https://music.apple.com/cn/song/'+str(start+i)}} for i in range(5)]}


def write(root, path, doc):
    p = root / path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False) if not isinstance(doc, str) else doc)


def frozen(doc):
    day = doc['date']; text = json.dumps(doc); state = json.dumps({'schema_version':1, 'provider':'apple_music',
                   'recommended': {t['canonical_id']:1 for t in doc['tracks']}})
    payloads = {key: state if key.endswith('state/tracks.json') else
                '\n'.join(t['apple_music']['url'] for t in doc['tracks']) if key.endswith('.md') else text
                for key in b.targets_for('music', day)}
    plan = {'schema_version':1, 'project':'music', 'date':day, 'operation_id':'music:'+day,
            'exposed_resource_ids':[t['canonical_id'] for t in doc['tracks']],
            'targets':[{'repository':k.split(':',1)[0], 'path':k.split(':',1)[1], 'stage':stage,
                        'base_sha':None, 'target_sha':r.blob_sha(payloads[k].encode())}
                       for k,stage in b.targets_for('music',day).items()]}
    body = {'schema_version':1,'plan':plan,'payloads':payloads,'plan_sha256':r.digest(plan)}
    return {**body,'bundle_sha256':r.digest(body)}


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root = Path(self.tmp.name)
        self.git('init','-q'); self.old = manifest('2026-01-01')
        write(self.root, m.MANIFESTS+'/2026-01-01.json', self.old)
        write(self.root, m.STATE, {'recommended':{t['canonical_id']:1 for t in self.old['tracks']}})
        self.commit()
    def git(self,*args):return m.git(self.root,*args)
    def commit(self):
        self.git('add','.');self.git('-c','user.name=Test','-c','user.email=test@example.invalid',
                                    '-c','commit.gpgsign=false','commit','-qm','fixture')
    def test_alias_older_than_window_rejected(self):
        for i in range(2,20):write(self.root,f'{m.MANIFESTS}/2026-01-{i:02}.json',manifest(f'2026-01-{i:02}',i*10000))
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root, manifest('2026-12-01',artist='翻译名'))
    def test_deleted_manifest_still_reserved(self):
        (self.root / (m.MANIFESTS+'/2026-01-01.json')).unlink();self.commit()
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root, manifest('2026-12-01'))
    def test_replaced_track_same_day_retained(self):
        write(self.root,m.MANIFESTS+'/2026-01-01.json',manifest('2026-01-01',20000));self.commit()
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root, manifest('2026-12-01'))
    def test_snapshots_are_one_occurrence(self):
        doc=copy.deepcopy(self.old);doc['extra']='format change'
        write(self.root,m.MANIFESTS+'/2026-01-01.json',doc);self.commit()
        rows=m.index(self.root)['records'];self.assertEqual(len(rows),5);self.assertEqual(len(rows[0]['sources']),2)
    def reserve(self):
        doc=manifest('2026-02-01',20000); bundle=frozen(doc)
        write(self.root,m.PREPARED+'/2026-02-01.json',bundle);self.commit();return doc,bundle
    def test_unfinished_prepared_reserves(self):
        self.reserve()
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root,manifest('2026-12-01',20000))
    def test_deleted_prepared_reserves(self):
        self.reserve();(self.root/(m.PREPARED+'/2026-02-01.json')).unlink();self.commit()
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root,manifest('2026-12-01',20000))
    def test_changed_prepared_rejected(self):
        self.reserve();write(self.root,m.PREPARED+'/2026-02-01.json',frozen(manifest('2026-02-01',30000)))
        with self.assertRaisesRegex(ValueError,'rewritten'):m.index(self.root)
    def test_same_operation_exact_recovery(self):
        doc,bundle=self.reserve()
        self.assertEqual(m.check_selection(self.root,doc,bundle_digest=bundle['bundle_sha256'])['status'],'passed_recording_identity')
        with self.assertRaisesRegex(ValueError,'digest'):m.check_selection(self.root,doc)
        doc['tracks'][0]['artist']='alias'
        with self.assertRaisesRegex(ValueError,'selection changed'):m.check_selection(self.root,doc,bundle_digest=bundle['bundle_sha256'])
    def test_same_operation_id_without_bundle_not_exempt(self):
        with self.assertRaisesRegex(ValueError,'adoption'):m.check_selection(self.root,self.old)
    def test_unrelated_future_date_passes(self):
        self.assertEqual(m.check_selection(self.root,manifest('2026-12-01',30000))['status'],'passed_recording_identity')
    def test_new_freeze_requires_gate(self):
        x=frozen(manifest('2026-12-01',30000))
        with self.assertRaisesRegex(ValueError,'pinned mirror'):b.freeze(x['plan'],x['payloads'])
    def test_recovery_binds_all_frozen_payloads(self):
        doc,bundle=self.reserve()
        payloads=copy.deepcopy(bundle['payloads'])
        key=next(k for k in payloads if k.endswith('.md'));payloads[key]+='\nchanged'
        plan=copy.deepcopy(bundle['plan'])
        for target in plan['targets']:
            if target['repository']+':'+target['path']==key:target['target_sha']=r.blob_sha(payloads[key].encode())
        with self.assertRaisesRegex(ValueError,'exact original'):
            m.publication_gate(self.root,plan,payloads,{}, {},bundle_digest=bundle['bundle_sha256'])
    def test_old_bundle_verification_does_not_certify_content(self):b.verify(frozen(self.old))
    def test_legacy_unknown_id_fails_closed(self):
        doc=manifest('2026-01-02',30000);doc['tracks'][0]['apple_music']['song_id']=None
        write(self.root,m.MANIFESTS+'/2026-01-02.json',doc)
        self.assertEqual(m.index(self.root)['status'],'incomplete_identity_evidence')
        with self.assertRaisesRegex(ValueError,'incomplete'):m.check_selection(self.root,manifest('2026-12-01',40000))
    def test_retired_note_identity_covers_state(self):
        state=json.loads((self.root/m.STATE).read_text());state['recommended']['Old::song']=1;write(self.root,m.STATE,state)
        path='Music/Daily/2025-12-01.md';write(self.root,path,'## 1. Old — song\nhttps://music.apple.com/cn/song/99999\n');self.commit()
        (self.root/path).unlink();self.commit()
        self.assertEqual(m.index(self.root)['status'],'complete_available_git_history')
        doc=manifest('2026-12-01',99999,artist='alias')
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(self.root,doc)
    def test_shallow_history_fails(self):
        original=m.git
        with patch.object(m,'git',side_effect=lambda root,*a:b'true' if a==('rev-parse','--is-shallow-repository') else original(root,*a)):
            with self.assertRaisesRegex(ValueError,'full Git'):m.index(self.root)
    def test_missing_identity_state_fails_closed(self):
        write(self.root,m.STATE,{'recommended':{'Lost::song':1}})
        with self.assertRaisesRegex(ValueError,'incomplete'):m.check_selection(self.root,manifest('2026-12-01',30000))


class IncidentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.doc=json.loads((ROOT/m.INCIDENT).read_text())
        paths=[m.INCIDENT]+[x['path'] for x in self.doc['occurrences']]+[self.doc[k]['path'] for k in ('prepared','failure_evidence')]
        for p in paths:
            target=self.root/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
    def test_exact_incident(self):self.assertEqual(m.incident(self.root)['content_qa'],'failed')
    def test_third_occurrence_not_covered(self):
        first,second=[(x['date'],x['position'],x['canonical_id']) for x in self.doc['occurrences']]
        self.assertTrue(m.exact_incident_pair(self.doc,first,second))
        self.assertFalse(m.exact_incident_pair(self.doc,second,('2026-11-07',3,second[2])))
    def test_scope_expansion_rejected(self):
        self.doc['occurrences'].append(self.doc['occurrences'][0]);write(self.root,m.INCIDENT,self.doc)
        with self.assertRaisesRegex(ValueError,'scope'):m.incident(self.root)
    def test_evidence_tampering_rejected(self):
        for key in ('prepared','failure_evidence'):
            p=self.root/self.doc[key]['path'];old=p.read_bytes();p.write_bytes(old+b' ')
            with self.assertRaisesRegex(ValueError,'evidence'):m.incident(self.root)
            p.write_bytes(old)
    def test_manifest_bytes_tampering_rejected(self):
        for row in self.doc['occurrences']:
            p=self.root/row['path'];old=p.read_bytes();p.write_bytes(old+b' ')
            with self.assertRaisesRegex(ValueError,'manifest'):m.incident(self.root)
            p.write_bytes(old)
    def test_success_receipt_rejected(self):
        write(self.root,'.recommendation/runs/2026-11-06-music.json',{'status':'success'})
        with self.assertRaisesRegex(ValueError,'success QA'):m.incident(self.root)
    def test_failed_day_cannot_be_certified(self):
        with self.assertRaisesRegex(ValueError,'remains content_qa=failed'):
            m.check_selection(ROOT,json.loads((ROOT/(m.MANIFESTS+'/2026-11-06.json')).read_text()),
                              bundle_digest=self.doc['prepared']['bundle_sha256'])
    def test_real_snapshot_keeps_failed_day_and_preserves_history(self):
        result=h.audit(ROOT,'2026-09-11','ddc17f5077c993b7903883138f5588aaa0b3024c')
        self.assertEqual(result['historical_failed_publications'][0]['content_qa'],'failed')
    def test_new_day_not_blocked_by_registered_incident(self):
        # A complete-history fixture with the exact accident, no unrelated legacy gap.
        docs=[json.loads((self.root/x['path']).read_text()) for x in self.doc['occurrences']]
        write(self.root,m.STATE,{'recommended':{t['canonical_id']:1 for doc in docs for t in doc['tracks']}})
        m.git(self.root,'init','-q');m.git(self.root,'add','.')
        m.git(self.root,'-c','user.name=Test','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-qm','fixture')
        result=m.check_selection(self.root,manifest('2026-12-01',999999999000))
        self.assertEqual(result['historical_failed_dates'],['2026-11-06'])
    def test_real_third_repeat_rejected(self):
        doc=manifest('2026-12-01',714861225,'localized alias')
        with self.assertRaisesRegex(ValueError,'reuse'):m.check_selection(ROOT,doc)
    def test_independent_reporting_after_failure(self):
        with patch.object(health.integrity,'audit',side_effect=ValueError('integrity fails')),patch.object(health.bundles,'audit_journal',return_value={'status':'bundles_ran'}):
            result=health.audit(ROOT)
            self.assertEqual(result['checks']['immutable_bundles']['status'],'bundles_ran')
            self.assertEqual(result['checks']['permanent_music_identity']['status'],'incomplete_identity_evidence')

if __name__ == '__main__':unittest.main()


class GateTests(unittest.TestCase):
    setUp = IdentityTests.setUp
    git = IdentityTests.git
    commit = IdentityTests.commit
    def snapshot(self):
        """Build complete evidence using actual Git objects in two local repositories."""
        for p in (self.root / m.MANIFESTS).glob('*.json'):
            write(self.root,'Music/Daily/'+p.stem+'.md','note')
        self.commit()
        other=self.root/'other';other.mkdir();m.git(other,'init','-q')
        for p in (self.root/m.MANIFESTS).glob('*.json'):
            write(other,'recommendations/'+p.stem[:4]+'/'+p.stem[5:7]+'/'+p.name,p.read_text())
        write(other,'state/tracks.json',(self.root/m.STATE).read_text())
        m.git(other,'add','.');m.git(other,'-c','user.name=Test','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-qm','mirror')
        def evidence(root):
            head=m.git(root,'rev-parse','HEAD').decode().strip();tree=m.git(root,'rev-parse','HEAD^{tree}').decode().strip();trees={}
            def visit(oid):
                entries=[]
                for row in m.git(root,'ls-tree','-z',oid).split(b'\0'):
                    if not row:continue
                    meta,name=row.split(b'\t');mode,kind,sha=meta.decode().split()
                    entries.append({'mode':mode,'type':kind,'sha':sha,'path':name.decode()})
                    if kind=='tree':visit(sha)
                trees[oid]={'sha':oid,'truncated':False,'tree':entries}
            visit(tree)
            return {'head_before':head,'head_after':head,'commit':{'sha':head,'tree':{'sha':tree}},'trees':trees}
        return {'schema_version':1,'music':evidence(other),'vault':evidence(self.root)}
    def test_real_positive_freeze_and_bound_receipt(self):
        snapshot=self.snapshot();heads={k:snapshot[k]['head_after'] for k in ('music','vault')}
        bundle=frozen(manifest('2026-12-01',30000))
        # Preserve baseline history when adding the new day's state entries.
        state=json.loads((self.root/m.STATE).read_text());state['schema_version']=1;state['provider']='apple_music'
        for t in manifest('2026-12-01',30000)['tracks']:state['recommended'][t['canonical_id']]=1
        for key in bundle['payloads']:
            if key.endswith('state/tracks.json'):bundle['payloads'][key]=json.dumps(state)
        for target in bundle['plan']['targets']:
            key=target['repository']+':'+target['path']
            target['target_sha']=r.blob_sha(bundle['payloads'][key].encode())
            if target['path'].endswith('state/tracks.json'):target['base_sha']=r.blob_sha((self.root/m.STATE).read_bytes())
        result=b.freeze(bundle['plan'],bundle['payloads'],music_root=self.root,mirror_snapshot=snapshot,expected_heads=heads)
        b.verify(result)
        gate=m.publication_gate(self.root,bundle['plan'],bundle['payloads'],snapshot,heads)
        self.assertEqual(gate['status'],'passed_music_publication_gate');self.assertEqual(gate['content_qa'],'not_evaluated')
        self.assertEqual(gate['payloads_sha256'],r.digest(bundle['payloads']))
        with self.assertRaisesRegex(ValueError,'versions'):
            m.publication_gate(self.root,bundle['plan'],bundle['payloads'],snapshot,{**heads,'music':'0'*40})
        changed=copy.deepcopy(snapshot);changed['music']['head_after']='0'*40
        with self.assertRaisesRegex(ValueError,'head moved'):
            m.publication_gate(self.root,bundle['plan'],bundle['payloads'],changed,heads)
        write(self.root,m.STATE,{'recommended':{}})
        with self.assertRaisesRegex(ValueError,'local manifest/state'):
            m.publication_gate(self.root,bundle['plan'],bundle['payloads'],snapshot,heads)
