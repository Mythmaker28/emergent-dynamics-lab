"""Minimal fixed-law mass-conservative Flow-Lenia core with strictly passive cohort tracers.

Single channel. Global (non-localized) fixed parameters. No evolution / resource collection / mutation /
multi-species. Dynamics: potential U = K*A (periodic FFT convolution), growth-shaped affinity, a
concentration-limited flow field F = (1-alpha)*grad(U) - alpha*grad(A), and mass-conserving transport of A by
forward bilinear reintegration tracking. Passive cohort fields are transported by the IDENTICAL operator (same F,
same weights) and by construction never enter U, the affinity, the flow, or the update -- they only label origin
of mass so a field material-retention can be measured. Deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class FlowLeniaSpec:
    size: int = 64
    kernel_radius: float = 10.0        # cells
    kernel_mu: float = 0.5             # peak position as fraction of kernel_radius
    kernel_sigma: float = 0.15         # shell width as fraction of kernel_radius
    growth_mu: float = 0.15
    growth_sigma: float = 0.017
    dt: float = 0.30                   # flow time step (advection CFL-limited)
    flow_gain: float = 1.0             # scales the flow field
    concentration_theta: float = 1.2   # A/theta concentration cap
    concentration_n: float = 2.0

    def as_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


def growth(u: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return 2.0 * np.exp(-0.5 * ((u - mu) / sigma) ** 2) - 1.0


def _kernel_fft(spec: FlowLeniaSpec) -> np.ndarray:
    n = spec.size
    coords = np.fft.fftfreq(n) * n
    yy, xx = np.meshgrid(coords, coords, indexing="ij")
    r = np.hypot(yy, xx)
    R = spec.kernel_radius
    shell = np.exp(-0.5 * ((r - spec.kernel_mu * R) / (spec.kernel_sigma * R)) ** 2)
    shell[r > R] = 0.0
    total = shell.sum()
    if total > 0:
        shell = shell / total          # normalized so sum(K) = 1 (potential is a weighted average)
    return np.fft.fft2(shell)


def _gradient_periodic(field_2d: np.ndarray) -> np.ndarray:
    gy = (np.roll(field_2d, -1, axis=0) - np.roll(field_2d, 1, axis=0)) * 0.5
    gx = (np.roll(field_2d, -1, axis=1) - np.roll(field_2d, 1, axis=1)) * 0.5
    return np.stack([gy, gx], axis=0)


def flow_field(A: np.ndarray, spec: FlowLeniaSpec, fK: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (F, U): the concentration-limited flow field and the potential. Uses A only (tracers excluded)."""
    U = np.real(np.fft.ifft2(fK * np.fft.fft2(A)))
    affinity = U                                    # potential is the affinity map mass flows along
    grad_aff = _gradient_periodic(affinity)
    grad_A = _gradient_periodic(A)
    alpha = np.clip((A / spec.concentration_theta) ** spec.concentration_n, 0.0, 1.0)
    F = spec.flow_gain * ((1.0 - alpha) * grad_aff - alpha * grad_A)
    return F, U


def reintegrate(fields: list[np.ndarray], disp: np.ndarray) -> list[np.ndarray]:
    """Mass-conserving forward bilinear transport of each field by displacement `disp` (2,H,W): [dy,dx].

    Weights depend only on `disp`, so the operator is linear and identical across fields -> a cohort partition
    (sum of cohorts == A) is preserved exactly, and total mass of every field is conserved to float rounding.
    """
    h, w = fields[0].shape
    ii, jj = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    ty = ii + disp[0]; tx = jj + disp[1]
    y0 = np.floor(ty).astype(np.int64); x0 = np.floor(tx).astype(np.int64)
    fy = ty - y0; fx = tx - x0
    y0m = y0 % h; x0m = x0 % w; y1m = (y0 + 1) % h; x1m = (x0 + 1) % w
    w00 = (1 - fy) * (1 - fx); w01 = (1 - fy) * fx; w10 = fy * (1 - fx); w11 = fy * fx
    dest = [(y0m, x0m, w00), (y0m, x1m, w01), (y1m, x0m, w10), (y1m, x1m, w11)]
    out = []
    for A in fields:
        acc = np.zeros_like(A)
        flat = acc.ravel()
        for (yy, xx, ww) in dest:
            np.add.at(flat, (yy * w + xx).ravel(), (A * ww).ravel())
        out.append(flat.reshape(h, w))
    return out


@dataclass
class FlowLeniaState:
    A: np.ndarray
    cohorts: np.ndarray                # (C, H, W); sum over C == A (invariant)
    step: int = 0

    def mass(self) -> float:
        return float(self.A.sum())


@dataclass
class FlowLeniaEngine:
    spec: FlowLeniaSpec
    _fK: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_fK", _kernel_fft(self.spec))

    def step(self, state: FlowLeniaState) -> FlowLeniaState:
        F, _ = flow_field(state.A, self.spec, self._fK)     # tracers NOT used to compute F
        disp = F * self.spec.dt
        # clamp displacement to < 1 cell for stable bilinear transport (CFL)
        mag = np.maximum(np.abs(disp[0]), np.abs(disp[1]))
        scale = np.where(mag > 0.9, 0.9 / np.maximum(mag, 1e-12), 1.0)
        disp = disp * scale
        transported = reintegrate([state.A, *list(state.cohorts)], disp)
        A_new = transported[0]
        cohorts_new = np.stack(transported[1:], axis=0) if state.cohorts.shape[0] else state.cohorts
        return FlowLeniaState(A_new, cohorts_new, state.step + 1)

    def simulate(self, state: FlowLeniaState, steps: int, snapshot_interval: int) -> list[FlowLeniaState]:
        out = [FlowLeniaState(state.A.copy(), state.cohorts.copy(), 0)]
        cur = state
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % snapshot_interval == 0 or t == steps:
                out.append(FlowLeniaState(cur.A.copy(), cur.cohorts.copy(), t))
        return out
