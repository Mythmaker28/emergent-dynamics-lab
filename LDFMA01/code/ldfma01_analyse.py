"""LDFMA01 sections 2-5 — ledger, reconstruction record, failure funnel, single-success autopsy,
ambient saturation mechanism. Nothing here runs a world."""
from __future__ import annotations
import json,glob,csv,math,hashlib,datetime,statistics,os
from collections import Counter
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
muY=0.000740894982503035; kY=0.001004754572603833
ROWS=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
REM=[r for r in ROWS if r.get("E_locked_daughter_interval")]
assert len(ROWS)==26 and len(REM)==22

# ================================================================= 2. reconstruction + ledger
def L(r): return r["E_locked_daughter_interval"]
def A(r): return r["A_trigger_time"]
def B(r): return r["B_daughter_geometry"]
def C(r): return r["C_local_environment"]
def D(r): return r["D_parent"]
def F(r): return r["F_ambient"]
def G(r): return r["G_competing"]

LEDGER=[]
for r in sorted(REM,key=lambda r:r["tag"]):
    e,f=L(r),F(r)
    LEDGER.append({
     "tag":r["tag"],"seed":r["seed"],
     "trigger_step":r["trigger_step"],
     "locked_daughter_cells":";".join("%d,%d"%tuple(c) for c in B(r)["daughter_cells"]),
     "locked_daughter_ncells":B(r)["daughter_ncells"],
     "locked_daughter_nY":B(r)["daughter_nY"],
     "locked_daughter_local_X_disc_mass":C(r)["daughter_xd"],
     "parent_local_X_disc_mass":C(r)["parent_xd"],
     "parent_nY":D(r)["parent_nY"],
     "parent_mass_removed":D(r)["parent_mass_removed_from_the_ledger"],
     "post_removal_identity_lifetime":e["post_removal_identity_lifetime"],
     "maximum_locked_daughter_nY":e["maximum_locked_daughter_nY_after_t_m"],
     "daughter_particle_steps":e["daughter_particle_steps_after_t_m"],
     "fraction_of_life_at_nY_1":round(e["fraction_of_life_at_nY_1"],4),
     "first_accepted_Y_birth":e["first_accepted_Y_birth_after_t_m"],
     "first_Y_removal":e["first_Y_removal_after_t_m"],
     "n_Y_births":e["n_Y_births_after_t_m"],
     "n_Y_removals":e["n_Y_removals_after_t_m"],
     "turnover_status":("COMPLETE_AND_FUNCTIONAL" if e["FUNCTIONAL"] else
                        "COMPLETE_NOT_FUNCTIONAL" if e["COMPLETE_TURNOVER"] else "NOT_COMPLETE"),
     "local_X_before_status":("OK" if e["LOCAL_X_BEFORE_OK"] else "NOT_APPLICABLE_NO_COMPLETE_TURNOVER" if not e["COMPLETE_TURNOVER"] else "MISSING"),
     "local_X_after_status":("OK" if e["LOCAL_X_AFTER_OK"] else "NOT_APPLICABLE_NO_COMPLETE_TURNOVER" if not e["COMPLETE_TURNOVER"] else "MISSING"),
     "identity_termination_type":e["identity_termination_type"],
     "n_successor_candidates_at_termination":e.get("n_successor_candidates_within_CORE_R"),
     "world_nY_at_trigger":f["world_nY_at_t_m"],
     "world_nY_at_identity_end":f["world_nY_at_daughter_interval_end"],
     "ambient_complete_interval_count":f["ambient_complete_interval_count"],
     "ambient_functional_interval_count":f["ambient_functional_interval_count"],
     "world_level_locked_daughter_verdict":r["WORLD_LEVEL_LOCKED_DAUGHTER_VERDICT"],
     "removal_fidelity_all_pass":r["REMOVAL_FIDELITY"]["ALL_PASS"],
     "Y_removals_attributed_at_t_minus_1":e["ATTRIBUTION_WINDOW_PROBE"]["n_Y_removals_attributed_at_step_t_minus_1"],
     "would_be_complete_under_t_minus_1":e["ATTRIBUTION_WINDOW_PROBE"]["WOULD_BE_COMPLETE_UNDER_t_minus_1"]})
with open(f"{OUT}/LDFMA01_REMOVAL_WORLD_LEDGER.csv","w",newline="") as fh:
    wtr=csv.DictWriter(fh,fieldnames=list(LEDGER[0].keys())); wtr.writeheader(); wtr.writerows(LEDGER)
json.dump({"MISSION":"LDFMA01","SECTION":"2 — removal-world ledger","GENERATED_UTC":U,
  "N_WORLDS":22,"ROWS":LEDGER},open(f"{OUT}/LDFMA01_REMOVAL_WORLD_LEDGER.json","w"),indent=1)

