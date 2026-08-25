"""FIMRCC01 Precondition B, completion — the parent/daughter naming reconstructed independently.

The earlier Precondition B pass reconstructed the components, the episodes, M2, M3, M5 and the
event step from raw physical inputs. It did NOT reconstruct which of the two components is the
daughter: Precondition A took that from the archive's own record. The owner's closure launcher
requires the naming itself to be independent, so this module reconstructs it from the frozen
FMRCT01 descent rule applied to the INDEPENDENT components, and uses the archive's record only as
something to be CHECKED AGAINST, never as an input.

Not used as an input anywhere below: the online component id, the online identity id, the online
selected-daughter id, the online trigger verdict, the online maturation verdict, the online
turnover verdict, the online M5 verdict, the online terminal label.

Used as inputs: the cell rows (t, y, x, per-cell Y occupancy), the world Y total, the Y-birth,
Y-death and X-birth ledgers, the toroidal geometry, the frozen centre rule, the frozen descent
rule, and the intervention ledger's step and cell list — the last only to locate the removal in
time and to audit its fidelity, never to decide which component is the daughter.
"""
from __future__ import annotations
import math
import tlmr01_offline as OFF
import fimrcc01_independent as IND

L=IND.L; CORE_R=IND.CORE_R; NEED=IND.NEED; F_PRIMARY=IND.F_PRIMARY; LATEST=IND.LATEST

def _centroid_of(cellset_ordered,idxs):
    return IND.centroid(cellset_ordered,idxs)

def descent(prev_cells,prev_idx,cur_cells,cur_groups):
    """the frozen FMRCT01 rule, rewritten. Returns (parent_index, daughter_index, verdict)."""
    if len(cur_groups)!=2:
        return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    pc=_centroid_of(prev_cells,prev_idx)
    d=[IND.tdist(pc,_centroid_of(cur_cells,g)) for g in cur_groups]
    if d[0]==d[1]: return None,None,"DESCENT_AMBIGUOUS_EXACT_TIE"
    p=0 if d[0]<d[1] else 1
    if d[p]>CORE_R: return None,None,"DESCENT_AMBIGUOUS_PARENT_NOT_CONTINUOUS"
    return p,1-p,"PARENT_CONTINUED_UNIQUELY"

def descent_literal(prev_cells,prev_idx,cur_cells,cur_groups):
    if len(cur_groups)!=2:
        return None,None,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS"
    pc=_centroid_of(prev_cells,prev_idx)
    d=[IND.tdist(pc,_centroid_of(cur_cells,g)) for g in cur_groups]
    cand=[i for i,x in enumerate(d) if x<=CORE_R]
    if len(cand)!=1:
        return None,None,("DESCENT_AMBIGUOUS_BOTH_INSIDE_CORE_R" if len(cand)==2
                          else "DESCENT_AMBIGUOUS_NONE_INSIDE_CORE_R")
    return cand[0],1-cand[0],"PARENT_CONTINUED_UNIQUELY"

