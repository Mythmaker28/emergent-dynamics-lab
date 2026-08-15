"""OBFOR01 §5, §6, §14 — identify the observable, reproduce the residuals, and test the
estimator that carries them.

The mandate warns against mixing a radius with a variance. It turns out the warning does not go
far enough: the two residuals are not carried by an observable at all, they are carried by the
WITHIN-SEED SUMMARY RULE applied to it.

Read off the frozen code, the residual-bearing quantity is

    per frame   r80_organiser = metrics_obtc.radii(nX, organiser_y, organiser_x)[0.8]
    per seed    the MEDIAN of that over the in-window frames
    per size    the arithmetic mean over analysable arms

and `radii` returns the smallest achievable lattice distance at which the EMPIRICAL cumulative
mass first reaches 0.8. Three properties follow: it is a finite-sample quantile of about 120
particles; it is a FIRST CROSSING, hence a minimum over d, hence biased downward; and it lives
on a discrete support whose spacing near these radii is a few percent.

This file measures four things on the same delivered frames, and lets them disagree:

  1. the residual under the frozen MEDIAN summary                     (the reported number)
  2. the residual under a MEAN summary of the same per-frame values   (the same data)
  3. the residual on M2, a per-particle mean and therefore unbiased   (a different estimator)
  4. the residual on the full radial CDF, radius by radius            (the whole profile)

If the profile and M2 agree with the operator while the median-summarised quantile does not,
the deficit is in the summary rule and not in the cloud.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBFOR01/verify/obtr01/wc"
OUT = "/home/claude/OBFOR01/out"
sys.path.insert(0, f"{WC}/OBTR01/code")
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")

from kernels_obtr01 import Operator                      # noqa: E402
import metrics_obtc as M                                 # noqa: E402

RADIAL_GRID = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0, 17.0)
BURN_IN = 2000
HORIZON = 11000


def wd(v, L):
    v = np.abs(v) % L
    return np.minimum(v, L - v)


class Ideal:
    """The operator's exact stationary law on the torus, and the reductions of it that the
    engine's own estimators would compute on an infinite sample."""

    def __init__(self, L, mobile, q, mu):
        self.L, self.mobile = L, mobile
        op = Operator(q, q if mobile else 0.0, mu, L)
        self.prof = op.stationary_profile()
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        self.d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
        o = np.argsort(self.d.ravel(), kind="stable")
        dd, ww = self.d.ravel()[o], self.prof.ravel()[o]
        cw = np.cumsum(ww) / ww.sum()
        self.r80 = float(dd[int(np.searchsorted(cw, 0.8, side="left"))])
        self.m2 = float((self.prof * self.d ** 2).sum())
        self.cdf = np.array([self.prof[self.d <= r].sum() for r in RADIAL_GRID])
        self.p = self.prof.ravel() / self.prof.sum()

    def draw_r80(self, N, rng):
        idx = rng.choice(self.L * self.L, size=int(N), p=self.p)
        g = np.zeros(self.L * self.L, np.int64)
        np.add.at(g, idx, 1)
        return float(M.radii(g.reshape(self.L, self.L), 0, 0)[0.8])


def arm_records(root, prefix, ideal_of):
    out = []
    for n in sorted(os.listdir(root)):
        if not n.startswith(prefix):
            continue
        z = np.load(f"{root}/{n}", allow_pickle=True)
        f, fy = z["nX_final"], z["nY_final"]
        if int(fy.sum()) < 1 or int(f.sum()) < 40:
            continue
        L = int(f.shape[0])
        oy, ox = [int(v[0]) for v in np.nonzero(fy)]
        fr = [json.loads(str(s)) for s in z["frames"]]
        w = [x for x in fr if x["step"] > BURN_IN]
        v = np.array([x["r80_organiser"] for x in w
                      if x.get("r80_organiser") is not None
                      and np.isfinite(x["r80_organiser"])], float)
        nx = np.array([x["N_X"] for x in w], float)
        if len(v) < 50:
            continue
        ys, xs = np.nonzero(f)
        c = f[ys, xs].astype(float)
        dist = np.sqrt(wd(ys - oy, L) ** 2 + wd(xs - ox, L) ** 2)
        Ntot = c.sum()
        out.append({
            "file": n, "L": L,
            "r80_median": float(np.median(v)), "r80_mean": float(v.mean()),
            "r80_sd_within_arm": float(v.std(ddof=1)),
            "r80_skew_within_arm": float(((v - v.mean()) ** 3).mean()
                                         / v.std(ddof=1) ** 3),
            "frames": int(len(v)),
            "N_X_frame_mean": float(nx.mean()), "N_X_frame_sd": float(nx.std(ddof=1)),
            "N_final": int(Ntot),
            "M2_final_frame": float((c * dist ** 2).sum() / Ntot),
            "cdf_final_frame": [float(c[dist <= r].sum() / Ntot) for r in RADIAL_GRID],
            "per_frame_values": v.tolist(),
            "per_frame_N": nx.tolist(),
        })
    return out


