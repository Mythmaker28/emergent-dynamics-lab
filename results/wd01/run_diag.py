"""WD-01 Phase-B frozen-writing diagnostic (D1 rank/decode + D2 saturation curve).
PREREGISTERED constants below. Writing equations are FROZEN (sc_mcm engine unchanged);
we only vary the INPUT history and READ the memory field. Resumable; checkpoints per unit."""
import os, sys, time, pickle, numpy as np
sys.path.insert(0, os.environ["REPO"])
from edlab.experiments.sc_mcm import config as C, harness as H

OUT="/tmp/wd01"; os.makedirs(OUT, exist_ok=True)
BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0 < BUDGET

SEEDS=(32100,32101,32102,32103)                 # DEV-family seeds only (no prospective 33xxx)
# D2 constant-drive saturation sweep
PS=(0.001,0.002,0.003,0.005,0.008,0.012,0.02,0.03,0.05)
# D1 conditions: independent (p1,p2), fixed RNG per condition
NH=12
def hists(cond):
    if cond=="A_mismatch": rng=np.random.default_rng(4101); return [(float(rng.uniform(0.005,0.025)),float(rng.uniform(0.0,1.0))) for _ in range(NH)]
    if cond=="B_matched_mid": rng=np.random.default_rng(4102); return [(float(rng.uniform(0.005,0.025)),float(rng.uniform(0.005,0.025))) for _ in range(NH)]
    if cond=="C_matched_low": rng=np.random.default_rng(4103); return [(float(rng.uniform(0.001,0.006)),float(rng.uniform(0.001,0.006))) for _ in range(NH)]
CONDS=("A_mismatch","B_matched_mid","C_matched_low")

def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o, open(p,"wb"))

warm=load(f"{OUT}/warm.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm.pkl",warm); print("WARMING",len(warm),flush=True); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm.pkl",warm)

def ent_cells(st):
    e=H.largest(st)
    if e is None: return None,None
    return e, (e.cells[:,0], e.cells[:,1])

def mem_features(st):
    """exact memory readout over the entity: entity-mean (m1,m2) + spatial summary (10-D) + clip fracs."""
    e,(ys,xs)=ent_cells(st)
    if e is None: return None
    rho=np.maximum(st.rho[ys,xs],1e-12)
    m1=st.Mf[0,ys,xs]/rho; m2=st.Mf[1,ys,xs]/rho
    def summ(v): return [float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    feat=summ(m1)+summ(m2)
    return dict(size=int(e.size), m_mean=[float(m1.mean()),float(m2.mean())],
                mplus=float((m1+m2).mean()), mminus=float((m1-m2).mean()),
                clip1=float((np.abs(m1)>0.999).mean()), clip2=float((np.abs(m2)>0.999).mean()),
                spatial=feat)

def psi_occ_constdrive(eng, st, p, T):
    """single-phase constant drive; record reconstructed-Psi saturation occupancy (proxy) over alive cells."""
    cur=st.copy(); occ=[]
    for _ in range(T):
        cur.N=cur.N+p; cur=eng.step(cur)
        alive=cur.rho>1e-4
        if alive.any():
            up=cur.uptake; arg=C.MC.k_exp*(cur.N-cur.c)+C.MC.k_up*(up-up[alive].mean())
            occ.append(float((np.abs(np.tanh(arg))[alive]>0.9).mean()))
    cur=H.advance(eng,cur,C.SETTLE)
    return (float(np.mean(occ)) if occ else np.nan), cur

D=load(f"{OUT}/diag.pkl",{"D2":[],"D1":[]})
seenD2={r["p"] for r in D["D2"]}
seenD1={(r["cond"],r["hi"],r["seed"]) for r in D["D1"]}

# D2 (one seed)
eng=H.mc_engine()
for p in PS:
    if p in seenD2: continue
    if not tleft(): save(f"{OUT}/diag.pkl",D); print("D2 BUDGET",len(D["D2"]),flush=True); sys.exit()
    occ,st=psi_occ_constdrive(eng, warm[SEEDS[0]], p, 60)
    mf=mem_features(st); 
    D["D2"].append({"p":p,"psi_occ":occ,"feat":mf}); save(f"{OUT}/diag.pkl",D)

# D1 (grid x seeds)
for cond in CONDS:
    HH=hists(cond)
    for hi,(p1,p2) in enumerate(HH):
        for seed in SEEDS:
            if (cond,hi,seed) in seenD1: continue
            if not tleft(): save(f"{OUT}/diag.pkl",D); print("D1 BUDGET",len(D["D1"]),flush=True); sys.exit()
            st=H.apply_cont_history(eng, warm[seed], p1, p2)
            mf=mem_features(st)
            rec={"cond":cond,"hi":hi,"seed":seed,"p1":p1,"p2":p2,"valid":mf is not None}
            if mf: rec.update(mf)
            D["D1"].append(rec); save(f"{OUT}/diag.pkl",D)
print("COMPLETE D2=%d D1=%d"%(len(D["D2"]),len(D["D1"])),flush=True)
