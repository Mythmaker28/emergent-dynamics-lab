"""LawSpec v3: the balanced chemostat of ORR01 v2, with ONE further operator optionally changed.

  COHESION = None                       v3 IS v2. `_decay` calls the inherited path literally,
                                        so v3 with no mechanism is the ORR01 engine exactly.
                                        `tests_csc.py` proves it by state hash.
  COHESION = C3_NEIGHBOUR_PROTECTED_DECAY
                                        mu_X(cell) = mu_X * (1 - lambda) ** m(cell), where
                                        m(cell) is the number of X molecules in the FOUR
                                        NEIGHBOURING cells. Nothing else changes: not the
                                        species set, not the reaction, not the candidate rule,
                                        not diffusion, not the exchange, not the update order.

WHAT THE OPERATOR READS. `m` is built from four `np.roll`s of the X field, i.e. every cell reads
its own four neighbours and nothing else. There is no global reduction, no score, no gate value,
no classification and no success flag anywhere in the rate. The MINCORE locality constraint —
"every operator reads a cell and its four neighbours only" — is preserved exactly.

WHAT IT CANNOT DO. It only ever DECREASES a death probability, so it creates no matter, moves no
matter, and leaves n_X = 0 invariant and n_Y = 0 birth-forbidding. The pre-declared controls keep
their meaning.

WHAT IT CHANGES ABOUT THE INHERITED BOUNDS. Transport is untouched, so D_X, D_Y and the
first-passage separation time tau_sep = Delta^2 / (8 D_Y) are unchanged, and the MTW01 minority
window is not invalidated. What does change is that the body length scale ell_X = sqrt(D_X/mu_X)
becomes STATE DEPENDENT: any statement that uses a single ell_X must be re-derived under this
mechanism. That re-derivation is recorded with the mission, not assumed.
"""
from __future__ import annotations

import numpy as np

import sys
sys.path.insert(0, "/home/claude/ORR01/code")

import kinetics as K            # noqa: E402
import lawspec_v2 as V2         # noqa: E402

C3 = "C3_NEIGHBOUR_PROTECTED_DECAY"
COHESION_NONE = None


def neighbour_count(nX):
    """m(cell) = number of X molecules in the four neighbouring cells. Periodic, local."""
    return (np.roll(nX, 1, 0) + np.roll(nX, -1, 0) +
            np.roll(nX, 1, 1) + np.roll(nX, -1, 1))


class WorldV3(V2.WorldV2):
    def __init__(self, *a, cohesion=COHESION_NONE, lam=0.0, **kw):
        super().__init__(*a, **kw)
        self.cohesion = cohesion
        self.lam = float(lam)
        if cohesion not in (COHESION_NONE, C3):
            raise ValueError("undeclared cohesion mechanism %r" % (cohesion,))
        if cohesion is C3 and not (0.0 <= self.lam < 1.0):
            raise ValueError("lambda must lie in [0, 1)")
        # write-only instrumentation, never read by any rate
        self.deaths_avoided_estimate = 0.0

    def _decay(self):
        if self.rec is not None:
            self.rec.pre_decay(self)
        self._decay_core()
        if self.rec is not None:
            self.rec.post_decay(self)

    def _decay_core(self):
        if self.cohesion is COHESION_NONE:
            K.World._decay(self)                 # the inherited path, literally
            return
        rng, sp = self.rng, self.sp
        nX = self.n["X"]
        m = neighbour_count(nX)
        mu = sp.muX * (1.0 - self.lam) ** m       # <= muX everywhere, never above
        d = rng.binomial(np.maximum(nX, 0), mu)
        if d.any():
            self.n["X"] = nX - d
            self.n["WX"] = self.n["WX"] + d
        self.deaths_avoided_estimate += float((nX * (sp.muX - mu)).sum())
        dy = rng.binomial(np.maximum(self.n["Y"], 0), sp.muY)   # Y decay: unchanged
        if dy.any():
            self.n["Y"] = self.n["Y"] - dy
            self.n["WY"] = self.n["WY"] + dy


def fresh_world(seed, sp, **kw):
    w = WorldV3(L=None, seed=seed, sp=sp, **kw)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    return w


def seed_one_organiser(w, x_seed):
    c = w.L // 2
    w.n["Y"][c, c] = 1
    w.n["X"][c, c] = int(x_seed)
    return (c, c)


def lambda_from_m_star(m_star):
    """The declared calibration: a molecule at the median neighbour count must have exactly half
    the death rate of an isolated one."""
    m_star = float(m_star)
    if m_star <= 0:
        return None
    return float(1.0 - 2.0 ** (-1.0 / m_star))


def effective_ell(sp, lam, m):
    """ell_X(m) = sqrt(D_X / mu_eff(m)), with D_X = q(1-q), q = p_hop/4."""
    q = sp.p_hop_X / 4.0
    D = q * (1.0 - q)
    mu = sp.muX * (1.0 - lam) ** m
    return float(np.sqrt(D / mu))
