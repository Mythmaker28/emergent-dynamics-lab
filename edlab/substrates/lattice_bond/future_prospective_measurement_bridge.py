"""Prospective measurement bridge: engine execution through anchored analysis access.

This module owns one chain end to end and accepts no product of that chain as an
input:

    schedule validation -> engine execution -> per-step passive-cohort advection
    -> per-sampled-frame float/mask/morphology capture -> canonical persistence
    -> re-read from disk -> owned-pipeline execution on the RE-READ masks
    -> nested measurement root -> fail-closed external-anchor gate
    -> owned analysis access

Nothing here is a scientific result.  Every number it writes is a mechanical
reproducibility binding.

Derivation of the cohort advection arguments
--------------------------------------------
``LatticeBondEngine.step`` applies

    ``matter_active = matter_natural * plan.matter_scale``
    ``matter_natural = matter_forward - matter_reverse``
    ``m_next = m - dt * divergence(matter_active)``

so the flux that is *actually applied* to the matter field is

    ``scale * forward - scale * reverse``

i.e. the gross one-way flows each multiplied by the same face coefficient.
``advance_passive_tracer`` re-derives ``expected_post = pre - dt *
divergence(forward - reverse)`` from the two gross flows it is handed and
refuses anything inconsistent with the supplied ``post_matter``.  Therefore the
only admissible arguments are ``ledger.matter_forward * ledger.matter_scale``
and ``ledger.matter_reverse * ledger.matter_scale``.  When no intervention is in
force the engine substitutes ``FaceIntervention.open`` and ``matter_scale`` is
all ones, so the same expression is used unconditionally: there is no branch,
because there is no difference.  Both scaled flows remain finite, non-negative
float64 fields, which is what the tracer contract requires.

Enrolment of the passive cohort
-------------------------------
The cohort is enrolled ONCE, at the first sampled frame, and it is enrolled
ENTITY-LOCALLY.  For every component :func:`detect_components` reports at that
frame under the measurement specification, the matter standing inside that
component's cell support is labelled; every other cell is labelled zero.  The
single tracer array carries the union of the per-component cohorts, so the
enrolled field is the matter field masked by the union of the component
supports.  Matter standing in cells that belong to no detected component is NOT
labelled.

Enrolling the cohort as the ENTIRE matter field is degenerate, and that is the
reason enrolment is component-local rather than global.
:func:`advance_passive_tracer` advects the cohort through exactly the gross
flows that advect the matter, so a tracer initialised to the whole matter field
reproduces the matter field bit-exactly at every later step.  ``cohort_mass``
then equals ``mass`` for every component at every frame, ``cohort_residual`` is
identically ``1.0``, the turnover channel is degenerate, and it can never
measure material replacement.  Under the component-local rule the residual
instead starts at exactly ``1.0`` for each enrolled component and falls as
unlabelled matter flows into it: the residual is the fraction of the
component's CURRENT material that was present at enrolment.

Limitation register
-------------------
* **MB-L1 — no physical time is authenticated.**  ``sampled_frames`` are engine
  step labels read back from ``LatticeBondState.step``.  They witness that the
  engine's own counter reached that value inside this process.  They witness
  nothing about wall-clock time, calendar time, or any external event.
* **MB-L2 — ``published_at_label`` is an opaque caller label.**  It is copied
  into the receipt and into ``ANCHOR_RECEIPT.json`` verbatim.  It is never
  parsed, never compared against a clock, and never authenticated.  A receipt
  claiming an anchoring date is making an unverified assertion.
* **MB-L3 — source hashes are reproducibility bindings, not authority.**  The
  SHA-256 values recorded in ``source_bindings`` are read from disk at call
  time.  They detect an edit to a source file between publication and
  verification.  They certify nothing about the correctness or the provenance of
  those files, and anyone able to write the files can also rewrite the bindings.
* **MB-L4 — :class:`DeterministicAppendOnlyLog` is test-only.**  It never
  contacts a network, has no witnesses, no timestamping authority and no
  external observers.  It is a deterministic hash chain that makes the
  fail-closed anchor gate exercisable.  A real anchor must be supplied by the
  caller through :data:`AnchorVerifier`.
* **MB-L5 — morphology is bound but not consumed.**  Component area, mass,
  centroid, radius of gyration, wrap flags and pixel support are digested into
  the frame digests and hence into the measurement root.  The lifecycle
  semantics reached through the owned pipeline read none of them: the lifecycle
  document binds the schedule, the assignments, the events and the track
  records.  A morphology change that leaves the track topology intact is
  therefore refused *here* and would have been accepted *there*.  That is the
  whole of the added binding; see OP-L3 of the owned pipeline.
* **MB-L6 — the cohort measures residual, and "replacement" is a DECLARED
  CONVENTION.**  ``cohort_residual`` is ``cohort_mass / mass`` for a detected
  component, where ``cohort_mass`` is the labelled cohort still inside the
  component's cells; it is the fraction of that component's current material
  that was already present when the cohort was enrolled, and it is ``0.0`` by
  declaration when ``mass`` is zero.  ``MeasurementSpec.cohort_residual_fraction`` is a declared
  convention recorded in the evidence; it is NOT an API tolerance.  It is never
  passed to :func:`advance_passive_tracer`, which has no ``epsilon`` parameter
  and admits none: its only tolerance is an internal conservation check derived
  from the supplied fields.  No function in this module compares a residual
  against ``cohort_residual_fraction`` to decide anything.
* **MB-L7 — the reproduced mask is the only cross-binding to the owned
  pipeline.**  The owned pipeline materialises every mask cell to
  ``present_matter`` and every other cell to ``absent_matter``, then applies its
  own detector.  Outside ``absent_matter < matter_threshold <= present_matter``
  the mask handed to the pipeline is not the mask the pipeline reproduces, so
  :class:`MeasurementSpec` refuses such a threshold outright.
* **MB-L8 — the measurement root does not bind ``step_count``.**  The root binds
  exactly the fields listed in :func:`_root_from_document`.  ``step_count`` and
  the run directory path are carried in the measurement document and are bound
  only by ``BRIDGE_BINDING.json``'s document digest, which is itself not inside
  the root.  They are bookkeeping, not evidence.
* **MB-L9 — verification is reproduction, not acquisition.**  As with the owned
  pipeline, re-reading proves that the persisted bytes reproduce the published
  digests.  It does not prove that those bytes are the ones the engine produced.
  Within one call of :func:`run_measurement_bridge` the two coincide because
  this module writes what it computed; afterwards they need not.
* **MB-L10 — the cohort is enrolled once, and only inside detected components.**
  A cohort enrolled as the entire matter field is degenerate: it is advected by
  the very flows that move the matter, so ``cohort_residual`` would be
  identically ``1.0`` and the channel would measure nothing.  Enrolment is
  therefore component-local, and the price is paid on the other side.  Matter in
  cells belonging to no component detected at the first sampled frame is never
  labelled, so ``total_cohort`` is in general strictly below ``total_matter``; a
  component that first appears after enrolment carries whatever label the matter
  that flowed into it happened to hold, not a residual of its own history; and a
  component that merges with an unlabelled one reports a residual of the merged
  body.  ``cohort_residual`` is a statement about the enrolled cohort and about
  nothing else.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import tempfile
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from . import engine as _engine
from . import future_lifecycle_owned_pipeline as _owned
from . import future_lifecycle_runner as _runner
from . import instrumentation as _instrumentation
from . import lifecycle as _lifecycle
from .engine import (
    FaceIntervention,
    LatticeBondEngine,
    LatticeBondSpec,
    LatticeBondState,
)
from .future_lifecycle_owned_pipeline import (
    OWNED_BINDING_NAME,
    _FRAME_MATERIALIZATION,
    OwnedPipelineError,
    OwnedPipelineRecord,
    open_owned_analysis_access,
    run_owned_future_pipeline,
)
from .future_lifecycle_runner import AnalysisAccess
from .instrumentation import (
    DetectorSpec,
    TrackerSpec,
    advance_passive_tracer,
    detect_components,
)

SCHEMA_VERSION = "future-prospective-measurement-bridge/v1"
BRIDGE_VERSION = "1.0.0"
MEASUREMENT_DOCUMENT_NAME = "MEASUREMENT.json"
BRIDGE_BINDING_NAME = "BRIDGE_BINDING.json"
ANCHOR_RECEIPT_NAME = "ANCHOR_RECEIPT.json"
MEASUREMENT_FRAME_DIRECTORY = "measurement_frames"

#: Read from the owned pipeline's inert materialisation table at import time.
ABSENT_MATTER = float(_FRAME_MATERIALIZATION["absent_matter"])
PRESENT_MATTER = float(_FRAME_MATERIALIZATION["present_matter"])

_CANONICALIZATION = {
    "encoding": "utf-8",
    "json_ensure_ascii": True,
    "json_nan_allowed": False,
    "json_separators": ",:",
    "json_sort_keys": True,
}

_CHANNEL_ENCODING = {
    "bond": "float64-little-endian-C-order",
    "mask": "uint8-0-or-1-C-order",
    "matter": "float64-little-endian-C-order",
    "resource": "float64-little-endian-C-order",
    "tracer": "float64-little-endian-C-order",
}

_CHANNELS = ("bond", "mask", "matter", "resource", "tracer")

_PROVENANCE_DISCLOSURE = (
    "sampled_frames are engine step labels read back from LatticeBondState.step; they are "
    "not evidence of physical elapsed time. published_at_label in an anchor receipt is an "
    "opaque caller label and is not authenticated. These digests bind bytes, not authority: "
    "any party able to write this directory can recompute them."
)

#: Channels a caller might expect and which this substrate cannot supply.  Recorded
#: in every measurement document and bound into the measurement root.
_UNAVAILABLE_CHANNELS = {
    "signed_internal_state_variable": (
        "engine state fields m>=0, n>=0, b in [0,1]; none takes both signs"
    ),
    "symmetry_partnered_convention_observable": (
        "matter flux is M*(chi - chi_plus) with M>=0; sign is fixed by a scalar "
        "potential difference"
    ),
    "transverse_orbital_chirality_term": (
        "absent from the lattice-bond update; OrbitalSpec belongs to the CORE V0 "
        "particle substrate"
    ),
}

_SPEC_FLOAT_KEYS = (
    "cohort_residual_fraction",
    "matter_threshold",
    "max_area_ratio",
    "max_centroid_displacement",
    "unique_score_margin",
)

_SPEC_KEYS = frozenset(_SPEC_FLOAT_KEYS + ("dilation_radius", "min_cells"))

_DOCUMENT_KEYS = frozenset(
    (
        "bridge_version",
        "canonicalization",
        "channel_encoding",
        "frame_directory_relative_path",
        "frame_shape",
        "frames",
        "initial_state_sha256",
        "intervention_sha256",
        "law_spec_sha256",
        "measurement_root_sha256",
        "measurement_spec",
        "measurement_spec_sha256",
        "owned_root_sha256",
        "provenance_disclosure",
        "sampled_frames",
        "schema_version",
        "source_bindings",
        "step_count",
        "unavailable_channels",
    )
)

_BINDING_KEYS = frozenset(
    (
        "bridge_version",
        "canonicalization",
        "measurement_document_relative_path",
        "measurement_document_sha256",
        "measurement_root_sha256",
        "owned_binding_relative_path",
        "owned_binding_sha256",
        "owned_root_sha256",
        "schema_version",
    )
)

_RECEIPT_KEYS = frozenset(
    ("published_at_label", "reference", "root_sha256", "schema_version", "venue")
)

_OWNED_ROOT_FIELDS = (
    "acquisition_ledger_sha256",
    "analysis_evidence_sha256",
    "completion_manifest_sha256",
    "detected_component_count",
    "entries_sha256",
    "frame_digests",
    "frame_shape",
    "invocation_count",
    "lifecycle_document_sha256",
    "sample_count",
    "sampled_frames",
    "terminal_record_count",
    "track_count",
)


class BridgeError(RuntimeError):
    """Base class for every bridge failure.  Never converted into success."""


class BridgeSpecificationError(BridgeError):
    """A measurement specification is outside the domain this bridge can honour."""


class BridgeScheduleError(BridgeError):
    """The declared schedule is absent, malformed, or unreachable from the state."""


class BridgeChannelError(BridgeError):
    """A persisted channel payload is malformed and cannot be decoded."""


class BridgeEvidenceError(BridgeError):
    """Persisted measurement evidence is absent, malformed or inconsistent."""


class BridgeAnchorError(BridgeError):
    """The external anchor is absent, does not bind this root, or did not verify."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_exact_bytes(path: Path) -> bytes:
    """Read the exact persisted bytes.  Never returns a cached in-memory object."""

    with path.open("rb") as handle:
        return handle.read()


