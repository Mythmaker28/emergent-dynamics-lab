"""FMRT01 §15 — complete transitive methods hash and the master freeze."""
from __future__ import annotations
import hashlib,importlib,json,os,sys,datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRT01/out"
ROOTS=("/home/claude/edl","/home/claude/ORR01","/home/claude/OBTC02","/home/claude/PQEC01")
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
def rel(p): return os.path.relpath(p,REPO) if p.startswith(REPO+"/") else p
def closure():
    for p in (f"{REPO}/FMRT01/code",f"{REPO}/PQEC01/code",f"{REPO}/FDFLT01/code",
              "/home/claude/ORR01/code","/home/claude/OBTC02/code"):
        if p not in sys.path: sys.path.insert(0,p)
    for m in ("fmrt01_engine","fmrt01_identity","fmrt01_endpoint","fmrt01_seeds","fmrt01_run",
              "fmrt01_analyse","fmrt01_review","fmrt01_final","fmrt01_fixtures","fmrt01_inertness",
              "pqec01_run","pqec01_observer","fdflt01_endpoint"):
        importlib.import_module(m)
    out=[]
    for name,mod in sorted(sys.modules.items()):
        f=getattr(mod,"__file__",None)
        if not f: continue
        f=os.path.abspath(f)
        if any(f.startswith(r+"/") for r in ROOTS) and f.endswith(".py") and "__pycache__" not in f:
            out.append({"module":name,"path":rel(f),"abs":f,"bytes":os.path.getsize(f),"sha256":sha(f)})
    return out
DATA=[f"{REPO}/OBTC02/code/obtc02_protocol.yaml","/home/claude/OBTC02/code/obtc02_protocol.yaml",
      f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json",
      f"{OUT}/FMRT01_SEED_BLOCK_MANIFEST.json",f"{OUT}/FMRT01_POWER_ANALYSIS.json",
      f"{OUT}/FMRT01_PRIMARY_ENDPOINT.json",f"{OUT}/FMRT01_CONTROL_DESIGN.json",
      f"{OUT}/FMRT01_INTERVENTION_FIXTURES.json",f"{OUT}/FMRT01_UNARMED_INERTNESS.json",
      f"{REPO}/RCD01/out/RCD01_REPRODUCTION_CRITERION.json",
      f"{REPO}/FDFLT01/out/FDFLT01_FINAL_DISPOSITION.json"]
def build():
    mods=closure(); import numpy,scipy,yaml
    pk={"numpy":numpy.__version__,"scipy":scipy.__version__,"pyyaml":yaml.__version__}
    data=[{"path":rel(p),"abs":p,"bytes":os.path.getsize(p),"sha256":sha(p)} for p in DATA if os.path.exists(p)]
    blob="\n".join("%s %s"%(m["sha256"],m["abs"]) for m in sorted(mods,key=lambda m:m["abs"]))
    blob+="\n"+"\n".join("%s %s"%(d["sha256"],d["abs"]) for d in sorted(data,key=lambda d:d["abs"]))
    blob+="\npython="+sys.version.split()[0]+"\n"+json.dumps(pk,sort_keys=True)
    MM={"SECTION":"FMRT01 §15 — complete transitive methods manifest",
        "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "PYTHON":sys.version.split()[0],"PACKAGES":pk,"PROJECT_ROOTS":list(ROOTS),
        "N_MODULES":len(mods),"MODULES":mods,"N_DATA_INPUTS":len(data),"DATA_INPUTS":data,
        "COMPLETE_PRE_RUN_METHODS_HASH":hashlib.sha256(blob.encode()).hexdigest()}
    json.dump(MM,open(f"{OUT}/FMRT01_METHODS_MANIFEST.json","w"),indent=2)
    with open(f"{OUT}/FMRT01_METHODS_SHA256SUMS","w") as fh:
        for m in sorted(mods,key=lambda m:m["abs"]): fh.write("%s  %s\n"%(m["sha256"],m["abs"]))
        for d in sorted(data,key=lambda d:d["abs"]): fh.write("%s  %s\n"%(d["sha256"],d["abs"]))
    return MM
def verify():
    MM=json.load(open(f"{OUT}/FMRT01_METHODS_MANIFEST.json"))
    bad=[m["abs"] for m in MM["MODULES"]+MM["DATA_INPUTS"] if not os.path.exists(m["abs"]) or sha(m["abs"])!=m["sha256"]]
    return {"CHANGED_OR_MISSING":bad,"PASS":not bad}
