"""LDFMA01 — the corrections the adjudication forces, the re-scored Route A, the new arbitration
and the terminal disposition. Written after the checker return was hashed and externalised."""
from __future__ import annotations
import json,glob,math,statistics,hashlib,datetime
from math import comb
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
ADJ=json.load(open(f"{OUT}/LDFMA01_CHECKER_ADJUDICATION.json"))
R=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
R=[r for r in R if r.get("E_locked_daughter_interval")]
muY=0.000740894982503035
def mcn(n,p1,p0,a=0.05):
    b=p1*(1-p0); c=p0*(1-p1); tot=0.0
    for d in range(n+1):
        pd=comb(n,d)*((b+c)**d)*((1-b-c)**(n-d))
        if pd<1e-12: continue
        q=b/(b+c) if (b+c)>0 else .5
        for k in range(d+1):
            pk=comb(d,k)*(q**k)*((1-q)**(d-k))
            if sum(comb(d,i)*0.5**d for i in range(k,d+1))<=a: tot+=pd*pk
    return tot
def wilson(k,n,z=1.959963985):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
# ---- C-21: define the unit and evaluate the forked design ----
tms=[r["trigger_step"] for r in R]; med_tm=statistics.median(tms); T=11000
frac=med_tm/T
# Costing must be per SEED, not per paired block: the pre-trigger prefix has to be run for every
# seed because which seeds trigger is unknowable in advance. My first formula charged the prefix
# per block and made the fork look MORE expensive; the checker's per-seed accounting is correct.
BUD=512; YIELD=22/256
per_block_full=2.0                                   # two independent full-horizon runs per block
cost_independent_per_seed=2.0                        # both arms run the full horizon
cost_forked_per_seed=1.0+YIELD*(1-frac)              # one full run, plus a SHAM tail only where it triggers
pairs_full=int(round(BUD/cost_independent_per_seed*YIELD))
pairs_fork=int(round(BUD/cost_forked_per_seed*YIELD))
p1=5/22; lo,hi=wilson(5,22)
ENV=[{"p_selective":round(p,3),"power_at_%d_pairs"%pairs_full:round(mcn(pairs_full,p,0.0),3),
      "power_at_%d_pairs"%pairs_fork:round(mcn(pairs_fork,p,0.0),3)} for p in (lo,p1,hi)]
