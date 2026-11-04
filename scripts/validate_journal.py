#!/usr/bin/env python3
"""Read-only Journal structure, identity and append-only checks, not literature QA."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlparse
import validate_daily_recommendations as v
from publication_recovery import require

HISTORY = '.recommendation/history/journal.jsonl'
NOTES = '00-inbox/Journal'
DOI_LINK = re.compile(r'https://(?:dx\.)?doi\.org/([^\s<>\)]+)', re.I)
INDEX_LINK = re.compile(r'\[\[(?:00-inbox/Journal/)?(\d{4}-\d{2}-\d{2})(?:\.md)?(?:\|[^\]]*)?\]\]')
START, END = '<!-- AUTO:START -->', '<!-- AUTO:END -->'


def normalize_doi(value: str) -> str:
    require(isinstance(value, str), 'DOI must be text')
    value = unquote(value.strip()).lower()
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value)
    require(re.fullmatch(r'10\.\d{4,9}/[^\s<>]+', value) is not None, 'invalid DOI: ' + value)
    return value


def normalize_title(value: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def history_rows(text: str) -> list[dict]:
    require(bool(text) and text.endswith('\n'), 'Journal history must end at a newline boundary')
    rows, versions, titles = [], set(), set()
    for number, line in enumerate(text.splitlines(), 1):
        require(bool(line.strip()), f'Journal history line {number}: empty row')
        row = v.strict_json(line)
        require(isinstance(row, dict), 'Journal history row must be an object')
        day = v.iso_day(row.get('date'))
        doi = normalize_doi(row.get('doi'))
        require(row.get('normalized_doi') == doi, 'Journal normalized DOI mismatch')
        require(row.get('operation_id') == 'journal:' + day, 'Journal operation/date mismatch')
        require(row.get('note_path') == f'{NOTES}/{day}.md', 'Journal note path mismatch')
        for key in ('title', 'authors', 'journal', 'source_url', 'reading_scope', 'publication_status'):
            require(isinstance(row.get(key), str) and bool(row[key].strip()), 'Journal missing ' + key)
        require(type(row.get('year')) is int and 1500 <= row['year'] <= int(day[:4]) + 1, 'invalid paper year')
        source = urlparse(row['source_url'])
        require(source.scheme == 'https' and bool(source.hostname), 'invalid Journal source URL')
        title = normalize_title(row['title'])
        require(bool(title) and row.get('normalized_title') == title, 'Journal normalized title mismatch')
        require(title not in titles, 'Journal repeated title: ' + row['title'])
        aliases = row.get('work_versions')
        require(isinstance(aliases, list) and bool(aliases), 'Journal work_versions required')
        normalized = [normalize_doi(x) for x in aliases]
        require(doi in normalized and len(normalized) == len(set(normalized)), 'invalid Journal version identities')
        require(not versions.intersection(normalized), 'Journal repeated DOI or study version: ' + doi)
        require(row['publication_status'] != 'retracted', 'retracted paper cannot be a normal recommendation')
        versions.update(normalized); titles.add(title); rows.append(row)
    return rows


def auto_content(note: str) -> str:
    require(note.count(START) == note.count(END) == 1, 'Journal requires one AUTO block')
    require(note.index(START) < note.index(END), 'Journal AUTO markers reversed')
    require(re.search(r'^## Notes\s*$', note.split(END, 1)[1], re.M), 'Journal Notes section missing')
    return note.split(START, 1)[1].split(END, 1)[0]


def validate_note(note: str, day: str, rows: list[dict], *, check_format: bool = True) -> None:
    shortfall = re.search(r'^## 数量说明\s*\n([^#\n][^\n]{10,})', note, re.M)
    require(2 <= len(rows) <= 4 or (len(rows) == 1 and shortfall),
            f'{day}: Journal requires 2–4 papers, or an explicit quality shortfall reason')
    require(re.match(r'\A---\r?\n', note) is not None, 'Journal frontmatter missing')
    front = note.split('---', 2)[1]
    require(re.search(r'^date:\s*' + re.escape(day) + r'\s*$', front, re.M), 'Journal note date mismatch')
    require(re.search(r'^type:\s*journal-daily\s*$', front, re.M), 'Journal note type mismatch')
    body = auto_content(note)
    if check_format:
        require(re.search(r'\*\*[^*\n]+[：:。？！]\*\*\S', body) is None,
                f'{day}: add a space after the bold label, e.g. **问题与观测：** DrBphP')
    ids = list(dict.fromkeys(normalize_doi(x) for x in DOI_LINK.findall(body)))
    require(ids == [row['normalized_doi'] for row in rows], f'{day}: Journal note/history DOI order differs')
    headings = [normalize_title(x) for x in re.findall(r'^## (.+)$', body, re.M)]
    for row in rows:
        require(any(row['normalized_title'] in h for h in headings), f'{day}: paper title missing from heading')
    require('精读' in body and '阅读' in body and 'reviewer_synthesis' in body, 'Journal reading/evidence labels missing')


def validate_index(note: str, dates: set[str]) -> None:
    listed = INDEX_LINK.findall(auto_content(note))
    require(len(listed) == len(set(listed)) and set(listed) == dates, 'Journal index/history dates differ')


def audit(root: Path, base: str | None = None) -> dict:
    path = root / HISTORY
    notes = {p.stem: p for p in (root / NOTES).glob('????-??-??.md')}
    if not path.exists():
        require(not notes, 'Journal notes exist without permanent history')
        if base:
            from check_daily_integrity import git
            require(not git(root, 'ls-tree', '-z', base, '--', HISTORY), 'Journal history was deleted')
        return {'status': 'not_started', 'days': 0, 'papers': 0}
    rows = history_rows(path.read_text(encoding='utf-8'))
    days = {row['date'] for row in rows}
    require(set(notes) == days, 'Journal orphan note or missing daily note')
    validate_index((root / NOTES / 'Index.md').read_text(encoding='utf-8'), days)
    for day, note in notes.items():
        validate_note(note.read_text(encoding='utf-8'), day, [row for row in rows if row['date'] == day])
    if base:
        from check_daily_integrity import git, preserve_prefix
        require(re.fullmatch(r'[0-9a-f]{40}', base) is not None, 'base-ref must be a full commit SHA')
        git(root, 'merge-base', '--is-ancestor', base, 'HEAD')
        if git(root, 'ls-tree', '-z', base, '--', HISTORY):
            preserve_prefix(git(root, 'show', base + ':' + HISTORY), path.read_bytes(), HISTORY)
    return {'status': 'passed_journal_integrity', 'days': len(days), 'papers': len(rows),
            'dates': sorted(days), 'append_only': 'passed_against_base' if base else 'not_checked',
            'content_qa': 'not_evaluated'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=v.ROOT)
    parser.add_argument('--base-ref')
    args = parser.parse_args()
    try:
        result = audit(args.root, args.base_ref)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}, ensure_ascii=False)); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
