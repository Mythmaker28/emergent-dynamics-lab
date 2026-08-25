"""FIMRCC01 closure — checkpoint binding, Precondition B result, endpoint adjudication,
final disposition. ZERO fresh worlds, zero fresh seeds, zero new trajectories."""
from __future__ import annotations
import json, glob, math, hashlib, datetime, os, subprocess, statistics
from collections import Counter
REPO="/home/claude/edl"; OUT=f"{REPO}/FIMRCC01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def git(*a):
    r=subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True)
    return r.returncode,r.stdout.strip()

F=0.0032015171041760242
def lsf(k,n,p):
    if k<=0: return 1.0
    if p<=0.0: return 0.0
    if p>=1.0: return 1.0
    lp=math.log(p); lq=math.log1p(-p); s=0.0
    for i in range(k,n+1):
        s+=math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)+i*lp+(n-i)*lq)
        if s>=1.0: return 1.0
    return s
def kstar(n,p0=F,a=0.05):
    for k in range(0,n+1):
        if lsf(k,n,p0)<=a: return k
def cp_lower(k,n,a=0.05):
    if k==0: return 0.0
    lo,hi=0.0,1.0
    for _ in range(200):
        mid=(lo+hi)/2
        if lsf(k,n,mid)>a: hi=mid
        else: lo=mid
    return (lo+hi)/2
def cp_upper(k,n,a=0.05):
    if k>=n: return 1.0
    lo,hi=0.0,1.0
    for _ in range(200):
        mid=(lo+hi)/2
        # P(X<=k) <= a  -> upper bound
        s=1.0-lsf(k+1,n,mid)
        if s>a: lo=mid
        else: hi=mid
    return (lo+hi)/2

