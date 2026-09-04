"""FMRT01 §9 — the four-level parent/daughter identity rule, deterministic including ties.

Reconstructed from the SPOIQ01 specification and re-tested here on the same synthetic cases,
including the exact tie geometry RCD01 discovered in world F_B1_i182_s961444860.
"""
from __future__ import annotations
import math
import numpy as np, yaml
P=yaml.safe_load(open("/home/claude/edl/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); CORE_R=float(P["analytic"]["core_radius_cells"])

def components(cells):
    n=len(cells)
    if n==0: return []
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        for j in range(i+1,n):
            dy=abs(cells[i][0]-cells[j][0]); dx=abs(cells[i][1]-cells[j][1])
            dy,dx=min(dy,L-dy),min(dx,L-dx)
            if (dy*dy+dx*dx)**0.5<=CORE_R:
                a,b=f(i),f(j)
                if a!=b: par[a]=b
    g={}
    for i in range(n): g.setdefault(f(i),[]).append(i)
    return [sorted(v) for _,v in sorted(g.items())]

def centroid(cells,idxs):
    a0=cells[idxs[0]]
    oy=[((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in idxs]
    ox=[((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in idxs]
    return (a0[0]+sum(oy)/len(oy))%L,(a0[1]+sum(ox)/len(ox))%L

def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def canonical(cells,idxs):
    pts=sorted((cells[i][0],cells[i][1]) for i in idxs)
    best=None
    for oy,ox in pts:
        rot=tuple(sorted(((y-oy)%L,(x-ox)%L) for y,x in pts))
        if best is None or rot<best: best=rot
    return best

def parent_daughter(prev_cells,cur_cells,occ=None):
    """Four levels: distance, overlap, Y occupancy, canonical representation."""
    comps=components(cur_cells)
    if len(comps)!=2 or not prev_cells: return None,None,None
    cprev=centroid(prev_cells,list(range(len(prev_cells))))
    d=[tdist(centroid(cur_cells,g),cprev) for g in comps]
    if d[0]!=d[1]:
        p=0 if d[0]<d[1] else 1
        return comps[p],comps[1-p],1
    ov=[len(set(cur_cells[i] for i in g) & set(prev_cells)) for g in comps]
    if ov[0]!=ov[1]:
        p=0 if ov[0]>ov[1] else 1
        return comps[p],comps[1-p],2
    if occ is not None:
        y=[sum(occ.get(cur_cells[i],1) for i in g) for g in comps]
        if y[0]!=y[1]:
            p=0 if y[0]>y[1] else 1
            return comps[p],comps[1-p],3
    c=[canonical(cur_cells,g) for g in comps]
    p=0 if c[0]<=c[1] else 1
    return comps[p],comps[1-p],4

def mask_for(cells,comp):
    m=np.zeros((L,L),bool)
    for i in comp: m[cells[i][0],cells[i][1]]=True
    return m

def disc_mask(cy,cx):
    ii=np.arange(L)
    dy=np.minimum(np.abs(ii-cy),L-np.abs(ii-cy)); dx=np.minimum(np.abs(ii-cx),L-np.abs(ii-cx))
    return (dy[:,None]**2+dx[None,:]**2)<=CORE_R*CORE_R
