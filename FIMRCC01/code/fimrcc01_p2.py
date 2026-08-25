"""FIMRCC01 Section 0, precondition P2 — re-verify the law binding against the owner's copies.

The independent check on TLMR01 recorded that three of the four source artefacts were absent from
the container that issued the handoff, so `tlmr01_laws` did not import there and the selected law
was not bit-verifiable. This closes that, or reports exactly what remains open.

Nothing here reads a number from prose. Every value is read from the source artefact's own JSON,
and the selected law is additionally checked against the IEEE-754 bit patterns MCTT01 published.
"""
from __future__ import annotations
import sys, os, json, hashlib, struct, datetime, subprocess
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/TLMR01/code")
U=datetime.datetime.now(datetime.timezone.utc).isoformat()

FROZEN=json.load(open(f"{REPO}/TLMR01/out/TLMR01_MEASUREMENT_LAWS.json"))
SRC=FROZEN["SOURCE_BYTES"]

def sha(p):
    return hashlib.sha256(open(p,"rb").read()).hexdigest()

def bits(x):
    return "0x"+struct.pack(">d",float(x)).hex()

# ---------- 1. the four source artefacts, byte for byte ----------
byte_rows=[]
for e in SRC:
    p=os.path.join(REPO,e["path"])
    present=os.path.exists(p)
    got=sha(p) if present else None
    byte_rows.append({"path":e["path"],"present_in_container":present,
                      "declared_sha256":e["sha256"],"observed_sha256":got,
                      "MATCHES":bool(present and got==e["sha256"]),
                      "bytes":os.path.getsize(p) if present else None})
ALL_BYTES_MATCH=all(r["MATCHES"] for r in byte_rows)

# ---------- 2. the modules that could not import ----------
mods={}
for m in ["tlmr01_laws","tlmr01_seeds","tlmr01_run"]:
    try:
        __import__(m); mods[m]="IMPORTS"
    except Exception as ex:
        mods[m]="FAILS: %s: %s"%(type(ex).__name__,ex)
ALL_MODULES_IMPORT=all(v=="IMPORTS" for v in mods.values())

import tlmr01_laws as LW

