"""WD-01 Phase C development runner (resumable). Warm dev seeds with C0; erase memory; apply 2-phase
nutrient history (T=60 each, settle=20); read memory features. Writing per candidate. Checkpoints per unit."""
import os,sys,time,pickle,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from candidates import make_engine, CANDS
OUT="/tmp/pcc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
SEEDS=(34001,34002,34003)
FAM={"F_mid":(0.003,0.020,34100),"F_low":(0.001,0.008,34101)}
def hists(lo,hi,rng,n=12):
    r=np.random.default_rng(rng); ae=r.uniform(lo,hi,n); al=r.uniform(lo,hi,n)
    return [(float(a),float(b)) for a,b in zip(ae,al)]
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm.pkl",warm); print("WARM",len(warm)); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm.pkl",warm)
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
    return dict(size=int(e.size),m_mean=[float(m1.mean()),float(m2.mean())],
                clip=[float((np.abs(m1)>0.999).mean()),float((np.abs(m2)>0.999).mean())],spatial=s(m1)+s(m2))
D=load(f"{OUT}/dev.pkl",[]); seen={(r["cand"],r["fam"],r["hi"],r["seed"]) for r in D}
engines={n:make_engine(C.SPEC,C.TRACER,n) for n in CANDS}
for cand in CANDS:
    eng=engines[cand]
    for fam,(lo,hi,rng) in FAM.items():
        HH=hists(lo,hi,rng)
        for hi_,(a_e,a_l) in enumerate(HH):
            for seed in SEEDS:
                key=(cand,fam,hi_,seed)
                if key in seen: continue
                if not tleft(): save(f"{OUT}/dev.pkl",D); print("BUDGET",len(D)); sys.exit()
                f=feat(apply2(eng,warm[seed],a_e,a_l))
                rec={"cand":cand,"fam":fam,"hi":hi_,"seed":seed,"a_e":a_e,"a_l":a_l,"h1":a_e+a_l,"h2":a_l-a_e,"valid":f is not None}
                if f: rec.update(f)
                D.append(rec); save(f"{OUT}/dev.pkl",D)
print("COMPLETE dev n=%d"%len(D))
