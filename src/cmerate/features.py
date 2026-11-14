"""Information available at an issue date: predictors, targets and the cycle-phase analogue.

Conventions (docs/PROTOCOL.md §3–§5)
-----------------------------------
* A forecast issued at month position ``t`` uses CME counts of months ``<= t - L``
  (catalog latency ``L``, 0 in the main analysis) and the SSN of months ``<= t``.
* CME rates are exposure-weighted: (sum of counts) / (sum of covered month fractions) over
  the usable months of a window. If more than ``max_unusable`` of a window is unusable the
  predictor is missing and no forecast is issued.
* The exposure of the *target* period (its observed coverage) is part of the target, not a
  predictor: models forecast a rate and the count is compared with rate × exposure.
* A cycle minimum counts as known ``minimum_lag`` months after it occurs.
* The oracle predictor (observed SSN of the target period) is the only quantity that looks
  past ``t``; it exists only for the upper bound I★ and is excluded from the leakage test.

Every function receives a position ``t`` and reads arrays only up to the positions allowed
above; ``tests/test_no_leakage.py`` checks this by comparing with truncated series.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MonthlySeries:
    """One subpopulation's monthly counts, exposure and SSN, positionally indexed."""
    months: pd.PeriodIndex
    y: np.ndarray        # counts; NaN in unusable months
    e: np.ndarray        # exposure = coverage fraction; 0 in unusable months
    ssn: np.ndarray

    @classmethod
    def from_table(cls, table: pd.DataFrame, subpopulation: str, last_month: str | None = None) -> "MonthlySeries":
        t = table if last_month is None else table[table["yearmonth"] <= last_month]
        usable = t["usable"].to_numpy(bool)
        y = t[f"n_{subpopulation}"].to_numpy(float)
        y = np.where(usable, y, np.nan)
        e = np.where(usable, t["coverage_fraction"].to_numpy(float), 0.0)
        return cls(pd.PeriodIndex(t["yearmonth"], freq="M"), y, e, t["ssn"].to_numpy(float))

    def __len__(self) -> int:
        return len(self.months)

    def pos(self, yearmonth: str) -> int:
        return int(self.months.get_loc(pd.Period(yearmonth, freq="M")))

    def truncated(self, t: int) -> "MonthlySeries":
        """The series as it would look if nothing after position t existed."""
        return MonthlySeries(self.months[: t + 1], self.y[: t + 1].copy(), self.e[: t + 1].copy(),
                             self.ssn[: t + 1].copy())


# ------------------------------------------------------------------ window statistics
def rate_mean(s: MonthlySeries, end: int, window: int, max_unusable: float) -> float:
    """Exposure-weighted CME rate over positions end-window+1 .. end (NaN if not computable)."""
    start = end - window + 1
    if start < 0 or end >= len(s):
        return np.nan
    y, e = s.y[start:end + 1], s.e[start:end + 1]
    usable = e > 0
    if (1 - usable.mean()) > max_unusable or e[usable].sum() <= 0:
        return np.nan
    return float(np.nansum(y[usable]) / e[usable].sum())


def last_rate(s: MonthlySeries, end: int) -> float:
    if end < 0 or end >= len(s) or s.e[end] <= 0:
        return np.nan
    return float(s.y[end] / s.e[end])


def ssn_mean(s: MonthlySeries, end: int, window: int) -> float:
    start = end - window + 1
    if start < 0 or end >= len(s):
        return np.nan
    v = s.ssn[start:end + 1]
    return float(v.mean()) if np.all(np.isfinite(v)) else np.nan


# ------------------------------------------------------------------ targets
def target_positions(s_len: int, t: int, horizon, months: pd.PeriodIndex | None = None) -> list[int] | None:
    """Positions of the target period of a forecast issued at t.

    horizon: int h (monthly count of month t+h), "total12" (months t+1..t+12) or
    "calendar" (the next calendar year; t must be a December).
    """
    if horizon == "total12":
        pos = list(range(t + 1, t + 13))
    elif horizon == "calendar":
        if months is None or months[t].month != 12:
            return None
        pos = list(range(t + 1, t + 13))
    else:
        pos = [t + int(horizon)]
    return pos if pos[-1] < s_len else None


