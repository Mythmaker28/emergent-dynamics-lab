"""Owned synthetic pipeline: acquisition through analysis access, in one entry point.

The qualified runner ``future_lifecycle_runner`` verifies *declared* evidence.  It
never calls ``track_components``, so it cannot know how many samples were actually
acquired or where a run truly ended.  That was the headline limitation recorded as
L1/L2 of ``FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01``.

This module closes that gap *inside its own API*.  It owns every stage:

    schedule validation -> acquisition -> canonical copy -> per-frame persistence
    -> canonical acquisition ledger -> atomic publication -> discard in memory
    -> re-read from disk -> independent digest reverification -> ``track_components``
    -> lifecycle validation -> qualified completion publication -> re-read and
    reverification -> ``COMPLETE`` -> ``AnalysisAccess``

Supported guarantee, scoped deliberately:

    Within ``run_owned_future_pipeline``, the single supported synthetic entry point,
    every acquired frame used for
    analysis comes from an invocation performed by the runner at a declared schedule
    position, is content-bound in an acquisition ledger, persisted and re-read before
    tracking, then passed through mandatory tracking, lifecycle validation and the
    qualified completion gate before analysis access is possible.

The guarantee is about **one execution of the supported entry point**.  It is not a claim
that the persisted directory can afterwards be defended against someone who can write to
it.  Read the limitation register below before quoting anything from this module.

What is **not** claimed, stated here so that no reader infers more:

* **No physical time is authenticated.**  Calling a synthetic source with the label
  ``1_000_000`` proves that the invocation was recorded under that label.  It does not
  prove that one million physical engine steps elapsed.  The labels are declared, the
  *invocations* are owned.
* No external experimental source is proved honest.  ``acquisition_source_identity``
  is a caller-declared reproducibility binding, never an authority certificate.
* SHA-256 binds bytes, not authority.  There is no secret anywhere in this module, so
  every digest it writes can also be recomputed by anyone who can write the bytes.
* No protection is claimed against an actor who edits this module, the tracker, the
  lifecycle validator or the qualified runner, monkeypatches attributes, or uses
  reflection.
* No engine runs.  Frames are handcrafted synthetic boolean masks supplied by an
  injectable source; the pipeline materialises them into inert lattice states solely
  so that the committed detector can be applied to them.

**Limitation register.**  Each entry is pinned by a named test rather than left to prose.

* **OP-L1 — the owned artefacts attest reproduction, not acquisition.**  On re-read, what
  is verified is that the persisted frames, specifications and schedule *reproduce* the
  published lifecycle document; not that they are the objects the source actually
  returned.  Within one run the two coincide, because the pipeline writes what it was
  handed.  Afterwards they need not: see OP-L2 and OP-L3.
* **OP-L2 — an inert specification perturbation is accepted.**  A ``detector_spec`` or
  ``tracker_spec`` edit that leaves the tracker output identical, with every digest
  re-pinned, is accepted.  The recorded specification really does reproduce the evidence;
  it is simply not the only one that would.
* **OP-L3 — a track-topology-equivalent frame substitution is accepted.**  Same reasoning,
  and it is by far the widest case.  The lifecycle document binds the schedule, the
  assignments, the events and the track records; it binds no component area, mass,
  centroid, pixel set or radius of gyration.  Any frame whose per-frame component count and
  resulting track topology are unchanged can therefore replace the original once its row
  digest, its ``true_cell_count``, the entries digest and the ledger digest are re-pinned --
  and for a component that terminates rather than persists, the geometry is entirely free:
  a four-cell blob may be replaced by the whole lattice.  (For a persisting track the space
  is bounded only by the tracker's own association thresholds.)
  The lifecycle document is the only anchor outside the acquisition chain and it binds the
  *tracking*, not the pixels.  Copying a whole genuine run directory to another directory
  likewise verifies there.  Re-minting ``LIFECYCLE.json`` and ``COMPLETION.json`` with the
  accepted public runner costs one API call, not a source edit, so a wholesale consistent
  re-forgery is cheap and is not prevented.
* **OP-L4 — the recorded invocation count is a within-process witness only.**  The
  ledger's ``invocation_ordinal`` and ``invocation_count`` come from a counter advanced
  inside the wrapper that calls the source, so an *implementation* that skips or duplicates
  a call writes a non-consecutive ordinal and is refused on re-read.  That is the whole of
  the claim.  On disk the fields carry no independent information: any document this module
  accepts has ``invocation_count == sample_count == len(entries)`` and every ordinal equal
  to its index, and an actor rewriting the ledger afterwards can write whatever it likes,
  subject to OP-L3.
* **OP-L7 — the declared identity payload is free text.**  The identity block's shape is
  bound (exactly three keys, ``authority == "NONE"``, ``declared_by == "caller"``, a
  non-empty mapping of strings to strings), but the *content* of ``declared`` is not, and
  can be rewritten after the fact under the same re-pin as OP-L3.  It is a label, not a
  measurement.
* **OP-L5 — the publication primitive is leaner than the accepted runner's.**  It does not
  confirm the temporary file's inode before unlinking it, and does not re-read the linked
  target.  Every published document is re-read and reverified downstream, so a hostile swap
  at the temporary path fails closed rather than being published as evidence.
* **OP-L6 — the returned capability is the accepted runner's.**  ``AnalysisAccess`` carries
  the twelve completion-manifest fields and nothing about the acquisition ledger.  The
  owned guarantee attaches to the *call* that produced it, not to the object.

Failure is always closed: if any stage fails, ``OWNED_PIPELINE.json`` is never
published, and analysis access is refused for that directory even if a completion
manifest exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from . import instrumentation as _instrumentation
from . import lifecycle as _lifecycle
from . import future_lifecycle_runner as _runner
from .instrumentation import DetectorSpec, TrackerSpec, detect_components, track_components
from .engine import LatticeBondState
from .future_lifecycle_runner import (
    COMPLETION_MANIFEST_NAME,
    LIFECYCLE_DOCUMENT_NAME,
    AnalysisAccess,
    RunnerIntegrationError,
    open_analysis_access,
    publish_future_family_completion,
)

SCHEMA_VERSION = "future-lifecycle-owned-pipeline/v1"
PIPELINE_VERSION = "1.0.0"
ACQUISITION_LEDGER_NAME = "ACQUISITION.json"
OWNED_BINDING_NAME = "OWNED_PIPELINE.json"
ACQUISITION_FRAME_DIRECTORY = "acquisition_frames"

_CANONICALIZATION = {
    "encoding": "utf-8",
    "json_ensure_ascii": True,
    "json_nan_allowed": False,
    "json_separators": ",:",
    "json_sort_keys": True,
}

# Inert materialisation constants.  They exist only so the committed detector can be
# applied to a handcrafted boolean mask.  They are bound in the ledger.
_FRAME_MATERIALIZATION = {
    "absent_matter": 0.1,
    "present_matter": 0.8,
    "resource": 0.8,
    "momentum": 0.0,
}

_FRAME_ENCODING = {
    "dtype": "bool",
    "false_value": 0,
    "order": "C",
    "storage": "uint8",
    "true_value": 1,
}

_PROVENANCE_DISCLOSURE = (
    "sampled_frames are DECLARED schedule labels recorded by the runner at the moment it "
    "invoked the acquisition source; they are not evidence of physical elapsed time. "
    "acquisition_source_identity is caller-declared and carries no authority. "
    "These digests bind bytes, not authority: any party able to write this directory can "
    "recompute them."
)

_IDENTITY_KEYS = frozenset(("authority", "declared", "declared_by"))

_LEDGER_KEYS = frozenset(
    (
        "acquisition_source_identity",
        "canonicalization",
        "detector_spec",
        "entries",
        "entries_sha256",
        "frame_directory_relative_path",
        "frame_encoding",
        "frame_materialization",
        "invocation_count",
        "pipeline_version",
        "provenance_disclosure",
        "sample_count",
        "sampled_frames",
        "schema_version",
        "source_bindings",
        "tracker_spec",
    )
)

_ENTRY_KEYS = frozenset(
    (
        "dtype",
        "frame_relative_path",
        "frame_sha256",
        "invocation_ordinal",
        "requested_sample_label",
        "sequence_position",
        "shape",
        "true_cell_count",
    )
)

_BINDING_KEYS = frozenset(
    (
        "acquisition_ledger_relative_path",
        "acquisition_ledger_sha256",
        "canonicalization",
        "completion_manifest_relative_path",
        "completion_manifest_sha256",
        "entries_sha256",
        "lifecycle_document_relative_path",
        "lifecycle_document_sha256",
        "pipeline_version",
        "provenance_disclosure",
        "sample_count",
        "sampled_frames",
        "schema_version",
        "source_bindings",
    )
)

AcquisitionSource = Callable[[int, int], "np.ndarray"]


class OwnedPipelineState(Enum):
    """Ordered owned-pipeline states.

    Ordering is enforced by straight-line control flow.  This enum and :class:`_Progress`
    *assert* that ordering; they are not the mechanism, and a reader must not treat
    ``ANALYSIS_UNLOCKED`` as the thing that gates anything.  Nor is
    :attr:`OwnedPipelineRecord.analysis_evidence_sha256` a proof that the final gate ran --
    it is a joint identity of the acquisition ledger and the reverified completion
    evidence, and any code with those values in scope could compute it.  The only thing
    that makes the final gate load-bearing is that the call is on the success path and its
    exception propagates.
    """

    UNSTARTED = 0
    SCHEDULE_VALIDATED = 1
    ACQUIRED = 2
    ACQUISITION_PUBLISHED = 3
    ACQUISITION_REVERIFIED = 4
    TRACKED = 5
    COMPLETE_PUBLISHED = 6
    ANALYSIS_UNLOCKED = 7


class OwnedPipelineError(RuntimeError):
    """Base class for every owned-pipeline failure.  Never converted into success."""


class OwnedScheduleError(OwnedPipelineError):
    """The requested schedule is absent or malformed.  Raised before any acquisition."""


class OwnedAcquisitionError(OwnedPipelineError):
    """The acquisition source, its arguments or a returned frame violated the contract."""


class OwnedPublicationError(OwnedPipelineError):
    """Owned evidence could not be published without overwriting."""


class OwnedEvidenceError(OwnedPipelineError):
    """Persisted owned evidence is absent, malformed or inconsistent."""


class _InvocationCounter:
    """Wraps the acquisition source so the counter cannot drift from the calls.

    Reviewer A blocker 1 / Reviewer B blocker 1, second round: the first attempt advanced a
    counter once per loop iteration, which is definitionally equal to the loop index and
    therefore witnessed nothing.  The increment now happens inside ``__call__``, so a
    skipped or duplicated call is visible in the persisted ordinals.
    """

    __slots__ = ("_source", "calls", "ordinal_of_last_call")

    def __init__(self, source: AcquisitionSource) -> None:
        self._source = source
        self.calls = 0
        self.ordinal_of_last_call = -1

    def __call__(self, position: int, label: int) -> object:
        self.ordinal_of_last_call = self.calls
        self.calls += 1
        return self._source(position, label)


class _Progress:
    """Monotonic internal state.  There is deliberately no public setter."""

    __slots__ = ("_state",)

    def __init__(self) -> None:
        self._state = OwnedPipelineState.UNSTARTED

    @property
    def state(self) -> OwnedPipelineState:
        return self._state

    def advance(self, target: OwnedPipelineState) -> None:
        if target.value != self._state.value + 1:
            raise OwnedPipelineError(
                f"illegal owned-pipeline transition {self._state.name} -> {target.name}"
            )
        self._state = target


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _plain_int(value: object) -> bool:
    """A JSON integer, never a bool.  ``True == 1`` must not slip through a count check."""

    return isinstance(value, int) and not isinstance(value, bool)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_exact_bytes(path: Path) -> bytes:
    """Read the exact persisted bytes.  Never returns a cached in-memory object."""

    with path.open("rb") as handle:
        return handle.read()


def _source_bindings() -> dict[str, str]:
    """Digest the four modules whose behaviour this evidence depends on.

    These are read from disk on every call, so a later edit to any of them changes the
    binding and invalidates previously published evidence.  This is a reproducibility
    binding, not an authority certificate.
    """

    return {
        "future_lifecycle_owned_pipeline_sha256": _sha256_bytes(
            _read_exact_bytes(Path(__file__))
        ),
        "future_lifecycle_runner_sha256": _sha256_bytes(
            _read_exact_bytes(Path(_runner.__file__))
        ),
        "instrumentation_sha256": _sha256_bytes(
            _read_exact_bytes(Path(_instrumentation.__file__))
        ),
        "lifecycle_sha256": _sha256_bytes(_read_exact_bytes(Path(_lifecycle.__file__))),
    }


def _validated_schedule(sampled_frames: Sequence[int]) -> tuple[int, ...]:
    """Validate the requested schedule BEFORE any acquisition call is made."""

    if sampled_frames is None:
        raise OwnedScheduleError("sampled_frames is mandatory; explicit None is refused")
    if isinstance(sampled_frames, (str, bytes, bytearray, Mapping)) or not isinstance(
        sampled_frames, Sequence
    ):
        raise OwnedScheduleError("sampled_frames must be an ordered sequence of integers")
    values = tuple(sampled_frames)
    if not values:
        raise OwnedScheduleError("sampled_frames must not be empty")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise OwnedScheduleError("sampled_frames entries must be plain integers")
        if value < 0:
            raise OwnedScheduleError("sampled_frames entries must be non-negative")
    for earlier, later in zip(values, values[1:]):
        if later <= earlier:
            raise OwnedScheduleError("sampled_frames must be strictly increasing")
    return values


def _validated_identity(identity: Mapping[str, str]) -> dict[str, str]:
    """Canonicalise the CALLER-DECLARED acquisition-source identity document."""

    if not isinstance(identity, Mapping):
        raise OwnedAcquisitionError("acquisition_source_identity must be a mapping")
    if not identity:
        raise OwnedAcquisitionError("acquisition_source_identity must not be empty")
    declared: dict[str, str] = {}
    for key, value in identity.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise OwnedAcquisitionError(
                "acquisition_source_identity must map strings to strings"
            )
        declared[key] = value
    return {
        "authority": "NONE",
        "declared": declared,
        "declared_by": "caller",
    }


def _validated_source(acquisition_source: AcquisitionSource) -> AcquisitionSource:
    """Refuse anything that is a container of prebuilt frames rather than a source."""

    if isinstance(acquisition_source, (Sequence, Mapping, np.ndarray)):
        raise OwnedAcquisitionError(
            "acquisition_source must be a callable source, not a prebuilt frame container"
        )
    if not callable(acquisition_source):
        raise OwnedAcquisitionError("acquisition_source must be callable")
    return acquisition_source


def _canonical_frame_bytes(frame: object, expected_shape: tuple[int, int] | None) -> tuple[
    bytes, tuple[int, int]
]:
    """Reject a malformed frame; otherwise return its canonical bytes and shape.

    The array is copied here, immediately on return from the source, so that a caller
    mutating its own buffer afterwards cannot change the persisted evidence.
    """

    if not isinstance(frame, np.ndarray):
        raise OwnedAcquisitionError("acquisition source must return a numpy array")
    if frame.dtype != np.bool_:
        raise OwnedAcquisitionError("acquisition source must return a boolean mask")
    # The copy is taken here, immediately on return, and every subsequent question about
    # geometry is asked of the copy.  A subclass that lies about ``shape`` or ``ndim``
    # therefore cannot describe the bytes this function persists.
    owned = np.array(frame, dtype=np.bool_, copy=True, order="C")
    if owned.ndim != 2:
        raise OwnedAcquisitionError("acquisition source must return a 2-D mask")
    shape = (int(owned.shape[0]), int(owned.shape[1]))
    if min(shape) < 2:
        raise OwnedAcquisitionError("acquired mask must be at least 2x2")
    if expected_shape is not None and shape != expected_shape:
        raise OwnedAcquisitionError("acquired mask shape changed during the run")
    return owned.astype(np.uint8).tobytes(order="C"), shape


def _decode_frame(payload: bytes, shape: tuple[int, int]) -> np.ndarray:
    """Decode canonical frame bytes, refusing anything that is not exactly 0/1."""

    if len(payload) != shape[0] * shape[1]:
        raise OwnedEvidenceError("persisted frame byte length does not match its shape")
    values = np.frombuffer(payload, dtype=np.uint8)
    if bool(np.any(values > 1)):
        raise OwnedEvidenceError("persisted frame is not a canonical 0/1 mask")
    return values.reshape(shape).astype(bool)


def _atomic_create(target: Path, payload: bytes) -> None:
    """Atomically create one non-overwriting file.

    There is no ``exists()`` pre-check: creation is the check.  A rival publication that
    appears at any moment before the link fails closed, so there is no
    time-of-check/time-of-use window at all -- and, unlike an ``exists()`` guard,
    a dangling symlink at the target cannot be written through.

    Disclosed as OP-L5: this is leaner than the accepted runner's publication primitive.
    It does not confirm the temporary file's inode before unlinking it and does not re-read
    the linked target.  The temporary name is random and can never be mistaken for
    evidence, and every published document is re-read and independently reverified
    downstream, so a hostile swap at the temporary path fails closed instead of being
    published as evidence.
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
            # ``FileExistsError`` is the rival case and is the common one; every other
            # ``OSError`` (no hard links on this filesystem, EPERM, ...) is typed here too
            # so that nothing escapes ``OwnedPipelineError``.
            raise OwnedPublicationError(
                f"could not publish {target.name} without overwriting: {exc}"
            ) from exc
    finally:
        partial.unlink(missing_ok=True)


