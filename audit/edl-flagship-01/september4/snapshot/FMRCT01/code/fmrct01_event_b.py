"""FMRCT01 §10 — implementation B of the load-bearing organisational event classifier.

Independently written: components by breadth-first search over an explicit adjacency list rather
than union-find; identity links built from explicit candidate sets in both directions rather than
from a dict comprehension; turnover accounting by scanning each identity's own step list rather
than by incremental accumulation. It shares no function with implementation A.
"""
from __future__ import annotations
import math, json, sys
import numpy as np
REPO="/home/claude/edl"
_C=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))["INHERITED_FROZEN_CONSTANTS"]
L=int(_C["L"]); CORE_R=float(_C["CORE_R"])

def _d(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy)
    dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def components(cells):
    n=len(cells)
    adj={i:[] for i in range(n)}
    for i in range(n):
        for j in range(i+1,n):
            if _d(cells[i],cells[j])<=CORE_R: adj[i].append(j); adj[j].append(i)
    seen=set(); out=[]
    for i in range(n):
        if i in seen: continue
        q=[i]; grp=[]
        while q:
            k=q.pop(0)
            if k in seen: continue
            seen.add(k); grp.append(k)
            for m in adj[k]:
                if m not in seen: q.append(m)
        out.append(sorted(grp))
    return sorted(out)

def centroid(cells,idxs):
    a=cells[idxs[0]]
    sy=sx=0.0
    for i in idxs:
        sy+=((cells[i][0]-a[0]+L/2)%L)-L/2
        sx+=((cells[i][1]-a[1]+L/2)%L)-L/2
    return ((a[0]+sy/len(idxs))%L,(a[1]+sx/len(idxs))%L)

def links(prev,cur):
    """explicit two-sided candidate sets; a link exists only when both sides have exactly one."""
    out={}
    for i in range(len(prev)):
        fwd=[j for j in range(len(cur)) if _d(prev[i],cur[j])<=CORE_R]
        if len(fwd)!=1: continue
        j=fwd[0]
        bwd=[k for k in range(len(prev)) if _d(prev[k],cur[j])<=CORE_R]
        if len(bwd)!=1: continue
        out[i]=j
    return out

def descent(prev_cells,prev_idx,cur_cells,cur_groups):
    if len(cur_groups)!=2: return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    pc=centroid(prev_cells,prev_idx)
    dd=[_d(pc,centroid(cur_cells,g)) for g in cur_groups]
    if dd[0]==dd[1]: return None,None,"DESCENT_AMBIGUOUS_EXACT_TIE"
    p=0 if dd[0]<dd[1] else 1
    if dd[p]>CORE_R: return None,None,"DESCENT_AMBIGUOUS_PARENT_NOT_CONTINUOUS"
    return p,1-p,"PARENT_CONTINUED_UNIQUELY"

def track(ycells,ybirth,ydeath,xbirth,horizon):
    rows={}
    for r in ycells: rows.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2]),int(r[3])))
    B={}; D={}; X={}
    for r in ybirth: B.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in ydeath: D.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in xbirth: X.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    hist={}          # id -> list of (step, frozenset(cells), nY)
    nxt=0; prev_cen=None; prev_ids=[]; steps={}
    for t in range(horizon):
        rr=rows.get(t)
        if not rr:
            prev_cen=None; prev_ids=[]; continue
        cells=[(y,x) for y,x,_ in rr]; nmap={(y,x):n for y,x,n in rr}
        gs=components(cells); cen=[centroid(cells,g) for g in gs]
        mp=links(prev_cen,cen) if prev_cen is not None else {}
        ids=[]
        for j in range(len(gs)):
            src=[i for i,jj in mp.items() if jj==j]
            if len(src)==1 and src[0]<len(prev_ids): ids.append(prev_ids[src[0]])
            else:
                ids.append(nxt); nxt+=1
        for j,i in enumerate(ids):
            S=frozenset(cells[k] for k in gs[j])
            hist.setdefault(i,[]).append((t,S,sum(nmap[c] for c in S)))
        steps[t]={"ids":ids,"sets":[set(cells[k] for k in g) for g in gs],"cells":cells,"cen":cen}
        prev_cen=cen; prev_ids=ids
    ev={}
    for i,h in hist.items():
        yb=[]; yd=[]; xb=[]
        for t,S,_ in h:
            for c,k in B.get(t,()):
                if c in S: yb.append(t)
            for c,k in D.get(t,()):
                if c in S: yd.append(t)
            for c,k in X.get(t,()):
                if c in S: xb.append(t)
        ev[i]={"start":h[0][0],"end":h[-1][0],"steps":len(h),"minNY":min(x[2] for x in h),
               "ybirth":yb,"ydeath":yd,"xbirth":xb}
    return steps,ev

def turnover(ev,idx,after):
    e=ev.get(idx)
    if e is None: return None
    yb=[t for t in e["ybirth"] if t>after]; yd=[t for t in e["ydeath"] if t>after]
    o={"COMPLETE":False,"FUNCTIONAL":False,"first_y_death":None,"x_before":0,"x_after":0,
       "post_duration":0,"minNY":e["minNY"],"y_births":len(yb),"y_deaths":len(yd)}
    if yb and yd and e["minNY"]>=1:
        o["COMPLETE"]=True; fd=min(yd); o["first_y_death"]=fd
        o["x_before"]=len([t for t in e["xbirth"] if after<t<fd])
        o["x_after"]=len([t for t in e["xbirth"] if t>fd])
        o["post_duration"]=e["end"]-fd
        o["FUNCTIONAL"]=bool(o["x_before"]>0 and o["x_after"]>0 and o["post_duration"]>0)
    return o
