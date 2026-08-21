"""FMRT01 — re-qualification of the reconstructed capability: UNARMED INERTNESS.

SPOIQ01 verified inertness against the 192 FDFLT01 archives. Those archives were destroyed
by the fifth container rollback and were never made durable, so that verification cannot be
repeated. This mission re-qualifies against the 88 surviving PQEC01 Phase-B archives, which
the same frozen engine and observer produced. The test is the same: run the capability-bearing
class UNARMED and require every stored array, every stop event and the final physical state
hash to match the frozen archive.
"""
from __future__ import annotations
import json, os, sys
import numpy as np
REPO="/home/claude/edl"; RAW="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FMRT01/out"
for _p in (f"{REPO}/FMRT01/code", f"{REPO}/PQEC01/code", "/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O
import fmrt01_engine as FE
O.PQECWorld = FE.FMRTWorld
import pqec01_run as PR

FREEZE=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
C=FREEZE["INHERITED_FROZEN_CONSTANTS"]
T_HORIZON=C["T_HORIZON"]; N_STAR=int(C["N_STAR"]); SCALARS=PR.SCALARS
ARRAYS=("field0","field_delta","scalars","ycells","ybirth","ydeath","yhop","xevent",
        "capacity","exchange","src","final")

def check(job):
    tag,seed,kY,muY=job
    try:
        w,_,sp=O.build_world(seed,kY,muY,L=None,horizon=T_HORIZON,instrumented=True)
        w.fmrt_init()
        scal=np.zeros((T_HORIZON,len(SCALARS)),np.float64)
        stop,stop_step="HORIZON",T_HORIZON; inv=True
        for t in range(T_HORIZON):
            w._one_step()
            nY,nX=w.n["Y"],w.n["X"]
            free=sp.CAP-sum(w.n[s] for s in O.SPECIES)
            if free.min()<0 or max(w.n[s].max() for s in O.SPECIES)>sp.CAP:
                inv=False; stop,stop_step="INTEGRITY_FAILURE",t; break
            ys,xs=np.nonzero(nY); cells=list(zip(ys.tolist(),xs.tolist()))
            ncen,mxd=PR._centres(cells); NY=int(nY.sum())
            if cells:
                fy,fx=cells[0]
                cf=int(min(w.n["SY"][fy,fx],max(free[fy,fx],0)))
                qf,sf,ff,xf=int(nX[fy,fx])*cf,int(w.n["SY"][fy,fx]),int(free[fy,fx]),int(nX[fy,fx])
            else: cf=qf=sf=ff=xf=0
            candY=np.minimum(w.n["SY"],np.maximum(free,0))
            scal[t]=[t,NY,int(nX.sum()),len(cells),ncen,mxd,qf,sf,ff,xf,cf,
                     float((nX*candY).sum()),float(w.n["SY"].mean()),
                     float(np.maximum(free,0).mean()),float(w.n["SY"].sum()),float(w.n["SX"].sum())]
            if NY==0: stop,stop_step="EXTINCT",t; break
            if ncen>=3: stop,stop_step="PREMATURE_THIRD_CENTRE",t; break
            if NY>N_STAR: stop,stop_step="MAX_PERMITTED_Y",t; break
        n=min(stop_step+1,T_HORIZON); F=w.pq_field[:n]
        got={"field0":F[0],"field_delta":np.diff(F.astype(np.int16),axis=0).astype(np.int8),
             "scalars":scal[:n].astype(np.float64),
             "ycells":np.array(w.pq_ycells,np.int32) if w.pq_ycells else np.zeros((0,9),np.int32),
             "ybirth":np.array(w.pq_ybirth,np.int32) if w.pq_ybirth else np.zeros((0,4),np.int32),
             "ydeath":np.array(w.pq_ydeath,np.int32) if w.pq_ydeath else np.zeros((0,4),np.int32),
             "yhop":np.array(w.pq_yhop,np.int32) if w.pq_yhop else np.zeros((0,7),np.int32),
             "xevent":np.array(w.pq_xevent,np.int32) if w.pq_xevent else np.zeros((0,3),np.int32),
             "capacity":np.array(w.pq_capacity,np.int64),"exchange":np.array(w.pq_exchange,np.int64),
             "src":np.array(w.pq_src,np.int32),
             "final":np.stack([w.n[s] for s in O.SPECIES]).astype(np.int32)}
        z=np.load(os.path.join(RAW,tag+".npz"),allow_pickle=True); m=json.loads(str(z["meta"][0]))
        cmp={k:bool(np.array_equal(got[k],z[k])) for k in ARRAYS}
        cmp["stop"]=bool(stop==m["stop"]); cmp["stop_step"]=bool(int(stop_step)==int(m["stop_step"]))
        cmp["final_state_hash"]=bool(w.state_hash()==m["final_state_hash"]); z.close()
        return {"tag":tag,"BIT_EXACT":all(cmp.values()),"COMPARISON":cmp,
                "interventions":int(w.intervention_count)}
    except Exception:
        import traceback
        return {"tag":tag,"BIT_EXACT":False,"ERROR":traceback.format_exc()[-400:]}

if __name__=="__main__":
    F=FREEZE["SEED_RULE"]["SEEDS"]
    jobs=[]
    for lab in ("B1","B2"):
        pt=FREEZE["PHASE_B"]["POINT_"+lab]
        for r in F[lab]:
            jobs.append(("B_%s_i%03d_s%d"%(lab,r["index"],r["seed"]),r["seed"],pt["kY"],pt["muY"]))
    import multiprocessing as mp
    out=[]
    with mp.Pool(2) as pool:
        for i,r in enumerate(pool.imap_unordered(check,jobs),1):
            out.append(r); print("  [%3d/%d] %s BIT_EXACT=%s"%(i,len(jobs),r["tag"],r.get("BIT_EXACT")),flush=True)
    ok=sum(1 for r in out if r.get("BIT_EXACT"))
    J={"SECTION":"FMRT01 — unarmed inertness re-qualification of the reconstructed capability",
       "WHY_NOT_THE_FDFLT01_ARCHIVES":("they were destroyed by the fifth container rollback and were "
         "never made durable; only the 92 MB result-bearing core survives, which does not contain the "
         "full six-plane arrays this comparison needs"),
       "TEST_SET":"the 88 surviving PQEC01 Phase-B archives, produced by the same frozen engine and observer",
       "N":len(out),"N_BIT_EXACT":ok,
       "UNARMED_INERTNESS":"PASS_%d_OF_%d"%(ok,len(out)),
       "TOTAL_INTERVENTIONS_INVOKED":sum(r.get("interventions",0) for r in out),
       "WORLDS":[{k:v for k,v in r.items() if k!="COMPARISON"} for r in out]}
    json.dump(J,open(f"{OUT}/FMRT01_UNARMED_INERTNESS.json","w"),indent=2)
    print("UNARMED_INERTNESS: %s  interventions=%d"%(J["UNARMED_INERTNESS"],J["TOTAL_INTERVENTIONS_INVOKED"]))
