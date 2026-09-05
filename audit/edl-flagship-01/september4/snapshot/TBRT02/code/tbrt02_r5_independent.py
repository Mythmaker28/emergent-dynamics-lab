"""TBRT02 — R5, reproduced independently of the checker.

R5, as the adversarial checker proposed it: at some step t, a cell of CERTAIN(daughter) and a
cell of DESC(competitor) carry the SAME c_cid — the frozen component id written by
FDOT01/code/fdot01_centres.components (toroidal single-linkage at CORE_R = 5.0) into every
archive row. Same body, therefore, under the programme's own frozen definition of a body.

The checker's numbers are NOT taken on trust. This file recomputes R5 from the archives, with
its own row reconstruction, and also recomputes R1 and R2 alongside so the three are read off
one pass and can be compared world by world.
"""
from __future__ import annotations
import os, sys, json, glob
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "CLEA01/code"))
import clea01_lineage_i1 as MC
L, OFFSETS = MC.L, MC.OFFSETS


def srcs(cell, prev):
    y, x = cell
    return {((y + dy) % L, (x + dx) % L) for dy, dx in OFFSETS} & prev.keys()


def run(path):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0])); iv = meta["intervention"]; t_m = int(meta["t_m"])
    T = int(meta["steps_executed"])
    ct = z["c_t"].astype(np.int64); cy = z["c_y"].astype(np.int64); cx = z["c_x"].astype(np.int64)
    cn = z["c_nY"].astype(np.int64); cid = z["c_cid"].astype(np.int64); z.close()
    m = (ct >= t_m) & (ct < T) & (cn > 0)
    occ, CID = {}, {}
    for t, y, x, n, k in zip(ct[m].tolist(), cy[m].tolist(), cx[m].tolist(), cn[m].tolist(), cid[m].tolist()):
        occ.setdefault(t, {})[(y, x)] = n
        CID.setdefault(t, {})[(y, x)] = k
    # post-intervention reconstruction (variant B), from meta.intervention alone
    prev = dict(occ.get(t_m, {}))
    removed = 0
    if meta["arm"] in ("SELECTIVE", "DISPLACED"):
        for c in iv["parent_cells"]:
            removed += prev.pop((int(c[0]), int(c[1])), 0)
    comp = None
    if meta["arm"] == "DISPLACED" and iv.get("competitor_cell") is not None:
        comp = (int(iv["competitor_cell"][0]), int(iv["competitor_cell"][1]))
        prev[comp] = prev.get(comp, 0) + int(iv["competitor_mass"])
    certain = {(int(a), int(b)) for a, b in iv["daughter_cells"]} & prev.keys()
    possible = set(certain)
    desc = {comp} if comp else set()
    out = {"index": int(meta["index"]), "arm": meta["arm"], "t_m": t_m,
           "R1_t": None, "R2_t": None, "R5_t": None,
           "mass_removed": removed, "mass_placed": int(iv["competitor_mass"] or 0) if comp else 0}
    t = t_m
    while t + 1 < T:
        cur = occ.get(t + 1)
        if not cur: break
        nc, npo, nd = set(), set(), set()
        for d in cur:
            S = srcs(d, prev)
            if not S: continue
            if certain and S <= certain: nc.add(d)
            if S & possible: npo.add(d)
            if S & desc: nd.add(d)
        certain, possible, desc = nc, npo, nd
        if desc:
            if out["R1_t"] is None and (certain & desc): out["R1_t"] = t + 1
            if out["R2_t"] is None and (possible & desc): out["R2_t"] = t + 1
            if out["R5_t"] is None and certain:
                k = CID.get(t + 1, {})
                kc = {k[c] for c in certain if c in k}
                kd = {k[c] for c in desc if c in k}
                if kc & kd: out["R5_t"] = t + 1
        prev = cur
        t += 1
        if not possible and not desc: break
    return out


if __name__ == "__main__":
    rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
    res = [run(r["ARCHIVES"]["DISPLACED"]["path"]) for r in adm]
    json.dump(res, open(f"{REPO}/TBRT02/work/c4/R5_INDEPENDENT.json", "w"))
    f = lambda k: [r["index"] for r in res if r[k] is not None]
    print("n", len(res))
    for k in ("R1_t", "R2_t", "R5_t"):
        v = [r[k] - r["t_m"] for r in res if r[k] is not None]
        v.sort()
        print(k, "fired", len(v), "/", len(res),
              ("min/med/max %d/%d/%d" % (v[0], v[len(v)//2], v[-1])) if v else "")
    print("R5 set == R2 set:", set(f("R5_t")) == set(f("R2_t")))
    print("R5 strictly earlier than R2 on all fired:",
          all(r["R5_t"] < r["R2_t"] for r in res if r["R5_t"] is not None and r["R2_t"] is not None))
    print("R5 indices:", sorted(f("R5_t")))
