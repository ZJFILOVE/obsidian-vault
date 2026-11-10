"""Hash-verified GitHub connector history; never executes Git or reads credentials.

A transport is a callable(url) -> original GitHub connector response. Immutable
objects may be cached, but every ref observation always calls the transport.
No commit-list pagination is trusted: every parent edge is followed to a root.
"""
from __future__ import annotations
import base64
import datetime as dt
import hashlib
import itertools
import json
from pathlib import Path
import re
import check_remote_music_snapshot as mirror
import publication_recovery as r
import validate_daily_recommendations as v

REPOS = {'vault': 'ZJFILOVE/obsidian-vault', 'music': 'ZJFILOVE/music-daily'}
HISTORY_DIRS = {'vault': ('Music/Daily', '.recommendation/transactions/music'),
                'music': ('recommendations', '.recommendation/transactions/music')}
CURRENT_DIRS = {'vault': HISTORY_DIRS['vault'],
                'music': HISTORY_DIRS['music'] + ('state',)}
CURRENT_FILES = {'vault': ('.recommendation/incidents/music-2026-11-06-714861225.json',
                          '.recommendation/transaction-corrections/music/2026-11-06/withdraw-714861225.json',
                          '.recommendation/transaction-runs/music/2026-11-06/qa-blocked-1793927282462.json',
                          '.recommendation/runs/2026-11-06-music.json'), 'music': ()}


def unwrap(value):
    r.require(isinstance(value, dict) and not value.get('isError'), 'connector read failed')
    if 'structuredContent' in value:
        value = value['structuredContent']
        r.require(isinstance(value, dict), 'connector structured response missing')
        value = value.get('content')
        r.require(isinstance(value, str), 'connector JSON content missing')
        value = v.strict_json(value)
    r.require(isinstance(value, dict), 'connector object missing')
    return value


def blob_response(value, oid):
    """Connector fetch decodes text blobs; accept exact UTF-8 only on SHA match."""
    r.require(isinstance(value,dict) and not value.get('isError'),'connector blob read failed')
    if isinstance(value.get('structuredContent'),dict):
        content=value['structuredContent'].get('content')
        r.require(isinstance(content,str),'connector blob bytes missing')
        raw=content.encode('utf-8')
        if r.blob_sha(raw)==oid:
            return dict(sha=oid,encoding='base64',size=len(raw),content=base64.b64encode(raw).decode())
    return unwrap(value)


