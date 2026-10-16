"""Narrow regressions accepted in the second pre-edit stress review."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from resqmonitor._support import check, json_object
from resqmonitor.__main__ import main
from resqmonitor.demo import demo
from resqmonitor.report import as_text, as_html

class ReviewRegressionTests(unittest.TestCase):
    def test_excessive_config_nesting_is_an_input_error(self):
        text = '{"x":' + '[' * 100000 + '0' + ']' * 100000 + '}'
        with self.assertRaisesRegex(ValueError, 'nesting'):
            json_object(text)
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text(text)
            csv = Path(directory) / 'input.csv'
            csv.write_text('record_id,predicted_label,actual_label\na,x,x\n')
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(['check', str(csv), '--config', str(path), '--format', 'json'])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stdout.getvalue())['error']['code'], 'INVALID_INPUT')
            self.assertIn('nesting', json.loads(stdout.getvalue())['error']['message'])
            self.assertEqual(stderr.getvalue(), '')

    def test_human_reports_preserve_serialized_check_precision(self):
        report = demo('healthy')
        report['checks']['precision_example'] = check('Boundary example', 94.996, '%', {}, 'Observed', minimum=95)
        for render in (as_text, as_html):
            self.assertIn('94.996 %', render(report))
        self.assertEqual(report['checks']['precision_example']['status'], 'attention')

    def test_missing_cost_is_distinct_from_measured_zero(self):
        from resqmonitor.engine import analyze
        for text in ('record_id,predicted_label,actual_label\na,x,x\n',
                     'record_id,predicted_label,actual_label,cost\na,x,x,\n',
                     'record_id,predicted_label,actual_label,cost\n'):
            with self.subTest(text=text):
                item = analyze(text, {'min_evaluated_rows': 1})['checks']['cost_per_correct']
                self.assertIsNone(item['evidence']['known_total_cost'])
                self.assertIsNone(item['value'])
                self.assertEqual(item['evidence_status'], 'missing')
                self.assertIn('NO_OBSERVATIONS', item['reason_codes'])
        item = analyze('record_id,predicted_label,actual_label,cost\na,x,x,0\n',
                       {'min_evaluated_rows': 1, 'max_cost_per_correct': .05})['checks']['cost_per_correct']
        self.assertEqual(item['evidence']['known_total_cost'], 0)
        self.assertEqual(item['value'], 0)
        self.assertEqual(item['status'], 'ok')

    def test_small_cost_and_boundary_remain_visible(self):
        from resqmonitor.engine import analyze
        for render in (as_text, as_html):
            self.assertIn('0.021053 EUR', render(demo('healthy')))
            report = analyze('record_id,predicted_label,actual_label,cost\na,x,x,.0504\n',
                             {'min_evaluated_rows': 1, 'max_cost_per_correct': .05})
            self.assertIn('0.0504 EUR', render(report))
            self.assertEqual(report['checks']['cost_per_correct']['status'], 'attention')
