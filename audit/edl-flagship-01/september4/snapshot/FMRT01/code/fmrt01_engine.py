"""FMRT01 — the selective parent-off capability.

RECONSTRUCTION NOTICE. The SPOIQ01 module that first carried this capability was destroyed
by the fifth container rollback and was never written to durable storage, so its recorded
hash cannot be claimed here. This file is a fresh implementation of the same specification
and is RE-QUALIFIED from scratch in this mission against the surviving PQEC01 archives.

The frozen engine file OBTC02/code/engine_obtc.py is NOT modified. The capability is a
subclass method the autonomous law never invokes; only an experimental runner can arm it.

SELECTIVE_Y_OFF(mask):   removed = Y[mask] ; Y[mask] -= removed ; WY[mask] += removed
Nothing else is touched. No random number is drawn.
"""
from __future__ import annotations
import hashlib, json, sys
import numpy as np
for _p in ("/home/claude/ORR01/code","/home/claude/OBTC02/code","/home/claude/edl/PQEC01/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O                                                    # noqa: E402

class FMRTWorld(O.PQECWorld):
    """PQECWorld plus one experimental hook, unarmed unless a runner calls it."""

    def fmrt_init(self):
        self.intervention_audit = []      # write-only; no rate ever reads it
        self.intervention_count = 0
        return self

    def selective_y_off(self, mask):
        """Remove Y from exactly the masked cells through the Y -> WY channel. No RNG."""
        m = np.asarray(mask, dtype=bool)
        if m.shape != self.n["Y"].shape:
            raise ValueError("mask shape must equal the lattice shape")
        removed = np.where(m, self.n["Y"], 0)
        n_rem = int(removed.sum())
        if n_rem:
            self.n["Y"] = self.n["Y"] - removed
            self.n["WY"] = self.n["WY"] + removed
        if not hasattr(self, "intervention_audit"): self.fmrt_init()
        self.intervention_audit.append((int(self.step), n_rem, int((removed > 0).sum())))
        self.intervention_count += 1
        return n_rem

    def sham_off(self, mask=None):
        """SHAM: identical branch and audit record, empty mask, state unchanged."""
        m = np.zeros_like(self.n["Y"], dtype=bool) if mask is None else np.zeros_like(self.n["Y"], dtype=bool)
        return self.selective_y_off(m)

def tracker_snapshot(w):
    t = w.tracker
    return {"id":np.array(t.id,np.int64),"y":np.array(t.y,np.int32),"x":np.array(t.x,np.int32),
            "birth_step":np.array(t.birth_step,np.int32),
            "birth_y":np.array(t.birth_y,np.int32),"birth_x":np.array(t.birth_x,np.int32)}

def rng_fingerprint(w):
    d={"rng":w.rng.bit_generator.state}
    if hasattr(w,"rng_feed"): d["rng_feed"]=w.rng_feed.bit_generator.state
    if getattr(w,"tracker",None) is not None: d["tracker_rng"]=w.tracker.rng.bit_generator.state
    return hashlib.sha256(json.dumps(d,sort_keys=True,default=str).encode()).hexdigest()
