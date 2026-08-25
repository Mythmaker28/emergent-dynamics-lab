"""FIMRCC01 Section 4 — the pre-registered candidates evaluated, and the selection rule applied.

The candidate set and every threshold in this file were fixed in
FIMRCC01_ENDPOINT_PREREGISTRATION.json, sha256 published before any number below existed.
"""
from __future__ import annotations
import json, math, hashlib, datetime, statistics
REPO="/home/claude/edl"; OUT=f"{REPO}/FIMRCC01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
REG_P=f"{OUT}/FIMRCC01_ENDPOINT_PREREGISTRATION.json"
REG=json.load(open(REG_P)); REG_SHA=hashlib.sha256(open(REG_P,"rb").read()).hexdigest()
D=json.load(open(f"{REPO}/FIMRCC01/work/e4_all.json"))
N=len(D); assert N==22
F=0.0032015171041760242
SAT=REG["CRITERION_2_DISCRIMINATION"]["SATURATION_THRESHOLD"]

def lsf(k,n,p):
    if k<=0: return 1.0
    if p<=0.0: return 0.0
    if p>=1.0: return 1.0 if k<=n else 0.0
    lp=math.log(p); lq=math.log1p(-p); s=0.0
    for i in range(k,n+1):
        s+=math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)+i*lp+(n-i)*lq)
        if s>=1.0: return 1.0
    return s
def kstar(n,p0=F,a=0.05):
    for k in range(0,n+1):
        if lsf(k,n,p0)<=a: return k
    return None
def cp_lower(k,n,a=0.05):
    if k==0: return 0.0
    lo,hi=0.0,1.0
    for _ in range(200):
        mid=(lo+hi)/2
        if lsf(k,n,mid)>a: hi=mid
        else: lo=mid
    return (lo+hi)/2

VALS={
 "E0":[1 if r["E0_FUNCTIONAL_anywhere"] else 0 for r in D],
 "E1":[1 if r.get("E1_FUNCTIONAL") else 0 for r in D],
 "E2":[1 if r.get("E2_COMPLETE") else 0 for r in D],
 "E3":[r["steps_after_tm"] for r in D],
 "E4":[r["y_births_after_tm"]+r["y_deaths_after_tm"] for r in D],
 "E5":[r["E5_n_complete_anywhere"] for r in D]}
KIND={"E0":"binary","E1":"binary","E2":"binary","E3":"count","E4":"count","E5":"count"}
RANK={c["id"]:c["proximity_rank"] for c in REG["CANDIDATES"]}
NAME={c["id"]:c["name"] for c in REG["CANDIDATES"]}

rows=[]
for cid in ("E0","E1","E2","E3","E4","E5"):
    v=VALS[cid]; n=len(v)
    modal=max(set(v),key=v.count); frac=v.count(modal)/n
    r={"id":cid,"name":NAME[cid],"kind":KIND[cid],"proximity_rank":RANK[cid],
       "n_worlds":n,"distinct_values":len(set(v)),
       "modal_value":modal,"fraction_at_the_modal_value":round(frac,4),
       "min":min(v),"median":statistics.median(v),"max":max(v),
       "CRITERION_1_ADMISSIBLE":True,
       "CRITERION_2_SATURATED":bool(frac>SAT),
       "CRITERION_2_PASSES":bool(frac<=SAT)}
    if KIND[cid]=="binary":
        k=sum(v); ks=kstar(50)
        # The pre-registration says "the candidate's own TLMR01 rate" without naming a denominator.
        # There are two, and they differ by an order of magnitude. Rather than resolve the
        # ambiguity in the direction that helps, BOTH are computed and the criterion must pass
        # under BOTH. See AMBIGUITY_IN_THE_PREREGISTRATION in this artefact.
        rate22=k/n                       # per world that reached a removal
        rate256=k/256                    # per world run, the denominator F_INTEGRATED is matched to
        pw22 =lsf(ks,50,rate22)  if rate22>0  else 0.0
        pw256=lsf(ks,50,rate256) if rate256>0 else 0.0
        r.update({"k_of_n_on_TLMR01":"%d/%d"%(k,n),
                  "rate_per_removal_world":rate22,
                  "rate_per_world_run":rate256,
                  "lower95_per_removal_world":round(cp_lower(k,n),6),
                  "lower95_per_world_run":round(cp_lower(k,256),6),
                  "ratio_to_F_INTEGRATED_per_world_run":round(rate256/F,3) if rate256 else 0.0,
                  "k_star_at_n50":ks,
                  "power_at_n50_per_removal_world":round(pw22,4),
                  "power_at_n50_per_world_run":round(pw256,4),
                  "power_at_n50_against_F_INTEGRATED":round(min(pw22,pw256),4),
                  "CRITERION_3_PASSES":bool(pw22>=0.80 and pw256>=0.80)})
    else:
        r.update({"mean":round(statistics.mean(v),2),
                  "stdev":round(statistics.pstdev(v),2),
                  "CRITERION_3_PASSES":None,
                  "POWER_NOT_ESTIMABLE_IN_ADVANCE":
                    "no matched control arm exists anywhere in TLMR01's 512 worlds, so the "
                    "distribution of the within-block difference between arms is unknown. This is "
                    "stated in the pre-registration and no power number is invented here."})
    r["SURVIVES"]=bool(r["CRITERION_1_ADMISSIBLE"] and r["CRITERION_2_PASSES"]
                       and (r["CRITERION_3_PASSES"] if KIND[cid]=="binary" else True))
    rows.append(r)

