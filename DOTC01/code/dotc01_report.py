import json, io, os, datetime, statistics
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"
L=lambda n: json.load(open(f"{OUT}/{n}"))
BD=L("DOTC01_PARENT_BINDING.json"); OM=L("DOTC01_EXECUTABLE_OBJECT_MAP.json")
OLD=L("DOTC01_OLD_OBJECT_VERIFICATION.json"); OB=L("DOTC01_ORGANISER_OBJECT_DEFINITION.json")
TE=L("DOTC01_TURNOVER_EVENT_DEFINITION.json"); FC=L("DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json")
TS=L("DOTC01_ORGANISER_TIMESCALE.json"); AU=L("DOTC01_EXISTING_DATA_TURNOVER_AUDIT.json")
CA=L("DOTC01_TURNOVER_CASES.json"); B1=L("DOTC01_B1_FEASIBILITY.json"); B2=L("DOTC01_B2_FEASIBILITY.json")
AR=L("DOTC01_CURRENT_ARCHITECTURE_FEASIBILITY.json"); PW=L("DOTC01_POWER_ANALYSIS.json")
IC=L("DOTC01_INDEPENDENT_CHECK.json"); FD=L("DOTC01_FINAL_DISPOSITION.json")
HOR=TS["HORIZON"]
b=io.StringIO(); w=b.write

w("# DOTC01 — DAUGHTER-ORGANISER-TURNOVER-CRITERION-01\n## FINAL REPORT\n\n")
w("A zero-run derivation. MRFA01 named two missing objects; this mission derives both, and then finds\n")
w("that the phenomenon they describe **has already happened** in data that survived on Tommy's disk.\n\n")
w("`NEW_SCIENTIFIC_RUNS_USED = 0`. No seed, no world, no trajectory was created, and no replay was needed.\n\n")
w("---\n\n## 0. The result in one paragraph\n\n")
S=AU["SUMMARY"]["B1"]
w("A daughter organising centre is redefined as a **continuously matched component of Y-occupied cells**\n")
w("whose identity survives material change — not as a molecule. The event that proves it is a\n")
w("**complete constituent turnover**: at least one Y birth and at least one Y removal inside one\n")
w("continuous identity interval that is never empty. Applying that criterion to the 128 surviving PQEC01\n")
w("worlds finds **%d centres in %d of %d B1 worlds** that complete a turnover, and **%d of the %d** keep\n"
  %(S["centres_with_complete_turnover"],S["worlds_with_complete_turnover"],S["n_worlds"],
    CA["N_WITH_FUNCTIONAL_CONTINUITY"],CA["N_CANDIDATES"]))
w("producing X at their own cells on both sides of the removal, persisting 99, 217 and 5644 further steps.\n")
w("B2 is structurally incapable — zero Y deaths in 44 worlds — and A0 has no Y dynamics at all. The\n")
w("architecture needs no change, B1 needs no replacement, and one clean prospectively frozen experiment\n")
w("of 128 worlds exists.\n\n")
w("Terminal disposition: `%s`.\n\n"%FD["FINAL_DISPOSITION"])

w("---\n\n## 1. Binding\n\n")
w("Parent `%s`, tip `%s`.\n\n"%(BD["PARENT_PROGRAM"],BD["PARENT_TIP_RESOLVED"]))
w("> %s\n\n"%BD["TIP_DISCREPANCY_NOTED"])
w("No container rollback this mission — %s.\n\n"%BD["ROLLBACK_CHECK"])
w("| Programme | SHA256SUMS verified | bad |\n|---|---|---|\n")
tot=0
for k,v in BD["PROGRAMMES"].items():
    ver=v.get("verification")
    if ver and ver.get("present"):
        w("| %s | %d | %d |\n"%(k,ver["verified"],ver["n_bad"])); tot+=ver["verified"]
    else: w("| %s | — | — |\n"%k)
w("\n%d files verified, 0 bad. Engine byte-unchanged: %s.\n\n"%(tot,BD["ENGINE_MATCHES_FROZEN"]))
w("### Where each executable object actually lives\n\n")
w("| Object | Status |\n|---|---|\n")
for k in ("Y_BIRTH_LAW","Y_DEATH_LAW","Y_DIFFUSION","CENTRE_CLASSIFIER","LOCAL_X_SOURCE_LAW",
          "PERSISTENT_CENTRE_TRACKER","Y_BIRTH_DEATH_LEDGERS","X_BIRTH_LEDGER"):
    v=OM[k]; w("| `%s` | %s |\n"%(k,v.get("status") or v.get("recoverable")))
