import json, io, statistics, datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/MRFA01/out"
L=lambda n: json.load(open(f"{OUT}/{n}"))
BD=L("MRFA01_PARENT_BINDING.json"); R1=L("MRFA01_R1_RECOMPUTATION.json")
DA=L("MRFA01_CRITERION_D_AUDIT.json"); SH=L("_sham_falsification.json")
DC=L("MRFA01_THREE_ARM_CAUSAL_DECOMPOSITION.json"); IX=L("MRFA01_CAUSAL_AUTONOMY_INDICES.json")
MX=L("MRFA01_DAUGHTER_INDEPENDENCE_CRITERION_MATRIX.json"); OA=L("MRFA01_OPERATOR_REFERENCE_AUDIT.json")
PT=L("MRFA01_R2_FAILURE_PARTITION.json"); PC=L("MRFA01_POPULATION_VS_CONDITIONAL_ANALYSIS.json")
DG=L("MRFA01_POST_OUTCOME_CRITERION_DIAGNOSTICS.json"); PV=L("MRFA01_FMRT01_PROVENANCE_ADJUDICATION.json")
IC=L("MRFA01_INDEPENDENT_CHECK.json"); PW=L("MRFA01_POWER_ANALYSIS.json"); SF=L("_scale_finding.json")
FD=L("MRFA01_FINAL_DISPOSITION.json")
b=io.StringIO(); w=b.write

w("# MRFA01 — MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01\n## FINAL REPORT\n\n")
w("A zero-run autopsy of FMRT01. It asks one question: did FMRT01 fail because the daughter remained\n")
w("dependent on its parent, or because criterion D did not measure local daughter autonomy?\n\n")
w("**`NEW_SCIENTIFIC_RUNS_USED = 0`.** No seed, no world and no trajectory was created.\n\n")
w("---\n\n## 0. The answer, and the part of it that is uncomfortable\n\n")
w("Criterion D did **not** measure local daughter autonomy. It compares a quantity defined over 6.25 %\n")
w("of the lattice against a reference computed over 100 % of it, and its verdict changes when X is added\n")
w("in a distant corner with no change to the daughter at all. In 20 of 22 blocks D's bound exceeds the\n")
w("daughter's **entire** mass at the moment of intervention, so a daughter that maintained its field\n")
w("perfectly would still be scored a failure.\n\n")
w("But correcting the scope does not rescue the experiment, and this is the finding that matters most.\n")
w("At the B1 point a *centre* is **one Y molecule**. Every triggered block has exactly two Y-occupied\n")
w("cells at maturation; the selective intervention removes one Y and the global intervention removes two.\n")
w("No daughter produced a new Y in any of the 22 blocks, in either arm that kept a daughter. So the\n")
w("object whose autonomy was being tested is a single molecule, its persistence is that molecule's\n")
w("survival, and its 'function' is Y-gated catalysis that the frozen law entails at any cell holding a\n")
w("Y and an X. **No local criterion measurable inside a 250-step hold can separate daughter autonomy\n")
w("from the law restating itself.**\n\n")
w("Terminal disposition: `%s`.\n\n"%FD["FINAL_DISPOSITION"])

w("---\n\n## 1. Binding, after the sixth container rollback\n\n")
w("> %s\n\n"%BD["CONTAINER_INCIDENT"])
V=BD["RESTORATION_VERIFICATION"]
w("Every restored byte was checked against the hashes FMRT01 itself committed: %d + %d + %d files, "
  "%d bad. Engine byte-unchanged: %s.\n\n"%(V["FMRT01_SHA256SUMS_entries"],V["FMRT01_RAW_SHA256SUMS_entries"],
  V["METHODS_CLOSURE_entries"],len(V["FMRT01_SHA256SUMS_bad"])+len(V["FMRT01_RAW_SHA256SUMS_bad"])+len(V["METHODS_CLOSURE_bad"]),
  V["ENGINE_MATCHES_FROZEN"]))
A=BD["EXACT_ACCOUNTING"]
w("| Accounting, recomputed from bytes | |\n|---|---|\n")
w("| blocks seeded | %d |\n| blocks triggered | %d |\n| blocks not triggered | %d |\n"%(A["blocks_seeded"],A["blocks_triggered"],A["blocks_not_triggered"]))
w("| technical replacements | %d |\n| reserve use | %d |\n| raw archives | %d |\n\n"%(A["technical_replacements"],A["reserve_use"],A["raw_archives"]))
F=BD["PRE_INTERVENTION_FORK_IDENTITY"]
w("### The §1 gate\n\n%s\n\n```\nPRE_INTERVENTION_PHYSICAL_STATE_IDENTICAL = %s\nPRE_INTERVENTION_RNG_STATE_IDENTICAL      = %s\n```\n\n**%s**\n\n"
  %(F["METHOD"],F["PRE_INTERVENTION_PHYSICAL_STATE_IDENTICAL"],F["PRE_INTERVENTION_RNG_STATE_IDENTICAL"],F["GATE"]))
