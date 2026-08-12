"""LawSpec v2: the same kinetics, with ONE operator replaced.

VERSIONS
  LAWSPEC_V1_ADDITIVE      the inherited rule. `_feed_and_outflow` adds resource toward S0 at
                           rate phi and drains waste at rate omega. Occupancy has one source
                           and one sink and the source is unconditional: the ratchet.
  LAWSPEC_V2_EXCHANGE      `_feed_and_outflow` is replaced by `_exchange`, a balanced chemostat:
                           the same rate phi and the same set-point S0 drive the number of units
                           the reservoir offers, and EVERY unit inserted displaces one unit
                           already present, drawn uniformly without replacement from the cell's
                           exchangeable pool. Occupancy is conserved EXACTLY, cell by cell and
                           step by step. omega is not used: waste leaves through the exchange,
                           which is what a chemostat outflow is.

The exchangeable pool is {SX, SY, WX, WY}: medium and waste, not body. That is the standard
reading of a chemostat, which exchanges medium and not biomass, and it is declared in advance;
a pre-declared control (POOL_INCLUDES_BODY) puts X into the pool and is run as a washout variant
so that the result cannot rest on the exclusion.

RNG MODES
  legacy_single_stream   one generator, drawn in the historical order. Reproduces the inherited
                         trajectories state for state.
  split_feed_stream      the feed or exchange operator draws from a SECOND generator, so that
                         diffusion, reaction and decay consume the first stream identically in
                         both arms. This is what makes a paired comparison possible. It changes
                         no rate and no distribution: the kernel is identical, only the source
                         of the numbers differs.

NOTHING ELSE CHANGES. Species, reaction, candidate rule, decay, diffusion, boundary and update
order are those of `kinetics.py`, which is byte-identical to the frozen MTW01 engine.
"""
from __future__ import annotations

import numpy as np

import kinetics as K

EXCHANGEABLE_DEFAULT = ("SX", "SY", "WX", "WY")
EXCHANGEABLE_WITH_BODY = ("SX", "SY", "WX", "WY", "X")

LAWSPEC_V1_ADDITIVE = "LAWSPEC_V1_ADDITIVE"
LAWSPEC_V2_EXCHANGE = "LAWSPEC_V2_EXCHANGE"


def _hyper_split(rng, stacks, k):
    """Exact multivariate hypergeometric: draw k units, per cell, from integer stacks
    (shape (m, L, L)) without replacement. Sequential conditional hypergeometric draws."""
    m = stacks.shape[0]
    n = stacks.sum(axis=0)
    k = np.minimum(np.maximum(k, 0), n)
    out = np.zeros_like(stacks)
    rem_k, rem_n = k.copy(), n.copy()
    for i in range(m - 1):
        good = stacks[i]
        bad = rem_n - good
        tot = good + bad
        bad_s = np.where(tot < 1, 1, bad)
        ns = np.clip(rem_k, 0, good + bad_s)
        take = rng.hypergeometric(np.maximum(good, 0), np.maximum(bad_s, 0), ns)
        take = np.where(tot < 1, 0, np.minimum(take, good))
        out[i] = take
        rem_k = rem_k - take
        rem_n = rem_n - good
    out[m - 1] = np.minimum(np.maximum(rem_k, 0), stacks[m - 1])
    return out


