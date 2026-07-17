"""DEV-only state surgery primitives for ACCESS-STRUCTURE-00 Phase 0.5.

This module qualifies intervention mechanics; it does not test where a causal
state resides.  It intentionally has no prospective-seed default.  Callers
must pass seeds from the already-open DEV namespace 50001--50010.

Operational state partition
---------------------------
``C`` is a fixed periodic disk containing the complete manipulable simulator
state around one tracked body.  ``B`` (the detected body) is a subset of C.
``H`` is the one-cell, four-neighbour stencil collar immediately outside C.
``E`` is the complement.  N/c are physical fields defined across C/H/E, not a
separate spatial partition.  The fixed disk makes translations bijective and
avoids clearing an irregular recipient body into an artificial blank state.

At the current DEV qualification radius (10 cells), C is deliberately broader
than droplet material.  Claims about C must therefore say "local/core access",
not "material ownership".
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
from typing import Iterable

import numpy as np

from edlab.experiments.sc_iom.engine import IOMState


DEV_SEEDS = tuple(range(50001, 50011))
STATE_FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
EXTENSIVE_FIELDS = ("rho", "U", "V", "C", "Mf")
PHYSICAL_INTENSIVE_FIELDS = ("c", "N")
DERIVED_READOUT_FIELDS = ("uptake",)
BALANCED_PHYSICAL_FIELDS = ("rho", "U", "V", "c", "N")
CORE_RADIUS = 10
HALO_WIDTH = 1
SERIALIZATION_SCHEMA = "ACCESS-STRUCTURE-00-IOMState-v1"


def require_dev_seed(seed: int) -> int:
    """Refuse any seed outside the already-open Phase 0.5 namespace."""
    seed = int(seed)
    if seed not in DEV_SEEDS:
        raise ValueError("REFUSED: ACCESS-STRUCTURE-00 Phase 0.5 permits DEV seeds 50001-50010 only")
    return seed


def _integer_center(center: Iterable[float], shape: tuple[int, int]) -> tuple[int, int]:
    values = tuple(float(value) for value in center)
    if len(values) != 2:
        raise ValueError("center must have exactly two coordinates")
    return tuple(int(np.rint(value)) % shape[index] for index, value in enumerate(values))


def periodic_distance(shape: tuple[int, int], center: Iterable[float]) -> np.ndarray:
    """Euclidean distance to an integer-centered point on a periodic grid."""
    cx, cy = _integer_center(center, shape)
    x, y = np.indices(shape)
    dx = np.minimum(np.abs(x - cx), shape[0] - np.abs(x - cx))
    dy = np.minimum(np.abs(y - cy), shape[1] - np.abs(y - cy))
    return np.sqrt(dx * dx + dy * dy)


@dataclass(frozen=True)
class StatePartition:
    center: tuple[int, int]
    core: np.ndarray
    halo: np.ndarray
    environment: np.ndarray
    distance: np.ndarray

    def validate(self) -> None:
        masks = (self.core, self.halo, self.environment)
        if any(mask.dtype != np.bool_ for mask in masks):
            raise ValueError("partition masks must be boolean")
        if (self.core & self.halo).any() or (self.core & self.environment).any() or (self.halo & self.environment).any():
            raise ValueError("C/H/E masks overlap")
        if not (self.core | self.halo | self.environment).all():
            raise ValueError("C/H/E masks are not exhaustive")


def partition_state(
    shape: tuple[int, int],
    center: Iterable[float],
    *,
    core_radius: int = CORE_RADIUS,
    halo_width: int = HALO_WIDTH,
) -> StatePartition:
    if core_radius < 1 or halo_width < 1:
        raise ValueError("core_radius and halo_width must be positive")
    c = _integer_center(center, shape)
    distance = periodic_distance(shape, c)
    core = distance <= float(core_radius)
    halo = (distance > float(core_radius)) & (distance <= float(core_radius + halo_width))
    result = StatePartition(c, core, halo, ~(core | halo), distance)
    result.validate()
    return result


def concentric_bands(partition: StatePartition) -> dict[str, np.ndarray]:
    """Frozen diagnostic bands; not candidate scientific intervention radii."""
    d = partition.distance
    # Boundaries are expressed relative to the actual outer edge of C.
    edge = float(np.max(d[partition.core]))
    return {
        "C": partition.core.copy(),
        "H_d1": (d > edge) & (d <= edge + 1.0),
        "E_d2_3": (d > edge + 1.0) & (d <= edge + 3.0),
        "E_d4_6": (d > edge + 3.0) & (d <= edge + 6.0),
        "E_far": d > edge + 6.0,
    }


def state_metadata(state: IOMState) -> dict:
    return {
        "schema": SERIALIZATION_SCHEMA,
        "step": int(state.step),
        "fields": {
            field: {"shape": list(getattr(state, field).shape), "dtype": str(getattr(state, field).dtype)}
            for field in STATE_FIELDS
        },
        "persistent_rng_state": None,
        "persistent_previous_state": None,
        "persistent_flux_or_gradient_buffers": None,
    }


def serialize_state(state: IOMState) -> bytes:
    """Serialize all persistent physics arrays and scheduler phase exactly."""
    payload = io.BytesIO()
    arrays = {field: getattr(state, field) for field in STATE_FIELDS}
    arrays["metadata_json"] = np.array(json.dumps(state_metadata(state), sort_keys=True))
    np.savez(payload, **arrays)
    return payload.getvalue()


def deserialize_state(payload: bytes) -> IOMState:
    with np.load(io.BytesIO(payload), allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata_json"]))
        if metadata.get("schema") != SERIALIZATION_SCHEMA:
            raise ValueError("unsupported ACCESS-STRUCTURE state serialization schema")
        arrays = {field: np.array(data[field], copy=True) for field in STATE_FIELDS}
    return IOMState(step=int(metadata["step"]), **arrays)


def state_sha256(state: IOMState) -> str:
    """Content digest independent of the npz container's metadata."""
    digest = hashlib.sha256()
    digest.update(str(int(state.step)).encode("ascii"))
    for field in STATE_FIELDS:
        array = np.ascontiguousarray(getattr(state, field))
        digest.update(field.encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def exact_state_errors(reference: IOMState, candidate: IOMState) -> dict[str, float | int]:
    result: dict[str, float | int] = {"step": int(candidate.step - reference.step)}
    for field in STATE_FIELDS:
        a = getattr(reference, field)
        b = getattr(candidate, field)
        if a.shape != b.shape:
            result[field] = float("inf")
        else:
            result[field] = float(np.max(np.abs(a - b))) if a.size else 0.0
    return result


def no_op_continuation(state: IOMState) -> IOMState:
    return state.copy()


def same_source_reinsert(state: IOMState, partition: StatePartition) -> IOMState:
    """Extract and reinsert the same C without numerical transformation."""
    result = state.copy()
    for field in STATE_FIELDS:
        source = getattr(state, field)
        target = getattr(result, field)
        if source.ndim == 2:
            target[partition.core] = source[partition.core]
        else:
            target[:, partition.core] = source[:, partition.core]
    return result


def coordinate_transform_sham(
    state: IOMState,
    partition: StatePartition,
    *,
    shift: tuple[int, int] = (7, -9),
) -> IOMState:
    """Exercise a periodic translation and its exact inverse before reinsertion."""
    result = state.copy()
    axes = (-2, -1)
    for field in STATE_FIELDS:
        source = getattr(state, field)
        roundtrip = np.roll(np.roll(source, shift, axis=axes), (-shift[0], -shift[1]), axis=axes)
        target = getattr(result, field)
        if source.ndim == 2:
            target[partition.core] = roundtrip[partition.core]
        else:
            target[:, partition.core] = roundtrip[:, partition.core]
    return result


def _translated(array: np.ndarray, shift: tuple[int, int]) -> np.ndarray:
    return np.roll(array, shift, axis=(-2, -1))


@dataclass(frozen=True)
class ExchangeRecord:
    center_a: tuple[int, int]
    center_b: tuple[int, int]
    shift_a_to_b: tuple[int, int]
    shift_b_to_a: tuple[int, int]
    core_radius: int
    source: dict[str, str]


def _validate_exchange(
    state_a: IOMState,
    state_b: IOMState,
    partition_a: StatePartition,
    partition_b: StatePartition,
) -> tuple[tuple[int, int], tuple[int, int]]:
    if state_a.step != state_b.step:
        raise ValueError("exchange worlds must have the same scheduler phase/step")
    for field in STATE_FIELDS:
        if getattr(state_a, field).shape != getattr(state_b, field).shape:
            raise ValueError(f"exchange-world shape mismatch for {field}")
    shift_ab = tuple(partition_b.center[index] - partition_a.center[index] for index in range(2))
    shift_ba = tuple(-value for value in shift_ab)
    if not np.array_equal(_translated(partition_a.core, shift_ab), partition_b.core):
        raise ValueError("A and B core supports are not translation-equivalent")
    return shift_ab, shift_ba


def exchange_cores(
    state_a: IOMState,
    state_b: IOMState,
    partition_a: StatePartition,
    partition_b: StatePartition,
) -> tuple[IOMState, IOMState, ExchangeRecord]:
    """Reciprocally exchange complete C blocks between two state worlds.

    Returns ``C_B E_A`` and ``C_A E_B`` in that order.  Every donor value is
    copied exactly under an integer toroidal translation: there is no scaling,
    interpolation, collar blending, zero fill, or recomputation. Totals are
    conserved across the paired branch exchange. They are conserved within a
    single combined world only when :func:`swap_cores` applies both reciprocal
    assignments to disjoint supports.
    """
    shift_ab, shift_ba = _validate_exchange(state_a, state_b, partition_a, partition_b)
    a_receives_b = state_a.copy()
    b_receives_a = state_b.copy()
    for field in STATE_FIELDS:
        values_a = getattr(state_a, field)
        values_b = getattr(state_b, field)
        into_a = _translated(values_b, shift_ba)
        into_b = _translated(values_a, shift_ab)
        target_a = getattr(a_receives_b, field)
        target_b = getattr(b_receives_a, field)
        if values_a.ndim == 2:
            target_a[partition_a.core] = into_a[partition_a.core]
            target_b[partition_b.core] = into_b[partition_b.core]
        else:
            target_a[:, partition_a.core] = into_a[:, partition_a.core]
            target_b[:, partition_b.core] = into_b[:, partition_b.core]

    record = ExchangeRecord(
        center_a=partition_a.center,
        center_b=partition_b.center,
        shift_a_to_b=shift_ab,
        shift_b_to_a=shift_ba,
        core_radius=int(np.max(partition_a.distance[partition_a.core])),
        source={
            "recipient_A": "C_B E_A",
            "recipient_B": "C_A E_B",
            "C_and_B": "opposite donor, exact translated values",
            "H_and_E": "recipient unchanged",
            "N_c_inside_C": "opposite donor, exact translated values",
            "N_c_outside_C": "recipient unchanged",
            "G": "recipient engine context; up_ref is dynamically recomputed after the exchange",
            "D": "matched scheduler step; no persistent buffers or RNG exist",
            "uptake": "opposite donor previous-step readout; not a next-step input",
            "transform": "integer toroidal roll; no interpolation",
            "collar": "no blend; the one-cell H collar is recipient state and seam is measured",
            "recompute": "none at surgery",
        },
    )
    return a_receives_b, b_receives_a, record


def swap_cores(
    state: IOMState,
    partition_a: StatePartition,
    partition_b: StatePartition,
) -> tuple[IOMState, ExchangeRecord]:
    """Within-world A<->B exchange producing both crossed arms simultaneously."""
    if (partition_a.core & partition_b.core).any():
        raise ValueError("within-world core supports overlap")
    a_receives_b, b_receives_a, record = exchange_cores(state, state, partition_a, partition_b)
    result = state.copy()
    for field in STATE_FIELDS:
        values = getattr(result, field)
        from_a = getattr(b_receives_a, field)
        from_b = getattr(a_receives_b, field)
        if values.ndim == 2:
            values[partition_a.core] = from_b[partition_a.core]
            values[partition_b.core] = from_a[partition_b.core]
        else:
            values[:, partition_a.core] = from_b[:, partition_a.core]
            values[:, partition_b.core] = from_a[:, partition_b.core]
    return result, record


def paired_environment_body_standardization(
    history_world: IOMState,
    no_history_world: IOMState,
    history_partition: StatePartition,
    reference_partition: StatePartition,
) -> tuple[IOMState, IOMState, ExchangeRecord]:
    """Return C_0 E_history and C_history E_0 as one reciprocal operation."""
    return exchange_cores(history_world, no_history_world, history_partition, reference_partition)


def environment_standardized(*args, **kwargs):
    """Alias with explicit role: second output is C_history E_0."""
    return paired_environment_body_standardization(*args, **kwargs)


def body_core_standardized(*args, **kwargs):
    """Alias with explicit role: first output is C_0 E_history."""
    return paired_environment_body_standardization(*args, **kwargs)


def environment_reset(*args, **kwargs):
    """Alias for the same reciprocal on-manifold exchange; blank reset is unsupported."""
    return paired_environment_body_standardization(*args, **kwargs)


def band_change(reference: IOMState, candidate: IOMState, bands: dict[str, np.ndarray]) -> dict:
    result = {}
    for band_name, mask in bands.items():
        fields = {}
        for field in STATE_FIELDS:
            delta = getattr(candidate, field) - getattr(reference, field)
            values = delta[..., mask]
            fields[field] = {
                "max_abs": float(np.max(np.abs(values))) if values.size else 0.0,
                "rms": float(np.sqrt(np.mean(values * values))) if values.size else 0.0,
            }
        result[band_name] = fields
    return result


# ---------------------------------------------------------------------------
# Phase 0.6A boundary-safe, individually balanced operator candidates.
#
# These are engineering candidates only.  They never evaluate feeding and do
# not imply that C is a storage compartment.  The complete four-configuration
# grid is frozen here and in the Phase 0.6A operator specification before the
# DEV qualification is executed.


@dataclass(frozen=True)
class BoundarySafeSpec:
    name: str
    family: str
    inner_radius: int
    outer_radius: int = CORE_RADIUS
    taper: str = "hard"

    def validate(self) -> None:
        if self.family not in {
            "recipient_interface_preserving_interior",
            "constrained_phase_consistent_projection",
        }:
            raise ValueError(f"unsupported boundary-safe family: {self.family}")
        if not (0 < self.inner_radius < self.outer_radius <= CORE_RADIUS):
            raise ValueError("boundary-safe radii must satisfy 0 < inner < outer <= CORE_RADIUS")
        if self.taper not in {"hard", "quintic"}:
            raise ValueError("boundary-safe taper must be hard or quintic")
        if self.family == "recipient_interface_preserving_interior" and self.taper != "hard":
            raise ValueError("recipient-interface-preserving family uses the declared hard interior")
        if self.family == "constrained_phase_consistent_projection" and self.taper != "quintic":
            raise ValueError("constrained projection family uses the declared quintic transition")


BOUNDARY_SAFE_SPECS = (
    BoundarySafeSpec(
        name="RIP_HARD_R9",
        family="recipient_interface_preserving_interior",
        inner_radius=9,
        taper="hard",
    ),
    BoundarySafeSpec(
        name="RIP_HARD_R8",
        family="recipient_interface_preserving_interior",
        inner_radius=8,
        taper="hard",
    ),
    BoundarySafeSpec(
        name="CPP_QUINTIC_R8",
        family="constrained_phase_consistent_projection",
        inner_radius=8,
        taper="quintic",
    ),
    BoundarySafeSpec(
        name="CPP_QUINTIC_R7",
        family="constrained_phase_consistent_projection",
        inner_radius=7,
        taper="quintic",
    ),
)


class BalanceProjectionError(RuntimeError):
    """Raised when an individual-arm physical total cannot be matched locally."""


def boundary_safe_weights(partition: StatePartition, spec: BoundarySafeSpec) -> np.ndarray:
    """Outcome-independent donor weight with an exactly recipient-valued outer edge."""
    spec.validate()
    d = partition.distance
    if spec.taper == "hard":
        return (d <= float(spec.inner_radius)).astype(float)
    weight = np.zeros_like(d, dtype=float)
    weight[d <= float(spec.inner_radius)] = 1.0
    transition = (d > float(spec.inner_radius)) & (d < float(spec.outer_radius))
    s = (d[transition] - float(spec.inner_radius)) / float(spec.outer_radius - spec.inner_radius)
    # One minus quintic smoothstep: value and first derivative match at both ends.
    weight[transition] = 1.0 - (6.0 * s**5 - 15.0 * s**4 + 10.0 * s**3)
    return weight


def boundary_safe_bands(partition: StatePartition, spec: BoundarySafeSpec) -> dict[str, np.ndarray]:
    """Frozen Phase 0.6A diagnostic partition around the candidate support."""
    spec.validate()
    d = partition.distance
    return {
        "payload_core": d <= float(spec.inner_radius),
        "interface_collar": (d > float(spec.inner_radius)) & (d <= float(spec.outer_radius)),
        "inner_halo": (d > float(spec.outer_radius)) & (d <= float(spec.outer_radius + 1)),
        "outer_halo": (d > float(spec.outer_radius + 1)) & (d <= float(spec.outer_radius + 3)),
        "far_environment": d > float(spec.outer_radius + 3),
    }


def _project_nonnegative_total(
    provisional: np.ndarray,
    recipient: np.ndarray,
    weight: np.ndarray,
) -> tuple[np.ndarray, dict[str, float | bool]]:
    """Match one recipient total using only a recipient-shaped local correction.

    The spatial correction basis is fixed by the recipient and the declared
    donor-weight map; the donor/history changes only the scalar amount that must
    be removed or added.  The outer interface and every cell outside the
    declared support remain exact recipient values.  A bounded active-set solve
    preserves non-negativity when material must be removed.
    """
    active = weight > 0.0
    result = np.array(provisional, dtype=float, copy=True)
    if not active.any():
        raise BalanceProjectionError("empty boundary-safe correction support")
    target = float(np.sum(recipient[active], dtype=np.float64))
    current = float(np.sum(result[active], dtype=np.float64))
    delta = target - current
    scale = max(float(np.mean(recipient[active])), 1.0)
    if abs(delta) <= 1e-14 * scale:
        return result, {
            "target_support_total": target,
            "provisional_support_total": current,
            "correction": 0.0,
            "active_set_clipped": False,
        }

    floor = max(abs(target) / max(1, int(active.sum())) * 1e-12, 1e-15)
    basis = weight[active] * (np.maximum(recipient[active], 0.0) + floor)
    if not np.any(basis > 0.0):
        basis = weight[active].copy()
    values = result[active].copy()
    clipped = False
    if delta > 0.0:
        values = values + delta * basis / float(basis.sum())
    else:
        # Find lambda <= 0 with sum(max(0, values + lambda*basis)) == target.
        high = 0.0
        low = -1.0
        while float(np.maximum(0.0, values + low * basis).sum()) > target:
            low *= 2.0
            if low < -1e18:
                raise BalanceProjectionError("non-negative local balance projection did not bracket")
        for _ in range(100):
            mid = 0.5 * (low + high)
            if float(np.maximum(0.0, values + mid * basis).sum()) > target:
                high = mid
            else:
                low = mid
        projected = np.maximum(0.0, values + 0.5 * (low + high) * basis)
        clipped = bool(np.any(values + 0.5 * (low + high) * basis < 0.0))
        values = projected

    residual = target - float(values.sum(dtype=np.float64))
    index = int(np.argmax(basis))
    values[index] += residual
    if values[index] < -1e-13 or not np.isfinite(values).all():
        raise BalanceProjectionError("local total projection violated non-negativity or finiteness")
    values[index] = max(0.0, values[index])
    result[active] = values
    result[~active] = recipient[~active]
    final = float(np.sum(result[active], dtype=np.float64))
    return result, {
        "target_support_total": target,
        "provisional_support_total": current,
        "final_support_total": final,
        "correction": float(final - current),
        "active_set_clipped": clipped,
    }


def _balance_base_cohorts(
    provisional: np.ndarray,
    recipient: np.ndarray,
    rho_after: np.ndarray,
    weight: np.ndarray,
) -> tuple[np.ndarray, dict[str, float | int]]:
    """Balance passive base-cohort rows and global columns by deterministic IPF."""
    active = weight > 0.0
    matrix = np.maximum(provisional[:, active], 0.0).astype(float, copy=True)
    target_rows = np.maximum(rho_after[active], 0.0)
    target_cols = np.maximum(recipient[:, active].sum(axis=1), 0.0)
    if not np.isclose(target_rows.sum(), target_cols.sum(), rtol=1e-12, atol=1e-12):
        raise BalanceProjectionError("base-cohort row and column balance targets disagree")

    if np.allclose(matrix.sum(axis=0), target_rows, rtol=1e-13, atol=1e-13) and np.allclose(
        matrix.sum(axis=1), target_cols, rtol=1e-13, atol=1e-13
    ):
        balanced = matrix
        iterations = 0
    else:
        positive_cols = target_cols > 0.0
        matrix[~positive_cols, :] = 0.0
        if positive_cols.any():
            tiny = max(float(target_rows.sum()) * 1e-18, 1e-18)
            matrix[positive_cols, :] += tiny
        iterations = 0
        for iterations in range(1, 2001):
            row_sums = matrix.sum(axis=0)
            nonzero_rows = target_rows > 0.0
            matrix[:, ~nonzero_rows] = 0.0
            matrix[:, nonzero_rows] *= (target_rows[nonzero_rows] / row_sums[nonzero_rows])[None, :]
            col_sums = matrix.sum(axis=1)
            matrix[positive_cols, :] *= (target_cols[positive_cols] / col_sums[positive_cols])[:, None]
            if (
                np.max(np.abs(matrix.sum(axis=0) - target_rows), initial=0.0) <= 5e-12
                and np.max(np.abs(matrix.sum(axis=1) - target_cols), initial=0.0) <= 5e-12
            ):
                break
        else:
            raise BalanceProjectionError("base-cohort balancing did not converge")
        # Finish on the per-cell invariant; the resulting column residual is
        # recorded and must remain inside the frozen float64 criterion.
        row_sums = matrix.sum(axis=0)
        nonzero_rows = target_rows > 0.0
        matrix[:, nonzero_rows] *= (target_rows[nonzero_rows] / row_sums[nonzero_rows])[None, :]

    result = recipient.copy()
    result[:, active] = matrix
    return result, {
        "iterations": int(iterations),
        "row_sum_max_abs": float(np.max(np.abs(matrix.sum(axis=0) - target_rows), initial=0.0)),
        "column_sum_max_abs": float(np.max(np.abs(matrix.sum(axis=1) - target_cols), initial=0.0)),
    }


def boundary_safe_transplant(
    recipient: IOMState,
    donor: IOMState,
    recipient_partition: StatePartition,
    donor_partition: StatePartition,
    spec: BoundarySafeSpec,
    *,
    appended_tracers: int = 3,
) -> tuple[IOMState, dict]:
    """Transplant one donor into one recipient with local per-arm balance.

    Physical fields ``rho,U,V,c,N`` are donor-weighted then projected back to
    the recipient's own total using only a recipient-shaped correction inside
    C.  Intensive memory is the protected causal payload and is not total-
    balanced: matching its mean would erase the history contrast under test.
    Passive diagnostic cohorts are balanced separately and never influence
    physics.  The incoming ``uptake`` array is retained from the recipient
    because it is a previous-step readout that the next update does not read.
    """
    spec.validate()
    shift_rd, _ = _validate_exchange(recipient, donor, recipient_partition, donor_partition)
    # _validate_exchange returns recipient->donor; donor->recipient is its inverse.
    donor_to_recipient = tuple(-value for value in shift_rd)
    weight = boundary_safe_weights(recipient_partition, spec)
    donor_values = {
        field: _translated(getattr(donor, field), donor_to_recipient) for field in STATE_FIELDS
    }
    result = recipient.copy()
    balance = {}

    for field in BALANCED_PHYSICAL_FIELDS:
        rec = getattr(recipient, field)
        src = donor_values[field]
        provisional = rec + weight * (src - rec)
        projected, audit = _project_nonnegative_total(provisional, rec, weight)
        setattr(result, field, projected)
        balance[field] = audit

    # Preserve donor intensive memory on the declared weight map while keeping
    # it coherent with the balanced scaffold density.
    rec_m = recipient.Mf / np.maximum(recipient.rho, 1e-12)[None, ...]
    don_m = donor_values["Mf"] / np.maximum(donor_values["rho"], 1e-12)[None, ...]
    mixed_m = rec_m + weight[None, ...] * (don_m - rec_m)
    result.Mf = result.rho[None, ...] * mixed_m

    if not (0 <= appended_tracers < recipient.C.shape[0]):
        raise ValueError("invalid appended tracer count")
    base_count = recipient.C.shape[0] - appended_tracers
    provisional_base = recipient.C[:base_count] + weight[None, ...] * (
        donor_values["C"][:base_count] - recipient.C[:base_count]
    )
    base_cohorts, cohort_audit = _balance_base_cohorts(
        provisional_base, recipient.C[:base_count], result.rho, weight
    )
    result.C[:base_count] = base_cohorts
    appended_audit = {}
    for channel in range(base_count, recipient.C.shape[0]):
        provisional = recipient.C[channel] + weight * (
            donor_values["C"][channel] - recipient.C[channel]
        )
        projected, audit = _project_nonnegative_total(
            provisional, recipient.C[channel], weight
        )
        result.C[channel] = projected
        appended_audit[str(channel)] = audit

    # Explicit phase/readout choice: scheduler parity is donor-matched, while
    # stale previous-step uptake remains recipient state and is not a payload.
    result.uptake = recipient.uptake.copy()
    result.step = recipient.step

    changed = np.zeros_like(weight, dtype=bool)
    for field in STATE_FIELDS:
        values = getattr(result, field)
        original = getattr(recipient, field)
        changed |= np.any(values != original, axis=0) if values.ndim == 3 else values != original
    if np.any(changed & ~recipient_partition.core):
        raise BalanceProjectionError("boundary-safe transplant changed a cell outside C")
    return result, {
        "schema": "ACCESS-STRUCTURE-00-PHASE06A-BOUNDARY-OPERATOR-v1",
        "spec": {
            "name": spec.name,
            "family": spec.family,
            "inner_radius": spec.inner_radius,
            "outer_radius": spec.outer_radius,
            "taper": spec.taper,
        },
        "recipient_center": list(recipient_partition.center),
        "donor_center": list(donor_partition.center),
        "donor_to_recipient_shift": list(donor_to_recipient),
        "physical_balance": balance,
        "base_cohort_balance": cohort_audit,
        "appended_tracer_balance": appended_audit,
        "memory_total_matched": False,
        "memory_reason": "Mf/rho is the protected history payload; total-matching it would erase the intended contrast",
        "uptake_previous_readout": "recipient preserved; not read by next update",
        "scheduler_step_preserved": True,
        "persistent_previous_flux_gradient_rng_or_cache": None,
        "changed_cells": int(changed.sum()),
        "affected_radius": float(np.max(recipient_partition.distance[changed])) if changed.any() else 0.0,
        "outside_C_change": False,
    }
