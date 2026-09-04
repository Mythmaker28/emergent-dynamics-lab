"""FDOT01 — implementation B of the same frozen rules, written independently of A.

A uses union-find, python distance loops and dict bookkeeping.
B uses scipy.sparse.csgraph.connected_components, a full numpy distance matrix and an
adjacency-count formulation of the linking rule. B imports nothing from A.
"""
from __future__ import annotations
import json
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
REPO="/home/claude/edl"
_C=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))["INHERITED_FROZEN_CONSTANTS"]
L=int(_C["L"]); CORE_R=float(_C["CORE_R"])

def _tor(a,b):
    d=np.abs(a[:,None]-b[None,:]); return np.minimum(d,L-d)

def components(cells):
    n=len(cells)
    if n==0: return []
    P=np.array(cells,dtype=float)
    dy=_tor(P[:,0],P[:,0]); dx=_tor(P[:,1],P[:,1])
    adj=(dy**2+dx**2)<=CORE_R**2
    np.fill_diagonal(adj,False)
    g=csr_matrix(adj)
    k,lab=connected_components(g,directed=False)
    return [sorted(np.flatnonzero(lab==c).tolist()) for c in range(k)]

def centroid(cells,idxs):
    a0=cells[idxs[0]]
    oy=np.array([((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in idxs],dtype=float)
    ox=np.array([((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in idxs],dtype=float)
    return (float((a0[0]+oy.mean())%L),float((a0[1]+ox.mean())%L))

def link(prev_cens,cur_cens):
    if not prev_cens or not cur_cens: return {}
    P=np.array(prev_cens,dtype=float); Cc=np.array(cur_cens,dtype=float)
    dy=_tor(P[:,0],Cc[:,0]); dx=_tor(P[:,1],Cc[:,1])
    D=np.sqrt(dy**2+dx**2)
    A=(D<=CORE_R)
    rows=A.sum(axis=1); cols=A.sum(axis=0)
    out={}
    for i in range(A.shape[0]):
        if rows[i]!=1: continue
        j=int(np.flatnonzero(A[i])[0])
        if cols[j]!=1: continue
        out[i]=j
    return out

def analyse_world(ycells,ybirth,ydeath,xbirth,horizon):
    ev={}
    for name,arr in (("yb",ybirth),("yd",ydeath),("xb",xbirth)):
        for r in arr: ev.setdefault((name,int(r[0])),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    steps={}
    for r in ycells: steps.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2]),int(r[3])))
    recs=[]; prevc=None; prevr={}
    for t in range(horizon):
        rows=steps.get(t)
        if not rows:
            prevc=None; prevr={}; continue
        cells=[(y,x) for y,x,_ in rows]; nm={(y,x):n for y,x,n in rows}
        gs=components(cells); cens=[centroid(cells,g) for g in gs]
        sets=[frozenset(cells[i] for i in g) for g in gs]
        m=link(prevc,cens) if prevc is not None else {}
        newr={}
        inv={v:k for k,v in m.items()}
        for j in range(len(gs)):
            i=inv.get(j)
            r=prevr.get(i) if i is not None else None
            if r is None:
                r={"start":t,"end":t,"yb":0,"yd":0,"xb":0,"minNY":None,"maxNY":0,
                   "fyb":None,"fyd":None,"xbs":[]}
                recs.append(r)
            r["end"]=t
            ny=sum(nm[c] for c in sets[j])
            r["minNY"]=ny if r["minNY"] is None else min(r["minNY"],ny)
            r["maxNY"]=max(r["maxNY"],ny)
            for c,k in ev.get(("yb",t),()):
                if c in sets[j]:
                    r["yb"]+=k
                    if r["fyb"] is None: r["fyb"]=t
            for c,k in ev.get(("yd",t),()):
                if c in sets[j]:
                    r["yd"]+=k
                    if r["fyd"] is None: r["fyd"]=t
            for c,k in ev.get(("xb",t),()):
                if c in sets[j]: r["xb"]+=k; r["xbs"].append(t)
            newr[j]=r
        prevc=cens; prevr=newr
    out=[]
    for r in recs:
        if r["yb"]>0 and r["yd"]>0 and (r["minNY"] or 0)>=1:
            cls=("COMPLETE_BIRTH_THEN_DEATH" if r["fyb"]<r["fyd"] else
                 "COMPLETE_DEATH_THEN_BIRTH" if r["fyd"]<r["fyb"] else "COMPLETE_SAME_STEP")
        elif r["yb"]>0: cls="PARTIAL_BIRTH_ONLY"
        elif r["yd"]>0: cls="PARTIAL_DEATH_ONLY"
        else: cls="NO_TURNOVER"
        fn=False; pre=post=dur=0
        if cls.startswith("COMPLETE"):
            fd=r["fyd"]
            pre=len([s for s in r["xbs"] if s<fd]); post=len([s for s in r["xbs"] if s>fd])
            dur=r["end"]-fd; fn=bool(pre and post and dur>0)
        out.append({"start":r["start"],"end":r["end"],"class":cls,"FUNCTIONAL":fn,
                    "y_births":r["yb"],"y_deaths":r["yd"],"x_births":r["xb"],
                    "minNY":r["minNY"] or 0,"maxNY":r["maxNY"],
                    "first_y_birth":r["fyb"],"first_y_death":r["fyd"],
                    "x_birth_steps_before_removal":pre,"x_birth_steps_after_removal":post,
                    "post_turnover_functional_duration":dur})
    return out
