"""FMRT01 §19-§20 — frozen causal analysis. Written and hashed before the first world."""
from __future__ import annotations
import csv,glob,json,math,os,sys
import numpy as np
from scipy.stats import binom,beta
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRT01/out"; RAW="/home/claude/FMRT01/raw"
sys.path.insert(0,f"{REPO}/FMRT01/code")
import fmrt01_identity as ID
import fmrt01_endpoint as EP
def crit(M,p0=0.05,alpha=0.05):
    if M==0: return None
    c=0
    while binom.sf(c-1,M,p0)>alpha: c+=1
    return c if c<=M else None
def cp(k,n,conf=0.95,one=False):
    if n==0: return [None,None]
    if one: return 0.0 if k==0 else float(beta.ppf(1-conf,k,n-k+1))
    a=(1-conf)/2
    return [0.0 if k==0 else float(beta.ppf(a,k,n-k+1)),1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))]

def r1_exact(z,rec):
    """inherited_mass_in_daughter_disc < f_primary * parent_disc_mass, at t_m."""
    t_m=rec["t_m"]; t0=t_m-EP.NEED+1
    y=z["tm_y"].astype(int); x=z["tm_x"].astype(int); bs=z["tm_birth_step"].astype(int)
    cy,cx=rec["daughter_centroid"]
    dm=ID.disc_mask(int(round(cy))%ID.L,int(round(cx))%ID.L)
    inside=dm[y,x]
    tot=int(inside.sum()); pre=int((inside&(bs<t0)).sum()); post=tot-pre
    loc=int((inside&(bs>=t0)).sum())
    req=EP.F_PRIMARY*rec["parent_mass_tm"]
    return {"t0_separation":t0,"daughter_total_tm":tot,"inherited":pre,"post_separation":post,
            "required":req,"R1_EXACT":bool(pre<req),
            "fraction_new":(post/tot) if tot else None}

