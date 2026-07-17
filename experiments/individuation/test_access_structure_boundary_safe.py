"""Focused DEV-only tests for ACCESS-STRUCTURE-00 Phase 0.6A operators."""
from __future__ import annotations

import numpy as np
import pytest

from experiments.individuation import access_structure_operators as ops
from experiments.individuation.test_access_structure_operators import assert_exact, synthetic_state


def _different_donor():
    donor = synthetic_state()
    x, y = np.indices(donor.rho.shape)
    donor.rho = donor.rho * (1.15 + 0.05 * np.sin(x / 3.0))
    donor.U = donor.U * (0.85 + 0.04 * np.cos(y / 4.0))
    donor.V = donor.V * 1.08
    donor.c = donor.c * (1.10 + 0.02 * np.sin(y / 5.0))
    donor.N = donor.N * 0.93
    donor.C = np.stack((0.30 * donor.rho, 0.70 * donor.rho))
    donor.Mf[0] = donor.rho * (0.42 + 0.02 * np.sin(x / 4.0))
    donor.Mf[1] = donor.rho * (-0.18 + 0.01 * np.cos(y / 3.0))
    donor.uptake = donor.uptake * 2.0
    return donor


def test_frozen_grid_contains_only_two_declared_families_and_four_configs():
    assert len(ops.BOUNDARY_SAFE_SPECS) == 4
    assert {spec.family for spec in ops.BOUNDARY_SAFE_SPECS} == {
        "recipient_interface_preserving_interior",
        "constrained_phase_consistent_projection",
    }
    assert [spec.name for spec in ops.BOUNDARY_SAFE_SPECS] == [
        "RIP_HARD_R9",
        "RIP_HARD_R8",
        "CPP_QUINTIC_R8",
        "CPP_QUINTIC_R7",
    ]


@pytest.mark.parametrize("spec", ops.BOUNDARY_SAFE_SPECS, ids=lambda spec: spec.name)
def test_boundary_safe_operator_balances_each_arm_and_changes_only_C(spec):
    recipient = synthetic_state()
    donor = _different_donor()
    part_rec = ops.partition_state(recipient.rho.shape, (8, 8), core_radius=10)
    part_don = ops.partition_state(donor.rho.shape, (24, 24), core_radius=10)
    result, record = ops.boundary_safe_transplant(
        recipient, donor, part_rec, part_don, spec, appended_tracers=0
    )

    for field in ops.BALANCED_PHYSICAL_FIELDS:
        before = float(getattr(recipient, field).sum())
        after = float(getattr(result, field).sum())
        assert abs(after - before) <= 1e-12 + 1e-10 * abs(before), field
        assert np.all(getattr(result, field) >= 0.0), field
    for field in ops.STATE_FIELDS:
        before = getattr(recipient, field)
        after = getattr(result, field)
        assert np.array_equal(before[..., ~part_rec.core], after[..., ~part_rec.core]), field
    assert np.max(np.abs(result.C.sum(axis=0) - result.rho)) <= 5e-11
    assert result.step == recipient.step
    assert np.array_equal(result.uptake, recipient.uptake)
    assert record["outside_C_change"] is False
    assert record["affected_radius"] <= spec.outer_radius


@pytest.mark.parametrize("spec", ops.BOUNDARY_SAFE_SPECS, ids=lambda spec: spec.name)
def test_protected_intensive_memory_is_exact_in_payload_core(spec):
    recipient = synthetic_state()
    donor = _different_donor()
    part_rec = ops.partition_state(recipient.rho.shape, (8, 8), core_radius=10)
    part_don = ops.partition_state(donor.rho.shape, (24, 24), core_radius=10)
    result, _ = ops.boundary_safe_transplant(
        recipient, donor, part_rec, part_don, spec, appended_tracers=0
    )
    shift = tuple(part_rec.center[i] - part_don.center[i] for i in range(2))
    donor_rho = np.roll(donor.rho, shift, axis=(-2, -1))
    donor_mf = np.roll(donor.Mf, shift, axis=(-2, -1))
    donor_m = donor_mf / np.maximum(donor_rho, 1e-12)[None]
    result_m = result.Mf / np.maximum(result.rho, 1e-12)[None]
    payload = (
        (part_rec.distance <= spec.inner_radius)
        & (donor_rho > 1e-4)
        & (result.rho > 1e-4)
    )
    assert payload.any()
    assert np.allclose(result_m[:, payload], donor_m[:, payload], rtol=0.0, atol=2e-15)


@pytest.mark.parametrize("spec", ops.BOUNDARY_SAFE_SPECS, ids=lambda spec: spec.name)
def test_same_source_active_operation_sham_is_exact(spec):
    state = synthetic_state()
    part = ops.partition_state(state.rho.shape, (8, 8), core_radius=10)
    result, record = ops.boundary_safe_transplant(
        state, state, part, part, spec, appended_tracers=0
    )
    assert_exact(state, result)
    assert record["changed_cells"] == 0


def test_quintic_transition_and_recipient_outer_edge_are_frozen():
    part = ops.partition_state((64, 64), (32, 32), core_radius=10)
    spec = next(item for item in ops.BOUNDARY_SAFE_SPECS if item.name == "CPP_QUINTIC_R8")
    weight = ops.boundary_safe_weights(part, spec)
    assert np.all(weight[part.distance <= 8.0] == 1.0)
    assert np.all(weight[part.distance >= 10.0] == 0.0)
    assert np.all((weight >= 0.0) & (weight <= 1.0))


def test_phase_mismatch_is_refused_before_projection():
    recipient = synthetic_state(step=19)
    donor = _different_donor()
    donor.step = 20
    part_rec = ops.partition_state(recipient.rho.shape, (8, 8), core_radius=10)
    part_don = ops.partition_state(donor.rho.shape, (24, 24), core_radius=10)
    with pytest.raises(ValueError, match="scheduler"):
        ops.boundary_safe_transplant(
            recipient,
            donor,
            part_rec,
            part_don,
            ops.BOUNDARY_SAFE_SPECS[0],
            appended_tracers=0,
        )
