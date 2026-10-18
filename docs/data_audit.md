# Data audit

Audit of the CME catalog data used in this project, carried out before any modelling.
Figures refer to the raw file `data/raw/cdaw_univ_all_2026-07-31.txt` unless stated.
The regression tests in `tests/test_dataset.py` pin the main figures.

## 1. Parsing the catalog

Each line of the CDAW text list has 12 whitespace-separated fields followed by a free-text
remark that may contain spaces. The previous pipeline split every line on all whitespace,
which kept only the **first word** of the remark. Quality flags usually follow other notes
(e.g. `Only C3; Poor Event`, `Faint; Very Poor Event; Only 2 points`, and from August 2019
`Fixed the PA issue on 2026-01-30; Poor Event`), so most flags were lost.

`src/cmerate/cdaw.py` splits each line at most 12 times and keeps the remark whole. All
43 440 lines parse; any unparseable line stops the pipeline.

Checks against the author's previously processed file for the same catalog version:
identical date, time, central PA, width, linear speed and MPA for all 43 440 events.

## 2. Quality flags and homogeneity of the total count

Fraction of events flagged "Poor Event" or "Very Poor Event", by period:

| Period | Flagged |
|---|---|
| 1996–1997 | 69–85 % |
| 1998–2005 | 31–52 % |
| 2006–2009 | 72–89 % |
| 2010–2017 | 66–76 % |
| 2018–2020 | 86–92 % |
| 2021–2026 | 62–77 % |

Overall 63.5 % of events are flagged, but only 8.7 % of fast CMEs (V ≥ 1000 km/s) and
13.5 % of full halos.

CMEs per unit sunspot number relative to Solar Cycle 23 (sum of counts / sum of monthly
SSN over usable months; versioned SILSO file `data/raw/SN_m_tot_V2.0.csv`; cycle boundaries
as in `config/config.toml`; 146, 132 and 79 months for C23, C24 and C25, the last up to
2026-06, the last definitive SSN month):

| Set | C24/C23 | C25/C23 |
|---|---|---|
| All CMEs | 1.72 | 1.03 |
| All, excluding flagged | 0.97 | 0.61 |
| Flagged only | 2.44 | 1.43 |
| Fast (≥ 1000 km/s) | 0.73 | 1.11 |
| Fast, excluding flagged | 0.73 | 1.04 |
| Halo | 1.48 | 1.33 |
| Halo, excluding flagged | 1.35 | 1.16 |
| Wide (120–360°) | 1.97 | 1.63 |
| Wide, excluding flagged | 1.81 | 1.43 |

> Caveats: (1) an earlier, unversioned SSN copy gave values within 0.03 of these.
> (2) The ratios move by up to ~0.15 depending on which months are excluded (e.g.
> excluding every month with any 5-day gap gives 1.58 and 0.91 for the first two rows);
> the qualitative conclusions below hold in all variants tried. (3) These are exploratory
> figures; any ratio quoted in the manuscript will be produced by code.

Interpretation:
- The apparent excess of CMEs per sunspot in Cycle 24 in the total count comes mostly from
  flagged (low-quality) events; without them the ratio is close to 1. The total count is
  therefore not a homogeneous series across cycles.
- Fast CMEs are insensitive to the quality flags, which makes them the most robust target.
  Their ratio to the SSN still changes between cycles.
- The excess of wide CMEs in Cycle 24 persists without flagged events and may have a
  physical origin (literature to be checked).

## 3. Observing gaps

Months without catalogued CMEs were previously zero-filled. Gaps found from the spacing
of consecutive events:
- no data: 1998-07, 1998-08, 1998-09, 1999-01 (SOHO outages);
- partial months: 1998-06, 1998-10, 1998-11, 1998-12, 1999-02;
- 7–10-day gaps during high activity: Sep–Oct 1999, Jun–Jul 2003, Apr 2004, May 2012.

The current coverage measure (`src/cmerate/coverage.py`) treats any interval of at least
5 days without catalogued CMEs as a gap. It is a **provisional proxy**: during solar minima
such intervals can be genuine quiet periods. It will be replaced by the official LASCO
data-gap information before coverage is used as an exposure term.

Counts in months with more than 50 % gap are set to missing (6 months).

## 4. Catalog versions

Between a copy of the catalog downloaded before 2026-01-30 and the current version,
5206 events from August 2019 to 2024 changed their MPA, 5032 their central PA and 79 their
angular width (correction announced by CDAW on 2026-01-30). Linear speeds did not change.
Results must therefore cite the catalog version used (see `data/raw/PROVENANCE.md`).

Between the February 2026 and July 2026 versions, the 42 744 events up to 2026-02-28 are
identical except for one event whose PA and width changed.

## 5. Other findings

- 119 events have no linear speed. They are kept, counted in the total and reported
  separately (`n_speed_missing`); they belong to no speed-defined subpopulation.
- Events with width < 20° (28 %) belonged to no width class in the previous subpopulation
  scheme; the current scheme does not partition by width.
- 2025 contains 70 fast CMEs in the current catalog (65 in January–November).
- July 2026 has 146 CMEs and no fast CME; the most recent months may still be incomplete
  and are not used for verification until confirmed with a later download.

## 6. Sunspot number

The SILSO file `SN_m_tot_V2.0.csv` (downloaded 2026-10-18) covers 1749-01 to 2026-09;
values from 2026-07 onwards are provisional. Compared with the copy used by the previous
repository, 360 of 362 common months are identical; January and February 2026 were revised
(112.5 → 115.0 and 78.2 → 77.4). Provisional values therefore change, and forecasts
verified retrospectively must account for which SSN values were available at each issue
date.

The solar-cycle minima used as cycle boundaries (1996-05, 2008-12, 2019-12) are the minima
of the 13-month smoothed SSN computed from this file (11.2, 2.2 and 1.8); a regression test
checks them.

## 7. Pending

- Official LASCO data-gap information.
- Archive of historical sunspot-number forecasts with issue dates (for verifying forecasts
  that use a predicted, rather than observed, sunspot number).
