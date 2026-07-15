"""Checkpoint-library builder (resumable). For each trajectory: warm up, then record checkpoints at
several ages. Stores accessible snapshot X, privileged hidden h, attractor coords, uptake, material, and
a COMPACT canonical full state (float32) sufficient to re-evolve for divergence tests.

Trajectory ID and privileged h are stored for ground-truth scoring only; they are never instrument inputs.
"""
from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np

from ..sc_hmc import harness as H
from ..sc_hmc.harness import SCState
from . import config as C
from . import core

OUT = os.environ.get("SC_HSI_OUT", "/tmp/sc_hsi")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)


class MonoTracer:
    n_spatial = 1; n_temporal = 0; tau_feed = 1
    @property
    def n_cohorts(self):
        return 1
    def active_feed_cohort(self, step):
        return 0


def mono_engine():
    from ..sc_hmc.harness import ScaffoldEngine
    return ScaffoldEngine(C.SPEC, MonoTracer())


def compact_state(st) -> dict:
    return {k: getattr(st, k).astype(np.float32) for k in ("rho", "U", "V", "c", "N", "uptake")} | {"step": int(st.step)}


def load_state(cs: dict) -> SCState:
    rho = cs["rho"].astype(np.float64)
    return SCState(rho, cs["U"].astype(np.float64), cs["V"].astype(np.float64),
                   cs["c"].astype(np.float64), cs["N"].astype(np.float64),
                   rho[None, :, :].copy(), cs["uptake"].astype(np.float64), int(cs["step"]))


def _load(p, d):
    return pickle.load(open(p, "rb")) if os.path.exists(p) else d


def _save(p, o):
    with open(p, "wb") as f:
        pickle.dump(o, f)


def build_trajectory(seed: int) -> dict:
    eng = mono_engine()
    st = H.warmup(seed)                      # frozen 2000-step warmup (uses frozen TRACER internally)
    # re-key onto mono cohort so we can re-evolve loaded states identically (C is passive)
    st.C = st.rho[None, :, :].copy()
    cur = st
    rec = {"seed": seed, "checkpoints": [], "canonical_state": None}
    prev_age = 0
    for age in C.CHECKPOINT_AGES:
        if age > prev_age:
            for _ in range(age - prev_age):
                cur = eng.step(cur)
            prev_age = age
        e = H.largest_entity(cur)
        if e is None:
            rec["checkpoints"].append({"age": age, "valid": False})
            continue
        cp = {"age": age, "valid": True,
              "X": core.snapshot_descriptor(cur, e), "h": core.hidden_descriptor(cur, e),
              "attr": core.attractor_coords(cur, e), "uptake": float(e.specific_uptake),
              "size": float(e.size), "rg": float(e.rg), "mass": float(e.mass),
              "mean_sig": float(e.mean_sig)}
        rec["checkpoints"].append(cp)
        if age == C.CANONICAL_AGE:
            rec["canonical_state"] = compact_state(cur)
    return rec


def run(split: str):
    t0 = time.time()
    seeds = {"dev": C.DEV_TRAJ, "prospective": C.PROSP_TRAJ}[split]
    p = f"{OUT}/lib_{split}.pkl"
    lib = _load(p, [])
    done = {r["seed"] for r in lib}
    for s in seeds:
        if s in done:
            continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET; {len(lib)}/{len(seeds)}; rerun", flush=True)
            return
        lib.append(build_trajectory(s))
        _save(p, lib)
    if len(lib) >= len(seeds):
        valid = sum(1 for r in lib if any(c.get("valid") for c in r["checkpoints"]))
        print(f"COMPLETE {split} {len(lib)}/{len(seeds)} ({valid} with entities)", flush=True)
    else:
        print(f"PROGRESS {len(lib)}/{len(seeds)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
