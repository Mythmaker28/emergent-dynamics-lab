import json, math, hashlib, os, sys, subprocess
import numpy as np
OUT="/home/claude/FTCTR01/out"
FP=json.load(open(f"{OUT}/FTCTR01_FIRST_PASSAGE.json"))
OB=json.load(open(f"{OUT}/FTCTR01_SEPARATION_VS_MATURATION.json"))
M=OB["MATURATION"]; E=FP["E_tau"]

TS = {
 "T_GEOMETRIC_FORMATION": {"definition":"first step at which the toroidal min-image distance between two Y exceeds CORE_R = 5.0, i.e. the step the FLCR01 classifier first returns state S",
   "exact_expectation_steps":E,"exact_sd":FP["SD_tau"],"exact_median":FP["median_tau"],
   "observed_mean_steps":OB["SEPARATION_DELAY_first_S_minus_first_birth"]["mean"],
   "observed_n_worlds":OB["SEPARATION_DELAY_first_S_minus_first_birth"]["n"],
   "STATUS":"DERIVED_EXACTLY_AND_CONFIRMED_AGAINST_THE_RECORD"},
 "T_X_MATURATION": {"definition":"steps for a NEW centre to build its X cloud from empty to the level an established organiser holds",
   "e_folding_steps":M["e_folding_steps_exact"],
   "steps_at_f_0.80":M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["steps_from_empty"],"maturation_time_vs_response_fraction":M["MATURATION_TIME_VS_RESPONSE_FRACTION"],
   "STATUS":"DERIVED__BUT_THE_TARGET_LEVEL_IS_NOT_YET_A_QUALIFIED_THRESHOLD"},
 "T_FUNCTIONAL_TWO_CENTRE": {"definition":"T_GEOMETRIC_FORMATION + T_X_MATURATION — the step at which BOTH centres hold a matured X response, not merely a spatial separation",
   "lower_bound_steps_at_f_0.80":E+M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["steps_from_empty"],"lower_bound_steps_at_one_e_folding":E+M["e_folding_steps_exact"],
   "STATUS":"NOT_MEASURED_IN_ANY_EXISTING_RECORD"},
 "T_FUNCTIONAL_HOLD": {"definition":"duration for which the two matured centres must both persist",
   "H_HOLD_used_by_FLCR01":M["H_HOLD_observed_median_S_run"],
   "H_HOLD_provenance":"median of an OBSERVED distribution of S-runs (n_episodes=%d), NOT a derived requirement" % M["n_S_episodes"],
   "fraction_of_X_cloud_built_in_H_HOLD_steps":M["fraction_of_cloud_built_in_H_HOLD_steps"],
   "SHORTFALL_FACTOR_at_f_0.80":M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["shortfall_factor_vs_H_HOLD"],
   "MIN_SHORTFALL_FACTOR_over_grid":M["MIN_SHORTFALL_FACTOR_over_grid"],
   "STATUS":"UNDERSPECIFIED_BY_MORE_THAN_AN_ORDER_OF_MAGNITUDE"},
 "T_THIRD_CENTRE": {"definition":"step at which a third spatial centre appears (classifier state P) after state S was reached",
   "worlds_reaching_S":OB["THIRD_CENTRE"]["worlds_reaching_S"],
   "of_which_later_reach_P":OB["THIRD_CENTRE"]["of_which_later_reach_P"],
   "fraction":OB["THIRD_CENTRE"]["fraction"],
   "STATUS":"MEASURED__ORDERING_RELATIVE_TO_FUNCTION_IS_NOT_YET_DEFINED"},
 "T_LINEAGE_EXTINCTION": {"definition":"step at which Y reaches zero (classifier state E)",
   "STATUS":"MEASURED_PER_WORLD_IN_THE_PQEC01_RECORD__NOT_A_LIMITING_TIMESCALE_AT_THIS_POINT"},
}