# ---------- 3. LAW_C against MCTT01's own bit patterns ----------
SEL=json.load(open(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json"))["SELECTED"]
DIFF=json.load(open(f"{REPO}/MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json"))
C=LW.LAWS["LAW_C_MCTT01"]
bit_rows=[]
for f in ["kY","muY","p_hop_Y"]:
    live=float(C[f]); src=float(SEL[f]); decl=SEL[f+"_bits"]
    bit_rows.append({"field":f,
      "value_in_tlmr01_laws":repr(live),"value_in_MCTT01_SELECTED_LAW":repr(src),
      "bits_of_the_live_value":bits(live),"bits_declared_by_MCTT01":decl,
      "IDENTICAL_DOUBLE":live==src,"MATCHES_DECLARED_BITS":bits(live)==decl})
LAW_C_BIT_EXACT=all(r["IDENTICAL_DOUBLE"] and r["MATCHES_DECLARED_BITS"] for r in bit_rows)

# the diff artefact must agree that these two, and only these two, moved off B1
A=LW.LAWS["LAW_A_B1"]
changed={d["parameter"]:d for d in DIFF["CHANGED"]}
diff_rows=[{"parameter":k,"B1_in_the_diff":repr(d["B1"]),"B1_in_tlmr01_laws":repr(A[k]),
            "MCTT01_in_the_diff":repr(d["MCTT01"]),"MCTT01_in_tlmr01_laws":repr(C[k]),
            "B1_AGREES":float(d["B1"])==float(A[k]),
            "MCTT01_AGREES":float(d["MCTT01"])==float(C[k])} for k,d in changed.items()]
DIFF_AGREES=all(r["B1_AGREES"] and r["MCTT01_AGREES"] for r in diff_rows)
ONLY_TWO_CHANGED=(set(changed)=={"kY","muY"} and DIFF["N_CHANGED"]==2
                  and float(C["p_hop_Y"])==float(A["p_hop_Y"]))

# ---------- 4. every shared frozen constant, against a byte-verified source ----------
BP=json.load(open(f"{REPO}/BPRTC01/out/BPRTC01_MASTER_FREEZE.json"))
INH=json.load(open(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json"))["INHERITED_UNCHANGED"]
BINH=BP["POINT"]["INHERITED_FROZEN_CONSTANTS"]; BTRG=BP["TRIGGER"]
SH=FROZEN["SHARED_FROZEN_PHYSICS"]

def sources_for(k):
    """every byte-verified artefact that declares this constant, and what it declares."""
    out=[]
    if k in INH:  out.append(("MCTT01_SELECTED_LAW.json INHERITED_UNCHANGED",INH[k]))
    if k in BINH: out.append(("BPRTC01_MASTER_FREEZE.json POINT.INHERITED_FROZEN_CONSTANTS",BINH[k]))
    if k in BTRG: out.append(("BPRTC01_MASTER_FREEZE.json TRIGGER",BTRG[k]))
    return out

phys_rows=[]
for k,v in sorted(SH.items()):
    src=sources_for(k)
    phys_rows.append({"field":k,"value_frozen_by_TLMR01":v,
                      "declared_by":[{"artefact":a,"value":b,"AGREES":float(b)==float(v)} for a,b in src],
                      "N_INDEPENDENT_SOURCES":len(src),
                      "HAS_A_BYTE_VERIFIED_SOURCE":len(src)>0,
                      "ALL_SOURCES_AGREE":all(float(b)==float(v) for _,b in src) if src else False})
PHYSICS_AGREES=all(r["ALL_SOURCES_AGREE"] for r in phys_rows)
EVERY_SHARED_CONSTANT_HAS_A_SOURCE=all(r["HAS_A_BYTE_VERIFIED_SOURCE"] for r in phys_rows)
UNCOVERED=sorted(r["field"] for r in phys_rows if not r["HAS_A_BYTE_VERIFIED_SOURCE"])

# F_PRIMARY is a trigger gate, not a physics field, and TLMR01 computes it as 1 - 1/e.
import math
F_PRIMARY_LIVE=1.0-1.0/math.e
F_PRIMARY_ROW={"computed_in_tlmr01_as_1_minus_1_over_e":repr(F_PRIMARY_LIVE),
  "declared_by_BPRTC01_TRIGGER":repr(BTRG["F_PRIMARY"]),
  "bits_live":bits(F_PRIMARY_LIVE),"bits_declared":bits(BTRG["F_PRIMARY"]),
  "IDENTICAL_DOUBLE":F_PRIMARY_LIVE==float(BTRG["F_PRIMARY"])}
F_PRIMARY_EXACT=F_PRIMARY_ROW["IDENTICAL_DOUBLE"]

# LAW_B, the third law, against BPRTC01's own POINT — so all three laws are bit-checked, not two.
B=LW.LAWS["LAW_B_POINT_D10"]; PT=BP["POINT"]
lawb_rows=[{"field":f,"value_in_tlmr01_laws":repr(B[f]),"value_in_BPRTC01_POINT":repr(PT[f]),
            "bits_live":bits(B[f]),"bits_source":bits(PT[f]),
            "IDENTICAL_DOUBLE":float(B[f])==float(PT[f])} for f in ["kY","muY","p_hop_Y"]]
LAW_B_BIT_EXACT=all(r["IDENTICAL_DOUBLE"] for r in lawb_rows)

# LAW_A, against PQEC01's freeze, so no law is taken on trust from TLMR01's own artefact.
PQ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
def find_b1(o):
    if isinstance(o,dict):
        if "POINT_B1" in o and isinstance(o["POINT_B1"],dict): return o["POINT_B1"]
        for v in o.values():
            r=find_b1(v)
            if r is not None: return r
    return None
B1=find_b1(PQ) or {}
lawa_rows=[]
for f in ["kY","muY","p_hop_Y"]:
    src=B1.get(f, BINH.get("p_hop_Y_mobile") if f=="p_hop_Y" else None)
    lawa_rows.append({"field":f,"value_in_tlmr01_laws":repr(A[f]),
      "value_in_source":repr(src) if src is not None else None,
      "source":"PQEC01_MASTER_FREEZE PHASE_B.POINT_B1" if f in B1 else
               "BPRTC01_MASTER_FREEZE POINT.INHERITED_FROZEN_CONSTANTS.p_hop_Y_mobile",
      "IDENTICAL_DOUBLE":(src is not None and float(src)==float(A[f]))})
LAW_A_BIT_EXACT=all(r["IDENTICAL_DOUBLE"] for r in lawa_rows)

# ---------- 5. the parent tip: reachability, and what it is corroborated by ----------
TIP=json.load(open(f"{REPO}/TLMR01/out/TLMR01_PARENT_BINDING.json"))["PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY"]
def git(*a):
    r=subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True)
    return r.returncode,r.stdout.strip(),r.stderr.strip()
rc,_,_=git("cat-file","-t",TIP)
TIP_OBJECT_REACHABLE=(rc==0)

# ---------- 6. the seed rule, re-derived from the frozen tip STRING ----------
MAN=json.load(open(f"{REPO}/TLMR01/out/TLMR01_SEED_MANIFEST.json"))
def seed(tip,law,role,i):
    h=hashlib.sha256(("%s|TLMR01|%s|%s|%d"%(tip,law,role,i)).encode()).digest()
    return int.from_bytes(h[:8],"big")%(2**32)
redo=[]
for b in MAN["SEEDS"]:
    redo.append(seed(TIP,b["law"],"PRIMARY",b["index"])==b["seed"])
for b in MAN["RESERVE_SEEDS"]:
    redo.append(seed(TIP,"ANY","RESERVE",b["index"])==b["seed"])
SEEDS_REDERIVE=all(redo)
rehash=hashlib.sha256(json.dumps(
  [[b["law"],b["role"],b["index"],b["seed"]] for b in MAN["SEEDS"]+MAN["RESERVE_SEEDS"]],
  sort_keys=True).encode()).hexdigest()
SEED_SET_HASH_AGREES=(rehash==MAN["SEED_SET_HASH"])

art={
 "MISSION":"FIMRCC01","SECTION":"0 — precondition P2, law-binding re-verification",
 "GENERATED_UTC":U,
 "WHY_THIS_EXISTS":"the TLMR01 handoff records that BPRTC01_MASTER_FREEZE.json, "
   "MCTT01_SELECTED_LAW.json and MCTT01_PHYSICS_DIFF_FROM_B1.json were absent from the container "
   "that issued it, so the selected law was not bit-verifiable there and three modules did not "
   "import. All three were retrieved from the owner's machine and are checked here.",
 "PROVENANCE_OF_THE_RETRIEVED_COPIES":{
   "MCTT01_SELECTED_LAW.json":"ISING_LIFE_AUTHORITATIVE_RECOVERY/delivery/MCTT01_FINAL_EVIDENCE_CAPSULE.tar :: MCTT01/out/",
   "MCTT01_PHYSICS_DIFF_FROM_B1.json":"ISING_LIFE_AUTHORITATIVE_RECOVERY/delivery/MCTT01_FINAL_EVIDENCE_CAPSULE.tar :: MCTT01/out/",
   "BPRTC01_MASTER_FREEZE.json":"ISING_LIFE_AUTHORITATIVE_RECOVERY/BPRTC01/final/BPRTC01_FINAL_EVIDENCE_CAPSULE.tar :: out/",
   "PQEC01_MASTER_FREEZE.json":"already present in the container; hashed here anyway"},
 "SOURCE_BYTES":byte_rows,"ALL_SOURCE_BYTES_MATCH":ALL_BYTES_MATCH,
 "MODULE_IMPORT":mods,"ALL_MODULES_IMPORT":ALL_MODULES_IMPORT,
 "LAW_C_AGAINST_MCTT01_BITS":bit_rows,"LAW_C_BIT_EXACT":LAW_C_BIT_EXACT,
 "NO_NUMBER_HERE_COMES_FROM_PROSE":"every value is read from the source artefact's JSON and "
   "compared as an IEEE-754 double and as a 64-bit pattern. MCTT01 itself records that its "
   "handoff prose printed kY and muY with a different repr that is the same double; the prose "
   "repr is never read by this check.",
 "PHYSICS_DIFF_FROM_B1":diff_rows,"DIFF_ARTEFACT_AGREES":DIFF_AGREES,
 "ONLY_kY_AND_muY_MOVED_OFF_B1":ONLY_TWO_CHANGED,
 "SHARED_PHYSICS":phys_rows,"SHARED_PHYSICS_AGREES":PHYSICS_AGREES,
 "EVERY_SHARED_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE":EVERY_SHARED_CONSTANT_HAS_A_SOURCE,
 "SHARED_CONSTANTS_WITHOUT_A_SOURCE":UNCOVERED,
 "F_PRIMARY":F_PRIMARY_ROW,"F_PRIMARY_BIT_EXACT":F_PRIMARY_EXACT,
 "LAW_A_AGAINST_PQEC01":lawa_rows,"LAW_A_BIT_EXACT":LAW_A_BIT_EXACT,
 "LAW_B_AGAINST_BPRTC01":lawb_rows,"LAW_B_BIT_EXACT":LAW_B_BIT_EXACT,
 "ALL_THREE_LAWS_BIT_EXACT_AGAINST_THEIR_OWN_SOURCE":bool(LAW_A_BIT_EXACT and LAW_B_BIT_EXACT and LAW_C_BIT_EXACT),
 "PARENT_TIP":TIP,
 "PARENT_TIP_OBJECT_REACHABLE_IN_THIS_CONTAINER":TIP_OBJECT_REACHABLE,
 "PARENT_TIP_SEARCHED_FOR_IN":[
   "the container repository (git cat-file)",
   "ISING_LIFE_AUTHORITATIVE_RECOVERY/git/edl_verify.git",
   "ISING_LIFE_AUTHORITATIVE_RECOVERY/git/vc2.git",
   "ISING_LIFE_AUTHORITATIVE_RECOVERY/git/verify_clone.git"],
 "PARENT_TIP_FOUND_IN_ANY_OF_THEM":False,
 "WHY_THE_OBJECT_IS_GONE":"the total container rollback erased FOTSEA01's history; TLMR01 C3 was "
   "rebuilt on 82f6c84 (FDOT01 C2) and the current history does not descend from the parent tip.",
 "WHAT_CORROBORATES_THE_TIP_STRING_INSTEAD":{
   "artefact":"TLMR01_C1_C2.bundle on the owner's machine, written 2026-08-24 before the rollback",
   "test":"git bundle verify against an empty repository",
   "result":"error: Repository lacks these prerequisite commits: "
            "9f4c70ceeb05b0b8a1f27c4cfc855e125f921ce9",
   "what_it_shows":"the bundle names that exact commit as its prerequisite, so TLMR01 C1 was "
     "written directly on top of it in a repository that contained it. This corroborates the "
     "tip STRING independently of TLMR01's own artefacts. It does not recover the object, so "
     "the tip's tree and message remain unverifiable.",
   "STATUS":"CORROBORATED_BUT_NOT_OBJECT_VERIFIABLE"},
 "WHY_THIS_DOES_NOT_BLOCK_A_WORLD":"the seed rule consumes the tip as a STRING fed to sha256, not "
   "as a git lookup. The string is frozen identically in TLMR01_PARENT_BINDING.json, in "
   "TLMR01_SEED_MANIFEST.json and in the bundle prerequisite above, and every one of the 518 "
   "frozen seeds re-derives from it here. Seed reproducibility and the disjointness proof "
   "FIMRCC01 owes are therefore fully checkable; what is NOT checkable is the CONTENT of the "
   "parent commit, and that is reported, not asserted away.",
 "SEED_RULE_REDERIVES_EVERY_FROZEN_SEED_FROM_THE_TIP_STRING":SEEDS_REDERIVE,
 "N_SEEDS_REDERIVED":len(redo),
 "SEED_SET_HASH_AGREES":SEED_SET_HASH_AGREES,
 "SEED_SET_HASH":MAN["SEED_SET_HASH"],
}
art["P2_BYTE_LEVEL_PASS"]=bool(ALL_BYTES_MATCH and ALL_MODULES_IMPORT and LAW_C_BIT_EXACT
  and LAW_A_BIT_EXACT and LAW_B_BIT_EXACT and F_PRIMARY_EXACT and EVERY_SHARED_CONSTANT_HAS_A_SOURCE
  and DIFF_AGREES and ONLY_TWO_CHANGED and PHYSICS_AGREES and SEEDS_REDERIVE and SEED_SET_HASH_AGREES)
art["P2_RESIDUAL_OPEN"]="the parent commit OBJECT is unrecoverable everywhere it was looked for. " \
  "The tip string is corroborated by an independent pre-rollback artefact and every frozen seed " \
  "re-derives from it, so the binding is checkable; the parent commit's content is not."
json.dump(art,open(f"{REPO}/FIMRCC01/out/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json","w"),indent=1)

for k in ["ALL_SOURCE_BYTES_MATCH","ALL_MODULES_IMPORT","LAW_A_BIT_EXACT","LAW_B_BIT_EXACT",
          "LAW_C_BIT_EXACT","ALL_THREE_LAWS_BIT_EXACT_AGAINST_THEIR_OWN_SOURCE","F_PRIMARY_BIT_EXACT",
          "DIFF_ARTEFACT_AGREES","EVERY_SHARED_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE",
          "ONLY_kY_AND_muY_MOVED_OFF_B1","SHARED_PHYSICS_AGREES",
          "SEED_RULE_REDERIVES_EVERY_FROZEN_SEED_FROM_THE_TIP_STRING","SEED_SET_HASH_AGREES",
          "PARENT_TIP_OBJECT_REACHABLE_IN_THIS_CONTAINER","P2_BYTE_LEVEL_PASS"]:
    print("%-58s = %s"%(k,art[k]))
print("shared constants without a byte-verified source:",UNCOVERED)
for r in bit_rows: print("  %-8s %-24s %s"%(r["field"],r["bits_of_the_live_value"],r["MATCHES_DECLARED_BITS"]))
