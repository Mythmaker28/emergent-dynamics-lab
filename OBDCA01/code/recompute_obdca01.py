"""OBDCA01 §6-§7 — exact reconstruction of the primary outcome, and its recomputation by TWO
independent routes.

ROUTE 1 : the frozen gate itself, `gate_obdi02.evaluate_primary`, re-executed on the delivered
          per-arm records.
ROUTE 2 : a second implementation written here from the RAW .npz frames, sharing no accumulator,
          no helper and no intermediate file with route 1. It re-derives the per-frame |C - Y|
          from the recorded frame fields, re-forms the per-seed median, re-takes the logarithm,
          re-fits the weighted slope and re-builds the interval.

A disagreement between the two routes is a defect detector. Agreement is not proof of
correctness, but disagreement would be proof of a problem.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBDCA01/verify/obdi02/wc"
OUT = "/home/claude/OBDCA01/out"
sys.path.insert(0, f"{WC}/OBDI02/code")
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")

SIZES = (36, 72, 96)


# ------------------------------------------------------------------ route 2 primitives
def wdist1(d, L):
    d = np.abs(np.asarray(d, float)) % L
    return np.minimum(d, L - d)


def z_one_sided(a):
    lo, hi = 0.0, 12.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        if 1.0 - 0.5 * (1.0 + math.erf(m / math.sqrt(2.0))) > a:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def norm_sf(x):
    return 1.0 - 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def slope_route2(x, y, w):
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    xb = float((w * x).sum() / w.sum())
    sxx = float((w * (x - xb) ** 2).sum())
    return float((w * (x - xb) * y).sum() / sxx), float(sxx ** -0.5)


def read_arm(tag):
    """Route 2 reads the RAW archive, not the per-arm json."""
    z = np.load("%s/OBDI02/raw/%s.npz" % (WC, tag.replace("/", "__")), allow_pickle=True)
    fr = [json.loads(s) for s in z["frames"]]
    return fr, z


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    R = json.load(open(f"{WC}/OBDI02/out/_results.json"))
    A = json.load(open(f"{WC}/OBDI02/out/_arms.json"))
    burn = int(spec["window"]["BURN_IN"])
    pe = spec["primary_endpoint"]
    delta_primary = float(pe["equivalence_margin"])
    delta_strict = float(pe["stringent_reference_margin"])
    alpha = float(pe["tost_alpha_one_sided"])
    c = z_one_sided(alpha)
    pred = {L: float(spec["predictions"][str(L)]["organiser_to_core"]) for L in SIZES}

    # ---------------------------------------------------------------- §6 the estimand
    estimand = {
        "PRIMARY_ESTIMAND": ("beta_CY = d log d_CY / d log L, with "
                             "d_CY(L) = median_{frames in window} |C - Y|  /  pred(L), where "
                             "pred(L) is the operator's exact finite-size prediction of "
                             "|C - Y| at that L"),
        "C": ("toroidal Frechet centre of the X field: the separable exact minimiser of the sum "
              "of squared toroidal distances, computed axis by axis, on a lattice site "
              "(metrics_obtc.frechet_centre)"),
        "Y": "the unique cell with n_Y > 0 (one organiser), read from the same frame",
        "TORIC_DISTANCE": "hypot(wdist1(dy, L), wdist1(dx, L)), wdist1(d,L)=min(d%L, L-d%L)",
        "PER_FRAME_SUMMARY": "|C - Y| of that frame, field name organiser_to_core",
        "INDEPENDENT_UNIT": "SEED",
        "WITHIN_SEED_SUMMARY": pe["within_seed_summary"],
        "LOG_TRANSFORM": "y_L = mean over analysable arms of log(summary) - log(pred(L))",
        "REGRESSION": pe["estimator"],
        "EXTINCTION_TREATMENT": spec["population_support_gate"]["seed_policy"],
        "LOW_POPULATION_TREATMENT": ("NONE. The frozen definition of an analysable arm is only "
                                     "'finite and strictly positive summary'. No population "
                                     "floor exists in the freeze."),
        "INTERVAL_METHOD": pe["method"],
        "BINDING_CONFIDENCE_LEVEL": pe["two_sided_interval_level"],
        "EQUIVALENCE_TEST": "TOST in confidence-interval form",
        "AGGREGATED_RULE": pe["decision_rule"],
        "BINDING_EQUIVALENCE_MARGIN": delta_primary,
        "SECONDARY_PRECISION_TARGET": delta_strict,
        "window_frames_expected": (int(spec["window"]["HORIZON"]) - burn)
        // int(spec["window"]["SAMPLE_EVERY"]),
    }

    # ---------------------------------------------------------------- route 2 from raw
    per_arm = []
    for a in A:
        tag, L = a["tag"], int(a["L"])
        fr, z = read_arm(tag)
        win = [f for f in fr if f["step"] > burn]
        # recompute |C-Y| from the recorded centre and organiser positions, not from the field
        d = []
        for f in win:
            if f["centre_y"] < 0 or f["organiser_y"] < 0:
                continue
            dy = wdist1(f["centre_y"] - f["organiser_y"], L)
            dx = wdist1(f["centre_x"] - f["organiser_x"], L)
            d.append(float(np.hypot(dy, dx)))
        d = np.array(d, float)
        recorded = np.array([f.get("organiser_to_core", np.nan) for f in win], float)
        agree = bool(len(d) == np.isfinite(recorded).sum()
                     and np.allclose(np.sort(d), np.sort(recorded[np.isfinite(recorded)]),
                                     atol=1e-9))
        nx = np.array([f["N_X"] for f in win], float)
        per_arm.append({
            "tag": tag, "L": L, "seed": a["seed"], "n_window_frames": len(win),
            "n_frames_with_a_centre": int(len(d)),
            "route2_recomputes_the_recorded_distance": agree,
            "summary_CY_route2": float(np.median(d)) if len(d) else float("nan"),
            "summary_CY_frozen": a["summary"]["organiser_to_core"],
            "N_X_mean": a["summary"]["N_X_mean"], "N_X_median": float(np.median(nx)),
            "N_X_min": float(nx.min()) if len(nx) else float("nan"),
            "frac_window_below_20": float(np.mean(nx < 20)) if len(nx) else float("nan"),
            "frac_window_below_50": float(np.mean(nx < 50)) if len(nx) else float("nan"),
            "Rg": a["summary"]["Rg"], "r80": a["summary"]["r80"],
            "density": a["summary"]["density"],
            "profile_TV": a["profile_TV"], "winding_frames": a["winding_frames"],
            "RUN_TECHNICALLY_VALID": a["RUN_TECHNICALLY_VALID"],
            "GATES_AGREE": a["GATES_AGREE"],
            "classification": a["classification"],
            "LEGACY_RELATIVE_LOCALIZATION": a["LEGACY_RELATIVE_LOCALIZATION"],
            "EXTINCT": a["EXTINCT"],
        })
    same = [p for p in per_arm if np.isfinite(p["summary_CY_route2"])
            and np.isfinite(p["summary_CY_frozen"])
            and abs(p["summary_CY_route2"] - p["summary_CY_frozen"]) < 1e-9]
    both_nan = [p for p in per_arm if not np.isfinite(p["summary_CY_route2"])
                and not np.isfinite(p["summary_CY_frozen"])]

    def fit(vals_by_L, predmap):
        x, y, w, det = [], [], [], {}
        for L in SIZES:
            v = np.array([q for q in vals_by_L[L] if np.isfinite(q) and q > 0], float)
            if len(v) < 2:
                continue
            lv = np.log(v)
            x.append(math.log(L))
            y.append(float(lv.mean()) - math.log(predmap[L]))
            w.append(len(v) / max(float(lv.std(ddof=1)), 1e-12) ** 2)
            det[str(L)] = {"n": len(v), "mean": float(v.mean()), "mean_of_log": float(lv.mean()),
                           "sd_of_log": float(lv.std(ddof=1)),
                           "se_of_log_mean": float(lv.std(ddof=1) / math.sqrt(len(v))),
                           "predicted": predmap[L],
                           "relative_deviation": float(math.exp(lv.mean()) / predmap[L] - 1)}
        b, se = slope_route2(x, y, w)
        return b, se, det

    by_L2 = {L: [p["summary_CY_route2"] for p in per_arm if p["L"] == L] for L in SIZES}
    b2, se2, det2 = fit(by_L2, pred)

    # ---------------------------------------------------------------- route 1: frozen gate
    import gate_obdi02 as GT
    os.environ.setdefault("PYTHONHASHSEED", "0")
    GT.SPEC_PATH = f"{WC}/OBDI02/code/obdi02_protocol.yaml"
    by_L1 = {L: {"summary_CY": [a["summary"]["organiser_to_core"] for a in A if a["L"] == L],
                 "summary_Rg": [a["summary"]["Rg"] for a in A if a["L"] == L],
                 "summary_r80": [a["summary"]["r80"] for a in A if a["L"] == L],
                 "density": [a["summary"]["density"] for a in A if a["L"] == L]}
             for L in SIZES}
    spec1 = GT.load(GT.SPEC_PATH)
    prim1 = GT.evaluate_primary(spec1, by_L1)

    agree_routes = {
        "beta": {"route1": prim1["beta"], "route2": b2, "abs_diff": abs(prim1["beta"] - b2)},
        "se": {"route1": prim1["se"], "route2": se2, "abs_diff": abs(prim1["se"] - se2)},
        "AGREE": bool(abs(prim1["beta"] - b2) < 1e-9 and abs(prim1["se"] - se2) < 1e-9),
        "per_arm_summaries_identical": len(same) + len(both_nan) == len(per_arm),
        "n_arms_identical": len(same), "n_arms_both_undefined": len(both_nan),
        "route2_recomputed_every_recorded_distance":
            all(p["route2_recomputes_the_recorded_distance"] for p in per_arm),
    }

    # ---------------------------------------------------------------- §7 the two TOSTs
    def tost(b, se, delta):
        t_lo = (b + delta) / se          # H0: beta <= -delta
        t_hi = (delta - b) / se          # H0: beta >= +delta
        p_lo, p_hi = norm_sf(t_lo), norm_sf(t_hi)
        return {"margin": delta,
                "lower_one_sided": {"statistic": t_lo, "p_value": p_lo},
                "upper_one_sided": {"statistic": t_hi, "p_value": p_hi},
                "tost_p_value": max(p_lo, p_hi),
                "interval": [b - c * se, b + c * se],
                "interval_inside_margin": bool(b - c * se > -delta and b + c * se < delta),
                "achieved_bound": abs(b) + c * se,
                "PASS": bool(max(p_lo, p_hi) < alpha)}

    t25, t042 = tost(b2, se2, delta_primary), tost(b2, se2, delta_strict)
    # the interval OBDI01 would have used, for contrast only
    c_obdi01 = 2.799625219301098
    historical = {"critical_value": c_obdi01,
                  "interval": [b2 - c_obdi01 * se2, b2 + c_obdi01 * se2],
                  "achieved_bound": abs(b2) + c_obdi01 * se2,
                  "PASS_at_0.25": bool(abs(b2) + c_obdi01 * se2 <= delta_primary),
                  "PASS_at_0.042": bool(abs(b2) + c_obdi01 * se2 <= delta_strict),
                  "note": "the 99.49 % interval OBDI01 used, applied to the OBDI02 data for "
                          "contrast only; it is not the frozen OBDI02 rule"}

    ratio = 96.0 / 36.0
    effect = {
        "range": "L = 36 -> 96, a factor %.4f" % ratio,
        "point_estimate": ratio ** b2,
        "interval_low": ratio ** t25["interval"][0],
        "interval_high": ratio ** t25["interval"][1],
        "margin_0.25": ratio ** delta_primary,
        "target_0.042": ratio ** delta_strict,
        "reading": ("the frozen margin 0.25 admits growth up to a factor %.3f over the tested "
                    "range; the secondary target 0.042 admits %.3f; the observed point estimate "
                    "is %.3f and its 90 %% interval runs from %.3f to %.3f"
                    % (ratio ** delta_primary, ratio ** delta_strict, ratio ** b2,
                       ratio ** t25["interval"][0], ratio ** t25["interval"][1]))}

    # ---------------------------------------------------------------- secondary endpoints
    sec = {}
    for stat, key in (("Rg", "Rg"), ("r80", "r80")):
        pm = {L: float(spec["predictions"][str(L)][key]) for L in SIZES}
        v = {L: [p[stat] for p in per_arm if p["L"] == L] for L in SIZES}
        b, se, det = fit(v, pm)
        sec["scaling_" + stat] = {"beta": b, "se": se, "interval": [b - c * se, b + c * se],
                                  "achieved_bound": abs(b) + c * se,
                                  "effect_over_the_range": ratio ** b, "per_L": det,
                                  "TOST_at_0.25": tost(b, se, delta_primary)["PASS"],
                                  "TOST_at_0.042": tost(b, se, delta_strict)["PASS"]}
    x, y, w, det = [], [], [], {}
    for L in SIZES:
        v = np.array([p["density"] for p in per_arm if p["L"] == L and p["density"] > 0], float)
        lv = np.log(v)
        x.append(math.log(L)); y.append(float(lv.mean()))
        w.append(len(v) / max(float(lv.std(ddof=1)), 1e-12) ** 2)
        det[str(L)] = {"n": len(v), "mean_density": float(v.mean()),
                       "mean_N_X": float(v.mean()) * L * L}
    g, seg = slope_route2(x, y, w)
    sec["density_exponent"] = {"gamma": g, "se": seg, "interval": [g - c * seg, g + c * seg],
                               "H_bound": -2.0, "per_L": det,
                               "deviation_from_minus_2": abs(g + 2.0)}
    sec["true_winding"] = {str(L): {"frames_with_winding":
                                    int(sum(p["winding_frames"] for p in per_arm if p["L"] == L)),
                                    "frames": int(sum(p["n_window_frames"] for p in per_arm
                                                      if p["L"] == L))} for L in SIZES}
    thr = {L: float(spec["profile_envelope"][str(L)]["quantile_value"]) for L in SIZES}
    sec["radial_profile"] = {
        str(L): {"threshold": thr[L],
                 "PASSING_ARMS": int(sum(1 for p in per_arm if p["L"] == L
                                         and np.isfinite(p["profile_TV"])
                                         and p["profile_TV"] <= thr[L])),
                 "TOTAL_ARMS": int(sum(1 for p in per_arm if p["L"] == L)),
                 "REQUIRED_PASSING_ARMS": int(math.ceil(0.8 * sum(1 for p in per_arm
                                                                  if p["L"] == L)))}
        for L in SIZES}
    n_plan = int(spec["domain"]["SEEDS_PER_SIZE"])
    need = int(math.ceil(float(spec["population_support_gate"]["fraction_required"]) * n_plan))
    sec["population_support"] = {
        str(L): {"analysable": int(sum(1 for p in per_arm if p["L"] == L
                                       and np.isfinite(p["summary_CY_route2"]))),
                 "arms_run": int(sum(1 for p in per_arm if p["L"] == L)),
                 "required": need} for L in SIZES}
    sec["legacy_D_gate"] = {
        str(L): {"PASSING_ARMS": int(sum(1 for p in per_arm if p["L"] == L
                                         and p["LEGACY_RELATIVE_LOCALIZATION"])),
                 "TOTAL_ARMS": int(sum(1 for p in per_arm if p["L"] == L))} for L in SIZES}

    out = {"SECTION": "OBDCA01 §6-§7", "ESTIMAND": estimand,
           "ROUTE_AGREEMENT": agree_routes,
           "BETA_CY": {"beta": b2, "se": se2, "per_L": det2,
                       "critical_value_c": c, "alpha_one_sided": alpha},
           "TOST_AT_0P25": t25, "TOST_AT_0P042": t042,
           "HISTORICAL_INTERVAL_FOR_CONTRAST": historical,
           "EFFECT_SIZE_OVER_THE_RANGE": effect,
           "SECONDARY": sec,
           "PER_ARM": per_arm}
    json.dump(out, open(f"{OUT}/_recompute.json", "w"), indent=1, default=str)

    print("ROUTE AGREEMENT")
    print("   beta   route1 %+.8f  route2 %+.8f  diff %.2e" % (prim1["beta"], b2,
                                                               abs(prim1["beta"] - b2)))
    print("   se     route1 %.8f  route2 %.8f  diff %.2e" % (prim1["se"], se2,
                                                             abs(prim1["se"] - se2)))
    print("   per-arm summaries identical on %d arms, both undefined on %d, total %d"
          % (len(same), len(both_nan), len(per_arm)))
    print("   route 2 reproduced every recorded |C-Y| from centre and organiser positions:",
          agree_routes["route2_recomputed_every_recorded_distance"])
    print("\nbeta_CY = %+.5f  se = %.5f   c = %.5f (alpha = %.2f one-sided)" % (b2, se2, c, alpha))
    for name, t in (("TOST at 0.25 ", t25), ("TOST at 0.042", t042)):
        print("%s  interval [%+.5f, %+.5f]  p_lo=%.3e p_hi=%.3e  tost p=%.3e  -> %s"
              % (name, t["interval"][0], t["interval"][1],
                 t["lower_one_sided"]["p_value"], t["upper_one_sided"]["p_value"],
                 t["tost_p_value"], "PASS" if t["PASS"] else "FAIL"))
    print("\neffect over L=36->96 : x%.4f   [x%.4f, x%.4f]   margin 0.25 allows x%.4f, "
          "target 0.042 allows x%.4f"
          % (effect["point_estimate"], effect["interval_low"], effect["interval_high"],
             effect["margin_0.25"], effect["target_0.042"]))
    print("\nsecondary: Rg beta=%+.5f se=%.5f | r80 beta=%+.5f se=%.5f | gamma=%+.5f se=%.5f"
          % (sec["scaling_Rg"]["beta"], sec["scaling_Rg"]["se"], sec["scaling_r80"]["beta"],
             sec["scaling_r80"]["se"], sec["density_exponent"]["gamma"],
             sec["density_exponent"]["se"]))


if __name__ == "__main__":
    main()
