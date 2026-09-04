"""FDOT01 §8, §15, §16 — the runner.

FULL HORIZON. Every primary world executes all T_HORIZON steps. PQEC01 stopped worlds on
EXTINCT, PREMATURE_THIRD_CENTRE and MAX_PERMITTED_Y; §8 forbids all three, so none is a stop
here. The single break is a genuine engine invariant failure, which is a technical fault and
never a scientific outcome.

FIREWALL. The live channel carries only an opaque token, completion, the predeclared technical
failure flag, and whether a checksum was written.
"""
from __future__ import annotations
import hashlib, json, os, sys, time, traceback
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/FDOT01/out"; RAW="/home/claude/FDOT01/raw"
sys.path.insert(0,f"{REPO}/FDOT01/code")
import fdot01_world as W
import pqec01_observer as O
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
B1=FZ["PHASE_B"]["POINT_B1"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]
T_HORIZON=int(C["T_HORIZON"])
SCALARS=["step","N_Y","N_X","n_y_cells","n_SY_total","n_SX_total"]

def phys_hash(w):
    h=hashlib.sha256()
    for s in O.SPECIES: h.update(np.ascontiguousarray(w.n[s]).tobytes())
    return h.hexdigest()

def run_world(job):
    kind,idx,seed=job
    tag="F_B1_%s_i%03d_s%d"%(kind[:1],idx,seed)
    path=os.path.join(RAW,tag+".npz")
    rec={"tag":tag,"kind":kind,"index":idx,"seed":seed,"kY":B1["kY"],"muY":B1["muY"]}
    t0=time.time()
    try:
        w,_,sp=W.build(seed,B1["kY"],B1["muY"],T_HORIZON)
        scal=np.zeros((T_HORIZON,len(SCALARS)),np.float32)
        integrity_ok=True; stop="HORIZON"; stop_step=T_HORIZON
        for t in range(T_HORIZON):
            w._one_step()
            free=sp.CAP-sum(w.n[s] for s in O.SPECIES)
            if free.min()<0 or max(w.n[s].max() for s in O.SPECIES)>sp.CAP:
                integrity_ok=False; stop="INTEGRITY_FAILURE"; stop_step=t; break
            nY=w.n["Y"]
            scal[t]=[t,int(nY.sum()),int(w.n["X"].sum()),int((nY>0).sum()),
                     int(w.n["SY"].sum()),int(w.n["SX"].sum())]
        n_rec=min(stop_step+1,T_HORIZON)
        rec.update({"steps_executed":n_rec,"stop":stop,"integrity_ok":bool(integrity_ok),
                    "final_state_hash":phys_hash(w),"runtime_s":round(time.time()-t0,2)})
        np.savez_compressed(path,
            meta=np.array([json.dumps(rec)]),
            scalars=scal[:n_rec], scalar_names=np.array(SCALARS),
            ycells=np.array(w.pq_ycells,np.int32) if w.pq_ycells else np.zeros((0,9),np.int32),
            ybirth=np.array(w.pq_ybirth,np.int32) if w.pq_ybirth else np.zeros((0,4),np.int32),
            ydeath=np.array(w.pq_ydeath,np.int32) if w.pq_ydeath else np.zeros((0,4),np.int32),
            xbirth=np.array(w.fd_xbirth,np.int32) if w.fd_xbirth else np.zeros((0,4),np.int32))
        rec["technical_failure"]=not (integrity_ok and os.path.exists(path))
        return rec
    except Exception:
        rec.update({"technical_failure":True,"ERROR":traceback.format_exc()[-400:],
                    "runtime_s":round(time.time()-t0,2)})
        return rec

def token(kind,i): return hashlib.sha256(("FDOT01|%s|%d"%(kind,i)).encode()).hexdigest()[:16]

def main():
    os.makedirs(RAW,exist_ok=True)
    SM=json.load(open(f"{OUT}/FDOT01_SEED_MANIFEST.json"))["SEEDS"]
    only=sys.argv[1] if len(sys.argv)>1 else "PRIMARY"
    jobs=[(b["kind"],b["index"],b["seed"]) for b in SM if b["kind"]==only]
    import multiprocessing as mp
    led=open(f"{OUT}/FDOT01_RUN_LEDGER.jsonl","a")
    seal=open("/home/claude/FDOT01/sealed.jsonl","a")
    done=0
    with mp.Pool(2) as pool:
        for rec in pool.imap_unordered(run_world,jobs):
            done+=1
            pub={"arm_token":token(rec["kind"],rec["index"]),
                 "completed":"ERROR" not in rec,
                 "technical_failure":bool(rec.get("technical_failure")),
                 "checksum_written":os.path.exists(os.path.join(RAW,rec["tag"]+".npz"))}
            led.write(json.dumps(pub)+"\n"); led.flush()
            seal.write(json.dumps(rec,default=str)+"\n"); seal.flush()
            print("  [%3d/%3d] %s completed=%s technical_failure=%s checksum=%s"%(
                done,len(jobs),pub["arm_token"],pub["completed"],pub["technical_failure"],
                pub["checksum_written"]),flush=True)
    led.close(); seal.close()
    print("worlds attempted: %d"%len(jobs))

if __name__=="__main__": main()
