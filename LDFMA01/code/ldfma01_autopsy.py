"""LDFMA01 sections 4 and 5 — the single-success autopsy against the pre-registered families, and
the ambient saturation mechanism. No significance test is run anywhere in this file."""
from __future__ import annotations
import json,glob,hashlib,datetime,statistics,math
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
REG_P=f"{OUT}/LDFMA01_SUCCESS_COMPARISON_PREREGISTRATION.json"
REG=json.load(open(REG_P)); REG_SHA=sha(REG_P)
ROWS=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
REM=[r for r in ROWS if r.get("E_locked_daughter_interval")]
SRC={"A":"A_trigger_time","B":"B_daughter_geometry","C":"C_local_environment","D":"D_parent",
     "E":"E_locked_daughter_interval","F":"F_ambient","G":"G_competing"}
BEFORE=set(REG["AVAILABLE_BEFORE_OUTCOME"]["families_available_before_outcome"])
succ=[r for r in REM if r["E_locked_daughter_interval"]["FUNCTIONAL"]][0]
fail=[r for r in REM if not r["E_locked_daughter_interval"]["FUNCTIONAL"]]
MECH={
 "post_removal_identity_lifetime":"longer identity window = more exposure for both legs",
 "maximum_locked_daughter_nY_after_t_m":"a daughter that reaches occupancy 2 or more can lose a "
   "constituent and still exist; at occupancy 1 any loss is fatal",
 "daughter_nY":"same, measured at the trigger",
 "n_Y_births_after_t_m":"the birth leg of the turnover",
 "n_Y_removals_after_t_m":"the removal leg of the turnover",
 "fraction_of_life_at_nY_1":"time spent where a loss is fatal rather than a turnover",
 "n_X_births_after_t_m":"the local X production the FUNCTIONAL qualification requires",
 "parent_daughter_centroid_distance":"separation geometry at the trigger",
 "daughter_xd":"local X mass available to the daughter at the trigger",
 "world_nY_at_t_m":"how much of the world is not the parent and the daughter"}
def num(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool)
FEAT=[]
for fam in REG["COMPARISON_FAMILIES"]:
    key=SRC[fam["family"]]
    for name in fam["features"]:
        sv=succ.get(key,{}).get(name)
        fv=[r.get(key,{}).get(name) for r in fail]
        fvn=[v for v in fv if num(v)]
        if not num(sv) or len(fvn)<len(fv)//2:
            FEAT.append({"family":fam["family"],"feature":name,"success_value":sv,
                         "failure_values":fv,"COMPARABLE":False,
                         "available_before_outcome":fam["family"] in BEFORE}); continue
        allv=sorted(fvn+[sv])
        rank=allv.index(sv)+1
        uniq=(sv<min(fvn)) or (sv>max(fvn))
        q=statistics.quantiles(fvn,n=4) if len(fvn)>=4 else [min(fvn),statistics.median(fvn),max(fvn)]
        inside_iqr=q[0]<=sv<=q[2]
        FEAT.append({"family":fam["family"],"feature":name,"COMPARABLE":True,
          "success_value":sv,
          "failure_min":min(fvn),"failure_q25":q[0],"failure_median":statistics.median(fvn),
          "failure_q75":q[2],"failure_max":max(fvn),"failure_n":len(fvn),
          "rank_of_the_success_among_22":rank,
          "UNIQUE_outside_the_failure_range":bool(uniq),
          "inside_the_failure_interquartile_span":bool(inside_iqr),
          "executable_mechanistic_interpretation":MECH.get(name),
          "has_an_executable_mechanistic_interpretation":name in MECH,
          "available_before_outcome":fam["family"] in BEFORE})
uniq=[f for f in FEAT if f.get("UNIQUE_outside_the_failure_range")]
uniq_before=[f for f in uniq if f["available_before_outcome"]]
falsified=[]
for f in FEAT:
    if f.get("COMPARABLE") and f.get("has_an_executable_mechanistic_interpretation") and f.get("inside_the_failure_interquartile_span"):
        falsified.append({"feature":f["feature"],"family":f["family"],
          "mechanism_falsified":"any mechanism requiring %s to be extreme for the locked daughter "
            "to complete a turnover"%f["feature"],
          "success_value":f["success_value"],"failure_q25":f["failure_q25"],"failure_q75":f["failure_q75"]})
