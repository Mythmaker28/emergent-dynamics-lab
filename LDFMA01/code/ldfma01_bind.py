"""LDFMA01 Section 1 — bind the accepted TLMR01 / FIMRCC01 record by exact bytes.

Every count below is RECOMPUTED from the committed per-world records, not read from the headline
artefacts that assert it. Where a recomputation and an assertion disagree, both are printed and the
binding fails; nothing is smoothed.
"""
from __future__ import annotations
import json, glob, math, hashlib, os, datetime, subprocess, statistics
REPO="/home/claude/edl"; OUT=f"{REPO}/LDFMA01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def git(*a):
    r=subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True)
    return r.returncode,r.stdout.strip()

# ---------- the bound artefacts, by exact bytes ----------
GROUPS={
 "TLMR01_final_raw_package":["TLMR01/out/TLMR01_RAW_MANIFEST.json","TLMR01/out/TLMR01_RAW_SHA256SUMS",
   "TLMR01/out/TLMR01_ARCHIVE_MANIFEST.json","TLMR01/out/TLMR01_ARCHIVE_SHA256SUMS",
   "TLMR01/out/TLMR01_RUN_LEDGER.jsonl","TLMR01/out/TLMR01_READ_BACK.jsonl"],
 "TLMR01_final_analysis_and_selection":["TLMR01/out/TLMR01_ANALYSIS.json",
   "TLMR01/out/TLMR01_WORLD_RESULTS.json","TLMR01/out/TLMR01_MEASUREMENT_LAWS.json",
   "TLMR01/out/TLMR01_SELECTION_RULE.json","TLMR01/out/TLMR01_MASTER_FREEZE.json",
   "TLMR01/out/TLMR01_METHODS_CLOSURE.json","TLMR01/out/TLMR01_FINAL_REPORT.md"],
 "TLMR01_checker_and_adjudication":["TLMR01/out/TLMR01_CHECKER_ADJUDICATION.json",
   "TLMR01/out/TLMR01_CHECKER_CORRECTIONS.json","TLMR01/out/TLMR01_FINAL_DISPOSITION.json",
   "TLMR01/out/TLMR01_DEVICE_PATH_CROSSCHECK.json","TLMR01/out/TLMR01_RECOVERY_INCIDENT.json"],
 "FIMRCC01_checkpoint":["FIMRCC01/out/FIMRCC01_CURRENT_CHECKPOINT_BINDING.json",
   "FIMRCC01/out/FIMRCC01_PARENT_BINDING.json","FIMRCC01/out/FIMRCC01_SELECTED_LAW.json",
   "FIMRCC01/out/FIMRCC01_PHYSICS_BINDING.json",
   "FIMRCC01/out/FIMRCC01_P2_LAW_BINDING_REVERIFICATION.json"],
 "FIMRCC01_precondition_A":["FIMRCC01/out/FIMRCC01_PRECONDITION_A_RULE.json",
   "FIMRCC01/out/FIMRCC01_LOCKED_IDENTITY_QUALIFICATION.json"],
 "FIMRCC01_precondition_B":["FIMRCC01/out/FIMRCC01_INDEPENDENT_ENDPOINT_QUALIFICATION.json",
   "FIMRCC01/out/FIMRCC01_PRECONDITION_B_RESULT.json","FIMRCC01/out/FIMRCC01_PRECONDITION_B_RESULT.md"],
 "FIMRCC01_endpoint_adjudication":["FIMRCC01/out/FIMRCC01_ENDPOINT_PREREGISTRATION.json",
   "FIMRCC01/out/FIMRCC01_ENDPOINT_TABLE.json","FIMRCC01/out/FIMRCC01_ENDPOINT_ADJUDICATION.json",
   "FIMRCC01/out/FIMRCC01_ENDPOINT_ADJUDICATION.md"],
 "FIMRCC01_final_report":["FIMRCC01/out/FIMRCC01_FINAL_REPORT.md",
   "FIMRCC01/out/FIMRCC01_PRECONDITION_CLOSURE_REPORT.md"],
 "FIMRCC01_final_disposition":["FIMRCC01/out/FIMRCC01_FINAL_DISPOSITION.json",
   "FIMRCC01/out/FIMRCC01_WINDOWS_DURABILITY.json","FIMRCC01/out/SHA256SUMS"]}
