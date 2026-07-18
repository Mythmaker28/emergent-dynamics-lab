"""ACCESS-STRUCTURE-00 Phase 0.7 — CORE-SUFFICIENCY-00 DEV causal pilot.

Runs the predeclared 2x2 DEV factorial (M_OWN/M_STD x K_COUPLED/K_CLAMPED) under
the frozen CONFIRM-02 probe and two mechanistic controls (lam_plus=0, up_ref=0),
on the already-open deep-feasible DEV worlds 50002/50004/50005/50007.  DEV only;
no prospective seed; no confirmatory certification.

Predeclared estimands (per target, then aggregated within world):
    tau_clamped = Y(M_OWN, K_CLAMPED) - Y(M_STD, K_CLAMPED)
    tau_coupled = Y(M_OWN, K_COUPLED) - Y(M_STD, K_COUPLED)
    interaction = tau_clamped - tau_coupled
Y = integrated future feeding on the bijectively tracked target (nm.measure).

Reframed scope (CORE-SUFFICIENCY-00): a positive, control-surviving, reference-
robust result may support "local/core causal sufficiency under a standardized
boundary."  It cannot establish unique local ownership, absence of environmental
/ redundant / relational access, individual identity, or active reconstruction.

M_STD is a LOCAL MEMORY-FIELD intervention with body/geometry preserved (Task 1):
the target core intensive memory m=(m1,m2) is set to the translated same-seed
no-history twin's intensive memory (extensive Mf rebuilt on the target's own rho).
It is NOT "the standardized complete core."  Because the no-history twin carries
comparable AMBIENT memory, M_STD swaps history for an on-manifold baseline of
similar magnitude rather than removing memory; the erase reference (m->0) is run
as a reference-sensitivity control.

Nothing here selects endpoints, time points, references, or margins by maximizing
the DEV effect.  The 40-step horizon is the frozen primary endpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
from dataclasses import replace
from pathlib import Path

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation import turnover_diag_engine as de
from experiments.individuation import nonmerging_confirm as nm
from experiments.individuation import causal_confirm as cc
from experiments.individuation import access_structure_dev_qualification as asdq

HERE = Path(__file__).resolve().parent
DEV_RAW = HERE / "turnover_dev_raw.json"
EPS = 1e-12
SETTLE_STD = nm.SETTLE_STD          # 40
HORIZON = nm.HORIZON                # 40 (frozen primary endpoint)
STIM_AMP = nm.STIM_AMP              # 0.25
STIM_DUR = nm.STIM_DUR              # 5
MEM = tdd.MEM                       # MCParams(lam_plus=0.25, lam_minus=0.15, C1c)
TIME_POINTS = (0, 1, 5, 10, 20, 40)  # horizon-relative disturbance/propagation points


# ---------------------------------------------------------------- M interventions
def m_std_intensive(state, core_mask, twin, shift):
    """M_STD: set core intensive memory to the translated no-history twin memory;
    rebuild extensive Mf on the target's OWN rho (body/geometry preserved)."""
    out = state.copy()
    twin_m = twin.Mf / np.maximum(twin.rho, EPS)[None]
    twin_m_tr = np.roll(twin_m, shift, axis=(-2, -1))
    out.Mf[:, core_mask] = out.rho[core_mask][None, :] * twin_m_tr[:, core_mask]
    return out


def m_erase(state, core_mask):
    """Reference-sensitivity control: erase core memory (m->0)."""
    return ns.erase_core_memory(state, core_mask)


# ---------------------------------------------------------------- engines
def coupled_engine(mem, up_ref_zero):
    return de.DiagEngine(MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER, up_ref_zero=up_ref_zero)


def clamp_engine(mem, up_ref_zero, driver):
    return ns.NoSwapClampEngine(MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER,
                                driver=driver, up_ref_zero=up_ref_zero)


def record_reference_barrier(twin, barrier, shift, mem, up_ref_zero):
    """Record the translated twin barrier trajectory under the EXACT frozen probe
    forcing (N:=N0, settle, uniform stimulus), 80 frames, aligned to nm.measure."""
    eng = coupled_engine(mem, up_ref_zero)
    ys, xs = np.where(barrier)
    st = twin.copy()
    st.N = np.full_like(st.N, cc.N0)
    frames = []

    def rec(s):
        fr = {}
        for f in ns.STATE_FIELDS:
            arr = getattr(s, f)
            rolled = np.roll(arr, shift, axis=(-2, -1)) if shift != (0, 0) else arr
            fr[f] = rolled[ys, xs].copy() if arr.ndim == 2 else rolled[:, ys, xs].copy()
        return fr

    for _ in range(SETTLE_STD):
        st = eng.step(st); frames.append(rec(st))
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR:
            st.N = st.N + STIM_AMP
        st = eng.step(st); frames.append(rec(st))
    return ns.BoundaryDriver(ring=barrier.astype(bool), frames=frames, label="reference_probe")


