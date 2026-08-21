"""DOTC01 §6-§7 — the organiser timescale, derived exactly from the executable Y process.

FORMULAS ARE FROZEN HERE BEFORE ANY DEVELOPMENTAL DISTRIBUTION IS READ.

  Y lifetime.        death is a per-molecule Bernoulli(muY) each step, so for one constituent
                     P(alive after t steps) = (1-muY)^t exactly.
                     T_Y_SURVIVAL = 1 / (-ln(1-muY))            (continuous e-folding)
                     E[steps survived] = (1-muY)/muY            (exact discrete mean)
                     median = ceil( ln(0.5) / ln(1-muY) ) - 1   (exact discrete median)

  Local Y birth.     at a Y-occupied cell, births ~ Binomial(cand, p) with
                     p = min(1, kY*nX*nY) and cand = min(nSY, free).
                     P(no Y birth at that cell this step) = (1 - p)^cand   EXACTLY.
                     The linearisation kY*nX*nY*cand = kY*Q is an UPPER bound on the hazard
                     (Bernoulli union bound) and is used only with its error stated.

  Waiting times.     computed from the REALISED per-step hazard sequence of each world, never
                     from a mean substituted for a time-dependent hazard. Where a summary is
                     needed the exact realised product is reported together with the bound.
"""
from __future__ import annotations
import json, math, os, statistics, datetime
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; PRAW="/home/claude/PQEC01/raw"
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
PB=FZ["PHASE_B"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]
POINTS={"B1":{"kY":PB["POINT_B1"]["kY"],"muY":PB["POINT_B1"]["muY"]},
        "B2":{"kY":PB["POINT_B2"]["kY"],"muY":PB["POINT_B2"]["muY"]},
        "A0":{"kY":0.0,"muY":0.0}}
HOR=C["T_HORIZON"]

def lifetime(muY):
    if muY<=0: return {"muY":muY,"T_Y_SURVIVAL":float("inf"),"exact_discrete_mean":float("inf"),
                       "exact_discrete_median":None,"P_death_within_11000":0.0,
                       "note":"muY = 0: a constituent never decays, so no removal event can ever occur"}
    return {"muY":muY,
      "T_Y_SURVIVAL_e_folding":1.0/(-math.log(1.0-muY)),
      "exact_discrete_mean_steps_survived":(1.0-muY)/muY,
      "exact_discrete_median":int(math.ceil(math.log(0.5)/math.log(1.0-muY)))-1,
      "P_death_within_1000":1.0-(1.0-muY)**1000,
      "P_death_within_2500":1.0-(1.0-muY)**2500,
      "P_death_within_5000":1.0-(1.0-muY)**5000,
      "P_death_within_11000":1.0-(1.0-muY)**HOR}

def load(tag):
    z=np.load(os.path.join(PRAW,tag),allow_pickle=True)
    return (json.loads(str(z["meta"][0])), z["ycells"], z["ybirth"], z["ydeath"], z["scalars"])

def hazards_for_point(pt):
    """EXACT realised per-step local Y-birth hazard, per world, from the recorded environment."""
    kY=POINTS[pt]["kY"]
    files=sorted(f for f in os.listdir(PRAW) if "_%s_"%pt in f)
    out=[]
    for f in files:
        m,yc,yb,yd,sc=load(f)
        # ycells rows: step,y,x,nY,nX,nSY,free,candY,Q
        step=yc[:,0].astype(np.int64); nY=yc[:,3].astype(np.float64); nX=yc[:,4].astype(np.float64)
        cand=yc[:,7].astype(np.float64)
        p=np.minimum(1.0,kY*nX*nY)
        q_nobirth=np.power(1.0-p,cand)                    # per cell per step, EXACT
        # aggregate to per-step: probability no Y birth ANYWHERE this step
        order=np.argsort(step,kind="stable")
        s=step[order]; qq=q_nobirth[order]
        uniq,idx=np.unique(s,return_index=True)
        per_step=np.multiply.reduceat(qq,idx)
        haz=1.0-per_step
        out.append({"tag":m["tag"],"seed":m["seed"],"stop":m["stop"],"stop_step":m["stop_step"],
                    "steps":len(uniq),"haz":haz,"steps_index":uniq,
                    "n_ybirth_events":int(yb.shape[0]),"n_ybirth_molecules":int(yb[:,3].sum()) if yb.shape[0] else 0,
                    "n_ydeath_events":int(yd.shape[0]),"n_ydeath_molecules":int(yd[:,3].sum()) if yd.shape[0] else 0,
                    "max_nY_cells_in_a_step":int(np.bincount(step).max()) if len(step) else 0,
                    "Q_mean":float((nX*cand).mean()) if len(nX) else 0.0,
                    "Q_median":float(np.median(nX*cand)) if len(nX) else 0.0,
                    "Q_max":float((nX*cand).max()) if len(nX) else 0.0})
    return out

def survival_from_hazards(haz,T):
    """exact P(no local Y birth up to and including step T-1) on the realised hazard sequence"""
    h=haz[:T]
    if len(h)==0: return 1.0
    return float(np.exp(np.sum(np.log1p(-h))))

