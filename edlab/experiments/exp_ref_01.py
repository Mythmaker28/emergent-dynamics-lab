"""EXP_REF_01: tracer-labeled dynamical reference benchmark (measurement positive control).

A KNOWN persistent dissipative organization under constituent turnover is scripted kinematically and fed to the
FROZEN detector/tracker/P/M stack, alongside a matched static-flux null. The reference is a stationary rotating
packet (real tangential velocities -> internal circulation + velocity dispersion) whose membership turns over
gradually; the null is the identical packet with rotation OFF and zero velocity (the frozen
STATIC_MOTIF_WITH_MATERIAL_FLUX regime). Diagnostic IDs are PASSIVE labels: positions are scripted, so labels
cannot affect the (scripted) dynamics, and by the frozen ParticleState/detector/tracker invariant they never
affect detection/tracking/phenotype -- only the ID-based M reflects turnover. P is used exactly as frozen
(PhenotypeSpec(0.11,0.25)); it is NOT recalibrated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..entities.detection import detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import measure_tracks
from ..specs import DetectionSpec, PhenotypeSpec, TrackerSpec, WorldSpec
from ..state import ParticleState
from ..substrates.particle_dynamics.engine import SimulationSnapshot


@dataclass(frozen=True)
class RefConfig:
    n_particles: int = 64
    n_types: int = 3
    box_size: float = 1.0
    center: tuple[float, float] = (0.5, 0.5)
    packet_size: int = 10          # K ring slots (detected organization)
    ring_radius: float = 0.045
    pool_size: int = 20            # ring-eligible ID pool that cycles through the K slots
    omega: float = 2.0            # rad / time unit (rotation); 0 in the static-flux null
    dt: float = 0.02
    steps: int = 600
    cadence: int = 10
    lag_indices: tuple[int, ...] = (1, 3, 6)
    detection_radius: float = 0.11
    min_entity_size: int = 4
    tracker_distance: float = 0.16
    tracker_min_size_ratio: float = 0.25
    speed_scale: float = 0.25


def _background_grid(cfg: RefConfig, n: int) -> np.ndarray:
    pts = []
    cx, cy = cfg.center
    g = np.arange(0.02, 0.99, 0.12)          # 0.12 spacing > connection_radius 0.11 -> no background components
    for x in g:
        for y in g:
            if np.hypot(x - cx, y - cy) < 0.19:   # keep clear of the packet so it stays isolated
                continue
            pts.append((x, y))
    pts = np.array(pts, dtype=float)
    if len(pts) < n:
        raise ValueError(f"background grid too small: {len(pts)} < {n}")
    return pts[:n]


def build_snapshots(cfg: RefConfig, *, rotating: bool) -> list[SimulationSnapshot]:
    """Script the full 64-particle state per snapshot. Packet membership shifts by one ID per snapshot."""
    K, pool = cfg.packet_size, cfg.pool_size
    background_ids = list(range(pool, cfg.n_particles))            # permanent background labels
    bg_pos = _background_grid(cfg, len(background_ids))
    assert len(bg_pos) == len(background_ids), (len(bg_pos), len(background_ids))
    center = np.asarray(cfg.center)
    omega = cfg.omega if rotating else 0.0
    types = np.zeros(cfg.n_particles, dtype=np.int64)
    types[pool:] = np.arange(len(background_ids)) % 2 + 1           # background types 1/2; packet pool type 0
    snaps: list[SimulationSnapshot] = []
    steps = [s for s in range(0, cfg.steps + 1) if s % cfg.cadence == 0]
    for s in steps:
        t = s * cfg.dt
        positions = np.zeros((cfg.n_particles, 2)); velocities = np.zeros((cfg.n_particles, 2))
        idx = s // cfg.cadence                                    # snapshot index -> gradual turnover (shift 1/snapshot)
        ring_ids = [(idx + j) % pool for j in range(K)]           # which pool IDs occupy the ring now
        for slot, pid in enumerate(ring_ids):
            ang = 2.0 * np.pi * slot / K + omega * t
            positions[pid] = (center + cfg.ring_radius * np.array([np.cos(ang), np.sin(ang)])) % cfg.box_size
            velocities[pid] = omega * cfg.ring_radius * np.array([-np.sin(ang), np.cos(ang)])
        # pool IDs not currently in the ring -> park them on background-like far points (no component)
        parked = [pid for pid in range(pool) if pid not in ring_ids]
        park_pos = _background_grid(cfg, len(background_ids) + len(parked))[len(background_ids):]
        for k, pid in enumerate(parked):
            positions[pid] = park_pos[k]
        for k, pid in enumerate(background_ids):
            positions[pid] = bg_pos[k]
        ids = np.arange(cfg.n_particles)
        snaps.append(SimulationSnapshot(step=s, time=t, state=ParticleState(positions, velocities, types.copy(), ids)))
    return snaps


def run_through_frozen_stack(cfg: RefConfig, snaps: list[SimulationSnapshot]) -> dict[str, Any]:
    """Frozen detector/tracker/P/M. Returns P/M measurements + packet phenotype feature series (unchanged P)."""
    world = WorldSpec(cfg.n_particles, cfg.n_types, box_size=cfg.box_size, initial_speed=0.04)
    det = DetectionSpec(cfg.detection_radius, cfg.min_entity_size)
    phe = PhenotypeSpec(length_scale=cfg.detection_radius, speed_scale=cfg.speed_scale)
    trk = TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio)
    tracker = LineageTracker(trk, box_size=world.box_size)
    ent_counts = []; circ = []; vdisp = []; cvel = []; sizes = []
    for snp in snaps:
        ents = detect_entities(snp.state, snapshot_step=snp.step, time=snp.time, world=world,
                               detection=det, phenotype_spec=phe)
        ent_counts.append(len(ents))
        packet = max(ents, key=lambda e: len(e.particle_indices)) if ents else None
        if packet is not None:
            circ.append(abs(float(packet.phenotype.raw["internal_circulation"])))
            vdisp.append(float(packet.phenotype.raw["velocity_dispersion"]))
            cvel.append(float(np.linalg.norm(packet.phenotype.raw["center_velocity"])))
            sizes.append(len(packet.particle_indices))
        tracker.update(ents, snapshot_step=snp.step, time=snp.time)
    meas = measure_tracks(tracker.tracks, lag_indices=cfg.lag_indices, events=tracker.events)
    # main track = the longest
    if tracker.tracks:
        main = max(tracker.tracks, key=lambda t: len(tracker.tracks[t]))
        main_obs = len(tracker.tracks[main])
    else:
        main, main_obs = None, 0
    main_meas = [m for m in meas if m.track_id == main]
    probe = [m for m in main_meas if m.phenotype_continuity > 0.8 and m.material_retention < 0.5]
    return {
        "n_snapshots": len(snaps), "n_tracks": len(tracker.tracks), "main_track_obs": main_obs,
        "single_entity_per_snapshot": all(c == 1 for c in ent_counts),
        "entity_count_range": [int(min(ent_counts)), int(max(ent_counts))] if ent_counts else [0, 0],
        "mean_abs_circulation": float(np.mean(circ)) if circ else 0.0,
        "mean_velocity_dispersion": float(np.mean(vdisp)) if vdisp else 0.0,
        "mean_center_velocity": float(np.mean(cvel)) if cvel else 0.0,
        "mean_packet_size": float(np.mean(sizes)) if sizes else 0.0,
        "P_min_main": float(min((m.phenotype_continuity for m in main_meas), default=0.0)),
        "P_max_main": float(max((m.phenotype_continuity for m in main_meas), default=0.0)),
        "M_min_main": float(min((m.material_retention for m in main_meas), default=1.0)),
        "n_probe_positive_main": len(probe),
        "probe_positive_lags": sorted({int(round((m.end_step - m.start_step) / 1)) for m in probe}),
        "example_probe": [
            {"start": m.start_step, "end": m.end_step, "P": round(m.phenotype_continuity, 4),
             "M": round(m.material_retention, 4)} for m in probe[:5]],
    }
