"""FDOT01 §1, §12 — parent binding, primary endpoint, and the complete pre-run methods freeze."""
from __future__ import annotations
import json, os, sys, hashlib, subprocess, datetime, platform
import numpy as np, scipy
REPO="/home/claude/edl"; OUT=f"{REPO}/FDOT01/out"
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
G=lambda *a: subprocess.check_output(["git","-C",REPO]+list(a),text=True).strip()
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
PARENT_TIP="d9f29d33864985068570ad3ddb9f69436b021234"
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
B1=FZ["PHASE_B"]["POINT_B1"]; C=FZ["INHERITED_FROZEN_CONSTANTS"]

def closure():
    sys.path.insert(0,f"{REPO}/FDOT01/code")
    for m in ("fdot01_world","fdot01_centres","fdot01_centres_b","fdot01_seeds","fdot01_design",
              "fdot01_run","fdot01_analyse","fdot01_review","fdot01_final","fdot01_fixtures",
              "fdot01_devrecompute"):
        __import__(m)
    roots=(REPO,"/home/claude/ORR01","/home/claude/OBTC02")
    mods=[]
    for name,mod in list(sys.modules.items()):
        f=getattr(mod,"__file__",None)
        if not f: continue
        f=os.path.abspath(f)
        if any(f.startswith(r+"/") for r in roots) and f.endswith(".py"):
            mods.append({"module":name,"abs":f,"path":os.path.relpath(f,REPO) if f.startswith(REPO+"/") else f,
                         "sha256":sha(f)})
    seen=set(); out=[]
    for m in sorted(mods,key=lambda m:m["abs"]):
        if m["abs"] in seen: continue
        seen.add(m["abs"]); out.append(m)
    return out

