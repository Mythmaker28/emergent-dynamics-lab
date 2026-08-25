"""LDFMA01 section 7 — Route B, and section 8, the hard arbitration."""
from __future__ import annotations
import json,hashlib,datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
PART=json.load(open(f"{OUT}/LDFMA01_FAILURE_PARTITION.json"))
MC=json.load(open(f"{OUT}/LDFMA01_MATCHED_CONTROL_ENDPOINTS.json"))
COND=["targets the dominant locked-daughter failure directly",
 "is smaller than adding a new species or genealogy",
 "its causal prediction is directional before runs",
 "exactly one value or deterministic rule can be fixed without a sweep",
 "one experiment can falsify it within 512 worlds",
 "it cannot trivially force success by definition"]
C1={"id":"B1","name":"occupancy-floored Y removal (spare the last constituent)",
 "exact_code_path":"lawspec_v2 / kinetics decay of species Y: apply muY only where the cell's "
   "component occupancy is at least 2",
 "new_degree_of_freedom":"none numeric — one deterministic predicate on an already-computed "
   "quantity",
 "physical_interpretation":"an organiser does not lose its last constituent to spontaneous decay",
 "which_failure_it_targets":"L3, birth without removal — nominally",
 "what_it_leaves_unchanged":"kY, muY, p_hop, the X LawSpec, the scheduler, the classifier",
 "new_state_variable":"none","new_instrumentation":"none",
 "falsifying_fixture":"a two-particle component must lose exactly one constituent and survive",
 "prospective_primary_endpoint":"locked-daughter COMPLETE_TURNOVER",
 "hard_experiment_cost":"512 worlds",
 "CONDITIONS":{
  COND[0]:{"verdict":"FAIL","why":"it does not target the dominant failure, because the dominant "
    "failure is not that removals fail to happen. Section 3 measured 8 of the 8.44 removals the "
    "decay rate predicts INSIDE the locked daughters, and 0 of 22 daughters went extinct: every "
    "one terminated by SPLIT_OR_TIE, not by losing its last constituent. The removals happen and "
    "the daughters survive them. A floor on removal repairs a failure that was not observed."},
  COND[1]:{"verdict":"PASS"},COND[2]:{"verdict":"PASS"},COND[3]:{"verdict":"PASS"},
  COND[4]:{"verdict":"PASS"},
  COND[5]:{"verdict":"PARTIAL","why":"it does not force turnover, but it removes the only way a "
    "small component can die, which inflates persistence for every object including the ambient "
    "population."}},
 "ELIGIBLE":False}
C2={"id":"B2","name":"occupancy-dependent Y birth throttling",
 "exact_code_path":"the Y-gated birth term: scale kY by a function of local component occupancy",
 "new_degree_of_freedom":"one throttling rule",
 "physical_interpretation":"growth saturates as an organiser fills",
 "which_failure_it_targets":"the late-time ambient bloom that saturates the unrestricted endpoint",
 "what_it_leaves_unchanged":"muY, mobility, X LawSpec, scheduler, classifier",
 "new_state_variable":"none","new_instrumentation":"none",
 "falsifying_fixture":"a large component must show a suppressed birth rate",
 "prospective_primary_endpoint":"locked-daughter COMPLETE_TURNOVER",
 "hard_experiment_cost":"512 worlds",
 "CONDITIONS":{
  COND[0]:{"verdict":"FAIL","why":"the ambient bloom is not what fails the locked daughter. "
    "Section 5 measured that 2017 of 2018 ambient complete intervals begin AFTER the locked "
    "identity has already ended, and that the world holds 2 to 5 Y particles at the trigger. "
    "Suppressing a bloom that arrives 706 to 2614 steps later cannot change the daughter's fate."},
  COND[1]:{"verdict":"PASS"},COND[2]:{"verdict":"PASS"},
  COND[3]:{"verdict":"FAIL","why":"no single throttling rule is derivable from the evidence; "
    "choosing its shape would be a parameter search."},
  COND[4]:{"verdict":"PASS"},COND[5]:{"verdict":"PASS"}},
 "ELIGIBLE":False}
