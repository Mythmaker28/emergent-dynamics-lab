"""TLMR01 §5 (continued) — PATH COVERAGE for the measurement instrument.

WHY THIS FILE EXISTS. The first §5 run proved the two required gates (INSTRUMENTATION_INERTNESS,
ARCHIVE_DECISION_RECONSTRUCTION) but its coverage fixtures were 1400 steps long and returned
max_components_seen = 1 and component_increase_events = 0 on all three laws. The fork, split,
merge, trigger and selective-removal branches of tlmr01_world.run_world had therefore NEVER
executed. §5 requires fixtures covering those paths, so the gap is closed here rather than
declared closed.

NON-SCIENTIFIC. Every trajectory in this file is a fixture. It uses fixture seeds, it is never
analysed for an outcome, and it is declared and excluded from every scientific budget.

FIXTURE OUTCOME FIREWALL. This file emits PATH BOOLEANS and CODE-LINE SETS. It does not emit, and
no TLMR01 design artefact may read, any rate, any threshold, any per-world outcome or any
estimate from a fixture. The one quantitative fact it prints, "a natural trigger occurred in the
fixture band", is already published in a committed parent artefact for this exact law
(MCTT01_STAGE_A_QUALIFICATION.json: 6 of 64), so it teaches this mission nothing it did not
inherit. The fixture set is FIXED IN ADVANCE and is run to completion whatever it finds: there is
no adaptive stopping, and therefore no outcome-dependent behaviour anywhere in this module.
"""
from __future__ import annotations
import sys, os, json, hashlib, datetime, time, dis
import numpy as np
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_world as TW, tlmr01_laws as LW
import fdot01_centres as CC, fmrct01_track as TR, fmrct01_world as FMW
import fmrct01_descent as DS
import pqec01_observer as O
SPECIES=O.SPECIES
L=CC.L; CORE_R=CC.CORE_R

# fixture band, disjoint from every primary and reserve seed by construction (§12 asserts it)
NAT_SEEDS_C=[71001,71002,71003,71004,71005,71006,71007,71008,
             71009,71010,71011,71012,71013,71014,71015,71016]
NAT_SEEDS_AB=[71101,71102,71103,71104,71105,71106,71107,71108,71109,71110,71111,71112]
INJ_SEEDS  =[71201,71202,71203]
NAT_STEPS_C=3500     # LAW_C t_m was observed at most 3188 historically; fork median 609
NAT_STEPS_AB=6500    # the frozen LATEST_ALLOWED_TRIGGER
INJ_STEPS  =8000

# ------------------------------------------------------------------ 1. deterministic geometry
def geometry_paths():
    """The identity paths, on exact synthetic configurations. No engine, no randomness.

    These exercise fdot01_centres.link and .components directly, which is where SPLIT, MERGE and
    TIE terminate an identity interval. CORE_R = 5.0, so adjacency is d^2 <= 25.
    """
    T=[]
    def rec(name,got,want):
        T.append({"case":name,"got":got,"expected":want,"PASS":got==want})
    # components: two cells 2 apart are one centre; 6 apart are two centres
    rec("components_one_centre",len(CC.components([(10,10),(10,12)])),1)
    rec("components_two_centres",len(CC.components([(10,10),(10,16)])),2)
    rec("components_toroidal_wrap",len(CC.components([(0,1),(0,L-2)])),1)
    rec("components_exact_CORE_R",len(CC.components([(0,0),(0,5)])),1)
    rec("components_just_beyond",len(CC.components([(0,0),(0,6)])),2)
    rec("components_empty",len(CC.components([])),0)
    # link: clean continuation
    rec("link_clean_continue",CC.link([(10.0,10.0)],[(10.0,11.0)]),{0:0})
    rec("link_clean_two_to_two",CC.link([(5.0,5.0),(25.0,25.0)],[(5.0,6.0),(25.0,26.0)]),{0:0,1:1})
    # SPLIT: one previous centre, two current centres both inside CORE_R -> no link at all
    rec("link_SPLIT_terminates",CC.link([(10.0,10.0)],[(10.0,8.0),(10.0,12.0)]),{})
    # MERGE: two previous centres, one current centre inside CORE_R of both -> no link
    rec("link_MERGE_terminates",CC.link([(10.0,8.0),(10.0,12.0)],[(10.0,10.0)]),{})
    # TIE: exactly equidistant, both inside CORE_R -> more than one candidate -> no link
    rec("link_TIE_terminates",CC.link([(10.0,10.0)],[(10.0,7.0),(10.0,13.0)]),{})
    # out of range: nothing within CORE_R -> no link, a fresh identity starts
    rec("link_OUT_OF_RANGE",CC.link([(0.0,0.0)],[(0.0,10.0)]),{})
    # partial: one of two previous centres links cleanly, the other is out of range
    rec("link_PARTIAL",CC.link([(0.0,0.0),(18.0,18.0)],[(0.0,1.0)]),{0:0})
    # toroidal link across the seam
    rec("link_TOROIDAL",CC.link([(0.0,0.5)],[(0.0,L-0.5)]),{0:0})
    # the frozen descent rule, on the same synthetic split
    p,d,lvl=DS.descent([(10,10)],[0],[(10,8),(10,12)],[[0],[1]])
    rec("descent_exact_tie",lvl,"DESCENT_AMBIGUOUS_EXACT_TIE")
    p,d,lvl=DS.descent([(10,10)],[0],[(10,9),(10,13)],[[0],[1]])
    rec("descent_resolves",lvl,"PARENT_CONTINUED_UNIQUELY")
    rec("descent_parent_is_nearer",p,0)
    p,d,lvl=DS.descent([(10,10)],[0],[(10,9),(10,13),(20,20)],[[0],[1],[2]])
    rec("descent_not_two_components",lvl,"DESCENT_AMBIGUOUS_NOT_EXACTLY_TWO_COMPONENTS")
    return {"N_CASES":len(T),"ALL_PASS":all(t["PASS"] for t in T),"CASES":T}

