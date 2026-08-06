"""PRB-6 -- the installed, maintained BLS/G1 verifier used by Route E.

This module is the ONLY place where a drand beacon signature is actually verified.
It does not implement any cryptography.  Every primitive -- RFC 9380 hash-to-curve on
G1, compressed-point decoding with the prime-order subgroup check, and the BLS12-381
pairing -- is taken from the maintained Rust library ``py_arkworks_bls12381`` (arkworks
bindings), pinned by version and by wheel hash in ``requirements-route-e-lock.txt``.

Design rules, all load-bearing:

* ``RE-BLS-1`` -- **no hand-rolled cryptography.**  Field arithmetic, curve arithmetic,
  cofactor clearing, subgroup checks and the pairing all come from the library.  The
  only code here is the drand message rule, the encoding checks and the single
  verification equation.
* ``RE-BLS-2`` -- there is never a permissive path when the verifier is missing.  If the library is
  not importable the adapter returns ``CONFIGURATION_ERROR``.  There is no default
  verifier, no fallback, no callback and no environment switch that can turn an absent
  verifier into an accepted round.
* ``RE-BLS-3`` -- **the chain is pinned, never taken from the response.**  Public key,
  scheme, DST and chain hash are module constants imported from the beacon adapter.
* ``RE-BLS-4`` -- **the round is an input, never a negotiation.**  The message is
  ``SHA256(uint64 big-endian round)`` for the designated round only.  A response for
  round +/- 1 fails on the message, not on a string comparison.
* ``RE-BLS-5`` -- **canonical encodings only.**  Compressed G1 is 48 bytes with the
  compression bit set; compressed G2 is 96 bytes.  A point at infinity, a point off
  the prime-order subgroup, or a non-canonical encoding is rejected before pairing.

The verification equation for the drand ``bls-unchained-g1-rfc9380`` scheme
(signature on G1, public key on G2) is::

    e(signature, g2) == e(H(message), public_key)

which is checked here as a single product-of-pairings identity.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

__all__ = [
    "BLS_LIBRARY_DISTRIBUTION",
    "BLS_LIBRARY_MIN_VERSION",
    "COMPRESSED_G1_BYTES",
    "COMPRESSED_G2_BYTES",
    "BlsVerifierUnavailable",
    "BlsCheck",
    "library_version",
    "beacon_message",
    "verify_beacon_signature",
]

#: The maintained dependency.  Pinned in requirements-route-e-lock.txt with a hash.
BLS_LIBRARY_DISTRIBUTION = "py_arkworks_bls12381"
BLS_LIBRARY_MIN_VERSION = "0.5.0"

COMPRESSED_G1_BYTES = 48
COMPRESSED_G2_BYTES = 96

_COMPRESSION_FLAG = 0b1000_0000
_INFINITY_FLAG = 0b0100_0000


class BlsVerifierUnavailable(RuntimeError):
    """Raised when the maintained verifier is not importable.

    It is deliberately an error and never a permissive default: PRB-6 forbids every
    permissive mode in which a missing verifier would still let a round through.
    """


@dataclass(frozen=True)
class BlsCheck:
    """An inert result.  ``valid`` is only ever ``True`` after a real pairing check."""

    valid: bool
    reason: str


def _library() -> Any:
    try:
        import py_arkworks_bls12381 as library  # noqa: PLC0415 - deliberate late import
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise BlsVerifierUnavailable(
            "the maintained BLS verifier "
            f"{BLS_LIBRARY_DISTRIBUTION}>={BLS_LIBRARY_MIN_VERSION} is not installed; "
            "PRB-6 forbids accepting a round without it"
        ) from exc
    return library


def library_version() -> str:
    """The installed version of the maintained verifier, for the receipt."""
    from importlib import metadata  # noqa: PLC0415

    _library()
    return metadata.version(BLS_LIBRARY_DISTRIBUTION)


def beacon_message(round_number: int) -> bytes:
    """The drand unchained message rule: ``SHA256(uint64 big-endian round)``."""
    if isinstance(round_number, bool) or not isinstance(round_number, int):
        raise TypeError("round must be a plain int")
    if round_number <= 0 or round_number >= 2**64:
        raise ValueError("round must be a positive 64-bit integer")
    return hashlib.sha256(round_number.to_bytes(8, "big")).digest()


def _decode_hex(value: Any, expected_bytes: int, label: str) -> tuple[bytes | None, str | None]:
    if not isinstance(value, str):
        return None, f"{label} must be a hex string"
    if len(value) != expected_bytes * 2:
        return None, f"{label} must be exactly {expected_bytes} bytes ({expected_bytes * 2} hex chars)"
    if value != value.lower():
        return None, f"{label} must be lower-case canonical hex"
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        return None, f"{label} is not valid hex"
    return raw, None


def _encoding_failure(raw: bytes, label: str) -> str | None:
    """Reject non-canonical compressed encodings before touching the library."""
    flags = raw[0]
    if not flags & _COMPRESSION_FLAG:
        return f"{label} is not in compressed form (compression bit unset): non-canonical encoding"
    if flags & _INFINITY_FLAG:
        return f"{label} encodes the point at infinity, which is never an admissible {label}"
    return None


def verify_beacon_signature(
    *,
    round_number: int,
    signature_hex: Any,
    public_key_hex: str,
    dst: bytes | str,
) -> BlsCheck:
    """Verify one drand ``bls-unchained-g1-rfc9380`` signature.

    Returns :class:`BlsCheck`.  Raises :class:`BlsVerifierUnavailable` -- never a
    permissive result -- when the maintained library is absent.
    """
    library = _library()
    G1Point = library.G1Point
    G2Point = library.G2Point
    GT = library.GT

    if isinstance(dst, str):
        dst = dst.encode("ascii")
    if not isinstance(dst, (bytes, bytearray)) or not dst:
        return BlsCheck(False, "the domain separation tag must be non-empty bytes")

    try:
        message = beacon_message(round_number)
    except (TypeError, ValueError) as exc:
        return BlsCheck(False, f"round refused: {exc}")

    raw_signature, failure = _decode_hex(signature_hex, COMPRESSED_G1_BYTES, "signature")
    if failure is not None:
        return BlsCheck(False, failure)
    raw_public_key, failure = _decode_hex(public_key_hex, COMPRESSED_G2_BYTES, "public key")
    if failure is not None:
        return BlsCheck(False, failure)

    failure = _encoding_failure(raw_signature, "signature")
    if failure is not None:
        return BlsCheck(False, failure)
    failure = _encoding_failure(raw_public_key, "public key")
    if failure is not None:
        return BlsCheck(False, failure)

    # from_compressed_bytes performs the on-curve and prime-order subgroup checks.
    try:
        signature = G1Point.from_compressed_bytes(raw_signature)
    except Exception:  # noqa: BLE001 - the library raises library-specific errors
        return BlsCheck(
            False,
            "the signature is not a canonical point of the G1 prime-order subgroup",
        )
    if signature is None:
        return BlsCheck(False, "the signature did not decode to a G1 point")
    try:
        public_key = G2Point.from_compressed_bytes(raw_public_key)
    except Exception:  # noqa: BLE001
        return BlsCheck(
            False,
            "the public key is not a canonical point of the G2 prime-order subgroup",
        )
    if public_key is None:
        return BlsCheck(False, "the public key did not decode to a G2 point")

    if not signature.is_in_subgroup():
        return BlsCheck(False, "the signature lies outside the G1 prime-order subgroup")
    if signature == G1Point.identity():
        return BlsCheck(False, "the signature is the point at infinity")
    if not public_key.is_in_subgroup():
        return BlsCheck(False, "the public key lies outside the G2 prime-order subgroup")
    if public_key == G2Point.identity():
        return BlsCheck(False, "the public key is the point at infinity")

    hashed = G1Point.hash_to_curve(message, bytes(dst))
    generator = G2Point()

    if GT.pairing(signature, generator) != GT.pairing(hashed, public_key):
        return BlsCheck(
            False,
            "the pairing identity e(signature, g2) == e(H(message), public_key) does not hold",
        )
    return BlsCheck(
        True,
        f"verified by {BLS_LIBRARY_DISTRIBUTION} against the pinned public key and DST",
    )
