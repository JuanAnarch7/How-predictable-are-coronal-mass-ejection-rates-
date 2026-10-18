"""Parse the SOHO/LASCO CDAW universal CME list (text version).

Each data line has 12 whitespace-separated fields followed by a free-text remark that
can contain spaces, for example::

    1996/01/22  03:11:01  105  37  267  401  130  0  -126.3*  7.1e+13*  2.5e+28*  103  Very Poor Event; Only C3

The line is split at most 12 times so that the remark is kept whole. Splitting on every
space (as the previous pipeline did) keeps only the first word of the remark and loses
the quality flags, which usually come after other notes.

Conventions
-----------
* ``Halo`` in the central position angle field means a full halo: ``halo_cpa`` is True
  and ``cpa`` is NaN.
* Dashes (``----``, ``-------``) mean the quantity was not measured: NaN.
* A trailing ``*`` marks an uncertain value: the number is kept and ``<field>_uncertain``
  is set to True.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

FIELDS = ["date", "time", "cpa", "width", "v_lin", "v2_init", "v2_final", "v2_20rs",
          "accel", "mass", "kin_energy", "mpa"]
NUMERIC = FIELDS[2:]
UNCERTAIN_FLAGGABLE = ["accel", "mass", "kin_energy"]

FEW_POINTS = re.compile(r"only\s+(?:\d+|one|two|three)\s+points?", re.IGNORECASE)


def _to_number(token: str) -> tuple[float, bool]:
    uncertain = token.endswith("*")
    token = token.rstrip("*")
    try:
        return float(token), uncertain
    except ValueError:
        return np.nan, uncertain


def parse_line(line: str) -> dict | None:
    """Parse one catalog line. Returns None for blank or non-data lines."""
    parts = line.rstrip("\n").split(None, len(FIELDS))
    if len(parts) < len(FIELDS) or not re.fullmatch(r"\d{4}/\d{2}/\d{2}", parts[0]):
        return None
    rec = dict(zip(FIELDS, parts[: len(FIELDS)]))
    rec["remarks"] = parts[len(FIELDS)].strip() if len(parts) > len(FIELDS) else ""
    rec["halo_cpa"] = rec["cpa"].strip().lower() == "halo"
    for field in NUMERIC:
        value, uncertain = _to_number(rec[field])
        rec[field] = value
        if field in UNCERTAIN_FLAGGABLE:
            rec[f"{field}_uncertain"] = uncertain
    return rec


def add_remark_flags(df: pd.DataFrame) -> pd.DataFrame:
    r = df["remarks"].str.lower()
    df["very_poor"] = r.str.contains("very poor event", regex=False)
    df["poor"] = r.str.contains("poor event", regex=False) & ~df["very_poor"]
    df["quality_flagged"] = df["poor"] | df["very_poor"]
    df["only_c2"] = r.str.contains("only c2", regex=False)
    df["only_c3"] = r.str.contains("only c3", regex=False)
    df["few_points"] = r.str.contains(FEW_POINTS)
    return df


def read_catalog(path: str | Path) -> pd.DataFrame:
    """Read the raw catalog file. Raises if any non-blank line cannot be parsed."""
    rows, rejected = [], []
    with open(path, encoding="utf-8", errors="strict") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            rec = parse_line(line)
            if rec is None:
                rejected.append((line_no, line.rstrip()))
                continue
            rec["raw_line"] = line_no
            rows.append(rec)
    if rejected:
        sample = "\n".join(f"  line {n}: {t[:100]}" for n, t in rejected[:5])
        raise ValueError(f"{len(rejected)} unparseable lines in {path}:\n{sample}")

    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y/%m/%d %H:%M:%S")
    df = df.drop(columns=["date", "time"])
    df = add_remark_flags(df)
    first = ["raw_line", "datetime", "halo_cpa"]
    return df[first + [c for c in df.columns if c not in first]]
