"""EXP_FL_02: isolated reservoir-exchange material-throughput mechanism; matched OFF/ON blind screen.

Cohort labelling (pre-declared): the verified spatial resolution G*=8 is applied SEPARATELY to each mass pool, so
cohorts distinguish ACTIVE-origin from RESERVOIR-origin mass (2*G = 16 cohorts total). This is required for the
tracer to register local A<->R exchange as constituent turnover; a purely spatial labelling would conflate
reservoir mass with active mass at the same location. Validated by a throughput positive control.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.flow_lenia.engine import FlowLeniaSpec, FlowLeniaEngine, FlowLeniaState, flow_field
from ..substrates.flow_lenia.engine_throughput import ThroughputSpec, ThroughputEngine, ThroughputState
from ..substrates.flow_lenia.observables import (
    FieldDetectionSpec, FieldPhenotypeSpec, detect_field_entities, to_entity_observation,
    field_material_retention, phenotype_continuity,
)
from .baseline import halton_point
from .exp_fl_00 import _cohort_grid, gaussian_blobs_state
from .exp_fl_01 import EXPFL01Config, flow_lenia_law_from_halton_v2

G_SPATIAL = 8   # verified tracer resolution (D-024), applied per mass pool


def throughput_state(spec: FlowLeniaSpec, tspec: ThroughputSpec, seed: int) -> ThroughputState:
    base = gaussian_blobs_state(spec, seed, n_cohorts=G_SPATIAL)
    A = base.A
    n = spec.size
    band = _cohort_grid(n, G_SPATIAL)
    active_mass = float(A.sum())
    R = np.full((n, n), tspec.reservoir_fraction * active_mass / (n * n), dtype=float)  # uniform latent reservoir
    C = 2 * G_SPATIAL
    CA = np.zeros((C, n, n)); CR = np.zeros((C, n, n))
    for c in range(G_SPATIAL):
        CA[c] = A * (band == c)                    # cohorts 0..G-1 = ACTIVE-origin mass, by region
        CR[G_SPATIAL + c] = R * (band == c)        # cohorts G..2G-1 = RESERVOIR-origin mass, by region
    return ThroughputState(A, R, CA, CR)


@dataclass(frozen=True)
class EXPFL02Config:
    n_laws: int = 64
    seeds: tuple[int, ...] = (8001, 8002, 8003)
    conditions: tuple[str, ...] = ("OFF", "ON")
    steps: int = 300
    cadence: int = 10
    lag_indices: tuple[int, ...] = (1, 3, 6)
    threshold: float = 0.15
    min_cells: int = 12
    length_scale: float = 10.0
    speed_scale: float = 1.0
    tracker_distance: float = 8.0
    tracker_min_size_ratio: float = 0.25
    enroll_min_obs: int = 8

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("seeds", "conditions", "lag_indices"):
            d[k] = list(d[k])
        return d


def throughput_law_from_halton(law_index: int, *, on: bool) -> tuple[FlowLeniaSpec, ThroughputSpec]:
    """Core law from the map-#2 flux-favouring sampler; throughput params from 3 extra Halton dims.
    OFF = exchange_rate 0 (EXACT current-core limit) with identical reservoir/diffusion."""
    spec = flow_lenia_law_from_halton_v2(law_index)
    p = halton_point(law_index + 32, 11)[8:11]
    diffusion = float(0.05 + 0.20 * p[1])
    fraction = float(0.5 + 1.5 * p[2])
    rate = float(0.05 + 0.75 * p[0]) if on else 0.0
    return spec, ThroughputSpec(exchange_rate=rate, reservoir_diffusion=diffusion, reservoir_fraction=fraction)


def screen_one(cfg: EXPFL02Config, law_index: int, condition: str, seed: int) -> dict[str, Any]:
    spec, tspec = throughput_law_from_halton(law_index, on=(condition == "ON"))
    eng = ThroughputEngine(spec, tspec)
    st = throughput_state(spec, tspec, seed)
    snaps = eng.simulate(st, cfg.steps, cfg.cadence)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells); phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    trk = LineageTracker(TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio), box_size=spec.size)
    cohort_by_track: dict[int, list[np.ndarray]] = {}
    phen_by_track: dict[int, list[Any]] = {}
    circ = []; n_ent = []
    m0 = snaps[0].total_mass()
    mass_drift = max(abs(s.total_mass() - m0) / m0 for s in snaps)
    for s in snaps:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                    detection=det, phenotype_spec=phe)
        n_ent.append(len(fes))
        for e in fes:
            circ.append(abs(e.phenotype.raw["internal_circulation"]))
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by_local = {e.local_index: e for e in fes}
        for to in tracked:
            fe = by_local[to.entity.local_index]
            cohort_by_track.setdefault(to.track_id, []).append(fe.cohort_mass)
            phen_by_track.setdefault(to.track_id, []).append(fe.phenotype)
    complex_tracks: set[int] = set()
    for e in trk.events:
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    n = 0; sP = 0.0; sM = 0.0; probe = 0; eligible = False; minM = 1.0
    for tid, cm in cohort_by_track.items():
        ph = phen_by_track[tid]; obs = len(cm)
        for lag in cfg.lag_indices:
            for i in range(obs - lag):
                p_ = phenotype_continuity(ph[i], ph[i + lag])
                m_ = field_material_retention(cm[i], cm[i + lag])
                n += 1; sP += p_; sM += m_; minM = min(minM, m_)
                if p_ > 0.8 and m_ < 0.5:
                    probe += 1
                    if tid not in complex_tracks and obs >= cfg.enroll_min_obs:
                        eligible = True
    tl = [len(v) for v in cohort_by_track.values()]
    return {
        "law_index": law_index, "condition": condition, "seed": seed, "n_meas": n,
        "mean_P": (sP / n) if n else None, "mean_M": (sM / n) if n else None, "min_M": minM,
        "probe_count": probe, "eligible_seed": eligible,
        "n_tracks": len(cohort_by_track), "max_track_obs": max(tl) if tl else 0,
        "long_tracks": int(sum(1 for L in tl if L >= cfg.enroll_min_obs)),
        "mean_abs_circulation": float(np.mean(circ)) if circ else 0.0,
        "total_mass_drift": mass_drift,
        "exchange_rate": tspec.exchange_rate,
    }


def screen_records(cfg: EXPFL02Config, law_indices) -> list[dict[str, Any]]:
    return [screen_one(cfg, li, cond, seed)
            for li in law_indices for cond in cfg.conditions for seed in cfg.seeds]
