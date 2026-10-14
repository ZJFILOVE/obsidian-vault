#!/usr/bin/env python3
"""Read-only preflight regressions; only synthetic temporary projects are used."""
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import deliver
import test_runtime as fixtures


def snapshot(root):
    """Detect new directories, content changes and even identical file rewrites."""
    return {str(path.relative_to(root)):
            ("file", path.read_bytes(), path.stat().st_mtime_ns)
            if path.is_file() else ("dir",)
            for path in root.rglob("*")}


@unittest.skipUnless(shutil.which("pdfinfo"), "needs poppler pdfinfo")
class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with contextlib.redirect_stdout(io.StringIO()):
            fixtures.make_project(self.temp.name)
            fixtures.seed_all(self.temp.name)

    def invoke(self, *flags):
        before = snapshot(self.root)
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["deliver.py", str(self.root), *flags]), \
                mock.patch.object(deliver, "run_check", side_effect=AssertionError("must not build")), \
                mock.patch.object(deliver, "atomic_release", side_effect=AssertionError("must not publish")), \
                contextlib.redirect_stdout(output):
            result = deliver.main()
        self.assertEqual(before, snapshot(self.root), "verification mutated the project")
        return result, output.getvalue()

    def remove_acceptance(self):
        shutil.rmtree(self.root / ".pd/acceptance")

    def test_ready_technical_evidence_without_acceptance(self):
        self.remove_acceptance()
        code, output = self.invoke("--preflight")
        self.assertEqual(code, 0, output)
        self.assertIn("教学验收待完成", output)
        self.assertFalse((self.root / "release").exists())
        self.assertFalse((self.root / ".pd/acceptance").exists())

    def test_check_only_still_requires_acceptance(self):
        self.remove_acceptance()
        code, output = self.invoke("--check-only")
        self.assertEqual(code, 1, output)

    def test_missing_reports_does_not_create_report_directory(self):
        shutil.rmtree(self.root / ".pd/reports")
        code, output = self.invoke("--preflight", "--skip-checks")
        self.assertEqual(code, 1, output)
        self.assertFalse((self.root / ".pd/reports").exists())

    def test_current_acceptance_never_publishes_or_overwrites_release(self):
        release = self.root / "release"
        release.mkdir()
        (release / "student.pdf").write_bytes(b"previous approved release")
        (release / "manifest.json").write_text('{"previous": true}')
        code, output = self.invoke("--preflight", "--skip-checks")
        self.assertEqual(code, 0, output)

    def test_stale_config_is_not_regenerated_in_project(self):
        (self.root / "config.tex").write_text("stale config")
        code, output = self.invoke("--preflight")
        self.assertNotEqual(code, 0, output)
        self.assertIn("配置产物过期", output)

    def test_missing_technical_evidence_blocks(self):
        for relative in (".pd/reports/build.json", ".pd/layout-review.json", ".pd/materials.json"):
            with self.subTest(relative=relative):
                path = self.root / relative
                data = path.read_bytes()
                path.unlink()
                code, output = self.invoke("--preflight")
                self.assertEqual(code, 1, output)
                path.write_bytes(data)

    def test_compare_review_requires_current_disposition(self):
        fixtures.seed_reports(str(self.root), compare_status="review")
        code, output = self.invoke("--preflight")
        self.assertEqual(code, 1, output)
        self.assertIn("疑似答案项", output)

    def test_graphic_without_provenance_blocks(self):
        section = self.root / "sec2.tex"
        section.write_text(section.read_text() + "\n\\includegraphics{pic1.png}\n")
        fixtures.seed_all(str(self.root))
        code, output = self.invoke("--preflight")
        self.assertEqual(code, 1, output)
        self.assertTrue("图片" in output or "figure" in output, output)

    def test_changed_input_is_not_reused(self):
        section = self.root / "sec2.tex"
        section.write_text(section.read_text() + "\nchanged input\n")
        code, output = self.invoke("--preflight")
        self.assertEqual(code, 1, output)
        self.assertIn("摘要", output)

    def test_cli_preflight_does_not_require_explicit_skip_checks(self):
        self.remove_acceptance()
        before = snapshot(self.root)
        result = subprocess.run([sys.executable, "-B", deliver.__file__, str(self.root), "--preflight"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, snapshot(self.root))

    def test_input_mutation_during_verification_is_detected(self):
        original = deliver.evidence.collect_inputs
        calls = 0

        def collect(project):
            nonlocal calls
            calls += 1
            result = original(project)
            if calls == 4:
                # Simulate another process changing inputs after checks. No disk write.
                result = dict(result, missing=result["missing"] + ["concurrent-change.tex"])
            return result

        with mock.patch.object(deliver.evidence, "collect_inputs", side_effect=collect):
            code, output = self.invoke("--preflight")
        self.assertEqual(code, 1, output)
        self.assertIn("已变化", output)


if __name__ == "__main__":
    unittest.main()
