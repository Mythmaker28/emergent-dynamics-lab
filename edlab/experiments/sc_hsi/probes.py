"""Intervention informativeness search (Section 10). Over a bounded preregistered N/c grid, score each
probe by how well it exposes the causally-relevant hidden difference (sigma-FLIP) in ACCESSIBLE outputs,
relative to the exact-clone stochastic divergence, while not destroying the entity. Selection on DEV only.
"""
from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np

from . import config as C
from . import library as LIB
from . import causal as CA
from ..sc_hmc import harness as H

OUT = os.environ.get("SC_HSI_OUT", "/tmp/sc_hsi")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))


def score_state(seed, state, scale) -> dict:
    A = LIB.load_state(state)
    flp = CA._flip(A)
    eng = CA._mono()
    res = {"seed": seed}
    for name, field, op, amp, dur in C.PROBE_GRID:
        probe = (field, op, amp, dur)
        fA = CA._traj(eng, A, probe=probe, horizon=C.PROBE_HORIZON, cadence=C.PROBE_CADENCE)
        fF = CA._traj(eng, flp, probe=probe, horizon=C.PROBE_HORIZON, cadence=C.PROBE_CADENCE)
        cl = np.mean([CA._D(fA, CA._traj(CA._noisy(seed, 200 + k), A, probe=probe,
                     horizon=C.PROBE_HORIZON, cadence=C.PROBE_CADENCE), scale) for k in range(2)])
        e = H.largest_entity(A)
        alive = fA[-1][0] >= C.DET.min_cells if len(fA) else False
        res[name] = {"flip_div": CA._D(fA, fF, scale), "clone_div": float(cl),
                     "ratio": CA._D(fA, fF, scale) / (cl + 1e-9), "alive": bool(alive)}
    return res


def run(split="dev"):
    t0 = time.time()
    lib = LIB._load(f"{OUT}/lib_dev.pkl", None)
    rows = [[c["size"], c["rg"], c["uptake"], c["mass"]] for r in lib for c in r["checkpoints"]
            if c.get("valid") and c["age"] == C.CANONICAL_AGE]
    scale = np.array(rows).std(0) + 1e-9
    states = {r["seed"]: r["canonical_state"] for r in lib if r.get("canonical_state") is not None}
    seeds = list(states)[:12]
    p = f"{OUT}/probes_dev.pkl"
    done = LIB._load(p, [])
    seen = {d["seed"] for d in done}
    for s in seeds:
        if s in seen:
            continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET {len(done)}/{len(seeds)}; rerun", flush=True); return
        done.append(score_state(s, states[s], scale)); LIB._save(p, done)
    if len(done) >= len(seeds):
        # aggregate
        agg = {}
        for name, *_ in C.PROBE_GRID:
            r = np.array([d[name]["ratio"] for d in done])
            a = np.mean([d[name]["alive"] for d in done])
            agg[name] = {"median_ratio": float(np.median(r)), "alive_frac": float(a)}
        best = max(agg, key=lambda k: agg[k]["median_ratio"] if agg[k]["alive_frac"] >= 0.9 else -1)
        LIB._save(f"{OUT}/probes_agg.pkl", {"agg": agg, "best": best})
        print("PROBE informativeness (median flip/clone ratio, alive_frac):", flush=True)
        for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["median_ratio"]):
            print(f"  {k:10s} ratio={v['median_ratio']:.2f} alive={v['alive_frac']:.2f}", flush=True)
        print("SELECTED:", best, flush=True)
    else:
        print(f"PROGRESS {len(done)}/{len(seeds)}", flush=True)


if __name__ == "__main__":
    run()
