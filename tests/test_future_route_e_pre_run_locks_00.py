"""Mechanical pins for the MISSION MANDATE of FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00:
the six frozen PRE_RUN_BLOCKERs PRB-1 .. PRB-6, plus the eleven corrections HR-1 .. HR-11
ordered by the human review ``bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd`` and the
corrections ordered by the independent review ``31ccccfb9e61809cf5d461a70425e00c3db7bc17``.

Every test uses synthetic deterministic fixtures and temporary directories.  None opens
Stage B, M_MINUS, a trajectory, a shard, a candidate or any historical result.  None
creates a scientific seed, beacon round, family, namespace, law, initial condition or
world.  None contacts the network.  None steps the engine.

WHAT THE PRB-5 TESTS DO AND DO NOT PROVE
----------------------------------------
``test_prb5_real_*`` call the FIVE REAL accepted public functions and prove that each
refuses, with its own typed exception, before every listed effect.  That is the WEAKER
property of LK-L1: the refusal is the function's own first check, NOT a Route E gate,
because no accepted source may be edited under the frozen allowlist.
``test_prb5_facade_*`` test ``route_e_entry``, which is a protocol facade and is NOT in
the call graph of those five functions.  Neither family closes PRB-5.
"""

from __future__ import annotations

import builtins
import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks
from edlab.substrates.lattice_bond import route_e_beacon_verifier as beacon
from edlab.substrates.lattice_bond.engine import LatticeBondState
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)

SYNTHETIC_ROOT = hashlib.sha256(b"LOCKS-SYNTHETIC-ROOT-NOT-A-SCIENTIFIC-SEED").digest()
DIGEST_A = hashlib.sha256(b"A").hexdigest()
DIGEST_B = hashlib.sha256(b"B").hexdigest()
DIGEST_C = hashlib.sha256(b"C").hexdigest()

_DETECTOR = DetectorSpec(matter_threshold=0.45, min_cells=3)
_TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=3.0, dilation_radius=1)
_BLOB_LEFT = [(0, 0), (0, 1), (1, 0), (1, 1)]
_BLOB_FAR = [(0, 8), (0, 9), (1, 8), (1, 9)]

_CUTOFF = 1_700_000_000
_PUBLISHED = _CUTOFF - 86_400


def _state(shape, cells):
    h, w = shape
    m = np.zeros((h, w), dtype=np.float64)
    for y, x in cells:
        m[y, x] = 1.0
    return LatticeBondState(
        m=m,
        n=np.zeros((h, w), dtype=np.float64),
        b=np.zeros((2, h, w), dtype=np.float64),
        step=0,
    )


def _frames(frames_cells, shape=(16, 16)):
    return [
        detect_components(_state(shape, cells), _DETECTOR, frame=index)
        for index, cells in enumerate(frames_cells)
    ]


def _track(frames_cells, shape=(16, 16)):
    frames = _frames(frames_cells, shape)
    return track_components(frames, _TRACKER, sampled_frames=tuple(range(len(frames_cells))))


def _support_map(frames_cells, shape=(16, 16)):
    out = {}
    for detected in _frames(frames_cells, shape):
        for component in detected:
            out.setdefault(component.frame, {})[component.index] = (
                component.shape,
                component.cells,
            )
    return out


class ForbiddenEffects:
    """Make every listed effect raise, so a refusal that happens first is provable.

    Covers, per the review's bound: entropy, network, subprocess, file open, filesystem
    read (a historical result or any scientific data), filesystem write, directory
    creation and the engine.  It does NOT claim to cover effects outside this list;
    that is the honest limit of the proof.

    ``arm_reads`` is switched off for the facade tests, which must legitimately re-read
    the persisted join evidence during the LOCAL_EVIDENCE phase.
    """

    TARGETS = (
        "entropy(os.urandom)",
        "network(socket.socket)",
        "subprocess(subprocess.Popen)",
        "file(builtins.open)",
        "read(Path.read_bytes)",
        "read(Path.read_text)",
        "write(Path.write_bytes)",
        "write(Path.write_text)",
        "mkdir(Path.mkdir)",
        "engine(LatticeBondEngine.step)",
    )

    def __init__(self, monkeypatch, *, arm_reads: bool = True):
        self.monkeypatch = monkeypatch
        self.arm_reads = arm_reads
        self.hits: list[str] = []

    def _boom(self, label):
        def _raise(*args, **kwargs):  # pragma: no cover - must never run
            self.hits.append(label)
            raise AssertionError(f"forbidden effect reached: {label}")

        return _raise

    def __enter__(self):
        from edlab.substrates.lattice_bond import engine as engine_module

        self.monkeypatch.setattr(os, "urandom", self._boom("entropy(os.urandom)"))
        self.monkeypatch.setattr(socket, "socket", self._boom("network(socket.socket)"))
        self.monkeypatch.setattr(subprocess, "Popen", self._boom("subprocess(subprocess.Popen)"))
        self.monkeypatch.setattr(builtins, "open", self._boom("file(builtins.open)"))
        if self.arm_reads:
            self.monkeypatch.setattr(Path, "read_bytes", self._boom("read(Path.read_bytes)"))
            self.monkeypatch.setattr(Path, "read_text", self._boom("read(Path.read_text)"))
        self.monkeypatch.setattr(Path, "write_bytes", self._boom("write(Path.write_bytes)"))
        self.monkeypatch.setattr(Path, "write_text", self._boom("write(Path.write_text)"))
        self.monkeypatch.setattr(Path, "mkdir", self._boom("mkdir(Path.mkdir)"))
        self.monkeypatch.setattr(
            engine_module.LatticeBondEngine, "step", self._boom("engine(LatticeBondEngine.step)")
        )
        return self

    def __exit__(self, *exc):
        return False


def _authorisation(granted=True):
    return frame.RouteEAuthorisation(
        preregistration_commit_sha1="a" * 40,
        human_review_commit_sha1="b" * 40,
        beacon_round=4242,
        seed_root_sha256="c" * 64,
        granted=granted,
    )


def _enrolment(identity="RUN-SYNTHETIC-0001"):
    return locks.FamilyEnrolment(
        run_identity=identity,
        seed_root_sha256=DIGEST_A,
        draw_plan_digest=DIGEST_B,
        n_draws=frame.N_LAW_DRAWS,
        worlds=frame.WORLD_COUNT,
    )


def _commitment(root, published_at=_PUBLISHED):
    return locks.PublicCommitment(
        root_sha256=root,
        venue="TEST_ONLY append-only log",
        reference="TEST_ONLY/0001",
        published_at_unix=published_at,
    )


def _receipt(root, published_at=_PUBLISHED):
    return locks.RouteEReceipt(root_sha256=root, commitment=_commitment(root, published_at))