def _materialise(mask: np.ndarray, frame: int) -> LatticeBondState:
    """Build an inert lattice state from a synthetic mask.  No engine step is taken."""

    shape = (int(mask.shape[0]), int(mask.shape[1]))
    matter = np.where(
        mask,
        _FRAME_MATERIALIZATION["present_matter"],
        _FRAME_MATERIALIZATION["absent_matter"],
    ).astype(np.float64)
    resource = np.full(shape, _FRAME_MATERIALIZATION["resource"], dtype=np.float64)
    momentum = np.full((2, *shape), _FRAME_MATERIALIZATION["momentum"], dtype=np.float64)
    return LatticeBondState(matter, resource, momentum, frame)


def _spec_payload(detector_spec: DetectorSpec, tracker_spec: TrackerSpec) -> tuple[
    dict[str, Any], dict[str, Any]
]:
    return (
        {
            "matter_threshold": float(detector_spec.matter_threshold),
            "min_cells": int(detector_spec.min_cells),
        },
        {
            "dilation_radius": int(tracker_spec.dilation_radius),
            "max_area_ratio": float(tracker_spec.max_area_ratio),
            "max_centroid_displacement": float(tracker_spec.max_centroid_displacement),
            "unique_score_margin": float(tracker_spec.unique_score_margin),
        },
    )


