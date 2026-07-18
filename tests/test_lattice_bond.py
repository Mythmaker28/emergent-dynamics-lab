"""Deterministic synthetic qualification for the Stage-A lattice-bond engine.

These fixtures are hand-built mechanics checks.  They contain no seed, search,
scientific entity, history field, or behavioral response.
"""

from __future__ import annotations

from dataclasses import fields, replace
import math

import numpy as np
import pytest

from edlab.substrates.lattice_bond.engine import (
    AdmissibilityError,
    FaceIntervention,
    FaceTerms,
    LatticeBondEngine,
    LatticeBondSpec,
    LatticeBondState,
    StepLedger,
)


ABS = 1e-12
REL = 1e-10


def _within(actual: np.ndarray | float, reference: np.ndarray | float) -> bool:
    a = np.asarray(actual, dtype=np.float64)
    r = np.asarray(reference, dtype=np.float64)
    return bool(np.all(np.abs(a - r) <= ABS + REL * np.abs(r)))


def _heterogeneous_state() -> LatticeBondState:
    m = np.array(
        [
            [0.05, 0.20, 0.55, 0.90, 0.35],
            [0.75, 0.40, 0.10, 0.65, 0.25],
            [0.30, 0.85, 0.45, 0.15, 0.70],
            [0.60, 0.00, 0.95, 0.50, 0.80],
        ],
        dtype=np.float64,
    )
    n = np.array(
        [
            [0.95, 0.15, 0.70, 0.30, 0.55],
            [0.25, 0.80, 0.05, 0.90, 0.40],
            [0.60, 0.35, 0.85, 0.10, 0.75],
            [0.45, 1.00, 0.20, 0.65, 0.50],
        ],
        dtype=np.float64,
    )
    b = np.empty((2, 4, 5), dtype=np.float64)
    b[0] = np.array(
        [
            [0.00, 0.20, 0.40, 0.60, 0.80],
            [0.10, 0.30, 0.50, 0.70, 0.90],
            [0.90, 0.70, 0.50, 0.30, 0.10],
            [0.80, 0.60, 0.40, 0.20, 0.00],
        ],
        dtype=np.float64,
    )
    b[1] = np.array(
        [
            [0.15, 0.35, 0.55, 0.75, 0.95],
            [0.05, 0.25, 0.45, 0.65, 0.85],
            [0.85, 0.65, 0.45, 0.25, 0.05],
            [0.95, 0.75, 0.55, 0.35, 0.15],
        ],
        dtype=np.float64,
    )
    return LatticeBondState(m, n, b, step=3)


def _square_state() -> LatticeBondState:
    base = _heterogeneous_state()
    return LatticeBondState(base.m[:, :4].copy(), base.n[:, :4].copy(), base.b[:, :, :4].copy(), base.step)


def _assert_dataclass_arrays_close(a: object, b: object) -> None:
    for item in fields(a):
        av, bv = getattr(a, item.name), getattr(b, item.name)
        if isinstance(av, np.ndarray):
            assert _within(av, bv), item.name
        else:
            assert _within(float(av), float(bv)), item.name


def _transform_bonds(b: np.ndarray, coordinate_map, *, oriented: bool = False) -> np.ndarray:
    """Transform an undirected positive-face representation on a square lattice."""

    size = b.shape[1]
    out = np.empty_like(b)
    assigned = np.zeros_like(b, dtype=bool)
    for axis in (0, 1):
        for y in range(size):
            for x in range(size):
                yp = (y + 1) % size if axis == 0 else y
                xp = (x + 1) % size if axis == 1 else x
                ay, ax = coordinate_map(y, x, size)
                by, bx = coordinate_map(yp, xp, size)
                dy, dx = (by - ay) % size, (bx - ax) % size
                if (dy, dx) == (1, 0):
                    key = (0, ay, ax)
                    sign = 1.0
                elif (dy, dx) == (size - 1, 0):
                    key = (0, by, bx)
                    sign = -1.0
                elif (dy, dx) == (0, 1):
                    key = (1, ay, ax)
                    sign = 1.0
                elif (dy, dx) == (0, size - 1):
                    key = (1, by, bx)
                    sign = -1.0
                else:  # pragma: no cover - guard for an invalid lattice symmetry helper
                    raise AssertionError((axis, y, x, (ay, ax), (by, bx)))
                out[key] = (sign if oriented else 1.0) * b[axis, y, x]
                assigned[key] = True
    assert assigned.all()
    return out


