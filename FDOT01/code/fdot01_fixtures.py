"""FDOT01 §5-§6 — pre-run fixtures. Non-scientific: synthetic ledgers plus one short
uninstrumented-vs-instrumented engine comparison on a seed that is NOT in any registry."""
from __future__ import annotations
import json, os, sys, hashlib, datetime
import numpy as np
REPO="/home/claude/edl"; sys.path.insert(0,f"{REPO}/FDOT01/code")
import fdot01_centres as A
import fdot01_centres_b as B
OUT=f"{REPO}/FDOT01/out"
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

def mk(steps):
    """steps: {t: [(y,x,nY), ...]} -> ycells array"""
    rows=[]
    for t in sorted(steps):
        for (y,x,n) in steps[t]: rows.append((t,y,x,n,0,0,0,0,0))
    return np.array(rows,np.int32) if rows else np.zeros((0,9),np.int32)
def ev(lst): return np.array(lst,np.int32) if lst else np.zeros((0,4),np.int32)

def run(name,steps,yb,yd,xb,H,expect):
    yc=mk(steps)
    ra=A.analyse_world(yc,ev(yb),ev(yd),ev(xb),H)
    rb=B.analyse_world(yc,ev(yb),ev(yd),ev(xb),H)
    key=lambda r: sorted((x["start"],x["end"],x["class"],x["FUNCTIONAL"]) for x in r)
    agree=key(ra)==key(rb)
    got={"n_intervals":len(ra),"classes":sorted(x["class"] for x in ra),
         "functional":sum(1 for x in ra if x["FUNCTIONAL"])}
    ok=all(got.get(k)==v for k,v in expect.items())
    return {"fixture":name,"A_vs_B_AGREE":agree,"expected":expect,"observed":got,
            "PASS":bool(agree and ok),"intervals":ra}