def Y(state, cents, engine, i):
    r = nm.measure(state, cents, engine)
    return {"tracked": float(r["tracked"][i]), "fixed": float(r["fixed"][i]),
            "branch_valid": bool(r["branch_valid"]), "status": str(r["statuses"][i]),
            "max_cov": float(r["max_cov"])}


# ---------------------------------------------------------------- Task 4: memory survival
def core_memory_survival(S, core, twin, shift, mem, up_ref_zero, clamped, driver=None):
    """Track the core m_plus contrast |mean(m_plus_OWN) - mean(m_plus_STD)| on the body
    under the probe forcing, at horizon-relative TIME_POINTS. Feeding-blind."""
    own0 = S.copy()
    std0 = m_std_intensive(S, core, twin, shift)
    body = (S.rho > 0.30) & core

    def mplus(s):
        m = s.Mf / np.maximum(s.rho, EPS)[None]
        return np.tanh(m[0] + m[1])

    if clamped:
        eng_o = clamp_engine(mem, up_ref_zero, ns.BoundaryDriver(driver.ring, driver.frames))
        eng_s = clamp_engine(mem, up_ref_zero, ns.BoundaryDriver(driver.ring, driver.frames))
    else:
        eng_o = coupled_engine(mem, up_ref_zero)
        eng_s = coupled_engine(mem, up_ref_zero)
    o = own0.copy(); s = std0.copy()
    o.N = np.full_like(o.N, cc.N0); s.N = np.full_like(s.N, cc.N0)
    # settle
    for _ in range(SETTLE_STD):
        o = eng_o.step(o); s = eng_s.step(s)
    course = {}
    diff0 = float(np.abs(mplus(o)[body].mean() - mplus(s)[body].mean()))
    course["0"] = diff0
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR:
            o.N = o.N + STIM_AMP; s.N = s.N + STIM_AMP
        o = eng_o.step(o); s = eng_s.step(s)
        if t in TIME_POINTS:
            course[str(t)] = float(np.abs(mplus(o)[body].mean() - mplus(s)[body].mean()))
    init = float(np.abs(mplus(own0)[body].mean() - mplus(std0)[body].mean()))
    return {"initial_core_mplus_contrast": init, "by_horizon_step": course,
            "retained_fraction_step40": (course.get("40", 0.0) / init) if init > 0 else None}


# ---------------------------------------------------------------- per world
def _center_of(mask):
    ys, xs = np.where(mask)
    return (float(ys.mean()), float(xs.mean()))


