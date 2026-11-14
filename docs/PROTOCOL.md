# Evaluation protocol

**Version:** protocol-v1.0 (draft, not yet tagged) · **Machine-readable settings:** `config/protocol.toml`
**Changes after tagging:** `docs/PROTOCOL_CHANGES.md` · **Decision log:** `docs/DECISIONS.md`

This document fixes, before the definitive evaluation is run, what is forecast, with which
information, against which references and with which metrics and tests. Everything the code
needs is in `config/protocol.toml`; the code has no analysis options outside that file.

## 0. Freezing

The protocol is frozen in two steps:

1. **`protocol-v1.0`**: this document and `config/protocol.toml` are tagged in git and
   deposited on Zenodo (verifiable date) before any model is implemented.
2. **`code-v1.0`**: the forecasting and verification code is implemented, validated on
   synthetic data and on data up to 2009-12 only, and tagged before it is run on the
   2010–2026 test period. Results files record both tags and the SHA-256 of
   `config/protocol.toml`.

Any later change is recorded in `docs/PROTOCOL_CHANGES.md` (date, what changes, why,
whether results had been seen) and produces a new tag; results of every version are kept.
New analyses are allowed but are labelled exploratory.

**Honesty note.** Exploratory analyses (October 2026) already scored comparisons similar to
the primary one on the 2010–2026 period. The protocol cannot make them blind. It guarantees
that the specification is not tuned to them, and the post-freeze verification (Section 12)
re-measures them on data nobody has seen. The comparison with forecast SSN (P3) is blind.

## 1. Questions

| | Question | Role |
|---|---|---|
| OE1 | With information available at the issue date, does the model beat simple history-based references? | Confirmatory (P1) |
| OE2 | How does skill, and the contribution of the SSN, change with the horizon? | Pre-specified estimate |
| OE3 | How much of the gap to the oracle (observed future SSN) is recovered with a *forecast* SSN? | Pre-specified estimate (P3) |
| OE4 | Does the CME–SSN relation learned in one cycle transfer to another? | Descriptive |
| OE5 | Prospective forecast with explicit issue date and full uncertainty | Issued, verified later |

## 2. Data and periods

| Item | Value |
|---|---|
| CME catalog | CDAW universal list, `data/raw/cdaw_univ_all_2026-07-31.txt` (SHA-256 in `config/config.toml`) |
| Sunspot number | SILSO monthly mean total SSN V2.0, `data/raw/SN_m_tot_V2.0.csv`, downloaded 2026-10-18 |
| Coverage | Official LASCO/C2 data-gap lists (D-15). C3 gaps are not available; C2 coverage is used for all events and this is declared as a limitation |
| Targets | **fast**: linear speed ≥ 1000 km/s; **halo**: angular width = 360° (D-05, D-12). Both also reported without events flagged "Poor"/"Very Poor" (supplementary) |
| Training data start | 1996-01 (unusable months are missing, never zero) |
| Test targets | 2010-01 to 2026-06 (198 months, all usable) |
| Cycle boundaries | 1996-05, 2008-12, 2019-12 (D-07) |

Unusable months (coverage unknown or more than 50 % of the month in data gaps) are never
targets and enter predictors only through exposure-adjusted rates.

## 3. Information at the issue date

**Issue convention.** A forecast "issued at t" is issued on the first day of month t+1 and
uses data up to the end of month t: the CME counts of months ≤ t (≤ t−L in the latency
sensitivity) and the monthly SSN of months ≤ t.

The exercise is **pseudo-operational**: it respects the chronology of the data but uses
their current versions.

| Datum | Used | Existed at t | Treatment |
|---|---|---|---|
| CME counts | July 2026 catalog | An earlier, possibly incomplete version | Latency sensitivity L = 0 (main), 1, 3 months. CDAW revised a 2026-04 event in 2026-11 (data audit §4) |
| Speeds and widths | Current version | Version of the time | No speed changed between the versions compared; older versions cannot be checked (declared) |
| SSN up to t | SILSO V2.0 definitive | Provisional value; V1.0 scale before 2015-07 | Declared limitation: slight optimism of I1 |
| Forecast SSN (I2) | Reconstructed with data up to t; NOAA/NASA 2019 panel | Forecasts actually issued | Reconstructions declared pseudo-operational; the panel is the only genuinely historical forecast |
| Cycle minima | Dates known today | Confirmed months later | A minimum counts as known **12 months** after it occurs |

