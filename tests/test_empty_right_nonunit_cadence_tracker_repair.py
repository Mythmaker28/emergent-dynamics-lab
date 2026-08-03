"""EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00 — qualification suite.

Synthetic detector frames only.  No engine, no seed, no scientific material, no
historical family.  Every fixture is a handcrafted boolean mask pushed through the
real detector so that the tracker is exercised on genuine ``DetectedComponent``
values rather than on hand-built stand-ins.

The defect under repair: ``track_components`` resolved the right observed frame of
a transition as ``transition_index + 1`` whenever the right detector frame was
empty.  Under non-unit or irregular cadence that fabricates a frame number that is
not on the declared sampling schedule, so ``qualify_lifecycle_contract`` raises
``INVALID_EVENT_FRAME`` and the *whole run* is rejected.  Because only runs in
which something disappeared could take that path, the rejection was correlated with
the outcome: a survivorship trapdoor.  The repair made the declared schedule
authoritative for the right frame of every transition.

MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01R extends the repair from
*available* to *mandatory*.  ``sampled_frames`` is now keyword-only, has no default
and is non-optional, so the schedule-free call path that carried the defect no
longer exists.  Every test below that previously compared the repaired path against
the legacy path has been restated: the legacy path cannot be invoked, and the
lifecycle guard that caught it is shown to be live — but now unreachable from
tracker output — using a HANDCRAFTED ``TrackingResult``, never the tracker.
"""

from __future__ import annotations

import inspect
import itertools

import numpy as np
import pytest

from edlab.substrates.lattice_bond import (
    DetectorSpec,
    LatticeBondState,
    TrackerSpec,
    detect_components,
    track_components,
)
from edlab.substrates.lattice_bond import instrumentation
from edlab.substrates.lattice_bond.instrumentation import TrackEvent, TrackingResult
from edlab.substrates.lattice_bond.lifecycle import (
    LifecycleContractError,
    qualify_lifecycle_contract,
)


SHAPE = (10, 12)
DETECTOR = DetectorSpec(matter_threshold=0.5, min_cells=1)
TRACKER = TrackerSpec(max_centroid_displacement=3.0, max_area_ratio=4.0, dilation_radius=1)


# --------------------------------------------------------------------------
# synthetic fixture builders
# --------------------------------------------------------------------------


def _mask(cells: set[tuple[int, int]], shape: tuple[int, int] = SHAPE) -> np.ndarray:
    value = np.zeros(shape, dtype=bool)
    for y, x in cells:
        value[y % shape[0], x % shape[1]] = True
    return value


EMPTY = np.zeros(SHAPE, dtype=bool)
BLOB_A = _mask({(3, 3), (3, 4), (4, 3), (4, 4)})
BLOB_B = _mask({(8, 9), (8, 10), (9, 9), (9, 10)})
JOINED = _mask({(4, x) for x in range(3, 8)})
SPLIT = _mask({(4, 3), (4, 4), (4, 6), (4, 7)})


def _state(mask: np.ndarray, frame: int) -> LatticeBondState:
    m = np.where(mask, 0.8, 0.1).astype(np.float64)
    n = np.full(mask.shape, 0.8, dtype=np.float64)
    b = np.zeros((2, *mask.shape), dtype=np.float64)
    return LatticeBondState(m, n, b, frame)


def _observed(schedule, *masks):
    """Detector output stamped with the ACTUAL sampled frame numbers."""

    assert len(schedule) == len(masks), "fixture schedule/mask length disagreement"
    return tuple(
        detect_components(_state(mask, int(frame)), DETECTOR, frame=int(frame))
        for frame, mask in zip(schedule, masks)
    )


def _tracked(schedule, *masks) -> TrackingResult:
    return track_components(_observed(schedule, *masks), TRACKER, sampled_frames=schedule)


def _offschedule_surrogate(schedule, *masks) -> TrackingResult:
    """Handcrafted stand-in for the DELETED schedule-free path.

    The tracker can no longer produce this.  It is rebuilt by hand, from real
    tracker output, by rewriting every event frame that the deleted fallback would
    have fabricated (``transition_index + 1``) back onto the events.  It exists only
    so that the lifecycle guard which used to catch the defect can be shown to be
    live rather than dead code.
    """

    honest = track_components(_observed(schedule, *masks), TRACKER, sampled_frames=schedule)
    position = {int(frame): index for index, frame in enumerate(schedule)}
    surrogate = tuple(
        event if event.frame == schedule[0] else _replace_frame(event, position[int(event.frame)])
        for event in honest.events
    )
    return TrackingResult(honest.tracks, surrogate, honest.edges, honest.assignments)


