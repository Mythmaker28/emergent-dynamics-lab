"""FMRCT01 §12/§13 — the master freeze and the methods manifest. Committed ALONE, before world 1."""
from __future__ import annotations
import json, hashlib, os, sys, glob, datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRCT01/out"
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()

def closure():
    """the ACTUAL transitive import closure, obtained by importing the FMRCT01 entry points and
    enumerating sys.modules, then mapping each loaded file to the repository copy with identical
    bytes. A hand-written list missed four transitively imported modules; this does not."""
    sys.path.insert(0,f"{REPO}/FMRCT01/code")
    for m in ("fmrct01_world","fmrct01_track","fmrct01_descent","fmrct01_event",
              "fmrct01_event_b","fmrct01_run","fmrct01_select","fmrct01_seeds","fmrct01_runtime"):
        __import__(m)
    ROOTS=(REPO,"/home/claude/ORR01","/home/claude/OBTC02","/home/claude/FDOT01")
    seen={}
    for name,mod in list(sys.modules.items()):
        f=getattr(mod,"__file__",None)
        if not f or not f.endswith(".py"): continue
        if not any(f.startswith(r) for r in ROOTS): continue
        seen[os.path.realpath(f)]=name
    # every YAML the protocol reads is load-bearing too
    for y in sorted(glob.glob(f"{REPO}/OBTC02/code/*.yaml")): seen[os.path.realpath(y)]=os.path.basename(y)
    out=[]; unresolved=[]
    for f in sorted(seen):
        h=sha(f)
        if f.startswith(REPO+os.sep):
            rel=os.path.relpath(f,REPO)
        else:
            # find the repository copy with identical bytes
            cands=[c for c in glob.glob(f"{REPO}/*/code/"+os.path.basename(f))
                   +glob.glob(f"{REPO}/*/*/code/"+os.path.basename(f)) if sha(c)==h]
            if not cands: unresolved.append(f); continue
            rel=os.path.relpath(sorted(cands)[0],REPO)
        out.append({"path":rel,"sha256":h,"bytes":os.path.getsize(f),
                    "imported_as":seen[f],"runtime_path":f})
    if unresolved:
        raise RuntimeError("load-bearing modules with no identical copy in the repository: %s"%unresolved)
    return out