def _plain_int(value: object) -> bool:
    """A JSON integer, never a bool.  ``True == 1`` must not slip through a check."""

    return isinstance(value, int) and not isinstance(value, bool)


def _source_bindings() -> dict[str, str]:
    """Digest every module whose behaviour this evidence depends on, from disk.

    Read on every call, so a later edit to any of them invalidates previously
    published evidence.  See MB-L3: this is a reproducibility binding, not an
    authority certificate.
    """

    return {
        "engine_sha256": _sha256_bytes(_read_exact_bytes(Path(_engine.__file__))),
        "future_lifecycle_owned_pipeline_sha256": _sha256_bytes(
            _read_exact_bytes(Path(_owned.__file__))
        ),
        "future_lifecycle_runner_sha256": _sha256_bytes(
            _read_exact_bytes(Path(_runner.__file__))
        ),
        "future_prospective_measurement_bridge_sha256": _sha256_bytes(
            _read_exact_bytes(Path(__file__))
        ),
        "instrumentation_sha256": _sha256_bytes(
            _read_exact_bytes(Path(_instrumentation.__file__))
        ),
        "lifecycle_sha256": _sha256_bytes(_read_exact_bytes(Path(_lifecycle.__file__))),
    }


def _atomic_create(target: Path, payload: bytes) -> None:
    """Atomically create one non-overwriting file.

    Mirrors the owned pipeline's primitive: ``mkstemp`` plus ``os.link``, with no
    ``exists()`` pre-check, because creation *is* the check.  Every ``OSError`` is
    typed into :class:`BridgeEvidenceError` so nothing escapes the hierarchy.
    """

    descriptor, partial_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".partial"
    )
    partial = Path(partial_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(partial, target)
        except OSError as exc:
            raise BridgeEvidenceError(
                f"could not publish {target.name} without overwriting: {exc}"
            ) from exc
    finally:
        partial.unlink(missing_ok=True)


@dataclass(frozen=True)
class MeasurementSpec:
    """Detector, tracker and cohort declaration for one measurement bridge run."""

    matter_threshold: float = 0.45
    min_cells: int = 3
    max_centroid_displacement: float = 3.0
    max_area_ratio: float = 3.0
    dilation_radius: int = 1
    unique_score_margin: float = 1e-12
    cohort_residual_fraction: float = 0.05

    def __post_init__(self) -> None:
        for name in _SPEC_FLOAT_KEYS:
            if not math.isfinite(float(getattr(self, name))):
                raise BridgeSpecificationError(f"{name} must be finite")
        if self.min_cells < 1:
            raise BridgeSpecificationError("min_cells must be >=1")
        if self.dilation_radius < 0:
            raise BridgeSpecificationError("dilation_radius must be >=0")
        if self.max_area_ratio < 1.0:
            raise BridgeSpecificationError("max_area_ratio must be >=1")
        if self.max_centroid_displacement <= 0.0:
            raise BridgeSpecificationError("max_centroid_displacement must be positive")
        if self.unique_score_margin <= 0.0:
            raise BridgeSpecificationError("unique_score_margin must be positive")
        if not 0.0 < self.cohort_residual_fraction < 1.0:
            raise BridgeSpecificationError(
                "cohort_residual_fraction is a declared convention in (0,1)"
            )
        if not ABSENT_MATTER < self.matter_threshold <= PRESENT_MATTER:
            raise BridgeSpecificationError(
                "matter_threshold must satisfy "
                f"{ABSENT_MATTER!r} < matter_threshold <= {PRESENT_MATTER!r}; outside that "
                "interval the mask handed to the owned pipeline is not the mask the "
                "pipeline's own detector reproduces"
            )

    def detector_spec(self) -> DetectorSpec:
        return DetectorSpec(
            matter_threshold=float(self.matter_threshold), min_cells=int(self.min_cells)
        )

    def tracker_spec(self) -> TrackerSpec:
        return TrackerSpec(
            max_centroid_displacement=float(self.max_centroid_displacement),
            max_area_ratio=float(self.max_area_ratio),
            dilation_radius=int(self.dilation_radius),
            unique_score_margin=float(self.unique_score_margin),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "cohort_residual_fraction": float(self.cohort_residual_fraction),
            "dilation_radius": int(self.dilation_radius),
            "matter_threshold": float(self.matter_threshold),
            "max_area_ratio": float(self.max_area_ratio),
            "max_centroid_displacement": float(self.max_centroid_displacement),
            "min_cells": int(self.min_cells),
            "unique_score_margin": float(self.unique_score_margin),
        }


@dataclass(frozen=True)
class ComponentMeasurement:
    """One detected component, its pixel support and its labelled-cohort residual."""

    index: int
    area: int
    mass: float
    centroid_y: float
    centroid_x: float
    radius_gyration: float
    wraps_y: bool
    wraps_x: bool
    pixel_support_sha256: str
    cohort_mass: float
    cohort_residual: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "area": int(self.area),
            "centroid_x": float(self.centroid_x),
            "centroid_y": float(self.centroid_y),
            "cohort_mass": float(self.cohort_mass),
            "cohort_residual": float(self.cohort_residual),
            "index": int(self.index),
            "mass": float(self.mass),
            "pixel_support_sha256": self.pixel_support_sha256,
            "radius_gyration": float(self.radius_gyration),
            "wraps_x": bool(self.wraps_x),
            "wraps_y": bool(self.wraps_y),
        }