## 4. Forecast targets and horizons

| Target | Definition | Issues | Role |
|---|---|---|---|
| **12-month total** | Sum of counts in months t+1…t+12 | Every month, 2009-12 to 2025-06 (187) | **Primary** |
| Monthly count, h = 1, 6, 12 | Count in month t+h | Common target set 2010-01 to 2026-06; issue t = target − h | Secondary (h = 1 is a control) |
| Calendar-year total | Sum over the next calendar year | Each January (data to December), years 2010–2025 (16) | Descriptive, non-overlapping check |
| h = 3 | Monthly count | As above | Supplementary only |

**Exposure (D-15, decision 4).** Every usable month is a target; its coverage fraction is the
exposure (offset in the models; references forecast rate × exposure). A 12-month or
calendar-year total is verified when the covered fraction of its window is ≥ 0.9, with the
summed exposure. Sensitivity: excluding months with coverage < 0.8 (in the test period:
2010-07, 2010-08, 2012-05).

A direct model is fitted for each target; no model is fed its own forecasts.

## 5. Information sets

| Set | Predictors allowed at issue t |
|---|---|
| I0 | CME rate (count/exposure) up to t: 3- and 12-month means; last month only for h = 1 |
| I1 | I0 + mean SSN of the last 3 and 12 months up to t |
| I2 | I1 + SSN forecast at t for the target period, with its uncertainty |
| I★ | I1 + observed SSN of the target period. Upper bound only; never reported as skill |

**Reconstructed SSN forecasts (I2, main).** At each issue t, the SSN of months t+1…t+24 is
forecast with a *scaled mean-cycle* method that uses only data up to t:

1. Reference cycles: cycles of the SILSO V2.0 series whose minimum (13-month smoothed SSN,
   same algorithm as D-07) falls in or after the cut-off year C, and whose end is known at t,
   aligned at their minimum. Mean cycle shape S(k), k = months since minimum.
2. Current cycle: months since the last minimum known at t (Section 3).
3. If at least 12 months of the current cycle are observed, the forecast is A·S(k), with A the
   least-squares scale factor of the observed current-cycle SSN against S(k) over the last W
   observed months (or all, if fewer); otherwise A = 1.
4. Uncertainty: the empirical distribution of log((1+observed)/(1+forecast)) of this method
   by horizon, from all past issues whose targets were observed by t, sampled as 500
   trajectories (one residual vector per past issue, preserving correlation across horizons).

**Choice of C and W (fixed rule, applied before `code-v1.0`).** Four variants are compared:
C ∈ {1855, 1940} × W ∈ {24 months, all observed months of the current cycle}. Each variant
issues SSN forecasts every month from 1960-01 to 2009-12, using only data up to each issue
date. They are scored with the CRPS of the mean SSN of the next 12 months (the quantity the
I2 model uses for 12-month totals). The variant with the lowest mean CRPS is used; ties
within 1 % go to C = 1855, W = 24. The SSN of 2010 onwards is not used to choose the
variant, so the choice is independent of the test period. The backtest scores and the
chosen variant are recorded with `code-v1.0`.

**Case study (I2).** The NOAA/NASA Solar Cycle 25 Prediction Panel forecast (December 2019)
for Cycle 25, with its published range, stored in `data/raw/` with provenance before use.

## 6. Models and references

The specification of every model is fixed here. Count models are negative binomial (NB2)
GLMs with log link and offset log(exposure), refitted at **every** issue on all
(issue, target) pairs whose target was observed by the issue date (expanding window from
1996-01).

