"""SMC-01 storage replication on the SEALED prospective family (run once), frozen C1c, DIST features."""
import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from candidates import make_engine
OUT="/tmp/smc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
man=json.load(open(os.environ["REPO"]+"/results/smc01/smc01_prospective_manifest.json"))
SEEDS=man["prospective"]["seeds"]; HH=man["prospective"]["histories"]
eng=make_engine(C.SPEC,C.TRACER,"C1c")
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm_p.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm_p.pkl",warm); print("WARM",len(warm)); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm_p.pkl",warm)
def apply2(body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=eng.step(cur)
    return H.advance(eng,cur,settle)
def dist(st):
    e=H.largest(st)
    if e is None: return None
    ys,xs=e.cells[:,0],e.cells[:,1];m=st.mem();m1=m[0][ys,xs];m2=m[1][ys,xs];f=[]
    for v in (m1,m2): f+=[float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    return {"feat":f,"m_mean":[float(m1.mean()),float(m2.mean())],"size":int(e.size)}
D=load(f"{OUT}/prosp_storage.pkl",[]); seen={(r["seed"],r["hi"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        if (seed,hi) in seen: continue
        if not tleft(): save(f"{OUT}/prosp_storage.pkl",D); print("BUDGET",len(D)); sys.exit()
        r=dist(apply2(warm[seed],a_e,a_l)); rec={"seed":seed,"hi":hi,"h1":a_e+a_l,"h2":a_l-a_e,"valid":r is not None}
        if r: rec.update(r)
        D.append(rec); save(f"{OUT}/prosp_storage.pkl",D)
print("COMPLETE prosp_storage n=%d"%len(D))