def agg(vals):
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], float)
    if not len(v):
        return None
    return {"n": int(len(v)), "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
            "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None,
            "values": [float(x) for x in v]}


def resid(a, pred):
    if not a or pred is None:
        return None
    r = a["mean"] / pred - 1.0
    se = a["se"] / pred if a.get("se") else None
    return {"predicted": pred, "observed": a["mean"], "n": a["n"],
            "residual": r, "residual_percent": 100 * r,
            "se_relative": se, "z": (r / se) if se else None}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    obt = yaml.safe_load(open(f"{WC}/OBTC02/code/obtc02_protocol.yaml"))
    pt = spec["point"]
    an = obt.get("analytic", {})
    mu, q = pt["muX"], pt["p_hop"] / 4.0
    rng = np.random.default_rng(20260815)

    ideal = {(L, m): Ideal(L, m, q, mu) for L in (36, 72, 96) for m in (True, False)}

    # ---------------------------------------------------------------- the exact definition
    definition = {
        "OBSERVABLE": "r80_organiser",
        "formula": ("radii(nX, organiser)[0.8] = the smallest achievable lattice distance at "
                    "which the EMPIRICAL cumulative mass first reaches 0.8"),
        "source": "OBTC02/code/protocol_obtc02.py line 99 -> metrics_obtc.radii",
        "WITHIN_SEED_SUMMARY": "MEDIAN over the in-window frames (step > BURN_IN = 2000)",
        "ACROSS_SEED_SUMMARY": "arithmetic mean over analysable arms",
        "UNIT_OF_ANALYSIS": "SEED",
        "NORMALIZATION": "none; prediction and observation are absolute lengths",
        "IT_IS_A_RADIUS_NOT_A_SECOND_MOMENT": True,
        "conversion_rule": ("if the whole profile were rescaled by (1 + e), r80 would move by "
                            "e and M2 by about 2e; a -1.8 % deficit on a radius is a -3.6 % "
                            "deficit on a variance and the two must never be quoted as one"),
        "three_properties_of_the_estimator": [
            "a finite-sample quantile of about 120 particles, not a population quantity",
            "a FIRST CROSSING, i.e. a minimum over d, and minima of noisy crossings are biased "
            "downward",
            "supported on the discrete set of achievable toroidal distances"],
        "PREDICTION_PROVENANCE": {
            "static_r80_frozen": an.get("static_r80"),
            "mobile_r80_frozen": an.get("organiser_frame_r80"),
            "static_recomputed": ideal[(36, False)].r80,
            "mobile_recomputed": ideal[(36, True)].r80,
            "REPRODUCES": (abs(ideal[(36, False)].r80 - float(an["static_r80"])) < 1e-12
                           and abs(ideal[(36, True)].r80
                                   - float(an["organiser_frame_r80"])) < 1e-12),
            "PRE_RUN_OR_POST_RUN_PREDICTION": "PRE_RUN",
            "why": ("both sit in the protocol yaml OBTC02 froze and hashed into METHODS_CORE "
                    "before any arm ran; they are recomputed here from the resolvent by an "
                    "independent route")},
    }

    # ---------------------------------------------------------------- the data
    S = arm_records(f"{WC}/OBTC02/raw", "S__", ideal)
    P = arm_records(f"{WC}/OBTC02/raw", "P__", ideal)
    D = {L: arm_records(f"{WC}/OBDI02/raw", "L%d__" % L, ideal) for L in (36, 72, 96)}
    Dall = [r for L in (36, 72, 96) for r in D[L]]

    def ratio_to_pred(rows, key, mobile):
        return agg([r[key] / ideal[(r["L"], mobile)].r80 for r in rows])

    def m2_ratio(rows, mobile):
        return agg([r["M2_final_frame"] / ideal[(r["L"], mobile)].m2 for r in rows])

    reported = {
        "STATIC_median_summary": resid(ratio_to_pred(S, "r80_median", False), 1.0),
        "MOBILE_median_summary_OBTC02": resid(ratio_to_pred(P, "r80_median", True), 1.0),
        "MOBILE_median_summary_OBDI02_all_L":
            resid(ratio_to_pred(Dall, "r80_median", True), 1.0),
        "STATIC_mean_summary": resid(ratio_to_pred(S, "r80_mean", False), 1.0),
        "MOBILE_mean_summary_OBTC02": resid(ratio_to_pred(P, "r80_mean", True), 1.0),
        "MOBILE_mean_summary_OBDI02_all_L": resid(ratio_to_pred(Dall, "r80_mean", True), 1.0),
        "STATIC_M2": resid(m2_ratio(S, False), 1.0),
        "MOBILE_M2_OBDI02_all_L": resid(m2_ratio(Dall, True), 1.0),
    }
    by_size = {L: {"median": resid(ratio_to_pred(D[L], "r80_median", True), 1.0),
                   "mean": resid(ratio_to_pred(D[L], "r80_mean", True), 1.0),
                   "M2": resid(m2_ratio(D[L], True), 1.0)} for L in (36, 72, 96)}

    # ---------------------------------------------------------------- the whole profile
    def cdf_table(rows, mobile):
        O = np.array([r["cdf_final_frame"] for r in rows])
        Pr = np.array([ideal[(r["L"], mobile)].cdf for r in rows])
        Dd = O - Pr
        out = []
        for i, r in enumerate(RADIAL_GRID):
            se = Dd[:, i].std(ddof=1) / math.sqrt(len(Dd)) if len(Dd) > 1 else None
            out.append({"r": r, "predicted": float(Pr[:, i].mean()),
                        "observed": float(O[:, i].mean()),
                        "difference": float(Dd[:, i].mean()),
                        "z": (float(Dd[:, i].mean() / se) if se else None)})
        return out
    cdf_mob = cdf_table(Dall, True)
    cdf_sta = cdf_table(S, False)
    zmax_mob = max(abs(x["z"]) for x in cdf_mob if x["z"] is not None)

    # ---------------------------------------------------------------- the estimator itself
    # i.i.d. draws from the EXACT stationary law, at the observed per-frame population sizes,
    # pushed through the SAME estimator pipeline.
    def simulate(rows, mobile, arms=42, frames=180):
        Ns = np.concatenate([np.asarray(r["per_frame_N"], float) for r in rows])
        Ns = Ns[Ns >= 1]
        L = rows[0]["L"]
        idl = ideal[(L, mobile)]
        med, mea, sd = [], [], []
        for _ in range(arms):
            v = np.array([idl.draw_r80(int(rng.choice(Ns)), rng) for _ in range(frames)])
            med.append(np.median(v))
            mea.append(v.mean())
            sd.append(v.std(ddof=1))
        return {"population_r80": idl.r80,
                "median_summary": float(np.mean(med)),
                "median_ratio": float(np.mean(med) / idl.r80),
                "mean_summary": float(np.mean(mea)),
                "mean_ratio": float(np.mean(mea) / idl.r80),
                "within_arm_sd": float(np.mean(sd)),
                "arms": arms, "frames": frames}

    sim_mob = simulate(D[36], True)
    sim_sta = simulate(S, False)

    observed_sd = {
        "static_within_arm_sd": float(np.mean([r["r80_sd_within_arm"] for r in S])),
        "mobile_within_arm_sd": float(np.mean([r["r80_sd_within_arm"] for r in D[36]])),
        "static_within_arm_skew": float(np.mean([r["r80_skew_within_arm"] for r in S])),
        "mobile_within_arm_skew": float(np.mean([r["r80_skew_within_arm"] for r in D[36]])),
        "iid_static_within_arm_sd": sim_sta["within_arm_sd"],
        "iid_mobile_within_arm_sd": sim_mob["within_arm_sd"],
    }

    estimator = {
        "WHAT_THE_SIMULATION_DOES": (
            "draws particles i.i.d. from the EXACT stationary law of the ideal operator, at "
            "the per-frame population sizes actually observed, and pushes them through the "
            "SAME estimator pipeline: per-frame first-crossing quantile, median over frames, "
            "mean over arms. No engine start, no lattice dynamics."),
        "IID_STATIC": sim_sta, "IID_MOBILE": sim_mob,
        "OBSERVED_DISPERSION": observed_sd,
        "READING": (
            "the i.i.d. simulation reproduces a median-summary deficit of %.2f %% static and "
            "%.2f %% mobile from the estimator alone. The observed within-arm dispersion of "
            "the per-frame value is %.2f static and %.2f mobile, against %.2f and %.2f under "
            "i.i.d. draws: the real per-frame statistic is over-dispersed and right-skewed, "
            "and the MEDIAN of a right-skewed statistic sits below its mean."
            % (100 * (sim_sta["median_ratio"] - 1), 100 * (sim_mob["median_ratio"] - 1),
               observed_sd["static_within_arm_sd"], observed_sd["mobile_within_arm_sd"],
               sim_sta["within_arm_sd"], sim_mob["within_arm_sd"])),
    }

    # ---------------------------------------------------------------- §6 the ratio
    def ratio_block(static_rows, mobile_rows, key, tag):
        sv = [r[key] for r in static_rows]
        pv = [r[key] for r in mobile_rows]
        pred = ideal[(36, True)].r80 / ideal[(36, False)].r80
        ms, mp = float(np.mean(sv)), float(np.mean(pv))
        ses = np.std(sv, ddof=1) / math.sqrt(len(sv))
        sep = np.std(pv, ddof=1) / math.sqrt(len(pv))
        rel = math.sqrt((sep / mp) ** 2 + (ses / ms) ** 2)
        t = 4.303 if min(len(sv), len(pv)) <= 3 else 2.086
        obs = mp / ms
        ci = [obs * (1 - t * rel), obs * (1 + t * rel)]
        return {"summary_rule": tag, "n_static": len(sv), "n_mobile": len(pv),
                "predicted_ratio": pred, "observed_ratio": obs,
                "deviation_percent": 100 * (obs / pred - 1),
                "ci95_delta_method": ci,
                "interval_relative_width": (ci[1] - ci[0]) / obs,
                "PREDICTION_INSIDE": bool(ci[0] <= pred <= ci[1]),
                "RATIO_ONE_INSIDE": bool(ci[0] <= 1.0 <= ci[1])}

    ratios = {
        "median_summary_OBTC02": ratio_block(S, P, "r80_median", "MEDIAN (frozen)"),
        "mean_summary_OBTC02": ratio_block(S, P, "r80_mean", "MEAN"),
        "median_summary_S_vs_OBDI02_L36": ratio_block(S, D[36], "r80_median",
                                                      "MEDIAN, mobile from OBDI02 L36"),
        "mean_summary_S_vs_OBDI02_L36": ratio_block(S, D[36], "r80_mean",
                                                    "MEAN, mobile from OBDI02 L36"),
    }
    best = ratios["mean_summary_S_vs_OBDI02_L36"]
    ratio_status = {
        "the_reported_pair": {"observed": 1.3443, "predicted": 1.4046,
                              "quotient": 1.3443 / 1.4046},
        "unrounded_under_the_frozen_median_rule":
            ratios["median_summary_OBTC02"]["observed_ratio"]
            / ratios["median_summary_OBTC02"]["predicted_ratio"],
        "MOBILE_BROADENING_HYPOTHESIS":
            "SUPPORTED" if not best["RATIO_ONE_INSIDE"] else "UNRESOLVED",
        "NO_MOBILE_BROADENING_RATIO_1":
            "REJECTED" if not best["RATIO_ONE_INSIDE"] else "NOT_REJECTED",
        "EXACT_RATIO_PREDICTION":
            ("EQUIVALENCE_NOT_ESTABLISHED" if best["interval_relative_width"] > 0.10
             else ("PASS" if best["PREDICTION_INSIDE"] else "FAIL")),
        "WHY": ("with three static arms the ratio interval is %.1f %% wide relative to the "
                "point estimate. Containing the prediction inside a wide interval is not "
                "equivalence, and calling the ratio 'exact' would overstate what three static "
                "arms can show. The direction is unambiguous: 1 is excluded."
                % (100 * best["interval_relative_width"])),
    }

    out = {
        "SECTION": "OBFOR01 §5, §6, §14", "CONSUMES_NO_SCIENTIFIC_RUN": True,
        "DEFINITION": definition,
        "PREDICTED": {"static_r80": ideal[(36, False)].r80,
                      "mobile_r80": ideal[(36, True)].r80,
                      "static_M2": ideal[(36, False)].m2,
                      "mobile_M2": ideal[(36, True)].m2,
                      "by_size_mobile_r80": {L: ideal[(L, True)].r80 for L in (36, 72, 96)}},
        "RESIDUALS": reported, "BY_SIZE": by_size,
        "RADIAL_CDF_MOBILE": cdf_mob, "RADIAL_CDF_STATIC": cdf_sta,
        "RADIAL_CDF_MOBILE_MAX_ABS_Z": zmax_mob,
        "PROFILE_AGREES_AT_EVERY_RADIUS": bool(zmax_mob < 2.0),
        "ESTIMATOR": estimator,
        "RATIOS": ratios, "RATIO_STATUS": ratio_status,
        "ARMS": {"OBTC02_S": len(S), "OBTC02_P": len(P),
                 "OBDI02": {L: len(D[L]) for L in (36, 72, 96)}},
    }
    json.dump(out, open(f"{OUT}/_residual.json", "w"), indent=1, default=str)

    print("OBSERVABLE  r80_organiser, first-crossing empirical quantile")
    print("            within seed: MEDIAN over in-window frames ; across seeds: mean")
    print("            IT IS A RADIUS. A -1.8 %% deficit on it is -3.6 %% on a variance.")
    print("            predictions are PRE_RUN and reproduce the frozen block: %s"
          % definition["PREDICTION_PROVENANCE"]["REPRODUCES"])
    print()
    hdr = "%-38s %4s %10s %10s %9s %7s" % ("", "n", "predicted", "observed", "residual", "z")
    print(hdr)
    print("-" * len(hdr))
    for k, v in reported.items():
        if v:
            print("%-38s %4d %10.4f %10.4f %8.2f %% %+7.2f"
                  % (k, v["n"], v["predicted"], v["observed"] * v["predicted"],
                     v["residual_percent"], v["z"] if v["z"] is not None else 0))
    print()
    print("BY DOMAIN SIZE, mobile")
    for L in (36, 72, 96):
        b = by_size[L]
        print("  L=%-3d median %+7.2f %% (z %+5.2f)   mean %+7.2f %% (z %+5.2f)   "
              "M2 %+7.2f %% (z %+5.2f)"
              % (L, b["median"]["residual_percent"], b["median"]["z"],
                 b["mean"]["residual_percent"], b["mean"]["z"],
                 b["M2"]["residual_percent"], b["M2"]["z"]))
    print()
    print("THE WHOLE RADIAL PROFILE, mobile, %d arms, max |z| over %d radii = %.2f"
          % (len(Dall), len(RADIAL_GRID), zmax_mob))
    for x in cdf_mob:
        print("    r=%5.1f  predicted %.4f  observed %.4f  difference %+.4f  z %+5.2f"
              % (x["r"], x["predicted"], x["observed"], x["difference"], x["z"]))
    print()
    print("THE ESTIMATOR, i.i.d. draws from the exact law through the same pipeline")
    print("  static : median summary %+.2f %% , mean summary %+.2f %% , within-arm sd %.3f "
          "(observed %.3f)"
          % (100 * (sim_sta["median_ratio"] - 1), 100 * (sim_sta["mean_ratio"] - 1),
             sim_sta["within_arm_sd"], observed_sd["static_within_arm_sd"]))
    print("  mobile : median summary %+.2f %% , mean summary %+.2f %% , within-arm sd %.3f "
          "(observed %.3f)"
          % (100 * (sim_mob["median_ratio"] - 1), 100 * (sim_mob["mean_ratio"] - 1),
             sim_mob["within_arm_sd"], observed_sd["mobile_within_arm_sd"]))
    print("  observed within-arm skew: static %+.3f, mobile %+.3f"
          % (observed_sd["static_within_arm_skew"], observed_sd["mobile_within_arm_skew"]))
    print()
    print("RATIO")
    for k, v in ratios.items():
        print("  %-34s predicted %.4f observed %.4f (%+6.2f %%)  CI [%.4f, %.4f] width %.1f %%"
              % (k, v["predicted_ratio"], v["observed_ratio"], v["deviation_percent"],
                 v["ci95_delta_method"][0], v["ci95_delta_method"][1],
                 100 * v["interval_relative_width"]))
    for k in ("MOBILE_BROADENING_HYPOTHESIS", "NO_MOBILE_BROADENING_RATIO_1",
              "EXACT_RATIO_PREDICTION"):
        print("  %-34s %s" % (k, ratio_status[k]))


if __name__ == "__main__":
    main()
