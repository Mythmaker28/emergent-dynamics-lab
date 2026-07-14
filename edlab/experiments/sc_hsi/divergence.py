"""Direct future-divergence test (the PRIMARY causal assay) + intervention accessibility.

For each matched pair (A,B) [snapshot-matched, hidden-different] we evolve states forward under identical
deterministic forcing and measure divergence in ACCESSIBLE axes (size, rg, uptake, mass). We compare:
  D_natural    A vs B                      (snapshot-matched, hidden-different aliasing pair)
  D_controlled A vs scramble(A)            (SAME rho/c/N, hidden U/V spatially scrambled -> isolates hidden state)
  D_clone      A vs noisy clones of A       (exact state, independent environmental noise -> stochastic ceiling)
  D_SA / D_DA  A vs same/different attractor unrelated state
Causal consequence requires D_controlled and D_natural to exceed the clone ceiling.
Accessibility: repeat under each bounded N/c probe and score hidden-discrimination vs clone divergence.
Resumable; heavy. Physics FROZEN.
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


def _states_by_seed(lib):
    return {r["seed"]: r["canonical_state"] for r in lib if r.get("canonical_state") is not None}


def _feat_scale(lib):
    rows = []
    for r in lib:
        cp = next((c for c in r["checkpoints"] if c.get("valid") and c["age"] == C.CANONICAL_AGE), None)
        if cp:
            rows.append([cp["size"], cp["rg"], cp["uptake"], cp["mass"]])
    a = np.array(rows)
    return a.std(0) + 1e-9


def accessible_traj(eng, st, horizon, cadence) -> np.ndarray:
    out = []
    cur = st.copy()
    for t in range(1, horizon + 1):
        cur = eng.step(cur)
        if t % cadence == 0:
            e = H.largest_entity(cur)
            out.append([e.size, e.rg, e.specific_uptake, e.mass] if e else [0, 0, 0, 0])
    return np.asarray(out, float)


def _D(a, b, scale):
    m = min(len(a), len(b))
    if m == 0:
        return 0.0
    return float(np.linalg.norm(((a[:m] - b[:m]) / scale).ravel()) / np.sqrt(m))


def mono():
    return LIB.mono_engine()


def noisy(seed, k):
    from .library import MonoTracer
    return NoisyForcingEngine(C.SPEC, MonoTracer(), np.random.default_rng(50000 + 101 * seed + k), C.CLONE_NOISE_SIGMA)


def pair_divergence(sa, sb, states, scale, attr_lookup, all_seeds) -> dict:
    if sa not in states or sb not in states:
        return {"valid": False}
    A = LIB.load_state(states[sa]); B = LIB.load_state(states[sb])
    eng = mono()
    fa = accessible_traj(eng, A, C.DIV_HORIZON, C.DIV_CADENCE)
    fb = accessible_traj(eng, B, C.DIV_HORIZON, C.DIV_CADENCE)
    # controlled hidden scramble of A (preserve rho/c/N; permute U,V within entity)
    A_scr = ARMS.arm_M(A, sa)
    fscr = accessible_traj(eng, A_scr, C.DIV_HORIZON, C.DIV_CADENCE)
    # clone ceiling: identical state under independent environmental noise
    dcl = []
    for k in range(C.N_CLONE_REALIZATIONS):
        fk = accessible_traj(noisy(sa, k), A, C.DIV_HORIZON, C.DIV_CADENCE)
        dcl.append(_D(fa, fk, scale))
    # same / different attractor unrelated
    la = attr_lookup.get(sa)
    sa_pool = [s for s in all_seeds if s != sa and attr_lookup.get(s) == la and s in states]
    da_pool = [s for s in all_seeds if attr_lookup.get(s) is not None and attr_lookup.get(s) != la and s in states]
    rng = np.random.default_rng(sa)
    D_SA = D_DA = None
    if sa_pool:
        so = states[rng.choice(sa_pool)]
        D_SA = _D(fa, accessible_traj(eng, LIB.load_state(so), C.DIV_HORIZON, C.DIV_CADENCE), scale)
    if da_pool:
        do = states[rng.choice(da_pool)]
        D_DA = _D(fa, accessible_traj(eng, LIB.load_state(do), C.DIV_HORIZON, C.DIV_CADENCE), scale)
    return {"valid": True, "seed_a": sa, "seed_b": sb,
            "D_natural": _D(fa, fb, scale), "D_controlled": _D(fa, fscr, scale),
            "D_clone": float(np.mean(dcl)), "D_clone_max": float(np.max(dcl)),
            "D_SA": D_SA, "D_DA": D_DA}


def run(split: str):
    t0 = time.time()
    lib = LIB._load(f"{OUT}/lib_dev.pkl", None)
    frozen = pickle.load(open(f"{OUT}/frozen_{split}.pkl", "rb"))
    tgt_lib = LIB._load(f"{OUT}/lib_{split}.pkl", None)
    states = _states_by_seed(tgt_lib) | _states_by_seed(lib)
    scale = _feat_scale(lib)
    # attractor labels for all seeds in target
    from . import core
    attr_lookup = {}
    for r in tgt_lib:
        cp = next((c for c in r["checkpoints"] if c.get("valid") and c["age"] == C.CANONICAL_AGE), None)
        if cp:
            attr_lookup[r["seed"]] = int(core.label_attractor(np.asarray(cp["attr"]), frozen["frozen"]["attr_model"])[0])
    all_seeds = list(attr_lookup)
    pairs = frozen["pairs"]["pairs"]
    p = f"{OUT}/div_{split}.pkl"
    done = LIB._load(p, [])
    dseen = {(d["seed_a"], d["seed_b"]) for d in done if d.get("valid")}
    for pr in pairs:
        key = (pr["seed_a"], pr["seed_b"])
        if key in dseen:
            continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET {len(done)}/{len(pairs)}; rerun", flush=True); return
        d = pair_divergence(pr["seed_a"], pr["seed_b"], states, scale, attr_lookup, all_seeds)
        d["x_dist"] = pr["x_dist"]; d["h_dist"] = pr["h_dist"]
        done.append(d); LIB._save(p, done)
    if len(done) >= len(pairs):
        print(f"COMPLETE {split} {len(done)}/{len(pairs)}", flush=True)
    else:
        print(f"PROGRESS {len(done)}/{len(pairs)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
