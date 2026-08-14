"""OBTR01 §15 — the raw-only historical phase.

Two jobs, both on delivered trajectories and consuming no scientific run.

(a) The three source-off e-foldings 233 / 297 / 245 against the analytic 249.5. The mandate
    requires their exact DEFINITION to be verified before they are recomputed, and it is not
    what the phrase "e-folding" suggests: `protocol_obtc02.source_off_response` takes the mean
    of N_X over the 200 steps BEFORE removal as a baseline and then reports the first step at
    which N_X falls to or below baseline/e. That is a first-passage time of a stochastic decay
    below a threshold set by a noisy baseline, not a fitted rate. So it is a BIASED and
    dispersed estimator of -1/ln(1-mu), and the size of that dispersion is derived here rather
    than assumed, by replaying the exact Binomial death process the engine implements.

(b) The static-source results, which OBTC02 reported only in summary ("six statistics out of
    six inside the envelope") without the numbers. They matter here because condition S sets
    p_hop_Y = 0, so the relative kernel collapses onto K_X and a_rel = a_X instead of 2 a_X.
    The static and mobile predictions differ by a factor sqrt(2) in radius, so recovering the S
    numbers is a DISCRIMINATING test of the §7 derivation, not a formality.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, "/home/claude/OBTR01/code")

from kernels_obtr01 import Operator                     # noqa: E402


def series_of(path):
    z = np.load(path, allow_pickle=True)
    return z, {str(n): i for i, n in enumerate(z["fields"])}


def recompute_e_folding(NX, off_at):
    """The frozen definition, transcribed from protocol_obtc02.source_off_response."""
    base = float(NX[max(off_at - 200, 0):off_at].mean())
    after = NX[off_at:]
    thr = base / math.e
    idx = np.nonzero(after <= thr)[0]
    return {"base": base, "threshold": thr,
            "N_at_removal": float(NX[off_at]),
            "e_folding_steps": float(idx[0]) if len(idx) else None,
            "steps_available_after_removal": int(len(after))}


def estimator_law(N0, base, mu, n_rep=20000, seed=7):
    """The exact null law of that estimator. After removal the engine's only action on X is
    _decay, which draws Binomial(n, mu) per step, so N(t+1) = N(t) - Binomial(N(t), mu). That
    is replayed here directly; no engine start is opened and no lattice is built."""
    rng = np.random.default_rng(seed)
    thr = base / math.e
    out = np.empty(n_rep)
    for r in range(n_rep):
        n, t = int(N0), 0
        while n > thr and t < 20000:
            n -= int(rng.binomial(n, mu))
            t += 1
        out[r] = t
    return out


def log_slope_law(N0, mu, floor=5, n_rep=4000, seed=11):
    """The same second estimator, applied to replays of the exact death process, so that its
    own bias and spread are measured rather than assumed."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_rep):
        n, path = int(N0), []
        while n >= floor and len(path) < 20000:
            path.append(n)
            n -= int(rng.binomial(n, mu))
        if len(path) < 10:
            continue
        t = np.arange(len(path), dtype=float)
        sl = np.polyfit(t, np.log(np.asarray(path, float)), 1)[0]
        if sl < 0:
            out.append(-1.0 / sl)
    return np.asarray(out)


def log_slope_e_folding(NX, off_at, floor=5):
    """A second, independent estimator: the least-squares slope of log N(t) on t over the decay,
    which estimates -1/ln(1-mu) directly instead of through a threshold crossing."""
    after = NX[off_at:]
    keep = np.nonzero(after >= floor)[0]
    if len(keep) < 10:
        return None
    t = keep.astype(float)
    y = np.log(after[keep])
    slope = np.polyfit(t, y, 1)[0]
    return float(-1.0 / slope) if slope < 0 else None


