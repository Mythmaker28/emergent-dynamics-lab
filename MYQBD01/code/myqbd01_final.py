"""MYQBD01 — consolidate the final disposition and answer the ten mandated questions."""
from __future__ import annotations

import json

OUT = "/home/claude/MYQBD01/out"


def main():
    bind = json.load(open(f"{OUT}/MYQBD01_PARENT_BINDING.json"))
    phase = json.load(open(f"{OUT}/MYQBD01_Q_PHASE_MAP.json"))
    inv = json.load(open(f"{OUT}/MYQBD01_RAW_DATA_INVENTORY.json"))
    temp = json.load(open(f"{OUT}/MYQBD01_TEMPORAL_DEPENDENCE.json"))
    fb = json.load(open(f"{OUT}/MYQBD01_FEEDBACK_BOUND.json"))
    oy = json.load(open(f"{OUT}/MYQBD01_ONE_Y_OPERATOR.json"))
    ty = json.load(open(f"{OUT}/MYQBD01_TWO_Y_OPERATOR.json"))
    reg = json.load(open(f"{OUT}/MYQBD01_DISCOVERY_REGION.json"))

    q = {
        "1_recorded_Q_matches_scheduler_event_phase":
            phase["PHASE"]["EXACT_IDENTITY"]["CLASSIFICATION"],
        "2_independent_information_28_arms_or_308000_frames": {
            "independent_unit": "28 arms (14 per branch)",
            "mean_integrated_autocorr_time_mobile": temp["MOBILE"]["mean_iat"],
            "reading": "the 308000 frames are strongly autocorrelated (IAT ~7-9); the "
                       "independent information is the 14 arm-level means per branch"},
        "3_beta_kY_EQ_sufficient": ty["REDUCTION"]["CLASSIFICATION"],
        "4_organiser_Q_describes_descendant_exposure":
            fb["SPATIAL"]["Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT"],
        "5_two_Y_operator_identifiable": ty["TWO_Y"]["TWO_Y_STATE_OPERATOR_STATUS"],
        "6_Y_feedback_controlled": {
            "classification": fb["FEEDBACK"]["CLASSIFICATION"],
            "controlled_for": fb["FEEDBACK"]["ERROR_IS_CONTROLLED_ONLY_FOR"]},
        "7_mobile_region_nonempty_across_all_14_arms":
            reg["POSITIVE_DISPOSITION_REQUIREMENTS"]["MOBILE_REGION_POSITIVE_WIDTH"],
        "8_prospective_Q_calibration_needed": True,
        "9_architecture_change_structurally_justified": False,
        "10_unique_next_eligibility": "PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01",
    }

    out = {
        "SECTION": "MYQBD01 FINAL DISPOSITION",
        "MISSION": "MINORITY-Y-Q-BOUND-DERIVATION-01",
        "PARENT_REPAIRED_TIP": bind["PARENT_REPAIRED_TIP_RESOLVED_FULL"],
        "ARMS_STATUS": "POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC",
        "EXACT_COUNTS": inv["EXACT_COUNTS_MATCH_REPORTED"],
        "Q_LEDGER_STATUS": phase["PHASE"]["EXACT_IDENTITY"]["CLASSIFICATION"],
        "SCALAR_Q_REDUCTION_STATUS": ty["REDUCTION"]["CLASSIFICATION"],
        "SPATIAL_ENVIRONMENT_STATUS": fb["SPATIAL"]["CLASSIFICATION"],
        "FROZEN_ENVIRONMENT_STATUS": fb["FEEDBACK"]["CLASSIFICATION"],
        "ONE_Y_OPERATOR_VERIFIED": oy["INDEPENDENT_VERIFICATION_vs_brute_force"]["MATCHES"],
        "TWO_Y_OPERATOR_STATUS": ty["TWO_Y"]["TWO_Y_STATE_OPERATOR_STATUS"],
        "MOBILE_DISCOVERY_REGION_STATUS": "NOT_CONSTRUCTIBLE_FROM_ORGANISER_ONLY_LEDGER",
        "STRUCTURAL_PRECLUSION_PROVED": reg["STRUCTURAL_PRECLUSION_CHECK"][
            "STRUCTURAL_PRECLUSION_PROVED"],
        "POSITIVE_DISPOSITION_REQUIREMENTS": reg["POSITIVE_DISPOSITION_REQUIREMENTS"],
        "EXACT_MISSING_ITEMS": reg["EXACT_MISSING_ITEMS"],
        "TEN_QUESTIONS": q,
        "FINAL_DISPOSITION": "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "NEXT_SCIENTIFIC_ELIGIBILITY": "PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01",
        "STATUSES_REPORTED_UNCONDITIONALLY": {
            "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
            "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
            "HISTORICAL_WINDOW_STATUS": "NOT_PORTABLE",
            "X_LAWSPEC_BASELINE": "UNCHANGED", "SCIENTIFIC_RUNS_USED": 0,
            "TOMMY_ACTION_REQUIRED": "NONE"},
    }
    json.dump(out, open(f"{OUT}/MYQBD01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)
    for k in ("Q_LEDGER_STATUS", "SCALAR_Q_REDUCTION_STATUS", "SPATIAL_ENVIRONMENT_STATUS",
              "FROZEN_ENVIRONMENT_STATUS", "TWO_Y_OPERATOR_STATUS",
              "MOBILE_DISCOVERY_REGION_STATUS", "STRUCTURAL_PRECLUSION_PROVED",
              "FINAL_DISPOSITION", "NEXT_SCIENTIFIC_ELIGIBILITY"):
        print("%-38s %s" % (k, out[k]))


if __name__ == "__main__":
    main()