RES={
 "PROGRAMME":"FTCTR01 — FUNCTIONAL-TWO-CENTRE TIMESCALE REDERIVATION",
 "RECORD_STATUS":"RECONSTRUCTED_AFTER_CONTAINER_ROLLBACK__EVERY_VALUE_RECOMPUTED_FROM_SOURCE",
 "NEW_ENGINE_RUNS":0,"NEW_WORLD_CONSTRUCTIONS":0,"NEW_SEEDS":0,"NEW_PARAMETER_POINTS":0,
 "EXACT_SEPARATION_CLOCK":FP,
 "OBSERVED_AND_MATURATION":{k:v for k,v in OB.items() if k!="PER_WORLD"},
 "SIX_TIMESCALES":TS,
 "PRINCIPAL_FINDINGS":[
  "The exact expected first passage of the relative coordinate to a toroidal separation greater than CORE_R is %.4f steps, obtained by two independent deterministic methods that agree to %.1e. The frozen TAU_SEP = 125.0 understates it by %.3f%% of the frozen value (%.3f%% of the exact value)."%(E,FP["abs_difference"],FP["frozen_understates_by_percent_of_frozen"],FP["frozen_understates_by_percent_of_exact"]),
  "The per-axis single-step displacement variance derived from the engine's own four ordered sub-shifts is %.10f, which reproduces the frozen a_X = 0.05 exactly; the relative-coordinate diffusion constant reproduces the frozen D_relative = 0.05 exactly. The kinetic law used for the clock is therefore the engine's, not an approximation of it."%FP["variance_one_axis_one_step"],
  "The observed separation delay over the %d PQEC01 worlds that reached two spatial centres has mean %.5f (sd %.5f); the exact expectation lies %.3f standard errors away, i.e. consistent."%(OB["SEPARATION_DELAY_first_S_minus_first_birth"]["n"],OB["SEPARATION_DELAY_first_S_minus_first_birth"]["mean"],OB["SEPARATION_DELAY_first_S_minus_first_birth"]["sd"],OB["z_sep_vs_exact"]),
  "GEOMETRIC SEPARATION IS NOT FUNCTIONAL SUCCESS. A new centre needs on the order of %.1f steps to build an X cloud to the level an established organiser holds, whereas H_HOLD = %.1f steps admits only %.2f%% of that cloud. The functional hold criterion used by FLCR01 is underspecified by a factor of %.1f."%(M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["steps_from_empty"],M["H_HOLD_observed_median_S_run"],100*M["fraction_of_cloud_built_in_H_HOLD_steps"],M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["shortfall_factor_vs_H_HOLD"]),
  "AUDIT OF THE HISTORICAL '101 accepted X births': the value 101.14 is the pre-removal X level of ONE arm (R/seed9302) of the OBTC02 causal-source-dependence test. The three R arms give %s. It was never a derived threshold and is not defensible as one."%(M["historical_101_binding"]["all_R_arm_pre_removal_levels"],),
  "Of the %d worlds that reached two spatial centres, %d later reached three or more (%.1f%%). A third centre is not a rare perturbation at this point."%(OB["THIRD_CENTRE"]["worlds_reaching_S"],OB["THIRD_CENTRE"]["of_which_later_reach_P"],100*OB["THIRD_CENTRE"]["fraction"]),
  "P(an S episode lasts at least one X e-folding) = %.6f over %d episodes."%(M["P_hold_ge_one_e_folding"],M["n_S_episodes"]),
 ],
 "WHAT_THIS_DOES_NOT_ESTABLISH":[
  "H3_STATUS = NOT_TESTED","REPRODUCTION_STATUS = NOT_TESTED","HEREDITY_STATUS = NOT_TESTED",
  "AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED","X_LAWSPEC_BASELINE = UNCHANGED",
  "ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED",
  "FOUNDER_SURVIVAL_GATE = rejected (inherited from FLCR01, unchanged)",
  "PARTICLE_GENEALOGY_REQUIRED = false (inherited from FLCR01, unchanged)"],
 "DISCREPANCY_AGAINST_THE_DESTROYED_RUN":{
   "SD_tau":{"destroyed_run_recorded":104.0536,"reconstructed":FP["SD_tau"],
     "resolution":"the reconstructed value is confirmed by two independent exact methods (linear solve of (I-Q)m2 = 1 + 2 Q m1, and the survival identity E[t^2] = sum_t (2t+1) P(tau>t)) which agree to machine precision; the earlier figure is superseded"},
   "maturation_build_time":{"destroyed_run_recorded":"451.6 steps / SHORTFALL 28.2","reconstructed":M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["steps_from_empty"],
     "resolution":"the earlier figure pinned maturation to ONE implicit response fraction (101/120.845 = 0.8358). That is exactly the step the mission forbids taking silently. This reconstruction reports the maturation time as an explicit function of the chosen response fraction f. Even at the most permissive f = 0.50 the shortfall factor is %.4f, and at f = 0.80 it is %.4f. The conclusion — H_HOLD = 16 is short by at least an order of magnitude — holds for EVERY f on the grid and does not depend on the choice."%(M["MIN_SHORTFALL_FACTOR_over_grid"],M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["shortfall_factor_vs_H_HOLD"])},
   "z_scores":{"destroyed_run_recorded":[-0.187,-0.305],"reconstructed":[OB["z_sep_vs_exact"],OB["z_cross_vs_exact"]],
     "resolution":"both are far inside 2 sigma; the qualitative conclusion (exact clock consistent with the record) is unchanged"}},
}
json.dump(RES,open(f"{OUT}/FTCTR01_RESULT.json","w"),indent=2)

