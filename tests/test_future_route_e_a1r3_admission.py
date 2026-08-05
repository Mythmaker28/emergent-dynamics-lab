"""A1-R3 admission tests.

Every negative fixture below is SELF-COHERENT AND RESEALED: the manifest, the anteriority
proof, the enrolment, the attempt inventory, the file inventory, the envelope and the
receipt are all recomputed after the injected defect.  A1-R2's tests edited a file and left
the envelope stale, so they proved only that a stale envelope is detected -- which no
attacker would ever produce.

NOTHING HERE RUNS A SCIENTIFIC CAMPAIGN.  No engine step is taken, no law is drawn from the
frozen family, no seed of a scientific namespace is created.  The worlds are hand-written
6x6 fixtures whose fixture_class is SYNTHETIC_NON_SCIENTIFIC, and the admission refuses to
let them contribute to any dataset.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pytest

from edlab import route_e_protocol as protocol
from edlab.substrates.lattice_bond import future_route_e_admission as admission
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_world_evidence as evidence
from edlab.substrates.lattice_bond.future_prospective_measurement_bridge import MeasurementSpec

REPO_ROOT = Path(__file__).resolve().parents[1]
SHAPE = (6, 6)
FRAMES = (0, 16, 32)
SPEC = MeasurementSpec(min_cells=1)


# --------------------------------------------------------------------------------------
# fixture construction
# --------------------------------------------------------------------------------------


def _sha(payload: bytes) -> str:
    import hashlib

    return hashlib.sha256(payload).hexdigest()


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _blob_mask(present: bool) -> np.ndarray:
    mask = np.zeros(SHAPE, dtype=bool)
    if present:
        mask[2:4, 2:4] = True
    return mask


def _make_world(
    directory: Path, *, residual: float, survives: bool = True, wrapping: bool = False
) -> None:
    """A hand-written world.  ``residual`` fixes cohort_mass / mass at the last frame."""
    directory.mkdir(parents=True, exist_ok=True)
    for position, _label in enumerate(FRAMES):
        last = position == len(FRAMES) - 1
        mask = _blob_mask(present=survives or not last)
        if wrapping:
            mask = np.zeros(SHAPE, dtype=bool)
            mask[3, :] = True  # a full row wraps the torus in x
        matter = np.where(mask, 0.9, 0.05).astype(np.float64)
        # A1-R5 enrolment invariant: at the first sampled frame the tracer equals the
        # matter inside the enrolled union and is zero outside, so residual(t0) == 1.
        # The residual then falls to `residual` by the horizon: a real replacement history.
        share = 1.0 if position == 0 else (
            1.0 + (residual - 1.0) * position / float(len(FRAMES) - 1)
        )
        tracer = np.where(mask, 0.9 * share, 0.0).astype(np.float64)
        for channel, array in (
            ("mask", mask),
            ("matter", matter),
            ("tracer", tracer),
            ("resource", np.full(SHAPE, 0.5)),
            ("bond", np.zeros(SHAPE)),
        ):
            if channel == "mask":
                payload = np.ascontiguousarray(array, dtype=np.bool_).astype(np.uint8).tobytes()
            else:
                payload = np.ascontiguousarray(array, dtype="<f8").tobytes()
            _write(
                directory / "measurement_frames" / f"frame_{position:06d}_{channel}.bin", payload
            )
    join = evidence.build_join_document(
        directory,
        sampled_frames=FRAMES,
        frame_shape=SHAPE,
        detector=SPEC.detector_spec(),
        tracker=SPEC.tracker_spec(),
        horizon_steps=32,
        cadence_steps=16,
    )
    _write(directory / "TRACK_COMPONENT_JOIN.json", protocol.canonical_bytes(join))
    measurement = {
        "frame_shape": [SHAPE[0], SHAPE[1]],
        "measurement_root_sha256": _sha(b"synthetic-measurement-root"),
    }
    _write(directory / "MEASUREMENT.json", protocol.canonical_bytes(measurement))
    _write(
        directory / "BRIDGE_BINDING.json",
        protocol.canonical_bytes(
            {"measurement_root_sha256": measurement["measurement_root_sha256"]}
        ),
    )
    _write(directory / "LIFECYCLE.json", protocol.canonical_bytes({"terminal_records": []}))


def _bound_source_digests() -> dict[str, str]:
    """Real files, real digests.  A fixture that binds nothing proves nothing."""
    targets = [
        "edlab/route_e_protocol.py",
        "edlab/substrates/lattice_bond/future_route_e_admission.py",
    ]
    return {name: _sha((REPO_ROOT / name).read_bytes()) for name in targets}


def build_root(
    tmp_path: Path,
    *,
    n_draws: int = 1,
    ics: int = 2,
    mode: str = "EXPLORATORY_PILOT",
    proof_type: str = "SELF_ATTESTED_NON_PUBLIC",
    public_claim: bool = False,
    provenance_tag: str | None = None,
    source_digest_override: dict[str, str] | None = None,
    manifest_extra: dict | None = None,
    residuals: list[float] | None = None,
    drop_measurement: bool = False,
    corrupt_join: bool = False,
) -> Path:
    """A complete, canonical, RESEALED Route E root with synthetic worlds."""
    root = tmp_path / "root"
    root.mkdir()
    worlds = n_draws * ics
    digests = source_digest_override or _bound_source_digests()
    manifest = {
        "canonical_cutoff_C": 1_800_000_000,
        "crash_retry_and_attempt_policy": {"retries": 0, "every_attempt_recorded": True},
        "designated_round_rule": dict(execution.DESIGNATED_ROUND_RULE),
        "distributions_and_draw_algorithm": {"cadence_steps": 16, "horizon_steps": 32},
        "experiment_id": "A1R3-SYNTHETIC-FIXTURE",
        "fixture_class": "SYNTHETIC_NON_SCIENTIFIC",
        "kind": protocol.PRE_RUN_KIND,
        "mode": mode,
        "outcome_and_claim_ceiling": {"level": "draw"},
        "output_namespace": "SYNTHETIC-NONSCI-A1R3",
        "protocol_and_analysis_digests": {"digests": digests},
        "run_identity": "a1r3-synthetic-fixture",
        "sample_size_and_world_policy": {
            "initial_conditions_per_law": ics,
            "n_draws": n_draws,
            "worlds": worlds,
        },
        "schema_version": "route-e-pre-run/v1",
        "source_commit_and_digests": {"commit": "0" * 40, "digests": digests},
    }
    if manifest_extra:
        manifest.update(manifest_extra)
    manifest_bytes = protocol.canonical_bytes(manifest)
    pre_run_root = _sha(protocol.PRE_RUN_DOMAIN + manifest_bytes)

    _write(
        root / "ROUTE_E_PROVENANCE.json",
        protocol.canonical_bytes(
            {
                "execution_version": execution.EXECUTION_VERSION,
                "kind": protocol.PROVENANCE_KIND,
                "pre_run_root": pre_run_root,
                "tag": provenance_tag or protocol.ROUTE_E_PROVENANCE_TAG,
            }
        ),
    )
    _write(root / "PRE_RUN_MANIFEST.json", manifest_bytes)
    _write(
        root / "PRE_RUN_ANTERIORITY.json",
        protocol.canonical_bytes(
            {
                "binds_cutoff_C": manifest["canonical_cutoff_C"],
                "binds_pre_run_root": pre_run_root,
                "kind": protocol.ANTERIORITY_KIND,
                "proof_type": proof_type,
                "public_registry_inclusion_proven": public_claim,
            }
        ),
    )
    _write(
        root / "BEACON_RESPONSE.json",
        protocol.canonical_bytes({"round": 1, "randomness": "ab" * 32, "signature": "cd" * 48}),
    )
    residual_values = residuals or [0.001] * worlds
    for ordinal in range(worlds):
        world = root / "worlds" / f"{ordinal:06d}"
        _make_world(world, residual=residual_values[ordinal])
        if drop_measurement and ordinal == 0:
            (world / "MEASUREMENT.json").unlink()
        if corrupt_join and ordinal == 0:
            document = json.loads((world / "TRACK_COMPONENT_JOIN.json").read_bytes())
            document["assignments"] = []
            (world / "TRACK_COMPONENT_JOIN.json").write_bytes(
                protocol.canonical_bytes(document)
            )
    return root


# --------------------------------------------------------------------------------------
# GROUP A -- pre-beacon refusals, end to end through the public API
# --------------------------------------------------------------------------------------


def test_a01_a_canonical_tag_with_a_non_canonical_producer_is_refused(tmp_path):
    root = build_root(tmp_path, provenance_tag="SOMEONE_ELSES_RUNNER/v9")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_CANONICAL_ROUTE_E_ROOT"


def test_a02_an_unknown_anteriority_proof_type_is_refused(tmp_path):
    root = build_root(tmp_path, proof_type="TOTALLY_NEW_SCHEME")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "ANTERIORITY_REFUSED"
    assert "unknown anteriority proof type" in verdict.reason


def test_a03_public_true_without_a_proof_that_can_prove_it_is_refused(tmp_path):
    root = build_root(tmp_path, proof_type="SELF_ATTESTED_NON_PUBLIC", public_claim=True)
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "ANTERIORITY_REFUSED"
    assert verdict.public_registry_inclusion_proven is False


def test_a04_ots_plus_rfc3161_stays_refused_until_a2(tmp_path):
    root = build_root(tmp_path, proof_type="OTS_PLUS_RFC3161", public_claim=True)
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "ANTERIORITY_REFUSED"
    assert "NOT implemented" in verdict.reason


def test_a05_a_confirmatory_run_that_is_not_67_over_134_is_refused(tmp_path):
    root = build_root(tmp_path, n_draws=1, ics=1, mode="CONFIRMATORY_67")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "CONFIRMATORY_SHAPE_REFUSED"
    assert "frozen at n_draws=67" in verdict.reason


def test_a06_a_confirmatory_run_declaring_134_primary_units_is_refused(tmp_path):
    root = build_root(tmp_path, n_draws=134, ics=1, mode="CONFIRMATORY_67")
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "CONFIRMATORY_SHAPE_REFUSED"


def test_a07_a_source_that_truly_diverges_from_its_published_digest_is_refused(tmp_path):
    root = build_root(
        tmp_path, source_digest_override={"edlab/route_e_protocol.py": "f" * 64}
    )
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "SOURCE_DIVERGENT"
    assert verdict.source_bytes_bound is False


def test_a08_a_declared_source_absent_from_the_running_tree_is_refused(tmp_path):
    root = build_root(
        tmp_path, source_digest_override={"edlab/not_a_real_module.py": "a" * 64}
    )
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "SOURCE_ABSENT"


def test_a09_a_manifest_with_an_extra_key_is_refused(tmp_path):
    root = build_root(tmp_path, manifest_extra={"convenient_extra": 1})
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "MANIFEST_SCHEMA"
    assert "extra=['convenient_extra']" in verdict.reason


def test_a10_malformed_json_becomes_a_verdict_never_a_crash(tmp_path):
    root = build_root(tmp_path)
    (root / "PRE_RUN_MANIFEST.json").write_bytes(b'{"kind": "route-e-pre')
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "MANIFEST_UNREADABLE"


def test_a11_a_missing_root_is_a_verdict_never_an_exception(tmp_path):
    verdict = admission.verify_route_e_run(tmp_path / "nowhere")
    assert verdict.admissible is False
    assert verdict.reason_code == "NOT_A_DIRECTORY"


@pytest.mark.parametrize(
    "payload", [b"", b"[]", b"null", b'{"kind":"x"}', b'{ "kind" : "x" }']
)
def test_a12_no_bare_exception_escapes_the_api(tmp_path, payload):
    root = build_root(tmp_path)
    (root / "ROUTE_E_PROVENANCE.json").write_bytes(payload)
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code != "ADMISSION_INTERNAL_ERROR"


# --------------------------------------------------------------------------------------
# GROUP B -- the beacon is re-verified, fail-closed
# --------------------------------------------------------------------------------------


def test_b01_an_unavailable_pinned_verifier_is_a_stop_never_a_pass(tmp_path, monkeypatch):
    monkeypatch.delenv("ROUTE_E_DRAND_VERIFY", raising=False)
    root = build_root(tmp_path)
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "VERIFIER_UNAVAILABLE"
    assert verdict.beacon_reverified is False
    # and the SOURCE binding did succeed before it, so this is a beacon stop, not an
    # accidental earlier refusal
    assert verdict.source_bytes_bound is True


def test_b02_an_unpinned_binary_is_not_a_verifier(tmp_path, monkeypatch):
    fake = tmp_path / "fake_verify"
    fake.write_bytes(b"#!/bin/sh\necho '{\"outcome\":\"verified\"}'\n")
    fake.chmod(0o755)
    monkeypatch.setenv("ROUTE_E_DRAND_VERIFY", str(fake))
    root = build_root(tmp_path)
    verdict = admission.verify_route_e_run(root)
    assert verdict.admissible is False
    assert verdict.reason_code == "VERIFIER_UNAVAILABLE"


def test_b03_the_admission_never_reads_a_boolean_for_public_inclusion(tmp_path):
    for claim in (True, False):
        base = tmp_path / f"c{claim}"
        base.mkdir()
        root = build_root(base, public_claim=claim)
        verdict = admission.verify_route_e_run(root)
        assert verdict.public_registry_inclusion_proven is False


# --------------------------------------------------------------------------------------
# GROUP C -- the per-world scientific proof
# --------------------------------------------------------------------------------------


def _outcome(world: Path):
    return evidence.derive_world_outcome(
        world,
        sampled_frames=FRAMES,
        frame_shape=SHAPE,
        detector=SPEC.detector_spec(),
        tracker=SPEC.tracker_spec(),
    )


def test_c01_a_genuine_synthetic_world_reaches_Y_equals_one(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.001)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert result.eligible_track_ids
    assert result.Y_by_f["0.01"] == 1
    assert result.disposition_by_f["0.01"] == "SUCCESS"


def test_c02_a_survivor_without_verified_replacement_is_Y_zero_not_unknown(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.9)
    result = _outcome(world)
    assert result.persisted_to_horizon is True
    assert result.Y_by_f["0.2"] == 0
    assert result.Y_by_f["0.2"] is not None
    assert result.disposition_by_f["0.2"] == "OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT"
    assert "TECHNICALLY_UNKNOWN" not in set(result.disposition_by_f.values())


def test_c03_the_three_conventions_give_distinct_results(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.10)  # 0.01 < 0.10 <= 0.20
    result = _outcome(world)
    assert result.Y_by_f["0.01"] == 0
    assert result.Y_by_f["0.05"] == 0
    assert result.Y_by_f["0.2"] == 1
    assert len(set(result.Y_by_f.values())) == 2, "the three f must not be merged"


def test_c04_a_wrapping_component_makes_the_whole_world_mechanically_ineligible(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.0, wrapping=True)
    result = _outcome(world)
    assert result.any_wrapping_component is True
    assert result.mechanically_ineligible is True
    assert set(result.Y_by_f.values()) == {0}


def test_c05_a_dissolving_world_never_reaches_the_horizon(tmp_path):
    world = tmp_path / "w"
    _make_world(world, residual=0.0, survives=False)
    result = _outcome(world)
    assert result.persisted_to_horizon is False
    assert set(result.Y_by_f.values()) == {0}


def test_c06_an_incoherent_join_is_refused(tmp_path):
    root = build_root(tmp_path, corrupt_join=True)
    world = root / "worlds" / "000000"
    attempt = {
        "attempt_ordinal": 0, "law_index": 0, "ic_ordinal": 0, "status": "SUCCESS",
        "world_relative_path": "worlds/000000",
        "measurement_root_sha256": json.loads((world / "MEASUREMENT.json").read_bytes())[
            "measurement_root_sha256"
        ],
        "lifecycle_document_sha256": _sha((world / "LIFECYCLE.json").read_bytes()),
    }
    with pytest.raises(protocol.ProtocolRefusal) as excinfo:
        admission._verify_world(
            root, attempt, detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
            sampled_frames=FRAMES,
        )
    assert excinfo.value.reason_code == "JOIN_INCOHERENT"


def test_c07_a_success_world_without_a_measurement_document_is_refused(tmp_path):
    root = build_root(tmp_path, drop_measurement=True)
    attempt = {
        "attempt_ordinal": 0, "law_index": 0, "ic_ordinal": 0, "status": "SUCCESS",
        "world_relative_path": "worlds/000000",
        "measurement_root_sha256": "0" * 64, "lifecycle_document_sha256": "0" * 64,
    }
    with pytest.raises(protocol.ProtocolRefusal) as excinfo:
        admission._verify_world(
            root, attempt, detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
            sampled_frames=FRAMES,
        )
    assert excinfo.value.reason_code == "EVIDENCE_MISSING"


def test_c08_an_incoherent_measurement_root_is_refused(tmp_path):
    root = build_root(tmp_path)
    attempt = {
        "attempt_ordinal": 0, "law_index": 0, "ic_ordinal": 0, "status": "SUCCESS",
        "world_relative_path": "worlds/000000",
        "measurement_root_sha256": "1" * 64, "lifecycle_document_sha256": "0" * 64,
    }
    with pytest.raises(protocol.ProtocolRefusal) as excinfo:
        admission._verify_world(
            root, attempt, detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
            sampled_frames=FRAMES,
        )
    assert excinfo.value.reason_code == "MEASUREMENT_ROOT_MISMATCH"


def test_c09_a_technical_incident_is_unknown_and_stays_in_the_denominator(tmp_path):
    root = build_root(tmp_path)
    attempt = {
        "attempt_ordinal": 0, "law_index": 0, "ic_ordinal": 0, "status": "CRASH",
        "world_relative_path": "worlds/000000",
    }
    outcome = admission._verify_world(
        root, attempt, detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
        sampled_frames=FRAMES,
    )
    assert set(outcome.Y_by_f.values()) == {None}
    assert set(outcome.disposition_by_f.values()) == {"TECHNICALLY_UNKNOWN"}


# --------------------------------------------------------------------------------------
# GROUP D -- the statistical unit
# --------------------------------------------------------------------------------------


def test_d01_the_frozen_confirmatory_shape_is_67_over_134(tmp_path):
    assert protocol.CONFIRMATORY_CONSTRAINTS == {
        "n_draws": 67, "initial_conditions_per_law": 2, "worlds": 134
    }
    protocol.check_confirmatory_constraints(
        mode="CONFIRMATORY_67", n_draws=67, worlds=134, ics_per_law=2, code="X"
    )


@pytest.mark.parametrize(
    "n_draws,worlds,ics", [(134, 134, 1), (67, 67, 1), (134, 268, 2), (66, 132, 2)]
)
def test_d02_no_other_confirmatory_shape_is_accepted(n_draws, worlds, ics):
    with pytest.raises(protocol.ProtocolRefusal):
        protocol.check_confirmatory_constraints(
            mode="CONFIRMATORY_67", n_draws=n_draws, worlds=worlds, ics_per_law=ics, code="X"
        )


def test_d03_worlds_must_equal_n_draws_times_ics(tmp_path):
    with pytest.raises(protocol.ProtocolRefusal):
        protocol.check_confirmatory_constraints(
            mode="EXPLORATORY_PILOT", n_draws=10, worlds=15, ics_per_law=2, code="X"
        )


def test_d04_the_second_initial_condition_is_never_a_term_of_k(tmp_path):
    """k sums PRIMARY units only.  The partner drives psi and nothing else."""
    root = build_root(tmp_path, n_draws=2, ics=2, residuals=[0.001, 0.9, 0.001, 0.001])
    outcomes = []
    for ordinal in range(4):
        law, ic = divmod(ordinal, 2)
        attempt = {
            "attempt_ordinal": ordinal, "law_index": law, "ic_ordinal": ic,
            "status": "SUCCESS", "world_relative_path": f"worlds/{ordinal:06d}",
            "measurement_root_sha256": json.loads(
                (root / "worlds" / f"{ordinal:06d}" / "MEASUREMENT.json").read_bytes()
            )["measurement_root_sha256"],
            "lifecycle_document_sha256": _sha(
                (root / "worlds" / f"{ordinal:06d}" / "LIFECYCLE.json").read_bytes()
            ),
        }
        outcomes.append(
            admission._verify_world(
                root, attempt, detector=SPEC.detector_spec(), tracker=SPEC.tracker_spec(),
                sampled_frames=FRAMES,
            )
        )
    primaries = [item for item in outcomes if item.is_primary]
    assert len(primaries) == 2, "one primary per law, never one per world"
    k = sum(int(item.Y_by_f["0.01"]) for item in primaries)
    assert k == 2
    # law 0's partner disagrees at f=0.01 (residual 0.9), law 1's agrees
    secondaries = {item.law_index: item for item in outcomes if not item.is_primary}
    discordant = sum(
        int(item.Y_by_f["0.01"] != secondaries[item.law_index].Y_by_f["0.01"])
        for item in primaries
    )
    assert discordant == 1
    assert discordant / 2 == 0.5  # psi


# --------------------------------------------------------------------------------------
# GROUP E -- the frozen initial-condition law
# --------------------------------------------------------------------------------------


def test_e01_the_resource_field_is_not_constant(tmp_path):
    state = execution._initial_state(b"\x11" * 32, 0, 8)
    assert float(state.n.std()) > 0.05, "n must be U[0,1] i.i.d., never a constant"
    assert not np.allclose(state.n, 0.8)


def test_e02_m_and_n_come_from_separate_domains(tmp_path):
    state = execution._initial_state(b"\x11" * 32, 0, 8)
    assert not np.array_equal(state.m, state.n)
    assert float(np.max(np.abs(np.corrcoef(state.m.ravel(), state.n.ravel())[0, 1]))) < 0.6


def test_e03_both_fields_are_in_the_unit_interval_and_bonds_are_zero(tmp_path):
    state = execution._initial_state(b"\x22" * 32, 3, 8)
    for field in (state.m, state.n):
        assert float(field.min()) >= 0.0 and float(field.max()) <= 1.0
    assert float(np.max(np.abs(state.b))) == 0.0


def test_e04_the_law_is_deterministic_in_the_seed_root(tmp_path):
    a = execution._initial_state(b"\x33" * 32, 1, 6)
    b = execution._initial_state(b"\x33" * 32, 1, 6)
    assert np.array_equal(a.m, b.m) and np.array_equal(a.n, b.n)
    c = execution._initial_state(b"\x34" * 32, 1, 6)
    assert not np.array_equal(a.m, c.m)


def test_e05_no_numpy_rng_or_random_module_is_used_for_the_initial_condition():
    source = (
        REPO_ROOT / "edlab" / "substrates" / "lattice_bond" / "future_route_e_execution.py"
    ).read_text()
    body = source.split("def _uniform_field")[1].split("def _schedule")[0]
    for forbidden in ("np.random", "default_rng", "random.", "import random"):
        assert forbidden not in body


# --------------------------------------------------------------------------------------
# GROUP F -- independence, established at RUNTIME in a fresh interpreter
# --------------------------------------------------------------------------------------


def test_f01_the_protocol_module_itself_loads_no_simulator_and_no_numpy():
    """Loaded standalone, the protocol module pulls in neither NumPy nor any substrate.

    DECLARED LIMITATION, tested below rather than hidden: importing it through the package
    (``import edlab.route_e_protocol``) DOES load NumPy, because ``edlab/__init__.py``
    imports ``.specs`` and ``.state``.  That is a property of the package root, which is a
    protected historical source this mission does not touch.  The module itself is clean.
    """
    script = textwrap.dedent(
        """
        import importlib.util, sys, json
        spec = importlib.util.spec_from_file_location(
            "route_e_protocol_standalone", "edlab/route_e_protocol.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded = sorted(m for m in sys.modules if "lattice_bond" in m or m == "numpy")
        print(json.dumps(loaded))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=str(REPO_ROOT), capture_output=True, text=True,
        check=True,
    )
    assert json.loads(completed.stdout.strip()) == []


