"""Route E executable locks for the six frozen PRE_RUN_BLOCKERs PRB-1 .. PRB-6.

This module is the answer to the MISSION's own mandate, quoted literally from the
accepted human review ``00afcdd1aacbdf32bb030d85ced735a2920421f6`` section 8:

    ``FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`` **pourra** fermer les six
    ``PRE_RUN_BLOCKER``.

The six obligations, quoted literally from ``…_01S_DECISION.json.pre_run_blockers``:

    PRB-1  persist the track-component join
           -> write (frame, canonical cell-set digest, track_id) into root-bound evidence
    PRB-2  mandatory receipt
           -> the supported scientific entry point refuses without a verified receipt
    PRB-3  frozen check order
           -> pin by test: local evidence -> root digest -> verifier
    PRB-4  replay binding
           -> bind run identity and family enrolment into the root
    PRB-5  single supported entry point
           -> close or declare out of protocol, with a refusal test:
              open_owned_analysis_access, future_lifecycle_runner.open_analysis_access,
              publish_future_family_completion, qualify_and_write_lifecycle_contract
              (and, per B15, run_owned_future_pipeline)
    PRB-6  external anchoring of the final root
           -> public immutable or append-only commitment, verifiable without a secret

WHAT THIS MODULE IS NOT
-----------------------
It runs nothing.  ``SCIENTIFIC_RUN_AUTHORIZED`` is ``False`` in the frame module and
every gate here is fail-closed and terminates in a refusal.  No scientific seed, no
beacon round, no family, no namespace, no law, no initial condition, no world and no
result is created, read or written.  There is no network access of any kind.

The obligations A-F closed by commit ``c6d4acf0`` are PREREGISTRATION obligations, not
this mission's mandate; they are kept, corrected, and are NOT renamed onto PRB-1..6.

WHAT IS AND IS NOT CLOSED -- read ``blocker_status()`` for the field-by-field facts.
``PRB-5`` and ``PRB-6`` are OPEN.  This module must never be summarised as "the
pre-run blockers are closed".

LOCK LIMITATION REGISTER
------------------------
LK-L1  The accepted sources (engine, instrumentation, lifecycle, runner, owned
       pipeline, measurement bridge) are immutable under the frozen allowlist.  Every
       lock here therefore sits in the ROUTE E path, in front of them.  A caller who
       bypasses the Route E path and calls an accepted function directly is refused by
       that function's own first check -- a strictly WEAKER property, separately
       tested and separately bounded (see LK-L4 and PRB-5 below).
LK-L2  ``verify_public_commitment`` requires a verifier supplied by the caller.  No
       verifier is bundled: closing PRB-6 and HR-4 with a real BLS check needs a
       maintained cryptographic dependency, and adding one would modify
       ``pyproject.toml``, which is outside the frozen allowlist.  The gate is
       implemented and fail-closed; the CRYPTOGRAPHIC VERIFIER ITSELF REMAINS AN OPEN
       SUB-OBLIGATION, reported rather than faked.  While it is open, the authenticity
       layer of PRB-2 is open too.
LK-L3  The Route E root binds the measurement root, the track-component join and the
       family enrolment.  It does not replace the bridge's own measurement root, which
       is computed inside an immutable accepted source.
LK-L4  ``route_e_entry`` is a PROTOCOL FACADE, not a gate.  It does not import the five
       accepted entry points, does not hold them as callables, is not in their call
       graph, and cannot intercept a direct call.  No test of the facade is evidence
       about those five functions.  See ``FACADE_IS_NOT_A_GATE``.
LK-L5  Nothing in this module is called by any accepted source.  The persisted join
       evidence of PRB-1 exists only when a Route E caller writes it; there is no
       accepted producer today, and creating one means editing an accepted source.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .instrumentation import TrackingResult

__all__ = [
    "LOCKS_VERSION",
    "PRE_RUN_BLOCKERS",
    # PRB-1
    "EVIDENCE_SCHEMA",
    "JOIN_EVIDENCE_FILENAME",
    "EvidenceInvalid",
    "JoinIncomplete",
    "JoinRecord",
    "canonical_cell_set_digest",
    "build_track_component_join",
    "canonical_join_bytes",
    "join_digest",
    "write_join_evidence",
    "read_join_evidence",
    # PRB-4
    "FamilyEnrolment",
    "enrolment_digest",
    "route_e_root",
    # PRB-6
    "PublicCommitment",
    "CommitmentInvalid",
    "verify_public_commitment",
    "RouteERequest",
    "RouteEGuardRefused",
    "enforce_route_e_guard",
    "ROUTE_E_GUARDED_ENTRY_POINTS",
    "GUARD_IS_NOT_INSTALLED",
    # PRB-2
    "RouteEReceipt",
    "ReceiptMissing",
    "ReceiptInvalid",
    # PRB-3
    "CHECK_ORDER",
    "CHECK_PHASES",
    "CheckOrderViolation",
    "RouteEAnalysisRefused",
    "open_route_e_analysis",
    # PRB-5
    "SUPPORTED_ENTRY_POINTS",
    "FACADE_IS_NOT_A_GATE",
    "EntryPointRefused",
    "route_e_entry",
    # status
    "blocker_status",
]

LOCKS_VERSION = "route-e-pre-run-locks/v1"

PRE_RUN_BLOCKERS: tuple[Mapping[str, str], ...] = (
    {
        "id": "PRB-1",
        "obligation": "persist the track-component join",
        "closure": (
            "write (frame, canonical cell-set digest, track_id) into root-bound evidence"
        ),
    },
    {
        "id": "PRB-2",
        "obligation": "mandatory receipt",
        "closure": (
            "the supported scientific entry point refuses without a verified receipt"
        ),
    },
    {
        "id": "PRB-3",
        "obligation": "frozen check order",
        "closure": "pin by test: local evidence -> root digest -> verifier",
    },
    {
        "id": "PRB-4",
        "obligation": "replay binding",
        "closure": "bind run identity and family enrolment into the root",
    },
    {
        "id": "PRB-5",
        "obligation": "single supported entry point",
        "closure": (
            "close or declare out of protocol, with a refusal test: "
            "open_owned_analysis_access, future_lifecycle_runner.open_analysis_access, "
            "publish_future_family_completion, qualify_and_write_lifecycle_contract "
            "(and, per B15, run_owned_future_pipeline)"
        ),
    },
    {
        "id": "PRB-6",
        "obligation": "external anchoring of the final root",
        "closure": (
            "public immutable or append-only commitment, verifiable without a secret"
        ),
    },
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256_hex(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


# ======================================================================================
# PRB-1  persist the track-component join
#
# The obligation is literally "WRITE (frame, canonical cell-set digest, track_id) INTO
# root-bound evidence".  Digest algebra alone does not discharge it: the triples must be
# serialised canonically, written atomically inside a bounded evidence root, read back
# from disk, and the Route E root recomputed FROM THE RE-READ BYTES -- never from an
# object still held in memory.
# ======================================================================================


class EvidenceInvalid(RuntimeError):
    """The persisted join evidence is absent, malformed, mutated or out of its root."""


class JoinIncomplete(ValueError):
    """The join does not cover the detected support exactly.  Never a silent drop."""


EVIDENCE_SCHEMA = "route-e-join-evidence/v1"
JOIN_EVIDENCE_FILENAME = "route_e_track_component_join.json"


@dataclass(frozen=True)
class JoinRecord:
    """One (frame, canonical cell-set digest, track_id) triple.  Exactly PRB-1's text."""

    frame: int
    cell_set_sha256: str
    track_id: int

    def __post_init__(self) -> None:
        if isinstance(self.frame, bool) or not isinstance(self.frame, int) or self.frame < 0:
            raise ValueError("frame must be a non-negative plain int")
        if (
            isinstance(self.track_id, bool)
            or not isinstance(self.track_id, int)
            or self.track_id < 0
        ):
            raise ValueError("track_id must be a non-negative plain int")
        if not _is_sha256_hex(self.cell_set_sha256):
            raise ValueError("cell_set_sha256 must be 64 lowercase hex characters")

    def as_tuple(self) -> tuple[int, str, int]:
        return (self.frame, self.cell_set_sha256, self.track_id)


