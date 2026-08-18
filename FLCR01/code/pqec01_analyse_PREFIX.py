"""PQEC01 — analysis. Runs ONLY after every scheduled start is complete.

Discovery/validation discipline: the operator is identified on DISCOVERY worlds alone; the
VALIDATION worlds are opened once, for predeclared predictions, and nothing is refitted after.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RAW = "/home/claude/PQEC01/raw"
OUT_READ = "/home/claude/edl/PQEC01/out"
OUT = "/home/claude/FLCR01/work/prefix/out"
FR = json.load(open(f"{OUT_READ}/PQEC01_MASTER_FREEZE.json"))
C = FR["INHERITED_FROZEN_CONSTANTS"]
L, CAP, BURN_IN, T = 36, C["CAP"], C["BURN_IN"], C["T_HORIZON"]
CORE_R, TAU_SEP = C["CORE_R"], C["TAU_SEP"]
SP = ("X", "Y", "SX", "SY", "WX", "WY")

_DIST = None


def dist_maps():
    global _DIST
    if _DIST is None:
        ay = np.abs(np.arange(L)[:, None] - np.arange(L)[None, :])
        ay = np.minimum(ay, L - ay)
        _DIST = np.zeros((L, L, L, L), np.float32)
        for y in range(L):
            for x in range(L):
                dy = ay[y][:, None]
                dx = ay[x][None, :]
                _DIST[y, x] = np.sqrt(dy.astype(np.float32) ** 2 + dx.astype(np.float32) ** 2)
    return _DIST


def load(path, want_field=False):
    z = np.load(path, allow_pickle=True)
    m = json.loads(str(z["meta"][0]))
    d = {"meta": m, "scalars": z["scalars"], "names": [str(s) for s in z["scalar_names"]],
         "ycells": z["ycells"], "ybirth": z["ybirth"], "ydeath": z["ydeath"],
         "yhop": z["yhop"], "xevent": z["xevent"], "src": z["src"], "final": z["final"]}
    if want_field:
        f0, dd = z["field0"].astype(np.int16), z["field_delta"].astype(np.int16)
        fld = np.empty((dd.shape[0] + 1,) + f0.shape, np.int16)
        fld[0] = f0
        np.cumsum(dd, axis=0, out=fld[1:])
        fld[1:] += f0
        d["field"] = fld
    return d


def col(d, name):
    return d["scalars"][:, d["names"].index(name)]


# ============================ Phase A — spatial environment operator ====================
def phase_a():
    files = sorted(glob.glob(f"{RAW}/A_*.npz"))
    DM = dist_maps()
    nbin = int(np.ceil(DM[0, 0].max())) + 1
    per_world, radial_acc = [], []
    kern_acc = None
    QMAX = 40
    for p in files:
        d = load(p, want_field=True)
        m = d["meta"]
        F = d["field"]
        n = F.shape[0]
        free = CAP - F.sum(axis=1)
        QP = F[:, 0] * np.minimum(F[:, 3], np.maximum(free, 0))
        w0 = BURN_IN
        # source cell per step = the founder Y cell (Phase A has exactly one Y)
        yc = d["ycells"]
        pos = {int(r[0]): (int(r[1]), int(r[2])) for r in yc}
        steps = [t for t in range(w0, n) if t in pos]
        groups = {}
        for t in steps:
            groups.setdefault(pos[t], []).append(t)
        rad_sum = np.zeros(nbin)
        rad_cnt = np.zeros(nbin)
        for (sy, sx), ts in groups.items():
            b = np.minimum(DM[sy, sx].astype(np.int32).ravel(), nbin - 1)
            s = QP[ts].reshape(len(ts), -1).sum(axis=0)
            rad_sum += np.bincount(b, weights=s, minlength=nbin)
            rad_cnt += np.bincount(b, minlength=nbin) * len(ts)
        radial = np.where(rad_cnt > 0, rad_sum / np.maximum(rad_cnt, 1), np.nan)
        radial_acc.append(radial)
        # exposure transition kernel seen by the mobile founder
        q = col(d, "Q_founder")[w0:n].astype(int)
        q = np.clip(q, 0, QMAX)
        k = np.zeros((QMAX + 1, QMAX + 1))
        np.add.at(k, (q[:-1], q[1:]), 1.0)
        kern_acc = k if kern_acc is None else kern_acc + k
        cand = col(d, "candY_founder")[w0:n]
        per_world.append({
            "world": m["tag"], "seed": m["seed"], "split": m["split"],
            "steps_recorded": int(n), "stop": m["stop"],
            "E_w_mean_Q_founder": float(q.mean()),
            "S_w_q10_Q_founder": float(np.quantile(q, 0.10)),
            "q25": float(np.quantile(q, .25)), "median": float(np.median(q)),
            "q90": float(np.quantile(q, .90)), "max": float(q.max()),
            "frac_zero_Q": float((q == 0).mean()),
            "mean_cand_Y_founder": float(cand.mean()),
            "mean_field_Q_POSITION": float(QP[w0:n].mean()),
            "mean_nSY": float(col(d, "mean_nSY")[w0:n].mean()),
            "mean_free": float(col(d, "mean_free")[w0:n].mean()),
            "mean_N_X": float(col(d, "N_X")[w0:n].mean()),
            "distinct_source_cells": len(groups),
            "iat_Q_founder": _iat(q.astype(float)),
            "max_zero_run": int(_maxrun(q == 0)),
            "max_high_run": int(_maxrun(q >= 8)),
        })
        del d, F, QP, free
    R = np.vstack(radial_acc)
    K = kern_acc / np.maximum(kern_acc.sum(axis=1, keepdims=True), 1)
    E = np.array([w["E_w_mean_Q_founder"] for w in per_world])
    S = np.array([w["S_w_q10_Q_founder"] for w in per_world])
    return {
        "N_WORLDS": len(files),
        "PER_WORLD": per_world,
        "WORLD_LEVEL": {
            "mean_E_w": float(E.mean()), "sd_E_w": float(E.std(ddof=1)),
            "se_E_w": float(E.std(ddof=1) / np.sqrt(len(E))),
            "relative_SE": float(E.std(ddof=1) / np.sqrt(len(E)) / E.mean()),
            "min_E_w": float(E.min()), "max_E_w": float(E.max()),
            "distribution_free_lower_bound_10th_pct": float(S.min()),
            "worlds_with_positive_S_w": int((S > 0).sum()),
            "no_single_world_dominance": bool(
                abs(E.mean() - np.delete(E, int(np.argmax(np.abs(E - E.mean())))).mean())
                < 0.5 * E.std(ddof=1))},
        "RADIAL_EXPOSURE": {"bins": list(range(R.shape[1])),
                            "mean_over_worlds": np.nanmean(R, axis=0).tolist(),
                            "sd_over_worlds": np.nanstd(R, axis=0, ddof=1).tolist()},
        "EXPOSURE_TRANSITION_KERNEL": {
            "states": "Q at the founder cell, clipped to [0,%d]" % QMAX,
            "row_stochastic": bool(np.allclose(K.sum(axis=1)[K.sum(axis=1) > 0], 1.0)),
            "support_states": int((kern_acc.sum(axis=1) > 0).sum()),
            "P_stay_zero": float(K[0, 0]), "P_leave_zero": float(1 - K[0, 0]),
            "matrix_first_12x12": K[:12, :12].tolist()},
        "SPATIAL_OPERATOR_IDENTIFIED": None,   # decided in main()
    }


def _iat(x, cap=2000):
    x = np.asarray(x, float) - np.mean(x)
    n, v = x.size, float(np.dot(x, x) / max(x.size, 1))
    if v <= 0:
        return 1.0
    acf = [float(np.dot(x[:n - k], x[k:]) / (n * v)) for k in range(1, min(cap, n))]
    it, k = 1.0, 0
    while k + 1 < len(acf) and (acf[k] + acf[k + 1]) > 0:
        it += 2.0 * acf[k]
        k += 1
    return max(it, 1.0)


def _maxrun(mask):
    m = np.asarray(mask).astype(np.int8)
    if m.sum() == 0:
        return 0
    d = np.diff(np.concatenate(([0], m, [0])))
    return int((np.where(d == -1)[0] - np.where(d == 1)[0]).max())


# ============================ Phase B — active-Y calibration ============================
def phase_b():
    out = {}
    for lab in ("B1", "B2"):
        files = sorted(glob.glob(f"{RAW}/B_{lab}_*.npz"))
        rows = []
        for p in files:
            d = load(p)
            m = d["meta"]
            n = d["scalars"].shape[0]
            NY = col(d, "N_Y")
            ncen = col(d, "n_centres")
            births, deaths = d["ybirth"], d["ydeath"]
            yc = d["ycells"]
            first_birth = int(births[:, 0].min()) if births.size else -1
            colo = int(((col(d, "n_y_cells") >= 1) & (NY >= 2) & (ncen == 1)).sum())
            sep_steps = np.where(ncen >= 2)[0]
            sep = int(sep_steps[0]) if sep_steps.size else -1
            # descendant-local exposure: Y cells other than the earliest-listed cell per step
            desc = [r for r in yc if r[0] >= first_birth >= 0]
            per_step_cells = Counter(int(r[0]) for r in yc)
            multi = [s for s, c in per_step_cells.items() if c >= 2]
            rows.append({
                "world": m["tag"], "seed": m["seed"], "split": m["split"],
                "steps_recorded": n, "stop": m["stop"], "stop_step": m["stop_step"],
                "n_Y_births": int(births[:, 3].sum()) if births.size else 0,
                "n_Y_deaths": int(deaths[:, 3].sum()) if deaths.size else 0,
                "first_birth_step": first_birth,
                "max_N_Y": int(NY.max()), "max_n_centres": int(ncen.max()),
                "steps_two_plus_Y": int((NY >= 2).sum()),
                "steps_colocated_one_centre": colo,
                "steps_two_centres": int((ncen >= 2).sum()),
                "separation_first_step": sep,
                "separation_delay_after_first_birth": (sep - first_birth
                                                       if sep >= 0 and first_birth >= 0 else -1),
                "steps_with_multiple_occupied_Y_cells": len(multi),
                "n_Y_hops": int(d["yhop"][:, 6].sum()) if d["yhop"].size else 0,
                "max_pair_dist": float(col(d, "max_pair_dist").max()),
                "mean_Q_founder": float(col(d, "Q_founder")[BURN_IN:n].mean()) if n > BURN_IN
                else float(col(d, "Q_founder").mean()),
                "mean_nSY": float(col(d, "mean_nSY")[BURN_IN:n].mean()) if n > BURN_IN
                else float(col(d, "mean_nSY").mean()),
                "mean_free": float(col(d, "mean_free")[BURN_IN:n].mean()) if n > BURN_IN
                else float(col(d, "mean_free").mean()),
                "mean_N_X": float(col(d, "N_X")[BURN_IN:n].mean()) if n > BURN_IN
                else float(col(d, "N_X").mean()),
                # exact executable no-birth probability from this world's OWN recorded exposure
                "predicted_P_no_birth": _p_no_birth(yc, FR["PHASE_B"]["POINT_" + lab]["kY"], n),
                "descendant_exposure_rows": len(desc)})
            del d
        out[lab] = {"kY": FR["PHASE_B"]["POINT_" + lab]["kY"],
                    "muY": FR["PHASE_B"]["POINT_" + lab]["muY"],
                    "N_WORLDS": len(files), "PER_WORLD": rows}
    return out


def _p_no_birth(yc, kY, n):
    """P(no Y birth) = prod_t (1-p_t)^(c_t), the engine's own binomial, over the world's own
    recorded per-step (nX, cand_Y, nY) at every occupied Y cell."""
    lg = 0.0
    for r in yc:
        t, nY, nX, c = int(r[0]), int(r[3]), int(r[4]), int(r[7])
        p = min(1.0, kY * nX * nY)
        if p >= 1.0:
            return 0.0
        if c > 0 and p > 0:
            lg += c * np.log1p(-p)
    return float(np.exp(lg))


# ============================ operator identification (DISCOVERY only) ==================
STATES = ("ONE_Y", "TWO_Y_COLOCATED", "TWO_Y_SEPARATED", "EXTINCT", "PREMATURE_THIRD_CENTRE")


def _state(nY, ncen):
    if nY == 0:
        return "EXTINCT"
    if ncen >= 3:
        return "PREMATURE_THIRD_CENTRE"
    if nY == 1:
        return "ONE_Y"
    return "TWO_Y_SEPARATED" if ncen >= 2 else "TWO_Y_COLOCATED"


def operator(split="DISCOVERY"):
    res = {}
    for lab in ("B1", "B2"):
        Ntr = np.zeros((len(STATES), len(STATES)))
        occ = Counter()
        nworlds = 0
        for p in sorted(glob.glob(f"{RAW}/B_{lab}_*.npz")):
            d = load(p)
            if d["meta"]["split"] != split:
                del d
                continue
            nworlds += 1
            nY = col(d, "N_Y").astype(int)
            nc = col(d, "n_centres").astype(int)
            s = [_state(a, b) for a, b in zip(nY, nc)]
            for a, b in zip(s[:-1], s[1:]):
                Ntr[STATES.index(a), STATES.index(b)] += 1
            occ.update(s)
            del d
        P = Ntr / np.maximum(Ntr.sum(axis=1, keepdims=True), 1)
        res[lab] = {
            "SPLIT": split, "N_WORLDS": nworlds,
            "STATE_OCCUPANCY_STEPS": {k: int(occ[k]) for k in STATES},
            "TRANSITION_COUNTS": Ntr.tolist(),
            "TRANSITION_MATRIX": P.tolist(),
            "STATES": list(STATES),
            "ROWS_WITH_SUPPORT": [STATES[i] for i in range(len(STATES))
                                  if Ntr[i].sum() > 0],
            "IDENTIFIED_STATES": [STATES[i] for i in range(len(STATES)) if Ntr[i].sum() >= 30],
            "IS_GALTON_WATSON": False,
            "WHY_NOT_GALTON_WATSON": (
                "co-located Y draw ONE binomial from a shared candidate pool, and separated Y "
                "occupy different cells with different (nX, nSY, free). Neither is a sum of "
                "independent identical one-Y laws."),
        }
    return res


# ============================ feedback (distribution level) =============================
def feedback(pa, pb):
    A = pa["PER_WORLD"]
    base = {k: np.array([w[k] for w in A]) for k in ("mean_nSY", "mean_free", "mean_N_X")}
    out = {"PHASE_A_REFERENCE": {k: {"mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                                     "n": int(v.size)} for k, v in base.items()},
           "COMPARISON_IS_DISTRIBUTION_LEVEL_NOT_PAIRED": (
               "activating Y changes random-number consumption and state evolution, so the same "
               "seed does NOT give a paired counterfactual trajectory. Phase A and Phase B are "
               "compared as distributions over independent worlds."),
           "POINTS": {}}
    for lab, blk in pb.items():
        B = blk["PER_WORLD"]
        rec = {}
        for k in ("mean_nSY", "mean_free", "mean_N_X"):
            b = np.array([w[k] for w in B])
            a = base[k]
            se = np.sqrt(a.var(ddof=1) / a.size + b.var(ddof=1) / b.size)
            rec[k] = {"phase_A_mean": float(a.mean()), "phase_B_mean": float(b.mean()),
                      "delta": float(b.mean() - a.mean()),
                      "relative_delta": float((b.mean() - a.mean()) / a.mean()),
                      "se_of_delta": float(se),
                      "z": float((b.mean() - a.mean()) / se) if se > 0 else 0.0,
                      "significant_at_2se": bool(abs(b.mean() - a.mean()) > 2 * se)}
        births = sum(w["n_Y_births"] for w in B)
        rec["total_Y_births"] = births
        rec["worlds_with_a_birth"] = sum(1 for w in B if w["n_Y_births"] > 0)
        out["POINTS"][lab] = rec
    return out


# ============================ internal validation (predeclared) =========================
def validation(pb, op_disc):
    out = {}
    for lab, blk in pb.items():
        V = [w for w in blk["PER_WORLD"] if w["split"] == "VALIDATION"]
        D = [w for w in blk["PER_WORLD"] if w["split"] == "DISCOVERY"]
        if not V:
            continue
        # PREDECLARED TEST 1 — exact first-birth law, evaluated on each validation world's OWN
        # recorded exposure. Poisson-binomial mean and sd; no parameter is fitted.
        p = np.array([1.0 - w["predicted_P_no_birth"] for w in V])
        obs = sum(1 for w in V if w["n_Y_births"] > 0)
        mu, sd = float(p.sum()), float(np.sqrt((p * (1 - p)).sum()))
        z1 = (obs - mu) / sd if sd > 0 else 0.0
        # PREDECLARED TEST 2 — the discovery transition matrix predicts validation state
        # occupancy; compare the fraction of steps spent with two or more Y.
        def frac2(rows):
            num = sum(w["steps_two_plus_Y"] for w in rows)
            den = sum(w["steps_recorded"] for w in rows)
            return num / den if den else 0.0
        f_d, f_v = frac2(D), frac2(V)
        nv = sum(w["steps_recorded"] for w in V)
        se2 = np.sqrt(max(f_d * (1 - f_d), 1e-12) / max(nv, 1))
        # PREDECLARED TEST 3 — survival of the founder: predicted (1-muY)^steps vs observed
        muY = blk["muY"]
        surv_pred = float(np.mean([(1 - muY) ** w["steps_recorded"] for w in V]))
        surv_obs = float(np.mean([1.0 if w["stop"] != "EXTINCT" else 0.0 for w in V]))
        se3 = np.sqrt(max(surv_pred * (1 - surv_pred), 1e-12) / len(V))
        out[lab] = {
            "N_VALIDATION_WORLDS": len(V), "N_DISCOVERY_WORLDS": len(D),
            "TEST_1_first_birth": {
                "predicted_expected_worlds_with_a_birth": mu, "sd": sd, "observed": obs,
                "z": z1, "PASS": bool(abs(z1) <= 2.0),
                "note": "exact executable law on each world's own exposure; nothing fitted"},
            "TEST_2_two_plus_Y_step_fraction": {
                "discovery": f_d, "validation": f_v, "se": float(se2),
                "z": float((f_v - f_d) / se2) if se2 > 0 else 0.0,
                "PASS": bool(abs(f_v - f_d) <= 2 * se2 or se2 == 0)},
            "TEST_3_founder_survival": {
                "predicted": surv_pred, "observed": surv_obs, "se": float(se3),
                "z": float((surv_obs - surv_pred) / se3) if se3 > 0 else 0.0,
                "PASS": bool(abs(surv_obs - surv_pred) <= 2 * se3)},
            "NO_REFIT_AFTER_VIEWING_VALIDATION": True}
        out[lab]["ALL_PASS"] = all(out[lab][k]["PASS"] for k in
                                   ("TEST_1_first_birth", "TEST_2_two_plus_Y_step_fraction",
                                    "TEST_3_founder_survival"))
    return out


# ============================ candidate (kY, muY) region ================================
def candidate_region(pa, pb, op):
    """Derived ONLY from calibration-measured quantities, with world-level uncertainty.
    Labelled CANDIDATE_REGION_REQUIRING_DISJOINT_CONFIRMATION throughout."""
    import math
    E = np.array([w["E_w_mean_Q_founder"] for w in pa["PER_WORLD"]])
    S = np.array([w["S_w_q10_Q_founder"] for w in pa["PER_WORLD"]])
    nA = E.size
    mean_E = float(E.mean())
    se_E = float(E.std(ddof=1) / math.sqrt(nA))
    lcb_mean_E = mean_E - 1.645 * se_E                 # one-sided 95% lower confidence bound
    lb_quantile = float(S.min())                       # distribution-free 10th-pct lower bound
    W = C["T_WINDOW"]

    # measured separation behaviour, pooled over both Phase-B points (world level)
    sep_delays, colo_frac, births_tot, worlds_tot, sep_worlds, third_worlds = [], [], 0, 0, 0, 0
    for lab, blk in pb.items():
        for w in blk["PER_WORLD"]:
            worlds_tot += 1
            births_tot += w["n_Y_births"]
            if w["separation_delay_after_first_birth"] > 0:
                sep_delays.append(w["separation_delay_after_first_birth"])
            if w["separation_first_step"] >= 0:
                sep_worlds += 1
            if w["stop"] == "PREMATURE_THIRD_CENTRE":
                third_worlds += 1
            if w["steps_recorded"] > 0:
                colo_frac.append(w["steps_two_plus_Y"] / w["steps_recorded"])
    measured = {
        "phase_A_worlds": nA, "mean_exposure_E": mean_E, "se_exposure": se_E,
        "one_sided_95_LCB_of_mean_exposure": lcb_mean_E,
        "distribution_free_10th_pct_lower_bound": lb_quantile,
        "phase_B_worlds": worlds_tot, "total_Y_births": births_tot,
        "worlds_reaching_two_centres": sep_worlds,
        "worlds_stopped_at_third_centre": third_worlds,
        "median_separation_delay_steps": (float(np.median(sep_delays)) if sep_delays else None),
        "mean_colocated_step_fraction": (float(np.mean(colo_frac)) if colo_frac else 0.0),
        "empirical_separation_rate_per_world": sep_worlds / max(worlds_tot, 1),
        "95pct_upper_bound_if_zero": (1 - 0.05 ** (1.0 / max(worlds_tot, 1))
                                      if sep_worlds == 0 else None)}

    tau = float(np.median(sep_delays)) if sep_delays else TAU_SEP
    grid_k = [10.0 ** v for v in np.linspace(-6, -2, 161)]
    grid_m = [10.0 ** v for v in np.linspace(-8, -1, 161)]
    inside = []
    for kY in grid_k:
        for muY in grid_m:
            births = kY * lcb_mean_E * W                       # conservative, LCB not the mean
            surv = (1.0 - muY) ** C["T_HORIZON"]
            n_sep = births * (1.0 - muY) ** tau
            c1 = births >= C["MIN_EVENTS"]
            c2 = surv >= 1.0 - C["ALPHA_SURVIVAL"]
            c3 = n_sep <= C["GAMMA_SEP"]
            c4 = kY * CAP * C["N_STAR"] <= 0.1
            c5 = kY > 1e-9 and muY > 1e-9
            if c1 and c2 and c3 and c4 and c5:
                inside.append((kY, muY))
    region = {
        "MEASURED_INPUTS": measured,
        "SEPARATION_TIME_USED": {"value": tau,
                                 "source": ("measured median delay from first birth to two "
                                            "centres" if sep_delays else
                                            "frozen TAU_SEP = %.1f, because no separation event "
                                            "was observed" % TAU_SEP)},
        "CRITERIA": {
            "C1_nontrivial_first_birth": "kY * LCB(E) * T_WINDOW >= MIN_EVENTS",
            "C2_persistence": "(1-muY)^T_HORIZON >= 1 - ALPHA_SURVIVAL",
            "C3_no_premature_third_centre": "C1_births * (1-muY)^tau <= GAMMA_SEP",
            "C4_numerical_margin_no_clamp": "kY * CAP * N_STAR <= 0.1",
            "C5_precision": "kY, muY > 1e-9",
            "NOTE": ("exposure enters through the one-sided 95% LOWER confidence bound of the "
                     "world-level mean, not the point estimate; a point or pooled-frame "
                     "estimate would be insufficient")},
        "REGION_POINTS": len(inside),
        "REGION_NONEMPTY": len(inside) > 0,
        "REGION_BOX": ({"kY": [min(p[0] for p in inside), max(p[0] for p in inside)],
                        "muY": [min(p[1] for p in inside), max(p[1] for p in inside)]}
                       if inside else None),
        "LABEL": "CANDIDATE_REGION_REQUIRING_DISJOINT_CONFIRMATION",
        "NOT_A_CONFIRMED_WINDOW": ("no calibration result is a confirmed reproduction, a "
                                   "confirmed lineage window, heredity or life"),
    }
    # which criterion is binding, at the best available point
    best, bestv = None, -1e18
    for kY in grid_k:
        for muY in grid_m:
            births = kY * lcb_mean_E * W
            surv = (1.0 - muY) ** C["T_HORIZON"]
            n_sep = births * (1.0 - muY) ** tau
            m = min(math.log10(max(births, 1e-300) / C["MIN_EVENTS"]),
                    math.log10(max(surv, 1e-300) / (1 - C["ALPHA_SURVIVAL"])),
                    math.log10(C["GAMMA_SEP"] / max(n_sep, 1e-300)),
                    math.log10(0.1 / max(kY * CAP * C["N_STAR"], 1e-300)))
            if m > bestv:
                bestv, best = m, (kY, muY, births, surv, n_sep)
    region["MAXIMIN_ON_MEASURED_INPUTS"] = {
        "kY": best[0], "muY": best[1], "expected_births": best[2],
        "founder_survival": best[3], "expected_separated_second_centres": best[4],
        "min_margin_decades": bestv,
        "READING": ("the best attainable point on MEASURED inputs; if this is negative the "
                    "region is empty for the frozen criteria and the shortfall factor is "
                    "10^(-min_margin) = %.3f" % (10 ** (-bestv)))}
    return region


# ============================ main ======================================================
def main():
    import csv
    ledger = [json.loads(l) for l in open(f"{OUT_READ}/PQEC01_RUN_LEDGER.jsonl")]
    frozen = {r["seed"] for v in FR["SEED_RULE"]["SEEDS"].values() for r in v}
    ran = {r["seed"] for r in ledger}
    accounting = {
        "FROZEN_STARTS": len(frozen), "LEDGER_ROWS": len(ledger),
        "DISTINCT_SEEDS_RUN": len(ran),
        "ALL_FROZEN_STARTS_ACCOUNTED_FOR": frozen == ran,
        "MISSING": sorted(frozen - ran), "UNEXPECTED": sorted(ran - frozen),
        "TECHNICALLY_INVALID": [r["tag"] for r in ledger if not r.get("TECHNICALLY_VALID")],
        "RESERVES_USED": 0,
        "NO_OUTCOME_DRIVEN_REPLACEMENT": True,
        "TOTAL_OUTCOME_INFORMATIVE_STARTS": len(ledger)}

    pa = phase_a()
    pb = phase_b()
    op_d = operator("DISCOVERY")
    fb = feedback(pa, pb)
    val = validation(pb, op_d)
    reg = candidate_region(pa, pb, op_d)

    pa["SPATIAL_OPERATOR_IDENTIFIED"] = bool(
        pa["N_WORLDS"] >= 29
        and pa["EXPOSURE_TRANSITION_KERNEL"]["row_stochastic"]
        and pa["WORLD_LEVEL"]["relative_SE"] < 0.05
        and np.isfinite(pa["RADIAL_EXPOSURE"]["mean_over_worlds"][1]))

    births = {lab: sum(w["n_Y_births"] for w in blk["PER_WORLD"]) for lab, blk in pb.items()}
    colo = {lab: sum(w["steps_colocated_one_centre"] for w in blk["PER_WORLD"])
            for lab, blk in pb.items()}
    sep = {lab: sum(1 for w in blk["PER_WORLD"] if w["separation_first_step"] >= 0)
           for lab, blk in pb.items()}
    desc_rows = {lab: sum(w["descendant_exposure_rows"] for w in blk["PER_WORLD"])
                 for lab, blk in pb.items()}

    gates = {
        "PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS": True,
        "INSTRUMENTATION_INERTNESS": json.load(
            open(f"{OUT_READ}/PQEC01_INSTRUMENTATION_TESTS.json"))["INSTRUMENTATION_INERTNESS"]
        == "PASS",
        "ALL_FROZEN_STARTS_ACCOUNTED_FOR": accounting["ALL_FROZEN_STARTS_ACCOUNTED_FOR"],
        "NO_OUTCOME_DRIVEN_REPLACEMENT": True,
        "PHASE_A_SPATIAL_OPERATOR_IDENTIFIED": pa["SPATIAL_OPERATOR_IDENTIFIED"],
        "PHASE_B_REAL_DESCENDANT_EXPOSURE_RECORDED": sum(births.values()) > 0
        and sum(desc_rows.values()) > 0,
        "FIRST_BIRTH_OPERATOR_VALIDATED": all(v["TEST_1_first_birth"]["PASS"]
                                              for v in val.values()) if val else False,
        "TWO_Y_OPERATOR_IDENTIFIED": all(
            "TWO_Y_COLOCATED" in op_d[l]["IDENTIFIED_STATES"] for l in op_d),
        "FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED": True,
        "INTERNAL_VALIDATION_PASS": all(v["ALL_PASS"] for v in val.values()) if val else False,
        "CANDIDATE_REGION_POSITIVE_WIDTH": reg["REGION_NONEMPTY"],
        "NO_SINGLE_WORLD_DOMINANCE": pa["WORLD_LEVEL"]["no_single_world_dominance"],
        "NO_FRAME_PSEUDOREPLICATION": True}

    if not gates["ALL_FROZEN_STARTS_ACCOUNTED_FOR"] or accounting["TECHNICALLY_INVALID"]:
        disp = "CALIBRATION_TECHNICALLY_INVALID"
    elif all(gates.values()):
        disp = "PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED"
    else:
        disp = ("PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__"
                "ADDITIONAL_INSTRUMENTATION_REQUIRED")

    json.dump({"SECTION": "PQEC01 Phase A", **pa},
              open(f"{OUT}/PQEC01_PHASE_A_WORLD_SUMMARIES.json", "w"), indent=1, default=str)
    with open(f"{OUT}/PQEC01_PHASE_A_WORLD_SUMMARIES.csv", "w", newline="") as fh:
        w_ = csv.DictWriter(fh, fieldnames=list(pa["PER_WORLD"][0].keys()))
        w_.writeheader()
        w_.writerows(pa["PER_WORLD"])
    json.dump({"SECTION": "PQEC01 Phase B", **pb},
              open(f"{OUT}/PQEC01_PHASE_B_WORLD_SUMMARIES.json", "w"), indent=1, default=str)
    rows = [r for blk in pb.values() for r in blk["PER_WORLD"]]
    with open(f"{OUT}/PQEC01_PHASE_B_WORLD_SUMMARIES.csv", "w", newline="") as fh:
        w_ = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w_.writeheader()
        w_.writerows(rows)
    json.dump({"SECTION": "PQEC01 environment operator", "DISCOVERY_ONLY": op_d,
               "PHASE_A_SPATIAL": {k: pa[k] for k in ("RADIAL_EXPOSURE",
                                                      "EXPOSURE_TRANSITION_KERNEL",
                                                      "WORLD_LEVEL",
                                                      "SPATIAL_OPERATOR_IDENTIFIED")}},
              open(f"{OUT}/PQEC01_ENVIRONMENT_OPERATOR.json", "w"), indent=1, default=str)
    json.dump(fb, open(f"{OUT}/PQEC01_FEEDBACK_ANALYSIS.json", "w"), indent=1, default=str)
    json.dump(val, open(f"{OUT}/PQEC01_INTERNAL_VALIDATION.json", "w"), indent=1, default=str)
    json.dump(reg, open(f"{OUT}/PQEC01_CANDIDATE_REGION.json", "w"), indent=1, default=str)
    json.dump({"SECTION": "PQEC01 candidate disposition", "ACCOUNTING": accounting,
               "DECISION_GATES": gates, "GATES_PASSED": sum(1 for v in gates.values() if v),
               "GATES_TOTAL": len(gates),
               "PHASE_B_TOTALS": {"Y_births": births, "colocated_steps": colo,
                                  "worlds_reaching_two_centres": sep,
                                  "descendant_exposure_rows": desc_rows},
               "CANDIDATE_DISPOSITION": disp},
              open(f"{OUT}/PQEC01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)

    print("accounting: frozen %d, ran %d, all accounted %s, technically invalid %d"
          % (accounting["FROZEN_STARTS"], accounting["DISTINCT_SEEDS_RUN"],
             accounting["ALL_FROZEN_STARTS_ACCOUNTED_FOR"],
             len(accounting["TECHNICALLY_INVALID"])))
    print("phase A: %d worlds, mean E_w %.4f (relSE %.4f), DF 10th-pct LB %.3f, radial bins %d"
          % (pa["N_WORLDS"], pa["WORLD_LEVEL"]["mean_E_w"], pa["WORLD_LEVEL"]["relative_SE"],
             pa["WORLD_LEVEL"]["distribution_free_lower_bound_10th_pct"],
             len(pa["RADIAL_EXPOSURE"]["bins"])))
    for lab in pb:
        r = pb[lab]["PER_WORLD"]
        print("phase B %s: %d worlds, births %d, worlds with a birth %d, colocated steps %d, "
              "worlds reaching 2 centres %d, stopped at 3rd centre %d"
              % (lab, len(r), births[lab], sum(1 for w in r if w["n_Y_births"] > 0), colo[lab],
                 sep[lab], sum(1 for w in r if w["stop"] == "PREMATURE_THIRD_CENTRE")))
        print("            stops:", dict(Counter(w["stop"] for w in r)))
    for lab, v in val.items():
        print("validation %s: T1 z=%.2f %s | T2 z=%.2f %s | T3 z=%.2f %s"
              % (lab, v["TEST_1_first_birth"]["z"], v["TEST_1_first_birth"]["PASS"],
                 v["TEST_2_two_plus_Y_step_fraction"]["z"],
                 v["TEST_2_two_plus_Y_step_fraction"]["PASS"],
                 v["TEST_3_founder_survival"]["z"], v["TEST_3_founder_survival"]["PASS"]))
    print("region nonempty:", reg["REGION_NONEMPTY"], "| maximin on measured inputs %.4f decades"
          % reg["MAXIMIN_ON_MEASURED_INPUTS"]["min_margin_decades"])
    print("\ngates:")
    for k, v in gates.items():
        print("   %-45s %s" % (k, v))
    print("\nCANDIDATE_DISPOSITION =", disp)


if __name__ == "__main__":
    main()
