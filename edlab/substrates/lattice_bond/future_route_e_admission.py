"""Independent admission of a Route E output root.  A1-R3.

WHAT CHANGED FROM A1-R2, AND WHY
--------------------------------
A1-R2 called itself an independent verification while (a) never re-verifying the beacon,
(b) believing a boolean the producer wrote, (c) never re-applying the manifest schema or the
frozen confirmatory shape, (d) never checking source digests, (e) never recomputing the
bridge proofs, and (f) offering no code path that could ever return ``Y = 1``.  It also
summed ``k`` over 134 worlds, which is twice the frozen number of primary units.

This module re-derives everything from bytes:

``verify_route_e_run`` NEVER raises.  Every malformed document, missing key, truncated JSON
and unexpected type becomes an ``AdmissionVerdict`` with ``admissible=False`` and a reason
code.  A caller cannot mistake an exception handler for an authorisation, and cannot mistake
an ambiguous crash for a refusal.

INDEPENDENCE, STATED HONESTLY
-----------------------------
The pure protocol primitives live in :mod:`edlab.route_e_protocol`, outside
``edlab.substrates``, importing neither the engine nor NumPy.  This module no longer reuses
a single private helper of ``future_route_e_execution``.

It does still import ``LatticeBondSpec`` transitively, and that is not concealed: the frozen
01S obligation makes the sampler's acceptance predicate the engine's OWN
``LatticeBondSpec`` construction, so recomputing the draw plan cannot avoid it.  "Recompute
the plan" and "import no engine" are contradictory by frozen design.

The claim, and the whole claim, established at runtime by
``tests/test_future_route_e_a1r3_admission.py`` in a fresh subprocess:

    No ``LatticeBondEngine`` is instantiated, no simulation step is taken, and no mutation
    of the output tree occurs during admission.

Nothing is claimed about a "first general effect": reads, imports and the cryptographic
subprocess all exist.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ... import route_e_protocol as _p
from . import future_route_e_pre_run_frame as _frame
from . import future_route_e_pre_run_locks as _locks
from . import future_route_e_world_evidence as _evidence
from .future_prospective_measurement_bridge import MeasurementSpec

__all__ = [
    "ADMISSION_VERSION",
    "AdmissionVerdict",
    "WorldOutcome",
    "verify_route_e_run",
]

ADMISSION_VERSION = "future-route-e-admission/v2-a1r3"

_LIFECYCLE_DOCUMENT_NAME = "LIFECYCLE.json"
_MEASUREMENT_DOCUMENT_NAME = "MEASUREMENT.json"
_BRIDGE_BINDING_NAME = "BRIDGE_BINDING.json"
_JOIN_NAME = "TRACK_COMPONENT_JOIN.json"

_PROVENANCE_NAME = "ROUTE_E_PROVENANCE.json"
_PRE_RUN_MANIFEST_NAME = "PRE_RUN_MANIFEST.json"
_ANTERIORITY_NAME = "PRE_RUN_ANTERIORITY.json"
_BEACON_RESPONSE_NAME = "BEACON_RESPONSE.json"
_ENROLMENT_NAME = "ENROLMENT.json"
_ATTEMPTS_NAME = "ATTEMPTS.jsonl"
_FILE_INVENTORY_NAME = "FILE_INVENTORY.json"
_POST_RUN_ENVELOPE_NAME = "POST_RUN_ENVELOPE.json"
_FINAL_RECEIPT_NAME = "FINAL_RECEIPT.json"
_INVENTORY_EXCLUDED = (_FILE_INVENTORY_NAME, _POST_RUN_ENVELOPE_NAME, _FINAL_RECEIPT_NAME)

_PINNED_VERIFIER_SHA256 = frozenset(
    {
        "2534fa4af5ed6d6d4294be26542b52fe7445412532db97e66a955cacba3cca6d",
        "ea15b5de9f88a6fd0557e1912c31493670f9322bc901d8841b6868cd3220045c",
    }
)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _refuse(message: str, code: str) -> _p.ProtocolRefusal:
    return _p.ProtocolRefusal(message, reason_code=code)


@dataclass(frozen=True)
class WorldOutcome:
    """One world, recomputed from persisted evidence.  ``Y_by_f`` may hold ``None``."""

    attempt_ordinal: int
    law_index: int
    ic_ordinal: int
    status: str
    is_primary: bool
    terminal_states: tuple[str, ...]
    disposition_by_f: Mapping[str, str]
    Y_by_f: Mapping[str, int | None]
    residual_min: float | None
    observed_from_first_frame: bool
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
    anteriority_proof_type: str | None = None
    public_registry_inclusion_proven: bool = False
    beacon_reverified: bool = False
    source_bytes_bound: bool = False
    engine_steps_taken: int = 0
    worlds: tuple[WorldOutcome, ...] = ()
    primary_unit_count: int = 0
    #: f -> k, summed over PRIMARY units only.  ``None`` when any primary is unknown.
    k_by_f: Mapping[str, int | None] = None  # type: ignore[assignment]
    #: f -> psi = proportion of laws whose two initial conditions disagree.
    psi_by_f: Mapping[str, float | None] = None  # type: ignore[assignment]
    unknown_primaries: int = 0
    thresholds_applied: bool = False
    contributes_to_k: bool = False
    notes: tuple[str, ...] = ()


# --------------------------------------------------------------------------------------
# source and protocol digest binding (defect 5)
# --------------------------------------------------------------------------------------


def _bind_source_digests(manifest: Mapping[str, Any], source_root: Path) -> list[str]:
    """Compare every frozen digest to the bytes actually present in the running tree.

    A1-R2 verified the digests of the OUTPUT root and nothing else, so the manifest could
    name any source commit and any protocol digest without consequence.  Here a declared
    path that is absent, or whose bytes differ, is a refusal.
    """
    notes: list[str] = []
    blocks = (
        ("source_commit_and_digests", manifest.get("source_commit_and_digests")),
        ("protocol_and_analysis_digests", manifest.get("protocol_and_analysis_digests")),
    )
    checked = 0
    for label, block in blocks:
        if not isinstance(block, Mapping):
            raise _refuse(f"{label} is not an object", "MANIFEST_SCHEMA")
        digests = block.get("digests") if "digests" in block else block
        if not isinstance(digests, Mapping) or not digests:
            raise _refuse(f"{label} carries no digest map", "MANIFEST_SCHEMA")
        for relative, declared in sorted(digests.items()):
            if not isinstance(relative, str) or not isinstance(declared, str):
                raise _refuse(f"{label} has a non-string digest entry", "MANIFEST_SCHEMA")
            if len(declared) != 64:
                # A commit hash or a free-form note is not a file digest; it is recorded
                # but never silently accepted as one.
                notes.append(f"{label}.{relative} is not a 64-hex file digest; not bound")
                continue
            candidate = (source_root / relative).resolve()
            try:
                candidate.relative_to(source_root.resolve())
            except ValueError as exc:
                raise _refuse(
                    f"{label} names {relative!r}, which escapes the source root",
                    "SOURCE_PATH_ESCAPE",
                ) from exc
            if not candidate.is_file():
                raise _refuse(
                    f"{label} names {relative!r}, which is ABSENT from the running tree",
                    "SOURCE_ABSENT",
                )
            observed = _sha(candidate.read_bytes())
            if observed != declared:
                raise _refuse(
                    f"{relative} diverges from its published digest "
                    f"(declared {declared[:16]}..., observed {observed[:16]}...)",
                    "SOURCE_DIVERGENT",
                )
            checked += 1
    if checked == 0:
        raise _refuse(
            "no declared digest could be bound to a file: the manifest binds no source",
            "SOURCE_UNBOUND",
        )
    notes.append(f"{checked} declared source/protocol digest(s) bound to bytes on disk")
    return notes


# --------------------------------------------------------------------------------------
# beacon re-verification (defect 1)
# --------------------------------------------------------------------------------------


def _pinned_verifier() -> Path | None:
    override = os.environ.get("ROUTE_E_DRAND_VERIFY")
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [Path(override)] if override else []
    candidates.append(repo_root / "tools" / "drand_verify" / "drand_verify")
    candidates.append(repo_root / "tools" / "drand_verify" / "drand_verify.exe")
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            if _sha(candidate.read_bytes()) in _PINNED_VERIFIER_SHA256:
                return candidate
            return None
    return None


def _reverify_beacon(response: Mapping[str, Any], designated: int) -> bytes:
    """Re-run the pinned cryptographic verifier over the PERSISTED response.

    A1-R2 compared ``response["round"]`` to the designated round and measured the length of
    the randomness.  Neither is cryptography: an attacker who edits the persisted response
    passes both.  Here the signature is checked by the same pinned helper the producer used,
    and an absent or unpinned helper is a STOP, never a pass.
    """
    helper = _pinned_verifier()
    if helper is None:
        raise _refuse(
            "no verifier whose bytes match the pinned digests is available; an absent or "
            "unpinned verifier is a STOP, never a pass",
            "VERIFIER_UNAVAILABLE",
        )
    try:
        return _frame.consume_beacon_round(
            response=dict(response), expected_round=int(designated), helper_path=helper
        )
    except _frame.BeaconUnavailable as exc:
        raise _refuse(f"the beacon is unavailable: {exc}", "BEACON_UNAVAILABLE") from exc
    except _frame.BeaconInvalid as exc:
        raise _refuse(f"the persisted beacon does not verify: {exc}", "BEACON_INVALID") from exc
    except (OSError, ValueError, TypeError) as exc:
        raise _refuse(f"the beacon verifier failed: {exc}", "BEACON_VERIFIER_ERROR") from exc


# --------------------------------------------------------------------------------------
# per-world scientific proof (defect 6, 7, 8, 11)
# --------------------------------------------------------------------------------------


def _verify_world(
    root: Path,
    attempt: Mapping[str, Any],
    *,
    detector,
    tracker,
    sampled_frames: Sequence[int],
) -> WorldOutcome:
    ordinal = int(attempt["attempt_ordinal"])
    law_index = int(attempt["law_index"])
    ic_ordinal = int(attempt["ic_ordinal"])
    status = str(attempt["status"])
    keys = [f"{value:g}" for value in _evidence.COHORT_RESIDUAL_CONVENTIONS]

    if status != "SUCCESS":
        return WorldOutcome(
            attempt_ordinal=ordinal, law_index=law_index, ic_ordinal=ic_ordinal,
            status=status, is_primary=(ic_ordinal == 0), terminal_states=(),
            disposition_by_f={k: "TECHNICALLY_UNKNOWN" for k in keys},
            Y_by_f={k: None for k in keys}, residual_min=None,
            observed_from_first_frame=False,
            recomputed_from="attempt inventory: a technical incident is UNKNOWN, never a silent 0",
        )

    world = root / str(attempt["world_relative_path"])

    measurement_bytes = _p.bounded_read(world / _MEASUREMENT_DOCUMENT_NAME, code="EVIDENCE_MISSING")
    measurement = _p.strict_object(measurement_bytes, "the measurement document", "EVIDENCE_MALFORMED")
    if measurement.get("measurement_root_sha256") != str(attempt.get("measurement_root_sha256")):
        raise _refuse(
            f"world {ordinal}: the inventoried measurement root is not the one on disk",
            "MEASUREMENT_ROOT_MISMATCH",
        )
    binding_bytes = _p.bounded_read(world / _BRIDGE_BINDING_NAME, code="EVIDENCE_MISSING")
    binding = _p.strict_object(binding_bytes, "the bridge binding", "EVIDENCE_MALFORMED")
    if binding.get("measurement_root_sha256") != measurement.get("measurement_root_sha256"):
        raise _refuse(f"world {ordinal}: the bridge binding names another root", "BINDING_MISMATCH")
    if binding.get("measurement_document_sha256") not in (None, _sha(measurement_bytes)):
        raise _refuse(f"world {ordinal}: the bridge binding names another document", "BINDING_MISMATCH")

    lifecycle_bytes = _p.bounded_read(world / _LIFECYCLE_DOCUMENT_NAME, code="EVIDENCE_MISSING")
    if _sha(lifecycle_bytes) != str(attempt.get("lifecycle_document_sha256")):
        raise _refuse(f"world {ordinal}: lifecycle evidence was altered", "EVIDENCE_ALTERED")

    shape = tuple(int(v) for v in measurement["frame_shape"])
    join_bytes = _p.bounded_read(world / _JOIN_NAME, code="JOIN_ABSENT")
    join_document = _p.strict_object(join_bytes, "the join", "JOIN_MALFORMED")
    _p.check_document(join_document, "join", code="JOIN_MALFORMED")

    recomputed_join = _evidence.build_join_document(
        world,
        sampled_frames=sampled_frames,
        frame_shape=shape,
        detector=detector,
        tracker=tracker,
        horizon_steps=int(join_document["horizon_steps"]),
        cadence_steps=int(join_document["cadence_steps"]),
    )
    if _p.canonical_bytes(recomputed_join) != join_bytes:
        raise _refuse(
            f"world {ordinal}: the persisted track/component join is not the one the "
            "persisted frames recompute",
            "JOIN_INCOHERENT",
        )

    evidence = _evidence.derive_world_outcome(
        world, sampled_frames=sampled_frames, frame_shape=shape,
        detector=detector, tracker=tracker,
    )
    residual_min = (
        min(evidence.residual_at_horizon.values()) if evidence.residual_at_horizon else None
    )
    return WorldOutcome(
        attempt_ordinal=ordinal, law_index=law_index, ic_ordinal=ic_ordinal,
        status=status, is_primary=(ic_ordinal == 0),
        terminal_states=evidence.terminal_states,
        disposition_by_f=dict(evidence.disposition_by_f),
        Y_by_f=dict(evidence.Y_by_f),
        residual_min=residual_min,
        observed_from_first_frame=evidence.observed_from_first_frame,
        recomputed_from=(
            "persisted frames: join recomputed and matched, eligibility, horizon and "
            "cohort residual re-derived at each frozen f"
        ),
    )


# --------------------------------------------------------------------------------------
# the entry point
# --------------------------------------------------------------------------------------


def verify_route_e_run(
    output_directory: str | os.PathLike[str],
    final_receipt_path: str | os.PathLike[str] | None = None,
    *,
    source_root: str | os.PathLike[str] | None = None,
) -> AdmissionVerdict:
    """Decide whether ``output_directory`` is admissible Route E evidence.

    Never raises.  Every failure becomes a refusal verdict carrying a reason code.
    """
    root = Path(output_directory)
    notes: list[str] = []
    keys = [f"{value:g}" for value in _evidence.COHORT_RESIDUAL_CONVENTIONS]
    empty_k: dict[str, int | None] = {k: None for k in keys}
    beacon_ok = False
    sources_ok = False
    try:
        if not root.is_dir():
            raise _refuse(f"{root} is not a directory", "NOT_A_DIRECTORY")

        # 1 -- provenance: exact kind, exact key set, exact tag.
        provenance = _p.check_document(
            _p.strict_object(
                _p.bounded_read(root / _PROVENANCE_NAME, code="NOT_A_CANONICAL_ROUTE_E_ROOT"),
                "the provenance", "NOT_A_CANONICAL_ROUTE_E_ROOT",
            ),
            "provenance", code="NOT_A_CANONICAL_ROUTE_E_ROOT",
        )

        # 2 -- no answer written anywhere by the runner.
        for path in sorted(root.rglob("*.json")):
            if path.name in (_LIFECYCLE_DOCUMENT_NAME, _MEASUREMENT_DOCUMENT_NAME):
                continue  # evidence documents: parsed, never trusted
            try:
                candidate = _p.strict_object(path.read_bytes(), path.name, "SCAN")
            except _p.ProtocolRefusal:
                continue
            _p.scan_for_forbidden_fields(
                candidate, where=path.name, code="RUNNER_WROTE_AN_ANSWER"
            )

        # 3 -- manifest: exact schema, then the frozen confirmatory shape.
        manifest_bytes = _p.bounded_read(root / _PRE_RUN_MANIFEST_NAME, code="MANIFEST_UNREADABLE")
        manifest = _p.check_document(
            _p.strict_object(manifest_bytes, "the pre-run manifest", "MANIFEST_UNREADABLE"),
            "manifest", code="MANIFEST_SCHEMA",
        )
        mode = manifest["mode"]
        fixture = manifest["fixture_class"]
        if mode not in ("EXPLORATORY_PILOT", "CONFIRMATORY_67"):
            raise _refuse(f"unknown mode {mode!r}", "MANIFEST_SCHEMA")
        if fixture not in ("SCIENTIFIC", "SYNTHETIC_NON_SCIENTIFIC"):
            raise _refuse(f"unknown fixture class {fixture!r}", "MANIFEST_SCHEMA")
        policy = manifest["sample_size_and_world_policy"]
        if not isinstance(policy, Mapping):
            raise _refuse("sample_size_and_world_policy is not an object", "MANIFEST_SCHEMA")
        try:
            n_draws = int(policy["n_draws"])
            worlds = int(policy["worlds"])
            ics = int(policy.get("initial_conditions_per_law", 2))
        except (KeyError, TypeError, ValueError) as exc:
            raise _refuse(f"the sample-size policy is malformed: {exc}", "MANIFEST_SCHEMA") from exc
        _p.check_confirmatory_constraints(
            mode=str(mode), n_draws=n_draws, worlds=worlds, ics_per_law=ics,
            code="CONFIRMATORY_SHAPE_REFUSED",
        )

        recomputed_p = _sha(_p.PRE_RUN_DOMAIN + _p.canonical_bytes(manifest))
        if provenance.get("pre_run_root") != recomputed_p:
            raise _refuse("the provenance binds a different pre-run root", "PRE_RUN_ROOT_MISMATCH")

        # 4 -- source and protocol digests against the running tree.
        base = Path(source_root) if source_root is not None else Path(__file__).resolve().parents[3]
        notes.extend(_bind_source_digests(manifest, base))
        sources_ok = True

        # 5 -- anteriority: exact schema, typed proof, DERIVED public flag.
        anteriority = _p.check_document(
            _p.strict_object(
                _p.bounded_read(root / _ANTERIORITY_NAME, code="ANTERIORITY_UNREADABLE"),
                "the anteriority proof", "ANTERIORITY_UNREADABLE",
            ),
            "anteriority", code="ANTERIORITY_SCHEMA",
        )
        if anteriority["binds_pre_run_root"] != recomputed_p:
            raise _refuse("the anteriority proof binds another pre-run root", "ANTERIORITY_MISMATCH")
        if anteriority["binds_cutoff_C"] != manifest["canonical_cutoff_C"]:
            raise _refuse("the anteriority proof binds another cutoff", "ANTERIORITY_MISMATCH")
        proof_type, public_inclusion = _p.classify_anteriority_proof(
            anteriority, code="ANTERIORITY_REFUSED"
        )

        # 6 -- round from the cutoff alone, then the beacon re-verified cryptographically.
        try:
            designated = _frame.designated_round(int(manifest["canonical_cutoff_C"]))
        except (TypeError, ValueError) as exc:
            raise _refuse(f"the cutoff does not designate a round: {exc}", "ROUND_UNDERIVABLE") from exc
        beacon = _p.strict_object(
            _p.bounded_read(root / _BEACON_RESPONSE_NAME, code="BEACON_UNREADABLE"),
            "the beacon response", "BEACON_UNREADABLE",
        )
        randomness = _reverify_beacon(beacon, designated)
        beacon_ok = True

        # 7 -- seed, plan, enrolment: recomputed, never read.
        seed_root = _derive_seed_root(recomputed_p, designated, randomness)
        enrolment_document = _p.check_document(
            _p.strict_object(
                _p.bounded_read(root / _ENROLMENT_NAME, code="ENROLMENT_UNREADABLE"),
                "the enrolment", "ENROLMENT_UNREADABLE",
            ),
            "enrolment", code="ENROLMENT_SCHEMA",
        )
        plan = _frame.build_draw_plan(seed_root, count=n_draws)
        if _sha(seed_root) != enrolment_document["seed_root_sha256"]:
            raise _refuse("the recorded seed root is not the one P and the randomness derive", "SEED_MISMATCH")
        if plan.digest() != enrolment_document["draw_plan_digest"]:
            raise _refuse("the recorded draw plan is not the one the seed derives", "PLAN_MISMATCH")
        enrolment = _locks.FamilyEnrolment(
            run_identity=str(manifest["run_identity"]),
            seed_root_sha256=_sha(seed_root),
            draw_plan_digest=plan.digest(),
            n_draws=n_draws,
            worlds=worlds,
        )
        enrolment_digest = _locks.enrolment_digest(enrolment)
        if enrolment_digest != enrolment_document["enrolment_digest"]:
            raise _refuse("the enrolment digest does not match", "ENROLMENT_MISMATCH")
        expected_order = [list(item) for item in plan.world_order[:worlds]]
        if enrolment_document["world_order"] != expected_order:
            raise _refuse("the recorded world order is not the canonical one", "WORLD_ORDER_MISMATCH")

        # 8 -- attempt inventory.
        attempts_bytes = _p.bounded_read(root / _ATTEMPTS_NAME, code="ATTEMPTS_UNREADABLE")
        attempts: list[dict[str, Any]] = []
        for line in attempts_bytes.split(b"\n"):
            if not line:
                continue
            attempts.append(_p.strict_object(line, "an attempt", "ATTEMPTS_MALFORMED"))
        if len(attempts) != worlds:
            raise _refuse(
                f"the attempt inventory holds {len(attempts)} entries for {worlds} worlds",
                "ATTEMPT_INVENTORY_INCOMPLETE",
            )
        for index, attempt in enumerate(attempts):
            for required in ("attempt_ordinal", "law_index", "ic_ordinal", "status", "world_relative_path"):
                if required not in attempt:
                    raise _refuse(f"attempt {index} lacks {required!r}", "ATTEMPTS_MALFORMED")
            if int(attempt["attempt_ordinal"]) != index:
                raise _refuse("the attempt inventory is out of order", "ATTEMPT_ORDER_CHANGED")
            if [int(attempt["law_index"]), int(attempt["ic_ordinal"])] != expected_order[index]:
                raise _refuse("an attempt is not at its canonical position", "ATTEMPT_ORDER_CHANGED")

        # 9 -- file inventory exact.
        inventory_bytes = _p.bounded_read(root / _FILE_INVENTORY_NAME, code="INVENTORY_UNREADABLE")
        inventory = _p.check_document(
            _p.strict_object(inventory_bytes, "the file inventory", "INVENTORY_UNREADABLE"),
            "file_inventory", code="INVENTORY_SCHEMA",
        )
        recorded = {}
        for entry in inventory["entries"]:
            if not isinstance(entry, Mapping) or {"path", "sha256", "bytes"} - set(entry):
                raise _refuse("a file-inventory entry is malformed", "INVENTORY_SCHEMA")
            recorded[str(entry["path"])] = entry
        observed: dict[str, tuple[str, int]] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in _INVENTORY_EXCLUDED:
                continue
            payload = path.read_bytes()
            observed[relative] = (_sha(payload), len(payload))
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
                raise _refuse(f"{relative} does not match its inventoried digest", "FILE_INVENTORY_INEXACT")

        # 10 -- envelope and receipt.
        envelope_bytes = _p.bounded_read(root / _POST_RUN_ENVELOPE_NAME, code="ENVELOPE_UNREADABLE")
        envelope = _p.check_document(
            _p.strict_object(envelope_bytes, "the post-run envelope", "ENVELOPE_UNREADABLE"),
            "envelope", code="ENVELOPE_SCHEMA",
        )
        for field, value in (
            ("pre_run_root", recomputed_p),
            ("file_inventory_sha256", _sha(inventory_bytes)),
            ("seed_root_sha256", _sha(seed_root)),
            ("designated_round", designated),
            ("enrolment_digest", enrolment_digest),
            ("draw_plan_digest", plan.digest()),
            ("anteriority_proof_type", proof_type),
        ):
            if envelope.get(field) != value:
                raise _refuse(f"the envelope binds a different {field}", "ENVELOPE_MISMATCH")
        if envelope.get("attempts") != attempts:
            raise _refuse("the envelope does not bind the attempt inventory on disk", "ENVELOPE_MISMATCH")
        if bool(envelope.get("public_registry_inclusion_proven")) != public_inclusion:
            raise _refuse(
                "the envelope's public-inclusion flag is not the one the proof type derives",
                "ENVELOPE_MISMATCH",
            )
        recomputed_e = _sha(_p.POST_RUN_DOMAIN + _p.canonical_bytes(envelope))
        receipt_path = Path(final_receipt_path) if final_receipt_path is not None else root / _FINAL_RECEIPT_NAME
        receipt = _p.check_document(
            _p.strict_object(
                _p.bounded_read(receipt_path, code="RECEIPT_UNREADABLE"),
                "the final receipt", "RECEIPT_UNREADABLE",
            ),
            "receipt", code="RECEIPT_SCHEMA",
        )
        if receipt["post_run_root"] != recomputed_e:
            raise _refuse("the sealed post-run root is not the one the evidence recomputes", "POST_RUN_ROOT_MISMATCH")
        if receipt["envelope_sha256"] != _sha(envelope_bytes):
            raise _refuse("the receipt binds a different envelope", "RECEIPT_MISMATCH")

        # 11 -- per-world scientific proof, at each frozen f.
        distributions = manifest["distributions_and_draw_algorithm"]
        if not isinstance(distributions, Mapping):
            raise _refuse("distributions_and_draw_algorithm is not an object", "MANIFEST_SCHEMA")
        try:
            horizon = int(distributions["horizon_steps"])
            cadence = int(distributions["cadence_steps"])
        except (KeyError, TypeError, ValueError) as exc:
            raise _refuse(f"the horizon/cadence declaration is malformed: {exc}", "MANIFEST_SCHEMA") from exc
        sampled_frames = tuple(range(0, horizon + 1, cadence))
        spec = MeasurementSpec(min_cells=1)
        outcomes = tuple(
            _verify_world(
                root, attempt, detector=spec.detector_spec(), tracker=spec.tracker_spec(),
                sampled_frames=sampled_frames,
            )
            for attempt in attempts
        )

        # 12 -- the statistical unit.  k is over the 67 PRIMARY units, never 134 worlds.
        primaries = [item for item in outcomes if item.is_primary]
        secondaries = {item.law_index: item for item in outcomes if not item.is_primary}
        if len(primaries) != n_draws:
            raise _refuse(
                f"{len(primaries)} primary units for {n_draws} declared laws",
                "PRIMARY_UNIT_COUNT_WRONG",
            )
        k_by_f: dict[str, int | None] = {}
        psi_by_f: dict[str, float | None] = {}
        unknown_primaries = sum(1 for item in primaries if item.Y_by_f[keys[0]] is None)
        for key in keys:
            values = [item.Y_by_f[key] for item in primaries]
            k_by_f[key] = None if any(v is None for v in values) else sum(int(v) for v in values)
            discordant = 0
            complete = True
            for item in primaries:
                partner = secondaries.get(item.law_index)
                if partner is None or item.Y_by_f[key] is None or partner.Y_by_f[key] is None:
                    complete = False
                    break
                discordant += int(item.Y_by_f[key] != partner.Y_by_f[key])
            psi_by_f[key] = None if not complete else discordant / float(n_draws)

        thresholds_applied = False
        if mode != "CONFIRMATORY_67":
            notes.append("pilot units are never added to the confirmatory k")
        if fixture != "SCIENTIFIC":
            notes.append("a synthetic non-scientific fixture never contributes to any dataset")
        if not public_inclusion:
            notes.append(
                "public pre-run inclusion is NOT proven, so this root may not contribute to "
                "the Route E dataset even though everything else recomputes"
            )
        if unknown_primaries:
            notes.append(
                f"{unknown_primaries} primary unit(s) are technically UNKNOWN; they stay in "
                "the denominator and k is withheld, fail-closed"
            )
        notes.append(
            "the second initial condition contributes to psi only; it is never a replicate, "
            "never a replacement and never a term of k"
        )
        notes.append("the 42 / 9 thresholds are NOT applied by this module under any mode")

        return AdmissionVerdict(
            output_directory=str(root), admissible=True, reason_code="RECOMPUTED",
            reason=(
                "every byte was re-read; P, the source digests, the beacon signature, the "
                "seed, the plan, the enrolment, the inventory, E, the per-world joins and "
                "the per-world outcomes at all three frozen f were recomputed, with no "
                "engine instantiated and no simulation step taken"
            ),
            pre_run_root=recomputed_p, post_run_root=recomputed_e,
            designated_round=designated, seed_root_sha256=_sha(seed_root),
            draw_plan_digest=plan.digest(), enrolment_digest=enrolment_digest,
            mode=str(mode), fixture_class=str(fixture),
            anteriority_proof_type=proof_type,
            public_registry_inclusion_proven=public_inclusion,
            beacon_reverified=beacon_ok, source_bytes_bound=sources_ok,
            engine_steps_taken=0, worlds=outcomes, primary_unit_count=len(primaries),
            k_by_f=k_by_f, psi_by_f=psi_by_f, unknown_primaries=unknown_primaries,
            thresholds_applied=thresholds_applied, contributes_to_k=False,
            notes=tuple(notes),
        )
    except _p.ProtocolRefusal as exc:
        return AdmissionVerdict(
            output_directory=str(root), admissible=False, reason_code=exc.reason_code,
            reason=str(exc), beacon_reverified=beacon_ok, source_bytes_bound=sources_ok,
            engine_steps_taken=0, k_by_f=empty_k, psi_by_f={k: None for k in keys},
            contributes_to_k=False, notes=tuple(notes),
        )
    except Exception as exc:  # noqa: BLE001 - a crash must never look like an authorisation
        return AdmissionVerdict(
            output_directory=str(root), admissible=False,
            reason_code="ADMISSION_INTERNAL_ERROR",
            reason=f"{type(exc).__name__}: {exc}",
            beacon_reverified=beacon_ok, source_bytes_bound=sources_ok,
            engine_steps_taken=0, k_by_f=empty_k, psi_by_f={k: None for k in keys},
            contributes_to_k=False, notes=tuple(notes),
        )


def _derive_seed_root(pre_run_root: str, designated: int, randomness: bytes) -> bytes:
    """Seed derivation, recomputed here rather than imported from the producer."""
    payload = (
        _p.SEED_DOMAIN
        + bytes.fromhex(str(_frame.BEACON_SOURCE["chain_hash"]))
        + int(designated).to_bytes(8, "big")
        + bytes(randomness)
        + bytes.fromhex(pre_run_root)
    )
    return hashlib.sha256(payload).digest()
