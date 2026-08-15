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
    div = C["DIVISION_FRAMING_THE_LAUNCHERS_TIMING_CONSTRAINT"]
    stat = C["REGION_C_STATIC_BRANCH"]
    gates = rg["INDEPENDENCE_GATES"]
    sent = orc["SENTINEL"]
    sent_op = op.get("SENTINEL", {})

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

    # THE LOAD-BEARING LEG is branch-independent. Two subsidiary observations are branch-
    # conditional and are reported AS such, not as pillars of the disposition. The adversarial
    # review confirmed that the earlier draft rested on three legs of which two were scoped to
    # the mobile branch without saying so; this is the corrected structure.
    legs = {
        "LOAD_BEARING__BIRTH_INTENSITY_HAS_NO_CERTIFIABLE_LOWER_BOUND_IN_kY": {
            "statement": ("the minority-Y birth intensity is beta = kY * E[Q] with "
                          "Q = nX * min(nSY, free) at the organiser's OWN cell. The UPPER "
                          "boundary transports to the control (beta <= 28 kY, so "
                          "kY <= beta_max/28). The LOWER boundary does not: inf Q = 0 over the "
                          "admissible cell-state set (60.1 %% of admissible states have Q = 0), "
                          "so no finite kY guarantees beta >= beta_min."),
            "branch_independent": True,
            "why_it_is_the_same_fact_the_parent_found": (
                "E[Q] is a property of the realized cloud measure, not of the LawSpec. This is "
                "MARGINAL_DENSITY_CLOSURE = NOT_CLOSED, the very reason the parent had to "
                "MEASURE its birth-flux law and the reason its prediction is CONDITIONAL. "
                "PMCR01 is forbidden from using such a category-B measurement as a "
                "load-bearing input, so it cannot locate the lower edge of the (kY, muY) "
                "window. Condition 2 of the robust region asks for the persistence boundary to "
                "be exceeded WITH NUMERICAL MARGIN; a margin is a number, and this one does "
                "not exist from category A."),
            "predeclared_bounds_were_tried":
                div["TRANSPORT_TO_THE_ACTUAL_PARAMETERS"]["PREDECLARED_BOUNDS"]["THEREFORE"],
            "reviewer_could_not_locate_E_Q_either": True,
        },
        "SUBSIDIARY_MOBILE_BRANCH__SINGLE_SOURCE_REGION_IS_EMPTY": {
            "SCOPE": "condition M only (p_hop_Y = p_hop_X); NOT a general claim",
            "statement": ("in the mobile branch the single-source region is empty at every one "
                          "of %d grid points for c in {1,4,7}, because one removal clock muY "
                          "must be both large (kill newborns before they separate) and small "
                          "(let the lineage persist)."
                          % C["SCANS"]["4"]["grid_points"]),
            "closed_form_ceiling": C["CLOSED_FORM_CEILING"],
            "shortfall_factor": C["THRESHOLD_AND_GEOMETRY_SENSITIVITY"]["SHORTFALL_FACTOR"],
            "DOES_NOT_HOLD_IN_THE_STATIC_BRANCH": True,
        },
        "STATIC_BRANCH_COUNTER_REGION__REPORTED_OPENLY": {
            "SCOPE": "condition S (p_hop_Y = 0), used by 14 of OBFOR01's 28 fresh arms",
            "single_source_region_in_beta_muY_is_nonempty":
                stat["SINGLE_SOURCE_REGION_IN_(beta,muY)_IS_NONEMPTY"],
            "n_inside": stat["n_inside"], "box": stat["bounding_box"],
            "why_it_does_not_overturn_the_disposition":
                stat["WHY_IT_DOES_NOT_OVERTURN_THE_DISPOSITION"],
            "single_Y_branching_is_an_overestimate_here":
                stat["SINGLE_Y_BRANCHING_IS_AN_OVERESTIMATE_HERE"],
            "HONEST_CONCESSION": ("the mobile-branch 'two jobs for one clock' argument does "
                                  "NOT apply here; immobile offspring never separate. The "
                                  "static branch fails only for the load-bearing reason, and "
                                  "saying otherwise would overclaim."),
        },
        "SUBSIDIARY_MOBILE_BRANCH__SUCCESS_LEAVES_THE_QUALIFIED_ENVIRONMENT": {
            "SCOPE": "condition M only; in the static branch all Y share one cell so the "
                     "observable layer is unambiguous and this does NOT apply",
            "content": div["QUALIFIED_ENVIRONMENT_CHECK"],
        },
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
        "THE_SINGLE_BRANCH_INDEPENDENT_BLOCKER": (
            "THE BIRTH INTENSITY IS NOT A LAWSPEC QUANTITY. beta = kY * E[nX min(nSY, free)] "
            "at the organiser's own cell, and that cell state is produced BY the lineage, "
            "since _react creates X only where nX nY >= 1. inf Q = 0 over the admissible set, "
            "so no lower boundary in kY exists without measuring the realized cloud. This is "
            "the only reason that holds in BOTH the static and mobile branches, and it is the "
            "reason the disposition is STOP rather than REACHABLE."),
        "ADDITIONAL_MOBILE_BRANCH_BLOCKERS_NOT_LOAD_BEARING": [
            "ONE removal clock, TWO roles (condition M only). _decay_core draws "
            "Binomial(n['Y'], muY) over the whole Y field and reads no age, position, contact "
            "or lineage label, so newborns and founder share one clock. In the STATIC branch "
            "this dissolves: immobile offspring never separate.",
            "THE OBSERVABLE LAYER IS SINGLE-ORGANISER (condition M only). metrics_obtc.frame "
            "resolves the organiser as oy[0], ox[0] from np.nonzero(nY); with two SEPARATED "
            "organisers it silently reports one. In the static branch all Y share one cell, so "
            "np.nonzero returns one cell and this is not triggered.",
        ],
        "BRANCH_INDEPENDENT_STRUCTURAL_FACT": (
            "THE X SOURCE IS SATURATED. p_X = min(1, kX nX nY) = 1 exactly at kX = 1.0 for any "
            "nX nY >= 1, so one organiser already drives the source at full strength; a second "
            "changes the system only by adding a source cell once it separates. 'Minority in "
            "count' and 'minority in causal role' come apart. True in both branches."),
        "MINIMAL_NEW_STATE_OR_EVENT": {
            "chosen": ("a LOCAL, FINITE, CONSERVED Y-PRECURSOR SPECIES bound to the "
                       "organiser, with its own replenishment rate rho, consumed by Y birth"),
            "why_this_one": (
                "it targets the single LOAD-BEARING blocker directly. A full organiser-bound "
                "pool makes the Y birth intensity bounded BELOW by a LawSpec quantity (the "
                "pool size and rho) rather than by the realized co-located X count E[Q], which "
                "is exactly the un-locatable object. That supplies the missing lower boundary. "
                "It does NOT by itself fix the mobile-branch removal-clock tension; that is a "
                "condition-M problem and is secondary, since the static branch has no such "
                "tension yet still fails on the lower boundary."),
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
        "LEGS": legs,
        "DISPOSITION_RESTS_ON": ("one branch-independent load-bearing leg (birth intensity "
                                 "has no certifiable lower bound in kY); the two mobile-branch "
                                 "arguments and the static counter-region are reported but are "
                                 "NOT pillars of the disposition"),
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
        "SENTINEL_AGGREGATED_OVER_ALL_ANALYSIS_PROCESSES": {
            "mutation_oracles": {k: sent[k] for k in
                                 ("ENGINE_CONSTRUCT_CALLS", "ENGINE_ADVANCE_CALLS",
                                  "SCIENTIFIC_WORLD_STARTS", "SCIENTIFIC_SEEDS_OPENED",
                                  "FIXTURE_CONSTRUCTIONS", "FIXTURE_STEPS", "ALL_FOUR_ZERO")},
            "operator_derivation": {k: sent_op.get(k) for k in
                                    ("ENGINE_CONSTRUCT_CALLS", "ENGINE_ADVANCE_CALLS",
                                     "SCIENTIFIC_WORLD_STARTS", "SCIENTIFIC_SEEDS_OPENED",
                                     "FIXTURE_CONSTRUCTIONS", "FIXTURE_STEPS", "ALL_FOUR_ZERO")},
            "ALL_FOUR_ZERO_IN_EVERY_PROCESS": bool(sent["ALL_FOUR_ZERO"]
                                                   and sent_op.get("ALL_FOUR_ZERO", True))},
        "FILESYSTEM_WITNESS_no_raw_file_written":
            sent.get("FILESYSTEM_WITNESS_raw_dirs", {}).get("NO_RAW_FILE_WRITTEN"),
    }
    json.dump(out, open(f"{OUT}/PMCR01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)

    for k, v in checklist.items():
        print("  %-44s %s" % (k, v))
    print("\n  ALL_TEN_MET = %s" % all_pass)
    print("\n  static-branch counter-region nonempty in (beta,muY): %s (does not overturn)"
          % stat["SINGLE_SOURCE_REGION_IN_(beta,muY)_IS_NONEMPTY"])
    print("  sentinel all-four-zero in every process: %s ; no raw file written: %s"
          % (out["SENTINEL_AGGREGATED_OVER_ALL_ANALYSIS_PROCESSES"]
             ["ALL_FOUR_ZERO_IN_EVERY_PROCESS"],
             out["FILESYSTEM_WITNESS_no_raw_file_written"]))
    print("\nFINAL_DISPOSITION = %s" % disposition)
    print("NEXT              = %s" % out["NEXT_SCIENTIFIC_ELIGIBILITY"])


if __name__ == "__main__":
    main()
