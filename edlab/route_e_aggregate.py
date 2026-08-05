"""A1-R5 production aggregator.  k, d, psi over the frozen primary units, fail-closed.

A1-R4's tests defined their own ``_aggregate`` helper locally, so they tested a function
that shipped nowhere.  This is the real one, imported by the tests and by the admission.

FROZEN RULES
------------
* exactly 67 paired units, no more and no fewer;
* every value is 0, 1 or an explicit technical incident -- never 2, never a bool, never a
  bare ``None`` compared with 0 or 1;
* ``k(f)`` sums the FIRST initial condition only;
* the SECOND initial condition enters ``d(f)`` and ``psi(f)`` and nothing else;
* any technical incident on either member invalidates the paired unit AND forbids the
  confirmatory result, which stays ``TECHNICAL_INVALID`` with no imputation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from . import route_e_strict as _strict

__all__ = ["PRIMARY_LAWS", "AggregateResult", "aggregate_primary_units"]

PRIMARY_LAWS = _strict.FROZEN_PRIMARY_SHAPE["primary_laws"]


@dataclass(frozen=True)
class AggregateResult:
    """One convention's aggregate.  ``k``/``d``/``psi`` are ``None`` when invalid."""

    f: str
    status: str
    k: int | None
    d: int | None
    psi: float | None
    invalid_units: tuple[int, ...]


def _checked_indicator(value: Any, *, where: str) -> int | None:
    """0, 1, or None for a declared technical incident.  Anything else refuses."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise _strict.StrictRefusal(
            f"{where} is a boolean; an indicator is 0, 1 or an explicit incident",
            reason_code="INDICATOR_NOT_PLAIN_INT",
        )
    if not isinstance(value, int):
        raise _strict.StrictRefusal(
            f"{where} is not an integer: {value!r}", reason_code="INDICATOR_NOT_PLAIN_INT"
        )
    if value not in (0, 1):
        raise _strict.StrictRefusal(
            f"{where} is {value!r}; an indicator is 0 or 1", reason_code="INDICATOR_OUT_OF_RANGE"
        )
    return int(value)


def aggregate_primary_units(
    pairs: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
    *,
    conventions: Sequence[float] = _strict.COHORT_RESIDUAL_CONVENTIONS,
    primary_laws: int = PRIMARY_LAWS,
) -> dict[str, AggregateResult]:
    """Aggregate exactly ``primary_laws`` paired units, fail-closed."""
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)):
        raise _strict.StrictRefusal("pairs is not a sequence", reason_code="PAIRS_MALFORMED")
    if len(pairs) != primary_laws:
        raise _strict.StrictRefusal(
            f"{len(pairs)} paired units for a frozen {primary_laws}; the frozen design is "
            "never rescaled to fit a run",
            reason_code="PRIMARY_UNIT_COUNT_WRONG",
        )
    keys = [f"{value:g}" for value in conventions]
    out: dict[str, AggregateResult] = {}
    for key in keys:
        invalid: list[int] = []
        first: list[int | None] = []
        second: list[int | None] = []
        for index, pair in enumerate(pairs):
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise _strict.StrictRefusal(
                    f"unit {index} is not a (Y_i1, Y_i2) pair", reason_code="PAIRS_MALFORMED"
                )
            for slot, member in enumerate(pair):
                if not isinstance(member, Mapping):
                    raise _strict.StrictRefusal(
                        f"unit {index} member {slot} is not a mapping",
                        reason_code="PAIRS_MALFORMED",
                    )
                if key not in member:
                    raise _strict.StrictRefusal(
                        f"unit {index} member {slot} has no convention {key!r}",
                        reason_code="CONVENTION_ABSENT",
                    )
            y1 = _checked_indicator(pair[0][key], where=f"unit {index} Y_i1[{key}]")
            y2 = _checked_indicator(pair[1][key], where=f"unit {index} Y_i2[{key}]")
            if y1 is None or y2 is None:
                invalid.append(index)
            first.append(y1)
            second.append(y2)
        if invalid:
            out[key] = AggregateResult(
                f=key, status="TECHNICAL_INVALID", k=None, d=None, psi=None,
                invalid_units=tuple(invalid),
            )
            continue
        k = sum(int(value) for value in first)          # FIRST initial condition ONLY
        d = sum(1 for a, b in zip(first, second) if a != b)
        out[key] = AggregateResult(
            f=key, status="COMPLETE", k=k, d=d, psi=d / float(primary_laws), invalid_units=()
        )
    return out
