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

Months without catalogued CMEs were previously zero-filled. Coverage now comes from the
official LASCO/C2 data-gap lists published by CDAW for each month (gaps of 3 h or more;
`data/raw/lasco_downtime/`, D-15). 366 of the 367 monthly lists were available at download
time; the list for 2026-07 was not yet published (HTTP 404), so that month has unknown
coverage and is unusable. The lists contain 1165 gap intervals; 30 cross a month boundary
and are clipped to each month without double counting.

Mean official coverage is 0.871 in 1996–2009 and 0.976 in 2010–2026-06. Unusable months
(> 50 % gap or no list): 1996-01 to 1996-04 (mission commissioning; coverage 0.03–0.38),
1998-07 to 1998-10 and 1999-01 (SOHO outages), and 2026-07. No month of the 2010-01 to
2026-06 test period is unusable. Three test-period months have coverage below 0.8: 2010-07
(0.78), 2010-08 (0.79) and 2012-05 (0.74).

Comparison with the provisional 5-day proxy used before D-15 (correlation 0.83; 59 months
differ by more than 0.1): the proxy missed gaps shorter than 5 days (e.g. 1996-03 to
1996-05, 2003-07, 2004-09, 2006-09 and 2009-02 have proxy coverage 0.93–1.00 but official
coverage 0.34–0.73) and marked genuine quiet periods at solar minimum as gaps (2018-06:
proxy 0.81, official 0.99; 2020-06: proxy 0.81, official 1.00). 2002-02 (coverage 0.77) is a
real gap.

Effect on the cycle ratios of Section 2: none of the newly unusable months falls in Cycles
23–25 as defined here, so the ratios computed from summed counts are unchanged. Because
mean coverage of usable months was lower in Cycle 23 (0.91) than in Cycles 24 and 25 (0.97
and 0.98), dividing by covered time instead
lowers the ratios relative to C23: fast 0.68 (C24/C23) and 1.04 (C25/C23); halos 1.39 and
1.25; all CMEs 1.62 and 0.97 (exploratory; exposure-adjusted figures used in the manuscript
will be produced by code).

## 4. Catalog versions

Between a copy of the catalog downloaded before 2026-01-30 and the current version,
5206 events from August 2019 to 2024 changed their MPA, 5032 their central PA and 79 their
angular width (correction announced by CDAW on 2026-01-30). Linear speeds did not change.
Results must therefore cite the catalog version used (see `data/raw/PROVENANCE.md`).

Between the February 2026 and July 2026 versions, the 42 744 events up to 2026-02-28 are
identical except for one event whose PA and width changed.

Between the July 2026 version and the version downloaded on 2026-11-14 (catalog header:
last updated 2026-11-12), the 43 440 events up to 2026-07-31 are identical in every field
except three changes, all in 2026: the event of 2026-04-15 11:48 changed from a partial halo
(width 259°) to a full halo (remark: width changed on 2026-11-03); the onset time of the
full halo of 2026-07-21 changed from 05:48 to 06:24 (changed on 2026-11-12); and one narrow
event was inserted on 2026-07-21 (inserted on 2026-11-12). No event of 2025 or earlier
changed. The November file adds 118 CMEs for 2026-08 and starts with three header lines that
the July file does not have.

Full halos in 2025 are therefore not a pending revision visible in this interval: the
catalog still lists 41 (102 in 2024). The low halo fraction among fast CMEs in 2025 (0.27)
has a precedent in 2022 (0.27; 2023–2024: 0.45–0.52). Whether it is physical or a feature of
the width measurements cannot be decided from the catalog alone.

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

- Treatment of LASCO/C3 data gaps (the official lists used here cover C2 only).
- Archive of historical sunspot-number forecasts with issue dates (for verifying forecasts
  that use a predicted, rather than observed, sunspot number).
