"""Frozen decoder for the longitudinal certification. Pure numpy; fully specified for reproducibility.

Decoder = grouped leave-one-history-out ridge (lambda = 1.0), per-fold standardization with
constant-column removal, features = 10-D per-entity memory order-statistics [mean,std,p10,p50,p90] of
(m1,m2) augmented with the m_minus dispersion (mminus_std) -> 11-D. R^2 is the pooled coefficient of
determination over all held-out records. Uncertainty = donor-level (history-grouped) percentile bootstrap,
n_boot = 3000, FIXED seed for determinism.

This decoder is a clean, documented re-implementation. See CLEANROOM_REPRODUCTION_REPORT.md for the
relationship between these reproduced values and the manuscript's inline values.
"""
from __future__ import annotations
import numpy as np

RIDGE_LAMBDA = 1.0
N_BOOT = 3000
BOOT_SEED = 20260715


def features_from_long(long_tuple):
    """long = (feat10, M, size, mminus_std) -> 11-D feature vector."""
    feat = list(long_tuple[0])
    mminus_std = float(long_tuple[3])
    return np.asarray(feat + [mminus_std], dtype=float)


def _ridge_logo_predict(X, y, groups, lam=RIDGE_LAMBDA):
    """Grouped leave-one-history-out ridge predictions (out-of-fold)."""
    pred = np.full_like(y, np.nan, dtype=float)
    for h in np.unique(groups):
        tr = groups != h
        te = groups == h
        mu = X[tr].mean(0)
        sd = X[tr].std(0)
        keep = sd > 1e-9
        if keep.sum() == 0:
            pred[te] = y[tr].mean()
            continue
        Xtr = (X[tr][:, keep] - mu[keep]) / sd[keep]
        Xte = (X[te][:, keep] - mu[keep]) / sd[keep]
        yb = y[tr].mean()
        A = Xtr.T @ Xtr + lam * np.eye(int(keep.sum()))
        w = np.linalg.solve(A, Xtr.T @ (y[tr] - yb))
        pred[te] = Xte @ w + yb
    return pred


def r2(y, pred):
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def decode_r2(X, y, groups, lam=RIDGE_LAMBDA):
    return r2(y, _ridge_logo_predict(X, y, groups, lam))


def bootstrap_ci(X, y, groups, lam=RIDGE_LAMBDA, n_boot=N_BOOT, seed=BOOT_SEED):
    """Donor-level (history-grouped) percentile bootstrap 95% CI. Deterministic given seed."""
    rng = np.random.default_rng(seed)
    hs = np.unique(groups)
    vals = []
    for _ in range(n_boot):
        pick = rng.choice(hs, size=len(hs), replace=True)
        idx = np.concatenate([np.where(groups == h)[0] for h in pick])
        gg = np.concatenate([[i] * int(np.sum(groups == h)) for i, h in enumerate(pick)])
        try:
            vals.append(decode_r2(X[idx], y[idx], gg, lam))
        except np.linalg.LinAlgError:
            continue
    vals = np.asarray(vals)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 50)), float(np.percentile(vals, 97.5))
