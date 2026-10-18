"""Per-month observing-coverage proxy derived from the catalog itself.

PROVISIONAL. An interval of at least ``gap_threshold_days`` between consecutive catalogued
CMEs is treated as a period without observations. This reliably finds the long SOHO
outages of 1998-1999, but during solar minima such intervals can be genuine quiet
periods. It must be replaced by the official LASCO data-gap information before the
coverage is used as an exposure term in any model (docs/DECISIONS.md, D-06).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def gap_intervals(times: pd.Series, start: pd.Timestamp, end: pd.Timestamp,
                  threshold_days: float) -> pd.DataFrame:
    """Intervals of at least ``threshold_days`` with no catalogued CME, within [start, end]."""
    t = pd.concat([pd.Series([start]), times.sort_values(), pd.Series([end])]).reset_index(drop=True)
    gaps = pd.DataFrame({"start": t.iloc[:-1].values, "end": t.iloc[1:].values})
    gaps["days"] = (gaps["end"] - gaps["start"]).dt.total_seconds() / 86400
    return gaps[gaps["days"] >= threshold_days].reset_index(drop=True)


def monthly_coverage(times: pd.Series, months: pd.PeriodIndex, threshold_days: float) -> pd.DataFrame:
    start = months[0].start_time
    end = months[-1].end_time
    gaps = gap_intervals(times, start, end, threshold_days)
    rows = []
    for m in months:
        a, b = m.start_time, m.end_time
        days_in_month = m.days_in_month
        overlap = gaps[(gaps["end"] > a) & (gaps["start"] < b)]
        gap_days = sum(
            (min(g.end, b) - max(g.start, a)).total_seconds() / 86400 for g in overlap.itertuples()
        )
        gap_days = min(gap_days, days_in_month)
        rows.append({
            "yearmonth": str(m),
            "days_in_month": days_in_month,
            "gap_days": round(gap_days, 3),
            "longest_gap_days": round(overlap["days"].max(), 3) if len(overlap) else 0.0,
        })
    out = pd.DataFrame(rows)
    out["coverage_fraction"] = (1 - out["gap_days"] / out["days_in_month"]).clip(0, 1).round(4)
    return out
