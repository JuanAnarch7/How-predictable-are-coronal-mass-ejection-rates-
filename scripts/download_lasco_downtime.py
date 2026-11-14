"""Download the monthly LASCO/C2 data-gap (downtime) lists from the CDAW catalog.

Run from the repository root, on a computer with normal internet access:

    python scripts/download_lasco_downtime.py

Files are saved unmodified to data/raw/lasco_downtime/c2dt_YYYYMM.txt, together with a
MANIFEST.csv (month, URL, HTTP status, size, SHA-256, download timestamp in UTC).
The files are not parsed here: the parser is written after inspecting the real format.

Source pattern, taken from the link "Check for LASCO/C2 data gaps here" on each monthly
page of the catalog (e.g. UNIVERSAL_ver2/2022_12/univ2022_12.html):
    https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/downtime/c2dt_YYYYMM.txt
"""
from __future__ import annotations

import csv
import hashlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/downtime/c2dt_{ym}.txt"
FIRST, LAST = (1996, 1), (2026, 7)          # same span as the versioned raw catalog
OUT = Path("data/raw/lasco_downtime")
PAUSE_S = 1.0                               # be polite to the server


def months():
    y, m = FIRST
    while (y, m) <= LAST:
        yield f"{y:04d}{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for ym in months():
        url = BASE.format(ym=ym)
        path = OUT / f"c2dt_{ym}.txt"
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data, status = r.read(), r.status
            path.write_bytes(data)
            rows.append([ym, url, status, len(data), hashlib.sha256(data).hexdigest(), stamp])
            print(f"{ym}  ok  {len(data):>7} bytes")
        except urllib.error.HTTPError as e:
            rows.append([ym, url, e.code, "", "", stamp])
            print(f"{ym}  HTTP {e.code}")
        except Exception as e:  # network errors: record and continue
            rows.append([ym, url, f"error: {e}", "", "", stamp])
            print(f"{ym}  error: {e}")
        time.sleep(PAUSE_S)
    with open(OUT / "MANIFEST.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["yearmonth", "url", "status", "bytes", "sha256", "downloaded_utc"])
        w.writerows(rows)
    missing = [r[0] for r in rows if r[2] != 200]
    print(f"\n{len(rows) - len(missing)} files saved; {len(missing)} not available: {missing}")


if __name__ == "__main__":
    main()
