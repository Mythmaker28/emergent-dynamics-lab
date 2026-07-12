"""EXP_FL_02: isolated, globally mass-conservative ACTIVE-FIELD / RESERVOIR exchange (material throughput).

One mechanism only. The active field A is the Flow-Lenia field (advected, detected, measured). A latent reservoir
field R holds inactive mass. A local, SPATIALLY GENERIC, detector-independent exchange converts mass between R and
A according to the local growth field G(U(A)):

    delta = exchange_rate * dt * ( max(G,0)*R  -  max(-G,0)*A ),  clipped to [-A, R]
    A <- A + delta ;  R <- R - delta            (A+R conserved exactly, cell by cell)

R never enters U, G or the flow field F (those depend on A only), so `exchange_rate = 0` is an EXACT OFF LIMIT
reproducing the current Flow-Lenia core bit-for-bit. R is transported by isotropic periodic diffusion (generic
medium), which is mass-conserving. Passive cohorts partition BOTH fields (sum_c C_A = A, sum_c C_R = R) and are
carried by exactly the same operators (reintegration for A, diffusion for R); on exchange, transferred mass takes
the LOCAL cohort proportions of its source field, so cohorts label origin across A<->R. Cohorts never influence
any dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .engine import FlowLeniaSpec, _kernel_fft, flow_field, growth, reintegrate


@dataclass(frozen=True)
class ThroughputSpec:
    exchange_rate: float = 0.0        # 0 = EXACT OFF limit (current Flow-Lenia core)
    reservoir_diffusion: float = 0.15  # isotropic diffusion coefficient for R (stability: <= 0.25)
    reservoir_fraction: float = 1.0    # initial reservoir mass = fraction * initial active mass

    def __post_init__(self) -> None:
        for v in (self.exchange_rate, self.reservoir_diffusion, self.reservoir_fraction):
            if not np.isfinite(v):
                raise ValueError("ThroughputSpec values must be finite")
        if self.exchange_rate < 0:
            raise ValueError("exchange_rate must be non-negative (0 = OFF limit)")
        if not 0.0 <= self.reservoir_diffusion <= 0.25:
            raise ValueError("reservoir_diffusion must lie in [0, 0.25] for explicit stability")
        if self.reservoir_fraction < 0:
            raise ValueError("reservoir_fraction must be non-negative")

    @property
    def is_off(self) -> bool:
        return self.exchange_rate == 0.0

    def as_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


@dataclass
class ThroughputState:
    A: np.ndarray
    R: np.ndarray
    cohorts_A: np.ndarray      # (C,H,W); sum == A
    cohorts_R: np.ndarray      # (C,H,W); sum == R
    step: int = 0

    def total_mass(self) -> float:
        return float(self.A.sum() + self.R.sum())


def _diffuse(fields: list[np.ndarray], coeff: float) -> list[np.ndarray]:
    """Isotropic periodic 4-neighbour diffusion; mass-conserving, nonnegativity-preserving for coeff<=0.25."""
    out = []
    for X in fields:
        lap = (np.roll(X, 1, 0) + np.roll(X, -1, 0) + np.roll(X, 1, 1) + np.roll(X, -1, 1) - 4.0 * X)
        out.append(X + coeff * lap)
    return out


@dataclass
class ThroughputEngine:
    spec: FlowLeniaSpec
    tspec: ThroughputSpec
    _fK: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_fK", _kernel_fft(self.spec))

    def step(self, st: ThroughputState) -> ThroughputState:
        # 1) Flow + growth from the ACTIVE field only (reservoir and cohorts never enter)
        F, U = flow_field(st.A, self.spec, self._fK)
        G = growth(U, self.spec.growth_mu, self.spec.growth_sigma)
        disp = F * self.spec.dt
        mag = np.maximum(np.abs(disp[0]), np.abs(disp[1]))
        disp = disp * np.where(mag > 0.9, 0.9 / np.maximum(mag, 1e-12), 1.0)

        # 2) Transport: A and its cohorts by the identical reintegration operator
        moved = reintegrate([st.A, *list(st.cohorts_A)], disp)
        A = moved[0]; CA = np.stack(moved[1:], axis=0)

        # 3) Reservoir transport: isotropic diffusion, identical operator for R and its cohorts
        d = self.tspec.reservoir_diffusion
        diffused = _diffuse([st.R, *list(st.cohorts_R)], d)
        R = diffused[0]; CR = np.stack(diffused[1:], axis=0)

        # 4) Balanced local exchange (spatially generic, detector-independent). OFF when exchange_rate == 0.
        if self.tspec.exchange_rate > 0.0:
            Gp = np.maximum(G, 0.0); Gm = np.maximum(-G, 0.0)
            delta = self.tspec.exchange_rate * self.spec.dt * (Gp * R - Gm * A)
            delta = np.clip(delta, -A, R)                       # cannot take more than exists
            gain = delta > 0.0; loss = delta < 0.0
            fr = np.zeros_like(delta); fa = np.zeros_like(delta)
            np.divide(delta, R, out=fr, where=gain & (R > 0))   # fraction of R transferred to A
            np.divide(-delta, A, out=fa, where=loss & (A > 0))  # fraction of A transferred to R
            transfer_R2A = CR * fr[None, :, :]
            transfer_A2R = CA * fa[None, :, :]
            CA = CA + transfer_R2A - transfer_A2R
            CR = CR - transfer_R2A + transfer_A2R
            A = A + delta; R = R - delta
        return ThroughputState(A, R, CA, CR, st.step + 1)

    def simulate(self, st: ThroughputState, steps: int, snapshot_interval: int) -> list[ThroughputState]:
        out = [ThroughputState(st.A.copy(), st.R.copy(), st.cohorts_A.copy(), st.cohorts_R.copy(), 0)]
        cur = st
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % snapshot_interval == 0 or t == steps:
                out.append(ThroughputState(cur.A.copy(), cur.R.copy(), cur.cohorts_A.copy(), cur.cohorts_R.copy(), t))
        return out
