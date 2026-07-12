"""EXP-MA-00: minimal open MULTISTABLE active-droplet / catalytic-field substrate.

Protocol: docs/experiments/EXP_MA_00_PROTOCOL.md (SHA f59dd700baac59620c50f739b2fb2ad6ce4b0e13), frozen first.

Two catalytic species A and B COHERE together (both climb a shared attractant c that both produce) but DEMIX from
each other (each is pushed down the gradient of the other, strength `lam`). Growth is species-preserving (A makes A),
so an internal morphology is maintained across complete constituent turnover.

lam = 0 is the built-in R8 NEGATIVE CONTROL: demixing off => one interchangeable entity type => R8-A/R8-B must FAIL.
Exact limits: g0 = k = 0 conserves rho_A and rho_B separately; chi0 = 0 removes cohesion.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..reaction_diffusion.engine import TracerSpec


@dataclass(frozen=True)
class MultiSpec:
    size: int = 64
    dt: float = 0.1
    chi0: float = 6.0
    lam: float = 3.0            # DEMIXING strength -- the multistability parameter. lam = 0 -> negative control.
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
class MAState:
    A: np.ndarray
    B: np.ndarray
    c: np.ndarray
    N: np.ndarray
    C: np.ndarray                # (n_cohorts,H,W); sum over axis 0 == A + B, exactly, cell-wise
    step: int = 0

    @property
    def rho(self) -> np.ndarray:
        return self.A + self.B

    def copy(self) -> "MAState":
        return MAState(self.A.copy(), self.B.copy(), self.c.copy(), self.N.copy(), self.C.copy(), self.step)


def lap(X: np.ndarray) -> np.ndarray:
    return (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1) - 4.0 * X)


class MultiEngine:
    def __init__(self, spec: MultiSpec, tracer: TracerSpec):
        self.spec = spec
        self.tracer = tracer

    def _flux(self, rX, rY, rho, c, axis):
        """Conservative face flux of species X. Positive = from cell i to cell i+1."""
        sp = self.spec
        rX_p = np.roll(rX, -1, axis)
        rY_p = np.roll(rY, -1, axis)
        rho_p = np.roll(rho, -1, axis)
        c_p = np.roll(c, -1, axis)
        dc = c_p - c
        dY = rY_p - rY
        c_face = 0.5 * (c + c_p)
        chi = sp.chi0 / (1.0 + (c_face / sp.c_sat) ** 2)
        # drift velocity of X on this face: cohesion (+chi grad c) minus demixing (-lam grad rho_Y)
        v = chi * dc - sp.lam * dY
        up_is_i = v > 0
        rX_up = np.where(up_is_i, rX, rX_p)
        rho_dn = np.where(up_is_i, rho_p, rho)               # volume exclusion on the RECEIVING cell
        adv = v * rX_up * np.maximum(0.0, 1.0 - rho_dn / sp.rho_max)
        dif = -sp.D_rho * (rX_p - rX)
        return adv + dif

    def step(self, st: MAState) -> MAState:
        sp = self.spec
        dt = sp.dt
        A, B, c, N, C = st.A, st.B, st.c, st.N, st.C
        rho = A + B
        eps = 1e-30
        frac = C / np.maximum(rho, eps)

        dA = np.zeros_like(A); dB = np.zeros_like(B); dC = np.zeros_like(C)
        for axis in (-2, -1):
            fA = self._flux(A, B, rho, c, axis)
            fB = self._flux(B, A, rho, c, axis)
            tot = fA + fB                                     # cohorts ride the TOTAL material flux
            donor_i = tot > 0
            frac_p = np.roll(frac, -1, axis)
            fdon = np.where(donor_i[None, ...], frac, frac_p)
            cf = tot[None, ...] * fdon
            dA += -(fA - np.roll(fA, 1, axis))
            dB += -(fB - np.roll(fB, 1, axis))
            dC += -(cf - np.roll(cf, 1, axis))

        A = A + dt * dA
        B = B + dt * dB
        C = C + dt * dC

        rho2 = A + B
        qq = np.maximum(0.0, 1.0 - rho2 / sp.rho_max)
        gA = dt * sp.g0 * A * N * qq                          # SPECIES-PRESERVING autocatalysis: A makes A
        gB = dt * sp.g0 * B * N * qq
        A = A + gA
        B = B + gB
        C[self.tracer.active_feed_cohort(st.step)] += gA + gB
        keep = 1.0 - dt * sp.k
        A = A * keep; B = B * keep; C = C * keep

        c = c + dt * (sp.D_c * lap(c) + sp.s * rho - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) - sp.g0 * rho * N + sp.F * (sp.N0 - N))
        return MAState(A, B, c, N, C, st.step + 1)

    def simulate(self, st: MAState, steps: int, cadence: int) -> list[MAState]:
        out = [st.copy()]
        cur = st
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % cadence == 0:
                out.append(cur.copy())
        return out
