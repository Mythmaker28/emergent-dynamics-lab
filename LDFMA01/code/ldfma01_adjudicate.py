"""LDFMA01 section 9 — the single adjudication of the checker's 28 findings, and the corrections
they force. The raw return was written and hashed before this file was written. No second checker,
no cascade: every finding is adjudicated exactly once."""
from __future__ import annotations
import json,glob,math,statistics,hashlib,datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
RAW=f"{REPO}/LDFMA01/review/LDFMA01_CHECKER_RAW.txt"
R=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
R=[r for r in R if r.get("E_locked_daughter_interval")]
muY=0.000740894982503035

# ---- recomputations the adjudication needs ----
lam=[(r["tag"],muY*r["E_locked_daughter_interval"]["daughter_particle_steps_after_t_m"],
      r["E_locked_daughter_interval"]["n_Y_births_after_t_m"]>0) for r in R]
poisson=sum((1-math.exp(-l)) for _,l,b in lam if b)
obs_complete=sum(1 for r in R if r["E_locked_daughter_interval"]["ATTRIBUTION_WINDOW_PROBE"]["WOULD_BE_COMPLETE_UNDER_t_minus_1"])
boundary=[]
for r in R:
    e=r["E_locked_daughter_interval"]; p=e["ATTRIBUTION_WINDOW_PROBE"]
    fd=p["first_removal_at_t_minus_1"]
    if fd is None: continue
    boundary.append({"tag":r["tag"],"first_removal_t_minus_1":fd,"interval_end":e["interval_end"],
      "end_minus_fd":e["interval_end"]-fd,"outside_the_identity":fd>e["interval_end"],
      "counted_as_COMPLETE":p["WOULD_BE_COMPLETE_UNDER_t_minus_1"],
      "would_pass_the_FUNCTIONAL_persistence_guard":(e["interval_end"]-fd)>0})
corr_complete=obs_complete
corr_func_upper=sum(1 for b in boundary if b["counted_as_COMPLETE"] and b["would_pass_the_FUNCTIONAL_persistence_guard"])
comp_ge2=sum(int(k)*v for r in R for k,v in r["E_locked_daughter_interval"]["daughter_nY_histogram_after_t_m"].items() if int(k)>=2)
ptot=sum(int(k)*v for r in R for k,v in r["E_locked_daughter_interval"]["daughter_nY_histogram_after_t_m"].items())
def F(cid,title,verdict,why,action):
    return {"id":cid,"title":title,"VERDICT":verdict,"adjudication":why,"action_taken":action}
