import base64
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import connector_music_history as h
import music_connector as c
import music_identity as m
import music_publication as p
import publication_bundle as b
import test_daily_music_recovery as fixtures
from test_daily_music_identity import manifest, write


def export(root, key, cache):
    repo=cache/h.REPOS[key].split('/')[1]
    def save(kind,oid,data):
        path=repo/kind/(oid+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data))
    heads=m.git(root,'rev-parse','HEAD').decode().strip()
    seen=set()
    def tree(oid):
        if oid in seen:return
        seen.add(oid);rows=[]
        for line in filter(None,m.git(root,'ls-tree','-z',oid).split(b'\0')):
            meta,name=line.split(b'\t',1);mode,kind,sha=meta.decode().split()
            rows.append(dict(path=name.decode(),mode=mode,type=kind,sha=sha))
            if kind=='tree':tree(sha)
            elif kind=='blob':
                raw=m.git(root,'cat-file','blob',sha)
                save('blobs',sha,dict(sha=sha,encoding='base64',size=len(raw),content=base64.b64encode(raw).decode()))
        save('trees',oid,dict(sha=oid,tree=rows,truncated=False))
    for oid in m.git(root,'rev-list','HEAD').decode().splitlines():
        raw=m.git(root,'cat-file','commit',oid);info=h.parse_commit(raw,oid)
        save('commits',oid,dict(sha=oid,raw_base64=base64.b64encode(raw).decode()))
        tree(info['tree'])
    return heads


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.MusicRecoveryTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.v,self.mu=self.f.root,self.f.other
        self.cache=Path(self.f.tmp.name)/'cache';self.heads=self.export()
        self.day='2026-03-01';self.calls=[]
    def export(self):return {k:export(root,k,self.cache) for k,root in [('vault',self.v),('music',self.mu)]}
    def fetch(self,url):
        self.calls.append(url)
        key=next(k for k,repo in h.REPOS.items() if '/'+repo+'/' in url)
        self.assertTrue(url.endswith('/git/ref/heads/main'),'immutable cache unexpectedly incomplete: '+url)
        return dict(ref='refs/heads/main',object=dict(type='commit',sha=self.heads[key]))
    def prepare(self,day=None):return c.prepare(self.cache,day or self.day,self.fetch)[0]
    def draft(self,start=30000):
        doc=manifest(self.day,start);return json.dumps(doc),'\n'.join(x['apple_music']['url'] for x in doc['tracks'])
    def change_cache(self,key,kind,oid,change):
        path=self.cache/h.REPOS[key].split('/')[1]/kind/(oid+'.json')
        data=json.loads(path.read_text());change(data);path.write_text(json.dumps(data))
    def test_prepare_and_freeze_with_every_subprocess_forbidden(self):
        with patch('subprocess.Popen',side_effect=AssertionError('runtime must not run Git or any subprocess')):
            report=self.prepare();self.assertEqual(report['mode'],'ready_before_selection')
            frozen=c.freeze(report,self.cache,*self.draft(),self.fetch);b.verify(frozen)
        self.assertEqual(len(self.calls),10) # live refs: prepare before/after + freeze before/after/final
        self.assertEqual(frozen['plan']['project'],'music')
    def test_existing_retry_preserves_exact_bundle(self):
        report=self.prepare('2026-02-01')
        self.assertEqual(report['mode'],'resume_existing_bundle')
        self.assertEqual(report['original_bundle'],self.f.bundle)
        self.assertEqual(report['planner']['next_stage'],1)
        with self.assertRaisesRegex(ValueError,'recover an existing'):
            c.freeze(report,self.cache,*self.draft(),self.fetch)
    def test_stage_one_retry(self):
        self.f.apply(1);self.heads=self.export()
        self.assertEqual(self.prepare('2026-02-01')['planner']['next_stage'],2)
    def test_completed_retry_noop(self):
        self.f.apply(1);self.f.apply(2);self.heads=self.export()
        self.assertEqual(self.prepare('2026-02-01')['planner']['status'],'artifacts_match')
    def test_stale_refs_before_freeze(self):
        report=self.prepare();write(self.v,'new.md','unrelated');self.f.commit(self.v);self.heads=self.export()
        with self.assertRaisesRegex(ValueError,'stale'):c.freeze(report,self.cache,*self.draft(),self.fetch)
    def test_refs_move_during_prepare(self):
        def fetch(url):
            data=self.fetch(url)
            if len(self.calls)>2:data['object']['sha']='a'*40
            return data
        with self.assertRaisesRegex(ValueError,'HEAD changed'):c.prepare(self.cache,self.day,fetch)
    def test_refs_move_after_candidate(self):
        report=self.prepare();self.calls=[]
        def fetch(url):
            data=self.fetch(url)
            if len(self.calls)>4:data['object']['sha']='a'*40
            return data
        with self.assertRaisesRegex(ValueError,'before frozen output'):c.freeze(report,self.cache,*self.draft(),fetch)
    def test_no_callback_cannot_use_old_ref_files(self):
        with self.assertRaisesRegex(ValueError,'live GitHub connector'):c.prepare(self.cache,self.day,None)
    def test_wrong_ref(self):
        with self.assertRaisesRegex(ValueError,'unexpected live ref'):
            c.prepare(self.cache,self.day,lambda url:dict(ref='refs/heads/other',object=dict(type='commit',sha='a'*40)))
    def test_missing_parent_fails_closed(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None)
        parent=repo.commit(repo.head)['parents'][0]
        (repo.cache/'commits'/(parent+'.json')).unlink()
        with self.assertRaisesRegex(ValueError,'missing connector object'):repo.collect()
    def test_valid_other_commit_cannot_substitute_requested_cache_key(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None)
        parent=repo.commit(repo.head)['parents'][0]
        target=repo.cache/'commits'/(repo.head+'.json')
        target.write_bytes((repo.cache/'commits'/(parent+'.json')).read_bytes())
        with self.assertRaisesRegex(ValueError,'cached object SHA differs'):self.prepare()
    def test_raw_commit_hash_mismatch(self):
        self.change_cache('vault','commits',self.heads['vault'],lambda d:d.update(raw_base64=base64.b64encode(b'tree '+'a'.encode()*40+b'\n\n').decode()))
        with self.assertRaisesRegex(ValueError,'raw commit hash mismatch'):self.prepare()
    def test_truncated_tree(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);oid=repo.commit(repo.head)['tree']
        self.change_cache('vault','trees',oid,lambda d:d.update(truncated=True))
        with self.assertRaisesRegex(ValueError,'truncated'):self.prepare()
    def test_omitted_tree_entry(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);oid=repo.commit(repo.head)['tree']
        self.change_cache('vault','trees',oid,lambda d:d['tree'].pop())
        with self.assertRaisesRegex(ValueError,'tree hash mismatch'):self.prepare()
    def test_missing_subtree_not_absence(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);row=repo.lookup(repo.head,'Music/Daily')
        (repo.cache/'trees'/(row['sha']+'.json')).unlink()
        with self.assertRaisesRegex(ValueError,'missing connector object'):repo.collect()
    def test_blob_omission_not_absence(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);row=repo.lookup(repo.head,m.STATE)
        (repo.cache/'blobs'/(row['sha']+'.json')).unlink()
        with self.assertRaisesRegex(ValueError,'missing connector object'):repo.collect()
    def test_live_connector_decoded_utf8_blob_shape(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);row=repo.lookup(repo.head,m.STATE)
        target=repo.cache/'blobs'/(row['sha']+'.json')
        data=json.loads(target.read_text());raw=base64.b64decode(data['content'])
        target.write_text(json.dumps({'content':[{'type':'text','text':'Action completed.'}],
          'structuredContent':{'content':raw.decode(),'url':'https://api.github.com/repos/ZJFILOVE/obsidian-vault/git/blobs/'+row['sha']},'isError':False}))
        self.assertEqual(self.prepare()['mode'],'ready_before_selection')
        bad=json.loads(target.read_text());bad['structuredContent']['content']+='\n';target.write_text(json.dumps(bad))
        with self.assertRaises(ValueError):self.prepare()
    def test_blob_bytes_mismatch(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);row=repo.lookup(repo.head,m.STATE)
        self.change_cache('vault','blobs',row['sha'],lambda d:d.update(content='e30='))
        with self.assertRaisesRegex(ValueError,'blob hash/size mismatch'):self.prepare()
    def test_historical_reservation_blocks_new_artist(self):
        report=self.prepare();doc=manifest(self.day,20000,artist='translated')
        with self.assertRaisesRegex(ValueError,'reuse'):
            c.freeze(report,self.cache,json.dumps(doc),'\n'.join(x['apple_music']['url'] for x in doc['tracks']),self.fetch)
    def test_deleted_prepared_still_reserved(self):
        (self.v/m.PREPARED/'2026-02-01.json').unlink();self.f.commit(self.v);self.heads=self.export()
        with self.assertRaisesRegex(ValueError,'retired exposure'):self.prepare('2026-02-01')
        with self.assertRaisesRegex(ValueError,'reuse'):
            c.freeze(self.prepare(),self.cache,*self.draft(20000),self.fetch)
    def test_music_repo_only_deleted_exposure_stays_reserved(self):
        path='recommendations/2025/12/2025-12-31.json'
        write(self.mu,path,manifest('2025-12-31',50000));self.f.commit(self.mu)
        (self.mu/path).unlink();self.f.commit(self.mu);self.heads=self.export()
        report=self.prepare()
        with self.assertRaisesRegex(ValueError,'reuse'):c.freeze(report,self.cache,*self.draft(50000),self.fetch)
    def test_same_blob_two_deleted_note_paths_remain_distinct(self):
        text='## 1. Retired — same\nhttps://music.apple.com/cn/song/987654321\n'
        paths=['Music/Daily/2025-12-01.md','Music/Daily/2025-12-02.md']
        for path in paths:write(self.v,path,text);self.f.commit(self.v)
        for path in paths:(self.v/path).unlink()
        self.f.commit(self.v);self.heads=self.export()
        rows=[x for x in self.prepare()['identity_index']['records'] if x['identity']=='apple_music:cn:987654321']
        self.assertEqual({x['date'] for x in rows},{'2025-12-01','2025-12-02'})
    def test_symlink_materialization_rejected_before_read(self):
        repos={k:h.Repository(k,head,self.cache,None).collect() for k,head in self.heads.items()}
        history=h.materialize(repos,Path(self.f.tmp.name)/'materialized')
        root=history.roots['vault'];target=root/m.STATE;target.unlink();target.symlink_to('/nonexistent/private-data')
        with self.assertRaisesRegex(ValueError,'contains symlink'):history.validate_root(root)
    def test_prepared_reformatted_is_not_immutable(self):
        path=self.v/m.PREPARED/'2026-02-01.json';path.write_text(path.read_text()+'\n');self.f.commit(self.v);self.heads=self.export()
        with self.assertRaisesRegex(ValueError,'PREPARED bytes rewritten'):self.prepare()
    def test_other_project_bad_data_unchanged_and_not_evaluated(self):
        write(self.v,'.recommendation/transactions/english/2026-02-02.json','{broken');self.f.commit(self.v);self.heads=self.export()
        report=self.prepare();self.assertEqual(report['mode'],'ready_before_selection')
        self.assertEqual(report['bundle_health']['other_projects'],'not_evaluated_or_changed')
    def test_no_output_overwrite_or_cache_write(self):
        output=Path(self.f.tmp.name)/'output.json';p.write_output(output,{},[self.cache])
        with self.assertRaises(FileExistsError):p.write_output(output,{},[self.cache])
        with self.assertRaisesRegex(ValueError,'outside'):p.write_output(self.cache/'output.json',{},[self.cache])
    def test_unused_binary_attachment_does_not_need_blob_download(self):
        path=self.v/'Music/Daily/art.png';path.write_bytes(b'\x89PNG\r\n\x1a\n\xff\x00')
        self.f.commit(self.v);self.heads=self.export()
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);row=repo.lookup(repo.head,'Music/Daily/art.png')
        (repo.cache/'blobs'/(row['sha']+'.json')).unlink()
        self.assertEqual(self.prepare()['mode'],'ready_before_selection')
    def test_corrupted_raw_commit_cache_is_rejected(self):
        repo=h.Repository('vault',self.heads['vault'],self.cache,None);repo.commit(repo.head)
        (repo.cache/'commit-raw'/repo.head).write_bytes(b'invalid')
        with self.assertRaisesRegex(ValueError,'raw commit hash mismatch'):self.prepare()
    def test_materialized_path_omission(self):
        repos={k:h.Repository(k,head,self.cache,None).collect() for k,head in self.heads.items()}
        history=h.materialize(repos,Path(self.f.tmp.name)/'materialized')
        (history.roots['vault']/m.STATE).unlink()
        with self.assertRaisesRegex(ValueError,'changed or omitted'):history.validate_root(history.roots['vault'])
    def test_materialized_extra_or_modified_files_rejected(self):
        repos={k:h.Repository(k,head,self.cache,None).collect() for k,head in self.heads.items()}
        history=h.materialize(repos,Path(self.f.tmp.name)/'materialized')
        root=history.roots['vault']
        for path in (m.MANIFESTS+'/2026-03-02.json',m.PREPARED+'/2026-03-02.json'):
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}')
            with self.assertRaisesRegex(ValueError,'changed or omitted'):history.validate_root(root)
            target.unlink()
        target=root/m.STATE;target.write_bytes(target.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError,'changed or omitted'):history.validate_root(root)
    def test_merge_second_parent_removed_exposure_reserved(self):
        main=m.git(self.v,'branch','--show-current').decode().strip()
        m.git(self.v,'checkout','-b','exposure-side')
        write(self.v,m.MANIFESTS+'/2026-02-03.json',manifest('2026-02-03',40000))
        self.f.commit(self.v)
        (self.v/m.MANIFESTS/'2026-02-03.json').unlink();self.f.commit(self.v)
        side=m.git(self.v,'rev-parse','HEAD').decode().strip()
        m.git(self.v,'checkout',main);write(self.v,'unrelated.md','main change');self.f.commit(self.v)
        m.git(self.v,'merge','--no-ff','-m','merge historical exposure','exposure-side');self.heads=self.export()
        report=self.prepare();self.assertTrue(any(x['identity']=='apple_music:cn:40000' for x in report['identity_index']['records']))
        with self.assertRaisesRegex(ValueError,'reuse'):c.freeze(report,self.cache,*self.draft(40000),self.fetch)
        repo=h.Repository('vault',self.heads['vault'],self.cache,None)
        self.assertIn(side,repo.commit(repo.head)['parents'])
        (repo.cache/'commits'/(side+'.json')).unlink()
        with self.assertRaisesRegex(ValueError,'missing connector object'):repo.collect()
    def test_missing_seed_page_cannot_truncate_parent_closure(self):
        # Commit-list pages are optional acceleration, never history boundaries.
        repo=h.Repository('vault',self.heads['vault'],self.cache,None)
        parent=repo.commit(repo.head)['parents'][0]
        target=repo.cache/'commits'/(parent+'.json');saved=json.loads(target.read_text());target.unlink()
        requested=[]
        def callback(url):
            requested.append(url);self.assertTrue(url.endswith('/commits/'+parent));return saved
        repo.fetch=callback;repo.collect()
        self.assertEqual(len(requested),1);self.assertIn(parent,repo.commits)
    def test_signed_commit_reconstruction(self):
        payload='tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\nauthor A <a@b> 0 +0000\ncommitter A <a@b> 0 +0000\n\nmsg\n'
        signature='-----BEGIN PGP SIGNATURE-----\nsignature\n-----END PGP SIGNATURE-----\n'
        head,body=payload.split('\n\n',1)
        raw=(head+'\ngpgsig '+signature.replace('\n','\n ').rstrip(' ')+'\n'+body).encode()
        data=dict(sha=h.object_sha('commit',raw),tree=dict(sha='4b825dc642cb6eb9a060e54bf8d69288fbee4904'),parents=[],verification=dict(payload=payload,signature=signature))
        self.assertEqual(h.raw_commit(data)[0],raw)
    def test_list_entry_commit_normalization(self):
        raw=b'tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\nauthor A <a@b> 0 +0000\ncommitter A <a@b> 0 +0000\n\nmessage\n'
        metadata=dict(tree=dict(sha='4b825dc642cb6eb9a060e54bf8d69288fbee4904'),author=dict(name='A',email='a@b',date='1970-01-01T00:00:00Z'),committer=dict(name='A',email='a@b',date='1970-01-01T00:00:00Z'),message='message')
        self.assertEqual(h.raw_commit(dict(sha=h.object_sha('commit',raw),parents=[],commit=metadata))[0],raw)
    def test_rpc_rejects_replayed_request_id(self):
        rpc=c.ConnectorRPC(io.StringIO('{"id":"old","response":{}}\n'),io.StringIO())
        with self.assertRaisesRegex(ValueError,'replayed'):rpc('https://api.github.com/test')
    def test_unsigned_commit_reconstructed_by_hash(self):
        raw=b'tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\nauthor A <a@b> 0 +0800\ncommitter A <a@b> 0 +0800\n\nmessage'
        doc=dict(sha=h.object_sha('commit',raw),tree=dict(sha='4b825dc642cb6eb9a060e54bf8d69288fbee4904'),parents=[],author=dict(name='A',email='a@b',date='1970-01-01T00:00:00Z'),committer=dict(name='A',email='a@b',date='1970-01-01T00:00:00Z'),message='message')
        self.assertEqual(h.raw_commit(doc)[0],raw)

