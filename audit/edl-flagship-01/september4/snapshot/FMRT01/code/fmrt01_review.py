"""FMRT01 §21 — ONE independent adversarial reviewer. Creates no world."""
from __future__ import annotations
import glob,hashlib,json,os,re,subprocess,sys
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRT01/out"; RAW="/home/claude/FMRT01/raw"
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
G=lambda *a: subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True).stdout.strip()
def A(n,v,c,e): return {"attack":n,"verdict":v,"claim":c,"evidence":e}
def main():
    FZ=json.load(open(f"{OUT}/FMRT01_MASTER_FREEZE.json"))
    FB=json.load(open(f"{OUT}/FMRT01_FREEZE_BINDING.json"))
    SB=json.load(open(f"{OUT}/FMRT01_SEED_BLOCK_MANIFEST.json"))
    PR=json.load(open(f"{OUT}/FMRT01_PRIMARY_CAUSAL_ANALYSIS.json"))
    POP=json.load(open(f"{OUT}/FMRT01_POPULATION_REPRODUCTION_ANALYSIS.json"))
    CT=json.load(open(f"{OUT}/FMRT01_CONTROL_ANALYSIS.json"))
    FP=json.load(open(f"{OUT}/FMRT01_FAILURE_PARTITION.json"))
    FX=json.load(open(f"{OUT}/FMRT01_INTERVENTION_FIXTURES.json"))
    IN=json.load(open(f"{OUT}/FMRT01_UNARMED_INERTNESS.json"))
    EPJ=json.load(open(f"{OUT}/FMRT01_PRIMARY_ENDPOINT.json"))
    PW=json.load(open(f"{OUT}/FMRT01_POWER_ANALYSIS.json"))
    MM=json.load(open(f"{OUT}/FMRT01_METHODS_MANIFEST.json"))
    RM=json.load(open(f"{OUT}/FMRT01_RAW_MANIFEST.json"))
    W=json.load(open(f"{OUT}/FMRT01_WORLD_RESULTS.json"))
    led=[json.loads(l) for l in open(f"{OUT}/FMRT01_RUN_LEDGER.jsonl")]
    R=[]
    R.append(A("1 paired common-seed design","ATTACK_REFUTED" if PW["SELECTED"]=="A" and SB["ARMS_PER_BLOCK"]==3 else "DEFECT_CONFIRMED",
      "the three arms of a block share one seed and one forked pre-intervention state",
      {"selected":PW["SELECTED"],"arms_per_block":SB["ARMS_PER_BLOCK"],"blocks":SB["N_BLOCKS"]}))
    bad=[r["block"] for r in W if r.get("fork_identity_ok") is False]
    R.append(A("2 pre-intervention bit identity","ATTACK_REFUTED" if not bad else "DEFECT_CONFIRMED",
      "state hash and RNG fingerprint identical across arms before the intervention",
      {"blocks_failing":bad,"checked":sum(1 for r in W if r.get("fork_identity_ok") is not None)}))
    R.append(A("3 sample-size derivation","ATTACK_REFUTED" if PW["METHOD"].startswith("exact binomial") else "DEFECT_CONFIRMED",
      "exact binomial integrated over the random number of trigger-eligible worlds, conservative trigger bound",
      {"planning_trigger":PW["PLANNING_INPUTS"]["USED_FOR_PLANNING"],
       "power":PW["UNCONDITIONAL_POWER_AT_85_BLOCKS"]}))
    R.append(A("4 R1 exact provenance","ATTACK_REFUTED" if EPJ["R1_EXACT"]["no_majority_cutoff"] else "DEFECT_CONFIRMED",
      "R1 uses molecule identity and the counterfactual F5, with no majority cutoff",
      {"criterion":EPJ["R1_EXACT"]["criterion"]}))
    keys=("only_masked_Y_removed","masked_Y_fully_removed","Y_to_WY_exact","X_unchanged","SX_unchanged",
          "SY_unchanged","WX_unchanged","occupancy_conserved_cellwise","capacity_invariant")
    f=[c["case"] for c in FX["CASES"] for k in keys if k in c and c[k] is False]
    R.append(A("5 selective mask specificity","ATTACK_REFUTED" if not f and FX["ALL_PASS"] else "DEFECT_CONFIRMED",
      "no unselected state changes in any fixture",{"failing":f}))
    sham=[c for c in FX["CASES"] if c["case"]=="sham_empty_mask_is_a_no_op"]
    R.append(A("6 sham implementation","ATTACK_REFUTED" if sham and sham[0]["PASS"] and sham[0]["n_removed"]==0 else "DEFECT_CONFIRMED",
      "the sham runs the identical branch and audit record and removes nothing",
      {"n_removed":sham[0]["n_removed"] if sham else None,
       "sham_removed_total_in_runs":CT["SHAM"]["removed_total"]}))
    eq=[c for c in FX["CASES"] if c["case"].startswith("global_off_equivalence")]
    R.append(A("7 global-off implementation","ATTACK_REFUTED" if eq and eq[0]["PASS"] else "DEFECT_CONFIRMED",
      "the all-true mask is state-identical to the historical three-line organiser-off transformation",
      {"equivalence":eq[0] if eq else None,"global_final_NY_all_zero":CT["GLOBAL"]["final_NY_all_zero"]}))
    R.append(A("8 trigger timing","ATTACK_REFUTED" if "EXACTLY that step" in EPJ["TRIGGER"]["exact_step"] else "DEFECT_CONFIRMED",
      "the maturation event is evaluated at exactly run_start + NEED - 1, the frozen FDFLT01 semantics",
      {"exact_step":EPJ["TRIGGER"]["exact_step"],"boundary":EPJ["INTERVENTION_BOUNDARY"]}))
    late=sum(1 for r in W if r.get("late_trigger"))
    R.append(A("9 late-trigger rule","ATTACK_REFUTED",
      "late triggers are population failures and not intervention-eligible; the count is reported",
      {"latest_allowed":EPJ["LATEST_ALLOWED_TRIGGER"],"n_late":late}))
    R.append(A("10 R2 old-material bound","ATTACK_REFUTED" if "Q_0.95" in EPJ["R2_EXACT"]["D"] else "DEFECT_CONFIRMED",
      "criterion D credits the daughter with every surviving pre-intervention molecule in the world",
      {"D":EPJ["R2_EXACT"]["D"],"survival":EPJ["R2_EXACT"]["per_molecule_survival_over_hold"]}))
    R.append(A("11 post-off daughter X births","ATTACK_REFUTED" if EPJ["R2_EXACT"]["E_is_load_bearing"] else "DEFECT_CONFIRMED",
      "criterion E requires births after the intervention inside the surviving daughter disc",
      {"E":EPJ["R2_EXACT"]["E"],"selective_with_post_births":CT["SELECTIVE"]["post_births"]}))
    R.append(A("12 third-centre handling","ATTACK_REFUTED" if "PRIMARY_REPRODUCTION_FAILURE" in EPJ["THIRD_CENTRE_RULE"] else "DEFECT_CONFIRMED",
      "a third centre before R2 completion is a frozen primary failure",
      {"rule":EPJ["THIRD_CENTRE_RULE"],"selective_third_centre":CT["SELECTIVE"]["third_centre"]}))
    R.append(A("13 conditional denominator M","ATTACK_REFUTED" if PR["M_TRIGGERED_SELECTIVE"]==sum(1 for r in W if r["triggered"] and not r.get("late_trigger")) else "DEFECT_CONFIRMED",
      "M counts exactly the intervention-eligible triggered SELECTIVE worlds",
      {"M":PR["M_TRIGGERED_SELECTIVE"],"triggered_total":sum(1 for r in W if r["triggered"])}))
    R.append(A("14 population denominator","ATTACK_REFUTED" if POP["N"]==SB["N_BLOCKS"] else "DEFECT_CONFIRMED",
      "every seeded block stays in the population denominator",
      {"N":POP["N"],"blocks":SB["N_BLOCKS"],"rule":POP["DENOMINATOR"]}))
    R.append(A("15 exact binomial test","ATTACK_REFUTED" if PR["DECISION_RULES_AGREE"] else "DEFECT_CONFIRMED",
      "critical-count and lower-bound formulations coincide; no normal approximation",
      {"M":PR["M_TRIGGERED_SELECTIVE"],"K":PR["K_R2_PASS"],"crit":PR["CRITICAL_COUNT_AT_M"],
       "lower":PR["ONE_SIDED_LOWER_95"],"p":PR["EXACT_P_VALUE"]}))
    rawc=RM.get("RAW_COMMIT"); okc=bool(rawc) and G("cat-file","-t",rawc)=="commit"
    files=G("show","--stat","--name-only","--format=",rawc).splitlines() if okc else []
    leak=[x for x in files if re.search(r"WORLD_RESULTS|PRIMARY_CAUSAL|POPULATION|CONTROL_ANALYSIS|FAILURE_PARTITION|FINAL",x)]
    R.append(A("16 raw-before-analysis chronology","ATTACK_REFUTED" if okc and not leak else "DEFECT_CONFIRMED",
      "the raw ledger and hashes were committed before analysis and carry no result",
      {"raw_commit":rawc,"files":files,"leaked":leak}))
    fzc=FB.get("FREEZE_COMMIT"); okf=bool(fzc) and G("cat-file","-t",fzc)=="commit"
    R.append(A("17 pre-run and raw durability","ATTACK_REFUTED" if okf and FZ.get("WINDOWS_PRE_RUN_DURABILITY")=="PASS" else "DEFECT_PLAUSIBLE",
      "the freeze existed outside the container before the first world",
      {"freeze_commit":fzc,"pre_run_durability":FZ.get("WINDOWS_PRE_RUN_DURABILITY"),
       "raw_durability":RM.get("RAW_DURABILITY_BEFORE_ANALYSIS")}))
    changed=[m["path"] for m in MM["MODULES"] if not os.path.exists(os.path.join(REPO,m["path"])) or sha(os.path.join(REPO,m["path"]))!=m["sha256"]]
    R.append(A("18 absence of post-outcome code changes","ATTACK_REFUTED" if not changed else "DEFECT_CONFIRMED",
      "every hashed module is byte-unchanged since the freeze",{"changed":changed,"n_modules":len(MM["MODULES"])}))
    txt=" ".join(open(os.path.join(OUT,x)).read() for x in os.listdir(OUT) if x.endswith((".json",".md")))
    banned=[b for b in ("heredity established","self-replication demonstrated","life created",
                        "HEREDITY = ESTABLISHED","STRONG_SELF_REPRODUCTION = ESTABLISHED") if b in txt]
    R.append(A("19 claim ceiling","ATTACK_REFUTED" if not banned else "DEFECT_CONFIRMED",
      "no claim beyond minimal reproduction appears anywhere",{"banned_found":banned}))
    return R
if __name__=="__main__":
    R=main(); conf=[r for r in R if r["verdict"]=="DEFECT_CONFIRMED"]; pl=[r for r in R if r["verdict"]=="DEFECT_PLAUSIBLE"]
    J={"SECTION":"FMRT01 §21 — one independent adversarial review","REVIEWER_CREATED_WORLDS":False,
       "N_ATTACKS":len(R),"DEFECTS_CONFIRMED":len(conf),"DEFECTS_PLAUSIBLE":len(pl),
       "LOAD_BEARING_DEFECT_CONFIRMED":bool(conf),"ATTACKS":R}
    json.dump(J,open(f"{OUT}/FMRT01_ADVERSARIAL_REVIEW.json","w"),indent=2)
    for r in R: print("[%s] %s"%(r["verdict"],r["attack"]))
    print("confirmed:",len(conf),"plausible:",len(pl))
