"""K3 maintenance-through-turnover: after simultaneous local drive, track each target by frozen overlap
tracker through renewal; re-read memory features at deep turnover; decode own history from renewed features."""
import sys, json, os, numpy as np
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0); N=C.SPEC.size
K=3; SEP=24.0; MINSIZE=45; WARM=800; PHASE=60; AMP_LO=0.005; AMP_HI=0.035; TURN=600; k_death=C.SPEC.k
def build(): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**C1c),C.TRACER)
def seed_world(seed):
    s=C.seed_state(C.SPEC,C.TRACER,seed,"random"); return IOMState(s.rho,s.U,s.V,s.c,s.N,s.C,s.uptake,np.zeros((2,N,N)),0)
def pdist(a,b): d=np.abs(np.array(a)-np.array(b)); d=np.minimum(d,N-d); return float(np.hypot(*d))
def patch(cy,cx,sig):
    ys,xs=np.mgrid[0:N,0:N]; dy=np.minimum(np.abs(ys-cy),N-np.abs(ys-cy)); dx=np.minimum(np.abs(xs-cx),N-np.abs(xs-cx))
    return np.exp(-(dy**2+dx**2)/(2*sig**2))
def mask(e): m=np.zeros((N,N),bool); m[e.cells[:,0],e.cells[:,1]]=True; return m
def overlap(m,e):
    em=mask(e); return (m&em).sum()/max(1,m.sum())
def feats(s,reg):
    m1=s.Mf[0][reg]/np.maximum(s.rho[reg],1e-9); m2=s.Mf[1][reg]/np.maximum(s.rho[reg],1e-9); f=[]
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
    cents=[e.centroid for e in T]; sigs=[max(3.0,e.rg*0.8) for e in T]
    pts=[patch(*cents[i],sigs[i]) for i in range(K)]
    hist=[(float(rng.uniform(AMP_LO,AMP_HI)),float(rng.uniform(AMP_LO,AMP_HI))) for _ in range(K)]
    for ph in (0,1):
        for _ in range(PHASE):
            for i in range(K): st.N=st.N+hist[i][ph]*pts[i]
            st=eng.step(st)
    for _ in range(C.SETTLE): st=eng.step(st)
    # init tracks from targets
    entsS=sorted(detect(st,C.DET),key=lambda e:-e.size)
    tracks=[mask(min(entsS,key=lambda e:pdist(e.centroid,c))) for c in cents]
    alive=[True]*K
    for t in range(TURN):
        st=eng.step(st)
        if t%5==4:
            ents=detect(st,C.DET)
            for i in range(K):
                if not alive[i]: continue
                best=max(ents,key=lambda e:overlap(tracks[i],e),default=None)
                if best is None or overlap(tracks[i],best)<0.1: alive[i]=False
                else: tracks[i]=mask(best)
    Mest=(1-k_death*C.SPEC.dt)**TURN
    feat_deep=[feats(st,tracks[i]) if alive[i] else None for i in range(K)]
    return {"seed":seed,"ok":True,"hist":hist,"feat_deep":feat_deep,"alive":alive,"M_est":float(Mest)}
if __name__=="__main__":
    out=sys.argv[1]; seeds=[int(x) for x in sys.argv[2:]]
    data=json.load(open(out)) if os.path.exists(out) else []
    done={d["seed"] for d in data}
    for s in seeds:
        if s in done: print("skip",s); continue
        r=run_seed(s); data.append(r); json.dump(data,open(out,"w"))
        print(f"seed {s}: ok={r['ok']}"+("" if not r['ok'] else f" alive={sum(r['alive'])}/{K} M~{r['M_est']:.2f}"))
