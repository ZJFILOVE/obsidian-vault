#!/usr/bin/env python3
"""Validate recorded visual review of both current PDFs; never generate PASS."""
import json
import os
import re
import subprocess
from pathlib import Path


def page_count(path):
    result = subprocess.run(["pdfinfo", str(path)], capture_output=True,
                            text=True, env=dict(os.environ, LC_ALL="C"))
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, re.M)
    if result.returncode or not match:
        raise ValueError("无法读取 PDF 页数: " + str(path))
    return int(match[1])


def validate(project, digest, pdf_sha):
    path = Path(project) / ".pd/layout-review.json"
    try:
        review = json.loads(path.read_text())
        if not isinstance(review, dict):
            raise ValueError("review must be an object")
    except (OSError, ValueError):
        return ["缺少有效 .pd/layout-review.json；须实际审读当前两版每一页"]
    errors = []
    if (review.get("schema_version") != 1 or review.get("status") != "pass"
            or not review.get("reviewer") or review.get("issues") != []):
        errors.append("排版审读未通过或仍有未解决问题")
    if review.get("input_digest") != digest or review.get("pdf_sha256") != pdf_sha:
        errors.append("排版审读未绑定当前输入或 student.pdf / teacher.pdf；须复验")
    for target in ("student", "teacher"):
        try:
            count = page_count(Path(project) / (target + ".pdf"))
            rows = review.get("pages", {}).get(target, [])
            if (not isinstance(rows, list)
                    or len(rows) != count
                    or any(not isinstance(r, dict) or not str(r.get("notes", "")).strip()
                           for r in rows)
                    or sorted(r.get("page", 0) for r in rows) != list(range(1, count + 1))):
                errors.append(target + " 排版审读必须逐页覆盖，记录图文边界、栏间距和图题检查")
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append("排版审读无法验证 " + target + ": " + str(exc))
    return errors
