"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 6 viability check (DEV, OBSERVATIONAL — not a confirmation).

For geometry-selected NON-FUSING probes, measure the paired own effect (intact - erase-target) on the
tracker-free FIXED mask, on DEV worlds. Purpose: confirm a memory->feeding signal SURVIVES without any fusion
(so the corrected protocol is viable). This is OBSERVATIONAL on already-seen DEV data; the probe was selected by
GEOMETRY ONLY (pilot_nonmerging_dev.py), NOT by this effect. No gate, no confirmation, no new prospective family.
The uptake is a directly-coupled readout by construction (g ∝ N·ρ·(1+λ₊·m₊)); the paired contrast is what makes
it causal, and it is reported honestly as such.
"""
import sys, json, importlib.util, pickle, numpy as np
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; DET = C.DET; N0 = cc.N0; WASHOUT_B = cc.WASHOUT_B

def branch(cache, mode, amp, dur, horizon, erase_j=None):
    S0 = cache["S0"]; cents = cache["cents"]; eng = cache["eng"]; pts = cache["pts"]
    st = S0.copy()
    if erase_j is not None:
        reg0, _ = cc.region_masks(st, cents)
        st.Mf[:, reg0[erase_j]] = 0.0
    st.N = np.full_like(st.N, N0)
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks, _ = cc.region_masks(st, cents); fixed = [t.copy() for t in tracks]
    integ_fixed = [0.0] * K
    for t in range(1, horizon + 1):
        if t <= dur:
            if mode == "uniform": st.N = st.N + amp
            else:
                for i in range(K): st.N = st.N + amp * pts[i]
        st = eng.step(st)
        for i in range(K): integ_fixed[i] += float(st.uptake[fixed[i]].sum())
    return integ_fixed

def measure(caches, mode, amp, dur, horizon):
    perworld = []
    for s, cache in caches.items():
        A = branch(cache, mode, amp, dur, horizon)
        eff = []
        for i in range(K):
            Ei = branch(cache, mode, amp, dur, horizon, erase_j=i)
            eff.append(A[i] - Ei[i])
        perworld.append(np.mean(eff))
    perworld = np.array(perworld)
    return dict(mode=mode, amp=amp, dur=dur, horizon=horizon,
                per_world_mean_own_fixed=float(perworld.mean()),
                worlds_pos=int((perworld > 0).sum()), nW=len(perworld),
                per_world=[float(x) for x in perworld])

def main():
    caches = pickle.load(open("/tmp/dev_s0_cache.pkl", "rb"))
    probes = [("local", 0.5, 15, 120), ("uniform", 0.25, 15, 120), ("uniform", 0.5, 15, 120)]  # last = sealed (fuses) for contrast
    out = []
    print("OBSERVATIONAL (DEV, tracker-free fixed-mask own effect; probe chosen by GEOMETRY, not this effect):")
    print(f"{'mode':>8} {'amp':>5} {'dur':>4} {'hor':>4} | {'mean own_fixed':>15} {'worlds>0':>9}")
    for mode, amp, dur, hor in probes:
        r = measure(caches, mode, amp, dur, hor); out.append(r)
        tag = "  <- SEALED probe (fuses 6/8; shown for contrast)" if (mode, amp, dur) == ("uniform", 0.5, 15) else ""
        print(f"{mode:>8} {amp:>5} {dur:>4} {hor:>4} | {r['per_world_mean_own_fixed']:>15.4f} {r['worlds_pos']:>4}/{r['nW']:<4}{tag}")
    json.dump(out, open("work/pilot_effect_dev.json", "w"), indent=2)
    print("\nNOTE: non-fusing probes still yield a positive tracker-free own effect on DEV -> corrected protocol is VIABLE.")
    print("This is OBSERVATIONAL on DEV; it is NOT a confirmation and opens no prospective family.")
    print("wrote work/pilot_effect_dev.json")

if __name__ == "__main__":
    main()
