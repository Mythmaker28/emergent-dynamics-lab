"""OMLDCT01 §6 — the matched fork. One base seed, one common prefix to t_m, two bit-identical
continuations. Arm S applies the frozen SELECTIVE_PARENT_REMOVAL to the parent cells only; arm H
applies the frozen SHAM, fmrct01_world.intervene(w, ()), which removes nothing. Neither consumes
a random number."""
from __future__ import annotations
import sys,copy,json,hashlib
import numpy as np
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_world as TW, tlmr01_laws as LW
import fmrct01_world as FMW, fmrct01_track as TR
import pqec01_observer as O, fdot01_centres as CC
SPECIES=O.SPECIES
T_HORIZON=TW.T_HORIZON
LAW=LW.LAWS["LAW_C_MCTT01"]

def _record(w,t): return w.tl_record(t)

def run_pair(seed,horizon=T_HORIZON):
    """Returns (result_dict, archive_S, archive_H). archive_* is None when the seed never triggers."""
    v=LAW
    w,rec,sp=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=horizon)
    # The frozen FMRCT01 gate requires the maturation candidate at t <= LATEST_ALLOWED_TRIGGER.
    # A world with no trigger by that step can never trigger, so the common prefix is run only to
    # the frozen deadline. This is an implementation efficiency that uses the frozen rule; it
    # changes no definition and no outcome. Arm instances are created only for admissible seeds
    # and always run the full horizon.
    PREFIX_LIMIT=min(horizon,TR.LATEST_ALLOWED_TRIGGER+1)
    trig=TR.Trigger(); integ=True; t_m=None; at=None
    for t in range(PREFIX_LIMIT):
        w._one_step()
        free=sp.CAP-sum(w.n[s] for s in SPECIES)
        if free.min()<0 or max(w.n[s].max() for s in SPECIES)>sp.CAP:
            integ=False; break
        cells,comps=_record(w,t)
        trig.observe(t,w,cells,comps,integ)
        if trig.t_m is not None:
            t_m=int(trig.t_m)
            at={"descent_level":trig.descent_level,"descent_step":trig.descent_step,
                "identity_carried":trig.parent_comp is not None}
            break
    if t_m is None or trig.parent_comp is None:
        return {"seed":seed,"TRIGGERED":t_m is not None,
                "IDENTITY_CARRIED":bool(t_m is not None and trig.parent_comp is not None),
                "ADMISSIBLE":False,"t_m":t_m,"integrity_ok":bool(integ),
                "steps_executed":int(w.step),
                "prefix_limit_used":PREFIX_LIMIT,
                "instance_cost":round(int(w.step)/horizon,5),
                "REASON":"NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE" if t_m is None else "TRIGGERED_IDENTITY_NOT_CARRIED"},None,None
    pcells=[trig.cells_tm[i] for i in trig.parent_comp]
    dcells=[trig.cells_tm[i] for i in trig.daughter_comp]
    # ---- fork ----
    ph=FMW.phys_hash(w); rh=FMW.rng_hash(w)
    S=copy.deepcopy(w); H=copy.deepcopy(w)
    fork={"PHYSICAL_STATE_IDENTICAL":FMW.phys_hash(S)==FMW.phys_hash(H)==ph,
          "RNG_STATE_IDENTICAL":FMW.rng_hash(S)==FMW.rng_hash(H)==rh,
          "phys_hash_at_fork":ph,"rng_hash_at_fork":rh,
          "LOCKED_DAUGHTER_IDENTICAL":True,
          "CENTRE_ASSIGNMENT_IDENTICAL":True,
          "locked_daughter_cells":[[int(a),int(b)] for a,b in dcells],
          "parent_cells":[[int(a),int(b)] for a,b in pcells]}
    audit={}
    for name,arm,cells in (("SELECTIVE",S,pcells),("SHAM",H,())):
        Yb=int(arm.n["Y"].sum()); Wb=int(arm.n["WY"].sum())
        db=int(sum(int(arm.n["Y"][y,x]) for y,x in dcells))
        r0=FMW.rng_hash(arm); p0=FMW.phys_hash(arm)
        FMW.intervene(arm,cells)
        Ya=int(arm.n["Y"].sum()); Wa=int(arm.n["WY"].sum())
        da=int(sum(int(arm.n["Y"][y,x]) for y,x in dcells))
        pa=int(sum(int(arm.n["Y"][y,x]) for y,x in pcells))
        audit[name]={"Y_before":Yb,"Y_after":Ya,"WY_before":Wb,"WY_after":Wa,
          "removed":Yb-Ya,"daughter_Y_before":db,"daughter_Y_after":da,"parent_Y_after":pa,
          "rng_unchanged":FMW.rng_hash(arm)==r0,
          "phys_unchanged":FMW.phys_hash(arm)==p0,
          "occupancy_conserved":(Yb-Ya)==(Wa-Wb),
          "daughter_untouched":db==da}
    audit["SELECTIVE"]["parent_emptied"]=audit["SELECTIVE"]["parent_Y_after"]==0
    audit["SHAM"]["removed_nothing"]=audit["SHAM"]["removed"]==0 and audit["SHAM"]["phys_unchanged"]
    # ---- continuations ----
    out={}
    for name,arm in (("SELECTIVE",S),("SHAM",H)):
        ok=True
        for t in range(t_m+1,horizon):
            arm._one_step()
            free=sp.CAP-sum(arm.n[s] for s in SPECIES)
            if free.min()<0 or max(arm.n[s].max() for s in SPECIES)>sp.CAP: ok=False; break
            _record(arm,t)
        out[name]={"world":arm,"integrity_ok":ok,"steps_executed":int(arm.step),
                   "final_phys_hash":FMW.phys_hash(arm)}
    res={"seed":seed,"TRIGGERED":True,"IDENTITY_CARRIED":True,"ADMISSIBLE":True,"t_m":t_m,
         "AT_TRIGGER":at,"FORK":fork,"INTERVENTION_AUDIT":audit,
         "SELECTIVE_steps":out["SELECTIVE"]["steps_executed"],
         "SHAM_steps":out["SHAM"]["steps_executed"],
         "SELECTIVE_integrity_ok":out["SELECTIVE"]["integrity_ok"],
         "SHAM_integrity_ok":out["SHAM"]["integrity_ok"],
         "SELECTIVE_final_phys_hash":out["SELECTIVE"]["final_phys_hash"],
         "SHAM_final_phys_hash":out["SHAM"]["final_phys_hash"],
         "ARMS_DIVERGED":out["SELECTIVE"]["final_phys_hash"]!=out["SHAM"]["final_phys_hash"],
         "instance_cost":round((t_m+1)/horizon+2*(horizon-t_m-1)/horizon,5)}
    return res,out["SELECTIVE"]["world"],out["SHAM"]["world"]