@dataclass(frozen=True)
class FrameMeasurement:
    """Every channel digest and every morphology value bound at one sampled frame."""

    frame: int
    ordinal: int
    matter_sha256: str
    resource_sha256: str
    bond_sha256: str
    tracer_sha256: str
    mask_sha256: str
    total_matter: float
    total_cohort: float
    components: tuple[ComponentMeasurement, ...]
    frame_digest_sha256: str

    def as_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["frame_digest_sha256"] = self.frame_digest_sha256
        return payload

    def _core(self) -> dict[str, Any]:
        return {
            "bond_sha256": self.bond_sha256,
            "components": [item.as_dict() for item in self.components],
            "frame": int(self.frame),
            "mask_sha256": self.mask_sha256,
            "matter_sha256": self.matter_sha256,
            "ordinal": int(self.ordinal),
            "resource_sha256": self.resource_sha256,
            "total_cohort": float(self.total_cohort),
            "total_matter": float(self.total_matter),
            "tracer_sha256": self.tracer_sha256,
        }


@dataclass(frozen=True)
class VerifiedMeasurement:
    """Measurement evidence rebuilt from disk.  Holding one grants nothing."""

    run_directory: str
    sampled_frames: tuple[int, ...]
    step_count: int
    frame_shape: tuple[int, int]
    frames: tuple[FrameMeasurement, ...]
    measurement_spec: MeasurementSpec
    measurement_spec_sha256: str
    law_spec_sha256: str
    initial_state_sha256: str
    intervention_sha256: str | None
    source_bindings: Mapping[str, str]
    unavailable_channels: Mapping[str, str]
    owned_root_sha256: str
    measurement_root_sha256: str


