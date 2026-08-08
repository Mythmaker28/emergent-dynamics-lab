"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — Phase 0 independent geometric characterization (DEV; geometry only).

For each candidate probe, replay the standardized branch on DEV worlds with the bijective tracker and record,
per step: max grid coverage, # unique components occupied by the 3 targets, min pairwise target separation,
tracker events. Purpose: pick the probe and behavioural horizon by GEOMETRY ONLY (margin to the 15% cap, no
fusion/collision/LOST, target survival, localisation). The causal effect is NOT consulted here.
"""
import sys, json, importlib.util, pickle, numpy as np
from itertools import combinations
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
mspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(mspec); mspec.loader.exec_module(mr)
bspec = importlib.util.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0; GRID = N * N; WASHOUT_B = cc.WASHOUT_B
HMAX = 120

def _centroid(m):
    ys, xs = np.where(m)
    if len(ys) == 0: return None
    def cm(v):
        ang = v / N * 2 * np.pi
        a = np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())
        return (a % (2 * np.pi)) / (2 * np.pi) * N
    return (cm(ys), cm(xs))

def run(cache, mode, amp, dur):
    S0 = cache["S0"]; cents = cache["cents"]; eng = cache["eng"]; pts = cache["pts"]
    st = S0.copy(); st.N = np.full_like(st.N, N0)
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks0, _ = cc.region_masks(st, cents); fixed = [t.copy() for t in tracks0]
    tr = bt.BijectiveTracker(theta=cc.TRACK_THETA); tr.seed(tracks0, 0)
    per_t = []
    first_bad = None
    for t in range(1, HMAX + 1):
        if t <= dur:
            if mode == "uniform": st.N = st.N + amp
            else:
                for i in range(K): st.N = st.N + amp * pts[i]
        st = eng.step(st)
        ents = detect(st, DET); emasks = [cc.mask(e) for e in ents]; esz = [int(m.sum()) for m in emasks]
        ev = tr.update(emasks, t)
        if ev and first_bad is None: first_bad = (t, dict(ev))
        # geometry
        occ = set()
        for j in range(K):
            bc = max(range(len(emasks)), key=lambda ci: mr.frac_cover(fixed[j], emasks[ci]), default=-1)
            if bc >= 0 and mr.frac_cover(fixed[j], emasks[bc]) > 0.30: occ.add(bc)
        alive = [tk for tk in tr.tracks if tk.status == bt.ALIVE]
        cds = [cc.pdist(_centroid(a.mask), _centroid(b.mask)) for a, b in combinations(alive, 2)
               if _centroid(a.mask) and _centroid(b.mask)]
        per_t.append((t, (max(esz) if esz else 0) / GRID, len(occ), min(cds) if cds else 0.0,
                      tr.summary()["alive"]))
    return per_t, first_bad

def main():
    caches = pickle.load(open("/tmp/dev_s0_cache.pkl", "rb"))
    seeds = list(caches); nW = len(seeds)
    probes = [("uniform", 0.25, 15), ("uniform", 0.25, 5), ("uniform", 0.20, 5),
              ("local", 0.5, 15), ("uniform", 0.25, 1)]
    horizons = [40, 60, 80, 120]
    print(f"DEV worlds={nW}")
    print(f"{'probe':>18} | {'cumInj':>6} | for H in {horizons}: worstCov%  (allValid? distinct=3 & alive=3 & no-bad)")
    out = {}
    for mode, amp, dur in probes:
        runs = {s: run(caches[s], mode, amp, dur) for s in seeds}
        cum = amp * dur
        row = {"mode": mode, "amp": amp, "dur": dur, "cum_injection": cum, "by_horizon": {}}
        cells = []
        for H in horizons:
            worst_cov = 0.0; all_valid = True; min_sep = 1e9
            for s in seeds:
                per_t, first_bad = runs[s]
                sub = [x for x in per_t if x[0] <= H]
                cov = max(x[1] for x in sub); worst_cov = max(worst_cov, cov)
                distinct_ok = all(x[2] == 3 for x in sub)
                alive_ok = sub[-1][4] == 3
                bad_ok = (first_bad is None) or (first_bad[0] > H)
                min_sep = min(min_sep, min(x[3] for x in sub))
                if not (distinct_ok and alive_ok and bad_ok): all_valid = False
            row["by_horizon"][H] = dict(worst_cov=worst_cov, all_valid=all_valid, min_sep=min_sep)
            cells.append(f"H{H}:{worst_cov*100:4.1f}%{'OK' if all_valid else 'XX'}")
        out[f"{mode}_{amp}x{dur}"] = row
        print(f"{mode+' '+str(amp)+'x'+str(dur):>18} | {cum:>6.2f} | " + "  ".join(cells))
    json.dump(out, open("work/geom_char.json", "w"), indent=2)
    print("\nLegend: worstCov = worst-world max grid coverage up to horizon H; OK = all DEV worlds keep 3 distinct")
    print("        components, 3 alive, and no MERGE/SPLIT/LOST/AMBIGUOUS through H. Cap = 15%.")
    print("wrote work/geom_char.json")

if __name__ == "__main__":
    main()