# ------------------------------------------------------------------ 2. archive path classifier
def classify_from_archive(w,steps):
    """Rebuild the per-step component structure FROM THE WRITTEN ROWS ALONE and classify every
    identity transition. This both covers the paths and shows the archive can name which path was
    taken, which is what §4 has to guarantee."""
    per={}
    for (t,y,x,nY,nX,nSY,free,cand,cid) in w.tl_cells: per.setdefault(t,[]).append((y,x,cid))
    out={"steps_with_cells":0,"max_components":0,"n_component_increase":0,"n_component_decrease":0,
         "n_clean_continuations":0,"n_split_terminations":0,"n_merge_terminations":0,
         "n_fresh_identities":0,"n_empty_gaps":0,"steps_at_two_components":0,
         "steps_above_two_components":0,"first_two_component_step":None}
    prev=None
    for t in range(steps):
        rows=per.get(t)
        if not rows:
            out["n_empty_gaps"]+=1; prev=None; continue
        out["steps_with_cells"]+=1
        cells=[(y,x) for y,x,_ in rows]
        groups={}
        for i,(y,x,c) in enumerate(rows): groups.setdefault(c,[]).append(i)
        gs=[sorted(v) for _,v in sorted(groups.items())]
        cens=[CC.centroid(cells,g) for g in gs]
        n=len(gs)
        out["max_components"]=max(out["max_components"],n)
        if n==2:
            out["steps_at_two_components"]+=1
            if out["first_two_component_step"] is None: out["first_two_component_step"]=t
        if n>2:
            out["steps_above_two_components"]+=1
            if out["first_two_component_step"] is None: out["first_two_component_step"]=t
        if prev is not None:
            pn=len(prev)
            if n>pn: out["n_component_increase"]+=1
            if n<pn: out["n_component_decrease"]+=1
            fwd={i:[j for j,c in enumerate(cens) if CC.tdist(p,c)<=CORE_R] for i,p in enumerate(prev)}
            bwd={j:[i for i,p in enumerate(prev) if CC.tdist(p,c)<=CORE_R] for j,c in enumerate(cens)}
            m=CC.link(prev,cens)
            out["n_clean_continuations"]+=len(m)
            out["n_split_terminations"]+=sum(1 for i,js in fwd.items() if len(js)>1)
            out["n_merge_terminations"]+=sum(1 for j,iss in bwd.items() if len(iss)>1)
            out["n_fresh_identities"]+=sum(1 for j in range(n) if j not in set(m.values()))
        prev=cens
    return out

def natural_paths(seed,law,steps):
    """An unmodified fixture trajectory through the real run_world, long enough for the paths."""
    v=LW.LAWS[law]
    t0=time.time()
    w,rec=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=steps)
    cl=classify_from_archive(w,steps)
    aud=removal_audit(w,rec)
    return {"seed":seed,"law":law,"steps":steps,"runtime_s":round(time.time()-t0,1),
            "AUDIT":aud,"AUDIT_ALL_PASS":bool(aud.get("ALL_PASS",False)),
            "y_birth_records":len(w.pq_ybirth),"y_death_records":len(w.pq_ydeath),
            "x_birth_records":len(w.fd_xbirth),
            "natural_trigger":rec["t_m"] is not None,
            "TERMINAL_LABEL":rec["TERMINAL_LABEL"],
            "n_descent_attempts":rec["n_descent_attempts"],
            "descent_level_at_trigger":rec["descent_level"],
            "selective_removal_applied":bool(rec["intervention"]["applied"]),
            "integrity_ok":rec["integrity_ok"],"steps_executed":rec["steps_executed"],
            **cl}