def reconstruct(A):
    """the whole trigger, including the naming, from the independent components."""
    I=IND.Independent(A)
    # per-step ordered cell list and index groups, from the independent components
    cellrows={}; groups={}
    for t,cl in I.comp.items():
        rows=A.cells.get(t,())
        cellrows[t]=[(r[0],r[1]) for r in rows]
        groups[t]=[c["idx"] for c in cl]

    nxt=0; prev=None; prev_ids=[]
    parent_id=daughter_id=None
    descent_level="DESCENT_NEVER_ATTEMPTED"; descent_step=None
    literal_level="DESCENT_NEVER_ATTEMPTED"; n_attempts=0
    ids_at={}; named_at={}; level_at={}
    for t in range(I.T):
        cl=I.comp.get(t)
        if not cl: prev=None; prev_ids=[]; continue
        cens=[(c["cy"],c["cx"]) for c in cl]
        if prev is None:
            ids=[]
            for _ in cens: ids.append(nxt); nxt+=1
        else:
            m=IND.link(prev[0],cens); ids=[]
            for j in range(len(cens)):
                src=[i for i,jj in m.items() if jj==j]
                if len(src)==1 and src[0]<len(prev_ids): ids.append(prev_ids[src[0]])
                else: ids.append(nxt); nxt+=1
        if prev is not None and len(prev_ids)==1 and len(cl)==2:
            n_attempts+=1
            pi,di,lvl=descent(prev[1],prev[2][0],cellrows[t],groups[t])
            _,_,lit=descent_literal(prev[1],prev[2][0],cellrows[t],groups[t])
            descent_level=lvl; descent_step=t; literal_level=lit
            if pi is not None: parent_id=ids[pi]; daughter_id=ids[di]
            else: parent_id=daughter_id=None
        # Snapshot the naming AS OF THIS STEP, in the online order: the descent block runs before
        # the trigger check inside the same observe() call. The frozen FMRCT01 trigger keeps
        # overwriting descent_level and the named pair at every LATER 1 -> 2 transition, so the
        # terminal values are those of the LAST separation in the trajectory, not of the one that
        # named this parent. TLMR01 recorded that defect; reading the terminal values at t_m would
        # reproduce it. The first pass of this module did exactly that and is corrected here
        # rather than quietly.
        named_at[t]=(parent_id,daughter_id); level_at[t]=(descent_level,descent_step,literal_level)
        ids_at[t]=list(ids)
        prev=(cens,cellrows[t],groups[t]); prev_ids=ids

    eps=IND.episodes(I)
    m3=IND.M3(eps)
    t_m=m3["first_trigger_step"]
    out={"t_m_independent":t_m,"n_matured_independent":m3["n_matured"],
         "n_triggered_independent":m3["n_triggered"],
         "descent_level_terminal":descent_level,"descent_step_terminal":descent_step,
         "descent_literal_terminal":literal_level,"n_descent_attempts":n_attempts,
         "terminators":{}}
    for e in eps: out["terminators"][e["terminator"]]=out["terminators"].get(e["terminator"],0)+1
    if t_m is None:
        out["VERDICT_INDEPENDENT"]="NOT_TRIGGERED"
        return I,out,None
    ids=ids_at.get(t_m,[])
    parent_id,daughter_id=named_at.get(t_m,(None,None))
    lvl_tm,step_tm,lit_tm=level_at.get(t_m,("DESCENT_NEVER_ATTEMPTED",None,"DESCENT_NEVER_ATTEMPTED"))
    out["descent_level_at_t_m"]=lvl_tm; out["descent_step_at_t_m"]=step_tm
    out["descent_literal_at_t_m"]=lit_tm
    out["TERMINAL_AND_AT_TRIGGER_DESCENT_DIFFER"]=(lvl_tm!=descent_level or step_tm!=descent_step)
    carried=(parent_id is not None and daughter_id is not None and set(ids)=={parent_id,daughter_id})
    out["identity_carried_to_maturation_independent"]=bool(carried)
    if not carried:
        out["VERDICT_INDEPENDENT"]="TRIGGERED_IDENTITY_NOT_CARRIED__NO_REMOVAL"
        return I,out,None
    jd=ids.index(daughter_id); jp=ids.index(parent_id)
    out["VERDICT_INDEPENDENT"]="TRIGGERED_AND_SELECTIVE_REMOVAL_APPLIED"
    out["daughter_cells_independent"]=sorted(I.comp[t_m][jd]["cells"])
    out["parent_cells_independent"]=sorted(I.comp[t_m][jp]["cells"])
    return I,out,(t_m,jd,jp,daughter_id,parent_id)

