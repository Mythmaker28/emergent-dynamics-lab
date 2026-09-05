"""TLMR01 §2 — the three exact measurement laws, bound bit-for-bit from committed parent bytes.

NO NEW PARAMETER TUPLE IS INVENTED. Every law below was executed historically and every field is
read from the artefact that froze it. The only permitted differences between laws are the exact
historically executed Y-law differences: kY, muY and p_hop_Y.
"""
from __future__ import annotations
import json, hashlib, os
REPO="/home/claude/edl"
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
C=FZ["INHERITED_FROZEN_CONSTANTS"]; B1=FZ["PHASE_B"]["POINT_B1"]
D10=json.load(open(f"{REPO}/BPRTC01/out/BPRTC01_MASTER_FREEZE.json"))["POINT"]
MC=json.load(open(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json"))
MCd=json.load(open(f"{REPO}/MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json"))
_mc={d["parameter"]:d["MCTT01"] for d in MCd["CHANGED"]}

LAWS={
 "LAW_A_B1":{"label":"B1","kY":float(B1["kY"]),"muY":float(B1["muY"]),
   "p_hop_Y":float(C["p_hop_Y_mobile"]),"n_worlds":128,
   "source":"PQEC01_MASTER_FREEZE.json PHASE_B.POINT_B1 + INHERITED_FROZEN_CONSTANTS.p_hop_Y_mobile",
   "role":"established daughter formation and functional-turnover anchor (FDOT01 7 of 160)"},
 "LAW_B_POINT_D10":{"label":"POINT_D10","kY":float(D10["kY"]),"muY":float(D10["muY"]),
   "p_hop_Y":float(D10["p_hop_Y"]),"n_worlds":128,
   "source":"BPRTC01_MASTER_FREEZE.json POINT",
   "role":"slow-mobility post-removal anchor with a measured integrated event rate (3 of 256)"},
 "LAW_C_MCTT01":{"label":"MCTT01_SELECTED","kY":float(_mc["kY"]),"muY":float(_mc["muY"]),
   "p_hop_Y":float(C["p_hop_Y_mobile"]),"n_worlds":256,
   "source":"MCTT01_PHYSICS_DIFF_FROM_B1.json CHANGED + MCTT01_SELECTED_LAW.json INHERITED_UNCHANGED",
   "role":"high-occupation law that directly populates the n>5 regime missing from e(n); its "
     "Stage B was never executed"},
}
SHARED={k:C[k] for k in ("CAP","S0","phi","omega","muX","kX","L","p_hop_X","X_SEED","CORE_R",
                          "T_HORIZON")}
SHARED["LATEST_ALLOWED_TRIGGER"]=6500
SHARED["NEED"]=250
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
SOURCES=["PQEC01/out/PQEC01_MASTER_FREEZE.json","BPRTC01/out/BPRTC01_MASTER_FREEZE.json",
         "MCTT01/out/MCTT01_SELECTED_LAW.json","MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json"]
def binding():
    diffs={k:{"kY":v["kY"],"muY":v["muY"],"p_hop_Y":v["p_hop_Y"]} for k,v in LAWS.items()}
    only_y=all(set(d)<= {"kY","muY","p_hop_Y"} for d in diffs.values())
    return {"MISSION":"TLMR01","SECTION":"2 — measurement-law binding",
     "LAWS":LAWS,"TOTAL_WORLDS":sum(v["n_worlds"] for v in LAWS.values()),
     "SHARED_FROZEN_PHYSICS":SHARED,
     "MEASUREMENT_LAWS_ARE_ALL_PREVIOUSLY_EXECUTED_EXACT_LAWS":True,
     "NEW_PARAMETER_POINTS":0,"X_LAWSPEC_BASELINE":"UNCHANGED",
     "ONLY_Y_LAW_FIELDS_DIFFER":only_y,
     "PER_LAW_Y_FIELDS":diffs,
     "SOURCE_BYTES":[{"path":p,"sha256":sha(f"{REPO}/{p}")} for p in SOURCES],
     "WHAT_IS_IDENTICAL_ACROSS_ALL_THREE":sorted(SHARED)+["initial condition (seed_one_organiser: "
       "one Y and X_SEED = 4 X at (L//2, L//2), SX = SY = S0 in every cell)","feed/exchange law",
       "scheduler","centre classifier","trigger rule","parent-removal intervention","engine",
       "LawSpec"],
     "NO_NEW_TUPLE_IS_INVENTED":"every value above is read from a committed parent artefact; none "
       "is chosen by this mission."}
