"""Monthly and annual CME count tables.

The annual table is always derived from the monthly table, so that both time scales come
from exactly the same events and cannot disagree.

Counts in months marked unusable (coverage below the configured limit) are set to NaN:
a data gap is never reported as zero CMEs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .coverage import monthly_coverage


def subpopulation_masks(events: pd.DataFrame, spec: dict) -> dict[str, pd.Series]:
    """Boolean masks for each subpopulation defined in config [subpopulations.*]."""
    masks = {}
    for name, rule in spec.items():
        if not isinstance(rule, dict):
            continue
        m = pd.Series(True, index=events.index)
        if "min_speed" in rule:
            m &= events["v_lin"] >= rule["min_speed"]
        if "max_speed" in rule:
            m &= events["v_lin"] <= rule["max_speed"]
        if "min_width" in rule:
            m &= events["width"] >= rule["min_width"]
        if "max_width" in rule:
            m &= events["width"] <= rule["max_width"]
        masks[name] = m.fillna(False)
    return masks


def build_monthly(events: pd.DataFrame, cfg: dict, ssn: pd.DataFrame | None = None) -> pd.DataFrame:
    months = pd.period_range(cfg["data"]["cdaw"]["first_month"], cfg["data"]["cdaw"]["last_month"], freq="M")
    month = events["datetime"].dt.to_period("M")
    good = ~events["quality_flagged"]

    def count(mask: pd.Series) -> pd.Series:
        return events[mask].groupby(month[mask]).size().reindex(months, fill_value=0)

    out = pd.DataFrame(index=months)
    for name, mask in subpopulation_masks(events, cfg["subpopulations"]).items():
        out[f"n_{name}"] = count(mask)
        out[f"n_{name}_good"] = count(mask & good)
    out["n_quality_flagged"] = count(events["quality_flagged"])
    out["n_speed_missing"] = count(events["v_lin"].isna())
    out.index = out.index.astype(str)
    out.index.name = "yearmonth"
    out = out.reset_index()

    cov = monthly_coverage(events["datetime"], months, cfg["coverage"]["gap_threshold_days"])
    out = out.merge(cov, on="yearmonth", how="left")
    out["usable"] = out["gap_days"] / out["days_in_month"] <= cfg["coverage"]["max_gap_fraction_usable"]

    count_cols = [c for c in out.columns if c.startswith("n_")]
    out[count_cols] = out[count_cols].astype("float64")
    out.loc[~out["usable"], count_cols] = np.nan

    if ssn is not None:
        out = out.merge(ssn, on="yearmonth", how="left")
    out["cycle"] = label_cycles(out["yearmonth"], cfg["cycles"])
    return out


def label_cycles(yearmonth: pd.Series, cycles: dict) -> pd.Series:
    ym = yearmonth.astype(str)
    lab = pd.Series("pre_C23", index=ym.index)
    lab[ym >= cycles["c23_start"]] = "C23"
    lab[ym >= cycles["c24_start"]] = "C24"
    lab[ym >= cycles["c25_start"]] = "C25"
    return lab


def build_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    """Calendar-year totals derived from the monthly table.

    ``n_*``                sum over usable months only (gaps contribute nothing)
    ``coverage_fraction``  covered days in usable months / days in the year;
                           models should use it as exposure rather than rescaling counts
    ``n_months_usable``    number of usable months (incomplete years have fewer than 12)
    """
    m = monthly.copy()
    m["year"] = m["yearmonth"].str[:4].astype(int)
    m["covered_days"] = np.where(m["usable"], m["days_in_month"] - m["gap_days"], 0.0)
    count_cols = [c for c in m.columns if c.startswith("n_")]
    agg = {c: (c, lambda s: s.sum(min_count=1)) for c in count_cols}
    agg.update({
        "days_in_year": ("days_in_month", "sum"),
        "covered_days": ("covered_days", "sum"),
        "n_months": ("yearmonth", "size"),
        "n_months_usable": ("usable", "sum"),
    })
    if "ssn" in m.columns:
        agg["ssn_mean"] = ("ssn", "mean")
        agg["n_months_ssn_provisional"] = ("ssn_provisional", "sum")
    out = m.groupby("year").agg(**agg).reset_index()
    out["coverage_fraction"] = (out["covered_days"] / out["days_in_year"]).round(4)
    out["complete_year"] = out["n_months"] == 12
    return out
