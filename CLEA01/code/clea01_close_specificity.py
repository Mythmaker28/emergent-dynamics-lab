"""CLEA01 closure §9 — ambient interval accounting, at row, mass and cell level.

The closure launcher asks for four counts that the audit pass did not record:

    ambient intervals B retains
    ambient intervals C rejects
    ambient intervals C retains with a CERTAIN witness
    ambient intervals C retains only as POSSIBLE

The archives contain exactly ONE ambient continuation per arm — the stretch of rows after Model A's
identity ends during which the world still carries Y — so the interval count is an arm count. That
is stated rather than hidden, and the row-level and mass-level accounting is reported alongside it
so the arm count cannot flatter anything.

Two differences from clea01_specificity.py, both declared:
  1. the walk does NOT stop when POSSIBLE empties. It continues while the world is occupied, so
     ambient mass with no causal path is counted rather than truncated away.
  2. POSSIBLE is tracked over the post-A window as well as CERTAIN, which is what separates
     "C rejects" from "C retains only as POSSIBLE".

No rule, constant or threshold is introduced. The propagation operator is imported unchanged.
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
    for a, b in daughter_cells:
        root[int(a), int(b)] = True
    certain = root & occ0
    possible = certain.copy()
    prev_occ = occ0
    r = dict(A_end_row=a_end, rows_after_A=0,
             rows_certain_nonempty=0, rows_possible_only=0, rows_neither=0,
             certain_mass_after_A=0, possible_mass_after_A=0, world_mass_after_A=0,
             cells_rejected_after_A=0, mass_rejected_after_A=0,
             occupied_cells_after_A=0,
             first_row_certain_after_A=None, last_row_certain_after_A=None,
             last_row_possible_after_A=None, last_occupied_row=t_m)
    t = t_m
    while t + 1 < T:
        occ, nY = I2.grid_at(data, t + 1)
        if not occ.any():
            break
        if certain.any() or possible.any():
            dil_cert = I2.dilate(certain)
            dil_noncert = I2.dilate(prev_occ & ~certain)
            certain = occ & dil_cert & ~dil_noncert
            possible = occ & I2.dilate(possible)
        row = t + 1
        r["last_occupied_row"] = row
        if row > a_end:
            r["rows_after_A"] += 1
            w = int(nY.sum())
            c = int(nY[certain].sum()) if certain.any() else 0
            p = int(nY[possible].sum()) if possible.any() else 0
            r["world_mass_after_A"] += w
            r["certain_mass_after_A"] += c
            r["possible_mass_after_A"] += p
            r["occupied_cells_after_A"] += int(occ.sum())
            rej = occ & ~possible
            r["cells_rejected_after_A"] += int(rej.sum())
            r["mass_rejected_after_A"] += int(nY[rej].sum()) if rej.any() else 0
            if certain.any():
                r["rows_certain_nonempty"] += 1
                if r["first_row_certain_after_A"] is None:
                    r["first_row_certain_after_A"] = row
                r["last_row_certain_after_A"] = row
            elif possible.any():
                r["rows_possible_only"] += 1
            else:
                r["rows_neither"] += 1
            if possible.any():
                r["last_row_possible_after_A"] = row
        prev_occ = occ
        t += 1
    w = r["world_mass_after_A"]
    r["POST_A_CLAIM_FRACTION"] = (r["certain_mass_after_A"] / w) if w else None
    r["POST_A_POSSIBLE_FRACTION"] = (r["possible_mass_after_A"] / w) if w else None
    r["POST_A_REJECTED_FRACTION"] = (r["mass_rejected_after_A"] / w) if w else None
    # the four interval verdicts, per arm
    if not w:
        r["INTERVAL"] = "NO_AMBIENT_CONTINUATION_TO_JUDGE"
    elif r["certain_mass_after_A"] > 0:
        r["INTERVAL"] = "C_RETAINS_WITH_CERTAIN_WITNESS"
    elif r["possible_mass_after_A"] > 0:
        r["INTERVAL"] = "C_RETAINS_ONLY_AS_POSSIBLE"
    else:
        r["INTERVAL"] = "C_REJECTS"
    return r


def main(split_name, out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {x["index"]: x for x in led if x.get("ADMISSIBLE")}
    meas = {m["index"]: m for m in json.load(open(f"{REPO}/OMLDCT02/work/OMLDCT02_PAIR_MEASUREMENTS.json"))}
    sm = json.load(open(f"{REPO}/CLEA01/out/CLEA01_SPLIT_MANIFEST.json"))
    want = [p["index"] for p in sm["PAIRS"] if split_name == "ALL" or p["SPLIT"] == split_name]
    done = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for i in want:
        if str(i) in done:
            continue
        x = by[i]; tm = x["t_m"]; dc = x["FORK"]["locked_daughter_cells"]
        rec = {"index": i, "t_m": tm}
        for arm in ("SELECTIVE", "SHAM"):
            rec[arm] = run(x["ARCHIVES"][arm]["path"], tm, dc, meas[i][arm]["A"]["interval_end"])
        done[str(i)] = rec
        tmp = out_path + ".part"
        with open(tmp, "w") as fh:
            json.dump(done, fh)
        os.replace(tmp, out_path)
        print(f"index {i}: S={rec['SELECTIVE']['INTERVAL']}  H={rec['SHAM']['INTERVAL']}", flush=True)
    print("done", len(done))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
