"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 2 event-by-event replay (POST HOC; committed).

Deterministic replay (byte-identical platform) of the INTACT behavioural branch, instrumented step-by-step, to
classify the double-tracking as MERGE / SPLIT / ASSIGNMENT-COLLISION / LOST / PERIODIC-WRAP and to pinpoint the
phase (washout / stimulus / horizon) of the FIRST problematic event. Reuses the SEALED functions of
causal_confirm.py verbatim (seed_world, build, pick, detect, mask, overlap, region_masks, patch, feats). No new
physics; no new hyperparameter. POST HOC — never a re-confirmation.

Event definitions (per step, K target masks fixed at horizon start = geometry snapshot):
  MERGE               one current connected component covers >50% of >=2 distinct fixed target masks
  ASSIGNMENT COLLISION >=2 alive tracks select the SAME current component as max-overlap best
  SPLIT               one fixed target mask is covered >30% by >=2 distinct current components
  LOST                a track finds no component with overlap>=theta (censored)
  PERIODIC WRAP       a single target's component spans a periodic boundary but stays ONE entity
                      (ruled out as the cause here iff MERGE fires on TWO DISTINCT targets)

Usage: python experiments/individuation/merge_replay.py  work/merge_replay_log.json  [seeds...]
"""
import sys, json, importlib.util, numpy as np
from itertools import combinations

# ---- load sealed runner verbatim ----
spec = importlib.util.spec_from_file_location("cc", "experiments/individuation/causal_confirm.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; N = cc.N; DET = C.DET
STIM_DUR = cc.STIM_DUR; HORIZON = cc.HORIZON; WASHOUT_B = cc.WASHOUT_B; STIM_AMP = cc.STIM_AMP
TRACK_THETA = cc.TRACK_THETA; GRID = N * N

def reconstruct_S0(seed):
    """Replicate the sealed storage block to obtain the common snapshot S0 and target centroids (verbatim path)."""
    rng = np.random.default_rng(seed)
    eng = cc.build(cc.MEM_INTACT)
    st = cc.seed_world(seed)
    for _ in range(cc.WARM): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    if len(T) < K:
        return None, None, None, eng
    cents = [e.centroid for e in T]; sigs = [max(3.0, e.rg * 0.8) for e in T]; sizes = [e.size for e in T]
    pts = [cc.patch(*cents[i], sigs[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    sS = st.copy()
    for ph in (0, 1):
        amps = [hist[i][ph] for i in range(K)]
        for _ in range(cc.PHASE):
            for i in range(K): sS.N = sS.N + amps[i] * pts[i]
            sS = eng.step(sS)
    for _ in range(cc.SETTLE): sS = eng.step(sS)
    return sS.copy(), cents, sizes, eng

def frac_cover(target_mask, comp_mask):
    tm = target_mask.sum()
    return float((target_mask & comp_mask).sum() / tm) if tm else 0.0

def replay_intact(seed, keep_steps=False):
    S0, cents, sizes, eng = reconstruct_S0(seed)
    if S0 is None:
        return {"seed": seed, "ok": False, "reason": "fewer_than_K_eligible"}
    # -- intact standardized branch: washout then stimulus+horizon (verbatim measure_branch path) --
    st = S0.copy()
    st.N = np.full_like(st.N, cc.N0)                 # standardize
    for _ in range(WASHOUT_B): st = eng.step(st)
    tracks, _ = cc.region_masks(st, cents); alive = [True] * K
    fixed = [t.copy() for t in tracks]               # geometry snapshot masks
    fixed_distinct_pairs = sum(1 for a, b in combinations(range(K), 2)
                               if (fixed[a] & fixed[b]).sum() == 0)
    log = []
    first_merge = None; first_collision = None; first_lost = None
    ever_merge_targets = set()
    last_occ = K; last_cover = 0.0
    for t in range(1, HORIZON + 1):
        if t <= STIM_DUR: st.N = st.N + STIM_AMP
        st = eng.step(st)
        ents = detect(st, DET)
        emasks = [cc.mask(e) for e in ents]; esizes = [int(m.sum()) for m in emasks]
        phase = "stimulus" if t <= STIM_DUR else "horizon"
        # assignment: best component per track (as in the sealed tracker)
        assign = []
        for i in range(K):
            if not alive[i]:
                assign.append(-1); continue
            ovs = [cc.overlap(tracks[i], e) for e in ents]
            if not ents or max(ovs) < TRACK_THETA:
                alive[i] = False; assign.append(-1)
                if first_lost is None: first_lost = (t, phase, i)
                continue
            bi = int(np.argmax(ovs)); assign.append(bi); tracks[i] = emasks[bi]
        # collision: two alive tracks same component
        alive_assign = [(i, a) for i, a in enumerate(assign) if a >= 0]
        comp_to_tracks = {}
        for i, a in alive_assign: comp_to_tracks.setdefault(a, []).append(i)
        collided = {a: ts for a, ts in comp_to_tracks.items() if len(ts) > 1}
        if collided and first_collision is None:
            first_collision = (t, phase, {int(a): ts for a, ts in collided.items()})
        # physical merge: one current component covers >50% of >=2 fixed target masks
        merged_now = []
        for ci, cm in enumerate(emasks):
            covered = [j for j in range(K) if frac_cover(fixed[j], cm) > 0.5]
            if len(covered) >= 2:
                merged_now.append((ci, covered, esizes[ci]))
                ever_merge_targets.update(covered)
        if merged_now and first_merge is None:
            ci, covered, csz = max(merged_now, key=lambda x: x[2])
            first_merge = (t, phase, covered, csz, csz / GRID)
        # distinct components occupied by the K targets (via fixed-mask attribution)
        occ = set()
        for j in range(K):
            best_c = max(range(len(emasks)), key=lambda ci: frac_cover(fixed[j], emasks[ci]), default=-1)
            if best_c >= 0 and frac_cover(fixed[j], emasks[best_c]) > 0.30: occ.add(best_c)
        largest = max(esizes) if esizes else 0
        last_occ = len(occ); last_cover = largest / GRID
        if keep_steps:
            cds = [cc.pdist(_centroid(tracks[a]), _centroid(tracks[b]))
                   for a, b in combinations(range(K), 2) if alive[a] and alive[b]]
            log.append(dict(t=t, phase=phase, assign=assign, alive=list(alive),
                            n_distinct_occupied=len(occ), largest_comp=largest,
                            largest_cover=largest / GRID, n_components=len(ents),
                            collided={int(a): ts for a, ts in collided.items()},
                            merged=[(ci, cov, sz) for ci, cov, sz in merged_now],
                            centroid_dists=[round(x, 2) for x in cds]))
    return dict(seed=seed, ok=True, init_sizes=sizes,
                fixed_distinct_pairs_at_start=fixed_distinct_pairs,  # 3 => all 3 disjoint at horizon start
                first_merge=first_merge, first_collision=first_collision, first_lost=first_lost,
                ever_merged_targets=sorted(ever_merge_targets),
                final_distinct_occupied=last_occ,
                final_largest_cover=last_cover,
                steps=(log if keep_steps else None))

def _centroid(m):
    ys, xs = np.where(m)
    if len(ys) == 0: return (0.0, 0.0)
    # circular mean for periodicity
    def cm(v):
        ang = v / N * 2 * np.pi
        a = np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())
        return (a % (2 * np.pi)) / (2 * np.pi) * N
    return (cm(ys), cm(xs))

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "work/merge_replay_log.json"
    seeds = [int(x) for x in sys.argv[2:]] or [52001, 52005, 52010, 52012, 52008]
    detail_seeds = {52001, 52005, 52010, 52012, 52008}
    results = {}
    print(f"{'seed':>6} {'elig':>5} {'fixStart':>8} {'firstMerge(t,phase,targets,cover)':>42} {'firstColl':>10} {'finalOcc':>8} {'finalCov':>8}")
    for s in seeds:
        r = replay_intact(s, keep_steps=(s in detail_seeds))
        results[s] = r
        if not r["ok"]:
            print(f"{s:>6} {'NO':>5}  ({r['reason']})"); continue
        fm = r["first_merge"]; fc = r["first_collision"]
        fm_s = f"t={fm[0]} {fm[1]} tgt={fm[2]} cov={fm[4]*100:.0f}%" if fm else "none"
        fc_s = f"t={fc[0]}" if fc else "none"
        print(f"{s:>6} {'yes':>5} {r['fixed_distinct_pairs_at_start']:>8} {fm_s:>42} {fc_s:>10} "
              f"{r['final_distinct_occupied']:>8} {r['final_largest_cover']*100:>7.0f}%")
    json.dump(results, open(out_path, "w"), indent=2, default=str)
    print(f"\nwrote {out_path}")

if __name__ == "__main__":
    main()
