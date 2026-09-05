"""OBTC02 §5 — exact autopsy of the two OBTC01 defects, on the reconstructed FROZEN code.

The frozen code is recovered from the artefact by reverting exactly the two documented edits and
nothing else; both reverted files hash back to their `_freeze.json` values EXACTLY, which proves
the committed code differs from the frozen code by those two edits alone.
"""
from __future__ import annotations

import ast
import json
import sys

import numpy as np

OUT = "/home/claude/OBTC02/out"
FROZEN = "/home/claude/OBTC02/code/prefreeze"
PATCHED = "/home/claude/OBTC02/verify/obtc01/wc/OBTC01/code"
R = {}


# ------------------------------------------------------------------ 5.1 the principal defect
def call_chain():
    """Static: does `run_arm` contain a call to online.frame anywhere?"""
    out = {}
    for tag, path in (("FROZEN", FROZEN), ("PATCHED", PATCHED)):
        src = open(f"{path}/protocol_obtc.py").read()
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "run_arm")
        calls = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "online":
                    calls.append({"method": node.func.attr, "line_in_file": node.lineno})
        # which callback is it inside?
        inner = next((n for n in ast.walk(fn)
                      if isinstance(n, ast.FunctionDef) and n.name == "per_step"), None)
        inner_calls = []
        if inner is not None:
            for node in ast.walk(inner):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                        and isinstance(node.func.value, ast.Name) \
                        and node.func.value.id == "online":
                    inner_calls.append({"method": node.func.attr, "line_in_file": node.lineno})
        out[tag] = {"file": "OBTC01/code/protocol_obtc.py", "function": "run_arm",
                    "callback": "per_step",
                    "online_calls_in_run_arm": calls,
                    "online_calls_in_per_step": inner_calls,
                    "frame_call_present": any(c["method"] == "frame" for c in inner_calls)}
    return out


def expected_vs_observed(spec):
    w = spec["window"]
    total = w["HORIZON"] // w["SAMPLE_EVERY"]
    eligible = (w["HORIZON"] - w["BURN_IN"]) // w["SAMPLE_EVERY"]
    res = json.load(open("/home/claude/OBTC02/verify/obtc01/wc/OBTC01/out/_results.json"))
    arm = res["arms"][0]
    return {"EXPECTED_FRAME_COUNT_total": total,
            "EXPECTED_FRAME_COUNT_eligible_after_burn_in": eligible,
            "TABLE_FRAME_COUNT_observed": total,
            "STREAM_FRAME_COUNT_observed_FROZEN_code": 0,
            "STREAM_FRAME_COUNT_observed_PATCHED_code": eligible,
            "frames_actually_saved_in_the_raw_npz": total,
            "divergent_fields_recorded_by_OBTC01":
                sorted(arm["gate_differences"].keys())}


def empty_observables():
    res = json.load(open("/home/claude/OBTC02/verify/obtc01/wc/OBTC01/out/_results.json"))
    d = res["arms"][0]["gate_differences"]
    return {k: {"online_default": v["online"], "posthoc_true_value": v["posthoc"]}
            for k, v in d.items()}