def _rot90_state(state: LatticeBondState) -> LatticeBondState:
    coord = lambda y, x, n: (n - 1 - x, y)
    return LatticeBondState(np.rot90(state.m), np.rot90(state.n), _transform_bonds(state.b, coord), state.step)


def _reflect_state(state: LatticeBondState) -> LatticeBondState:
    coord = lambda y, x, n: (y, n - 1 - x)
    return LatticeBondState(np.fliplr(state.m), np.fliplr(state.n), _transform_bonds(state.b, coord), state.step)


def _transform_face_array(array: np.ndarray, coordinate_map, *, oriented: bool = False) -> np.ndarray:
    return _transform_bonds(array, coordinate_map, oriented=oriented)


def _active_bond_components(b: np.ndarray, threshold: float = 0.8) -> list[frozenset[tuple[int, int]]]:
    """Fixture-only graph diagnostic; it is not imported by or exposed from the engine."""

    h, w = b.shape[1:]
    adjacency: dict[tuple[int, int], set[tuple[int, int]]] = {}
    for axis in (0, 1):
        for y in range(h):
            for x in range(w):
                if b[axis, y, x] < threshold:
                    continue
                other = ((y + 1) % h, x) if axis == 0 else (y, (x + 1) % w)
                adjacency.setdefault((y, x), set()).add(other)
                adjacency.setdefault(other, set()).add((y, x))
    components: list[frozenset[tuple[int, int]]] = []
    unseen = set(adjacency)
    while unseen:
        root = min(unseen)
        stack = [root]
        component: set[tuple[int, int]] = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(adjacency[node] - component)
        unseen -= component
        components.append(frozenset(component))
    return sorted(components, key=lambda component: min(component))


def test_field_registry_state_validation_and_no_size_parameter():
    spec = LatticeBondSpec()
    assert "size" not in spec.__dataclass_fields__
    assert set(LatticeBondState.__dataclass_fields__) == {"m", "n", "b", "step"}
    state = _heterogeneous_state()
    state.validate(spec)
    with pytest.raises(AdmissibilityError):
        LatticeBondState(state.m.astype(np.float32), state.n, state.b).validate(spec)
    with pytest.raises(AdmissibilityError):
        LatticeBondState(state.m, state.n, np.zeros((4, *state.shape), dtype=np.float64)).validate(spec)


def test_uniform_state_remains_spatially_uniform_under_uniform_local_law():
    state = LatticeBondState(
        np.full((4, 5), 0.4, dtype=np.float64),
        np.full((4, 5), 0.8, dtype=np.float64),
        np.full((2, 4, 5), 0.3, dtype=np.float64),
    )
    result = LatticeBondEngine().step(state)
    assert float(np.ptp(result.state.m)) == 0.0
    assert float(np.ptp(result.state.n)) == 0.0
    assert float(np.ptp(result.state.b)) == 0.0


def test_isolated_two_cell_exchange_uses_one_antisymmetric_face_value():
    spec = LatticeBondSpec(kappa_m=0.0, k_on=0.0, k_off=0.0, k_tension=0.0)
    n = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float64)
    state = LatticeBondState(np.zeros((2, 2), dtype=np.float64), n, np.zeros((2, 2, 2), dtype=np.float64))
    result = LatticeBondEngine(spec).step(state)
    ledger = result.ledger
    assert ledger.resource_natural[1, 0, 0] > 0.0
    assert ledger.resource_natural[1, 0, 1] < 0.0
    assert np.array_equal(ledger.resource_missing_from_delta, -ledger.resource_missing_to_delta)
    assert result.state.n[0, 0] < state.n[0, 0]
    assert result.state.n[0, 1] > state.n[0, 1]
    assert abs(float(result.state.n.sum() - state.n.sum())) <= ABS


