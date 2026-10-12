"""Shared deterministic statistics with explicit degenerate-case behavior."""
from __future__ import annotations

import math
import numpy as np
from scipy.stats import binomtest, rankdata


def auc(y, scores) -> float:
    y, scores = np.asarray(y), np.asarray(scores, float)
    if y.ndim != 1 or scores.shape != y.shape or not np.isin(y, [0, 1]).all() or not np.isfinite(scores).all():
        raise ValueError("AUROC needs aligned binary labels and finite scores")
    p = int(y.sum()); n = len(y) - p
    return float((rankdata(scores)[y == 1].sum() - p * (p + 1) / 2) / (p * n)) if p and n else float("nan")


def random_hit(n: int, positives: int, k: int) -> float:
    if n < 1 or not 0 <= positives <= n or k < 1:
        raise ValueError("invalid hit@k counts")
    k = min(k, n)
    return 1.0 - math.comb(n - positives, k) / math.comb(n, k) if k <= n - positives else 1.0


def expected_tied_hit(y, scores, k: int) -> float:
    """Probability of any evidence when ties at the cutoff are broken uniformly."""
    y, s = np.asarray(y), np.asarray(scores)
    if k < 1 or len(y) == 0:
        raise ValueError("hit@k needs a positive k and nonempty pool")
    k = min(k, len(y)); cutoff = np.sort(s)[-k]
    above, tied = s > cutoff, s == cutoff
    if y[above].any():
        return 1.0
    return random_hit(int(tied.sum()), int(y[tied].sum()), k - int(above.sum()))


def cluster_mean_ci(values, clusters, *, n_boot: int = 2000, seed: int = 0) -> dict:
    v, c = np.asarray(values, float), np.asarray(clusters)
    if v.ndim != 1 or c.shape != v.shape or not np.isfinite(v).all() or n_boot < 1:
        raise ValueError("finite, aligned values and positive bootstrap count required")
    groups = np.unique(c)
    out = {"mean": float(v.mean()) if len(v) else None, "lo": None, "hi": None, "n": len(v), "n_clusters": len(groups)}
    if len(groups) < 2:
        return out
    sums = np.array([v[c == g].sum() for g in groups]); counts = np.array([(c == g).sum() for g in groups])
    rng = np.random.default_rng(seed)
    draw = rng.integers(len(groups), size=(n_boot, len(groups)))
    b = sums[draw].sum(axis=1) / counts[draw].sum(axis=1)
    out.update(lo=float(np.quantile(b, .025)), hi=float(np.quantile(b, .975)))
    return out


def mcnemar_exact(a, b) -> dict:
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape or a.ndim != 1 or not np.isin(a, [0, 1]).all() or not np.isin(b, [0, 1]).all():
        raise ValueError("aligned binary outcomes required")
    x = int(((a == 1) & (b == 0)).sum()); y = int(((a == 0) & (b == 1)).sum())
    return {"only_a": x, "only_b": y, "n": len(a), "p": float(binomtest(x, x+y, .5).pvalue) if x+y else 1.0}


def holm(pvalues) -> list[float]:
    p = np.asarray(pvalues, float)
    if p.ndim != 1 or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("p values must be finite and in [0, 1]")
    order = np.argsort(p); out = np.empty(len(p)); high = 0.0
    for i, j in enumerate(order):
        high = max(high, min(1., (len(p)-i)*p[j])); out[j] = high
    return out.tolist()
