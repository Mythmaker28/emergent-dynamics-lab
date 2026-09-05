"""EXP-SC-00 orthogonality qualification O1-O4. NO R8 screen until these pass. NO law map. NO GATE-0."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from ..substrates.scaffold.engine import ScaffoldSpec, SCState, ScaffoldEngine
from ..substrates.scaffold.observables import SCDetectionSpec, detect
from ..substrates.chemotaxis.diagnostics import participation_ratio, entity_radius_of_gyration, THRESHOLD_BAND
from ..substrates.reaction_diffusion.engine import TracerSpec

TRACER = TracerSpec(n_spatial=4, n_temporal=8, tau_feed=200)
DET = SCDetectionSpec()
SPEC = ScaffoldSpec()
T_STAR = 2000
PR_MAX = 0.15
RG_MAX = 8.0
OCC_MAX = 0.15
# O2 tolerances (frozen)
D_PR_TOL = 0.05
D_RG_TOL = 1.5
# O4 margin (frozen): flipping the internal state must change future specific uptake by >= 10% (relative)
O4_MARGIN = 0.10


def r7(st: SCState, rho_max: float) -> dict:
    rho = st.rho
    pr = participation_ratio(rho)
    occ = {t: float((rho > t * rho_max).mean()) for t in THRESHOLD_BAND}
    ergs = {t: entity_radius_of_gyration(rho, t * rho_max)[0] for t in THRESHOLD_BAND}
    localized = bool(float(rho.sum()) > 1e-3 and pr <= PR_MAX
                     and all(v <= RG_MAX for v in ergs.values())
                     and all(v <= OCC_MAX for v in occ.values()))
    rgm = max(v for v in ergs.values() if np.isfinite(v)) if any(np.isfinite(v) for v in ergs.values()) else np.inf
    return {"pr": pr, "rg": rgm, "localized": localized, "n_entities": len(detect(st, DET, rho_max))}


def seed_state(sp: ScaffoldSpec, tr: TracerSpec, seed: int, internal: str = "random") -> SCState:
    rng = np.random.default_rng(seed)
    n = sp.size
    rho = np.clip(0.25 * sp.rho_max + 0.02 * rng.standard_normal((n, n)), 0.0, sp.rho_max)
    if internal == "u":
        u = np.full((n, n), 1.6); v = np.full((n, n), 0.1)
    elif internal == "v":
        u = np.full((n, n), 0.1); v = np.full((n, n), 1.6)
    elif internal == "off":
        u = np.zeros((n, n)); v = np.zeros((n, n))
    else:
        u = 0.8 + 0.4 * rng.standard_normal((n, n))
        v = 0.8 + 0.4 * rng.standard_normal((n, n))
        u = np.clip(u, 0.0, None); v = np.clip(v, 0.0, None)
    C = np.zeros((tr.n_cohorts, n, n))
    ys = np.arange(n)[:, None] * np.ones((1, n))
    for q in range(tr.n_spatial):
        C[q] = np.where(((ys * tr.n_spatial) // n) % tr.n_spatial == q, rho, 0.0)
    return SCState(rho, rho * u, rho * v, np.zeros((n, n)), np.full((n, n), sp.N0), C, np.zeros((n, n)), 0)


def _run(sp: ScaffoldSpec, seed: int, internal: str, steps: int = T_STAR) -> SCState:
    eng = ScaffoldEngine(sp, TRACER)
    st = seed_state(sp, TRACER, seed, internal)
    for _ in range(steps):
        st = eng.step(st)
    return st


def orthogonality(seed: int = 8001) -> dict:
    out: dict = {}
    sp = SPEC

    # O1 -- the scaffold coheres with the internal network DISABLED (a = 0)
    off = replace(sp, a=0.0)
    st = _run(off, seed, "off")
    d = r7(st, sp.rho_max)
    out["O1_scaffold_only"] = {**d, "passes": d["localized"]}

    # O2 -- distinct internal states leave localization broadly intact
    states = {}
    for name in ("u", "v", "random"):
        s = _run(sp, seed, name)
        states[name] = r7(s, sp.rho_max)
    prs = [v["pr"] for v in states.values()]
    rgs = [v["rg"] for v in states.values()]
    out["O2_states"] = states
    out["O2"] = {"all_localized": all(v["localized"] for v in states.values()),
                 "d_pr": float(max(prs) - min(prs)), "d_rg": float(max(rgs) - min(rgs)),
                 "passes": bool(all(v["localized"] for v in states.values())
                                and (max(prs) - min(prs)) <= D_PR_TOL
                                and (max(rgs) - min(rgs)) <= D_RG_TOL)}

    # O3 -- the internal fields ALONE cannot create an entity (sub-threshold scaffold, any u/v)
    n = sp.size
    rng = np.random.default_rng(999)
    rho = np.full((n, n), 0.15 * sp.rho_max)                   # everywhere BELOW the detector threshold
    u = np.where(rng.random((n, n)) < 0.5, 2.0, 0.05)          # violently structured internal fields
    v = 2.05 - u
    C = np.stack([rho] + [np.zeros((n, n))] * (TRACER.n_cohorts - 1))
    probe = SCState(rho, rho * u, rho * v, np.zeros((n, n)), np.full((n, n), sp.N0), C, np.zeros((n, n)), 0)
    out["O3"] = {"n_entities_from_internal_fields_alone": len(detect(probe, DET, sp.rho_max)),
                 "max_rho": float(rho.max()), "passes": len(detect(probe, DET, sp.rho_max)) == 0}

    # O4 -- flipping the internal state must change FUTURE specific uptake; with beta = 0 it must NOT
    def flip_and_measure(spec):
        eng = ScaffoldEngine(spec, TRACER)
        base = _run(spec, seed, "u")
        flipped = base.copy()
        flipped.U, flipped.V = base.V.copy(), base.U.copy()     # flip the internal state ONLY
        res = {}
        for tag, s0 in (("keep", base), ("flip", flipped)):
            s = s0.copy()
            for _ in range(300):                                # measure a FUTURE observable
                s = eng.step(s)
            es = detect(s, DET, spec.rho_max)
            res[tag] = float(np.mean([e.specific_uptake for e in es])) if es else 0.0
        rel = abs(res["flip"] - res["keep"]) / (abs(res["keep"]) + 1e-12)
        return {**res, "relative_change": rel}

    on = flip_and_measure(sp)
    ctrl = flip_and_measure(replace(sp, beta=0.0))
    out["O4"] = {"beta_on": on, "beta_zero_NEGATIVE_CONTROL": ctrl, "margin": O4_MARGIN,
                 "passes": bool(on["relative_change"] >= O4_MARGIN and ctrl["relative_change"] < O4_MARGIN)}

    out["ALL_PASS"] = bool(out["O1_scaffold_only"]["passes"] and out["O2"]["passes"]
                           and out["O3"]["passes"] and out["O4"]["passes"])
    return out