def _no_beacon():
    """No beacon response: the frozen answer is WAIT, on the SAME round."""
    return None


def _records():
    tracking = _track([_BLOB_LEFT, _BLOB_LEFT])
    return locks.build_track_component_join(tracking, _support_map([_BLOB_LEFT, _BLOB_LEFT]))


def _persisted(tmp_path, measurement_root=DIGEST_C, identity="RUN-SYNTHETIC-0001"):
    """Persist a join and return what the frozen order needs, plus the expected root."""
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    path, digest = locks.write_join_evidence(root_dir, _records())
    enrolment = _enrolment(identity)
    expected = locks.route_e_root(
        measurement_root_sha256=measurement_root,
        track_component_join_digest=digest,
        family_enrolment_digest=locks.enrolment_digest(enrolment),
    )
    return path, enrolment, expected


# ======================================================================================
# PRB-1  persist the track-component join
# ======================================================================================


def test_prb1_01_literal_text_is_carried_in_the_module():
    entry = next(b for b in locks.PRE_RUN_BLOCKERS if b["id"] == "PRB-1")
    assert entry["obligation"] == "persist the track-component join"
    assert entry["closure"] == (
        "write (frame, canonical cell-set digest, track_id) into root-bound evidence"
    )


def test_prb2_to_6_literal_texts_are_carried_verbatim():
    by_id = {b["id"]: b for b in locks.PRE_RUN_BLOCKERS}
    assert by_id["PRB-2"]["closure"] == (
        "the supported scientific entry point refuses without a verified receipt"
    )
    assert by_id["PRB-3"]["closure"] == "pin by test: local evidence -> root digest -> verifier"
    assert by_id["PRB-4"]["closure"] == "bind run identity and family enrolment into the root"
    assert "run_owned_future_pipeline" in by_id["PRB-5"]["closure"]
    assert by_id["PRB-6"]["closure"] == (
        "public immutable or append-only commitment, verifiable without a secret"
    )
    assert len(locks.PRE_RUN_BLOCKERS) == 6


def test_prb1_02_join_record_carries_exactly_the_three_declared_fields():
    record = locks.JoinRecord(frame=16, cell_set_sha256=DIGEST_A, track_id=3)
    assert record.as_tuple() == (16, DIGEST_A, 3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"frame": -1, "cell_set_sha256": DIGEST_A, "track_id": 0},
        {"frame": True, "cell_set_sha256": DIGEST_A, "track_id": 0},
        {"frame": 0, "cell_set_sha256": "short", "track_id": 0},
        {"frame": 0, "cell_set_sha256": DIGEST_A, "track_id": -2},
        {"frame": 0, "cell_set_sha256": DIGEST_A, "track_id": True},
    ],
)
def test_prb1_03_join_record_is_fail_closed(kwargs):
    with pytest.raises(ValueError):
        locks.JoinRecord(**kwargs)


def test_prb1_04_cell_set_digest_is_canonical_and_binds_the_shape():
    first = locks.canonical_cell_set_digest((16, 16), [3, 1, 2, 1])
    assert first == locks.canonical_cell_set_digest((16, 16), [1, 2, 3])
    assert first != locks.canonical_cell_set_digest((32, 32), [1, 2, 3])


@pytest.mark.parametrize(
    "args",
    [
        ((16,), [1]),
        ((16, 16), "123"),
        ((16, 16), []),
        ((16, 16), [10_000]),
        ((16, 16), [True]),
        ((1, 16), [0]),
    ],
)
def test_prb1_05_cell_set_digest_is_fail_closed(args):
    with pytest.raises((ValueError, TypeError)):
        locks.canonical_cell_set_digest(*args)


def test_prb1_06_join_covers_the_detected_support_exactly():
    cells = [_BLOB_LEFT, _BLOB_LEFT]
    tracking = _track(cells)
    support = _support_map(cells)
    records = locks.build_track_component_join(tracking, support)
    detected = {(f, i) for f, per in support.items() for i in per}
    assert len(records) == len(tracking.assignments)
    assert len(records) == len(detected)


def test_prb1_07_an_orphan_assignment_is_refused_not_dropped():
    cells = [_BLOB_LEFT, _BLOB_LEFT]
    tracking = _track(cells)
    support = _support_map(cells)
    support[1].clear()
    with pytest.raises(locks.JoinIncomplete) as excinfo:
        locks.build_track_component_join(tracking, support)
    assert "orphan assignment" in str(excinfo.value)


def test_prb1_08_an_unassigned_component_is_refused():
    cells = [_BLOB_LEFT, _BLOB_LEFT]
    tracking = _track(cells)
    support = _support_map(cells)
    support[0][99] = ((16, 16), [200, 201, 202])
    with pytest.raises(locks.JoinIncomplete) as excinfo:
        locks.build_track_component_join(tracking, support)
    assert "incomplete join" in str(excinfo.value)


def test_prb1_09_duplicate_rows_are_refused_never_absorbed():
    record = locks.JoinRecord(frame=0, cell_set_sha256=DIGEST_A, track_id=1)
    with pytest.raises(ValueError):
        locks.canonical_join_bytes([record, record])
    with pytest.raises(ValueError):
        locks.join_digest([record, record])


def test_prb1_10_join_bytes_are_order_independent_and_refuse_emptiness():
    a = locks.JoinRecord(frame=0, cell_set_sha256=DIGEST_A, track_id=1)
    b = locks.JoinRecord(frame=1, cell_set_sha256=DIGEST_B, track_id=2)
    assert locks.canonical_join_bytes([a, b]) == locks.canonical_join_bytes([b, a])
    assert locks.join_digest([a, b]) == locks.join_digest([b, a])
    with pytest.raises(ValueError):
        locks.canonical_join_bytes([])


def test_prb1_11_the_join_is_actually_written_and_read_back(tmp_path):
    """The artefact EXISTS on disk and its digest is recomputed from the bytes read.

    A writer replaced by a no-op cannot satisfy this test: there would be no file.
    """
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    records = _records()
    path, digest = locks.write_join_evidence(root_dir, records)
    assert path.is_file()
    assert path.parent == root_dir
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    reread, reread_digest = locks.read_join_evidence(path)
    assert reread_digest == digest
    assert reread == records
    assert locks.join_digest(records) == digest


def test_prb1_12_permuting_the_input_gives_identical_bytes(tmp_path):
    records = _records()
    first_root = tmp_path / "a"
    first_root.mkdir()
    second_root = tmp_path / "b"
    second_root.mkdir()
    path_a, digest_a = locks.write_join_evidence(first_root, records)
    path_b, digest_b = locks.write_join_evidence(second_root, tuple(reversed(records)))
    assert path_a.read_bytes() == path_b.read_bytes()
    assert digest_a == digest_b