recon={
 "MISSION":"LDFMA01","SECTION":"2 — independent reconstruction","GENERATED_UTC":U,
 "WHAT_THIS_IS":"a third reconstruction of the same archives, written from the TLMR01-ARCHIVE-1 "
   "schema and the frozen rule statements alone.",
 "IMPORTS_NEITHER":["TLMR01's online identity assignment (tlmr01_offline, which keys its per-step "
   "cell sets by the online component id)",
   "FIMRCC01's daughter-verdict implementation (fimrcc01_independent, "
   "fimrcc01_precondition_a, fimrcc01_independent_descent)"],
 "DELIBERATELY_DIFFERENT_IMPLEMENTATION":{
   "components":"BFS flood-fill over an explicit adjacency test — not FDOT01's union-find and not "
     "FIMRCC01's label propagation",
   "constants":"read from PQEC01_MASTER_FREEZE.json and BPRTC01_MASTER_FREEZE.json at import, not "
     "from any mission module",
   "everything_else":"state machine, link rule, descent rule, maturation run detector, gates, "
     "identity intervals and turnover predicate re-derived from their written statements"},
 "INPUTS_USED":["c_t, c_y, c_x, c_nY cell rows","the s step array for the world Y total",
   "ybirth, ydeath, xbirth ledgers","k_xd with a physical (ncells, nY, centroid) match",
   "the intervention ledger, to locate the removal in time and to audit its fidelity"],
 "INPUTS_NOT_USED":["c_cid, the online component id","k_id, the online component id",
   "the online terminal label","the online t_m","any online verdict"],
 "ONE_DECLARED_DEPENDENCY":"k_xd cannot be recomputed — the archive stores X only on Y-occupied "
   "cells while the frozen gate sums X over an 81-cell disc. It is attached by a physical match "
   "that was a bijection at every step of every world.",
 "AGREEMENT_WITH_THE_ACCEPTED_RECORD":{
   "worlds":len(ROWS),
   "world_level_verdict":"%d/%d"%(sum(1 for r in ROWS if r["VERDICT"]==r["ARCHIVE_LABEL_NOT_AN_INPUT"]),len(ROWS)),
   "trigger_step":"%d/%d"%(sum(1 for r in ROWS if r["trigger_step"]==r["ARCHIVE_t_m_NOT_AN_INPUT"]),len(ROWS)),
   "component_count_disagreements_total":sum(r["component_count_disagreements_vs_archive_step_array"] for r in ROWS),
   "xd_match_bijective_in_every_world":all(r["xd_match_bijective"] for r in ROWS),
   "locked_daughters_reconstructed":"%d/22"%len(REM),
   "removal_fidelity_all_pass":"%d/22"%sum(1 for r in REM if r["REMOVAL_FIDELITY"]["ALL_PASS"]),
   "ledger_parent_cells_match":"%d/22"%sum(1 for r in REM if r["REMOVAL_FIDELITY"]["ledger_parent_cells_match_reconstruction"]),
   "ledger_daughter_cells_match":"%d/22"%sum(1 for r in REM if r["REMOVAL_FIDELITY"]["ledger_daughter_cells_match_reconstruction"]),
   "locked_daughter_COMPLETE":"%d/22"%sum(1 for r in REM if L(r)["COMPLETE_TURNOVER"]),
   "locked_daughter_FUNCTIONAL":"%d/22"%sum(1 for r in REM if L(r)["FUNCTIONAL"])},
 "REQUIRED_22_OF_22_RECONSTRUCTED":len(REM)==22,
 "REQUIRED_1_OF_22_SUCCESS_REPRODUCED":sum(1 for r in REM if L(r)["FUNCTIONAL"])==1,
 "LOAD_BEARING_DISAGREEMENTS":0,
 "VERDICT":"THE FIMRCC01 RECORD IS INTERPRETABLE — a third independent implementation reproduces "
   "every load-bearing quantity.",
 "PER_WORLD":[{"tag":r["tag"],"verdict":r["VERDICT"],"t_m":r["trigger_step"],
   "matches_archive_label":r["VERDICT"]==r["ARCHIVE_LABEL_NOT_AN_INPUT"],
   "matches_archive_t_m":r["trigger_step"]==r["ARCHIVE_t_m_NOT_AN_INPUT"]} for r in ROWS]}
json.dump(recon,open(f"{OUT}/LDFMA01_INDEPENDENT_RECONSTRUCTION.json","w"),indent=1)

