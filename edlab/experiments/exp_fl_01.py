"""EXP_FL_01: blind low-discrepancy Flow-Lenia regime map (first regime map; no threshold relaxation).

Halton sample over the fixed-law Flow-Lenia parameter space; screen each (law, seed) through the QUALIFIED field
stack for persistent organization under constituent turnover (field P high, cohort field M low, on a clean long
track). Five evidence levels kept separate; no composite score; thresholds frozen; same-state causal intervention
is carried over for any survivor (not run in the screen).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.flow_lenia.engine import FlowLeniaSpec, FlowLeniaEngine, FlowLeniaState, flow_field
from ..substrates.flow_lenia.observables import (
    FieldDetectionSpec, FieldPhenotypeSpec, detect_field_entities, to_entity_observation,
    field_material_retention, phenotype_continuity,
)
from .baseline import halton_point
from .exp_fl_00 import gaussian_blobs_state


@dataclass(frozen=True)
class EXPFL01Config:
    n_laws: int = 24
    seeds: tuple[int, ...] = (8001, 8002, 8003)
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
        for k in ("seeds", "lag_indices"):
            d[k] = list(d[k])
        return d


def flow_lenia_law_from_halton(law_index: int) -> FlowLeniaSpec:
    p = halton_point(law_index + 32, 5)
    return FlowLeniaSpec(
        size=64, kernel_radius=10.0,
        kernel_mu=float(0.35 + 0.30 * p[0]),
        kernel_sigma=float(0.10 + 0.12 * p[1]),
        growth_mu=float(0.08 + 0.18 * p[2]),
        growth_sigma=float(0.010 + 0.030 * p[3]),
        dt=float(0.20 + 0.30 * p[4]),
    )


def screen_one(cfg: EXPFL01Config, law_index: int, seed: int) -> dict[str, Any]:
    spec = flow_lenia_law_from_halton(law_index)
    eng = FlowLeniaEngine(spec)
    st = gaussian_blobs_state(spec, seed)
    snaps = eng.simulate(st, cfg.steps, cfg.cadence)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells)
    phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    trk = LineageTracker(TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio), box_size=spec.size)
    cohort_by_track: dict[int, list[tuple[int, np.ndarray]]] = {}
    phen_by_track: dict[int, list[tuple[int, Any]]] = {}
    circ = []; masses = []; n_entities = []
    for s in snaps:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts, snapshot_step=s.step, time=float(s.step),
                                    detection=det, phenotype_spec=phe)
        n_entities.append(len(fes))
        for e in fes:
            circ.append(abs(e.phenotype.raw["internal_circulation"]))
            masses.append(e.phenotype.raw["mass"])
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by_local = {e.local_index: e for e in fes}
        for to in tracked:
            fe = by_local[to.entity.local_index]
            cohort_by_track.setdefault(to.track_id, []).append((s.step, fe.cohort_mass))
            phen_by_track.setdefault(to.track_id, []).append((s.step, fe.phenotype))
    complex_tracks: set[int] = set()
    for e in trk.events:
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    n = 0; sP = 0.0; sM = 0.0; probe = 0; eligible = False
    for tid, cm in cohort_by_track.items():
        ph = phen_by_track[tid]
        obs = len(cm)
        for lag in cfg.lag_indices:
            for i in range(obs - lag):
                p = phenotype_continuity(ph[i][1], ph[i + lag][1])
                m = field_material_retention(cm[i][1], cm[i + lag][1])
                n += 1; sP += p; sM += m
                if p > 0.8 and m < 0.5:
                    probe += 1
                    if tid not in complex_tracks and obs >= cfg.enroll_min_obs:
                        eligible = True
    track_lens = [len(v) for v in cohort_by_track.values()]
    return {
        "law_index": law_index, "seed": seed, "n_meas": n,
        "mean_P": (sP / n) if n else None, "mean_M": (sM / n) if n else None,
        "probe_count": probe, "eligible_seed": eligible,
        "n_tracks": len(cohort_by_track), "max_track_obs": max(track_lens) if track_lens else 0,
        "long_tracks": int(sum(1 for L in track_lens if L >= cfg.enroll_min_obs)),
        "mean_abs_circulation": float(np.mean(circ)) if circ else 0.0,
        "mean_entity_mass": float(np.mean(masses)) if masses else 0.0,
        "mean_entities_per_snapshot": float(np.mean(n_entities)) if n_entities else 0.0,
    }


def screen_records(cfg: EXPFL01Config, law_indices) -> list[dict[str, Any]]:
    return [screen_one(cfg, li, seed) for li in law_indices for seed in cfg.seeds]


def assemble_summary(cfg: EXPFL01Config, records: list[dict[str, Any]]) -> dict[str, Any]:
    elig_by_law: dict[int, int] = defaultdict(int)
    for r in records:
        if r["eligible_seed"]:
            elig_by_law[r["law_index"]] += 1
    permitted = sorted(l for l, c in elig_by_law.items() if c >= 2)
    Pvals = [r["mean_P"] for r in records if r["mean_P"] is not None]
    Mvals = [r["mean_M"] for r in records if r["mean_M"] is not None]
    decision = "EXP_FL_01_SCREEN_NEGATIVE" if not permitted else "EXP_FL_01_SCREEN_CANDIDATES"
    return {
        "config": cfg.as_dict(), "n_runs": len(records),
        "mean_field_P": float(np.mean(Pvals)) if Pvals else None,
        "mean_field_M": float(np.mean(Mvals)) if Mvals else None,
        "total_probe_rows": sum(r["probe_count"] for r in records),
        "laws_with_any_long_track": sorted({r["law_index"] for r in records if r["long_tracks"] > 0}),
        "eligible_seed_counts_by_law": {str(l): elig_by_law.get(l, 0) for l in sorted(elig_by_law)},
        "screening_permitted_laws": permitted, "n_screening_permitted_laws": len(permitted),
        "mean_abs_circulation": float(np.mean([r["mean_abs_circulation"] for r in records])),
        "decision": decision,
        "interpretation_levels": {"1_distributional_shift": "descriptive P/M/circulation across the map",
                                  "2_screening_signal": "permitted laws (>=2/3 seeds); permission, not candidate",
                                  "3_fresh_seed_recurrence": "not evaluated in this screen",
                                  "4_alias_rejection": "not evaluated in this screen",
                                  "5_causal_reestablishment": "not evaluated in this screen"},
        "boundary": "P and M separate; no composite; thresholds frozen; same-state causal intervention carried over for any survivor.",
    }