@pytest.mark.parametrize("field", ["frame", "cell_set_sha256", "track_id"])
def test_prb1_13_mutating_any_field_changes_the_root(field):
    records = list(_records())
    original = locks.join_digest(records)
    first = records[0]
    records[0] = {
        "frame": locks.JoinRecord(
            frame=first.frame + 1000,
            cell_set_sha256=first.cell_set_sha256,
            track_id=first.track_id,
        ),
        "cell_set_sha256": locks.JoinRecord(
            frame=first.frame, cell_set_sha256=DIGEST_C, track_id=first.track_id
        ),
        "track_id": locks.JoinRecord(
            frame=first.frame,
            cell_set_sha256=first.cell_set_sha256,
            track_id=first.track_id + 77,
        ),
    }[field]
    mutated = locks.join_digest(records)
    assert mutated != original
    enrolment_hash = locks.enrolment_digest(_enrolment())
    assert locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=original,
        family_enrolment_digest=enrolment_hash,
    ) != locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=mutated,
        family_enrolment_digest=enrolment_hash,
    )


def test_prb1_14_a_mutated_artefact_can_never_reproduce_its_digest(tmp_path):
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    path, digest = locks.write_join_evidence(root_dir, _records())
    raw = path.read_bytes()
    tampered = raw.replace(b'"schema"', b'"schemA"', 1)
    assert tampered != raw
    path.unlink()
    path.write_bytes(tampered)
    assert hashlib.sha256(path.read_bytes()).hexdigest() != digest
    with pytest.raises(locks.EvidenceInvalid):
        locks.read_join_evidence(path)


def test_prb1_15_non_canonical_bytes_are_refused_not_recanonicalised(tmp_path):
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    path, _ = locks.write_join_evidence(root_dir, _records())
    payload = json.loads(path.read_bytes().decode("ascii"))
    path.unlink()
    path.write_bytes(json.dumps(payload, indent=2).encode("ascii"))
    with pytest.raises(locks.EvidenceInvalid) as excinfo:
        locks.read_join_evidence(path)
    assert "canonical" in str(excinfo.value)


def test_prb1_16_the_writer_never_overwrites_and_needs_a_real_root(tmp_path):
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    records = _records()
    locks.write_join_evidence(root_dir, records)
    with pytest.raises(locks.EvidenceInvalid) as excinfo:
        locks.write_join_evidence(root_dir, records)
    assert "overwrite" in str(excinfo.value)
    with pytest.raises(locks.EvidenceInvalid):
        locks.write_join_evidence(tmp_path / "absent", records)


def test_prb1_17_a_symlinked_root_or_artefact_is_refused(tmp_path):
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    path, _ = locks.write_join_evidence(root_dir, _records())
    link_root = tmp_path / "linked"
    link_root.symlink_to(root_dir, target_is_directory=True)
    with pytest.raises(locks.EvidenceInvalid) as excinfo:
        locks.write_join_evidence(link_root, _records())
    assert "symlink" in str(excinfo.value)
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.symlink_to(path)
    with pytest.raises(locks.EvidenceInvalid) as excinfo:
        locks.read_join_evidence(elsewhere)
    assert "symlink" in str(excinfo.value)


def test_prb1_18_a_missing_artefact_is_refused(tmp_path):
    with pytest.raises(locks.EvidenceInvalid):
        locks.read_join_evidence(tmp_path / "nothing.json")


def test_prb1_19_the_persisted_digest_is_the_one_bound_into_the_root(tmp_path):
    path, enrolment, expected = _persisted(tmp_path)
    _, digest_from_disk = locks.read_join_evidence(path)
    assert expected == locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=digest_from_disk,
        family_enrolment_digest=locks.enrolment_digest(enrolment),
    )


# ======================================================================================
# PRB-4  replay binding
# ======================================================================================


def test_prb4_01_enrolment_binds_run_identity_seed_and_plan():
    assert locks._is_sha256_hex(locks.enrolment_digest(_enrolment()))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"run_identity": "short"},
        {"seed_root_sha256": "zz" * 32},
        {"draw_plan_digest": "nope"},
        {"n_draws": 0},
        {"worlds": True},
    ],
)
def test_prb4_02_enrolment_is_fail_closed(kwargs):
    base = dict(
        run_identity="RUN-SYNTHETIC-0001",
        seed_root_sha256=DIGEST_A,
        draw_plan_digest=DIGEST_B,
        n_draws=67,
        worlds=134,
    )
    base.update(kwargs)
    with pytest.raises(ValueError):
        locks.FamilyEnrolment(**base)


def test_prb4_03_a_bit_identical_copy_under_another_identity_does_not_replay():
    first = locks.enrolment_digest(_enrolment("RUN-SYNTHETIC-0001"))
    second = locks.enrolment_digest(_enrolment("RUN-SYNTHETIC-0002"))
    assert first != second
    assert locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=DIGEST_B,
        family_enrolment_digest=first,
    ) != locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=DIGEST_B,
        family_enrolment_digest=second,
    )


@pytest.mark.parametrize("bad", ["", "zz" * 32, DIGEST_A[:-1], 12345])
def test_prb4_04_root_is_fail_closed(bad):
    with pytest.raises(ValueError):
        locks.route_e_root(
            measurement_root_sha256=bad,
            track_component_join_digest=DIGEST_B,
            family_enrolment_digest=DIGEST_C,
        )


def test_prb4_05_the_three_root_slots_are_not_interchangeable():
    assert locks.route_e_root(
        measurement_root_sha256=DIGEST_A,
        track_component_join_digest=DIGEST_B,
        family_enrolment_digest=DIGEST_C,
    ) != locks.route_e_root(
        measurement_root_sha256=DIGEST_B,
        track_component_join_digest=DIGEST_A,
        family_enrolment_digest=DIGEST_C,
    )


def test_prb4_06_status_claims_only_the_digest_level():
    status = locks.blocker_status()["PRB-4"]
    assert status["closed_at_digest_level"] is True
    assert status["persistence_or_external_anchoring"] is False


# ======================================================================================
# PRB-6  external anchoring.  There is NO callback anywhere: the commitment's priority
# is checked here and the designated round is verified by the pinned maintained
# verifier (see test_route_e_beacon_verifier.py for the cryptography itself).
# ======================================================================================

_ANCHOR = dict(beacon_response=None, verifier_path=None)


def test_prb6_01_absent_commitment_is_refused():
    with pytest.raises(locks.CommitmentInvalid):
        locks.verify_public_commitment(
            None, expected_root_sha256=DIGEST_A, must_precede_unix=_CUTOFF, **_ANCHOR
        )