def main():
    F=[]; H=40
    # 1 translation — one centre drifting one cell per step keeps ONE identity interval
    F.append(run("1_translation",{t:[(10,10+t,1)] for t in range(H)},[],[],
                 [(t,10,10+t,1) for t in range(H)],H,{"n_intervals":1,"classes":["NO_TURNOVER"]}))
    # 2 crossing — two centres passing each other come within CORE_R and the ambiguity must
    #   terminate both identities rather than be bridged
    st={}
    for t in range(H):
        st[t]=[(10,4+t,1),(10,30-t,1)]
    F.append(run("2_crossing",st,[],[],[],H,{}))
    F[-1]["NOTE"]=("two centres approach, merge into ONE component while within CORE_R, then "
                   "separate. The run must show more than one identity interval, i.e. the crossing "
                   "is NOT silently bridged.")
    F[-1]["PASS"]=bool(F[-1]["A_vs_B_AGREE"] and F[-1]["observed"]["n_intervals"]>2)
    # 3 equal-distance tie — one centre with two equidistant successors
    st={0:[(10,10,1)],1:[(10,7,1),(10,13,1)]}
    F.append(run("3_equal_distance_tie",st,[],[],[],3,{"n_intervals":3}))
    F[-1]["NOTE"]="a tie leaves two candidates, so no link is clean and three intervals result"
    # 4 split — a GENUINE asymmetric split: the two children are 6 apart, so they are two
    #   components, and both sit within CORE_R of the parent centroid at unequal distances.
    #   The first draft of this fixture put the children 4 apart, which is inside CORE_R and
    #   therefore still ONE component: it tested nothing. Corrected here, before any world ran.
    st={0:[(10,10,2)],1:[(10,8,1),(10,14,1)]}
    F.append(run("4_split",st,[],[],[],3,{"n_intervals":3}))
    F[-1]["NOTE"]=("children 6 apart => two components; both within CORE_R of the parent centroid "
      "at distances 2 and 4 => the parent has two candidates => the identity terminates and is not "
      "resolved by preferring the nearer child")
    # 5 merge
    st={0:[(10,8,1),(10,14,1)],1:[(10,11,2)]}
    F.append(run("5_merge",st,[],[],[],3,{"n_intervals":3}))
    F[-1]["NOTE"]="the child has two candidates within CORE_R, so the identity terminates"
    # 6 birth inside centre
    st={t:[(10,10,1 if t<5 else 2)] for t in range(10)}
    F.append(run("6_birth_inside_centre",st,[(5,10,10,1)],[],[],10,
                 {"n_intervals":1,"classes":["PARTIAL_BIRTH_ONLY"]}))
    # 7 death inside centre
    st={t:[(10,10,2 if t<5 else 1)] for t in range(10)}
    F.append(run("7_death_inside_centre",st,[],[(5,10,10,1)],[],10,
                 {"n_intervals":1,"classes":["PARTIAL_DEATH_ONLY"]}))
    # 8 birth then death, with X production on both sides -> FUNCTIONAL
    st={t:[(10,10,1 if t<3 else (2 if t<7 else 1))] for t in range(12)}
    F.append(run("8_birth_then_death_functional",st,[(3,10,10,1)],[(7,10,10,1)],
                 [(t,10,10,1) for t in range(12)],12,
                 {"n_intervals":1,"classes":["COMPLETE_BIRTH_THEN_DEATH"],"functional":1}))
    # 8b same event but NO X production after the removal -> NOT functional
    F.append(run("8b_birth_then_death_no_post_X",st,[(3,10,10,1)],[(7,10,10,1)],
                 [(t,10,10,1) for t in range(7)],12,
                 {"n_intervals":1,"classes":["COMPLETE_BIRTH_THEN_DEATH"],"functional":0}))
    # 9 death then birth with N_Y >= 2 throughout
    st={t:[(10,10,2 if t<4 else (1 if t<8 else 2))] for t in range(12)}
    F.append(run("9_death_then_birth_NY_ge_2",st,[(8,10,10,1)],[(4,10,10,1)],
                 [(t,10,10,1) for t in range(12)],12,
                 {"n_intervals":1,"classes":["COMPLETE_DEATH_THEN_BIRTH"],"functional":1}))
    # 10 single-Y death causing extinction — the component disappears, so no COMPLETE is possible
    st={t:[(10,10,1)] for t in range(5)}
    F.append(run("10_single_Y_death_extinction",st,[],[(4,10,10,1)],
                 [(t,10,10,1) for t in range(5)],12,
                 {"n_intervals":1,"classes":["PARTIAL_DEATH_ONLY"],"functional":0}))
    F[-1]["NOTE"]=("the theorem of DOTC01 §4 as a deterministic fixture: a one-constituent centre "
      "that loses its constituent leaves the component empty, the interval ends, and no "
      "COMPLETE_DEATH_THEN_BIRTH can follow. Observed class is PARTIAL_DEATH_ONLY.")
    # 11 a later birth after extinction must NOT be joined to the dead interval
    st={t:[(10,10,1)] for t in range(5)}
    st.update({t:[(10,10,1)] for t in range(9,14)})
    F.append(run("11_no_bridging_across_an_empty_gap",st,[(10,10,10,1)],[(4,10,10,1)],
                 [(t,10,10,1) for t in list(range(5))+list(range(9,14))],14,
                 {"n_intervals":2}))
    F[-1]["NOTE"]=("after the component is empty for four steps a new interval must start; "
      "bridging would manufacture a false COMPLETE_DEATH_THEN_BIRTH")
    F[-1]["PASS"]=bool(F[-1]["A_vs_B_AGREE"] and F[-1]["observed"]["n_intervals"]==2
                       and not any(x["class"].startswith("COMPLETE") for x in F[-1]["intervals"]))
    # 12 OBSERVER INERTNESS — bit-exact instrumented vs uninstrumented, on a fixture seed
    #    (1) that is deliberately outside every scientific registry.
    import fdot01_world as W, pqec01_observer as O, engine_obtc as EN
    FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json")); B1=FZ["PHASE_B"]["POINT_B1"]
    def phash(w):
        h=hashlib.sha256()
        for s_ in O.SPECIES: h.update(np.ascontiguousarray(w.n[s_]).tobytes())
        return h.hexdigest()
    wi,_,_=W.build(1,B1["kY"],B1["muY"],600)
    wu,_,spu=O.build_world(1,B1["kY"],B1["muY"],L=None,horizon=600,instrumented=False)
    for _ in range(600): wi._one_step()
    for _ in range(600): wu._one_step()
    inert=(phash(wi)==phash(wu))
    F.append({"fixture":"12_observer_inertness","A_vs_B_AGREE":True,
      "expected":{"identical_state_after_600_steps":True},
      "observed":{"instrumented_hash":phash(wi)[:16],"uninstrumented_hash":phash(wu)[:16],
                  "identical_state_after_600_steps":inert},
      "PASS":bool(inert),"intervals":[],
      "NOTE":("the FDOT01 X-birth ledger is pure observation. Fixture seed 1 is outside every "
              "scientific registry and its output is discarded.")})
    res={"SECTION":"FDOT01 §5-§6 — pre-run fixtures","GENERATED_UTC":NOW(),
      "TWO_INDEPENDENT_IMPLEMENTATIONS":["fdot01_centres.py (union-find)","fdot01_centres_b.py (scipy csgraph)"],
      "N_FIXTURES":len(F),"N_PASS":sum(1 for f in F if f["PASS"]),
      "ALL_PASS":all(f["PASS"] for f in F),
      "A_AND_B_AGREE_ON_EVERY_FIXTURE":all(f["A_vs_B_AGREE"] for f in F),
      "FIXTURES":[{k:v for k,v in f.items() if k!="intervals"} for f in F]}
    json.dump(res,open(f"{OUT}/FDOT01_FIXTURES.json","w"),indent=1)
    for f in F: print("  [%s] %-34s A==B:%s  %s"%("PASS" if f["PASS"] else "FAIL",f["fixture"],f["A_vs_B_AGREE"],f["observed"]))
    print("ALL_PASS:",res["ALL_PASS"],"| A==B everywhere:",res["A_AND_B_AGREE_ON_EVERY_FIXTURE"])

if __name__=="__main__": main()
