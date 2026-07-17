from dataclasses import replace

import numpy as np
import pytest

from edlab.experiments.sc_iom.engine import IOMState
from edlab.experiments.sc_mcm import config as MCM_CONFIG
from edlab.substrates.scaffold.engine import ScaffoldEngine
from experiments.individuation import access_structure_noswap_operators as ns
from experiments.individuation import causal_confirm as cc
from experiments.individuation import downstream_order_reader_instrumentation as inst
from experiments.individuation.access_structure_operators import state_sha256
from experiments.individuation.turnover_diag_engine import DiagEngine


def synthetic_state() -> tuple[IOMState, np.ndarray]:
    n = MCM_CONFIG.SPEC.size
    yy, xx = np.ogrid[:n, :n]
    support = (yy - n // 2) ** 2 + (xx - n // 2) ** 2 <= 8**2
    rho = np.zeros((n, n), dtype=float)
    rho[support] = 0.35
    U = 0.30 * rho
    V = 0.20 * rho
    c = np.full((n, n), 0.1, dtype=float)
    N = np.full((n, n), 0.8, dtype=float)
    C = np.zeros((MCM_CONFIG.TRACER.n_cohorts, n, n), dtype=float)
    C[0] = rho
    uptake = np.zeros((n, n), dtype=float)
    Mf = np.zeros((2, n, n), dtype=float)
    Mf[0, support] = rho[support] * -0.05
    Mf[1, support] = rho[support] * 0.20
    return IOMState(rho, U, V, c, N, C, uptake, Mf, 100), support


def assert_state_fields_equal(left: IOMState, right: IOMState, *, except_fields=()):
    for field in ns.STATE_FIELDS:
        if field not in except_fields:
            assert np.array_equal(getattr(left, field), getattr(right, field)), field
    assert left.step == right.step


def test_passive_logger_is_state_identical_and_records_exact_engine_fluxes():
    state, _ = synthetic_state()
    base_engine = DiagEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True,
    )
    expected = {
        axis: base_engine._face_flux(state.rho, state.c, axis).copy()
        for axis in (-2, -1)
    }
    base = base_engine.step(state.copy())

    logged_engine = inst.PassiveFluxDiagEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True,
    )
    logged = logged_engine.step(state.copy())

    assert state_sha256(base) == state_sha256(logged)
    records = logged_engine.face_flux_records
    assert tuple(record.axis for record in records) == (-2, -1)
    assert tuple(record.input_step for record in records) == (state.step, state.step)
    for record in records:
        assert np.array_equal(record.flux, expected[record.axis])
        assert not record.flux.flags.writeable
        assert not np.shares_memory(record.flux, expected[record.axis])
        with pytest.raises(ValueError):
            record.flux[0, 0] = 1.0

    logged_engine.clear_face_flux_records()
    assert logged_engine.face_flux_records == ()


def test_passive_logger_is_state_identical_with_the_qualified_noswap_clamp():
    state, _ = synthetic_state()
    ring = np.zeros_like(state.rho, dtype=bool)
    ring[8, 8:20] = True
    ys, xs = np.where(ring)
    frame = ns._read_ring_frame(state, ys, xs, (0, 0))

    def driver(label):
        copied = {field: values.copy() for field, values in frame.items()}
        return ns.BoundaryDriver(ring.copy(), [copied], label=label)

    base_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=driver("base"), up_ref_zero=True,
    )
    logged_engine = inst.PassiveFluxNoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=driver("logged"), up_ref_zero=True,
    )
    assert state_sha256(base_engine.step(state.copy())) == state_sha256(
        logged_engine.step(state.copy())
    )
    assert tuple(record.axis for record in logged_engine.face_flux_records) == (-2, -1)


