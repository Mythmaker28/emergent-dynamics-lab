"""Passive Stage-B measurement stack for the lattice-bond substrate.

Nothing in this module is imported by :mod:`engine`.  Detection reads only the
instantaneous matter field.  Tracking reads only detector geometry and mass;
it never reads passive tracers, bond conductance, energetic throughput, future
regime labels, or intervention responses.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Iterable, Literal, Mapping, Sequence

import numpy as np

from .engine import LatticeBondSpec, LatticeBondState, StepLedger


EventKind = Literal[
    "APPEARANCE",
    "CONTINUATION",
    "SPLIT",
    "MERGE",
    "TEMPORARY_CONTACT",
    "DISSOLUTION",
    "TRACKING_UNRESOLVED",
]
Regime = Literal[
    "EMPTY_OR_GAS",
    "STATIC_CRYSTAL_OR_SHELL",
    "PERCOLATED",
    "DISSOLVED",
    "ACTIVE_UNBOUNDED",
    "PERSISTENT_NO_TURNOVER",
    "TURNOVER_WITHOUT_PERSISTENCE",
    "TRACKING_UNRESOLVED",
    "BOUNDED_ACTIVE_TURNOVER_CANDIDATE",
]


@dataclass(frozen=True)
class DetectorSpec:
    """Yield-independent instantaneous matter detector.

    ``b`` is deliberately absent: selecting components by the same structural
    conductance that a later experiment might manipulate would be circular.
    """

    matter_threshold: float = 0.45
    min_cells: int = 3

    def __post_init__(self) -> None:
        if not math.isfinite(self.matter_threshold) or self.matter_threshold <= 0.0:
            raise ValueError("matter_threshold must be finite and positive")
        if self.min_cells < 1:
            raise ValueError("min_cells must be positive")


@dataclass(frozen=True)
class DetectedComponent:
    frame: int
    index: int
    shape: tuple[int, int]
    cells: tuple[int, ...]
    area: int
    mass: float
    centroid_y: float
    centroid_x: float
    radius_gyration: float
    wraps_y: bool
    wraps_x: bool

    @property
    def percolates(self) -> bool:
        return self.wraps_y or self.wraps_x

    @property
    def key(self) -> tuple[int, int]:
        return (self.frame, self.index)

    def mask(self) -> np.ndarray:
        mask = np.zeros(self.shape[0] * self.shape[1], dtype=bool)
        mask[np.asarray(self.cells, dtype=np.int64)] = True
        return mask.reshape(self.shape)


def _neighbours(y: int, x: int, shape: tuple[int, int]) -> Iterable[tuple[int, int, int, int]]:
    h, w = shape
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        yield ((y + dy) % h, (x + dx) % w, dy, dx)


def detect_components(
    state: LatticeBondState,
    spec: DetectorSpec,
    *,
    frame: int | None = None,
) -> tuple[DetectedComponent, ...]:
    """Return deterministic periodic components without tracker state."""

    occupied = np.asarray(state.m >= spec.matter_threshold, dtype=bool)
    h, w = state.shape
    unseen = {int(v) for v in np.flatnonzero(occupied)}
    raw: list[tuple[tuple[int, ...], dict[int, tuple[int, int]], bool, bool]] = []
    while unseen:
        root = min(unseen)
        root_y, root_x = divmod(root, w)
        stack = [root]
        lifts: dict[int, tuple[int, int]] = {root: (root_y, root_x)}
        cells: set[int] = set()
        wraps_y = False
        wraps_x = False
        while stack:
            linear = stack.pop()
            if linear in cells:
                continue
            cells.add(linear)
            y, x = divmod(linear, w)
            ly, lx = lifts[linear]
            for ny, nx, dy, dx in _neighbours(y, x, state.shape):
                if not occupied[ny, nx]:
                    continue
                neighbour = ny * w + nx
                proposed = (ly + dy, lx + dx)
                if neighbour in lifts:
                    previous = lifts[neighbour]
                    wraps_y = wraps_y or previous[0] != proposed[0]
                    wraps_x = wraps_x or previous[1] != proposed[1]
                else:
                    lifts[neighbour] = proposed
                    stack.append(neighbour)
        unseen -= cells
        if len(cells) >= spec.min_cells:
            raw.append((tuple(sorted(cells)), lifts, wraps_y, wraps_x))

    raw.sort(key=lambda item: item[0][0])
    components: list[DetectedComponent] = []
    resolved_frame = int(state.step if frame is None else frame)
    for index, (cells, lifts, wraps_y, wraps_x) in enumerate(raw):
        lift_values = np.asarray([lifts[cell] for cell in cells], dtype=np.float64)
        weights = np.asarray([state.m[divmod(cell, w)] for cell in cells], dtype=np.float64)
        mass = math.fsum(float(value) for value in weights)
        if mass > 0.0:
            centre = np.sum(lift_values * weights[:, None], axis=0) / mass
            squared = np.sum((lift_values - centre[None, :]) ** 2, axis=1)
            radius = math.sqrt(float(np.sum(weights * squared) / mass))
        else:
            centre = np.mean(lift_values, axis=0)
            radius = 0.0
        components.append(
            DetectedComponent(
                frame=resolved_frame,
                index=index,
                shape=state.shape,
                cells=cells,
                area=len(cells),
                mass=mass,
                centroid_y=float(centre[0] % h),
                centroid_x=float(centre[1] % w),
                radius_gyration=radius,
                wraps_y=wraps_y,
                wraps_x=wraps_x,
            )
        )
    return tuple(components)


def _periodic_distance(a: DetectedComponent, b: DetectedComponent) -> float:
    h, w = a.shape
    dy = abs(a.centroid_y - b.centroid_y)
    dx = abs(a.centroid_x - b.centroid_x)
    return math.hypot(min(dy, h - dy), min(dx, w - dx))


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    result = mask.copy()
    frontier = mask.copy()
    for _ in range(radius):
        frontier = (
            np.roll(frontier, 1, axis=0)
            | np.roll(frontier, -1, axis=0)
            | np.roll(frontier, 1, axis=1)
            | np.roll(frontier, -1, axis=1)
        )
        result |= frontier
    return result


@dataclass(frozen=True)
class TrackerSpec:
    max_centroid_displacement: float = 3.0
    max_area_ratio: float = 3.0
    dilation_radius: int = 1
    unique_score_margin: float = 1e-12

    def __post_init__(self) -> None:
        if not math.isfinite(self.max_centroid_displacement) or self.max_centroid_displacement <= 0.0:
            raise ValueError("max_centroid_displacement must be finite and positive")
        if not math.isfinite(self.max_area_ratio) or self.max_area_ratio < 1.0:
            raise ValueError("max_area_ratio must be finite and >=1")
        if self.dilation_radius < 0:
            raise ValueError("dilation_radius must be nonnegative")
        if not math.isfinite(self.unique_score_margin) or self.unique_score_margin < 0.0:
            raise ValueError("unique_score_margin must be finite and nonnegative")


@dataclass(frozen=True)
class AssociationEdge:
    source: tuple[int, int]
    target: tuple[int, int]
    overlap_cells: int
    iou: float
    dilated_iou: float
    centroid_distance: float
    area_ratio: float
    score: float
    qualified: bool
    qualification_reason: str
    selected: bool
    selection_reason: str


def association_edge(a: DetectedComponent, b: DetectedComponent, spec: TrackerSpec) -> AssociationEdge:
    if a.shape != b.shape:
        raise ValueError("component shapes differ")
    am = a.mask()
    bm = b.mask()
    overlap = int(np.count_nonzero(am & bm))
    union = int(np.count_nonzero(am | bm))
    iou = overlap / union if union else 0.0
    ad = _dilate(am, spec.dilation_radius)
    bd = _dilate(bm, spec.dilation_radius)
    d_union = int(np.count_nonzero(ad | bd))
    d_iou = int(np.count_nonzero(ad & bd)) / d_union if d_union else 0.0
    distance = _periodic_distance(a, b)
    ratio = max(a.area, b.area) / min(a.area, b.area)
    size_similarity = min(a.area, b.area) / max(a.area, b.area)
    score = 4.0 * iou + 2.0 * d_iou + math.exp(-distance / spec.max_centroid_displacement) + size_similarity
    if ratio > spec.max_area_ratio:
        qualified = False
        qualification_reason = "REJECT_AREA_RATIO"
    elif distance > spec.max_centroid_displacement:
        qualified = False
        qualification_reason = "REJECT_CENTROID_DISTANCE"
    elif overlap == 0 and d_iou == 0.0:
        qualified = False
        qualification_reason = "REJECT_NO_GEOMETRIC_SUPPORT"
    else:
        qualified = True
        qualification_reason = "QUALIFIED_RAW_OVERLAP" if overlap > 0 else "QUALIFIED_DILATED_GEOMETRY"
    return AssociationEdge(
        a.key,
        b.key,
        overlap,
        iou,
        d_iou,
        distance,
        ratio,
        score,
        qualified,
        qualification_reason,
        False,
        "NOT_EVALUATED",
    )


@dataclass(frozen=True)
class TrackPoint:
    frame: int
    component_index: int


@dataclass(frozen=True)
class TrackRecord:
    track_id: int
    points: tuple[TrackPoint, ...]
    parent_track_ids: tuple[int, ...]
    child_track_ids: tuple[int, ...]
    unresolved: bool


@dataclass(frozen=True)
class TrackEvent:
    frame: int
    kind: EventKind
    source_track_ids: tuple[int, ...]
    source_components: tuple[tuple[int, int], ...]
    target_components: tuple[tuple[int, int], ...]
    target_track_ids: tuple[int, ...]
    resolved: bool


@dataclass(frozen=True)
class TrackingResult:
    tracks: tuple[TrackRecord, ...]
    events: tuple[TrackEvent, ...]
    edges: tuple[AssociationEdge, ...]
    assignments: tuple[tuple[int, int, int], ...]

    def track_for(self, frame: int, component_index: int) -> int | None:
        for item_frame, item_component, track_id in self.assignments:
            if item_frame == frame and item_component == component_index:
                return track_id
        return None


def _raw_graph_edges(
    sources: Sequence[DetectedComponent],
    targets: Sequence[DetectedComponent],
    spec: TrackerSpec,
) -> tuple[
    list[AssociationEdge],
    set[tuple[tuple[int, int], tuple[int, int]]],
    set[tuple[tuple[int, int], tuple[int, int]]],
]:
    all_edges = [association_edge(source, target, spec) for source in sources for target in targets]
    selected = {(edge.source, edge.target) for edge in all_edges if edge.qualified and edge.overlap_cells > 0}
    selection_reasons = {key: "SELECTED_RAW_OVERLAP" for key in selected}
    selected_sources = {source for source, _ in selected}
    selected_targets = {target for _, target in selected}

    candidates = [edge for edge in all_edges if edge.qualified and edge.source not in selected_sources and edge.target not in selected_targets]
    by_source: dict[tuple[int, int], list[AssociationEdge]] = {}
    by_target: dict[tuple[int, int], list[AssociationEdge]] = {}
    for edge in candidates:
        by_source.setdefault(edge.source, []).append(edge)
        by_target.setdefault(edge.target, []).append(edge)
    for values in by_source.values():
        values.sort(key=lambda edge: (-edge.score, edge.target))
    for values in by_target.values():
        values.sort(key=lambda edge: (-edge.score, edge.source))
    for edge in candidates:
        source_best = by_source[edge.source]
        target_best = by_target[edge.target]
        source_unique = len(source_best) == 1 or source_best[0].score - source_best[1].score > spec.unique_score_margin
        target_unique = len(target_best) == 1 or target_best[0].score - target_best[1].score > spec.unique_score_margin
        if source_unique and target_unique and source_best[0] == edge and target_best[0] == edge:
            key = (edge.source, edge.target)
            selected.add(key)
            selection_reasons[key] = "SELECTED_UNIQUE_MUTUAL_BEST"
    final_selected_sources = {source for source, _ in selected}
    final_selected_targets = {target for _, target in selected}
    ambiguous = {
        (edge.source, edge.target)
        for edge in candidates
        if (edge.source, edge.target) not in selected
        and edge.source not in final_selected_sources
        and edge.target not in final_selected_targets
    }
    annotated = []
    for edge in all_edges:
        key = (edge.source, edge.target)
        if key in selected:
            reason = selection_reasons[key]
        elif key in ambiguous:
            reason = "QUALIFIED_AMBIGUOUS_UNSELECTED"
        elif edge.qualified:
            reason = "QUALIFIED_NOT_SELECTED_LOWER_SCORE"
        else:
            reason = edge.qualification_reason
        annotated.append(replace(edge, selected=key in selected, selection_reason=reason))
    return annotated, selected, ambiguous


def _collapse_nodes(
    frames: Sequence[Sequence[DetectedComponent]],
    selected_by_transition: Sequence[set[tuple[tuple[int, int], tuple[int, int]]]],
) -> set[tuple[int, int]]:
    """Find many-to-one-to-many detector collapses that cannot carry identity."""

    collapses: set[tuple[int, int]] = set()
    for middle_frame in range(1, len(frames) - 1):
        incoming = selected_by_transition[middle_frame - 1]
        outgoing = selected_by_transition[middle_frame]
        for middle in frames[middle_frame]:
            previous = sorted(source for source, target in incoming if target == middle.key)
            following = sorted(target for source, target in outgoing if source == middle.key)
            if len(previous) >= 2 and len(following) >= 2:
                collapses.add(middle.key)
    return collapses


def _minimum_periodic_manhattan(a: DetectedComponent, b: DetectedComponent) -> int:
    h, w = a.shape
    best = h + w
    for a_cell in a.cells:
        ay, ax = divmod(a_cell, w)
        for b_cell in b.cells:
            by, bx = divmod(b_cell, w)
            dy = abs(ay - by)
            dx = abs(ax - bx)
            best = min(best, min(dy, h - dy) + min(dx, w - dx))
    return best


def _temporary_contact_pairs(components: Sequence[DetectedComponent]) -> tuple[tuple[DetectedComponent, DetectedComponent], ...]:
    """Return still-distinct components separated by exactly one empty cell."""

    pairs = []
    for left_index, left in enumerate(components):
        for right in components[left_index + 1 :]:
            if _minimum_periodic_manhattan(left, right) == 2:
                pairs.append((left, right))
    return tuple(pairs)


def track_components(
    frames: Sequence[Sequence[DetectedComponent]],
    spec: TrackerSpec,
) -> TrackingResult:
    """Track a complete sequence and log contact without merging identities."""

    if not frames:
        return TrackingResult((), (), (), ())
    all_edges: list[AssociationEdge] = []
    selected_by_transition: list[set[tuple[tuple[int, int], tuple[int, int]]]] = []
    ambiguous_by_transition: list[set[tuple[tuple[int, int], tuple[int, int]]]] = []
    for left, right in zip(frames[:-1], frames[1:], strict=True):
        edges, selected, ambiguous = _raw_graph_edges(left, right, spec)
        all_edges.extend(edges)
        selected_by_transition.append(selected)
        ambiguous_by_transition.append(ambiguous)
    collapse_nodes = _collapse_nodes(frames, selected_by_transition)

    next_track_id = 0
    points: dict[int, list[TrackPoint]] = {}
    parents: dict[int, set[int]] = {}
    children: dict[int, set[int]] = {}
    unresolved: dict[int, bool] = {}
    assignment: dict[tuple[int, int], int] = {}
    events: list[TrackEvent] = []

    def new_track(component: DetectedComponent, parent_ids: Iterable[int] = (), *, is_unresolved: bool = False) -> int:
        nonlocal next_track_id
        track_id = next_track_id
        next_track_id += 1
        points[track_id] = [TrackPoint(component.frame, component.index)]
        parents[track_id] = set(parent_ids)
        children[track_id] = set()
        unresolved[track_id] = is_unresolved
        assignment[component.key] = track_id
        for parent in parent_ids:
            children[parent].add(track_id)
        return track_id

    for component in frames[0]:
        track_id = new_track(component)
        events.append(TrackEvent(component.frame, "APPEARANCE", (), (), (component.key,), (track_id,), True))

    for transition_index, (left, right) in enumerate(zip(frames[:-1], frames[1:], strict=True)):
        right_frame = right[0].frame if right else transition_index + 1
        selected = selected_by_transition[transition_index]
        ambiguous = ambiguous_by_transition[transition_index]
        usable_left = list(left)
        usable_right = list(right)
        graph_edges = set(selected | ambiguous)
        source_targets = {component.key: sorted(target for source, target in graph_edges if source == component.key) for component in usable_left}
        target_sources = {component.key: sorted(source for source, target in graph_edges if target == component.key) for component in usable_right}

        visited_sources: set[tuple[int, int]] = set()
        visited_targets: set[tuple[int, int]] = set()
        for source_component in usable_left:
            source_key = source_component.key
            if source_key in visited_sources or not source_targets[source_key]:
                continue
            source_group = {source_key}
            target_group: set[tuple[int, int]] = set()
            frontier_sources = [source_key]
            while frontier_sources:
                source = frontier_sources.pop()
                for target in source_targets[source]:
                    if target in target_group:
                        continue
                    target_group.add(target)
                    for related_source in target_sources[target]:
                        if related_source not in source_group:
                            source_group.add(related_source)
                            frontier_sources.append(related_source)
            visited_sources.update(source_group)
            visited_targets.update(target_group)
            source_tracks = tuple(sorted(assignment[source] for source in source_group))
            target_objects = [next(component for component in usable_right if component.key == target) for target in sorted(target_group)]
            collapse_ambiguous = any(key in collapse_nodes for key in source_group | target_group)
            association_ambiguous = any(
                source in source_group and target in target_group for source, target in ambiguous
            )
            if len(source_group) == 1 and len(target_group) == 1 and not collapse_ambiguous and not association_ambiguous:
                track_id = source_tracks[0]
                target = target_objects[0]
                points[track_id].append(TrackPoint(target.frame, target.index))
                assignment[target.key] = track_id
                events.append(TrackEvent(target.frame, "CONTINUATION", source_tracks, tuple(source_group), (target.key,), (track_id,), True))
            elif len(source_group) == 1 and not collapse_ambiguous and not association_ambiguous:
                child_ids = tuple(new_track(target, source_tracks) for target in target_objects)
                events.append(TrackEvent(right_frame, "SPLIT", source_tracks, tuple(sorted(source_group)), tuple(sorted(target_group)), child_ids, True))
            elif len(target_group) == 1 and not collapse_ambiguous and not association_ambiguous:
                merged_id = new_track(target_objects[0], source_tracks)
                events.append(TrackEvent(right_frame, "MERGE", source_tracks, tuple(sorted(source_group)), tuple(sorted(target_group)), (merged_id,), True))
            else:
                new_ids = tuple(new_track(target, source_tracks, is_unresolved=True) for target in target_objects)
                for source_track in source_tracks:
                    unresolved[source_track] = True
                events.append(TrackEvent(right_frame, "TRACKING_UNRESOLVED", source_tracks, tuple(sorted(source_group)), tuple(sorted(target_group)), new_ids, False))

        for source_component in usable_left:
            if source_component.key not in visited_sources and not source_targets[source_component.key]:
                track_id = assignment[source_component.key]
                events.append(TrackEvent(right_frame, "DISSOLUTION", (track_id,), (source_component.key,), (), (), True))
        for target_component in usable_right:
            if target_component.key not in visited_targets and not target_sources[target_component.key]:
                track_id = new_track(target_component)
                events.append(TrackEvent(right_frame, "APPEARANCE", (), (), (target_component.key,), (track_id,), True))

        for left_component, right_component in _temporary_contact_pairs(right):
            left_track = assignment.get(left_component.key)
            right_track = assignment.get(right_component.key)
            if left_track is None or right_track is None or unresolved[left_track] or unresolved[right_track]:
                continue
            track_ids = tuple(sorted((left_track, right_track)))
            component_keys = tuple(sorted((left_component.key, right_component.key)))
            events.append(
                TrackEvent(
                    right_frame,
                    "TEMPORARY_CONTACT",
                    track_ids,
                    component_keys,
                    component_keys,
                    track_ids,
                    True,
                )
            )

    records = tuple(
        TrackRecord(
            track_id=track_id,
            points=tuple(points[track_id]),
            parent_track_ids=tuple(sorted(parents[track_id])),
            child_track_ids=tuple(sorted(children[track_id])),
            unresolved=unresolved[track_id],
        )
        for track_id in sorted(points)
    )
    assignments = tuple(sorted((frame, component, track_id) for (frame, component), track_id in assignment.items()))
    return TrackingResult(records, tuple(events), tuple(all_edges), assignments)


def advance_passive_tracer(
    tracer: np.ndarray,
    pre_matter: np.ndarray,
    matter_forward: np.ndarray,
    matter_reverse: np.ndarray,
    post_matter: np.ndarray,
    dt: float,
) -> np.ndarray:
    """Advect a labelled matter cohort through the existing gross flows."""

    for name, array in (
        ("tracer", tracer),
        ("pre_matter", pre_matter),
        ("post_matter", post_matter),
    ):
        if array.dtype != np.float64 or array.ndim != 2 or not np.isfinite(array).all():
            raise ValueError(f"{name} must be a finite float64 cell field")
    if tracer.shape != pre_matter.shape or post_matter.shape != pre_matter.shape:
        raise ValueError("tracer, pre_matter and post_matter must have the same shape")
    if not math.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    if matter_forward.shape != (2, *pre_matter.shape) or matter_reverse.shape != matter_forward.shape:
        raise ValueError("gross matter flows must have shape (2,H,W)")
    for name, flow in (("matter_forward", matter_forward), ("matter_reverse", matter_reverse)):
        if flow.dtype != np.float64 or not np.isfinite(flow).all() or float(np.min(flow)) < 0.0:
            raise ValueError(f"{name} must be finite nonnegative float64 gross flows")
    if float(np.min(pre_matter)) < 0.0 or float(np.min(post_matter)) < 0.0:
        raise ValueError("matter fields must be nonnegative")
    tolerance = 1e-12 + 1e-10 * max(1.0, float(np.max(pre_matter)), float(np.max(post_matter)))
    matter_net = matter_forward - matter_reverse
    matter_divergence = (matter_net[0] - np.roll(matter_net[0], 1, axis=0)) + (
        matter_net[1] - np.roll(matter_net[1], 1, axis=1)
    )
    expected_post = pre_matter - dt * matter_divergence
    if float(np.max(np.abs(expected_post - post_matter))) > tolerance:
        raise ValueError("pre/post matter is inconsistent with the supplied gross flows")
    if float(np.min(tracer)) < -tolerance or float(np.max(tracer - pre_matter)) > tolerance:
        raise ValueError("tracer must lie in [0,pre_matter]")
    fraction = np.divide(tracer, pre_matter, out=np.zeros_like(tracer), where=pre_matter > 0.0)
    tracer_flux = np.empty_like(matter_forward)
    for axis in (0, 1):
        fraction_plus = np.roll(fraction, -1, axis=axis)
        tracer_flux[axis] = matter_forward[axis] * fraction - matter_reverse[axis] * fraction_plus
    divergence = (tracer_flux[0] - np.roll(tracer_flux[0], 1, axis=0)) + (
        tracer_flux[1] - np.roll(tracer_flux[1], 1, axis=1)
    )
    result = tracer - dt * divergence
    if float(np.min(result)) < -tolerance or float(np.max(result - post_matter)) > tolerance:
        raise ArithmeticError("passive tracer left the transported matter domain")
    if abs(math.fsum(result.ravel()) - math.fsum(tracer.ravel())) > tolerance * tracer.size:
        raise ArithmeticError("passive tracer conservation failed")
    return result


@dataclass(frozen=True)
class ComponentDiagnostics:
    component_key: tuple[int, int]
    matter_internal_gross: float
    matter_in_gross: float
    matter_out_gross: float
    resource_boundary_exchange: float
    bond_work_throughput: float
    mean_internal_bond: float
    boundary_face_count: int

    @property
    def matter_boundary_gross(self) -> float:
        return self.matter_in_gross + self.matter_out_gross


def component_diagnostics(
    component: DetectedComponent,
    state: LatticeBondState,
    ledger: StepLedger,
    spec: LatticeBondSpec,
) -> ComponentDiagnostics:
    """Compute ordinary-flow diagnostics without changing state or ledger."""

    if state.shape != component.shape:
        raise ValueError("component and state shapes differ")
    mask = component.mask()
    internal = np.zeros_like(ledger.matter_natural, dtype=bool)
    boundary = np.zeros_like(internal)
    matter_in = 0.0
    matter_out = 0.0
    for axis in (0, 1):
        plus = np.roll(mask, -1, axis=axis)
        internal[axis] = mask & plus
        boundary[axis] = mask ^ plus
        source_inside = mask & ~plus
        target_inside = ~mask & plus
        matter_out += spec.dt * math.fsum(float(v) for v in ledger.matter_forward[axis][source_inside])
        matter_out += spec.dt * math.fsum(float(v) for v in ledger.matter_reverse[axis][target_inside])
        matter_in += spec.dt * math.fsum(float(v) for v in ledger.matter_reverse[axis][source_inside])
        matter_in += spec.dt * math.fsum(float(v) for v in ledger.matter_forward[axis][target_inside])
    gross_internal = spec.dt * math.fsum(
        float(value) for value in (ledger.matter_forward[internal] + ledger.matter_reverse[internal])
    )
    resource_exchange = spec.dt * math.fsum(float(value) for value in np.abs(ledger.resource_natural[boundary]))
    incident_weight = internal.astype(np.float64) + 0.5 * boundary.astype(np.float64)
    work_field = incident_weight * (ledger.gross_formation_work + ledger.gross_rupture_release)
    work = math.fsum(float(value) for value in work_field.ravel(order="C"))
    internal_count = int(np.count_nonzero(internal))
    mean_bond = math.fsum(float(value) for value in state.b[internal]) / internal_count if internal_count else 0.0
    return ComponentDiagnostics(
        component.key,
        gross_internal,
        matter_in,
        matter_out,
        resource_exchange,
        work,
        mean_bond if internal_count else 0.0,
        int(np.count_nonzero(boundary)),
    )


@dataclass(frozen=True)
class TrackMetrics:
    track_id: int
    observed_frames: int
    span_frames: int
    maximum_area_fraction: float
    bounded_fraction: float
    percolated_fraction: float
    mean_activity_per_mass: float
    mean_energy_throughput_per_mass: float
    maximum_turnover_fraction: float
    post_turnover_frames: int
    unresolved: bool
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class TrackObservation:
    track_id: int
    frame: int
    component_index: int
    area_fraction: float
    percolated: bool
    activity_per_mass: float
    energy_throughput_per_mass: float
    turnover_fraction: float


@dataclass(frozen=True)
class RegimeThresholds:
    min_persistence_frames: int
    max_area_fraction: float
    min_bounded_fraction: float
    min_activity_per_mass: float
    min_energy_throughput_per_mass: float
    min_turnover_fraction: float
    min_post_turnover_frames: int

    def __post_init__(self) -> None:
        if self.min_persistence_frames < 2 or self.min_post_turnover_frames < 1:
            raise ValueError("frame thresholds must be positive and nontrivial")
        for name in ("max_area_fraction", "min_bounded_fraction", "min_turnover_fraction"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0,1]")
        for name in ("min_activity_per_mass", "min_energy_throughput_per_mass"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class WorldMetrics:
    ever_detected: bool
    final_component_count: int
    any_percolated: bool
    any_active_unbounded: bool
    any_turnover_without_persistence: bool
    tracking_unresolved: bool
    tracks: tuple[TrackMetrics, ...]
    reason_codes: tuple[str, ...] = ()


def assemble_world_metrics(
    frames: Sequence[Sequence[DetectedComponent]],
    tracking: TrackingResult,
    observations: Sequence[TrackObservation],
    thresholds: RegimeThresholds,
) -> WorldMetrics:
    """Assemble raw observations into fail-closed auditable classifier inputs."""

    component_by_key: dict[tuple[int, int], DetectedComponent] = {}
    global_reasons: set[str] = set()
    for frame_components in frames:
        for component in frame_components:
            if component.key in component_by_key:
                global_reasons.add("DUPLICATE_DETECTED_COMPONENT")
            component_by_key[component.key] = component

    expected_observation_keys = {
        (track.track_id, point.frame, point.component_index)
        for track in tracking.tracks
        for point in track.points
    }
    observation_by_key: dict[tuple[int, int, int], TrackObservation] = {}
    for observation in observations:
        key = (observation.track_id, observation.frame, observation.component_index)
        if key in observation_by_key:
            global_reasons.add("DUPLICATE_TRACK_OBSERVATION")
        observation_by_key[key] = observation
        if key not in expected_observation_keys:
            global_reasons.add("ORPHAN_TRACK_OBSERVATION")

    integrity_reasons = {
        "MISSING_TRACK_OBSERVATION",
        "MISSING_DETECTED_COMPONENT",
        "NONFINITE_TRACK_OBSERVATION",
        "INVALID_AREA_FRACTION",
        "AREA_GEOMETRY_MISMATCH",
        "PERCOLATION_GEOMETRY_MISMATCH",
        "NEGATIVE_THROUGHPUT",
        "INVALID_TURNOVER_FRACTION",
    }

    metrics: list[TrackMetrics] = []
    for track in tracking.tracks:
        track_observations: list[TrackObservation] = []
        reasons: set[str] = set()
        for point in track.points:
            key = (track.track_id, point.frame, point.component_index)
            observation = observation_by_key.get(key)
            if observation is None:
                reasons.add("MISSING_TRACK_OBSERVATION")
                continue
            component = component_by_key.get((point.frame, point.component_index))
            if component is None:
                reasons.add("MISSING_DETECTED_COMPONENT")
                continue
            numeric = (
                observation.area_fraction,
                observation.activity_per_mass,
                observation.energy_throughput_per_mass,
                observation.turnover_fraction,
            )
            if not all(math.isfinite(value) for value in numeric):
                reasons.add("NONFINITE_TRACK_OBSERVATION")
                continue
            if not 0.0 <= observation.area_fraction <= 1.0:
                reasons.add("INVALID_AREA_FRACTION")
                continue
            expected_area_fraction = component.area / (component.shape[0] * component.shape[1])
            if observation.area_fraction != expected_area_fraction:
                reasons.add("AREA_GEOMETRY_MISMATCH")
                continue
            if observation.percolated != component.percolates:
                reasons.add("PERCOLATION_GEOMETRY_MISMATCH")
                continue
            if observation.activity_per_mass < 0.0 or observation.energy_throughput_per_mass < 0.0:
                reasons.add("NEGATIVE_THROUGHPUT")
                continue
            if not 0.0 <= observation.turnover_fraction <= 1.0:
                reasons.add("INVALID_TURNOVER_FRACTION")
                continue
            track_observations.append(observation)

        observed = len(track_observations)
        span = max((point.frame for point in track.points), default=0) - min(
            (point.frame for point in track.points), default=0
        ) + (1 if track.points else 0)
        if track_observations:
            maximum_area = max(item.area_fraction for item in track_observations)
            bounded_fraction = sum(
                not item.percolated and item.area_fraction <= thresholds.max_area_fraction
                for item in track_observations
            ) / observed
            percolated_fraction = sum(item.percolated for item in track_observations) / observed
            activity = math.fsum(item.activity_per_mass for item in track_observations) / observed
            energy = math.fsum(item.energy_throughput_per_mass for item in track_observations) / observed
            turnover = max(item.turnover_fraction for item in track_observations)
            turnover_frames = [item.frame for item in track_observations if item.turnover_fraction >= thresholds.min_turnover_fraction]
            first_turnover = min(turnover_frames) if turnover_frames else None
            post_turnover = sum(item.frame > first_turnover for item in track_observations) if first_turnover is not None else 0
        else:
            maximum_area = math.inf
            bounded_fraction = 0.0
            percolated_fraction = 0.0
            activity = 0.0
            energy = 0.0
            turnover = 0.0
            post_turnover = 0

        if observed < thresholds.min_persistence_frames:
            reasons.add("INSUFFICIENT_OBSERVED_FRAMES")
        if span < thresholds.min_persistence_frames:
            reasons.add("INSUFFICIENT_SPAN")
        if maximum_area > thresholds.max_area_fraction:
            reasons.add("AREA_EXCEEDS_MAX")
        if bounded_fraction < thresholds.min_bounded_fraction:
            reasons.add("INSUFFICIENT_BOUNDED_FRACTION")
        if activity < thresholds.min_activity_per_mass:
            reasons.add("INSUFFICIENT_ACTIVITY")
        if energy < thresholds.min_energy_throughput_per_mass:
            reasons.add("INSUFFICIENT_ENERGY_THROUGHPUT")
        if turnover < thresholds.min_turnover_fraction:
            reasons.add("INSUFFICIENT_TURNOVER")
        if post_turnover < thresholds.min_post_turnover_frames:
            reasons.add("INSUFFICIENT_POST_TURNOVER_SURVIVAL")
        if track.unresolved:
            reasons.add("TRACKING_UNRESOLVED")

        metrics.append(
            TrackMetrics(
                track.track_id,
                observed,
                span,
                maximum_area,
                bounded_fraction,
                percolated_fraction,
                activity,
                energy,
                turnover,
                post_turnover,
                track.unresolved or bool(reasons & integrity_reasons),
                tuple(sorted(reasons)),
            )
        )

    unresolved_events = any(not event.resolved or event.kind == "TRACKING_UNRESOLVED" for event in tracking.events)
    tracking_unresolved = unresolved_events or bool(global_reasons) or any(track.unresolved for track in metrics)
    any_percolated = any(track.percolated_fraction > 0.0 for track in metrics)
    any_active_unbounded = any(
        track.percolated_fraction > 0.0
        and track.mean_activity_per_mass >= thresholds.min_activity_per_mass
        and track.mean_energy_throughput_per_mass >= thresholds.min_energy_throughput_per_mass
        for track in metrics
    )
    any_turnover_without_persistence = any(
        track.maximum_turnover_fraction >= thresholds.min_turnover_fraction
        and (
            track.observed_frames < thresholds.min_persistence_frames
            or track.span_frames < thresholds.min_persistence_frames
        )
        for track in metrics
    )
    return WorldMetrics(
        ever_detected=any(bool(frame) for frame in frames),
        final_component_count=len(frames[-1]) if frames else 0,
        any_percolated=any_percolated,
        any_active_unbounded=any_active_unbounded,
        any_turnover_without_persistence=any_turnover_without_persistence,
        tracking_unresolved=tracking_unresolved,
        tracks=tuple(metrics),
        reason_codes=tuple(sorted(global_reasons)),
    )


def classify_regime(metrics: WorldMetrics, thresholds: RegimeThresholds) -> Regime:
    """Deterministic, saturated and order-fixed Stage-B regime classifier."""

    if metrics.tracking_unresolved or any(track.unresolved for track in metrics.tracks):
        return "TRACKING_UNRESOLVED"
    if metrics.any_active_unbounded:
        return "ACTIVE_UNBOUNDED"
    if metrics.any_percolated:
        return "PERCOLATED"
    if not metrics.ever_detected:
        return "EMPTY_OR_GAS"
    if metrics.final_component_count == 0:
        return "DISSOLVED"

    persistent = [
        track
        for track in metrics.tracks
        if track.observed_frames >= thresholds.min_persistence_frames
        and track.span_frames >= thresholds.min_persistence_frames
    ]
    candidates = [
        track
        for track in persistent
        if track.maximum_area_fraction <= thresholds.max_area_fraction
        and track.bounded_fraction >= thresholds.min_bounded_fraction
        and track.percolated_fraction == 0.0
        and track.mean_activity_per_mass >= thresholds.min_activity_per_mass
        and track.mean_energy_throughput_per_mass >= thresholds.min_energy_throughput_per_mass
        and track.maximum_turnover_fraction >= thresholds.min_turnover_fraction
        and track.post_turnover_frames >= thresholds.min_post_turnover_frames
    ]
    if candidates:
        return "BOUNDED_ACTIVE_TURNOVER_CANDIDATE"
    if persistent:
        active = any(
            track.mean_activity_per_mass >= thresholds.min_activity_per_mass
            and track.mean_energy_throughput_per_mass >= thresholds.min_energy_throughput_per_mass
            for track in persistent
        )
        turnover = any(track.maximum_turnover_fraction >= thresholds.min_turnover_fraction for track in persistent)
        if active and not turnover:
            return "PERSISTENT_NO_TURNOVER"
        return "STATIC_CRYSTAL_OR_SHELL"
    if metrics.any_turnover_without_persistence:
        return "TURNOVER_WITHOUT_PERSISTENCE"
    return "DISSOLVED"


def state_sequence_bytes(states: Sequence[LatticeBondState]) -> bytes:
    """Stable helper used by passivity fixtures."""

    return b"".join(state.canonical_bytes() for state in states)


def assignments_by_key(result: TrackingResult) -> Mapping[tuple[int, int], int]:
    return {(frame, component): track_id for frame, component, track_id in result.assignments}
