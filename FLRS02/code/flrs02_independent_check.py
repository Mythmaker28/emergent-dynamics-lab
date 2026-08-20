"""FLRS02 §14 — exact agreement test between the two independent checkers."""
import json, datetime
A={r["world"]:r for r in json.load(open("out/_checkerA.json"))}
B={r["world"]:r for r in json.load(open("out/_checkerB.json"))}
KEYS=("T_50","T_primary","T_80","T_90")
REQUIRED=["first_S","first_P","n_S_episodes","max_S_duration","extinct","n_births","integrity_ok"]
for k in KEYS:
    REQUIRED += [f"dur_ok_{k}",f"noP_ok_{k}",f"resp_ok_{k}",f"event_step_{k}",
                 f"P_before_event_{k}",f"joint_timing_{k}",f"joint_{k}"]
diffs=[]
assert set(A)==set(B), "world sets differ"
for w in sorted(A):
    for f in REQUIRED:
        a,b=A[w].get(f),B[w].get(f)
        if a!=b: diffs.append({"world":w,"field":f,"A":a,"B":b})
# ratios compared with a tolerance and reported separately (floating aggregation order differs)
rat=[]
for w in sorted(A):
    for k in KEYS:
        a=A[w].get(f"weak_centre_X_ratio_{k}"); b=B[w].get(f"weak_centre_X_ratio_{k}")
        if (a is None)!=(b is None): rat.append({"world":w,"key":k,"A":a,"B":b,"kind":"presence"})
        elif a is not None and abs(a-b)>1e-12: rat.append({"world":w,"key":k,"A":a,"B":b,"kind":"value"})
agree = (len(diffs)==0)
J={"SECTION":"FLRS02 §14 — two independent zero-run calculators",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "SHARED":"raw archives, frozen protocol constants, the six-state definition and the seven success conditions",
 "NOT_SHARED":{"state_sequence":"A python loop / B vectorised np.select",
   "episode_extraction":"A running-index loop / B np.diff on a boolean mask",
   "connected_components":"A union-find / B BFS queue",
   "toroidal_centroid":"A anchored offsets / B complex circular mean",
   "X_plane_reconstruction":"A single cumsum / B direct partial sum per event",
   "local_X_aggregation":"A boolean disc mask / B precomputed toroidal distance table"},
 "N_WORLDS":len(A),
 "FIELDS_REQUIRING_EXACT_AGREEMENT":REQUIRED,
 "N_DISAGREEMENTS":len(diffs),"DISAGREEMENTS":diffs[:50],
 "RATIO_COMPARISON":{"n_mismatch_beyond_1e_12":len(rat),"detail":rat[:20],
   "note":"the weak-centre X ratio is a floating aggregation and is compared with tolerance, not required bit-exact"},
 "EXACT_AGREEMENT":bool(agree),
 "VERDICT":"INDEPENDENT_REANALYSES_AGREE" if agree else "INDEPENDENT_REANALYSES_DISAGREE"}
json.dump(J,open("out/FLRS02_INDEPENDENT_CHECK.json","w"),indent=2)
print("EXACT_AGREEMENT:",agree,"| disagreements:",len(diffs),"| ratio mismatches:",len(rat))
for d in rat[:8]: print("  ",d)
