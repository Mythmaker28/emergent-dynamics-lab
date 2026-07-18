"""SMC-01: save full entity memory FIELDS for frozen C1c dev histories (for frame/geom/transplant analysis)."""
import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from candidates import make_engine
OUT="/tmp/smc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
man=json.load(open(os.environ["REPO"]+"/results/smc01/smc01_prospective_manifest.json"))
SEEDS=man["dev"]["seeds"]; HH=man["dev"]["histories"]
eng=make_engine(C.SPEC,C.TRACER,"C1c")
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm.pkl",warm); print("WARM",len(warm)); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm.pkl",warm)
def apply2(body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=eng.step(cur)
    return H.advance(eng,cur,settle)
def rec_field(st,h1,h2,seed,hi):
    e=H.largest(st)
    if e is None: return {"seed":seed,"hi":hi,"valid":False}
    ys,xs=e.cells[:,0],e.cells[:,1]; n=st.rho.shape[0]; cen=e.centroid
    dy=((ys-cen[0]+n/2)%n-n/2); dx=((xs-cen[1]+n/2)%n-n/2)
    rho=st.rho[ys,xs]; m=st.mem()
    return {"seed":seed,"hi":hi,"valid":True,"h1":h1,"h2":h2,"size":int(e.size),"rg":float(e.rg),
            "com":[float(cen[0]),float(cen[1])],
            "dy":dy.astype(np.float32),"dx":dx.astype(np.float32),
            "ys":ys.astype(np.int16),"xs":xs.astype(np.int16),
            "m1":m[0][ys,xs].astype(np.float32),"m2":m[1][ys,xs].astype(np.float32),
            "rho":rho.astype(np.float32)}
D=load(f"{OUT}/fields.pkl",[]); seen={(r["seed"],r["hi"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        if (seed,hi) in seen: continue
        if not tleft(): save(f"{OUT}/fields.pkl",D); print("BUDGET",len(D)); sys.exit()
        st=apply2(warm[seed],a_e,a_l)
        D.append(rec_field(st,a_e+a_l,a_l-a_e,seed,hi)); save(f"{OUT}/fields.pkl",D)
print("COMPLETE fields n=%d"%len(D))
