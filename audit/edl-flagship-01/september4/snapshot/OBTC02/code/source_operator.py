"""OBTC01 §7 — the source-transport-decay operator, derived from the engine, no free parameter.

READ OFF THE FROZEN ENGINE
--------------------------
BIRTH.   `_react` draws  births ~ Binomial(cand, p),  p = min(1, kX * n_X * n_Y),
         cand = min(n_SX, max(free, 0)).  p is ZERO wherever n_Y = 0 or n_X = 0, so with one
         organiser X is created in EXACTLY ONE CELL: the organiser's own. At kX = 1 and
         n_X >= 1, n_Y >= 1 the probability saturates at 1 and the number born is exactly
         min(n_SX, free) at that cell. The source is a point, and its intensity is set by the
         local resource and the local free capacity, not by N_X.

TRANSPORT. `_diffuse` makes four passes per step in the frozen order (+y, -y, +x, -x), each
         moving Binomial(n, q) molecules with q = p_hop / 4, accepted up to the destination's
         free capacity. Ignoring the capacity cap, one step displaces a molecule by
         dy = B1 - B2, dx = B3 - B4 with four independent Bernoulli(q), so per axis

             Var = 2 q (1 - q) =: a        D = a / 2 = q (1 - q)

         and the one-step characteristic function factorises:

             phi(k) = [1 - a (1 - cos k_y)] [1 - a (1 - cos k_x)]

         This is NOT the naive p_hop/4 diffusion constant; the second pass can undo the first.

DECAY.   `_decay` draws  d ~ Binomial(n_X, mu_X)  per cell, independent of position and of the
         neighbourhood. A molecule's age is therefore Geometric with success probability mu_X.

THE CONVOLUTION
---------------
    rho_t(x) = sum_{s <= t} B_s K_{t-s}(x - Y_s),    K_u = (1 - mu)^u P_u

with P_u the u-step free-walk law. It is EXACT if and only if transport never hits the capacity
cap and the organiser's own motion is not coupled to X. Both are measured, not assumed:
`hops_blocked / hops_offered` decides the first, and the second is a structural fact of
`_diffuse`, whose acceptance for Y reads `free()`, which contains n_X. The status is therefore
at best CONDITIONAL_EXACT, and the measurement decides.
"""
from __future__ import annotations

import numpy as np


