"""FIMRCC01 Section 4 — the endpoint candidate set and the selection rule, PRE-REGISTERED.

Written and hashed BEFORE any candidate's properties are computed. The TLMR01 handoff requires the
endpoint to be shown to discriminate before it is used, and requires a discriminating endpoint to
be declared and frozen before world 1 if the inherited one is saturated. It also says, in the same
paragraph, that this is a design requirement and not a licence to search endpoints after seeing
outcomes. This file is how that distinction is made enforceable: the candidate set is CLOSED here,
the criterion is fixed here, and the tie-break deliberately prefers the endpoint CLOSEST to the
inherited definition rather than the one with the most power.
"""
from __future__ import annotations
import json, hashlib, datetime
OUT="/home/claude/edl/FIMRCC01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()

REG={
 "MISSION":"FIMRCC01","SECTION":"4 — endpoint pre-registration","GENERATED_UTC":U,
 "WHY":"FIMRCC01_LOCKED_IDENTITY_QUALIFICATION.json established, before world 1, that the "
   "inherited endpoint is saturated at this law (22 of 22 worlds) and that the same endpoint "
   "restricted to the locked daughter fires in 1 of 22. Neither is usable as it stands: the first "
   "carries no information, the second sits 1.22x above the endpoint-matched floor.",

 "CANDIDATE_SET_IS_CLOSED":True,
 "N_CANDIDATES":6,
 "CANDIDATES":[
  {"id":"E0","name":"inherited, unrestricted",
   "definition":"at least one identity interval ANYWHERE in the world satisfies the frozen DOTC01 "
     "FUNCTIONAL COMPLETE_TURNOVER strictly after t_m.",
   "kind":"binary per world","proximity_rank":0,
   "note":"this is TLMR01's D stage, unchanged. It is in the set because a candidate set that "
          "excluded the inherited endpoint would be choosing before it compared."},
  {"id":"E1","name":"locked daughter, FUNCTIONAL",
   "definition":"the frozen FUNCTIONAL COMPLETE_TURNOVER evaluated strictly inside the ONE "
     "identity interval that carries the daughter named at the 1->2 separation, strictly after t_m.",
   "kind":"binary per world","proximity_rank":1},
  {"id":"E2","name":"locked daughter, COMPLETE only",
   "definition":"at least one Y birth and at least one Y death inside the daughter's interval "
     "after t_m, the interval never empty. The FUNCTIONAL qualification (accepted X birth on both "
     "sides of the first removal, centre still present) is dropped.",
   "kind":"binary per world","proximity_rank":2},
  {"id":"E3","name":"locked daughter, persistence",
   "definition":"the number of steps the daughter's identity interval survives strictly after t_m, "
     "under the frozen link rule, compared BETWEEN ARMS on the same seed.",
   "kind":"count per world, used as a paired between-arm contrast","proximity_rank":3},
  {"id":"E4","name":"locked daughter, constituent events",
   "definition":"the number of Y births and the number of Y deaths attributed to the daughter's "
     "interval after t_m, compared BETWEEN ARMS on the same seed.",
   "kind":"count per world, used as a paired between-arm contrast","proximity_rank":4},
  {"id":"E5","name":"ambient population, paired",
   "definition":"the number of intervals satisfying the frozen COMPLETE_TURNOVER anywhere in the "
     "world after t_m, compared BETWEEN ARMS on the same seed. Uses the ambient population, but "
     "the occupancy confound is controlled by the matching rather than by restriction.",
   "kind":"count per world, used as a paired between-arm contrast","proximity_rank":5}],

 "CRITERION_1_ADMISSIBILITY":{
   "required":["computable by BOTH classifiers of Precondition B",
               "evaluable identically in all three arms SELECTIVE, SHAM and GLOBAL_OFF",
               "independent of the online component id",
               "defined without reference to any FIMRCC01 outcome",
               "defined without any new physical parameter"],
   "a_candidate_failing_any_of_these_is_struck":True},

 "CRITERION_2_DISCRIMINATION":{
   "test":"on TLMR01's 22 LAW_C worlds with a removal applied, the endpoint must not be saturated.",
   "SATURATION_THRESHOLD":0.90,
   "definition_of_saturated":"the endpoint takes the same value in more than 90 % of those worlds.",
   "THIS_THRESHOLD_IS_FIXED_HERE_BEFORE_ANY_CANDIDATE_IS_EVALUATED":True},

 "CRITERION_3_POWER":{
   "for_binary_candidates":{
     "test":"exact one-sided binomial, alpha = 0.05, against the endpoint-matched floor",
     "required":"at least 80 % power at n = 50 blocks, evaluated at the candidate's own TLMR01 rate",
     "floor":"F_INTEGRATED = 0.0032015171041760242 for endpoints matched to it; a candidate whose "
             "definition differs from the one F_INTEGRATED was matched to must state its own floor "
             "or be struck under criterion 1"},
   "for_paired_count_candidates":{
     "STATED_LIMITATION":"power is NOT estimable in advance. A paired contrast's power depends on "
       "the distribution of the within-block difference between arms, and there is no matched "
       "control arm anywhere in TLMR01's 512 worlds — that absence is the reason the SHAM arm "
       "exists. What CAN be reported in advance is whether the endpoint is non-degenerate: "
       "whether it varies at all across TLMR01's 22 worlds, which is a necessary and not a "
       "sufficient condition.",
     "reported_instead":["the number of distinct values across the 22 worlds",
                         "the min, median and max",
                         "the fraction of worlds at the modal value"],
     "NO_POWER_NUMBER_WILL_BE_INVENTED_FOR_THESE":True}},

 "SELECTION_RULE":{
   "step_1":"strike every candidate failing criterion 1.",
   "step_2":"strike every candidate failing criterion 2.",
   "step_3":"among binary candidates, strike every one failing criterion 3.",
   "step_4":"if one or more BINARY candidates survive, select the surviving binary candidate with "
            "the SMALLEST proximity_rank — the one closest to the inherited DOTC01 definition. "
            "This deliberately does not select for power.",
   "step_5":"if NO binary candidate survives, the mission cannot deliver the prospective "
            "replication of a binary event at n = 50 that its terminal dispositions name. The "
            "paired count candidates are then reported with their dispersion, and the CHOICE "
            "between (a) taking the terminal disposition "
            "CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED and (b) re-scoping the "
            "mission around a paired contrast IS REFERRED TO THE OWNER. It is not made here, "
            "because ADAPTIVE_SAMPLE_SIZE is forbidden, MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS is 0, "
            "and re-scoping changes what the frozen terminal strings mean.",
   "step_6":"no candidate outside the closed set above may be introduced later, under any "
            "circumstance, including by the independent checker."},

 "WHAT_IS_DELIBERATELY_NOT_PERMITTED":[
   "relaxing the strict identity rule so the daughter interval survives longer. BPRTC01's own "
   "freeze already named RELAXING_THE_STRICT_IDENTITY_RULE as a hazard; doing it to raise an "
   "event rate would be exactly the failure this programme exists to avoid.",
   "conditioning the endpoint on any quantity measured after the trigger.",
   "raising n above the declared 50 base blocks.",
   "introducing a seventh candidate after seeing this table."],

 "NEW_PARAMETER_POINTS":0,"PARAMETER_RETUNING":"forbidden","INTERPOLATION":"forbidden",
 "ADAPTIVE_SAMPLE_SIZE":"forbidden","ADAPTIVE_STOPPING":"forbidden",
 "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0,
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "THIS_FILE_IS_HASHED_AND_EXTERNALISED_BEFORE_ANY_CANDIDATE_IS_EVALUATED":True}

p=f"{OUT}/FIMRCC01_ENDPOINT_PREREGISTRATION.json"
json.dump(REG,open(p,"w"),indent=1)
print("FIMRCC01_ENDPOINT_PREREGISTRATION.json")
print("sha256 =",hashlib.sha256(open(p,"rb").read()).hexdigest())
