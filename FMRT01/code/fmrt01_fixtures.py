"""FMRT01 — fixtures. Synthetic states and the declared non-scientific fixture seed band."""
from __future__ import annotations
import json,sys
import numpy as np
REPO="/home/claude/edl"
for _p in (f"{REPO}/FMRT01/code",f"{REPO}/PQEC01/code","/home/claude/ORR01/code","/home/claude/OBTC02/code"):
    if _p not in sys.path: sys.path.insert(0,_p)
import pqec01_observer as O
import fmrt01_engine as FE
O.PQECWorld=FE.FMRTWorld
import fmrt01_identity as ID
F=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
B1=F["PHASE_B"]["POINT_B1"]; CAP=F["INHERITED_FROZEN_CONSTANTS"]["CAP"]
def fresh(seed=77000001):
    w,_,sp=O.build_world(seed,B1["kY"],B1["muY"],L=None,horizon=10,instrumented=True)
    w.fmrt_init(); return w,sp
def snap(w): return {s:w.n[s].copy() for s in O.SPECIES}
def case(name,setup,maskfn):
    w,sp=fresh(); setup(w); before=snap(w); fp=FE.rng_fingerprint(w)
    occ0=sum(before[s] for s in O.SPECIES); m=maskfn(w); n=w.selective_y_off(m)
    after=snap(w); occ1=sum(after[s] for s in O.SPECIES)
    c={"only_masked_Y_removed":bool(np.array_equal(after["Y"][~m],before["Y"][~m])),
       "masked_Y_fully_removed":bool((after["Y"][m]==0).all()),
       "Y_to_WY_exact":bool(np.array_equal(after["WY"]-before["WY"],np.where(m,before["Y"],0))),
       "X_unchanged":bool(np.array_equal(after["X"],before["X"])),
       "SX_unchanged":bool(np.array_equal(after["SX"],before["SX"])),
       "SY_unchanged":bool(np.array_equal(after["SY"],before["SY"])),
       "WX_unchanged":bool(np.array_equal(after["WX"],before["WX"])),
       "occupancy_conserved_cellwise":bool(np.array_equal(occ0,occ1)),
       "capacity_invariant":bool((occ1<=CAP).all()),
       "no_RNG_consumed":bool(FE.rng_fingerprint(w)==fp),"n_removed":int(n)}
    c["PASS"]=all(v for v in c.values() if isinstance(v,bool))
    return {"case":name,**c}
def put(w,cells,sp="Y",n=1):
    for (y,x) in cells: w.n[sp][y,x]+=n
def two_sep(w):
    w.n["Y"][:]=0; put(w,[(18,18)]); put(w,[(18,30)])
R=[]
R.append(case("one_Y",lambda w:None,lambda w:(w.n["Y"]>0)))
R.append(case("two_colocated",lambda w:put(w,[(18,18)]),lambda w:(w.n["Y"]>0)))
R.append(case("two_separated_remove_parent",two_sep,lambda w:ID.mask_for([(18,18),(18,30)],[0])))
R.append(case("two_separated_remove_daughter",two_sep,lambda w:ID.mask_for([(18,18),(18,30)],[1])))
R.append(case("multi_Y_in_parent",lambda w:(two_sep(w),put(w,[(19,18),(18,19)])),
              lambda w:ID.mask_for([(18,18),(19,18),(18,19),(18,30)],[0,1,2])))
def sat(w):
    w.n["Y"][:]=0; w.n["Y"][18,18]=1
    room=CAP-sum(int(w.n[s][18,18]) for s in O.SPECIES); w.n["SY"][18,18]+=max(room,0)
R.append(case("capacity_saturation",sat,lambda w:(w.n["Y"]>0)))
R.append(case("sham_empty_mask_is_a_no_op",two_sep,lambda w:np.zeros_like(w.n["Y"],bool)))
R.append(case("global_all_true_mask",two_sep,lambda w:np.ones_like(w.n["Y"],bool)))
# --- GLOBAL-OFF EQUIVALENCE: all-true mask vs the historical three lines ---
wa,_=fresh(77000003); two_sep(wa); wa.selective_y_off(np.ones_like(wa.n["Y"],bool))
wb,_=fresh(77000003); two_sep(wb)
y=wb.n["Y"].copy(); wb.n["Y"]=wb.n["Y"]-y; wb.n["WY"]=wb.n["WY"]+y      # engine_obtc.py:226-228
EQ={"case":"global_off_equivalence_to_the_historical_three_lines",
 "states_identical":bool(all(np.array_equal(wa.n[s],wb.n[s]) for s in O.SPECIES)),
 "source":"OBTC02/code/engine_obtc.py lines 226-228, quoted verbatim in the comparison"}
EQ["PASS"]=EQ["states_identical"]; R.append(EQ)
# --- mask symmetry ---
w1,_=fresh(); two_sep(w1); w1.selective_y_off(ID.mask_for([(18,18),(18,30)],[0]))
w2,_=fresh(); two_sep(w2); w2.selective_y_off(ID.mask_for([(18,18),(18,30)],[1]))
w3,_=fresh(); two_sep(w3); w3.selective_y_off(ID.mask_for([(18,18),(18,30)],[0]))
SY={"case":"mask_symmetry","same_mask_same_state":bool(np.array_equal(w1.n["Y"],w3.n["Y"])),
    "different_mask_different_state":bool(not np.array_equal(w1.n["Y"],w2.n["Y"])),
    "each_leaves_one_centre":bool(int(w1.n["Y"].sum())==1 and int(w2.n["Y"].sum())==1)}
SY["PASS"]=all(v for v in SY.values() if isinstance(v,bool)); R.append(SY)
# --- identity tie ---
p,d,l=ID.parent_daughter([(20,33),(23,32)],[(19,33),(24,32)])
TIE={"case":"identity_tie_RCD01_geometry","level_used":l,"resolved":bool(p is not None),
     "PASS":bool(p is not None and l==4)}
R.append(TIE)
J={"SECTION":"FMRT01 — intervention and identity fixtures","N":len(R),
   "ALL_PASS":all(x["PASS"] for x in R),
   "FIXTURE_SEEDS":"77000001 and 77000003, the declared non-scientific fixture band","CASES":R}
json.dump(J,open(f"{REPO}/FMRT01/out/FMRT01_INTERVENTION_FIXTURES.json","w"),indent=2)
for x in R: print("[%s] %s"%("PASS" if x["PASS"] else "FAIL",x["case"]))
print("ALL_PASS:",J["ALL_PASS"])
