"""FDFLT01 §16 — terminal disposition. Computed from committed inputs; never assigned a literal."""
from __future__ import annotations
import json, os, sys, datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/FDFLT01/out"

def main():
    PR=json.load(open(f"{OUT}/FDFLT01_PRIMARY_ANALYSIS.json"))
    SEC=json.load(open(f"{OUT}/FDFLT01_SECONDARY_ANALYSIS.json"))
    TS=json.load(open(f"{OUT}/FDFLT01_TIMING_SENSITIVITY.json"))
    RV=json.load(open(f"{OUT}/FDFLT01_ADVERSARIAL_REVIEW.json"))
    FZ=json.load(open(f"{OUT}/FDFLT01_MASTER_FREEZE.json"))
    GT=json.load(open(f"{OUT}/FDFLT01_PRE_RUN_GATES.json"))
    DUR=json.load(open(f"{OUT}/FDFLT01_DURABILITY.json"))
    led=[json.loads(l) for l in open(f"{OUT}/FDFLT01_RUN_LEDGER.jsonl")]

    gates={
     "ALL_192_PRIMARY_STARTS_ACCOUNTED":bool(PR["ALL_PLANNED_WORLDS_PRESENT"]),
     "NO_OUTCOME_DRIVEN_REPLACEMENT":bool(sum(1 for r in led if r.get("kind")=="RESERVE")
                                          ==sum(1 for r in led if r.get("technical_failure"))),
     "COMPLETE_PRE_RUN_METHODS_HASH":bool(FZ["COMPLETE_PRE_RUN_METHODS_HASH"]=="PASS"),
     "WINDOWS_PRE_RUN_DURABILITY":bool(DUR["WINDOWS_PRE_RUN_DURABILITY"]=="PASS"),
     "WINDOWS_RAW_DURABILITY_BEFORE_ANALYSIS":bool(DUR.get("WINDOWS_RAW_DURABILITY_BEFORE_ANALYSIS")=="PASS"),
     "RAW_BEFORE_ANALYSIS_CHRONOLOGY":bool(any(a["attack"].startswith("15") and a["verdict"]=="ATTACK_REFUTED" for a in RV["ATTACKS"])),
     "PRE_RUN_GATES":bool(GT["ALL_PASS"]),
     "DUAL_IMPLEMENTATION_EXACT_AGREEMENT":bool(PR["DUAL_IMPLEMENTATION"]["EXACT_AGREEMENT"]),
     "NO_LOAD_BEARING_REVIEW_DEFECT":not RV["LOAD_BEARING_DEFECT_CONFIRMED"],
     "PRIMARY_EXACT_TEST_REJECTS_H0":bool(PR["REJECT_H0"])}
    technically_valid=all(v for k,v in gates.items() if k!="PRIMARY_EXACT_TEST_REJECTS_H0")
    if not technically_valid:
        disp="DIRECT_FUNCTIONAL_LINEAGE_TEST_TECHNICALLY_INVALID"
    elif gates["PRIMARY_EXACT_TEST_REJECTS_H0"]:
        disp="DIRECT_FUNCTIONAL_LINEAGE_POINT_QUALIFIED__SUCCESS_RATE_EXCEEDS_0_10"
    else:
        disp="DIRECT_FUNCTIONAL_LINEAGE_POINT_NOT_QUALIFIED__SUCCESS_RATE_NOT_SHOWN_ABOVE_0_10"

    dev=json.load(open(f"{OUT}/FDFLT01_POWER_ANALYSIS.json"))
    dl,dh=dev["DEVELOPMENTAL_B1_LOWER_95"],None
    A=json.load(open(f"{REPO}/FLRS02/out/FLRS02_B1_DIRECT_ATLAS.json"))["ATLAS"]["RATES"]["P_JOINT_FUNCTIONAL_SUCCESS_T_primary"]
    conc = (A["exact_binomial_95"][0] <= PR["PRIMARY_SUCCESS_RATE"] <= A["exact_binomial_95"][1]) and \
           (PR["PRIMARY_TWO_SIDED_95"][0] <= A["point_estimate"] <= PR["PRIMARY_TWO_SIDED_95"][1])
    D={"PROGRAMME":"FDFLT01 — FRESH-DIRECT-FUNCTIONAL-LINEAGE-TEST-01",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "PRIMARY_POINT":"B1","PRIMARY_NULL_RATE":PR["PRIMARY_NULL_RATE"],
     "PRIMARY_ALPHA":PR["PRIMARY_ALPHA"],"PRIMARY_N":PR["PRIMARY_N_PLANNED"],
     "PRIMARY_CRITICAL_SUCCESS_COUNT":PR["PRIMARY_CRITICAL_SUCCESS_COUNT"],
     "PRIMARY_SUCCESS_COUNT":PR["PRIMARY_SUCCESS_COUNT"],
     "PRIMARY_SUCCESS_RATE":PR["PRIMARY_SUCCESS_RATE"],
     "PRIMARY_ONE_SIDED_LOWER_95":PR["PRIMARY_ONE_SIDED_LOWER_95"],
     "PRIMARY_TWO_SIDED_95":PR["PRIMARY_TWO_SIDED_95"],
     "PRIMARY_EXACT_P_VALUE":PR["PRIMARY_EXACT_P_VALUE"],
     "DECISION_GATES":gates,"TECHNICALLY_VALID":technically_valid,
     "DEVELOPMENTAL_B1":{"count":A["count"],"n":A["n"],"rate":A["point_estimate"],
                         "exact_95":A["exact_binomial_95"]},
     "DEVELOPMENTAL_CONCORDANCE":bool(conc),
     "TIMING_SENSITIVITY":TS["BY_FRACTION"],
     "SECONDARY":{k:(v.get("rate") if isinstance(v,dict) else v) for k,v in SEC.items()
                  if k in ("first_birth","lineage_non_extinction","geometric_two_centre_formation",
                           "third_centre_before_function","X_source_integrity")},
     "FIRST_FAILING_COMPONENT_COUNTS":SEC["FIRST_FAILING_COMPONENT_COUNTS"],
     "CLAIM_CEILING":("at the prospectively frozen B1 law, the probability of the predeclared complete "
        "functional two-centre lineage event exceeds 0.10. Nothing further."),
     "FINAL_DISPOSITION":disp,
     "REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
     "H3_STATUS":"NOT_TESTED","AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
     "X_LAWSPEC_BASELINE":"UNCHANGED","ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
     "NEXT_SCIENTIFIC_ELIGIBILITY":("REPRODUCTION-CRITERION-DESIGN-01 (zero run)" if disp.startswith("DIRECT_FUNCTIONAL_LINEAGE_POINT_QUALIFIED")
        else "DIRECT-FUNCTIONAL-LINEAGE-FAILURE-AUTOPSY-01 (zero run)" if disp.endswith("NOT_SHOWN_ABOVE_0_10")
        else "NONE__THE_TEST_IS_TECHNICALLY_INVALID_AND_MAY_NOT_BE_SCIENTIFICALLY_REPAIRED")}
    json.dump(D,open(f"{OUT}/FDFLT01_FINAL_DISPOSITION.json","w"),indent=2)
    print(json.dumps({k:D[k] for k in ("PRIMARY_SUCCESS_COUNT","PRIMARY_SUCCESS_RATE",
      "PRIMARY_ONE_SIDED_LOWER_95","PRIMARY_EXACT_P_VALUE","DEVELOPMENTAL_CONCORDANCE",
      "TECHNICALLY_VALID","FINAL_DISPOSITION")},indent=2))
    print("gates:",json.dumps(gates,indent=1))

if __name__=="__main__": main()