def test_prb6_02_a_commitment_binding_another_root_is_refused():
    with pytest.raises(locks.CommitmentInvalid):
        locks.verify_public_commitment(
            _commitment(DIGEST_B),
            expected_root_sha256=DIGEST_A,
            must_precede_unix=_CUTOFF,
            **_ANCHOR,
        )


def test_prb6_03_no_verifier_means_a_stop_never_a_default():
    """Priority passes, then the missing verifier is a STOP.  Never a silent pass."""
    with pytest.raises(frame.BeaconInvalid) as excinfo:
        locks.verify_public_commitment(
            _commitment(DIGEST_A),
            expected_root_sha256=DIGEST_A,
            must_precede_unix=_CUTOFF,
            beacon_response={"round": 1, "randomness": "00" * 32, "signature": "00" * 48,
                             "chain_hash": beacon.QUICKNET_CHAIN_HASH},
            verifier_path=None,
        )
    assert "configuration_error" in str(excinfo.value)
    assert frame.BeaconInvalid.disposition == "STOP"


def test_prb6_04_no_boolean_callback_exists_in_any_signature():
    import inspect

    for function in (
        locks.verify_public_commitment,
        locks.open_route_e_analysis,
        locks.route_e_entry,
        locks.enforce_route_e_guard,
    ):
        names = set(inspect.signature(function).parameters)
        assert "verifier" not in names
        assert "callback" not in names
    assert "verifier_path" in set(inspect.signature(locks.verify_public_commitment).parameters)


def test_prb6_05_an_absent_beacon_is_wait_not_a_refusal_of_the_anchor():
    with pytest.raises(frame.BeaconUnavailable) as excinfo:
        locks.verify_public_commitment(
            _commitment(DIGEST_A),
            expected_root_sha256=DIGEST_A,
            must_precede_unix=_CUTOFF,
            beacon_response=None,
            verifier_path=None,
        )
    assert "SAME round" in str(excinfo.value)


@pytest.mark.parametrize("published", [_CUTOFF, _CUTOFF + 1])
def test_prb6_06_priority_is_strict_which_is_the_anti_reroll_condition(published):
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.verify_public_commitment(
            _commitment(DIGEST_A, published_at=published),
            expected_root_sha256=DIGEST_A,
            must_precede_unix=_CUTOFF,
            **_ANCHOR,
        )
    assert "strictly prior" in str(excinfo.value)


@pytest.mark.parametrize("cutoff", [None, True, 0, -1])
def test_prb6_07_the_priority_cutoff_has_no_default_and_cannot_be_skipped(cutoff):
    with pytest.raises(locks.CommitmentInvalid):
        locks.verify_public_commitment(
            _commitment(DIGEST_A),
            expected_root_sha256=DIGEST_A,
            must_precede_unix=cutoff,
            **_ANCHOR,
        )


def test_prb6_08_status_reports_a_delivered_verifier_and_a_derived_round():
    status = locks.blocker_status()["PRB-6"]
    assert status["verifier_delivered"] is True
    assert status["chain_parameters_pinned_in_adapter"] is True
    assert status["round_derived_never_supplied"] is True
    assert status["human_review_required"] is True
    assert any("NOT committed" in item for item in status["remaining_sub_obligations"])


def test_prb6_09_a_fully_formed_chain_still_never_opens_anything(tmp_path):
    """Even if every phase were to pass, the gate ends at the frozen stop."""
    path, enrolment, expected = _persisted(tmp_path)
    with pytest.raises((locks.RouteEAnalysisRefused, frame.BeaconUnavailable, frame.BeaconInvalid)):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(expected),
            must_precede_unix=_CUTOFF,
            beacon_response=None,
            verifier_path=None,
        )


# ======================================================================================
# PRB-2 and PRB-3  one frozen order, on every public path, with no believed root
# ======================================================================================


def test_prb3_01_the_frozen_order_is_exactly_the_declared_one():
    assert locks.CHECK_ORDER == ("LOCAL_EVIDENCE", "ROOT_DIGEST", "VERIFIER")
    assert locks.CHECK_PHASES == (
        "ENTRY_GUARD",
        "LOCAL_EVIDENCE",
        "ROOT_DIGEST",
        "RECEIPT_ROOT_BINDING",
        "VERIFIER",
    )
    positions = [locks.CHECK_PHASES.index(step) for step in locks.CHECK_ORDER]
    assert positions == sorted(positions)


def test_prb2_01_no_receipt_is_refused_at_the_entry_guard(tmp_path):
    path, enrolment, _ = _persisted(tmp_path)
    trace: list[str] = []
    with pytest.raises(locks.ReceiptMissing):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=None,
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
            trace=trace,
        )
    assert trace == ["ENTRY_GUARD"]


def test_prb2_02_a_receipt_must_agree_with_its_own_commitment():
    with pytest.raises(ValueError):
        locks.RouteEReceipt(root_sha256=DIGEST_A, commitment=_commitment(DIGEST_B))


def test_prb2_03_a_receipt_binding_another_root_is_refused_after_recomputation(tmp_path):
    path, enrolment, _ = _persisted(tmp_path)
    trace: list[str] = []
    with pytest.raises(locks.ReceiptInvalid) as excinfo:
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(DIGEST_B),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
            trace=trace,
        )
    assert "recomputed from the persisted evidence" in str(excinfo.value)
    assert trace == ["ENTRY_GUARD", "LOCAL_EVIDENCE", "ROOT_DIGEST", "RECEIPT_ROOT_BINDING"]
    assert "VERIFIER" not in trace


def test_prb2_04_no_public_signature_accepts_a_caller_supplied_root():
    import inspect

    for function in (locks.open_route_e_analysis, locks.route_e_entry):
        names = set(inspect.signature(function).parameters)
        assert "recomputed_root_sha256" not in names
        assert {name for name in names if name.endswith("root_sha256")} == {
            "measurement_root_sha256"
        }


def test_prb2_05_a_self_consistent_receipt_on_a_lying_root_is_rejected(tmp_path):
    """A forged receipt is internally coherent and still cannot pass: the gate does not
    believe it, it recomputes the root from the persisted evidence."""
    path, enrolment, expected = _persisted(tmp_path)
    forged_root = hashlib.sha256(b"a root nobody computed from evidence").hexdigest()
    forged = _receipt(forged_root)
    assert forged.commitment.root_sha256 == forged.root_sha256
    assert forged_root != expected
    with pytest.raises(locks.ReceiptInvalid):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=forged,
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
        )