| Model | Set | Specification | Role |
|---|---|---|---|
| Persistence | I0 | Rate of the last month × exposure (monthly targets); for totals, identical to MA12 | Reference |
| MA3, MA12 | I0 | Mean rate of the last 3 / 12 months × exposure | Reference |
| Cycle-phase analogue | I0 | Mean rate at the same phase of previous cycles (monthly: ±1-month window; totals: same 12-month window), unscaled, minima known at t | Reference |
| **NB-hist+SSN** | I1 | log μ = β0 + β1 log(1+MA3) + β2 log(1+MA12) [+ β3 log(1+last month), h = 1 only] + β4 log(1+SSN₃) + β5 log(1+SSN₁₂) + log(exposure) | **Main model** |
| SSN-only regression | I1 | NB2 with log(1+SSN₃), log(1+SSN₁₂) only | Competitor (secondary comparison) |
| NB-hist | I0 | NB-hist+SSN without the SSN terms | Secondary: isolates the SSN contribution |
| NB-hist+SSNfc | I2 | NB-hist+SSN + log(1+forecast SSN of the target period), mixed over trajectories | Main model for OE3 |
| NB-hist+SSN★ | I★ | NB-hist+SSN + log(1+observed SSN of the target period) | Upper bound |
| Climatology | I0 | Mean rate of all history up to t | Robustness |

Rates in predictors are exposure-adjusted means over usable months; if more than a quarter
of a window is unusable, the forecast is not issued and is reported as missing.

**References are probabilistic.** Each reference gets an NB2 predictive distribution with
dispersion estimated by moments from its own training errors.

**Removed:** ARIMA/ARIMAX models of every kind. They model a continuous series and
do not handle counts with many zeros or exposure; in exploration a Gaussian regression on
log(1+count) with the same predictors was indistinguishable in CRPS from the NB model, so
ARIMA adds no information to the comparison. The link with the previous manuscript is
made through the information sets (its ARIMAX corresponds to the I★ upper bound), not
through the model class. Also removed: seasonal terms (no 12-month seasonality) and
Poisson models (under-cover: 46–76 % for a nominal 80 % interval in exploration).

## 7. Predictive uncertainty

The predictive distribution is a Monte Carlo mixture of three layers:

1. **SSN** (I2 and prospective only): 500 SSN trajectories (Section 5).
2. **Parameters:** for each trajectory, one coefficient vector drawn from the asymptotic
   multivariate normal of the fit.
3. **Counts:** NB2 draws given those coefficients and that trajectory.

I1 and I★ use layers 2–3. For the prospective forecast, the share of predictive variance
due to each layer is reported.

## 8. Metrics

| Metric | Use |
|---|---|
| CRPS (counts: Σₖ [F(k) − 1{k ≥ y}]²) and CRPS skill score SS = 1 − CRPS_model / CRPS_ref | Primary |
| Randomized PIT histogram; coverage of central 50/80/95 % intervals; mean width of the 80 % interval | Calibration and sharpness |
| MAE of the predictive median; RMSE of the predictive mean | Secondary |
| Bias by cycle (Σ forecast means / Σ observations) | OE4 |
| Log score | Robustness: primary conclusion must not change sign |
| Brier score of "active year" (calendar-year total above the upper tercile of 1996–2009 annual totals) | Descriptive |

Not used: out-of-sample R², percentage changes of R², correlation, AIC.

**Reference of the skill score.** For P1 the reference is the best (lowest mean CRPS on the
evaluated set) of persistence, MA3, MA12 and the cycle-phase analogue. Choosing it a
posteriori favours the reference, so the skill is conservative. Skill against each
reference is also reported.

## 9. Comparisons

**Confirmatory (two tests, Holm at 5 % family-wise, one-sided):**
- **P1-fast** and **P1-halo:** NB-hist+SSN versus the best I0 reference, 12-month totals
  issued monthly. H₀: the model is not better (SS ≤ 0).

**Pre-specified estimates (with 95 % intervals, no test):**
- **P3:** skill of NB-hist+SSNfc versus NB-hist+SSN, and the recovered fraction
  φ = (CRPS_I1 − CRPS_I2) / (CRPS_I1 − CRPS_I★), 12-month totals.
- **SSN contribution by horizon:** SS of NB-hist+SSN versus NB-hist at h = 1, 6, 12 and for
  12-month totals, and the difference between h = 12 and h = 1 (joint block bootstrap over
  the common targets).
- NB-hist+SSN versus SSN-only regression (does CME history add to the SSN?).

**Secondary and descriptive:** all horizons against each reference; calendar-year totals;
results by cycle; leave-one-cycle-out (train C23 → test C24, C24 → C23, C23+C24 → C25);
the I★ − I1 gap.

## 10. Inference