# ---- corrected probe counts ----
comp=sum(1 for r in R if r["E_locked_daughter_interval"]["ATTRIBUTION_WINDOW_PROBE"]["WOULD_BE_COMPLETE_UNDER_t_minus_1"])
func=ADJ["RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR"]["corrected_FUNCTIONAL_upper_bound"]
lamtab=ADJ["PER_WORLD_LAMBDA"]
corr={
 "MISSION":"LDFMA01","SECTION":"9 — corrections published after one adjudication","GENERATED_UTC":U,
 "CHECKER_RAW_SHA256":ADJ["CHECKER_RAW_RETURN"]["sha256"],
 "N_FINDINGS":28,"N_DISMISSED":0,"N_LOAD_BEARING_UPHELD":4,
 "CORRECTION_1_THE_ALIGNMENT_ARGUMENT_WAS_WRONG":{
   "finding":"C-03",
   "what_I_claimed":"persistence is NOT the binding constraint, because the daughters persist a "
     "median 230 steps and up to 1472 and still fail",
   "what_the_numbers_say":"the daughter's constituent-removal count is exposure-limited. With "
     "lambda_w = muY x daughter particle-steps, the exposure model predicts %.3f COMPLETE worlds "
     "among those that saw a birth, against 5 observed under the probe. lambda runs %.4f to %.4f, "
     "mean %.4f, so P(no removal) is about 0.68 per world by physics alone."%(
     ADJ["RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR"]["poisson_expected_COMPLETE_worlds"],
     ADJ["RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR"]["lambda_min"],
     ADJ["RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR"]["lambda_max"],
     ADJ["RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR"]["lambda_mean"]),
   "WITHDRAWN":"the claim that persistence is not binding, and with it the ground on which E3 was "
     "rejected and B3's condition 1 was downgraded",
   "PER_WORLD_LAMBDA":lamtab},
 "CORRECTION_2_THE_PROBE_IS_A_LOWER_BOUNDING_PROXY_AND_ITS_COUNTS_ARE_SPLIT":{
   "findings":["C-01","C-02","C-04","C-05","C-06","C-09"],
   "corrected_statement":"the frozen endpoint's step-t attribution is blind to most of the "
     "constituent removals the decay rate delivers. Re-attributing the identical ledger rows at "
     "step t-1 — a LOWER-BOUNDING PROXY for a pre-decay configuration the archive does not store — "
     "raises the count from 1 to 8 and recovers 7 previously unattributed. It raises the measured "
     "COMPLETE rate from 1/22 to %d/22 and the FUNCTIONAL rate to at most %d/22. Seventeen of the "
     "21 failures survive the repair, and they survive for a physical reason."%(comp,func),
   "units_are_not_commensurable":{"frozen_count":"cell-events","t_minus_1_count":"step-events",
     "expectation_8.435":"particles","OUTSTANDING_ITEM":"recount all three in particles by summing "
     "the ydeath n_died column; the 22 archives are not in this container after the fifth rollback"},
   "hop_out_false_negative_rate":"about 10 %, from p_hop_Y = 0.10263340389897246",
   "boundary_table":ADJ["BOUNDARY_TABLE"],
   "WITHDRAWN":"the bolded claim 'the physics already produces locked-daughter constituent "
     "turnover; the measurement does not see it', and the assertion that no verdict uses the probe",
   "EVERY_PROBE_DERIVED_STATEMENT_IS_NOW_LABELLED_PROBE_CONDITIONAL":True},
 "CORRECTION_3_ROUTE_B_RE_DERIVED_ON_THE_FROZEN_RECORD_ALONE":{
   "findings":["C-01","C-25"],
   "B1_occupancy_floored_removal":"still ineligible. On the frozen record alone, 0 of 22 daughters "
     "went extinct and all 22 identities ended by SPLIT_OR_TIE, so a floor on removal repairs a "
     "failure mode that was never observed. This argument uses no probe.",
   "B2_birth_throttling":"still ineligible: the ambient bloom arrives 706 to 2614 steps after the "
     "removal, and no single throttling rule is derivable without a sweep.",
   "B3_cohesion":"still ineligible on the launcher's own PARAMETER_SWEEP prohibition, which is "
     "independent and sufficient. The denominator argument is WITHDRAWN — identity lifetime is "
     "not a denominator of a per-block binary, and the same objection was scored PARTIAL for B1.",
   "ROUTE_B_CLASSIFICATION":"NO_MINIMAL_CHANGE_JUSTIFIED",
   "AND_IT_NO_LONGER_DEPENDS_ON_THE_PROBE":True},
 "CORRECTION_4_THE_BUDGET_UNIT_AND_THE_FORKED_DESIGN":{
   "finding":"C-21",
   "PRIMARY_ARM_INSTANCE_DEFINED":"one full-horizon world-equivalent of engine work, T = 11000 steps",
   "why_a_fork_is_admissible":"SELECTIVE and SHAM are bit-identical up to t_m: the SHAM path is a "
     "proved bit-exact no-op and the intervention leaves the generator hash unchanged in 22 of 22 "
     "worlds. The pre-trigger prefix can be paid once.",
   "median_t_m":med_tm,"shared_prefix_fraction":round(frac,4),
   "cost_per_seed_independent_runs":cost_independent_per_seed,
   "cost_per_seed_forked":round(cost_forked_per_seed,4),
   "MY_FIRST_COST_FORMULA_WAS_WRONG":"it charged the shared prefix per PAIRED BLOCK and so made the fork look more expensive. The prefix must be paid for every seed, because which seeds trigger is unknowable in advance. The checker's per-seed accounting is correct and is used here.",
   "paired_blocks_at_512_independent":pairs_full,
   "paired_blocks_at_512_forked":pairs_fork,
   "WITHDRAWN":"the unqualified statement that 512 arm instances buy only 22 paired blocks"},
 "CORRECTION_5_POWER_IS_STATED_WITH_ITS_UNCERTAINTY":{
   "findings":["C-22","C-23"],
   "p1_point_estimate":round(p1,4),"wilson_95_CI":[round(lo,4),round(hi,4)],
   "power_envelope_against_p_sham_0":ENV,
   "paired_SD_relabelled":"the 0.997 figure is the MARGINAL log-SD of the 22 SELECTIVE lifetimes. "
     "The paired SELECTIVE-minus-SHAM SD is unmeasured because no SHAM arm has ever been executed; "
     "the shared prefix makes the true paired SD smaller, so E3 is if anything better powered."},
 "CORRECTION_6_THE_AUTOPSY_PROSE_IS_REWRITTEN":{
   "findings":["C-15","C-16","C-17","C-18","C-19","C-20"],
   "what_was_wrong":"the markdown named parent-daughter distance and ambient pressure as falsified "
     "when the JSON shows the success at rank 2 of 22 and OUTSIDE the failure interquartile span "
     "on the distance; it said 30 comparable features when there are 39; and the inclusive "
     "interquartile test inverted three of seven falsifications on tied discrete features.",
   "corrected_falsification_count":"at most 4, with rank reported beside each",
   "features_on_which_the_success_is_at_rank_<=3_and_outside_the_failure_IQR":
     ["parent_daughter_centroid_distance","mean_world_nY_after_t_m",
      "ambient_complete_interval_count","ambient_functional_interval_count"],
   "the_mechanism_mapping_is_declared_POST_HOC":True,
   "null_expectation_for_UNIQUE_features":"2/22 x 39 = 3.5 against 4 observed — the uniqueness "
     "scan carries no evidence of a separating feature, which strengthens rather than weakens the "
     "conclusion that no prospective eligibility criterion exists.",
   "WITHDRAWN":"the sentence 'Everything else about it is ordinary'"},
 "CORRECTION_7_THE_AMBIENT_MODEL_IS_DEMOTED":{
   "findings":["C-10","C-11"],
   "WITHDRAWN":"the repeated-opportunity expression as a TEST — with n >= 694 it cannot fail",
   "what_the_conclusion_now_rests_on":["the model-free observation that every world contains 65 to "
     "117 COMPLETE intervals","the timing fact, corrected below"],
   "corrected_timing_fact":"ZERO complete intervals other than the locked daughter's own start "
     "inside any daughter's window. The single exception in the earlier '2017 of 2018' was the "
     "daughter itself, whose interval begins at t_m - 249.",
   "ambient_count_excluding_the_daughter":2017},
 "CORRECTION_8_THE_INDEPENDENCE_CLAIM_IS_NARROWED":{
   "findings":["C-26","C-12","C-14"],
   "declared_online_input":"s[:,7], the online component count, is read for the disagreement "
     "counter. It enters no verdict, and the counter compares component COUNTS, not partitions.",
   "deliberately_different_implementation_applies_to":"the component finder only. centroid and "
     "link are near-transcriptions and MUST be, or the k_xd physical match cannot bind.",
   "codes_unreachable_BY_CONSTRUCTION":["L5"],
   "codes_merely_unobserved":["L0","L1","L4","L6","L7","L9","L10","L11","L12"],
   "dominant_stage_counter_now_excludes_SUCCESS":True},
 "CORRECTION_9_PROVENANCE":{"finding":"C-27",
   "action":"an input/output manifest is written and the mission is committed."},
 "CORRECTION_10_THE_VOCABULARY_GAP_NOTE_IS_DELETED":{"finding":"C-28",
   "why":"once C-03 is granted a route IS eligible, so the terminal no longer needs a gap note.",
   "the_instrumentation_repair_is_moved":"from prose in an artefact into the authorised handoff, "
     "as a PRECONDITION."},
 "CORRECTIONS_ARE_PUBLISHED_NOT_QUIETLY_APPLIED":True}