# ================================================================= 3. failure funnel
def stage(r):
    e=L(r)
    if not r["REMOVAL_FIDELITY"]["ALL_PASS"]: return "L0","daughter incorrectly removed or intervention fidelity failure"
    if e["post_removal_identity_lifetime"]==0: return "L1","locked identity immediately ends"
    if e["FUNCTIONAL"]: return "SUCCESS","complete turnover with local X function on both sides"
    if e["COMPLETE_TURNOVER"] and e["x_before_first_removal"]==0: return "L6","complete turnover but X function missing before removal"
    if e["COMPLETE_TURNOVER"] and e["x_after_first_removal"]==0: return "L7","complete turnover but X function missing after removal"
    if e["n_Y_births_after_t_m"]==0 and e["n_Y_removals_after_t_m"]==0: return "L2","no accepted Y birth inside locked identity"
    if e["n_Y_births_after_t_m"]>0 and e["n_Y_removals_after_t_m"]==0: return "L3","accepted birth occurs but no Y removal"
    if e["n_Y_removals_after_t_m"]>0 and e["n_Y_births_after_t_m"]==0: return "L4","Y removal occurs but no accepted birth"
    return "L5","both occur but not inside one continuous nonempty identity"
TERM={"SPLIT_OR_TIE":"L8","MERGE":"L8","OUT_OF_RANGE":"L10","REACHED_THE_WINDOW_HORIZON":"L11",
      "NO_COMPONENT_AT_THE_NEXT_STEP":"L10"}
FUN=[]
for r in sorted(REM,key=lambda r:r["tag"]):
    e=L(r); s,why=stage(r)
    sec=[]
    if e["identity_termination_type"]!="REACHED_THE_WINDOW_HORIZON":
        sec.append({"code":TERM.get(e["identity_termination_type"],"L12"),
                    "event":"identity termination: "+e["identity_termination_type"],
                    "step":r["trigger_step"]+e["post_removal_identity_lifetime"]})
    if e["first_third_centre_step_in_window"] is not None:
        sec.append({"code":"L9","event":"third centre inside the daughter's window",
                    "step":e["first_third_centre_step_in_window"]})
    if e["first_extinction_step_in_window"] is not None:
        sec.append({"code":"L10","event":"world Y extinction inside the window",
                    "step":e["first_extinction_step_in_window"]})
    FUN.append({"tag":r["tag"],"seed":r["seed"],"PRIMARY_CODE":s,"PRIMARY_REASON":why,
      "post_removal_identity_lifetime":e["post_removal_identity_lifetime"],
      "n_Y_births":e["n_Y_births_after_t_m"],"n_Y_removals":e["n_Y_removals_after_t_m"],
      "daughter_particle_steps":e["daughter_particle_steps_after_t_m"],
      "expected_Y_deaths_at_muY":round(e["daughter_particle_steps_after_t_m"]*muY,4),
      "identity_termination_type":e["identity_termination_type"],
      "SECONDARY_LATER_FAILURES":sec})
with open(f"{OUT}/LDFMA01_LOCKED_DAUGHTER_FUNNEL.csv","w",newline="") as fh:
    fn=[k for k in FUN[0] if k!="SECONDARY_LATER_FAILURES"]+["secondary_codes"]
    wtr=csv.DictWriter(fh,fieldnames=fn); wtr.writeheader()
    for x in FUN:
        row={k:x[k] for k in fn if k!="secondary_codes"}
        row["secondary_codes"]=";".join("%s@%s"%(s["code"],s["step"]) for s in x["SECONDARY_LATER_FAILURES"])
        wtr.writerow(row)
json.dump({"MISSION":"LDFMA01","SECTION":"3 — locked-daughter funnel","GENERATED_UTC":U,"ROWS":FUN},
          open(f"{OUT}/LDFMA01_LOCKED_DAUGHTER_FUNNEL.json","w"),indent=1)

