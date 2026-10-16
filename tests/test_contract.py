"""Offline regression tests for the bounded evidence contract."""

import hashlib
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from resqmonitor._support import check, json_object, read_csv
from resqmonitor.__main__ import main
from resqmonitor.demo import SCENARIOS, demo
from resqmonitor.engine import analyze, configuration
from resqmonitor.report import as_html, as_json, as_text


class ContractTests(unittest.TestCase):
    def test_all_synthetic_scenarios(self):
        expected = {"healthy": "ok", "degraded": "attention", "unknown": "unknown", "small_sample": "unknown"}
        self.assertEqual(set(SCENARIOS), set(expected))
        for scenario, status in expected.items():
            with self.subTest(scenario=scenario):
                report = demo(scenario)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["schema_version"], "2.0")
                self.assertTrue(report["synthetic"])
                self.assertEqual(report["evaluated_at"], "2026-10-13T12:00:00+00:00")
                self.assertEqual(report["decision"]["scope"], "supplied_observations")
                self.assertIs(report["decision"]["action_authorized"], False)
                self.assertTrue(set(report["decision"]["required_checks"]) <= set(report["checks"]))
                for item in report["checks"].values():
                    self.assertEqual(len(item["reason_codes"]), len(set(item["reason_codes"])))
                    if item["status"] != "unknown":
                        self.assertEqual(item["evidence_status"], "sufficient")
                        self.assertEqual(item["status"], item["threshold_status"])
                self.assertEqual(json.loads(as_json(report)), report)
                self.assertIn("Decision:", as_text(report))
                self.assertIn("Evidence:", as_html(report))

    def test_small_sample_is_measured_but_not_accepted(self):
        report = demo("small_sample")
        item = report["checks"]["accuracy"]
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["threshold_status"], "ok")
        self.assertEqual(item["evidence_status"], "insufficient")
        self.assertEqual(item["status"], "unknown")
        self.assertIn("BELOW_MIN_SAMPLE", item["reason_codes"])
        self.assertEqual(report["decision"]["outcome"], "undetermined")

    def test_no_target_is_not_a_pass(self):
        item = check("Measured", 100, "%", {}, "Observed")
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["evidence_status"], "sufficient")
        self.assertEqual(item["status"], "unknown")
        self.assertIn("THRESHOLD_NOT_CONFIGURED", item["reason_codes"])

    def test_unrounded_comparison_and_evidence_precedence(self):
        item = check("Boundary", 94.99999999, "%", {}, "Observed", minimum=95)
        self.assertEqual(item["value"], 95)
        self.assertEqual(item["threshold_status"], "attention")
        self.assertEqual(item["status"], "attention")
        item = check("Invalid", None, "%", {}, "Observed", minimum=95,
                     evidence_issues=["NO_OBSERVATIONS", "INVALID_RECORD", "INVALID_RECORD"])
        self.assertEqual(item["evidence_status"], "invalid")
        self.assertEqual(item["status"], "unknown")
        self.assertEqual(item["reason_codes"], ["NO_OBSERVATIONS", "INVALID_RECORD"])

    def test_policy_fingerprints_and_snapshot(self):
        report = demo("healthy")
        policy = json.dumps(report["policy"], sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        self.assertEqual(report["provenance"]["policy_sha256"], hashlib.sha256(policy.encode()).hexdigest())
        self.assertEqual(report["provenance"]["source_verification"], "not_performed")
        self.assertEqual(report["provenance"]["generalization"], "not_assessed")
        cfg = {"evidence_context": {"purpose": "Example"}}
        effective = configuration(cfg)
        cfg["evidence_context"]["purpose"] = "Changed"
        self.assertEqual(effective["evidence_context"]["purpose"], "Example")
        self.assertIsNone(effective["evidence_context"]["population"])
        for context in ({"unknown": "x"}, {"purpose": ""}, {"purpose": 1}, {"purpose": "x" * 2001}):
            with self.subTest(context=str(context)[:40]), self.assertRaises(ValueError):
                configuration({"evidence_context": context})

    def test_input_rejection(self):
        for text in ('id,id\na,b\n', 'id,value\na\n', 'id\n"unclosed', ''):
            with self.subTest(text=text), self.assertRaises(ValueError):
                read_csv(text)
        for text in ('{"x": NaN}', '{"x": 1, "x": 2}', '[]'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                json_object(text)
        with self.assertRaises(ValueError):
            configuration({"undeclared_rule": 1})

    def test_html_escapes_caller_strings(self):
        report = demo("healthy")
        report["dataset"] = '<script>alert("data")</script>'
        report["policy"]["evidence_context"]["purpose"] = '<img src=x onerror=alert(1)>'
        page = as_html(report)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img src=x", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&lt;img", page)

    def test_cli_exit_statuses_and_errors(self):
        for scenario, required_exit in (("healthy", 0), ("degraded", 1), ("unknown", 1), ("small_sample", 1)):
            with self.subTest(scenario=scenario):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["demo", "--scenario", scenario, "--format", "json", "--require-ok"])
                self.assertEqual(code, required_exit)
                self.assertEqual(json.loads(stdout.getvalue())["scenario"], scenario)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["demo", "--scenario", "unknown", "--format", "json"]), 0)
        with TemporaryDirectory() as directory:
            missing = str(Path(directory) / "absent.csv")
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["check", missing, "--format", "json"])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "error")
            self.assertEqual(stderr.getvalue(), "")
            output = Path(directory) / "nested/report.html"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["demo", "--output", str(output), "--format", "html"]), 0)
            self.assertIn("<!doctype html>", output.read_text())
