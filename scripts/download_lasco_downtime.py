"""Download the monthly LASCO/C2 data-gap (downtime) lists from the CDAW catalog.

Run from the repository root, on a computer with normal internet access:

    python scripts/download_lasco_downtime.py              # all months, 1996-01 to 2026-07
    python scripts/download_lasco_downtime.py 201304 201305  # retry only these months

Files are saved unmodified to data/raw/lasco_downtime/c2dt_YYYYMM.txt. MANIFEST.csv keeps
one row per month (URL, HTTP status, size, SHA-256, download timestamp in UTC); a retry
replaces only the rows of the months it downloads. After each run the summary lines of
data/raw/lasco_downtime/README.md and data/raw/PROVENANCE.md (download dates, months
retrieved, months not available) are refreshed from the manifest.

Source pattern, taken from the link "Check for LASCO/C2 data gaps here" on each monthly
page of the catalog (e.g. UNIVERSAL_ver2/2022_12/univ2022_12.html):
    https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/downtime/c2dt_YYYYMM.txt
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/downtime/c2dt_{ym}.txt"
FIRST, LAST = (1996, 1), (2026, 7)          # same span as the versioned raw catalog
OUT = Path("data/raw/lasco_downtime")
MANIFEST = OUT / "MANIFEST.csv"
HEADER = ["yearmonth", "url", "status", "bytes", "sha256", "downloaded_utc"]
PAUSE_S = 1.0                               # be polite to the server


def all_months() -> list[str]:
    out, (y, m) = [], FIRST
    while (y, m) <= LAST:
        out.append(f"{y:04d}{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def fetch(ym: str) -> list:
    url = BASE.format(ym=ym)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data, status = r.read(), r.status
        (OUT / f"c2dt_{ym}.txt").write_bytes(data)
        print(f"{ym}  ok  {len(data):>7} bytes")
        return [ym, url, status, len(data), hashlib.sha256(data).hexdigest(), stamp]
    except urllib.error.HTTPError as e:
        print(f"{ym}  HTTP {e.code}")
        return [ym, url, e.code, "", "", stamp]
    except Exception as e:  # network errors: record and continue
        print(f"{ym}  error: {e}")
        return [ym, url, f"error: {e}", "", "", stamp]


def read_manifest() -> dict[str, list]:
    if not MANIFEST.exists():
        return {}
    with open(MANIFEST, newline="") as fh:
        return {r["yearmonth"]: [r[k] for k in HEADER] for r in csv.DictReader(fh)}


def refresh_docs(rows: list[list]) -> None:
    ok = [r for r in rows if str(r[2]) == "200"]
    missing = " ".join(r[0] for r in rows if str(r[2]) != "200") or "none"
    dates = sorted({str(r[5])[:10] for r in ok})
    when = dates[0] if len(dates) == 1 else ", ".join(dates)
    subs = {
        "README.md": [(r"^\| Download date \|.*$", f"| Download date | {when} (UTC; per-file timestamps in `MANIFEST.csv`) |"),
                      (r"^\| Files retrieved \|.*$", f"| Files retrieved | {len(ok)} of {len(rows)} months |"),
                      (r"^\| Not available \|.*$", f"| Not available | {missing} |")],
    }
    readme = OUT / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for pat, rep in subs["README.md"]:
            text = re.sub(pat, rep, text, flags=re.M)
        readme.write_text(text, encoding="utf-8")
    prov = Path("data/raw/PROVENANCE.md")
    if prov.exists():
        text = prov.read_text(encoding="utf-8")
        head, sep, section = text.partition("## LASCO/C2 data-gap lists")
        if sep:
            section = re.sub(r"^\| Download date \|.*$", f"| Download date | {when} |", section, count=1, flags=re.M)
            section = re.sub(r"^\| Retrieved \|.*$", f"| Retrieved | {len(ok)} of {len(rows)} months |", section, count=1, flags=re.M)
            section = re.sub(r"\(\d+ monthly files", f"({len(ok)} monthly files", section, count=1)
            prov.write_text(head + sep + section, encoding="utf-8")


def main(argv: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    valid = all_months()
    todo = argv or valid
    bad = [m for m in todo if m not in valid]
    if bad:
        sys.exit(f"Months outside {valid[0]}-{valid[-1]} or badly formatted (use YYYYMM): {bad}")
    manifest = read_manifest()
    for ym in todo:
        manifest[ym] = fetch(ym)
        time.sleep(PAUSE_S)
    rows = [manifest[m] for m in valid if m in manifest]
    with open(MANIFEST, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        w.writerows(rows)
    refresh_docs(rows)
    missing = [r[0] for r in rows if str(r[2]) != "200"]
    print(f"\n{len(rows) - len(missing)} of {len(rows)} months available; not available: {missing}")


if __name__ == "__main__":
    main(sys.argv[1:])
