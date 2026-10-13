"""Synthetic boundary cases for classification-result evidence."""

import hashlib
import unittest

from resqmonitor.engine import analyze, configuration, wilson_interval

AT = "2026-10-13T12:00:00Z"
HEADER = "record_id,predicted_label,actual_label,confidence,cost,latency_ms,group\n"


def sample(count=40, correct=38):
    return HEADER + "".join(f"R{i},a,{'a' if i < correct else 'b'},0.95,1,100,g\n" for i in range(count))


class EvidenceTests(unittest.TestCase):
    def report(self, data=None, config=None, baseline=None):
        return analyze(sample() if data is None else data, config, baseline_csv=baseline, at=AT)

    def test_point_estimate_and_wilson_are_distinct_policies(self):
        point = self.report()
        lower = self.report(config={"accuracy_threshold_basis": "wilson_lower_bound"})
        self.assertEqual(point["checks"]["accuracy"]["value"], 95)
        self.assertEqual(point["checks"]["accuracy"]["status"], "ok")
        item = lower["checks"]["accuracy"]
        self.assertEqual(item["value"], 95)
        self.assertAlmostEqual(item["threshold"]["assessment_value"], 83.49613, places=4)
        self.assertEqual(item["status"], "attention")
        self.assertNotEqual(point["provenance"]["policy_sha256"], lower["provenance"]["policy_sha256"])

    def test_wilson_threshold_uses_unrounded_bound(self):
        bound = wilson_interval(38, 40)[0]
        equal = self.report(config={"accuracy_threshold_basis": "wilson_lower_bound", "min_accuracy_pct": bound})
        higher = self.report(config={"accuracy_threshold_basis": "wilson_lower_bound", "min_accuracy_pct": bound + 1e-9})
        self.assertEqual(equal["checks"]["accuracy"]["status"], "ok")
        self.assertEqual(higher["checks"]["accuracy"]["status"], "attention")
        self.assertIsNone(wilson_interval(0, 0))
        self.assertAlmostEqual(wilson_interval(0, 40)[0], 0)

    def test_minimum_boundary(self):
        self.assertEqual(self.report(sample(30, 30))["checks"]["accuracy"]["status"], "ok")
        item = self.report(sample(29, 29))["checks"]["accuracy"]
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["status"], "unknown")
        self.assertIn("BELOW_MIN_SAMPLE", item["reason_codes"])

    def test_high_conditional_accuracy_with_missing_outcomes_is_unknown(self):
        data = sample(40, 40) + "".join(f"P{i},a,,0.95,1,100,g\n" for i in range(10))
        report = self.report(data)
        item = report["checks"]["accuracy"]
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["status"], "unknown")
        self.assertEqual(item["evidence_status"], "insufficient")
        self.assertIn("LOW_OUTCOME_COVERAGE", item["reason_codes"])
        self.assertEqual(report["checks"]["outcome_coverage"]["value"], 80)
        self.assertEqual(report["checks"]["outcome_coverage"]["status"], "attention")
        self.assertEqual(report["status"], "attention")

    def test_all_duplicate_occurrences_are_invalid(self):
        report = self.report(sample() + "R0,a,a,0.95,1,100,g\n")
        self.assertEqual(report["summary"]["duplicate_id_rows"], 2)
        self.assertEqual(report["summary"]["evaluated_rows"], 39)
        self.assertEqual(report["checks"]["accuracy"]["evidence_status"], "invalid")
        self.assertEqual(report["checks"]["accuracy"]["status"], "unknown")
        self.assertEqual(report["status"], "attention")

    def test_cost_includes_incorrect_outputs(self):
        report = self.report(config={"max_cost_per_correct": 2})
        item = report["checks"]["cost_per_correct"]
        self.assertAlmostEqual(item["value"], 40 / 38, places=5)
        self.assertEqual(item["evidence"]["known_total_cost"], 40)
        self.assertEqual(item["status"], "ok")

    def test_zero_correct_and_incomplete_cost_are_not_free_success(self):
        item = self.report(sample(40, 0), {"max_cost_per_correct": 2})["checks"]["cost_per_correct"]
        self.assertIsNone(item["value"])
        self.assertEqual(item["status"], "unknown")
        self.assertIn("NO_CORRECT_OUTCOMES", item["reason_codes"])
        item = self.report(sample().replace("R0,a,a,0.95,1,", "R0,a,a,0.95,,"),
                           {"max_cost_per_correct": 2})["checks"]["cost_per_correct"]
        self.assertIsNone(item["value"])
        self.assertEqual(item["evidence"]["cost_rows"], 39)
        self.assertIn("INCOMPLETE_MEASUREMENTS", item["reason_codes"])

    def test_pending_and_no_output_failures_do_not_get_cost_verdicts(self):
        pending = self.report(sample() + "P0,a,,0.95,1,100,g\n", {"max_cost_per_correct": 2})
        self.assertIsNone(pending["checks"]["cost_per_correct"]["value"])
        self.assertIn("INCOMPLETE_OUTCOMES", pending["checks"]["cost_per_correct"]["reason_codes"])
        failed = self.report(sample() + "F0,,a,,1,100,g\n")
        self.assertEqual(failed["summary"]["invalid_rows"], 1)
        self.assertEqual(failed["status"], "attention")

    def test_unconfigured_diagnostics_are_visible_without_a_pass(self):
        report = self.report()
        for name in ("cost_per_correct", "latency"):
            item = report["checks"][name]
            self.assertIsNotNone(item["value"])
            self.assertEqual(item["evidence_status"], "sufficient")
            self.assertEqual(item["status"], "unknown")
            self.assertNotIn(name, report["decision"]["required_checks"])
        self.assertEqual(report["status"], "ok")

    def test_partial_confidence_and_latency_are_unknown(self):
        data = sample().replace("R0,a,a,0.95,1,100,", "R0,a,a,,1,,")
        report = self.report(data, {"max_mean_latency_ms": 200})
        for name in ("confidence_alignment", "latency"):
            item = report["checks"][name]
            self.assertIsNotNone(item["value"])
            self.assertEqual(item["status"], "unknown")
            self.assertIn("INCOMPLETE_MEASUREMENTS", item["reason_codes"])

    def test_baseline_and_group_guardrails(self):
        report = self.report(baseline=sample(29, 29))
        self.assertIsNotNone(report["checks"]["baseline_accuracy"]["value"])
        self.assertEqual(report["checks"]["baseline_accuracy"]["status"], "unknown")
        valid = self.report(baseline=sample(40, 36))
        self.assertEqual(valid["checks"]["baseline_accuracy"]["value"], 5)
        self.assertEqual(valid["checks"]["case_mix"]["status"], "ok")
        missing_group = self.report(sample().replace("100,g", "100,"), baseline=sample())
        self.assertIsNone(missing_group["checks"]["case_mix"]["value"])
        self.assertIn("INCOMPLETE_GROUP_ASSIGNMENT", missing_group["checks"]["case_mix"]["reason_codes"])

    def test_fingerprint_scope_and_reference_time(self):
        data = sample()
        report = self.report(data)
        self.assertEqual(report["provenance"]["input_sha256"]["current"], hashlib.sha256(data.encode()).hexdigest())
        self.assertIsNone(report["provenance"]["input_sha256"]["baseline"])
        self.assertEqual(report["evaluated_at"], "2026-10-13T12:00:00+00:00")
        self.assertFalse(report["synthetic"])

    def test_configuration_and_reference_time_validation(self):
        for cfg in ({"accuracy_threshold_basis": "certainty"}, {"min_evaluated_rows": True},
                    {"min_evaluated_rows": 0}, {"max_cost_per_correct": float("inf")}):
            with self.subTest(config=cfg), self.assertRaises(ValueError):
                configuration(cfg)
        with self.assertRaises(ValueError):
            analyze(sample(), at="2026-10-13T12:00:00")
