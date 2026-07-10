"""EXP_FL_00: qualification of the Flow-Lenia substrate + field measurement stack.

No law search. Validates the mass-conservative core + passive cohorts, adapts the detector/tracker/P/M to fields,
preregisters a field material-retention M(tau), and reruns the EXP-REF-01 measurement positive control on the new
field stack (a scripted rotating mass blob with cohort turnover vs a matched static-flux field null). P is not
recalibrated; the field phenotype uses declared (not tuned) scales.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.flow_lenia.engine import FlowLeniaSpec, FlowLeniaEngine, FlowLeniaState
from ..substrates.flow_lenia.observables import (
    FieldDetectionSpec, FieldPhenotypeSpec, detect_field_entities, to_entity_observation,
    field_material_retention, phenotype_continuity,
)


@dataclass(frozen=True)
class RefFieldConfig:
    size: int = 64
    blob_radius: float = 7.0
    blob_amp: float = 1.0
    omega: float = 0.15            # rotation (0 in the static-flux null)
    n_cohorts: int = 8
    cohort_width: float = 1.0
    n_snapshots: int = 61
    lag_indices: tuple[int, ...] = (1, 3, 6)
    threshold: float = 0.15
    min_cells: int = 12
    length_scale: float = 10.0
    speed_scale: float = 1.0
    tracker_distance: float = 8.0   # cells (field units); geometry-only association (frozen tracker logic)
    tracker_min_size_ratio: float = 0.25


def build_field_snapshots(cfg: RefFieldConfig, *, rotating: bool):
    """Scripted persistent dissipative organization: fixed blob (persistent phenotype), rotation velocity field
    (circulation) when rotating, and gradual cohort turnover (a shifting cohort window)."""
    n = cfg.size
    yy, xx = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    cy = cx = n / 2.0
    r2 = (yy - cy) ** 2 + (xx - cx) ** 2
    A = cfg.blob_amp * np.exp(-r2 / (2.0 * cfg.blob_radius ** 2))
    omega = cfg.omega if rotating else 0.0
    F = np.stack([-omega * (xx - cx), omega * (yy - cy)], axis=0)   # [Fy,Fx] rigid rotation (0 if static)
    snaps = []
    for s in range(cfg.n_snapshots):
        phase = float(s)                                            # shift 1 cohort/snapshot -> gradual turnover
        cc = np.arange(cfg.n_cohorts)
        d = np.minimum((cc - phase) % cfg.n_cohorts, (phase - cc) % cfg.n_cohorts)
        w = np.exp(-0.5 * (d / cfg.cohort_width) ** 2); w = w / w.sum()
        cohorts = A[None, :, :] * w[:, None, None]                  # sum_c cohorts == A
        snaps.append((s, float(s), A.copy(), F.copy(), cohorts))
    return snaps


def run_field_stack(cfg: RefFieldConfig, snaps) -> dict[str, Any]:
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells)
    phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)
    trk = LineageTracker(TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio), box_size=cfg.size)
    ent_counts = []; circ = []; vdisp = []; cvel = []
    cohort_by_track: dict[int, list[tuple[int, np.ndarray]]] = {}
    phen_by_track: dict[int, list[tuple[int, Any]]] = {}
    for (s, t, A, F, cohorts) in snaps:
        fes = detect_field_entities(A, F, cohorts, snapshot_step=s, time=t, detection=det, phenotype_spec=phe)
        ent_counts.append(len(fes))
        if fes:
            big = max(fes, key=lambda e: e.size)
            circ.append(abs(big.phenotype.raw["internal_circulation"]))
            vdisp.append(big.phenotype.raw["velocity_dispersion"])
            cvel.append(float(np.linalg.norm(big.phenotype.raw["center_velocity"])))
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s, time=t)
        by_local = {e.local_index: e for e in fes}
        for to in tracked:
            fe = by_local[to.entity.local_index]
            cohort_by_track.setdefault(to.track_id, []).append((s, fe.cohort_mass))
            phen_by_track.setdefault(to.track_id, []).append((s, fe.phenotype))
    # P/M on the longest track at the declared lags
    if cohort_by_track:
        main = max(cohort_by_track, key=lambda k: len(cohort_by_track[k]))
        cm = cohort_by_track[main]; ph = phen_by_track[main]
        Ps = []; Ms = []; probe = []
        for lag in cfg.lag_indices:
            for i in range(len(cm) - lag):
                p = phenotype_continuity(ph[i][1], ph[i + lag][1])
                m = field_material_retention(cm[i][1], cm[i + lag][1])
                Ps.append(p); Ms.append(m)
                if p > 0.8 and m < 0.5:
                    probe.append((cm[i][0], cm[i + lag][0], round(p, 4), round(m, 4)))
        main_obs = len(cm)
    else:
        main, Ps, Ms, probe, main_obs = None, [], [], [], 0
    return {
        "n_snapshots": len(snaps), "n_tracks": len(cohort_by_track), "main_track_obs": main_obs,
        "single_entity_per_snapshot": all(c == 1 for c in ent_counts),
        "entity_count_range": [int(min(ent_counts)), int(max(ent_counts))] if ent_counts else [0, 0],
        "P_max_main": float(max(Ps)) if Ps else 0.0, "P_min_main": float(min(Ps)) if Ps else 0.0,
        "M_min_main": float(min(Ms)) if Ms else 1.0,
        "n_probe_positive_main": len(probe), "example_probe": probe[:5],
        "mean_abs_circulation": float(np.mean(circ)) if circ else 0.0,
        "mean_velocity_dispersion": float(np.mean(vdisp)) if vdisp else 0.0,
        "mean_center_velocity": float(np.mean(cvel)) if cvel else 0.0,
    }


def _cohort_grid(n: int, n_cohorts: int):
    """Deterministic square-ish spatial partition of the grid into n_cohorts bands."""
    cols = int(round(n_cohorts ** 0.5))
    while n_cohorts % cols:
        cols -= 1
    rows = n_cohorts // cols
    yy, xx = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    band = (xx * cols // n) + cols * (yy * rows // n)
    return band % n_cohorts


def gaussian_blobs_state(spec: FlowLeniaSpec, seed: int, n_blobs: int = 3, n_cohorts: int = 8) -> FlowLeniaState:
    rng = np.random.default_rng(seed)
    n = spec.size
    yy, xx = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    A = np.zeros((n, n))
    for _ in range(n_blobs):
        cy, cx = rng.uniform(0, n, 2); r = rng.uniform(5, 10)
        d2 = np.minimum((yy - cy) % n, (cy - yy) % n) ** 2 + np.minimum((xx - cx) % n, (cx - xx) % n) ** 2
        A += rng.uniform(0.6, 1.0) * np.exp(-d2 / (2 * r ** 2))
    band = _cohort_grid(n, n_cohorts)
    cohorts = np.stack([A * (band == c) for c in range(n_cohorts)], axis=0)
    return FlowLeniaState(A, cohorts)


def _direct_potential(spec: FlowLeniaSpec, A: np.ndarray) -> np.ndarray:
    n = spec.size
    c = np.fft.fftfreq(n) * n
    yy, xx = np.meshgrid(c, c, indexing="ij"); r = np.hypot(yy, xx)
    R = spec.kernel_radius
    K = np.exp(-0.5 * ((r - spec.kernel_mu * R) / (spec.kernel_sigma * R)) ** 2); K[r > R] = 0.0; K /= K.sum()
    U = np.zeros_like(A)
    for dy, dx in zip(*np.nonzero(K)):
        U += K[dy, dx] * np.roll(np.roll(A, dy, axis=0), dx, axis=1)
    return U


def qualify(spec: FlowLeniaSpec | None = None) -> dict[str, Any]:
    """Run the frozen EXP_FL_00 qualification gate. Returns per-check results and overall pass/fail."""
    spec = spec or FlowLeniaSpec()
    eng = FlowLeniaEngine(spec)
    st = gaussian_blobs_state(spec, 1)
    snaps = eng.simulate(FlowLeniaState(st.A.copy(), st.cohorts.copy()), 200, 10)
    m0 = float(st.A.sum())
    mass_drift = max(abs(float(s.A.sum()) - m0) / m0 for s in snaps)
    nonneg = min(float(s.A.min()) for s in snaps)
    cohort_partition = max(float(np.max(np.abs(s.cohorts.sum(0) - s.A))) for s in snaps)
    snaps2 = eng.simulate(FlowLeniaState(st.A.copy(), st.cohorts.copy()), 200, 10)
    determinism = max(float(np.max(np.abs(a.A - b.A))) for a, b in zip(snaps, snaps2))
    # passive tracer invariance
    sb = eng.simulate(FlowLeniaState(st.A.copy(), np.zeros((1, spec.size, spec.size))), 200, 10)
    tracer_inv = max(float(np.max(np.abs(a.A - b.A))) for a, b in zip(snaps, sb))
    # reference-path agreement
    from ..substrates.flow_lenia.engine import _kernel_fft
    U_fft = np.real(np.fft.ifft2(_kernel_fft(spec) * np.fft.fft2(st.A)))
    refpath = float(np.max(np.abs(U_fft - _direct_potential(spec, st.A))))
    # detector/tracker on real dynamics
    from ..substrates.flow_lenia.engine import flow_field
    from ..substrates.flow_lenia.observables import detect_field_entities, to_entity_observation, FieldDetectionSpec, FieldPhenotypeSpec
    det = FieldDetectionSpec(0.15, 12); phe = FieldPhenotypeSpec(10.0, 1.0)
    trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=spec.size)
    for s in snaps:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts, snapshot_step=s.step, time=float(s.step), detection=det, phenotype_spec=phe)
        trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
    max_track = max((len(v) for v in trk.tracks.values()), default=0)
    # EXP-REF-01 field rerun
    cfg = RefFieldConfig()
    ref = run_field_stack(cfg, build_field_snapshots(cfg, rotating=True))
    nul = run_field_stack(cfg, build_field_snapshots(cfg, rotating=False))
    recognized = (ref["single_entity_per_snapshot"] and ref["n_tracks"] == 1 and ref["P_max_main"] > 0.8
                  and ref["M_min_main"] < 0.5 and ref["n_probe_positive_main"] > 0)
    separated = (ref["mean_abs_circulation"] > 0.02 and ref["mean_velocity_dispersion"] > 0.02
                 and nul["mean_abs_circulation"] < 1e-6 and nul["mean_velocity_dispersion"] < 1e-6)
    checks = {
        "mass_conservation": mass_drift < 1e-9,
        "nonnegativity": nonneg >= -1e-12,
        "cohort_partition_preserved": cohort_partition < 1e-9,
        "determinism": determinism == 0.0,
        "passive_tracer_invariance": tracer_inv == 0.0,
        "reference_path_agreement": refpath <= 1e-9,
        "detector_tracker_on_real_dynamics": max_track >= 3,
        "expref01_recognized": recognized,
        "expref01_separated": separated,
    }
    return {
        "checks": checks, "passed": all(checks.values()),
        "metrics": {"mass_drift": mass_drift, "min_A": nonneg, "cohort_partition_err": cohort_partition,
                    "determinism": determinism, "tracer_invariance": tracer_inv, "refpath_err": refpath,
                    "max_track_len": max_track},
        "expref01_reference": ref, "expref01_null": nul,
    }
