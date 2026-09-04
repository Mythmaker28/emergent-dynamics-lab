"""FDOT01 — the world, instrumented for the organiser question.

INERTNESS. This module subclasses PQEC01's observer, which is reused BYTE-UNCHANGED, and adds one
buffer: the per-cell X birth ledger, which PQEC01 recorded only as a world total. The override
reads `self.n["X"]` before and after the parent's `_react` and appends to its own list. It draws
no number from any engine generator and mutates no engine array. The claim is not asserted: it is
tested bit-for-bit against an uninstrumented run in fdot01_fixtures.py.

HORIZON. Every primary world executes the full frozen horizon. PQEC01 stopped worlds on EXTINCT,
PREMATURE_THIRD_CENTRE and MAX_PERMITTED_Y; FDOT01 §8 forbids that, so none of those is a stop
here. The only break is a genuine engine invariant failure, which is a technical fault and not a
scientific outcome.
"""
from __future__ import annotations
import sys, json
import numpy as np
REPO="/home/claude/edl"
for _p in (f"{REPO}/PQEC01/code", "/home/claude/ORR01/code", "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O          # noqa: E402  reused byte-unchanged
import engine_obtc as EN             # noqa: E402
SPECIES = O.SPECIES

class FDOTWorld(O.PQECWorld):
    def fdot_init(self):
        self.fd_xbirth = []          # (step, y, x, n_born) — the object PQEC01 did not store
        return self
    def _react(self):
        xb = self.n["X"].copy()      # read only
        super()._react()             # PQEC01's observer, then the frozen engine reaction
        d = self.n["X"] - xb
        if d.any():
            st = int(self.step)
            ys, xs = np.nonzero(d > 0)
            for y, x in zip(ys.tolist(), xs.tolist()):
                self.fd_xbirth.append((st, y, x, int(d[y, x])))

def build(seed, kY, muY, horizon):
    """Identical to PQEC01's builder except that the six-plane field recorder is OFF (the
    organiser question needs the event ledgers, not the fields) and FDOTWorld is used."""
    _cls = O.PQECWorld
    O.PQECWorld = FDOTWorld
    try:
        w, rec, sp = O.build_world(seed, kY, muY, L=None, horizon=horizon,
                                   instrumented=True, record_fields=False)
    finally:
        O.PQECWorld = _cls
    w.fdot_init()
    return w, rec, sp