def test_periodic_global_and_heterogeneous_multiface_conservation():
    result = LatticeBondEngine().step(_heterogeneous_state())
    assert abs(result.ledger.matter_residual) <= ABS + REL * abs(result.ledger.initial_matter)
    assert abs(result.ledger.energy_residual) <= ABS + REL * abs(result.ledger.initial_stored_energy)
    assert np.array_equal(result.ledger.matter_missing_from_delta, -result.ledger.matter_missing_to_delta)
    assert np.array_equal(result.ledger.resource_missing_from_delta, -result.ledger.resource_missing_to_delta)
    assert _within(
        result.ledger.weakening_heat + result.ledger.dissolution_heat,
        result.ledger.rupture_heat,
    )
    assert _within(
        result.ledger.gross_weakening_release + result.ledger.gross_dissolution_release,
        result.ledger.gross_rupture_release,
    )


def test_vectorized_and_independent_scalar_reference_paths_agree():
    engine = LatticeBondEngine()
    state = _heterogeneous_state()
    vector = engine.step(state, backend="vectorized")
    reference = engine.step(state, backend="reference")
    assert _within(vector.state.m, reference.state.m)
    assert _within(vector.state.n, reference.state.n)
    assert _within(vector.state.b, reference.state.b)
    _assert_dataclass_arrays_close(vector.ledger, reference.ledger)


def test_positivity_and_capacity_at_frozen_representable_timestep_limit():
    base = LatticeBondSpec()
    spec = replace(base, dt=base.admissible_dt_limit)
    checker = np.indices((4, 4)).sum(axis=0) % 2
    states = [
        LatticeBondState(
            (checker * spec.m_max).astype(np.float64),
            (checker * spec.n_max).astype(np.float64),
            np.zeros((2, 4, 4), dtype=np.float64),
        ),
        LatticeBondState(
            np.full((4, 4), spec.m_max, dtype=np.float64),
            np.full((4, 4), spec.n_max, dtype=np.float64),
            np.zeros((2, 4, 4), dtype=np.float64),
        ),
    ]
    for state in states:
        next_state = LatticeBondEngine(spec).step(state).state
        assert float(np.min(next_state.m)) >= 0.0
        assert float(np.max(next_state.m)) <= spec.m_max
        assert float(np.min(next_state.n)) >= 0.0
        assert float(np.max(next_state.n)) <= spec.n_max
        assert float(np.min(next_state.b)) >= 0.0
        assert float(np.max(next_state.b)) <= 1.0
    with pytest.raises(AdmissibilityError):
        replace(base, dt=math.nextafter(base.analytic_dt_bound, math.inf))


def test_exhaustive_two_by_two_extreme_states_are_admissible_at_timestep_limit():
    base = LatticeBondSpec()
    spec = replace(base, dt=base.admissible_dt_limit)
    engine = LatticeBondEngine(spec)
    for m_bits in range(16):
        m = np.array([(m_bits >> bit) & 1 for bit in range(4)], dtype=np.float64).reshape(2, 2)
        for n_bits in range(16):
            n = np.array([(n_bits >> bit) & 1 for bit in range(4)], dtype=np.float64).reshape(2, 2)
            state = LatticeBondState(m, n, np.zeros((2, 2, 2), dtype=np.float64))
            next_state = engine.step(state).state
            assert 0.0 <= float(np.min(next_state.m)) <= float(np.max(next_state.m)) <= spec.m_max
            assert 0.0 <= float(np.min(next_state.n)) <= float(np.max(next_state.n)) <= spec.n_max
            assert 0.0 <= float(np.min(next_state.b)) <= float(np.max(next_state.b)) <= 1.0


def test_bond_creation_has_exact_endpoint_fuel_debit_and_stored_energy_gain():
    spec = LatticeBondSpec(kappa_m=0.0, resource_diffusivity=0.0, k_off=0.0, k_tension=0.0)
    state = LatticeBondState(
        np.full((3, 3), 0.8, dtype=np.float64),
        np.full((3, 3), 0.9, dtype=np.float64),
        np.zeros((2, 3, 3), dtype=np.float64),
    )
    result = LatticeBondEngine(spec).step(state)
    ledger = result.ledger
    assert np.all(ledger.gross_formation > 0.0)
    assert np.array_equal(ledger.gross_rupture, np.zeros_like(ledger.gross_rupture))
    assert _within(ledger.formation_fuel, spec.epsilon_b * (result.state.b - state.b))
    assert _within(float(state.n.sum() - result.state.n.sum()), float(ledger.formation_fuel.sum()))
    assert abs(ledger.energy_residual) <= ABS