@dataclass(frozen=True)
class OwnedAcquisitionEvidence:
    """Reverified acquisition evidence, rebuilt from disk and never from memory."""

    sampled_frames: tuple[int, ...]
    sample_count: int
    frame_digests: tuple[str, ...]
    frame_shape: tuple[int, int]
    entries_sha256: str
    ledger_sha256: str
    detector_spec: DetectorSpec
    tracker_spec: TrackerSpec


@dataclass(frozen=True)
class OwnedPipelineRecord:
    """Inert description of one completed owned run.  Holding it grants nothing."""

    run_directory: str
    sampled_frames: tuple[int, ...]
    sample_count: int
    invocation_count: int
    frame_shape: tuple[int, int]
    frame_digests: tuple[str, ...]
    acquisition_ledger_sha256: str
    entries_sha256: str
    lifecycle_document_sha256: str
    completion_manifest_sha256: str
    analysis_evidence_sha256: str
    terminal_record_count: int
    detected_component_count: int
    track_count: int
    state: OwnedPipelineState


def _read_canonical_object(path: Path, keys: frozenset[str], label: str) -> tuple[
    dict[str, Any], bytes
]:
    """Read one canonical JSON object with an exact key set, or fail closed."""

    if not path.is_file():
        raise OwnedEvidenceError(f"no {label}: analysis access remains locked")
    raw = _read_exact_bytes(path)
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OwnedEvidenceError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise OwnedEvidenceError(f"{label} must be a JSON object")
    if set(value) != set(keys):
        raise OwnedEvidenceError(f"{label} key set mismatch")
    try:
        canonical = _canonical_bytes(value)
    except ValueError as exc:
        raise OwnedEvidenceError(f"{label} is not canonically representable: {exc}") from exc
    if canonical != raw:
        raise OwnedEvidenceError(f"{label} bytes are not canonical")
    return value, raw


