"""EXP_FL_02 validation: isolated reservoir-exchange throughput mechanism."""

from __future__ import annotations

import numpy as np
import pytest

from edlab.substrates.flow_lenia.engine import FlowLeniaEngine, FlowLeniaState
from edlab.substrates.flow_lenia.engine_throughput import ThroughputSpec, ThroughputEngine
from edlab.experiments.exp_fl_00 import gaussian_blobs_state
from edlab.experiments.exp_fl_02 import throughput_state, throughput_law_from_halton, G_SPATIAL


@pytest.mark.parametrize("li", [0, 3, 11])
def test_exact_off_limit_reproduces_core_bitwise(li):
    spec, t_off = throughput_law_from_halton(li, on=False)
    base = gaussian_blobs_state(spec, 8001, n_cohorts=G_SPATIAL)
    core = FlowLeniaEngine(spec).simulate(FlowLeniaState(base.A.copy(), base.cohorts.copy()), 120, 10)
    thr = ThroughputEngine(spec, t_off).simulate(throughput_state(spec, t_off, 8001), 120, 10)
    for a, b in zip(core, thr):
        assert np.array_equal(a.A, b.A)          # exchange_rate=0 -> exact current-core limit


def test_global_mass_conservation_and_partitions_and_nonnegativity():
    spec, t_on = throughput_law_from_halton(3, on=True)
    snaps = ThroughputEngine(spec, t_on).simulate(throughput_state(spec, t_on, 8001), 200, 10)
    m0 = snaps[0].total_mass()
    assert max(abs(s.total_mass() - m0) / m0 for s in snaps) < 1e-9      # A+R globally conserved
    assert max(float(np.max(np.abs(s.cohorts_A.sum(0) - s.A))) for s in snaps) < 1e-9
    assert max(float(np.max(np.abs(s.cohorts_R.sum(0) - s.R))) for s in snaps) < 1e-9
    assert min(float(s.A.min()) for s in snaps) >= -1e-12
    assert min(float(s.R.min()) for s in snaps) >= -1e-12


def test_determinism_and_tracers_do_not_affect_dynamics():
    spec, t_on = throughput_law_from_halton(5, on=True)
    eng = ThroughputEngine(spec, t_on)
    a = eng.simulate(throughput_state(spec, t_on, 8002), 120, 10)
    b = eng.simulate(throughput_state(spec, t_on, 8002), 120, 10)
    assert max(float(np.max(np.abs(x.A - y.A))) for x, y in zip(a, b)) == 0.0
    # zeroing the cohort labels must not change A or R (cohorts are passive labels only)
    st = throughput_state(spec, t_on, 8002)
    st.cohorts_A = np.zeros_like(st.cohorts_A); st.cohorts_R = np.zeros_like(st.cohorts_R)
    c = eng.simulate(st, 120, 10)
    assert max(float(np.max(np.abs(x.A - y.A))) for x, y in zip(a, c)) == 0.0
    assert max(float(np.max(np.abs(x.R - y.R))) for x, y in zip(a, c)) == 0.0


def test_throughput_positive_control_tracers_measure_real_turnover():
    """ON must push reservoir-origin mass INTO the active field; OFF must not."""
    spec, t_on = throughput_law_from_halton(3, on=True)
    _, t_off = throughput_law_from_halton(3, on=False)
    on = ThroughputEngine(spec, t_on).simulate(throughput_state(spec, t_on, 8001), 300, 10)[-1]
    off = ThroughputEngine(spec, t_off).simulate(throughput_state(spec, t_off, 8001), 300, 10)[-1]
    res_on = on.cohorts_A[G_SPATIAL:].sum() / max(on.cohorts_A.sum(), 1e-12)
    res_off = off.cohorts_A[G_SPATIAL:].sum() / max(off.cohorts_A.sum(), 1e-12)
    assert res_on > 0.10       # real material throughput into the active field
    assert res_off < 1e-9      # no exchange in the OFF limit