json.dump(corr,open(f"{OUT}/LDFMA01_CHECKER_CORRECTIONS.json","w"),indent=1)

# ---------------- re-scored Route A and the new arbitration ----------------
E3={"id":"E3","name":"locked-daughter post-removal exposure, SELECTIVE vs SHAM, paired",
 "primary":"the daughter's post-removal identity lifetime (persistence)",
 "co_primary_pre_declared":"the daughter's post-removal particle-step exposure, sum over the "
   "interval of component nY — the quantity the verified Poisson map converts into completion "
   "probability with no free parameter",
 "causal_estimand":"paired within-block difference, SELECTIVE minus SHAM, on the same seed",
 "independent_unit":"the base block","time_origin":"t_m, identical in both arms by construction",
 "censoring":"administrative at the horizon; 0 of 22 retrospective worlds reached it",
 "competing_events":"third centre, merge, extinction — none observed as a terminator in 22 of 22",
 "decision_rule":"Wilcoxon signed-rank on the paired log difference, two-sided, alpha 0.05",
 "claim_ceiling":"a causal effect of parent removal on the locked daughter's post-removal "
   "exposure. NOT reproduction, NOT heredity, NOT a turnover measurement.",
 "CONDITIONS":{
  "1 relevant to daughter independence":{"verdict":"PASS","why":"C-03: exposure = occupancy x "
    "identity lifetime is the binding constraint on the daughter's constituent turnover, verified "
    "at 5.809 predicted against 5 observed. My earlier PARTIAL rested on a claim now withdrawn."},
  "2 does not substitute ambient for daughter":{"verdict":"PASS"},
  "3 non-arbitrary decision rule":{"verdict":"PASS","why":"a paired difference needs no threshold "
    "beyond zero"},
  "4 reconstructable offline":{"verdict":"PASS","why":"reconstructed here by a third implementation"},
  "5 decision-capable within 512 primary arm instances":{"verdict":"PASS","why":"%d paired blocks "
    "with independent runs, %d with the admissible fork at t_m; the endpoint is continuous and "
    "paired, and the shared prefix makes the paired SD smaller than the marginal 0.997"%(
    pairs_full,pairs_fork)},
  "6 no outcome-chosen threshold":{"verdict":"PASS","why":"no threshold is taken from any outcome; "
    "the endpoint needs no attribution repair and no probe"},
  "7 a positive result materially advances the reproduction question":{"verdict":"PASS_WITH_A_"
    "STATED_CEILING","why":"the exposure-to-completion map is verified with no free parameter, so "
    "a measured causal change in exposure is a measured causal change in the daughter's "
    "probability of completing a constituent turnover. The ceiling is that this is an effect on "
    "exposure, not a reproduction result, and the handoff must say so."}},
 "ELIGIBLE":True,"CLASSIFICATION":"MATCHED_CONTROL_TEST_ELIGIBLE",
 "WHY_NOT_E1_CORRECTED":"selecting the turnover binary would require adopting an attribution "
   "repair identified after the outcomes — post-outcome endpoint selection, which the launcher "
   "forbids and which the checker independently warned against. The repair belongs in the handoff "
   "as a PRECONDITION to be frozen and justified before world 1, not as the selected endpoint.",
 "WHY_NOT_E5":"unchanged: it substitutes ambient-population turnover for locked-daughter turnover, "
   "and zero non-daughter complete intervals start inside any daughter's window."}
