"""The single canonical Route E execution entry point.

WHY THIS MODULE EXISTS
----------------------
The previous strategy added an OPTIONAL ``route_e`` parameter to five generic functions.
That strategy is RETIRED.  It could not work, and the reason is architectural rather than
accidental: an optional keyword-only parameter is a *caller self-declaration*.  Nothing in
``run_directory``, ``tracking`` or ``sampled_frames`` lets a generic function tell a Route E
intent from any other, and ``future_prospective_measurement_bridge.run_measurement_bridge``
runs the engine and persists frames BEFORE it calls the owned pipeline, so a guard placed in
the owned pipeline would fire after the fact -- when it fired at all.

THE AUTHORITATIVE PROPERTY
--------------------------
This module does NOT claim that nobody can call ``LatticeBondEngine``, copy the code or run
an exploratory simulation.  That claim is explicitly abandoned.  What it establishes is:

    No artefact contributes to the Route E dataset, to any ``Y_i`` or to ``k`` unless it
    satisfies, in full, the pre-run manifest, the enrolment, the beacon, the attempt
    inventory and the independent verification.

Admissibility is decided by :mod:`future_route_e_admission`, which re-reads every byte from
disk, recomputes everything, runs no engine step, and refuses anything that does not carry
the provenance this module writes.  A generic bridge run, a Stage-B run, a historical
five-function run and a direct engine call are all *inadmissible* -- not impossible.

TOPOLOGY
--------
``run_route_e`` sits ABOVE the existing bridge.  The bridge stays a generic internal
component and is not modified.  Nothing here is added to ``lifecycle.py``,
``future_lifecycle_runner.py``, ``future_lifecycle_owned_pipeline.py``, ``stage_b.py`` or
``stage_b_reproduce.py``.

PRE-RUN AND POST-RUN ARE DIFFERENT OBJECTS
------------------------------------------
``P`` is the pre-run root.  It binds only what must exist BEFORE the cutoff ``C``: identity,
namespace, sources, protocol, distributions, sample size, claim ceiling, attempt policy,
``C`` itself and the rule that derives the round from ``C``.  It may not contain a seed, a
draw plan, a law, an initial condition, a measurement root, a join digest, a ``Y_i``, a
``k``, an outcome or a result.  The loader refuses such a key anywhere in the document.

``E`` is the post-run root.  It binds ``P``, the anteriority proof, the verified beacon, the
seed root, the full draw plan and enrolment, the source snapshot, the world order, EVERY
attempt including crashes and invalidities, the per-world measurement roots, the
track/component joins and the exact file inventory.  ``E`` is computed after the run and can
never take part in choosing the beacon.

The two roots use DIFFERENT domain separation tags and DIFFERENT ``kind`` strings, so a
pre-run document can never be presented as a post-run one, or the reverse.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from . import future_route_e_pre_run_frame as _frame
from . import future_route_e_pre_run_locks as _locks
from .engine import LatticeBondSpec, LatticeBondState
from .future_prospective_measurement_bridge import (
    BridgeError,
    MeasurementSpec,
    run_measurement_bridge,
)

__all__ = [
    "EXECUTION_VERSION",
    "PRE_RUN_KIND",
    "POST_RUN_KIND",
    "PRE_RUN_DOMAIN",
    "POST_RUN_DOMAIN",
    "ROUTE_E_PROVENANCE_TAG",
    "PROVENANCE_NAME",
    "PRE_RUN_MANIFEST_NAME",
    "ANTERIORITY_NAME",
    "BEACON_RESPONSE_NAME",
    "ENROLMENT_NAME",
    "ATTEMPTS_NAME",
    "FILE_INVENTORY_NAME",
    "POST_RUN_ENVELOPE_NAME",
    "FINAL_RECEIPT_NAME",
    "WORLDS_DIRECTORY",
    "JOIN_EVIDENCE_NAME",
    "POST_RUN_ONLY_KEYS",
    "REQUIRED_MANIFEST_KEYS",
    "DESIGNATED_ROUND_RULE",
    "PINNED_VERIFIER_SHA256",
    "EXECUTION_PHASES",
    "FIRST_EFFECT_PHASE",
    "RouteEExecutionRefused",
    "RouteEExecutionWaiting",
    "RouteERunRecord",
    "canonical_bytes",
    "pre_run_root",
    "post_run_root",
    "derive_route_e_seed_root",
    "run_route_e",
]

EXECUTION_VERSION = "future-route-e-execution/v1"

#: Domain separation.  The two roots are computed over DIFFERENT prefixes, so the same
#: byte string can never hash to both a pre-run and a post-run root.
PRE_RUN_DOMAIN = b"EDLAB/ROUTE-E/PRE-RUN/v1\x00"
POST_RUN_DOMAIN = b"EDLAB/ROUTE-E/POST-RUN/v1\x00"
SEED_DOMAIN = b"EDLAB/ROUTE-E/SEED-FROM-PRE-RUN-ROOT/v1\x00"

PRE_RUN_KIND = "route-e-pre-run-manifest/v1"
ANTERIORITY_KIND = "route-e-pre-run-anteriority/v1"
POST_RUN_KIND = "route-e-post-run-envelope/v1"
RECEIPT_KIND = "route-e-final-receipt/v1"

#: Written into every canonical output root.  The generic bridge, Stage-B, the historical
#: reproducer and the five historical functions never write it, which is exactly why their
#: outputs are inadmissible for Route E.
ROUTE_E_PROVENANCE_TAG = "ROUTE_E_CANONICAL_EXECUTION/v1"

PROVENANCE_NAME = "ROUTE_E_PROVENANCE.json"
PRE_RUN_MANIFEST_NAME = "PRE_RUN_MANIFEST.json"
ANTERIORITY_NAME = "PRE_RUN_ANTERIORITY.json"
BEACON_RESPONSE_NAME = "BEACON_RESPONSE.json"
ENROLMENT_NAME = "ENROLMENT.json"
ATTEMPTS_NAME = "ATTEMPTS.jsonl"
FILE_INVENTORY_NAME = "FILE_INVENTORY.json"
POST_RUN_ENVELOPE_NAME = "POST_RUN_ENVELOPE.json"
FINAL_RECEIPT_NAME = "FINAL_RECEIPT.json"
WORLDS_DIRECTORY = "worlds"
JOIN_EVIDENCE_NAME = "TRACK_COMPONENT_JOIN.json"

#: Files written AFTER the inventory, therefore deliberately outside it.  There is no
#: cycle: inventory -> envelope -> receipt, each binding only what precedes it.
_INVENTORY_EXCLUDED = (FILE_INVENTORY_NAME, POST_RUN_ENVELOPE_NAME, FINAL_RECEIPT_NAME)

#: A pre-run manifest that carries any of these -- at any depth, as a key or as a whole
#: string value -- is refused.  This is what keeps ``P`` free of post-run information.
POST_RUN_ONLY_KEYS: frozenset[str] = frozenset(
    {
        "seed",
        "seed_root",
        "seed_root_sha256",
        "draw_plan",
        "draw_plan_digest",
        "law_draw",
        "law_fields",
        "laws",
        "initial_condition",
        "initial_conditions",
        "ic_indices",
        "measurement_root",
        "measurement_root_sha256",
        "join",
        "join_digest",
        "track_component_join_digest",
        "randomness",
        "signature",
        "beacon_response",
        "round",
        "beacon_round",
        "y_i",
        "y",
        "k",
        "successes",
        "outcome",
        "outcomes",
        "result",
        "results",
        "verdict",
        "route_e_root",
        "enrolment",
        "enrolment_digest",
        "post_run_root",
        "attempts",
        "world_order",
    }
)

REQUIRED_MANIFEST_KEYS: tuple[str, ...] = (
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
)

MODES: tuple[str, ...] = ("EXPLORATORY_PILOT", "CONFIRMATORY_67")
FIXTURE_CLASSES: tuple[str, ...] = ("SCIENTIFIC", "SYNTHETIC_NON_SCIENTIFIC")
SYNTHETIC_NAMESPACE_PREFIX = "SYNTHETIC-NONSCI-"

#: The ONLY round rule this module accepts.  The round is a function of ``C`` alone.
DESIGNATED_ROUND_RULE: Mapping[str, Any] = {
    "chain": "quicknet",
    "rule": "beacon_round_at_or_after(canonical_cutoff_C + delay_seconds)",
    "delay_seconds": 86400,
}

#: The verifier LOCATION may be supplied by the environment, but its BYTES are pinned.
#: A caller who points the environment at another binary gets a refusal, so the location
#: is not an injection point.
PINNED_VERIFIER_SHA256: Mapping[str, str] = {
    "linux-amd64": "2534fa4af5ed6d6d4294be26542b52fe7445412532db97e66a955cacba3cca6d",
    "windows-amd64": "ea15b5de9f88a6fd0557e1912c31493670f9322bc901d8841b6868cd3220045c",
}

#: The frozen order.  Nothing touches the filesystem before ``CREATE_OUTPUT_ROOT``.
EXECUTION_PHASES: tuple[str, ...] = (
    "READ_AND_CANONICALISE_BUNDLE",
    "RECOMPUTE_PRE_RUN_ROOT",
    "VERIFY_ANTERIORITY",
    "DERIVE_ROUND_FROM_CUTOFF",
    "VERIFY_BEACON",
    "DERIVE_SEED_PLAN_ENROLMENT",
    "CHECK_NAMESPACE_FIRST_WRITE_WINS",
    "CREATE_OUTPUT_ROOT",
    "EXECUTE_WORLDS",
    "RECORD_ATTEMPTS",
    "SEAL_ENVELOPE",
)

#: The first phase allowed to mutate anything outside memory.
FIRST_EFFECT_PHASE = "CREATE_OUTPUT_ROOT"
_PHASE_INDEX = {name: index for index, name in enumerate(EXECUTION_PHASES)}
_FIRST_EFFECT_INDEX = _PHASE_INDEX[FIRST_EFFECT_PHASE]


class RouteEExecutionRefused(RuntimeError):
    """STOP.  The run is refused; nothing was written unless ``effects_started`` is True."""

    def __init__(self, message: str, *, phase: str, effects_started: bool = False) -> None:
        super().__init__(f"[{phase}] {message}")
        self.phase = phase
        self.effects_started = effects_started
        self.disposition = "STOP"


class RouteEExecutionWaiting(RuntimeError):
    """WAIT on the SAME round.  Never the next round, never another source."""

    def __init__(self, message: str, *, phase: str) -> None:
        super().__init__(f"[{phase}] {message}")
        self.phase = phase
        self.effects_started = False
        self.disposition = "WAIT"


def canonical_bytes(value: Any) -> bytes:
    """The one canonical encoding used by both roots and by the admission module."""
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def pre_run_root(manifest: Mapping[str, Any]) -> str:
    """``P``.  Domain-separated; a post-run envelope can never produce this digest."""
    return _sha256_hex(PRE_RUN_DOMAIN + canonical_bytes(manifest))


def post_run_root(envelope: Mapping[str, Any]) -> str:
    """``E``.  Domain-separated; a pre-run manifest can never produce this digest."""
    return _sha256_hex(POST_RUN_DOMAIN + canonical_bytes(envelope))


def derive_route_e_seed_root(
    *, pre_run_root_sha256: str, beacon_round: int, beacon_randomness: bytes
) -> bytes:
    """Seed derivation by domain separation from ``P`` and the VERIFIED randomness.

    This is deliberately NOT :func:`future_route_e_pre_run_frame.derive_seed_root`, which
    binds a preregistration commit hash.  Binding ``P`` instead is precisely the correction
    this mission makes: the object that must pre-exist the cutoff is the pre-run manifest,
    not a commit, and it is the manifest whose anteriority is proved.

    There is no caller-supplied seed anywhere in this module: the only inputs are ``P``,
    the round the cutoff designates, and the randomness the pinned verifier accepted.
    """
    if not isinstance(pre_run_root_sha256, str) or len(pre_run_root_sha256) != 64:
        raise ValueError("pre_run_root_sha256 must be 64 hex characters")
    if isinstance(beacon_round, bool) or not isinstance(beacon_round, int) or beacon_round <= 0:
        raise ValueError("beacon_round must be a positive plain int")
    if not isinstance(beacon_randomness, (bytes, bytearray)) or len(beacon_randomness) != 32:
        raise ValueError("beacon_randomness must be exactly 32 bytes")
    payload = (
        SEED_DOMAIN
        + bytes.fromhex(str(_frame.BEACON_SOURCE["chain_hash"]))
        + int(beacon_round).to_bytes(8, "big")
        + bytes(beacon_randomness)
        + bytes.fromhex(pre_run_root_sha256)
    )
    return hashlib.sha256(payload).digest()


@dataclass(frozen=True)
class RouteERunRecord:
    """Inert description of one canonical Route E run.  Holding it grants nothing.

    In particular it carries no ``Y_i``, no ``k`` and no verdict: those are recomputed
    from the persisted evidence by :mod:`future_route_e_admission`, never taken from here.
    """

    output_directory: str
    pre_run_root: str
    post_run_root: str
    designated_round: int
    seed_root_sha256: str
    draw_plan_digest: str
    enrolment_digest: str
    worlds_attempted: int
    worlds_succeeded: int
    worlds_failed: int
    file_inventory_sha256: str
    public_registry_inclusion_proven: bool
    contributes_to_dataset: bool


# --------------------------------------------------------------------------------------
# reading, with no filesystem mutation whatsoever
# --------------------------------------------------------------------------------------


def _read_exact(path: Path, phase: str, label: str, limit: int = 4_194_304) -> bytes:
    if not path.is_file():
        raise RouteEExecutionRefused(f"{label} is absent at {path}", phase=phase)
    size = path.stat().st_size
    if size > limit:
        raise RouteEExecutionRefused(f"{label} exceeds the bounded size", phase=phase)
    return path.read_bytes()


def _strict_object(payload: bytes, phase: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RouteEExecutionRefused(f"{label} is not ASCII JSON: {exc}", phase=phase) from exc
    if not isinstance(value, dict):
        raise RouteEExecutionRefused(f"{label} is not a JSON object", phase=phase)
    if canonical_bytes(value) != payload:
        raise RouteEExecutionRefused(
            f"{label} is not in canonical form; the bytes on disk must be exactly the "
            "canonical encoding, otherwise two byte strings could share one root",
            phase=phase,
        )
    return value


def _reject_post_run_keys(value: Any, phase: str, trail: str = "") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise RouteEExecutionRefused("manifest keys must be strings", phase=phase)
            if key.lower() in POST_RUN_ONLY_KEYS:
                raise RouteEExecutionRefused(
                    f"the pre-run manifest carries the post-run key {trail}/{key!r}; a "
                    "pre-run root may never contain a seed, a plan, a draw, a measurement, "
                    "a join, an outcome or a result",
                    phase=phase,
                )
            _reject_post_run_keys(item, phase, f"{trail}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_post_run_keys(item, phase, f"{trail}[{index}]")
    elif isinstance(value, str) and value.lower() in POST_RUN_ONLY_KEYS:
        raise RouteEExecutionRefused(
            f"the pre-run manifest names the post-run quantity {value!r} at {trail}",
            phase=phase,
        )


def _require(condition: bool, message: str, phase: str) -> None:
    if not condition:
        raise RouteEExecutionRefused(message, phase=phase)


def _validated_manifest(payload: bytes) -> dict[str, Any]:
    phase = "READ_AND_CANONICALISE_BUNDLE"
    manifest = _strict_object(payload, phase, "the pre-run manifest")
    _require(
        manifest.get("kind") == PRE_RUN_KIND,
        f"the pre-run manifest must declare kind {PRE_RUN_KIND!r}; a post-run envelope "
        "carries a different kind and can never be substituted",
        phase,
    )
    _require(
        manifest.get("schema_version") == EXECUTION_VERSION,
        "the pre-run manifest declares an unknown schema version",
        phase,
    )
    missing = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    _require(not missing, f"the pre-run manifest is missing {missing}", phase)
    extra = [key for key in manifest if key not in REQUIRED_MANIFEST_KEYS]
    _require(not extra, f"the pre-run manifest carries unknown keys {extra}", phase)
    _reject_post_run_keys(
        {key: value for key, value in manifest.items() if key != "kind"}, phase
    )

    mode = manifest["mode"]
    _require(mode in MODES, f"mode must be one of {MODES}", phase)
    fixture = manifest["fixture_class"]
    _require(fixture in FIXTURE_CLASSES, f"fixture_class must be one of {FIXTURE_CLASSES}", phase)
    namespace = manifest["output_namespace"]
    _require(
        isinstance(namespace, str) and 8 <= len(namespace) <= 128,
        "output_namespace must be a string of 8 to 128 characters",
        phase,
    )
    if fixture == "SYNTHETIC_NON_SCIENTIFIC":
        _require(
            namespace.startswith(SYNTHETIC_NAMESPACE_PREFIX),
            "a synthetic non-scientific fixture must use a namespace beginning with "
            f"{SYNTHETIC_NAMESPACE_PREFIX!r}, so it can never be mistaken for a real one",
            phase,
        )
    else:
        _require(
            not namespace.startswith(SYNTHETIC_NAMESPACE_PREFIX),
            "a scientific run may not borrow the synthetic namespace prefix",
            phase,
        )

    cutoff = manifest["canonical_cutoff_C"]
    _require(
        not isinstance(cutoff, bool) and isinstance(cutoff, int) and cutoff > 0,
        "canonical_cutoff_C must be a positive plain int",
        phase,
    )
    _require(
        manifest["designated_round_rule"] == dict(DESIGNATED_ROUND_RULE),
        "designated_round_rule must be exactly the pinned rule; the round is a function "
        "of the cutoff alone and is never negotiated",
        phase,
    )

    distributions = manifest["distributions_and_draw_algorithm"]
    _require(isinstance(distributions, dict), "distributions_and_draw_algorithm must be an object", phase)
    for key in ("generator", "lattice_sizes", "horizon_steps", "cadence_steps"):
        _require(key in distributions, f"distributions_and_draw_algorithm needs {key!r}", phase)
    _require(
        distributions["generator"] == _frame.DRAW_GENERATOR["algorithm"],
        "the draw generator is frozen and may not be replaced",
        phase,
    )
    _require(
        list(distributions["lattice_sizes"]) == list(_frame.LATTICE_SIZES),
        "the lattice size set is frozen",
        phase,
    )

    policy = manifest["sample_size_and_world_policy"]
    _require(isinstance(policy, dict), "sample_size_and_world_policy must be an object", phase)
    for key in ("n_draws", "worlds", "initial_conditions_per_law", "world_order_rule"):
        _require(key in policy, f"sample_size_and_world_policy needs {key!r}", phase)
    n_draws = policy["n_draws"]
    worlds = policy["worlds"]
    for name, value in (("n_draws", n_draws), ("worlds", worlds)):
        _require(
            not isinstance(value, bool) and isinstance(value, int) and value > 0,
            f"{name} must be a positive plain int",
            phase,
        )
    _require(
        policy["initial_conditions_per_law"] == _frame.INITIAL_CONDITIONS_PER_LAW,
        "the number of initial conditions per law is frozen",
        phase,
    )
    _require(
        policy["world_order_rule"] == _frame.CANONICAL_DRAW_ORDER[3],
        "the world order rule is frozen and quoted literally",
        phase,
    )
    _require(
        worlds <= n_draws * _frame.INITIAL_CONDITIONS_PER_LAW,
        "worlds may not exceed the number the draw plan can produce",
        phase,
    )

    ceiling = manifest["outcome_and_claim_ceiling"]
    _require(isinstance(ceiling, dict), "outcome_and_claim_ceiling must be an object", phase)
    for key in ("estimand", "positive_min_k", "negative_max_k", "claim_template"):
        _require(key in ceiling, f"outcome_and_claim_ceiling needs {key!r}", phase)
    _require(
        ceiling["positive_min_k"] == _frame.POSITIVE_MIN_K
        and ceiling["negative_max_k"] == _frame.NEGATIVE_MAX_K,
        "the decision thresholds are frozen",
        phase,
    )

    attempts = manifest["crash_retry_and_attempt_policy"]
    _require(isinstance(attempts, dict), "crash_retry_and_attempt_policy must be an object", phase)
    for key in ("retries_allowed", "replacement_allowed", "attempt_inventory_required"):
        _require(key in attempts, f"crash_retry_and_attempt_policy needs {key!r}", phase)
    _require(attempts["retries_allowed"] == 0, "retries are not permitted", phase)
    _require(attempts["replacement_allowed"] is False, "replacement is not permitted", phase)
    _require(
        attempts["attempt_inventory_required"] is True,
        "the attempt inventory is mandatory",
        phase,
    )

    if mode == "CONFIRMATORY_67":
        _require(fixture == "SCIENTIFIC", "a confirmatory run may not be synthetic", phase)
        _require(
            n_draws == _frame.N_LAW_DRAWS and worlds == _frame.WORLD_COUNT,
            "a confirmatory run is frozen at 67 draws and 134 worlds",
            phase,
        )
        _require(
            distributions["horizon_steps"] == _frame.HORIZON_STEPS
            and distributions["cadence_steps"] == _frame.CADENCE_STEPS,
            "a confirmatory run is frozen at the declared horizon and cadence",
            phase,
        )

    sources = manifest["source_commit_and_digests"]
    _require(isinstance(sources, dict), "source_commit_and_digests must be an object", phase)
    _require("commit_sha1" in sources and "digests" in sources, "source binding is incomplete", phase)
    _require(
        isinstance(sources["commit_sha1"], str) and len(sources["commit_sha1"]) == 40,
        "commit_sha1 must be 40 hex characters",
        phase,
    )
    _require(isinstance(sources["digests"], dict) and sources["digests"], "digests must be a non-empty object", phase)
    _require(
        isinstance(manifest["protocol_and_analysis_digests"], dict)
        and manifest["protocol_and_analysis_digests"],
        "protocol_and_analysis_digests must be a non-empty object",
        phase,
    )
    _require(
        isinstance(manifest["experiment_id"], str) and manifest["experiment_id"],
        "experiment_id must be a non-empty string",
        phase,
    )
    _require(
        isinstance(manifest["run_identity"], str) and 8 <= len(manifest["run_identity"]) <= 128,
        "run_identity must be a string of 8 to 128 characters",
        phase,
    )
    return manifest


def _validated_anteriority(payload: bytes, root: str, cutoff: int) -> tuple[dict[str, Any], bool]:
    """Structural verification of the anteriority proof.  Returns (proof, public?)."""
    phase = "VERIFY_ANTERIORITY"
    proof = _strict_object(payload, phase, "the anteriority proof")
    _require(proof.get("kind") == ANTERIORITY_KIND, "the anteriority proof has the wrong kind", phase)
    for key in ("binds_pre_run_root", "binds_cutoff_C", "proof_type", "public_registry_inclusion_proven"):
        _require(key in proof, f"the anteriority proof needs {key!r}", phase)
    _require(
        proof["binds_pre_run_root"] == root,
        "the anteriority proof binds a DIFFERENT pre-run root than the manifest supplied; "
        "a valid proof of another manifest is not a proof of this one",
        phase,
    )
    _require(
        proof["binds_cutoff_C"] == cutoff,
        "the anteriority proof binds a different cutoff than the manifest declares",
        phase,
    )

    proof_type = proof["proof_type"]
    if proof_type == "OTS_PLUS_RFC3161":
        raise RouteEExecutionRefused(
            "the frozen A2 decision is 'complete OpenTimestamps proof AND an RFC 3161 "
            "token over its canonical encoding'.  That verifier is NOT implemented in "
            "this mission, so a run claiming it is refused rather than believed.",
            phase=phase,
        )
    if proof_type == "SELF_ATTESTED_NON_PUBLIC":
        _require(
            proof["public_registry_inclusion_proven"] is False,
            "a self-attested proof may never claim public registry inclusion",
            phase,
        )
        return proof, False
    raise RouteEExecutionRefused(f"unknown anteriority proof type {proof_type!r}", phase=phase)


def _pinned_verifier() -> Path | None:
    """Locate the helper, then PIN ITS BYTES.  A wrong binary is not a verifier."""
    override = os.environ.get("ROUTE_E_DRAND_VERIFY")
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [Path(override)] if override else []
    candidates.append(repo_root / "tools" / "drand_verify" / "drand_verify")
    candidates.append(repo_root / "tools" / "drand_verify" / "drand_verify.exe")
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            digest = _sha256_hex(candidate.read_bytes())
            if digest in set(PINNED_VERIFIER_SHA256.values()):
                return candidate
            return None
    return None


# --------------------------------------------------------------------------------------
# writing, only ever after the whole verification succeeded
# --------------------------------------------------------------------------------------


def _write_exact(path: Path, payload: bytes) -> str:
    """Non-overwriting durable write.  Returns the sha256 of the bytes written."""
    if path.exists():
        raise RouteEExecutionRefused(
            f"{path.name} already exists; nothing is ever replaced", phase="SEAL_ENVELOPE",
            effects_started=True,
        )
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=".partial-")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return _sha256_hex(payload)


def _law_spec_from_fields(fields: Mapping[str, float]) -> LatticeBondSpec:
    accepted = {name for name in LatticeBondSpec.__dataclass_fields__}
    return LatticeBondSpec(**{k: float(v) for k, v in fields.items() if k in accepted})


def _initial_state(seed_root: bytes, ic_index: int, size: int) -> LatticeBondState:
    """The initial condition of one world, derived from the seed root alone."""
    cells = size * size
    matter = np.empty(cells, dtype=np.float64)
    produced = 0
    block_index = ic_index * 1_000_000
    while produced < cells:
        block = _frame.draw_block(seed_root, b"IC", block_index)
        block_index += 1
        for offset in range(0, 32, 4):
            if produced == cells:
                break
            word = int.from_bytes(block[offset : offset + 4], "big")
            matter[produced] = word / float(1 << 32)
            produced += 1
    grid = matter.reshape((size, size))
    return LatticeBondState(
        grid,
        np.full((size, size), 0.8, dtype=np.float64),
        np.zeros((2, size, size), dtype=np.float64),
        0,
    )


def _schedule(horizon: int, cadence: int) -> tuple[int, ...]:
    return tuple(range(0, horizon + 1, cadence))


def _inventory(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in _INVENTORY_EXCLUDED:
            continue
        payload = path.read_bytes()
        entries.append(
            {"path": relative, "sha256": _sha256_hex(payload), "bytes": len(payload)}
        )
    return entries


def run_route_e(
    pre_run_bundle_path: str | os.PathLike[str],
    beacon_response_path: str | os.PathLike[str],
    output_directory: str | os.PathLike[str],
) -> RouteERunRecord:
    """The single supported Route E execution entry point.

    It accepts NO verification callback, NO authorisation boolean, NO law, NO initial
    condition, NO seed, NO round, NO root, NO tracking and NO outcome.  Everything it
    needs is derived, in this order, and every phase before ``CREATE_OUTPUT_ROOT``
    is pure: it reads, hashes and computes, and touches nothing.

    The valid path returns a :class:`RouteERunRecord`.  There is no terminal
    ``raise "unreachable"`` and no global boolean anyone has to flip later.
    """
    bundle = Path(pre_run_bundle_path)
    beacon_path = Path(beacon_response_path)
    destination = Path(output_directory)

    # 1 -- read and canonicalise the bundle.  Pure.
    phase = "READ_AND_CANONICALISE_BUNDLE"
    _require(bundle.is_dir(), f"the pre-run bundle is not a directory: {bundle}", phase)
    manifest_bytes = _read_exact(bundle / PRE_RUN_MANIFEST_NAME, phase, "the pre-run manifest")
    anteriority_bytes = _read_exact(bundle / ANTERIORITY_NAME, phase, "the anteriority proof")
    manifest = _validated_manifest(manifest_bytes)

    # 2 -- recompute P from the bytes that were read back.  Pure.
    root = pre_run_root(manifest)

    # 3 -- verify the anteriority of P against C.  Pure.
    cutoff = int(manifest["canonical_cutoff_C"])
    proof, public_inclusion = _validated_anteriority(anteriority_bytes, root, cutoff)

    # 4 -- derive the round from C ALONE.  Pure.  No proof timestamp takes part.
    phase = "DERIVE_ROUND_FROM_CUTOFF"
    try:
        designated = _frame.designated_round(cutoff)
    except ValueError as exc:
        raise RouteEExecutionRefused(str(exc), phase=phase) from exc

    # 5 -- verify the beacon cryptographically through the pinned helper.  Pure.
    phase = "VERIFY_BEACON"
    beacon_bytes = _read_exact(beacon_path, phase, "the beacon response")
    response = _strict_object(beacon_bytes, phase, "the beacon response")
    helper = _pinned_verifier()
    if helper is None:
        raise RouteEExecutionRefused(
            "no verifier whose bytes match the pinned digests is available; an absent or "
            "unpinned verifier is a STOP, never a pass",
            phase=phase,
        )
    try:
        randomness = _frame.consume_beacon_round(
            response=response, expected_round=designated, helper_path=helper
        )
    except _frame.BeaconUnavailable as exc:
        raise RouteEExecutionWaiting(str(exc), phase=phase) from exc
    except _frame.BeaconInvalid as exc:
        raise RouteEExecutionRefused(str(exc), phase=phase) from exc

    # 6 -- derive the seed, the plan and the enrolment, entirely in memory.  Pure.
    phase = "DERIVE_SEED_PLAN_ENROLMENT"
    seed_root = derive_route_e_seed_root(
        pre_run_root_sha256=root, beacon_round=designated, beacon_randomness=randomness
    )
    policy = manifest["sample_size_and_world_policy"]
    distributions = manifest["distributions_and_draw_algorithm"]
    n_draws = int(policy["n_draws"])
    worlds = int(policy["worlds"])
    plan = _frame.build_draw_plan(seed_root, count=n_draws)
    plan_digest = plan.digest()
    enrolment = _locks.FamilyEnrolment(
        run_identity=str(manifest["run_identity"]),
        seed_root_sha256=_sha256_hex(seed_root),
        draw_plan_digest=plan_digest,
        n_draws=n_draws,
        worlds=worlds,
    )
    enrolment_sha = _locks.enrolment_digest(enrolment)

    # 7 -- first-write-wins on the namespace.  Still pure: it only observes.
    phase = "CHECK_NAMESPACE_FIRST_WRITE_WINS"
    _require(
        destination.name == str(manifest["output_namespace"]),
        "the output directory name must equal the declared output namespace",
        phase,
    )
    _require(
        destination.parent.is_dir(),
        f"the parent of the output directory does not exist: {destination.parent}",
        phase,
    )
    _require(
        not destination.exists(),
        "the namespace is already claimed; first write wins and a run is never replaced",
        phase,
    )

    # 8 -- FIRST AUTHORISED EFFECT.  Everything above succeeded.
    phase = "CREATE_OUTPUT_ROOT"
    try:
        os.mkdir(destination)
    except FileExistsError as exc:
        raise RouteEExecutionRefused(
            "the namespace was claimed concurrently; first write wins", phase=phase
        ) from exc
    except OSError as exc:
        raise RouteEExecutionRefused(f"the output root could not be created: {exc}", phase=phase) from exc

    _write_exact(
        destination / PROVENANCE_NAME,
        canonical_bytes(
            {
                "execution_version": EXECUTION_VERSION,
                "kind": "route-e-provenance/v1",
                "pre_run_root": root,
                "tag": ROUTE_E_PROVENANCE_TAG,
            }
        ),
    )
    _write_exact(destination / PRE_RUN_MANIFEST_NAME, manifest_bytes)
    _write_exact(destination / ANTERIORITY_NAME, anteriority_bytes)
    _write_exact(destination / BEACON_RESPONSE_NAME, beacon_bytes)
    _write_exact(
        destination / ENROLMENT_NAME,
        canonical_bytes(
            {
                "designated_round": designated,
                "draw_plan_digest": plan_digest,
                "enrolment_digest": enrolment_sha,
                "kind": "route-e-enrolment/v1",
                "law_proposal_indices": list(plan.proposal_indices),
                "lattice_sizes": list(plan.lattice_sizes),
                "n_draws": n_draws,
                "proposals_consumed": plan.proposals_consumed,
                "run_identity": enrolment.run_identity,
                "seed_root_sha256": enrolment.seed_root_sha256,
                "world_order": [list(item) for item in plan.world_order[:worlds]],
                "worlds": worlds,
            }
        ),
    )

    # 9 / 10 -- execute the worlds through the generic bridge, keeping EVERY attempt.
    phase = "EXECUTE_WORLDS"
    worlds_root = destination / WORLDS_DIRECTORY
    os.mkdir(worlds_root)
    horizon = int(distributions["horizon_steps"])
    cadence = int(distributions["cadence_steps"])
    schedule = _schedule(horizon, cadence)
    measurement_spec = MeasurementSpec(min_cells=1)
    attempts: list[dict[str, Any]] = []
    succeeded = 0
    for ordinal, (law_index, ic_ordinal) in enumerate(plan.world_order[:worlds]):
        world_directory = worlds_root / f"{ordinal:06d}"
        os.mkdir(world_directory)
        attempt: dict[str, Any] = {
            "attempt_ordinal": ordinal,
            "ic_ordinal": int(ic_ordinal),
            "law_index": int(law_index),
            "world_relative_path": world_directory.relative_to(destination).as_posix(),
        }
        try:
            law_spec = _law_spec_from_fields(plan.law_fields[law_index])
            state = _initial_state(
                seed_root, plan.ic_indices[law_index][ic_ordinal], int(plan.lattice_sizes[law_index])
            )
            record = run_measurement_bridge(
                world_directory,
                law_spec=law_spec,
                initial_state=state,
                sampled_frames=schedule,
                measurement_spec=measurement_spec,
                acquisition_source_identity={
                    "kind": "route-e-canonical-execution",
                    "name": f"{enrolment.run_identity}/{ordinal:06d}",
                },
            )
        except (BridgeError, ValueError, ArithmeticError, OSError) as exc:
            attempt["status"] = "CRASH"
            attempt["failure_class"] = type(exc).__name__
            attempt["failure_detail"] = str(exc)[:400]
        else:
            attempt["status"] = "SUCCESS"
            attempt["measurement_root_sha256"] = record.measurement_root_sha256
            attempt["lifecycle_document_sha256"] = record.owned_record.lifecycle_document_sha256
            attempt["terminal_record_count"] = int(record.owned_record.terminal_record_count)
            succeeded += 1
        attempts.append(attempt)

    phase = "RECORD_ATTEMPTS"
    _write_exact(
        destination / ATTEMPTS_NAME,
        b"".join(canonical_bytes(item) + b"\n" for item in attempts),
    )

    # 11 -- inventory, envelope, receipt.  Each binds only what precedes it: no cycle.
    phase = "SEAL_ENVELOPE"
    entries = _inventory(destination)
    inventory_document = {
        "entries": entries,
        "excluded": list(_INVENTORY_EXCLUDED),
        "kind": "route-e-file-inventory/v1",
    }
    inventory_sha = _write_exact(
        destination / FILE_INVENTORY_NAME, canonical_bytes(inventory_document)
    )
    envelope = {
        "anteriority_proof_type": proof["proof_type"],
        "anteriority_sha256": _sha256_hex(anteriority_bytes),
        "attempts": attempts,
        "beacon_response_sha256": _sha256_hex(beacon_bytes),
        "contributes_to_dataset": False,
        "designated_round": designated,
        "draw_plan_digest": plan_digest,
        "enrolment_digest": enrolment_sha,
        "execution_version": EXECUTION_VERSION,
        "file_inventory_sha256": inventory_sha,
        "fixture_class": manifest["fixture_class"],
        "kind": POST_RUN_KIND,
        "mode": manifest["mode"],
        "output_namespace": manifest["output_namespace"],
        "pre_run_manifest_sha256": _sha256_hex(manifest_bytes),
        "pre_run_root": root,
        "provenance_tag": ROUTE_E_PROVENANCE_TAG,
        "public_registry_inclusion_proven": public_inclusion,
        "seed_root_sha256": enrolment.seed_root_sha256,
        "world_order": [list(item) for item in plan.world_order[:worlds]],
        "worlds_attempted": len(attempts),
        "worlds_failed": len(attempts) - succeeded,
        "worlds_succeeded": succeeded,
    }
    envelope_sha = _write_exact(destination / POST_RUN_ENVELOPE_NAME, canonical_bytes(envelope))
    final_root = post_run_root(envelope)
    _write_exact(
        destination / FINAL_RECEIPT_NAME,
        canonical_bytes(
            {
                "envelope_sha256": envelope_sha,
                "kind": RECEIPT_KIND,
                "post_run_root": final_root,
                "pre_run_root": root,
            }
        ),
    )
    return RouteERunRecord(
        output_directory=str(destination),
        pre_run_root=root,
        post_run_root=final_root,
        designated_round=designated,
        seed_root_sha256=enrolment.seed_root_sha256,
        draw_plan_digest=plan_digest,
        enrolment_digest=enrolment_sha,
        worlds_attempted=len(attempts),
        worlds_succeeded=succeeded,
        worlds_failed=len(attempts) - succeeded,
        file_inventory_sha256=inventory_sha,
        public_registry_inclusion_proven=public_inclusion,
        contributes_to_dataset=False,
    )
