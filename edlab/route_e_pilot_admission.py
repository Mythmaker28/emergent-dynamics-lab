"""Pilot admission: recompute the transport, then re-derive the outcome from bytes.

THE TWO CHECKS ARE DELIBERATELY SEPARATE
----------------------------------------
:func:`admit_pilot_world` takes NO engine step.  It reads persisted bytes, recomputes the
passive cohort for EVERY transition from the persisted gross flows, checks the physical
bounds, the finiteness and the global conservation at every step, and compares the result
with the persisted tracer.  It then re-derives the outcome through the A1-R5 hardened
``derive_world_outcome``, which it does not reimplement.

:func:`verify_engine_provenance` DOES take engine steps, on purpose, and says so in its
name.  It re-executes the canonical engine from the persisted law spec and initial state
and requires every persisted matter and tracer frame to be byte-identical.  This is the
check a handwritten or resealed artefact cannot pass, and it is the ONLY thing in this
module that may set ``engine_reexecution_verified``.

Keeping them apart matters: the first establishes that the numbers are internally
derivable from the transport; only the second establishes that the canonical engine
produced them.  Merging them would let an engine-free claim borrow the engine's authority.

TECHNICAL INCIDENTS ARE NEVER RESULTS
-------------------------------------
Every refusal raised here classifies the unit ``TECHNICAL_INVALID`` with ``Y = None`` for
all three conventions.  There is no path from a crash, a truncated horizon, a broken join
or an inconsistent flux to a ``Y = 0``.  ``Y = 0`` requires an OBSERVED failure inside a
complete, verified horizon.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .substrates.lattice_bond.future_prospective_measurement_bridge import MeasurementSpec
from .substrates.lattice_bond.future_route_e_world_evidence import (
    COHORT_RESIDUAL_CONVENTIONS,
    derive_world_outcome,
    read_channel,
)
from .substrates.lattice_bond.instrumentation import detect_components, track_components
from .substrates.lattice_bond.engine import LatticeBondState
from . import route_e_pilot as _pilot
from . import route_e_pilot_acquisition as _acq
from . import route_e_strict as _strict

__all__ = [
    "PilotAdmissionRefusal",
    "TrackDiagnostic",
    "PilotWorldAdmission",
    "admit_pilot_world",
    "verify_engine_provenance",
    "TECHNICAL_INVALID",
]

TECHNICAL_INVALID = "TECHNICAL_INVALID"

_MASK_PRESENT = 0.8
_MASK_ABSENT = 0.1
_MASK_RESOURCE = 0.8


class PilotAdmissionRefusal(ValueError):
    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


@dataclass(frozen=True)
class TrackDiagnostic:
    """One eligible track at the horizon, with everything the protocol demands."""

    track_id: int
    residual_union: float
    residual_focal: float | None
    component_mass: float
    component_cells: int
    q_min_inventory: float
    inventory_blocks_convention: Mapping[str, bool]
    rank_of_minimum: int


@dataclass
class PilotWorldAdmission:
    ordinal: int
    status: str
    lattice_size: int
    sampled_frames: tuple[int, ...] = ()
    Y_by_f: Mapping[str, int | None] = field(default_factory=dict)
    disposition_by_f: Mapping[str, str] = field(default_factory=dict)
    classification: str = _strict.ENGINE_UNPROVEN_CLASS
    transport_transitions_recomputed: int = 0
    transport_max_tracer_deviation: float = 0.0
    global_tracer_conservation_max_drift: float = 0.0
    mechanically_ineligible: bool = False
    ineligibility_cause: str = ""
    terminal_states: tuple[str, ...] = ()
    eligible_tracks: tuple[TrackDiagnostic, ...] = ()
    wrapping_at_t0: bool = False
    wrapping_anywhere: bool = False
    total_matter: tuple[float, ...] = ()
    total_tracer: tuple[float, ...] = ()
    labelled_fraction: tuple[float, ...] = ()
    boundary_flux: tuple[Mapping[str, float], ...] = ()
    engine_reexecution_verified: bool = False
    #: Mechanically false on every pilot verdict.  There is no code path that sets it.
    contributes_to_k: bool = False
    incident: str = ""
    incident_reason_code: str = ""

    def as_document(self) -> dict[str, Any]:
        return {
            "Y_by_f": {k: (None if v is None else int(v)) for k, v in sorted(self.Y_by_f.items())},
            "boundary_flux": [dict(sorted(entry.items())) for entry in self.boundary_flux],
            "classification": self.classification,
            "disposition_by_f": dict(sorted(self.disposition_by_f.items())),
            "eligible_tracks": [
                {
                    "component_cells": int(t.component_cells),
                    "component_mass": float(t.component_mass),
                    "inventory_blocks_convention": dict(sorted(t.inventory_blocks_convention.items())),
                    "q_min_inventory": float(t.q_min_inventory),
                    "rank_of_minimum": int(t.rank_of_minimum),
                    "residual_focal": (
                        None if t.residual_focal is None else float(t.residual_focal)
                    ),
                    "residual_union": float(t.residual_union),
                    "track_id": int(t.track_id),
                }
                for t in self.eligible_tracks
            ],
            "contributes_to_k": False,
            "engine_reexecution_verified": bool(self.engine_reexecution_verified),
            "global_tracer_conservation_max_drift": float(self.global_tracer_conservation_max_drift),
            "incident": self.incident,
            "incident_reason_code": self.incident_reason_code,
            "ineligibility_cause": self.ineligibility_cause,
            "labelled_fraction": [float(v) for v in self.labelled_fraction],
            "lattice_size": int(self.lattice_size),
            "mechanically_ineligible": bool(self.mechanically_ineligible),
            "ordinal": int(self.ordinal),
            "sampled_frames": [int(v) for v in self.sampled_frames],
            "status": self.status,
            "terminal_states": list(self.terminal_states),
            "total_matter": [float(v) for v in self.total_matter],
            "total_tracer": [float(v) for v in self.total_tracer],
            "transport_max_tracer_deviation": float(self.transport_max_tracer_deviation),
            "transport_transitions_recomputed": int(self.transport_transitions_recomputed),
            "wrapping_anywhere": bool(self.wrapping_anywhere),
            "wrapping_at_t0": bool(self.wrapping_at_t0),
        }


def _invalid(ordinal: int, size: int, exc: Exception, cause: str) -> PilotWorldAdmission:
    """Every refusal lands here: Y is None for every convention, never 0."""
    code = getattr(exc, "reason_code", type(exc).__name__)
    return PilotWorldAdmission(
        ordinal=int(ordinal),
        status=TECHNICAL_INVALID,
        lattice_size=int(size),
        Y_by_f={f"{value:g}": None for value in COHORT_RESIDUAL_CONVENTIONS},
        disposition_by_f={f"{value:g}": "TECHNICALLY_UNKNOWN" for value in COHORT_RESIDUAL_CONVENTIONS},
        incident=f"{cause}: {str(exc)[:300]}",
        incident_reason_code=str(code),
    )


def _read_json(path: Path, label: str, code: str) -> dict[str, Any]:
    if not path.is_file():
        raise PilotAdmissionRefusal(f"{label} is absent", reason_code=code)
    return _strict.strict_json_object(path.read_bytes(), label, code)


def _load_ledger(directory: Path) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    header = _read_json(
        directory / _acq.LEDGER_DIRECTORY / "LEDGER.json", "LEDGER.json", "PILOT_LEDGER_ABSENT"
    )
    if header.get("kind") != _acq.LEDGER_KIND:
        raise PilotAdmissionRefusal("LEDGER.json is not a pilot transport ledger",
                                    reason_code="PILOT_LEDGER_KIND")
    shape = (int(header["frame_shape"][0]), int(header["frame_shape"][1]))
    cells = shape[0] * shape[1]
    transitions = _strict.require_plain_int(
        header["transitions"], "transitions", code="PILOT_LEDGER_SHAPE"
    )
    frames = _strict.require_plain_int(
        header["matter_frames"], "matter_frames", code="PILOT_LEDGER_SHAPE"
    )
    if frames != transitions + 1:
        raise PilotAdmissionRefusal(
            "the ledger must hold exactly one more state frame than it holds transitions",
            reason_code="PILOT_LEDGER_SHAPE",
        )
    paths = _acq.ledger_paths(directory)
    expected = {
        "matter": frames * cells * 8,
        "tracer": frames * cells * 8,
        "forward": transitions * 2 * cells * 8,
        "reverse": transitions * 2 * cells * 8,
    }
    arrays: dict[str, np.ndarray] = {}
    digests = header.get("ledger_sha256", {})
    for name, size in expected.items():
        path = paths[name]
        if not path.is_file():
            raise PilotAdmissionRefusal(f"ledger channel {name} is absent",
                                        reason_code="PILOT_LEDGER_ABSENT")
        payload = path.read_bytes()
        if len(payload) != size:
            raise PilotAdmissionRefusal(
                f"ledger channel {name} is {len(payload)} bytes, expected {size}",
                reason_code="PILOT_LEDGER_SHAPE",
            )
        if hashlib.sha256(payload).hexdigest() != str(digests.get(name)):
            raise PilotAdmissionRefusal(
                f"ledger channel {name} does not match its declared digest",
                reason_code="PILOT_LEDGER_DIGEST",
            )
        values = np.frombuffer(payload, dtype="<f8")
        if not bool(np.isfinite(values).all()):
            raise PilotAdmissionRefusal(f"ledger channel {name} carries a non-finite value",
                                        reason_code="PILOT_LEDGER_NON_FINITE")
        if name in ("matter", "tracer"):
            arrays[name] = values.reshape((frames, *shape))
        else:
            arrays[name] = values.reshape((transitions, 2, *shape))
    return header, arrays


def _divergence(net: np.ndarray) -> np.ndarray:
    return (net[0] - np.roll(net[0], 1, axis=0)) + (net[1] - np.roll(net[1], 1, axis=1))


def _advance_tracer_from_ledger(
    tracer: np.ndarray,
    pre_matter: np.ndarray,
    forward: np.ndarray,
    reverse: np.ndarray,
    dt: float,
) -> np.ndarray:
    """The transport step, written out from the persisted flows.

    This is deliberately an INDEPENDENT statement of the same arithmetic as
    ``instrumentation.advance_passive_tracer``: if the two ever disagreed, the pilot
    would see it as a deviation rather than inherit the producer's own helper.  The
    formula is the one the module's docstring declares, not a copy of its code path --
    there are no guard clauses here, only the arithmetic.
    """
    fraction = np.divide(tracer, pre_matter, out=np.zeros_like(tracer), where=pre_matter > 0.0)
    flux = np.empty_like(forward)
    for axis in (0, 1):
        flux[axis] = forward[axis] * fraction - reverse[axis] * np.roll(fraction, -1, axis=axis)
    return tracer - dt * _divergence(flux)


def _boundary_flux(
    cells: np.ndarray,
    shape: tuple[int, int],
    forward: np.ndarray,
    reverse: np.ndarray,
    fraction: np.ndarray,
    dt: float,
) -> dict[str, float]:
    """Gross matter crossing this component's boundary, split labelled / unlabelled."""
    inside = np.zeros(shape, dtype=bool)
    rows, cols = np.divmod(np.asarray(sorted(int(c) for c in cells)), shape[1])
    inside[rows, cols] = True
    total_in = total_out = labelled_in = labelled_out = 0.0
    for axis in (0, 1):
        plus = np.roll(inside, -1, axis=axis)
        frac_plus = np.roll(fraction, -1, axis=axis)
        entering = (~inside) & plus  # face carries (y,x) -> neighbour, neighbour inside
        leaving = inside & (~plus)
        total_in += float(dt * np.sum(forward[axis][entering]))
        labelled_in += float(dt * np.sum(forward[axis][entering] * fraction[entering]))
        total_out += float(dt * np.sum(reverse[axis][entering]))
        labelled_out += float(dt * np.sum(reverse[axis][entering] * frac_plus[entering]))
        total_out += float(dt * np.sum(forward[axis][leaving]))
        labelled_out += float(dt * np.sum(forward[axis][leaving] * fraction[leaving]))
        total_in += float(dt * np.sum(reverse[axis][leaving]))
        labelled_in += float(dt * np.sum(reverse[axis][leaving] * frac_plus[leaving]))
    return {
        "gross_in": total_in,
        "gross_in_labelled": labelled_in,
        "gross_in_unlabelled": total_in - labelled_in,
        "gross_out": total_out,
        "gross_out_labelled": labelled_out,
        "gross_out_unlabelled": total_out - labelled_out,
    }


