"""AXIS-TRANSPOSE-EQUIVARIANCE-01S — mechanical facts about the lattice-bond stack.

Every fixture in this file is handcrafted: explicit literal arrays, or explicit
deterministic integer patterns over an index grid.  There is no scientific seed,
no parameter sweep and no fixture family.  The one pseudo-random stream that
appears (``_rejection_stream``) is a *numerical* device used solely to exhibit
that a declared admissible set has positive finite Lebesgue measure; it is
labelled as such and it is not a scientific seed.

The transpose operator ``T`` used throughout is:

    state         ->  LatticeBondState(m.T, n.T, stack([b[1].T, b[0].T]), step)
    face field A  ->  stack([A[1].T, A[0].T])
    intervention  ->  FaceIntervention(T_faces(matter_scale), T_faces(resource_scale))
    mask M        ->  M.T

Nothing here is a scientific outcome.  Every number is a mechanical fact about
code that already exists; the timing section is explicitly an engineering cost
fact and nothing else.
"""

from __future__ import annotations

from dataclasses import fields
import math
from pathlib import Path
import time

import numpy as np
import pytest

from edlab.substrates.lattice_bond.engine import (
    AdmissibilityError,
    FaceIntervention,
    LatticeBondEngine,
    LatticeBondSpec,
    LatticeBondState,
)
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import (
    MEASUREMENT_FRAME_DIRECTORY,
    MeasurementSpec,
    run_measurement_bridge,
)


TOL = 1e-15
DETECTOR = DetectorSpec(matter_threshold=0.45, min_cells=3)
TRACKER = TrackerSpec()


# ======================================================================================
# module-level helpers: the definitions this file establishes facts about
# ======================================================================================


def T_faces(array: np.ndarray) -> np.ndarray:
    """``T`` on a (2,H,W) face field: swap the two face axes and transpose each."""

    return np.stack([np.asarray(array[1]).T, np.asarray(array[0]).T])


def T_state(state: LatticeBondState) -> LatticeBondState:
    """``T`` on a state."""

    return LatticeBondState(
        np.ascontiguousarray(state.m.T),
        np.ascontiguousarray(state.n.T),
        np.ascontiguousarray(T_faces(state.b)),
        int(state.step),
    )


def T_intervention(plan: FaceIntervention) -> FaceIntervention:
    """``T`` on a face intervention."""

    return FaceIntervention(
        np.stack([plan.matter_scale[1].T, plan.matter_scale[0].T]),
        np.stack([plan.resource_scale[1].T, plan.resource_scale[0].T]),
    )


def T_mask(mask: np.ndarray) -> np.ndarray:
    """``T`` on a boolean 2-D mask."""

    return np.asarray(mask).T


def internal_faces(mask: np.ndarray, axis: int) -> np.ndarray:
    """Internal faces of ``mask`` along ``axis`` (periodic)."""

    return np.asarray(mask) & np.roll(np.asarray(mask), -1, axis=axis)


def _exact_mean(values: np.ndarray) -> float:
    """Order-independent mean: ``math.fsum`` rounds the exact sum exactly once."""

    flat = np.ravel(np.asarray(values, dtype=np.float64))
    if flat.size == 0:
        raise ValueError("mean of an empty face set is undefined")
    return math.fsum(float(v) for v in flat) / float(flat.size)


def Q(state: LatticeBondState, mask: np.ndarray) -> float:
    """``mean(b[0][F0]) - mean(b[1][F1])`` over the internal faces of ``mask``.

    Undefined (``ValueError``) if either internal-face set is empty.
    """

    f0 = internal_faces(mask, 0)
    f1 = internal_faces(mask, 1)
    if not f0.any() or not f1.any():
        raise ValueError("Q is undefined: an internal-face set is empty")
    return _exact_mean(state.b[0][f0]) - _exact_mean(state.b[1][f1])


def _circular_mean(coords: np.ndarray, period: int) -> float:
    """Standard circular (angle-method) mean on a ring of circumference ``period``."""

    values = [float(v) for v in np.ravel(coords)]
    scale = 2.0 * math.pi / float(period)
    sin_bar = math.fsum(math.sin(scale * v) for v in values) / float(len(values))
    cos_bar = math.fsum(math.cos(scale * v) for v in values) / float(len(values))
    return (math.atan2(sin_bar, cos_bar) / scale) % float(period)


def _minimum_image(delta: float, period: int) -> float:
    return (delta + 0.5 * period) % float(period) - 0.5 * period


def S(mask: np.ndarray) -> float:
    """Shape anisotropy ``(I_yy - I_xx)/(I_yy + I_xx)`` from the MASK ALONE.

    ``I_yy = sum dy^2`` and ``I_xx = sum dx^2`` over the mask's cells, taken about
    the circular-mean centroid with minimum-image (torus) displacements.
    Undefined (``ValueError``) when ``I_yy + I_xx == 0``.
    """

    mask = np.asarray(mask, dtype=bool)
    height, width = mask.shape
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        raise ValueError("S is undefined for an empty mask")
    cy = _circular_mean(ys, height)
    cx = _circular_mean(xs, width)
    i_yy = math.fsum(_minimum_image(float(v) - cy, height) ** 2 for v in ys)
    i_xx = math.fsum(_minimum_image(float(v) - cx, width) ** 2 for v in xs)
    if i_yy + i_xx == 0.0:
        raise ValueError("S is undefined: the second-moment trace vanishes")
    return (i_yy - i_xx) / (i_yy + i_xx)


