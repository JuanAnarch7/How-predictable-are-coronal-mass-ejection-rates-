"""Consistency checks between config/protocol.toml, config/config.toml and the data."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate.config import load_config, load_protocol, repo_path  # noqa: E402


def month(s: str) -> pd.Period:
    return pd.Period(s, freq="M")


class TestProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load_protocol()
        cls.cfg = load_config()

    def test_document_and_version(self):
        doc = repo_path(self.p["protocol"]["document"]).read_text(encoding="utf-8")
        self.assertIn(self.p["protocol"]["version"], doc)
        self.assertIn(self.p["protocol"]["status"], {"draft", "frozen"})

    def test_targets_are_defined_subpopulations(self):
        for name in self.p["targets"]["subpopulations"]:
            self.assertIn(name, self.cfg["subpopulations"])
        self.assertEqual(self.p["inference"]["confirmatory"],
                         [f"P1_{s}" for s in self.p["targets"]["subpopulations"]])

    def test_period_arithmetic(self):
        per = self.p["periods"]
        self.assertEqual(month(per["total12_issue_first"]) + 1, month(per["test_target_first"]))
        self.assertEqual(month(per["total12_issue_last"]) + 12, month(per["test_target_last"]))
        self.assertGreaterEqual(per["calendar_year_first"], month(per["test_target_first"]).year)
        self.assertLessEqual(per["calendar_year_last"], month(per["test_target_last"]).year)
        self.assertLessEqual(month(per["test_target_last"]), month(self.cfg["data"]["cdaw"]["last_month"]))
        self.assertGreaterEqual(month(per["training_start"]), month(self.cfg["data"]["cdaw"]["first_month"]))

    def test_coverage_rule_matches_dataset_rule(self):
        self.assertAlmostEqual(self.p["coverage"]["target_min_monthly"],
                               1 - self.cfg["coverage"]["max_gap_fraction_usable"])

    def test_all_test_targets_usable(self):
        m = pd.read_csv(repo_path(self.cfg["outputs"]["monthly"]))
        per = self.p["periods"]
        t = m[(m["yearmonth"] >= per["test_target_first"]) & (m["yearmonth"] <= per["test_target_last"])]
        n_months = (month(per["test_target_last"]) - month(per["test_target_first"])).n + 1
        self.assertEqual(len(t), n_months)
        self.assertTrue(t["usable"].all())

    def test_horizons_and_inference(self):
        self.assertTrue(all(h >= 1 for h in self.p["horizons"]["monthly"]))
        inf = self.p["inference"]
        self.assertEqual(inf["newey_west_lags_total12"], 11)       # 12-month windows overlap by 11
        self.assertEqual(inf["sides"], "one")
        self.assertEqual(inf["multiplicity"], "holm")
        lo, hi = self.p["success"]["coverage80_low"], self.p["success"]["coverage80_high"]
        self.assertLess(lo, 0.8)
        self.assertGreater(hi, 0.8)

    def test_ssn_forecast_backtest_outside_test_period(self):
        f = self.p["ssn_forecast"]
        c, w = f["default_variant"]
        self.assertIn(c, f["reference_cycles_since_year_candidates"])
        self.assertIn(w, f["scaling_window_months_candidates"])
        self.assertLess(month(f["backtest_issues"][1]), month(self.p["periods"]["test_target_first"]))

    def test_calibration_uses_conservative_rule(self):
        inf = self.p["inference"]
        self.assertEqual(inf["calibration_rule"], "max_critical_value")
        main = inf["calibration_generator_fit_periods"][0]
        self.assertLess(month(main[1]), month(self.p["periods"]["test_target_first"]))

    def test_post_freeze_catalogs_exist(self):
        for f in self.p["post_freeze"]["catalogs"]:
            self.assertTrue(repo_path(f).exists(), f)


if __name__ == "__main__":
    unittest.main()
