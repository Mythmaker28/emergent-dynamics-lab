"""FLRS02 §5+§6 — CHECKER A. World re-scoring by scalar-state sequence + field X response.

Independent implementation 1 of 2. Shares raw inputs and the frozen observable
definition with checker B, but no calculation code.
"""
from __future__ import annotations
import json, glob, math, os, sys
import numpy as np, yaml

REPO="/home/claude/edl"; RAW="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FLRS02/out"
C=json.load(open(f"{OUT}/FLRS02_FUNCTIONAL_CRITERION.json"))
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); CORE_R=float(P["analytic"]["core_radius_cells"])
BAND=C["MANDATORY_SENSITIVITY_BAND"]
TKEYS=["T_50","T_primary","T_80","T_90"]
FRAC={"T_50":0.50,"T_primary":1.0-1.0/math.e,"T_80":0.80,"T_90":0.90}

ii=np.arange(L); mi=np.minimum(ii,L-ii)
def torus_disc(cy,cx):
    dy=np.minimum(np.abs(ii-cy),L-np.abs(ii-cy))
    dx=np.minimum(np.abs(ii-cx),L-np.abs(ii-cx))
    return (dy[:,None]**2+dx[None,:]**2)<=CORE_R*CORE_R

def state_seq(NY,NC,integrity_ok):
    out=[]
    for i in range(len(NY)):
        if not integrity_ok: out.append("F"); continue
        if NY[i]==0: out.append("E")
        elif NC[i]>=3: out.append("P")
        elif NY[i]==1: out.append("O")
        else: out.append("S" if NC[i]==2 else "C")
    return out

def episodes(seq,mark="S"):
    ep=[]; t0=None
    for i,s in enumerate(seq):
        if s==mark and t0 is None: t0=i
        elif s!=mark and t0 is not None: ep.append((t0,i-1)); t0=None
    if t0 is not None: ep.append((t0,len(seq)-1))
    return ep

def xfield_plane(z,lo,hi):
    """Reconstruct ONLY the X plane on [lo,hi] inclusive."""
    f0=z["field0"][0].astype(np.int32)
    dd=z["field_delta"][:,0]
    if hi<=0: return {0:f0}
    cs=np.cumsum(dd[:hi].astype(np.int32),axis=0)
    return {"base":f0,"cs":cs,"lo":lo,"hi":hi}

def x_at(Xd,t):
    if t==0: return Xd["base"]
    return Xd["base"]+Xd["cs"][t-1]

def centres_of_step(yc_by_t,t):
    """Toroidal single-linkage over Y-occupied cells; returns list of (cy,cx,cells)."""
    pts=yc_by_t.get(t)
    if not pts: return []
    n=len(pts); P_=np.array([(p[0],p[1]) for p in pts],float)
    dy=np.abs(P_[:,0][:,None]-P_[:,0][None,:]); dy=np.minimum(dy,L-dy)
    dx=np.abs(P_[:,1][:,None]-P_[:,1][None,:]); dx=np.minimum(dx,L-dx)
    D=np.sqrt(dy**2+dx**2); adj=D<=CORE_R
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        for j in range(i+1,n):
            if adj[i,j]:
                a,b=f(i),f(j)
                if a!=b: par[a]=b
    grp={}
    for i in range(n): grp.setdefault(f(i),[]).append(i)
    res=[]
    for _,idxs in grp.items():
        # toroidal centroid via circular mean, anchored on the first member
        a0=P_[idxs[0]]
        oy=((P_[idxs,0]-a0[0]+L/2)%L)-L/2
        ox=((P_[idxs,1]-a0[1]+L/2)%L)-L/2
        cy=(a0[0]+oy.mean())%L; cx=(a0[1]+ox.mean())%L
        res.append((cy,cx,[pts[i] for i in idxs]))
    return res

