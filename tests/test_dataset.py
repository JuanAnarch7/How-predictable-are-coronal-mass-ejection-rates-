"""Regression tests on the real raw catalog.

They pin the dataset to the figures verified in docs/data_audit.md and check that the
committed processed tables are exactly what the code produces from the raw file.
"""
from __future__ import annotations

import io
import sys
import unittest
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate.config import load_config, repo_path, sha256  # noqa: E402
from cmerate.pipeline import build_all  # noqa: E402


class TestRealCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config()
        cls.raw = repo_path(cls.cfg["data"]["cdaw"]["raw_file"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            built = build_all(cls.cfg)
        cls.events, cls.monthly, cls.annual = built["events"], built["monthly"], built["annual"]

    def test_checksum(self):
        self.assertEqual(sha256(self.raw), self.cfg["data"]["cdaw"]["sha256"])

    def test_audited_figures(self):
        e = self.events
        self.assertEqual(len(e), 43440)
        self.assertEqual(str(e["datetime"].min()), "1996-01-11 00:14:36")
        self.assertEqual(str(e["datetime"].max()), "2026-07-31 22:00:31")
        self.assertEqual(int((e["v_lin"] >= 1000).sum()), 1036)
        self.assertEqual(int((e["width"] == 360).sum()), 1033)
        self.assertEqual(int(e["halo_cpa"].sum()), 1033)
        self.assertEqual(int(e["v_lin"].isna().sum()), 119)
        fast_2025 = (e["v_lin"] >= 1000) & (e["datetime"].dt.year == 2025)
        self.assertEqual(int(fast_2025.sum()), 70)

    def test_cycle_boundaries_are_smoothed_ssn_minima(self):
        """config [cycles] must match the minima of the 13-month smoothed SSN (D-07)."""
        if "ssn" not in self.monthly.columns:
            self.skipTest("SSN file not present")
        from cmerate.ssn import read_ssn
        s = read_ssn(repo_path(self.cfg["data"]["ssn"]["raw_file"])).dropna(subset=["ssn"]).reset_index(drop=True)
        x = s["ssn"].to_numpy()
        smoothed = np.full(len(x), np.nan)
        for i in range(6, len(x) - 6):
            w = x[i - 6:i + 7]
            smoothed[i] = (0.5 * w[0] + w[1:12].sum() + 0.5 * w[12]) / 12
        s["smoothed"] = smoothed
        cycles = self.cfg["cycles"]
        for key, (lo, hi) in {"c23_start": ("1995-01", "1998-12"),
                              "c24_start": ("2007-01", "2010-12"),
                              "c25_start": ("2018-01", "2021-12")}.items():
            window = s[(s["yearmonth"] >= lo) & (s["yearmonth"] <= hi)]
            self.assertEqual(window.loc[window["smoothed"].idxmin(), "yearmonth"], cycles[key], key)

    def test_soho_outage_months_unusable(self):
        unusable = set(self.monthly.loc[~self.monthly["usable"], "yearmonth"])
        for ym in ["1998-07", "1998-08", "1998-09", "1999-01"]:
            self.assertIn(ym, unusable)

    def test_monthly_counts_add_up(self):
        m = self.monthly[self.monthly["usable"]]
        self.assertTrue((m["n_all_good"] + m["n_quality_flagged"] == m["n_all"]).all())
        for name in ["fast", "halo", "wide"]:
            self.assertTrue((m[f"n_{name}"] <= m["n_all"]).all())
            self.assertTrue((m[f"n_{name}_good"] <= m[f"n_{name}"]).all())

    def test_annual_matches_monthly(self):
        m = self.monthly.assign(year=self.monthly["yearmonth"].str[:4].astype(int))
        for col in [c for c in m.columns if c.startswith("n_")]:
            expected = m.groupby("year")[col].sum(min_count=1).values
            np.testing.assert_array_equal(self.annual[col].values, expected)

    def test_committed_tables_are_reproducible(self):
        """data/processed/*.csv must be exactly what the pipeline produces from the raw file."""
        for key, df in [("monthly", self.monthly), ("annual", self.annual)]:
            committed = repo_path(self.cfg["outputs"][key])
            if not committed.exists():
                self.skipTest(f"{committed} not built yet")
            buf = io.StringIO()
            df.to_csv(buf, index=False, lineterminator="\n")
            self.assertEqual(buf.getvalue(), committed.read_text(encoding="utf-8"),
                             f"{committed} differs from a fresh build")


if __name__ == "__main__":
    unittest.main()