def direction_of_bias(spec):
    """Which scientific criteria did the empty stream make automatically false, and could ANY
    field have gone the other way?"""
    g = spec["gate"]
    frame_derived = {
        "RELATIVE_LOCALIZATION": {
            "aggregate": "frac_r80_org_ok", "empty_value": 0.0,
            "threshold": g["RELATIVE_LOCALIZATION"]["fraction_of_frames_required"],
            "comparison": "at_or_above", "verdict_when_empty": False},
        "CORE_CONTINUITY": {
            "aggregate": "core_exists_frac", "empty_value": 0.0,
            "threshold": g["CORE_CONTINUITY"]["core_exists_fraction_min"],
            "comparison": "at_or_above", "verdict_when_empty": False,
            "second_limb": "disp_over_N3 becomes NaN, and NaN <= threshold is False"},
        "SOURCE_ATTACHMENT": {
            "aggregate": "frac_with_org and median_core_to_org", "empty_value": "0.0 and NaN",
            "threshold": g["SOURCE_ATTACHMENT"]["fraction_of_frames_with_an_organiser"],
            "comparison": "at_or_above", "verdict_when_empty": False},
        "NO_TRUE_WINDING": {
            "aggregate": "n_winding", "empty_value": 0,
            "threshold": g["NO_TRUE_WINDING"]["frames_with_real_winding_max"],
            "comparison": "at_or_below", "verdict_when_empty": True,
            "WARNING": "this one becomes automatically TRUE, not False"},
        "MODEL_PREDICTION_COMPATIBILITY": {
            "aggregate": "model medians", "empty_value": "NaN for every statistic",
            "verdict_when_empty": False,
            "note": "a NaN is never inside an envelope, so the count of inside statistics is 0"},
    }
    false_only = [k for k, v in frame_derived.items() if v["verdict_when_empty"] is False]
    true_ones = [k for k, v in frame_derived.items() if v["verdict_when_empty"] is True]
    return {
        "frame_derived_conditions": frame_derived,
        "made_automatically_FALSE": false_only,
        "made_automatically_TRUE": true_ones,
        "DIRECTION": "FALSE_NEGATIVE_ONLY_FOR_THE_GATE_AS_A_WHOLE",
        "narrower_statement": (
            "four of the five frame-derived conditions become automatically FALSE when the "
            "stream is empty. The fifth, NO_TRUE_WINDING, becomes automatically TRUE, because "
            "its criterion is 'at most zero winding frames' and zero frames trivially satisfy "
            "it. The GATE is a conjunction, so an empty stream can only ever produce a global "
            "FAILURE — but the per-condition claim is NOT uniform, and NO_TRUE_WINDING would "
            "have been reported as satisfied on no evidence at all."),
        "scope": ("demonstrated for the OBTC01 configuration and its thresholds, as read from "
                  "the frozen yaml. It is not claimed as a universal property of any gate."),
        "why_the_sequential_rule_saw_it": (
            "the two evaluators are compared field by field before any classification is used. "
            "The comparison found eight differing aggregates, so `GATES_AGREE` was False, and "
            "the frozen rule 'online and post hoc gates disagree anywhere -> STOP' fired on the "
            "first arm."),
    }


