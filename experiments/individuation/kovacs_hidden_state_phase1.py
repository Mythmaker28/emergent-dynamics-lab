"""KOVACS-HIDDEN-STATE-00 Phase-1 DEV natural-coincidence qualification engine.

HARD FIREWALL (Phase-1 constraint): NO scientific excursion outcome is computed.
This module records only the MATCHING trajectory up to the common-clock coincidence,
the overt physical panel, and a residual hidden-state (memory) DIAGNOSTIC at the
coincidence. It never computes, integrates, or reports a post-release Kovacs hump;
the short look-ahead is used ONLY to gate coincidence *stability* (matching quality).

Design (revised after the Phase-1 pilot):
  After the frozen 1000-step deep turnover the feed-starve overshoot transient is
  gone (>> memory timescales), leaving a near-constant dose-carryover mass offset, so
  a post-turnover opposite-direction mass *crossing* is not naturally achievable.
  We therefore match TOTAL DOSE (Σ amp·steps) between two histories that differ only
  in DELIVERY PATTERN (a brief spike vs gentle sustained feeding). Equal dose ⇒ the
  clones reach a COMMON-CLOCK coincidence (equal core mass at the same absolute time)
  by construction, and the scientific question is whether the OVERT physical panel
  also coincides there while the HIDDEN memory fields differ (STRONG) or whether overt
  area/shape/energy remain apart (SCALAR_ONLY).

Architecture:
  * CALIBRATION and ANALYSIS clones are byte-identical replays of a SINGLE FROZEN,
    dose-matched schedule family (no per-world outcome-dependent tuning); determinism
    is proven by re-running and comparing state hashes.
  * The schedule + coincidence rule are hashed BEFORE any coincidence analysis.

Overt panel (tracker-free, frozen checkpoint-centred core mask, COMMON to both clones):
  core mass, occupied support, 2nd spatial moment (rg^2), centroid offset, core
  nutrient/attractant/uptake totals, collar mass/nutrient, coverage/viability.
  Memory (m1,m2,m_plus,m_minus) is recorded ONLY as the hidden residual diagnostic.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np

from experiments.individuation import counterfactual_history_core_dev as chc
from experiments.individuation import causal_confirm as cc
from experiments.individuation import access_structure_noswap_operators as ns

N = chc.N
bh = chc.bh
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# ---- FROZEN dose-matched schedule family + common-clock coincidence rule ----
# Both histories deliver total nutrient Σ(amp·steps) = 2.40 (matched dose); they differ
# only in delivery pattern. Amplitudes stay within the parent gentle-support ceiling
# except the brief spike, declared explicitly.
SCHEDULE = {
    "schema": "KOVACS-HIDDEN-STATE-00-PHASE1-SCHEDULE-v2",
    "matched_total_dose": 2.40,
    "H_SPIKE": [[0.060, 40], [0.0, 120]],     # brief strong spike then rest; dose 0.060*40 = 2.40
    "H_SUSTAINED": [[0.015, 160]],            # gentle sustained; dose 0.015*160 = 2.40
    "deep_turnover_steps": chc.DEEP_STEPS,    # 1000, inherited
    "relaxation_steps": 180,                  # no-drive relaxation window
    "coincidence_rule": {
        "match_variable": "core_mass",
        "type": "common_clock",
        "primary_step": 90,                   # frozen common-clock release step (>~3x fast-memory tau)
        "robustness_steps": [60, 90, 120],    # frozen alternates for robustness
        "rationale": "fast-memory tau~28 steps: >=60 washes fast transient; slow m2 tau~1700 intact",
    },
    "stability_steps": 3,                     # look-ahead for matching stability only (NOT an excursion)
}
CONFIG_LABEL = "PATTERN"  # spike vs sustained at matched dose

def schedule_hash():
    return hashlib.sha256(json.dumps(SCHEDULE, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

# ---------------- frozen common core frame + panel ----------------
def make_core_frame(shape, center):
    partition, core, ring = ns.core_and_collar(shape, center)
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]]
    dy = ((ys - center[0] + shape[0] / 2) % shape[0]) - shape[0] / 2
    dx = ((xs - center[1] + shape[1] / 2) % shape[1]) - shape[1] / 2
    return {"core": core, "ring": ring, "dy": dy.astype(float), "dx": dx.astype(float),
            "r2": (dy * dy + dx * dx).astype(float)}

def panel(state, frame):
    core = frame["core"]; ring = frame["ring"]; rho = state.rho
    m = float(rho[core].sum())
    support = int((rho[core] > 1e-4).sum())
    if m > 1e-9:
        cy = float((rho[core] * frame["dy"][core]).sum() / m)
        cx = float((rho[core] * frame["dx"][core]).sum() / m)
        rg2 = float((rho[core] * frame["r2"][core]).sum() / m)
    else:
        cy = cx = rg2 = 0.0
    return {"core_mass": m, "core_support": support, "core_rg2": rg2,
            "core_centroid_off": float(math.hypot(cy, cx)),
            "core_N": float(state.N[core].sum()), "core_c": float(state.c[core].sum()),
            "core_uptake": float(state.uptake[core].sum()),
            "collar_mass": float(rho[ring].sum()), "collar_N": float(state.N[ring].sum())}

PANEL_KEYS = ["core_mass", "core_support", "core_rg2", "core_centroid_off",
              "core_N", "core_c", "core_uptake", "collar_mass", "collar_N"]

def memory_diag(state, frame):
    core = frame["core"]; rho = state.rho
    denom = np.maximum(rho[core], 1e-9)
    m1 = state.Mf[0][core] / denom; m2 = state.Mf[1][core] / denom
    w = rho[core]; W = float(w.sum()); W = W if W > 1e-9 else 1.0
    return {"m1_mean": float((w * m1).sum() / W), "m2_mean": float((w * m2).sum() / W),
            "mplus_mean": float((w * np.tanh(m1 + m2)).sum() / W),
            "mminus_mean": float((w * np.tanh(m1 - m2)).sum() / W)}

# ---------------- history / turnover / relaxation ----------------
def apply_custom_history(cp, stages):
    br = chc.clone_checkpoint(cp); state = br["state"]; fid = int(br["focal_id"])
    tracker = chc._new_tracker(br["tracker_masks"], state.step)
    fe = cp["entities"][fid]
    patch = bh.gaussian_patch(fe.centroid, max(3.0, 0.8 * float(fe.rg)))
    engine = cc.build(cc.MEM_INTACT); maxcov = 0.0
    for amp, nsteps in stages:
        for _ in range(int(nsteps)):
            if amp:
                state.N = state.N + float(amp) * patch
            state = engine.step(state); up = chc._tracker_update(tracker, state)
            maxcov = max(maxcov, up["coverage"])
            if (not chc._focal_alive(tracker, fid)) or up["coverage"] >= chc.COVER_CAP:
                return {"valid": False, "reason": "history_focal_lost_or_cover", "max_coverage": maxcov}
    return {"valid": True, "state": state, "focal_region": tracker.tracks[fid].mask.copy(), "max_coverage": maxcov}

def run_branch(cp, stages, frame, R):
    hist = apply_custom_history(cp, stages)
    if not hist["valid"]:
        return {"valid": False, "reason": hist["reason"], "stage": "history"}
    deep = chc.turnover_fixed(hist["state"], hist["focal_region"])
    if not deep["valid"]:
        return {"valid": False, "reason": deep.get("reason", "turnover_invalid"), "stage": "turnover"}
    engine = cc.build(cc.MEM_INTACT); s = deep["state"]; traj = []
    for k in range(R + 1):
        traj.append({"k": k, **panel(s, frame), "_mem": memory_diag(s, frame)})
        if k < R:
            s = engine.step(s)
    return {"valid": True, "traj": traj,
            "deep_material_M": float(deep["material"]["M"]) if deep.get("material") else None,
            "post_relax_state_sha256": chc.state_hash(s)}

def _repeat(traj, key, k, w=3):
    vals = [traj[j][key] for j in range(max(0, k - w), min(len(traj), k + w + 1))]
    return float(np.std(vals)) if len(vals) > 1 else 0.0

def coincidence_at(trajA, trajB, k, stability):
    a = trajA[k]; b = trajB[k]
    panel_abs = {key: abs(a[key] - b[key]) for key in PANEL_KEYS}
    panel_rel = {key: panel_abs[key] / ((abs(a[key]) + abs(b[key])) / 2 or 1.0) for key in PANEL_KEYS}
    mem_diff = {key: a["_mem"][key] - b["_mem"][key] for key in a["_mem"]}
    dA = a["core_mass"] - trajA[k - 1]["core_mass"] if k >= 1 else 0.0
    dB = b["core_mass"] - trajB[k - 1]["core_mass"] if k >= 1 else 0.0
    kmax = min(len(trajA), len(trajB)) - 1
    stab = [abs(trajA[k + j]["core_mass"] - trajB[k + j]["core_mass"])
            for j in range(1, stability + 1) if k + j <= kmax]
    repeat = {key: max(_repeat(trajA, key, k), _repeat(trajB, key, k)) for key in PANEL_KEYS}
    return {"k": k, "mass_OVER": a["core_mass"], "mass_APPR": b["core_mass"],
            "mass_abs_diff": panel_abs["core_mass"], "panel_abs": panel_abs, "panel_rel": panel_rel,
            "memory_diff": mem_diff, "deriv_SPIKE_pre": dA, "deriv_SUSTAINED_pre": dB,
            "opposite_direction": bool(dA * dB < 0), "stability_mass_absdiff_next": stab,
            "repeatability": repeat}

def process_world(seed, R=None, prove_determinism=False):
    R = SCHEDULE["relaxation_steps"] if R is None else R
    out = {"seed": seed, "config": CONFIG_LABEL, "schedule_sha256": schedule_hash()}
    try:
        cp = chc.make_checkpoint(seed)
    except Exception as ex:
        out["error"] = f"checkpoint:{ex}"; return out
    if cp["focal_id"] is None:
        out["eligible"] = False; out["reason"] = "no_focal"; return out
    out["eligible"] = True
    center = tuple(float(v) for v in cp["entities"][cp["focal_id"]].centroid)
    frame = make_core_frame(cp["state"].rho.shape, center)
    out["checkpoint_core_mass"] = panel(cp["state"], frame)["core_mass"]
    brA = run_branch(cp, SCHEDULE["H_SPIKE"], frame, R)
    brB = run_branch(cp, SCHEDULE["H_SUSTAINED"], frame, R)
    for nm, r in (("SPIKE", brA), ("SUSTAINED", brB)):
        if not r["valid"]:
            out["branch_invalid"] = {"branch": nm, "reason": r["reason"], "stage": r.get("stage")}
            return out
    # determinism proof (independent re-clone replay -> identical hash); run on demand only
    if prove_determinism:
        reA = run_branch(cp, SCHEDULE["H_SPIKE"], frame, R)
        reB = run_branch(cp, SCHEDULE["H_SUSTAINED"], frame, R)
        out["determinism_bitmatch"] = bool(reA.get("post_relax_state_sha256") == brA.get("post_relax_state_sha256")
                                           and reB.get("post_relax_state_sha256") == brB.get("post_relax_state_sha256"))
        out["state_sha_SPIKE"] = brA.get("post_relax_state_sha256")
        out["state_sha_SUSTAINED"] = brB.get("post_relax_state_sha256")
    else:
        out["determinism_bitmatch"] = None
        out["state_sha_SPIKE"] = brA.get("post_relax_state_sha256")
        out["state_sha_SUSTAINED"] = brB.get("post_relax_state_sha256")
    out["deep_material_M"] = {"SPIKE": brA["deep_material_M"], "SUSTAINED": brB["deep_material_M"]}
    cr = SCHEDULE["coincidence_rule"]
    out["coincidence_primary"] = coincidence_at(brA["traj"], brB["traj"], cr["primary_step"], SCHEDULE["stability_steps"])
    out["coincidence_robustness"] = {str(k): coincidence_at(brA["traj"], brB["traj"], k, SCHEDULE["stability_steps"])
                                     for k in cr["robustness_steps"]}
    out["relax_mass_SPIKE"] = [brA["traj"][0]["core_mass"], brA["traj"][-1]["core_mass"]]
    out["relax_mass_SUSTAINED"] = [brB["traj"][0]["core_mass"], brB["traj"][-1]["core_mass"]]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="")
    ap.add_argument("--out", default=str(REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_PHASE1_DEV_RESULTS.json"))
    ap.add_argument("--relax", type=int, default=SCHEDULE["relaxation_steps"])
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",") if s.strip()] if a.seeds else list(chc.DEV_SEEDS)
    outpath = Path(a.out)
    report = {"schema": "KOVACS-HIDDEN-STATE-00-PHASE1-DEV-RESULTS-v2",
              "firewall": "no post-release excursion computed; matched-dose common-clock coincidence + hidden-residual diagnostic only",
              "config": CONFIG_LABEL, "schedule": SCHEDULE, "schedule_sha256": schedule_hash(), "grid_N": N, "worlds": []}
    if outpath.exists():
        try:
            prev = json.load(open(outpath)); done = {w["seed"] for w in prev.get("worlds", [])}
            report["worlds"] = prev["worlds"]; seeds = [s for s in seeds if s not in done]
            print(f"resume: {len(done)} done, {len(seeds)} remaining")
        except Exception:
            pass
    for i, seed in enumerate(seeds):
        row = process_world(seed, R=a.relax, prove_determinism=(i == 0)); report["worlds"].append(row)
        c = row.get("coincidence_primary", {})
        print(f"seed {seed}: elig={row.get('eligible')} det={row.get('determinism_bitmatch')} "
              f"massΔ={round(c.get('mass_abs_diff',-1),4) if c else '-'} "
              f"suppΔ={c.get('panel_abs',{}).get('core_support','-') if c else '-'} "
              f"rg2rel={round(c.get('panel_rel',{}).get('core_rg2',-1),4) if c else '-'} "
              f"massrel={round(c.get('panel_rel',{}).get('core_mass',-1),4) if c else '-'} "
              f"mminusΔ={round(c.get('memory_diff',{}).get('mminus_mean',0),5) if c else '-'} "
              f"m2Δ={round(c.get('memory_diff',{}).get('m2_mean',0),5) if c else '-'}", flush=True)
        outpath.write_text(json.dumps(report, indent=2))
    print("WROTE", outpath, flush=True)

if __name__ == "__main__":
    main()
