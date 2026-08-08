"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 6 DEV pilot: find a NON-MERGING probe (DEV seeds only; POST HOC).

Sweeps behavioural-probe parameters and selects one that measures the effect BEFORE any fusion. Selection uses
GEOMETRIC criteria ONLY (no fusion, no assignment collision, no giant component, target survival, localisation,
bijective tracking) — NEVER the size of the causal effect. DEV seeds 50001-50010 only. No new prospective family.

Geometry metrics per (probe, world), via the corrected bijective tracker + merge detector:
  first_merge step over the full horizon (None = never fuses); n_alive at readout; max grid coverage; min
  pairwise separation of surviving targets.
Levers: mode uniform/local, amplitude, duration, (readout horizon reported separately).
"""
import sys, json, importlib.util, numpy as np
from itertools import combinations
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
mspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(mspec); mspec.loader.exec_module(mr)
bspec = importlib.util.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0; GRID = N * N
WASHOUT_B = cc.WASHOUT_B; HORIZON = 120

DEV = list(range(50001, 50011))
AMPS = [0.50, 0.25, 0.10]
DURS = [15, 5, 1]
MODES = ["uniform", "local"]
COVER_CAP = 0.15   # geometric giant-component cap: max component must stay < 15% of grid

def cache_S0(seed):
    S0, cents, sizes, eng = mr.reconstruct_S0(seed)
    if S0 is None: return None
    sigs = None
    # rebuild the local Gaussian patches at the target centroids (for 'local' probe mode)
    ents = sorted(detect(S0, DET), key=lambda e: -e.size)
    tgt = [cc.nearest(c, ents) for c in cents]
    sigs = [max(3.0, e.rg * 0.8) for e in tgt]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    return dict(S0=S0, cents=cents, eng=eng, pts=pts)

def run_probe(cache, mode, amp, dur, horizon=HORIZON):
    S0 = cache["S0"]; cents = cache["cents"]; eng = cache["eng"]; pts = cache["pts"]
    st = S0.copy(); st.N = np.full_like(st.N, N0)
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks0, _ = cc.region_masks(st, cents)
    fixed = [t.copy() for t in tracks0]
    tr = bt.BijectiveTracker(theta=cc.TRACK_THETA)
    tr.seed(tracks0, 0)
    first_merge = None; max_cov = 0.0
    for t in range(1, horizon + 1):
        if t <= dur:
            if mode == "uniform": st.N = st.N + amp
            else:
                for i in range(K): st.N = st.N + amp * pts[i]     # identical local stimulus around each target
        st = eng.step(st)
        ents = detect(st, DET); emasks = [cc.mask(e) for e in ents]; esz = [int(m.sum()) for m in emasks]
        tr.update(emasks, t)
        max_cov = max(max_cov, (max(esz) if esz else 0) / GRID)
        merged = any(sum(1 for j in range(K) if mr.frac_cover(fixed[j], cm) > 0.5) >= 2 for cm in emasks)
        if merged and first_merge is None: first_merge = t
    s = tr.summary()
    return dict(first_merge=first_merge, n_alive=s["alive"], merged=s["merged"], lost=s["lost"],
                max_cov=max_cov)

def main():
    import pickle, os
    pkl = "/tmp/dev_s0_cache.pkl"
    if os.path.exists(pkl):
        caches = pickle.load(open(pkl, "rb"))
    else:
        caches = {s: c for s in DEV if (c := cache_S0(s)) is not None}
        pickle.dump(caches, open(pkl, "wb"))
    seeds = list(caches); nW = len(seeds)
    print(f"DEV eligible worlds = {nW}: {seeds}\n")
    rows = []
    print(f"{'mode':>8} {'amp':>5} {'dur':>4} | {'noFuse/W':>9} {'all3alive/W':>11} {'meanMaxCov':>10} {'worstCov':>8}")
    for mode in MODES:
        for amp in AMPS:
            for dur in DURS:
                res = [run_probe(caches[s], mode, amp, dur) for s in seeds]
                no_fuse = sum(1 for r in res if r["first_merge"] is None)
                all3 = sum(1 for r in res if r["n_alive"] == K)
                covs = [r["max_cov"] for r in res]
                row = dict(mode=mode, amp=amp, dur=dur, no_fuse=no_fuse, all3=all3, nW=nW,
                           mean_maxcov=float(np.mean(covs)), worst_cov=float(np.max(covs)))
                rows.append(row)
                print(f"{mode:>8} {amp:>5} {dur:>4} | {no_fuse:>4}/{nW:<4} {all3:>6}/{nW:<4} "
                      f"{row['mean_maxcov']*100:>9.1f}% {row['worst_cov']*100:>7.1f}%")
    # ---- GEOMETRIC selection: all worlds non-fusing, all targets alive, worst coverage < cap ----
    valid = [r for r in rows if r["no_fuse"] == nW and r["all3"] == nW and r["worst_cov"] < COVER_CAP]
    # among geometry-valid probes prefer the STRONGEST stimulus (amp*dur) for SNR — geometry-bounded, NOT effect-based
    valid.sort(key=lambda r: (r["amp"] * r["dur"]), reverse=True)
    sel = valid[0] if valid else None
    print(f"\nGEOMETRY-VALID probes (no fusion, all-3 alive, worst coverage<{COVER_CAP*100:.0f}%): {len(valid)}")
    for r in valid[:6]:
        print(f"   mode={r['mode']} amp={r['amp']} dur={r['dur']}  worstCov={r['worst_cov']*100:.1f}%")
    print(f"\nSELECTED (strongest geometry-valid; selection is GEOMETRIC ONLY, not effect-based): {sel}")
    json.dump(dict(dev_worlds=seeds, grid=rows, cover_cap=COVER_CAP, selected=sel,
                   selection_rule="no fusion in ALL DEV worlds AND all-3 targets ALIVE (bijective) AND worst "
                                  "grid coverage < 15%; tie-break strongest amp*dur (geometry-bounded, NOT effect size)"),
              open("work/pilot_nonmerging_dev.json", "w"), indent=2)
    print("\nwrote work/pilot_nonmerging_dev.json")

if __name__ == "__main__":
    main()
