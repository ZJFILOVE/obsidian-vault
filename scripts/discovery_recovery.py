"""Narrow recovery of one truncated PREPARED; no publication/network writes.

The recovered bundle is NEW evidence, never claimed to be the missing original.
The malformed original and original failure remain immutable audit artifacts.
"""
from __future__ import annotations
import argparse
import copy
import json
import hashlib
from pathlib import Path
import subprocess
import publication_recovery as r
import validate_daily_recommendations as v

OP = 'news-youtube-reddit:2026-11-08'
DAY = '2026-11-08'
TRANSACTION = '.recommendation/transactions/news-youtube-reddit/2026-11-08.json'
DIRECTORY = '.recommendation/transaction-recoveries/news-youtube-reddit/2026-11-08'
ARCHIVE = DIRECTORY + '/original-truncated.txt'
RECEIPT = DIRECTORY + '/recovery.json'
EVIDENCE = DIRECTORY + '/source-evidence.json'
ORIGINAL_PLAN_FILE = DIRECTORY + '/original-plan.json'
ORIGINAL_NOTES = {kind: DIRECTORY + '/original-' + kind + '.md' for kind in ('news', 'youtube', 'reddit')}
ORIGINAL_REDDIT = DIRECTORY + '/original-reddit-append.jsonl'
RECOVERY_ID = 'news-youtube-reddit-2026-11-08-truncation'
OLD_YOUTUBE = ['hB9JIjzIwrU', '8IJdwTRSTFQ', 'MPDwVSODXP0', '2_rO0YNIwPA', 'M9Xx--JRXmM']
NEW_YOUTUBE = ['hB9JIjzIwrU', '8IJdwTRSTFQ', 'k20doHDjMwo', '2_rO0YNIwPA', 'LI53uFBXj4I']
REDDIT = ['1l8p440', '1plriuo', '12bogty', '1uo7rf2', '1u03p4m', '1sb02pb', '1r73l52', '1rkhp2m', '1tcwlsg', '1u24s8i']
OLD_IDS = ['youtube:' + x for x in OLD_YOUTUBE] + ['reddit:' + x for x in REDDIT]
ACTIVE_IDS = ['youtube:' + x for x in NEW_YOUTUBE] + ['reddit:' + x for x in REDDIT]
RESERVED_IDS = OLD_IDS + ['youtube:k20doHDjMwo', 'youtube:LI53uFBXj4I']
FAILURE = '.recommendation/transaction-runs/news-youtube-reddit/2026-11-08/20261108T003948Z.json'
BAD_BLOB = '18ec095cf56f73aef6c11aa4713067b93635d425'
FAILURE_BLOB = '5e88073bad267dcf5d40dd4eade0436640dbf23a'
ORIGINAL_EXPECTED_BLOB = '841ee2c8543432981e83723a6941c372fcf753d7'
ORIGINAL_PLAN = 'a830123a64fa2d8da659e6e87312e29c60b63208f297bb7286a864839f160457'
ORIGINAL_BUNDLE = '9fd0e0a48830b1f53cb3bc458400d1eb1221412c251140aec18f9931fe1ccfdd'
PREFIX = b'Warning: truncated output (original token count: 51584)\nTotal output lines: 72\n\n'
VAULT = 'ZJFILOVE/obsidian-vault:'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def known_original(raw: bytes):
    r.require(r.blob_sha(raw) == BAD_BLOB and raw.startswith(PREFIX), 'not the exact registered truncated transaction')
    # Parsing exposes intact fragments, NOT a claim that this is a valid bundle.
    doc = v.strict_json(raw[len(PREFIX):].decode())
    r.require(doc['plan_sha256'] == ORIGINAL_PLAN and r.digest(doc['plan']) == ORIGINAL_PLAN,
              'registered original plan changed')
    r.require(doc['bundle_sha256'] == ORIGINAL_BUNDLE and doc['plan']['operation_id'] == OP,
              'registered original operation/digest changed')
    r.validate(doc['plan'])
    r.require(doc['plan']['exposed_resource_ids'] == OLD_IDS, 'original reservations changed')
    for target in doc['plan']['targets']:
        if target['path'].endswith('.md'):
            text = doc['payloads'][target['repository'] + ':' + target['path']]
            r.require(r.blob_sha(text.encode()) == target['target_sha'], 'intact original note hash mismatch')
    return doc