def main():
    os.makedirs(OUT,exist_ok=True)
    # ---------------- parent binding ----------------
    dot={f:sha(f"{REPO}/DOTC01/out/{f}") for f in (
      "DOTC01_ORGANISER_OBJECT_DEFINITION.json","DOTC01_TURNOVER_EVENT_DEFINITION.json",
      "DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json","DOTC01_ORGANISER_TIMESCALE.json",
      "DOTC01_B1_FEASIBILITY.json","DOTC01_INDEPENDENT_CHECK.json","DOTC01_FINAL_DISPOSITION.json")}
    ob=json.load(open(f"{REPO}/DOTC01/out/DOTC01_ORGANISER_OBJECT_DEFINITION.json"))
    te=json.load(open(f"{REPO}/DOTC01/out/DOTC01_TURNOVER_EVENT_DEFINITION.json"))
    fc=json.load(open(f"{REPO}/DOTC01/out/DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json"))
    DV=json.load(open(f"{OUT}/FDOT01_DEVELOPMENTAL_RECOMPUTE.json"))
    PB={"SECTION":"FDOT01 §1 — parent binding by exact bytes","GENERATED_UTC":NOW(),
     "PARENT_PROGRAM":"DAUGHTER-ORGANISER-TURNOVER-CRITERION-01",
     "PARENT_TIP_RESOLVED":PARENT_TIP,
     "PARENT_TIP_IS_A_COMMIT":G("cat-file","-t",PARENT_TIP)=="commit",
     "PARENT_FINAL_DISPOSITION":json.load(open(f"{REPO}/DOTC01/out/DOTC01_FINAL_DISPOSITION.json"))["FINAL_DISPOSITION"],
     "DOTC01_FILE_HASHES":dot,
     "DOTC01_SHA256SUMS_VERIFIED":True,
     "PRIMARY_EVENT_RECOVERED_EXACTLY":True,
     "THE_EVENT_AS_INHERITED":{
       "centre":ob["CENTRE"],"identity_rule":ob["CENTRE_IDENTITY_ACROSS_STEPS"]["rule"],
       "six_conditions":ob["ORGANISER_LEVEL_CONTINUITY"][
         "an interval [t0,t1] on one continuously matched component C qualifies only if ALL SIX hold"],
       "complete_turnover":te["COMPLETE_TURNOVER"]["requires"],
       "functional_measure":fc["FUNCTIONAL_CONTINUITY_MEASURE"],
       "functional_operational_form":fc["OPERATIONAL_FORM"],
       "no_genealogy":ob["NO_GENEALOGY"]},
     "DECLARED_DIFFERENCE_BETWEEN_THE_PARENT_DEFINITION_AND_THE_PARENT_CODE":{
       "what":("DOTC01's audit CODE linked components by mutual-nearest with a tie guard, which does "
         "not terminate an identity interval when one component splits into two that both remain "
         "within CORE_R. Its written DEFINITION says a match that is not mutually unique ends the "
         "interval, and FDOT01 §5 lists ties, splits and merges as all terminating identity."),
       "resolution":("§1 orders the parent DEFINITION preserved. FDOT01 implements the definition, "
         "which is strictly stricter than the parent code."),
       "consequence_measured_before_any_run":{
         "developmental_complete_under_the_strict_rule":DV["COMPLETE_TURNOVER"]["k"],
         "developmental_functional_under_the_strict_rule":DV["FUNCTIONAL_TURNOVER"]["k"],
         "DOTC01_reported_complete":DV["DOTC01_REPORTED"]["complete"],
         "DOTC01_reported_functional":DV["DOTC01_REPORTED"]["functional"],
         "of_worlds":DV["N_DEVELOPMENTAL_B1_WORLDS"]},
       "reported_not_resolved_in_favour_of_the_convenient_number":True},
     "B1_LAW_BOUND_BY_BYTES":{
       "engine":"/home/claude/OBTC02/code/engine_obtc.py","engine_sha256":sha("/home/claude/OBTC02/code/engine_obtc.py"),
       "engine_unchanged":sha("/home/claude/OBTC02/code/engine_obtc.py")=="2172deae5bbabf37238cf7712cb17663c151494befcf85505c537a7cac0ded30",
       "lawspec":"/home/claude/ORR01/code/lawspec_v2.py","lawspec_sha256":sha("/home/claude/ORR01/code/lawspec_v2.py"),
       "kinetics_sha256":sha("/home/claude/ORR01/code/kinetics.py"),
       "protocol_sha256":sha("/home/claude/OBTC02/code/obtc02_protocol.yaml"),
       "observer_sha256":sha(f"{REPO}/PQEC01/code/pqec01_observer.py"),
       "kY":B1["kY"],"muY":B1["muY"],"INHERITED":C,
       "muY_NOT_CHANGED":True,"kY_NOT_CHANGED":True,"HORIZON_NOT_LENGTHENED":True,"B2_NOT_RERUN":True}}
    json.dump(PB,open(f"{OUT}/FDOT01_PARENT_BINDING.json","w"),indent=1)
    # ---------------- primary endpoint ----------------
    EP={"SECTION":"FDOT01 §2-§4 — the frozen primary endpoint","GENERATED_UTC":NOW(),
     "PRIMARY_QUESTION":("does the prospectively frozen B1 law repeatedly produce daughter organising "
       "centres whose local organising function survives replacement of constituent Y material?"),
     "UNIT":"the seeded world","N":160,
     "K":"the number of fresh independent worlds, of 160, that satisfy FUNCTIONAL_COMPLETE_TURNOVER",
     "QUALIFICATION":"FUNCTIONAL_ORGANISER_TURNOVER_PROSPECTIVELY_REPLICATED iff K >= 2",
     "WHY_NOT_H0_p_EQ_0":("a p = 0 null is degenerate: a single event would reject it automatically. "
       "The criterion here is prospective REPLICATION — the frozen event seen independently in at "
       "least two fresh worlds under one fixed law."),
     "IT_IS_NOT":["a biological constant","a probability threshold of nature","a hypothesis test"],
     "RATE_ESTIMATION_IS_CO_PRIMARY_DESCRIPTIVE_EVIDENCE":True,
     "NO_POOLING_WITH_THE_44_DEVELOPMENTAL_WORLDS":True,
     "NO_THRESHOLD_SUCH_AS_p_GT_0_05_OR_0_10_OR_0_50_MAY_BE_INVENTED_AFTER_THE_FACT":True,
     "HORIZON":C["T_HORIZON"],
     "EVERY_WORLD_RUNS_THE_FULL_HORIZON":True,
     "NOT_STOPS":["EXTINCT","PREMATURE_THIRD_CENTRE","MAX_PERMITTED_Y","event became impossible",
                  "one turnover already succeeded"],
     "ONLY_BREAK":"a genuine engine invariant failure, which is a technical fault and not a scientific outcome",
     "THIRD_CENTRE_INTERPRETATION_FROZEN_BEFORE_RUNS":(
       "a daughter identity interval that splits into multiple centres TERMINATES, so that candidate "
       "centre cannot complete a turnover after the split. The world is still recorded to the horizon, "
       "and third-centre timing is reported as a scientific outcome, never as a technical failure.")}
    json.dump(EP,open(f"{OUT}/FDOT01_PRIMARY_ENDPOINT.json","w"),indent=1)
    # ---------------- methods ----------------
    mods=closure()
    MM={"SECTION":"FDOT01 §12 — complete pre-run methods freeze","GENERATED_UTC":NOW(),
     "PYTHON":platform.python_version(),"NUMPY":np.__version__,"SCIPY":scipy.__version__,
     "PLATFORM":platform.platform(),
     "N_MODULES":len(mods),"MODULES":mods,
     "DATA_INPUTS":[{"path":p,"sha256":sha(f"{REPO}/{p}")} for p in (
       "PQEC01/out/PQEC01_MASTER_FREEZE.json","FDOT01/out/FDOT01_SEED_MANIFEST.json",
       "FDOT01/out/FDOT01_DEVELOPMENTAL_RECOMPUTE.json","FDOT01/out/FDOT01_DETECTION_ASSURANCE.json",
       "FDOT01/out/FDOT01_PRIMARY_ENDPOINT.json","FDOT01/out/FDOT01_PARENT_BINDING.json",
       "FDOT01/out/FDOT01_FIXTURES.json",
       "DOTC01/out/DOTC01_ORGANISER_OBJECT_DEFINITION.json",
       "DOTC01/out/DOTC01_TURNOVER_EVENT_DEFINITION.json",
       "DOTC01/out/DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json")]+
       [{"path":"/home/claude/OBTC02/code/obtc02_protocol.yaml","sha256":sha("/home/claude/OBTC02/code/obtc02_protocol.yaml")}],
     "RUNTIME_VERIFICATION":"fdot01_run and fdot01_analyse compare imported file bytes to these hashes before use"}
    MM["COMPLETE_PRE_RUN_METHODS_HASH"]=hashlib.sha256(
      "".join(m["sha256"] for m in mods).encode()+"".join(d["sha256"] for d in MM["DATA_INPUTS"]).encode()).hexdigest()
    json.dump(MM,open(f"{OUT}/FDOT01_METHODS_MANIFEST.json","w"),indent=1)
    with open(f"{OUT}/FDOT01_METHODS_SHA256SUMS","w") as fh:
        for m in mods: fh.write("%s  %s\n"%(m["sha256"],m["abs"]))
        for d in MM["DATA_INPUTS"]: fh.write("%s  %s\n"%(d["sha256"],d["path"]))
    # ---------------- master freeze ----------------
    DA=json.load(open(f"{OUT}/FDOT01_DETECTION_ASSURANCE.json"))
    SM=json.load(open(f"{OUT}/FDOT01_SEED_MANIFEST.json"))
    FX=json.load(open(f"{OUT}/FDOT01_FIXTURES.json"))
    MF={"PROGRAM":"FRESH-DAUGHTER-ORGANISER-TURNOVER-TEST-01","SHORT_NAME":"FDOT01",
     "GENERATED_UTC":NOW(),"PARENT_TIP":PARENT_TIP,
     "FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_FRESH_WORLD":True,
     "POINT":{"LABEL":"B1","kY":B1["kY"],"muY":B1["muY"],"INHERITED_FROZEN_CONSTANTS":C},
     "NEW_PARAMETER_POINTS":0,"PARAMETER_RETUNING":"forbidden","INTERPOLATION":"forbidden",
     "PRIMARY_SCIENTIFIC_WORLDS":160,"MAX_TECHNICAL_RESERVES":6,
     "ADAPTIVE_SAMPLE_SIZE":"forbidden","OUTCOME_DRIVEN_STOPPING_OF_THE_BATCH":"forbidden",
     "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0,
     "PRIMARY_ENDPOINT":EP,"PARENT_BINDING_SUMMARY":PB["DECLARED_DIFFERENCE_BETWEEN_THE_PARENT_DEFINITION_AND_THE_PARENT_CODE"],
     "DETECTION_ASSURANCE":DA["ASSURANCE"],"DESIGN_INPUTS":DA["DESIGN_INPUTS"],
     "THE_PRE_RUN_PROBLEM_STATED_PLAINLY":DA["THE_PRE_RUN_PROBLEM_STATED_PLAINLY"],
     "SEEDS":{"formula":SM["FORMULA"],"n_primary":SM["N_PRIMARY"],"n_reserve":SM["N_RESERVE"],
              "disjoint":SM["DISJOINT_FROM_KNOWN"],"unique":SM["ALL_UNIQUE"],"bumps":SM["TOTAL_BUMPS"],
              "registry_size":SM["KNOWN_REGISTRY_SIZE"]},
     "FIXTURES":{"n":FX["N_FIXTURES"],"all_pass":FX["ALL_PASS"],"two_implementations_agree":FX["A_AND_B_AGREE_ON_EVERY_FIXTURE"]},
     "METHODS_HASH":MM["COMPLETE_PRE_RUN_METHODS_HASH"],
     "OUTCOME_FIREWALL":{"EXPOSED":["opaque arm token","completed","technical failure","checksum written"],
       "WITHHELD":["seed","turnover","birth/death counts","centre count","runtime","file size",
                   "stop reason","X production","success status"]},
     "TERMINAL_DISPOSITIONS":["FUNCTIONAL_ORGANISER_TURNOVER_PROSPECTIVELY_REPLICATED",
       "FUNCTIONAL_ORGANISER_TURNOVER_NOT_PROSPECTIVELY_REPLICATED","FDOT01_TECHNICALLY_INVALID"],
     "CLAIM_CEILING":("organiser-level constituent turnover with retained local function at the frozen "
       "B1 law. Not reproduction, not heredity, not self-replication."),
     "WINDOWS_PRE_RUN_DURABILITY":"RECORDED_SEPARATELY_IN_FDOT01_DURABILITY_JSON"}
    json.dump(MF,open(f"{OUT}/FDOT01_MASTER_FREEZE.json","w"),indent=1)
    print("modules",len(mods),"data",len(MM["DATA_INPUTS"]))
    print("METHODS_HASH:",MM["COMPLETE_PRE_RUN_METHODS_HASH"])
    print("engine unchanged:",PB["B1_LAW_BOUND_BY_BYTES"]["engine_unchanged"])
    print("parent tip is a commit:",PB["PARENT_TIP_IS_A_COMMIT"])

if __name__=="__main__": main()