def target(s: MonthlySeries, t: int, horizon, min_window_coverage: float) -> tuple[float, float] | None:
    """(observed count, exposure) of the target, or None if it cannot be verified."""
    pos = target_positions(len(s), t, horizon, s.months)
    if pos is None:
        return None
    y, e = s.y[pos], s.e[pos]
    if len(pos) == 1:
        return (float(y[0]), float(e[0])) if e[0] > 0 else None
    if np.any(e <= 0) or e.mean() < min_window_coverage:
        return None
    return float(y.sum()), float(e.sum())


# ------------------------------------------------------------------ cycle-phase analogue
def known_minima(starts: list[int], t: int, minimum_lag: int) -> list[int]:
    return [p for p in starts if p + minimum_lag <= t]


def analogue_rate(s: MonthlySeries, t: int, horizon, starts: list[int], minimum_lag: int,
                  halfwindow: int, latency: int = 0) -> float:
    """Mean monthly rate at the same cycle phase in previous cycles (NaN if unavailable).

    The current cycle starts at the last minimum known at t; previous cycles are the earlier
    known minima. For each previous cycle, the months aligned with the target period
    (±halfwindow for a single month) are averaged with exposure weights, using only months
    observed by t - latency. The result is the mean over previous cycles.
    """
    known = known_minima(starts, t, minimum_lag)
    if len(known) < 2:
        return np.nan
    current, previous = known[-1], known[:-1]
    pos = target_positions(len(s) + 10_000, t, horizon, None if horizon != "calendar" else s.months)
    if pos is None:
        return np.nan
    hw = halfwindow if len(pos) == 1 else 0
    last_obs = t - latency
    rates = []
    for p in previous:
        aligned = [p + (k - current) + d for k in pos for d in range(-hw, hw + 1)]
        aligned = [a for a in aligned if 0 <= a <= last_obs]
        if not aligned:
            continue
        e = s.e[aligned]
        if e.sum() <= 0:
            continue
        rates.append(np.nansum(s.y[aligned][e > 0]) / e[e > 0].sum())
    return float(np.mean(rates)) if rates else np.nan


# ------------------------------------------------------------------ predictors
def predictors(s: MonthlySeries, t: int, horizon, info: str, *, windows=(3, 12),
               last_month_horizons=(1,), latency: int = 0, max_unusable: float = 0.25) -> dict | None:
    """Predictor values for a forecast issued at t, or None if a required one is missing.

    info: "I0" (CME history), "I1" (+ SSN up to t) or "Istar" (+ observed SSN of the target
    period; upper bound only). Keys hold raw values; models apply log(1 + x).
    """
    c = t - latency                                  # last month of CME data available
    w_short, w_long = windows
    out = {"rate_short": rate_mean(s, c, w_short, max_unusable),
           "rate_long": rate_mean(s, c, w_long, max_unusable)}
    if not isinstance(horizon, str) and int(horizon) in last_month_horizons:
        out["rate_last"] = last_rate(s, c)
    if info in ("I1", "Istar"):
        out["ssn_short"] = ssn_mean(s, t, w_short)
        out["ssn_long"] = ssn_mean(s, t, w_long)
    if info == "Istar":
        pos = target_positions(len(s), t, horizon, s.months)
        if pos is None:
            return None
        v = s.ssn[pos]
        out["ssn_target"] = float(v.mean()) if np.all(np.isfinite(v)) else np.nan
    if info not in ("I0", "I1", "Istar"):
        raise ValueError(f"unknown information set {info!r}")
    return out if all(np.isfinite(v) for v in out.values()) else None