def score(path):
    z=np.load(path,allow_pickle=True); m=json.loads(str(z["meta"][0]))
    sc=z["scalars"]; nm=[str(s) for s in z["scalar_names"]]
    NY=sc[:,nm.index("N_Y")].astype(int); NC=sc[:,nm.index("n_centres")].astype(int)
    yb=z["ybirth"]; T=sc.shape[0]
    integ = m["stop"]!="INTEGRITY_FAILURE"
    seq=state_seq(NY,NC,integ)
    eps=episodes(seq,"S")
    first_birth=int(yb[:,0].min()) if yb.size else -1
    n_births=int(yb[:,3].sum()) if yb.size else 0
    firstP=next((i for i,s in enumerate(seq) if s=="P"),-1)
    firstS=eps[0][0] if eps else -1
    extinct=(seq[-1]=="E")
    row={"world":m["tag"],"point":m["point"],"split":m["split"],"stop":m["stop"],
         "kY":m["kY"],"muY":m["muY"],"steps":T,
         "first_birth":first_birth,"n_births":n_births,"extinct":bool(extinct),
         "first_S":firstS,"first_P":firstP,"n_S_episodes":len(eps),
         "max_S_duration":max((b-a+1 for a,b in eps),default=0),
         "integrity_ok":bool(integ)}
    # ---- functional evaluation per response fraction ----
    yc=np.asarray(z["ycells"])
    need = bool(eps) and any((b-a+1)>=min(BAND[k] for k in TKEYS) for a,b in eps)
    yc_by_t={}
    if need:
        for r in yc:
            yc_by_t.setdefault(int(r[0]),[]).append((int(r[1]),int(r[2])))
        hi=max(b for a,b in eps)
        Xd=xfield_plane(z,0,min(hi+1,T-1))
    for k in TKEYS:
        Tf=BAND[k]; need_steps=int(math.ceil(Tf))
        f_req=FRAC[k]
        ok_dur=False; ok_noP=False; ok_resp=False
        first_ratio=None; first_ev=-1; first_pin=None; first_abs=None
        for (a,b) in eps:
            if (b-a+1)<need_steps: continue
            e=a+need_steps-1
            p_in = any(seq[i]=="P" for i in range(a,e+1))
            ratio=None; absw=None
            cs=centres_of_step(yc_by_t,e) if need else []
            if len(cs)==2:
                X=x_at(Xd,e)
                vals=[]
                for (cy,cx,_) in cs:
                    dmask=torus_disc(int(round(cy))%L,int(round(cx))%L)
                    vals.append(float(X[dmask].sum()))
                mx=max(vals); ratio=(min(vals)/mx) if mx>0 else 0.0; absw=min(vals)
            if first_ev<0:                      # FIRST qualifying episode, never outcome-selected
                first_ratio, first_ev, first_pin, first_abs = ratio, e, p_in, absw
            ok_dur=True
            if not p_in: ok_noP=True
            if (ratio is not None) and (ratio>=f_req) and (not p_in): ok_resp=True
        row[f"dur_ok_{k}"]=bool(ok_dur)
        row[f"noP_ok_{k}"]=bool(ok_noP)
        row[f"resp_ok_{k}"]=bool(ok_resp)
        row[f"event_step_{k}"]=int(first_ev)
        row[f"weak_centre_X_ratio_{k}"]=first_ratio
        row[f"weak_centre_X_abs_{k}"]=first_abs
        row[f"P_before_event_{k}"]=first_pin
        row[f"joint_timing_{k}"]=bool(n_births>=1 and ok_dur and ok_noP and integ)
        row[f"joint_{k}"]=bool(n_births>=1 and ok_dur and ok_noP and ok_resp and integ)
    z.close()
    return row

if __name__=="__main__":
    rows=[score(p) for p in sorted(glob.glob(f"{RAW}/*.npz"))]
    json.dump(rows,open(f"{OUT}/_checkerA.json","w"),indent=1)
    import collections
    for pt in ("A0","B1","B2"):
        R=[r for r in rows if r["point"]==pt]
        print("%s n=%d births>=1:%d extinct:%d reachedS:%d reachedP:%d maxSdur=%d"%(
            pt,len(R),sum(r["n_births"]>=1 for r in R),sum(r["extinct"] for r in R),
            sum(r["first_S"]>=0 for r in R),sum(r["first_P"]>=0 for r in R),
            max((r["max_S_duration"] for r in R),default=0)))
        for k in TKEYS:
            print("    %-10s dur=%d noP=%d resp=%d joint_timing=%d joint=%d"%(k,
                sum(r[f"dur_ok_{k}"] for r in R),sum(r[f"noP_ok_{k}"] for r in R),
                sum(r[f"resp_ok_{k}"] for r in R),sum(r[f"joint_timing_{k}"] for r in R),
                sum(r[f"joint_{k}"] for r in R)))