if __name__=="__main__":
    MM=build()
    sys.path.insert(0,f"{REPO}/FMRT01/code"); import fmrt01_endpoint as EP
    SB=json.load(open(f"{OUT}/FMRT01_SEED_BLOCK_MANIFEST.json"))
    PW=json.load(open(f"{OUT}/FMRT01_POWER_ANALYSIS.json"))
    EPJ=json.load(open(f"{OUT}/FMRT01_PRIMARY_ENDPOINT.json"))
    CD=json.load(open(f"{OUT}/FMRT01_CONTROL_DESIGN.json"))
    IN=json.load(open(f"{OUT}/FMRT01_UNARMED_INERTNESS.json"))
    FX=json.load(open(f"{OUT}/FMRT01_INTERVENTION_FIXTURES.json"))
    P=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
    FZ={"PROGRAM":"FRESH-MINIMAL-REPRODUCTION-TEST-01","SHORT_NAME":"FMRT01",
     "GENERATED_UTC":MM["GENERATED_UTC"],
     "FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_SCIENTIFIC_WORLD":True,
     "PARENT_TIP":SB["PARENT_TIP"],
     "CONTAINER_INCIDENT":("this mission began after the FIFTH container rollback. The repository was "
       "restored from RCD01_INCREMENT.bundle on Tommy's Windows disk. The SPOIQ01 capability module was "
       "never made durable and was destroyed; it is RECONSTRUCTED here and RE-QUALIFIED from scratch, "
       "and SPOIQ01's recorded hashes are NOT claimed."),
     "N_BLOCKS":SB["N_BLOCKS"],"ARMS_PER_BLOCK":3,"PRIMARY_SCIENTIFIC_WORLDS":SB["PRIMARY_SCIENTIFIC_WORLDS"],
     "MAX_PRIMARY_WORLDS":256,
     "POINT":{"LABEL":"B1","kY":P["PHASE_B"]["POINT_B1"]["kY"],"muY":P["PHASE_B"]["POINT_B1"]["muY"],
              "INHERITED_FROZEN_CONSTANTS":P["INHERITED_FROZEN_CONSTANTS"]},
     "EXECUTION_LAW":{"engine":"OBTC02/code/engine_obtc.py, byte-unchanged",
       "engine_sha256":sha("/home/claude/OBTC02/code/engine_obtc.py"),
       "engine_unchanged":sha("/home/claude/OBTC02/code/engine_obtc.py")=="2172deae5bbabf37238cf7712cb17663c151494befcf85505c537a7cac0ded30",
       "observer":"PQEC01/code/pqec01_observer.py","observer_sha256":sha(f"{REPO}/PQEC01/code/pqec01_observer.py"),
       "capability":"FMRT01/code/fmrt01_engine.py subclass; the autonomous law never invokes it",
       "capability_sha256":sha(f"{REPO}/FMRT01/code/fmrt01_engine.py")},
     "DESIGN":PW["SELECTED"],"DESIGN_REASONING":PW["SELECTION_REASONING"],
     "UNCONDITIONAL_POWER":PW["UNCONDITIONAL_POWER_AT_85_BLOCKS"],
     "PRIMARY_NULL":PW["PRIMARY_NULL"],
     "PRIMARY_ENDPOINT":EPJ,"CONTROL_DESIGN":CD,
     "QUALIFICATION":{"UNARMED_INERTNESS":IN["UNARMED_INERTNESS"],"FIXTURES_ALL_PASS":FX["ALL_PASS"]},
     "COMPLETE_PRE_RUN_METHODS_HASH":"PASS","METHODS_HASH":MM["COMPLETE_PRE_RUN_METHODS_HASH"],
     "MAX_TECHNICAL_RESERVES":6,"NO_SCIENTIFIC_FAILURE_MAY_TRIGGER_REPLACEMENT":True,
     "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0,
     "OUTCOME_FIREWALL":{"EXPOSED":["opaque block token","completed","technical failure","checksum written"],
       "WITHHELD":["condition","seed","trigger occurrence","R0","R1","R2","runtime","file size","stop step","centre count","X response"]},
     "TERMINAL_DISPOSITIONS":["MINIMAL_REPRODUCTION_CAUSALLY_QUALIFIED",
       "MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED",
       "MINIMAL_REPRODUCTION_NOT_QUALIFIED__PRE_INTERVENTION_MULTIPLICATION_TOO_RARE",
       "MINIMAL_REPRODUCTION_TEST_TECHNICALLY_INVALID"],
     "CLAIM_CEILING":("minimal reproduction under R0+R1+R2 at the frozen B1 law. Not strong self-"
       "reproduction, not second-generation competence, not heredity, not evolution, not life."),
     "WINDOWS_PRE_RUN_DURABILITY":"PENDING"}
    json.dump(FZ,open(f"{OUT}/FMRT01_MASTER_FREEZE.json","w"),indent=2)
    print("modules:",MM["N_MODULES"],"data:",MM["N_DATA_INPUTS"])
    print("METHODS_HASH:",MM["COMPLETE_PRE_RUN_METHODS_HASH"])
    print("engine unchanged:",FZ["EXECUTION_LAW"]["engine_unchanged"])
    print("verify:",verify()["PASS"])
