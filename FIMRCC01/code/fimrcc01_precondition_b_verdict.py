"""FIMRCC01 Section 3 — Precondition B verdict: the two classifiers, over all 256 LAW_C archives."""
from __future__ import annotations
import json, glob, hashlib, datetime, os
REPO="/home/claude/edl"; OUT=f"{REPO}/FIMRCC01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pb3/*.json"))]
assert len(rows)==256 and all(r["law"]=="LAW_C_MCTT01" for r in rows)

def cnt(pred): return sum(1 for r in rows if pred(r))
steps=sum(r["N_STEPS_COMPARED"] for r in rows)
eps  =sum(r["N_EPISODES"][0] for r in rows)
sc_steps=sum(r["COMPONENTS_FAST_VS_UNIONFIND"]["n_steps_checked"] for r in rows)
sc_bad  =sum(r["COMPONENTS_FAST_VS_UNIONFIND"]["n_disagreements"] for r in rows)
removed=[r for r in rows if r["removal_applied"]]

gates={
 "COMPONENT_COUNT_AGREES_AT_EVERY_STEP":cnt(lambda r:r["N_COMPONENT_COUNT_DISAGREEMENTS"]==0)==256,
 "EPISODES_AGREE_IN_EVERY_WORLD":cnt(lambda r:r["EPISODES_AGREE"])==256,
 "M2_AGREES_IN_EVERY_WORLD":cnt(lambda r:r["M2_AGREES"])==256,
 "M3_AGREES_IN_EVERY_WORLD":cnt(lambda r:r["M3_AGREES"])==256,
 "M5_AGREES_IN_EVERY_WORLD":cnt(lambda r:r["M5_AGREES"])==256,
 "EVENT_STEP_AGREES_IN_EVERY_WORLD":cnt(lambda r:r["EVENT_STEP_AGREES"])==256,
 "XD_PHYSICAL_MATCH_IS_A_BIJECTION_IN_EVERY_WORLD":cnt(lambda r:r["XD_PHYSICAL_MATCH_IS_A_BIJECTION"])==256,
 "FAST_COMPONENTS_EQUAL_UNIONFIND_ON_EVERY_SAMPLED_STEP":sc_bad==0}
PASS=all(gates.values())

art={
 "MISSION":"FIMRCC01","SECTION":"3 — Precondition B verdict","GENERATED_UTC":U,
 "LAW":"LAW_C_MCTT01","N_WORLDS":len(rows),
 "CLASSIFIER_1":{"module":"TLMR01/code/tlmr01_offline.py","status":"frozen, byte-unchanged",
   "sha256":hashlib.sha256(open(f"{REPO}/TLMR01/code/tlmr01_offline.py","rb").read()).hexdigest(),
   "reads_the_online_component_id":True,
   "where":"A.comps is built from the archive's compressed component rows, which carry the online "
           "id, and identity_intervals keys its per-step cell sets by that id."},
 "CLASSIFIER_2":{"module":"FIMRCC01/code/fimrcc01_independent.py","status":"independent",
   "sha256":hashlib.sha256(open(f"{REPO}/FIMRCC01/code/fimrcc01_independent.py","rb").read()).hexdigest(),
   "reads_the_online_component_id":False,
   "inputs_it_uses":["the step index t","the cell coordinates (y,x)","the per-cell Y occupancy",
                     "the world Y total from the step array","the birth and death ledgers"],
   "what_it_recomputes":["the components, by toroidal single-linkage at CORE_R from coordinates alone",
                         "the centroids, from the cell sets",
                         "the per-component Y occupancy, by summing the cell rows",
                         "the identity links, the episodes, the maturation gates, the identity "
                         "intervals and their event content"],
   "algorithmic_independence":"components are closed by label propagation to the per-row minimum, "
     "not by union-find. Both formulations are implemented and checked against each other."},
 "THE_ONE_DECLARED_DEPENDENCY":{
   "quantity":"the local X disc mass xd",
   "why_it_cannot_be_recomputed":"the narrow archive stores the X field only on Y-occupied cells, "
     "and the frozen gate sums X over an 81-cell disc most of which is not Y-occupied.",
   "how_it_is_obtained":"read from the archive's component rows and attached by matching "
     "(centroid, ncells, nY) — a physical match. No component id is used to make the match.",
   "what_would_expose_a_problem":"a non-bijective match, which is counted below and is zero.",
   "what_it_affects":"only GATE_local_x_ratio in M3. The component structure, M2, the identity "
     "intervals and the event step do not depend on it.",
   "THIS_IS_STATED_RATHER_THAN_CLAIMED_AWAY":True},
 "SCALE_OF_THE_COMPARISON":{
   "worlds":len(rows),"steps_compared":steps,"episodes_compared":eps,
   "worlds_with_a_removal":len(removed),
   "component_algorithm_selfcheck_steps":sc_steps,
   "component_algorithm_selfcheck_disagreements":sc_bad},
 "AGREEMENT":{
   "worlds_with_full_agreement":cnt(lambda r:r["ALL_AGREE"]),
   "of":len(rows),
   "percent":100.0*cnt(lambda r:r["ALL_AGREE"])/len(rows),
   "component_count_disagreements_total":sum(r["N_COMPONENT_COUNT_DISAGREEMENTS"] for r in rows),
   "xd_match_failures_total":sum(r["N_XD_MATCH_FAILURES"] for r in rows)},
 "GATES":gates,
 "REQUIRED":"100 % agreement on M2, M3, M5 and the event step",
 "PRECONDITION_B":"PASS" if PASS else "FAIL",
 "DISAGREEING_WORLDS":[r["tag"] for r in rows if not r["ALL_AGREE"]],
 "EVENT_STEPS":{r["tag"]:r["EVENT_STEP"] for r in removed},
 "WHAT_THIS_ESTABLISHES":"that every number FIMRCC01 will read out of an archive can be produced "
   "without trusting the online component bookkeeping. It does not establish that the endpoint is "
   "the right one, and it does not establish anything about reproduction, heredity, life or "
   "autonomous cohesion, in the affirmative or in the negative.",
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "PER_WORLD":[{"tag":r["tag"],"seed":r["seed"],"steps":r["N_STEPS_COMPARED"],
   "n_episodes":r["N_EPISODES"][0],"ALL_AGREE":r["ALL_AGREE"],
   "event_step":r["EVENT_STEP"],"removal":r["removal_applied"]} for r in rows]}
json.dump(art,open(f"{OUT}/FIMRCC01_INDEPENDENT_ENDPOINT_QUALIFICATION.json","w"),indent=1)

for k,v in gates.items(): print("%-56s %s"%(k,v))
print()
print("worlds %d | steps compared %d | episodes compared %d"%(len(rows),steps,eps))
print("component-algorithm selfcheck: %d steps, %d disagreements"%(sc_steps,sc_bad))
print("full agreement: %d / %d"%(cnt(lambda r:r['ALL_AGREE']),len(rows)))
print("PRECONDITION_B =",art["PRECONDITION_B"])
print("sha256",hashlib.sha256(open(f"{OUT}/FIMRCC01_INDEPENDENT_ENDPOINT_QUALIFICATION.json","rb").read()).hexdigest())
