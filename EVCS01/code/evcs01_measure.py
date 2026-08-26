"""EVCS01 §3 and §4 — Gate 0, then the threshold-free composition of E3_EXPOSURE.

Gate 0 first, and it is an exact equality against a frozen external file, so there is no room to
adjust it after seeing anything: Model A is reconstructed from LDFMA01's frozen classifier and the
parent's own two numbers are recomputed under the parent's own frozen conventions

    E3_DURATION = interval_end - t_m
    E3_EXPOSURE = sum of the mass inside A's component over rows t_m .. interval_end, t_m INCLUDED

and compared with OMLDCT02_PAIR_MEASUREMENTS.json classifier A. All 66 arms must reproduce exactly.

Then the composition. Every unit of Y mass inside A's component, on every row of the interval, falls
into exactly one of three classes under CLEA01's frozen CERTAIN/POSSIBLE operator, imported
unchanged from clea01_lineage_i2 and not re-specified here:

    CERTAIN         d is occupied, S(d) non-empty, S(d) contained in CERTAIN(t-1)
    POSSIBLE_ONLY   d is in POSSIBLE but not in CERTAIN
    NO_CAUSAL_PATH  d is in neither: no admissible source of d is even POSSIBLE

Exhaustive and disjoint by construction, because CERTAIN is a subset of POSSIBLE at every row and
the third class is the complement of POSSIBLE.

One walk produces both the gate quantities and the composition. That is stated rather than hidden:
the gate is an exact equality against bytes frozen in another mission, so computing the composition
in the same pass cannot influence whether the gate passes.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
import numpy as np
REPO = os.environ.get("EVCS01_REPO", "/home/claude/edl")
os.environ.setdefault("LDFMA01_REPO", REPO)
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
sys.path.insert(0, f"{REPO}/LDFMA01/code")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H          # noqa: E402
import clea01_lineage_i2 as I2       # noqa: E402  the frozen propagation operator, unchanged
import clea01_g4_containment as G4   # noqa: E402  the frozen Model A reconstruction, unchanged

L = I2.L


def one_arm(path, t_m, daughter_cells, interval_end_recorded):
    """returns the gate quantities and the composition for one arm."""
    acells, a_end = G4.a_cells_by_row(path, t_m, daughter_cells)
    if acells is None:
        return {"A_RECONSTRUCTED": False}

    meta, T, data, YB, YD, XB = I2.load_grids(path, t_m)
    occ0, nY0 = I2.grid_at(data, t_m)
    root = np.zeros((L, L), bool)
    for a, b in daughter_cells:
        root[int(a), int(b)] = True
    certain = root & occ0
    possible = certain.copy()

    upto = max(a_end, interval_end_recorded)
    exposure = 0
    rows_in_interval = 0
    comp = {"CERTAIN": 0, "POSSIBLE_ONLY": 0, "NO_CAUSAL_PATH": 0}
    rows_any_nopath = 0
    rows_zero_certain = 0
    first_nopath_row = None
    per_row = []
    prev_occ = occ0
    t = t_m
    while t <= upto and t < T:
        if t > t_m:
            occ, nY = I2.grid_at(data, t)
            if not occ.any():
                break
            certain = occ & I2.dilate(certain) & ~I2.dilate(prev_occ & ~certain)
            possible = occ & I2.dilate(possible)
            prev_occ = occ
        else:
            nY = nY0
        cells = acells.get(t)
        if cells is not None and t <= interval_end_recorded:
            rows_in_interval += 1
            m_c = m_p = m_n = 0
            for (y, x) in cells:
                v = int(nY[y, x])
                if v == 0:
                    continue
                if certain[y, x]:
                    m_c += v
                elif possible[y, x]:
                    m_p += v
                else:
                    m_n += v
            exposure += m_c + m_p + m_n
            comp["CERTAIN"] += m_c
            comp["POSSIBLE_ONLY"] += m_p
            comp["NO_CAUSAL_PATH"] += m_n
            if m_n:
                rows_any_nopath += 1
                if first_nopath_row is None:
                    first_nopath_row = t
            if m_c == 0:
                rows_zero_certain += 1
            if m_n and len(per_row) < 8:
                per_row.append({"row": t, "A_cells": sorted(map(list, cells)),
                                "mass_CERTAIN": m_c, "mass_POSSIBLE_ONLY": m_p,
                                "mass_NO_CAUSAL_PATH": m_n})
        t += 1
    return {
        "A_RECONSTRUCTED": True,
        "A_end_reconstructed": a_end,
        "interval_end_recorded": interval_end_recorded,
        "E3_DURATION_recomputed": interval_end_recorded - t_m,
        "E3_EXPOSURE_recomputed": exposure,
        "n_rows_in_interval_recomputed": rows_in_interval,
        "COMPOSITION": comp,
        "rows_with_any_NO_CAUSAL_PATH_mass": rows_any_nopath,
        "rows_with_ZERO_CERTAIN_mass": rows_zero_certain,
        "first_row_with_NO_CAUSAL_PATH_mass": first_nopath_row,
        "EXAMPLE_ROWS": per_row,
    }


def main(out_path):
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    meas = {m["index"]: m for m in json.load(open(f"{REPO}/OMLDCT02/work/OMLDCT02_PAIR_MEASUREMENTS.json"))}
    done = json.load(open(out_path)) if os.path.exists(out_path) else {}
    for i in sorted(by):
        for arm in ("SELECTIVE", "SHAM"):
            key = f"{i}|{arm}"
            if key in done:
                continue
            r = by[i]
            rec = meas[i][arm]["A"]
            got = one_arm(r["ARCHIVES"][arm]["path"], r["t_m"],
                          r["FORK"]["locked_daughter_cells"], rec["interval_end"])
            got["index"] = i
            got["arm"] = arm
            got["t_m"] = r["t_m"]
            got["E3_DURATION_recorded"] = rec["E3_DURATION"]
            got["E3_EXPOSURE_recorded"] = rec["E3_EXPOSURE"]
            got["n_rows_in_interval_recorded"] = rec["n_rows_in_interval"]
            got["GATE0_DURATION_MATCHES"] = got.get("E3_DURATION_recomputed") == rec["E3_DURATION"]
            got["GATE0_EXPOSURE_MATCHES"] = got.get("E3_EXPOSURE_recomputed") == rec["E3_EXPOSURE"]
            got["GATE0_ROWS_MATCH"] = got.get("n_rows_in_interval_recomputed") == rec["n_rows_in_interval"]
            got["GATE0_PASS"] = bool(got["GATE0_DURATION_MATCHES"] and got["GATE0_EXPOSURE_MATCHES"]
                                     and got["GATE0_ROWS_MATCH"])
            done[key] = got
            tmp = out_path + ".part"
            with open(tmp, "w") as fh:
                json.dump(done, fh)
            os.replace(tmp, out_path)
            c = got.get("COMPOSITION", {})
            print(f"{key:>16}  gate0={'PASS' if got['GATE0_PASS'] else 'FAIL'}  "
                  f"exp {got.get('E3_EXPOSURE_recomputed')}/{rec['E3_EXPOSURE']}  "
                  f"C={c.get('CERTAIN')} P={c.get('POSSIBLE_ONLY')} N={c.get('NO_CAUSAL_PATH')}",
                  flush=True)
    print("done", len(done))


if __name__ == "__main__":
    main(sys.argv[1])