def canonical_cell_set_digest(shape: tuple[int, int], cells: Sequence[int]) -> str:
    """Canonical digest of a component's cell set.

    The cells are sorted and deduplicated, the lattice shape is bound, and the payload
    is canonical JSON with sorted keys and ASCII separators.  Two components with the
    same support on the same lattice therefore always produce the same digest, and a
    different lattice shape always produces a different one.
    """
    if (
        not isinstance(shape, tuple)
        or len(shape) != 2
        or any(isinstance(v, bool) or not isinstance(v, int) or v < 2 for v in shape)
    ):
        raise ValueError("shape must be a tuple of two ints, each at least 2")
    if isinstance(cells, (str, bytes)) or not isinstance(cells, Sequence):
        raise TypeError("cells must be a sequence of ints")
    total = shape[0] * shape[1]
    values = []
    for cell in cells:
        if isinstance(cell, bool) or not isinstance(cell, int):
            raise TypeError("every cell index must be a plain int")
        if not 0 <= cell < total:
            raise ValueError("cell index outside the lattice")
        values.append(cell)
    if not values:
        raise ValueError("an empty cell set has no canonical digest")
    payload = {"cells": sorted(set(values)), "shape": [shape[0], shape[1]]}
    return _sha256_hex(_canonical_bytes(payload))


