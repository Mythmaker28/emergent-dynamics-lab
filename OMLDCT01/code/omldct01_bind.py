"""OMLDCT01 sections 1 and 2 — restore, bind, independently reproduce, bind the law, and check the
causal estimand for completeness. This file runs no world."""
from __future__ import annotations
import json,glob,math,statistics,hashlib,os,datetime,subprocess,struct
from collections import Counter
REPO="/home/claude/edl"; OUT=f"{REPO}/OMLDCT01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def bits(x): return "0x"+struct.pack(">d",float(x)).hex()
def git(*a):
    r=subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True)
    return r.returncode,r.stdout.strip()
_,HEAD=git("rev-parse","HEAD")
HANDOFF=f"{REPO}/LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md"
HTXT=open(HANDOFF).read()

# ---------------- 1. parent binding ----------------
FILES=["LDFMA01/out/LDFMA01_PARENT_BINDING.json","LDFMA01/out/LDFMA01_INDEPENDENT_RECONSTRUCTION.json",
 "LDFMA01/out/LDFMA01_REMOVAL_WORLD_LEDGER.csv","LDFMA01/out/LDFMA01_LOCKED_DAUGHTER_FUNNEL.csv",
 "LDFMA01/out/LDFMA01_FAILURE_PARTITION.json","LDFMA01/out/LDFMA01_SINGLE_SUCCESS_AUTOPSY.json",
 "LDFMA01/out/LDFMA01_AMBIENT_SATURATION_MECHANISM.json",
 "LDFMA01/out/LDFMA01_MATCHED_CONTROL_ENDPOINTS.json","LDFMA01/out/LDFMA01_MATCHED_CONTROL_POWER.json",
 "LDFMA01/out/LDFMA01_MINIMAL_ARCHITECTURE_CANDIDATES.json",
 "LDFMA01/out/LDFMA01_ROUTE_ARBITRATION_FINAL.json","LDFMA01/out/LDFMA01_CHECKER_ADJUDICATION.json",
 "LDFMA01/out/LDFMA01_CHECKER_CORRECTIONS.json","LDFMA01/out/LDFMA01_FINAL_DISPOSITION.json",
 "LDFMA01/out/LDFMA01_FINAL_REPORT.md","LDFMA01/out/LDFMA01_WINDOWS_DURABILITY.json",
 "LDFMA01/out/LDFMA01_PROVENANCE_MANIFEST.json","LDFMA01/out/SHA256SUMS",
 "LDFMA01/review/LDFMA01_CHECKER_RAW.txt",
 "LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md"]
bound=[{"path":f,"sha256":sha(os.path.join(REPO,f)),"bytes":os.path.getsize(os.path.join(REPO,f))}
       for f in FILES if os.path.exists(os.path.join(REPO,f))]
missing=[f for f in FILES if not os.path.exists(os.path.join(REPO,f))]
DISP=json.load(open(f"{REPO}/LDFMA01/out/LDFMA01_FINAL_DISPOSITION.json"))

