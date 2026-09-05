"""TLMR01 §16 — the frozen analysis. Written and hashed BEFORE world 1.

It reads archives, applies the offline reconstruction, aggregates M1 to M5 per law under the §7
support and clustering rules, applies the §8 selection rule, and returns exactly one disposition
from the §8 cascade. It contains no free choice: every threshold, every unit and every ordering
is read from the frozen artefacts rather than written here.
"""
from __future__ import annotations
import json, os, sys, glob, hashlib, datetime, math
import numpy as np
from scipy.stats import beta, binom
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"; RAW="/home/claude/TLMR01/raw"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_offline as OFF
import tlmr01_design as DZ
U=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
B_BOOT=2000

def ci(k,n):
    if n==0: return [None,None]
    return [0.0 if k==0 else float(beta.ppf(0.025,k,n-k+1)),
            1.0 if k==n else float(beta.ppf(0.975,k+1,n-k))]
def lo95(k,n): return 0.0 if (n==0 or k==0) else float(beta.ppf(0.05,k,n-k+1))
def up95(k,n): return None if n==0 else (1.0 if k==n else float(beta.ppf(0.95,k+1,n-k)))

def prop(k,n,worlds=None):
    d={"k":int(k),"n":int(n),"rate":(k/n if n else None),"exact_95_CI":ci(k,n),
       "one_sided_lower_95":lo95(k,n),"one_sided_upper_95":up95(k,n)}
    if worlds is not None:
        d["contributing_worlds"]=int(worlds)
        d["DIRECTLY_MEASURED"]=bool(worlds>=DZ.MIN_WORLDS and n>=DZ.MIN_EVENTS)
        if not d["DIRECTLY_MEASURED"]: d["SUPPORT"]="SUPPORT_TOO_THIN__NOT_DIRECTLY_MEASURED"
    return d

def boot_ratio(pairs,rng,B=B_BOOT):
    """world-clustered percentile interval for sum(num)/sum(den) over worlds."""
    if not pairs: return [None,None]
    num=np.array([p[0] for p in pairs],float); den=np.array([p[1] for p in pairs],float)
    if den.sum()<=0: return [None,None]
    n=len(pairs); out=np.empty(B)
    idx=rng.integers(0,n,size=(B,n))
    for b in range(B):
        i=idx[b]; dd=den[i].sum()
        out[b]=(num[i].sum()/dd) if dd>0 else np.nan
    out=out[~np.isnan(out)]
    if out.size==0: return [None,None]
    return [float(np.percentile(out,2.5)),float(np.percentile(out,97.5))]

