"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 1 raw audit (POST HOC diagnostic; committed regenerator).

Independent re-analysis of experiments/individuation/causal_confirmation_raw.json (b415503) to test the
physical-merge / double-tracking alert on LCI-CAUSAL-CONFIRMATION-01. Reads ONLY the committed raw; runs no
simulation. Every recomputation below is a POST HOC diagnostic and is NEVER a new positive confirmation
(constraint: no new positive claim from post-hoc diagnostics; no silent world removal; no threshold change
after observation).

What it establishes, per branch and per seed:
  - track pairs with EXACTLY equal final (size, mass, mean_c)  -> same readout component
  - number of UNIQUE final components actually observed per world (grouping equal-triple tracks)
  - tracks that share a component (2-collapsed vs 3-collapsed / all-same)
  - initial vs final sizes, relative growth, grid-coverage fraction (N=64 -> 4096 cells)
  - whether the tracker-free FIXED-mask readout is ALSO collapsed (integ_fixed equal pairs)
  - proper vs neighbour vs sham effects in fused vs non-fused worlds
  - fidelity reproduction of the sealed GATE_CERTIFICATE headline numbers

Recomputations (all POST HOC, never a re-confirmation):
  A. all worlds (reproduce headline, tracked readout)
  B. worlds with NO detected duplication only
  C. fixed-mask (tracker-free) readout
  D. one observation per UNIQUE final component (collapse duplicated tracks)

Usage:  python experiments/individuation/merge_incident_audit.py \
            experiments/individuation/causal_confirmation_raw.json  work/merge_incident_audit.json
