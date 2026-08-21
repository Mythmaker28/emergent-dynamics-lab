"""RCD01 §15 — IMPLEMENTATION B, independent of A. BFS components, complex circular centroid,
per-event partial sum of the X plane, distance-table aggregation, its own binomial bound call.
It imports neither rcd01_audit_A nor fdflt01_endpoint."""
from __future__ import annotations
import json, math, os, sys
import numpy as np, yaml
from collections import deque
from scipy.stats import binom
REPO="/home/claude/edl"; RAW="/home/claude/FDFLT01/raw"; OUT=f"{REPO}/RCD01/out"
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
LL=int(P["point"]["L"]); RC=float(P["analytic"]["core_radius_cells"]); MU=float(P["point"]["muX"])
NEED=int(math.ceil(math.log(1.0-(1.0-1.0/math.e))/math.log(1.0-MU)))   # = 250, recomputed
DELTA=NEED-1; SURV=(1.0-MU)**DELTA
_a=np.arange(LL); _t=np.abs(_a[:,None]-_a[None,:]); DT=np.minimum(_t,LL-_t).astype(float)
def pd_(p,q): return math.hypot(DT[p[0],q[0]],DT[p[1],q[1]])
def comps(cells):
    n=len(cells); seen=[False]*n; out=[]
    for s in range(n):
        if seen[s]: continue
        seen[s]=True; Q=deque([s]); g=[s]
        while Q:
            u=Q.popleft()
            for v in range(n):
                if not seen[v] and pd_(cells[u],cells[v])<=RC:
                    seen[v]=True; Q.append(v); g.append(v)
        out.append(g)
    return out
def cen(cells,idx):
    w=2.0*math.pi/LL
    zy=np.mean([complex(math.cos(w*cells[i][0]),math.sin(w*cells[i][0])) for i in idx])
    zx=np.mean([complex(math.cos(w*cells[i][1]),math.sin(w*cells[i][1])) for i in idx])
    return (math.atan2(zy.imag,zy.real)/w)%LL,(math.atan2(zx.imag,zx.real)/w)%LL
def cdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,LL-dy); dx=abs(a[1]-b[1]); dx=min(dx,LL-dx)
    return math.hypot(dy,dx)
def lx(X,c):
    iy,ix=int(round(c[0]))%LL,int(round(c[1]))%LL
    return float(X[(DT[iy][:,None]**2+DT[ix][None,:]**2)<=RC*RC].sum())
def xplane(z,t):
    b=z["field0"][0].astype(np.int64)
    return b if t==0 else b+z["field_delta"][:t,0].astype(np.int64).sum(axis=0)
def sup(N0): return 0 if N0<=0 else int(binom.ppf(0.95,N0,SURV))
def runs(mask):
    m=np.concatenate(([False],mask,[False])); d=np.diff(m.astype(np.int8))
    return list(zip(np.flatnonzero(d==1).tolist(),(np.flatnonzero(d==-1)-1).tolist()))

