"""LCI-CAUSAL-TURNOVER-PREREG-03 — per-target PASSIVE material tracer (DEV; strictly observational).

Measures per-droplet material continuity M_i(t) = fraction of the SNAPSHOT material of droplet i that is still
in droplet i's (bijectively-tracked) region at time t, using extra passive origin cohorts appended to the frozen
engine's cohort array C. NO ENGINE MODIFICATION and NO PHYSICAL FEEDBACK:

  * The frozen MultiChannelMemoryEngine reads C only to advect it, scale it by homogeneous death, and deposit feed
    into `tracer.active_feed_cohort(step)`. rho, U, V, c, N, Mf evolve WITHOUT reading C. Appending cohorts to C
    therefore cannot change the physics — verified byte-identical (test_material_tracer.py: rho,U,V,c,N,Mf,uptake
    max|Δ| = 0.0 between standard-C and extended-C runs).
  * The feed index active_feed_cohort(step) = n_spatial + (step//tau_feed) % n_temporal is ALWAYS < C0 (the
    original cohort count), so tracer cohorts appended at indices >= C0 NEVER receive feed: they only decay by
    death (keep = 1 - k*dt) and advect passively with the scaffold flux. That is exactly "old snapshot material."

Accounting per region i at time t (den = total rho in region i):
    M_i          = tracer_i mass in region_i / den            (own snapshot material still here)
    cross_{i<-j} = tracer_j mass in region_i / den            (neighbour j's snapshot material now here)
    new_i        = 1 - M_i - sum_j cross_{i<-j}               (freshly-fed / unlabelled material)
"new material" (deep turnover) is the complement of ALL snapshot cohorts, i.e. 1 - sum_j tracer_j in region.
"""
import numpy as np


def seed_tracers(state, region_masks):
    """Return (state_with_tracers, base) where `base` is the index of the first appended tracer cohort.
    Tracer cohort i is seeded as rho * region_mask_i (the current mass of droplet i at the snapshot)."""
    s = state.copy()
    base = int(s.C.shape[0])
    extra = np.stack([s.rho * m for m in region_masks]).astype(s.C.dtype)  # (K, N, N)
    s.C = np.concatenate([s.C, extra], axis=0)
    return s, base


def assert_no_feed_collision(tracer, base, n_steps):
    """Guard: over [0, n_steps) the engine's feed index must never fall on a tracer cohort (>= base)."""
    idxs = {int(tracer.active_feed_cohort(t)) for t in range(max(1, n_steps))}
    hi = max(idxs)
    if hi >= base:
        raise AssertionError(f"feed index {hi} collides with tracer cohort base {base}")
    return hi


def read_material(state, base, region_masks):
    """Per-region material accounting on the CURRENT (e.g. bijectively-tracked) region masks.
    region_masks[i] may be None (censored track) -> that entry is None."""
    K = len(region_masks)
    out = []
    for i, m in enumerate(region_masks):
        if m is None:
            out.append(None); continue
        den = float(state.rho[m].sum())
        if den <= 1e-12:
            out.append(dict(M=float('nan'), cross={}, new=float('nan'), rho_region=den)); continue
        own = float(state.C[base + i][m].sum()) / den
        cross = {int(j): float(state.C[base + j][m].sum()) / den for j in range(K) if j != i and region_masks[j] is not None}
        new = 1.0 - own - float(sum(cross.values()))
        out.append(dict(M=own, cross=cross, new=new, rho_region=den))
    return out
