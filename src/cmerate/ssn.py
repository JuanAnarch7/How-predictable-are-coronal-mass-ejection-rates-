"""Read the SILSO monthly mean total sunspot number, version 2.0 (SN_m_tot_V2.0).

SILSO distributes the file as semicolon-separated CSV or whitespace-separated text with
the same seven columns:

1. year  2. month  3. decimal date  4. monthly mean total sunspot number
5. monthly mean standard deviation  6. number of observations
7. definitive/provisional marker (1 = definitive, 0 = provisional)

Missing values are coded -1. Column meanings follow the SILSO file description and must
be re-checked against https://www.sidc.be/SILSO/ whenever a new file is downloaded.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["year", "month", "decimal_date", "ssn", "ssn_std", "n_obs", "definitive"]


def read_ssn(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    sep = ";" if ";" in text.splitlines()[0] else r"\s+"
    df = pd.read_csv(path, sep=sep, header=None, engine="python")
    if df.shape[1] != len(COLUMNS):
        raise ValueError(f"{path} has {df.shape[1]} columns; SN_m_tot_V2.0 has {len(COLUMNS)}")
    df.columns = COLUMNS
    if not df["month"].between(1, 12).all() or not df["definitive"].isin([0, 1]).all():
        raise ValueError(f"{path} does not look like SN_m_tot_V2.0")
    df["yearmonth"] = (df["year"].astype(int).astype(str) + "-"
                       + df["month"].astype(int).astype(str).str.zfill(2))
    df["ssn"] = df["ssn"].where(df["ssn"] >= 0, np.nan)
    df["ssn_std"] = df["ssn_std"].where(df["ssn_std"] >= 0, np.nan)
    df["ssn_provisional"] = df["definitive"].astype(int) == 0
    return df[["yearmonth", "ssn", "ssn_std", "n_obs", "ssn_provisional"]]
