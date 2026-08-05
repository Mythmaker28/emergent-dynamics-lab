"""A1-R4 strict protocol primitives.  Trust boundary: INTERNAL_ARTIFACT_CONSISTENCY_ONLY.

WHAT THIS ADDS OVER A1-R3
-------------------------
A1-R3 validated document shapes but accepted, silently:

* a JSON boolean wherever an integer was expected (``True == 1`` in Python);
* duplicate JSON keys (``json.loads`` keeps the last silently);
* a ``min_cells`` that was not the frozen value -- and the producer and the verifier both
  hard-coded the SAME wrong value, so no differential check could ever catch it;
* a four-byte / ``2**-32`` initial-condition generator instead of the canonical frozen
  eight-byte / ``2**-64`` one.

WHAT IS *NOT* CLAIMED
---------------------
``trust_boundary = INTERNAL_ARTIFACT_CONSISTENCY_ONLY``.  Recomputation establishes that a
persisted artefact set is complete and internally coherent.  It does NOT establish that the
canonical engine produced the transitions.  A fully resealed, internally coherent but
transitionally impossible world is classified ``ARTIFACT_CONSISTENT_ENGINE_UNPROVEN`` and
never receives a scientific admission.
"""

from __future__ import annotations

import json
import math
import os
import posixpath
from typing import Any, Mapping, Sequence

__all__ = [
    "STRICT_VERSION",
    "TRUST_BOUNDARY",
    "ENGINE_UNPROVEN_CLASS",
    "FROZEN_MEASUREMENT_SPEC",
    "FROZEN_PRIMARY_SHAPE",
    "COHORT_RESIDUAL_CONVENTIONS",
    "IC_MATTER_DOMAIN",
    "IC_RESOURCE_DOMAIN",
    "IC_RESOLUTION_BITS",
    "IC_WORD_BYTES",
    "IC_MAPPING_VERSION",
    "IC_MAPPING_SUPERSEDED",
    "StrictRefusal",
    "strict_json_object",
    "require_plain_int",
    "require_exact_float",
    "require_finite",
    "contained_relative_path",
    "check_frozen_measurement_spec",
]

STRICT_VERSION = "route-e-strict/v1-a1r4"
TRUST_BOUNDARY = "INTERNAL_ARTIFACT_CONSISTENCY_ONLY"
ENGINE_UNPROVEN_CLASS = "ARTIFACT_CONSISTENT_ENGINE_UNPROVEN"

#: The frozen measurement specification.  These ARE the ``MeasurementSpec`` defaults; any
#: other value -- notably ``min_cells = 1``, which both A1-R2 and A1-R3 used -- is refused.
FROZEN_MEASUREMENT_SPEC: Mapping[str, Any] = {
    "matter_threshold": 0.45,
    "min_cells": 3,
    "max_centroid_displacement": 3.0,
    "max_area_ratio": 3.0,
    "dilation_radius": 1,
    "unique_score_margin": 1e-12,
}

FROZEN_PRIMARY_SHAPE: Mapping[str, int] = {
    "primary_laws": 67,
    "initial_conditions_per_law": 2,
    "primary_worlds": 134,
}

COHORT_RESIDUAL_CONVENTIONS: tuple[float, ...] = (0.01, 0.05, 0.20)

#: The canonical frozen generator is ``future_route_e_pre_run_frame.draw_uniform``.
#: OWNER DECISION ``SELECT_OPTION_1_TOP_53_BITS`` applied by
#: ROUTE_E_PILOT_READINESS_AND_FEASIBILITY_00: the mapping is now ``U53_TOP_BITS_V1``,
#: ``u = (int.from_bytes(draw_block(...)[0:8], "big") >> 11) * 2**-53``.
#: EIGHT bytes are still consumed per draw; the RESOLUTION is 53 bits, not 64, and the
#: range is strictly ``[0, 1)``.  ``IC_RESOLUTION_BITS = 64`` was a declared property
#: that binary64 made false (A1-R5 Phase 8), so it is corrected forward, not restated.
IC_MATTER_DOMAIN = b"IC-M"
IC_RESOURCE_DOMAIN = b"IC-N"
IC_RESOLUTION_BITS = 53
IC_WORD_BYTES = 8
IC_MAPPING_VERSION = "U53_TOP_BITS_V1"
IC_MAPPING_SUPERSEDED = "U64_DIVIDE_V0_SUPERSEDED"


class StrictRefusal(ValueError):
    """A refusal carrying a reason code.  Never a bare KeyError or TypeError."""

    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise StrictRefusal(
                f"duplicate JSON key {key!r}: json.loads would silently keep the last one",
                reason_code="DUPLICATE_JSON_KEY",
            )
        seen[key] = value
    return seen


