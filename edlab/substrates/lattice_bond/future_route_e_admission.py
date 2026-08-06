"""Independent admission of a Route E output root.

WHAT THIS IS
------------
The other half of the Route E security boundary.  :mod:`future_route_e_execution` performs
the canonical execution; this module decides, afterwards and independently, whether what is
on disk may contribute to the Route E dataset at all.

It re-reads EVERY byte from disk, recomputes the pre-run root ``P``, the seed root, the draw
plan, the enrolment, the file inventory and the post-run root ``E``, and re-derives the
per-world outcomes from the PERSISTED EVIDENCE.

WHAT IT NEVER DOES
------------------
* It never advances the engine.  It imports no engine and takes no step.
* It never believes a ``Y_i``, a ``k`` or a verdict written by the runner.  The canonical
  runner writes none, and this module REFUSES any root in which such a field appears.
* It never applies the ``42 / 9`` decision thresholds outside a confirmatory run.
* It never adds pilot or synthetic units to a confirmatory ``k``.

WHAT IT REFUSES
---------------
Anything that is not a canonical Route E root.  A generic
``future_prospective_measurement_bridge`` run, a Stage-B namespace, a
``stage_b_reproduce`` reproduction and a direct engine call all lack
``ROUTE_E_PROVENANCE.json`` with the canonical tag, so all four are inadmissible.  This is
an admissibility statement, not a claim that those paths cannot be executed: the frozen
decision ``UNIVERSAL_ENGINE_EXECUTION_PREVENTION = NOT_CLAIMED`` is respected literally.

Refusing a Route E claim does not make those artefacts unreadable.  In particular the
historical reproducer stays fully usable for historical reproducibility; only its
*admissibility as Route E evidence* is denied.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import future_route_e_pre_run_frame as _frame
from . import future_route_e_pre_run_locks as _locks
from . import future_route_e_execution as _execution

__all__ = [
    "ADMISSION_VERSION",
    "FORBIDDEN_RUNNER_FIELDS",
    "AdmissionVerdict",
    "WorldOutcome",
    "verify_route_e_run",
]

ADMISSION_VERSION = "future-route-e-admission/v1"

#: If any persisted document carries one of these, the root is refused: the runner is not
#: allowed to have an opinion about the answer.
FORBIDDEN_RUNNER_FIELDS: frozenset[str] = frozenset(
    {"y_i", "y", "k", "successes", "outcome", "outcomes", "verdict", "result", "results",
     "claim", "decision", "significant", "positive", "negative"}
)

_OBSERVED_FAILURE_BY_TERMINAL_STATE: Mapping[str, str] = {
    "DISSOLVED_DETECTED_TRACK": _frame.DrawDisposition.OBSERVED_FAILURE_DISSOLVED.value,
    "SPLIT_INTO_TRACKS": _frame.DrawDisposition.OBSERVED_FAILURE_SPLIT.value,
    "MERGED_INTO_TRACK": _frame.DrawDisposition.OBSERVED_FAILURE_MERGED.value,
    "UNRESOLVED_HANDOFF": _frame.DrawDisposition.OBSERVED_FAILURE_UNRESOLVED.value,
}

_LIFECYCLE_DOCUMENT_NAME = "LIFECYCLE.json"


class RouteEAdmissionRefused(RuntimeError):
    """The root is not admissible as Route E evidence."""

    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


@dataclass(frozen=True)
class WorldOutcome:
    """One world, recomputed from persisted evidence.  ``Y`` may be ``None``."""

    attempt_ordinal: int
    law_index: int
    ic_ordinal: int
    status: str
    disposition: str
    terminal_states: tuple[str, ...]
    Y: int | None
    recomputed_from: str


@dataclass(frozen=True)
class AdmissionVerdict:
    """An inert verdict.  Holding one grants nothing and authorises nothing."""

    output_directory: str
    admissible: bool
    reason_code: str
    reason: str
    pre_run_root: str | None = None
    post_run_root: str | None = None
    designated_round: int | None = None
    seed_root_sha256: str | None = None
    draw_plan_digest: str | None = None
    enrolment_digest: str | None = None
    mode: str | None = None
    fixture_class: str | None = None
    public_registry_inclusion_proven: bool = False
    engine_steps_taken: int = 0
    worlds: tuple[WorldOutcome, ...] = ()
    k_recomputed: int | None = None
    k_unknown: int = 0
    thresholds_applied: bool = False
    contributes_to_k: bool = False
    notes: tuple[str, ...] = ()


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _refuse(message: str, code: str) -> RouteEAdmissionRefused:
    return RouteEAdmissionRefused(message, reason_code=code)


def _read(path: Path, code: str, limit: int = 8_388_608) -> bytes:
    if not path.is_file():
        raise _refuse(f"{path.name} is absent", code)
    if path.stat().st_size > limit:
        raise _refuse(f"{path.name} exceeds the bounded size", code)
    return path.read_bytes()


def _canonical_object(payload: bytes, label: str, code: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise _refuse(f"{label} is not ASCII JSON: {exc}", code) from exc
    if not isinstance(value, dict):
        raise _refuse(f"{label} is not a JSON object", code)
    if _execution.canonical_bytes(value) != payload:
        raise _refuse(f"{label} is not in canonical form", code)
    return value


def _scan_for_runner_opinions(root: Path) -> None:
    """Refuse a root in which the runner recorded an answer instead of evidence."""
    for path in sorted(root.rglob("*.json")):
        if path.name == _LIFECYCLE_DOCUMENT_NAME:
            continue  # the lifecycle document is EVIDENCE; it is parsed, never trusted
        try:
            value = json.loads(path.read_bytes().decode("ascii"))
        except (UnicodeDecodeError, ValueError):
            continue
        stack: list[Any] = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, sub in item.items():
                    if isinstance(key, str) and key.lower() in FORBIDDEN_RUNNER_FIELDS:
                        raise _refuse(
                            f"{path.name} carries the field {key!r}: the runner may record "
                            "evidence, never an answer",
                            "RUNNER_WROTE_AN_ANSWER",
                        )
                    stack.append(sub)
            elif isinstance(item, list):
                stack.extend(item)


def _world_outcome(root: Path, attempt: Mapping[str, Any]) -> WorldOutcome:
    ordinal = int(attempt["attempt_ordinal"])
    law_index = int(attempt["law_index"])
    ic_ordinal = int(attempt["ic_ordinal"])
    status = str(attempt["status"])
    if status != "SUCCESS":
        return WorldOutcome(
            attempt_ordinal=ordinal,
            law_index=law_index,
            ic_ordinal=ic_ordinal,
            status=status,
            disposition=_frame.DrawDisposition.TECHNICALLY_UNKNOWN.value,
            terminal_states=(),
            Y=None,
            recomputed_from="attempt inventory: a crash is UNKNOWN and never a silent 0",
        )
    document_path = root / str(attempt["world_relative_path"]) / _LIFECYCLE_DOCUMENT_NAME
    if not document_path.is_file():
        raise _refuse(
            f"world {ordinal} is recorded as SUCCESS but its lifecycle evidence is absent",
            "EVIDENCE_MISSING",
        )
    payload = document_path.read_bytes()
    if _sha256_hex(payload) != str(attempt["lifecycle_document_sha256"]):
        raise _refuse(
            f"world {ordinal} lifecycle evidence does not match the inventoried digest",
            "EVIDENCE_ALTERED",
        )
    document = json.loads(payload.decode("utf-8"))
    records = document.get("terminal_records")
    if not isinstance(records, list):
        raise _refuse(f"world {ordinal} lifecycle evidence has no terminal records", "EVIDENCE_MALFORMED")
    states = tuple(str(item.get("terminal_state")) for item in records)
    for state in states:
        if state not in _frame.FROZEN_TERMINAL_STATES:
            raise _refuse(
                f"world {ordinal} reports the unknown terminal state {state!r}",
                "EVIDENCE_MALFORMED",
            )
    if not states:
        return WorldOutcome(
            attempt_ordinal=ordinal, law_index=law_index, ic_ordinal=ic_ordinal,
            status=status,
            disposition=_frame.DrawDisposition.MECHANICALLY_INELIGIBLE.value,
            terminal_states=states, Y=0,
            recomputed_from="persisted lifecycle document: no eligible component",
        )
    for state in states:
        if state in _OBSERVED_FAILURE_BY_TERMINAL_STATE:
            disposition = _OBSERVED_FAILURE_BY_TERMINAL_STATE[state]
            return WorldOutcome(
                attempt_ordinal=ordinal, law_index=law_index, ic_ordinal=ic_ordinal,
                status=status, disposition=disposition, terminal_states=states, Y=0,
                recomputed_from="persisted lifecycle document: observed failure",
            )
    # Only RIGHT_CENSORED_AT_HORIZON remains.  The frozen table splits that terminal state
    # between SUCCESS and OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT on verified
    # replacement evidence, which this mission does not produce.  The ambiguity is named,
    # never resolved silently, so Y stays UNKNOWN.
    return WorldOutcome(
        attempt_ordinal=ordinal, law_index=law_index, ic_ordinal=ic_ordinal,
        status=status,
        disposition=_frame.DrawDisposition.TECHNICALLY_UNKNOWN.value,
        terminal_states=states, Y=None,
        recomputed_from=(
            "persisted lifecycle document: RIGHT_CENSORED_AT_HORIZON without verified "
            "replacement evidence is UNKNOWN, never a silent 1 and never a silent 0"
        ),
    )


def verify_route_e_run(
    output_directory: str | os.PathLike[str],
    final_receipt_path: str | os.PathLike[str] | None = None,
) -> AdmissionVerdict:
    """Decide whether ``output_directory`` is admissible Route E evidence.

    Reads everything from disk, recomputes everything, takes no engine step, and returns
    an inert verdict.  A refusal is returned as a verdict, never raised, so a caller cannot
    mistake an exception handler for an authorisation.
    """
    root = Path(output_directory)
    engine_steps = 0
    notes: list[str] = []
    try:
        if not root.is_dir():
            raise _refuse(f"{root} is not a directory", "NOT_A_DIRECTORY")

        # 1 -- provenance.  This is what makes a generic artefact inadmissible.
        provenance_path = root / _execution.PROVENANCE_NAME
        if not provenance_path.is_file():
            raise _refuse(
                "there is no ROUTE_E_PROVENANCE.json: this root was not produced by the "
                "canonical Route E entry point.  A generic measurement-bridge run, a "
                "Stage-B namespace, a historical reproduction and a direct engine call all "
                "land here.  They remain readable; they are not Route E evidence.",
                "NOT_A_CANONICAL_ROUTE_E_ROOT",
            )
        provenance = _canonical_object(
            _read(provenance_path, "PROVENANCE_UNREADABLE"), "the provenance", "PROVENANCE_UNREADABLE"
        )
        if provenance.get("tag") != _execution.ROUTE_E_PROVENANCE_TAG:
            raise _refuse("the provenance tag is not the canonical one", "NOT_A_CANONICAL_ROUTE_E_ROOT")

        _scan_for_runner_opinions(root)

        # 2 -- recompute P from the manifest bytes on disk.
        manifest_bytes = _read(root / _execution.PRE_RUN_MANIFEST_NAME, "MANIFEST_UNREADABLE")
        manifest = _canonical_object(manifest_bytes, "the pre-run manifest", "MANIFEST_UNREADABLE")
        if manifest.get("kind") != _execution.PRE_RUN_KIND:
            raise _refuse("the pre-run manifest has the wrong kind", "KIND_MISMATCH")
        recomputed_p = _execution.pre_run_root(manifest)
        if provenance.get("pre_run_root") != recomputed_p:
            raise _refuse("the provenance binds a different pre-run root", "PRE_RUN_ROOT_MISMATCH")

        # 3 -- anteriority.
        anteriority_bytes = _read(root / _execution.ANTERIORITY_NAME, "ANTERIORITY_UNREADABLE")
        anteriority = _canonical_object(
            anteriority_bytes, "the anteriority proof", "ANTERIORITY_UNREADABLE"
        )
        if anteriority.get("binds_pre_run_root") != recomputed_p:
            raise _refuse("the anteriority proof binds a different pre-run root", "ANTERIORITY_MISMATCH")
        if anteriority.get("binds_cutoff_C") != manifest.get("canonical_cutoff_C"):
            raise _refuse("the anteriority proof binds a different cutoff", "ANTERIORITY_MISMATCH")
        public_inclusion = bool(anteriority.get("public_registry_inclusion_proven"))

        # 4 -- the round is a function of the cutoff alone.
        designated = _frame.designated_round(int(manifest["canonical_cutoff_C"]))

        # 5 -- the beacon response on disk must be the one the round designates.
        beacon_bytes = _read(root / _execution.BEACON_RESPONSE_NAME, "BEACON_UNREADABLE")
        beacon = _canonical_object(beacon_bytes, "the beacon response", "BEACON_UNREADABLE")
        if int(beacon.get("round", -1)) != designated:
            raise _refuse(
                "the persisted beacon response is not the round the cutoff designates",
                "ROUND_MISMATCH",
            )
        randomness = bytes.fromhex(str(beacon["randomness"]))
        if len(randomness) != 32:
            raise _refuse("the persisted randomness is not 32 bytes", "BEACON_MALFORMED")

        # 6 -- seed, plan and enrolment, recomputed, never read.
        seed_root = _execution.derive_route_e_seed_root(
            pre_run_root_sha256=recomputed_p,
            beacon_round=designated,
            beacon_randomness=randomness,
        )
        enrolment_bytes = _read(root / _execution.ENROLMENT_NAME, "ENROLMENT_UNREADABLE")
        enrolment_document = _canonical_object(
            enrolment_bytes, "the enrolment", "ENROLMENT_UNREADABLE"
        )
        policy = manifest["sample_size_and_world_policy"]
        n_draws = int(policy["n_draws"])
        worlds = int(policy["worlds"])
        plan = _frame.build_draw_plan(seed_root, count=n_draws)
        if _sha256_hex(seed_root) != enrolment_document.get("seed_root_sha256"):
            raise _refuse(
                "the recorded seed root is not the one P and the verified randomness "
                "derive; no seed is ever accepted from a caller or from disk",
                "SEED_MISMATCH",
            )
        if plan.digest() != enrolment_document.get("draw_plan_digest"):
            raise _refuse("the recorded draw plan is not the one the seed derives", "PLAN_MISMATCH")
        enrolment = _locks.FamilyEnrolment(
            run_identity=str(manifest["run_identity"]),
            seed_root_sha256=_sha256_hex(seed_root),
            draw_plan_digest=plan.digest(),
            n_draws=n_draws,
            worlds=worlds,
        )
        recomputed_enrolment_digest = _locks.enrolment_digest(enrolment)
        if recomputed_enrolment_digest != enrolment_document.get("enrolment_digest"):
            raise _refuse("the enrolment digest does not match the recomputed enrolment", "ENROLMENT_MISMATCH")
        expected_order = [list(item) for item in plan.world_order[:worlds]]
        if enrolment_document.get("world_order") != expected_order:
            raise _refuse("the recorded world order is not the canonical one", "WORLD_ORDER_MISMATCH")

        # 7 -- the attempt inventory: complete, ordered, nothing deleted.
        attempts_bytes = _read(root / _execution.ATTEMPTS_NAME, "ATTEMPTS_UNREADABLE")
        attempts: list[dict[str, Any]] = []
        for line in attempts_bytes.split(b"\n"):
            if not line:
                continue
            attempts.append(_canonical_object(line, "an attempt", "ATTEMPTS_MALFORMED"))
        if len(attempts) != worlds:
            raise _refuse(
                f"the attempt inventory holds {len(attempts)} entries for {worlds} worlds: "
                "an attempt was dropped, and a dropped attempt is never tolerated",
                "ATTEMPT_INVENTORY_INCOMPLETE",
            )
        for index, attempt in enumerate(attempts):
            if int(attempt.get("attempt_ordinal", -1)) != index:
                raise _refuse("the attempt inventory is out of order", "ATTEMPT_ORDER_CHANGED")
            if [int(attempt["law_index"]), int(attempt["ic_ordinal"])] != expected_order[index]:
                raise _refuse(
                    "an attempt does not sit at its canonical position in the world order",
                    "ATTEMPT_ORDER_CHANGED",
                )

        # 7b -- PRB-1 and PRB-4: the persisted join and the persisted replay root are
        # re-read from disk, recomputed from those bytes, and required.  A missing,
        # mutated, swapped or foreign artefact refuses here, before any admission.
        replay_bytes = _read(root / _execution.REPLAY_ROOT_NAME, "REPLAY_ROOT_UNREADABLE")
        replay_document = _canonical_object(
            replay_bytes, "the replay root document", "REPLAY_ROOT_UNREADABLE"
        )
        if replay_document.get("kind") != _execution.REPLAY_ROOT_KIND:
            raise _refuse("the replay root document has the wrong kind", "KIND_MISMATCH")
        if replay_document.get("run_identity") != str(manifest["run_identity"]):
            raise _refuse(
                "the replay root document belongs to another run identity",
                "REPLAY_ROOT_FOREIGN_RUN",
            )
        if replay_document.get("pre_run_root") != recomputed_p:
            raise _refuse(
                "the replay root document binds a different pre-run root",
                "REPLAY_ROOT_FOREIGN_RUN",
            )
        if replay_document.get("enrolment_digest") != recomputed_enrolment_digest:
            raise _refuse(
                "the replay root document binds a different enrolment",
                "REPLAY_ROOT_MISMATCH",
            )
        successes = [item for item in attempts if item.get("status") == "SUCCESS"]
        recorded_worlds = replay_document.get("worlds")
        if not isinstance(recorded_worlds, list) or len(recorded_worlds) != len(successes):
            raise _refuse(
                "the replay root document does not cover exactly the successful worlds",
                "REPLAY_ROOT_INCOMPLETE",
            )
        for attempt, recorded in zip(successes, recorded_worlds):
            if int(recorded.get("attempt_ordinal", -1)) != int(attempt["attempt_ordinal"]):
                raise _refuse("the replay root document is out of order", "REPLAY_ROOT_MISMATCH")
            world_directory = root / str(attempt["world_relative_path"])
            join_path = world_directory / _locks.JOIN_EVIDENCE_FILENAME
            try:
                _, recomputed_join = _locks.read_join_evidence(join_path)
            except Exception as exc:  # noqa: BLE001 - any refusal is a refusal
                raise _refuse(
                    f"the persisted track-component join is absent or not canonical: {exc}",
                    "JOIN_EVIDENCE_INVALID",
                ) from exc
            if recomputed_join != attempt.get("track_component_join_sha256"):
                raise _refuse(
                    "the persisted join does not reproduce the digest the attempt records",
                    "JOIN_EVIDENCE_MISMATCH",
                )
            if recomputed_join != recorded.get("track_component_join_sha256"):
                raise _refuse(
                    "the replay root document binds another join digest",
                    "JOIN_EVIDENCE_MISMATCH",
                )
            recomputed_replay = _locks.route_e_root(
                measurement_root_sha256=str(attempt["measurement_root_sha256"]),
                track_component_join_digest=recomputed_join,
                family_enrolment_digest=recomputed_enrolment_digest,
            )
            if recomputed_replay != attempt.get("route_e_replay_root"):
                raise _refuse(
                    "the attempt records a replay root the persisted evidence does not "
                    "recompute; a root is never reconstructed from a missing artefact",
                    "REPLAY_ROOT_MISMATCH",
                )
            if recomputed_replay != recorded.get("route_e_replay_root"):
                raise _refuse(
                    "the replay root document binds another replay root",
                    "REPLAY_ROOT_MISMATCH",
                )
        notes.append(
            f"PRB-1/PRB-4: {len(successes)} persisted join(s) and replay root(s) re-read "
            "from disk and recomputed"
        )

        # 8 -- the file inventory must be exact.
        inventory_bytes = _read(root / _execution.FILE_INVENTORY_NAME, "INVENTORY_UNREADABLE")
        inventory = _canonical_object(inventory_bytes, "the file inventory", "INVENTORY_UNREADABLE")
        recorded = {entry["path"]: entry for entry in inventory.get("entries", [])}
        observed: dict[str, tuple[str, int]] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in _execution._INVENTORY_EXCLUDED:
                continue
            payload = path.read_bytes()
            observed[relative] = (_sha256_hex(payload), len(payload))
        missing = sorted(set(recorded) - set(observed))
        added = sorted(set(observed) - set(recorded))
        if missing or added:
            raise _refuse(
                f"the file inventory is not exact: missing={missing[:5]} added={added[:5]}",
                "FILE_INVENTORY_INEXACT",
            )
        for relative, (digest, size) in observed.items():
            entry = recorded[relative]
            if entry["sha256"] != digest or int(entry["bytes"]) != size:
                raise _refuse(
                    f"{relative} does not match its inventoried digest", "FILE_INVENTORY_INEXACT"
                )

        # 9 -- recompute E and compare with the sealed receipt.
        envelope_bytes = _read(root / _execution.POST_RUN_ENVELOPE_NAME, "ENVELOPE_UNREADABLE")
        envelope = _canonical_object(envelope_bytes, "the post-run envelope", "ENVELOPE_UNREADABLE")
        if envelope.get("kind") != _execution.POST_RUN_KIND:
            raise _refuse(
                "the post-run envelope has the wrong kind; a pre-run manifest can never be "
                "presented as a post-run envelope",
                "KIND_MISMATCH",
            )
        if envelope.get("pre_run_root") != recomputed_p:
            raise _refuse("the envelope binds a different pre-run root", "ENVELOPE_MISMATCH")
        if envelope.get("file_inventory_sha256") != _sha256_hex(inventory_bytes):
            raise _refuse("the envelope binds a different file inventory", "ENVELOPE_MISMATCH")
        if envelope.get("attempts") != attempts:
            raise _refuse(
                "the envelope does not bind exactly the attempt inventory on disk",
                "ENVELOPE_MISMATCH",
            )
        if envelope.get("seed_root_sha256") != _sha256_hex(seed_root):
            raise _refuse("the envelope binds a different seed root", "ENVELOPE_MISMATCH")
        if envelope.get("designated_round") != designated:
            raise _refuse("the envelope binds a different round", "ENVELOPE_MISMATCH")
        recomputed_e = _execution.post_run_root(envelope)

        receipt_path = (
            Path(final_receipt_path)
            if final_receipt_path is not None
            else root / _execution.FINAL_RECEIPT_NAME
        )
        receipt = _canonical_object(
            _read(receipt_path, "RECEIPT_UNREADABLE"), "the final receipt", "RECEIPT_UNREADABLE"
        )
        if receipt.get("post_run_root") != recomputed_e:
            raise _refuse(
                "the sealed post-run root is not the one the evidence on disk recomputes",
                "POST_RUN_ROOT_MISMATCH",
            )
        if receipt.get("envelope_sha256") != _sha256_hex(envelope_bytes):
            raise _refuse("the receipt binds a different envelope", "RECEIPT_MISMATCH")

        # 10 -- outcomes, recomputed from evidence only.
        outcomes = tuple(_world_outcome(root, attempt) for attempt in attempts)
        k_recomputed = sum(1 for item in outcomes if item.Y == 1)
        k_unknown = sum(1 for item in outcomes if item.Y is None)

        mode = str(manifest["mode"])
        fixture = str(manifest["fixture_class"])
        thresholds_applied = mode == "CONFIRMATORY_67" and fixture == "SCIENTIFIC"
        if not thresholds_applied:
            notes.append(
                "the 42 / 9 thresholds are NOT applied: they belong to a confirmatory "
                "scientific run and to nothing else"
            )
        contributes = False
        if fixture != "SCIENTIFIC":
            notes.append("a synthetic non-scientific fixture never contributes to any dataset")
        if mode != "CONFIRMATORY_67":
            notes.append("pilot units are never added to the confirmatory k")
        if not public_inclusion:
            notes.append(
                "public pre-run inclusion is NOT proven, so this root may not contribute "
                "to the Route E dataset even if everything else recomputes"
            )
        if k_unknown:
            notes.append(
                f"{k_unknown} world(s) are UNKNOWN and stay in the denominator; an unknown "
                "is never silently 0 and never silently 1"
            )

        return AdmissionVerdict(
            output_directory=str(root),
            admissible=True,
            reason_code="RECOMPUTED",
            reason=(
                "every byte was re-read, P, the seed, the plan, the enrolment, the file "
                "inventory and E were recomputed, and the outcomes were re-derived from "
                "persisted evidence without a single engine step"
            ),
            pre_run_root=recomputed_p,
            post_run_root=recomputed_e,
            designated_round=designated,
            seed_root_sha256=_sha256_hex(seed_root),
            draw_plan_digest=plan.digest(),
            enrolment_digest=recomputed_enrolment_digest,
            mode=mode,
            fixture_class=fixture,
            public_registry_inclusion_proven=public_inclusion,
            engine_steps_taken=engine_steps,
            worlds=outcomes,
            k_recomputed=k_recomputed,
            k_unknown=k_unknown,
            thresholds_applied=thresholds_applied,
            contributes_to_k=contributes,
            notes=tuple(notes),
        )
    except RouteEAdmissionRefused as exc:
        return AdmissionVerdict(
            output_directory=str(root),
            admissible=False,
            reason_code=exc.reason_code,
            reason=str(exc),
            engine_steps_taken=engine_steps,
            contributes_to_k=False,
            notes=tuple(notes),
        )
