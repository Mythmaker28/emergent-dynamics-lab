"""Continuous-history manifold + individuation. Sectored histories (4 spatial quadrants get independent
nutrient-boost amplitudes) can write a high-cardinality SPATIAL memory pattern. We test whether that
memory (a) occupies a continuous/high-dim manifold beyond the 4 generic attractor classes, (b) individuates
trajectories (same history closer than different history), and (c) is decodable from CAUSAL response.
Warmups are cached per base seed. Resumable. Physics: frozen base + memory extension."""
from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np

from . import config as C
from . import harness as H
from .experiment import probe_response, erase_memory, _D, SCALE

OUT = os.environ.get("SC_IOM_OUT", "/tmp/sc_iom")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)
N_HIST = {"dev": 12, "prospective": 8}
SEEDS = {"dev": (30100, 30101, 30102, 30103), "prospective": (31100, 31101, 31102, 31103)}
HIST_STEPS = 200


def _quadrant_masks(n):
    ys = np.arange(n)[:, None] * np.ones((1, n)); xs = np.ones((n, 1)) * np.arange(n)[None, :]
    top = ys < n / 2; left = xs < n / 2
    return [top & left, top & ~left, ~top & left, ~top & ~left]


def sector_history(eng, st, amps, masks) -> "H.IOMState":
    cur = st.copy()
    for _ in range(HIST_STEPS):
        boost = np.zeros_like(cur.N)
        for q in range(4):
            boost += amps[q] * masks[q]
        cur.N = cur.N + boost
        cur = eng.step(cur)
    return H.advance(eng, cur, C.SETTLE)


def gen_histories(split):
    rng = np.random.default_rng(2024 if split == "dev" else 4048)
    lo, hi = 0.0, 0.10
    return [rng.uniform(lo, hi, size=4) for _ in range(N_HIST[split])]


def run(split="dev"):
    t0 = time.time()
    masks = _quadrant_masks(C.SPEC.size)
    hists = gen_histories(split)
    p = f"{OUT}/cont_{split}.pkl"
    done = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    seen = {(d["hist"], d["seed"]) for d in done}
    # cache warmups
    wp = f"{OUT}/warm_{split}.pkl"
    warm = pickle.load(open(wp, "rb")) if os.path.exists(wp) else {}
    eng = H.mem_engine()
    for si, seed in enumerate(SEEDS[split]):
        if seed not in warm:
            if time.time() - t0 > BUDGET:
                pickle.dump(warm, open(wp, "wb")); print(f"WARMING {len(warm)}/{len(SEEDS[split])}", flush=True); return
            warm[seed] = H.warmup(seed)
            pickle.dump(warm, open(wp, "wb"))
    for hi, amps in enumerate(hists):
        for seed in SEEDS[split]:
            if (hi, seed) in seen:
                continue
            if time.time() - t0 > BUDGET:
                pickle.dump(done, open(p, "wb")); print(f"BUDGET {len(done)}/{N_HIST[split]*len(SEEDS[split])}; rerun", flush=True); return
            st = sector_history(eng, warm[seed], amps, masks)
            e = H.largest(st)
            if e is None:
                done.append({"hist": hi, "seed": seed, "valid": False}); continue
            mf = H.entity_memory_field(st, e, grid=4)
            resp = probe_response(eng, st)
            resp_era = probe_response(eng, erase_memory(st))
            done.append({"hist": hi, "seed": seed, "valid": True, "amps": amps.tolist(),
                         "mem_field": mf.tolist(), "mem_mean": H.entity_memory(st, e).tolist(),
                         "resp": resp.tolist(), "mem_effect": _D(resp, resp_era)})
            pickle.dump(done, open(p, "wb"))
    print(f"COMPLETE {split} {len([d for d in done if d.get('valid')])} valid", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "dev")
