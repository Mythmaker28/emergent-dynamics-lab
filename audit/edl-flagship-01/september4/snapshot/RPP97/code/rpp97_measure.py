"""RPP97 — the measurement. Refuses to run unless the capability test cleared it.

Reads the 123 sealed TBRT02 archives. Launches no world. For every component at every step in
the two frozen windows it computes S1 and S2, and counts exactly how often S1 is undefined and
at what component sizes — that count is a result, not an implementation detail.

    FAR  [t_m - 2000, t_m - 1000]   the temporal control
    PRE  [t_m -  250, t_m -    1]   the pre-division window

Status: POST-HOC. See RPP97/out/RPP97_STATEMENT.md section 0.
"""
from __future__ import annotations
import os, sys, json, glob
import numpy as np
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "RPP97/code"))
import rpp97_stats as S

FAR = (-2000, -1000)
PRE = (-250, -1)


def one(path):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0])); t_m = int(meta["t_m"])
    ct = z["c_t"].astype(np.int64); cy = z["c_y"].astype(np.int64); cx = z["c_x"].astype(np.int64)
    cnX = z["c_nX"].astype(np.int64); cid = z["c_cid"].astype(np.int64)
    kt = z["k_t"].astype(np.int64); kid = z["k_id"].astype(np.int64)
    knc = z["k_ncells"].astype(np.int64)
    ka0y = z["k_a0y"].astype(np.int64); ka0x = z["k_a0x"].astype(np.int64)
    ksoy = z["k_soy"].astype(np.int64); ksox = z["k_sox"].astype(np.int64)
    kxd = z["k_xd"].astype(np.int64); srow = z["s"].astype(np.int64); z.close()
    nXtot = {int(r[0]): int(r[2]) for r in srow}

    lo, hi = t_m + FAR[0], t_m + PRE[1]
    m = (ct >= lo) & (ct <= hi)
    bycell = {}
    for t, y, x, nx, k in zip(ct[m].tolist(), cy[m].tolist(), cx[m].tolist(),
                              cnX[m].tolist(), cid[m].tolist()):
        bycell.setdefault((t, k), []).append(((y, x), nx))

    km = (kt >= lo) & (kt <= hi)
    res = {w: {"S1": [], "S2": []} for w in ("FAR", "PRE")}
    sizes_ok, sizes_small = [], []
    seen = 0
    for t, k, nc, a0y, a0x, soy, sox, xd in zip(kt[km].tolist(), kid[km].tolist(), knc[km].tolist(),
                                                ka0y[km].tolist(), ka0x[km].tolist(),
                                                ksoy[km].tolist(), ksox[km].tolist(),
                                                kxd[km].tolist()):
        d = t - t_m
        win = "FAR" if FAR[0] <= d <= FAR[1] else ("PRE" if PRE[0] <= d <= PRE[1] else None)
        if win is None:
            continue
        seen += 1
        cen = S.centroid_frozen(a0y, a0x, soy, sox, nc)
        rows = bycell.get((t, k))
        if rows:
            cells = [c for c, _ in rows]; nx = [v for _, v in rows]
            s1 = S.S1(cells, nx, cen)
            if s1 is None:
                sizes_small.append(len(cells))
            else:
                sizes_ok.append(len(cells)); res[win]["S1"].append(s1)
        if t in nXtot:
            res[win]["S2"].append(S.S2(xd, nXtot[t]))
    out = {"tag": meta["tag"], "arm": meta["arm"], "index": int(meta["index"]), "t_m": t_m,
           "component_steps_seen": seen,
           "S1_defined": len(sizes_ok), "S1_undefined_too_small": len(sizes_small),
           "sizes_when_defined_min_med_max": ([int(np.min(sizes_ok)), int(np.median(sizes_ok)),
                                               int(np.max(sizes_ok))] if sizes_ok else None),
           "sizes_when_too_small_min_med_max": ([int(np.min(sizes_small)), int(np.median(sizes_small)),
                                                 int(np.max(sizes_small))] if sizes_small else None)}
    for w in ("FAR", "PRE"):
        for st in ("S1", "S2"):
            v = res[w][st]
            out[f"{w}_{st}_n"] = len(v)
            out[f"{w}_{st}_mean"] = float(np.mean(v)) if v else None
            out[f"{w}_{st}_median"] = float(np.median(v)) if v else None
    return out


def main(out_path, shard, nshards):
    rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
    RAW = "/home/claude/TBRT02_raw"
    jobs = [(r["index"], a, os.path.join(RAW, os.path.basename(d["path"])))
            for r in adm for a, d in sorted(r["ARCHIVES"].items())]
    jobs = [j for i, j in enumerate(jobs) if i % nshards == shard]
    res = []
    for idx, arm, path in jobs:
        res.append(one(path))
        print(json.dumps({"index": idx, "arm": arm, "S1def": res[-1]["S1_defined"],
                          "S1small": res[-1]["S1_undefined_too_small"],
                          "FAR_S2": res[-1]["FAR_S2_median"], "PRE_S2": res[-1]["PRE_S2_median"]}),
              flush=True)
        json.dump(res, open(out_path, "w"))


if __name__ == "__main__":
    cap = json.load(open(f"{REPO}/RPP97/out/RPP97_CAPABILITY.json"))
    assert cap["MEASUREMENT_MAY_PROCEED"], "the capability test did not clear the measurement"
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
