"""TLMR01 §2 §4 §11 — the law binding, the physics binding, the archive schema, and the MASTER
FREEZE that binds every pre-run artefact by hash.

The master freeze is taken ALONE, in its own commit, before every primary world. Nothing that is
not hashed here may be read by the run or by the analysis.
"""
from __future__ import annotations
import json, hashlib, datetime, os, sys, platform, subprocess
import numpy as np, scipy
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_laws as LW, tlmr01_run as RUN
U=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

PRE_RUN_ARTEFACTS=[
 "TLMR01_PARENT_BINDING.json","TLMR01_SCIENTIFIC_STATE_LEDGER.json",
 "TLMR01_MEASUREMENT_LAWS.json","TLMR01_PHYSICS_BINDING.json",
 "TLMR01_ARCHIVE_SCHEMA.json","TLMR01_MEASUREMENT_OBJECTS.json",
 "TLMR01_UNCERTAINTY_RULES.json","TLMR01_POWER_RULE.json","TLMR01_SELECTION_RULE.json",
 "TLMR01_TERMINAL_VOCABULARY.json","TLMR01_DISPOSITION_LOGIC.json",
 "TLMR01_SEED_MANIFEST.json","TLMR01_METHODS_CLOSURE.json",
 "TLMR01_INSTRUMENTATION_QUALIFICATION.json","TLMR01_PATH_COVERAGE.json",
 "TLMR01_WRITER_QUALIFICATION.json","TLMR01_FIXTURES.json"]

def archive_schema():
    return {"MISSION":"TLMR01","SECTION":"4 — the archive schema","GENERATED_UTC":U(),
     "PRINCIPLE":"the archive must be sufficient, ON ITS OWN, to rebuild every decision the "
       "online path made — the component structure, the frozen state machine, the maturation "
       "candidate, the local-X ratio and the identity intervals — WITHOUT importing the online "
       "trigger or the online endpoint. §5 proves that offline reconstruction step by step "
       "against the online record before world 1.",
     "FILE":"one .npz per world, named TLMR01_<LAW>_<ROLE>_i<index>_s<seed>.npz",
     "ARRAYS":RUN.SCHEMA,
     "WHY_PER_CELL_ROWS":"the frozen centre rule is single-linkage over Y-OCCUPIED CELLS, so a "
       "per-cell row is the smallest lossless unit. Scalars per step would not let the component "
       "structure be rebuilt, and a summary would not let a later definition of a fork be applied "
       "without re-running 512 worlds.",
     "WHY_x_disc":"the frozen f5 ratio sums X over a CORE_R disc at the rounded centroid. That "
       "disc covers cells carrying no Y, which no other row sees. Without k_xd, "
       "P(trigger | matured) is not reconstructable from the archive AT ALL. The gap was found "
       "while deriving M3 and the schema was widened before world 1.",
     "WHY_EXACT_CENTROID_INPUTS":"a centroid rounded to three decimals could flip an identity "
       "link whose true distance lies within rounding of CORE_R = 5. k_a0y, k_a0x, k_soy, k_sox "
       "let the offline reader recompute (a0 + so/m) % L in the frozen expression order, so the "
       "reconstruction is bit-equal rather than approximately equal.",
     "REMOVAL_SEMANTICS":"the rows written at the removal step are the state BEFORE the "
       "intervention, because the recorder runs before the trigger is consulted. The post-removal "
       "state first appears at step + 1. run_world additionally records Y and WY totals on both "
       "sides of the intervention, the parent Y after, and the daughter Y before and after, so "
       "the conservation of the declared channel is auditable per world.",
     "META_FIELDS":["tag","law","role","index","seed","kY","muY","p_hop_Y","steps_executed","stop",
       "integrity_ok","TERMINAL_LABEL","t_m","AT_TRIGGER","terminal_descent_level",
       "terminal_descent_step","descent_level","descent_step","n_descent_attempts","intervention",
       "final_state_hash","runtime_s","NARROW_DTYPES_LOSSLESS","archive_sha256","archive_bytes"],
     "AT_TRIGGER_VERSUS_TERMINAL":"the inherited FMRCT01 trigger re-evaluates and OVERWRITES its "
       "descent fields at every later 1 -> 2 separation, so its terminal value is the LAST "
       "separation in the trajectory and not the one that named the removed parent. run_world "
       "snapshots AT_TRIGGER at the firing step and reports the terminal values under separate "
       "names. Neither may stand in for the other. The inherited module is unchanged.",
     "NARROW_DTYPES":"columns are stored in the narrowest dtype that holds them, and every world "
       "asserts the narrowing is lossless before it is written. A world whose values would be "
       "truncated is a TECHNICAL failure, never a silent write.",
     "NO_FIELD_IS_ADDED_OR_REMOVED_AFTER_THIS_FREEZE":True}

