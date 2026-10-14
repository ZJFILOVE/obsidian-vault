#!/usr/bin/env python3
"""Incremental-cache regressions using temporary projects and real validators.

No models, real books, TeX builds or acceptance records are changed. External
check execution is mocked; collect_inputs and deliver.verify_report are real.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("technical.py")
spec = importlib.util.spec_from_file_location("technical", MODULE_PATH)
technical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(technical)


class IncrementalChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = technical.DEFAULT_SKILL.resolve()
        cls.deliver = technical.load_skill(cls.skill)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="technical-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "self"
        self.project.mkdir()
        for name, text in {
                "config.yaml": "main_title: 学案\ndialogue_enabled: false\n",
                "main.tex": "\\input{sec1.tex}\n",
                "student.tex": "\\input{main.tex}\n",
                "teacher.tex": "\\input{main.tex}\n",
                "sec1.tex": "% qid: q1\nQuestion.\n"}.items():
            (self.project / name).write_text(text, encoding="utf-8")
        self.calls = []
        self.fail_script = None
        self.compare_review = False
        self.fake_code = 1
        self.load_patch = patch.object(technical, "load_skill", return_value=self.deliver)
        self.load_patch.start()
        self.addCleanup(self.load_patch.stop)
        self.exec_patch = patch.object(technical, "execute", side_effect=self.execute)
        self.exec_patch.start()
        self.addCleanup(self.exec_patch.stop)
        self.text_patch = patch.object(self.deliver, "pdf_text_sha", side_effect=technical.sha)
        self.text_patch.start()
        self.addCleanup(self.text_patch.stop)
        self.which_patch = patch.object(self.deliver.shutil, "which", return_value="/usr/bin/pdftotext")
        self.which_patch.start()
        self.addCleanup(self.which_patch.stop)

    def execute(self, command, log):
        script = Path(command[1]).name
        self.calls.append(script)
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("mock external checker\n")
        if script == self.fail_script:
            return self.fake_code
        if script == "gen_config.py":
            return self.deliver.gen_config.generate(str(self.project))
        ev = self.deliver.evidence
        input_digest = ev.content_digest(ev.collect_inputs(str(self.project)))
        if script == "build.py":
            for target in ("student", "teacher"):
                (self.project / (target + ".pdf")).write_text(target + " " + input_digest)
                (self.project / (target + ".log")).write_text("Mock clean build log\n")
        pdfs = {t: technical.sha(self.project / (t + ".pdf")) for t in ("student", "teacher")}
        report = {"schema_version": ev.SCHEMA_VERSION, "tool": script,
                  "tool_version": technical.tool_version(self.skill / "scripts" / script),
                  "input_digest": input_digest, "pdf_sha256": None,
                  "status": "pass", "issues": [], "evidence": {}}
        if script in ("build.py", "compare_versions.py"):
            report["pdf_sha256"] = pdfs
            report["evidence"]["log_sha256"] = {
                t: technical.sha(self.project / (t + ".log")) for t in pdfs}
        if script == "build.py":
            report["evidence"]["layout_policy"] = {"version": 1, "max_overfull_pt": 2,
                "max_overfull_vbox_pt": .5, "allow_mdframed_breaks": False}
        if script == "compare_versions.py":
            report["evidence"]["pdf_text_sha256"] = pdfs
            if self.compare_review:
                report["status"] = "review"
        if script == "make_review_pack.py":
            out = self.project / ".pd/review"
            out.mkdir(parents=True, exist_ok=True)
            report["student_pdf_sha256"] = pdfs["student"]
            report["pdf_sha256"] = {"student": pdfs["student"]}
            (out / "student-pages.txt").write_text("===== 第 1 页 =====\nQuestion.\n")
            path = out / "manifest.json"
        else:
            path = Path(command[command.index("--json") + 1])
        path.write_text(json.dumps(report), encoding="utf-8")
        return 1 if script == "compare_versions.py" and self.compare_review else 0

    def run_pipeline(self, force=False):
        with contextlib.redirect_stdout(io.StringIO()):
            with technical.project_lock(self.project):
                return technical.Runner(self.project, self.skill, force=force).run()

    def test_first_run_then_no_subprocesses_on_unchanged_input(self):
        first = self.run_pipeline()
        self.assertEqual(len(first), 6)
        self.assertEqual(len(self.calls), 6)
        self.calls.clear()
        second = self.run_pipeline()
        self.assertEqual(self.calls, [])
        self.assertTrue(all(s["action"] == "复用" for s in second))

    def test_source_change_invalidates_checks_and_review_pack(self):
        self.run_pipeline()
        self.calls.clear()
        (self.project / "sec1.tex").write_text("Changed question.\n")
        self.run_pipeline()
        self.assertEqual(self.calls, [s for s, _ in technical.CHECKS] + ["make_review_pack.py"])

    def test_coverage_ledger_is_included_in_dialogue_cache(self):
        self.run_pipeline()
        self.calls.clear()
        (self.project / "coverage-map.md").write_text("Synthetic ledger fixture.\n")
        self.run_pipeline()
        self.assertEqual(self.calls, ["check_dialogue.py"])

    def test_pdf_and_log_tampering_require_new_build(self):
        for target in ("student.pdf", "teacher.log"):
            with self.subTest(target=target):
                self.run_pipeline()
                self.calls.clear()
                (self.project / target).write_text("Replaced externally")
                self.run_pipeline()
                self.assertIn("build.py", self.calls)

    def test_report_tampering_requires_exact_checker(self):
        self.run_pipeline()
        self.calls.clear()
        path = self.project / ".pd/reports/check_numbering.json"
        report = json.loads(path.read_text())
        report["schema_version"] = 1
        path.write_text(json.dumps(report))
        self.run_pipeline()
        self.assertEqual(self.calls, ["check_numbering.py"])

    def test_cache_cannot_override_real_validator(self):
        self.run_pipeline()
        path = self.project / ".pd/reports/build.json"
        report = json.loads(path.read_text())
        report["evidence"]["layout_policy"]["max_overfull_pt"] = 100
        path.write_text(json.dumps(report))
        cache_path = self.project / ".pd/technical-cache.json"
        cache = json.loads(cache_path.read_text())
        cache["stages"]["build.py"]["outputs"][".pd/reports/build.json"] = technical.sha(path)
        cache_path.write_text(json.dumps(cache))
        self.calls.clear()
        self.run_pipeline()
        self.assertIn("build.py", self.calls)

    def test_failed_execution_removes_old_pass_and_does_not_cache_failure(self):
        self.run_pipeline()
        self.fail_script = "check_numbering.py"
        self.calls.clear()
        with self.assertRaises(technical.TechnicalError):
            self.run_pipeline(force=True)
        self.assertFalse((self.project / ".pd/reports/check_numbering.json").exists())
        cache = json.loads((self.project / ".pd/technical-cache.json").read_text())
        self.assertNotIn("check_numbering.py", cache["stages"])
        self.assertEqual(self.calls, ["gen_config.py", "check_numbering.py"])

    def test_compare_review_is_preserved_without_acceptance_or_release(self):
        self.compare_review = True
        self.run_pipeline()
        self.assertEqual(json.loads((self.project / ".pd/reports/compare.json").read_text())["status"], "review")
        for relative in ("release", ".pd/acceptance", ".pd/materials.json", ".pd/layout-review.json"):
            self.assertFalse((self.project / relative).exists())
        self.calls.clear()
        self.run_pipeline()
        self.assertEqual(self.calls, [])

    def test_skill_change_forces_new_reports(self):
        self.run_pipeline()
        self.calls.clear()
        with patch.object(technical, "toolchain_hash", return_value="a new installed toolchain"):
            self.run_pipeline()
        self.assertEqual(len(self.calls), 6)

    def test_template_fingerprint_changes_with_contents_not_mtime(self):
        root = Path(self.temp.name) / "skill-fixture"
        (root / "templates").mkdir(parents=True)
        template = root / "templates/main.tex"
        template.write_text("first")
        before = technical.toolchain_hash(root)
        template.touch()
        self.assertEqual(before, technical.toolchain_hash(root))
        template.write_text("second")
        self.assertNotEqual(before, technical.toolchain_hash(root))

    def test_missing_input_blocks_before_any_checker(self):
        (self.project / "main.tex").write_text("\\input{missing.tex}\n")
        with self.assertRaisesRegex(technical.TechnicalError, "输入清单不完整"):
            self.run_pipeline()
        self.assertEqual(self.calls, ["gen_config.py"])

    def test_second_process_lock_is_rejected(self):
        with technical.project_lock(self.project):
            with self.assertRaisesRegex(technical.TechnicalError, "已有技术检查进程"):
                with technical.project_lock(self.project):
                    self.fail("Second lock must not enter")

    def test_review_text_mutation_regenerates_only_review_pack(self):
        self.run_pipeline()
        self.calls.clear()
        (self.project / ".pd/review/student-pages.txt").write_text("Outdated text")
        self.run_pipeline()
        self.assertEqual(self.calls, ["make_review_pack.py"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