def test_bond_rupture_release_and_weakening_dissolution_partition_are_exact():
    uniform = LatticeBondState(
        np.full((3, 3), 0.5, dtype=np.float64),
        np.full((3, 3), 0.8, dtype=np.float64),
        np.full((2, 3, 3), 0.7, dtype=np.float64),
    )
    dissolve_spec = LatticeBondSpec(
        kappa_m=0.0,
        resource_diffusivity=0.0,
        k_on=0.0,
        k_off=0.2,
        k_tension=0.0,
    )
    dissolved = LatticeBondEngine(dissolve_spec).step(uniform)
    assert np.array_equal(dissolved.state.n, uniform.n)
    assert np.all(dissolved.state.b < uniform.b)
    assert np.array_equal(dissolved.ledger.weakening_heat, np.zeros_like(uniform.b))
    assert _within(dissolved.ledger.dissolution_heat, dissolved.ledger.rupture_heat)
    assert abs(dissolved.ledger.energy_residual) <= ABS

    contrast = uniform.copy()
    contrast.m[::2, ::2] = 0.9
    contrast.m[1::2, 1::2] = 0.1
    weaken_spec = replace(dissolve_spec, k_off=0.0, k_tension=0.3)
    weakened = LatticeBondEngine(weaken_spec).step(contrast)
    assert float(weakened.ledger.weakening_heat.sum()) > 0.0
    assert np.array_equal(weakened.ledger.dissolution_heat, np.zeros_like(uniform.b))
    assert _within(weakened.ledger.weakening_heat, weakened.ledger.rupture_heat)


def test_simultaneous_on_off_maintenance_work_is_explicitly_recycled():
    state = LatticeBondState(
        np.full((3, 3), 0.7, dtype=np.float64),
        np.full((3, 3), 0.9, dtype=np.float64),
        np.full((2, 3, 3), 0.5, dtype=np.float64),
    )
    ledger = LatticeBondEngine().step(state).ledger
    assert float(ledger.maintenance_recycled_work.sum()) > 0.0
    assert _within(
        ledger.gross_formation_work,
        ledger.formation_fuel + ledger.maintenance_recycled_work,
    )
    assert _within(
        ledger.gross_rupture_release,
        ledger.rupture_heat + ledger.maintenance_recycled_work,
    )
    assert abs(ledger.energy_residual) <= ABS


def test_zero_full_and_intermediate_bond_conductance_limits():
    spec = LatticeBondSpec(k_on=0.0, k_off=0.0, k_tension=0.0)
    base = _square_state()
    terms: dict[float, FaceTerms] = {}
    for bond in (0.0, 0.5, 1.0):
        state = LatticeBondState(base.m, base.n, np.full_like(base.b, bond), base.step)
        terms[bond] = LatticeBondEngine(spec).face_terms(state)
    assert np.array_equal(terms[1.0].matter_natural, np.zeros_like(base.b))
    assert _within(terms[0.5].matter_natural, 0.5 * terms[0.0].matter_natural)
    assert _within(
        terms[1.0].resource_natural,
        spec.resource_leak_floor * terms[0.0].resource_natural,
    )
    mid = spec.resource_leak_floor + 0.5 * (1.0 - spec.resource_leak_floor)
    assert _within(terms[0.5].resource_natural, mid * terms[0.0].resource_natural)


def test_translation_covariance_is_exact_for_vectorized_path():
    engine = LatticeBondEngine()
    state = _heterogeneous_state()
    shift = (1, -2)
    shifted = LatticeBondState(
        np.roll(state.m, shift, axis=(0, 1)),
        np.roll(state.n, shift, axis=(0, 1)),
        np.roll(state.b, shift, axis=(1, 2)),
        state.step,
    )
    base_result = engine.step(state)
    shifted_result = engine.step(shifted)
    assert np.array_equal(shifted_result.state.m, np.roll(base_result.state.m, shift, axis=(0, 1)))
    assert np.array_equal(shifted_result.state.n, np.roll(base_result.state.n, shift, axis=(0, 1)))
    assert np.array_equal(shifted_result.state.b, np.roll(base_result.state.b, shift, axis=(1, 2)))


