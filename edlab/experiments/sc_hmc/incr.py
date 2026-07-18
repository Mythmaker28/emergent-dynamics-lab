"""Resumable, budget-bounded runner (isolated shells can't hold background jobs).

Each invocation: (1) extends the cached unrelated pool, then (2) measures as many un-measured seeds as
fit in a wall budget, checkpointing after EVERY unit. Invoke repeatedly until it prints COMPLETE.

    python -m edlab.experiments.sc_hmc.incr <dev|prospective>
"""
from __future__ import annotations

import os
import pickle
import sys
import time

from . import config as C
from . import experiment as E
from . import harness as H

OUT = os.environ.get("SC_HMC_OUT", "/tmp/sc_hmc")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)


def _load(p, d):
    return pickle.load(open(p, "rb")) if os.path.exists(p) else d


def _save(p, o):
    with open(p, "wb") as f:
        pickle.dump(o, f)


def build_pool(t0) -> tuple[list, bool]:
    p = f"{OUT}/pool.pkl"
    pool = _load(p, [])
    done = {c["seed"] for c in pool}
    for s in C.UNRELATED_SEEDS:
        if s in done:
            continue
        if time.time() - t0 > BUDGET:
            return pool, False
        st = H.advance(H.pulse_chase_engine(), H.relabel_pulse_chase(H.warmup(s)), C.CHECKPOINT)
        e = H.largest_entity(st)
        entry = {"seed": s, "state": st, "size": float(e.size) if e else 0.0,
                 "rg": float(e.rg) if e else 0.0, "valid": e is not None}
        pool.append(entry)
        _save(p, pool)
        print(f"pool seed {s} valid={e is not None} ({len(pool)}/{len(C.UNRELATED_SEEDS)})", flush=True)
    ready = len([c for c in pool if c.get("valid")]) >= max(3, len(C.UNRELATED_SEEDS) - 3)
    return [c for c in pool if c.get("valid")], ready


def run(split: str) -> None:
    t0 = time.time()
    seeds = {"dev": C.DEV_SEEDS, "prospective": C.PROSPECTIVE_SEEDS}[split]
    pool, ready = build_pool(t0)
    if not ready:
        print(f"POOL_BUILDING {len(pool)} valid so far; rerun", flush=True)
        return
    rp = f"{OUT}/records_{split}.pkl"
    recs = _load(rp, [])
    done = {r["seed"] for r in recs}
    for s in seeds:
        if s in done:
            continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET hit; PROGRESS {len(recs)}/{len(seeds)}; rerun", flush=True)
            return
        r = E.measure_seed(s, pool)
        r["dist"] = E.summarize_distances(r)
        recs.append(r)
        _save(rp, recs)
        d = r.get("dist", {})
        print(f"seed {s} valid={r.get('valid')} M_tc={_r(r.get('M_tc'))} "
              f"d_H={_r(d.get('d_H'))} d_P={_r(d.get('d_P'))} d_M={_r(d.get('d_M'))} "
              f"d_U={_r(d.get('d_U'))} ceil={_r(d.get('clone_ceiling_mean'))} "
              f"({len(recs)}/{len(seeds)})", flush=True)
    if len(recs) >= len(seeds):
        print(f"COMPLETE {split} {len(recs)}/{len(seeds)}", flush=True)


def _r(x):
    return round(x, 4) if isinstance(x, float) else x


if __name__ == "__main__":
    run(sys.argv[1])
