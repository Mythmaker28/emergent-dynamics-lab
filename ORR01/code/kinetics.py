"""MTW01 engine — MINCORE species kinetics, torus boundary, cohort ledger disabled.

RELATION TO MINCORE/code/mincore.py (sha256 f5ecd405...c385af1)
    IDENTICAL: species set, reaction scheme, birth probability min(1, k*nX*nY), candidate rule
        cand = min(n[resource], max(free,0)), free = CAP - occupancy over all six species,
        decay, local feed toward S0 at rate phi, local waste outflow at rate omega, and the
        frozen update order diffuse(X,Y,SX,SY) -> react(X then Y) -> decay -> feed_and_outflow.
    CHANGED, and why, both decided analytically before any start (see the preplan):
      1. PERIODIC boundary instead of reflecting. A freely diffusing organiser wanders
         7.9*sqrt(margin) cloud radii during one division cycle whatever D_Y is (the wander is
         scale free because tau_div and tau_sep both scale as 1/D_Y), so a reflecting box would
         need L >= 38*ell_X and would censor most arms. The absolute position of the cluster is
         irrelevant to the window; only the RELATIVE separation of two organisers is.
      2. COHORT LEDGER DISABLED. The three integer channels on SX/SY/X/Y exist to account for
         donor versus receiver material. This mission uses no cohort observable. MINCORE
         integrity test 8 established that cohort labels are causally inert, so removing them
         leaves the law of the species process unchanged while removing 40 hypergeometric draws
         per step.
    NOT CHANGED: no global reduction of any kind enters any rate. Every operator reads a cell
    and its four neighbours only.

NOTHING in this file reads a score, a decision or an outcome. The observables live in
observe.py and the protocol lives in blocks.py.
"""
from __future__ import annotations

import numpy as np

ALL_OCC = ("X", "Y", "SX", "SY", "WX", "WY")


class Spec:
    """MTW01 design point. Every value is fixed by code/window.py, in the order given there."""
    L = 36
    CAP = 16
    S0 = 3
    phi = 0.05
    omega = 0.05
    p_hop_X = 1.0                       # D_X = 0.25, the largest the lattice allows
    p_hop_Y = 0.5                       # D_Y = 0.125 = D_X/2
    muX = 0.04                          # ell_X = sqrt(D_X/muX) = 2.5 exactly
    muY = 1.9511206603301160e-06
    kX = 1.0                            # supra-marginal: the cloud must exist; enters no bound
    kY = 1.9511206603301162e-05

    @classmethod
    def D_X(cls):
        return cls.p_hop_X / 4.0

    @classmethod
    def D_Y(cls):
        return cls.p_hop_Y / 4.0

    @classmethod
    def ell_X(cls):
        return float(np.sqrt(cls.D_X() / cls.muX))

    @classmethod
    def as_dict(cls):
        return {k: getattr(cls, k) for k in
                ("L", "CAP", "S0", "phi", "omega", "p_hop_X", "p_hop_Y", "muX", "muY",
                 "kX", "kY")}


def spec_with(**over):
    """A frozen variant of Spec. Used only for the pre-declared control blocks."""
    d = dict(Spec.as_dict())
    d.update(over)
    return type("SpecVariant", (Spec,), d)


class World:
    def __init__(self, L=None, seed=0, sp=Spec):
        self.sp = sp
        self.L = int(sp.L if L is None else L)
        self.rng = np.random.default_rng(seed)
        self.n = {k: np.zeros((self.L, self.L), dtype=np.int64) for k in ALL_OCC}
        self.step = 0
        self.removed_waste = 0
        # cumulative hazard of a further organiser, accumulated only while armed
        self.hazard_armed = False
        self.H3_exact = 0.0            # -sum cand*ln(1-p) : exact -log P(no Y birth)
        self.H3_kk = 0.0               # sum cand*p        : the KK first-order form

    # ---------------------------------------------------------------- helpers
    def occ(self):
        return sum(self.n[k] for k in ALL_OCC)

    def free(self):
        return self.sp.CAP - self.occ()

    def state_hash(self):
        import hashlib
        h = hashlib.sha256()
        for k in ALL_OCC:
            h.update(k.encode())
            h.update(np.ascontiguousarray(self.n[k]).tobytes())
        h.update(str(self.step).encode())
        return h.hexdigest()

    # ---------------------------------------------------------------- operators
    def _diffuse(self, sname, p_hop):
        rng = self.rng
        for shift, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):      # frozen order
            n = self.n[sname]
            movers = rng.binomial(np.maximum(n, 0), p_hop / 4.0)
            dest_free = np.roll(self.free(), -shift, axis=ax)     # PERIODIC: no edge masking
            accepted = np.minimum(movers, np.maximum(dest_free, 0))
            if not accepted.any():
                continue
            self.n[sname] = n - accepted + np.roll(accepted, shift, axis=ax)

    def _react(self):
        rng, sp = self.rng, self.sp
        nX, nY = self.n["X"], self.n["Y"]
        pair = nX * nY
        free0 = np.maximum(self.free(), 0)
        for prod, res, kk in (("X", "SX", sp.kX), ("Y", "SY", sp.kY)):
            p = np.minimum(1.0, kk * pair)
            cand = np.minimum(self.n[res], free0)
            if prod == "Y" and self.hazard_armed:
                # exact cumulative hazard of at least one Y birth this step:
                #   P(no birth in a cell) = (1-p)^cand   =>  -log = cand * -log(1-p)
                m = (cand > 0) & (p > 0)
                if m.any():
                    self.H3_exact += float(
                        (cand[m] * (-np.log1p(-np.minimum(p[m], 1.0 - 1e-15)))).sum())
                    self.H3_kk += float((cand[m] * p[m]).sum())
            births = rng.binomial(np.maximum(cand, 0), p)
            if not births.any():
                continue
            self.n[res] = self.n[res] - births
            self.n[prod] = self.n[prod] + births

    def _decay(self):
        rng, sp = self.rng, self.sp
        for s, w, mu in (("X", "WX", sp.muX), ("Y", "WY", sp.muY)):
            d = rng.binomial(np.maximum(self.n[s], 0), mu)
            if not d.any():
                continue
            self.n[s] = self.n[s] - d
            self.n[w] = self.n[w] + d

    def _feed_and_outflow(self):
        rng, sp = self.rng, self.sp
        for s in ("SX", "SY"):
            room = np.minimum(np.maximum(sp.S0 - self.n[s], 0), np.maximum(self.free(), 0))
            self.n[s] = self.n[s] + rng.binomial(room, sp.phi)
        for w in ("WX", "WY"):
            out = rng.binomial(np.maximum(self.n[w], 0), sp.omega)
            self.n[w] = self.n[w] - out
            self.removed_waste += int(out.sum())

    def _one_step(self):
        self._diffuse("X", self.sp.p_hop_X)
        self._diffuse("Y", self.sp.p_hop_Y)
        self._diffuse("SX", self.sp.p_hop_X)
        self._diffuse("SY", self.sp.p_hop_X)
        self._react()
        self._decay()
        self._feed_and_outflow()
        self.step += 1


def fresh_world(seed, sp=Spec, L=None):
    w = World(L=L, seed=seed, sp=sp)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    return w


def seed_one_organiser(w, x_seed):
    """FROZEN seed: exactly one organiser at the centre of the torus, with x_seed body
    molecules in the same cell. No boundary is drawn, nothing is copied, nothing is divided."""
    c = w.L // 2
    w.n["Y"][c, c] = 1
    w.n["X"][c, c] = int(x_seed)
    return (c, c)
