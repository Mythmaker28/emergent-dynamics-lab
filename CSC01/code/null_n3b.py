"""CSC01 — N3b, the strongest no-cohesion null available.

N3 assumes a STATIC point source. The real source is the organiser, which diffuses, and the real
birth rate is not constant. N3b removes both idealisations while still containing NO interaction
of any kind between X molecules:

    * a molecule alive at time t was born at time t - s, with s drawn from the ACTUAL recorded
      birth history weighted by survival: P(s) ∝ births(t - s) · (1 - mu)^s ;
    * it was born at the ACTUAL recorded position of the organiser at time t - s ;
    * it then performed a free lattice walk for s steps with the engine's own four-attempt rule,
      with no capacity constraint, no attraction, no boundary, nothing.

r80, Rg and the rest are then measured about the SAMPLE's own Frechet centre, exactly as for the
observation, so the common drift of the source is removed in both.

If the observation is indistinguishable from N3b, then every spatial feature of the X population
is accounted for by "a point source that wanders, plus a finite lifetime", and the declared
operator contains no cohesion. If the observation is significantly MORE compact than N3b, the
excess is the cohesion to be explained.
"""
from __future__ import annotations

import numpy as np

import nulls as NU


def sample_n3b(rng, L, N_X, t, births, org_traj, org_steps, p_hop, mu, max_age=4000):
    """One realisation of the no-interaction cloud at time t."""
    s = np.arange(1, min(max_age, t) + 1)
    b = births[t - s]                                   # births at t - s (recorded, exact)
    wgt = b * (1.0 - mu) ** s
    if wgt.sum() <= 0:
        return None
    wgt = wgt / wgt.sum()
    ages = rng.choice(s, size=N_X, p=wgt)
    # organiser position at the birth time, from the recorded trajectory
    j = np.searchsorted(org_steps, t - ages, side="right") - 1
    j = np.clip(j, 0, len(org_steps) - 1)
    y0 = org_traj[j, 0]
    x0 = org_traj[j, 1]
    q = p_hop / 4.0
    dy = rng.binomial(ages, q) - rng.binomial(ages, q)
    dx = rng.binomial(ages, q) - rng.binomial(ages, q)
    f = np.zeros((L, L), np.int64)
    np.add.at(f, ((y0 + dy) % L, (x0 + dx) % L), 1)
    return f


def n3b_distribution(n_draws, seed, L, ell_X, **kw):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_draws):
        f = sample_n3b(rng, L, kw["N_X"], kw["t"], kw["births"], kw["org_traj"],
                       kw["org_steps"], kw["p_hop"], kw["mu"])
        if f is None:
            continue
        rows.append(NU.light_report(f, ell_X))
    if not rows:
        return {}
    return {k: np.array([r[k] for r in rows], dtype=float) for k in rows[0]}