def failure(root):
    raw = (root / FAILURE).read_bytes()
    r.require(r.blob_sha(raw) == FAILURE_BLOB, 'original failure evidence changed')
    doc = v.strict_json(raw.decode())
    r.require(doc['operation_id'] == OP and doc['status'] == 'blocked_before_publication', 'wrong original failure')
    return doc


def baseline(root, target):
    r.require(target['path'].endswith('.jsonl'), 'only history bases can be reconstructed')
    raw = git(root, 'cat-file', 'blob', target['base_sha'])
    r.require(r.blob_sha(raw) == target['base_sha'] and raw.endswith(b'\n'), 'verified history baseline missing')
    return raw.decode()


def appended_rows(text, kind, ids):
    r.require(text.endswith('\n'), 'recovery history append must end at newline')
    rows = [v.strict_json(line) for line in text.splitlines()]
    key = 'video_id' if kind == 'youtube' else 'post_id'
    r.require(all(isinstance(row, dict) for row in rows), 'recovery history rows must be objects')
    r.require([row.get(key) for row in rows] == ids, 'recovery changed reservation order/IDs')
    r.require(all(row.get('date') == DAY and row.get('operation_id') == OP and row.get('position') == i
                  for i, row in enumerate(rows, 1)), 'recovery changed operation/date/positions')
    return rows


def recovered_reddit(original):
    fragments = original['payloads'][VAULT + '.recommendation/history/youtube.jsonl']
    lines = []
    for line in fragments.splitlines():
        try: row = v.strict_json(line)
        except ValueError: continue
        if isinstance(row, dict) and row.get('date') == DAY:
            lines.append(line)
    text = '\n'.join(lines) + '\n'
    appended_rows(text, 'reddit', REDDIT)
    return text


def evidence(raw, plan, root):
    doc = v.strict_json(raw.decode())
    r.require(isinstance(doc, dict) and doc.get('operation_id') == OP,
              'recovery source evidence must name the exact operation')
    r.require(doc.get('youtube_ids') == NEW_YOUTUBE, 'source evidence reservation IDs differ')
    # The JSON is source evidence supplied by the authorized investigator, not
    # self-certifying QA. The receipt/CLI always report content_qa not_evaluated.
    r.require(bool(doc.get('source_checks')), 'recovery source observations missing')
    if 'input_zip_path' in doc or 'input_zip_sha256' in doc:
        path = '.recommendation/transaction-runs/news-youtube-reddit/2026-11-08/recovery-source-inputs.zip'
        expected = '70e13ebbacad2db5070fe113024d151e2b93872544d1ecc88c9447cbcd19f6b8'
        r.require(doc.get('input_zip_path') == path and doc.get('input_zip_sha256') == expected,
                  'recovery input archive binding changed')
        r.require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected,
                  'recovery input archive missing or changed')
    return doc


def validate_selection(plan, actual_ids):
    """Only this exact authorized supersession can reserve more than selected."""
    r.require(plan.get('recovery_id') == RECOVERY_ID and plan.get('operation_id') == OP and
              plan.get('project') == 'news-youtube-reddit' and plan.get('date') == DAY,
              'unsupported recovery operation')
    r.require(plan.get('original_plan_sha256') == ORIGINAL_PLAN and
              plan.get('original_bundle_sha256') == ORIGINAL_BUNDLE,
              'recovery lost original digest binding')
    r.require(plan.get('exposed_resource_ids') == RESERVED_IDS and
              plan.get('selected_resource_ids') == ACTIVE_IDS and actual_ids == ACTIVE_IDS,
              'recovery selection or permanent reservation union changed')


def original_artifacts(original):
    artifacts = {ORIGINAL_PLAN_FILE: (json.dumps(original['plan'], ensure_ascii=False, indent=2) + '\n').encode(),
                 ORIGINAL_REDDIT: recovered_reddit(original).encode()}
    for kind, path in ORIGINAL_NOTES.items():
        directory = {'news': 'News', 'youtube': 'Resources/YouTube', 'reddit': 'Resources/Reddit'}[kind]
        artifacts[path] = original['payloads'][VAULT + directory + '/Daily/' + DAY + '.md'].encode()
    return artifacts