@pytest.mark.parametrize(
    ("state_transform", "coord"),
    [
        (_rot90_state, lambda y, x, n: (n - 1 - x, y)),
        (_reflect_state, lambda y, x, n: (y, n - 1 - x)),
    ],
)
def test_rotation_and_reflection_covariance_with_operation_tolerance(state_transform, coord):
    engine = LatticeBondEngine()
    state = _square_state()
    base = engine.step(state)
    transformed = engine.step(state_transform(state))
    expected = state_transform(base.state)
    assert _within(transformed.state.m, expected.m)
    assert _within(transformed.state.n, expected.n)
    assert _within(transformed.state.b, expected.b)
    for name in (
        "matter_natural",
        "resource_natural",
        "bond_cue",
        "bond_tension",
        "gross_formation",
        "gross_rupture",
    ):
        assert _within(
            getattr(transformed.ledger, name),
            _transform_face_array(
                getattr(base.ledger, name),
                coord,
                oriented=name in {"matter_natural", "resource_natural"},
            ),
        ), name


def test_open_gate_is_byte_identical_to_ordinary_execution():
    engine = LatticeBondEngine()
    state = _heterogeneous_state()
    ordinary = engine.step(state)
    explicit_open = engine.step(state, FaceIntervention.open(state.shape))
    assert ordinary.canonical_bytes() == explicit_open.canonical_bytes()


def test_face_plans_compose_commute_and_are_idempotent_for_binary_cuts():
    shape = (4, 5)
    a = FaceIntervention.from_cuts(shape, matter_faces=[(0, 1, 2)], resource_faces=[(1, 2, 3)])
    b = FaceIntervention.from_cuts(shape, matter_faces=[(1, 0, 4)], resource_faces=[(0, 3, 1)])
    assert a.compose(b).canonical_bytes() == b.compose(a).canonical_bytes()
    assert a.compose(a).canonical_bytes() == a.canonical_bytes()
    with pytest.raises(ValueError):
        a.matter_scale.setflags(write=True)
    with pytest.raises(ValueError):
        a.resource_scale.setflags(write=True)
    state = _heterogeneous_state()
    engine = LatticeBondEngine()
    assert engine.step(state, a.compose(b)).canonical_bytes() == engine.step(state, b.compose(a)).canonical_bytes()


def test_symmetric_face_cut_changes_only_declared_preexisting_flux_and_logs_missing_pair():
    engine = LatticeBondEngine()
    state = _heterogeneous_state()
    face = (1, 1, 2)
    before = state.canonical_bytes()
    cut = FaceIntervention.from_cuts(state.shape, matter_faces=[face], resource_faces=[face])
    assert state.canonical_bytes() == before
    opened = engine.step(state)
    closed = engine.step(state, cut)
    assert closed.ledger.matter_active[face] == 0.0
    assert closed.ledger.resource_active[face] == 0.0
    assert closed.ledger.matter_missing[face] == closed.ledger.matter_natural[face]
    assert closed.ledger.resource_missing[face] == closed.ledger.resource_natural[face]
    mask = np.ones(state.face_shape, dtype=bool)
    mask[face] = False
    assert np.array_equal(closed.ledger.matter_active[mask], opened.ledger.matter_active[mask])
    assert np.array_equal(closed.ledger.resource_active[mask], opened.ledger.resource_active[mask])
    assert np.any(opened.ledger.r_on > 0.0)
    assert np.any(opened.ledger.r_off > 0.0)
    assert np.array_equal(closed.state.b, opened.state.b)
    for name in (
        "bond_cue",
        "bond_tension",
        "r_on",
        "r_off",
        "gross_formation",
        "gross_rupture",
        "gross_formation_work",
        "gross_rupture_release",
        "gross_weakening_release",
        "gross_dissolution_release",
        "maintenance_recycled_work",
        "formation_fuel",
        "rupture_heat",
        "weakening_heat",
        "dissolution_heat",
    ):
        assert np.array_equal(getattr(closed.ledger, name), getattr(opened.ledger, name)), name
    assert np.array_equal(closed.ledger.matter_missing_from_delta, -closed.ledger.matter_missing_to_delta)
    assert np.array_equal(closed.ledger.resource_missing_from_delta, -closed.ledger.resource_missing_to_delta)
    assert closed.ledger.controller_onset_energy_jump == 0.0
    assert abs(closed.ledger.matter_residual) <= ABS
    assert abs(closed.ledger.energy_residual) <= ABS


