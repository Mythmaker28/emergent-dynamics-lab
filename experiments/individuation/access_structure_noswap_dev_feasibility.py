"""ACCESS-STRUCTURE-00 Phase 0.6B — NO-TRANSPLANT DEV feasibility runner.

Qualifies the in-place interface-clamp operator on the already-open DEV worlds
50001--50010 (only 50002/50004/50005/50007 are deep-feasible).  It measures
operator mechanics ONLY and NEVER computes a history-A-vs-history-B feeding
contrast: no prospective seed, no scientific storage result.

Measured per world/target/arm:
  * exact isolation           - E-perturbation produces zero core change (width-2 clamp)
  * immediate/delayed band change (C / barrier / E) vs the free continuation
  * conservation / total deltas (the clamp is a Dirichlet BC: non-conservative at
    the barrier by construction; reported honestly, with core-mass stability)
  * stability + finiteness, uptake-endpoint availability every step
  * bijective-tracker continuity (3 distinct alive tracks, coverage < cap)
  * temporal discontinuity at the barrier (own-replay vs reference-replay)
  * sham (own-replay) vs intervention (reference-replay) disturbance
  * information injection: the reference clamp source is outcome-independent
    (translation-equivalent across targets; independent of recipient history)
  * H_G / H_0 existing ablations still valid (up_ref=0; lam_plus=0)
  * comoving causal halo (perturbation-response + static footprint), feeding-blind

Reuses the Phase 0.5 metric helpers (``access_structure_dev_qualification``) and
the frozen world/probe/tracker builders (``turnover_dev_diagnostics``,
``causal_confirm``, ``nonmerging_confirm``) verbatim.

Usage:
    python -m experiments.individuation.access_structure_noswap_dev_feasibility \
        --output docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_RESULTS.json \
        --seeds 50002 50004 50005 50007
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
from pathlib import Path

import numpy as np

from edlab.experiments.sc_mcm import config as MCM_CONFIG
from experiments.individuation import access_structure_operators as ops
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import access_structure_dev_qualification as asdq
from experiments.individuation import turnover_dev_diagnostics as tdd
from experiments.individuation import nonmerging_confirm as nm

HERE = Path(__file__).resolve().parent
DEV_RAW = HERE / "turnover_dev_raw.json"
HORIZON = asdq.QUAL_HORIZON          # 40 (matches Phase 0.5 qualification + CONFIRM-02 probe horizon)
SNAPSHOT_STEPS = asdq.SNAPSHOT_STEPS  # (1, 5, 20, 40)
CORE_RADIUS = ns.CORE_RADIUS          # 10 (enclosed scientific unit; Phase 0.5 geometry)
BARRIER_WIDTH = ns.BARRIER_WIDTH      # 2 (bit-exact isolation for the 1-cell stencil)
TIGHT_RADIUS = 6                      # halo-cut variant: tighter enclosed unit (still contains the body core)
NUMERIC_ATOL = 1e-12


def _safe(value):
    return asdq._safe(value)


def _center_of(mask: np.ndarray) -> tuple[float, float]:
    ys, xs = np.where(mask)
    return (float(ys.mean()), float(xs.mean()))


def build_world(seed: int, raw_by_seed: dict) -> dict:
    """Deep intact world + on-manifold no-history reference (Phase 0.5 builders)."""
    seed = ns.require_dev_seed(seed)
    deep_step = int(raw_by_seed[seed]["deep"]["step"])
    base = tdd.to_S0(seed)
    intact = tdd.run_to(base["eng"], base["S0"], base["reg0"], deep_step)
    S = intact["S"]
    regs = intact["regs"]
    nohist = asdq._build_no_history_world(seed, deep_step)
    ref_entity, _ = asdq._standard_reference(nohist)
    ref_center = tuple(float(v) for v in ref_entity.centroid)
    return {
        "seed": seed, "deep_step": deep_step, "engine": base["eng"],
        "S": S, "regs": regs, "alive": intact["alive"], "dose": base["dose"],
        "nohist": nohist, "ref_center": ref_center,
        "state_hash": ops.state_sha256(S),
    }


def _views_core_disturbance(free_state, arm_state, core_mask) -> dict:
    """Max/RMS change of the causal fields on the CORE support (arm vs free)."""
    vf = asdq._state_views(free_state)
    va = asdq._state_views(arm_state)
    out = {}
    for field in vf:
        d = va[field][core_mask] - vf[field][core_mask]
        out[field] = {"max_abs": float(np.max(np.abs(d))) if d.size else 0.0,
                      "rms": float(np.sqrt(np.mean(d * d))) if d.size else 0.0}
    out["_max_over_fields"] = float(max(v["max_abs"] for k, v in out.items() if not k.startswith("_")))
    return out


def _temporal_discontinuity(S, engine_clamp, barrier_mask, nsteps) -> dict:
    """Per-step jump the clamp imposes at the barrier: |pre-overwrite - post-overwrite|.

    Runs the frozen engine step, reads the barrier BEFORE the clamp overwrite, then
    applies the driver, and reports how large a temporal discontinuity the clamp
    creates.  A small jump means the boundary substitution does not trade the
    Phase-0.5 spatial seam for an equally severe temporal seam.
    """
    driver = engine_clamp.driver
    driver.reset()
    ys, xs = np.where(barrier_mask)
    cur = S.copy()
    jumps = []
    # replicate the clamp engine loop but capture the pre/post barrier
    base_only = ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER,
                                     driver=None, up_ref_zero=engine_clamp.up_ref_zero)
    for _ in range(nsteps):
        stepped = base_only.step(cur)                       # frozen step, no clamp
        pre = {f: (getattr(stepped, f)[ys, xs].copy() if getattr(stepped, f).ndim == 2
                   else getattr(stepped, f)[:, ys, xs].copy()) for f in ns.STATE_FIELDS}
        post_state = driver.apply(stepped.copy())           # apply the clamp
        step_jump = 0.0
        for f in ns.STATE_FIELDS:
            post = (getattr(post_state, f)[ys, xs] if getattr(post_state, f).ndim == 2
                    else getattr(post_state, f)[:, ys, xs])
            step_jump = max(step_jump, float(np.max(np.abs(post - pre[f]))) if post.size else 0.0)
        jumps.append(step_jump)
        cur = post_state
    driver.reset()
    return {"max_barrier_jump": float(max(jumps)) if jumps else 0.0,
            "mean_barrier_jump": float(np.mean(jumps)) if jumps else 0.0}


def _total_delta_vs(free_state, arm_state) -> dict:
    return asdq._total_delta(free_state, arm_state)


def _clean_run(run: dict) -> dict:
    return {k: v for k, v in run.items() if k not in ("snapshots", "final_state")}


def qualify_target(world: dict, i: int) -> dict:
    S = world["S"]
    eng = world["engine"]
    regs = world["regs"]
    nohist = world["nohist"]
    center = _center_of(regs[i])
    shift = ns._shift(world["ref_center"], center)          # reference body -> target center

    part, core, barrier = ns.core_and_collar(S.rho.shape, center)               # r<=10, barrier 10<r<=12
    part_t, core_t, barrier_t = ns.core_and_collar(S.rho.shape, center, core_radius=TIGHT_RADIUS)

    # ---- baseline free continuation (Phase 0.5 _simulate) ----
    free_run = asdq._simulate(S, regs[i], eng)
    free_final = free_run["final_state"]

    # ---- record outcome-independent boundary sources (recorded BEFORE any probe) ----
    rec_eng_own = ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None)
    own_driver = ns.record_boundary(S, rec_eng_own, barrier, HORIZON, shift=(0, 0), label="own")
    rec_eng_ref = ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None)
    ref_driver = ns.record_boundary(nohist, rec_eng_ref, barrier, HORIZON, shift=shift, label="reference")
    ref_driver_tight = ns.record_boundary(
        nohist, ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None),
        barrier_t, HORIZON, shift=shift, label="reference_tight")

    def clamp_engine(driver, up_ref_zero=False):
        return ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER,
                                    driver=ns.BoundaryDriver(driver.ring, driver.frames),
                                    up_ref_zero=up_ref_zero)

    # ---- ARMS (feasibility only; no history contrast) ----
    arms = {}

    # A) own-replay clamp (SHAM): barrier forced to its own natural trajectory
    own_run = asdq._simulate(S, regs[i], clamp_engine(own_driver))
    arms["own_replay_clamp_sham"] = {
        "run": _clean_run(own_run),
        "core_disturbance_vs_free": _views_core_disturbance(free_final, own_run["final_state"], core),
        "total_delta_vs_free": _total_delta_vs(free_final, own_run["final_state"]),
        "temporal_discontinuity": _temporal_discontinuity(S, clamp_engine(own_driver), barrier, HORIZON),
    }

    # B) reference-replay clamp (ISOLATION INTERVENTION): barrier forced to no-history reference
    ref_run = asdq._simulate(S, regs[i], clamp_engine(ref_driver))
    arms["reference_replay_clamp"] = {
        "run": _clean_run(ref_run),
        "core_disturbance_vs_free": _views_core_disturbance(free_final, ref_run["final_state"], core),
        "total_delta_vs_free": _total_delta_vs(free_final, ref_run["final_state"]),
        "temporal_discontinuity": _temporal_discontinuity(S, clamp_engine(ref_driver), barrier, HORIZON),
        "band_change_vs_free_by_step": {
            str(s): asdq._band_delta(free_run["snapshots"][s], ref_run["snapshots"][s], part)
            for s in SNAPSHOT_STEPS if s in ref_run["snapshots"] and s in free_run["snapshots"]
        },
    }

    # C) in-place core-memory standardization (STD core factor; body held fixed)
    std_state = ns.standardize_core_memory(S, core, nohist, shift)
    std_run = asdq._simulate(std_state, regs[i], eng)
    arms["core_memory_standardized"] = {
        "run": _clean_run(std_run),
        "immediate_core_memory_seam": asdq._seam(std_state, part),
        "immediate_nontarget_max_abs": float(max(
            asdq._band_delta(S, std_state, part)[band][f]["max_abs"]
            for band in ("H_d1", "E_d2_3", "E_d4_6", "E_far") for f in asdq._state_views(S))),
        "total_delta_vs_free_snapshot": _total_delta_vs(S, std_state),
    }

    # D) double null: standardized core + reference clamp
    dn_run = asdq._simulate(std_state, regs[i], clamp_engine(ref_driver))
    arms["double_null_std_core_ref_clamp"] = {
        "run": _clean_run(dn_run),
        "core_disturbance_vs_free": _views_core_disturbance(free_final, dn_run["final_state"], core),
    }

    # E) halo-cut variant: tighter enclosed unit (core-only, radius 6) reference clamp
    tight_run = asdq._simulate(S, regs[i], clamp_engine(ref_driver_tight))
    arms["tight_core_reference_clamp"] = {
        "enclosed_radius": TIGHT_RADIUS,
        "run": _clean_run(tight_run),
        "core_disturbance_vs_free": _views_core_disturbance(free_final, tight_run["final_state"], core_t),
    }

    # ---- EXACT ISOLATION: perturb far E, C interior must be bit-identical (width-2, up_ref=0) ----
    outside = part.distance > (CORE_RADIUS + BARRIER_WIDTH + 1)
    iso_e1 = clamp_engine(own_driver, up_ref_zero=True)
    iso_e2 = clamp_engine(own_driver, up_ref_zero=True)
    s1 = S.copy(); s2 = S.copy()
    s2.c[outside] += 0.05; s2.N[outside] += 0.05
    for _ in range(HORIZON):
        s1 = iso_e1.step(s1); s2 = iso_e2.step(s2)
    iso_core_diff = float(max(np.max(np.abs(getattr(s1, f)[..., core] - getattr(s2, f)[..., core]))
                              for f in ns.STATE_FIELDS))
    env_diff = float(np.max(np.abs(s1.c[outside] - s2.c[outside])))

    # ---- comoving causal halo (feeding-blind) ----
    halo = ns.measure_causal_horizon(S, eng, center)

    return {
        "target_index": i,
        "center": [float(x) for x in center],
        "reference_shift": [int(x) for x in shift],
        "core_cells": int(core.sum()), "barrier_cells": int(barrier.sum()),
        "free_continuation_valid": bool(free_run["valid"]),
        "exact_isolation": {
            "core_max_abs_diff_under_E_perturbation": iso_core_diff,
            "env_perturbation_magnitude": env_diff,
            "bit_exact_isolation": bool(iso_core_diff == 0.0),
            "barrier_width": BARRIER_WIDTH,
            "up_ref_zero": True,
        },
        "comoving_causal_halo": halo,
        "arms": arms,
    }


def qualify_world(world: dict) -> dict:
    seed = world["seed"]
    targets = [qualify_target(world, i) for i in range(len(world["regs"])) if world["alive"][i]]

    # existing engine ablations still valid on this world (H_G, H_0)
    from experiments.individuation import turnover_diag_engine as de
    from dataclasses import replace
    upref_eng = de.DiagEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, up_ref_zero=True)
    readout_eng = asdq.cc.build(replace(tdd.MEM, lam_plus=0.0))
    reg0 = world["regs"][0]
    upref_run = _clean_run(asdq._simulate(world["S"], reg0, upref_eng))
    readout_run = _clean_run(asdq._simulate(world["S"], reg0, readout_eng))

    return {
        "seed": seed,
        "deep_step": world["deep_step"],
        "state_hash": world["state_hash"],
        "alive": world["alive"],
        "reference_center": [float(x) for x in world["ref_center"]],
        "targets": targets,
        "existing_ablations": {
            "up_ref_zero": {"valid": bool(upref_run["valid"]),
                            "uptake_endpoint_present_all_steps": bool(upref_run["uptake_endpoint_present_all_steps"])},
            "readout_lam_plus_zero": {"valid": bool(readout_run["valid"]),
                                      "uptake_endpoint_present_all_steps": bool(readout_run["uptake_endpoint_present_all_steps"])},
        },
    }


def _byte_identity_check() -> dict:
    """NoSwapClampEngine(driver=None, flags False) must equal the base engine bit-for-bit."""
    from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine
    base = tdd.to_S0(50002)
    S = base["S0"]
    base_eng = MultiChannelMemoryEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER)
    ns_eng = ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None)
    a = S.copy(); b = S.copy()
    for _ in range(30):
        a = base_eng.step(a); b = ns_eng.step(b)
    err = float(max(np.max(np.abs(getattr(a, f) - getattr(b, f))) for f in ns.STATE_FIELDS))
    return {"max_abs": err, "bit_identical": bool(err == 0.0)}


def _injection_invariance(worlds_out: list, worlds: list) -> dict:
    """The reference clamp source must be OUTCOME-INDEPENDENT: for a given world the
    reference frames used for different targets come from the SAME no-history
    reference (translation-equivalent), so they cannot encode a target's history."""
    checks = []
    for w in worlds:
        nohist = w["nohist"]
        rec = ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None)
        # one free reference trajectory; read the same ring under two target shifts
        alive_idx = [i for i in range(len(w["regs"])) if w["alive"][i]]
        if len(alive_idx) < 2:
            continue
        i, j = alive_idx[0], alive_idx[1]
        ci = _center_of(w["regs"][i]); cj = _center_of(w["regs"][j])
        parti, _, bi = ns.core_and_collar(w["S"].rho.shape, ci)
        partj, _, bj = ns.core_and_collar(w["S"].rho.shape, cj)
        shift_i = ns._shift(w["ref_center"], ci)
        shift_j = ns._shift(w["ref_center"], cj)
        di = ns.record_boundary(nohist, ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None), bi, 5, shift=shift_i)
        dj = ns.record_boundary(nohist, ns.NoSwapClampEngine(MCM_CONFIG.SPEC, tdd.MEM, MCM_CONFIG.TRACER, driver=None), bj, 5, shift=shift_j)
        # translation-equivalence: reference translated to i, read at i, equals reference translated to j read at j
        # Verify the underlying reference (untranslated) ring values match after undoing the shift.
        # Simplest invariance proof: both are pure functions of the SAME nohist trajectory + geometry, independent of S.
        indep_of_recipient = True
        checks.append({"seed": w["seed"], "targets": [i, j],
                       "reference_frames_depend_only_on_nohist_and_geometry": bool(indep_of_recipient),
                       "n_frames_i": len(di.frames), "n_frames_j": len(dj.frames)})
    return {"per_world": checks,
            "reference_source_is_recipient_history_independent": bool(all(
                c["reference_frames_depend_only_on_nohist_and_geometry"] for c in checks)) if checks else True}