def run_world(seed, world, condition):
    """condition in {'normal','lam_plus_zero','up_ref_zero'}."""
    if condition == "normal":
        mem, upref = MEM, False
    elif condition == "lam_plus_zero":
        mem, upref = replace(MEM, lam_plus=0.0), False
    elif condition == "up_ref_zero":
        mem, upref = MEM, True
    else:
        raise ValueError(condition)

    S = world["S"]; regs = world["regs"]; twin = world["nohist"]; refc = world["ref_center"]
    cents = [_center_of(regs[i]) for i in range(len(regs))]
    per_target = []
    for i in range(len(regs)):
        if not world["alive"][i]:
            continue
        center = cents[i]
        part, core, barrier = ns.core_and_collar(S.rho.shape, center)
        shift = ns._shift(refc, center)
        driver = record_reference_barrier(twin, barrier, shift, mem, upref)

        own = S.copy()
        std = m_std_intensive(S, core, twin, shift)
        ceng = coupled_engine(mem, upref)
        y_own_coupled = Y(own, cents, ceng, i)
        y_std_coupled = Y(std, cents, coupled_engine(mem, upref), i)
        y_own_clamped = Y(own, cents, clamp_engine(mem, upref, ns.BoundaryDriver(driver.ring, driver.frames)), i)
        y_std_clamped = Y(std, cents, clamp_engine(mem, upref, ns.BoundaryDriver(driver.ring, driver.frames)), i)

        cell_valid = all(y["branch_valid"] for y in (y_own_coupled, y_std_coupled, y_own_clamped, y_std_clamped))
        rec = {
            "target": i, "center": [round(x, 2) for x in center], "shift": list(shift),
            "cells": {
                "M_OWN_K_COUPLED": y_own_coupled, "M_STD_K_COUPLED": y_std_coupled,
                "M_OWN_K_CLAMPED": y_own_clamped, "M_STD_K_CLAMPED": y_std_clamped,
            },
            "tau_coupled_tracked": y_own_coupled["tracked"] - y_std_coupled["tracked"],
            "tau_clamped_tracked": y_own_clamped["tracked"] - y_std_clamped["tracked"],
            "tau_coupled_fixed": y_own_coupled["fixed"] - y_std_coupled["fixed"],
            "tau_clamped_fixed": y_own_clamped["fixed"] - y_std_clamped["fixed"],
            "all_cells_valid": cell_valid,
        }
        rec["interaction_tracked"] = rec["tau_clamped_tracked"] - rec["tau_coupled_tracked"]

        if condition == "normal":
            # reference sensitivity: erase reference (m->0)
            er = m_erase(S, core)
            y_er_coupled = Y(er, cents, coupled_engine(mem, upref), i)
            y_er_clamped = Y(er, cents, clamp_engine(mem, upref, ns.BoundaryDriver(driver.ring, driver.frames)), i)
            rec["reference_sensitivity_erase"] = {
                "tau_coupled_tracked_vs_erase": y_own_coupled["tracked"] - y_er_coupled["tracked"],
                "tau_clamped_tracked_vs_erase": y_own_clamped["tracked"] - y_er_clamped["tracked"],
                "erase_branch_valid": bool(y_er_coupled["branch_valid"] and y_er_clamped["branch_valid"]),
            }
            rec["core_memory_survival_coupled"] = core_memory_survival(S, core, twin, shift, mem, upref, clamped=False)
            rec["core_memory_survival_clamped"] = core_memory_survival(S, core, twin, shift, mem, upref, clamped=True, driver=driver)
        per_target.append(rec)

    valid = [t for t in per_target if t["all_cells_valid"]]
    def agg(key):
        vals = [t[key] for t in valid]
        return float(np.mean(vals)) if vals else None
    return {
        "seed": seed, "condition": condition,
        "n_targets": len(per_target), "n_valid_targets": len(valid),
        "targets": per_target,
        "world_tau_coupled_tracked": agg("tau_coupled_tracked"),
        "world_tau_clamped_tracked": agg("tau_clamped_tracked"),
        "world_interaction_tracked": agg("interaction_tracked"),
        "world_tau_coupled_fixed": agg("tau_coupled_fixed"),
        "world_tau_clamped_fixed": agg("tau_clamped_fixed"),
    }


# ---------------------------------------------------------------- differential verification
def differential_check(world):
    """Independent path: nm.measure intact vs region-erase must reproduce the known
    own effect sign/scale (validates the probe machinery, second oracle)."""
    S = world["S"]; regs = world["regs"]
    cents = [_center_of(regs[i]) for i in range(len(regs))]
    eng = coupled_engine(MEM, False)
    intact = nm.measure(S, cents, eng)
    out = []
    for i in range(len(regs)):
        if not world["alive"][i]:
            continue
        er = nm.measure(S, cents, coupled_engine(MEM, False), erase_mask=regs[i])
        own = float(intact["tracked"][i] - er["tracked"][i])
        out.append({"target": i, "nm_region_erase_own_tracked": own,
                    "own_fraction": own / intact["tracked"][i] if intact["tracked"][i] else None})
    return out


def build_world(seed, raw_by_seed):
    deep_step = int(raw_by_seed[seed]["deep"]["step"])
    base = tdd.to_S0(seed)
    intact = tdd.run_to(base["eng"], base["S0"], base["reg0"], deep_step)
    nohist = asdq._build_no_history_world(seed, deep_step)
    ref_entity, _ = asdq._standard_reference(nohist)
    return {"seed": seed, "deep_step": deep_step, "S": intact["S"], "regs": intact["regs"],
            "alive": intact["alive"], "dose": base["dose"], "nohist": nohist,
            "ref_center": tuple(float(v) for v in ref_entity.centroid),
            "state_hash": ops.state_sha256(intact["S"])}


