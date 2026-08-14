"""OBTC01 engine wrapper. NO LawSpec change, NO cohesion, NO C3.

Three additions, all of them observers or declared interventions, none of them a rate:

  1. INSTRUMENTATION. `_diffuse`, `_react` and `_decay` are copied VERBATIM from the frozen
     engine and augmented with counters and with a molecular tracker. The counters record how
     often a hop is refused by capacity — the single fact that decides whether the
     source-transport-decay convolution is exact or only conditionally exact.

  2. MOLECULAR TRACKER. The engine moves counts, not individuals. Molecules of one species in
     one cell are exchangeable, so ANY assignment of the count moves to labelled individuals is
     a valid coupling of the same process. The tracker draws that assignment from a SEPARATE
     generator, so the count trajectory is untouched — and `tests_obtc.py` proves it by state
     hash, with and without tracking, on the same seed.

  3. INTERVENTIONS, declared in advance:
       organiser_immobile   the organiser's hop probability is set to 0 in the Spec. Nothing
                            else changes; `_diffuse` still draws Binomial(n, 0).
       organiser_off_at     at that step the organiser is decayed by intervention, Y -> WY,
                            through the SAME channel a spontaneous decay would use. Occupancy
                            is conserved exactly. No X molecule is moved, created or destroyed,
                            and no resource is touched.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")

import kinetics as K            # noqa: E402
import lawspec_v2 as V2         # noqa: E402

NEI = ((1, 0), (-1, 0), (1, 1), (-1, 1))       # the frozen order of kinetics._diffuse


class Tracker:
    """Labelled X molecules, kept consistent with the counts. Draws from its own generator."""

    def __init__(self, L, seed):
        self.L = L
        self.rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(3)[2])
        self.y = np.zeros(0, dtype=np.int32)
        self.x = np.zeros(0, dtype=np.int32)
        self.id = np.zeros(0, dtype=np.int64)
        self.birth_step = np.zeros(0, dtype=np.int32)
        self.birth_y = np.zeros(0, dtype=np.int32)
        self.birth_x = np.zeros(0, dtype=np.int32)
        self.next_id = 0
        self.dead = []          # (id, birth_step, birth_y, birth_x, death_step, cause)
        self.n_moves = 0

    # -------------------------------------------------------------- helpers
    def _cell(self):
        return self.y.astype(np.int64) * self.L + self.x.astype(np.int64)

    def _pick(self, count_field):
        """Return a boolean mask selecting, in each cell, `count_field[cell]` molecules chosen
        uniformly without replacement among those present."""
        if len(self.y) == 0:
            return np.zeros(0, dtype=bool)
        k = count_field.ravel()
        if not k.any():
            return np.zeros(len(self.y), dtype=bool)
        cells = self._cell()
        r = self.rng.random(len(cells))
        order = np.lexsort((r, cells))          # sort by cell, random within cell
        sorted_cells = cells[order]
        # rank of each molecule inside its cell
        first = np.searchsorted(sorted_cells, sorted_cells, side="left")
        rank = np.arange(len(order)) - first
        take_sorted = rank < k[sorted_cells]
        mask = np.zeros(len(cells), dtype=bool)
        mask[order[take_sorted]] = True
        return mask

    # -------------------------------------------------------------- events
    def move(self, accepted, shift, axis):
        m = self._pick(accepted)
        if not m.any():
            return
        if axis == 0:
            self.y[m] = (self.y[m] + shift) % self.L
        else:
            self.x[m] = (self.x[m] + shift) % self.L
        self.n_moves += int(m.sum())

    def birth(self, births, step):
        n = int(births.sum())
        if n == 0:
            return
        ys, xs = np.nonzero(births)
        yy = np.repeat(ys, births[ys, xs]).astype(np.int32)
        xx = np.repeat(xs, births[ys, xs]).astype(np.int32)
        ids = np.arange(self.next_id, self.next_id + n, dtype=np.int64)
        self.next_id += n
        self.y = np.concatenate([self.y, yy])
        self.x = np.concatenate([self.x, xx])
        self.id = np.concatenate([self.id, ids])
        self.birth_step = np.concatenate([self.birth_step,
                                          np.full(n, step, dtype=np.int32)])
        self.birth_y = np.concatenate([self.birth_y, yy])
        self.birth_x = np.concatenate([self.birth_x, xx])

    def death(self, deaths, step, cause="decay"):
        m = self._pick(deaths)
        if not m.any():
            return
        for i in np.nonzero(m)[0]:
            self.dead.append((int(self.id[i]), int(self.birth_step[i]), int(self.birth_y[i]),
                              int(self.birth_x[i]), int(step), cause))
        keep = ~m
        self.y, self.x, self.id = self.y[keep], self.x[keep], self.id[keep]
        self.birth_step = self.birth_step[keep]
        self.birth_y, self.birth_x = self.birth_y[keep], self.birth_x[keep]

    def consistent_with(self, nX):
        f = np.zeros_like(nX)
        if len(self.y):
            np.add.at(f, (self.y, self.x), 1)
        return bool(np.array_equal(f, nX))


class WorldOBTC(V2.WorldV2):
    def __init__(self, *a, track=False, organiser_off_at=None, **kw):
        super().__init__(*a, **kw)
        self.track = bool(track)
        self.tracker = Tracker(self.L, kw.get("seed", 0)) if track else None
        self.organiser_off_at = organiser_off_at
        self.organiser_removed_at = None
        # write-only counters, never read by any rate
        self.hops_offered = {"X": 0, "Y": 0, "SX": 0, "SY": 0}
        self.hops_blocked = {"X": 0, "Y": 0, "SX": 0, "SY": 0}
        self.births_total = 0
        self.deaths_total = 0
        self.birth_offsets = []        # (step, dy, dx) of each birth relative to the organiser
        self.last_births = None
        self.last_deaths = None

    # ---------------------------------------------------------------- verbatim + counters
    def _diffuse(self, sname, p_hop):
        rng = self.rng
        for shift, ax in NEI:                                  # frozen order
            n = self.n[sname]
            movers = rng.binomial(np.maximum(n, 0), p_hop / 4.0)
            dest_free = np.roll(self.free(), -shift, axis=ax)
            accepted = np.minimum(movers, np.maximum(dest_free, 0))
            if sname in self.hops_offered:
                self.hops_offered[sname] += int(movers.sum())
                self.hops_blocked[sname] += int((movers - accepted).sum())
            if not accepted.any():
                continue
            self.n[sname] = n - accepted + np.roll(accepted, shift, axis=ax)
            if self.track and sname == "X":
                self.tracker.move(accepted, shift, ax)

    def _react_core(self):
        rng, sp = self.rng, self.sp
        nX, nY = self.n["X"], self.n["Y"]
        pair = nX * nY
        free0 = np.maximum(self.free(), 0)
        out = None
        for prod, res, kk in (("X", "SX", sp.kX), ("Y", "SY", sp.kY)):
            p = np.minimum(1.0, kk * pair)
            cand = np.minimum(self.n[res], free0)
            births = rng.binomial(np.maximum(cand, 0), p)
            if prod == "X":
                out = births
            if not births.any():
                continue
            self.n[res] = self.n[res] - births
            self.n[prod] = self.n[prod] + births
        return out

    def _react(self):
        if self.rec is not None:
            self.rec.pre_react(self)
        b = self._react_core()
        self.last_births = b
        if b is not None and b.any():
            self.births_total += int(b.sum())
            oy, ox = np.nonzero(self.n["Y"])
            if len(oy):
                ys, xs = np.nonzero(b)
                for yy, xx in zip(ys, xs):
                    dy = (int(yy) - int(oy[0]) + self.L // 2) % self.L - self.L // 2
                    dx = (int(xx) - int(ox[0]) + self.L // 2) % self.L - self.L // 2
                    self.birth_offsets.append((int(self.step), dy, dx, int(b[yy, xx])))
            if self.track:
                self.tracker.birth(b, self.step)
        if self.rec is not None:
            self.rec.post_react(self)

    def _decay_core(self):
        rng, sp = self.rng, self.sp
        out = None
        for s, w, mu in (("X", "WX", sp.muX), ("Y", "WY", sp.muY)):
            d = rng.binomial(np.maximum(self.n[s], 0), mu)
            if s == "X":
                out = d
            if not d.any():
                continue
            self.n[s] = self.n[s] - d
            self.n[w] = self.n[w] + d
        return out

    def _decay(self):
        if self.rec is not None:
            self.rec.pre_decay(self)
        d = self._decay_core()
        self.last_deaths = d
        if d is not None and d.any():
            self.deaths_total += int(d.sum())
            if self.track:
                self.tracker.death(d, self.step, "decay")
        if self.rec is not None:
            self.rec.post_decay(self)

    def _one_step(self):
        super()._one_step()
        if (self.organiser_off_at is not None and self.step >= self.organiser_off_at
                and self.organiser_removed_at is None and self.n["Y"].sum() > 0):
            # DECLARED INTERVENTION: the organiser is decayed, Y -> WY, through the same
            # channel a spontaneous decay uses. Occupancy is conserved exactly.
            y = self.n["Y"].copy()
            self.n["Y"] = self.n["Y"] - y
            self.n["WY"] = self.n["WY"] + y
            self.organiser_removed_at = int(self.step)


def fresh_world(seed, sp, **kw):
    w = WorldOBTC(L=None, seed=seed, sp=sp, **kw)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    return w


def seed_one_organiser(w, x_seed):
    c = w.L // 2
    w.n["Y"][c, c] = 1
    w.n["X"][c, c] = int(x_seed)
    if w.track:
        b = np.zeros_like(w.n["X"])
        b[c, c] = int(x_seed)
        w.tracker.birth(b, 0)
    return (c, c)
