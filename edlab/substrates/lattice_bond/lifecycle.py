"""Future-only, fail-closed lifecycle closure for generic tracker output.

The contract in this module is deliberately downstream of detection and
tracking.  It reads no lattice fields, physics, regimes, candidates, laws,
seeds, or intervention outcomes.  Association edges remain separate tracker
audit evidence: the lifecycle-input digest binds only the complete schedule,
tracks, events, and assignments used by this closure theorem.  This module is
not wired into any historical writer.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from numbers import Integral
import os
from pathlib import Path
import tempfile
from typing import Any, Literal, Mapping, Sequence

from .instrumentation import TrackEvent, TrackRecord, TrackingResult


SCHEMA_VERSION = "future-lifecycle-contract/v1"
VALIDATOR_VERSION = "1.0.0"

TerminalState = Literal[
    "DISSOLVED_DETECTED_TRACK",
    "SPLIT_INTO_TRACKS",
    "MERGED_INTO_TRACK",
    "UNRESOLVED_HANDOFF",
    "RIGHT_CENSORED_AT_HORIZON",
]

_KNOWN_EVENT_KINDS = frozenset(
    {
        "APPEARANCE",
        "CONTINUATION",
        "SPLIT",
        "MERGE",
        "TEMPORARY_CONTACT",
        "DISSOLUTION",
        "TRACKING_UNRESOLVED",
    }
)
_ONSET_EVENT_KINDS = frozenset(
    {"APPEARANCE", "SPLIT", "MERGE", "TRACKING_UNRESOLVED"}
)
_TERMINAL_EVENT_STATES: Mapping[str, TerminalState] = {
    "DISSOLUTION": "DISSOLVED_DETECTED_TRACK",
    "SPLIT": "SPLIT_INTO_TRACKS",
    "MERGE": "MERGED_INTO_TRACK",
    "TRACKING_UNRESOLVED": "UNRESOLVED_HANDOFF",
}

_ERROR_PRECEDENCE = {
    code: index
    for index, code in enumerate(
        (
            "EMPTY_SAMPLE_SCHEDULE",
            "INVALID_SAMPLE_FRAME",
            "NON_INCREASING_SAMPLE_SCHEDULE",
            "INVALID_TRACK_ID",
            "DUPLICATE_TRACK_ID",
            "EMPTY_TRACK",
            "INVALID_TRACK_POINT",
            "TRACK_POINT_OUTSIDE_SCHEDULE",
            "DUPLICATE_COMPONENT_POINT",
            "TRACK_POINT_GAP",
            "INVALID_LINEAGE_IDS",
            "DUPLICATE_LINEAGE_ID",
            "SELF_LINEAGE_LINK",
            "UNKNOWN_LINEAGE_ID",
            "CYCLIC_LINEAGE",
            "INVALID_UNRESOLVED_FLAG",
            "INVALID_ASSIGNMENT",
            "DUPLICATE_ASSIGNMENT",
            "CONFLICTING_COMPONENT_ASSIGNMENT",
            "ASSIGNMENT_SET_MISMATCH",
            "INVALID_EVENT_FRAME",
            "UNKNOWN_EVENT_KIND",
            "INVALID_EVENT_IDS",
            "DUPLICATE_EVENT_ID",
            "INVALID_EVENT_COMPONENT",
            "DUPLICATE_EVENT_COMPONENT",
            "INVALID_EVENT_RESOLUTION",
            "DUPLICATE_EVENT",
            "EVENT_CARDINALITY_MISMATCH",
            "EVENT_POLARITY_MISMATCH",
            "EVENT_COMPONENT_UNASSIGNED",
            "EVENT_COMPONENT_POLARITY_MISMATCH",
            "EVENT_COMPONENT_FRAME_MISMATCH",
            "EVENT_TEMPORAL_MISMATCH",
            "MISSING_ONSET_EVENT",
            "MULTIPLE_ONSET_EVENTS",
            "PARENT_LINK_MISMATCH",
            "MISSING_CONTINUATION_EVENT",
            "MULTIPLE_CONTINUATION_EVENTS",
            "UNEXPECTED_CONTINUATION_EVENT",
            "MULTIPLE_TERMINAL_EVENTS",
            "SILENT_PRE_HORIZON_TERMINATION",
            "TERMINAL_FRAME_MISMATCH",
            "TERMINAL_AT_HORIZON",
            "CHILD_LINK_MISMATCH",
            "UNRESOLVED_FLAG_MISMATCH",
            "POST_TERMINAL_EVENT",
            "TERMINAL_COUNT_MISMATCH",
            "DOCUMENT_INVALID_JSON",
            "DOCUMENT_NOT_CANONICAL",
            "DOCUMENT_BINDING_MISMATCH",
        )
    )
}


def _is_int(value: object) -> bool:
    return isinstance(value, Integral) and not isinstance(value, bool)


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class LifecycleViolation:
    code: str
    detail: str
    track_id: int | None = None
    frame: int | None = None
    event_id: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "detail": self.detail,
            "event_id": self.event_id,
            "frame": self.frame,
            "track_id": self.track_id,
        }


def _violation_key(item: LifecycleViolation) -> tuple[object, ...]:
    return (
        _ERROR_PRECEDENCE.get(item.code, len(_ERROR_PRECEDENCE)),
        -1 if item.track_id is None else item.track_id,
        -1 if item.frame is None else item.frame,
        "" if item.event_id is None else item.event_id,
        item.detail,
    )


class LifecycleContractError(ValueError):
    """One or more fail-closed lifecycle invariants were violated."""

    def __init__(self, violations: Sequence[LifecycleViolation]):
        ordered = tuple(sorted(violations, key=_violation_key))
        if not ordered:
            raise ValueError("LifecycleContractError requires at least one violation")
        self.violations = ordered
        summary = "; ".join(
            f"{item.code}"
            + (f" track={item.track_id}" if item.track_id is not None else "")
            + (f" frame={item.frame}" if item.frame is not None else "")
            for item in ordered
        )
        super().__init__(f"FUTURE_LIFECYCLE_CONTRACT_INVALID: {summary}")


class LifecyclePublicationError(RuntimeError):
    """The qualified future-only contract could not be published atomically."""


@dataclass(frozen=True)
class LifecycleTerminalRecord:
    track_id: int
    first_observed_frame: int
    last_observed_frame: int
    last_component_index: int
    terminal_frame: int
    terminal_state: TerminalState
    evidence_kind: Literal["TRACK_EVENT", "DECLARED_HORIZON"]
    terminal_event_id: str | None
    parent_track_ids: tuple[int, ...]
    successor_track_ids: tuple[int, ...]
    lineage_status: Literal["RESOLVED", "UNRESOLVED"]

    def as_dict(self) -> dict[str, object]:
        return {
            "evidence_kind": self.evidence_kind,
            "first_observed_frame": self.first_observed_frame,
            "last_component_index": self.last_component_index,
            "last_observed_frame": self.last_observed_frame,
            "lineage_status": self.lineage_status,
            "parent_track_ids": list(self.parent_track_ids),
            "successor_track_ids": list(self.successor_track_ids),
            "terminal_event_id": self.terminal_event_id,
            "terminal_frame": self.terminal_frame,
            "terminal_state": self.terminal_state,
            "track_id": self.track_id,
        }


@dataclass(frozen=True)
class LifecycleRunClosure:
    sampled_frames: tuple[int, ...]
    lifecycle_input_digest_sha256: str
    records_digest_sha256: str
    track_count: int
    event_count: int
    assignment_count: int
    terminal_records: tuple[LifecycleTerminalRecord, ...]

    @property
    def run_terminal_state(self) -> str:
        return "EMPTY_TRACK_SET" if self.track_count == 0 else "ALL_TRACKS_CLOSED"

    def as_dict(self) -> dict[str, object]:
        return {
            "lifecycle_binding": {
                "records_sha256": self.records_digest_sha256,
                "terminal_record_count": len(self.terminal_records),
            },
            "qualification": {
                "all_tracks_closed": True,
                "disposition": "QUALIFIED",
                "run_terminal_state": self.run_terminal_state,
            },
            "sampled_frames": list(self.sampled_frames),
            "schema_version": SCHEMA_VERSION,
            "source_binding": {
                "assignment_count": self.assignment_count,
                "event_count": self.event_count,
                "lifecycle_input_sha256": self.lifecycle_input_digest_sha256,
                "track_count": self.track_count,
            },
            "terminal_records": [item.as_dict() for item in self.terminal_records],
            "validator_version": VALIDATOR_VERSION,
        }


@dataclass(frozen=True)
class _TrackView:
    record: TrackRecord
    track_id: int
    points: tuple[tuple[int, int], ...]
    parents: tuple[int, ...]
    children: tuple[int, ...]
    unresolved: bool


@dataclass(frozen=True)
class _EventView:
    event: TrackEvent
    frame: int
    kind: str
    sources: tuple[int, ...]
    source_components: tuple[tuple[int, int], ...]
    target_components: tuple[tuple[int, int], ...]
    targets: tuple[int, ...]
    resolved: bool
    event_id: str

    def payload(self) -> dict[str, object]:
        return {
            "frame": self.frame,
            "kind": self.kind,
            "resolved": self.resolved,
            "source_components": [list(item) for item in self.source_components],
            "source_track_ids": list(self.sources),
            "target_components": [list(item) for item in self.target_components],
            "target_track_ids": list(self.targets),
        }


def _add(
    violations: list[LifecycleViolation],
    code: str,
    detail: str,
    *,
    track_id: int | None = None,
    frame: int | None = None,
    event_id: str | None = None,
) -> None:
    violations.append(LifecycleViolation(code, detail, track_id, frame, event_id))


def _normalize_id_tuple(
    values: object,
    *,
    field: str,
    violations: list[LifecycleViolation],
    event_id: str | None = None,
    track_id: int | None = None,
) -> tuple[int, ...] | None:
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError:
        _add(
            violations,
            "INVALID_EVENT_IDS" if event_id else "INVALID_LINEAGE_IDS",
            f"{field} is not a sequence",
            track_id=track_id,
            event_id=event_id,
        )
        return None
    if any(not _is_int(value) or int(value) < 0 for value in items):
        _add(
            violations,
            "INVALID_EVENT_IDS" if event_id else "INVALID_LINEAGE_IDS",
            f"{field} must contain nonnegative integers",
            track_id=track_id,
            event_id=event_id,
        )
        return None
    normalized = tuple(int(value) for value in items)
    if len(set(normalized)) != len(normalized):
        _add(
            violations,
            "DUPLICATE_EVENT_ID" if event_id else "DUPLICATE_LINEAGE_ID",
            f"{field} contains a duplicate ID",
            track_id=track_id,
            event_id=event_id,
        )
    return tuple(sorted(normalized))


def _normalize_component_tuple(
    values: object,
    *,
    field: str,
    violations: list[LifecycleViolation],
    event_id: str,
) -> tuple[tuple[int, int], ...] | None:
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError:
        _add(violations, "INVALID_EVENT_COMPONENT", f"{field} is not a sequence", event_id=event_id)
        return None
    normalized: list[tuple[int, int]] = []
    for value in items:
        if (
            not isinstance(value, (tuple, list))
            or len(value) != 2
            or not _is_int(value[0])
            or not _is_int(value[1])
            or int(value[1]) < 0
        ):
            _add(
                violations,
                "INVALID_EVENT_COMPONENT",
                f"{field} must contain (frame, nonnegative component) pairs",
                event_id=event_id,
            )
            return None
        normalized.append((int(value[0]), int(value[1])))
    if len(set(normalized)) != len(normalized):
        _add(
            violations,
            "DUPLICATE_EVENT_COMPONENT",
            f"{field} contains a duplicate component key",
            event_id=event_id,
        )
    return tuple(sorted(normalized))


def _stable_raw_seed(value: object) -> object:
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if _is_int(value):
        return {"type": "int", "value": int(value)}
    if isinstance(value, str):
        return {"type": "str", "value": value}
    if value is None:
        return {"type": "null"}
    if isinstance(value, (tuple, list)):
        items = [_stable_raw_seed(item) for item in value]
        return {
            "type": "sequence",
            "items": sorted(items, key=_canonical_json_bytes),
        }
    return {"type": type(value).__name__, "repr": repr(value)}


def _stable_id_seed(values: object) -> object:
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError:
        return _stable_raw_seed(values)
    if all(_is_int(item) for item in items):
        return [int(item) for item in sorted(items, key=int)]
    return _stable_raw_seed(items)


def _stable_component_seed(values: object) -> object:
    try:
        items = tuple(values)  # type: ignore[arg-type]
    except TypeError:
        return _stable_raw_seed(values)
    if all(
        isinstance(item, (tuple, list))
        and len(item) == 2
        and _is_int(item[0])
        and _is_int(item[1])
        for item in items
    ):
        return sorted([[int(item[0]), int(item[1])] for item in items])
    return _stable_raw_seed(items)


def _event_seed(event: TrackEvent) -> str:
    raw = {
        "frame": _stable_raw_seed(event.frame),
        "kind": _stable_raw_seed(event.kind),
        "resolved": _stable_raw_seed(event.resolved),
        "source_components": _stable_component_seed(event.source_components),
        "source_track_ids": _stable_id_seed(event.source_track_ids),
        "target_components": _stable_component_seed(event.target_components),
        "target_track_ids": _stable_id_seed(event.target_track_ids),
    }
    return hashlib.sha256(_canonical_json_bytes(raw)).hexdigest()


def _tracking_payload(
    tracks: Mapping[int, _TrackView],
    events: Sequence[_EventView],
    assignments: Sequence[tuple[int, int, int]],
    sampled_frames: Sequence[int],
) -> dict[str, object]:
    return {
        "sampled_frames": list(sampled_frames),
        "assignments": [list(item) for item in sorted(assignments)],
        "events": [item.payload() for item in sorted(events, key=lambda item: _canonical_json_bytes(item.payload()))],
        "tracks": [
            {
                "child_track_ids": list(track.children),
                "parent_track_ids": list(track.parents),
                "points": [list(point) for point in track.points],
                "track_id": track.track_id,
                "unresolved": track.unresolved,
            }
            for track in (tracks[track_id] for track_id in sorted(tracks))
        ],
    }


def _validate_event_shape(
    item: _EventView,
    violations: list[LifecycleViolation],
) -> None:
    sources = item.sources
    targets = item.targets
    source_components = item.source_components
    target_components = item.target_components
    expected_resolved = item.kind != "TRACKING_UNRESOLVED"
    if item.resolved is not expected_resolved:
        _add(
            violations,
            "INVALID_EVENT_RESOLUTION",
            f"{item.kind} resolved must be {expected_resolved}",
            frame=item.frame,
            event_id=item.event_id,
        )

    cardinality_ok = False
    polarity_ok = True
    if item.kind == "APPEARANCE":
        cardinality_ok = len(sources) == 0 and len(targets) == 1
    elif item.kind == "CONTINUATION":
        cardinality_ok = len(sources) == 1 and len(targets) == 1
        polarity_ok = cardinality_ok and sources == targets
    elif item.kind == "TEMPORARY_CONTACT":
        cardinality_ok = len(sources) == 2 and len(targets) == 2
        polarity_ok = cardinality_ok and sources == targets
    elif item.kind == "DISSOLUTION":
        cardinality_ok = len(sources) == 1 and len(targets) == 0
    elif item.kind == "SPLIT":
        cardinality_ok = len(sources) == 1 and len(targets) >= 2
        polarity_ok = cardinality_ok and set(sources).isdisjoint(targets)
    elif item.kind == "MERGE":
        cardinality_ok = len(sources) >= 2 and len(targets) == 1
        polarity_ok = cardinality_ok and set(sources).isdisjoint(targets)
    elif item.kind == "TRACKING_UNRESOLVED":
        cardinality_ok = len(sources) >= 1 and len(targets) >= 1
        polarity_ok = cardinality_ok and set(sources).isdisjoint(targets)

    if not cardinality_ok:
        _add(
            violations,
            "EVENT_CARDINALITY_MISMATCH",
            f"invalid source/target cardinality for {item.kind}",
            frame=item.frame,
            event_id=item.event_id,
        )
    if not polarity_ok:
        _add(
            violations,
            "EVENT_POLARITY_MISMATCH",
            f"invalid source/target polarity for {item.kind}",
            frame=item.frame,
            event_id=item.event_id,
        )
    if len(source_components) != len(sources) or len(target_components) != len(targets):
        _add(
            violations,
            "EVENT_CARDINALITY_MISMATCH",
            "component cardinalities do not match track cardinalities",
            frame=item.frame,
            event_id=item.event_id,
        )
    if item.kind == "TEMPORARY_CONTACT" and source_components != target_components:
        _add(
            violations,
            "EVENT_POLARITY_MISMATCH",
            "temporary contact must cite identical source and target components",
            frame=item.frame,
            event_id=item.event_id,
        )


def qualify_lifecycle_contract(
    tracking: TrackingResult,
    sampled_frames: Sequence[int],
) -> LifecycleRunClosure:
    """Return a total lifecycle closure or reject the complete tracker input.

    ``sampled_frames`` is an explicit ordered schedule.  The validator never
    assumes unit cadence and never invents a terminal state from absence.
    """

    violations: list[LifecycleViolation] = []
    try:
        raw_frames = tuple(sampled_frames)
    except TypeError:
        raw_frames = ()
    if not raw_frames:
        _add(violations, "EMPTY_SAMPLE_SCHEDULE", "sampled_frames must be non-empty")
        raise LifecycleContractError(violations)
    if any(not _is_int(frame) or int(frame) < 0 for frame in raw_frames):
        _add(
            violations,
            "INVALID_SAMPLE_FRAME",
            "every sampled frame must be a nonnegative integer",
        )
        raise LifecycleContractError(violations)
    frames = tuple(int(frame) for frame in raw_frames)
    if any(right <= left for left, right in zip(frames, frames[1:])):
        _add(
            violations,
            "NON_INCREASING_SAMPLE_SCHEDULE",
            "sampled_frames must be strictly increasing and unique",
        )
        raise LifecycleContractError(violations)
    frame_position = {frame: index for index, frame in enumerate(frames)}

    records_by_id: dict[int, list[TrackRecord]] = defaultdict(list)
    for record in tracking.tracks:
        if not _is_int(record.track_id) or int(record.track_id) < 0:
            _add(
                violations,
                "INVALID_TRACK_ID",
                f"invalid track ID {record.track_id!r}",
            )
            continue
        records_by_id[int(record.track_id)].append(record)

    tracks: dict[int, _TrackView] = {}
    component_claims: dict[tuple[int, int], list[int]] = defaultdict(list)
    for track_id in sorted(records_by_id):
        records = records_by_id[track_id]
        if len(records) != 1:
            _add(
                violations,
                "DUPLICATE_TRACK_ID",
                f"track ID appears {len(records)} times",
                track_id=track_id,
            )
            continue
        record = records[0]
        points: list[tuple[int, int]] = []
        for point in record.points:
            if (
                not _is_int(point.frame)
                or not _is_int(point.component_index)
                or int(point.component_index) < 0
            ):
                _add(violations, "INVALID_TRACK_POINT", "track point is not a valid frame/component pair", track_id=track_id)
                continue
            key = (int(point.frame), int(point.component_index))
            points.append(key)
            component_claims[key].append(track_id)
            if key[0] not in frame_position:
                _add(
                    violations,
                    "TRACK_POINT_OUTSIDE_SCHEDULE",
                    "track point frame is absent from sampled_frames",
                    track_id=track_id,
                    frame=key[0],
                )
        if not points:
            _add(violations, "EMPTY_TRACK", "every track must contain at least one point", track_id=track_id)
        elif all(frame in frame_position for frame, _ in points):
            positions = [frame_position[frame] for frame, _ in points]
            expected = list(range(positions[0], positions[0] + len(positions)))
            if positions != expected:
                _add(
                    violations,
                    "TRACK_POINT_GAP",
                    "track points must occupy consecutive positions in sampled_frames",
                    track_id=track_id,
                )

        parents = _normalize_id_tuple(
            record.parent_track_ids,
            field="parent_track_ids",
            violations=violations,
            track_id=track_id,
        )
        children = _normalize_id_tuple(
            record.child_track_ids,
            field="child_track_ids",
            violations=violations,
            track_id=track_id,
        )
        if parents is None:
            parents = ()
        if children is None:
            children = ()
        if track_id in parents or track_id in children:
            _add(violations, "SELF_LINEAGE_LINK", "a track cannot be its own parent or child", track_id=track_id)
        if not isinstance(record.unresolved, bool):
            _add(violations, "INVALID_UNRESOLVED_FLAG", "unresolved must be boolean", track_id=track_id)
        tracks[track_id] = _TrackView(
            record,
            track_id,
            tuple(points),
            parents,
            children,
            bool(record.unresolved),
        )

    for key in sorted(component_claims):
        claimants = tuple(sorted(component_claims[key]))
        if len(claimants) > 1:
            _add(
                violations,
                "DUPLICATE_COMPONENT_POINT",
                f"component key is claimed by track IDs {claimants}",
                track_id=min(claimants),
                frame=key[0],
            )

    known_ids = set(tracks)
    for track in tracks.values():
        for linked in track.parents + track.children:
            if linked not in known_ids:
                _add(
                    violations,
                    "UNKNOWN_LINEAGE_ID",
                    f"lineage link references unknown track {linked}",
                    track_id=track.track_id,
                )

    visit_state: dict[int, int] = {}

    def visit_lineage(track_id: int, path: tuple[int, ...]) -> None:
        state = visit_state.get(track_id, 0)
        if state == 2:
            return
        if state == 1:
            cycle = path[path.index(track_id) :] + (track_id,) if track_id in path else path + (track_id,)
            _add(
                violations,
                "CYCLIC_LINEAGE",
                f"lineage cycle detected: {cycle}",
                track_id=track_id,
            )
            return
        visit_state[track_id] = 1
        for child in tracks[track_id].children:
            if child in tracks:
                visit_lineage(child, path + (track_id,))
        visit_state[track_id] = 2

    for track_id in sorted(tracks):
        visit_lineage(track_id, ())

    assignments: list[tuple[int, int, int]] = []
    for raw in tracking.assignments:
        if (
            not isinstance(raw, (tuple, list))
            or len(raw) != 3
            or any(not _is_int(value) for value in raw)
            or int(raw[1]) < 0
            or int(raw[2]) < 0
        ):
            _add(violations, "INVALID_ASSIGNMENT", "assignment must be (frame, component, track_id)")
            continue
        assignment = (int(raw[0]), int(raw[1]), int(raw[2]))
        assignments.append(assignment)
        if assignment[0] not in frame_position or assignment[2] not in known_ids:
            _add(
                violations,
                "INVALID_ASSIGNMENT",
                "assignment frame and track ID must exist in the declared lifecycle input",
                track_id=assignment[2],
                frame=assignment[0],
            )
    assignment_counts = Counter(assignments)
    assignment_set = set(assignment_counts)
    for assignment in sorted(assignment_counts):
        count = assignment_counts[assignment]
        if count > 1:
            _add(
                violations,
                "DUPLICATE_ASSIGNMENT",
                f"assignment row occurs {count} times",
                track_id=assignment[2],
                frame=assignment[0],
            )

    assignment_claims: dict[tuple[int, int], set[int]] = defaultdict(set)
    for frame, component, track_id in assignment_set:
        assignment_claims[(frame, component)].add(track_id)
    assignment_owner: dict[tuple[int, int], int] = {}
    for key in sorted(assignment_claims):
        owners = tuple(sorted(assignment_claims[key]))
        if len(owners) > 1:
            _add(
                violations,
                "CONFLICTING_COMPONENT_ASSIGNMENT",
                f"component key is assigned to track IDs {owners}",
                frame=key[0],
            )
        else:
            assignment_owner[key] = owners[0]

    expected_assignments = {
        (frame, component, track.track_id)
        for track in tracks.values()
        for frame, component in track.points
    }
    if assignment_set != expected_assignments:
        missing = len(expected_assignments - assignment_set)
        extra = len(assignment_set - expected_assignments)
        _add(
            violations,
            "ASSIGNMENT_SET_MISMATCH",
            f"assignments differ from track points (missing={missing}, extra={extra})",
        )

    events: list[_EventView] = []
    event_payload_counts: Counter[bytes] = Counter()
    for event in tracking.events:
        seed = _event_seed(event)
        if not _is_int(event.frame) or int(event.frame) not in frame_position:
            _add(
                violations,
                "INVALID_EVENT_FRAME",
                "event frame is absent from sampled_frames",
                frame=int(event.frame) if _is_int(event.frame) else None,
                event_id=seed,
            )
            continue
        frame = int(event.frame)
        if not isinstance(event.kind, str) or event.kind not in _KNOWN_EVENT_KINDS:
            _add(
                violations,
                "UNKNOWN_EVENT_KIND",
                f"unsupported event kind {event.kind!r}",
                frame=frame,
                event_id=seed,
            )
            continue
        sources = _normalize_id_tuple(
            event.source_track_ids,
            field="source_track_ids",
            violations=violations,
            event_id=seed,
        )
        targets = _normalize_id_tuple(
            event.target_track_ids,
            field="target_track_ids",
            violations=violations,
            event_id=seed,
        )
        source_components = _normalize_component_tuple(
            event.source_components,
            field="source_components",
            violations=violations,
            event_id=seed,
        )
        target_components = _normalize_component_tuple(
            event.target_components,
            field="target_components",
            violations=violations,
            event_id=seed,
        )
        if not isinstance(event.resolved, bool):
            _add(
                violations,
                "INVALID_EVENT_RESOLUTION",
                "resolved must be boolean",
                frame=frame,
                event_id=seed,
            )
            continue
        if None in (sources, targets, source_components, target_components):
            continue
        normalized_payload = {
            "frame": frame,
            "kind": event.kind,
            "resolved": event.resolved,
            "source_components": [list(item) for item in source_components],
            "source_track_ids": list(sources),
            "target_components": [list(item) for item in target_components],
            "target_track_ids": list(targets),
        }
        event_id = _sha256(normalized_payload)
        view = _EventView(
            event,
            frame,
            event.kind,
            sources,
            source_components,
            target_components,
            targets,
            event.resolved,
            event_id,
        )
        events.append(view)
        payload_bytes = _canonical_json_bytes(normalized_payload)
        event_payload_counts[payload_bytes] += 1
        _validate_event_shape(view, violations)

        for track_id in sources + targets:
            if track_id not in known_ids:
                _add(
                    violations,
                    "UNKNOWN_LINEAGE_ID",
                    f"event references unknown track {track_id}",
                    track_id=track_id,
                    frame=frame,
                    event_id=event_id,
                )
        for key in source_components + target_components:
            if key not in assignment_owner:
                _add(
                    violations,
                    "EVENT_COMPONENT_UNASSIGNED",
                    f"event component {key} has no assignment",
                    frame=frame,
                    event_id=event_id,
                )
        mapped_sources = tuple(sorted(assignment_owner[key] for key in source_components if key in assignment_owner))
        mapped_targets = tuple(sorted(assignment_owner[key] for key in target_components if key in assignment_owner))
        if len(mapped_sources) == len(source_components) and mapped_sources != sources:
            _add(
                violations,
                "EVENT_COMPONENT_POLARITY_MISMATCH",
                "source components do not belong to source tracks",
                frame=frame,
                event_id=event_id,
            )
        if len(mapped_targets) == len(target_components) and mapped_targets != targets:
            _add(
                violations,
                "EVENT_COMPONENT_POLARITY_MISMATCH",
                "target components do not belong to target tracks",
                frame=frame,
                event_id=event_id,
            )
        if event.kind in _ONSET_EVENT_KINDS | {"CONTINUATION"}:
            if any(key[0] != frame for key in target_components):
                _add(
                    violations,
                    "EVENT_COMPONENT_FRAME_MISMATCH",
                    "target component frame must equal event frame",
                    frame=frame,
                    event_id=event_id,
                )
        if event.kind == "TEMPORARY_CONTACT" and any(key[0] != frame for key in source_components):
            _add(
                violations,
                "EVENT_COMPONENT_FRAME_MISMATCH",
                "temporary-contact components must equal event frame",
                frame=frame,
                event_id=event_id,
            )

    for payload, count in event_payload_counts.items():
        if count > 1:
            _add(
                violations,
                "DUPLICATE_EVENT",
                f"identical event occurs {count} times",
                event_id=hashlib.sha256(payload).hexdigest(),
            )

    onset_by_track: dict[int, list[_EventView]] = defaultdict(list)
    terminal_by_track: dict[int, list[_EventView]] = defaultdict(list)
    continuation_by_track: dict[int, list[_EventView]] = defaultdict(list)
    unresolved_witness: set[int] = set()
    events_by_track: dict[int, list[_EventView]] = defaultdict(list)
    for event in events:
        for track_id in set(event.sources + event.targets):
            events_by_track[track_id].append(event)
        if event.kind in _ONSET_EVENT_KINDS:
            for track_id in event.targets:
                onset_by_track[track_id].append(event)
        if event.kind in _TERMINAL_EVENT_STATES:
            for track_id in event.sources:
                terminal_by_track[track_id].append(event)
        if event.kind == "CONTINUATION" and len(event.sources) == 1:
            continuation_by_track[event.sources[0]].append(event)
        if event.kind == "TRACKING_UNRESOLVED":
            unresolved_witness.update(event.sources)
            unresolved_witness.update(event.targets)

    terminal_records: list[LifecycleTerminalRecord] = []
    final_frame = frames[-1]
    for track_id in sorted(tracks):
        track = tracks[track_id]
        if not track.points:
            continue
        first_key = track.points[0]
        last_key = track.points[-1]
        onsets = onset_by_track.get(track_id, [])
        if not onsets:
            _add(violations, "MISSING_ONSET_EVENT", "track has no onset event", track_id=track_id, frame=first_key[0])
        elif len(onsets) > 1:
            _add(
                violations,
                "MULTIPLE_ONSET_EVENTS",
                f"track has {len(onsets)} onset events",
                track_id=track_id,
                frame=first_key[0],
            )
        else:
            onset = onsets[0]
            expected_parents = () if onset.kind == "APPEARANCE" else onset.sources
            if onset.frame != first_key[0] or first_key not in onset.target_components:
                _add(
                    violations,
                    "EVENT_TEMPORAL_MISMATCH",
                    "onset event does not match the first track point",
                    track_id=track_id,
                    frame=onset.frame,
                    event_id=onset.event_id,
                )
            if track.parents != expected_parents:
                _add(
                    violations,
                    "PARENT_LINK_MISMATCH",
                    f"parents {track.parents} do not match onset sources {expected_parents}",
                    track_id=track_id,
                    frame=onset.frame,
                    event_id=onset.event_id,
                )

        expected_continuations = {
            (track.points[index - 1], track.points[index], track.points[index][0])
            for index in range(1, len(track.points))
        }
        actual_continuations: Counter[tuple[tuple[int, int], tuple[int, int], int]] = Counter()
        for continuation in continuation_by_track.get(track_id, []):
            if (
                len(continuation.sources) == 1
                and continuation.sources == continuation.targets
                and len(continuation.source_components) == 1
                and len(continuation.target_components) == 1
            ):
                key = (
                    continuation.source_components[0],
                    continuation.target_components[0],
                    continuation.frame,
                )
                actual_continuations[key] += 1
        for expected in sorted(expected_continuations):
            count = actual_continuations.get(expected, 0)
            if count == 0:
                _add(
                    violations,
                    "MISSING_CONTINUATION_EVENT",
                    f"missing continuation {expected[0]} -> {expected[1]}",
                    track_id=track_id,
                    frame=expected[2],
                )
            elif count > 1:
                _add(
                    violations,
                    "MULTIPLE_CONTINUATION_EVENTS",
                    f"continuation {expected[0]} -> {expected[1]} occurs {count} times",
                    track_id=track_id,
                    frame=expected[2],
                )
        for actual in sorted(set(actual_continuations) - expected_continuations):
            _add(
                violations,
                "UNEXPECTED_CONTINUATION_EVENT",
                f"unexpected continuation {actual[0]} -> {actual[1]}",
                track_id=track_id,
                frame=actual[2],
            )

        terminal_events = terminal_by_track.get(track_id, [])
        terminal_event: _EventView | None = None
        if len(terminal_events) > 1:
            _add(
                violations,
                "MULTIPLE_TERMINAL_EVENTS",
                f"track has {len(terminal_events)} terminal events",
                track_id=track_id,
            )
        elif terminal_events:
            terminal_event = terminal_events[0]

        if last_key[0] == final_frame:
            if terminal_event is not None:
                _add(
                    violations,
                    "TERMINAL_AT_HORIZON",
                    "a horizon-reaching track cannot also have a terminal event",
                    track_id=track_id,
                    frame=terminal_event.frame,
                    event_id=terminal_event.event_id,
                )
            expected_children: tuple[int, ...] = ()
            terminal_records.append(
                LifecycleTerminalRecord(
                    track_id,
                    first_key[0],
                    last_key[0],
                    last_key[1],
                    final_frame,
                    "RIGHT_CENSORED_AT_HORIZON",
                    "DECLARED_HORIZON",
                    None,
                    track.parents,
                    (),
                    "UNRESOLVED" if track.unresolved else "RESOLVED",
                )
            )
        elif terminal_event is None:
            expected_children = ()
            _add(
                violations,
                "SILENT_PRE_HORIZON_TERMINATION",
                "track ends before the horizon without an explicit terminal event",
                track_id=track_id,
                frame=last_key[0],
            )
        else:
            last_position = frame_position.get(last_key[0])
            expected_terminal_frame = (
                frames[last_position + 1]
                if last_position is not None and last_position + 1 < len(frames)
                else None
            )
            if (
                terminal_event.frame != expected_terminal_frame
                or last_key not in terminal_event.source_components
            ):
                _add(
                    violations,
                    "TERMINAL_FRAME_MISMATCH",
                    f"terminal event must consume the last point at next sampled frame {expected_terminal_frame}",
                    track_id=track_id,
                    frame=terminal_event.frame,
                    event_id=terminal_event.event_id,
                )
            expected_children = (
                terminal_event.targets
                if terminal_event.kind in {"SPLIT", "MERGE", "TRACKING_UNRESOLVED"}
                else ()
            )
            terminal_records.append(
                LifecycleTerminalRecord(
                    track_id,
                    first_key[0],
                    last_key[0],
                    last_key[1],
                    terminal_event.frame,
                    _TERMINAL_EVENT_STATES[terminal_event.kind],
                    "TRACK_EVENT",
                    terminal_event.event_id,
                    track.parents,
                    terminal_event.targets,
                    "UNRESOLVED" if track.unresolved else "RESOLVED",
                )
            )
        if track.children != expected_children:
            _add(
                violations,
                "CHILD_LINK_MISMATCH",
                f"children {track.children} do not match terminal successors {expected_children}",
                track_id=track_id,
            )
        if track.unresolved != (track_id in unresolved_witness):
            _add(
                violations,
                "UNRESOLVED_FLAG_MISMATCH",
                "unresolved flag must be backed exactly by an unresolved transition",
                track_id=track_id,
            )
        if terminal_event is not None:
            for event in events_by_track.get(track_id, []):
                if event.frame > terminal_event.frame:
                    _add(
                        violations,
                        "POST_TERMINAL_EVENT",
                        "track is referenced after its terminal event",
                        track_id=track_id,
                        frame=event.frame,
                        event_id=event.event_id,
                    )

    if len(terminal_records) != len(tracks):
        _add(
            violations,
            "TERMINAL_COUNT_MISMATCH",
            f"terminal rows {len(terminal_records)} do not equal tracks {len(tracks)}",
        )
    if violations:
        raise LifecycleContractError(violations)

    ordered_records = tuple(sorted(terminal_records, key=lambda item: item.track_id))
    records_payload = [item.as_dict() for item in ordered_records]
    source_payload = _tracking_payload(tracks, events, assignments, frames)
    return LifecycleRunClosure(
        sampled_frames=frames,
        lifecycle_input_digest_sha256=_sha256(source_payload),
        records_digest_sha256=_sha256(records_payload),
        track_count=len(tracks),
        event_count=len(events),
        assignment_count=len(assignments),
        terminal_records=ordered_records,
    )


def canonical_lifecycle_bytes(contract: LifecycleRunClosure) -> bytes:
    """Return the sole admitted byte representation of a qualified contract."""

    return _canonical_json_bytes(contract.as_dict())


def verify_lifecycle_document(
    data: bytes | str,
    tracking: TrackingResult,
    sampled_frames: Sequence[int],
) -> LifecycleRunClosure:
    """Recompute and byte-verify a persisted future lifecycle contract."""

    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    expected = qualify_lifecycle_contract(tracking, sampled_frames)
    expected_bytes = canonical_lifecycle_bytes(expected)
    try:
        observed = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleContractError(
            (LifecycleViolation("DOCUMENT_INVALID_JSON", f"invalid JSON document: {exc}"),)
        ) from exc
    if observed == expected.as_dict() and raw != expected_bytes:
        raise LifecycleContractError(
            (LifecycleViolation("DOCUMENT_NOT_CANONICAL", "JSON content matches but bytes are not canonical"),)
        )
    if observed != expected.as_dict():
        raise LifecycleContractError(
            (LifecycleViolation("DOCUMENT_BINDING_MISMATCH", "document does not match recomputed tracker binding"),)
        )
    return expected


def qualify_and_write_lifecycle_contract(
    path: str | os.PathLike[str],
    tracking: TrackingResult,
    sampled_frames: Sequence[int],
) -> LifecycleRunClosure:
    """Qualify first, then atomically create one non-overwriting contract file."""

    contract = qualify_lifecycle_contract(tracking, sampled_frames)
    target = Path(path)
    parent = target.parent
    if not parent.is_dir():
        raise LifecyclePublicationError("publication parent must already exist")
    if target.exists():
        raise LifecyclePublicationError("refusing to overwrite an existing lifecycle contract")
    payload = canonical_lifecycle_bytes(contract)
    descriptor, partial_name = tempfile.mkstemp(
        dir=parent,
        prefix=f".{target.name}.",
        suffix=".partial",
    )
    partial = Path(partial_name)
    owned_identity: tuple[int, int] | None = None
    target_linked = False

    def identity(stat_result: os.stat_result) -> tuple[int, int]:
        return (int(stat_result.st_dev), int(stat_result.st_ino))

    def unlink_if_owned(path_value: Path) -> None:
        if owned_identity is None:
            return
        try:
            current = os.stat(path_value, follow_symlinks=False)
        except FileNotFoundError:
            return
        if identity(current) == owned_identity:
            path_value.unlink()

    try:
        with os.fdopen(descriptor, "wb") as handle:
            owned_identity = identity(os.fstat(handle.fileno()))
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            # Creating a hard link is an atomic destination-absent operation
            # on the same filesystem.  The still-open descriptor and the
            # identity/byte checks below prevent a swapped partial path from
            # being accepted as this invocation's output.
            os.link(partial, target)
            target_linked = True
            with target.open("rb") as observed_handle:
                observed_identity = identity(os.fstat(observed_handle.fileno()))
                observed_payload = observed_handle.read()
            partial_identity = identity(os.stat(partial, follow_symlinks=False))
            if (
                observed_identity != owned_identity
                or partial_identity != owned_identity
                or observed_payload != payload
            ):
                raise LifecyclePublicationError(
                    "published lifecycle identity or canonical bytes changed during publication"
                )
        unlink_if_owned(partial)
    except FileExistsError as exc:
        unlink_if_owned(partial)
        raise LifecyclePublicationError(
            "refusing a concurrent lifecycle publication without overwriting it"
        ) from exc
    except BaseException:
        if target_linked:
            unlink_if_owned(target)
        unlink_if_owned(partial)
        raise
    return contract


__all__ = [
    "LifecycleContractError",
    "LifecyclePublicationError",
    "LifecycleRunClosure",
    "LifecycleTerminalRecord",
    "LifecycleViolation",
    "SCHEMA_VERSION",
    "VALIDATOR_VERSION",
    "canonical_lifecycle_bytes",
    "qualify_and_write_lifecycle_contract",
    "qualify_lifecycle_contract",
    "verify_lifecycle_document",
]