L=[]
L.append("# FTCTR01 — REDERIVATION DE L'HORLOGE FONCTIONNELLE A DEUX CENTRES")
L.append("")
L.append("**Statut de l'enregistrement : RECONSTRUIT** apres le retour en arriere du conteneur.")
L.append("Chaque valeur ci-dessous est **recalculee depuis la source**, aucune n'est recopiee.")
L.append("")
L.append("`NEW_ENGINE_RUNS = 0` — `NEW_WORLD_CONSTRUCTIONS = 0` — `NEW_SEEDS = 0` — `NEW_PARAMETER_POINTS = 0`")
L.append("")
L.append("## 1. L'horloge de separation, exacte")
L.append("")
L.append("| Quantite | Valeur |")
L.append("|---|---|")
L.append("| Variance de deplacement par axe et par pas | %.10f |"%FP["variance_one_axis_one_step"])
L.append("| `a_X` gele | %s — **identique** |"%FP["frozen_a_X"])
L.append("| `D_relative` derive / gele | %.10f / %s — **identique** |"%(FP["D_relative_derived"],FP["frozen_D_relative"]))
L.append("| Etats transitoires / absorbants | %d / %d |"%(FP["n_transient_states"],FP["n_absorbing_states"]))
L.append("| `E[tau]` methode A (solve lineaire) | %.14f |"%FP["E_tau_method_A_linear_solve"])
L.append("| `E[tau]` methode B (somme de survie) | %.14f |"%FP["E_tau_method_B_survival_sum"])
L.append("| Ecart entre methodes | %.2e — **accord** |"%FP["abs_difference"])
L.append("| Ecart-type (deux methodes, accord) | %.10f |"%FP["SD_tau"])
L.append("| Mediane / IQR | %.0f / %.0f–%.0f |"%(FP["median_tau"],FP["q25_tau"],FP["q75_tau"]))
L.append("| `TAU_SEP` gele | %.1f |"%FP["TAU_SEP_frozen"])
L.append("| Rapport exact/gele | %.10f |"%FP["ratio_exact_over_frozen"])
L.append("| Sous-estimation | **%.3f %%** du gele (%.3f %% de l'exact) |"%(FP["frozen_understates_by_percent_of_frozen"],FP["frozen_understates_by_percent_of_exact"]))
L.append("")
L.append("## 2. Confrontation au dossier observe")
L.append("")
s=OB["SEPARATION_DELAY_first_S_minus_first_birth"]; c=OB["CROSSING_DELAY_max_pair_dist_gt_CORE_R"]
L.append("| Quantite | n | mediane | moyenne | ecart-type | z vs exact |")
L.append("|---|---|---|---|---|---|")
L.append("| Delai de separation (`first_S` − premiere naissance) | %d | %.0f | %.11f | %.11f | %.4f |"%(s["n"],s["median"],s["mean"],s["sd"],OB["z_sep_vs_exact"]))
L.append("| Franchissement `max_pair_dist > CORE_R` | %d | %.0f | %.11f | %.11f | — |"%(c["n"],c["median"],c["mean"],c["sd"]))
L.append("")
L.append("Sur %d mondes, %d atteignent deux centres spatiaux. L'attente exacte est **compatible** avec le dossier."%(OB["N_WORLDS"],s["n"]))
L.append("")
L.append("## 3. L'horloge de maturation — le resultat principal")
L.append("")
L.append("| Quantite | Valeur |")
L.append("|---|---|")
L.append("| Temps de e-folding du champ X (exact) | %.11f |"%M["e_folding_steps_exact"])
L.append("| conforme a la valeur gelee | %s |"%M["e_folding_matches_frozen"])
L.append("| `N_X` stationnaire mesure (%d mondes PQEC01) | %.5f (ecart-type %.5f) |"%(M["N_X_stationary_n_worlds"],M["N_X_stationary_non_extinct_worlds"],M["N_X_stationary_sd"]))
L.append("| Niveaux `pre_removal_level` des 3 bras R d'OBTC02 | %s |"%M["historical_101_binding"]["all_R_arm_pre_removal_levels"])
L.append("")
L.append("**Temps de maturation en fonction de la fraction de reponse choisie** (`t(f) = ln(1-f)/ln(1-muX)`) :")
L.append("")
L.append("| fraction de reponse `f` | pas depuis le vide | facteur de deficit vs `H_HOLD` |")
L.append("|---|---|---|")
for cv in M["MATURATION_TIME_VS_RESPONSE_FRACTION"]:
    L.append("| %.4f%s | %.5f | **%.4f** |"%(cv["response_fraction"], " (un e-folding)" if abs(cv["response_fraction"]-(1-1/2.718281828459045))<1e-6 else "", cv["steps_from_empty"], cv["shortfall_factor_vs_H_HOLD"]))