R=BD["RECONSTRUCTION"]
w("The reconstruction that produced those three hashes is a **bit-exact deterministic replay** of the 22\n")
w("already executed frozen seeds — `%s` — accepted only because it reproduced every archived hash,\n"%R["STATUS"])
w("fingerprint, scalar and series in %d of %d triads. Its outputs never enter a denominator.\n\n"%(R["bit_exact_triads"],R["of"]))
w("It exists because the archives do not contain what §5 requires: they store world-level totals every 25\n")
w("steps and record the GLOBAL arm's daughter mass as `null`, because that code path needed a surviving Y\n")
w("component to place the disc.\n\n")

w("---\n\n## 2. What FMRT01 actually established, preserved\n\n")
FR=R1["FRACTION_NEWLY_PRODUCED"]
w("R1 recomputed molecule by molecule: **%d of 22** by calculator A, **%d of 22** by calculator B, "
  "against FMRT01's reported 22.\n\n"%(R1["CALCULATOR_A_R1_EXACT"],R1["CALCULATOR_B_R1_EXACT"]))
w("Fraction of the daughter's local X that was produced *after* the daughter lineage originated:\n")
w("min %.4f, q1 %.4f, median %.4f, q3 %.4f, max %.4f.\n\n"%(FR["min"],FR["q1"],FR["median"],FR["q3"],FR["max"]))
w("```\n%s\n```\n\n"%R1["LABEL"])
w("This is **not** minimal reproduction and is not labelled as such.\n\n")
E=R1["CRITERION_E"]
w("Criterion E recomputed: positive in %d/%d SELECTIVE, %d/%d SHAM, %d/%d GLOBAL. Median accepted births\n"
  %(E["SELECTIVE_positive"],E["of"],E["SHAM_positive"],E["of"],E["GLOBAL_positive"],E["of"]))
w("inside the fixed daughter disc: SELECTIVE %s, SHAM %s, GLOBAL %s.\n\n"
  %(E["median_births_in_the_fixed_daughter_disc"]["SELECTIVE"],E["median_births_in_the_fixed_daughter_disc"]["SHAM"],
    E["median_births_in_the_fixed_daughter_disc"]["GLOBAL"]))
w("> %s\n\n"%E["E_ALONE_IS_NOT_INDEPENDENCE"])

w("---\n\n## 3. Criterion D\n\n```\n%s\n```\n\n"%DA["EXACT_FORMULA"])
Q=DA["QUANTITATIVE_CONSEQUENCES"]
w("| | |\n|---|---|\n")
w("| Left-hand side | %s |\n"%DA["WHAT_D_COMPARES"]["left_hand_side"])
w("| Right-hand side | %s |\n"%DA["WHAT_D_COMPARES"]["right_hand_side"])
w("| Reference derived from | `%s` |\n"%DA["WHAT_D_COMPARES"]["reference_derived_from"])
w("| Median bound | %s |\n| Median daughter mass at intervention | %s |\n"%(Q["median_bound"],Q["median_daughter_mass_at_intervention"]))
w("| Blocks where the bound exceeds the daughter's entire mass | %d/%d |\n"%(Q["blocks_where_the_bound_EXCEEDS_the_daughters_entire_mass_at_intervention"],Q["of_blocks"]))
w("| Bound / the daughter's own decayed stock | %.3f |\n"%Q["bound_as_multiple_of_the_daughters_own_decayed_stock"])
w("| Measured old material in the fixed disc (GLOBAL arm) | %s |\n"%Q["measured_old_material_in_the_fixed_disc_GLOBAL_arm_median"])
w("| Analytic bound / measured old material | %.2f |\n\n"%Q["analytic_bound_over_measured_old_material"])
w("**World-size test.** Scaling the world's X while leaving the daughter untouched:\n\n")
w("| World X scaled | Median bound | SELECTIVE passes |\n|---|---|---|\n")
for k,v in DA["WORLD_SIZE_SENSITIVITY"].items():
    w("| %s | %s | %s/22 |\n"%(k.replace("world_X_",""),v["median_bound"],v["SELECTIVE_passes"]))
