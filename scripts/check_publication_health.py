#!/usr/bin/env python3
"""Independent local reports: one failed check must not hide the others."""
import argparse
import json
from pathlib import Path
import subprocess
import check_daily_integrity as integrity
import publication_bundle as bundles
import music_identity as music
import validate_daily_recommendations as v


def audit(root, base=None):
    checks = {}
    for name, check in (
        ('integrity', lambda: integrity.audit(root, v.strict_json((root / '.recommendation/policy.json').read_text())['strict_from'], base)),
        ('immutable_bundles', lambda: bundles.audit_journal(root, base)),
        ('permanent_music_identity', lambda: music.index(root)),
    ):
        try:
            result = check()
            if name == 'permanent_music_identity':
                result = {k: value for k, value in result.items() if k not in ('records', 'prepared')}
            checks[name] = result
        except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, SystemExit) as exc:
            checks[name] = {'status': 'failed', 'error': str(exc)}
    failed = any(x['status'] in ('failed', 'incomplete_identity_evidence') for x in checks.values())
    return {'status': 'blocked' if failed else 'passed_local_checks', 'checks': checks,
            'content_qa': 'not_evaluated', 'mirror_status': 'not_checked', 'transport': 'not_evaluated'}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=v.ROOT); p.add_argument('--base-ref')
    args = p.parse_args(); result = audit(args.root, args.base_ref)
    print(json.dumps(result, ensure_ascii=False, indent=2)); return int(result['status'] == 'blocked')

if __name__ == '__main__': raise SystemExit(main())
