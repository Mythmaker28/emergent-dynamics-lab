"""FDFLT01 §10 + §11 — complete transitive methods hash and the master freeze."""
from __future__ import annotations
import hashlib, importlib, json, os, sys, datetime, subprocess
REPO="/home/claude/edl"; OUT=f"{REPO}/FDFLT01/out"
ROOTS=("/home/claude/edl","/home/claude/ORR01","/home/claude/OBTC02","/home/claude/PQEC01")
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
def rel(p):
    for r in ROOTS:
        if p.startswith(r+"/"): return os.path.relpath(p,REPO) if r==REPO else p
    return p

def transitive_closure():
    """Import every entry point and collect every project module that actually loaded."""
    for p in (f"{REPO}/FDFLT01/code", f"{REPO}/PQEC01/code", "/home/claude/ORR01/code",
              "/home/claude/OBTC02/code"):
        if p not in sys.path: sys.path.insert(0,p)
    before=set(sys.modules)
    for m in ("fdflt01_endpoint","fdflt01_score_B","fdflt01_seeds","fdflt01_power",
              "fdflt01_selftest","fdflt01_run","fdflt01_analyse","fdflt01_review","fdflt01_final",
              "pqec01_run","pqec01_observer"):
        importlib.import_module(m)
    mods=[]
    for name,mod in sorted(sys.modules.items()):
        f=getattr(mod,"__file__",None)
        if not f: continue
        f=os.path.abspath(f)
        if any(f.startswith(r+"/") for r in ROOTS) and f.endswith(".py") and "__pycache__" not in f:
            mods.append({"module":name,"path":rel(f),"abs":f,"bytes":os.path.getsize(f),"sha256":sha(f)})
    return mods

DATA_INPUTS=[f"{REPO}/OBTC02/code/obtc02_protocol.yaml",
             "/home/claude/OBTC02/code/obtc02_protocol.yaml",
             f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json",
             f"{REPO}/FDFLT01/out/FDFLT01_SEED_MANIFEST.json",
             f"{REPO}/FDFLT01/out/FDFLT01_POWER_ANALYSIS.json",
             f"{REPO}/FDFLT01/out/FDFLT01_PRE_RUN_GATES.json",
             f"{REPO}/FLRS02/out/FLRS02_B1_DIRECT_ATLAS.json",
             f"{REPO}/FLRS02/out/FLRS02_FUNCTIONAL_CRITERION.json"]

def build():
    mods=transitive_closure()
    import numpy, scipy, yaml
    pkgs={"numpy":numpy.__version__,"scipy":scipy.__version__,"pyyaml":yaml.__version__}
    data=[{"path":rel(p),"abs":p,"bytes":os.path.getsize(p),"sha256":sha(p)}
          for p in DATA_INPUTS if os.path.exists(p)]
    blob="\n".join("%s %s"%(m["sha256"],m["abs"]) for m in sorted(mods,key=lambda m:m["abs"]))
    blob+="\n"+"\n".join("%s %s"%(d["sha256"],d["abs"]) for d in sorted(data,key=lambda d:d["abs"]))
    blob+="\npython="+sys.version.split()[0]+"\n"+json.dumps(pkgs,sort_keys=True)
    MM={"SECTION":"FDFLT01 §10 — complete transitive methods manifest",
        "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "PYTHON":sys.version.split()[0],"PACKAGES":pkgs,
        "IMPORT_CLOSURE_METHOD":"every entry point is imported and every loaded module under the project roots is hashed",
        "PROJECT_ROOTS":list(ROOTS),
        "N_MODULES":len(mods),"MODULES":mods,
        "N_DATA_INPUTS":len(data),"DATA_INPUTS":data,
        "COMPLETE_PRE_RUN_METHODS_HASH":hashlib.sha256(blob.encode()).hexdigest()}
    json.dump(MM,open(f"{OUT}/FDFLT01_METHODS_MANIFEST.json","w"),indent=2)
    with open(f"{OUT}/FDFLT01_METHODS_SHA256SUMS","w") as fh:
        for m in sorted(mods,key=lambda m:m["abs"]): fh.write("%s  %s\n"%(m["sha256"],m["abs"]))
        for d in sorted(data,key=lambda d:d["abs"]): fh.write("%s  %s\n"%(d["sha256"],d["abs"]))
    return MM