w("\n%s\n\n"%DA["WORLD_SIZE_ARGUMENT"])
w("D **is** alpha-valid, and that is worth preserving. %s\n\n"%DA["ALPHA_VALIDITY_IS_NOT_ENOUGH"])
w("```\nCLASSIFICATION = %s\n```\n\n%s\n\n"%(DA["CLASSIFICATION"],DA["CLASSIFICATION_BASIS"]))

w("---\n\n## 4. The SHAM falsification\n\n")
S=SH["RECOMPUTED_FROM_BYTES"]
w("SHAM keeps both centres and removes %d molecules. Its daughter survives **%d/%d** and produces X in the\n"%(S["SHAM_removed_total"],S["SHAM_daughter_survives"],S["of"]))
w("fixed disc **%d/%d**. It still fails D in **%d/%d**. FMRT01 reported 8/22; recomputed 8/22, agrees: %s.\n\n"
  %(S["SHAM_produces_X_in_the_fixed_daughter_disc"],S["of"],S["SHAM_criterion_D_fails"],S["of"],S["AGREES"]))
for k,v in SH["HYPOTHESES"].items(): w("- **%s** → `%s`\n"%(k.split("_")[0],v["verdict"]))
w("\nConclusion: **%s — D is mis-scaled relative to local function.** %s\n\n"%(SH["CONCLUSION"],SH["THE_PHYSICAL_REASON"]))

w("---\n\n## 5. The three-arm causal decomposition\n\n")
w("Windows predeclared from physics before any trajectory was inspected. One X e-folding is\n")
w("%.4f steps; FMRT01's hold is 250 steps = **%.6f e-foldings**, so only the first of the three\n"%(DC["E_FOLDING_STEPS"],DC["T_HOLD_IN_E_FOLDINGS"]))
w("requested windows exists. `%s` — extending the arms would be a new trajectory, not a reconstruction.\n\n"%DC["WINDOWS_2_AND_3_E_FOLDINGS"])
w("Geometry: %s.\n\n"%DC["GEOMETRY"])
blocks=DC["BLOCKS"]
w("| Sub-window | daughter-only effect (mass) | parent increment (mass) | daughter-only (births) |\n|---|---|---|---|\n")
for n,_,_ in [(x["name"],x["lo"],x["hi"]) for x in DC["WINDOWS_PREDECLARED"]]:
    d=[r[n]["DAUGHTER_ONLY_EFFECT_mass"] for r in blocks]; p=[r[n]["PARENT_INCREMENT_mass"] for r in blocks]
    db=[r[n]["DAUGHTER_ONLY_EFFECT_birth"] for r in blocks]
    w("| %s | %+.2f | %+.2f | %+.2f |\n"%(n,statistics.median(d),statistics.median(p),statistics.median(db)))
em={a:[r["endpoint"]["mass"][a] for r in blocks] for a in ("SELECTIVE","SHAM","GLOBAL")}
bt={a:[r["endpoint"]["births_total"][a] for r in blocks] for a in ("SELECTIVE","SHAM","GLOBAL")}
w("\n| Arm | Endpoint fixed-disc mass (median) | Total fixed-disc births (median) |\n|---|---|---|\n")
for a in ("SELECTIVE","SHAM","GLOBAL"):
    w("| %s | %.1f | %.1f |\n"%(a,statistics.median(em[a]),statistics.median(bt[a])))
w("\n**GLOBAL produced exactly zero births inside the daughter disc, in every block, total.** X birth is\n")
w("Y-gated in the frozen engine, so production is an unambiguous signature of a local Y source — and\n")
w("under SELECTIVE the only Y left in the world is the daughter's.\n\n")
w("The parent adds almost nothing to the daughter's local field for the first two-thirds of the\n")
w("e-folding (parent increment %+.2f then %+.2f) and only %+.2f in the last third.\n\n"
  %(statistics.median([r[DC["WINDOWS_PREDECLARED"][0]["name"]]["PARENT_INCREMENT_mass"] for r in blocks]),
    statistics.median([r[DC["WINDOWS_PREDECLARED"][1]["name"]]["PARENT_INCREMENT_mass"] for r in blocks]),
    statistics.median([r[DC["WINDOWS_PREDECLARED"][2]["name"]]["PARENT_INCREMENT_mass"] for r in blocks])))