C3={"id":"B3","name":"local cohesion regulation to stop the identity terminating on split",
 "exact_code_path":"the Y diffusion term: reduce p_hop_Y inside an occupied component",
 "new_degree_of_freedom":"one cohesion rule",
 "physical_interpretation":"constituents of one organiser hold together",
 "which_failure_it_targets":"the SPLIT_OR_TIE termination observed in 22 of 22",
 "what_it_leaves_unchanged":"kY, muY, X LawSpec, scheduler, classifier",
 "new_state_variable":"none","new_instrumentation":"none",
 "falsifying_fixture":"a two-cell component must show a reduced split rate",
 "prospective_primary_endpoint":"locked-daughter COMPLETE_TURNOVER",
 "hard_experiment_cost":"512 worlds",
 "CONDITIONS":{
  COND[0]:{"verdict":"PARTIAL","why":"SPLIT_OR_TIE does terminate 22 of 22 identities. But it is "
    "not what stops the turnover: the daughters already survive long enough for the decay rate to "
    "deliver 8.44 expected removals, and 8 of them are measurable in the ledger. Extending the "
    "window is not the repair the evidence asks for."},
  COND[1]:{"verdict":"PASS"},COND[2]:{"verdict":"PASS"},
  COND[3]:{"verdict":"FAIL","why":"p_hop_Y is an already-executed frozen value; making it "
    "state-dependent introduces a new value that cannot be fixed without a sweep, and "
    "PARAMETER_SWEEP is forbidden."},
  COND[4]:{"verdict":"PASS"},
  COND[5]:{"verdict":"FAIL","why":"suppressing splits directly inflates identity lifetime, which "
    "is the denominator of the very endpoint being tested."}},
 "ELIGIBLE":False}