def audit(path):
    z=np.load(path,allow_pickle=True); m=json.loads(str(z["meta"][0]))
    sc=z["scalars"]; nm=[str(s) for s in z["scalar_names"]]
    ny=sc[:,nm.index("N_Y")].astype(np.int64); nc=sc[:,nm.index("n_centres")].astype(np.int64)
    nx=sc[:,nm.index("N_X")].astype(np.int64)
    integ=(m["stop"]!="INTEGRITY_FAILURE")
    st=np.full(ny.shape,5,np.int8) if not integ else np.select([ny==0,nc>=3,ny==1,nc==2],[0,4,1,3],default=2).astype(np.int8)
    S=runs(st==3); Pm=(st==4)
    fP=int(np.flatnonzero(Pm)[0]) if Pm.any() else -1
    yc=np.asarray(z["ycells"]); by={}
    for r_ in yc: by.setdefault(int(r_[0]),[]).append((int(r_[1]),int(r_[2])))
    out={"world":m["tag"],"first_P":fP,"extinct":bool(st[-1]==0),
         "max_S_duration":max((b-a+1 for a,b in S),default=0),
         "R0_functional_success":False,"R1_material":None,"N0_total_X":None,
         "daughter_mass":None,"parent_mass":None,"survivor_upper_95":None,
         "t0_separation":None,"t_maturation":None,"daughter_is_weaker":None,
         "third_centre_cell":None,"closest_existing_centre":None,"closest_distance":None}
    nb=int(z["ybirth"][:,3].sum()) if z["ybirth"].size else 0
    q=[(a,b) for a,b in S if (b-a+1)>=NEED]
    if q:
        # the frozen FDFLT01 rule accepts ANY qualifying episode, not only the first
        resp=False
        for (aa,bb) in q:
            ee=aa+NEED-1
            if bool(Pm[aa:ee+1].any()): continue
            cc=by.get(ee,[]); gg=comps(cc)
            if len(gg)!=2: continue
            Xq=xplane(z,ee); vq=[lx(Xq,cen(cc,g)) for g in gg]
            hq=max(vq); rq=(min(vq)/hq) if hq>0 else 0.0
            if rq>=(1.0-1.0/math.e): resp=True; break
        out["R0_functional_success"]=bool(nb>=1 and integ and resp)
        # provenance is evaluated on the FIRST qualifying episode, as implementation A does
        a,b=q[0]; e=a+NEED-1
        c0=by.get(a,[]); g0=comps(c0); prev=by.get(a-1,[]) if a>0 else []
        cE=by.get(e,[]); gE=comps(cE)
        if len(g0)==2 and len(gE)==2 and prev:
            cp=cen(prev,list(range(len(prev))))
            k0=[cen(c0,g) for g in g0]
            pi=0 if cdist(k0[0],cp)<=cdist(k0[1],cp) else 1
            di=1-pi
            # forward match by overlap then centroid distance
            s0=[set(c0[i] for i in g) for g in g0]; sE=[set(cE[i] for i in g) for g in gE]
            kE=[cen(cE,g) for g in gE]
            cand=sorted([(-len(sE[j]&s0[i]),cdist(kE[j],k0[i]),j,i) for j in range(len(gE)) for i in range(len(g0))])
            up,uc,mp=set(),set(),{}
            for _o,_d,j,i in cand:
                if j in uc or i in up: continue
                uc.add(j); up.add(i); mp[j]=i
            dj=[j for j,i in mp.items() if i==di]; pj=[j for j,i in mp.items() if i==pi]
            if len(dj)==1 and len(pj)==1:
                X=xplane(z,e)
                Dm=lx(X,kE[dj[0]]); Pmass=lx(X,kE[pj[0]]); N0=int(nx[a]); su=sup(N0)
                out.update({"t0_separation":a,"t_maturation":e,"N0_total_X":N0,
                  "daughter_mass":Dm,"parent_mass":Pmass,"survivor_upper_95":su,
                  "R1_material":bool(Dm>su),"daughter_is_weaker":bool(Dm<=Pmass)})
    if fP>=0:
        cP=by.get(fP,[]); gP=comps(cP); pv=by.get(fP-1,[]) if fP>0 else []
        gpv=comps(pv) if pv else []
        if len(gP)>=3 and gpv:
            sP=[set(cP[i] for i in g) for g in gP]; spv=[set(pv[i] for i in g) for g in gpv]
            kP=[cen(cP,g) for g in gP]; kpv=[cen(pv,g) for g in gpv]
            cand=sorted([(-len(sP[j]&spv[i]),cdist(kP[j],kpv[i]),j,i) for j in range(len(gP)) for i in range(len(gpv))])
            up,uc,mp=set(),set(),{}
            for _o,_d,j,i in cand:
                if j in uc or i in up: continue
                uc.add(j); up.add(i); mp[j]=i
            new=[j for j in range(len(gP)) if j not in mp]
            if len(new)==1:
                cn=kP[new[0]]
                oth=sorted([(cdist(cn,kP[k]),k) for k in range(len(gP)) if k!=new[0]])
                out["third_centre_cell"]=[int(round(cn[0]))%LL,int(round(cn[1]))%LL]
                out["closest_existing_centre"]=int(oth[0][1]); out["closest_distance"]=round(oth[0][0],4)
    z.close(); return out

if __name__=="__main__":
    SM=json.load(open(f"{REPO}/FDFLT01/out/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]["PRIMARY"]
    rows=[audit(os.path.join(RAW,"F_B1_i%03d_s%d.npz"%(s["index"],s["seed"]))) for s in SM]
    json.dump(rows,open(f"{OUT}/_auditB.json","w"),indent=1)
    R0=[r for r in rows if r["R0_functional_success"]]
    print("B: worlds=%d R0=%d R1=%d reachedP=%d NEED=%d SURV=%.10f"%(
      len(rows),len(R0),sum(1 for r in R0 if r["R1_material"]),
      sum(1 for r in rows if r["first_P"]>=0),NEED,SURV))
