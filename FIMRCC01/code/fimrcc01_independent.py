"""FIMRCC01 Section 3 — the INDEPENDENT offline classifier.

It rebuilds every component, every centroid and every identity interval from the RAW PHYSICAL cell
rows alone: the step index, the cell coordinates and the per-cell Y occupancy. It never reads the
online component id `cid`, and it never reads the compressed component rows to decide anything
about structure.

ONE DECLARED DEPENDENCY, and it is physical, not structural: the local X disc mass `xd` cannot be
recomputed, because the narrow archive stores the X field only on Y-occupied cells and the frozen
gate sums X over an 81-cell disc most of which is not Y-occupied. `xd` is therefore READ from the
component rows and attached by matching (centroid, ncells, nY) — a physical match, never an id
match. If that match is not a bijection the world is reported as a disagreement.
"""
from __future__ import annotations
import numpy as np, math
import tlmr01_offline as OFF

L=OFF.L; CORE_R=OFF.CORE_R; R2=CORE_R*CORE_R
NEED=OFF.NEED; F_PRIMARY=OFF.F_PRIMARY; LATEST=OFF.LATEST_ALLOWED_TRIGGER

def components_from_cells(ys,xs):
    """toroidal single-linkage at CORE_R, from coordinates alone. Returns a list of index lists,
    each sorted, ordered by their smallest member — the convention fdot01_centres.components
    produces, reached by a different algorithm: label propagation to the per-row minimum over the
    adjacency edge list, instead of union-find. The relation closed is exactly
    `toroidal squared distance <= CORE_R**2`.

    Each label converges to the smallest index in its component, so ordering by label is ordering
    by smallest member, and a stable argsort leaves each group in ascending index order.
    `_components_reference` below is the same relation closed by an explicit union-find; the two
    are checked against each other on real archives in fimrcc01_precondition_b."""
    n=len(ys)
    if n==0: return []
    if n==1: return [[0]]
    dy=np.abs(ys[:,None]-ys[None,:]); dy=np.minimum(dy,L-dy)
    dx=np.abs(xs[:,None]-xs[None,:]); dx=np.minimum(dx,L-dx)
    adj=(dy*dy+dx*dx)<=R2                      # symmetric, includes the diagonal
    ii,jj=np.nonzero(adj); st=np.searchsorted(ii,np.arange(n))
    lab=np.arange(n)
    while True:
        new=np.minimum.reduceat(lab[jj],st)
        while True:                            # full pointer compression: new[k] <= k always
            nn=new[new]
            if np.array_equal(nn,new): break
            new=nn
        if np.array_equal(new,lab): break
        lab=new
    o=np.argsort(lab,kind="stable"); sl=lab[o]
    return [g.tolist() for g in np.split(o,np.flatnonzero(np.diff(sl))+1)]

def _components_reference(ys,xs):
    """the same relation closed by an explicit union-find over every adjacent pair — the slow,
    obviously-correct formulation the fast path is checked against on real archives."""
    n=len(ys)
    if n==0: return []
    if n==1: return [[0]]
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    ys=[int(v) for v in ys]; xs=[int(v) for v in xs]
    for i in range(n):
        for j in range(i+1,n):
            dy=abs(ys[i]-ys[j]); dy=min(dy,L-dy); dx=abs(xs[i]-xs[j]); dx=min(dx,L-dx)
            if dy*dy+dx*dx<=R2:
                a,b=f(i),f(j)
                if a!=b: par[a]=b
    g={}
    for i in range(n): g.setdefault(f(i),[]).append(i)
    return [sorted(v) for _,v in sorted(g.items(),key=lambda kv:min(kv[1]))]

