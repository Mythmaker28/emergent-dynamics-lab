"""EXP_FL_00 qualification gate tests: mass-conservative Flow-Lenia + passive cohorts + field stack + EXP-REF-01."""

from __future__ import annotations

import numpy as np

from edlab.substrates.flow_lenia.engine import FlowLeniaSpec, FlowLeniaEngine, FlowLeniaState, flow_field
from edlab.experiments.exp_fl_00 import (
    RefFieldConfig, build_field_snapshots, run_field_stack, gaussian_blobs_state, qualify,
)

SPEC = FlowLeniaSpec(size=64)


def test_mass_conserved_and_nonnegative_and_cohort_partition():
    eng = FlowLeniaEngine(SPEC); st = gaussian_blobs_state(SPEC, 3)
    m0 = st.mass(); snaps = eng.simulate(st, 200, 10)
    assert max(abs(s.mass() - m0) / m0 for s in snaps) < 1e-9
    assert min(float(s.A.min()) for s in snaps) >= -1e-12
    assert max(float(np.max(np.abs(s.cohorts.sum(0) - s.A))) for s in snaps) < 1e-9


def test_passive_tracer_invariance_and_determinism():
    eng = FlowLeniaEngine(SPEC); st = gaussian_blobs_state(SPEC, 1)
    a = eng.simulate(FlowLeniaState(st.A.copy(), st.cohorts.copy()), 120, 10)
    b = eng.simulate(FlowLeniaState(st.A.copy(), st.cohorts.copy()), 120, 10)
    assert max(float(np.max(np.abs(x.A - y.A))) for x, y in zip(a, b)) == 0.0
    c = eng.simulate(FlowLeniaState(st.A.copy(), np.zeros((1, 64, 64))), 120, 10)
    assert max(float(np.max(np.abs(x.A - y.A))) for x, y in zip(a, c)) == 0.0   # tracers don't affect dynamics


def test_expref01_recognized_and_separated_on_field_stack():
    cfg = RefFieldConfig()
    ref = run_field_stack(cfg, build_field_snapshots(cfg, rotating=True))
    nul = run_field_stack(cfg, build_field_snapshots(cfg, rotating=False))
    assert ref["P_max_main"] > 0.8 and ref["M_min_main"] < 0.5 and ref["n_probe_positive_main"] > 0
    assert nul["n_probe_positive_main"] > 0                                   # P/M alone cannot separate
    assert ref["mean_abs_circulation"] > 0.02 and ref["mean_velocity_dispersion"] > 0.02
    assert nul["mean_abs_circulation"] < 1e-6 and nul["mean_velocity_dispersion"] < 1e-6


def test_qualification_gate_passes():
    result = qualify(SPEC)
    assert result["passed"], result["checks"]
