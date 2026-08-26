"""CLEA01 closure §7 and §8 — exhibit the two structural witnesses, and publish the two G4 failures
row by row.

The closure launcher refuses to accept a difference of one to four particles out of ~1.7 million as
"meaningful merely because it is nonzero", and requires instead a QUALITATIVE structural
distinction, exhibited:

    (a) at least one load-bearing continuation that Model A terminates but Model C retains, through
        an explicit causal witness;
    (b) at least one ambient continuation that Model B retains but Model C rejects for lack of a
        causal path.

The arm is not hand-picked. It is chosen by a rule stated before it is applied: among SHAM arms
where C's certain duration exceeds A's AND C rejects more than half the post-A world mass, take the
one with the largest excess duration, breaking ties by index. That rule selects one arm; both
witnesses are then read out of that same arm, so the two halves of the requirement are not met by
two conveniently different worlds.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/CLEA01/code")
os.environ.setdefault("LDFMA01_REPO", REPO)
sys.path.insert(0, f"{REPO}/LDFMA01/code")
import omldct02_hashes as H
import clea01_lineage_i1 as I1
import clea01_lineage_i2 as I2
import clea01_g4_containment as G4

L = 36
OFF = I1.OFFSETS


def walk(path, t_m, daughter_cells, upto):
    """CERTAIN and POSSIBLE and the raw occupancy, row by row, to `upto`."""
    meta, T, data, YB, YD, XB = I2.load_grids(path, t_m)
    occ0, nY0 = I2.grid_at(data, t_m)
    root = np.zeros((L, L), bool)
    for a, b in daughter_cells:
        root[int(a), int(b)] = True
    certain = root & occ0
    possible = certain.copy()
    hist = {t_m: (occ0.copy(), certain.copy(), possible.copy())}
    prev = occ0
    t = t_m
    while t + 1 <= upto and t + 1 < T:
        occ, nY = I2.grid_at(data, t + 1)
        if not occ.any():
            break
        certain = occ & I2.dilate(certain) & ~I2.dilate(prev & ~certain)
        possible = occ & I2.dilate(possible)
        hist[t + 1] = (occ.copy(), certain.copy(), possible.copy())
        prev = occ
        t += 1
    return hist, T


def cells(a):
    return [(int(y), int(x)) for y, x in np.argwhere(a)]


def witness_for(d, occ_prev, certain_prev):
    """the enumerable witness for 'd is CERTAIN': S(d) and the certainty of each member."""
    y, x = d
    S = []
    for dy, dx in OFF:
        c = ((y + dy) % L, (x + dx) % L)
        if occ_prev[c]:
            S.append({"source": list(c), "was_CERTAIN": bool(certain_prev[c])})
    return {"cell": list(d), "S_of_d": S, "S_is_non_empty": bool(S),
            "every_source_certain": bool(S) and all(s["was_CERTAIN"] for s in S)}


def rejection_for(d, occ_prev, possible_prev):
    y, x = d
    S = []
    for dy, dx in OFF:
        c = ((y + dy) % L, (x + dx) % L)
        if occ_prev[c]:
            S.append({"source": list(c), "was_POSSIBLE": bool(possible_prev[c])})
    return {"cell": list(d), "S_of_d": S,
            "S_intersect_POSSIBLE_is_empty": not any(s["was_POSSIBLE"] for s in S),
            "reason": "every admissible source of this cell is outside the lineage envelope, so no "
                      "causal path from the daughter root reaches it"}


def main():
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    per = {(a["index"], a["arm"]): a for a in
           json.load(open(f"{REPO}/CLEA01/out/CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json"))["PER_ARM"]}
    spec = json.load(open(f"{REPO}/CLEA01/work/close_spec.json"))

    RULE = ("among SHAM arms with C_certain_duration > A_duration and POST_A_REJECTED_FRACTION > 0.5, "
            "take the largest (C_certain_duration - A_duration); ties broken by smallest index.")
    cand = []
    for (i, arm), a in per.items():
        if arm != "SHAM":
            continue
        s = spec[str(i)]["SHAM"]
        rej = s.get("POST_A_REJECTED_FRACTION") or 0
        if a["C_certain_duration"] > a["A_duration"] and rej > 0.5:
            cand.append((-(a["C_certain_duration"] - a["A_duration"]), i))
    cand.sort()
    pick = cand[0][1]

    r = by[pick]; tm = r["t_m"]; dc = r["FORK"]["locked_daughter_cells"]
    a = per[(pick, "SHAM")]
    a_end = tm + a["A_duration"]
    c_end = tm + a["C_certain_duration"]
    hist, T = walk(r["ARCHIVES"]["SHAM"]["path"], tm, dc, min(c_end + 2, tm + a["B_duration"]))

    # (a) a continuation A has terminated but C retains, with its witness.
    #     The exhibit row is the post-A row, still inside C's certain interval, carrying the most
    #     outright-rejected occupied cells — so that BOTH witnesses can be read from one row and
    #     the rejection half is not exhibited by a single cell. The rule is stated, not tuned:
    #     any post-A row inside the certain interval would satisfy the requirement.
    usable = [t for t in range(a_end + 1, c_end + 1)
              if t in hist and hist[t][1].any() and (t - 1) in hist]
    row_a = max(usable, key=lambda t: (int((hist[t][0] & ~hist[t][2]).sum()), -t))
    row_first = usable[0] if usable else None
    occ, cert, poss = hist[row_a]
    p_occ, p_cert, p_poss = hist[row_a - 1]
    kept = cells(cert)
    wit = [witness_for(d, p_occ, p_cert) for d in kept[:6]]

    # (b) an ambient continuation B retains but C rejects, from the same row
    rejected = cells(occ & ~poss)
    rej = [rejection_for(d, p_occ, p_poss) for d in rejected[:6]]

    ex = {
        "SELECTION_RULE": RULE, "N_CANDIDATE_ARMS": len(cand),
        "ARM_SELECTED": {"index": pick, "arm": "SHAM", "t_m": tm},
        "A_duration": a["A_duration"], "C_certain_duration": a["C_certain_duration"],
        "B_duration": a["B_duration"],
        "A_ended_at_row": a_end, "C_certain_ended_at_row": c_end,
        "POST_A_CLAIM_FRACTION": spec[str(pick)]["SHAM"]["POST_A_CLAIM_FRACTION"],
        "POST_A_REJECTED_FRACTION": spec[str(pick)]["SHAM"]["POST_A_REJECTED_FRACTION"],
        "CELLS_REJECTED_OVER_THE_WHOLE_POST_A_WINDOW":
            spec[str(pick)]["SHAM"]["cells_rejected_after_A"],
        "OCCUPIED_CELLS_OVER_THE_WHOLE_POST_A_WINDOW":
            spec[str(pick)]["SHAM"]["occupied_cells_after_A"],
        "EXHIBIT_ROW_SELECTION": "the post-A row inside C's certain interval with the most "
                                 "outright-rejected occupied cells; ties to the earlier row. "
                                 "%d rows qualified." % len(usable),
        "FIRST_QUALIFYING_ROW": row_first,
        "WITNESS_A_ROW": row_a,
        "WITNESS_A_N_CERTAIN_CELLS_ON_THAT_ROW": len(kept),
        "WITNESS_A_EXAMPLES": wit,
        "WITNESS_A_MEANS": "Model A's identity ended at row %d. On row %d, %d cells are still "
                           "CERTAIN, and for each one the witness is enumerable: every admissible "
                           "source on the previous row was itself CERTAIN. The continuation is "
                           "%d rows long — %d rows beyond where A stopped."
                           % (a_end, row_a, len(kept), a["C_certain_duration"],
                              a["C_certain_duration"] - a["A_duration"]),
        "WITNESS_B_ROW": row_a,
        "WITNESS_B_N_OCCUPIED_CELLS_REJECTED_ON_THAT_ROW": len(rejected),
        "WITNESS_B_EXAMPLES": rej,
        "WITNESS_B_MEANS": "on the same row the world carries %d occupied cells that Model B counts "
                           "and Model C rejects outright — not as uncertain, but as unreachable: "
                           "none of their admissible sources is even POSSIBLE."
                           % len(rejected),
        "BOTH_WITNESSES_COME_FROM_THE_SAME_ARM_AND_THE_SAME_ROW": True,
    }

    # §8 — the two G4 failures, row by row
    g4 = {}
    for idx in (402, 518):
        rr = by[idx]; t0 = rr["t_m"]; d0 = rr["FORK"]["locked_daughter_cells"]
        p = rr["ARCHIVES"]["SHAM"]["path"]
        acells, aend = G4.a_cells_by_row(p, t0, d0)
        h, _T = walk(p, t0, d0, aend)
        rows = []
        for t in sorted(acells):
            if t not in h:
                continue
            occ_, cert_, poss_ = h[t]
            miss = sorted(set(acells[t]) - set(cells(cert_)))
            if not miss:
                continue
            pocc, pcert, pposs = h[t - 1] if (t - 1) in h else (None, None, None)
            det = []
            for d in miss:
                e = {"cell": list(d), "in_A": True, "in_C_CERTAIN": False,
                     "in_C_POSSIBLE": bool(poss_[d])}
                if pocc is not None:
                    e.update(witness_for(d, pocc, pcert))
                    e["S_intersect_POSSIBLE_is_empty"] = not any(
                        pposs[tuple(s["source"])] for s in e["S_of_d"])
                det.append(e)
            rows.append({"row": t, "A_cells": [list(c) for c in sorted(acells[t])],
                         "C_CERTAIN_cells": [list(c) for c in cells(cert_)],
                         "raw_occupied_cells": [list(c) for c in cells(occ_)],
                         "missing_from_C": [list(c) for c in miss], "detail": det})
            if len(rows) >= 6:
                break
        # was any missing cell EVER certain or possible, at any row up to A's end?
        ever = {}
        allmiss = sorted({tuple(c) for rw in rows for c in rw["missing_from_C"]})
        for d in allmiss:
            d = tuple(d)
            ec = any(h[t][1][d] for t in h)
            ep = any(h[t][2][d] for t in h)
            ever[str(list(d))] = {"ever_CERTAIN": bool(ec), "ever_POSSIBLE": bool(ep)}
        g4[f"{idx}_SHAM"] = {
            "index": idx, "t_m": t0, "A_end_row": aend, "A_rows": len(acells),
            "first_disagreeing_rows": rows,
            "EVER_CERTAIN_OR_POSSIBLE_AT_ANY_ROW": ever,
            "VERDICT": "LEGITIMATE_CAUSAL_PROVENANCE_DISTINCTION__NOT_AN_IMPLEMENTATION_DEFECT"
            if all(not v["ever_CERTAIN"] and not v["ever_POSSIBLE"] for v in ever.values())
            else "REVIEW__A_MISSING_CELL_WAS_REACHABLE_AT_SOME_ROW",
        }

    doc = {"MISSION": "CLEA01", "SECTION": "7 and 8 — structural witnesses and known-success detail",
           "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
           "STRUCTURAL_WITNESS": ex, "G4_FAILURES": g4}
    doc["WITNESS_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("WITNESS_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/CLEA01/work/close_witness.json", "w"), indent=1)
    print("selected arm:", pick, "SHAM   candidates:", len(cand))
    print("A ends", a_end, " C certain ends", c_end, " B runs to", tm + a["B_duration"])
    print("witness row", row_a, ": CERTAIN cells", len(kept), " rejected occupied cells", len(rejected))
    for k, v in g4.items():
        print(k, "->", v["VERDICT"], " rows shown:", len(v["first_disagreeing_rows"]))
    return doc


if __name__ == "__main__":
    main()