def test_prb2_06_mutating_the_artefact_after_the_receipt_invalidates_it(tmp_path):
    path, enrolment, expected = _persisted(tmp_path)
    receipt = _receipt(expected)
    raw = path.read_bytes()
    path.unlink()
    path.write_bytes(raw + b" ")
    with pytest.raises(locks.EvidenceInvalid):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=receipt,
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
        )


def test_prb2_07_a_different_enrolment_breaks_the_binding(tmp_path):
    path, _, expected = _persisted(tmp_path)
    with pytest.raises(locks.ReceiptInvalid):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=_enrolment("RUN-SYNTHETIC-9999"),
            receipt=_receipt(expected),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
        )


def test_prb2_08_authenticity_is_now_delegated_to_the_pinned_verifier():
    status = locks.blocker_status()["PRB-2"]
    assert status["root_recomputed_from_reread_bytes"] is True
    assert status["authenticity_established"] is True
    assert status["integration_into_accepted_sources"] is False
    assert "no callback" in status["authenticity_mechanism"]


def test_prb3_02_a_missing_artefact_stops_before_root_and_verifier(tmp_path):
    calls: list[str] = []

    def spy(commitment):
        calls.append("verifier")  # pragma: no cover - must never run
        return True

    trace: list[str] = []
    with pytest.raises(locks.EvidenceInvalid):
        locks.open_route_e_analysis(
            evidence_path=tmp_path / "absent.json",
            measurement_root_sha256=DIGEST_C,
            family_enrolment=_enrolment(),
            receipt=_receipt(DIGEST_A),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
            trace=trace,
        )
    assert trace == ["ENTRY_GUARD", "LOCAL_EVIDENCE"]
    assert calls == []


def test_prb3_03_the_verifier_phase_runs_last_and_is_reached(tmp_path):
    """Every earlier phase passes, so the run reaches VERIFIER and stops there."""
    path, enrolment, expected = _persisted(tmp_path)
    trace: list[str] = []
    with pytest.raises(frame.BeaconUnavailable):
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(expected),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
            trace=trace,
        )
    assert trace == [
        "ENTRY_GUARD",
        "LOCAL_EVIDENCE",
        "ROOT_DIGEST",
        "RECEIPT_ROOT_BINDING",
        "VERIFIER",
    ]


def test_prb3_04_the_order_cannot_be_reordered():
    order = locks._OrderTrace()
    order.enter("LOCAL_EVIDENCE")
    with pytest.raises(locks.CheckOrderViolation):
        order.enter("VERIFIER")


def test_prb3_05_both_public_entries_use_the_one_internal_path():
    import inspect

    for function in (locks.open_route_e_analysis, locks.route_e_entry):
        assert "_frozen_check_order" in inspect.getsource(function)


def test_prb3_06_the_cutoff_is_mandatory_on_both_public_entries(tmp_path):
    import inspect

    for function in (locks.open_route_e_analysis, locks.route_e_entry):
        parameter = inspect.signature(function).parameters["must_precede_unix"]
        assert parameter.default in (inspect.Parameter.empty, None)
    path, enrolment, expected = _persisted(tmp_path)
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.open_route_e_analysis(
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(expected),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=None,
        )
    assert "no public-priority cutoff" in str(excinfo.value)


def test_prb3_07_the_facade_enforces_the_same_order(tmp_path):
    path, enrolment, expected = _persisted(tmp_path)
    calls: list[str] = []

    def spy(commitment):
        calls.append("verifier")  # pragma: no cover - must never run
        return True

    with pytest.raises(locks.EvidenceInvalid):
        locks.route_e_entry(
            locks.SUPPORTED_ENTRY_POINTS[0],
            authorisation=_authorisation(),
            evidence_path=tmp_path / "absent.json",
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(expected),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=_CUTOFF,
        )
    assert calls == []
    with pytest.raises(locks.CommitmentInvalid):
        locks.route_e_entry(
            locks.SUPPORTED_ENTRY_POINTS[0],
            authorisation=_authorisation(),
            evidence_path=path,
            measurement_root_sha256=DIGEST_C,
            family_enrolment=enrolment,
            receipt=_receipt(expected),
            beacon_response=None,
            verifier_path=None,
            must_precede_unix=None,
        )
    assert calls == []


# ======================================================================================
# PRB-5.  The five REAL entry points, their typed guard and their call graph are tested
# in tests/test_future_route_e_pre_run_integration_00.py.  What remains here is the
# facade -- which is NOT a gate -- and the honest status.
# ======================================================================================


def test_prb5_01_the_five_literal_entry_points_are_enumerated():
    assert len(locks.SUPPORTED_ENTRY_POINTS) == 5
    assert locks.ROUTE_E_GUARDED_ENTRY_POINTS == locks.SUPPORTED_ENTRY_POINTS
    for name in (
        "run_owned_future_pipeline",
        "open_owned_analysis_access",
        "future_lifecycle_runner.open_analysis_access",
        "publish_future_family_completion",
        "qualify_and_write_lifecycle_contract",
    ):
        assert any(name in entry for entry in locks.SUPPORTED_ENTRY_POINTS)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_facade_01_refuses_without_authorisation(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused) as excinfo:
            locks.route_e_entry(entry_point, authorisation=None)
    assert "requires a Route E authorisation" in str(excinfo.value)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_facade_02_refuses_an_invalid_authorisation(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused):
            locks.route_e_entry(entry_point, authorisation=_authorisation(granted=False))


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_facade_03_refuses_without_a_receipt(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.ReceiptMissing):
            locks.route_e_entry(entry_point, authorisation=_authorisation(), receipt=None)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_facade_04_reaches_the_frozen_stop_and_no_further(
    entry_point, tmp_path, monkeypatch
):
    path, enrolment, expected = _persisted(tmp_path)
    with ForbiddenEffects(monkeypatch, arm_reads=False):
        with pytest.raises(frame.BeaconUnavailable):
            locks.route_e_entry(
                entry_point,
                authorisation=_authorisation(),
                evidence_path=path,
                measurement_root_sha256=DIGEST_C,
                family_enrolment=enrolment,
                receipt=_receipt(expected),
                must_precede_unix=_CUTOFF,
                beacon_response=None,
                verifier_path=None,
            )


def test_prb5_facade_05_an_unknown_entry_point_is_refused(monkeypatch):
    with ForbiddenEffects(monkeypatch):
        for bad in ("run_everything", "", 12345):
            with pytest.raises(locks.EntryPointRefused):
                locks.route_e_entry(bad, authorisation=_authorisation())


def test_prb5_facade_06_is_still_declared_not_to_be_a_gate():
    """The facade is not the integration.  The integration is the guard."""
    import inspect

    assert "not in the call graph" in locks.FACADE_IS_NOT_A_GATE
    assert "LK-L4" in locks.__doc__
    source = inspect.getsource(locks)
    for module_name in ("future_lifecycle_owned_pipeline", "future_lifecycle_runner"):
        assert f"import {module_name}" not in source