def build_track_component_join(
    tracking: TrackingResult,
    components_by_frame: Mapping[int, Mapping[int, tuple[tuple[int, int], Sequence[int]]]],
) -> tuple[JoinRecord, ...]:
    """The join, with EXACT support coverage.  Fail-closed on every mismatch.

    ``components_by_frame[frame][component_index] = (shape, cells)``.

    Four refusals, all before any byte is written:

    * an assignment with no component support        -> orphan assignment, refused;
    * a detected component with no assignment        -> incomplete join, refused;
    * a duplicated ``(frame, component_index)`` key   -> refused;
    * two identical resulting triples                 -> refused.

    The declared policy on duplicates is therefore REFUSAL, not absorption: a duplicate
    is a defect of the caller's support map, never something the digest should hide.
    """
    if not isinstance(tracking, TrackingResult):
        raise TypeError("tracking must be a TrackingResult")
    if not isinstance(components_by_frame, Mapping):
        raise TypeError("components_by_frame must be a mapping frame -> index -> support")

    support_keys: set[tuple[int, int]] = set()
    for frame, per_frame in components_by_frame.items():
        if isinstance(frame, bool) or not isinstance(frame, int) or frame < 0:
            raise ValueError("every support frame must be a non-negative plain int")
        if not isinstance(per_frame, Mapping):
            raise TypeError("every support frame must map component index -> support")
        for index in per_frame:
            if isinstance(index, bool) or not isinstance(index, int) or index < 0:
                raise ValueError("every component index must be a non-negative plain int")
            support_keys.add((int(frame), int(index)))

    seen: set[tuple[int, int]] = set()
    records: list[JoinRecord] = []
    for frame, component_index, track_id in tracking.assignments:
        key = (int(frame), int(component_index))
        if key in seen:
            raise JoinIncomplete(
                f"duplicated assignment for (frame={frame}, index={component_index})"
            )
        seen.add(key)
        try:
            shape, cells = components_by_frame[frame][component_index]
        except (KeyError, TypeError, ValueError) as exc:
            raise JoinIncomplete(
                f"orphan assignment: no component support for (frame={frame}, "
                f"index={component_index})"
            ) from exc
        records.append(
            JoinRecord(
                frame=int(frame),
                cell_set_sha256=canonical_cell_set_digest(tuple(shape), cells),
                track_id=int(track_id),
            )
        )

    unassigned = sorted(support_keys - seen)
    if unassigned:
        raise JoinIncomplete(
            f"incomplete join: {len(unassigned)} detected component(s) carry no "
            f"assignment, first is (frame={unassigned[0][0]}, index={unassigned[0][1]}); "
            "an unassigned component is refused, never silently omitted"
        )

    triples = [record.as_tuple() for record in records]
    if len(set(triples)) != len(triples):
        raise JoinIncomplete(
            "two assignments produce an identical (frame, cell-set digest, track_id) "
            "triple; duplicates are refused, never absorbed by the digest"
        )
    return tuple(sorted(records, key=JoinRecord.as_tuple))


def canonical_join_bytes(records: Sequence[JoinRecord]) -> bytes:
    """The exact bytes that are written, and the exact bytes that are digested."""
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise TypeError("records must be a sequence of JoinRecord")
    if not records:
        raise ValueError("an empty join is refused: PRB-1 requires the join to exist")
    rows = []
    for record in records:
        if not isinstance(record, JoinRecord):
            raise TypeError("every record must be a JoinRecord")
        rows.append([record.frame, record.cell_set_sha256, record.track_id])
    if len({tuple(row) for row in rows}) != len(rows):
        raise ValueError("duplicate join rows are refused")
    payload = {"join": sorted(rows), "schema": EVIDENCE_SCHEMA}
    return _canonical_bytes(payload)


def join_digest(records: Sequence[JoinRecord]) -> str:
    """Order-independent digest of a complete join = sha256 of the persisted bytes."""
    return _sha256_hex(canonical_join_bytes(records))


