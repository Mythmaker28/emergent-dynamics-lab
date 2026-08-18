"""FLCR01 — adjudication of the review, updated disposition, review-and-repair ledger."""
from __future__ import annotations
import glob, hashlib, json, os
REPO = "/home/claude/edl"; OUT = f"{REPO}/FLCR01/out"; RV = "/home/claude/FLCR01/review"
J = lambda n: json.load(open(f"{OUT}/{n}"))


def main():
    rep = J("FLCR01_REPAIR.json")
    d = J("FLCR01_FINAL_DISPOSITION.json")
    rv = json.load(open(f"{RV}/FLCR01_ADVERSARIAL_REVIEW.json"))
    vb = rv.get("VERDICT_BLOCK", {})
    R3 = rep["R3_REGION_WITH_WORLD_LEVEL_UNCERTAINTY"]
    R4 = rep["R4_COMPOSITION_CORRECTION"]
    R2 = rep["R2_CHAIN_CALIBRATION"]

    d["REPAIR_ROUND"] = {
        "ROUNDS_AUTHORIZED": 1, "ROUNDS_USED": 1,
        "REVIEW_VERDICT": vb.get("REVIEWER_VERDICT", "EVIDENCE_OR_PROVENANCE_INCOMPLETE"),
        "REVIEW_COUNTS": {k: vb.get(k) for k in ("LOAD_BEARING_DEFECTS", "SUBSTANTIVE_DEFECTS",
                                                 "COSMETIC_DEFECTS", "ATTACKS_REFUTED")},
        "OPERATOR_REVERIFIED_EVERY_ACCEPTED_FINDING": True}
    d["LINEAGE_REGION"] = {
        "SUPERSEDED_PUBLISHED_BOX": {"grid_points": 563,
                                     "kY": [1.58e-05, 5.62e-04], "muY": [1.00e-08, 1.19e-03],
                                     "WHY_WITHDRAWN": R3["QUANTITATIVE_BOX_IS_NOT"]},
        "AT_THE_MEASURED_MEAN": R3["AT_THE_MEASURED_MEAN"],
        "ROBUST_CORE_90PCT_OF_WORLDS": R3["ROBUST_CORE_90PCT_OF_WORLDS"],
        "INTERSECTION_OVER_ALL_WORLDS": R3["INTERSECTION_OVER_ALL_WORLDS"],
        "WORLDS_WITH_AN_EMPTY_REGION": R3["WORLDS_WITH_AN_EMPTY_REGION"],
        "EMPTY": not R3["NON_EMPTINESS_IS_ROBUST"],
        "STATUS": ("DEVELOPMENTAL, and downgraded to a NECESSARY-CONDITION SCREEN: the chain "
                   "that produces it is rejected by the data at both testable points, so a "
                   "point outside the region is excluded while a point inside it is not "
                   "endorsed."),
        "IT_IS_A_LINEAGE_COUNT_REGION_NOT_A_TWO_CENTRE_REGION":
            R4["L3_TO_L7_NEVER_EVALUATED_IN_THE_REGION"]}
    d["CHAIN_CALIBRATION"] = {"MEAN_FIELD_REJECTED": R2["MEAN_FIELD_REJECTED"],
                              "WORLD_LEVEL_REJECTED": R2["WORLD_LEVEL_REJECTED"],
                              "PER_POINT": R2["PER_POINT"],
                              "CONSEQUENCE": R2["CONSEQUENCE"]}
    d["CAUSAL_ATTRIBUTION_CORRECTED"] = {
        "WITHDRAWN": R4["WITHDRAWN_CLAIM"], "WHY": R4["WHY_IT_WAS_WRONG"],
        "SATISFY_C3_AMONG_REGION_POINTS": R4["SATISFY_C3"],
        "COUNTERFACTUAL": R4["COUNTERFACTUAL_ON_THE_ORIGINAL_FROZEN_SET"],
        "WHAT_STILL_STANDS": R4["WHAT_STILL_STANDS"]}
    d["GATE_CORRECTIONS"] = rep["R5_GATE_AND_ARCHITECTURE_FIXES"]
    d["DISPOSITION_UNCHANGED_BY_THE_REVIEW"] = True
    d["WHY_THE_DISPOSITION_SURVIVES"] = (
        "every load-bearing defect makes the operator LESS identified, never more. The chain "
        "being rejected at both testable points, the region shrinking to a 90%%-robust core, the "
        "intersection over all worlds being empty and the non-emptiness turning out to be driven "
        "by dropping C3 rather than by replacing the founder gate -- all of these sharpen the "
        "same conclusion: the lineage criterion is the right one, and PQEC01's developmental "
        "data cannot identify the operator. Nothing in the review supports a POSITIVE "
        "disposition, and nothing supports architecture change.")
    json.dump(d, open(f"{OUT}/FLCR01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)

    rr = {"SECTION": "FLCR01 review and repair",
          "REVIEW": {"REVIEWS_AUTHORIZED": 1, "REVIEWS_USED": 1,
                     "VERDICT_BLOCK": vb,
                     "FILES": {f: hashlib.sha256(open(f"{RV}/{f}", "rb").read()).hexdigest()
                               for f in ("FLCR01_ADVERSARIAL_REVIEW.md",
                                         "FLCR01_ADVERSARIAL_REVIEW.json")},
                     "NO_FURTHER_SEAL_AUTHORIZED": True},
          "REPAIR": {"ROUNDS": 1,
                     "R1_environment_provenance": "grandparent constants replaced by PQEC01's own "
                                                  "Phase-A measurements (1.5011x inflation removed)",
                     "R2_chain_calibration": "chain tested against both measurable points and "
                                             "REJECTED; downgraded to a necessary-condition screen",
                     "R3_world_level_uncertainty": "region recomputed in every world's own "
                                                   "environment; robust core published, published "
                                                   "box withdrawn",
                     "R4_causal_attribution": "non-emptiness attributed to dropping C3, not to "
                                              "replacing the founder gate",
                     "R5_gates_and_architecture": "L4 withdrawn as degenerate; L1 horizon "
                                                  "corrected to T_birth; test A rescored "
                                                  "NOT_ESTABLISHED; 'none of A-E holds' withdrawn",
                     "DISPOSITION_CHANGED": False}}
    json.dump(rr, open(f"{OUT}/FLCR01_REVIEW_AND_REPAIR.json", "w"), indent=1, default=str)
    print("verdict:", vb.get("REVIEWER_VERDICT"), "| load-bearing:", vb.get("LOAD_BEARING_DEFECTS"))
    print("region: mean %d | robust core %d | intersection %d | empty-region worlds %d"
          % (R3["AT_THE_MEASURED_MEAN"]["n_points"], R3["ROBUST_CORE_90PCT_OF_WORLDS"]["n_points"],
             R3["INTERSECTION_OVER_ALL_WORLDS"]["n_points"], R3["WORLDS_WITH_AN_EMPTY_REGION"]))
    print("FINAL_DISPOSITION =", d["FINAL_DISPOSITION"])


if __name__ == "__main__":
    main()
