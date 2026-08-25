"""FIMRCC01 Section 2 — Precondition A: locate the frozen daughter offline and qualify it.

The daughter is NOT defined here. It is named by frozen inherited code at the 1 -> 2 separation
and recorded in every archive's meta. This module locates that recorded daughter among the OFFLINE
components rebuilt from the written cell rows, follows its identity interval under the frozen link
rule, and evaluates the frozen turnover endpoint inside that ONE interval.

`id_trace` is a re-implementation of tlmr01_offline.identity_intervals that additionally returns
the per-step identity assignment. It is asserted EQUAL to the frozen function on every archive it
touches; if it ever differs the world is reported as a failure, never silently accepted.
"""
from __future__ import annotations
import tlmr01_offline as OFF

def id_trace(A):
    """identity_intervals, plus trace[t] = the interval id of each component at t, in comp order."""
    yb={}; yd={}; xb={}
    for arr,d in ((A.ybirth,yb),(A.ydeath,yd),(A.xbirth,xb)):
        for r in arr:
            d.setdefault(int(r[0]),[]).append(((int(r[1]),int(r[2])),int(r[3])))
    nxt=0; prev_c=None; prev_ids=[]; ev={}; trace={}
    for t in range(A.T):
        cl=A.comps.get(t)
        if not cl: prev_c=None; prev_ids=[]; continue
        cens=[(d["cy"],d["cx"]) for d in cl]
        m=OFF.link(prev_c,cens) if prev_c is not None else {}
        ids=[]; sets={}
        for (y,x,n,cid) in A.cells.get(t,()): sets.setdefault(cid,set()).add((y,x))
        for j in range(len(cl)):
            src=[i for i,jj in m.items() if jj==j]
            if len(src)==1 and src[0]<len(prev_ids): i=prev_ids[src[0]]
            else:
                i=nxt; nxt+=1
                ev[i]={"start":t,"end":t,"ybirth":[],"ydeath":[],"xbirth":[],"minNY":10**9,"steps":0}
            ids.append(i); e=ev[i]; e["end"]=t; e["steps"]+=1
            S=sets.get(cl[j]["id"],set())
            e["minNY"]=min(e["minNY"],cl[j]["nY"])
            for c,k in yb.get(t,()):
                if c in S: e["ybirth"].append(t)
            for c,k in yd.get(t,()):
                if c in S: e["ydeath"].append(t)
            for c,k in xb.get(t,()):
                if c in S: e["xbirth"].append(t)
        trace[t]=list(ids)
        prev_c=cens; prev_ids=ids
    return ev,trace

def cellsets(A,t):
    s={}
    for (y,x,n,cid) in A.cells.get(t,()): s.setdefault(cid,set()).add((y,x))
    return s

def localise(A,t,cells):
    """Which OFFLINE component at step t is the recorded daughter? Exact set equality only.
    Containment and multiplicity are reported so a near-miss can never pass as a match."""
    want=set((int(a),int(b)) for a,b in cells)
    cl=A.comps.get(t,[]); sets=cellsets(A,t)
    exact=[j for j,d in enumerate(cl) if sets.get(d["id"],set())==want]
    contain=[j for j,d in enumerate(cl) if want and want<=sets.get(d["id"],set())]
    overlap=[j for j,d in enumerate(cl) if want & sets.get(d["id"],set())]
    return {"n_components_at_t":len(cl),"n_recorded_daughter_cells":len(want),
            "exact_matches":exact,"containment_matches":contain,"overlap_matches":overlap,
            "UNIQUE_EXACT":len(exact)==1,
            "REQUIRED_A_TIE_BREAK":len(exact)>1 or (len(exact)==0 and len(contain)>1)}

def follow(A,trace,did,t0):
    """the daughter interval's life after t0, and why it ended."""
    steps=[t for t in range(t0,A.T) if did in trace.get(t,())]
    if not steps: return {"alive_at_t0":False,"last_step":None,"steps_after_t0":0,
                          "END_REASON":"NOT_PRESENT_AT_T0"}
    last=max(steps)
    if last>=A.T-1: reason="REACHED_THE_WINDOW_HORIZON"
    else:
        cl=A.comps.get(last,[]); nx=A.comps.get(last+1,[])
        if not nx: reason="NO_COMPONENT_AT_THE_NEXT_STEP"
        else:
            j=trace[last].index(did)
            r=OFF.link_reason([(d["cy"],d["cx"]) for d in cl],[(d["cy"],d["cx"]) for d in nx])
            reason=r.get(j,"UNCLASSIFIED")
    return {"alive_at_t0":True,"last_step":last,"steps_after_t0":last-t0,
            "contiguous":len(steps)==(last-min(steps)+1),"END_REASON":reason}

def qualify(path):
    A=OFF.Archive(path)
    meta=A.meta; iv=meta.get("intervention",{})
    eps=OFF.episodes(A)
    amb=sum(1 for e in eps if e["IDENTITY_AMBIGUOUS"])
    m3=OFF.M3_trigger_given_matured(eps)
    row={"tag":meta["tag"],"law":meta["law"],"seed":meta["seed"],"T":A.T,
         "TERMINAL_LABEL":meta["TERMINAL_LABEL"],"online_t_m":meta.get("t_m"),
         "identity_carried_to_maturation":(meta.get("AT_TRIGGER") or {}).get("identity_carried_to_maturation"),
         "n_episodes":len(eps),"n_identity_ambiguous_episodes":amb,
         "n_matured":m3["n_matured"],"n_triggered":m3["n_triggered"],
         "removal_applied":bool(iv.get("applied")),"removal_step":iv.get("step"),
         "TRACE_EQUALS_FROZEN":None,"DAUGHTER":None}
    if not iv.get("applied"):
        return row
    ev,trace=id_trace(A)
    row["TRACE_EQUALS_FROZEN"]=(ev==OFF.identity_intervals(A))
    tm=int(iv["step"])
    row["removal_step_equals_online_t_m"]=(meta.get("t_m") is not None and tm==int(meta["t_m"]))
    loc=localise(A,tm,iv.get("daughter_cells_after") or [])
    d={"localisation":loc}
    if loc["UNIQUE_EXACT"]:
        j=loc["exact_matches"][0]
        ids=trace.get(tm,[])
        if j<len(ids):
            did=ids[j]
            d["interval_id"]=did
            d["interval_id_is_unique_at_t_m"]=(ids.count(did)==1)
            d["life"]=follow(A,trace,did,tm)
            one={did:ev[did]}
            D=OFF.turnover_in(one,tm)
            d["daughter_endpoint"]={
              "n_complete":len(D),
              "n_functional":sum(1 for x in D if x["FUNCTIONAL"]),
              "COMPLETE":bool(D),
              "FUNCTIONAL":any(x["FUNCTIONAL"] for x in D),
              "detail":D}
        else:
            d["interval_id"]=None; d["interval_id_is_unique_at_t_m"]=False
    # the unrestricted frozen endpoint, for the saturation contrast only
    Dall=OFF.turnover_in(ev,tm)
    d["unrestricted_endpoint"]={"n_complete":len(Dall),
      "n_functional":sum(1 for x in Dall if x["FUNCTIONAL"]),
      "FUNCTIONAL":any(x["FUNCTIONAL"] for x in Dall)}
    row["DAUGHTER"]=d
    return row