def object_sha(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def parse_commit(raw, oid):
    r.require(object_sha('commit', raw) == oid, 'raw commit hash mismatch: ' + oid)
    headers, sep, _ = raw.partition(b'\n\n')
    r.require(sep and headers.startswith(b'tree '), 'invalid commit headers')
    lines = headers.split(b'\n')
    trees = [line[5:].decode('ascii') for line in lines if line.startswith(b'tree ')]
    parents = [line[7:].decode('ascii') for line in lines if line.startswith(b'parent ')]
    r.require(len(trees) == 1, 'ambiguous commit tree')
    r.sha(trees[0])
    for parent in parents: r.sha(parent)
    r.require(len(set(parents)) == len(parents), 'duplicate commit parent')
    return {'tree': trees[0], 'parents': parents}


def raw_commit(value):
    """Recover exact bytes, accepting ONLY a candidate matching Git's object ID.

    GitHub normalizes dates and sometimes message newlines. Enumerating the
    original offset/newline is safe only because the complete raw SHA must match.
    Signed commits use GitHub's payload + signature. Unknown headers fail closed.
    """
    value = unwrap(value)
    if isinstance(value.get('commit'), dict):
        # An unchanged REST commit-list entry; parent traversal, not list pages,
        # proves closure. Never trust a page's count as evidence of completeness.
        value = {**value['commit'], 'sha': value['sha'], 'parents': value['parents']}
    oid = value['sha']; r.sha(oid)
    if isinstance(value.get('raw_base64'), str):
        raw = base64.b64decode(value['raw_base64'], validate=True)
        info = parse_commit(raw, oid)
        return raw, info
    tree = value['tree']['sha']; parents = [x['sha'] for x in value['parents']]
    r.sha(tree)
    for parent in parents: r.sha(parent)
    prefix = 'tree ' + tree + '\n' + ''.join('parent ' + x + '\n' for x in parents)
    verification = value.get('verification') or {}
    payload = verification.get('payload'); signature = verification.get('signature')
    candidates = []
    if isinstance(payload, str):
        candidates.append(payload.encode())
        if isinstance(signature, str):
            h, sep, body = payload.partition('\n\n')
            r.require(sep, 'invalid signed payload')
            # gpgsig is a multiline header; preserve signature's trailing newline.
            sig = 'gpgsig ' + signature.replace('\n', '\n ').rstrip(' ')
            if sig.endswith('\n'): sig = sig[:-1]
            candidates.append((h + '\n' + sig + '\n\n' + body).encode())
    for raw in candidates:
        if object_sha('commit', raw) == oid:
            info = parse_commit(raw, oid)
            r.require(info == {'tree': tree, 'parents': parents}, 'commit metadata differs from raw')
            return raw, info
    r.require(not signature, 'signed commit raw reconstruction failed: ' + oid)
    def person(key, zone):
        item = value[key]
        r.require(all(isinstance(item.get(k), str) and '\n' not in item[k] for k in ('name','email','date')), 'invalid commit identity')
        timestamp = int(dt.datetime.fromisoformat(item['date'].replace('Z', '+00:00')).timestamp())
        return f"{key} {item['name']} <{item['email']}> {timestamp} {zone}\n"
    zones = ['+0000', '+0800'] + [f'{sign}{minute//60:02d}{minute%60:02d}'
             for sign in ('+', '-') for minute in range(0, 14*60+1)]
    zones = list(dict.fromkeys(zones))
    message = value['message']; r.require(isinstance(message,str), 'commit message missing')
    messages = list(dict.fromkeys([message, message + '\n', message.rstrip('\n'), message.rstrip('\n') + '\n']))
    # Common equal-zone case first. Unusual differing offsets remain supported.
    def try_zones(pairs):
        for a, c in pairs:
            head = prefix + person('author', a) + person('committer', c) + '\n'
            for msg in messages:
                raw = (head + msg).encode()
                if object_sha('commit', raw) == oid: return raw
    raw = try_zones((z,z) for z in zones)
    if raw is None: raw = try_zones(itertools.product(zones, zones))
    r.require(raw is not None, 'cannot reconstruct exact raw commit: ' + oid)
    return raw, parse_commit(raw, oid)


def selected(repo, path):
    if path.startswith('.recommendation/transactions/music/') and path.endswith('.json'): return True
    if repo == 'vault':
        return (path.startswith('Music/Daily/manifests/') and path.endswith('.json') or
                re.fullmatch(r'Music/Daily/\d{4}-\d{2}-\d{2}\.md', path) is not None)
    return path.startswith('recommendations/') and path.endswith('.json')


def current_needed(repo, path):
    # Enumerate/hash complete trees, but do not request bytes for attachments
    # unused by the Music validators. Binary art must not become a Git blocker.
    return (selected(repo,path) or path in CURRENT_FILES[repo] or
            path == ('Music/Daily/state/tracks.json' if repo=='vault' else 'state/tracks.json'))


class Repository:
    def __init__(self, key, head, cache, fetch):
        self.key=key; self.repo=REPOS[key]; self.head=head; r.sha(head)
        self.cache=Path(cache)/self.repo.split('/')[1]; self.fetch=fetch
        self.commits={}; self.trees={}; self.blobs={}; self.versions={}; self.current={}

    def object(self, kind, oid):
        r.sha(oid); path=self.cache/kind/(oid+'.json')
        if path.exists():
            response=v.strict_json(path.read_text())
            data=blob_response(response,oid) if kind=='blobs' else unwrap(response)
            r.require(data.get('sha') == oid, 'cached object SHA differs from requested object')
            return data
        r.require(callable(self.fetch), 'missing connector object: '+str(path))
        response=self.fetch(f'https://api.github.com/repos/{self.repo}/git/{kind}/{oid}')
        data=blob_response(response,oid) if kind=='blobs' else unwrap(response)
        r.require(data.get('sha') == oid, 'connector returned wrong object')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x') as out: json.dump(response,out,ensure_ascii=False)
        return data

    def commit(self, oid):
        if oid not in self.commits:
            data=self.object('commits',oid)
            raw_path=self.cache/'commit-raw'/oid
            if raw_path.exists():
                raw=raw_path.read_bytes();info=parse_commit(raw,oid)
            else:
                raw,info=raw_commit(data)
                r.require(object_sha('commit',raw)==oid,'raw commit differs from requested object')
                raw_path.parent.mkdir(parents=True,exist_ok=True)
                with raw_path.open('xb') as out:out.write(raw)
            self.commits[oid]=info
        return self.commits[oid]

    def entries(self, oid):
        if oid not in self.trees:
            data=self.object('trees',oid)
            r.require(data.get('sha') == oid and data.get('truncated') is False, 'missing or truncated tree: '+oid)
            r.require(mirror.tree_sha(data.get('tree')) == oid, 'tree hash mismatch: '+oid)
            self.trees[oid]=data
        return {row['path']:row for row in self.trees[oid]['tree']}

    def blob(self, oid):
        if oid not in self.blobs:
            data=self.object('blobs',oid)
            r.require(data.get('sha') == oid and data.get('encoding') == 'base64', 'exact base64 blob required')
            raw=base64.b64decode(''.join(data['content'].split()),validate=True)
            r.require(data.get('size') == len(raw) and r.blob_sha(raw) == oid, 'blob hash/size mismatch: '+oid)
            self.blobs[oid]=raw
        return self.blobs[oid]

    def lookup(self, commit, path):
        oid=self.commit(commit)['tree']; parts=path.split('/')
        for i, part in enumerate(parts):
            row=self.entries(oid).get(part)
            if row is None:return None
            if i == len(parts)-1:return row
            r.require(row['type']=='tree','non-directory in evidence path: '+path);oid=row['sha']

    def files(self, commit, directory):
        row=self.lookup(commit,directory)
        if row is None:return {}
        r.require(row['type']=='tree','non-directory in evidence path: '+directory)
        result={};todo=[(row['sha'], directory)]
        while todo:
            oid,prefix=todo.pop()
            for item in self.entries(oid).values():
                path=prefix+'/'+item['path']
                if item['type']=='tree':todo.append((item['sha'],path))
                else:
                    r.require(item['type']=='blob' and item['mode'] in ('100644','100755'),'non-regular publication evidence: '+path)
                    result[path]=item['sha']
        return result

    def collect(self):
        todo=[self.head];visited=set()
        while todo:
            oid=todo.pop()
            if oid in visited:continue
            visited.add(oid)
            info=self.commit(oid);todo.extend(info['parents'])
        # Every reachable commit has exact raw bytes and every parent is present.
        for commit in tuple(self.commits):
            for directory in HISTORY_DIRS[self.key]:
                for path,oid in self.files(commit,directory).items():
                    if selected(self.key,path):
                        self.blob(oid);self.versions.setdefault((path,oid),[]).append(commit)
        for directory in CURRENT_DIRS[self.key]:
            self.current.update({path:oid for path,oid in self.files(self.head,directory).items()
                                 if current_needed(self.key,path)})
        for path in CURRENT_FILES[self.key]:
            row=self.lookup(self.head,path)
            if row is not None:
                r.require(row['type']=='blob' and row['mode'] in ('100644','100755'),'non-regular current evidence')
                self.current[path]=row['sha']
        for oid in self.current.values():self.blob(oid)
        return self

    def snapshot(self):
        # The current mirror proof needs only current scoped trees, not a copy
        # of every ancestor tree in each preflight output. History stays cached.
        root=self.commits[self.head]['tree'];used={root}
        for path in CURRENT_DIRS[self.key]+CURRENT_FILES[self.key]:
            oid=root;row=None
            for part in path.split('/'):
                used.add(oid);row=self.entries(oid).get(part)
                if row is None:break
                if row['type']=='tree':oid=row['sha']
            if row is not None and row['type']=='tree':
                todo=[row['sha']]
                while todo:
                    at=todo.pop()
                    if at in used:continue
                    used.add(at)
                    todo.extend(item['sha'] for item in self.entries(at).values() if item['type']=='tree')
        return {'head_before':self.head,'head_after':self.head,
                'commit':{'sha':self.head,'tree':{'sha':root}},'trees':{oid:self.trees[oid] for oid in used}}


class History:
    def __init__(self, repos, roots):
        self.repos=repos;self.roots={k:Path(p).resolve() for k,p in roots.items()};self.head=repos['vault'].head
    def validate_root(self, root):
        r.require(Path(root).resolve()==self.roots['vault'],'wrong history root')
        for key,repo in self.repos.items():
            root=self.roots[key]
            r.require(not root.is_symlink() and not any(p.is_symlink() for p in root.rglob('*')),'materialized evidence contains symlink')
            actual={p.relative_to(root).as_posix():r.blob_sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
            r.require(actual==repo.current,'materialized evidence changed or omitted')
    def sources(self):
        return {(key+':'+path,oid):repo.blob(oid) for key,repo in self.repos.items() for path,oid in repo.versions}
    def identity_path(self,path):
        key,path=path.split(':',1)
        if key=='music' and path.startswith('recommendations/'):
            match=re.fullmatch(r'recommendations/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})\.json',path)
            r.require(match is not None and match[1]==match[3][:4] and match[2]==match[3][5:7],'noncanonical historical manifest path')
            return 'Music/Daily/manifests/'+match[3]+'.json'
        return path
    def commits_for(self,path,oid):
        key,path=path.split(':',1)
        return [key+':'+commit for commit in self.repos[key].versions.get((path,oid),[])]
    def is_ancestor(self,old,new):
        key,old=old.split(':',1);other,new=new.split(':',1)
        if key!=other:return False
        todo=[new];seen=set()
        while todo:
            at=todo.pop()
            if at==old:return True
            if at in seen:continue
            seen.add(at);todo.extend(self.repos[key].commits[at]['parents'])
        return False


def read_heads(fetch):
    r.require(callable(fetch),'live GitHub connector callback is required')
    result={}
    for key,repo in REPOS.items():
        data=unwrap(fetch(f'https://api.github.com/repos/{repo}/git/ref/heads/main'))
        r.require(data.get('ref')=='refs/heads/main' and data.get('object',{}).get('type')=='commit','unexpected live ref response')
        result[key]=data['object']['sha'];r.sha(result[key])
    return result


def materialize(repos, directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    roots={}
    for key,repo in repos.items():
        root=directory/key;root.mkdir();roots[key]=root
        for path,oid in repo.current.items():
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as out:out.write(repo.blob(oid))
    return History(repos,roots)
