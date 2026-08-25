"""FIMRCC01 Section 3 — Precondition B: the two classifiers, compared world by world.

Classifier 1 is the frozen tlmr01_offline, byte-unchanged, which reads the online component id.
Classifier 2 is fimrcc01_independent, which reads coordinates and per-cell Y occupancy only.

The required agreement is 100 % on M2, M3, M5 and the event step. Anything less is a FAIL and the
disagreeing worlds are named.
"""
from __future__ import annotations
import tlmr01_offline as OFF
import fimrcc01_independent as IND

def norm(o):
    """JSON round-trips integer dict keys to strings; normalise BOTH sides identically so the
    comparison tests values, not key typing. The same helper closed TLMR01 F-01."""
    if isinstance(o,dict): return {str(k):norm(v) for k,v in o.items()}
    if isinstance(o,list): return [norm(v) for v in o]
    return o

def ep_key(e):
    """the episode fields both classifiers must agree on, including the gates and the event step."""
    k={f:e[f] for f in ("start","end","length","n_at_separation","terminator",
                        "interior_ambiguous_steps","IDENTITY_AMBIGUOUS","MATURED","candidate_step")}
    for f in ("candidate_ncen","candidate_f5_ratio","GATE_deadline","GATE_exactly_two_centres",
              "GATE_local_x_ratio","TRIGGERS","candidate_x_disc"):
        if f in e: k[f]=e[f]
    return k

def components_selfcheck(A,stride=97):
    """the independent classifier's fast label propagation against an explicit union-find over
    every adjacent pair, on a deterministic sample of steps. Both close the same relation; this
    checks the implementation, not the definition."""
    import numpy as np
    ck=0; bad=[]
    for t in range(0,A.T,stride):
        rows=A.cells.get(t)
        if not rows: continue
        ys=np.array([r[0] for r in rows]); xs=np.array([r[1] for r in rows])
        ck+=1
        if IND.components_from_cells(ys,xs)!=IND._components_reference(ys,xs): bad.append(t)
    return {"stride":stride,"n_steps_checked":ck,"n_disagreements":len(bad),
            "first_disagreement":(bad[0] if bad else None),"AGREES":len(bad)==0}

def compare(path):
    A=OFF.Archive(path)
    I=IND.Independent(A)
    sc=components_selfcheck(A)

    e1=OFF.episodes(A); e2=IND.episodes(I)
    m2_1=OFF.M2_maturation(e1); m2_2=IND.M2(e2)
    m3_1=OFF.M3_trigger_given_matured(e1); m3_2=IND.M3(e2)
    m5_1=OFF.M5_world_chain(A,e1); m5_2,ev2,tr2=IND.M5(I,A,e2)

    iv=A.meta.get("intervention",{})
    ev_step_1=A.meta.get("t_m")
    ev_step_2=m3_2["first_trigger_step"]

    ncen_bad=[t for t in range(A.T) if I.ncen(t)!=int(A.ncomp[t])]
    eps_equal=(len(e1)==len(e2) and all(norm(ep_key(a))==norm(ep_key(b)) for a,b in zip(e1,e2)))
    m5_1c={k:v for k,v in m5_1.items() if k!="post_removal_intervals"}
    m5_2c={k:v for k,v in m5_2.items() if k!="post_removal_intervals"}

    out={"tag":A.meta["tag"],"law":A.meta["law"],"seed":A.meta["seed"],"T":A.T,
         "TERMINAL_LABEL":A.meta["TERMINAL_LABEL"],
         "removal_applied":bool(iv.get("applied")),
         "N_STEPS_COMPARED":A.T,
         "N_COMPONENT_COUNT_DISAGREEMENTS":len(ncen_bad),
         "FIRST_COMPONENT_COUNT_DISAGREEMENT":(ncen_bad[0] if ncen_bad else None),
         "COMPONENTS_FAST_VS_UNIONFIND":sc,
         "XD_PHYSICAL_MATCH_IS_A_BIJECTION":I.xd_match_ok,
         "N_XD_MATCH_FAILURES":len(I.xd_mismatch_steps),
         "N_EPISODES":[len(e1),len(e2)],
         "EPISODES_AGREE":eps_equal,
         "M2_AGREES":norm(m2_1)==norm(m2_2),
         "M3_AGREES":norm(m3_1)==norm(m3_2),
         "M5_AGREES":norm(m5_1c)==norm(m5_2c),
         "EVENT_STEP":[ev_step_1,ev_step_2],
         "EVENT_STEP_AGREES":(ev_step_1==ev_step_2),
         "M5_1":m5_1c,"M5_2":m5_2c}
    out["ALL_AGREE"]=bool(out["EPISODES_AGREE"] and out["M2_AGREES"] and out["M3_AGREES"]
                          and out["M5_AGREES"] and out["EVENT_STEP_AGREES"]
                          and out["N_COMPONENT_COUNT_DISAGREEMENTS"]==0
                          and sc["AGREES"] and I.xd_match_ok)
    if not out["ALL_AGREE"]:
        d=[]
        if not out["EPISODES_AGREE"]:
            for a,b in zip(e1,e2):
                if norm(ep_key(a))!=norm(ep_key(b)):
                    d.append({"episode_start":a["start"],"frozen":ep_key(a),"independent":ep_key(b)})
                    if len(d)>=3: break
        out["FIRST_DISAGREEMENTS"]=d
        out["M3_FROZEN"]=m3_1; out["M3_INDEPENDENT"]=m3_2
    return out
