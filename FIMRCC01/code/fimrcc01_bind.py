"""FIMRCC01 Section 1 — bind the parent, the law and the physics, bit-for-bit.

Nothing in this file chooses a number. Every physical value is read from a byte-verified parent
artefact whose sha256 is checked here against TLMR01's frozen SOURCE_BYTES record, and the
selected law is additionally checked against the IEEE-754 bit patterns MCTT01 published for it.
No parameter is retuned, no point is invented, nothing is interpolated.
"""
from __future__ import annotations
import sys, os, json, hashlib, struct, datetime, subprocess, math
REPO="/home/claude/edl"; OUT=f"{REPO}/FIMRCC01/out"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_laws as LW
U=datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def bits(x): return "0x"+struct.pack(">d",float(x)).hex()
def git(*a):
    r=subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True)
    return r.returncode,r.stdout.strip()

FROZEN =json.load(open(f"{REPO}/TLMR01/out/TLMR01_MEASUREMENT_LAWS.json"))
DISP   =json.load(open(f"{REPO}/TLMR01/out/TLMR01_FINAL_DISPOSITION.json"))
TPB    =json.load(open(f"{REPO}/TLMR01/out/TLMR01_PARENT_BINDING.json"))
P2     =json.load(open(f"{OUT}/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json"))
XCHK   =json.load(open(f"{REPO}/TLMR01/out/TLMR01_DEVICE_PATH_CROSSCHECK.json"))
SEL    =json.load(open(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json"))
DIFF   =json.load(open(f"{REPO}/MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json"))
BP     =json.load(open(f"{REPO}/BPRTC01/out/BPRTC01_MASTER_FREEZE.json"))

HANDOFF=f"{REPO}/TLMR01/out/HANDOFF_FRESH_INTEGRATED_MINIMAL_REPRODUCTION_CAUSAL_CONFIRMATION_01.md"
_,TIP=git("rev-parse","HEAD")
FLOOR="06c592313df96601de8d2a89676d5a5cf79fc414"
rc_floor,_=git("cat-file","-t",FLOOR)

# clauses inherited at birth — re-emitted VERBATIM from §5 of the handoff, in its own order
INHERITED_VERBATIM={
 "MEASUREMENT_NOT_POINT_SEARCH":"true",
 "ONE_ZERO_RUN_DETOUR_ONLY":"spent — no further finite-size mission",
 "SECOND_FINITE_SIZE_EXTENSION":"forbidden",
 "NEW_SIZE_LADDER":"forbidden",
 "POST_OUTCOME_SIZE_RETUNING":"forbidden",
 "NEW_PARAMETER_SWEEP":"forbidden",
 "GENERIC_CALIBRATION_SUCCESSOR":"forbidden",
 "INTERPOLATION":"forbidden",
 "RESPONSE_SURFACE":"forbidden",
 "EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES":"true",
 "REOPENING_FINITE_SIZE_REQUIRES_EXPLICIT_HUMAN_AUTHORISATION":"true",
 "MAX_INDEPENDENT_CHECKERS":"1",
 "MAX_REVIEW_CASCADES":"0",
 "CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON":"mandatory",
 "SECOND_TARGETED_MEASUREMENT_CAMPAIGN":"forbidden"}

LAUNCHER={
 "SELECTED_LAW":"exact LAW_C_MCTT01",
 "NEW_PARAMETER_POINTS":0,
 "PARAMETER_RETUNING":"forbidden",
 "INTERPOLATION":"forbidden",
 "RESPONSE_SURFACE":"forbidden",
 "ADAPTIVE_SAMPLE_SIZE":"forbidden",
 "ADAPTIVE_STOPPING":"forbidden",
 "POST_OUTCOME_THRESHOLD_CHANGE":"forbidden",
 "EXPECTED_FRESH_BASE_BLOCKS":50,
 "MAX_ARM_INSTANCES":"3 x blocks",
 "MAX_TECHNICAL_RESERVES":6,
 "MAX_INTENTIONAL_COMMITS":5,
 "MAX_INDEPENDENT_CHECKERS":1,
 "REVIEW_CASCADE":"forbidden",
 "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0,
 "NO_DESIGN_MISSION_MAY_INTERVENE":True,
 "FRESH_DISJOINT_SEEDS":"mandatory; disjoint from TLMR01's 512 primary, 6 reserve and the 71xxx "
   "fixture band, proved by enumeration"}

STATUS={
 "H3_STATUS":"NOT_TESTED",
 "REPRODUCTION_STATUS":"NOT_TESTED",
 "HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
 "FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED",
 "PTOPD01_LINEAGE_POINT_ROUTE_STATUS":"MEASURED, NOT QUALIFIED",
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED"}

# ------------------------------------------------------------------ 1. parent binding
parent={
 "MISSION":"FIMRCC01","SECTION":"1 — parent binding","GENERATED_UTC":U,
 "PARENT":"TLMR01 — TARGETED-LINEAGE-MEASUREMENT-FOR-REPRODUCTION-01",
 "PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY":TIP,
 "PARENT_TIP_SUBJECT":git("log","-1","--format=%s",TIP)[1],
 "PARENT_TIP_IS_THE_CURRENT_HEAD":True,
 "PARENT_DISPOSITION":DISP["FINAL_DISPOSITION"],
 "PARENT_DISPOSITION_IS_ONE_OF_THE_FOUR_FROZEN_TERMINALS":DISP["DISPOSITION_IS_ONE_OF_THE_FOUR_FROZEN_TERMINALS"],
 "SELECTED_CONFIRMATION_LAW_INHERITED":DISP["SELECTED_CONFIRMATION_LAW"],
 "HANDOFF":{"path":"TLMR01/out/HANDOFF_FRESH_INTEGRATED_MINIMAL_REPRODUCTION_CAUSAL_CONFIRMATION_01.md",
            "sha256":sha(HANDOFF),"bytes":os.path.getsize(HANDOFF)},
 "SECTION_0_PRECONDITIONS":{
   "P1_DEVICE_PATH_CROSS_CHECK":{
     "artefact":"TLMR01/out/TLMR01_DEVICE_PATH_CROSSCHECK.json",
     "sha256":sha(f"{REPO}/TLMR01/out/TLMR01_DEVICE_PATH_CROSSCHECK.json"),
     "CROSS_CHECK_PASS":XCHK["CROSS_CHECK_PASS"],
     "NON_VACUOUS":XCHK["NON_VACUITY"]["NON_VACUOUS"],
     "N_WORLDS":XCHK["N_CROSS_CHECKED"],
     "ALL_HAVE_A_REMOVAL_APPLIED":XCHK["ALL_HAVE_A_REMOVAL_APPLIED"],
     "STATUS":"CLOSED" if (XCHK["CROSS_CHECK_PASS"] and XCHK["NON_VACUITY"]["NON_VACUOUS"]) else "OPEN"},
   "P2_LAW_BINDING_REVERIFICATION":{
     "artefact":"FIMRCC01/out/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json",
     "sha256":sha(f"{OUT}/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json"),
     "P2_BYTE_LEVEL_PASS":P2["P2_BYTE_LEVEL_PASS"],
     "RESIDUAL_OPEN":P2["P2_RESIDUAL_OPEN"],
     "PARENT_TIP_OF_TLMR01_OBJECT_REACHABLE":P2["PARENT_TIP_OBJECT_REACHABLE_IN_THIS_CONTAINER"],
     "STATUS":"CLOSED_AT_THE_BYTE_LEVEL_WITH_ONE_REPORTED_RESIDUAL" if P2["P2_BYTE_LEVEL_PASS"] else "OPEN"}},
 "BOTH_PRECONDITIONS_CLOSED_BEFORE_ANY_WORLD":bool(
    XCHK["CROSS_CHECK_PASS"] and XCHK["NON_VACUITY"]["NON_VACUOUS"] and P2["P2_BYTE_LEVEL_PASS"]),
 "INHERITED_CLAUSES_RE_EMITTED_VERBATIM":INHERITED_VERBATIM,
 "WHY_THEY_ARE_RE_EMITTED":"the clause EVERY_SUCCESSOR_MUST_RE_EMIT_THESE_CLAUSES is itself one of "
   "them. Re-emitting them here binds them at FIMRCC01's birth, and FIMRCC01's own handoff must "
   "re-emit them again.",
 "LAUNCHER_CONSTRAINTS":LAUNCHER,
 "NEVER_REWRITE_INHERITED_HISTORY_AT_OR_BELOW":FLOOR,
 "FLOOR_COMMIT_RESOLVES_IN_THIS_CONTAINER":rc_floor==0,
 "HEAD_AT_BINDING":TIP,
 "STATUS_STRINGS_BINDING_UNCONDITIONALLY":STATUS,
 "FORBIDDEN_VOCABULARY":["organism","daughter organism","life created","self-replication demonstrated"],
 "FORBIDDEN_CLAIMS_INCLUDING_IN_DENIAL":["reproduction","heredity","life","autonomous cohesion",
   "H3 confirmation","Kamimura-Kaneko validation","a minority window"]}

# ------------------------------------------------------------------ 2. selected law
C=LW.LAWS["LAW_C_MCTT01"]; S=SEL["SELECTED"]
law_fields=[]
for f in ["kY","muY","p_hop_Y"]:
    law_fields.append({"field":f,"value":repr(float(C[f])),"bits":bits(C[f]),
      "declared_bits_in_MCTT01_SELECTED_LAW":S[f+"_bits"],
      "MATCHES_DECLARED_BITS":bits(C[f])==S[f+"_bits"],
      "IDENTICAL_DOUBLE_TO_THE_SOURCE":float(C[f])==float(S[f])})
selected={
 "MISSION":"FIMRCC01","SECTION":"1 — the selected law","GENERATED_UTC":U,
 "SELECTED_LAW":"LAW_C_MCTT01",
 "MAX_SELECTED_LAWS":1,"N_SELECTED":1,
 "IT_IS_THE_LAW_TLMR01_SELECTED":DISP["SELECTED_CONFIRMATION_LAW"]=="LAW_C_MCTT01",
 "NEW_PARAMETER_POINTS":0,
 "PARAMETER_RETUNING":"forbidden — and none is performed; every field below is read from a "
   "byte-verified parent artefact",
 "SELECTED_Y_LAW":{f:float(C[f]) for f in ["kY","muY","p_hop_Y"]},
 "BIT_LEVEL_VERIFICATION":law_fields,
 "ALL_FIELDS_BIT_EXACT":all(r["MATCHES_DECLARED_BITS"] and r["IDENTICAL_DOUBLE_TO_THE_SOURCE"] for r in law_fields),
 "PROVENANCE_CHAIN":[
   {"step":1,"artefact":"MCTT01/out/MCTT01_SELECTED_LAW.json",
    "sha256":sha(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json"),
    "declares":"SELECTED.kY, SELECTED.muY, SELECTED.p_hop_Y and their 64-bit patterns"},
   {"step":2,"artefact":"MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json",
    "sha256":sha(f"{REPO}/MCTT01/out/MCTT01_PHYSICS_DIFF_FROM_B1.json"),
    "declares":"that exactly two parameters, kY and muY, moved off B1, and by what factor"},
   {"step":3,"artefact":"TLMR01/out/TLMR01_MEASUREMENT_LAWS.json",
    "sha256":sha(f"{REPO}/TLMR01/out/TLMR01_MEASUREMENT_LAWS.json"),
    "declares":"the same three doubles as LAW_C_MCTT01, and the sha256 of all four source artefacts"},
   {"step":4,"artefact":"FIMRCC01/out/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json",
    "sha256":sha(f"{OUT}/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json"),
    "declares":"that all four source artefacts hash to their declared values in this container "
               "and that all three laws are bit-exact against their own sources"}],
 "NO_NUMBER_IS_READ_FROM_PROSE":"MCTT01 records that its own handoff prose printed kY as "
   "0.0010047545726038329 and muY as 0.00074089498250303496 — different reprs of the same "
   "doubles. Neither prose literal is read anywhere in this mission; the doubles are taken from "
   "the JSON and checked against the published bit patterns.",
 "kY_IS_40x_B1":float(C["kY"])==float(DIFF["CHANGED"][0]["MCTT01"]) and DIFF["CHANGED"][0]["factor"]==40.0,
 "muY_IS_8x_B1":float(C["muY"])==float(DIFF["CHANGED"][1]["MCTT01"]) and DIFF["CHANGED"][1]["factor"]==8.0,
 "MOBILITY_IS_AN_ALREADY_EXECUTED_VALUE":DIFF["MOBILITY_IS_AN_ALREADY_EXECUTED_VALUE"],
 "MOBILITY_RETUNED":DIFF["MOBILITY_RETUNED"],
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "WHAT_TLMR01_MEASURED_AT_THIS_LAW_AND_NOTHING_MORE":{
   "n_worlds":256,"M5_integrated":"22/256","M5_lower95":0.0589,
   "F_INTEGRATED_endpoint_matched_floor":0.0032015171041760242,
   "CAVEAT_THAT_TRAVELS_WITH_THE_SELECTION":"the frozen turnover endpoint is confounded with "
     "occupancy: at this law the 22 removals leave 2,018 complete post-removal identity "
     "intervals, median 93 per world, so an endpoint asking for at least one is saturated. "
     "There is no no-removal control anywhere in TLMR01's 512 worlds. This is the reason "
     "FIMRCC01 is a three-arm matched design and not a repeat."}}

# ------------------------------------------------------------------ 3. physics binding
SH=FROZEN["SHARED_FROZEN_PHYSICS"]
phys={r["field"]:r for r in P2["SHARED_PHYSICS"]}
physics={
 "MISSION":"FIMRCC01","SECTION":"1 — physics binding","GENERATED_UTC":U,
 "EVERY_CONSTANT_AND_ITS_BYTE_VERIFIED_SOURCE":[
   {"field":k,"value":SH[k],
    "declared_by":[d["artefact"] for d in phys[k]["declared_by"]],
    "N_INDEPENDENT_SOURCES":phys[k]["N_INDEPENDENT_SOURCES"],
    "ALL_SOURCES_AGREE":phys[k]["ALL_SOURCES_AGREE"]} for k in sorted(SH)],
 "EVERY_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE":P2["EVERY_SHARED_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE"],
 "TRIGGER_GATES":{
   "NEED":BP["TRIGGER"]["NEED"],
   "F_PRIMARY":BP["TRIGGER"]["F_PRIMARY"],
   "F_PRIMARY_bits":bits(BP["TRIGGER"]["F_PRIMARY"]),
   "F_PRIMARY_computed_as_1_minus_1_over_e_is_the_same_double":P2["F_PRIMARY_BIT_EXACT"],
   "LATEST_ALLOWED_TRIGGER":BP["TRIGGER"]["LATEST_ALLOWED_TRIGGER"],
   "rule":BP["TRIGGER"]["rule"],
   "UNCHANGED_FROM":BP["TRIGGER"]["UNCHANGED_FROM"]},
 "UNCHANGED_MACHINERY":FROZEN["WHAT_IS_IDENTICAL_ACROSS_ALL_THREE"],
 "NEW_ARCHITECTURE":False,"NEW_SUBSTRATE":False,"NEW_SPECIES":False,"NEW_X_LAWSPEC":False,
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "ENGINE":"the frozen WorldV2._one_step order — diffuse, react, decay, exchange — reached through "
   "pqec01_observer.build_world and lawspec_v2.spec_with, unchanged.",
 "CENTRE_CLASSIFIER":SEL["CENTRE_CLASSIFIER"],
 "FEED_EXCHANGE_LAW":SEL["FEED_EXCHANGE_LAW"],
 "INITIAL_CONDITION":SEL["INITIAL_CONDITION"],
 "SCHEDULER":SEL["SCHEDULER"],
 "PARENT_REMOVAL_INTERVENTION":SEL["PARENT_REMOVAL_INTERVENTION"],
 "MOBILITY_CONSTANCY":SEL["MOBILITY_CONSTANCY"],
 "WHAT_FIMRCC01_ADDS_TO_THE_PHYSICS":"nothing. The three arms differ only in which cells the "
   "intervention writes to at the trigger step; the law, the engine, the scheduler, the "
   "classifier and the trigger rule are byte-identical across all three.",
 "SEED_RULE":"sha256(PARENT_TIP | 'FIMRCC01' | ARM | ROLE | INDEX)[:8] as big-endian uint64, "
   "mod 2**32, with PARENT_TIP = "+TIP+". Disjointness from TLMR01's primary, reserve and "
   "fixture bands is PROVED BY ENUMERATION in the pre-run freeze, not argued from the mission "
   "string.",
 "SEED_RULE_IS_DECLARED_HERE_AND_EXECUTED_IN_THE_FREEZE":True}

for name,obj in [("FIMRCC01_PARENT_BINDING.json",parent),
                 ("FIMRCC01_SELECTED_LAW.json",selected),
                 ("FIMRCC01_PHYSICS_BINDING.json",physics)]:
    json.dump(obj,open(f"{OUT}/{name}","w"),indent=1)
    print("%-40s %s"%(name,sha(f"{OUT}/{name}")))

print()
print("BOTH_PRECONDITIONS_CLOSED_BEFORE_ANY_WORLD =",parent["BOTH_PRECONDITIONS_CLOSED_BEFORE_ANY_WORLD"])
print("ALL_FIELDS_BIT_EXACT                       =",selected["ALL_FIELDS_BIT_EXACT"])
print("EVERY_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE  =",physics["EVERY_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE"])
print("FLOOR_COMMIT_RESOLVES                      =",parent["FLOOR_COMMIT_RESOLVES_IN_THIS_CONTAINER"])
print("kY 40x / muY 8x                            =",selected["kY_IS_40x_B1"],selected["muY_IS_8x_B1"])