w("---\n\n## 6. The autonomy indices, after their audit\n\n")
AU=IX["AUDIT_PERFORMED_BEFORE_LOOKING_AT_THE_DISTRIBUTION"]
w("The audit was done first. %s\n\n"%AU["why_the_birth_index_is_better_conditioned"])
w("- Mass denominator non-positive in %d block(s); birth denominator non-positive in %d.\n"
  %(AU["denominator_sign_and_stability"]["mass"]["non_positive_blocks"],AU["denominator_sign_and_stability"]["birth"]["non_positive_blocks"]))
w("- Is mass the right response variable? %s\n"%AU["is_mass_the_right_response_variable"])
OV=AU["does_SHAM_contain_parent_field_overlap_in_the_daughter_disc"]
w("- Parent/daughter discs are disjoint in %d blocks and overlap in %d. %s. A_birth median is %.4f on the\n"
  %(OV["disjoint_blocks"],OV["overlapping_blocks"],OV["consequence"],OV["A_birth_median_disjoint"]))
w("  disjoint subset and %.4f on the overlapping one, so the concern is real and does not drive the result.\n\n"%OV["A_birth_median_overlapping"])
AM=IX["A_MASS"]; AB=IX["A_BIRTH"]
w("| Index | n | median | q1 | q3 | ≥0.5 | ≥0.8 | >1 | <0 |\n|---|---|---|---|---|---|---|---|---|\n")
w("| A_mass | %d | %.4f | %.4f | %.4f | %d | %d | %d | %d |\n"%(AM["n"],AM["median"],AM["q1"],AM["q3"],AM["ge_0_5"],AM["ge_0_8"],AM["gt_1"],AM["lt_0"]))
w("| A_birth | %d | %.4f | %.4f | %.4f | %d | %d | %d | %d |\n\n"%(AB["n"],AB["median"],AB["q1"],AB["q3"],AB["ge_0_5"],AB["ge_0_8"],AB["gt_1"],AB["lt_0"]))
w("A_birth ≈ 1 means the daughter alone produces about as much new X in its own disc as it does with the\n")
w("parent present. `NO_THRESHOLD_IS_CHOSEN_FROM_FMRT01_OUTCOMES = %s`.\n\n"%IX["NO_THRESHOLD_IS_CHOSEN_FROM_FMRT01_OUTCOMES"])

w("---\n\n## 7. What the object under test actually is\n\n")
TS=SF["TIMESCALES"]
w("| | |\n|---|---|\n")
w("| Y-occupied cells at maturation | 2, in every block |\n")
w("| N_Y at maturation | %d |\n"%SF["NY_AT_t_m"])
w("| Y removed by SELECTIVE / GLOBAL | %s / %s |\n"%(SF["Y_REMOVED_BY_SELECTIVE"],SF["Y_REMOVED_BY_GLOBAL"]))
w("| Daughters that produced a new Y during the hold | SELECTIVE %d, SHAM %d, of %d |\n"
  %(SF["DAUGHTER_EVER_PRODUCED_A_NEW_Y_DURING_THE_HOLD"]["SELECTIVE"],SF["DAUGHTER_EVER_PRODUCED_A_NEW_Y_DURING_THE_HOLD"]["SHAM"],SF["DAUGHTER_EVER_PRODUCED_A_NEW_Y_DURING_THE_HOLD"]["of"]))
w("| Single-Y survival over the hold | %.6f |\n"%SF["SINGLE_Y_SURVIVAL_OVER_THE_HOLD"])
w("| Observed daughter persistence | %.4f |\n"%SF["OBSERVED_DAUGHTER_PERSISTENCE"])
w("| X e-folding | %.1f steps |\n| Y decay e-folding | %.1f steps |\n"%(TS["X_e_folding_steps"],TS["Y_decay_e_folding_steps"]))
w("| Hold, in X e-foldings | %.4f |\n| Hold, in Y e-foldings | %.4f |\n"%(TS["T_HOLD_in_X_e_foldings"],TS["T_HOLD_in_Y_e_foldings"]))
w("| Empirical single-centre → two-centre waiting time | %s steps |\n"%TS["empirical_Y_reproduction_waiting_time_median_t_m"])
w("| Hold as a fraction of that | %.4f |\n"%TS["T_HOLD_as_fraction_of_that"])
w("| Analytic Y-birth waiting time | %.0f–%.0f steps |\n\n"%(TS["analytic_Y_birth_waiting_time_steps"][1],TS["analytic_Y_birth_waiting_time_steps"][0]))
w("> %s\n\n"%SF["CONSEQUENCE"])

