"""SEAL §3-§4 — the information-flow audit of the predictions, and an independent
recomputation of every load-bearing number.

The prediction pipeline is traced by reading the frozen code, not by trusting its docstring.
Every headline figure is recomputed from the committed raw evidence.
"""
from __future__ import annotations

import ast
import json
import math
import os
import subprocess
import sys

import numpy as np

V = "/home/claude/SEAL01/verify/wc"
OUT = "/home/claude/SEAL01/out"
sys.path.insert(0, f"{V}/OBTR01/code")
sys.path.insert(0, f"{V}/OBTC02/code")
sys.path.insert(0, f"{V}/ORR01/code")

from kernels_obtr01 import Operator                      # noqa: E402
import metrics_obtc as M                                 # noqa: E402

RADIAL_GRID = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0, 17.0)
BURN_IN, HORIZON = 2000, 11000

# Monte-Carlo standard deviation of the M6 POINT PREDICTIONS themselves, measured in the
# repair round over 16 independent replicates of the frozen 30-arm design. Every frozen
# prediction must be quoted with this beside it.
PRED_SD = {"static": 0.315, "mobile": 0.563, "ratio": 0.645}


def wd(v, L):
    v = np.abs(v) % L
    return np.minimum(v, L - v)


# ================================================================= §3 information flow
def trace_prediction_inputs():
    """Static trace of what the frozen predictor actually reads."""
    src = open(f"{V}/OBFOR01/code/m6_obfor01.py").read()
    tree = ast.parse(src)
    npz_keys, reads_obs = set(), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, str):
            npz_keys.add(node.slice.value)
    # which function computes the frozen predictions, and what it takes
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "simulate_arm")
    args = [a.arg for a in fn.args.args]
    # does simulate_arm reference any observed statistic?
    body_src = ast.get_source_segment(src, fn)
    for bad in ("r80", "M2", "_residual", "observed", "OBSERVED", "nX_final", "frames"):
        if bad in body_src:
            reads_obs.append(bad)
    # what empirical_birth_flux reads
    fbf = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
               and n.name == "empirical_birth_flux")
    bf_src = ast.get_source_segment(src, fbf)
    return {"simulate_arm_arguments": args,
            "simulate_arm_references_to_target_statistics": reads_obs,
            "empirical_birth_flux_reads": [k for k in ("series", "fields", "accepted_births_X",
                                                       "N_X", "nX_final", "frames")
                                           if k in bf_src],
            "npz_keys_referenced_anywhere_in_the_file": sorted(npz_keys)}