def run(seeds):
    seeds = [ns.require_dev_seed(s) for s in seeds]
    raw_by_seed = {int(r["seed"]): r for r in json.loads(DEV_RAW.read_text())}
    cache_path = os.environ.get("ASNS_CACHE")
    cache = pickle.load(open(cache_path, "rb")) if (cache_path and os.path.exists(cache_path)) else None

    worlds = []
    for seed in seeds:
        if not raw_by_seed[seed].get("feasible"):
            worlds.append({"seed": seed, "feasible": False,
                           "reason": raw_by_seed[seed].get("deep_reason") or "not_deep_feasible"})
            continue
        if cache and seed in cache:
            c = cache[seed]
            worlds.append({"seed": seed, "feasible": True, "deep_step": c["deep_step"], "S": c["S"],
                           "regs": c["regs"], "alive": c["alive"], "dose": c["dose"], "nohist": c["nohist"],
                           "ref_center": c["ref_center"], "state_hash": ops.state_sha256(c["S"])})
        else:
            w = build_world(seed, raw_by_seed); w["feasible"] = True; worlds.append(w)

    feasible = [w for w in worlds if w.get("feasible")]
    conditions = ["normal", "lam_plus_zero", "up_ref_zero"]
    results = {cond: [run_world(w["seed"], w, cond) for w in feasible] for cond in conditions}
    diffcheck = {w["seed"]: differential_check(w) for w in feasible}

    def world_vec(cond, key):
        return [r[key] for r in results[cond] if r[key] is not None]

    def descr(vec):
        if not vec:
            return None
        a = np.array(vec, float)
        return {"n": len(vec), "values": [round(float(x), 6) for x in vec],
                "mean": float(a.mean()), "median": float(np.median(a)),
                "min": float(a.min()), "max": float(a.max()),
                "all_same_sign": bool(np.all(a > 0) or np.all(a < 0))}

    summary = {
        "n_deep_feasible_worlds": len(feasible),
        "statistical_unit": "original_world (targets aggregated within world by mean over valid targets)",
        "primary_endpoint": "integrated tracked uptake at horizon step 40 (frozen)",
        "normal": {
            "tau_coupled_tracked_worldlevel": descr(world_vec("normal", "world_tau_coupled_tracked")),
            "tau_clamped_tracked_worldlevel": descr(world_vec("normal", "world_tau_clamped_tracked")),
            "interaction_tracked_worldlevel": descr(world_vec("normal", "world_interaction_tracked")),
        },
        "lam_plus_zero": {
            "tau_coupled_tracked_worldlevel": descr(world_vec("lam_plus_zero", "world_tau_coupled_tracked")),
            "tau_clamped_tracked_worldlevel": descr(world_vec("lam_plus_zero", "world_tau_clamped_tracked")),
        },
        "up_ref_zero": {
            "tau_coupled_tracked_worldlevel": descr(world_vec("up_ref_zero", "world_tau_coupled_tracked")),
            "tau_clamped_tracked_worldlevel": descr(world_vec("up_ref_zero", "world_tau_clamped_tracked")),
        },
    }
    return {
        "schema": "ACCESS-STRUCTURE-00-PHASE07-CORE-SUFFICIENCY-v1",
        "mode": "DEV_ONLY_ALREADY_OPEN_SEEDS_NO_TRANSPLANT_NO_PROSPECTIVE",
        "canonical_parent": "fa261734300631f16ca5e0bacceba11d5f7ddc1e",
        "phase06b_tip": "7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b",
        "seeds_requested": seeds,
        "allowed_seed_namespace": list(ns.DEV_SEEDS),
        "new_seed_or_prospective_family_opened": False,
        "confirmatory_pvalue_or_certification_claimed": False,
        "predeclared_estimands": {
            "tau_clamped": "Y(M_OWN,K_CLAMPED) - Y(M_STD,K_CLAMPED)",
            "tau_coupled": "Y(M_OWN,K_COUPLED) - Y(M_STD,K_COUPLED)",
            "interaction": "tau_clamped - tau_coupled",
        },
        "M_STD_definition": ("intensive same-seed no-history twin core-memory standardization; body/geometry "
                             "preserved; NOT the standardized complete core"),
        "differential_verification_nm_region_erase": asdq._safe(diffcheck),
        "results_by_condition": asdq._safe(results),
        "summary": asdq._safe(summary),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--seeds", nargs="+", type=int, required=True)
    args = p.parse_args()
    result = run(args.seeds)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    (out.parent / (out.stem + ".sha256")).write_text(digest + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print("RESULT_SHA256", digest)


if __name__ == "__main__":
    main()
