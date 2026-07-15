"""Controlled causal-consequence + accessibility test, isolating the two parts of the internal state:
  - SCRAMBLE: permute U,V spatially (preserves mean sigma / attractor class; destroys spatial organization)
  - FLIP:     swap U<->V (flips sigma sign -> opposite attractor class; same rho/c/N)
Both hold the accessible snapshot's rho/c/N fixed. We measure accessible-axis future divergence vs the
exact-clone stochastic ceiling, WITHOUT and WITH a bounded nutrient probe (accessibility).

If FLIP >> ceiling but SCRAMBLE ~ ceiling: the internal state is causally consequential only as a generic
ATTRACTOR CLASS (mean sigma), while the finer hidden organization is epiphenomenal. Physics FROZEN.
"""
from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np

from . import config as C
from . import library as LIB
from ..sc_hmc import harness as H
from ..sc_hmc import arms as ARMS
from ..sc_hmc import interventions as INT
from ..sc_hmc.harness import NoisyForcingEngine

OUT = os.environ.get("SC_HSI_OUT", "/tmp/sc_hsi")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
PROBE = ("N", "add", 0.50, 15)   # bounded nutrient probe used for the accessibility arm


def _mono():
    return LIB.mono_engine()


def _noisy(seed, k):
    from .library import MonoTracer
    return NoisyForcingEngine(C.SPEC, MonoTracer(), np.random.default_rng(60000 + 101 * seed + k), C.CLONE_NOISE_SIGMA)


def _flip(st):
    out = st.copy(); out.U, out.V = st.V.copy(), st.U.copy(); return out


def _traj(eng, st, probe=None, horizon=None, cadence=None):
    horizon = C.DIV_HORIZON if horizon is None else horizon
    cadence = C.DIV_CADENCE if cadence is None else cadence
    cur = st.copy(); out = []
    field, op, amp, dur = probe if probe else (None, None, None, 0)
    for t in range(1, horizon + 1):
        if probe and t <= dur:
            cur = INT._perturb(cur, field, op, amp)
        cur = eng.step(cur)
        if t % cadence == 0:
            e = H.largest_entity(cur)
            out.append([e.size, e.rg, e.specific_uptake, e.mass] if e else [0, 0, 0, 0])
    return np.asarray(out, float)


def _D(a, b, scale):
    m = min(len(a), len(b))
    return float(np.linalg.norm(((a[:m] - b[:m]) / scale).ravel()) / np.sqrt(m)) if m else 0.0


def base_test(seed, state, scale) -> dict:
    A = LIB.load_state(state)
    eng = _mono()
    fA = _traj(eng, A)
    fA_p = _traj(eng, A, probe=PROBE)
    scr = ARMS.arm_M(A, seed); flp = _flip(A)
    out = {"seed": seed}
    # clone ceiling (no probe) and under probe
    cl, clp = [], []
    for k in range(C.N_CLONE_REALIZATIONS):
        cl.append(_D(fA, _traj(_noisy(seed, k), A), scale))
        clp.append(_D(fA_p, _traj(_noisy(seed, 100 + k), A, probe=PROBE), scale))
    out["D_clone"] = float(np.mean(cl)); out["D_clone_probe"] = float(np.mean(clp))
    out["D_scramble"] = _D(fA, _traj(eng, scr), scale)
    out["D_flip"] = _D(fA, _traj(eng, flp), scale)
    out["D_scramble_probe"] = _D(fA_p, _traj(eng, scr, probe=PROBE), scale)
    out["D_flip_probe"] = _D(fA_p, _traj(eng, flp, probe=PROBE), scale)
    return out


def run(split: str):
    t0 = time.time()
    lib = LIB._load(f"{OUT}/lib_{split}.pkl", None)
    dev = LIB._load(f"{OUT}/lib_dev.pkl", None)
    # feature scale from dev canonical
    rows = [[c["size"], c["rg"], c["uptake"], c["mass"]] for r in dev for c in r["checkpoints"]
            if c.get("valid") and c["age"] == C.CANONICAL_AGE]
    scale = np.array(rows).std(0) + 1e-9
    states = {r["seed"]: r["canonical_state"] for r in lib if r.get("canonical_state") is not None}
    seeds = list(states)[: (40 if split == "dev" else 32)]
    p = f"{OUT}/causal_{split}.pkl"
    done = LIB._load(p, [])
    dseen = {d["seed"] for d in done}
    for s in seeds:
        if s in dseen:
            continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET {len(done)}/{len(seeds)}; rerun", flush=True); return
        done.append(base_test(s, states[s], scale)); LIB._save(p, done)
    if len(done) >= len(seeds):
        print(f"COMPLETE {split} {len(done)}/{len(seeds)}", flush=True)
    else:
        print(f"PROGRESS {len(done)}/{len(seeds)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
