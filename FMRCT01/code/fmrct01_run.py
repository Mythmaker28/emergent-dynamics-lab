"""FMRCT01 §8, §15, §16 — the runner.

FULL HORIZON. Every base trajectory and every continuation executes all 11000 steps. Nothing is
stopped for extinction, a third centre, a failed daughter, a success, or the event becoming
impossible. The only break is a genuine engine invariant failure, which is a technical fault and
never a scientific outcome.

FIREWALL. The live channel carries an opaque token, completion, the predeclared technical-failure
flag and whether a checksum was written. Trigger records are written to a SEALED file that the
selection step reads mechanically; no scientific summary is printed.

FORKS ARE REPLAYS. A continuation re-runs the block from its seed to t_m and asserts that the
physical state, every generator state and every counter match the base trajectory's recorded
fingerprint before the intervention is applied. That is the §4 identity proof, executed rather
than asserted.
"""
from __future__ import annotations
import hashlib, json, os, sys, time, traceback
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRCT01/out"; RAW="/home/claude/FMRCT01/raw"
SEAL="/home/claude/FMRCT01/sealed"
sys.path.insert(0,f"{REPO}/FMRCT01/code")
import fmrct01_world as W
import fmrct01_track as T
import fmrct01_runtime as RT
import pqec01_observer as O
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
B1=FZ["PHASE_B"]["POINT_B1"]; CST=FZ["INHERITED_FROZEN_CONSTANTS"]
HOR=T.T_HORIZON

def _integrity(w,sp):
    free=sp.CAP-sum(w.n[s] for s in O.SPECIES)
    return not (free.min()<0 or max(w.n[s].max() for s in O.SPECIES)>sp.CAP)

def _save(path,rec,w):
    np.savez_compressed(path,
        meta=np.array([json.dumps(rec)]),
        ycells=np.array(w.pq_ycells,np.int32) if w.pq_ycells else np.zeros((0,9),np.int32),
        ybirth=np.array(w.pq_ybirth,np.int32) if w.pq_ybirth else np.zeros((0,4),np.int32),
        ydeath=np.array(w.pq_ydeath,np.int32) if w.pq_ydeath else np.zeros((0,4),np.int32),
        xbirth=np.array(w.fd_xbirth,np.int32) if w.fd_xbirth else np.zeros((0,4),np.int32))

def run_base(job):
    idx,seed=job
    tag="C_B1_b%03d_s%d"%(idx,seed)
    path=os.path.join(RAW,tag+".npz")
    rec={"arm":"SHAM_BASE","block":idx,"seed":seed,"tag":tag,"kY":B1["kY"],"muY":B1["muY"]}
    t0=time.time()
    try:
        w,_,sp=W.build(seed,B1["kY"],B1["muY"],HOR)
        tr=T.Trigger(); integ=True; stop="HORIZON"; stop_step=HOR
        fp=None
        for t in range(HOR):
            w._one_step()
            if not _integrity(w,sp):
                integ=False; stop="INTEGRITY_FAILURE"; stop_step=t; break
            if tr.t_m is None:
                cells,comps=T.centres_now(w)
                if tr.observe(t,w,cells,comps,integ):
                    fp=W.fork_fingerprint(w)
                    vals=T.EP.local_x_masses(T.xplane(w),tr.cells_tm,
                          [tr.parent_comp,tr.daughter_comp] if tr.parent_comp is not None else
                          T.CC.components(tr.cells_tm))
                    rec.update({"parent_mass_tm":vals[0],"daughter_mass_tm":vals[-1],
                                "NX_world_at_tm":int(w.n["X"].sum()),
                                "NY_world_at_tm":int(w.n["Y"].sum())})
        rec.update({"triggered":tr.t_m is not None,"t_m":tr.t_m,
                    "descent_level":getattr(tr,"descent_level",None),
                    "cells_tm":tr.cells_tm,"parent_comp":tr.parent_comp,
                    "daughter_comp":tr.daughter_comp,
                    "fork_fingerprint":fp,
                    "steps_executed":min(stop_step+1,HOR),"stop":stop,
                    "integrity_ok":bool(integ),"final_phys_hash":W.phys_hash(w),
                    "runtime_s":round(time.time()-t0,2)})
        _save(path,rec,w)
        rec["technical_failure"]=not (integ and os.path.exists(path))
        return rec
    except Exception:
        rec.update({"technical_failure":True,"ERROR":traceback.format_exc()[-500:],
                    "runtime_s":round(time.time()-t0,2)})
        return rec

