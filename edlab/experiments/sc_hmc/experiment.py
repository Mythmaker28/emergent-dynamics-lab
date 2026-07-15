"""Per-seed measurement: builds the full record used by every downstream analysis.

Timeline per seed (all under the FROZEN physics, beta=0.10):
    warmup (2000)  ->  t0 relabel pulse-chase  ->  EARLY (t_c - offset)  ->  CHECKPOINT t_c
At EARLY we record the entity's OWN earlier causal response (R_early) and early axes/material.
At t_c we build arms H/P/M/U/C and record each arm's future causal response and axes, plus M(t0,t_c).
"""
from __future__ import annotations

import numpy as np

from . import config as C
from . import harness as H
from . import axes as AX
from . import arms as ARMS
from . import interventions as I


def _entity_external(st, e):
    """Visible external-field summary over the entity mask (mean c, mean N) - snapshot-accessible."""
    if e is None:
        return np.array([0.0, 0.0])
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    return np.array([float(st.c[ys, xs].mean()), float(st.N[ys, xs].mean())])


def battery(st, eng=None) -> dict:
    """Run the frozen intervention battery ONCE; return both the full causal-response PROFILE (concat)
    and the per-family MAGNITUDE 4-vec. Avoids evolving the battery twice per arm."""
    fam = I.response_by_family(H.pulse_chase_engine() if eng is None else eng, st,
                               horizon=C.RESPONSE_HORIZON, cadence=30)
    profile = np.concatenate([fam[name] for name, _ in C.INTERVENTIONS])
    mags = np.array([np.linalg.norm(fam[name]) for name, _ in C.INTERVENTIONS])
    return {"profile": profile, "mags": mags}


def _resp_family_mag(st, eng=None) -> np.ndarray:
    return battery(st, eng)["mags"]


def build_unrelated_pool() -> list:
    """Warm up + evolve each unrelated seed to the checkpoint ONCE; cache (state,size,rg)."""
    pool = []
    for s in C.UNRELATED_SEEDS:
        st = H.advance(H.pulse_chase_engine(), H.relabel_pulse_chase(H.warmup(s)), C.CHECKPOINT)
        e = H.largest_entity(st)
        if e is not None:
            pool.append({"seed": s, "state": st, "size": float(e.size), "rg": float(e.rg)})
    return pool


def measure_seed(seed: int, pool: list) -> dict:
    rec: dict = {"seed": seed}
    eng = H.pulse_chase_engine()

    # --- warmup + pulse-chase label ----------------------------------------------------------
    st0 = H.relabel_pulse_chase(H.warmup(seed))

    # --- evolve to EARLY, recording a trajectory for P6 --------------------------------------
    traj = H.trajectory(eng, st0, C.CHECKPOINT - C.EARLY_OFFSET, cadence=25)
    st_early = traj[-1]
    e_early = H.largest_entity(st_early)
    if e_early is None:
        rec["valid"] = False
        return rec
    rec["M_early"] = H.material_continuity(e_early)
    lab_e, new_e = H.labelled_unlabelled(e_early)
    rec["mass_early"] = float(e_early.mass)
    rec["P1_early"] = AX.p1_geometry(st_early, e_early)
    rec["P2_early"] = AX.p2_internal(st_early, e_early)
    rec["P3_early"] = AX.p3_function(st_early, e_early)
    rec["ext_early"] = _entity_external(st_early, e_early)
    rec["R_early"] = _resp_family_mag(st_early)
    rec["path_early"] = AX.p6_path(traj)

    # --- evolve to CHECKPOINT t_c ------------------------------------------------------------
    traj2 = H.trajectory(eng, st_early, C.EARLY_OFFSET, cadence=25)
    st_tc = traj2[-1]
    e_tc = H.largest_entity(st_tc)
    if e_tc is None:
        rec["valid"] = False
        return rec
    rec["valid"] = True
    rec["M_tc"] = H.material_continuity(e_tc)
    rec["mass_tc"] = float(e_tc.mass)
    rec["ref_size"] = float(e_tc.size)
    rec["ref_rg"] = float(e_tc.rg)
    rec["path_full"] = AX.p6_path(traj + traj2)

    # --- ARM H (continuous history) ----------------------------------------------------------
    stH = ARMS.arm_H(st_tc)
    bH = battery(stH)
    rec["H"] = {
        "P1": AX.p1_geometry(stH), "P2": AX.p2_internal(stH), "P3": AX.p3_function(stH),
        "P4": bH["profile"], "P5": AX.p5_recovery(stH),
        "R": bH["mags"], "M": H.material_continuity(H.largest_entity(stH)),
    }

    # --- ARM P (phenotype-matched reset) -----------------------------------------------------
    stP = ARMS.arm_P(st_tc, seed)
    eP = H.largest_entity(stP)
    bP = battery(stP)
    rec["P"] = {"P1": AX.p1_geometry(stP), "P2": AX.p2_internal(stP), "P3": AX.p3_function(stP),
                "P4": bP["profile"], "R": bP["mags"],
                "M": H.material_continuity(eP) if eP else 1.0}

    # --- ARM M (material-retaining organizational reset) -------------------------------------
    stM = ARMS.arm_M(st_tc, seed)
    eM = H.largest_entity(stM)
    bM = battery(stM)
    rec["M_arm"] = {"P1": AX.p1_geometry(stM), "P2": AX.p2_internal(stM), "P3": AX.p3_function(stM),
                    "P4": bM["profile"], "R": bM["mags"],
                    "M": H.material_continuity(eM) if eM else 1.0}

    # --- ARM U (unrelated phenotype-matched) -------------------------------------------------
    best, best_d = None, np.inf
    for cand in pool:
        if cand["seed"] == seed:
            continue
        d = abs(np.log(cand["size"] + 1) - np.log(rec["ref_size"] + 1)) + abs(cand["rg"] - rec["ref_rg"]) / 3.0
        if d < best_d:
            best_d, best = d, cand
    if best is not None:
        stU = best["state"]
        bU = battery(stU)
        rec["U"] = {"P1": AX.p1_geometry(stU), "P2": AX.p2_internal(stU), "P3": AX.p3_function(stU),
                    "P4": bU["profile"], "R": bU["mags"],
                    "match_dist": float(best_d), "match_seed": best["seed"]}

    # --- ARM C (exact clone, independent noise) -> stochastic ceiling ------------------------
    rc = []
    for k in range(4):
        stc, engc = ARMS.arm_C(st_tc, seed, k)
        rc.append(_resp_family_mag(stc, eng=engc))
    rec["C"] = {"R_clones": rc}
    return rec


def summarize_distances(rec: dict) -> dict:
    """Section-10 comparison: is H's future response closest to its OWN earlier response?"""
    if not rec.get("valid"):
        return {}
    Re = rec["R_early"]
    out = {}
    out["d_H"] = float(np.linalg.norm(rec["H"]["R"] - Re))
    if "P" in rec:
        out["d_P"] = float(np.linalg.norm(rec["P"]["R"] - Re))
    if "M_arm" in rec:
        out["d_M"] = float(np.linalg.norm(rec["M_arm"]["R"] - Re))
    if "U" in rec:
        out["d_U"] 