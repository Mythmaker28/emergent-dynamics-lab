"""DOTC01 §8-§9 — audit surviving developmental data for REAL organiser turnover.

Run only after §3-§7 are frozen. Every number here is POST_OUTCOME_DEVELOPMENTAL_DIAGNOSTIC.
No CLOC02 or RSLOC03 product is used.
"""
from __future__ import annotations
import json, math, os, csv, datetime, collections
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; PRAW="/home/claude/PQEC01/raw"
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
C=FZ["INHERITED_FROZEN_CONSTANTS"]; L=int(C["L"]); CORE_R=float(C["CORE_R"])

def components(cells):
    n=len(cells)
    if n==0: return []
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        for j in range(i+1,n):
            dy=abs(cells[i][0]-cells[j][0]); dy=min(dy,L-dy)
            dx=abs(cells[i][1]-cells[j][1]); dx=min(dx,L-dx)
            if math.hypot(dy,dx)<=CORE_R:
                a,b=f(i),f(j)
                if a!=b: par[a]=b
    g={}
    for i in range(n): g.setdefault(f(i),[]).append(i)
    return [sorted(v) for _,v in sorted(g.items())]

def centroid(cells,idxs):
    a0=cells[idxs[0]]
    oy=[((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in idxs]
    ox=[((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in idxs]
    return ((a0[0]+sum(oy)/len(oy))%L,(a0[1]+sum(ox)/len(ox))%L)

def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def match(prev,cur):
    """mutual-unique nearest-centroid matching within CORE_R; anything else ends the interval"""
    if not prev or not cur: return {}
    pc=[c for c,_ in prev]; cc=[c for c,_ in cur]
    m={}
    for i,a in enumerate(pc):
        d=[tdist(a,b) for b in cc]
        j=int(np.argmin(d))
        if d[j]>CORE_R: continue
        if sorted(d)[:2]!=sorted(d)[:1] and len(d)>1 and sorted(d)[0]==sorted(d)[1]: continue   # tie -> no match
        # reverse check
        dr=[tdist(cc[j],b) for b in pc]
        k=int(np.argmin(dr))
        if k!=i: continue
        if len(dr)>1 and sorted(dr)[0]==sorted(dr)[1]: continue
        m[i]=j
    return m

def audit_world(path,point):
    z=np.load(path,allow_pickle=True)
    meta=json.loads(str(z["meta"][0]))
    yc=z["ycells"]; yb=z["ybirth"]; yd=z["ydeath"]
    if yc.shape[0]==0: return None
    birth_by=collections.defaultdict(list); death_by=collections.defaultdict(list)
    for r in yb: birth_by[int(r[0])].append((int(r[1]),int(r[2]),int(r[3])))
    for r in yd: death_by[int(r[0])].append((int(r[1]),int(r[2]),int(r[3])))
    steps=collections.defaultdict(list)
    for r in yc: steps[int(r[0])].append((int(r[1]),int(r[2]),int(r[3])))   # y,x,nY
    order=sorted(steps)
    # identity intervals
    tracks=[]     # each: dict(start,end,births,deaths,minNY,maxNY,cells_seen,ended_by)
    prev=None; prev_tracks={}
    for t in order:
        cells=[(y,x) for y,x,_ in steps[t]]
        nYmap={(y,x):n for y,x,n in steps[t]}
        comps=components(cells)
        cur=[(centroid(cells,g),[cells[i] for i in g]) for g in comps]
        m=match(prev,cur) if prev is not None else {}
        newtracks={}
        for j,(cen,cl) in enumerate(cur):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0] in prev_tracks:
                tk=prev_tracks[src[0]]
            else:
                tk={"start":t,"births":0,"deaths":0,"minNY":10**9,"maxNY":0,"ended_by":None,
                    "birth_steps":[],"death_steps":[]}
                tracks.append(tk)
            tk["end"]=t
            ny=sum(nYmap[c] for c in cl); tk["minNY"]=min(tk["minNY"],ny); tk["maxNY"]=max(tk["maxNY"],ny)
            S=set(cl)
            for (by,bx,bn) in birth_by.get(t,[]):
                if (by,bx) in S: tk["births"]+=bn; tk["birth_steps"].append(t)
            for (dy_,dx_,dn) in death_by.get(t,[]):
                if (dy_,dx_) in S: tk["deaths"]+=dn; tk["death_steps"].append(t)
            newtracks[j]=tk
        prev=cur; prev_tracks=newtracks
    comp_turn=[]; part=[]
    for tk in tracks:
        if tk["births"]>0 and tk["deaths"]>0 and tk["minNY"]>=1:
            fb=min(tk["birth_steps"]); fd=min(tk["death_steps"])
            tk["ordering"]="BIRTH_THEN_DEATH" if fb<fd else ("DEATH_THEN_BIRTH" if fd<fb else "SAME_STEP")
            tk["first_birth"]=fb; tk["first_death"]=fd
            comp_turn.append(tk)
        elif tk["births"]>0 or tk["deaths"]>0:
            part.append(tk)
    return {"tag":meta["tag"],"point":point,"seed":meta["seed"],"stop":meta["stop"],"stop_step":meta["stop_step"],
            "n_identity_intervals":len(tracks),
            "n_partial_turnover":len(part),"n_complete_turnover":len(comp_turn),
            "complete":[{k:v for k,v in t.items() if k not in("birth_steps","death_steps")} for t in comp_turn],
            "total_Y_births":int(yb[:,3].sum()) if yb.shape[0] else 0,
            "total_Y_deaths":int(yd[:,3].sum()) if yd.shape[0] else 0}

def main():
    rows=[]
    for pt in ("B1","B2","A0"):
        for f in sorted(x for x in os.listdir(PRAW) if "_%s_"%pt in x):
            r=audit_world(os.path.join(PRAW,f),pt)
            if r: rows.append(r)
        print("  %s done"%pt,flush=True)
    agg={}
    for pt in ("B1","B2","A0"):
        R=[r for r in rows if r["point"]==pt]
        agg[pt]={"n_worlds":len(R),
          "total_identity_intervals":sum(r["n_identity_intervals"] for r in R),
          "worlds_with_partial_turnover":sum(1 for r in R if r["n_partial_turnover"]>0),
          "worlds_with_complete_turnover":sum(1 for r in R if r["n_complete_turnover"]>0),
          "centres_with_complete_turnover":sum(r["n_complete_turnover"] for r in R),
          "total_Y_births":sum(r["total_Y_births"] for r in R),
          "total_Y_deaths":sum(r["total_Y_deaths"] for r in R),
          "orderings":dict(collections.Counter(c["ordering"] for r in R for c in r["complete"])),
          "stops":dict(collections.Counter(r["stop"] for r in R))}
    A={"SECTION":"DOTC01 §8-§9 — audit of surviving developmental data for real organiser turnover",
      "GENERATED_UTC":NOW(),"STATUS":"POST_OUTCOME_DEVELOPMENTAL_DIAGNOSTIC",
      "SOURCE":"PQEC01 raw, 128 archives, exact event-aligned ybirth/ydeath ledgers and per-step ycells",
      "LOST_PRODUCTS_NOT_USED":["CLOC02","RSLOC03"],
      "CENTRE_RULE":"toroidal single-linkage, CORE_R = %r"%CORE_R,
      "IDENTITY_RULE":"mutual-unique nearest-centroid match within CORE_R; a tie, a fission or a merger ends the interval",
      "TURNOVER_VS_CREATION":("a fission ends the identity interval and starts new ones, so centre CREATION can "
        "never be counted as centre TURNOVER. §9 is enforced structurally, not by inspection."),
      "SUMMARY":agg,"WORLDS":rows}
    json.dump(A,open(f"{OUT}/DOTC01_EXISTING_DATA_TURNOVER_AUDIT.json","w"),indent=1)
    with open(f"{OUT}/DOTC01_EXISTING_DATA_TURNOVER_AUDIT.csv","w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["point","tag","seed","stop","stop_step","n_identity_intervals",
          "n_partial_turnover","n_complete_turnover","total_Y_births","total_Y_deaths"])
        for r in rows: w.writerow([r["point"],r["tag"],r["seed"],r["stop"],r["stop_step"],
          r["n_identity_intervals"],r["n_partial_turnover"],r["n_complete_turnover"],
          r["total_Y_births"],r["total_Y_deaths"]])
    print(json.dumps(agg,indent=1))

if __name__=="__main__": main()