def test_no_preferred_size_same_local_state_gives_same_face_law():
    engine = LatticeBondEngine()
    values: list[tuple[float, ...]] = []
    for size in (4, 8):
        state = LatticeBondState(
            np.full((size, size), 0.6, dtype=np.float64),
            np.full((size, size), 0.7, dtype=np.float64),
            np.full((2, size, size), 0.4, dtype=np.float64),
        )
        terms = engine.face_terms(state)
        values.append(
            tuple(
                float(array[0, 0, 0])
                for array in (
                    terms.matter_natural,
                    terms.resource_natural,
                    terms.bond_cue,
                    terms.bond_tension,
                    terms.bond_next,
                )
            )
        )
    assert values[0] == values[1]


def test_dissolution_leakage_percolation_split_and_merge_are_representable():
    shape = (4, 4)
    percolating = np.zeros((2, *shape), dtype=np.float64)
    percolating[1, 0, :] = 1.0
    components = _active_bond_components(percolating)
    assert components == [frozenset((0, x) for x in range(shape[1]))]
    assert percolating[1, 0, -1] == 1.0  # explicit periodic wrap face

    split = np.zeros_like(percolating)
    split[1, 1, 0:3] = 1.0
    assert len(_active_bond_components(split)) == 1
    split[1, 1, 1] = 0.0
    assert len(_active_bond_components(split)) == 2
    split[1, 1, 1] = 1.0
    assert len(_active_bond_components(split)) == 1

    dissolve_spec = LatticeBondSpec(
        dt=1.0,
        kappa_m=0.0,
        resource_diffusivity=0.0,
        k_on=0.0,
        k_off=5.0,
        k_tension=0.0,
    )
    state = LatticeBondState(
        np.full(shape, 0.4, dtype=np.float64),
        np.full(shape, 0.8, dtype=np.float64),
        percolating,
    )
    dissolved = LatticeBondEngine(dissolve_spec).step(state)
    assert _active_bond_components(dissolved.state.b) == []
    leak_terms = LatticeBondEngine(replace(dissolve_spec, dt=0.5, resource_diffusivity=0.1, k_off=0.0)).face_terms(
        LatticeBondState(state.m, _square_state().n, percolating)
    )
    assert float(np.max(np.abs(leak_terms.resource_natural[percolating == 1.0]))) > 0.0


def test_inert_static_shell_is_mechanically_inert_not_an_individuality_result():
    shape = (6, 6)
    shell = np.zeros((2, *shape), dtype=np.float64)
    shell[0, 1, 2:4] = 1.0
    shell[0, 3, 2:4] = 1.0
    shell[1, 2:4, 1] = 1.0
    shell[1, 2:4, 3] = 1.0
    spec = LatticeBondSpec(
        kappa_m=0.0,
        resource_diffusivity=0.0,
        k_on=0.0,
        k_off=0.0,
        k_tension=0.0,
    )
    state = LatticeBondState(
        np.full(shape, 0.5, dtype=np.float64),
        np.full(shape, 0.5, dtype=np.float64),
        shell,
    )
    engine = LatticeBondEngine(spec)
    result = engine.step(state)
    assert result.state.canonical_bytes() != state.canonical_bytes()  # clock advances
    assert np.array_equal(result.state.m, state.m)
    assert np.array_equal(result.state.n, state.n)
    assert np.array_equal(result.state.b, state.b)
    assert not hasattr(engine, "detect") and not hasattr(engine, "individuality")


def test_active_open_pattern_has_flux_without_a_boundary_or_scientific_response():
    state = _square_state()
    state.b[:] = 0.0
    engine = LatticeBondEngine(replace(LatticeBondSpec(), k_on=0.0, k_off=0.0, k_tension=0.0))
    result = engine.step(state)
    assert float(np.max(np.abs(result.ledger.matter_active))) > 0.0
    assert float(np.max(np.abs(result.ledger.resource_active))) > 0.0
    assert _active_bond_components(state.b) == []
    assert set(result.state.__dataclass_fields__) == {"m", "n", "b", "step"}
    assert all("response" not in item.name and "fitness" not in item.name for item in fields(StepLedger))