def test_prb5_07_status_records_the_guard_as_implemented_but_not_installed():
    status = locks.blocker_status()["PRB-5"]
    assert status["status"] == "OPEN"
    assert status["guard_implemented"] is True
    assert status["guard_installed"] is False
    assert status["route_e_specific_refusal_inside_accepted_sources"] is False
    assert status["facade_is_a_gate"] is False
    assert status["human_review_required"] is True


def test_prb5_08_no_blocker_is_reported_as_a_composite_token():
    status = locks.blocker_status()
    assert set(status) == {"PRB-1", "PRB-2", "PRB-3", "PRB-4", "PRB-5", "PRB-6"}
    for entry in status.values():
        assert "closed" not in entry
        assert entry["human_review_required"] is True


# ======================================================================================
# HR-1 / HR-2  terminal dispositions
# ======================================================================================


def test_hr1_01_the_five_frozen_terminal_states_are_named():
    assert frame.FROZEN_TERMINAL_STATES == (
        "DISSOLVED_DETECTED_TRACK",
        "SPLIT_INTO_TRACKS",
        "MERGED_INTO_TRACK",
        "UNRESOLVED_HANDOFF",
        "RIGHT_CENSORED_AT_HORIZON",
    )


def test_hr1_02_the_disposition_table_is_exhaustive_and_specified():
    assert set(frame.DISPOSITION_TABLE) == {d.value for d in frame.DrawDisposition}
    for row in frame.DISPOSITION_TABLE.values():
        assert row["in_denominator"] is True
        assert set(row) >= {"observed", "eligible", "Y", "in_denominator", "terminal_state"}


def test_hr1_03_censoring_is_disjoint_from_every_other_failure():
    censoring = frame.DrawDisposition.OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT
    assert frame.DISPOSITION_TABLE[censoring.value]["Y"] == 0
    quantity = frame.HORIZON_CENSORING_ATTRIBUTION.quantity
    assert "DISJOINT" in quantity
    for state in ("DISSOLVED_DETECTED_TRACK", "SPLIT_INTO_TRACKS", "MERGED_INTO_TRACK"):
        assert state in quantity


def test_hr2_01_an_unknown_draw_never_becomes_a_zero():
    assert frame.draw_score(frame.DrawDisposition.TECHNICALLY_UNKNOWN) is None
    assert frame.draw_score(frame.DrawDisposition.SUCCESS) == 1
    assert frame.draw_score(frame.DrawDisposition.MECHANICALLY_INELIGIBLE) == 0


def test_hr2_02_observed_failures_score_zero_and_stay_in_the_denominator():
    for disposition in frame.DrawDisposition:
        row = frame.DISPOSITION_TABLE[disposition.value]
        assert row["in_denominator"] is True
        if disposition is frame.DrawDisposition.SUCCESS:
            assert row["Y"] == 1
        elif disposition is frame.DrawDisposition.TECHNICALLY_UNKNOWN:
            assert row["Y"] is None
        else:
            assert row["Y"] == 0


def test_hr2_03_robust_rule_reduces_to_the_frozen_rule_without_unknowns():
    for successes in range(0, frame.N_LAW_DRAWS + 1):
        expected = (
            "POSITIVE"
            if successes >= frame.POSITIVE_MIN_K
            else "NEGATIVE"
            if successes <= frame.NEGATIVE_MAX_K
            else "INDETERMINATE"
        )
        assert frame.robust_verdict(successes=successes, unknowns=0) == expected


def test_hr2_04_robust_rule_never_imputes_unknowns():
    """Exhaustive: every decision returned must hold for EVERY completion."""
    for successes in range(0, frame.N_LAW_DRAWS + 1):
        for unknowns in range(0, frame.N_LAW_DRAWS + 1 - successes):
            verdict = frame.robust_verdict(successes=successes, unknowns=unknowns)
            possible = {
                "POSITIVE"
                if successes + extra >= frame.POSITIVE_MIN_K
                else "NEGATIVE"
                if successes + extra <= frame.NEGATIVE_MAX_K
                else "INDETERMINATE"
                for extra in range(unknowns + 1)
            }
            if verdict != "TECHNICAL_FAIL":
                assert possible == {verdict}
            else:
                assert unknowns > 0


def test_hr2_05_robust_rule_is_fail_closed():
    with pytest.raises(ValueError):
        frame.robust_verdict(successes=1, unknowns=0, n=66)
    with pytest.raises(ValueError):
        frame.robust_verdict(successes=60, unknowns=60)
    with pytest.raises(TypeError):
        frame.robust_verdict(successes=True, unknowns=0)


def test_hr2_06_the_censoring_boundary_is_reproduced():
    assert frame.attribute_horizon_censoring(24) == "HORIZON_CENSORING_NOT_SUFFICIENT"
    assert frame.attribute_horizon_censoring(25) == "HORIZON_CENSORING_NOT_SUFFICIENT"
    assert frame.attribute_horizon_censoring(26) == "HORIZON_CENSORING_SUFFICIENT"
    for bad in (-1, 68, True, 25.0, "25", None):
        with pytest.raises((ValueError, TypeError)):
            frame.attribute_horizon_censoring(bad)


# ======================================================================================
# HR-3  the round is keyed on a PUBLIC commitment.  HR-4 and HR-5 (the real verifier,
# WAIT/STOP, and every malformed-round case) live in test_route_e_beacon_verifier.py,
# next to the pinned adapter they belong to.
# ======================================================================================


def test_hr3_01_the_round_rule_keys_on_a_public_commitment_not_a_local_commit():
    rule = frame.BEACON_SOURCE["round_rule"]
    assert "PUBLIC" in rule
    assert "never a local git commit" in rule


def test_hr3_02_anti_reroll_is_declared_conditional_on_prb6():
    text = " ".join(frame.ANTI_REROLL)
    assert "UNPROVEN" in text or "PRB-6" in text
    assert "PRB-6" in text


def test_hr3_03_designated_round_is_derived_and_fail_closed():
    published = 1_700_000_000
    assert frame.designated_round(published) == frame.beacon_round_at_or_after(published + 86_400)
    for bad in (0, -1, True, None, 1.5):
        with pytest.raises((ValueError, TypeError)):
            frame.designated_round(bad)


def test_hr3_04_the_verifier_is_pinned_and_not_a_caller_choice():
    assert "never chosen by a caller" in frame.BEACON_VERIFIER_IS_PINNED
    assert frame.BEACON_SOURCE["dst"] == "BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"


# ======================================================================================
# HR-6 / HR-7  uniformity
# ======================================================================================