def centroid(cells,idxs):
    """fdot01_centres.centroid, rewritten: anchor on the FIRST member, wrap offsets to [-L/2,L/2).
    Summation order is the index order, identical to the parent's list comprehension."""
    a0=cells[idxs[0]]
    oy=[((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in idxs]
    ox=[((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in idxs]
    return ((a0[0]+sum(oy)/len(oy))%L,(a0[1]+sum(ox)/len(ox))%L)

def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def link(prev,cur):
    if not prev or not cur: return {}
    fwd={i:[j for j,c in enumerate(cur) if tdist(p,c)<=CORE_R] for i,p in enumerate(prev)}
    bwd={j:[i for i,p in enumerate(prev) if tdist(p,c)<=CORE_R] for j,c in enumerate(cur)}
    return {i:js[0] for i,js in fwd.items() if len(js)==1 and len(bwd[js[0]])==1}

class Independent:
    """the whole classifier, built from cell rows only."""
    def __init__(self,A):
        self.T=A.T; self.integrity_ok=A.integrity_ok
        self.nYworld=A.nY                       # world Y total, a physical scalar from s
        self.cellsets={}; self.comp={}          # t -> [ {cells,cy,cx,nY} ]
        self.xd_match_ok=True; self.xd_mismatch_steps=[]
        for t in range(self.T):
            rows=A.cells.get(t)
            if not rows: continue
            cells=[(r[0],r[1]) for r in rows]; occ=[r[2] for r in rows]
            ys=np.array([c[0] for c in cells]); xs=np.array([c[1] for c in cells])
            gs=components_from_cells(ys,xs)
            cl=[]
            for g in gs:
                cy,cx=centroid(cells,g)
                cl.append({"idx":g,"cells":set(cells[i] for i in g),"cy":cy,"cx":cx,
                           "ncells":len(g),"nY":int(sum(occ[i] for i in g)),"xd":None})
            self.comp[t]=cl
        self._attach_xd(A)
    def _attach_xd(self,A):
        """physical match to the archive's component rows on (centroid, ncells, nY). No id is used."""
        for t,cl in self.comp.items():
            rows=A.comps.get(t,[])
            used=set()
            for c in cl:
                hit=[k for k,d in enumerate(rows) if k not in used and d["ncells"]==c["ncells"]
                     and d["nY"]==c["nY"] and abs(d["cy"]-c["cy"])<1e-9 and abs(d["cx"]-c["cx"])<1e-9]
                if len(hit)==1:
                    c["xd"]=int(rows[hit[0]]["xd"]); used.add(hit[0])
                else:
                    self.xd_match_ok=False; self.xd_mismatch_steps.append(t); c["xd"]=None
    def ncen(self,t): return len(self.comp.get(t,[]))
    def cens(self,t): return [(c["cy"],c["cx"]) for c in self.comp.get(t,[])]
    def states(self):
        return [OFF.state_of(int(self.nYworld[t]),self.ncen(t),self.integrity_ok) for t in range(self.T)]

def episodes(I):
    st=I.states(); out=[]; i=0
    while i<I.T:
        if st[i]!="S": i+=1; continue
        j=i
        while j+1<I.T and st[j+1]=="S": j+=1
        n=int(I.nYworld[i]); ln=j-i+1
        if j+1>=I.T: term="REACHED_THE_WINDOW_HORIZON"
        else:
            term={"E":"Y_EXTINCT","P":"FORMED_A_THIRD_CENTRE","O":"LOST_A_CENTRE_TO_A_SINGLE_Y",
                  "C":"MERGED_TO_ONE_CENTRE","F":"INTEGRITY_FAULT"}.get(st[j+1],"UNCLASSIFIED")
        amb=0
        for t in range(i,j):
            if len(link(I.cens(t),I.cens(t+1)))!=2: amb+=1
        matured=ln>=NEED; cand=(i+NEED-1) if matured else None
        e={"start":i,"end":j,"length":ln,"n_at_separation":n,"terminator":term,
           "interior_ambiguous_steps":amb,"IDENTITY_AMBIGUOUS":amb>0,
           "MATURED":bool(matured),"candidate_step":cand}
        if matured:
            cl=I.comp.get(cand,[]); xd=[c["xd"] for c in cl]
            r=OFF.f5_ratio([v for v in xd if v is not None]) if all(v is not None for v in xd) else None
            e.update({"candidate_ncen":len(cl),"candidate_x_disc":xd,"candidate_f5_ratio":r,
                      "GATE_deadline":bool(cand<=LATEST),
                      "GATE_exactly_two_centres":bool(len(cl)==2),
                      "GATE_local_x_ratio":bool(r is not None and r>=F_PRIMARY),
                      "TRIGGERS":bool(cand<=LATEST and len(cl)==2 and r is not None and r>=F_PRIMARY)})
        out.append(e); i=j+1
    return out

def M2(eps):
    by={}
    for e in eps:
        n=e["n_at_separation"]; d=by.setdefault(n,{"episodes":0,"matured":0,"terminators":{}})
        d["episodes"]+=1; d["matured"]+=int(e["MATURED"])
        d["terminators"][e["terminator"]]=d["terminators"].get(e["terminator"],0)+1
    return by

def M3(eps):
    m=[e for e in eps if e["MATURED"]]; fired=[e for e in m if e["TRIGGERS"]]
    return {"n_matured":len(m),"n_triggered":len(fired),
            "failure_modes":{"deadline":sum(1 for e in m if not e["GATE_deadline"]),
                             "not_exactly_two_centres":sum(1 for e in m if not e["GATE_exactly_two_centres"]),
                             "local_x_ratio":sum(1 for e in m if not e["GATE_local_x_ratio"])},
            "first_trigger_step":min([e["candidate_step"] for e in fired],default=None),
            "candidate_steps":[e["candidate_step"] for e in m]}

def identity_intervals(I,A):
    """the frozen interval construction, over the INDEPENDENT components and their own cell sets."""
    yb={}; yd={}; xb={}
    for arr,d in ((A.ybirth,yb),(A.ydeath,yd),(A.xbirth,xb)):
        for r in arr: d.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    nxt=0; prev_c=None; prev_ids=[]; ev={}; trace={}
    for t in range(I.T):
        cl=I.comp.get(t)
        if not cl: prev_c=None; prev_ids=[]; continue
        cens=[(c["cy"],c["cx"]) for c in cl]
        m=link(prev_c,cens) if prev_c is not None else {}
        ids=[]
        for j in range(len(cl)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0]<len(prev_ids): i=prev_ids[src[0]]
            else:
                i=nxt; nxt+=1
                ev[i]={"start":t,"end":t,"ybirth":[],"ydeath":[],"xbirth":[],"minNY":10**9,"steps":0}
            ids.append(i); e=ev[i]; e["end"]=t; e["steps"]+=1
            S=cl[j]["cells"]; e["minNY"]=min(e["minNY"],cl[j]["nY"])
            for c,k in yb.get(t,()):
                if c in S: e["ybirth"].append(t)
            for c,k in yd.get(t,()):
                if c in S: e["ydeath"].append(t)
            for c,k in xb.get(t,()):
                if c in S: e["xbirth"].append(t)
        trace[t]=list(ids); prev_c=cens; prev_ids=ids
    return ev,trace

def M5(I,A,eps):
    m3=M3(eps); iv=A.meta.get("intervention",{})
    C=bool(iv.get("applied")); D=[]; ev=None; trace=None
    if C:
        ev,trace=identity_intervals(I,A)
        D=OFF.turnover_in(ev,int(iv["step"]))
    return ({"A_maturation_reached":m3["n_matured"]>0,"B_trigger_fired":m3["n_triggered"]>0,
             "C_selective_removal_applied":C,
             "D_post_removal_functional_complete_turnover":any(d["FUNCTIONAL"] for d in D),
             "n_post_removal_complete_intervals":len(D),
             "n_post_removal_functional_intervals":sum(1 for d in D if d["FUNCTIONAL"]),
             "INTEGRATED":bool(m3["n_matured"]>0 and m3["n_triggered"]>0 and C and
                               any(d["FUNCTIONAL"] for d in D))},ev,trace)