def _reverify_acquisition(directory: Path) -> OwnedAcquisitionEvidence:
    """Re-read the ledger and every frame from disk and recompute every digest."""

    ledger, raw = _read_canonical_object(
        directory / ACQUISITION_LEDGER_NAME, _LEDGER_KEYS, "acquisition ledger"
    )
    if ledger["schema_version"] != SCHEMA_VERSION:
        raise OwnedEvidenceError("unsupported acquisition ledger schema version")
    if ledger["pipeline_version"] != PIPELINE_VERSION:
        raise OwnedEvidenceError("unsupported owned pipeline version")
    if ledger["canonicalization"] != _CANONICALIZATION:
        raise OwnedEvidenceError("acquisition ledger canonicalization declaration mismatch")
    if ledger["frame_encoding"] != _FRAME_ENCODING:
        raise OwnedEvidenceError("acquisition ledger frame encoding mismatch")
    if ledger["frame_materialization"] != _FRAME_MATERIALIZATION:
        raise OwnedEvidenceError("acquisition ledger frame materialization mismatch")
    if ledger["frame_directory_relative_path"] != ACQUISITION_FRAME_DIRECTORY:
        raise OwnedEvidenceError("acquisition ledger frame directory mismatch")
    if ledger["source_bindings"] != _source_bindings():
        raise OwnedEvidenceError(
            "acquisition ledger source bindings do not match the executing sources"
        )
    if ledger["provenance_disclosure"] != _PROVENANCE_DISCLOSURE:
        raise OwnedEvidenceError("acquisition ledger provenance disclosure mismatch")
    identity = ledger["acquisition_source_identity"]
    if not isinstance(identity, dict) or set(identity) != set(_IDENTITY_KEYS):
        raise OwnedEvidenceError("acquisition source identity key set mismatch")
    if identity["authority"] != "NONE" or identity["declared_by"] != "caller":
        raise OwnedEvidenceError("acquisition source identity must remain a caller declaration")
    declared = identity["declared"]
    if not isinstance(declared, dict) or not declared:
        raise OwnedEvidenceError("acquisition source identity declaration is malformed")
    for key, value in declared.items():
        if not isinstance(value, str):
            raise OwnedEvidenceError("acquisition source identity must declare only strings")

    schedule = _reverified_schedule(ledger["sampled_frames"])
    if not _plain_int(ledger["sample_count"]) or ledger["sample_count"] != len(schedule):
        raise OwnedEvidenceError("acquisition ledger sample count disagrees with the schedule")
    if not _plain_int(ledger["invocation_count"]) or ledger["invocation_count"] != len(schedule):
        raise OwnedEvidenceError(
            "recorded acquisition invocations disagree with the declared schedule"
        )
    entries = ledger["entries"]
    if not isinstance(entries, list) or len(entries) != len(schedule):
        raise OwnedEvidenceError("acquisition ledger row count disagrees with the schedule")
    if _sha256_bytes(_canonical_bytes(entries)) != ledger["entries_sha256"]:
        raise OwnedEvidenceError("acquisition ledger entries digest mismatch")

    detector_spec, tracker_spec = _reverified_specs(ledger)
    frame_directory = directory / ACQUISITION_FRAME_DIRECTORY
    digests: list[str] = []
    shape: tuple[int, int] | None = None
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != set(_ENTRY_KEYS):
            raise OwnedEvidenceError("acquisition ledger row key set mismatch")
        if not _plain_int(entry["sequence_position"]) or entry["sequence_position"] != position:
            raise OwnedEvidenceError("acquisition ledger rows are out of sequence")
        if not _plain_int(entry["invocation_ordinal"]) or entry["invocation_ordinal"] != position:
            raise OwnedEvidenceError("acquisition invocation ordinals are not consecutive")
        if (
            not _plain_int(entry["requested_sample_label"])
            or entry["requested_sample_label"] != schedule[position]
        ):
            raise OwnedEvidenceError("acquisition ledger row does not match the schedule")
        if entry["dtype"] != "bool":
            raise OwnedEvidenceError("acquisition ledger row declares a non-boolean frame")
        row_shape = entry["shape"]
        if (
            not isinstance(row_shape, list)
            or len(row_shape) != 2
            or not all(isinstance(v, int) and not isinstance(v, bool) for v in row_shape)
        ):
            raise OwnedEvidenceError("acquisition ledger row shape is malformed")
        row_shape = (row_shape[0], row_shape[1])
        if min(row_shape) < 2:
            raise OwnedEvidenceError("acquisition ledger row shape is malformed")
        if shape is not None and row_shape != shape:
            raise OwnedEvidenceError("acquisition ledger rows disagree about the frame shape")
        shape = row_shape
        if entry["frame_relative_path"] != _frame_relative_path(position):
            raise OwnedEvidenceError("acquisition ledger row frame path mismatch")
        frame_path = directory / entry["frame_relative_path"]
        if frame_path.is_symlink() or not frame_path.is_file():
            raise OwnedEvidenceError("acquisition ledger references a missing frame")
        payload = _read_exact_bytes(frame_path)
        digest = _sha256_bytes(payload)
        if digest != entry["frame_sha256"]:
            raise OwnedEvidenceError("persisted frame digest does not match the ledger")
        mask = _decode_frame(payload, row_shape)
        if not _plain_int(entry["true_cell_count"]):
            raise OwnedEvidenceError("persisted frame cell count does not match the ledger")
        if int(np.count_nonzero(mask)) != entry["true_cell_count"]:
            raise OwnedEvidenceError("persisted frame cell count does not match the ledger")
        digests.append(digest)
    _refuse_extra_frames(frame_directory, len(entries))
    _refuse_unusable_specifications(detector_spec, tracker_spec, shape)
    return OwnedAcquisitionEvidence(
        sampled_frames=schedule,
        sample_count=len(schedule),
        frame_digests=tuple(digests),
        frame_shape=shape,
        entries_sha256=ledger["entries_sha256"],
        ledger_sha256=_sha256_bytes(raw),
        detector_spec=detector_spec,
        tracker_spec=tracker_spec,
    )


