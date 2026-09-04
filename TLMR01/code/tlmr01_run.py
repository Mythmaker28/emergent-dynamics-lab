"""TLMR01 §14 — the runner.

FULL HORIZON. Every primary world executes all T_HORIZON = 11000 steps. There is no scientific
early stop of any kind: not extinction, not a third centre, not a maximum occupancy. The single
break is an engine invariant failure, which is a TECHNICAL fault and never a scientific outcome.

FIREWALL. The live channel carries only an opaque token, completion, the predeclared technical
failure flag, whether a checksum was written, and the archive's size in bytes. No trigger, no
label, no count of anything physical reaches the operator while worlds are still running. The
full per-world record goes to a sealed file that is not read until the raw commitment (C3).

BATCHES. Worlds run in batches of at most BATCH = 16. After every batch each archive is read back
from disk, its sha256 re-verified against what was written, and the offline reader is constructed
on it. A batch that fails read-back stops the run; it is never papered over.
"""
from __future__ import annotations
import hashlib, json, os, sys, time, traceback
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"; RAW="/home/claude/TLMR01/raw"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_world as TW, tlmr01_laws as LW
BATCH=16
SCHEMA={"VERSION":"TLMR01-ARCHIVE-1",
 "s":["t","nY_total","nX_total","nSY_total","nSX_total","free_min","n_y_cells","n_components"],
 "cells":["c_t","c_y","c_x","c_nY","c_nX","c_nSY","c_free","c_cand","c_cid"],
 "comp":["k_t","k_id","k_ncells","k_nY","k_a0y","k_a0x","k_soy","k_sox","k_xd"],
 "ledgers":["ybirth","ydeath","xbirth"],
 "cells_semantics":"one row per Y-OCCUPIED cell per step; lossless for the frozen centre rules",
 "comp_semantics":"one row per component per step; k_xd is the sum of X over the frozen CORE_R "
   "disc at the rounded centroid, which is the exact input to the frozen f5 ratio. k_a0*/k_so* are the exact centroid inputs: centroid = (a0 + so/k_ncells) % L, bit-equal to the online value, so an offline identity link can never flip on a rounded coordinate",
 "removal_semantics":"the rows at the removal step are recorded BEFORE the intervention; the "
   "post-removal state first appears at step+1"}

def _narrow(w):
    c=np.array(w.tl_cells,np.int64) if w.tl_cells else np.zeros((0,9),np.int64)
    k=np.array(w.tl_comp,np.int64) if w.tl_comp else np.zeros((0,9),np.int64)
    s=np.array(w.tl_step,np.int64) if w.tl_step else np.zeros((0,8),np.int64)
    d={"c_t":c[:,0].astype(np.uint16),"c_y":c[:,1].astype(np.uint8),"c_x":c[:,2].astype(np.uint8),
       "c_nY":c[:,3].astype(np.uint8),"c_nX":c[:,4].astype(np.uint8),"c_nSY":c[:,5].astype(np.uint8),
       "c_free":c[:,6].astype(np.uint8),"c_cand":c[:,7].astype(np.int32),
       "c_cid":c[:,8].astype(np.int16),
       "k_t":k[:,0].astype(np.uint16),"k_id":k[:,1].astype(np.int16),
       "k_ncells":k[:,2].astype(np.uint16),"k_nY":k[:,3].astype(np.uint16),
       "k_a0y":k[:,4].astype(np.int16),"k_a0x":k[:,5].astype(np.int16),
       "k_soy":k[:,6].astype(np.int32),"k_sox":k[:,7].astype(np.int32),
       "k_xd":k[:,8].astype(np.int32),
       "s":s.astype(np.int32),
       "ybirth":np.array(w.pq_ybirth or [],np.int32).reshape(-1,4),
       "ydeath":np.array(w.pq_ydeath or [],np.int32).reshape(-1,4),
       "xbirth":np.array(w.fd_xbirth or [],np.int32).reshape(-1,4)}
    # the narrow dtypes must be lossless: proved per world, not assumed
    ok=(c.shape[0]==0 or (int(c[:,0].max())<2**16 and int(c[:,1].max())<256 and int(c[:,2].max())<256
        and int(c[:,3].max())<256 and int(c[:,4].max())<256 and int(c[:,5].max())<256
        and int(c[:,6].max())<256 and int(c[:,8].max())<2**15)) and \
       (k.shape[0]==0 or (int(k[:,0].max())<2**16 and int(k[:,1].max())<2**15
        and int(k[:,2].max())<2**16 and int(k[:,3].max())<2**16
        and int(np.abs(k[:,4]).max())<2**15 and int(np.abs(k[:,5]).max())<2**15))
    return d,bool(ok)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def run_one(job):
    law,role,idx,seed=job
    v=LW.LAWS[law]
    tag="TLMR01_%s_%s_i%03d_s%d"%(law,role[:1],idx,seed)
    path=os.path.join(RAW,tag+".npz")
    rec={"tag":tag,"law":law,"role":role,"index":idx,"seed":seed,
         "kY":v["kY"],"muY":v["muY"],"p_hop_Y":v["p_hop_Y"]}
    t0=time.time()
    try:
        w,r=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=TW.T_HORIZON)
        rec.update(r); rec["runtime_s"]=round(time.time()-t0,1)
        d,lossless=_narrow(w)
        rec["NARROW_DTYPES_LOSSLESS"]=lossless
        if not lossless: raise RuntimeError("narrow dtype would truncate a recorded value")
        d["meta"]=np.array([json.dumps(rec,default=str)])
        d["schema"]=np.array([json.dumps(SCHEMA)])
        # np.savez_compressed APPENDS .npz when the name does not already end in it, so the
        # temporary name must end in .npz or the atomic replace looks for a file that was never
        # written. Found by the §5 writer fixture, before world 1.
        tmp=path+".part.npz"
        np.savez_compressed(tmp,**d); os.replace(tmp,path)
        rec["archive_sha256"]=sha(path); rec["archive_bytes"]=os.path.getsize(path)
        rec["technical_failure"]=not (r["integrity_ok"] and os.path.exists(path))
        return rec
    except Exception:
        rec.update({"technical_failure":True,"ERROR":traceback.format_exc()[-600:],
                    "runtime_s":round(time.time()-t0,1)})
        return rec

