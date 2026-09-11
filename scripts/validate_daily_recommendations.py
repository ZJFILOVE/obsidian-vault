#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRICT_FROM = "2026-09-11"

YOUTUBE_DIR = ROOT / "Resources" / "YouTube" / "Daily"
REDDIT_DIR = ROOT / "Resources" / "Reddit" / "Daily"
ENGLISH_DIR = ROOT / "50-courses" / "English" / "Daily"
MUSIC_DIR = ROOT / "Music" / "Daily"
POLICY = ROOT / ".recommendation" / "policy.json"
YOUTUBE_HISTORY = ROOT / ".recommendation" / "history" / "youtube.jsonl"
REDDIT_HISTORY = ROOT / ".recommendation" / "history" / "reddit.jsonl"
ENGLISH_HISTORY = ROOT / ".recommendation" / "history" / "english.jsonl"

YT_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})")
REDDIT_RE = re.compile(r"reddit\.com/r/[^/]+/comments/([A-Za-z0-9]+)", re.I)
URL_RE = re.compile(r"https?://[^\s)>]+")
MUSIC_SONG_RE = re.compile(r"https://music\.apple\.com/cn/song/(?:[^/]+/)?([0-9]+)")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def date_from_path(path: Path) -> str:
    m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.md", path.name)
    if not m:
        fail(f"unexpected dated filename: {path}")
    return m.group(1)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_jsonl(path: Path, required_key: str) -> None:
    if not path.exists():
        fail(f"missing history index: {path.relative_to(ROOT)}")
    for lineno, line in enumerate(text(path).splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path.relative_to(ROOT)}:{lineno}: invalid JSON: {exc}")
        if required_key not in obj:
            fail(f"{path.relative_to(ROOT)}:{lineno}: missing {required_key}")


def validate_youtube() -> int:
    seen: set[str] = set()
    checked = 0
    for path in sorted(YOUTUBE_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        ids = YT_RE.findall(text(path))
        unique = set(ids)
        if date >= STRICT_FROM:
            if len(ids) != 5 or len(unique) != 5:
                fail(f"{path.relative_to(ROOT)}: strict daily must contain exactly 5 unique YouTube video IDs, found {len(ids)} / {len(unique)}")
            dup = unique & seen
            if dup:
                fail(f"{path.relative_to(ROOT)}: repeats earlier YouTube IDs: {sorted(dup)}")
            checked += len(unique)
        seen.update(unique)
    return checked


def validate_reddit() -> int:
    seen: set[str] = set()
    checked = 0
    for path in sorted(REDDIT_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        ids = [x.lower() for x in REDDIT_RE.findall(text(path))]
        unique = set(ids)
        if date >= STRICT_FROM:
            if len(ids) != 10 or len(unique) != 10:
                fail(f"{path.relative_to(ROOT)}: strict daily must contain exactly 10 unique Reddit post IDs, found {len(ids)} / {len(unique)}")
            dup = unique & seen
            if dup:
                fail(f"{path.relative_to(ROOT)}: repeats earlier Reddit post IDs: {sorted(dup)}")
            checked += len(unique)
        seen.update(unique)
    return checked


def extract_source_url(note: str) -> str | None:
    for line in note.splitlines():
        low = line.lower()
        if "source url" in low or re.match(r"^\s*-?\s*\*\*?source\*\*?\s*:", line, re.I) or re.match(r"^\s*-\s*source\s*:", line, re.I):
            m = URL_RE.search(line)
            if m:
                return m.group(0).rstrip(".,;\"")
    return None


def validate_english() -> int:
    seen: set[str] = set()
    checked = 0
    for path in sorted(ENGLISH_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        url = extract_source_url(text(path))
        if url is None:
            if date >= STRICT_FROM:
                fail(f"{path.relative_to(ROOT)}: strict daily must contain a Source URL")
            continue
        if date >= STRICT_FROM:
            if url in seen:
                fail(f"{path.relative_to(ROOT)}: English source URL already used earlier: {url}")
            checked += 1
        seen.add(url)
    return checked


def frontmatter_value(note: str, key: str) -> str | None:
    if not note.startswith("---\n"):
        return None
    end = note.find("\n---", 4)
    if end == -1:
        return None
    front = note[4:end]
    m = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", front)
    return m.group(1).strip() if m else None


def validate_music() -> int:
    checked = 0
    required_markers = [
        "### 为什么今天推荐",
        "### 编曲与音色",
        "### 具体聆听点",
        "**Album:**",
        "**song_id:**",
        "**Apple Music：中国大陆区**",
    ]
    for path in sorted(MUSIC_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        if date < STRICT_FROM:
            continue
        note = text(path)
        song_ids = MUSIC_SONG_RE.findall(note)
        if len(song_ids) != 5 or len(set(song_ids)) != 5:
            fail(f"{path.relative_to(ROOT)}: strict daily must contain 5 unique direct Apple Music China song URLs")
        for marker in required_markers:
            count = note.count(marker)
            expected = 5 if marker.startswith("###") or marker.startswith("**Album") or marker.startswith("**song_id") or marker.startswith("**Apple Music") else 1
            if count != expected:
                fail(f"{path.relative_to(ROOT)}: expected {expected} occurrences of {marker!r}, found {count}")
        manifest = frontmatter_value(note, "manifest")
        if not manifest:
            fail(f"{path.relative_to(ROOT)}: missing manifest frontmatter")
        manifest_path = ROOT / manifest
        if not manifest_path.exists():
            fail(f"{path.relative_to(ROOT)}: referenced manifest does not exist: {manifest}")
        try:
            data = json.loads(text(manifest_path))
        except Exception as exc:
            fail(f"{manifest}: invalid JSON: {exc}")
        tracks = data.get("tracks")
        if not isinstance(tracks, list) or len(tracks) != 5:
            fail(f"{manifest}: must contain exactly 5 tracks")
        manifest_ids = [str(t.get("apple_music", {}).get("song_id", "")) for t in tracks]
        if manifest_ids != song_ids:
            fail(f"{path.relative_to(ROOT)}: note song IDs do not match manifest order")
        for t in tracks:
            if len(str(t.get("analysis_summary", "")).strip()) < 35:
                fail(f"{manifest}: analysis_summary too short for {t.get('title')}")
            if len(str(t.get("listening_cue", "")).strip()) < 20:
                fail(f"{manifest}: listening_cue too short for {t.get('title')}")
        checked += 5
    return checked


def main() -> None:
    if not POLICY.exists():
        fail("missing .recommendation/policy.json")
    try:
        policy = json.loads(text(POLICY))
    except Exception as exc:
        fail(f"invalid recommendation policy: {exc}")
    if policy.get("version") != 2:
        fail("recommendation policy must be version 2")

    validate_jsonl(YOUTUBE_HISTORY, "video_id")
    validate_jsonl(REDDIT_HISTORY, "post_id")
    validate_jsonl(ENGLISH_HISTORY, "source_url")

    yt = validate_youtube()
    rd = validate_reddit()
    en = validate_english()
    mu = validate_music()
    print(f"OK: strict daily recommendations validated — youtube={yt}, reddit={rd}, english={en}, music={mu}")


if __name__ == "__main__":
    main()
