"""FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00 -- the whole test surface.

Every test this mission adds lives HERE, in a file that is NOT one of the four selectors
bound by ``test_rs01_12``.  Nothing is added, removed or renamed in those four files, so
their collected node list stays at 251 entries with the same SHA-256.  ``test_collection_14``
below re-checks that from the outside.

The real cryptography runs only when a verifier whose BYTES match the pinned reproducible
build is available.  Both branches assert something real: with the verifier, a synthetic
bundle reaches the first authorised effect; without it, the run is refused at
``VERIFY_BEACON`` and nothing is written.  A missing verifier is never a pass.

No scientific data, seed, family or namespace is used anywhere.  The only bundle that
succeeds is declared ``SYNTHETIC_NON_SCIENTIFIC`` and lives in a temporary directory; the
admission layer refuses to let it contribute to any dataset.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from edlab.substrates.lattice_bond import future_route_e_admission as admission
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame

_REPO_ROOT = Path(__file__).resolve().parent.parent
_VECTORS = json.loads((_REPO_ROOT / "tests" / "data" / "route_e_beacon_vectors.json").read_text("ascii"))
_V2 = [item for item in _VECTORS["vectors"] if item["id"] == "V2"][0]

#: ``designated_round(C) == 123``, the round of the committed quicknet fixture V2.
#: ``t(123) = genesis + 122 * period = 1692803733`` and ``C = t(123) - 86400``.
CUTOFF_C = 1692803733 - 86400


def _pinned_verifier_available() -> bool:
    return execution._pinned_verifier() is not None


VERIFIER_AVAILABLE = _pinned_verifier_available()
requires_verifier = pytest.mark.skipif(  # noqa: PT028 - see the module docstring
    not VERIFIER_AVAILABLE,
    reason="no verifier whose bytes match the pinned reproducible build is present",
)


# --------------------------------------------------------------------------------------
# fixtures -- synthetic, non-scientific, temporary
# --------------------------------------------------------------------------------------


def _manifest(**overrides):
    document = {
        "canonical_cutoff_C": CUTOFF_C,
        "crash_retry_and_attempt_policy": {
            "attempt_inventory_required": True,
            "replacement_allowed": False,
            "retries_allowed": 0,
        },
        "designated_round_rule": dict(execution.DESIGNATED_ROUND_RULE),
        "distributions_and_draw_algorithm": {
            "cadence_steps": 1,
            "generator": frame.DRAW_GENERATOR["algorithm"],
            "horizon_steps": 2,
            "lattice_sizes": list(frame.LATTICE_SIZES),
        },
        "experiment_id": "ROUTE-E-EXECUTION-BOUNDARY-CORRECTION-00",
        "fixture_class": "SYNTHETIC_NON_SCIENTIFIC",
        "kind": execution.PRE_RUN_KIND,
        "mode": "EXPLORATORY_PILOT",
        "outcome_and_claim_ceiling": {
            "claim_template": "none-in-this-mission",
            "estimand": "persistence-under-turnover",
            "negative_max_k": frame.NEGATIVE_MAX_K,
            "positive_min_k": frame.POSITIVE_MIN_K,
        },
        "output_namespace": "SYNTHETIC-NONSCI-BOUNDARY-0001",
        "protocol_and_analysis_digests": {"protocol": "0" * 64},
        "run_identity": "synthetic-boundary-0001",
        "sample_size_and_world_policy": {
            "initial_conditions_per_law": frame.INITIAL_CONDITIONS_PER_LAW,
            "n_draws": 1,
            "world_order_rule": frame.CANONICAL_DRAW_ORDER[3],
            "worlds": 1,
        },
        "schema_version": execution.EXECUTION_VERSION,
        "source_commit_and_digests": {
            "commit_sha1": "da0ec3f1e6198fcb25690cee02490f0d2ce9d034",
            "digests": {"edlab/substrates/lattice_bond/future_route_e_execution.py": "1" * 64},
        },
    }
    document.update(overrides)
    return document


def _bundle(directory: Path, document=None, *, proof_overrides=None) -> tuple[Path, str]:
    document = _manifest() if document is None else document
    bundle = directory / "bundle"
    bundle.mkdir(parents=True)
    (bundle / execution.PRE_RUN_MANIFEST_NAME).write_bytes(execution.canonical_bytes(document))
    root = execution.pre_run_root(document)
    proof = {
        "binds_cutoff_C": document.get("canonical_cutoff_C"),
        "binds_pre_run_root": root,
        "detail": {"note": "structural binding only; no public registry is contacted"},
        "kind": "route-e-pre-run-anteriority/v1",
        "proof_type": "SELF_ATTESTED_NON_PUBLIC",
        "public_registry_inclusion_proven": False,
    }
    if proof_overrides:
        proof.update(proof_overrides)
    (bundle / execution.ANTERIORITY_NAME).write_bytes(execution.canonical_bytes(proof))
    return bundle, root


def _beacon(directory: Path, **overrides) -> Path:
    response = {
        "chain_hash": _V2["chain_hash"],
        "randomness": _V2["randomness"],
        "round": int(_V2["round"]),
        "signature": _V2["signature"],
    }
    response.update(overrides)
    path = directory / "beacon.json"
    path.write_bytes(execution.canonical_bytes(response))
    return path


def _destination(directory: Path, namespace="SYNTHETIC-NONSCI-BOUNDARY-0001") -> Path:
    parent = directory / "out"
    parent.mkdir(exist_ok=True)
    return parent / namespace


def _run(directory: Path, document=None, *, proof_overrides=None, beacon_overrides=None):
    bundle, _ = _bundle(directory, document, proof_overrides=proof_overrides)
    beacon = _beacon(directory, **(beacon_overrides or {}))
    namespace = (document or _manifest())["output_namespace"]
    return execution.run_route_e(bundle, beacon, _destination(directory, namespace))


def _rewrite(path: Path, mutate) -> None:
    document = json.loads(path.read_bytes().decode("ascii"))
    mutate(document)
    path.write_bytes(execution.canonical_bytes(document))


# --------------------------------------------------------------------------------------
# 0.  the architecture itself
# --------------------------------------------------------------------------------------


def test_arch_01_the_two_roots_are_distinct_objects_and_cannot_be_interchanged() -> None:
    """A pre-run manifest and a post-run envelope never hash to the same root."""
    payload = {"a": 1}
    assert execution.pre_run_root(payload) != execution.post_run_root(payload)
    assert execution.PRE_RUN_DOMAIN != execution.POST_RUN_DOMAIN
    assert execution.PRE_RUN_KIND != execution.POST_RUN_KIND


def test_arch_02_a_single_public_execution_api_with_exactly_three_parameters() -> None:
    import inspect

    signature = inspect.signature(execution.run_route_e)
    assert list(signature.parameters) == [
        "pre_run_bundle_path",
        "beacon_response_path",
        "output_directory",
    ]
    text = (_REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_execution.py").read_text("utf-8")
    for forbidden in ("granted", "authorised=True", "authorized=True", "def verify_callback"):
        assert forbidden not in text, forbidden


def test_arch_03_no_route_e_parameter_was_added_to_any_generic_function() -> None:
    """The retired five-guard strategy left no trace in the generic sources."""
    import inspect

    from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
    from edlab.substrates.lattice_bond import future_lifecycle_runner as runner
    from edlab.substrates.lattice_bond import lifecycle as lifecycle_module

    for module, name in (
        (runner, "publish_future_family_completion"),
        (runner, "open_analysis_access"),
        (owned, "run_owned_future_pipeline"),
        (owned, "open_owned_analysis_access"),
        (lifecycle_module, "qualify_and_write_lifecycle_contract"),
    ):
        assert "route_e" not in inspect.signature(getattr(module, name)).parameters, name


def test_arch_04_the_execution_module_sits_above_the_bridge_and_never_edits_it() -> None:
    text = (_REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_execution.py").read_text("utf-8")
    assert "run_measurement_bridge" in text
    bridge = (_REPO_ROOT / "edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py").read_text("utf-8")
    assert "future_route_e_execution" not in bridge
    assert "route_e" not in bridge


def test_arch_05_the_admission_reuses_no_private_helper_of_the_producer() -> None:
    """A1-R3 replaces a FALSE claim with a true one.

    The A1-R2 assertion here was "the admission module imports no engine", established by
    searching the source text for ``from .engine import``.  Both halves were wrong: the
    module imported ``future_route_e_execution``, which imports the engine, so the property
    was false; and a string search is not evidence of an import graph, so the method could
    not have detected it.

    What is asserted now is the property that is true and that matters: the verifier reuses
    no private helper of the producer.  The runtime claim -- no ``LatticeBondEngine``
    instantiated, no simulation step taken, no output-tree mutation -- is established in a
    fresh subprocess by ``tests/test_future_route_e_a1r3_admission.py::test_f02``, because
    only an interpreter can establish it.
    """
    import ast

    text = (_REPO_ROOT / "edlab/substrates/lattice_bond/future_route_e_admission.py").read_text("utf-8")
    imported: list[str] = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ImportFrom):
            imported.extend(f"{node.module or ''}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
    assert not any("future_route_e_execution" in name for name in imported), imported
    assert any("route_e_protocol" in name for name in imported), imported


# --------------------------------------------------------------------------------------
# 1.  absent, wrong-typed or altered bundle -> refusal BEFORE any effect
# --------------------------------------------------------------------------------------


def _assert_no_effect(destination: Path) -> None:
    assert not destination.exists()
    assert list(destination.parent.iterdir()) == []


def test_bundle_01_an_absent_bundle_is_refused_before_any_effect(tmp_path: Path) -> None:
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(tmp_path / "nowhere", tmp_path / "nothing.json", destination)
    assert caught.value.phase == "READ_AND_CANONICALISE_BUNDLE"
    assert caught.value.effects_started is False
    _assert_no_effect(destination)


def test_bundle_02_a_file_where_a_bundle_belongs_is_refused(tmp_path: Path) -> None:
    impostor = tmp_path / "bundle_as_file"
    impostor.write_text("{}", encoding="ascii")
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(impostor, tmp_path / "nothing.json", destination)
    assert caught.value.phase == "READ_AND_CANONICALISE_BUNDLE"
    _assert_no_effect(destination)


def test_bundle_03_a_non_canonical_manifest_is_refused(tmp_path: Path) -> None:
    bundle, _ = _bundle(tmp_path)
    path = bundle / execution.PRE_RUN_MANIFEST_NAME
    path.write_bytes(b" " + path.read_bytes())
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "canonical form" in str(caught.value)
    _assert_no_effect(destination)


def test_bundle_04_a_post_run_envelope_cannot_pose_as_a_pre_run_manifest(tmp_path: Path) -> None:
    document = _manifest(kind=execution.POST_RUN_KIND)
    bundle, _ = _bundle(tmp_path, document)
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "kind" in str(caught.value)
    _assert_no_effect(destination)


def test_bundle_05_an_altered_manifest_invalidates_its_own_proof(tmp_path: Path) -> None:
    """The proof is genuine and well formed; it simply proves a DIFFERENT manifest."""
    bundle, root = _bundle(tmp_path)
    path = bundle / execution.PRE_RUN_MANIFEST_NAME
    _rewrite(path, lambda document: document.update({"experiment_id": "SOMETHING-ELSE"}))
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert caught.value.phase == "VERIFY_ANTERIORITY"
    assert "DIFFERENT pre-run root" in str(caught.value)
    _assert_no_effect(destination)


def test_bundle_06_a_valid_proof_of_another_cutoff_is_refused(tmp_path: Path) -> None:
    bundle, root = _bundle(tmp_path, proof_overrides={"binds_cutoff_C": CUTOFF_C + 1})
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert caught.value.phase == "VERIFY_ANTERIORITY"
    _assert_no_effect(destination)


def test_bundle_07_the_frozen_a2_proof_type_is_refused_not_believed(tmp_path: Path) -> None:
    """The owner froze OTS AND RFC 3161.  That verifier is not implemented, so a run
    claiming it is STOPPED rather than accepted on its word."""
    bundle, _ = _bundle(
        tmp_path,
        proof_overrides={"proof_type": "OTS_PLUS_RFC3161", "public_registry_inclusion_proven": True},
    )
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "NOT implemented" in str(caught.value)
    _assert_no_effect(destination)


def test_bundle_08_a_self_attested_proof_may_never_claim_public_inclusion(tmp_path: Path) -> None:
    bundle, _ = _bundle(tmp_path, proof_overrides={"public_registry_inclusion_proven": True})
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "never claim public registry inclusion" in str(caught.value)
    _assert_no_effect(destination)


# --------------------------------------------------------------------------------------
# 3.  a pre-run root may not carry post-run information
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "injected",
    [
        {"seed_root_sha256": "0" * 64},
        {"draw_plan_digest": "0" * 64},
        {"measurement_root_sha256": "0" * 64},
        {"join_digest": "0" * 64},
        {"k": 42},
        {"outcome": "POSITIVE"},
        {"result": "anything"},
        {"round": 123},
        {"randomness": "0" * 64},
    ],
)
def test_pre_run_01_a_post_run_field_anywhere_in_p_is_refused(tmp_path: Path, injected) -> None:
    document = _manifest()
    document["protocol_and_analysis_digests"] = dict(document["protocol_and_analysis_digests"], **injected)
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / execution.PRE_RUN_MANIFEST_NAME).write_bytes(execution.canonical_bytes(document))
    (bundle / execution.ANTERIORITY_NAME).write_bytes(
        execution.canonical_bytes(
            {
                "binds_cutoff_C": CUTOFF_C,
                "binds_pre_run_root": execution.pre_run_root(document),
                "detail": {},
                "kind": "route-e-pre-run-anteriority/v1",
                "proof_type": "SELF_ATTESTED_NON_PUBLIC",
                "public_registry_inclusion_proven": False,
            }
        )
    )
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "post-run" in str(caught.value)
    _assert_no_effect(destination)


def test_pre_run_02_the_manifest_may_not_carry_an_unknown_key(tmp_path: Path) -> None:
    document = _manifest()
    document["extra_field"] = "smuggled"
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / execution.PRE_RUN_MANIFEST_NAME).write_bytes(execution.canonical_bytes(document))
    (bundle / execution.ANTERIORITY_NAME).write_bytes(b"{}")
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert "unknown keys" in str(caught.value)
    _assert_no_effect(destination)


# --------------------------------------------------------------------------------------
# 4.  an injected round or seed is impossible, not merely refused
# --------------------------------------------------------------------------------------


def test_injection_01_the_public_api_accepts_no_seed_round_law_or_outcome() -> None:
    import inspect

    parameters = set(inspect.signature(execution.run_route_e).parameters)
    for forbidden in (
        "seed", "seed_root", "round", "beacon_round", "law", "law_spec", "initial_state",
        "initial_condition", "tracking", "outcome", "root", "verifier", "granted",
    ):
        assert forbidden not in parameters, forbidden


def test_injection_02_the_round_is_a_function_of_the_cutoff_alone(tmp_path: Path) -> None:
    """Changing the proof cannot change the round; changing C is the only way."""
    assert frame.designated_round(CUTOFF_C) == int(_V2["round"])
    assert frame.designated_round(CUTOFF_C + 3) != int(_V2["round"])


def test_injection_03_a_response_carrying_another_round_is_refused(tmp_path: Path) -> None:
    bundle, _ = _bundle(tmp_path)
    beacon = _beacon(tmp_path, round=int(_V2["round"]) + 1)
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, beacon, destination)
    assert caught.value.phase == "VERIFY_BEACON"
    _assert_no_effect(destination)


def test_injection_04_the_seed_is_derived_from_p_and_the_verified_randomness_only() -> None:
    randomness = bytes.fromhex(_V2["randomness"])
    first = execution.derive_route_e_seed_root(
        pre_run_root_sha256="a" * 64, beacon_round=123, beacon_randomness=randomness
    )
    second = execution.derive_route_e_seed_root(
        pre_run_root_sha256="b" * 64, beacon_round=123, beacon_randomness=randomness
    )
    third = execution.derive_route_e_seed_root(
        pre_run_root_sha256="a" * 64, beacon_round=124, beacon_randomness=randomness
    )
    assert first != second and first != third
    with pytest.raises(ValueError):
        execution.derive_route_e_seed_root(
            pre_run_root_sha256="a" * 64, beacon_round=123, beacon_randomness=b"short"
        )


def test_injection_05_an_unpinned_verifier_is_not_a_verifier(tmp_path: Path, monkeypatch) -> None:
    impostor = tmp_path / "impostor"
    impostor.write_bytes(b"#!/bin/sh\necho '{\"status\":\"verified\"}'\n")
    impostor.chmod(0o755)
    monkeypatch.setenv("ROUTE_E_DRAND_VERIFY", str(impostor))
    assert execution._pinned_verifier() is None
    bundle, _ = _bundle(tmp_path)
    destination = _destination(tmp_path)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), destination)
    assert caught.value.phase == "VERIFY_BEACON"
    assert "pinned digests" in str(caught.value)
    _assert_no_effect(destination)


# --------------------------------------------------------------------------------------
# 5.  no mkdir, no engine and no write before the verification completes
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "break_it",
    [
        "absent_manifest",
        "altered_manifest",
        "wrong_cutoff_proof",
        "post_run_field",
        "wrong_round",
    ],
)
def test_no_effect_01_nothing_is_created_before_the_verification_completes(
    tmp_path: Path, monkeypatch, break_it
) -> None:
    """``os.mkdir`` and the bridge are ARMED to explode.  A refusal must not touch them."""

    document = _manifest()
    proof_overrides = None
    beacon_overrides = None
    if break_it == "post_run_field":
        document["protocol_and_analysis_digests"] = {"protocol": "0" * 64, "k": 1}
    if break_it == "wrong_cutoff_proof":
        proof_overrides = {"binds_cutoff_C": CUTOFF_C + 7}
    if break_it == "wrong_round":
        beacon_overrides = {"round": int(_V2["round"]) + 5}

    bundle, _ = _bundle(tmp_path, document, proof_overrides=proof_overrides)
    if break_it == "absent_manifest":
        (bundle / execution.PRE_RUN_MANIFEST_NAME).unlink()
    if break_it == "altered_manifest":
        _rewrite(
            bundle / execution.PRE_RUN_MANIFEST_NAME,
            lambda item: item.update({"experiment_id": "MUTATED"}),
        )
    beacon = _beacon(tmp_path, **(beacon_overrides or {}))
    destination = _destination(tmp_path, document["output_namespace"])

    # every directory this test needs already exists; only NOW are the traps armed, so a
    # single mkdir or a single engine step inside run_route_e is fatal.
    def _explode_mkdir(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("mkdir was reached before the verification completed")

    def _explode_bridge(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("the engine was reached before the verification completed")

    monkeypatch.setattr(execution.os, "mkdir", _explode_mkdir)
    monkeypatch.setattr(execution, "run_measurement_bridge", _explode_bridge)

    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, beacon, destination)
    assert caught.value.effects_started is False
    assert execution.EXECUTION_PHASES.index(caught.value.phase) < execution.EXECUTION_PHASES.index(
        execution.FIRST_EFFECT_PHASE
    )
    _assert_no_effect(destination)


@requires_verifier
def test_no_effect_02_the_very_first_effect_is_the_output_root(tmp_path: Path, monkeypatch) -> None:
    """Everything verifies, then ``os.mkdir`` fails: the refusal lands EXACTLY on the
    first authorised effect, which proves nothing was written earlier."""

    bundle, _ = _bundle(tmp_path)
    beacon = _beacon(tmp_path)
    destination = _destination(tmp_path)

    def _refuse_mkdir(*args, **kwargs):
        raise OSError("mkdir disarmed for this test")

    monkeypatch.setattr(execution.os, "mkdir", _refuse_mkdir)
    monkeypatch.setattr(
        execution,
        "run_measurement_bridge",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("engine reached")),
    )
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, beacon, destination)
    assert caught.value.phase == execution.FIRST_EFFECT_PHASE
    _assert_no_effect(destination)


def test_no_effect_03_without_a_pinned_verifier_nothing_is_written(tmp_path: Path, monkeypatch) -> None:
    bundle, _ = _bundle(tmp_path)
    beacon = _beacon(tmp_path)
    destination = _destination(tmp_path)
    monkeypatch.setattr(execution, "_pinned_verifier", lambda: None)
    monkeypatch.setattr(
        execution.os, "mkdir", lambda *a, **k: (_ for _ in ()).throw(AssertionError("mkdir"))
    )
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, beacon, destination)
    assert caught.value.phase == "VERIFY_BEACON"
    _assert_no_effect(destination)


# --------------------------------------------------------------------------------------
# 6.  a valid synthetic bundle really reaches the first authorised effect
# --------------------------------------------------------------------------------------


@requires_verifier
def test_valid_01_a_synthetic_bundle_completes_and_seals(tmp_path: Path) -> None:
    record = _run(tmp_path)
    root = Path(record.output_directory)
    assert root.is_dir()
    for name in (
        execution.PROVENANCE_NAME,
        execution.PRE_RUN_MANIFEST_NAME,
        execution.ANTERIORITY_NAME,
        execution.BEACON_RESPONSE_NAME,
        execution.ENROLMENT_NAME,
        execution.ATTEMPTS_NAME,
        execution.FILE_INVENTORY_NAME,
        execution.POST_RUN_ENVELOPE_NAME,
        execution.FINAL_RECEIPT_NAME,
    ):
        assert (root / name).is_file(), name
    assert record.designated_round == int(_V2["round"])
    assert record.worlds_attempted == 1
    assert record.public_registry_inclusion_proven is False
    assert record.contributes_to_dataset is False
    assert record.pre_run_root != record.post_run_root


@requires_verifier
def test_valid_02_the_namespace_is_first_write_wins(tmp_path: Path) -> None:
    _run(tmp_path)
    bundle, _ = _bundle(tmp_path / "second")
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(
            bundle, _beacon(tmp_path / "second"), _destination(tmp_path)
        )
    assert caught.value.phase == "CHECK_NAMESPACE_FIRST_WRITE_WINS"
    assert "first write wins" in str(caught.value)


@requires_verifier
def test_valid_03_the_run_is_deterministic(tmp_path: Path) -> None:
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b")
    assert first.pre_run_root == second.pre_run_root
    assert first.seed_root_sha256 == second.seed_root_sha256
    assert first.draw_plan_digest == second.draw_plan_digest
    assert first.enrolment_digest == second.enrolment_digest


# --------------------------------------------------------------------------------------
# 7-9.  generic, Stage-B and reproducer outputs are inadmissible
# --------------------------------------------------------------------------------------


def test_inadmissible_01_a_bare_measurement_bridge_output_is_refused(tmp_path: Path) -> None:
    """Shaped exactly like a bridge run: MEASUREMENT.json, BRIDGE_BINDING.json, frames.

    No bridge run is executed here.  The discriminator is structural and is proved twice:
    the directory carries no ``ROUTE_E_PROVENANCE.json``, and the bridge source provably
    never writes one.
    """
    generic = tmp_path / "generic-bridge-run"
    (generic / "measurement_frames").mkdir(parents=True)
    (generic / "MEASUREMENT.json").write_text("{}", encoding="ascii")
    (generic / "BRIDGE_BINDING.json").write_text("{}", encoding="ascii")
    (generic / "LIFECYCLE.json").write_text("{}", encoding="ascii")
    verdict = admission.verify_route_e_run(generic)
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"
    assert verdict.contributes_to_k is False
    bridge_source = (_REPO_ROOT / "edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py").read_text("utf-8")
    assert execution.ROUTE_E_PROVENANCE_TAG not in bridge_source
    assert execution.PROVENANCE_NAME not in bridge_source


def test_inadmissible_02_a_stage_b_namespace_is_refused(tmp_path: Path) -> None:
    stage_b = tmp_path / "stage-b-namespace"
    stage_b.mkdir()
    (stage_b / "enrollment.json").write_text("{}", encoding="ascii")
    (stage_b / "classification.json").write_text("{}", encoding="ascii")
    verdict = admission.verify_route_e_run(stage_b)
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"
    source = (_REPO_ROOT / "edlab/substrates/lattice_bond/stage_b.py").read_text("utf-8")
    assert execution.ROUTE_E_PROVENANCE_TAG not in source
    assert execution.PROVENANCE_NAME not in source
    assert "future_route_e" not in source


def test_inadmissible_03_the_historical_reproducer_is_refused_but_stays_readable(tmp_path: Path) -> None:
    reproduction = tmp_path / "historical-reproduction"
    reproduction.mkdir()
    payload = json.dumps({"reproduced": True}, sort_keys=True).encode("ascii")
    (reproduction / "REPRODUCTION.json").write_bytes(payload)
    verdict = admission.verify_route_e_run(reproduction)
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"
    # refusing a ROUTE E claim never damages or hides the artefact itself
    assert (reproduction / "REPRODUCTION.json").read_bytes() == payload
    source = (_REPO_ROOT / "edlab/substrates/lattice_bond/stage_b_reproduce.py").read_text("utf-8")
    assert execution.PROVENANCE_NAME not in source
    assert "future_route_e" not in source
    assert "LatticeBondEngine" not in source


def test_inadmissible_04_the_five_historical_functions_write_no_route_e_provenance() -> None:
    for relative in (
        "edlab/substrates/lattice_bond/lifecycle.py",
        "edlab/substrates/lattice_bond/future_lifecycle_runner.py",
        "edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py",
    ):
        text = (_REPO_ROOT / relative).read_text("utf-8")
        assert execution.PROVENANCE_NAME not in text, relative
        assert execution.ROUTE_E_PROVENANCE_TAG not in text, relative


def test_inadmissible_05_a_forged_provenance_tag_is_refused(tmp_path: Path) -> None:
    forged = tmp_path / "forged"
    forged.mkdir()
    (forged / execution.PROVENANCE_NAME).write_bytes(
        execution.canonical_bytes(
            {
                "execution_version": execution.EXECUTION_VERSION,
                "kind": "route-e-provenance/v1",
                "pre_run_root": "0" * 64,
                "tag": "SOMETHING_ELSE",
            }
        )
    )
    verdict = admission.verify_route_e_run(forged)
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"


# --------------------------------------------------------------------------------------
# 10.  tampering with any bound artefact invalidates E
# --------------------------------------------------------------------------------------


@requires_verifier
def test_tamper_00_an_untouched_root_is_admissible(tmp_path: Path) -> None:
    record = _run(tmp_path)
    verdict = admission.verify_route_e_run(record.output_directory)
    assert verdict.admissible is True, verdict.reason
    assert verdict.reason_code == "RECOMPUTED"
    assert verdict.pre_run_root == record.pre_run_root
    assert verdict.post_run_root == record.post_run_root
    assert verdict.engine_steps_taken == 0


@requires_verifier
@pytest.mark.parametrize(
    "target",
    ["manifest", "beacon", "enrolment", "attempts_drop", "attempts_reorder", "world_file",
     "inventory", "envelope", "receipt", "extra_file"],
)
def test_tamper_01_any_alteration_makes_the_post_run_root_invalid(tmp_path: Path, target) -> None:
    record = _run(tmp_path)
    root = Path(record.output_directory)
    if target == "manifest":
        _rewrite(root / execution.PRE_RUN_MANIFEST_NAME, lambda d: d.update({"experiment_id": "X"}))
    elif target == "beacon":
        _rewrite(root / execution.BEACON_RESPONSE_NAME, lambda d: d.update({"round": 999}))
    elif target == "enrolment":
        _rewrite(root / execution.ENROLMENT_NAME, lambda d: d.update({"seed_root_sha256": "0" * 64}))
    elif target == "attempts_drop":
        (root / execution.ATTEMPTS_NAME).write_bytes(b"")
    elif target == "attempts_reorder":
        lines = [
            line for line in (root / execution.ATTEMPTS_NAME).read_bytes().split(b"\n") if line
        ]
        document = json.loads(lines[0].decode("ascii"))
        document["attempt_ordinal"] = 7
        (root / execution.ATTEMPTS_NAME).write_bytes(execution.canonical_bytes(document) + b"\n")
    elif target == "world_file":
        target_path = next((root / execution.WORLDS_DIRECTORY).rglob("*.json"))
        target_path.write_bytes(target_path.read_bytes() + b" ")
    elif target == "inventory":
        _rewrite(root / execution.FILE_INVENTORY_NAME, lambda d: d["entries"].pop())
    elif target == "envelope":
        _rewrite(root / execution.POST_RUN_ENVELOPE_NAME, lambda d: d.update({"worlds_succeeded": 99}))
    elif target == "receipt":
        _rewrite(root / execution.FINAL_RECEIPT_NAME, lambda d: d.update({"post_run_root": "0" * 64}))
    elif target == "extra_file":
        (root / "SMUGGLED.json").write_bytes(b"{}")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False, target
    assert verdict.contributes_to_k is False


@requires_verifier
def test_tamper_02_a_crash_removed_from_the_inventory_is_detected(tmp_path: Path, monkeypatch) -> None:
    """A run whose only world crashed still records the attempt.  Deleting it is caught."""

    def _crash(*args, **kwargs):
        raise ValueError("synthetic crash, non-scientific")

    monkeypatch.setattr(execution, "run_measurement_bridge", _crash)
    record = _run(tmp_path)
    assert record.worlds_failed == 1 and record.worlds_succeeded == 0
    root = Path(record.output_directory)
    entries = [line for line in (root / execution.ATTEMPTS_NAME).read_bytes().split(b"\n") if line]
    assert len(entries) == 1
    assert json.loads(entries[0].decode("ascii"))["status"] == "CRASH"
    assert admission.verify_route_e_run(root).admissible is True
    (root / execution.ATTEMPTS_NAME).write_bytes(b"")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "ATTEMPT_INVENTORY_INCOMPLETE"


@requires_verifier
def test_tamper_03_a_crash_is_unknown_and_never_a_silent_zero(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        execution,
        "run_measurement_bridge",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("synthetic crash")),
    )
    record = _run(tmp_path)
    verdict = admission.verify_route_e_run(record.output_directory)
    assert verdict.admissible is True
    assert len(verdict.worlds) == 1
    assert verdict.worlds[0].Y is None
    assert verdict.worlds[0].disposition == frame.DrawDisposition.TECHNICALLY_UNKNOWN.value
    assert verdict.k_unknown == 1


# --------------------------------------------------------------------------------------
# 11.  the independent reader recomputes without the engine and believes nothing
# --------------------------------------------------------------------------------------


@requires_verifier
def test_reader_01_the_admission_recomputes_every_root_from_disk(tmp_path: Path) -> None:
    record = _run(tmp_path)
    verdict = admission.verify_route_e_run(record.output_directory)
    assert verdict.seed_root_sha256 == record.seed_root_sha256
    assert verdict.draw_plan_digest == record.draw_plan_digest
    assert verdict.enrolment_digest == record.enrolment_digest
    assert verdict.designated_round == record.designated_round
    assert verdict.engine_steps_taken == 0


@requires_verifier
def test_reader_02_no_persisted_document_carries_an_answer(tmp_path: Path) -> None:
    """The runner writes evidence only.  Planting an answer makes the root inadmissible."""
    record = _run(tmp_path)
    root = Path(record.output_directory)
    assert admission.verify_route_e_run(root).admissible is True
    (root / "OPINION.json").write_bytes(json.dumps({"verdict": "POSITIVE"}).encode("ascii"))
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "RUNNER_WROTE_AN_ANSWER"


@requires_verifier
def test_reader_03_a_refusal_is_a_verdict_not_an_exception(tmp_path: Path) -> None:
    verdict = admission.verify_route_e_run(tmp_path / "absent")
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_DIRECTORY"
    assert verdict.contributes_to_k is False


# --------------------------------------------------------------------------------------
# 12.  pilot and confirmation never mix
# --------------------------------------------------------------------------------------


def test_scope_01_a_confirmatory_run_may_not_be_synthetic(tmp_path: Path) -> None:
    document = _manifest(mode="CONFIRMATORY_67")
    bundle, _ = _bundle(tmp_path, document)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"]))
    assert "may not be synthetic" in str(caught.value)


def test_scope_02_a_confirmatory_run_is_frozen_at_67_and_134(tmp_path: Path) -> None:
    document = _manifest(
        mode="CONFIRMATORY_67",
        fixture_class="SCIENTIFIC",
        output_namespace="ROUTE-E-CONFIRMATORY-0001",
    )
    bundle, _ = _bundle(tmp_path, document)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"]))
    assert "67 draws and 134 worlds" in str(caught.value)


def test_scope_03_a_synthetic_fixture_must_use_the_synthetic_namespace(tmp_path: Path) -> None:
    document = _manifest(output_namespace="ROUTE-E-LOOKS-REAL-0001")
    bundle, _ = _bundle(tmp_path, document)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"]))
    assert execution.SYNTHETIC_NAMESPACE_PREFIX in str(caught.value)


def test_scope_04_a_scientific_run_may_not_borrow_the_synthetic_prefix(tmp_path: Path) -> None:
    document = _manifest(fixture_class="SCIENTIFIC")
    bundle, _ = _bundle(tmp_path, document)
    with pytest.raises(execution.RouteEExecutionRefused) as caught:
        execution.run_route_e(bundle, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"]))
    assert "borrow the synthetic namespace prefix" in str(caught.value)


@requires_verifier
def test_scope_05_thresholds_are_never_applied_outside_a_confirmatory_run(tmp_path: Path) -> None:
    record = _run(tmp_path)
    verdict = admission.verify_route_e_run(record.output_directory)
    assert verdict.thresholds_applied is False
    assert verdict.contributes_to_k is False
    joined = " ".join(verdict.notes)
    assert "42 / 9" in joined
    assert "pilot units are never added to the confirmatory k" in joined


@requires_verifier
def test_scope_06_two_namespaces_produce_disjoint_seeds_and_counts(tmp_path: Path) -> None:
    first = _run(tmp_path / "a")
    other = _manifest(
        output_namespace="SYNTHETIC-NONSCI-BOUNDARY-0002", run_identity="synthetic-boundary-0002"
    )
    second = _run(tmp_path / "b", other)
    assert first.pre_run_root != second.pre_run_root
    assert first.seed_root_sha256 != second.seed_root_sha256
    assert Path(first.output_directory).name != Path(second.output_directory).name
    assert admission.verify_route_e_run(first.output_directory).contributes_to_k is False
    assert admission.verify_route_e_run(second.output_directory).contributes_to_k is False


# --------------------------------------------------------------------------------------
# 13-14.  the historical surface is untouched
# --------------------------------------------------------------------------------------

HISTORICAL_QUALIFICATIONS = {
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json":
        "8f423bb0f0ece04a3e576b76cb2c7704d5edf6c82c827110bd5608e8e5514ece",
    "docs/individuation/FUTURE_LIFECYCLE_CONTRACT_REQUALIFICATION_01R_QUALIFICATION.json":
        "0752b86c6ef9c7b6579a90e7be6250bc2500dcbfbac4d47379c40e277061f403",
    "docs/individuation/FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json":
        "509f27b23a17b36b7c027cb687860f61b5ee53f4247c0f58e04d2ff1ffd6643a",
    "docs/individuation/FUTURE_LIFECYCLE_RUNNER_HARDENING_00_QUALIFICATION.json":
        "f29da3694b2438ff6bc0d03692771020b145ec6edcfa6ae80a533040207f58df",
}

SELECTED_NODE_COUNT = 251
SELECTED_NODE_LIST_SHA256 = "a425c3736f0b5d819ef708c2433b785cf706381798ffc48a7ce4b5941161276a"
SELECTORS = (
    "tests/test_empty_right_nonunit_cadence_tracker_repair.py",
    "tests/test_future_lifecycle_contract.py",
    "tests/test_future_lifecycle_runner_integration.py",
    "tests/test_lattice_bond_instrumentation.py",
)

INHERITED_FAILURES = (
    "tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[split]",
    "tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[merge]",
    "tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[tie]",
    "tests/test_lattice_bond_stage_b.py::test_independent_tracker_matches_split_merge_tie_and_collapse[collapse]",
    "tests/test_motile_polar.py::test_scramble_preserves_all_declared_invariants_and_destroys_organization",
)


def test_historical_13_the_four_qualifications_are_byte_identical() -> None:
    for relative, digest in HISTORICAL_QUALIFICATIONS.items():
        observed = hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
        assert observed == digest, relative


def test_historical_13b_the_five_inherited_failures_still_exist_by_node_id() -> None:
    """Their node IDs are pinned so a rename or a deletion cannot pass as a repair."""
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header",
         "-p", "no:cacheprovider",
         "tests/test_lattice_bond_stage_b.py", "tests/test_motile_polar.py"],
        cwd=_REPO_ROOT, capture_output=True, text=True, check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    collected = {line.strip() for line in completed.stdout.splitlines() if "::" in line}
    for node in INHERITED_FAILURES:
        assert node in collected, node


def test_collection_14_the_selected_node_set_is_unchanged() -> None:
    """This mission adds no test to any of the four bound selectors."""
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header",
         "-p", "no:cacheprovider", *SELECTORS],
        cwd=_REPO_ROOT, capture_output=True, text=True, check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    collected = sorted(
        line.strip()
        for line in completed.stdout.splitlines()
        if "::" in line and line.strip().startswith("tests/")
    )
    assert len(collected) == SELECTED_NODE_COUNT
    digest = hashlib.sha256("\n".join(collected).encode("utf-8")).hexdigest()
    assert digest == SELECTED_NODE_LIST_SHA256


def test_collection_14b_this_file_is_not_one_of_the_selectors() -> None:
    assert Path(__file__).name not in {Path(item).name for item in SELECTORS}


# --------------------------------------------------------------------------------------
# the literal pin of the current-source qualification record
#
# The record is written BEFORE this block, so its own bytes are final when the digest
# below is taken.  The digest is LITERAL: it is never recomputed from the file, never
# wildcarded, never a prefix, and there is no "latest record found" discovery anywhere.
# Reading this file's digest from inside this file would be a cycle; exactly as the
# accepted 01R record does for its own selector, that one value is verified out of band
# and recorded in the mission REPORT.
# --------------------------------------------------------------------------------------

CURRENT_SOURCE_QUALIFICATION = (
    "docs/individuation/FUTURE_ROUTE_E_EXECUTION_BOUNDARY_CORRECTION_00_"
    "CURRENT_SOURCE_QUALIFICATION.json"
)
CURRENT_SOURCE_QUALIFICATION_SHA256 = (
    "ae43faa0518e67fdf0ae94245ac0ecd2c2fee404d56e9cbc0a65c8ce2bb045dd"
)


def test_record_01_the_current_source_record_is_byte_identical() -> None:
    payload = (_REPO_ROOT / CURRENT_SOURCE_QUALIFICATION).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == CURRENT_SOURCE_QUALIFICATION_SHA256


def test_record_02_the_record_binds_the_current_source_bytes() -> None:
    record = json.loads((_REPO_ROOT / CURRENT_SOURCE_QUALIFICATION).read_text("utf-8"))
    bound = record["current_source_bound_by_this_mission"]
    assert set(bound) == {
        "edlab/route_e_protocol.py",
        "edlab/substrates/lattice_bond/future_route_e_world_evidence.py",
        "edlab/substrates/lattice_bond/future_route_e_execution.py",
        "edlab/substrates/lattice_bond/future_route_e_admission.py",
    }
    for relative, entry in bound.items():
        payload = (_REPO_ROOT / relative).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"], relative
        assert len(payload) == entry["bytes"], relative
        assert entry["source_changed_by_this_mission"] is True


def test_record_03_the_record_does_not_accept_itself() -> None:
    record = json.loads((_REPO_ROOT / CURRENT_SOURCE_QUALIFICATION).read_text("utf-8"))
    assert record["human_review"] == "PENDING"
    assert record["self_accepting"] is False
    assert record["scientific_run_authorized"] is False
    assert record["pilot_authorized"] is False
    assert record["preregistration_authorized"] is False
    assert record["public_pre_run_inclusion_proven"] is False
    assert record["historical_qualifications_byte_identical"]["files_modified"] == 0
    assert record["selected_node_binding_unchanged"]["node_count"] == SELECTED_NODE_COUNT
    assert (
        record["selected_node_binding_unchanged"]["node_list_sha256"]
        == SELECTED_NODE_LIST_SHA256
    )
    assert record["owner_decisions_applied"]["UNIVERSAL_ENGINE_EXECUTION_PREVENTION"] == "NOT_CLAIMED"
