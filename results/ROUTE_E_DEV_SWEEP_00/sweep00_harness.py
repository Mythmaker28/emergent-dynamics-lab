"""ANTI_STAGNATION_ROUTE_E_FEASIBILITY_SWEEP_00 -- DEV feasibility harness.

Drives the PRODUCTION measurement bridge (detector, tracker, cohort_residual all
unmodified) over a single occupancy control parameter and four morphological arms.
No production file is modified. No primary/reproduction seed is opened.
"""

from __future__ import annotations

import csv
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np

from edlab.substrates.lattice_bond.engine import LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec,
    run_measurement_bridge,
)

THRESHOLD = 0.45
CONVENTIONS = (0.01, 0.05, 0.20)
HORIZON = 256
CADENCE = 16
LAW = LatticeBondSpec(dt=1.0, m_max=1.0, n_max=1.0)
SPEC = MeasurementSpec()
FRAMES = tuple(range(0, HORIZON + 1, CADENCE))


# ---------------------------------------------------------------- initial conditions
def ic_route_e(rng: np.random.Generator, L: int, p: float) -> np.ndarray:
    """Monotone quantile map of U(0,1). At p=0.55 this is the IDENTITY, i.e. the
    frozen production initial condition m ~ U(0,1) bit-for-bit."""
    u = rng.random((L, L))
    if abs(p - (1.0 - THRESHOLD)) < 1e-12:
        return u  # EXACTLY the frozen production initial condition m ~ U(0,1)
    m = np.empty_like(u)
    lo_frac = 1.0 - p
    hi_frac = p
    # snap so that p = 1 - THRESHOLD reproduces the production IC BIT-IDENTICALLY
    if abs(lo_frac - THRESHOLD) < 1e-12:
        lo_frac, hi_frac = THRESHOLD, 1.0 - THRESHOLD
    lo = u < lo_frac
    m[lo] = THRESHOLD * u[lo] / lo_frac
    m[~lo] = THRESHOLD + (1.0 - THRESHOLD) * (u[~lo] - lo_frac) / hi_frac
    return m


def ic_shuffled(rng: np.random.Generator, L: int, p: float) -> np.ndarray:
    m = ic_route_e(rng, L, p).reshape(-1)
    rng.shuffle(m)
    return m.reshape((L, L))


def _background(rng: np.random.Generator, L: int) -> np.ndarray:
    """Sub-threshold reservoir, uniform on [0, THRESHOLD)."""
    return rng.random((L, L)) * THRESHOLD * 0.999999


