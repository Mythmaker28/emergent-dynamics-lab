"""Dev influence matrix C_ij: memory-write footprint in droplet j when a strictly-local drive perturbs i.
Well-separated targets (pairwise >= SEP). Differential vs same-seed no-drive baseline. Diagonal dominance."""
import sys, numpy as np, itertools
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect
C1c=dict(eta_w=0.015,eta_d1=0.35,eta_d2=0.006,k_exp=1.0); N=C.SPEC.size
def build(): return MultiChannelMemoryEngine(C.SPEC,MCParams(lam_plus=0.25,lam_minus=0.15,**C1c),C.TRACER)
def seed_world(seed):
    s=C.seed_state(C.SPEC,C.TRACER,seed,"random"); return IOMState(s.rho,s.U,s.V,s.c,s.N,s.C,s.uptake,np.zeros((2,N,N)),0)
def pdist(a,b): d=np.abs(np.array(a)-np.array(b)); d=np.minimum(d,N-d); return float(np.hypot(*d))
def patch(cy,cx,sig):
    ys,xs=np.mgrid[0:N,0:N]; dy=np.minimum(np.abs(ys-cy),N-np.abs(ys-cy)); dx=np.minimum(np.abs(xs-cx),N-np.abs(xs-cx))
    return np.exp(-(dy**2+dx**2)/(2*sig**2))
def mask(e): m=np.zeros((N,N),bool); m[e.cells[:,0],e.cells[:,1]]=True; return m
def pick_targets(ents, K, SEP, minsize):
    cand=[e for e in ents if e.size>=minsize]; chosen=[]
    for e in cand:
        if all(pdist(e.centroid,o.centroid)>=SEP for o in chosen): chosen.append(e)
        if len(chosen)>=K: break
    return chosen
def influence(seed, K=3, SEP=24, drive=120, amp=0.03, warm=800, minsize=45):
    eng=build(); st=seed_world(seed)
    for _ in range(warm): st=eng.step(st)
    ents=sorted(detect(st,C.DET),key=lambda e:-e.size)
    T=pick_targets(ents,K,SEP,minsize)
    if len(T)<K: return None
    sigs=[max(3.0,e.rg*0.8) for e in T]; cents=[e.centroid for e in T]
    # baseline (no drive)
    sB=st.copy()
    for _ in range(drive): sB=eng.step(sB)
    mpB=(sB.Mf[0]+sB.Mf[1])/np.maximum(sB.rho,1e-9)
    entsB=sorted(detect(sB,C.DET),key=lambda e:-e.size)
    regions=[mask(min(entsB,key=lambda e:pdist(e.centroid,c))) for c in cents]
    Cmat=np.zeros((K,K))
    for i in range(K):
        sA=st.copy(); pt=patch(*cents[i],sigs[i])
        for _ in range(drive): sA.N=sA.N+amp*pt; sA=eng.step(sA)
        mpA=(sA.Mf[0]+sA.Mf[1])/np.maximum(sA.rho,1e-9); dM=np.abs(mpA-mpB)
        for j in range(K): Cmat[i,j]=dM[regions[j]].mean()
    return Cmat, [pdist(cents[a],cents[b]) for a,b in itertools.combinations(range(K),2)]
for seed in (50001,50002):
    r=influence(seed)
    if r is None: print(f"seed {seed}: <K well-separated targets"); continue
    Cmat,ds=r
    diag=np.diag(Cmat); off=Cmat[~np.eye(len(Cmat),dtype=bool)]
    dd=diag.mean()/ (np.abs(off).mean()+1e-12)
    print(f"seed {seed}: pairwise dists={[round(d,1) for d in ds]}")
    print("  C_ij (row=perturbed i, col=measured j), rows normalized by diagonal:")
    for i in range(len(Cmat)):
        print("   ", " ".join(f"{Cmat[i,j]/Cmat[i,i]:5.3f}" for j in range(len(Cmat))))
    print(f"  diagonal dominance mean(diag)/mean(|off|) = {dd:.1f}")
