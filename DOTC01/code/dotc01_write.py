import json, io, os, datetime, statistics
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"
L=lambda n: json.load(open(f"{OUT}/{n}"))
BD=L("DOTC01_PARENT_BINDING.json"); OM=L("DOTC01_EXECUTABLE_OBJECT_MAP.json")
OLD=L("DOTC01_OLD_OBJECT_VERIFICATION.json"); OB=L("DOTC01_ORGANISER_OBJECT_DEFINITION.json")
TE=L("DOTC01_TURNOVER_EVENT_DEFINITION.json"); FCd=L("DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json")
TS=L("DOTC01_ORGANISER_TIMESCALE.json"); AU=L("DOTC01_EXISTING_DATA_TURNOVER_AUDIT.json")
CA=L("DOTC01_TURNOVER_CASES.json"); B1=L("DOTC01_B1_FEASIBILITY.json"); B2=L("DOTC01_B2_FEASIBILITY.json")
AR=L("DOTC01_CURRENT_ARCHITECTURE_FEASIBILITY.json"); PW=L("DOTC01_POWER_ANALYSIS.json")
CK=L("_checkB.json")
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
HOR=TS["HORIZON"]

# -------------------- independent check --------------------
def independent():
    items=[
     ("Y lifetime e-folding B1",TS["Y_LIFETIME"]["B1"]["T_Y_SURVIVAL_e_folding"],CK["Y_LIFETIME"]["B1"]["e_folding"]),
     ("P(one constituent decays by 11000) B1",TS["Y_LIFETIME"]["B1"]["P_death_within_11000"],CK["Y_LIFETIME"]["B1"]["P_death_11000"]),
     ("P(one constituent decays by 11000) B2",TS["Y_LIFETIME"]["B2"]["P_death_within_11000"],CK["Y_LIFETIME"]["B2"]["P_death_11000"]),
     ("P(>=1 local Y birth by 11000) B1",TS["POINT_SUMMARY"]["B1"]["P_at_least_one_local_Y_birth_by"][str(HOR)],CK["P_AT_LEAST_ONE_LOCAL_Y_BIRTH_BY_HORIZON"]["B1"]),
     ("P(>=1 local Y birth by 11000) B2",TS["POINT_SUMMARY"]["B2"]["P_at_least_one_local_Y_birth_by"][str(HOR)],CK["P_AT_LEAST_ONE_LOCAL_Y_BIRTH_BY_HORIZON"]["B2"]),
     ("worlds with complete turnover B1",AU["SUMMARY"]["B1"]["worlds_with_complete_turnover"],CK["TURNOVER_AUDIT"]["B1"]["worlds_with_complete_turnover"]),
     ("centres with complete turnover B1",AU["SUMMARY"]["B1"]["centres_with_complete_turnover"],CK["TURNOVER_AUDIT"]["B1"]["centres_with_complete_turnover"]),
     ("orderings B1",AU["SUMMARY"]["B1"]["orderings"],CK["TURNOVER_AUDIT"]["B1"]["orderings"]),
     ("worlds with complete turnover B2",AU["SUMMARY"]["B2"]["worlds_with_complete_turnover"],CK["TURNOVER_AUDIT"]["B2"]["worlds_with_complete_turnover"]),
     ("total Y births B1",AU["SUMMARY"]["B1"]["total_Y_births"],CK["TURNOVER_AUDIT"]["B1"]["total_Y_births"]),
     ("total Y deaths B1",AU["SUMMARY"]["B1"]["total_Y_deaths"],CK["TURNOVER_AUDIT"]["B1"]["total_Y_deaths"]),
     ("total Y deaths B2",AU["SUMMARY"]["B2"]["total_Y_deaths"],CK["TURNOVER_AUDIT"]["B2"]["total_Y_deaths"]),
     ("centres persisting after the removal B1",CA["N_WITH_FUNCTIONAL_CONTINUITY"],CK["TURNOVER_AUDIT"]["B1"]["worlds_with_persistence_after_removal_gt_0"]),
    ]
    def close(a,b):
        if isinstance(a,(int,)) and isinstance(b,(int,)): return a==b
        if isinstance(a,dict): return a==b
        return abs(float(a)-float(b))<=1e-6*max(1.0,abs(float(a)))
    dis=[(k,a,b) for k,a,b in items if not close(a,b)]
    I={"SECTION":"DOTC01 §17 — independent check","GENERATED_UTC":NOW,
     "CHECKER_RAN_ZERO_WORLDS":True,"CHECKER_IMPORTS_THE_PRIMARY_ANALYSIS":False,
     "INDEPENDENCE":CK["INDEPENDENCE"],
     "AGREEMENT_TABLE":[{"quantity":k,"primary":a,"checker":b,"agree":close(a,b)} for k,a,b in items],
     "N_CHECKED":len(items),"N_DISAGREEMENTS":len(dis),"DISAGREEMENTS":dis,
     "LOAD_BEARING_DISAGREEMENT":bool(dis),
     "TERMINAL_ROUTE_DECISION_INDEPENDENTLY_SUPPORTED":(
       CK["TURNOVER_AUDIT"]["B1"]["worlds_with_complete_turnover"]>0 and CK["TURNOVER_AUDIT"]["B2"]["worlds_with_complete_turnover"]==0),
     "VERDICT":"INDEPENDENT_DERIVATIONS_AGREE" if not dis else "INDEPENDENT_DERIVATIONS_DISAGREE"}
    json.dump(I,open(f"{OUT}/DOTC01_INDEPENDENT_CHECK.json","w"),indent=1)
    return I