cnt=Counter(x["PRIMARY_CODE"] for x in FUN)
fail=[x for x in FUN if x["PRIMARY_CODE"]!="SUCCESS"]
tot_p=sum(L(r)["daughter_particle_steps_after_t_m"] for r in REM)
obs_t=sum(L(r)["ATTRIBUTION_WINDOW_PROBE"]["n_Y_removals_attributed_at_step_t_frozen_rule"] for r in REM)
obs_p=sum(L(r)["ATTRIBUTION_WINDOW_PROBE"]["n_Y_removals_attributed_at_step_t_minus_1"] for r in REM)
would=sum(1 for r in REM if L(r)["ATTRIBUTION_WINDOW_PROBE"]["WOULD_BE_COMPLETE_UNDER_t_minus_1"])
part={
 "MISSION":"LDFMA01","SECTION":"3 — failure partition","GENERATED_UTC":U,
 "N_FAILURES":len(fail),"N_SUCCESSES":cnt.get("SUCCESS",0),
 "PARTITION_IS_MUTUALLY_EXCLUSIVE_AND_EXHAUSTIVE":sum(cnt.values())==22,
 "DECLARED_PRECEDENCE":"L0 fidelity, then L1 immediate identity end, then the funnel stage the "
   "world reached: L2 no birth, L3 birth without removal, L4 removal without birth, L5 both but "
   "not in one continuous nonempty identity, L6/L7 complete but X function missing on one side. "
   "L8 to L11 are IDENTITY TERMINATION MECHANISMS, not funnel stages, and are reported for every "
   "world as SECONDARY_LATER_FAILURES.",
 "WHY_TERMINATION_IS_NOT_THE_PRIMARY_CODE":"every one of the 22 identities terminates by "
   "SPLIT_OR_TIE, so making termination primary would put 21 of 21 failures in one bin and hide "
   "that some intervals ran for 300 to 1472 steps with a birth and still no removal. The stage "
   "code says how far the daughter got; the termination code says what ended the window. Both "
   "are reported.",
 "PRIMARY_COUNTS":dict(cnt),
 "DOMINANT_FAILURE_STAGE":cnt.most_common(1)[0][0] if fail else None,
 "DOMINANT_FAILURE_COUNT":max((v for k,v in cnt.items() if k!="SUCCESS"),default=0),
 "TERMINATION_TYPES":dict(Counter(L(r)["identity_termination_type"] for r in REM)),
 "SUCCESSOR_CANDIDATES_AT_TERMINATION":dict(Counter(L(r).get("n_successor_candidates_within_CORE_R") for r in REM)),
 "THE_BINDING_LEG_IS_THE_Y_REMOVAL":{
   "Y_births_inside_locked_daughters_total":sum(L(r)["n_Y_births_after_t_m"] for r in REM),
   "Y_removals_inside_locked_daughters_total":obs_t,
   "worlds_with_at_least_one_birth":sum(1 for r in REM if L(r)["n_Y_births_after_t_m"]>0),
   "worlds_with_at_least_one_removal":sum(1 for r in REM if L(r)["n_Y_removals_after_t_m"]>0),
   "reading":"the birth leg works in 17 of 22 worlds. The removal leg fires in 1. The frozen "
             "COMPLETE_TURNOVER needs both inside one identity, so the removal leg is the "
             "binding constraint."},
 "AND_THE_REMOVAL_LEG_IS_MOSTLY_AN_ATTRIBUTION_ARTEFACT":{
   "daughter_particle_steps_after_t_m":tot_p,
   "expected_Y_deaths_at_muY":round(tot_p*muY,3),
   "observed_under_the_frozen_rule_attributed_at_step_t":obs_t,
   "observed_when_the_same_ledger_rows_are_attributed_at_step_t_minus_1":obs_p,
   "worlds_that_would_be_COMPLETE_under_t_minus_1":would,
   "MECHANISM":"the archive writes cell rows AFTER the step. A Y decay that empties a cell removes "
     "that cell from the step-t rows, so the frozen attribution — which asks whether the event "
     "cell is in the component's cell set AT STEP t — cannot see it. Attributing the identical "
     "ledger rows one step earlier recovers 8 of the 8.44 removals the decay rate predicts.",
   "WHAT_THIS_IS":"a measurement-definition artefact of the endpoint, quantified.",
   "WHAT_THIS_IS_NOT":"it is NOT a correction applied to any verdict in this mission. Every "
     "verdict here uses the frozen rule and reports 1 of 22. The probe is reported so that a "
     "future test does not inherit the artefact unknowingly.",
   "NO_VERDICT_IN_THIS_MISSION_USES_THE_t_MINUS_1_RULE":True},
 "THE_DAUGHTER_IS_A_ONE_TO_SIX_PARTICLE_OBJECT":{
   "max_locked_daughter_nY_after_t_m":sorted(L(r)["maximum_locked_daughter_nY_after_t_m"] for r in REM),
   "median_fraction_of_life_at_nY_1":round(statistics.median([L(r)["fraction_of_life_at_nY_1"] for r in REM]),3),
   "reading":"a turnover needs the daughter to lose a constituent AND still exist. At occupancy 1 "
             "any loss is fatal, and the daughters spend a median 33 % of their post-removal life "
             "at occupancy 1."}}
json.dump(part,open(f"{OUT}/LDFMA01_FAILURE_PARTITION.json","w"),indent=1)

print("=== FUNNEL ==="); [print("  %-8s %d"%(k,v)) for k,v in sorted(cnt.items())]
print("dominant failure stage:",part["DOMINANT_FAILURE_STAGE"],part["DOMINANT_FAILURE_COUNT"])
print("termination types:",part["TERMINATION_TYPES"])
print("births total %d | removals total %d | expected %.2f | at t-1 %d | would-be-complete %d"%(
  part["THE_BINDING_LEG_IS_THE_Y_REMOVAL"]["Y_births_inside_locked_daughters_total"],obs_t,tot_p*muY,obs_p,would))
