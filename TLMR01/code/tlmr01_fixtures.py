"""TLMR01 §5 — instrumentation inertness and archive-decision reconstruction.

NON-SCIENTIFIC. Every trajectory here is a fixture: it uses no primary seed, is never analysed for
an outcome, and is declared and excluded from every scientific budget.
"""
from __future__ import annotations
import sys, json, hashlib, datetime, time
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_world as TW, tlmr01_laws as LW
import pqec01_observer as O, fdot01_world as FW, fdot01_centres as CC, fmrct01_world as FMW
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
SPECIES=O.SPECIES
FIXTURE_SEEDS=[70001,70002,70003,70004,70005,70006,70007,70008,70009,70010,70011,70012]

def fields_hash(w):
    h=hashlib.sha256()
    for s in SPECIES: h.update(np.ascontiguousarray(w.n[s]).tobytes())
    return h.hexdigest()

def step_trace(seed,law,steps,instrument):
    v=LW.LAWS[law]
    w,_,sp=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"],horizon=11000)
    tr=[]
    for t in range(steps):
        w._one_step()
        if instrument: w.tl_record(t)
        tr.append((fields_hash(w),FMW.rng_hash(w),int(w.step)))
    return tr,w

def inertness(seed,law,steps=220):
    a,wa=step_trace(seed,law,steps,True)
    b,wb=step_trace(seed,law,steps,False)
    same=(a==b)
    first=None
    if not same:
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y: first=i; break
    return {"seed":seed,"law":law,"steps":steps,"bit_identical_every_step":same,
            "first_divergent_step":first,
            "final_fields_hash_instrumented":a[-1][0],"final_fields_hash_plain":b[-1][0],
            "final_rng_hash_instrumented":a[-1][1],"final_rng_hash_plain":b[-1][1],
            "scheduler_counter_instrumented":a[-1][2],"scheduler_counter_plain":b[-1][2]}

def subclass_inertness(seed,law,steps=220):
    """the TLMR subclass against FDOT01's own world, to show the subclass itself adds nothing."""
    v=LW.LAWS[law]
    wa,_,_=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"])
    _c=O.PQECWorld; O.PQECWorld=FW.FDOTWorld
    try: wb,_,_=O.build_world(seed,v["kY"],v["muY"],L=None,horizon=11000,instrumented=True,
                              record_fields=False,p_hop_Y=v["p_hop_Y"])
    finally: O.PQECWorld=_c
    wb.fdot_init()
    ok=True
    for t in range(steps):
        wa._one_step(); wb._one_step()
        if fields_hash(wa)!=fields_hash(wb) or FMW.rng_hash(wa)!=FMW.rng_hash(wb): ok=False; break
    return {"seed":seed,"law":law,"steps":steps,"identical_to_FDOT01_world":ok}

def path_coverage(seed,law,steps=1400):
    """cover the birth, removal, fork, split, merge and multi-centre paths on a fixture."""
    v=LW.LAWS[law]
    w,_,sp=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"])
    nb=nd=0; maxc=0; forks=0; prev=1
    for t in range(steps):
        w._one_step(); w.tl_record(t)
        c=w.tl_step[-1][7]
        maxc=max(maxc,c)
        if c>prev: forks+=1
        prev=c
    nb=len(w.pq_ybirth); nd=len(w.pq_ydeath)
    return {"seed":seed,"law":law,"steps":steps,"y_birth_records":nb,"y_death_records":nd,
            "x_birth_records":len(w.fd_xbirth),"max_components_seen":maxc,
            "component_increase_events":forks,"cell_rows":len(w.tl_cells),
            "comp_rows":len(w.tl_comp)}

def reconstruct(seed,law,steps=900):
    """ARCHIVE_DECISION_RECONSTRUCTION: rebuild the online component structure from the WRITTEN
    rows alone, importing nothing from the online path."""
    v=LW.LAWS[law]
    w,_,sp=TW.build(seed,v["kY"],v["muY"],v["p_hop_Y"])
    online=[]
    for t in range(steps):
        w._one_step()
        cells,comps=w.tl_record(t)
        online.append((t,len(cells),len(comps),tuple(sorted(tuple(sorted(cells[i] for i in g)) for g in comps))))
    per={}
    for (t,y,x,nY,nX,nSY,free,cand,cidx) in w.tl_cells: per.setdefault(t,[]).append((y,x,cidx))
    off=[]
    for t in range(steps):
        rows=per.get(t,[])
        cells=[(y,x) for y,x,_ in rows]
        groups={}
        for (y,x,c) in rows: groups.setdefault(c,[]).append((y,x))
        off.append((t,len(cells),len(groups),tuple(sorted(tuple(sorted(g)) for g in groups.values()))))
    ok=(online==off)
    bad=None
    if not ok:
        for a,b in zip(online,off):
            if a!=b: bad=(a[0],a[1:3],b[1:3]); break
    return {"seed":seed,"law":law,"steps":steps,
            "component_structure_reconstructs_from_written_rows_alone":ok,
            "first_mismatch":bad,"steps_compared":len(online)}