def derive(root, raw, payloads, source_evidence):
    from publication_bundle import verify, targets_for
    original = known_original(raw); failure(root); evidence(source_evidence, original['plan'], root)
    r.require(set(payloads) == set(targets_for('news-youtube-reddit', DAY)), 'recovery payload set changed')
    r.require(all(isinstance(text, str) for text in payloads.values()), 'recovery payloads must be complete UTF-8 text')
    plan = copy.deepcopy(original['plan'])
    plan.update(recovery_id=RECOVERY_ID, original_plan_sha256=ORIGINAL_PLAN, original_bundle_sha256=ORIGINAL_BUNDLE,
                exposed_resource_ids=RESERVED_IDS, selected_resource_ids=ACTIVE_IDS)
    for target in plan['targets']:
        key = target['repository'] + ':' + target['path']
        if target['path'].endswith('.jsonl'):
            kind = Path(target['path']).stem; before = baseline(root, target)
            r.require(payloads[key].startswith(before), 'recovery changed permanent history prefix')
            rows = appended_rows(payloads[key][len(before):], kind, NEW_YOUTUBE if kind == 'youtube' else REDDIT)
            field = 'video_id' if kind == 'youtube' else 'post_id'
            prior = {v.strict_json(line)[field] for line in before.splitlines()}
            r.require(not prior.intersection(row[field] for row in rows), 'recovery repeats an earlier permanent history resource')
            if kind == 'reddit':
                r.require(r.blob_sha((before + recovered_reddit(original)).encode()) == target['target_sha'],
                          'original Reddit reconstruction does not match original target')
        target['target_sha'] = r.blob_sha(payloads[key].encode())
    body = {'schema_version': 1, 'plan': plan, 'payloads': payloads, 'plan_sha256': r.digest(plan)}
    bundle = {**body, 'bundle_sha256': r.digest(body)}
    verify(bundle)
    bundle_raw = (json.dumps(bundle, ensure_ascii=False, indent=2) + '\n').encode()
    receipt = {
        'schema_version': 1, 'recovery_id': RECOVERY_ID,
        'operation_id': OP, 'kind': 'authorized_superseding_recovery_not_original',
        'original_path': TRANSACTION, 'original_corrupt_blob_sha': BAD_BLOB,
        'archived_original_path': ARCHIVE, 'original_expected_blob_sha': ORIGINAL_EXPECTED_BLOB,
        'original_expected_plan_sha256': ORIGINAL_PLAN, 'original_expected_bundle_sha256': ORIGINAL_BUNDLE,
        'failure_path': FAILURE, 'failure_blob_sha': FAILURE_BLOB,
        'preserved_original_resource_ids': OLD_IDS, 'selected_resource_ids': ACTIVE_IDS,
        'permanent_reserved_resource_ids': RESERVED_IDS,
        'replacements': {'youtube:MPDwVSODXP0': 'youtube:k20doHDjMwo', 'youtube:M9Xx--JRXmM': 'youtube:LI53uFBXj4I'},
        'recovered_path': TRANSACTION, 'recovered_blob_sha': r.blob_sha(bundle_raw),
        'recovered_plan_sha256': bundle['plan_sha256'], 'recovered_bundle_sha256': bundle['bundle_sha256'],
        'source_evidence_path': EVIDENCE, 'source_evidence_blob_sha': r.blob_sha(source_evidence),
        'original_artifacts': {path: r.blob_sha(data) for path, data in original_artifacts(original).items()},
        'reconstruction': {'notes': 'new recovery-time reviewed content; originals preserved separately',
                           'reddit_history': 'original base plus recovery-time rows; original append retained separately',
                           'youtube_history': 'original base plus newly supplied five rechecked rows'},
        'original_publication_status': 'blocked_before_publication', 'content_qa': 'not_evaluated',
        'publication_target_writes_performed': 0,
    }
    return bundle, bundle_raw, receipt


def require_full_history(root):
    r.require(git(root, 'rev-parse', '--is-shallow-repository').strip() == b'false', 'full Git history required for recovery evidence')
    r.require(not git(root, 'replace', '-l').strip(), 'Git replace refs cannot certify recovery evidence')
    import os
    names = [git(root, 'rev-parse', '--git-path', 'info/grafts').decode().strip()]
    if os.environ.get('GIT_GRAFT_FILE'): names.append(os.environ['GIT_GRAFT_FILE'])
    for name in names:
        path = Path(name)
        if not path.is_absolute(): path = root / path
        r.require(not path.exists(), 'Git grafts cannot certify recovery evidence')


