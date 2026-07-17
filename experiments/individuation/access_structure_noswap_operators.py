"""ACCESS-STRUCTURE-00 Phase 0.6B — NO-TRANSPLANT causal-access primitives (DEV-only).

This module is the no-swap counterpart to ``access_structure_operators.py``.  It
NEVER moves a foreign spatial field into a foreign environment: there is no core
exchange, no reciprocal graft, no on-manifold body transplant.  It therefore
cannot create the 22.87x boundary seam qualified-but-rejected in Phase 0.5.

The single novel mechanism is an **in-place directional interface clamp**.  All
spatial coupling in the frozen ``MultiChannelMemoryEngine`` is nearest-neighbour
(``np.roll +/- 1``, ``lap``, ``_face_flux``, ``_tmean``); the only non-local term
is the world-global scalar ``up_ref = mean(uptake over alive cells)``.  Because of
this, severing the core ``C`` from the environment ``E`` is EXACT: overwrite the
one-cell stencil collar ``H`` with a predeclared, outcome-independent source value
after every engine step.  Information from ``E`` reaches ``H`` during a step but is
discarded by the overwrite before it can cross into ``C``; ``C``'s interior then
evolves under the true engine, driven only by the standardized collar.

This is a Dirichlet boundary condition, not a closed operation: it is deliberately
non-conservative at the collar, and that is measured, not hidden.  With
``driver=None`` and both diagnostic flags ``False`` the clamp engine is
BYTE-IDENTICAL to the base engine (inherited from the validated ``DiagEngine``).

Scope guards
------------
* Callers must pass seeds from the already-open DEV namespace 50001--50010.
* Nothing here tests where a causal state resides.  It qualifies operator
  mechanics only (disturbance, conservation, isolation, injection, phase).
* It does not import, edit, or call the transplant operator.

Companion runner: ``access_structure_noswap_dev_feasibility.py``.
Design: ``docs/individuation/ACCESS_STRUCTURE_00_PHASE06B_NOSWAP_DESIGN.md``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

# Reuse — never redefine — the Phase 0.5 partition, field list, and digests.
from experiments.individuation import access_structure_operators as ops
from experiments.individuation.turnover_diag_engine import DiagEngine
from edlab.experiments.sc_iom.engine import IOMState

DEV_SEEDS = ops.DEV_SEEDS
STATE_FIELDS = ops.STATE_FIELDS            # ("rho","U","V","c","N","C","uptake","Mf")
CORE_RADIUS = ops.CORE_RADIUS              # 10 (Phase 0.5 DEV geometry; contained every source body)
HALO_WIDTH = ops.HALO_WIDTH                # 1 (four-neighbour stencil collar; diagnostic only)

# Engineering barrier thickness for the interface clamp.  The frozen engine has a
# one-cell stencil, so a one-cell overwrite ring is a topological 4-adjacency
# separator in principle, but it leaks at ~1e-13 (machine epsilon) once a front
# reaches it (verified on DEV 50002).  A TWO-cell overwrite barrier gives
# BIT-EXACT isolation (core diff == 0.0), which is what makes the disturbance and
# injection claims airtight.  The enclosed radius (not the barrier) defines the
# scientific unit whose sufficiency is tested.
BARRIER_WIDTH = 2


def require_dev_seed(seed: int) -> int:
    """Refuse any seed outside the already-open Phase 0.5/0.6 DEV namespace."""
    seed = int(seed)
    if seed not in DEV_SEEDS:
        raise ValueError("REFUSED: ACCESS-STRUCTURE-00 Phase 0.6B permits DEV seeds 50001-50010 only")
    return seed


def _shift(from_center: Sequence[int], to_center: Sequence[int]) -> tuple[int, int]:
    """Integer toroidal translation taking ``from_center`` onto ``to_center``."""
    return (int(round(to_center[0] - from_center[0])), int(round(to_center[1] - from_center[1])))


def _translated(array: np.ndarray, shift: tuple[int, int]) -> np.ndarray:
    return np.roll(array, shift, axis=(-2, -1))


# ----------------------------------------------------------------------------
# Boundary driver: records an outcome-independent collar trajectory and re-imposes
# it on a recipient ring after every step.  This is the whole no-swap mechanism.
# ----------------------------------------------------------------------------
@dataclass
class BoundaryDriver:
    """Overwrites a fixed recipient collar with a recorded per-step source frame.

    ``ring`` is a boolean mask (the collar cells).  ``frames`` is a list of
    per-step dicts ``{field: values_on_ring}`` (2-D fields give a 1-D vector,
    3-D fields give ``(k, n_ring)``).  ``offset`` shifts the temporal index to
    implement a phase-mismatched replay; ``label`` records provenance.
    """

    ring: np.ndarray
    frames: list
    offset: int = 0
    label: str = "unspecified"
    _cursor: int = 0

    def reset(self) -> "BoundaryDriver":
        self._cursor = 0
        return self

    def __len__(self) -> int:
        return len(self.frames)

    def apply(self, state: IOMState) -> IOMState:
        if not self.frames:
            return state
        idx = min(max(self._cursor + self.offset, 0), len(self.frames) - 1)
        frame = self.frames[idx]
        ys, xs = np.where(self.ring)
        for field, values in frame.items():
            target = getattr(state, field)
            if target.ndim == 2:
                target[ys, xs] = values
            else:
                target[:, ys, xs] = values
        self._cursor += 1
        return state


def _read_ring_frame(state: IOMState, ring_ys, ring_xs, shift: tuple[int, int]) -> dict:
    frame = {}
    for field in STATE_FIELDS:
        array = getattr(state, field)
        rolled = _translated(array, shift) if shift != (0, 0) else array
        if array.ndim == 2:
            frame[field] = rolled[ring_ys, ring_xs].copy()
        else:
            frame[field] = rolled[:, ring_ys, ring_xs].copy()
    return frame


def record_boundary(
    source_state: IOMState,
    engine,
    ring: np.ndarray,
    nsteps: int,
    *,
    shift: tuple[int, int] = (0, 0),
    label: str = "unspecified",
) -> BoundaryDriver:
    """Free-run ``source_state`` under ``engine`` for ``nsteps`` and record the
    (optionally translated) source collar values that fall on the recipient ring.

    The source trajectory is recorded BEFORE any recipient probe and is therefore
    independent of the recipient's future feeding outcome.  ``shift`` translates a
    foreign source (e.g. the on-manifold no-history reference or a crossed world)
    onto the recipient ring; ``shift=(0,0)`` gives the own/matched replay used as
    the sham.
    """
    ring_ys, ring_xs = np.where(ring)
    frames = []
    current = source_state.copy()
    for _ in range(nsteps):
        current = engine.step(current)
        frames.append(_read_ring_frame(current, ring_ys, ring_xs, shift))
    return BoundaryDriver(ring=ring.astype(bool), frames=frames, label=label)


class NoSwapClampEngine(DiagEngine):
    """Frozen engine + optional in-place collar clamp.  Extends ``DiagEngine`` so
    ``up_ref_zero`` (global-channel ablation, H_G) and ``copy_disabled`` remain
    available.  ``driver=None`` and both flags ``False`` -> byte-identical to the
    base ``MultiChannelMemoryEngine``.

    The clamp is applied AFTER the frozen ``step``: the scheduler ``step`` counter,
    update parity, and all physics equations are untouched; only the declared
    collar cells are overwritten.
    """

    def __init__(self, spec, mem, tracer, driver: BoundaryDriver = None,
                 up_ref_zero: bool = False, copy_disabled: bool = False):
        super().__init__(spec, mem, tracer, up_ref_zero=up_ref_zero, copy_disabled=copy_disabled)
        self.driver = driver

    def step(self, st: IOMState) -> IOMState:
        out = super().step(st)
        if self.driver is not None:
            out = self.driver.apply(out)
        return out


# ----------------------------------------------------------------------------
# In-place core-memory standardization (the "STD core" factor).  Varies ONLY the
# memory field on the frozen core support, holding the body (rho,U,V,c,N) fixed.
# This is the 03G/causal_confirm counterfactual, generalized to an on-manifold
# reference; it is NOT a body transplant.
# ----------------------------------------------------------------------------
def erase_core_memory(state: IOMState, core_mask: np.ndarray) -> IOMState:
    """Zero the memory field on the core support (matches causal_confirm erase)."""
    out = state.copy()
    out.Mf[:, core_mask] = 0.0
    return out


def standardize_core_memory(
    state: IOMState,
    core_mask: np.ndarray,
    reference_state: IOMState,
    shift: tuple[int, int],
) -> IOMState:
    """Set the core memory to the translated on-manifold reference memory in place.

    Only ``Mf`` on ``core_mask`` changes; the physical body is preserved exactly.
    """
    out = state.copy()
    ref_Mf = _translated(reference_state.Mf, shift)
    out.Mf[:, core_mask] = ref_Mf[:, core_mask]
    return out


# ----------------------------------------------------------------------------
# Outcome-independent comoving causal-horizon measurement (Task 5 / H_HALO).
# Defines the halo by interaction range + relaxation time from a small DEV-only
# perturbation response, NEVER by future feeding success.
# ----------------------------------------------------------------------------
def comoving_footprint(state: IOMState, center: Iterable[float], *,
                       rel_floor: float = 1e-2, local_radius: int = 15) -> dict:
    """Static, feeding-blind extent of the body and its self-produced attractant
    cloud around ``center``: the outermost radius where ``rho`` (body) and ``c``
    (attractant) still exceed ``rel_floor`` of their near-core peak.  This bounds
    the physical comoving object independent of any perturbation or outcome.

    The reference peak is taken over the LOCAL neighbourhood (``r <= local_radius``)
    so a denser neighbouring droplet does not deflate this target's own profile."""
    shape = state.rho.shape
    rgrid = np.rint(ops.periodic_distance(shape, tuple(center))).astype(int)
    out = {}
    for name, arr in (("rho", state.rho), ("c", state.c),
                      ("m_plus", np.tanh((state.Mf[0] + state.Mf[1]) / np.maximum(state.rho, ops_eps())))):
        max_r = int(rgrid.max())
        amp = [float(np.abs(arr[rgrid == r]).max()) if (rgrid == r).any() else 0.0 for r in range(max_r + 1)]
        peak = max(amp[:local_radius + 1]) if amp else 0.0
        # CONTIGUOUS from centre: stop at the first radius that drops below the floor,
        # so neighbouring droplets (>= SEP away, separated by a near-zero gap) do not
        # inflate this target's own comoving footprint.
        radius = 0
        if peak > 0:
            for r in range(len(amp)):
                if amp[r] >= rel_floor * peak:
                    radius = r
                else:
                    break
        out[name] = {"footprint_radius": int(radius), "peak": float(peak)}
    return out