def removal_audit(w,rec,snap_Y=None):
    """The conservation audit of ONE selective parent removal, read from what run_world recorded
    on both sides of the inherited intervene(). It applies to a natural removal and to an injected
    one identically: nothing in it depends on how the trigger came to fire."""
    iv=rec["intervention"]
    if not iv["applied"]: return {"APPLIED":False}
    pc=[(int(a),int(b)) for a,b in iv["parent_cells"]]
    dc=[(int(a),int(b)) for a,b in (iv["daughter_cells_before"] or [])]
    tS=iv["step"]
    rowsA={(y,x):nY for (t,y,x,nY,nX,nSY,f,c,ci) in w.tl_cells if t==tS}
    rowsB={(y,x):nY for (t,y,x,nY,nX,nSY,f,c,ci) in w.tl_cells if t==tS+1}
    aud={"APPLIED":True,
     "removed_is_positive":iv["removed_Y"]>0,
     "parent_and_daughter_are_disjoint":len(set(pc)&set(dc))==0,
     "rng_untouched_by_the_removal":iv["rng_hash_before"]==iv["rng_hash_after"],
     "phys_changed_by_the_removal":iv["phys_hash_before"]!=iv["phys_hash_after"],
     "archive_at_the_removal_step_is_PRE_removal":all(rowsA.get(c,0)>0 for c in pc),
     "daughter_cells_present_before":all(rowsA.get(c,0)>0 for c in dc),
     "parent_Y_is_exactly_zero_after":iv["parent_Y_after"]==0,
     "daughter_Y_is_bit_unchanged":iv["daughter_Y_before"]==iv["daughter_Y_after"],
     "Y_total_falls_by_exactly_the_removed_count":
        iv["Y_total_before"]-iv["Y_total_after"]==iv["removed_Y"],
     "WY_total_rises_by_exactly_the_removed_count":
        iv["WY_total_after"]-iv["WY_total_before"]==iv["removed_Y"],
     "occupancy_is_conserved_exactly":
        (iv["Y_total_before"]+iv["WY_total_before"])==(iv["Y_total_after"]+iv["WY_total_after"]),
     "removal_step_equals_the_trigger_step":iv["step"]==rec["t_m"],
     "no_parent_cell_carries_its_removed_Y_into_the_next_step":
        all(rowsB.get(c,0)<=max(0,rowsA.get(c,0)-1) or c not in rowsB for c in pc),
     "removed_equals_the_archived_parent_Y_at_the_removal_step":
        iv["removed_Y"]==sum(rowsA.get(c,0) for c in pc)}
    if snap_Y is not None:
        aud["snapshot_agrees_with_the_engine"]=int(snap_Y.sum())==iv["Y_total_before"]
        aud["removed_equals_parent_Y_before"]=int(sum(int(snap_Y[y,x]) for y,x in pc))==iv["removed_Y"]
    aud["parent_Y_before"]=iv["Y_total_before"]-iv["Y_total_after"]
    aud["Y_total_before"]=iv["Y_total_before"]; aud["Y_total_after"]=iv["Y_total_after"]
    aud["WY_total_before"]=iv["WY_total_before"]; aud["WY_total_after"]=iv["WY_total_after"]
    aud["parent_cells_still_occupied_at_next_step"]=sum(1 for c in pc if c in rowsB)
    aud["ALL_PASS"]=all(v for k,v in aud.items() if isinstance(v,bool) and k!="APPLIED")
    return aud

# ------------------------------------------------------------------ 3. injected removal
class InjectedTrigger(TR.Trigger):
    """FIXTURE ONLY, NON-SCIENTIFIC.

    It subclasses the frozen FMRCT01 trigger and changes NOTHING about it: super().observe does
    all of the real work, including the whole identity and descent machinery. The single addition
    is that once the frozen descent rule has ALREADY named a parent and a daughter at a real
    1 -> 2 separation, and the world genuinely still holds exactly those two identities, this
    fixture fires WITHOUT waiting for the FDFLT01 maturation gate. The bypassed condition is
    exactly one thing: the 250-step functional-maturation window and its local-X mass ratio. The
    parent and daughter components handed to the intervention are the real ones, computed by the
    frozen rule from the real trajectory; no geometry is fabricated.

    Its purpose is to guarantee that run_world's OWN trigger and selective-removal lines execute
    on every law, instead of hoping a rare endogenous trigger appears in a fixture.
    """
    def __init__(self,force_at=0):
        super().__init__(); self.force_at=int(force_at); self.INJECTED=False
        self.snap_Y=None; self.snap_WY=None; self.snap_rng=None
    def observe(self,t,w,cells,comps,integ):
        fired=super().observe(t,w,cells,comps,integ)
        if fired or self.t_m is not None or t<self.force_at: return fired
        if len(comps)!=2 or self.parent_id is None or self.daughter_id is None: return fired
        ids=self._prev_ids
        if set(ids)!={self.parent_id,self.daughter_id}: return fired
        self.w.fired=True; self.t_m=t; self.cells_tm=list(cells)
        self.parent_comp=[int(i) for i in comps[ids.index(self.parent_id)]]
        self.daughter_comp=[int(i) for i in comps[ids.index(self.daughter_id)]]
        self.INJECTED=True
        self.snap_Y=w.n["Y"].copy(); self.snap_WY=w.n["WY"].copy(); self.snap_rng=FMW.rng_hash(w)
        return True

def injected_removal(seed,law,steps=INJ_STEPS):
    """Run the REAL run_world with the injected trigger patched into its module namespace, then
    audit the intervention against the engine's declared conservation properties."""
    v=LW.LAWS[law]; t0=time.time()
    holder={}
    orig=TR.Trigger
    class _F(TR.Trigger):
        def __new__(cls,*a,**k):
            o=InjectedTrigger(force_at=0); holder["trig"]=o; return o
    TW.TR.Trigger=_F
    try:
        w,rec=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=steps)
    finally:
        TW.TR.Trigger=orig
    trig=holder["trig"]; iv=rec["intervention"]
    out={"seed":seed,"law":law,"steps":steps,"runtime_s":round(time.time()-t0,1),
         "INJECTED":bool(getattr(trig,"INJECTED",False)),
         "trigger_step":rec["t_m"],"TERMINAL_LABEL":rec["TERMINAL_LABEL"],
         "descent_level_at_trigger":rec["descent_level"],
         "descent_step_at_trigger":rec["descent_step"],
         "terminal_descent_level":rec["terminal_descent_level"],
         "terminal_descent_step":rec["terminal_descent_step"],
         "DESCENT_FIELDS_DIFFER_FROM_TERMINAL":rec["descent_step"]!=rec["terminal_descent_step"],
         "n_descent_attempts":rec["n_descent_attempts"],
         "removal_applied":bool(iv["applied"]),"removal_step":iv["step"],
         "removed_Y":iv["removed_Y"],
         "n_parent_cells":len(iv["parent_cells"] or []),
         "n_daughter_cells":len(iv["daughter_cells_before"] or []),
         "ran_to_horizon":rec["steps_executed"]==steps,"integrity_ok":rec["integrity_ok"]}
    out["AUDIT"]=removal_audit(w,rec,getattr(trig,"snap_Y",None))
    out["AUDIT_ALL_PASS"]=bool(out["AUDIT"].get("ALL_PASS",False))
    return out

