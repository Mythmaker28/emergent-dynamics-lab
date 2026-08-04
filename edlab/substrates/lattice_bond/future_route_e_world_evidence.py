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
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

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
            raise ValueError(f"{path.name}: mask length {len(payload)} != {cells}")
        values = np.frombuffer(payload, dtype=np.uint8)
        if bool(np.any(values > 1)):
            raise ValueError(f"{path.name}: mask is not a canonical 0/1 field")
        return values.reshape(shape).astype(bool)
    if len(payload) != cells * 8:
        raise ValueError(f"{path.name}: float length {len(payload)} != {cells * 8}")
    values = np.frombuffer(payload, dtype="<f8")
    if not bool(np.isfinite(values).all()):
        raise ValueError(f"{path.name}: channel carries a non-finite value")
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
        for point in track.points:
            owner[(int(point.frame), int(point.component_index))] = int(track.track_id)

    assignments: list[list[Any]] = []
    for position, label in enumerate(sampled_frames):
        for component in frames[position]:
            digest = cell_set_digest(component.cells)
            track_id = owner.get((int(label), int(component.index)), -1)
            assignments.append([int(label), digest, track_id])
    assignments.sort(key=lambda item: (item[0], item[1]))

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
    matter_last = read_channel(directory, len(labels) - 1, "matter", shape)
    tracer_last = read_channel(directory, len(labels) - 1, "tracer", shape)
    by_index_last = {int(c.index): c for c in frames[-1]}

    eligible: list[int] = []
    residuals: dict[int, float] = {}
    observed_from_first = False
    for track in tracking.tracks:
        points = list(track.points)
        if not points:
            continue
        if int(points[-1].frame) != last_label:
            continue  # did not reach the horizon
        component = by_index_last.get(int(points[-1].component_index))
        if component is None:
            continue
        if bool(component.wraps_y or component.wraps_x):
            continue
        if int(component.area) * 2 > cells_total:
            continue
        rows, cols = np.divmod(np.asarray(sorted(int(c) for c in component.cells)), shape[1])
        mass = float(np.sum(matter_last[rows, cols]))
        if not mass > 0.0:
            continue
        cohort = float(np.sum(tracer_last[rows, cols]))
        eligible.append(int(track.track_id))
        residuals[int(track.track_id)] = cohort / mass if mass > 0.0 else 1.0
        if int(points[0].frame) == first_label and len(points) == len(labels):
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
