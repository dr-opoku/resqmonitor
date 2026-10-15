"""Adversarial CLI and report-consumption regression tests; no network."""
import copy
import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from resqmonitor.__main__ import main
from resqmonitor.demo import SCENARIOS, demo
from resqmonitor._support import check, overall

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("consumer", ROOT / "scripts/inspect_report.py")
consumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer)


class StressTests(unittest.TestCase):
    def test_fractional_cost_total_is_reproducible(self):
        self.assertEqual(demo("healthy")["checks"]["cost_per_correct"]["evidence"]["known_total_cost"], 0.8)
        self.assertEqual(demo("degraded")["checks"]["cost_per_correct"]["evidence"]["known_total_cost"], 2.0)

    def test_output_aliases_never_change_inputs(self):
        for source_key in ("csv", "config", "baseline"):
            for alias in ("same", "symlink", "hardlink"):
                with self.subTest(source=source_key, alias=alias), TemporaryDirectory() as directory:
                    folder = Path(directory)
                    paths = {"csv": folder / "input.csv", "config": folder / "config.json", "baseline": folder / "extra.csv"}
                    for key, path in paths.items():
                        path.write_text("sentinel-" + key, encoding="utf-8")
                    source = paths[source_key]
                    target = source if alias == "same" else folder / "output.json"
                    if alias == "symlink":
                        target.symlink_to(source)
                    elif alias == "hardlink":
                        os.link(source, target)
                    before = {k:p.read_bytes() for k,p in paths.items()}
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        code = main(["check", str(paths["csv"]), "--config", str(paths["config"]), "--baseline", str(paths["baseline"]), "--format", "json", "--output", str(target)])
                    self.assertEqual(code, 2)
                    self.assertIn("overwrite", json.loads(stdout.getvalue())["error"]["message"])
                    self.assertEqual(before, {k:p.read_bytes() for k,p in paths.items()})

    def test_demo_cannot_overwrite_its_fixtures(self):
        source = ROOT / "resqmonitor/fixtures/config.json"
        before = source.read_bytes()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["demo", "--output", str(source)]), 2)
        self.assertEqual(source.read_bytes(), before)

    def test_consumer_matches_all_scenarios_and_never_authorizes(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                report = demo(scenario)
                result = consumer.inspect_report(report)
                self.assertEqual(result["assessment"], {"ok":"sample_rules_met", "attention":"criteria_not_met", "unknown":"insufficient_evidence"}[report["status"]])
                self.assertIs(result["action_authorized"], False)

    def test_consumer_respects_producer_rounding_at_thresholds(self):
        for value, bounds in ((94.99999999, {"minimum": 95}),
                              (95.00000001, {"maximum": 95}),
                              (95.0, {"minimum": 95})):
            with self.subTest(value=value, bounds=bounds):
                report = demo("healthy")
                report["checks"]["accuracy"] = check(
                    "Boundary", value, "%", {"observations": 1}, "Observed", **bounds)
                status = overall(list(report["checks"].values()), report["findings"])
                report["status"] = status
                report["decision"]["outcome"] = {
                    "ok": "criteria_met", "attention": "criteria_not_met",
                    "unknown": "undetermined"}[status]
                result = consumer.inspect_report(report)
                self.assertEqual(result["assessment"],
                                 "sample_rules_met" if status == "ok" else "criteria_not_met")
                self.assertIs(result["action_authorized"], False)

    def test_consumer_rejects_inconsistent_or_absent_evidence(self):
        mutations = [
            lambda r:r.update(schema_version="99"),
            lambda r:r.update(tool="unrelated"),
            lambda r:r.pop("provenance"),
            lambda r:r["decision"].update(action_authorized=True),
            lambda r:r["decision"].update(required_checks=[]),
            lambda r:r["checks"].pop("accuracy"),
            lambda r:r["checks"]["accuracy"].update(evidence={}),
            lambda r:r["checks"]["accuracy"].update(evidence_status="missing"),
            lambda r:r["checks"]["accuracy"].update(value=True),
            lambda r:r["checks"]["accuracy"].update(reason_codes=["UNVERIFIED"]),
            lambda r:r.update(status="unknown"),
            lambda r:r["checks"]["accuracy"] ["threshold"].update(minimum=101),
            lambda r:r["policy"].update(dataset_name="changed"),
        ]
        for mutate in mutations:
            report = copy.deepcopy(demo("healthy"));mutate(report)
            with self.subTest(report=str(report)[:80]), self.assertRaises(ValueError):
                consumer.inspect_report(report)

    def test_consumer_exit_codes_and_strict_json(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            for scenario in SCENARIOS:
                path.write_text(json.dumps(demo(scenario)), encoding="utf-8")
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(consumer.main([str(path)]), 0 if scenario == "healthy" else 1)
            error = {"schema_version":"2.0", "tool":"resqmonitor", "status":"error"}
            path.write_text(json.dumps(error), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(consumer.main([str(path)]), 2)
            for invalid in ('{"schema_version":"2.0","schema_version":"2.0"}', 'NaN', '1e999', '[]', '{'):
                path.write_text(invalid, encoding="utf-8")
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(consumer.main([str(path)]), 2)
