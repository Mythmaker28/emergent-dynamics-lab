"""TBRT02 — connectivity exposure, measured POST HOC from the archives.

WHY THIS FILE EXISTS INSTEAD OF LEDGER FIELDS. The suggestion was to add six NON_ADJUDICATIVE
fields to the sealed ledger for every admissible triple. The scientific motive is sound and is
adopted in full: Hintze and Bohm's outlier-automaton work admits SPATIALLY DISJOINT replicators, so
defining a centre as a connected component is a contested modelling assumption, and the right
response mid-campaign is to record enough to test it later rather than to change the criterion.

But the ledger is written by tbrt02_fork.one_seed, and that file is pinned by METHODS_HASH inside
the committed master freeze. Editing it would make METHODS_HASH unverifiable — which is exactly how
TBRT01 died three hours ago, and exactly what the guard exists to prevent. So the literal
instruction is REFUSED and the goal is met another way.

Everything those six fields would have held is recoverable from the archives, because the archives
record every Y-occupied cell on every row. Nothing needs to be captured at run time. This file
computes them afterwards, changes no frozen artefact, and re-spends no world.

THESE QUANTITIES ENTER NO VERDICT. They are exposure only. The frozen refutation condition remains
primary and sole, and no gate, disposition or adjudication in TBRT02 reads anything computed here.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
import numpy as np
from scipy import ndimage

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H          # noqa: E402
import clea01_lineage_i2 as I2       # noqa: E402

L = I2.L
NON_ADJUDICATIVE = ("These fields are EXPOSURE ONLY and enter no verdict. No gate, no disposition "
                    "and no adjudication in TBRT02 reads them. They exist so that the connected-"
                    "component definition of a centre can be tested later without re-spending the "
                    "campaign.")


def _components(occ):
    """toroidal 8-connected labelling. scipy.ndimage.label is not periodic, so the field is tiled
    3x3, labelled once, and the labels of the centre tile are unified through the wrap."""
    if not occ.any():
        return 0, [], None
    big = np.tile(occ, (3, 3))
    lab, n = ndimage.label(big, structure=np.ones((3, 3), bool))
    centre = lab[L:2 * L, L:2 * L]
    # unify labels that are the same physical component across the wrap
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x]); x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for ty in range(3):
        for tx in range(3):
            tile = lab[ty * L:(ty + 1) * L, tx * L:(tx + 1) * L]
            m = (tile > 0) & (centre > 0)
            for a, b in zip(tile[m].tolist(), centre[m].tolist()):
                union(a, b)
    roots = {}
    for y, x in np.argwhere(centre > 0):
        roots.setdefault(find(int(centre[y, x])), []).append((int(y), int(x)))
    sizes = sorted((len(v) for v in roots.values()), reverse=True)
    return len(roots), sizes, roots


def _min_toroidal_distance(groups):
    if len(groups) < 2:
        return None
    g = sorted(groups.values(), key=len, reverse=True)[:2]
    best = None
    for (ay, ax) in g[0]:
        for (by, bx) in g[1]:
            dy = min((ay - by) % L, (by - ay) % L)
            dx = min((ax - bx) % L, (bx - ax) % L)
            d = max(dy, dx)
            best = d if best is None else min(best, d)
    return best


def one_arm(path, t_m, daughter_cells):
    meta, T, data, YB, YD, XB = I2.load_grids(path, t_m)
    occ0, nY0 = I2.grid_at(data, t_m)
    n_trig, sizes_trig, groups_trig = _components(occ0)
    root = np.zeros((L, L), bool)
    for a, b in daughter_cells:
        root[int(a), int(b)] = True
    certain = root & occ0
    ever_split = False
    last = (n_trig, sizes_trig)
    prev = occ0
    t = t_m
    while t + 1 < T:
        occ, nY = I2.grid_at(data, t + 1)
        if not occ.any():
            break
        certain = occ & I2.dilate(certain) & ~I2.dilate(prev & ~certain)
        if certain.any():
            nc, _, _ = _components(certain)
            if nc > 1:
                ever_split = True
        prev = occ
        t += 1
        last = None
    occ_end, _ = I2.grid_at(data, min(t, T - 1))
    n_end, sizes_end, groups_end = _components(occ_end)
    return {
        "n_Y_components_at_trigger": n_trig,
        "n_Y_components_at_end": n_end,
        "size_largest_component": sizes_end[0] if sizes_end else 0,
        "size_second_largest_component": sizes_end[1] if len(sizes_end) > 1 else None,
        "min_toroidal_distance_between_two_largest": _min_toroidal_distance(groups_end or {}),
        "daughter_CERTAIN_set_ever_split_into_2_or_more": ever_split,
        "last_row_examined": int(t),
    }


def main(out_path):
    led = []
    for f in sorted(os.listdir(f"{REPO}/TBRT02/work")):
        if f.endswith(".jsonl"):
            for line in open(f"{REPO}/TBRT02/work/{f}"):
                if line.strip():
                    led.append(json.loads(line))
    adm = sorted([r for r in led if r.get("ADMISSIBLE")], key=lambda r: r["index"])
    done = json.load(open(out_path)) if os.path.exists(out_path) else {"RECORDS": {}}
    done.setdefault("RECORDS", {})
    for r in adm:
        key = str(r["index"])
        if key in done["RECORDS"]:
            continue
        rec = {"index": r["index"], "t_m": r["t_m"]}
        for arm, a in r["ARCHIVES"].items():
            if not os.path.exists(a["path"]):
                rec[arm] = {"ARCHIVE_MISSING": True}
                continue
            rec[arm] = one_arm(a["path"], r["t_m"], r["FORK"]["locked_daughter_cells"])
        done["RECORDS"][key] = rec
        print(f"  index {r['index']} done", flush=True)
    done.update({
        "MISSION": "TBRT02", "SECTION": "connectivity exposure, post hoc, NON-ADJUDICATIVE",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "NON_ADJUDICATIVE": NON_ADJUDICATIVE,
        "WHY_NOT_IN_THE_SEALED_LEDGER": "the ledger is written by tbrt02_fork.one_seed, pinned by "
            "METHODS_HASH in the committed master freeze. Editing it would make METHODS_HASH "
            "unverifiable, which is how TBRT01 died. Computed from the archives instead; nothing "
            "is lost because the archives record every Y-occupied cell on every row.",
        "MOTIVE": "a centre defined as a connected component is a contested modelling assumption. "
                  "Recording this now means the assumption can be tested later without re-spending "
                  "the campaign. It does not change any criterion.",
        "TOROIDAL_LABELLING": "scipy.ndimage.label is not periodic, so the field is tiled 3x3, "
                              "labelled once, and the centre tile's labels are unified through the "
                              "wrap by union-find.",
        "N_ADMISSIBLE_TRIPLES_COVERED": len(done["RECORDS"]),
    })
    json.dump(done, open(out_path, "w"), indent=1)
    print("records:", len(done["RECORDS"]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else f"{REPO}/TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json")
