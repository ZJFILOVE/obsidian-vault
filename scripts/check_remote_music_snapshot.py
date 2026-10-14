#!/usr/bin/env python3
"""Compare authorized Git tree evidence. No credentials, network calls or repository writes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from publication_recovery import require, sha
from validate_daily_recommendations import iso_day, strict_json


def tree_sha(entries: list[dict]) -> str:
    require(isinstance(entries, list), 'tree entries missing')
    names = set(); chunks = []
    for row in entries:
        require(isinstance(row, dict), 'invalid tree entry')
        name = row.get('path'); mode = row.get('mode'); kind = row.get('type')
        require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name and '\0' not in name, 'need complete non-recursive tree entries')
        require(name not in names, 'duplicate tree entry'); names.add(name)
        require((mode, kind) in (('040000', 'tree'), ('100644', 'blob'), ('100755', 'blob'), ('120000', 'blob'), ('160000', 'commit')), 'invalid mode/type')
        sha(row.get('sha'))
        sortkey = (name + ('/' if kind == 'tree' else '')).encode('utf-8')
        chunk = mode.lstrip('0').encode() + b' ' + name.encode('utf-8') + b'\0' + bytes.fromhex(row['sha'])
        chunks.append((sortkey, chunk))
    raw = b''.join(x[1] for x in sorted(chunks))
    return hashlib.sha1(b'tree ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class Snapshot:
    def __init__(self, data: dict):
        require(isinstance(data, dict), 'repository snapshot missing')
        self.data = data; sha(data.get('head_before')); sha(data.get('head_after'))
        require(data['head_before'] == data['head_after'], 'head moved during scan; recollect, do not report consistent')
        self.root = data['commit']['tree']['sha']; sha(self.root)
        require(data['commit']['sha'] == data['head_before'], 'commit is not pinned to observed branch')
        require(isinstance(data.get('trees'), dict), 'tree evidence missing')

    def entries(self, oid: str) -> dict[str, dict]:
        node = self.data['trees'].get(oid)
        require(isinstance(node, dict) and node.get('truncated') is False, 'missing or truncated tree ' + oid)
        require(node.get('sha') == oid and tree_sha(node.get('tree')) == oid, 'tree hash mismatch: incomplete or altered response')
        return {r['path']: r for r in node['tree']}

    def get(self, path: str) -> dict:
        oid = self.root
        parts = path.split('/')
        for i, part in enumerate(parts):
            row = self.entries(oid).get(part)
            require(row is not None, 'missing path: ' + path)
            if i == len(parts) - 1: return row
            require(row['type'] == 'tree', 'not a directory: ' + path)
            oid = row['sha']
        raise ValueError('empty path')

    def blobs(self, path: str) -> dict[str, str]:
        parent = self.get(path); require(parent['type'] == 'tree', 'not a directory: ' + path)
        found = {}
        def visit(oid: str, prefix: str, ancestors: set[str]) -> None:
            require(oid not in ancestors, 'cyclic tree evidence')
            for row in self.entries(oid).values():
                key = prefix + row['path']
                if row['type'] == 'tree': visit(row['sha'], key + '/', ancestors | {oid})
                else:
                    require(row['type'] == 'blob' and row['mode'] in ('100644', '100755'), 'symlink/submodule in content directory')
                    found[key] = row['sha']
        visit(parent['sha'], '', set()); return found

    def file_sha(self, path: str) -> str:
        row = self.get(path)
        require(row['type'] == 'blob' and row['mode'] == '100644', 'expected regular data file: ' + path)
        return row['sha']


def audit(data: dict) -> dict:
    require(isinstance(data, dict) and data.get('schema_version') == 1, 'invalid evidence version')
    music, vault = Snapshot(data['music']), Snapshot(data['vault'])
    raw = music.blobs('recommendations'); manifests = {}
    for path, oid in raw.items():
        if not path.endswith('.json'): continue
        match = re.fullmatch(r'(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})\.json', path)
        require(match is not None, 'noncanonical manifest path: ' + path)
        day = iso_day(match[3]); require(match[1] == day[:4] and match[2] == day[5:7], 'manifest path/date mismatch')
        require(day not in manifests, 'duplicate date'); manifests[day + '.json'] = oid
    require(bool(manifests), 'empty source manifest set')
    mirror = {p: oid for p, oid in vault.blobs('Music/Daily/manifests').items() if p.endswith('.json')}
    require(manifests == mirror, 'manifest missing, orphaned or different across repositories')
    for name in manifests: vault.file_sha('Music/Daily/' + name.removesuffix('.json') + '.md')
    state = music.file_sha('state/tracks.json')
    require(state == vault.file_sha('Music/Daily/state/tracks.json'), 'state differs across repositories')
    return {'status': 'passed_current_music_mirrors', 'manifests': len(manifests), 'manifest_blobs': manifests,
            'state_blob_sha': state, 'heads': {'music': data['music']['head_after'], 'vault': data['vault']['head_after']},
            'checked': ['all manifest names and blob hashes', 'state blob hash', 'corresponding music notes exist', 'tree evidence completeness', 'stable branch observations'],
            'not_certified': ['state semantic coverage (run local CI)', 'live sources', 'editorial quality', 'device synchronization', 'notification delivery']}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('snapshot', type=Path); args = p.parse_args()
    try: result = audit(strict_json(args.snapshot.read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError, OSError, RecursionError) as exc:
        print(json.dumps({'status': 'failed_or_unverified', 'error': str(exc)})); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0

if __name__ == '__main__': raise SystemExit(main())
