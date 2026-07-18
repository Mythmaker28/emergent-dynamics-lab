"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — Phase 3 power exploration (DEV; sizes the family, NOT a claim).

Reuses cached DEV S0 snapshots. For the frozen probe (uniform 0.25x5), runs intact/erase_j/sham branches with the
bijective tracker, recording the cumulative TRACKED readout at horizon checkpoints. Estimates world-level effect
size and SD for the paired contrasts own(=intact-eraseTarget), own-sham, own-neighbour, and the number of VALID
worlds needed for a one-sided worldboot lower bound > 0 at power ~0.8. Also picks the behavioural horizon by
power (geometry is safe at all these horizons for 0.25x5). The causal effect is used ONLY for sizing, never to
pick the probe, and yields NO positive claim.
"""
import json, importlib.util, pickle, numpy as np
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
bspec = importlib.util.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; N0 = cc.N0; GRID = N * N
AMP = 0.25; DUR = 5; SETTLE_STD = 40; THETA = cc.TRACK_THETA
CKPTS = [30, 40, 60, 80, 120]

def branch(cache, erase_j=None):
    S0 = cache["S0"]; cents = cache["cents"]; eng = cache["eng"]
    st = S0.copy()
    if erase_j is not None:
        reg0, _ = cc.region_masks(st, cents); st.Mf[:, reg0[erase_j]] = 0.0
    st.N = np.full_like(st.N, N0)
    for _ in range(SETTLE_STD): st = eng.step(st)
    tracks0, _ = cc.region_masks(st, cents); tr = bt.BijectiveTracker(theta=THETA); tr.seed(tracks0, 0)
    integ = [0.0] * K; ck = {c: None for c in CKPTS}
    for t in range(1, max(CKPTS) + 1):
        if t <= DUR: st.N = st.N + AMP
        st = eng.step(st)
        comps = [cc.mask(e) for e in detect(st, DET)]; tr.update(comps, t)
        for i in range(K):
            if tr.tracks[i].status == bt.ALIVE: integ[i] += float(st.uptake[tr.tracks[i].mask].sum())
        if t in ck: ck[t] = list(integ)
    return ck

def need_n(mean, sd):
    if mean <= 0 or sd == 0: return None
    return (2.8 * sd / mean) ** 2   # one-sided alpha=0.025, power 0.8

def main():
    caches = pickle.load(open("/tmp/dev_s0_cache.pkl", "rb"))
    seeds = list(caches)
    # compute branches (intact, erase_j) once per seed; sham computed with the real empty patch below
    data = {}
    for s in seeds:
        data[s] = dict(intact=branch(caches[s]), sham=branch(caches[s], erase_j=None),
                       erase=[branch(caches[s], erase_j=j) for j in range(K)])
        # NB sham here uses empty-patch? For power we approximate sham≈intact baseline is wrong; use real empty patch:
    # recompute sham with the real empty-patch erase
    for s in seeds:
        cache = caches[s]; S0 = cache["S0"]; cents = cache["cents"]
        empty = cc.empty_patch_mask(S0, cents)
        # replicate branch() but with erase_mask=empty
        eng = cache["eng"]; st = S0.copy(); st.Mf[:, empty] = 0.0; st.N = np.full_like(st.N, N0)
        for _ in range(SETTLE_STD): st = eng.step(st)
        tracks0, _ = cc.region_masks(st, cents); tr = bt.BijectiveTracker(theta=THETA); tr.seed(tracks0, 0)
        integ = [0.0] * K; ck = {c: None for c in CKPTS}
        for t in range(1, max(CKPTS) + 1):
            if t <= DUR: st.N = st.N + AMP
            st = eng.step(st)
            comps = [cc.mask(e) for e in detect(st, DET)]; tr.update(comps, t)
            for i in range(K):
                if tr.tracks[i].status == bt.ALIVE: integ[i] += float(st.uptake[tr.tracks[i].mask].sum())
            if t in ck: ck[t] = list(integ)
        data[s]["sham"] = ck

    print(f"DEV worlds={len(seeds)}  (world = mean over 3 targets)")
    print(f"{'H':>4} | {'own mean±sd':>16} {'need_n':>7} | {'own-sham mean±sd':>18} {'need_n':>7} | {'own-neigh mean±sd':>18} {'need_n':>7}")
    out = {"probe": "uniform 0.25x5", "checkpoints": CKPTS, "per_horizon": {}}
    for H in CKPTS:
        own_w = []; osh_w = []; one_w = []
        for s in seeds:
            A = data[s]["intact"][H]; S = data[s]["sham"][H]; ers = [data[s]["erase"][j][H] for j in range(K)]
            own = [A[i] - ers[i][i] for i in range(K)]
            sham = [A[i] - S[i] for i in range(K)]
            neigh = [np.mean([A[i] - ers[j][i] for j in range(K) if j != i]) for i in range(K)]
            own_w.append(np.mean(own)); osh_w.append(np.mean([own[i] - sham[i] for i in range(K)]))
            one_w.append(np.mean([own[i] - neigh[i] for i in range(K)]))
        own_w = np.array(own_w); osh_w = np.array(osh_w); one_w = np.array(one_w)
        def fmt(a): return f"{a.mean():+.3f}±{a.std(ddof=1):.3f}"
        no = need_n(own_w.mean(), own_w.std(ddof=1)); ns = need_n(osh_w.mean(), osh_w.std(ddof=1)); nn = need_n(one_w.mean(), one_w.std(ddof=1))
        print(f"{H:>4} | {fmt(own_w):>16} {('%.1f'%no) if no else 'na':>7} | {fmt(osh_w):>18} {('%.1f'%ns) if ns else 'na':>7} | {fmt(one_w):>18} {('%.1f'%nn) if nn else 'na':>7}")
        out["per_horizon"][H] = dict(own=[own_w.mean(), own_w.std(ddof=1)], own_sham=[osh_w.mean(), osh_w.std(ddof=1)],
                                     own_neigh=[one_w.mean(), one_w.std(ddof=1)],
                                     need_n_own=no, need_n_ownsham=ns, need_n_ownneigh=nn,
                                     own_pos=int((own_w > 0).sum()), ownsham_pos=int((osh_w > 0).sum()),
                                     ownneigh_pos=int((one_w > 0).sum()), nW=len(seeds))
    json.dump(out, open("work/power_explore.json", "w"), indent=2)
    print("\nneed_n = valid worlds for one-sided worldboot lower>0 at power~0.8 (n=(2.8*sd/mean)^2).")
    print("wrote work/power_explore.json")

if __name__ == "__main__":
    main()