def test_hr6_01_the_integer_draw_has_no_modulo_bias():
    modulus = 3
    limit = (2**64 // modulus) * modulus
    assert limit % modulus == 0
    assert 2**64 - limit == 2**64 % modulus
    counts = {0: 0, 1: 0, 2: 0}
    for index in range(3000):
        counts[frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", index, modulus)] += 1
    assert sum(counts.values()) == 3000
    assert all(value > 800 for value in counts.values())


def test_hr6_02_the_integer_draw_is_deterministic_and_fail_closed():
    first = [frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", i, 3) for i in range(20)]
    second = [frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", i, 3) for i in range(20)]
    assert first == second
    for bad in (0, -1, True, 2**33):
        with pytest.raises(ValueError):
            frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", 0, bad)


def test_hr6_03_the_size_draw_uses_the_unbiased_path():
    import inspect

    source = inspect.getsource(frame.build_draw_plan)
    assert "draw_index_below" in source
    assert "int(draw_uniform" not in source
    assert "LATTICE_SIZES[draw_index_below(" in source
    plan_text = " ".join(frame.CANONICAL_DRAW_ORDER)
    assert "no floor(3*u) shortcut" in plan_text
    assert "EXACTLY uniform index" in plan_text


def test_hr6_04_the_four_uniformity_claims_are_distinguished():
    assert set(frame.UNIFORMITY_STATEMENT) == {
        "1_ideal_continuous",
        "2_realised_grid",
        "3_exact_on_the_grid",
        "4_approximation_bound",
    }
    assert "NO LITERAL EQUALITY WITH LEBESGUE MEASURE IS CLAIMED" in (
        frame.UNIFORMITY_STATEMENT["4_approximation_bound"]
    )


def test_hr6_05_the_declared_resolution_bound_is_the_real_one():
    import math

    cap = 2 * math.log(frame.HORIZON_STEPS / 4)
    assert cap == frame.PROPOSAL_BOX["affinity_sum_cap"]
    # PILOT_READINESS_00: under U53_TOP_BITS_V1 the realised grid step is (hi-lo)/2**53.
    # The superseded values on these lines were 6.0e-19 and 3.3e-21 over 2**64.
    assert abs(cap / 2**53 - 1.2312767348986591e-15) < 1e-25
    low, high = frame.PROPOSAL_BOX["rate_interval"]
    assert abs((high - low) / 2**53 - 6.830473686658678e-18) < 1e-28
    assert "1.2e-15" in frame.UNIFORMITY_STATEMENT["2_realised_grid"]
    assert "6.8e-18" in frame.UNIFORMITY_STATEMENT["2_realised_grid"]


def test_hr6_06_the_frame_no_longer_claims_exact_uniformity_on_the_continuum():
    import inspect

    source = inspect.getsource(frame.propose_law_fields)
    assert "EXACTLY ON THE FINITE DYADIC GRID" in source
    assert "not on the continuum" in source


def test_hr7_01_the_analytic_rejection_proof_is_present_and_complete():
    proof = frame.REJECTION_PROOF
    assert "Proof." in proof
    assert "QED" in proof
    assert "1/|A|" in proof
    assert "independent of a" in proof


# ======================================================================================
# HR-8 / HR-9  estimand and ceiling
# ======================================================================================


def test_hr8_01_every_missing_axis_is_now_present():
    for key in (
        "numerator",
        "denominator",
        "invalid_cases",
        "relation_to_censoring",
        "relation_to_mechanical_ineligibility",
        "no_retroactive_effect",
    ):
        assert key in frame.DELTA_DEFINITION


def test_hr8_02_the_denominator_is_frozen_and_never_reduced():
    assert "exactly 67" in frame.DELTA_DEFINITION["denominator"]
    for bad in (66, 68, 0, 1):
        with pytest.raises(ValueError):
            frame.robust_verdict(successes=0, unknowns=0, n=bad)
    with pytest.raises(frame.ClaimRefused):
        frame.RouteEClaim(
            estimand=frame.Estimand.DELTA_F_001,
            scope=frame.ClaimScope.DRAW_LEVEL_FROZEN_FRAME,
            verdict=frame.ClaimVerdict.POSITIVE,
            k=42,
            n=66,
            ci_low=0.5,
            ci_high=0.6,
        )


def test_hr8_03_invalid_cases_map_to_unknown_not_to_zero():
    assert "TECHNICALLY_UNKNOWN" in frame.DELTA_DEFINITION["invalid_cases"]
    assert "never 0" in frame.DELTA_DEFINITION["invalid_cases"]


@pytest.mark.parametrize(
    "claim",
    [
        "The component owns its internal information.",
        "Each entity governs its own repair after damage.",
        "This generalises to every law distribution.",
        "Evidence of complex life in the lattice.",
        "We found no dependence on initial conditions.",
        "The blob is self-maintaining and self-producing.",
    ],
)
def test_hr9_01_every_recorded_bypass_now_fails_the_screen(claim):
    within, offending = frame.lexical_ceiling_screen(claim)
    assert within is False
    assert offending


def test_hr9_02_the_screen_is_documented_as_a_limited_aid_not_a_guarantee():
    doc = frame.lexical_ceiling_screen.__doc__
    assert "LIMITED SOFTWARE AID" in doc
    assert "RE-L9" in frame.__doc__


def test_hr9_03_the_enforceable_ceiling_is_a_closed_vocabulary_object():
    claim = frame.RouteEClaim(
        estimand=frame.Estimand.DELTA_F_001,
        scope=frame.ClaimScope.DRAW_LEVEL_FROZEN_FRAME,
        verdict=frame.ClaimVerdict.POSITIVE,
        k=42,
        n=67,
        ci_low=0.500105,
        ci_high=0.742026,
    )
    lowered = frame.render_claim(claim).lower()
    for banned in ("own", "alive", "autonom", "individual", "reconstruct", "hered", "self-"):
        assert banned not in lowered


@pytest.mark.parametrize(
    "kwargs",
    [
        {"estimand": "Delta"},
        {"scope": "anything"},
        {"verdict": "PROVEN"},
        {"k": 68},
        {"n": 66},
        {"ci_low": 1.5},
        {"ci_low": 0.9, "ci_high": 0.1},
    ],
)
def test_hr9_04_the_claim_object_refuses_anything_outside_the_schema(kwargs):
    base = dict(
        estimand=frame.Estimand.DELTA_F_001,
        scope=frame.ClaimScope.DRAW_LEVEL_FROZEN_FRAME,
        verdict=frame.ClaimVerdict.POSITIVE,
        k=42,
        n=67,
        ci_low=0.5,
        ci_high=0.7,
    )
    base.update(kwargs)
    with pytest.raises(frame.ClaimRefused):
        frame.RouteEClaim(**base)


def test_hr9_05_free_text_can_never_be_rendered_as_a_claim():
    with pytest.raises(frame.ClaimRefused):
        frame.render_claim("The component owns its information.")


def test_hr9_06_every_verdict_has_exactly_one_authorised_template():
    assert set(frame.CLAIM_TEMPLATES) == {v.value for v in frame.ClaimVerdict}


# ======================================================================================
# HR-10  the classifier is not substitutable on the public path
# ======================================================================================


def test_hr10_01_the_public_api_has_no_classifier_parameter():
    import inspect

    assert "classifier" not in inspect.signature(frame.assemble_draw_outcome).parameters
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    with pytest.raises(TypeError):
        frame.assemble_draw_outcome(
            tracking,
            persisted_to_horizon=True,
            replacement_verified=True,
            eligible=True,
            classifier=lambda t: (),
        )


def test_hr10_02_the_public_path_passes_the_real_classifier_exactly_once(monkeypatch):
    calls: list[int] = []
    real = frame.classify_track_terminations

    def counting(tracking):
        calls.append(1)
        return real(tracking)

    monkeypatch.setattr(frame, "classify_track_terminations", counting)
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=False, eligible=True
    )
    assert calls == [1]
    assert outcome.disposition is (
        frame.DrawDisposition.OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT
    )


def test_hr10_03_the_outcome_really_depends_on_the_classifier_result(monkeypatch):
    """Neutralising the classifier changes the outcome, so the call is load-bearing."""
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    genuine = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=False, eligible=True
    )
    assert genuine.association_gate_breaks >= 1
    monkeypatch.setattr(frame, "classify_track_terminations", lambda t: ())
    neutralised = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=False, eligible=True
    )
    assert neutralised.association_gate_breaks == 0
    assert neutralised.terminations == ()


_AMBIGUOUS_F0 = [(0, 0), (0, 1), (1, 0), (1, 1), (8, 8), (8, 9), (9, 8), (9, 9)]
_AMBIGUOUS_F1 = [(6, 8), (6, 9), (6, 10), (11, 8), (11, 9), (11, 10)]


def test_hr10_04_an_ambiguous_termination_is_fail_closed():
    tracking = _track([_AMBIGUOUS_F0, _AMBIGUOUS_F1])
    states = {item.terminal_state for item in frame.classify_track_terminations(tracking)}
    assert len(states) >= 2
    with pytest.raises(frame.AmbiguousTermination):
        frame.assemble_draw_outcome(
            tracking, persisted_to_horizon=False, replacement_verified=False, eligible=True
        )


def test_hr10_05_a_genuine_dissolution_resolves_to_one_observed_failure():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=False, replacement_verified=False, eligible=True
    )
    assert outcome.disposition is frame.DrawDisposition.OBSERVED_FAILURE_DISSOLVED
    assert outcome.score == 0