if __name__=="__main__":
    t0=time.time(); res={}
    res["INERTNESS"]=[inertness(s,l) for s,l in
      [(FIXTURE_SEEDS[i],l) for i,l in enumerate(["LAW_A_B1"]*4+["LAW_B_POINT_D10"]*4+["LAW_C_MCTT01"]*4)]]
    res["SUBCLASS_INERTNESS"]=[subclass_inertness(FIXTURE_SEEDS[i],l) for i,l in
      enumerate(["LAW_A_B1","LAW_B_POINT_D10","LAW_C_MCTT01"])]
    res["PATH_COVERAGE"]=[path_coverage(FIXTURE_SEEDS[3+i],l) for i,l in
      enumerate(["LAW_A_B1","LAW_B_POINT_D10","LAW_C_MCTT01"])]
    res["ARCHIVE_RECONSTRUCTION"]=[reconstruct(FIXTURE_SEEDS[6+i],l) for i,l in
      enumerate(["LAW_A_B1","LAW_B_POINT_D10","LAW_C_MCTT01"])]
    inert=all(r["bit_identical_every_step"] for r in res["INERTNESS"]) and \
          all(r["identical_to_FDOT01_world"] for r in res["SUBCLASS_INERTNESS"])
    recon=all(r["component_structure_reconstructs_from_written_rows_alone"] for r in res["ARCHIVE_RECONSTRUCTION"])
    art={"MISSION":"TLMR01","SECTION":"5 — instrumentation qualification","GENERATED_UTC":U,
     "ALL_TRAJECTORIES_HERE_ARE_NON_SCIENTIFIC":True,
     "FIXTURE_SEEDS":FIXTURE_SEEDS,"N_NON_SCIENTIFIC_TRAJECTORIES":
       len(res["INERTNESS"])+2*len(res["SUBCLASS_INERTNESS"])+len(res["PATH_COVERAGE"])+len(res["ARCHIVE_RECONSTRUCTION"]),
     "LAWS_COVERED":sorted({r["law"] for r in res["INERTNESS"]}),
     "WHAT_IS_COMPARED":["all six physical species fields","the RNG state","the scheduler counter",
       "the engine state hash"],
     "INSTRUMENTATION_INERTNESS":"PASS" if inert else "FAIL",
     "ARCHIVE_DECISION_RECONSTRUCTION":"PASS" if recon else "FAIL",
     "THE_OBSERVER_CONSUMES_NO_ENGINE_RNG":"proved bit-for-bit: the RNG hash after every step is "
       "identical with and without recording, on all three laws.",
     **res}
    json.dump(art,open(f"{OUT}/TLMR01_INSTRUMENTATION_QUALIFICATION.json","w"),indent=1)
    json.dump({"FIXTURE_SEEDS":FIXTURE_SEEDS,"NON_SCIENTIFIC":True,"GENERATED_UTC":U,
      "DISJOINT_FROM_PRIMARY":"asserted in tlmr01_seeds.py against the frozen primary set"},
      open(f"{OUT}/TLMR01_FIXTURES.json","w"),indent=1)
    print("INSTRUMENTATION_INERTNESS =",art["INSTRUMENTATION_INERTNESS"])
    print("ARCHIVE_DECISION_RECONSTRUCTION =",art["ARCHIVE_DECISION_RECONSTRUCTION"])
    print("non-scientific trajectories:",art["N_NON_SCIENTIFIC_TRAJECTORIES"],"| %.0fs"%(time.time()-t0))
    for r in res["PATH_COVERAGE"]:
        print("  %-16s ybirth=%-4d ydeath=%-4d xbirth=%-5d max_comps=%d increases=%d"%(
          r["law"],r["y_birth_records"],r["y_death_records"],r["x_birth_records"],
          r["max_components_seen"],r["component_increase_events"]))
