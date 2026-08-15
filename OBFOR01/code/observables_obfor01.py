"""OBFOR01 §5-§6 — what exactly carries the -1.8 % and the -6.1 %, and what the ratio is.

The mandate is blunt about the trap: "un écart de 2 % sur un rayon ne représente pas le même
écart sur sa variance". So the first job is not interpretation, it is IDENTIFICATION.

Read off the frozen code, the residual-bearing quantity is

    r80_organiser = metrics_obtc.radii(nX, organiser_y, organiser_x)[0.8]

and `radii` is

    d  = toroidal distance field from the given centre, flattened
    w  = the X occupancy, flattened, sorted by d
    cw = cumsum(w) / N
    r_q = d[ searchsorted(cw, q, side="left") ]

which is the SMALLEST lattice distance at which the empirical cumulative mass reaches q. Three
properties follow and none of them is innocent:

  1. it is an EMPIRICAL QUANTILE of about 120 particles, not a population quantity;
  2. it is a FIRST CROSSING, i.e. a minimum over d of {d : F_hat(d) >= q}, and minima of noisy
     crossings are biased DOWNWARD;
  3. it takes values only on the discrete set of achievable toroidal distances, whose spacing
     near the relevant radii is a few percent -- comparable to the residual itself.

So this section reports the residual on r80 AND on M2, the mean per-particle squared distance
to the organiser, which is a per-particle mean and therefore unbiased at every N. If the
deficit is on r80 and not on M2, it is an estimator artefact; if it is on both, it is physical.
Nothing here interprets: it measures both and reports the contrast.
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


def wd(d, L):
    d = np.abs(d) % L
    return np.minimum(d, L - d)


def profile_radii_and_m2(op, L, qs=(0.5, 0.8, 0.9)):
    """The operator's exact stationary law on the torus, reduced by the SAME rule the engine's
    `radii` uses (first crossing on the sorted distance field), plus its exact second moment."""
    prof = op.stationary_profile()
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    o = np.argsort(d.ravel(), kind="stable")
    dd, ww = d.ravel()[o], prof.ravel()[o]
    cw = np.cumsum(ww) / ww.sum()
    rq = {q: float(dd[int(np.searchsorted(cw, q, side="left"))]) for q in qs}
    m2 = float((prof * d ** 2).sum())
    return rq, m2, prof, d


def observed_from_frames(z, burn_in):
    fr = [json.loads(str(s)) for s in z["frames"]]
    w = [f for f in fr if f["step"] > burn_in]

    def med(k):
        v = [f[k] for f in w if f.get(k) is not None and np.isfinite(f[k])]
        return (float(np.median(v)), len(v)) if v else (None, 0)
    r80o, n80 = med("r80_organiser")
    rg, _ = med("Rg")
    otc, _ = med("organiser_to_core")
    nx, _ = med("N_X")
    return {"r80_organiser": r80o, "n_frames_used": n80, "Rg": rg,
            "organiser_to_core": otc, "N_X": nx, "frames_in_window": len(w)}


def m2_from_final(z):
    f, fy = z["nX_final"], z["nY_final"]
    if int(fy.sum()) < 1 or int(f.sum()) < 1:
        return None
    L = int(f.shape[0])
    oy, ox = [int(v[0]) for v in np.nonzero(fy)]
    ys, xs = np.nonzero(f)
    n = f[ys, xs].astype(float)
    d2 = wd(ys - oy, L) ** 2 + wd(xs - ox, L) ** 2
    N = float(n.sum())
    return {"M2": float((n * d2).sum() / N), "N": int(N), "L": L,
            "r80_from_the_same_frame": float(M.radii(f, oy, ox)[0.8])}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    obt = yaml.safe_load(open(f"{WC}/OBTC02/code/obtc02_protocol.yaml"))
    pt, win = spec["point"], spec["window"]
    an = obt.get("analytic", {})
    L, mu, q = int(pt["L"]), pt["muX"], pt["p_hop"] / 4.0
    burn_in = int(win["BURN_IN"])

    op_static = Operator(q, 0.0, mu, L)      # condition S: p_hop_Y = 0
    op_mobile = Operator(q, q, mu, L)        # condition P: the organiser moves
    rq_s, m2_s, prof_s, dfield = profile_radii_and_m2(op_static, L)
    rq_m, m2_m, prof_m, _ = profile_radii_and_m2(op_mobile, L)

    # ---------------------------------------------------------------- pre-run status
    frozen_static = an.get("static_r80")
    frozen_mobile = an.get("organiser_frame_r80")
    prerun = {
        "where_the_predictions_live": "OBTC02/code/obtc02_protocol.yaml, block `analytic`",
        "static_r80_frozen": frozen_static, "static_r80_recomputed": rq_s[0.8],
        "STATIC_REPRODUCES": abs(rq_s[0.8] - float(frozen_static)) < 1e-12,
        "mobile_r80_frozen": frozen_mobile, "mobile_r80_recomputed": rq_m[0.8],
        "MOBILE_REPRODUCES": abs(rq_m[0.8] - float(frozen_mobile)) < 1e-12,
        "STATUS": "PRE_RUN",
        "why": ("both figures sit inside the protocol yaml that OBTC02 froze and hashed into "
                "METHODS_CORE before any arm was run, so they are predictions and not fits. "
                "They are recomputed here from the resolvent by an independent route."),
        "M2_static_predicted": m2_s, "M2_mobile_predicted": m2_m,
        "M2_IS_NOT_IN_THE_FROZEN_BLOCK": "M2" not in json.dumps(an),
        "M2_prediction_status": ("DERIVED_IN_THIS_MISSION_FROM_THE_SAME_FROZEN_OPERATOR — it "
                                 "is a new reduction of an already-frozen law, not a new law"),
    }

    # ---------------------------------------------------------------- observations
    res0 = json.load(open(f"{WC}/OBTC02/out/_results.json"))
    rows = []
    for a in res0["arms"]:
        if a["condition"] not in ("S", "P"):
            continue
        p = f"{WC}/OBTC02/raw/{a['tag'].replace('/', '__')}.npz"
        if not os.path.exists(p):
            continue
        z = np.load(p, allow_pickle=True)
        r = observed_from_frames(z, burn_in)
        r.update({"tag": a["tag"], "condition": a["condition"], "L": a["L"],
                  "seed": a["seed"]})
        fin = m2_from_final(z)
        if fin:
            r.update({"M2_final_frame": fin["M2"], "N_final": fin["N"],
                      "r80_final_frame": fin["r80_from_the_same_frame"]})
        r["ANALYSABLE"] = bool(r.get("N_X") and r["N_X"] > 0)
        rows.append(r)

    # OBDI02 gives 138 more MOBILE arms; only L = 36 is comparable to the OBTC02 predictions
    mob36 = []
    for n in sorted(os.listdir(f"{WC}/OBDI02/raw")):
        if not n.startswith("L36__"):
            continue
        z = np.load(f"{WC}/OBDI02/raw/{n}", allow_pickle=True)
        fin = m2_from_final(z)
        if fin and fin["N"] >= 20:
            fr = observed_from_frames(z, burn_in)
            mob36.append({"file": n, "M2_final_frame": fin["M2"], "N_final": fin["N"],
                          "r80_organiser": fr["r80_organiser"], "N_X": fr["N_X"]})

    def agg(key, cond=None, src=None):
        if src is None:
            v = [r[key] for r in rows if r["condition"] == cond and r["ANALYSABLE"]
                 and r.get(key) is not None and np.isfinite(r[key])]
        else:
            v = [r[key] for r in src if r.get(key) is not None and np.isfinite(r[key])]
        if not v:
            return None
        v = np.asarray(v, float)
        return {"n": int(len(v)), "mean": float(v.mean()),
                "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None,
                "min": float(v.min()), "max": float(v.max()),
                "values": [float(x) for x in v]}

    obs = {
        "S_r80_organiser": agg("r80_organiser", "S"),
        "P_r80_organiser": agg("r80_organiser", "P"),
        "S_M2_final_frame": agg("M2_final_frame", "S"),
        "P_M2_final_frame": agg("M2_final_frame", "P"),
        "OBDI02_L36_M2_final_frame": agg("M2_final_frame", src=mob36),
        "OBDI02_L36_r80_organiser": agg("r80_organiser", src=mob36),
    }

    def residual(o, p):
        if not o or p is None:
            return None
        r = o["mean"] / p - 1.0
        se = (o["se"] / p) if o.get("se") else None
        return {"observed_mean": o["mean"], "predicted": p, "residual": r,
                "residual_percent": 100 * r, "n": o["n"], "se_of_the_ratio": se,
                "z": (r / se) if se else None,
                "ci95": ([o["mean"] - 1.96 * o["se"], o["mean"] + 1.96 * o["se"]]
                         if o.get("se") else None)}

    RES = {
        "STATIC_r80": residual(obs["S_r80_organiser"], rq_s[0.8]),
        "MOBILE_r80_OBTC02": residual(obs["P_r80_organiser"], rq_m[0.8]),
        "MOBILE_r80_OBDI02_L36": residual(obs["OBDI02_L36_r80_organiser"], rq_m[0.8]),
        "STATIC_M2": residual(obs["S_M2_final_frame"], m2_s),
        "MOBILE_M2_OBTC02": residual(obs["P_M2_final_frame"], m2_m),
        "MOBILE_M2_OBDI02_L36": residual(obs["OBDI02_L36_M2_final_frame"], m2_m),
    }

    # ---------------------------------------------------------------- radius vs variance
    conv = {
        "WHY_IT_MATTERS": ("r80 is a LENGTH and M2 is a SQUARED length. If the whole profile "
                           "were rescaled by a factor (1 + e), r80 would move by e and M2 by "
                           "about 2e. A -1.8 % deficit on a radius is a -3.6 % deficit on the "
                           "variance, and the two must never be quoted as the same number."),
        "static_r80_residual_percent": RES["STATIC_r80"]["residual_percent"],
        "static_implied_variance_residual_percent":
            100 * ((1 + RES["STATIC_r80"]["residual"]) ** 2 - 1),
        "static_M2_residual_percent": (RES["STATIC_M2"]["residual_percent"]
                                       if RES["STATIC_M2"] else None),
        "mobile_r80_residual_percent": RES["MOBILE_r80_OBTC02"]["residual_percent"],
        "mobile_implied_variance_residual_percent":
            100 * ((1 + RES["MOBILE_r80_OBTC02"]["residual"]) ** 2 - 1),
        "mobile_M2_residual_percent": (RES["MOBILE_M2_OBTC02"]["residual_percent"]
                                       if RES["MOBILE_M2_OBTC02"] else None),
    }

    # ---------------------------------------------------------------- §6 the ratio
    sv = obs["S_r80_organiser"]["values"]
    pv = obs["P_r80_organiser"]["values"]
    pred_ratio = rq_m[0.8] / rq_s[0.8]
    obs_ratio = float(np.mean(pv) / np.mean(sv))
    rng = np.random.default_rng(20260815)
    boot = np.array([np.mean(rng.choice(pv, len(pv))) / np.mean(rng.choice(sv, len(sv)))
                     for _ in range(40000)])
    ci = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
    # the seed is the independent unit, and n is 3 and 5, so a bootstrap of the mean is
    # optimistic. A Fieller-type interval on the ratio of two means with Welch standard
    # errors is reported beside it.
    ms, mp = np.mean(sv), np.mean(pv)
    ses = np.std(sv, ddof=1) / math.sqrt(len(sv))
    sep = np.std(pv, ddof=1) / math.sqrt(len(pv))
    rel = math.sqrt((sep / mp) ** 2 + (ses / ms) ** 2)
    from math import erf  # noqa: F401
    t975 = 2.776   # t_{0.975} at 4 dof, the smaller of the two samples
    ci_delta = [obs_ratio * (1 - t975 * rel), obs_ratio * (1 + t975 * rel)]

    ratio = {
        "PREDICTED_STATIC_VALUE": rq_s[0.8], "PREDICTED_MOBILE_VALUE": rq_m[0.8],
        "PREDICTED_MOBILE_STATIC_RATIO": pred_ratio,
        "OBSERVED_STATIC_VALUE": ms, "OBSERVED_MOBILE_VALUE": mp,
        "OBSERVED_MOBILE_STATIC_RATIO": obs_ratio,
        "UNROUNDED": True,
        "the_reported_pair_1p3443_over_1p4046": 1.3443 / 1.4046,
        "unrounded_equivalent": obs_ratio / pred_ratio,
        "relative_deviation_percent": 100 * (obs_ratio / pred_ratio - 1),
        "bootstrap_ci95_over_arms": ci,
        "delta_method_ci95_t4": ci_delta,
        "worst_case_min_P_over_max_S": float(min(pv) / max(sv)),
        "n_static_arms": len(sv), "n_mobile_arms": len(pv),
        "UNIT_OF_ANALYSIS": "the seed; one arm is one seed, frames are reduced first",
        "PREDICTED_RATIO_INSIDE_THE_BOOTSTRAP_CI":
            bool(ci[0] <= pred_ratio <= ci[1]),
        "PREDICTED_RATIO_INSIDE_THE_DELTA_CI":
            bool(ci_delta[0] <= pred_ratio <= ci_delta[1]),
        "RATIO_ONE_INSIDE_THE_BOOTSTRAP_CI": bool(ci[0] <= 1.0 <= ci[1]),
        "RATIO_ONE_INSIDE_THE_DELTA_CI": bool(ci_delta[0] <= 1.0 <= ci_delta[1]),
    }
    ratio["MOBILE_BROADENING_HYPOTHESIS"] = (
        "SUPPORTED" if not ratio["RATIO_ONE_INSIDE_THE_DELTA_CI"] else "UNRESOLVED")
    ratio["NO_MOBILE_BROADENING_RATIO_1"] = (
        "REJECTED" if not ratio["RATIO_ONE_INSIDE_THE_DELTA_CI"] else "NOT_REJECTED")
    # an interval that contains the prediction is not the same as a prediction that is exact.
    width = (ci_delta[1] - ci_delta[0]) / obs_ratio
    ratio["interval_relative_width"] = width
    ratio["EXACT_RATIO_PREDICTION"] = (
        "EQUIVALENCE_NOT_ESTABLISHED" if width > 0.10 else
        ("PASS" if ratio["PREDICTED_RATIO_INSIDE_THE_DELTA_CI"] else "FAIL"))
    ratio["WHY"] = (
        "the predicted ratio %.6f sits %s the delta-method interval, but that interval is "
        "%.1f %% wide relative to the point estimate. Containing a value inside a wide "
        "interval is not equivalence; with 3 static and 5 mobile arms the design cannot "
        "distinguish %.4f from %.4f, and saying the ratio is 'exact' would overstate what 8 "
        "arms can show." % (pred_ratio,
                            "inside" if ratio["PREDICTED_RATIO_INSIDE_THE_DELTA_CI"]
                            else "outside", 100 * width, obs_ratio, pred_ratio))

    out = {
        "SECTION": "OBFOR01 §5-§6", "CONSUMES_NO_SCIENTIFIC_RUN": True,
        "EXACT_DEFINITIONS": {
            "residual_bearing_observable": "r80_organiser",
            "source": "OBTC02/code/protocol_obtc02.py line 99, calling metrics_obtc.radii",
            "formula": ("r_q = d[ searchsorted( cumsum(w_sorted_by_d)/N , q, side='left') ], "
                        "with d the toroidal distance field centred on the ORGANISER cell and "
                        "w the X occupancy"),
            "what_it_is": ("the smallest achievable lattice distance at which the EMPIRICAL "
                           "cumulative mass of about 120 particles first reaches 0.8"),
            "three_properties": [
                "an empirical quantile, not a population quantity",
                "a FIRST CROSSING, i.e. a minimum over d, and minima of noisy crossings are "
                "biased downward",
                "supported on the discrete set of achievable toroidal distances, whose "
                "spacing near these radii is a few percent"],
            "within_seed_summary": "median over the in-window frames (step > BURN_IN)",
            "across_seed_summary": "arithmetic mean over analysable arms",
            "UNIT_OF_ANALYSIS": "SEED",
            "NORMALIZATION": "none; both prediction and observation are absolute lengths",
            "second_observable_added_here": "M2 = mean per-particle squared toroidal distance "
                                            "to the organiser, a per-particle mean and "
                                            "therefore unbiased at every N",
        },
        "PREDICTION_STATUS": prerun,
        "PREDICTED": {"static_r50_r80_r90": rq_s, "mobile_r50_r80_r90": rq_m,
                      "static_M2": m2_s, "mobile_M2": m2_m,
                      "static_rms": math.sqrt(m2_s), "mobile_rms": math.sqrt(m2_m)},
        "OBSERVED": obs,
        "RESIDUALS": RES,
        "RADIUS_VERSUS_VARIANCE": conv,
        "RATIO": ratio,
        "PER_ARM": rows,
        "OBDI02_L36_ARMS": len(mob36),
    }
    json.dump(out, open(f"{OUT}/_observables_exact.json", "w"), indent=1, default=str)

    print("EXACT OBSERVABLE   r80_organiser = radii(nX, organiser)[0.8], first crossing on the")
    print("                   discrete distance field; per-frame, median over frames, mean")
    print("                   over arms; UNIT_OF_ANALYSIS = SEED")
    print()
    print("prediction status  static %s frozen %.15g recomputed %.15g  %s"
          % ("PRE_RUN", float(frozen_static), rq_s[0.8], prerun["STATIC_REPRODUCES"]))
    print("                   mobile %s frozen %.15g recomputed %.15g  %s"
          % ("PRE_RUN", float(frozen_mobile), rq_m[0.8], prerun["MOBILE_REPRODUCES"]))
    print()
    hdr = "%-26s %5s %12s %12s %10s %8s" % ("RESIDUAL", "n", "predicted", "observed",
                                            "residual", "z")
    print(hdr)
    print("-" * len(hdr))
    for k, v in RES.items():
        if v:
            print("%-26s %5d %12.6f %12.6f %9.3f %% %8s"
                  % (k, v["n"], v["predicted"], v["observed_mean"], v["residual_percent"],
                     ("%+.2f" % v["z"]) if v["z"] is not None else "-"))
    print()
    print("RADIUS vs VARIANCE")
    print("  static : r80 %+.3f %%  -> implied variance %+.3f %%   measured M2 %+.3f %%"
          % (conv["static_r80_residual_percent"],
             conv["static_implied_variance_residual_percent"],
             conv["static_M2_residual_percent"] or float("nan")))
    print("  mobile : r80 %+.3f %%  -> implied variance %+.3f %%   measured M2 %+.3f %%"
          % (conv["mobile_r80_residual_percent"],
             conv["mobile_implied_variance_residual_percent"],
             conv["mobile_M2_residual_percent"] or float("nan")))
    print()
    print("RATIO   predicted %.6f   observed %.6f   deviation %+.3f %%"
          % (pred_ratio, obs_ratio, ratio["relative_deviation_percent"]))
    print("        bootstrap CI [%.4f, %.4f]   delta-method CI [%.4f, %.4f]  (width %.1f %%)"
          % (ci[0], ci[1], ci_delta[0], ci_delta[1], 100 * width))
    print("        prediction inside delta CI %s ; ratio 1 inside %s"
          % (ratio["PREDICTED_RATIO_INSIDE_THE_DELTA_CI"],
             ratio["RATIO_ONE_INSIDE_THE_DELTA_CI"]))
    print("        MOBILE_BROADENING_HYPOTHESIS = %s" % ratio["MOBILE_BROADENING_HYPOTHESIS"])
    print("        NO_MOBILE_BROADENING_RATIO_1 = %s" % ratio["NO_MOBILE_BROADENING_RATIO_1"])
    print("        EXACT_RATIO_PREDICTION       = %s" % ratio["EXACT_RATIO_PREDICTION"])


if __name__ == "__main__":
    main()
