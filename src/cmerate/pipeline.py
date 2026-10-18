"""End-to-end data build shared by scripts/build_dataset.py and the tests."""
from __future__ import annotations

import warnings

import pandas as pd

from . import cdaw, ssn as ssn_mod, tables
from .config import check_checksum, repo_path


def build_all(cfg: dict) -> dict[str, pd.DataFrame]:
    """Return {'events', 'monthly', 'annual'} built from the raw files named in cfg."""
    raw_cdaw = repo_path(cfg["data"]["cdaw"]["raw_file"])
    check_checksum(raw_cdaw, cfg["data"]["cdaw"]["sha256"])
    events = cdaw.read_catalog(raw_cdaw)

    ssn = None
    raw_ssn = repo_path(cfg["data"]["ssn"]["raw_file"])
    if raw_ssn.exists():
        check_checksum(raw_ssn, cfg["data"]["ssn"]["sha256"])
        ssn = ssn_mod.read_ssn(raw_ssn)
    else:
        warnings.warn(f"{raw_ssn.name} not found: tables are built without sunspot numbers.",
                      stacklevel=2)

    monthly = tables.build_monthly(events, cfg, ssn)
    annual = tables.build_annual(monthly)
    return {"events": events, "monthly": monthly, "annual": annual}


def dataset_numbers(events: pd.DataFrame, monthly: pd.DataFrame) -> dict:
    """Dataset-level figures quoted in the manuscript (Data section)."""
    v, w = events["v_lin"], events["width"]
    fast = v >= 1000
    halo = w == 360
    year = events["datetime"].dt.year
    return {
        "NEventsTotal": int(len(events)),
        "FirstEventDate": events["datetime"].min().strftime("%Y-%m-%d"),
        "LastEventDate": events["datetime"].max().strftime("%Y-%m-%d"),
        "NEventsFast": int(fast.sum()),
        "NEventsHalo": int(halo.sum()),
        "NEventsSpeedMissing": int(v.isna().sum()),
        "PctQualityFlaggedAll": f"{100 * events['quality_flagged'].mean():.1f}",
        "PctQualityFlaggedFast": f"{100 * events.loc[fast, 'quality_flagged'].mean():.1f}",
        "PctQualityFlaggedHalo": f"{100 * events.loc[halo, 'quality_flagged'].mean():.1f}",
        "NMonthsTotal": int(len(monthly)),
        "NMonthsUnusable": int((~monthly["usable"]).sum()),
        "NFastTwentyTwentyFive": int((fast & (year == 2025)).sum()),
    }