def main():
    os.makedirs(OUT,exist_ok=True)
    R={"SECTION":"DOTC01 §6-§7 — organiser timescale, derived from the executable Y process",
       "GENERATED_UTC":NOW(),
       "FORMULAS_FROZEN_BEFORE_READING_ANY_DEVELOPMENTAL_DISTRIBUTION":True,
       "HORIZON":HOR,"POINTS":POINTS,"Y_LIFETIME":{p:lifetime(POINTS[p]["muY"]) for p in POINTS}}
    per={}
    for pt in ("B1","B2"):
        rows=hazards_for_point(pt)
        muY=POINTS[pt]["muY"]
        Hs=[]
        for r in rows:
            for T in (1000,2500,5000,HOR):
                r["S_nobirth_%d"%T]=survival_from_hazards(r["haz"],T)
            r["S_nobirth_full"]=survival_from_hazards(r["haz"],len(r["haz"]))
            r["haz_mean"]=float(r["haz"].mean()); r["haz_median"]=float(np.median(r["haz"]))
            r["haz_max"]=float(r["haz"].max())
            Hs.append(r)
        agg={"n_worlds":len(Hs),
          "per_step_local_Y_birth_hazard":{
            "mean_of_world_means":statistics.mean([r["haz_mean"] for r in Hs]),
            "median_of_world_medians":statistics.median([r["haz_median"] for r in Hs]),
            "max_observed":max(r["haz_max"] for r in Hs)},
          "P_at_least_one_local_Y_birth_by":{
            str(T):1.0-statistics.mean([r["S_nobirth_%d"%T] for r in Hs]) for T in (1000,2500,5000,HOR)},
          "worlds_with_at_least_one_actual_Y_BIRTH_event":sum(1 for r in Hs if r["n_ybirth_events"]>0),
          "worlds_with_at_least_one_actual_Y_DEATH_event":sum(1 for r in Hs if r["n_ydeath_events"]>0),
          "total_Y_birth_molecules":sum(r["n_ybirth_molecules"] for r in Hs),
          "total_Y_death_molecules":sum(r["n_ydeath_molecules"] for r in Hs),
          "worlds_with_BOTH_a_birth_and_a_death_anywhere":sum(1 for r in Hs if r["n_ybirth_events"]>0 and r["n_ydeath_events"]>0),
          "max_Y_cells_ever_in_one_step":max(r["max_nY_cells_in_a_step"] for r in Hs),
          "Q_mean_over_worlds":statistics.mean([r["Q_mean"] for r in Hs]),
          "Q_max_over_worlds":max(r["Q_max"] for r in Hs),
          "stops":dict(__import__("collections").Counter(r["stop"] for r in Hs)),
          "LINEARISATION_ERROR":{
            "bound":"kY*Q is an upper bound on the per-cell hazard 1-(1-p)^cand",
            "max_relative_overstatement_observed":max(
              (POINTS[pt]["kY"]*r["Q_max"])/(r["haz_max"] if r["haz_max"]>0 else 1) for r in Hs) if any(r["haz_max"]>0 for r in Hs) else None}}
        per[pt]=agg
        R.setdefault("PER_WORLD",{})[pt]=[{k:v for k,v in r.items() if k not in("haz","steps_index")} for r in Hs]
    R["POINT_SUMMARY"]=per
    json.dump(R,open(f"{OUT}/DOTC01_ORGANISER_TIMESCALE.json","w"),indent=1)
    for p in ("B1","B2"):
        lt=R["Y_LIFETIME"][p]; a=per[p]
        print("=== %s ==="%p)
        print("  muY=%r kY=%r"%(POINTS[p]["muY"],POINTS[p]["kY"]))
        print("  T_Y_SURVIVAL e-folding: %s"%lt.get("T_Y_SURVIVAL_e_folding"))
        print("  P(one constituent decays within 11000): %.6g"%lt["P_death_within_11000"])
        print("  local Y-birth hazard/step: mean %.3e median %.3e max %.3e"%(
            a["per_step_local_Y_birth_hazard"]["mean_of_world_means"],
            a["per_step_local_Y_birth_hazard"]["median_of_world_medians"],
            a["per_step_local_Y_birth_hazard"]["max_observed"]))
        print("  P(>=1 local Y birth) by 1000/2500/5000/11000: %s"%(
            " ".join("%.4f"%a["P_at_least_one_local_Y_birth_by"][str(T)] for T in (1000,2500,5000,HOR))))
        print("  ACTUAL ledger: worlds with a Y BIRTH %d/%d, with a Y DEATH %d/%d, with BOTH %d/%d"%(
            a["worlds_with_at_least_one_actual_Y_BIRTH_event"],a["n_worlds"],
            a["worlds_with_at_least_one_actual_Y_DEATH_event"],a["n_worlds"],
            a["worlds_with_BOTH_a_birth_and_a_death_anywhere"],a["n_worlds"]))
        print("  total Y molecules born %d, died %d | max Y cells in one step %d"%(
            a["total_Y_birth_molecules"],a["total_Y_death_molecules"],a["max_Y_cells_ever_in_one_step"]))
        print("  stops:",a["stops"])

if __name__=="__main__": main()
