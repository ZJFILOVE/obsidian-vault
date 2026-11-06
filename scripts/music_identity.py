"""Permanent Apple Music identities and evidence-bound pre-publication gate.

Read-only. Git history is required; a shallow checkout is not complete evidence.
Content/source QA and transport success are deliberately separate from this gate.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse
import publication_recovery as r
import validate_daily_recommendations as v

MANIFESTS = 'Music/Daily/manifests'
PREPARED = '.recommendation/transactions/music'
STATE = 'Music/Daily/state/tracks.json'
INCIDENT = '.recommendation/incidents/music-2026-11-06-714861225.json'
# Deliberately pinned: changing evidence or scope requires a reviewed code change.
INCIDENT_SHA256 = '68419b05b1707cb7017d8e0bd92df58922637a21183aaff116a9db18db0b4ab6'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def identity(track, *, historical=False):
    am = track['apple_music']; sid = am.get('song_id')
    if historical and sid is None:
        return None
    r.require(isinstance(sid, str) and re.fullmatch(r'[0-9]+', sid), 'invalid Apple song ID')
    url = urlparse(am.get('url', ''))
    match = re.fullmatch(r'/([a-z]{2})/song/(?:[^/]+/)?([0-9]+)', url.path)
    r.require(url.scheme == 'https' and url.netloc == 'music.apple.com' and match and
              match[2] == sid and not url.query and not url.fragment, 'invalid Apple song URL')
    storefront = am.get('storefront', match[1] if historical else None)
    r.require(storefront == match[1] and (historical or storefront == 'cn'), 'wrong storefront')
    return 'apple_music:' + storefront + ':' + sid


def incident(root: Path):
    path = root / INCIDENT
    if not path.exists():
        # Production repositories must not silently remove the registered accident.
        r.require(not (root / f'{MANIFESTS}/2026-11-06.json').exists(), 'incident registration missing')
        return None
    raw = path.read_bytes()
    r.require(hashlib.sha256(raw).hexdigest() == INCIDENT_SHA256, 'incident scope/evidence changed')
    doc = v.strict_json(raw.decode())
    for row in doc['occurrences']:
        raw = (root / row['path']).read_bytes()
        r.require(r.blob_sha(raw) == row['manifest_blob_sha'], 'incident manifest changed')
        manifest = v.strict_json(raw.decode()); track = manifest['tracks'][row['position'] - 1]
        r.require(manifest['date'] == row['date'] and track['position'] == row['position'] and
                  track['canonical_id'] == row['canonical_id'] and identity(track) == doc['identity'],
                  'incident occurrence changed')
    for key in ('failure_evidence', 'prepared'):
        evidence = doc[key]; raw = (root / evidence['path']).read_bytes()
        r.require(r.blob_sha(raw) == evidence['blob_sha'], 'incident evidence changed')
    from publication_bundle import verify
    bundle = v.strict_json((root / doc['prepared']['path']).read_text()); verify(bundle)
    r.require(bundle['bundle_sha256'] == doc['prepared']['bundle_sha256'], 'incident bundle digest changed')
    failure = v.strict_json((root / doc['failure_evidence']['path']).read_text())
    r.require(failure['status'] == 'blocked_current_publication' and failure['qa_run_written'] is False,
              'incident failure was relabelled')
    r.require(not (root / '.recommendation/runs/2026-11-06-music.json').exists(),
              'failed incident date cannot receive success QA')
    return doc


def exact_incident_pair(doc, first, second):
    if doc is None: return False
    expected = [(x['date'], x['position'], x['canonical_id']) for x in doc['occurrences']]
    return [first, second] == expected


def index(root: Path):
    """Union current, all HEAD-ancestor blobs, and all PREPARED payloads.

    Historical missing IDs remain unresolved; later records with the same name
    are useful evidence, but cannot prove which recording a search link exposed.
    """
    r.require(git(root, 'rev-parse', '--is-shallow-repository').strip() == b'false', 'full Git history required')
    r.require(not git(root, 'replace', '-l').strip(), 'Git replace refs are not history evidence')
    sources = {}
    for directory in (MANIFESTS, PREPARED):
        for path in sorted((root / directory).glob('*.json')):
            raw = path.read_bytes(); sources[(path.relative_to(root).as_posix(), r.blob_sha(raw))] = raw
    for path in sorted((root / 'Music/Daily').glob('????-??-??.md')):
        raw = path.read_bytes(); sources[(path.relative_to(root).as_posix(), r.blob_sha(raw))] = raw
    rows = git(root, 'rev-list', '--objects', 'HEAD', '--', 'Music/Daily', PREPARED).decode().splitlines()
    for line in rows:
        oid, _, path = line.partition(' ')
        if ((path.startswith(MANIFESTS + '/') or path.startswith(PREPARED + '/')) and path.endswith('.json')) or re.fullmatch(r'Music/Daily/\d{4}-\d{2}-\d{2}\.md', path):
            sources.setdefault((path, oid), git(root, 'cat-file', 'blob', oid))
    records = []; bundles = {}; missing = []
    for (path, oid), raw in sorted(sources.items()):
        if path.endswith('.md'):
            day = v.iso_day(Path(path).stem)
            sections = re.split(r'^## (\d+)\. ([^\n]+)\n', raw.decode(), flags=re.M)
            for offset in range(1, len(sections), 3):
                position, heading, body = sections[offset:offset + 3]
                cid = heading.replace(' — ', '::', 1) if ' — ' in heading else ''
                for sid in set(v.MUSIC_SONG_RE.findall(body)):
                    records.append(dict(operation_id='music:' + day, date=day, position=int(position),
                        canonical_id=cid, identity='apple_music:cn:' + sid, source_path=path, source_blob_sha=oid))
            # Even links outside recognized sections are exposures. Do not guess a title.
            covered_ids = {x['identity'].rsplit(':', 1)[-1] for x in records
                           if x['source_path'] == path and x['source_blob_sha'] == oid}
            for sid in set(v.MUSIC_SONG_RE.findall(raw.decode())) - covered_ids:
                records.append(dict(operation_id='music:' + day, date=day, position=0, canonical_id='',
                    identity='apple_music:cn:' + sid, source_path=path, source_blob_sha=oid))
            continue
        doc = v.strict_json(raw.decode())
        if path.startswith(PREPARED + '/'):
            from publication_bundle import verify
            verify(doc); day = doc['plan']['date']
            r.require(path == f'{PREPARED}/{day}.json', 'PREPARED operation/path mismatch')
            r.require(day not in bundles or bundles[day] == doc['bundle_sha256'], 'PREPARED rewritten in history')
            bundles[day] = doc['bundle_sha256']
            doc = v.strict_json(doc['payloads'][f'ZJFILOVE/obsidian-vault:{MANIFESTS}/{day}.json'])
        day = v.iso_day(doc['date'])
        r.require(doc.get('provider') == 'apple_music', 'wrong historical provider')
        for track in doc['tracks']:
            cid = track['canonical_id']; key = identity(track, historical=True)
            row = dict(operation_id='music:' + day, date=day, position=track['position'],
                       canonical_id=cid, identity=key, source_path=path, source_blob_sha=oid)
            records.append(row)
            if key is None: missing.append(row)
    resolved = {(x['operation_id'], x['position'], x['canonical_id']) for x in records if x['identity']}
    unresolved = missing
    later_evidence = [x for x in missing if (x['operation_id'], x['position'], x['canonical_id']) in resolved]
    state = v.strict_json((root / STATE).read_text())['recommended']
    covered = {x['canonical_id'] for x in records}
    unmapped = sorted(set(state) - covered)
    # Multiple snapshots of one occurrence are provenance, not new exposures.
    grouped = {}
    for row in records:
        key = (row['operation_id'], row['position'], row['canonical_id'], row['identity'])
        item = grouped.setdefault(key, {k: row[k] for k in
            ('operation_id', 'date', 'position', 'canonical_id', 'identity')})
        item.setdefault('sources', []).append({'path': row['source_path'], 'blob_sha': row['source_blob_sha']})
    records = sorted(grouped.values(), key=lambda x: (x['date'], x['position'], x['canonical_id'], x['identity'] or ''))
    digest = r.digest(records)
    return dict(schema_version=1, status='incomplete_identity_evidence' if unresolved or unmapped else 'complete_available_git_history', unmapped_state_keys=unmapped, head=git(root,'rev-parse','HEAD').decode().strip(),
                index_sha256=digest, records=records, prepared=bundles,
                legacy_missing_id_rows=missing, unresolved_identities=unresolved, later_identity_candidates=later_evidence,
                scope='current files and all available HEAD ancestors; not proof of unavailable external history')


def check_selection(root: Path, manifest: dict, *, bundle_digest=None):
    """Same-operation reservation permitted only for exact frozen manifest bytes upstream."""
    history = index(root); day = v.iso_day(manifest['date']); operation = 'music:' + day
    registered = incident(root)
    r.require(not registered or day != registered['failed_date'], 'historical incident date remains content_qa=failed')
    if day in history['prepared']:
        r.require(bundle_digest == history['prepared'][day], 'same-operation recovery requires original bundle digest')
        saved = v.strict_json((root / f'{PREPARED}/{day}.json').read_text())
        frozen = v.strict_json(saved['payloads'][f'ZJFILOVE/obsidian-vault:{MANIFESTS}/{day}.json'])
        r.require(manifest == frozen, 'same-operation selection changed')
    else:
        r.require(not any(x['operation_id'] == operation for x in history['records']),
                  'existing exposure requires immutable adoption/recovery review')
    seen_ids = set(); seen_cids = set()
    for track in manifest['tracks']:
        key = identity(track); cid = track['canonical_id']
        r.require(key not in seen_ids and cid not in seen_cids, 'duplicate within candidate selection')
        seen_ids.add(key); seen_cids.add(cid)
        collisions = [x for x in history['records'] if x['operation_id'] != operation and
                      (x['identity'] == key or x['canonical_id'] == cid)]
        r.require(not collisions, 'permanent recording reuse: ' + key)
    r.require(history['status'] == 'complete_available_git_history',
              'incomplete permanent identity evidence: ' + repr(history['unmapped_state_keys']) +
              '; unresolved historical rows=' + str(len(history['unresolved_identities'])))
    return {'status': 'passed_recording_identity', 'operation_id': operation,
            'identity_index_sha256': history['index_sha256'], 'history_head': history['head'],
            'identities': [identity(t) for t in manifest['tracks']],
            'historical_failed_dates': [registered['failed_date']] if registered else [],
            'content_qa': 'not_evaluated', 'transport': 'not_evaluated'}


def publication_gate(root: Path, plan: dict, payloads: dict, snapshot: dict, expected_heads: dict, *, bundle_digest=None):
    from check_remote_music_snapshot import audit
    from publication_bundle import validate_payloads, verify
    validate_payloads(plan, payloads)
    if bundle_digest is not None:
        saved = v.strict_json((root / PREPARED / (plan['date'] + '.json')).read_text())
        verify(saved)
        r.require(saved['bundle_sha256'] == bundle_digest and saved['plan'] == plan and
                  saved['payloads'] == payloads, 'recovery must use the exact original frozen plan/payloads')
    mirror = audit(snapshot)
    r.require(set(expected_heads) == {'music', 'vault'} and mirror['heads'] == expected_heads,
              'snapshot is not pinned to requested repository versions')
    r.require(git(root, 'rev-parse', 'HEAD').decode().strip() == expected_heads['vault'], 'local history head differs')
    local = {p.name: r.blob_sha(p.read_bytes()) for p in (root / MANIFESTS).glob('*.json')}
    r.require(local == mirror['manifest_blobs'] and r.blob_sha((root / STATE).read_bytes()) == mirror['state_blob_sha'],
              'local manifest/state differs from mirror evidence')
    # Bind each mutable target baseline to the independently verified snapshot.
    for target in plan['targets']:
        path = target['path']
        if path.endswith('state/tracks.json'): expected = mirror['state_blob_sha']
        elif path.endswith('.json'): expected = mirror['manifest_blobs'].get(plan['date'] + '.json')
        else: continue
        r.require(target['base_sha'] == expected or (bundle_digest and target['target_sha'] == expected),
                  'plan baseline is not the verified mirror version')
    before = v.strict_json((root / STATE).read_text())['recommended']
    after = v.strict_json(payloads['ZJFILOVE/obsidian-vault:' + STATE])['recommended']
    r.require(all(key in after and after[key] == value for key, value in before.items()),
              'candidate changed permanent state values')
    day = plan['date']; key = f'ZJFILOVE/obsidian-vault:{MANIFESTS}/{day}.json'
    selection = check_selection(root, v.strict_json(payloads[key]), bundle_digest=bundle_digest)
    return {**selection, 'schema_version': 1, 'status': 'passed_music_publication_gate',
            'mirror_status': mirror['status'], 'heads': mirror['heads'],
            'manifest_blobs': mirror['manifest_blobs'], 'state_blob_sha': mirror['state_blob_sha'],
            'plan_sha256': r.digest(plan), 'payloads_sha256': r.digest(payloads),
            'content_qa': 'not_evaluated', 'transport': 'not_evaluated'}
