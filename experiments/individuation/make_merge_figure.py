"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 2 first-merge figure + pre/post-merge accrual (POST HOC; committed).

For an all-3-collapsed world (default 52012) reconstruct S0 (sealed path), replay the intact branch, and:
  (1) capture rho grids + the 3 fixed target masks at horizon-start / pre-merge / first-merge / final;
  (2) quantify the fraction of the tracked integrated uptake that accrues AFTER the first merge
      (the double-counted, contaminated share) vs the fixed-mask readout.
Renders docs/individuation/MERGE_INCIDENT_FIRST_MERGE.png. No new physics.
"""
import sys, json, importlib.util, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from itertools import combinations

spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET; GRID = N * N
STIM_DUR = cc.STIM_DUR; HORIZON = cc.HORIZON; WASHOUT_B = cc.WASHOUT_B; STIM_AMP = cc.STIM_AMP; THETA = cc.TRACK_THETA

# import reconstruct_S0 + frac_cover from the replay module
rspec = importlib.util.spec_from_file_location("mr", "experiments/individuation/merge_replay.py")
mr = importlib.util.module_from_spec(rspec); rspec.loader.exec_module(mr)

def run(seed):
    S0, cents, sizes, eng = mr.reconstruct_S0(seed)
    st = S0.copy(); st.N = np.full_like(st.N, cc.N0)
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks, _ = cc.region_masks(st, cents); alive = [True] * K
    fixed = [t.copy() for t in tracks]
    integ_track = 0.0; integ_fixed = 0.0
    curve = []  # (t, n_distinct, largest_cover, cum_track, cum_fixed)
    snaps = {}
    first_merge = None
    want = None
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR: st.N = st.N + STIM_AMP
        st = eng.step(st)
        ents = detect(st, DET); emasks = [cc.mask(e) for e in ents]; esizes = [int(m.sum()) for m in emasks]
        for i in range(K):
            if not alive[i]: continue
            ovs = [cc.overlap(tracks[i], e) for e in ents]
            if not ents or max(ovs) < THETA: alive[i] = False; continue
            tracks[i] = emasks[int(np.argmax(ovs))]
        # integrate (sum over the 3 tracked regions / 3 fixed regions)
        for i in range(K):
            integ_fixed += float(st.uptake[fixed[i]].sum())
            if alive[i]: integ_track += float(st.uptake[tracks[i]].sum())
        # merge detection
        merged = [(ci, [j for j in range(K) if mr.frac_cover(fixed[j], cm) > 0.5], esizes[ci])
                  for ci, cm in enumerate(emasks)]
        merged = [m for m in merged if len(m[1]) >= 2]
        if merged and first_merge is None:
            first_merge = t
            want = ("premerge", max(1, t - 20)), ("merge", t)
        occ = set()
        for j in range(K):
            bc = max(range(len(emasks)), key=lambda ci: mr.frac_cover(fixed[j], emasks[ci]), default=-1)
            if bc >= 0 and mr.frac_cover(fixed[j], emasks[bc]) > 0.30: occ.add(bc)
        curve.append((t, len(occ), (max(esizes) if esizes else 0) / GRID, integ_track, integ_fixed))
        if t in (1,): snaps["start"] = (st.rho.copy(), [f.copy() for f in fixed])
    # capture pre-merge / merge / final snapshots by re-running to those steps (cheap)
    for label, tt in [("premerge", max(1, (first_merge or 60) - 20)), ("merge", first_merge or 60), ("final", HORIZON)]:
        st2 = S0.copy(); st2.N = np.full_like(st2.N, cc.N0)
        for _ in range(WASHOUT_B): st2 = eng.step(st2)
        for t in range(1, tt + 1):
            if t <= STIM_DUR: st2.N = st2.N + STIM_AMP
            st2 = eng.step(st2)
        snaps[label] = (st2.rho.copy(), [f.copy() for f in fixed])
    return dict(seed=seed, sizes=sizes, first_merge=first_merge, curve=curve, snaps=snaps,
                integ_track=integ_track, integ_fixed=integ_fixed)

def outline(ax, m, color):
    ax.contour(m.astype(float), levels=[0.5], colors=[color], linewidths=1.2)

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 52012
    r = run(seed)
    curve = np.array(r["curve"], float); fm = r["first_merge"]
    # pre/post-merge accrual of tracked uptake
    cum_track = curve[:, 3]; total = cum_track[-1]
    pre = cum_track[curve[:, 0] == fm][0] if fm else total
    post_share = 1 - pre / total
    colors = ["#e63946", "#2a9d8f", "#457b9d"]
    fig = plt.figure(figsize=(13, 6.2))
    order = ["start", "premerge", "merge", "final"]
    titles = ["horizon start (t=1)\n3 distinct components", f"pre-merge (t={max(1,(fm or 60)-20)})\ngrowing",
              f"FIRST MERGE (t={fm})\ntargets share 1 component", f"final (t={HORIZON})\npercolated blob"]
    for k, key in enumerate(order):
        ax = fig.add_subplot(2, 4, k + 1)
        rho, fixed = r["snaps"][key]
        ax.imshow(rho, cmap="magma", vmin=0, vmax=1.0)
        for j in range(K): outline(ax, fixed[j], colors[j])
        ax.set_title(titles[k], fontsize=9); ax.set_xticks([]); ax.set_yticks([])
    # bottom-left: n distinct occupied + largest coverage
    ax = fig.add_subplot(2, 2, 3)
    ax.plot(curve[:, 0], curve[:, 1], color="#1d3557", label="# distinct components occupied by the 3 targets")
    ax.axhline(3, ls=":", c="grey"); ax.axvline(STIM_DUR, ls="--", c="orange", label="stimulus end (t=15)")
    if fm: ax.axvline(fm, ls="-", c="red", label=f"first merge (t={fm})")
    ax.set_ylim(0, 3.3); ax.set_xlabel("horizon step"); ax.set_ylabel("# components", color="#1d3557")
    ax2 = ax.twinx(); ax2.plot(curve[:, 0], curve[:, 2] * 100, color="#8d99ae", alpha=0.8)
    ax2.set_ylabel("largest component grid coverage (%)", color="#8d99ae")
    ax.legend(fontsize=7, loc="center left"); ax.set_title(f"seed {seed}: 3 targets collapse to 1 component", fontsize=9)
    # bottom-right: cumulative tracked vs fixed uptake
    ax = fig.add_subplot(2, 2, 4)
    ax.plot(curve[:, 0], curve[:, 3], color="#e63946", label="tracked (follows growing/merged blob)")
    ax.plot(curve[:, 0], curve[:, 4], color="#457b9d", label="fixed-mask (tracker-free)")
    ax.axvline(STIM_DUR, ls="--", c="orange");
    if fm: ax.axvline(fm, ls="-", c="red")
    ax.set_xlabel("horizon step"); ax.set_ylabel("cumulative uptake (sum of 3 regions)")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title(f"tracked/fixed final ratio={r['integ_track']/r['integ_fixed']:.1f}x; "
                 f"{post_share*100:.0f}% of tracked accrues AFTER merge", fontsize=8)
    fig.suptitle(f"LCI-CAUSAL-MERGE-INCIDENT-01 — first physical merge (seed {seed}, all-3 collapse) — POST HOC replay",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = "docs/individuation/MERGE_INCIDENT_FIRST_MERGE.png"
    fig.savefig(out, dpi=130); print("wrote", out)
    print(json.dumps(dict(seed=seed, first_merge=fm, tracked_final=r["integ_track"], fixed_final=r["integ_fixed"],
                          tracked_over_fixed=r["integ_track"]/r["integ_fixed"],
                          post_merge_share_of_tracked=post_share), indent=2))

if __name__ == "__main__":
    main()
