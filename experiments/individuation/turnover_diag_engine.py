"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — diagnostic engine variants (DEV only; clean ablations of EXISTING paths).

Subclasses the frozen MultiChannelMemoryEngine and toggles exactly two existing terms:
  * up_ref_zero    : set the GLOBAL write reference up_ref := 0 (keeps the LOCAL uptake term; removes the only
                     world-global scalar in the write). Diagnostic of the known global channel (TASK 3C).
  * copy_disabled  : drop the passive-inheritance term `Mf += g*m` so new growth does NOT inherit local memory
                     (old material unchanged). Clean ablation of the passive-copy path (TASK 3E).

With both flags False, step() MUST be byte-identical to the base engine (validated). This is NOT new physics: both
toggles zero out a single pre-existing term, exactly as the ablation engine zeroes lam_plus/lam_minus.
"""
from __future__ import annotations
import numpy as np
from edlab.substrates.scaffold.engine import lap, EPS
from edlab.experiments.sc_iom.engine import IOMState, _tmean
from edlab.experiments.sc_mcm.engine import MultiChannelMemoryEngine


class DiagEngine(MultiChannelMemoryEngine):
    def __init__(self, spec, mem, tracer, up_ref_zero=False, copy_disabled=False):
        super().__init__(spec, mem, tracer)
        self.up_ref_zero = up_ref_zero
        self.copy_disabled = copy_disabled

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

        u, v = U / np.maximum(rho, EPS), V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        m_plus = np.tanh(m[0] + m[1])
        qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
        g = dt * sp.g0 * rho * N * qq * (1.0 + sp.beta * sig) * (1.0 + mp.lam_plus * m_plus)
        g = np.clip(g, 0.0, np.maximum(N, 0.0))
        uptake = g.copy()
        N = N - g; rho = rho + g; U = U + g * u; V = V + g * v
        if not self.copy_disabled:
            Mf = Mf + g[None, :, :] * m                    # PASSIVE COPY (ablated when copy_disabled)
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

        alive = rho > 1e-4
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        up_ref = 0.0 if self.up_ref_zero else (float(uptake[alive].mean()) if alive.any() else 0.0)  # GLOBAL ref ablation
        Psi = np.tanh(mp.k_exp * (N - c) + mp.k_up * (uptake - up_ref))
        eta_d = mp.eta_d
        newm = np.empty_like(m)
        for k in range(mp.n_comp):
            mk = m[k]
            dmk = mp.eta_w * Psi - eta_d[k] * mk + mp.eta_t * (_tmean(mk) - mk) + mp.D_m * lap(mk)
            mk = mk + dt * dmk * alive
            newm[k] = np.clip(mk, -1.0, 1.0) * alive
        Mf = rho * newm

        m_minus = np.tanh(newm[0] - newm[1])
        c = c + dt * (sp.D_c * lap(c) + sp.s * rho0 * (1.0 + mp.lam_minus * m_minus) - sp.delta * c)
        N = N + dt * (sp.D_N * lap(N) + sp.F * (sp.N0 - N))
        return IOMState(rho, U, V, c, N, C, uptake, Mf, st.step + 1)
