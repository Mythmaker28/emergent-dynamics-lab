"""Open chemotactic self-aggregation substrate (EXP-CH-00).

Protocol: docs/experiments/EXP_CH_00_PROTOCOL.md (SHA 119188cf74052267cc02239c8d87e40630ce7147), frozen first.

Cohesion is CONSTITUTIVE: cells secrete c and climb grad(c), so the field they produce pulls them together.
The finite-density regularization is part of the core, NOT a later rescue:
  chi(rho,c) = chi0 * 1/(1+(c/c_sat)^2)      <- saturating (receptor) chemotactic response
                    * max(0, 1 - rho/rho_max) <- volume exclusion; chi -> 0 exactly at rho_max
The volume-filling factor makes the system globally bounded: blow-up is impossible, rho <= rho_max is preserved.

Exact controlled limits: g0 = k = 0 -> total rho conserved exactly (flux form).  chi0 = 0 -> chemotaxis removed
(the causal control for cohesion).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..reaction_diffusion.engine import TracerSpec


@dataclass(frozen=True)
class ChemoSpec:
    size: int = 64
    dt: float = 0.1
    chi0: float = 6.0
    D_rho: float = 0.12
    D_c: float = 0.50
    s: float = 0.20
    delta: float = 0.08
    g0: float = 0.08
    k: float = 0.04
    F: float = 0.05
    D_N: float = 0.5
    N0: float = 1.0
    rho_max: float = 1.0
    c_sat: float = 1.0

    @property
    def is_closed(self) -> bool:
        return self.g0 == 0.0 and self.k == 0.0


@dataclass
class CHState:
    rho: np.ndarray
    c: np.ndarray
    N: np.ndarray
    C: np.ndarray          # (n_cohorts, H, W); sum over axis 0 == rho, exactly, cell-wise
    step: int = 0

    def copy(self) -> "CHState":
        return CHState(self.rho.copy(), self.c.copy(), self.N.copy(), self.C.copy(), self.step)


def lap(X: np.ndarray) -> np.ndarray:
    return (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1) - 4.0 * X)


class ChemoEngine:
    def __init__(self, spec: ChemoSpec, tracer: TracerSpec):
        self.spec = spec
        self.tracer = tracer

    def _faces(self, rho: np.ndarray, c: np.ndarray, axis: int):
        """Conservative face flux between cell i and its neighbour i+1 along `axis`.
        Positive flux = net transport FROM cell i TO cell i+1. Donor cell is chosen upwind."""
        sp = self.spec
        rho_p = np.roll(rho, -1, axis)          # neighbour i+1
        c_p = np.roll(c, -1, axis)
        dc = c_p - c                            # chemotactic drift is +chi*grad(c): sign(dc) sets the direction
        c_face = 0.5 * (c + c_p)
        up_is_i = dc > 0                        # cells climb the gradient: if c_{i+1} > c_i, donor is i
        rho_up = np.where(up_is_i, rho, rho_p)       # DONOR   (supplies the cells)
        rho_dn = np.where(up_is_i, rho_p, rho)       # RECEIVER (must have room for them)
        # VOLUME EXCLUSION is evaluated on the RECEIVER: a cell already at rho_max cannot be filled further.
        # (Evaluating it on the donor, as in my first draft, still permits overfilling -- observed rho = 1.408.)
        chi = (sp.chi0 / (1.0 + (c_face / sp.c_sat) ** 2)) * np.maximum(0.0, 1.0 - rho_dn / sp.rho_max)
        chemo = chi * dc * rho_up               # advective, upwind, saturating + volume-excluded
        diff = -sp.D_rho * (rho_p - rho)        # Fickian
        flux = chemo + diff
        # donor cell for COMPOSITION: whichever cell the net flux leaves
        donor_is_i = flux > 0
        return flux, donor_is_i

    def step(self, st: CHState) -> CHState:
        sp = self.spec
        dt = sp.dt
        rho, c, N, C = st.rho, st.c, st.N, st.C
        eps = 1e-30
        frac = C / np.maximum(rho, eps)                       # local cohort composition (sums to 1 where rho>0)

        drho = np.zeros_like(rho)
        dC = np.zeros_like(C)
        for axis in (-2, -1):
            flux, donor_is_i = self._faces(rho, c, axis)
            frac_p = np.roll(frac, -1, axis + 0)
            frac_donor = np.where(donor_is_i[None, ...], frac, frac_p)
            cflux = flux[None, ...] * frac_donor              # SAME face flux, donor composition => sum_c == flux
            drho += -(flux - np.roll(flux, 1, axis))          # -div
            dC += -(cflux - np.roll(cflux, 1, axis))

        rho = rho + dt * drho
        C = C + dt * dC

        # growth (into the ACTIVE temporal cohort) and homogeneous death (removes local cohort proportions).
        # The SAME volume-filling factor regularizes the SOURCE: growth vanishes at rho_max. Without it the
        # finite-density guarantee is vacuous -- growth alone drove rho to 1.408 > rho_max in the first draft.
        g = dt * sp.g0 * rho * N * np.maximum(0.0, 1.0 - rho / sp.rho_max)
        rho = rho + g
        C[self.tracer.active_feed_cohort(st.step)] += g
        keep = 1.0 - dt * sp.k
        rho = rho * keep
        C = C * keep

        c = c + dt * (sp.D_c * lap(c) + sp.s * st.rho - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) - sp.g0 * st.rho * N + sp.F * (sp.N0 - N))
        return CHState(rho, c, N, C, st.step + 1)

    def simulate(self, st: CHState, steps: int, cadence: int) -> list[CHState]:
        out = [st.copy()]
        cur = st
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % cadence == 0:
                out.append(cur.copy())
        return out
