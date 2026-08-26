"""CLEA01 §4 — the ambient-inheritance specificity pass.

It changes NO rule. It re-runs the frozen Model C propagation of implementation 2 and records two
extra observables that section 4 item 4 requires and that the first pass did not store:

  POST_A_CLAIM_FRACTION  = sum over rows AFTER Model A's identity ended of the Y mass Model C calls
                           CERTAIN, divided by the world Y mass over the same rows. It answers, with
                           no threshold, "once the locked spatial daughter is gone, how much of the
                           world does the causal lineage claim?"
  AMBIENT_ROWS_CLAIMED   = the number of those rows on which CERTAIN is non-empty.

Declared honestly: these were added after the first development sweep, because section 4 item 4
demands an ambient-inheritance test and the first sweep did not record one. No rule, no constant and
no threshold was introduced or tuned; only two sums are counted.
"""
from __future__ import annotations
import json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import clea01_lineage_i2 as I2

def run(path, t_m, daughter_cells, a_end):
    meta, T, data, YB, YD, XB = I2.load_grids(path, t_m)
    occ0, nY0 = I2.grid_at(data, t_m)
    root = np.zeros((I2.L, I2.L), bool)
    for a, b in daughter_cells: root[int(a), int(b)] = True
    certain = root & occ0
    possible = certain.copy()
    post_cert = post_world = 0
    rows_claimed = rows_post = 0
    prev_occ = occ0
    t = t_m
    while t + 1 < T:
        occ, nY = I2.grid_at(data, t + 1)
        if not occ.any(): break
        dil_cert = I2.dilate(certain); dil_noncert = I2.dilate(prev_occ & ~certain)
        dil_poss = I2.dilate(possible)
        certain = occ & dil_cert & ~dil_noncert
        possible = occ & dil_poss
        if t + 1 > a_end:
            rows_post += 1
            w = int(nY.sum()); c = int(nY[certain].sum())
            post_world += w; post_cert += c
            if certain.any(): rows_claimed += 1
        prev_occ = occ
        t += 1
        if not possible.any(): break
    return {"A_end_row": a_end, "rows_after_A": rows_post,
            "AMBIENT_ROWS_CLAIMED": rows_claimed,
            "certain_mass_after_A": post_cert, "world_mass_after_A": post_world,
            "POST_A_CLAIM_FRACTION": (post_cert / post_world) if post_world else None}

def main(split_name, out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    meas = {m["index"]: m for m in json.load(open(f"{REPO}/OMLDCT02/work/OMLDCT02_PAIR_MEASUREMENTS.json"))}
    sm = json.load(open(f"{REPO}/CLEA01/out/CLEA01_SPLIT_MANIFEST.json"))
    want = [p["index"] for p in sm["PAIRS"] if p["SPLIT"] == split_name]
    done = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for i in want:
        if str(i) in done: continue
        r = by[i]; tm = r["t_m"]; dc = r["FORK"]["locked_daughter_cells"]
        rec = {"index": i, "t_m": tm}
        for arm in ("SELECTIVE", "SHAM"):
            a_end = meas[i][arm]["A"]["interval_end"]
            rec[arm] = run(r["ARCHIVES"][arm]["path"], tm, dc, a_end)
        done[str(i)] = rec
        tmp = out_path + ".part"
        with open(tmp, "w") as fh: json.dump(done, fh)
        os.replace(tmp, out_path)
        fmt = lambda v: "n/a" if v is None else f"{v:.4f}"
        print(f"index {i}: S={fmt(rec['SELECTIVE']['POST_A_CLAIM_FRACTION'])} "
              f"H={fmt(rec['SHAM']['POST_A_CLAIM_FRACTION'])}", flush=True)
    print("done", len(done))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
