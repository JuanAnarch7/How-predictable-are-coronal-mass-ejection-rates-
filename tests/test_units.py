"""Unit tests on small synthetic inputs. Run with:  python -m unittest discover tests  (or pytest)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate import cdaw, coverage, ssn, tables  # noqa: E402
from cmerate.numbers import write_numbers  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"

CFG = {
    "data": {"cdaw": {"first_month": "2021-07", "last_month": "2021-09"}},
    "subpopulations": {
        "primary": "fast",
        "all": {"description": "all"},
        "fast": {"min_speed": 1000},
        "halo": {"min_width": 360, "max_width": 360},
        "wide": {"min_width": 120, "max_width": 360},
    },
    "coverage": {"gap_threshold_days": 5.0, "max_gap_fraction_usable": 0.5},
    "cycles": {"c23_start": "1996-05", "c24_start": "2008-12", "c25_start": "2019-12"},
}


class TestCdawParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = cdaw.read_catalog(FIXTURES / "cdaw_sample.txt")

    def test_all_lines_parsed(self):
        self.assertEqual(len(self.df), 7)
        self.assertEqual(self.df["raw_line"].tolist(), [2, 3, 4, 5, 6, 7, 8])

    def test_full_remark_kept(self):
        self.assertEqual(self.df.loc[2, "remarks"], "Faint; Very Poor Event; Only 2 points; Only C2")

    def test_quality_flags_after_other_notes(self):
        # The previous pipeline kept only the first word ("Fixed", "Faint") and lost these flags.
        self.assertTrue(self.df.loc[3, "poor"])
        self.assertFalse(self.df.loc[3, "very_poor"])
        self.assertTrue(self.df.loc[2, "very_poor"])
        self.assertFalse(self.df.loc[2, "poor"])
        self.assertEqual(self.df["quality_flagged"].tolist(), [False, True, True, True, False, False, False])

    def test_other_flags(self):
        self.assertEqual(self.df["only_c2"].tolist(), [False, False, True, True, False, False, False])
        self.assertEqual(self.df["only_c3"].tolist(), [True, True, False, False, False, False, False])
        self.assertEqual(self.df["few_points"].tolist(), [False, False, True, False, False, True, False])

    def test_halo_and_missing_values(self):
        row = self.df.loc[2]
        self.assertTrue(row["halo_cpa"])
        self.assertTrue(np.isnan(row["cpa"]))
        self.assertEqual(row["width"], 360)
        self.assertTrue(np.isnan(row["v2_init"]))
        self.assertTrue(np.isnan(self.df.loc[6, "v_lin"]))

    def test_uncertain_marker(self):
        row = self.df.loc[1]
        self.assertAlmostEqual(row["accel"], -126.3)
        self.assertTrue(row["accel_uncertain"])
        self.assertAlmostEqual(row["mass"], 7.1e13)
        self.assertTrue(row["mass_uncertain"])
        self.assertFalse(self.df.loc[3, "accel_uncertain"])

    def test_rejects_malformed_line(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("1996/01/11  00:14:36  267  18\n")
        with self.assertRaises(ValueError):
            cdaw.read_catalog(fh.name)


class TestSsnReader(unittest.TestCase):
    ROWS = [(2026, 1, 2026.042, 112.5, 15.0, 900, 0), (2025, 12, 2025.958, 124.2, 14.1, 950, 1),
            (1749, 1, 1749.042, 96.7, -1.0, -1, 1)]

    def _write(self, sep: str) -> str:
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            for r in self.ROWS:
                fh.write(sep.join(str(x) for x in r) + "\n")
        return fh.name

    def test_both_formats(self):
        for sep in (";", "  "):
            df = ssn.read_ssn(self._write(sep))
            self.assertEqual(df["yearmonth"].tolist(), ["2026-01", "2025-12", "1749-01"])
            self.assertEqual(df["ssn_provisional"].tolist(), [True, False, False])
            self.assertTrue(np.isnan(df.loc[2, "ssn_std"]))
            self.assertAlmostEqual(df.loc[0, "ssn"], 112.5)
            # no SSN column may start with "n_": those are treated as CME counts
            self.assertFalse(any(c.startswith("n_") for c in df.columns))

    def test_rejects_wrong_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("2026;1;2026.042;112.5\n")
        with self.assertRaises(ValueError):
            ssn.read_ssn(fh.name)


def _events(times, widths=None, speeds=None, flagged=None):
    n = len(times)
    return pd.DataFrame({
        "datetime": pd.to_datetime(times),
        "width": widths if widths is not None else [50.0] * n,
        "v_lin": speeds if speeds is not None else [400.0] * n,
        "quality_flagged": flagged if flagged is not None else [False] * n,
    })


class TestCoverage(unittest.TestCase):
    def test_known_gap(self):
        # Events every day except a 10-day hole from 2021-07-10 to 2021-07-20.
        days = [d for d in pd.date_range("2021-07-01 12:00", "2021-07-31 12:00", freq="D")
                if not pd.Timestamp("2021-07-10 13:00") <= d < pd.Timestamp("2021-07-20 12:00")]
        cov = coverage.monthly_coverage(pd.Series(days), pd.period_range("2021-07", "2021-07", freq="M"), 5.0)
        self.assertAlmostEqual(cov.loc[0, "gap_days"], 10.0, places=3)
        self.assertAlmostEqual(cov.loc[0, "coverage_fraction"], 1 - 10 / 31, places=3)

    def test_short_quiet_periods_ignored(self):
        days = pd.Series(pd.date_range("2021-07-01", "2021-07-31", freq="4D"))
        cov = coverage.monthly_coverage(days, pd.period_range("2021-07", "2021-07", freq="M"), 5.0)
        self.assertEqual(cov.loc[0, "gap_days"], 0.0)


class TestTables(unittest.TestCase):
    def setUp(self):
        # July: daily events (full coverage). August: no events (gap). September: daily events.
        times = list(pd.date_range("2021-07-01 06:00", "2021-07-31 06:00", freq="D")) + \
                list(pd.date_range("2021-09-01 06:00", "2021-09-30 06:00", freq="D"))
        n = len(times)
        speeds = [400.0] * n
        widths = [50.0] * n
        speeds[0], speeds[1], speeds[2] = 1000.0, 999.9, np.nan   # boundary and missing speed
        widths[3], widths[4], widths[5] = 120.0, 119.0, 360.0     # boundary widths and a halo
        flagged = [False] * n
        flagged[0] = True
        self.events = _events(times, widths, speeds, flagged)
        self.monthly = tables.build_monthly(self.events, CFG)

    def test_boundaries(self):
        jul = self.monthly.iloc[0]
        self.assertEqual(jul["n_all"], 31)
        self.assertEqual(jul["n_fast"], 1)          # 1000 included, 999.9 and NaN excluded
        self.assertEqual(jul["n_fast_good"], 0)     # the fast event is flagged
        self.assertEqual(jul["n_wide"], 2)          # 120 and 360 included, 119 excluded
        self.assertEqual(jul["n_halo"], 1)
        self.assertEqual(jul["n_speed_missing"], 1)
        self.assertEqual(jul["n_quality_flagged"], 1)

    def test_gap_month_is_nan_not_zero(self):
        aug = self.monthly.iloc[1]
        self.assertFalse(aug["usable"])
        self.assertTrue(np.isnan(aug["n_all"]))

    def test_annual_is_sum_of_usable_months(self):
        annual = tables.build_annual(self.monthly)
        self.assertEqual(annual.loc[0, "n_all"], 61)
        self.assertEqual(annual.loc[0, "n_months_usable"], 2)
        self.assertFalse(annual.loc[0, "complete_year"])

    def test_cycle_labels(self):
        lab = tables.label_cycles(pd.Series(["1996-04", "1996-05", "2008-12", "2019-11", "2019-12"]), CFG["cycles"])
        self.assertEqual(lab.tolist(), ["pre_C23", "C23", "C24", "C24", "C25"])


class TestNumbers(unittest.TestCase):
    def test_macros(self):
        with tempfile.TemporaryDirectory() as d:
            write_numbers({"NEventsTotal": 5}, Path(d) / "n.json", Path(d) / "n.tex")
            self.assertIn(r"\newcommand{\NEventsTotal}{5}", (Path(d) / "n.tex").read_text())

    def test_invalid_key(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_numbers({"n_2025": 1}, Path(d) / "n.json", Path(d) / "n.tex")


if __name__ == "__main__":
    unittest.main()
