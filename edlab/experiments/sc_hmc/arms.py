"""Counterfactual arms built at checkpoint t_c. Each isolates a different putative carrier of future
behaviour: history (H), instantaneous phenotype (P), material (M), between-entity similarity (U), and
the exact-state stochastic ceiling (C).

Truth/construction is kept separate from evaluation: these functions only BUILD states; scoring lives in
axes.py / models.py.
"""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.engine import SCState
from . import config as C
from . import harness as H


def _entity_cells(st: SCState, e):
    return e.cells[:, 0], e.cells[:, 1]


def arm_H(st_tc: SCState) -> SCState:
    """Continuous history: the entity itself, unchanged."""
    return st_tc.copy()


def arm_P(st_tc: SCState, seed: int) -> SCState:
    """Phenotype-matched reset clone: preserve rho, c, N, geometry, mass, position; RESET the hidden
    internal dynamical history (U,V spatial pattern + attractor state) to a fresh random field."""
    rng = np.random.default_rng(10_000 + seed)
    out = st_tc.copy()
    n = out.rho.shape[0]
    u = np.clip(0.8 + 0.4 * rng.standard_normal((n, n)), 0.0, None)
    v = np.clip(0.8 + 0.4 * rng.standard_normal((n, n)), 0.0, None)
    out.U = out.rho * u
    out.V = out.rho * v
    # material labels are NOT meaningful for a fresh phenotype copy: collapse to a single 'new' bin
    out.C = np.stack([np.zeros_like(out.rho), out.rho.copy()])
    return out


def arm_M(st_tc: SCState, seed: int) -> SCState:
    """Material-retaining organizational reset: preserve rho AND cohort/material labels EXACTLY, but
    destroy internal ORGANIZATION by spatially permuting (U,V) among the entity's cells (keeps the
    internal-state histogram and mean sigma; erases spatial structure)."""
    rng = np.random.default_rng(20_000 + seed)
    out = st_tc.copy()
    e = H.largest_entity(out)
    if e is None:
        return out
    ys, xs = _entity_cells(out, e)
    u = out.U[ys, xs].copy(); v = out.V[ys, xs].copy()
    perm = rng.permutation(len(ys))
    out.U[ys, xs] = u[perm]
    out.V[ys, xs] = v[perm]
    # rho and C (material) are preserved bit-for-bit -> material continuity intact, organization gone
    return out


def arm_U(st_tc: SCState, seed: int, ref_size: float, ref_rg: float):
    """Unrelated phenotype-matched entity: a DIFFERENT trajectory whose largest entity best matches H's
    geometry at t_c but shares no history. Returns (state, engine) or (None, None) if no match."""
    best, best_d = None, np.inf
    age = C.CHECKPOINT
    for s in C.UNRELATED_SEEDS:
        if s == seed:
            continue
        st = H.warmup(s)
        st = H.advance(H.pulse_chase_engine(), H.relabel_pulse_chase(st), age)
        e = H.largest_entity(st)
        if e is None:
            continue
        d = abs(np.log(e.size + 1) - np.log(ref_size + 1)) + abs(e.rg - ref_rg) / 3.0
        if d < best_d:
            best_d, best = d, st
    return best, best_d


def arm_C(st_tc: SCState, seed: int, k: int) -> tuple[SCState, "H.NoisyForcingEngine"]:
    """Exact full-state clone k, evolved under INDEPENDENT bounded environmental noise. Defines the
    reproducibility / stochastic ceiling. Not physically realizable (exact cloning is a simulation
    privilege) -- reported as such."""
    rng = np.random.default_rng(30_000 + 101 * seed + k)
    eng = H.NoisyForcingEngine(C.SPEC, H.PulseChaseTracer(), rng)
    return st_tc.copy(), eng