L.append("")
L.append("| Quantite | Valeur |")
L.append("|---|---|")
L.append("| `H_HOLD` employe par FLCR01 | %.1f |"%M["H_HOLD_observed_median_S_run"])
L.append("| Fraction du nuage X construite en `H_HOLD` pas | **%.4f %%** |"%(100*M["fraction_of_cloud_built_in_H_HOLD_steps"]))
L.append("| **`SHORTFALL_FACTOR`** | **%.4f** |"%M["MATURATION_TIME_VS_RESPONSE_FRACTION"][2]["shortfall_factor_vs_H_HOLD"])
L.append("| `P(episode S >= un e-folding)` sur %d episodes | %.6f |"%(M["n_S_episodes"],M["P_hold_ge_one_e_folding"]))
L.append("")
L.append("## 4. Audit du seuil historique « 101 naissances X acceptees »")
L.append("")
L.append("La valeur 101.14 est le `pre_removal_level` d'**un seul bras** (`R/seed9302`) du test de dependance causale a la source d'OBTC02. Les trois bras R donnent %s (moyenne %.5f). Ce n'etait pas un seuil derive et il n'est pas defendable comme tel."%(M["historical_101_binding"]["all_R_arm_pre_removal_levels"],M["historical_101_binding"]["mean"]))
L.append("")
L.append("`AUDIT = %s`"%M["historical_101_binding"]["AUDIT"])
L.append("")
L.append("## 5. Les six echelles de temps, distinguees")
L.append("")
for k,v in TS.items():
    L.append("### `%s`"%k); L.append(""); L.append(v["definition"]+".")
    L.append(""); L.append("`STATUS = %s`"%v["STATUS"]); L.append("")
L.append("## 6. Ce que ceci n'etablit pas")
L.append("")
for x in RES["WHAT_THIS_DOES_NOT_ESTABLISH"]: L.append("- `%s`"%x)
L.append("")
L.append("## 7. Ecarts par rapport a l'execution detruite")
L.append("")
for k,v in RES["DISCREPANCY_AGAINST_THE_DESTROYED_RUN"].items():
    L.append("- **%s** — enregistre : `%s` ; reconstruit : `%s`. %s"%(k,v["destroyed_run_recorded"],v["reconstructed"],v["resolution"]))
L.append("")
open(f"{OUT}/FTCTR01_FINAL_REPORT.md","w").write("\n".join(L)+"\n")
print("\n".join(L[:40]))
print("...")
print("WROTE", os.listdir(OUT))
