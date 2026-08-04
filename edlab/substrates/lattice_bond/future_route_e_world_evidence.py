"""Route E per-world evidence: the track/component join and the outcome derivation.  A1-R3.

WHAT THIS FIXES
---------------
A1-R2 declared ``JOIN_EVIDENCE_NAME = "TRACK_COMPONENT_JOIN.json"`` and never wrote it, and
its admission derived no outcome at all beyond the four observed-failure terminal states, so
no path could ever produce ``Y = 1``.  This module supplies both halves:

* :func:`build_join_document` -- the real ``TRACK_COMPONENT_JOIN.json``, PRB-1's literal
  obligation: ``(frame, canonical cell-set digest, track_id)`` for every observed component,
  derived from the PERSISTED mask frames and nothing else.
* :func:`derive_world_outcome` -- the existential Route E criterion, evaluated separately at
  each of the three frozen conventions ``f in {0.01, 0.05, 0.20}``.

WHY IT IS A SEPARATE MODULE
---------------------------
The join has exactly one definition.  The producer writes it and the verifier recomputes it,
both from the same persisted bytes, and the verifier refuses on any disagreement.  Putting
the definition in the producer and having the verifier import a private helper of the
producer -- which is what A1-R2 did -- is what made the independence claim indefensible.
Here neither side owns the definition.

WHAT IS RECOMPUTED, AND FROM WHAT
---------------------------------
Everything comes from ``measurement_frames/frame_NNNNNN_{mask,matter,tracer}.bin``:

* the mask frames give the components, the tracks and the join;
* ``matter`` and ``tracer`` give ``cohort_residual = cohort_mass / mass`` over the tracked
  component's own cells, which is the replacement evidence A1-R2 never verified.

No engine step is taken anywhere in this module and no ``LatticeBondEngine`` is constructed.
``LatticeBondState`` is used only as an inert container the frozen detector accepts.
"""

from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ... import route_e_strict as _strict
from .engine import LatticeBondState
from .instrumentation import (
    DetectedComponent,
    DetectorSpec,
    TrackerSpec,
    detect_components,
    track_components,
)

__all__ = [
    "JOIN_KIND",
    "COHORT_RESIDUAL_CONVENTIONS",
    "WorldEvidence",
    "cell_set_digest",
    "read_channel",
    "build_join_document",
    "derive_world_outcome",
]

JOIN_KIND = "route-e-track-component-join/v1"

#: The three frozen conventions.  They are evaluated SEPARATELY and never merged.
COHORT_RESIDUAL_CONVENTIONS: tuple[float, ...] = (0.01, 0.05, 0.20)

_MASK_PRESENT = 0.8
_MASK_ABSENT = 0.1
_MASK_RESOURCE = 0.8


def cell_set_digest(cells: Sequence[int]) -> str:
    """Canonical digest of a component's cell set.  Order-independent by construction."""
    payload = b"EDLAB/ROUTE-E/CELLSET/v1\x00" + b"".join(
        struct.pack("<q", int(cell)) for cell in sorted(int(c) for c in cells)
    )
    return hashlib.sha256(payload).hexdigest()


def read_channel(
    world_directory: Path, position: int, channel: str, shape: tuple[int, int]
) -> np.ndarray:
    """Read one persisted channel frame, refusing any length or value violation."""
    path = world_directory / "measurement_frames" / f"frame_{position:06d}_{channel}.bin"
    payload = path.read_bytes()
    cells = shape[0] * shape[1]
    if channel == "mask":
        if len(payload) != cells:
            raise _strict.StrictRefusal(f"{path.name}: mask length {len(payload)} != {cells}", reason_code="CHANNEL_SHAPE")
        values = np.frombuffer(payload, dtype=np.uint8)
        if bool(np.any(values > 1)):
            raise _strict.StrictRefusal(f"{path.name}: mask is not a canonical 0/1 field", reason_code="CHANNEL_SHAPE")
        return values.reshape(shape).astype(bool)
    if len(payload) != cells * 8:
        raise _strict.StrictRefusal(f"{path.name}: float length {len(payload)} != {cells * 8}", reason_code="CHANNEL_SHAPE")
    values = np.frombuffer(payload, dtype="<f8")
    if not bool(np.isfinite(values).all()):
        raise _strict.StrictRefusal(f"{path.name}: channel carries a non-finite value", reason_code="CHANNEL_NON_FINITE")
    return values.reshape(shape)