def test_hr10_06_broken_evidence_is_unknown_not_zero():
    tracking = _track([_BLOB_LEFT, _BLOB_LEFT])
    outcome = frame.assemble_draw_outcome(
        tracking,
        persisted_to_horizon=True,
        replacement_verified=True,
        eligible=True,
        evidence_ok=False,
    )
    assert outcome.disposition is frame.DrawDisposition.TECHNICALLY_UNKNOWN
    assert outcome.score is None


def test_hr10_07_an_ineligible_draw_is_a_true_zero_in_the_denominator():
    tracking = _track([_BLOB_LEFT, _BLOB_LEFT])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=True, eligible=False
    )
    assert outcome.disposition is frame.DrawDisposition.MECHANICALLY_INELIGIBLE
    assert outcome.score == 0
    assert frame.DISPOSITION_TABLE[outcome.disposition.value]["in_denominator"] is True


def test_hr10_08_assembly_is_fail_closed_and_idempotent():
    tracking = _track([_BLOB_LEFT, _BLOB_LEFT])
    for bad in ({"persisted_to_horizon": 1}, {"eligible": None}, {"evidence_ok": "yes"}):
        kwargs = dict(persisted_to_horizon=True, replacement_verified=True, eligible=True)
        kwargs.update(bad)
        with pytest.raises(TypeError):
            frame.assemble_draw_outcome(tracking, **kwargs)
    first = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=True, eligible=True
    )
    second = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=True, eligible=True
    )
    assert first == second


def test_hr10_09_the_anticipatory_scope_is_declared_not_hidden():
    assert "RE-L10" in frame.__doc__
    doc = " ".join(frame.assemble_draw_outcome.__doc__.split())
    assert "this function is not called by any accepted source" in doc
    assert "not an integration into production" in doc
    assert "must not be attributed to the production tracker" in doc


# ======================================================================================
# HR-11  the section 8 title and scope
# ======================================================================================


def test_hr11_01_the_section_8_title_and_scope_are_restored():
    doc = frame.__doc__
    assert "Obligations portees a la preregistration" in doc
    assert "ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00" in doc
    assert "pourra" in doc and "PRE_RUN_BLOCKER" in doc
    assert "never renamed" in doc
    assert "future_route_e_pre_run_locks.py" in doc


# ======================================================================================
# Firewall
# ======================================================================================


def test_firewall_01_scientific_run_is_not_authorised():
    assert frame.SCIENTIFIC_RUN_AUTHORIZED is False


def test_firewall_02_no_module_level_scientific_entity_exists():
    for module in (frame, locks):
        for name in (
            "SEED",
            "SCIENTIFIC_SEED",
            "SEED_ROOT",
            "BEACON_ROUND",
            "FAMILY",
            "NAMESPACE",
            "LAW_SPEC",
            "WORLD",
        ):
            assert not hasattr(module, name)


def test_firewall_03_no_designated_round_is_selected_at_import_time():
    import inspect

    source = inspect.getsource(frame)
    assert "def designated_round(" in source
    body = source.split("def designated_round(")[1].split("\n\n\ndef ")[0]
    assert "designated_round(" not in body


def test_firewall_04_the_locks_module_creates_no_scientific_artefact(tmp_path, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.ReceiptMissing):
            locks.route_e_entry(
                locks.SUPPORTED_ENTRY_POINTS[0], authorisation=_authorisation()
            )
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_firewall_05_the_evidence_writer_stays_inside_its_declared_root(tmp_path):
    root_dir = tmp_path / "evidence"
    root_dir.mkdir()
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    locks.write_join_evidence(root_dir, _records())
    assert sorted(p.name for p in root_dir.iterdir()) == [locks.JOIN_EVIDENCE_FILENAME]
    assert sorted(p.name for p in sibling.iterdir()) == []
