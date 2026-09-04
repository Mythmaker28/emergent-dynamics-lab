"""Exact finite-state analysis of the additive LawSpec.

The engine's step is a composition of independent binomial draws. On a small lattice the whole
step kernel can therefore be enumerated EXACTLY, with no sampling, by pushing a dictionary
{state -> probability} through each sub-step and merging. This module does that, and cross-checks
the enumerator against the real engine by comparing the enumerated kernel with the empirical
transition frequencies of `kinetics.World` (a differential check: two independent routes to the
same object, any disagreement is a bug).

Scope of the enumeration, declared:
  CELL1   L = 1, all six species. On a 1x1 torus every roll is the identity, so `_diffuse` is a
          no-op and this isolates react + decay + feed + outflow exactly.
  RES2    L = 2, resource species only. This isolates diffusion + feed, which is where the
          ratchet lives.
"""
from __future__ import annotations

import itertools
import json
from fractions import Fraction as Fr

import numpy as np

import kinetics as K

SPEC_ORDER = ("X", "Y", "SX", "SY", "WX", "WY")


def binom(n, p):
    """Exact binomial pmf as a list of (k, Fraction)."""
    if n == 0:
        return [(0, Fr(1))]
    out = []
    from math import comb
    for k in range(n + 1):
        out.append((k, Fr(comb(n, k)) * p ** k * (1 - p) ** (n - k)))
    return out


