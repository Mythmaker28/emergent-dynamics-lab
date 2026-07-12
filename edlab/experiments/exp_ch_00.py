"""EXP-CH-00 R7 qualification: blind Halton sample of the FROZEN bounded domain. No hand-picking."""

from __future__ import annotations

import numpy as np

from ..substrates.chemotaxis.engine import ChemoSpec, CHState, ChemoEngine
from ..substrates.chemotaxis.diagnostics import r7_diagnostics, circular_centroid
from ..substrates.reaction_diffusion.engine import TracerSpec
from .baseline import halton_point

TRACER = TracerSpec(n_spatial=4, n_temporal=8, tau_feed=200)
N_POINTS = 32                       # frozen: the qualification domain is the first 32 Halton points
QUAL_SEEDS = (5001, 5002, 5003, 5004, 5005)
T_STAR = 2000                       # engine steps (dt = 0.1 -> 200 time units)
WINDOW = 1000
CADENCE = 100
BOX = {"chi0": (2.0, 12.0), "D_rho": (0.05, 0.30), "D_c": (0.20, 1.00), "s": (0.05, 0.40),
       "delta": (0.02, 0.20), "g0": (0.02, 0.20), "k": (0.01, 0.10), "F": (0.01, 0.10)}


def chemo_law(i: int) -> ChemoSpec:
    h = halton_point(i + 1, len(BOX))
    vals = {name: lo + (hi - lo) * float(h[j]) for j, (name, (lo, hi)) in enumerate(BOX.items())}
    return ChemoSpec(**vals)


def seed_state(spec: ChemoSpec, tracer: TracerSpec, seed: int) -> CHState:
    """Near-uniform low-density cells + small noise: aggregation must be SPONTANEOUS and SELF-organized."""
    rng = np.random.default_rng(seed)
    n = spec.size
    rho = 0.25 * spec.rho_max + 0.02 * rng.standard_normal((n, n))
    rho = np.clip(rho, 0.0, spec.rho_max)
    c = np.zeros((n, n))
    N = np.full((n, n), spec.N0)
    C = np.zeros((tracer.n_cohorts, n, n))
    ys = np.arange(n)[:, None] * np.ones((1, n))
    for q in range(tracer.n_spatial):
        C[q] = np.where(((ys * tracer.n_spatial) // n) % tracer.n_spatial == q, rho, 0.0)
    return CHState(rho, c, N, C, 0)


def r7_unit(law_index: int, seed: int) -> dict:
    spec = chemo_law(law_index)
    eng = ChemoEngine(spec, TRACER)
    st = seed_state(spec, TRACER, seed)
    for _ in range(T_STAR):
        st = eng.step(st)
        if not np.isfinite(st.rho).all():
            return {"law_index": law_index, "seed": seed, "diverged": True, "localized": False}
    d0 = r7_diagnostics(st, spec.rho_max)
    snaps = eng.simulate(st, WINDOW, CADENCE)[1:]
    ds = [r7_diagnostics(s, spec.rho_max) for s in snaps]
    persist = all(d["localized"] for d in ds) and d0["localized"]
    cens = [circular_centroid(s.rho) for s in ([st] + snaps)]
    n = spec.size
    hops = []
    for i in range(1, len(cens)):
        dv = cens[i] - cens[i - 1]
        dv -= n * np.round(dv / n)
        hops.append(float(np.linalg.norm(dv)))
    path = float(sum(hops))
    net = cens[-1] - cens[0]
    net -= n * np.round(net / n)
    return {"law_index": law_index, "seed": seed, "diverged": False,
            "localized_at_t_star": d0["localized"], "localized_all_window": persist,
            "pr": d0["participation_ratio"], "rg_global": d0["radius_of_gyration_global"],
            "entity_rg": d0["entity_rg"], "entity_size": d0["entity_size"], "mass": d0["mass"],
            "occ": d0["occupancy"], "comp": d0["largest_component_frac"],
            "rho_max_observed": d0["rho_max_observed"],
            "unwrapping_unambiguous": bool(all(h < n / 2 for h in hops)),
            "path": path, "net_displacement": float(np.linalg.norm(net)),
            "straightness": float(np.linalg.norm(net) / path) if path > 1e-9 else 0.0,
            "spec": {k: getattr(spec, k) for k in BOX}}
