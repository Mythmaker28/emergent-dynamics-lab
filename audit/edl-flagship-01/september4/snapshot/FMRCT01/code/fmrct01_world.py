"""FMRCT01 — the world, the three interventions, and exact state hashing.

INERTNESS. The engine is imported byte-unchanged and never retyped. The world is FDOT01's
FDOTWorld, reused unchanged, which adds only the per-cell X birth ledger.

THE THREE INTERVENTIONS ARE ONE FUNCTION WITH A MASK. SHAM passes an empty mask, SELECTIVE
passes the parent component's cells, GLOBAL_OFF passes every cell. The removal channel is the
engine's own declared organiser-off channel: Y -> WY, occupancy conserved exactly, and NO
generator is touched by any of the three. SHAM is therefore a bit-exact no-op by construction,
which is what lets the base trajectory serve as the SHAM arm. That claim is not asserted here:
fmrct01_fixtures.py tests it bit-for-bit, and if it fails the frozen fallback design applies.
"""
from __future__ import annotations
import hashlib, sys, json
import numpy as np
REPO="/home/claude/edl"
for _p in (f"{REPO}/FDOT01/code", f"{REPO}/PQEC01/code", "/home/claude/ORR01/code",
           "/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import fdot01_world as FW            # reused byte-unchanged
import pqec01_observer as O
SPECIES=O.SPECIES

def build(seed,kY,muY,horizon):
    return FW.build(seed,kY,muY,horizon)

# ------------------------------------------------------------------ exact state hashing
def _generators(w):
    """every numpy Generator reachable from the world, found by introspection rather than by a
    hard-coded list, so a generator added by any layer cannot silently escape the fork proof."""
    out=[]
    def walk(obj,prefix,depth):
        if depth>2: return
        for k,v in sorted(vars(obj).items()):
            if isinstance(v,np.random.Generator): out.append((prefix+k,v))
            elif hasattr(v,"__dict__") and not isinstance(v,(np.ndarray,)):
                try: walk(v,prefix+k+".",depth+1)
                except Exception: pass
    walk(w,"",0)
    return out

def phys_hash(w):
    h=hashlib.sha256()
    for s in SPECIES: h.update(np.ascontiguousarray(w.n[s]).tobytes())
    return h.hexdigest()

def rng_hash(w):
    h=hashlib.sha256()
    for name,g in _generators(w):
        h.update(name.encode()); h.update(json.dumps(g.bit_generator.state,sort_keys=True,default=str).encode())
    return h.hexdigest()

def counter_hash(w):
    d={"step":int(w.step),"births_total":int(w.births_total),"deaths_total":int(w.deaths_total),
       "hops_offered":{k:int(v) for k,v in w.hops_offered.items()},
       "hops_blocked":{k:int(v) for k,v in w.hops_blocked.items()},
       "n_ycells":len(w.pq_ycells),"n_ybirth":len(w.pq_ybirth),"n_ydeath":len(w.pq_ydeath),
       "n_xbirth":len(w.fd_xbirth),"organiser_removed_at":w.organiser_removed_at}
    return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()

def fork_fingerprint(w):
    return {"phys":phys_hash(w),"rng":rng_hash(w),"counters":counter_hash(w),
            "n_generators":len(_generators(w))}

# ------------------------------------------------------------------ the one intervention
def intervene(w, cells):
    """Remove Y from `cells` through the engine's declared organiser-off channel.

    cells = ()            -> SHAM,             removes nothing
    cells = parent cells  -> SELECTIVE_PARENT_REMOVAL
    cells = None          -> GLOBAL_OFF,       every cell

    Deterministic. Consumes no random number. Occupancy is conserved exactly because every
    removed Y is moved to WY, which is the same channel a spontaneous decay uses.
    """
    if cells is None:
        m=np.ones_like(w.n["Y"],dtype=bool)
    else:
        m=np.zeros_like(w.n["Y"],dtype=bool)
        for (y,x) in cells: m[y,x]=True
    y=np.where(m,w.n["Y"],0)
    removed=int(y.sum())
    if removed:
        w.n["Y"]=w.n["Y"]-y
        w.n["WY"]=w.n["WY"]+y
    return removed

ARMS=("SHAM","SELECTIVE","GLOBAL_OFF")
def apply_arm(w, arm, parent_cells):
    if arm=="SHAM":       return intervene(w, ())
    if arm=="SELECTIVE":  return intervene(w, parent_cells)
    if arm=="GLOBAL_OFF": return intervene(w, None)
    raise ValueError(arm)
