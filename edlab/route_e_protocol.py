"""Pure Route E protocol primitives.  A1-R3.

WHY THIS MODULE EXISTS, AND WHERE IT SITS
-----------------------------------------
A1-R2 placed the admission module inside ``edlab.substrates.lattice_bond`` and had it import
``future_route_e_execution``, which imports the engine.  Calling that "independent
verification" was not defensible: the verifier reused the producer's own private helpers.

This module is the smallest defensible separation.  It holds every protocol primitive that
is a pure function of bytes: the canonical encoding, the two domain-separated roots, the
seed derivation, the exact document schemas, the frozen confirmatory constraints, the
anteriority proof-type table, and a genuinely atomic no-clobber write.

It imports NOTHING from ``edlab.substrates`` and NOTHING from ``numpy``.  It cannot reach
the engine even transitively.  ``import edlab.route_e_protocol`` in a virgin interpreter
loads no simulator.  ``tests/test_future_route_e_a1r3_admission.py`` proves this by
inspecting ``sys.modules`` in a fresh subprocess, not by grepping for import statements.

WHAT THIS MODULE DOES *NOT* ESTABLISH
-------------------------------------
It does not make the whole admission engine-free, and no such claim is made.  The frozen
01S obligation 3 says the sampler's acceptance predicate MUST BE the engine's own
``LatticeBondSpec`` construction, so recomputing the draw plan necessarily constructs
``LatticeBondSpec`` objects.  ``LatticeBondSpec`` lives in ``engine.py``.  The two demands
"recompute the plan" and "import no engine" are therefore contradictory by frozen design,
and the contradiction is named here rather than hidden.

The claim that IS made, and that the tests establish at runtime:

    No ``LatticeBondEngine`` is instantiated, no simulation step is taken, and no mutation
    of the output tree occurs during admission.

Nothing is claimed about "the first general effect": reads, imports and the cryptographic
subprocess all exist before any output-tree phase.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from typing import Any, Iterable, Mapping

__all__ = [
    "PROTOCOL_VERSION",
    "PRE_RUN_DOMAIN",
    "POST_RUN_DOMAIN",
    "SEED_DOMAIN",
    "PRE_RUN_KIND",
    "ANTERIORITY_KIND",
    "POST_RUN_KIND",
    "RECEIPT_KIND",
    "PROVENANCE_KIND",
    "ENROLMENT_KIND",
    "FILE_INVENTORY_KIND",
    "JOIN_KIND",
    "ROUTE_E_PROVENANCE_TAG",
    "DOCUMENT_SCHEMAS",
    "CONFIRMATORY_CONSTRAINTS",
    "ANTERIORITY_PROOF_TYPES",
    "FORBIDDEN_RUNNER_FIELDS",
    "ProtocolRefusal",
    "canonical_bytes",
    "sha256_hex",
    "strict_object",
    "check_document",
    "check_confirmatory_constraints",
    "classify_anteriority_proof",
    "scan_for_forbidden_fields",
    "no_clobber_write",
]

PROTOCOL_VERSION = "route-e-protocol/v1"

# Byte-for-byte identical to future_route_e_execution.  A test asserts the equality, so a
# future divergence is a failing test rather than a silent fork of the protocol.
PRE_RUN_DOMAIN = b"EDLAB/ROUTE-E/PRE-RUN/v1\x00"
POST_RUN_DOMAIN = b"EDLAB/ROUTE-E/POST-RUN/v1\x00"
SEED_DOMAIN = b"EDLAB/ROUTE-E/SEED-FROM-PRE-RUN-ROOT/v1\x00"

PRE_RUN_KIND = "route-e-pre-run-manifest/v1"
ANTERIORITY_KIND = "route-e-pre-run-anteriority/v1"
POST_RUN_KIND = "route-e-post-run-envelope/v1"
RECEIPT_KIND = "route-e-final-receipt/v1"
PROVENANCE_KIND = "route-e-provenance/v1"
ENROLMENT_KIND = "route-e-enrolment/v1"
FILE_INVENTORY_KIND = "route-e-file-inventory/v1"
JOIN_KIND = "route-e-track-component-join/v1"

ROUTE_E_PROVENANCE_TAG = "ROUTE_E_CANONICAL_EXECUTION/v1"


class ProtocolRefusal(ValueError):
    """A refusal carrying a reason code.  Never a bare KeyError or ValueError."""

    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


def canonical_bytes(value: Any) -> bytes:
    """The one canonical encoding.  Identical to the producer's, by construction."""
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# --------------------------------------------------------------------------------------
# Document schemas.  EXACT key sets, not "at least these keys".
#
# A1-R2 checked only ``kind`` on two documents and nothing at all on the others, so an
# attacker (or a bug) could add or drop a key freely.  Each entry below is
# (kind, exact key set, tag field name or None, tag value or None).
# --------------------------------------------------------------------------------------