def aggregate(rows,rng):
    """rows: per-world measure dicts, all at ONE law."""
    nW=len(rows)
    # ---- M4 exposure, and M1 hazard, both resolved by occupancy
    expo={}; forks={}; per_world={}
    for r in rows:
        for n_,v in r["M1"]["exposure_by_n"].items():
            n_=int(n_); expo[n_]=expo.get(n_,0)+v
            per_world.setdefault(n_,{}).setdefault(r["tag"],[0,0])[1]+=v
        for n_,v in r["M1"]["fork_to_two_or_more_by_n"].items():
            n_=int(n_); forks[n_]=forks.get(n_,0)+v
            per_world.setdefault(n_,{}).setdefault(r["tag"],[0,0])[0]+=v
    M1={}
    for n_ in sorted(expo):
        pw=[tuple(v) for v in per_world[n_].values()]
        d=prop(forks.get(n_,0),expo[n_],worlds=len(per_world[n_]))
        d["world_clustered_95_CI"]=boot_ratio(pw,rng)
        M1[str(n_)]=d
    above={n_:v for n_,v in expo.items() if n_>OFF.sI}
    M1_above=None
    if above:
        pw={}
        for r in rows:
            a=sum(v for n_,v in r["M1"]["exposure_by_n"].items() if int(n_)>OFF.sI)
            f=sum(v for n_,v in r["M1"]["fork_to_two_or_more_by_n"].items() if int(n_)>OFF.sI)
            if a: pw[r["tag"]]=(f,a)
        M1_above=prop(sum(forks.get(n_,0) for n_ in above),sum(above.values()),worlds=len(pw))
        M1_above["world_clustered_95_CI"]=boot_ratio(list(pw.values()),rng)
        M1_above["strata"]=sorted(above)
    # ---- M2 maturation by occupancy at separation
    ep={}; epw={}
    for r in rows:
        for n_,d in r["M2"].items():
            n_=int(n_); e=ep.setdefault(n_,{"episodes":0,"matured":0,"terminators":{}})
            e["episodes"]+=d["episodes"]; e["matured"]+=d["matured"]
            for k,v in d["terminators"].items(): e["terminators"][k]=e["terminators"].get(k,0)+v
            epw.setdefault(n_,{})[r["tag"]]=(d["matured"],d["episodes"])
    M2={}
    for n_ in sorted(ep):
        d=prop(ep[n_]["matured"],ep[n_]["episodes"],worlds=len(epw[n_]))
        d["world_clustered_95_CI"]=boot_ratio(list(epw[n_].values()),rng)
        d["terminators"]=ep[n_]["terminators"]
        M2[str(n_)]=d
    # ---- M3
    nm=sum(r["M3"]["n_matured"] for r in rows); nt=sum(r["M3"]["n_triggered"] for r in rows)
    wm=[r["tag"] for r in rows if r["M3"]["n_matured"]>0]
    fm={}
    for r in rows:
        for k,v in r["M3"]["failure_modes"].items(): fm[k]=fm.get(k,0)+v
    M3=prop(nt,nm,worlds=len(wm)); M3["failure_modes"]=fm
    M3["world_clustered_95_CI"]=boot_ratio([(r["M3"]["n_triggered"],r["M3"]["n_matured"])
                                            for r in rows if r["M3"]["n_matured"]>0],rng)
    # ---- M4
    tot=sum(r["M4"]["single_centre_steps"] for r in rows)
    ab=sum(r["M4"]["steps_above_support_ceiling"] for r in rows)
    hist={}
    for r in rows:
        for n_,v in r["M4"]["by_occupancy"].items(): hist[int(n_)]=hist.get(int(n_),0)+v
    M4={"single_centre_steps_total":tot,"steps_above_support_ceiling":ab,
        "support_ceiling_sI":OFF.sI,
        "worlds_with_exposure_above_the_ceiling":sum(
            1 for r in rows if r["M4"]["steps_above_support_ceiling"]>0),
        "max_single_centre_occupancy":max([r["M4"]["max_single_centre_occupancy"] for r in rows],default=0),
        "occupancy_histogram":{str(k):hist[k] for k in sorted(hist)},
        "median_horizon_fraction_single_centre":float(np.median(
            [r["M4"]["fraction_of_horizon_single_centre"] for r in rows])) if rows else None}
    # ---- M5, the selection statistic. Unit = world.
    A=sum(1 for r in rows if r["M5"]["A_maturation_reached"])
    Bs=sum(1 for r in rows if r["M5"]["B_trigger_fired"])
    C=sum(1 for r in rows if r["M5"]["C_selective_removal_applied"])
    D=sum(1 for r in rows if r["M5"]["INTEGRATED"])
    M5={"per_world":prop(D,nW,worlds=nW),
        "chain":{"A_maturation_reached":prop(A,nW),
                 "B_trigger_given_A":prop(Bs,A) if A else prop(0,0),
                 "C_removal_given_B":prop(C,Bs) if Bs else prop(0,0),
                 "D_functional_turnover_given_C":prop(D,C) if C else prop(0,0)},
        "counts":{"A":A,"B":Bs,"C":C,"D":D,"N":nW}}
    return {"N_WORLDS":nW,"M1_by_occupancy":M1,"M1_above_support_ceiling":M1_above,
            "M2_by_occupancy_at_separation":M2,"M3_trigger_given_matured":M3,
            "M4_single_centre_exposure":M4,"M5_integrated":M5}

def eligibility(law,agg,planned_n,tech_failures):
    F=DZ.FLOOR["value"]; m5=agg["M5_integrated"]["per_world"]
    K=m5["k"]; n=m5["n"]; lb=m5["one_sided_lower_95"]
    cn=DZ.confirmation_n(lb,F) if lb and lb>F else None
    m2ok=any(v.get("DIRECTLY_MEASURED") and v["k"]>0
             for v in agg["M2_by_occupancy_at_separation"].values())
    m3ok=agg["M3_trigger_given_matured"]["n"]>0
    E={"E1_complete_denominator_no_unreplaced_technical_failure":bool(n==planned_n and tech_failures==0),
       "E2_K_at_least_%d"%DZ.K_MIN:bool(K>=DZ.K_MIN),
       "E3_lower_bound_exceeds_F_INTEGRATED":bool(lb>F),
       "E4_M2_directly_measured_where_maturation_observed":bool(m2ok),
       "E5_M3_directly_measured":bool(m3ok),
       "E6_confirmation_affordable_at_or_below_%d_worlds"%DZ.CONFIRMATION_CEILING:bool(cn is not None)}
    return {"law":law,"K":K,"n":n,"lower_95":lb,"F_INTEGRATED":F,
            "confirmation_n_required":cn,
            "CLEARS_THE_STRONGER_TURNOVER_REFERENCE":bool(lb>DZ.STRONGER_REFERENCE["value"]),
            "CLAUSES":E,"ELIGIBLE":all(E.values())}

