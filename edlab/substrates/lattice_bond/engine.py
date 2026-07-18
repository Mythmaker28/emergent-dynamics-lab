"""Code-only Candidate-C lattice-bond engine.

The engine contains no entity detector, tracker, membrane class, history field,
scientific response, or search procedure.  It evolves three physical fields on
a periodic square lattice:

``m``
    bounded mobile matter on cells;
``n``
    bounded resource on cells, also used as explicit bond fuel;
``b``
    a structural bond fraction on every positive-y and positive-x face.

Every transported face value is stored once.  The exact same float is applied
with opposite signs to its two endpoints.  Bond formation consumes endpoint
resource, rupture releases stored bond energy to heat, and maintenance consumes
no additional external resource: the exact simultaneous on/off turnover that
maintains a bond is exposed as internally recycled work.  A complete per-step
ledger is returned.

This module is a mechanical substrate qualification target only.  Direct flux
and bond terms are compliance diagnostics, never scientific outcomes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
import struct
from typing import Any, Iterable, Literal

import numpy as np


FACE_AXES = (0, 1)
Backend = Literal["vectorized", "reference"]


class AdmissibilityError(ValueError):
    """Raised before an update when state or timestep leaves the frozen domain."""


def _finite_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")


@dataclass(frozen=True)
class LatticeBondSpec:
    """Frozen Stage-A local law and compact admissible domain.

    There is deliberately no lattice size, component size, contour, target,
    identity, or tracker parameter.  The representable timestep limit is the
    predecessor of the analytic bound, providing one floating-point ULP of
    slack without clipping any state output.
    """

    dt: float = 0.05
    m_max: float = 1.0
    n_max: float = 1.0
    kappa_m: float = 0.05
    theta_m: float = 0.5
    theta_n: float = 0.5
    resource_diffusivity: float = 0.10
    resource_leak_floor: float = 0.05
    epsilon_b: float = 0.25
    k_on: float = 0.30
    k_off: float = 0.05
    k_tension: float = 0.15

    def __post_init__(self) -> None:
        if not math.isfinite(self.dt) or self.dt <= 0.0:
            raise ValueError("dt must be finite and positive")
        if not math.isfinite(self.m_max) or self.m_max <= 0.0:
            raise ValueError("m_max must be finite and positive")
        if not math.isfinite(self.n_max) or self.n_max <= 0.0:
            raise ValueError("n_max must be finite and positive")
        for name in (
            "kappa_m",
            "theta_m",
            "theta_n",
            "resource_diffusivity",
            "epsilon_b",
            "k_on",
            "k_off",
            "k_tension",
        ):
            _finite_nonnegative(name, float(getattr(self, name)))
        if not math.isfinite(self.resource_leak_floor) or not 0.0 <= self.resource_leak_floor <= 1.0:
            raise ValueError("resource_leak_floor must lie in [0,1]")
        if self.dt > self.admissible_dt_limit:
            raise AdmissibilityError(
                f"dt={self.dt!r} exceeds frozen admissible limit {self.admissible_dt_limit!r}"
            )

    @property
    def affinity_span(self) -> float:
        return self.theta_m * self.m_max + self.theta_n * self.n_max

    @property
    def matter_dt_bound(self) -> float:
        if self.kappa_m == 0.0:
            return math.inf
        return 1.0 / (4.0 * self.kappa_m * math.exp(0.5 * self.affinity_span))

    @property
    def resource_bond_dt_bound(self) -> float:
        rate = 4.0 * self.resource_diffusivity + 2.0 * self.epsilon_b * self.k_on / self.n_max
        if rate == 0.0:
            return math.inf
        return 1.0 / rate

    @property
    def analytic_dt_bound(self) -> float:
        return min(self.matter_dt_bound, self.resource_bond_dt_bound)

    @property
    def admissible_dt_limit(self) -> float:
        bound = self.analytic_dt_bound
        return math.nextafter(bound, 0.0) if math.isfinite(bound) else math.inf

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.update(
            affinity_span=self.affinity_span,
            matter_dt_bound=self.matter_dt_bound,
            resource_bond_dt_bound=self.resource_bond_dt_bound,
            analytic_dt_bound=self.analytic_dt_bound,
            admissible_dt_limit=self.admissible_dt_limit,
        )
        return data


@dataclass
class LatticeBondState:
    """Complete Stage-A physical state; arrays are never modified in place."""

    m: np.ndarray
    n: np.ndarray
    b: np.ndarray
    step: int = 0

    @property
    def shape(self) -> tuple[int, int]:
        return tuple(int(v) for v in self.m.shape)  # type: ignore[return-value]

    @property
    def face_shape(self) -> tuple[int, int, int]:
        return (2, *self.shape)

    def validate(self, spec: LatticeBondSpec) -> None:
        if self.m.ndim != 2 or min(self.m.shape) < 2:
            raise AdmissibilityError("m must be a two-dimensional lattice with both dimensions >=2")
        if self.n.shape != self.m.shape:
            raise AdmissibilityError("n must have the same cell shape as m")
        if self.b.shape != self.face_shape:
            raise AdmissibilityError("b must have shape (2,H,W)")
        if self.step < 0 or not isinstance(self.step, (int, np.integer)):
            raise AdmissibilityError("step must be a nonnegative integer")
        for name, array in (("m", self.m), ("n", self.n), ("b", self.b)):
            if array.dtype != np.float64:
                raise AdmissibilityError(f"{name} must have dtype float64")
            if not np.isfinite(array).all():
                raise AdmissibilityError(f"{name} must contain only finite values")
        if float(np.min(self.m)) < 0.0 or float(np.max(self.m)) > spec.m_max:
            raise AdmissibilityError("m leaves [0,m_max]")
        if float(np.min(self.n)) < 0.0 or float(np.max(self.n)) > spec.n_max:
            raise AdmissibilityError("n leaves [0,n_max]")
        if float(np.min(self.b)) < 0.0 or float(np.max(self.b)) > 1.0:
            raise AdmissibilityError("b leaves [0,1]")

    def copy(self) -> "LatticeBondState":
        return LatticeBondState(self.m.copy(), self.n.copy(), self.b.copy(), int(self.step))

    def canonical_bytes(self) -> bytes:
        header = struct.pack("<3q", self.shape[0], self.shape[1], int(self.step))
        return header + b"".join(
            np.ascontiguousarray(array, dtype="<f8").tobytes()
            for array in (self.m, self.n, self.b)
        )


def _readonly_scale(name: str, value: np.ndarray) -> np.ndarray:
    candidate = np.array(value, dtype=np.float64, copy=True, order="C")
    if candidate.ndim != 3 or candidate.shape[0] != 2:
        raise ValueError(f"{name} must have shape (2,H,W)")
    if not np.isfinite(candidate).all() or float(np.min(candidate)) < 0.0 or float(np.max(candidate)) > 1.0:
        raise ValueError(f"{name} must contain finite coefficients in [0,1]")
    shape = candidate.shape
    # Immutable bytes, rather than an owning ndarray, prevent callers from
    # re-enabling NumPy's WRITEABLE flag after plan construction.
    array = np.frombuffer(candidate.astype("<f8", copy=False).tobytes(), dtype="<f8").reshape(shape)
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class FaceIntervention:
    """Immutable fixed-face coefficient plan for pre-existing transported terms."""

    matter_scale: np.ndarray
    resource_scale: np.ndarray

    def __post_init__(self) -> None:
        matter = _readonly_scale("matter_scale", self.matter_scale)
        resource = _readonly_scale("resource_scale", self.resource_scale)
        if matter.shape != resource.shape:
            raise ValueError("matter_scale and resource_scale must have identical shapes")
        object.__setattr__(self, "matter_scale", matter)
        object.__setattr__(self, "resource_scale", resource)

    @classmethod
    def open(cls, shape: tuple[int, int]) -> "FaceIntervention":
        face_shape = (2, *shape)
        return cls(np.ones(face_shape, dtype=np.float64), np.ones(face_shape, dtype=np.float64))

    @classmethod
    def from_cuts(
        cls,
        shape: tuple[int, int],
        *,
        matter_faces: Iterable[tuple[int, int, int]] = (),
        resource_faces: Iterable[tuple[int, int, int]] = (),
    ) -> "FaceIntervention":
        matter = np.ones((2, *shape), dtype=np.float64)
        resource = np.ones((2, *shape), dtype=np.float64)
        for target, faces_to_cut in ((matter, matter_faces), (resource, resource_faces)):
            for axis, y, x in faces_to_cut:
                if axis not in FACE_AXES or not 0 <= y < shape[0] or not 0 <= x < shape[1]:
                    raise ValueError(f"invalid fixed face {(axis, y, x)!r} for shape {shape!r}")
                target[axis, y, x] = 0.0
        return cls(matter, resource)

    @property
    def shape(self) -> tuple[int, int]:
        return (int(self.matter_scale.shape[1]), int(self.matter_scale.shape[2]))

    def compose(self, other: "FaceIntervention") -> "FaceIntervention":
        if self.matter_scale.shape != other.matter_scale.shape:
            raise ValueError("cannot compose plans with different face shapes")
        return FaceIntervention(
            self.matter_scale * other.matter_scale,
            self.resource_scale * other.resource_scale,
        )

    def canonical_bytes(self) -> bytes:
        header = struct.pack("<2q", *self.shape)
        return header + np.ascontiguousarray(self.matter_scale, dtype="<f8").tobytes() + np.ascontiguousarray(
            self.resource_scale, dtype="<f8"
        ).tobytes()


@dataclass(frozen=True)
class FaceTerms:
    affinity: np.ndarray
    matter_forward: np.ndarray
    matter_reverse: np.ndarray
    matter_natural: np.ndarray
    resource_permeability: np.ndarray
    resource_natural: np.ndarray
    bond_cue: np.ndarray
    bond_tension: np.ndarray
    r_on: np.ndarray
    r_off: np.ndarray
    bond_next: np.ndarray
    gross_formation: np.ndarray
    gross_rupture: np.ndarray
    gross_formation_work: np.ndarray
    gross_rupture_release: np.ndarray
    gross_weakening_release: np.ndarray
    gross_dissolution_release: np.ndarray
    maintenance_recycled_work: np.ndarray
    formation_fuel: np.ndarray
    rupture_heat: np.ndarray
    weakening_heat: np.ndarray
    dissolution_heat: np.ndarray


@dataclass(frozen=True)
class StepLedger:
    affinity: np.ndarray
    matter_forward: np.ndarray
    matter_reverse: np.ndarray
    matter_natural: np.ndarray
    matter_active: np.ndarray
    matter_missing: np.ndarray
    resource_permeability: np.ndarray
    resource_natural: np.ndarray
    resource_active: np.ndarray
    resource_missing: np.ndarray
    bond_cue: np.ndarray
    bond_tension: np.ndarray
    r_on: np.ndarray
    r_off: np.ndarray
    gross_formation: np.ndarray
    gross_rupture: np.ndarray
    gross_formation_work: np.ndarray
    gross_rupture_release: np.ndarray
    gross_weakening_release: np.ndarray
    gross_dissolution_release: np.ndarray
    maintenance_recycled_work: np.ndarray
    formation_fuel: np.ndarray
    rupture_heat: np.ndarray
    weakening_heat: np.ndarray
    dissolution_heat: np.ndarray
    matter_missing_from_delta: np.ndarray
    matter_missing_to_delta: np.ndarray
    resource_missing_from_delta: np.ndarray
    resource_missing_to_delta: np.ndarray
    matter_scale: np.ndarray
    resource_scale: np.ndarray
    initial_matter: float
    final_matter: float
    matter_residual: float
    initial_stored_energy: float
    final_stored_energy: float
    total_rupture_heat: float
    total_maintenance_recycled_work: float
    energy_residual: float
    controller_onset_energy_jump: float

    def canonical_bytes(self) -> bytes:
        chunks: list[bytes] = []
        for item in fields(self):
            value = getattr(self, item.name)
            if isinstance(value, np.ndarray):
                chunks.append(np.ascontiguousarray(value, dtype="<f8").tobytes())
            else:
                chunks.append(struct.pack("<d", float(value)))
        return b"".join(chunks)


@dataclass(frozen=True)
class StepResult:
    state: LatticeBondState
    ledger: StepLedger

    def canonical_bytes(self) -> bytes:
        return self.state.canonical_bytes() + self.ledger.canonical_bytes()


def _positive_neighbour(array: np.ndarray, face_axis: int) -> np.ndarray:
    return np.roll(array, -1, axis=face_axis)


def _divergence(face_values: np.ndarray) -> np.ndarray:
    return (face_values[0] - np.roll(face_values[0], 1, axis=0)) + (
        face_values[1] - np.roll(face_values[1], 1, axis=1)
    )


def _incident_sum(face_values: np.ndarray) -> np.ndarray:
    return (face_values[0] + np.roll(face_values[0], 1, axis=0)) + (
        face_values[1] + np.roll(face_values[1], 1, axis=1)
    )


def _fsum(array: np.ndarray) -> float:
    return math.fsum(float(value) for value in np.ravel(array, order="C"))


class LatticeBondEngine:
    """Uniform fixed-face Stage-A update with vectorized and scalar paths."""

    def __init__(self, spec: LatticeBondSpec | None = None):
        self.spec = spec if spec is not None else LatticeBondSpec()

    def face_terms(self, state: LatticeBondState, *, backend: Backend = "vectorized") -> FaceTerms:
        state.validate(self.spec)
        if backend == "vectorized":
            return self._face_terms_vectorized(state)
        if backend == "reference":
            return self._face_terms_reference(state)
        raise ValueError("backend must be 'vectorized' or 'reference'")

    def _face_terms_vectorized(self, state: LatticeBondState) -> FaceTerms:
        sp = self.spec
        m, n, b = state.m, state.n, state.b
        affinity = sp.theta_m * 0.25 * (
            np.roll(m, 1, axis=0)
            + np.roll(m, -1, axis=0)
            + np.roll(m, 1, axis=1)
            + np.roll(m, -1, axis=1)
        ) + sp.theta_n * n

        shape = state.face_shape
        matter_forward = np.empty(shape, dtype=np.float64)
        matter_reverse = np.empty(shape, dtype=np.float64)
        resource_permeability = sp.resource_leak_floor + (1.0 - sp.resource_leak_floor) * (1.0 - b)
        resource_natural = np.empty(shape, dtype=np.float64)
        bond_cue = np.empty(shape, dtype=np.float64)
        bond_tension = np.empty(shape, dtype=np.float64)

        for face_axis in FACE_AXES:
            m_plus = _positive_neighbour(m, face_axis)
            n_plus = _positive_neighbour(n, face_axis)
            a_plus = _positive_neighbour(affinity, face_axis)
            conductance = 1.0 - b[face_axis]
            matter_forward[face_axis] = (
                sp.kappa_m
                * conductance
                * m
                * (1.0 - m_plus / sp.m_max)
                * np.exp(0.5 * (a_plus - affinity))
            )
            matter_reverse[face_axis] = (
                sp.kappa_m
                * conductance
                * m_plus
                * (1.0 - m / sp.m_max)
                * np.exp(0.5 * (affinity - a_plus))
            )
            resource_natural[face_axis] = (
                sp.resource_diffusivity * resource_permeability[face_axis] * (n - n_plus)
            )
            bond_cue[face_axis] = (
                (m / sp.m_max) * (m_plus / sp.m_max) * (np.minimum(n, n_plus) / sp.n_max)
            )
            bond_tension[face_axis] = np.abs(m - m_plus) / sp.m_max

        matter_natural = matter_forward - matter_reverse
        r_on = sp.k_on * bond_cue
        tension_rate = sp.k_tension * bond_tension
        r_off = sp.k_off + tension_rate
        total_rate = r_on + r_off
        relaxation = np.zeros_like(total_rate)
        np.subtract(1.0, np.exp(-total_rate * sp.dt), out=relaxation, where=total_rate > 0.0)
        on_share = np.zeros_like(total_rate)
        off_share = np.zeros_like(total_rate)
        np.divide(r_on, total_rate, out=on_share, where=total_rate > 0.0)
        np.divide(r_off, total_rate, out=off_share, where=total_rate > 0.0)
        gross_formation = (1.0 - b) * on_share * relaxation
        gross_rupture = b * off_share * relaxation
        bond_next = b + gross_formation - gross_rupture
        gross_formation_work = sp.epsilon_b * gross_formation
        gross_rupture_release = sp.epsilon_b * gross_rupture
        maintenance_recycled_work = np.minimum(gross_formation_work, gross_rupture_release)
        formation_fuel = gross_formation_work - maintenance_recycled_work
        rupture_heat = gross_rupture_release - maintenance_recycled_work
        weakening_share = np.zeros_like(r_off)
        dissolution_share = np.zeros_like(r_off)
        np.divide(tension_rate, r_off, out=weakening_share, where=r_off > 0.0)
        np.divide(sp.k_off, r_off, out=dissolution_share, where=r_off > 0.0)
        weakening_heat = rupture_heat * weakening_share
        dissolution_heat = rupture_heat * dissolution_share
        gross_weakening_release = gross_rupture_release * weakening_share
        gross_dissolution_release = gross_rupture_release * dissolution_share
        return FaceTerms(
            affinity,
            matter_forward,
            matter_reverse,
            matter_natural,
            resource_permeability,
            resource_natural,
            bond_cue,
            bond_tension,
            r_on,
            r_off,
            bond_next,
            gross_formation,
            gross_rupture,
            gross_formation_work,
            gross_rupture_release,
            gross_weakening_release,
            gross_dissolution_release,
            maintenance_recycled_work,
            formation_fuel,
            rupture_heat,
            weakening_heat,
            dissolution_heat,
        )

    def _face_terms_reference(self, state: LatticeBondState) -> FaceTerms:
        sp = self.spec
        h, w = state.shape
        m, n, b = state.m, state.n, state.b
        affinity = np.empty_like(m)
        for y in range(h):
            for x in range(w):
                neighbour_sum = m[(y - 1) % h, x] + m[(y + 1) % h, x] + m[y, (x - 1) % w] + m[y, (x + 1) % w]
                affinity[y, x] = sp.theta_m * 0.25 * neighbour_sum + sp.theta_n * n[y, x]

        arrays = [np.empty(state.face_shape, dtype=np.float64) for _ in range(20)]
        (
            matter_forward,
            matter_reverse,
            resource_permeability,
            resource_natural,
            bond_cue,
            bond_tension,
            r_on,
            r_off,
            bond_next,
            gross_formation,
            gross_rupture,
            gross_formation_work,
            gross_rupture_release,
            gross_weakening_release,
            gross_dissolution_release,
            maintenance_recycled_work,
            formation_fuel,
            rupture_heat,
            weakening_heat,
            dissolution_heat,
        ) = arrays
        for face_axis in FACE_AXES:
            for y in range(h):
                for x in range(w):
                    yp = (y + 1) % h if face_axis == 0 else y
                    xp = (x + 1) % w if face_axis == 1 else x
                    bi = b[face_axis, y, x]
                    mi, mj = m[y, x], m[yp, xp]
                    ni, nj = n[y, x], n[yp, xp]
                    ai, aj = affinity[y, x], affinity[yp, xp]
                    conductance = 1.0 - bi
                    matter_forward[face_axis, y, x] = sp.kappa_m * conductance * mi * (1.0 - mj / sp.m_max) * math.exp(0.5 * (aj - ai))
                    matter_reverse[face_axis, y, x] = sp.kappa_m * conductance * mj * (1.0 - mi / sp.m_max) * math.exp(0.5 * (ai - aj))
                    permeability = sp.resource_leak_floor + (1.0 - sp.resource_leak_floor) * (1.0 - bi)
                    resource_permeability[face_axis, y, x] = permeability
                    resource_natural[face_axis, y, x] = sp.resource_diffusivity * permeability * (ni - nj)
                    cue = (mi / sp.m_max) * (mj / sp.m_max) * (min(ni, nj) / sp.n_max)
                    tension = abs(mi - mj) / sp.m_max
                    ron = sp.k_on * cue
                    tension_off = sp.k_tension * tension
                    roff = sp.k_off + tension_off
                    total = ron + roff
                    relax = 1.0 - math.exp(-total * sp.dt) if total > 0.0 else 0.0
                    gf = (1.0 - bi) * (ron / total) * relax if total > 0.0 else 0.0
                    gr = bi * (roff / total) * relax if total > 0.0 else 0.0
                    r_on[face_axis, y, x] = ron
                    r_off[face_axis, y, x] = roff
                    bond_cue[face_axis, y, x] = cue
                    bond_tension[face_axis, y, x] = tension
                    bond_next[face_axis, y, x] = bi + gf - gr
                    gross_formation[face_axis, y, x] = gf
                    gross_rupture[face_axis, y, x] = gr
                    gfw = sp.epsilon_b * gf
                    grr = sp.epsilon_b * gr
                    recycled = min(gfw, grr)
                    gross_formation_work[face_axis, y, x] = gfw
                    gross_rupture_release[face_axis, y, x] = grr
                    gross_weakening_release[face_axis, y, x] = grr * tension_off / roff if roff > 0.0 else 0.0
                    gross_dissolution_release[face_axis, y, x] = grr * sp.k_off / roff if roff > 0.0 else 0.0
                    maintenance_recycled_work[face_axis, y, x] = recycled
                    formation_fuel[face_axis, y, x] = gfw - recycled
                    rh = grr - recycled
                    rupture_heat[face_axis, y, x] = rh
                    weakening_heat[face_axis, y, x] = rh * tension_off / roff if roff > 0.0 else 0.0
                    dissolution_heat[face_axis, y, x] = rh * sp.k_off / roff if roff > 0.0 else 0.0
        matter_natural = matter_forward - matter_reverse
        return FaceTerms(
            affinity,
            matter_forward,
            matter_reverse,
            matter_natural,
            resource_permeability,
            resource_natural,
            bond_cue,
            bond_tension,
            r_on,
            r_off,
            bond_next,
            gross_formation,
            gross_rupture,
            gross_formation_work,
            gross_rupture_release,
            gross_weakening_release,
            gross_dissolution_release,
            maintenance_recycled_work,
            formation_fuel,
            rupture_heat,
            weakening_heat,
            dissolution_heat,
        )

    def step(
        self,
        state: LatticeBondState,
        intervention: FaceIntervention | None = None,
        *,
        backend: Backend = "vectorized",
    ) -> StepResult:
        state.validate(self.spec)
        plan = FaceIntervention.open(state.shape) if intervention is None else intervention
        if plan.shape != state.shape:
            raise ValueError("intervention plan shape does not match state")
        terms = self.face_terms(state, backend=backend)
        matter_active = terms.matter_natural * plan.matter_scale
        resource_active = terms.resource_natural * plan.resource_scale
        matter_missing = terms.matter_natural - matter_active
        resource_missing = terms.resource_natural - resource_active
        bond_debit = terms.formation_fuel

        if backend == "vectorized":
            m_next = state.m - self.spec.dt * _divergence(matter_active)
            n_next = state.n - self.spec.dt * _divergence(resource_active) - 0.5 * _incident_sum(bond_debit)
        elif backend == "reference":
            m_next = state.m.copy()
            n_next = state.n.copy()
            h, w = state.shape
            for face_axis in FACE_AXES:
                for y in range(h):
                    for x in range(w):
                        yp = (y + 1) % h if face_axis == 0 else y
                        xp = (x + 1) % w if face_axis == 1 else x
                        jm = matter_active[face_axis, y, x]
                        jn = resource_active[face_axis, y, x]
                        debit = 0.5 * bond_debit[face_axis, y, x]
                        m_next[y, x] -= self.spec.dt * jm
                        m_next[yp, xp] += self.spec.dt * jm
                        n_next[y, x] -= self.spec.dt * jn + debit
                        n_next[yp, xp] += self.spec.dt * jn - debit
        else:
            raise ValueError("backend must be 'vectorized' or 'reference'")

        tolerance = 1e-12 + 1e-10 * max(self.spec.m_max, self.spec.n_max, 1.0)
        if float(np.min(m_next)) < -tolerance or float(np.max(m_next)) > self.spec.m_max + tolerance:
            raise ArithmeticError("declared matter timestep bound failed")
        if float(np.min(n_next)) < -tolerance or float(np.max(n_next)) > self.spec.n_max + tolerance:
            raise ArithmeticError("declared resource/bond timestep bound failed")
        if float(np.min(terms.bond_next)) < -tolerance or float(np.max(terms.bond_next)) > 1.0 + tolerance:
            raise ArithmeticError("exact bond relaxation left [0,1]")

        next_state = LatticeBondState(m_next, n_next, terms.bond_next.copy(), int(state.step) + 1)
        initial_matter = _fsum(state.m)
        final_matter = _fsum(m_next)
        initial_energy = _fsum(state.n) + self.spec.epsilon_b * _fsum(state.b)
        final_energy = _fsum(n_next) + self.spec.epsilon_b * _fsum(terms.bond_next)
        total_rupture = _fsum(terms.rupture_heat)
        total_maintenance_recycled = _fsum(terms.maintenance_recycled_work)
        ledger = StepLedger(
            terms.affinity.copy(),
            terms.matter_forward.copy(),
            terms.matter_reverse.copy(),
            terms.matter_natural.copy(),
            matter_active.copy(),
            matter_missing.copy(),
            terms.resource_permeability.copy(),
            terms.resource_natural.copy(),
            resource_active.copy(),
            resource_missing.copy(),
            terms.bond_cue.copy(),
            terms.bond_tension.copy(),
            terms.r_on.copy(),
            terms.r_off.copy(),
            terms.gross_formation.copy(),
            terms.gross_rupture.copy(),
            terms.gross_formation_work.copy(),
            terms.gross_rupture_release.copy(),
            terms.gross_weakening_release.copy(),
            terms.gross_dissolution_release.copy(),
            terms.maintenance_recycled_work.copy(),
            terms.formation_fuel.copy(),
            terms.rupture_heat.copy(),
            terms.weakening_heat.copy(),
            terms.dissolution_heat.copy(),
            -self.spec.dt * matter_missing.copy(),
            self.spec.dt * matter_missing.copy(),
            -self.spec.dt * resource_missing.copy(),
            self.spec.dt * resource_missing.copy(),
            plan.matter_scale.copy(),
            plan.resource_scale.copy(),
            initial_matter,
            final_matter,
            final_matter - initial_matter,
            initial_energy,
            final_energy,
            total_rupture,
            total_maintenance_recycled,
            final_energy + total_rupture - initial_energy,
            0.0,
        )
        return StepResult(next_state, ledger)
