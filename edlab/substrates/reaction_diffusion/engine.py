"""Minimal genuinely OPEN reaction-diffusion substrate (Gray-Scott) with passive origin tracers.

    dU/dt = Du*lap(U) - U*V^2 + F*(1 - U)      feed F is a SPATIALLY HOMOGENEOUS source (+F) and removal (-F*U)
    dV/dt = Dv*lap(V) + U*V^2 - (F + k)*V      removal (F+k) is SPATIALLY HOMOGENEOUS

Feed and removal are scalars applied identically at every cell and depend only on the LOCAL field value: they are
spatially homogeneous and detector-independent, so they cannot impose a spatial pattern (verified by the
HOMOGENEITY NULL: a uniform state stays uniform forever).

EXACT CONTROLLED LIMIT: F = 0 AND k = 0 removes the source and both sinks, leaving diffusion + the U->V reaction
transfer, which conserves U+V EXACTLY (a closed system). This is the matched CLOSED control for the OPEN system.

PASSIVE ORIGIN TRACERS: cohorts partition BOTH species (sum_c CU = U, sum_c CV = V). Indices 0..G-1 label initial
spatial origin; index G is the FEED cohort = material introduced from OUTSIDE by the feed. Cohorts are moved by
exactly the same operators as their fields (identical diffusion; reaction transfer carries the LOCAL cohort
proportions of the source species; removal scales all cohorts equally; the feed deposits into the FEED cohort).
Cohorts NEVER influence U, V or any rate.

Operator-split explicit scheme (declared): diffuse -> reaction transfer -> V removal -> U removal + feed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class GrayScottSpec:
    size: int = 96
    Du: float = 0.16
    Dv: float = 0.08
    F: float = 0.035          # feed (0 = closed limit)
    k: float = 0.060          # extra V removal (0 with F=0 -> closed limit)
    dt: float = 1.0

    def __post_init__(self) -> None:
        for v in (self.Du, self.Dv, self.F, self.k, self.dt):
            if not np.isfinite(v):
                raise ValueError("GrayScottSpec values must be finite")
        if self.Du < 0 or self.Dv < 0 or self.F < 0 or self.k < 0 or self.dt <= 0:
            raise ValueError("Du,Dv,F,k must be >=0 and dt>0")
        if max(self.Du, self.Dv) * self.dt > 0.25:
            raise ValueError("explicit diffusion stability requires max(Du,Dv)*dt <= 0.25")

    @property
    def is_closed(self) -> bool:
        return self.F == 0.0 and self.k == 0.0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def laplacian(X: np.ndarray) -> np.ndarray:
    """Periodic 5-point Laplacian on the LAST TWO axes (works for (H,W) and stacked (C,H,W))."""
    return (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1) - 4.0 * X)


def laplacian_reference(X: np.ndarray) -> np.ndarray:
    """Independent reference path (explicit shifted sums) for agreement testing."""
    out = -4.0 * X.copy()
    for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
        out = out + np.roll(X, sh, axis=ax)
    return out


@dataclass
class RDState:
    U: np.ndarray
    V: np.ndarray
    CU: np.ndarray            # (C,H,W) sum == U
    CV: np.ndarray            # (C,H,W) sum == V
    step: int = 0

    def total(self) -> float:
        return float(self.U.sum() + self.V.sum())


@dataclass(frozen=True)
class TracerSpec:
    """Passive origin tracers: spatial-origin cohorts + ROTATING TEMPORAL FEED cohorts (pulse-chase).

    A single permanent FEED cohort saturates: once feed-origin mass dominates a structure, the cohort composition
    stops changing and CONTINUED turnover becomes invisible. Temporal feed cohorts fix this: material fed during
    time-window w is labelled by w, so a structure that keeps replacing its material keeps shifting its composition
    toward newer temporal cohorts, and M(tau) keeps registering turnover indefinitely.
    """

    n_spatial: int = 8          # initial-origin spatial cohorts (verified resolution, D-024)
    n_temporal: int = 8         # rotating temporal FEED cohorts (SELECTED, EXP-RD-00B)
    tau_feed: int = 250         # steps per temporal cohort (SELECTED); cycle = n_temporal * tau_feed

    def __post_init__(self) -> None:
        if self.n_spatial < 1 or self.n_temporal < 1 or self.tau_feed < 1:
            raise ValueError("TracerSpec values must be >= 1")

    @property
    def n_cohorts(self) -> int:
        return self.n_spatial + self.n_temporal

    @property
    def cycle(self) -> int:
        return self.n_temporal * self.tau_feed

    def active_feed_cohort(self, step: int) -> int:
        """Index of the currently active temporal feed cohort at `step`."""
        return self.n_spatial + ((step // self.tau_feed) % self.n_temporal)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RDEngine:
    spec: GrayScottSpec
    tracer: TracerSpec = field(default_factory=TracerSpec)

    def step(self, st: RDState) -> RDState:
        s = self.spec
        U, V, CU, CV = st.U, st.V, st.CU, st.CV
        dt = s.dt
        # --- A) diffusion (identical operator on fields and their cohorts)
        U = U + dt * s.Du * laplacian(U)
        V = V + dt * s.Dv * laplacian(V)
        CU = CU + dt * s.Du * laplacian(CU)      # vectorized over the cohort axis; identical operator
        CV = CV + dt * s.Dv * laplacian(CV)
        # --- B) reaction transfer U -> V (material moves; carries U's LOCAL cohort proportions)
        r = dt * U * V * V
        r = np.clip(r, 0.0, np.maximum(U, 0.0))
        frac = np.zeros_like(U)
        np.divide(r, U, out=frac, where=U > 0)
        frac = np.clip(frac, 0.0, 1.0)
        transfer = CU * frac[None, :, :]
        CU = CU - transfer
        CV = CV + transfer
        U = U - r
        V = V + r
        # --- C) V removal (homogeneous rate; scales every cohort equally)
        keepV = 1.0 - dt * (s.F + s.k)
        V = V * keepV
        CV = CV * keepV
        # --- D) U removal (-F*U) + FEED source (+F), both spatially homogeneous
        keepU = 1.0 - dt * s.F
        U = U * keepU
        CU = CU * keepU
        if s.F > 0.0:
            U = U + dt * s.F
            active = self.tracer.active_feed_cohort(st.step)   # PULSE-CHASE: fed material is labelled by WHEN it entered
            CU[active] = CU[active] + dt * s.F
        return RDState(U, V, CU, CV, st.step + 1)

    def simulate(self, st: RDState, steps: int, snapshot_interval: int) -> list[RDState]:
        out = [RDState(st.U.copy(), st.V.copy(), st.CU.copy(), st.CV.copy(), 0)]
        cur = st
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % snapshot_interval == 0 or t == steps:
                out.append(RDState(cur.U.copy(), cur.V.copy(), cur.CU.copy(), cur.CV.copy(), t))
        return out
