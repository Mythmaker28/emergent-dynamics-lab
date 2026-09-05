"""TBRT02 — the three-arm fork. One base seed in, one ledger record and up to three archives out.

The common prefix and the trigger are IDENTICAL to OMLDCT02's, imported and re-specified nowhere, so
admissibility is decided exactly as before and the accrual arithmetic measured on OMLDCT02's 805
prospective seeds transfers without adjustment. The only change is three worlds instead of two. The
archive writer, the narrow-dtype packer and the TLMR01-ARCHIVE-1 schema are OMLDCT02's, imported
verbatim, so every downstream tool in this programme already reads what TBRT02 produces.

Every scientific-scale construction passes through tbrt02_guard.assert_allowed first.
"""
from __future__ import annotations
import copy, json, os, sys, time
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("TBRT02/code", "OMLDCT02/code", "TLMR01/code", "FMRCT01/code", "PQEC01/code",
          "ORR01/code", "OBTC02/code"):
    sys.path.insert(0, os.path.join(REPO, p))
import tlmr01_world as TW            # noqa: E402
import fmrct01_world as FMW          # noqa: E402
import fmrct01_track as TR           # noqa: E402
import pqec01_observer as O          # noqa: E402
import omldct02_fork as OF           # noqa: E402
import tbrt02_guard as G             # noqa: E402
import tbrt02_displace as D          # noqa: E402

_write = OF._write
SCHEMA = OF.SCHEMA
SPECIES = O.SPECIES
LAW = {"kY": 0.001004754572603833, "muY": 0.000740894982503035,
       "p_hop_Y": 0.10263340389897246}
L_GRID = 36
T_HORIZON = 11000
ARMS = ("SHAM", "SELECTIVE", "DISPLACED")


def one_seed(index, seed, rawdir, horizon=T_HORIZON):
    G.assert_allowed(L=L_GRID, horizon=horizon, seed=seed, what=f"base seed index {index}")
    v = LAW
    t0 = time.time()
    rec = {"index": index, "seed": seed, "law": "LAW_C_MCTT01", "mission": "TBRT02",
           "kY": v["kY"], "muY": v["muY"], "p_hop_Y": v["p_hop_Y"], "horizon": horizon}
    w, _, sp = TW.build(seed, v["kY"], v["muY"], v["p_hop_Y"], horizon=horizon)
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
                    "runtime_s": round(time.time() - t0, 1), "technical_failure": False})
        return rec, {}
    pcells = [trig.cells_tm[i] for i in trig.parent_comp]
    dcells = [trig.cells_tm[i] for i in trig.daughter_comp]
    ph = FMW.phys_hash(w); rh = FMW.rng_hash(w)
    forks = {name: copy.deepcopy(w) for name in ARMS}
    rec["AT_TRIGGER"] = at
    rec["FORK"] = {"PHYSICAL_STATE_IDENTICAL": all(FMW.phys_hash(a) == ph for a in forks.values()),
                   "RNG_STATE_IDENTICAL": all(FMW.rng_hash(a) == rh for a in forks.values()),
                   "phys_hash_at_fork": ph, "rng_hash_at_fork": rh, "n_arms": len(ARMS),
                   "locked_daughter_cells": [[int(a), int(b)] for a, b in dcells],
                   "parent_cells": [[int(a), int(b)] for a, b in pcells]}
    audit = {}
    for name in ARMS:
        arm = forks[name]
        Yb = int(arm.n["Y"].sum()); Wb = int(arm.n["WY"].sum())
        db = int(sum(int(arm.n["Y"][y, x]) for y, x in dcells))
        r0 = FMW.rng_hash(arm); p0 = FMW.phys_hash(arm)
        extra = None
        if name == "SHAM":
            FMW.intervene(arm, ())
        elif name == "SELECTIVE":
            FMW.intervene(arm, pcells)
        else:
            extra = D.displace(arm, pcells, dcells)
        Ya = int(arm.n["Y"].sum()); Wa = int(arm.n["WY"].sum())
        da = int(sum(int(arm.n["Y"][y, x]) for y, x in dcells))
        pa = int(sum(int(arm.n["Y"][y, x]) for y, x in pcells))
        a = {"Y_before": Yb, "Y_after": Ya, "WY_before": Wb, "WY_after": Wa,
             "daughter_Y_before": db, "daughter_Y_after": da, "parent_Y_after": pa,
             "rng_unchanged": FMW.rng_hash(arm) == r0,
             "phys_unchanged": FMW.phys_hash(arm) == p0,
             "daughter_untouched": db == da}
        if name == "SHAM":
            a["removed_nothing"] = (Yb == Ya and a["phys_unchanged"] and a["rng_unchanged"])
        elif name == "SELECTIVE":
            a["removed"] = Yb - Ya
            a["occupancy_conserved"] = (Yb - Ya) == (Wa - Wb)
            a["parent_emptied"] = pa == 0
        else:
            a["displacement"] = extra
            a["Y_MASS_CONSERVED"] = Yb == Ya
            a["WY_UNTOUCHED"] = Wb == Wa
            a["parent_emptied"] = pa == 0
            a["competitor_cell"] = extra["destination"]
            a["competitor_mass"] = extra["moved"]
            a["separation_from_the_daughter"] = extra["chebyshev_to_the_nearest_daughter_cell"]
        audit[name] = a
    rec["INTERVENTION_AUDIT"] = audit
    os.makedirs(rawdir, exist_ok=True)
    arch = {}
    for name in ARMS:
        arm = forks[name]
        ok = True
        for t in range(t_m + 1, horizon):
            arm._one_step()
            free = sp.CAP - sum(arm.n[s] for s in SPECIES)
            if free.min() < 0 or max(arm.n[s].max() for s in SPECIES) > sp.CAP:
                ok = False; break
            arm.tl_record(t)
        tag = "TBRT02_i%04d_s%d_%s" % (index, seed, name)
        meta = {"tag": tag, "mission": "TBRT02", "arm": name, "index": index, "seed": seed,
                "law": "LAW_C_MCTT01", "kY": v["kY"], "muY": v["muY"], "p_hop_Y": v["p_hop_Y"],
                "steps_executed": int(arm.step), "horizon": horizon, "integrity_ok": bool(ok),
                "t_m": t_m,
                "intervention": {"arm": name, "step": t_m,
                                 "parent_cells": [[int(a), int(b)] for a, b in pcells],
                                 "daughter_cells": [[int(a), int(b)] for a, b in dcells],
                                 "competitor_cell": audit[name].get("competitor_cell"),
                                 "competitor_mass": audit[name].get("competitor_mass"),
                                 "rng_hash_before": rh, "rng_hash_after": FMW.rng_hash(arm)},
                "final_phys_hash": FMW.phys_hash(arm)}
        p = os.path.join(rawdir, tag + ".npz")
        sha, nbytes = _write(p, arm, meta)
        arch[name] = {"tag": tag, "path": p, "sha256": sha, "bytes": nbytes,
                      "steps_executed": int(arm.step), "integrity_ok": bool(ok),
                      "final_phys_hash": meta["final_phys_hash"]}
    hashes = {n: arch[n]["final_phys_hash"] for n in ARMS}
    rec.update({"TRIGGERED": True, "ADMISSIBLE": True,
                "ALL_THREE_ARMS_DIVERGED": len(set(hashes.values())) == 3,
                "ARCHIVES": arch,
                "instance_cost": round((t_m + 1) / horizon
                                       + len(ARMS) * (horizon - t_m - 1) / horizon, 5),
                "runtime_s": round(time.time() - t0, 1), "technical_failure": False})
    return rec, arch
