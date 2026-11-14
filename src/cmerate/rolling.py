"""Rolling-origin design: issue dates of the test period and training pairs at each issue.

docs/PROTOCOL.md §4: the monthly horizons share one target set (issue = target - h); the
12-month totals are issued every month over a fixed range; calendar-year totals are issued
each December (forecast published in January). At issue t, a model is trained on every
past issue u whose whole target period was observed by t - L (catalog latency) and whose
predictors and target exist (expanding window from the start of the data).
"""
from __future__ import annotations

import pandas as pd

from .features import MonthlySeries, predictors, target, target_positions


def issue_positions(s: MonthlySeries, horizon, periods: dict) -> list[int]:
    """Issue positions of the test period for one target type."""
    if horizon == "total12":
        return list(range(s.pos(periods["total12_issue_first"]), s.pos(periods["total12_issue_last"]) + 1))
    if horizon == "calendar":
        return [s.pos(f"{year - 1}-12") for year in range(periods["calendar_year_first"],
                                                           periods["calendar_year_last"] + 1)]
    h = int(horizon)
    first, last = s.pos(periods["test_target_first"]), s.pos(periods["test_target_last"])
    return [k - h for k in range(first, last + 1)]


def training_issues(s: MonthlySeries, t: int, horizon, info: str, *, latency: int = 0,
                    min_window_coverage: float = 0.9, **predictor_kw) -> list[int]:
    """Past issues usable for training a model issued at t (targets observed by t - latency)."""
    out = []
    for u in range(0, t):
        pos = target_positions(len(s), u, horizon, s.months)
        if pos is None or pos[-1] > t - latency:
            continue
        if horizon == "calendar" and s.months[u].month != 12:
            continue
        if target(s, u, horizon, min_window_coverage) is None:
            continue
        if predictors(s, u, horizon, info, latency=latency, **predictor_kw) is None:
            continue
        out.append(u)
    return out


def issue_month(s: MonthlySeries, t: int) -> pd.Period:
    return s.months[t]
