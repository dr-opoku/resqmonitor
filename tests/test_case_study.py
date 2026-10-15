"""Verify externally calculated confusion counts; not a new core feature."""
import csv
from collections import Counter
import io
from pathlib import Path
import unittest
from resqmonitor.demo import demo

FIXTURES = Path(__file__).resolve().parents[1] / 'resqmonitor/fixtures'

class CaseStudyTests(unittest.TestCase):
    def rows(self, name):
        return list(csv.DictReader(io.StringIO((FIXTURES/f'{name}.csv').read_text())))

    def test_case_confusion_counts_match_all_supplied_rows(self):
        expected = {
          'healthy': {('billing','billing'):13,('billing','refund'):1,('refund','refund'):13,('account','account'):12,('account','billing'):1},
          'degraded': {('billing','billing'):9,('billing','refund'):5,('refund','refund'):9,('refund','account'):4,('account','account'):8,('account','billing'):5}}
        for scenario, cells in expected.items():
            with self.subTest(scenario=scenario):
                observed = Counter((r['actual_label'],r['predicted_label']) for r in self.rows(scenario))
                self.assertEqual(observed, Counter(cells))
                self.assertEqual(sum(observed.values()),40)
                self.assertEqual(sum(v for (actual,predicted),v in observed.items() if actual==predicted),38 if scenario=='healthy' else 26)

    def test_supplied_cost_and_group_contrasts_are_descriptive(self):
        for scenario, total, correct in [('healthy',.8,38),('degraded',2.0,26)]:
            rows=self.rows(scenario)
            self.assertAlmostEqual(sum(float(r['cost']) for r in rows),total)
            self.assertEqual(sum(r['actual_label']==r['predicted_label'] for r in rows),correct)
        rows=self.rows('degraded')
        for group, correct in [('business',6),('consumer',20)]:
            sample=[r for r in rows if r['group']==group]
            self.assertEqual(len(sample),20)
            self.assertEqual(sum(r['actual_label']==r['predicted_label'] for r in sample),correct)
        self.assertEqual(demo('degraded')['status'],'attention')
