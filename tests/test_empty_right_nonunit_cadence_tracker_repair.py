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
the outcome: a survivorship trapdoor.  The repair makes the declared schedule
authoritative for the right frame of every transition.
"""

from __future__ import annotations

import numpy as np
import pytest

from edlab.substrates.lattice_bond import (
    DetectorSpec,
    LatticeBondState,
    TrackerSpec,
    detect_components,
    track_components,
)
from edlab.substrates.lattice_bond.instrumentation import TrackingResult
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


def _legacy(schedule, *masks) -> TrackingResult:
    """The accepted-parent call path: no declared schedule."""

    return track_components(_observed(schedule, *masks), TRACKER)


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
    """Unit cadence: the repaired path must agree with the legacy path exactly."""

    schedule = (0, 1)
    repaired = _tracked(schedule, BLOB_A, EMPTY)
    legacy = _legacy(schedule, BLOB_A, EMPTY)
    assert repaired == legacy
    assert _frames_of(repaired, "DISSOLUTION") == [1]
    assert _violations(repaired, schedule) is None
    assert _terminals(repaired, schedule)[0][:2] == ("DISSOLVED_DETECTED_TRACK", 1)


def test_02_empty_right_frame_at_nonunit_cadence_binds_the_actual_frame():
    """The defect and its repair, side by side, on identical detector input."""

    schedule = (0, 5)
    observed = _observed(schedule, BLOB_A, EMPTY)

    legacy = track_components(observed, TRACKER)
    assert _frames_of(legacy, "DISSOLUTION") == [1], "legacy fabricated frame must be 1"
    assert _violations(legacy, schedule) == [
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
    """Disappearance and survival must be distinguishable, and both must qualify."""

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
def test_15_unit_cadence_behaviour_is_bit_identical_with_and_without_a_schedule(masks):
    """The repair is inert on the unit-cadence path that every existing test uses."""

    schedule = tuple(range(len(masks)))
    observed = _observed(schedule, *masks)
    assert track_components(observed, TRACKER) == track_components(
        observed, TRACKER, sampled_frames=schedule
    )


def test_15b_the_legacy_call_path_is_untouched_when_no_schedule_is_supplied():
    """Omitting ``sampled_frames`` must reproduce the accepted-parent behaviour exactly,
    including the behaviour this mission classifies as defective."""

    observed = _observed((0, 5), BLOB_A, EMPTY)
    legacy = track_components(observed, TRACKER)
    assert _frames_of(legacy, "DISSOLUTION") == [1]


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

    # the accepted parent: the surviving run qualified, the dissolving run did not.
    legacy_dissolving = _legacy(schedule, BLOB_A, EMPTY, BLOB_B)
    legacy_surviving = _legacy(schedule, BLOB_A, BLOB_A, BLOB_A)
    assert _violations(legacy_surviving, schedule) is None
    legacy_codes = _violations(legacy_dissolving, schedule)
    assert legacy_codes is not None and "INVALID_EVENT_FRAME" in legacy_codes


def test_s2_a_disappearing_track_stays_in_the_enrolled_denominator():
    schedule = (0, 5, 11)
    repaired = _tracked(schedule, BLOB_A | BLOB_B, BLOB_B, BLOB_B)
    contract = qualify_lifecycle_contract(repaired, schedule)
    assert contract.track_count == len(repaired.tracks) == 2
    assert len(contract.terminal_records) == contract.track_count
    assert contract.run_terminal_state == "ALL_TRACKS_CLOSED"


def test_s3_disappearance_is_not_reported_as_survival():
    schedule = (0, 5, 11)
    dissolving = _tracked(schedule, BLOB_A, EMPTY, EMPTY)
    surviving = _tracked(schedule, BLOB_A, BLOB_A, BLOB_A)
    assert _terminals(dissolving, schedule)[0][0] == "DISSOLVED_DETECTED_TRACK"
    assert _terminals(surviving, schedule)[0][0] == "RIGHT_CENSORED_AT_HORIZON"