def _materialise(mask: np.ndarray, frame: int) -> LatticeBondState:
    """Inert container matching the owned pipeline's own materialisation convention."""
    shape = (int(mask.shape[0]), int(mask.shape[1]))
    matter = np.where(mask, _MASK_PRESENT, _MASK_ABSENT).astype(np.float64)
    resource = np.full(shape, _MASK_RESOURCE, dtype=np.float64)
    bond = np.zeros((2, *shape), dtype=np.float64)
    return LatticeBondState(matter, resource, bond, frame)


def _detect_all(
    world_directory: Path,
    sampled_frames: Sequence[int],
    shape: tuple[int, int],
    detector: DetectorSpec,
) -> list[list[DetectedComponent]]:
    frames: list[list[DetectedComponent]] = []
    for position, label in enumerate(sampled_frames):
        mask = read_channel(world_directory, position, "mask", shape)
        frames.append(list(detect_components(_materialise(mask, int(label)), detector, frame=int(label))))
    return frames


def build_join_document(
    world_directory: str | Path,
    *,
    sampled_frames: Sequence[int],
    frame_shape: Sequence[int],
    detector: DetectorSpec,
    tracker: TrackerSpec,
    horizon_steps: int,
    cadence_steps: int,
) -> dict[str, Any]:
    """PRB-1's literal obligation, produced from persisted bytes.

    ``assignments`` is the list of ``[frame, cell_set_digest, track_id]`` triples.  A
    component observed at a frame but belonging to no track is recorded with a ``track_id``
    of ``-1`` rather than dropped: a component that the tracker refused to associate is
    evidence, and silently omitting it would hide exactly the association-gate break the
    frozen taxonomy wants counted.
    """
    directory = Path(world_directory)
    shape = (int(frame_shape[0]), int(frame_shape[1]))
    frames = _detect_all(directory, sampled_frames, shape, detector)
    tracking = track_components(tuple(frames), tracker, sampled_frames=tuple(int(f) for f in sampled_frames))

    owner: dict[tuple[int, int], int] = {}
    for track in tracking.tracks:
        if int(track.track_id) < 0:
            raise _strict.StrictRefusal(
                f"track {track.track_id} has a negative identifier", reason_code="JOIN_NEGATIVE_TRACK_ID"
            )
        for point in track.points:
            key = (int(point.frame), int(point.component_index))
            if key in owner:
                raise _strict.StrictRefusal(
                    f"component {key} is claimed by two tracks", reason_code="JOIN_DUPLICATE"
                )
            owner[key] = int(track.track_id)

    assignments: list[list[Any]] = []
    for position, label in enumerate(sampled_frames):
        for component in frames[position]:
            key = (int(label), int(component.index))
            if key not in owner:
                # A1-R4 closes the A1-R3 design choice of recording a negative track identifier.  An
                # orphan component is a gap in the join, not evidence to carry forward:
                # the frozen requirement is EXACT coverage of every detected component.
                raise _strict.StrictRefusal(
                    f"component {key} is detected but assigned to no track",
                    reason_code="JOIN_ORPHAN_COMPONENT",
                )
            assignments.append([int(label), cell_set_digest(component.cells), owner[key]])
    assignments.sort(key=lambda item: (item[0], item[1]))

    detected = sum(len(frame_components) for frame_components in frames)
    if len(assignments) != detected:
        raise _strict.StrictRefusal(
            f"the join holds {len(assignments)} assignments for {detected} detected components",
            reason_code="JOIN_COVERAGE_INEXACT",
        )
    if len(owner) != detected:
        raise _strict.StrictRefusal(
            "a track claims a component that no frame detected",
            reason_code="JOIN_SURPLUS_ENTRY",
        )

    return {
        "assignments": assignments,
        "cadence_steps": int(cadence_steps),
        "horizon_steps": int(horizon_steps),
        "kind": JOIN_KIND,
        "sampled_frames": [int(f) for f in sampled_frames],
    }


@dataclass(frozen=True)
class WorldEvidence:
    """One world's outcome, recomputed from persisted bytes, at all three conventions."""

    any_wrapping_component: bool
    eligible_track_ids: tuple[int, ...]
    mechanically_ineligible: bool
    terminal_states: tuple[str, ...]
    persisted_to_horizon: bool
    #: track_id -> minimum cohort residual observed at the last sampled frame
    residual_at_horizon: Mapping[int, float]
    #: f -> Y in {0, 1}
    Y_by_f: Mapping[str, int]
    #: f -> the frozen DrawDisposition value
    disposition_by_f: Mapping[str, str]
    observed_from_first_frame: bool
    notes: tuple[str, ...]