w("---\n\n## 8. Where the 19 R2 failures are, and the 17 that matter\n\n")
w("| Class | Count |\n|---|---|\n")
for k,v in PT["PARTITION"].items(): w("| `%s` | %d |\n"%(k,v))
w("\nSum %d of %d, `IS_A_PARTITION = %s`.\n\n"%(PT["SUM"],PT["N_TRIGGERED"],PT["IS_A_PARTITION"]))
EP=PT["E_PASSED_BUT_FROZEN_R2_FAILED"]
w("### The %d worlds where E passed and frozen R2 failed\n\n%s\n\n"%(EP["count"],EP["why"]))
w("| | |\n|---|---|\n")
w("| Median bound | %s |\n| Median daughter mass at intervention | %s |\n"%(EP["median_bound"],EP["median_daughter_mass_at_intervention"]))
w("| Median excess of the bound over that mass | +%s |\n"%EP["median_bound_minus_daughter_mass_at_intervention"])
w("| Blocks where the bound exceeded the daughter's entire mass | %d of %d |\n"%(EP["blocks_where_the_bound_exceeded_the_daughters_ENTIRE_mass_at_intervention"],EP["count"]))
w("| Median new X produced in the fixed daughter disc | %s |\n"%EP["median_new_X_produced_in_the_fixed_daughter_disc"])
w("| Median GLOBAL control births in the same disc | %s |\n\n"%EP["median_GLOBAL_control_births_in_the_same_disc"])

w("---\n\n## 9. Population incidence and conditional autonomy, kept apart\n\n")
w("%s\n\n"%PC["WHY"])
w("| | k/n | rate | exact 95 %% |\n|---|---|---|---|\n")
for k in ("P_TRIGGER","P_AUTONOMY_GIVEN_TRIGGER_FROZEN_R2","P_JOINT_FROZEN_R2"):
    v=PC[k]; w("| `%s` | %d/%d | %.6f | [%.6f, %.6f] |\n"%(k,v["k"],v["n"],v["rate"],v["exact_95"][0],v["exact_95"][1]))
w("\n---\n\n## 10. Candidate criteria applied to the existing worlds — diagnostics only\n\n")
w("`STATUS = %s`. %s\n\n"%(DG["STATUS"],DG["NO_P_VALUE_IS_PUBLISHED_HERE"]))
w("| Candidate | SELECTIVE | SHAM | GLOBAL | population rate over 85 |\n|---|---|---|---|---|\n")
for k,v in DG["CANDIDATES"].items():
    w("| `%s` | %s | %s | %s | %.6f |\n"%(k,v["SELECTIVE"],v["SHAM"],v["GLOBAL"],v["population_rate"]))
w("\n---\n\n## 11. The single-centre operator as a reference\n\n")
w("| Aspect | Comparable? |\n|---|---|\n")
for c in OA["COMPARISON"]: w("| %s | %s |\n"%(c["aspect"],c["comparable"]))
w("\n```\n%s\n```\n\n"%OA["VERDICT"])
for g in OA["GROUNDS"]: w("- %s\n"%g)
w("\nTherefore: %s. This choice is load-bearing.\n\n"%OA["THEREFORE"])

w("---\n\n## 12. FMRT01's provenance defects, classified and not repaired\n\n")
w("`NO_FMRT01_JSON_WAS_ALTERED = %s`.\n\n"%PV["NO_FMRT01_JSON_WAS_ALTERED"])
w("- **P1** trigger leakage through raw naming → `%s`\n"%PV["P1_TRIGGER_LEAKAGE_THROUGH_RAW_NAMING"]["CLASSIFICATION"])
w("- **P2** durability-gate self-reference → `%s`\n"%PV["P2_DURABILITY_GATE_SELF_REFERENCE"]["CLASSIFICATION"])
w("- **P3**, found by this autopsy: %s → `%s`\n\n"%(PV["P3_FOUND_BY_THIS_AUTOPSY__WORLD_COUNT_OVERSTATED"]["what"],PV["P3_FOUND_BY_THIS_AUTOPSY__WORLD_COUNT_OVERSTATED"]["CLASSIFICATION"]))
w("`ORIGINAL_MACHINE_DISPOSITION = %s`\n`FMRT01_ADJUDICATED_DISPOSITION = %s`\n\n"%(PV["ORIGINAL_MACHINE_DISPOSITION"],PV["FMRT01_ADJUDICATED_DISPOSITION"]))
w("%s\n\n`A_BROKEN_DURABILITY_BOOLEAN_DOES_NOT_QUALIFY_A_FAILED_TEST = %s`.\n\n"%(PV["SCIENTIFIC_CAUSAL_RESULT"],PV["A_BROKEN_DURABILITY_BOOLEAN_DOES_NOT_QUALIFY_A_FAILED_TEST"]))

