"""Monthly observing coverage of LASCO.

Official coverage (used by the pipeline)
----------------------------------------
The CDAW Data Center publishes, for each month, the list of LASCO/C2 data gaps of 3 h or
more (``data/raw/lasco_downtime/c2dt_YYYYMM.txt``, see its README). Each data line is::

    2012/05/03 22:12 - 2012/05/11 10:36

Lines starting with ``#`` are comments (a header, or the note that the month has no gap).
Intervals are merged across files (a gap that crosses a month boundary is listed in both
months), clipped to each calendar month, and turned into a covered fraction of the month.
A month without a published list has unknown coverage (NaN): it is never assumed complete.

Proxy coverage (diagnostic only)
--------------------------------
``monthly_coverage`` treats any interval of at least ``threshold_days`` between consecutive
catalogued CMEs as a gap. It finds the long SOHO outages but mistakes genuine quiet periods
at solar minimum for gaps, and misses gaps shorter than the threshold. It is kept as the
``coverage_fraction_proxy`` column for comparison (docs/DECISIONS.md, D-15 replaces D-06).
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

GAP_LINE = re.compile(r"^(\d{4}/\d{2}/\d{2} \d{2}:\d{2})\s*-\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2})$")
TIME_FORMAT = "%Y/%m/%d %H:%M"


# --------------------------------------------------------------------------- official
def parse_downtime_text(text: str, source: str = "<text>") -> pd.DataFrame:
    """Gap intervals in one CDAW downtime file. Raises on any non-comment line it cannot read."""
    rows = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = GAP_LINE.match(s)
        if not m:
            raise ValueError(f"{source}:{line_no}: cannot parse data-gap line {s!r}")
        start = pd.to_datetime(m[1], format=TIME_FORMAT)
        end = pd.to_datetime(m[2], format=TIME_FORMAT)
        if end < start:
            raise ValueError(f"{source}:{line_no}: gap ends before it starts: {s!r}")
        rows.append((start, end))
    return pd.DataFrame(rows, columns=["start", "end"])


def read_downtime_dir(directory: str | Path, manifest_sha256: str) -> tuple[pd.DataFrame, set[str]]:
    """Read every downloaded month listed in MANIFEST.csv, verifying each file's SHA-256.

    Returns (gap intervals, set of 'YYYY-MM' months that have an official list).
    """
    directory = Path(directory)
    manifest = directory / "MANIFEST.csv"
    actual = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if actual != manifest_sha256:
        raise ValueError(f"Checksum mismatch for {manifest}:\n  expected {manifest_sha256}\n  found    {actual}")
    frames, available = [], set()
    with open(manifest, newline="") as fh:
        for row in csv.DictReader(fh):
            if row["status"] != "200":
                continue
            path = directory / f"c2dt_{row['yearmonth']}.txt"
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError(f"{path} does not match its SHA-256 in {manifest.name}")
            frames.append(parse_downtime_text(data.decode("utf-8"), path.name))
            available.add(f"{row['yearmonth'][:4]}-{row['yearmonth'][4:]}")
    gaps = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["start", "end"])
    return gaps, available


def merge_intervals(gaps: pd.DataFrame) -> pd.DataFrame:
    """Union of possibly overlapping or duplicated intervals."""
    g = gaps.drop_duplicates().sort_values(["start", "end"])
    merged: list[list[pd.Timestamp]] = []
    for start, end in zip(g["start"], g["end"]):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return pd.DataFrame(merged, columns=["start", "end"])


def official_monthly_coverage(gaps: pd.DataFrame, months: pd.PeriodIndex,
                              available: set[str]) -> pd.DataFrame:
    """Covered fraction of each month from official gap intervals.

    Months not in ``available`` get NaN gap and coverage values.
    """
    merged = merge_intervals(gaps)
    rows = []
    for m in months:
        a, b = m.start_time, (m + 1).start_time
        ym = str(m)
        if ym not in available:
            rows.append({"yearmonth": ym, "days_in_month": m.days_in_month, "gap_days": np.nan,
                         "longest_gap_days": np.nan})
            continue
        lo = (merged["end"] > a) & (merged["start"] < b)
        pieces = [(min(e, b) - max(s, a)).total_seconds() / 86400
                  for s, e in zip(merged.loc[lo, "start"], merged.loc[lo, "end"])]
        rows.append({"yearmonth": ym, "days_in_month": m.days_in_month,
                     "gap_days": round(min(sum(pieces), m.days_in_month), 4),
                     "longest_gap_days": round(max(pieces), 4) if pieces else 0.0})
    out = pd.DataFrame(rows)
    out["coverage_fraction"] = (1 - out["gap_days"] / out["days_in_month"]).clip(0, 1).round(4)
    return out


# --------------------------------------------------------------------------- proxy
def gap_intervals(times: pd.Series, start: pd.Timestamp, end: pd.Timestamp,
                  threshold_days: float) -> pd.DataFrame:
    """Intervals of at least ``threshold_days`` with no catalogued CME, within [start, end]."""
    t = pd.concat([pd.Series([start]), times.sort_values(), pd.Series([end])]).reset_index(drop=True)
    gaps = pd.DataFrame({"start": t.iloc[:-1].values, "end": t.iloc[1:].values})
    gaps["days"] = (gaps["end"] - gaps["start"]).dt.total_seconds() / 86400
    return gaps[gaps["days"] >= threshold_days].reset_index(drop=True)


def monthly_coverage(times: pd.Series, months: pd.PeriodIndex, threshold_days: float) -> pd.DataFrame:
    """Proxy coverage from the spacing of catalogued CMEs (diagnostic only)."""
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
