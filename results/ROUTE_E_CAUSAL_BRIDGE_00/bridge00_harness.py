"""ROUTE_E_NONMERGING_CAUSAL_BRIDGE_DEV_00 -- paired law contrast, DEV only.

The requested Route E <-> NONMERGING_CONFIRM_02 swap is NOT executable: the two are
different substrates with disjoint state spaces (see bridge00_protocol.json,
PHASE_1_FINDING). This harness runs the executable substitute: the substrate and the
initial microstate are held bit-identical and only the LawSpec varies, drawn from the
frozen Route E law measure.

Production detector, tracker and residual are used unmodified.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import time
from pathlib import Path

import numpy as np

from edlab.substrates.lattice_bond.engine import LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec, run_measurement_bridge,
)
from edlab.substrates.lattice_bond.future_route_e_pre_run_frame import (
    propose_law_fields, in_proposal_box, engine_accepts,
)

FRAMES = (0, 16, 32, 64, 128, 256, 512, 1024)
SPEC = MeasurementSpec()
CONV = (0.01, 0.05, 0.20)
LAW_ROOT = hashlib.sha256(b"ROUTE_E_NONMERGING_CAUSAL_BRIDGE_DEV_00").digest()
LAW_INDICES = (15, 16, 19, 29, 35)


def law_arms() -> dict[str, LatticeBondSpec]:
    arms = {"BASELINE_SWEEP00": LatticeBondSpec(dt=1.0, m_max=1.0, n_max=1.0)}
    accepted = {name for name in LatticeBondSpec.__dataclass_fields__}
    for i in LAW_INDICES:
        f = propose_law_fields(LAW_ROOT, i)
        assert in_proposal_box(f), f"law {i} outside the frozen design box"
        ok, why = engine_accepts(f)
        assert ok, f"law {i} refused by the engine: {why}"
        arms[f"LAW_{i}"] = LatticeBondSpec(**{k: float(v) for k, v in f.items()
                                              if k in accepted})
    return arms


def initial_state(L: int, seed: int) -> LatticeBondState:
    """The FROZEN production initial condition. Identical bytes for a given (L, seed)."""
    m = np.random.default_rng(seed).random((L, L))
    return LatticeBondState(np.ascontiguousarray(m, dtype=np.float64),
                            np.full((L, L), 0.8, dtype=np.float64),
                            np.zeros((2, L, L), dtype=np.float64), 0)


def run_world(arm: str, law: LatticeBondSpec, L: int, seed: int) -> dict:
    state = initial_state(L, seed)
    row = {"arm": arm, "L": L, "seed": seed, "technical_failure": False, "error": ""}
    try:
        with tempfile.TemporaryDirectory() as d:
            rec = run_measurement_bridge(
                d, law_spec=law, initial_state=state, sampled_frames=FRAMES,
                measurement_spec=SPEC,
                acquisition_source_identity={"probe": "DEV_CAUSAL_BRIDGE_00", "arm": arm})
            frames = rec.frames
    except Exception as exc:                                  # kept in the denominator
        row.update(technical_failure=True, error=f"{type(exc).__name__}: {exc}"[:200])
        return row

    counts = [len(f.components) for f in frames]
    wrapped = [any(c.wraps_x or c.wraps_y for c in f.components) for f in frames]
    first_wrap = next((f.frame for f, w in zip(frames, wrapped) if w), None)
    first_empty = next((f.frame for f, c in zip(frames, counts) if c == 0), None)
    f0, fend = frames[0], frames[-1]
    labelled = f0.total_cohort / f0.total_matter if f0.total_matter > 0 else float("nan")
    end_bounded = [c for c in fend.components if not (c.wraps_x or c.wraps_y)]
    res_end = min((c.cohort_residual for c in end_bounded), default=float("nan"))

    survived = (first_wrap is None) and (first_empty is None) and bool(end_bounded)
    row.update({
        "component_count_by_frame": "|".join(str(c) for c in counts),
        "largest_over_L2_by_frame": "|".join(
            f"{(max((c.area for c in f.components), default=0) / (L * L)):.4f}" for f in frames),
        "first_wrapping_frame": first_wrap, "first_empty_frame": first_empty,
        "labelled_fraction": labelled,
        "component_count_end": counts[-1], "bounded_components_end": len(end_bounded),
        "min_bounded_residual_at_1024": res_end,
        "bounded_survival_to_1024": survived,
    })
    for f in CONV:
        row[f"PASS_at_{f}"] = bool(survived and res_end <= f)
    return row


# ------------------------------------------------------------- measurement controls
def measurement_controls() -> list[dict]:
    """Validate detection / wrapping / dissolution on the PRODUCTION detector."""
    from edlab.substrates.lattice_bond.instrumentation import DetectorSpec, detect_components
    det = DetectorSpec(matter_threshold=SPEC.matter_threshold, min_cells=SPEC.min_cells)
    L = 24
    out = []

    def state_from(mask_val: np.ndarray) -> LatticeBondState:
        return LatticeBondState(np.ascontiguousarray(mask_val, dtype=np.float64),
                                np.full((L, L), 0.8), np.zeros((2, L, L)), 0)

    # 1. persistent compact bounded non-wrapping component
    m = np.full((L, L), 0.1)
    yy, xx = np.mgrid[0:L, 0:L]
    m[((yy - 12) ** 2 + (xx - 12) ** 2) <= 9] = 0.9
    comps = detect_components(state_from(m), det, frame=0)
    out.append({"control": "compact_bounded_persistent", "n_components": len(comps),
                "any_wrapping": any(c.wraps_x or c.wraps_y for c in comps),
                "expected": "1 component, no wrapping",
                "PASS": len(comps) == 1 and not any(c.wraps_x or c.wraps_y for c in comps)})

    # 2. wrapping band
    m = np.full((L, L), 0.1)
    m[10:13, :] = 0.9
    comps = detect_components(state_from(m), det, frame=0)
    out.append({"control": "wrapping_band", "n_components": len(comps),
                "any_wrapping": any(c.wraps_x or c.wraps_y for c in comps),
                "expected": "wrapping detected",
                "PASS": any(c.wraps_x or c.wraps_y for c in comps)})

    # 3. a component that disappears
    m = np.full((L, L), 0.1)
    comps = detect_components(state_from(m), det, frame=0)
    out.append({"control": "dissolved_component", "n_components": len(comps),
                "any_wrapping": False, "expected": "0 components",
                "PASS": len(comps) == 0})
    return out


def main() -> None:
    arms = law_arms()
    sizes = [24, 32]
    seeds = list(range(910000, 910012))

    controls = measurement_controls()
    print("=== CONTROLES DE MESURE ===")
    for c in controls:
        print(f"  {c['control']:32s} n={c['n_components']} wrap={c['any_wrapping']} "
              f"-> {'PASS' if c['PASS'] else 'FAIL'}  ({c['expected']})")
    Path("bridge00_controls.json").write_text(json.dumps(controls, indent=1))
    if not all(c["PASS"] for c in controls):
        print("\nCONTROLES EN ECHEC -> PROBE_INVALID, arret avant tout monde moteur.")
        return

    Path("bridge00_laws.json").write_text(json.dumps(
        {k: {f: getattr(v, f) for f in LatticeBondSpec.__dataclass_fields__}
         for k, v in arms.items()}, indent=1))

    rows, t0 = [], time.time()
    for arm, law in arms.items():
        for L in sizes:
            for s in seeds:
                rows.append(run_world(arm, law, L, s + 1000 * sizes.index(L)))
        print(f"  {arm:18s} done ({len(rows)}/{len(arms)*len(sizes)*len(seeds)}, "
              f"{time.time()-t0:.0f}s)", flush=True)

    out = Path("bridge00_rows.csv")
    fields = sorted({k for r in rows for k in r})
    with out.open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\n{len(rows)} mondes -> {out} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
