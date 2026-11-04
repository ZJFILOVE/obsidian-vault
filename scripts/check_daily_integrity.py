#!/usr/bin/env python3
"""Read-only integrity/append-only checks; never certify live sources or delivery."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import validate_daily_recommendations as v
import validate_journal as j

HISTORIES = {"youtube": "video_id", "reddit": "post_id", "english": "source_url"}
STATE = "Music/Daily/state/tracks.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def preserve_prefix(old: bytes, new: bytes, path: str) -> None:
    require(new.startswith(old), f"{path}: append-only history was rewritten or deleted")
    if old and not old.endswith(b"\n") and len(new) > len(old):
        require(new[len(old):].startswith(b"\n"), f"{path}: append must start on a new line")


def preserve_state(old: dict, new: dict) -> None:
    require(isinstance(old.get("recommended"), dict), "base state is not a mapping")
    require(isinstance(new.get("recommended"), dict), "current state is not a mapping")
    require(all(k in new["recommended"] and new["recommended"][k] == value
                for k, value in old["recommended"].items()),
            "music permanent history entries were deleted or changed")


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def check_append_only(root: Path, base: str) -> None:
    require(re.fullmatch(r"[0-9a-f]{40}", base) is not None, "base-ref must be a full commit SHA")
    git(root, "cat-file", "-e", base + "^{commit}")
    git(root, "merge-base", "--is-ancestor", base, "HEAD")
    paths = [f".recommendation/history/{name}.jsonl" for name in HISTORIES] + [j.HISTORY, STATE]
    for path in paths:
        if not git(root, "ls-tree", "-z", base, "--", path):
            continue  # A newly introduced index has no prior bytes to preserve.
        old, new = git(root, "show", base + ":" + path), (root / path).read_bytes()
        if path == STATE:
            preserve_state(v.strict_json(old.decode("utf-8")), v.strict_json(new.decode("utf-8")))
        else:
            preserve_prefix(old, new, path)


def audit(root: Path, strict_from: str, base: str | None = None) -> dict:
    histories, legacy = {}, []
    for name, key in HISTORIES.items():
        rows = v.validate_jsonl(root / f".recommendation/history/{name}.jsonl", key)
        dates = {}
        for row in rows:
            value = row[key].lower() if key == "post_id" else row[key]
            dates.setdefault(value, set()).add(row["date"])
        for value, days in dates.items():
            if len(days) > 1:
                require(max(days) < strict_from, f"{name}: resource repeated after strict policy: {value}")
                legacy.append({"project": name, "resource_id": value, "dates": sorted(days),
                               "action": "retain all historical records; block every future reuse"})
        histories[name] = {"rows": len(rows), "unique_resources": len(dates)}
    state_doc = v.strict_json((root / STATE).read_text(encoding="utf-8"))
    require(isinstance(state_doc, dict), "state root must be an object")
    require(state_doc.get("provider") == "apple_music" and state_doc.get("schema_version") == 1,
            "wrong music state provider/schema")
    state = state_doc.get("recommended")
    require(isinstance(state, dict) and bool(state), "music state must be a non-empty mapping")
    for key, value in state.items():
        require(isinstance(key, str) and "::" in key and all(key.split("::", 1)), "invalid canonical ID")
        if type(value) is int:
            require(value >= 1, "invalid legacy history count")
        else:
            require(isinstance(value, dict) and type(value.get("count")) is int and value["count"] >= 1,
                    "invalid history count")
            require(v.iso_day(value.get("first_recommended")) <= v.iso_day(value.get("last_recommended")),
                    "reversed music history dates")
    manifests = sorted((root / "Music/Daily/manifests").glob("*.json"))
    require(bool(manifests), "no music manifests found")
    cids, sids, dates = set(), set(), set()
    for path in manifests:
        doc = v.strict_json(path.read_text(encoding="utf-8"))
        require(isinstance(doc, dict), f"{path.name}: manifest must be an object")
        day = v.iso_day(doc.get("date"))
        require(path.stem == day, f"{path.name}: date mismatch")
        tracks = doc.get("tracks")
        require(isinstance(tracks, list) and len(tracks) == 5, f"{day}: not exactly five tracks")
        order = []
        for position, track in enumerate(tracks, 1):
            require(isinstance(track, dict), f"{day}: track must be an object")
            require(type(track.get("position")) is int and track["position"] == position, f"{day}: wrong position")
            cid = track.get("canonical_id")
            require(isinstance(cid, str) and cid == str(track.get("artist")) + "::" + str(track.get("title")),
                    f"{day}: canonical ID mismatch")
            require(cid in state, f"{day}: current track missing from permanent history")
            am = track.get("apple_music")
            require(isinstance(am, dict), f"{day}: missing apple_music object")
            sid = am.get("song_id")
            require(isinstance(sid, str) and re.fullmatch(r"[0-9]+", sid) is not None, f"{day}: invalid song ID")
            match = v.MUSIC_SONG_RE.fullmatch(str(am.get("url", "")))
            require(match is not None and match.group(1) == sid and am.get("storefront") == "cn",
                    f"{day}: wrong direct URL/song ID/storefront")
            require(cid not in cids and sid not in sids, f"{day}: duplicate music resource")
            cids.add(cid); sids.add(sid); order.append(sid)
        note = root / "Music/Daily" / (day + ".md")
        require(note.is_file(), f"{day}: missing music note")
        require(v.MUSIC_SONG_RE.findall(note.read_text(encoding="utf-8")) == order, f"{day}: note/manifest ID mismatch")
        dates.add(day)
    note_dates = {p.stem for p in (root / "Music/Daily").glob("????-??-??.md")}
    require(note_dates == dates, "orphan music note or missing manifest")
    if base:
        check_append_only(root, base)
    journal = j.audit(root, base)
    return {"status": "passed_local_integrity", "history": histories, "journal": journal,
            "music": {"manifests": len(manifests), "current_tracks": len(cids), "state_entries": len(state),
                      "retired_entries_retained": len(set(state) - cids)},
            "append_only": "passed_against_base" if base else "not_checked_without_base_ref",
            "base_ref": base, "legacy_duplicate_groups": legacy,
            "cross_repository": "not_checked_requires_two_authorized_checkouts",
            "not_certified": ["live sources", "semantic quality", "candidate pools", "local Obsidian sync", "task delivery"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", help="Full ancestor commit SHA; history bytes/values must be preserved")
    args = parser.parse_args()
    try:
        policy = v.strict_json(v.POLICY.read_text(encoding="utf-8"))
        result = audit(v.ROOT, v.iso_day(policy["strict_from"]), args.base_ref)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
