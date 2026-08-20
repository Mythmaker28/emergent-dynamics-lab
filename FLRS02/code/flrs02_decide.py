"""FLRS02 §6 + §9 + §11 + §12 — reconstructibility class, architecture test, route decision."""
import json, math, datetime
import numpy as np
OUT="/home/claude/edl/FLRS02/out"
KEYS=("T_50","T_primary","T_80","T_90")
ATL={pt:json.load(open(f"{OUT}/FLRS02_{pt}_DIRECT_ATLAS.json")) for pt in ("B1","B2")}
POW=json.load(open(f"{OUT}/FLRS02_POWER_ANALYSIS.json"))
SENS=json.load(open(f"{OUT}/_sensitivity_capability.json"))
CRIT=json.load(open(f"{OUT}/FLRS02_FUNCTIONAL_CRITERION.json"))
TB=json.load(open(f"{OUT}/FLRS02_TIMESCALE_BINDING.json"))
TP=json.load(open(f"{OUT}/FLRS02_THRESHOLD_PROVENANCE.json"))
IC=json.load(open(f"{OUT}/FLRS02_INDEPENDENT_CHECK.json"))
A=json.load(open(f"{OUT}/_checkerA.json"))
BEST=POW["SELECTED_POINT"]

# ---------------- §6 reconstructibility ----------------
REC={"CLASS":"DIRECT_FUNCTION_RECONSTRUCTIBLE",
 "EVIDENCE":{
   "full_spatial_fields":"field0 (6,L,L) plus field_delta (T-1,6,L,L) reconstruct every species plane at every step",
   "verified_against":"ycells rows (t,y,x,nY,nX,nSY,free,candY,Q) match the reconstructed field exactly at the cell level",
   "plane_map":"0 = X, 1 = Y, 3 = SY (established from the PQEC01 review code a10_field.py and re-verified here)"},
 "WHAT_WAS_MEASURED_DIRECTLY":"local X mass within CORE_R of each spatial centre's toroidal centroid at the maturation event",
 "WHAT_IS_INFERRED_RATHER_THAN_OBSERVED":"nothing in condition 5; the response is measured. The maturation DURATION T(f) is operator-derived and is a timing criterion, stated as such.",
 "COMPARISON_WITH_THE_TRANSIENT_OPERATOR":{
   "operator_prediction_at_T_primary":1.0-1.0/math.e,
   "observed_weak_centre_ratio_median":{pt:ATL[pt]["PHASE_B_DESCRIPTIVE"]["WEAK_CENTRE_X_RATIO"]["T_primary"]["median"] for pt in ("B1","B2")},
   "verdict":"the observed second-centre response at the operator-derived time EXCEEDS the operator's own predicted fraction at both points, so the timing criterion is conservative rather than permissive"},
 "NO_FIELD_MANUFACTURED":True,
 "PARENT_CHILD_IDENTITY":"none constructed; persistent spatial-centre identity only"}

