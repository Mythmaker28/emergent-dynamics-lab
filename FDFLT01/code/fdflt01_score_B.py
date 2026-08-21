"""FDFLT01 — INDEPENDENT SCORER B. Shares raw inputs and the frozen definitions with the
endpoint module; shares no calculation code. Vectorised states, mask-diff episodes, BFS
components, complex circular centroid, per-event partial sum, distance-table aggregation."""
from __future__ import annotations
import json, math, os, sys
import numpy as np, yaml
from collections import deque

REPO="/home/claude/edl"
PROTO=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
LL=int(PROTO["point"]["L"]); RC=float(PROTO["analytic"]["core_radius_cells"]); MU=float(PROTO["point"]["muX"])
FP=1.0-1.0/math.e
FR={"T_50":0.50,"T_primary":FP,"T_80":0.80,"T_90":0.90}
BD={k:math.log(1.0-v)/math.log(1.0-MU) for k,v in FR.items()}
ST={k:int(math.ceil(v)) for k,v in BD.items()}
_a=np.arange(LL); _t=np.abs(_a[:,None]-_a[None,:]); DT=np.minimum(_t,LL-_t).astype(float)

def _cls(ny,nc,integ):
    if not integ: return np.full(ny.shape,5,np.int8)
    return np.select([ny==0,nc>=3,ny==1,nc==2],[0,4,1,3],default=2).astype(np.int8)
def _runs(mask):
    m=np.concatenate(([False],mask,[False])); d=np.diff(m.astype(np.int8))
    return list(zip(np.flatnonzero(d==1).tolist(),(np.flatnonzero(d==-1)-1).tolist()))
def _pd(p,q): return math.hypot(DT[p[0],q[0]],DT[p[1],q[1]])
def _comps(cells):
    n=len(cells); seen=[False]*n; out=[]
    for s in range(n):
        if seen[s]: continue
        seen[s]=True; Q=deque([s]); g=[s]
        while Q:
            u=Q.popleft()
            for v in range(n):
                if not seen[v] and _pd(cells[u],cells[v])<=RC:
                    seen[v]=True; Q.append(v); g.append(v)
        out.append(g)
    return out
def _cen(cells,idx):
    w=2.0*math.pi/LL
    zy=np.mean([complex(math.cos(w*cells[i][0]),math.sin(w*cells[i][0])) for i in idx])
    zx=np.mean([complex(math.cos(w*cells[i][1]),math.sin(w*cells[i][1])) for i in idx])
    return (math.atan2(zy.imag,zy.real)/w)%LL,(math.atan2(zx.imag,zx.real)/w)%LL
def _xat(z,t):
    b=z["field0"][0].astype(np.int64)
    return b if t==0 else b+z["field_delta"][:t,0].astype(np.int64).sum(axis=0)
def _lx(X,cy,cx):
    iy,ix=int(round(cy))%LL,int(round(cx))%LL
    return float(X[(DT[iy][:,None]**2+DT[ix][None,:]**2)<=RC*RC].sum())

def score_world(path):
    z=np.load(path,allow_pickle=True); m=json.loads(str(z["meta"][0]))
    sc=z["scalars"]; nm=[str(s) for s in z["scalar_names"]]
    ny=sc[:,nm.index("N_Y")].astype(np.int64); nc=sc[:,nm.index("n_centres")].astype(np.int64)
    integ=(m["stop"]!="INTEGRITY_FAILURE")
    st=_cls(ny,nc,integ); S=_runs(st==3); Pm=(st==4)
    yb=z["ybirth"]; nb=int(yb[:,3].sum()) if yb.size else 0
    row={"world":m["tag"],"seed":m["seed"],"stop":m["stop"],
         "first_S":(S[0][0] if S else -1),
         "first_P":(int(np.flatnonzero(Pm)[0]) if Pm.any() else -1),
         "extinct":bool(st[-1]==0),"n_births":nb,"integrity_ok":bool(integ),
         "n_S_episodes":len(S),"max_S_duration":max((b-a+1 for a,b in S),default=0)}
    yc=np.asarray(z["ycells"])
    for k in ST:
        need=ST[k]; fr=FR[k]; dur=noP=resp=False; r0=None; e0=-1; p0=None
        for (a,b) in S:
            if (b-a+1)<need: continue
            e=a+need-1; pin=bool(Pm[a:e+1].any()); ratio=None
            cells=[(int(r[1]),int(r[2])) for r in yc[yc[:,0]==e]]
            if cells:
                cs=_comps(cells)
                if len(cs)==2:
                    X=_xat(z,e); v=[_lx(X,*_cen(cells,g)) for g in cs]
                    hi=max(v); ratio=(min(v)/hi) if hi>0 else 0.0
            if e0<0: r0,e0,p0=ratio,e,pin
            dur=True
            if not pin: noP=True
            if (ratio is not None) and (ratio>=fr) and (not pin): resp=True
        row[f"dur_ok_{k}"]=dur; row[f"noP_ok_{k}"]=noP; row[f"resp_ok_{k}"]=resp
        row[f"event_step_{k}"]=int(e0); row[f"weak_centre_X_ratio_{k}"]=r0
        row[f"P_before_event_{k}"]=p0
        row[f"joint_timing_{k}"]=bool(nb>=1 and dur and noP and integ)
        row[f"PRIMARY_SUCCESS_{k}"]=bool(nb>=1 and dur and noP and resp and integ)
    row["PRIMARY_SUCCESS"]=row["PRIMARY_SUCCESS_T_primary"]
    z.close(); return row