def historical_evidence(root, paths):
    """Every path/blob pair across HEAD ancestry, including deleted evidence."""
    found = {path: set() for path in paths}
    for commit in git(root, 'rev-list', 'HEAD').decode().splitlines():
        for row in filter(None, git(root, 'ls-tree', '-rz', commit, '--', *paths).split(b'\0')):
            meta, path = row.split(b'\t', 1); path = path.decode()
            if path in found:
                mode, kind, oid = meta.split()
                r.require(kind == b'blob' and mode == b'100644', 'non-regular recovery evidence')
                found[path].add(oid.decode())
    return found


def validate_installed(root: Path):
    """Verify this one complete transition, including its append-only evidence.

    No exception exists before all replacement artifacts are staged. Generic
    bundle verification stays strict; old malformed bytes never become a bundle.
    """
    require_full_history(root)
    r.require((root / RECEIPT).is_file(), 'registered recovery receipt missing; truncated transaction remains blocked')
    raw = (root / ARCHIVE).read_bytes(); original = known_original(raw)
    current_raw = (root / TRANSACTION).read_bytes()
    bundle = v.strict_json(current_raw.decode())
    from publication_bundle import verify
    verify(bundle)
    rebuilt, expected_raw, expected_receipt = derive(root, raw, bundle['payloads'], (root / EVIDENCE).read_bytes())
    r.require(bundle == rebuilt and current_raw == expected_raw, 'recovered plan/payloads differ from exact allowed reconstruction')
    receipt_raw = (root / RECEIPT).read_bytes()
    r.require(v.strict_json(receipt_raw.decode()) == expected_receipt, 'recovery receipt scope/evidence changed')
    artifacts = original_artifacts(original)
    for path, expected in artifacts.items():
        r.require((root / path).read_bytes() == expected, 'archived original fragment changed: ' + path)
    protected = [ARCHIVE, RECEIPT, EVIDENCE, TRANSACTION, *artifacts]
    versions = historical_evidence(root, protected)
    for path in protected:
        allowed = {r.blob_sha((root / path).read_bytes())}
        if path == TRANSACTION: allowed.add(BAD_BLOB)
        r.require(versions[path] <= allowed, 'committed recovery evidence changed or superseded: ' + path)
    reservations = reservation_gate(root, bundle)
    return {'status': 'verified_exact_truncation_recovery', 'operation_id': OP, 'reservation_gate': reservations,
            'original_status': 'invalid_truncated_PREPARED_preserved', 'original_blob_sha': BAD_BLOB,
            'recovered_blob_sha': r.blob_sha(current_raw), 'recovered_bundle_sha256': bundle['bundle_sha256'],
            'content_qa': 'not_evaluated', 'publication_target_writes_performed': 0}


def reservation_gate(root: Path, bundle: dict):
    """Exclude current AND retired reservations; a matching operation name is insufficient."""
    from publication_bundle import verify
    verify(bundle); require_full_history(root)
    plan = bundle['plan']; operation = plan['operation_id']
    r.require(plan['project'] == 'news-youtube-reddit', 'wrong reservation gate project')
    prefixes = ['.recommendation/transactions/news-youtube-reddit',
                '.recommendation/history/youtube.jsonl', '.recommendation/history/reddit.jsonl']
    versions = set()
    for commit in git(root, 'rev-list', 'HEAD').decode().splitlines():
        for row in filter(None, git(root, 'ls-tree', '-rz', commit, '--', *prefixes).split(b'\0')):
            meta, path = row.split(b'\t', 1); mode, kind, oid = meta.split()
            r.require(mode == b'100644' and kind == b'blob', 'non-regular discovery history')
            versions.add((path.decode(), oid.decode()))
    blobs = {}
    for prefix in prefixes:
        path = root / prefix
        for item in (path.rglob('*.json') if path.is_dir() else [path]):
            if item.is_file():
                raw = item.read_bytes(); oid = r.blob_sha(raw)
                versions.add((item.relative_to(root).as_posix(), oid)); blobs[oid] = raw
    seen = {}; prepared_count = 0
    for path, oid in sorted(versions):
        if oid not in blobs: blobs[oid] = git(root, 'cat-file', 'blob', oid)
        raw = blobs[oid]
        if path.endswith('.jsonl'):
            resource_kind = Path(path).stem
            field = 'video_id' if resource_kind == 'youtube' else 'post_id'
            for line in raw.decode().splitlines():
                if not line.strip(): continue
                row = v.strict_json(line)
                resource = resource_kind + ':' + row[field]
                owner = 'news-youtube-reddit:' + row['date']
                r.require(row.get('operation_id', owner) == owner, 'history operation/date mismatch')
                seen.setdefault(resource, set()).add(owner)
            continue
        prepared_count += 1
        if path == TRANSACTION and oid == BAD_BLOB:
            old = known_original(raw); failure(root)
        else:
            old = v.strict_json(raw.decode()); verify(old)
        oldplan = old['plan']
        r.require(path == '.recommendation/transactions/news-youtube-reddit/' + oldplan['date'] + '.json' and
                  oldplan['project'] == 'news-youtube-reddit', 'reservation path/operation mismatch')
        if oldplan['operation_id'] == operation:
            allowed_original = (path == TRANSACTION and oid == BAD_BLOB and
                                plan.get('recovery_id') == RECOVERY_ID)
            r.require(allowed_original or old['bundle_sha256'] == bundle['bundle_sha256'],
                      'same operation has a different frozen selection/payload')
        for resource in oldplan['exposed_resource_ids']:
            seen.setdefault(resource, set()).add(oldplan['operation_id'])
    conflicts = {resource: sorted(seen.get(resource, set()) - {operation})
                 for resource in plan['exposed_resource_ids']
                 if seen.get(resource, set()) - {operation}}
    r.require(not conflicts, 'resources reserved by another operation: ' + json.dumps(conflicts, sort_keys=True))
    return {'status': 'passed_permanent_discovery_reservations', 'scope': 'worktree_and_all_HEAD_ancestors',
            'prepared_path_blob_versions': prepared_count, 'historical_resource_count': len(seen),
            'reserved_resource_ids': plan['exposed_resource_ids'], 'content_qa': 'not_evaluated'}


