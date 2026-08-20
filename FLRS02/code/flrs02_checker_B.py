"""FLRS02 §14 — CHECKER B. Independent implementation 2 of 2.

Shares raw inputs and the frozen observable definitions with checker A; shares no
calculation code. State sequence: vectorised np.select. Episodes: np.diff on a mask.
Components: BFS queue. Centroid: complex circular mean. X plane: direct partial sum
per event step. Local X: precomputed toroidal distance table.
"""
from __future__ import annotations
import json, glob, math
import numpy as np, yaml
from collections import deque

REPO="/home/claude/edl"; RAW="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FLRS02/out"
CR=json.load(open(f"{OUT}/FLRS02_FUNCTIONAL_CRITERION.json"))
PR=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
LL=int(PR["point"]["L"]); RCORE=float(PR["analytic"]["core_radius_cells"])
BAND=CR["MANDATORY_SENSITIVITY_BAND"]
KEYS=("T_50","T_primary","T_80","T_90")
FREQ={"T_50":0.50,"T_primary":1.0-1.0/math.e,"T_80":0.80,"T_90":0.90}

# precomputed toroidal distance table between every pair of lattice coordinates
_a=np.arange(LL); _d=np.abs(_a[:,None]-_a[None,:]); _d=np.minimum(_d,LL-_d)
DTAB=_d.astype(np.float64)                                    # DTAB[i,j] = 1-D toroidal distance
def pair_dist(p,q_):
    return math.hypot(DTAB[p[0],q_[0]], DTAB[p[1],q_[1]])

def classify_vec(ny,nc,integrity):
    """Vectorised state assignment. 0=E 1=O 2=C 3=S 4=P 5=F"""
    if not integrity: return np.full(ny.shape,5,dtype=np.int8)
    return np.select(
        [ny==0, nc>=3, ny==1, nc==2],
        [0,     4,     1,     3],
        default=2).astype(np.int8)

def runs_of(mask):
    """Maximal runs of True via edge differences."""
    m=np.concatenate(([False],mask,[False]))
    d=np.diff(m.astype(np.int8))
    st=np.flatnonzero(d==1); en=np.flatnonzero(d==-1)-1
    return list(zip(st.tolist(),en.tolist()))

def components_bfs(cells):
    """BFS connected components with adjacency = toroidal distance <= RCORE."""
    n=len(cells); seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        seen[s]=True; Q=deque([s]); grp=[s]
        while Q:
            u=Q.popleft()
            for v in range(n):
                if not seen[v] and pair_dist(cells[u],cells[v])<=RCORE:
                    seen[v]=True; Q.append(v); grp.append(v)
        comps.append(grp)
    return comps

def centroid_circular(cells,idxs):
    """Circular mean via complex exponentials."""
    w=2.0*math.pi/LL
    zy=np.mean([complex(math.cos(w*cells[i][0]),math.sin(w*cells[i][0])) for i in idxs])
    zx=np.mean([complex(math.cos(w*cells[i][1]),math.sin(w*cells[i][1])) for i in idxs])
    cy=(math.atan2(zy.imag,zy.real)/w)%LL; cx=(math.atan2(zx.imag,zx.real)/w)%LL
    return cy,cx

def x_plane_at(z,t):
    """Direct partial sum of the X deltas up to t. No cumulative array is retained."""
    base=z["field0"][0].astype(np.int64)
    if t==0: return base
    return base+z["field_delta"][:t,0].astype(np.int64).sum(axis=0)

def local_x(X,cy,cx):
    iy=int(round(cy))%LL; ix=int(round(cx))%LL
    sel=(DTAB[iy][:,None]**2 + DTAB[ix][None,:]**2)<=RCORE*RCORE
    return float(X[sel].sum())

def score(path):
    z=np.load(path,allow_pickle=True); m=json.loads(str(z["meta"][0]))
    sc=z["scalars"]; nm=[str(s) for s in z["scalar_names"]]
    ny=sc[:,nm.index("N_Y")].astype(np.int64); nc=sc[:,nm.index("n_centres")].astype(np.int64)
    integ=(m["stop"]!="INTEGRITY_FAILURE")
    st=classify_vec(ny,nc,integ)
    Sruns=runs_of(st==3); Pmask=(st==4)
    yb=z["ybirth"]
    fb=int(yb[:,0].min()) if yb.size else -1
    nbr=int(yb[:,3].sum()) if yb.size else 0
    fP=int(np.flatnonzero(Pmask)[0]) if Pmask.any() else -1
    row={"world":m["tag"],"point":m["point"],"stop":m["stop"],"steps":int(sc.shape[0]),
         "first_birth":fb,"n_births":nbr,"extinct":bool(st[-1]==0),
         "first_S":(Sruns[0][0] if Sruns else -1),"first_P":fP,
         "n_S_episodes":len(Sruns),
         "max_S_duration":max((b-a+1 for a,b in Sruns),default=0),
         "integrity_ok":bool(integ)}
    yc=np.asarray(z["ycells"])
    for k in KEYS:
        need=int(math.ceil(BAND[k])); fr=FREQ[k]
        dur=False; noP=False; resp=False
        r0=None; e0=-1; p0=None
        for (a,b) in Sruns:
            if (b-a+1)<need: continue
            e=a+need-1
            pin=bool(Pmask[a:e+1].any())
            ratio=None
            sub=yc[yc[:,0]==e]
            cells=[(int(r[1]),int(r[2])) for r in sub]
            if cells:
                comps=components_bfs(cells)
                if len(comps)==2:
                    X=x_plane_at(z,e)
                    v=[local_x(X,*centroid_circular(cells,g)) for g in comps]
                    hi=max(v); ratio=(min(v)/hi) if hi>0 else 0.0
            if e0<0: r0,e0,p0=ratio,e,pin
            dur=True
            if not pin: noP=True
            if (ratio is not None) and (ratio>=fr) and (not pin): resp=True
        row[f"dur_ok_{k}"]=dur; row[f"noP_ok_{k}"]=noP; row[f"resp_ok_{k}"]=resp
        row[f"event_step_{k}"]=int(e0); row[f"weak_centre_X_ratio_{k}"]=r0
        row[f"P_before_event_{k}"]=p0
        row[f"joint_timing_{k}"]=bool(nbr>=1 and dur and noP and integ)
        row[f"joint_{k}"]=bool(nbr>=1 and dur and noP and resp and integ)
    z.close()
    return row

if __name__=="__main__":
    rows=[score(p) for p in sorted(glob.glob(f"{RAW}/*.npz"))]
    json.dump(rows,open(f"{OUT}/_checkerB.json","w"),indent=1)
    for pt in ("A0","B1","B2"):
        R=[r for r in rows if r["point"]==pt]
        print(pt,"n=%d S=%d P=%d"%(len(R),sum(r["first_S"]>=0 for r in R),sum(r["first_P"]>=0 for r in R)),
              {k:sum(r[f"joint_{k}"] for r in R) for k in KEYS})