DOCUMENT_SCHEMAS: Mapping[str, Mapping[str, Any]] = {
    "provenance": {
        "kind": PROVENANCE_KIND,
        "keys": frozenset({"execution_version", "kind", "pre_run_root", "tag"}),
        "tag_field": "tag",
        "tag_value": ROUTE_E_PROVENANCE_TAG,
    },
    "manifest": {
        "kind": PRE_RUN_KIND,
        "keys": frozenset(
            {
                "canonical_cutoff_C",
                "crash_retry_and_attempt_policy",
                "designated_round_rule",
                "distributions_and_draw_algorithm",
                "experiment_id",
                "fixture_class",
                "kind",
                "mode",
                "outcome_and_claim_ceiling",
                "output_namespace",
                "protocol_and_analysis_digests",
                "run_identity",
                "sample_size_and_world_policy",
                "schema_version",
                "source_commit_and_digests",
            }
        ),
        "tag_field": None,
        "tag_value": None,
    },
    "anteriority": {
        "kind": ANTERIORITY_KIND,
        "keys": frozenset(
            {
                "binds_cutoff_C",
                "binds_pre_run_root",
                "kind",
                "proof_type",
                "public_registry_inclusion_proven",
            }
        ),
        "tag_field": None,
        "tag_value": None,
    },
    "enrolment": {
        "kind": ENROLMENT_KIND,
        "keys": frozenset(
            {
                "designated_round",
                "draw_plan_digest",
                "enrolment_digest",
                "kind",
                "law_proposal_indices",
                "lattice_sizes",
                "n_draws",
                "proposals_consumed",
                "run_identity",
                "seed_root_sha256",
                "world_order",
                "worlds",
            }
        ),
        "tag_field": None,
        "tag_value": None,
    },
    "file_inventory": {
        "kind": FILE_INVENTORY_KIND,
        "keys": frozenset({"entries", "excluded", "kind"}),
        "tag_field": None,
        "tag_value": None,
    },
    "envelope": {
        "kind": POST_RUN_KIND,
        "keys": frozenset(
            {
                "anteriority_proof_type",
                "anteriority_sha256",
                "attempts",
                "beacon_response_sha256",
                "contributes_to_dataset",
                "designated_round",
                "draw_plan_digest",
                "enrolment_digest",
                "execution_version",
                "file_inventory_sha256",
                "fixture_class",
                "kind",
                "mode",
                "output_namespace",
                "pre_run_manifest_sha256",
                "pre_run_root",
                "provenance_tag",
                "public_registry_inclusion_proven",
                "seed_root_sha256",
                "world_order",
                "worlds_attempted",
                "worlds_failed",
                "worlds_succeeded",
            }
        ),
        "tag_field": "provenance_tag",
        "tag_value": ROUTE_E_PROVENANCE_TAG,
    },
    "receipt": {
        "kind": RECEIPT_KIND,
        "keys": frozenset({"envelope_sha256", "kind", "post_run_root", "pre_run_root"}),
        "tag_field": None,
        "tag_value": None,
    },
    "join": {
        "kind": JOIN_KIND,
        "keys": frozenset(
            {"assignments", "cadence_steps", "horizon_steps", "kind", "sampled_frames"}
        ),
        "tag_field": None,
        "tag_value": None,
    },
}


#: The frozen confirmatory design.  A confirmatory run is 67 primary laws, two initial
#: conditions per law, 134 executed worlds -- and NOTHING ELSE is a confirmatory run.
CONFIRMATORY_CONSTRAINTS: Mapping[str, int] = {
    "n_draws": 67,
    "initial_conditions_per_law": 2,
    "worlds": 134,
}

