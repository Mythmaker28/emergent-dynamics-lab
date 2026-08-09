"""PUBLIC_PATH_ADAPTIVE_INTERFACE_00 — the constructed LawSpec.

PROGRAM_STATUS = SEPARATE_MODEL_CONSTRUCTION, NOT CONFIRMATION OF sc_mcm.

WHAT THIS IS. The frozen EXP-SC-00 scaffold physics, unchanged, plus the frozen sc_mcm memory
WRITER, unchanged, plus EXACTLY ONE new coupling: a single already-existing internal scalar
modulates the permeability of the material-bath faces to the two existing public fields c and N.

THE PERMITTED CAUSAL GRAPH, and the only one this engine implements:

    public realized c/N flux -> Psi -> z -> kappa(z) -> public realized c/N flux
                             -> material dynamics -> externally observable future response

WHAT WAS REMOVED, and why. The parent sc_mcm has two PRIVATE couplings from the memory to
function: lam_plus (m_plus -> uptake) and lam_minus (m_minus -> attractant production). Both are
direct z -> response paths that bypass the public field, and both are forbidden by the permitted
graph. They are set to zero IDENTICALLY here -- not as a parameter, but structurally. The
nesting target is therefore the ROOT LawSpec of this whole line, the frozen `ScaffoldEngine` of
`exp_sc_00`, which sc_mcm itself reduces to when both couplings vanish (DOMC fixture 2, bit-exact).

  z            : m1, the FIRST memory component. Chosen because it is the coordinate the parent
                 line certified as robust (TCA-01 certifies h1; SMC-01 found h2 homogenises while
                 h1 persists; H2-CERT-01 recorded h2 as transient under deep turnover) AND because
                 it is unsaturated in this configuration, unlike m2 which clips at 1.0. Frozen
                 before any outcome of this programme.

  kappa(z)     = 1 + g * tanh(z)          bounded, odd, centred at z = 0
  face factor  = 0.5 * (kappa(z_i) + kappa(z_j))   symmetric in the two cells, so translation and
                 rotation invariant and owner-label symmetric
  applied to   : the diffusive transport of c AND of N, with the SAME factor. H is not encoded as
                 secretion of one species and L as another.

  g in {-1/3, 0, +1/3}. |g| = 1/3 is FIXED, not tuned: positivity needs |g| < 1, and the frozen
  requirement that the permeability contrast not exceed 2x native gives (1+g)/(1-g) <= 2, i.e.
  g <= 1/3. The largest value satisfying both constraints is taken so that the weakest detectable
  coupling is not confounded with numerical noise; it is not selected on any ownership outcome.

  Fresh material begins with z = 0: the `Mf += g*m` inheritance term of the parent is REMOVED, so
  new mass dilutes the extensive memory. Any persistence through turnover must be physically
  rewritten, never inherited.

NOTHING ELSE. No component identity, no history label, no provenance, no tracker, no future
outcome, and no set-point enters the dynamics anywhere.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/claude/sweep")
from dataclasses import dataclass
import numpy as np

from edlab.substrates.scaffold.engine import ScaffoldEngine, ScaffoldSpec, lap, EPS
from edlab.experiments.sc_iom.engine import IOMState


def _tmean(X):
    return 0.25 * (np.roll(X, 1, -2) + np.roll(X, -1, -2)
                   + np.roll(X, 1, -1) + np.roll(X, -1, -1))


@dataclass(frozen=True)
class PPAIParams:
    # --- writer, taken UNCHANGED from the frozen sc_mcm MCParams -------------------------
    eta_w: float = 0.05
    eta_d1: float = 0.03
    eta_d2: float = 0.003
    eta_t: float = 0.010
    D_m: float = 0.010
    k_exp: float = 2.0
    k_up: float = 1.0
    n_comp: int = 2
    # --- the ONE new coupling ------------------------------------------------------------
    gain: float = 0.0            # g in {-1/3, 0, +1/3}
    z_index: int = 0             # z = m1

    @property
    def eta_d(self):
        return (self.eta_d1, self.eta_d2)


GAIN_CLASSES = {"NEGATIVE_FEEDBACK": -1.0 / 3.0,
                "ZERO_FEEDBACK": 0.0,
                "POSITIVE_FEEDBACK": +1.0 / 3.0}
MAX_CONTRAST = 2.0


def kappa(z, g):
    """bounded, odd, centred. kappa(0) = 1 exactly for every g."""
    return 1.0 + g * np.tanh(z)


class PPAIEngine(ScaffoldEngine):
    def __init__(self, spec: ScaffoldSpec, par: PPAIParams, tracer):
        super().__init__(spec, tracer)
        self.par = par

    # ---------------------------------------------------------------- the adaptive interface
    def _face_transport(self, X, kap):
        """Divergence of a face flux with a symmetric face permeability.

        With kap identically 1 this is ALGEBRAICALLY lap(X). To keep the nested null BIT-exact
        rather than merely equal to round-off, the zero-gain case takes the frozen `lap`
        expression itself; the general branch is verified against it in the fixtures, where the
        residual is reported rather than assumed."""
        if self.par.gain == 0.0:
            return lap(X)
        out = np.zeros_like(X)
        for axis in (-2, -1):
            kf = 0.5 * (kap + np.roll(kap, -1, axis))          # face between i and i+1
            fl = kf * (np.roll(X, -1, axis) - X)
            out += fl - np.roll(fl, 1, axis)
        return out

    # ------------------------------------------------------------------------------- step
    def step(self, st: IOMState) -> IOMState:
        sp, mp, dt = self.spec, self.par, self.spec.dt
        rho, U, V, c, N, C, Mf = st.rho, st.U, st.V, st.c, st.N, st.C, st.Mf
        r_safe = np.maximum(rho, EPS)
        frac = C / r_safe
        fU, fV = U / r_safe, V / r_safe
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

        # ---- growth: NO private memory coupling. This is the frozen scaffold uptake. -------
        u, v = U / np.maximum(rho, EPS), V / np.maximum(rho, EPS)
        sig = (u - v) / (u + v + EPS)
        qq = np.maximum(0.0, 1.0 - rho / sp.rho_max)
        g = dt * sp.g0 * rho * N * qq * (1.0 + sp.beta * sig)
        g = np.clip(g, 0.0, np.maximum(N, 0.0))
        uptake = g.copy()
        N = N - g
        rho = rho + g
        U = U + g * u
        V = V + g * v
        # fresh material carries z = 0: the parent's `Mf += g * m` inheritance is REMOVED
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
            u = np.clip(u, 0.0, None) * alive
            v = np.clip(v, 0.0, None) * alive
            U = rho * u
            V = rho * v

        # ---- the WRITER, unchanged from the frozen sc_mcm --------------------------------
        alive = rho > 1e-4
        m = Mf / np.maximum(rho, EPS)[None, :, :]
        up_ref = float(uptake[alive].mean()) if alive.any() else 0.0
        Psi = np.tanh(mp.k_exp * (N - c) + mp.k_up * (uptake - up_ref))
        newm = np.empty_like(m)
        for kk in range(mp.n_comp):
            mk = m[kk]
            dmk = (mp.eta_w * Psi - mp.eta_d[kk] * mk
                   + mp.eta_t * (_tmean(mk) - mk) + mp.D_m * lap(mk))
            mk = mk + dt * dmk * alive
            newm[kk] = np.clip(mk, -1.0, 1.0) * alive
        Mf = rho * newm

        # ---- THE ONE NEW COUPLING: z modulates the public interface, for c AND for N ------
        z = newm[mp.z_index] * alive                       # z = 0 wherever there is no matter
        kap = kappa(z, mp.gain)
        c = c + dt * (sp.D_c * self._face_transport(c, kap) + sp.s * st.rho - sp.delta * c)
        N = N + dt * (sp.D_N * self._face_transport(N, kap) + sp.F * (sp.N0 - N))
        return IOMState(rho, U, V, c, N, C, uptake, Mf, st.step + 1)


def z_field(st, par=PPAIParams()):
    """the public-facing definition of z, for auditors only."""
    m = st.Mf / np.maximum(st.rho, EPS)[None, :, :]
    return m[par.z_index] * (st.rho > 1e-4)
