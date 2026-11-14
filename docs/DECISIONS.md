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
| D-09 | Forecast SSN (information set I2): pseudo-operational forecasts reconstructed at each issue date with a scaled mean-cycle method (main), plus the NOAA/NASA Solar Cycle 25 panel forecast of December 2019 as a case study (`docs/PROTOCOL.md` §5). | decided | 2026-11-14 |
| D-10 | Annual series derived from the monthly table (never built separately). Annual verification by 12-month-ahead totals issued monthly (primary) and calendar-year totals issued in January (descriptive), see D-19. | decided | 2026-10-17 |
| D-11 | Events without linear speed are kept and counted in the total only. | decided | 2026-10-18 |
| D-12 | Width boundaries inclusive: wide = 120° ≤ W ≤ 360°; halo = W = 360°. Speed boundary inclusive: fast = V ≥ 1000 km/s. | decided | 2026-10-18 |
| D-13 | Configuration in TOML (Python standard library); code tested with Python 3.13, pandas 3.0.5, numpy 2.5.3. | decided | 2026-10-18 |
| D-14 | Working title provisional; final title after results (F3). | provisional | 2026-10-18 |
| D-15 | Observing coverage from the official LASCO/C2 data-gap lists published by CDAW (gaps ≥ 3 h; `data/raw/lasco_downtime/`, downloaded 2026-11-13/14). Months with > 50 % of the time in gaps, or with no published list, are unusable (counts set to missing); other months keep their counts and use the covered fraction as exposure. The 5-day proxy is kept only as the diagnostic column `coverage_fraction_proxy`. C2 gaps only; the treatment of C3 gaps is pending. | decided | 2026-11-14 |
| D-16 | Evaluation protocol in `docs/PROTOCOL.md`, settings in `config/protocol.toml` (TOML, as D-13). Frozen in two steps: `protocol-v1.0` (document + settings, Zenodo) before implementing models; `code-v1.0` before scoring the 2010–2026 test period. | decided | 2026-11-14 |
| D-17 | Reference set for the primary comparison: persistence, MA3, MA12 and the cycle-phase analogue; skill against the best of them on the evaluated set. The SSN-only regression is an I1 competitor, compared with the main model as a secondary analysis. | decided | 2026-11-14 |
| D-18 | Horizons: monthly h = 1 (control), 6, 12 on a common target set (2010-01 to 2026-06); h = 3 supplementary only. The SSN contribution by horizon is a pre-specified estimate, not a test. | decided | 2026-11-14 |
| D-19 | Primary comparison P1 (fast, halo): main model NB-hist+SSN versus the best reference, 12-month totals issued monthly; one-sided Diebold–Mariano statistic with simulation-calibrated critical values; Holm over the two subpopulations. P3 (forecast SSN) is a pre-specified estimate. Calendar-year totals are descriptive. | decided | 2026-11-14 |
| D-20 | Targets: every usable month (coverage ≥ 0.5), with coverage as exposure; 12-month and calendar-year totals verified when window coverage ≥ 0.9. Sensitivity excluding months with coverage < 0.8. | decided | 2026-11-14 |
| D-21 | Catalog latency sensitivity L = 1, 3 months (L = 0 main); a cycle minimum is known 12 months after it occurs; calibration acceptable when 80 % coverage is in 0.70–0.90; Brier score of active years descriptive; post-freeze verification with later catalog downloads; retrospective verification of published forecasts out of scope. | decided | 2026-11-14 |
| D-22 | LASCO/C3 gaps not available: C2 coverage used for all events (declared limitation). Pre-specified sensitivity for halos without the 2025 targets. | decided | 2026-11-14 |
| D-23 | ARIMA/ARIMAX models are not part of the evaluation. The connection with the previous manuscript is made through the information sets (its ARIMAX used the observed SSN of the forecast period, i.e. the I★ upper bound). | decided | 2026-11-14 |
| D-24 | Scaled mean-cycle SSN forecasts (I2): cut-off year of the reference cycles (1855 or 1940) and scaling window (24 months or the whole current cycle) chosen by a backtest of SSN forecasts issued 1960–2009 (lowest CRPS of the next-12-month mean SSN; ties to 1855/24). The SSN after 2009 is not used for the choice. | decided (rule); variant fixed before `code-v1.0` | 2026-11-14 |
| D-25 | Critical values of P1 calibrated with two null generators, fitted to 1996–2009 (main) and to 1996–2026-06 (control); the larger critical value is used and both are reported. | decided | 2026-11-14 |