class WorldV2(K.World):
    """Subclass of the frozen engine. In v1 mode not one line of the inherited path is bypassed:
    `_feed_and_outflow` is inherited unchanged, so v1 + legacy_single_stream is the historical
    engine exactly."""

    def __init__(self, L=None, seed=0, sp=K.Spec, lawspec=LAWSPEC_V1_ADDITIVE,
                 rng_mode="legacy_single_stream", exchangeable=EXCHANGEABLE_DEFAULT,
                 insert_mode="reservoir", rec=None):
        super().__init__(L=L, seed=seed, sp=sp)
        self.lawspec = lawspec
        self.rng_mode = rng_mode
        self.exchangeable = tuple(exchangeable)
        self.insert_mode = insert_mode      # "reservoir" or "sham_reinsert" (declared control)
        self.rec = rec
        self.rng_feed = (self.rng if rng_mode == "legacy_single_stream"
                         else np.random.default_rng(np.random.SeedSequence(seed).spawn(2)[1]))
        # write-only ledgers, never read by any rate
        self.flux_in = 0
        self.flux_out = 0
        self.displaced = {k: 0 for k in EXCHANGEABLE_WITH_BODY}

    # ------------------------------------------------------------------ v2 operator
    def _exchange(self):
        rng, sp = self.rng_feed, self.sp
        # how many units the reservoir offers, per cell, per species: the SAME rule as the
        # legacy feed except that it is not capped by free capacity, because nothing is added
        offers = {}
        for s in ("SX", "SY"):
            room = np.maximum(sp.S0 - self.n[s], 0)
            offers[s] = rng.binomial(room, sp.phi)
        want = offers["SX"] + offers["SY"]
        pool = np.stack([self.n[k] for k in self.exchangeable])
        avail = pool.sum(axis=0)
        k = np.minimum(want, avail)                      # never insert more than can be removed
        if not k.any():
            return
        # which species leave, exactly, without replacement
        taken = _hyper_split(rng, pool, k)
        for i, s in enumerate(self.exchangeable):
            self.n[s] = self.n[s] - taken[i]
            self.displaced[s] += int(taken[i].sum())
        if self.insert_mode == "sham_reinsert":
            # DECLARED SHAM: put back exactly what was taken. Occupancy AND composition are
            # conserved, so the operator renews nothing. It isolates the renewal from the mere
            # conservation of occupancy.
            for i, s in enumerate(self.exchangeable):
                self.n[s] = self.n[s] + taken[i]
            self.flux_in += int(k.sum()); self.flux_out += int(k.sum())
            return
        # which species enter: split k between SX and SY in proportion to what was offered
        good = offers["SX"]
        bad = np.maximum(want - good, 0)
        tot = good + bad
        bad_s = np.where(tot < 1, 1, bad)
        ins_sx = rng.hypergeometric(np.maximum(good, 0), np.maximum(bad_s, 0),
                                    np.clip(k, 0, good + bad_s))
        ins_sx = np.where(tot < 1, 0, np.minimum(ins_sx, k))
        ins_sy = k - ins_sx
        self.n["SX"] = self.n["SX"] + ins_sx
        self.n["SY"] = self.n["SY"] + ins_sy
        self.flux_in += int(k.sum())
        self.flux_out += int(k.sum())

    def _feed_and_outflow(self):
        if self.lawspec == LAWSPEC_V2_EXCHANGE:
            self._exchange()
            return
        if self.rng_mode == "legacy_single_stream":
            super()._feed_and_outflow()                  # the inherited path, untouched
            return
        # v1 kinetics drawing from the second stream: identical kernel, different source of
        # numbers. Used only so that the additive control can be paired with the repair.
        rng, sp = self.rng_feed, self.sp
        for s in ("SX", "SY"):
            room = np.minimum(np.maximum(sp.S0 - self.n[s], 0), np.maximum(self.free(), 0))
            add = rng.binomial(room, sp.phi)
            self.n[s] = self.n[s] + add
            self.flux_in += int(add.sum())
        for w in ("WX", "WY"):
            out = rng.binomial(np.maximum(self.n[w], 0), sp.omega)
            self.n[w] = self.n[w] - out
            self.removed_waste += int(out.sum())
            self.flux_out += int(out.sum())

    # ------------------------------------------------------------------ instrumentation only
    def _react(self):
        if self.rec is not None:
            self.rec.pre_react(self)
        super()._react()
        if self.rec is not None:
            self.rec.post_react(self)

    def _decay(self):
        if self.rec is not None:
            self.rec.pre_decay(self)
        super()._decay()
        if self.rec is not None:
            self.rec.post_decay(self)

    def _one_step(self):
        o0 = int(self.occ().sum())
        super()._one_step()
        self._last_occ_delta = int(self.occ().sum()) - o0
        if self.rec is not None:
            self.rec.close_step(self)


def spec_with(**over):
    d = dict(K.Spec.as_dict())
    d.update(over)
    return type("SpecVariant", (K.Spec,), d)


def fresh_world(seed, sp, **kw):
    w = WorldV2(L=None, seed=seed, sp=sp, **kw)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    return w


def seed_one_organiser(w, x_seed):
    c = w.L // 2
    w.n["Y"][c, c] = 1
    w.n["X"][c, c] = int(x_seed)
    return (c, c)