def information_flow():
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    m6 = json.load(open(f"{V}/OBFOR01/out/_m6.json"))
    trace = trace_prediction_inputs()

    inputs = [
        {"input": "LawSpec point (L, CAP, S0, phi, omega, muX, muY, kX, kY, p_hop, X_SEED)",
         "category": "A", "why": "frozen in obdi02_protocol.yaml before every mission"},
        {"input": "exact one-step kernels K_X and K_Y", "category": "A",
         "why": "derived in OBTR01 from the engine source, hashed into METHODS_CORE"},
        {"input": "condition (static p_hop_Y = 0 / mobile)", "category": "A",
         "why": "the experimental condition itself"},
        {"input": "domain size L = 36, horizon 11000, burn-in 2000, cadence 50",
         "category": "A", "why": "frozen window block"},
        {"input": "the 28 fresh seeds", "category": "A",
         "why": "enumerated in the freeze commit's _freeze.json before any arm ran"},
        {"input": "organiser trajectory", "category": "A",
         "SIMULATED_EX_ANTE": True, "INJECTED_FROM_THE_ENGINE": False,
         "why": ("simulate_arm draws the organiser's increments itself, from the same exact "
                 "kernel, inside each simulated arm. No realized engine path is read. The "
                 "path is SHARED BY CONSTRUCTION within a simulated arm, which is the "
                 "mechanism under test, not an injection.")},
        {"input": "empirical birth-flux distribution", "category": "B",
         "SIMULATED_EX_ANTE": False, "INJECTED_FROM_THE_ENGINE": True,
         "source": "accepted_births_X per step, from up to 40 HISTORICAL OBDI02 / OBTC02 arms",
         "why": ("this is a MEASURED birth flux taken from delivered engine output. It is "
                 "non-target with respect to the fresh arms and it was frozen before them. "
                 "M6 cannot be started without it: the simulator does not derive the source "
                 "from the chemostat, it is handed the source. That derivational fact is "
                 "what makes the prediction conditional."),
         "load_bearing": False,
         "NUMERICALLY_LOAD_BEARING": False,
         "WITHDRAWN_JUSTIFICATION": (
             "the mission asserted that this input is load-bearing because replacing it by a "
             "Poisson source of the same mean moved the mobile prediction by 1.27 points. "
             "The repair round replicated that ablation sixteen times per side and obtained "
             "+0.41 +- 0.20 pp, an order of magnitude smaller and of the OPPOSITE sign; "
             "doubling the source intensity moved the prediction by +0.01 +- 0.23 pp with "
             "the dose verified delivered (117 -> 237 particles). The 1.27 pp figure is "
             "withdrawn. See OBFOR01_SEAL_REPAIR_EVIDENCE.json, R1 and R2."),
         "WHY_THE_CONCLUSION_IS_UNCHANGED": (
             "conditionality is a property of the DERIVATION, not of the sensitivity. An "
             "input measured on the system being predicted makes the prediction conditional "
             "on that measurement whatever its numerical influence turns out to be. The "
             "measured insensitivity is a robustness result and is reported as one."),
         "PROVENANCE_CONDITIONING": True},
        {"input": "N_X of historical arms", "category": "B",
         "role": "used ONLY to skip extinct historical arms when estimating the birth flux",
         "load_bearing": False, "PROVENANCE_CONDITIONING": False},
        {"input": "capacity refusals", "category": "not used",
         "why": "not simulated; bounded separately at 0.018 % on r80"},
        {"input": "finite-torus path", "category": "A",
         "why": "the torus is applied by construction in the simulator's modulo arithmetic"},
        {"input": "event-order history", "category": "A",
         "why": "the intra-step order is transcribed from kinetics.py, not measured"},
        {"input": "observed r80, M2 or radial profile of ANY arm", "category": "C",
         "USED_IN_THE_PREDICTION": False,
         "why": ("simulate_arm takes no such argument and references none; the observed "
                 "values are read only afterwards, to compare. Static trace: %s"
                 % (trace["simulate_arm_references_to_target_statistics"] or "no reference"))},
        {"input": "historical arm-to-arm dispersion of r80", "category": "C_HISTORICAL",
         "USED_IN_THE_POINT_PREDICTION": False,
         "USED_IN_THE_MARGIN_WIDTH": True,
         "why": ("the sampling term of the +-2.9 % margin is sized on the historical "
                 "arm-to-arm relative standard deviation. That is a dispersion, not a mean, "
                 "it cannot move the point comparison, and it was frozen before the fresh "
                 "arms. It is disclosed rather than hidden.")},
    ]
    used_C = [i for i in inputs if i["category"] == "C" and i.get("USED_IN_THE_PREDICTION")]
    used_B = [i for i in inputs if i["category"] == "B" and i.get("load_bearing")]
    provenance_B = [i for i in inputs if i.get("PROVENANCE_CONDITIONING")]

    # The rule is DERIVATIONAL. An earlier version of this classifier keyed on a hand-typed
    # "load_bearing" flag; once that flag is corrected to the measured value, that version
    # would emit UNCONDITIONAL. It is recorded here that it would, and why that would be
    # wrong: a numerically weak measured input is still a measured input.
    mode = ("TARGET_CONTAMINATED" if used_C
            else ("CONDITIONAL" if provenance_B else "UNCONDITIONAL"))
    naive_mode = ("TARGET_CONTAMINATED" if used_C
                  else ("CONDITIONAL" if used_B else "UNCONDITIONAL"))
    return {
        "STATIC_TRACE_OF_THE_FROZEN_PREDICTOR": trace,
        "DEPENDENCY_GRAPH": inputs,
        "LOAD_BEARING_CATEGORY_B_INPUTS": [i["input"] for i in used_B],
        "PROVENANCE_CONDITIONING_INPUTS": [i["input"] for i in provenance_B],
        "CLASSIFIER_RULE": ("CONDITIONAL as soon as any input to the prediction is a "
                            "measurement taken from delivered engine output, regardless of "
                            "its numerical influence"),
        "WHAT_A_SENSITIVITY_BASED_CLASSIFIER_WOULD_EMIT": naive_mode,
        "WHY_THAT_CLASSIFIER_IS_REJECTED": (
            "it would upgrade the claim on the strength of a null result. 'The input barely "
            "matters' is not 'the operator does not need the input'. M6 does not run without "
            "a birth-flux law and does not derive one."),
        "ANY_CATEGORY_C_INPUT_IN_THE_PREDICTION": bool(used_C),
        "SOURCE_PATH_TREATMENT": "SIMULATED_EX_ANTE__SHARED_BY_CONSTRUCTION",
        "BIRTH_FLUX_TREATMENT": "MEASURED_FROM_HISTORICAL_ARMS_AND_INJECTED_AS_A_LAW",
        "CAPACITY_TREATMENT": "NOT_MODELLED__BOUNDED_SEPARATELY",
        "TORUS_TREATMENT": "APPLIED_BY_CONSTRUCTION",
        "EVENT_ORDER_TREATMENT": "TRANSCRIBED_FROM_SOURCE",
        "STATIC_PREDICTION_MODE": mode,
        "MOBILE_PREDICTION_MODE": mode,
        "RATIO_PREDICTION_MODE": mode,
        "WHY_NOT_UNCONDITIONAL": (
            "the predictions are conditional on a birth-flux law measured from delivered "
            "engine output. Nothing target-derived enters, and the organiser trajectory is "
            "simulated rather than injected, so the predictions are genuinely predictive of "
            "the fresh clouds; but a model that must be TOLD the source, because it does not "
            "derive it from the chemostat, is not an unconditional first-principles "
            "operator. The conditioning is derivational. It is also, as the repair round "
            "measured, numerically weak: the mobile prediction is invariant to a doubling of "
            "the source intensity (+0.01 +- 0.23 pp) and moves by +0.41 +- 0.20 pp when the "
            "flux shape is replaced by a Poisson law of the same mean. Weak conditioning is "
            "still conditioning."),
        "FROZEN_PREDICTION_VALUES": {
            "static_median_r80": frz["PRIMARY_PREDICTIONS"][
                "STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"],
            "mobile_median_r80": frz["PRIMARY_PREDICTIONS"][
                "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"],
            "ratio": frz["PRIMARY_PREDICTIONS"]["MOBILE_STATIC_RATIO_COMPATIBILITY"][
                "predicted_ratio_under_M6"],
            "margin_percent": frz["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"]},
        "M6_BIRTH_FLUX_PROVENANCE": m6["BIRTH_FLUX_SOURCE"],
    }