#: Every proof type the admission recognises, and what each one is allowed to assert.
#: An unknown type is a refusal, never a default.  ``OTS_PLUS_RFC3161`` is the frozen A2
#: rule and stays REFUSED until A2 is implemented and separately reviewed; this module does
#: not implement it and does not modify it.
ANTERIORITY_PROOF_TYPES: Mapping[str, Mapping[str, Any]] = {
    "SELF_ATTESTED_NON_PUBLIC": {
        "public_registry_inclusion_provable": False,
        "implemented": True,
        "note": "a self-attestation proves nothing public; inclusion is forced False",
    },
    "OTS_PLUS_RFC3161": {
        "public_registry_inclusion_provable": True,
        "implemented": False,
        "note": (
            "frozen A2 rule: a COMPLETE OpenTimestamps proof on Bitcoin mainnet AND an "
            "RFC 3161 token from the Sigstore TSA over the canonical bytes of that "
            "complete OTS proof.  Rekor, GitHub, Zenodo and integratedTime replace "
            "neither conjunct.  Not implemented here, therefore refused, never believed."
        ),
    },
}

#: If any persisted document carries one of these the root is refused: the runner may
#: record evidence, never an answer.
FORBIDDEN_RUNNER_FIELDS: frozenset[str] = frozenset(
    {
        "y_i", "y", "k", "successes", "outcome", "outcomes", "verdict", "result",
        "results", "claim", "decision", "significant", "positive", "negative",
    }
)


def strict_object(payload: bytes, label: str, code: str) -> dict[str, Any]:
    """ASCII JSON object in canonical form, or a typed refusal.  Never a bare exception."""
    if not isinstance(payload, (bytes, bytearray)):
        raise ProtocolRefusal(f"{label} is not bytes", reason_code=code)
    try:
        text = bytes(payload).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ProtocolRefusal(f"{label} is not ASCII: {exc}", reason_code=code) from exc
    try:
        value = json.loads(text)
    except ValueError as exc:
        raise ProtocolRefusal(f"{label} is not valid JSON: {exc}", reason_code=code) from exc
    if not isinstance(value, dict):
        raise ProtocolRefusal(f"{label} is not a JSON object", reason_code=code)
    if canonical_bytes(value) != bytes(payload):
        raise ProtocolRefusal(f"{label} is not in canonical form", reason_code=code)
    return value


def check_document(
    document: Mapping[str, Any], schema_name: str, *, code: str
) -> dict[str, Any]:
    """Validate kind, tag and the EXACT key set.  Missing OR extra keys both refuse."""
    schema = DOCUMENT_SCHEMAS.get(schema_name)
    if schema is None:
        raise ProtocolRefusal(f"unknown schema {schema_name!r}", reason_code="SCHEMA_UNKNOWN")
    if not isinstance(document, Mapping):
        raise ProtocolRefusal(f"{schema_name} is not an object", reason_code=code)
    if document.get("kind") != schema["kind"]:
        raise ProtocolRefusal(
            f"{schema_name} has kind {document.get('kind')!r}, expected {schema['kind']!r}",
            reason_code=code,
        )
    observed = frozenset(document.keys())
    expected = schema["keys"]
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise ProtocolRefusal(
            f"{schema_name} key set is wrong: missing={missing} extra={extra}",
            reason_code=code,
        )
    tag_field = schema["tag_field"]
    if tag_field is not None and document.get(tag_field) != schema["tag_value"]:
        raise ProtocolRefusal(
            f"{schema_name} carries the wrong {tag_field}: {document.get(tag_field)!r}",
            reason_code=code,
        )
    return dict(document)


