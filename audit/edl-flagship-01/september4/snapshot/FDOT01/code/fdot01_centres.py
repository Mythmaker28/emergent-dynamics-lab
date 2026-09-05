"""FDOT01 — implementation A of the frozen DOTC01 organiser object, turnover event and
functional-continuity rule.

THE RULES ARE DOTC01'S, NOT NEW ONES.

  Centre                a toroidal single-linkage component of Y-occupied cells, adjacency
                        distance <= CORE_R.
  Identity across steps  DOTC01's definition: "a component at step t+1 continues a component at
                        step t when it is the unique nearest component by toroidal centroid
                        distance in both directions and that distance does not exceed CORE_R. A
                        step at which the match is not mutually unique ENDS the identity
                        interval; it is never resolved by preference."
                        FDOT01 §5 spells out the same thing: tie -> terminate, split -> terminate,
                        merge -> terminate.
  COMPLETE_TURNOVER     at least one accepted Y birth inside C, at least one Y removal inside C,
                        both inside ONE identity interval, C never empty.
  FUNCTIONAL            ACTIVE_LOCAL_X_PRODUCTION: at least one accepted X birth inside the
                        centre's own cells on BOTH sides of the removal event, and the centre
                        still exists after that removal.

DECLARED DIFFERENCE FROM THE PARENT CODE, PRESERVING THE PARENT DEFINITION.
DOTC01's audit code linked components by mutual-nearest with a tie guard, which does NOT
terminate an interval when one component splits into two that both remain within CORE_R. Its
written definition, and FDOT01 §5, both say a split terminates identity. This module implements
the DEFINITION: a link continues an identity only when the previous component has exactly one
candidate within CORE_R and the current component has exactly one candidate within CORE_R.
That is STRICTER than the parent code, so it can only lower the event rate, never raise it. The
developmental rate is therefore recomputed under THIS rule before any world is run, and both
figures are reported.
"""
from __future__ import annotations
import json, math
import numpy as np
REPO="/home/claude/edl"
_C=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))["INHERITED_FROZEN_CONSTANTS"]
L=int(_C["L"]); CORE_R=float(_C["CORE_R"])

def components(cells):
    """toroidal single-linkage over Y-occupied cells, adjacency <= CORE_R (union-find)"""
    n=len(cells)
    if n==0: return []
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        yi,xi=cells[i]
        for j in range(i+1,n):
            yj,xj=cells[j]
            dy=abs(yi-yj); dy=min(dy,L-dy); dx=abs(xi-xj); dx=min(dx,L-dx)
            if dy*dy+dx*dx<=CORE_R*CORE_R:
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

def link(prev_cens,cur_cens):
    """DOTC01's identity rule. Returns {prev_index: cur_index} for CLEAN links only.
    A previous component with two or more candidates within CORE_R is a SPLIT and is not linked.
    A current component with two or more candidates within CORE_R is a MERGE and is not linked.
    An equal-distance tie leaves more than one candidate and is therefore also not linked."""
    if not prev_cens or not cur_cens: return {}
    cand_fwd={i:[j for j,c in enumerate(cur_cens) if tdist(p,c)<=CORE_R] for i,p in enumerate(prev_cens)}
    cand_bwd={j:[i for i,p in enumerate(prev_cens) if tdist(p,c)<=CORE_R] for j,c in enumerate(cur_cens)}
    out={}
    for i,js in cand_fwd.items():
        if len(js)!=1: continue
        j=js[0]
        if len(cand_bwd[j])!=1: continue
        out[i]=j
    return out

class Track:
    __slots__=("start","end","ybirths","ydeaths","xbirths","minNY","maxNY","first_ybirth",
               "first_ydeath","xbirth_steps","ybirth_steps","ydeath_steps","ended_reason","n_steps")
    def __init__(self,t):
        self.start=t; self.end=t; self.ybirths=0; self.ydeaths=0; self.xbirths=0
        self.minNY=10**9; self.maxNY=0; self.first_ybirth=None; self.first_ydeath=None
        self.xbirth_steps=[]; self.ybirth_steps=[]; self.ydeath_steps=[]
        self.ended_reason=None; self.n_steps=0