def ic_compact_islands(rng: np.random.Generator, L: int, p: float) -> np.ndarray:
    """Positive control: disjoint compact discs above threshold, equal occupancy."""
    m = _background(rng, L)
    target = int(round(p * L * L))
    if target < 1:
        return m
    # island radius chosen so that a handful of well separated discs reach `target`
    n_islands = max(1, min(6, target // 9))
    per = max(3, target // n_islands)
    radius = max(1.0, math.sqrt(per / math.pi))
    yy, xx = np.mgrid[0:L, 0:L]
    placed = np.zeros((L, L), dtype=bool)
    centres: list[tuple[float, float]] = []
    tries = 0
    while len(centres) < n_islands and tries < 400:
        tries += 1
        cy, cx = rng.random() * L, rng.random() * L
        # keep discs apart and away from the border so nothing wraps
        if not (radius + 1.5 <= cy <= L - radius - 1.5):
            continue
        if not (radius + 1.5 <= cx <= L - radius - 1.5):
            continue
        if any(math.hypot(cy - y, cx - x) < 2 * radius + 2.0 for y, x in centres):
            continue
        centres.append((cy, cx))
        placed |= ((yy - cy) ** 2 + (xx - cx) ** 2) <= radius ** 2
    # trim / grow to the exact cardinality
    idx = np.flatnonzero(placed.reshape(-1))
    if idx.size > target:
        idx = idx[:target]
    m = m.reshape(-1)
    m[idx] = THRESHOLD + (1.0 - THRESHOLD) * (0.4 + 0.6 * rng.random(idx.size))
    return m.reshape((L, L))


def ic_spanning_band(rng: np.random.Generator, L: int, p: float) -> np.ndarray:
    """Negative morphological control: one band spanning the lattice, equal occupancy."""
    m = _background(rng, L)
    target = int(round(p * L * L))
    width = max(1, int(round(target / L)))
    start = int(rng.integers(0, L))
    rows = [(start + k) % L for k in range(width)]
    flat = m.reshape(-1)
    cells = []
    for r in rows:
        cells.extend(range(r * L, r * L + L))
    cells = cells[:target]
    flat[cells] = THRESHOLD + (1.0 - THRESHOLD) * (0.4 + 0.6 * rng.random(len(cells)))
    return flat.reshape((L, L))


ARMS = {
    "ROUTE_E": ic_route_e,
    "SHUFFLED": ic_shuffled,
    "COMPACT_ISLANDS": ic_compact_islands,
    "SPANNING_BAND": ic_spanning_band,
}


# ---------------------------------------------------------------- one world
def run_world(arm: str, L: int, p: float, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    m = np.ascontiguousarray(ARMS[arm](rng, L, p), dtype=np.float64)
    state = LatticeBondState(
        m, np.full((L, L), 0.8, dtype=np.float64),
        np.zeros((2, L, L), dtype=np.float64), 0,
    )
    occ0 = float((m >= THRESHOLD).mean())
    with tempfile.TemporaryDirectory() as directory:
        record = run_measurement_bridge(
            directory, law_spec=LAW, initial_state=state, sampled_frames=FRAMES,
            measurement_spec=SPEC,
            acquisition_source_identity={"probe": "ANTI_STAGNATION_DEV_SWEEP_00",
                                         "arm": arm, "fixture": "DEV_FEASIBILITY"},
        )
        frames = record.frames

    f0, fend = frames[0], frames[-1]
    labelled = f0.total_cohort / f0.total_matter if f0.total_matter > 0 else float("nan")
    areas0 = [c.area for c in f0.components] or [0]
    occupied0 = max(1, int(round(occ0 * L * L)))

    wraps_t0 = any(c.wraps_x or c.wraps_y for c in f0.components)
    first_wrap = None
    min_res_any = float("inf")
    min_res_bounded = float("inf")  # over NON-wrapping components only
    for fr in frames:
        if first_wrap is None and any(c.wraps_x or c.wraps_y for c in fr.components):
            first_wrap = fr.frame
        for c in fr.components:
            if math.isfinite(c.cohort_residual):
                min_res_any = min(min_res_any, c.cohort_residual)
                if not (c.wraps_x or c.wraps_y):
                    min_res_bounded = min(min_res_bounded, c.cohort_residual)
    min_res_end = min((c.cohort_residual for c in fend.components), default=float("nan"))

    # occupancy actually realised at the horizon, recomputed from component areas
    occ_end = sum(c.area for c in fend.components) / (L * L)

    ineligible = first_wrap is not None
    reason = "WRAPPING_COMPONENT_PRESENT" if ineligible else (
        "NO_COMPONENT" if not f0.components else "NONE")

    row = {
        "arm": arm, "L": L, "target_occupancy": p, "seed": seed,
        "realized_occupation_t0": occ0,
        "realized_occupation_end": occ_end,
        "component_count_t0": len(f0.components),
        "component_count_end": len(fend.components),
        "largest_component_over_L2": max(areas0) / (L * L),
        "largest_component_over_occupied": max(areas0) / occupied0,
        "wraps_at_t0": wraps_t0,
        "wraps_anywhere": ineligible,
        "first_wrapping_frame": first_wrap,
        "labelled_fraction": labelled,
        "total_matter_t0": f0.total_matter,
        "total_cohort_t0": f0.total_cohort,
        "min_cohort_residual_any": None if min_res_any == float("inf") else min_res_any,
        "min_cohort_residual_bounded": None if min_res_bounded == float("inf") else min_res_bounded,
        "min_cohort_residual_at_horizon": min_res_end,
        "mechanically_ineligible": ineligible,
        "ineligibility_reason": reason,
    }
    for f in CONVENTIONS:
        # UPPER bound on attainability: best residual any component ever reaches,
        # restricted to bounded (non-wrapping) components, and the world must not be
        # mechanically ineligible.
        row[f"attainable_at_{f}"] = bool(
            (not ineligible) and min_res_bounded <= f
        )
        row[f"residual_floor_admits_{f}"] = bool(labelled <= f)
    return row


# ---------------------------------------------------------------- sweep
def main() -> None:
    grid = [0.03, 0.056, 0.10, 0.20, 0.35, 0.45, 0.55, 0.60]
    sizes = [16, 24, 32]
    seeds_main = list(range(900000, 900012))   # 12 DEV seeds for ROUTE_E
    seeds_ctrl = list(range(900000, 900006))   # 6 DEV seeds for each control arm
    rows: list[dict] = []
    started = time.time()
    total = sum(len(grid) * len(sizes) * len(seeds_main if a == "ROUTE_E" else seeds_ctrl)
                for a in ARMS)
    done = 0
    for arm in ARMS:
        seeds = seeds_main if arm == "ROUTE_E" else seeds_ctrl
        for p in grid:
            for L in sizes:
                for s in seeds:
                    seed = s + 1000 * sizes.index(L) + 100000 * grid.index(p)
                    rows.append(run_world(arm, L, p, seed))
                    done += 1
        print(f"  {arm:16s} done  ({done}/{total}, {time.time()-started:.0f}s)", flush=True)

    out = Path("sweep00_rows.csv")
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} worlds -> {out}  ({time.time()-started:.0f}s total)")
    Path("sweep00_meta.json").write_text(json.dumps({
        "worlds": len(rows), "wall_clock_seconds": time.time() - started,
        "grid": grid, "sizes": sizes, "seeds_per_level": len(seeds),
        "horizon": HORIZON, "cadence": CADENCE, "conventions": list(CONVENTIONS),
    }, indent=1))


if __name__ == "__main__":
    main()
