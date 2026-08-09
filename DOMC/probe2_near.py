"""DOMC probe 2 — is the NEAR geometry viable, and how strong is the coupling between the two
components in each geometry?

Two questions, both pre-registration questions, neither a hypothesis test:
  Q1  does the founding at sites (32,24) and (32,40) also give exactly two components over the
      full experimental horizon?
  Q2  how strongly does driving ONE side change the OTHER component? This is the coupling the
      word "communicating" refers to, and it must be measured, not asserted.
"""
from __future__ import annotations
import sys, json, time
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import domc_core as K

HOR = 1400


def viability(geom, seeds):
    K.set_geometry(geom)
    out = []
    for s in seeds:
        eng = K.engine()
        st = K.found(s)
        rec = {"seed": s, "series": []}
        for t in range(1, HOR + 1):
            st = eng.step(st)
            if t % 100 == 0:
                pick, dst, ncomp = K.read_sites(st)
                rec["series"].append([t, ncomp,
                                      int(pick["A"].size) if pick["A"] else 0,
                                      int(pick["B"].size) if pick["B"] else 0,
                                      round(dst["A"], 2), round(dst["B"], 2)])
        out.append(rec)
        print(geom, s, " ".join(f"{r[0]}:{r[1]}({r[2]},{r[3]})" for r in rec["series"]), flush=True)
    return out


def coupling(geom, seeds):
    """Drive ONE half for one frozen phase; measure how much the OTHER component's memory and
    response move, against the same component in the undriven world. Fully paired."""
    K.set_geometry(geom)
    res = []
    for s in seeds:
        eng = K.engine()
        base = K.advance(eng, K.found(s), K.T_FOUND)
        # driven: nutrient on half A only, for one frozen phase; free: nothing
        drv = base.copy()
        for _ in range(K.T_PHASE):
            drv.N[:, K.HALF_A] = drv.N[:, K.HALF_A] + K.AMP
            drv = eng.step(drv)
        fre = K.advance(eng, base, K.T_PHASE)
        drv = K.advance(eng, drv, K.SETTLE)
        fre = K.advance(eng, fre, K.SETTLE)
        sd, sf = K.scalars(drv), K.scalars(fre)
        rd, rf = K.response_at_sites(eng, drv), K.response_at_sites(eng, fre)
        if any(v is None for v in list(sd.values()) + list(sf.values())):
            continue
        row = {"seed": s}
        for nm in ("A", "B"):
            row[f"dm_plus_{nm}"] = sd[nm]["m_plus"] - sf[nm]["m_plus"]
            row[f"dm_minus_{nm}"] = sd[nm]["m_minus"] - sf[nm]["m_minus"]
            row[f"dR_{nm}"] = K.dist(rd[nm], rf[nm])
        row["memory_leak_ratio"] = abs(row["dm_plus_B"]) / max(abs(row["dm_plus_A"]), 1e-12)
        row["response_leak_ratio"] = row["dR_B"] / max(row["dR_A"], 1e-12)
        res.append(row)
        print(f"{geom} s={s}  dm+_A={row['dm_plus_A']:+.4f} dm+_B={row['dm_plus_B']:+.4f} "
              f"leak={row['memory_leak_ratio']:.4f} | dR_A={row['dR_A']:.4f} "
              f"dR_B={row['dR_B']:.4f} leak={row['response_leak_ratio']:.4f}", flush=True)
    return res


if __name__ == "__main__":
    t0 = time.time()
    SEEDS = (34000, 34001, 34002)
    out = {"viability": {}, "coupling": {}}
    for g in ("FAR", "NEAR"):
        out["viability"][g] = viability(g, SEEDS)
    for g in ("FAR", "NEAR"):
        out["coupling"][g] = coupling(g, SEEDS)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open("probe2_near.json", "w"), indent=1)
    print("DONE", out["seconds"], "s")