def stage(root: Path, payloads: dict, source_evidence: bytes, destination: Path):
    """Create reviewable artifacts outside the repository; never publish notes."""
    require_full_history(root)
    r.require(destination.resolve() != root.resolve() and not destination.resolve().is_relative_to(root.resolve()),
              'stage recovery outside the source repository')
    r.require(not destination.exists(), 'staging destination already exists; do not overwrite')
    raw = (root / TRANSACTION).read_bytes()
    bundle, bundle_raw, receipt = derive(root, raw, payloads, source_evidence)
    # Fresh baselines: preparation must not silently overwrite changed histories
    # or existing notes. Later retries use the normal digest-bound planner.
    from publication_bundle import check_baselines
    baselines = {t['repository'] + ':' + t['path']:
                 (root / t['path']).read_text() if (root / t['path']).is_file() else None
                 for t in bundle['plan']['targets']}
    check_baselines(bundle, baselines)
    reservations = reservation_gate(root, bundle)
    artifacts = {TRANSACTION: bundle_raw, ARCHIVE: raw, EVIDENCE: source_evidence,
                 RECEIPT: (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode(),
                 **original_artifacts(known_original(raw))}
    for name, data in artifacts.items():
        path = destination / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    return {'status': 'staged_new_reconstruction_not_published', 'operation_id': OP,
            'reservation_gate': reservations, 'staging_directory': str(destination), 'artifacts': {path: r.blob_sha(raw) for path, raw in artifacts.items()},
            'bundle_sha256': bundle['bundle_sha256'], 'plan_sha256': bundle['plan_sha256'],
            'content_qa': 'not_evaluated', 'publication_target_writes_performed': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=v.ROOT); p.add_argument('--payloads-dir', type=Path)
    p.add_argument('--source-evidence', type=Path); p.add_argument('--stage-dir', type=Path)
    p.add_argument('--verify-installed', action='store_true')
    args = p.parse_args()
    try:
        if args.verify_installed:
            r.require(not any((args.payloads_dir, args.source_evidence, args.stage_dir)), 'choose verification or staging')
            report = validate_installed(args.root)
        else:
            r.require(all((args.payloads_dir, args.source_evidence, args.stage_dir)), 'staging requires payloads-dir, evidence and external stage-dir')
            from publication_bundle import targets_for
            payloads = {key: (args.payloads_dir / key.split(':', 1)[1]).read_text()
                        for key in targets_for('news-youtube-reddit', DAY)}
            report = stage(args.root, payloads, args.source_evidence.read_bytes(), args.stage_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status': 'blocked_recovery', 'error': str(exc)})); return 1

if __name__ == '__main__': raise SystemExit(main())