def test_revised_schedule_uses_one_common_settle_source_only_lam_and_common_response():
    initial, _ = synthetic_state()
    ring = np.zeros_like(initial.rho, dtype=bool)
    ring[8, 8:20] = True
    ys, xs = np.where(ring)
    common_frame = ns._read_ring_frame(initial, ys, xs, (0, 0))

    def common_driver(nsteps: int, label: str):
        frames = [
            {field: values.copy() for field, values in common_frame.items()}
            for _ in range(nsteps)
        ]
        return ns.BoundaryDriver(ring.copy(), frames, label=label)

    settle_engine = ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=common_driver(40, "common-settle"), up_ref_zero=True,
    )
    settled = initial.copy()
    for _ in range(40):
        settled = settle_engine.step(settled)

    source_inputs = {
        lam: settled.copy()
        for lam in (0.15, 0.0)
    }
    assert len({state_sha256(state) for state in source_inputs.values()}) == 1

    source_outputs = {}
    for lam, source_input in source_inputs.items():
        source_mem = replace(cc.MEM_INTACT, lam_minus=lam)
        source_engine = ns.NoSwapClampEngine(
            MCM_CONFIG.SPEC, source_mem, MCM_CONFIG.TRACER,
            driver=common_driver(1, f"common-source-{lam}"), up_ref_zero=True,
        )
        source_outputs[lam] = source_engine.step(source_input)

    assert_state_fields_equal(source_outputs[0.15], source_outputs[0.0], except_fields=("c",))
    assert not np.array_equal(source_outputs[0.15].c, source_outputs[0.0].c)

    geometry = inst.integer_disk_ramp_geometry(
        settled.rho.shape, (settled.rho.shape[0] // 2, settled.rho.shape[1] // 2), 10,
    )
    for source_lam, source_output in source_outputs.items():
        for arm in (-1, 0, 1):
            response_input = source_output.copy()
            response_input.c = inst.apply_matched_c_ramp(
                source_output.c, geometry, arm=arm, epsilon_c=0.01,
            )
            assert_state_fields_equal(response_input, source_output, except_fields=("c",))

            response_engine = inst.PassiveFluxNoSwapClampEngine(
                MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
                driver=common_driver(1, f"common-response-{source_lam}-{arm}"),
                up_ref_zero=True,
            )
            response_engine.step(response_input)
            assert response_engine.mem.lam_minus == pytest.approx(0.15)
            assert tuple(record.axis for record in response_engine.face_flux_records) == (-2, -1)
            assert all(record.input_step == source_output.step for record in response_engine.face_flux_records)
        assert source_lam in (0.0, 0.15)


def test_matched_ramp_geometry_is_nonnegative_symmetric_and_mass_matched():
    geometry = inst.integer_disk_ramp_geometry((64, 64), (32, 32), 10)
    assert int(geometry.core.sum()) == 317
    assert int(inst.positive_face_masks(geometry.core).internal.sum()) == 296
    assert float(geometry.signed_x.sum()) == pytest.approx(0.0, abs=1e-12)
    assert np.max(np.abs(geometry.signed_x)) == pytest.approx(1.0)

    base = np.full((64, 64), 0.2)
    arms = {
        arm: inst.apply_matched_c_ramp(base, geometry, arm=arm, epsilon_c=0.01)
        for arm in (-1, 0, 1)
    }
    totals = [(arms[arm] - base).sum() for arm in (-1, 0, 1)]
    np.testing.assert_allclose(totals, [3.17, 3.17, 3.17], atol=1e-12, rtol=1e-10)
    np.testing.assert_allclose(
        arms[1] - arms[0], -(arms[-1] - arms[0]), atol=1e-12, rtol=1e-10,
    )
    assert all(np.min(arm) >= 0.0 for arm in arms.values())


def test_internal_face_flux_sum_equals_first_moment_increment_on_closed_fixture():
    flux = np.arange(5 * 7, dtype=float).reshape(5, 7) / 100.0
    flux[:, -1] = 0.0
    terms = inst.closed_first_moment_terms(flux, dt=0.1, axis=-1)
    assert terms.first_moment_increment == pytest.approx(
        terms.internal_face_flux_integral, abs=1e-12, rel=1e-10,
    )
    assert terms.residual == pytest.approx(0.0, abs=1e-12)

    open_flux = flux.copy()
    open_flux[2, -1] = 0.25
    with pytest.raises(ValueError, match="zero wrap-boundary flux"):
        inst.closed_first_moment_terms(open_flux, dt=0.1, axis=-1)


def test_boundary_flux_is_diagnosed_and_does_not_enter_the_internal_endpoint():
    core = np.zeros((8, 9), dtype=bool)
    core[2:6, 2:7] = True
    masks = inst.positive_face_masks(core, axis=-1)
    flux = np.zeros(core.shape, dtype=float)
    flux[masks.internal] = 0.2
    mass = 4.0
    dt = 0.1
    baseline = inst.mass_specific_internal_x_face_flux_sum(flux, core, mass=mass, dt=dt)

    outgoing_index = tuple(np.argwhere(masks.outgoing_boundary)[0])
    incoming_index = tuple(np.argwhere(masks.incoming_boundary)[0])
    flux[outgoing_index] = 0.7
    flux[incoming_index] = 0.4
    with_boundary = inst.mass_specific_internal_x_face_flux_sum(flux, core, mass=mass, dt=dt)
    partition = inst.diagnostic_face_flux_partition(flux, core, axis=-1)

    assert with_boundary == baseline
    assert partition.outgoing_boundary == pytest.approx(0.7)
    assert partition.incoming_boundary == pytest.approx(0.4)
    delta_rho = -dt * (flux - np.roll(flux, 1, axis=-1))
    assert float(delta_rho[core].sum()) == pytest.approx(
        dt * (partition.incoming_boundary - partition.outgoing_boundary)
    )


def test_matched_ramp_response_can_reverse_sign_under_saturation():
    geometry = inst.integer_disk_ramp_geometry((64, 64), (32, 32), 10)
    rho = np.zeros((64, 64), dtype=float)
    rho[32, 41:43] = 0.4
    mass = float(rho[geometry.core].sum())
    engine = ScaffoldEngine(MCM_CONFIG.SPEC, MCM_CONFIG.TRACER)

    def paired_response(c_i: float, c_p: float) -> float:
        base_c = np.zeros((64, 64), dtype=float)
        base_c[32, 40] = max(0.0, c_i - (c_p - c_i))
        base_c[32, 41] = c_i
        base_c[32, 42] = c_p
        values = {}
        for arm in (-1, 1):
            ramped = inst.apply_matched_c_ramp(
                base_c, geometry, arm=arm, epsilon_c=0.01,
            )
            flux_x = engine._face_flux(rho, ramped, -1)
            values[arm] = inst.mass_specific_internal_x_face_flux_sum(
                flux_x, geometry.core, mass=mass, dt=MCM_CONFIG.SPEC.dt,
            )
        return (values[1] - values[-1]) / 2.0

    ordinary = paired_response(0.20, 0.21)
    saturated = paired_response(10.0, 11.0)
    assert ordinary > 0.0
    assert saturated < 0.0