def sham_is_a_no_op(seed,law,steps=200):
    """the SHAM end of the same intervention function: removing nothing must change nothing."""
    v=LW.LAWS[law]
    w,_,sp=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"])
    for t in range(steps): w._one_step(); w.tl_record(t)
    a=(FMW.phys_hash(w),FMW.rng_hash(w))
    n=FMW.intervene(w,())
    b=(FMW.phys_hash(w),FMW.rng_hash(w))
    return {"seed":seed,"law":law,"removed":n,"bit_identical":a==b}


class _OverfillWorld(TW.TLMRWorld):
    """FIXTURE ONLY, NON-SCIENTIFIC. It deliberately violates the CAP invariant at a declared step
    so that run_world's integrity guard is proved to FIRE rather than assumed to. Nothing about
    this class is ever used by a scientific world; it exists so that the one branch of the runner
    that must never be reached in science is nevertheless known to work."""
    CORRUPT_AT=None
    def _one_step(self):
        super()._one_step()
        if self.CORRUPT_AT is not None and int(self.step)>=self.CORRUPT_AT:
            self.n["Y"][0,0]=self.sp.CAP+3

def integrity_guard(seed,law,corrupt_at=40,steps=120):
    v=LW.LAWS[law]; orig=TW.TLMRWorld
    _OverfillWorld.CORRUPT_AT=int(corrupt_at)
    TW.TLMRWorld=_OverfillWorld
    try: w,rec=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=steps)
    finally: TW.TLMRWorld=orig; _OverfillWorld.CORRUPT_AT=None
    return {"seed":seed,"law":law,"corrupt_at":corrupt_at,"steps":steps,
            "stop":rec["stop"],"steps_executed":rec["steps_executed"],
            "integrity_ok":rec["integrity_ok"],
            "GUARD_FIRED":rec["stop"]=="INTEGRITY_FAILURE" and rec["integrity_ok"] is False,
            "GUARD_FIRED_AT_OR_BEFORE_THE_CORRUPTION":rec["steps_executed"]<=corrupt_at+2,
            "NO_INTERVENTION_AFTER_A_FAULT":not rec["intervention"]["applied"]}

# ------------------------------------------------------------------ 4. runtime line coverage
def executable_lines(fn):
    """the lines that can raise a 'line' event INSIDE the frame. dis.findlinestarts also reports
    the `def` line, which executes in the ENCLOSING frame and can never appear here, so it is
    removed rather than counted as a permanent miss."""
    ln={l for _,l in dis.findlinestarts(fn.__code__) if l is not None}
    return ln-{fn.__code__.co_firstlineno}

def trace(targets,f,*a,**k):
    hit={t:set() for t in targets}
    def local(frame,event,arg):
        if event=="line": hit[frame.f_code.co_filename].add(frame.f_lineno)
        return local
    def glob(frame,event,arg):
        if event=="call" and frame.f_code.co_filename in hit: return local
        return None
    sys.settrace(glob)
    try: r=f(*a,**k)
    finally: sys.settrace(None)
    return r,hit

def _composite(seed,law,steps):
    """every branch of run_world in one traced call: instrumented + trigger + selective removal,
    uninstrumented, and the integrity fault path."""
    a=injected_removal(seed,law,steps)
    b=uninstrumented_branch(seed,law,150)
    c=integrity_guard(seed,law,40,120)
    return {"injected":a,"uninstrumented":b,"integrity_guard":c}

def line_coverage(seed,law,steps=1500):
    """Which lines of the instrument actually ran. Measured, not asserted."""
    F=TW.__file__
    r,hit=trace([F],_composite,seed,law,steps)
    got=hit[F]
    rep={}
    for name in ("run_world","tl_record","build","tlmr_init"):
        obj=getattr(TW,name,None) or getattr(TW.TLMRWorld,name)
        ex=executable_lines(obj)
        miss=sorted(ex-got)
        rep[name]={"executable_body_lines":len(ex),"executed":len(ex&got),
                   "coverage":round(len(ex&got)/len(ex),4),"NOT_EXECUTED":miss,
                   "NOT_EXECUTED_SOURCE":[open(F).read().splitlines()[l-1].strip() for l in miss]}
    return {"seed":seed,"law":law,"steps":steps,"file":F,"composite_result":r,
            "DEF_LINES_EXCLUDED":"the def line executes in the enclosing frame and is not a body line",
            "PER_FUNCTION":rep,
            "FULL_BODY_COVERAGE":all(v["coverage"]==1.0 for v in rep.values())}