def derive_world_outcome(
    world_directory: str | Path,
    *,
    sampled_frames: Sequence[int],
    frame_shape: Sequence[int],
    detector: DetectorSpec,
    tracker: TrackerSpec,
) -> WorldEvidence:
    """The existential Route E criterion, evaluated at each frozen ``f`` separately.

        at least one ELIGIBLE component
        AND persistence to the horizon
        AND cohort residual <= f

    Eligibility is the frozen four-clause rule: a non-wrapping component, area <= L^2/2,
    mass > 0 at readout, and NO wrapping component anywhere in the world at ANY sampled
    frame.  The fourth clause is a property of the whole world, so one percolating
    component at one frame makes the entire world mechanically ineligible.
    """
    directory = Path(world_directory)
    shape = (int(frame_shape[0]), int(frame_shape[1]))
    cells_total = shape[0] * shape[1]
    labels = [int(f) for f in sampled_frames]
    frames = _detect_all(directory, labels, shape, detector)
    tracking = track_components(tuple(frames), tracker, sampled_frames=tuple(labels))
    notes: list[str] = []

    any_wrapping = any(
        bool(component.wraps_y or component.wraps_x)
        for frame_components in frames
        for component in frame_components
    )

    terminal_states = tuple(
        sorted({str(event.kind) for event in tracking.events if str(event.kind) in _TERMINAL_EVENTS})
    )
    mapped = tuple(_TERMINAL_EVENTS[state] for state in terminal_states)

    if any_wrapping:
        notes.append(
            "a wrapping component exists at some sampled frame: the whole world is "
            "mechanically ineligible under the frozen fourth clause"
        )
        zero = {f"{value:g}": 0 for value in COHORT_RESIDUAL_CONVENTIONS}
        return WorldEvidence(
            any_wrapping_component=True,
            eligible_track_ids=(),
            mechanically_ineligible=True,
            terminal_states=mapped,
            persisted_to_horizon=False,
            residual_at_horizon={},
            Y_by_f=zero,
            disposition_by_f={k: "MECHANICALLY_INELIGIBLE" for k in zero},
            observed_from_first_frame=False,
            notes=tuple(notes),
        )

    last_label = labels[-1]
    first_label = labels[0]

    # PHYSICAL BOUNDS, enforced BEFORE any outcome arithmetic.  A1-R3 computed the
    # residual straight from the arrays; a negative tracer, a tracer above the matter it
    # labels, a NaN or a zero denominator all produced a silent number.
    matter_last = read_channel(directory, len(labels) - 1, "matter", shape)
    tracer_last = read_channel(directory, len(labels) - 1, "tracer", shape)
    matter_first = read_channel(directory, 0, "matter", shape)
    tracer_first = read_channel(directory, 0, "tracer", shape)
    for name, array in (
        ("matter@first", matter_first), ("tracer@first", tracer_first),
        ("matter@horizon", matter_last), ("tracer@horizon", tracer_last),
    ):
        _strict.require_finite(array, name, code="CHANNEL_NON_FINITE")
    for name, matter, tracer in (
        ("first", matter_first, tracer_first), ("horizon", matter_last, tracer_last)
    ):
        if float(np.min(matter)) < 0.0:
            raise _strict.StrictRefusal(f"matter@{name} is negative", reason_code="MATTER_NEGATIVE")
        if float(np.min(tracer)) < 0.0:
            raise _strict.StrictRefusal(f"tracer@{name} is negative", reason_code="TRACER_NEGATIVE")
        if float(np.max(tracer - matter)) > 1e-12:
            raise _strict.StrictRefusal(
                f"tracer@{name} exceeds the matter it labels", reason_code="TRACER_ABOVE_MATTER"
            )

    by_index_last = {int(c.index): c for c in frames[-1]}
    by_index_first = {int(c.index): c for c in frames[0]}

    eligible: list[int] = []
    residuals: dict[int, float] = {}
    observed_from_first = False
    for track in tracking.tracks:
        points = list(track.points)
        if not points:
            continue
        if int(track.track_id) < 0:
            continue
        # A1-R4: the candidate must exist at the ENROLMENT frame, be assigned exactly once
        # per scheduled frame, keep the SAME track throughout, and reach the horizon.  A
        # component born after enrolment carries residual ~0 by construction and could
        # otherwise score 1 trivially -- the frozen rule now forbids it.
        if int(points[0].frame) != first_label:
            continue
        if int(points[-1].frame) != last_label:
            continue
        observed = [int(point.frame) for point in points]
        if observed != labels:
            continue  # a missing intermediate frame, or disappear-then-reappear
        if len(set(observed)) != len(observed):
            continue  # assigned twice at one frame
        enrolled = by_index_first.get(int(points[0].component_index))
        if enrolled is None:
            continue
        rows0, cols0 = np.divmod(np.asarray(sorted(int(c) for c in enrolled.cells)), shape[1])
        cohort_initial = float(np.sum(tracer_first[rows0, cols0]))
        if not cohort_initial > 0.0:
            raise _strict.StrictRefusal(
                f"track {track.track_id} enrols an empty cohort", reason_code="COHORT_EMPTY"
            )
        component = by_index_last.get(int(points[-1].component_index))
        if component is None:
            continue
        # continuous eligibility at EVERY scheduled frame, not only at the horizon
        continuously_eligible = True
        for position, point in enumerate(points):
            observed_component = next(
                (c for c in frames[position] if int(c.index) == int(point.component_index)), None
            )
            if observed_component is None:
                continuously_eligible = False
                break
            if bool(observed_component.wraps_y or observed_component.wraps_x):
                continuously_eligible = False
                break
            if int(observed_component.area) * 2 > cells_total:
                continuously_eligible = False
                break
        if not continuously_eligible:
            continue
        rows, cols = np.divmod(np.asarray(sorted(int(c) for c in component.cells)), shape[1])
        mass = float(np.sum(matter_last[rows, cols]))
        if not mass > 0.0:
            continue
        cohort = float(np.sum(tracer_last[rows, cols]))
        residual = cohort / mass
        if not (0.0 <= residual <= 1.0) or not math.isfinite(residual):
            raise _strict.StrictRefusal(
                f"track {track.track_id} residual {residual!r} leaves [0,1]",
                reason_code="RESIDUAL_OUT_OF_DOMAIN",
            )
        eligible.append(int(track.track_id))
        residuals[int(track.track_id)] = residual
        observed_from_first = True

    if not eligible:
        zero = {f"{value:g}": 0 for value in COHORT_RESIDUAL_CONVENTIONS}
        if mapped:
            disposition = {k: mapped[0] for k in zero}
            notes.append("no eligible component reached the horizon: observed failure")
        else:
            disposition = {k: "MECHANICALLY_INELIGIBLE" for k in zero}
            notes.append("no eligible component at all: mechanically ineligible")
        return WorldEvidence(
            any_wrapping_component=False,
            eligible_track_ids=(),
            mechanically_ineligible=not mapped,
            terminal_states=mapped,
            persisted_to_horizon=False,
            residual_at_horizon={},
            Y_by_f=zero,
            disposition_by_f=disposition,
            observed_from_first_frame=False,
            notes=tuple(notes),
        )

    best = min(residuals[track_id] for track_id in eligible)
    Y_by_f: dict[str, int] = {}
    disposition_by_f: dict[str, str] = {}
    for value in COHORT_RESIDUAL_CONVENTIONS:
        key = f"{value:g}"
        if best <= value:
            Y_by_f[key] = 1
            disposition_by_f[key] = "SUCCESS"
        else:
            # THE correction of A1-R2 defect 11.  A correctly observed survivor whose
            # replacement is not verified under f is an OBSERVED FAILURE inside the
            # declared horizon, hence Y = 0.  It is never UNKNOWN: nothing failed.
            Y_by_f[key] = 0
            disposition_by_f[key] = "OBSERVED_FAILURE_HORIZON_WITHOUT_REPLACEMENT"
    if not observed_from_first:
        notes.append(
            "no eligible surviving track was observed at the cohort-enrolment frame; the "
            "cohort is enrolled once at the first sampled frame, so a component that first "
            "appears later carries residual ~0 by construction.  Recorded, not scored."
        )
    return WorldEvidence(
        any_wrapping_component=False,
        eligible_track_ids=tuple(sorted(eligible)),
        mechanically_ineligible=False,
        terminal_states=mapped,
        persisted_to_horizon=True,
        residual_at_horizon=dict(residuals),
        Y_by_f=Y_by_f,
        disposition_by_f=disposition_by_f,
        observed_from_first_frame=observed_from_first,
        notes=tuple(notes),
    )


_TERMINAL_EVENTS: Mapping[str, str] = {
    "DISSOLUTION": "DISSOLVED_DETECTED_TRACK",
    "SPLIT": "SPLIT_INTO_TRACKS",
    "MERGE": "MERGED_INTO_TRACK",
    "TRACKING_UNRESOLVED": "UNRESOLVED_HANDOFF",
}
