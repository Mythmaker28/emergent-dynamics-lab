"""CLEA01 G4 — the strong form: does Model C's CERTAIN set CONTAIN Model A's component cells at
every row of Model A's interval?

Duration and exposure being larger is necessary but not sufficient: C could be long and yet not
cover the very cells A tracked. This walks both objects row by row and reports the first row of
disagreement, if any.

Model A's per-row cells come from LDFMA01's frozen reconstruction (classifier A), which is what
OMLDCT02 qualified. Model C's come from implementation 2. Neither is re-specified here.
"""
from __future__ import annotations
import json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
os.environ.setdefault("LDFMA01_REPO", REPO)
sys.path.insert(0, f"{REPO}/LDFMA01/code"); sys.path.insert(0, f"{REPO}/CLEA01/code")
import ldfma01_raw as A
import clea01_lineage_i2 as I2

def a_cells_by_row(path, t_m, daughter_cells):
    w = A.World(path)
    ev, ids_at, named_at, lvl_at, n = w.trace()
    dset = frozenset((int(a), int(b)) for a, b in daughter_cells)
    gs = w.groups.get(t_m)
    hit = [j for j in range(len(gs))] if gs else []
    hit = [j for j in hit if w.gcells[t_m][j] == dset]
    if len(hit) != 1: return None, None
    did = ids_at[t_m][hit[0]]
    out = {}
    for t in range(t_m, w.T):
        ids = ids_at.get(t)
        if not ids or did not in ids: continue
        out[t] = set(map(tuple, w.gcells[t][ids.index(did)]))
    return out, max(out) if out else t_m

def c_cells_by_row(path, t_m, daughter_cells, upto):
    meta, T, data, YB, YD, XB = I2.load_grids(path, t_m)
    occ0, nY0 = I2.grid_at(data, t_m)
    root = np.zeros((I2.L, I2.L), bool)
    for a, b in daughter_cells: root[int(a), int(b)] = True
    certain = root & occ0
    out = {t_m: {(int(a), int(b)) for a, b in np.argwhere(certain)}}
    prev = occ0; t = t_m
    while t + 1 <= upto and t + 1 < T:
        occ, nY = I2.grid_at(data, t + 1)
        if not occ.any(): break
        certain = occ & I2.dilate(certain) & ~I2.dilate(prev & ~certain)
        out[t + 1] = {(int(a), int(b)) for a, b in np.argwhere(certain)}
        prev = occ; t += 1
        if not certain.any(): break
    return out

def main(split_name, out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    sm = json.load(open(f"{REPO}/CLEA01/out/CLEA01_SPLIT_MANIFEST.json"))
    want = [p["index"] for p in sm["PAIRS"] if p["SPLIT"] == split_name]
    done = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for i in want:
        if str(i) in done: continue
        r = by[i]; tm = r["t_m"]; dc = r["FORK"]["locked_daughter_cells"]
        rec = {"index": i, "t_m": tm}
        for arm in ("SELECTIVE", "SHAM"):
            p = r["ARCHIVES"][arm]["path"]
            acells, aend = a_cells_by_row(p, tm, dc)
            if acells is None:
                rec[arm] = {"A_RECONSTRUCTED": False}; continue
            ccells = c_cells_by_row(p, tm, dc, aend)
            miss = []
            for t in sorted(acells):
                c = ccells.get(t, set())
                if not acells[t] <= c:
                    miss.append({"row": t, "A_cells": sorted(acells[t]),
                                 "missing_from_C": sorted(acells[t] - c)})
                    if len(miss) >= 3: break
            rec[arm] = {"A_RECONSTRUCTED": True, "A_rows": len(acells), "A_end": aend,
                        "C_CONTAINS_A_ON_EVERY_ROW": not miss,
                        "first_failures": miss}
        done[str(i)] = rec
        tmp = out_path + ".part"
        with open(tmp, "w") as fh: json.dump(done, fh)
        os.replace(tmp, out_path)
        ok = all(v.get("C_CONTAINS_A_ON_EVERY_ROW") for k, v in rec.items() if isinstance(v, dict))
        print(f"index {i}: contains={ok}", flush=True)
    print("done", len(done))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
