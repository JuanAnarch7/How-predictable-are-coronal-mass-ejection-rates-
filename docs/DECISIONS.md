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
| D-05 | Primary target: fast CMEs (V ≥ 1000 km/s). Secondary: full halos, wide CMEs (120–360°), total count; each with and without flagged events. | **pending author confirmation** | — |
| D-06 | Observing coverage from a 5-day gap proxy; months with > 50 % gap set to missing. To be replaced by official LASCO gap information. | provisional | 2026-10-18 |
| D-07 | Solar-cycle boundaries 1996-05, 2008-12, 2019-12. To be checked against SILSO minima. | provisional | 2026-10-18 |
| D-08 | SILSO SN_m_tot_V2.0 file: version and download date. | Decided | 2026-10-18 |
| D-09 | Source of historical SSN forecasts with issue dates (NOAA/NASA 2019 panel, reconstructed SILSO methods, SILSO archive). | **pending** | — |
| D-10 | Annual series derived from the monthly table (never built separately). Annual verification by 12-month-ahead totals issued monthly. | decided (verification details in F1) | 2026-10-17 |
| D-11 | Events without linear speed are kept and counted in the total only. | decided | 2026-10-18 |
| D-12 | Width boundaries inclusive: wide = 120° ≤ W ≤ 360°; halo = W = 360°. Speed boundary inclusive: fast = V ≥ 1000 km/s. | decided | 2026-10-18 |
| D-13 | Configuration in TOML (Python standard library); code tested with Python 3.13, pandas 3.0.5, numpy 2.5.3. | decided | 2026-10-18 |
| D-14 | Working title provisional; final title after results (F3). | provisional | 2026-10-18 |
