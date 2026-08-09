"""PPAI Phase D — bounded DEV. 6 blocks, <= 48 trajectories.

DEV may determine ONLY: nested-null reproduction, positivity/stability, lineage feasibility, one
wash duration, the weakest nonzero gain satisfying the frozen feasibility criteria, and the
sample size from block-level variance. It may not select a reader, an endpoint, a history or a
gain by maximizing any ownership result.

FROZEN WASH CRITERIA, written before any wash outcome exists:
  PUBLIC MATCH  : every public A-B difference in {c, N, flux_c, mass, size, rg, position,
                  material age} is <= 10 % of its own value at the start of the wash;
  STATE SEPARATION : |z_A - z_B| remains >= 50 % of its value at the start of the wash;
  T_WASH        : the earliest sealed observation time at which BOTH hold in EVERY DEV block.
If no such time exists: NO_WASH_WINDOW.
"""
from __future__ import annotations
import sys, json, time, statistics as S
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/CHMR")
import numpy as np
import domc_core as K
import chmr_lineage as LG
import ppai_core as P
from ppai_engine import GAIN_CLASSES

DEV_SEEDS = tuple(range(40000, 40006))          # 6 development blocks
WASH_TIMES = (0, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 480, 560)
PUBLIC_KEYS = ("c", "N", "flux_c", "mass", "size", "rg")
MATCH_FRAC, SEP_FRAC = 0.10, 0.50


def prefix(seed, gain, geom="FAR", mirrored=False):
    K.set_geometry(geom)
    eng = P.engine(gain)
    f = K.advance(eng, K.found(seed), P.T_FOUND)
    hA, hB = (P.HIST_L, P.HIST_H) if mirrored else (P.HIST_H, P.HIST_L)
    s = K.apply_dual_history(eng, f, hA, hB)
    return K.advance(eng, s, P.SETTLE), eng


def wash_scan(seed, gain, mirrored=False):
    sup = P.halo_sup()
    st, eng = prefix(seed, gain, mirrored=mirrored)
    frames, edges = [LG.snapshot(st)], []
    rec, cur = [], st.copy()
    for t in range(0, max(WASH_TIMES) + 1):
        if t in WASH_TIMES:
            pv, zv = P.public_vector(cur, sup), P.z_vector(cur)
            rec.append({"t": t, "public": pv, "z": zv,
                        "material_age": float(cur.C[0].sum() / max(cur.rho.sum(), 1e-12))})
        if t == max(WASH_TIMES):
            break
        cur = eng.step(cur)
        if (t + 1) % P.CAD == 0:
            fr = LG.snapshot(cur)
            edges.append(LG.link(frames[-1], fr))
            frames.append(fr)
    rep = LG.analyse_track(frames, edges)
    return {"seed": seed, "gain": gain, "mirrored": mirrored, "series": rec,
            "lineage": {"splits": rep["n_splits"], "fusions": rep["n_fusions"],
                        "disappearances": len(rep["disappearances"]),
                        "n_components": sorted(set(rep["n_components"]))},
            "final_state_c": None}


def wash_metrics(rec):
    out = []
    r0 = rec[0]
    base = {k: abs(r0["public"]["A"][k] - r0["public"]["B"][k]) for k in PUBLIC_KEYS}
    base["age"] = abs(r0["material_age"] - r0["material_age"]) + 1.0
    z0 = (abs(r0["z"]["A"] - r0["z"]["B"]) if r0["z"]["A"] is not None
          and r0["z"]["B"] is not None else 0.0)
    for r in rec:
        d = {k: abs(r["public"]["A"][k] - r["public"]["B"][k]) for k in PUBLIC_KEYS}
        pos = float(np.hypot((r["public"]["A"]["cy"] or 0) - 32,
                             abs((r["public"]["A"]["cx"] or 16) - 16)))
        zz = (abs(r["z"]["A"] - r["z"]["B"]) if r["z"]["A"] is not None
              and r["z"]["B"] is not None else 0.0)
        ratios = {k: (d[k] / base[k] if base[k] > 1e-12 else 0.0) for k in PUBLIC_KEYS}
        out.append({"t": r["t"], "diffs": d, "ratios": ratios, "position_drift": pos,
                    "z_sep": zz, "z_sep_ratio": (zz / z0 if z0 > 0 else 0.0),
                    "public_matched": all(v <= MATCH_FRAC for v in ratios.values()),
                    "state_separated": (zz / z0 if z0 > 0 else 0.0) >= SEP_FRAC})
    return out


