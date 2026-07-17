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
