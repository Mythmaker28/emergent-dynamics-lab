"""Stage-A-only conservative access-port qualification wrapper.

This module duplicates the frozen ``MultiChannelMemoryEngine.step`` arithmetic
only inside an isolated diagnostic wrapper.  The frozen engine is never
modified.  Natural/open execution delegates directly to the supplied frozen
engine.  The active kernel exists solely to qualify the exact Phase-0
candidate on deterministic synthetic states.

The environmental polarity is availability: ``e_available=0`` holds
post-t0 outside-parent innovations at hash-bound preprobe references.  It is
not total environmental absence.  No member-directed ``K`` namespace exists
in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable

import numpy as np


STATE_FIELDS = ("rho", "U", "V", "c", "N", "C", "uptake", "Mf")
EXTENSIVE_FIELDS = ("rho", "U", "V", "C", "Mf")
ARM_SETTINGS = {
    "L0E0": (0, 0),
    "L1E0": (1, 0),
    "L0E1": (0, 1),
    "L1E1": (1, 1),
}
H_STAR = 2
EPS = 1e-12


def _lap(array: np.ndarray) -> np.ndarray:
    return (
        np.roll(array, 1, -2)
        + np.roll(array, -1, -2)
        + np.roll(array, 1, -1)
        + np.roll(array, -1, -1)
        - 4.0 * array
    )


def _tmean(array: np.ndarray) -> np.ndarray:
    return 0.25 * (
        np.roll(array, 1, -2)
        + np.roll(array, -1, -2)
        + np.roll(array, 1, -1)
        + np.roll(array, -1, -1)
    )


def _array_hash(array: np.ndarray) -> str:
    value = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(value.shape).encode("ascii"))
    digest.update(str(value.dtype).encode("ascii"))
    digest.update(value.tobytes())
    return digest.hexdigest()


def state_sha256(state: Any) -> str:
    digest = hashlib.sha256()
    digest.update(str(int(state.step)).encode("ascii"))
    for field in STATE_FIELDS:
        array = np.ascontiguousarray(getattr(state, field))
        digest.update(field.encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def state_bytes_equal(left: Any, right: Any) -> bool:
    return left.step == right.step and all(
        np.array_equal(getattr(left, field), getattr(right, field)) for field in STATE_FIELDS
    )


def operation_tolerance(terms: Iterable[np.ndarray | float], additions: int) -> float:
    """Higham gamma_n bound fixed by operation count, never by observed error."""
    if additions < 0:
        raise ValueError("additions must be non-negative")
    eps = np.finfo(np.float64).eps
    if additions * eps >= 1.0:
        raise ValueError("operation count is outside the gamma_n domain")
    absolute_sum = 0.0
    for term in terms:
        absolute_sum += float(np.abs(np.asarray(term, dtype=np.float64)).sum(dtype=np.float64))
    gamma = (additions * eps) / (1.0 - additions * eps)
    return gamma * absolute_sum


@dataclass(frozen=True)
class ReferenceBundle:
    rho: np.ndarray
    U: np.ndarray
    V: np.ndarray
    c: np.ndarray
    N: np.ndarray
    C: np.ndarray
    uptake: np.ndarray
    Mf: np.ndarray
    fU: np.ndarray
    fV: np.ndarray
    frac: np.ndarray
    fM: np.ndarray
    u: np.ndarray
    v: np.ndarray
    m: np.ndarray
    external_up_sum_t0: float
    external_alive_count_t0: int
    reference_hash: str


@dataclass(frozen=True)
class AccessPortPlan:
    target_mask: np.ndarray
    t0_step: int
    h_star: int
    l_available: int
    e_available: int
    probe_schedule: tuple[np.ndarray, ...]
    references: ReferenceBundle
    target_mask_hash: str
    schedule_hash: str
    canonical_plan_hash: str

    @property
    def is_fully_open(self) -> bool:
        return self.l_available == 1 and self.e_available == 1


@dataclass(frozen=True)
class AccessStepResult:
    state: Any
    diagnostics: dict[str, Any]


def _readonly_copy(array: np.ndarray) -> np.ndarray:
    result = np.array(array, copy=True)
    result.flags.writeable = False
    return result


def _references(state: Any, target_mask: np.ndarray) -> ReferenceBundle:
    rho = _readonly_copy(state.rho)
    U = _readonly_copy(state.U)
    V = _readonly_copy(state.V)
    c = _readonly_copy(state.c)
    nutrient = _readonly_copy(state.N)
    cohorts = _readonly_copy(state.C)
    uptake = _readonly_copy(state.uptake)
    memory = _readonly_copy(state.Mf)
    safe = np.maximum(rho, EPS)
    fU = _readonly_copy(U / safe)
    fV = _readonly_copy(V / safe)
    frac = _readonly_copy(cohorts / safe)
    fM = _readonly_copy(memory / safe[None, :, :])
    outside = ~target_mask
    alive = rho > 1e-4
    external_alive = outside & alive
    external_sum = float(uptake[external_alive].sum(dtype=np.float64))
    external_count = int(external_alive.sum())
    digest = hashlib.sha256()
    for name, array in (
        ("rho", rho), ("U", U), ("V", V), ("c", c), ("N", nutrient),
        ("C", cohorts), ("uptake", uptake), ("Mf", memory),
    ):
        digest.update(name.encode("ascii"))
        digest.update(_array_hash(array).encode("ascii"))
    digest.update(str(external_sum).encode("ascii"))
    digest.update(str(external_count).encode("ascii"))
    return ReferenceBundle(
        rho=rho,
        U=U,
        V=V,
        c=c,
        N=nutrient,
        C=cohorts,
        uptake=uptake,
        Mf=memory,
        fU=fU,
        fV=fV,
        frac=frac,
        fM=fM,
        u=fU,
        v=fV,
        m=fM,
        external_up_sum_t0=external_sum,
        external_alive_count_t0=external_count,
        reference_hash=digest.hexdigest(),
    )


def compile_plan(
    state: Any,
    target_mask: np.ndarray,
    *,
    l_available: int,
    e_available: int,
    probe_schedule: Iterable[np.ndarray] | None = None,
    compile_order: tuple[str, str] = ("L", "E"),
) -> AccessPortPlan:
    mask = np.asarray(target_mask)
    if mask.dtype != np.bool_ or mask.shape != state.rho.shape:
        raise ValueError("target_mask must be boolean and match the spatial state shape")
    if not mask.any() or mask.all():
        raise ValueError("target_mask must contain target and external cells")
    if l_available not in (0, 1) or e_available not in (0, 1):
        raise ValueError("availability polarity is binary with 1=open")
    if tuple(compile_order) not in (("L", "E"), ("E", "L")):
        raise ValueError("compile_order must contain L and E exactly once")
    if probe_schedule is None:
        schedule = tuple(np.zeros_like(state.N) for _ in range(H_STAR))
    else:
        schedule = tuple(_readonly_copy(np.asarray(item)) for item in probe_schedule)
        if len(schedule) != H_STAR:
            raise ValueError(f"probe_schedule must contain exactly H*={H_STAR} arrays")
        if any(item.shape != state.N.shape for item in schedule):
            raise ValueError("every probe array must match N")
    frozen_mask = _readonly_copy(mask)
    refs = _references(state, frozen_mask)
    mask_hash = _array_hash(frozen_mask)
    schedule_digest = hashlib.sha256()
    for offset, item in enumerate(schedule):
        schedule_digest.update(str(offset).encode("ascii"))
        schedule_digest.update(_array_hash(item).encode("ascii"))
    schedule_hash = schedule_digest.hexdigest()
    canonical = {
        "schema": "CAA01-STAGE-A-PLAN-v1",
        "t0_step": int(state.step),
        "h_star": H_STAR,
        "l_available": int(l_available),
        "e_available": int(e_available),
        "target_mask_hash": mask_hash,
        "schedule_hash": schedule_hash,
        "reference_hash": refs.reference_hash,
        "local_window": [int(state.step), int(state.step) + 1],
        "environment_window": [int(state.step), int(state.step) + H_STAR],
    }
    plan_hash = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return AccessPortPlan(
        target_mask=frozen_mask,
        t0_step=int(state.step),
        h_star=H_STAR,
        l_available=int(l_available),
        e_available=int(e_available),
        probe_schedule=schedule,
        references=refs,
        target_mask_hash=mask_hash,
        schedule_hash=schedule_hash,
        canonical_plan_hash=plan_hash,
    )


def compile_four_arms(
    state: Any,
    target_mask: np.ndarray,
    *,
    probe_schedule: Iterable[np.ndarray] | None = None,
    compile_order: tuple[str, str] = ("L", "E"),
) -> dict[str, AccessPortPlan]:
    return {
        name: compile_plan(
            state,
            target_mask,
            l_available=values[0],
            e_available=values[1],
            probe_schedule=probe_schedule,
            compile_order=compile_order,
        )
        for name, values in ARM_SETTINGS.items()
    }


def exact_clone(state: Any) -> Any:
    return state.copy()


def apply_common_probe(state: Any, pulse: np.ndarray) -> Any:
    if pulse.shape != state.N.shape:
        raise ValueError("probe pulse must match N")
    result = state.copy()
    result.N = result.N + pulse
    return result


def _face_flux_lr(rho_l: np.ndarray, c_l: np.ndarray, rho_r: np.ndarray, c_r: np.ndarray, spec: Any) -> np.ndarray:
    dc = c_r - c_l
    chi = spec.chi0 / (1.0 + (0.5 * (c_l + c_r) / spec.c_sat) ** 2)
    left_is_up = dc > 0
    rho_up = np.where(left_is_up, rho_l, rho_r)
    rho_down = np.where(left_is_up, rho_r, rho_l)
    adv = chi * dc * rho_up * np.maximum(0.0, 1.0 - rho_down / spec.rho_max)
    dif = -spec.D_rho * (rho_r - rho_l)
    return adv + dif


def _gated_lap(current: np.ndarray, reference: np.ndarray, target: np.ndarray, e_available: int) -> np.ndarray:
    if e_available == 1:
        return _lap(current)
    total = np.zeros_like(current)
    for axis, shift in ((-2, 1), (-2, -1), (-1, 1), (-1, -1)):
        neighbour = np.roll(current, shift, axis)
        ref_neighbour = np.roll(reference, shift, axis)
        outside = np.roll(~target, shift, axis)
        selected = np.where(target & outside, ref_neighbour, neighbour)
        total = total + selected
    return total - 4.0 * current


def _gated_tmean(current: np.ndarray, reference: np.ndarray, target: np.ndarray, e_available: int) -> np.ndarray:
    if e_available == 1:
        return _tmean(current)
    total = np.zeros_like(current)
    for axis, shift in ((-2, 1), (-2, -1), (-1, 1), (-1, -1)):
        neighbour = np.roll(current, shift, axis)
        ref_neighbour = np.roll(reference, shift, axis)
        outside = np.roll(~target, shift, axis)
        total = total + np.where(target & outside, ref_neighbour, neighbour)
    return 0.25 * total


class ConservativeAccessEngine:
    """Isolated diagnostic wrapper around an unchanged frozen MCM engine."""

    def __init__(self, frozen_engine: Any):
        self.frozen = frozen_engine

    def step(self, state: Any, plan: AccessPortPlan | None = None, *, force_active: bool = False) -> Any:
        return self.step_with_diagnostics(state, plan, force_active=force_active).state

    def step_with_diagnostics(
        self,
        state: Any,
        plan: AccessPortPlan | None = None,
        *,
        force_active: bool = False,
    ) -> AccessStepResult:
        before = state_sha256(state)
        if plan is None:
            result = self.frozen.step(state)
            return AccessStepResult(result, {
                "parent_delegated": True,
                "active_kernel": False,
                "input_state_preserved": before == state_sha256(state),
                "input_hash": before,
            })
        self._validate_runtime(state, plan)
        offset = int(state.step) - plan.t0_step
        local_active = offset == 0 and plan.l_available == 0
        environment_active = 0 <= offset < plan.h_star and plan.e_available == 0
        if not force_active and not local_active and not environment_active:
            result = self.frozen.step(state)
            return AccessStepResult(result, {
                "parent_delegated": True,
                "active_kernel": False,
                "offset": offset,
                "local_gate_active": False,
                "environment_gate_active": False,
                "input_state_preserved": before == state_sha256(state),
                "input_hash": before,
                "plan_hash": plan.canonical_plan_hash,
            })
        result, diagnostics = self._active_step(state, plan, offset)
        diagnostics.update({
            "parent_delegated": False,
            "active_kernel": True,
            "offset": offset,
            "local_gate_active": local_active,
            "environment_gate_active": environment_active,
            "input_state_preserved": before == state_sha256(state),
            "input_hash": before,
            "plan_hash": plan.canonical_plan_hash,
        })
        return AccessStepResult(result, diagnostics)

    @staticmethod
    def _validate_runtime(state: Any, plan: AccessPortPlan) -> None:
        if state.rho.shape != plan.target_mask.shape:
            raise ValueError("runtime state shape does not match immutable target mask")
        offset = int(state.step) - plan.t0_step
        if offset < 0:
            raise ValueError("state precedes plan t0")

    def _transport(
        self,
        rho: np.ndarray,
        U: np.ndarray,
        V: np.ndarray,
        c: np.ndarray,
        C: np.ndarray,
        Mf: np.ndarray,
        plan: AccessPortPlan,
        e_available: int,
    ) -> tuple[dict[str, np.ndarray], dict[str, float]]:
        spec = self.frozen.spec
        safe = np.maximum(rho, EPS)
        values = {
            "U": U / safe,
            "V": V / safe,
            "C": C / safe,
            "Mf": Mf / safe[None, :, :],
        }
        refs = {
            "U": plan.references.fU,
            "V": plan.references.fV,
            "C": plan.references.frac,
            "Mf": plan.references.fM,
        }
        increments = {
            "rho": np.zeros_like(rho),
            "U": np.zeros_like(U),
            "V": np.zeros_like(V),
            "C": np.zeros_like(C),
            "Mf": np.zeros_like(Mf),
        }
        ledger = {field: 0.0 for field in EXTENSIVE_FIELDS}
        target = plan.target_mask
        for axis in (-2, -1):
            frozen_flux = self.frozen._face_flux(rho, c, axis)
            donor_left = frozen_flux > 0
            frozen = {
                "rho": -(frozen_flux - np.roll(frozen_flux, 1, axis)),
            }
            for field, intensive in values.items():
                donor = np.where(donor_left[None, ...], intensive, np.roll(intensive, -1, axis)) if intensive.ndim == 3 else np.where(donor_left, intensive, np.roll(intensive, -1, axis))
                flux = frozen_flux[None, ...] * donor if intensive.ndim == 3 else frozen_flux * donor
                frozen[field] = -(flux - np.roll(flux, 1, axis))
            if e_available == 1:
                for field in increments:
                    increments[field] = increments[field] + frozen[field]
                continue

            plus_outside = target & np.roll(~target, -1, axis)
            minus_outside = target & np.roll(~target, 1, axis)
            rho_right = np.where(plus_outside, np.roll(plan.references.rho, -1, axis), np.roll(rho, -1, axis))
            c_right = np.where(plus_outside, np.roll(plan.references.c, -1, axis), np.roll(c, -1, axis))
            out_flux = _face_flux_lr(rho, c, rho_right, c_right, spec)
            rho_left = np.where(minus_outside, np.roll(plan.references.rho, 1, axis), np.roll(rho, 1, axis))
            c_left = np.where(minus_outside, np.roll(plan.references.c, 1, axis), np.roll(c, 1, axis))
            in_flux = _face_flux_lr(rho_left, c_left, rho, c, spec)
            active = {"rho": -(out_flux - in_flux)}
            for field, intensive in values.items():
                ref = refs[field]
                right = np.roll(intensive, -1, axis)
                left = np.roll(intensive, 1, axis)
                if intensive.ndim == 3:
                    plus_mask = plus_outside[None, ...]
                    minus_mask = minus_outside[None, ...]
                    right = np.where(plus_mask, np.roll(ref, -1, axis), right)
                    left = np.where(minus_mask, np.roll(ref, 1, axis), left)
                    out_donor = np.where((out_flux > 0)[None, ...], intensive, right)
                    in_donor = np.where((in_flux > 0)[None, ...], left, intensive)
                    active[field] = -(out_flux[None, ...] * out_donor - in_flux[None, ...] * in_donor)
                else:
                    right = np.where(plus_outside, np.roll(ref, -1, axis), right)
                    left = np.where(minus_outside, np.roll(ref, 1, axis), left)
                    out_donor = np.where(out_flux > 0, intensive, right)
                    in_donor = np.where(in_flux > 0, left, intensive)
                    active[field] = -(out_flux * out_donor - in_flux * in_donor)
            for field in increments:
                mask = target if active[field].ndim == 2 else target[None, ...]
                selected = np.where(mask, active[field], frozen[field])
                delta = np.where(mask, active[field] - frozen[field], 0.0)
                increments[field] = increments[field] + selected
                ledger[field] += float(delta.sum(dtype=np.float64))
        return increments, ledger

    def _active_step(self, state: Any, plan: AccessPortPlan, offset: int) -> tuple[Any, dict[str, Any]]:
        spec = self.frozen.spec
        mem = self.frozen.mem
        dt = spec.dt
        target = plan.target_mask
        e_available = plan.e_available if 0 <= offset < plan.h_star else 1
        local_closed = offset == 0 and plan.l_available == 0
        rho, U, V, c, nutrient, C, Mf = state.rho, state.U, state.V, state.c, state.N, state.C, state.Mf
        rho0 = rho

        transport, transport_ledger = self._transport(rho, U, V, c, C, Mf, plan, e_available)
        rho = rho + dt * transport["rho"]
        U = U + dt * transport["U"]
        V = V + dt * transport["V"]
        C = C + dt * transport["C"]
        Mf = Mf + dt * transport["Mf"]

        u = U / np.maximum(rho, EPS)
        v = V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        m_plus = np.tanh(m[0] + m[1])
        if local_closed:
            selected_m_plus = np.where(target, 0.0, m_plus)
        else:
            selected_m_plus = m_plus
        qq = np.maximum(0.0, 1.0 - rho / spec.rho_max)
        g = dt * spec.g0 * rho * nutrient * qq * (1.0 + spec.beta * sig) * (1.0 + mem.lam_plus * selected_m_plus)
        g = np.clip(g, 0.0, np.maximum(nutrient, 0.0))
        uptake = g.copy()
        nutrient = nutrient - g
        rho = rho + g
        U = U + g * u
        V = V + g * v
        Mf = Mf + g[None, :, :] * m
        C[self.frozen.tracer.active_feed_cohort(state.step)] += g

        keep = 1.0 - dt * spec.k
        rho = rho * keep
        U = U * keep
        V = V * keep
        C = C * keep
        Mf = Mf * keep

        stage_ledger: dict[str, Any] = {"transport": transport_ledger}
        if spec.a > 0.0:
            alive = rho > 1e-4
            u = np.where(alive, U / np.maximum(rho, EPS), 0.0)
            v = np.where(alive, V / np.maximum(rho, EPS), 0.0)
            du = spec.a / (1.0 + (v / spec.K) ** 2) - u
            dv = spec.a / (1.0 + (u / spec.K) ** 2) - v
            lap_u_open = _lap(u)
            lap_v_open = _lap(v)
            lap_u = _gated_lap(u, plan.references.u, target, e_available)
            lap_v = _gated_lap(v, plan.references.v, target, e_available)
            u_open = np.clip(u + dt * (spec.tau * du + spec.D_int * lap_u_open * alive), 0.0, None) * alive
            v_open = np.clip(v + dt * (spec.tau * dv + spec.D_int * lap_v_open * alive), 0.0, None) * alive
            u = np.clip(u + dt * (spec.tau * du + spec.D_int * lap_u * alive), 0.0, None) * alive
            v = np.clip(v + dt * (spec.tau * dv + spec.D_int * lap_v * alive), 0.0, None) * alive
            U = rho * u
            V = rho * v
            stage_ledger["toggle"] = {
                "U_target_delta": float(((rho * u - rho * u_open)[target]).sum(dtype=np.float64)),
                "V_target_delta": float(((rho * v - rho * v_open)[target]).sum(dtype=np.float64)),
            }

        alive = rho > 1e-4
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        frozen_up_ref = float(uptake[alive].mean()) if alive.any() else 0.0
        if e_available == 1:
            selected_up_ref = frozen_up_ref
            S_A = float(uptake[target & alive].sum(dtype=np.float64))
            n_A = int((target & alive).sum())
            S_B = float(uptake[(~target) & alive].sum(dtype=np.float64))
            n_B = int(((~target) & alive).sum())
        else:
            target_alive = target & alive
            S_A = float(uptake[target_alive].sum(dtype=np.float64))
            n_A = int(target_alive.sum())
            S_B = plan.references.external_up_sum_t0
            n_B = plan.references.external_alive_count_t0
            denominator = n_A + n_B
            selected_up_ref = (S_A + S_B) / denominator if denominator else 0.0
        Psi = np.tanh(mem.k_exp * (nutrient - c) + mem.k_up * (uptake - selected_up_ref))
        Psi_open = np.tanh(mem.k_exp * (nutrient - c) + mem.k_up * (uptake - frozen_up_ref))
        eta_d = mem.eta_d
        newm = np.empty_like(m)
        newm_open = np.empty_like(m)
        for k in range(mem.n_comp):
            mk = m[k]
            tmean_open = _tmean(mk)
            lap_open = _lap(mk)
            tmean_selected = _gated_tmean(mk, plan.references.m[k], target, e_available)
            lap_selected = _gated_lap(mk, plan.references.m[k], target, e_available)
            dmk_open = mem.eta_w * Psi_open - eta_d[k] * mk + mem.eta_t * (tmean_open - mk) + mem.D_m * lap_open
            dmk = mem.eta_w * Psi - eta_d[k] * mk + mem.eta_t * (tmean_selected - mk) + mem.D_m * lap_selected
            newm_open[k] = np.clip(mk + dt * dmk_open * alive, -1.0, 1.0) * alive
            newm[k] = np.clip(mk + dt * dmk * alive, -1.0, 1.0) * alive
        Mf_open = rho * newm_open
        Mf = rho * newm
        stage_ledger["up_ref"] = {
            "frozen": frozen_up_ref,
            "selected": selected_up_ref,
            "S_A": S_A,
            "n_A": n_A,
            "S_B_selected": S_B,
            "n_B_selected": n_B,
            "S_B0": plan.references.external_up_sum_t0,
            "n_B0": plan.references.external_alive_count_t0,
        }
        stage_ledger["writer"] = {
            "Mf_target_delta": [
                float((Mf[k][target] - Mf_open[k][target]).sum(dtype=np.float64)) for k in range(mem.n_comp)
            ]
        }

        m_minus = np.tanh(newm[0] - newm[1])
        lap_c_open = _lap(c)
        lap_c = _gated_lap(c, plan.references.c, target, e_available)
        c_open_gate = c + dt * (spec.D_c * lap_c_open + spec.s * rho0 * (1.0 + mem.lam_minus * m_minus) - spec.delta * c)
        c = c + dt * (spec.D_c * lap_c + spec.s * rho0 * (1.0 + mem.lam_minus * m_minus) - spec.delta * c)
        stage_ledger["c"] = {"target_gate_delta": float((c[target] - c_open_gate[target]).sum(dtype=np.float64))}

        pulse = plan.probe_schedule[offset] if 0 <= offset < len(plan.probe_schedule) else np.zeros_like(nutrient)
        reference_n = plan.references.N + pulse
        lap_n_open = _lap(nutrient)
        lap_n = _gated_lap(nutrient, reference_n, target, e_available)
        n_open_gate = nutrient + dt * (spec.D_N * lap_n_open + spec.F * (spec.N0 - nutrient))
        nutrient = nutrient + dt * (spec.D_N * lap_n + spec.F * (spec.N0 - nutrient))
        stage_ledger["N"] = {
            "target_gate_delta": float((nutrient[target] - n_open_gate[target]).sum(dtype=np.float64)),
            "probe_hash": _array_hash(pulse),
            "reference_plus_probe_hash": _array_hash(reference_n),
            "reservoir_gated": False,
        }

        result = type(state)(rho, U, V, c, nutrient, C, uptake, Mf, state.step + 1)
        diagnostics = {
            "schema": "CAA01-STAGE-A-STEP-DIAGNOSTICS-v1",
            "h_star": H_STAR,
            "local_window": [plan.t0_step, plan.t0_step + 1],
            "environment_window": [plan.t0_step, plan.t0_step + H_STAR],
            "availability": {"l": plan.l_available, "e": plan.e_available},
            "stage_ledger": stage_ledger,
            "target_boundary_face_count": int(sum(
                (target & np.roll(~target, shift, axis)).sum()
                for axis, shift in ((-2, 1), (-2, -1), (-1, 1), (-1, -1))
            )),
            "state_schema": list(STATE_FIELDS) + ["step"],
            "new_reporter_in_state": False,
        }
        return result, diagnostics