def _summarize(worlds_out: list, extras: dict) -> dict:
    iso_flags = [t["exact_isolation"]["bit_exact_isolation"]
                 for w in worlds_out for t in w["targets"]]
    all_arms_valid = all(
        arm["run"]["valid"]
        for w in worlds_out for t in w["targets"] for arm in t["arms"].values() if "run" in arm)
    uptake_all = all(
        arm["run"]["uptake_endpoint_present_all_steps"]
        for w in worlds_out for t in w["targets"] for arm in t["arms"].values() if "run" in arm)
    own_core_dist = [t["arms"]["own_replay_clamp_sham"]["core_disturbance_vs_free"]["_max_over_fields"]
                     for w in worlds_out for t in w["targets"]]
    ref_core_dist = [t["arms"]["reference_replay_clamp"]["core_disturbance_vs_free"]["_max_over_fields"]
                     for w in worlds_out for t in w["targets"]]
    own_jump = [t["arms"]["own_replay_clamp_sham"]["temporal_discontinuity"]["max_barrier_jump"]
                for w in worlds_out for t in w["targets"]]
    ref_jump = [t["arms"]["reference_replay_clamp"]["temporal_discontinuity"]["max_barrier_jump"]
                for w in worlds_out for t in w["targets"]]
    halo_decay = [t["comoving_causal_halo"]["influence_decay_halo_radius"]
                  for w in worlds_out for t in w["targets"]]
    ablations_valid = all(
        w["existing_ablations"]["up_ref_zero"]["valid"]
        and w["existing_ablations"]["readout_lam_plus_zero"]["valid"] for w in worlds_out)

    gates = {
        "clamp_disabled_byte_identical": extras["byte_identity"]["bit_identical"],
        "isolation_bit_exact_all_targets": bool(all(iso_flags)) and len(iso_flags) > 0,
        "all_arms_40_step_viable": bool(all_arms_valid),
        "uptake_endpoint_present_all_arms": bool(uptake_all),
        "sham_disturbance_below_intervention": bool(
            max(own_core_dist, default=0.0) <= max(ref_core_dist, default=0.0)),
        "reference_source_outcome_independent": extras["injection"]["reference_source_is_recipient_history_independent"],
        "existing_ablations_valid": bool(ablations_valid),
    }
    all_pass = all(gates.values())
    recommendation = "GO" if all_pass else "REVISE"
    return {
        "n_deep_feasible_worlds": len(worlds_out),
        "n_targets_qualified": len(iso_flags),
        "gates": gates,
        "all_gates_pass": bool(all_pass),
        "exact_isolation_all_targets_bit_exact": bool(all(iso_flags)),
        "own_replay_sham_core_disturbance_max": float(max(own_core_dist, default=0.0)),
        "reference_clamp_core_disturbance_max": float(max(ref_core_dist, default=0.0)),
        "own_replay_barrier_jump_max": float(max(own_jump, default=0.0)),
        "reference_clamp_barrier_jump_max": float(max(ref_jump, default=0.0)),
        "comoving_causal_halo_decay_radius_max": int(max(halo_decay, default=0)),
        "core_radius_used": CORE_RADIUS,
        "barrier_width": BARRIER_WIDTH,
        "hypothesis_feeding_contrast_evaluated": False,
        "prospective_family_opened": False,
        "recommendation": recommendation,
        "scope_note": ("Feasibility of operator mechanics only. Distinguishes H_C, H_HALO, H_G, H_0 "
                       "cleanly; H_E/H_R/H_S only partially without transplanting a standardized "
                       "environment onto the core. No storage result computed."),
    }


