"""EXP-RD-00B: temporal-feed-cohort (pulse-chase) tracer tests."""

from __future__ import annotations

import numpy as np

from edlab.substrates.reaction_diffusion.engine import GrayScottSpec, RDEngine, TracerSpec
from edlab.experiments.exp_rd_00b import run_control, rd_state_t, OPEN


def test_temporal_feed_cohort_rotates():
    t = TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250)
    assert t.n_cohorts == 16 and t.cycle == 2000
    assert t.active_feed_cohort(0) == 8
    assert t.active_feed_cohort(250) == 9
    assert t.active_feed_cohort(2000) == 8            # wraps after a full cycle


def test_cohorts_partition_and_are_passive_with_temporal_feed():
    tr = TracerSpec()
    eng = RDEngine(OPEN, tr)
    snaps = eng.simulate(rd_state_t(OPEN, tr, 2), 600, 100)
    assert max(float(np.max(np.abs(s.CU.sum(0) - s.U))) for s in snaps) < 1e-9
    assert max(float(np.max(np.abs(s.CV.sum(0) - s.V))) for s in snaps) < 1e-9
    z = rd_state_t(OPEN, tr, 2); z.CU = np.zeros_like(z.CU); z.CV = np.zeros_like(z.CV)
    sz = eng.simulate(z, 600, 100)
    for a, b in zip(snaps, sz):
        assert np.array_equal(a.U, b.U) and np.array_equal(a.V, b.V)   # strictly passive


def test_control1_continued_turnover_is_detected_despite_full_feed_saturation():
    """Continuous throughput: the tracer must keep seeing turnover even when the structure is 100% feed-origin."""
    c1 = run_control(TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250), switch_to_closed=False)
    assert c1["feed_frac_end"] > 0.9          # material fully replaced by external matter (saturation regime)
    assert c1["median_late_M"] < 0.5          # ... and continued turnover is STILL registered


def test_control2_ceased_turnover_is_distinguishable():
    """One-time replacement then the exact closed limit: the tracer must report no further turnover."""
    tr = TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250)
    c1 = run_control(tr, switch_to_closed=False)
    c2 = run_control(tr, switch_to_closed=True)
    assert c2["median_late_M"] > 0.9
    assert (c2["median_late_M"] - c1["median_late_M"]) > 0.30     # discrimination


def test_legacy_single_permanent_feed_cohort_fails():
    """The old design saturates and cannot see continued turnover -- this is why it was replaced."""
    legacy = TracerSpec(n_spatial=8, n_temporal=1, tau_feed=10 ** 9)
    c1 = run_control(legacy, switch_to_closed=False)
    c2 = run_control(legacy, switch_to_closed=True)
    assert c1["feed_frac_end"] > 0.9
    assert c1["median_late_M"] > 0.5                               # blind: reports (almost) no turnover
    assert (c2["median_late_M"] - c1["median_late_M"]) < 0.30      # cannot discriminate C1 from C2
