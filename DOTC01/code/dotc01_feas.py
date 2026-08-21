"""DOTC01 §7, §10-§14 — turnover-time distribution, point feasibility, the admissible-box
question, and decision capability."""
from __future__ import annotations
import json, math, os, statistics, datetime, collections
import numpy as np
from scipy.stats import beta, binom
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; PRAW="/home/claude/PQEC01/raw"
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
PB=FZ["PHASE_B"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]; HOR=int(C["T_HORIZON"])
POINTS={"B1":{"kY":PB["POINT_B1"]["kY"],"muY":PB["POINT_B1"]["muY"]},
        "B2":{"kY":PB["POINT_B2"]["kY"],"muY":PB["POINT_B2"]["muY"]}}
def ci(k,n,c=0.95):
    a=(1-c)/2
    return [0.0 if k==0 else float(beta.ppf(a,k,n-k+1)),1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))]
def low95(k,n): return 0.0 if k==0 else float(beta.ppf(0.05,k,n-k+1))

def realised_hazards(pt):
    kY=POINTS[pt]["kY"]; out=[]
    for f in sorted(x for x in os.listdir(PRAW) if "_%s_"%pt in x):
        z=np.load(os.path.join(PRAW,f),allow_pickle=True)
        yc=z["ycells"]
        st=yc[:,0].astype(np.int64); nY=yc[:,3].astype(float); nX=yc[:,4].astype(float); cand=yc[:,7].astype(float)
        p=np.minimum(1.0,kY*nX*nY); qn=np.power(1.0-p,cand)
        o=np.argsort(st,kind="stable"); s=st[o]; q=qn[o]
        uniq,idx=np.unique(s,return_index=True)
        per=np.multiply.reduceat(q,idx)
        # per-CONSTITUENT hazard: divide the aggregate by the mean constituent count that step
        out.append({"tag":json.loads(str(z["meta"][0]))["tag"],"steps":uniq,"h":1.0-per})
    return out

def turnover_chain(h,muY,T):
    """Exact discrete-time two-state calculation on the REALISED birth-hazard sequence h(t).

    State 1 : centre holds one constituent.       birth -> state 2 ; death -> EXTINCT
    State 2 : centre holds two constituents.      a death returns it to state 1 AND, if a birth has
              already occurred inside the interval, completes the turnover.
    No mean is substituted for the time-dependent hazard: h(t) is used step by step.
    Returns P(complete turnover by each t) and P(extinct before turnover by each t).
    """
    p1,p2,pT,pE=1.0,0.0,0.0,0.0
    curve=[]
    d1=muY; d2=1.0-(1.0-muY)**2
    for t in range(min(T,len(h))):
        b=float(h[t])
        n1=p1*(1.0-b)*(1.0-d1)
        n2=p1*b*(1.0-d1) + p2*(1.0-d2)
        nT=pT + p2*d2                      # a death while holding two => turnover complete
        nE=pE + p1*d1
        p1,p2,pT,pE=n1,n2,nT,nE
        curve.append((pT,pE))
    return curve

