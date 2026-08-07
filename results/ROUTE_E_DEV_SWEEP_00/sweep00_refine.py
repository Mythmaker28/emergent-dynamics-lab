"""SINGLE authorised refinement pass.

Two corrections to the main sweep, both forced by its own differential check:
  1. PERSISTENCE. The frozen criterion requires a component observed continuously to
     the horizon. The main sweep's attainability counted residuals reached by
     components that then vanished (60/529 worlds with ncEnd == 0): a dissolution
     artefact, which the frozen predicate classifies as DISSOLVED_DETECTED_TRACK,
     an observed failure -- never a positive.
  2. HORIZON. Re-run the decisive levels at the FROZEN horizon 1024, removing the
     DEV horizon as a declared limitation exactly where it could change the sign.
"""

from __future__ import annotations

import csv
import math
import tempfile
import time
from pathlib import Path

import numpy as np

from edlab.substrates.lattice_bond.engine import LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec, run_measurement_bridge,
)
from sweep00_harness import ARMS, THRESHOLD, CONVENTIONS

HORIZON, CADENCE = 1024, 16
FRAMES = tuple(range(0, HORIZON + 1, CADENCE))
LAW = LatticeBondSpec(dt=1.0, m_max=1.0, n_max=1.0)
SPEC = MeasurementSpec()


def run_world(arm: str, L: int, p: float, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    m = np.ascontiguousarray(ARMS[arm](rng, L, p), dtype=np.float64)
    state = LatticeBondState(m, np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    with tempfile.TemporaryDirectory() as d:
        rec = run_measurement_bridge(
            d, law_spec=LAW, initial_state=state, sampled_frames=FRAMES,
            measurement_spec=SPEC,
            acquisition_source_identity={"probe": "ANTI_STAGNATION_DEV_REFINE_00",
                                         "arm": arm, "fixture": "DEV_FEASIBILITY"})
        frames = rec.frames

    f0, fend = frames[0], frames[-1]
    labelled = f0.total_cohort / f0.total_matter if f0.total_matter > 0 else float("nan")
    counts = [len(fr.components) for fr in frames]
    wrapped = [any(c.wraps_x or c.wraps_y for c in fr.components) for fr in frames]
    first_wrap = next((fr.frame for fr, w in zip(frames, wrapped) if w), None)
    ever_empty = any(c == 0 for c in counts)

    # bounded components alive AT the horizon
    end_bounded = [c for c in fend.components if not (c.wraps_x or c.wraps_y)]
    res_end = min((c.cohort_residual for c in end_bounded), default=float("nan"))

    # a persistent bounded population: at least one component at EVERY sampled frame,
    # never wrapping, and still present at the horizon
    persistent = (not ever_empty) and (first_wrap is None) and bool(end_bounded)

    row = {
        "arm": arm, "L": L, "target_occupancy": p, "seed": seed, "horizon": HORIZON,
        "realized_occupation_t0": float((m >= THRESHOLD).mean()),
        "component_count_t0": counts[0], "component_count_end": counts[-1],
        "min_component_count_any_frame": min(counts),
        "ever_empty": ever_empty,
        "wraps_anywhere": first_wrap is not None, "first_wrapping_frame": first_wrap,
        "labelled_fraction": labelled,
        "persistent_bounded_population": persistent,
        "residual_at_horizon_bounded": res_end,
    }
    for f in CONVENTIONS:
        row[f"PASS_at_{f}"] = bool(persistent and res_end <= f)
        row[f"floor_admits_{f}"] = bool(labelled <= f)
    return row


def main() -> None:
    grid = [0.056, 0.10, 0.20, 0.35]
    sizes = [16, 24, 32]
    seeds = list(range(900000, 900006))
    arms = ["ROUTE_E", "COMPACT_ISLANDS"]
    rows, t0 = [], time.time()
    for arm in arms:
        for p in grid:
            for L in sizes:
                for s in seeds:
                    rows.append(run_world(arm, L, p, s + 1000 * sizes.index(L)
                                          + 100000 * grid.index(p)))
            print(f"  {arm:16s} p={p:.3f} done ({len(rows)}, {time.time()-t0:.0f}s)", flush=True)
    out = Path("sweep00_refine_rows.csv")
    with out.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"\n{len(rows)} worlds -> {out} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
