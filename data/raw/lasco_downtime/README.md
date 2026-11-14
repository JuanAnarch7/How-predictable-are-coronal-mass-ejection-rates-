# Official LASCO/C2 data-gap lists (CDAW)

Monthly lists of LASCO/C2 data gaps of 3 h or more, published by the CDAW Data Center with
the SOHO/LASCO CME Catalog. The catalog states that the data-gap list must be consulted
before deciding whether CMEs occurred during a period.

| Field | Value |
|---|---|
| Files | `c2dt_YYYYMM.txt`, one per month, 1996-01 to 2026-07 |
| Source | `https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/downtime/c2dt_YYYYMM.txt` (linked from each monthly page of the catalog) |
| Downloaded with | `scripts/download_lasco_downtime.py` |
| Download date | 2026-11-13 (UTC; per-file timestamps in `MANIFEST.csv`) |
| Files retrieved | 362 of 367 months |
| Not available | 201304 201305 201306 201307 202607  |
| Checksums | SHA-256 of every file in `MANIFEST.csv` |

Files are stored exactly as downloaded. Never edit them; a new download goes to a new
folder with its own manifest.

Use: replaces the provisional 5-day coverage proxy (`src/cmerate/coverage.py`,
docs/DECISIONS.md D-06) as the source of the monthly observing coverage. The lists cover
C2 only; how C3 gaps are treated is recorded in docs/DECISIONS.md.
