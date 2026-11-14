"""Verification scores against known cases (docs/PROTOCOL.md §8)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate import scores  # noqa: E402

K = 200


class TestScores(unittest.TestCase):
    def test_crps_of_point_forecast_is_absolute_error(self):
        for x, y in [(0, 0), (3, 7), (10, 2), (5, 5)]:
            self.assertAlmostEqual(scores.crps(scores.point_pmf(x, K), y), abs(x - y))

    def test_crps_nb_matches_sample_formula(self):
        rng = np.random.default_rng(1)
        mu, a, y = 6.0, 0.4, 9
        pmf = scores.nb_pmf(mu, a, K)
        n = 1 / a
        x = rng.negative_binomial(n, n / (n + mu), size=400_000)
        x2 = rng.negative_binomial(n, n / (n + mu), size=400_000)
        mc = np.mean(np.abs(x - y)) - 0.5 * np.mean(np.abs(x - x2))
        self.assertAlmostEqual(scores.crps(pmf, y), mc, delta=0.02)

    def test_truncated_pmf_is_refused(self):
        with self.assertRaises(ValueError):
            scores.crps(scores.nb_pmf(150.0, 0.5, 100), 10)

    def test_pit_and_coverage_of_calibrated_forecasts(self):
        rng = np.random.default_rng(2)
        mus = rng.uniform(0.3, 15, size=4000); a = 0.5; n = 1 / a
        ys = rng.negative_binomial(n, n / (n + mus))
        u = rng.uniform(size=len(ys))
        pits, cov80 = [], []
        for mu, y, uu in zip(mus, ys, u):
            pmf = scores.nb_pmf(mu, a, K)
            pits.append(scores.pit(pmf, y, uu))
            cov80.append(scores.covered(pmf, y, 0.8))
        self.assertGreater(stats.kstest(pits, "uniform").pvalue, 0.01)
        self.assertGreater(np.mean(cov80), 0.78)          # discrete intervals cover at least nominally
        self.assertLess(np.mean(cov80), 0.90)

    def test_overconfident_forecasts_give_u_shaped_pit(self):
        rng = np.random.default_rng(3)
        mus = rng.uniform(2, 15, size=3000); n = 1 / 1.0
        ys = rng.negative_binomial(n, n / (n + mus))                 # true dispersion 1.0
        pits = [scores.pit(scores.nb_pmf(mu, 0.01, K), y, u)          # forecast almost Poisson
                for mu, y, u in zip(mus, ys, rng.uniform(size=len(ys)))]
        tails = np.mean((np.array(pits) < 0.1) | (np.array(pits) > 0.9))
        self.assertGreater(tails, 0.3)

    def test_mixture_mean_and_skill(self):
        pmf = scores.mixture_pmf(np.array([2.0, 4.0]), 0.3, K)
        self.assertAlmostEqual(scores.mean(pmf), 3.0, places=6)
        self.assertAlmostEqual(scores.skill_score(np.array([1.0, 1.0]), np.array([2.0, 2.0])), 0.5)
        self.assertEqual(scores.brier(0.25, True), 0.5625)


if __name__ == "__main__":
    unittest.main()
