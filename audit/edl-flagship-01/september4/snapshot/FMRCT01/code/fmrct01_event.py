"""FMRCT01 §6 — the frozen block-level event R0..R6 (implementation A).

Evaluated offline from the committed raw ledgers. The rules are the frozen ones: toroidal
single-linkage centres, the strict FDOT01 identity link, the FMRCT01 descent rule, the FDFLT01
maturation trigger and the ACTIVE_LOCAL_X_PRODUCTION functional criterion.
"""
from __future__ import annotations
import json, sys
import numpy as np
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/FMRCT01/code")
import fmrct01_track as T
import fmrct01_descent as DS
CC=T.CC; HOR=T.T_HORIZON

def load(path):
    z=np.load(path,allow_pickle=True)
    return json.loads(str(z["meta"][0])),z

def daughter_after(steps,ev,t_m,daughter_cells):
    """the identity id occupying the daughter's cells at t_m"""
    s=steps.get(t_m)
    if s is None: return None
    want=set(tuple(c) for c in daughter_cells)
    for j,S in enumerate(s["sets"]):
        if S==want: return s["ids"][j]
    for j,S in enumerate(s["sets"]):
        if S & want: return s["ids"][j]
    return None

def evaluate(sel, base_path, selective_path, global_path):
    """sel = one entry of FMRCT01_FORK_SELECTION.json"""
    t_m=sel["t_m"]
    R={"block":sel["block"],"seed":sel["seed"],"t_m":t_m}
    mb,zb=load(base_path); ms,zs=load(selective_path); mg,zg=load(global_path)
    R["fork_identity_ok"]=bool(ms.get("fork_identity_ok") and mg.get("fork_identity_ok"))
    R["rng_untouched"]=bool(ms.get("rng_untouched_by_intervention") and mg.get("rng_untouched_by_intervention"))
    R["removed_selective"]=ms.get("removed"); R["removed_global"]=mg.get("removed")

    # ---------------- SELECTIVE arm ----------------
    st,ev=T.track(zs["ycells"],zs["ybirth"],zs["ydeath"],zs["xbirth"],HOR)
    did=daughter_after(st,ev,t_m,sel["daughter_cells"])
    pid=daughter_after(st,ev,t_m,sel["parent_cells"])
    R["daughter_id"]=did; R["parent_id"]=pid
    R["R0_single_parent_tracked"]=bool(pid is not None)
    R["R1_endogenous_daughter_uniquely_identified"]=bool(did is not None and pid is not None and did!=pid)
    e=ev.get(did) if did is not None else None
    xb_pre=[t for t,_ in e["xbirth"] if t<=t_m] if e else []
    R["R2_daughter_matured_and_produced_local_X"]=bool(e is not None and len(xb_pre)>0)
    # R3 selective removal fidelity
    pc=set(tuple(c) for c in sel["parent_cells"]); dc=set(tuple(c) for c in sel["daughter_cells"])
    yb_tm={(int(r[1]),int(r[2])):int(r[3]) for r in zs["ycells"] if int(r[0])==t_m}
    par_Y=sum(v for c,v in yb_tm.items() if c in pc); dau_Y=sum(v for c,v in yb_tm.items() if c in dc)
    ys_tm1={(int(r[1]),int(r[2])):int(r[3]) for r in zs["ycells"] if int(r[0])==t_m+1}
    R["parent_Y_at_tm"]=par_Y; R["daughter_Y_at_tm"]=dau_Y
    R["R3_selective_removal_fidelity"]=bool(ms.get("removed")==par_Y and par_Y>0)
    # R4 continued local X production after removal
    xb_post=[t for t,_ in e["xbirth"] if t>t_m] if e else []
    R["daughter_x_births_after_tm"]=len(xb_post)
    R["R4_continued_local_X_production"]=bool(len(xb_post)>0)
    # R5 constituent turnover after removal, inside ONE identity interval
    to=T.identity_turnover(ev,did,t_m,window=None,require_after=t_m) if did is not None else None
    R["turnover"]=to
    R["R5_complete_turnover_after_removal"]=bool(to and to["COMPLETE"])
    R["R6_function_both_sides"]=bool(to and to["FUNCTIONAL"])
    # parent absence after removal
    pe=ev.get(pid) if pid is not None else None
    R["parent_identity_end"]=pe["end"] if pe else None
    R["parent_absent_after_removal"]=bool(pe is None or pe["end"]<=t_m)
    # ---------------- controls ----------------
    stg,evg=T.track(zg["ycells"],zg["ybirth"],zg["ydeath"],zg["xbirth"],HOR)
    gx=[int(r[0]) for r in zg["xbirth"] if int(r[0])>t_m]
    R["GLOBAL_OFF_x_births_anywhere_after_tm"]=len(gx)
    gY=[int(r[3]) for r in zg["ycells"] if int(r[0])>t_m]
    R["GLOBAL_OFF_Y_present_after_tm"]=int(sum(gY))
    R["GLOBAL_OFF_control_ok"]=bool(len(gx)==0 and sum(gY)==0)
    stb,evb=T.track(zb["ycells"],zb["ybirth"],zb["ydeath"],zb["xbirth"],HOR)
    dbid=daughter_after(stb,evb,t_m,sel["daughter_cells"])
    eb=evb.get(dbid) if dbid is not None else None
    R["SHAM_daughter_x_births_after_tm"]=len([t for t,_ in eb["xbirth"] if t>t_m]) if eb else 0
    R["SHAM_daughter_identity_end"]=eb["end"] if eb else None
    R["SHAM_control_ok"]=bool(eb is not None and R["SHAM_daughter_x_births_after_tm"]>0)
    reqs=["R0_single_parent_tracked","R1_endogenous_daughter_uniquely_identified",
          "R2_daughter_matured_and_produced_local_X","R3_selective_removal_fidelity",
          "R4_continued_local_X_production","R5_complete_turnover_after_removal",
          "R6_function_both_sides"]
    R["R_ALL"]=all(R[k] for k in reqs)
    R["CONTROLS_OK"]=bool(R["GLOBAL_OFF_control_ok"] and R["SHAM_control_ok"])
    R["MINIMAL_REPRODUCTION_CAUSAL_SUCCESS"]=bool(R["R_ALL"] and R["CONTROLS_OK"]
                                                  and R["fork_identity_ok"] and R["parent_absent_after_removal"])
    return R
