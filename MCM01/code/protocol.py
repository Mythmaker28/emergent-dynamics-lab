"""MCM01 protocol. FROZEN before the first start.

Start classes and their caps live in guard.py and are enforced there, not here.

  cost_probe   2   timing only, on the provably non-scientific manifold n[Y] == 0
  calibration  8   measurement of c_X at the four cheapest analytically admissible points
  confirmation 6   independent seeds at the point the frozen rule selects
  control     10   the pre-declared controls

Calibration seeds, confirmation seeds and control seeds are disjoint and declared here. No
calibration arm can be counted as confirmation: the class is part of the ledger entry.
"""
from __future__ import annotations

import json
import math
import time

import numpy as np

import guard
import lattice as LAT
import mcm
import region as REG

OUT, RAW = "/home/claude/MCM01/out", "/home/claude/MCM01/raw"

# ---------------------------------------------------------------- frozen protocol constants
X_SEED = 4                    # body molecules placed with the single organiser, as in MTW01
N_FORM = 30                   # formation threshold on the total body population
U_FORM = 3.0                  # formation threshold on the organiser-cell occupancy
K_FORM = 50                   # consecutive qualifying steps required for formation
FORM_LIFETIMES = REG.FORM_LIFETIMES        # T_FORM_MAX = FORM_LIFETIMES / muX
MAINT_LIFETIMES = REG.MAINT_LIFETIMES      # T_MAINT >= MAINT_LIFETIMES / muX
FRAC_MIN = 0.95               # fraction of maintenance steps at or above N_KEEP
CRIT_FRAC = 0.90              # fraction of maintenance steps with c_X*G(0) > 1
N_KEEP_FRACTION = 0.25        # N_KEEP = max(20, N_KEEP_FRACTION * N_X_predicted)
N_KEEP_FLOOR = 20
RUN_MAX_LIFETIMES = 1.0       # a dip longer than one body lifetime means the cloud died
SAMPLE_EVERY = 50             # component reports
CAL_LIFETIMES = 5.0           # calibration measurement window, in body lifetimes after forming
N_CANDIDATES = 4              # the four cheapest admissible points enter calibration
CONFIRM_REQUIRED = 5          # of 6 seeds must be MAINTENANCE_ACHIEVED

SEEDS = {"calibration": (1001, 1002), "confirmation": (2001, 2002, 2003, 2004, 2005, 2006),
         "control": (3001,)}

# organiser kinetics for the primary arms: the organiser is a permanent inert catalyst, so the
# body-cloud question is isolated exactly. A control switches the window kinetics back on.
PRIMARY_ORGANISER = {"kY": 0.0, "muY": 0.0}


def spec_for(point, **over):
    d = {"L": point["L"], "CAP": point["CAP"], "S0": point["S0"], "phi": point["phi"],
         "omega": point["omega"], "p_hop_X": point["p_hop_X"], "p_hop_Y": point["p_hop_Y"],
         "muX": point["muX"], "kX": 1.0}
    d.update(PRIMARY_ORGANISER)
    d.update(over)
    return mcm.spec_with(**d)


def thresholds_for(point):
    muX = point["muX"]
    N_pred = point["N_X_predicted"]
    return {"T_FORM_MAX": int(round(FORM_LIFETIMES / muX)),
            "T_MAINT": int(round(max(MAINT_LIFETIMES / muX, 10.0 * point["tau_sep"]))),
            "N_KEEP": int(max(N_KEEP_FLOOR, round(N_KEEP_FRACTION * N_pred))),
            "RUN_MAX": int(round(RUN_MAX_LIFETIMES / muX)),
            "T_CAL": int(round(CAL_LIFETIMES / muX)),
            "G0": point["G0_relative"]}


