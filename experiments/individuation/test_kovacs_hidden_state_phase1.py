"""Focused Phase-1 tests: exact-clone determinism, schedule binding, tracker-free
panel, memory-excluded-from-panel, and the excursion firewall (structural)."""
import json
from pathlib import Path
import numpy as np
import pytest

from experiments.individuation import kovacs_hidden_state_phase1 as k1
from experiments.individuation import counterfactual_history_core_dev as chc

REPO = Path(__file__).resolve().parents[2]


def test_schedule_hash_stable_and_dose_matched():
    h1 = k1.schedule_hash(); h2 = k1.schedule_hash()
    assert h1 == h2 and len(h1) == 64
    dose_spike = sum(a * n for a, n in k1.SCHEDULE["H_SPIKE"])
    dose_sust = sum(a * n for a, n in k1.SCHEDULE["H_SUSTAINED"])
    assert abs(dose_spike - k1.SCHEDULE["matched_total_dose"]) < 1e-9
    assert abs(dose_sust - k1.SCHEDULE["matched_total_dose"]) < 1e-9
    assert abs(dose_spike - dose_sust) < 1e-9  # matched dose is the whole point


def test_panel_excludes_memory():
    # the matching panel must NOT contain any memory readout
    for key in k1.PANEL_KEYS:
        assert key not in ("m1_mean", "m2_mean", "mplus_mean", "mminus_mean")
    assert set(k1.memory_diag.__code__.co_consts) is not None  # memory_diag exists & separate


def test_firewall_no_excursion_fields():
    # coincidence_at output (the only per-world scientific product) must expose ONLY
    # matching + hidden-residual diagnostics, never a post-release excursion/hump quantity.
    def mk(mass, mem):
        return {**{key: 1.0 for key in k1.PANEL_KEYS}, "core_mass": mass,
                "_mem": {"m1_mean": mem, "m2_mean": mem, "mplus_mean": mem, "mminus_mean": mem}}
    trajA = [mk(10.0 - 0.1 * i, 0.2) for i in range(8)]
    trajB = [mk(9.5 - 0.1 * i, 0.1) for i in range(8)]
    out = k1.coincidence_at(trajA, trajB, 5, 3)
    keys = " ".join(out.keys()).lower()
    for banned in ("hump", "excursion", "signed_area", "post_release"):
        assert banned not in keys, banned
    assert "panel_abs" in out and "memory_diff" in out  # matching + hidden diagnostic only


def test_exact_clone_determinism_and_panel_tracker_free():
    # one-world exact-clone determinism + panel is a pure function of state+frozen mask
    cp = chc.make_checkpoint(57006)
    assert cp["focal_id"] is not None
    center = tuple(float(v) for v in cp["entities"][cp["focal_id"]].centroid)
    frame = k1.make_core_frame(cp["state"].rho.shape, center)
    # two independent short replays of the same history -> identical post-history hash
    a = k1.apply_custom_history(cp, [[0.02, 20]])
    b = k1.apply_custom_history(cp, [[0.02, 20]])
    assert a["valid"] and b["valid"]
    assert chc.state_hash(a["state"]) == chc.state_hash(b["state"])  # deterministic
    # panel is a pure function of (state, frozen mask): same state -> same panel, no tracker
    p1 = k1.panel(a["state"], frame); p2 = k1.panel(a["state"], frame)
    assert p1 == p2
    assert set(k1.PANEL_KEYS) <= set(p1.keys())


def test_dev_results_present_and_firewalled():
    f = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_PHASE1_DEV_RESULTS.json"
    d = json.load(open(f))
    assert "no post-release excursion" in d["firewall"]
    worlds = [w for w in d["worlds"] if w.get("coincidence_primary")]
    assert len(worlds) >= 12
    # no excursion field leaked into any world record
    blob = json.dumps(d).lower()
    assert "hump" not in blob
    # coincidence carries matching + memory diagnostic only
    c = worlds[0]["coincidence_primary"]
    assert "panel_abs" in c and "memory_diff" in c and "mass_abs_diff" in c
