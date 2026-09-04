"""OMLDCT02 — the matched fork. One base seed, one common prefix to t_m, two bit-identical
continuations. Arm S applies the frozen SELECTIVE_PARENT_REMOVAL to the parent cells only; arm H
applies the frozen SHAM, fmrct01_world.intervene(w, ()), which removes nothing and consumes no
random number.

Every construction passes through the pre-C2 guard first. OMLDCT01 had no such gate and died for
want of one.
"""
from __future__ import annotations
import sys, os, copy, json, hashlib, time, traceback
import numpy as np

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/TLMR01/code")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import tlmr01_world as TW, tlmr01_laws as LW
import fmrct01_world as FMW, fmrct01_track as TR
import pqec01_observer as O
import omldct02_guard as G

SPECIES = O.SPECIES
T_HORIZON = TW.T_HORIZON
LAW = LW.LAWS["LAW_C_MCTT01"]
L_GRID = 36
SCHEMA = {"VERSION": "TLMR01-ARCHIVE-1",
 "s": ["t", "nY_total", "nX_total", "nSY_total", "nSX_total", "free_min", "n_y_cells", "n_components"],
 "cells": ["c_t", "c_y", "c_x", "c_nY", "c_nX", "c_nSY", "c_free", "c_cand", "c_cid"],
 "comp": ["k_t", "k_id", "k_ncells", "k_nY", "k_a0y", "k_a0x", "k_soy", "k_sox", "k_xd"],
 "ledgers": ["ybirth", "ydeath", "xbirth"],
 "cells_semantics": "one row per Y-occupied cell per step; lossless for the frozen centre rules",
 "removal_semantics": "the rows at the fork step are recorded BEFORE the intervention; the "
                      "post-intervention state first appears at step+1"}

def _narrow(w):
    c = np.array(w.tl_cells, np.int64) if w.tl_cells else np.zeros((0, 9), np.int64)
    k = np.array(w.tl_comp, np.int64) if w.tl_comp else np.zeros((0, 9), np.int64)
    s = np.array(w.tl_step, np.int64) if w.tl_step else np.zeros((0, 8), np.int64)
    d = {"c_t": c[:, 0].astype(np.uint16), "c_y": c[:, 1].astype(np.uint8), "c_x": c[:, 2].astype(np.uint8),
         "c_nY": c[:, 3].astype(np.uint8), "c_nX": c[:, 4].astype(np.uint8), "c_nSY": c[:, 5].astype(np.uint8),
         "c_free": c[:, 6].astype(np.uint8), "c_cand": c[:, 7].astype(np.int32),
         "c_cid": c[:, 8].astype(np.int16),
         "k_t": k[:, 0].astype(np.uint16), "k_id": k[:, 1].astype(np.int16),
         "k_ncells": k[:, 2].astype(np.uint16), "k_nY": k[:, 3].astype(np.uint16),
         "k_a0y": k[:, 4].astype(np.int16), "k_a0x": k[:, 5].astype(np.int16),
         "k_soy": k[:, 6].astype(np.int32), "k_sox": k[:, 7].astype(np.int32),
         "k_xd": k[:, 8].astype(np.int32), "s": s.astype(np.int32),
         "ybirth": np.array(w.pq_ybirth or [], np.int32).reshape(-1, 4),
         "ydeath": np.array(w.pq_ydeath or [], np.int32).reshape(-1, 4),
         "xbirth": np.array(w.fd_xbirth or [], np.int32).reshape(-1, 4)}
    ok = (c.shape[0] == 0 or (int(c[:, 0].max()) < 2**16 and int(c[:, 1].max()) < 256
          and int(c[:, 2].max()) < 256 and int(c[:, 3].max()) < 256 and int(c[:, 4].max()) < 256
          and int(c[:, 5].max()) < 256 and int(c[:, 6].max()) < 256 and int(c[:, 8].max()) < 2**15)) and \
         (k.shape[0] == 0 or (int(k[:, 0].max()) < 2**16 and int(k[:, 1].max()) < 2**15
          and int(k[:, 2].max()) < 2**16 and int(k[:, 3].max()) < 2**16
          and int(np.abs(k[:, 4]).max()) < 2**15 and int(np.abs(k[:, 5]).max()) < 2**15))
    return d, bool(ok)