def check_confirmatory_constraints(
    *, mode: str, n_draws: Any, worlds: Any, ics_per_law: Any, code: str
) -> None:
    """A confirmatory run is 67 / 2 / 134.  Any other shape is refused, not scaled."""
    for name, value in (("n_draws", n_draws), ("worlds", worlds), ("ics_per_law", ics_per_law)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ProtocolRefusal(
                f"{name} must be a positive plain int, got {value!r}", reason_code=code
            )
    if int(worlds) != int(n_draws) * int(ics_per_law):
        raise ProtocolRefusal(
            f"worlds={worlds} is not n_draws={n_draws} times ics_per_law={ics_per_law}",
            reason_code=code,
        )
    if mode != "CONFIRMATORY_67":
        return
    for name, expected in (
        ("n_draws", CONFIRMATORY_CONSTRAINTS["n_draws"]),
        ("worlds", CONFIRMATORY_CONSTRAINTS["worlds"]),
        ("ics_per_law", CONFIRMATORY_CONSTRAINTS["initial_conditions_per_law"]),
    ):
        observed = {"n_draws": n_draws, "worlds": worlds, "ics_per_law": ics_per_law}[name]
        if int(observed) != expected:
            raise ProtocolRefusal(
                f"a confirmatory run is frozen at {name}={expected}; this root declares "
                f"{name}={observed}.  The frozen design is never rescaled to fit a run.",
                reason_code=code,
            )


def classify_anteriority_proof(
    proof: Mapping[str, Any], *, code: str
) -> tuple[str, bool]:
    """Return (proof_type, public_registry_inclusion_proven).

    The boolean is DERIVED from the proof type, never read from the document.  A document
    that claims public inclusion under a type that cannot prove it is refused rather than
    downgraded, because a false claim is evidence of tampering, not of sloppiness.
    """
    proof_type = proof.get("proof_type")
    if not isinstance(proof_type, str):
        raise ProtocolRefusal("proof_type is not a string", reason_code=code)
    entry = ANTERIORITY_PROOF_TYPES.get(proof_type)
    if entry is None:
        raise ProtocolRefusal(
            f"unknown anteriority proof type {proof_type!r}; an unknown type is refused, "
            "never treated as a weaker known one",
            reason_code=code,
        )
    claimed = proof.get("public_registry_inclusion_proven")
    if not isinstance(claimed, bool):
        raise ProtocolRefusal(
            "public_registry_inclusion_proven must be a JSON boolean", reason_code=code
        )
    if not entry["implemented"]:
        raise ProtocolRefusal(
            f"{proof_type} is recognised but NOT implemented: {entry['note']}",
            reason_code=code,
        )
    derived = bool(entry["public_registry_inclusion_provable"])
    if claimed and not derived:
        raise ProtocolRefusal(
            f"the document claims public registry inclusion under {proof_type!r}, which "
            "cannot prove it.  A boolean written by the producer is never believed.",
            reason_code=code,
        )
    return proof_type, derived


def scan_for_forbidden_fields(document: Any, *, where: str, code: str) -> None:
    """Refuse any answer-shaped key at any depth."""
    stack: list[Any] = [document]
    while stack:
        item = stack.pop()
        if isinstance(item, Mapping):
            for key, sub in item.items():
                if isinstance(key, str) and key.lower() in FORBIDDEN_RUNNER_FIELDS:
                    raise ProtocolRefusal(
                        f"{where} carries the field {key!r}: the runner may record "
                        "evidence, never an answer",
                        reason_code=code,
                    )
                stack.append(sub)
        elif isinstance(item, (list, tuple)):
            stack.extend(item)


def no_clobber_write(path: str | os.PathLike[str], payload: bytes) -> str:
    """Genuinely atomic first-write-wins.  Returns the sha256 of the bytes written.

    A1-R2 used ``if path.exists(): refuse`` followed by ``os.replace``.  Two concurrent
    runs under the same namespace both pass ``exists()`` and the second ``os.replace``
    silently overwrites the first, because ``os.replace`` is atomic but NOT exclusive.
    The window is real and the loser is destroyed without a trace.

    ``O_CREAT | O_EXCL`` closes it: the kernel performs existence-check-and-create as one
    operation, so exactly one writer can win, and the loser gets ``FileExistsError``.  The
    payload is written into the final inode, so there is no rename step to race on.
    """
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):  # Windows
        flags |= os.O_BINARY  # pragma: no cover - platform dependent
    handle = os.open(os.fspath(path), flags, 0o644)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.unlink(os.fspath(path))
        except OSError:
            pass
        raise
    return sha256_hex(payload)


def bounded_read(path: str | os.PathLike[str], *, code: str, limit: int = 8_388_608) -> bytes:
    """Read a regular file under a bounded size, or refuse with a code."""
    try:
        info = os.stat(os.fspath(path))
    except OSError as exc:
        raise ProtocolRefusal(f"{path} cannot be read: {exc}", reason_code=code) from exc
    if not os.path.isfile(os.fspath(path)):
        raise ProtocolRefusal(f"{path} is not a regular file", reason_code=code)
    if info.st_size > limit:
        raise ProtocolRefusal(f"{path} exceeds the bounded size", reason_code=code)
    try:
        with open(os.fspath(path), "rb") as stream:
            return stream.read()
    except OSError as exc:  # pragma: no cover - defensive
        raise ProtocolRefusal(f"{path} cannot be read: {exc}", reason_code=code) from exc
