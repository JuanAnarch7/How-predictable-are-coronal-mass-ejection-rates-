# Decision log

Every choice that can change a result is recorded here, with its status. Once the
evaluation protocol (F1) is frozen, changes to frozen items must be justified and dated,
and the manuscript must report them.

| ID | Decision | Status | Date |
|---|---|---|---|
| D-01 | The sunspot number is the only exogenous predictor. Active-region properties are out of scope. | decided | 2026-10-17 |
| D-02 | Forecasts use only information available at the issue date. Observed SSN for the forecast period is never an input. | decided | 2026-10-17 |
| D-03 | Dataset based on the CDAW catalog version with coverage to 2026-07-31 (`data/raw/PROVENANCE.md`). | decided | 2026-10-18 |
| D-04 | Catalog parsed keeping the full remark; quality flags ("Poor Event", "Very Poor Event") stored per event. | decided | 2026-10-18 |
| D-05 | Targets of the main analysis: fast CMEs (V ≥ 1000 km/s) and full halos (W = 360°), each also reported without flagged events. Total count and wide CMEs are not analysed in this article. | decided (with S. Vargas) | 2026-11-13 |
| D-06 | Observing coverage from a 5-day gap proxy; months with > 50 % gap set to missing. | superseded by D-15 | 2026-10-18 |
| D-07 | Solar-cycle boundaries 1996-05, 2008-12, 2019-12: minima of the 13-month smoothed SSN from the versioned SILSO file (checked by a test). | decided | 2026-10-18 |
| D-08 | SILSO SN_m_tot_V2.0 file downloaded 2026-10-18 (`data/raw/PROVENANCE.md`). | decided | 2026-10-18 |
| D-09 | Source of historical SSN forecasts with issue dates (NOAA/NASA 2019 panel, reconstructed SILSO methods, SILSO archive). | **pending** | — |
| D-10 | Annual series derived from the monthly table (never built separately). Annual verification by 12-month-ahead totals issued monthly. | decided (verification details in F1) | 2026-10-17 |
| D-11 | Events without linear speed are kept and counted in the total only. | decided | 2026-10-18 |
| D-12 | Width boundaries inclusive: wide = 120° ≤ W ≤ 360°; halo = W = 360°. Speed boundary inclusive: fast = V ≥ 1000 km/s. | decided | 2026-10-18 |
| D-13 | Configuration in TOML (Python standard library); code tested with Python 3.13, pandas 3.0.5, numpy 2.5.3. | decided | 2026-10-18 |
| D-14 | Working title provisional; final title after results (F3). | provisional | 2026-10-18 |
| D-15 | Observing coverage from the official LASCO/C2 data-gap lists published by CDAW (gaps ≥ 3 h; `data/raw/lasco_downtime/`, downloaded 2026-11-13/14). Months with > 50 % of the time in gaps, or with no published list, are unusable (counts set to missing); other months keep their counts and use the covered fraction as exposure. The 5-day proxy is kept only as the diagnostic column `coverage_fraction_proxy`. C2 gaps only; the treatment of C3 gaps is pending. | decided | 2026-11-14 |
