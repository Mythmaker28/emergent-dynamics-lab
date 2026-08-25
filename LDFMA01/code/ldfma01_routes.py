"""LDFMA01 sections 6-8 — Route A, Route B and the hard arbitration. Nothing is executed."""
from __future__ import annotations
import json,glob,math,statistics,hashlib,datetime
from math import comb
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
REM=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
REM=[r for r in REM if r.get("E_locked_daughter_interval")]
PART=json.load(open(f"{OUT}/LDFMA01_FAILURE_PARTITION.json"))
AMB=json.load(open(f"{OUT}/LDFMA01_AMBIENT_SATURATION_MECHANISM.json"))
AUT=json.load(open(f"{OUT}/LDFMA01_SINGLE_SUCCESS_AUTOPSY.json"))
BUDGET=512; ARMS=2; YIELD=22/256
PAIRS=int(round(BUDGET/ARMS*YIELD))
def mcnemar_power(n,p1,p0,alpha=0.05):
    b=p1*(1-p0); c=p0*(1-p1); tot=0.0
    for d in range(0,n+1):
        pd=comb(n,d)*((b+c)**d)*((1-b-c)**(n-d))
        if pd<1e-12: continue
        q=b/(b+c) if (b+c)>0 else 0.5
        for k in range(0,d+1):
            pk=comb(d,k)*(q**k)*((1-q)**(d-k))
            if sum(comb(d,i)*0.5**d for i in range(k,d+1))<=alpha: tot+=pd*pk
    return tot
lif=[r["E_locked_daughter_interval"]["post_removal_identity_lifetime"] for r in REM]
logsd=statistics.pstdev([math.log(x) for x in lif])
p_corr=5/22
GRID=[{"p_selective":p1,"p_sham":p0,"power_at_%d_pairs"%PAIRS:round(mcnemar_power(PAIRS,p1,p0),3)}
      for p1,p0 in [(p_corr,0.0),(p_corr,0.05),(p_corr,0.10),(p_corr,p_corr),(0.40,0.0),(0.50,0.0)]]
COND=["1 answers a question directly relevant to daughter independence",
      "2 does not substitute ambient-population turnover for locked-daughter turnover",
      "3 its decision rule has a non-arbitrary physical or causal derivation",
      "4 the endpoint is reconstructable offline",
      "5 one prospective design is decision-capable within 512 primary arm instances",
      "6 no developmental outcome is used to choose its threshold",
      "7 a positive result would materially advance the reproduction question"]
E3={"id":"E3","name":"locked-daughter persistence, SELECTIVE vs SHAM, paired",
 "scientific_question":"does removing the parent change how long the locked daughter's identity "
   "persists under the frozen strict rule?",
 "causal_estimand":"the paired within-block difference in post-trigger identity lifetime between "
   "the SELECTIVE and SHAM arms on the same seed",
 "independent_unit":"the base block (one seed, one trigger, both arms)",
 "matched_arms":["SELECTIVE_PARENT_REMOVAL","SHAM_NO_REMOVAL"],
 "time_origin":"the trigger step t_m, identical in both arms by construction",
 "endpoint":"continuous: steps of identity survival after t_m",
 "censoring":"administrative at the horizon; observed in 0 of 22 retrospective worlds, all of "
   "which terminated by SPLIT_OR_TIE well before the horizon",
 "competing_events":"third centre, merge, extinction — none observed as a terminator in 22 of 22",
 "decision_rule":"Wilcoxon signed-rank on the paired log-lifetime difference, two-sided, alpha 0.05",
 "claim_ceiling":"a persistence difference. NOT reproduction, NOT heredity, NOT turnover.",
 "CONDITIONS":{
  COND[0]:{"verdict":"PARTIAL","why":"persistence is necessary for a daughter to turn over, but "
    "the funnel just measured that persistence is NOT the binding constraint: the daughters "
    "persist a median 230 steps and up to 1472, and still fail."},
  COND[1]:{"verdict":"PASS","why":"it is the locked daughter and nothing else."},
  COND[2]:{"verdict":"PASS","why":"a paired difference needs no threshold beyond zero."},
  COND[3]:{"verdict":"PASS","why":"reconstructed here by a third implementation."},
  COND[4]:{"verdict":"PASS","why":"22 paired blocks, paired log-SD %.2f; a Wilcoxon signed-rank "
    "detects roughly a two-fold shift at 80 %% power."%logsd},
  COND[5]:{"verdict":"PASS","why":"no threshold is taken from a developmental outcome."},
  COND[6]:{"verdict":"FAIL","why":"a persistence difference would show the removal has SOME causal "
    "effect on the daughter. It would not show the daughter completes a constituent turnover, "
    "which is the reproduction-relevant event and the one that fails. Answering a question about "
    "a variable the funnel has just shown is not binding does not materially advance the "
    "reproduction question."}},
 "ELIGIBLE":False,
 "CLASSIFICATION":"MATCHED_CONTROL_OBJECT_NOT_SCIENTIFICALLY_ALIGNED"}
