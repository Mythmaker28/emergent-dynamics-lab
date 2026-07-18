"""KOVACS-HIDDEN-STATE-00 Phase-0 DEV crossing/timing FEASIBILITY probe.

Integrity firewall:
  * Uses ONLY already-open DEV worlds (57001-57024). No new seed namespace.
  * Measures ONLY the candidate MATCHING variable Z (focal mass) trajectory during
    drive + no-drive relaxation, to test whether two histories can reach a common
    per-world value from opposite directions (overshoot vs approach) and at what
    elapsed time / age.
  * Does NOT compute or use any post-release between-branch excursion (the prospective
    outcome estimand). No design parameter (m*, tolerance, horizon, gate) is selected
    from any response here. Matching feasibility only.

Reproduce:
  PYTHONPATH=<repo> python3 -m experiments.individuation.kovacs_hidden_state_dev_crossing_probe
Writes: docs/individuation/KOVACS_HIDDEN_STATE_00_DEV_CROSSING.json
"""
import json
from pathlib import Path
import numpy as np
from experiments.individuation import counterfactual_history_core_dev as chc
from experiments.individuation import causal_confirm as cc
from experiments.individuation import access_structure_noswap_operators as ns

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_DEV_CROSSING.json"
N = chc.N
bh = chc.bh

def core_mask(shape, center):
    _, core, _ = ns.core_and_collar(shape, center)
    return core

def run_schedule(cp, stages, label):
    br = chc.clone_checkpoint(cp)
    state = br["state"]; fid = int(br["focal_id"])
    tracker = chc._new_tracker(br["tracker_masks"], state.step)
    fe = cp["entities"][fid]
    center = tuple(float(v) for v in fe.centroid)
    patch = bh.gaussian_patch(fe.centroid, max(3.0, 0.8 * float(fe.rg)))
    cmask = core_mask(state.rho.shape, center)
    engine = cc.build(cc.MEM_INTACT)
    traj = []; elapsed = 0; alive = True
    for amp, nsteps in stages:
        for _ in range(int(nsteps)):
            if amp:
                state.N = state.N + float(amp) * patch
            state = engine.step(state)
            up = chc._tracker_update(tracker, state)
            elapsed += 1
            core_m = float(state.rho[cmask].sum())
            if chc._focal_alive(tracker, fid):
                tm = float(state.rho[tracker.tracks[fid].mask].sum())
            else:
                tm = None; alive = False
            traj.append((elapsed, tm, core_m, up["coverage"]))
            if not alive or up["coverage"] >= chc.COVER_CAP:
                return {"label": label, "alive": alive,
                        "reason": ("focal_lost" if not alive else "coverage"),
                        "elapsed_end": elapsed, "traj": traj, "center": center}
    return {"label": label, "alive": alive, "reason": None,
            "elapsed_end": elapsed, "traj": traj, "center": center}

def summarize(res):
    tj = res["traj"]
    tm = [(e, m) for (e, m, c, cov) in tj if m is not None]
    cm = [(e, c) for (e, m, c, cov) in tj]
    out = {"label": res["label"], "alive": res["alive"], "reason": res["reason"], "elapsed_end": res["elapsed_end"]}
    if tm:
        masses = [m for _, m in tm]
        pk = int(np.argmax(masses)); trough_after = min(masses[pk:]) if pk < len(masses) else masses[-1]
        out.update({"tracked_first": round(tm[0][1], 4), "tracked_last": round(tm[-1][1], 4),
                    "tracked_min": round(min(masses), 4), "tracked_max": round(max(masses), 4),
                    "tracked_peak_elapsed": tm[pk][0],
                    "decline_after_peak": round(masses[pk] - trough_after, 4),
                    "monotone_nondecreasing": all(masses[i+1] >= masses[i] - 1e-9 for i in range(len(masses)-1))})
    if cm:
        cmv = [c for _, c in cm]
        out.update({"core_first": round(cm[0][1], 4), "core_last": round(cm[-1][1], 4),
                    "core_min": round(min(cmv), 4), "core_max": round(max(cmv), 4)})
    return out

def first_cross(res, target):
    prev = None
    for (e, m, c, cov) in res["traj"]:
        if m is None: continue
        if prev is not None and ((prev - target) == 0 or (prev - target) * (m - target) <= 0):
            return {"elapsed": e, "from": ("down" if m < prev else "up"), "mass": round(m, 4)}
        prev = m
    return None

def mass_at(res, e_target):
    best = None
    for (e, m, c, cov) in res["traj"]:
        if m is None: continue
        if best is None or abs(e - e_target) < abs(best[0] - e_target): best = (e, m)
    return best[1] if best else None

def main():
    seeds = [57001, 57003, 57006, 57008, 57009, 57010]
    OVER = [(0.060, 60), (0.0, 60), (0.0, 360)]   # hard early feed -> starve -> long no-drive
    APPR = [(0.010, 120), (0.0, 360)]             # gentle sustained feed -> no-drive
    NODR = [(0.0, 480)]                           # direct no-drive reference-ish
    report = {"schema": "KOVACS-HIDDEN-STATE-00-DEV-CROSSING-PROBE-v1",
              "scope": "already-open DEV worlds only; matching-variable trajectories only; no outcome estimand",
              "grid_N": N, "schedules": {"OVERSHOOT": OVER, "APPROACH": APPR, "NODRIVE": NODR},
              "worlds": []}
    for seed in seeds:
        try:
            cp = chc.make_checkpoint(seed)
        except Exception as ex:
            report["worlds"].append({"seed": seed, "error": f"checkpoint:{ex}"}); continue
        if cp["focal_id"] is None:
            report["worlds"].append({"seed": seed, "error": "no_focal"}); continue
        over = run_schedule(cp, OVER, "OVERSHOOT")
        appr = run_schedule(cp, APPR, "APPROACH")
        nodr = run_schedule(cp, NODR, "NODRIVE")
        ref_mass = mass_at(nodr, 240); appr_plateau = mass_at(appr, 400)
        cands = [v for v in (ref_mass, appr_plateau) if v is not None]
        mstar = sum(cands) / len(cands) if cands else None
        wrow = {"seed": seed, "OVERSHOOT": summarize(over), "APPROACH": summarize(appr), "NODRIVE": summarize(nodr)}
        if mstar is not None:
            wrow["placeholder_crossing"] = {"m_star_placeholder": round(mstar, 4),
                                            "overshoot_cross": first_cross(over, mstar),
                                            "approach_cross": first_cross(appr, mstar),
                                            "note": "placeholder m* is midpoint(no-drive@240, approach@400); geometry check only, NOT the prereg rule"}
        report["worlds"].append(wrow)
        oc = wrow["OVERSHOOT"]
        print(f"seed {seed}: over(mono={oc.get('monotone_nondecreasing')},decl={oc.get('decline_after_peak')},"
              f"pk@{oc.get('tracked_peak_elapsed')},max={oc.get('tracked_max')},last={oc.get('tracked_last')}) "
              f"appr(max={wrow['APPROACH'].get('tracked_max')},last={wrow['APPROACH'].get('tracked_last')}) "
              f"nodr(last={wrow['NODRIVE'].get('tracked_last')})", flush=True)
        OUT.write_text(json.dumps(report, indent=2))
    print("WROTE", OUT, flush=True)

if __name__ == "__main__":
    main()