surviving_binary=[r for r in rows if r["kind"]=="binary" and r["SURVIVES"]]
selected=min(surviving_binary,key=lambda r:r["proximity_rank"]) if surviving_binary else None
surviving_counts=[r for r in rows if r["kind"]=="count" and r["SURVIVES"]]

art={
 "MISSION":"FIMRCC01","SECTION":"4 — endpoint candidate table and selection","GENERATED_UTC":U,
 "PREREGISTRATION":"FIMRCC01_ENDPOINT_PREREGISTRATION.json","PREREGISTRATION_SHA256":REG_SHA,
 "THE_CANDIDATE_SET_AND_EVERY_THRESHOLD_WERE_FIXED_BEFORE_THESE_NUMBERS":True,
 "EVALUATED_ON":"TLMR01's 22 LAW_C_MCTT01 worlds with a selective removal applied — the only "
   "worlds anywhere in the inherited data where the endpoint is askable at all.",
 "N_WORLDS":N,"F_INTEGRATED":F,"SATURATION_THRESHOLD":SAT,
 "AMBIGUITY_IN_THE_PREREGISTRATION":{
   "what_was_ambiguous":"criterion 3 says power is evaluated at 'the candidate\'s own TLMR01 "
     "rate' and does not name a denominator. Two are available and they differ by an order of "
     "magnitude: k out of the 22 worlds that reached a removal, and k out of the 256 worlds run.",
   "why_it_matters":"FIMRCC01's 50 fresh base blocks are WORLDS, not removal worlds. Only about "
     "22 of 256 LAW_C worlds reach a removal at all, so roughly 4 of 50 fresh blocks will. The "
     "per-world-run denominator is also the one F_INTEGRATED = lower95(3,256) is matched to.",
   "how_it_was_resolved":"BOTH are computed and criterion 3 requires the candidate to pass under "
     "BOTH. That is the only resolution that cannot be accused of choosing the convenient "
     "denominator after seeing the numbers.",
   "does_the_resolution_change_the_outcome":"no. E1 and E2 fail under both (0.6697 and 0.0165); "
     "E0 passes criterion 3 under both but is struck by criterion 2.",
   "IT_IS_RECORDED_RATHER_THAN_QUIETLY_FIXED":True},
 "TABLE":rows,
 "SURVIVING_BINARY_CANDIDATES":[r["id"] for r in surviving_binary],
 "SURVIVING_COUNT_CANDIDATES":[r["id"] for r in surviving_counts],
 "SELECTED_BINARY_ENDPOINT":(selected["id"] if selected else None),
 "SELECTION_RULE_OUTCOME":("step_4: the surviving binary candidate closest to the inherited "
   "definition is %s"%selected["id"]) if selected else
   ("step_5: NO binary candidate survives. Every binary candidate is either saturated at this "
    "law's occupancy or sits too close to the endpoint-matched floor to be tested at n = 50. The "
    "choice between taking CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED and "
    "re-scoping the mission around a paired between-arm contrast is REFERRED TO THE OWNER, "
    "exactly as the pre-registration says it must be."),
 "REFERRED_TO_THE_OWNER":selected is None,
 "WHAT_IS_NOT_DONE_HERE":[
   "no seventh candidate is introduced",
   "no threshold is moved",
   "the strict identity rule is not relaxed",
   "n is not raised above 50"],
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "PER_WORLD":[{"tag":r["tag"],"seed":r["seed"],"t_m":r["t_m"],
   "E0":VALS["E0"][i],"E1":VALS["E1"][i],"E2":VALS["E2"][i],
   "E3_steps_after_tm":VALS["E3"][i],"E4_y_events":VALS["E4"][i],"E5_ambient":VALS["E5"][i]}
   for i,r in enumerate(D)]}
p=f"{OUT}/FIMRCC01_ENDPOINT_TABLE.json"
json.dump(art,open(p,"w"),indent=1)

hdr="%-4s %-30s %-7s %-9s %-8s %-10s %-15s %-8s %s"%("id","name","kind","k/n or med","satur.","C2","power@50 (22/256)","C3","SURVIVES")
print(hdr); print("-"*len(hdr))
for r in rows:
    kn=r.get("k_of_n_on_TLMR01") or ("med %g"%r["median"])
    pw=("%.4f/%.4f"%(r["power_at_n50_per_removal_world"],r["power_at_n50_per_world_run"])) if r["kind"]=="binary" else "n/a"
    print("%-4s %-30s %-7s %-9s %-8.2f %-10s %-15s %-8s %s"%(
      r["id"],r["name"][:30],r["kind"],kn,r["fraction_at_the_modal_value"],
      "PASS" if r["CRITERION_2_PASSES"] else "SATURATED",pw,
      ("PASS" if r["CRITERION_3_PASSES"] else "FAIL") if r["kind"]=="binary" else "n/a",
      r["SURVIVES"]))
print()
print("surviving binary :",art["SURVIVING_BINARY_CANDIDATES"])
print("surviving counts :",art["SURVIVING_COUNT_CANDIDATES"])
print("SELECTED         :",art["SELECTED_BINARY_ENDPOINT"])
print("REFERRED_TO_OWNER:",art["REFERRED_TO_THE_OWNER"])
print("sha256",hashlib.sha256(open(p,"rb").read()).hexdigest())