# ================================================================= §4 recomputation
def ideal(L, mobile, q, mu):
    op = Operator(q, q if mobile else 0.0, mu, L)
    prof = op.stationary_profile()
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    o = np.argsort(d.ravel(), kind="stable")
    dd, ww = d.ravel()[o], prof.ravel()[o]
    cw = np.cumsum(ww) / ww.sum()
    return {"r80": float(dd[int(np.searchsorted(cw, 0.8, side="left"))]),
            "m2": float((prof * d ** 2).sum()),
            "cdf": np.array([prof[d <= r].sum() for r in RADIAL_GRID]),
            "p": prof.ravel() / prof.sum()}


def historical(q, mu):
    IDEAL = {(L, m): ideal(L, m, q, mu) for L in (36, 72, 96) for m in (True, False)}
    rows = []
    for root, prefix, mobile in ((f"{V}/OBDI02/raw", "L", True),
                                 (f"{V}/OBTC02/raw", "S__", False),
                                 (f"{V}/OBTC02/raw", "P__", True)):
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
            if len(v) < 50:
                continue
            ys, xs = np.nonzero(f)
            c = f[ys, xs].astype(float)
            dist = np.sqrt(wd(ys - oy, L) ** 2 + wd(xs - ox, L) ** 2)
            N = c.sum()
            rows.append({"file": n, "L": L, "mobile": mobile,
                         "median": float(np.median(v)), "mean": float(v.mean()),
                         "sd": float(v.std(ddof=1)),
                         "skew": float(((v - v.mean()) ** 3).mean() / v.std(ddof=1) ** 3),
                         "M2": float((c * dist ** 2).sum() / N),
                         "cdf": [float(c[dist <= r].sum() / N) for r in RADIAL_GRID],
                         "src": "OBDI02" if root.endswith("OBDI02/raw") else "OBTC02"})
    mob = [r for r in rows if r["mobile"] and r["src"] == "OBDI02"]
    sta = [r for r in rows if not r["mobile"]]
    P = [r for r in rows if r["mobile"] and r["src"] == "OBTC02"]

    def resid(rs, key, field):
        v = np.array([r[key] / IDEAL[(r["L"], r["mobile"])][field] for r in rs])
        se = v.std(ddof=1) / math.sqrt(len(v))
        return {"n": len(v), "ratio": float(v.mean()), "percent": 100 * (v.mean() - 1),
                "se_percent": 100 * se, "z": float((v.mean() - 1) / se)}

    O = np.array([r["cdf"] for r in mob])
    Pr = np.array([IDEAL[(r["L"], True)]["cdf"] for r in mob])
    Dd = O - Pr
    cdf_rows = []
    for i, r in enumerate(RADIAL_GRID):
        se = Dd[:, i].std(ddof=1) / math.sqrt(len(Dd))
        cdf_rows.append({"r": r, "predicted": float(Pr[:, i].mean()),
                         "observed": float(O[:, i].mean()),
                         "difference": float(Dd[:, i].mean()),
                         "z": float(Dd[:, i].mean() / se)})
    zmax = max(abs(x["z"]) for x in cdf_rows)
    dmax = max(abs(x["difference"]) for x in cdf_rows)

    # independent-draw dispersion, for the comparison the report makes
    rng = np.random.default_rng(4242)
    idl = IDEAL[(36, True)]
    iid_sd = []
    for _ in range(12):
        vv = []
        for _ in range(180):
            idx = rng.choice(36 * 36, size=118, p=idl["p"])
            g = np.zeros(36 * 36, np.int64)
            np.add.at(g, idx, 1)
            vv.append(M.radii(g.reshape(36, 36), 0, 0)[0.8])
        iid_sd.append(np.std(vv, ddof=1))

    return {
        "STATUS_OF_THIS_BLOCK": "REPRODUCTION_OF_THE_MISSION_PIPELINE__NOT_AN_INDEPENDENT_CHECK",
        "WHY": ("this function re-implements the mission's own arm-inclusion conditions "
                "(nY_final >= 1, nX_final >= 40, at least 50 in-window frames) byte for "
                "byte. Re-executing a filter can only confirm that the filter was executed. "
                "It is structurally incapable of detecting that the filter itself selects on "
                "an outcome. The rule is varied, not merely repeated, in "
                "OBFOR01_SEAL_REPAIR_EVIDENCE.json section R5."),
        "INCLUSION_RULE_IS_OUTCOME_DEPENDENT": {
            "rule": "nX_final >= 40",
            "nX_final_is": "the TERMINAL population of the arm, an outcome, not a design "
                           "variable",
            "sensitivity_of_the_headline_mobile_median_residual_percent": {
                "with the rule (n=116)": -5.101, "population threshold dropped (n=126)": -4.348,
                "no outcome-dependent threshold (n=129)": -2.144},
            "DIRECTION": "the excluded arms carry higher residuals; the rule pushes the "
                         "headline downward",
            "DISCLOSED_HERE_BECAUSE": "the headline -5.10 % is a property of the observable "
                                      "AND of the inclusion rule, and was reported as though "
                                      "it were a property of the observable alone"},
        "COMPOSITION_OF_THE_116_ARMS": {
            "OBDI02_mobile_arms_meeting_the_filter": len(mob),
            "by_size": {L: sum(1 for r in mob if r["L"] == L) for L in (36, 72, 96)},
            "OBTC02_static_arms": len(sta), "OBTC02_mobile_P_arms": len(P),
            "claimed": 116, "MATCHES": len(mob) == 116,
            "INDEPENDENT_UNITS": "the seed; one arm is one seed",
            "n_independent_units": len(mob)},
        "RADIAL_CDF": cdf_rows,
        "MAX_ABS_Z": zmax, "claimed_max_abs_z": 0.64, "MAX_Z_MATCHES": abs(zmax - 0.64) < 0.02,
        "MAX_PROBABILITY_DISCREPANCY": dmax, "claimed_max_discrepancy": 0.0038,
        "MAX_DISCREPANCY_MATCHES": abs(dmax - 0.0038) < 0.0003,
        "r80_MEDIAN_RULE": {"mobile": resid(mob, "median", "r80"),
                            "static": resid(sta, "median", "r80")},
        "r80_MEAN_RULE": {"mobile": resid(mob, "mean", "r80"),
                          "static": resid(sta, "mean", "r80")},
        "M2": {"mobile": resid(mob, "M2", "m2"), "static": resid(sta, "M2", "m2")},
        "WITHIN_ARM_DISPERSION": {
            "mobile_sd": float(np.mean([r["sd"] for r in mob if r["L"] == 36])),
            "static_sd": float(np.mean([r["sd"] for r in sta])),
            "mobile_skew": float(np.mean([r["skew"] for r in mob if r["L"] == 36])),
            "static_skew": float(np.mean([r["skew"] for r in sta])),
            "independent_draw_sd": float(np.mean(iid_sd)),
            "OVER_DISPERSION_FACTOR": float(np.mean([r["sd"] for r in mob if r["L"] == 36])
                                            / np.mean(iid_sd))},
    }


