"""ALIAS-INTERVENTION-COREV0: same-state matched-branch displacement test for survivors {0,52}.

Purpose (see docs/experiments/ALIAS_INTERVENTION_COREV0_01_PROTOCOL.md):
Distinguish, for a screening-eligible candidate organization, whether phenotype continuity P under
constituent turnover M reflects an organization carried by its constituents (individuality) versus a
stationary spatial-occupancy / look-alike alias. The intervention rigidly displaces the candidate's
constituent set off its former spatial site by a pre-declared vector; three matched branches start from
the identical pre-intervention physical state.

Scientific invariants honored:
- Diagnostic particle IDs are used ONLY to follow constituents for measurement/audit. They never enter
  physics (engine), detection, or tracker association (which use geometry/size only).
- P (phenotype continuity to the frozen pre-intervention descriptor) and M (Jaccard of ID sets) are logged
  separately. No composite recovery/memory/theseus score is formed.
- Thresholds (P>0.8, M<0.5, min_size, tracker gates) are the frozen CORE V0 values; none are altered here.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

from ..entities.detection import EntityObservation, detect_entities
from ..entities.tracking import LineageTracker
from ..observables.continuity import material_retention
from ..observables.phenotype import Phenotype, phenotype_similarity
from ..specs import DetectionSpec, PhenotypeSpec, RunSpec, TrackerSpec, WorldSpec
from ..state import ParticleState
from ..substrates.particle_dynamics.engine import initialize_world, minimum_image, simulate
from .baseline import law_from_halton


@dataclass(frozen=True)
class CausalConfig:
    # frozen CORE V0 physics/observers (identical to baseline defaults)
    n_particles: int = 64
    n_types: int = 3
    initial_speed: float = 0.04
    dt: float = 0.02
    base_cadence: int = 10
    enroll_cadences: tuple[int, ...] = (10, 30, 60)
    lag_indices: tuple[int, ...] = (1, 3, 6)
    detection_radius: float = 0.11
    min_entity_size: int = 4
    tracker_distance: float = 0.16
    tracker_min_size_ratio: float = 0.25
    speed_scale: float = 0.25
    enroll_steps: int = 600           # steps simulated to locate the first eligible endpoint
    enroll_min_obs: int = 8           # frozen long-track requirement
    enroll_cross_cadence: int = 2     # frozen same-endpoint corroboration
    # intervention
    laws: tuple[int, ...] = (0, 52)
    seed_plan: tuple[int, ...] = tuple(range(5001, 5041))   # fresh, unseen causal seeds
    delta: tuple[float, float] = (0.30, 0.30)               # pre-declared off-site displacement (box units)
    horizon_post: int = 360           # post-intervention observation steps (36 base-cadence snapshots)
    site_radius: float = 0.11         # "at a site" if periodic centroid within this of the site
    persist_p: float = 0.8            # phenotype match to phi* (frozen probe P threshold)
    material_low: float = 0.5         # frozen probe M threshold

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("enroll_cadences", "lag_indices", "laws", "seed_plan", "delta"):
            d[k] = list(d[k])
        return d


def _world(cfg: CausalConfig) -> WorldSpec:
    return WorldSpec(n_particles=cfg.n_particles, n_types=cfg.n_types, initial_speed=cfg.initial_speed)


def _specs(cfg: CausalConfig):
    det = DetectionSpec(cfg.detection_radius, cfg.min_entity_size)
    phe = PhenotypeSpec(length_scale=cfg.detection_radius, speed_scale=cfg.speed_scale)
    trk = TrackerSpec(cfg.tracker_distance, cfg.tracker_min_size_ratio)
    return det, phe, trk


def periodic_distance(a: np.ndarray, b: np.ndarray, box: float) -> float:
    return float(np.linalg.norm(minimum_image(np.asarray(a) - np.asarray(b), box)))


# --------------------------------------------------------------------------- enrollment

@dataclass(frozen=True)
class Enrollment:
    law_index: int
    seed: int
    enrolled: bool
    reason: str
    first_eligible_start: int | None
    first_eligible_end: int | None
    corroborating_cadences: tuple[int, ...]
    enroll_cadence: int | None
    track_id: int | None
    candidate_indices: tuple[int, ...]
    candidate_ids: tuple[int, ...]
    candidate_size: int
    old_centroid: tuple[float, float] | None
    prior_snapshots: int
    state: ParticleState | None = None
    phi_star: Phenotype | None = None


def _detect_all(snapshots, world, det, phe):
    return {
        s.step: detect_entities(s.state, snapshot_step=s.step, time=s.time,
                                world=world, detection=det, phenotype_spec=phe)
        for s in snapshots
    }


def enroll(cfg: CausalConfig, law_index: int, seed: int):
    """Locate the first eligible endpoint using the EXACT frozen cross-cadence eligibility rule.

    Returns (Enrollment, snapshots, entities_by_step) so branches can reuse the pre-intervention state.
    """
    world = _world(cfg)
    det, phe, trk = _specs(cfg)
    law = law_from_halton(law_index, cfg.n_types)
    run = RunSpec(seed=seed, dt=cfg.dt, steps=cfg.enroll_steps,
                  snapshot_interval=cfg.base_cadence, backend="vectorized")
    initial = initialize_world(world, seed + 100_000 * law_index)
    snapshots = simulate(initial, law, world, run)
    ents = _detect_all(snapshots, world, det, phe)

    from ..observables.continuity import measure_tracks
    clean_endpoint_cad: dict[tuple[int, int], set[int]] = defaultdict(set)
    trackers: dict[int, LineageTracker] = {}
    for cad in cfg.enroll_cadences:
        tracker = LineageTracker(trk, box_size=world.box_size)
        for s in [s for s in snapshots if s.step % cad == 0]:
            tracker.update(ents[s.step], snapshot_step=s.step, time=s.time)
        trackers[cad] = tracker
        meas = measure_tracks(tracker.tracks, lag_indices=cfg.lag_indices, events=tracker.events)
        complex_tracks: set[int] = set()
        for e in tracker.events:
            if e.kind in {"split", "merge", "ambiguous_association"}:
                complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
        obs = {t: len(v) for t, v in tracker.tracks.items()}
        for m in meas:
            if m.phenotype_continuity > cfg.persist_p and m.material_retention < cfg.material_low:
                if m.track_id in complex_tracks or obs[m.track_id] < cfg.enroll_min_obs:
                    continue
                clean_endpoint_cad[(m.start_step, m.end_step)].add(cad)

    eligible = [se for se, cads in clean_endpoint_cad.items() if len(cads) >= cfg.enroll_cross_cadence]
    if not eligible:
        return (Enrollment(law_index, seed, False, "no_cross_cadence_eligible_endpoint",
                           None, None, (), None, None, (), (), 0, None, 0), snapshots, ents)
    eligible.sort(key=lambda se: (se[1], se[0]))
    start, end = eligible[0]
    cads = tuple(sorted(clean_endpoint_cad[(start, end)]))
    cad = cads[0]
    tracker = trackers[cad]
    meas = measure_tracks(tracker.tracks, lag_indices=cfg.lag_indices, events=tracker.events)
    complex_tracks = set()
    for e in tracker.events:
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    obs = {t: len(v) for t, v in tracker.tracks.items()}
    owners = sorted({m.track_id for m in meas
                     if m.start_step == start and m.end_step == end
                     and m.phenotype_continuity > cfg.persist_p and m.material_retention < cfg.material_low
                     and m.track_id not in complex_tracks and obs[m.track_id] >= cfg.enroll_min_obs},
                    key=lambda t: (-obs[t], t))
    track_id = owners[0]
    end_ent = [o for o in tracker.tracks[track_id] if o.snapshot_step == end][0]
    state_star = [s for s in snapshots if s.step == end][0].state
    enr = Enrollment(
        law_index, seed, True, "eligible",
        start, end, cads, cad, track_id,
        tuple(int(i) for i in end_ent.particle_indices),
        tuple(sorted(int(i) for i in end_ent.particle_ids)),
        len(end_ent.particle_indices),
        (float(end_ent.centroid[0]), float(end_ent.centroid[1])),
        end // cfg.base_cadence,
        state_star.copy(),
        end_ent.phenotype,
    )
    return enr, snapshots, ents


# --------------------------------------------------------------------------- intervention harness

def apply_displacement(state: ParticleState, indices, delta, box: float) -> ParticleState:
    """Rigidly translate the given constituents by `delta` (mod box). Velocities/types/ids unchanged.

    The full detect->select->serialize->reinstantiate path is exercised regardless of delta magnitude, so a
    zero-delta call is a pipeline-exact no-op sham (must reproduce the untouched state bit-for-bit)."""
    positions = state.positions.copy()
    velocities = state.velocities.copy()
    types = state.types.copy()
    ids = state.ids.copy()
    idx = np.asarray(indices, dtype=np.int64)
    positions[idx] = (positions[idx] + np.asarray(delta, dtype=np.float64)) % box
    return ParticleState(positions, velocities, types, ids)


def largest_other_component(state, candidate_indices, cfg, world, det, phe):
    """The largest non-candidate connected component (EntityObservation) — the displacement placebo target."""
    obsv = detect_entities(state, snapshot_step=0, time=0.0, world=world, detection=det, phenotype_spec=phe)
    cand = set(int(i) for i in candidate_indices)
    others = [o for o in obsv if not (set(int(i) for i in o.particle_indices) & cand)]
    if not others:
        return None
    others.sort(key=lambda o: (-len(o.particle_indices), o.local_index))
    return others[0]


# --------------------------------------------------------------------------- branch readout

def _carrier(entities, C):
    best, best_overlap = None, -1
    for e in entities:
        ov = len(e.particle_ids & C)
        if ov > best_overlap:
            best, best_overlap = e, ov
    return best


def measure_branch(cfg, snapshots, focus_ids, phi_star, origin_centroid, home_centroid,
                   world, det, phe, t_star):
    """Follow the branch's DISPLACED set (or the candidate, in-place, for control/sham) by diagnostic IDs.

    origin_centroid = where the followed set started; home_centroid = where it is expected after the
    branch operation (origin for control/sham; origin+delta for perturbed/placebo). Diagnostic IDs are used
    ONLY to follow constituents for measurement; physics/detection/tracking remain geometry-only.
    """
    rows = []
    F = frozenset(int(i) for i in focus_ids)
    origin = np.asarray(origin_centroid)
    home = np.asarray(home_centroid)
    for s in snapshots:
        if s.step == 0:
            continue  # relative step 0 == pre-intervention state
        ents = detect_entities(s.state, snapshot_step=s.step, time=s.time, world=world,
                               detection=det, phenotype_spec=phe)
        best_P = max((phenotype_similarity(phi_star, e.phenotype) for e in ents), default=0.0)
        carrier = _carrier(ents, F)
        if carrier is not None:
            carrier_P = phenotype_similarity(phi_star, carrier.phenotype)
            carrier_M = material_retention(F, carrier.particle_ids)
            carrier_size = len(carrier.particle_indices)
            carrier_dist_home = periodic_distance(carrier.centroid, home, world.box_size)
            carrier_dist_origin = periodic_distance(carrier.centroid, origin, world.box_size)
        else:
            carrier_P = carrier_M = 0.0
            carrier_size = 0
            carrier_dist_home = carrier_dist_origin = float("nan")

        def site_entity(site):
            near = [e for e in ents if periodic_distance(e.centroid, site, world.box_size) <= cfg.site_radius]
            return max(near, key=lambda e: phenotype_similarity(phi_star, e.phenotype)) if near else None
        origin_e = site_entity(origin)
        rows.append({
            "rel_step": s.step, "abs_step": t_star + s.step, "time": s.time,
            "best_P_anywhere": best_P,
            "carrier_P": carrier_P, "carrier_M": carrier_M, "carrier_size": carrier_size,
            "carrier_dist_home": carrier_dist_home, "carrier_dist_origin": carrier_dist_origin,
            "origin_site_P": (phenotype_similarity(phi_star, origin_e.phenotype) if origin_e else 0.0),
            "origin_site_M_vs_focus": (material_retention(F, origin_e.particle_ids) if origin_e else float("nan")),
            "origin_site_size": (len(origin_e.particle_indices) if origin_e else 0),
        })

    P = cfg.persist_p
    ms = cfg.min_entity_size
    sr = cfg.site_radius
    def ok(r):
        return r["carrier_size"] >= ms and r["carrier_P"] > P
    def at_home(r):
        d = r["carrier_dist_home"]
        return d == d and d <= sr  # not-nan and within site radius
    # longest consecutive run of organized-at-home (robust to the immediate post-displacement transient dip)
    longest = cur = 0
    for r in rows:
        if ok(r) and at_home(r):
            cur += 1; longest = max(longest, cur)
        else:
            cur = 0
    n = len(rows)
    late = rows[max(0, n - (n + 1) // 2):]  # last ~half of the window
    late_home_frac = (sum(1 for r in late if ok(r) and at_home(r)) / len(late)) if late else 0.0
    final_ok_home = bool(rows) and ok(rows[-1]) and at_home(rows[-1])
    reestablished = bool(late_home_frac >= 0.5 and final_ok_home)
    origin_regen = [r for r in rows if r["origin_site_P"] > P and (r["origin_site_M_vs_focus"] < cfg.material_low)]
    summary = {
        "n_post_snapshots": n,
        "best_P_max": max((r["best_P_anywhere"] for r in rows), default=0.0),
        "best_P_final": rows[-1]["best_P_anywhere"] if rows else 0.0,
        "carrier_organized_at_home_snapshots": sum(1 for r in rows if ok(r) and at_home(r)),
        "carrier_longest_consec_at_home": longest,
        "carrier_late_home_frac": late_home_frac,
        "carrier_reestablished_at_home": reestablished,
        "carrier_P_final": rows[-1]["carrier_P"] if rows else 0.0,
        "carrier_M_final": rows[-1]["carrier_M"] if rows else 0.0,
        "origin_regen_any": bool(origin_regen),
        "origin_regen_first_rel_step": (origin_regen[0]["rel_step"] if origin_regen else None),
        "origin_regen_count": len(origin_regen),
    }
    return rows, summary


def branch_lineage_flags(cfg, snapshots, world, det, phe, old_centroid):
    """Fresh tracker over the branch to expose alias structure (births/ambiguous/split/merge, old-site look-alike)."""
    _, _, trk = _specs(cfg)
    tracker = LineageTracker(trk, box_size=world.box_size)
    for s in snapshots:
        ents = detect_entities(s.state, snapshot_step=s.step, time=s.time, world=world,
                               detection=det, phenotype_spec=phe)
        tracker.update(ents, snapshot_step=s.step, time=s.time)
    counts = Counter(e.kind for e in tracker.events)
    births_after0 = [e for e in tracker.events if e.kind == "birth" and e.snapshot_step > 0]
    return {
        "events": dict(sorted(counts.items())),
        "births_after_start": len(births_after0),
        "ambiguous": counts.get("ambiguous_association", 0),
        "split": counts.get("split", 0),
        "merge": counts.get("merge", 0),
        "n_tracks": len(tracker.tracks),
    }


# --------------------------------------------------------------------------- orchestration

def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8"); return
    cols: list[str] = []
    seen: set[str] = set()
    for row in rows:  # stable union of keys (enrolled rows carry more columns than censored rows)
        for key in row:
            if key not in seen:
                seen.add(key); cols.append(key)
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=cols, restval=""); w.writeheader(); w.writerows(rows)


def _hash(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda: h.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def run_causal_experiment(*, output_dir: Path, experiment_id: str, git_commit: str,
                          config: CausalConfig, protocol_sha: str = "UNFROZEN") -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=False)
    world = _world(config)
    det, phe, _ = _specs(config)
    box = world.box_size
    delta = np.asarray(config.delta, dtype=np.float64)

    enroll_rows: list[dict[str, Any]] = []
    branch_rows: list[dict[str, Any]] = []
    traj_rows: list[dict[str, Any]] = []

    for law_index in config.laws:
        law = law_from_halton(law_index, config.n_types)
        for seed in config.seed_plan:
            enr, _, _ = enroll(config, law_index, seed)
            base = {"law_index": law_index, "seed": seed, "enrolled": enr.enrolled, "reason": enr.reason,
                    "first_eligible_start": enr.first_eligible_start, "first_eligible_end": enr.first_eligible_end,
                    "corroborating_cadences": json.dumps(list(enr.corroborating_cadences)),
                    "enroll_cadence": enr.enroll_cadence, "track_id": enr.track_id,
                    "candidate_size": enr.candidate_size, "prior_snapshots": enr.prior_snapshots,
                    "old_centroid_json": json.dumps(list(enr.old_centroid) if enr.old_centroid else None)}
            if not enr.enrolled:
                enroll_rows.append(base); continue

            S = enr.state
            C = frozenset(enr.candidate_ids)
            phi_star = enr.phi_star
            old_c = np.asarray(enr.old_centroid)
            new_c = (old_c + delta) % box
            init_disp = periodic_distance(new_c, old_c, box)

            # matched branches from the identical pre-intervention state S
            control_state = S.copy()
            sham_state = apply_displacement(S, enr.candidate_indices, (0.0, 0.0), box)
            perturbed_state = apply_displacement(S, enr.candidate_indices, config.delta, box)
            placebo_obs = largest_other_component(S, enr.candidate_indices, config, world, det, phe)
            placebo_idx = (tuple(int(i) for i in placebo_obs.particle_indices)
                           if placebo_obs is not None else None)
            placebo_state = (apply_displacement(S, placebo_idx, config.delta, box)
                             if placebo_idx is not None else None)

            # sham must equal control bit-for-bit (validated-reference / no-op identity)
            sham_identity = bool(np.array_equal(sham_state.positions, control_state.positions)
                                 and np.array_equal(sham_state.velocities, control_state.velocities))
            # perturbation must actually move the candidate off-site, conserving global quantities
            moved = float(np.max(np.abs(minimum_image(perturbed_state.positions - control_state.positions, box))))
            momentum_conserved = bool(np.allclose(perturbed_state.velocities.sum(0),
                                                  control_state.velocities.sum(0), atol=1e-12))
            types_conserved = bool(np.array_equal(np.sort(perturbed_state.types), np.sort(control_state.types)))

            run = RunSpec(seed=seed, dt=config.dt, steps=config.horizon_post,
                          snapshot_interval=config.base_cadence, backend="vectorized")
            branches = {"CONTROL": control_state, "SHAM": sham_state, "PERTURBED": perturbed_state}
            if placebo_state is not None:
                branches["PLACEBO"] = placebo_state

            # per-branch focus = the DISPLACED set (candidate for control/sham/perturbed; C' for placebo),
            # each measured against its OWN reference phenotype and its own origin/home site.
            from ..entities.detection import periodic_centroid
            focus = {
                "CONTROL":   (enr.candidate_ids, phi_star, old_c, old_c),
                "SHAM":      (enr.candidate_ids, phi_star, old_c, old_c),
                "PERTURBED": (enr.candidate_ids, phi_star, old_c, new_c),
            }
            if placebo_obs is not None:
                cprime = np.asarray(periodic_centroid(S.positions[np.asarray(placebo_idx)], box))
                focus["PLACEBO"] = (tuple(sorted(int(i) for i in placebo_obs.particle_ids)),
                                    placebo_obs.phenotype, cprime, (cprime + delta) % box)

            branch_summaries = {}
            for name, state0 in branches.items():
                snaps = simulate(state0, law, world, run)
                f_ids, f_phi, f_origin, f_home = focus[name]
                rows, summ = measure_branch(config, snaps, f_ids, f_phi, f_origin, f_home,
                                            world, det, phe, t_star=enr.first_eligible_end)
                flags = branch_lineage_flags(config, snaps, world, det, phe, old_c)
                branch_summaries[name] = summ
                brow = {**{k: base[k] for k in ("law_index", "seed", "first_eligible_end", "candidate_size")},
                        "branch": name,
                        "initial_centroid_displacement": (init_disp if name in ("PERTURBED", "PLACEBO") else 0.0),
                        "sham_equals_control": sham_identity, "perturb_max_abs_move": moved,
                        "momentum_conserved": momentum_conserved, "types_conserved": types_conserved,
                        **summ,
                        "lineage_events_json": json.dumps(flags["events"]),
                        "births_after_start": flags["births_after_start"], "ambiguous": flags["ambiguous"],
                        "split": flags["split"], "merge": flags["merge"]}
                branch_rows.append(brow)
                for r in rows:
                    traj_rows.append({"law_index": law_index, "seed": seed, "branch": name, **r})

            # comparative, robust classification (faithful to the frozen protocol decision rule)
            pert = branch_summaries["PERTURBED"]; ctrl = branch_summaries["CONTROL"]
            plac = branch_summaries.get("PLACEBO")
            plac_frac = plac["carrier_late_home_frac"] if plac else 0.0
            non_informative = init_disp <= config.tracker_distance
            catastrophic = (pert["carrier_organized_at_home_snapshots"] == 0
                            and pert["best_P_max"] <= config.persist_p)
            occupancy = pert["origin_regen_any"]
            # individuality signal: displaced candidate re-establishes organization at the NEW site,
            # exceeds a displaced random clump by a pre-declared margin, and the old site does not regenerate.
            margin = 0.25
            individuality = bool(pert["carrier_reestablished_at_home"]
                                 and (pert["carrier_late_home_frac"] - plac_frac) > margin
                                 and not occupancy)
            base.update({
                "init_centroid_displacement": init_disp, "sham_equals_control": sham_identity,
                "perturb_max_abs_move": moved, "momentum_conserved": momentum_conserved,
                "placebo_available": placebo_state is not None,
                "class_non_informative": non_informative, "class_catastrophic": catastrophic,
                "class_occupancy_alias": occupancy, "class_individuality_signal": individuality,
                "pert_reestablished": pert["carrier_reestablished_at_home"],
                "plac_reestablished": (plac["carrier_reestablished_at_home"] if plac else None),
                "pert_late_home_frac": pert["carrier_late_home_frac"],
                "ctrl_late_home_frac": ctrl["carrier_late_home_frac"],
                "plac_late_home_frac": plac_frac,
                "pert_longest_consec_home": pert["carrier_longest_consec_at_home"],
                "ctrl_longest_consec_home": ctrl["carrier_longest_consec_at_home"],
                "pert_origin_regen": occupancy, "pert_best_P_max": pert["best_P_max"],
            })
            enroll_rows.append(base)

    _write_csv(output_dir / "enrollment.csv", enroll_rows)
    _write_csv(output_dir / "branch_readouts.csv", branch_rows)
    _write_csv(output_dir / "post_intervention_trajectory.csv", traj_rows)

    enrolled = [r for r in enroll_rows if r["enrolled"]]
    by_law = {}
    for law_index in config.laws:
        law_enr = [r for r in enrolled if r["law_index"] == law_index]
        by_law[str(law_index)] = {
            "enrolled_seeds": [r["seed"] for r in law_enr],
            "censored_seeds": [r["seed"] for r in enroll_rows
                               if r["law_index"] == law_index and not r["enrolled"]],
            "n_enrolled": len(law_enr),
            "n_occupancy_alias": sum(1 for r in law_enr if r["class_occupancy_alias"]),
            "n_individuality_signal": sum(1 for r in law_enr if r["class_individuality_signal"]),
            "n_pert_reestablished": sum(1 for r in law_enr if r["pert_reestablished"]),
            "n_catastrophic": sum(1 for r in law_enr if r["class_catastrophic"]),
            "n_non_informative": sum(1 for r in law_enr if r["class_non_informative"]),
            "all_sham_equals_control": all(r["sham_equals_control"] for r in law_enr) if law_enr else None,
        }

    summary = {
        "experiment_id": experiment_id, "git_commit": git_commit, "protocol_sha": protocol_sha,
        "config": config.as_dict(), "n_enrolled_total": len(enrolled),
        "n_censored_total": len(enroll_rows) - len(enrolled), "by_law": by_law,
        "interpretation_boundary": (
            "First-eligible-endpoint-per-seed units. Counts are diagnostic, not probabilities. "
            "P and M are separate; no composite score. Apparent recovery that depends on ambiguous "
            "association, old-site regeneration with turnover constituents, or spatial occupancy is "
            "ALIAS-COMPATIBLE RECOVERY, not RECOVERY."),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    paths = sorted(p for p in output_dir.iterdir() if p.is_file())
    manifest = {
        "experiment_id": experiment_id, "git_commit": git_commit, "protocol_sha": protocol_sha,
        "code_version": "0.1.0", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "substrate": "particle_dynamics", "core_mechanism_version": "CORE_V0",
        "config": config.as_dict(), "world_spec": world.as_dict(),
        "dependencies": {"python": platform.python_version(), "numpy": version("numpy")},
        "output_sha256": {p.name: _hash(p) for p in paths},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return summary