if __name__=='__main__':unittest.main()


class HostBootstrapTests(unittest.TestCase):
    """The host installs exact bytes before running the read-only Music CLI."""
    def setUp(self):
        source = (Path(__file__).parent / 'connector_host_bridge.js').read_text()
        python = source.split('const PYTHON = String.raw`', 1)[1].split('\n`;\n', 1)[0]
        self.ns = {'__name__': 'bootstrap_unit_test'}
        exec(compile(python, 'connector_host_bridge.js:PYTHON', 'exec'), self.ns)
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
    def test_exact_trailing_and_no_trailing_newline(self):
        for i, raw in enumerate((b'one\n', b'two', b'three\n\n', '中文'.encode())):
            oid = h.object_sha('blob', raw)
            response = {'structuredContent': {'content': raw.decode()}}
            out = self.root / str(i)
            self.ns['install_blob'](response, oid, out)
            self.assertEqual(out.read_bytes(), raw)
            self.assertEqual(h.object_sha('blob', out.read_bytes()), oid)
    def test_base64_source_and_tamper(self):
        raw = b'no final newline'; oid = h.object_sha('blob', raw)
        response = dict(sha=oid, encoding='base64', size=len(raw), content=base64.b64encode(raw).decode())
        self.ns['install_blob'](response, oid, self.root/'good')
        self.assertEqual((self.root/'good').read_bytes(), raw)
        response['content'] = base64.b64encode(raw+b'\n').decode()
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.ns['install_blob'](response, oid, self.root/'bad')
        self.assertFalse((self.root/'bad').exists())
    def test_full_cold_source_bootstrap(self):
        objects = {}; paths = {}
        for path in self.ns['FILES']:
            source = Path(__file__).parent.parent/path
            raw = source.read_bytes() if source.exists() else b'{"version":2,"strict_from":"2026-01-01"}'
            oid = h.object_sha('blob', raw)
            objects['blobs/'+oid] = {'structuredContent':{'content':raw.decode()}}
            paths[path] = oid
        def tree(prefix):
            names = sorted({path[len(prefix):].split('/')[0] for path in paths if path.startswith(prefix)})
            rows = []
            for name in names:
                full = prefix + name
                if full in paths: rows.append(dict(path=name, mode='100644', type='blob', sha=paths[full]))
                else: rows.append(dict(path=name, mode='040000', type='tree', sha=tree(full+'/')))
            sha = h.mirror.tree_sha(rows); objects['trees/'+sha] = dict(sha=sha, tree=rows, truncated=False)
            return sha
        root = tree('')
        raw = ('tree '+root+'\nauthor Unit Test <test@example.invalid> 1 +0000\ncommitter Unit Test <test@example.invalid> 1 +0000\n\nBootstrap test\n').encode()
        commit = h.object_sha('commit', raw)
        objects['commits/'+commit] = dict(sha=commit, tree={'sha':root}, raw_base64=base64.b64encode(raw).decode())
        calls = []
        def fetch(url):
            key = url.split('/git/',1)[1]; calls.append(key); return objects[key]
        with patch('subprocess.Popen', side_effect=AssertionError('bootstrap does not need subprocess')):
            runtime, manifest = self.ns['bootstrap'](commit, fetch, self.root/'runtime')
        self.assertEqual(manifest['source_commit'], commit)
        self.assertEqual(set(manifest['files']), set(paths))
        self.assertEqual(set(calls), set(objects))
        self.assertFalse((runtime/'.git').exists())
        for path, oid in paths.items():
            self.assertEqual(h.object_sha('blob', (runtime/path).read_bytes()), oid)
        # A separate isolated interpreter cannot reuse this suite's sys.modules.
        import subprocess, sys
        probe = ("import sys,pathlib,subprocess,importlib; "
                 "sys.path.insert(0,sys.argv[1]); "
                 "subprocess.Popen=lambda *a,**k: (_ for _ in ()).throw(AssertionError('no runtime subprocess')); "
                 "names=sys.argv[2:]; "
                 "mods=[importlib.import_module(n) for n in names]; "
                 "assert all(pathlib.Path(m.__file__).resolve().parent==pathlib.Path(sys.argv[1]).resolve() for m in mods); "
                 "print('isolated installed source imports passed')")
        names = [Path(path).stem for path in paths if path.endswith('.py')]
        result = subprocess.run([sys.executable, '-I', '-c', probe, str(runtime/'scripts'), *names],
                                text=True, capture_output=True, check=True)
        self.assertIn('isolated installed source imports passed', result.stdout)
    def test_source_tree_tampering_and_truncation(self):
        rows = [dict(path='x', mode='100644', type='blob', sha='a'*40)]
        oid = h.mirror.tree_sha(rows)
        with self.assertRaisesRegex(ValueError, 'truncated'):
            self.ns['tree_entries'](dict(sha=oid, tree=rows, truncated=True), oid)
        rows[0]['path'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.ns['tree_entries'](dict(sha=oid, tree=rows, truncated=False), oid)
    def test_forged_source_commit_is_rejected_before_code_fetch(self):
        expected = 'a'*40; calls = []
        raw = b'tree bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n\nforged\n'
        forged = dict(sha=expected, tree={'sha':'b'*40}, raw_base64=base64.b64encode(raw).decode())
        def fetch(url):
            calls.append(url)
            self.assertTrue(url.endswith('/commits/'+expected), 'must not request substituted code')
            return forged
        with self.assertRaisesRegex(ValueError, 'commit hash mismatch'):
            self.ns['bootstrap'](expected, fetch, self.root/'forged')
        self.assertEqual(len(calls), 1)
        self.assertFalse(any(path.name=='scripts' for path in (self.root/'forged').rglob('*')))
    def test_source_commit_binding_rejects_changed_tree(self):
        raw = b'tree aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n\nknown\n'
        expected = h.object_sha('commit', raw)
        forged = dict(sha=expected, tree={'sha':'b'*40}, raw_base64=base64.b64encode(raw).decode())
        with self.assertRaisesRegex(ValueError, 'tree mismatch'):
            self.ns['commit_bytes'](forged, expected)
    def test_source_runtime_symlink_parent_rejected(self):
        external = self.root/'external'; external.mkdir()
        linked = self.root/'linked'; linked.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink source runtime parent'):
            self.ns['bootstrap']('a'*40, lambda _: self.fail('no fetch before path check'), linked/'nested')
        self.assertEqual(list(external.iterdir()), [])