@dataclass(frozen=True)
class MeasurementRecord:
    """Inert description of one completed bridge run.  Holding it grants nothing."""

    run_directory: str
    sampled_frames: tuple[int, ...]
    step_count: int
    frame_shape: tuple[int, int]
    frames: tuple[FrameMeasurement, ...]
    measurement_spec_sha256: str
    law_spec_sha256: str
    initial_state_sha256: str
    intervention_sha256: str | None
    source_bindings: Mapping[str, str]
    unavailable_channels: Mapping[str, str]
    owned_record: OwnedPipelineRecord
    owned_root_sha256: str
    measurement_root_sha256: str


@dataclass(frozen=True)
class AnchorReceipt:
    """A caller-supplied external anchoring claim.  ``published_at_label`` is opaque.

    See MB-L2: the label is never parsed and never authenticated.  A receipt is
    evidence that *some* anchor bound ``root_sha256``; the venue, the reference
    and the label are exactly as strong as the verifier the caller supplies.
    """

    root_sha256: str
    venue: str
    reference: str
    published_at_label: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "published_at_label": self.published_at_label,
            "reference": self.reference,
            "root_sha256": self.root_sha256,
            "schema_version": SCHEMA_VERSION,
            "venue": self.venue,
        }


AnchorVerifier = Callable[[AnchorReceipt], bool]


class DeterministicAppendOnlyLog:
    """Test-only fake anchor.  NEVER contacts a network.  See MB-L4.

    Append-only hash chain: ``head_0 = sha256(b"genesis")`` and publishing a
    digest ``d`` yields ``head_{k+1} = sha256(head_k || d)``; the reference is the
    hex of ``head_{k+1}``.  :meth:`verify` recomputes the whole chain and returns
    ``True`` iff the receipt's reference is the head produced by that exact digest
    at some position.
    """

    GENESIS = hashlib.sha256(b"genesis").digest()
    __slots__ = ("_published", "venue")

    def __init__(self, venue: str = "deterministic-append-only-log/test-only") -> None:
        self.venue = str(venue)
        self._published: list[tuple[str, bytes]] = []

    def _heads(self) -> list[bytes]:
        head = self.GENESIS
        heads: list[bytes] = []
        for _hex_digest, raw in self._published:
            head = hashlib.sha256(head + raw).digest()
            heads.append(head)
        return heads

    def publish(
        self,
        digest: str,
        *,
        published_at_label: str = "unauthenticated-caller-label",
    ) -> AnchorReceipt:
        self._published.append((str(digest), bytes.fromhex(str(digest))))
        return AnchorReceipt(
            root_sha256=str(digest),
            venue=self.venue,
            reference=self._heads()[-1].hex(),
            published_at_label=str(published_at_label),
        )

    def verify(self, receipt: AnchorReceipt) -> bool:
        heads = self._heads()
        for position, (hex_digest, _raw) in enumerate(self._published):
            if hex_digest == receipt.root_sha256 and heads[position].hex() == receipt.reference:
                return True
        return False


def _channel_relative_path(position: int, channel: str) -> str:
    return f"{MEASUREMENT_FRAME_DIRECTORY}/frame_{position:06d}_{channel}.bin"


def _float_bytes(array: np.ndarray) -> bytes:
    return np.ascontiguousarray(array, dtype="<f8").tobytes()


def _mask_bytes(mask: np.ndarray) -> bytes:
    return np.ascontiguousarray(mask, dtype=np.bool_).astype(np.uint8).tobytes(order="C")


def _pixel_support_bytes(cells: Sequence[int]) -> bytes:
    return b"".join(struct.pack("<q", int(cell)) for cell in sorted(cells))


def _decode_float(payload: bytes, shape: tuple[int, ...], label: str) -> np.ndarray:
    expected = 8
    for extent in shape:
        expected *= extent
    if len(payload) != expected:
        raise BridgeChannelError(f"persisted {label} channel has the wrong byte length")
    values = np.frombuffer(payload, dtype="<f8").reshape(shape).astype(np.float64)
    if not bool(np.isfinite(values).all()):
        raise BridgeChannelError(f"persisted {label} channel is not finite")
    return np.ascontiguousarray(values)


def _decode_mask(payload: bytes, shape: tuple[int, int]) -> np.ndarray:
    if len(payload) != shape[0] * shape[1]:
        raise BridgeChannelError("persisted mask channel has the wrong byte length")
    values = np.frombuffer(payload, dtype=np.uint8)
    if bool(np.any(values > 1)):
        raise BridgeChannelError("persisted mask channel is not a canonical 0/1 mask")
    return values.reshape(shape).astype(bool)


def _validated_schedule(sampled_frames: Sequence[int], initial_step: int) -> tuple[int, ...]:
    """Validate the declared schedule BEFORE the engine is touched.

    Plain integers only: ``bool`` is refused because ``True == 1`` must not become
    a frame label, and NumPy integers are refused because the persisted schedule
    must be a JSON integer list with no silent coercion.
    """

    if sampled_frames is None:
        raise BridgeScheduleError("sampled_frames is mandatory; explicit None is refused")
    if isinstance(sampled_frames, (str, bytes, bytearray, Mapping)) or not isinstance(
        sampled_frames, Sequence
    ):
        raise BridgeScheduleError("sampled_frames must be an ordered sequence of integers")
    values = tuple(sampled_frames)
    if not values:
        raise BridgeScheduleError("sampled_frames must not be empty")
    for value in values:
        if not _plain_int(value):
            raise BridgeScheduleError("sampled_frames entries must be plain integers")
    for earlier, later in zip(values, values[1:]):
        if later <= earlier:
            raise BridgeScheduleError("sampled_frames must be strictly increasing")
    if values[0] < initial_step:
        raise BridgeScheduleError(
            "sampled_frames must not precede the initial engine step "
            f"{initial_step}"
        )
    return values


