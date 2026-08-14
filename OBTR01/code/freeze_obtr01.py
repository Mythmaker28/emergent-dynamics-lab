"""OBTR01 §16, §22-§26 — the gate before any fresh run, the freeze, and the disposition.

The disposition of this mission is NOT chosen by this file. §3 established that OBDI02's one
protocol violation was exactly that: a post-run, rank-7 file selecting a label because the
frozen protocol had enumerated dispositions without freezing a rule to map outcomes onto them.
The correction is structural. The rule used here is the one the MANDATE states in §16 --

    if the original window is not reconstructible in the qualified LawSpec, record
    ORIGINAL_WINDOW_NOT_PORTABLE and run nothing

-- which is a rank-1 source written before any of this mission's analysis existed. This file
evaluates the antecedent and applies the rule; it does not choose.
"""
from __future__ import annotations

import hashlib
import json
import os

CODE = "/home/claude/OBTR01/code"
OUT = "/home/claude/OBTR01/out"
WC = "/home/claude/OBTR01/verify/obdca01/wc"

METHODS_CORE = [
    "kernels_obtr01.py", "corrections_obtr01.py", "portability_obtr01.py",
    "observables_obtr01.py", "timescales_obtr01.py", "capacity_obtr01.py",
    "historical_obtr01.py", "window_obtr01.py", "deviation_obtr01.py",
    "provenance_obtr01.py", "recover_mtw01.py", "freeze_obtr01.py",
]
INHERITED_CORE = [
    (f"{WC}/OBDI02/code/obdi02_protocol.yaml", "obdi02_protocol.yaml"),
    (f"{WC}/OBTC02/code/obtc02_protocol.yaml", "obtc02_protocol.yaml"),
    (f"{WC}/OBTC02/code/source_operator.py", "source_operator.py"),
    (f"{WC}/OBTC02/code/protocol_obtc02.py", "protocol_obtc02.py"),
    (f"{WC}/OBTC02/code/metrics_obtc.py", "metrics_obtc.py"),
    (f"{WC}/OBTC02/code/engine_obtc.py", "engine_obtc.py"),
    (f"{WC}/OBTC02/code/guard_obtc.py", "guard_obtc.py"),
    (f"{WC}/ORR01/code/kinetics.py", "kinetics.py"),
    (f"{WC}/ORR01/code/lawspec_v2.py", "lawspec_v2.py"),
    (f"{WC}/ORR01/code/observe.py", "observe.py"),
]


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    dev = json.load(open(f"{OUT}/_obdi02_deviation_closure.json"))
    prov = json.load(open(f"{OUT}/_provenance.json"))
    mtw = json.load(open(f"{OUT}/_mtw01_recovery.json"))
    port = json.load(open(f"{OUT}/_portability.json"))
    corr = json.load(open(f"{OUT}/_corrections.json"))
    ker = json.load(open(f"{OUT}/_kernels_operator.json"))
    obs = json.load(open(f"{OUT}/_observables.json"))
    tau = json.load(open(f"{OUT}/_timescales.json"))
    cap = json.load(open(f"{OUT}/_capacity.json"))
    hist = json.load(open(f"{OUT}/_historical_raw.json"))
    win = json.load(open(f"{OUT}/_window_rederivation.json"))

    # ---------------------------------------------------------------- §22 the freeze
    digests, missing = {}, []
    for n in METHODS_CORE:
        p = os.path.join(CODE, n)
        if os.path.exists(p):
            digests[n] = sha256(p)
        else:
            missing.append(n)
    for p, n in INHERITED_CORE:
        if os.path.exists(p):
            digests[n] = sha256(p)
        else:
            missing.append(n)
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode())
        h.update(b"\0")
        h.update(digests[n].encode())
        h.update(b"\n")
    core = h.hexdigest()

    # ---------------------------------------------------------------- §16 the gate
    gate = [
        {"id": "G1_PROVENANCE",
         "requirement": "the inherited delivery reads back offline, self-contained",
         "evidence": prov["READBACK_STATUS"],
         "PASS": prov["READBACK_STATUS"] == "SELF_CONTAINED_SPLIT_DELIVERY_PASS"},
        {"id": "G2_INHERITED_EVIDENCE_CLOSED",
         "requirement": "the OBDI02 post-run adjudication deviation is closed append-only and "
                        "touched neither data, gate, freeze nor trajectories",
         "evidence": {"closure": dev["CLOSURE"], "blocking": dev["BLOCKING_CATEGORIES"]},
         "PASS": dev["CLOSURE"] == "CLOSED_APPEND_ONLY" and not dev["BLOCKING_CATEGORIES"]},
        {"id": "G3_HISTORICAL_ARTEFACTS_RECOVERED",
         "requirement": "the historical question is recoverable from digest-verified artefacts",
         "evidence": mtw["STATUS"],
         "PASS": mtw["STATUS"] == "HISTORICAL_ARTEFACTS_RECOVERED_AND_DIGEST_VERIFIED"},
        {"id": "G4_SYMBOLS_CLASSIFIED",
         "requirement": "every historical symbol carries a portability label and none is left "
                        "UNRESOLVED",
         "evidence": {"counts": port["COUNTS"], "unresolved": port["UNRESOLVED_ROWS"]},
         "PASS": not port["UNRESOLVED_ROWS"]},
        {"id": "G5_CORRECTIONS_REPRODUCED",
         "requirement": "every inherited correction is independently reproduced",
         "evidence": corr["ALL_REPRODUCED"], "PASS": bool(corr["ALL_REPRODUCED"])},
        {"id": "G6_KERNELS_VALIDATED",
         "requirement": "the kernels pass enumeration, unit mass, an independent "
                        "implementation, an engine Monte Carlo, moments, symmetries and the "
                        "diffusion convention",
         "evidence": {
             "enumeration": ker["KERNELS"]["ALGEBRA_MATCHES_BRUTE_FORCE_ENUMERATION"],
             "unit_mass": ker["KERNELS"]["MASS_IS_ONE"],
             "independent": ker["KERNELS"]["INDEPENDENT_IMPLEMENTATION"][
                 "AGREES_TO_MACHINE_PRECISION"],
             "engine_monte_carlo": ker["KERNELS"]["ENGINE_MONTE_CARLO"]["WITHIN_3_SIGMA"],
             "symmetries": ker["KERNELS"]["SYMMETRY_TESTS"]["K_X"]["ALL_WITHIN_TOL"],
             "convention_z": ker["KERNELS"]["DIFFUSION_CONVENTION_TEST"]["z_vs_corrected"]},
         "PASS": all([ker["KERNELS"]["ALGEBRA_MATCHES_BRUTE_FORCE_ENUMERATION"],
                      ker["KERNELS"]["MASS_IS_ONE"],
                      ker["KERNELS"]["INDEPENDENT_IMPLEMENTATION"][
                          "AGREES_TO_MACHINE_PRECISION"],
                      ker["KERNELS"]["ENGINE_MONTE_CARLO"]["WITHIN_3_SIGMA"],
                      ker["KERNELS"]["SYMMETRY_TESTS"]["K_X"]["ALL_WITHIN_TOL"],
                      abs(ker["KERNELS"]["DIFFUSION_CONVENTION_TEST"][
                          "z_vs_corrected"]) < 3.0])},
        {"id": "G7_OBSERVABLES_POPULATION_ROBUST",
         "requirement": "the registered primary observables are demonstrated robust in N, and "
                        "|C - Y| appears in no primary outcome",
         "evidence": obs["VERDICTS"],
         "PASS": all([obs["VERDICTS"]["M2_IS_POPULATION_ROBUST"],
                      obs["VERDICTS"]["W2_DEBIASED_IS_POPULATION_ROBUST"],
                      obs["VERDICTS"]["abs_C_minus_Y_IS_NOT"]])},
        {"id": "G8_TIMESCALES_DERIVED_AND_CLASSIFIED",
         "requirement": "the eight timescales are derived and every relation classified",
         "evidence": {"n_timescales": len(tau["EIGHT_TIMESCALES"]),
                      "n_relations": len(tau["RELATIONS"]),
                      "unresolved": [r["left"] + " vs " + r["right"] for r in tau["RELATIONS"]
                                     if r["CLASSIFICATION"] == "UNRESOLVED"],
                      "frozen_cross_check": tau["FROZEN_CROSS_CHECK"]["MATCHES"]},
         "PASS": (len(tau["EIGHT_TIMESCALES"]) == 8
                  and not [r for r in tau["RELATIONS"]
                           if r["CLASSIFICATION"] == "UNRESOLVED"]
                  and tau["FROZEN_CROSS_CHECK"]["MATCHES"])},
        {"id": "G9_CAPACITY_ERROR_BOUNDED",
         "requirement": "the capacity-refusal error is bounded for the registered observables",
         "evidence": {"status": cap["FULL_OPERATOR_ERROR"],
                      "worst_arm_bound": cap["CERTIFIED_BOUND"]["AT_THE_WORST_ARM"][
                          "additive_error_on_a_probability_observable"]},
         "PASS": cap["CERTIFIED_BOUND"]["AT_THE_WORST_ARM"][
             "additive_error_on_a_probability_observable"] < 0.05},
        {"id": "G10_ORIGINAL_WINDOW_RECONSTRUCTIBLE",
         "requirement": "the original window is reconstructible in the qualified LawSpec, i.e. "
                        "the reachable band of R_Y intersects the window",
         "evidence": {"WINDOW_STATUS": win["WINDOW_STATUS"],
                      "QUALIFIED_POINT_WINDOW_STATUS": win["QUALIFIED_POINT_WINDOW_STATUS"],
                      "reachable_intersects": win["REACHABLE_BAND_INTERSECTS_THE_WINDOW"],
                      "symbols_without_a_referent": len(
                          port["SYMBOLS_WITHOUT_A_REFERENT_HERE"])},
         "PASS": bool(win["REACHABLE_BAND_INTERSECTS_THE_WINDOW"]),
         "DECISIVE": True},
    ]
    passed = [g["id"] for g in gate if g["PASS"]]
    failed = [g["id"] for g in gate if not g["PASS"]]
    decisive_failed = [g["id"] for g in gate if not g["PASS"] and g.get("DECISIVE")]
    gate_open = not failed

    # ---------------------------------------------------------------- §24 the disposition
    rule = ("MANDATE §16, frozen before any analysis of this mission existed: if the original "
            "window is not reconstructible in the qualified LawSpec, record "
            "ORIGINAL_WINDOW_NOT_PORTABLE and run nothing.")
    if dev["BLOCKING_CATEGORIES"]:
        disposition = "INHERITED_EVIDENCE_NOT_CLOSED"
        why = "the §3 closure was refused: " + ", ".join(dev["BLOCKING_CATEGORIES"])
    elif not win["REACHABLE_BAND_INTERSECTS_THE_WINDOW"]:
        disposition = "ORIGINAL_WINDOW_NOT_PORTABLE"
        why = ("the antecedent of the frozen rule holds. The reachable band of R_Y at the "
               "qualified point is the single point {0}; the window is the open interval "
               "(0, 1.787e-4); the intersection is empty. Eight of the twenty-one historical "
               "symbols have no referent here, including both terms of the lower bound.")
    else:
        disposition = "GATE_OPEN__FRESH_VALIDATION_ELIGIBLE"
        why = "all ten gate conditions pass and the window is reconstructible"

    # ---------------------------------------------------------------- §25 secondary statuses
    secondary = {
        "H3_STATUS": "NOT_TESTED",
        "REPRODUCTION_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "SCIENTIFIC_RUNS_USED": 0,
        "SCIENTIFIC_RUNS_ALLOWED_AFTER_THE_GATE": 0,
        "OBDI02_POSTRUN_ADJUDICATION_DEVIATION":
            dev["OBDI02_POSTRUN_ADJUDICATION_DEVIATION"],
        "DEVIATION_DIRECTION": dev["DEVIATION_DIRECTION"],
        "FROZEN_EVIDENCE_STATUS": dev["FROZEN_EVIDENCE_STATUS"],
        "CUMULATIVE_CLOUD_EVIDENCE_STATUS": dev["CUMULATIVE_CLOUD_EVIDENCE_STATUS"],
        "OBDCA01_FORMAL_LIMITATION": dev["OBDCA01_FORMAL_LIMITATION"],
        "X_KERNEL_STATUS": ker["KERNELS"]["X_KERNEL_STATUS"],
        "ORGANIZER_KERNEL_STATUS": ker["KERNELS"]["ORGANIZER_KERNEL_STATUS"],
        "RELATIVE_KERNEL_STATUS": ker["KERNELS"]["RELATIVE_KERNEL_STATUS"],
        "UNBLOCKED_SOURCE_RESPONSE_OPERATOR": ker["OPERATOR"][
            "UNBLOCKED_SOURCE_RESPONSE_OPERATOR"],
        "FULL_SOURCE_RESPONSE_OPERATOR": ker["OPERATOR"]["FULL_SOURCE_RESPONSE_OPERATOR"],
        "FULL_OPERATOR_ERROR": cap["FULL_OPERATOR_ERROR"],
        "SOURCE_TERM_CLASSIFICATION": ker["OPERATOR"]["LINEARITY"]["CLASSIFICATION"],
        "SOURCE_CLASSIFICATION": corr["C5_SOURCE_CLASSIFICATION"]["SOURCE_CLASSIFICATION"],
        "SCALAR_CRITICALITY_STATUS": corr["C4_SCALAR_CRITICALITY"][
            "SCALAR_CRITICALITY_STATUS"],
        "WINDOW_STATUS": win["WINDOW_STATUS"],
        "QUALIFIED_POINT_WINDOW_STATUS": win["QUALIFIED_POINT_WINDOW_STATUS"],
        "FUTURE_SELECTED_DESIGN_POINT": "NOT_SELECTED_IN_THIS_MISSION",
        "TIMESCALE_DEGREES_OF_FREEDOM": tau["TIMESCALE_COLLAPSE"][
            "DEGREES_OF_FREEDOM_AS_TIMESCALES"],
        "SOURCE_QUASI_STATIC_STATUS": tau["COHERENCE"]["STATUS"],
        "PRIMARY_ATTACHMENT_METRIC": "FORBIDDEN__|C - Y| NOT USED IN ANY PRIMARY OUTCOME",
        "STATIC_VERSUS_MOBILE_KERNEL_DISCRIMINATION":
            "RELATIVE_KERNEL_SUPPORTED__ABSOLUTE_DEFICIT_OPEN",
        "SOURCE_OFF_RECOMPUTATION": ("REPRODUCED__ALL_THREE_WITHIN_ONE_SIGMA_OF_THE_"
                                     "ESTIMATOR_NULL_LAW"),
    }

    # ---------------------------------------------------------------- §26 next eligibility
    eligibility = {
        "NEXT_SCIENTIFIC_ELIGIBILITY": "NO_FRESH_RUN_AT_THE_QUALIFIED_POINT_FOR_THIS_QUESTION",
        "WHY": ("the question the window asks is about organiser birth and death. Neither "
                "exists in the qualified LawSpec, so no run at this point can answer it, "
                "however long. This is not an underpowered test; it is an absent mechanism."),
        "WHAT_WOULD_BE_ELIGIBLE": [
            {"target": "a new LawSpec with k_Y > 0 and mu_Y > 0",
             "status": "ANALYTICALLY_ELIGIBLE__REQUIRES_ITS_OWN_QUALIFICATION",
             "cost": "one expected division takes about 22 400 steps, twice the frozen "
                     "horizon, and the cumulative cloud qualification does not transfer",
             "blocking": "ORGANIZER_BOUND_SOURCE is exactly k_Y = 0, so this is a different "
                         "LawSpec"},
            {"target": "separating the timescales at fixed LawSpec",
             "status": "NOT_ELIGIBLE_AS_POSED",
             "why": "seven of the eight timescales are fixed rational multiples of 1/mu_X, so "
                    "no run can make them disagree. A design must move mu_X and p_hop "
                    "independently so that ell_X changes in lattice sites."},
            {"target": "the absolute radial deficit found in §15",
             "status": "ELIGIBLE_AT_THE_QUALIFIED_POINT",
             "why": "the static and mobile arms both sit below their absolute predictions, by "
                    "1.8 % and 6.1 %, while their RATIO matches. That residual is a genuine "
                    "open question at this point, it needs no new LawSpec, and the observables "
                    "registered in §9 are the right instrument for it."}],
        "FORBIDDEN_CLAIMS_REAFFIRMED": [
            "the system reproduces", "the system rebuilds an identity",
            "the system has a memory", "the system has an individuality",
            "the system is alive", "the system is self-bound",
            "the system has autonomous cohesion", "H3 is confirmed",
            "Kamimura-Kaneko is globally validated"],
    }

    out = {
        "SECTION": "OBTR01 §16, §22-§26",
        "FREEZE": {
            "OBTR01_METHODS_CORE_HASH": core,
            "METHODS_CORE_FILES": digests,
            "METHODS_CORE_MISSING": missing,
            "construction": "sha256 over, for each name in sorted order, "
                            "name | NUL | digest | LF",
            "PARENT": {"mission": "ORGANIZER-BOUND-DOMAIN-CONTRACT-AUDIT-01",
                       "head": "ad8f6bfb939ddb9a5b3b5c66155a3fdf118b2b29",
                       "disposition": "CUMULATIVE_CLOUD_QUALIFIED_UNDER_FROZEN_PRIMARY__"
                                      "ATTACHMENT_ESTIMAND_LIMITED"},
            "NOTE": ("this mission used ZERO scientific runs, so the freeze licenses future "
                     "work rather than sealing a run plan already executed. Every number in "
                     "the artefacts is a closed form, an exact discrete solve, or a "
                     "recomputation from delivered trajectories."),
        },
        "GATE": {"CONDITIONS": gate, "PASSED": passed, "FAILED": failed,
                 "DECISIVE_FAILURES": decisive_failed, "GATE_OPEN": gate_open,
                 "FRESH_RUNS_AUTHORISED": bool(gate_open)},
        "STOPPING_RULE": {
            "rule": "no scientific run may start unless all ten gate conditions pass",
            "SCIENTIFIC_RUNS_USED": 0,
            "STOPPED_AT": "§16, on G10",
            "EARLY_STOPPING": "NOT_APPLICABLE__NO_RUN_WAS_EVER_STARTED"},
        "DISPOSITION_SELECTION_RULE": rule,
        "RULE_RANK": "1 (the mandate itself), not a post-run file",
        "DISPOSITION": disposition,
        "WHY_THIS_DISPOSITION": why,
        "SECONDARY_STATUSES": secondary,
        "NEXT_ELIGIBILITY": eligibility,
    }
    json.dump(out, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)

    print("OBTR01_METHODS_CORE_HASH = %s" % core)
    print("  %d files in METHODS_CORE, %d missing" % (len(digests), len(missing)))
    print()
    print("%-38s %s" % ("GATE CONDITION", "PASS"))
    print("-" * 56)
    for g in gate:
        print("%-38s %s%s" % (g["id"], g["PASS"], "   <- DECISIVE" if g.get("DECISIVE") else ""))
    print("-" * 56)
    print("GATE_OPEN = %s   FRESH_RUNS_AUTHORISED = %s" % (gate_open, gate_open))
    print()
    print("selection rule (rank 1): %s" % rule)
    print("DISPOSITION = %s" % disposition)
    print()
    print("SECONDARY STATUSES")
    for k, v in secondary.items():
        print("  %-44s %s" % (k, v))
    print()
    print("NEXT_SCIENTIFIC_ELIGIBILITY = %s"
          % eligibility["NEXT_SCIENTIFIC_ELIGIBILITY"])


if __name__ == "__main__":
    main()
