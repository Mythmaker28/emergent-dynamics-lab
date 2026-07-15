"""SMC-01 turnover audit under frozen C1c. After history, relabel all material as OLD (cohort 0), run C1c
forward (no drive) with PulseChaseTracer (new growth -> cohort 1). Checkpoint M=old fraction + memory DIST."""
import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_hmc.harness import PulseChaseTracer
OUT="/tmp/smc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
man=json.load(open(os.environ["REPO"]+"/results/smc01/smc01_prospective_manifest.json"))
SEEDS=man["dev"]["seeds"][:2]; HH=man["dev"]["histories"]
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0)
def eng_default(): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**C1c),C.TRACER)
def eng_pc():      return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**C1c),PulseChaseTracer())
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm.pkl",{})
def apply2(body,a_e,a_l,eng,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=eng.step(cur)
    return H.advance(eng,cur,settle)
def relabel(st):
    out=st.copy(); out.C=np.stack([out.rho.copy(), np.zeros_like(out.rho)]); return out
def dist(st):
    e=H.largest(st)
    if e is None: return None,None,None
    ys,xs=e.cells[:,0],e.cells[:,1]; m=st.mem(); m1=m[0][ys,xs]; m2=m[1][ys,xs]
    feat=[]
    for v in (m1,m2): feat+=[float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    cm=np.asarray(e.cohort_mass); M=float(cm[0]/(cm.sum()+1e-9)) if cm.size>=1 else 1.0
    return feat,M,int(e.size)
CHECK=[0,40,90,160,260,380]
D=load(f"{OUT}/turnover.pkl",[]); seen={(r["seed"],r["hi"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        if (seed,hi) in seen: continue
        if not tleft(): save(f"{OUT}/turnover.pkl",D); print("BUDGET",len(D)); sys.exit()
        st=apply2(warm[seed],a_e,a_l,eng_default())     # write memory
        st=relabel(st); pc=eng_pc(); traj=[]
        nxt=0
        for step in range(CHECK[-1]+1):
            if step in CHECK:
                f,M,sz=dist(st)
                if f is not None: traj.append({"step":step,"M":M,"feat":f,"size":sz})
            st=pc.step(st)
        D.append({"seed":seed,"hi":hi,"h1":a_e+a_l,"h2":a_l-a_e,"traj":traj}); save(f"{OUT}/turnover.pkl",D)
print("COMPLETE turnover n=%d"%len(D))
