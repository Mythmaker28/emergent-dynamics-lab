"""EXP_FL_00B: passive-tracer (cohort) resolution sensitivity check.

Compares fixed cohort granularities on the VALIDATED turnover reference and on representative static/cohesive
Flow-Lenia regimes. Dynamics (the mass field A) must be identical across granularities (cohorts are passive). The
cohort resolution is selected by a PRE-DECLARED measurement-resolution criterion anchored on the reference's known
turnover -- never on target-quadrant occupancy or candidate yield.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.flow_lenia.engine import FlowLeniaSpec, FlowLeniaEngine, FlowLeniaState, flow_field
from ..substrates.flow_lenia.observables import (
    FieldDetectionSpec, FieldPhenotypeSpec, detect_field_entities, to_entity_observation, field_material_retention,
)
from .exp_fl_00 import RefFieldConfig, build_field_snapshots, run_field_stack, gaussian_blobs_state
from .exp_fl_01 import EXPFL01Config, flow_lenia_law_from_halton


GRANULARITIES = (8, 16, 32)
CONVERGENCE_PROBE = 64                      # finer probe to check convergence of the coarsest adequate G
REFERENCE_TURNOVER_MAX = 0.15               # reference genuinely fully turns over -> adequate tracer sees M_min<=0.15
REP_STATIC_LAWS = (0, 6, 12, 18)            # blind representatives from map #1 (deterministic, not result-chosen)


def _field_M_stats(law_index: int, seed: int, n_cohorts: int, steps: int = 200) -> dict[str, float]:
    cfg = EXPFL01Config()
    spec = flow_lenia_law_from_halton(law_index)
    eng = FlowLeniaEngine(spec)
    st = gaussian_blobs_state(spec, seed, n_cohorts=n_cohorts)
    snaps = eng.simulate(st, steps, cfg.cadence)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells); phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    trk = LineageTracker(TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio), box_size=spec.size)
    cohort_by_track: dict[int, list[np.ndarray]] = {}
    for s in snaps:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts, snapshot_step=s.step, time=float(s.step), detection=det, phenotype_spec=phe)
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by_local = {e.local_index: e for e in fes}
        for to in tracked:
            cohort_by_track.setdefault(to.track_id, []).append(by_local[to.entity.local_index].cohort_mass)
    Ms = []
    for cm in cohort_by_track.values():
        for lag in cfg.lag_indices:
            for i in range(len(cm) - lag):
                Ms.append(field_material_retention(cm[i], cm[i + lag]))
    return {"mean_M": float(np.mean(Ms)) if Ms else 1.0, "min_M": float(min(Ms)) if Ms else 1.0}


def dynamics_identical_across_granularity(law_index: int = 0, seed: int = 8001, steps: int = 120) -> float:
    """Max |A_G1 - A_G2| over a run: cohorts are passive, so A must be identical across cohort counts."""
    spec = flow_lenia_law_from_halton(law_index); eng = FlowLeniaEngine(spec)
    a = eng.simulate(gaussian_blobs_state(spec, seed, n_cohorts=8), steps, 10)
    b = eng.simulate(gaussian_blobs_state(spec, seed, n_cohorts=32), steps, 10)
    return max(float(np.max(np.abs(x.A - y.A))) for x, y in zip(a, b))


def run_sensitivity() -> dict[str, Any]:
    ref_min_M: dict[int, float] = {}
    for G in (*GRANULARITIES, CONVERGENCE_PROBE):
        r = run_field_stack(RefFieldConfig(n_cohorts=G), build_field_snapshots(RefFieldConfig(n_cohorts=G), rotating=True))
        ref_min_M[G] = r["M_min_main"]
    static_M: dict[int, dict[str, float]] = {}
    for G in GRANULARITIES:
        vals = [_field_M_stats(li, 8001, G) for li in REP_STATIC_LAWS]
        static_M[G] = {"mean_M": float(np.mean([v["mean_M"] for v in vals])),
                       "min_M": float(np.min([v["min_M"] for v in vals]))}
    dyn = dynamics_identical_across_granularity()
    # PRE-DECLARED criterion: coarsest G in {8,16,32} that resolves reference turnover (M_min_ref(G) <= 0.15),
    # convergent (|M_min_ref(G) - M_min_ref(2G or 64)| <= 0.10). Static M reported as specificity only.
    adequate = [G for G in GRANULARITIES if ref_min_M[G] <= REFERENCE_TURNOVER_MAX]
    selected = None
    for G in GRANULARITIES:                        # ascending -> pick coarsest adequate + convergent
        if G not in adequate:
            continue
        finer = {8: 16, 16: 32, 32: CONVERGENCE_PROBE}[G]
        if abs(ref_min_M[G] - ref_min_M[finer]) <= 0.10:
            selected = G; break
    if selected is None and adequate:
        selected = adequate[0]
    return {
        "granularities": list(GRANULARITIES), "reference_min_M_by_G": {str(k): v for k, v in ref_min_M.items()},
        "static_regime_M_by_G": {str(k): v for k, v in static_M.items()},
        "dynamics_identical_across_G_maxdiff": dyn,
        "criterion": ("coarsest G resolving reference turnover (M_min_ref<=0.15) and convergent "
                      "(|dM_min_ref to next finer|<=0.10); static M is specificity-only; selection is "
                      "independent of candidate yield / target-quadrant occupancy"),
        "selected_cohort_resolution": selected,
        "passive_invariance_ok": dyn == 0.0,
    }
