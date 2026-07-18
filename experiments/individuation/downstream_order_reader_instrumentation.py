"""Passive instrumentation for ``DOWNSTREAM-ORDER-READER-01``.

This module contains no seed family, history runner, outcome analyzer, or
decision rule.  It only provides:

* a mixin that copies the exact face-flux arrays returned to the frozen engine;
* the matched radius-core attractant ramp;
* the explicitly named mass-specific internal +x face-flux sum; and
* synthetic-only geometry/first-moment diagnostics.

The logger never replaces, scales, clips, or otherwise edits the array returned
to the engine's conservative transport calculation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from experiments.individuation.access_structure_noswap_operators import NoSwapClampEngine
from experiments.individuation.turnover_diag_engine import DiagEngine


@dataclass(frozen=True)
class FaceFluxRecord:
    """Read-only copy of one exact face-flux array used by an engine step."""

    input_step: int
    axis: int
    flux: np.ndarray


class PassiveFaceFluxLoggerMixin:
    """Record exact face fluxes while returning the unmodified live array.

    Put this mixin before an engine class in the method-resolution order.  The
    copied records are observational state owned by the instrument; they are not
    read by the physics, clamp, tracker, or endpoint calculation.
    """

    def __init__(self, *args, **kwargs):
        self._face_flux_records: list[FaceFluxRecord] = []
        self._logging_input_step: int | None = None
        super().__init__(*args, **kwargs)

    @property
    def face_flux_records(self) -> tuple[FaceFluxRecord, ...]:
        return tuple(self._face_flux_records)

    def clear_face_flux_records(self) -> None:
        self._face_flux_records.clear()

    def step(self, st):
        if self._logging_input_step is not None:
            raise RuntimeError("nested engine step is not supported by the passive flux logger")
        start = len(self._face_flux_records)
        self._logging_input_step = int(st.step)
        try:
            return super().step(st)
        except Exception:
            del self._face_flux_records[start:]
            raise
        finally:
            self._logging_input_step = None

    def _face_flux(self, rho, c, axis):
        flux = super()._face_flux(rho, c, axis)
        if self._logging_input_step is not None:
            recorded = np.array(flux, copy=True, order="C")
            recorded.flags.writeable = False
            self._face_flux_records.append(FaceFluxRecord(
                input_step=self._logging_input_step,
                axis=int(axis),
                flux=recorded,
            ))
        return flux


class PassiveFluxDiagEngine(PassiveFaceFluxLoggerMixin, DiagEngine):
    """Frozen diagnostic engine with passive exact-face-flux logging."""


class PassiveFluxNoSwapClampEngine(PassiveFaceFluxLoggerMixin, NoSwapClampEngine):
    """Qualified no-swap clamp engine with passive exact-face-flux logging."""


@dataclass(frozen=True)
class RampGeometry:
    core: np.ndarray
    signed_x: np.ndarray


def integer_disk_ramp_geometry(
    shape: tuple[int, int],
    center: tuple[int, int],
    radius: int,
) -> RampGeometry:
    """Return the periodic integer disk and frozen signed x ramp ``G=d_x/R``."""

    if len(shape) != 2 or any(int(n) <= 0 for n in shape):
        raise ValueError("shape must contain two positive dimensions")
    if radius <= 0 or 2 * radius >= min(shape):
        raise ValueError("radius must be positive and smaller than half the lattice")
    cy, cx = (int(center[0]), int(center[1]))
    if not (0 <= cy < shape[0] and 0 <= cx < shape[1]):
        raise ValueError("center must lie on the lattice")

    yy, xx = np.indices(shape)
    dy = ((yy - cy + shape[0] // 2) % shape[0]) - shape[0] // 2
    dx = ((xx - cx + shape[1] // 2) % shape[1]) - shape[1] // 2
    core = (dx * dx + dy * dy) <= radius * radius
    signed_x = np.zeros(shape, dtype=float)
    signed_x[core] = dx[core] / float(radius)
    core.flags.writeable = False
    signed_x.flags.writeable = False
    return RampGeometry(core=core, signed_x=signed_x)


def apply_matched_c_ramp(
    c: np.ndarray,
    geometry: RampGeometry,
    *,
    arm: int,
    epsilon_c: float,
) -> np.ndarray:
    """Return ``c + epsilon_c * 1_K * (1 + arm*G)`` without editing ``c``."""

    base = np.asarray(c)
    core = geometry.core
    signed_x = geometry.signed_x
    if base.ndim != 2 or base.shape != core.shape or base.shape != signed_x.shape:
        raise ValueError("c and ramp geometry must be congruent 2-D arrays")
    if arm not in (-1, 0, 1):
        raise ValueError("arm must be exactly -1, 0, or +1")
    if not np.isfinite(epsilon_c) or epsilon_c < 0:
        raise ValueError("epsilon_c must be finite and non-negative")
    if np.any(signed_x[~core] != 0.0) or np.max(np.abs(signed_x[core])) > 1.0:
        raise ValueError("invalid signed ramp geometry")
    if not np.isfinite(base).all() or np.any(base < 0.0):
        raise ValueError("the incoming c field must be finite and non-negative")

    addition = epsilon_c * core * (1.0 + arm * signed_x)
    if np.any(addition < 0.0):
        raise ValueError("matched ramp would subtract attractant")
    out = np.array(base, copy=True)
    out += addition
    if not np.isfinite(out).all() or np.any(out < 0.0):
        raise ValueError("matched ramp produced an invalid c field")
    return out


@dataclass(frozen=True)
class PositiveFaceMasks:
    internal: np.ndarray
    outgoing_boundary: np.ndarray
    incoming_boundary: np.ndarray


def positive_face_masks(core: np.ndarray, *, axis: int = -1) -> PositiveFaceMasks:
    """Partition positive-axis faces relative to ``core``.

    A flux entry at cell ``i`` is the oriented face from ``i`` to ``i+1``.
    Boundary masks are diagnostics and are not additional reader endpoints.
    """

    core = np.asarray(core, dtype=bool)
    if core.ndim != 2 or axis not in (-2, -1, 0, 1):
        raise ValueError("core must be 2-D and axis must select a spatial dimension")
    axis = axis % core.ndim
    neighbour = np.roll(core, -1, axis=axis)
    internal = core & neighbour
    outgoing = core & ~neighbour
    incoming = ~core & neighbour
    for mask in (internal, outgoing, incoming):
        mask.flags.writeable = False
    return PositiveFaceMasks(internal, outgoing, incoming)


def mass_specific_internal_x_face_flux_sum(
    face_flux_x: np.ndarray,
    core: np.ndarray,
    *,
    mass: float,
    dt: float,
) -> float:
    """Return ``dt/M * sum(F_x)`` on +x faces with both endpoints in ``core``.

    This is deliberately named an internal face-flux sum.  It equals a
    first-moment displacement only in a closed domain with the corresponding
    boundary flux equal to zero.
    """

    flux = np.asarray(face_flux_x)
    core = np.asarray(core, dtype=bool)
    if flux.ndim != 2 or flux.shape != core.shape or not np.isfinite(flux).all():
        raise ValueError("face flux and core must be finite congruent 2-D arrays")
    if not np.isfinite(mass) or mass <= 0.0:
        raise ValueError("mass must be finite and positive")
    if not np.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    internal = positive_face_masks(core, axis=-1).internal
    return float(dt * flux[internal].sum() / mass)


@dataclass(frozen=True)
class FaceFluxPartitionSums:
    internal: float
    outgoing_boundary: float
    incoming_boundary: float


def diagnostic_face_flux_partition(
    face_flux: np.ndarray,
    core: np.ndarray,
    *,
    axis: int = -1,
) -> FaceFluxPartitionSums:
    """Report internal and boundary sums for synthetic/validity diagnostics."""

    flux = np.asarray(face_flux)
    core = np.asarray(core, dtype=bool)
    if flux.ndim != 2 or flux.shape != core.shape or not np.isfinite(flux).all():
        raise ValueError("face flux and core must be finite congruent 2-D arrays")
    masks = positive_face_masks(core, axis=axis)
    return FaceFluxPartitionSums(
        internal=float(flux[masks.internal].sum()),
        outgoing_boundary=float(flux[masks.outgoing_boundary].sum()),
        incoming_boundary=float(flux[masks.incoming_boundary].sum()),
    )


@dataclass(frozen=True)
class ClosedFirstMomentTerms:
    internal_face_flux_integral: float
    first_moment_increment: float
    residual: float


def closed_first_moment_terms(
    face_flux: np.ndarray,
    *,
    dt: float,
    axis: int = -1,
) -> ClosedFirstMomentTerms:
    """Evaluate the discrete first-moment identity on a closed periodic fixture.

    The positive-axis wrap face must be exactly zero.  Under that closed-fixture
    condition, conservative transport gives

    ``sum(x * delta_rho) = dt * sum(non-wrap positive-axis face_flux)``.
    """

    flux = np.asarray(face_flux)
    if flux.ndim != 2 or not np.isfinite(flux).all():
        raise ValueError("face_flux must be a finite 2-D array")
    if not np.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    if axis not in (-2, -1, 0, 1):
        raise ValueError("axis must select a spatial dimension")
    axis = axis % flux.ndim
    wrap_slice = [slice(None)] * flux.ndim
    wrap_slice[axis] = -1
    if np.any(flux[tuple(wrap_slice)] != 0.0):
        raise ValueError("closed first-moment fixture requires zero wrap-boundary flux")

    delta_rho = -dt * (flux - np.roll(flux, 1, axis=axis))
    coordinates = np.arange(flux.shape[axis], dtype=float)
    reshape = [1] * flux.ndim
    reshape[axis] = flux.shape[axis]
    first_moment = float((delta_rho * coordinates.reshape(reshape)).sum())
    internal_integral = float(dt * flux.sum())
    return ClosedFirstMomentTerms(
        internal_face_flux_integral=internal_integral,
        first_moment_increment=first_moment,
        residual=float(first_moment - internal_integral),
    )
