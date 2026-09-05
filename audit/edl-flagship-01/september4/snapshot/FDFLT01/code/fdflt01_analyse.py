"""FDFLT01 §13 + §14 — frozen confirmatory analysis. Written and hashed BEFORE the first run."""
from __future__ import annotations
import csv, glob, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fdflt01_endpoint as E
import fdflt01_score_B as B
import fdflt01_power as PW

REPO="/home/claude/edl"; RAW="/home/claude/FDFLT01/raw"; OUT=f"{REPO}/FDFLT01/out"
KEYS=list(E.STEPS.keys())

def load_primary_paths():
    seeds=json.load(open(f"{OUT}/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]["PRIMARY"]
    paths=[]
    for r in seeds:
        p=os.path.join(RAW,"F_B1_i%03d_s%d.npz"%(r["index"],r["seed"]))
        paths.append((r["index"],r["seed"],p,os.path.exists(p)))
    return paths

def main():
    paths=load_primary_paths()
    missing=[(i,s) for i,s,p,ok in paths if not ok]
    A=[E.score_world(p) for _,_,p,ok in paths if ok]
    Bs={r["world"]:r for r in (B.score_world(p) for _,_,p,ok in paths if ok)}
    # ---- dual-implementation agreement on every load-bearing field ----
    req=["first_S","first_P","extinct","n_births","integrity_ok","n_S_episodes","max_S_duration"]
    for k in KEYS:
        req+=[f"dur_ok_{k}",f"noP_ok_{k}",f"resp_ok_{k}",f"event_step_{k}",
              f"P_before_event_{k}",f"joint_timing_{k}",f"PRIMARY_SUCCESS_{k}"]
    dis=[{"world":r["world"],"field":f,"A":r.get(f),"B":Bs[r["world"]].get(f)}
         for r in A for f in req if r.get(f)!=Bs[r["world"]].get(f)]
    rat=[{"world":r["world"],"key":k} for r in A for k in KEYS
         if (r[f"weak_centre_X_ratio_{k}"] is None)!=(Bs[r["world"]][f"weak_centre_X_ratio_{k}"] is None)
         or (r[f"weak_centre_X_ratio_{k}"] is not None
             and abs(r[f"weak_centre_X_ratio_{k}"]-Bs[r["world"]][f"weak_centre_X_ratio_{k}"])>1e-12)]

    n=len(A); X=sum(r["PRIMARY_SUCCESS"] for r in A)
    C=PW.critical(); lo1=PW.cp(X,PW.N,0.95,True); lo2,hi2=PW.cp(X,PW.N)
    from scipy.stats import binom
    pval=float(binom.sf(X-1,PW.N,PW.P0))
    PRIM={"SECTION":"FDFLT01 §13 — primary confirmatory analysis",
     "PRIMARY_N_PLANNED":PW.N,"PRIMARY_N_SCORED":n,"ALL_PLANNED_WORLDS_PRESENT":bool(n==PW.N and not missing),
     "MISSING":missing,
     "PRIMARY_NULL_RATE":PW.P0,"PRIMARY_ALPHA":PW.ALPHA,
     "PRIMARY_CRITICAL_SUCCESS_COUNT":C,
     "PRIMARY_SUCCESS_COUNT":X,"PRIMARY_SUCCESS_RATE":X/PW.N,
     "PRIMARY_ONE_SIDED_LOWER_95":lo1,
     "PRIMARY_TWO_SIDED_95":[lo2,hi2],
     "PRIMARY_EXACT_P_VALUE":pval,
     "REJECT_H0":bool(X>=C),
     "LOWER_BOUND_EXCEEDS_NULL":bool(lo1>PW.P0),
     "DECISION_RULES_AGREE":bool((X>=C)==(lo1>PW.P0)),
     "METHOD":"exact binomial; no normal approximation at any step",
     "DEVELOPMENTAL_WORLDS_POOLED":False,
     "DUAL_IMPLEMENTATION":{"n_disagreements":len(dis),"disagreements":dis[:40],
        "ratio_mismatches_beyond_1e_12":len(rat),"EXACT_AGREEMENT":bool(not dis)}}
    json.dump(PRIM,open(f"{OUT}/FDFLT01_PRIMARY_ANALYSIS.json","w"),indent=2)

    def rate(k_,n_): return {"count":int(k_),"n":int(n_),"rate":(k_/n_ if n_ else None),
                             "exact_95":list(PW.cp(k_,n_))}
    SEC={"SECTION":"FDFLT01 §14 — predeclared secondary outcomes; descriptive, they do not alter the primary decision",
     "first_birth":rate(sum(r["n_births"]>=1 for r in A),n),
     "lineage_non_extinction":rate(sum(not r["extinct"] for r in A),n),
     "geometric_two_centre_formation":rate(sum(r["first_S"]>=0 for r in A),n),
     "functional_maturation_timing_only":rate(sum(r[f"joint_timing_{E.PRIMARY_KEY}"] for r in A),n),
     "third_centre_before_function":rate(sum(1 for r in A if r.get(f"P_before_event_{E.PRIMARY_KEY}") is True),n),
     "X_source_integrity":rate(sum(r["integrity_ok"] for r in A),n),
     "reached_third_centre_at_any_time":rate(sum(r["first_P"]>=0 for r in A),n),
     "time_to_geometric_separation":None,"max_S_episode_duration":None,
     "second_over_first_centre_X_response":None,
     "stop_reasons":{},"newer_centre_is_weaker_concordance":None}
    seps=[r["first_S"]-r["first_birth"] for r in A if r["first_birth"]>=0 and r["first_S"]>r["first_birth"]]
    if seps: SEC["time_to_geometric_separation"]={"n":len(seps),"median":float(np.median(seps)),
        "mean":float(np.mean(seps)),"min":int(min(seps)),"max":int(max(seps))}
    ds=[r["max_S_duration"] for r in A if r["first_S"]>=0]
    if ds: SEC["max_S_episode_duration"]={"n":len(ds),"median":float(np.median(ds)),"max":int(max(ds))}
    rr=[r[f"weak_centre_X_ratio_{E.PRIMARY_KEY}"] for r in A if r[f"weak_centre_X_ratio_{E.PRIMARY_KEY}"] is not None]
    if rr: SEC["second_over_first_centre_X_response"]={"n":len(rr),"median":float(np.median(rr)),
        "mean":float(np.mean(rr)),"min":float(min(rr)),"max":float(max(rr)),
        "operator_predicted_fraction":E.F_PRIMARY}
    from collections import Counter
    SEC["stop_reasons"]=dict(Counter(r["stop"] for r in A))
    nw=[r[f"newer_centre_is_weaker_{E.PRIMARY_KEY}"] for r in A if r.get(f"newer_centre_is_weaker_{E.PRIMARY_KEY}") is not None]
    if nw: SEC["newer_centre_is_weaker_concordance"]={"n":len(nw),"fraction_true":float(np.mean(nw))}
    # component failure accounting
    F={"no_birth":sum(1 for r in A if r["n_births"]<1),
       "extinct":sum(1 for r in A if r["extinct"]),
       "no_geometric_two_centres":sum(1 for r in A if r["n_births"]>=1 and r["first_S"]<0),
       "duration_too_short":sum(1 for r in A if r["first_S"]>=0 and not r[f"dur_ok_{E.PRIMARY_KEY}"]),
       "third_centre_before_function":sum(1 for r in A if r[f"dur_ok_{E.PRIMARY_KEY}"] and not r[f"noP_ok_{E.PRIMARY_KEY}"]),
       "X_response_below_criterion":sum(1 for r in A if r[f"noP_ok_{E.PRIMARY_KEY}"] and not r[f"resp_ok_{E.PRIMARY_KEY}"]),
       "integrity_failure":sum(1 for r in A if not r["integrity_ok"])}
    SEC["FIRST_FAILING_COMPONENT_COUNTS"]=F
    SEC["FAILURE_ACCOUNTING_SUMS_TO_NON_SUCCESS"]=bool(sum(F.values())==n-X)
    json.dump(SEC,open(f"{OUT}/FDFLT01_SECONDARY_ANALYSIS.json","w"),indent=2)

    TS={"SECTION":"FDFLT01 §14 — timing sensitivity; descriptive only, the primary criterion is unchanged",
        "PRIMARY_KEY":E.PRIMARY_KEY,"STEPS":E.STEPS,"BAND":E.BAND,"FRACTIONS":E.FRACTIONS,"BY_FRACTION":{}}
    for k in KEYS:
        kx=sum(r[f"PRIMARY_SUCCESS_{k}"] for r in A)
        TS["BY_FRACTION"][k]={"success_count":kx,"rate":kx/PW.N,
            "exact_95":list(PW.cp(kx,PW.N)),"one_sided_lower_95":PW.cp(kx,PW.N,0.95,True),
            "would_reject_at_p0_0.10":bool(kx>=C)}
    json.dump(TS,open(f"{OUT}/FDFLT01_TIMING_SENSITIVITY.json","w"),indent=2)

    cols=list(A[0].keys()) if A else []
    with open(f"{OUT}/FDFLT01_WORLD_RESULTS.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore"); w.writeheader()
        for r in A: w.writerow(r)
    json.dump(A,open(f"{OUT}/FDFLT01_WORLD_RESULTS.json","w"),indent=1)
    print(json.dumps({k:PRIM[k] for k in ("PRIMARY_N_SCORED","PRIMARY_SUCCESS_COUNT","PRIMARY_SUCCESS_RATE",
        "PRIMARY_CRITICAL_SUCCESS_COUNT","PRIMARY_ONE_SIDED_LOWER_95","PRIMARY_EXACT_P_VALUE",
        "REJECT_H0","DECISION_RULES_AGREE")},indent=2))
    print("dual-impl disagreements:",len(dis),"| ratio mismatches:",len(rat))
    print("secondary:",json.dumps({k:(v["rate"] if isinstance(v,dict) and "rate" in v else v)
        for k,v in SEC.items() if k in ("first_birth","lineage_non_extinction","geometric_two_centre_formation",
        "third_centre_before_function","X_source_integrity")},indent=1))
    print("failure accounting:",F,"sums:",SEC["FAILURE_ACCOUNTING_SUMS_TO_NON_SUCCESS"])
    print("timing:",{k:TS["BY_FRACTION"][k]["success_count"] for k in KEYS})

if __name__=="__main__": main()