def main():
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    L=lambda n: json.load(open(f"{OUT}/{n}"))
    PB=L("FMRCT01_PARENT_BINDING.json"); AS=L("FMRCT01_ASSURANCE.json")
    CL=L("FMRCT01_CLAIM_CEILING.json"); SM=L("FMRCT01_SEED_MANIFEST.json")
    FX=L("FMRCT01_FIXTURES.json"); DD=L("FMRCT01_DEVELOPMENTAL_DESCENT.json")
    EL=L("FMRCT01_DEVELOPMENTAL_ELIGIBILITY.json")
    import fmrct01_track as T
    man=closure()
    MF={"PROGRAM":"FRESH-MINIMAL-REPRODUCTION-CAUSAL-TEST-01","SHORT_NAME":"FMRCT01",
     "GENERATED_UTC":now,
     "PARENT_TIP":PB["PARENT_TIP"],
     "FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_FRESH_WORLD":True,
     "WORLDS_RUN_AT_THIS_POINT":0,
     "POINT":PB["POINT"],"ENGINE":PB["ENGINE"],
     "PARAMETER_RETUNING":"forbidden","INTERPOLATION":"forbidden","NEW_SPECIES":0,
     "SUBSTRATE_CHANGE":"forbidden",
     "TRIGGER":{"rule":"the frozen FDFLT01 functional maturation: a maximal run of exactly two "
        "spatial centres lasting NEED = %d steps with no third centre in the run, and the weaker "
        "centre's local X mass at the event at least F_PRIMARY = 1 - 1/e of the stronger's; the "
        "event is at exactly run_start + NEED - 1"%T.NEED,
       "NEED":T.NEED,"F_PRIMARY":T.F_PRIMARY,
       "LATEST_ALLOWED_TRIGGER":T.LATEST_ALLOWED_TRIGGER,
       "POST_TRIGGER_WINDOW":T.POST_TRIGGER_WINDOW,
       "MATERIAL_PROVENANCE_IS_NOT_PART_OF_THE_TRIGGER":True},
     "HORIZON":{"T_HORIZON":T.T_HORIZON,"EVERY_TRAJECTORY_RUNS_THE_FULL_HORIZON":True,
       "NOT_STOPS":["EXTINCT","THIRD_CENTRE","MAX_PERMITTED_Y","daughter failed","success occurred",
                    "event became impossible"],
       "ONLY_BREAK":"a genuine engine invariant failure, which is a technical fault and not a scientific outcome",
       "DIFFERENCE_FROM_FMRT01":"FMRT01 stopped phase 1 on extinction, a third centre and NY > N_STAR. "
         "FMRCT01 stops for none of them, so FMRT01's 15/85 trigger rate is a LOWER bound here."},
     "DESCENT_RULE":{"module":"fmrct01_descent.py",
       "frozen":"exactly two components; exact tie is ambiguous; the parent is the component at "
         "strictly minimal toroidal centroid distance from the parent's last centroid; that minimum "
         "must be <= CORE_R; the other component is the daughter; both identities must survive under "
         "the strict FDOT01 link rule from the separation to maturation",
       "LITERAL_MRCI01_CLAUSE_4_IS_ALSO_EVALUATED_AND_REPORTED_FOR_EVERY_BLOCK":True,
       "WHY_THE_LITERAL_RULE_IS_NOT_USED":DD["WHY_THE_TWO_READINGS_DIVERGE"],
       "MEASURED_LITERAL_RESOLUTION_RATE":DD["READING_A_LITERAL_MRCI01"],
       "MEASURED_FROZEN_RESOLUTION_RATE":DD["READING_B_STRICT_MINIMUM"],
       "SIZE_AGE_AND_X_MASS_ARE_NEVER_USED":True},
     "IDENTITY_RULE":"the strict FDOT01 link: a link continues an identity only when the previous "
       "component has exactly one candidate within CORE_R and the current component has exactly one. "
       "Ties, splits and merges all terminate the identity.",
     "PRIMARY_EVENT":{"R0":"exactly one parent organiser exists and is continuously tracked",
       "R1":"one endogenous daughter organiser forms and is uniquely identified by the frozen descent rule",
       "R2":"the daughter reaches the frozen functional maturation and produces local X",
       "R3":"the parent organiser is selectively removed and the daughter is left physically untouched",
       "R4":"after the removal the daughter continues generating local X in its own cells",
       "R5":"while the parent remains absent the daughter completes at least one constituent-Y turnover inside ONE identity interval",
       "R6":"local X production is present on BOTH sides of that removal, and the daughter persists past it",
       "CONTROLS":"a matched GLOBAL_OFF showing zero local production and a matched SHAM showing the machinery inert",
       "UNIT":"one independent seed block; steps, centres, births, turnovers and particles are never replicates",
       "ORDERING":"R5 must follow R3"},
     "ARMS":{"SHAM":"the base trajectory itself; the intervention is a bit-exact no-op, proven in fixtures",
             "SELECTIVE":"Y of the parent component only, Y -> WY through the engine's declared channel",
             "GLOBAL_OFF":"every Y in the world, same channel",
             "ALL_THREE_ARE_DETERMINISTIC_AND_CONSUME_NO_RANDOM_NUMBER":True},
     "DESIGN":{"N_BLOCKS":SM["N_BLOCKS"],"MAX_FULL_FORKS":SM["MAX_FULL_FORKS"],
       "MAX_REALIZED_ARM_INSTANCES":AS["CHOSEN"]["MAX_REALIZED_ARM_INSTANCES"],"CEILING":512,
       "HARD_BOUND_PROOF":AS["HARD_BOUND_PROOF"],
       "ADAPTIVE_SAMPLE_SIZE":"forbidden","OUTCOME_DRIVEN_STOPPING":"forbidden",
       "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0},
     "FORK_SELECTION":{"rule":SM["FORK_PRIORITY"],"order_sha256":SM["PRIORITY_ORDER_SHA256"],
       "eligibility":"triggered AND t_m <= 6500 AND the frozen descent resolved AND both identities "
         "carried to maturation. Every clause is a PRE-intervention property of the base trajectory; "
         "no post-intervention outcome can enter the selection."},
     "CORRECTED_ASSURANCE":AS["ASSURANCE_OF_THE_CHOSEN_DESIGN"],
     "THE_CORRECTION":AS["THE_CORRECTION"],
     "HONEST_LIMITATION_FROZEN_BEFORE_OUTCOMES":AS["HONEST_LIMITATION_FROZEN_BEFORE_OUTCOMES"],
     "CLAIM_LEVELS":CL["LEVELS"],
     "UNCONDITIONAL":CL["UNCONDITIONAL_WHATEVER_K_IS"],
     "TERMINAL_DISPOSITIONS_ALLOWED":CL["TERMINAL_DISPOSITIONS_ALLOWED"],
     "FIXTURES":{"n":FX["N"],"all_pass":FX["ALL_PASS"],
       "two_independent_implementations":"fmrct01_track/fmrct01_event (A) and fmrct01_event_b (B)"},
     "DEVELOPMENTAL_INPUTS_ARE_NOT_CONFIRMATORY":True,
     "NO_POOLING_WITH_ANY_PREVIOUS_EXPERIMENT":True,
     "METHODS_MANIFEST":man,"N_METHODS_FILES":len(man)}
    json.dump(MF,open(f"{OUT}/FMRCT01_MASTER_FREEZE.json","w"),indent=1)
    with open(f"{OUT}/FMRCT01_METHODS_SHA256SUMS","w") as f:
        for m in man: f.write("%s  %s\n"%(m["sha256"],m["path"]))
    print("freeze written; methods files:",len(man))
    print("N",SM["N_BLOCKS"],"F",SM["MAX_FULL_FORKS"],"worst",AS["CHOSEN"]["MAX_REALIZED_ARM_INSTANCES"])
if __name__=="__main__": main()