def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def _write(path, w, meta):
    d, lossless = _narrow(w)
    if not lossless: raise RuntimeError("narrow dtype would truncate a recorded value")
    meta = dict(meta); meta["NARROW_DTYPES_LOSSLESS"] = True
    d["meta"] = np.array([json.dumps(meta, default=str)])
    d["schema"] = np.array([json.dumps(SCHEMA)])
    tmp = path + ".part.npz"
    np.savez_compressed(tmp, **d); os.replace(tmp, path)
    return _sha(path), os.path.getsize(path)

def run_pair(seed, index, rawdir, horizon=T_HORIZON):
    """The whole unit of work for one base seed. Returns a record; writes two archives only when the
    seed is admissible. Nothing scientific is returned to the operator by this function beyond the
    predeclared technical fields — the endpoints are computed later, from the archives."""
    G.assert_allowed(L=L_GRID, horizon=horizon, seed=seed, what=f"base seed index {index}")
    v = LAW
    t0 = time.time()
    rec = {"index": index, "seed": seed, "law": "LAW_C_MCTT01",
           "kY": v["kY"], "muY": v["muY"], "p_hop_Y": v["p_hop_Y"], "horizon": horizon}
    w, _, sp = TW.build(seed, v["kY"], v["muY"], v["p_hop_Y"], horizon=horizon)
    # A maturation candidate after the frozen deadline fails the frozen gate, so a world with no
    # candidate by that step can never trigger. The common prefix therefore stops there. This uses
    # the frozen rule and changes no definition.
    PREFIX_LIMIT = min(horizon, TR.LATEST_ALLOWED_TRIGGER + 1)
    trig = TR.Trigger(); integ = True; t_m = None; at = None
    for t in range(PREFIX_LIMIT):
        w._one_step()
        free = sp.CAP - sum(w.n[s] for s in SPECIES)
        if free.min() < 0 or max(w.n[s].max() for s in SPECIES) > sp.CAP:
            integ = False; break
        cells, comps = w.tl_record(t)
        trig.observe(t, w, cells, comps, integ)
        if trig.t_m is not None:
            t_m = int(trig.t_m)
            at = {"descent_level": trig.descent_level, "descent_step": trig.descent_step,
                  "identity_carried": trig.parent_comp is not None}
            break
    rec["prefix_steps"] = int(w.step); rec["prefix_limit_used"] = PREFIX_LIMIT
    rec["integrity_ok_prefix"] = bool(integ); rec["t_m"] = t_m
    if t_m is None or trig.parent_comp is None:
        rec.update({"TRIGGERED": t_m is not None, "ADMISSIBLE": False,
                    "REASON": "NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE" if t_m is None
                              else "TRIGGERED_IDENTITY_NOT_CARRIED",
                    "instance_cost": round(int(w.step) / horizon, 5),
                    "runtime_s": round(time.time() - t0, 1)})
        return rec, None, None
    pcells = [trig.cells_tm[i] for i in trig.parent_comp]
    dcells = [trig.cells_tm[i] for i in trig.daughter_comp]
    ph = FMW.phys_hash(w); rh = FMW.rng_hash(w)
    S = copy.deepcopy(w); H = copy.deepcopy(w)
    rec["AT_TRIGGER"] = at
    rec["FORK"] = {"PHYSICAL_STATE_IDENTICAL": FMW.phys_hash(S) == FMW.phys_hash(H) == ph,
                   "RNG_STATE_IDENTICAL": FMW.rng_hash(S) == FMW.rng_hash(H) == rh,
                   "phys_hash_at_fork": ph, "rng_hash_at_fork": rh,
                   "locked_daughter_cells": [[int(a), int(b)] for a, b in dcells],
                   "parent_cells": [[int(a), int(b)] for a, b in pcells]}
    audit = {}
    for name, arm, cells in (("SELECTIVE", S, pcells), ("SHAM", H, ())):
        Yb = int(arm.n["Y"].sum()); Wb = int(arm.n["WY"].sum())
        db = int(sum(int(arm.n["Y"][y, x]) for y, x in dcells))
        r0 = FMW.rng_hash(arm); p0 = FMW.phys_hash(arm)
        FMW.intervene(arm, cells)
        Ya = int(arm.n["Y"].sum()); Wa = int(arm.n["WY"].sum())
        da = int(sum(int(arm.n["Y"][y, x]) for y, x in dcells))
        pa = int(sum(int(arm.n["Y"][y, x]) for y, x in pcells))
        audit[name] = {"Y_before": Yb, "Y_after": Ya, "WY_before": Wb, "WY_after": Wa,
                       "removed": Yb - Ya, "daughter_Y_before": db, "daughter_Y_after": da,
                       "parent_Y_after": pa, "rng_unchanged": FMW.rng_hash(arm) == r0,
                       "phys_unchanged": FMW.phys_hash(arm) == p0,
                       "occupancy_conserved": (Yb - Ya) == (Wa - Wb),
                       "daughter_untouched": db == da}
    audit["SELECTIVE"]["parent_emptied"] = audit["SELECTIVE"]["parent_Y_after"] == 0
    audit["SHAM"]["removed_nothing"] = (audit["SHAM"]["removed"] == 0 and audit["SHAM"]["phys_unchanged"]
                                        and audit["SHAM"]["rng_unchanged"])
    rec["INTERVENTION_AUDIT"] = audit
    os.makedirs(rawdir, exist_ok=True)
    arch = {}
    for name, arm in (("SELECTIVE", S), ("SHAM", H)):
        ok = True
        for t in range(t_m + 1, horizon):
            arm._one_step()
            free = sp.CAP - sum(arm.n[s] for s in SPECIES)
            if free.min() < 0 or max(arm.n[s].max() for s in SPECIES) > sp.CAP: ok = False; break
            arm.tl_record(t)
        tag = "OMLDCT02_i%04d_s%d_%s" % (index, seed, name)
        meta = {"tag": tag, "mission": "OMLDCT02", "arm": name, "index": index, "seed": seed,
                "law": "LAW_C_MCTT01", "kY": v["kY"], "muY": v["muY"], "p_hop_Y": v["p_hop_Y"],
                "steps_executed": int(arm.step), "horizon": horizon, "integrity_ok": bool(ok),
                "t_m": t_m,
                "intervention": {"applied": name == "SELECTIVE", "step": t_m,
                                 "parent_cells": [[int(a), int(b)] for a, b in pcells],
                                 "daughter_cells_after": [[int(a), int(b)] for a, b in dcells],
                                 "removed_Y": audit[name]["removed"],
                                 "rng_hash_before": rh, "rng_hash_after": FMW.rng_hash(arm)},
                "final_phys_hash": FMW.phys_hash(arm)}
        p = os.path.join(rawdir, tag + ".npz")
        sha, nbytes = _write(p, arm, meta)
        arch[name] = {"tag": tag, "path": p, "sha256": sha, "bytes": nbytes,
                      "steps_executed": int(arm.step), "integrity_ok": bool(ok),
                      "final_phys_hash": meta["final_phys_hash"]}
    rec.update({"TRIGGERED": True, "ADMISSIBLE": True,
                "ARMS_DIVERGED": arch["SELECTIVE"]["final_phys_hash"] != arch["SHAM"]["final_phys_hash"],
                "ARCHIVES": arch,
                "instance_cost": round((t_m + 1) / horizon + 2 * (horizon - t_m - 1) / horizon, 5),
                "runtime_s": round(time.time() - t0, 1)})
    return rec, arch["SELECTIVE"]["path"], arch["SHAM"]["path"]
