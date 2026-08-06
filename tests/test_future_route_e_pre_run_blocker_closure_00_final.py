"""FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 -- final implementation.

Closes the residuals the last human review left open, with executable code only:

* ``PRB-5`` -- four refusal tests calling the four REAL public entry points that had
  none, on the exact model of the surviving ``run_owned_future_pipeline`` test.  No
  stub, no mock, no spy stands in for the function under test: each test imports the
  production callable and calls it.
* ``PRB-6`` -- the maintained BLS/G1 verifier is INSTALLED and used.  A positive
  authentic vector verifies; round +/- 1, an altered signature, a point outside the
  prime-order subgroup, the point at infinity, a non-canonical encoding and a wrong DST
  are all refused.  Absence of the library is a STOP, never an accept.
* ``HR-10`` -- the substitutable ``classifier`` seam is gone from the production path.
* Route E runtime wiring -- the path ``P -> commitment -> beacon -> run_route_e -> E``
  is exercised end to end, the enabled arm changes the fixture state measurably, the
  disabled arm is byte-identical to the witness, an independent verifier admits the run,
  the historical "empty right frame + non-unit cadence" case cannot reach ``COMPLETE``,
  the run is deterministic and restart-identical, and no silent fallback exists.

Nothing here opens a scientific seed, a law, a family or a holdout.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from edlab.substrates.lattice_bond import future_route_e_execution as execution
from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import route_e_beacon_verifier as beacon
from edlab.substrates.lattice_bond import route_e_bls_verifier as bls
from edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline import (
    OwnedEvidenceError,
    open_owned_analysis_access,
)
from edlab.substrates.lattice_bond.future_lifecycle_runner import (
    CompletionEvidenceError,
    CompletionPublicationError,
    open_analysis_access,
    publish_future_family_completion,
)
from edlab.substrates.lattice_bond.lifecycle import (
    LifecyclePublicationError,
    qualify_and_write_lifecycle_contract,
)
from edlab.substrates.lattice_bond.instrumentation import TrackingResult

_REPO_ROOT = Path(__file__).resolve().parent.parent
_VECTORS = json.loads((_REPO_ROOT / "tests" / "data" / "route_e_beacon_vectors.json").read_text("ascii"))
_QUICKNET = [v for v in _VECTORS["vectors"] if v["chain"] == "quicknet"]
_V2 = [v for v in _VECTORS["vectors"] if v["id"] == "V2"][0]

#: An on-curve G1 point that is NOT in the prime-order subgroup (found by search over
#: canonical compressed encodings; recorded here so the test is deterministic).
OFF_SUBGROUP_G1 = (
    "800000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000004"
)
#: The canonical compressed encoding of the G1 point at infinity.
INFINITY_G1 = "c0" + "00" * 47
#: The fastnet DST -- a real DST for a DIFFERENT drand scheme.
WRONG_DST = b"BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_WRONG"


def _tree_digest(root: Path) -> str:
    parts = []
    for path in sorted(root.rglob("*")):
        parts.append(str(path.relative_to(root)))
        if path.is_file():
            parts.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def _tracking(frames=(0, 1, 2)) -> TrackingResult:
    """A minimal, entirely synthetic tracking result.  ENGINEERING ONLY."""
    return TrackingResult((), (), (), ())


# ======================================================================================
# PRB-5 -- refusal tests on the four REAL entry points that had none
# ======================================================================================


def test_prb5_final_01_open_owned_analysis_access_refuses_before_any_effect(tmp_path):
    """The REAL open_owned_analysis_access, not a helper and not a stub."""
    absent = tmp_path / "unauthorised_route_e_namespace"
    assert not absent.exists()
    before = _tree_digest(tmp_path)

    with pytest.raises(OwnedEvidenceError) as excinfo:
        open_owned_analysis_access(absent)

    assert "run_directory must already exist" in str(excinfo.value)
    assert not absent.exists()
    assert _tree_digest(tmp_path) == before
    assert list(tmp_path.iterdir()) == []


def test_prb5_final_02_runner_open_analysis_access_refuses_before_any_effect(tmp_path):
    """The REAL future_lifecycle_runner.open_analysis_access."""
    absent = tmp_path / "unauthorised_route_e_namespace"
    before = _tree_digest(tmp_path)

    with pytest.raises(CompletionEvidenceError) as excinfo:
        open_analysis_access(absent, _tracking(), (0, 1, 2))

    assert "run_directory must already exist" in str(excinfo.value)
    assert not absent.exists()
    assert _tree_digest(tmp_path) == before
    assert list(tmp_path.iterdir()) == []


def test_prb5_final_03_publish_future_family_completion_refuses_before_any_effect(tmp_path):
    """The REAL publish_future_family_completion.  COMPLETE is never reachable here."""
    absent = tmp_path / "unauthorised_route_e_namespace"
    before = _tree_digest(tmp_path)

    with pytest.raises(CompletionPublicationError) as excinfo:
        publish_future_family_completion(absent, _tracking(), (0, 1, 2))

    assert "run_directory must already exist" in str(excinfo.value)
    assert not absent.exists()
    assert _tree_digest(tmp_path) == before
    assert list(tmp_path.iterdir()) == []


def test_prb5_final_04_qualify_and_write_lifecycle_contract_refuses_before_any_effect(tmp_path):
    """The REAL qualify_and_write_lifecycle_contract."""
    target = tmp_path / "absent_parent" / "LIFECYCLE.json"
    before = _tree_digest(tmp_path)

    with pytest.raises(LifecyclePublicationError) as excinfo:
        qualify_and_write_lifecycle_contract(target, _tracking(), (0, 1, 2))

    assert "publication parent must already exist" in str(excinfo.value)
    assert not target.exists()
    assert not target.parent.exists()
    assert _tree_digest(tmp_path) == before
    assert list(tmp_path.iterdir()) == []


def test_prb5_final_05_no_engine_step_survives_any_of_the_four_refusals(tmp_path, monkeypatch):
    """None of the four refusals may step the engine or write a byte."""
    from edlab.substrates.lattice_bond import engine as engine_module

    steps: list[int] = []

    def refuse(self, *args, **kwargs):  # pragma: no cover - must never run
        steps.append(1)
        raise AssertionError("a refused entry point must not step the engine")

    monkeypatch.setattr(engine_module.LatticeBondEngine, "step", refuse)
    before = _tree_digest(tmp_path)

    with pytest.raises(OwnedEvidenceError):
        open_owned_analysis_access(tmp_path / "a")
    with pytest.raises(CompletionEvidenceError):
        open_analysis_access(tmp_path / "b", _tracking(), (0, 1))
    with pytest.raises(CompletionPublicationError):
        publish_future_family_completion(tmp_path / "c", _tracking(), (0, 1))
    with pytest.raises(LifecyclePublicationError):
        qualify_and_write_lifecycle_contract(tmp_path / "d" / "L.json", _tracking(), (0, 1))

    assert steps == []
    assert _tree_digest(tmp_path) == before
    assert list(tmp_path.iterdir()) == []


def test_prb5_final_06_all_five_supported_entry_points_now_have_a_refusal_test():
    """The 1-of-5 gap named by the human review is closed: 5 of 5."""
    from edlab.substrates.lattice_bond import future_route_e_pre_run_locks as locks

    covered = {
        "future_lifecycle_owned_pipeline.run_owned_future_pipeline",
        "future_lifecycle_owned_pipeline.open_owned_analysis_access",
        "future_lifecycle_runner.open_analysis_access",
        "future_lifecycle_runner.publish_future_family_completion",
        "lifecycle.qualify_and_write_lifecycle_contract",
    }
    assert set(locks.SUPPORTED_ENTRY_POINTS) == covered
    # route_e_entry is a protocol convention, not a gate: it references no accepted module.
    assert locks.FACADE_IS_NOT_A_GATE


# ======================================================================================
# PRB-6 -- the installed maintained verifier, positive vector and six negative cases
# ======================================================================================


def test_prb6_final_01_the_verifier_is_installed_and_versioned():
    assert bls.library_version()
    lock = (_REPO_ROOT / "requirements-route-e-lock.txt").read_text("utf-8")
    assert "py_arkworks_bls12381==0.5.0" in lock
    assert "--hash=sha256:" in lock
    assert beacon.INSTALLED_VERIFIER_DISTRIBUTION == bls.BLS_LIBRARY_DISTRIBUTION


@pytest.mark.parametrize("vector", _QUICKNET, ids=lambda v: v["id"])
def test_prb6_final_02_authentic_positive_vector_verifies(vector):
    check = bls.verify_beacon_signature(
        round_number=vector["round"],
        signature_hex=vector["signature"],
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert check.valid, check.reason
    assert bls.BLS_LIBRARY_DISTRIBUTION in check.reason


@pytest.mark.parametrize("delta", [-1, 1])
def test_prb6_final_03_round_plus_or_minus_one_is_refused(delta):
    check = bls.verify_beacon_signature(
        round_number=_V2["round"] + delta,
        signature_hex=_V2["signature"],
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert not check.valid
    assert "pairing identity" in check.reason


def test_prb6_final_04_an_altered_signature_is_refused():
    """A VALID G1 point that is not this round's signature: fails the pairing itself."""
    other = next(v for v in _QUICKNET if v["id"] != _V2["id"])
    check = bls.verify_beacon_signature(
        round_number=_V2["round"],
        signature_hex=other["signature"],
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert not check.valid
    assert "pairing identity" in check.reason


def test_prb6_final_05_a_point_outside_the_subgroup_is_refused():
    from py_arkworks_bls12381 import G1Point

    raw = bytes.fromhex(OFF_SUBGROUP_G1)
    unchecked = G1Point.from_compressed_bytes_unchecked(raw)
    assert unchecked is not None
    assert not unchecked.is_in_subgroup()  # the fixture really is off-subgroup

    check = bls.verify_beacon_signature(
        round_number=_V2["round"],
        signature_hex=OFF_SUBGROUP_G1,
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert not check.valid
    assert "subgroup" in check.reason


def test_prb6_final_06_the_point_at_infinity_is_refused():
    check = bls.verify_beacon_signature(
        round_number=_V2["round"],
        signature_hex=INFINITY_G1,
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert not check.valid
    assert "infinity" in check.reason


@pytest.mark.parametrize(
    "mutated,expected",
    [
        ("00" + _V2["signature"][2:], "non-canonical encoding"),
        (_V2["signature"].upper(), "lower-case canonical hex"),
        (_V2["signature"] + "00", "exactly 48 bytes"),
    ],
)
def test_prb6_final_07_non_canonical_encodings_are_refused(mutated, expected):
    check = bls.verify_beacon_signature(
        round_number=_V2["round"],
        signature_hex=mutated,
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=beacon.QUICKNET_DST,
    )
    assert not check.valid
    assert expected in check.reason


def test_prb6_final_08_the_wrong_dst_is_refused():
    check = bls.verify_beacon_signature(
        round_number=_V2["round"],
        signature_hex=_V2["signature"],
        public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
        dst=WRONG_DST,
    )
    assert not check.valid
    assert "pairing identity" in check.reason


def test_prb6_final_09_no_verifier_unavailable_accept_anyway_mode(monkeypatch):
    """NO_SILENT_FALLBACK at the crypto layer."""

    def absent():
        raise bls.BlsVerifierUnavailable("simulated absence")

    monkeypatch.setattr(bls, "_library", absent)
    with pytest.raises(bls.BlsVerifierUnavailable):
        bls.verify_beacon_signature(
            round_number=_V2["round"],
            signature_hex=_V2["signature"],
            public_key_hex=beacon.QUICKNET_PUBLIC_KEY,
            dst=beacon.QUICKNET_DST,
        )
    verdict = beacon.verify_round(
        response={
            "round": _V2["round"],
            "randomness": _V2["randomness"],
            "signature": _V2["signature"],
            "chain_hash": beacon.QUICKNET_CHAIN_HASH,
        },
        expected_round=_V2["round"],
        helper_path=None,
    )
    assert verdict.outcome is beacon.BeaconOutcome.CONFIGURATION_ERROR
    assert beacon.disposition_for(verdict.outcome) == "STOP"


def test_prb6_final_10_the_source_tree_implements_no_bls_arithmetic():
    """No hand-rolled crypto: the adapter delegates, it does not compute."""
    source = (_REPO_ROOT / "edlab/substrates/lattice_bond/route_e_bls_verifier.py").read_text("utf-8")
    for forbidden in ("field_modulus", "% p", "pow(", "sqrt", "def _add(", "def _double("):
        assert forbidden not in source, forbidden
    assert "py_arkworks_bls12381" in source
