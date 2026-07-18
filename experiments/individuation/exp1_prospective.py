"""EXP-1 LOCAL-CAUSAL-INDIVIDUATION-00 prospective runner (frozen protocol; resumable per seed).
Per seed: warm 800; select K=3 targets (size>=45, pairwise>=24); assign distinct local histories;
drive ALL simultaneously (each its own patch); settle; read per-droplet 11-D memory features + own history.
Also single-perturbation influence matrix C_ij (memory-write) and behavioural footprint (Δuptake)."""
import sys, json, os, numpy as np, itertools
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0); N=C.SPEC.size
K=3; SEP=24.0; MINSIZE=45; WARM=800; PHASE=60; AMP_LO=0.005; AMP_HI=0.035
def build(mem=None): return MultiChannelMemoryEngine(C.SPEC, mem or MCParams(lam_plus=0.25,lam_minus=0.15,**C1c), C.TRACER)
def seed_world(seed):
    s=C.seed_state(C.SPEC,C.TRACER,seed,"random"); return IOMState(s.rho,s.U,s.V,s.c,s.N,s.C,s.uptake,np.zeros((2,N,N)),0)
def pdist(a,b): d=np.abs(np.array(a)-np.array(b)); d=np.minimum(d,N-d); return float(np.hypot(*d))
def patch(cy,cx,sig):
    ys,xs=np.mgrid[0:N,0:N]; dy=np.minimum(np.abs(ys-cy),N-np.abs(ys-cy)); dx=np.minimum(np.abs(xs-cx),N-np.abs(xs-cx))
    return np.exp(-(dy**2+dx**2)/(2*sig**2))
def mask(e): m=np.zeros((N,N),bool); m[e.cells[:,0],e.cells[:,1]]=True; return m
def feats(s,e):
    reg=mask(e); m1=s.Mf[0][reg]/np.maximum(s.rho[reg],1e-9); m2=s.Mf[1][reg]/np.maximum(s.rho[reg],1e-9)
    f=[]
    for v in (m1,m2): f+=[float(v.mean()),float(v.std()),float(np.percentile(v,10)),float(np.percentile(v,50)),float(np.percentile(v,90))]
    f.append(float((m1-m2).std())); return f
def pick(ents):
    ch=[]
    for e in sorted(ents,key=lambda e:-e.size):
        if e.size<MINSIZE: continue
        if all(pdist(e.centroid,o.centroid)>=SEP for o in ch): ch.append(e)
        if len(ch)>=K: break
    return ch
def run_seed(seed):
    rng=np.random.default_rng(seed); eng=build(); st=seed_world(seed)
    for _ in range(WARM): st=eng.step(st)
    T=pick(sorted(detect(st,C.DET),key=lambda e:-e.size))
    if len(T)<K: return {"seed":seed,"ok":False}
    cents=[e.centroid for e in T]; sigs=[max(3.0,e.rg*0.8) for e in T]; sizes=[e.size for e in T]
    pts=[patch(*cents[i],sigs[i]) for i in range(K)]
    hist=[(float(rng.uniform(AMP_LO,AMP_HI)),float(rng.uniform(AMP_LO,AMP_HI))) for _ in range(K)]  # (a1,a2)
    # SIMULTANEOUS drive: all targets, each own local history
    sS=st.copy()
    for ph in (0,1):
        amps=[hist[i][ph] for i in range(K)]
        for _ in range(PHASE):
            for i in range(K): sS.N=sS.N+amps[i]*pts[i]
            sS=eng.step(sS)
    for _ in range(C.SETTLE): sS=eng.step(sS)
    entsS=sorted(detect(sS,C.DET),key=lambda e:-e.size)
    def nearest(c,es): return min(es,key=lambda e:pdist(e.centroid,c))
    feat=[feats(sS,nearest(c,entsS)) for c in cents]
    # single-perturbation influence matrix (memory-write + behavioural), differential vs baseline
    sB=st.copy()
    for _ in range(2*PHASE+C.SETTLE): sB=eng.step(sB)
    mpB=(sB.Mf[0]+sB.Mf[1])/np.maximum(sB.rho,1e-9); upB=sB.uptake.copy()
    entsB=sorted(detect(sB,C.DET),key=lambda e:-e.size); regs=[mask(nearest(c,entsB)) for c in cents]
    Cm=np.zeros((K,K)); Cu=np.zeros((K,K))
    for i in range(K):
        sA=st.copy()
        for ph in (0,1):
            a=hist[i][ph]
            for _ in range(PHASE): sA.N=sA.N+a*pts[i]; sA=eng.step(sA)
        for _ in range(C.SETTLE): sA=eng.step(sA)
        mpA=(sA.Mf[0]+sA.Mf[1])/np.maximum(sA.rho,1e-9); dM=np.abs(mpA-mpB); dU=np.abs(sA.uptake-upB)
        for j in range(K): Cm[i,j]=float(dM[regs[j]].mean()); Cu[i,j]=float(dU[regs[j]].mean())
    return {"seed":seed,"ok":True,"cents":[[float(x) for x in c] for c in cents],"sizes":sizes,
            "hist":hist,"feat":feat,"Cm":Cm.tolist(),"Cu":Cu.tolist(),
            "dists":[pdist(cents[a],cents[b]) for a,b in itertools.combinations(range(K),2)]}
if __name__=="__main__":
    out=sys.argv[1]; seeds=[int(x) for x in sys.argv[2:]]
    data=json.load(open(out)) if os.path.exists(out) else []
    done={d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip",s); continue
        r=run_seed(s); data.append(r); json.dump(data,open(out,"w"))
        print(f"seed {s}: ok={r['ok']}" + ("" if not r['ok'] else f" dists={[round(x,1) for x in r['dists']]}"))
