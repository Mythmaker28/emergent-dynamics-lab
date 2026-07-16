"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 3/4 bridge: apply the bijective tracker to the sealed intact branch (POST HOC).

For every eligible confirmation world, replay the intact standardized branch (sealed path) and track the 3 targets
with the CORRECTED bijective/censoring tracker (geometry only). Report how many of the 39 nominal targets remain
ALIVE (distinct individual) at readout vs are censored MERGED/SPLIT/LOST, and the censorship step. This is a POST
HOC diagnostic of the tracking claim ("39/39", "13/13 robust") — NOT a new confirmation.
"""
import sys, json, importlib.util, numpy as np
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
mspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(mspec); mspec.loader.exec_module(mr)
bspec = importlib.util.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bt)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; DET = C.DET; STIM_DUR = cc.STIM_DUR; HORIZON = cc.HORIZON; WASHOUT_B = cc.WASHOUT_B; STIM_AMP = cc.STIM_AMP

def run_seed(seed):
    S0, cents, sizes, eng = mr.reconstruct_S0(seed)
    if S0 is None: return None
    st = S0.copy(); st.N = np.full_like(st.N, cc.N0)
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks0, _ = cc.region_masks(st, cents)
    tr = bt.BijectiveTracker(theta=cc.TRACK_THETA)
    seeds = tr.seed(tracks0, 0)
    censor_step = {s.id: None for s in seeds}
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR: st.N = st.N + STIM_AMP
        st = eng.step(st)
        comps = [cc.mask(e) for e in detect(st, DET)]
        ev = tr.update(comps, t)
        for tid, status in ev.items():
            if censor_step[tid] is None: censor_step[tid] = (t, status)
    summ = tr.summary()
    statuses = [s.status for s in tr.tracks]
    return dict(seed=seed, alive=summ["alive"], merged=summ["merged"], lost=summ["lost"],
                split=summ["split"], ambiguous=summ["ambiguous"], statuses=statuses,
                censor=[censor_step[s.id] for s in tr.tracks])

def main():
    raw = json.load(open("experiments/individuation/causal_confirmation_raw.json"))
    seeds = [r["seed"] for r in raw if r.get("ok")]
    out = {}; tot_alive = 0; tot = 0
    print(f"{'seed':>6}  {'ALIVE':>5} {'MERGED':>6} {'LOST':>4} {'SPLIT':>5}  statuses / censor(step,why)")
    for s in seeds:
        r = run_seed(s)
        if r is None: continue
        out[s] = r; tot_alive += r["alive"]; tot += K
        cens = "; ".join(f"{c[0]}:{c[1][:5]}" if c else "alive" for c in r["censor"])
        print(f"{s:>6}  {r['alive']:>5} {r['merged']:>6} {r['lost']:>4} {r['split']:>5}  {r['statuses']}  [{cens}]")
    print(f"\nCORRECTED individual survivors at readout = {tot_alive}/{tot} "
          f"(vs sealed claim 39/39 'tracked & survive').")
    out["_summary"] = dict(corrected_alive=tot_alive, nominal=tot,
                           note="POST HOC; ALIVE = distinct individual, never censored through readout")
    json.dump(out, open("work/corrected_tracker_survivors.json", "w"), indent=2, default=str)
    print("wrote work/corrected_tracker_survivors.json")

if __name__ == "__main__":
    main()
