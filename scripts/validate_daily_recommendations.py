#!/usr/bin/env python3
from __future__ import annotations

from datetime import date as calendar_date
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

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

YT_RE = re.compile(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})(?=$|[\s<>"`()\[\]{},;.!?&#/])')
REDDIT_RE = re.compile(r'https?://(?:(?:www|old)\.)?reddit\.com/r/[^/\s<>"`()]+/comments/([A-Za-z0-9]+)(?=$|[/\s<>"`()\[\]{},;.!?&#])', re.I)
URL_RE = re.compile(r"https?://[^\s)>]+")
# Neither the slug nor the numeric ID may consume a neighbouring Markdown line.
# A non-delimiter after the ID must reject the whole URL, not truncate its ID.
MUSIC_SONG_RE = re.compile(
    r'https://music\.apple\.com/cn/song/(?:[^/\s<>"`?#()\[\]{}]+/)?'
    r'([0-9]+)(?=$|[\s<>"`()\[\]{},;.!])'
)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def iso_day(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError(f"invalid date format: {value!r}")
    calendar_date.fromisoformat(value)
    return value


def date_from_path(path: Path) -> str:
    if path.suffix != ".md":
        fail(f"unexpected dated filename: {path}")
    try:
        return iso_day(path.stem)
    except ValueError as exc:
        fail(f"{path}: {exc}")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strict_json(value: str) -> object:
    def unique(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = item
        return result
    def nonfinite(value):
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(value, object_pairs_hook=unique, parse_constant=nonfinite)


def validate_jsonl(path: Path, required_key: str) -> list[dict]:
    if not path.is_file():
        fail(f"missing history index: {path}")
    rows, pairs = [], set()
    for lineno, line in enumerate(text(path).splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = strict_json(line)
            if not isinstance(obj, dict):
                raise ValueError("history row must be an object")
            day = iso_day(obj.get("date"))
            value = obj.get(required_key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"missing or non-string {required_key}")
            if required_key == "video_id" and not re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
                raise ValueError("invalid video_id")
            if required_key == "post_id":
                if not re.fullmatch(r"[A-Za-z0-9]+", value):
                    raise ValueError("invalid post_id")
                value = value.lower()
            if required_key == "source_url":
                parsed = urlsplit(value)
                if parsed.scheme not in ("http", "https") or not parsed.netloc or re.search(r"\s", value):
                    raise ValueError("invalid source_url")
            pair = (day, value)
            if pair in pairs:
                raise ValueError(f"duplicate same-date history append: {pair}")
            pairs.add(pair)
            rows.append(obj)
        except (ValueError, TypeError) as exc:
            fail(f"{path}:{lineno}: {exc}")
    if not rows:
        fail(f"empty history index: {path}")
    return rows


def recorded_pairs(rows: list[dict] | None, key: str) -> set[tuple[str, str]]:
    return {(r["date"], r[key].lower() if key == "post_id" else r[key]) for r in rows or []}


def require_recorded(path: Path, day: str, ids: set[str], pairs: set[tuple[str, str]]) -> None:
    missing = sorted(value for value in ids if (day, value) not in pairs)
    if missing:
        fail(f"{path}: published resources missing from permanent history: {missing}")


def validate_youtube(history: list[dict] | None = None) -> int:
    pairs = recorded_pairs(history, "video_id")
    seen: set[str] = set()
    checked = 0
    for path in sorted(YOUTUBE_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        ids = YT_RE.findall(text(path))
        unique = set(ids)
        if history is not None:
            require_recorded(path, date, unique, pairs)
        if date >= STRICT_FROM:
            if len(ids) != 5 or len(unique) != 5:
                fail(f"{path.relative_to(ROOT)}: strict daily must contain exactly 5 unique YouTube video IDs, found {len(ids)} / {len(unique)}")
            dup = unique & (seen | {value for day, value in pairs if day < date})
            if dup:
                fail(f"{path.relative_to(ROOT)}: repeats earlier YouTube IDs: {sorted(dup)}")
            checked += len(unique)
        seen.update(unique)
    return checked


def validate_reddit(history: list[dict] | None = None) -> int:
    pairs = recorded_pairs(history, "post_id")
    seen: set[str] = set()
    checked = 0
    for path in sorted(REDDIT_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        ids = [x.lower() for x in REDDIT_RE.findall(text(path))]
        unique = set(ids)
        if history is not None:
            require_recorded(path, date, unique, pairs)
        if date >= STRICT_FROM:
            if len(ids) != 10 or len(unique) != 10:
                fail(f"{path.relative_to(ROOT)}: strict daily must contain exactly 10 unique Reddit post IDs, found {len(ids)} / {len(unique)}")
            dup = unique & (seen | {value for day, value in pairs if day < date})
            if dup:
                fail(f"{path.relative_to(ROOT)}: repeats earlier Reddit post IDs: {sorted(dup)}")
            checked += len(unique)
        seen.update(unique)
    return checked


def extract_source_url(note: str) -> str | None:
    value = frontmatter_value(note, "source_url")
    if value:
        value = value.strip("\"' ")
        if re.fullmatch(r"https?://[^\s<>]+", value):
            return value
    for line in note.splitlines():
        plain = re.sub(r"^\s*-\s*", "", line).replace("**", "").strip()
        if re.match(r"^(?:source(?:[ \t]+url)?|official page \+ transcript|official video|official episode page)[ \t]*:", plain, re.I):
            match = URL_RE.search(plain)
            if match:
                return match.group(0).rstrip(".,;\"")
    return None


def validate_english(history: list[dict] | None = None) -> int:
    seen: set[str] = set()
    pairs = recorded_pairs(history, "source_url")
    checked = 0
    english_root = ENGLISH_DIR.parent
    paths = list(ENGLISH_DIR.glob("????-??-??.md"))
    paths += list((english_root / "Weekly").rglob("????-??-??.md"))
    for path in sorted(paths, key=lambda p: (p.stem, p.as_posix())):
        day = date_from_path(path)
        url = extract_source_url(text(path))
        if url is None:
            fail(f"{path}: published English material must contain a Source URL")
        if history is not None:
            require_recorded(path, day, {url}, pairs)
        if day >= STRICT_FROM:
            if url in seen or any(old_day < day and old_url == url for old_day, old_url in pairs):
                fail(f"{path}: English source URL already used earlier: {url}")
            checked += 1
        seen.add(url)
        if path.parent == ENGLISH_DIR:
            for component in ("Translation", "Vocabulary"):
                if not (english_root / component / path.name).is_file():
                    fail(f"{path}: missing same-day {component} material")
    return checked


def frontmatter_value(note: str, key: str) -> str | None:
    front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", note, re.S)
    if front is None:
        return None
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*([^\r\n]+)$", front.group(1))
    return match.group(1).strip() if match else None


def music_fields(note: str) -> dict[str, list[str]]:
    fields = {"Album": [], "song_id": [], "Apple Music": []}
    for line in note.splitlines():
        plain = re.sub(r"^\s*[-*]\s+", "", line).replace("**", "").strip()
        for field, pattern in (
            ("Album", r"^Album[:：]\s*(\S.*)$"),
            ("song_id", r"^song_id[:：]\s*`?([0-9]+)`?\s*$"),
            ("Apple Music", r"^Apple Music(?:\s*(?:CN|国区)|（中国大陆）)?\s*[:：](?:中国大陆区)?\s*(https://\S+)$"),
        ):
            match = re.match(pattern, plain, re.I)
            if match:
                fields[field].append(match.group(1))
    return fields


def validate_music() -> int:
    checked = 0
    required_markers = [
        "### 为什么今天推荐",
        "### 编曲与音色",
        "### 具体聆听点",
    ]
    for path in sorted(MUSIC_DIR.glob("????-??-??.md")):
        date = date_from_path(path)
        if date < STRICT_FROM:
            continue
        from music_withdrawal import count_for
        expected_count = count_for(ROOT, date)
        note = text(path)
        song_ids = MUSIC_SONG_RE.findall(note)
        if len(song_ids) != expected_count or len(set(song_ids)) != expected_count:
            fail(f"{path.relative_to(ROOT)}: strict daily must contain {expected_count} unique direct Apple Music China song URLs")
        blocks = [b for b in re.split(r"(?m)^##[ \t]+", note) if MUSIC_SONG_RE.search(b)]
        if len(blocks) != expected_count:
            fail(f"{path}: expected {expected_count} distinct song sections")
        for position, block in enumerate(blocks, 1):
            for field, values in music_fields(block).items():
                if len(values) != 1:
                    fail(f"{path}: song {position} needs one non-empty {field} field")
            direct = music_fields(block)["Apple Music"][0]
            if MUSIC_SONG_RE.fullmatch(direct) is None:
                fail(f"{path}: song {position} has a malformed direct URL")
            if len(MUSIC_SONG_RE.findall(block)) != 1:
                fail(f"{path}: song {position} must have exactly one direct song URL")
            for marker in required_markers:
                headings = re.findall(rf"(?m)^{re.escape(marker)}[ \t]*$", block)
                if len(headings) != 1:
                    fail(f"{path}: song {position} needs one {marker!r}")
        # Markdown presentation is not a data constraint: both existing bold
        # metadata and ordinary list metadata are accepted. Values remain required.
        fields = music_fields(note)
        for field, values in fields.items():
            if len(values) != expected_count:
                fail(f"{path.relative_to(ROOT)}: expected {expected_count} non-empty {field} fields, found {len(values)}")
        if fields["song_id"] != song_ids:
            fail(f"{path.relative_to(ROOT)}: song_id fields do not match direct URL order")
        manifest = frontmatter_value(note, "manifest")
        if not manifest:
            fail(f"{path.relative_to(ROOT)}: missing manifest frontmatter")
        manifest_path = (ROOT / manifest).resolve()
        if not manifest_path.is_relative_to(ROOT.resolve()):
            fail(f"{path.relative_to(ROOT)}: manifest path escapes vault")
        if not manifest_path.exists():
            fail(f"{path.relative_to(ROOT)}: referenced manifest does not exist: {manifest}")
        try:
            data = strict_json(text(manifest_path))
        except Exception as exc:
            fail(f"{manifest}: invalid JSON: {exc}")
        if not isinstance(data, dict):
            fail(f"{manifest}: root must be an object")
        tracks = data.get("tracks")
        if not isinstance(tracks, list) or len(tracks) != expected_count:
            fail(f"{manifest}: must contain exactly {expected_count} tracks")
        manifest_ids = [str(t.get("apple_music", {}).get("song_id", "")) for t in tracks]
        if manifest_ids != song_ids:
            fail(f"{path.relative_to(ROOT)}: note song IDs do not match manifest order")
        for t in tracks:
            if len(str(t.get("analysis_summary", "")).strip()) < 35:
                fail(f"{manifest}: analysis_summary too short for {t.get('title')}")
            if len(str(t.get("listening_cue", "")).strip()) < 20:
                fail(f"{manifest}: listening_cue too short for {t.get('title')}")
        checked += expected_count
    return checked


def main() -> None:
    global STRICT_FROM
    if not POLICY.exists():
        fail("missing .recommendation/policy.json")
    try:
        policy = strict_json(text(POLICY))
        if not isinstance(policy, dict):
            raise ValueError("policy root must be an object")
        STRICT_FROM = iso_day(policy.get("strict_from"))
    except Exception as exc:
        fail(f"invalid recommendation policy: {exc}")
    if policy.get("version") != 2:
        fail("recommendation policy must be version 2")

    for directory in (YOUTUBE_DIR, REDDIT_DIR, ENGLISH_DIR, MUSIC_DIR):
        if not any(directory.glob("????-??-??.md")):
            fail(f"missing or empty publication directory: {directory}")
    youtube_history = validate_jsonl(YOUTUBE_HISTORY, "video_id")
    reddit_history = validate_jsonl(REDDIT_HISTORY, "post_id")
    english_history = validate_jsonl(ENGLISH_HISTORY, "source_url")

    yt = validate_youtube(youtube_history)
    rd = validate_reddit(reddit_history)
    en = validate_english(english_history)
    mu = validate_music()
    print(f"OK: strict daily recommendations validated — youtube={yt}, reddit={rd}, english={en}, music={mu}")


if __name__ == "__main__":
    main()