def main():
    rows=[]
    for p in sorted(glob.glob(f"{RAW}/*.npz")):
        z=np.load(p,allow_pickle=True); rec=json.loads(str(z["meta"][0]))
        r={"block":rec["block"],"seed":rec["seed"],"triggered":bool(rec.get("triggered")),
           "t_m":rec.get("t_m"),"phase1_stop":rec.get("phase1_stop"),
           "identity_level":rec.get("identity_level"),
           "technical_failure":bool(rec.get("technical_failure")),
           "fork_identity_ok":rec.get("fork_identity_ok")}
        if rec.get("triggered"):
            r.update(r1_exact(z,rec))
            r["NX_world_at_intervention"]=rec["NX_world_at_intervention"]
            r["parent_mass_tm"]=rec["parent_mass_tm"]; r["daughter_mass_tm"]=rec["daughter_mass_tm"]
            for a,v in rec["ARMS"].items():
                for k2,v2 in v.items():
                    if k2.startswith("NX_series") or k2.startswith("NY_series"): continue
                    r["%s_%s"%(a,k2)]=v2
            r["late_trigger"]=bool(rec["t_m"]>EP.LATEST_ALLOWED_TRIGGER)
        z.close(); rows.append(r)
    rows.sort(key=lambda r:r["block"])
    N=len(rows)
    trig=[r for r in rows if r["triggered"] and not r.get("late_trigger")]
    M=len(trig)
    K=sum(1 for r in trig if r.get("SELECTIVE_R2_PASS"))
    c=crit(M)
    pval=float(binom.sf(K-1,M,0.05)) if M else None
    lo1=cp(K,M,0.95,True) if M else None
    PRIM={"SECTION":"FMRT01 §19 — primary causal analysis",
     "PRIMARY_SEED_BLOCKS":N,"PRIMARY_SCIENTIFIC_WORLDS":3*N,
     "M_TRIGGERED_SELECTIVE":M,"K_R2_PASS":K,
     "CRITICAL_COUNT_AT_M":c,"REJECT_H0":bool(c is not None and K>=c),
     "Q_AUTONOMY":(K/M) if M else None,
     "ONE_SIDED_LOWER_95":lo1,"TWO_SIDED_95":cp(K,M) if M else None,
     "EXACT_P_VALUE":pval,
     "LOWER_BOUND_EXCEEDS_NULL":bool(lo1 is not None and lo1>0.05),
     "DECISION_RULES_AGREE":bool(c is not None and lo1 is not None and (K>=c)==(lo1>0.05)),
     "NULL":"H0: q <= 0.05 (the frozen false-positive bound of R2 criterion D)",
     "METHOD":"exact binomial conditional on M; no normal approximation",
     "TECHNICAL_FAILURES":sum(1 for r in rows if r["technical_failure"]),
     "FORK_IDENTITY_OK_ALL":all(r.get("fork_identity_ok") is not False for r in rows)}
    json.dump(PRIM,open(f"{OUT}/FMRT01_PRIMARY_CAUSAL_ANALYSIS.json","w"),indent=2)
    repro=[r for r in rows if r["triggered"] and not r.get("late_trigger")
           and r.get("R1_EXACT") and r.get("SELECTIVE_R2_PASS")]
    POP={"SECTION":"FMRT01 §5 — population-level minimal reproduction",
     "DENOMINATOR":"every seeded block; failures before intervention are failures, not censored",
     "N":N,"COUNT":len(repro),"RATE":len(repro)/N if N else None,
     "TWO_SIDED_95":cp(len(repro),N),"ONE_SIDED_LOWER_95":cp(len(repro),N,0.95,True),
     "NOT_SUBSTITUTED_BY_THE_CONDITIONAL_RATE":True}
    json.dump(POP,open(f"{OUT}/FMRT01_POPULATION_REPRODUCTION_ANALYSIS.json","w"),indent=2)
    CTRL={"SECTION":"FMRT01 §14 — control analysis, paired on the same blocks",
     "N_TRIGGERED_BLOCKS":M,
     "SELECTIVE":{"R2_pass":K,"daughter_exists":sum(1 for r in trig if r.get("SELECTIVE_daughter_exists")),
       "criterion_D":sum(1 for r in trig if r.get("SELECTIVE_criterion_D")),
       "post_births":sum(1 for r in trig if (r.get("SELECTIVE_criterion_E_post_intervention_births_in_daughter") or 0)>0),
       "third_centre":sum(1 for r in trig if r.get("SELECTIVE_third_centre_in_window"))},
     "SHAM":{"R2_pass":sum(1 for r in trig if r.get("SHAM_R2_PASS")),
       "daughter_exists":sum(1 for r in trig if r.get("SHAM_daughter_exists")),
       "criterion_D":sum(1 for r in trig if r.get("SHAM_criterion_D")),
       "removed_total":sum(r.get("SHAM_removed",0) for r in trig),
       "third_centre":sum(1 for r in trig if r.get("SHAM_third_centre_in_window"))},
     "GLOBAL":{"R2_pass":sum(1 for r in trig if r.get("GLOBAL_R2_PASS")),
       "daughter_exists":sum(1 for r in trig if r.get("GLOBAL_daughter_exists")),
       "criterion_D":sum(1 for r in trig if r.get("GLOBAL_criterion_D")),
       "final_NY_all_zero":all(r.get("GLOBAL_final_NY")==0 for r in trig) if trig else None,
       "median_final_NX":float(np.median([r.get("GLOBAL_final_NX",0) for r in trig])) if trig else None},
     "SELECTIVE_median_final_NX":float(np.median([r.get("SELECTIVE_final_NX",0) for r in trig])) if trig else None,
     "SHAM_median_final_NX":float(np.median([r.get("SHAM_final_NX",0) for r in trig])) if trig else None,
     "INTERPRETATION_RULE":"SHAM checks that the trigger and audit machinery does not itself destroy daughter function; GLOBAL checks that with no Y source the field behaves as decaying inherited stock. SELECTIVE is not required to equal SHAM."}
    json.dump(CTRL,open(f"{OUT}/FMRT01_CONTROL_ANALYSIS.json","w"),indent=2)
    part={"no_trigger":0,"trigger_too_late":0,"triggered_R1_failed":0,
          "R1_ok_R2_failed_third_centre":0,"R1_ok_R2_failed_integrity":0,
          "R1_ok_R2_failed_other":0,"MINIMAL_REPRODUCTION_SUCCESS":0}
    for r in rows:
        if not r["triggered"]: part["no_trigger"]+=1; continue
        if r.get("late_trigger"): part["trigger_too_late"]+=1; continue
        if not r.get("R1_EXACT"): part["triggered_R1_failed"]+=1; continue
        if r.get("SELECTIVE_R2_PASS"): part["MINIMAL_REPRODUCTION_SUCCESS"]+=1; continue
        if r.get("SELECTIVE_third_centre_in_window"): part["R1_ok_R2_failed_third_centre"]+=1; continue
        if not r.get("SELECTIVE_integrity_ok_post",True): part["R1_ok_R2_failed_integrity"]+=1; continue
        part["R1_ok_R2_failed_other"]+=1
    FP={"SECTION":"FMRT01 §20 — failure partition; the categories are mutually exclusive and exhaustive",
     "PARTITION":part,"SUM":sum(part.values()),"N":N,"IS_A_PARTITION":sum(part.values())==N,
     "ORDER":"evaluated in the listed order so each block falls in exactly one class"}
    json.dump(FP,open(f"{OUT}/FMRT01_FAILURE_PARTITION.json","w"),indent=2)
    cols=sorted({k for r in rows for k in r})
    with open(f"{OUT}/FMRT01_WORLD_RESULTS.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore"); w.writeheader()
        for r in rows: w.writerow(r)
    json.dump(rows,open(f"{OUT}/FMRT01_WORLD_RESULTS.json","w"),indent=1)
    print(json.dumps({k:PRIM[k] for k in ("PRIMARY_SEED_BLOCKS","PRIMARY_SCIENTIFIC_WORLDS",
      "M_TRIGGERED_SELECTIVE","K_R2_PASS","CRITICAL_COUNT_AT_M","Q_AUTONOMY","ONE_SIDED_LOWER_95",
      "EXACT_P_VALUE","REJECT_H0","DECISION_RULES_AGREE","TECHNICAL_FAILURES")},indent=2))
    print("population:",{k:POP[k] for k in ("COUNT","RATE","TWO_SIDED_95")})
    print("controls:",json.dumps({k:CTRL[k] for k in ("SELECTIVE","SHAM","GLOBAL")},indent=1))
    print("partition:",part,"is_partition:",FP["IS_A_PARTITION"])
if __name__=="__main__": main()