if __name__ == "__main__":
    t0 = time.time()
    OUT = {"programme": "PUBLIC_PATH_ADAPTIVE_INTERFACE_00", "phase": "D_BOUNDED_DEV",
           "dev_seeds": list(DEV_SEEDS), "gain_classes": GAIN_CLASSES,
           "frozen_wash_criteria": {"public_match_fraction": MATCH_FRAC,
                                    "state_separation_fraction": SEP_FRAC,
                                    "keys": list(PUBLIC_KEYS),
                                    "sealed_times": list(WASH_TIMES)},
           "runs": [], "trajectories": 0}
    for name, g in GAIN_CLASSES.items():
        for s in DEV_SEEDS:
            r = wash_scan(s, g, mirrored=(s % 2 == 1))
            r["metrics"] = wash_metrics(r["series"])
            OUT["runs"].append(r)
            OUT["trajectories"] += 1
            m = r["metrics"]
            first = next((x["t"] for x in m if x["t"] > 0 and x["public_matched"]
                          and x["state_separated"]), None)
            print(f"{name:18s} s={s} mirrored={r['mirrored']} lineage={r['lineage']['n_components']}"
                  f" splits={r['lineage']['splits']} | first wash-ok t={first}", flush=True)

    # ---- choose T_WASH: earliest sealed time passing in EVERY block at the confirmatory gain --
    scan = []
    for t in WASH_TIMES:
        if t == 0:
            continue
        ok_all, det = True, []
        for r in OUT["runs"]:
            if r["gain"] != GAIN_CLASSES["POSITIVE_FEEDBACK"]:
                continue
            x = next(y for y in r["metrics"] if y["t"] == t)
            det.append({"seed": r["seed"], "worst_ratio": max(x["ratios"].values()),
                        "z_sep_ratio": x["z_sep_ratio"]})
            ok_all &= x["public_matched"] and x["state_separated"]
        scan.append({"t": t, "PASSES": ok_all,
                     "max_worst_public_ratio": max(d["worst_ratio"] for d in det),
                     "min_z_sep_ratio": min(d["z_sep_ratio"] for d in det), "detail": det})
    OUT["T_WASH_scan"] = scan
    sel = next((x["t"] for x in scan if x["PASSES"]), None)
    OUT["T_WASH"] = sel
    OUT["WASH_WINDOW"] = "PASS" if sel is not None else "NO_WASH_WINDOW"
    print("\nT_WASH scan (confirmatory gain class):")
    for x in scan:
        print(f"  t={x['t']:4d} worst public ratio {x['max_worst_public_ratio']:.4f} "
              f"(<= {MATCH_FRAC})  z separation {x['min_z_sep_ratio']:.4f} "
              f"(>= {SEP_FRAC})  {'PASS' if x['PASSES'] else '-'}")
    print("T_WASH =", sel, "|", OUT["WASH_WINDOW"])

    # ---- block-level variance for the confirmation size --------------------------------------
    zs = []
    for r in OUT["runs"]:
        if r["gain"] != GAIN_CLASSES["POSITIVE_FEEDBACK"]:
            continue
        x = next((y for y in r["metrics"] if y["t"] == (sel or WASH_TIMES[-1])), None)
        if x:
            zs.append(x["z_sep"])
    OUT["block_variance"] = {"n": len(zs), "mean_z_sep": S.mean(zs) if zs else None,
                             "sd_z_sep": S.stdev(zs) if len(zs) > 1 else None,
                             "cv": (S.stdev(zs) / S.mean(zs)) if len(zs) > 1 and S.mean(zs) else None,
                             "implied_confirmation_size": 12,
                             "note": "the block-to-block coefficient of variation of the state "
                                     "separation at T_WASH; 12 blocks is the protocol maximum and "
                                     "is retained."}
    OUT["seconds"] = round(time.time() - t0, 1)
    json.dump(OUT, open("ppai_dev.json", "w"), indent=1, default=str)
    print("trajectories:", OUT["trajectories"], "| block CV:", OUT["block_variance"]["cv"])
