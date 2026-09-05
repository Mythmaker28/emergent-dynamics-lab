"""FDOT01 §18-§19 — the frozen primary and secondary analyses. Frozen before the first world."""
from __future__ import annotations
import json, os, sys, csv, statistics, datetime, collections
import numpy as np
from scipy.stats import beta
REPO="/home/claude/edl"; OUT=f"{REPO}/FDOT01/out"; RAW="/home/claude/FDOT01/raw"
sys.path.insert(0,f"{REPO}/FDOT01/code")
import fdot01_centres as A
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
C=FZ["INHERITED_FROZEN_CONSTANTS"]; HOR=int(C["T_HORIZON"])
N_PRIMARY=160; THRESH=2
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def ci(k,n):
    return [0.0 if k==0 else float(beta.ppf(0.025,k,n-k+1)),1.0 if k==n else float(beta.ppf(0.975,k+1,n-k))]
def lo(k,n): return 0.0 if k==0 else float(beta.ppf(0.05,k,n-k+1))

def world(tag):
    z=np.load(os.path.join(RAW,tag+".npz"),allow_pickle=True)
    m=json.loads(str(z["meta"][0]))
    iv=A.analyse_world(z["ycells"],z["ybirth"],z["ydeath"],z["xbirth"],HOR)
    v=A.world_verdict(iv)
    sc=z["scalars"]; NY=sc[:,1]; ncells=sc[:,3]
    # centre count per step, from ycells, for the third-centre secondary
    per={}
    for r in z["ycells"]: per.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2])))
    ncen={t:len(A.components(cs)) for t,cs in per.items()}
    first3=min((t for t,n in ncen.items() if n>=3),default=None)
    first2=min((t for t,n in ncen.items() if n>=2),default=None)
    ext=int(np.argmax(NY==0)) if (NY==0).any() else None
    comp=[i for i in iv if i["class"].startswith("COMPLETE")]
    fun=[i for i in comp if i["FUNCTIONAL"]]
    tt=[i["first_y_death"] for i in fun] or [i["first_y_death"] for i in comp]
    row={"tag":tag,"seed":m["seed"],"kind":m["kind"],"index":m["index"],"stop":m["stop"],
      "steps_executed":m["steps_executed"],"integrity_ok":m["integrity_ok"],
      "final_state_hash":m["final_state_hash"],
      "n_intervals":v["n_intervals"],"n_complete":v["n_complete"],"n_functional":v["n_functional"],
      "COMPLETE_TURNOVER":v["COMPLETE_TURNOVER"],"FUNCTIONAL_COMPLETE_TURNOVER":v["FUNCTIONAL_COMPLETE_TURNOVER"],
      "birth_then_death":v["birth_then_death"],"death_then_birth":v["death_then_birth"],
      "same_step":v["same_step"],
      "partial_birth_only":v["partial_birth_only"],"partial_death_only":v["partial_death_only"],
      "no_turnover":v["no_turnover"],
      "total_Y_births":int(z["ybirth"][:,3].sum()) if z["ybirth"].shape[0] else 0,
      "total_Y_deaths":int(z["ydeath"][:,3].sum()) if z["ydeath"].shape[0] else 0,
      "total_X_births":int(z["xbirth"][:,3].sum()) if z["xbirth"].shape[0] else 0,
      "max_NY":int(NY.max()),"max_Y_cells":int(ncells.max()),
      "first_two_centre_step":first2,"first_three_centre_step":first3,
      "extinction_step":ext,"daughter_formed":first2 is not None,
      "turnover_time":min(tt) if tt else None,
      "post_turnover_functional_duration":max([i["post_turnover_functional_duration"] for i in fun],default=0),
      "x_births_before_removal_steps":max([i["x_birth_steps_before_removal"] for i in fun],default=0),
      "x_births_after_removal_steps":max([i["x_birth_steps_after_removal"] for i in fun],default=0)}
    return row,iv