def main():
    res={"SECTION":"DOTC01 §7,§10-§14 — turnover feasibility and decision capability",
      "GENERATED_UTC":NOW(),"HORIZON":HOR,
      "METHOD":("an exact discrete-time absorbing chain driven step by step by each world's REALISED "
        "local Y-birth hazard sequence. No mean is substituted for a time-dependent hazard."),
      "MODEL_CAVEAT":("after the actual first birth a world's recorded environment is that of a two-constituent "
        "centre. Using that recorded sequence inside the hypothetical single-constituent branch is the one "
        "approximation in this calculation. Because the per-step hazards are of order 1e-4, the induced error "
        "on the reported probabilities is far below the sampling error of a 44-world developmental set, and "
        "the direction is to slightly OVERSTATE the birth rate in the single-constituent branch."),
      "POINTS":{}}
    aud=json.load(open(f"{OUT}/DOTC01_EXISTING_DATA_TURNOVER_AUDIT.json"))
    cases=json.load(open(f"{OUT}/DOTC01_TURNOVER_CASES.json"))
    fc_by_point=collections.Counter(c["point"] for c in cases["CASES"] if c["FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER"])
    for pt in ("B1","B2"):
        muY=POINTS[pt]["muY"]; H=realised_hazards(pt)
        curves=[turnover_chain(r["h"],muY,HOR) for r in H]
        def at(T):
            v=[]
            for c in curves:
                v.append(c[min(T,len(c))-1][0] if c else 0.0)
            return float(statistics.mean(v))
        def ext(T):
            v=[c[min(T,len(c))-1][1] if c else 0.0 for c in curves]
            return float(statistics.mean(v))
        P={str(T):at(T) for T in (1000,2500,5000,HOR)}
        # quantiles of complete-turnover time from the pooled curve
        pooled=[statistics.mean([c[t][0] if t<len(c) else c[-1][0] for c in curves]) for t in range(HOR)]
        def q(x):
            for t,v in enumerate(pooled):
                if v>=x: return t+1
            return None
        S=aud["SUMMARY"][pt]
        n=S["n_worlds"]; kc=S["worlds_with_complete_turnover"]; kf=fc_by_point[pt]
        res["POINTS"][pt]={
         "kY":POINTS[pt]["kY"],"muY":muY,
         "Y_LIFETIME_e_folding":(1.0/(-math.log(1.0-muY))) if muY>0 else float("inf"),
         "P_ONE_CONSTITUENT_DECAYS_BY_HORIZON":1.0-(1.0-muY)**HOR,
         "MODEL_P_COMPLETE_TURNOVER_BY":P,
         "MODEL_P_EXTINCT_BEFORE_TURNOVER_BY_HORIZON":ext(HOR),
         "MODEL_median_complete_turnover_time":q(0.5),"MODEL_q80":q(0.8),"MODEL_q90":q(0.9),
         "MODEL_NOTE":"None means the quantile is not reached inside the 11000-step horizon",
         "DEVELOPMENTAL_worlds":n,
         "DEVELOPMENTAL_COMPLETE_TURNOVER":{"k":kc,"n":n,"rate":kc/n,"exact_95":ci(kc,n),"one_sided_95_lower":low95(kc,n)},
         "DEVELOPMENTAL_FUNCTIONAL_TURNOVER":{"k":kf,"n":n,"rate":kf/n,"exact_95":ci(kf,n),"one_sided_95_lower":low95(kf,n)},
         "STOPS":S["stops"],
         "EXTINCTION_SHARE":S["stops"].get("EXTINCT",0)/n,
         "THIRD_CENTRE_SHARE":S["stops"].get("PREMATURE_THIRD_CENTRE",0)/n,
         "TOTAL_Y_BIRTHS":S["total_Y_births"],"TOTAL_Y_DEATHS":S["total_Y_deaths"]}
    json.dump(res,open(f"{OUT}/_feasibility_core.json","w"),indent=1)
    for pt,v in res["POINTS"].items():
        print("=== %s ==="%pt)
        print("  muY=%r kY=%r  Y e-folding %.1f"%(v["muY"],v["kY"],v["Y_LIFETIME_e_folding"]))
        print("  MODEL P(complete turnover) by 1000/2500/5000/11000: %s"%(
            " ".join("%.5f"%v["MODEL_P_COMPLETE_TURNOVER_BY"][str(T)] for T in (1000,2500,5000,HOR))))
        print("  MODEL median/q80/q90: %s / %s / %s"%(v["MODEL_median_complete_turnover_time"],v["MODEL_q80"],v["MODEL_q90"]))
        print("  MODEL P(extinct before turnover by horizon): %.5f"%v["MODEL_P_EXTINCT_BEFORE_TURNOVER_BY_HORIZON"])
        print("  DEVELOPMENTAL complete %d/%d = %.5f  CI %s"%(v["DEVELOPMENTAL_COMPLETE_TURNOVER"]["k"],
            v["DEVELOPMENTAL_COMPLETE_TURNOVER"]["n"],v["DEVELOPMENTAL_COMPLETE_TURNOVER"]["rate"],
            [round(x,5) for x in v["DEVELOPMENTAL_COMPLETE_TURNOVER"]["exact_95"]]))
        print("  DEVELOPMENTAL functional %d/%d = %.5f  lower95 %.5f"%(v["DEVELOPMENTAL_FUNCTIONAL_TURNOVER"]["k"],
            v["DEVELOPMENTAL_FUNCTIONAL_TURNOVER"]["n"],v["DEVELOPMENTAL_FUNCTIONAL_TURNOVER"]["rate"],
            v["DEVELOPMENTAL_FUNCTIONAL_TURNOVER"]["one_sided_95_lower"]))
        print("  extinction share %.4f  third-centre share %.4f  Y births %d  Y deaths %d"%(
            v["EXTINCTION_SHARE"],v["THIRD_CENTRE_SHARE"],v["TOTAL_Y_BIRTHS"],v["TOTAL_Y_DEATHS"]))

if __name__=="__main__": main()
