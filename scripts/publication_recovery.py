#!/usr/bin/env python3
"""Read-only write/retry planner. It neither writes GitHub nor certifies content QA."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from validate_daily_recommendations import iso_day, strict_json


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def digest(plan: dict) -> str:
    return hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha(value: object, optional: bool = False) -> None:
    require((optional and value is None) or
            (isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None), "invalid blob SHA")


def validate(plan: dict) -> None:
    require(isinstance(plan, dict) and plan.get("schema_version") == 1, "invalid plan schema")
    project = plan.get("project")
    require(project in ("music", "english", "news-youtube-reddit"), "unsupported project")
    day = iso_day(plan.get("date"))
    require(plan.get("operation_id") == f"{project}:{day}", "operation ID must be project:business-date")
    exposed = plan.get("exposed_resource_ids")
    require(isinstance(exposed, list) and bool(exposed) and all(isinstance(x, str) and x.strip() for x in exposed),
            "frozen exposure list required")
    require(len(exposed) == len(set(exposed)), "duplicate frozen exposure")
    targets = plan.get("targets")
    require(isinstance(targets, list) and bool(targets), "target files required")
    seen = set()
    for target in targets:
        require(isinstance(target, dict), "target must be an object")
        repo, path = target.get("repository"), target.get("path")
        require(repo in ("ZJFILOVE/music-daily", "ZJFILOVE/obsidian-vault"), "unapproved repository")
        require(isinstance(path, str) and bool(path) and not any(ord(c) < 32 for c in path), "invalid target path")
        require(not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts and "\\" not in path
                and PurePosixPath(path).as_posix() == path, "non-canonical or unsafe target path")
        require((repo, path) not in seen, "duplicate target")
        seen.add((repo, path))
        sha(target.get("base_sha"), optional=True); sha(target.get("target_sha"))
        require(type(target.get("stage")) is int and target["stage"] >= 1, "invalid stage")


def inspect(plan: dict, observations: dict, expected_digest: str) -> dict:
    validate(plan)
    require(digest(plan) == expected_digest, "prepared plan changed; do not reselect or overwrite its baseline")
    require(isinstance(observations, dict), "observations must be a mapping")
    decisions = []
    for target in plan["targets"]:
        key = target["repository"] + ":" + target["path"]
        observed = observations.get(key)
        action, reason = "unverified", "fresh readback missing or failed"
        if isinstance(observed, dict):
            known = observed.get("status") == "ok" or (observed.get("status") == "missing" and observed.get("confirmed") is True)
            if known:
                current = observed.get("sha") if observed["status"] == "ok" else None
                sha(current, optional=observed["status"] == "missing")
                if current == target["target_sha"]:
                    action, reason = "no_op", "target already present, including a lost successful response"
                elif current == target.get("base_sha"):
                    action = "create" if current is None else "update"
                    reason = "observed baseline matches frozen plan"
                else:
                    action, reason = "conflict", "unexpected change; refetch and reconcile, never force"
        decisions.append({"repository": target["repository"], "path": target["path"], "stage": target["stage"],
                          "action": action, "reason": reason, "expected_sha": target.get("base_sha"),
                          "target_sha": target["target_sha"]})
    blocked = any(d["action"] in ("conflict", "unverified") for d in decisions)
    pending = [d["stage"] for d in decisions if d["action"] in ("create", "update")]
    return {"operation_id": plan["operation_id"], "plan_sha256": expected_digest,
            "status": "blocked" if blocked else ("ready_to_resume" if pending else "artifacts_match"),
            "next_stage": min(pending) if pending and not blocked else None,
            "decisions": decisions, "content_qa": "not_evaluated", "github_writes_performed": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--expected-digest", help="Digest retained from the original PREPARED record, not recomputed on retry")
    args = parser.parse_args()
    try:
        plan = strict_json(args.plan.read_text(encoding="utf-8")); validate(plan)
        if args.observations is None:
            print(json.dumps({"operation_id": plan["operation_id"], "plan_sha256": digest(plan), "status": "plan_valid_not_published"}))
            return 0
        require(bool(args.expected_digest), "retry requires the original --expected-digest")
        result = inspect(plan, strict_json(args.observations.read_text(encoding="utf-8")), args.expected_digest)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["status"] == "blocked" else 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