@dataclass(frozen=True)
class _Capture:
    label: int
    matter: np.ndarray
    resource: np.ndarray
    bond: np.ndarray
    tracer: np.ndarray


def _enrolled_cohort(state: LatticeBondState, detector: DetectorSpec) -> np.ndarray:
    """Label the matter inside every detected component and nothing else.

    The enrolled field is ``state.m`` masked by the union of the cell supports of
    the components :func:`detect_components` reports for ``state``.  A cell that
    belongs to no detected component is labelled ``0.0``.

    Enrolling the whole matter field instead would be degenerate: the cohort is
    advected by exactly the flows that advect the matter, so the tracer would
    reproduce the matter field and ``cohort_residual`` would be identically
    ``1.0`` at every frame.  See MB-L10.
    """

    matter = np.ascontiguousarray(state.m, dtype=np.float64)
    cohort = np.zeros_like(matter)
    flat_matter = matter.reshape(-1)
    flat_cohort = cohort.reshape(-1)
    for detected in detect_components(state, detector, frame=int(state.step)):
        for cell in detected.cells:
            flat_cohort[int(cell)] = flat_matter[int(cell)]
    return cohort


def _execute(
    law_spec: LatticeBondSpec,
    initial_state: LatticeBondState,
    schedule: tuple[int, ...],
    intervention: FaceIntervention | None,
    backend: str,
    detector: DetectorSpec,
) -> tuple[tuple[_Capture, ...], int]:
    """Step the engine, advect the cohort, and capture every sampled frame.

    The label bound for each sample is ``state.step`` read from the engine state,
    never the declared value.  A disagreement is a schedule failure.

    The cohort is enrolled at the FIRST sampled frame and component-locally, by
    :func:`_enrolled_cohort`; steps taken before that frame advect nothing,
    because there is no cohort yet.
    """

    engine = LatticeBondEngine(law_spec)
    state = initial_state.copy()
    tracer: np.ndarray | None = None
    captures: list[_Capture] = []
    step_count = 0
    for label in schedule:
        while int(state.step) < label:
            pre = state
            result = engine.step(pre, intervention, backend=backend)
            ledger = result.ledger
            if tracer is not None:
                try:
                    tracer = advance_passive_tracer(
                        tracer,
                        pre.m,
                        ledger.matter_forward * ledger.matter_scale,
                        ledger.matter_reverse * ledger.matter_scale,
                        result.state.m,
                        law_spec.dt,
                    )
                except ValueError as exc:
                    raise BridgeChannelError(
                        "the passive cohort refused the engine's gross matter flows: "
                        f"{exc}"
                    ) from exc
            state = result.state
            step_count += 1
        if int(state.step) != label:
            raise BridgeScheduleError(
                f"engine state step {int(state.step)} does not equal declared frame {label}"
            )
        if tracer is None:
            tracer = _enrolled_cohort(state, detector)
        captures.append(
            _Capture(
                label=int(state.step),
                matter=state.m.copy(),
                resource=state.n.copy(),
                bond=state.b.copy(),
                tracer=tracer.copy(),
            )
        )
    return tuple(captures), step_count


def _persist_captures(
    directory: Path, captures: Sequence[_Capture], threshold: float
) -> None:
    for position, capture in enumerate(captures):
        payloads = {
            "bond": _float_bytes(capture.bond),
            "mask": _mask_bytes(capture.matter >= threshold),
            "matter": _float_bytes(capture.matter),
            "resource": _float_bytes(capture.resource),
            "tracer": _float_bytes(capture.tracer),
        }
        for channel in _CHANNELS:
            _atomic_create(
                directory / _channel_relative_path(position, channel), payloads[channel]
            )


def _refuse_extra_frames(frame_directory: Path, count: int) -> None:
    """Refuse a missing, extra or non-regular entry in the measurement frame directory."""

    if not frame_directory.is_dir():
        raise BridgeEvidenceError("no measurement frame directory: evidence is incomplete")
    observed: list[str] = []
    for entry in os.scandir(frame_directory):
        if not entry.is_file(follow_symlinks=False):
            raise BridgeEvidenceError(
                "measurement frame directory contains a non-regular entry"
            )
        observed.append(entry.name)
    expected = sorted(
        f"frame_{position:06d}_{channel}.bin"
        for position in range(count)
        for channel in _CHANNELS
    )
    if sorted(observed) != expected:
        raise BridgeEvidenceError(
            "measurement frame directory contains missing or unexpected entries"
        )