def analyse_world(ycells,ybirth,ydeath,xbirth,horizon):
    """Returns the list of identity intervals with their event content, and the world verdict."""
    per={}
    for r in ycells: per.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2]),int(r[3])))
    yb={}; yd={}; xb={}
    for r in ybirth: yb.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in ydeath: yd.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    for r in xbirth: xb.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    tracks=[]; prev_cens=None; prev_tracks={}
    for t in range(horizon):
        rows=per.get(t)
        if not rows:
            prev_cens=None; prev_tracks={}
            continue
        cells=[(y,x) for y,x,_ in rows]; nmap={(y,x):n for y,x,n in rows}
        gs=components(cells)
        cens=[centroid(cells,g) for g in gs]
        cellsets=[set(cells[i] for i in g) for g in gs]
        m=link(prev_cens,cens) if prev_cens is not None else {}
        newT={}
        for j in range(len(gs)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0] in prev_tracks:
                tk=prev_tracks[src[0]]
            else:
                tk=Track(t); tracks.append(tk)
            tk.end=t; tk.n_steps+=1
            S=cellsets[j]
            ny=sum(nmap[c] for c in S)
            tk.minNY=min(tk.minNY,ny); tk.maxNY=max(tk.maxNY,ny)
            for c,k in yb.get(t,()):
                if c in S:
                    tk.ybirths+=k; tk.ybirth_steps.append(t)
                    if tk.first_ybirth is None: tk.first_ybirth=t
            for c,k in yd.get(t,()):
                if c in S:
                    tk.ydeaths+=k; tk.ydeath_steps.append(t)
                    if tk.first_ydeath is None: tk.first_ydeath=t
            for c,k in xb.get(t,()):
                if c in S: tk.xbirths+=k; tk.xbirth_steps.append(t)
            newT[j]=tk
        prev_cens=cens; prev_tracks=newT
    out=[]
    for tk in tracks:
        cls="NO_TURNOVER"
        if tk.ybirths>0 and tk.ydeaths>0 and tk.minNY>=1:
            cls=("COMPLETE_BIRTH_THEN_DEATH" if tk.first_ybirth<tk.first_ydeath
                 else ("COMPLETE_DEATH_THEN_BIRTH" if tk.first_ydeath<tk.first_ybirth
                       else "COMPLETE_SAME_STEP"))
        elif tk.ybirths>0: cls="PARTIAL_BIRTH_ONLY"
        elif tk.ydeaths>0: cls="PARTIAL_DEATH_ONLY"
        functional=False; pre=post=0; dur=0
        if cls.startswith("COMPLETE"):
            fd=tk.first_ydeath
            pre=sum(1 for s in tk.xbirth_steps if s<fd)
            post=sum(1 for s in tk.xbirth_steps if s>fd)
            dur=tk.end-fd
            functional=bool(pre>0 and post>0 and dur>0)
        out.append({"start":tk.start,"end":tk.end,"n_steps":tk.n_steps,
          "y_births":tk.ybirths,"y_deaths":tk.ydeaths,"x_births":tk.xbirths,
          "minNY":tk.minNY if tk.minNY<10**9 else 0,"maxNY":tk.maxNY,
          "first_y_birth":tk.first_ybirth,"first_y_death":tk.first_ydeath,
          "class":cls,"x_birth_steps_before_removal":pre,"x_birth_steps_after_removal":post,
          "post_turnover_functional_duration":dur,"FUNCTIONAL":functional})
    return out

def world_verdict(intervals):
    comp=[i for i in intervals if i["class"].startswith("COMPLETE")]
    fun=[i for i in comp if i["FUNCTIONAL"]]
    return {"n_intervals":len(intervals),
            "n_complete":len(comp),"n_functional":len(fun),
            "COMPLETE_TURNOVER":len(comp)>0,"FUNCTIONAL_COMPLETE_TURNOVER":len(fun)>0,
            "birth_then_death":sum(1 for i in comp if i["class"]=="COMPLETE_BIRTH_THEN_DEATH"),
            "death_then_birth":sum(1 for i in comp if i["class"]=="COMPLETE_DEATH_THEN_BIRTH"),
            "same_step":sum(1 for i in comp if i["class"]=="COMPLETE_SAME_STEP"),
            "partial_birth_only":sum(1 for i in intervals if i["class"]=="PARTIAL_BIRTH_ONLY"),
            "partial_death_only":sum(1 for i in intervals if i["class"]=="PARTIAL_DEATH_ONLY"),
            "no_turnover":sum(1 for i in intervals if i["class"]=="NO_TURNOVER")}