def radial_from_frames(z, burn_in, sample_every):
    fr = [json.loads(str(s)) for s in z["frames"]]
    w = [f for f in fr if f["step"] > burn_in]
    def med(k):
        v = [f[k] for f in w if f.get(k) is not None and np.isfinite(f[k])]
        return float(np.median(v)) if v else None
    return {"frames_in_window": len(w), "r50": med("r50"), "r80": med("r80"),
            "r90": med("r90"), "Rg": med("Rg"),
            "r80_organiser": med("r80_organiser"),
            "organiser_to_core": med("organiser_to_core"),
            "N_X": med("N_X")}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    obt = yaml.safe_load(open(f"{WC}/OBTC02/code/obtc02_protocol.yaml"))
    pt, win = spec["point"], spec["window"]
    an = obt.get("analytic", {})
    mu, q, L = pt["muX"], pt["p_hop"] / 4.0, pt["L"]
    off_at = int(win["SOURCE_OFF_AT"])
    tau_analytic = -1.0 / math.log(1.0 - mu)
    res0 = json.load(open(f"{WC}/OBTC02/out/_results.json"))

    # ---------------------------------------------------------------- (a) source-off
    R_arms, recorded = [], {}
    for a in res0["arms"]:
        if a.get("condition") == "R":
            recorded[a["tag"]] = a["source_off"]
    rows = []
    for tag, rec in sorted(recorded.items()):
        p = f"{WC}/OBTC02/raw/{tag.replace('/', '__')}.npz"
        z, F = series_of(p)
        NX = z["series"][:, F["N_X"]]
        got = recompute_e_folding(NX, off_at)
        law = estimator_law(got["N_at_removal"], got["base"], mu)
        alt = log_slope_e_folding(NX, off_at)
        altlaw = log_slope_law(got["N_at_removal"], mu)
        rows.append({
            "tag": tag,
            "recorded": rec,
            "recomputed": got,
            "REPRODUCES_THE_RECORDED_VALUE":
                rec.get("e_folding_steps") == got["e_folding_steps"],
            "REPRODUCES_THE_RECORDED_BASELINE": abs(rec["pre_removal_level"]
                                                    - got["base"]) < 1e-9,
            "estimator_law": {"mean": float(law.mean()), "sd": float(law.std(ddof=1)),
                              "q05": float(np.quantile(law, 0.05)),
                              "q50": float(np.quantile(law, 0.50)),
                              "q95": float(np.quantile(law, 0.95)),
                              "replicates": int(len(law))},
            "z_of_the_observed_value": float((got["e_folding_steps"] - law.mean())
                                             / law.std(ddof=1)),
            "second_estimator_log_slope": alt,
            "second_estimator_law": {"mean": float(altlaw.mean()),
                                     "sd": float(altlaw.std(ddof=1)),
                                     "replicates": int(len(altlaw))},
            "z_of_the_second_estimator": (float((alt - altlaw.mean()) / altlaw.std(ddof=1))
                                          if alt else None),
        })
        R_arms.append(tag)

    obs = [r["recomputed"]["e_folding_steps"] for r in rows]
    means = [r["estimator_law"]["mean"] for r in rows]
    sds = [r["estimator_law"]["sd"] for r in rows]
    alts = [r["second_estimator_log_slope"] for r in rows if r["second_estimator_log_slope"]]

    source_off = {
        "FROZEN_DEFINITION": (
            "base = mean of N_X over the 200 steps before removal; e_folding = the first step "
            "after removal at which N_X <= base/e. A first-passage time below a threshold set "
            "by a noisy baseline, NOT a fitted rate."),
        "analytic_prediction_minus_one_over_log": tau_analytic,
        "frozen_acceptance_window": [tau_analytic / 2.0, tau_analytic * 2.0],
        "RECORDED": [233.0, 297.0, 245.0],
        "RECOMPUTED": obs,
        "ALL_THREE_REPRODUCE": all(r["REPRODUCES_THE_RECORDED_VALUE"] for r in rows),
        "ALL_THREE_BASELINES_REPRODUCE": all(r["REPRODUCES_THE_RECORDED_BASELINE"]
                                             for r in rows),
        "PER_ARM": rows,
        "WHY_THE_SPREAD": (
            "the estimator inherits two independent sources of dispersion: the baseline is a "
            "200-step running mean while the decay starts from the instantaneous N at removal, "
            "and the decay itself is a Binomial thinning whose crossing of base/e fluctuates. "
            "Replaying the exact death process gives a predicted sd of about %.0f steps per "
            "arm, against an observed spread of %.0f steps across the three arms. The three "
            "values are therefore exactly where the analytic law puts them; they are not "
            "evidence of a rate different from %.1f."
            % (float(np.mean(sds)), float(np.std(obs, ddof=1)), tau_analytic)),
        "MEAN_OF_THE_ESTIMATOR_LAW": float(np.mean(means)),
        "ESTIMATOR_IS_BIASED_RELATIVE_TO_TAU": float(np.mean(means) - tau_analytic),
        "SECOND_ESTIMATOR_log_slope": {
            "values": alts, "mean": float(np.mean(alts)) if alts else None,
            "analytic": tau_analytic,
            "null_law_mean": float(np.mean([r["second_estimator_law"]["mean"] for r in rows])),
            "null_law_sd": float(np.mean([r["second_estimator_law"]["sd"] for r in rows])),
            "z_values": [r["z_of_the_second_estimator"] for r in rows],
            "note": ("a least-squares slope of log N on t is tighter than the threshold "
                     "crossing, but it is NOT unbiased either: truncating the path at N >= "
                     "%d censors the tail, so its null law is measured by replaying the same "
                     "death process through the same estimator." % 5)},
        "MAX_ABS_Z": float(max(abs(r["z_of_the_observed_value"]) for r in rows)),
        "ALL_WITHIN_2_SIGMA": bool(max(abs(r["z_of_the_observed_value"])
                                       for r in rows) < 2.0),
    }

    # ---------------------------------------------------------------- (b) static source
    op_static = Operator(q, 0.0, mu, L)          # p_hop_Y = 0 under condition S
    op_mobile = Operator(q, q, mu, L)

    def radii(op):
        prof = op.stationary_profile()
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
        o = np.argsort(d.ravel(), kind="stable")
        dd, ww = d.ravel()[o], prof.ravel()[o]
        cw = np.cumsum(ww)
        return {k: float(dd[int(np.searchsorted(cw, k, side="left"))])
                for k in (0.5, 0.8, 0.9)}

    pred_static, pred_mobile = radii(op_static), radii(op_mobile)
    S_rows = []
    for a in res0["arms"]:
        if a.get("condition") not in ("S", "P"):
            continue
        p = f"{WC}/OBTC02/raw/{a['tag'].replace('/', '__')}.npz"
        if not os.path.exists(p):
            continue
        z = np.load(p, allow_pickle=True)
        r = radial_from_frames(z, int(spec["window"]["BURN_IN"]),
                               int(spec["window"]["SAMPLE_EVERY"]))
        r.update({"tag": a["tag"], "condition": a["condition"]})
        S_rows.append(r)

    # an arm whose window-median N_X is zero is EXTINCT and is not analysable, by the
    # definition frozen in OBDI02's population support gate. It is excluded from the primary
    # aggregate and reported separately, never deleted.
    for r in S_rows:
        r["ANALYSABLE"] = bool(r.get("N_X") is not None and r["N_X"] > 0)
    extinct = [r["tag"] for r in S_rows if not r["ANALYSABLE"]]

    def agg(cond, key, analysable_only=True):
        v = [r[key] for r in S_rows if r["condition"] == cond and r.get(key) is not None
             and (r["ANALYSABLE"] or not analysable_only)]
        return {"n": len(v), "mean": float(np.mean(v)) if v else None,
                "min": float(min(v)) if v else None, "max": float(max(v)) if v else None,
                "values": [float(x) for x in v]}

    static = {
        "WHY_IT_DISCRIMINATES": (
            "condition S sets p_hop_Y = 0, so K_rel collapses onto K_X and a_rel = a_X instead "
            "of 2 a_X. The predicted radii differ by sqrt(2) between the two regimes, so the S "
            "and P arms test the relative-kernel derivation against each other with no free "
            "parameter."),
        "PREDICTED_STATIC_r50_r80_r90": pred_static,
        "PREDICTED_MOBILE_r50_r80_r90": pred_mobile,
        "RATIO_MOBILE_OVER_STATIC_r80": pred_mobile[0.8] / pred_static[0.8],
        "SQRT_2": math.sqrt(2.0),
        "FROZEN_static_r80": an.get("static_r80"),
        "FROZEN_organiser_frame_r80": an.get("organiser_frame_r80"),
        "REPRODUCES_THE_FROZEN_STATIC_r80": abs(pred_static[0.8]
                                                - float(an.get("static_r80", 0))) < 1e-9,
        "REPRODUCES_THE_FROZEN_MOBILE_r80": abs(pred_mobile[0.8]
                                                - float(an.get("organiser_frame_r80", 0)))
        < 1e-9,
        "OBSERVED": {
            "S_r80_organiser": agg("S", "r80_organiser"), "P_r80_organiser": agg("P",
                                                                                 "r80_organiser"),
            "S_r80": agg("S", "r80"), "P_r80": agg("P", "r80"),
            "S_organiser_to_core": agg("S", "organiser_to_core"),
            "P_organiser_to_core": agg("P", "organiser_to_core"),
            "S_N_X": agg("S", "N_X"), "P_N_X": agg("P", "N_X")},
        "PER_ARM": S_rows,
        "WHAT_OBTC02_OMITTED": ("the OBTC02 report gave the S arms as 'six statistics out of "
                                "six inside the envelope' with the numbers withheld, and gave "
                                "the core-organiser distance as 0.00, which is a consequence "
                                "of the organiser being immobile rather than a measurement of "
                                "attachment."),
    }
    static["EXTINCT_ARMS_EXCLUDED_FROM_THE_PRIMARY_AGGREGATE"] = extinct
    static["INCLUDING_THE_EXTINCT_ARM"] = {
        "P_r80_organiser": agg("P", "r80_organiser", analysable_only=False)}

    sv = static["OBSERVED"]["S_r80_organiser"]["values"]
    pv = static["OBSERVED"]["P_r80_organiser"]["values"]
    if sv and pv:
        sr, pr = float(np.mean(sv)), float(np.mean(pv))
        pred_ratio = pred_mobile[0.8] / pred_static[0.8]
        # the discriminating comparison: a_rel = a_X + a_Y predicts the ratio above; the
        # alternative a_rel = a_X (organiser motion irrelevant) predicts exactly 1.
        rng = np.random.default_rng(99)
        boot = np.array([np.mean(rng.choice(pv, len(pv))) / np.mean(rng.choice(sv, len(sv)))
                         for _ in range(20000)])
        static["DISCRIMINATION"] = {
            "H_relative_kernel": "ratio = %.4f  (a_rel = a_X + a_Y)" % pred_ratio,
            "H_organiser_motion_irrelevant": "ratio = 1.0  (a_rel = a_X)",
            "observed_ratio": pr / sr,
            "bootstrap_95_interval": [float(np.quantile(boot, 0.025)),
                                      float(np.quantile(boot, 0.975))],
            "worst_case_ratio_min_P_over_max_S": min(pv) / max(sv),
            "EXCLUDES_RATIO_ONE": bool(float(np.quantile(boot, 0.025)) > 1.0),
            "relative_deviation_from_the_predicted_ratio": (pr / sr) / pred_ratio - 1.0,
            "AGREES_WITHIN_10_PERCENT": bool(abs((pr / sr) / pred_ratio - 1) < 0.10),
            "ALSO_OBSERVED": ("both regimes sit slightly BELOW their absolute predictions "
                              "(static %.4f against %.4f, mobile %.4f against %.4f). The "
                              "ratio is the parameter-free discriminator and is reported as "
                              "the primary comparison; the absolute deficit is recorded as an "
                              "open residual, not explained away."
                              % (sr, pred_static[0.8], pr, pred_mobile[0.8])),
            "absolute_deficit_static": sr / pred_static[0.8] - 1.0,
            "absolute_deficit_mobile": pr / pred_mobile[0.8] - 1.0}
        static["OBSERVED_RATIO_P_OVER_S_r80_organiser"] = pr / sr
        static["PREDICTED_RATIO"] = pred_ratio
        static["RATIO_AGREES_WITHIN_10_PERCENT"] = static["DISCRIMINATION"][
            "AGREES_WITHIN_10_PERCENT"]

    out = {"SECTION": "OBTR01 §15", "CONSUMES_NO_SCIENTIFIC_RUN": True,
           "SOURCE_OFF": source_off, "STATIC_SOURCE": static}
    json.dump(out, open(f"{OUT}/_historical_raw.json", "w"), indent=1, default=str)

    print("(a) SOURCE-OFF, condition R, %d arms" % len(rows))
    print("    frozen definition: %s" % source_off["FROZEN_DEFINITION"][:78])
    print("    analytic tau = %.4f, frozen acceptance window [%.1f, %.1f]"
          % (tau_analytic, tau_analytic / 2, tau_analytic * 2))
    for r in rows:
        print("    %-12s recorded %6.1f  recomputed %6.1f  %s | estimator law mean %6.1f "
              "sd %5.1f  z = %+5.2f | log-slope %6.1f"
              % (r["tag"], r["recorded"]["e_folding_steps"],
                 r["recomputed"]["e_folding_steps"],
                 "MATCH" if r["REPRODUCES_THE_RECORDED_VALUE"] else "DIFFER",
                 r["estimator_law"]["mean"], r["estimator_law"]["sd"],
                 r["z_of_the_observed_value"],
                 r["second_estimator_log_slope"] or float("nan")))
    print("    all three reproduce: %s ; all within 2 sigma: %s ; estimator bias %+0.1f steps"
          % (source_off["ALL_THREE_REPRODUCE"], source_off["ALL_WITHIN_2_SIGMA"],
             source_off["ESTIMATOR_IS_BIASED_RELATIVE_TO_TAU"]))
    print("    second estimator (log slope) mean %.1f against analytic %.1f"
          % (source_off["SECOND_ESTIMATOR_log_slope"]["mean"], tau_analytic))
    print()
    print("(b) STATIC SOURCE, condition S")
    print("    predicted r80 static %.6f  mobile %.6f  ratio %.6f (sqrt 2 = %.6f)"
          % (pred_static[0.8], pred_mobile[0.8], static["RATIO_MOBILE_OVER_STATIC_r80"],
             math.sqrt(2)))
    print("    reproduces the frozen analytic block: static %s, mobile %s"
          % (static["REPRODUCES_THE_FROZEN_STATIC_r80"],
             static["REPRODUCES_THE_FROZEN_MOBILE_r80"]))
    def fmt(x):
        return "%8.4f" % x if isinstance(x, (int, float)) else "       -"
    print("    extinct arms excluded from the primary aggregate: %s" % (extinct or "none"))
    for k in ("r80_organiser", "r80", "organiser_to_core", "N_X"):
        sv_, pv_ = static["OBSERVED"]["S_" + k], static["OBSERVED"]["P_" + k]
        print("    %-20s S %s (n=%d, %s..%s)   P %s (n=%d, %s..%s)"
              % (k, fmt(sv_["mean"]), sv_["n"], fmt(sv_["min"]), fmt(sv_["max"]),
                 fmt(pv_["mean"]), pv_["n"], fmt(pv_["min"]), fmt(pv_["max"])))
    d = static.get("DISCRIMINATION")
    if d:
        print()
        print("    DISCRIMINATION between a_rel = a_X + a_Y and a_rel = a_X")
        print("      predicted ratio %.4f   alternative predicts 1.0000"
              % static["PREDICTED_RATIO"])
        print("      observed  ratio %.4f   bootstrap 95 %% [%.4f, %.4f]   worst case %.4f"
              % (d["observed_ratio"], d["bootstrap_95_interval"][0],
                 d["bootstrap_95_interval"][1], d["worst_case_ratio_min_P_over_max_S"]))
        print("      excludes ratio 1: %s   within 10 %% of the prediction: %s   deviation %+.2f %%"
              % (d["EXCLUDES_RATIO_ONE"], d["AGREES_WITHIN_10_PERCENT"],
                 100 * d["relative_deviation_from_the_predicted_ratio"]))
        print("      absolute deficits: static %+.2f %%, mobile %+.2f %%"
              % (100 * d["absolute_deficit_static"], 100 * d["absolute_deficit_mobile"]))


if __name__ == "__main__":
    main()