def _records_from_payload(payload: object) -> tuple[JoinRecord, ...]:
    if not isinstance(payload, dict) or set(payload) != {"join", "schema"}:
        raise EvidenceInvalid("refused: the join evidence key set is not the canonical one")
    if payload["schema"] != EVIDENCE_SCHEMA:
        raise EvidenceInvalid("refused: unsupported join evidence schema")
    rows = payload["join"]
    if not isinstance(rows, list) or not rows:
        raise EvidenceInvalid("refused: the join evidence carries no row")
    records = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 3:
            raise EvidenceInvalid("refused: a join row is not a triple")
        frame, digest, track_id = row
        try:
            records.append(
                JoinRecord(frame=frame, cell_set_sha256=digest, track_id=track_id)
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceInvalid(f"refused: malformed join row: {exc}") from exc
    return tuple(records)


def write_join_evidence(
    evidence_root: str | os.PathLike[str],
    records: Sequence[JoinRecord],
) -> tuple[Path, str]:
    """Write the join into a BOUNDED evidence root, atomically, without overwriting.

    Returns ``(path, digest)`` where ``digest`` is the sha256 of the bytes that are now
    on disk -- verified by reading them back before returning.  Refusals: root absent,
    root not a real directory, root is a symlink, target already exists, target escapes
    the root, no atomic link available, or read-back mismatch.  Nothing is ever
    overwritten and nothing is written outside the declared root.
    """
    payload = canonical_join_bytes(records)
    root = Path(evidence_root)
    if root.is_symlink():
        raise EvidenceInvalid("refused: the evidence root is a symlink")
    if not root.is_dir():
        raise EvidenceInvalid("refused: the evidence root must already exist")
    real_root = os.path.realpath(root)
    target = root / JOIN_EVIDENCE_FILENAME
    if os.path.dirname(os.path.realpath(target)) != real_root:
        raise EvidenceInvalid("refused: the evidence path escapes its declared root")
    if target.exists() or target.is_symlink():
        raise EvidenceInvalid("refused: refusing to overwrite existing join evidence")

    descriptor, partial_name = tempfile.mkstemp(dir=root, prefix=".join.", suffix=".partial")
    partial = Path(partial_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(partial, target)
        except OSError as exc:  # pragma: no cover - platform without hard links
            raise EvidenceInvalid(
                f"refused: no atomic non-overwriting link available: {exc}"
            ) from exc
    finally:
        try:
            os.unlink(partial)
        except OSError:  # pragma: no cover - create-only mounts
            pass

    _, digest = read_join_evidence(target)
    if digest != _sha256_hex(payload):
        raise EvidenceInvalid("refused: the persisted bytes do not reproduce the join digest")
    return target, digest


def read_join_evidence(path: str | os.PathLike[str]) -> tuple[tuple[JoinRecord, ...], str]:
    """Re-read the artefact and recompute its digest FROM THE BYTES ON DISK.

    The digest returned here is ``sha256`` of exactly what was read.  A mutated,
    re-ordered or non-canonical file is refused rather than re-canonicalised, so a
    tampered artefact can never reproduce the original digest.
    """
    target = Path(path)
    if target.is_symlink():
        raise EvidenceInvalid("refused: the join evidence is a symlink")
    if not target.is_file():
        raise EvidenceInvalid("refused: the join evidence does not exist")
    raw = target.read_bytes()
    digest = _sha256_hex(raw)
    try:
        payload = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise EvidenceInvalid(f"refused: the join evidence is not canonical JSON: {exc}") from exc
    records = _records_from_payload(payload)
    if _canonical_bytes(payload) != raw:
        raise EvidenceInvalid("refused: the join evidence is not in canonical byte form")
    if canonical_join_bytes(records) != raw:
        raise EvidenceInvalid("refused: the join evidence does not round-trip byte-for-byte")
    return records, digest


# ======================================================================================
# PRB-4  replay binding -- run identity and family enrolment inside the root
# ======================================================================================


@dataclass(frozen=True)
class FamilyEnrolment:
    """The enrolment a Route E root must bind.  Nothing here creates a family."""

    run_identity: str
    seed_root_sha256: str
    draw_plan_digest: str
    n_draws: int
    worlds: int

    def __post_init__(self) -> None:
        if not isinstance(self.run_identity, str) or not 8 <= len(self.run_identity) <= 128:
            raise ValueError("run_identity must be a string of 8 to 128 characters")
        for name in ("seed_root_sha256", "draw_plan_digest"):
            if not _is_sha256_hex(getattr(self, name)):
                raise ValueError(f"{name} must be 64 lowercase hex characters")
        for name in ("n_draws", "worlds"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive plain int")


def enrolment_digest(enrolment: FamilyEnrolment) -> str:
    if not isinstance(enrolment, FamilyEnrolment):
        raise TypeError("enrolment must be a FamilyEnrolment")
    payload = {
        "draw_plan_digest": enrolment.draw_plan_digest,
        "n_draws": enrolment.n_draws,
        "run_identity": enrolment.run_identity,
        "schema": LOCKS_VERSION,
        "seed_root_sha256": enrolment.seed_root_sha256,
        "worlds": enrolment.worlds,
    }
    return _sha256_hex(_canonical_bytes(payload))


def route_e_root(
    *,
    measurement_root_sha256: str,
    track_component_join_digest: str,
    family_enrolment_digest: str,
) -> str:
    """The final Route E root.  Binds PRB-1 and PRB-4 into one publishable digest.

    It does NOT replace the bridge's measurement root: it binds it.  Changing any of
    the three inputs by one bit changes the root, so a bit-identical directory replayed
    under a different run identity does not reproduce the anchored root (PRB-4).
    """
    for name, value in (
        ("measurement_root_sha256", measurement_root_sha256),
        ("track_component_join_digest", track_component_join_digest),
        ("family_enrolment_digest", family_enrolment_digest),
    ):
        if not _is_sha256_hex(value):
            raise ValueError(f"{name} must be 64 lowercase hex characters")
    payload = {
        "family_enrolment_digest": family_enrolment_digest,
        "measurement_root_sha256": measurement_root_sha256,
        "schema": LOCKS_VERSION,
        "track_component_join_digest": track_component_join_digest,
    }
    return _sha256_hex(_canonical_bytes(payload))


# ======================================================================================
# PRB-6  external anchoring of the final root
# ======================================================================================


class CommitmentInvalid(RuntimeError):
    """The public commitment is absent, malformed, unverified or not prior."""


@dataclass(frozen=True)
class PublicCommitment:
    """A claim that ``root_sha256`` was published immutably at ``published_at_unix``.

    Holding one grants nothing.  It is checked by ``verify_public_commitment`` against
    a caller-supplied verifier; the venue and reference are exactly as strong as that
    verifier.  ``published_at_unix`` is the PUBLIC timestamp, which is what makes the
    commitment prior to a later beacon round -- a local commit hash cannot do this.
    """

    root_sha256: str
    venue: str
    reference: str
    published_at_unix: int

    def __post_init__(self) -> None:
        if not _is_sha256_hex(self.root_sha256):
            raise ValueError("root_sha256 must be 64 lowercase hex characters")
        for name in ("venue", "reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if (
            isinstance(self.published_at_unix, bool)
            or not isinstance(self.published_at_unix, int)
            or self.published_at_unix <= 0
        ):
            raise ValueError("published_at_unix must be a positive plain int")


def verify_public_commitment(
    commitment: PublicCommitment | None,
    *,
    expected_root_sha256: str,
    must_precede_unix: int,
    beacon_response: Mapping[str, Any] | None,
    verifier_path: str | os.PathLike[str] | None,
) -> bytes:
    """Fail-closed verification of PRB-6.  Returns the verified randomness, or raises.

    In this order, and no other:
      1. a commitment must be present and well formed;
      2. it must bind exactly the expected root;
      3. the public-priority cutoff must be present -- there is NO default, because a
         commitment that is not prior to the reveal cannot bind it (HR-3);
      4. the PUBLIC timestamp must be strictly earlier than that cutoff;
      5. the designated round is DERIVED from that public timestamp; it is never an
         argument and never negotiable;
      6. the round is verified cryptographically by the pinned maintained verifier.

    There is no boolean callback anywhere in this signature.  A caller cannot assert
    that a commitment is anchored, cannot choose the chain, the scheme, the DST or the
    public key, and cannot choose the round.
    """
    if commitment is None:
        raise CommitmentInvalid("refused: no public commitment was presented")
    if not isinstance(commitment, PublicCommitment):
        raise CommitmentInvalid("refused: commitment is not a PublicCommitment")
    if not _is_sha256_hex(expected_root_sha256):
        raise CommitmentInvalid("refused: expected root is not a sha256 digest")
    if commitment.root_sha256 != expected_root_sha256:
        raise CommitmentInvalid("refused: the commitment does not bind the expected root")
    if must_precede_unix is None:
        raise CommitmentInvalid(
            "refused: no public-priority cutoff supplied; the anti-reroll precondition "
            "has no default and cannot be skipped (HR-3)"
        )
    if isinstance(must_precede_unix, bool) or not isinstance(must_precede_unix, int):
        raise CommitmentInvalid("refused: must_precede_unix must be a plain int")
    if must_precede_unix <= 0:
        raise CommitmentInvalid("refused: must_precede_unix must be positive")
    if commitment.published_at_unix >= must_precede_unix:
        raise CommitmentInvalid(
            "refused: the public commitment is not strictly prior to the designated "
            "instant; a commitment published at or after the reveal cannot bind it"
        )

    from . import future_route_e_pre_run_frame as _frame

    designated = _frame.designated_round(commitment.published_at_unix)
    return _frame.consume_beacon_round(
        response=beacon_response,
        expected_round=designated,
        helper_path=verifier_path,
    )


# ======================================================================================
# PRB-2  mandatory receipt
# ======================================================================================


class ReceiptMissing(RuntimeError):
    """No receipt was presented to the supported scientific entry point."""


class ReceiptInvalid(RuntimeError):
    """A receipt was presented but does not bind the recomputed root."""


@dataclass(frozen=True)
class RouteEReceipt:
    """A receipt is a claim that ``root_sha256`` was anchored by ``commitment``.

    A receipt is a CLAIM, never a proof.  Its root is never believed: the gate
    recomputes the root from persisted evidence and compares.  Its authenticity is
    exactly the strength of the PRB-6 verifier, which is not delivered.
    """

    root_sha256: str
    commitment: PublicCommitment

    def __post_init__(self) -> None:
        if not _is_sha256_hex(self.root_sha256):
            raise ValueError("root_sha256 must be 64 lowercase hex characters")
        if not isinstance(self.commitment, PublicCommitment):
            raise ValueError("commitment must be a PublicCommitment")
        if self.commitment.root_sha256 != self.root_sha256:
            raise ValueError("the receipt and its commitment must bind the same root")


# ======================================================================================
# PRB-3  frozen check order:  local evidence -> root digest -> verifier
#
# ONE internal path, used by EVERY public entry.  A public function that skipped a
# phase would have to re-implement this function, which is what the mutation tests
# detect.
# ======================================================================================

CHECK_ORDER: tuple[str, ...] = ("LOCAL_EVIDENCE", "ROOT_DIGEST", "VERIFIER")

#: The realisation of the frozen order.  ``ENTRY_GUARD`` is a preflight that trusts
#: NOTHING (it only checks that a receipt of the right shape is present, before any
#: effect), and ``RECEIPT_ROOT_BINDING`` is a sub-step inside ``VERIFIER``.  The three
#: frozen phases are neither reordered nor removed.
CHECK_PHASES: tuple[str, ...] = (
    "ENTRY_GUARD",
    "LOCAL_EVIDENCE",
    "ROOT_DIGEST",
    "RECEIPT_ROOT_BINDING",
    "VERIFIER",
)


class CheckOrderViolation(RuntimeError):
    """The frozen check order was not respected."""


class RouteEAnalysisRefused(RuntimeError):
    """The Route E analysis gate refused.  It always does in this mission."""


class _OrderTrace:
    """Records which frozen checks actually ran, in the order they ran."""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def enter(self, step: str) -> None:
        expected = CHECK_ORDER[len(self.steps)] if len(self.steps) < len(CHECK_ORDER) else None
        if step != expected:
            raise CheckOrderViolation(
                f"frozen check order violated: expected {expected!r}, got {step!r}"
            )
        self.steps.append(step)


def _frozen_check_order(
    *,
    evidence_path: str | os.PathLike[str],
    measurement_root_sha256: str,
    family_enrolment: FamilyEnrolment,
    receipt: RouteEReceipt | None,
    must_precede_unix: int,
    beacon_response: Mapping[str, Any] | None,
    verifier_path: str | os.PathLike[str] | None,
    trace: list[str] | None,
) -> str:
    """THE single ordered path.  Returns the recomputed root, or raises.

    ``ENTRY_GUARD``  a receipt must be present and of the right type.  Its root is NOT
                     read here and NOT believed anywhere.
    ``LOCAL_EVIDENCE`` the persisted join is re-read from disk and its digest recomputed
                     from those bytes.
    ``ROOT_DIGEST``  the Route E root is RECOMPUTED from the re-read join digest, the
                     measurement root and the enrolment digest.  No caller-supplied
                     root string exists anywhere in this signature.
    ``RECEIPT_ROOT_BINDING`` the receipt must bind exactly that recomputed root.
    ``VERIFIER``     the public commitment must verify, and be strictly prior.
    """

    def mark(step: str) -> None:
        if trace is not None:
            trace.append(step)

    # -- phase 0: ENTRY_GUARD, before any effect, believing nothing -------------------
    mark("ENTRY_GUARD")
    if receipt is None:
        raise ReceiptMissing("refused at ENTRY_GUARD: no receipt was presented")
    if not isinstance(receipt, RouteEReceipt):
        raise ReceiptInvalid("refused at ENTRY_GUARD: receipt is not a RouteEReceipt")
    if must_precede_unix is None:
        raise CommitmentInvalid(
            "refused at ENTRY_GUARD: no public-priority cutoff supplied; there is no "
            "default and the check cannot be skipped (HR-3)"
        )

    order = _OrderTrace()

    # -- phase 1: LOCAL_EVIDENCE ------------------------------------------------------
    order.enter("LOCAL_EVIDENCE")
    mark("LOCAL_EVIDENCE")
    _, recomputed_join_digest = read_join_evidence(evidence_path)

    # -- phase 2: ROOT_DIGEST ---------------------------------------------------------
    order.enter("ROOT_DIGEST")
    mark("ROOT_DIGEST")
    if not isinstance(family_enrolment, FamilyEnrolment):
        raise ReceiptInvalid("refused at ROOT_DIGEST: enrolment is not a FamilyEnrolment")
    recomputed_root = route_e_root(
        measurement_root_sha256=measurement_root_sha256,
        track_component_join_digest=recomputed_join_digest,
        family_enrolment_digest=enrolment_digest(family_enrolment),
    )

    # -- phase 3: RECEIPT_ROOT_BINDING then VERIFIER ----------------------------------
    order.enter("VERIFIER")
    mark("RECEIPT_ROOT_BINDING")
    if receipt.root_sha256 != recomputed_root:
        raise ReceiptInvalid(
            "refused at RECEIPT_ROOT_BINDING: the receipt does not bind the root "
            "recomputed from the persisted evidence"
        )
    mark("VERIFIER")
    verify_public_commitment(
        receipt.commitment,
        expected_root_sha256=recomputed_root,
        must_precede_unix=must_precede_unix,
        beacon_response=beacon_response,
        verifier_path=verifier_path,
    )
    return recomputed_root


def open_route_e_analysis(
    *,
    evidence_path: str | os.PathLike[str],
    measurement_root_sha256: str,
    family_enrolment: FamilyEnrolment,
    receipt: RouteEReceipt | None,
    must_precede_unix: int,
    beacon_response: Mapping[str, Any] | None = None,
    verifier_path: str | os.PathLike[str] | None = None,
    trace: list[str] | None = None,
) -> None:
    """The Route E analysis entry point.  Fail-closed, in the frozen order.

    Even when every phase passes, this function refuses: ``scientific_run_authorized``
    is ``False`` for this mission and no preregistration or execution authorisation
    exists.  There is no argument that makes it return.
    """
    _frozen_check_order(
        evidence_path=evidence_path,
        measurement_root_sha256=measurement_root_sha256,
        family_enrolment=family_enrolment,
        receipt=receipt,
        must_precede_unix=must_precede_unix,
        beacon_response=beacon_response,
        verifier_path=verifier_path,
        trace=trace,
    )
    raise RouteEAnalysisRefused(
        "refused after VERIFIER: scientific_run_authorized is False; no preregistration "
        "exists and no human review has authorised execution"
    )


# ======================================================================================
# PRB-5  single supported entry point
#
# WHAT THIS IS, STATED WITHOUT EMBELLISHMENT
# ------------------------------------------
# ``route_e_entry`` is a PROTOCOL FACADE, not a gate.  It is NOT in the call graph of
# the five accepted functions: it does not import them, does not reference them as
# callables, and cannot prevent a direct call to any of them.  Its own tests therefore
# prove a property of the facade and NOTHING about those five functions.
#
# Closing PRB-5 requires a refusal that lives INSIDE each accepted entry point, which
# means editing an accepted source.  That is outside the frozen allowlist, so PRB-5 is
# reported OPEN and the exact paths required are named in the report.
# ======================================================================================

SUPPORTED_ENTRY_POINTS: tuple[str, ...] = (
    "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
    "future_lifecycle_owned_pipeline.open_owned_analysis_access",
    "future_lifecycle_runner.open_analysis_access",
    "future_lifecycle_runner.publish_future_family_completion",
    "lifecycle.qualify_and_write_lifecycle_contract",
)

FACADE_IS_NOT_A_GATE: str = (
    "route_e_entry is a protocol facade.  It is not in the call graph of the five "
    "accepted entry points, it cannot intercept a direct call to any of them, and no "
    "test of this facade is evidence about them.  The weaker property that an accepted "
    "function called directly in an unauthorised Route E context refuses at its own "
    "first check is tested separately and is bounded by LK-L1."
)


class EntryPointRefused(RuntimeError):
    """The Route E protocol facade refused."""


def route_e_entry(
    entry_point: str,
    *,
    authorisation: Any = None,
    evidence_path: str | os.PathLike[str] | None = None,
    measurement_root_sha256: str | None = None,
    family_enrolment: FamilyEnrolment | None = None,
    receipt: RouteEReceipt | None = None,
    must_precede_unix: int | None = None,
    beacon_response: Mapping[str, Any] | None = None,
    verifier_path: str | os.PathLike[str] | None = None,
) -> None:
    """The in-protocol Route E facade.  It always refuses, in the frozen order.

    It delegates to ``_frozen_check_order`` -- the SAME internal path used by
    ``open_route_e_analysis`` -- so the frozen order and the mandatory public-priority
    cutoff hold identically on both public entries.  It dispatches to nothing.
    """
    from . import future_route_e_pre_run_frame as _frame

    if not isinstance(entry_point, str):
        raise EntryPointRefused("refused: entry_point must be a string")
    if entry_point not in SUPPORTED_ENTRY_POINTS:
        raise EntryPointRefused(
            f"refused: {entry_point!r} is not one of the five supported entry points"
        )
    if authorisation is None:
        raise EntryPointRefused(
            f"refused: {entry_point} requires a Route E authorisation and none was given"
        )
    if not isinstance(authorisation, _frame.RouteEAuthorisation) or not authorisation.is_valid():
        raise EntryPointRefused(
            f"refused: {entry_point} received an invalid Route E authorisation"
        )
    _frozen_check_order(
        evidence_path=evidence_path,
        measurement_root_sha256=measurement_root_sha256,
        family_enrolment=family_enrolment,
        receipt=receipt,
        must_precede_unix=must_precede_unix,
        beacon_response=beacon_response,
        verifier_path=verifier_path,
        trace=None,
    )
    if not _frame.SCIENTIFIC_RUN_AUTHORIZED:
        raise EntryPointRefused(
            f"refused: {entry_point} is unreachable while scientific_run_authorized is "
            "False; PRB-1..PRB-6 closure, a preregistration and a human review all "
            "precede any execution"
        )
    raise EntryPointRefused(  # pragma: no cover - unreachable by construction
        "refused: unreachable"
    )


# ======================================================================================
# PRB-5 / PRB-2  THE ROUTE E GUARD, installed inside the five accepted entry points
#
# ``RouteERequest`` is a TYPED signal, never a free string.  When an accepted entry
# point receives one, it runs ``enforce_route_e_guard`` as its FIRST statement -- before
# its own directory check, before any argument validation, before any effect.  When it
# receives ``None`` (the default), the accepted function behaves exactly as before and
# nothing in this module runs.
# ======================================================================================

ROUTE_E_GUARDED_ENTRY_POINTS: tuple[str, ...] = SUPPORTED_ENTRY_POINTS

#: THE GUARD IS PREPARED BUT NOT INSTALLED.  Installing it means adding one call as the
#: first statement of each of the five accepted public functions, which changes the
#: bytes of three accepted sources.  Those bytes are pinned, test by test, in
#: ``tests/test_future_lifecycle_runner_integration.py`` and
#: ``tests/test_future_lifecycle_owned_pipeline.py`` -- two files that are NOT in this
#: mission's allowlist.  Installing without extending the allowlist to those two files
#: turns nine previously green tests red, so it is not done here.  See the report.
GUARD_IS_NOT_INSTALLED: str = (
    "enforce_route_e_guard is implemented and tested, but it is NOT called by any "
    "accepted entry point.  The one-line hook is blocked by byte-level source pins in "
    "tests/test_future_lifecycle_runner_integration.py and "
    "tests/test_future_lifecycle_owned_pipeline.py, which are outside the allowlist."
)


class RouteEGuardRefused(RuntimeError):
    """The Route E guard refused inside an accepted entry point.  It always does."""


@dataclass(frozen=True)
class RouteERequest:
    """The typed Route E signal.  Constructing one grants nothing.

    It carries everything the frozen order needs and NOTHING the caller may decide:
    there is no root, no round, no scheme, no DST, no chain and no verdict callback in
    this object.  The root is recomputed from the persisted evidence, the round is
    derived from the public timestamp, and the chain parameters are pinned in
    ``route_e_beacon_verifier``.
    """

    evidence_path: str | os.PathLike[str]
    measurement_root_sha256: str
    family_enrolment: FamilyEnrolment
    receipt: RouteEReceipt
    must_precede_unix: int
    beacon_response: Mapping[str, Any] | None = None
    verifier_path: str | os.PathLike[str] | None = None


def enforce_route_e_guard(request: Any, *, entry_point: str) -> None:
    """Run the frozen order for an accepted entry point.  ALWAYS raises.

    It is deliberately impossible for this function to return: even a request that
    passes every phase ends at ``scientific_run_authorized is False``.  A caller
    therefore cannot use the Route E path to reach any accepted behaviour.
    """
    if not isinstance(entry_point, str) or entry_point not in ROUTE_E_GUARDED_ENTRY_POINTS:
        raise RouteEGuardRefused(
            f"refused: {entry_point!r} is not one of the five guarded entry points"
        )
    if not isinstance(request, RouteERequest):
        raise RouteEGuardRefused(
            f"refused: {entry_point} received a Route E signal that is not a "
            "RouteERequest; a free string or an untyped object is never a signal"
        )

    from . import future_route_e_pre_run_frame as _frame

    _frozen_check_order(
        evidence_path=request.evidence_path,
        measurement_root_sha256=request.measurement_root_sha256,
        family_enrolment=request.family_enrolment,
        receipt=request.receipt,
        must_precede_unix=request.must_precede_unix,
        beacon_response=request.beacon_response,
        verifier_path=request.verifier_path,
        trace=None,
    )
    if not _frame.SCIENTIFIC_RUN_AUTHORIZED:
        raise RouteEGuardRefused(
            f"refused: {entry_point} is unreachable while scientific_run_authorized is "
            "False; PRB-1..PRB-6 closure, a preregistration and a human review all "
            "precede any execution"
        )
    raise RouteEGuardRefused(  # pragma: no cover - unreachable by construction
        "refused: unreachable"
    )


# ======================================================================================
# Factual per-blocker status.  No composite token, no boolean "closed" verdict.
# ======================================================================================


def blocker_status() -> Mapping[str, Mapping[str, Any]]:
    """Separate facts, not a verdict.  Human review is still required for all six."""
    return {
        "PRB-1": {
            "mechanism_present": True,
            "persistence_present": True,
            "discriminating_tests_present": True,
            "integration_into_accepted_sources": False,
            "remaining_sub_obligations": (
                "no accepted producer calls build_track_component_join or "
                "write_join_evidence; the evidence exists only when a Route E caller "
                "writes it (LK-L1)",
            ),
            "human_review_required": True,
        },
        "PRB-2": {
            "mechanism_present": True,
            "root_recomputed_from_reread_bytes": True,
            "discriminating_tests_present": True,
            "integration_into_accepted_sources": False,
            "authenticity_established": True,
            "authenticity_mechanism": "the commitment is bound to the recomputed root and "
            "the designated round is verified by the pinned maintained drand verifier; "
            "there is no callback and no caller-supplied verdict",
            "remaining_sub_obligations": (
                "no accepted entry point calls the guard; the one-line hook is blocked "
                "by byte-level source pins outside the allowlist (GUARD_IS_NOT_INSTALLED)",
            ),
            "human_review_required": True,
        },
        "PRB-3": {
            "mechanism_present": True,
            "single_internal_path": "_frozen_check_order, used by both public entries",
            "discriminating_tests_present": True,
            "integration_into_accepted_sources": False,
            "remaining_sub_obligations": (
                "the order binds every Route E path in this module; an accepted "
                "function called directly still follows its own order (LK-L1)",
            ),
            "human_review_required": True,
        },
        "PRB-4": {
            "mechanism_present": True,
            "closed_at_digest_level": True,
            "discriminating_tests_present": True,
            "persistence_or_external_anchoring": False,
            "remaining_sub_obligations": (
                "the root is computed and bound, never anchored; anchoring is PRB-6",
            ),
            "human_review_required": True,
        },
        "PRB-5": {
            "mechanism_present": True,
            "facade_present": True,
            "facade_is_a_gate": False,
            "route_e_specific_refusal_inside_accepted_sources": False,
            "guard_implemented": True,
            "guard_installed": True,
            "guard": "enforce_route_e_guard is INSTALLED, via _refuse_route_e_signal, as "
            "the FIRST statement of all five accepted public functions.  A typed "
            "RouteERequest presented to any of them runs the frozen check order and "
            "ALWAYS refuses, before any read, any write, any engine call and any "
            "acquisition.  No signature changed; no authorisation parameter was added.",
            "real_entry_point_refusal_tests": "5 of 5, calling the REAL public functions: "
            "run_owned_future_pipeline (PRB-F) plus the four added by "
            "FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_FINAL.  Each proves refusal at the "
            "first check with no effect, and the installed guard additionally proves "
            "refusal of a typed Route E signal at the first statement.",
            "non_route_e_behaviour_preserved": True,
            "blocked_by": (),
            "remaining_sub_obligations": (),
            "status": "CANDIDATE_CLOSED",
            "human_review_required": True,
        },
        "PRB-6": {
            "mechanism_present": True,
            "gate_is_fail_closed": True,
            "verifier_delivered": True,
            "verifier": "py_arkworks_bls12381, the maintained arkworks BLS12-381 "
            "binding, INSTALLED and pinned by version and wheel hash in "
            "requirements-route-e-lock.txt and used by route_e_bls_verifier; the "
            "no-network Go helper tools/drand_verify remains accepted when its bytes "
            "match the pinned digests.  No BLS arithmetic is written in this repository.",
            "chain_parameters_pinned_in_adapter": True,
            "round_derived_never_supplied": True,
            "remaining_sub_obligations": (
                "an absent verifier is a STOP, never a pass; the optional Go helper is "
                "still not committed and is only used when its bytes match the pins",
            ),
            "installed_verifier_distribution": "py_arkworks_bls12381",
            "installed_verifier_lockfile": "requirements-route-e-lock.txt",
            "status": "CANDIDATE_CLOSED",
            "anti_reroll_round_selection": "CANDIDATE_PASS: the designated round is "
            "derived from the frozen public timestamp, is never an argument, is verified "
            "cryptographically, and cannot be retried or substituted",
            "anti_reroll_publication": "UNPROVEN: that the root was actually published, "
            "immutably, at the declared instant is still ASSERTED by the commitment's "
            "venue and reference, not verified; verifying it needs a venue-specific "
            "inclusion proof, which is not delivered",
            "human_review_required": True,
        },
    }