def _materialise(mask: np.ndarray, frame: int) -> LatticeBondState:
    shape = (int(mask.shape[0]), int(mask.shape[1]))
    return LatticeBondState(
        np.where(mask, _MASK_PRESENT, _MASK_ABSENT).astype(np.float64),
        np.full(shape, _MASK_RESOURCE, dtype=np.float64),
        np.zeros((2, *shape), dtype=np.float64),
        frame,
    )


def admit_pilot_world(
    world_directory: str | Path,
    *,
    ordinal: int,
    lattice_size: int,
    measurement_spec: MeasurementSpec | None = None,
    require_fixture_class: str | None = None,
    expected_sampled_frames: Sequence[int] | None = None,
) -> PilotWorldAdmission:
    """Read bytes, recompute the transport, re-derive the outcome.  No engine step.

    ``require_fixture_class`` is how the engine-data path refuses a synthetic fixture:
    the scientific pilot runner passes ``PILOT_EXPLORATORY_NON_CONFIRMATORY``, so a
    transport-constructed ``SYNTHETIC_NON_SCIENTIFIC`` world is refused outright rather
    than silently mixed into the engine population.
    """
    directory = Path(world_directory)
    spec = MeasurementSpec() if measurement_spec is None else measurement_spec
    try:
        _strict.check_frozen_measurement_spec(spec)
        provenance = _read_json(
            directory / "PILOT_PROVENANCE.json", "PILOT_PROVENANCE.json", "PILOT_PROVENANCE_ABSENT"
        )
        if provenance.get("kind") != _pilot.PILOT_PROVENANCE_KIND:
            raise PilotAdmissionRefusal("not a pilot provenance document",
                                        reason_code="PILOT_NOT_A_PILOT_ROOT")
        if provenance.get("tag") != _pilot.PILOT_PROVENANCE_TAG:
            raise PilotAdmissionRefusal("the pilot provenance tag is not the canonical one",
                                        reason_code="PILOT_NOT_A_PILOT_ROOT")
        namespace = provenance.get("output_namespace")
        if not isinstance(namespace, str) or not namespace.startswith(
            _pilot.PILOT_NAMESPACE_PREFIX
        ):
            raise PilotAdmissionRefusal("a pilot root must carry a PILOT- namespace",
                                        reason_code="PILOT_NAMESPACE_PREFIX")
        if require_fixture_class is not None and (
            provenance.get("fixture_class") != require_fixture_class
        ):
            raise PilotAdmissionRefusal(
                f"fixture_class is {provenance.get('fixture_class')!r}, and this entry "
                f"admits only {require_fixture_class!r}",
                reason_code="FIXTURE_CLASS_REFUSED",
            )
        for forbidden in ("Y", "y", "k", "verdict", "outcome", "result"):
            if forbidden in provenance:
                raise PilotAdmissionRefusal(
                    f"the acquisition wrote {forbidden!r}: a producer never writes an answer",
                    reason_code="RUNNER_WROTE_AN_ANSWER",
                )

        header, ledger = _load_ledger(directory)
        shape = (int(header["frame_shape"][0]), int(header["frame_shape"][1]))
        if shape[0] != int(lattice_size) or shape[1] != int(lattice_size):
            raise PilotAdmissionRefusal("the ledger shape is not the declared lattice size",
                                        reason_code="PILOT_LEDGER_SHAPE")
        dt = float(header["dt"])
        labels = [int(v) for v in header["sampled_frames"]]
        transitions = int(header["transitions"])
        if expected_sampled_frames is not None and labels != [
            int(v) for v in expected_sampled_frames
        ]:
            # CORRECTIVE PASS.  The horizon moves the outcome, so it may not be a free
            # knob: the reviewer showed the same law and seed giving Y = 0 at horizon 64
            # and Y = 1 at horizon 4096.  The scientific runner now passes the schedule
            # derived from the COMMITTED manifest, and a ledger declaring any other
            # schedule is refused.
            raise PilotAdmissionRefusal(
                "the ledger schedule is not the schedule committed in the manifest",
                reason_code="SCHEDULE_NOT_THE_COMMITTED_ONE",
            )
        matter = ledger["matter"]
        tracer = ledger["tracer"]
        forward = ledger["forward"]
        reverse = ledger["reverse"]

        # ---- G2.  Every transition, recomputed from persisted evidence alone. --------
        # CORRECTIVE PASS.  The first draft used ONE absolute tolerance derived from the
        # ledger-wide maximum matter value, and an independent reviewer defeated it: a
        # single far-away cell holding a huge value inflated the bound until a fabricated
        # cohort passed.  The criterion is now ELEMENT-WISE and RELATIVE -- exactly the
        # frozen float64 criterion this repository already declares in AGENTS.md,
        # ``abs(error) <= 1e-12 + 1e-10 * abs(reference)`` -- so no distant cell can widen
        # the bound applied to any other cell.
        def _within(observed: np.ndarray, reference: np.ndarray) -> bool:
            return bool(
                np.all(np.abs(observed - reference) <= 1e-12 + 1e-10 * np.abs(reference))
            )

        def _worst(observed: np.ndarray, reference: np.ndarray) -> float:
            allowed = 1e-12 + 1e-10 * np.abs(reference)
            return float(np.max(np.abs(observed - reference) - allowed))

        cohort = tracer[0].copy()
        max_deviation = 0.0
        max_conservation_drift = 0.0
        enrolled_total = float(math.fsum(cohort.ravel()))
        for t in range(transitions):
            pre = matter[t]
            post = matter[t + 1]
            fwd = forward[t]
            rev = reverse[t]
            if float(np.min(fwd)) < 0.0 or float(np.min(rev)) < 0.0:
                raise PilotAdmissionRefusal(
                    f"a gross flow is negative at transition {t}", reason_code="FLOW_NEGATIVE"
                )
            if float(np.min(pre)) < 0.0 or float(np.min(post)) < 0.0:
                raise PilotAdmissionRefusal(
                    f"matter is negative at transition {t}", reason_code="MATTER_NEGATIVE"
                )
            expected_post = pre - dt * _divergence(fwd - rev)
            if not _within(post, expected_post):
                raise PilotAdmissionRefusal(
                    f"persisted matter at {t + 1} is inconsistent with the persisted flows",
                    reason_code="MATTER_FLUX_INCONSISTENT",
                )
            local = 1e-12 + 1e-10 * np.abs(pre)
            if bool(np.any(cohort - pre > local)) or bool(np.any(cohort < -local)):
                raise PilotAdmissionRefusal(
                    f"the cohort left [0, matter] at step {t}", reason_code="TRACER_OUT_OF_DOMAIN"
                )
            cohort = _advance_tracer_from_ledger(cohort, pre, fwd, rev, dt)
            drift = abs(float(math.fsum(cohort.ravel())) - enrolled_total)
            max_conservation_drift = max(max_conservation_drift, drift)
            if drift > 1e-12 + 1e-10 * abs(enrolled_total):
                raise PilotAdmissionRefusal(
                    f"global cohort conservation failed at transition {t}",
                    reason_code="TRACER_CONSERVATION_FAILED",
                )
            max_deviation = max(max_deviation, _worst(cohort, tracer[t + 1]))
            if not _within(cohort, tracer[t + 1]):
                raise PilotAdmissionRefusal(
                    f"the recomputed cohort disagrees with the persisted cohort at {t + 1}",
                    reason_code="TRACER_RECOMPUTATION_MISMATCH",
                )

        # ---- the sampled frames must BE the ledger frames at the scheduled labels ----
        # CORRECTIVE PASS.  The first draft cross-checked ``matter`` and ``tracer`` only.
        # An independent reviewer then fabricated a Y = 1 in a world with ZERO transport
        # by rewriting nothing but the ``mask`` frames: the mask alone decides which
        # components exist, which tracks are followed, and which cells the residual is
        # read over, so a mask that no longer summarises the matter selects an imaginary
        # component.  The mask is a DERIVED channel and is now re-derived here, from the
        # matter ledger and the frozen threshold, and required to match bit for bit.
        for position, label in enumerate(labels):
            persisted_matter = read_channel(directory, position, "matter", shape)
            persisted_tracer = read_channel(directory, position, "tracer", shape)
            persisted_mask = read_channel(directory, position, "mask", shape)
            if not np.array_equal(persisted_matter, matter[label]):
                raise PilotAdmissionRefusal(
                    f"sampled matter frame {position} is not the ledger state at step {label}",
                    reason_code="FRAME_LEDGER_DISAGREEMENT",
                )
            if not np.array_equal(persisted_tracer, tracer[label]):
                raise PilotAdmissionRefusal(
                    f"sampled tracer frame {position} is not the ledger cohort at step {label}",
                    reason_code="FRAME_LEDGER_DISAGREEMENT",
                )
            if not np.array_equal(persisted_mask, matter[label] >= spec.matter_threshold):
                raise PilotAdmissionRefusal(
                    f"sampled mask frame {position} is not the matter field thresholded at "
                    f"{spec.matter_threshold}: the mask is derived evidence and may not "
                    "disagree with the matter it summarises",
                    reason_code="MASK_NOT_DERIVED_FROM_MATTER",
                )

        # ---- the outcome, re-derived by the A1-R5 hardened path, not reimplemented ---
        evidence = derive_world_outcome(
            directory,
            sampled_frames=labels,
            frame_shape=shape,
            detector=spec.detector_spec(),
            tracker=spec.tracker_spec(),
        )

        # ---- diagnostics ------------------------------------------------------------
        totals_matter = tuple(float(math.fsum(matter[label].ravel())) for label in labels)
        totals_tracer = tuple(float(math.fsum(tracer[label].ravel())) for label in labels)
        labelled_fraction = tuple(
            (tt / tm if tm > 0.0 else 0.0) for tm, tt in zip(totals_matter, totals_tracer)
        )

        frames_components = [
            list(detect_components(_materialise(read_channel(directory, p, "mask", shape), int(l)),
                                   spec.detector_spec(), frame=int(l)))
            for p, l in enumerate(labels)
        ]
        wrapping_at_t0 = any(bool(c.wraps_y or c.wraps_x) for c in frames_components[0])
        wrapping_anywhere = any(
            bool(c.wraps_y or c.wraps_x) for fc in frames_components for c in fc
        )

        cause = ""
        if evidence.mechanically_ineligible or not evidence.eligible_track_ids:
            if wrapping_anywhere:
                cause = "WRAPPING_COMPONENT_PRESENT"
            elif not any(frames_components[0]):
                cause = "NO_COMPONENT_AT_ENROLMENT"
            elif evidence.terminal_states:
                cause = "TERMINAL_" + "+".join(evidence.terminal_states)
            else:
                cause = "NO_ELIGIBLE_TRACK_TO_HORIZON"

        # focal cohort: the largest eligible component at t0, propagated through the SAME
        # persisted flows.  The transport is linear in the cohort, so this needs no engine.
        focal_by_track: dict[int, float] = {}
        if evidence.eligible_track_ids:
            focal_cells = _largest_component_cells(frames_components[0], shape)
            if focal_cells is not None:
                focal = np.zeros(shape, dtype=np.float64)
                rows, cols = np.divmod(np.asarray(sorted(focal_cells)), shape[1])
                focal[rows, cols] = matter[0][rows, cols]
                for t in range(transitions):
                    focal = _advance_tracer_from_ledger(
                        focal, matter[t], forward[t], reverse[t], dt
                    )
                last = frames_components[-1]
                tracking = track_components(
                    tuple(frames_components), spec.tracker_spec(), sampled_frames=tuple(labels)
                )
                index_by_track = {
                    int(track.track_id): int(track.points[-1].component_index)
                    for track in tracking.tracks
                    if track.points
                }
                by_index = {int(c.index): c for c in last}
                for track_id in evidence.eligible_track_ids:
                    component = by_index.get(index_by_track.get(int(track_id), -1))
                    if component is None:
                        continue
                    r, c = np.divmod(
                        np.asarray(sorted(int(x) for x in component.cells)), shape[1]
                    )
                    mass = float(np.sum(matter[labels[-1]][r, c]))
                    if mass > 0.0:
                        focal_by_track[int(track_id)] = float(np.sum(focal[r, c])) / mass

        residuals = dict(evidence.residual_at_horizon)
        ordered = sorted(evidence.eligible_track_ids, key=lambda t: residuals.get(int(t), 1.0))
        total_unlabelled = totals_matter[-1] - totals_tracer[-1]
        last_components = {int(c.index): c for c in frames_components[-1]}
        tracking_last = track_components(
            tuple(frames_components), spec.tracker_spec(), sampled_frames=tuple(labels)
        )
        index_by_track_last = {
            int(track.track_id): int(track.points[-1].component_index)
            for track in tracking_last.tracks
            if track.points
        }
        diagnostics: list[TrackDiagnostic] = []
        for rank, track_id in enumerate(ordered):
            component = last_components.get(index_by_track_last.get(int(track_id), -1))
            if component is None:
                continue
            r, c = np.divmod(np.asarray(sorted(int(x) for x in component.cells)), shape[1])
            mass = float(np.sum(matter[labels[-1]][r, c]))
            q_min = max(0.0, 1.0 - (total_unlabelled / mass)) if mass > 0.0 else 1.0
            diagnostics.append(
                TrackDiagnostic(
                    track_id=int(track_id),
                    residual_union=float(residuals.get(int(track_id), float("nan"))),
                    residual_focal=focal_by_track.get(int(track_id)),
                    component_mass=mass,
                    component_cells=int(component.area),
                    q_min_inventory=float(q_min),
                    inventory_blocks_convention={
                        f"{value:g}": bool(mass > total_unlabelled / (1.0 - value))
                        for value in COHORT_RESIDUAL_CONVENTIONS
                    },
                    rank_of_minimum=int(rank),
                )
            )

        flux: list[dict[str, float]] = []
        if diagnostics:
            best_track = diagnostics[0].track_id
            index_by_track_frame = {
                int(track.track_id): {int(p.frame): int(p.component_index) for p in track.points}
                for track in tracking_last.tracks
            }
            per_frame = index_by_track_frame.get(int(best_track), {})
            for position, label in enumerate(labels[:-1]):
                component_index = per_frame.get(int(label))
                if component_index is None:
                    continue
                component = next(
                    (c for c in frames_components[position] if int(c.index) == component_index), None
                )
                if component is None:
                    continue
                pre = matter[label]
                frac = np.divide(
                    tracer[label], pre, out=np.zeros_like(pre), where=pre > 0.0
                )
                entry = _boundary_flux(
                    np.asarray(sorted(int(x) for x in component.cells)),
                    shape,
                    forward[label],
                    reverse[label],
                    frac,
                    dt,
                )
                entry["frame"] = float(label)
                flux.append(entry)

        return PilotWorldAdmission(
            ordinal=int(ordinal),
            status="ADMITTED",
            lattice_size=int(lattice_size),
            sampled_frames=tuple(labels),
            Y_by_f=dict(evidence.Y_by_f),
            disposition_by_f=dict(evidence.disposition_by_f),
            classification=str(evidence.classification),
            transport_transitions_recomputed=int(transitions),
            transport_max_tracer_deviation=float(max_deviation),
            global_tracer_conservation_max_drift=float(max_conservation_drift),
            mechanically_ineligible=bool(evidence.mechanically_ineligible),
            ineligibility_cause=cause,
            terminal_states=tuple(evidence.terminal_states),
            eligible_tracks=tuple(diagnostics),
            wrapping_at_t0=bool(wrapping_at_t0),
            wrapping_anywhere=bool(wrapping_anywhere),
            total_matter=totals_matter,
            total_tracer=totals_tracer,
            labelled_fraction=labelled_fraction,
            boundary_flux=tuple(flux),
        )
    except Exception as exc:  # noqa: BLE001 - every failure is a TECHNICAL_INVALID unit
        return _invalid(ordinal, lattice_size, exc, "ADMISSION_REFUSED")