def fresh(q, mu):
    val = json.load(open(f"{V}/OBFOR01/out/_validation.json"))
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    delta = frz["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"]
    ep = frz["PRIMARY_PREDICTIONS"]
    # recompute the per-arm summaries from the RAW npz, not from the recorded arm records
    S, Mo = [], []
    for a in val["ARMS"]:
        z = np.load(f"{V}/OBFOR01/raw/%s.npz" % a["tag"].replace("/", "__"), allow_pickle=True)
        fr = [json.loads(str(s)) for s in z["frames"]]
        w = [x for x in fr if x["step"] > BURN_IN]
        v = np.array([x["r80_organiser"] for x in w
                      if x.get("r80_organiser") is not None
                      and np.isfinite(x["r80_organiser"])], float)
        rec = {"tag": a["tag"], "median": float(np.median(v)), "mean": float(v.mean()),
               "sd": float(v.std(ddof=1)), "recorded_median": a["r80_median"],
               "MATCHES_RECORD": abs(np.median(v) - a["r80_median"]) < 1e-12}
        (S if a["condition"] == "S" else Mo).append(rec)

    from seal_repair import t_sf                          # the t upper tail, no scipy

    def endpoint(name, vals, pred):
        v = np.array([x["median"] for x in vals])
        m, se = v.mean(), v.std(ddof=1) / math.sqrt(len(v))
        r = m / pred - 1
        rse = se / pred
        df = len(v) - 1
        return {"NAME": name, "n_independent_units": len(v), "prediction": pred,
                "PREDICTION_MONTE_CARLO_SD_percent": PRED_SD[name],
                "observed": float(m), "absolute_error": float(m - pred),
                "relative_error_percent": 100 * r,
                "se_relative_percent": 100 * rse,
                "ci95_relative_percent": [100 * (r - 1.96 * rse), 100 * (r + 1.96 * rse)],
                "margin_percent": delta,
                "CRITERION_OF_RECORD": "POINT_INSIDE (the frozen rule)",
                "POINT_INSIDE": bool(abs(r) <= delta / 100),
                "WHOLE_INTERVAL_INSIDE": bool(abs(r) + 1.96 * rse <= delta / 100),
                "WHOLE_INTERVAL_IS_POST_FREEZE": True,
                "TOST_p_t_%d_df" % df: float(t_sf((delta / 100 - abs(r)) / rse, df))
                if rse > 0 else 0.0,
                "TOST_p_NORMAL_AS_ORIGINALLY_REPORTED__WRONG":
                    float(1 - 0.5 * (math.erf((delta / 100 - abs(r))
                                              / (rse * math.sqrt(2))) + 1)) if rse > 0 else 0.0,
                "TOST_NOTE": ("the standard error rests on %d degrees of freedom; the "
                              "originally reported p used a normal tail and was optimistic "
                              "by up to four orders of magnitude" % df)}

    e_s = endpoint("static", S, ep["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"][
        "predicted_r80_median"])
    e_m = endpoint("mobile", Mo, ep["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"][
        "predicted_r80_median"])
    vs = np.array([x["median"] for x in S])
    vm = np.array([x["median"] for x in Mo])
    ms, mm = vs.mean(), vm.mean()
    ses, sem = vs.std(ddof=1) / math.sqrt(len(vs)), vm.std(ddof=1) / math.sqrt(len(vm))
    predr = ep["MOBILE_STATIC_RATIO_COMPATIBILITY"]["predicted_ratio_under_M6"]
    obsr = mm / ms
    rel = math.sqrt((sem / mm) ** 2 + (ses / ms) ** 2)
    r = obsr / predr - 1
    e_r = {"NAME": "ratio", "n_static": len(vs), "n_mobile": len(vm),
           "prediction": predr, "observed": float(obsr),
           "PREDICTION_MONTE_CARLO_SD_percent": PRED_SD["ratio"],
           "relative_error_percent": 100 * r, "se_relative_percent": 100 * rel,
           "ci95_relative_percent": [100 * (r - 1.96 * rel), 100 * (r + 1.96 * rel)],
           "margin_percent": delta,
           "CRITERION_OF_RECORD": "POINT_INSIDE (the frozen rule)",
           "POINT_INSIDE": bool(abs(r) <= delta / 100),
           "WHOLE_INTERVAL_INSIDE": bool(abs(r) + 1.96 * rel <= delta / 100),
           "WHOLE_INTERVAL_IS_POST_FREEZE": True,
           "WHOLE_INTERVAL_WITH_THE_PREDICTION_SD_PROPAGATED_percent":
               100 * (abs(r) + 2.0555 * math.sqrt(rel ** 2 + (PRED_SD["ratio"] / 100) ** 2)),
           "MARGIN_RECIPE_APPLIED_TO_THE_RATIO_WOULD_HAVE_GIVEN_percent": 3.15,
           "MARGIN_NOTE": ("delta = 2.9 was sized on the two ABSOLUTE endpoints. Applying "
                           "the same recipe to the ratio, whose sampling error is the "
                           "quadrature sum of the two, would have given about 3.15 %. The "
                           "ratio was therefore judged against a margin slightly TIGHTER "
                           "than its own recipe, which is the conservative direction."),
           "DEPENDENCE_TREATMENT": (
               "the static and mobile arms are DISJOINT seed sets drawn from a single frozen "
               "register and executed in one batch, so the two means are independent and the "
               "delta-method variance is the sum of the two relative variances. Treating them "
               "as paired would be wrong: there is no pairing."),
           "INDEPENDENT_BY_CONSTRUCTION": True}
    return {"PER_ARM_RECOMPUTED_FROM_RAW": {"static": S, "mobile": Mo},
            "ALL_ARM_SUMMARIES_REPRODUCE_THE_RECORD":
                all(x["MATCHES_RECORD"] for x in S + Mo),
            "ENDPOINTS": {"static": e_s, "mobile": e_m, "ratio": e_r},
            "THE_FROZEN_CRITERION": {
                "text": frz["RESIDUAL_TOLERANCE"]["RULE"],
                "form": "POINT rule: |observed / predicted - 1| <= 2.9 %",
                "it_names_no_interval_no_confidence_level_and_no_quantile": True},
            "ALL_THREE_POINTS_INSIDE__THE_CRITERION_OF_RECORD":
                bool(e_s["POINT_INSIDE"] and e_m["POINT_INSIDE"] and e_r["POINT_INSIDE"]),
            "WHOLE_INTERVAL_CRITERION_PROVENANCE": (
                "the whole-interval criterion, the 1.96 factor, the delta-method variance of "
                "the ratio and the TOST-style p ALL first appear in adjudicate_obfor01.py, "
                "committed at cb1aaa2, i.e. AFTER the 28 arms ran at 0148acc. They are "
                "POST-FREEZE. Mitigating: the interval criterion is STRICTER than the frozen "
                "point rule, so applying it could only make passing harder. Aggravating: "
                "delta = 2.9 was itself sized as roughly two sampling standard errors of "
                "this very experiment, so a criterion that then adds 1.96 standard errors is "
                "close to consuming the whole margin, and it passed comfortably only because "
                "the fresh arms turned out less dispersed than assumed (2.71 % against the "
                "4.15 % historical figure used to size the margin)."),
            "ALL_THREE_WHOLE_INTERVALS_INSIDE":
                bool(e_s["WHOLE_INTERVAL_INSIDE"] and e_m["WHOLE_INTERVAL_INSIDE"]
                     and e_r["WHOLE_INTERVAL_INSIDE"])}