def token(law,role,i):
    return hashlib.sha256(("TLMR01|%s|%s|%d"%(law,role,i)).encode()).hexdigest()[:16]

def read_back(recs):
    """durability gate: every archive re-hashed from disk and opened by the OFFLINE reader."""
    import tlmr01_offline as OFF
    out=[]
    for r in recs:
        p=os.path.join(RAW,r["tag"]+".npz")
        e={"tag":r["tag"],"exists":os.path.exists(p)}
        if e["exists"]:
            e["sha256_matches"]=(sha(p)==r.get("archive_sha256"))
            try:
                A=OFF.Archive(p); e["offline_reader_opens"]=True
                e["steps_indexed"]=int(A.T)
                e["schema_version"]=A.schema["VERSION"]
            except Exception as ex:
                e["offline_reader_opens"]=False; e["reader_error"]=repr(ex)[:200]
        e["OK"]=bool(e.get("exists") and e.get("sha256_matches") and e.get("offline_reader_opens"))
        out.append(e)
    return out

def main():
    os.makedirs(RAW,exist_ok=True); os.makedirs(OUT,exist_ok=True)
    SM=json.load(open(f"{OUT}/TLMR01_SEED_MANIFEST.json"))
    only=sys.argv[1] if len(sys.argv)>1 else "PRIMARY"
    jobs=[(b["law"],b["role"],b["index"],b["seed"]) for b in SM["SEEDS"] if b["role"]==only]
    done=set()
    lp=f"{OUT}/TLMR01_RUN_LEDGER.jsonl"
    if os.path.exists(lp):
        for ln in open(lp):
            try: done.add(json.loads(ln)["arm_token"])
            except Exception: pass
    jobs=[j for j in jobs if token(j[0],j[1],j[2]) not in done]
    print("worlds to run: %d"%len(jobs),flush=True)
    import multiprocessing as mp
    led=open(lp,"a"); seal=open("/home/claude/TLMR01/sealed.jsonl","a")
    rb=open(f"{OUT}/TLMR01_READ_BACK.jsonl","a")
    t0=time.time(); n=0
    for bi in range(0,len(jobs),BATCH):
        batch=jobs[bi:bi+BATCH]; recs=[]
        with mp.Pool(2) as pool:
            for rec in pool.imap_unordered(run_one,batch):
                recs.append(rec); n+=1
                pub={"arm_token":token(rec["law"],rec["role"],rec["index"]),
                     "completed":"ERROR" not in rec,
                     "technical_failure":bool(rec.get("technical_failure")),
                     "checksum_written":bool(rec.get("archive_sha256")),
                     "archive_bytes":int(rec.get("archive_bytes",0))}
                led.write(json.dumps(pub)+"\n"); led.flush()
                seal.write(json.dumps(rec,default=str)+"\n"); seal.flush()
                print("  [%3d/%3d] %s completed=%s tech_fail=%s checksum=%s %.1f MB  %.0fs elapsed"%(
                  n,len(jobs),pub["arm_token"],pub["completed"],pub["technical_failure"],
                  pub["checksum_written"],pub["archive_bytes"]/1e6,time.time()-t0),flush=True)
        chk=read_back(recs)
        for e in chk: rb.write(json.dumps(e)+"\n")
        rb.flush()
        bad=[e["tag"] for e in chk if not e["OK"]]
        print("  batch %d read-back: %d/%d OK%s"%(bi//BATCH,sum(e["OK"] for e in chk),len(chk),
              ("  FAILED: "+",".join(bad)) if bad else ""),flush=True)
        if bad:
            print("STOPPING: read-back failed. No world is replaced and nothing is repaired here.",flush=True)
            break
    led.close(); seal.close(); rb.close()
    print("attempted %d worlds in %.0fs"%(n,time.time()-t0))

if __name__=="__main__": main()