def uninstrumented_branch(seed,law,steps=150):
    """run_world(instrument=False) — the else branch that computes components without recording."""
    v=LW.LAWS[law]
    w,rec=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=steps,instrument=False)
    return {"seed":seed,"law":law,"steps":steps,"no_rows_written":len(w.tl_cells)==0,
            "steps_executed":rec["steps_executed"]}


# ------------------------------------------------------------------ 6. offline == online
import fmrt01_endpoint as EP
import fmrt01_identity as IDY
import tlmr01_offline as OFF
import tlmr01_run as RUN

def disc_equivalence():
    """the translated disc used by the instrument against ID.disc_mask itself, at EVERY centre of
    the lattice, on random X planes. If these ever differed the archived f5 input would be wrong."""
    rng=np.random.default_rng(20260824)
    bad=[]; n=0
    for cy in range(L):
        for cx in range(L):
            nX=rng.integers(0,17,(L,L))
            n+=1
            if TW.x_disc_mass(nX,cy,cx)!=int(nX[IDY.disc_mask(cy,cx)].sum()): bad.append((cy,cx))
    return {"centres_tested":n,"disc_cells":int(len(TW._DOY)),"mismatches":len(bad),
            "first_mismatches":bad[:5],
            "ALSO_TESTED_ON_A_ZERO_PLANE":TW.x_disc_mass(np.zeros((L,L),np.int64),0,0)==0,
            "PASS":len(bad)==0}

class _RecTrigger(TR.Trigger):
    """FIXTURE ONLY. The frozen trigger plus a shadow record of everything the offline reader will
    have to reproduce. It changes no decision: super().observe does all the work."""
    def __init__(self):
        super().__init__()
        self.log=[]; self.shadow=EP.TriggerWatcher(); self.shadow_cands=[]
    def observe(self,t,w,cells,comps,integ):
        NY=int(w.n["Y"].sum()); ncen=len(comps)
        st=EP.state_of(NY,ncen,integ)
        if self.shadow.observe(t,st): self.shadow_cands.append(t)
        cens=[CC.centroid(cells,g) for g in comps]
        lx=EP.local_x_masses(w.n["X"],cells,comps) if comps else []
        self.log.append((t,st,ncen,NY,[ (round(a,12),round(b,12)) for a,b in cens ],
                         [int(round(v)) for v in lx],
                         (EP.f5_ratio(lx) if ncen==2 else None)))
        return super().observe(t,w,cells,comps,integ)

def offline_agreement(seed,law,steps=4500):
    """Write a fixture archive through the REAL writer, then prove the offline reader reproduces
    the online record exactly. This is the gate that makes M2, M3 and M5 reconstructable."""
    v=LW.LAWS[law]; t0=time.time(); holder={}
    orig=TR.Trigger
    class _F(TR.Trigger):
        def __new__(cls,*a,**k):
            o=_RecTrigger(); holder["t"]=o; return o
    TW.TR.Trigger=_F
    try: w,rec=TW.run_world(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=steps)
    finally: TW.TR.Trigger=orig
    trig=holder["t"]
    os.makedirs("/tmp/tlmr01_fixture_raw",exist_ok=True)
    path="/tmp/tlmr01_fixture_raw/FIX_%s_%d.npz"%(law,seed)
    rec2=dict(rec); rec2.update({"tag":"FIXTURE_%s_%d"%(law,seed),"law":law,"seed":seed,
                                 "role":"FIXTURE","index":-1})
    d,lossless=RUN._narrow(w)
    d["meta"]=np.array([json.dumps(rec2,default=str)]); d["schema"]=np.array([json.dumps(RUN.SCHEMA)])
    np.savez_compressed(path,**d)
    A=OFF.Archive(path)
    # ---- state by state, centroid by centroid, local-X mass by local-X mass
    st_off=A.states()
    n_state=n_cen=n_lx=n_link=0
    bad_state=bad_cen=bad_lx=bad_link=0
    first={}
    for (t,st,ncen,NY,cens,lx,f5) in trig.log:
        if t>=A.T: continue
        n_state+=1
        if st_off[t]!=st:
            bad_state+=1; first.setdefault("state",(t,st,st_off[t]))
        cl=A.comps.get(t,[])
        if len(cl)!=ncen:
            bad_cen+=1; first.setdefault("ncomp",(t,ncen,len(cl)))
        else:
            for j,(cy,cx) in enumerate(cens):
                n_cen+=1
                if round(cl[j]["cy"],12)!=cy or round(cl[j]["cx"],12)!=cx:
                    bad_cen+=1; first.setdefault("centroid",(t,j,(cy,cx),(cl[j]["cy"],cl[j]["cx"])))
            for j,v2 in enumerate(lx):
                n_lx+=1
                if cl[j]["xd"]!=v2:
                    bad_lx+=1; first.setdefault("x_disc",(t,j,v2,cl[j]["xd"]))
        if t+1<A.T:
            n_link+=1
            if OFF.link(A.cens(t),A.cens(t+1))!=CC.link(A.cens(t),A.cens(t+1)):
                bad_link+=1; first.setdefault("link",t)
    # ---- candidates and the trigger itself
    eps=OFF.episodes(A)
    off_cands=[e["candidate_step"] for e in eps if e["MATURED"]]
    on_cands=[t for t in trig.shadow_cands if t<A.T]
    off_trig=[e["candidate_step"] for e in eps if e["MATURED"] and e["TRIGGERS"]]
    off_first=min(off_trig) if off_trig else None
    m5=OFF.M5_world_chain(A,eps)
    return {"seed":seed,"law":law,"steps":steps,"runtime_s":round(time.time()-t0,1),
      "archive_bytes":os.path.getsize(path),"narrow_dtypes_lossless":lossless,
      "steps_compared":n_state,"centroids_compared":n_cen,"x_disc_compared":n_lx,
      "links_compared":n_link,
      "STATE_MACHINE_AGREES":bad_state==0,"CENTROIDS_BIT_EQUAL":bad_cen==0,
      "LOCAL_X_DISC_EQUALS_THE_FROZEN_MASS":bad_lx==0,"IDENTITY_LINK_AGREES":bad_link==0,
      "MATURATION_CANDIDATES_AGREE":off_cands==on_cands,
      "n_candidates":len(off_cands),
      "ONLINE_t_m":rec["t_m"],"OFFLINE_first_trigger":off_first,
      "TRIGGER_STEP_AGREES":off_first==rec["t_m"],
      "TERMINAL_LABEL":rec["TERMINAL_LABEL"],
      "M5_chain":{k:m5[k] for k in ("A_maturation_reached","B_trigger_fired",
                                    "C_selective_removal_applied",
                                    "D_post_removal_functional_complete_turnover","INTEGRATED")},
      "first_disagreements":first,
      "ALL_PASS":bad_state==0 and bad_cen==0 and bad_lx==0 and bad_link==0
                 and off_cands==on_cands and off_first==rec["t_m"] and lossless}

