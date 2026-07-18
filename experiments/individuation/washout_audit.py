"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 5 washout residual audit (POST HOC; committed).

Quantifies the ACTUAL residual nutrient ΔN (drive world minus no-drive counterfactual, as a fraction of N0) as a
function of natural-washout steps, on the sealed platform. Tests two things the CAUSAL_CONFIRMATION docs assert:
  - Independent View §4: preinscribed natural washout to residual ΔN < 2% of N0, estimated ~800 steps
    (committed curve: +0→53% ; +120→30% ; +300→13% ; +600→3.2% ; +1000→0.13%).
  - PRESEAL froze WASHOUT_LONG = 200 for the "survives washout" gate (G3f).
Reproduces the curve and reads off the residual AT 200 steps. No new physics.
"""
import sys, json, importlib.util, numpy as np
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
mspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(mspec); mspec.loader.exec_module(mr)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0

CHECKPOINTS = [0, 40, 120, 200, 300, 400, 600, 800, 1000]

def residual_curve(seed):
    """Return mean residual ΔN/N0 over the 3 target regions at each checkpoint of natural washout."""
    rng = np.random.default_rng(seed)
    eng = cc.build(cc.MEM_INTACT); st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    if len(T) < K: return None
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    # DRIVE world -> S0
    sD = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(cc.PHASE):
            for i in range(K): sD.N = sD.N + amps[i] * pts[i]
            sD = eng.step(sD)
    for _ in range(cc.SETTLE): sD = eng.step(sD)
    # NO-DRIVE world matched in time (2*PHASE + SETTLE), no history injection
    sB = st.copy()
    for _ in range(2 * cc.PHASE + cc.SETTLE): sB = eng.step(sB)
    # region masks fixed at S0 (post-drive) target geometry
    regs = [cc.mask(cc.nearest(c, sorted(detect(sD, DET), key=lambda e: -e.size))) for c in cents]
    out = {}
    nextcp = set(CHECKPOINTS)
    for step in range(0, max(CHECKPOINTS) + 1):
        if step in nextcp:
            res = np.mean([float((sD.N[regs[i]].mean() - sB.N[regs[i]].mean()) / N0) for i in range(K)])
            out[step] = res
        if step == max(CHECKPOINTS): break
        sD = eng.step(sD); sB = eng.step(sB)   # natural evolution, NO reset, NO stimulus
    return out

def main():
    seeds = [int(x) for x in sys.argv[1:]] or [52001, 52005, 52008, 52012, 52010]
    curves = {}
    for s in seeds:
        c = residual_curve(s)
        if c: curves[s] = c
    steps = CHECKPOINTS
    mean = {t: float(np.mean([curves[s][t] for s in curves])) for t in steps}
    print(f"seeds={list(curves)}   residual ΔN as % of N0, natural washout (no reset):")
    print("  step :  " + "  ".join(f"{t:>5}" for t in steps))
    print("  %N0  :  " + "  ".join(f"{mean[t]*100:5.1f}" for t in steps))
    print(f"\n  --> residual at frozen WASHOUT_LONG=200 : {mean[200]*100:.1f}% of N0")
    print(f"  --> Independent View target (<2% of N0) reached near ~{next((t for t in steps if mean[t]<0.02), '>1000')} steps")
    print(f"  --> Independent View committed curve: 0->53% 120->30% 300->13% 600->3.2% 1000->0.13%")
    out = dict(seeds=list(curves), checkpoints=steps, mean_residual_frac={str(t): mean[t] for t in steps},
               residual_at_200=mean[200], per_seed={str(s): {str(t): curves[s][t] for t in steps} for s in curves},
               interpretation=dict(
                   frozen_washout_long=200,
                   residual_at_frozen_washout_pct=mean[200] * 100,
                   independent_view_target="<2% of N0 (~800 steps)",
                   discrepancy=("the frozen 200-step washout leaves ~%.0f%% residual N0, NOT <2%%; the standardized "
                                "branches instead remove residual by an explicit N:=N0 RESET (WASHOUT_B=40), so "
                                "'suppression du résidu' is achieved by the reset, not by the 200-step washout" ) % (mean[200] * 100)))
    json.dump(out, open("work/washout_audit.json", "w"), indent=2)
    print("\nwrote work/washout_audit.json")

if __name__ == "__main__":
    main()