E5={"id":"E5","name":"ambient-population response, SELECTIVE vs SHAM, paired",
 "scientific_question":"does removing the parent change the ambient identity/population dynamics?",
 "causal_estimand":"the paired within-block difference in the count of COMPLETE_TURNOVER intervals "
   "anywhere in the world after t_m",
 "independent_unit":"the base block","matched_arms":["SELECTIVE_PARENT_REMOVAL","SHAM_NO_REMOVAL"],
 "time_origin":"t_m","endpoint":"count per world","censoring":"administrative at the horizon",
 "competing_events":"none defined at the population level",
 "decision_rule":"paired test on the count difference",
 "claim_ceiling":"a population-level response. NOT the daughter.",
 "CONDITIONS":{
  COND[0]:{"verdict":"FAIL","why":"the object is the population, not the daughter's independence."},
  COND[1]:{"verdict":"FAIL","why":"it substitutes ambient-population turnover for locked-daughter "
    "turnover by construction — the exact substitution condition 2 exists to forbid. Section 5 "
    "measured that 2017 of 2018 ambient complete intervals begin AFTER the locked identity has "
    "already ended, in a population that did not exist at the removal."},
  COND[2]:{"verdict":"PASS","why":"a paired difference needs no threshold."},
  COND[3]:{"verdict":"PASS","why":"reconstructed here."},
  COND[4]:{"verdict":"PASS","why":"counts are large; 22 pairs would detect a modest shift."},
  COND[5]:{"verdict":"PASS","why":"no outcome-chosen threshold."},
  COND[6]:{"verdict":"FAIL","why":"a population response at a 706-to-2614-step lag says nothing "
    "about whether a daughter reproduces."}},
 "ELIGIBLE":False,
 "CLASSIFICATION":"MATCHED_CONTROL_OBJECT_NOT_SCIENTIFICALLY_ALIGNED"}
E1C={"id":"E1-corrected","name":"locked-daughter COMPLETE_TURNOVER with the attribution defect "
   "repaired, SELECTIVE vs SHAM, paired",
 "why_it_is_considered":"it is the only candidate aligned with the identified mechanism. It is "
   "NOT a new endpoint: it is the frozen locked-daughter endpoint with the event-attribution "
   "defect quantified in section 3 repaired at the instrumentation level.",
 "scientific_question":"does removing the parent change the probability that the locked daughter "
   "completes a constituent turnover inside its own identity?",
 "causal_estimand":"the paired difference in that binary, SELECTIVE minus SHAM, on the same seed",
 "independent_unit":"the base block","matched_arms":["SELECTIVE_PARENT_REMOVAL","SHAM_NO_REMOVAL"],
 "time_origin":"t_m","endpoint":"binary per block","censoring":"administrative at the horizon",
 "competing_events":"identity termination by split, merge or extinction before completion",
 "decision_rule":"exact McNemar on discordant pairs, one-sided, alpha 0.05",
 "claim_ceiling":"a causal effect of parent removal on locked-daughter constituent turnover. NOT "
   "reproduction, NOT heredity.",
 "RETROSPECTIVE_RATE_USED_FOR_POWER_ONLY":{"value":"5/22","note":"the rate the SAME archives give "
   "when the identical ledger rows are attributed one step earlier. Used to size a hypothetical "
   "design. It is NOT adopted as a verdict anywhere in this mission."},
 "CONDITIONS":{
  COND[0]:{"verdict":"PASS","why":"it is exactly the reproduction-relevant event."},
  COND[1]:{"verdict":"PASS","why":"restricted to the one locked identity."},
  COND[2]:{"verdict":"PASS","why":"McNemar on discordant pairs; no free threshold."},
  COND[3]:{"verdict":"PASS","why":"reconstructable, given the instrumentation repair."},
  COND[4]:{"verdict":"FAIL","why":"only %d paired blocks are expected from 512 primary arm "
    "instances, because just 8.6 %% of LAW_C worlds ever reach a removal. Exact McNemar power at "
    "%d pairs is 0.58 even against the most extreme alternative (0.227 vs 0.000) and 0.15 against "
    "0.227 vs 0.100. It cannot decide anything but near-total suppression."%(PAIRS,PAIRS)},
  COND[5]:{"verdict":"PARTIAL","why":"the attribution repair is justified by a defect argument — "
    "the frozen rule recovers 1 of the 8.44 removals the decay rate predicts — and not by the "
    "value it produces. But the repair was identified AFTER the outcomes were known, so it must "
    "be frozen and independently justified before any world runs, not adopted here."},
  COND[6]:{"verdict":"PASS","why":"a demonstrated causal effect on locked-daughter turnover would "
    "materially advance the reproduction question."}},
 "ELIGIBLE":False,
 "CLASSIFICATION":"MATCHED_CONTROL_TEST_NOT_DECISION_CAPABLE"}
