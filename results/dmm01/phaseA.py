import os,sys,time,pickle,json,numpy as np
sys.path.insert(0,os.environ["REPO"]); sys.path.insert(0,"/tmp/pcc")
from edlab.experiments.sc_mcm import config as C, harness as H
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_hmc.harness import PulseChaseTracer
OUT="/tmp/dmm"; BUDGET=float(os.environ.get("BUDGET","38")); t0=time.time()
def tleft(): return time.time()-t0<BUDGET
man=json.load(open(os.environ["REPO"]+"/results/dmm01/dmm01_prospective_manifest.json"))
SEEDS=man["dev"]["seeds"][:2]; HH=man["dev"]["histories"]
BASE=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0)
BR={"A0":dict(eta_t=0.010,D_m=0.010),"A4_tmpl0":dict(eta_t=0.0,D_m=0.010),
    "A3_diff0":dict(eta_t=0.010,D_m=0.0),"A34_both0":dict(eta_t=0.0,D_m=0.0)}
def eng(br,tracer): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**BASE,**BR[br]),tracer)
def load(p,d): return pickle.load(open(p,"rb")) if os.path.exists(p) else d
def save(p,o): pickle.dump(o,open(p,"wb"))
warm=load(f"{OUT}/warm.pkl",{})
for s in SEEDS:
    if s not in warm:
        if not tleft(): save(f"{OUT}/warm.pkl",warm); print("WARM",len(warm)); sys.exit()
        warm[s]=H.warmup(s); save(f"{OUT}/warm.pkl",warm)
weng=eng("A0",C.TRACER)
def apply2(body,a_e,a_l,T=60,settle=20):
    cur=H.erase_memory(body).copy()
    for a in (a_e,a_l):
        for _ in range(T): cur.N=cur.N+a; cur=weng.step(cur)
    return H.advance(weng,cur,settle)
def relabel(st):
    out=st.copy(); out.C=np.stack([out.rho.copy(),np.zeros_like(out.rho)]); return out
def dist(v):
    return [float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))] if len(v)>=4 else None
def readck(st):
    e=H.largest(st)
    if e is None: return None
    ys,xs=e.cells[:,0],e.cells[:,1]; m=st.mem(); m1=m[0][ys,xs]; m2=m[1][ys,xs]
    Cf=st.C; oldf=Cf[0][ys,xs]/(Cf[0][ys,xs]+Cf[1][ys,xs]+1e-9)
    cm=np.asarray(e.cohort_mass); M=float(cm[0]/(cm.sum()+1e-9))
    allf=(dist(m1) or [0]*5)+(dist(m2) or [0]*5)
    om=oldf>0.5; nm=oldf<0.5
    oldd=((dist(m1[om]) or [0]*5)+(dist(m2[om]) or [0]*5)) if om.sum()>=4 else None
    newd=((dist(m1[nm]) or [0]*5)+(dist(m2[nm]) or [0]*5)) if nm.sum()>=4 else None
    return {"M":M,"size":int(e.size),"all":allf,"old":oldd,"new":newd,"newfrac":float(nm.mean())}
CHECK=[0,60,150,300]
D=load(f"{OUT}/phaseA.pkl",[]); seen={(r["seed"],r["hi"],r["br"]) for r in D}
for hi,(a_e,a_l) in enumerate(HH):
    for seed in SEEDS:
        base=None
        for br in BR:
            if (seed,hi,br) in seen: continue
            if not tleft(): save(f"{OUT}/phaseA.pkl",D); print("BUDGET",len(D)); sys.exit()
            if base is None: base=apply2(warm[seed],a_e,a_l)
            st=relabel(base); e=eng(br,PulseChaseTracer()); traj=[]
            for step in range(CHECK[-1]+1):
                if step in CHECK:
                    ck=readck(st)
                    if ck: ck["step"]=step; traj.append(ck)
                st=e.step(st)
            D.append({"seed":seed,"hi":hi,"br":br,"h1":a_e+a_l,"h2":a_l-a_e,"traj":traj}); save(f"{OUT}/phaseA.pkl",D)
print("COMPLETE phaseA n=%d"%len(D))