def transpose_cells(cells, width: int) -> frozenset:
    """Map linear cell indices ``y*W + x`` of a SQUARE lattice to ``x*W + y``."""

    return frozenset(int(c % width) * width + int(c // width) for c in cells)


def quotient(frame_components, state: LatticeBondState):
    """Sorted multiset of ``(frozenset(cells), round(Q,12), round(S,12))``.

    Carries NO component index and NO track id.  An entity for which ``Q`` or ``S``
    is undefined is SKIPPED, exactly as the definition permits.  Skipping is itself
    transpose-symmetric: the axis-0 internal-face set of a mask is the axis-1
    internal-face set of its transpose, so an entity is skipped for ``x`` iff its
    image is skipped for ``T(x)``.
    """

    items = []
    for component in frame_components:
        mask = component.mask()
        try:
            entry = (
                frozenset(int(c) for c in component.cells),
                round(Q(state, mask), 12),
                round(S(mask), 12),
            )
        except ValueError:
            continue
        items.append(entry)
    return sorted(items, key=lambda item: (sorted(item[0]), item[1], item[2]))


# ======================================================================================
# handcrafted fixtures (no RNG, no seed)
# ======================================================================================


def _woven_state(size: int) -> LatticeBondState:
    """A handcrafted, deliberately axis-asymmetric square lattice.

    Every field is an explicit integer pattern over the index grid divided by an
    explicit integer, so the values are exactly representable and the lattice is
    reproducible by inspection.
    """

    yy, xx = np.mgrid[0:size, 0:size]
    m = (((yy * 3 + xx * 5) % 7) / 8.0).astype(np.float64)
    n = (((yy * 2 + xx * 11) % 9) / 16.0).astype(np.float64)
    b = np.stack(
        [
            (((yy + 2 * xx) % 5) / 8.0).astype(np.float64),
            (((3 * yy + xx) % 4) / 16.0).astype(np.float64),
        ]
    )
    return LatticeBondState(m, n, np.ascontiguousarray(b), 0)


def _literal_4x4_state() -> LatticeBondState:
    """A fully literal 4x4 lattice, written out cell by cell."""

    m = np.array(
        [
            [0.00, 0.25, 0.50, 0.75],
            [0.75, 0.00, 0.25, 0.50],
            [0.50, 0.75, 0.00, 0.25],
            [0.25, 0.50, 0.75, 0.00],
        ],
        dtype=np.float64,
    )
    n = np.array(
        [
            [0.500, 0.625, 0.250, 0.125],
            [0.125, 0.500, 0.625, 0.250],
            [0.750, 0.125, 0.500, 0.625],
            [0.625, 0.750, 0.125, 0.500],
        ],
        dtype=np.float64,
    )
    b0 = np.array(
        [
            [0.5, 0.0, 0.25, 0.125],
            [0.0, 0.25, 0.5, 0.0],
            [0.125, 0.5, 0.0, 0.25],
            [0.25, 0.125, 0.0, 0.5],
        ],
        dtype=np.float64,
    )
    b1 = np.array(
        [
            [0.0, 0.125, 0.0, 0.5],
            [0.25, 0.0, 0.125, 0.0],
            [0.5, 0.25, 0.0, 0.125],
            [0.0, 0.5, 0.25, 0.0],
        ],
        dtype=np.float64,
    )
    return LatticeBondState(m, n, np.stack([b0, b1]), 0)


def _symmetric_block_state(size: int = 8) -> LatticeBondState:
    """A T-invariant matter block with a deliberately T-asymmetric bond field."""

    m = np.zeros((size, size), dtype=np.float64)
    m[2:6, 2:6] = 1.0
    n = np.full((size, size), 0.8, dtype=np.float64)
    b = np.zeros((2, size, size), dtype=np.float64)
    b[0, 2:6, 2:6] = 0.6
    return LatticeBondState(m, n, b, 0)


def _two_blob_state(size: int = 8) -> LatticeBondState:
    """Two handcrafted blobs of DIFFERENT shape, placed so the index order flips.

    Blob A is a 2x3 block at rows 0-1 / cols 3-5 (smallest linear index 3); blob B
    is a 2x2 block at rows 3-4 / cols 0-1 (smallest linear index 24).  Transposing
    swaps which blob owns the smaller linear index, and ``detect_components`` orders
    components by exactly that smallest linear index.
    """

    m = np.zeros((size, size), dtype=np.float64)
    m[0:2, 3:6] = 1.0
    m[3:5, 0:2] = 0.9
    n = np.full((size, size), 0.7, dtype=np.float64)
    b = np.zeros((2, size, size), dtype=np.float64)
    b[0, 0:2, 3:6] = 0.5
    b[1, 3:5, 0:2] = 0.3
    return LatticeBondState(m, n, b, 0)


def _rect_state(height: int = 5, width: int = 8) -> LatticeBondState:
    yy, xx = np.mgrid[0:height, 0:width]
    m = (((yy * 3 + xx * 5) % 7) / 8.0).astype(np.float64)
    n = (((yy * 2 + xx * 11) % 9) / 16.0).astype(np.float64)
    b = np.stack(
        [
            (((yy + 2 * xx) % 5) / 8.0).astype(np.float64),
            (((3 * yy + xx) % 4) / 16.0).astype(np.float64),
        ]
    )
    return LatticeBondState(m, n, np.ascontiguousarray(b), 0)


SQUARE_SIZES = (4, 6, 9)


def _square_fixtures():
    return [_literal_4x4_state(), _woven_state(6), _woven_state(9)]


def _state_residual(left: LatticeBondState, right: LatticeBondState) -> float:
    return max(
        float(np.max(np.abs(left.m - right.m))),
        float(np.max(np.abs(left.n - right.n))),
        float(np.max(np.abs(left.b - right.b))),
    )


# ======================================================================================
# A. involution and equivariance
# ======================================================================================


def test_fact01_transpose_is_an_exact_involution_on_states_interventions_and_masks():
    for state in _square_fixtures() + [_symmetric_block_state(), _two_blob_state()]:
        back = T_state(T_state(state))
        assert np.array_equal(back.m, state.m)
        assert np.array_equal(back.n, state.n)
        assert np.array_equal(back.b, state.b)
        assert back.step == state.step
        assert _state_residual(back, state) == 0.0

    shape = (6, 6)
    plan = FaceIntervention.from_cuts(
        shape, matter_faces=[(0, 1, 2), (0, 3, 4)], resource_faces=[(1, 2, 0)]
    )
    back_plan = T_intervention(T_intervention(plan))
    assert np.array_equal(back_plan.matter_scale, plan.matter_scale)
    assert np.array_equal(back_plan.resource_scale, plan.resource_scale)

    mask = np.zeros((6, 6), dtype=bool)
    mask[1:4, 2:5] = True
    mask[5, 0] = True
    assert np.array_equal(T_mask(T_mask(mask)), mask)


def test_fact02_law_has_no_per_axis_field_so_transpose_acts_trivially_on_it():
    names = tuple(item.name for item in fields(LatticeBondSpec))
    assert names == (
        "dt",
        "m_max",
        "n_max",
        "kappa_m",
        "theta_m",
        "theta_n",
        "resource_diffusivity",
        "resource_leak_floor",
        "epsilon_b",
        "k_on",
        "k_off",
        "k_tension",
    )
    forbidden = ("axis", "_x", "_y", "row", "col", "horiz", "vert", "along")
    for name in names:
        lowered = name.lower()
        for token in forbidden:
            assert token not in lowered, f"{name!r} looks per-axis"
    # theta_m / theta_n index the two FIELDS (matter, resource), not the two axes.
    assert "theta_m" in names and "theta_n" in names
    assert not any(name.endswith(("_0", "_1")) for name in names)


@pytest.mark.parametrize("backend", ["vectorized", "reference"])
def test_fact03_single_step_is_transpose_equivariant_on_both_backends(backend, capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    worst = 0.0
    for state in _square_fixtures():
        left = T_state(engine.step(state, backend=backend).state)
        right = engine.step(T_state(state), backend=backend).state
        residual = _state_residual(left, right)
        worst = max(worst, residual)
        assert residual <= TOL, (state.shape, backend, residual)
        assert left.step == right.step
    with capsys.disabled():
        print(f"\n[fact03] backend={backend} max abs residual over m,n,b = {worst!r}")


@pytest.mark.parametrize("backend", ["vectorized", "reference"])
def test_fact04_multistep_equivariance_is_cumulatively_exact(backend, capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    steps = 25
    worst = 0.0
    for state in _square_fixtures():
        plain = state
        transposed = T_state(state)
        for _ in range(steps):
            plain = engine.step(plain, backend=backend).state
            transposed = engine.step(transposed, backend=backend).state
            residual = _state_residual(T_state(plain), transposed)
            worst = max(worst, residual)
            assert residual <= TOL
    with capsys.disabled():
        print(
            f"\n[fact04] backend={backend} steps={steps} "
            f"cumulative max abs residual = {worst!r}"
        )


@pytest.mark.parametrize("backend", ["vectorized", "reference"])
def test_fact05_equivariance_holds_under_a_non_self_transpose_intervention(backend, capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    worst = 0.0
    for size in (6, 9):
        state = _woven_state(size)
        plan = FaceIntervention.from_cuts(
            (size, size),
            matter_faces=[(0, 1, 2), (0, 3, 4), (1, 0, 5)],
            resource_faces=[(1, 2, 0), (0, 4, 1)],
        )
        transposed_plan = T_intervention(plan)
        assert not np.array_equal(plan.matter_scale, transposed_plan.matter_scale)
        assert not np.array_equal(plan.resource_scale, transposed_plan.resource_scale)

        left = T_state(engine.step(state, plan, backend=backend).state)
        right = engine.step(T_state(state), transposed_plan, backend=backend).state
        residual = _state_residual(left, right)
        worst = max(worst, residual)
        assert residual <= TOL
    with capsys.disabled():
        print(f"\n[fact05] backend={backend} max abs residual = {worst!r}")


LEDGER_FACE_CHANNELS = (
    "matter_natural",
    "matter_active",
    "matter_missing",
    "bond_cue",
    "resource_natural",
    "r_on",
    "r_off",
    "gross_formation",
    "gross_rupture",
    "formation_fuel",
)


def test_fact06_ledger_face_channels_are_transpose_equivariant(capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    size = 6
    state = _woven_state(size)
    plan = FaceIntervention.from_cuts(
        (size, size), matter_faces=[(0, 1, 2), (1, 4, 3)], resource_faces=[(1, 2, 0)]
    )
    plain = engine.step(state, plan).ledger
    transposed = engine.step(T_state(state), T_intervention(plan)).ledger
    worst = {}
    for channel in LEDGER_FACE_CHANNELS:
        residual = float(
            np.max(np.abs(T_faces(getattr(plain, channel)) - getattr(transposed, channel)))
        )
        worst[channel] = residual
        assert residual <= TOL, (channel, residual)
    # the cell-shaped affinity channel transposes as a plain 2-D field
    affinity_residual = float(np.max(np.abs(plain.affinity.T - transposed.affinity)))
    assert affinity_residual <= TOL
    with capsys.disabled():
        print(f"\n[fact06] ledger residuals = {worst!r} affinity={affinity_residual!r}")


# ======================================================================================
# B. Q and S
# ======================================================================================


def _threshold_mask(state: LatticeBondState) -> np.ndarray:
    return np.asarray(state.m >= DETECTOR.matter_threshold, dtype=bool)


def _handcrafted_q_fixtures():
    """(state, mask) pairs with non-empty internal faces on both axes."""

    pairs = []
    for state in _square_fixtures():
        mask = np.ones(state.shape, dtype=bool)
        pairs.append((state, mask))
    block = _symmetric_block_state()
    mask = np.zeros(block.shape, dtype=bool)
    mask[2:6, 2:6] = True
    pairs.append((block, mask))
    woven = _woven_state(6)
    ragged = np.zeros(woven.shape, dtype=bool)
    ragged[0:3, 1:5] = True
    ragged[4:6, 0:2] = True
    pairs.append((woven, ragged))
    return pairs


def test_fact07_Q_is_odd_under_transpose(capsys):
    # N5: the oddness of Q on these handcrafted fixtures holds BIT-EXACTLY, not merely
    # to 1e-15.  The assertion below is ``==`` rather than a tolerance because the exact
    # form is what actually passes; ``worst`` is reported and is measured to be 0.0.
    worst = 0.0
    for state, mask in _handcrafted_q_fixtures():
        left = Q(T_state(state), T_mask(mask))
        right = -Q(state, mask)
        worst = max(worst, abs(left - right))
        assert left == right  # exact
    assert worst == 0.0
    with capsys.disabled():
        print(f"\n[fact07] max |Q(Tx,TM) + Q(x,M)| = {worst!r} (exact equality asserted)")


def test_fact08_Q_vanishes_on_transpose_invariant_state_and_mask(capsys):
    results = []

    # (i) explicit symmetric block with b[0] == b[1].T
    size = 8
    m = np.zeros((size, size), dtype=np.float64)
    m[2:6, 2:6] = 1.0
    n = np.full((size, size), 0.8, dtype=np.float64)
    b0 = np.zeros((size, size), dtype=np.float64)
    b0[2:6, 2:6] = np.array(
        [
            [0.5, 0.25, 0.125, 0.0],
            [0.0, 0.5, 0.25, 0.125],
            [0.125, 0.0, 0.5, 0.25],
            [0.25, 0.125, 0.0, 0.5],
        ],
        dtype=np.float64,
    )
    symmetric = LatticeBondState(
        np.ascontiguousarray((m + m.T) / 2.0),
        np.ascontiguousarray((n + n.T) / 2.0),
        np.stack([b0, np.ascontiguousarray(b0.T)]),
        0,
    )
    assert np.array_equal(symmetric.b[0], symmetric.b[1].T)
    mask = np.zeros((size, size), dtype=bool)
    mask[2:6, 2:6] = True
    assert np.array_equal(mask, mask.T)
    results.append(("explicit_symmetric_block", Q(symmetric, mask)))

    # (ii) a handcrafted asymmetric lattice symmetrised componentwise: (x + T(x))/2
    raw = _woven_state(6)
    transposed = T_state(raw)
    sym = LatticeBondState(
        np.ascontiguousarray((raw.m + transposed.m) / 2.0),
        np.ascontiguousarray((raw.n + transposed.n) / 2.0),
        np.ascontiguousarray((raw.b + transposed.b) / 2.0),
        0,
    )
    back = T_state(sym)
    assert np.array_equal(back.m, sym.m)
    assert np.array_equal(back.n, sym.n)
    assert np.array_equal(back.b, sym.b)
    full = np.ones(sym.shape, dtype=bool)
    results.append(("symmetrised_woven", Q(sym, full)))

    # N5: Q vanishes EXACTLY on both T-invariant fixtures, not merely to 1e-15.
    for label, value in results:
        assert value == 0.0, (label, value)  # exact
    with capsys.disabled():
        print(
            f"\n[fact08] Q on T-invariant fixtures = {results!r} "
            "(exact zero asserted)"
        )


def test_fact09_S_is_odd_under_transpose_and_vanishes_on_invariant_masks(capsys):
    size = 8
    oblong = np.zeros((size, size), dtype=bool)
    oblong[1:4, 1:6] = True
    wrapping = np.zeros((size, size), dtype=bool)
    wrapping[7, 2] = wrapping[0, 2] = wrapping[1, 2] = wrapping[0, 3] = True
    odd_results = []
    for mask in (oblong, wrapping):
        left = S(T_mask(mask))
        right = -S(mask)
        odd_results.append((S(mask), left))
        assert left == right  # exact

    square = np.zeros((size, size), dtype=bool)
    square[2:6, 2:6] = True
    plus = np.zeros((size, size), dtype=bool)
    plus[3, 1:6] = True
    plus[1:6, 3] = True
    invariant = []
    for mask in (square, plus):
        assert np.array_equal(mask, mask.T)
        value = S(mask)
        invariant.append(value)
        assert value == 0.0  # exact
    with capsys.disabled():
        print(f"\n[fact09] (S(M), S(M.T)) = {odd_results!r}; S on invariant = {invariant!r}")


def test_fact10_Q_is_not_a_function_of_the_mask(capsys):
    size = 8
    mask = np.zeros((size, size), dtype=bool)
    mask[2:6, 2:6] = True
    assert np.array_equal(mask, mask.T)

    m = np.zeros((size, size), dtype=np.float64)
    m[2:6, 2:6] = 1.0
    n = np.full((size, size), 0.8, dtype=np.float64)

    b_one = np.zeros((2, size, size), dtype=np.float64)
    b_one[0, 2:6, 2:6] = 0.625
    b_two = np.zeros((2, size, size), dtype=np.float64)
    b_two[1, 2:6, 2:6] = 0.625

    state_one = LatticeBondState(m.copy(), n.copy(), b_one, 0)
    state_two = LatticeBondState(m.copy(), n.copy(), b_two, 0)

    # the two states are indistinguishable to any mask-only functional
    assert np.array_equal(_threshold_mask(state_one), _threshold_mask(state_two))
    assert np.array_equal(state_one.m, state_two.m)

    q_one = Q(state_one, mask)
    q_two = Q(state_two, mask)
    assert abs(q_one) > 0.0
    assert q_one == -q_two  # exact
    assert S(mask) == 0.0
    with capsys.disabled():
        print(f"\n[fact10] identical mask, Q_1={q_one!r} Q_2={q_two!r} S(M)={S(mask)!r}")


def test_fact11_opposite_Q_is_maintained_at_identical_shape_under_stepping(capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    branch_a = _symmetric_block_state()
    branch_b = T_state(branch_a)
    assert np.array_equal(_threshold_mask(branch_a), _threshold_mask(branch_b))

    steps = 30
    trajectory_a = []
    worst_sum = 0.0
    smallest = math.inf
    for index in range(steps + 1):
        mask_a = _threshold_mask(branch_a)
        mask_b = _threshold_mask(branch_b)
        assert np.array_equal(mask_a, mask_b), index  # SAME detected shape
        q_a = Q(branch_a, mask_a)
        q_b = Q(branch_b, mask_b)
        trajectory_a.append(q_a)
        worst_sum = max(worst_sum, abs(q_a + q_b))
        smallest = min(smallest, abs(q_a))
        assert q_a == -q_b  # exactly opposite
        assert abs(q_a) > 0.0  # non-zero
        if index < steps:
            branch_a = engine.step(branch_a).state
            branch_b = engine.step(branch_b).state
    assert worst_sum == 0.0
    with capsys.disabled():
        print(
            f"\n[fact11] Q trajectory (branch a, {steps + 1} samples) = "
            f"{[round(v, 12) for v in trajectory_a]!r}"
        )
        print(f"[fact11] max |Q_a + Q_b| = {worst_sum!r}; min |Q_a| = {smallest!r}")


# ======================================================================================
# C. detector and tracker
# ======================================================================================


def _detected_frames(state: LatticeBondState, count: int):
    engine = LatticeBondEngine(LatticeBondSpec())
    frames = []
    schedule = []
    states = []
    current = state
    for _ in range(count):
        frames.append(detect_components(current, DETECTOR))
        schedule.append(int(current.step))
        states.append(current)
        current = engine.step(current).state
    return frames, schedule, states


def test_fact12_detector_quotient_is_transpose_equivariant(capsys):
    checked = 0
    sizes = []
    for state in (_two_blob_state(), _symmetric_block_state(), _woven_state(8)):
        width = state.shape[1]
        detected = detect_components(state, DETECTOR)
        plain = quotient(detected, state)
        sizes.append((state.shape, len(detected), len(plain)))
        if not plain:
            continue
        expected = sorted(
            (
                (transpose_cells(cells, width), round(-q, 12), round(-s, 12))
                for cells, q, s in plain
            ),
            key=lambda item: (sorted(item[0]), item[1], item[2]),
        )
        transposed_state = T_state(state)
        observed = quotient(detect_components(transposed_state, DETECTOR), transposed_state)
        assert observed == expected
        assert set(observed) == set(expected)
        checked += 1
    assert checked >= 2
    with capsys.disabled():
        print(f"\n[fact12] quotient equality verified on {checked} handcrafted lattices")
        print(
            "[fact12] (shape, detected components, quotient entries after skipping "
            f"Q/S-undefined entities) = {sizes!r}"
        )


def test_fact13_component_index_is_not_transpose_equivariant(capsys):
    state = _two_blob_state()
    width = state.shape[1]
    plain = detect_components(state, DETECTOR)
    transposed = detect_components(T_state(state), DETECTOR)
    assert len(plain) == len(transposed) == 2

    mapping = {}
    for component in plain:
        image = transpose_cells(component.cells, width)
        matches = [
            other.index
            for other in transposed
            if frozenset(int(c) for c in other.cells) == image
        ]
        assert len(matches) == 1
        mapping[component.index] = matches[0]

    assert mapping != {index: index for index in mapping}
    assert mapping == {0: 1, 1: 0}
    with capsys.disabled():
        print(
            f"\n[fact13] index map x -> T(x) is {mapping!r}; "
            f"x cells={[c.cells for c in plain]!r} "
            f"T(x) cells={[c.cells for c in transposed]!r}"
        )


def _track_signature(result, frames, *, transpose_width: int | None):
    lookup = {}
    for frame in frames:
        for component in frame:
            lookup[(int(component.frame), int(component.index))] = component.cells
    signatures = []
    for track in result.tracks:
        sequence = []
        for point in track.points:
            cells = lookup[(int(point.frame), int(point.component_index))]
            if transpose_width is None:
                sequence.append((int(point.frame), frozenset(int(c) for c in cells)))
            else:
                sequence.append(
                    (int(point.frame), transpose_cells(cells, transpose_width))
                )
        signatures.append(tuple(sequence))
    return sorted(signatures, key=lambda seq: [(f, sorted(c)) for f, c in seq])


def test_fact14_tracker_is_equivariant_up_to_a_bijection_of_track_ids(capsys):
    state = _two_blob_state()
    width = state.shape[1]
    frames_a, schedule_a, _ = _detected_frames(state, 5)
    frames_b, schedule_b, _ = _detected_frames(T_state(state), 5)
    assert schedule_a == schedule_b

    result_a = track_components(frames_a, TRACKER, sampled_frames=schedule_a)
    result_b = track_components(frames_b, TRACKER, sampled_frames=schedule_b)

    signature_a = _track_signature(result_a, frames_a, transpose_width=width)
    signature_b = _track_signature(result_b, frames_b, transpose_width=None)
    assert len(result_a.tracks) == len(result_b.tracks) >= 2
    assert signature_a == signature_b

    kinds_a = sorted(event.kind for event in result_a.events)
    kinds_b = sorted(event.kind for event in result_b.events)
    assert kinds_a == kinds_b
    with capsys.disabled():
        print(
            f"\n[fact14] tracks={len(result_a.tracks)} events={len(result_a.events)}; "
            "per-track cell sequences agree as multisets after transpose"
        )


# ======================================================================================
# D. rectangular lattice
# ======================================================================================


def test_fact15_transpose_is_not_an_endomorphism_on_a_rectangular_lattice(capsys):
    state = _rect_state(5, 8)
    assert state.shape == (5, 8)
    transposed = T_state(state)
    assert transposed.shape == (8, 5)
    assert transposed.shape != state.shape
    assert transposed.b.shape == (2, 8, 5)

    # T(T(x)) == x still holds, bit-exactly
    back = T_state(transposed)
    assert back.shape == state.shape
    assert np.array_equal(back.m, state.m)
    assert np.array_equal(back.n, state.n)
    assert np.array_equal(back.b, state.b)

    engine = LatticeBondEngine(LatticeBondSpec())
    plain = engine.step(state).state
    other = engine.step(transposed).state
    assert plain.shape == (5, 8)
    assert other.shape == (8, 5)

    # the two evolutions cannot even be compared: the arrays have different shapes
    with pytest.raises(ValueError):
        np.subtract(plain.m, other.m)

    # an intervention plan built for one lattice is refused by the other
    plan = FaceIntervention.open(state.shape)
    with pytest.raises(ValueError):
        engine.step(transposed, plan)

    with capsys.disabled():
        print(
            "\n[fact15] H != W: T maps shape (5, 8) -> (8, 5). T(T(x)) == x exactly, "
            "but T(x) is NOT an element of the state space of x, so there is no "
            "internal Z2 action on a rectangular lattice: T is an isomorphism between "
            "two DIFFERENT state spaces, not an involution of one."
        )


# ======================================================================================
# E. frame closure witness
# ======================================================================================


WITNESS_H = 1024
WITNESS_DF = 16
GROUP_NAMES = (
    "kappa_hat",
    "D_hat",
    "k_on_hat",
    "k_off_hat",
    "k_tens_hat",
    "eps_b_hat",
    "lam",
    "theta_m_hat",
    "theta_n_hat",
)


def _box_bounds(h: int = WITNESS_H, df: int = WITNESS_DF):
    rate_lo = 1.0 / float(h)
    rate_hi = 1.0 / float(df)
    theta_hi = 2.0 * math.log(float(h) / 4.0)
    return rate_lo, rate_hi, theta_hi


def in_admissible_set(point, h: int = WITNESS_H, df: int = WITNESS_DF) -> bool:
    """Predicate ``A`` over the nine dimensionless groups."""

    (
        kappa_hat,
        d_hat,
        k_on_hat,
        k_off_hat,
        k_tens_hat,
        eps_b_hat,
        lam,
        theta_m_hat,
        theta_n_hat,
    ) = (float(v) for v in point)
    rate_lo, rate_hi, theta_hi = _box_bounds(h, df)
    for value in (kappa_hat, d_hat, k_on_hat, k_off_hat, k_tens_hat):
        if not rate_lo <= value <= rate_hi:
            return False
    if not 0.0 <= eps_b_hat <= 1.0:
        return False
    if not 0.0 <= lam <= 1.0:
        return False
    if theta_m_hat < 0.0 or theta_n_hat < 0.0:
        return False
    if not theta_m_hat + theta_n_hat < theta_hi:
        return False
    # (B1)
    if not kappa_hat < 0.25 * math.exp(-(theta_m_hat + theta_n_hat) / 2.0):
        return False
    # (B2)
    if not 4.0 * d_hat + 2.0 * eps_b_hat * k_on_hat < 1.0:
        return False
    return True


def spec_from_point(point, *, dt: float = 0.5) -> LatticeBondSpec:
    (
        kappa_hat,
        d_hat,
        k_on_hat,
        k_off_hat,
        k_tens_hat,
        eps_b_hat,
        lam,
        theta_m_hat,
        theta_n_hat,
    ) = (float(v) for v in point)
    return LatticeBondSpec(
        dt=dt,
        m_max=1.0,
        n_max=1.0,
        kappa_m=kappa_hat,
        theta_m=theta_m_hat,
        theta_n=theta_n_hat,
        resource_diffusivity=d_hat,
        resource_leak_floor=lam,
        epsilon_b=eps_b_hat,
        k_on=k_on_hat,
        k_off=k_off_hat,
        k_tension=k_tens_hat,
    )


WITNESS_POINT = (0.03, 0.03, 0.03, 0.03, 0.03, 0.5, 0.5, 1.0, 1.0)
WITNESS_RADIUS = 0.005


def test_fact16_admissible_set_is_a_non_empty_open_witness_with_positive_measure(capsys):
    rate_lo, rate_hi, theta_hi = _box_bounds()
    assert rate_lo == 1.0 / 1024.0 and rate_hi == 1.0 / 16.0

    # -- non-emptiness: an explicit interior witness point ------------------------------
    assert in_admissible_set(WITNESS_POINT)

    # -- a small open ball: the 18 axis-aligned corner perturbations at radius r ---------
    perturbations = []
    for axis in range(9):
        for sign in (+1.0, -1.0):
            probe = list(WITNESS_POINT)
            probe[axis] += sign * WITNESS_RADIUS
            perturbations.append((GROUP_NAMES[axis], sign, tuple(probe)))
    assert len(perturbations) == 18
    for name, sign, probe in perturbations:
        assert in_admissible_set(probe), (name, sign, probe)

    # -- positive finite Lebesgue measure via exact rejection sampling ------------------
    # NOTE: this generator is a NUMERICAL device for a measure witness only.  It is not
    # a scientific seed: nothing downstream of this test depends on its value.
    rejection_stream = np.random.default_rng(20240803)
    draws = 20000
    sample = np.empty((draws, 9), dtype=np.float64)
    sample[:, 0:5] = rejection_stream.uniform(rate_lo, rate_hi, size=(draws, 5))
    sample[:, 5] = rejection_stream.uniform(0.0, 1.0, size=draws)
    sample[:, 6] = rejection_stream.uniform(0.0, 1.0, size=draws)
    sample[:, 7] = rejection_stream.uniform(0.0, theta_hi, size=draws)
    sample[:, 8] = rejection_stream.uniform(0.0, theta_hi, size=draws)

    accepted = [tuple(row) for row in sample if in_admissible_set(row)]
    acceptance = len(accepted) / draws
    assert acceptance > 0.0
    assert acceptance < 1.0  # A is a proper subset: the box is strictly larger
    # Rejection sampling from a box that strictly contains A, keeping exactly the draws
    # in A, is by construction an exact sampler for the uniform law ON A; that law is a
    # proper normalized distribution precisely because 0 < |A| < |box| < inf.

    # -- which of the two extra constraints actually bind inside the box ----------------
    b2_failures = sum(
        1 for row in sample if not (4.0 * row[1] + 2.0 * row[5] * row[2] < 1.0)
    )

    # -- every accepted draw is a spec the engine accepts, and one full step succeeds ---
    for point in accepted:
        spec = spec_from_point(point)
        assert spec.dt <= spec.admissible_dt_limit

    engine_state = LatticeBondState(
        np.pad(np.ones((3, 3)), 1).astype(np.float64),
        np.full((5, 5), 0.6, dtype=np.float64),
        np.zeros((2, 5, 5), dtype=np.float64),
        0,
    )
    engine_state.b[0, 1:4, 1:4] = 0.4
    stepped = 0
    for point in accepted[:200]:
        result = LatticeBondEngine(spec_from_point(point)).step(engine_state.copy())
        assert result.state.step == 1
        assert np.isfinite(result.state.m).all()
        stepped += 1
    assert stepped >= 1

    with capsys.disabled():
        print(
            f"\n[fact16] H={WITNESS_H} df={WITNESS_DF} (MECHANICAL WITNESS VALUES, "
            "NOT design values)"
        )
        print(
            f"[fact16] box rates=[{rate_lo!r},{rate_hi!r}] theta bound={theta_hi!r} "
            f"0.25*exp(-bound/2)={0.25 * math.exp(-theta_hi / 2.0)!r}"
        )
        print(
            f"[fact16] draws={draws} accepted={len(accepted)} "
            f"acceptance rate={acceptance!r}"
        )
        print(
            f"[fact16] (B2) failures inside the box = {b2_failures} "
            "-> (B2) is NON-BINDING under this box; (B1) and the theta-sum cap bind"
        )
        print(
            f"[fact16] specs constructed and accepted by the engine = {len(accepted)}; "
            f"full engine steps run = {stepped} (dt=0.5, m_max=n_max=1.0)"
        )


# ======================================================================================
# F. cost measurement (engineering cost facts only)
# ======================================================================================


def test_fact17_engineering_cost_per_engine_step(capsys):
    engine = LatticeBondEngine(LatticeBondSpec())
    rows = []
    for size in (16, 32, 64):
        state = _woven_state(size)
        engine.step(state)  # warm-up, excluded from the measurement
        repeats = 20
        current = state
        start = time.perf_counter()
        for _ in range(repeats):
            current = engine.step(current).state
        elapsed = time.perf_counter() - start
        per_step = elapsed / repeats
        rows.append((size, per_step, per_step / float(size * size)))
        assert per_step > 0.0
    with capsys.disabled():
        print("\n[fact17] ENGINEERING COST FACTS (not a scientific result):")
        for size, per_step, per_cell in rows:
            print(
                f"[fact17]   {size}x{size}: {per_step:.6e} s/step, "
                f"{per_cell:.6e} s/step/cell"
            )


# ======================================================================================
# G. pipeline round-trip
# ======================================================================================


def _persisted_channel(directory: Path, position: int, channel: str) -> bytes:
    return (
        directory / MEASUREMENT_FRAME_DIRECTORY / f"frame_{position:06d}_{channel}.bin"
    ).read_bytes()


def test_fact18_Q_survives_the_measurement_bridge_round_trip(tmp_path, capsys):
    law = LatticeBondSpec()
    measurement = MeasurementSpec(min_cells=3)
    initial = _symmetric_block_state()
    schedule = [0, 1, 2, 3]
    run_directory = tmp_path / "run"
    run_directory.mkdir()

    record = run_measurement_bridge(
        run_directory,
        law_spec=law,
        initial_state=initial,
        sampled_frames=schedule,
        measurement_spec=measurement,
        acquisition_source_identity={
            "kind": "lattice-bond-engine",
            "name": "axis-transpose-equivariance-01s",
        },
    )
    assert list(record.sampled_frames) == schedule
    height, width = record.frame_shape

    engine = LatticeBondEngine(law)
    current = initial
    comparisons = []
    for position, label in enumerate(schedule):
        while int(current.step) < label:
            current = engine.step(current).state
        assert int(current.step) == label

        bond = np.frombuffer(
            _persisted_channel(run_directory, position, "bond"), dtype="<f8"
        ).reshape(2, height, width)
        mask = (
            np.frombuffer(_persisted_channel(run_directory, position, "mask"), dtype=np.uint8)
            .reshape(height, width)
            .astype(bool)
        )
        reread_state = LatticeBondState(
            np.zeros((height, width), dtype=np.float64),
            np.zeros((height, width), dtype=np.float64),
            np.ascontiguousarray(bond, dtype=np.float64),
            int(label),
        )
        q_disk = Q(reread_state, mask)

        memory_mask = np.asarray(current.m >= measurement.matter_threshold, dtype=bool)
        q_memory = Q(current, memory_mask)

        assert np.array_equal(mask, memory_mask)
        assert q_disk == q_memory  # exact
        comparisons.append((label, q_memory, q_disk - q_memory))

    with capsys.disabled():
        print(
            "\n[fact18] the bridge persists bond and mask per sampled frame under "
            f"{MEASUREMENT_FRAME_DIRECTORY}/frame_%06d_{{bond,mask}}.bin; "
            "Q is recomputable from those bytes alone."
        )
        for label, q_memory, delta in comparisons:
            print(f"[fact18]   frame {label}: Q={q_memory!r} (disk - memory) = {delta!r}")


# ======================================================================================
# H. adversarial-review facts (N1-N4)
#
# Everything below records mechanical facts that two adversarial reviewers established
# against this same stack.  Two of them are NEGATIVE results: a quantity that the
# earlier sections show to be exactly odd over a short horizon does NOT keep a stable
# sign over the design horizon, and the tracker quotient that section C shows to be
# transpose-equivariant on non-wrapping fixtures is NOT equivariant once a component
# wraps the torus.  Both are pinned here so that they cannot silently regress into an
# unexamined assumption.
# ======================================================================================


# --------------------------------------------------------------------------------------
# N1. sign(Q) is not stable over the design horizon
# --------------------------------------------------------------------------------------


N1_HORIZON = 1024


def test_fact19_sign_of_Q_is_not_stable_over_the_design_horizon(capsys):
    """Reviewer A: ``Q`` is exactly odd at short horizon but changes SIGN later.

    ``test_fact11`` establishes, over 30 steps, that the ``_symmetric_block_state``
    fixture and its transpose carry exactly opposite, non-zero ``Q``.  That is a
    short-horizon fact.  Run the SAME fixture at the SAME default ``LatticeBondSpec``
    out to 1024 steps and two things fail:

    (a) ``sign(Q_a)`` is not constant -- the branch-a trajectory crosses zero; and
    (b) the exact inter-branch oddness ``Q_b == -Q_a`` fails at a large fraction of
        sampled steps, at the level of one or two ULP of the mean.

    Neither is a defect of the engine: the engine's own transpose equivariance is exact
    (section A), and the detected shapes stay exact transposes of one another the whole
    way (asserted below).  The failure is in ``Q`` itself -- it is a DIFFERENCE OF TWO
    MEANS, so the two branches sum two different float sequences in two different
    orders, and the difference of two nearly-equal means loses its last bits exactly
    when ``|Q|`` becomes small.  Any downstream use of ``sign(Q)`` as a stable label
    over a 1024-step horizon is therefore unsound.
    """

    engine = LatticeBondEngine(LatticeBondSpec())
    branch_a = _symmetric_block_state()
    branch_b = T_state(branch_a)

    crossings: list[int] = []
    oddness_failures: list[tuple[int, float]] = []
    samples = 0
    previous_sign = None
    worst_oddness = 0.0
    smallest_abs = math.inf
    trajectory: list[tuple[int, float]] = []
    shape_mismatches = 0

    for index in range(N1_HORIZON + 1):
        mask_a = _threshold_mask(branch_a)
        mask_b = _threshold_mask(branch_b)
        # the DETECTED SHAPE stays an exact transpose the whole way: the failure below
        # is not a divergence of the two trajectories' geometry.
        if not np.array_equal(mask_b, np.asarray(mask_a).T):
            shape_mismatches += 1
        q_a = Q(branch_a, mask_a)
        q_b = Q(branch_b, mask_b)
        samples += 1
        trajectory.append((index, q_a))

        current_sign = math.copysign(1.0, q_a) if q_a != 0.0 else 0.0
        if previous_sign is not None and current_sign != previous_sign:
            crossings.append(index)
        previous_sign = current_sign

        residual = q_a + q_b
        if residual != 0.0:
            oddness_failures.append((index, residual))
        worst_oddness = max(worst_oddness, abs(residual))
        smallest_abs = min(smallest_abs, abs(q_a))

        if index < N1_HORIZON:
            branch_a = engine.step(branch_a).state
            branch_b = engine.step(branch_b).state

    assert shape_mismatches == 0
    assert samples == N1_HORIZON + 1

    # (a) sign(Q_a) is NOT constant over the horizon
    assert len(crossings) >= 1, "sign(Q_a) did not change over the horizon"

    # (b) exact inter-branch oddness fails at a positive number of sampled steps
    assert len(oddness_failures) > 0, "Q_a + Q_b == 0.0 held exactly at every sample"

    # the failures are pure last-bit noise, not a physical divergence
    assert worst_oddness <= 4.0 * float(np.finfo(np.float64).eps)

    first_failure = oddness_failures[0][0]
    with capsys.disabled():
        print(
            f"\n[fact19] NEGATIVE RESULT. horizon={N1_HORIZON} steps, stepped 1 at a "
            f"time, sampled at EVERY step -> {samples} samples."
        )
        print(f"[fact19] sign(Q_a) crossing steps = {crossings!r}")
        print(
            f"[fact19] exact-oddness failures (Q_a + Q_b != 0.0) = "
            f"{len(oddness_failures)} of {samples} sampled steps; first at step "
            f"{first_failure}; max |Q_a + Q_b| = {worst_oddness!r}"
        )
        print(
            f"[fact19] min |Q_a| over the horizon = {smallest_abs!r}; "
            f"Q_a(0) = {trajectory[0][1]!r}; Q_a({N1_HORIZON}) = {trajectory[-1][1]!r}"
        )
        for step_index in crossings:
            print(
                f"[fact19]   crossing at step {step_index}: "
                f"Q_a({step_index - 1}) = {trajectory[step_index - 1][1]!r} -> "
                f"Q_a({step_index}) = {trajectory[step_index][1]!r}"
            )
        print(
            "[fact19] detected shapes stayed exact transposes at all "
            f"{samples} samples ({shape_mismatches} mismatches), so sign(Q) is unstable "
            "for a purely numerical reason, not a geometric one."
        )


# --------------------------------------------------------------------------------------
# N2. the tracker is not transpose-equivariant when a component wraps the torus
# --------------------------------------------------------------------------------------


N2_SIZE = 8


def _mask_state(mask: np.ndarray, size: int = N2_SIZE) -> LatticeBondState:
    """A state whose threshold mask is exactly ``mask`` and whose bonds are zero."""

    occupied = np.asarray(mask, dtype=bool)
    m = np.where(occupied, 1.0, 0.0).astype(np.float64)
    n = np.full((size, size), 0.7, dtype=np.float64)
    b = np.zeros((2, size, size), dtype=np.float64)
    return LatticeBondState(m, n, b, 0)


def _literal_mask(rows) -> np.ndarray:
    return np.asarray(rows, dtype=bool)


# Reviewer B's counterexample, written out cell by cell.  Each frame carries ONE
# component: a full row (which therefore wraps in x) plus a single tail cell hanging off
# its left end.  The whole object drifts two rows downward per frame.
N2_FRAME_0 = _literal_mask(
    [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
)
N2_FRAME_1 = _literal_mask(
    [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
)
N2_FRAME_2 = _literal_mask(
    [
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ]
)
N2_COUNTEREXAMPLE = (N2_FRAME_0, N2_FRAME_1, N2_FRAME_2)


def _tracked_branch(masks, *, transposed: bool):
    """Detect and track a handcrafted mask sequence, plain or transposed."""

    frames = []
    for position, mask in enumerate(masks):
        state = _mask_state(mask)
        if transposed:
            state = T_state(state)
        frames.append(detect_components(state, DETECTOR, frame=position))
    schedule = list(range(len(masks)))
    return frames, track_components(frames, TRACKER, sampled_frames=schedule)


def _branch_summary(frames, result, *, transpose_width: int | None):
    return (
        len(result.tracks),
        tuple(sorted(event.kind for event in result.events)),
        tuple(_track_signature(result, frames, transpose_width=transpose_width)),
    )


def test_fact20_tracker_is_not_transpose_equivariant_when_a_component_wraps(capsys):
    """Reviewer B: a wrapping component breaks the tracker's transpose equivariance.

    ``detect_components`` builds each component by a DFS that assigns integer LIFTS
    (unwrapped coordinates) starting from the cell with the smallest LINEAR index
    ``y*W + x``, and the reported centroid is the mass-weighted mean of those lifts
    reduced mod ``H`` / ``W``.  For a component that does not wrap, the lift is the
    honest position and the centroid is transpose-covariant.  For a component that
    WRAPS, the lift depends on which cell seeded the DFS -- and ``min(y*W + x)`` is not
    transpose-covariant, because transposing permutes the linear order.

    In the fixture above the object is a full row (wrapping in x) plus one tail cell.
    In frames 0 and 1 the smallest linear index belongs to the row, so the row is lifted
    from its own left end.  In frame 2 the tail cell sits at ``(0, 3)`` -> linear index
    3, which is smaller than any row cell, so the DFS seeds THERE and the row is lifted
    from a different origin.  The reported ``centroid_x`` therefore jumps by ~2.67
    cells between frames 1 and 2 with no cell having moved in x at all, the periodic
    centroid distance goes to 3.333 > ``TrackerSpec.max_centroid_displacement`` = 3.0,
    and the association edge is rejected with ``REJECT_CENTROID_DISTANCE``.

    In the transposed branch the same object wraps in y instead, the seed stays on the
    bar in all three frames, ``centroid_y`` is constant, the distance is 2.0, and the
    edge survives.  The two branches therefore disagree about how many entities exist.
    """

    plain_frames, plain = _tracked_branch(N2_COUNTEREXAMPLE, transposed=False)
    transposed_frames, transposed = _tracked_branch(N2_COUNTEREXAMPLE, transposed=True)

    # exactly one component per frame in both branches, and it wraps
    for frames, axis in ((plain_frames, "x"), (transposed_frames, "y")):
        for frame in frames:
            assert len(frame) == 1
            component = frame[0]
            assert component.area == 9
            assert component.percolates
            if axis == "x":
                assert component.wraps_x and not component.wraps_y
            else:
                assert component.wraps_y and not component.wraps_x

    # the two branches see the SAME geometry up to transpose ...
    for left, right in zip(plain_frames, transposed_frames, strict=True):
        assert transpose_cells(left[0].cells, N2_SIZE) == frozenset(
            int(c) for c in right[0].cells
        )

    # ... and nonetheless disagree about identity.
    plain_kinds = [event.kind for event in plain.events]
    transposed_kinds = [event.kind for event in transposed.events]

    assert plain_kinds == ["APPEARANCE", "CONTINUATION", "DISSOLUTION", "APPEARANCE"]
    assert transposed_kinds == ["APPEARANCE", "CONTINUATION", "CONTINUATION"]
    assert len(plain.tracks) == 2
    assert len(transposed.tracks) == 1

    # the pinned negative assertion: the two branches DIFFER
    assert len(plain.tracks) != len(transposed.tracks)
    assert sorted(plain_kinds) != sorted(transposed_kinds)
    assert _branch_summary(plain_frames, plain, transpose_width=N2_SIZE) != _branch_summary(
        transposed_frames, transposed, transpose_width=None
    )

    centroids_plain = [
        (frame[0].centroid_y, frame[0].centroid_x) for frame in plain_frames
    ]
    centroids_transposed = [
        (frame[0].centroid_y, frame[0].centroid_x) for frame in transposed_frames
    ]
    rejected = [
        (edge.source, edge.target, edge.centroid_distance, edge.qualification_reason)
        for edge in plain.edges
        if not edge.qualified
    ]
    with capsys.disabled():
        print(
            "\n[fact20] NEGATIVE RESULT. handcrafted 8x8, 3-frame sequence, ONE "
            "wrapping component per frame."
        )
        print(f"[fact20] plain      tracks={len(plain.tracks)} events={plain_kinds!r}")
        print(
            f"[fact20] transposed tracks={len(transposed.tracks)} "
            f"events={transposed_kinds!r}"
        )
        print(f"[fact20] plain      (cy,cx) per frame = {centroids_plain!r}")
        print(f"[fact20] transposed (cy,cx) per frame = {centroids_transposed!r}")
        print(f"[fact20] rejected plain-branch edges = {rejected!r}")
        print(
            "[fact20] cause: detect_components lifts each component from the cell of "
            "smallest LINEAR index y*W+x, which is not transpose-covariant for a "
            "wrapping component; the centroid, and therefore the tracker's periodic "
            "centroid-distance gate, inherits that asymmetry."
        )


# The positive control.  A deterministic catalogue of explicit cell-offset shapes,
# placed on an explicit grid of origins, drifted by an explicit list of per-frame
# integer displacements.  No RNG appears anywhere in it.
N2_SHAPES = {
    "bar3v": ((0, 0), (1, 0), (2, 0)),
    "bar3h": ((0, 0), (0, 1), (0, 2)),
    "square2": ((0, 0), (0, 1), (1, 0), (1, 1)),
    "ell": ((0, 0), (1, 0), (2, 0), (2, 1)),
    "jay": ((0, 0), (0, 1), (1, 1), (2, 1)),
    "ess": ((0, 0), (0, 1), (1, 1), (1, 2)),
    "tee": ((0, 0), (0, 1), (0, 2), (1, 1)),
    "plus": ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1)),
    "rect23": ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)),
    "hook": ((0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2)),
}
N2_ORIGINS = tuple((oy, ox) for oy in range(0, N2_SIZE, 2) for ox in range(0, N2_SIZE, 2))
N2_DRIFTS = (
    ((0, 0), (0, 0)),
    ((1, 0), (1, 0)),
    ((0, 1), (0, 1)),
    ((1, 1), (1, 1)),
    ((1, 0), (0, 1)),
    ((0, 1), (1, 0)),
    ((2, 0), (0, 2)),
    ((1, 1), (1, -1)),
)


def _place(offsets, oy: int, ox: int, size: int = N2_SIZE) -> np.ndarray:
    mask = np.zeros((size, size), dtype=bool)
    for dy, dx in offsets:
        mask[(oy + dy) % size, (ox + dx) % size] = True
    return mask


def _no_component_wraps(frames) -> bool:
    return all(
        (not component.wraps_y) and (not component.wraps_x)
        for frame in frames
        for component in frame
    )


def test_fact21_tracker_quotient_is_equivariant_when_nothing_wraps(capsys):
    """Positive control for fact20: without wrapping, the tracker quotient IS equivariant.

    Over a systematic, fully handcrafted family of 3-frame sequences in which
    ``wraps_y == wraps_x == False`` for EVERY component in EVERY frame of BOTH branches,
    the number of tracks, the multiset of event kinds and the transposed per-track cell
    sequences all agree.  This isolates the fact20 failure to wrapping alone: it is not
    a general tracker defect, and it is not an artefact of the comparison method, which
    is the same one ``test_fact14`` uses.
    """

    checked = 0
    asymmetries: list[tuple] = []
    skipped_for_wrapping = 0

    for name, offsets in N2_SHAPES.items():
        for oy, ox in N2_ORIGINS:
            for first, second in N2_DRIFTS:
                masks = (
                    _place(offsets, oy, ox),
                    _place(offsets, oy + first[0], ox + first[1]),
                    _place(
                        offsets,
                        oy + first[0] + second[0],
                        ox + first[1] + second[1],
                    ),
                )
                plain_frames, plain = _tracked_branch(masks, transposed=False)
                if not _no_component_wraps(plain_frames):
                    skipped_for_wrapping += 1
                    continue
                transposed_frames, transposed = _tracked_branch(masks, transposed=True)
                if not _no_component_wraps(transposed_frames):
                    skipped_for_wrapping += 1
                    continue
                checked += 1
                left = _branch_summary(plain_frames, plain, transpose_width=N2_SIZE)
                right = _branch_summary(
                    transposed_frames, transposed, transpose_width=None
                )
                if left != right:
                    asymmetries.append((name, oy, ox, first, second, left, right))

    assert checked >= 200, checked
    assert asymmetries == [], asymmetries[:3]
    with capsys.disabled():
        print(
            f"\n[fact21] POSITIVE CONTROL. handcrafted non-wrapping 3-frame sequences "
            f"checked = {checked} (candidates skipped because something wrapped = "
            f"{skipped_for_wrapping})"
        )
        print(
            f"[fact21] asymmetries (track count, event-kind multiset, or transposed "
            f"per-track cell sequences) = {len(asymmetries)}"
        )
        print(
            f"[fact21] catalogue: {len(N2_SHAPES)} explicit shapes x "
            f"{len(N2_ORIGINS)} origins x {len(N2_DRIFTS)} drift pairs, no RNG"
        )


# --------------------------------------------------------------------------------------
# N3. the initial-condition law is a proper normalized distribution, and the three
#     scales close the frame
# --------------------------------------------------------------------------------------


def bound_B1(kappa_hat: float, theta_m_hat: float, theta_n_hat: float) -> bool:
    """(B1) matter bound at ``dt = 1``, ``m_max = n_max = 1``."""

    return kappa_hat < 0.25 * math.exp(-(theta_m_hat + theta_n_hat) / 2.0)


def bound_B2(d_hat: float, eps_b_hat: float, k_on_hat: float) -> bool:
    """(B2) resource/bond bound at ``dt = 1``, ``m_max = n_max = 1``."""

    return 4.0 * d_hat + 2.0 * eps_b_hat * k_on_hat < 1.0


# An explicit box that STRADDLES both bounds, so the sample contains accepted and
# rejected points in quantity.  Written out group by group.
N3_BOX = (
    ("kappa_hat", 0.0, 0.30),
    ("D_hat", 0.0, 0.30),
    ("k_on_hat", 0.0, 0.50),
    ("k_off_hat", 0.0, 0.50),
    ("k_tens_hat", 0.0, 0.50),
    ("eps_b_hat", 0.0, 1.0),
    ("lam", 0.0, 1.0),
    ("theta_m_hat", 0.0, 2.0),
    ("theta_n_hat", 0.0, 2.0),
)
N3_DRAWS = 2500


def test_fact22_nine_groups_are_the_spec_fields_and_dt_admissibility_is_exactly_B1_and_B2(
    capsys,
):
    """At ``dt = 1``, ``m_max = n_max = 1`` the nine groups ARE the twelve-field law.

    Non-dimensionalising the Stage-A law by the three scales ``dt``, ``m_max`` and
    ``n_max`` leaves nine dimensionless groups.  Setting all three scales to one makes
    the reduction the identity: each group is numerically the corresponding
    ``LatticeBondSpec`` field.  Under that identification the engine's OWN admissibility
    predicate, ``dt <= spec.admissible_dt_limit``, is exactly the conjunction of

        (B1)  kappa_hat < 0.25 * exp(-(theta_m_hat + theta_n_hat) / 2)
        (B2)  4*D_hat + 2*eps_b_hat*k_on_hat < 1

    because ``admissible_dt_limit`` is ``nextafter(min(bound_1, bound_2), 0)`` and, for
    a positive float ``x``, ``1.0 <= nextafter(x, 0.0)`` iff ``x > 1.0``.  The frame
    closes: the three scales, the nine groups and the two bounds are the whole story,
    with nothing left over.
    """

    # -- the nine groups are the fields, numerically --------------------------------
    reference = (0.05, 0.10, 0.30, 0.05, 0.15, 0.25, 0.05, 0.5, 0.5)
    spec = spec_from_point(reference, dt=1.0)
    assert spec.dt == 1.0 and spec.m_max == 1.0 and spec.n_max == 1.0
    identifications = (
        ("kappa_m", "kappa_hat", spec.kappa_m, reference[0]),
        ("resource_diffusivity", "D_hat", spec.resource_diffusivity, reference[1]),
        ("k_on", "k_on_hat", spec.k_on, reference[2]),
        ("k_off", "k_off_hat", spec.k_off, reference[3]),
        ("k_tension", "k_tens_hat", spec.k_tension, reference[4]),
        ("epsilon_b", "eps_b_hat", spec.epsilon_b, reference[5]),
        ("resource_leak_floor", "lam", spec.resource_leak_floor, reference[6]),
        ("theta_m", "theta_m_hat", spec.theta_m, reference[7]),
        ("theta_n", "theta_n_hat", spec.theta_n, reference[8]),
    )
    assert len(identifications) == len(GROUP_NAMES) == 9
    for field_name, group_name, field_value, group_value in identifications:
        assert field_value == group_value, (field_name, group_name)

    # the derived quantities lose their scales too
    assert spec.affinity_span == spec.theta_m + spec.theta_n  # m_max = n_max = 1
    assert spec.matter_dt_bound == 1.0 / (
        4.0 * spec.kappa_m * math.exp(0.5 * (spec.theta_m + spec.theta_n))
    )
    assert spec.resource_bond_dt_bound == 1.0 / (
        4.0 * spec.resource_diffusivity + 2.0 * spec.epsilon_b * spec.k_on
    )
    assert spec.analytic_dt_bound == min(
        spec.matter_dt_bound, spec.resource_bond_dt_bound
    )
    assert spec.admissible_dt_limit == math.nextafter(spec.analytic_dt_bound, 0.0)

    # -- the iff, on a straddling sample --------------------------------------------
    # NOTE: this generator is a NUMERICAL device used only to place points in an
    # explicit box on both sides of two explicit inequalities.  It is not a scientific
    # seed: nothing downstream of this test depends on its value, and the assertion is
    # a per-point identity, not an aggregate.
    box_stream = np.random.default_rng(20240804)
    sample = np.empty((N3_DRAWS, 9), dtype=np.float64)
    for column, (_, low, high) in enumerate(N3_BOX):
        sample[:, column] = box_stream.uniform(low, high, size=N3_DRAWS)

    accepted = 0
    b1_failures = 0
    b2_failures = 0
    both_failures = 0
    construction_mismatches: list[tuple] = []
    limit_mismatches: list[tuple] = []

    for row in sample:
        point = tuple(float(v) for v in row)
        (
            kappa_hat,
            d_hat,
            k_on_hat,
            _k_off_hat,
            _k_tens_hat,
            eps_b_hat,
            _lam,
            theta_m_hat,
            theta_n_hat,
        ) = point
        b1 = bound_B1(kappa_hat, theta_m_hat, theta_n_hat)
        b2 = bound_B2(d_hat, eps_b_hat, k_on_hat)
        predicted = b1 and b2
        if not b1:
            b1_failures += 1
        if not b2:
            b2_failures += 1
        if not b1 and not b2:
            both_failures += 1

        # (i) construction at dt = 1.0 succeeds iff (B1) and (B2)
        try:
            constructed = spec_from_point(point, dt=1.0)
        except AdmissibilityError:
            constructed = None
        observed = constructed is not None
        if observed != predicted:
            construction_mismatches.append((point, b1, b2, observed))
        if constructed is not None:
            accepted += 1
            assert constructed.dt <= constructed.admissible_dt_limit

        # (ii) the engine's own limit, read off a spec built at a dt small enough that
        #      construction never fails, agrees with the same conjunction
        probe = spec_from_point(point, dt=1e-9)
        assert probe.admissible_dt_limit > 1e-9
        if (1.0 <= probe.admissible_dt_limit) != predicted:
            limit_mismatches.append((point, b1, b2, probe.admissible_dt_limit))

    assert N3_DRAWS >= 2000
    assert 0 < accepted < N3_DRAWS  # the sample really straddles the boundary
    assert construction_mismatches == [], construction_mismatches[:3]
    assert limit_mismatches == [], limit_mismatches[:3]

    with capsys.disabled():
        print(
            f"\n[fact22] dt=1.0, m_max=n_max=1.0: all {len(identifications)} groups are "
            "numerically the corresponding LatticeBondSpec fields."
        )
        print(f"[fact22] box = {N3_BOX!r}")
        print(
            f"[fact22] draws={N3_DRAWS} accepted={accepted} rejected={N3_DRAWS - accepted} "
            f"(B1 fails={b1_failures}, B2 fails={b2_failures}, both fail={both_failures})"
        )
        print(
            f"[fact22] iff mismatches: construction={len(construction_mismatches)}, "
            f"admissible_dt_limit={len(limit_mismatches)} -> "
            "'LatticeBondSpec(...) constructs' is EXACTLY '(B1) and (B2)' on this sample."
        )


N3_IC_SIZES = (16, 24, 32)
N3_IC_DRAWS_PER_SIZE = 70


def test_fact23_initial_condition_law_is_a_normalized_product_of_uniforms(capsys):
    """The IC law is exactly samplable, normalized, and always engine-admissible.

    The declared initial-condition law is

        m[y, x] ~ U[0, m_max]  i.i.d.,   n[y, x] ~ U[0, n_max]  i.i.d.,   b == 0.

    That is a product of independent uniform measures on the compact box
    ``[0, m_max]^(L*L) x [0, n_max]^(L*L) x {0}``.  A product of uniform measures on a
    compact box has finite positive volume, so it is normalized by construction, and it
    is exactly samplable coordinate by coordinate -- no rejection step and no
    normalizing constant is ever needed.  The support bounds are asserted explicitly
    below, and every draw is accepted by ``LatticeBondState.validate`` against every
    law in the admissible set, at every declared size.
    """

    rate_lo, rate_hi, theta_hi = _box_bounds()

    # NOTE: numerical device only (see fact16 / fact22); not a scientific seed.
    ic_stream = np.random.default_rng(20240805)

    laws: list[tuple[float, ...]] = []
    while len(laws) < 8:
        probe = (
            float(ic_stream.uniform(rate_lo, rate_hi)),
            float(ic_stream.uniform(rate_lo, rate_hi)),
            float(ic_stream.uniform(rate_lo, rate_hi)),
            float(ic_stream.uniform(rate_lo, rate_hi)),
            float(ic_stream.uniform(rate_lo, rate_hi)),
            float(ic_stream.uniform(0.0, 1.0)),
            float(ic_stream.uniform(0.0, 1.0)),
            float(ic_stream.uniform(0.0, theta_hi)),
            float(ic_stream.uniform(0.0, theta_hi)),
        )
        if in_admissible_set(probe):
            laws.append(probe)
    specs = [spec_from_point(point, dt=1.0) for point in laws]
    for spec in specs:
        assert spec.m_max == 1.0 and spec.n_max == 1.0 and spec.dt == 1.0
        assert spec.dt <= spec.admissible_dt_limit

    draws = 0
    stepped = 0
    lowest_m = math.inf
    highest_m = -math.inf
    lowest_n = math.inf
    highest_n = -math.inf
    step_triples: list[tuple[int, int]] = []

    for size in N3_IC_SIZES:
        for draw_index in range(N3_IC_DRAWS_PER_SIZE):
            spec = specs[draw_index % len(specs)]
            m = ic_stream.uniform(0.0, spec.m_max, size=(size, size)).astype(np.float64)
            n = ic_stream.uniform(0.0, spec.n_max, size=(size, size)).astype(np.float64)
            b = np.zeros((2, size, size), dtype=np.float64)
            state = LatticeBondState(m, n, b, 0)
            draws += 1

            # -- explicit support bounds -------------------------------------------
            assert float(np.min(m)) >= 0.0 and float(np.max(m)) <= spec.m_max
            assert float(np.min(n)) >= 0.0 and float(np.max(n)) <= spec.n_max
            assert float(np.min(b)) == 0.0 and float(np.max(b)) == 0.0
            assert np.isfinite(m).all() and np.isfinite(n).all()
            lowest_m = min(lowest_m, float(np.min(m)))
            highest_m = max(highest_m, float(np.max(m)))
            lowest_n = min(lowest_n, float(np.min(n)))
            highest_n = max(highest_n, float(np.max(n)))

            # -- admissible against EVERY law in the sampled admissible set ---------
            for candidate in specs:
                state.validate(candidate)

            # -- at least one full engine step for this (law, IC, L) triple ---------
            result = LatticeBondEngine(spec).step(state)
            assert result.state.step == 1
            assert np.isfinite(result.state.m).all()
            assert np.isfinite(result.state.n).all()
            assert np.isfinite(result.state.b).all()
            result.state.validate(spec)
            stepped += 1
            step_triples.append((draw_index % len(specs), size))

    assert draws >= 200, draws
    assert stepped == draws
    assert len(set(step_triples)) == len(specs) * len(N3_IC_SIZES)

    # the sampled empirical support really fills the declared box
    assert 0.0 <= lowest_m < 0.01 and 0.99 < highest_m <= 1.0
    assert 0.0 <= lowest_n < 0.01 and 0.99 < highest_n <= 1.0

    with capsys.disabled():
        print(
            f"\n[fact23] IC law = product of i.i.d. U[0,m_max] x U[0,n_max] x {{b == 0}} "
            "on a compact box: normalized and exactly samplable by construction."
        )
        print(
            f"[fact23] draws={draws} across L in {N3_IC_SIZES!r}; every draw validated "
            f"against all {len(specs)} sampled admissible laws "
            f"({draws * len(specs)} validations, 0 rejections)."
        )
        print(
            f"[fact23] empirical support: m in [{lowest_m!r}, {highest_m!r}] c [0,1]; "
            f"n in [{lowest_n!r}, {highest_n!r}] c [0,1]; b == 0 exactly."
        )
        print(
            f"[fact23] full engine.step succeeded on {stepped} (law, IC, L) triples "
            f"covering all {len(set(step_triples))} (law, L) combinations."
        )


# --------------------------------------------------------------------------------------
# N4. equivariance at the declared sizes and at laws drawn from A
# --------------------------------------------------------------------------------------


N4_SIZES = (16, 24, 32)
N4_LAW_COUNT = 8
N4_STEPS = 25


def test_fact24_equivariance_at_declared_sizes_for_laws_drawn_from_the_admissible_set(
    capsys,
):
    """Sections A/B run only the DEFAULT law at L in {4, 6, 9}.  This widens both.

    Eight laws are drawn from the admissible set ``A`` (the same predicate
    ``in_admissible_set`` that fact16 exhibits), instantiated at ``dt = 1.0`` --
    the largest timestep the frame admits, which is the hardest case -- and run at the
    declared sizes ``L in (16, 24, 32)``, under an intervention plan that is
    demonstrably not its own transpose.  Both the single-step and the cumulative
    25-step residuals are reported.
    """

    rate_lo, rate_hi, theta_hi = _box_bounds()
    # NOTE: numerical device only (see fact16); not a scientific seed.
    law_stream = np.random.default_rng(20240806)
    laws: list[tuple[float, ...]] = []
    attempts = 0
    while len(laws) < N4_LAW_COUNT:
        attempts += 1
        probe = (
            float(law_stream.uniform(rate_lo, rate_hi)),
            float(law_stream.uniform(rate_lo, rate_hi)),
            float(law_stream.uniform(rate_lo, rate_hi)),
            float(law_stream.uniform(rate_lo, rate_hi)),
            float(law_stream.uniform(rate_lo, rate_hi)),
            float(law_stream.uniform(0.0, 1.0)),
            float(law_stream.uniform(0.0, 1.0)),
            float(law_stream.uniform(0.0, theta_hi)),
            float(law_stream.uniform(0.0, theta_hi)),
        )
        if in_admissible_set(probe):
            laws.append(probe)
    assert len(laws) == N4_LAW_COUNT >= 8

    worst_single = 0.0
    worst_cumulative = 0.0
    per_size: list[tuple[int, float, float]] = []
    combinations = 0

    for size in N4_SIZES:
        state = _woven_state(size)
        plan = FaceIntervention.from_cuts(
            (size, size),
            matter_faces=[(0, 1, 2), (0, 3, 4), (1, 0, 5)],
            resource_faces=[(1, 2, 0), (0, 4, 1)],
        )
        transposed_plan = T_intervention(plan)
        assert not np.array_equal(plan.matter_scale, transposed_plan.matter_scale)
        assert not np.array_equal(plan.resource_scale, transposed_plan.resource_scale)

        size_single = 0.0
        size_cumulative = 0.0
        for point in laws:
            spec = spec_from_point(point, dt=1.0)
            assert spec.dt <= spec.admissible_dt_limit
            engine = LatticeBondEngine(spec)

            left = T_state(engine.step(state, plan).state)
            right = engine.step(T_state(state), transposed_plan).state
            single = _state_residual(left, right)
            size_single = max(size_single, single)
            assert single <= TOL, (size, point, single)

            plain = state
            transposed = T_state(state)
            for _ in range(N4_STEPS):
                plain = engine.step(plain, plan).state
                transposed = engine.step(transposed, transposed_plan).state
                residual = _state_residual(T_state(plain), transposed)
                size_cumulative = max(size_cumulative, residual)
                assert residual <= TOL, (size, point, residual)
            combinations += 1

        per_size.append((size, size_single, size_cumulative))
        worst_single = max(worst_single, size_single)
        worst_cumulative = max(worst_cumulative, size_cumulative)

    assert combinations == len(N4_SIZES) * N4_LAW_COUNT

    with capsys.disabled():
        print(
            f"\n[fact24] {N4_LAW_COUNT} laws drawn from A (rejection over "
            f"{attempts} box draws), dt=1.0, sizes {N4_SIZES!r}, "
            f"non-self-transpose intervention, {N4_STEPS}-step horizon."
        )
        for size, single, cumulative in per_size:
            print(
                f"[fact24]   L={size}: max 1-step residual = {single!r}; "
                f"max {N4_STEPS}-step cumulative residual = {cumulative!r}"
            )
        print(
            f"[fact24] overall: max 1-step = {worst_single!r}; "
            f"max {N4_STEPS}-step cumulative = {worst_cumulative!r} "
            f"over {combinations} (law, L) combinations."
        )
