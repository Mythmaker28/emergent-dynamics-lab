"""ROUTE_E_LAW16_OCCUPANCY_FRONTIER_PAIRED_DEV_01 -- paired DEV experiment.

72 unique initial blocks, each hashed field by field and deep-copied twice, run under
BASELINE_SWEEP00 and LAW_16. Production detector / tracker gate terms / residual are used
unmodified. No production file is changed.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np

from edlab.substrates.lattice_bond.engine import LatticeBondSpec, LatticeBondState
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec, run_measurement_bridge,
)
from edlab.substrates.lattice_bond.instrumentation import DetectorSpec, detect_components
from sweep00_harness import ic_route_e
from bridge00_harness import law_arms

SPEC = MeasurementSpec()
CADENCE = 16
PRIMARY_H = 2048
TRANSIENT_H = 1024
FRAMES = tuple(range(0, PRIMARY_H + 1, CADENCE))
REPORT_H = (0, 16, 32, 64, 128, 256, 512, 1024, 2048)
OCCUPANCIES = (0.35, 0.45, 0.55)
SIZES = (24, 32)
ARMS = ("BASELINE_SWEEP00", "LAW_16")
CONV = (0.01, 0.05, 0.20)


def seed_for(pi: int, li: int, k: int) -> int:
    """72 disjoint DEV seeds, DEV_LAW16_OCCUPANCY_FRONTIER_01, never reused across cells."""
    return 920000 + pi * 1000 + li * 100 + k


def field_hashes(state: LatticeBondState) -> dict:
    out = {}
    for name in ("m", "n", "b"):
        a = getattr(state, name)
        out[name] = {
            "sha256": hashlib.sha256(a.tobytes(order="C")).hexdigest(),
            "dtype": str(a.dtype), "shape": list(a.shape),
            "c_contiguous": bool(a.flags["C_CONTIGUOUS"]),
            "sum": float(a.sum()),
        }
    out["step"] = int(state.step)
    payload = json.dumps(out, sort_keys=True).encode()
    out["microstate_sha256"] = hashlib.sha256(payload).hexdigest()
    return out


def make_block(L: int, p: float, seed: int) -> tuple[LatticeBondState, dict]:
    m = np.ascontiguousarray(ic_route_e(np.random.default_rng(seed), L, p), dtype=np.float64)
    st = LatticeBondState(m, np.full((L, L), 0.8, dtype=np.float64),
                          np.zeros((2, L, L), dtype=np.float64), 0)
    return st, field_hashes(st)


def initial_gate(state: LatticeBondState) -> tuple[str, int]:
    det = DetectorSpec(matter_threshold=SPEC.matter_threshold, min_cells=SPEC.min_cells)
    comps = detect_components(state, det, frame=0)
    if any(c.wraps_x or c.wraps_y for c in comps):
        return "INITIAL_WRAPPING", len(comps)
    if not comps:
        return "NO_NONTRIVIAL_BOUNDED_COMPONENT", 0
    return "INITIAL_GATE_PASS", len(comps)


def _largest_bounded(frame):
    """FROZEN tracked-component rule, inscribed before the run: the largest bounded
    non-wrapping component; ties broken by (-area, centroid_y, centroid_x, index)."""
    cand = [c for c in frame.components if not (c.wraps_x or c.wraps_y)]
    if not cand:
        return None
    return sorted(cand, key=lambda c: (-c.area, c.centroid_y, c.centroid_x, c.index))[0]


def run_arm(arm: str, law: LatticeBondSpec, state: LatticeBondState, L: int) -> dict:
    with tempfile.TemporaryDirectory() as d:
        rec = run_measurement_bridge(
            d, law_spec=law, initial_state=state, sampled_frames=FRAMES,
            measurement_spec=SPEC,
            acquisition_source_identity={"probe": "DEV_LAW16_OCCUPANCY_FRONTIER_01", "arm": arm})
        frames = rec.frames

    counts = [len(f.components) for f in frames]
    wrapped_at = [f.frame for f in frames if any(c.wraps_x or c.wraps_y for c in f.components)]
    empty_at = [f.frame for f in frames if len(f.components) == 0]
    f0 = frames[0]
    labelled = f0.total_cohort / f0.total_matter if f0.total_matter > 0 else float("nan")
    initial_wrapping = bool(wrapped_at and wrapped_at[0] == 0)

    # dynamic wrapping = wrapping that was NOT already present at t0
    dyn_wrap = next((t for t in wrapped_at if t > 0), None)
    t_wrap = "NA_INITIAL_GATE_FAIL" if initial_wrapping else dyn_wrap
    t_diss = empty_at[0] if empty_at else None

    # track continuity under the FROZEN tracker gate terms, applied at cadence 16
    t_trackloss = None
    prev = None
    for f in frames:
        cur = _largest_bounded(f)
        if cur is None:
            t_trackloss = f.frame
            break
        if prev is not None:
            disp = math.hypot(cur.centroid_y - prev.centroid_y, cur.centroid_x - prev.centroid_x)
            ratio = (cur.area / prev.area) if prev.area else float("inf")
            if disp > SPEC.max_centroid_displacement or not (
                    1.0 / SPEC.max_area_ratio <= ratio <= SPEC.max_area_ratio):
                t_trackloss = f.frame
                break
        prev = cur

    terminal = [(t, k) for t, k in (
        (dyn_wrap, "DYNAMIC_WRAPPING"), (t_diss, "DISSOLUTION"), (t_trackloss, "TRACK_LOSS"))
        if t is not None]
    if initial_wrapping:
        first_fail, fail_type = 0, "INITIAL_GATE_FAIL"
    elif terminal:
        first = min(t for t, _ in terminal)
        kinds = sorted(k for t, k in terminal if t == first)
        first_fail = first
        fail_type = kinds[0] if len(kinds) == 1 else "SIMULTANEOUS:" + "+".join(kinds)
    else:
        first_fail, fail_type = None, "NONE"

    def alive_at(H):
        idx = FRAMES.index(H)
        sub = frames[: idx + 1]
        if any(any(c.wraps_x or c.wraps_y for c in f.components) for f in sub):
            return False
        if any(len(f.components) == 0 for f in sub):
            return False
        if t_trackloss is not None and t_trackloss <= H:
            return False
        return _largest_bounded(frames[idx]) is not None

    end = frames[FRAMES.index(PRIMARY_H)]
    end_b = _largest_bounded(end)
    res_end = end_b.cohort_residual if end_b is not None else float("nan")
    row = {
        "arm": arm, "L": L,
        "initial_wrapping": initial_wrapping,
        "ever_wrapped": bool(wrapped_at), "ever_empty": bool(empty_at),
        "time_to_first_dynamic_wrapping": t_wrap,
        "time_to_complete_dissolution": t_diss,
        "time_to_track_loss": t_trackloss,
        "time_to_first_terminal_failure": first_fail,
        "first_failure_type": fail_type,
        "labelled_fraction": labelled,
        "component_count_over_time": "|".join(str(c) for c in counts[:: (len(FRAMES) // 8)]),
        "largest_component_fraction_end": (end_b.area / (L * L)) if end_b else 0.0,
        "tracked_component_lifetime": (first_fail if first_fail is not None else PRIMARY_H),
        "residual_at_2048": res_end,
    }
    for H in (256, TRANSIENT_H, PRIMARY_H):
        row[f"survival_at_{H}"] = alive_at(H)
    for f in CONV:
        row[f"PASS_at_{f}"] = bool(row[f"survival_at_{PRIMARY_H}"] and res_end <= f)
    return row


def measurement_controls() -> list[dict]:
    det = DetectorSpec(matter_threshold=SPEC.matter_threshold, min_cells=SPEC.min_cells)
    L = 24
    def stt(m):
        return LatticeBondState(np.ascontiguousarray(m, dtype=np.float64),
                                np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    yy, xx = np.mgrid[0:L, 0:L]
    out = []
    m = np.full((L, L), 0.1); m[((yy - 12) ** 2 + (xx - 12) ** 2) <= 9] = 0.9
    c = detect_components(stt(m), det, frame=0)
    out.append({"fixture": "compact_bounded_series", "observed": "BOUNDED_PERSISTENT"
                if (len(c) == 1 and not any(x.wraps_x or x.wraps_y for x in c)) else "OTHER",
                "expected": "BOUNDED_PERSISTENT"})
    m = np.full((L, L), 0.1); m[10:13, :] = 0.9
    c = detect_components(stt(m), det, frame=0)
    out.append({"fixture": "wrapping_band", "observed": "WRAPPING"
                if any(x.wraps_x or x.wraps_y for x in c) else "OTHER", "expected": "WRAPPING"})
    c = detect_components(stt(np.full((L, L), 0.1)), det, frame=0)
    out.append({"fixture": "dissolved_series", "observed": "DISSOLVED" if not c else "OTHER",
                "expected": "DISSOLVED"})
    for o in out:
        o["PASS"] = o["observed"] == o["expected"]
    return out


def main() -> None:
    controls = measurement_controls()
    print("=== CONTROLES DE MESURE ===")
    for c in controls:
        print(f"  {c['fixture']:26s} {c['observed']:20s} -> {'PASS' if c['PASS'] else 'FAIL'}")
    Path("law16_frontier_controls.json").write_text(json.dumps(controls, indent=1))
    if not all(c["PASS"] for c in controls):
        print("PROBE_INVALID — aucune trajectoire moteur lancee."); return

    arms = law_arms()
    laws = {"BASELINE_SWEEP00": arms["BASELINE_SWEEP00"], "LAW_16": arms["LAW_16"]}
    rows, blocks, t0 = [], [], time.time()

    for pi, p in enumerate(OCCUPANCIES):
        for li, L in enumerate(SIZES):
            for k in range(12):
                seed = seed_for(pi, li, k)
                state, hashes = make_block(L, p, seed)
                gate, ncomp = initial_gate(state)
                occ = float((state.m >= SPEC.matter_threshold).mean())
                blocks.append({"target_occupancy": p, "L": L, "seed": seed,
                               "realized_initial_occupancy": occ, "initial_gate": gate,
                               "n_components_t0": ncomp, **hashes})
                copies = {a: copy.deepcopy(state) for a in ARMS}
                # exact field-by-field equality BEFORE the first step
                ok = all(np.array_equal(getattr(copies[ARMS[0]], f), getattr(copies[ARMS[1]], f))
                         for f in ("m", "n", "b"))
                assert ok, f"pairing broken at {(p, L, seed)}"
                assert field_hashes(copies[ARMS[0]]) == field_hashes(copies[ARMS[1]]) == hashes
                for a in ARMS:
                    r = run_arm(a, laws[a], copies[a], L)
                    r.update(target_occupancy=p, seed=seed, initial_gate=gate,
                             realized_initial_occupancy=occ,
                             initial_microstate_sha256=hashes["microstate_sha256"],
                             n_components_t0=ncomp)
                    rows.append(r)
            print(f"  p={p:.2f} L={L} done ({len(rows)}/144, {time.time()-t0:.0f}s)", flush=True)

    Path("law16_frontier_blocks.json").write_text(json.dumps(blocks, indent=1))
    fields = sorted({k for r in rows for k in r})
    with Path("law16_frontier_rows.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\n{len(rows)} trajectoires / {len(blocks)} blocs -> law16_frontier_rows.csv "
          f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
