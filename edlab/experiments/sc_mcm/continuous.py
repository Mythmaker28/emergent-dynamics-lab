"""Continuous 2-D history decoding + response dimensionality + individuation. Histories vary DOSE (amp)
and ORDER (order_w) orthogonally. Memory is transplanted into a common body and read as a multi-axis
resting signature R; we decode both history dimensions from R (held-out), estimate response
dimensionality, and test individuation. Resumable."""
from __future__ import annotations

import os, pickle, sys, time
import numpy as np

from . import config as C
from . import harness as H
from .experiment import read_signature, transplant_mean

OUT = os.environ.get("SC_MCM_OUT", "/tmp/sc_mcm")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)


def gen_histories(split):
    rng = np.random.default_rng(700 if split == "dev" else 1400)
    lo_a, hi_a = C.CONT_AMP_RANGE
    return [(float(rng.uniform(lo_a, hi_a)), float(rng.uniform(*C.CONT_ORDER_RANGE))) for _ in range(C.N_CONT[split])]


def run(split="dev"):
    t0 = time.time()
    hists = gen_histories(split)
    seeds = C.CONT_SEEDS[split]
    p = f"{OUT}/cont_{split}.pkl"; done = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    seen = {(d["hist"], d["seed"]) for d in done}
    wp = f"{OUT}/warm_{split}.pkl"; warm = pickle.load(open(wp, "rb")) if os.path.exists(wp) else {}
    eng = H.mc_engine()
    # common reference body B0 (built once from the first seed's neutral history, erased)
    bp = f"{OUT}/B0_{split}.pkl"
    if os.path.exists(bp):
        B0 = pickle.load(open(bp, "rb"))
    else:
        s0 = seeds[0]
        if s0 not in warm:
            warm[s0] = H.warmup(s0); pickle.dump(warm, open(wp, "wb"))
        B0 = H.erase_memory(H.advance(eng, H.apply_history(eng, warm[s0], C.HISTORIES["H4"]), C.SETTLE))
        pickle.dump(B0, open(bp, "wb"))
    for seed in seeds:
        if seed not in warm:
            if time.time() - t0 > BUDGET:
                pickle.dump(warm, open(wp, "wb")); print(f"WARMING {len(warm)}", flush=True); return
            warm[seed] = H.warmup(seed); pickle.dump(warm, open(wp, "wb"))
    for hi, (amp, ow) in enumerate(hists):
        for seed in seeds:
            if (hi, seed) in seen: continue
            if time.time() - t0 > BUDGET:
                pickle.dump(done, open(p, "wb")); print(f"BUDGET {len(done)}/{C.N_CONT[split]*len(seeds)}; rerun", flush=True); return
            st = H.apply_cont_history(eng, warm[seed], amp, ow)
            e = H.largest(st)
            if e is None:
                done.append({"hist": hi, "seed": seed, "valid": False}); continue
            m = H.entity_memory(st, e)
            Rv = read_signature(eng, B0, m)
            done.append({"hist": hi, "seed": seed, "valid": True, "amp": amp, "order_w": ow,
                         "mem": m.tolist(), "pm": H.entity_pm(st, e).tolist(), "Rv": Rv.tolist()})
            pickle.dump(done, open(p, "wb"))
    print(f"COMPLETE {split} {len([d for d in done if d.get('valid')])} valid", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "dev")