def physics_binding():
    C=LW.SHARED
    return {"MISSION":"TLMR01","SECTION":"2 — physics binding","GENERATED_UTC":U(),
     "SHARED_FROZEN_PHYSICS":C,
     "IDENTICAL_ACROSS_ALL_THREE_LAWS":["the engine","the LawSpec","the feed and exchange law",
       "the scheduler","the initial condition","the centre classifier","the identity rule",
       "the trigger rule","the intervention","the horizon","CAP","L","p_hop_X","muX","kX","X_SEED"],
     "THE_ONLY_DIFFERENCES_ARE":["kY","muY","p_hop_Y"],
     "X_LAWSPEC_BASELINE":"UNCHANGED",
     "NEW_PARAMETER_POINTS":0,
     "L":int(C["L"]),"L_IS_UNCHANGED":True,
     "FINITE_SIZE_SCOPE":"OUT_OF_SCOPE — FINITE_SIZE_RELEVANCE = NOT_SUPPORTED and "
       "ONE_ZERO_RUN_DETOUR_ONLY is spent",
     "T_HORIZON":int(C["T_HORIZON"]),"FULL_HORIZON_EVERY_WORLD":True,
     "NO_SCIENTIFIC_EARLY_STOP":"not extinction, not a third centre, not a maximum occupancy. The "
       "single break is an engine invariant failure, which is technical.",
     "ENVIRONMENT":{"python":platform.python_version(),"numpy":np.__version__,
                    "scipy":scipy.__version__,"platform":platform.platform()}}

def main():
    os.makedirs(OUT,exist_ok=True)
    json.dump(LW.binding(),open(f"{OUT}/TLMR01_MEASUREMENT_LAWS.json","w"),indent=1)
    json.dump(physics_binding(),open(f"{OUT}/TLMR01_PHYSICS_BINDING.json","w"),indent=1)
    json.dump(archive_schema(),open(f"{OUT}/TLMR01_ARCHIVE_SCHEMA.json","w"),indent=1)
    missing=[a for a in PRE_RUN_ARTEFACTS if not os.path.exists(f"{OUT}/{a}")]
    files=[{"artefact":a,"sha256":sha(f"{OUT}/{a}"),"bytes":os.path.getsize(f"{OUT}/{a}")}
           for a in PRE_RUN_ARTEFACTS if os.path.exists(f"{OUT}/{a}")]
    MC=json.load(open(f"{OUT}/TLMR01_METHODS_CLOSURE.json")) if os.path.exists(f"{OUT}/TLMR01_METHODS_CLOSURE.json") else {}
    IQ=json.load(open(f"{OUT}/TLMR01_INSTRUMENTATION_QUALIFICATION.json")) if os.path.exists(f"{OUT}/TLMR01_INSTRUMENTATION_QUALIFICATION.json") else {}
    PC=json.load(open(f"{OUT}/TLMR01_PATH_COVERAGE.json")) if os.path.exists(f"{OUT}/TLMR01_PATH_COVERAGE.json") else {}
    SM=json.load(open(f"{OUT}/TLMR01_SEED_MANIFEST.json"))
    gates={
     "ALL_PRE_RUN_ARTEFACTS_PRESENT":not missing,
     "METHODS_CLOSURES_AGREE":MC.get("TWO_INDEPENDENT_CLOSURES",{}).get("CLOSURES_AGREE"),
     "NO_INHERITED_MODULE_HAS_DRIFTED":MC.get("NO_INHERITED_MODULE_HAS_DRIFTED"),
     "INSTRUMENTATION_INERTNESS":IQ.get("INSTRUMENTATION_INERTNESS"),
     "ARCHIVE_DECISION_RECONSTRUCTION":IQ.get("ARCHIVE_DECISION_RECONSTRUCTION"),
     "PATH_COVERAGE":PC.get("PATH_COVERAGE"),
     "WRITER_AND_READ_BACK":(json.load(open(f"{OUT}/TLMR01_WRITER_QUALIFICATION.json"))["ALL_PASS"]
        if os.path.exists(f"{OUT}/TLMR01_WRITER_QUALIFICATION.json") else None),
     "OFFLINE_AGREEMENT_NON_VACUOUS":PC.get("OFFLINE_AGREEMENT_NON_VACUITY",{}).get("NON_VACUOUS"),
     "SEED_GATES":SM.get("ALL_GATES"),
     "PRIMARY_BUDGET_EXACT":SM.get("PRIMARY_BUDGET_EXACT")}
    art={"MISSION":"TLMR01","SECTION":"11 — MASTER FREEZE","GENERATED_UTC":U(),
     "TAKEN_ALONE_IN_ITS_OWN_COMMIT_BEFORE_EVERY_PRIMARY_WORLD":True,
     "MISSING_ARTEFACTS":missing,
     "PRE_RUN_ARTEFACTS":files,
     "COMPLETE_PRE_RUN_METHODS_HASH":MC.get("COMPLETE_PRE_RUN_METHODS_HASH"),
     "SEED_SET_HASH":SM.get("SEED_SET_HASH"),
     "PARENT_TIP":json.load(open(f"{OUT}/TLMR01_PARENT_BINDING.json"))["PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY"],
     "GATES":gates,
     "ALL_GATES_PASS":all(v in (True,"PASS") for v in gates.values()),
     "WHAT_A_FAILED_GATE_MEANS":"no primary world is run. A gate is never waived and never "
       "downgraded to a warning.",
     "AFTER_THIS_POINT":["no artefact above may change","no rule may be added or removed",
       "no threshold may move","no world may be moved between laws","no sample size may change"],
     "FREEZE_HASH":None}
    art["FREEZE_HASH"]=hashlib.sha256(json.dumps(
      {k:v for k,v in art.items() if k!="FREEZE_HASH"},sort_keys=True).encode()).hexdigest()
    json.dump(art,open(f"{OUT}/TLMR01_MASTER_FREEZE.json","w"),indent=1)
    print("missing artefacts:",missing or "none")
    for k,v in gates.items(): print("  %-38s %s"%(k,v))
    print("ALL_GATES_PASS =",art["ALL_GATES_PASS"])
    print("FREEZE_HASH =",art["FREEZE_HASH"])

if __name__=="__main__": main()
