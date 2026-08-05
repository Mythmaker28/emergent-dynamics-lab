"""Pilot acquisition: the real engine, the real cohort, plus a TRANSPORT LEDGER.

WHY A NEW ACQUISITION MODULE EXISTS
-----------------------------------
Gate G2 requires that the admission be able to RECOMPUTE the passive cohort for every
transition between enrolment and horizon, from persisted evidence alone.  The qualified
measurement bridge persists only the SAMPLED frames -- five channels every sixteen steps.
Between two sampled frames there are sixteen engine steps whose gross matter flows exist
only in memory and are then discarded.  From the bridge's output the tracer therefore
CANNOT be recomputed: the evidence is missing, not merely inconvenient.

That is a fact about the persistence design, not a defect of the bridge, which was never
asked for a transport ledger.  The honest options were to declare
``BLOCKED_PILOT_GATE_MISSING_TRANSPORT_LEDGER`` or to persist the missing evidence.  This
module persists it, for the pilot only.

WHAT IS PERSISTED, AND WHY EACH PIECE IS NECESSARY
--------------------------------------------------
``measurement_frames/`` -- byte-identical in name, layout and content to what
``run_measurement_bridge`` writes for the same law, initial state and schedule.  A
differential test asserts that equality, so the pilot measures the same object the
confirmatory design would measure.

``transport_ledger/`` -- one contiguous little-endian float64 file per quantity:

  ``matter.f64``   ``horizon + 1`` frames: the matter field at EVERY step 0..horizon.
                   Frame ``t`` is the pre-state of transition ``t`` and the post-state of
                   transition ``t-1``, so nothing is stored twice.
  ``tracer.f64``   ``horizon + 1`` frames: the cohort at every step.  Persisting it per
                   step makes each transition independently checkable, instead of only
                   the cumulative chain from enrolment to horizon.
  ``forward.f64``  ``horizon`` frames of shape (2, H, W): the SCALED gross forward flow
                   actually handed to the tracer, ``ledger.matter_forward * matter_scale``.
  ``reverse.f64``  the same for ``ledger.matter_reverse * matter_scale``.

``matter_scale`` is NOT persisted separately, and that is not a shortcut: the scaled flows
are exactly the arrays the transport consumed, and the admission independently verifies
``post = pre - dt * div(forward - reverse)`` against the persisted matter.  A forged scale
cannot survive that identity.  The pilot declares ``intervention = null``; the identity is
what binds the claim, not the declaration.

WHAT THIS MODULE DOES NOT CLAIM
-------------------------------
Persisting a ledger does not by itself prove the canonical engine produced it.  That is a
separate, explicitly engine-USING check --
:func:`edlab.route_e_pilot_admission.verify_engine_provenance` -- which re-executes the
engine from the persisted initial state and compares every frame byte for byte.  This
module writes evidence; it awards no trust.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .substrates.lattice_bond.engine import LatticeBondEngine, LatticeBondSpec
from .substrates.lattice_bond.instrumentation import (
    DetectorSpec,
    advance_passive_tracer,
    detect_components,
)
from .substrates.lattice_bond.engine import LatticeBondState
from .substrates.lattice_bond.future_prospective_measurement_bridge import (
    MeasurementSpec,
    _enrolled_cohort,
)
from . import route_e_pilot as _pilot
from . import route_e_strict as _strict

__all__ = [
    "LEDGER_DIRECTORY",
    "LEDGER_KIND",
    "FRAME_CHANNELS",
    "AcquisitionRefusal",
    "PilotWorldRecord",
    "acquire_pilot_world",
    "ledger_paths",
]

LEDGER_DIRECTORY = "transport_ledger"
LEDGER_KIND = "route-e-pilot-transport-ledger/v1"
FRAME_CHANNELS: tuple[str, ...] = ("bond", "mask", "matter", "resource", "tracer")


class AcquisitionRefusal(ValueError):
    def __init__(self, message: str, *, reason_code: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code


@dataclass(frozen=True)
class PilotWorldRecord:
    ordinal: int
    lattice_size: int
    horizon_steps: int
    cadence_steps: int
    sampled_frames: tuple[int, ...]
    steps_taken: int
    ledger_digests: Mapping[str, str]
    frame_digests: Mapping[str, str]
    provenance_sha256: str


def _float_bytes(array: np.ndarray) -> bytes:
    return np.ascontiguousarray(array, dtype="<f8").tobytes()


def _mask_bytes(mask: np.ndarray) -> bytes:
    return np.ascontiguousarray(mask, dtype=np.uint8).tobytes()


def _channel_relative_path(position: int, channel: str) -> str:
    return f"measurement_frames/frame_{position:06d}_{channel}.bin"


def _atomic_create(path: Path, payload: bytes) -> None:
    """O_CREAT|O_EXCL: a pilot never overwrites an artefact it already wrote."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(handle, payload)
    finally:
        os.close(handle)