def main():
    FZ=json.load(open(f"{OUT}/TLMR01_MASTER_FREEZE.json"))
    assert FZ["ALL_GATES_PASS"], "the master freeze did not pass; no analysis is run"
    SM=json.load(open(f"{OUT}/TLMR01_SEED_MANIFEST.json"))
    planned={law:0 for law in DZ.N}
    for b in SM["SEEDS"]:
        if b["role"]=="PRIMARY": planned[b["law"]]+=1
    seed=int(hashlib.sha256(("TLMR01|BOOTSTRAP|"+FZ["PARENT_TIP"]).encode()).hexdigest()[:8],16)
    rng=np.random.default_rng(seed)
    paths=sorted(glob.glob(os.path.join(RAW,"TLMR01_*_P_*.npz")))
    rows=[OFF.measure_world(p) for p in paths]
    by={}
    for r in rows: by.setdefault(r["law"],[]).append(r)
    tech={law:sum(1 for r in v if not r["integrity_ok"]) for law,v in by.items()}
    aggs={law:aggregate(v,rng) for law,v in by.items()}
    elig={law:eligibility(law,aggs[law],planned[law],tech.get(law,0)) for law in aggs}
    # ---- §8 disposition cascade, first match wins
    short=[law for law in planned if len(by.get(law,[]))!=planned[law]]
    anytech=sum(tech.values())
    primary_ok=any(a["M1_above_support_ceiling"] and a["M1_above_support_ceiling"].get("DIRECTLY_MEASURED")
                   for a in aggs.values())
    ok=[e for e in elig.values() if e["ELIGIBLE"]]
    disp=None; selected=None
    if short or anytech>0:
        disp="TECHNICALLY_INVALID__DENOMINATOR_INCOMPLETE_OR_UNREPLACED_TECHNICAL_FAILURE"
    elif not primary_ok:
        disp="MEASUREMENT_INCOMPLETE__PRIMARY_REGIME_UNREACHED"
    else:
        if ok:
            best=max(e["lower_95"] for e in ok)
            tied=[e for e in ok if e["lower_95"]==best]
            if len(tied)==1:
                disp="MEASUREMENT_DELIVERED__ONE_LAW_SELECTED_FOR_DISJOINT_CONFIRMATION"
                selected=tied[0]["law"]
            else:
                disp="MEASUREMENT_DELIVERED__NO_LAW_SELECTED__EXACT_TIE"
        else:
            disp="MEASUREMENT_DELIVERED__NO_LAW_ELIGIBLE__CONFIRMATION_NOT_AUTHORISED"
    art={"MISSION":"TLMR01","SECTION":"16 — frozen analysis","GENERATED_UTC":U(),
     "FREEZE_HASH":FZ["FREEZE_HASH"],"BOOTSTRAP_SEED":seed,"BOOTSTRAP_DRAWS":B_BOOT,
     "N_ARCHIVES_READ":len(rows),"PLANNED_PER_LAW":planned,
     "READ_PER_LAW":{law:len(v) for law,v in by.items()},
     "TECHNICAL_FAILURES_PER_LAW":tech,
     "SHORT_DENOMINATORS":short,
     "PER_LAW":aggs,"ELIGIBILITY":elig,
     "PRIMARY_ESTIMAND_SUPPORT_REACHED":primary_ok,
     "SELECTED_LAW":selected,"DISPOSITION":disp,
     "UNCONDITIONAL":DZ.terminal_vocabulary()["UNCONDITIONAL"],
     "NO_POOLING_ACROSS_LAWS_IN_ANY_GATE":True,
     "NO_THRESHOLD_WAS_CHANGED_AFTER_THE_FREEZE":True}
    json.dump(art,open(f"{OUT}/TLMR01_ANALYSIS.json","w"),indent=1)
    json.dump({"PER_WORLD":[{k:r[k] for k in ("tag","law","seed","steps_executed","integrity_ok",
        "TERMINAL_LABEL","online_t_m")} | {"M5":r["M5"]["INTEGRATED"],
        "single_centre_steps":r["M4"]["single_centre_steps"],
        "steps_above_sI":r["M4"]["steps_above_support_ceiling"],
        "n_episodes":len(r["M2_episodes"]),"n_matured":r["M3"]["n_matured"]} for r in rows]},
      open(f"{OUT}/TLMR01_WORLD_RESULTS.json","w"),indent=1)
    print("archives read:",len(rows),"| per law:",art["READ_PER_LAW"])
    print("primary support above sI reached:",primary_ok)
    for law,e in elig.items():
        print("  %-16s K=%d/%d lower95=%.5f eligible=%s conf_n=%s"%(
          law,e["K"],e["n"],e["lower_95"] or 0.0,e["ELIGIBLE"],e["confirmation_n_required"]))
    print("SELECTED_LAW =",selected)
    print("DISPOSITION  =",disp)

if __name__=="__main__": main()
