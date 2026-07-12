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


def alias_audit_track(cfg: EXPFL02Config, law_index: int, seed: int) -> dict[str, Any]:
    """Direct alias audit on the eligible track: is the low M a PERSISTENT structure exchanging constituents, or
    blob dissolution/reformation (look-alike)? Reports mass stability, net displacement, reservoir-origin uptake."""
    spec, tspec = throughput_law_from_halton(law_index, on=True)
    eng = ThroughputEngine(spec, tspec)
    snaps = eng.simulate(throughput_state(spec, tspec, seed), cfg.steps, cfg.cadence)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells); phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    trk = LineageTracker(TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio), box_size=spec.size)
    rec: dict[int, list[Any]] = {}
    for s in snaps:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                    detection=det, phenotype_spec=phe)
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by_local = {e.local_index: e for e in fes}
        for to in tracked:
            fe = by_local[to.entity.local_index]
            rec.setdefault(to.track_id, []).append(fe)
    complex_tracks: set[int] = set()
    for e in trk.events:
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    best = None
    for tid, fes in rec.items():
        if tid in complex_tracks or len(fes) < cfg.enroll_min_obs:
            continue
        for lag in cfg.lag_indices:
            for i in range(len(fes) - lag):
                p_ = phenotype_continuity(fes[i].phenotype, fes[i + lag].phenotype)
                m_ = field_material_retention(fes[i].cohort_mass, fes[i + lag].cohort_mass)
                if p_ > 0.8 and m_ < 0.5:
                    best = (tid, fes); break
            if best: break
        if best: break
    if best is None:
        return {"law_index": law_index, "seed": seed, "eligible": False}
    tid, fes = best
    mass = np.array([f.phenotype.raw["mass"] for f in fes])
    cents = np.array([f.centroid for f in fes])
    from ..substrates.particle_dynamics.engine import minimum_image
    disp = float(np.linalg.norm(minimum_image(cents[-1] - cents[0], spec.size)))
    path = float(sum(np.linalg.norm(minimum_image(cents[i+1]-cents[i], spec.size)) for i in range(len(cents)-1)))
    res_frac = [float(f.cohort_mass[G_SPATIAL:].sum() / max(f.cohort_mass.sum(), 1e-12)) for f in fes]
    return {
        "law_index": law_index, "seed": seed, "eligible": True, "track_obs": len(fes),
        "mass_median": float(np.median(mass)), "mass_cv": float(mass.std() / max(mass.mean(), 1e-12)),
        "mass_min_over_median": float(mass.min() / max(np.median(mass), 1e-12)),
        "net_displacement_cells": disp, "path_length_cells": path,
        "reservoir_origin_frac_start": res_frac[0], "reservoir_origin_frac_end": res_frac[-1],
        "n_tracks_in_run": len(rec),
        # alias-compatible if the structure dissolves (mass collapse) rather than persisting through turnover
        "dissolution_alias": bool(mass.min() / max(np.median(mass), 1e-12) < 0.35),
    }


# ---------------------------------------------------------------- Level 5: same-state causal intervention

def _displace_mass(A, cohorts_A, cells, dy, dx):
    """Mass-conservatively relocate the mass of `cells` by (dy,dx). Zero-displacement is an exact no-op."""
    n = A.shape[0]
    mask = np.zeros_like(A); mask[cells[:, 0], cells[:, 1]] = 1.0
    keep = A * (1.0 - mask)
    moved = np.roll(np.roll(A * mask, dy, axis=0), dx, axis=1)
    A2 = keep + moved
    C2 = np.empty_like(cohorts_A)
    for c in range(cohorts_A.shape[0]):
        km = cohorts_A[c] * (1.0 - mask)
        mv = np.roll(np.roll(cohorts_A[c] * mask, dy, axis=0), dx, axis=1)
        C2[c] = km + mv
    return A2, C2


