"""FMRT01 §22 — terminal disposition, computed from committed inputs."""
from __future__ import annotations
import json,datetime,os
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRT01/out"
def main():
    PR=json.load(open(f"{OUT}/FMRT01_PRIMARY_CAUSAL_ANALYSIS.json"))
    POP=json.load(open(f"{OUT}/FMRT01_POPULATION_REPRODUCTION_ANALYSIS.json"))
    CT=json.load(open(f"{OUT}/FMRT01_CONTROL_ANALYSIS.json"))
    FP=json.load(open(f"{OUT}/FMRT01_FAILURE_PARTITION.json"))
    RV=json.load(open(f"{OUT}/FMRT01_ADVERSARIAL_REVIEW.json"))
    AD=json.load(open(f"{OUT}/FMRT01_REVIEW_ADJUDICATION.json"))
    FZ=json.load(open(f"{OUT}/FMRT01_MASTER_FREEZE.json"))
    IN=json.load(open(f"{OUT}/FMRT01_UNARMED_INERTNESS.json"))
    FX=json.load(open(f"{OUT}/FMRT01_INTERVENTION_FIXTURES.json"))
    RM=json.load(open(f"{OUT}/FMRT01_RAW_MANIFEST.json"))
    gates={
     "ALL_BLOCKS_ACCOUNTED":PR["PRIMARY_SEED_BLOCKS"]==FZ["N_BLOCKS"],
     "NO_TECHNICAL_FAILURE":PR["TECHNICAL_FAILURES"]==0,
     "FORK_IDENTITY_OK":PR["FORK_IDENTITY_OK_ALL"],
     "UNARMED_INERTNESS":IN["UNARMED_INERTNESS"].startswith("PASS_88_OF_88"),
     "FIXTURES_PASS":FX["ALL_PASS"],
     "FAILURE_PARTITION_VALID":FP["IS_A_PARTITION"],
     "PRE_RUN_DURABILITY":FZ.get("WINDOWS_PRE_RUN_DURABILITY")=="PASS",
     "RAW_DURABILITY_BEFORE_ANALYSIS":RM.get("RAW_DURABILITY_BEFORE_ANALYSIS")=="PASS",
     "NO_LOAD_BEARING_REVIEW_DEFECT":not AD["LOAD_BEARING_DEFECT_CONFIRMED"],
     "DECISION_RULES_AGREE":PR["DECISION_RULES_AGREE"]}
    valid=all(gates.values())
    M=PR["M_TRIGGERED_SELECTIVE"]
    if not valid: disp="MINIMAL_REPRODUCTION_TEST_TECHNICALLY_INVALID"
    elif M==0 or (PR["CRITICAL_COUNT_AT_M"] is None):
        disp="MINIMAL_REPRODUCTION_NOT_QUALIFIED__PRE_INTERVENTION_MULTIPLICATION_TOO_RARE"
    elif PR["REJECT_H0"] and POP["COUNT"]>0:
        disp="MINIMAL_REPRODUCTION_CAUSALLY_QUALIFIED"
    else:
        disp="MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED"
    D={"PROGRAMME":"FMRT01 — FRESH-MINIMAL-REPRODUCTION-TEST-01",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "EXPERIMENTAL_DESIGN":"paired 3-arm common-seed blocks, forked at the frozen trigger",
     "PRIMARY_SEED_BLOCKS":PR["PRIMARY_SEED_BLOCKS"],
     "PRIMARY_SCIENTIFIC_WORLDS":PR["PRIMARY_SCIENTIFIC_WORLDS"],
     "TRIGGERED_SELECTIVE_WORLDS":M,"R2_SUCCESS_COUNT":PR["K_R2_PASS"],
     "CRITICAL_COUNT_AT_M":PR["CRITICAL_COUNT_AT_M"],
     "Q_AUTONOMY":PR["Q_AUTONOMY"],"ONE_SIDED_LOWER_95":PR["ONE_SIDED_LOWER_95"],
     "TWO_SIDED_95":PR["TWO_SIDED_95"],"EXACT_P_VALUE":PR["EXACT_P_VALUE"],
     "REJECT_H0":PR["REJECT_H0"],
     "POPULATION_COUNT":POP["COUNT"],"POPULATION_RATE":POP["RATE"],
     "POPULATION_TWO_SIDED_95":POP["TWO_SIDED_95"],
     "CONTROLS":CT,"FAILURE_PARTITION":FP["PARTITION"],
     "DECISION_GATES":gates,"TECHNICALLY_VALID":valid,
     "FINAL_DISPOSITION":disp,
     "CLAIM_CEILING":("a positive result establishes MINIMAL REPRODUCTION under the operational "
       "R0+R1+R2 definition at the prospectively frozen B1 law. It establishes nothing about strong "
       "self-reproduction, second-generation competence, heredity, evolution or life."),
     "STRONG_SELF_REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
     "R3_STATUS":"NOT_TESTED","ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
     "NEXT_SCIENTIFIC_ELIGIBILITY":("STRONG-SELF-REPRODUCTION-GENERATION-DESIGN-01 (zero run)"
       if disp=="MINIMAL_REPRODUCTION_CAUSALLY_QUALIFIED"
       else "MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01 (zero run)")}
    json.dump(D,open(f"{OUT}/FMRT01_FINAL_DISPOSITION.json","w"),indent=2)
    print(json.dumps({k:D[k] for k in ("TRIGGERED_SELECTIVE_WORLDS","R2_SUCCESS_COUNT",
      "CRITICAL_COUNT_AT_M","Q_AUTONOMY","ONE_SIDED_LOWER_95","EXACT_P_VALUE","REJECT_H0",
      "POPULATION_COUNT","POPULATION_RATE","TECHNICALLY_VALID","FINAL_DISPOSITION")},indent=2))
    print("gates:",json.dumps(gates,indent=1))
if __name__=="__main__": main()
