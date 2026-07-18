"""EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00 — orthogonal functional readout of the EXISTING memory.

The WRITING equations are frozen from IOM-00 (dc04f5d): the same m=(m1,m2) field, written by the same
local experience signal, forgotten on two timescales, templated, diffused, inherited by new material.

Only the READOUT is expanded to two orthogonal scalar channels (Level R1):
    m_plus  = m1 + m2   (accumulated experience / dose)  -> nutrient UPTAKE   (as in IOM-00)
    m_minus = m1 - m2   (temporal-order contrast)         -> attractant PRODUCTION (new channel)
    uptake_eff        = uptake        * (1 + lam_plus  * tanh(m_plus))
    c_production_eff  = s * rho       * (1 + lam_minus * tanh(m_minus))
Backward compatibility: lam_minus=0 reproduces IOM-00 bit-identically; lam_plus=lam_minus=0 reproduces the
frozen scaffold. No writing parameter is changed. No tags/IDs/cohorts enter the physics.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ...substrates.scaffold.engine import ScaffoldEngine, ScaffoldSpec, lap, EPS
from ..sc_iom.engine import IOMState, _tmean


@dataclass(frozen=True)
class MCParams:
    eta_w: float = 0.05
    eta_d1: float = 0.03
    eta_d2: float = 0.003
    eta_t: float = 0.010
    D_m: float = 0.010
    lam_plus: float = 0.25      # m_plus -> uptake  (== IOM-00 lam_m)
    lam_minus: float = 0.15     # m_minus -> attractant production (NEW; 0 recovers IOM-00)
    k_exp: float = 2.0
    k_up: float = 1.0
    n_comp: int = 2

    @property
    def eta_d(self):
        return (self.eta_d1, self.eta_d2)


class MultiChannelMemoryEngine(ScaffoldEngine):
    def __init__(self, spec: ScaffoldSpec, mem: MCParams, tracer):
        super().__init__(spec, tracer)
        self.mem = mem

    def step(self, st: IOMState) -> IOMState:
        sp = self.spec; mp = self.mem; dt = sp.dt
        rho, U, V, c, N, C, Mf = st.rho, st.U, st.V, st.c, st.N, st.C, st.Mf
        rho0 = rho
        r_safe = np.maximum(rho, EPS)
        frac = C / r_safe; fU = U / r_safe; fV = V / r_safe; fM = Mf / r_safe[None, :, :]

        drho = np.zeros_like(rho); dU = np.zeros_like(U); dV = np.zeros_like(V)
        dC = np.zeros_like(C); dM = np.zeros_like(Mf)
        for axis in (-2, -1):
            fl = self._face_flux(rho, c, axis)
            donor_i = fl > 0

            def donor(f):
                return np.where(donor_i, f, np.roll(f, -1, axis))

            drho += -(fl - np.roll(fl, 1, axis))
            gu = fl * donor(fU); gv = fl * donor(fV)
            dU += -(gu - np.roll(gu, 1, axis)); dV += -(gv - np.roll(gv, 1, axis))
            fdon = np.where(donor_i[None, ...], frac, np.roll(frac, -1, axis))
            cf = fl[None, ...] * fdon; dC += -(cf - np.roll(cf, 1, axis))
            mdon = np.where(donor_i[None, ...], fM, np.roll(fM, -1, axis))
            gm = fl[None, ...] * mdon; dM += -(gm - np.roll(gm, 1, axis))

        rho = rho + dt * drho; U = U + dt * dU; V = V + dt * dV; C = C + dt * dC; Mf = Mf + dt * dM

        # CHANNEL 1: m_plus -> uptake (identical to IOM-00 when lam_plus plays lam_m)
        u, v = U / np.maximum(rho, EPS), V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        m_plus = np.tanh(m[0] + m[1])
        qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
        g = dt * sp.g0 * rho * N * qq * (1.0 + sp.beta * sig) * (1.0 + mp.lam_plus * m_plus)
        g = np.clip(g, 0.0, np.maximum(N, 0.0))
        uptake = g.copy()
        N = N - g; rho = rho + g; U = U + g * u; V = V + g * v
        Mf = Mf + g[None, :, :] * m
        C[self.tracer.active_feed_cohort(st.step)] += g

        keep = 1.0 - dt * sp.k
        rho = rho * keep; U = U * keep; V = V * keep; C = C * keep; Mf = Mf * keep

        if sp.a > 0.0:
            alive = rho > 1e-4
            u = np.where(alive, U / np.maximum(rho, EPS), 0.0)
            v = np.where(alive, V / np.maximum(rho, EPS), 0.0)
            du = sp.a / (1.0 + (v / sp.K) ** 2) - u
            dv = sp.a / (1.0 + (u / sp.K) ** 2) - v
            u = u + dt * (sp.tau * du + sp.D_int * lap(u) * alive)
            v = v + dt * (sp.tau * dv + sp.D_int * lap(v) * alive)
            u = np.clip(u, 0.0, None) * alive; v = np.clip(v, 0.0, None) * alive
            U = rho * u; V = rho * v

        # MEMORY intensive update (frozen IOM-00 writing)
        alive = rho > 1e-4
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        up_ref = float(uptake[alive].mean()) if alive.any() else 0.0
        Psi = np.tanh(mp.k_exp * (N - c) + mp.k_up * (uptake - up_ref))
        eta_d = mp.eta_d
        newm = np.empty_like(m)
        for k in range(mp.n_comp):
            mk = m[k]
            dmk = mp.eta_w * Psi - eta_d[k] * mk + mp.eta_t * (_tmean(mk) - mk) + mp.D_m * lap(mk)
            mk = mk + dt * dmk * alive
            newm[k] = np.clip(mk, -1.0, 1.0) * alive
        Mf = rho * newm

        # CHANNEL 2 (NEW): m_minus -> attractant PRODUCTION. lam_minus=0 -> identical to IOM-00 c update.
        m_minus = np.tanh(newm[0] - newm[1])
        c = c + dt * (sp.D_c * lap(c) + sp.s * rho0 * (1.0 + mp.lam_minus * m_minus) - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) + sp.F * (sp.N0 - N))
        return IOMState(rho, U, V, c, N, C, uptake, Mf, st.step + 1)