- **Unit:** score differences d(t) = CRPS_ref(t) − CRPS_model(t) per issue.
- **P1 test statistic:** Diebold–Mariano statistic with Newey–West variance (11 lags) and the
  Harvey–Leybourne–Newbold correction.
- **Calibrated critical value.** Because overlapping 12-month windows make the usual
  bootstrap and Diebold–Mariano tests anti-conservative (false-positive rates of 6–9 % at a
  nominal 2.5 % in a pre-freeze simulation), the critical value is calibrated by simulation.
  Synthetic CME series are drawn from an NB2 generator with log μ = a + b·log(1+SSN) and a
  persistent latent AR(1) term, driven by the real SSN. On each series, two forecasts of
  equal expected skill (NB-hist plus one of two independent irrelevant smooth covariates)
  are compared with the full rolling-origin pipeline, and the statistic is recorded. The
  critical value for each Holm step is the corresponding upper quantile over 2000 series.
  This is done with **two generators**: (a) fitted to counts of 1996-01 to 2009-12 only (main),
  and (b) fitted to counts of 1996-01 to 2026-06 (control; it uses test-period counts but no
  forecast or score, and a null generator carries no information on skill). **The larger of
  the two critical values is used**, and both are reported, so the choice of generator can
  never make the test more permissive. Generators, seeds and critical values are recorded
  with `code-v1.0`, before the test period is scored.
- **Intervals for skill scores:** moving-block bootstrap, 10 000 replicates; block 24 months
  for 12-month totals, 12 for monthly horizons (sensitivity: 6, 36), 2 years for calendar-year
  totals. Reported with the effective number of independent windows (≈ 16 years).
- **Results by cycle** (≈ 10 years of C24, 6.5 of C25): descriptive only.

## 11. Success criteria

| Result | Criterion |
|---|---|
| Skill (P1) | Holm-adjusted rejection of H₀ with the calibrated critical value |
| Forecast SSN (P3) | φ and SS with intervals; any sign is a result |
| Acceptable calibration | Coverage of the 80 % interval between 0.70 and 0.90; no marked U-shape in monthly PIT histograms |
| Stability across cycles | Descriptive: sign of skill in C24 and C25, bias by cycle |

## 12. Sensitivity analyses (supplementary, pre-specified)

Catalog latency L = 1, 3; speed threshold 900 and 1100 km/s; excluding months with coverage
< 0.8; **halos without the 2025 targets** (2025 has 41 halos versus 102 in 2024; the catalog
did not change between the July and November 2026 versions); versions without flagged
events; bootstrap block lengths; log score instead of CRPS.

**Post-freeze verification.** With the catalog downloaded on 2026-11-14 (and later
versions), forecasts whose targets fall after 2026-06 are verified with the code tagged
`code-v1.0`, without any change. Reported descriptively; it is the only blind test.

## 13. Limits of interpretation

- A change of the CME–SSN relation between cycles can be measured but not attributed to the
  Sun or to the catalog (cadence, identification criteria, revisions).
- Insensitivity of fast CMEs and halos to quality flags (flagged fraction < 20 % in every
  cycle) does not prove that the series are homogeneous across cycles.
- Skill figures are, at best, a slightly optimistic bound on real-time skill (Section 3).
- C2-only coverage.

## 14. Outputs

Main table (P1 with Holm, pre-specified estimates); skill against each reference by horizon;
forecast-versus-observed series with 80 % bands (12-month totals, h = 12, h = 1); PIT and
coverage; skill and bias by cycle and leave-one-cycle-out; prospective forecast with issue
date, SSN trajectories and variance shares; full grid of models × horizons × metrics and all
sensitivities (supplementary, generated by code); raw forecasts (one row per issue, target
and model, with the parameters of the predictive distribution) in the repository and on
Zenodo.

## References (methods; bibliographic details to be checked before citing in the paper)

Gneiting & Raftery (2007, JASA 102, 359); Gneiting, Balabdaoui & Raftery (2007, JRSS-B 69,
243); Czado, Gneiting & Held (2009, Biometrics 65, 1254); Gneiting (2011, JASA 106, 746);
Diebold & Mariano (1995, JBES 13, 253); Harvey, Leybourne & Newbold (1997, IJF 13, 281);
Künsch (1989, Ann. Stat. 17, 1217); Holm (1979, Scand. J. Stat. 6, 65).
