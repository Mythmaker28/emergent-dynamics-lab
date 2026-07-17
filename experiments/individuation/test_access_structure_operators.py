"""Focused non-prospective tests for ACCESS-STRUCTURE-00 Phase 0.5 operators."""
from __future__ import annotations

import numpy as np
import pytest

from edlab.experiments.sc_iom.engine import IOMState
from experiments.individuation import access_structure_operators as ops


def synthetic_state(n: int = 32, step: int = 19) -> IOMState:
    x, y = np.indices((n, n))
    rho = 0.2 + 0.01 * x + 0.02 * y
    U = rho * (0.7 + 0.003 * x)
    V = rho * (0.4 + 0.002 * y)
    c = 0.3 + 0.005 * x + 0.001 * y
    nutrient = 0.5 + 0.002 * x + 0.004 * y
    cohorts = np.stack((0.45 * rho, 0.55 * rho))
    uptake = 0.01 + 0.0002 * x + 0.0001 * y
    memory = np.stack((rho * (0.1 + 0.001 * x), rho * (0.2 + 0.001 * y)))
    return IOMState(rho, U, V, c, nutrient, cohorts, uptake, memory, step)


def assert_exact(a: IOMState, b: IOMState) -> None:
    assert a.step == b.step
    for field in ops.STATE_FIELDS:
        assert np.array_equal(getattr(a, field), getattr(b, field)), field


def test_dev_seed_guard_refuses_unopened_namespaces():
    assert ops.require_dev_seed(50001) == 50001
    assert ops.require_dev_seed(50010) == 50010
    with pytest.raises(ValueError, match="50001-50010"):
        ops.require_dev_seed(50011)


def test_partition_is_exhaustive_disjoint_and_periodic():
    part = ops.partition_state((32, 32), (31.6, -0.4), core_radius=5, halo_width=1)
    part.validate()
    assert part.center == (0, 0)
    assert part.core[0, 0]
    assert part.core[31, 0]
    assert not (part.core & part.halo).any()
    assert (part.core | part.halo | part.environment).all()


def test_complete_physics_state_serialization_roundtrip_is_bit_exact():
    state = synthetic_state()
    payload = ops.serialize_state(state)
    restored = ops.deserialize_state(payload)
    assert_exact(state, restored)
    assert ops.state_sha256(state) == ops.state_sha256(restored)
    meta = ops.state_metadata(state)
    assert meta["persistent_rng_state"] is None
    assert set(meta["fields"]) == set(ops.STATE_FIELDS)


def test_noop_same_source_and_coordinate_shams_are_bit_exact():
    state = synthetic_state()
    part = ops.partition_state(state.rho.shape, (8, 9), core_radius=4)
    assert_exact(state, ops.no_op_continuation(state))
    assert_exact(state, ops.same_source_reinsert(state, part))
    assert_exact(state, ops.coordinate_transform_sham(state, part))


def test_within_world_swap_changes_only_two_cores_and_conserves_every_field_total():
    state = synthetic_state()
    part_a = ops.partition_state(state.rho.shape, (7, 8), core_radius=4)
    part_b = ops.partition_state(state.rho.shape, (23, 22), core_radius=4)
    crossed, record = ops.swap_cores(state, part_a, part_b)

    outside = ~(part_a.core | part_b.core)
    for field in ops.STATE_FIELDS:
        before = getattr(state, field)
        after = getattr(crossed, field)
        assert np.array_equal(before[..., outside], after[..., outside]), field
        assert np.allclose(
            before.sum(axis=(-2, -1)), after.sum(axis=(-2, -1)), rtol=2e-15, atol=2e-15
        ), field
    assert crossed.step == state.step

    for field in ops.STATE_FIELDS:
        shifted_a = np.roll(getattr(state, field), record.shift_a_to_b, axis=(-2, -1))
        shifted_b = np.roll(getattr(state, field), record.shift_b_to_a, axis=(-2, -1))
        assert np.array_equal(getattr(crossed, field)[..., part_b.core], shifted_a[..., part_b.core]), field
        assert np.array_equal(getattr(crossed, field)[..., part_a.core], shifted_b[..., part_a.core]), field


def test_same_source_through_exchange_kernel_is_exact():
    state = synthetic_state()
    part = ops.partition_state(state.rho.shape, (8, 9), core_radius=4)
    a, b, record = ops.exchange_cores(state, state, part, part)
    assert record.shift_a_to_b == (0, 0)
    assert_exact(state, a)
    assert_exact(state, b)


def test_cross_world_exchange_preserves_each_donor_core_without_scaling():
    state_a = synthetic_state()
    state_b = synthetic_state()
    state_b.rho = state_b.rho * 1.7
    state_b.U = state_b.U * 1.3
    part_a = ops.partition_state(state_a.rho.shape, (7, 8), core_radius=4)
    part_b = ops.partition_state(state_b.rho.shape, (23, 22), core_radius=4)
    a_receives_b, b_receives_a, record = ops.exchange_cores(state_a, state_b, part_a, part_b)
    shifted_a = np.roll(state_a.rho, record.shift_a_to_b, axis=(-2, -1))
    shifted_b = np.roll(state_b.rho, record.shift_b_to_a, axis=(-2, -1))
    assert np.array_equal(b_receives_a.rho[part_b.core], shifted_a[part_b.core])
    assert np.array_equal(a_receives_b.rho[part_a.core], shifted_b[part_a.core])
    pair_before = float(state_a.rho.sum() + state_b.rho.sum())
    pair_after = float(a_receives_b.rho.sum() + b_receives_a.rho.sum())
    assert np.isclose(pair_after, pair_before, rtol=2e-15, atol=2e-15)


def test_mismatched_scheduler_phase_is_refused():
    donor = synthetic_state(step=19)
    recipient = synthetic_state(step=20)
    a = ops.partition_state(donor.rho.shape, (8, 8), core_radius=4)
    b = ops.partition_state(donor.rho.shape, (24, 24), core_radius=4)
    with pytest.raises(ValueError, match="scheduler"):
        ops.exchange_cores(donor, recipient, a, b)
