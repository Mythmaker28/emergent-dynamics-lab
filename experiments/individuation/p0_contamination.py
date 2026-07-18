"""Phase-0 dev pilot: quantify locality of a strictly-local drive on the FROZEN C1c engine.
Differential design (drive vs same-seed no-drive counterfactual) isolates the drive's causal footprint.
No label/future-response is used: the local patch is a fixed spatial Gaussian at a droplet's detected centroid
at drive-onset (detection uses only rho). Measures memory-write contamination target vs neighbour vs far."""
import sys, numpy as np
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect

C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
N = C.SPEC.size
def build(): return MultiChannelMemoryEngine(C.SPEC, MCParams(lam_plus=0.25, lam_minus=0.15, **C1c), C.TRACER)
def seed_world(seed):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, np.zeros((2,N,N)), 0)
def pdist(a, b):
    d = np.abs(np.array(a)-np.array(b)); d = np.minimum(d, N-d); return float(np.hypot(*d))
def gauss_patch(cy, cx, sig):
    ys, xs = np.mgrid[0:N,0:N]
    dy = np.minimum(np.abs(ys-cy), N-np.abs(ys-cy)); dx = np.minimum(np.abs(xs-cx), N-np.abs(xs-cx))
    return np.exp(-(dy**2+dx**2)/(2*sig**2))

warm=int(sys.argv[1]) if len(sys.argv)>1 else 800
drive=int(sys.argv[2]) if len(sys.argv)>2 else 120
amp=float(sys.argv[3]) if len(sys.argv)>3 else 0.03
seed=int(sys.argv[4]) if len(sys.argv)>4 else 50001

eng=build(); st=seed_world(seed)
for _ in range(warm): st=eng.step(st)
ents=sorted(detect(st,C.DET), key=lambda e:-e.size)
tgt=ents[0]; cy,cx=tgt.centroid
others=[e for e in ents[1:] if e.size>=30]
neigh=min(others, key=lambda e:pdist(e.centroid,(cy,cx)))
far=max(others, key=lambda e:pdist(e.centroid,(cy,cx)))
sig=max(3.0, tgt.rg*0.8)
patch=gauss_patch(cy,cx,sig)
print(f"warm={warm} seed={seed} target size={tgt.size} rg={tgt.rg:.1f} sigma={sig:.1f}")
print(f"neighbour dist={pdist(neigh.centroid,(cy,cx)):.1f} (size {neigh.size}); far dist={pdist(far.centroid,(cy,cx)):.1f}")

# two runs from identical state
sA=st.copy(); sB=st.copy()
for _ in range(drive):
    sA.N = sA.N + amp*patch            # LOCAL drive on A only
    sA=eng.step(sA); sB=eng.step(sB)   # B is the matched no-drive counterfactual
# differential memory footprint m_plus = m1+m2
def mplus(s): return (s.Mf[0]+s.Mf[1])/np.maximum(s.rho,1e-9)
dM=np.abs(mplus(sA)-mplus(sB))          # |Δ memory| per cell
def region_mask(e): 
    m=np.zeros((N,N),bool); m[e.cells[:,0],e.cells[:,1]]=True; return m
# use B's (undriven) regions for stable footprints
entsB=sorted(detect(sB,C.DET), key=lambda e:-e.size)
def nearest(cy,cx): return min(entsB,key=lambda e:pdist(e.centroid,(cy,cx)))
mt=region_mask(nearest(cy,cx)); 
mn=region_mask(nearest(*neigh.centroid)); mfar=region_mask(nearest(*far.centroid))
dt=dM[mt].mean(); dn=dM[mn].mean(); df=dM[mfar].mean()
print(f"|Δm| target={dt:.4e}  neighbour={dn:.4e}  far={df:.4e}")
print(f"contamination  neighbour/target={dn/dt:.3f}   far/target={df/dt:.3f}")
# field diffusion footprint
dN=np.abs(sA.N-sB.N); dc=np.abs(sA.c-sB.c)
print(f"|ΔN| target={dN[mt].mean():.4e} neigh={dN[mn].mean():.4e} far={dN[mfar].mean():.4e}")
print(f"|Δc| target={dc[mt].mean():.4e} neigh={dc[mn].mean():.4e} far={dc[mfar].mean():.4e}")
# global up_ref coupling: mean-uptake shift caused by driving one droplet
print(f"global up_ref shift: mean uptake A={sA.uptake[sA.rho>1e-4].mean():.4e} B={sB.uptake[sB.rho>1e-4].mean():.4e}")
