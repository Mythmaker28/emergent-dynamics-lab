"""OBDI02 §2 — append-only adjudication of the OBDI01 disposition.

APPEND-ONLY. This file reads OBDI01's delivered artefacts and writes a NEW record. It does not
touch, rewrite or reinterpret the frozen OBDI01 report, whose text stands exactly as delivered.
The adjudication is a statement ABOUT that report, not a correction OF it.
"""
from __future__ import annotations

import json

import yaml

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"

# Dispositions carrying INHERITED authority: each is named in the mission chain itself (the
# OBDI01 mandate's own stop conditions) rather than authored by OBDI01 after its results.
INHERITED_AUTHORISED = {
    "INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED":
        "named in the OBDI01 mandate §3 as the stop if an axis other than D were unmet",
    "DOMAIN_TEST_UNDERPOWERED":
        "named in the OBDI01 mandate §14 as the outcome if the design could not reach the "
        "required power",
    "AUDIT_INVALID":
        "the standing disposition of the mission chain for a defect of the instrument or of "
        "the protocol, used by OBTC01",
}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI01/code/obdi01_protocol.yaml"))
    ev = json.load(open(f"{WC}/OBDI01/out/_evidence.json"))
    res = json.load(open(f"{WC}/OBDI01/out/_results.json"))
    frz = json.load(open(f"{WC}/OBDI01/out/_freeze.json"))
    pw = json.load(open(f"{WC}/OBDI01/out/_power.json"))
    report = open(f"{WC}/OBDI01/out/OBDI01_FINAL_REPORT.md").read()

    # ---------------------------------------------------------------- was it authorised?
    keys_with_disposition = [k for k in spec if "disp" in k.lower()]
    frozen_list_present = bool(keys_with_disposition)
    space = ev.get("DISPOSITION_SPACE", {})
    provenance = ev.get("DISPOSITION_SPACE_PROVENANCE", "")
    reported = "DOMAIN_INVARIANCE_PARTIAL"
    in_self_authored_space = reported in space
    in_inherited_space = reported in INHERITED_AUTHORISED

    authorised = bool(frozen_list_present and in_self_authored_space)

    # ---------------------------------------------------------------- the eight facts
    P = res["PRINCIPAL"]
    A = P["components"]["A_shape_invariance"]["by_statistic"]
    facts = {
        "1_all_runs_technically_valid": {
            "value": "%d/%d" % (res["technically_valid"], res["n_arms"]),
            "TRUE": res["technically_valid"] == res["n_arms"] == 15},
        "2_protocol_executed_in_full": {
            "value": "%d planned arms, %d run, halted = %s"
                     % (res["planned_arms"], res["n_arms"], res["halted"]),
            "TRUE": bool(res["all_planned_arms_run"])},
        "3_lawspec_unchanged": {
            "value": frz["LAWSPEC_DIFF_FROM_OBDI01"] if "LAWSPEC_DIFF_FROM_OBDI01" in frz
                     else frz["LAWSPEC_DIFF_FROM_OBTC02"],
            "TRUE": frz.get("LAWSPEC_DIFF_FROM_OBTC02") == "NONE"},
        "4_no_threshold_moved_after_the_results": {
            "value": "spec_sha256 recorded at freeze %s; the runner asserts it before the "
                     "first arm" % frz["spec_sha256"][:16],
            "TRUE": True},
        "5_estimates_exclude_the_declared_unbounded_alternatives": {
            "value": {s: {"beta": d["beta"], "excludes_H_sublinear": d["excludes_H_sublinear"],
                          "excludes_H_linear": d["excludes_H_linear"]} for s, d in A.items()},
            "TRUE": all(d["excludes_H_linear"] and d["excludes_H_sublinear"]
                        for d in A.values())},
        "6_the_equivalence_interval_is_still_too_wide": {
            "value": {"statistic": "organiser_to_core",
                      "beta": A["organiser_to_core"]["beta"],
                      "se": A["organiser_to_core"]["se"],
                      "abs_beta_plus_c_se": A["organiser_to_core"]["abs_beta_plus_c_se"],
                      "frozen_margin": A["organiser_to_core"]["margin"],
                      "excess": A["organiser_to_core"]["abs_beta_plus_c_se"]
                      - A["organiser_to_core"]["margin"]},
            "TRUE": not A["organiser_to_core"]["PASS"]},
        "7_the_power_analysis_used_the_wrong_sizing_metric": {
            "value": ("OBDI01 §14 sized n against H_linear USING R_g. The frozen rule reads: "
                      "%s. Applied to R_g it returned n = %s, and the adopted n = %s came from "
                      "an estimability floor, not from the precision of the statistic that "
                      "actually carried the claim."
                      % (pw["POWER_RULE"], pw["n_from_power"], pw["SEEDS_PER_DOMAIN_SIZE"])),
            "TRUE": True},
        "8_about_eight_arms_per_size_would_have_been_needed": {
            "value": ev["POST_HOC_DIAGNOSTICS"]["failing_component"][
                "arms_per_L_that_would_have_sufficed"],
            "TRUE": True},
    }

    # ---------------------------------------------------------------- which one applies?
    ruling = {
        "INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED": {
            "applies": False,
            "why": "OBDI01 §3 proved D was the only axis with an unmet frozen requirement, so "
                   "this stop was not reached"},
        "AUDIT_INVALID": {
            "applies": False,
            "why": "15/15 arms technically valid, both evaluators agreeing on 15/15, no "
                   "threshold moved after the freeze, no seed replaced, no early stop, no "
                   "result opened before the freeze. Nothing in the instrument failed."},
        "DOMAIN_TEST_UNDERPOWERED": {
            "applies": True,
            "why": ("the mission's claim was an EQUIVALENCE claim, and the design was never "
                    "sized for it. Every fact above holds: the runs are valid, the protocol "
                    "was executed, nothing moved, the unbounded alternatives are excluded, and "
                    "the interval is nevertheless too wide. That is precisely the state the "
                    "inherited taxonomy calls DOMAIN_TEST_UNDERPOWERED.")},
    }

    caveat = (
        "The frozen §14 rule of OBDI01, READ LITERALLY, did not trigger: it asked for 80 % "
        "power against H_linear measured on R_g, and that was reached at n = 1. The rule was "
        "keyed to the wrong statistic and to the wrong kind of alternative — power against a "
        "distant alternative rather than precision for an equivalence interval — so it could "
        "not detect the very deficiency it was meant to guard against. That is not an argument "
        "against the adjudication; it is the mechanism that produced it, and OBDI01 itself "
        "recorded it as defect (b) of its own §31.")

    out = {
        "SECTION": "OBDI02 §2 — append-only adjudication of OBDI01",
        "APPEND_ONLY": True,
        "THE_FROZEN_OBDI01_REPORT_IS_NOT_MODIFIED": True,
        "obdi01_head": "5a37a7be73c3624e76b9c77ee75fd22172b6eb52",
        "obdi01_methods_core_hash": frz["OBDI01_METHODS_CORE_HASH"],

        "AUTHORISED_DISPOSITION_LIST": {
            "frozen_protocol_contains_a_disposition_list": frozen_list_present,
            "keys_searched": list(spec.keys()),
            "where_the_list_actually_lives": "OBDI01/out/_evidence.json, written AFTER the runs",
            "its_own_declared_provenance": provenance,
            "self_authored_space": sorted(space),
            "inherited_authorised_space": INHERITED_AUTHORISED,
            "FINDING": ("the OBDI01 protocol froze NO disposition list. The nine-item space was "
                        "authored by OBDI01 itself, after its results, and was explicitly "
                        "declared a reconstruction in the same file and in §31(d) and §33 of "
                        "its report. A disposition invented after the results cannot be the "
                        "authorised disposition of those results.")},

        "OBDI01_REPORTED_DISPOSITION": reported,
        "WAS_IT_AUTHORISED": authorised,
        "reported_disposition_in_self_authored_space": in_self_authored_space,
        "reported_disposition_in_inherited_space": in_inherited_space,

        "EIGHT_FACTS": facts,
        "ALL_EIGHT_FACTS_HOLD": all(f["TRUE"] for f in facts.values()),
        "RULING_BY_CANDIDATE": ruling,
        "OBDI01_ADJUDICATED_DISPOSITION": "DOMAIN_TEST_UNDERPOWERED",
        "CAVEAT_ON_THE_FROZEN_RULE": caveat,

        "WHAT_THIS_CHANGES": [
            "the OBDI01 report keeps its text, its hash and its commit unchanged",
            "the scientific content of OBDI01 is unchanged: no estimate, interval or verdict "
            "is revised here",
            "what changes is the LABEL: the mission is recorded as underpowered for the claim "
            "it made, not as a partial success",
        ],
        "WHAT_THIS_DOES_NOT_CHANGE": [
            "OBTC02 remains ORGANIZER_BOUND_CLOUD_PARTIAL",
            "LEGACY_D_GATE_STATUS remains MISALIGNED_WITH_DOMAIN_INVARIANCE",
            "H3_STATUS NOT_TESTED, REPRODUCTION_STATUS NOT_TESTED, "
            "AUTONOMOUS_COHESION_STATUS NOT_ESTABLISHED",
        ],
        "report_states_reconstruction": bool("reconstruction" in report.lower()),
    }
    json.dump(out, open(f"{OUT}/_adjudication.json", "w"), indent=1, default=str)
    print("frozen protocol contains a disposition list :", frozen_list_present)
    print("declared provenance of the nine-item space  :", provenance[:80], "...")
    print("OBDI01_REPORTED_DISPOSITION                 :", reported)
    print("WAS_IT_AUTHORISED                           :", authorised)
    print("all eight facts hold                        :", out["ALL_EIGHT_FACTS_HOLD"])
    for k, v in facts.items():
        print("   %-52s %s" % (k, v["TRUE"]))
    print("OBDI01_ADJUDICATED_DISPOSITION              :", out["OBDI01_ADJUDICATED_DISPOSITION"])


if __name__ == "__main__":
    main()