def _replace_frame(event, fabricated_frame: int):
    return TrackEvent(
        fabricated_frame,
        event.kind,
        event.source_track_ids,
        event.source_components,
        event.target_components,
        event.target_track_ids,
        event.resolved,
    )


def _kinds(result) -> list[str]:
    return [event.kind for event in result.events]


def _frames_of(result, kind) -> list[int]:
    return sorted(event.frame for event in result.events if event.kind == kind)


def _violations(result, schedule) -> list[str] | None:
    try:
        qualify_lifecycle_contract(result, tuple(schedule))
    except LifecycleContractError as exc:
        return sorted({item.code for item in exc.violations})
    return None


def _terminals(result, schedule):
    contract = qualify_lifecycle_contract(result, tuple(schedule))
    return {
        record.track_id: (record.terminal_state, record.terminal_frame, record.evidence_kind)
        for record in contract.terminal_records
    }


# --------------------------------------------------------------------------
# 1-5: cadence coverage
# --------------------------------------------------------------------------


def test_01_empty_right_frame_at_unit_cadence_is_unchanged():
    """Unit cadence: the mandatory schedule reproduces the frozen accepted behaviour.

    01R: the legacy comparand is gone with the schedule-free path, so the frozen
    values are asserted directly instead of against a second call.
    """

    schedule = (0, 1)
    repaired = _tracked(schedule, BLOB_A, EMPTY)
    assert _kinds(repaired) == ["APPEARANCE", "DISSOLUTION"]
    assert _frames_of(repaired, "DISSOLUTION") == [1]
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0][:2] == ("DISSOLVED_DETECTED_TRACK", 1)


def test_02_empty_right_frame_at_nonunit_cadence_binds_the_actual_frame():
    """The defect and its repair, side by side, on identical detector input."""

    schedule = (0, 5)
    observed = _observed(schedule, BLOB_A, EMPTY)

    # 01R: the defective call can no longer be made at all.
    with pytest.raises(TypeError):
        track_components(observed, TRACKER)

    # The frame the deleted fallback would have fabricated, rebuilt by hand, is still
    # caught by the lifecycle contract with the identical violation triple: the guard
    # is live, and it is now simply unreachable from tracker output.
    surrogate = _offschedule_surrogate(schedule, BLOB_A, EMPTY)
    assert _frames_of(surrogate, "DISSOLUTION") == [1], "surrogate fabricated frame must be 1"
    assert _violations(surrogate, schedule) == [
        "INVALID_EVENT_FRAME",
        "SILENT_PRE_HORIZON_TERMINATION",
        "TERMINAL_COUNT_MISMATCH",
    ]

    repaired = track_components(observed, TRACKER, sampled_frames=schedule)
    assert _frames_of(repaired, "DISSOLUTION") == [5]
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0][:2] == ("DISSOLVED_DETECTED_TRACK", 5)


def test_03_irregular_cadence_binds_each_transition_independently():
    """Gaps of 5, 6, 1 and 28.  ``i+1``, ``left+1`` and the true right frame all differ."""

    schedule = (0, 5, 11, 12, 40)
    repaired = _tracked(schedule, BLOB_A, EMPTY, BLOB_B, BLOB_B, BLOB_B)
    assert _frames_of(repaired, "DISSOLUTION") == [5]
    # the fabricated positional value (1) and the left+1 value (1) are both absent
    assert 1 not in {event.frame for event in repaired.events}
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert terminals[0][:2] == ("DISSOLVED_DETECTED_TRACK", 5)
    assert terminals[1][:2] == ("RIGHT_CENSORED_AT_HORIZON", 40)


def test_04_nonzero_schedule_origin_is_not_treated_as_an_offset():
    """Origin 7: a unit-cadence-only rule would emit 8, and left+1 would emit 8 too."""

    schedule = (7, 19)
    repaired = _tracked(schedule, BLOB_A, EMPTY)
    assert _frames_of(repaired, "DISSOLUTION") == [19]
    assert 8 not in {event.frame for event in repaired.events}
    assert 1 not in {event.frame for event in repaired.events}
    assert _violations(repaired, schedule) is None


def test_05_very_large_frame_numbers_are_carried_exactly():
    schedule = (10**12, 10**12 + 7, 10**12 + 1000)
    repaired = _tracked(schedule, BLOB_A, EMPTY, BLOB_B)
    assert _frames_of(repaired, "DISSOLUTION") == [10**12 + 7]
    assert all(isinstance(event.frame, int) for event in repaired.events)
    assert _violations(repaired, schedule) is None


