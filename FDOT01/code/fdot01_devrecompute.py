"""FDOT01 §3 — recompute the developmental design inputs from the PARENT BYTES, under the exact
rule FDOT01 will use, BEFORE any fresh world is run. Design inputs only."""
from __future__ import annotations
import json, os, sys, datetime
import numpy as np
REPO="/home/claude/edl"; sys.path.insert(0,f"{REPO}/FDOT01/code")
import fdot01_centres as A
PRAW="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FDOT01/out"
SPECIES=("X","Y","SX","SY","WX","WY")
HOR=11000

def xbirths_from_planes(z,steps_needed,cellsets_by_step):
    """EXACT: kX = 1.0 so p = min(1,kX*nX*nY) = 1 at any Y cell holding an X, and the birth count
    is exactly min(nSX, free). free and nX are in ycells; nSX comes from the recorded planes."""
    if not steps_needed: return {}
    f0=z["field0"].astype(np.int32); dl=z["field_delta"]
    need=max(steps_needed); want=set(steps_needed); cur=f0.copy(); out={}
    if 0 in want: out[0]=cur.copy()
    for t in range(1,min(need+1,dl.shape[0]+1)):
        cur=cur+dl[t-1].astype(np.int32)
        if t in want: out[t]=cur.copy()
    return out

def main():
    files=sorted(f for f in os.listdir(PRAW) if "_B1_" in f)
    rows=[]
    for f in files:
        z=np.load(os.path.join(PRAW,f),allow_pickle=True)
        m=json.loads(str(z["meta"][0]))
        yc=z["ycells"]; yb=z["ybirth"]; yd=z["ydeath"]
        iv=A.analyse_world(yc,yb,yd,np.zeros((0,4),np.int32),HOR)   # no X ledger yet
        comp=[i for i in iv if i["class"].startswith("COMPLETE")]
        row={"tag":m["tag"],"stop":m["stop"],"n_intervals":len(iv),"n_complete":len(comp),
             "complete":comp,"functional":0}
        if comp:
            # rebuild the centre cell sets only where needed, then count exact X births
            per={}
            for r in yc: per.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2]),int(r[3]),int(r[4]),int(r[6])))
            need=set()
            for c in comp: need.update(range(c["start"],c["end"]+1))
            pl=xbirths_from_planes(z,sorted(need),None)
            for c in comp:
                fd=c["first_y_death"]; pre=post=0
                for t in range(c["start"],c["end"]+1):
                    P=pl.get(t)
                    if P is None: continue
                    tot=0
                    for (y,x,nY,nX,free) in per.get(t,[]):
                        if nX>=1 and nY>=1:
                            tot+=min(int(P[SPECIES.index("SX")][y,x]),max(int(free),0))
                    if tot>0:
                        if t<fd: pre+=1
                        elif t>fd: post+=1
                c["x_steps_before"]=pre; c["x_steps_after"]=post
                c["FUNCTIONAL"]=bool(pre>0 and post>0 and (c["end"]-fd)>0)
            row["functional"]=sum(1 for c in comp if c["FUNCTIONAL"])
        rows.append(row)
        print("  %s complete=%d functional=%d"%(row["tag"],row["n_complete"],row["functional"]),flush=True)
    n=len(rows)
    kc=sum(1 for r in rows if r["n_complete"]>0); kf=sum(1 for r in rows if r["functional"]>0)
    from scipy.stats import beta
    lo=lambda k,N: 0.0 if k==0 else float(beta.ppf(0.05,k,N-k+1))
    ci=lambda k,N: [0.0 if k==0 else float(beta.ppf(0.025,k,N-k+1)),1.0 if k==N else float(beta.ppf(0.975,k+1,N-k))]
    R={"SECTION":"FDOT01 §3 — developmental design inputs recomputed from parent bytes, before runs",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "RULE_USED":"the FDOT01 implementation of the DOTC01 definition, in which a split or a merge terminates identity",
     "N_DEVELOPMENTAL_B1_WORLDS":n,
     "COMPLETE_TURNOVER":{"k":kc,"n":n,"rate":kc/n,"exact_95":ci(kc,n),"one_sided_95_lower":lo(kc,n)},
     "FUNCTIONAL_TURNOVER":{"k":kf,"n":n,"rate":kf/n,"exact_95":ci(kf,n),"one_sided_95_lower":lo(kf,n)},
     "DOTC01_REPORTED":{"complete":4,"functional":3,"functional_one_sided_95_lower":0.018840467964271104},
     "DIFFERENCE_EXPLAINED":("DOTC01's audit code linked components by mutual-nearest with a tie guard, "
       "which does not terminate an interval when one component splits into two that both stay within "
       "CORE_R. Its written definition, and FDOT01 §5, both say a split terminates identity. FDOT01 "
       "implements the DEFINITION, which is strictly stricter, so the recomputed counts can only be "
       "lower or equal. Both figures are reported and the parent definition is preserved."),
     "WORLDS":rows}
    json.dump(R,open(f"{OUT}/FDOT01_DEVELOPMENTAL_RECOMPUTE.json","w"),indent=1)
    print("\nSTRICT RULE on the 44 developmental B1 worlds: complete %d/%d, functional %d/%d"%(kc,n,kf,n))
    print("functional one-sided 95%% lower bound: %.8f  (DOTC01 reported %.8f)"%(lo(kf,n),0.018840467964271104))

if __name__=="__main__": main()