"""
import sys, json, numpy as np
from itertools import combinations

K = 3
N_GRID = 64                # C.SPEC.size (verified by import)
GRID_CELLS = N_GRID * N_GRID
BOOT_SEED = 20260715       # frozen seed (unchanged; reused only to reproduce the sealed CI, not to re-gate)

def load(path):
    return [r for r in json.load(open(path)) if r.get("ok")]

def triple(cond, i):
    # exact final identity of a track's readout component
    return (int(cond["size"][i]), cond["mass"][i], cond["mean_c"][i])

def wb_ci(perworld, nb=5000, seed=BOOT_SEED):
    rng = np.random.default_rng(seed); n = len(perworld)
    bs = np.array([perworld[rng.integers(0, n, n)].mean() for _ in range(nb)])
    return [float(x) for x in np.percentile(bs, [2.5, 50, 97.5])]

def per_droplet_rows(recs):
    rows = []
    for r in recs:
        b = r["beh"]; A = b["intact"]; er = b["erase"]; E = b["ablate"]; erabl = b["erase_ablate"]
        S = b["sham"]; Ares = b["intact_res"]; erres = b["erase_res"]; Al = b["intact_long"]; erl = b["erase_long"]
        m = np.array(A["mass"], float)
        for i in range(K):
            rows.append(dict(
                seed=r["seed"], i=i, dose=r["dose"][i],
                init_size=r["sizes"][i], final_size=A["size"][i],
                own=A["integ_upt"][i] - er[i]["integ_upt"][i],
                own_fixed=A["integ_fixed"][i] - er[i]["integ_fixed"][i],
                abl=E["integ_upt"][i] - erabl[i]["integ_upt"][i],
                sham=A["integ_upt"][i] - S["integ_upt"][i],
                neigh=float(np.mean([A["integ_upt"][i] - er[j]["integ_upt"][i] for j in range(K) if j != i])),
                res=Ares["integ_upt"][i] - erres[i]["integ_upt"][i],
                lon=Al["integ_upt"][i] - erl[i]["integ_upt"][i],
                triple_intact=triple(A, i)))
    return rows

def analyze(raw_path):
    recs = load(raw_path); nW = len(recs)
    rows = per_droplet_rows(recs)
    seeds = [r["seed"] for r in recs]

    # ---------- fidelity: reproduce sealed headline ----------
    def col(k): return np.array([x[k] for x in rows], float)
    def perworld(k): return np.array([np.mean([x[k] for x in rows if x["seed"] == s]) for s in seeds])
    own = col("own"); pw_own = perworld("own"); ci_own = wb_ci(pw_own)
    pw_fix = perworld("own_fixed"); ci_fix = wb_ci(pw_fix)
    abl = col("abl"); neigh = col("neigh"); sham = col("sham")
    headline = dict(
        eff_own_worldCI=ci_own, worlds_pos=int((pw_own > 0).sum()), droplets_pos=int((own > 0).sum()),
        SNR=float(pw_own.mean() / (pw_own.std(ddof=1) / np.sqrt(nW))),
        eff_fixed_worldCI=ci_fix, fixed_worlds_pos=int((pw_fix > 0).sum()),
        ablation_ratio=float(np.abs(abl).mean() / (np.abs(own).mean() + 1e-12)),
        neigh_ratio=float(np.abs(neigh).mean() / (np.abs(own).mean() + 1e-12)),
        sham_ratio=float(np.abs(sham).mean() / (np.abs(own).mean() + 1e-12)),
        tracked_over_fixed_inflation=float(np.median(pw_own) / np.median(pw_fix)))

    # ---------- merge signature, per branch ----------
    branch_specs = {
        "intact": lambda b: b["intact"],
        "sham": lambda b: b["sham"],
        "ablate": lambda b: b["ablate"],
        "inert": lambda b: b["inert"],
        "intact_res": lambda b: b["intact_res"],
        "intact_long": lambda b: b["intact_long"],
        "nodrive": lambda b: b["nodrive"],
    }
    branch_pairs = {}
    for bname, get in branch_specs.items():
        total = 0; worlds = []
        for r in recs:
            cond = get(r["beh"]); trs = [triple(cond, i) for i in range(K)]
            pairs = [(a, c) for a, c in combinations(range(K), 2) if trs[a] == trs[c]]
            if pairs:
                total += len(pairs); worlds.append(r["seed"])
        branch_pairs[bname] = dict(identical_pairs=total, worlds=worlds, n_worlds=len(worlds))

    # detailed per-world (intact) merge map
    per_world = []
    fused_worlds = []; all3 = []
    for r in recs:
        A = r["beh"]["intact"]; trs = [triple(A, i) for i in range(K)]
        uniq = len(set(trs))
        pairs = [(a, c) for a, c in combinations(range(K), 2) if trs[a] == trs[c]]
        cover = [s / GRID_CELLS for s in A["size"]]
        growth = [A["size"][i] / max(r["sizes"][i], 1) for i in range(K)]
        if pairs:
            fused_worlds.append(r["seed"])
            if uniq == 1: all3.append(r["seed"])
        per_world.append(dict(
            seed=r["seed"], n_detected=r["n_detected"], init_sizes=r["sizes"], final_sizes=A["size"],
            unique_final_components=uniq, identical_pairs=pairs, fused=bool(pairs),
            all_three_collapsed=bool(uniq == 1),
            max_grid_coverage=float(max(cover)), growth_min=float(min(growth)), growth_max=float(max(growth)),
            min_target_separation=float(min(r["dists"]))))

    # ---------- fixed-mask collapse test ----------
    fixed_collapse_pairs = 0
    for r in recs:
        A = r["beh"]["intact"]; vals = [A["integ_fixed"][i] for i in range(K)]
        fixed_collapse_pairs += sum(1 for a, c in combinations(range(K), 2) if vals[a] == vals[c])

    # ---------- A / B / C / D recomputations (POST HOC) ----------
    fused_set = set(fused_worlds)
    def subset_effect(pred, key):
        vals = [x[key] for x in rows if pred(x["seed"])]
        return float(np.mean(vals)) if vals else None
    # D: one observation per unique final component (representative = first track of each equal-triple group)
    d_rows = []
    for r in recs:
        A = r["beh"]["intact"]; er = r["beh"]["erase"]
        seen = {}
        for i in range(K):
            t = triple(A, i)
            if t in seen:
                continue
            seen[t] = i
        for i in seen.values():
            d_rows.append(A["integ_upt"][i] - er[i]["integ_upt"][i])
    recompute = {
        "A_all_worlds_tracked": dict(mean_own=float(own.mean()), worlds=nW, droplets=len(rows),
                                     note="reproduces sealed headline; tracker-dependent"),
        "B_nonduplicated_worlds_only": dict(
            seeds=[s for s in seeds if s not in fused_set],
            n_worlds=int(nW - len(fused_set)),
            mean_own_tracked=subset_effect(lambda s: s not in fused_set, "own"),
            mean_own_fixed=subset_effect(lambda s: s not in fused_set, "own_fixed"),
            mean_neigh=subset_effect(lambda s: s not in fused_set, "neigh"),
            note="POST HOC diagnostic on the 2 clean worlds; underpowered; NOT a confirmation"),
        "C_fixed_mask_tracker_free": dict(
            mean_own_fixed=float(col("own_fixed").mean()), worldCI=ci_fix,
            fixed_worlds_pos=int((pw_fix > 0).sum()),
            note="tracker-free readout on the geometry snapshot; smaller but sign-stable"),
        "D_one_per_unique_component": dict(
            n_unique_readout_units=len(d_rows),
            nominal_droplet_count=len(rows),
            mean_own_tracked=float(np.mean(d_rows)),
            note="collapses duplicated tracks to unique final components; 39 nominal -> %d actual" % len(d_rows)),
        "fused_vs_nonfused": {
            "fused": dict(n_droplets=int(sum(1 for x in rows if x["seed"] in fused_set)),
                          mean_own=subset_effect(lambda s: s in fused_set, "own"),
                          mean_own_fixed=subset_effect(lambda s: s in fused_set, "own_fixed"),
                          mean_neigh=subset_effect(lambda s: s in fused_set, "neigh")),
            "nonfused": dict(n_droplets=int(sum(1 for x in rows if x["seed"] not in fused_set)),
                             mean_own=subset_effect(lambda s: s not in fused_set, "own"),
                             mean_own_fixed=subset_effect(lambda s: s not in fused_set, "own_fixed"),
                             mean_neigh=subset_effect(lambda s: s not in fused_set, "neigh"))},
    }

    growth_all = [x["final_size"] / max(x["init_size"], 1) for x in rows]
    out = dict(
        mission="LCI-CAUSAL-MERGE-INCIDENT-01",
        phase="1 raw audit (POST HOC)",
        source_raw="experiments/individuation/causal_confirmation_raw.json (b415503)",
        grid=dict(N=N_GRID, cells=GRID_CELLS, rho_threshold=0.30, min_cells=12),
        eligible_worlds=nW, seeds=seeds,
        headline_reproduction=headline,
        merge_signature=dict(
            intact_identical_pairs=branch_pairs["intact"]["identical_pairs"],
            intact_fused_worlds=branch_pairs["intact"]["worlds"],
            n_fused_worlds=branch_pairs["intact"]["n_worlds"],
            all_three_collapsed_worlds=all3,
            nonfused_worlds=[s for s in seeds if s not in fused_set],
            per_branch_identical_pairs={k: v["identical_pairs"] for k, v in branch_pairs.items()},
            per_branch_fused_worldcount={k: v["n_worlds"] for k, v in branch_pairs.items()},
            fixed_mask_identical_pairs=fixed_collapse_pairs,
            fixed_mask_collapsed=bool(fixed_collapse_pairs > 0)),
        growth=dict(median=float(np.median(growth_all)), min=float(np.min(growth_all)),
                    max=float(np.max(growth_all)),
                    max_grid_coverage=float(max(pw["max_grid_coverage"] for pw in per_world))),
        per_world=per_world,
        recompute_A_B_C_D=recompute,
        spec_vs_impl=dict(
            tracker_spec_says="one-to-one (a component may be claimed by at most one track); cadence 5 steps",
            implementation_in_causal_confirm="independent per-track max-overlap (NON-bijective); cadence 1 step; "
                                             "censor on overlap<theta but NO cross-track exclusion",
            mismatch=True,
            consequence="multiple tracks legally select the same component after physical fusion -> "
                        "assignment collision on top of a genuine physical merge"),
        constraints_note="All B/C/D are POST HOC diagnostics; none is a new positive confirmation. "
                         "No world silently removed; no threshold changed after observation.")
    return out

def main():
    raw_path = sys.argv[1] if len(sys.argv) > 1 else "experiments/individuation/causal_confirmation_raw.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "work/merge_incident_audit.json"
    out = analyze(raw_path)
    json.dump(out, open(out_path, "w"), indent=2)

    ms = out["merge_signature"]; hl = out["headline_reproduction"]
    print(f"=== LCI-CAUSAL-MERGE-INCIDENT-01 Phase 1 raw audit ===")
    print(f"grid {out['grid']['N']}x{out['grid']['N']}={out['grid']['cells']} cells; eligible worlds={out['eligible_worlds']}")
    print(f"\n[fidelity] eff_own worldCI={hl['eff_own_worldCI']} worlds>0={hl['worlds_pos']}/13 droplets>0={hl['droplets_pos']}/39 SNR={hl['SNR']:.2f}")
    print(f"[fidelity] eff_FIXED worldCI={hl['eff_fixed_worldCI']} -> tracked/fixed inflation = {hl['tracked_over_fixed_inflation']:.2f}x")
    print(f"[fidelity] ablation={hl['ablation_ratio']:.4f} neigh={hl['neigh_ratio']:.4f} sham={hl['sham_ratio']:.4f}")
    print(f"\n[merge] INTACT identical (size,mass,mean_c) pairs = {ms['intact_identical_pairs']} across {ms['n_fused_worlds']} worlds")
    print(f"[merge] all-3-collapsed worlds = {ms['all_three_collapsed_worlds']}")
    print(f"[merge] fused worlds = {ms['intact_fused_worlds']}")
    print(f"[merge] non-fused worlds = {ms['nonfused_worlds']}")
    print(f"[merge] per-branch identical pairs = {ms['per_branch_identical_pairs']}")
    print(f"[merge] FIXED-mask identical pairs = {ms['fixed_mask_identical_pairs']} (collapsed={ms['fixed_mask_collapsed']})")
    print(f"[growth] median={out['growth']['median']:.1f}x max={out['growth']['max']:.1f}x max grid coverage={out['growth']['max_grid_coverage']*100:.0f}%")
    r = out["recompute_A_B_C_D"]
    print(f"\n[A all/tracked]   mean_own={r['A_all_worlds_tracked']['mean_own']:+.3f}")
    print(f"[B nonfused only] seeds={r['B_nonduplicated_worlds_only']['seeds']} own_tracked={r['B_nonduplicated_worlds_only']['mean_own_tracked']:+.3f} own_fixed={r['B_nonduplicated_worlds_only']['mean_own_fixed']:+.3f} neigh={r['B_nonduplicated_worlds_only']['mean_neigh']:+.4f}")
    print(f"[C fixed-mask]    mean_own_fixed={r['C_fixed_mask_tracker_free']['mean_own_fixed']:+.3f} worldCI={r['C_fixed_mask_tracker_free']['worldCI']}")
    print(f"[D unique comps]  {r['D_one_per_unique_component']['n_unique_readout_units']} actual readout units vs {r['D_one_per_unique_component']['nominal_droplet_count']} nominal droplets")
    fv = r["fused_vs_nonfused"]
    print(f"[fused]    own={fv['fused']['mean_own']:+.3f} fixed={fv['fused']['mean_own_fixed']:+.3f} neigh={fv['fused']['mean_neigh']:+.4f}")
    print(f"[nonfused] own={fv['nonfused']['mean_own']:+.3f} fixed={fv['nonfused']['mean_own_fixed']:+.3f} neigh={fv['nonfused']['mean_neigh']:+.4f}")
    print(f"\n[spec/impl] mismatch={out['spec_vs_impl']['mismatch']}: {out['spec_vs_impl']['consequence']}")
    print(f"\nwrote {out_path}")

if __name__ == "__main__":
    main()
