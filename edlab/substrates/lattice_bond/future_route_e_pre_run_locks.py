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

LOCK LIMITATION REGISTER
------------------------
LK-L1  The accepted sources (engine, instrumentation, lifecycle, runner, owned
       pipeline, measurement bridge) are immutable under the frozen allowlist.  Every
       lock here therefore sits in the ROUTE E path, in front of them.  A caller who
       bypasses the Route E path and calls an accepted function directly is refused by
       that function's own first check, which is a weaker property, separately tested
       and separately bounded (see PRB-5 below).
LK-L2  ``verify_public_commitment`` and ``consume_beacon_round`` require a verifier
       supplied by the caller.  No verifier is bundled: closing PRB-6 and HR-4 with a
       real BLS check needs a maintained cryptographic dependency, and adding one would
       modify ``pyproject.toml``, which is outside the frozen allowlist.  The gate is
       implemented and fail-closed; the CRYPTOGRAPHIC VERIFIER ITSELF REMAINS AN OPEN
       SUB-OBLIGATION, reported rather than faked.
LK-L3  The Route E root binds the measurement root, the track-component join and the
       family enrolment.  It does not replace the bridge's own measurement root, which
       is computed inside an immutable accepted source.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from .instrumentation import TrackingResult

__all__ = [
    "LOCKS_VERSION",
    "PRE_RUN_BLOCKERS",
    # PRB-1
    "JoinRecord",
    "canonical_cell_set_digest",
    "build_track_component_join",
    "join_digest",
    # PRB-4
    "FamilyEnrolment",
    "enrolment_digest",
    "route_e_root",
    # PRB-6
    "PublicCommitment",
    "CommitmentInvalid",
    "verify_public_commitment",
    # PRB-2
    "RouteEReceipt",
    "ReceiptMissing",
    "ReceiptInvalid",
    # PRB-3
    "CHECK_ORDER",
    "CheckOrderViolation",
    "RouteEAnalysisRefused",
    "open_route_e_analysis",
    # PRB-5
    "SUPPORTED_ENTRY_POINTS",
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
# ======================================================================================


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
    """Every assignment of the tracking artefact, as a canonical join record.

    ``components_by_frame[frame][component_index] = (shape, cells)``.  Every assignment
    must resolve: a missing component is a refusal, never a silently dropped row.
    """
    if not isinstance(tracking, TrackingResult):
        raise TypeError("tracking must be a TrackingResult")
    records: list[JoinRecord] = []
    for frame, component_index, track_id in tracking.assignments:
        try:
            shape, cells = components_by_frame[frame][component_index]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"no component support for (frame={frame}, index={component_index})"
            ) from exc
        records.append(
            JoinRecord(
                frame=int(frame),
                cell_set_sha256=canonical_cell_set_digest(tuple(shape), cells),
                track_id=int(track_id),
            )
        )
    return tuple(sorted(records, key=JoinRecord.as_tuple))


def join_digest(records: Sequence[JoinRecord]) -> str:
    """Order-independent digest of a complete join.  Empty joins are refused."""
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise TypeError("records must be a sequence of JoinRecord")
    if not records:
        raise ValueError("an empty join is refused: PRB-1 requires the join to exist")
    rows = []
    for record in records:
        if not isinstance(record, JoinRecord):
            raise TypeError("every record must be a JoinRecord")
        rows.append([record.frame, record.cell_set_sha256, record.track_id])
    payload = {"schema": LOCKS_VERSION, "join": sorted(rows)}
    return _sha256_hex(_canonical_bytes(payload))


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


CommitmentVerifier = Callable[[PublicCommitment], bool]


