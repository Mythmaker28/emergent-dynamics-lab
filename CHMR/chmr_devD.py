"""CHMR Phase D — bounded DEV: passive halo relaxation and the choice of T_RECOVERY.

DEV cap: 8 independent founding blocks (36000-36007), never used for confirmation.

T_RECOVERY is defined BEFORE any mismatch outcome is read, as the earliest sealed observation
time at which BOTH hold:
   (i)  the ORPHAN_HALO residual is <= 10 % of its value immediately after the operation;
   (ii) pair/lineage feasibility is still above the frozen threshold: in every DEV block, both
        sites still carry a component of their own continuous lineage, with no split and no
        fusion.
If no such time exists among the sealed observation times: TIMESCALE_SEPARATION_FAIL.

The residual is measured on the FROZEN halo vector only. No outcome, no response, no core.
"""
from __future__ import annotations
import sys, json, time, statistics as S
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
import numpy as np
import domc_core as K
import chmr_core as X
import chmr_lineage as LG

DEV_SEEDS = tuple(range(36000, 36008))
RESIDUAL_CRITERION = 0.10


def prefix(seed, geom="FAR"):
    """Founding, the two localized histories, and the settle. Site A owns HIST_H, site B HIST_L."""
    K.set_geometry(geom)
    eng = X.engine()
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    s = K.apply_dual_history(eng, f, X.HIST_H, X.HIST_L)
    return K.advance(eng, s, K.SETTLE), eng


def run_dev(seed, geom="FAR"):
    st0, eng = prefix(seed, geom)
    sup = X.halo_supports()
    out = {"seed": seed, "geometry": geom}

    # --- the matched world, tracked with the frozen lineage tracker ----------------------
    frames = [LG.snapshot(st0)]
    edges = []
    cur = st0.copy()
    matched, lineage_ok = [], True
    for t in range(0, max(X.OBS_TIMES) + 1):
        if t in X.OBS_TIMES:
            matched.append({"t": t, "halo": X.halo_vector(cur, sup), "core": X.core_vector(cur),
                            "geom": X.geometry_vector(cur)})
        if t == max(X.OBS_TIMES):
            break
        cur = eng.step(cur)
        if (t + 1) % X.CAD_LINEAGE == 0:
            f = LG.snapshot(cur)
            edges.append(LG.link(frames[-1], f))
            frames.append(f)
    rep = LG.analyse_track(frames, edges)
    out["matched"] = matched
    out["lineage"] = {"n_components": rep["n_components"], "n_splits": rep["n_splits"],
                      "n_fusions": rep["n_fusions"],
                      "n_disappearances": len(rep["disappearances"])}

    # --- the orphan halo: same state, core removed, c/N preserved exactly ----------------
    orph = X.orphan_halo(st0)
    out["orphan_ledger"] = X.ledger(st0, orph, "ORPHAN_HALO")
    cur = orph
    orphan = []
    # the reference the halo relaxes TOWARDS is the empty-world equilibrium: with no rho there is
    # no source, so c -> 0 and N -> N0. Both are known constants of the frozen LawSpec.
    for t in range(0, max(X.OBS_TIMES) + 1):
        if t in X.OBS_TIMES:
            orphan.append({"t": t, "halo": X.halo_vector(cur, sup)})
        if t == max(X.OBS_TIMES):
            break
        cur = eng.step(cur)
    out["orphan"] = orphan

    # residual of the halo CONTRAST, which is the quantity the mismatch experiment moves
    h0 = orphan[0]["halo"]
    gap0_c = h0["A"][0] - h0["B"][0]
    gap0_N = h0["A"][1] - h0["B"][1]
    res = []
    for r in orphan:
        gc = r["halo"]["A"][0] - r["halo"]["B"][0]
        gn = r["halo"]["A"][1] - r["halo"]["B"][1]
        res.append({"t": r["t"],
                    "residual_c": abs(gc / gap0_c) if gap0_c else None,
                    "residual_N": abs(gn / gap0_N) if gap0_N else None,
                    "gap_c": gc, "gap_N": gn})
    out["orphan_residual"] = res
    out["gap0"] = {"c": gap0_c, "N": gap0_N}
    return out


if __name__ == "__main__":
    t0 = time.time()
    OUT = {"programme": "CORE_HALO_MISMATCH_RECOVERY_00", "phase": "D_DEV_TIMESCALE",
           "dev_seeds": list(DEV_SEEDS), "residual_criterion": RESIDUAL_CRITERION,
           "sealed_observation_times": list(X.OBS_TIMES), "blocks": []}
    for s in DEV_SEEDS:
        r = run_dev(s)
        OUT["blocks"].append(r)
        rr = r["orphan_residual"]
        print(f"block {s}: gap0_c={r['gap0']['c']:.4f}  residual_c "
              + " ".join(f"{x['t']}:{x['residual_c']:.3f}" for x in rr)
              + f"  | splits={r['lineage']['n_splits']} fusions={r['lineage']['n_fusions']} "
                f"ncomp={sorted(set(r['lineage']['n_components']))}", flush=True)

    # --- choose T_RECOVERY, on DEV only, before any mismatch outcome exists --------------
    ok_t = []
    for t in X.OBS_TIMES:
        rc = [next(x["residual_c"] for x in b["orphan_residual"] if x["t"] == t)
              for b in OUT["blocks"]]
        feas = all(b["lineage"]["n_splits"] == 0 and b["lineage"]["n_fusions"] == 0
                   and set(b["lineage"]["n_components"]) <= {2} for b in OUT["blocks"])
        ok = (max(rc) <= RESIDUAL_CRITERION) and feas
        ok_t.append({"t": t, "max_residual_c": max(rc), "median_residual_c": S.median(rc),
                     "feasible": feas, "PASSES": ok})
    OUT["T_RECOVERY_scan"] = ok_t
    sel = next((x["t"] for x in ok_t if x["PASSES"] and x["t"] > 0), None)
    OUT["T_RECOVERY"] = sel
    OUT["TIMESCALE_SEPARATION"] = "PASS" if sel is not None else "TIMESCALE_SEPARATION_FAIL"
    print("\nT_RECOVERY scan:")
    for x in ok_t:
        print(f"  t={x['t']:4d}  max residual_c = {x['max_residual_c']:.4f}  "
              f"median = {x['median_residual_c']:.4f}  feasible={x['feasible']}  "
              f"{'PASS' if x['PASSES'] else '-'}")
    print("T_RECOVERY =", sel, "|", OUT["TIMESCALE_SEPARATION"])
    OUT["seconds"] = round(time.time() - t0, 1)
    json.dump(OUT, open("chmr_devD.json", "w"), indent=1, default=str)