arb2={"MISSION":"LDFMA01","SECTION":"8 — route arbitration, RE-DERIVED after adjudication",
 "GENERATED_UTC":U,"SUPERSEDES":"the pre-checker arbitration in LDFMA01_ROUTE_ARBITRATION.json",
 "WHAT_CHANGED_AND_WHY":"C-03 was upheld. The pause had rested on rejecting E3 for measuring a "
   "variable that is not binding. That claim was wrong and was mine; exposure IS binding. With it "
   "withdrawn, E3 satisfies all seven conditions and arbitration rule 1 applies.",
 "STEP_1_ROUTE_A":{"classification":"MATCHED_CONTROL_TEST_ELIGIBLE","selected_endpoint":"E3"},
 "STEP_2_ROUTE_B":{"classification":"NO_MINIMAL_CHANGE_JUSTIFIED",
   "now_independent_of_the_probe":True},
 "SELECTED_ROUTE":"ROUTE_A__ONE_MATCHED_CONTROL_TEST","MAX_SELECTED_ROUTES":1,"N_SELECTED":1,
 "THE_CHECKER_RECOMMENDED_THE_SAME_ROUTE":True,
 "NOT_CHOSEN_FOR_POWER":"E5 remains rejected although it has more power than E3.",
 "E3":E3}