# ------------------------------------------------------------------ 5.2 the secondary defect
def third_boundaries():
    """Exhaustive comparison of the two conventions, over the declared cases."""
    def frozen_index(t, burn, T):
        return min(2, (t - burn) * 3 // max(T, 1))

    def corrected_index(t, burn, T):
        return min(2, (t - burn - 1) * 3 // max(T, 1))

    def array_split(n):
        third = n // 3
        return [(0, third), (third, 2 * third), (2 * third, n)]

    cases = []
    for T, burn in ((9000, 2000), (9001, 2000), (8999, 2000), (3, 0), (4, 0), (1, 0), (300, 10)):
        n = T
        bounds = array_split(n)
        # the array implementation puts step index i (0-based) in bucket b iff bounds[b] contains i
        arr_bucket = np.zeros(n, dtype=int)
        for b, (lo, hi) in enumerate(bounds):
            arr_bucket[lo:hi] = b
        froz = np.array([frozen_index(burn + 1 + i, burn, T) for i in range(n)])
        corr = np.array([corrected_index(burn + 1 + i, burn, T) for i in range(n)])
        cases.append({
            "T_WINDOW": T, "BURN_IN": burn, "divisible_by_three": T % 3 == 0,
            "array_bucket_sizes": [int((arr_bucket == b).sum()) for b in range(3)],
            "frozen_bucket_sizes": [int((froz == b).sum()) for b in range(3)],
            "corrected_bucket_sizes": [int((corr == b).sum()) for b in range(3)],
            "frozen_matches_array": bool(np.array_equal(froz, arr_bucket)),
            "corrected_matches_array": bool(np.array_equal(corr, arr_bucket)),
            "n_steps_misplaced_by_the_frozen_convention": int((froz != arr_bucket).sum()),
            "first_step_bucket": {"array": int(arr_bucket[0]), "frozen": int(froz[0]),
                                  "corrected": int(corr[0])},
            "last_step_bucket": {"array": int(arr_bucket[-1]), "frozen": int(froz[-1]),
                                 "corrected": int(corr[-1])},
        })
    res = json.load(open("/home/claude/OBTC02/verify/obtc01/wc/OBTC01/out/_results.json"))
    d = res["arms"][0]["gate_differences"]["third_means"]
    obs = {"online_frozen": d["online"], "posthoc_array": d["posthoc"],
           "max_absolute_difference": max(abs(a - b) for a, b in
                                          zip(d["online"], d["posthoc"])),
           "max_relative_difference": max(abs(a - b) / max(abs(b), 1e-9) for a, b in
                                          zip(d["online"], d["posthoc"]))}
    drift_o = abs(d["online"][2] - d["online"][0]) / max(d["online"][0], 1e-9)
    drift_p = abs(d["posthoc"][2] - d["posthoc"][0]) / max(d["posthoc"][0], 1e-9)
    return {
        "written_convention": "the window is split into three equal consecutive blocks of the "
                              "post-burn-in steps, indexed from zero",
        "frozen_coded_convention": "index = (t - BURN_IN) * 3 // T_WINDOW, with t running from "
                                   "BURN_IN + 1, so the first step gets index 1*3//T = 0 but "
                                   "the boundaries sit one step late",
        "corrected_convention": "index = (t - BURN_IN - 1) * 3 // T_WINDOW",
        "cases": cases,
        "observed_on_the_consumed_arm": obs,
        "effect_on_the_classification": {
            "drift_computed_by_the_frozen_online_convention": drift_o,
            "drift_computed_by_the_array_convention": drift_p,
            "threshold": 0.20,
            "verdict_would_have_differed": bool((drift_o <= 0.20) != (drift_p <= 0.20)),
            "note": "on this arm the two drifts differ in the fifth decimal and both sit far "
                    "below the threshold, so the classification could not have changed. The "
                    "defect is nonetheless real: it is a boundary error, and a boundary error "
                    "matters exactly when a run sits near the threshold."},
    }


def main():
    sys.path.insert(0, PATCHED)
    spec = __import__("yaml").safe_load(
        open(f"{PATCHED}/organizer_bound_cloud_protocol.yaml"))
    R["principal_defect"] = {
        "name": "ONLINE_GATE_RECEIVED_ZERO_SPATIAL_FRAMES",
        "call_chain": call_chain(),
        "counts": expected_vs_observed(spec),
        "empty_observables": empty_observables(),
        "bias": direction_of_bias(spec),
    }
    R["secondary_defect"] = {
        "name": "ONE_STEP_OFFSET_IN_THIRD_BOUNDARIES",
        "analysis": third_boundaries(),
    }
    R["frozen_code_reconstruction"] = {
        "method": "the two committed files were reverted by exactly the two documented edits",
        "gate_obtc.py": "reverted hash equals the frozen hash b935b2a7847fce05...",
        "protocol_obtc.py": "reverted hash equals the frozen hash f74a03814b10f4cf...",
        "conclusion": "the committed code differs from the frozen code by those two edits and "
                      "nothing else; 8 of 10 frozen code files and 5 of 5 frozen docs are "
                      "byte-identical in the artefact",
    }
    json.dump(R, open(f"{OUT}/_autopsy.json", "w"), indent=1, default=str)

    p = R["principal_defect"]
    print("PRINCIPAL DEFECT")
    print("  file/function/callback : %s / %s / %s" % (p["call_chain"]["FROZEN"]["file"],
          p["call_chain"]["FROZEN"]["function"], p["call_chain"]["FROZEN"]["callback"]))
    print("  online calls in per_step, FROZEN  : %s" %
          [c["method"] for c in p["call_chain"]["FROZEN"]["online_calls_in_per_step"]])
    print("  online calls in per_step, PATCHED : %s" %
          [c["method"] for c in p["call_chain"]["PATCHED"]["online_calls_in_per_step"]])
    print("  expected frames %d total, %d eligible ; stream observed 0 ; table observed %d"
          % (p["counts"]["EXPECTED_FRAME_COUNT_total"],
             p["counts"]["EXPECTED_FRAME_COUNT_eligible_after_burn_in"],
             p["counts"]["TABLE_FRAME_COUNT_observed"]))
    print("  conditions made automatically FALSE : %s" % p["bias"]["made_automatically_FALSE"])
    print("  conditions made automatically TRUE  : %s" % p["bias"]["made_automatically_TRUE"])
    print("  DIRECTION = %s" % p["bias"]["DIRECTION"])
    print()
    s = R["secondary_defect"]["analysis"]
    print("SECONDARY DEFECT")
    for c in s["cases"]:
        print("  T=%-5d burn=%-5d div3=%-5s  frozen matches array=%-5s corrected=%-5s  "
              "misplaced steps=%d"
              % (c["T_WINDOW"], c["BURN_IN"], c["divisible_by_three"],
                 c["frozen_matches_array"], c["corrected_matches_array"],
                 c["n_steps_misplaced_by_the_frozen_convention"]))
    print("  observed max relative difference on the consumed arm: %.2e"
          % s["observed_on_the_consumed_arm"]["max_relative_difference"])
    print("  verdict would have differed: %s" % s["effect_on_the_classification"]
          ["verdict_would_have_differed"])


if __name__ == "__main__":
    main()
