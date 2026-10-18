# Changes from the previous repository

Previous repository:
[Forecasting-Coronal-Mass-Ejection-Occurrence-Rates-Using-ARIMA-and-ARIMAX-Models](https://github.com/JuanAnarch7/Forecasting-Coronal-Mass-Ejection-Occurrence-Rates-Using-ARIMA-and-ARIMAX-Models)
(last commit 9d2c4df, 2026-06-02). It remains available unchanged for reference.

## Forecast design

| Previous | Now | Why |
|---|---|---|
| ARIMAX/SARIMAX used the observed sunspot number of the forecast period ("nowcasting"). | Only information available at the issue date is used; the cost of forecasting the SSN itself is measured explicitly. | The observed SSN of a future period is not available when a forecast is issued, so the earlier skill was not forecast skill. |
| ARIMA (no SSN) compared with ARIMAX (observed SSN). | All models receive the same information. | A fair comparison needs equal inputs. |
| No baselines. | Persistence, climatology, cycle-phase analogues and a regression/GLM on the SSN are mandatory baselines. | A simple regression on the SSN performed as well as ARIMAX; skill must be shown relative to simple references. |
| One-step-ahead in-sample fits shown as forecasting ability. | Multi-step out-of-sample forecasts only, with rolling origin and leave-one-cycle-out validation. | In-sample one-step fits track the series by construction. |
| Improvements reported as percentage changes of \|R²\|. | Skill scores relative to baselines; probabilistic verification. | Relative changes of R² are not interpretable. |
| Annual test period of 5 points. | 12-month-ahead totals issued every month. | More, and genuinely out-of-sample, verification points. |

## Data

| Previous | Now | Why |
|---|---|---|
| Catalog remarks truncated to their first word. | Full remark kept; quality flags stored per event. | Quality flags were lost (see `docs/data_audit.md`). |
| Months without data counted as zero CMEs. | Gaps reported as missing; coverage recorded per month. | A gap is not an absence of CMEs. |
| Raw files not stored; file names did not identify the catalog version. | Raw files stored with download date and SHA-256; pipeline checks the checksum. | The catalog changes between versions. |
| Subpopulation definitions differed between manuscript and code (120° boundary, "fast" range). | Defined once in `config/config.toml`, inclusive boundaries, tested. | Consistency between text and code. |
| Text, tables and figures edited by hand. | Every quoted number generated into `manuscript/generated/numbers.tex`. | Several discrepancies between text and code were found in the previous version. |
| README stated that incomplete events were removed; the code removed none. | Events without speed kept and counted separately; documented. | Documentation must match the code. |