def ablations():
    adj = json.load(open(f"{V}/OBFOR01/out/_adjudication.json"))
    m6 = json.load(open(f"{V}/OBFOR01/out/_m6.json"))
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    ab = adj["ABLATION"]
    d = {k: ab[k] for k in ("distance_to_the_full_model",
                            "distance_to_the_model_without_the_shared_trajectory",
                            "distance_to_the_model_with_a_poisson_source")}
    d["distance_to_the_uncorrected_ideal_value"] = abs(
        ab["observed_mobile_median"] - ab["predictions"]["ideal_population_value"])
    full = d["distance_to_the_full_model"]
    return {
        "DISTANCES": d,
        "claimed": {"full": 0.0197, "no_shared": 0.2975, "poisson": 0.0889,
                    "uncorrected": 0.4669},
        "MATCH": {k: abs(d[a] - v) < 5e-4 for (k, v), a in zip(
            {"full": 0.0197, "no_shared": 0.2975, "poisson": 0.0889,
             "uncorrected": 0.4669}.items(),
            ["distance_to_the_full_model",
             "distance_to_the_model_without_the_shared_trajectory",
             "distance_to_the_model_with_a_poisson_source",
             "distance_to_the_uncorrected_ideal_value"])},
        "FACTORS": {"no_shared_over_full":
                    d["distance_to_the_model_without_the_shared_trajectory"] / full,
                    "poisson_over_full":
                        d["distance_to_the_model_with_a_poisson_source"] / full,
                    "uncorrected_over_full":
                        d["distance_to_the_uncorrected_ideal_value"] / full},
        "claimed_factors": [15, 4.5, 24],
        "THE_POISSON_FACTOR_OF_4p5_IS_NOT_A_REJECTION": (
            "the Poisson-source variant sits 4.5 times further from the observation than the "
            "full model, but its own residual is -4.42 %% against an observation of "
            "-5.17 %%, i.e. it PASSES the primary +-2.9 %% endpoint on its own. Reporting it "
            "through a distance ratio makes a passing model look rejected. It is not "
            "rejected, and the repair round shows the underlying difference does not even "
            "replicate."),
        "SEQUENTIAL": m6["DECOMPOSITION"]["SEQUENTIAL"],
        "FACTORIAL": m6["DECOMPOSITION"]["FACTORIAL"],
        "WHICH_DECOMPOSITION_TERMS_SURVIVE_REPLICATION": {
            "shared_trajectory_main_effect_pp": -3.7396923099114794,
            "shared_trajectory_SURVIVES": True,
            "why": ("about six times the measured replicate standard deviation of a 30-arm "
                    "M6 point prediction (0.563 pp), and independently confirmed by the "
                    "fresh ablation endpoint, where the no-shared-trajectory model misses "
                    "the fresh mobile observation by -3.55 %, outside the margin"),
            "birth_flux_main_effect_pp": -1.298673772890935,
            "birth_flux_SURVIVES": False,
            "why_not": ("replication over 16 x 30 arms per side gives +0.41 +- 0.20 pp, an "
                        "order of magnitude smaller and of the opposite sign; see "
                        "OBFOR01_SEAL_REPAIR_EVIDENCE.json R1"),
            "interaction_SURVIVES": False},
        "WHAT_WAS_FROZEN_BEFORE_THE_FRESH_RUNS": {
            "the ablation predictions themselves": True,
            "the ablation RULE (full model must sit closer than the no-shared-trajectory "
            "model)": True,
            "evidence": frz["PRIMARY_PREDICTIONS"]["ABLATION_RULE"],
            "the sequential and factorial decomposition": True,
            "note": "all of these live inside the freeze commit's _m6.json and _freeze.json"},
        "WHAT_IS_A_POST_OUTCOME_DIAGNOSTIC": [
            "the observed distances themselves, which can only exist after the arms ran",
            "the factor arithmetic 15 / 4.5 / 24",
            "the continuum-to-discrete comparison, computed in the raw-only phase and never "
            "used as a confirmatory endpoint"],
        "IS_A_POST_OUTCOME_ABLATION_THE_PRIMARY_TEST": False,
        "why": ("the three primary endpoints are the absolute static profile, the absolute "
                "mobile profile and their ratio, all frozen. The ablation is a mechanistic "
                "control declared in the same freeze, and it is reported as such."),
    }