w("---\n\n## 13. Two independent calculators\n\n")
w("They share the raw archives and nothing else: %s.\n\n"%"; ".join("%s — A: %s, B: %s"%(k,v["A"],v["B"]) for k,v in IC["INDEPENDENCE"].items() if isinstance(v,dict)))
w("%d quantities checked, **%d disagreements**. `%s`.\n\n"%(IC["N_CHECKED"],IC["N_DISAGREEMENTS"],IC["VERDICT"]))
O=IC["ONE_NUMERIC_DIFFERENCE_RECORDED"]
w("One numeric difference is recorded rather than hidden: %s, A = %r, B = %r, relative difference %.3e.\n"%(O["quantity"],O["A"],O["B"],O["relative_difference"]))
w("Cause: %s. Load-bearing: %s — %s.\n\n"%(O["cause"],O["load_bearing"],O["why_not"]))

w("---\n\n## 14. Eligibility for a fresh test\n\n")
w("| # | Condition | Met |\n|---|---|---|\n")
for c in PW["SEVEN_CONDITIONS"]: w("| %d | %s | **%s** |\n"%(c["n"],c["condition"],c["met"]))
w("\n%d of 7. `FRESH_TEST_ELIGIBLE = %s`.\n\n"%(PW["N_MET"],PW["FRESH_TEST_ELIGIBLE"]))
for c in PW["SEVEN_CONDITIONS"]:
    if not c["met"]: w("**Condition %d fails.** %s\n\n"%(c["n"],c["evidence"]))
PI=PW["PLANNING_INPUTS"]
w("Had it been eligible, the null would have been exact — `%s`, %s — and the exact unconditional power\n"%(PW["NULL"]["H0"],PW["NULL"]["basis"].split(".")[0]))
w("at 85 blocks on the conservative planning inputs (q = %.4f, P(trigger) = %.4f) is **%.4f**, below 0.80.\n\n"
  %(PI["q_conservative_lower_95"],PI["P_trigger_conservative_lower_95"],PW["POWER_AT_85_BLOCKS_ON_THE_CONSERVATIVE_INPUT"]))
w("| Blocks | q=0.95 | q=0.90 | q=0.85 | q=0.80 | q=0.75 |\n|---|---|---|---|---|---|\n")
for nb,row in PW["EXACT_UNCONDITIONAL_POWER"].items():
    w("| %s | %.4f | %.4f | %.4f | %.4f | %.4f |\n"%(nb,row["q=0.95"],row["q=0.90"],row["q=0.85"],row["q=0.80"],row["q=0.75"]))

w("\n---\n\n## 15. Terminal disposition\n\n```\n%s\n```\n\n"%FD["FINAL_DISPOSITION"])
w("### The exact missing object\n\n")
for o in FD["THE_EXACT_MISSING_OBJECT"]: w("1. **%s** — %s\n\n"%(o["object"],o["why"]))
w("### No handoff is created\n\n%s\n\n"%FD["CONDITIONAL_HANDOFF"])
w("A successor becomes eligible only with:\n\n")
for x in FD["WHAT_WOULD_MAKE_A_SUCCESSOR_ELIGIBLE"]: w("- %s\n"%x)
w("\n%s\n\n"%FD["PARAMETER_POINT"])
w("---\n\n## 16. Status\n\n```\n")
for k in ("MINIMAL_REPRODUCTION_STATUS","STRONG_SELF_REPRODUCTION_STATUS","HEREDITY_STATUS","R3_STATUS",
          "H3_STATUS","REPRODUCTION_STATUS","AUTONOMOUS_COHESION_STATUS","X_LAWSPEC_BASELINE",
          "ARCHITECTURE_CHANGE_NECESSITY"):
    w("%s = %s\n"%(k,FD[k]))
w("NEW_SCIENTIFIC_RUNS_USED = 0\n```\n\n")
w("FMRT01's frozen result is unchanged and no retroactive success is claimed: %s.\n"%FD["RETROACTIVE_FMRT01_SUCCESS"])
open(f"{OUT}/MRFA01_FINAL_REPORT.md","w").write(b.getvalue())
print("report bytes",len(b.getvalue()))