# ---------------------------------------------------------------- one arm
def run_arm(cls, tag, point, seed, mode, spec_override=None, L_override=None):
    """mode = 'calibration' (form, then measure c_X over T_CAL) or 'full' (form, then maintain).
    Every raw series is written to disk before any gate is evaluated."""
    th = thresholds_for(point)
    sp = spec_for(point, **(spec_override or {}))
    if L_override:
        sp = mcm.spec_with(**{**sp.as_dict(), "L": L_override})
    horizon = th["T_FORM_MAX"] + (th["T_CAL"] if mode == "calibration" else th["T_MAINT"])
    rec = mcm.Recorder()
    w = mcm.fresh_world(seed, sp, rec=rec)
    org = None if spec_override and spec_override.get("_no_organiser") else \
        mcm.seed_one_organiser(w, X_SEED)
    rng0 = json.loads(json.dumps(w.rng.bit_generator.state, default=str))
    comp = []
    t0 = time.time()
    with guard.start(cls, tag, horizon):
        guard.advance(w, horizon,
                      per_step=lambda ww: comp.append(mcm.component_report(ww))
                      if ww.step % SAMPLE_EVERY == 0 else None)
    wall = time.time() - t0
    arr = rec.array()

    np.savez_compressed("%s/%s.npz" % (RAW, tag.replace("/", "__")), series=arr,
                        fields=np.array(mcm.Recorder.FIELDS),
                        nX_final=w.n["X"], nY_final=w.n["Y"], nSX_final=w.n["SX"],
                        nSY_final=w.n["SY"], nWX_final=w.n["WX"], nWY_final=w.n["WY"])
    F = mcm.Recorder.FIELDS
    formed = mcm.formation_gate(arr, F, th["T_FORM_MAX"], N_FORM, U_FORM, K_FORM)
    rec_out = {"class": cls, "tag": tag, "seed": seed, "mode": mode, "horizon": horizon,
               "wall_seconds": wall, "spec": sp.as_dict(), "point": {k: point[k] for k in
                                                                     ("muX", "phi", "ell_X",
                                                                      "rho_Y")},
               "thresholds": th, "organiser_seed_cell": org, "rng_state_initial": rng0,
               "rng_state_final": json.loads(json.dumps(w.rng.bit_generator.state, default=str)),
               "formed_at": formed, "component_samples": comp,
               "raw_npz": "%s.npz" % tag.replace("/", "__"),
               "steps_used": int(w.step)}

    if mode == "calibration":
        if formed is None:
            rec_out.update({"c_X_stats": None, "outcome": "NO_FORMATION"})
        else:
            lo, hi = formed, min(len(arr), formed + th["T_CAL"])
            seg = arr[lo:hi]
            cx = seg[:, F.index("c_X_per_org")]
            crit = cx * th["G0"]
            above = crit > 1.0
            longest, run = 0, 0
            for b in above:
                run = run + 1 if b else 0
                longest = max(longest, run)
            rec_out["c_X_stats"] = {
                "n": int(len(cx)), "min": float(cx.min()), "q05": float(np.quantile(cx, 0.05)),
                "q25": float(np.quantile(cx, 0.25)), "median": float(np.median(cx)),
                "mean": float(cx.mean()), "max": float(cx.max()),
                "at_formation": float(cx[0]),
                "fraction_cX_G0_above_1": float(above.mean()),
                "longest_consecutive_above_1": int(longest),
                "u_mean": float(seg[:, F.index("u_nX_at_org")].mean()),
                "N_X_mean": float(seg[:, F.index("N_X")].mean()),
                "accepted_births_mean": float(seg[:, F.index("accepted_births_X")].mean()),
                "deaths_mean": float(seg[:, F.index("deaths_X")].mean())}
            rec_out["outcome"] = "MEASURED"
    else:
        if formed is None:
            pers = {"PASS": False, "checks": {}, "reason": "no formation"}
        else:
            pers = mcm.persistence_gate(arr, F, formed, th["T_MAINT"], th["N_KEEP"], FRAC_MIN,
                                        th["RUN_MAX"], th["G0"], CRIT_FRAC, comp)
        rec_out["persistence"] = pers
        rec_out["classification"] = mcm.classify(formed, pers, arr, F, comp)
        rec_out["PASS"] = bool(pers.get("PASS"))
        # the c_X statistics required by the handoff, over the maintenance window
        if formed is not None and len(arr) >= formed + th["T_MAINT"]:
            seg = arr[formed:formed + th["T_MAINT"]]
            cx = seg[:, F.index("c_X_per_org")]
            crit = cx * th["G0"]
            above = crit > 1.0
            longest, run = 0, 0
            for b in above:
                run = run + 1 if b else 0
                longest = max(longest, run)
            pre = arr[max(0, formed - th["RUN_MAX"]):formed][:, F.index("c_X_per_org")]
            rec_out["c_X_stats"] = {
                "min": float(cx.min()), "q05": float(np.quantile(cx, 0.05)),
                "q25": float(np.quantile(cx, 0.25)), "median": float(np.median(cx)),
                "mean": float(cx.mean()), "at_formation": float(cx[0]),
                "before_formation_mean": float(pre.mean()) if len(pre) else None,
                "fraction_cX_G0_above_1": float(above.mean()),
                "longest_consecutive_above_1": int(longest),
                "u_mean": float(seg[:, F.index("u_nX_at_org")].mean())}
        else:
            rec_out["c_X_stats"] = None
    return rec_out