# --------------------------------------------------------------------------
# 6-9: multiplicity, survival, ordering, final transition
# --------------------------------------------------------------------------


def test_06_several_left_entities_all_close_at_the_empty_right_frame():
    """A mutant that closes only the first disappearing track cannot pass this."""

    schedule = (0, 5)
    both = BLOB_A | BLOB_B
    repaired = _tracked(schedule, both, EMPTY)
    assert len(repaired.tracks) == 2
    assert _frames_of(repaired, "DISSOLUTION") == [5, 5]
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert set(terminals) == {0, 1}
    assert all(value[:2] == ("DISSOLVED_DETECTED_TRACK", 5) for value in terminals.values())


def test_07_one_track_disappears_while_another_survives():
    """Disappearance and survival must be distinguishable, and both must qualify.

    Recorded honestly: the right detector frame here is *not* empty (the survivor is
    in it), so ``right[0].frame`` already yields the correct number and this case
    passes on the defective parent too.  It is kept because it pins the mixed-fate
    accounting, and its passing on the parent is itself informative — the defect is
    specific to a **totally** empty right detector frame.  The empty-right analogue
    is :func:`test_s2_a_disappearing_track_stays_in_the_enrolled_denominator`.
    """

    schedule = (0, 5, 11)
    both = BLOB_A | BLOB_B
    repaired = _tracked(schedule, both, BLOB_B, BLOB_B)
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert len(terminals) == len(repaired.tracks) == 2
    states = {value[:2] for value in terminals.values()}
    assert states == {("DISSOLVED_DETECTED_TRACK", 5), ("RIGHT_CENSORED_AT_HORIZON", 11)}
    kinds = {value[2] for value in terminals.values()}
    assert kinds == {"TRACK_EVENT", "DECLARED_HORIZON"}


def test_08_disappearance_followed_by_later_empty_observations():
    """The terminal frame is the transition's right frame, never the run horizon."""

    schedule = (0, 5, 11, 40)
    repaired = _tracked(schedule, BLOB_A, EMPTY, EMPTY, EMPTY)
    assert _frames_of(repaired, "DISSOLUTION") == [5]
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0][:2] == ("DISSOLVED_DETECTED_TRACK", 5)


def test_09_disappearance_at_the_final_sampled_transition():
    """The track's last point is at ``schedule[-2]``; the empty frame is the horizon.

    The *track* never reached the horizon, so this is a pre-horizon terminal event
    by the contract's definition and ``TERMINAL_AT_HORIZON`` must not fire.
    """

    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A, BLOB_A, EMPTY)
    assert _frames_of(repaired, "DISSOLUTION") == [11]
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0][:2] == ("DISSOLVED_DETECTED_TRACK", 11)


# --------------------------------------------------------------------------
# 10-11: lineage events immediately before an empty frame
# --------------------------------------------------------------------------


def test_10_split_immediately_before_a_later_empty_frame():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, JOINED, SPLIT, EMPTY)
    split_events = [event for event in repaired.events if event.kind == "SPLIT"]
    assert len(split_events) == 1
    assert split_events[0].frame == 5
    assert _frames_of(repaired, "DISSOLUTION") == [11, 11]
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert terminals[0][0] == "SPLIT_INTO_TRACKS" and terminals[0][1] == 5
    children = {key: value for key, value in terminals.items() if key != 0}
    assert all(value[:2] == ("DISSOLVED_DETECTED_TRACK", 11) for value in children.values())


def test_11_merge_immediately_before_a_later_empty_frame():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, SPLIT, JOINED, EMPTY)
    merge_events = [event for event in repaired.events if event.kind == "MERGE"]
    assert len(merge_events) == 1
    assert merge_events[0].frame == 5
    assert _frames_of(repaired, "DISSOLUTION") == [11]
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    merged = merge_events[0].target_track_ids[0]
    assert terminals[merged][:2] == ("DISSOLVED_DETECTED_TRACK", 11)
    for parent in merge_events[0].source_track_ids:
        assert terminals[parent][:2] == ("MERGED_INTO_TRACK", 5)


# --------------------------------------------------------------------------
# 12-15: schedule validation, membership, determinism, compatibility
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "schedule, reason",
    [
        ((0,), "too short"),
        ((0, 1, 2), "too long"),
        ((0, 0), "not strictly increasing"),
        ((5, 0), "decreasing"),
        ((-1, 5), "negative"),
        ((0, 5.0), "non-integer"),
        ((0, True), "bool is not an admissible frame index"),
        ((0, "5"), "string"),
    ],
)
def test_12_malformed_schedules_are_rejected_never_silently_repaired(schedule, reason):
    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(ValueError):
        track_components(observed, TRACKER, sampled_frames=schedule)


