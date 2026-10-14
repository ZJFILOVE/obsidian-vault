#!/usr/bin/env python3
"""Regression tests for vertical overflow, stale evidence and tall content.
Only synthetic temporary projects are written.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build
import deliver
import layout_review
import test_runtime as fixtures
import test_templates


class QualityGates(unittest.TestCase):
    def test_vertical_overflow_blocks(self):
        args = SimpleNamespace(allow_mdframed_breaks=False, max_overfull_pt=2,
                               max_overfull_vbox_pt=.5, max_underfull_student=None,
                               max_underfull_teacher=10, strict=False)
        text = r'Overfull \vbox (517.41437pt too high) has occurred while \output is active'
        errors, _ = build.scan_log(text, 'student', args)
        self.assertTrue(any('vbox' in e for e in errors))
        errors, _ = build.scan_log(r'Underfull \vbox (badness 10000)', 'student', args)
        self.assertEqual(errors, [])

    def test_legacy_or_loosened_build_not_deliverable(self):
        with tempfile.TemporaryDirectory() as d:
            fixtures.make_project(d)
            digest, pdfs, _ = fixtures.seed_reports(d)
            rep = json.loads((Path(d) / '.pd/reports/build.json').read_text())
            rep['evidence']['layout_policy']['max_overfull_vbox_pt'] = 600
            errors = []
            deliver.verify_report('build.py', 'build.json', rep, d, digest, pdfs, errors)
            self.assertTrue(any('阈值' in e for e in errors))
            rep['evidence'].pop('layout_policy')
            errors = []
            deliver.verify_report('build.py', 'build.json', rep, d, digest, pdfs, errors)
            self.assertTrue(errors)

    def test_declared_pass_cannot_hide_vertical_overflow(self):
        with tempfile.TemporaryDirectory() as d:
            fixtures.make_project(d)
            digest, pdfs, _ = fixtures.seed_reports(d)
            log = Path(d) / 'student.log'
            log.write_text(r'Overfull \vbox (517.4pt too high)')
            rep = json.loads((Path(d) / '.pd/reports/build.json').read_text())
            rep['evidence']['log_sha256']['student'] = fixtures.sha(log)
            errors = []
            deliver.verify_report('build.py', 'build.json', rep, d, digest, pdfs, errors)
            self.assertTrue(any('vbox' in e for e in errors))

    def test_missing_or_stale_page_review_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            fixtures.make_project(d)
            fixtures.seed_all(d)
            path = Path(d) / '.pd/layout-review.json'
            review = json.loads(path.read_text())
            self.assertEqual(layout_review.validate(d, review['input_digest'], review['pdf_sha256']), [])
            review['pages']['student'] = []
            path.write_text(json.dumps(review))
            self.assertTrue(layout_review.validate(d, review['input_digest'], review['pdf_sha256']))
            self.assertTrue(layout_review.validate(d, 'changed', review['pdf_sha256']))

    def test_check_only_keeps_project_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            fixtures.make_project(d)
            fixtures.seed_all(d)
            root = Path(d)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = fixtures.run_cli('deliver.py', d, '--check-only')
            self.assertEqual(result.returncode, 0, result.stdout)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    @unittest.skipUnless(shutil.which('xelatex') and shutil.which('pdftotext'), 'needs TeX/poppler')
    def test_tall_image_and_long_box_real_compile(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Generate a valid tall one-page PDF by updating MediaBox and xref offsets.
            # Reuse fixture builder's dimensions without changing text content.
            data = fixtures.minimal_pdf()
            # Same byte length preserves all xref offsets.
            (root / 'tall.pdf').write_bytes(data.replace(b'595 842', b'100 999'))
            body = (r'\section*{I 分页回归}' + '\n' + r'\begin{microknowledge}' + '\n'
                    + ('这是应当允许跨栏跨页的解释段落，文字不能越过页脚。\\par\n' * 100)
                    + r'\end{microknowledge}' + '\n'
                    + r'\pdEndColumns\clearpage\pdBeginColumns' + '\n'
                    + r'\setbox0=\hbox{\includegraphics[width=.72\linewidth]{tall.pdf}}' + '\n'
                    + r'\typeout{TESTIMAGEHEIGHT=\the\ht0}' + '\n'
                    + r'\typeout{TESTTEXTHEIGHT=\the\textheight}' + '\n'
                    + r'\noindent\box0\par' + '\n' + test_templates.SEC_OK
                    + '\nENDOFCONTENT\n')
            test_templates.make_project(d, ['sec1.tex'], {'sec1.tex': body})
            result = test_templates.run('build.py', d, '--max-underfull-teacher', '200')
            self.assertEqual(result.returncode, 0, result.stdout[-7000:] + result.stderr)
            for target in ('student', 'teacher'):
                log = (root / (target + '.log')).read_text()
                h = float(re.search(r'TESTIMAGEHEIGHT=([\d.]+)pt', log)[1])
                page_h = float(re.search(r'TESTTEXTHEIGHT=([\d.]+)pt', log)[1])
                self.assertLessEqual(h, .65 * page_h + .1)
                self.assertFalse(build.RE_OVERFULL_VBOX.search(log))
                text = subprocess.check_output(['pdftotext', str(root / (target + '.pdf')), '-']).decode()
                self.assertIn('ENDOFCONTENT', text)
                self.assertEqual(text.count('这是应当'), 100)
                self.assertGreater(layout_review.page_count(root / (target + '.pdf')), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