def test_f01b_the_package_root_is_the_only_reason_numpy_appears():
    script = textwrap.dedent(
        """
        import sys, json
        import edlab.route_e_protocol  # noqa: F401
        print(json.dumps(sorted(m for m in sys.modules if "lattice_bond" in m)))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=str(REPO_ROOT), capture_output=True, text=True,
        check=True,
    )
    assert json.loads(completed.stdout.strip()) == [], "no substrate module is ever loaded"


def test_f02_no_engine_is_instantiated_and_no_step_is_taken_during_admission(tmp_path):
    """The runtime claim, proved by instrumentation in a FRESH subprocess.

    Not a string search: ``LatticeBondEngine.__init__`` and ``.step`` are replaced with
    raising stubs, so any construction or step during admission is a hard failure.
    """
    root = build_root(tmp_path)
    script = textwrap.dedent(
        f"""
        import json, sys
        from edlab.substrates.lattice_bond import engine as E

        calls = {{"init": 0, "step": 0}}
        def _init(self, *a, **k):
            calls["init"] += 1
            raise AssertionError("LatticeBondEngine was instantiated during admission")
        def _step(self, *a, **k):
            calls["step"] += 1
            raise AssertionError("a simulation step was taken during admission")
        E.LatticeBondEngine.__init__ = _init
        E.LatticeBondEngine.step = _step

        from edlab.substrates.lattice_bond import future_route_e_admission as A
        verdict = A.verify_route_e_run({str(root)!r})
        print(json.dumps({{
            "code": verdict.reason_code,
            "engine_steps": verdict.engine_steps_taken,
            "calls": calls,
        }}))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout.strip())
    assert payload["calls"] == {"init": 0, "step": 0}
    assert payload["engine_steps"] == 0


