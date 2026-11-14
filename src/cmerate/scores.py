"""Verification scores for count forecasts (docs/PROTOCOL.md §8).

Predictive distributions are represented by a probability mass function on 0..K-1
(``pmf``), so that negative-binomial forecasts, Monte Carlo mixtures and point forecasts are
scored the same way. K must be large enough that the omitted tail is negligible; every
function checks it.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

TAIL_TOLERANCE = 1e-6


def nb_pmf(mu: float, alpha: float, K: int) -> np.ndarray:
    """NB2 pmf on 0..K-1 with mean mu and variance mu + alpha·mu²."""
    n = 1.0 / alpha
    return stats.nbinom.pmf(np.arange(K), n, n / (n + mu))


def mixture_pmf(mus: np.ndarray, alpha: float, K: int) -> np.ndarray:
    """Equal-weight mixture of NB2 pmfs (Monte Carlo predictive distribution)."""
    n = 1.0 / alpha
    k = np.arange(K)
    return stats.nbinom.pmf(k[None, :], n, n / (n + np.asarray(mus)[:, None])).mean(axis=0)


def point_pmf(value: int, K: int) -> np.ndarray:
    p = np.zeros(K); p[int(value)] = 1.0
    return p


def _check(pmf: np.ndarray) -> np.ndarray:
    missing = 1.0 - pmf.sum()
    if missing > TAIL_TOLERANCE:
        raise ValueError(f"pmf truncated: {missing:.2e} of the mass lies beyond K={len(pmf)}; increase K")
    return pmf


def crps(pmf: np.ndarray, y: float) -> float:
    """CRPS for counts: sum_k (F(k) - 1{k >= y})^2."""
    F = np.cumsum(_check(pmf))
    if y >= len(F):
        raise ValueError(f"observation {y} beyond K={len(F)}")
    k = np.arange(len(F))
    return float(((F - (k >= y)) ** 2).sum())


def log_score(pmf: np.ndarray, y: float) -> float:
    p = _check(pmf)[int(y)]
    return float(-np.log(max(p, 1e-300)))


def quantile(pmf: np.ndarray, q: float) -> int:
    return int(np.searchsorted(np.cumsum(_check(pmf)), q - 1e-12))


def mean(pmf: np.ndarray) -> float:
    return float((np.arange(len(pmf)) * _check(pmf)).sum())


def pit(pmf: np.ndarray, y: float, u: float) -> float:
    """Randomized PIT value F(y-1) + u·P(y), with u ~ Uniform(0, 1) supplied by the caller."""
    F = np.cumsum(_check(pmf))
    lower = F[int(y) - 1] if y >= 1 else 0.0
    return float(lower + u * pmf[int(y)])


def central_interval(pmf: np.ndarray, level: float) -> tuple[int, int]:
    return quantile(pmf, (1 - level) / 2), quantile(pmf, (1 + level) / 2)


def covered(pmf: np.ndarray, y: float, level: float) -> bool:
    lo, hi = central_interval(pmf, level)
    return lo <= y <= hi


def skill_score(score_model: np.ndarray, score_reference: np.ndarray) -> float:
    """1 - mean(model) / mean(reference); 1 is perfect, 0 no gain, < 0 worse."""
    return float(1.0 - np.mean(score_model) / np.mean(score_reference))


def brier(prob: float, outcome: bool) -> float:
    return float((prob - float(outcome)) ** 2)