def verify_public_commitment(
    commitment: PublicCommitment | None,
    *,
    verifier: CommitmentVerifier | None,
    expected_root_sha256: str,
    must_precede_unix: int | None = None,
) -> None:
    """Fail-closed verification of PRB-6.  Returns ``None`` or raises.

    In this order, and no other:
      1. a commitment must be present and well formed;
      2. it must bind exactly the expected root;
      3. a verifier must be supplied -- there is no default and no bundled verifier;
      4. the verifier must return exactly ``True``;
      5. if ``must_precede_unix`` is given, the PUBLIC timestamp must be strictly
         earlier, which is the anti-reroll precondition HR-3 requires.
    """
    if commitment is None:
        raise CommitmentInvalid("refused: no public commitment was presented")
    if not isinstance(commitment, PublicCommitment):
        raise CommitmentInvalid("refused: commitment is not a PublicCommitment")
    if not _is_sha256_hex(expected_root_sha256):
        raise CommitmentInvalid("refused: expected root is not a sha256 digest")
    if commitment.root_sha256 != expected_root_sha256:
        raise CommitmentInvalid("refused: the commitment does not bind the expected root")
    if verifier is None:
        raise CommitmentInvalid(
            "refused: no commitment verifier supplied; PRB-6 has no bundled verifier "
            "and none is inferred (LK-L2)"
        )
    if not callable(verifier):
        raise CommitmentInvalid("refused: verifier is not callable")
    try:
        verdict = verifier(commitment)
    except Exception as exc:  # noqa: BLE001 - any verifier failure is a refusal
        raise CommitmentInvalid(f"refused: the commitment verifier raised: {exc!r}") from exc
    if verdict is not True:
        raise CommitmentInvalid("refused: the commitment verifier did not return True")
    if must_precede_unix is not None:
        if isinstance(must_precede_unix, bool) or not isinstance(must_precede_unix, int):
            raise CommitmentInvalid("refused: must_precede_unix must be a plain int")
        if commitment.published_at_unix >= must_precede_unix:
            raise CommitmentInvalid(
                "refused: the public commitment is not strictly prior to the designated "
                "instant; a commitment published at or after the reveal cannot bind it"
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
    """A receipt is a claim that ``root_sha256`` was anchored by ``commitment``."""

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
# ======================================================================================

CHECK_ORDER: tuple[str, ...] = ("LOCAL_EVIDENCE", "ROOT_DIGEST", "VERIFIER")


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


def open_route_e_analysis(
    *,
    local_evidence_ok: bool,
    recomputed_root_sha256: str,
    receipt: RouteEReceipt | None,
    verifier: CommitmentVerifier | None,
    must_precede_unix: int | None = None,
    trace: list[str] | None = None,
) -> None:
    """The single supported Route E analysis entry point.  Fail-closed, in order.

    1. LOCAL_EVIDENCE -- the caller's local re-verification must have succeeded.
    2. ROOT_DIGEST    -- a receipt must exist and bind the RECOMPUTED root exactly.
    3. VERIFIER       -- the public commitment must verify, and be prior.

    A failure at step *n* raises before step *n+1* is entered; that is what ``trace``
    pins.  Even when all three pass, this function refuses, because
    ``scientific_run_authorized`` is ``False`` for this mission and no preregistration
    or execution authorisation exists.
    """
    order = _OrderTrace()

    order.enter("LOCAL_EVIDENCE")
    if trace is not None:
        trace.append("LOCAL_EVIDENCE")
    if local_evidence_ok is not True:
        raise RouteEAnalysisRefused("refused at LOCAL_EVIDENCE: local re-verification failed")

    order.enter("ROOT_DIGEST")
    if trace is not None:
        trace.append("ROOT_DIGEST")
    if receipt is None:
        raise ReceiptMissing("refused at ROOT_DIGEST: no receipt was presented")
    if not isinstance(receipt, RouteEReceipt):
        raise ReceiptInvalid("refused at ROOT_DIGEST: receipt is not a RouteEReceipt")
    if not _is_sha256_hex(recomputed_root_sha256):
        raise ReceiptInvalid("refused at ROOT_DIGEST: recomputed root is not a digest")
    if receipt.root_sha256 != recomputed_root_sha256:
        raise ReceiptInvalid(
            "refused at ROOT_DIGEST: the receipt does not bind the recomputed root"
        )

    order.enter("VERIFIER")
    if trace is not None:
        trace.append("VERIFIER")
    verify_public_commitment(
        receipt.commitment,
        verifier=verifier,
        expected_root_sha256=recomputed_root_sha256,
        must_precede_unix=must_precede_unix,
    )

    raise RouteEAnalysisRefused(
        "refused after VERIFIER: scientific_run_authorized is False; no preregistration "
        "exists and no human review has authorised execution"
    )


# ======================================================================================
# PRB-5  single supported entry point -- all five, each with its own refusal
# ======================================================================================

SUPPORTED_ENTRY_POINTS: tuple[str, ...] = (
    "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
    "future_lifecycle_owned_pipeline.open_owned_analysis_access",
    "future_lifecycle_runner.open_analysis_access",
    "future_lifecycle_runner.publish_future_family_completion",
    "lifecycle.qualify_and_write_lifecycle_contract",
)


class EntryPointRefused(RuntimeError):
    """The Route E entry gate refused before dispatching to an accepted source."""


def route_e_entry(
    entry_point: str,
    *,
    authorisation: Any = None,
    receipt: RouteEReceipt | None = None,
    verifier: CommitmentVerifier | None = None,
    **_ignored: Any,
) -> None:
    """The ONLY in-protocol way for Route E to reach an accepted entry point.

    It refuses before anything: before entropy, before any network or external source,
    before any subprocess, before any seed, family or namespace, before any law or
    initial condition, before the engine, before any file, before any result read and
    before any persistent write.  Nothing below this refusal is ever reached, which is
    what the per-entry-point refusal tests pin -- one test per entry point, five in all.
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
    if receipt is None:
        raise ReceiptMissing(
            f"refused: {entry_point} requires a verified receipt (PRB-2) and none was given"
        )
    if not isinstance(receipt, RouteEReceipt):
        raise ReceiptInvalid(f"refused: {entry_point} received a malformed receipt")
    verify_public_commitment(
        receipt.commitment,
        verifier=verifier,
        expected_root_sha256=receipt.root_sha256,
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
# Honest per-blocker status.  Read by the report and by the DECISION.json.
# ======================================================================================


def blocker_status() -> Mapping[str, Mapping[str, Any]]:
    """What is closed, what is not, and what the residue is.  No optimism."""
    return {
        "PRB-1": {
            "closed": True,
            "mechanism": "JoinRecord / canonical_cell_set_digest / build_track_component_join "
            "/ join_digest, bound into route_e_root",
            "residue": None,
        },
        "PRB-2": {
            "closed": True,
            "mechanism": "RouteEReceipt required by open_route_e_analysis and by "
            "route_e_entry; absence raises ReceiptMissing before anything else",
            "residue": None,
        },
        "PRB-3": {
            "closed": True,
            "mechanism": "CHECK_ORDER pinned by _OrderTrace inside open_route_e_analysis; "
            "a failure at step n raises before step n+1 is entered",
            "residue": None,
        },
        "PRB-4": {
            "closed": True,
            "mechanism": "FamilyEnrolment (run identity + seed root + draw plan digest + "
            "counts) folded into route_e_root",
            "residue": None,
        },
        "PRB-5": {
            "closed": True,
            "mechanism": "route_e_entry gates all five literal entry points; one refusal "
            "test per entry point, each proving refusal before every listed effect",
            "residue": "the accepted functions remain reachable outside the Route E path; "
            "that weaker property is tested separately and bounded (LK-L1)",
        },
        "PRB-6": {
            "closed": False,
            "mechanism": "PublicCommitment + verify_public_commitment, fail-closed, with "
            "the strict-priority precondition HR-3 requires",
            "residue": "OPEN: no maintained BLS / commitment verifier is available inside "
            "the frozen allowlist; supplying one would modify pyproject.toml. The gate is "
            "implemented and refuses without a verifier, but the verifier itself is not "
            "delivered (LK-L2)",
        },
    }