@pytest.mark.parametrize(
    "schedule, reason",
    [
        ((0, 5, 3), "third entry decreases: only the first adjacent pair increases"),
        ((0, 5, 5), "third entry repeats: only the first adjacent pair increases"),
        ((0, 0, 5), "first adjacent pair repeats"),
        ((5, 0, 11), "first adjacent pair decreases"),
    ],
)
def test_12c_monotonicity_is_checked_on_every_adjacent_pair(schedule, reason):
    """Reviewer A, OBS-1: every previous ordering case was a two-entry schedule, so a
    mutant that scanned only the first adjacent pair survived."""

    observed = _observed((0, 5, 11), BLOB_A, EMPTY, BLOB_B)
    with pytest.raises(ValueError, match="strictly increasing"):
        track_components(observed, TRACKER, sampled_frames=schedule)


def test_12d_a_unit_cadence_schedule_contradicting_the_detector_is_rejected():
    """Reviewer A, OBS-2: every previous contradiction case was non-unit, wrong-length
    or non-monotone, so a mutant that skipped the cross-check for contiguous unit
    cadence survived and let an off-schedule CONTINUATION frame through."""

    observed = _observed((0, 7), BLOB_A, BLOB_A)
    with pytest.raises(ValueError, match="disagree with an observed detector frame"):
        track_components(observed, TRACKER, sampled_frames=(0, 1))


def test_12e_a_mapping_is_not_accepted_as_a_schedule():
    """Reviewer A, NIT-8: the stated rule is 'ordered sequence only'."""

    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(ValueError, match="ordered sequence"):
        track_components(observed, TRACKER, sampled_frames={0: "a", 5: "b"})


def test_12b_a_schedule_contradicting_an_observed_frame_is_rejected():
    """The declared schedule may not disagree with a detector frame it is describing."""

    observed = _observed((0, 5), BLOB_A, BLOB_B)
    with pytest.raises(ValueError):
        track_components(observed, TRACKER, sampled_frames=(0, 6))


@pytest.mark.parametrize(
    "schedule, masks",
    [
        ((0, 1), (BLOB_A, EMPTY)),
        ((0, 5), (BLOB_A, EMPTY)),
        ((0, 5, 11, 12, 40), (BLOB_A, EMPTY, BLOB_B, BLOB_B, BLOB_B)),
        ((7, 19), (BLOB_A, EMPTY)),
        ((0, 5, 11), (JOINED, SPLIT, EMPTY)),
        ((0, 5, 11), (SPLIT, JOINED, EMPTY)),
        ((0, 5, 11, 40), (BLOB_A, EMPTY, EMPTY, EMPTY)),
    ],
)
def test_13_every_event_frame_belongs_to_the_declared_schedule(schedule, masks):
    repaired = _tracked(schedule, *masks)
    assert repaired.events, "fixture must produce at least one event"
    assert {event.frame for event in repaired.events} <= set(schedule)


def test_14_repaired_tracking_is_deterministic_and_canonically_ordered():
    schedule = (0, 5, 11, 12, 40)
    masks = (BLOB_A | BLOB_B, BLOB_B, EMPTY, BLOB_A, BLOB_A)
    first = _tracked(schedule, *masks)
    second = _tracked(schedule, *masks)
    assert first == second
    frames = [event.frame for event in first.events]
    assert frames == sorted(frames)
    contract_a = qualify_lifecycle_contract(first, schedule)
    contract_b = qualify_lifecycle_contract(second, schedule)
    assert contract_a.records_digest_sha256 == contract_b.records_digest_sha256
    ids = [record.track_id for record in contract_a.terminal_records]
    assert ids == sorted(ids)


@pytest.mark.parametrize(
    "masks",
    [
        (BLOB_A, EMPTY),
        (EMPTY, BLOB_A, EMPTY),
        (JOINED, SPLIT),
        (SPLIT, JOINED),
        (BLOB_A | BLOB_B, BLOB_B),
        (BLOB_A, BLOB_A, BLOB_A),
    ],
)
def test_15_unit_cadence_output_is_deterministic_and_on_schedule(masks):
    """01R: the with/without comparison is gone; the invariant it protected is not.

    At unit cadence every event frame is on the declared schedule and the result is
    reproducible call to call.
    """

    schedule = (0, 1) if len(masks) == 2 else (0, 1, 2)
    observed = _observed(schedule, *masks)
    first = track_components(observed, TRACKER, sampled_frames=schedule)
    second = track_components(observed, TRACKER, sampled_frames=schedule)
    assert first == second
    assert {event.frame for event in first.events} <= set(schedule)
    assert _violations(first, schedule) is None


