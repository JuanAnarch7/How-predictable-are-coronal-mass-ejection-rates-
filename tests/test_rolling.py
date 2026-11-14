"""Issue dates and training sets of the rolling-origin design (docs/PROTOCOL.md §4)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate.config import load_config, load_protocol, repo_path  # noqa: E402
from cmerate.features import MonthlySeries, known_minima, target, target_positions  # noqa: E402
from cmerate.rolling import issue_positions, training_issues  # noqa: E402


class TestRolling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg, cls.p = load_config(), load_protocol()
        table = pd.read_csv(repo_path(cls.cfg["outputs"]["monthly"]))
        cls.s = MonthlySeries.from_table(table, "fast", cls.cfg["data"]["cdaw"]["last_month"])

    def test_number_of_issue_positions(self):
        per = self.p["periods"]
        for h in self.p["horizons"]["monthly"]:
            self.assertEqual(len(issue_positions(self.s, h, per)), 198)
        self.assertEqual(len(issue_positions(self.s, "total12", per)), 187)
        self.assertEqual(len(issue_positions(self.s, "calendar", per)), 16)

    def test_monthly_horizons_share_targets(self):
        per = self.p["periods"]
        targets = {h: [t + h for t in issue_positions(self.s, h, per)] for h in self.p["horizons"]["monthly"]}
        first = targets[self.p["horizons"]["monthly"][0]]
        for h, tg in targets.items():
            self.assertEqual(tg, first, h)

    def test_all_test_targets_verifiable(self):
        per = self.p["periods"]; mc = self.p["coverage"]["target_min_window"]
        for h in self.p["horizons"]["monthly"] + ["total12", "calendar"]:
            for t in issue_positions(self.s, h, per):
                self.assertIsNotNone(target(self.s, t, h, mc), (h, str(self.s.months[t])))

    def test_training_targets_observed_before_issue(self):
        t = self.s.pos("2009-12")
        for h, L in [(1, 0), (12, 0), ("total12", 0), ("total12", 3)]:
            tr = training_issues(self.s, t, h, "I1", latency=L)
            self.assertGreater(len(tr), 20)
            for u in tr:
                self.assertLessEqual(target_positions(len(self.s), u, h, self.s.months)[-1], t - L)

    def test_minima_known_with_lag(self):
        s, lag = self.s, self.p["information"]["minimum_known_after_months"]
        starts = [s.pos(self.cfg["cycles"][k]) for k in ("c23_start", "c24_start", "c25_start")]
        self.assertEqual(known_minima(starts, s.pos("2009-11"), lag), starts[:1])
        self.assertEqual(known_minima(starts, s.pos("2009-12"), lag), starts[:2])
        self.assertEqual(known_minima(starts, s.pos("2020-12"), lag), starts)


if __name__ == "__main__":
    unittest.main()
