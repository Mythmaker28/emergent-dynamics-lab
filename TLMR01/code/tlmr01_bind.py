"""TLMR01 §1 — the parent binding and the scientific state ledger.

The parent tip is RESOLVED FROM THE REPOSITORY, never copied from prose. The FOTSEA01 handoff
itself instructs this: its PARENT_TIP line carries the ILRR01 tip and says in the same breath
that the value must be re-resolved from the repository rather than trusted. It is re-resolved
here, and the discrepancy is reported rather than smoothed.

The state ledger records what each ancestor ESTABLISHED and, more importantly, what it did NOT.
A successor that inherits only the good news is how a claim ceiling drifts.
"""
from __future__ import annotations
import json, subprocess, hashlib, datetime, os, sys
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
U=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def git(*a):
    return subprocess.run(["git","-C",REPO]+list(a),capture_output=True,text=True).stdout.strip()

HANDOFF="FOTSEA01/out/HANDOFF_TARGETED_LINEAGE_MEASUREMENT_FOR_REPRODUCTION_01.md"
INHERITED_CLAUSES={
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
 "CHECKER_RETURN_WRITTEN_BEFORE_ANY_FINDING_IS_ACTED_ON":"mandatory"}
LAUNCHER_CONSTRAINTS={
 "NEW_SCIENTIFIC_ENGINE_RUNS":"authorised only after the complete pre-run freeze",
 "MAX_PRIMARY_MEASUREMENT_WORLDS":512,"MAX_TECHNICAL_RESERVES":6,"MAX_MEASUREMENT_LAWS":3,
 "MAX_SELECTED_CONFIRMATION_LAWS":1,"SECOND_TARGETED_MEASUREMENT_CAMPAIGN":"forbidden",
 "POST_OUTCOME_NEW_LAW_SELECTION":"forbidden","UNEXECUTED_LAW_SELECTION":"forbidden",
 "INTERPOLATION":"forbidden","RESPONSE_SURFACE":"forbidden",
 "ADAPTIVE_PARAMETER_RETUNING":"forbidden","ADAPTIVE_SAMPLE_SIZE":"forbidden",
 "MAX_INTENTIONAL_COMMITS":5,"MAX_INDEPENDENT_CHECKERS":1,"REVIEW_CASCADE":"forbidden",
 "MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS":0}

LEDGER=[
 {"mission":"FDOT01","disposition":"FUNCTIONAL_ORGANISER_TURNOVER_PROSPECTIVELY_REPLICATED",
  "established":"7 of 160 fresh B1 worlds showed a FUNCTIONAL COMPLETE TURNOVER under the strict "
    "identity rule, prospectively, with the threshold frozen before world 1",
  "did_not_establish":"nothing about reproduction, heredity or any intervention: no trigger and "
    "no removal are involved in that endpoint"},
 {"mission":"FMRCT01","disposition":"the frozen trigger and the three interventions",
  "established":"LATEST_ALLOWED_TRIGGER = 6500, the full-horizon policy, and "
    "SELECTIVE_PARENT_REMOVAL as a deterministic occupancy-conserving channel that consumes no "
    "random number",
  "did_not_establish":"any rate"},
 {"mission":"BPRTC01","disposition":"NO_POST_REMOVAL_TURNOVER_POINT_IDENTIFIED_WITHIN_BOUNDED_DESIGN",
  "established":"at POINT_D10, 256 worlds: 35 triggered, 34 removals applied, 3 post-removal "
    "FUNCTIONAL COMPLETE TURNOVERS. This is the only published measurement of the exact chain "
    "TLMR01 calls M5, and it is the floor of TLMR01's selection rule",
  "did_not_establish":"a qualifying point"},
 {"mission":"MCTT01","disposition":"STAGE_A_CANDIDATE_NOT_QUALIFIED",
  "established":"at the MCTT01 law, 6 of 64 worlds triggered against a modelled 0.545; the "
    "fork-to-trigger conversion measured at baseline kY does NOT transport in kY",
  "did_not_establish":"Stage B was never executed; the law's post-removal behaviour is unmeasured"},
 {"mission":"PTOPD01","disposition":"PRE_TRIGGER_OPERATOR_NOT_IDENTIFIABLE__EXACT_MISSING_OBJECT_NAMED",
  "established":"the five missing objects by name, and that the support-extrapolation gate cannot "
    "pass above the occupation support ceiling sI = 5 because no archive recorded the "
    "single-centre exposure there",
  "did_not_establish":"any point; PTOPD01_MISSING_OBJECTS_SOLVED = false"},
 {"mission":"ILRR01","disposition":"NO_CURRENT_ISING_ROUTE_DECISION_CAPABLE__PROJECT_PAUSE_RECOMMENDED",
  "established":"that a route whose declared ceiling omits its own engineering is inadmissible, "
    "and that fdot01_centres binds L at import so no existing object is executable at another size",
  "did_not_establish":"a route"},
 {"mission":"FOTSEA01","disposition":"FINITE_SIZE_RELEVANCE_NOT_SUPPORTED__RETURN_TO_REPRODUCTION_MEASUREMENT",
  "established":"at zero worlds, that all four finite-size relevance criteria fail; the organiser "
    "is a one- to two-cell object whose excursion is indistinguishable from the free kernel; and "
    "that FUNCTIONAL is non-discriminating at this law — 99.25 per cent of identity intervals of "
    "at least 10 steps already contain an X birth",
  "did_not_establish":"anything about reproduction; ONE_ZERO_RUN_DETOUR_ONLY is now spent"}]