def test_15b_the_schedule_free_call_path_no_longer_exists():
    """01R: the accepted-parent call path is deleted, not merely discouraged."""

    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(TypeError):
        track_components(observed, TRACKER)
    with pytest.raises(ValueError):
        track_components(observed, TRACKER, sampled_frames=None)


# --------------------------------------------------------------------------
# horizon semantics: the four frozen cases, separately demonstrated
# --------------------------------------------------------------------------


def test_h1_pre_horizon_terminal_event_with_a_later_declared_observation():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A, EMPTY, BLOB_B)
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert terminals[0] == ("DISSOLVED_DETECTED_TRACK", 5, "TRACK_EVENT")
    assert terminals[1] == ("RIGHT_CENSORED_AT_HORIZON", 11, "DECLARED_HORIZON")


def test_h2_disappearance_first_detected_at_the_horizon_is_still_pre_horizon():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A, BLOB_A, EMPTY)
    codes = _violations(repaired, schedule)
    assert codes is None, f"TERMINAL_AT_HORIZON must not fire here, got {codes}"
    assert _terminals(repaired, schedule)[0] == ("DISSOLVED_DETECTED_TRACK", 11, "TRACK_EVENT")


def test_h3_a_track_observed_at_the_horizon_is_censored_not_terminated():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A, BLOB_A, BLOB_A)
    assert "DISSOLUTION" not in _kinds(repaired)
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0] == ("RIGHT_CENSORED_AT_HORIZON", 11, "DECLARED_HORIZON")


def test_h4_a_pre_horizon_end_without_a_terminal_event_remains_a_violation():
    """The repair must not weaken the rule it is exercising."""

    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A, EMPTY, BLOB_B)
    stripped = TrackingResult(
        repaired.tracks,
        tuple(event for event in repaired.events if event.kind != "DISSOLUTION"),
        repaired.edges,
        repaired.assignments,
    )
    codes = _violations(stripped, schedule)
    assert codes is not None and "SILENT_PRE_HORIZON_TERMINATION" in codes


# --------------------------------------------------------------------------
# survivorship: the property the whole mission exists to establish
# --------------------------------------------------------------------------


def test_s1_disappearance_is_no_longer_correlated_with_global_rejection():
    """Identical cadence, identical spec: the dissolving run and the surviving run
    both qualify.  On the accepted parent only the surviving run qualified."""

    schedule = (0, 5, 11)
    dissolving = _tracked(schedule, BLOB_A, EMPTY, BLOB_B)
    surviving = _tracked(schedule, BLOB_A, BLOB_A, BLOB_A)
    assert _violations(dissolving, schedule) is None
    assert _violations(surviving, schedule) is None

    # the accepted parent, reconstructed by hand: the surviving run qualified, the
    # dissolving run did not.  Neither is reachable from the tracker any more.
    surrogate_dissolving = _offschedule_surrogate(schedule, BLOB_A, EMPTY, BLOB_B)
    surrogate_codes = _violations(surrogate_dissolving, schedule)
    assert surrogate_codes is not None and "INVALID_EVENT_FRAME" in surrogate_codes


def test_s2_a_disappearing_track_stays_in_the_enrolled_denominator():
    """Empty right detector frame: the tracks that vanish are counted, not dropped."""

    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A | BLOB_B, EMPTY, BLOB_B)
    assert (
        _violations(_offschedule_surrogate(schedule, BLOB_A | BLOB_B, EMPTY, BLOB_B), schedule)
        is not None
    )
    contract = qualify_lifecycle_contract(repaired, schedule)
    assert contract.track_count == len(repaired.tracks) == 3
    assert len(contract.terminal_records) == contract.track_count
    assert contract.run_terminal_state == "ALL_TRACKS_CLOSED"
    fates = sorted(
        (record.terminal_state, record.terminal_frame) for record in contract.terminal_records
    )
    assert fates == [
        ("DISSOLVED_DETECTED_TRACK", 5),
        ("DISSOLVED_DETECTED_TRACK", 5),
        ("RIGHT_CENSORED_AT_HORIZON", 11),
    ]