rb={"MISSION":"LDFMA01","SECTION":"7 — minimal architecture candidates","GENERATED_UTC":U,
 "PRECONDITION_FOR_CONSIDERING_ROUTE_B":"an architecture change is evaluated only if the failure "
   "funnel identifies a specific mechanism the unchanged architecture cannot test cleanly.",
 "IS_THAT_PRECONDITION_MET":False,
 "WHY_NOT":"the funnel identified the mechanism, and the mechanism is not in the architecture. "
   "Inside the locked daughters the decay rate predicts 8.44 Y removals over 11,385 particle-steps; "
   "8 of them are present in the ledger and the daughters survived them, with 0 of 22 extinctions. "
   "What fails is the frozen endpoint's EVENT ATTRIBUTION, which asks whether the event cell is in "
   "the component's cell set at step t, while the archive writes cell rows after the step — so a "
   "decay that empties a cell is invisible to it. The physics already produces locked-daughter "
   "constituent turnover; the measurement does not see it.",
 "CANDIDATES":[C1,C2,C3],"MAX_CANDIDATES":3,"N_CANDIDATES":3,
 "ELIGIBLE_CANDIDATES":[],
 "ROUTE_B_CLASSIFICATION":"NO_MINIMAL_CHANGE_JUSTIFIED",
 "THE_GENERAL_ARGUMENT":"changing the physics to repair a measurement defect would be the worst "
   "available move. It would alter the substrate on the strength of an artefact, and any apparent "
   "improvement would be uninterpretable.",
 "WHAT_IS_JUSTIFIED_INSTEAD_AND_IS_NOT_AN_ARCHITECTURE_CHANGE":
   "an INSTRUMENTATION repair: the archive should record each ledger event with the component "
   "membership it had at the moment it occurred. That changes no law, no parameter and no "
   "classifier. It is not authorised here and no handoff is emitted for it.",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED"}
json.dump(rb,open(f"{OUT}/LDFMA01_MINIMAL_ARCHITECTURE_CANDIDATES.json","w"),indent=1)
json.dump({"MISSION":"LDFMA01","SECTION":"7 — architecture test feasibility","GENERATED_UTC":U,
 "EVALUATED":3,"ELIGIBLE":0,
 "PER_CANDIDATE":[{"id":c["id"],"eligible":c["ELIGIBLE"],
   "failed_conditions":[k for k,v in c["CONDITIONS"].items() if v["verdict"]=="FAIL"]} for c in (C1,C2,C3)],
 "NO_NEW_SPECIES_WAS_CONSIDERED":True,"NO_PARTICLE_GENEALOGY_WAS_CONSIDERED":True,
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "CLASSIFICATION":"NO_MINIMAL_CHANGE_JUSTIFIED"},
 open(f"{OUT}/LDFMA01_ARCHITECTURE_TEST_FEASIBILITY.json","w"),indent=1)

# ---------------- section 8: arbitration ----------------
SCORE=[
 {"criterion":"scientific alignment with reproduction","Route_A":"E1-corrected aligned; E3 and E5 not",
  "Route_B":"none of the three targets the measured mechanism","Route_C":"n/a"},
 {"criterion":"clarity of estimand","Route_A":"clear for all three candidates","Route_B":"clear",
  "Route_C":"n/a"},
 {"criterion":"ability to falsify","Route_A":"yes, but only near-total suppression at 22 pairs",
  "Route_B":"yes, but would falsify a hypothesis the evidence does not support","Route_C":"n/a"},
 {"criterion":"independence from post-hoc thresholds","Route_A":"E1-corrected needs an attribution "
  "repair identified after the outcomes; it must be frozen and justified before any world runs",
  "Route_B":"B2 and B3 would need a swept value","Route_C":"n/a"},
 {"criterion":"world cost","Route_A":"512 arm instances for ~22 paired blocks","Route_B":"512 worlds",
  "Route_C":"0"},
 {"criterion":"implementation risk","Route_A":"low; the arms already exist and the SHAM no-op is "
  "proved bit-exact","Route_B":"high; a substrate change on the strength of an artefact","Route_C":"none"},
 {"criterion":"risk of another methodological loop","Route_A":"high — an underpowered test would "
  "return NOT_REPLICATED for a power reason, exactly the failure FIMRCC01 already stopped",
  "Route_B":"very high — an uninterpretable improvement","Route_C":"low"}]
arb={"MISSION":"LDFMA01","SECTION":"8 — route arbitration","GENERATED_UTC":U,
 "ARBITRATION_ORDER_APPLIED":["1 prefer Route A when a matched-control design is scientifically "
   "aligned, non-arbitrary and decision-capable","2 select Route B only when Route A fails and one "
   "minimal architecture change directly targets an identified mechanism","3 otherwise pause"],
 "STEP_1_ROUTE_A":{"classification":"MATCHED_CONTROL_TEST_NOT_DECISION_CAPABLE",
   "aligned_candidate":"E1-corrected","why_it_fails":"only ~22 paired blocks are reachable inside "
     "512 primary arm instances, because 8.6 % of LAW_C worlds reach a removal. Exact McNemar "
     "power is 0.58 against the most extreme alternative and 0.15 against a modest one.",
   "the_two_powered_candidates_were_rejected_on_alignment_not_power":True},
 "STEP_2_ROUTE_B":{"classification":"NO_MINIMAL_CHANGE_JUSTIFIED",
   "why":"the identified mechanism is a measurement-attribution defect, not a missing physical "
     "degree of freedom. The decay already delivers the removals and the daughters already "
     "survive them."},
 "STEP_3":"pause",
 "SELECTED_ROUTE":"ROUTE_C__PAUSE",
 "MAX_SELECTED_ROUTES":1,"N_SELECTED":1,
 "SCORING":SCORE,
 "NO_SECOND_ROUTE_WAS_SELECTED":True,"NO_HANDOFF_IS_EMITTED":True,
 "A_VOCABULARY_GAP_IN_THE_FROZEN_TERMINAL_SET":{
   "what_the_evidence_reached":"the locked-daughter failure mechanism IS identified, "
     "quantitatively and by a third independent reconstruction, and NO route is eligible.",
   "what_the_frozen_terminals_offer":"they pair MECHANISM_IDENTIFIED with an eligible route, or "
     "pair a pause with NOT_IDENTIFIABLE. There is no terminal for identified-and-no-route.",
   "what_was_done":"the launcher permits no fifth disposition, so "
     "LOCKED_DAUGHTER_FAILURE_NOT_IDENTIFIABLE__LINEAGE_ROUTE_PAUSED is used for its PAUSE half, "
     "and this note records that its NOT_IDENTIFIABLE half understates the result. The mechanism "
     "is named in section 3 and section 5 and should be read there, not from the terminal string.",
   "THIS_IS_REPORTED_RATHER_THAN_RESOLVED_BY_INVENTING_A_TERMINAL":True}}
json.dump(arb,open(f"{OUT}/LDFMA01_ROUTE_ARBITRATION.json","w"),indent=1)
print("Route A:",arb["STEP_1_ROUTE_A"]["classification"])
print("Route B:",arb["STEP_2_ROUTE_B"]["classification"])
print("SELECTED:",arb["SELECTED_ROUTE"])
