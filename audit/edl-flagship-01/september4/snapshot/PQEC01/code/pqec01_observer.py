"""PQEC01 — observer-only instrumentation.

Records the EXACT pre-reaction spatial environment at the phase already qualified for `Q` by the
parent programme (immediately before `_react_core`, on the post-diffusion pre-reaction state).

DESIGN NOTE — losslessness without redundancy. `free = CAP - sum(6 species)`,
`candidate_X = min(nSX, free)`, `candidate_Y = min(nSY, free)` and
`Q_POSITION = nX * candidate_Y` are EXACT functions of the six species fields. Storing the six
fields at every step therefore stores every field the mandate names, with no loss and no
cadence reduction. The derived fields are recomputed on read, not re-stored.

INERTNESS — this module only READS engine state and appends to its own buffers. It draws no
number from any engine generator and mutates no engine array. That claim is not asserted: it is
tested bit-for-bit in pqec01_qualify.py against an uninstrumented run.
"""
from __future__ import annotations

import sys

import numpy as np

for _p in ("/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import engine_obtc as EN          # noqa: E402
import lawspec_v2 as V2           # noqa: E402
import observe as OBS             # noqa: E402
import protocol_obtc02 as PC      # noqa: E402

SPECIES = ("X", "Y", "SX", "SY", "WX", "WY")


class PQECWorld(EN.WorldOBTC):
    """WorldOBTC plus observer-only recording. No physics is touched."""

    def pqec_init(self, horizon, record_fields=True):
        L = self.L
        self.pq_T = int(horizon)
        self.pq_record_fields = bool(record_fields)
        # (T, 6, L, L) uint8 — the complete pre-reaction environment, every step
        self.pq_field = (np.zeros((self.pq_T, len(SPECIES), L, L), np.uint8)
                         if record_fields else None)
        self.pq_steps_recorded = 0
        self.pq_ycells = []        # (step, y, x, nY, nX, nSY, free, cand_Y, Q_local)
        self.pq_ybirth = []        # (step, y, x, n_born)
        self.pq_ydeath = []        # (step, y, x, n_died)
        self.pq_yhop = []          # (step, sub, shift, ax, y_from, x_from, n_accepted)
        self.pq_xevent = []        # (step, n_X_born, n_X_died)
        self.pq_capacity = []      # (step, species_idx, offered, blocked)
        self.pq_exchange = []      # (step, dSX, dSY, dWX, dWY) over _feed_and_outflow
        self.pq_src = []           # (step, sub, species_idx, y_before, x_before, y_after, x_after)
        self.pq_stephash = []      # (step_pre, state_hash) -- provenance, cheap
        return self

    # ------------------------------------------------------------------ helpers (read-only)
    def _pq_snap(self):
        return np.stack([self.n[s] for s in SPECIES]).astype(np.uint8, copy=True)

    def _pq_org(self):
        ys, xs = np.nonzero(self.n["Y"])
        return (int(ys[0]), int(xs[0])) if len(ys) else (-1, -1)

    def _pq_record_ycells(self, step):
        nY = self.n["Y"]
        ys, xs = np.nonzero(nY)
        if not len(ys):
            return
        free = np.maximum(self.free(), 0)
        nX, nSY = self.n["X"], self.n["SY"]
        for y, x in zip(ys.tolist(), xs.tolist()):
            c = int(min(nSY[y, x], free[y, x]))
            self.pq_ycells.append((step, y, x, int(nY[y, x]), int(nX[y, x]), int(nSY[y, x]),
                                   int(free[y, x]), c, int(nX[y, x]) * c))

    # ------------------------------------------------------------------ overrides
    def _diffuse(self, sname, p_hop):
        if sname != "Y":
            o0 = self._pq_org()
            off0 = self.hops_offered.get(sname, 0)
            blk0 = self.hops_blocked.get(sname, 0)
            super()._diffuse(sname, p_hop)
            self.pq_capacity.append((int(self.step), SPECIES.index(sname),
                                     int(self.hops_offered.get(sname, 0) - off0),
                                     int(self.hops_blocked.get(sname, 0) - blk0)))
            o1 = self._pq_org()
            self.pq_src.append((int(self.step), -1, SPECIES.index(sname),
                                o0[0], o0[1], o1[0], o1[1]))
            return
        # Y: record the field before and after EACH frozen sub-shift so hops are exact
        off0 = self.hops_offered.get(sname, 0)
        blk0 = self.hops_blocked.get(sname, 0)
        before_all = self.n["Y"].copy()
        rng = self.rng
        for sub, (shift, ax) in enumerate(EN.NEI):
            n = self.n[sname]
            before = n.copy()
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
            ys, xs = np.nonzero(accepted)
            for y, x in zip(ys.tolist(), xs.tolist()):
                self.pq_yhop.append((int(self.step), sub, int(shift), int(ax), y, x,
                                     int(accepted[y, x])))
            del before
        self.pq_capacity.append((int(self.step), SPECIES.index(sname),
                                 int(self.hops_offered.get(sname, 0) - off0),
                                 int(self.hops_blocked.get(sname, 0) - blk0)))
        del before_all

    def _react(self):
        st = int(self.step)
        # ---- THE QUALIFIED PHASE: post-diffusion, pre-reaction ----
        if self.pq_record_fields and st < self.pq_T:
            self.pq_field[st] = self._pq_snap()
            self.pq_steps_recorded = max(self.pq_steps_recorded, st + 1)
        self._pq_record_ycells(st)
        self.pq_stephash.append((st, self.state_hash()))
        yb = self.n["Y"].copy()
        x0 = int(self.n["X"].sum())
        super()._react()
        d = self.n["Y"] - yb
        ys, xs = np.nonzero(d > 0)
        for y, x in zip(ys.tolist(), xs.tolist()):
            self.pq_ybirth.append((st, y, x, int(d[y, x])))
        self.pq_xevent.append([st, int(self.n["X"].sum()) - x0, 0])

    def _decay(self):
        st = int(self.step)
        yb, xb = self.n["Y"].copy(), int(self.n["X"].sum())
        super()._decay()
        d = yb - self.n["Y"]
        ys, xs = np.nonzero(d > 0)
        for y, x in zip(ys.tolist(), xs.tolist()):
            self.pq_ydeath.append((st, y, x, int(d[y, x])))
        if self.pq_xevent and self.pq_xevent[-1][0] == st:
            self.pq_xevent[-1][2] = xb - int(self.n["X"].sum())

    def _feed_and_outflow(self):
        st = int(self.step)
        b = {s: int(self.n[s].sum()) for s in ("SX", "SY", "WX", "WY")}
        super()._feed_and_outflow()
        self.pq_exchange.append((st, int(self.n["SX"].sum()) - b["SX"],
                                 int(self.n["SY"].sum()) - b["SY"],
                                 int(self.n["WX"].sum()) - b["WX"],
                                 int(self.n["WY"].sum()) - b["WY"]))


def build_world(seed, kY, muY, L=None, horizon=11000, instrumented=True, record_fields=True,
                p_hop_Y=None, cap_override=None):
    """Construct a world at the frozen X/source baseline with the given Y coupling."""
    base = PC.spec_for(L, immobile_organiser=False)
    d = {k: getattr(base, k) for k in ("CAP", "S0", "phi", "omega", "muX", "muY", "kX", "kY",
                                       "L", "p_hop_X", "p_hop_Y")}
    d["kY"] = float(kY)
    d["muY"] = float(muY)
    if p_hop_Y is not None:
        d["p_hop_Y"] = float(p_hop_Y)
    if L is not None:
        d["L"] = int(L)
    if cap_override is not None:
        d["CAP"] = int(cap_override)
    sp = V2.spec_with(**d)
    rec = OBS.Recorder()
    cls = PQECWorld if instrumented else EN.WorldOBTC
    w = cls(L=None, seed=seed, sp=sp, lawspec=V2.LAWSPEC_V2_EXCHANGE,
            rng_mode="split_feed_stream", exchangeable=V2.EXCHANGEABLE_DEFAULT,
            insert_mode="reservoir", rec=rec, track=True, organiser_off_at=None)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    if instrumented:
        w.pqec_init(horizon, record_fields=record_fields)
    EN.seed_one_organiser(w, int(PC.PT["X_SEED"]))
    return w, rec, sp


def rng_states(w):
    """Every engine generator's bit-generator state, for bit-exact comparison."""
    out = {"rng": w.rng.bit_generator.state}
    if hasattr(w, "rng_feed"):
        out["rng_feed"] = w.rng_feed.bit_generator.state
    if getattr(w, "tracker", None) is not None and hasattr(w.tracker, "rng"):
        out["tracker_rng"] = w.tracker.rng.bit_generator.state
    return out


def physical_state(w):
    return {s: np.ascontiguousarray(w.n[s]).tobytes() for s in SPECIES}
