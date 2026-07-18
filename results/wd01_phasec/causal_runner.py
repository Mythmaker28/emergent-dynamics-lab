"""Causal controls for frozen C1c: mean-transplant each stored memory into a COMMON erased body, settle,
read R=[size,rg,uptake,mass,mean_c] with full and channel-ablated engines. Isolates the memory's causal
role (common body removes body confound). Uses held-out prospective F_mid memories."""
import os,sys,time,pickle,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm.experiment import read_signature
OUT="/tmp/pcc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0)  # frozen
def mk(lp,lm): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=lp,lam_minus=lm,**C1c),C.TRACER)
ENG={"full":mk(0.25,0.15),"lp0":mk(0.0,0.15),"lm0":mk(0.25,0.0),"both0":mk(0.0,0.0)}
PR=pickle.load(open(f"{OUT}/prosp.pkl","rb"))
recs=[r for r in PR if r["cand"]=="C1c" and r["fam"]=="F_mid" and r.get("valid")]
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm_p.pkl",{})
B0p=f"{OUT}/B0.pkl"
if os.path.exists(B0p): B0=pickle.load(open(B0p,"rb"))
else:
    B0=H.erase_memory(H.advance(H.mc_engine(), H.apply_history(H.mc_engine(), warm[35001], C.HISTORIES["H4"]), C.SETTLE))
    save(B0p,B0)
D=load(f"{OUT}/causal.pkl",[]); seen={(r["hi"],r["seed"]) for r in D}
for r in recs:
    key=(r["hi"],r["seed"])
    if key in seen: continue
    if not tleft(): save(f"{OUT}/causal.pkl",D); print("BUDGET",len(D)); sys.exit()
    dm=np.array(r["m_mean"])
    row={"hi":r["hi"],"seed":r["seed"],"h1":r["h1"],"h2":r["h2"]}
    for nm,eng in ENG.items():
        row["R_"+nm]=read_signature(eng,B0,dm).tolist()
    row["R_erase"]=read_signature(ENG["full"],B0,np.zeros(2)).tolist()
    D.append(row); save(f"{OUT}/causal.pkl",D)
print("COMPLETE causal n=%d"%len(D))
