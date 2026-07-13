"""EXP-SC-00B: prospective orthogonality qualification with O2' (VIABILITY, not size-invariance).

Protocol: docs/experiments/EXP_SC_00B_PROTOCOL.md (SHA a6d301870b29b4ef046194b68466727dc6e4ddb6), frozen first.
Substrate UNCHANGED. Only `beta` is selected, prospectively, on entirely unseen seeds, by O1/O2'/O3/O4' alone.
D-044's seeds (8001, 8101, 8102) are NOT reused and its result is NOT reinterpreted.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from ..substrates.scaffold.engine import ScaffoldSpec, SCState, ScaffoldEngine
from ..substrates.scaffold.observables import detect
from ..substrates.chemotaxis.diagnostics import (participation_ratio, entity_radius_of_gyration,
                                                 _largest_component, THRESHOLD_BAND)
from ..substrates.reaction_diffusion.observables import rd_material_retention
from ..substrates.particle_dynamics.engine import minimum_image
from ..identity.gates import partial_correlation_test
from .exp_sc_00 import SPEC, TRACER, DET, seed_state, T_STAR

BETA_GRID = (0.05, 0.10, 0.20, 0.30, 0.45, 0.60)
SEEDS = (8201, 8202, 8203)                 # entirely unseen
STATES = ("u", "v", "random")
WINDOW = 800
CADENCE = 100
DELTA_T = 300                              # O4': behaviour is measured DELTA_T steps in the FUTURE
PR_MAX = 0.15
RG_MAX = 8.0
OCC_MAX = 0.15
COMP_MAX = 0.15
FRAG_MIN = 0.05                            # largest entity must hold >= 5% of above-threshold material
PERSIST_MIN = 0.8
TURNOVER_M = 0.5
TURNOVER_LAG_STEPS = (400, 600)            # material half-life = ln2/(k*dt) = 268 steps; the lag spans one
R_PARTIAL_MIN = 0.30


def _viability(st: SCState, rho_max: float) -> dict:
    rho = st.rho
    pr = participation_ratio(rho)
    occ = {t: float((rho > t * rho_max).mean()) for t in THRESHOLD_BAND}
    ergs = {t: entity_radius_of_gyration(rho, t * rho_max)[0] for t in THRESHOLD_BAND}
    comp = {t: _largest_component(rho > t * rho_max) / rho.size for t in THRESHOLD_BAND}
    ents = detect(st, DET, rho_max)
    above = float((rho > DET.threshold * rho_max).sum())
    biggest = max((e.size for e in ents), default=0)
    frag = biggest / above if above > 0 else 0.0
    return {
        "pr": pr, "occ": occ, "entity_rg": ergs, "comp": comp,
        "mass": float(rho.sum()), "n_entities": len(ents),
        "largest_entity_cells": biggest, "largest_entity_share": frag,
        # REPORTED, not thresholded:
        "sizes": [e.size for e in ents], "rgs": [e.rg for e in ents],
        "masses": [e.mass for e in ents], "densities": [e.mass / e.size for e in ents],
        "loc": bool(pr <= PR_MAX and all(v <= RG_MAX for v in ergs.values())
                    and all(v <= OCC_MAX for v in occ.values())),
        "no_invasion": bool(all(v <= COMP_MAX for v in comp.values())),
        "not_extinct": bool(float(rho.sum()) > 1e-3 and len(ents) > 0),
        "not_fragmented": bool(biggest >= DET.min_cells and frag >= FRAG_MIN),
    }


def o2prime(sp: ScaffoldSpec, seed: int, state: str) -> dict:
    eng = ScaffoldEngine(sp, TRACER)
    st = seed_state(sp, TRACER, seed, state)
    for _ in range(T_STAR):
        st = eng.step(st)
    v0 = _viability(st, sp.rho_max)
    snaps = eng.simulate(st, WINDOW, CADENCE)[1:]
    vs = [_viability(s, sp.rho_max) for s in snaps]
    persist = float(np.mean([v["not_extinct"] for v in vs]))
    # continued turnover of the largest entity, lags declared in STEPS (observer-independent)
    chain = []
    for s in snaps:
        es = detect(s, DET, sp.rho_max)
        chain.append(max(es, key=lambda e: e.size).cohort_mass if es else None)
    alive = [c for c in chain if c is not None]
    turn = False
    for lag in TURNOVER_LAG_STEPS:
        j = max(1, lag // CADENCE)
        for i in range(len(alive) - j):
            if rd_material_retention(alive[i], alive[i + j]) < TURNOVER_M:
                turn = True
    ok = bool(v0["loc"] and v0["no_invasion"] and v0["not_extinct"] and v0["not_fragmented"]
              and all(v["loc"] and v["no_invasion"] and v["not_fragmented"] for v in vs)
              and persist >= PERSIST_MIN and turn)
    return {"state": state, "seed": seed, "t_star": v0, "persistence": persist,
            "continued_turnover": turn, "passes": ok}


def o4prime_records(sp: ScaffoldSpec, seed: int, state: str) -> list[dict]:
    """Per-entity: internal state + trivial morphology NOW, specific uptake DELTA_T steps in the FUTURE."""
    eng = ScaffoldEngine(sp, TRACER)
    st = seed_state(sp, TRACER, seed, state)
    for _ in range(T_STAR):
        st = eng.step(st)
    now = detect(st, DET, sp.rho_max)
    if not now:
        return []
    fut = st.copy()
    for _ in range(DELTA_T):
        fut = eng.step(fut)
    later = detect(fut, DET, sp.rho_max)
    n = sp.size
    out = []
    for e in now:
        if not later:
            continue
        m = min(later, key=lambda z: np.linalg.norm(minimum_image(np.asarray(z.centroid) - np.asarray(e.centroid), n)))
        d = float(np.linalg.norm(minimum_image(np.asarray(m.centroid) - np.asarray(e.centroid), n)))
        if d > 8.0:
            continue
        out.append({"sig": e.mean_sig, "mass": e.mass, "rg": e.rg,
                    "density": e.mass / e.size, "size": float(e.size),
                    "future_uptake": m.specific_uptake})
    return out


def qualify_beta(beta: float) -> dict:
    sp = replace(SPEC, beta=beta)
    o2 = [o2prime(sp, sd, stt) for sd in SEEDS for stt in STATES]
    recs: list[dict] = []
    for sd in SEEDS:
        for stt in STATES:
            recs += o4prime_records(sp, sd, stt)
    if len(recs) >= 8:
        y = np.array([r["future_uptake"] for r in recs])
        x = np.array([r["sig"] for r in recs])
        Z = np.array([[r["mass"], r["rg"], r["density"], r["size"]] for r in recs])
        o4 = partial_correlation_test(y, x, Z, n_perm=2000, seed=11)
    else:
        o4 = {"r_partial": 0.0, "p_permutation": 1.0, "n": len(recs), "passes": False}
    return {"beta": beta, "O2prime": o2, "O2prime_pass": all(r["passes"] for r in o2),
            "O4prime": o4, "O4prime_pass": bool(o4["passes"]),
            "qualifies": bool(all(r["passes"] for r in o2) and o4["passes"])}
