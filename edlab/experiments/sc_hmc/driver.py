"""Batch driver: measure a split's seeds, serialize full records + a JSON distance summary.

Usage:  python -m edlab.experiments.sc_hmc.driver <dev|prospective>
Heavy; intended to run in the background (nohup) with progress to a log.
"""
from __future__ import annotations

import json
import os
import pickle
import sys
import time

import numpy as np

from . import config as C
from . import experiment as E

OUT = os.environ.get("SC_HMC_OUT", "results/sc_hmc")


def _to_native(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    return str(o)


def run(split: str, seeds: list) -> None:
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    print(f"[{split}] START seeds={list(seeds)} out={OUT}", flush=True)
    pool = E.build_unrelated_pool()
    print(f"[{split}] unrelated pool={len(pool)} built t={time.time()-t0:.0f}s", flush=True)
    recs = []
    for s in seeds:
        r = E.measure_seed(s, pool)
        r["dist"] = E.summarize_distances(r)
        recs.append(r)
        d = r.get("dist", {})
        print(f"[{split}] seed {s} valid={r.get('valid')} "
              f"M_tc={r.get('M_tc')!r} d_H={d.get('d_H')!r} d_P={d.get('d_P')!r} "
              f"d_M={d.get('d_M')!r} d_U={d.get('d_U')!r} t={time.time()-t0:.0f}s", flush=True)
    with open(f"results/sc_hmc/records_{split}.pkl", "wb") as f:
        pickle.dump(recs, f)
    summ = [{"seed": r.get("seed"), "valid": r.get("valid"),
             "M_early": r.get("M_early"), "M_tc": r.get("M_tc"),
             "dist": r.get("dist", {})} for r in recs]
    json.dump(summ, open(f"results/sc_hmc/summary_{split}.json", "w"), indent=2, default=_to_native)
    print(f"[{split}] DONE {len(recs)} seeds in {time.time()-t0:.0f}s