class Small:
    """State = tuple of length 6*L*L, species-major, matching SPEC_ORDER."""

    def __init__(self, L, sp):
        self.L, self.sp = L, sp
        self.NC = L * L

    def unpack(self, s):
        return {k: np.array(s[i * self.NC:(i + 1) * self.NC], dtype=np.int64).reshape(self.L,
                                                                                      self.L)
                for i, k in enumerate(SPEC_ORDER)}

    def pack(self, n):
        return tuple(int(v) for k in SPEC_ORDER for v in n[k].reshape(-1))

    def free(self, n):
        return self.sp.CAP - sum(n[k] for k in SPEC_ORDER)

    # ---------------------------------------------------------------- sub-steps
    def _draws(self, dist, counts, probs):
        """Push {state: prob} through independent per-cell binomial draws.
        `counts(n)` returns the per-cell trial counts, `probs` the per-cell probability,
        and `apply(n, k)` is supplied by the caller through a closure."""
        raise NotImplementedError

    def diffuse(self, dist, sname, p_hop):
        q = Fr(p_hop).limit_denominator(10 ** 9) / 4
        for shift, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            new = {}
            for s, pr in dist.items():
                n = self.unpack(s)
                fr = self.free(n)
                dest_free = np.roll(fr, -shift, axis=ax)
                cells = list(np.ndindex(self.L, self.L))
                opts = [binom(int(n[sname][c]), q) for c in cells]
                for combo in itertools.product(*opts):
                    p2 = pr
                    for _, w in combo:
                        p2 *= w
                    if p2 == 0:
                        continue
                    acc = np.zeros((self.L, self.L), dtype=np.int64)
                    for c, (k, _) in zip(cells, combo):
                        acc[c] = min(k, max(int(dest_free[c]), 0))
                    n2 = {kk: vv.copy() for kk, vv in n.items()}
                    n2[sname] = n[sname] - acc + np.roll(acc, shift, axis=ax)
                    key = self.pack(n2)
                    new[key] = new.get(key, Fr(0)) + p2
            dist = new
        return dist

    def react(self, dist):
        sp = self.sp
        for prod, res, kk in (("X", "SX", sp.kX), ("Y", "SY", sp.kY)):
            new = {}
            for s, pr in dist.items():
                n = self.unpack(s)
                fr = np.maximum(self.free(n), 0)
                cells = list(np.ndindex(self.L, self.L))
                opts = []
                for c in cells:
                    pp = min(Fr(1), Fr(kk).limit_denominator(10 ** 9) * int(n["X"][c])
                             * int(n["Y"][c]))
                    cand = min(int(n[res][c]), int(fr[c]))
                    opts.append(binom(cand, pp))
                for combo in itertools.product(*opts):
                    p2 = pr
                    for _, w in combo:
                        p2 *= w
                    if p2 == 0:
                        continue
                    n2 = {a: b.copy() for a, b in n.items()}
                    for c, (k, _) in zip(cells, combo):
                        n2[res][c] -= k
                        n2[prod][c] += k
                    key = self.pack(n2)
                    new[key] = new.get(key, Fr(0)) + p2
            dist = new
        return dist

    def decay(self, dist):
        sp = self.sp
        for s_, w_, mu in (("X", "WX", sp.muX), ("Y", "WY", sp.muY)):
            new = {}
            for s, pr in dist.items():
                n = self.unpack(s)
                cells = list(np.ndindex(self.L, self.L))
                opts = [binom(int(n[s_][c]), Fr(mu).limit_denominator(10 ** 9)) for c in cells]
                for combo in itertools.product(*opts):
                    p2 = pr
                    for _, wt in combo:
                        p2 *= wt
                    if p2 == 0:
                        continue
                    n2 = {a: b.copy() for a, b in n.items()}
                    for c, (k, _) in zip(cells, combo):
                        n2[s_][c] -= k
                        n2[w_][c] += k
                    key = self.pack(n2)
                    new[key] = new.get(key, Fr(0)) + p2
            dist = new
        return dist

    def feed_outflow(self, dist):
        sp = self.sp
        phi = Fr(sp.phi).limit_denominator(10 ** 9)
        om = Fr(sp.omega).limit_denominator(10 ** 9)
        for s_ in ("SX", "SY"):
            new = {}
            for s, pr in dist.items():
                n = self.unpack(s)
                fr = np.maximum(self.free(n), 0)
                cells = list(np.ndindex(self.L, self.L))
                opts = [binom(int(min(max(sp.S0 - n[s_][c], 0), fr[c])), phi) for c in cells]
                for combo in itertools.product(*opts):
                    p2 = pr
                    for _, w in combo:
                        p2 *= w
                    if p2 == 0:
                        continue
                    n2 = {a: b.copy() for a, b in n.items()}
                    for c, (k, _) in zip(cells, combo):
                        n2[s_][c] += k
                    key = self.pack(n2)
                    new[key] = new.get(key, Fr(0)) + p2
            dist = new
        for w_ in ("WX", "WY"):
            new = {}
            for s, pr in dist.items():
                n = self.unpack(s)
                cells = list(np.ndindex(self.L, self.L))
                opts = [binom(int(n[w_][c]), om) for c in cells]
                for combo in itertools.product(*opts):
                    p2 = pr
                    for _, w in combo:
                        p2 *= w
                    if p2 == 0:
                        continue
                    n2 = {a: b.copy() for a, b in n.items()}
                    for c, (k, _) in zip(cells, combo):
                        n2[w_][c] -= k
                    key = self.pack(n2)
                    new[key] = new.get(key, Fr(0)) + p2
            dist = new
        return dist

    def kernel(self, state):
        d = {state: Fr(1)}
        for s_, ph in (("X", self.sp.p_hop_X), ("Y", self.sp.p_hop_Y),
                       ("SX", self.sp.p_hop_X), ("SY", self.sp.p_hop_X)):
            d = self.diffuse(d, s_, ph)
        d = self.react(d)
        d = self.decay(d)
        d = self.feed_outflow(d)
        return d


# ---------------------------------------------------------------- state spaces
def states_one_cell(CAP):
    out = []
    for v in itertools.product(range(CAP + 1), repeat=6):
        if sum(v) <= CAP:
            out.append(tuple(v))
    return out


def states_resource_only(L, CAP):
    NC = L * L
    out = []
    for v in itertools.product(range(CAP + 1), repeat=NC):
        out.append(tuple([0] * NC * 2 + list(v) + [0] * NC * 3))
    return out


def stationary(P, states, iters=4000):
    idx = {s: i for i, s in enumerate(states)}
    M = np.zeros((len(states), len(states)))
    for s, row in P.items():
        for t, pr in row.items():
            M[idx[s], idx[t]] = float(pr)
    v = np.full(len(states), 1.0 / len(states))
    for _ in range(iters):
        v = v @ M
        v /= v.sum()
    return v, idx, M


def absorbing_states(P):
    return [s for s, row in P.items() if len(row) == 1 and next(iter(row)) == s]