def measure_causal_horizon(
    state: IOMState,
    engine,
    center: Iterable[float],
    *,
    field: str = "Mf",
    rel_amp: float = 5e-2,
    nsteps: int = 30,
) -> dict:
    """Perturb the persistent carrier ``field`` at ``center`` by a small relative
    amount and track the response FOOTPRINT (radius above a scale-relative floor)
    per step.  Reports the propagation-front speed, the influence-decay halo radius
    at the relaxed step, and the static comoving footprint.

    The halo is defined by the substrate's own interaction/relaxation length from a
    small DEV-only perturbation and by the body/attractant footprint — NEVER by
    future feeding success.  Perturbing ``Mf`` (memory, the slow persistent carrier)
    gives a stable footprint; ``c`` decays too fast to localise a halo.
    """
    shape = state.rho.shape
    distance = ops.periodic_distance(shape, tuple(center))
    rgrid = np.rint(distance).astype(int)
    cy, cx = ops._integer_center(tuple(center), shape)
    base = state.copy()
    pert = state.copy()
    arr = getattr(pert, field)
    scale = float(np.mean(np.abs(getattr(state, field)))) + ops_eps()
    delta = rel_amp * (scale if scale > 0 else 1.0)
    floor = 1e-6 * delta
    if arr.ndim == 2:
        arr[cy, cx] += delta
    else:
        arr[:, cy, cx] += delta

    fronts = []
    radii = []
    b, p = base, pert
    for t in range(1, nsteps + 1):
        b = engine.step(b)
        p = engine.step(p)
        diff = np.zeros(shape)
        for f in STATE_FIELDS:
            d = np.abs(getattr(p, f) - getattr(b, f))
            if d.ndim == 3:
                d = d.max(axis=0)
            diff = np.maximum(diff, d)
        influenced = diff > floor
        r = float(distance[influenced].max()) if influenced.any() else 0.0
        radii.append(r)
        fronts.append({"step": t, "front_radius": r, "n_influenced": int(influenced.sum())})

    increments = np.diff([0.0] + radii)
    front_speed = float(np.median(increments[increments > 0])) if np.any(increments > 0) else 0.0

    # influence-decay halo at the relaxed step: amplitude binned by radius vs peak
    final_diff = np.zeros(shape)
    for f in STATE_FIELDS:
        d = np.abs(getattr(p, f) - getattr(b, f))
        if d.ndim == 3:
            d = d.max(axis=0)
        final_diff = np.maximum(final_diff, d)
    max_r = int(rgrid.max())
    amp_by_r = [float(final_diff[rgrid == r].max()) if (rgrid == r).any() else 0.0 for r in range(max_r + 1)]
    peak = max(amp_by_r) if amp_by_r else 0.0
    rel_floor = 1e-2
    halo_radius = 0
    if peak > 0:
        for r in range(len(amp_by_r)):
            if amp_by_r[r] >= rel_floor * peak:
                halo_radius = r
    return {
        "field_perturbed": field,
        "rel_amp": rel_amp,
        "delta_absolute": float(delta),
        "nsteps": int(nsteps),
        "front_radius_by_step": fronts,
        "front_speed_cells_per_step": front_speed,
        "influence_decay_halo_radius": int(halo_radius),
        "influence_relative_floor": rel_floor,
        "static_footprint": comoving_footprint(state, center),
        "core_radius_used": int(CORE_RADIUS),
        "note": ("influence-decay halo + static footprint; feeding-blind; H_HALO "
                 "operational definition. Front speed reported separately."),
    }


def ops_eps() -> float:
    return 1e-12


# ----------------------------------------------------------------------------
# Convenience: build the collar ring and core mask for a target center.
# ----------------------------------------------------------------------------
def core_and_collar(shape, center, *, core_radius=CORE_RADIUS, barrier_width=BARRIER_WIDTH):
    """Return (partition, core_mask, barrier_mask) for a target center.

    ``core_mask`` (d <= ``core_radius``) is the enclosed scientific unit whose
    sufficiency is tested; ``barrier_mask`` is the clamp ring
    (``core_radius`` < d <= ``core_radius + barrier_width``).  ``barrier_width=2``
    gives bit-exact isolation for the one-cell stencil.  Increasing
    ``core_radius`` to ``core_radius + w_halo`` yields the comoving-halo-inclusive
    unit used to test H_HALO (core-only vs core+halo sufficiency).
    """
    partition = ops.partition_state(shape, center, core_radius=core_radius, halo_width=barrier_width)
    return partition, partition.core.copy(), partition.halo.copy()
