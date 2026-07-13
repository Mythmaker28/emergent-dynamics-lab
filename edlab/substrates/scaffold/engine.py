"""EXP-SC-00: open SCAFFOLD (cohesion) + CONFINED INTERNAL bistable network (identity), functionally orthogonal.

Protocol: docs/experiments/EXP_SC_00_PROTOCOL.md (SHA aed457c2d48861781dc00aeceab7df017c995f0a), frozen first.

Cohesion is carried ONLY by the scaffold (rho, shared attractant c, volume exclusion). The internal network (u, v)
NEVER enters chi, c, or any cohesive term -- structuring the interior costs the droplet no cohesion. That is the
whole point, and it is what EXP-MA-00 lacked (D-043).

Limits: a=0 -> internal network off (O1 scaffold-only control). beta=0 -> internal state causally inert (O4 negative
control). g0=k=0 -> rho conserved. chi0=0 -> cohesion removed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..reaction_diffusion.engine import TracerSpec

EPS = 1e-12


@dataclass(frozen=True)
class ScaffoldSpec:
    size: int = 64
    dt: float = 0.1
    # --- scaffold (cohesion). FROZEN: these are EXACTLY the parameters of EXP-CH-00 law 2, an R7 survivor (D-038).
    # They are NOT hand-chosen. My first draft hand-set them and O1 failed (PR = 0.821): the protocol specifies the
    # ALREADY-VALIDATED scaffold, and the code did not implement it. That was a bug, and fixing it is not a rescue.
    chi0: float = 9.50000
    D_rho: float = 0.07778
    D_c: float = 0.68000
    s: float = 0.20000
    delta: float = 0.06909
    g0: float = 0.06154
    k: float = 0.02588
    F: float = 0.02421
    D_N: float = 0.5
    N0: float = 1.0
    rho_max: float = 1.0
    c_sat: float = 1.0
    # --- internal bistable toggle (identity). Plays NO part in cohesion.
    a: float = 2.0            # toggle production; a = 0 -> internal network OFF
    K: float = 0.5            # inhibition constant
    D_int: float = 0.008      # SMALL internal diffusion -> domain walls pin -> several metastable interiors
    tau: float = 0.20         # internal reaction rate
    beta: float = 0.6         # internal state -> FUTURE UPTAKE. beta = 0 -> decorative label (negative control)

    @property
    def is_closed(self) -> bool:
        return self.g0 == 0.0 and self.k == 0.0


@dataclass
class SCState:
    rho: np.ndarray
    U: np.ndarray            # extensive internal species (U = rho * u)
    V: np.ndarray
    c: np.ndarray
    N: np.ndarray
    C: np.ndarray            # cohorts; sum_c C == rho exactly
    uptake: np.ndarray       # per-cell nutrient consumed in the last step (behavioural observable)
    step: int = 0

    def conc(self):
        r = np.maximum(self.rho, EPS)
        return self.U / r, self.V / r

    def sigma(self):
        u, v = self.conc()
        return (u - v) / (u + v + EPS)

    def copy(self) -> "SCState":
        return SCState(self.rho.copy(), self.U.copy(), self.V.copy(), self.c.copy(), self.N.copy(),
                       self.C.copy(), self.uptake.copy(), self.step)


def lap(X):
    return (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1) - 4.0 * X)


class ScaffoldEngine:
    def __init__(self, spec: ScaffoldSpec, tracer: TracerSpec):
        self.spec = spec
        self.tracer = tracer

    def _face_flux(self, rho, c, axis):
        sp = self.spec
        rho_p = np.roll(rho, -1, axis)
        c_p = np.roll(c, -1, axis)
        dc = c_p - c
        chi = sp.chi0 / (1.0 + (0.5 * (c + c_p) / sp.c_sat) ** 2)
        up_i = dc > 0
        rho_up = np.where(up_i, rho, rho_p)
        rho_dn = np.where(up_i, rho_p, rho)
        adv = chi * dc * rho_up * np.maximum(0.0, 1.0 - rho_dn / sp.rho_max)
        dif = -sp.D_rho * (rho_p - rho)
        return adv + dif

    def step(self, st: SCState) -> SCState:
        sp = self.spec
        dt = sp.dt
        rho, U, V, c, N, C = st.rho, st.U, st.V, st.c, st.N, st.C
        r_safe = np.maximum(rho, EPS)
        frac = C / r_safe
        fU = U / r_safe                       # internal concentrations ride the scaffold
        fV = V / r_safe

        drho = np.zeros_like(rho); dU = np.zeros_like(U); dV = np.zeros_like(V); dC = np.zeros_like(C)
        for axis in (-2, -1):
            fl = self._face_flux(rho, c, axis)
            donor_i = fl > 0
            def donor(f):
                return np.where(donor_i, f, np.roll(f, -1, axis))
            drho += -(fl - np.roll(fl, 1, axis))
            gu = fl * donor(fU); gv = fl * donor(fV)
            dU += -(gu - np.roll(gu, 1, axis))
            dV += -(gv - np.roll(gv, 1, axis))
            fdon = np.where(donor_i[None, ...], frac, np.roll(frac, -1, axis))
            cf = fl[None, ...] * fdon
            dC += -(cf - np.roll(cf, 1, axis))

        rho = rho + dt * drho
        U = U + dt * dU
        V = V + dt * dV
        C = C + dt * dC

        # BEHAVIOUR: uptake depends on the internal state (beta = 0 -> decorative label)
        u, v = U / np.maximum(rho, EPS), V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
        g = dt * sp.g0 * rho * N * qq * (1.0 + sp.beta * sig)
        g = np.clip(g, 0.0, np.maximum(N, 0.0))
        uptake = g.copy()
        N = N - g
        rho = rho + g
        U = U + g * u                          # new mass INHERITS the local internal state
        V = V + g * v
        C[self.tracer.active_feed_cohort(st.step)] += g

        keep = 1.0 - dt * sp.k                 # homogeneous death: concentrations invariant under turnover
        rho = rho * keep; U = U * keep; V = V * keep; C = C * keep

        # INTERNAL bistable toggle + small internal diffusion, on CONCENTRATIONS, confined to the scaffold
        if sp.a > 0.0:
            alive = rho > 1e-4
            u = np.where(alive, U / np.maximum(rho, EPS), 0.0)
            v = np.where(alive, V / np.maximum(rho, EPS), 0.0)
            du = sp.a / (1.0 + (v / sp.K) ** 2) - u
            dv = sp.a / (1.0 + (u / sp.K) ** 2) - v
            u = u + dt * (sp.tau * du + sp.D_int * lap(u) * alive)
            v = v + dt * (sp.tau * dv + sp.D_int * lap(v) * alive)
            u = np.clip(u, 0.0, None) * alive
            v = np.clip(v, 0.0, None) * alive
            U = rho * u
            V = rho * v

        c = c + dt * (sp.D_c * lap(c) + sp.s * st.rho - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) + sp.F * (sp.N0 - N))
        return SCState(rho, U, V, c, N, C, uptake, st.step + 1)

    def simulate(self, st: SCState, steps: int, cadence: int) -> list[SCState]:
        out = [st.copy()]
        cur = st
        for t in range(1, steps + 1):
            cur = self.step(cur)
            if t % cadence == 0:
                out.append(cur.copy())
        return out
