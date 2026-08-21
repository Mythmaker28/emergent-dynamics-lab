"""RCD01 §7 + §8 — IMPLEMENTATION A. Parent/daughter identity, material provenance, third-centre
developmental analysis. Union-find components, anchored toroidal centroid, single cumsum X plane."""
from __future__ import annotations
import json, math, os, sys
import numpy as np, yaml
REPO="/home/claude/edl"; RAW="/home/claude/FDFLT01/raw"; OUT=f"{REPO}/RCD01/out"
sys.path.insert(0,f"{REPO}/FDFLT01/code"); sys.path.insert(0,f"{REPO}/RCD01/code")
import fdflt01_endpoint as E
import rcd01_provenance_criterion as PC
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); CORE_R=float(P["analytic"]["core_radius_cells"])
NEED=E.STEPS["T_primary"]
_ii=np.arange(L); _D1=np.minimum(np.abs(_ii[:,None]-_ii[None,:]),L-np.abs(_ii[:,None]-_ii[None,:])).astype(float)
def disc(cy,cx):
    iy,ix=int(round(cy))%L,int(round(cx))%L
    return (_D1[iy][:,None]**2+_D1[ix][None,:]**2)<=CORE_R*CORE_R
def tdist(a,b):
    dy=abs(a[0]-b[0]); dy=min(dy,L-dy); dx=abs(a[1]-b[1]); dx=min(dx,L-dx)
    return math.hypot(dy,dx)

