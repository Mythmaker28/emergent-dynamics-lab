"""FDFLT01 pre-run gates. Both must PASS before the first fresh world exists.

GATE 1 — EQUIVALENCE. The frozen endpoint module must reproduce the FLRS02 developmental
         result on the historical PQEC01 B1 archives EXACTLY. This proves the scientific rule
         was not altered when the raw directory was parameterised.
GATE 2 — PERSISTENT CENTRE IDENTITY on synthetic cases, with no engine RNG consumed.
"""
from __future__ import annotations
import glob, json, math, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fdflt01_endpoint as E

REPO="/home/claude/edl"; PQ="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FDFLT01/out"

def gate_equivalence():
    rows=[E.score_world(p) for p in sorted(glob.glob(f"{PQ}/B_B1_*.npz"))]
    got={k:sum(r[f"PRIMARY_SUCCESS_{k}"] for r in rows) for k in E.STEPS}
    got_timing={k:sum(r[f"joint_timing_{k}"] for r in rows) for k in E.STEPS}
    F=json.load(open(f"{REPO}/FLRS02/out/FLRS02_B1_DIRECT_ATLAS.json"))["ATLAS"]["RATES"]
    exp={k:F[f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]["count"] for k in E.STEPS}
    exp_timing={k:F[f"P_FUNCTIONAL_MATURATION_{k}"]["count"] for k in E.STEPS}
    ok = (got==exp) and (got_timing==exp_timing) and len(rows)==44
    # per-world identity of the primary flag against the FLRS02 checker A record
    A={r["world"]:r for r in json.load(open(f"{REPO}/FLRS02/out/_checkerA.json"))}
    mism=[w for w in (r["world"] for r in rows)
          if A[w][f"joint_{E.PRIMARY_KEY}"] != next(r for r in rows if r["world"]==w)[f"PRIMARY_SUCCESS_{E.PRIMARY_KEY}"]]
    return {"GATE":"EQUIVALENCE_WITH_FLRS02_ON_HISTORICAL_B1","n_worlds":len(rows),
            "expected_success_counts":exp,"reproduced_success_counts":got,
            "expected_timing_counts":exp_timing,"reproduced_timing_counts":got_timing,
            "per_world_mismatches":mism,"PASS":bool(ok and not mism)}

def gate_identity():
    C=[]
    def case(name,cells_prev,cells_cur,expect_new):
        p=E.components(cells_prev); c=E.components(cells_cur)
        mp=E.match_persistent(p,c,cells_prev,cells_cur)
        new=[j for j,v in mp.items() if v is None]
        C.append({"case":name,"n_prev":len(p),"n_cur":len(c),"unmatched_current":len(new),
                  "expected_unmatched":expect_new,"map":{str(k):v for k,v in mp.items()},
                  "PASS":len(new)==expect_new})
    case("stationary_two_centres",[(5,5),(20,20)],[(5,5),(20,20)],0)
    case("crossing_centres",[(5,5),(20,20)],[(6,6),(19,19)],0)
    case("centre_translation",[(5,5),(20,20)],[(7,7),(22,22)],0)
    case("temporary_equal_distance_tie",[(0,0),(18,18)],[(1,1),(17,17)],0)
    case("merge",[(5,5),(20,20)],[(12,12),(13,13)],0)          # two -> one, one current comp
    case("split",[(12,12),(13,13)],[(5,5),(20,20)],1)          # one -> two, one is new
    case("third_centre_appears",[(5,5),(20,20)],[(5,5),(20,20),(30,30)],1)
    # inertness: the tracker must consume no engine RNG
    rng=np.random.default_rng(12345); before=rng.bit_generator.state
    E.match_persistent(E.components([(5,5),(20,20)]),E.components([(5,5),(20,20)]),
                       [(5,5),(20,20)],[(5,5),(20,20)])
    inert = (rng.bit_generator.state == before)
    return {"GATE":"PERSISTENT_CENTRE_IDENTITY","cases":C,
            "NO_ENGINE_RNG_CONSUMED":bool(inert),
            "PASS":bool(all(c["PASS"] for c in C) and inert)}

if __name__=="__main__":
    g1=gate_equivalence(); g2=gate_identity()
    R={"FDFLT01_PRE_RUN_GATES":[g1,g2],"ALL_PASS":bool(g1["PASS"] and g2["PASS"])}
    json.dump(R,open(f"{OUT}/FDFLT01_PRE_RUN_GATES.json","w"),indent=2)
    print(json.dumps({"EQUIVALENCE":{k:g1[k] for k in ("expected_success_counts","reproduced_success_counts","expected_timing_counts","reproduced_timing_counts","per_world_mismatches","PASS")},
                      "IDENTITY":{"cases":[(c["case"],c["PASS"]) for c in g2["cases"]],
                                  "inert":g2["NO_ENGINE_RNG_CONSUMED"],"PASS":g2["PASS"]},
                      "ALL_PASS":R["ALL_PASS"]},indent=2))
