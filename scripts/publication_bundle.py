#!/usr/bin/env python3
"""Freeze recoverable UTF-8 payloads; validate updates without doing any GitHub writes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import publication_recovery as r
import validate_daily_recommendations as v
import validate_journal as j

VAULT = 'ZJFILOVE/obsidian-vault'
MUSIC = 'ZJFILOVE/music-daily'
START, END = '<!-- AUTO:START -->', '<!-- AUTO:END -->'


def targets_for(project: str, day: str) -> dict[str, int]:
    v.iso_day(day)
    if project == 'journal':
        return {f'{VAULT}:{path}': 1 for path in
                (f'00-inbox/Journal/{day}.md', '00-inbox/Journal/Index.md', j.HISTORY)}
    if project == 'music':
        return {f'{MUSIC}:recommendations/{day[:4]}/{day[5:7]}/{day}.json': 1,
                f'{MUSIC}:state/tracks.json': 1,
                f'{VAULT}:Music/Daily/{day}.md': 2,
                f'{VAULT}:Music/Daily/manifests/{day}.json': 2,
                f'{VAULT}:Music/Daily/state/tracks.json': 2}
    if project == 'english':
        from datetime import date
        weekday = date.fromisoformat(day).weekday()
        paths = ([f'50-courses/English/{part}/{day}.md' for part in ('Daily', 'Translation', 'Vocabulary')]
                 if weekday < 5 else [f'50-courses/English/Weekly/{"TV/" if weekday == 5 else ""}{day}.md'])
        return {f'{VAULT}:{p}': 1 for p in paths + ['.recommendation/history/english.jsonl']}
    r.require(project == 'news-youtube-reddit', 'unsupported project')
    paths = [f'{p}/{day}.md' for p in ('News/Daily', 'Resources/YouTube/Daily', 'Resources/Reddit/Daily')]
    paths += ['.recommendation/history/youtube.jsonl', '.recommendation/history/reddit.jsonl']
    return {f'{VAULT}:{p}': 1 for p in paths}


def validate_payloads(plan: dict, payloads: dict, *, legacy_journal: bool = False) -> None:
    r.validate(plan)
    expected = targets_for(plan['project'], plan['date'])
    r.require(isinstance(payloads, dict) and set(payloads) == set(expected), 'missing or extra publication payload')
    actual = {t['repository'] + ':' + t['path']: t for t in plan['targets']}
    r.require(set(actual) == set(expected), 'missing or extra publication target')
    for key, t in actual.items():
        r.require('base_sha' in t, 'base_sha must be explicit; null only after confirmed absence')
        r.require(t['stage'] == expected[key], 'incorrect publication stage')
        r.require(isinstance(payloads[key], str), 'payload must be UTF-8 text')
        r.require(r.blob_sha(payloads[key].encode('utf-8')) == t['target_sha'], 'payload hash mismatch: ' + key)
        if key.endswith('.json'):
            v.strict_json(payloads[key])
        elif key.endswith('.jsonl'):
            r.require(payloads[key].endswith('\n'), 'history must end at a newline boundary')
            for line in payloads[key].splitlines():
                if line.strip():
                    r.require(isinstance(v.strict_json(line), dict), 'history row must be an object')
    day, project = plan['date'], plan['project']
    if project == 'music':
        manifest_key = f'{MUSIC}:recommendations/{day[:4]}/{day[5:7]}/{day}.json'
        mirror = f'{VAULT}:Music/Daily/manifests/{day}.json'
        doc = v.strict_json(payloads[manifest_key])
        tracks = doc.get('tracks', [])
        r.require(doc.get('date') == day and len(tracks) == 5, 'music date/count mismatch')
        r.require([t.get('position') for t in tracks] == [1, 2, 3, 4, 5], 'music positions mismatch')
        ids = [t['canonical_id'] for t in tracks]
        r.require(ids == plan['exposed_resource_ids'], 'selection changed')
        r.require(payloads[manifest_key] == payloads[mirror], 'manifest mirrors differ')
        r.require(payloads[f'{MUSIC}:state/tracks.json'] == payloads[f'{VAULT}:Music/Daily/state/tracks.json'], 'state mirrors differ')
        state = v.strict_json(payloads[f'{MUSIC}:state/tracks.json'])['recommended']
        r.require(set(ids) <= state.keys(), 'music selection not in permanent history')
        note_ids = v.MUSIC_SONG_RE.findall(payloads[f'{VAULT}:Music/Daily/{day}.md'])
        r.require(note_ids == [t['apple_music']['song_id'] for t in tracks], 'note order differs')
    elif project == 'english':
        notes = [k for k in expected if k.endswith('.md') and '/Translation/' not in k and '/Vocabulary/' not in k]
        url = v.extract_source_url(payloads[notes[0]])
        r.require(url is not None and [url] == plan['exposed_resource_ids'], 'English selection changed')
        rows = [v.strict_json(x) for x in payloads[f'{VAULT}:.recommendation/history/english.jsonl'].splitlines() if x.strip()]
        r.require(sum(x.get('date') == day and x.get('source_url') == url for x in rows) == 1, 'English publication must be registered exactly once')
    elif project == 'journal':
        rows = j.history_rows(payloads[f'{VAULT}:{j.HISTORY}'])
        selected = [row for row in rows if row['date'] == day]
        r.require(['doi:' + row['normalized_doi'] for row in selected] == plan['exposed_resource_ids'],
                  'Journal selection changed')
        j.validate_note(payloads[f'{VAULT}:00-inbox/Journal/{day}.md'], day, selected,
                        check_format=not legacy_journal)
        j.validate_index(payloads[f'{VAULT}:00-inbox/Journal/Index.md'], {row['date'] for row in rows})
    else:
        selected = []
        for name, pattern, count, field in [('youtube', v.YT_RE, 5, 'video_id'), ('reddit', v.REDDIT_RE, 10, 'post_id')]:
            dirname = 'YouTube' if name == 'youtube' else 'Reddit'
            ids = pattern.findall(payloads[f'{VAULT}:Resources/{dirname}/Daily/{day}.md'])
            if name == 'reddit': ids = [x.lower() for x in ids]
            r.require(len(ids) == count and len(set(ids)) == count, name + ' count/IDs mismatch')
            selected.extend(name + ':' + x for x in ids)
            rows = [v.strict_json(x) for x in payloads[f'{VAULT}:.recommendation/history/{name}.jsonl'].splitlines() if x.strip()]
            r.require(all(sum(x.get('date') == day and x.get(field) == value for x in rows) == 1 for value in ids), 'missing/duplicate history registration')
        if 'recovery_id' in plan:
            from discovery_recovery import validate_selection
            validate_selection(plan, selected)
        else:
            r.require(selected == plan['exposed_resource_ids'], 'discovery selection changed')


def freeze(plan: dict, payloads: dict, *, music_root=None, mirror_snapshot=None, expected_heads=None, discovery_root=None) -> dict:
    r.require(plan.get('schema_version') == 1, 'new bundles require plan schema_version=1')
    validate_payloads(plan, payloads)
    if plan['project'] == 'music':
        r.require(music_root is not None and mirror_snapshot is not None and expected_heads is not None,
                  'music freeze requires full history and pinned mirror evidence; run music_publication.py prepare before selection, then music_publication.py freeze (music_root is the Vault checkout)')
        from music_identity import publication_gate
        publication_gate(Path(music_root), plan, payloads, mirror_snapshot, expected_heads)
    body = {'schema_version': 1, 'plan': plan, 'payloads': payloads, 'plan_sha256': r.digest(plan)}
    bundle = {**body, 'bundle_sha256': r.digest(body)}
    if plan['project'] == 'news-youtube-reddit':
        r.require(discovery_root is not None, 'discovery freeze requires full history checkout')
        from discovery_recovery import reservation_gate
        reservation_gate(Path(discovery_root), bundle)
    return bundle


def verify(bundle: dict) -> None:
    r.require(isinstance(bundle, dict), 'invalid bundle envelope')
    legacy = bundle.get('schema_version') == 'journal-frozen-v1'
    keys = {'schema_version', 'plan', 'payloads', 'plan_sha256', 'bundle_sha256'}
    if legacy:
        keys |= {'status', 'compatibility_note', 'evidence'}
    r.require(set(bundle) == keys, 'invalid bundle envelope')
    r.require(bundle['schema_version'] == 1 or legacy, 'unsupported bundle version')
    body = {k: value for k, value in bundle.items() if k != 'bundle_sha256'}
    r.require(r.digest(body) == bundle['bundle_sha256'], 'persisted bundle changed')
    r.require(r.digest(bundle['plan']) == bundle['plan_sha256'], 'persisted plan changed')
    if legacy:
        r.require(bundle['status'] == 'PREPARED' and bundle['plan'].get('project') == 'journal',
                  'invalid legacy Journal record')
        r.require(bundle['plan'].get('version') == 1 and 'schema_version' not in bundle['plan'],
                  'invalid legacy Journal plan')
        papers = bundle['evidence'].get('papers')
        r.require(isinstance(papers, list) and
                  ['doi:' + j.normalize_doi(p['doi']) for p in papers] == bundle['plan']['exposed_resource_ids'],
                  'Journal evidence/selection mismatch')
    validate_payloads(bundle['plan'], payloads_for(bundle), legacy_journal=legacy)


def payloads_for(bundle: dict) -> dict:
    """Adapt old keys in memory; never rewrite an immutable PREPARED record or digest."""
    if bundle.get('schema_version') == 'journal-frozen-v1':
        return {VAULT + ':' + path: text for path, text in bundle['payloads'].items()}
    return bundle['payloads']


def preserve_note(old: str, new: str) -> None:
    if old == new: return
    r.require(old.count(START) == old.count(END) == new.count(START) == new.count(END) == 1, 'existing unmarked note cannot be replaced automatically')
    a, body = old.split(START); old_auto, b = body.split(END)
    c, body = new.split(START); new_auto, d = body.split(END)
    r.require(a == c and b == d, 'manual content outside AUTO markers changed')


def check_baselines(bundle: dict, baselines: dict) -> None:
    """Call just before write; missing read/error is not a null (confirmed new) base."""
    verify(bundle)
    payloads = payloads_for(bundle)
    for t in bundle['plan']['targets']:
        key = t['repository'] + ':' + t['path']
        r.require(key in baselines, 'baseline read missing')
        old = baselines[key]; new = payloads[key]
        if old is None:
            r.require(t['base_sha'] is None, 'existing baseline disappeared')
            continue
        r.require(isinstance(old, str), 'baseline must be verified text, not an API error')
        r.require(r.blob_sha(old.encode('utf-8')) == t['base_sha'], 'unexpected baseline SHA')
        if t['path'].endswith('.md'): preserve_note(old, new)
        elif t['path'].endswith('.jsonl'):
            r.require((not old or old.endswith('\n')) and new.startswith(old), 'history is not byte-prefix append-only')
        elif t['path'].endswith('state/tracks.json'):
            before, after = v.strict_json(old), v.strict_json(new)
            r.require(before['schema_version'] == after['schema_version'] and before['provider'] == after['provider'], 'state schema/provider changed')
            r.require(all(k in after['recommended'] and value == after['recommended'][k] for k, value in before['recommended'].items()), 'permanent music history changed')


def load_prepared(path: Path, root: Path | None = None) -> dict:
    bundle = v.strict_json(path.read_text(encoding='utf-8')); verify(bundle)
    from discovery_recovery import OP, TRANSACTION, validate_installed
    if bundle['plan'].get('recovery_id') or bundle['plan'].get('operation_id') == OP:
        r.require(root is not None and path.resolve() == (root / TRANSACTION).resolve(),
                  'registered recovery requires its complete repository evidence')
        validate_installed(root)
    return bundle


class ProjectDataError(ValueError):
    """A proven file-level failure, not an arbitrary validator exception."""
    def __init__(self, project, path, detail):
        self.project, self.path = project, path
        super().__init__(path + ': ' + detail)


def audit_registered_discovery(root):
    import discovery_recovery as d
    d.require_full_history(root)
    paths = [d.RECEIPT, d.ARCHIVE, d.EVIDENCE, d.TRANSACTION, d.FAILURE,
             d.ORIGINAL_PLAN_FILE, d.ORIGINAL_REDDIT, *d.ORIGINAL_NOTES.values(),
             '.recommendation/transaction-runs/news-youtube-reddit/2026-11-08/recovery-source-inputs.zip']
    versions = d.historical_evidence(root, paths)
    for path, recorded in versions.items():
        if path == d.TRANSACTION: recorded = recorded - {d.BAD_BLOB}
        if not recorded: continue  # staging has no committed baseline yet
        if not (root / path).is_file():
            raise ProjectDataError('news-youtube-reddit', path, 'committed recovery data missing')
        if recorded != {r.blob_sha((root / path).read_bytes())}:
            raise ProjectDataError('news-youtube-reddit', path, 'immutable recovery data differs from recorded ancestry')
    # Shared-code errors and unclassified failures are deliberately not wrapped.
    return d.validate_installed(root)


def audit_journal(root: Path, base: str | None = None) -> dict:
    from discovery_recovery import RECEIPT, validate_installed, git as recovery_git
    registered = (root / RECEIPT).exists()
    if (root / '.git').exists():
        registered = registered or bool(recovery_git(root, 'log', '--format=%H', 'HEAD', '--', RECEIPT).strip())
    if registered: audit_registered_discovery(root)
    directory = root / '.recommendation/transactions'
    paths = sorted(directory.rglob('*.json')) if directory.exists() else []
    for path in paths:
        try:
            bundle = load_prepared(path, root)
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError(f'{path.relative_to(root)}: {exc}') from exc
        plan = bundle['plan']
        r.require(path.relative_to(directory).as_posix() == plan['project'] + '/' + plan['date'] + '.json', 'transaction path/operation mismatch')
    if base:
        from check_daily_integrity import git
        r.sha(base); git(root, 'merge-base', '--is-ancestor', base, 'HEAD')
        names = git(root, 'ls-tree', '-rz', '--name-only', base, '--', '.recommendation/transactions').split(b'\0')
        for name in names:
            if name.endswith(b'.json'):
                rel = name.decode('utf-8'); old = git(root, 'show', base + ':' + rel)
                if (root / rel).is_file() and (root / rel).read_bytes() == old: continue
                from discovery_recovery import TRANSACTION, BAD_BLOB, validate_installed
                r.require(rel == TRANSACTION and r.blob_sha(old) == BAD_BLOB,
                          'PREPARED transaction was rewritten or deleted: ' + rel)
                validate_installed(root)
    return {'status': 'passed_immutable_publication_bundles', 'bundles': len(paths), 'base_ref': base, 'content_qa': 'not_evaluated'}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle', type=Path, nargs='?'); p.add_argument('--observations', type=Path)
    p.add_argument('--journal-root', type=Path); p.add_argument('--base-ref')
    p.add_argument('--discovery-root', type=Path)
    p.add_argument('--music-root', type=Path); p.add_argument('--mirror-snapshot', type=Path)
    p.add_argument('--music-head'); p.add_argument('--vault-head')
    p.add_argument('--baselines', type=Path); p.add_argument('--expected-bundle-digest')
    args = p.parse_args()
    try:
        if args.journal_root is not None:
            r.require(args.bundle is None, 'choose bundle or journal-root')
            print(json.dumps(audit_journal(args.journal_root, args.base_ref), ensure_ascii=False, indent=2)); return 0
        r.require(args.bundle is not None, 'bundle or journal-root required')
        bundle = load_prepared(args.bundle, args.discovery_root)
        if args.expected_bundle_digest is not None:
            r.require(args.expected_bundle_digest == bundle['bundle_sha256'], 'original PREPARED bundle digest changed')
        if args.baselines: check_baselines(bundle, v.strict_json(args.baselines.read_text(encoding='utf-8')))
        result = {'status': 'bundle_valid', 'operation_id': bundle['plan']['operation_id'], 'bundle_sha256': bundle['bundle_sha256'], 'github_writes_performed': 0, 'content_qa': 'not_evaluated'}
        if args.observations and bundle['plan']['project'] == 'music':
            r.require(args.music_root is not None and args.mirror_snapshot is not None and
                      args.music_head is not None and args.vault_head is not None,
                      'music publication requires full history and pinned mirror evidence')
            from music_identity import recovery_gate
            result['music_gate'] = recovery_gate(args.music_root, bundle,
                v.strict_json(args.mirror_snapshot.read_text()),
                {'music': args.music_head, 'vault': args.vault_head},
                v.strict_json(args.observations.read_text()))
        if args.observations and bundle['plan']['project'] == 'news-youtube-reddit':
            r.require(args.discovery_root is not None, 'discovery recovery requires full history checkout')
            from discovery_recovery import reservation_gate
            result['discovery_gate'] = reservation_gate(args.discovery_root, bundle)
        if args.observations:
            r.require(args.expected_bundle_digest is not None, 'retries require original PREPARED digest')
            result.update(r.inspect(bundle['plan'], v.strict_json(args.observations.read_text(encoding='utf-8')), bundle['plan_sha256']))
        print(json.dumps(result, ensure_ascii=False, indent=2)); return int(result['status'] == 'blocked')
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}, ensure_ascii=False)); return 1

if __name__ == '__main__': raise SystemExit(main())
