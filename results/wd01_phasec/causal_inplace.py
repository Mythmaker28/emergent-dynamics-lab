"""In-place causal test (preserves SPATIAL memory): from post-history state, read response with full vs
memory-inert engine on the SAME body; dR isolates the memory's causal effect incl. spatial structure."""
import os,sys,time,pickle,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from candidates import make_engine
OUT="/tmp/pcc"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
import json
man=json.load(open(os.environ["REPO"]+"/results/wd01_phasec/prospective_manifest.json"))
HH=man["prospective"]["F_mid"]["histories"]; SEEDS=man["prospective"]["seeds"][:2]
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0)
full=make_engine(C.SPEC,C.TRACER,"C1c")
both0=MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.0,lam_minus=0.0,**C1c),C.TRACER)
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm_p.pkl",{})
def apply2(eng,body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=eng.step(cur)
    return H.advance(eng,cur,settle)
def feat(st):
    e=H.largest(st)
    if e is None: return [0.]*5
    ys,xs=e.cells[:,0],e.cells[:,1]
    return [float(e.size),float(e.rg),float(e.specific_uptake),float(e.mass),float(st.c[ys,xs].mean())]
D=load(f"{OUT}/causal_ip.pkl",[]); seen={(r["hi"],r["seed"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        if (hi,seed) in seen: continue
        if not tleft(): save(f"{OUT}/causal_ip.pkl",D); print("BUDGET",len(D)); sys.exit()
        s=apply2(full,warm[seed],a_e,a_l)     # post-history state (spatial memory intact)
        Rf=feat(H.advance(full,s.copy(),40)); Rb=feat(H.advance(both0,s.copy(),40))
        D.append({"hi":hi,"seed":seed,"h1":a_e+a_l,"h2":a_l-a_e,"Rfull":Rf,"Rboth0":Rb})
        save(f"{OUT}/causal_ip.pkl",D)
print("COMPLETE causal_ip n=%d"%len(D))