def main():
    SM=json.load(open(f"{OUT}/FDOT01_SEED_MANIFEST.json"))["SEEDS"]
    tags=[]
    for b in SM:
        if b["kind"]!="PRIMARY": continue
        tags.append("F_B1_P_i%03d_s%d"%(b["index"],b["seed"]))
    rows=[];allint={}
    for t in tags:
        r,iv=world(t); rows.append(r); allint[t]=iv
    N=len(rows)
    K_comp=sum(1 for r in rows if r["COMPLETE_TURNOVER"])
    K=sum(1 for r in rows if r["FUNCTIONAL_COMPLETE_TURNOVER"])
    P={"SECTION":"FDOT01 §18 — primary analysis","GENERATED_UTC":NOW(),
     "PRIMARY_POINT":"B1","PRIMARY_N":N_PRIMARY,"WORLDS_ANALYSED":N,
     "ALL_PRIMARY_WORLDS_PRESENT":N==N_PRIMARY,
     "K_COMPLETE_TURNOVER":K_comp,"K_FUNCTIONAL_COMPLETE_TURNOVER":K,
     "PRIMARY_K":K,"REPLICATION_THRESHOLD":THRESH,
     "QUALIFIED":bool(K>=THRESH),
     "FRESH_RATE":K/N if N else 0.0,"EXACT_95_CI":ci(K,N),"ONE_SIDED_LOWER_95":lo(K,N),
     "COMPLETE_RATE":K_comp/N if N else 0.0,"COMPLETE_EXACT_95_CI":ci(K_comp,N),
     "TECHNICAL_FAILURES":sum(1 for r in rows if not r["integrity_ok"]),
     "ALL_RAN_FULL_HORIZON":all(r["steps_executed"]==HOR for r in rows),
     "NO_THRESHOLD_INVENTED_AFTER_THE_FACT":True}
    json.dump(P,open(f"{OUT}/FDOT01_PRIMARY_ANALYSIS.json","w"),indent=1)
    D=json.load(open(f"{OUT}/FDOT01_DEVELOPMENTAL_RECOMPUTE.json"))
    tt=[r["turnover_time"] for r in rows if r["turnover_time"] is not None]
    S={"SECTION":"FDOT01 §19 — predeclared secondary analyses","GENERATED_UTC":NOW(),
     "daughter_formation_rate":{"k":sum(1 for r in rows if r["daughter_formed"]),"n":N},
     "complete_turnover_rate":{"k":K_comp,"n":N},
     "functional_turnover_rate":{"k":K,"n":N},
     "birth_then_death_intervals":sum(r["birth_then_death"] for r in rows),
     "death_then_birth_intervals":sum(r["death_then_birth"] for r in rows),
     "same_step_intervals":sum(r["same_step"] for r in rows),
     "partial_birth_only_intervals":sum(r["partial_birth_only"] for r in rows),
     "partial_death_only_intervals":sum(r["partial_death_only"] for r in rows),
     "no_turnover_intervals":sum(r["no_turnover"] for r in rows),
     "total_identity_intervals":sum(r["n_intervals"] for r in rows),
     "worlds_with_extinction":sum(1 for r in rows if r["extinction_step"] is not None),
     "worlds_with_a_third_centre":sum(1 for r in rows if r["first_three_centre_step"] is not None),
     "third_centre_before_turnover":sum(1 for r in rows if r["first_three_centre_step"] is not None
        and r["turnover_time"] is not None and r["first_three_centre_step"]<r["turnover_time"]),
     "third_centre_after_turnover":sum(1 for r in rows if r["first_three_centre_step"] is not None
        and r["turnover_time"] is not None and r["first_three_centre_step"]>=r["turnover_time"]),
     "no_third_centre":sum(1 for r in rows if r["first_three_centre_step"] is None),
     "total_Y_births":sum(r["total_Y_births"] for r in rows),
     "total_Y_deaths":sum(r["total_Y_deaths"] for r in rows),
     "total_X_births":sum(r["total_X_births"] for r in rows),
     "TURNOVER_TIME":{"n":len(tt),"min":min(tt) if tt else None,"median":statistics.median(tt) if tt else None,
                      "max":max(tt) if tt else None},
     "POST_TURNOVER_FUNCTIONAL_DURATION":[r["post_turnover_functional_duration"] for r in rows if r["FUNCTIONAL_COMPLETE_TURNOVER"]],
     "FRESH_VERSUS_DEVELOPMENTAL":{
       "NOT_POOLED":True,
       "fresh":{"n":N,"complete":K_comp,"functional":K},
       "developmental_recomputed_under_the_same_strict_rule":{
         "n":D["N_DEVELOPMENTAL_B1_WORLDS"],"complete":D["COMPLETE_TURNOVER"]["k"],"functional":D["FUNCTIONAL_TURNOVER"]["k"]},
       "developmental_as_DOTC01_reported":D["DOTC01_REPORTED"],
       "comparison_is_descriptive_only":True}}
    json.dump(S,open(f"{OUT}/FDOT01_SECONDARY_ANALYSIS.json","w"),indent=1)
    T={"SECTION":"FDOT01 §19 — turnover-time and duration detail","GENERATED_UTC":NOW(),
     "PER_WORLD":[{k:r[k] for k in ("tag","seed","turnover_time","post_turnover_functional_duration",
        "x_births_before_removal_steps","x_births_after_removal_steps","n_complete","n_functional")}
        for r in rows if r["n_complete"]>0]}
    json.dump(T,open(f"{OUT}/FDOT01_TURNOVER_TIME_ANALYSIS.json","w"),indent=1)
    json.dump(rows,open(f"{OUT}/FDOT01_WORLD_RESULTS.json","w"),indent=1)
    with open(f"{OUT}/FDOT01_WORLD_RESULTS.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    json.dump({"INTERVALS":{k:v for k,v in allint.items() if any(i["class"]!="NO_TURNOVER" for i in v)}},
              open(f"{OUT}/FDOT01_EVENT_INTERVALS.json","w"),indent=1)
    print(json.dumps({k:P[k] for k in ("WORLDS_ANALYSED","ALL_PRIMARY_WORLDS_PRESENT","K_COMPLETE_TURNOVER",
      "K_FUNCTIONAL_COMPLETE_TURNOVER","PRIMARY_K","QUALIFIED","FRESH_RATE","EXACT_95_CI",
      "ONE_SIDED_LOWER_95","TECHNICAL_FAILURES","ALL_RAN_FULL_HORIZON")},indent=1))

if __name__=="__main__": main()