def strict_json_object(payload: bytes, label: str, code: str) -> dict[str, Any]:
    """ASCII JSON object, duplicate keys refused, non-finite numbers refused."""
    if not isinstance(payload, (bytes, bytearray)):
        raise StrictRefusal(f"{label} is not bytes", reason_code=code)
    try:
        text = bytes(payload).decode("ascii")
    except UnicodeDecodeError as exc:
        raise StrictRefusal(f"{label} is not ASCII: {exc}", reason_code=code) from exc
    try:
        value = json.loads(
            text, object_pairs_hook=_reject_duplicate_keys, parse_constant=_refuse_constant
        )
    except StrictRefusal:
        raise
    except ValueError as exc:
        raise StrictRefusal(f"{label} is not valid JSON: {exc}", reason_code=code) from exc
    if not isinstance(value, dict):
        raise StrictRefusal(f"{label} is not a JSON object", reason_code=code)
    return value


def _refuse_constant(name: str) -> Any:
    raise StrictRefusal(
        f"non-finite JSON constant {name!r} is never accepted", reason_code="NON_FINITE_JSON"
    )


def require_plain_int(value: Any, name: str, *, code: str) -> int:
    """A Python ``bool`` is an ``int``.  It is never accepted where an integer is required."""
    if isinstance(value, bool):
        raise StrictRefusal(
            f"{name} is a JSON boolean; a boolean is never an integer here",
            reason_code=code,
        )
    if not isinstance(value, int):
        raise StrictRefusal(f"{name} is not an integer: {value!r}", reason_code=code)
    return int(value)


def require_exact_float(value: Any, expected: float, name: str, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StrictRefusal(f"{name} is not a number: {value!r}", reason_code=code)
    if not math.isfinite(float(value)):
        raise StrictRefusal(f"{name} is not finite", reason_code=code)
    if float(value) != float(expected):
        raise StrictRefusal(
            f"{name} is {value!r}, frozen at {expected!r}; the frozen protocol is never "
            "adjusted to fit a run",
            reason_code=code,
        )
    return float(value)


def require_finite(values, name: str, *, code: str) -> None:
    """Refuse NaN, +/-inf anywhere in an array-like."""
    import numpy as np

    array = np.asarray(values)
    if array.size and not bool(np.isfinite(array).all()):
        raise StrictRefusal(f"{name} carries a non-finite value", reason_code=code)


def contained_relative_path(candidate: str, *, name: str, code: str) -> str:
    """A relative, normalised POSIX path contained in the canonical root.

    Refuses absolute paths, drive letters, UNC prefixes, ``..``, NUL bytes, empty segments
    and anything that escapes after normalisation.  The caller never chooses the root.
    """
    if not isinstance(candidate, str) or not candidate:
        raise StrictRefusal(f"{name} is not a non-empty string", reason_code=code)
    if "\x00" in candidate:
        raise StrictRefusal(f"{name} contains a NUL byte", reason_code=code)
    if "\\" in candidate:
        raise StrictRefusal(f"{name} contains a backslash separator", reason_code=code)
    if candidate.startswith("/") or candidate.startswith("//"):
        raise StrictRefusal(f"{name} is absolute", reason_code=code)
    if len(candidate) >= 2 and candidate[1] == ":":
        raise StrictRefusal(f"{name} carries a drive letter", reason_code=code)
    segments = candidate.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        raise StrictRefusal(
            f"{name} has an empty, current or parent segment: {candidate!r}", reason_code=code
        )
    normalised = posixpath.normpath(candidate)
    if normalised != candidate:
        raise StrictRefusal(
            f"{name} is not in normal form ({normalised!r} != {candidate!r})", reason_code=code
        )
    return candidate


def resolve_contained(root, relative: str, *, name: str, code: str):
    """Resolve ``relative`` under ``root``, refusing symlinks at any level."""
    from pathlib import Path

    contained_relative_path(relative, name=name, code=code)
    base = Path(root).resolve(strict=False)
    target = base
    for segment in relative.split("/"):
        target = target / segment
        if target.is_symlink():
            raise StrictRefusal(
                f"{name} traverses or ends on a symlink at {segment!r}", reason_code=code
            )
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise StrictRefusal(
            f"{name} escapes the canonical root after resolution", reason_code=code
        ) from exc
    if target.exists() and not target.is_file() and not target.is_dir():
        raise StrictRefusal(f"{name} is a special file", reason_code=code)
    return target


def check_frozen_measurement_spec(spec: Any, *, code: str = "MEASUREMENT_SPEC_NOT_FROZEN") -> None:
    """Refuse any measurement specification that is not the frozen one.

    This is the A1-R3 defect B3: ``MeasurementSpec(min_cells=1)`` was hard-coded in BOTH the
    producer and the verifier, so the two agreed and no differential check could fire.  The
    frozen values are asserted here, against a single authority both sides import.
    """
    for name, expected in FROZEN_MEASUREMENT_SPEC.items():
        observed = getattr(spec, name, None)
        if observed is None:
            raise StrictRefusal(f"the measurement spec has no {name}", reason_code=code)
        if isinstance(expected, int) and not isinstance(expected, bool):
            got = require_plain_int(observed, f"measurement_spec.{name}", code=code)
            if got != expected:
                raise StrictRefusal(
                    f"measurement_spec.{name} is {got}, frozen at {expected}",
                    reason_code=code,
                )
        else:
            require_exact_float(observed, float(expected), f"measurement_spec.{name}", code=code)
