"""Mechanical pins for the MISSION MANDATE of FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00:
the six frozen PRE_RUN_BLOCKERs PRB-1 .. PRB-6, plus the eleven corrections HR-1 .. HR-11
ordered by the human review ``bc2a42c468eec5a4e1732ebb08c7cc20c4dab7dd``.

Every test uses synthetic deterministic fixtures and temporary directories.  None opens
Stage B, M_MINUS, a trajectory, a shard, a candidate or any historical result.  None
creates a scientific seed, beacon round, family, namespace, law, initial condition or
world.  None contacts the network.  None steps the engine.
"""

from __future__ import annotations

import builtins
import hashlib
import os
import socket
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks
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
    write, directory creation and the engine.  It does NOT claim to cover effects outside
    this list; that is the honest limit of the proof.
    """

    TARGETS = (
        "entropy(os.urandom)",
        "network(socket.socket)",
        "subprocess(subprocess.Popen)",
        "file(builtins.open)",
        "write(Path.write_bytes)",
        "write(Path.write_text)",
        "mkdir(Path.mkdir)",
        "engine(LatticeBondEngine.step)",
    )

    def __init__(self, monkeypatch):
        self.monkeypatch = monkeypatch
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


def _commitment(root, published_at=1_700_000_000):
    return locks.PublicCommitment(
        root_sha256=root,
        venue="TEST_ONLY append-only log",
        reference="TEST_ONLY/0001",
        published_at_unix=published_at,
    )


def _receipt(root, published_at=1_700_000_000):
    return locks.RouteEReceipt(root_sha256=root, commitment=_commitment(root, published_at))


def _accepting_verifier(commitment):
    return True


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
    a = locks.canonical_cell_set_digest((16, 16), [5, 1, 9])
    b = locks.canonical_cell_set_digest((16, 16), [9, 5, 1, 5])
    c = locks.canonical_cell_set_digest((24, 24), [5, 1, 9])
    assert a == b  # order and duplicates are irrelevant
    assert a != c  # the lattice shape is bound


@pytest.mark.parametrize(
    "args",
    [
        ((16,), [1]),
        ((16, 16), []),
        ((16, 16), [999999]),
        ((16, 16), "12"),
        ((1, 16), [1]),
        ((16, 16), [True]),
    ],
)
def test_prb1_05_cell_set_digest_is_fail_closed(args):
    with pytest.raises((TypeError, ValueError)):
        locks.canonical_cell_set_digest(*args)


def test_prb1_06_join_is_built_for_every_assignment():
    fixture = [_BLOB_LEFT, _BLOB_FAR]
    tracking = _track(fixture)
    records = locks.build_track_component_join(tracking, _support_map(fixture))
    assert len(records) == len(tracking.assignments)
    assert all(isinstance(r, locks.JoinRecord) for r in records)
    assert list(records) == sorted(records, key=locks.JoinRecord.as_tuple)


def test_prb1_07_a_missing_component_support_is_refused_not_dropped():
    fixture = [_BLOB_LEFT, _BLOB_FAR]
    tracking = _track(fixture)
    support = _support_map(fixture)
    support[1].pop(next(iter(support[1])))
    with pytest.raises(ValueError):
        locks.build_track_component_join(tracking, support)


def test_prb1_08_join_digest_is_order_independent_and_refuses_emptiness():
    records = [
        locks.JoinRecord(frame=0, cell_set_sha256=DIGEST_A, track_id=0),
        locks.JoinRecord(frame=16, cell_set_sha256=DIGEST_B, track_id=1),
    ]
    assert locks.join_digest(records) == locks.join_digest(list(reversed(records)))
    with pytest.raises(ValueError):
        locks.join_digest([])
    with pytest.raises(TypeError):
        locks.join_digest(["not a record"])


def test_prb1_09_the_join_is_bound_into_the_root():
    fixture = [_BLOB_LEFT, _BLOB_FAR]
    records = locks.build_track_component_join(_track(fixture), _support_map(fixture))
    digest = locks.join_digest(records)
    root = locks.route_e_root(
        measurement_root_sha256=DIGEST_A,
        track_component_join_digest=digest,
        family_enrolment_digest=DIGEST_B,
    )
    other = locks.route_e_root(
        measurement_root_sha256=DIGEST_A,
        track_component_join_digest=DIGEST_C,
        family_enrolment_digest=DIGEST_B,
    )
    assert root != other  # changing the join changes the root


# ======================================================================================
# PRB-4  replay binding
# ======================================================================================


def _enrolment(run_identity="RUN-SYNTHETIC-0001", seed=DIGEST_A, plan=DIGEST_B):
    return locks.FamilyEnrolment(
        run_identity=run_identity,
        seed_root_sha256=seed,
        draw_plan_digest=plan,
        n_draws=67,
        worlds=134,
    )


def test_prb4_01_enrolment_binds_run_identity_seed_and_plan():
    base = locks.enrolment_digest(_enrolment())
    assert base != locks.enrolment_digest(_enrolment(run_identity="RUN-SYNTHETIC-0002"))
    assert base != locks.enrolment_digest(_enrolment(seed=DIGEST_C))
    assert base != locks.enrolment_digest(_enrolment(plan=DIGEST_C))
    assert base == locks.enrolment_digest(_enrolment())


@pytest.mark.parametrize(
    "kwargs",
    [
        {"run_identity": "short"},
        {"seed": "nope"},
        {"plan": "nope"},
    ],
)
def test_prb4_02_enrolment_is_fail_closed(kwargs):
    with pytest.raises(ValueError):
        _enrolment(**kwargs)


def test_prb4_03_a_bit_identical_copy_under_another_identity_does_not_replay():
    """The whole point of PRB-4: same evidence, different run identity, different root."""
    join = DIGEST_C
    first = locks.route_e_root(
        measurement_root_sha256=DIGEST_A,
        track_component_join_digest=join,
        family_enrolment_digest=locks.enrolment_digest(_enrolment("RUN-SYNTHETIC-0001")),
    )
    replay = locks.route_e_root(
        measurement_root_sha256=DIGEST_A,  # identical evidence
        track_component_join_digest=join,  # identical join
        family_enrolment_digest=locks.enrolment_digest(_enrolment("RUN-SYNTHETIC-0002")),
    )
    assert first != replay


@pytest.mark.parametrize("bad", ["", "zz" * 32, DIGEST_A[:-1], 12345])
def test_prb4_04_root_is_fail_closed(bad):
    with pytest.raises(ValueError):
        locks.route_e_root(
            measurement_root_sha256=bad,
            track_component_join_digest=DIGEST_B,
            family_enrolment_digest=DIGEST_C,
        )


# ======================================================================================
# PRB-6  external anchoring of the final root
# ======================================================================================


def test_prb6_01_absent_commitment_is_refused():
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.verify_public_commitment(
            None, verifier=_accepting_verifier, expected_root_sha256=DIGEST_A
        )
    assert "no public commitment" in str(excinfo.value)


def test_prb6_02_a_commitment_binding_another_root_is_refused():
    with pytest.raises(locks.CommitmentInvalid):
        locks.verify_public_commitment(
            _commitment(DIGEST_B), verifier=_accepting_verifier, expected_root_sha256=DIGEST_A
        )


def test_prb6_03_no_verifier_means_refusal_never_a_default():
    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.verify_public_commitment(
            _commitment(DIGEST_A), verifier=None, expected_root_sha256=DIGEST_A
        )
    assert "no commitment verifier" in str(excinfo.value)


@pytest.mark.parametrize(
    "verifier",
    [
        lambda c: False,
        lambda c: None,
        lambda c: 1,  # truthy but not True
        "not callable",
    ],
)
def test_prb6_04_only_an_exact_true_passes(verifier):
    with pytest.raises(locks.CommitmentInvalid):
        locks.verify_public_commitment(
            _commitment(DIGEST_A), verifier=verifier, expected_root_sha256=DIGEST_A
        )


def test_prb6_05_a_raising_verifier_is_a_refusal():
    def boom(commitment):
        raise RuntimeError("network down")

    with pytest.raises(locks.CommitmentInvalid) as excinfo:
        locks.verify_public_commitment(
            _commitment(DIGEST_A), verifier=boom, expected_root_sha256=DIGEST_A
        )
    assert "raised" in str(excinfo.value)


def test_prb6_06_priority_is_strict_which_is_the_anti_reroll_condition():
    """HR-3: a commitment published at or after the reveal cannot bind it."""
    locks.verify_public_commitment(
        _commitment(DIGEST_A, published_at=1000),
        verifier=_accepting_verifier,
        expected_root_sha256=DIGEST_A,
        must_precede_unix=1001,
    )
    for published_at in (1001, 1002):
        with pytest.raises(locks.CommitmentInvalid) as excinfo:
            locks.verify_public_commitment(
                _commitment(DIGEST_A, published_at=published_at),
                verifier=_accepting_verifier,
                expected_root_sha256=DIGEST_A,
                must_precede_unix=1001,
            )
        assert "strictly prior" in str(excinfo.value)


def test_prb6_07_status_reports_prb6_as_open_not_closed():
    """The verifier itself is not delivered; the report must say so."""
    status = locks.blocker_status()
    assert status["PRB-6"]["closed"] is False
    assert "OPEN" in status["PRB-6"]["residue"]
    assert "LK-L2" in locks.__doc__


# ======================================================================================
# PRB-2  mandatory receipt   /   PRB-3  frozen check order
# ======================================================================================


def test_prb3_01_the_frozen_order_is_exactly_the_declared_one():
    assert locks.CHECK_ORDER == ("LOCAL_EVIDENCE", "ROOT_DIGEST", "VERIFIER")


def test_prb3_02_failure_at_local_evidence_stops_before_root_digest():
    trace: list[str] = []
    with pytest.raises(locks.RouteEAnalysisRefused):
        locks.open_route_e_analysis(
            local_evidence_ok=False,
            recomputed_root_sha256=DIGEST_A,
            receipt=_receipt(DIGEST_A),
            verifier=_accepting_verifier,
            trace=trace,
        )
    assert trace == ["LOCAL_EVIDENCE"]


def test_prb2_01_no_receipt_is_refused_at_root_digest():
    trace: list[str] = []
    with pytest.raises(locks.ReceiptMissing):
        locks.open_route_e_analysis(
            local_evidence_ok=True,
            recomputed_root_sha256=DIGEST_A,
            receipt=None,
            verifier=_accepting_verifier,
            trace=trace,
        )
    assert trace == ["LOCAL_EVIDENCE", "ROOT_DIGEST"]


def test_prb2_02_a_receipt_binding_another_root_is_refused():
    with pytest.raises(locks.ReceiptInvalid):
        locks.open_route_e_analysis(
            local_evidence_ok=True,
            recomputed_root_sha256=DIGEST_A,
            receipt=_receipt(DIGEST_B),
            verifier=_accepting_verifier,
        )


def test_prb2_03_a_receipt_must_agree_with_its_own_commitment():
    with pytest.raises(ValueError):
        locks.RouteEReceipt(root_sha256=DIGEST_A, commitment=_commitment(DIGEST_B))


def test_prb3_03_failure_at_root_digest_stops_before_verifier():
    trace: list[str] = []
    with pytest.raises(locks.ReceiptInvalid):
        locks.open_route_e_analysis(
            local_evidence_ok=True,
            recomputed_root_sha256=DIGEST_A,
            receipt=_receipt(DIGEST_B),
            verifier=_accepting_verifier,
            trace=trace,
        )
    assert trace == ["LOCAL_EVIDENCE", "ROOT_DIGEST"]
    assert "VERIFIER" not in trace


def test_prb3_04_the_verifier_runs_only_third_and_is_reached_last():
    calls: list[str] = []

    def spy(commitment):
        calls.append("verifier")
        return True

    trace: list[str] = []
    with pytest.raises(locks.RouteEAnalysisRefused) as excinfo:
        locks.open_route_e_analysis(
            local_evidence_ok=True,
            recomputed_root_sha256=DIGEST_A,
            receipt=_receipt(DIGEST_A),
            verifier=spy,
            trace=trace,
        )
    assert trace == ["LOCAL_EVIDENCE", "ROOT_DIGEST", "VERIFIER"]
    assert calls == ["verifier"]
    assert "scientific_run_authorized is False" in str(excinfo.value)


def test_prb3_05_the_order_cannot_be_reordered():
    order = locks._OrderTrace()
    order.enter("LOCAL_EVIDENCE")
    with pytest.raises(locks.CheckOrderViolation):
        order.enter("VERIFIER")


def test_prb3_06_the_gate_never_returns_even_when_all_three_pass():
    with pytest.raises(locks.RouteEAnalysisRefused):
        locks.open_route_e_analysis(
            local_evidence_ok=True,
            recomputed_root_sha256=DIGEST_A,
            receipt=_receipt(DIGEST_A),
            verifier=_accepting_verifier,
        )


# ======================================================================================
# PRB-5  single supported entry point -- one refusal test PER entry point
# ======================================================================================


def test_prb5_01_the_five_literal_entry_points_are_enumerated():
    assert len(locks.SUPPORTED_ENTRY_POINTS) == 5
    for name in (
        "run_owned_future_pipeline",
        "open_owned_analysis_access",
        "future_lifecycle_runner.open_analysis_access",
        "publish_future_family_completion",
        "qualify_and_write_lifecycle_contract",
    ):
        assert any(name in entry for entry in locks.SUPPORTED_ENTRY_POINTS)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_02_every_entry_point_refuses_without_authorisation(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused) as excinfo:
            locks.route_e_entry(entry_point, authorisation=None)
    assert "requires a Route E authorisation" in str(excinfo.value)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_03_every_entry_point_refuses_an_invalid_authorisation(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused):
            locks.route_e_entry(entry_point, authorisation=_authorisation(granted=False))


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_04_every_entry_point_refuses_without_a_receipt(entry_point, monkeypatch):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.ReceiptMissing):
            locks.route_e_entry(entry_point, authorisation=_authorisation(), receipt=None)


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_05_every_entry_point_refuses_without_a_commitment_verifier(
    entry_point, monkeypatch
):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.CommitmentInvalid):
            locks.route_e_entry(
                entry_point,
                authorisation=_authorisation(),
                receipt=_receipt(DIGEST_A),
                verifier=None,
            )


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_06_every_entry_point_refuses_even_when_everything_else_passes(
    entry_point, monkeypatch
):
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused) as excinfo:
            locks.route_e_entry(
                entry_point,
                authorisation=_authorisation(),
                receipt=_receipt(DIGEST_A),
                verifier=_accepting_verifier,
            )
    assert "scientific_run_authorized is False" in str(excinfo.value)


def test_prb5_07_an_unknown_entry_point_is_refused(monkeypatch):
    with ForbiddenEffects(monkeypatch):
        for bad in ("run_everything", "", 12345):
            with pytest.raises(locks.EntryPointRefused):
                locks.route_e_entry(bad, authorisation=_authorisation())


@pytest.mark.parametrize("entry_point", locks.SUPPORTED_ENTRY_POINTS)
def test_prb5_08_the_gate_never_dispatches_to_the_accepted_function(entry_point, monkeypatch):
    """The accepted callables are replaced by spies; none of them may be reached."""
    from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
    from edlab.substrates.lattice_bond import future_lifecycle_runner as runner
    from edlab.substrates.lattice_bond import lifecycle as lifecycle_module

    reached: list[str] = []

    def spy(name):
        def _call(*args, **kwargs):  # pragma: no cover - must never run
            reached.append(name)
            raise AssertionError(f"the gate dispatched to {name}")

        return _call

    monkeypatch.setattr(owned, "run_owned_future_pipeline", spy("run_owned_future_pipeline"))
    monkeypatch.setattr(owned, "open_owned_analysis_access", spy("open_owned_analysis_access"))
    monkeypatch.setattr(runner, "open_analysis_access", spy("open_analysis_access"))
    monkeypatch.setattr(
        runner, "publish_future_family_completion", spy("publish_future_family_completion")
    )
    monkeypatch.setattr(
        lifecycle_module,
        "qualify_and_write_lifecycle_contract",
        spy("qualify_and_write_lifecycle_contract"),
    )
    with pytest.raises((locks.EntryPointRefused, locks.ReceiptMissing, locks.CommitmentInvalid)):
        locks.route_e_entry(entry_point, authorisation=_authorisation())
    assert reached == []


def test_prb5_09_status_records_the_bounded_residue():
    status = locks.blocker_status()
    assert status["PRB-5"]["closed"] is True
    assert "outside the Route E path" in status["PRB-5"]["residue"]
    assert "LK-L1" in locks.__doc__


# ======================================================================================
# HR-1 / HR-2  terminal dispositions: observed, ineligible and unknown never merge
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
    for name, row in frame.DISPOSITION_TABLE.items():
        for key in ("observed", "eligible", "Y", "in_denominator", "terminal_state", "effect"):
            assert key in row, (name, key)
        assert row["in_denominator"] is True  # the denominator is never reduced


def test_hr1_03_censoring_is_disjoint_from_every_other_failure():
    quantity = frame.HORIZON_CENSORING_ATTRIBUTION.quantity
    assert "OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT" in quantity
    assert "RIGHT_CENSORED_AT_HORIZON" in quantity
    assert "DISJOINT" in quantity
    for other in ("DISSOLVED_DETECTED_TRACK", "SPLIT_INTO_TRACKS", "MERGED_INTO_TRACK",
                  "UNRESOLVED_HANDOFF", "MECHANICALLY_INELIGIBLE", "TECHNICALLY_UNKNOWN"):
        assert other in quantity
    # exactly one disposition feeds the threshold
    feeding = [
        d for d in frame.DrawDisposition
        if frame.DISPOSITION_TABLE[d.value]["terminal_state"] == "RIGHT_CENSORED_AT_HORIZON"
        and frame.DISPOSITION_TABLE[d.value]["Y"] == 0
    ]
    assert feeding == [frame.DrawDisposition.OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT]


def test_hr2_01_an_unknown_draw_never_becomes_a_zero():
    assert frame.draw_score(frame.DrawDisposition.TECHNICALLY_UNKNOWN) is None
    assert frame.DISPOSITION_TABLE["TECHNICALLY_UNKNOWN"]["observed"] is False
    assert frame.DISPOSITION_TABLE["TECHNICALLY_UNKNOWN"]["in_denominator"] is True


def test_hr2_02_observed_failures_score_zero_and_stay_in_the_denominator():
    for disposition in (
        frame.DrawDisposition.OBSERVED_FAILURE_DISSOLVED,
        frame.DrawDisposition.OBSERVED_FAILURE_SPLIT,
        frame.DrawDisposition.OBSERVED_FAILURE_MERGED,
        frame.DrawDisposition.OBSERVED_FAILURE_UNRESOLVED,
        frame.DrawDisposition.OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT,
        frame.DrawDisposition.MECHANICALLY_INELIGIBLE,
    ):
        assert frame.draw_score(disposition) == 0
        assert frame.DISPOSITION_TABLE[disposition.value]["in_denominator"] is True
    assert frame.draw_score(frame.DrawDisposition.SUCCESS) == 1


def test_hr2_03_robust_rule_reduces_to_the_frozen_rule_without_unknowns():
    for successes in range(0, 68):
        verdict = frame.robust_verdict(successes=successes, unknowns=0)
        expected = (
            "POSITIVE" if successes >= 42 else "NEGATIVE" if successes <= 9 else "INDETERMINATE"
        )
        assert verdict == expected, successes


def test_hr2_04_robust_rule_never_imputes_unknowns():
    assert frame.robust_verdict(successes=42, unknowns=5) == "POSITIVE"
    assert frame.robust_verdict(successes=5, unknowns=4) == "NEGATIVE"
    assert frame.robust_verdict(successes=5, unknowns=5) == "TECHNICAL_FAIL"
    assert frame.robust_verdict(successes=41, unknowns=1) == "TECHNICAL_FAIL"


def test_hr2_05_robust_rule_is_fail_closed_and_idempotent():
    for bad in ({"successes": -1, "unknowns": 0}, {"successes": True, "unknowns": 0},
                {"successes": 1.0, "unknowns": 0}):
        with pytest.raises(TypeError):
            frame.robust_verdict(**bad)
    with pytest.raises(ValueError):
        frame.robust_verdict(successes=60, unknowns=60)
    with pytest.raises(ValueError):
        frame.robust_verdict(successes=1, unknowns=0, n=66)
    assert frame.robust_verdict(successes=30, unknowns=0) == frame.robust_verdict(
        successes=30, unknowns=0
    )


def test_hr2_06_the_censoring_boundary_is_reproduced_against_the_robust_rule():
    for censored in (24, 25, 26):
        best_case_k = 67 - censored
        verdict = frame.robust_verdict(successes=best_case_k, unknowns=0)
        assert (verdict == "POSITIVE") == (censored <= 25)
        assert frame.attribute_horizon_censoring(censored) == (
            "HORIZON_CENSORING_SUFFICIENT" if censored > 25 else "HORIZON_CENSORING_NOT_SUFFICIENT"
        )


# ======================================================================================
# HR-3 / HR-4 / HR-5  beacon anchoring, verification and availability
# ======================================================================================


def test_hr3_01_the_round_rule_keys_on_a_public_commitment_not_a_local_commit():
    rule = str(frame.BEACON_SOURCE["round_rule"])
    assert "PUBLIC timestamp" in rule
    assert "never a local git commit" in rule
    assert "86400" in rule


def test_hr3_02_anti_reroll_is_declared_conditional_on_prb6():
    text = " ".join(frame.ANTI_REROLL)
    assert "CONDITIONAL" in text
    assert "PRB-6" in text
    assert "UNPROVEN" in text
    assert "a local commit hash is not a public timestamp" in text


def test_hr3_03_designated_round_is_derived_and_fail_closed():
    genesis = int(frame.BEACON_SOURCE["genesis_time_unix"])
    period = int(frame.BEACON_SOURCE["period_seconds"])
    published = genesis + 10_000
    r = frame.designated_round(published)
    assert genesis + (r - 1) * period >= published + 86400
    assert genesis + (r - 2) * period < published + 86400
    for bad in (0, -1, True, 1.0):
        with pytest.raises((TypeError, ValueError)):
            frame.designated_round(bad)


def _response(round_value=100, signature=b"\x01" * 48, chain=None, randomness=None):
    chain = chain if chain is not None else frame.BEACON_SOURCE["chain_hash"]
    randomness = (
        randomness if randomness is not None else hashlib.sha256(signature).digest().hex()
    )
    return {
        "round": round_value,
        "randomness": randomness,
        "signature": signature.hex(),
        "chain_hash": chain,
    }


def test_hr5_01_an_absent_round_is_WAIT_never_a_substitution():
    with pytest.raises(frame.BeaconUnavailable) as excinfo:
        frame.consume_beacon_round(response=None, expected_round=100, verifier=lambda *a: True)
    assert frame.BeaconUnavailable.disposition == "WAIT"
    assert "never the next round" in str(excinfo.value)
    assert "never an alternative endpoint" in str(excinfo.value)


@pytest.mark.parametrize(
    "response",
    [
        {"round": 100},
        {"round": 100, "randomness": "00", "signature": "00"},
        _response(round_value=101),
        _response(chain="0" * 64),
        _response(signature=b"\x02" * 47),
        {"round": True, "randomness": "aa" * 32, "signature": "bb" * 48,
         "chain_hash": frame.BEACON_SOURCE["chain_hash"]},
        {"round": 100, "randomness": "zz", "signature": "bb" * 48,
         "chain_hash": frame.BEACON_SOURCE["chain_hash"]},
        "not a mapping",
    ],
)
def test_hr5_02_malformed_or_wrong_rounds_are_STOP(response):
    with pytest.raises(frame.BeaconInvalid):
        frame.consume_beacon_round(
            response=response, expected_round=100, verifier=lambda *a: True
        )
    assert frame.BeaconInvalid.disposition == "STOP"


def test_hr4_01_no_verifier_means_STOP_an_http_response_is_not_evidence():
    with pytest.raises(frame.BeaconInvalid) as excinfo:
        frame.consume_beacon_round(response=_response(), expected_round=100, verifier=None)
    assert "no BLS verifier supplied" in str(excinfo.value)
    assert "not evidence" in str(excinfo.value)


@pytest.mark.parametrize("verifier", [lambda *a: False, lambda *a: None, lambda *a: 1, "nope"])
def test_hr4_02_a_verifier_that_does_not_return_true_is_STOP(verifier):
    with pytest.raises(frame.BeaconInvalid):
        frame.consume_beacon_round(response=_response(), expected_round=100, verifier=verifier)


def test_hr4_03_a_raising_verifier_is_STOP():
    def boom(*args):
        raise RuntimeError("bad point")

    with pytest.raises(frame.BeaconInvalid) as excinfo:
        frame.consume_beacon_round(response=_response(), expected_round=100, verifier=boom)
    assert "raised" in str(excinfo.value)


def test_hr4_04_randomness_must_equal_sha256_of_the_signature():
    bad = _response(randomness=("11" * 32))
    with pytest.raises(frame.BeaconInvalid) as excinfo:
        frame.consume_beacon_round(response=bad, expected_round=100, verifier=lambda *a: True)
    assert "sha256(signature)" in str(excinfo.value)


def test_hr4_05_a_well_formed_verified_round_returns_the_randomness():
    """TEST_ONLY synthetic vectors; no network, no real chain data."""
    signature = b"\x07" * 48
    response = _response(signature=signature)
    out = frame.consume_beacon_round(
        response=response, expected_round=100, verifier=lambda *a: True
    )
    assert out == hashlib.sha256(signature).digest()


def test_hr4_06_the_verification_rule_is_declared_and_the_verifier_is_not_bundled():
    assert "BLS on G1" in str(frame.BEACON_SOURCE["verification_rule"])
    assert "No verifier is bundled" in str(frame.BEACON_SOURCE["verification_rule"])
    assert "WAIT" in str(frame.BEACON_SOURCE["unavailability_rule"])
    assert "STOP" in str(frame.BEACON_SOURCE["unavailability_rule"])


def test_hr4_07_no_module_contacts_the_network(monkeypatch):
    """Static and dynamic: neither module imports a client nor opens a socket."""
    import inspect

    for module in (frame, locks):
        source = inspect.getsource(module)
        for banned in ("requests", "urllib", "httpx", "http.client", "socket."):
            assert banned not in source, (module.__name__, banned)
    monkeypatch.setattr(socket, "socket", lambda *a, **k: pytest.fail("network contacted"))
    frame.consume_beacon_round(
        response=_response(), expected_round=100, verifier=lambda *a: True
    )


# ======================================================================================
# HR-6 / HR-7  the realised law, its grid, and the proof
# ======================================================================================


def test_hr6_01_the_integer_draw_has_no_modulo_bias():
    limit = (2**64 // 3) * 3
    assert limit % 3 == 0  # the accepted range is an exact multiple
    assert 2**64 - limit == 2**64 % 3
    values = [frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", i, 3) for i in range(6000)]
    assert set(values) == {0, 1, 2}
    counts = [values.count(v) for v in (0, 1, 2)]
    chi2 = sum((c - 2000) ** 2 / 2000 for c in counts)
    assert chi2 < 13.82, counts  # 0.999 quantile, 2 degrees of freedom


def test_hr6_02_the_integer_draw_is_deterministic_and_fail_closed():
    a = frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", 7, 3)
    assert a == frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", 7, 3)
    assert frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", 7, 1) == 0
    for bad in (0, -1, True, 2**33):
        with pytest.raises(ValueError):
            frame.draw_index_below(SYNTHETIC_ROOT, b"SIZE", 0, bad)


def test_hr6_03_the_size_draw_uses_the_unbiased_path():
    import inspect

    source = inspect.getsource(frame.build_draw_plan)
    assert "draw_index_below" in source
    assert "int(draw_uniform" not in source


def test_hr6_04_the_four_uniformity_claims_are_distinguished():
    statement = frame.UNIFORMITY_STATEMENT
    assert set(statement) == {
        "1_ideal_continuous",
        "2_realised_grid",
        "3_exact_on_the_grid",
        "4_approximation_bound",
    }
    assert "FINITE dyadic grid" in statement["2_realised_grid"]
    assert "EXACTLY uniform" in statement["3_exact_on_the_grid"]
    assert "NO LITERAL EQUALITY WITH LEBESGUE MEASURE IS CLAIMED" in statement[
        "4_approximation_bound"
    ]


def test_hr6_05_the_declared_resolution_bound_is_the_real_one():
    cap = frame.PROPOSAL_BOX["affinity_sum_cap"]
    low, high = frame.PROPOSAL_BOX["rate_interval"]
    theta_step = cap / 2**64
    rate_step = (high - low) / 2**64
    assert theta_step == pytest.approx(6.0e-19, rel=0.05)
    assert rate_step == pytest.approx(3.3e-21, rel=0.05)
    assert "6.0e-19" in frame.UNIFORMITY_STATEMENT["2_realised_grid"]
    assert "3.3e-21" in frame.UNIFORMITY_STATEMENT["2_realised_grid"]


def test_hr7_01_the_analytic_rejection_proof_is_present_and_complete():
    proof = frame.REJECTION_PROOF
    assert "uniform on a finite set B" in proof
    assert "1/|A|" in proof
    assert "QED" in proof
    assert "Rejected proposals are consumed" in proof


def test_hr6_06_the_frame_no_longer_claims_exact_uniformity_on_the_continuum():
    import inspect

    doc = inspect.getdoc(frame.propose_law_fields)
    assert "EXACTLY ON THE FINITE DYADIC GRID" in doc
    assert "not on the continuum" in doc


# ======================================================================================
# HR-8  the Delta axes
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
        assert frame.DELTA_DEFINITION[key]


def test_hr8_02_the_denominator_is_frozen_and_never_reduced():
    text = str(frame.DELTA_DEFINITION["denominator"])
    assert "exactly 67" in text
    assert "No replacement, no re-draw, no supplement, no exclusion" in text


def test_hr8_03_invalid_cases_map_to_unknown_not_to_zero():
    text = str(frame.DELTA_DEFINITION["invalid_cases"])
    assert "TECHNICALLY_UNKNOWN" in text
    assert "never 0" in text
    assert "TECHNICAL_FAIL" in text


# ======================================================================================
# HR-9  the enforceable ceiling
# ======================================================================================


@pytest.mark.parametrize(
    "claim",
    [
        "The component owns its internal information.",
        "Each entity governs its own repair after damage.",
        "This generalises to every law distribution.",
        "Evidence of complex life in the lattice.",
        "We found no dependence on initial conditions.",
        "The blob is self-maintaining and self-producing.",
        "The entity shows autonomy.",
        "This establishes individuality.",
        "Active reconstruction after damage follows.",
        "Reproduction and heredity are implied.",
        "The result is robust.",
        "The lattice blobs are alive.",
    ],
)
def test_hr9_01_every_recorded_bypass_now_fails_the_screen(claim):
    within, hits = frame.lexical_ceiling_screen(claim)
    assert within is False, claim
    assert hits


def test_hr9_02_the_screen_is_documented_as_a_limited_aid_not_a_guarantee():
    import inspect

    doc = inspect.getdoc(frame.lexical_ceiling_screen)
    assert "LIMITED SOFTWARE AID" in doc
    assert "not, and cannot be, a semantic guarantee" in doc
    assert "RouteEClaim" in doc
    assert "RE-L9" in frame.__doc__


def test_hr9_03_the_enforceable_ceiling_is_a_closed_vocabulary_object():
    claim = frame.RouteEClaim(
        estimand=frame.Estimand.DELTA_F_001,
        scope=frame.ClaimScope.DRAW_LEVEL_FROZEN_FRAME,
        verdict=frame.ClaimVerdict.POSITIVE,
        k=45,
        n=67,
        ci_low=0.5501,
        ci_high=0.7899,
    )
    rendered = frame.render_claim(claim)
    assert "persistence AND verified material replacement" in rendered
    assert "k = 45 of n = 67" in rendered
    for banned in ("ownership", "autonomy", "individuality", "heredity", "alive"):
        assert banned not in rendered.lower()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"estimand": "Delta"},
        {"scope": "anything"},
        {"verdict": "GOOD"},
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
        k=45,
        n=67,
        ci_low=0.5,
        ci_high=0.7,
    )
    base.update(kwargs)
    with pytest.raises(frame.ClaimRefused):
        frame.RouteEClaim(**base)


def test_hr9_05_free_text_can_never_be_rendered_as_a_claim():
    with pytest.raises(frame.ClaimRefused):
        frame.render_claim("Route E proves the entity is an individual.")


def test_hr9_06_every_verdict_has_exactly_one_authorised_template():
    assert set(frame.CLAIM_TEMPLATES) == {v.value for v in frame.ClaimVerdict}


# ======================================================================================
# HR-10  the classifier is integrated into the Route E path
# ======================================================================================


def test_hr10_01_the_production_path_always_calls_the_classifier():
    calls: list[int] = []

    def spy(tracking):
        calls.append(1)
        return frame.classify_track_terminations(tracking)

    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking,
        persisted_to_horizon=True,
        replacement_verified=True,
        eligible=True,
        classifier=spy,
    )
    assert calls == [1]
    assert outcome.disposition is frame.DrawDisposition.SUCCESS
    assert outcome.score == 1


def test_hr10_02_the_default_path_uses_the_real_classifier():
    import inspect

    source = inspect.getsource(frame.assemble_draw_outcome)
    assert "classify_track_terminations" in source
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=False, eligible=True
    )
    assert outcome.association_gate_breaks >= 1
    assert outcome.disposition is (
        frame.DrawDisposition.OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT
    )
    assert outcome.score == 0


# frame 0: blob A (top left) and blob B (middle).  frame 1: A vanishes -> DISSOLUTION,
# B is re-detected as two disjoint pieces the association graph cannot resolve ->
# TRACKING_UNRESOLVED.  Two different observed failure states at once, so the draw's
# disposition is genuinely ambiguous and must fail closed rather than be guessed.
_AMBIGUOUS_F0 = [(0, 0), (0, 1), (1, 0), (1, 1), (8, 8), (8, 9), (9, 8), (9, 9)]
_AMBIGUOUS_F1 = [(6, 8), (6, 9), (6, 10), (11, 8), (11, 9), (11, 10)]


def test_hr10_03_an_ambiguous_termination_is_fail_closed():
    tracking = _track([_AMBIGUOUS_F0, _AMBIGUOUS_F1])
    states = {
        item.terminal_state for item in frame.classify_track_terminations(tracking)
    }
    assert states == {"DISSOLVED_DETECTED_TRACK", "UNRESOLVED_HANDOFF"}, states
    with pytest.raises(frame.AmbiguousTermination) as excinfo:
        frame.assemble_draw_outcome(
            tracking, persisted_to_horizon=False, replacement_verified=False, eligible=True
        )
    assert "do not resolve to exactly one observed failure" in str(excinfo.value)


def test_hr10_04_a_genuine_dissolution_resolves_to_one_observed_failure():
    tracking = _track([_BLOB_LEFT, []])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=False, replacement_verified=False, eligible=True
    )
    assert outcome.disposition is frame.DrawDisposition.OBSERVED_FAILURE_DISSOLVED
    assert outcome.score == 0


def test_hr10_05_broken_evidence_is_unknown_not_zero():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking,
        persisted_to_horizon=True,
        replacement_verified=True,
        eligible=True,
        evidence_ok=False,
    )
    assert outcome.disposition is frame.DrawDisposition.TECHNICALLY_UNKNOWN
    assert outcome.score is None


def test_hr10_06_an_ineligible_draw_is_a_true_zero_in_the_denominator():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    outcome = frame.assemble_draw_outcome(
        tracking, persisted_to_horizon=True, replacement_verified=True, eligible=False
    )
    assert outcome.disposition is frame.DrawDisposition.MECHANICALLY_INELIGIBLE
    assert outcome.score == 0
    assert frame.DISPOSITION_TABLE["MECHANICALLY_INELIGIBLE"]["in_denominator"] is True


def test_hr10_07_assembly_is_fail_closed_on_its_inputs():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    with pytest.raises(TypeError):
        frame.assemble_draw_outcome(
            "not tracking", persisted_to_horizon=True, replacement_verified=True, eligible=True
        )
    with pytest.raises(TypeError):
        frame.assemble_draw_outcome(
            tracking, persisted_to_horizon=1, replacement_verified=True, eligible=True
        )


def test_hr10_08_assembly_is_idempotent():
    tracking = _track([_BLOB_LEFT, _BLOB_FAR])
    kwargs = dict(persisted_to_horizon=True, replacement_verified=False, eligible=True)
    assert frame.assemble_draw_outcome(tracking, **kwargs) == frame.assemble_draw_outcome(
        tracking, **kwargs
    )


# ======================================================================================
# Firewall: nothing scientific was materialised
# ======================================================================================


def test_firewall_01_scientific_run_is_not_authorised():
    assert frame.SCIENTIFIC_RUN_AUTHORIZED is False


def test_firewall_02_no_module_level_scientific_entity_exists():
    for module in (frame, locks):
        for banned in ("SEED", "SCIENTIFIC_SEED", "SEED_ROOT", "BEACON_ROUND", "FAMILY",
                       "NAMESPACE", "LAW_SPEC", "WORLD"):
            assert not hasattr(module, banned), (module.__name__, banned)


def test_firewall_03_no_designated_round_is_selected_at_import_time():
    import inspect

    for module in (frame, locks):
        source = inspect.getsource(module)
        assert "designated_round(" not in source.split("def designated_round")[0]


def test_firewall_04_the_locks_module_creates_no_scientific_artefact(tmp_path, monkeypatch):
    before = sorted(os.listdir(tmp_path))
    with ForbiddenEffects(monkeypatch):
        with pytest.raises(locks.EntryPointRefused):
            locks.route_e_entry(
                locks.SUPPORTED_ENTRY_POINTS[0],
                authorisation=_authorisation(),
                receipt=_receipt(DIGEST_A),
                verifier=_accepting_verifier,
            )
    assert sorted(os.listdir(tmp_path)) == before == []
