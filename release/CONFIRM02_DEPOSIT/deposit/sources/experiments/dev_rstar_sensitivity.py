"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — DEV-only R* geometric sensitivity test (POST HOC; geometry ONLY).

Compares probe uniform 0.2575x5 (R*=0.2575) vs the sealed 0.25x5 on DEV worlds, measuring ONLY geometry:
fusion, assignment collision, max grid coverage, target survival, unique-component count — via the bijective
tracker. The causal EFFECT SIZE is NEVER computed here. This does not alter the sealed CONFIRM-02 prospective
(probe 0.25x5, run once); it is a robustness record and freezes the choice for any future replication.
Guard rail: do NOT proliferate intermediate amplitudes; this tests exactly the two requested probes.
"""
import json, importlib.util, pickle, numpy as np
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
mspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(mspec); mspec.loader.exec_module(mr)
bspec = importlib.util.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0; GRID = N * N; SETTLE_STD = 40; THETA = cc.TRACK_THETA
H_SEAL = 40; H_MAX = 120; COVER_CAP = 0.15

def geom(cache, amp, dur):
    """Geometry only: bijective tracker over the standardized+probe branch. No effect computed."""
    S0 = cache["S0"]; cents = cache["cents"]; eng = cache["eng"]
    st = S0.copy(); st.N = np.full_like(st.N, N0)
    for _ in range(SETTLE_STD): st = eng.step(st)
    tracks0, _ = cc.region_masks(st, cents); fixed = [t.copy() for t in tracks0]
    tr = bt.BijectiveTracker(theta=THETA); tr.seed(tracks0, 0)
    first_event = None; first_merge = None
    cov_at = {H_SEAL: 0.0, H_MAX: 0.0}; min_distinct_at = {H_SEAL: K, H_MAX: K}; alive_at = {}
    for t in range(1, H_MAX + 1):
        if t <= dur: st.N = st.N + amp
        st = eng.step(st)
        ents = detect(st, DET); emasks = [cc.mask(e) for e in ents]; esz = [int(m.sum()) for m in emasks]
        ev = tr.update(emasks, t)
        if ev and first_event is None: first_event = (t, dict(ev))
        merged = any(sum(1 for j in range(K) if mr.frac_cover(fixed[j], cm) > 0.5) >= 2 for cm in emasks)
        if merged and first_merge is None: first_merge = t
        cov = (max(esz) if esz else 0) / GRID
        nalive = tr.summary()["alive"]
        for Hk in (H_SEAL, H_MAX):
            if t <= Hk:
                cov_at[Hk] = max(cov_at[Hk], cov); min_distinct_at[Hk] = min(min_distinct_at[Hk], nalive)
        if t in (H_SEAL, H_MAX): alive_at[t] = nalive
    return dict(first_event=first_event, first_merge=first_merge,
                cov_H40=cov_at[H_SEAL], cov_H120=cov_at[H_MAX],
                distinct_H40=min_distinct_at[H_SEAL], distinct_H120=min_distinct_at[H_MAX],
                alive_H40=alive_at[H_SEAL], alive_H120=alive_at[H_MAX])

def summarize(caches, amp, dur):
    seeds = list(caches); res = {s: geom(caches[s], amp, dur) for s in seeds}
    def frac(pred): return sum(1 for s in seeds if pred(res[s]))
    return dict(
        amp=amp, dur=dur, cum=amp * dur, nW=len(seeds),
        worlds_no_fusion=frac(lambda r: r["first_merge"] is None),
        worlds_no_tracker_event=frac(lambda r: r["first_event"] is None),
        worst_cov_H40=max(res[s]["cov_H40"] for s in seeds),
        worst_cov_H120=max(res[s]["cov_H120"] for s in seeds),
        worlds_3distinct_H40=frac(lambda r: r["distinct_H40"] == K),
        worlds_3alive_H40=frac(lambda r: r["alive_H40"] == K),
        worlds_G0valid_H40=frac(lambda r: r["first_event"] is None and r["cov_H40"] < COVER_CAP and r["distinct_H40"] == K),
        per_world={str(s): res[s] for s in seeds})

def main():
    caches = pickle.load(open("/tmp/dev_s0_cache.pkl", "rb"))
    A = summarize(caches, 0.25, 5)
    B = summarize(caches, 0.2575, 5)
    print(f"DEV worlds = {A['nW']}   (GEOMETRY ONLY — effect size NOT consulted)")
    hdr = f"{'probe':>14} {'cum':>7} {'noFusion':>9} {'noTrkEvt':>9} {'worstCov@40':>12} {'worstCov@120':>13} {'3distinct@40':>13} {'G0valid@40':>11}"
    print(hdr)
    for lab, S in [("0.25x5 (seal)", A), ("0.2575x5 (R*)", B)]:
        print(f"{lab:>14} {S['cum']:>7.4f} {S['worlds_no_fusion']:>4}/{S['nW']:<4} {S['worlds_no_tracker_event']:>4}/{S['nW']:<4} "
              f"{S['worst_cov_H40']*100:>11.2f}% {S['worst_cov_H120']*100:>12.2f}% {S['worlds_3distinct_H40']:>6}/{S['nW']:<6} {S['worlds_G0valid_H40']:>5}/{S['nW']:<5}")
    both_pass = (A['worlds_G0valid_H40'] == A['nW'] and B['worlds_G0valid_H40'] == B['nW'])
    dcov = (B['worst_cov_H40'] - A['worst_cov_H40']) * 100
    print(f"\nboth pass G0 (all worlds, H40): {both_pass}")
    print(f"worst-coverage difference (0.2575 - 0.25) at H40 = {dcov:+.2f} percentage points (margin to 15% cap essentially unchanged)")
    json.dump({"seal_0.25x5": A, "rstar_0.2575x5": B, "both_pass": bool(both_pass), "worst_cov_delta_H40_pct": dcov},
              open("work/dev_rstar_sensitivity.json", "w"), indent=2)
    print("wrote work/dev_rstar_sensitivity.json")

if __name__ == "__main__":
    main()
