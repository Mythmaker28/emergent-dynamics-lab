"""DOTC01 — exact scrutiny of every candidate complete-turnover centre, including the
functional-continuity test of §5 using the exact X-birth law."""
from __future__ import annotations
import json, math, os, collections, datetime
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; PRAW="/home/claude/PQEC01/raw"
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json")); C=FZ["INHERITED_FROZEN_CONSTANTS"]
L=int(C["L"]); CORE_R=float(C["CORE_R"]); KX=float(C["kX"]); CAP=int(C["CAP"])
SPECIES=("X","Y","SX","SY","WX","WY")

def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx); return math.hypot(dy,dx)

def planes_at(z,steps):
    """reconstruct the 6 planes at the recorded (post-diffusion, pre-reaction) phase for given steps"""
    f0=z["field0"].astype(np.int32); dl=z["field_delta"]
    need=max(steps)+1
    cur=f0.copy(); out={}
    want=set(steps)
    if 0 in want: out[0]=cur.copy()
    for t in range(1,min(need,dl.shape[0]+1)):
        cur=cur+dl[t-1].astype(np.int32)
        if t in want: out[t]=cur.copy()
    return out

def inspect(tag):
    z=np.load(os.path.join(PRAW,tag+".npz"),allow_pickle=True)
    yc=z["ycells"]; yb=z["ybirth"]; yd=z["ydeath"]
    byst=collections.defaultdict(list)
    for r in yc: byst[int(r[0])].append((int(r[1]),int(r[2]),int(r[3]),int(r[4]),int(r[6])))  # y,x,nY,nX,free
    return z,byst,yb,yd

def main():
    A=json.load(open(f"{OUT}/DOTC01_EXISTING_DATA_TURNOVER_AUDIT.json"))
    cases=[]
    for r in A["WORLDS"]:
        for c in r["complete"]:
            cases.append((r,c))
    results=[]
    for r,c in cases:
        z,byst,yb,yd=inspect(r["tag"])
        s0,s1=c["start"],c["end"]; fb,fd=c["first_birth"],c["first_death"]
        # NY trajectory of the tracked centre, approximated by the total NY within CORE_R of the
        # centre's cells at each step; for these small centres this equals the component NY.
        ny={t:sum(x[2] for x in byst.get(t,[])) for t in range(s0,min(s1,s0+1)+1)}
        traj=[]
        for t in list(range(max(s0,fd-6),min(s1,fd+6)+1)):
            traj.append((t,sum(x[2] for x in byst.get(t,[])),len(byst.get(t,[]))))
        # what ended the interval
        after=[]
        for t in range(s1,min(s1+4,max(byst)+1)):
            after.append((t,len(byst.get(t,[])),sum(x[2] for x in byst.get(t,[]))))
        # NY at the step of the first death (pre-reaction snapshot)
        ny_at_death=sum(x[2] for x in byst.get(fd,[]))
        ny_before_death=sum(x[2] for x in byst.get(fd-1,[])) if fd-1 in byst else None
        ny_after_death=sum(x[2] for x in byst.get(fd+1,[])) if fd+1 in byst else None
        # ---- §5 functional continuity: exact X births at the centre's Y cells ----
        probe=[t for t in (fd-200,fd-100,fd-20,fd-5,fd,fd+5,fd+20,fd+100,fd+200) if s0<=t<=s1 and t in byst]
        pl=planes_at(z,probe) if probe else {}
        fx=[]
        for t in probe:
            P=pl[t]; tot=0
            for (y,x,nY,nX,free) in byst[t]:
                nSX=int(P[SPECIES.index("SX")][y,x]); fr=int(free)
                cand=min(nSX,max(fr,0))
                p=min(1.0,KX*nX*nY)
                tot+= cand if (p>=1.0 and cand>0) else 0
            fx.append({"step":t,"exact_X_births_at_centre_cells":int(tot),
                       "relative_to_first_death":t-fd})
        pre=[q for q in fx if q["relative_to_first_death"]<0]
        post=[q for q in fx if q["relative_to_first_death"]>0]
        results.append({"tag":r["tag"],"seed":r["seed"],"point":r["point"],
          "stop":r["stop"],"stop_step":r["stop_step"],
          "interval":[s0,s1],"length":s1-s0+1,"ordering":c["ordering"],
          "first_birth":fb,"first_death":fd,"births":c["births"],"deaths":c["deaths"],
          "minNY":c["minNY"],"maxNY":c["maxNY"],
          "NY_at_the_death_step_pre_reaction":ny_at_death,
          "NY_one_step_before_death":ny_before_death,"NY_one_step_after_death":ny_after_death,
          "steps_the_centre_persisted_after_the_removal":s1-fd,
          "NY_trajectory_around_the_removal":traj,
          "world_state_just_after_the_interval_ended":after,
          "X_PRODUCTION_PROBE":fx,
          "active_local_X_production_before_removal":any(q["exact_X_births_at_centre_cells"]>0 for q in pre),
          "active_local_X_production_after_removal":any(q["exact_X_births_at_centre_cells"]>0 for q in post),
          "FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER":(any(q["exact_X_births_at_centre_cells"]>0 for q in pre)
              and any(q["exact_X_births_at_centre_cells"]>0 for q in post) and (s1-fd)>0)})
        print("%-24s %s int[%d,%d] fb=%d fd=%d NYatdeath=%s persisted_after=%d  Xprod pre=%s post=%s -> FC=%s"%(
            r["tag"],c["ordering"],s0,s1,fb,fd,ny_at_death,s1-fd,
            results[-1]["active_local_X_production_before_removal"],
            results[-1]["active_local_X_production_after_removal"],
            results[-1]["FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER"]),flush=True)
    json.dump({"SECTION":"DOTC01 — exact scrutiny of every candidate complete-turnover centre",
      "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "STATUS":"POST_OUTCOME_DEVELOPMENTAL_DIAGNOSTIC",
      "X_BIRTH_LAW_USED":("kX = 1.0, so p = min(1, kX*nX*nY) = 1 at any Y-occupied cell holding at least one X. "
        "X births there are then exactly min(nSX, free), a DETERMINISTIC count, so local X production is read "
        "off the reconstructed planes without any stochastic inference."),
      "N_CANDIDATES":len(results),
      "N_WITH_FUNCTIONAL_CONTINUITY":sum(1 for r in results if r["FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER"]),
      "CASES":results},open(f"{OUT}/DOTC01_TURNOVER_CASES.json","w"),indent=1)
    print("\nFUNCTIONAL_CONTINUITY_ACROSS_TURNOVER: %d of %d candidates"%(
        sum(1 for r in results if r["FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER"]),len(results)))

if __name__=="__main__": main()