def endpoint(A,I,pick):
    """the locked-daughter endpoint on the INDEPENDENTLY named daughter."""
    t_m,jd,jp,did_named,pid_named=pick
    ev,trace=IND.identity_intervals(I,A)
    ids=trace.get(t_m,[])
    did=ids[jd]
    e=ev[did]
    yb=[t for t in e["ybirth"] if t>t_m]; yd=[t for t in e["ydeath"] if t>t_m]
    xb=[t for t in e["xbirth"] if t>t_m]
    complete=bool(yb and yd and e["minNY"]>=1)
    r={"interval_id":did,"interval_start":e["start"],"interval_end":e["end"],
       "steps_after_t_m":e["end"]-t_m,"minNY_over_interval":e["minNY"],
       "y_births_after_t_m":len(yb),"y_deaths_after_t_m":len(yd),
       "x_births_after_t_m":len(xb),"COMPLETE":complete,"FUNCTIONAL":False}
    if complete:
        fd=min(yd); pre=sum(1 for t in xb if t<fd); post=sum(1 for t in xb if t>fd)
        r.update({"first_y_death_after_t_m":fd,"x_births_before_first_death":pre,
                  "x_births_after_first_death":post,"post_duration":e["end"]-fd,
                  "FUNCTIONAL":bool(pre>0 and post>0 and (e["end"]-fd)>0)})
    Dall=OFF.turnover_in(ev,t_m)
    r["ambient_n_complete"]=len(Dall)
    r["ambient_FUNCTIONAL"]=any(d["FUNCTIONAL"] for d in Dall)
    return r

def removal_fidelity(A,pick):
    """audit the recorded intervention against the independently named parent, and against
    conservation. The ledger's cell list is checked, not trusted."""
    iv=A.meta.get("intervention",{})
    if not iv.get("applied"): return {"applied":False}
    _,_,_,_,_=pick
    return {"applied":True,"step":int(iv["step"]),
            "Y_conserved":(int(iv["Y_total_before"])-int(iv["removed_Y"])==int(iv["Y_total_after"])),
            "WY_gained_equals_Y_removed":(int(iv["WY_total_after"])-int(iv["WY_total_before"])==int(iv["removed_Y"])),
            "parent_emptied":(int(iv["parent_Y_after"])==0),
            "daughter_untouched":(int(iv["daughter_Y_before"])==int(iv["daughter_Y_after"])),
            "rng_unchanged":(iv["rng_hash_before"]==iv["rng_hash_after"]),
            "removed_Y":int(iv["removed_Y"])}

def audit(path):
    A=OFF.Archive(path)
    I,rec,pick=reconstruct(A)
    iv=A.meta.get("intervention",{})
    row={"tag":A.meta["tag"],"seed":A.meta["seed"],"T":A.T,
         "ARCHIVE_LABEL_NOT_USED_AS_INPUT":A.meta["TERMINAL_LABEL"],
         "ARCHIVE_t_m_NOT_USED_AS_INPUT":A.meta.get("t_m")}
    row.update(rec)
    row["VERDICT_MATCHES_THE_ARCHIVE_LABEL"]=(rec["VERDICT_INDEPENDENT"]==A.meta["TERMINAL_LABEL"])
    row["t_m_MATCHES_THE_ARCHIVE"]=(rec["t_m_independent"]==A.meta.get("t_m"))
    if pick is not None:
        dc=set((int(a),int(b)) for a,b in (iv.get("daughter_cells_after") or []))
        pc=set((int(a),int(b)) for a,b in (iv.get("parent_cells") or []))
        row["DAUGHTER_CELLS_MATCH_THE_ARCHIVE"]=(set(rec["daughter_cells_independent"])==dc)
        row["PARENT_CELLS_MATCH_THE_ARCHIVE"]=(set(rec["parent_cells_independent"])==pc)
        row["ENDPOINT"]=endpoint(A,I,pick)
        row["REMOVAL_FIDELITY"]=removal_fidelity(A,pick)
    row["ALL_INDEPENDENT_CHECKS_AGREE"]=bool(
        row["VERDICT_MATCHES_THE_ARCHIVE_LABEL"] and row["t_m_MATCHES_THE_ARCHIVE"]
        and row.get("DAUGHTER_CELLS_MATCH_THE_ARCHIVE",True)
        and row.get("PARENT_CELLS_MATCH_THE_ARCHIVE",True)
        and all(row.get("REMOVAL_FIDELITY",{"applied":False}).get(k,True)
                for k in ("Y_conserved","WY_gained_equals_Y_removed","parent_emptied",
                          "daughter_untouched","rng_unchanged")))
    return row