aut={
 "MISSION":"LDFMA01","SECTION":"4 — single-success autopsy","GENERATED_UTC":U,
 "PREREGISTRATION":"LDFMA01_SUCCESS_COMPARISON_PREREGISTRATION.json","PREREGISTRATION_SHA256":REG_SHA,
 "HONEST_LIMIT":REG["AN_HONEST_LIMIT_ON_THIS_PRE_REGISTRATION"],
 "N_SUCCESSES":1,"N_FAILURES":len(fail),
 "NO_SIGNIFICANCE_TEST_WAS_RUN":True,
 "SUCCESS_WORLD":succ["tag"],
 "FEATURES":FEAT,
 "UNIQUE_FEATURES":[{"family":f["family"],"feature":f["feature"],"success":f["success_value"],
    "failure_range":[f["failure_min"],f["failure_max"]],
    "available_before_outcome":f["available_before_outcome"]} for f in uniq],
 "N_UNIQUE":len(uniq),
 "N_UNIQUE_AND_AVAILABLE_BEFORE_OUTCOME":len(uniq_before),
 "MECHANISMS_FALSIFIED_BY_THE_SUCCESS":falsified,
 "THE_ONE_THING_THAT_SEPARATES_THE_SUCCESS":
   "the success is the only world in which a Y removal was ATTRIBUTED to the locked daughter under "
   "the frozen rule. Every other measured quantity about it — lifetime, occupancy, local X, parent "
   "distance, ambient pressure — sits inside the failure distribution.",
 "WHAT_THIS_MEANS_FOR_A_PROSPECTIVE_DESIGN":
   "no available-before-outcome feature separates the success from the failures, so there is no "
   "prospective eligibility criterion that could enrich a future experiment for locked-daughter "
   "turnover. A design that hoped to select promising worlds in advance has nothing to select on.",
 "N_1_IS_NOT_A_POPULATION_LAW":"this autopsy can falsify mechanisms and name necessary conditions. "
   "It cannot estimate any rate, and no rate is estimated here.",
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED"}
json.dump(aut,open(f"{OUT}/LDFMA01_SINGLE_SUCCESS_AUTOPSY.json","w"),indent=1)

# ================================================================= 5. ambient saturation
muY=0.000740894982503035
starts=[];rel=[];life=[];afterend=0;tot=0
per=[]
for r in REM:
    t=r["trigger_step"]; e=r["E_locked_daughter_interval"]; f=r["F_ambient"]
    dend=t+e["post_removal_identity_lifetime"]
    ss=f["complete_interval_start_steps"]; starts+=ss; rel+=[s-t for s in ss]; tot+=len(ss)
    afterend+=sum(1 for s in ss if s>dend)
    life+=f["interval_lifetimes_after_t_m"]
    per.append({"tag":r["tag"],"n_intervals_after_t_m":f["n_identity_intervals_live_after_t_m"],
      "n_complete":f["ambient_complete_interval_count"],"n_functional":f["ambient_functional_interval_count"],
      "per_interval_complete_rate":f["ambient_complete_interval_count"]/max(1,f["n_identity_intervals_live_after_t_m"]),
      "world_nY_at_t_m":f["world_nY_at_t_m"],
      "mean_world_nY_after_t_m":f["mean_world_nY_after_t_m"],
      "mean_centres_after_t_m":f["mean_centres_after_t_m"],"max_centres_after_t_m":f["max_centres_after_t_m"],
      "first_step_with_world_nY_ge_20":f["first_step_after_t_m_with_world_nY_ge_20"],
      "lag_from_t_m_to_nY_ge_20":(f["first_step_after_t_m_with_world_nY_ge_20"]-t) if f["first_step_after_t_m_with_world_nY_ge_20"] is not None else None,
      "daughter_identity_end_step":dend})
rates=[p["per_interval_complete_rate"] for p in per]
nints=[p["n_intervals_after_t_m"] for p in per]
pbar=sum(p["n_complete"] for p in per)/sum(nints)
pred=[1-(1-pbar)**n for n in nints]
amb={
 "MISSION":"LDFMA01","SECTION":"5 — ambient saturation mechanism","GENERATED_UTC":U,
 "THE_QUESTION":"why does an endpoint asking whether ANY identity anywhere completed a turnover "
   "after the removal return 22 of 22, when the locked daughter returns 1 of 22?",
 "MEASURED":{
  "n_identity_intervals_live_after_t_m":{"min":min(nints),"median":statistics.median(nints),
     "max":max(nints),"total":sum(nints)},
  "identity_lifetime_after_t_m":{"min":min(life),"median":statistics.median(life),
     "max":max(life),"mean":round(statistics.mean(life),2),"n":len(life)},
  "complete_turnover_rate_PER_IDENTITY":{"pooled":round(pbar,6),
     "per_world_min":round(min(rates),6),"per_world_median":round(statistics.median(rates),6),
     "per_world_max":round(max(rates),6)},
  "simultaneously_occupied_centres_after_t_m":{
     "mean_of_per_world_means":round(statistics.mean([p["mean_centres_after_t_m"] for p in per]),3),
     "max_observed":max(p["max_centres_after_t_m"] for p in per)},
  "world_nY_at_the_trigger":{"values":sorted(p["world_nY_at_t_m"] for p in per),
     "max":max(p["world_nY_at_t_m"] for p in per),
     "reading":"at the trigger the whole world holds between 2 and 5 Y particles. The parent and "
               "the daughter ARE the world; there is no ambient population yet."},
  "lag_from_t_m_to_world_nY_at_least_20":{
     "min":min(p["lag_from_t_m_to_nY_ge_20"] for p in per),
     "median":statistics.median([p["lag_from_t_m_to_nY_ge_20"] for p in per]),
     "max":max(p["lag_from_t_m_to_nY_ge_20"] for p in per)}},
 "REPEATED_OPPORTUNITY_TEST":{
   "model":"1 - (1 - p_bar)^n, with p_bar the pooled per-identity complete-turnover rate and n the "
           "number of identity intervals live after t_m in that world",
   "p_bar":round(pbar,6),
   "predicted_world_level_success_probability":{"min":round(min(pred),6),
      "median":round(statistics.median(pred),6),"max":round(max(pred),6)},
   "n_worlds_with_predicted_probability_above_0_99":sum(1 for x in pred if x>0.99),
   "observed_world_level_success":"22/22",
   "CONCLUSION":"the unrestricted endpoint is saturated because each world offers hundreds to "
     "thousands of successive identity intervals at a modest per-interval rate. It is a "
     "repeated-opportunity effect, not a world-level daughter mechanism."},
 "THE_DECISIVE_TIMING_FACT":{
   "n_ambient_complete_intervals":tot,
   "start_step_quartiles":[min(starts),round(statistics.quantiles(starts,n=4)[0]),
       round(statistics.median(starts)),round(statistics.quantiles(starts,n=4)[2]),max(starts)],
   "steps_after_t_m":{"min":min(rel),"median":statistics.median(rel),"max":max(rel)},
   "median_daughter_identity_lifetime_after_t_m":statistics.median(
       [r["E_locked_daughter_interval"]["post_removal_identity_lifetime"] for r in REM]),
   "ambient_complete_intervals_that_START_AFTER_the_daughter_identity_has_already_ended":afterend,
   "as_a_fraction":round(afterend/tot,6),
   "READING":"the ambient turnovers do not compete with the daughter, they SUCCEED it. Essentially "
     "every one of them begins after the locked identity is already gone, in a population that "
     "did not exist at the removal."},
 "IDENTITIES_WITHIN_A_WORLD_ARE_NOT_INDEPENDENT_REPLICATES":
   "they share one trajectory, one lattice and one realised history, and they are largely "
   "successive rather than concurrent. No per-identity rate in this artefact is treated as an "
   "independent experimental replicate, and no confidence interval is placed on one.",
 "WHAT_THIS_DOES_NOT_SAY":"it does not say TLMR01's 22/22 is wrong. It says what object the "
   "22/22 measures: a late-time population, not the daughter the removal was applied to.",
 "PER_WORLD":per}
json.dump(amb,open(f"{OUT}/LDFMA01_AMBIENT_SATURATION_MECHANISM.json","w"),indent=1)
print("UNIQUE features:",len(uniq),"| unique AND available-before-outcome:",len(uniq_before))
for f in uniq: print("   %-4s %-42s success=%s failures=[%s,%s] before=%s"%(f["family"],f["feature"],f["success_value"],f["failure_min"],f["failure_max"],f["available_before_outcome"]))
print()
print("p_bar per identity = %.6f | predicted world success min %.4f med %.4f"%(pbar,min(pred),statistics.median(pred)))
print("ambient complete intervals starting AFTER the daughter is gone: %d/%d"%(afterend,tot))
print("mechanisms falsified by the success:",len(falsified))