def test_s3_disappearance_is_not_reported_as_survival():
    schedule = (0, 5, 11)
    dissolving = _tracked(schedule, BLOB_A, EMPTY, EMPTY)
    surviving = _tracked(schedule, BLOB_A, BLOB_A, BLOB_A)
    assert _terminals(dissolving, schedule)[0][0] == "DISSOLVED_DETECTED_TRACK"
    assert _terminals(surviving, schedule)[0][0] == "RIGHT_CENSORED_AT_HORIZON"


# --------------------------------------------------------------------------
# review round 1 — coverage gaps found by the independent reviewers
# --------------------------------------------------------------------------

SEPARATED = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 7), (4, 8), (5, 7), (5, 8)})
CONTACT = _mask({(4, 2), (4, 3), (5, 2), (5, 3), (4, 5), (4, 6), (5, 5), (5, 6)})


def _collapsed() -> np.ndarray:
    value = SEPARATED.copy()
    value[4, 4:7] = True
    return value


def test_r1_tracking_unresolved_is_stamped_with_the_scheduled_frame():
    """Reviewer A, OBS-1: no fixture produced TRACKING_UNRESOLVED at non-unit cadence,
    so a mutant that reverted *only* that event to the positional surrogate survived."""

    schedule = (0, 5, 11, 40)
    repaired = _tracked(schedule, SEPARATED, _collapsed(), SEPARATED, EMPTY)
    unresolved = [event for event in repaired.events if event.kind == "TRACKING_UNRESOLVED"]
    assert unresolved, "fixture must produce an unresolved handoff"
    assert {event.frame for event in unresolved} <= set(schedule)
    assert 1 not in {event.frame for event in repaired.events}
    assert 2 not in {event.frame for event in repaired.events}
    assert unresolved[0].frame == 5
    assert _frames_of(repaired, "DISSOLUTION") == [40] * len(_frames_of(repaired, "DISSOLUTION"))
    assert _violations(repaired, schedule) is None
    states = {value[0] for value in _terminals(repaired, schedule).values()}
    assert "UNRESOLVED_HANDOFF" in states


def test_r2_temporary_contact_is_stamped_with_the_scheduled_frame():
    schedule = (0, 5, 11, 40)
    repaired = _tracked(schedule, SEPARATED, CONTACT, SEPARATED, EMPTY)
    contacts = [event for event in repaired.events if event.kind == "TEMPORARY_CONTACT"]
    assert contacts, "fixture must produce a temporary contact"
    assert {event.frame for event in contacts} <= set(schedule)
    assert contacts[0].frame == 5
    assert _violations(repaired, schedule) is None


def test_r3_a_negative_schedule_is_rejected_by_the_nonnegativity_rule_itself():
    """Reviewer A, OBS-3: every previous negative case was rejected by the
    *consistency* check instead, leaving the nonnegativity rule unpinned.  With a
    leading EMPTY frame there is no observed component to disagree with."""

    observed = _observed((0, 5), EMPTY, BLOB_A)
    with pytest.raises(ValueError, match="nonnegative"):
        track_components(observed, TRACKER, sampled_frames=(-5, 5))


def test_r4_an_unordered_container_is_not_accepted_as_a_schedule():
    """Reviewer A, OBS-4: a set has no order, so it may not stand in for a schedule."""

    observed = _observed((0, 5), BLOB_A, EMPTY)
    for container in ({0, 5}, frozenset({0, 5}), "05", b"\x00\x05"):
        with pytest.raises(ValueError):
            track_components(observed, TRACKER, sampled_frames=container)


def test_r5_first_frame_empty_then_populated_at_nonunit_cadence():
    """Reviewer A, C6: an onset APPEARANCE must carry the real frame, not position 1."""

    schedule = (3, 9, 20)
    repaired = _tracked(schedule, EMPTY, BLOB_A, BLOB_A)
    assert _frames_of(repaired, "APPEARANCE") == [9]
    assert _violations(repaired, schedule) is None


def test_r6_a_visually_identical_component_returning_later_is_not_stitched():
    """Reviewer A, C6: disappearance must not be silently undone by a look-alike."""

    schedule = (0, 5, 11, 17, 23)
    repaired = _tracked(schedule, BLOB_A, EMPTY, EMPTY, EMPTY, BLOB_A)
    assert _frames_of(repaired, "DISSOLUTION") == [5]
    assert _frames_of(repaired, "APPEARANCE") == [0, 23]
    assert len(repaired.tracks) == 2
    assert _violations(repaired, schedule) is None
    terminals = _terminals(repaired, schedule)
    assert terminals[0][:2] == ("DISSOLVED_DETECTED_TRACK", 5)
    assert terminals[1][:2] == ("RIGHT_CENSORED_AT_HORIZON", 23)


