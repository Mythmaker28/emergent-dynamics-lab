"""EXP-RD-00: open reaction-diffusion substrate qualification tests."""

from __future__ import annotations

import numpy as np

from edlab.substrates.reaction_diffusion.engine import (GrayScottSpec, RDEngine, RDState, laplacian,
                                                        laplacian_reference)
from edlab.experiments.exp_rd_00 import rd_state, qualify, N_COHORTS, build_control_snapshots, run_control_through_stack

OPEN = GrayScottSpec(F=0.025, k=0.055)
CLOSED = GrayScottSpec(F=0.0, k=0.0)


def test_exact_closed_limit_conserves_material():
    st = rd_state(CLOSED, 1); m0 = st.total()
    snaps = RDEngine(CLOSED).simulate(st, 400, 50)
    assert max(abs(s.total() - m0) / m0 for s in snaps) < 1e-9      # F=k=0 -> closed, U+V conserved exactly
    assert CLOSED.is_closed


def test_open_system_is_actually_open():
    n = OPEN.size
    probe = RDState(np.full((n, n), 0.5), np.zeros((n, n)),
                    np.zeros((N_COHORTS, n, n)), np.zeros((N_COHORTS, n, n)))
    probe.CU[0] = probe.U.copy()
    s = RDEngine(OPEN).simulate(probe, 200, 50)
    assert (s[-1].total() - s[0].total()) / s[0].total() > 1e-3      # homogeneous feed adds material


def test_homogeneity_null_forcing_imposes_no_spatial_pattern():
    """A uniform state must stay EXACTLY uniform: the feed/removal cannot impose spatial structure."""
    n = OPEN.size
    uni = RDState(np.full((n, n), 0.5), np.full((n, n), 0.25),
                  np.zeros((N_COHORTS, n, n)), np.zeros((N_COHORTS, n, n)))
    uni.CU[0] = uni.U.copy(); uni.CV[0] = uni.V.copy()
    for s in RDEngine(OPEN).simulate(uni, 400, 100):
        assert float(np.ptp(s.U)) == 0.0 and float(np.ptp(s.V)) == 0.0


def test_tracers_partition_and_are_passive_and_feed_cohort_grows():
    st = rd_state(OPEN, 1)
    snaps = RDEngine(OPEN).simulate(st, 400, 50)
    assert max(float(np.max(np.abs(s.CU.sum(0) - s.U))) for s in snaps) < 1e-9
    assert max(float(np.max(np.abs(s.CV.sum(0) - s.V))) for s in snaps) < 1e-9
    assert float(snaps[-1].CU[-1].sum() + snaps[-1].CV[-1].sum()) > 0.0   # FEED (external-origin) cohort grows
    z = rd_state(OPEN, 1); z.CU = np.zeros_like(z.CU); z.CV = np.zeros_like(z.CV)
    sz = RDEngine(OPEN).simulate(z, 400, 50)
    for a, b in zip(snaps, sz):
        assert np.array_equal(a.U, b.U) and np.array_equal(a.V, b.V)     # cohorts never affect dynamics


def test_reference_path_agreement_and_determinism():
    st = rd_state(OPEN, 3)
    assert float(np.max(np.abs(laplacian(st.V) - laplacian_reference(st.V)))) <= 1e-12
    a = RDEngine(OPEN).simulate(rd_state(OPEN, 3), 200, 50)
    b = RDEngine(OPEN).simulate(rd_state(OPEN, 3), 200, 50)
    for x, y in zip(a, b):
        assert np.array_equal(x.V, y.V)


def test_positive_and_negative_measurement_controls():
    pos = run_control_through_stack(build_control_snapshots(active=True))
    neg = run_control_through_stack(build_control_snapshots(active=False))
    # recognized: persistent phenotype under constituent turnover
    assert pos["P_max"] > 0.8 and pos["M_min"] < 0.5 and pos["n_probe"] > 0
    # P/M ALONE cannot separate an imposed/frozen pattern from a real dissipative organization
    assert neg["P_max"] > 0.8 and neg["M_min"] < 0.5 and neg["n_probe"] > 0
    # the OPEN-SYSTEM rates DO separate them
    assert pos["mean_production"] > 1e-4 and pos["mean_activity"] > 1e-4
    assert neg["mean_production"] < 1e-9 and neg["mean_activity"] < 1e-9


def test_qualification_gate_passes():
    r = qualify()
    assert r["passed"], r["checks"]
