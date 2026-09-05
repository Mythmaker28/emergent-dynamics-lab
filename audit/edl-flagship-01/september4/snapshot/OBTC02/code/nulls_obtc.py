"""OBTC01 §6.4 — four nulls, and the CONDITIONAL / GENERATIVE distinction kept explicit.

N0  COMPLETE SPATIAL RANDOMNESS      conditional on N_X and the domain only.
    Question: is there ANY localisation?

N1  CONDITIONAL SOURCE               conditional on the OBSERVED organiser trajectory and the
    OBSERVED birth times and places. Free transport, declared lifetime law, no interaction.
    Question: is there any compaction BEYOND what a mobile source explains?
    It cannot confirm the generative mechanism, because it is handed the mechanism's output.

N2  GENERATIVE SOURCE-TRANSPORT      conditional on NOTHING that was realised. The organiser's
    walk, the births, the transport and the deaths are all generated from the frozen Spec.
    Question: does the operator PREDICT the observables?
    Only the sample size is matched, and only because sampling noise depends on it; every shape
    observable of this null is invariant to the birth intensity.

N3  TEMPORAL CONTINUITY DESTROYED    marginal distributions preserved, the identity of the main
    component across time destroyed by pairing frames from independent times.
    Question: is the core's persistence a real continuity?
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "/home/claude/OBTC01/code")

import metrics_obtc as M        # noqa: E402

SHAPE = ("r50", "r80", "r90", "Rg", "main_mass_fraction", "n_eff_components", "core_fraction")


def _report(nX, core_radius):
    nY = np.zeros_like(nX)
    f, _ = M.frame(nX, nY, core_radius)
    return {k: f[k] for k in SHAPE}


# ------------------------------------------------------------------ N0
def n0_csr(rng, L, N_X, cap):
    f = rng.multinomial(N_X, np.full(L * L, 1.0 / (L * L))).reshape(L, L)
    while (f > cap).any():
        ex = int((f[f > cap] - cap).sum())
        f[f > cap] = cap
        f += rng.multinomial(ex, np.full(L * L, 1.0 / (L * L))).reshape(L, L)
    return f.astype(np.int64)


# ------------------------------------------------------------------ N1
def n1_conditional(rng, L, N_X, t, births_series, org_steps, org_traj, q_X, mu, max_age=6000):
    """Ages drawn from the OBSERVED birth history weighted by survival; birthplaces are the
    OBSERVED organiser positions; transport is the free four-attempt walk."""
    s = np.arange(1, min(max_age, t) + 1)
    w = births_series[t - s] * (1.0 - mu) ** s
    if w.sum() <= 0:
        return None
    ages = rng.choice(s, size=N_X, p=w / w.sum())
    j = np.clip(np.searchsorted(org_steps, t - ages, side="right") - 1, 0, len(org_steps) - 1)
    y0, x0 = org_traj[j, 0], org_traj[j, 1]
    dy = rng.binomial(ages, q_X) - rng.binomial(ages, q_X)
    dx = rng.binomial(ages, q_X) - rng.binomial(ages, q_X)
    f = np.zeros((L, L), np.int64)
    np.add.at(f, ((y0 + dy) % L, (x0 + dx) % L), 1)
    return f


# ------------------------------------------------------------------ N2
def n2_generative(rng, L, N_X, q_X, q_Y, mu, burn=6000):
    """Nothing realised is used. The organiser walks with the engine's own rule; molecules are
    born at it, walk with the same rule and die at rate mu. Only the sample size is matched.

    Returns (field, organiser_position, core_offset) in the organiser's own frame."""
    T = burn
    dy = rng.binomial(1, q_Y, T) - rng.binomial(1, q_Y, T)
    dx = rng.binomial(1, q_Y, T) - rng.binomial(1, q_Y, T)
    oy = np.cumsum(dy)
    ox = np.cumsum(dx)
    # ages of the surviving population: Geometric(mu), truncated at the burn-in
    a = np.arange(1, T + 1)
    w = (1.0 - mu) ** a
    ages = rng.choice(a, size=N_X, p=w / w.sum())
    by = oy[T - ages]
    bx = ox[T - ages]
    wy = rng.binomial(ages, q_X) - rng.binomial(ages, q_X)
    wx = rng.binomial(ages, q_X) - rng.binomial(ages, q_X)
    ys = (by + wy - oy[T - 1] + L // 2) % L
    xs = (bx + wx - ox[T - 1] + L // 2) % L
    f = np.zeros((L, L), np.int64)
    np.add.at(f, (ys.astype(int), xs.astype(int)), 1)
    return f, (L // 2, L // 2)


def n2_distribution(n_draws, seed, L, N_X, q_X, q_Y, mu, core_radius, burn=6000):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_draws):
        f, org = n2_generative(rng, L, N_X, q_X, q_Y, mu, burn)
        r = _report(f, core_radius)
        cy, cx = M.frechet_centre(f)
        r["organiser_to_core"] = float(np.hypot(M.wdist1(org[0] - cy, L),
                                                M.wdist1(org[1] - cx, L)))
        rows.append(r)
    return {k: np.array([r[k] for r in rows], float) for k in rows[0]}


# ------------------------------------------------------------------ N3
def n3_decorrelated(rng, centres, L, n_draw=4000):
    c = np.asarray(centres, np.int64)
    if len(c) < 3:
        return np.zeros(0)
    i = rng.integers(0, len(c), n_draw)
    j = rng.integers(0, len(c), n_draw)
    k = i != j
    return np.hypot(M.wdist1(c[i[k], 0] - c[j[k], 0], L), M.wdist1(c[i[k], 1] - c[j[k], 1], L))


# ------------------------------------------------------------------ driver
def distribution(kind, n_draws, seed, L, core_radius, **kw):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_draws):
        if kind == "N0":
            f = n0_csr(rng, L, kw["N_X"], kw["cap"])
        elif kind == "N1":
            f = n1_conditional(rng, L, kw["N_X"], kw["t"], kw["births"], kw["org_steps"],
                               kw["org_traj"], kw["q_X"], kw["mu"])
            if f is None:
                continue
        else:
            raise ValueError(kind)
        rows.append(_report(f, core_radius))
    if not rows:
        return {}
    return {k: np.array([r[k] for r in rows], float) for k in rows[0]}


def quantiles(a, qs=(0.01, 0.05, 0.5, 0.95, 0.99)):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {str(q): float("nan") for q in qs}
    return {str(q): float(np.quantile(a, q)) for q in qs}


def position(a, obs):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if a.size == 0 or not np.isfinite(obs):
        return float("nan")
    return float((a <= obs).mean())
