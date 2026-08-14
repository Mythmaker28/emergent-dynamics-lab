"""CSC01 — the five spatial nulls of §3 of the autopsy pre-plan.

N3 is the one that matters. A population fed by a POINT SOURCE and killed at a constant rate is
localised for free, with no interaction between its members whatsoever: its stationary profile is
the lattice Green's function of the death-modified walk, with decay length ell_X. Beating the
uniform null N1 therefore proves nothing about cohesion. The observable must be compared to N3.

N3 is computed EXACTLY on the L x L torus, not approximated: the one-step displacement of a
molecule under the engine's own `_diffuse` is delta_y = B1 - B2, delta_x = B3 - B4 with each B
Bernoulli(q), q = p_hop/4, so the characteristic function factorises as

    phi(k) = [1 - a(1 - cos k_y)] [1 - a(1 - cos k_x)],   a = 2q(1-q),

and the stationary profile of a unit point source with per-step survival (1 - mu) is

    n_hat(k) = 1 / (1 - (1 - mu) phi(k)),

inverted by an exact 2-D DFT over the L^2 lattice momenta.
"""
from __future__ import annotations

import numpy as np

import spatial as SP


# ------------------------------------------------------------------ a light frame report
def light_report(nX, ell_X):
    """Only the four observables the nulls are compared on. No BFS, so ~20x faster."""
    L = nX.shape[0]
    out = {}
    M = float(nX.sum())
    if M <= 0:
        return {"r80": np.nan, "Rg_pairwise": np.nan, "main_mass_fraction": np.nan,
                "n_eff_components": np.nan, "core_fraction_within_2ellX": np.nan, "r50": np.nan}
    cy, cx, _ = SP.frechet_centre(nX)
    rq = SP.radii_quantiles(nX, cy, cx)
    out["r50"], out["r80"] = rq[0.5], rq[0.8]
    out["Rg_pairwise"] = SP.rg_pairwise(nX)
    out["core_fraction_within_2ellX"] = SP.mass_within(nX, cy, cx, 2.0 * ell_X) / M
    labels, _ = SP.torus_components(nX > 0)
    k = labels.max() + 1
    if k <= 0:
        out["main_mass_fraction"] = np.nan
        out["n_eff_components"] = np.nan
        return out
    masses = np.array([float(nX[labels == c].sum()) for c in range(k)])
    out["main_mass_fraction"] = float(masses.max() / masses.sum())
    out["n_eff_components"] = SP.effective_n(masses)
    return out


# ------------------------------------------------------------------ N1 complete spatial randomness
def n1_csr(rng, L, N_X, cap=16):
    """N_X molecules placed uniformly at random over the L^2 cells, at most `cap` per cell."""
    f = rng.multinomial(N_X, np.full(L * L, 1.0 / (L * L))).reshape(L, L)
    over = f > cap
    while over.any():                                     # essentially never fires at N_X ~ 10^2
        excess = int((f[over] - cap).sum())
        f[over] = cap
        f += rng.multinomial(excess, np.full(L * L, 1.0 / (L * L))).reshape(L, L)
        over = f > cap
    return f.astype(np.int64)


# ------------------------------------------------------------------ N2 pure diffusion
def n2_diffusion(rng, L, N_X, cy, cx, T, p_hop):
    """N_X molecules released at (cy, cx) and diffused for T steps with the engine's own
    four-attempt rule, free lattice, no birth, no death, no capacity."""
    q = p_hop / 4.0
    dy = rng.binomial(T, q, N_X) - rng.binomial(T, q, N_X)
    dx = rng.binomial(T, q, N_X) - rng.binomial(T, q, N_X)
    ys = (cy + dy) % L
    xs = (cx + dx) % L
    f = np.zeros((L, L), np.int64)
    np.add.at(f, (ys, xs), 1)
    return f


# ------------------------------------------------------------------ N3 point source, exact
def n3_profile(L, p_hop, mu):
    """Exact stationary profile of birth at one cell, diffusion, death at rate mu, on the torus.
    Returns a normalised probability field centred on (0, 0)."""
    q = p_hop / 4.0
    a = 2.0 * q * (1.0 - q)
    k = 2.0 * np.pi * np.arange(L) / L
    phi1 = 1.0 - a * (1.0 - np.cos(k))
    phi = phi1[:, None] * phi1[None, :]
    denom = 1.0 - (1.0 - mu) * phi
    nhat = 1.0 / denom
    prof = np.real(np.fft.ifft2(nhat))
    prof = np.maximum(prof, 0.0)
    return prof / prof.sum()


def n3_sample(rng, prof, N_X, cy, cx):
    """N_X molecules drawn i.i.d. from the point-source profile centred at (cy, cx)."""
    L = prof.shape[0]
    p = np.roll(np.roll(prof, cy, axis=0), cx, axis=1).ravel()
    f = rng.multinomial(N_X, p / p.sum()).reshape(L, L)
    return f.astype(np.int64)


# ------------------------------------------------------------------ N4 label permutation
def n4_permute(rng, nX):
    L = nX.shape[0]
    flat = nX.ravel().copy()
    rng.shuffle(flat)
    return flat.reshape(L, L)


# ------------------------------------------------------------------ N5 decorrelated frames
def n5_decorrelated_steps(rng, centres, L, n_draw=2000):
    """Distances between centres taken at INDEPENDENT times: the marginal distribution of core
    positions is preserved, the temporal continuity is destroyed."""
    c = np.asarray(centres, dtype=np.int64)
    n = len(c)
    if n < 3:
        return np.zeros(0)
    i = rng.integers(0, n, n_draw)
    j = rng.integers(0, n, n_draw)
    keep = i != j
    i, j = i[keep], j[keep]
    dy = SP.wrapped_abs(c[i, 0] - c[j, 0], L)
    dx = SP.wrapped_abs(c[i, 1] - c[j, 1], L)
    return np.hypot(dy, dx)


# ------------------------------------------------------------------ driver
def null_distribution(kind, n_draws, seed, L, ell_X, **kw):
    rng = np.random.default_rng(seed)
    rows = []
    prof = kw.get("prof")
    for _ in range(n_draws):
        if kind == "N1":
            f = n1_csr(rng, L, kw["N_X"], kw.get("cap", 16))
        elif kind == "N2":
            f = n2_diffusion(rng, L, kw["N_X"], kw["cy"], kw["cx"], kw["T"], kw["p_hop"])
        elif kind == "N3":
            f = n3_sample(rng, prof, kw["N_X"], kw["cy"], kw["cx"])
        elif kind == "N4":
            f = n4_permute(rng, kw["nX"])
        else:
            raise ValueError(kind)
        rows.append(light_report(f, ell_X))
    keys = rows[0].keys()
    return {k: np.array([r[k] for r in rows], dtype=float) for k in keys}


def quantiles(arr, qs=(0.01, 0.05, 0.5, 0.95, 0.99)):
    a = np.asarray(arr, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {str(q): float("nan") for q in qs}
    return {str(q): float(np.quantile(a, q)) for q in qs}