def _largest_component_cells(components: Sequence[Any], shape: tuple[int, int]):
    """Largest non-wrapping component at enrolment, ties broken by canonical index."""
    eligible = [
        c
        for c in components
        if not bool(c.wraps_y or c.wraps_x) and int(c.area) * 2 <= shape[0] * shape[1]
    ]
    if not eligible:
        return None
    best = sorted(eligible, key=lambda c: (-int(c.area), int(c.index)))[0]
    return [int(x) for x in best.cells]


def verify_engine_provenance(
    world_directory: str | Path,
    *,
    law_spec,
    initial_state,
    backend: str = "vectorized",
) -> tuple[bool, str]:
    """Re-execute the canonical engine and require every persisted frame byte-identical.

    THIS FUNCTION TAKES ENGINE STEPS.  It is the only thing in this module that does, and
    it is the only thing that may conclude that the canonical engine produced an artefact.
    A handwritten or resealed world fails it: reproducing 1024 float64 lattices bit for bit
    requires actually running the engine on the declared law and initial condition.

    Within the declared trusted-local threat model this is a provenance proof.  It is not
    a proof against an adversary who can also run the engine; that adversary is out of
    scope here and is named rather than defended against.
    """
    directory = Path(world_directory)
    try:
        header, ledger = _load_ledger(directory)
    except PilotAdmissionRefusal as exc:
        return False, f"ledger unreadable: {exc}"
    shape = (int(header["frame_shape"][0]), int(header["frame_shape"][1]))
    transitions = int(header["transitions"])
    matter = ledger["matter"]
    tracer = ledger["tracer"]
    forward = ledger["forward"]
    reverse = ledger["reverse"]

    from .substrates.lattice_bond.engine import LatticeBondEngine
    from .substrates.lattice_bond.instrumentation import advance_passive_tracer

    threshold = float(MeasurementSpec().matter_threshold)
    sampled_positions = {
        int(label): position for position, label in enumerate(header["sampled_frames"])
    }
    engine = LatticeBondEngine(law_spec)
    state = initial_state.copy()
    if not np.array_equal(state.m, matter[0]):
        return False, "the persisted step-0 matter is not the declared initial condition"
    cohort = tracer[0].copy()
    for t in range(transitions):
        result = engine.step(state, None, backend=backend)
        fwd = result.ledger.matter_forward * result.ledger.matter_scale
        rev = result.ledger.matter_reverse * result.ledger.matter_scale
        if not np.array_equal(fwd, forward[t]):
            return False, f"persisted forward flow at transition {t} is not the engine's"
        if not np.array_equal(rev, reverse[t]):
            return False, f"persisted reverse flow at transition {t} is not the engine's"
        if not np.array_equal(result.state.m, matter[t + 1]):
            return False, f"persisted matter at step {t + 1} is not the engine's"
        if t + 1 in sampled_positions:
            position = sampled_positions[t + 1]
            persisted_mask = read_channel(directory, position, "mask", shape)
            if not np.array_equal(persisted_mask, result.state.m >= threshold):
                return False, f"persisted mask frame {position} is not the engine's matter"
        cohort = advance_passive_tracer(cohort, state.m, fwd, rev, result.state.m, law_spec.dt)
        if not np.array_equal(cohort, tracer[t + 1]):
            return False, f"persisted cohort at step {t + 1} is not the engine transport's"
        state = result.state
    return True, "every persisted frame, flow and cohort reproduced byte-identically"