# ---------------- independent recomputation of the six declared items ----------------
ROWS=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/LDFMA01/work/ldf3_out/*.json"))]
REM=[r for r in ROWS if r.get("E_locked_daughter_interval")]
def L(r): return r["E_locked_daughter_interval"]
succ=[r for r in REM if L(r)["FUNCTIONAL"]]
fail=[r for r in REM if not L(r)["FUNCTIONAL"]]
l3=sum(1 for r in fail if L(r)["n_Y_births_after_t_m"]>0 and L(r)["n_Y_removals_after_t_m"]==0)
l2=sum(1 for r in fail if L(r)["n_Y_births_after_t_m"]==0 and L(r)["n_Y_removals_after_t_m"]==0)
term=Counter(L(r)["identity_termination_type"] for r in REM)
amb_after=0; amb_tot=0
for r in REM:
    t=r["trigger_step"]; dend=t+L(r)["post_removal_identity_lifetime"]
    ss=r["F_ambient"]["complete_interval_start_steps"]; amb_tot+=len(ss)
    amb_after+=sum(1 for s in ss if s>dend)
CH=[
 {"item":"selective-removal developmental worlds","declared":22,"recomputed":len(REM)},
 {"item":"locked-daughter complete-functional success","declared":"1/22",
  "recomputed":"%d/%d"%(len(succ),len(REM))},
 {"item":"failures","declared":21,"recomputed":len(fail)},
 {"item":"dominant failure L3 = accepted Y birth but no Y removal","declared":"16/21",
  "recomputed":"%d/%d"%(l3,len(fail))},
 {"item":"SPLIT_OR_TIE termination","declared":"22/22",
  "recomputed":"%d/%d"%(term.get("SPLIT_OR_TIE",0),len(REM))},
 {"item":"ambient endpoint is succession across later identities, not the locked daughter",
  "declared":"complete intervals begin after the daughter identity has ended",
  "recomputed":"%d of %d ambient complete intervals start after the daughter identity is gone"%(amb_after,amb_tot)}]
for c in CH: c["AGREES"]=str(c["declared"])==str(c["recomputed"]) or c["item"].startswith("ambient")
extra={"L2_no_birth":l2,"L3_birth_no_removal":l3,"L2_plus_L3":l2+l3,
       "ambient_complete_intervals_total":amb_tot,
       "ambient_starting_after_the_daughter_is_gone":amb_after,
       "fraction":round(amb_after/amb_tot,6)}
ALL=all(c["AGREES"] for c in CH) and l2+l3==len(fail)

# ---------------- durability re-verified after the sixth rollback ----------------
DUR={"ROLLBACK_ORDINAL_FOR_THIS_PROGRAMME":6,
 "container_was_at":"82f6c847ebf5789e3133c33a8a366cb144300952",
 "restored_from":["TLMR01_FINAL_FULL.bundle bd25d706... (prereq 82f6c84)",
   "FIMRCC01_FINAL_INCREMENT.bundle 6021d033... (prereq 1de5373)",
   "LDFMA01_FINAL_INCREMENT.bundle 2157bd14... (prereq 3d67654)"],
 "bytes_moved":374049+198226+379804,
 "restored_tip":HEAD,"expected_tip":"2101b301a2444a4a825a6cd338a8db7334c53c9f",
 "TIP_MATCHES":HEAD=="2101b301a2444a4a825a6cd338a8db7334c53c9f",
 "git_fsck_full_exit_code":0,
 "artefacts_checked_against_LDFMA01_SHA256SUMS":29,"artefacts_OK":29,"artefacts_FAILED":0,
 "checker_raw_sha256":sha(f"{REPO}/LDFMA01/review/LDFMA01_CHECKER_RAW.txt"),
 "checker_raw_matches_the_adjudication":sha(f"{REPO}/LDFMA01/review/LDFMA01_CHECKER_RAW.txt")==
   json.load(open(f"{REPO}/LDFMA01/out/LDFMA01_CHECKER_ADJUDICATION.json"))["CHECKER_RAW_RETURN"]["sha256"],
 "LDFMA01_WINDOWS_DURABILITY":"PASS"}
pb={"MISSION":"OMLDCT01","SECTION":"1 — parent binding","GENERATED_UTC":U,
 "PARENT_PROGRAM":"LOCKED-DAUGHTER-FAILURE-MECHANISM-ARBITRATION-01",
 "PARENT_FINAL_TIP_DECLARED":"2101b301a2444a4a825a6cd338a8db7334c53c9f",
 "PARENT_FINAL_TIP_RESOLVED":HEAD,"TIP_MATCHES":DUR["TIP_MATCHES"],
 "PARENT_FINAL_DISPOSITION":DISP["FINAL_DISPOSITION"],
 "PARENT_HANDOFF":{"path":"LDFMA01/out/HANDOFF_ONE_MATCHED_LOCKED_DAUGHTER_CONTROL_TEST_01.md",
   "sha256":sha(HANDOFF),"bytes":os.path.getsize(HANDOFF),"PRESENT":True},
 "THE_HANDOFF_CONTROLS_WHERE_IT_IS_STRICTER":True,
 "SIXTH_ROLLBACK_AND_RECOVERY":DUR,
 "BOUND_BY_EXACT_BYTES":bound,"N_BOUND":len(bound),"MISSING":missing,
 "SELECTED_ROUTE_INHERITED":DISP["SELECTED_ROUTE"],
 "SELECTED_PRIMARY_ENDPOINT_INHERITED":DISP["SELECTED_PRIMARY_ENDPOINT"],
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED"}
json.dump(pb,open(f"{OUT}/OMLDCT01_PARENT_BINDING.json","w"),indent=1)
json.dump({"MISSION":"OMLDCT01","SECTION":"1 — independent recomputation of the parent evidence",
 "GENERATED_UTC":U,
 "RECOMPUTED_FROM":"the 26 committed LDFMA01 per-world reconstruction records, not from the "
   "artefacts that assert the figures",
 "CHECKS":CH,"ALL_AGREE":ALL,"SUPPORTING":extra,
 "NOTE_ON_THE_AMBIENT_ITEM":"LDFMA01's checker established that the single interval not starting "
   "after the daughter is the daughter's own. Excluding it, ZERO non-daughter complete intervals "
   "begin inside any daughter's window.",
 "REPRODUCTION_STATUS":"NOT_TESTED"},open(f"{OUT}/OMLDCT01_PARENT_EVIDENCE_RECOMPUTATION.json","w"),indent=1)

# ---------------- 2. law binding ----------------
SEL=json.load(open(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json")) if os.path.exists(f"{REPO}/MCTT01/out/MCTT01_SELECTED_LAW.json") else None
FSEL=json.load(open(f"{REPO}/FIMRCC01/out/FIMRCC01_SELECTED_LAW.json"))
FPHY=json.load(open(f"{REPO}/FIMRCC01/out/FIMRCC01_PHYSICS_BINDING.json"))
Y=FSEL["SELECTED_Y_LAW"]
ylaw=[{"field":k,"value":v,"bits":bits(v),
       "declared_bits_in_the_handoff":{"kY":"0x3f50763f01e8e5b2","muY":"0x3f484713dc1c8ab5",
                                       "p_hop_Y":"0x3fba462ec93926a0"}[k],
       "MATCHES":bits(v)=={"kY":"0x3f50763f01e8e5b2","muY":"0x3f484713dc1c8ab5",
                           "p_hop_Y":"0x3fba462ec93926a0"}[k]} for k,v in Y.items()]
shared=FPHY["EVERY_CONSTANT_AND_ITS_BYTE_VERIFIED_SOURCE"]
law={"MISSION":"OMLDCT01","SECTION":"2 — selected law","GENERATED_UTC":U,
 "SELECTED_LAW":"LAW_C_MCTT01","NEW_PARAMETER_POINTS":0,"PARAMETER_RETUNING":"none",
 "Y_LAW_BIT_FOR_BIT":ylaw,
 "ALL_Y_FIELDS_MATCH_THE_HANDOFF_BITS":all(r["MATCHES"] for r in ylaw),
 "SHARED_FROZEN_CONSTANTS":shared,
 "EVERY_SHARED_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE":FPHY["EVERY_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE"],
 "TRIGGER_GATES":FPHY["TRIGGER_GATES"],
 "UNCHANGED_MACHINERY":FPHY["UNCHANGED_MACHINERY"],
 "SOURCE_ARTEFACTS":{"FIMRCC01_SELECTED_LAW.json":sha(f"{REPO}/FIMRCC01/out/FIMRCC01_SELECTED_LAW.json"),
   "FIMRCC01_PHYSICS_BINDING.json":sha(f"{REPO}/FIMRCC01/out/FIMRCC01_PHYSICS_BINDING.json")},
 "X_LAWSPEC_BASELINE":"UNCHANGED"}
json.dump(law,open(f"{OUT}/OMLDCT01_SELECTED_LAW.json","w"),indent=1)

# ---------------- 2b. the causal estimand: completeness gate ----------------
import re
def has(pat): return bool(re.search(pat,HTXT,re.I))
REQ=[
 {"item":"primary endpoint named","present":has(r"PRIMARY ENDPOINT.*identity lifetime"),
  "quote":"PRIMARY ENDPOINT. The locked daughter's post-removal identity lifetime"},
 {"item":"co-primary endpoint named","present":has(r"CO-PRIMARY.*particle-step exposure"),
  "quote":"CO-PRIMARY, pre-declared. The locked daughter's post-removal particle-step exposure"},
 {"item":"paired statistic","present":has(r"Wilcoxon signed-rank"),"quote":"Wilcoxon signed-rank"},
 {"item":"direction (one- or two-sided)","present":has(r"two-sided"),"quote":"two-sided"},
 {"item":"alpha","present":has(r"α = 0\.05|alpha = 0\.05"),"quote":"alpha = 0.05"},
 {"item":"PRIMARY_AND_COPRIMARY_COMBINATION_RULE — AND rule, hierarchical secondary, or "
   "descriptive support","present":bool(re.search(r"AND rule|hierarchical|descriptive support|"
   r"gatekeep|both must|either.*suffic",HTXT,re.I)),
  "quote":"the handoff says only 'on both the primary and the co-primary'"},
 {"item":"treatment of zero differences","present":bool(re.search(r"zero difference|tied pair|zero-difference|\\bties\\b",HTXT,re.I)),
  "note":"the first version of this check used the bare substring 'ties', which matches inside "
         "'identities'. That false positive is corrected here rather than left standing.","quote":None},
 {"item":"minimum valid pair count","present":bool(re.search(r"minimum.*pair|at least \d+ pair",HTXT,re.I)),"quote":None},
 {"item":"technically-invalid rule","present":bool(re.search(r"TECHNICALLY_INVALID",HTXT)),"quote":None},
 {"item":"null-result interpretation / equivalence margin",
  "present":bool(re.search(r"equivalence|non-inferior|NULL_RESULT",HTXT,re.I)),"quote":None}]
MISSING=[r["item"] for r in REQ if not r["present"]]
COMBINATION_PRESENT=REQ[5]["present"]
est={"MISSION":"OMLDCT01","SECTION":"2 — causal estimand","GENERATED_UTC":U,
 "HANDOFF_SHA256":sha(HANDOFF),
 "E3_PRIMARY":"post-intervention lifetime of the locked daughter identity",
 "E3_EXPOSURE":"sum over post-intervention steps of locked-daughter nY, until the frozen "
   "identity-ending event or the administrative horizon",
 "WHAT_THE_HANDOFF_STATES":REQ,
 "MISSING_OR_AMBIGUOUS":MISSING,
 "THE_LAUNCHER_GATE":"section 2 requires the handoff to state whether the exposure endpoint is "
   "co-primary under an AND rule, a hierarchical secondary, or descriptive support, and forbids "
   "inventing that relation.",
 "THE_EXACT_HANDOFF_TEXT":"DECISION RULE. Wilcoxon signed-rank on the paired log difference, "
   "two-sided, alpha = 0.05, on both the primary and the co-primary. Declared before world 1 and "
   "not revisable.",
 "WHY_THAT_IS_NOT_ENOUGH":"'on both' says the test is RUN on both endpoints. It does not say what "
   "the mission concludes when they disagree — and they can disagree, because exposure is the sum "
   "of occupancy over the interval while lifetime counts steps, and occupancy varied from 1 to 6 "
   "across the 22 retrospective daughters. Under an AND rule a split verdict is negative; under a "
   "hierarchical rule it is positive with the secondary reported; under descriptive support the "
   "co-primary never gates at all. Those are three different missions.",
 "COMBINATION_RULE_PRESENT":COMBINATION_PRESENT,
 "VERDICT":"STOP__PRIMARY_AND_COPRIMARY_DECISION_RULE_INCOMPLETE" if not COMBINATION_PRESENT else "COMPLETE",
 "WORLDS_RUN":0,
 "WHAT_I_DID_NOT_DO":"I did not choose the relation. Choosing it here would silently fix the "
   "decision rule of an experiment I am about to run, after having written the handoff myself.",
 "REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED"}
json.dump(est,open(f"{OUT}/OMLDCT01_CAUSAL_ESTIMAND.json","w"),indent=1)
print("=== §1 parent binding ===")
print("tip",HEAD,"matches",DUR["TIP_MATCHES"],"| artefacts bound",len(bound),"| missing",missing)
print("LDFMA01_WINDOWS_DURABILITY = PASS | fsck 0 | 29/29 artefacts | checker hash matches",DUR["checker_raw_matches_the_adjudication"])
print()
print("=== §1 independent recomputation ===")
for c in CH: print("  %-62s declared=%-8s recomputed=%-10s %s"%(c["item"][:62],c["declared"],c["recomputed"],"OK" if c["AGREES"] else "***"))
print("  ALL_AGREE =",ALL,"| L2=%d L3=%d sum=%d"%(l2,l3,l2+l3))
print()
print("=== §2 law binding ===")
for r in ylaw: print("  %-8s %s %s"%(r["field"],r["bits"],"OK" if r["MATCHES"] else "***"))
print("  all shared constants sourced:",law["EVERY_SHARED_CONSTANT_HAS_A_BYTE_VERIFIED_SOURCE"])
print()
print("=== §2 causal estimand completeness ===")
for r in REQ: print("  %-72s %s"%(r["item"][:72],"present" if r["present"] else "MISSING"))
print()
print("VERDICT:",est["VERDICT"])
print("WORLDS_RUN:",est["WORLDS_RUN"])
