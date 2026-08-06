"""Pinned, offline adapter to the maintained drand beacon verifier (PRB-6).

WHAT THIS IS
------------
A bounded, no-shell bridge to ``tools/drand_verify``, a Go helper built on the
MAINTAINED drand libraries (``github.com/drand/kyber-bls12381`` and
``github.com/drand/kyber``).  No BLS arithmetic is implemented in this repository.

WHAT THIS IS NOT
----------------
It performs **no network access**.  It never retrieves a beacon, never selects a
round, and never contacts drand.  The beacon response is data supplied by the caller;
availability is the caller's problem and its absence is a WAIT, never a substitution.

WHAT THE CALLER MAY NOT CHOOSE
------------------------------
The scheme, the domain separation tag, the chain hash and the chain public key are
PINNED here as module constants.  They are never read from a receipt, never taken from
a beacon response and never accepted as arguments.  A response that names a different
chain is refused; a caller that wants a different chain has to change this file, which
is an auditable act.

OUTCOMES
--------
``BeaconOutcome`` is a closed set of five values and nothing else:

===================== ==========================================================
``VERIFIED``          the round signature verified against the pinned key and
                      ``randomness == sha256(signature)``
``INVALID``           chain, round, encoding, signature or randomness is wrong
``UNAVAILABLE``       the caller could not retrieve the designated round
``CONFIGURATION_ERROR`` the verifier is absent, unusable or misconfigured
``INTERNAL_ERROR``    the verifier crashed, timed out or answered ambiguously
===================== ==========================================================

The WAIT / STOP translation is fixed by :func:`disposition_for`:
``UNAVAILABLE`` is the ONLY WAIT, and it waits on the SAME round.  Everything else
is a STOP.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "QUICKNET_CHAIN_HASH",
    "QUICKNET_PUBLIC_KEY",
    "QUICKNET_SCHEME",
    "QUICKNET_DST",
    "QUICKNET_PERIOD_SECONDS",
    "QUICKNET_GENESIS_TIME_UNIX",
    "HELPER_ARGUMENTS",
    "HELPER_TIMEOUT_SECONDS",
    "MAX_HELPER_OUTPUT_BYTES",
    "BeaconOutcome",
    "BeaconVerdict",
    "disposition_for",
    "verify_round",
    "INSTALLED_VERIFIER_DISTRIBUTION",
]

#: PRB-6: the maintained verifier actually installed and used when no external helper
#: is supplied.  Pinned by version and wheel hash in requirements-route-e-lock.txt.
INSTALLED_VERIFIER_DISTRIBUTION = "py_arkworks_bls12381"

# --------------------------------------------------------------------------------------
# Pinned chain parameters.  NOT caller-supplied, NOT read from any receipt or response.
# Source: github.com/drand/drand common/chain/info_test.go and crypto/schemes.go, and
# github.com/drand/tlock tlock_test.go -- all committed fixtures, fetched over https,
# never from a beacon endpoint.
# --------------------------------------------------------------------------------------

QUICKNET_CHAIN_HASH = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
QUICKNET_PUBLIC_KEY = (
    "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c"
    "8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb"
    "5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a"
)
QUICKNET_SCHEME = "bls-unchained-g1-rfc9380"
QUICKNET_DST = "BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"
QUICKNET_PERIOD_SECONDS = 3
QUICKNET_GENESIS_TIME_UNIX = 1692803367

#: The helper is invoked with a FIXED argument list.  There is no shell, no format
#: string, no user-controlled argument and no environment inheritance.
HELPER_ARGUMENTS: tuple[str, ...] = ("verify",)
HELPER_TIMEOUT_SECONDS = 20
MAX_HELPER_OUTPUT_BYTES = 4096
MAX_HELPER_STDERR_BYTES = 4096

_REQUIRED_RESPONSE_KEYS = ("round", "randomness", "signature", "chain_hash")


class BeaconOutcome(Enum):
    """The closed set of outcomes.  Nothing else may ever be returned."""

    VERIFIED = "verified"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"
    CONFIGURATION_ERROR = "configuration_error"
    INTERNAL_ERROR = "internal_error"


@dataclass(frozen=True)
class BeaconVerdict:
    """An inert verdict.  Holding one grants nothing."""

    outcome: BeaconOutcome
    reason: str
    round: int | None = None
    randomness: str | None = None


def disposition_for(outcome: BeaconOutcome) -> str:
    """WAIT or STOP.  Genuine unavailability is the ONLY WAIT, on the SAME round."""
    if not isinstance(outcome, BeaconOutcome):
        raise TypeError("outcome must be a BeaconOutcome")
    return "WAIT" if outcome is BeaconOutcome.UNAVAILABLE else "STOP"


def _configuration(reason: str) -> BeaconVerdict:
    return BeaconVerdict(BeaconOutcome.CONFIGURATION_ERROR, reason)


def _invalid(reason: str, expected_round: int | None = None) -> BeaconVerdict:
    return BeaconVerdict(BeaconOutcome.INVALID, reason, round=expected_round)


def _internal(reason: str) -> BeaconVerdict:
    return BeaconVerdict(BeaconOutcome.INTERNAL_ERROR, reason)


def _validated_helper(helper_path: Any) -> tuple[Path | None, BeaconVerdict | None]:
    if helper_path is None:
        return None, _configuration(
            "no external helper supplied; the installed verifier is used instead"
        )
    if not isinstance(helper_path, (str, os.PathLike)):
        return None, _configuration("helper_path must be a filesystem path")
    resolved = Path(helper_path)
    if not resolved.is_file():
        return None, _configuration(f"the verifier is absent at {resolved}")
    if not os.access(resolved, os.X_OK):
        return None, _configuration(f"the verifier at {resolved} is not executable")
    return resolved, None


def _validated_response(response: Any, expected_round: int) -> tuple[dict | None, BeaconVerdict | None]:
    if not isinstance(response, Mapping):
        return None, _invalid("the beacon response is not a mapping", expected_round)
    missing = [key for key in _REQUIRED_RESPONSE_KEYS if key not in response]
    if missing:
        return None, _invalid(f"the beacon response is missing {missing}", expected_round)
    extra = [key for key in response if key not in _REQUIRED_RESPONSE_KEYS]
    if extra:
        return None, _invalid(f"the beacon response carries unknown keys {extra}", expected_round)

    chain_hash = response["chain_hash"]
    if not isinstance(chain_hash, str) or chain_hash != QUICKNET_CHAIN_HASH:
        return None, _invalid(
            "the beacon response is not from the pinned chain; the chain is pinned in "
            "the adapter and is never taken from the response",
            expected_round,
        )
    round_value = response["round"]
    if isinstance(round_value, bool) or not isinstance(round_value, int):
        return None, _invalid("the round number is not a plain int", expected_round)
    if round_value != expected_round:
        return None, _invalid(
            f"the response carries round {round_value}, not the designated round "
            f"{expected_round}; changing round is forbidden",
            expected_round,
        )
    for name in ("randomness", "signature"):
        if not isinstance(response[name], str):
            return None, _invalid(f"{name} must be a hex string", expected_round)
    return dict(response), None


def _verify_in_process(parsed: dict, expected_round: int) -> BeaconVerdict:
    """PRB-6: verify with the INSTALLED maintained library, in this process.

    There is no permissive branch.  An absent library is a CONFIGURATION_ERROR, and a
    randomness that is not ``sha256(signature)`` is INVALID even when the signature
    itself verifies.
    """
    from . import route_e_bls_verifier as bls

    try:
        check = bls.verify_beacon_signature(
            round_number=expected_round,
            signature_hex=parsed["signature"],
            public_key_hex=QUICKNET_PUBLIC_KEY,
            dst=QUICKNET_DST,
        )
    except bls.BlsVerifierUnavailable as exc:
        return _configuration(str(exc))
    except Exception as exc:  # noqa: BLE001 - never silently accept
        return _internal(f"the installed verifier raised {type(exc).__name__}: {exc}")

    if not check.valid:
        return _invalid(check.reason, expected_round)

    expected_randomness = hashlib.sha256(bytes.fromhex(parsed["signature"])).hexdigest()
    if parsed["randomness"] != expected_randomness:
        return _invalid(
            "randomness is not sha256(signature); an HTTP response is not evidence",
            expected_round,
        )
    return BeaconVerdict(
        BeaconOutcome.VERIFIED,
        check.reason,
        round=expected_round,
        randomness=parsed["randomness"],
    )


def verify_round(
    *,
    response: Mapping[str, Any] | None,
    expected_round: int,
    helper_path: str | os.PathLike[str] | None,
) -> BeaconVerdict:
    """Verify ONE designated round, offline, through the pinned helper.

    ``expected_round`` is computed by the caller from the frozen public timestamp; it is
    checked against the response and passed to the helper.  It is never negotiated.
    """
    if isinstance(expected_round, bool) or not isinstance(expected_round, int) or expected_round <= 0:
        return _configuration("expected_round must be a positive plain int")

    if response is None:
        return BeaconVerdict(
            BeaconOutcome.UNAVAILABLE,
            "the designated round is not retrievable; WAIT and retry the SAME round. "
            "Never the next round, never an alternative endpoint, never another source.",
            round=expected_round,
        )

    if helper_path is None:
        parsed, failure = _validated_response(response, expected_round)
        if failure is not None:
            return failure
        return _verify_in_process(parsed, expected_round)

    helper, failure = _validated_helper(helper_path)
    if failure is not None:
        return failure

    parsed, failure = _validated_response(response, expected_round)
    if failure is not None:
        return failure

    request = json.dumps(
        {
            "scheme": QUICKNET_SCHEME,
            "public_key": QUICKNET_PUBLIC_KEY,
            "round": expected_round,
            "signature": parsed["signature"],
            "randomness": parsed["randomness"],
        },
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")

    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, minimal env
            [str(helper), *HELPER_ARGUMENTS],
            input=request,
            capture_output=True,
            timeout=HELPER_TIMEOUT_SECONDS,
            shell=False,
            env={"PATH": "", "LC_ALL": "C"},
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _internal("the verifier exceeded its timeout")
    except OSError as exc:
        return _configuration(f"the verifier could not be executed: {exc}")

    if len(completed.stdout) > MAX_HELPER_OUTPUT_BYTES:
        return _internal("the verifier produced more output than the bounded limit")

    try:
        payload = json.loads(completed.stdout.decode("ascii"))
    except (UnicodeDecodeError, ValueError):
        return _internal(
            f"the verifier answer is not JSON (exit {completed.returncode}); "
            f"stderr={completed.stderr[:MAX_HELPER_STDERR_BYTES]!r}"
        )
    if not isinstance(payload, dict) or "status" not in payload:
        return _internal("the verifier answer has no status")

    status = payload["status"]
    reason = payload.get("reason", "")
    if not isinstance(reason, str):
        return _internal("the verifier reason is not a string")

    if status == BeaconOutcome.VERIFIED.value:
        if completed.returncode != 0:
            return _internal("the verifier reported success with a non-zero exit code")
        if payload.get("scheme") != QUICKNET_SCHEME or payload.get("dst") != QUICKNET_DST:
            return _internal("the verifier did not echo the pinned scheme and DST")
        return BeaconVerdict(
            BeaconOutcome.VERIFIED,
            reason,
            round=expected_round,
            randomness=parsed["randomness"],
        )
    if status == BeaconOutcome.INVALID.value:
        return _invalid(reason, expected_round)
    if status == BeaconOutcome.CONFIGURATION_ERROR.value:
        return _configuration(reason)
    if status == BeaconOutcome.INTERNAL_ERROR.value:
        return _internal(reason)
    return _internal(f"the verifier returned an unknown status {status!r}")