def test_f03_admission_mutates_nothing_in_the_output_tree(tmp_path):
    root = build_root(tmp_path)
    before = {
        path.relative_to(root).as_posix(): _sha(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    admission.verify_route_e_run(root)
    after = {
        path.relative_to(root).as_posix(): _sha(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    assert before == after


def test_f04_the_admission_reuses_no_private_helper_of_the_producer():
    source = (
        REPO_ROOT / "edlab" / "substrates" / "lattice_bond" / "future_route_e_admission.py"
    ).read_text()
    import ast

    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.extend(f"{node.module or ''}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
    assert not any("future_route_e_execution" in name for name in imported), imported
    assert "_execution." not in source.split('"""', 2)[-1]


def test_f05_the_two_modules_agree_on_the_domain_separation_bytes():
    assert protocol.PRE_RUN_DOMAIN == execution.PRE_RUN_DOMAIN
    assert protocol.POST_RUN_DOMAIN == execution.POST_RUN_DOMAIN
    assert protocol.SEED_DOMAIN == execution.SEED_DOMAIN


# --------------------------------------------------------------------------------------
# GROUP G -- concurrency
# --------------------------------------------------------------------------------------


def test_g01_no_clobber_write_is_exclusive_not_merely_atomic(tmp_path):
    target = tmp_path / "once.json"
    digest = protocol.no_clobber_write(target, b"first")
    assert digest == _sha(b"first")
    with pytest.raises(FileExistsError):
        protocol.no_clobber_write(target, b"second")
    assert target.read_bytes() == b"first", "first-write-wins, and the loser never overwrites"


def test_g02_the_producer_refuses_rather_than_replacing(tmp_path):
    target = tmp_path / "once.json"
    target.write_bytes(b"incumbent")
    with pytest.raises(execution.RouteEExecutionRefused) as excinfo:
        execution._write_exact(target, b"challenger")
    assert "nothing is ever replaced" in str(excinfo.value)
    assert target.read_bytes() == b"incumbent"


def test_g03_there_is_no_exists_then_replace_window_left(tmp_path):
    source = (
        REPO_ROOT / "edlab" / "substrates" / "lattice_bond" / "future_route_e_execution.py"
    ).read_text()
    body = source.split("def _write_exact")[1].split("def _law_spec_from_fields")[0]
    code = body.split('"""')[2]  # drop the signature and the docstring; keep the code
    assert "os.replace" not in code
    assert "path.exists()" not in code
    assert "no_clobber_write" in code


# --------------------------------------------------------------------------------------
# GROUP H -- the A2 rule is stated and NOT modified
# --------------------------------------------------------------------------------------


def test_h01_the_frozen_a2_rule_is_recorded_verbatim_and_refused():
    entry = protocol.ANTERIORITY_PROOF_TYPES["OTS_PLUS_RFC3161"]
    assert entry["implemented"] is False
    note = entry["note"]
    assert "COMPLETE OpenTimestamps proof on Bitcoin mainnet" in note
    assert "RFC 3161 token from the Sigstore TSA" in note
    assert "Rekor, GitHub, Zenodo and integratedTime replace" in note