bound={}; missing=[]
for g,fs in GROUPS.items():
    rows=[]
    for f in fs:
        p=os.path.join(REPO,f)
        if os.path.exists(p): rows.append({"path":f,"sha256":sha(p),"bytes":os.path.getsize(p)})
        else: missing.append(f); rows.append({"path":f,"sha256":None,"MISSING":True})
    bound[g]=rows

# ---------- independent recomputation from the per-world records ----------
PA=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pa_out/*.json"))]
PB=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pb3/*.json"))]
PD=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pbd/*.json"))]

law_c        = len(PA)
triggered    = sum(1 for r in PA if r["n_triggered"]>0)
removed      = [r for r in PA if r["removal_applied"]]
n_removed    = len(removed)
ambient_fun  = sum(1 for r in removed if (r["DAUGHTER"] or {}).get("unrestricted_endpoint",{}).get("FUNCTIONAL"))
ambient_tot  = sum((r["DAUGHTER"] or {}).get("unrestricted_endpoint",{}).get("n_complete",0) for r in removed)
ambient_med  = statistics.median([(r["DAUGHTER"] or {}).get("unrestricted_endpoint",{}).get("n_complete",0) for r in removed])
locked_fun   = sum(1 for r in removed if (r["DAUGHTER"] or {}).get("daughter_endpoint",{}).get("FUNCTIONAL"))

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
K=kstar(50); PK=lsf(K,50,1/256)

DISP=json.load(open(f"{REPO}/FIMRCC01/out/FIMRCC01_FINAL_DISPOSITION.json"))
CHECKS=[
 {"quantity":"LAW_C primary worlds","declared":256,"recomputed":law_c,
  "recomputed_from":"count of FIMRCC01/work/pa_out per-world records"},
 {"quantity":"triggered worlds","declared":26,"recomputed":triggered,
  "recomputed_from":"per-world n_triggered > 0"},
 {"quantity":"selective-removal worlds","declared":22,"recomputed":n_removed,
  "recomputed_from":"per-world removal_applied"},
 {"quantity":"unrestricted ambient-population endpoint","declared":"22/22",
  "recomputed":"%d/%d"%(ambient_fun,n_removed),
  "recomputed_from":"per-world unrestricted_endpoint.FUNCTIONAL"},
 {"quantity":"complete identity intervals","declared":2018,"recomputed":ambient_tot,
  "recomputed_from":"sum of per-world unrestricted_endpoint.n_complete"},
 {"quantity":"median complete intervals per removed world","declared":93,"recomputed":ambient_med,
  "recomputed_from":"median of the same per-world counts"},
 {"quantity":"locked-daughter complete-functional events","declared":"1/22",
  "recomputed":"%d/%d"%(locked_fun,n_removed),
  "recomputed_from":"per-world daughter_endpoint.FUNCTIONAL"},
 {"quantity":"locked-daughter world-level events","declared":"1/256",
  "recomputed":"%d/%d"%(locked_fun,law_c),"recomputed_from":"the same, over all LAW_C worlds"},
 {"quantity":"P(K >= 2 | N=50, p=1/256)","declared":0.0165,"recomputed":round(PK,4),
  "recomputed_from":"exact one-sided binomial, k* recomputed against F_INTEGRATED"},
 {"quantity":"fresh worlds used by FIMRCC01","declared":0,"recomputed":DISP["FRESH_WORLD_COUNT"],
  "recomputed_from":"FIMRCC01_FINAL_DISPOSITION"}]
for c in CHECKS:
    d,r=c["declared"],c["recomputed"]
    c["AGREES"]=(str(d)==str(r)) or (isinstance(d,(int,float)) and isinstance(r,(int,float)) and abs(float(d)-float(r))<5e-5)
ALL_AGREE=all(c["AGREES"] for c in CHECKS)

# second, harder cross-check: the same numbers from the OTHER two per-world record sets
pb_agree=sum(1 for r in PB if r["ALL_AGREE"])
pd_removed=[r for r in PD if r.get("ENDPOINT")]
pd_locked=sum(1 for r in pd_removed if r["ENDPOINT"]["FUNCTIONAL"])
pd_ambient=sum(1 for r in pd_removed if r["ENDPOINT"]["ambient_FUNCTIONAL"])
pd_ambient_tot=sum(r["ENDPOINT"]["ambient_n_complete"] for r in pd_removed)

_,HEAD=git("rev-parse","HEAD")
art={
 "MISSION":"LDFMA01","SECTION":"1 — parent binding","GENERATED_UTC":U,
 "PARENT_PROGRAM":"FRESH-INTEGRATED-MINIMAL-REPRODUCTION-CAUSAL-CONFIRMATION-01",
 "PARENT_FINAL_TIP_DECLARED":"3d67654fc5cfa7e5502c4d7e93b13c090d735263",
 "PARENT_FINAL_TIP_RESOLVED":HEAD,
 "TIP_MATCHES":HEAD=="3d67654fc5cfa7e5502c4d7e93b13c090d735263",
 "PARENT_FINAL_DISPOSITION":DISP["FINAL_DISPOSITION"],
 "BOUND_BY_EXACT_BYTES":bound,
 "N_ARTEFACTS_BOUND":sum(len(v) for v in bound.values()),
 "MISSING_ARTEFACTS":missing,
 "INDEPENDENT_VERIFICATION":CHECKS,
 "ALL_DECLARED_COUNTS_REPRODUCE":ALL_AGREE,
 "SECOND_CROSS_CHECK_FROM_THE_OTHER_RECORD_SETS":{
   "precondition_B_worlds_with_full_agreement":"%d/%d"%(pb_agree,len(PB)),
   "descent_audit_worlds_with_an_endpoint":len(pd_removed),
   "locked_daughter_FUNCTIONAL_from_the_descent_audit":"%d/%d"%(pd_locked,len(pd_removed)),
   "ambient_FUNCTIONAL_from_the_descent_audit":"%d/%d"%(pd_ambient,len(pd_removed)),
   "ambient_complete_intervals_from_the_descent_audit":pd_ambient_tot,
   "AGREES_WITH_THE_PRIMARY_RECOMPUTATION":bool(pd_locked==locked_fun and pd_ambient==ambient_fun
                                                and pd_ambient_tot==ambient_tot)},
 "PRESERVED_PERMANENTLY":{
   "TLMR01_ambient_population_result":"VALID DEVELOPMENTAL RESULT FOR A BROADER POPULATION OBJECT",
   "WHAT_THE_22_OF_22_IS":"a true statement that at least one identity somewhere in the world "
     "completed a constituent turnover after the removal, in every world that received one.",
   "WHAT_THE_22_OF_22_IS_NOT":"it does not measure the locked daughter. The identity the frozen "
     "code names as the daughter satisfies the same endpoint in 1 of those 22 worlds.",
   "IT_IS_NOT_CALLED_FALSE":True,
   "FIMRCC01_final_disposition":"CONFIRMATION_PRECONDITIONS_NOT_MET__LINEAGE_ROUTE_PAUSED"},
 "LAUNCHER_CONSTRAINTS":{
   "NEW_SCIENTIFIC_ENGINE_RUNS":0,"NEW_WORLD_CONSTRUCTIONS":0,"NEW_SEEDS":0,"NEW_TRAJECTORIES":0,
   "PARAMETER_SWEEP":"forbidden","INTERPOLATION":"forbidden","RESPONSE_SURFACE":"forbidden",
   "POST_OUTCOME_ENDPOINT_SELECTION":"forbidden",
   "MAX_ROUTE_CANDIDATES":3,"MAX_SELECTED_ROUTES":1,"MAX_INTENTIONAL_COMMITS":4,
   "MAX_INDEPENDENT_CHECKERS":1,"REVIEW_CASCADE":"forbidden"},
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED"}
json.dump(art,open(f"{OUT}/LDFMA01_PARENT_BINDING.json","w"),indent=1)
for c in CHECKS:
    print("%-46s declared=%-8s recomputed=%-8s %s"%(c["quantity"][:46],c["declared"],c["recomputed"],
          "OK" if c["AGREES"] else "*** DISAGREES ***"))
print()
print("artefacts bound:",art["N_ARTEFACTS_BOUND"],"| missing:",len(missing),missing[:4])
print("tip matches      :",art["TIP_MATCHES"])
print("ALL_DECLARED_COUNTS_REPRODUCE =",ALL_AGREE)
print("second cross-check agrees     =",art["SECOND_CROSS_CHECK_FROM_THE_OTHER_RECORD_SETS"]["AGREES_WITH_THE_PRIMARY_RECOMPUTATION"])