def main():
    tip=git("rev-parse","9f4c70c^{commit}")
    prose="098cfa12f3460f3cc56a6419bfe6c4eb501ec4f8"
    hp=f"{REPO}/{HANDOFF}"
    art={"MISSION":"TLMR01","SECTION":"1 — parent binding","GENERATED_UTC":U(),
     "PARENT":"FOTSEA01 — FUNCTIONAL-ORGANISER-TURNOVER-SPATIAL-EXTENT-AUDIT-01",
     "PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY":tip,
     "PARENT_TIP_AS_WRITTEN_IN_THE_HANDOFF_PROSE":prose,
     "THE_TWO_DIFFER":tip!=prose,
     "WHICH_ONE_BINDS":"the resolved one. The handoff's own PARENT_TIP line says the value must be "
       "re-resolved from the repository and not taken from prose; the prose value is ILRR01's tip, "
       "which was FOTSEA01's parent, not FOTSEA01's own. The discrepancy is reported, not smoothed, "
       "and every TLMR01 seed is derived from the RESOLVED tip.",
     "PARENT_TIP_SUBJECT":git("log","-1","--format=%s",tip),
     "PARENT_DISPOSITION":"FINITE_SIZE_RELEVANCE_NOT_SUPPORTED__RETURN_TO_REPRODUCTION_MEASUREMENT",
     "HANDOFF":{"path":HANDOFF,"sha256":sha(hp),"bytes":os.path.getsize(hp)},
     "INHERITED_CLAUSES_RE_EMITTED_VERBATIM":INHERITED_CLAUSES,
     "WHY_THEY_ARE_RE_EMITTED":"the FOTSEA01 handoff makes re-emission a clause in its own right, "
       "because its first handoff bound only one generation and the independent check called that "
       "cosmetic (HANDOFF-UNCONDITIONAL). Re-emitting them here binds them at TLMR01's birth and "
       "TLMR01's own handoff must re-emit them again.",
     "LAUNCHER_CONSTRAINTS":LAUNCHER_CONSTRAINTS,
     "NEVER_REWRITE_INHERITED_HISTORY_AT_OR_BELOW":"06c592313df96601de8d2a89676d5a5cf79fc414",
     "WORKING_BRANCH":git("rev-parse","--abbrev-ref","HEAD"),
     "HEAD_AT_BINDING":git("rev-parse","HEAD"),
     "HEAD_IS_DESCENDED_FROM_THE_PARENT_TIP":subprocess.run(
        ["git","-C",REPO,"merge-base","--is-ancestor",tip,"HEAD"]).returncode==0}
    json.dump(art,open(f"{OUT}/TLMR01_PARENT_BINDING.json","w"),indent=1)
    led={"MISSION":"TLMR01","SECTION":"1 — scientific state ledger","GENERATED_UTC":U(),
     "WHAT_IS_ESTABLISHED_AND_WHAT_IS_NOT":LEDGER,
     "UNCONDITIONAL_STATUS":{
       "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
       "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
       "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
       "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
       "PTOPD01_MISSING_OBJECTS_SOLVED":False,
       "PTOPD01_POINT_SELECTION_ROUTE":"PAUSED",
       "OLD_ROUTE_A_STATUS":"REJECTED__NOT_AUTHORISED",
       "FINITE_SIZE_RELEVANCE":"NOT_SUPPORTED"},
     "WHAT_TLMR01_MAY_ADD_AT_MOST":"the five named objects, measured at the three laws and the "
       "occupancies actually reached, plus at most one law nominated for a later disjoint causal "
       "confirmation. Nothing else.",
     "WHAT_TLMR01_MAY_NEVER_CLAIM":["reproduction","heredity","life","autonomous cohesion",
       "H3 confirmation","Kamimura-Kaneko validation","a minority window"],
     "INCLUDING_IN_DENIAL":"the forbidden claims may not be made even in the form of a denial; "
       "the frozen status strings above are the only permitted formulation."}
    json.dump(led,open(f"{OUT}/TLMR01_SCIENTIFIC_STATE_LEDGER.json","w"),indent=1)
    print("parent tip resolved :",tip)
    print("prose tip in handoff:",prose,"  differ =",tip!=prose)
    print("HEAD descended from the parent tip:",art["HEAD_IS_DESCENDED_FROM_THE_PARENT_TIP"])
    print("branch:",art["WORKING_BRANCH"])

if __name__=="__main__": main()
