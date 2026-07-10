"""EXP03-B screen: CORE V0 + isolated orbital/transverse interaction, matched OFF (neutral) vs ON.

Mirrors the EXP03-A screen structure and reuses the FROZEN CORE V0 observers (detector, tracker, phenotype,
P, M) with no recalibration. Adds mean |internal circulation| as the orbital-distinguishing descriptive metric.
OFF (orbital_strength=0) is CORE V0 on the identical core law/seed (matched comparator).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..entities.detection import detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import measure_tracks
from ..specs import DetectionSpec, LawSpec, OrbitalSpec, PhenotypeSpec, RunSpec, TrackerSpec, WorldSpec
from ..substrates.particle_dynamics.engine import initialize_world
from ..substrates.particle_dynamics.engine_orbital import simulate_orbital
from .baseline import halton_point, law_from_halton

ORBITAL_STRENGTH_MAG_RANGE = (0.4, 1.6)   # ON magnitude; sign from a Halton coord (chirality)
ORBITAL_RANGE_RANGE = (0.12, 0.28)        # < box/2


@dataclass(frozen=True)
class EXP03BConfig:
    n_laws: int = 64
    seeds: tuple[int, ...] = (7001, 7002, 7003)
    conditions: tuple[str, ...] = ("OFF", "ON")
    n_particles: int = 64
    n_types: int = 3
    dt: float = 0.02
    steps: int = 600
    snapshot_cadences: tuple[int, ...] = (10, 30, 60)
    lag_indices: tuple[int, ...] = (1, 3, 6)
    detection_radius: float = 0.11
    min_entity_size: int = 4
    tracker_distance: float = 0.16
    tracker_min_size_ratio: float = 0.25
    speed_scale: float = 0.25
    enroll_min_obs: int = 8
    cross_cadence: int = 2
    seed_offset_per_law: int = 100_000

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("seeds", "conditions", "snapshot_cadences", "lag_indices"):
            d[k] = list(d[k])
        d["orbital_strength_mag_range"] = list(ORBITAL_STRENGTH_MAG_RANGE)
        d["orbital_range_range"] = list(ORBITAL_RANGE_RANGE)
        return d


def exp03b_law(law_index: int, n_types: int = 3, *, orbital_on: bool) -> tuple[LawSpec, OrbitalSpec]:
    core = law_from_halton(law_index, n_types)
    point = halton_point(law_index + 32, n_types * n_types + 4 + 3)
    t = point[n_types * n_types + 4:]  # dims 13,14,15
    mag = ORBITAL_STRENGTH_MAG_RANGE[0] + (ORBITAL_STRENGTH_MAG_RANGE[1] - ORBITAL_STRENGTH_MAG_RANGE[0]) * t[0]
    rng = ORBITAL_RANGE_RANGE[0] + (ORBITAL_RANGE_RANGE[1] - ORBITAL_RANGE_RANGE[0]) * t[1]
    sign = 1.0 if t[2] < 0.5 else -1.0
    if orbital_on:
        orbital = OrbitalSpec(orbital_strength=float(sign * mag), orbital_range=float(rng))
    else:
        orbital = OrbitalSpec(orbital_strength=0.0, orbital_range=float(rng))
    return core, orbital


PM_EDGES = np.linspace(0.0, 1.0, 21)


def screen_one(cfg: EXP03BConfig, law_index: int, condition: str, seed: int) -> dict[str, Any]:
    world = WorldSpec(cfg.n_particles, cfg.n_types, initial_speed=0.04)
    det = DetectionSpec(cfg.detection_radius, cfg.min_entity_size)
    phe = PhenotypeSpec(length_scale=cfg.detection_radius, speed_scale=cfg.speed_scale)
    trk = TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio)
    core, orbital = exp03b_law(law_index, cfg.n_types, orbital_on=(condition == "ON"))
    run = RunSpec(seed=seed, dt=cfg.dt, steps=cfg.steps, snapshot_interval=min(cfg.snapshot_cadences),
                  backend="vectorized")
    initial = initialize_world(world, seed + cfg.seed_offset_per_law * law_index)
    snaps = simulate_orbital(initial, core, orbital, world, run)
    ents = {s.step: detect_entities(s.state, snapshot_step=s.step, time=s.time, world=world,
                                    detection=det, phenotype_spec=phe) for s in snaps}
    last_step = snaps[-1].step

    circ_abs: list[float] = []
    for obs in ents.values():
        for e in obs:
            circ_abs.append(abs(float(e.phenotype.raw["internal_circulation"])))

    sums = dict(n=0, P=0.0, M=0.0, PP=0.0, MM=0.0, PM=0.0)
    probe = 0
    hist = np.zeros((20, 20), dtype=np.int64)
    clean_endpoint_cad: dict[tuple[int, int], set[int]] = defaultdict(set)
    ev_counts: Counter[str] = Counter()
    track_obs_all: list[int] = []
    censored_tracks = 0
    turnover_vals: list[float] = []
    for cad in cfg.snapshot_cadences:
        tracker = LineageTracker(trk, box_size=world.box_size)
        for s in [s for s in snaps if s.step % cad == 0]:
            tracker.update(ents[s.step], snapshot_step=s.step, time=s.time)
        meas = measure_tracks(tracker.tracks, lag_indices=cfg.lag_indices, events=tracker.events)
        complex_tracks: set[int] = set()
        for e in tracker.events:
            ev_counts[e.kind] += 1
            if e.kind in {"split", "merge", "ambiguous_association"}:
                complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
        obs = {t: len(v) for t, v in tracker.tracks.items()}
        for tid, observations in tracker.tracks.items():
            track_obs_all.append(len(observations))
            if max(o.snapshot_step for o in observations) < last_step:
                censored_tracks += 1
        for m in meas:
            p, mm = m.phenotype_continuity, m.material_retention
            sums["n"] += 1; sums["P"] += p; sums["M"] += mm
            sums["PP"] += p * p; sums["MM"] += mm * mm; sums["PM"] += p * mm
            turnover_vals.append(1.0 - mm)
            ip = min(19, int(p * 20)); im = min(19, int(mm * 20)); hist[ip, im] += 1
            if p > 0.8 and mm < 0.5:
                probe += 1
                if m.track_id not in complex_tracks and obs[m.track_id] >= cfg.enroll_min_obs:
                    clean_endpoint_cad[(m.start_step, m.end_step)].add(cad)
    eligible_endpoints = [se for se, cads in clean_endpoint_cad.items() if len(cads) >= cfg.cross_cadence]
    return {
        "law_index": law_index, "condition": condition, "seed": seed,
        "n_meas": sums["n"], "sum_P": sums["P"], "sum_M": sums["M"],
        "sum_PP": sums["PP"], "sum_MM": sums["MM"], "sum_PM": sums["PM"],
        "mean_P": (sums["P"] / sums["n"]) if sums["n"] else None,
        "mean_M": (sums["M"] / sums["n"]) if sums["n"] else None,
        "mean_turnover": (float(np.mean(turnover_vals)) if turnover_vals else None),
        "mean_abs_circulation": (float(np.mean(circ_abs)) if circ_abs else 0.0),
        "probe_count": probe,
        "cross_cadence_endpoints": len(eligible_endpoints),
        "eligible_seed": bool(eligible_endpoints),
        "n_tracks": len(track_obs_all),
        "long_tracks": int(sum(1 for o in track_obs_all if o >= cfg.enroll_min_obs)),
        "mean_track_obs": (float(np.mean(track_obs_all)) if track_obs_all else 0.0),
        "max_track_obs": (int(max(track_obs_all)) if track_obs_all else 0),
        "censored_tracks": censored_tracks,
        "births": ev_counts.get("birth", 0), "splits": ev_counts.get("split", 0),
        "merges": ev_counts.get("merge", 0), "ambiguous": ev_counts.get("ambiguous_association", 0),
        "pm_hist": hist.flatten().tolist(),
    }


def screen_records(cfg: EXP03BConfig, law_indices) -> list[dict[str, Any]]:
    return [screen_one(cfg, li, cond, seed)
            for li in law_indices for cond in cfg.conditions for seed in cfg.seeds]


def _pearson(n, sx, sy, sxx, syy, sxy):
    if n < 2:
        return None
    cov = sxy - sx * sy / n; vx = sxx - sx * sx / n; vy = syy - sy * sy / n
    if vx <= 0 or vy <= 0:
        return None
    return float(cov / (vx * vy) ** 0.5)


def assemble_summary(cfg: EXP03BConfig, records: list[dict[str, Any]]) -> dict[str, Any]:
    by_cond: dict[str, dict[str, Any]] = {}
    for cond in cfg.conditions:
        rs = [r for r in records if r["condition"] == cond]
        n = sum(r["n_meas"] for r in rs)
        sP = sum(r["sum_P"] for r in rs); sM = sum(r["sum_M"] for r in rs)
        sPP = sum(r["sum_PP"] for r in rs); sMM = sum(r["sum_MM"] for r in rs); sPM = sum(r["sum_PM"] for r in rs)
        elig_by_law: dict[int, int] = defaultdict(int)
        for r in rs:
            if r["eligible_seed"]:
                elig_by_law[r["law_index"]] += 1
        permitted = sorted(l for l, c in elig_by_law.items() if c >= 2)
        hist = np.zeros(400, dtype=np.int64)
        for r in rs:
            hist += np.asarray(r["pm_hist"], dtype=np.int64)
        by_cond[cond] = {
            "n_measurements": n, "mean_P": (sP / n) if n else None, "mean_M": (sM / n) if n else None,
            "pearson_P_M_descriptive": _pearson(n, sP, sM, sPP, sMM, sPM),
            "probe_rows_P>0.8_M<0.5": sum(r["probe_count"] for r in rs),
            "probe_fraction": (sum(r["probe_count"] for r in rs) / n) if n else None,
            "long_tracks_total": sum(r["long_tracks"] for r in rs),
            "mean_abs_circulation": float(np.mean([r["mean_abs_circulation"] for r in rs])),
            "eligible_seed_counts_by_law": {str(l): elig_by_law.get(l, 0) for l in sorted(elig_by_law)},
            "screening_permitted_laws": permitted, "n_screening_permitted_laws": len(permitted),
            "mean_turnover": float(np.mean([r["mean_turnover"] for r in rs if r["mean_turnover"] is not None])),
            "censored_tracks_total": sum(r["censored_tracks"] for r in rs),
            "pm_hist_20x20": hist.reshape(20, 20).tolist(),
        }
    off = by_cond.get("OFF", {}); on = by_cond.get("ON", {})
    decision = "EXP03B_SCREEN_NEGATIVE" if on.get("n_screening_permitted_laws", 0) == 0 else "EXP03B_SCREEN_CANDIDATES"
    def d(a, b):
        return (a - b) if (a is not None and b is not None) else None
    return {
        "config": cfg.as_dict(), "by_condition": by_cond,
        "distributional_shift_ON_minus_OFF": {
            "d_mean_P": d(on.get("mean_P"), off.get("mean_P")), "d_mean_M": d(on.get("mean_M"), off.get("mean_M")),
            "d_probe_fraction": d(on.get("probe_fraction"), off.get("probe_fraction")),
            "d_mean_abs_circulation": d(on.get("mean_abs_circulation"), off.get("mean_abs_circulation")),
            "d_screening_permitted_laws": on.get("n_screening_permitted_laws", 0) - off.get("n_screening_permitted_laws", 0),
        },
        "decision": decision,
        "interpretation_levels": {
            "1_distributional_shift": "descriptive only (incl. circulation); not a candidate",
            "2_screening_signal": "screening permission (>=2/3 seeds); a permission, not a candidate",
            "3_fresh_seed_recurrence": "not evaluated in this screen run",
            "4_alias_rejection": "not evaluated in this screen run",
            "5_causal_reestablishment": "not evaluated in this screen run",
        },
        "boundary": ("P and M separate; no composite score. Screening permission is not a candidate. The five "
                     "evidence levels are distinct."),
    }