IC=independent()
DISP=("ORGANISER_TURNOVER_CRITERION_DERIVED__ONE_EXISTING_POINT_DIRECT_TEST_ELIGIBLE"
      if IC["VERDICT"]=="INDEPENDENT_DERIVATIONS_AGREE" and B1["CANDIDATE"] and PW["DECISION_CAPABLE"]
      else "ORGANISER_TURNOVER_CRITERION_NOT_IDENTIFIABLE__INDEPENDENT_DERIVATIONS_DISAGREE")

# -------------------- organiser object md --------------------
b=io.StringIO(); w=b.write
w("# DOTC01 — THE ORGANISER-LEVEL DAUGHTER OBJECT\n\n")
w("## Why the old object was not enough\n\n")
w("Recomputed from raw FMRT01 bytes: %d triggered blocks, every one with exactly %d Y-occupied cells at\n"%(OLD["TRIGGERED_BLOCKS"],2))
w("maturation, one per centre. The selective intervention removes %s Y and the global one removes %s.\n"%(OLD["Y_REMOVED_BY_SELECTIVE"],OLD["Y_REMOVED_BY_GLOBAL"]))
w("A single constituent survives the old 250-step window with probability %.6f analytically and did so in\n"%OLD["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["analytic_single_Y"])
w("%d of %d observed cases.\n\n"%(OLD["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["observed_final_NY_ge_1"],OLD["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["of"]))
w("```\nOLD_DAUGHTER_OBJECT = %s\nVERDICT             = %s\n```\n\n"%(OLD["OLD_DAUGHTER_OBJECT"],OLD["VERDICT"]))
w("> %s\n\n"%OLD["WHY_NOT_INVALID"])
w("---\n\n## The new object\n\n%s\n\n"%OB["NO_GENEALOGY"])
w("**Centre.** %s — %s, `CORE_R = %s`.\n\n"%(OB["CENTRE"]["definition"],OB["CENTRE"]["frozen_rule"],OB["CENTRE"]["CORE_R"]))
w("**Identity across steps.** %s\n\n"%OB["CENTRE_IDENTITY_ACROSS_STEPS"]["rule"])
w("*%s.*\n\n"%OB["CENTRE_IDENTITY_ACROSS_STEPS"]["why_mutual_and_unique"])
w("**%s** holds on an interval only if all six conditions hold:\n\n"%OB["ORGANISER_LEVEL_CONTINUITY"]["NAME"])
for c in OB["ORGANISER_LEVEL_CONTINUITY"]["an interval [t0,t1] on one continuously matched component C qualifies only if ALL SIX hold"]:
    w("%s\n"%c)
w("\n> %s\n\n"%OB["WHY_N_Y_GE_2_IS_NOT_THE_CRITERION"])
w("### Removal\n\n%s\n\n%s\n\n"%(OB["REMOVAL_IS_DEFINED_AS"]["primary"],OB["REMOVAL_IS_DEFINED_AS"]["why_not_emigration"]))
w("### Birth is always inside the centre — structurally\n\n%s\n\n"%OB["BIRTH_IS_ALWAYS_INSIDE_C"])
w("---\n\n## The turnover event\n\n")
w("**COMPLETE_TURNOVER** requires: %s.\n\n"%"; ".join(TE["COMPLETE_TURNOVER"]["requires"]))
O=TE["COMPLETE_TURNOVER"]["orderings_analysed"]
w("| Ordering | Admissible |\n|---|---|\n")
w("| BIRTH_THEN_DEATH | %s — %s |\n"%(O["BIRTH_THEN_DEATH"]["admissible"],O["BIRTH_THEN_DEATH"]["note"]))
w("| DEATH_THEN_BIRTH | %s |\n\n"%O["DEATH_THEN_BIRTH"]["admissible"])
w("**Theorem.** %s\n\n"%O["DEATH_THEN_BIRTH"]["proof"])
w("%s\n\n"%TE["COMPLETE_TURNOVER"]["consequence_for_the_B1_daughter"])
w("**PARTIAL_TURNOVER** — %s. **NO_TURNOVER** — %s.\n\n"%(TE["PARTIAL_TURNOVER"],TE["NO_TURNOVER"]))
w("---\n\n## Functional continuity\n\n")
w("Primary observable: **%s**.\n\n%s\n\n"%(FCd["PRIMARY_OBSERVABLE"],FCd["WHY"]))
w("No world-total quantity may enter. %s\n\n"%FCd["WORLD_TOTAL_X_MAY_NOT_ENTER"])
w("No operator-derived floor is transportable: %s\n\n"%FCd["TURNOVER_GAP"]["why_not"])
w("```\nFUNCTIONAL_CONTINUITY_MEASURE = %s\n```\n\n%s\n"%(FCd["FUNCTIONAL_CONTINUITY_MEASURE"],FCd["OPERATIONAL_FORM"]))
open(f"{OUT}/DOTC01_ORGANISER_OBJECT_DEFINITION.md","w").write(b.getvalue())

# -------------------- timescale md --------------------
b=io.StringIO(); w=b.write
w("# DOTC01 — THE ORGANISER TIMESCALE\n\n")
w("Formulas frozen before any developmental distribution was read: `%s`.\n\n"%TS["FORMULAS_FROZEN_BEFORE_READING_ANY_DEVELOPMENTAL_DISTRIBUTION"])
w("## Constituent lifetime\n\n| | B1 | B2 |\n|---|---|---|\n")
for k,lab in (("muY","muY"),("T_Y_SURVIVAL_e_folding","e-folding, steps"),
              ("exact_discrete_mean_steps_survived","exact discrete mean"),
              ("exact_discrete_median","exact discrete median"),
              ("P_death_within_1000","P(decay by 1000)"),("P_death_within_2500","P(decay by 2500)"),
              ("P_death_within_5000","P(decay by 5000)"),("P_death_within_11000","P(decay by 11000)")):
    w("| %s | %s | %s |\n"%(lab,TS["Y_LIFETIME"]["B1"].get(k),TS["Y_LIFETIME"]["B2"].get(k)))
w("\n## Local Y-birth hazard\n\nExact per cell per step: `P(no Y birth) = (1 - min(1, kY*nX*nY))^cand`, `cand = min(nSY, free)`.\n\n")
w("| | B1 | B2 |\n|---|---|---|\n")
for pt in ("B1","B2"): pass
a1=TS["POINT_SUMMARY"]["B1"]; a2=TS["POINT_SUMMARY"]["B2"]
w("| mean of world means | %.4e | %.4e |\n"%(a1["per_step_local_Y_birth_hazard"]["mean_of_world_means"],a2["per_step_local_Y_birth_hazard"]["mean_of_world_means"]))
w("| median of world medians | %.4e | %.4e |\n"%(a1["per_step_local_Y_birth_hazard"]["median_of_world_medians"],a2["per_step_local_Y_birth_hazard"]["median_of_world_medians"]))
w("| max observed | %.4e | %.4e |\n"%(a1["per_step_local_Y_birth_hazard"]["max_observed"],a2["per_step_local_Y_birth_hazard"]["max_observed"]))
for T in (1000,2500,5000,HOR):
    w("| P(>=1 local Y birth by %d) | %.4f | %.4f |\n"%(T,a1["P_at_least_one_local_Y_birth_by"][str(T)],a2["P_at_least_one_local_Y_birth_by"][str(T)]))
w("\nThe linearisation `kY*Q` is an upper bound on the exact hazard and is never substituted for it.\n\n")
w("## Complete-turnover time\n\nAn exact discrete-time absorbing chain driven step by step by each world's realised hazard sequence.\n")
w("No mean replaces a time-dependent hazard.\n\n")
w("| | B1 | B2 |\n|---|---|---|\n")
for T in (1000,2500,5000,HOR):
    w("| P(complete turnover by %d) | %.5f | %.5f |\n"%(T,B1["TURNOVER_FEASIBILITY"]["MODEL_P_COMPLETE_TURNOVER_BY"][str(T)],B2["TURNOVER_FEASIBILITY"]["MODEL_P_COMPLETE_TURNOVER_BY"][str(T)]))
w("| median / q80 / q90 | %s / %s / %s | %s / %s / %s |\n"%(
  B1["TURNOVER_FEASIBILITY"]["MODEL_median"],B1["TURNOVER_FEASIBILITY"]["MODEL_q80"],B1["TURNOVER_FEASIBILITY"]["MODEL_q90"],
  B2["TURNOVER_FEASIBILITY"]["MODEL_median"],B2["TURNOVER_FEASIBILITY"]["MODEL_q80"],B2["TURNOVER_FEASIBILITY"]["MODEL_q90"]))
w("| P(extinct before turnover) | %.5f | %.5f |\n\n"%(B1["LINEAGE_EXTINCTION"]["MODEL_P_extinct_before_turnover"],B2["LINEAGE_EXTINCTION"]["MODEL_P_extinct_before_turnover"]))
w("`None` means the quantile is not reached inside the 11000-step horizon.\n\n")
w("**The hold is event-based, not a clock.** The criterion is that the centre keeps its local X organising\n")
w("function through at least one complete constituent turnover. The horizon exists only to bound the\n")
w("observation, and it is not lengthened beyond 11000.\n\n")
w("## The one approximation, stated\n\n> %s\n"%B1.get("MODEL_CAVEAT",json.load(open(f"{OUT}/_feasibility_core.json"))["MODEL_CAVEAT"]))
open(f"{OUT}/DOTC01_ORGANISER_TIMESCALE.md","w").write(b.getvalue())

# -------------------- architecture md --------------------
b=io.StringIO(); w=b.write
w("# DOTC01 — IS THE CURRENT ARCHITECTURE CAPABLE?\n\n")
w("%s\n\n"%AR["THE_QUESTION"])
w("## The answer does not need a feasibility bound\n\n> %s\n\n"%AR["THE_ANSWER_IS_ALREADY_IN_THE_DATA"])
w("| Structural requirement | Status |\n|---|---|\n")
for r in AR["STRUCTURAL_REQUIREMENTS_AND_WHERE_EACH_IS_SATISFIED"]:
    w("| %s | **%s** |\n"%(r["requirement"],r["status"]))
w("\n")
for r in AR["STRUCTURAL_REQUIREMENTS_AND_WHERE_EACH_IS_SATISFIED"]:
    w("- **%s** — %s\n"%(r["status"],r["why"]))
w("\n## The four canonical conflicts\n\n")
for k,v in AR["THE_FOUR_CANONICAL_CONFLICTS_AND_THEIR_STATUS"].items():
    w("- *%s* → **%s**\n"%(k,v))
w("\n```\nARCHITECTURE_CHANGE_NECESSITY = %s\n```\n\n%s\n\n"%(AR["ARCHITECTURE_CHANGE_NECESSITY"],AR["WHY_NOT"]))
w("`NEW_PARAMETER_DESIGN_REQUIRED = %s`. %s\n"%(AR["NEW_PARAMETER_DESIGN_REQUIRED"],AR["WHY_NO_NEW_POINT"]))
open(f"{OUT}/DOTC01_CURRENT_ARCHITECTURE_FEASIBILITY.md","w").write(b.getvalue())

# -------------------- disposition --------------------
D={"PROGRAMME":"DOTC01 — DAUGHTER-ORGANISER-TURNOVER-CRITERION-01","GENERATED_UTC":NOW,
 "PARENT":BD["PARENT_PROGRAM"],"PARENT_TIP":BD["PARENT_TIP_RESOLVED"],
 "PARENT_FINAL_DISPOSITION":BD["PARENT_FINAL_DISPOSITION"],
 "NEW_SCIENTIFIC_RUNS_USED":0,"NEW_SEEDS":0,"NEW_WORLDS":0,"NEW_TRAJECTORIES":0,
 "DAUGHTER_ORGANISER_OBJECT":OB["ORGANISER_LEVEL_CONTINUITY"]["NAME"],
 "TURNOVER_EVENT":"COMPLETE_TURNOVER — at least one accepted Y birth and at least one Y removal inside ONE continuous centre-identity interval that is never empty",
 "FUNCTIONAL_CONTINUITY_MEASURE":FCd["FUNCTIONAL_CONTINUITY_MEASURE"],
 "B1":{"kY":B1["kY"],"muY":B1["muY"],"Y_e_folding":B1["Y_LIFETIME_SCALE"]["e_folding_steps"],
   "MODEL_P_complete_turnover_by_horizon":B1["TURNOVER_FEASIBILITY"]["MODEL_P_COMPLETE_TURNOVER_BY"][str(HOR)],
   "DEVELOPMENTAL_complete":B1["TURNOVER_FEASIBILITY"]["DEVELOPMENTAL_COMPLETE"],
   "DEVELOPMENTAL_functional":B1["TURNOVER_FEASIBILITY"]["DEVELOPMENTAL_FUNCTIONAL"],
   "CANDIDATE":B1["CANDIDATE"]},
 "B2":{"kY":B2["kY"],"muY":B2["muY"],"CANDIDATE":B2["CANDIDATE"],"WHY_NOT":B2["WHY_NOT"]},
 "ARCHITECTURE_CHANGE_NECESSITY":AR["ARCHITECTURE_CHANGE_NECESSITY"],
 "INDEPENDENT_CHECK":IC["VERDICT"],
 "DECISION_CAPABLE":PW["DECISION_CAPABLE"],"RECOMMENDED_N":PW["RECOMMENDED_N"],
 "FINAL_DISPOSITION":DISP,
 "CONDITIONAL_HANDOFF":"HANDOFF_FRESH_DAUGHTER_ORGANISER_TURNOVER_TEST_01.md",
 "RETROACTIVE_REPRODUCTION_CLAIM":"NOT_MADE",
 "MINIMAL_REPRODUCTION_STATUS":"NOT_ESTABLISHED","STRONG_SELF_REPRODUCTION_STATUS":"NOT_TESTED",
 "HEREDITY_STATUS":"NOT_TESTED","R3_STATUS":"NOT_TESTED","H3_STATUS":"NOT_TESTED",
 "REPRODUCTION_STATUS":"NOT_TESTED","AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "PARAMETER_POINT":"B1, unchanged. No sweep, no interpolation, no new point, no architecture change."}
json.dump(D,open(f"{OUT}/DOTC01_FINAL_DISPOSITION.json","w"),indent=2)
print("INDEPENDENT CHECK:",IC["VERDICT"],"| disagreements:",IC["N_DISAGREEMENTS"])
print("FINAL_DISPOSITION:",DISP)