def causal_intervention(cfg: EXPFL02Config, law_index: int, seed: int, delta=(20, 20),
                        horizon: int = 150) -> dict[str, Any]:
    """Same-state matched branches: CONTROL / SHAM (no-op pipeline) / PERTURBED (displace the structure's mass
    off-site) / PLACEBO (displace a matched non-candidate mass region). Tests occupancy vs constituent-carried."""
    spec, tspec = throughput_law_from_halton(law_index, on=True)
    eng = ThroughputEngine(spec, tspec)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells); phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    snaps = eng.simulate(throughput_state(spec, tspec, seed), cfg.steps, cfg.cadence)
    # enroll: first snapshot (after warmup) with a detected entity of decent size = the candidate structure
    star = None
    for s in snaps[8:]:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                    detection=det, phenotype_spec=phe)
        if fes:
            big = max(fes, key=lambda e: e.size)
            if big.size >= 3 * cfg.min_cells:
                star = (s, big); break
    if star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False}
    s_star, cand = star
    phi_star = cand.phenotype
    old_c = np.asarray(cand.centroid)
    dy, dx = int(delta[0]), int(delta[1])
    new_c = (old_c + np.array([dy, dx])) % spec.size

    def run_branch(A0, C0):
        st = ThroughputState(A0.copy(), s_star.R.copy(), C0.copy(), s_star.cohorts_R.copy())
        out = eng.simulate(st, horizon, cfg.cadence)
        near_new = []; near_old = []
        for s in out[1:]:
            F, _ = flow_field(s.A, spec, eng._fK)
            fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                        detection=det, phenotype_spec=phe)
            def best_near(site):
                cand_l = [e for e in fes if float(np.linalg.norm(
                    minimum_image(np.asarray(e.centroid) - site, spec.size))) <= 12.0]
                if not cand_l: return 0.0
                return max(phenotype_continuity(phi_star, e.phenotype) for e in cand_l)
            near_new.append(best_near(new_c)); near_old.append(best_near(old_c))
        return {"P_new_site_mean": float(np.mean(near_new)), "P_new_site_final": float(near_new[-1]),
                "P_old_site_mean": float(np.mean(near_old)), "P_old_site_final": float(near_old[-1]),
                "frac_new_site_organized": float(np.mean([p > 0.8 for p in near_new])),
                "frac_old_site_organized": float(np.mean([p > 0.8 for p in near_old]))}

    from ..substrates.particle_dynamics.engine import minimum_image
    cells = cand.cells
    A_ctrl, C_ctrl = s_star.A, s_star.cohorts_A
    A_sham, C_sham = _displace_mass(s_star.A, s_star.cohorts_A, cells, 0, 0)          # pipeline no-op
    A_pert, C_pert = _displace_mass(s_star.A, s_star.cohorts_A, cells, dy, dx)        # displace the structure
    # placebo: displace a matched non-candidate mass region (same cell count, elsewhere)
    occupied = np.zeros_like(s_star.A, dtype=bool); occupied[cells[:, 0], cells[:, 1]] = True
    ys, xs = np.nonzero(~occupied & (s_star.A > 0))
    k = min(len(cells), len(ys))
    pcells = np.stack([ys[:k], xs[:k]], axis=1)
    A_plac, C_plac = _displace_mass(s_star.A, s_star.cohorts_A, pcells, dy, dx)

    sham_identical = bool(np.array_equal(A_sham, A_ctrl) and np.array_equal(C_sham, C_ctrl))
    branches = {"CONTROL": run_branch(A_ctrl, C_ctrl), "SHAM": run_branch(A_sham, C_sham),
                "PERTURBED": run_branch(A_pert, C_pert), "PLACEBO": run_branch(A_plac, C_plac)}
    p = branches["PERTURBED"]
    # occupancy alias: after displacing the structure, the OLD site regenerates the phenotype anyway
    occupancy_alias = p["frac_old_site_organized"] > 0.5
    # constituent-carried: the displaced mass re-establishes the organization at the NEW site
    carried = p["frac_new_site_organized"] > 0.5
    return {"law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
            "sham_equals_control": sham_identical, "cand_cells": int(len(cells)),
            "branches": branches, "occupancy_alias": occupancy_alias, "constituent_carried": carried,
            "audited_reestablishment": bool(carried and not occupancy_alias)}