mc={"MISSION":"LDFMA01","SECTION":"6 — matched-control endpoints","GENERATED_UTC":U,
 "DERIVED_FROM_FIRST_PRINCIPLES_NOT_INHERITED":"E3 and E5 are re-derived here against the seven "
   "conditions. Being listed in FIMRCC01 gives them no standing.",
 "MAX_ROUTE_CANDIDATES":3,"N_CANDIDATES":3,
 "CANDIDATES":[E1C,E3,E5],
 "ELIGIBLE_CANDIDATES":[c["id"] for c in (E1C,E3,E5) if c["ELIGIBLE"]],
 "ROUTE_A_CLASSIFICATION":"MATCHED_CONTROL_TEST_NOT_DECISION_CAPABLE",
 "THE_BINDING_REASON":"the trigger yield. Only 22 of 256 LAW_C worlds reach a selective removal, "
   "so a two-arm design inside 512 primary arm instances yields about %d paired blocks. That is "
   "enough to detect near-total suppression and nothing finer."%PAIRS,
 "NOT_CHOSEN_FOR_POWER":"E3 has more statistical power than E1-corrected and was still rejected, "
   "because it measures a variable the funnel showed is not the binding constraint."}
json.dump(mc,open(f"{OUT}/LDFMA01_MATCHED_CONTROL_ENDPOINTS.json","w"),indent=1)
json.dump({"MISSION":"LDFMA01","SECTION":"6 — matched-control power","GENERATED_UTC":U,
 "BUDGET_PRIMARY_ARM_INSTANCES":BUDGET,"ARMS":ARMS,"INSTANCES_PER_ARM":BUDGET//ARMS,
 "TRIGGER_YIELD_PER_WORLD":round(YIELD,6),
 "EXPECTED_PAIRED_BLOCKS":PAIRS,
 "TEST":"exact McNemar on discordant pairs, one-sided, alpha 0.05",
 "POWER_GRID":GRID,
 "DISCORDANT_PAIRS_NEEDED_FOR_SIGNIFICANCE_ALL_ONE_WAY":5,
 "E3_CONTINUOUS_ALTERNATIVE":{"paired_log_SD_from_the_22_SELECTIVE_worlds":round(logsd,3),
   "n_pairs":PAIRS,"detectable_shift_at_80pc_power_approx":"about a two-fold change in persistence",
   "note":"reported so the rejection of E3 cannot be mistaken for a power argument. E3 has the "
          "power; it does not have the alignment."},
 "CONCLUSION":"no matched-control endpoint is simultaneously aligned with the identified mechanism "
   "and decision-capable inside the declared budget."},
 open(f"{OUT}/LDFMA01_MATCHED_CONTROL_POWER.json","w"),indent=1)
print("expected paired blocks:",PAIRS)
for g in GRID: print("  ",g)
print("Route A ->",mc["ROUTE_A_CLASSIFICATION"])