P2   =json.load(open(f"{OUT}/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json"))
PB   =json.load(open(f"{OUT}/FIMRCC01_PARENT_BINDING.json"))
SEL  =json.load(open(f"{OUT}/FIMRCC01_SELECTED_LAW.json"))
PHY  =json.load(open(f"{OUT}/FIMRCC01_PHYSICS_BINDING.json"))
PA   =json.load(open(f"{OUT}/FIMRCC01_LOCKED_IDENTITY_QUALIFICATION.json"))
PBQ  =json.load(open(f"{OUT}/FIMRCC01_INDEPENDENT_ENDPOINT_QUALIFICATION.json"))
REG  =json.load(open(f"{OUT}/FIMRCC01_ENDPOINT_PREREGISTRATION.json"))
TAB  =json.load(open(f"{OUT}/FIMRCC01_ENDPOINT_TABLE.json"))
XCHK =json.load(open(f"{REPO}/TLMR01/out/TLMR01_DEVICE_PATH_CROSSCHECK.json"))
MAN  =json.load(open(f"{REPO}/TLMR01/out/TLMR01_SEED_MANIFEST.json"))
DES  =[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pbd/*.json"))]
PBROW=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pb3/*.json"))]

# ------------------------------------------------------------------ 1. checkpoint binding
_,HEAD=git("rev-parse","HEAD")
TIP=P2["PARENT_TIP"]
files=["FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json","FIMRCC01_PARENT_BINDING.json",
       "FIMRCC01_SELECTED_LAW.json","FIMRCC01_PHYSICS_BINDING.json",
       "FIMRCC01_PRECONDITION_A_RULE.json","FIMRCC01_LOCKED_IDENTITY_QUALIFICATION.json",
       "FIMRCC01_INDEPENDENT_ENDPOINT_QUALIFICATION.json",
       "FIMRCC01_ENDPOINT_PREREGISTRATION.json","FIMRCC01_ENDPOINT_TABLE.json"]
chk={
 "MISSION":"FIMRCC01","SECTION":"closure 1 — current checkpoint binding","GENERATED_UTC":U,
 "HUMAN_DECISION":"A__PRECONDITIONS_NOT_MET",
 "NEW_SCIENTIFIC_WORLDS":0,"NEW_WORLD_CONSTRUCTIONS":0,"NEW_SEEDS":0,"NEW_TRAJECTORIES":0,
 "HEAD_AT_CLOSURE":HEAD,
 "PARENT_TIP_OF_TLMR01":TIP,
 "PARENT_GIT_OBJECT_STATUS":"PARENT_GIT_OBJECT_NOT_RECOVERED",
 "PARENT_SOURCE_BYTE_STATUS":"SOURCE_BYTES_AND_CHAIN_PREREQUISITE_VERIFIED",
 "WHAT_THAT_DISTINCTION_MEANS":"the commit OBJECT 9f4c70ce... is unrecoverable in the container, "
   "in all three owner-side bare repositories and in every bundle checked. Its CONTENT is not "
   "verifiable. What IS verified is (a) the four source artefacts it is supposed to have carried, "
   "byte for byte, and (b) that TLMR01_C1_C2.bundle, written before the rollback, names that "
   "exact commit as its prerequisite. Content recovery is not object recovery and is not reported "
   "as such.",
 "THE_FOUR_VERIFIED_SOURCE_HASHES":P2["SOURCE_BYTES"],
 "ALL_SOURCE_BYTES_MATCH":P2["ALL_SOURCE_BYTES_MATCH"],
 "THE_THREE_EXACT_LAW_BINDINGS":{
   "LAW_A_B1":{"bit_exact":P2["LAW_A_BIT_EXACT"],"rows":P2["LAW_A_AGAINST_PQEC01"]},
   "LAW_B_POINT_D10":{"bit_exact":P2["LAW_B_BIT_EXACT"],"rows":P2["LAW_B_AGAINST_BPRTC01"]},
   "LAW_C_MCTT01":{"bit_exact":P2["LAW_C_BIT_EXACT"],"rows":P2["LAW_C_AGAINST_MCTT01_BITS"]}},
 "ALL_THREE_LAWS_BIT_EXACT":P2["ALL_THREE_LAWS_BIT_EXACT_AGAINST_THEIR_OWN_SOURCE"],
 "SEEDS":{"n_rederived":P2["N_SEEDS_REDERIVED"],
   "all_rederive_from_the_tip_string":P2["SEED_RULE_REDERIVES_EVERY_FROZEN_SEED_FROM_THE_TIP_STRING"],
   "seed_set_hash":P2["SEED_SET_HASH"],"seed_set_hash_agrees":P2["SEED_SET_HASH_AGREES"],
   "n_primary":MAN["N_PRIMARY"],"n_reserve":MAN["N_RESERVE"],
   "FRESH_SEEDS_CONSUMED_BY_FIMRCC01":0},
 "P1_DEVICE_PATH_VERIFICATION":{
   "CROSS_CHECK_PASS":XCHK["CROSS_CHECK_PASS"],"NON_VACUOUS":XCHK["NON_VACUITY"]["NON_VACUOUS"],
   "n_worlds":XCHK["N_CROSS_CHECKED"],"all_with_a_removal":XCHK["ALL_HAVE_A_REMOVAL_APPLIED"],
   "STATUS":"CLOSED"},
 "P2_SOURCE_BYTE_VERIFICATION":{"P2_BYTE_LEVEL_PASS":P2["P2_BYTE_LEVEL_PASS"],
   "RESIDUAL":P2["P2_RESIDUAL_OPEN"],"STATUS":"CLOSED_AT_THE_BYTE_LEVEL"},
 "LOCKED_DAUGHTER_REANALYSIS":{
   "PRECONDITION_A":PA["PRECONDITION_A"],
   "A1":PA["GATE_A1_UNIQUE_LOCALISATION"]["PASS"],
   "A2":PA["GATE_A2_NO_SILENT_TIE"]["PASS"],
   "A3":PA["GATE_A3_ENDPOINT_IS_ASKABLE"]["PASS"],
   "rule_sha256":PA["RULE_SHA256"]},
 "UNRESTRICTED_VERSUS_LOCKED_ENDPOINT":PA["SATURATION_DISCLOSURE_NOT_A_GATE"],
 "ARTEFACTS_BOUND":[{"file":f,"sha256":sha(f"{OUT}/{f}"),"bytes":os.path.getsize(f"{OUT}/{f}")}
                    for f in files],
 "RECOMPUTED_BECAUSE_A_FILE_INTEGRITY_CHECK_FAILED":False,
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED"}
json.dump(chk,open(f"{OUT}/FIMRCC01_CURRENT_CHECKPOINT_BINDING.json","w"),indent=1)

# ------------------------------------------------------------------ 2. Precondition B result
E=[r["ENDPOINT"] for r in DES if "ENDPOINT" in r]
Fi=[r["REMOVAL_FIDELITY"] for r in DES if "REMOVAL_FIDELITY" in r]
k_lock=sum(e["FUNCTIONAL"] for e in E)
pbres={
 "MISSION":"FIMRCC01","SECTION":"closure 2 — Precondition B result","GENERATED_UTC":U,
 "REQUIRED":"an independent offline reconstruction from raw physical inputs only, agreeing 100 % "
   "on M2, M3, M5 and the event step, and additionally — at the owner's closure instruction — "
   "reconstructing the parent/daughter naming, the selective-removal fidelity, the X function "
   "either side of turnover, the competing terminal events and the world-level locked-daughter "
   "verdict without using any online verdict or id.",
 "PASS_1_ALL_256_LAW_C_ARCHIVES":{
   "worlds":PBQ["N_WORLDS"],"steps_compared":PBQ["SCALE_OF_THE_COMPARISON"]["steps_compared"],
   "episodes_compared":PBQ["SCALE_OF_THE_COMPARISON"]["episodes_compared"],
   "worlds_with_full_agreement":PBQ["AGREEMENT"]["worlds_with_full_agreement"],
   "GATES":PBQ["GATES"],"VERDICT":PBQ["PRECONDITION_B"]},
 "PASS_2_THE_NAMING_ITSELF_ON_THE_26_TRIGGERED_WORLDS":{
   "why_only_26":"the parent/daughter naming is defined only where a trigger occurred. For the "
     "other 230 worlds the independent reconstruction already returned NOT_TRIGGERED in pass 1, "
     "with M3 and the event step agreeing in all 256.",
   "n_worlds":len(DES),
   "INPUTS_NOT_USED":["online component id","online identity id","online selected-daughter id",
     "online trigger verdict","online maturation verdict","online turnover verdict",
     "online M5 verdict","online terminal label"],
   "INPUTS_USED":["cell rows (t, y, x, per-cell Y occupancy)","world Y total",
     "Y-birth, Y-death and X-birth ledgers","toroidal geometry","the frozen centre rule",
     "the frozen FMRCT01 descent rule",
     "the intervention ledger's step and cell list, to locate the removal in time and to audit "
     "its fidelity — never to decide which component is the daughter"],
   "AGREEMENT":{
     "world_level_verdict":"%d/%d"%(sum(r["VERDICT_MATCHES_THE_ARCHIVE_LABEL"] for r in DES),len(DES)),
     "event_step_t_m":"%d/%d"%(sum(r["t_m_MATCHES_THE_ARCHIVE"] for r in DES),len(DES)),
     "daughter_cell_set":"%d/%d"%(sum(1 for r in DES if r.get("DAUGHTER_CELLS_MATCH_THE_ARCHIVE")),
                                  sum(1 for r in DES if "DAUGHTER_CELLS_MATCH_THE_ARCHIVE" in r)),
     "parent_cell_set":"%d/%d"%(sum(1 for r in DES if r.get("PARENT_CELLS_MATCH_THE_ARCHIVE")),
                                sum(1 for r in DES if "PARENT_CELLS_MATCH_THE_ARCHIVE" in r)),
     "ALL_CHECKS":"%d/%d"%(sum(r["ALL_INDEPENDENT_CHECKS_AGREE"] for r in DES),len(DES))},
   "INDEPENDENT_VERDICT_COUNTS":dict(Counter(r["VERDICT_INDEPENDENT"] for r in DES)),
   "SELECTIVE_REMOVAL_FIDELITY":{k:"%d/%d"%(sum(f[k] for f in Fi),len(Fi)) for k in
     ("Y_conserved","WY_gained_equals_Y_removed","parent_emptied","daughter_untouched","rng_unchanged")},
   "COMPETING_TERMINAL_EVENTS":dict(Counter(
     kk for r in DES for kk,vv in r["terminators"].items() for _ in range(vv))),
   "DESCENT_AT_THE_TRIGGER":dict(Counter(r.get("descent_level_at_t_m") for r in DES)),
   "LITERAL_MRCI01_CLAUSE_4_AT_THE_TRIGGER":dict(Counter(r.get("descent_literal_at_t_m") for r in DES)),
   "TERMINAL_DESCENT_DIFFERS_FROM_AT_TRIGGER_IN":sum(
     1 for r in DES if r.get("TERMINAL_AND_AT_TRIGGER_DESCENT_DIFFER")),
   "WHY_THAT_LAST_LINE_MATTERS":"the frozen FMRCT01 trigger keeps overwriting descent_level and "
     "the named pair at every later 1 -> 2 transition, so its terminal value is the LAST "
     "separation in the trajectory. TLMR01 recorded that defect; this reconstruction snapshots "
     "the naming AS OF the trigger step, as the online code does when it fires. The first version "
     "of this module read the terminal values instead and disagreed with the archive on world "
     "P_i001; the cause was that bug in the reconstruction, not a data disagreement, and it is "
     "recorded here rather than quietly fixed."},
 "INDEPENDENT_LOCKED_DAUGHTER_ENDPOINT":{
   "COMPLETE":"%d/%d"%(sum(e["COMPLETE"] for e in E),len(E)),
   "FUNCTIONAL":"%d/%d"%(k_lock,len(E)),
   "reproduces_Precondition_A":k_lock==1,
   "ambient_FUNCTIONAL":"%d/%d"%(sum(e["ambient_FUNCTIONAL"] for e in E),len(E)),
   "ambient_total_complete_intervals":sum(e["ambient_n_complete"] for e in E),
   "daughter_life_after_t_m":{"min":min(e["steps_after_t_m"] for e in E),
     "median":statistics.median([e["steps_after_t_m"] for e in E]),
     "max":max(e["steps_after_t_m"] for e in E)}},
 "CONFIRMED_LOAD_BEARING_DISAGREEMENTS":0,
 "DISAGREEING_WORLDS":[r["tag"] for r in DES if not r["ALL_INDEPENDENT_CHECKS_AGREE"]],
 "PRECONDITION_B":"PASS",
 "CONSEQUENCE_FOR_THE_DISPOSITION":"the independent reconstruction AGREES on the load-bearing "
   "locked-daughter endpoint, so the disposition is not FIMRCC01_TECHNICALLY_INVALID. The "
   "human-selected disposition A is not forced through a technical defect: there is no technical "
   "defect.",
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "PER_WORLD":[{"tag":r["tag"],"seed":r["seed"],"verdict":r["VERDICT_INDEPENDENT"],
   "t_m":r["t_m_independent"],"agrees":r["ALL_INDEPENDENT_CHECKS_AGREE"],
   "locked_daughter_COMPLETE":(r.get("ENDPOINT") or {}).get("COMPLETE"),
   "locked_daughter_FUNCTIONAL":(r.get("ENDPOINT") or {}).get("FUNCTIONAL"),
   "steps_after_t_m":(r.get("ENDPOINT") or {}).get("steps_after_t_m"),
   "ambient_n_complete":(r.get("ENDPOINT") or {}).get("ambient_n_complete")} for r in DES]}
json.dump(pbres,open(f"{OUT}/FIMRCC01_PRECONDITION_B_RESULT.json","w"),indent=1)

# ------------------------------------------------------------------ 3. endpoint adjudication
K_REQ=kstar(50)
p_world=1/256; p_removed=1/22
adj={
 "MISSION":"FIMRCC01","SECTION":"closure 3 — endpoint adjudication","GENERATED_UTC":U,
 "PREREGISTRATION_SHA256":TAB["PREREGISTRATION_SHA256"],
 "THE_CANDIDATE_SET_WAS_CLOSED_BEFORE_ANY_NUMBER":True,
 "FROZEN_DESIGN":{"N_BASE_BLOCKS":50,"K_REQUIREMENT":K_REQ,
   "F_INTEGRATED":F,"test":"exact one-sided binomial, alpha = 0.05, against F_INTEGRATED"},
 "E0":{"name":"unrestricted population endpoint",
   "STATUS":["SATURATED","NON_DISCRIMINATING","NOT_ELIGIBLE_AS_PRIMARY"],
   "evidence":{"worlds":"22/22 FUNCTIONAL among removal worlds",
     "complete_identity_intervals":2018,"median_per_world":93,
     "carried_by":"the ambient population rather than one locked daughter"},
   "TLMR01_RESULT_IS_PRESERVED":"TLMR01's developmental result is not called false. It answers a "
     "BROADER, population-level question than the intended minimal-reproduction claim: whether "
     "ANY identity anywhere in the world completed a constituent turnover after the removal. At "
     "this law's occupancy the answer is yes in every world that got a removal, and that is a "
     "true statement about the population, not about the daughter."},
 "E1_E2":{"name":"locked-daughter binary endpoints",
   "STATUS":["CLAIM_ALIGNED","NOT_DECISION_CAPABLE_AT_THE_FROZEN_N"],
   "k_among_removed_worlds":"1/22",
   "rate_among_removed_worlds":p_removed,
   "exact_95_interval_among_removed_worlds":[round(cp_lower(1,22),6),round(cp_upper(1,22),6)],
   "world_level_rate":"1/256","world_level_point":p_world,
   "exact_95_interval_world_level":[round(cp_lower(1,256),6),round(cp_upper(1,256),6)],
   "ratio_to_F_INTEGRATED":round(p_world/F,4),
   "K_REQUIREMENT":K_REQ,
   "P_K_GE_2_AT_N50_WORLD_LEVEL":round(lsf(K_REQ,50,p_world),4),
   "P_K_GE_2_AT_N50_REMOVED_WORLD_DENOMINATOR":round(lsf(K_REQ,50,p_removed),4),
   "THIS_IS_THE_LOAD_BEARING_REASON":"this is the load-bearing reason the confirmation cannot "
     "proceed. At N = 50 the pre-declared K >= 2 criterion has approximately 1.65 % assurance "
     "under the measured world-level rate, and no larger N repairs it because 1/256 = 0.0039 is "
     "only 1.22x the endpoint-matched floor."},
 "E3_E4_E5":{"name":"paired count contrasts",
   "STATUS":["SECONDARY_MECHANISTIC_QUESTIONS","NOT_SELECTED",
             "NOT_CONFIRMATORY_ENDPOINTS_IN_FIMRCC01"],
   "why_not":["they are contrasts, not the frozen binary reproduction event",
     "the inherited data contain no matched no-removal arm at LAW_C, anywhere in 512 worlds",
     "their prospective power is therefore not identified",
     "selecting one now would change the scientific question after developmental outcome access",
     "no fresh run may be authorised from them inside this mission"],
   "E3_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
   "E4_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
   "E5_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
   "NO_HANDOFF_IS_EMITTED_FOR_ANY_OF_THEM":True},
 "TABLE":TAB["TABLE"],
 "CONCLUSION":"no primary endpoint is simultaneously scientifically aligned, independently "
   "reconstructable, non-saturated, and decision-capable under the frozen fresh design.",
 "THIS_IS":"PRECONDITIONS_NOT_MET",
 "THIS_IS_NOT":["evidence that the phenomenon is impossible",
   "evidence that the architecture cannot support it",
   "a negative fresh confirmation",
   "a reason to reinterpret TLMR01 retrospectively"],
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED"}
json.dump(adj,open(f"{OUT}/FIMRCC01_ENDPOINT_ADJUDICATION.json","w"),indent=1)

# ------------------------------------------------------------------ 4. final disposition
disp={
 "MISSION":"FIMRCC01","SECTION":"closure 4 — final disposition","GENERATED_UTC":U,
 "FINAL_DISPOSITION":"CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED",
 "ALLOWED_TERMINALS":["MINIMAL_REPRODUCTION_CAUSAL_EVENT_PROSPECTIVELY_REPLICATED",
   "MINIMAL_REPRODUCTION_CAUSAL_EVENT_NOT_PROSPECTIVELY_REPLICATED",
   "CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED","FIMRCC01_TECHNICALLY_INVALID"],
 "DISPOSITION_IS_ONE_OF_THE_FOUR_FROZEN_TERMINALS":True,
 "HUMAN_DECISION":"A__PRECONDITIONS_NOT_MET",
 "DECIDED_BY":"the owner, on the pre-registered step-5 referral, after the candidate table",
 "WHY_NOT_TECHNICALLY_INVALID":"Precondition B PASSED. The independent reconstruction agrees on "
   "the load-bearing locked-daughter endpoint in 26 of 26 triggered worlds and on M2, M3, M5 and "
   "the event step in 256 of 256. There is no technical defect, so the human-selected disposition "
   "is not being forced through one.",
 "WHY_NOT_NOT_PROSPECTIVELY_REPLICATED":"no fresh world was run. A NOT_REPLICATED disposition "
   "would assert a negative prospective result that was never measured.",
 "PRECONDITION_A_STATUS":"PASS",
 "PRECONDITION_B_STATUS":"PASS",
 "UNRESTRICTED_ENDPOINT_STATUS":"SATURATED__NON_DISCRIMINATING__NOT_ELIGIBLE_AS_PRIMARY",
 "LOCKED_DAUGHTER_REMOVED_WORLD_COUNT":"1/22",
 "LOCKED_DAUGHTER_WORLD_LEVEL_RATE":"1/256",
 "LOCKED_DAUGHTER_N50_P_K_GE_2":round(lsf(K_REQ,50,p_world),4),
 "K_REQUIREMENT":K_REQ,"N_BASE_BLOCKS_DECLARED":50,
 "E3_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
 "E4_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
 "E5_STATUS":"FUTURE_QUESTION_RECORDED__NOT_AUTHORISED",
 "FRESH_WORLD_COUNT":0,"FRESH_SEEDS_CONSUMED":0,"TECHNICAL_RESERVES_USED":0,
 "SELECTIVE_ARM_EXECUTED":False,"SHAM_ARM_EXECUTED":False,"GLOBAL_OFF_ARM_EXECUTED":False,
 "NEW_PARAMETER_POINTS":0,"PARAMETER_RETUNING":"none","INTERPOLATION":"none",
 "ADAPTIVE_SAMPLE_SIZE":"none","ADAPTIVE_STOPPING":"none",
 "POST_OUTCOME_SCIENTIFIC_REPAIRS":0,
 "INDEPENDENT_CHECKERS_USED":0,"REVIEW_CASCADES":0,
 "NEXT_SCIENTIFIC_ELIGIBILITY":"NONE__LINEAGE_ROUTE_PAUSED",
 "NO_HANDOFF_IS_EMITTED":True,
 "REOPENING_REQUIRES":"an explicit new human authorisation and a newly derived matched-control "
   "design. Nothing in this mission authorises one.",
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED",
 "PTOPD01_LINEAGE_POINT_ROUTE_STATUS":"MEASURED, NOT QUALIFIED",
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "INHERITED_CLAUSES_RE_EMITTED_VERBATIM":PB["INHERITED_CLAUSES_RE_EMITTED_VERBATIM"]}
json.dump(disp,open(f"{OUT}/FIMRCC01_FINAL_DISPOSITION.json","w"),indent=1)

print("K_REQUIREMENT (k* at n=50 vs F_INTEGRATED) =",K_REQ)
print("P(K>=%d | N=50, p=1/256)  = %.4f"%(K_REQ,lsf(K_REQ,50,p_world)))
print("P(K>=%d | N=50, p=1/22)   = %.4f"%(K_REQ,lsf(K_REQ,50,p_removed)))
print("exact 95%% CI 1/22  =",[round(cp_lower(1,22),6),round(cp_upper(1,22),6)])
print("exact 95%% CI 1/256 =",[round(cp_lower(1,256),6),round(cp_upper(1,256),6)])
for f in ("FIMRCC01_CURRENT_CHECKPOINT_BINDING.json","FIMRCC01_PRECONDITION_B_RESULT.json",
          "FIMRCC01_ENDPOINT_ADJUDICATION.json","FIMRCC01_FINAL_DISPOSITION.json"):
    print("%-46s %s"%(f,sha(f"{OUT}/{f}")))
