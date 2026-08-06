"""Future-family runner integration for the qualified lifecycle closure contract.

This module is an engineering skeleton.  It computes no scientific quantity, opens
no historical family and executes no engine.  Its only purpose is to make the
qualified lifecycle contract an unavoidable part of the single supported
completion path of a future family.

Supported guarantee, scoped deliberately:

    Within the committed public API of this module, and given immutable on-disk
    evidence, no code path publishes ``COMPLETE`` or returns an
    :class:`AnalysisAccess` unless the qualified lifecycle contract was executed
    from the supplied tracking inputs, canonically persisted, read back from
    disk and independently reverified against those same inputs.

This is Python.  The guarantee does *not* extend to an actor who edits this
module or ``lifecycle.py``, monkeypatches module attributes, reaches for private
names or reflection, replaces the import, or otherwise controls both the written
bytes and the verifying code.  No absolute protection is claimed.

Four further scope facts, stated here so that no reader infers more than holds:

* Completion evidence is **content-addressed, not provenance-bound**.  Copying a
  genuine ``LIFECYCLE.json`` and ``COMPLETION.json`` pair into another directory
  yields a valid access there.  This follows directly from the manifest storing
  only a relative lifecycle identity, which is what makes identical inputs
  produce byte-identical evidence.  The correct tracking input and schedule are
  still required.
* The manifest carries **no independent authority**.  Every field is a
  deterministic function of the lifecycle document bytes and module constants,
  so anyone able to produce a qualifying lifecycle document can mint the
  matching manifest.  ``COMPLETE`` therefore adds no evidentiary weight beyond
  the lifecycle document itself; its role is to make the gate unavoidable, not
  to attest to anything further.
* Ordering is enforced by straight-line control flow.  :class:`RunnerState` and
  :class:`_Progress` *assert* that ordering; they are not the mechanism, and a
  reader should not treat the state enum as the thing that gates completion.
* A run with no tracks at all publishes ``COMPLETE`` with
  ``terminal_record_count == 0`` and an explicit ``EMPTY_TRACK_SET`` closure.
  ``COMPLETE`` is a statement about lifecycle accounting, never about content.

On failure this module removes only files whose inode it has confirmed owning.
A ``.partial`` temporary may therefore survive if the descriptor could not be
opened at all; it is never mistaken for completion evidence, and this matches
the behaviour of the frozen lifecycle primitive.

A publication failure after the lifecycle document has been persisted leaves
that document in place.  This is deliberate: it blocks silent reuse of the
directory.  The document alone never unlocks analysis.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from .instrumentation import TrackingResult
from .lifecycle import (
    LifecycleContractError,
    LifecyclePublicationError,
    SCHEMA_VERSION as LIFECYCLE_SCHEMA_VERSION,
    VALIDATOR_VERSION as LIFECYCLE_VALIDATOR_VERSION,
    canonical_lifecycle_bytes,
    qualify_and_write_lifecycle_contract,
    verify_lifecycle_document,
)

SCHEMA_VERSION = "future-lifecycle-runner-integration/v1"
INTEGRATION_VERSION = "1.0.0"
LIFECYCLE_DOCUMENT_NAME = "LIFECYCLE.json"
COMPLETION_MANIFEST_NAME = "COMPLETION.json"

_COMPLETION_DISPOSITION = "COMPLETE"

_CANONICALIZATION = {
    "encoding": "utf-8",
    "json_ensure_ascii": True,
    "json_nan_allowed": False,
    "json_separators": ",:",
    "json_sort_keys": True,
}

_MANIFEST_KEYS = frozenset(
    (
        "canonicalization",
        "disposition",
        "integration_version",
        "lifecycle_document_relative_path",
        "lifecycle_document_sha256",
        "lifecycle_input_sha256",
        "lifecycle_records_sha256",
        "lifecycle_schema_version",
        "lifecycle_validator_version",
        "sampled_frames",
        "schema_version",
        "terminal_record_count",
    )
)


class RunnerState(Enum):
    """Ordered completion states.  No later state exists if an earlier one failed."""

    UNSTARTED = 0
    LIFECYCLE_PERSISTED = 1
    LIFECYCLE_VERIFIED = 2
    COMPLETE_PUBLISHED = 3


class RunnerIntegrationError(RuntimeError):
    """Base class for every integration failure.  Never converted into success."""


class LifecycleEvidenceError(RunnerIntegrationError):
    """Lifecycle qualification, persistence or verification did not hold."""


class CompletionPublicationError(RunnerIntegrationError):
    """The completion manifest could not be published without overwriting."""


class CompletionEvidenceError(RunnerIntegrationError):
    """Persisted completion evidence is absent, malformed or inconsistent."""


class _Progress:
    """Monotonic internal state.  There is deliberately no public setter."""

    __slots__ = ("_state",)

    def __init__(self) -> None:
        self._state = RunnerState.UNSTARTED

    @property
    def state(self) -> RunnerState:
        return self._state

    def advance(self, target: RunnerState) -> None:
        if target.value != self._state.value + 1:
            raise RunnerIntegrationError(
                f"illegal completion transition {self._state.name} -> {target.name}"
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


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_exact_bytes(path: Path) -> bytes:
    """Read the exact persisted bytes.  Never returns a cached in-memory object."""

    with path.open("rb") as handle:
        return handle.read()


@dataclass(frozen=True)
class CompletionRecord:
    """Inert description of a published completion.

    Holding one of these grants nothing.  It is *not* a capability: analysis
    access is re-derived from disk by :func:`open_analysis_access` every time.
    """

    run_directory: str
    manifest_relative_path: str
    lifecycle_document_relative_path: str
    lifecycle_document_sha256: str
    lifecycle_input_sha256: str
    lifecycle_records_sha256: str
    sampled_frames: tuple[int, ...]
    terminal_record_count: int
    state: RunnerState


_ISSUE_TOKEN = object()


class AnalysisAccess:
    """Capability returned only by :func:`open_analysis_access`.

    Direct construction is refused.  The object cannot be produced without a
    successful, independent, disk-based reverification of the lifecycle document
    and the completion manifest.
    """

    __slots__ = ("_evidence",)

    def __init__(self, issue_token: object, evidence: Mapping[str, Any]) -> None:
        if issue_token is not _ISSUE_TOKEN:
            raise CompletionEvidenceError(
                "AnalysisAccess cannot be constructed directly; use open_analysis_access"
            )
        self._evidence = dict(evidence)

    def verified_completion_evidence(self) -> dict[str, Any]:
        """The gated entry point: reverified completion evidence, never an outcome.

        A deep copy is returned so that a caller mutating a nested value cannot
        change what this instance reports on a later call.
        """

        return copy.deepcopy(self._evidence)


def _build_manifest(contract: object, document_sha256: str) -> dict[str, Any]:
    """Build the manifest strictly from a reverified contract and on-disk bytes."""

    return {
        "canonicalization": dict(_CANONICALIZATION),
        "disposition": _COMPLETION_DISPOSITION,
        "integration_version": INTEGRATION_VERSION,
        "lifecycle_document_relative_path": LIFECYCLE_DOCUMENT_NAME,
        "lifecycle_document_sha256": document_sha256,
        "lifecycle_input_sha256": contract.lifecycle_input_digest_sha256,
        "lifecycle_records_sha256": contract.records_digest_sha256,
        "lifecycle_schema_version": LIFECYCLE_SCHEMA_VERSION,
        "lifecycle_validator_version": LIFECYCLE_VALIDATOR_VERSION,
        "sampled_frames": list(contract.sampled_frames),
        "schema_version": SCHEMA_VERSION,
        "terminal_record_count": len(contract.terminal_records),
    }


def _publish_new_canonical_file(target: Path, payload: bytes) -> None:
    """Atomically create one non-overwriting file.

    Nothing is left behind that this invocation has *confirmed owning*.  If the
    descriptor cannot be opened at all, the ``mkstemp`` file may survive, because
    unlinking a path whose inode has not been confirmed is the more dangerous
    choice.  Such a leftover is named ``.<target>.<random>.partial`` and can
    never be mistaken for completion evidence.
    """

    parent = target.parent
    if not parent.is_dir():
        raise CompletionPublicationError("publication parent must already exist")
    if target.exists():
        raise CompletionPublicationError("refusing to overwrite an existing completion manifest")
    descriptor, partial_name = tempfile.mkstemp(
        dir=parent,
        prefix=f".{target.name}.",
        suffix=".partial",
    )
    partial = Path(partial_name)
    owned_identity: tuple[int, int] | None = None
    target_linked = False

    def identity(stat_result: os.stat_result) -> tuple[int, int]:
        return (int(stat_result.st_dev), int(stat_result.st_ino))

    def unlink_if_owned(path_value: Path) -> None:
        if owned_identity is None:
            return
        try:
            current = os.stat(path_value, follow_symlinks=False)
        except FileNotFoundError:
            return
        if identity(current) == owned_identity:
            path_value.unlink()

    try:
        with os.fdopen(descriptor, "wb") as handle:
            owned_identity = identity(os.fstat(handle.fileno()))
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            os.link(partial, target)
            target_linked = True
            with target.open("rb") as observed_handle:
                observed_identity = identity(os.fstat(observed_handle.fileno()))
                observed_payload = observed_handle.read()
            partial_identity = identity(os.stat(partial, follow_symlinks=False))
            if (
                observed_identity != owned_identity
                or partial_identity != owned_identity
                or observed_payload != payload
            ):
                raise CompletionPublicationError(
                    "published completion identity or canonical bytes changed during publication"
                )
        unlink_if_owned(partial)
    except FileExistsError as exc:
        unlink_if_owned(partial)
        raise CompletionPublicationError(
            "refusing a concurrent completion publication without overwriting it"
        ) from exc
    except BaseException:
        if target_linked:
            unlink_if_owned(target)
        unlink_if_owned(partial)
        raise


def publish_future_family_completion(
    run_directory: str | os.PathLike[str],
    tracking: TrackingResult,
    sampled_frames: Sequence[int],
) -> CompletionRecord:
    """The single supported completion path.  Lifecycle-gated by construction.

    ``COMPLETE`` is unreachable before the lifecycle contract has been qualified,
    canonically persisted, read back from disk and reverified against the exact
    inputs supplied here.
    """
    _refuse_route_e_signal(run_directory, "future_lifecycle_runner.publish_future_family_completion")

    progress = _Progress()
    directory = Path(run_directory)
    if not directory.is_dir():
        raise CompletionPublicationError("run_directory must already exist")
    lifecycle_path = directory / LIFECYCLE_DOCUMENT_NAME
    manifest_path = directory / COMPLETION_MANIFEST_NAME
    if manifest_path.exists():
        raise CompletionPublicationError("refusing to overwrite an existing completion manifest")
    if lifecycle_path.exists():
        raise LifecycleEvidenceError("refusing to overwrite an existing lifecycle document")

    # The in-memory object returned here is deliberately discarded.  Only bytes
    # that survive a round trip through the filesystem are ever trusted.
    try:
        qualify_and_write_lifecycle_contract(lifecycle_path, tracking, sampled_frames)
    except (LifecycleContractError, LifecyclePublicationError, OSError) as exc:
        # OSError covers filesystems on which the frozen writer's hard link is
        # unavailable; it must not escape the typed hierarchy.
        raise LifecycleEvidenceError(
            f"lifecycle qualification or persistence failed: {exc}"
        ) from exc
    progress.advance(RunnerState.LIFECYCLE_PERSISTED)

    persisted = _read_exact_bytes(lifecycle_path)
    try:
        verified = verify_lifecycle_document(persisted, tracking, sampled_frames)
    except LifecycleContractError as exc:
        raise LifecycleEvidenceError(
            f"persisted lifecycle document failed read-back verification: {exc}"
        ) from exc
    if canonical_lifecycle_bytes(verified) != persisted:
        raise LifecycleEvidenceError(
            "persisted lifecycle bytes are not the canonical bytes of the verified contract"
        )
    progress.advance(RunnerState.LIFECYCLE_VERIFIED)

    document_sha256 = _sha256_bytes(persisted)
    manifest = _build_manifest(verified, document_sha256)
    _publish_new_canonical_file(manifest_path, _canonical_bytes(manifest))
    progress.advance(RunnerState.COMPLETE_PUBLISHED)

    return CompletionRecord(
        run_directory=str(directory),
        manifest_relative_path=COMPLETION_MANIFEST_NAME,
        lifecycle_document_relative_path=LIFECYCLE_DOCUMENT_NAME,
        lifecycle_document_sha256=document_sha256,
        lifecycle_input_sha256=verified.lifecycle_input_digest_sha256,
        lifecycle_records_sha256=verified.records_digest_sha256,
        sampled_frames=tuple(verified.sampled_frames),
        terminal_record_count=len(verified.terminal_records),
        state=progress.state,
    )


def open_analysis_access(
    run_directory: str | os.PathLike[str],
    tracking: TrackingResult,
    sampled_frames: Sequence[int],
) -> AnalysisAccess:
    """The single supported analysis entry point.

    Independently repeats the disk verification on every call.  A lifecycle
    document alone never unlocks analysis; a completion manifest alone never
    unlocks analysis.
    """
    _refuse_route_e_signal(run_directory, "future_lifecycle_runner.open_analysis_access")

    directory = Path(run_directory)
    if not directory.is_dir():
        raise CompletionEvidenceError("run_directory must already exist")
    manifest_path = directory / COMPLETION_MANIFEST_NAME
    if not manifest_path.is_file():
        raise CompletionEvidenceError(
            "no completion manifest: analysis access remains locked"
        )
    raw = _read_exact_bytes(manifest_path)
    try:
        manifest = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CompletionEvidenceError(
            f"completion manifest is not valid JSON: {exc}"
        ) from exc
    if not isinstance(manifest, dict):
        raise CompletionEvidenceError("completion manifest must be a JSON object")
    if set(manifest) != set(_MANIFEST_KEYS):
        raise CompletionEvidenceError("completion manifest key set mismatch")
    try:
        canonical_manifest = _canonical_bytes(manifest)
    except ValueError as exc:
        # json.loads accepts NaN/Infinity; the canonical form does not.
        raise CompletionEvidenceError(
            f"completion manifest is not canonically representable: {exc}"
        ) from exc
    if canonical_manifest != raw:
        raise CompletionEvidenceError("completion manifest bytes are not canonical")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise CompletionEvidenceError("unsupported completion manifest schema version")
    if manifest["integration_version"] != INTEGRATION_VERSION:
        raise CompletionEvidenceError("unsupported integration version")
    if manifest["lifecycle_schema_version"] != LIFECYCLE_SCHEMA_VERSION:
        raise CompletionEvidenceError("unsupported lifecycle schema version")
    if manifest["lifecycle_validator_version"] != LIFECYCLE_VALIDATOR_VERSION:
        raise CompletionEvidenceError("unsupported lifecycle validator version")
    if manifest["disposition"] != _COMPLETION_DISPOSITION:
        raise CompletionEvidenceError("completion manifest does not declare COMPLETE")
    if manifest["canonicalization"] != _CANONICALIZATION:
        raise CompletionEvidenceError("completion manifest canonicalization declaration mismatch")
    if manifest["lifecycle_document_relative_path"] != LIFECYCLE_DOCUMENT_NAME:
        raise CompletionEvidenceError("unsupported lifecycle document identity")

    lifecycle_path = directory / LIFECYCLE_DOCUMENT_NAME
    if not lifecycle_path.is_file():
        raise CompletionEvidenceError(
            "completion manifest references a missing lifecycle document"
        )
    document = _read_exact_bytes(lifecycle_path)
    if _sha256_bytes(document) != manifest["lifecycle_document_sha256"]:
        raise CompletionEvidenceError(
            "lifecycle document digest does not match the completion manifest"
        )
    try:
        verified = verify_lifecycle_document(document, tracking, sampled_frames)
    except LifecycleContractError as exc:
        raise LifecycleEvidenceError(
            f"persisted lifecycle document failed independent reverification: {exc}"
        ) from exc
    if canonical_lifecycle_bytes(verified) != document:
        raise LifecycleEvidenceError(
            "persisted lifecycle bytes are not the canonical bytes of the verified contract"
        )
    expected = _build_manifest(verified, _sha256_bytes(document))
    if _canonical_bytes(expected) != raw:
        raise CompletionEvidenceError(
            "completion manifest bindings do not match the reverified lifecycle contract"
        )
    return AnalysisAccess(_ISSUE_TOKEN, expected)


__all__ = [
    "COMPLETION_MANIFEST_NAME",
    "INTEGRATION_VERSION",
    "LIFECYCLE_DOCUMENT_NAME",
    "SCHEMA_VERSION",
    "AnalysisAccess",
    "CompletionEvidenceError",
    "CompletionPublicationError",
    "CompletionRecord",
    "LifecycleEvidenceError",
    "RunnerIntegrationError",
    "RunnerState",
    "open_analysis_access",
    "publish_future_family_completion",
]


def _refuse_route_e_signal(candidate: object, entry_point: str) -> None:
    """PRB-5: the installed Route E guard.

    Installed as the FIRST statement of every accepted public entry point.  It costs
    nothing on the normal path (one isinstance check) and it makes the Route E guard
    unavoidable: an accepted entry point driven with a typed ``RouteERequest`` runs the
    frozen check order and ALWAYS refuses, before any other check, any read, any write,
    any engine call and any acquisition.  No parameter was added to any signature.
    """
    from .future_route_e_pre_run_locks import RouteERequest, enforce_route_e_guard

    if isinstance(candidate, RouteERequest):
        enforce_route_e_guard(candidate, entry_point=entry_point)