def _reverified_schedule(value: object) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise OwnedEvidenceError("persisted schedule must be a non-empty list")
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            raise OwnedEvidenceError("persisted schedule entries must be non-negative integers")
    for earlier, later in zip(value, value[1:]):
        if later <= earlier:
            raise OwnedEvidenceError("persisted schedule must be strictly increasing")
    return tuple(value)


def _reverified_specs(ledger: Mapping[str, Any]) -> tuple[DetectorSpec, TrackerSpec]:
    detector = ledger["detector_spec"]
    tracker = ledger["tracker_spec"]
    if not isinstance(detector, dict) or set(detector) != {"matter_threshold", "min_cells"}:
        raise OwnedEvidenceError("persisted detector specification key set mismatch")
    if not isinstance(tracker, dict) or set(tracker) != {
        "dilation_radius",
        "max_area_ratio",
        "max_centroid_displacement",
        "unique_score_margin",
    }:
        raise OwnedEvidenceError("persisted tracker specification key set mismatch")
    if not _plain_int(detector["min_cells"]) or not _plain_int(tracker["dilation_radius"]):
        raise OwnedEvidenceError("persisted specifications must use plain integers")
    for value in (
        detector["matter_threshold"],
        tracker["max_centroid_displacement"],
        tracker["max_area_ratio"],
        tracker["unique_score_margin"],
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise OwnedEvidenceError("persisted specifications must use plain numbers")
    try:
        detector_spec = DetectorSpec(
            matter_threshold=float(detector["matter_threshold"]),
            min_cells=int(detector["min_cells"]),
        )
        tracker_spec = TrackerSpec(
            max_centroid_displacement=float(tracker["max_centroid_displacement"]),
            max_area_ratio=float(tracker["max_area_ratio"]),
            dilation_radius=int(tracker["dilation_radius"]),
            unique_score_margin=float(tracker["unique_score_margin"]),
        )
    except (TypeError, ValueError) as exc:
        raise OwnedEvidenceError(f"persisted specifications are malformed: {exc}") from exc
    return detector_spec, tracker_spec


def _refuse_unusable_specifications(
    detector_spec: DetectorSpec, tracker_spec: TrackerSpec, shape: tuple[int, int]
) -> None:
    """Refuse a persisted specification that cannot be applied to the persisted frames.

    Reviewer A, material 2: without an upper bound a persisted ``dilation_radius`` of 10**9
    made the supported analysis entry point run effectively forever instead of failing
    closed.  A radius beyond the lattice is geometrically inert, so the bound is free.

    Only the two cases the committed specification types themselves admit are checked here.
    Every other out-of-range value (``min_cells`` below one, a non-positive threshold, a
    negative displacement, area ratio or score margin) is already refused by ``DetectorSpec``
    and ``TrackerSpec`` at construction, and surfaces through the malformed-specification
    path above.  Duplicating those checks would only create branches no input can reach.
    """

    if not 0.0 < detector_spec.matter_threshold <= 1.0:
        raise OwnedEvidenceError("persisted detector specification is out of range")
    if tracker_spec.dilation_radius > max(shape):
        raise OwnedEvidenceError("persisted tracker specification is out of range")


def _frame_relative_path(position: int) -> str:
    return f"{ACQUISITION_FRAME_DIRECTORY}/frame_{position:06d}.bin"


def _refuse_extra_frames(frame_directory: Path, expected: int) -> None:
    """Refuse an additional frame file smuggled into the acquisition directory."""

    observed = []
    for entry in os.scandir(frame_directory):
        if not entry.is_file(follow_symlinks=False):
            raise OwnedEvidenceError(
                "acquisition frame directory contains a non-regular entry"
            )
        observed.append(entry.name)
    if sorted(observed) != [f"frame_{position:06d}.bin" for position in range(expected)]:
        raise OwnedEvidenceError("acquisition frame directory contains unexpected entries")


def _retrack(evidence: OwnedAcquisitionEvidence, directory: Path):
    """Call the mandatory tracker ourselves, on frames re-read from disk."""

    observed = []
    detected = 0
    for position, label in enumerate(evidence.sampled_frames):
        payload = _read_exact_bytes(directory / _frame_relative_path(position))
        mask = _decode_frame(payload, evidence.frame_shape)
        components = detect_components(
            _materialise(mask, int(label)), evidence.detector_spec, frame=int(label)
        )
        detected += len(components)
        observed.append(components)
    tracking = track_components(
        tuple(observed), evidence.tracker_spec, sampled_frames=evidence.sampled_frames
    )
    return tracking, detected


def run_owned_future_pipeline(
    run_directory: str | os.PathLike[str],
    *,
    acquisition_source: AcquisitionSource,
    sampled_frames: Sequence[int],
    detector_spec: DetectorSpec,
    tracker_spec: TrackerSpec,
    acquisition_source_identity: Mapping[str, str],
) -> OwnedPipelineRecord:
    """The single supported owned entry point.  It performs every stage itself.

    There is deliberately no ``frames``, ``tracking``, ``lifecycle``, ``disposition``,
    ``manifest``, ``ledger`` or ``access`` parameter: those artefacts are produced
    here, never accepted.

    ``sampled_frames`` are DECLARED labels.  Calling a synthetic source with the label
    ``1_000_000`` proves that the invocation was recorded under that label; it does not
    prove that one million physical engine steps elapsed.  See OP-L1 to OP-L6 in the module
    docstring before quoting any guarantee from this function.
    """

    progress = _Progress()
    directory = Path(run_directory)
    if not directory.is_dir():
        raise OwnedPublicationError("run_directory must already exist")
    if not isinstance(detector_spec, DetectorSpec):
        raise OwnedAcquisitionError("detector_spec must be a DetectorSpec")
    if not isinstance(tracker_spec, TrackerSpec):
        raise OwnedAcquisitionError("tracker_spec must be a TrackerSpec")
    source = _validated_source(acquisition_source)
    identity = _validated_identity(acquisition_source_identity)
    schedule = _validated_schedule(sampled_frames)
    progress.advance(OwnedPipelineState.SCHEDULE_VALIDATED)

    frame_directory = directory / ACQUISITION_FRAME_DIRECTORY
    try:
        frame_directory.mkdir()
    except FileExistsError as exc:
        raise OwnedPublicationError(
            "refusing to reuse an existing acquisition frame directory"
        ) from exc

    entries: list[dict[str, Any]] = []
    counter = _InvocationCounter(source)
    shape: tuple[int, int] | None = None
    for position, label in enumerate(schedule):
        try:
            acquired = counter(position, int(label))
        except Exception as exc:  # noqa: BLE001 - every source failure is fatal here
            raise OwnedAcquisitionError(
                f"acquisition source failed at sequence position {position}: {exc!r}"
            ) from exc
        # The ordinal is the counter's value AT THE CALL, and the counter is advanced
        # inside the wrapper, not by this loop.  An implementation that skips or duplicates
        # a call therefore records a non-consecutive ordinal and is refused on re-read.
        ordinal = counter.ordinal_of_last_call
        payload, shape = _canonical_frame_bytes(acquired, shape)
        relative = _frame_relative_path(position)
        _atomic_create(directory / relative, payload)
        entries.append(
            {
                "dtype": "bool",
                "frame_relative_path": relative,
                "frame_sha256": _sha256_bytes(payload),
                "invocation_ordinal": ordinal,
                "requested_sample_label": int(label),
                "sequence_position": position,
                "shape": [shape[0], shape[1]],
                "true_cell_count": int(np.count_nonzero(np.frombuffer(payload, dtype=np.uint8))),
            }
        )
    progress.advance(OwnedPipelineState.ACQUIRED)

    bindings = _source_bindings()
    detector_payload, tracker_payload = _spec_payload(detector_spec, tracker_spec)
    ledger = {
        "acquisition_source_identity": identity,
        "canonicalization": dict(_CANONICALIZATION),
        "detector_spec": detector_payload,
        "entries": entries,
        "entries_sha256": _sha256_bytes(_canonical_bytes(entries)),
        "frame_directory_relative_path": ACQUISITION_FRAME_DIRECTORY,
        "frame_encoding": dict(_FRAME_ENCODING),
        "frame_materialization": dict(_FRAME_MATERIALIZATION),
        "invocation_count": counter.calls,
        "pipeline_version": PIPELINE_VERSION,
        "provenance_disclosure": _PROVENANCE_DISCLOSURE,
        "sample_count": len(schedule),
        "sampled_frames": [int(value) for value in schedule],
        "schema_version": SCHEMA_VERSION,
        "source_bindings": bindings,
        "tracker_spec": tracker_payload,
    }
    _atomic_create(directory / ACQUISITION_LEDGER_NAME, _canonical_bytes(ledger))
    progress.advance(OwnedPipelineState.ACQUISITION_PUBLISHED)

    # Everything built above is now discarded.  Only bytes that survive a round trip
    # through the filesystem are trusted from here on.
    del entries, ledger, payload, shape, acquired, ordinal
    evidence = _reverify_acquisition(directory)
    progress.advance(OwnedPipelineState.ACQUISITION_REVERIFIED)

    tracking, detected = _retrack(evidence, directory)
    progress.advance(OwnedPipelineState.TRACKED)

    try:
        completion = publish_future_family_completion(
            directory, tracking, evidence.sampled_frames
        )
    except RunnerIntegrationError as exc:
        raise OwnedEvidenceError(f"qualified completion refused the owned run: {exc}") from exc
    progress.advance(OwnedPipelineState.COMPLETE_PUBLISHED)

    binding = {
        "acquisition_ledger_relative_path": ACQUISITION_LEDGER_NAME,
        "acquisition_ledger_sha256": evidence.ledger_sha256,
        "canonicalization": dict(_CANONICALIZATION),
        "completion_manifest_relative_path": COMPLETION_MANIFEST_NAME,
        "completion_manifest_sha256": _sha256_bytes(
            _read_exact_bytes(directory / COMPLETION_MANIFEST_NAME)
        ),
        "entries_sha256": evidence.entries_sha256,
        "lifecycle_document_relative_path": LIFECYCLE_DOCUMENT_NAME,
        "lifecycle_document_sha256": completion.lifecycle_document_sha256,
        "pipeline_version": PIPELINE_VERSION,
        "provenance_disclosure": _PROVENANCE_DISCLOSURE,
        "sample_count": evidence.sample_count,
        "sampled_frames": [int(value) for value in evidence.sampled_frames],
        "schema_version": SCHEMA_VERSION,
        "source_bindings": bindings,
    }
    _atomic_create(directory / OWNED_BINDING_NAME, _canonical_bytes(binding))

    # Final gate: the access is opened through the same public, disk-only path a later
    # caller would use.  If it raises, this function raises and no record is returned.
    #
    # Honest scope, after Reviewer B blocker 2: ``canonical(verified_completion_evidence())``
    # is provably the completion manifest's own bytes, so a digest of it alone would be a
    # restatement of ``completion_manifest_sha256`` and would witness nothing.  The digest
    # below additionally binds the acquisition ledger, so it is a joint identity of the
    # owned and the qualified evidence -- but it is still only a value, not a capability.
    # What actually makes the gate load-bearing is that this call is on the success path
    # and propagates; that is pinned by test_op_01b, not by this field.
    analysis_evidence_sha256 = _sha256_bytes(
        _canonical_bytes(
            {
                "acquisition_ledger_sha256": evidence.ledger_sha256,
                "entries_sha256": evidence.entries_sha256,
                "reverified_completion_evidence": (
                    open_owned_analysis_access(directory).verified_completion_evidence()
                ),
            }
        )
    )
    progress.advance(OwnedPipelineState.ANALYSIS_UNLOCKED)

    return OwnedPipelineRecord(
        run_directory=str(directory),
        sampled_frames=evidence.sampled_frames,
        sample_count=evidence.sample_count,
        invocation_count=counter.calls,
        frame_shape=evidence.frame_shape,
        frame_digests=evidence.frame_digests,
        acquisition_ledger_sha256=evidence.ledger_sha256,
        entries_sha256=evidence.entries_sha256,
        lifecycle_document_sha256=completion.lifecycle_document_sha256,
        completion_manifest_sha256=binding["completion_manifest_sha256"],
        analysis_evidence_sha256=analysis_evidence_sha256,
        terminal_record_count=completion.terminal_record_count,
        detected_component_count=detected,
        track_count=len(tracking.tracks),
        state=progress.state,
    )


def open_owned_analysis_access(
    run_directory: str | os.PathLike[str],
) -> AnalysisAccess:
    """The single supported owned analysis entry point.

    It accepts a directory and nothing else.  Every schedule, specification and frame
    is re-read from disk, every digest is recomputed, the tracker is re-run on the
    re-read frames, and the qualified runner then independently reverifies the
    lifecycle document and completion manifest.  A caller cannot re-supply any input
    that would be compared against the persisted evidence.

    What this verifies is REPRODUCTION, not acquisition: that the persisted frames,
    specifications and schedule reproduce the published lifecycle document.  It is not
    evidence that they are the objects the source returned, nor that any physical time
    elapsed.  See OP-L1 to OP-L6 in the module docstring.
    """

    directory = Path(run_directory)
    if not directory.is_dir():
        raise OwnedEvidenceError("run_directory must already exist")
    binding, _ = _read_canonical_object(
        directory / OWNED_BINDING_NAME, _BINDING_KEYS, "owned pipeline binding"
    )
    if binding["schema_version"] != SCHEMA_VERSION:
        raise OwnedEvidenceError("unsupported owned pipeline binding schema version")
    if binding["pipeline_version"] != PIPELINE_VERSION:
        raise OwnedEvidenceError("unsupported owned pipeline version")
    if binding["canonicalization"] != _CANONICALIZATION:
        raise OwnedEvidenceError("owned pipeline binding canonicalization declaration mismatch")
    if binding["acquisition_ledger_relative_path"] != ACQUISITION_LEDGER_NAME:
        raise OwnedEvidenceError("owned pipeline binding acquisition ledger identity mismatch")
    if binding["completion_manifest_relative_path"] != COMPLETION_MANIFEST_NAME:
        raise OwnedEvidenceError("owned pipeline binding completion manifest identity mismatch")
    if binding["lifecycle_document_relative_path"] != LIFECYCLE_DOCUMENT_NAME:
        raise OwnedEvidenceError("owned pipeline binding lifecycle document identity mismatch")
    if binding["provenance_disclosure"] != _PROVENANCE_DISCLOSURE:
        raise OwnedEvidenceError("owned pipeline binding provenance disclosure mismatch")
    if binding["source_bindings"] != _source_bindings():
        raise OwnedEvidenceError(
            "owned pipeline binding source bindings do not match the executing sources"
        )

    evidence = _reverify_acquisition(directory)
    if binding["acquisition_ledger_sha256"] != evidence.ledger_sha256:
        raise OwnedEvidenceError("owned pipeline binding does not match the acquisition ledger")
    if binding["entries_sha256"] != evidence.entries_sha256:
        raise OwnedEvidenceError("owned pipeline binding does not match the ledger entries")
    if not _plain_int(binding["sample_count"]) or binding["sample_count"] != evidence.sample_count:
        raise OwnedEvidenceError("owned pipeline binding disagrees about the sample count")
    if tuple(binding["sampled_frames"]) != evidence.sampled_frames:
        raise OwnedEvidenceError("owned pipeline binding disagrees about the schedule")

    manifest_path = directory / COMPLETION_MANIFEST_NAME
    if not manifest_path.is_file():
        raise OwnedEvidenceError("no completion manifest: analysis access remains locked")
    if _sha256_bytes(_read_exact_bytes(manifest_path)) != binding["completion_manifest_sha256"]:
        raise OwnedEvidenceError("completion manifest digest does not match the owned binding")
    lifecycle_path = directory / LIFECYCLE_DOCUMENT_NAME
    if not lifecycle_path.is_file():
        raise OwnedEvidenceError("no lifecycle document: analysis access remains locked")
    if _sha256_bytes(_read_exact_bytes(lifecycle_path)) != binding["lifecycle_document_sha256"]:
        raise OwnedEvidenceError("lifecycle document digest does not match the owned binding")

    tracking, _detected = _retrack(evidence, directory)
    try:
        return open_analysis_access(directory, tracking, evidence.sampled_frames)
    except RunnerIntegrationError as exc:
        raise OwnedEvidenceError(
            f"qualified analysis access refused the owned evidence: {exc}"
        ) from exc


__all__ = [
    "ACQUISITION_FRAME_DIRECTORY",
    "ACQUISITION_LEDGER_NAME",
    "OWNED_BINDING_NAME",
    "PIPELINE_VERSION",
    "SCHEMA_VERSION",
    "OwnedAcquisitionError",
    "OwnedAcquisitionEvidence",
    "OwnedEvidenceError",
    "OwnedPipelineError",
    "OwnedPipelineRecord",
    "OwnedPipelineState",
    "OwnedPublicationError",
    "OwnedScheduleError",
    "open_owned_analysis_access",
    "run_owned_future_pipeline",
]
