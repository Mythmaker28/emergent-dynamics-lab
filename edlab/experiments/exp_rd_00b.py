"""EXP-RD-00B: temporal-feed-cohort (pulse-chase) tracer qualification.

A single permanent FEED cohort SATURATES: once feed-origin mass dominates a structure its cohort composition stops
changing, so CONTINUED turnover becomes invisible. Rotating TEMPORAL feed cohorts label fed material by WHEN it
entered, so continued replacement keeps shifting the composition and M(tau) keeps registering turnover.

Two controls (pre-declared):
  C1 CONTINUOUS THROUGHPUT: open Gray-Scott throughout -> the structure keeps replacing its material ->
     the tracer MUST keep reporting turnover in the LATE window (median late M < 0.5, the frozen probe threshold).
  C2 ONE-TIME REPLACEMENT THEN NO FURTHER TURNOVER: open for a phase (external material replaces the original),
     then switch to the EXACT CLOSED limit (F=k=0: no feed, no removal) -> no further external replacement ->
     the tracer MUST report (near-)no continued turnover in the LATE window.
Discrimination = median_late_M(C2) - median_late_M(C1) > MARGIN.

Temporal resolution is selected ONLY by this measurement-discrimination criterion -- never by candidate yield or
target-quadrant occupancy.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.reaction_diffusion.engine import GrayScottSpec, RDEngine, TracerSpec
from ..substrates.reaction_diffusion.observables import (
    RDDetectionSpec, RDPhenotypeSpec, detect_rd_entities, to_entity_observation, rd_material_retention,
)
from .exp_rd_00 import rd_state as _rd_state_base, rates
from .exp_fl_00 import _cohort_grid

OPEN = GrayScottSpec(size=64, F=0.025, k=0.055)
CLOSED = GrayScottSpec(size=64, F=0.0, k=0.0)
STEPS = 2000
CADENCE = 50
SWITCH = 1000                 # C2 switches to the exact closed limit here
LAGS = (1, 3, 6)
TURNOVER_M = 0.5              # frozen probe threshold (unchanged)
DISCRIM_MARGIN = 0.30         # pre-declared discrimination margin
DET = RDDetectionSpec(); PHE = RDPhenotypeSpec()


def rd_state_t(spec: GrayScottSpec, tracer: TracerSpec, seed: int):
    st = _rd_state_base(spec, seed)
    n = spec.size
    band = _cohort_grid(n, tracer.n_spatial)
    CU = np.zeros((tracer.n_cohorts, n, n)); CV = np.zeros((tracer.n_cohorts, n, n))
    for c in range(tracer.n_spatial):
        CU[c] = st.U * (band == c); CV[c] = st.V * (band == c)
    st.CU = CU; st.CV = CV
    return st


def run_control(tracer: TracerSpec, *, switch_to_closed: bool, seed: int = 2) -> dict[str, Any]:
    eng_open = RDEngine(OPEN, tracer); eng_closed = RDEngine(CLOSED, tracer)
    st = rd_state_t(OPEN, tracer, seed)
    trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=OPEN.size)
    per_track: dict[int, list] = {}
    snap_idx: dict[int, list[int]] = {}
    cur = st
    for t in range(0, STEPS + 1):
        if t % CADENCE == 0:
            spec_now = CLOSED if (switch_to_closed and t >= SWITCH) else OPEN
            p, r, a = rates(spec_now, cur)
            fes = detect_rd_entities(cur.U, cur.V, cur.CV, p, r, a, snapshot_step=t, time=float(t),
                                     detection=DET, phenotype_spec=PHE)
            tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=t, time=float(t))
            by = {e.local_index: e for e in fes}
            for to in tracked:
                per_track.setdefault(to.track_id, []).append(by[to.entity.local_index])
                snap_idx.setdefault(to.track_id, []).append(t)
        if t == STEPS:
            break
        eng = eng_closed if (switch_to_closed and t >= SWITCH) else eng_open
        cur = eng.step(cur)
    if not per_track:
        return {"n_tracks": 0, "median_late_M": 1.0, "median_early_M": 1.0, "main_obs": 0, "feed_frac_end": 0.0}
    main = max(per_track, key=lambda k: len(per_track[k]))
    fes = per_track[main]; steps_ = snap_idx[main]
    earlyM = []; lateM = []
    for lag in LAGS:
        for i in range(len(fes) - lag):
            m = rd_material_retention(fes[i].cohort_mass, fes[i + lag].cohort_mass)
            (lateM if steps_[i] >= SWITCH else earlyM).append(m)
    feed_end = float(fes[-1].cohort_mass[tracer.n_spatial:].sum() / max(fes[-1].cohort_mass.sum(), 1e-12))
    return {"n_tracks": len(per_track), "main_obs": len(fes),
            "median_early_M": float(np.median(earlyM)) if earlyM else 1.0,
            "median_late_M": float(np.median(lateM)) if lateM else 1.0,
            "feed_frac_end": feed_end}


def qualify_tracer() -> dict[str, Any]:
    """Pre-declared criterion: adequate iff median_late_M(C1) < 0.5 AND
    median_late_M(C2) - median_late_M(C1) > 0.30. Select the COARSEST adequate tau_feed."""
    candidates = [(500, 4), (250, 8), (125, 16), (62, 32)]        # (tau_feed, n_temporal); cycle ~= 2000 each
    results = {}
    for tau, T in candidates:
        tr = TracerSpec(n_spatial=8, n_temporal=T, tau_feed=tau)
        c1 = run_control(tr, switch_to_closed=False)
        c2 = run_control(tr, switch_to_closed=True)
        disc = c2["median_late_M"] - c1["median_late_M"]
        adequate = (c1["median_late_M"] < TURNOVER_M) and (disc > DISCRIM_MARGIN)
        results[f"tau{tau}_T{T}"] = {"tau_feed": tau, "n_temporal": T, "C1_late_M": c1["median_late_M"],
                                     "C2_late_M": c2["median_late_M"], "discrimination": disc,
                                     "adequate": bool(adequate), "C1_feed_frac_end": c1["feed_frac_end"]}
    # LEGACY single permanent FEED cohort -> must FAIL (saturation)
    legacy = TracerSpec(n_spatial=8, n_temporal=1, tau_feed=10 ** 9)
    l1 = run_control(legacy, switch_to_closed=False); l2 = run_control(legacy, switch_to_closed=True)
    legacy_disc = l2["median_late_M"] - l1["median_late_M"]
    legacy_res = {"C1_late_M": l1["median_late_M"], "C2_late_M": l2["median_late_M"],
                  "discrimination": legacy_disc, "C1_feed_frac_end": l1["feed_frac_end"],
                  "fails_as_predicted": bool(not (l1["median_late_M"] < TURNOVER_M and legacy_disc > DISCRIM_MARGIN))}
    adequate = [(v["tau_feed"], k) for k, v in results.items() if v["adequate"]]
    selected = max(adequate)[1] if adequate else None      # COARSEST (largest tau_feed) adequate
    return {"candidates": results, "legacy_single_feed_cohort": legacy_res,
            "criterion": ("adequate iff median_late_M(C1) < 0.5 AND median_late_M(C2)-median_late_M(C1) > 0.30; "
                          "select the COARSEST adequate tau_feed; never uses candidate yield or quadrant occupancy"),
            "selected": selected, "passed": bool(selected is not None and legacy_res["fails_as_predicted"])}