# ------------------------------------------------------------------ 5. the suite
def _nat(job): return natural_paths(*job)
def _inj(job): return injected_removal(*job)

def main():
    U=datetime.datetime.now(datetime.timezone.utc).isoformat()
    import multiprocessing as mp
    t0=time.time()
    res={"MISSION":"TLMR01","SECTION":"5 — path coverage of the measurement instrument",
     "GENERATED_UTC":U,
     "ALL_TRAJECTORIES_HERE_ARE_NON_SCIENTIFIC":True,
     "WHY":"the first §5 run returned max_components_seen = 1 and component_increase_events = 0 on "
       "all three laws, so the fork, split, merge, trigger and selective-removal branches had "
       "never executed. 1400 steps was far too short: the median first two-centre step is 2312 at "
       "LAW_A and 609 at LAW_C, both already published in committed parent artefacts.",
     "FIXTURE_OUTCOME_FIREWALL":{
       "EMITS":["path booleans","executed code-line sets","conservation audits of one intervention"],
       "EMITS_NO":["rate","threshold","per-world scientific outcome","estimate","design input"],
       "FIXTURE_SET_IS_FIXED_IN_ADVANCE":True,"ADAPTIVE_STOPPING":False,
       "NO_TLMR01_DESIGN_ARTEFACT_READS_ANY_FIXTURE_NUMBER":True},
     "SEEDS":{"NATURAL_LAW_C":NAT_SEEDS_C,"NATURAL_LAW_A_AND_B":NAT_SEEDS_AB,
              "INJECTED":INJ_SEEDS,"BAND":"71xxx — fixture band"}}
    res["GEOMETRY_PATHS"]=geometry_paths()
    jobs=[(s,"LAW_C_MCTT01",NAT_STEPS_C) for s in NAT_SEEDS_C]
    jobs+=[(s,"LAW_A_B1",NAT_STEPS_AB) for s in NAT_SEEDS_AB]
    jobs+=[(s,"LAW_B_POINT_D10",NAT_STEPS_AB) for s in NAT_SEEDS_AB]
    ijobs=[(s,l,INJ_STEPS) for l in ("LAW_A_B1","LAW_B_POINT_D10","LAW_C_MCTT01") for s in INJ_SEEDS]
    with mp.Pool(2) as pool:
        res["NATURAL_PATHS"]=list(pool.imap(_nat,jobs))
        print("  natural done %.0fs"%(time.time()-t0),flush=True)
        res["INJECTED_REMOVAL"]=list(pool.imap(_inj,ijobs))
        print("  injected done %.0fs"%(time.time()-t0),flush=True)
    res["SHAM_NO_OP"]=[sham_is_a_no_op(INJ_SEEDS[0],l) for l in LW.LAWS]
    res["UNINSTRUMENTED_BRANCH"]=[uninstrumented_branch(INJ_SEEDS[0],l) for l in LW.LAWS]
    res["INTEGRITY_GUARD"]=[integrity_guard(INJ_SEEDS[0],l) for l in LW.LAWS]
    res["DISC_EQUIVALENCE"]=disc_equivalence()
    # The agreement set deliberately uses fixture seeds ALREADY KNOWN to reach a maturation
    # candidate, so that the t_m comparison cannot pass vacuously. FOTSEA01 shipped two
    # replacement tests that were mathematically incapable of returning a nonzero value; a gate
    # that cannot fail is not a gate, and this one is required to be non-vacuous below.
    res["OFFLINE_AGREEMENT"]=[offline_agreement(sd,l,st) for l,sd,st in
        (("LAW_A_B1",71104,6500),("LAW_B_POINT_D10",71102,6500),
         ("LAW_B_POINT_D10",71104,6500),("LAW_C_MCTT01",71001,3500),
         ("LAW_C_MCTT01",71404,4500))]
    OA=res["OFFLINE_AGREEMENT"]
    res["OFFLINE_AGREEMENT_NON_VACUITY"]={
      "worlds":len(OA),
      "total_maturation_candidates":sum(r["n_candidates"] for r in OA),
      "worlds_with_a_candidate":sum(1 for r in OA if r["n_candidates"]>0),
      "worlds_where_the_trigger_fired":sum(1 for r in OA if r["ONLINE_t_m"] is not None),
      "worlds_where_the_removal_was_applied":sum(1 for r in OA if r["M5_chain"]["C_selective_removal_applied"]),
      "worlds_with_no_candidate_at_all":sum(1 for r in OA if r["n_candidates"]==0),
      "NON_VACUOUS":(sum(r["n_candidates"] for r in OA)>0
                     and sum(1 for r in OA if r["ONLINE_t_m"] is not None)>0
                     and sum(1 for r in OA if r["M5_chain"]["C_selective_removal_applied"])>0),
      "why":"a t_m comparison over worlds that never trigger agrees trivially. The set is required "
            "to contain at least one maturation candidate, at least one fired trigger and at least "
            "one applied removal before the gate is allowed to read PASS."}
    res["LINE_COVERAGE"]=line_coverage(INJ_SEEDS[0],"LAW_C_MCTT01",1500)
    print("  coverage done %.0fs"%(time.time()-t0),flush=True)

    N=res["NATURAL_PATHS"]; I=res["INJECTED_REMOVAL"]
    by={}
    for law in LW.LAWS:
        n=[r for r in N if r["law"]==law]; i=[r for r in I if r["law"]==law]
        by[law]={
         "n_natural_trajectories":len(n),"n_injected_trajectories":len(i),
         "Y_BIRTH":any(r["y_birth_records"]>0 for r in n),
         "Y_REMOVAL":any(r["y_death_records"]>0 for r in n),
         "X_BIRTH":any(r["x_birth_records"]>0 for r in n),
         "FORK_component_count_increase":any(r["n_component_increase"]>0 for r in n),
         "TWO_COMPONENTS_HELD":any(r["steps_at_two_components"]>0 for r in n),
         "THREE_OR_MORE_COMPONENTS":any(r["steps_above_two_components"]>0 for r in n),
         "SPLIT_identity_termination":any(r["n_split_terminations"]>0 for r in n),
         "MERGE_identity_termination":any(r["n_merge_terminations"]>0 for r in n),
         "CLEAN_CONTINUATION":any(r["n_clean_continuations"]>0 for r in n),
         "FRESH_IDENTITY":any(r["n_fresh_identities"]>0 for r in n),
         "EMPTY_CENTRE_GAP":any(r["n_empty_gaps"]>0 for r in n),
         "DESCENT_RULE_EVALUATED":any(r["n_descent_attempts"]>0 for r in n+i),
         "TRIGGER_natural":any(r["natural_trigger"] for r in n),
         "TRIGGER_path_executed":any(r["natural_trigger"] for r in n) or any(r["INJECTED"] for r in i),
         "SELECTIVE_REMOVAL_path_executed":any(r["selective_removal_applied"] for r in n)
                                           or any(r["removal_applied"] for r in i),
         "SELECTIVE_REMOVAL_natural":any(r["selective_removal_applied"] for r in n),
         "N_REMOVALS_AUDITED":sum(1 for r in n if r["selective_removal_applied"])
                              +sum(1 for r in i if r["removal_applied"]),
         "SELECTIVE_REMOVAL_AUDIT_ALL_PASS":(
              all(r["AUDIT_ALL_PASS"] for r in n if r["selective_removal_applied"])
              and all(r["AUDIT_ALL_PASS"] for r in i if r["removal_applied"])
              and (any(r["selective_removal_applied"] for r in n) or any(r["removal_applied"] for r in i))),
         "INTEGRITY_GUARD_FIRES":all(r["GUARD_FIRED"] and r["NO_INTERVENTION_AFTER_A_FAULT"]
                                     for r in res["INTEGRITY_GUARD"] if r["law"]==law),
         "UNINSTRUMENTED_BRANCH_WRITES_NOTHING":all(r["no_rows_written"]
                                     for r in res["UNINSTRUMENTED_BRANCH"] if r["law"]==law),
         "OFFLINE_RECONSTRUCTION_AGREES_WITH_ONLINE":all(r["ALL_PASS"]
                                     for r in res["OFFLINE_AGREEMENT"] if r["law"]==law),
         "SHAM_IS_A_BIT_EXACT_NO_OP":all(r["bit_identical"] for r in res["SHAM_NO_OP"] if r["law"]==law),
         "ALL_RAN_TO_HORIZON":all(r["steps_executed"]==r["steps"] for r in n)
                              and all(r["ran_to_horizon"] for r in i),
         "NO_INTEGRITY_FAILURE":all(r["integrity_ok"] for r in n+i)}
    res["PER_LAW_COVERAGE"]=by
    REQUIRED=["Y_BIRTH","Y_REMOVAL","X_BIRTH","FORK_component_count_increase","TWO_COMPONENTS_HELD",
      "SPLIT_identity_termination","MERGE_identity_termination","CLEAN_CONTINUATION",
      "DESCENT_RULE_EVALUATED","TRIGGER_path_executed","SELECTIVE_REMOVAL_path_executed",
      "SELECTIVE_REMOVAL_AUDIT_ALL_PASS","SHAM_IS_A_BIT_EXACT_NO_OP","ALL_RAN_TO_HORIZON",
      "NO_INTEGRITY_FAILURE","INTEGRITY_GUARD_FIRES","UNINSTRUMENTED_BRANCH_WRITES_NOTHING",
      "FRESH_IDENTITY","OFFLINE_RECONSTRUCTION_AGREES_WITH_ONLINE"]
    REPORTED_NOT_REQUIRED=["THREE_OR_MORE_COMPONENTS","EMPTY_CENTRE_GAP","TRIGGER_natural",
      "SELECTIVE_REMOVAL_natural"]
    res["REQUIRED_PATHS"]=REQUIRED
    res["REPORTED_BUT_NOT_REQUIRED"]={"paths":REPORTED_NOT_REQUIRED,
      "why":"these depend on the law's own dynamics rather than on a code branch. A three-centre "
        "state cannot be forced at LAW_A without changing the physics, and an empty-centre gap "
        "requires extinction. They are reported wherever they occur and never used as a gate."}
    miss={law:[k for k in REQUIRED if not by[law][k]] for law in by}
    res["UNCOVERED_REQUIRED_PATHS"]=miss
    res["PATH_COVERAGE"]="PASS" if all(not v for v in miss.values()) and \
        res["GEOMETRY_PATHS"]["ALL_PASS"] and res["LINE_COVERAGE"]["FULL_BODY_COVERAGE"] \
        and res["DISC_EQUIVALENCE"]["PASS"] \
        and res["OFFLINE_AGREEMENT_NON_VACUITY"]["NON_VACUOUS"] else "FAIL"
    res["DEFECT_FOUND_BY_THIS_FIXTURE"]={
     "id":"D-DESCENT-TERMINAL-OVERWRITE",
     "what":"the inherited FMRCT01 Trigger re-evaluates and OVERWRITES descent_level, descent_step, "
       "descent_literal and descent_distances at EVERY later 1 -> 2 separation, including after it "
       "has fired, so its terminal value is the last separation in the trajectory and not the one "
       "that named the parent that was removed.",
     "evidence":"a fixture trajectory fired at step 299 and finished carrying descent_step = 1165.",
     "load_bearing":"yes — a per-world record that reported the terminal value as the descent of "
       "the removed parent would be wrong on any world with a later separation.",
     "inherited_code_changed":"NO. fmrct01_track.py is untouched.",
     "fix":"tlmr01_world.run_world snapshots AT_TRIGGER at the firing step and reports the terminal "
       "values under separate names. Neither may stand in for the other.",
     "found_before_any_scientific_world":True}
    res["RUNTIME_S"]=round(time.time()-t0,1)
    json.dump(res,open(f"{REPO}/TLMR01/out/TLMR01_PATH_COVERAGE.json","w"),indent=1)
    print("PATH_COVERAGE =",res["PATH_COVERAGE"])
    print("GEOMETRY: %d cases, all pass = %s"%(res["GEOMETRY_PATHS"]["N_CASES"],
                                               res["GEOMETRY_PATHS"]["ALL_PASS"]))
    for law in by:
        b=by[law]
        print("  %-16s fork=%s split=%s merge=%s trig_nat=%s trig_path=%s removal=%s audit=%s"%(
          law,b["FORK_component_count_increase"],b["SPLIT_identity_termination"],
          b["MERGE_identity_termination"],b["TRIGGER_natural"],b["TRIGGER_path_executed"],
          b["SELECTIVE_REMOVAL_path_executed"],b["SELECTIVE_REMOVAL_AUDIT_ALL_PASS"]))
        if miss[law]: print("      UNCOVERED:",miss[law])
    for k,v in res["LINE_COVERAGE"]["PER_FUNCTION"].items():
        print("  line coverage %-12s %d/%d = %.3f  not executed: %s"%(
          k,v["executed"],v["executable_body_lines"],v["coverage"],v["NOT_EXECUTED"]))
    print("  FULL_BODY_COVERAGE =",res["LINE_COVERAGE"]["FULL_BODY_COVERAGE"])
    print("  DISC_EQUIVALENCE:",res["DISC_EQUIVALENCE"]["centres_tested"],"centres,",
          res["DISC_EQUIVALENCE"]["mismatches"],"mismatches")
    print("  NON_VACUOUS =",res["OFFLINE_AGREEMENT_NON_VACUITY"]["NON_VACUOUS"],
          res["OFFLINE_AGREEMENT_NON_VACUITY"]["total_maturation_candidates"],"candidates,",
          res["OFFLINE_AGREEMENT_NON_VACUITY"]["worlds_where_the_removal_was_applied"],"removals")
    for r in res["OFFLINE_AGREEMENT"]:
        print("  offline %-16s all_pass=%s state=%s cen=%s xdisc=%s link=%s cands=%s t_m=%s/%s"%(
          r["law"],r["ALL_PASS"],r["STATE_MACHINE_AGREES"],r["CENTROIDS_BIT_EQUAL"],
          r["LOCAL_X_DISC_EQUALS_THE_FROZEN_MASS"],r["IDENTITY_LINK_AGREES"],
          r["MATURATION_CANDIDATES_AGREE"],r["OFFLINE_first_trigger"],r["ONLINE_t_m"]))
    print("total %.0fs"%res["RUNTIME_S"])

if __name__=="__main__": main()
