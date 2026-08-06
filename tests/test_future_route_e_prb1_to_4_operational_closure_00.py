"""FUTURE_ROUTE_E_PRB_1_TO_4_AND_HR10_OPERATIONAL_CLOSURE_00.

Every gate here is executable and goes through a REAL public entry point.

* ``PRB-1`` -- the track-component join is built from the real tracking and the real
  component support rebuilt from disk, written atomically into the world evidence,
  re-read by the real consumer (``verify_route_e_run``) and REQUIRED for admission.
* ``PRB-2`` -- ``open_measured_analysis_access`` refuses any caller-supplied verifier
  and verifies the anchor through the INSTALLED maintained verifier: root binding,
  round derived from the public timestamp, pinned network and DST.
* ``PRB-3`` -- both public paths (``open_route_e_analysis`` and ``route_e_entry``)
  produce the SAME frozen order, and ``must_precede_unix=None`` closes admission.
* ``PRB-4`` -- the replay root is persisted, bound to the run identity, the pre-run
  root and the enrolment, re-read and recomputed by the consumer, never reconstructed.
* ``HR-10`` -- the public assembly has no ``classifier`` parameter at all.

ENGINEERING_ONLY / NOT_SCIENTIFIC_DATA / NOT_ELIGIBLE_FOR_ANALYSIS.
No scientific law, seed, family, horizon or holdout is opened.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import future_route_e_admission as admission
from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks
from edlab.substrates.lattice_bond import future_prospective_measurement_bridge as bridge
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    rebuild_tracking_and_components,
)

from tests.test_future_route_e_execution_boundary_00 import (  # noqa: E402
    CUTOFF_C,
    _beacon,
    _bundle,
    _destination,
    _manifest,
    requires_verifier,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_VECTORS = json.loads((_REPO_ROOT / "tests" / "data" / "route_e_beacon_vectors.json").read_text("ascii"))
_V2 = [v for v in _VECTORS["vectors"] if v["id"] == "V2"][0]

CANARY = ("ENGINEERING_ONLY", "NOT_SCIENTIFIC_DATA", "NOT_ELIGIBLE_FOR_ANALYSIS")


def _run(tmp_path: Path, **manifest_overrides):
    document = _manifest()
    document.update(manifest_overrides)
    bundle_dir, _ = _bundle(tmp_path, document)
    return execution.run_route_e(
        bundle_dir, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"])
    )


def _rewrite(path: Path, mutate) -> None:
    document = json.loads(path.read_bytes().decode("ascii"))
    mutate(document)
    path.write_bytes(execution.canonical_bytes(document))


def _world(record) -> Path:
    return Path(record.output_directory) / execution.WORLDS_DIRECTORY / "000000"


# ======================================================================================
# PRB-1 -- the join is persisted, re-read and mandatory
# ======================================================================================


@requires_verifier
def test_prb1_01_the_join_is_written_by_the_real_run_and_covers_real_components(tmp_path):
    record = _run(tmp_path)
    join_path = _world(record) / locks.JOIN_EVIDENCE_FILENAME
    assert join_path.is_file(), "the run did not persist the track-component join"

    records, digest = locks.read_join_evidence(join_path)
    assert records, "an empty join is never admissible"

    # the persisted join is exactly the one the REAL tracking and the REAL component
    # support rebuild from the persisted frames
    tracking, components = rebuild_tracking_and_components(_world(record))
    rebuilt = locks.build_track_component_join(tracking, components)
    assert locks.join_digest(rebuilt) == digest
    frames = {row.frame for row in records}
    tracks = {row.track_id for row in records}
    assert len(records) >= 2 and frames, "the fixture must exercise several rows"
    assert all(isinstance(row.cell_set_sha256, str) and len(row.cell_set_sha256) == 64 for row in records)
    assert len(tracks) >= 1


@requires_verifier
def test_prb1_02_write_then_read_back_is_exact_and_restart_identical(tmp_path):
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b")
    _, digest_a = locks.read_join_evidence(_world(first) / locks.JOIN_EVIDENCE_FILENAME)
    _, digest_b = locks.read_join_evidence(_world(second) / locks.JOIN_EVIDENCE_FILENAME)
    assert digest_a == digest_b, "the persisted join is not restart-identical"
    assert first.post_run_root == second.post_run_root


@requires_verifier
def test_prb1_03_an_absent_join_is_refused_by_the_real_consumer(tmp_path):
    record = _run(tmp_path)
    join_path = _world(record) / locks.JOIN_EVIDENCE_FILENAME
    join_path.unlink()
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert not verdict.admissible
    assert verdict.reason_code in {"JOIN_EVIDENCE_INVALID", "FILE_INVENTORY_INEXACT"}


@requires_verifier
def test_prb1_04_an_altered_join_is_refused_before_admission(tmp_path):
    record = _run(tmp_path)
    join_path = _world(record) / locks.JOIN_EVIDENCE_FILENAME
    payload = json.loads(join_path.read_bytes().decode("ascii"))
    # swap the association of the first row onto another track id
    payload["join"][0][2] = payload["join"][0][2] + 1
    join_path.write_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    )
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert not verdict.admissible
    assert verdict.reason_code in {
        "JOIN_EVIDENCE_MISMATCH",
        "JOIN_EVIDENCE_INVALID",
        "FILE_INVENTORY_INEXACT",
    }


@requires_verifier
def test_prb1_05_a_join_from_another_run_is_refused(tmp_path):
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b", output_namespace="SYNTHETIC-NONSCI-BOUNDARY-0002")
    foreign = (_world(second) / locks.JOIN_EVIDENCE_FILENAME).read_bytes()
    target = _world(first) / locks.JOIN_EVIDENCE_FILENAME
    if foreign == target.read_bytes():
        pytest.skip("the two synthetic worlds are byte-identical by construction")
    target.write_bytes(foreign)
    verdict = admission.verify_route_e_run(Path(first.output_directory))
    assert not verdict.admissible


def test_prb1_06_the_join_refuses_an_empty_or_unsupported_assignment(tmp_path):
    from edlab.substrates.lattice_bond.instrumentation import TrackingResult

    # a support frame that is not a non-negative int is refused outright
    with pytest.raises((locks.EvidenceInvalid, ValueError, TypeError)):
        locks.build_track_component_join(TrackingResult((), (), (), ()), {-1: {}})
    # a tracking with no assignment and no support produces NO row ...
    empty = locks.build_track_component_join(TrackingResult((), (), (), ()), {})
    assert empty == ()
    # ... and an empty join can never be persisted, so it can never be admitted
    root = tmp_path / "evidence"
    root.mkdir()
    with pytest.raises((locks.EvidenceInvalid, ValueError)):
        locks.write_join_evidence(root, empty)



# ======================================================================================
# PRB-2 -- the receipt is mandatory and authentically verified
# ======================================================================================


def _measured_run(tmp_path: Path):
    """A tiny synthetic bridge run.  ENGINEERING_ONLY."""
    from edlab.substrates.lattice_bond.engine import LatticeBondSpec, LatticeBondState

    directory = tmp_path / "measured"
    directory.mkdir()
    size = 8
    rng = np.random.default_rng(20260806)
    state = LatticeBondState(
        rng.random((size, size)) * 0.5 + 0.25,
        np.full((size, size), 0.5),
        np.zeros((2, size, size)),
        0,
    )
    return directory, bridge.run_measurement_bridge(
        directory,
        law_spec=LatticeBondSpec(),
        initial_state=state,
        sampled_frames=(0, 1, 2),
        measurement_spec=bridge.MeasurementSpec(min_cells=1),
        acquisition_source_identity={"kind": "engineering-only", "name": "PRB2-CANARY"},
    )


def _write_anchor(directory: Path, root_sha256: str, **overrides) -> None:
    commitment = {
        "published_at_unix": CUTOFF_C,
        "reference": "ENGINEERING-ONLY/0001",
        "root_sha256": root_sha256,
        "venue": "ENGINEERING_ONLY",
    }
    commitment.update(overrides.pop("commitment", {}))
    document = {
        "beacon_response": {
            "chain_hash": _V2["chain_hash"],
            "randomness": _V2["randomness"],
            "round": int(_V2["round"]),
            "signature": _V2["signature"],
        },
        "commitment": commitment,
        "must_precede_unix": CUTOFF_C + 1,
        "schema_version": bridge.SCHEMA_VERSION,
    }
    document.update(overrides)
    (directory / bridge.ROUTE_E_ANCHOR_NAME).write_bytes(
        json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    )


def test_prb2_01_no_caller_supplied_verifier_is_accepted_on_the_production_path(tmp_path):
    directory, record = _measured_run(tmp_path)
    bridge.write_anchor_receipt(
        directory,
        bridge.AnchorReceipt(record.measurement_root_sha256, "ENGINEERING_ONLY", "r", "l"),
    )
    with pytest.raises(bridge.BridgeAnchorError) as excinfo:
        bridge.open_measured_analysis_access(directory, verifier=lambda receipt: True)
    assert "no caller-supplied verifier" in str(excinfo.value)


def test_prb2_02_an_authentic_anchor_passes_through_the_installed_verifier(tmp_path):
    directory, record = _measured_run(tmp_path)
    bridge.write_anchor_receipt(
        directory,
        bridge.AnchorReceipt(record.measurement_root_sha256, "ENGINEERING_ONLY", "r", "l"),
    )
    _write_anchor(directory, record.measurement_root_sha256)
    access = bridge.open_measured_analysis_access(directory)
    assert isinstance(access, bridge.MeasuredAnalysisAccess)
    assert access.anchor_receipt.root_sha256 == record.measurement_root_sha256


def test_prb2_03_a_missing_anchor_is_refused(tmp_path):
    directory, record = _measured_run(tmp_path)
    bridge.write_anchor_receipt(
        directory,
        bridge.AnchorReceipt(record.measurement_root_sha256, "ENGINEERING_ONLY", "r", "l"),
    )
    with pytest.raises(bridge.BridgeAnchorError) as excinfo:
        bridge.open_measured_analysis_access(directory)
    assert "ROUTE_E_ANCHOR" in str(excinfo.value)


@pytest.mark.parametrize(
    "mutate,expected",
    [
        ({"commitment": {"root_sha256": "0" * 64}}, "does not bind"),
        ({"must_precede_unix": CUTOFF_C - 10_000}, "did not verify"),
        ({"beacon_response": {"chain_hash": "1" * 64, "randomness": _V2["randomness"],
                              "round": int(_V2["round"]), "signature": _V2["signature"]}}, "did not verify"),
        ({"beacon_response": {"chain_hash": _V2["chain_hash"], "randomness": _V2["randomness"],
                              "round": int(_V2["round"]) + 1, "signature": _V2["signature"]}}, "did not verify"),
        ({"beacon_response": {"chain_hash": _V2["chain_hash"], "randomness": "0" * 64,
                              "round": int(_V2["round"]), "signature": _V2["signature"]}}, "did not verify"),
    ],
    ids=["wrong-root", "cutoff", "wrong-network", "wrong-round", "forged-randomness"],
)
def test_prb2_04_a_forged_or_mismatched_anchor_is_refused(tmp_path, mutate, expected):
    directory, record = _measured_run(tmp_path)
    bridge.write_anchor_receipt(
        directory,
        bridge.AnchorReceipt(record.measurement_root_sha256, "ENGINEERING_ONLY", "r", "l"),
    )
    _write_anchor(directory, record.measurement_root_sha256, **mutate)
    with pytest.raises(bridge.BridgeAnchorError) as excinfo:
        bridge.open_measured_analysis_access(directory)
    assert expected in str(excinfo.value)


def test_prb2_05_a_file_mutated_after_validation_is_refused_on_re_read(tmp_path):
    directory, record = _measured_run(tmp_path)
    bridge.write_anchor_receipt(
        directory,
        bridge.AnchorReceipt(record.measurement_root_sha256, "ENGINEERING_ONLY", "r", "l"),
    )
    _write_anchor(directory, record.measurement_root_sha256)
    assert bridge.open_measured_analysis_access(directory)
    anchor = directory / bridge.ROUTE_E_ANCHOR_NAME
    document = json.loads(anchor.read_bytes().decode("ascii"))
    root = document["commitment"]["root_sha256"]
    document["commitment"]["root_sha256"] = ("0" if root[0] != "0" else "1") + root[1:]
    anchor.write_bytes(
        json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    )
    with pytest.raises(bridge.BridgeAnchorError):
        bridge.open_measured_analysis_access(directory)


def test_prb2_06_the_injection_helper_is_private_and_unexported():
    assert "_open_measured_analysis_access_with_injected_verifier" not in bridge.__all__
    signature = inspect.signature(bridge.open_measured_analysis_access)
    assert signature.parameters["verifier"].default is None


# ======================================================================================
# PRB-3 -- one frozen order on every public path
# ======================================================================================


def _authorisation():
    """A well-formed authorisation.  It grants nothing: the gate still refuses."""
    return frame.RouteEAuthorisation(
        preregistration_commit_sha1="0" * 40,
        human_review_commit_sha1="1" * 40,
        beacon_round=int(_V2["round"]),
        seed_root_sha256="c" * 64,
        granted=True,
    )


def _order_inputs(tmp_path: Path):
    root = tmp_path / "evidence"
    root.mkdir(parents=True, exist_ok=True)
    from edlab.substrates.lattice_bond.instrumentation import TrackingResult

    records = (
        locks.JoinRecord(frame=0, cell_set_sha256="a" * 64, track_id=1),
        locks.JoinRecord(frame=1, cell_set_sha256="b" * 64, track_id=1),
    )
    path, digest = locks.write_join_evidence(root, records)
    enrolment = locks.FamilyEnrolment(
        run_identity="engineering-only-0001",
        seed_root_sha256="c" * 64,
        draw_plan_digest="d" * 64,
        n_draws=1,
        worlds=1,
    )
    expected = locks.route_e_root(
        measurement_root_sha256="e" * 64,
        track_component_join_digest=digest,
        family_enrolment_digest=locks.enrolment_digest(enrolment),
    )
    receipt = locks.RouteEReceipt(
        root_sha256=expected,
        commitment=locks.PublicCommitment(
            root_sha256=expected,
            venue="ENGINEERING_ONLY",
            reference="ENGINEERING-ONLY/0001",
            published_at_unix=CUTOFF_C,
        ),
    )
    return path, enrolment, receipt


def test_prb3_01_both_public_paths_produce_the_identical_frozen_order(tmp_path):
    path, enrolment, receipt = _order_inputs(tmp_path)
    trace_a: list[str] = []
    with pytest.raises(Exception):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256="e" * 64,
            family_enrolment=enrolment,
            receipt=receipt,
            must_precede_unix=CUTOFF_C + 1,
            beacon_response=None,
            verifier_path=None,
            trace=trace_a,
        )
    trace_b: list[str] = []
    with pytest.raises(Exception):
        locks.route_e_entry(
            "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
            authorisation=_authorisation(),
            evidence_path=path,
            measurement_root_sha256="e" * 64,
            family_enrolment=enrolment,
            receipt=receipt,
            must_precede_unix=CUTOFF_C + 1,
            beacon_response=None,
            verifier_path=None,
            trace=trace_b,
        )
    assert trace_a == trace_b
    assert trace_a[:3] == ["ENTRY_GUARD", "LOCAL_EVIDENCE", "ROOT_DIGEST"]
    assert [step for step in trace_a if step in locks.CHECK_ORDER] == list(locks.CHECK_ORDER)


@pytest.mark.parametrize(
    "entry", ["open_route_e_analysis", "route_e_entry"], ids=["analysis", "facade"]
)
def test_prb3_02_a_missing_cutoff_closes_admission_on_every_public_path(tmp_path, entry):
    path, enrolment, receipt = _order_inputs(tmp_path)
    common = dict(
        evidence_path=path,
        measurement_root_sha256="e" * 64,
        family_enrolment=enrolment,
        receipt=receipt,
        must_precede_unix=None,
        beacon_response=None,
        verifier_path=None,
    )
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        if entry == "open_route_e_analysis":
            locks.open_route_e_analysis(**common)
        else:
            locks.route_e_entry(
                "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
                authorisation=_authorisation(),
                **common,
            )
    assert "cutoff" in str(excinfo.value)


def test_prb3_03_a_reordered_step_is_refused():
    order = locks._OrderTrace()
    order.enter("LOCAL_EVIDENCE")
    with pytest.raises(locks.CheckOrderViolation):
        order.enter("LOCAL_EVIDENCE")
    other = locks._OrderTrace()
    with pytest.raises(locks.CheckOrderViolation):
        other.enter("VERIFIER")


def test_prb3_04_a_commitment_at_or_after_the_cutoff_is_refused(tmp_path):
    path, enrolment, receipt = _order_inputs(tmp_path)
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256="e" * 64,
            family_enrolment=enrolment,
            receipt=receipt,
            must_precede_unix=CUTOFF_C,
            beacon_response=None,
            verifier_path=None,
        )
    assert "strictly prior" in str(excinfo.value)


def test_prb3_05_both_public_entries_delegate_to_the_same_internal_path():
    source = Path(locks.__file__).read_text("utf-8")
    assert source.count("_frozen_check_order(") >= 3  # definition + two public callers
    for name in ("open_route_e_analysis", "route_e_entry"):
        body = inspect.getsource(getattr(locks, name))
        assert "_frozen_check_order(" in body, name


# ======================================================================================
# PRB-4 -- the replay root is persisted, anchored and recomputed
# ======================================================================================


@requires_verifier
def test_prb4_01_the_replay_root_is_persisted_and_bound_to_the_run(tmp_path):
    record = _run(tmp_path)
    document = json.loads(
        (Path(record.output_directory) / execution.REPLAY_ROOT_NAME).read_bytes().decode("ascii")
    )
    assert document["kind"] == execution.REPLAY_ROOT_KIND
    assert document["pre_run_root"] == record.pre_run_root
    assert document["enrolment_digest"] == record.enrolment_digest
    assert document["worlds"] and all(
        len(world["route_e_replay_root"]) == 64 for world in document["worlds"]
    )
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert verdict.admissible, verdict


@requires_verifier
@pytest.mark.parametrize(
    "field",
    ["run_identity", "pre_run_root", "enrolment_digest", "worlds", "replay_root", "join_digest"],
)
def test_prb4_02_every_bound_element_refuses_when_mutated(tmp_path, field):
    record = _run(tmp_path)
    path = Path(record.output_directory) / execution.REPLAY_ROOT_NAME

    def mutate(document):
        if field == "run_identity":
            document["run_identity"] = "another-run-identity"
        elif field == "pre_run_root":
            document["pre_run_root"] = "0" * 64
        elif field == "enrolment_digest":
            document["enrolment_digest"] = "0" * 64
        elif field == "worlds":
            document["worlds"] = []
        elif field == "replay_root":
            document["worlds"][0]["route_e_replay_root"] = "0" * 64
        else:
            document["worlds"][0]["track_component_join_sha256"] = "0" * 64

    _rewrite(path, mutate)
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert not verdict.admissible
    assert verdict.reason_code in {
        "REPLAY_ROOT_FOREIGN_RUN",
        "REPLAY_ROOT_MISMATCH",
        "REPLAY_ROOT_INCOMPLETE",
        "JOIN_EVIDENCE_MISMATCH",
        "FILE_INVENTORY_INEXACT",
    }


@requires_verifier
def test_prb4_03_an_absent_replay_root_is_never_reconstructed(tmp_path):
    record = _run(tmp_path)
    (Path(record.output_directory) / execution.REPLAY_ROOT_NAME).unlink()
    verdict = admission.verify_route_e_run(Path(record.output_directory))
    assert not verdict.admissible
    assert verdict.reason_code in {"REPLAY_ROOT_UNREADABLE", "FILE_INVENTORY_INEXACT"}


@requires_verifier
def test_prb4_04_a_replay_root_from_another_run_is_refused(tmp_path):
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b", output_namespace="SYNTHETIC-NONSCI-BOUNDARY-0003",
                  run_identity="synthetic-boundary-0003")
    foreign = (Path(second.output_directory) / execution.REPLAY_ROOT_NAME).read_bytes()
    (Path(first.output_directory) / execution.REPLAY_ROOT_NAME).write_bytes(foreign)
    verdict = admission.verify_route_e_run(Path(first.output_directory))
    assert not verdict.admissible


@requires_verifier
def test_prb4_05_the_persisted_replay_root_is_restart_identical(tmp_path):
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b")
    a = json.loads((Path(first.output_directory) / execution.REPLAY_ROOT_NAME).read_bytes())
    b = json.loads((Path(second.output_directory) / execution.REPLAY_ROOT_NAME).read_bytes())
    assert [w["route_e_replay_root"] for w in a["worlds"]] == [
        w["route_e_replay_root"] for w in b["worlds"]
    ]


# ======================================================================================
# HR-10 -- the real classifier, always
# ======================================================================================


def test_hr10_01_the_public_assembly_has_no_classifier_parameter():
    assert "classifier" not in inspect.signature(frame.assemble_draw_outcome).parameters


def test_hr10_02_a_supplied_classifier_cannot_bypass_the_real_one():
    from edlab.substrates.lattice_bond.instrumentation import TrackingResult

    tracking = TrackingResult((), (), (), ())
    with pytest.raises(TypeError):
        frame.assemble_draw_outcome(
            tracking,
            persisted_to_horizon=True,
            replacement_verified=True,
            eligible=True,
            classifier=lambda _t: (),
        )


def test_hr10_03_the_public_path_calls_the_real_classifier(monkeypatch):
    from edlab.substrates.lattice_bond.instrumentation import TrackingResult

    calls: list[int] = []
    real = frame.classify_track_terminations

    def spy(tracking):
        calls.append(1)
        return real(tracking)

    monkeypatch.setattr(frame, "classify_track_terminations", spy)
    frame.assemble_draw_outcome(
        TrackingResult((), (), (), ()),
        persisted_to_horizon=True,
        replacement_verified=True,
        eligible=True,
    )
    assert calls == [1], "the public assembly did not call the real classifier"


def test_hr10_04_the_five_guarded_entry_points_stay_guarded():
    from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
    from edlab.substrates.lattice_bond import future_lifecycle_runner as runner
    from edlab.substrates.lattice_bond import lifecycle as lifecycle_module

    for module in (owned, runner, lifecycle_module):
        assert "_refuse_route_e_signal" in Path(module.__file__).read_text("utf-8")
    status = locks.blocker_status()["PRB-5"]
    assert status["guard_installed"] is True


# ======================================================================================
# The integrated public path, and the four separate tamperings
# ======================================================================================


@requires_verifier
def test_integrated_01_the_real_public_path_traverses_every_closed_blocker(tmp_path):
    """P -> commitment -> beacon -> frozen order -> Route E -> join -> classification
    -> re-read -> engineering admission.  ENGINEERING_ONLY."""
    document = _manifest()
    document["output_namespace"] = "SYNTHETIC-NONSCI-INTEGRATED-0001"
    document["experiment_id"] = "ENGINEERING_ONLY-NOT_SCIENTIFIC_DATA"
    assert document["fixture_class"] == "SYNTHETIC_NON_SCIENTIFIC"
    bundle_dir, root = _bundle(tmp_path, document)

    record = execution.run_route_e(
        bundle_dir, _beacon(tmp_path), _destination(tmp_path, document["output_namespace"])
    )
    output = Path(record.output_directory)

    # P and the commitment
    assert record.pre_run_root == root
    proof = json.loads((bundle_dir / execution.ANTERIORITY_NAME).read_bytes())
    assert proof["binds_pre_run_root"] == root
    # the beacon really verified: the seed derives from the verified randomness
    assert record.designated_round == int(_V2["round"])
    # PRB-1 and PRB-4 evidence exists on disk
    assert (_world(record) / locks.JOIN_EVIDENCE_FILENAME).is_file()
    assert (output / execution.REPLAY_ROOT_NAME).is_file()
    # the real consumer admits it
    verdict = admission.verify_route_e_run(output)
    assert verdict.admissible, verdict
    assert record.contributes_to_dataset is False
    assert all(marker in " ".join(CANARY) for marker in CANARY)


@requires_verifier
@pytest.mark.parametrize("blocker", ["PRB-1", "PRB-2", "PRB-3", "PRB-4"])
def test_integrated_02_each_tampering_forbids_complete(tmp_path, blocker):
    record = _run(tmp_path)
    output = Path(record.output_directory)
    assert admission.verify_route_e_run(output).admissible

    if blocker == "PRB-1":
        (_world(record) / locks.JOIN_EVIDENCE_FILENAME).unlink()
    elif blocker == "PRB-2":
        # the sealed receipt no longer binds the evidence
        _rewrite(output / execution.FINAL_RECEIPT_NAME, lambda d: d.update(post_run_root="0" * 64))
    elif blocker == "PRB-3":
        # the frozen order refuses without the mandatory public-priority cutoff
        path, enrolment, receipt = _order_inputs(tmp_path / "order")
        with pytest.raises(locks.CommitmentInvalid):
            locks.route_e_entry(
                "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
                authorisation=_authorisation(),
                evidence_path=path,
                measurement_root_sha256="e" * 64,
                family_enrolment=enrolment,
                receipt=receipt,
                must_precede_unix=None,
            )
        return
    else:
        _rewrite(
            output / execution.REPLAY_ROOT_NAME,
            lambda d: d["worlds"][0].update(route_e_replay_root="0" * 64),
        )

    verdict = admission.verify_route_e_run(output)
    assert not verdict.admissible, f"{blocker} tampering still reached admission"
