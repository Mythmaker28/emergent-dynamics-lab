"""Validation of EXP-REF-01 construction + passive-tracer invariance (before the verdict)."""

from __future__ import annotations

import numpy as np

from edlab.experiments.exp_ref_01 import RefConfig, build_snapshots, run_through_frozen_stack
from edlab.entities.detection import detect_entities
from edlab.specs import DetectionSpec, PhenotypeSpec, WorldSpec

CFG = RefConfig()
W = WorldSpec(64, 3, box_size=1.0, initial_speed=0.04)
DET = DetectionSpec(0.11, 4); PHE = PhenotypeSpec(0.11, 0.25)


def test_reference_recognized_and_turns_over():
    r = run_through_frozen_stack(CFG, build_snapshots(CFG, rotating=True))
    assert r["single_entity_per_snapshot"] and r["n_tracks"] == 1
    assert r["main_track_obs"] >= 50
    assert r["P_max_main"] > 0.8            # frozen P, high continuity
    assert r["M_min_main"] < 0.5            # genuine constituent turnover
    assert r["n_probe_positive_main"] > 0   # recognized as probe-positive under turnover


def test_reference_separates_from_static_flux_on_frozen_observables():
    ref = run_through_frozen_stack(CFG, build_snapshots(CFG, rotating=True))
    nul = run_through_frozen_stack(CFG, build_snapshots(CFG, rotating=False))
    # raw P/M do NOT separate them (both probe-positive)
    assert nul["n_probe_positive_main"] > 0
    # frozen dynamical observables DO separate them
    assert ref["mean_abs_circulation"] > 0.02 and ref["mean_velocity_dispersion"] > 0.02
    assert nul["mean_abs_circulation"] < 1e-6 and nul["mean_velocity_dispersion"] < 1e-6


def test_passive_tracer_labels_do_not_affect_detection_or_phenotype():
    # permuting diagnostic IDs must not change detection geometry or the phenotype vector (only ID-based M could).
    snaps = build_snapshots(CFG, rotating=True)
    s = snaps[3].state
    ents = detect_entities(s, snapshot_step=3, time=0.06, world=W, detection=DET, phenotype_spec=PHE)
    perm = s.copy(); perm.ids = np.random.default_rng(0).permutation(perm.ids)
    ents2 = detect_entities(perm, snapshot_step=3, time=0.06, world=W, detection=DET, phenotype_spec=PHE)
    assert len(ents) == len(ents2) == 1
    assert np.allclose(ents[0].phenotype.vector, ents2[0].phenotype.vector)
    assert np.allclose(ents[0].centroid, ents2[0].centroid)


def test_determinism():
    a = run_through_frozen_stack(CFG, build_snapshots(CFG, rotating=True))
    b = run_through_frozen_stack(CFG, build_snapshots(CFG, rotating=True))
    assert a == b
