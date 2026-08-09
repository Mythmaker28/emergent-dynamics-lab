"""DOMC Phase C — the collision scan on the frozen scalar dictionary.

WHY THIS EXISTS. The first full DEV run used the frozen sc_mcm order pair ("Nc","cN"). It showed
something the design had to be told: that pair separates the two components' MEMORY states by
only |dm+| = 0.15 and |dm-| = 0.15, while separating their BODIES by 9 cells out of ~45. The
reciprocal exchange therefore swaps two nearly identical states, and the test of memory-borne
ownership is unpowered by construction. That is a property of the history pair, not a result.

WHAT IS SELECTED HERE, AND ON WHAT. One history pair out of the eight frozen candidates, on
DEVELOPMENT blocks only, by a criterion computed entirely from the frozen scalar dictionary on
the settled state -- BEFORE any probe, any response, any intervention and any endpoint:

    Q = (|dm_plus| + |dm_minus|) / (1 + |dsize| / mean_size)

i.e. memory-state separation per unit of body mismatch. Q contains no endpoint, no response, no
survival and no comparison between arms. Ties are broken by the order of the frozen candidate
list. The selected pair is then sealed and the confirmatory split is run with it.

WHAT IS ALSO MEASURED HERE. The collision itself: how much of one side's drive lands in the
other side's memory. That is a property of the world, reported for every candidate.
"""
from __future__ import annotations
import sys, json, time, statistics as S
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import domc_core as K

SEEDS = tuple(range(34000, 34012))          # DEVELOPMENT blocks only


def one(seed, hA, hB, geom="FAR"):
    K.set_geometry(geom)
    eng = K.engine()
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    s = K.apply_dual_history(eng, f, hA, hB)
    s = K.advance(eng, s, K.SETTLE)
    sc = K.scalars(s)
    if sc["A"] is None or sc["B"] is None:
        return None
    a, b = sc["A"], sc["B"]
    msz = 0.5 * (a["size"] + b["size"])
    return {"seed": seed, "pair": f"{hA}|{hB}",
            "dm_plus": a["m_plus"] - b["m_plus"], "dm_minus": a["m_minus"] - b["m_minus"],
            "m_plus_A": a["m_plus"], "m_plus_B": b["m_plus"],
            "m_minus_A": a["m_minus"], "m_minus_B": b["m_minus"],
            "dsize": a["size"] - b["size"], "mean_size": msz,
            "dmass": a["mass"] - b["mass"],
            "dlocal_c": a["local_mean_c"] - b["local_mean_c"],
            "dlocal_N": a["local_mean_N"] - b["local_mean_N"],
            "Q": (abs(a["m_plus"] - b["m_plus"]) + abs(a["m_minus"] - b["m_minus"]))
                 / (1.0 + abs(a["size"] - b["size"]) / max(msz, 1e-9))}


def collision(seed, code, geom="FAR"):
    """Drive ONE side with `code` and leave the other side undriven ("00"); measure how much of
    the drive lands in the UNDRIVEN component's memory. Pure world property, no endpoint."""
    K.set_geometry(geom)
    eng = K.engine()
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    drv = K.advance(eng, K.apply_dual_history(eng, f, code, "00"), K.SETTLE)
    nul = K.advance(eng, K.apply_dual_history(eng, f, "00", "00"), K.SETTLE)
    a, b = K.scalars(drv), K.scalars(nul)
    if any(v is None for v in list(a.values()) + list(b.values())):
        return None
    dA = a["A"]["m_plus"] - b["A"]["m_plus"]
    dB = a["B"]["m_plus"] - b["B"]["m_plus"]
    nA = a["A"]["m_minus"] - b["A"]["m_minus"]
    nB = a["B"]["m_minus"] - b["B"]["m_minus"]
    return {"seed": seed, "code": code, "dm_plus_driven": dA, "dm_plus_undriven": dB,
            "dm_minus_driven": nA, "dm_minus_undriven": nB,
            "leak_plus": abs(dB) / max(abs(dA), 1e-12),
            "leak_minus": abs(nB) / max(abs(nA), 1e-12),
            "dsize_driven": a["A"]["size"] - b["A"]["size"],
            "dsize_undriven": a["B"]["size"] - b["B"]["size"]}


if __name__ == "__main__":
    t0 = time.time()
    out = {"criterion": "Q = (|dm_plus| + |dm_minus|) / (1 + |dsize|/mean_size), median over "
                        "the 12 DEV blocks, computed on the frozen scalar dictionary of the "
                        "settled state, before any probe or endpoint",
           "candidates": [f"{a}|{b}" for a, b in K.CANDIDATE_PAIRS],
           "dev_seeds": list(SEEDS), "per_pair": {}, "collision": {}}
    for hA, hB in K.CANDIDATE_PAIRS:
        rows = [r for r in (one(s, hA, hB) for s in SEEDS) if r]
        k = f"{hA}|{hB}"
        out["per_pair"][k] = {
            "n": len(rows),
            "median_Q": S.median([r["Q"] for r in rows]),
            "median_abs_dm_plus": S.median([abs(r["dm_plus"]) for r in rows]),
            "median_abs_dm_minus": S.median([abs(r["dm_minus"]) for r in rows]),
            "median_abs_dsize": S.median([abs(r["dsize"]) for r in rows]),
            "median_mean_size": S.median([r["mean_size"] for r in rows]),
            "median_abs_dlocal_c": S.median([abs(r["dlocal_c"]) for r in rows]),
            "median_abs_dlocal_N": S.median([abs(r["dlocal_N"]) for r in rows]),
            "rows": rows}
        v = out["per_pair"][k]
        print(f"{k:10s} Q={v['median_Q']:.4f}  |dm+|={v['median_abs_dm_plus']:.4f} "
              f"|dm-|={v['median_abs_dm_minus']:.4f}  |dsize|={v['median_abs_dsize']:.1f} "
              f"of {v['median_mean_size']:.0f}  |dc|={v['median_abs_dlocal_c']:.4f} "
              f"|dN|={v['median_abs_dlocal_N']:.4f}", flush=True)
    best = max(out["per_pair"], key=lambda k: out["per_pair"][k]["median_Q"])
    out["SELECTED_PAIR"] = best
    print("\nSELECTED:", best)

    for code in ("N0", "NN", "cc"):
        rows = [r for r in (collision(s, code) for s in SEEDS) if r]
        out["collision"][code] = {
            "n": len(rows),
            "median_leak_plus": S.median([r["leak_plus"] for r in rows]),
            "median_leak_minus": S.median([r["leak_minus"] for r in rows]),
            "median_dm_plus_driven": S.median([r["dm_plus_driven"] for r in rows]),
            "median_dm_plus_undriven": S.median([r["dm_plus_undriven"] for r in rows]),
            "median_dsize_driven": S.median([r["dsize_driven"] for r in rows]),
            "median_dsize_undriven": S.median([r["dsize_undriven"] for r in rows]),
            "rows": rows}
        v = out["collision"][code]
        print(f"collision {code}: dm+ driven={v['median_dm_plus_driven']:+.4f} "
              f"undriven={v['median_dm_plus_undriven']:+.4f} leak={v['median_leak_plus']:.5f} | "
              f"dsize driven={v['median_dsize_driven']:+.0f} undriven={v['median_dsize_undriven']:+.0f}",
              flush=True)

    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open("domc_phaseC.json", "w"), indent=1)
    print("DONE", out["seconds"], "s")