def ledger_paths(world_directory: Path) -> dict[str, Path]:
    root = Path(world_directory) / LEDGER_DIRECTORY
    return {
        "matter": root / "matter.f64",
        "tracer": root / "tracer.f64",
        "forward": root / "forward.f64",
        "reverse": root / "reverse.f64",
    }


def acquire_pilot_world(
    world_directory: str | Path,
    *,
    law_spec: LatticeBondSpec,
    initial_state: LatticeBondState,
    sampled_frames: Sequence[int],
    measurement_spec: MeasurementSpec | None = None,
    backend: str = "vectorized",
    namespace: str,
    ordinal: int,
    persist_ledger: bool = True,
) -> PilotWorldRecord:
    """Run one pilot world: engine, cohort, sampled frames and transport ledger.

    The cohort is enrolled at the FIRST sampled frame, component-locally, by the
    bridge's own :func:`_enrolled_cohort` -- the identical function, imported, not a
    copy.  The tracer is advected by the bridge's own
    :func:`advance_passive_tracer`, with the identical scaled gross flows.  Nothing in
    the measurement path is reimplemented here; only the ledger is added.
    """
    if not isinstance(namespace, str) or not namespace.startswith(_pilot.PILOT_NAMESPACE_PREFIX):
        raise AcquisitionRefusal(
            f"a pilot world must live under a {_pilot.PILOT_NAMESPACE_PREFIX!r} namespace",
            reason_code="PILOT_NAMESPACE_PREFIX",
        )
    spec = MeasurementSpec() if measurement_spec is None else measurement_spec
    _strict.check_frozen_measurement_spec(spec)
    detector = spec.detector_spec()
    labels = [int(value) for value in sampled_frames]
    if not labels or labels[0] != 0 or labels != sorted(set(labels)):
        raise AcquisitionRefusal(
            "the schedule must start at 0 and be strictly increasing",
            reason_code="PILOT_SCHEDULE",
        )
    horizon = labels[-1]
    directory = Path(world_directory)
    directory.mkdir(parents=True, exist_ok=False)

    engine = LatticeBondEngine(law_spec)
    state = initial_state.copy()
    shape = (int(state.m.shape[0]), int(state.m.shape[1]))
    tracer: np.ndarray | None = None

    matter_chunks: list[bytes] = []
    tracer_chunks: list[bytes] = []
    forward_chunks: list[bytes] = []
    reverse_chunks: list[bytes] = []
    captures: list[tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    label_set = set(labels)
    steps_taken = 0

    for step_index in range(horizon + 1):
        if int(state.step) != step_index:
            raise AcquisitionRefusal(
                f"engine step {int(state.step)} does not equal {step_index}",
                reason_code="PILOT_SCHEDULE_DRIFT",
            )
        if tracer is None and step_index == labels[0]:
            tracer = _enrolled_cohort(state, detector)
        if persist_ledger:
            matter_chunks.append(_float_bytes(state.m))
            tracer_chunks.append(
                _float_bytes(tracer if tracer is not None else np.zeros(shape, dtype=np.float64))
            )
        if step_index in label_set:
            if tracer is None:  # pragma: no cover - the schedule starts at 0
                raise AcquisitionRefusal("no cohort at a sampled frame",
                                         reason_code="PILOT_COHORT_MISSING")
            captures.append(
                (step_index, state.m.copy(), state.n.copy(), state.b.copy(), tracer.copy())
            )
        if step_index == horizon:
            break
        pre = state
        result = engine.step(pre, None, backend=backend)
        ledger = result.ledger
        forward = ledger.matter_forward * ledger.matter_scale
        reverse = ledger.matter_reverse * ledger.matter_scale
        if persist_ledger:
            forward_chunks.append(_float_bytes(forward))
            reverse_chunks.append(_float_bytes(reverse))
        if tracer is not None:
            tracer = advance_passive_tracer(
                tracer, pre.m, forward, reverse, result.state.m, law_spec.dt
            )
        state = result.state
        steps_taken += 1

    for position, (label, matter, resource, bond, cohort) in enumerate(captures):
        payloads = {
            "bond": _float_bytes(bond),
            "mask": _mask_bytes(matter >= spec.matter_threshold),
            "matter": _float_bytes(matter),
            "resource": _float_bytes(resource),
            "tracer": _float_bytes(cohort),
        }
        for channel in FRAME_CHANNELS:
            _atomic_create(directory / _channel_relative_path(position, channel), payloads[channel])

    ledger_digests: dict[str, str] = {}
    if persist_ledger:
        paths = ledger_paths(directory)
        for name, chunks in (
            ("matter", matter_chunks),
            ("tracer", tracer_chunks),
            ("forward", forward_chunks),
            ("reverse", reverse_chunks),
        ):
            payload = b"".join(chunks)
            _atomic_create(paths[name], payload)
            ledger_digests[name] = hashlib.sha256(payload).hexdigest()
        header = {
            "cadence_steps": int(labels[1] - labels[0]) if len(labels) > 1 else 0,
            "dt": float(law_spec.dt),
            "frame_shape": [int(shape[0]), int(shape[1])],
            "horizon_steps": int(horizon),
            "intervention": None,
            "kind": LEDGER_KIND,
            "ledger_sha256": dict(sorted(ledger_digests.items())),
            "matter_frames": int(horizon + 1),
            "sampled_frames": [int(value) for value in labels],
            "transitions": int(horizon),
        }
        _atomic_create(
            directory / LEDGER_DIRECTORY / "LEDGER.json", _pilot.canonical_bytes(header)
        )

    frame_digests = {
        _channel_relative_path(position, channel): hashlib.sha256(
            (directory / _channel_relative_path(position, channel)).read_bytes()
        ).hexdigest()
        for position in range(len(captures))
        for channel in FRAME_CHANNELS
    }

    provenance = {
        "acquisition_module": "edlab.route_e_pilot_acquisition",
        "backend": str(backend),
        "engine_reexecution_verified": False,
        "fixture_class": "PILOT_EXPLORATORY_NON_CONFIRMATORY",
        "kind": _pilot.PILOT_PROVENANCE_KIND,
        "law_spec": {
            name: float(getattr(law_spec, name))
            for name in sorted(LatticeBondSpec.__dataclass_fields__)
        },
        "lattice_size": int(shape[0]),
        "mission": _pilot.PILOT_MISSION,
        "ordinal": int(ordinal),
        "output_namespace": str(namespace),
        "tag": _pilot.PILOT_PROVENANCE_TAG,
        "transport_ledger_persisted": bool(persist_ledger),
    }
    payload = _pilot.canonical_bytes(provenance)
    _atomic_create(directory / "PILOT_PROVENANCE.json", payload)

    return PilotWorldRecord(
        ordinal=int(ordinal),
        lattice_size=int(shape[0]),
        horizon_steps=int(horizon),
        cadence_steps=int(labels[1] - labels[0]) if len(labels) > 1 else 0,
        sampled_frames=tuple(labels),
        steps_taken=int(steps_taken),
        ledger_digests=dict(sorted(ledger_digests.items())),
        frame_digests=dict(sorted(frame_digests.items())),
        provenance_sha256=hashlib.sha256(payload).hexdigest(),
    )


# ======================================================================================
# SYNTHETIC, NON-SCIENTIFIC fixtures.  Public producer, declared synthetic, ENGINE-FREE.
# ======================================================================================
#
# Gate G1 needs a world in which a component genuinely persists AND its material is
# genuinely replaced -- a true ``Y = 1`` -- and a world in which it genuinely is not --
# a true ``Y = 0``.  Both are built here, and both are built by TRANSPORT, never by
# writing a residual by hand.
#
# The mechanism is a PURE EXCHANGE flow: ``forward == reverse`` everywhere, so the net
# matter flux is identically zero and the matter field never changes -- the component
# stays detected for the whole horizon by construction -- while the GROSS flows are
# non-zero, so the cohort still mixes with the surrounding unlabelled matter exactly as
# ``advance_passive_tracer`` prescribes.  The residual therefore falls from exactly 1 at
# enrolment toward the lattice-wide labelled fraction, purely by transport.
#
# WHY THESE ARE NOT ENGINE WORLDS, AND MUST NOT BE
# ------------------------------------------------
# Whether the CANONICAL ENGINE can produce a persisting, materially replaced component is
# the pilot's scientific question.  Building a fixture by searching the engine's law space
# for a Y = 1 and then presenting it as a gate would answer that question with a selected
# example, which is exactly the failure this programme keeps recording.  So the gate
# fixture is transport-constructed and declared synthetic, it carries
# ``fixture_class = SYNTHETIC_NON_SCIENTIFIC``, ``acquire_pilot_world`` refuses it, and
# ``verify_engine_provenance`` refuses it too.  The engine question stays with the pilot.

SYNTHETIC_FIXTURE_CLASS = "SYNTHETIC_NON_SCIENTIFIC"


def build_synthetic_transport_world(
    world_directory: str | Path,
    *,
    shape: tuple[int, int] = (16, 16),
    blob: Sequence[tuple[int, int]] = ((7, 7), (7, 8), (8, 7), (8, 8)),
    blob_value: float = 0.9,
    sea_value: float = 0.2,
    exchange: float = 0.05,
    horizon: int = 512,
    cadence: int = 64,
    dt: float = 1.0,
    namespace: str = "PILOT-SYNTHETIC",
    ordinal: int = 0,
    deplete_at_enrolment: float | None = None,
    leak_tracer_at: int | None = None,
    break_matter_at: int | None = None,
    late_birth_cells: Sequence[tuple[int, int]] | None = None,
    late_birth_drive: float = 0.02,
    late_birth_seed_value: float = 0.40,
    late_birth_steps: int = 64,
    drop_frame_position: int | None = None,
) -> dict[str, Any]:
    """A transport-consistent synthetic world.  Never an engine world, never scientific.

    ``exchange = 0`` gives a world with no material exchange at all, whose residual stays
    exactly 1 -- a true ``Y = 0`` reached by an OBSERVED failure inside a complete
    horizon, not by an incident.

    ``deplete_at_enrolment`` writes a cohort BELOW the matter at the first frame.  Such a
    world must be REFUSED by the admission: it would satisfy ``residual <= f`` without any
    replacement having occurred.  ``leak_tracer_at`` and ``break_matter_at`` are tamper
    handles for the gate tests; each must be detected, never scored.
    """
    directory = Path(world_directory)
    directory.mkdir(parents=True, exist_ok=False)
    labels = list(range(0, horizon + 1, cadence))
    matter = np.full(shape, float(sea_value), dtype=np.float64)
    for y, x in blob:
        matter[int(y), int(x)] = float(blob_value)
    if late_birth_cells:
        # a SUB-THRESHOLD seed: present in the matter field, invisible to the detector,
        # therefore never enrolled.  The drive lifts it above the threshold after the
        # enrolment frame, which is exactly the late-birth false positive under test.
        for y, x in late_birth_cells:
            matter[int(y), int(x)] = float(late_birth_seed_value)
    cohort = np.zeros(shape, dtype=np.float64)
    for y, x in blob:
        cohort[int(y), int(x)] = matter[int(y), int(x)]
    if deplete_at_enrolment is not None:
        cohort *= float(deplete_at_enrolment)

    base_flow = np.full((2, *shape), float(exchange), dtype=np.float64)

    # A LATE BIRTH is driven by a real net flux, never by editing the matter field: extra
    # forward flow on every face pointing INTO the target cells, extra reverse flow on
    # every face pointing out of them.  The matter field is then DERIVED from the
    # divergence identity, so the world stays transport-consistent while a brand new
    # component rises above the detection threshold after enrolment, carrying unlabelled
    # sea matter and therefore a residual near zero.  The frozen rule must refuse it.
    drive_forward = np.zeros_like(base_flow)
    drive_reverse = np.zeros_like(base_flow)
    if late_birth_cells:
        target = np.zeros(shape, dtype=bool)
        for y, x in late_birth_cells:
            target[int(y), int(x)] = True
        for axis in (0, 1):
            plus = np.roll(target, -1, axis=axis)
            drive_forward[axis][(~target) & plus] = float(late_birth_drive)
            drive_reverse[axis][target & (~plus)] = float(late_birth_drive)

    def _divergence_of(net: np.ndarray) -> np.ndarray:
        return (net[0] - np.roll(net[0], 1, axis=0)) + (net[1] - np.roll(net[1], 1, axis=1))

    def _advance(tracer: np.ndarray, pre: np.ndarray, fwd: np.ndarray, rev: np.ndarray) -> np.ndarray:
        fraction = np.divide(tracer, pre, out=np.zeros_like(tracer), where=pre > 0.0)
        flux = np.empty_like(fwd)
        for axis in (0, 1):
            flux[axis] = fwd[axis] * fraction - rev[axis] * np.roll(fraction, -1, axis=axis)
        return tracer - dt * _divergence_of(flux)

    matter_chunks = [_float_bytes(matter)]
    tracer_chunks = [_float_bytes(cohort)]
    forward_chunks: list[bytes] = []
    reverse_chunks: list[bytes] = []
    captures: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    if 0 in labels:
        captures[0] = (matter.copy(), cohort.copy())
    for step in range(horizon):
        driving = bool(late_birth_cells) and step < int(late_birth_steps)
        fwd = base_flow + (drive_forward if driving else 0.0)
        rev = base_flow + (drive_reverse if driving else 0.0)
        forward_chunks.append(_float_bytes(fwd))
        reverse_chunks.append(_float_bytes(rev))
        pre = matter
        cohort = _advance(cohort, pre, fwd, rev)
        if leak_tracer_at is not None and step == int(leak_tracer_at):
            cohort = cohort * 0.5  # destroys conservation: must be detected
        matter = pre - dt * _divergence_of(fwd - rev)
        written_matter = matter.copy()
        if break_matter_at is not None and step == int(break_matter_at):
            written_matter = written_matter + 0.01  # inconsistent with the persisted flux
            matter = written_matter
        matter_chunks.append(_float_bytes(written_matter))
        tracer_chunks.append(_float_bytes(cohort))
        if (step + 1) in labels:
            captures[step + 1] = (written_matter.copy(), cohort.copy())

    for position, label in enumerate(labels):
        if drop_frame_position is not None and position == int(drop_frame_position):
            continue  # a missing sampled frame: an incident, never a score
        frame_matter, frame_tracer = captures[label]
        payloads = {
            "bond": _float_bytes(np.zeros((2, *shape))),
            "mask": _mask_bytes(frame_matter >= 0.45),
            "matter": _float_bytes(frame_matter),
            "resource": _float_bytes(np.full(shape, 0.5)),
            "tracer": _float_bytes(frame_tracer),
        }
        for channel in FRAME_CHANNELS:
            _atomic_create(directory / _channel_relative_path(position, channel), payloads[channel])

    paths = ledger_paths(directory)
    digests: dict[str, str] = {}
    for name, chunks in (
        ("matter", matter_chunks),
        ("tracer", tracer_chunks),
        ("forward", forward_chunks),
        ("reverse", reverse_chunks),
    ):
        payload = b"".join(chunks)
        _atomic_create(paths[name], payload)
        digests[name] = hashlib.sha256(payload).hexdigest()
    header = {
        "cadence_steps": int(cadence),
        "dt": float(dt),
        "frame_shape": [int(shape[0]), int(shape[1])],
        "horizon_steps": int(horizon),
        "intervention": None,
        "kind": LEDGER_KIND,
        "ledger_sha256": dict(sorted(digests.items())),
        "matter_frames": int(horizon + 1),
        "sampled_frames": [int(v) for v in labels],
        "transitions": int(horizon),
    }
    _atomic_create(directory / LEDGER_DIRECTORY / "LEDGER.json", _pilot.canonical_bytes(header))
    provenance = {
        "acquisition_module": "edlab.route_e_pilot_acquisition.build_synthetic_transport_world",
        "backend": "none",
        "engine_reexecution_verified": False,
        "fixture_class": SYNTHETIC_FIXTURE_CLASS,
        "kind": _pilot.PILOT_PROVENANCE_KIND,
        "law_spec": {},
        "lattice_size": int(shape[0]),
        "mission": _pilot.PILOT_MISSION,
        "ordinal": int(ordinal),
        "output_namespace": str(namespace),
        "tag": _pilot.PILOT_PROVENANCE_TAG,
        "transport_ledger_persisted": True,
    }
    _atomic_create(directory / "PILOT_PROVENANCE.json", _pilot.canonical_bytes(provenance))
    return {"sampled_frames": labels, "shape": shape, "ledger_sha256": digests}
