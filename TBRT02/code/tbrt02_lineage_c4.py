"""TBRT02 — C4 enumeration. Co-propagates TWO lineages from the frozen Model C primitives.

It does NOT reimplement Model C. It imports `L`, `OFFSETS`, `sources` and `load_rows` from
CLEA01/code/clea01_lineage_i1.py byte-unchanged, and uses them to propagate, on the SAME rows
and in lockstep:

    the DAUGHTER lineage   root = meta.intervention.daughter_cells
    the COMPETITOR lineage root = meta.intervention.competitor_cell   (DISPLACED arm only)

and reports, per step and in aggregate, the three readings declared in
TBRT02/work/TBRT02_C4_ANALYSIS_NOTES.md BEFORE any of them was computed:

    R1  CERTAIN_daughter  ∩ DESC_competitor      the frozen refutation condition, strict reading
    R2  POSSIBLE_daughter ∩ DESC_competitor      permissive contamination
    R3  quantum-level                            NOT COMPUTABLE: the archive carries no hop
                                                 ledger (schema TLMR01-ARCHIVE-1 has no pq_yhop)

DESC (descendants of the displaced mass) is the ANY-source closure from the competitor cell —
the same rule the frozen model calls POSSIBLE, applied to the competitor root.

Nothing here selects on an outcome. Every admissible triple is processed; none is skipped.
"""
from __future__ import annotations
import os, sys, json, gzip
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "CLEA01/code"))
import clea01_lineage_i1 as MC          # byte-unchanged: the frozen Model C

L, OFFSETS, sources, load_rows = MC.L, MC.OFFSETS, MC.sources, MC.load_rows


def post_intervention_row(occ_tm, iv, arm):
    """Reconstruct the t_m row as it stands AFTER the intervention.

    The archive records the fork row BEFORE the intervention (schema: removal_semantics), so it
    still carries the parent's Y and does not yet carry the displaced mass. Both edits are fully
    determined by meta.intervention — parent_cells, competitor_cell, competitor_mass — with no
    free parameter. Returns (row, audit) so the reconstruction can be checked, not trusted."""
    row = dict(occ_tm)
    removed = 0
    if arm in ("SELECTIVE", "DISPLACED"):
        for c in iv["parent_cells"]:
            c = (int(c[0]), int(c[1]))
            removed += row.pop(c, 0)
    placed = 0
    if arm == "DISPLACED" and iv.get("competitor_cell") is not None:
        c = (int(iv["competitor_cell"][0]), int(iv["competitor_cell"][1]))
        placed = int(iv["competitor_mass"])
        row[c] = row.get(c, 0) + placed
    return row, {"Y_before": sum(occ_tm.values()), "Y_after": sum(row.values()),
                 "removed_from_parent": removed, "placed_at_competitor": placed,
                 "MASS_CONSERVED": (removed == placed) if arm == "DISPLACED" else None,
                 "PARENT_Y_REMOVED": removed if arm in ("SELECTIVE", "DISPLACED") else 0}


