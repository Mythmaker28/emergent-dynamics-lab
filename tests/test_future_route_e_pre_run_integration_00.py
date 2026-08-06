"""PRB-5 / PRB-2: the Route E guard, the five REAL entry points, and the blocker.

STATE OF THE WORLD, STATED FIRST
--------------------------------
``enforce_route_e_guard`` is implemented and exercised here directly, end to end,
including the real cryptographic verification of the designated round.  It is **NOT
installed** in the five accepted entry points.  Installing it means adding one call as
the first statement of each of those functions, which changes the bytes of three
accepted sources; those bytes are pinned test by test in
``tests/test_future_lifecycle_runner_integration.py`` and
``tests/test_future_lifecycle_owned_pipeline.py``, two files outside this mission's
allowlist.  Nine currently green tests would turn red.  The hook is therefore NOT
installed and the blocker is reported instead of being worked around.

So this file proves three separate things and conflates none of them:

1. the guard itself refuses, in the frozen order, with the real verifier (``guard_*``);
2. the five REAL accepted functions refuse today for their OWN reasons -- the weaker
   LK-L1 property, which is NOT a Route E refusal (``weak_*``);
3. the accepted sources contain no Route E concept at all, which is exactly why PRB-5
   stays OPEN (``blocker_*``).

NO NETWORK.  NO BEACON ENDPOINT.  NO ENGINE STEP.  NO SCIENTIFIC ENTITY.
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

from edlab.substrates.lattice_bond import future_lifecycle_owned_pipeline as owned
from edlab.substrates.lattice_bond import future_lifecycle_runner as runner
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks
from edlab.substrates.lattice_bond import lifecycle as lifecycle_module
from edlab.substrates.lattice_bond import route_e_beacon_verifier as beacon
from edlab.substrates.lattice_bond.engine import LatticeBondState
from edlab.substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
VECTORS = json.loads(
    (_REPO_ROOT / "tests" / "data" / "route_e_beacon_vectors.json").read_text(encoding="ascii")
)
_QUICKNET_VECTOR = next(v for v in VECTORS["vectors"] if v["chain"] == "quicknet")


def _helper() -> Path | None:
    override = os.environ.get("ROUTE_E_DRAND_VERIFY")
    for candidate in (
        *( [Path(override)] if override else [] ),
        _REPO_ROOT / "tools" / "drand_verify" / "drand_verify",
        _REPO_ROOT / "tools" / "drand_verify" / "drand_verify.exe",
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


HELPER = _helper()

_DETECTOR = DetectorSpec(matter_threshold=0.45, min_cells=3)
_TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=3.0, dilation_radius=1)
_BLOB = [(0, 0), (0, 1), (1, 0), (1, 1)]
DIGEST_A = hashlib.sha256(b"A").hexdigest()
DIGEST_B = hashlib.sha256(b"B").hexdigest()
DIGEST_C = hashlib.sha256(b"C").hexdigest()

#: A synthetic PUBLIC commitment timestamp whose designated round is EXACTLY the round
#: of the official vector.  It is DERIVED from the frozen chain arithmetic, never
#: chosen: t(r) = genesis + (r - 1) * period, and the rule adds 86400 seconds.
#: See ``test_round_01``.
_PUBLISHED_AT = (
    beacon.QUICKNET_GENESIS_TIME_UNIX
    + (_QUICKNET_VECTOR["round"] - 1) * beacon.QUICKNET_PERIOD_SECONDS
    - 86_400
)


def _state(cells, shape=(16, 16)):
    height, width = shape
    matter = np.zeros((height, width), dtype=np.float64)
    for y, x in cells:
        matter[y, x] = 1.0
    return LatticeBondState(
        m=matter,
        n=np.zeros((height, width), dtype=np.float64),
        b=np.zeros((2, height, width), dtype=np.float64),
        step=0,
    )


def _tracking_and_support():
    frames = [detect_components(_state(_BLOB), _DETECTOR, frame=i) for i in range(2)]
    tracking = track_components(frames, _TRACKER, sampled_frames=(0, 1))
    support: dict = {}
    for detected in frames:
        for component in detected:
            support.setdefault(component.frame, {})[component.index] = (
                component.shape,
                component.cells,
            )
    return tracking, support


class ArmedSpies:
    """Every forbidden effect raises, so a refusal that happens first is provable."""

    TARGETS = (
        "entropy(os.urandom)",
        "network(socket.socket)",
        "subprocess(any non-cryptographic subprocess)",
        "seed/family/namespace(frame.derive_seed_root)",
        "seed/family/namespace(frame.build_draw_plan)",
        "law-or-initial-condition(frame.propose_law_fields)",
        "engine(LatticeBondEngine.step)",
        "historical-read(Path.read_text)",
        "scientific-write(Path.write_text)",
        "scientific-write(Path.write_bytes)",
        "file(builtins.open)",
        "mkdir(Path.mkdir)",
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
        # A subprocess is forbidden UNLESS it is exactly the pinned cryptographic
        # verifier invoked with its fixed argv.  Anything else raises.
        real_popen = subprocess.Popen
        allowed = [str(HELPER), *beacon.HELPER_ARGUMENTS] if HELPER is not None else None

        def guarded_popen(args, *rest, **kwargs):
            if allowed is not None and list(args) == allowed:
                return real_popen(args, *rest, **kwargs)
            self.hits.append("subprocess(any non-cryptographic subprocess)")
            raise AssertionError(f"forbidden effect reached: subprocess {args!r}")

        self.monkeypatch.setattr(subprocess, "Popen", guarded_popen)
        self.monkeypatch.setattr(
            frame, "derive_seed_root", self._boom("seed/family/namespace(frame.derive_seed_root)")
        )
        self.monkeypatch.setattr(
            frame, "build_draw_plan", self._boom("seed/family/namespace(frame.build_draw_plan)")
        )
        self.monkeypatch.setattr(
            frame,
            "propose_law_fields",
            self._boom("law-or-initial-condition(frame.propose_law_fields)"),
        )
        self.monkeypatch.setattr(
            engine_module.LatticeBondEngine, "step", self._boom("engine(LatticeBondEngine.step)")
        )
        self.monkeypatch.setattr(Path, "read_text", self._boom("historical-read(Path.read_text)"))
        self.monkeypatch.setattr(
            Path, "write_text", self._boom("scientific-write(Path.write_text)")
        )
        self.monkeypatch.setattr(
            Path, "write_bytes", self._boom("scientific-write(Path.write_bytes)")
        )
        self.monkeypatch.setattr(builtins, "open", self._boom("file(builtins.open)"))
        self.monkeypatch.setattr(Path, "mkdir", self._boom("mkdir(Path.mkdir)"))
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def route_e_request(tmp_path):
    """A complete, well-formed Route E signal built from the official vector."""
    tracking, support = _tracking_and_support()
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()
    path, digest = locks.write_join_evidence(
        evidence_root, locks.build_track_component_join(tracking, support)
    )
    enrolment = locks.FamilyEnrolment(
        run_identity="RUN-SYNTHETIC-0001",
        seed_root_sha256=DIGEST_A,
        draw_plan_digest=DIGEST_B,
        n_draws=frame.N_LAW_DRAWS,
        worlds=frame.WORLD_COUNT,
    )
    root = locks.route_e_root(
        measurement_root_sha256=DIGEST_C,
        track_component_join_digest=digest,
        family_enrolment_digest=locks.enrolment_digest(enrolment),
    )
    commitment = locks.PublicCommitment(
        root_sha256=root,
        venue="TEST_ONLY append-only log",
        reference="TEST_ONLY/0001",
        published_at_unix=_PUBLISHED_AT,
    )
    response = {
        "round": _QUICKNET_VECTOR["round"],
        "randomness": _QUICKNET_VECTOR["randomness"],
        "signature": _QUICKNET_VECTOR["signature"],
        "chain_hash": beacon.QUICKNET_CHAIN_HASH,
    }
    return locks.RouteERequest(
        evidence_path=path,
        measurement_root_sha256=DIGEST_C,
        family_enrolment=enrolment,
        receipt=locks.RouteEReceipt(root_sha256=root, commitment=commitment),
        must_precede_unix=_PUBLISHED_AT + 1,
        beacon_response=response,
        verifier_path=HELPER,
    )


def _calls(tmp_path):
    """Every real public function, invoked on a directory that does not exist."""
    missing = tmp_path / "no-such-run-directory"
    tracking, _ = _tracking_and_support()
    return {
        "future_lifecycle_owned_pipeline.run_owned_future_pipeline": lambda: (
            owned.run_owned_future_pipeline(
                missing,
                acquisition_source=None,
                sampled_frames=(0, 1),
                detector_spec=_DETECTOR,
                tracker_spec=_TRACKER,
                acquisition_source_identity={},
            )
        ),
        "future_lifecycle_owned_pipeline.open_owned_analysis_access": lambda: (
            owned.open_owned_analysis_access(missing)
        ),
        "future_lifecycle_runner.open_analysis_access": lambda: (
            runner.open_analysis_access(missing, tracking, (0, 1))
        ),
        "future_lifecycle_runner.publish_future_family_completion": lambda: (
            runner.publish_future_family_completion(missing, tracking, (0, 1))
        ),
        "lifecycle.qualify_and_write_lifecycle_contract": lambda: (
            lifecycle_module.qualify_and_write_lifecycle_contract(
                missing / "contract.json", tracking, (0, 1)
            )
        ),
    }


ENTRY_POINTS = tuple(locks.ROUTE_E_GUARDED_ENTRY_POINTS)


def test_guard_00_the_five_literal_entry_points_are_the_frozen_ones():
    assert len(ENTRY_POINTS) == 5
    for name in (
        "run_owned_future_pipeline",
        "open_owned_analysis_access",
        "future_lifecycle_runner.open_analysis_access",
        "publish_future_family_completion",
        "qualify_and_write_lifecycle_contract",
    ):
        assert any(name in entry for entry in ENTRY_POINTS)


def _guard(signal, entry_point=None):
    locks.enforce_route_e_guard(signal, entry_point=entry_point or ENTRY_POINTS[0])


@pytest.mark.parametrize("entry_point", ENTRY_POINTS)
def test_guard_01_the_guard_refuses_for_every_named_entry_point(
    entry_point, route_e_request, monkeypatch
):
    with ArmedSpies(monkeypatch):
        with pytest.raises(
            (locks.RouteEGuardRefused, frame.BeaconInvalid, frame.BeaconUnavailable)
        ) as excinfo:
            _guard(route_e_request, entry_point)
    message = str(excinfo.value)
    assert "must already exist" not in message, "an ordinary validation is not a refusal"


def test_guard_02_a_complete_signal_reaches_the_frozen_stop_and_no_further(
    route_e_request, monkeypatch
):
    """Every phase passes -- evidence, root, binding, priority, real crypto -- and the
    guard still refuses, because ``scientific_run_authorized`` is False."""
    spies = ArmedSpies(monkeypatch)
    with spies:
        with pytest.raises(Exception) as excinfo:
            _guard(route_e_request)
    assert spies.hits == []
    # With the maintained verifier INSTALLED (PRB-6), the crypto phase really passes and
    # the guard still refuses on scientific_run_authorized.
    assert isinstance(excinfo.value, locks.RouteEGuardRefused)
    assert "scientific_run_authorized is False" in str(excinfo.value)


@pytest.mark.parametrize(
    "signal", ["ROUTE_E", 1, {"receipt": "yes"}, object()], ids=["str", "int", "dict", "object"]
)
def test_guard_03_an_untyped_signal_is_never_a_signal(signal, monkeypatch):
    with ArmedSpies(monkeypatch):
        with pytest.raises(locks.RouteEGuardRefused) as excinfo:
            _guard(signal)
    assert "not a RouteERequest" in str(excinfo.value)


def test_guard_04_an_unknown_entry_point_is_refused(route_e_request):
    with pytest.raises(locks.RouteEGuardRefused) as excinfo:
        locks.enforce_route_e_guard(route_e_request, entry_point="not.an.entry.point")
    assert "not one of the five guarded entry points" in str(excinfo.value)


def test_guard_05_an_absent_beacon_is_wait_on_the_same_round(route_e_request, monkeypatch):
    import dataclasses

    signal = dataclasses.replace(route_e_request, beacon_response=None)
    with ArmedSpies(monkeypatch):
        with pytest.raises(frame.BeaconUnavailable) as excinfo:
            _guard(signal)
    assert "SAME round" in str(excinfo.value)
    assert frame.BeaconUnavailable.disposition == "WAIT"


def test_guard_06_a_missing_verifier_is_stop(route_e_request, monkeypatch):
    import dataclasses

    import edlab.substrates.lattice_bond.route_e_bls_verifier as bls

    def absent():
        raise bls.BlsVerifierUnavailable("simulated absence of the maintained verifier")

    monkeypatch.setattr(bls, "_library", absent)
    signal = dataclasses.replace(route_e_request, verifier_path=None)
    with ArmedSpies(monkeypatch):
        with pytest.raises(frame.BeaconInvalid) as excinfo:
            _guard(signal)
    assert "configuration_error" in str(excinfo.value)
    assert frame.BeaconInvalid.disposition == "STOP"


def test_guard_07_a_broken_receipt_binding_is_refused_before_the_verifier(
    route_e_request, monkeypatch
):
    import dataclasses

    other = hashlib.sha256(b"a root nobody computed").hexdigest()
    forged = locks.RouteEReceipt(
        root_sha256=other,
        commitment=locks.PublicCommitment(
            root_sha256=other,
            venue="TEST_ONLY",
            reference="TEST_ONLY/0002",
            published_at_unix=_PUBLISHED_AT,
        ),
    )
    signal = dataclasses.replace(route_e_request, receipt=forged)
    with ArmedSpies(monkeypatch):
        with pytest.raises(locks.ReceiptInvalid) as excinfo:
            _guard(signal)
    assert "recomputed from the persisted evidence" in str(excinfo.value)


def test_guard_08_the_guard_can_never_return(route_e_request):
    with pytest.raises(Exception):
        _guard(route_e_request)


# ======================================================================================
# The five REAL entry points today: the WEAKER property, and the blocker
# ======================================================================================


@pytest.mark.parametrize("entry_point", ENTRY_POINTS)
def test_weak_01_every_real_entry_point_refuses_before_every_effect(
    entry_point, tmp_path, monkeypatch
):
    """LK-L1 only: the function's OWN first check refuses.  This is NOT a Route E
    refusal and it does NOT close PRB-5."""
    call = _calls(tmp_path)[entry_point]
    expected = {
        "future_lifecycle_owned_pipeline.run_owned_future_pipeline": owned.OwnedPublicationError,
        "future_lifecycle_owned_pipeline.open_owned_analysis_access": owned.OwnedEvidenceError,
        "future_lifecycle_runner.open_analysis_access": runner.CompletionEvidenceError,
        "future_lifecycle_runner.publish_future_family_completion": runner.CompletionPublicationError,
        "lifecycle.qualify_and_write_lifecycle_contract": lifecycle_module.LifecyclePublicationError,
    }[entry_point]
    spies = ArmedSpies(monkeypatch)
    with spies:
        with pytest.raises(expected) as excinfo:
            call()
    assert spies.hits == []
    assert type(excinfo.value) is expected
    assert "must already exist" in str(excinfo.value)
    assert not (tmp_path / "no-such-run-directory").exists()


def test_blocker_01_the_guard_is_installed_and_changes_nothing_else():
    """PRB-5, closed: the accepted sources now refuse a typed Route E signal at their
    FIRST statement, and know nothing else about Route E."""
    import inspect

    for module in (owned, runner, lifecycle_module):
        source = inspect.getsource(module)
        assert "_refuse_route_e_signal" in source, module.__name__
        # no receipt, no request construction, no Route E behaviour beyond the refusal
        assert "RouteEReceipt(" not in source, module.__name__
        assert "RouteERequest(" not in source, module.__name__


def test_blocker_02_no_accepted_public_signature_carries_a_route_e_parameter():
    import inspect

    for function in (
        owned.run_owned_future_pipeline,
        owned.open_owned_analysis_access,
        runner.open_analysis_access,
        runner.publish_future_family_completion,
        lifecycle_module.qualify_and_write_lifecycle_contract,
    ):
        assert "route_e" not in inspect.signature(function).parameters


def test_blocker_03_the_closure_is_declared_not_assumed():
    status = locks.blocker_status()["PRB-5"]
    assert status["status"] == "CANDIDATE_CLOSED"
    assert status["guard_implemented"] is True
    assert status["guard_installed"] is True
    assert set(status["blocked_by"]) == set()
    assert status["human_review_required"] is True


# ======================================================================================
# The designated round is derived, never supplied, never retried
# ======================================================================================


def test_round_01_the_round_is_derived_from_the_public_timestamp_alone():
    assert frame.designated_round(_PUBLISHED_AT) == _QUICKNET_VECTOR["round"]
    assert frame.designated_round(_PUBLISHED_AT) == frame.beacon_round_at_or_after(
        _PUBLISHED_AT + 86_400
    )
    assert frame.designated_round(_PUBLISHED_AT) == frame.designated_round(_PUBLISHED_AT)


def test_round_02_no_signature_lets_a_caller_choose_the_round():
    import inspect

    for name in ("evidence_path", "measurement_root_sha256", "family_enrolment", "receipt"):
        assert name in locks.RouteERequest.__dataclass_fields__
    for forbidden in ("round", "expected_round", "designated_round", "scheme", "dst", "chain_hash"):
        assert forbidden not in locks.RouteERequest.__dataclass_fields__
    names = set(inspect.signature(locks.verify_public_commitment).parameters)
    assert "round" not in names and "expected_round" not in names


@pytest.mark.parametrize("shift", [-1, 1])
def test_round_03_a_neighbouring_round_is_refused_even_if_well_formed(
    shift, route_e_request, monkeypatch
):
    import dataclasses

    response = dict(route_e_request.beacon_response)
    response["round"] = response["round"] + shift
    signal = dataclasses.replace(route_e_request, beacon_response=response)
    with ArmedSpies(monkeypatch):
        with pytest.raises(frame.BeaconInvalid) as excinfo:
            _guard(signal)
    assert "not the designated round" in str(excinfo.value)


def test_round_04_a_later_public_timestamp_designates_a_later_round():
    first = frame.designated_round(_PUBLISHED_AT)
    later = frame.designated_round(_PUBLISHED_AT + 3)
    assert later > first
    assert frame.designated_round(_PUBLISHED_AT + 86_400) > later


def test_round_05_there_is_no_retry_and_no_fallback_path():
    """No loop, no second attempt, no alternative source anywhere on the path."""
    import inspect

    import re

    for module in (locks, beacon):
        source = inspect.getsource(module)
        loops = [
            line
            for line in source.splitlines()
            if re.match(r"\s*(while|for)\s", line) and "beacon" in line.lower()
        ]
        assert loops == [], f"{module.__name__} loops on the beacon path: {loops}"
        assert "next_round" not in source
        prohibitions = ("never an alternative endpoint", "a beacon endpoint", "endpoint,")
        stripped = source
        for phrase in prohibitions:
            stripped = stripped.replace(phrase, "")
        assert "endpoint" not in stripped
    adapter = inspect.getsource(beacon.verify_round)
    assert adapter.count("subprocess.run") == 1, "exactly one attempt, never a retry"
    assert "except subprocess.TimeoutExpired" in adapter, "a timeout is terminal, not a retry"


# ======================================================================================
# Firewall
# ======================================================================================


def test_firewall_01_no_scientific_entity_is_created(route_e_request, monkeypatch):
    with ArmedSpies(monkeypatch):
        with pytest.raises(Exception):
            _guard(route_e_request)
    assert frame.SCIENTIFIC_RUN_AUTHORIZED is False


def test_firewall_02_the_integration_never_reads_a_historical_result():
    import inspect

    for module in (locks, beacon):
        source = inspect.getsource(module)
        for forbidden in ("results/", "M_MINUS", "stage_b", "shard"):
            assert forbidden not in source


def test_firewall_03_the_status_is_factual_and_carries_no_composite_token():
    status = locks.blocker_status()
    assert status["PRB-5"]["status"] == "CANDIDATE_CLOSED"
    assert status["PRB-2"]["authenticity_established"] is True
    assert status["PRB-2"]["integration_into_accepted_sources"] is False
    for entry in status.values():
        assert "closed" not in entry
        assert entry["human_review_required"] is True