def _reread_frames(
    directory: Path,
    measurement_spec: MeasurementSpec,
    schedule: Sequence[int],
    shape: tuple[int, int],
) -> tuple[FrameMeasurement, ...]:
    """Rebuild every frame measurement from the persisted bytes and nothing else.

    The mask cross-binding is enforced here: the persisted mask must equal
    ``matter >= matter_threshold`` recomputed from the persisted float matter.
    """

    _refuse_extra_frames(directory / MEASUREMENT_FRAME_DIRECTORY, len(schedule))
    detector = measurement_spec.detector_spec()
    frames: list[FrameMeasurement] = []
    for position, label in enumerate(schedule):
        payloads = {
            channel: _read_exact_bytes(directory / _channel_relative_path(position, channel))
            for channel in _CHANNELS
        }
        matter = _decode_float(payloads["matter"], shape, "matter")
        resource = _decode_float(payloads["resource"], shape, "resource")
        bond = _decode_float(payloads["bond"], (2, *shape), "bond")
        tracer = _decode_float(payloads["tracer"], shape, "tracer")
        mask = _decode_mask(payloads["mask"], shape)
        if not bool(np.array_equal(mask, matter >= measurement_spec.matter_threshold)):
            raise BridgeEvidenceError(
                "persisted mask is not the threshold of the persisted float matter"
            )
        state = LatticeBondState(matter, resource, bond, int(label))
        flat_tracer = tracer.reshape(-1)
        components: list[ComponentMeasurement] = []
        for detected in detect_components(state, detector, frame=int(label)):
            cohort_mass = math.fsum(
                float(flat_tracer[int(cell)]) for cell in detected.cells
            )
            components.append(
                ComponentMeasurement(
                    index=int(detected.index),
                    area=int(detected.area),
                    mass=float(detected.mass),
                    centroid_y=float(detected.centroid_y),
                    centroid_x=float(detected.centroid_x),
                    radius_gyration=float(detected.radius_gyration),
                    wraps_y=bool(detected.wraps_y),
                    wraps_x=bool(detected.wraps_x),
                    pixel_support_sha256=_sha256_bytes(
                        _pixel_support_bytes(detected.cells)
                    ),
                    cohort_mass=cohort_mass,
                    cohort_residual=(
                        cohort_mass / float(detected.mass) if detected.mass else 0.0
                    ),
                )
            )
        core = {
            "bond_sha256": _sha256_bytes(payloads["bond"]),
            "components": [item.as_dict() for item in components],
            "frame": int(label),
            "mask_sha256": _sha256_bytes(payloads["mask"]),
            "matter_sha256": _sha256_bytes(payloads["matter"]),
            "ordinal": position,
            "resource_sha256": _sha256_bytes(payloads["resource"]),
            "total_cohort": math.fsum(float(value) for value in flat_tracer),
            "total_matter": math.fsum(float(value) for value in matter.reshape(-1)),
            "tracer_sha256": _sha256_bytes(payloads["tracer"]),
        }
        frames.append(
            FrameMeasurement(
                frame=core["frame"],
                ordinal=core["ordinal"],
                matter_sha256=core["matter_sha256"],
                resource_sha256=core["resource_sha256"],
                bond_sha256=core["bond_sha256"],
                tracer_sha256=core["tracer_sha256"],
                mask_sha256=core["mask_sha256"],
                total_matter=core["total_matter"],
                total_cohort=core["total_cohort"],
                components=tuple(components),
                frame_digest_sha256=_sha256_bytes(_canonical_bytes(core)),
            )
        )
    return tuple(frames)


def _owned_root_sha256(record: OwnedPipelineRecord) -> str:
    """Digest the owned pipeline record's own digest and count fields.

    The run directory path and the progress enum are deliberately excluded: the
    first is not evidence and the second is not a digest.
    """

    payload: dict[str, Any] = {}
    for name in _OWNED_ROOT_FIELDS:
        value = getattr(record, name)
        payload[name] = list(value) if isinstance(value, tuple) else value
    return _sha256_bytes(_canonical_bytes(payload))


def _root_from_document(document: Mapping[str, Any]) -> str:
    """THE measurement root.  Binds everything above it, including the owned root."""

    return _sha256_bytes(
        _canonical_bytes(
            {
                "bridge_version": document["bridge_version"],
                "frame_digests": [
                    item["frame_digest_sha256"] for item in document["frames"]
                ],
                "initial_state_sha256": document["initial_state_sha256"],
                "intervention_sha256": document["intervention_sha256"],
                "law_spec_sha256": document["law_spec_sha256"],
                "measurement_spec_sha256": document["measurement_spec_sha256"],
                "owned_root_sha256": document["owned_root_sha256"],
                "sampled_frames": list(document["sampled_frames"]),
                "schema_version": document["schema_version"],
                "source_bindings": dict(document["source_bindings"]),
                "unavailable_channels": dict(document["unavailable_channels"]),
            }
        )
    )


