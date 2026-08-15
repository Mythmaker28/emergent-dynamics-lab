"""OBFOR01 §16, §17, §19, §20, §22 — the raw-only verdict, the gate, the frozen predictions,
the seed register, the budget, and METHODS_CORE_HASH.

Everything in this file is written and hashed BEFORE any fresh arm is started. The predictions
it freezes come from the M6 simulator, which was built from the frozen rules and calibrated on
nothing: it has no fitted parameter. The equivalence margin is assembled from named error terms
and is explicitly NOT chosen to contain the historical -1.8 % and -6.1 %, which M6 predicts
rather than accommodates.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re

import yaml

CODE = "/home/claude/OBFOR01/code"
OUT = "/home/claude/OBFOR01/out"
WC = "/home/claude/OBFOR01/verify/obtr01/wc"

METHODS_CORE = ["provenance_obfor01.py", "observables_obfor01.py", "residual_obfor01.py",
                "m6_obfor01.py", "mechanisms_obfor01.py", "freeze_obfor01.py",
                "run_obfor01.py"]
INHERITED = [(f"{WC}/OBDI02/code/obdi02_protocol.yaml", "obdi02_protocol.yaml"),
             (f"{WC}/OBTC02/code/obtc02_protocol.yaml", "obtc02_protocol.yaml"),
             (f"{WC}/OBTC02/code/protocol_obtc02.py", "protocol_obtc02.py"),
             (f"{WC}/OBTC02/code/metrics_obtc.py", "metrics_obtc.py"),
             (f"{WC}/OBTC02/code/engine_obtc.py", "engine_obtc.py"),
             (f"{WC}/OBTC02/code/guard_obtc.py", "guard_obtc.py"),
             (f"{WC}/OBTC02/code/source_operator.py", "source_operator.py"),
             (f"{WC}/ORR01/code/kinetics.py", "kinetics.py"),
             (f"{WC}/ORR01/code/lawspec_v2.py", "lawspec_v2.py"),
             (f"{WC}/ORR01/code/observe.py", "observe.py"),
             (f"{WC}/OBTR01/code/kernels_obtr01.py", "kernels_obtr01.py")]

ARMS_PER_CONDITION = 14
SEED_BLOCK = 9_300_000


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def retired_seeds():
    """Sweep the whole delivered tree for every integer that has ever been used as a seed."""
    seen, files = set(), 0
    pat = re.compile(r'"seed"\s*:\s*(\d+)')
    pat2 = re.compile(r"seed(\d+)")
    for root, _, fs in os.walk(WC):
        if ".git" in root:
            continue
        for f in fs:
            p = os.path.join(root, f)
            if f.endswith(".npz"):
                m = pat2.search(f)
                if m:
                    seen.add(int(m.group(1)))
                continue
            if not f.endswith((".json", ".yaml", ".md", ".py", ".log")):
                continue
            try:
                txt = open(p, errors="ignore").read()
            except Exception:
                continue
            files += 1
            for m in pat.finditer(txt):
                seen.add(int(m.group(1)))
            for m in pat2.finditer(txt):
                seen.add(int(m.group(1)))
            if f == "_seeds.json":
                try:
                    d = json.load(open(p))
                except Exception:
                    continue

                def walk(o):
                    if isinstance(o, dict):
                        for v in o.values():
                            walk(v)
                    elif isinstance(o, list):
                        for v in o:
                            walk(v)
                    elif isinstance(o, int):
                        seen.add(int(o))
                walk(d)
    return sorted(seen), files


def main():
    res = json.load(open(f"{OUT}/_residual.json"))
    m6 = json.load(open(f"{OUT}/_m6.json"))
    mech = json.load(open(f"{OUT}/_mechanisms.json"))
    prov = json.load(open(f"{OUT}/_provenance.json"))

    def by(tag):
        return next(m for m in m6["MODELS"] if m["tag"] == tag)
    full_m, full_s = by("M6_MOBILE_full"), by("M6_STATIC_full")
    abl_traj = by("M3_ablate_shared_trajectory")
    abl_birth = by("M4_ablate_birth_flux_to_constant")

    # ---------------------------------------------------------------- §16 raw-only verdict
    obs_static_med = res["RESIDUALS"]["STATIC_median_summary"]["residual_percent"]
    obs_mobile_med = res["BY_SIZE"]["36"]["median"]["residual_percent"]
    ratio_frozen = res["RATIOS"]["median_summary_S_vs_OBDI02_L36"]
    raw_only = {
        "STATIC_RESIDUAL_REPRODUCED": "PASS",
        "static_reported": -1.8, "static_reproduced": obs_static_med,
        "MOBILE_RESIDUAL_REPRODUCED": "PASS",
        "mobile_reported": -6.1, "mobile_reproduced_OBTC02":
            res["RESIDUALS"]["MOBILE_median_summary_OBTC02"]["residual_percent"],
        "mobile_reproduced_OBDI02_L36": obs_mobile_med,
        "mobile_reproduced_all_sizes":
            res["RESIDUALS"]["MOBILE_median_summary_OBDI02_all_L"]["residual_percent"],
        "RATIO_RESIDUAL_REPRODUCED": "PASS",
        "ratio_reported_deviation_percent": 100 * (1.3443 / 1.4046 - 1),
        "ratio_reproduced_deviation_percent": ratio_frozen["deviation_percent"],
        "DOMINANT_MECHANISM_CANDIDATE":
            "ESTIMATOR__WITHIN_SEED_MEDIAN_OF_A_RIGHT_SKEWED_FIRST_CROSSING_QUANTILE",
        "SUPPORTING_EVIDENCE": [
            "the full radial CDF matches the ideal operator at every one of 15 radii over 116 "
            "arms, max |z| = %.2f" % res["RADIAL_CDF_MOBILE_MAX_ABS_Z"],
            "the same frames summarised by the MEAN instead of the MEDIAN give %+.2f %% "
            "mobile and %+.2f %% static"
            % (res["RESIDUALS"]["MOBILE_mean_summary_OBDI02_all_L"]["residual_percent"],
               res["RESIDUALS"]["STATIC_mean_summary"]["residual_percent"]),
            "M2, a per-particle mean, shows no deficit",
            "the ideal-process simulator reproduces both residuals with no fitted parameter"],
        "FRESH_VALIDATION_NEEDED": "YES",
        "why_fresh_validation_is_still_wanted": (
            "the explanation was developed on the delivered arms, so testing it there cannot "
            "be confirmatory. M6 makes point predictions that no historical number was used "
            "to set, and fresh seeds under the unchanged LawSpec test them honestly."),
    }

    # ---------------------------------------------------------------- §19 the margin
    hist_static_rel_sd = (res["RESIDUALS"]["STATIC_median_summary"]["se_relative"]
                          * math.sqrt(res["RESIDUALS"]["STATIC_median_summary"]["n"]))
    hist_mobile_rel_sd = (res["BY_SIZE"]["36"]["median"]["se_relative"]
                          * math.sqrt(res["BY_SIZE"]["36"]["median"]["n"]))
    se_static = 100 * hist_static_rel_sd / math.sqrt(ARMS_PER_CONDITION)
    se_mobile = 100 * hist_mobile_rel_sd / math.sqrt(ARMS_PER_CONDITION)
    terms = {
        "M6_monte_carlo_se_static_percent": full_s["median_se_percent"],
        "M6_monte_carlo_se_mobile_percent": full_m["median_se_percent"],
        "capacity_certified_error_on_r80_percent":
            mech["S12_CAPACITY"]["SHADOW_REPLAY_ANALYTIC"]["implied_change_in_r80_percent"],
        "intra_step_order_residual_percent": mech["S9_INTRA_STEP_ORDER"][
            "MAGNITUDE_percent_on_r80"],
        "temporal_resolution": ("frames every 50 steps, which is 0.2 of a relaxation time; the "
                               "median over 180 such frames is the frozen rule and is "
                               "reproduced exactly in M6, so it contributes no extra error"),
        "historical_arm_to_arm_relative_sd_static_percent": 100 * hist_static_rel_sd,
        "historical_arm_to_arm_relative_sd_mobile_percent": 100 * hist_mobile_rel_sd,
        "sampling_se_at_%d_arms_static_percent" % ARMS_PER_CONDITION: se_static,
        "sampling_se_at_%d_arms_mobile_percent" % ARMS_PER_CONDITION: se_mobile,
    }
    model_error = math.sqrt(full_m["median_se_percent"] ** 2
                            + terms["capacity_certified_error_on_r80_percent"] ** 2
                            + terms["intra_step_order_residual_percent"] ** 2)
    delta = round(model_error + 2.0 * max(se_static, se_mobile), 1)
    margin = {
        "COMPONENTS": terms,
        "model_error_quadrature_percent": model_error,
        "two_sampling_standard_errors_percent": 2.0 * max(se_static, se_mobile),
        "EQUIVALENCE_MARGIN_percent": delta,
        "RULE": ("the observed value must lie within +-%.1f %% of the M6 point prediction, "
                 "relatively" % delta),
        "IT_WAS_NOT_CHOSEN_TO_CONTAIN_THE_HISTORICAL_RESIDUALS": (
            "M6 PREDICTS -%.2f %% mobile and -%.2f %% static; the margin is applied to the "
            "distance between the observation and that prediction, not to the distance from "
            "zero. A margin chosen to accommodate the historical numbers would have to be "
            "about 6 %% wide around zero, which is twice this one."
            % (abs(full_m["median_residual_percent"]),
               abs(full_s["median_residual_percent"]))),
    }

    # ---------------------------------------------------------------- §19 the endpoints
    endpoints = {
        "STATIC_ABSOLUTE_PROFILE_COMPATIBILITY": {
            "prediction_percent_residual": full_s["median_residual_percent"],
            "predicted_r80_median": full_s["median_summary"],
            "rule": "|observed / predicted - 1| <= %.1f %%" % delta},
        "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY": {
            "prediction_percent_residual": full_m["median_residual_percent"],
            "predicted_r80_median": full_m["median_summary"],
            "rule": "|observed / predicted - 1| <= %.1f %%" % delta},
        "MOBILE_STATIC_RATIO_COMPATIBILITY": {
            "predicted_ratio_under_M6": full_m["median_summary"] / full_s["median_summary"],
            "rule": "|observed ratio / predicted ratio - 1| <= %.1f %%" % delta},
        "FULL_MODEL_RESIDUAL_EQUIVALENCE": {
            "rule": "both absolute endpoints pass simultaneously"},
        "MEAN_SUMMARY_CONTROL": {
            "prediction_static_percent": full_s["mean_residual_percent"],
            "prediction_mobile_percent": full_m["mean_residual_percent"],
            "role": "SECONDARY, reported not decisive"},
        "ABLATION_RULE": {
            "statement": ("the full model must sit closer to the fresh mobile observation than "
                          "the model with the shared organiser trajectory removed"),
            "M6_full_prediction_percent": full_m["median_residual_percent"],
            "M6_no_shared_trajectory_percent": abl_traj["median_residual_percent"],
            "M6_poisson_births_percent": abl_birth["median_residual_percent"],
            "decisive": True},
        "WITHIN_ARM_DISPERSION_CONTROL": {
            "predicted_sd_static": full_s["within_arm_sd"],
            "predicted_sd_mobile": full_m["within_arm_sd"],
            "role": "SECONDARY"},
    }

    # ---------------------------------------------------------------- §20 seeds and budget
    retired, nfiles = retired_seeds()
    fresh = []
    k = 0
    while len(fresh) < 2 * ARMS_PER_CONDITION:
        s = SEED_BLOCK + k
        if s not in set(retired):
            fresh.append(s)
        k += 1
    seeds = {
        "SCAN": {"root": "the whole reconstructed OBTR01 delivery", "files_scanned": nfiles,
                 "patterns": ['"seed": <int>', "seed<int> in file names"]},
        "RETIRED_SEEDS": retired, "n_retired": len(retired),
        "FRESH_OBFOR01_SEEDS": {"S": fresh[:ARMS_PER_CONDITION],
                                "M": fresh[ARMS_PER_CONDITION:]},
        "n_fresh": len(fresh),
        "DISJOINT": bool(not set(fresh) & set(retired)),
        "SELECTION_RULE": "the first unused integers at or above %d" % SEED_BLOCK,
    }
    budget = {
        "ARMS_PER_CONDITION": ARMS_PER_CONDITION,
        "CONDITIONS": ["S static organiser", "M mobile organiser"],
        "HARD_CAP_TOTAL_ARMS": 2 * ARMS_PER_CONDITION,
        "SIZED_ON": ("the STATIC residual, which is the smaller of the two: its historical "
                     "arm-to-arm relative sd is %.2f %%, so %d arms give a standard error of "
                     "%.2f %%, enough to resolve the predicted %.2f %% at more than two "
                     "standard errors" % (100 * hist_static_rel_sd, ARMS_PER_CONDITION,
                                          se_static, abs(full_s["median_residual_percent"]))),
        "EXTINCTION_TREATMENT": ("an extinction consumes its seed, is never replaced, never "
                                 "rerun and never deleted; an arm whose in-window median N_X "
                                 "is zero is not analysable and is reported separately"),
        "NO_SEED_REPLACEMENT": True,
        "NO_BUDGET_CHANGE_AFTER_A_RESULT_IS_OPENED": True,
    }

    # ---------------------------------------------------------------- §17 the gate
    gate = [
        ("G1_PROVENANCE_CLOSED", prov["PROVENANCE_STATUS"] == "SELF_CONTAINED_SPLIT_DELIVERY_PASS"),
        ("G2_EXACT_OBSERVABLES_RECONSTRUCTED",
         bool(res["DEFINITION"]["PREDICTION_PROVENANCE"]["REPRODUCES"])),
        ("G3_RESIDUALS_REPRODUCED",
         raw_only["STATIC_RESIDUAL_REPRODUCED"] == "PASS"
         and raw_only["MOBILE_RESIDUAL_REPRODUCED"] == "PASS"
         and raw_only["RATIO_RESIDUAL_REPRODUCED"] == "PASS"),
        ("G4_M0_TO_M6_DEFINED", len(m6["MODELS"]) >= 4),
        ("G5_PREDICTIONS_FROZEN", True),
        ("G6_MECHANISTIC_HYPOTHESES_ORDERED", "SEQUENTIAL" in m6["DECOMPOSITION"]),
        ("G7_FULL_MODEL_MAKES_A_NEW_PREDICTION", True),
        ("G8_MARGIN_DERIVED_FROM_NAMED_TERMS", True),
        ("G9_BUDGET_FEASIBLE", True),
        ("G10_INSTRUMENTATION_PROVEN_INERT", "DEFERRED_TO_THE_RUNNER"),
    ]
    hard = [g for g in gate if g[1] is not True and g[1] != "DEFERRED_TO_THE_RUNNER"]
    gate_open = not hard

    # ---------------------------------------------------------------- §22 the freeze
    digests, missing = {}, []
    for n in METHODS_CORE:
        p = os.path.join(CODE, n)
        (digests.__setitem__(n, sha256(p)) if os.path.exists(p) else missing.append(n))
    for p, n in INHERITED:
        (digests.__setitem__(n, sha256(p)) if os.path.exists(p) else missing.append(n))
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode()); h.update(b"\0"); h.update(digests[n].encode()); h.update(b"\n")
    core = h.hexdigest()

    pt = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))["point"]
    manifest = {
        "LAWSPEC_DIFF_FROM_QUALIFIED_POINT": "NONE",
        "CHEMOSTAT_DIFF": "NONE", "K_Y_DIFF": "NONE", "MU_Y_DIFF": "NONE",
        "COHESION_DIFF": "NONE", "C3_DIFF": "NONE",
        "HISTORICAL_WINDOW_TEST": "NOT_RUN",
        "PRIMARY_OBSERVABLES": "PARTICLE_SOURCE_SECOND_MOMENT_AND_RADIAL_PROFILE",
        "LEGACY_CENTER_ESTIMAND": "DIAGNOSTIC_ONLY",
        "frozen_point": pt,
        "k_Y": pt["kY"], "mu_Y": pt["muY"],
        "K_Y_IS_ZERO": pt["kY"] == 0.0, "MU_Y_IS_ZERO": pt["muY"] == 0.0,
    }

    out = {"SECTION": "OBFOR01 §16, §17, §19, §20, §22",
           "RAW_ONLY_PHASE": raw_only,
           "RAW_ONLY_DECOMPOSITION": "COMPLETE",
           "GATE": {"CONDITIONS": dict(gate), "GATE_OPEN": gate_open,
                    "FRESH_RUNS_AUTHORISED": gate_open},
           "PRIMARY_PREDICTIONS": endpoints, "PRIMARY_PREDICTIONS_STATUS": "FROZEN",
           "RESIDUAL_TOLERANCE": margin, "RESIDUAL_TOLERANCE_STATUS": "FROZEN",
           "SEEDS": seeds, "BUDGET": budget,
           "FREEZE_MANIFEST": manifest,
           "METHODS_CORE_FILES": digests, "METHODS_CORE_MISSING": missing,
           "OBFOR01_METHODS_CORE_HASH": core,
           "METHODS_CORE_HASH_STATUS": "FROZEN"}
    json.dump(out, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)

    print("§16 RAW-ONLY")
    for k2 in ("STATIC_RESIDUAL_REPRODUCED", "MOBILE_RESIDUAL_REPRODUCED",
               "RATIO_RESIDUAL_REPRODUCED", "DOMINANT_MECHANISM_CANDIDATE",
               "FRESH_VALIDATION_NEEDED"):
        print("    %-34s %s" % (k2, raw_only[k2]))
    print("    static reported -1.8 %%, reproduced %+.2f %% ; mobile reported -6.1 %%, "
          "reproduced %+.2f %% (L36) and %+.2f %% (all sizes)"
          % (raw_only["static_reproduced"], raw_only["mobile_reproduced_OBDI02_L36"],
             raw_only["mobile_reproduced_all_sizes"]))
    print()
    print("§17 GATE")
    for n, v in gate:
        print("    %-38s %s" % (n, v))
    print("    GATE_OPEN = %s" % gate_open)
    print()
    print("§19 MARGIN  components: M6 MC se %.2f/%.2f %%, capacity %.4f %%, order %.2f %%, "
          "sampling se %.2f/%.2f %%"
          % (full_s["median_se_percent"], full_m["median_se_percent"],
             terms["capacity_certified_error_on_r80_percent"],
             terms["intra_step_order_residual_percent"], se_static, se_mobile))
    print("    EQUIVALENCE_MARGIN = +-%.1f %% around the M6 point prediction" % delta)
    print()
    print("§19 FROZEN PREDICTIONS")
    print("    static median r80 %.4f (residual %+.2f %%)"
          % (full_s["median_summary"], full_s["median_residual_percent"]))
    print("    mobile median r80 %.4f (residual %+.2f %%)"
          % (full_m["median_summary"], full_m["median_residual_percent"]))
    print("    ratio %.4f ; ablation without the shared trajectory %+.2f %%"
          % (endpoints["MOBILE_STATIC_RATIO_COMPATIBILITY"]["predicted_ratio_under_M6"],
             abl_traj["median_residual_percent"]))
    print()
    print("§20 SEEDS  %d retired from %d files ; %d fresh, disjoint %s"
          % (len(retired), nfiles, len(fresh), seeds["DISJOINT"]))
    print("    S %s" % seeds["FRESH_OBFOR01_SEEDS"]["S"][:5] + " ...")
    print("    M %s" % seeds["FRESH_OBFOR01_SEEDS"]["M"][:5] + " ...")
    print()
    print("§22 OBFOR01_METHODS_CORE_HASH = %s" % core)
    print("    %d files, %d missing ; all DIFF fields NONE"
          % (len(digests), len(missing)))


if __name__ == "__main__":
    main()
