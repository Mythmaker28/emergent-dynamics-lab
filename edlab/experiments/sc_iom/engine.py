"""EXP-SC-INDIVIDUAL-ORGANIZATIONAL-MEMORY-00 — minimal physics extension.

Adds a bounded, distributed, experience-written organizational-memory field m = (m1, m2) that rides the
scaffold rho exactly as U,V do. m starts at 0 for every entity (no identity tag). It is written by local
environmental experience Psi(N,c,uptake), forgotten (two timescales), spatially templated + diffused, and
inherited by newly grown material. It couples back to function through the uptake term only.

Backward compatibility: with lam_m = 0 the base fields (rho,U,V,c,N,C) evolve BIT-IDENTICALLY to the
frozen scaffold engine (memory is uncoupled); with eta_w = lam_m = 0 the memory stays exactly 0.

Base scaffold physics (chi/D_rho/growth/death/toggle/c/N) is reproduced from the FROZEN engine blob
7c91b91 and is NOT otherwise altered.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ...substrates.scaffold.engine import ScaffoldEngine, ScaffoldSpec, SCState, lap, EPS


@dataclass(frozen=True)
class MemParams:
    eta_w: float = 0.05     # experience writing strength
    eta_d1: float = 0.03    # fast forgetting (recent-experience component m1)
    eta_d2: float = 0.003   # slow forgetting (integrated-history component m2)
    eta_t: float = 0.010    # organizational templating toward local consensus (self-maintenance)
    D_m: float = 0.010      # memory spatial coherence
    lam_m: float = 0.25     # functional coupling into uptake (bounded)
    k_exp: float = 2.0      # experience-signal gain on the local nutrient-attractant balance
    k_up: float = 1.0       # experience-signal gain on uptake surprise
    n_comp: int = 2

    @property
    def eta_d(self):
        return (self.eta_d1, self.eta_d2)


@dataclass
class IOMState:
    rho: np.ndarray
    U: np.ndarray
    V: np.ndarray
    c: np.ndarray
    N: np.ndarray
    C: np.ndarray
    uptake: np.ndarray
    Mf: np.ndarray          # extensive memory: Mf[k] = rho * m_k ; shape (n_comp, n, n)
    step: int = 0

    def conc(self):
        r = np.maximum(self.rho, EPS)
        return self.U / r, self.V / r

    def sigma(self):
        u, v = self.conc()
        return (u - v) / (u + v + EPS)

    def mem(self):
        return self.Mf / np.maximum(self.rho, EPS)[None, :, :]

    def copy(self) -> "IOMState":
        return IOMState(self.rho.copy(), self.U.copy(), self.V.copy(), self.c.copy(), self.N.copy(),
                        self.C.copy(), self.uptake.copy(), self.Mf.copy(), self.step)


def _tmean(X):
    """4-neighbour spatial mean (periodic) -> local organizational template."""
    return 0.25 * (np.roll(X, 1, -2) + np.roll(X, -1, -2) + np.roll(X, 1, -1) + np.roll(X, -1, -1))


class MemoryScaffoldEngine(ScaffoldEngine):
    def __init__(self, spec: ScaffoldSpec, mem: MemParams, tracer):
        super().__init__(spec, tracer)
        self.mem = mem

    def step(self, st: IOMState) -> IOMState:
        sp = self.spec
        mp = self.mem
        dt = sp.dt
        rho, U, V, c, N, C, Mf = st.rho, st.U, st.V, st.c, st.N, st.C, st.Mf
        r_safe = np.maximum(rho, EPS)
        frac = C / r_safe
        fU = U / r_safe
        fV = V / r_safe
        fM = Mf / r_safe[None, :, :]

        drho = np.zeros_like(rho); dU = np.zeros_like(U); dV = np.zeros_like(V)
        dC = np.zeros_like(C); dM = np.zeros_like(Mf)
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
            mdon = np.where(donor_i[None, ...], fM, np.roll(fM, -1, axis))
            gm = fl[None, ...] * mdon
            dM += -(gm - np.roll(gm, 1, axis))

        rho = rho + dt * drho
        U = U + dt * dU
        V = V + dt * dV
        C = C + dt * dC
        Mf = Mf + dt * dM

        # ---- BEHAVIOUR: uptake depends on internal state AND memory (lam_m=0 -> identical to frozen) ----
        u, v = U / np.maximum(rho, EPS), V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        m_read = np.tanh(m.sum(axis=0))                       # both components drive function
        mem_factor = 1.0 + mp.lam_m * m_read                  # == 1.0 exactly when lam_m == 0
        qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
        g = dt * sp.g0 * rho * N * qq * (1.0 + sp.beta * sig) * mem_factor
        g = np.clip(g, 0.0, np.maximum(N, 0.0))
        uptake = g.copy()
        N = N - g
        rho = rho + g
        U = U + g * u
        V = V + g * v
        Mf = Mf + g[None, :, :] * m                            # new material INHERITS local memory
        C[self.tracer.active_feed_cohort(st.step)] += g

        keep = 1.0 - dt * sp.k
        rho = rho * keep; U = U * keep; V = V * keep; C = C * keep; Mf = Mf * keep

        # ---- internal bistable toggle (unchanged frozen dynamics) ----
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

        # ---- MEMORY intensive update: experience writing + forgetting + templating + diffusion ----
        alive = rho > 1e-4
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        # experience signal Psi from LOCAL environment: nutrient-attractant balance + uptake surprise
        up_ref = float(uptake[alive].mean()) if alive.any() else 0.0
        Psi = np.tanh(mp.k_exp * (N - c) + mp.k_up * (uptake - up_ref))
        eta_d = mp.eta_d
        newm = np.empty_like(m)
        for k in range(mp.n_comp):
            mk = m[k]
            dmk = (mp.eta_w * Psi
                   - eta_d[k] * mk
                   + mp.eta_t * (_tmean(mk) - mk)
                   + mp.D_m * lap(mk))
            mk = mk + dt * dmk * alive
            newm[k] = np.clip(mk, -1.0, 1.0) * alive
        Mf = rho * newm

        c = c + dt * (sp.D_c * lap(c) + sp.s * st.rho - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) + sp.F * (sp.N0 - N))
        return IOMState(rho, U, V, c, N, C, uptake, Mf, st.step + 1)