# --------------------------------------------------------------------------
# MANDATORY_SAMPLED_FRAMES_LIFECYCLE_REQUALIFICATION_01R
#
# The schedule is mandatory throughout the supported generic tracker and the
# permitted synthetic stack.  These tests pin the API shape itself, the absence of
# every removed fallback, the migration of every permitted call site, and the
# exhaustive synthetic survivorship proof re-run through the mandatory API.
# --------------------------------------------------------------------------


ALLOWED_SOURCE_PATHS = (
    "edlab/__init__.py",
    "edlab/specs.py",
    "edlab/state.py",
    "edlab/substrates/__init__.py",
    "edlab/substrates/lattice_bond/__init__.py",
    "edlab/substrates/lattice_bond/engine.py",
    "edlab/substrates/lattice_bond/instrumentation.py",
    "edlab/substrates/lattice_bond/lifecycle.py",
    "edlab/substrates/lattice_bond/future_lifecycle_runner.py",
    "tests/test_lattice_bond_instrumentation.py",
    "tests/test_future_lifecycle_contract.py",
    "tests/test_future_lifecycle_runner_integration.py",
    "tests/test_empty_right_nonunit_cadence_tracker_repair.py",
)


def _repository_root():
    from pathlib import Path

    return Path(__file__).resolve().parents[1]


# --- m1-m4: the mandatory API boundary -------------------------------------


def test_m1_schedule_omission_fails_at_the_public_api_boundary():
    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(TypeError):
        track_components(observed, TRACKER)


def test_m2_explicit_none_is_refused_rather_than_treated_as_absent():
    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(ValueError, match="must not be None"):
        track_components(observed, TRACKER, sampled_frames=None)


def test_m3_the_signature_itself_carries_no_schedule_free_path():
    parameters = inspect.signature(track_components).parameters
    assert "sampled_frames" in parameters
    parameter = parameters["sampled_frames"]
    assert parameter.default is inspect.Parameter.empty, "sampled_frames must have no default"
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, "sampled_frames must be keyword-only"
    annotation = str(parameter.annotation)
    assert "None" not in annotation and "Optional" not in annotation, annotation


def test_m4_no_compatibility_alias_restores_the_old_signature():
    """No positional third argument, and no second entry point with a default."""

    observed = _observed((0, 5), BLOB_A, EMPTY)
    with pytest.raises(TypeError):
        track_components(observed, TRACKER, (0, 5))
    module_root = _repository_root() / "edlab" / "substrates" / "lattice_bond"
    source = (module_root / "instrumentation.py").read_text(encoding="utf-8")
    assert "sampled_frames: Sequence[int] | None" not in source
    assert "sampled_frames=None" not in source
    assert "sampled_frames: Sequence[int] = " not in source
    exported = (module_root / "__init__.py").read_text(encoding="utf-8")
    assert exported.count("track_components") == 2, "one import, one __all__ entry, no alias"


# --- m5-m7: the removed fallbacks ------------------------------------------


def test_m5_the_transition_index_fallback_is_gone_from_the_module():
    assert not hasattr(instrumentation, "_transition_right_frame")
    source = (
        _repository_root() / "edlab" / "substrates" / "lattice_bond" / "instrumentation.py"
    ).read_text(encoding="utf-8")
    assert "right[0].frame if right else" not in source
    # ``transition_index + 1`` may only ever appear as an index INTO the declared
    # schedule; as a bare frame value it is the deleted positional surrogate.
    occurrences = source.count("transition_index + 1")
    assert occurrences == source.count("schedule[transition_index + 1]") == 1, source.count(
        "transition_index + 1"
    )


def test_m6_no_implicit_unit_cadence_is_reconstructed_anywhere():
    source = (
        _repository_root() / "edlab" / "substrates" / "lattice_bond" / "instrumentation.py"
    ).read_text(encoding="utf-8")
    assert "range(len(frames))" not in source
    assert "_validated_sample_schedule" in source
    validator = inspect.signature(instrumentation._validated_sample_schedule)
    assert "None" not in str(validator.return_annotation), str(validator.return_annotation)


def test_m7_the_validator_never_returns_for_a_missing_schedule():
    with pytest.raises(ValueError):
        instrumentation._validated_sample_schedule((), None)


# --- m8: every permitted call site supplies a schedule ---------------------


