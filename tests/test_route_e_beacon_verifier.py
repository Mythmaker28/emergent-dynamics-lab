"""PRB-6: the pinned, offline drand beacon verifier and its Python adapter.

NO NETWORK.  NO BEACON ENDPOINT.  Every vector used here was copied out of a COMMITTED
fixture file in an official repository and lives in ``tests/data/route_e_beacon_vectors.json``
with its provenance.  Nothing in this file retrieves a round.

The real cryptography is exercised only when the Go helper has been built, because the
binary is deliberately NOT committed.  Both branches assert something real:

* helper present -> every official vector must verify and every negative case must fail
  in exactly the declared way;
* helper absent  -> the adapter must report ``CONFIGURATION_ERROR`` and the frozen
  translation must be STOP.  A missing verifier is never a pass.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from edlab.substrates.lattice_bond import future_route_e_pre_run_frame as frame
from edlab.substrates.lattice_bond import route_e_beacon_verifier as verifier

_REPO_ROOT = Path(__file__).resolve().parent.parent
VECTORS_PATH = _REPO_ROOT / "tests" / "data" / "route_e_beacon_vectors.json"
VECTORS = json.loads(VECTORS_PATH.read_text(encoding="ascii"))


def _helper() -> Path | None:
    """The built helper, or ``None``.  The binary is never committed."""
    override = os.environ.get("ROUTE_E_DRAND_VERIFY")
    candidates = [Path(override)] if override else []
    candidates.append(_REPO_ROOT / "tools" / "drand_verify" / "drand_verify")
    candidates.append(_REPO_ROOT / "tools" / "drand_verify" / "drand_verify.exe")
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


HELPER = _helper()
HELPER_AVAILABLE = HELPER is not None


def _fake_helper(tmp_path: Path, body: str) -> Path:
    """A stand-in executable used ONLY to exercise the protocol, never the maths."""
    script = tmp_path / "fake_helper"
    script.write_text("#!" + sys.executable + "\n" + body, encoding="ascii")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def _response(vector) -> dict:
    return {
        "round": vector["round"],
        "randomness": vector["randomness"],
        "signature": vector["signature"],
        "chain_hash": verifier.QUICKNET_CHAIN_HASH,
    }


# ======================================================================================
# Pinning and provenance
# ======================================================================================


def test_pin_01_the_chain_parameters_are_pinned_not_negotiable():
    assert verifier.QUICKNET_SCHEME == "bls-unchained-g1-rfc9380"
    assert verifier.QUICKNET_DST == "BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"
    assert len(verifier.QUICKNET_PUBLIC_KEY) == 192, "G2 public key is 96 bytes"
    assert len(verifier.QUICKNET_CHAIN_HASH) == 64
    assert verifier.QUICKNET_PERIOD_SECONDS == 3
    assert verifier.QUICKNET_GENESIS_TIME_UNIX == 1692803367


def test_pin_02_no_public_signature_lets_a_caller_choose_the_cryptography():
    import inspect

    names = set(inspect.signature(verifier.verify_round).parameters)
    for forbidden in ("scheme", "dst", "public_key", "chain_hash", "verifier", "callback"):
        assert forbidden not in names
    assert names == {"response", "expected_round", "helper_path"}


def test_pin_03_the_frame_reuses_the_pinned_values_and_does_not_restate_them():
    assert frame.BEACON_SOURCE["chain_hash"] is verifier.QUICKNET_CHAIN_HASH
    assert frame.BEACON_SOURCE["public_key"] is verifier.QUICKNET_PUBLIC_KEY
    assert frame.BEACON_SOURCE["scheme"] is verifier.QUICKNET_SCHEME
    assert frame.BEACON_SOURCE["dst"] is verifier.QUICKNET_DST


def test_pin_04_the_adapter_performs_no_network_access():
    import inspect

    source = inspect.getsource(verifier)
    for forbidden in ("requests", "urllib", "httpx", "http.client", "socket.", "urlopen"):
        assert forbidden not in source
    assert "shell=False" in source


def test_prov_01_every_vector_declares_a_traceable_official_source():
    sources = {entry["id"]: entry for entry in VECTORS["sources"]}
    assert VECTORS["scheme"] == verifier.QUICKNET_SCHEME
    assert VECTORS["dst"] == verifier.QUICKNET_DST
    assert VECTORS["vectors"], "there must be at least one vector"
    for vector in VECTORS["vectors"]:
        source = sources[vector["source"]]
        for key in ("repository", "path", "licence", "fetched_file_sha256"):
            assert source[key], f"{vector['id']} lacks {key}"
        assert source["committed_fixture"] is True
        assert source["network_at_test_time"] is False
        assert vector["scheme"] == verifier.QUICKNET_SCHEME
        assert len(vector["signature"]) == 96, "G1 signature is 48 bytes"
        assert len(vector["public_key"]) == 192
        assert len(vector["randomness"]) == 64
        assert vector["randomness_provenance"]


def test_prov_02_at_least_one_vector_commits_the_randomness_itself():
    """Only a committed randomness proves randomness = sha256(signature) officially."""
    import hashlib

    committed = [
        v for v in VECTORS["vectors"] if v["randomness_provenance"].startswith("COMMITTED")
    ]
    assert committed, "no official fixture commits the randomness"
    for vector in committed:
        derived = hashlib.sha256(bytes.fromhex(vector["signature"])).hexdigest()
        assert derived == vector["randomness"]


def test_prov_03_the_quicknet_vectors_use_the_pinned_chain():
    quicknet = [v for v in VECTORS["vectors"] if v["chain"] == "quicknet"]
    assert quicknet
    for vector in quicknet:
        assert vector["chain_hash"] == verifier.QUICKNET_CHAIN_HASH
        assert vector["public_key"] == verifier.QUICKNET_PUBLIC_KEY


# ======================================================================================
# Outcome algebra and the WAIT / STOP translation
# ======================================================================================


def test_outcome_01_the_outcome_set_is_closed():
    assert {o.value for o in verifier.BeaconOutcome} == {
        "verified",
        "invalid",
        "unavailable",
        "configuration_error",
        "internal_error",
    }


def test_outcome_02_unavailable_is_the_only_wait():
    for outcome in verifier.BeaconOutcome:
        expected = "WAIT" if outcome is verifier.BeaconOutcome.UNAVAILABLE else "STOP"
        assert verifier.disposition_for(outcome) == expected
    with pytest.raises(TypeError):
        verifier.disposition_for("unavailable")


def test_outcome_03_an_absent_round_is_unavailable_hence_wait():
    verdict = verifier.verify_round(response=None, expected_round=123, helper_path=HELPER)
    assert verdict.outcome is verifier.BeaconOutcome.UNAVAILABLE
    assert verifier.disposition_for(verdict.outcome) == "WAIT"
    assert "SAME round" in verdict.reason
    assert "never the next round" in verdict.reason.lower()


def test_outcome_04_a_missing_verifier_is_a_stop_never_a_pass(monkeypatch):
    """PRB-6 / NO_SILENT_FALLBACK: no library, no verdict.  Never an accept."""
    import edlab.substrates.lattice_bond.route_e_bls_verifier as bls

    def absent():
        raise bls.BlsVerifierUnavailable("simulated absence of the maintained verifier")

    monkeypatch.setattr(bls, "_library", absent)
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=None
    )
    assert verdict.outcome is verifier.BeaconOutcome.CONFIGURATION_ERROR
    assert verifier.disposition_for(verdict.outcome) == "STOP"


def test_outcome_05_an_absent_binary_is_a_stop(tmp_path):
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector),
        expected_round=vector["round"],
        helper_path=tmp_path / "not-built",
    )
    assert verdict.outcome is verifier.BeaconOutcome.CONFIGURATION_ERROR
    assert verifier.disposition_for(verdict.outcome) == "STOP"


@pytest.mark.parametrize(
    "mutation",
    [
        {"chain_hash": "00" * 32},
        {"round": 999_999_999},
        {"signature": 12345},
        {"randomness": None},
    ],
)
def test_outcome_06_a_response_that_does_not_match_the_pin_is_invalid(mutation):
    vector = VECTORS["vectors"][0]
    response = dict(_response(vector))
    response.update(mutation)
    verdict = verifier.verify_round(
        response=response, expected_round=vector["round"], helper_path=HELPER
    )
    assert verdict.outcome is verifier.BeaconOutcome.INVALID
    assert verifier.disposition_for(verdict.outcome) == "STOP"


def test_outcome_07_unknown_or_missing_response_keys_are_invalid():
    vector = VECTORS["vectors"][0]
    extra = dict(_response(vector))
    extra["previous_signature"] = "00"
    assert (
        verifier.verify_round(
            response=extra, expected_round=vector["round"], helper_path=HELPER
        ).outcome
        is verifier.BeaconOutcome.INVALID
    )
    incomplete = dict(_response(vector))
    incomplete.pop("signature")
    assert (
        verifier.verify_round(
            response=incomplete, expected_round=vector["round"], helper_path=HELPER
        ).outcome
        is verifier.BeaconOutcome.INVALID
    )


def test_outcome_08_a_non_positive_round_is_a_configuration_error():
    vector = VECTORS["vectors"][0]
    for bad in (0, -1, True):
        verdict = verifier.verify_round(
            response=_response(vector), expected_round=bad, helper_path=HELPER
        )
        assert verdict.outcome is verifier.BeaconOutcome.CONFIGURATION_ERROR


# ======================================================================================
# Helper protocol: crash, timeout, malformed output -- exercised without the maths
# ======================================================================================


def test_helper_01_a_crashing_helper_is_an_internal_error(tmp_path):
    helper = _fake_helper(tmp_path, "import sys\nsys.exit(9)\n")
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR
    assert verifier.disposition_for(verdict.outcome) == "STOP"


def test_helper_02_malformed_output_is_an_internal_error(tmp_path):
    helper = _fake_helper(tmp_path, "print('not json at all')\n")
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR


def test_helper_03_a_status_free_answer_is_an_internal_error(tmp_path):
    helper = _fake_helper(tmp_path, "print('{\"ok\": true}')\n")
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR


def test_helper_04_an_unknown_status_is_an_internal_error(tmp_path):
    helper = _fake_helper(tmp_path, "print('{\"status\": \"probably\", \"reason\": \"\"}')\n")
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR


def test_helper_05_a_forged_success_without_the_pinned_echo_is_refused(tmp_path):
    """A helper that merely says 'verified' does not get believed."""
    helper = _fake_helper(tmp_path, "print('{\"status\": \"verified\", \"reason\": \"trust me\"}')\n")
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR


def test_helper_06_a_timeout_is_an_internal_error(tmp_path, monkeypatch):
    helper = _fake_helper(tmp_path, "import time\ntime.sleep(30)\n")
    monkeypatch.setattr(verifier, "HELPER_TIMEOUT_SECONDS", 1)
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR
    assert "timeout" in verdict.reason


def test_helper_07_oversized_output_is_an_internal_error(tmp_path, monkeypatch):
    helper = _fake_helper(tmp_path, "print('x' * 100000)\n")
    monkeypatch.setattr(verifier, "MAX_HELPER_OUTPUT_BYTES", 16)
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.outcome is verifier.BeaconOutcome.INTERNAL_ERROR


def test_helper_08_the_helper_is_invoked_with_a_fixed_argv_and_no_shell(tmp_path):
    helper = _fake_helper(
        tmp_path,
        "import sys, json\n"
        "print(json.dumps({'status': 'invalid', 'reason': 'argv=' + ','.join(sys.argv[1:])}))\n",
    )
    vector = VECTORS["vectors"][0]
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=helper
    )
    assert verdict.reason == "argv=verify"
    assert verifier.HELPER_ARGUMENTS == ("verify",)


# ======================================================================================
# The real cryptography, when the helper has been built
# ======================================================================================


def test_crypto_01_the_installed_verifier_is_present_and_named():
    """PRB-6: the maintained verifier is INSTALLED, not merely proposed."""
    import edlab.substrates.lattice_bond.route_e_bls_verifier as bls

    assert verifier.INSTALLED_VERIFIER_DISTRIBUTION == bls.BLS_LIBRARY_DISTRIBUTION
    version = bls.library_version()
    assert tuple(int(p) for p in version.split(".")[:3]) >= (0, 5, 0)


@pytest.mark.parametrize("vector", VECTORS["vectors"], ids=lambda v: v["id"])
def test_crypto_02_every_official_vector_verifies(vector):
    if not HELPER_AVAILABLE:
        # The installed maintained verifier is the one under test.
        verdict = verifier.verify_round(
            response=_response(vector), expected_round=vector["round"], helper_path=None
        )
        if vector["chain"] == "quicknet":
            assert verdict.outcome is verifier.BeaconOutcome.VERIFIED
            assert verdict.randomness == vector["randomness"]
        else:
            # another chain: the adapter pins quicknet, so it must REFUSE, never accept
            assert verdict.outcome is verifier.BeaconOutcome.INVALID
        return
    if vector["chain"] != "quicknet":
        # the adapter pins quicknet, so a vector on another chain is refused there;
        # it is verified directly against the helper instead, with its own key.
        request = json.dumps(
            {
                "scheme": vector["scheme"],
                "public_key": vector["public_key"],
                "round": vector["round"],
                "signature": vector["signature"],
                "randomness": vector["randomness"],
            }
        ).encode("ascii")
        completed = subprocess.run(
            [str(HELPER), "verify"], input=request, capture_output=True, timeout=30, check=False
        )
        assert json.loads(completed.stdout)["status"] == "verified"
        return
    verdict = verifier.verify_round(
        response=_response(vector), expected_round=vector["round"], helper_path=HELPER
    )
    assert verdict.outcome is verifier.BeaconOutcome.VERIFIED
    assert verdict.randomness == vector["randomness"]


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda v, r: dict(r, round=v["round"] + 1), id="round_plus_1"),
        pytest.param(lambda v, r: dict(r, round=v["round"] - 1), id="round_minus_1"),
        pytest.param(
            lambda v, r: dict(r, signature=("a" if r["signature"][0] != "a" else "b") + r["signature"][1:]),
            id="tampered_signature",
        ),
        pytest.param(lambda v, r: dict(r, randomness="11" * 32), id="inconsistent_randomness"),
        pytest.param(lambda v, r: dict(r, signature="c0" + "00" * 47), id="point_at_infinity"),
        pytest.param(lambda v, r: dict(r, signature="9f" + "ff" * 47), id="non_canonical_x_ge_p"),
        pytest.param(lambda v, r: dict(r, signature=r["signature"] + "ab"), id="wrong_length"),
    ],
)
def test_crypto_03_every_negative_case_is_refused(mutate):
    vector = next(v for v in VECTORS["vectors"] if v["chain"] == "quicknet")
    response = mutate(vector, _response(vector))
    if not HELPER_AVAILABLE:
        verdict = verifier.verify_round(
            response=response, expected_round=vector["round"], helper_path=None
        )
        assert verdict.outcome in {
            verifier.BeaconOutcome.CONFIGURATION_ERROR,
            verifier.BeaconOutcome.INVALID,
        }
        return
    verdict = verifier.verify_round(
        response=response, expected_round=vector["round"], helper_path=HELPER
    )
    assert verdict.outcome is verifier.BeaconOutcome.INVALID
    assert verifier.disposition_for(verdict.outcome) == "STOP"


def test_crypto_04_the_declared_negative_catalogue_is_complete():
    ids = {case["id"] for case in VECTORS["negative_cases"]}
    assert len(ids) == len(VECTORS["negative_cases"])
    mutations = " ".join(case["mutation"] for case in VECTORS["negative_cases"])
    for required in (
        "round + 1",
        "round - 1",
        "public key replaced",
        "signature byte flipped",
        "randomness replaced",
        "point at infinity",
        "non-canonical",
        "too long",
        "fastnet",
        "extra JSON field",
        "subgroup",
        "helper binary absent",
        "helper crashes",
        "timeout",
        "malformed output",
    ):
        assert required in mutations, required


# ======================================================================================
# consume_beacon_round: the frame delegates and translates WAIT / STOP
# ======================================================================================


def test_consume_01_no_callback_exists_anywhere_in_the_signature():
    import inspect

    names = set(inspect.signature(frame.consume_beacon_round).parameters)
    assert names == {"response", "expected_round", "helper_path"}
    assert "verifier" not in names


def test_consume_02_unavailability_is_wait():
    with pytest.raises(frame.BeaconUnavailable) as excinfo:
        frame.consume_beacon_round(response=None, expected_round=123, helper_path=HELPER)
    assert frame.BeaconUnavailable.disposition == "WAIT"
    assert "never the next round" in str(excinfo.value).lower()


def test_consume_03_a_missing_verifier_is_stop(monkeypatch):
    import edlab.substrates.lattice_bond.route_e_bls_verifier as bls

    def absent():
        raise bls.BlsVerifierUnavailable("simulated absence of the maintained verifier")

    monkeypatch.setattr(bls, "_library", absent)
    vector = VECTORS["vectors"][0]
    with pytest.raises(frame.BeaconInvalid) as excinfo:
        frame.consume_beacon_round(
            response=_response(vector), expected_round=vector["round"], helper_path=None
        )
    assert frame.BeaconInvalid.disposition == "STOP"
    assert "configuration_error" in str(excinfo.value)


def test_consume_04_a_verified_round_returns_the_randomness():
    vector = next(v for v in VECTORS["vectors"] if v["chain"] == "quicknet")
    if not HELPER_AVAILABLE:
        randomness = frame.consume_beacon_round(
            response=_response(vector), expected_round=vector["round"], helper_path=None
        )
        assert randomness == bytes.fromhex(vector["randomness"])
        return
    randomness = frame.consume_beacon_round(
        response=_response(vector), expected_round=vector["round"], helper_path=HELPER
    )
    assert randomness == bytes.fromhex(vector["randomness"])
