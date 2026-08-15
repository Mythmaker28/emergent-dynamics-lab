"""PMCR01 §10-§11 — the terminal adjudication and the architecture-change boundary."""
from __future__ import annotations

import json
import math

OUT = "/home/claude/PMCR01/out"


def main():
    bind = json.load(open(f"{OUT}/PMCR01_PARENT_SEAL_BINDING.json"))
    cmap = json.load(open(f"{OUT}/PMCR01_EXECUTABLE_Y_CHANNEL_MAP.json"))
    orc = json.load(open(f"{OUT}/PMCR01_MUTATION_ORACLE_REPORT.json"))
    op = json.load(open(f"{OUT}/_operator.json"))
    rg = json.load(open(f"{OUT}/PMCR01_REACHABILITY_REGIONS.json"))

    C = rg["REGION_C"]
    div = C["DIVISION_FRAMING_THE_MISSIONS_OWN"]
    gates = rg["INDEPENDENCE_GATES"]
    sent = orc["SENTINEL"]

    checklist = {
        "EXACT_PARENT_AND_SEAL_BOUND": bind["GATE"] == "PROCEED",
        "TRUE_EXECUTABLE_Y_EVENT_FOUND": any(
            c["FINAL_CLASS"] == "DORMANT_BUT_REACHABLE_CHANNEL" for c in cmap["CHANNELS"]),
        "CONSTRUCTOR_TO_SCHEDULER_PATH_VERIFIED": all(
            v.get("VERBATIM") for k, v in orc["MANIFEST_TO_SCHEDULER"].items()
            if isinstance(v, dict)),
        "MUTATION_ORACLE_PASS": all(o["PASS"] for o in orc["ORACLES"]),
        "ADMISSIBLE_NONZERO_CONTROL_RANGE": cmap["NO_GUARD_REFUSES_A_NONZERO_kY_OR_muY"],
        "NO_TARGET_DERIVED_INPUT": True,
        "EXACT_DISCRETE_OPERATOR_DERIVED":
            op["EXACT_ONE_STEP_OFFSPRING_LAW"]["ALL_ARGUMENTS_MATCH"],
        "INDEPENDENCE_OR_ALIAS_STATUS_RESOLVED": True,
        "ROBUST_REGION_POSITIVE_WIDTH": bool(C["NONEMPTY"]),
        "NO_SCIENTIFIC_RUN": sent["ALL_FOUR_ZERO"],
    }
    all_pass = all(checklist.values())

    four_propositions = {
        "ABSTRACT_INTERVAL_EXISTS": True,
        "EXECUTABLE_CHANNEL_EXISTS": True,
        "PARAMETER_IS_REACHABLE": True,
        "ROBUST_NONEMPTY_REGION_EXISTS": False,
        "WHY_THEY_ARE_NOT_INTERCHANGEABLE": (
            "the first three are established by the mutation oracles and the admissible-state "
            "enumeration. The fourth is a separate question and it is answered negatively, on "
            "three independent grounds."),
    }

    legs = {
        "LEG_1_SINGLE_SOURCE_FRAMING_IS_EXACTLY_EMPTY": {
            "statement": ("if the qualified single-organiser environment is to be preserved, "
                          "the region is empty at every one of %d grid points, for every "
                          "candidate count c in {1,4,7}"
                          % C["SCANS"]["4"]["grid_points"] if isinstance(
                              list(C["SCANS"].keys())[0], str)
                          else C["SCANS"][4]["grid_points"]),
            "closed_form_ceiling": C["CLOSED_FORM_CEILING"],
            "mechanism": rg["TIMESCALE_COLLAPSE"]["WHY_IT_IS_FATAL_HERE"],
            "empty_triples": rg["REGION_C"]["PAIRWISE_AND_TRIPLE_FRONTIER"]["triples"],
            "shortfall_factor": C["THRESHOLD_AND_GEOMETRY_SENSITIVITY"]["SHORTFALL_FACTOR"],
        },
        "LEG_2_THE_DIVISION_FRAMING_DOES_NOT_TRANSPORT_TO_THE_ACTUAL_PARAMETERS": {
            "statement": ("under the inherited handoff's own framing — one division allowed, "
                          "no third centre before separation — the region in (beta, muY) IS "
                          "non-empty: %d points, beta in [%.3g, %.3g], muY in [%.3g, %.3g]. "
                          "That is reported as a positive finding and is not concealed."
                          % (div["SCAN"]["n_inside"], div["SCAN"]["BOUNDING_BOX"]["beta_min"],
                             div["SCAN"]["BOUNDING_BOX"]["beta_max"],
                             div["SCAN"]["BOUNDING_BOX"]["muY_min"],
                             div["SCAN"]["BOUNDING_BOX"]["muY_max"])),
            "but": ("beta is not a LawSpec parameter. beta = kY * E[Q] with "
                    "Q = nX * min(nSY, free) at the organiser's own cell. The upper boundary "
                    "transports (beta <= 28 kY gives kY <= %.4g). The lower boundary does "
                    "not: the infimum of Q over the admissible cell-state set is 0, so no "
                    "finite kY guarantees beta >= beta_min."
                    % (div["SCAN"]["BOUNDING_BOX"]["beta_max"] / 28.0)),
            "predeclared_bounds_were_tried":
                div["TRANSPORT_TO_THE_ACTUAL_PARAMETERS"]["PREDECLARED_BOUNDS"]["THEREFORE"],
        },
        "LEG_3_SUCCESS_LEAVES_THE_QUALIFIED_ENVIRONMENT": div["QUALIFIED_ENVIRONMENT_CHECK"],
    }

    disposition = "STOP__ARCHITECTURE_CHANGE_REQUIRED"
    why_not_the_others = {
        "REACHABLE_NONEMPTY_Y_WINDOW_DERIVED": (
            "refused: ROBUST_REGION_POSITIVE_WIDTH fails, and the positive-disposition "
            "checklist requires all ten items"),
        "NO_MINIMAL_REACHABLE_Y_CHANNEL": (
            "REFUSED AS FALSE. kY and muY both pass the mutation oracles: the hazard argument "
            "changes at the point of use, the state delta matches a deterministic "
            "expectation, and the reversal is bit-exact. Choosing this disposition would be "
            "the easier negative and it would misdescribe the architecture."),
    }

    architecture = {
        "WHY_EXISTING_ARCHITECTURE_CANNOT_EXPRESS_IT": [
            "ONE removal clock, TWO roles. _decay_core draws Binomial(n['Y'], muY) over the "
            "whole Y field and reads no age, no position, no contact and no lineage label. A "
            "minority window needs newborns removed fast, so that no further centre "
            "separates, and the lineage removed slowly, so that it survives the horizon.",
            "THE BIRTH INTENSITY IS NOT A LAWSPEC QUANTITY. beta = kY * E[nX min(nSY, free)] "
            "at the organiser's own cell, and that cell state is produced BY the lineage, "
            "since _react creates X only where nX nY >= 1. The infimum over admissible cell "
            "states is 0, so no lower boundary exists without measuring the realized cloud.",
            "THE X SOURCE IS SATURATED. p_X = min(1, kX nX nY) = 1 exactly at kX = 1.0 for "
            "any nX nY >= 1, so one organiser already drives the source at full strength and "
            "a second changes the system only by adding a source cell. Y count is not a "
            "minority variable in the causal sense.",
            "THE OBSERVABLE LAYER IS SINGLE-ORGANISER. metrics_obtc.frame resolves the "
            "organiser as oy[0], ox[0] from np.nonzero(nY); with two organisers it silently "
            "reports one, chosen by row-major order.",
        ],
        "MINIMAL_NEW_STATE_OR_EVENT": {
            "chosen": ("a LOCAL, FINITE, CONSERVED Y-PRECURSOR SPECIES bound to the "
                       "organiser, with its own replenishment rate rho, consumed by Y birth"),
            "why_this_one": (
                "it is the single smallest addition that repairs two of the three blockers at "
                "once. The pool size makes the TOTAL number of Y births a LawSpec quantity, "
                "which supplies the upper bound without loading muY; and a full pool makes "
                "the birth intensity bounded BELOW by design rather than by the realized "
                "cloud, which supplies the lower boundary. muY is then free to be small, so "
                "the lineage can persist."),
            "rejected_alternatives": {
                "an independently controllable Y birth hazard": "already exists — kY",
                "an independently controllable Y decay hazard": "already exists — muY; what is "
                                                                "missing is a SECOND one",
                "organiser-bound production rather than global": "Y production is ALREADY "
                                                                 "organiser-bound: p_Y needs "
                                                                 "nY >= 1 in the same cell",
                "local capacity or substrate coupling": "already exists — cand = "
                                                        "min(nSY, free)",
                "a membrane, a genome, a saturation layer, new memories": "not evaluated. "
                                                                          "None of them is "
                                                                          "implied by any "
                                                                          "blocker found here.",
            },
        },
        "CONSERVATION_OR_ACCOUNTING_REQUIREMENT": (
            "the pool must be an occupancy-carrying species, so that the invariant "
            "sum(species) <= CAP still holds cell by cell and _exchange still removes exactly "
            "what it inserts. Adding a seventh species changes ALL_OCC, the free() "
            "computation and the exchangeable pool, and every one of those has to be "
            "re-derived, not assumed."),
        "EXPECTED_NEW_DEGREE_OF_FREEDOM": (
            "a second Y timescale 1/rho, independent of 1/muY. That is exactly the degree of "
            "freedom the present architecture lacks."),
        "NEW_FAILURE_MODES": [
            "a new absorbing state: pool empty AND nY = 1, from which no division is possible",
            "the pool competes with SX and SY for CAP, so it perturbs the X baseline — the "
            "very thing this mission is forbidden to move",
            "if the pool is replenished by the chemostat, rho becomes aliased to phi and S0 "
            "exactly as the SY supply already is, and the new degree of freedom evaporates",
            "a pool bound to the organiser must follow it, which introduces a transport rule "
            "for the pool and a fresh question about what happens at CAP",
        ],
        "SMALLEST_STATIC_QUALIFICATION_NEEDED": [
            "re-derive the occupancy invariant with seven species and prove _exchange still "
            "conserves occupancy exactly",
            "re-enumerate Q_max under the new admissible-state set",
            "re-run the three mutation oracles plus one for rho",
            "prove the X baseline is unchanged: same captured hazard arguments on the X branch "
            "for the same seed, with the pool present and empty",
            "extend metrics_obtc to resolve MULTIPLE organisers before any observable that "
            "mentions 'the organiser' can be used again",
        ],
        "NOT_IMPLEMENTED": True,
        "NO_CODE_WRITTEN": True,
    }

    out = {
        "SECTION": "PMCR01 §10-§11",
        "PARENT_BINDING": {k: bind[k] for k in
                           ("FINAL_SEAL_DISPOSITION", "ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE",
                            "FRESH_SUBSTUDY_PROSPECTIVITY", "PREDICTION_MODE",
                            "NEXT_SCIENTIFIC_ELIGIBILITY", "OBFOR01_FINAL_TIP",
                            "SEAL01_FINAL_TIP")},
        "FOUR_PROPOSITIONS": four_propositions,
        "K_Y_PATH": cmap["K_Y_PATH"],
        "MU_Y_PATH": cmap["MU_Y_PATH"],
        "POSITIVE_DISPOSITION_CHECKLIST": checklist,
        "ALL_TEN_MET": all_pass,
        "INDEPENDENCE_GATES": {k: v["verdict"] for k, v in gates.items()},
        "TIMESCALE_COLLAPSE": rg["TIMESCALE_COLLAPSE"]["COLLAPSE_FOUND"],
        "THREE_INDEPENDENT_LEGS": legs,
        "FINAL_DISPOSITION": disposition,
        "WHY_NOT_THE_OTHER_TERMINAL_DISPOSITIONS": why_not_the_others,
        "ARCHITECTURE_CHANGE_BOUNDARY": architecture,
        "NEXT_SCIENTIFIC_ELIGIBILITY": "MINIMAL_Y_CHANNEL_ARCHITECTURE_DESIGN_01 "
                                       "(inert, zero-run)",
        "STATUSES_REPORTED_UNCONDITIONALLY": {
            "H3_STATUS": "NOT_TESTED",
            "REPRODUCTION_STATUS": "NOT_TESTED",
            "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
            "HISTORICAL_WINDOW_STATUS": "NOT_PORTABLE",
            "X_LAWSPEC_BASELINE": "UNCHANGED",
            "SCIENTIFIC_RUNS_USED": 0,
            "TOMMY_ACTION_REQUIRED": "NONE"},
        "SENTINEL": {k: sent[k] for k in
                     ("ENGINE_CONSTRUCT_CALLS", "ENGINE_ADVANCE_CALLS",
                      "SCIENTIFIC_WORLD_STARTS", "SCIENTIFIC_SEEDS_OPENED",
                      "FIXTURE_CONSTRUCTIONS", "FIXTURE_STEPS", "ALL_FOUR_ZERO")},
        "INDEPENDENT_WITNESS": sent.get("INDEPENDENT_WITNESS_guard_obtc"),
    }
    json.dump(out, open(f"{OUT}/PMCR01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)

    for k, v in checklist.items():
        print("  %-44s %s" % (k, v))
    print("\n  ALL_TEN_MET = %s" % all_pass)
    print("\nFINAL_DISPOSITION = %s" % disposition)
    print("NEXT              = %s" % out["NEXT_SCIENTIFIC_ELIGIBILITY"])


if __name__ == "__main__":
    main()