class Op:
    """Every quantity below is a function of the frozen Spec alone."""

    def __init__(self, sp):
        self.sp = sp
        self.L = int(sp.L)
        self.qX = sp.p_hop_X / 4.0
        self.qY = sp.p_hop_Y / 4.0
        self.aX = 2.0 * self.qX * (1.0 - self.qX)          # per-axis variance per step
        self.aY = 2.0 * self.qY * (1.0 - self.qY)
        self.DX = self.aX / 2.0
        self.DY = self.aY / 2.0
        self.mu = float(sp.muX)
        self.a_rel = self.aX + self.aY                     # relative walk X - Y
        self.D_rel = self.a_rel / 2.0
        self.ell_X = float(np.sqrt(self.DX / self.mu))     # isolated localisation length
        self.ell_rel = float(np.sqrt(self.D_rel / self.mu))

    # ------------------------------------------------------------------ exact discrete profile
    def profile(self, a, L=None):
        """Stationary profile of a unit point source with per-step survival (1 - mu), on the
        L x L torus, EXACT: n_hat(k) = 1 / (1 - (1-mu) phi(k)), inverted by DFT."""
        L = int(L or self.L)
        k = 2.0 * np.pi * np.arange(L) / L
        phi1 = 1.0 - a * (1.0 - np.cos(k))
        phi = phi1[:, None] * phi1[None, :]
        p = np.real(np.fft.ifft2(1.0 / (1.0 - (1.0 - self.mu) * phi)))
        p = np.maximum(p, 0.0)
        return p / p.sum()

    def static_profile(self, L=None):
        """The organiser immobilised: only X moves."""
        return self.profile(self.aX, L)

    def relative_profile(self, L=None):
        """The organiser mobile: the law of X - Y, whose per-step variance is aX + aY."""
        return self.profile(self.a_rel, L)

    # ------------------------------------------------------------------ radial summaries
    @staticmethod
    def _radii(prof, qs=(0.5, 0.8, 0.9)):
        L = prof.shape[0]
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2).ravel()
        w = prof.ravel()
        o = np.argsort(d, kind="stable")
        d, w = d[o], w[o]
        cw = np.cumsum(w) / w.sum()
        return {q: float(d[int(np.searchsorted(cw, q, side="left"))]) for q in qs}

    @staticmethod
    def _second_moment(prof):
        L = prof.shape[0]
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        d2 = d1[:, None] ** 2 + d1[None, :] ** 2
        return float((prof * d2).sum())

    # ------------------------------------------------------------------ closed forms
    def mean_age(self):
        """E[S] for S ~ Geometric(mu) on {0, 1, ...}."""
        return (1.0 - self.mu) / self.mu

    def e_min_age(self):
        """E[min(S, S')] for two independent ages."""
        m = self.mu
        return (1.0 - m) ** 2 / (m * (2.0 - m))

    def predictions(self, L=None):
        L = int(L or self.L)
        stat, rel = self.static_profile(L), self.relative_profile(L)
        r_stat, r_rel = self._radii(stat), self._radii(rel)
        # analytic second moments on the infinite lattice
        r2_stat_inf = 2.0 * self.aX * (1.0 - self.mu) / self.mu
        r2_rel_inf = 2.0 * self.a_rel * (1.0 - self.mu) / self.mu
        # core centre against the organiser: C - Y = E_S[Y_{t-S} - Y_t]
        r2_core = 2.0 * self.aY * self.e_min_age()
        return {
            "L": L,
            "constants": {"q_X": self.qX, "q_Y": self.qY, "a_X": self.aX, "a_Y": self.aY,
                          "D_X": self.DX, "D_Y": self.DY, "a_relative": self.a_rel,
                          "D_relative": self.D_rel, "mu_X": self.mu,
                          "ell_X_isolated": self.ell_X, "ell_relative": self.ell_rel},
            "static_source": {
                "r50": r_stat[0.5], "r80": r_stat[0.8], "r90": r_stat[0.9],
                "second_moment_torus": self._second_moment(stat),
                "second_moment_infinite_lattice": r2_stat_inf,
                "rms_radius": float(np.sqrt(self._second_moment(stat))),
                "relaxation_time_steps": 1.0 / self.mu},
            "mobile_source": {
                "r50": r_rel[0.5], "r80": r_rel[0.8], "r90": r_rel[0.9],
                "second_moment_torus": self._second_moment(rel),
                "second_moment_infinite_lattice": r2_rel_inf,
                "rms_radius": float(np.sqrt(self._second_moment(rel)))},
            "core_to_organiser": {
                "mean_age_steps": self.mean_age(),
                "E_min_age_steps": self.e_min_age(),
                "second_moment": r2_core,
                "rms": float(np.sqrt(r2_core)),
                "mean_modulus_rayleigh": float(np.sqrt(np.pi / 4.0) * np.sqrt(r2_core)),
                "optimal_lag_steps": self.mean_age()},
            "source_off": {
                "decay_law": "N_X(t) = N_X(0) (1 - mu)^t",
                "e_folding_steps": -1.0 / np.log(1.0 - self.mu),
                "half_life_steps": np.log(2.0) / (-np.log(1.0 - self.mu))},
            "population": {
                "N_X_stationary": "B / mu, with B the mean accepted births per step",
                "note": "B is set by the local resource and free capacity at the organiser and "
                        "is measured, not predicted, because the chemostat's local supply is "
                        "itself a stationary quantity of the coupled system"},
            "domain_condition": {
                "requirement": "L must be large compared with the relative localisation length "
                               "so that the periodic images do not overlap",
                "ell_relative": self.ell_rel,
                "L_over_ell_relative": L / self.ell_rel,
                "profile_mass_beyond_L_over_2": float(self._tail_mass(rel))},
        }

    @staticmethod
    def _tail_mass(prof):
        L = prof.shape[0]
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
        return float(prof[d >= L / 2.0].sum())


def finite_n_correction(op, N_X, prof=None):
    """The measured core centre is an EMPIRICAL mean over N_X molecules and is rounded to a
    lattice site. Both add variance to |C - Y|, and both are computed here rather than fitted."""
    rel = prof if prof is not None else op.relative_profile()
    var_cloud = op._second_moment(rel)
    sampling = var_cloud / max(N_X, 1)
    rounding = 2.0 * (1.0 / 12.0)                    # two axes, uniform rounding to a site
    base = 2.0 * op.aY * op.e_min_age()
    tot = base + sampling + rounding
    return {"base_second_moment": base, "sampling_term": sampling, "rounding_term": rounding,
            "total_second_moment": tot, "rms": float(np.sqrt(tot)),
            "mean_modulus_rayleigh": float(np.sqrt(np.pi / 4.0) * np.sqrt(tot))}
