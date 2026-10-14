#!/usr/bin/env python3
"""Run only stale courseware technical checks. Never review or publish a book.

Usage: python technical.py PROJECT [--skill PATH] [--force]
Exit 0: technical reports and student review pack are current (not acceptance).
Exit 1: check failed. Exit 2: input, dependency, execution or lock error.
The first invocation conservatively runs all stages; subsequent invocations
validate cached reports through the skill's own deliver.verify_report function.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

_BUNDLED_SKILL = Path(__file__).resolve().parent.parent
DEFAULT_SKILL = (_BUNDLED_SKILL if (_BUNDLED_SKILL / "SKILL.md").is_file()
                 else Path.home() / ".agents/skills/problem-driven-courseware")
CACHE_VERSION = 1
CHECKS = (("check_numbering.py", "check_numbering.json"),
          ("check_dialogue.py", "check_dialogue.json"),
          ("build.py", "build.json"),
          ("compare_versions.py", "compare.json"))


class TechnicalError(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def sha(path):
    path = Path(path)
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def atomic_json(path, value):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def project_lock(project):
    pd = project / ".pd"
    pd.mkdir(parents=True, exist_ok=True)
    # Keep the lock inode: deleting it permits a second process to lock a new one.
    with (pd / "technical.lock").open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise TechnicalError("该工程已有技术检查进程；稍后重试。") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def load_skill(skill):
    scripts = skill / "scripts"
    required = [name for name, _ in CHECKS] + ["evidence.py", "deliver.py",
                "gen_config.py", "make_review_pack.py", "layout_review.py"]
    missing = [str(scripts / name) for name in required
               if not (scripts / name).is_file()]
    if missing:
        raise TechnicalError("缺少 skill 工具：" + ", ".join(missing))
    # deliver imports these siblings by their ordinary names. Refuse a silently
    # mixed toolchain if this module is embedded in an existing Python process.
    for name in ("evidence", "gen_config", "layout_review", "build"):
        loaded = sys.modules.get(name)
        if loaded and Path(loaded.__file__).resolve() != (scripts / (name + ".py")).resolve():
            raise TechnicalError("已有不同 skill 的 Python 模块；请单独运行本 CLI。")
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location("courseware_deliver", scripts / "deliver.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        raise TechnicalError("无法加载 skill 检查器：" + str(exc)) from exc
    if not callable(getattr(module, "verify_report", None)):
        raise TechnicalError("当前 skill 没有 deliver.verify_report，不能安全复用报告。")
    return module


def toolchain_hash(skill):
    paths = [Path(__file__).resolve()]
    for name in ("scripts", "templates", "references", "prompts"):
        folder = skill / name
        paths.extend(p for p in folder.rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts
                     and p.suffix not in (".pyc", ".pyo"))
    paths.append(skill / "SKILL.md")
    return digest({str(p): sha(p) for p in sorted(set(paths))})


def tool_version(path):
    # Read the declared version without executing another program's main.
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
                t.id == "TOOL_VERSION" for t in node.targets):
            return ast.literal_eval(node.value)
    raise TechnicalError("工具缺少 TOOL_VERSION：" + str(path))


def execute(command, log_path):
    """One subprocess with captured output; useful as a test seam."""
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError) as exc:
        raise TechnicalError("执行失败：" + str(exc)) from exc
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
    return result.returncode


class Runner:
    def __init__(self, project, skill, *, force=False):
        self.project = Path(project).resolve()
        self.skill = Path(skill).resolve()
        self.scripts = self.skill / "scripts"
        self.force = force
        self.deliver = load_skill(self.skill)
        self.evidence = self.deliver.evidence
        self.chain = toolchain_hash(self.skill)
        self.cache_path = self.project / ".pd/technical-cache.json"
        self.cache = read_json(self.cache_path)
        if self.cache.get("schema_version") != CACHE_VERSION:
            self.cache = {"schema_version": CACHE_VERSION, "stages": {}}
        if not isinstance(self.cache.get("stages"), dict):
            self.cache["stages"] = {}
        self.steps = []

    def save(self):
        atomic_json(self.cache_path, self.cache)

    def snapshot(self):
        manifest = self.evidence.collect_inputs(str(self.project))
        if manifest.get("missing") or manifest.get("unresolved"):
            raise TechnicalError("输入清单不完整：missing=%s unresolved=%s" %
                                 (manifest.get("missing"), manifest.get("unresolved")))
        return self.evidence.content_digest(manifest)

    def pdf_hashes(self):
        return {n: self.evidence.sha256_file(str(self.project / (n + ".pdf")))
                for n in ("student", "teacher")}

    def current_key(self, input_key):
        return digest({"toolchain": self.chain, "input": input_key})

    def cached(self, stage, key, files):
        record = self.cache["stages"].get(stage)
        hashes = {str(p.relative_to(self.project)): sha(p) for p in files}
        return (not self.force and isinstance(record, dict)
                and record.get("key") == key and all(hashes.values())
                and record.get("outputs") == hashes)

    def remember(self, stage, key, files):
        self.cache["stages"][stage] = {
            "key": key,
            "outputs": {str(p.relative_to(self.project)): sha(p) for p in files}}
        self.save()

    def invalidate(self, stage):
        self.cache["stages"].pop(stage, None)
        self.save()

    def emit(self, stage, action, since):
        seconds = time.monotonic() - since
        self.steps.append({"stage": stage, "action": action, "seconds": seconds})
        print("[technical] %s %s %.2fs" % (action, stage, seconds), flush=True)

    def call(self, script, arguments):
        log = self.project / ".pd/technical-logs" / (Path(script).stem + ".log")
        code = execute([sys.executable, str(self.scripts / script), *arguments], log)
        return code, log

    def configuration(self):
        started = time.monotonic()
        stage = "gen_config.py"
        key = self.current_key({"config.yaml": sha(self.project / "config.yaml")})
        files = [self.project / n for n in ("config.tex", "config-class.tex")]
        if self.cached(stage, key, files):
            self.emit(stage, "复用", started)
            return
        self.invalidate(stage)
        code, log = self.call(stage, ["--project", str(self.project)])
        if code != 0 or not all(sha(p) for p in files):
            raise TechnicalError("配置生成失败；详情：" + str(log))
        if key != self.current_key({"config.yaml": sha(self.project / "config.yaml")}):
            raise TechnicalError("配置生成期间 config.yaml 改变，请重跑。", 1)
        self.remember(stage, key, files)
        self.emit(stage, "运行", started)

    def report_blockers(self, script, fname, expected_digest):
        path = self.project / ".pd/reports" / fname
        report = read_json(path)
        blockers = []
        try:
            self.deliver.verify_report(script, fname, report or None,
                str(self.project), expected_digest, self.pdf_hashes(), blockers)
        except Exception as exc:
            blockers.append("报告验证异常：" + str(exc))
        if report.get("tool_version") != tool_version(self.scripts / script):
            blockers.append("报告工具版本不匹配")
        allowed = ("pass", "review") if script == "compare_versions.py" else ("pass",)
        if report.get("status") not in allowed:
            blockers.append("检查状态为 " + str(report.get("status")))
        if script in ("build.py", "compare_versions.py") and not all(self.pdf_hashes().values()):
            blockers.append("缺少双版 PDF")
        return blockers

    def check(self, script, fname, input_digest):
        started = time.monotonic()
        # The shared TeX digest does not include this Markdown ledger, although
        # check_dialogue reads it. Track it separately without redefining the
        # authoritative content_digest used by the reports and acceptance.
        side_inputs = ({"coverage-map.md": sha(self.project / "coverage-map.md")}
                       if script == "check_dialogue.py" else {})
        key = self.current_key({"content_digest": input_digest, "side_inputs": side_inputs})
        report = self.project / ".pd/reports" / fname
        if self.cached(script, key, [report]) and not self.report_blockers(script, fname, input_digest):
            self.emit(script, "复用", started)
            return
        self.invalidate(script)
        report.parent.mkdir(parents=True, exist_ok=True)
        # Remove the old PASS before invoking the tool, as deliver itself does.
        report.unlink(missing_ok=True)
        code, log = self.call(script, [str(self.project), "--json", str(report)])
        value = read_json(report)
        review_exit = script == "compare_versions.py" and code == 1 and value.get("status") == "review"
        if code != 0 and not review_exit:
            raise TechnicalError("%s 未通过（退出码 %s）；详情：%s" % (script, code, log),
                                 1 if code == 1 else 2)
        problems = self.report_blockers(script, fname, input_digest)
        if self.snapshot() != input_digest:
            problems.append("检查期间输入改变")
        if side_inputs and side_inputs["coverage-map.md"] != sha(self.project / "coverage-map.md"):
            problems.append("检查期间 coverage-map.md 改变")
        if problems:
            raise TechnicalError("%s 证据无效：%s；详情：%s" %
                                 (script, "；".join(problems[:3]), log), 1)
        self.remember(script, key, [report])
        self.emit(script, "运行", started)

    def review_pack_valid(self, input_digest):
        manifest = read_json(self.project / ".pd/review/manifest.json")
        return (manifest.get("input_digest") == input_digest
                and manifest.get("student_pdf_sha256") == self.pdf_hashes()["student"]
                and manifest.get("tool") == "make_review_pack.py"
                and manifest.get("tool_version") == tool_version(self.scripts / "make_review_pack.py")
                and manifest.get("schema_version") == self.evidence.SCHEMA_VERSION
                and manifest.get("status") == "pass")

    def review_pack(self, input_digest):
        started = time.monotonic()
        stage = "make_review_pack.py"
        key = self.current_key({"input_digest": input_digest, "student_pdf": self.pdf_hashes()["student"]})
        files = [self.project / ".pd/review" / n for n in ("manifest.json", "student-pages.txt")]
        if self.cached(stage, key, files) and self.review_pack_valid(input_digest):
            self.emit(stage, "复用", started)
            return
        self.invalidate(stage)
        # A failed generator must not leave an old manifest looking current.
        files[0].unlink(missing_ok=True)
        code, log = self.call(stage, [str(self.project)])
        if code != 0 or not all(sha(p) for p in files) or not self.review_pack_valid(input_digest):
            raise TechnicalError("学生审读包生成失败；详情：" + str(log))
        self.remember(stage, key, files)
        self.emit(stage, "运行", started)

    def run(self):
        self.configuration()
        input_digest = self.snapshot()
        coverage_digest = sha(self.project / "coverage-map.md")
        for script, fname in CHECKS:
            self.check(script, fname, input_digest)
        self.review_pack(input_digest)
        if (self.snapshot() != input_digest or toolchain_hash(self.skill) != self.chain
                or sha(self.project / "coverage-map.md") != coverage_digest):
            raise TechnicalError("执行期间源文件或 skill 改变；本轮不可作为当前技术结果。", 1)
        # Catch a concurrent editor or compiler changing evidence after an earlier stage.
        for script, fname in CHECKS:
            problems = self.report_blockers(script, fname, input_digest)
            if problems:
                raise TechnicalError("结束复核失败：%s：%s" % (script, "；".join(problems[:3])), 1)
        compare = read_json(self.project / ".pd/reports/compare.json")
        suffix = "；compare 疑似项仍待逐项复核" if compare.get("status") == "review" else ""
        print("[technical] 技术报告与学生审读包已就绪%s。图片、版面、教学验收和发布仍须独立完成。" % suffix)
        return self.steps


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    parser.add_argument("--force", action="store_true", help="重跑技术阶段，仍保留全部验收门禁")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if not project.is_dir() or not (project / "main.tex").is_file():
        print("[technical] 需要含 main.tex 的现有 self 工程：" + str(project), file=sys.stderr)
        return 2
    if "source" in project.parts:
        print("[technical] source/ 原始输入只读，不能作为构建目录。", file=sys.stderr)
        return 2
    try:
        with project_lock(project):
            Runner(project, args.skill, force=args.force).run()
    except (TechnicalError, OSError, ValueError) as exc:
        print("[technical] " + str(exc), file=sys.stderr)
        return getattr(exc, "code", 2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
