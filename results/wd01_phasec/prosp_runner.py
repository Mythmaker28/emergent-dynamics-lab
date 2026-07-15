import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from candidates import make_engine
OUT="/tmp/pcc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
man=json.load(open(os.environ["REPO"]+"/results/wd01_phasec/prospective_manifest.json"))
SEEDS=man["prospective"]["seeds"]
FAM={"F_mid":man["prospective"]["F_mid"]["histories"],"F_low":man["prospective"]["F_low"]["histories"]}
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm_p.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm_p.pkl",warm); print("WARM",len(warm)); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm_p.pkl",warm)
def apply2(eng,body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=eng.step(cur)
    return H.advance(eng,cur,settle)
def feat(st):
    e=H.largest(st)
    if e is None: return None
    ys,xs=e.cells[:,0],e.cells[:,1]; rho=np.maximum(st.rho[ys,xs],1e-12)
    m1=st.Mf[0,ys,xs]/rho; m2=st.Mf[1,ys,xs]/rho
    def s(v): return [float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    return dict(size=int(e.size),m_mean=[float(m1.mean()),float(m2.mean())],spatial=s(m1)+s(m2))
D=load(f"{OUT}/prosp.pkl",[]); seen={(r["cand"],r["fam"],r["hi"],r["seed"]) for r in D}
eng={"C1c":make_engine(C.SPEC,C.TRACER,"C1c"),"C0":make_engine(C.SPEC,C.TRACER,"C0")}
for cand in ("C1c","C0"):
    for fam,HH in FAM.items():
        for hi_,(a_e,a_l) in enumerate(HH):
            for seed in SEEDS:
                key=(cand,fam,hi_,seed)
                if key in seen: continue
                if not tleft(): save(f"{OUT}/prosp.pkl",D); print("BUDGET",len(D)); sys.exit()
                f=feat(apply2(eng[cand],warm[seed],a_e,a_l))
                rec={"cand":cand,"fam":fam,"hi":hi_,"seed":seed,"h1":a_e+a_l,"h2":a_l-a_e,"valid":f is not None}
                if f: rec.update(f)
                D.append(rec); save(f"{OUT}/prosp.pkl",D)
print("COMPLETE prosp n=%d"%len(D))