def audit(path):
    z=np.load(path,allow_pickle=True); m=json.loads(str(z["meta"][0]))
    sc=z["scalars"]; nm=[str(s) for s in z["scalar_names"]]
    NY=sc[:,nm.index("N_Y")].astype(int); NC=sc[:,nm.index("n_centres")].astype(int)
    NXtot=sc[:,nm.index("N_X")].astype(int)
    yb=z["ybirth"]; integ=(m["stop"]!="INTEGRITY_FAILURE")
    seq=E.classify(NY,NC,integ); eps=E.s_episodes(seq)
    firstP=next((i for i,s in enumerate(seq) if s=="P"),-1)
    fb=int(yb[:,0].min()) if yb.size else -1
    r={"world":m["tag"],"seed":m["seed"],"stop":m["stop"],"steps":int(sc.shape[0]),
       "first_birth":fb,"n_births":int(yb[:,3].sum()) if yb.size else 0,
       "extinct":bool(seq[-1]=="E"),"first_P":firstP,"integrity_ok":bool(integ),
       "max_S_duration":max((b-a+1 for a,b in eps),default=0),"n_S_episodes":len(eps)}
    yc=np.asarray(z["ycells"]); by={}
    for row in yc: by.setdefault(int(row[0]),[]).append((int(row[1]),int(row[2])))
    qual=[(a,b) for a,b in eps if (b-a+1)>=NEED]
    r["R0_functional_success"]=False
    r.update({k:None for k in ("t0_separation","t_maturation","N0_total_X","parent_mass","daughter_mass",
        "survivor_upper_95","R1_material","f_new_lower","daughter_is_weaker","parent_centroid","daughter_centroid")})
    if qual:
        a,b=qual[0]; e=a+NEED-1
        cells0=by.get(a,[]); comps0=E.components(cells0)
        prev=by.get(a-1,[]) if a>0 else []
        if len(comps0)==2 and prev:
            cprev=E.centroid(prev,list(range(len(prev))))
            c0=[E.centroid(cells0,g) for g in comps0]
            pi=0 if tdist(c0[0],cprev)<=tdist(c0[1],cprev) else 1
            di=1-pi
            cellsE=by.get(e,[]); compsE=E.components(cellsE)
            if len(compsE)==2:
                mp=E.match_persistent(comps0,compsE,cells0,cellsE)
                # current index -> previous index; find which current comp maps to the daughter
                dcur=[j for j,v in mp.items() if v==di]
                pcur=[j for j,v in mp.items() if v==pi]
                if len(dcur)==1 and len(pcur)==1:
                    f0=z["field0"][0].astype(np.int32)
                    X=f0 if e==0 else f0+np.cumsum(z["field_delta"][:e,0].astype(np.int32),axis=0)[e-1]
                    cd=E.centroid(cellsE,compsE[dcur[0]]); cpar=E.centroid(cellsE,compsE[pcur[0]])
                    Dm=float(X[disc(*cd)].sum()); Pm=float(X[disc(*cpar)].sum())
                    N0=int(NXtot[a]); su=PC.survivor_upper(N0)
                    r.update({"t0_separation":a,"t_maturation":e,"N0_total_X":N0,
                      "parent_mass":Pm,"daughter_mass":Dm,"survivor_upper_95":su,
                      "R1_material":bool(Dm>su),"f_new_lower":PC.f_new_lower(Dm,N0),
                      "daughter_is_weaker":bool(Dm<=Pm),
                      "parent_centroid":[round(cpar[0],4),round(cpar[1],4)],
                      "daughter_centroid":[round(cd[0],4),round(cd[1],4)]})
        r["R0_functional_success"]=bool(E.score_world(path)["PRIMARY_SUCCESS"])
    # ---- §8 third-centre developmental analysis ----
    r.update({k:None for k in ("third_centre_cell","closest_existing_centre","closest_distance",
        "two_still_functional_at_P","third_matures","steps_after_P_available")})
    if firstP>=0:
        cellsP=by.get(firstP,[]); compsP=E.components(cellsP)
        prevc=by.get(firstP-1,[]) if firstP>0 else []
        compsPrev=E.components(prevc) if prevc else []
        if len(compsP)>=3 and compsPrev:
            mp=E.match_persistent(compsPrev,compsP,prevc,cellsP)
            new=[j for j,v in mp.items() if v is None]
            if len(new)==1:
                cn=E.centroid(cellsP,compsP[new[0]])
                others=[(tdist(cn,E.centroid(cellsP,g)),k) for k,g in enumerate(compsP) if k!=new[0]]
                others.sort()
                r["third_centre_cell"]=[int(round(cn[0]))%L,int(round(cn[1]))%L]
                r["closest_existing_centre"]=int(others[0][1]); r["closest_distance"]=round(others[0][0],4)
        r["two_still_functional_at_P"]=bool(r["t_maturation"] is not None and firstP>r["t_maturation"])
        r["steps_after_P_available"]=int(sc.shape[0]-1-firstP)
        r["third_matures"]=bool(r["steps_after_P_available"]>=NEED) if r["steps_after_P_available"] is not None else None
    z.close(); return r

if __name__=="__main__":
    SM=json.load(open(f"{REPO}/FDFLT01/out/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]["PRIMARY"]
    rows=[audit(os.path.join(RAW,"F_B1_i%03d_s%d.npz"%(s["index"],s["seed"]))) for s in SM]
    json.dump(rows,open(f"{OUT}/_auditA.json","w"),indent=1)
    R0=[r for r in rows if r["R0_functional_success"]]
    R1=[r for r in R0 if r["R1_material"]]
    print("worlds=%d  R0=%d  R1=%d  reachedP=%d"%(len(rows),len(R0),len(R1),sum(1 for r in rows if r["first_P"]>=0)))
    fn=[r["f_new_lower"] for r in R0 if r["f_new_lower"] is not None]
    if fn: print("certified lower bound on new fraction: median=%.4f min=%.4f max=%.4f n=%d"%(
        float(np.median(fn)),min(fn),max(fn),len(fn)))
    print("daughter is the weaker centre in %d of %d evaluated"%(
        sum(1 for r in R0 if r["daughter_is_weaker"]),sum(1 for r in R0 if r["daughter_is_weaker"] is not None)))
