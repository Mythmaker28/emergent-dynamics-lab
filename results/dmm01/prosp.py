import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_hmc.harness import PulseChaseTracer
OUT="/tmp/dmm"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0)
def mk(tr): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**C1c),tr)
weng=mk(C.TRACER)
man=json.load(open(os.environ["REPO"]+"/results/dmm01/dmm01_prospective_manifest.json"))
HH=man["prospective"]["histories"]; SEEDS=man["prospective"]["seeds"]
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm_p.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm_p.pkl",warm);print("WARM",len(warm));sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm_p.pkl",warm)
def apply2(body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=weng.step(cur)
    return H.advance(weng,cur,settle)
def relabel(st):
    out=st.copy(); out.C=np.stack([out.rho.copy(),np.zeros_like(out.rho)]); return out
def feat(st):
    e=H.largest(st)
    if e is None: return None
    ys,xs=e.cells[:,0],e.cells[:,1];m=st.mem();f=[]
    for v in (m[0][ys,xs],m[1][ys,xs]): f+=[float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    cm=np.asarray(e.cohort_mass);return f,float(cm[0]/(cm.sum()+1e-9)),int(e.size)
CHECK=[0,200,400]
D=load(f"{OUT}/prosp.pkl",[]); seen={(r["seed"],r["hi"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        if (seed,hi) in seen: continue
        if not tleft(): save(f"{OUT}/prosp.pkl",D);print("BUDGET",len(D));sys.exit()
        st=relabel(apply2(warm[seed],a_e,a_l));pc=mk(PulseChaseTracer());rb={}
        for step in range(CHECK[-1]+1):
            if step in CHECK: rb[step]=feat(st)
            st=pc.step(st)
        D.append({"seed":seed,"hi":hi,"h2":a_l-a_e,"h1":a_e+a_l,"traj":rb}); save(f"{OUT}/prosp.pkl",D)
print("COMPLETE prosp n=%d"%len(D))