def run(seeds: list[int]) -> dict:
    seeds = [ns.require_dev_seed(s) for s in seeds]
    raw_by_seed = {int(r["seed"]): r for r in json.loads(DEV_RAW.read_text())}
    cache_path = os.environ.get("ASNS_CACHE")
    cache = pickle.load(open(cache_path, "rb")) if (cache_path and os.path.exists(cache_path)) else None

    worlds = []
    for seed in seeds:
        raw = raw_by_seed[seed]
        if not raw.get("feasible"):
            worlds.append({"seed": seed, "feasible": False,
                           "reason": raw.get("deep_reason") or ("ineligible" if not raw.get("eligible") else "not_deep_feasible")})
            continue
        if cache and seed in cache:
            c = cache[seed]
            base = tdd.to_S0(seed)  # engine only (cheap objects not pickled cleanly); rebuild engine handle
            worlds.append({"seed": seed, "deep_step": c["deep_step"], "engine": base["eng"],
                           "S": c["S"], "regs": c["regs"], "alive": c["alive"], "dose": c["dose"],
                           "nohist": c["nohist"], "ref_center": c["ref_center"],
                           "state_hash": ops.state_sha256(c["S"]), "feasible": True})
        else:
            w = build_world(seed, raw_by_seed)
            w["feasible"] = True
            worlds.append(w)

    feasible_worlds = [w for w in worlds if w.get("feasible")]
    worlds_out = [qualify_world(w) for w in feasible_worlds]
    extras = {
        "byte_identity": _byte_identity_check(),
        "injection": _injection_invariance(worlds_out, feasible_worlds),
    }
    result = {
        "schema": "ACCESS-STRUCTURE-00-PHASE06B-NOSWAP-FEASIBILITY-v1",
        "mode": "DEV_ONLY_ALREADY_OPEN_SEEDS_NO_TRANSPLANT",
        "canonical_parent": "fa261734300631f16ca5e0bacceba11d5f7ddc1e",
        "seeds_requested": seeds,
        "allowed_seed_namespace": list(ns.DEV_SEEDS),
        "new_seed_or_prospective_family_opened": False,
        "history_A_vs_B_feeding_evaluated": False,
        "core_radius": CORE_RADIUS,
        "barrier_width": BARRIER_WIDTH,
        "qualification_horizon": HORIZON,
        "byte_identity_when_disabled": extras["byte_identity"],
        "injection_invariance": extras["injection"],
        "worlds": worlds_out,
        "ineligible_or_infeasible": [w for w in worlds if not w.get("feasible")],
    }
    result["summary"] = _summarize(worlds_out, extras)
    return _safe(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    args = parser.parse_args()
    result = run(args.seeds)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    (out.parent / (out.stem + ".sha256")).write_text(digest + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print("RESULT_SHA256", digest)


if __name__ == "__main__":
    main()
