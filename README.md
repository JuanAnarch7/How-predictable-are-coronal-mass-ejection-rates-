# CME rate forecast verification

Data pipeline and forecast-verification framework for monthly and annual coronal mass
ejection (CME) occurrence rates from the SOHO/LASCO CDAW catalog, using the sunspot
number as the only exogenous predictor.

**Working title of the accompanying paper (provisional):**
*Probabilistic forecasts of monthly and annual CME rates from the sunspot number: a
reproducible verification framework.*

> **Status: data stage.** The dataset is built, audited and tested. The evaluation
> protocol, models and results are not yet in the repository (see [Roadmap](#roadmap)).

## Principles

1. **Issue-time information only.** A forecast may use only data available at its issue
   date. No observed sunspot number from the forecast period is ever used as an input.
2. **Every number is generated.** Tables, figures and every figure quoted in the
   manuscript come from code. Numbers reach the LaTeX source through
   `manuscript/generated/numbers.tex`; nothing is typed by hand.
3. **One configuration file.** Dates, thresholds, subpopulations and file versions live in
   `config/config.toml`. Changes are logged in `docs/DECISIONS.md`.
4. **Versioned raw data.** Raw files are stored unmodified, with download date and SHA-256
   in `data/raw/PROVENANCE.md`. The pipeline refuses to run on a file whose checksum does
   not match the configuration.
5. **Gaps are not zeros.** Months without observations are reported as missing, never as
   months with no CMEs.

## Repository layout

```
config/config.toml          single source of truth for all choices
data/raw/                   raw files exactly as downloaded + PROVENANCE.md
data/processed/             generated tables (never edited by hand)
src/cmerate/                Python package: parsing, coverage, tables, numbers export
scripts/build_dataset.py    raw files -> processed tables + numbers
tests/                      unit tests and regression tests on the real catalog
results/                    numbers.json, tables, figures (generated)
manuscript/                 LaTeX source; generated/numbers.tex holds all quoted numbers
docs/                       data audit, decision log, changes from the previous repository
```

## Quick start

Requires Python ≥ 3.11.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh            # build the dataset and run the tests
```

`run_all.sh` runs `python scripts/build_dataset.py` and then
`python -m unittest discover -s tests`. The tests also work with `pytest`.

## Data

| Source | File | Coverage |
|---|---|---|
| SOHO/LASCO CDAW CME catalog, universal list (text) | `data/raw/cdaw_univ_all_2026-07-31.txt` | 1996-01-11 to 2026-07-31, 43 440 CMEs |
| SILSO monthly mean total sunspot number V2.0 | `data/raw/SN_m_tot_V2.0.csv` | *pending* |

Processed outputs:

| File | Content |
|---|---|
| `data/processed/cme_events.csv` | one row per CME, full remarks, quality and uncertainty flags (regenerated, not committed) |
| `data/processed/cme_monthly.csv` | monthly counts per subpopulation, with and without quality-flagged events; coverage; SSN; cycle label |
| `data/processed/cme_annual.csv` | calendar-year totals derived from the monthly table; coverage fraction |

Subpopulations (configurable): all CMEs; fast (V ≥ 1000 km/s); full halo (W = 360°);
wide (120° ≤ W ≤ 360°). Each is also counted excluding events flagged "Poor Event" or
"Very Poor Event" by the catalog (`_good` columns).

See `docs/data_audit.md` for the checks behind these choices, including the
inhomogeneity of the total CME count across solar cycles.

## Roadmap

| Stage | Content | Status |
|---|---|---|
| F0 | Data audit and versioned dataset | done (SSN file and official gap list pending) |
| F1 | Evaluation protocol: rolling-origin and leave-one-cycle-out validation, horizons, baselines, metrics | next |
| F2 | Models: persistence, climatology, cycle-phase analogues, Poisson/negative-binomial GLMs on SSN, ARIMA/ARIMAX for comparison | — |
| F3 | Results and figures | — |
| F4 | Manuscript | — |
| F5 | Submission and Zenodo release | — |

## Relation to the previous repository

This repository supersedes
[Forecasting-Coronal-Mass-Ejection-Occurrence-Rates-Using-ARIMA-and-ARIMAX-Models](https://github.com/JuanAnarch7/Forecasting-Coronal-Mass-Ejection-Occurrence-Rates-Using-ARIMA-and-ARIMAX-Models).
What changed and why is documented in `docs/CHANGES_FROM_PREVIOUS.md`.

## Citation and license

Citation metadata: `CITATION.cff` (a Zenodo DOI will be added at release).
Code under the MIT License (`LICENSE`). The CDAW catalog and SILSO data remain subject
to their providers' terms and acknowledgement requests.
