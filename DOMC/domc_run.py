"""DOMC runner. One independent founding block = one independent unit. Never pool components,
events, cells or time points as replicates.

Usage:  python3 domc_run.py <GEOM> <SPLIT> <hA> <hB> [ARMSET]
        GEOM   in {FAR, NEAR}
        SPLIT  in {DEV, PROSP}
        hA,hB  the sealed history pair, e.g. cc 00
        ARMSET in {FULL, GATE, NEAR}
"""
from __future__ import annotations
import sys, os, json, pickle, time
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import domc_core as K

SEEDS = {"DEV": tuple(range(34000, 34012)),      # 12 development founding blocks
         "PROSP": tuple(range(35000, 35012))}    # 12 held-out prospective founding blocks

ARMSETS = {
    # FULL: the confirmatory arm set.
    "FULL": [("AB", "NONE"), ("BA", "NONE"), ("AA", "NONE"),
             ("AB", "ERASE_A"), ("AB", "ERASE_B"), ("AB", "ERASE_SHAM"),
             ("AB", "CROSS"), ("AA", "CROSS"), ("AB", "CROSS_ROLL")],
    # GATE: the development arm set. ERASE_SHAM is dropped because fixture 6 proves it is a
    # bit-exact no-op, and CROSS_ROLL because it is a robustness variant; neither sets a gate.
    "GATE": [("AB", "NONE"), ("BA", "NONE"), ("AA", "NONE"),
             ("AB", "ERASE_A"), ("AB", "ERASE_B"), ("AB", "CROSS"), ("AA", "CROSS")],
    "NEAR": [("AB", "NONE"), ("BA", "NONE"), ("AA", "NONE"), ("AB", "CROSS")],
    # CONF: the confirmatory arm set. ERASE_SHAM is not run (fixture 6 proves it a bit-exact
    # no-op, so it would cost 12 trajectories for zero information); CROSS_ENV and its sham are
    # added because H_ENVIRONMENT is a preregistered rival and needs its own adjudicating arm.
    "CONF": [("AB", "NONE"), ("BA", "NONE"), ("AA", "NONE"),
             ("AB", "ERASE_A"), ("AB", "ERASE_B"),
             ("AB", "CROSS"), ("AA", "CROSS"), ("AB", "CROSS_ROLL"),
             ("AB", "CROSS_ENV"), ("AA", "CROSS_ENV")],
}
HA = HB = None      # set from argv; the sealed history pair


def assign(asg):
    return {"AB": (HA, HB), "BA": (HB, HA), "AA": (HA, HA)}[asg]


def block(seed, geom, armset):
    K.set_geometry(geom)
    eng = K.engine()
    pc = K.pc_engine()
    arms = ARMSETS[armset]
    out = {"seed": seed, "geometry": geom, "armset": armset, "pair": [HA, HB],
           "sites": {"A": K.SITE_A, "B": K.SITE_B}, "arms": {}}

    # --- founding, then the three settled prefixes (one per history assignment) --------------
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    pick, dst, ncomp = K.read_sites(f)
    out["founding"] = {"n_components": ncomp, "d_A": round(dst["A"], 3), "d_B": round(dst["B"], 3),
                       "PAIR_OK": bool(ncomp == 2 and pick["A"] is not None
                                       and pick["B"] is not None)}
    settled = {}
    for asg in sorted({a for a, _ in arms}):
        hA, hB = assign(asg)
        s = K.apply_dual_history(eng, f, hA, hB)
        settled[asg] = K.advance(eng, s, K.SETTLE)

    for asg, iv in arms:
        key = f"{asg}|{iv}"
        s0 = K.INTERVENTIONS[iv](settled[asg])
        p0, d0, n0 = K.read_sites(s0)
        R0 = K.response_at_sites(eng, s0)
        sc0 = K.scalars(s0)
        # --- material turnover on the frozen criterion, then the SAME readout again ---------
        stT = K.advance(pc, K.relabel(s0), K.T_TURN)
        pT, dT, nT = K.read_sites(stT)
        MT = K.turnover_M(stT)
        RT = K.response_at_sites(pc, stT)
        scT = K.scalars(stT)
        out["arms"][key] = {
            "assignment": asg, "intervention": iv,
            "t0": {"n_components": n0, "alive_A": p0["A"] is not None,
                   "alive_B": p0["B"] is not None,
                   "d_A": round(d0["A"], 3), "d_B": round(d0["B"], 3),
                   "R_A": R0["A"].tolist(), "R_B": R0["B"].tolist(),
                   "ctrl_A": R0["ctrl_A"].tolist(), "ctrl_B": R0["ctrl_B"].tolist(),
                   "scalars": sc0,
                   "sum_Mf": float(s0.Mf.sum())},
            "turn": {"n_components": nT, "alive_A": pT["A"] is not None,
                     "alive_B": pT["B"] is not None,
                     "d_A": round(dT["A"], 3), "d_B": round(dT["B"], 3),
                     "M_A": MT["A"], "M_B": MT["B"],
                     "R_A": RT["A"].tolist(), "R_B": RT["B"].tolist(),
                     "ctrl_A": RT["ctrl_A"].tolist(), "ctrl_B": RT["ctrl_B"].tolist(),
                     "scalars": scT}}
    return out


def main(geom, split, armset):
    seeds = SEEDS[split]
    p = f"domc_{geom}_{split}_{HA}-{HB}.pkl"
    done = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    seen = {d["seed"] for d in done}
    t0 = time.time()
    for s in seeds:
        if s in seen:
            continue
        r = block(s, geom, armset)
        done.append(r)
        pickle.dump(done, open(p, "wb"))
        alive = sum(1 for k, v in r["arms"].items()
                    if v["turn"]["alive_A"] and v["turn"]["alive_B"])
        print(f"{geom}/{split} block {s}: pair_ok={r['founding']['PAIR_OK']} "
              f"arms_with_both_alive_after_turnover={alive}/{len(r['arms'])} "
              f"[{time.time()-t0:.0f}s]", flush=True)
    n_traj = len(done) * len(ARMSETS[armset])
    print(f"COMPLETE {geom}/{split}: {len(done)} blocks, {n_traj} trajectories, "
          f"{time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    HA, HB = sys.argv[3], sys.argv[4]
    main(sys.argv[1], sys.argv[2], sys.argv[5] if len(sys.argv) > 5 else "FULL")