A=[
F("C-01","the t-1 probe is used as a verdict","UPHELD",
  "correct and important. The Route B classification did rest on the probe while the partition "
  "asserted no verdict uses it. The two cannot both stand.",
  "the assertion is withdrawn. Route B is re-derived below on the FROZEN record alone, and every "
  "probe-derived statement is relabelled probe-conditional."),
F("C-02","'the physics already produces turnover, the measurement does not see it' overstates","UPHELD",
  "correct. Under the probe the endpoint moves from 1/22 to 5/22 COMPLETE, so 17 of 21 failures "
  "survive the repair. The claim is true of the EVENT COUNT and false of the WORLD-LEVEL failure.",
  "the sentence is replaced by the checker's own formulation, and the bolded physical claim is "
  "removed from LDFMA01_MINIMAL_ARCHITECTURE_CANDIDATES."),
F("C-03","the corrected rate is exactly the exposure-limited Poisson expectation","UPHELD__LOAD_BEARING",
  "verified independently: sum over worlds of 1(birth)*(1-exp(-lambda_w)) = %.3f against the "
  "checker's 5.81 and against 5 observed. lambda ranges %.4f to %.4f, mean %.4f. The alignment "
  "argument used to reject E3 — that persistence is not the binding constraint — is WRONG, and it "
  "was mine. Exposure = occupancy x identity lifetime is the binding constraint at both the "
  "frozen and the corrected endpoint."%(poisson,min(l for _,l,_ in lam),max(l for _,l,_ in lam),
  statistics.mean([l for _,l,_ in lam])),
  "the argument is withdrawn. E3 is re-scored, Route A is re-classified and the terminal "
  "disposition changes. The per-world lambda table is published."),
F("C-04","the probe mixes cell-events, step-events and particles","UPHELD_AS_A_UNIT_DEFECT",
  "correct that three units are set side by side. The archives are no longer in this container "
  "after the fifth rollback, so n_died cannot be re-summed here without re-staging 22 files.",
  "the three quantities are relabelled with their units and the recount is recorded as an "
  "OUTSTANDING_ITEM rather than claimed."),
F("C-05","the t-1 window overhangs the identity by one step","PARTIALLY_UPHELD",
  "the overhang is real and the FUNCTIONAL guard is genuinely missing from the probe: i119 has "
  "first_removal = interval_end, so end-fd = 0 and the frozen FUNCTIONAL guard would reject it. "
  "Corrected COMPLETE = %d/22; corrected FUNCTIONAL is at most %d/22. The checker is WRONG on one "
  "detail: i153 does overhang (715 against interval_end 714) but was already NOT counted as "
  "COMPLETE, so it is not one of the five."%(corr_complete,corr_func_upper),
  "both corrected counts are published with the boundary table, and 5/22 is never used again "
  "without its FUNCTIONAL companion."),
F("C-06","t-1 is a proxy for an unarchivable configuration","UPHELD",
  "correct. The decay acts after that step's diffusion, p_hop_Y = 0.1026, and the pre-decay field "
  "is not in TLMR01-ARCHIVE-1. The birth count falling from 33 to 30 is the evidence.",
  "the probe is relabelled a LOWER-BOUNDING PROXY throughout, and the hop-out false-negative rate "
  "is stated."),
F("C-07","the multiply-occupied-cell test is absent","UPHELD_IN_PRINCIPLE__NOT_REPRODUCIBLE_HERE",
  "the test is the right one. The checker computed it at CELL level on the one surviving archive "
  "(13.6 %%, predicting 1.15 against 1 observed). LDFMA01 recorded only COMPONENT occupancy, which "
  "gives %.1f %% and predicts %.2f — a different quantity, and NOT a substitute. The cell-level "
  "figure stands for one world only."%(100*comp_ge2/ptot,muY*comp_ge2),
  "the checker's one-world cell-level number is recorded as his, with the component-level figure "
  "shown beside it and explicitly NOT offered as the same test."),
F("C-08","three of eight recovered removals come from the one world where the daughter is not alone",
  "UPHELD","correct and worth stating: parent_nY + daughter_nY = world_nY in 22 of 22, so after "
  "the removal the daughter is the entire Y population and attribution is near-trivial except in "
  "i045.","recorded; the per-event table is an OUTSTANDING_ITEM for the same rollback reason."),
F("C-09","'recovers 8' should be 'recovers 7'","UPHELD","arithmetic; one of the eight was already "
  "attributed by the frozen rule.","corrected in all three artefacts."),
F("C-10","the repeated-opportunity model is circular","UPHELD",
  "correct. With n >= 694 the prediction exceeds 0.99 for any p_bar >= 0.0066, and the same file "
  "denies the independence the exponent assumes.",
  "the model is demoted to an ILLUSTRATION. Section 5's conclusion now rests on the model-free "
  "observation that every world contains 65 to 117 complete intervals and on the timing fact."),
F("C-11","'2017 of 2018' understates; the exception is the daughter itself","UPHELD",
  "correct, and the corrected statement is stronger: ZERO non-daughter complete intervals start "
  "inside any daughter's window.","corrected, with the daughter excluded from the ambient count."),
F("C-12","the exclusivity check is vacuous and L5 is unreachable","UPHELD",
  "correct on both. sum(counts)==22 is true by construction, and minNY>=1 always holds because "
  "cell rows exist only for occupied cells.",
  "the vacuous flag is replaced by an explicit statement of which codes are unreachable BY "
  "CONSTRUCTION (L5) and which are merely unobserved (L0, L1, L4, L6, L7, L9, L10, L11, L12)."),
F("C-13","demoting SPLIT_OR_TIE to secondary hides the causal ordering","UPHELD__LOAD_BEARING",
  "correct once C-03 is granted. If the endpoint is exposure-limited, the split that closes the "
  "window is upstream of 'birth without removal'. My defence was about informativeness, not "
  "causality.","both orderings are now published side by side, and the split is named as the "
  "upstream mechanism."),
F("C-14","DOMINANT_FAILURE_STAGE counted over a counter including SUCCESS","UPHELD",
  "a real defect, harmless at 16 against 1.","corrected to exclude SUCCESS from both."),
F("C-15","'30' against 39 comparable features","UPHELD","transcription error in my prose.","corrected to 39."),
F("C-16","the autopsy prose contradicts its own JSON","UPHELD__LOAD_BEARING",
  "correct and the worst of my errors: I wrote that parent-daughter distance and ambient pressure "
  "were falsified when the JSON says the success is at rank 2 and outside the failure IQR on the "
  "distance. 'Everything else about it is ordinary' is not supported.",
  "the prose is rewritten to transcribe the JSON, and the four features on which the success sits "
  "at rank <= 3 and outside the failure IQR are named."),
F("C-17","three of seven falsifications are inverted by an inclusive IQR test","UPHELD",
  "correct. On tied discrete features Q1 equals the minimum, so joint-extremal values were "
  "declared 'inside the IQR'.","the test now excludes values at the failure min or max; the "
  "falsified count drops from 7 to at most 4 and rank is reported beside every one."),
F("C-18","the mechanism mapping was fixed after the outcomes","UPHELD",
  "correct. The pre-registration fixed the feature set at 18:25; the MECH dictionary deciding "
  "which features are mechanistically interpretable was written at 18:42, and it contains one "
  "entry outside the pre-registered families.",
  "the mapping is declared POST-HOC in the autopsy, and the falsification is reported both with "
  "and without the out-of-family entry."),
F("C-19","the unique before-outcome feature is a folded-statistic boundary artefact","UPHELD",
  "correct: f5 is capped at 1.0 and its unfolded twin ranks 13 of 22.",
  "the JSON now flags capped statistics and reports both."),
F("C-20","the null expectation for uniqueness is 3.5 and four were observed","UPHELD",
  "correct, and it strengthens the mission's own conclusion rather than weakening it.",
  "the 3.5 null is stated beside the 4."),
F("C-21","the budget arithmetic is unexamined; a forked design buys about twice the pairs",
  "UPHELD__LOAD_BEARING",
  "correct that 'primary arm instance' was never defined and that a fork at t_m is admissible: "
  "the SHAM path is a proved bit-exact no-op and the intervention leaves the generator hash "
  "unchanged in 22 of 22, so the pre-trigger prefix is shared and need be paid once.",
  "'primary arm instance' is defined as one full-horizon world-equivalent of engine work; the "
  "forked design is evaluated and carried into the handoff."),
F("C-22","the not-decision-capable verdict is conditioned on an n=22 point estimate","UPHELD",
  "correct. Wilson 95 %% on 5/22 is [0.101, 0.434] and power at 22 pairs spans 0.065 to 0.988.",
  "a power envelope over the interval is published and the classification is stated as conditional."),
F("C-23","'paired log-SD' is a marginal SD","UPHELD","correct; no SHAM arm has ever been executed, "
  "so the paired SD is unmeasured.","relabelled, with the direction of the bias stated."),
F("C-24","'the arms already exist' is not true","UPHELD","correct; a proved-inert code path is not "
  "an executed arm.","corrected to the checker's wording."),
F("C-25","B3 is dismissed on a wrong reason and an inconsistent standard","UPHELD",
  "correct. Identity lifetime is not a denominator of a per-block binary, and the same objection "
  "was scored PARTIAL for B1 and FAIL for B3.",
  "the denominator argument is withdrawn. B3 still fails on the launcher's own PARAMETER_SWEEP "
  "prohibition, which is independent and sufficient."),
F("C-26","two overstatements in the independence claim","UPHELD",
  "correct on both. s[:,7] is an undeclared online input used for the disagreement count, and "
  "centroid and link are near-transcriptions that MUST be exact for the k_xd physical match to "
  "bind.","both declared; 'deliberately different implementation' is narrowed to the component "
  "finder. The checker confirms no online id reaches a verdict."),
F("C-27","the mission binds its parent and none of its own inputs","UPHELD",
  "correct and material after a fifth rollback.",
  "an input and output manifest is written and the mission is committed."),
F("C-28","the vocabulary-gap note keeps a strong claim","UPHELD__SUPERSEDED",
  "correct as written, and now moot: once C-03 is granted a route IS eligible, so the terminal no "
  "longer needs a gap note. The checker is also right that a prose instrumentation repair in an "
  "artefact is a handoff in all but name.",
  "the gap note is deleted. The instrumentation repair is moved into the authorised handoff as a "
  "PRECONDITION rather than left as prose."),
]
art={
 "MISSION":"LDFMA01","SECTION":"9 — checker adjudication","GENERATED_UTC":U,
 "MAX_INDEPENDENT_CHECKERS":1,"CHECKERS_USED":1,"REVIEW_CASCADE":"none — adjudicated once",
 "CHECKER_RAW_RETURN":{"path":"LDFMA01/review/LDFMA01_CHECKER_RAW.txt","sha256":sha(RAW),
   "bytes":len(open(RAW,'rb').read()),
   "WRITTEN_AND_HASHED_AND_EXTERNALISED_BEFORE_ANY_FINDING_WAS_ACTED_ON":True},
 "N_FINDINGS":len(A),
 "VERDICT_COUNTS":{v:sum(1 for f in A if f["VERDICT"]==v) for v in sorted({f["VERDICT"] for f in A})},
 "LOAD_BEARING_UPHELD":[f["id"] for f in A if "LOAD_BEARING" in f["VERDICT"]],
 "FINDINGS":A,
 "THE_CHECKER_WAS_WRONG_ABOUT_EXACTLY_ONE_THING":{
   "finding":"C-05","what":"it names i153 as one of the five worlds that flip under the probe",
   "fact":"i153's recovered removal at step 715 lies outside its identity, which ends at 714, and "
     "it was already NOT counted as COMPLETE. The rest of C-05 is upheld.",
   "does_it_change_the_finding":"no — the FUNCTIONAL guard gap it identifies is real and i119 "
     "demonstrates it."},
 "RECOMPUTATIONS_PERFORMED_BY_THE_AUTHOR":{
   "poisson_expected_COMPLETE_worlds":round(poisson,3),
   "checker_value":5.81,"observed_under_the_probe":obs_complete,
   "lambda_min":round(min(l for _,l,_ in lam),4),"lambda_max":round(max(l for _,l,_ in lam),4),
   "lambda_mean":round(statistics.mean([l for _,l,_ in lam]),4),
   "corrected_COMPLETE":corr_complete,"corrected_FUNCTIONAL_upper_bound":corr_func_upper,
   "component_level_multiply_occupied_particle_step_fraction":round(comp_ge2/ptot,4),
   "NOT_the_same_as_the_checkers_cell_level_figure":True},
 "PER_WORLD_LAMBDA":[{"tag":t,"lambda":round(l,4),"birth_observed":b,
    "P_at_least_one_removal":round(1-math.exp(-l),4)} for t,l,b in lam],
 "BOUNDARY_TABLE":boundary,
 "CONSEQUENCE_FOR_THE_TERMINAL":"C-03 is upheld and it removes the argument on which the pause "
   "rested. Route A is re-classified as eligible with E3 as primary. The disposition changes from "
   "the pause terminal to LOCKED_DAUGHTER_FAILURE_MECHANISM_IDENTIFIED__ONE_MATCHED_CONTROL_TEST_"
   "ELIGIBLE, which is the checker's own recommendation.",
 "NO_FINDING_WAS_DISMISSED":True,
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED"}
json.dump(art,open(f"{OUT}/LDFMA01_CHECKER_ADJUDICATION.json","w"),indent=1)
print("findings:",len(A))
for v,n in art["VERDICT_COUNTS"].items(): print("  %-38s %d"%(v,n))
print("load-bearing upheld:",art["LOAD_BEARING_UPHELD"])
print("poisson %.3f vs observed %d | corrected COMPLETE %d FUNCTIONAL<=%d"%(poisson,obs_complete,corr_complete,corr_func_upper))