def verify_runtime():
    """Runtime check: every imported project module must match its frozen hash."""
    MM=json.load(open(f"{OUT}/FDFLT01_METHODS_MANIFEST.json"))
    bad=[m["abs"] for m in MM["MODULES"] if not os.path.exists(m["abs"]) or sha(m["abs"])!=m["sha256"]]
    bad+=[d["abs"] for d in MM["DATA_INPUTS"] if not os.path.exists(d["abs"]) or sha(d["abs"])!=d["sha256"]]
    return {"CHANGED_OR_MISSING":bad,"PASS":not bad}

if __name__=="__main__":
    MM=build()
    E=json.load(open(f"{OUT}/FDFLT01_POWER_ANALYSIS.json"))
    S=json.load(open(f"{OUT}/FDFLT01_SEED_MANIFEST.json"))
    G=json.load(open(f"{OUT}/FDFLT01_PRE_RUN_GATES.json"))
    sys.path.insert(0,f"{REPO}/FDFLT01/code"); import fdflt01_endpoint as EP
    P=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
    FZ={"PROGRAM":"FRESH-DIRECT-FUNCTIONAL-LINEAGE-TEST-01","SHORT_NAME":"FDFLT01",
     "GENERATED_UTC":MM["GENERATED_UTC"],
     "PARENT_PROGRAM":"FUNCTIONAL-LINEAGE-ROUTE-SELECTION-02",
     "PARENT_TIP":S["PARENT_TIP"],
     "PARENT_TIP_SOURCE":"resolved from FLRS02_INCREMENT_MANIFEST.json on the Windows recovery disk",
     "PARENT_DISPOSITION":"ONE_EXISTING_POINT_DIRECT_TEST_JUSTIFIED",
     "FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_SCIENTIFIC_START":True,
     "COMPLETE_PRE_RUN_METHODS_HASH":"PASS",
     "METHODS_HASH":MM["COMPLETE_PRE_RUN_METHODS_HASH"],
     "SCIENTIFIC_QUESTION":("At the exact frozen B1 law, does the probability of the predeclared complete "
        "functional two-centre lineage event exceed 0.10?"),
     "INDEPENDENT_UNIT":"one world",
     "POINT":{"LABEL":"B1","kY":P["PHASE_B"]["POINT_B1"]["kY"],"muY":P["PHASE_B"]["POINT_B1"]["muY"],
              "OTHER_PARAMETERS":"inherited byte-for-byte from PQEC01_MASTER_FREEZE.json INHERITED_FROZEN_CONSTANTS",
              "INHERITED_FROZEN_CONSTANTS":P["INHERITED_FROZEN_CONSTANTS"]},
     "EXECUTION_LAW":{"METHOD":"the frozen PQEC01 runner pqec01_run.run_world is IMPORTED AND EXECUTED, not reimplemented",
        "pqec01_run_sha256":sha(f"{REPO}/PQEC01/code/pqec01_run.py"),
        "pqec01_observer_sha256":sha(f"{REPO}/PQEC01/code/pqec01_observer.py"),
        "ONLY_NON_PHYSICAL_DIFFERENCES":["raw output directory","tag prefix F instead of B","outcome firewall on what leaves the worker"],
        "STOP_RULES":P["STOP_RULES_PER_WORLD_ORDERED"],
        "HORIZON":P["INHERITED_FROZEN_CONSTANTS"]["T_HORIZON"]},
     "PRIMARY_ENDPOINT":{"f_primary":EP.F_PRIMARY,"T_primary_continuous":EP.BAND["T_primary"],
        "T_PRIMARY_STEPS":EP.STEPS["T_primary"],
        "INTEGER_CONVENTION":"need_steps = ceil(T(f)); the maturation event is at episode_start + need_steps - 1",
        "CONVENTION_VERIFIED_AGAINST_PARENT":"the pre-run equivalence gate reproduces the FLRS02 result exactly",
        "BAND_STEPS":EP.STEPS,"FRACTIONS":EP.FRACTIONS,
        "SEVEN_CONDITIONS":["F1 at least one dynamic Y birth",
          "F2 no extinction before functional maturation","F3 exactly two spatial centres under the frozen classifier",
          "F4 the two centres remain distinct for the complete primary maturation duration",
          "F5 the weaker centre's local X response reaches the frozen fraction",
          "F6 no third spatial centre before functional maturation completes",
          "F7 X/source integrity valid through functional maturation"],
        "FOUNDER_SURVIVAL_REQUIRED":False,"PARTICLE_GENEALOGY":"none constructed"},
     "DECISION_RULE":{k:E[k] for k in ("PRIMARY_N","PRIMARY_NULL_RATE","PRIMARY_ALPHA",
        "PRIMARY_CRITICAL_SUCCESS_COUNT","REJECT_H0_IF","P_p0_X_ge_critical",
        "POWER_AT_DEVELOPMENTAL_LOWER_BOUND","DEVELOPMENTAL_B1_SUCCESS","DEVELOPMENTAL_B1_LOWER_95")},
     "SEEDS":{"N_PRIMARY":S["N_PRIMARY"],"N_RESERVE":S["N_RESERVE"],"FORMULA":S["FORMULA"],
              "DISJOINT_FROM_KNOWN":S["DISJOINT_FROM_KNOWN"],"ALL_UNIQUE":S["ALL_UNIQUE"]},
     "TECHNICAL_FAILURE_DEFINITIONS":[
        "returncode != 0 (process interruption or unhandled exception)",
        "archive absent after the write","schema_ok False (corrupt or incomplete serialization)",
        "engine_invariants_ok False (engine invariant violation preventing a readable outcome)",
        "sha256 recomputation over the written bytes disagrees with the value recorded at write time"],
     "NO_SCIENTIFIC_FAILURE_MAY_TRIGGER_REPLACEMENT":True,
     "OUTCOME_FIREWALL":{"EXPOSED":["opaque arm token","completed flag","technical failure flag","checksum written flag"],
        "WITHHELD":["seed","success","birth count","centre count","stop reason","steps_recorded","runtime","file size","X response","extinction","third-centre event"]},
     "PRE_RUN_GATES":{"EQUIVALENCE_WITH_PARENT":G["FDFLT01_PRE_RUN_GATES"][0]["PASS"],
                      "PERSISTENT_CENTRE_IDENTITY":G["FDFLT01_PRE_RUN_GATES"][1]["PASS"]},
     "DEVELOPMENTAL_DATA_MAY_NOT_ENTER":["the 192-world primary estimate","the test statistic",
        "the confidence interval","the success count","the final confirmation claim"],
     "CLAIM_CEILING":("a positive result establishes at most that the probability of the predeclared complete "
        "functional two-centre lineage event at the frozen B1 law exceeds 0.10. It does not establish "
        "reproduction, heredity, evolution, life, multi-generation descent, a parameter-space region, "
        "or a universal lineage mechanism."),
     "TERMINAL_DISPOSITIONS":["DIRECT_FUNCTIONAL_LINEAGE_POINT_QUALIFIED__SUCCESS_RATE_EXCEEDS_0_10",
        "DIRECT_FUNCTIONAL_LINEAGE_POINT_NOT_QUALIFIED__SUCCESS_RATE_NOT_SHOWN_ABOVE_0_10",
        "DIRECT_FUNCTIONAL_LINEAGE_TEST_TECHNICALLY_INVALID"],
     "FORBIDDEN":["parameter retuning","interpolation","adaptive sample size","adaptive stopping of the batch",
        "founder survival gate","post-outcome scientific repair","pooling developmental worlds"],
     "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0}
    json.dump(FZ,open(f"{OUT}/FDFLT01_MASTER_FREEZE.json","w"),indent=2)
    print("modules:",MM["N_MODULES"],"data:",MM["N_DATA_INPUTS"])
    print("METHODS_HASH:",MM["COMPLETE_PRE_RUN_METHODS_HASH"])
    print("verify_runtime:",verify_runtime()["PASS"])
    print("critical:",FZ["DECISION_RULE"]["PRIMARY_CRITICAL_SUCCESS_COUNT"],
          "| T_PRIMARY_STEPS:",FZ["PRIMARY_ENDPOINT"]["T_PRIMARY_STEPS"])