# ---------------------------------------------------------------- material balance, no start
def material_balance(tag):
    """Exact audit from the saved raw series: every body molecule created must be accounted for
    by the population change plus the deaths. Uses no new start."""
    d = np.load("%s/%s.npz" % (RAW, tag.replace("/", "__")), allow_pickle=True)
    F = list(d["fields"])
    a = d["series"]
    NX = a[:, F.index("N_X")]
    births = a[:, F.index("accepted_births_X")]
    deaths = a[:, F.index("deaths_X")]
    resid = NX[1:] - (NX[:-1] + births[1:] - deaths[1:])
    return {"tag": tag, "steps": int(len(a)), "max_abs_residual": float(np.abs(resid).max()),
            "exact": bool(np.abs(resid).max() == 0.0),
            "total_births": float(births.sum()), "total_deaths": float(deaths.sum()),
            "N_X_first": float(NX[0]), "N_X_last": float(NX[-1])}


def constants():
    return {"X_SEED": X_SEED, "N_FORM": N_FORM, "U_FORM": U_FORM, "K_FORM": K_FORM,
            "FORM_LIFETIMES": FORM_LIFETIMES, "MAINT_LIFETIMES": MAINT_LIFETIMES,
            "FRAC_MIN": FRAC_MIN, "CRIT_FRAC": CRIT_FRAC,
            "N_KEEP_FRACTION": N_KEEP_FRACTION, "N_KEEP_FLOOR": N_KEEP_FLOOR,
            "RUN_MAX_LIFETIMES": RUN_MAX_LIFETIMES, "SAMPLE_EVERY": SAMPLE_EVERY,
            "CAL_LIFETIMES": CAL_LIFETIMES, "N_CANDIDATES": N_CANDIDATES,
            "CONFIRM_REQUIRED": CONFIRM_REQUIRED, "SEEDS": {k: list(v) for k, v in SEEDS.items()},
            "PRIMARY_ORGANISER": PRIMARY_ORGANISER,
            "start_caps": dict(guard.CAPS),
            "c_X_pooling": "min over calibration seeds of the median over the measurement "
                           "window; conservative, chosen because the certified transport value "
                           "is an UPPER bound and the gate must not be flattered",
            "selection_rule": "among points passing every analytic constraint AND the measured "
                              "criticality and population thresholds, take the minimum predicted "
                              "T_run; ties broken by the ascending lexicographic order "
                              + str(REG.TIE_BREAK),
            "sequential_stopping_rule": [
                "1 no analytically admissible point -> STOP, FAIL (region empty)",
                "2 no calibration arm forms a cloud -> STOP, CX_UNRESOLVED",
                "3 no point survives the frozen rule with the MEASURED c_X -> STOP, FAIL",
                "4 the first two confirmation seeds both fail to form -> STOP, FAIL",
                "5 the first three confirmation seeds all fail maintenance -> STOP, FAIL",
                "6 any protocol or logging defect -> STOP, AUDIT_INVALID",
                "7 controls run only if at least three confirmation seeds were executed"],
            "success_criterion": "at least %d of %d confirmation seeds classified "
                                 "MAINTENANCE_ACHIEVED" % (CONFIRM_REQUIRED,
                                                           len(SEEDS["confirmation"])),
            "raw_variables_saved": list(mcm.Recorder.FIELDS) + [
                "final n[X], n[Y], n[SX], n[SY], n[WX], n[WY] fields",
                "per-component: id, cells, N_X, N_Y, mass, density, circular centre of mass, "
                "radius of gyration, extent, gap to the periodic image, wrap flag",
                "escapee list", "initial and final RNG state", "seed", "full LawSpec",
                "step index of every sample"]}