w("\n> %s\n\n"%OM["THE_DATA_SOURCE_FOR_THIS_MISSION"]["why_no_replay_is_needed"])
w("`CLOC02` and `RSLOC03` are not used as numerical evidence anywhere.\n\n")

w("---\n\n## 2. The old object, stated without dismissing it\n\n")
w("Recomputed from raw FMRT01 bytes: **%d** triggered blocks, **every one** with exactly two Y-occupied\n"%OLD["TRIGGERED_BLOCKS"])
w("cells at maturation, one per centre. Selective removal takes %s Y, global removal takes %s.\n"%(OLD["Y_REMOVED_BY_SELECTIVE"],OLD["Y_REMOVED_BY_GLOBAL"]))
w("A single constituent survives the old 250-step window with probability **%.6f**.\n\n"%OLD["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["analytic_single_Y"])
w("```\nOLD_DAUGHTER_OBJECT = %s\n%s\n```\n\n"%(OLD["OLD_DAUGHTER_OBJECT"],OLD["VERDICT"]))
w("> %s\n\n"%OLD["WHY_NOT_INVALID"])
w("One caveat is recorded rather than glossed: %s\n\n"%OLD["NEW_Y_BIRTHS_BY_THE_DAUGHTER_IN_THE_CAUSAL_WINDOW"]["caveat"])

w("---\n\n## 3. The new object\n\n")
w("**%s.**\n\n"%OB["ORGANISER_LEVEL_CONTINUITY"]["NAME"])
for c in OB["ORGANISER_LEVEL_CONTINUITY"]["an interval [t0,t1] on one continuously matched component C qualifies only if ALL SIX hold"]:
    w("%s\n"%c)
w("\n%s\n\n"%OB["NO_GENEALOGY"])
w("> %s\n\n"%OB["WHY_N_Y_GE_2_IS_NOT_THE_CRITERION"])
w("**Birth is inside the centre by construction, not by assumption.** %s\n\n"%OB["BIRTH_IS_ALWAYS_INSIDE_C"])
w("### A theorem about the orderings\n\n")
O=TE["COMPLETE_TURNOVER"]["orderings_analysed"]
w("%s\n\n"%O["DEATH_THEN_BIRTH"]["proof"])
w("The data confirms it rather than contradicting it: the single observed `DEATH_THEN_BIRTH` case had\n")
w("`N_Y = 2` at the removal step.\n\n")

w("---\n\n## 4. The organiser timescale\n\n")
w("| | B1 | B2 |\n|---|---|---|\n")
w("| muY | %r | %r |\n"%(TS["Y_LIFETIME"]["B1"]["muY"],TS["Y_LIFETIME"]["B2"]["muY"]))
w("| constituent e-folding, steps | %.1f | %.3g |\n"%(TS["Y_LIFETIME"]["B1"]["T_Y_SURVIVAL_e_folding"],TS["Y_LIFETIME"]["B2"]["T_Y_SURVIVAL_e_folding"]))
w("| exact discrete median lifetime | %d | %d |\n"%(TS["Y_LIFETIME"]["B1"]["exact_discrete_median"],TS["Y_LIFETIME"]["B2"]["exact_discrete_median"]))
w("| P(one constituent decays by 11000) | %.6f | %.6g |\n"%(TS["Y_LIFETIME"]["B1"]["P_death_within_11000"],TS["Y_LIFETIME"]["B2"]["P_death_within_11000"]))
a1=TS["POINT_SUMMARY"]["B1"]; a2=TS["POINT_SUMMARY"]["B2"]
w("| local Y-birth hazard, mean per step | %.4e | %.4e |\n"%(a1["per_step_local_Y_birth_hazard"]["mean_of_world_means"],a2["per_step_local_Y_birth_hazard"]["mean_of_world_means"]))
w("| birth-to-death hazard ratio | %.4f | %.3g |\n"%(B1["LOCAL_BIRTH_SCALE"]["birth_to_death_hazard_ratio"],B2["LOCAL_BIRTH_SCALE"]["birth_to_death_hazard_ratio"]))
for T in (1000,2500,5000,HOR):
    w("| P(complete turnover by %d) | %.5f | %.5f |\n"%(T,B1["TURNOVER_FEASIBILITY"]["MODEL_P_COMPLETE_TURNOVER_BY"][str(T)],B2["TURNOVER_FEASIBILITY"]["MODEL_P_COMPLETE_TURNOVER_BY"][str(T)]))
w("| median / q80 / q90 | %s / %s / %s | %s / %s / %s |\n"%(
  B1["TURNOVER_FEASIBILITY"]["MODEL_median"],B1["TURNOVER_FEASIBILITY"]["MODEL_q80"],B1["TURNOVER_FEASIBILITY"]["MODEL_q90"],
  B2["TURNOVER_FEASIBILITY"]["MODEL_median"],B2["TURNOVER_FEASIBILITY"]["MODEL_q80"],B2["TURNOVER_FEASIBILITY"]["MODEL_q90"]))
w("| P(extinct before turnover) | %.5f | %.5f |\n\n"%(B1["LINEAGE_EXTINCTION"]["MODEL_P_extinct_before_turnover"],B2["LINEAGE_EXTINCTION"]["MODEL_P_extinct_before_turnover"]))
w("`None` means the quantile is not reached inside the horizon. The chain is driven step by step by each\n")
w("world's realised hazard sequence; no mean is substituted for a time-dependent hazard, and the single\n")
w("approximation is stated in `DOTC01_ORGANISER_TIMESCALE.md`.\n\n")
w("**The hold is an event, not a clock.** The centre must carry its local X function through at least one\n")
w("complete turnover. The horizon only bounds the observation, and it is not lengthened past 11000.\n\n")

w("---\n\n## 5. The audit: it already happened\n\n")
w("| | B1 | B2 | A0 |\n|---|---|---|---|\n")
for k,lab in (("n_worlds","worlds"),("total_identity_intervals","identity intervals"),
              ("worlds_with_partial_turnover","worlds with partial turnover"),
              ("worlds_with_complete_turnover","worlds with COMPLETE turnover"),
              ("centres_with_complete_turnover","centres with COMPLETE turnover"),
              ("total_Y_births","Y molecules born"),("total_Y_deaths","Y molecules died")):
    w("| %s | %s | %s | %s |\n"%(lab,AU["SUMMARY"]["B1"][k],AU["SUMMARY"]["B2"][k],AU["SUMMARY"]["A0"][k]))
w("\nOrderings at B1: %s.\n\n"%AU["SUMMARY"]["B1"]["orderings"])
w("### The four candidates, each scrutinised\n\n")
w("| World | ordering | interval | first birth | first death | N_Y at removal | steps persisted after | X production before / after | functional |\n|---|---|---|---|---|---|---|---|---|\n")
for c in CA["CASES"]:
    w("| `%s` | %s | [%d, %d] | %d | %d | %s | %d | %s / %s | **%s** |\n"%(
      c["tag"],c["ordering"],c["interval"][0],c["interval"][1],c["first_birth"],c["first_death"],
      c["NY_at_the_death_step_pre_reaction"],c["steps_the_centre_persisted_after_the_removal"],
      c["active_local_X_production_before_removal"],c["active_local_X_production_after_removal"],
      c["FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER"]))
w("\n`%s` in **%d of %d**. The one rejection is honest: in that world the removal fell on the last step of\n"%(
  "FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER",CA["N_WITH_FUNCTIONAL_CONTINUITY"],CA["N_CANDIDATES"]))
w("the identity interval, so the centre never carried its function *through* the turnover.\n\n")
w("> %s\n\n"%CA["X_BIRTH_LAW_USED"])
w("`STATUS = %s`. These are found in data that already existed, by a criterion written before the search.\n"%CA["STATUS"])
w("They are a diagnostic, not a result, and the successor exists to fix that.\n\n")
w("### Turnover is not creation\n\n%s\n\n"%AU["TURNOVER_VS_CREATION"])
J=B1["P_DAUGHTER_FORMATION_AND_FUNCTIONAL_TURNOVER"]
w("In the same 44 worlds, `P(daughter formation AND functional turnover)` = **%d/%d = %.5f**, exact 95 %% %s.\n"
  %(J["k"],J["n"],J["rate"],[round(x,5) for x in J["exact_95"]]))
w("%s %s\n\n"%(J["observed_not_assumed"],J["note"]))

w("---\n\n## 6. Which point, and whether the architecture is the problem\n\n")
w("| | B1 | B2 |\n|---|---|---|\n")
w("| candidate | **%s** | **%s** |\n"%(B1["CANDIDATE"],B2["CANDIDATE"]))
w("| extinction share | %.4f | %.4f |\n"%(B1["LINEAGE_EXTINCTION"]["stop_EXTINCT_share"],B2["LINEAGE_EXTINCTION"]["stop_EXTINCT_share"]))
w("| third-centre share | %.4f | %.4f |\n"%(B1["THIRD_CENTRE_RISK"]["stop_PREMATURE_THIRD_CENTRE_share"],B2["THIRD_CENTRE_RISK"]["stop_PREMATURE_THIRD_CENTRE_share"]))
w("| X integrity failures | %d | %d |\n\n"%(B1["X_INTEGRITY"]["integrity_failures_in_the_developmental_set"],B2["X_INTEGRITY"]["integrity_failures_in_the_developmental_set"]))
w("**B2 is excluded structurally, not statistically.** %s\n\n"%B2["WHY_NOT"])
w("**B1 agrees with its own model**: %s.\n\n"%B1["TURNOVER_FEASIBILITY"]["MODEL_AND_LEDGER_AGREE"])
w("### The architecture question\n\n> %s\n\n"%AR["THE_ANSWER_IS_ALREADY_IN_THE_DATA"])
for k,v in AR["THE_FOUR_CANONICAL_CONFLICTS_AND_THEIR_STATUS"].items():
    w("- *%s* → **%s**\n"%(k,v))
w("\n```\nARCHITECTURE_CHANGE_NECESSITY = %s\n```\n\n%s\n\n"%(AR["ARCHITECTURE_CHANGE_NECESSITY"],AR["WHY_NOT"]))
w("`NEW_PARAMETER_DESIGN_REQUIRED = %s`. %s\n\n"%(AR["NEW_PARAMETER_DESIGN_REQUIRED"],AR["WHY_NO_NEW_POINT"]))

w("---\n\n## 7. Is one clean experiment available?\n\n")
w("Primary endpoint: %s\n\n"%PW["PRIMARY_ENDPOINT"])
w("```\n%s\n```\n\n%s\n\n"%(PW["NULL"]["H0"],PW["NULL"]["basis"]))
w("**Said plainly:** %s\n\n"%PW["NULL"]["honesty"])
w("| Worlds | power at the conservative lower bound %.5f | power at the point estimate %.5f |\n|---|---|---|\n"
  %(PW["PLANNING_INPUTS"]["exact_one_sided_95_lower"],PW["PLANNING_INPUTS"]["developmental_functional_rate"]))
for N,row in PW["POWER_TABLE"].items():
    v=list(row.values()); w("| %s | %.4f | %.4f |\n"%(N,v[0],v[1]))
w("\nRecommended **N = %d**. %s\n\n"%(PW["RECOMMENDED_N"],PW["WHY_128"]))
w("No matched fork: %s\n\n"%PW["NO_MATCHED_FORK"])

w("---\n\n## 8. The independent check\n\n")
w("One checker, zero worlds, importing nothing from the primary analysis: %s.\n\n"
  %"; ".join("%s — %s"%(k,v) for k,v in IC["INDEPENDENCE"].items()))
w("%d quantities checked, **%d disagreements**. `%s`.\n\n"%(IC["N_CHECKED"],IC["N_DISAGREEMENTS"],IC["VERDICT"]))
w("| Quantity | primary | checker |\n|---|---|---|\n")
for r in IC["AGREEMENT_TABLE"]:
    w("| %s | %s | %s |\n"%(r["quantity"],r["primary"],r["checker"]))

w("\n---\n\n## 9. Terminal disposition\n\n```\n%s\n```\n\n"%FD["FINAL_DISPOSITION"])
w("One conditional handoff, created and **not** executed: `%s`.\n\n"%FD["CONDITIONAL_HANDOFF"])
w("%s\n\n"%FD["PARAMETER_POINT"])
w("---\n\n## 10. Status\n\n```\n")
for k in ("MINIMAL_REPRODUCTION_STATUS","STRONG_SELF_REPRODUCTION_STATUS","HEREDITY_STATUS","R3_STATUS",
          "H3_STATUS","REPRODUCTION_STATUS","AUTONOMOUS_COHESION_STATUS","X_LAWSPEC_BASELINE",
          "ARCHITECTURE_CHANGE_NECESSITY"):
    w("%s = %s\n"%(k,FD[k]))
w("NEW_SCIENTIFIC_RUNS_USED = 0\nRETROACTIVE_REPRODUCTION_CLAIM = %s\n```\n\n"%FD["RETROACTIVE_REPRODUCTION_CLAIM"])
w("Nothing here re-scores FMRT01, and nothing here is a reproduction claim. What has been shown is that\n")
w("an organising centre in this engine can lose a constituent, gain a constituent, and go on organising —\n")
w("and that the experiment which would establish that prospectively costs 128 worlds at a point the\n")
w("programme already owns.\n")
open(f"{OUT}/DOTC01_FINAL_REPORT.md","w").write(b.getvalue())
print("report bytes",len(b.getvalue()))