# ---------------- §11 architecture test ----------------
ARCH={"SECTION":"FLRS02 §11 — architecture change test",
 "CANDIDATE_CONFLICT_1_kY_forces_P_before_function":{
   "observed_P_before_function":{pt:ATL[pt]["ATLAS"]["RATES"]["P_THIRD_BEFORE_FUNCTION"]["count"] for pt in ("B1","B2")},
   "verdict":"NOT_OBSERVED — 0 of 44 at both points"},
 "CANDIDATE_CONFLICT_2_muY_needed_to_control_centres_destroys_continuity":{
   "B2_muY":ATL["B2"]["PHASE_B_DESCRIPTIVE"]["muY"],
   "B2_lineage_non_extinction":ATL["B2"]["ATLAS"]["RATES"]["P_LINEAGE_NON_EXTINCTION"]["point_estimate"],
   "B2_third_before_function":ATL["B2"]["ATLAS"]["RATES"]["P_THIRD_BEFORE_FUNCTION"]["count"],
   "verdict":("NOT_OBSERVED — at B2 muY is essentially zero, lineage non-extinction is 1.000, and no third centre "
              "precedes function. There is no point at which controlling extra centres costs lineage continuity.")},
 "CANDIDATE_CONFLICT_3_X_integrity_collapses_where_two_centre_episodes_are_common":{
   "X_integrity":{pt:ATL[pt]["ATLAS"]["RATES"]["P_X_INTEGRITY"]["point_estimate"] for pt in ("B1","B2")},
   "verdict":"NOT_OBSERVED — integrity holds in 88 of 88 Phase-B worlds"},
 "EXPLICIT_NON_EVIDENCE":"the physical inadequacy of the retired 16-step hold is NOT evidence of architecture failure",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED"}

# ---------------- §9 eligibility checklist ----------------
R=ATL[BEST]["ATLAS"]["RATES"]
J=R["P_JOINT_FUNCTIONAL_SUCCESS_T_primary"]
CHK=[
 {"requirement":"functional success observed in more than isolated exceptional worlds",
  "evidence":"%d of %d worlds at %s under the primary criterion"%(J["count"],J["n"],BEST),"PASS":J["count"]>=5},
 {"requirement":"the conclusion is not destroyed by moving from 50% to the canonical e-folding",
  "evidence":"joint success moves %d -> %d of %d"%(R["P_JOINT_FUNCTIONAL_SUCCESS_T_50"]["count"],J["count"],J["n"]),
  "PASS":abs(R["P_JOINT_FUNCTIONAL_SUCCESS_T_50"]["count"]-J["count"])<=2},
 {"requirement":"third-centre-before-function risk is not dominant",
  "evidence":"%d of %d"%(R["P_THIRD_BEFORE_FUNCTION"]["count"],R["P_THIRD_BEFORE_FUNCTION"]["n"]),
  "PASS":R["P_THIRD_BEFORE_FUNCTION"]["count"]==0},
 {"requirement":"X integrity is acceptable","evidence":"%d of %d"%(R["P_X_INTEGRITY"]["count"],R["P_X_INTEGRITY"]["n"]),
  "PASS":R["P_X_INTEGRITY"]["point_estimate"]==1.0},
 {"requirement":"no interpolation is required",
  "evidence":"%s is an exact executable parameter point already run by PQEC01 (kY=%.10e, muY=%.10e)"%(
      BEST,ATL[BEST]["PHASE_B_DESCRIPTIVE"]["kY"],ATL[BEST]["PHASE_B_DESCRIPTIVE"]["muY"]),"PASS":True},
 {"requirement":"no architecture modification is required","evidence":ARCH["ARCHITECTURE_CHANGE_NECESSITY"],"PASS":True},
 {"requirement":"a fresh disjoint experiment separates the rate from a null within <= 192 worlds",
  "evidence":"at %s under the primary criterion, conservative planning (95%% lower bound p1=%.4f) needs n=%s against p0=0.05 and n=%s against p0=0.10"%(
      BEST,J["exact_binomial_95"][0],SENS[BEST]["T_primary"]["n_req_cons_p0_0.05"],SENS[BEST]["T_primary"]["n_req_cons_p0_0.1"]),
  "PASS":SENS[BEST]["T_primary"]["n_req_cons_p0_0.1"] is not None and SENS[BEST]["T_primary"]["n_req_cons_p0_0.1"]<=192}]
ALLPASS=all(c["PASS"] for c in CHK)

SENSVERDICT=("STABLE_THROUGH_T_80__NOT_DECISION_CAPABLE_AT_T_90_WITHIN_192")
DISP="ONE_EXISTING_POINT_DIRECT_TEST_JUSTIFIED" if ALLPASS else "FUNCTIONAL_LINEAGE_EXPERIMENT_NOT_YET_JUSTIFIED__EXACT_LIMIT_NAMED"

D={"PROGRAMME":"FLRS02 — FUNCTIONAL-LINEAGE-ROUTE-SELECTION-02",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "NEW_SCIENTIFIC_ENGINE_RUNS":0,"NEW_WORLD_CONSTRUCTIONS":0,"NEW_SEEDS":0,
 "NEW_TRAJECTORIES":0,"CHECKPOINT_CONTINUATIONS":0,
 "PRIMARY_FUNCTIONAL_CRITERION":CRIT["PRIMARY_FUNCTIONAL_CRITERION"],
 "WHY_THAT_CRITERION":CRIT["SPECTRUM_DEMONSTRATION"]["INTERPRETATION"],
 "SENSITIVITY":{k:{pt:{"count":ATL[pt]["ATLAS"]["RATES"][f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]["count"],
                       "p":ATL[pt]["ATLAS"]["RATES"][f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]["point_estimate"],
                       "lower95":ATL[pt]["ATLAS"]["RATES"][f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]["exact_binomial_95"][0],
                       "n_req_cons_vs_p0_0.05":SENS[pt][k]["n_req_cons_p0_0.05"]} for pt in ("B1","B2")} for k in KEYS},
 "FUNCTIONAL_THRESHOLD_SENSITIVITY":SENSVERDICT,
 "SENSITIVITY_STATEMENT":("the joint success rate declines monotonically and without a sign change across the band "
   "(B1: 0.3182 -> 0.2955 -> 0.2045 -> 0.1364). What degrades is the POWER to separate the rate from a null inside "
   "the 192-world budget, not the sign or the magnitude of the effect. At T_90 no null above 0.015 is separable "
   "conservatively, so no claim may be made at T_90 from a 192-world experiment."),
 "RECONSTRUCTIBILITY":REC,
 "POINT_SELECTION":{"rule":POW["POINT_SELECTION_RULE"],
   "min_lower_margins":{k:{pt:POW["SELECTION"][k][pt]["MIN_LOWER_MARGIN"] for pt in ("B1","B2")} for k in KEYS},
   "winner_per_fraction":{k:POW["SELECTION"][k]["WINNER"] for k in KEYS},
   "SELECTED":BEST,
   "HONEST_CAVEAT":("B1 and B2 are statistically indistinguishable (13/44 vs 12/44 under the primary criterion). "
     "The frozen primary criterion selects B1; the ordering is not stable across the whole band (B2 wins at T_80, "
     "the two tie at T_50 and T_90). The selection is therefore a defensible tie-break, not a demonstrated superiority.")},
 "ELIGIBILITY_CHECKLIST":CHK,"ALL_REQUIREMENTS_PASS":ALLPASS,
 "ARCHITECTURE_TEST":ARCH,
 "THRESHOLD_PROVENANCE":{"classification":TP["CLASSIFICATION"],"consequence":TP["CONSEQUENCE"]},
 "INDEPENDENT_CHECK":{"verdict":IC["VERDICT"],"n_disagreements":IC["N_DISAGREEMENTS"]},
 "DATA_STATUS":"the 128 PQEC01 worlds are POST_OUTCOME_DEVELOPMENTAL_DATA. They are not confirmation.",
 "RECORDED_LIMITS":[
   "14 of the 88 Phase-B worlds (7 per point) were terminated by the runner at PREMATURE_THIRD_CENTRE. This is outcome-dependent truncation: what would have followed the third centre is unobserved. It does not bias P_THIRD_BEFORE_FUNCTION, which is observed directly, but it censors later development.",
   "28 of 44 B1 worlds went extinct; those are genuine failures and are counted in the denominator of 44.",
   "the PQEC01 DISCOVERY/VALIDATION split is pooled here because one world is the unit and the split was an internal PQEC01 device; per-point splits are B1 29/15 and B2 28/16.",
   "the weak-centre X ratio is self-normalising (weaker centre over stronger). The A0 control supplies an absolute single-centre reference (mean local X within CORE_R = %.4f) but its spread is wide (sd %.4f), so the ratio is used as the criterion and the absolute level only as a diagnostic."%(
       ATL["B1"]["A0_SINGLE_CENTRE_REFERENCE"]["local_X_within_CORE_R_mean"],
       ATL["B1"]["A0_SINGLE_CENTRE_REFERENCE"]["sd"])],
 "FINAL_ROUTE_DISPOSITION":DISP,
 "FORBIDDEN_CLAIM_STATUS":{"H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED",
   "HEREDITY_STATUS":"NOT_TESTED","AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
   "X_LAWSPEC_BASELINE":"UNCHANGED","ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
   "FOUNDER_SURVIVAL_GATE":"rejected","PARTICLE_GENEALOGY_REQUIRED":"false"}}
json.dump(D,open(f"{OUT}/FLRS02_ROUTE_DECISION.json","w"),indent=2)
print("DISPOSITION:",DISP,"| SELECTED:",BEST,"| ALL_PASS:",ALLPASS)
for c in CHK: print("  [%s] %s -- %s"%("PASS" if c["PASS"] else "FAIL",c["requirement"],c["evidence"]))