def claim_scope(q, mu):
    mech = json.load(open(f"{V}/OBFOR01/out/_mechanisms.json"))
    hist = historical.__wrapped__ if hasattr(historical, "__wrapped__") else None
    return {
        "LEVELS": {
            "exact_conditional_state_update": mech["S8_CONDITIONAL_OPERATOR"][
                "FULL_ONE_STEP_CONDITIONAL_OPERATOR"],
            "observable_level_prediction": "QUALIFIED_FOR_THE_TESTED_OBSERVABLES",
            "marginal_density_closure": mech["S8_CONDITIONAL_OPERATOR"][
                "MARGINAL_DENSITY_CLOSURE"],
            "full_state_physical_theory": "NOT_CLAIMED"},
        "EVIDENCE_THAT_THE_MARGINAL_DOES_NOT_CLOSE":
            mech["S8_CONDITIONAL_OPERATOR"]["MEASURED_COUPLINGS"],
        "THE_CLAIM_MUST_NOT_BE": [
            "a closed evolution equation for the density",
            "a full-state physical theory",
            "an exact-zero residual"],
    }


def main():
    spec_pt = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))["FREEZE_MANIFEST"]["frozen_point"]
    q, mu = spec_pt["p_hop"] / 4.0, spec_pt["muX"]

    flow = information_flow()
    json.dump(flow, open(f"{OUT}/OBFOR01_PREDICTION_INFORMATION_FLOW.json", "w"),
              indent=1, default=str)

    H = historical(q, mu)
    Fr = fresh(q, mu)
    Ab = ablations()
    Cs = claim_scope(q, mu)
    # is "no deficit" the same as "exact zero"? test the M2 residuals against zero
    for k in ("mobile", "static"):
        m2 = H["M2"][k]
        m2["CI95_percent"] = [m2["percent"] - 1.96 * m2["se_percent"],
                              m2["percent"] + 1.96 * m2["se_percent"]]
        m2["ZERO_INSIDE_THE_INTERVAL"] = bool(m2["CI95_percent"][0] <= 0 <= m2["CI95_percent"][1])
        m2["EXACT_ZERO_ESTABLISHED"] = False
    rec = {"SECTION": "SEAL §4", "HISTORICAL": H, "FRESH": Fr, "ABLATIONS": Ab,
           "CLAIM_SCOPE": Cs,
           "NO_DEFICIT_IS_NOT_EXACT_ZERO": (
               "the M2 residuals are +%.2f %% mobile [%.2f, %.2f] and +%.2f %% static "
               "[%.2f, %.2f]. Zero lies inside both intervals, so no deficit is detected; but "
               "the intervals are wide, so an exact zero residual is NOT established and must "
               "not be claimed."
               % (H["M2"]["mobile"]["percent"], H["M2"]["mobile"]["CI95_percent"][0],
                  H["M2"]["mobile"]["CI95_percent"][1], H["M2"]["static"]["percent"],
                  H["M2"]["static"]["CI95_percent"][0], H["M2"]["static"]["CI95_percent"][1]))}
    json.dump(rec, open(f"{OUT}/OBFOR01_HEADLINE_RECOMPUTATION.json", "w"), indent=1,
              default=str)

    print("§3 INFORMATION FLOW")
    print("  source path      %s" % flow["SOURCE_PATH_TREATMENT"])
    print("  birth flux       %s" % flow["BIRTH_FLUX_TREATMENT"])
    print("  category C used  %s" % flow["ANY_CATEGORY_C_INPUT_IN_THE_PREDICTION"])
    print("  load-bearing B   %s" % flow["LOAD_BEARING_CATEGORY_B_INPUTS"])
    print("  STATIC/MOBILE/RATIO_PREDICTION_MODE = %s" % flow["STATIC_PREDICTION_MODE"])
    print()
    print("§4A HISTORICAL")
    c = H["COMPOSITION_OF_THE_116_ARMS"]
    print("  116 arms: recomputed %d (%s), by size %s" % (c["OBDI02_mobile_arms_meeting_the_filter"],
                                                          c["MATCHES"], c["by_size"]))
    print("  max |z| %.4f (claimed 0.64: %s) ; max discrepancy %.5f (claimed 0.0038: %s)"
          % (H["MAX_ABS_Z"], H["MAX_Z_MATCHES"], H["MAX_PROBABILITY_DISCREPANCY"],
             H["MAX_DISCREPANCY_MATCHES"]))
    for rule in ("r80_MEDIAN_RULE", "r80_MEAN_RULE", "M2"):
        for k in ("mobile", "static"):
            v = H[rule][k]
            print("  %-16s %-7s n=%3d  %+7.2f %%  se %.2f  z %+6.2f"
                  % (rule, k, v["n"], v["percent"], v["se_percent"], v["z"]))
    w = H["WITHIN_ARM_DISPERSION"]
    print("  within-arm sd mobile %.3f static %.3f ; independent draw %.3f -> factor %.2f"
          % (w["mobile_sd"], w["static_sd"], w["independent_draw_sd"],
             w["OVER_DISPERSION_FACTOR"]))
    print("  skew mobile %+.3f static %+.3f" % (w["mobile_skew"], w["static_skew"]))
    print()
    print("§4B FRESH")
    print("  per-arm summaries reproduce the record: %s"
          % Fr["ALL_ARM_SUMMARIES_REPRODUCE_THE_RECORD"])
    for k, v in Fr["ENDPOINTS"].items():
        print("  %-7s n=%2s pred %8.4f obs %8.4f  err %+6.2f %%  CI [%+.2f, %+.2f]  "
              "point in %s  WHOLE interval in %s"
              % (k, v.get("n_independent_units", v.get("n_mobile")), v["prediction"],
                 v["observed"], v["relative_error_percent"], v["ci95_relative_percent"][0],
                 v["ci95_relative_percent"][1], v["POINT_INSIDE"], v["WHOLE_INTERVAL_INSIDE"]))
    print("  ALL THREE WHOLE INTERVALS INSIDE THE MARGIN: %s"
          % Fr["ALL_THREE_WHOLE_INTERVALS_INSIDE"])
    print()
    print("§4C ABLATIONS  %s" % {k: round(v, 4) for k, v in Ab["DISTANCES"].items()})
    print("  match claims %s ; factors %s"
          % (Ab["MATCH"], {k: round(v, 2) for k, v in Ab["FACTORS"].items()}))
    print()
    print("§4D CLAIM SCOPE")
    print("  " + rec["NO_DEFICIT_IS_NOT_EXACT_ZERO"])


if __name__ == "__main__":
    main()