def test_m8_every_permitted_call_site_passes_an_explicit_schedule():
    """Exact-path inventory.  Scoped to the permitted generic tracker and synthetic
    stack only; it makes no claim about callers outside these declared paths."""

    import ast

    def _raises_guarded(tree):
        """Nodes lexically inside a ``with pytest.raises(...)`` block.

        Those call sites exist precisely to prove that a malformed or absent schedule
        is refused, so they are negative evidence, not unmigrated callers.
        """

        guarded = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.With):
                continue
            if not any(
                isinstance(item.context_expr, ast.Call)
                and isinstance(item.context_expr.func, ast.Attribute)
                and item.context_expr.func.attr == "raises"
                for item in node.items
            ):
                continue
            for statement in node.body:
                for inner in ast.walk(statement):
                    guarded.add(id(inner))
        return guarded

    root = _repository_root()
    inventory: dict[str, int] = {}
    refused: dict[str, int] = {}
    for relative in ALLOWED_SOURCE_PATHS:
        tree = ast.parse((root / relative).read_text(encoding="utf-8"), filename=relative)
        guarded = _raises_guarded(tree)
        calls = 0
        negatives = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            target = node.func
            name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", None)
            if name != "track_components":
                continue
            if id(node) in guarded:
                negatives += 1
                continue
            calls += 1
            keywords = {keyword.arg for keyword in node.keywords}
            assert "sampled_frames" in keywords, f"{relative}: schedule-free call site"
            assert len(node.args) == 2, f"{relative}: schedule must not be positional"
        if calls:
            inventory[relative] = calls
        if negatives:
            refused[relative] = negatives
    assert inventory, "the inventory must not be silently empty"
    assert refused, "the refusal evidence must not be silently empty"
    assert set(inventory) == {
        "tests/test_lattice_bond_instrumentation.py",
        "tests/test_future_lifecycle_contract.py",
        "tests/test_future_lifecycle_runner_integration.py",
        "tests/test_empty_right_nonunit_cadence_tracker_repair.py",
    }


# --- e1: the exhaustive synthetic proof, re-run through the mandatory API ---


ENUMERATION_SCHEDULE = (0, 5, 11, 12)
# Declared alphabet, eight handcrafted masks, all defined in this module.  Reviewer B
# of EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00 described the historical alphabet in
# ``EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REVIEW_JOURNAL.md`` as "empty, two
# disjoint blobs, a third blob, a joinable bar, a split bar, and a symmetric-tie pair
# that forces TRACKING_UNRESOLVED"; this reconstruction follows that description.  The
# third blob's pixel geometry is recorded nowhere, so the with/without-disappearance
# PARTITION is not reconstructible — see the 01R report.  Every REQUIRED outcome below
# is zero-valued and alphabet-independent.
BLOB_C = _mask({(1, 1), (1, 2), (2, 1), (2, 2)})
ENUMERATION_ALPHABET = (
    EMPTY,
    BLOB_A,
    BLOB_B,
    BLOB_C,
    JOINED,
    SPLIT,
    SEPARATED,
)


def test_e1_exhaustive_depth4_enumeration_through_the_mandatory_api():
    alphabet = ENUMERATION_ALPHABET + (_collapsed(),)
    assert len(alphabet) == 8
    schedule = ENUMERATION_SCHEDULE
    configurations = 0
    with_disappearance = 0
    rejected_with = 0
    rejected_without = 0
    off_schedule = 0
    accounting_failures = 0
    scheduled = set(schedule)
    for combination in itertools.product(alphabet, repeat=len(schedule)):
        observed = _observed(schedule, *combination)
        result = track_components(observed, TRACKER, sampled_frames=schedule)
        configurations += 1
        if any(event.frame not in scheduled for event in result.events):
            off_schedule += 1
        disappeared = any(event.kind == "DISSOLUTION" for event in result.events)
        try:
            contract = qualify_lifecycle_contract(result, schedule)
        except LifecycleContractError:
            if disappeared:
                rejected_with += 1
            else:
                rejected_without += 1
            continue
        if len(contract.terminal_records) != len(result.tracks):
            accounting_failures += 1
        if disappeared:
            with_disappearance += 1
    assert configurations == 4096
    assert off_schedule == 0, "every event frame must belong to the declared schedule"
    assert rejected_with == 0, "disappearance must not be correlated with global rejection"
    assert rejected_without == 0, "survival must not be rejected either"
    assert accounting_failures == 0, "terminal accounting must be exhaustive"
    assert with_disappearance > 0, "the enumeration must actually exercise disappearance"