def run_fork(job):
    idx,seed,arm,t_m,parent_cells,fp_expected=job
    tag="C_B1_b%03d_s%d_%s"%(idx,seed,arm)
    path=os.path.join(RAW,tag+".npz")
    rec={"arm":arm,"block":idx,"seed":seed,"tag":tag,"t_m":t_m}
    t0=time.time()
    try:
        w,_,sp=W.build(seed,B1["kY"],B1["muY"],HOR)
        integ=True; stop="HORIZON"
        for t in range(t_m+1):
            w._one_step()
            if not _integrity(w,sp): integ=False; stop="INTEGRITY_FAILURE"; break
        fp=W.fork_fingerprint(w)
        rec["fork_identity_ok"]=bool(fp==fp_expected)
        rec["fork_fingerprint"]=fp
        if not rec["fork_identity_ok"]:
            rec.update({"technical_failure":True,"ERROR":"FORK_STATE_MISMATCH",
                        "runtime_s":round(time.time()-t0,2)})
            return rec
        rec["removed"]=W.apply_arm(w,arm,[tuple(c) for c in parent_cells] if parent_cells else [])
        rec["post_intervention_phys_hash"]=W.phys_hash(w)
        rec["post_intervention_rng"]=W.rng_hash(w)
        rec["rng_untouched_by_intervention"]=bool(rec["post_intervention_rng"]==fp["rng"])
        for t in range(t_m+1,HOR):
            w._one_step()
            if not _integrity(w,sp): integ=False; stop="INTEGRITY_FAILURE"; break
        rec.update({"steps_executed":HOR,"stop":stop,"integrity_ok":bool(integ),
                    "final_phys_hash":W.phys_hash(w),"runtime_s":round(time.time()-t0,2)})
        _save(path,rec,w)
        rec["technical_failure"]=not (integ and os.path.exists(path))
        return rec
    except Exception:
        rec.update({"technical_failure":True,"ERROR":traceback.format_exc()[-500:],
                    "runtime_s":round(time.time()-t0,2)})
        return rec

def token(kind,i,arm=""): return hashlib.sha256(("FMRCT01|%s|%d|%s"%(kind,i,arm)).encode()).hexdigest()[:16]

def main():
    os.makedirs(RAW,exist_ok=True); os.makedirs(SEAL,exist_ok=True)
    v=RT.verify(strict=True)            # §12: a methods mismatch is a technical fault, not science
    print("methods verified: %d frozen files, %d loaded project modules"%(
        v["frozen_files"],v["loaded_project_modules"]),flush=True)
    phase=sys.argv[1] if len(sys.argv)>1 else "BASE"
    SM=json.load(open(f"{OUT}/FMRCT01_SEED_MANIFEST.json"))
    import multiprocessing as mp
    led=open(f"{OUT}/FMRCT01_RUN_LEDGER.jsonl","a")
    if phase=="BASE":
        done_tags=set()
        sp_path=f"{SEAL}/base.jsonl"
        if os.path.exists(sp_path):
            for line in open(sp_path):
                try: done_tags.add(json.loads(line)["tag"])
                except Exception: pass
        jobs=[(b["index"],b["seed"]) for b in SM["SEEDS"] if b["kind"]=="BLOCK"
              and "C_B1_b%03d_s%d"%(b["index"],b["seed"]) not in done_tags]
        seal=open(sp_path,"a")
        fn=run_base
    else:
        SEL=json.load(open(f"{OUT}/FMRCT01_FORK_SELECTION.json"))
        done_tags=set()
        sp_path=f"{SEAL}/fork.jsonl"
        if os.path.exists(sp_path):
            for line in open(sp_path):
                try: done_tags.add(json.loads(line)["tag"])
                except Exception: pass
        jobs=[]
        for s in SEL["SELECTED"]:
            for arm in ("SELECTIVE","GLOBAL_OFF"):
                tg="C_B1_b%03d_s%d_%s"%(s["block"],s["seed"],arm)
                if tg in done_tags: continue
                jobs.append((s["block"],s["seed"],arm,s["t_m"],s["parent_cells"],s["fork_fingerprint"]))
        seal=open(sp_path,"a")
        fn=run_fork
    n=len(jobs); done=0
    with mp.Pool(2) as pool:
        for rec in pool.imap_unordered(fn,jobs):
            done+=1
            seal.write(json.dumps(rec)+"\n"); seal.flush()
            pub={"arm_token":token(phase,rec.get("block",-1),rec.get("arm","")),
                 "completed":"ERROR" not in rec,
                 "technical_failure":bool(rec.get("technical_failure")),
                 "checksum_written":os.path.exists(os.path.join(RAW,rec["tag"]+".npz"))}
            led.write(json.dumps(pub)+"\n"); led.flush()
            if done%20==0 or done==n:
                print("%s %d/%d"%(phase,done,n),flush=True)
    print("PHASE_%s_COMPLETE"%phase,flush=True)
if __name__=="__main__": main()
