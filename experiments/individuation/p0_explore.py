"""Phase-0 exploration: how many droplets self-organize, timing, field structure. Frozen C1c engine."""
import sys, time, numpy as np
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine, MCParams
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_iom.engine import IOMState
from edlab.substrates.scaffold.observables import detect

C1c = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)   # frozen writing
def build(): return MultiChannelMemoryEngine(C.SPEC, MCParams(lam_plus=0.25, lam_minus=0.15, **C1c), C.TRACER)
def seed_world(seed):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    Mf = np.zeros((2, C.SPEC.size, C.SPEC.size))
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, Mf, 0)

steps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 50001
eng = build(); st = seed_world(seed)
t0 = time.time()
for _ in range(steps): st = eng.step(st)
dt = time.time() - t0
ents = detect(st, C.DET)
print(f"seed {seed}: {steps} steps in {dt:.2f}s ({1000*dt/steps:.1f} ms/step)")
print(f"world {C.SPEC.size}x{C.SPEC.size}; entities detected: {len(ents)}")
for i, e in enumerate(sorted(ents, key=lambda e: -e.size)[:8]):
    print(f"  ent{i}: size={e.size} mass={e.mass:.1f} centroid=({e.centroid[0]:.1f},{e.centroid[1]:.1f}) rg={e.rg:.1f}")
print(f"total rho mass={st.rho.sum():.1f}  N mean={st.N.mean():.3f}  c mean={st.c.mean():.3f}")
