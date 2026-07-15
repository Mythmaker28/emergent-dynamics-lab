"""Contamination vs distance: |Δmemory| in every droplet relative to the driven target, differential design."""
import sys, numpy as np
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
def run(seed,warm=800,drive=120,amp=0.03):
    eng=build(); st=seed_world(seed)
    for _ in range(warm): st=eng.step(st)
    ents=sorted(detect(st,C.DET),key=lambda e:-e.size); tgt=ents[0]; cy,cx=tgt.centroid
    sig=max(3.0,tgt.rg*0.8); pt=patch(cy,cx,sig)
    sA=st.copy(); sB=st.copy()
    for _ in range(drive):
        sA.N=sA.N+amp*pt; sA=eng.step(sA); sB=eng.step(sB)
    mp=lambda s:(s.Mf[0]+s.Mf[1])/np.maximum(s.rho,1e-9); dM=np.abs(mp(sA)-mp(sB))
    entsB=sorted(detect(sB,C.DET),key=lambda e:-e.size)
    tref=min(entsB,key=lambda e:pdist(e.centroid,(cy,cx))); base=dM[mask(tref)].mean()
    rows=[]
    for e in entsB:
        if e.size<30: continue
        rows.append((pdist(e.centroid,(cy,cx)), dM[mask(e)].mean()/base))
    return sorted(rows)
for seed in (50001,50002,50003):
    rows=run(seed)
    # bin by distance
    print(f"seed {seed}: contamination |Δm|/target vs distance")
    for d,r in rows[:10]:
        bar='#'*int(min(40,r*40))
        print(f"  dist={d:5.1f}  rel={r:6.3f} {bar}")