json.dump(arb2,open(f"{OUT}/LDFMA01_ROUTE_ARBITRATION_FINAL.json","w"),indent=1)
disp={"MISSION":"LDFMA01","SECTION":"10 — terminal disposition","GENERATED_UTC":U,
 "FINAL_DISPOSITION":"LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__ONE_MATCHED_CONTROL_TEST_ELIGIBLE",
 "ALLOWED_TERMINALS":[
  "LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__ONE_MATCHED_CONTROL_TEST_ELIGIBLE",
  "LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__ONE_MINIMAL_ARCHITECTURE_TEST_ELIGIBLE",
  "LOCKED_DAUGHTER_FAILURE_NOT_IDENTIFIABLE__LINEAGE_ROUTE_PAUSED",
  "FIMRCC01_RECORD_NOT_INTERPRETABLE__LOAD_BEARING_RECONSTRUCTION_DEFECT"],
 "DISPOSITION_IS_ONE_OF_THE_FOUR":True,
 "IT_CHANGED_AFTER_THE_CHECKER":{"before":"LOCKED_DAUGHTER_FAILURE_NOT_IDENTIFIABLE__LINEAGE_ROUTE_PAUSED",
   "after":"LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__ONE_MATCHED_CONTROL_TEST_ELIGIBLE",
   "cause":"C-03, upheld and independently recomputed","the_checker_recommended_this":True},
 "THE_IDENTIFIED_MECHANISM":{
   "part_1_exposure":"after the removal the locked daughter is a 1-to-6 particle object holding the "
     "world's entire Y population (parent_nY + daughter_nY = world_nY in 22 of 22). Its identity "
     "window is closed by a split with exactly two successor candidates within CORE_R in 22 of 22, "
     "at a median of 230 steps. The resulting 11,385 particle-steps predict 8.44 constituent "
     "removals, and the exposure model reproduces the observed completion count to 5.809 against 5.",
   "part_2_attribution":"the frozen endpoint attributes a ledger event to the component whose cell "
     "set contains it AT STEP t, while the archive writes cell rows after the step, so a decay that "
     "empties a cell is invisible. This is a measurement defect, quantified but NOT repaired here.",
   "which_is_load_bearing":"both. Part 1 sets how many removals occur; part 2 sets how many are "
     "counted. Neither alone explains 1 of 22."},
 "SELECTED_ROUTE":"ROUTE_A__ONE_MATCHED_CONTROL_TEST","SELECTED_PRIMARY_ENDPOINT":"E3",
 "SELECTED_MAXIMUM_RUN_BUDGET":"512 primary arm instances, one instance = one full-horizon "
   "world-equivalent of engine work",
 "NEW_SCIENTIFIC_ENGINE_RUNS_IN_LDFMA01":0,"NEW_SEEDS":0,"NEW_TRAJECTORIES":0,
 "ROUTE_CANDIDATES_EVALUATED":3,"ROUTES_SELECTED":1,
 "INDEPENDENT_CHECKERS_USED":1,"REVIEW_CASCADES":0,
 "HANDOFF_EMITTED":"HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md",
 "HANDOFF_IS_CREATED_NOT_EXECUTED":True,
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED","FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED",
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "NEXT_SCIENTIFIC_ELIGIBILITY":"ONE_MATCHED_CONTROL_TEST__AWAITING_TOMMYS_AUTHORISATION"}
json.dump(disp,open(f"{OUT}/LDFMA01_FINAL_DISPOSITION.json","w"),indent=1)
print("paired blocks: independent %d | forked %d"%(pairs_full,pairs_fork))
print("Wilson CI on 5/22: [%.3f, %.3f]"%(lo,hi))
for e in ENV: print("  ",e)
print("SELECTED_ROUTE:",arb2["SELECTED_ROUTE"])
print("FINAL_DISPOSITION:",disp["FINAL_DISPOSITION"])