def _read_canonical_object(
    path: Path,
    keys: frozenset[str],
    label: str,
    error: type[BridgeError] = BridgeEvidenceError,
) -> tuple[dict[str, Any], bytes]:
    """Read one canonical JSON object with an exact key set, or fail closed."""

    if not path.is_file():
        raise error(f"no {label}: measured analysis access remains locked")
    raw = _read_exact_bytes(path)
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise error(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise error(f"{label} must be a JSON object")
    if set(value) != set(keys):
        raise error(f"{label} key set mismatch")
    try:
        canonical = _canonical_bytes(value)
    except ValueError as exc:
        raise error(f"{label} is not canonically representable: {exc}") from exc
    if canonical != raw:
        raise error(f"{label} bytes are not canonical")
    return value, raw


def _verified_evidence(directory: Path) -> VerifiedMeasurement:
    """Re-read and re-verify every local artefact.  No anchor is consulted here."""

    document, raw = _read_canonical_object(
        directory / MEASUREMENT_DOCUMENT_NAME, _DOCUMENT_KEYS, "measurement document"
    )
    if (
        document["schema_version"] != SCHEMA_VERSION
        or document["bridge_version"] != BRIDGE_VERSION
        or document["canonicalization"] != _CANONICALIZATION
        or document["channel_encoding"] != _CHANNEL_ENCODING
        or document["frame_directory_relative_path"] != MEASUREMENT_FRAME_DIRECTORY
        or document["provenance_disclosure"] != _PROVENANCE_DISCLOSURE
    ):
        raise BridgeEvidenceError("measurement document static declarations mismatch")
    if document["source_bindings"] != _source_bindings():
        raise BridgeEvidenceError(
            "measurement document source bindings do not match the executing sources"
        )
    if document["unavailable_channels"] != dict(_UNAVAILABLE_CHANNELS):
        raise BridgeEvidenceError("measurement document unavailable-channel register mismatch")

    payload = document["measurement_spec"]
    if (
        not isinstance(payload, dict)
        or set(payload) != set(_SPEC_KEYS)
        or not _plain_int(payload["min_cells"])
        or not _plain_int(payload["dilation_radius"])
        or any(
            isinstance(payload[name], bool) or not isinstance(payload[name], (int, float))
            for name in _SPEC_FLOAT_KEYS
        )
    ):
        raise BridgeEvidenceError("persisted measurement specification is malformed")
    measurement_spec = MeasurementSpec(**payload)
    measurement_spec_sha256 = _sha256_bytes(_canonical_bytes(measurement_spec.as_dict()))
    if measurement_spec_sha256 != document["measurement_spec_sha256"]:
        raise BridgeEvidenceError("persisted measurement specification digest mismatch")

    schedule = document["sampled_frames"]
    if (
        not isinstance(schedule, list)
        or not schedule
        or any(not _plain_int(value) for value in schedule)
    ):
        raise BridgeEvidenceError("persisted schedule is malformed")
    if any(later <= earlier for earlier, later in zip(schedule, schedule[1:])):
        raise BridgeEvidenceError("persisted schedule must be strictly increasing")
    shape_payload = document["frame_shape"]
    if (
        not isinstance(shape_payload, list)
        or len(shape_payload) != 2
        or any(not _plain_int(value) for value in shape_payload)
        or min(shape_payload) < 2
    ):
        raise BridgeEvidenceError("persisted frame shape is malformed")
    if not _plain_int(document["step_count"]) or document["step_count"] < 0:
        raise BridgeEvidenceError("persisted step count is malformed")

    shape = (int(shape_payload[0]), int(shape_payload[1]))
    frames = _reread_frames(directory, measurement_spec, schedule, shape)
    if [item.as_dict() for item in frames] != document["frames"]:
        raise BridgeEvidenceError(
            "persisted frames do not reproduce the published frame measurements"
        )
    if _root_from_document(document) != document["measurement_root_sha256"]:
        raise BridgeEvidenceError("recomputed measurement root does not match the document")

    binding, _binding_raw = _read_canonical_object(
        directory / BRIDGE_BINDING_NAME, _BINDING_KEYS, "bridge binding"
    )
    if (
        binding["schema_version"] != SCHEMA_VERSION
        or binding["bridge_version"] != BRIDGE_VERSION
        or binding["canonicalization"] != _CANONICALIZATION
        or binding["measurement_document_relative_path"] != MEASUREMENT_DOCUMENT_NAME
        or binding["owned_binding_relative_path"] != OWNED_BINDING_NAME
    ):
        raise BridgeEvidenceError("bridge binding static declarations mismatch")
    if (
        binding["measurement_document_sha256"] != _sha256_bytes(raw)
        or binding["measurement_root_sha256"] != document["measurement_root_sha256"]
        or binding["owned_root_sha256"] != document["owned_root_sha256"]
    ):
        raise BridgeEvidenceError("bridge binding does not match the measurement document")
    owned_binding_path = directory / OWNED_BINDING_NAME
    if not owned_binding_path.is_file():
        raise BridgeEvidenceError("no owned pipeline binding: evidence is incomplete")
    if binding["owned_binding_sha256"] != _sha256_bytes(
        _read_exact_bytes(owned_binding_path)
    ):
        raise BridgeEvidenceError("bridge binding does not match the owned pipeline binding")

    return VerifiedMeasurement(
        run_directory=str(directory),
        sampled_frames=tuple(int(value) for value in schedule),
        step_count=int(document["step_count"]),
        frame_shape=shape,
        frames=frames,
        measurement_spec=measurement_spec,
        measurement_spec_sha256=measurement_spec_sha256,
        law_spec_sha256=document["law_spec_sha256"],
        initial_state_sha256=document["initial_state_sha256"],
        intervention_sha256=document["intervention_sha256"],
        source_bindings=dict(document["source_bindings"]),
        unavailable_channels=dict(document["unavailable_channels"]),
        owned_root_sha256=document["owned_root_sha256"],
        measurement_root_sha256=document["measurement_root_sha256"],
    )


def run_measurement_bridge(
    run_directory: str | os.PathLike[str],
    *,
    law_spec: LatticeBondSpec,
    initial_state: LatticeBondState,
    sampled_frames: Sequence[int],
    measurement_spec: MeasurementSpec = MeasurementSpec(),
    intervention: FaceIntervention | None = None,
    backend: str = "vectorized",
    acquisition_source_identity: Mapping[str, str],
) -> MeasurementRecord:
    """The single supported measurement entry point.  It performs every stage itself.

    There is deliberately no ``frames``, ``masks``, ``tracking``, ``lifecycle``,
    ``manifest``, ``digest``, ``root`` or ``receipt`` parameter: those artefacts
    are produced here, never accepted.  The acquisition source handed to the owned
    pipeline is a private closure built below; it returns the mask re-read from
    disk, never the in-memory one.

    See MB-L1: ``sampled_frames`` are engine step labels, not physical time.
    """

    directory = Path(run_directory)
    if not directory.is_dir():
        raise BridgeEvidenceError("run_directory must already exist")
    schedule = _validated_schedule(sampled_frames, int(initial_state.step))
    try:
        (directory / MEASUREMENT_FRAME_DIRECTORY).mkdir()
    except OSError as exc:
        raise BridgeEvidenceError(
            f"could not create the measurement frame directory: {exc}"
        ) from exc

    captures, step_count = _execute(
        law_spec,
        initial_state,
        schedule,
        intervention,
        backend,
        measurement_spec.detector_spec(),
    )
    shape = (int(captures[0].matter.shape[0]), int(captures[0].matter.shape[1]))
    _persist_captures(directory, captures, float(measurement_spec.matter_threshold))
    frames = _reread_frames(directory, measurement_spec, schedule, shape)

    def _mask_source(position: int, label: int) -> np.ndarray:
        """Private closure: the mask is re-read from disk on every invocation."""

        payload = _read_exact_bytes(
            directory / _channel_relative_path(position, "mask")
        )
        return _decode_mask(payload, shape)

    try:
        owned_record = run_owned_future_pipeline(
            directory,
            acquisition_source=_mask_source,
            sampled_frames=[int(value) for value in schedule],
            detector_spec=measurement_spec.detector_spec(),
            tracker_spec=measurement_spec.tracker_spec(),
            acquisition_source_identity=acquisition_source_identity,
        )
    except OwnedPipelineError as exc:
        raise BridgeEvidenceError(f"owned pipeline refused the measured run: {exc}") from exc

    document: dict[str, Any] = {
        "bridge_version": BRIDGE_VERSION,
        "canonicalization": dict(_CANONICALIZATION),
        "channel_encoding": dict(_CHANNEL_ENCODING),
        "frame_directory_relative_path": MEASUREMENT_FRAME_DIRECTORY,
        "frame_shape": [shape[0], shape[1]],
        "frames": [item.as_dict() for item in frames],
        "initial_state_sha256": _sha256_bytes(initial_state.canonical_bytes()),
        "intervention_sha256": (
            None if intervention is None else _sha256_bytes(intervention.canonical_bytes())
        ),
        "law_spec_sha256": _sha256_bytes(_canonical_bytes(asdict(law_spec))),
        "measurement_spec": measurement_spec.as_dict(),
        "measurement_spec_sha256": _sha256_bytes(
            _canonical_bytes(measurement_spec.as_dict())
        ),
        "owned_root_sha256": _owned_root_sha256(owned_record),
        "provenance_disclosure": _PROVENANCE_DISCLOSURE,
        "sampled_frames": [int(value) for value in schedule],
        "schema_version": SCHEMA_VERSION,
        "source_bindings": _source_bindings(),
        "step_count": int(step_count),
        "unavailable_channels": dict(_UNAVAILABLE_CHANNELS),
    }
    document["measurement_root_sha256"] = _root_from_document(document)
    document_bytes = _canonical_bytes(document)
    _atomic_create(directory / MEASUREMENT_DOCUMENT_NAME, document_bytes)
    _atomic_create(
        directory / BRIDGE_BINDING_NAME,
        _canonical_bytes(
            {
                "bridge_version": BRIDGE_VERSION,
                "canonicalization": dict(_CANONICALIZATION),
                "measurement_document_relative_path": MEASUREMENT_DOCUMENT_NAME,
                "measurement_document_sha256": _sha256_bytes(document_bytes),
                "measurement_root_sha256": document["measurement_root_sha256"],
                "owned_binding_relative_path": OWNED_BINDING_NAME,
                "owned_binding_sha256": _sha256_bytes(
                    _read_exact_bytes(directory / OWNED_BINDING_NAME)
                ),
                "owned_root_sha256": document["owned_root_sha256"],
                "schema_version": SCHEMA_VERSION,
            }
        ),
    )

    verified = _verified_evidence(directory)
    return MeasurementRecord(
        run_directory=verified.run_directory,
        sampled_frames=verified.sampled_frames,
        step_count=verified.step_count,
        frame_shape=verified.frame_shape,
        frames=verified.frames,
        measurement_spec_sha256=verified.measurement_spec_sha256,
        law_spec_sha256=verified.law_spec_sha256,
        initial_state_sha256=verified.initial_state_sha256,
        intervention_sha256=verified.intervention_sha256,
        source_bindings=verified.source_bindings,
        unavailable_channels=verified.unavailable_channels,
        owned_record=owned_record,
        owned_root_sha256=verified.owned_root_sha256,
        measurement_root_sha256=verified.measurement_root_sha256,
    )


def write_anchor_receipt(
    run_directory: str | os.PathLike[str], receipt: AnchorReceipt
) -> None:
    """Publish one anchor receipt atomically.  This step verifies NOTHING.

    Writing a receipt is the publication act.  Whether the receipt binds this
    directory's root, and whether its venue means anything, is decided only by
    :func:`open_measured_analysis_access` and the verifier supplied there.
    """

    _atomic_create(
        Path(run_directory) / ANCHOR_RECEIPT_NAME, _canonical_bytes(receipt.as_dict())
    )


def _read_anchor_receipt(directory: Path) -> AnchorReceipt:
    document, _raw = _read_canonical_object(
        directory / ANCHOR_RECEIPT_NAME, _RECEIPT_KEYS, "anchor receipt", BridgeAnchorError
    )
    if document["schema_version"] != SCHEMA_VERSION:
        raise BridgeAnchorError("unsupported anchor receipt schema version")
    return AnchorReceipt(
        root_sha256=document["root_sha256"],
        venue=document["venue"],
        reference=document["reference"],
        published_at_label=document["published_at_label"],
    )


@dataclass(frozen=True)
class MeasuredAnalysisAccess:
    """Returned only after every local check AND the external anchor gate passed."""

    owned_access: AnalysisAccess
    verified_record: VerifiedMeasurement
    anchor_receipt: AnchorReceipt


def open_measured_analysis_access(
    run_directory: str | os.PathLike[str], *, verifier: AnchorVerifier
) -> MeasuredAnalysisAccess:
    """The single supported measured analysis entry point.  Fail-closed, in order.

    1. Re-read and re-verify every local artefact, including the mask
       cross-binding and the recomputed measurement root.
    2. Require ``ANCHOR_RECEIPT.json``.
    3. Require the receipt to bind the recomputed measurement root.
    4. Require ``verifier(receipt)`` to return ``True``.

    Only then is :func:`open_owned_analysis_access` called.  Any failure above
    raises before that call is reached, so a directory whose bytes changed after
    the receipt was written recomputes a different root and is refused.
    """

    directory = Path(run_directory)
    verified = _verified_evidence(directory)
    receipt = _read_anchor_receipt(directory)
    if receipt.root_sha256 != verified.measurement_root_sha256:
        raise BridgeAnchorError(
            "anchor receipt does not bind the recomputed measurement root"
        )
    if not verifier(receipt):
        raise BridgeAnchorError("anchor verifier refused the receipt")
    try:
        owned_access = open_owned_analysis_access(directory)
    except OwnedPipelineError as exc:
        raise BridgeEvidenceError(
            f"owned analysis access refused the measured evidence: {exc}"
        ) from exc
    return MeasuredAnalysisAccess(
        owned_access=owned_access, verified_record=verified, anchor_receipt=receipt
    )


__all__ = [
    "ANCHOR_RECEIPT_NAME",
    "BRIDGE_BINDING_NAME",
    "BRIDGE_VERSION",
    "MEASUREMENT_DOCUMENT_NAME",
    "MEASUREMENT_FRAME_DIRECTORY",
    "SCHEMA_VERSION",
    "AnchorReceipt",
    "AnchorVerifier",
    "BridgeAnchorError",
    "BridgeChannelError",
    "BridgeError",
    "BridgeEvidenceError",
    "BridgeScheduleError",
    "BridgeSpecificationError",
    "ComponentMeasurement",
    "DeterministicAppendOnlyLog",
    "FrameMeasurement",
    "MeasuredAnalysisAccess",
    "MeasurementRecord",
    "MeasurementSpec",
    "VerifiedMeasurement",
    "open_measured_analysis_access",
    "run_measurement_bridge",
    "write_anchor_receipt",
]