def co_run(path, horizon_cap=None, variant="A"):
    """Propagate the daughter lineage (CERTAIN and POSSIBLE) and, when the arm is DISPLACED,
    the competitor's descendant set, on the same rows, step by step."""
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0])); z.close()
    iv = meta["intervention"]
    t_m = int(meta["t_m"])
    meta_, T, occ, YB, YD, XB = load_rows(path, t_m)
    cap = T if horizon_cap is None else min(T, horizon_cap)

    root = set((int(a), int(b)) for a, b in iv["daughter_cells"])
    comp_cell = iv.get("competitor_cell")
    comp_root = set() if comp_cell is None else {(int(comp_cell[0]), int(comp_cell[1]))}

    prev_recorded = occ.get(t_m, {})
    if variant == "B":
        prev, recon = post_intervention_row(prev_recorded, iv, meta["arm"])
    else:
        prev, recon = prev_recorded, None
    certain  = set(c for c in root if c in prev)
    possible = set(certain)
    # The competitor mass is placed AT t_m but the row at t_m is recorded BEFORE the
    # intervention (schema: removal_semantics), so the destination cell is absent from
    # occ[t_m] and CANNOT be reached by sources() on that row. Its descendant set is
    # therefore seeded at t_m+1, on the first row in which the displaced mass exists.
    # Verified on the archives: the destination cell first appears at t_m+1, never at t_m.
    desc = set(comp_root) if variant == "B" else set()
    desc_pending = set() if variant == "B" else set(comp_root)
    _B_seed = (variant == "B" and bool(comp_root))

    seeded_ok = (certain == root)
    r1_first = r2_first = None
    r1_rows = r2_rows = 0
    r1_cells, r2_cells = [], []
    cert_end = poss_end = desc_end = t_m
    cert_steps = poss_steps = 0
    cert_exposure = sum(prev[c] for c in certain)
    poss_exposure = sum(prev[c] for c in possible)
    desc_max = 0
    cert_max = len(certain)
    desc_seeded_at = None
    desc_seed_present = None
    if _B_seed:
        desc_seeded_at = t_m
        desc_seed_present = True
        desc_max = len(desc)
    inv = 0
    t = t_m
    while t + 1 < cap:
        cur = occ.get(t + 1, {})
        if not cur:
            break
        nc, npo, nd = set(), set(), set()
        for d in cur:
            S = sources(d, prev)
            if not S:
                inv += 1
                continue
            if S <= certain and certain: nc.add(d)
            if S & possible:             npo.add(d)
            if S & desc:                 nd.add(d)
        if desc_pending:                      # the seeding row, t_m+1
            nd |= {c for c in desc_pending if c in cur}
            desc_seeded_at = t + 1
            desc_seed_present = bool(nd & desc_pending)
            desc_pending = set()
        certain, possible, desc = nc, npo, nd
        # the two readings, enumerated
        i1 = certain & desc
        if i1:
            r1_rows += 1
            if r1_first is None: r1_first = t + 1
            if len(r1_cells) < 20: r1_cells.append({"t": t + 1, "cells": sorted(map(list, i1))})
        i2 = possible & desc
        if i2:
            r2_rows += 1
            if r2_first is None: r2_first = t + 1
            if len(r2_cells) < 5: r2_cells.append({"t": t + 1, "n": len(i2)})
        if certain:
            cert_end = t + 1; cert_steps += 1
            cert_exposure += sum(cur[c] for c in certain)
            cert_max = max(cert_max, len(certain))
        if possible:
            poss_end = t + 1; poss_steps += 1
            poss_exposure += sum(cur[c] for c in possible)
        if desc:
            desc_end = t + 1
            desc_max = max(desc_max, len(desc))
        prev = cur
        t += 1
        if not possible and not desc:
            break
    return {
        "VARIANT": variant, "reconstruction_audit": recon,
        "tag": meta["tag"], "arm": meta["arm"], "index": int(meta["index"]),
        "seed": int(meta["seed"]), "t_m": t_m, "horizon": T,
        "root_all_occupied_at_t_m": seeded_ok,
        "competitor_cell": comp_cell, "competitor_mass": iv.get("competitor_mass"),
        "CERTAIN_duration": cert_end - t_m, "CERTAIN_steps": cert_steps,
        "CERTAIN_exposure": cert_exposure, "CERTAIN_max_cells": cert_max,
        "POSSIBLE_duration": poss_end - t_m, "POSSIBLE_steps": poss_steps,
        "POSSIBLE_exposure": poss_exposure,
        "DESC_duration": (desc_end - t_m) if desc_seeded_at else 0,
        "DESC_max_cells": desc_max,
        "DESC_seeded_at": desc_seeded_at,
        "DESC_seed_cell_present_in_that_row": desc_seed_present,
        "R1_rows": r1_rows, "R1_first_t": r1_first, "R1_witness": r1_cells,
        "R2_rows": r2_rows, "R2_first_t": r2_first, "R2_witness": r2_cells,
        "R1_FIRED": r1_rows > 0, "R2_FIRED": r2_rows > 0,
        "n_invariant_violations": inv, "stopped_at": t,
    }


def main(out_path, only_arm=None, shard=None, nshards=None):
    import glob
    rows = []
    for p in sorted(glob.glob(os.path.join(REPO, "TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))):
        for l in open(p):
            l = l.strip()
            if l: rows.append(json.loads(l))
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
    jobs = []
    for r in adm:
        for arm, a in sorted(r["ARCHIVES"].items()):
            if only_arm and arm != only_arm: continue
            jobs.append((r["index"], arm, a["path"]))
    if shard is not None:
        jobs = [j for i, j in enumerate(jobs) if i % nshards == shard]
    res = []
    for idx, arm, path in jobs:
        d = co_run(path, variant=os.environ.get("TBRT02_C4_VARIANT","A"))
        res.append(d)
        print(json.dumps({"index": idx, "arm": arm, "R1": d["R1_FIRED"], "R2": d["R2_FIRED"],
                          "CERT_dur": d["CERTAIN_duration"], "POSS_dur": d["POSSIBLE_duration"],
                          "DESC_dur": d["DESC_duration"]}), flush=True)
        with open(out_path, "w") as f:
            json.dump(res, f)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    out = a[0]
    arm = a[1] if len(a) > 1 and a[1] != "-" else None
    sh = int(a[2]) if len(a) > 3 else None
    ns = int(a[3]) if len(a) > 3 else None
    main(out, arm, sh, ns)
