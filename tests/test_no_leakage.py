"""No predictor, training set or reference may use data after the issue date (docs/PROTOCOL.md §3).

For many issue dates t, every quantity computed from the full series must equal the same
quantity computed from the series truncated at t (or with CME counts truncated at t - L).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate.config import load_config, load_protocol, repo_path  # noqa: E402
from cmerate.features import MonthlySeries, analogue_rate, predictors  # noqa: E402
from cmerate.rolling import training_issues  # noqa: E402

HORIZONS = [1, 6, 12, "total12", "calendar"]


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(np.isclose(a[k], b[k], equal_nan=True) for k in a)
    return bool(np.isclose(a, b, equal_nan=True))


class TestNoLeakage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg, cls.p = load_config(), load_protocol()
        table = pd.read_csv(repo_path(cfg["outputs"]["monthly"]))
        cls.series = {sp: MonthlySeries.from_table(table, sp, cfg["data"]["cdaw"]["last_month"])
                      for sp in cls.p["targets"]["subpopulations"]}
        s = cls.series["fast"]
        cls.starts = [s.pos(cfg["cycles"][k]) for k in ("c23_start", "c24_start", "c25_start")]
        rng = np.random.default_rng(0)
        cls.issues = sorted(set(rng.integers(20, len(s) - 14, size=25).tolist()) |
                            {s.pos("2009-12"), s.pos("2019-12"), s.pos("2020-12")})
        inf = cls.p["information"]
        cls.kw = dict(windows=tuple(inf["predictor_windows"]), last_month_horizons=tuple(inf["last_month_term_horizons"]),
                      max_unusable=inf["max_unusable_fraction_in_window"])

    def test_predictors(self):
        for sp, s in self.series.items():
            for t in self.issues:
                cut = s.truncated(t)
                for h in HORIZONS:
                    for info in ("I0", "I1"):
                        for L in (0, 1, 3):
                            a = predictors(s, t, h, info, latency=L, **self.kw)
                            b = predictors(cut, t, h, info, latency=L, **self.kw)
                            self.assertTrue(same(a, b), (sp, str(s.months[t]), h, info, L))

    def test_latency_hides_recent_counts(self):
        s = self.series["fast"]
        for t in self.issues:
            for L in (1, 3):
                hidden = MonthlySeries(s.months, s.y.copy(), s.e.copy(), s.ssn)
                hidden.y[t - L + 1:] = 999.0          # counts the forecaster cannot know yet
                a = predictors(s, t, 6, "I1", latency=L, **self.kw)
                b = predictors(hidden, t, 6, "I1", latency=L, **self.kw)
                self.assertTrue(same(a, b), (str(s.months[t]), L))

    def test_analogue(self):
        lag = self.p["information"]["minimum_known_after_months"]
        hw = self.p["models"]["phase_analogue_monthly_halfwindow"]
        for s in self.series.values():
            for t in self.issues:
                cut = s.truncated(t)
                for h in HORIZONS:
                    for L in (0, 3):
                        a = analogue_rate(s, t, h, self.starts, lag, hw, L)
                        b = analogue_rate(cut, t, h, self.starts, lag, hw, L)
                        self.assertTrue(same(a, b), (str(s.months[t]), h, L))

    def test_training_sets(self):
        s = self.series["halo"]
        for t in self.issues[::4]:
            for h in (1, 12, "total12"):
                a = training_issues(s, t, h, "I1", **self.kw)
                b = training_issues(s.truncated(t), t, h, "I1", **self.kw)
                self.assertEqual(a, b, (str(s.months[t]), h))

    def test_oracle_does_look_ahead(self):
        """Sanity check of the test itself: the oracle predictor must differ when truncated."""
        s = self.series["fast"]
        t = s.pos("2012-06")
        self.assertIsNotNone(predictors(s, t, "total12", "Istar", **self.kw))
        self.assertIsNone(predictors(s.truncated(t), t, "total12", "Istar", **self.kw))


if __name__ == "__main__":
    unittest.main()
