"""OMLDCT01 — final closure. The owner has adjudicated: the four pre-C2 full-scale trajectories
are scientific-scale pilots, and the mission is technically invalid. This writes that closure and
nothing softer."""
from __future__ import annotations
import json, hashlib, datetime, os, subprocess

REPO = os.environ.get("OMLDCT01_REPO", "/home/claude/edl")
O = f"{REPO}/OMLDCT01/out"
TIP = "4d61da4b68364277f2a9739a4837055860c0c01e"   # resolved from the verified Windows chain

def sf(p):
    with open(p, "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()

PILOTS = [
 {"index": 0, "seed": 1440724471, "outcome": "TRIGGERED_IDENTITY_NOT_CARRIED at t_m = 1303",
  "admissible": False},
 {"index": 1, "seed": 818998374,  "outcome": "NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE", "admissible": False},
 {"index": 2, "seed": 3087639930, "outcome": "NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE", "admissible": False},
 {"index": 3, "seed": 2434593729, "outcome": "NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE", "admissible": False},
]

INCIDENT = {
 "MISSION": "OMLDCT01",
 "SECTION": "pre-C2 incident record",
 "GENERATED_UTC": None,
 "OMLDCT01_CURRENT_TIP": TIP,
 "TIP_RESOLVED_FROM": "the verified Windows bundle chain, restored and fsck-clean, not from the "
                      "container's working copy",

 "WHAT_HAPPENED": "while validating the fork runner I executed four trajectories at full scientific "
                  "scale — L = 36, T = 11000, the frozen LAW_C_MCTT01 — on FROZEN CANDIDATE BASE "
                  "SEED indices 0, 1, 2 and 3, BEFORE the master freeze was committed as C2.",

 "WHY_IT_IS_FATAL_AND_NOT_A_FIXTURE": [
   "C2 did not precede the first scientific-scale trajectory.",
   "The four trajectories used frozen candidate seeds from the mission's own accrual list.",
   "Their non-trigger and no-admissible-pair outcomes became known to me.",
   "Those four seeds were subsequently removed from accrual — a removal informed by their outcomes.",
   "Section 5 names 'C2 does not precede world 1' as a campaign-level technical invalidity."],

 "THE_ADJUDICATION_IS_THE_OWNERS_AND_IT_IS_FINAL":
   "THE_FOUR_PRE_C2_FULL_SCALE_TRAJECTORIES_ARE_SCIENTIFIC_SCALE_PILOTS",
 "WHAT_I_AM_NOT_PERMITTED_TO_DO":
   "reinterpret them as non-scientific fixtures. I proposed that reading myself when I declared the "
   "deviation; the owner has rejected it and the rejection is correct. Retiring four seeds after "
   "seeing that they failed to trigger is outcome-informed seed selection whatever it is called.",

 "PRE_C2_SCIENTIFIC_SCALE_TRAJECTORIES": 4,
 "PILOT_SEED_INDICES": [0, 1, 2, 3],
 "PILOT_SEEDS": [p["seed"] for p in PILOTS],
 "PRIMARY_CONFIRMATORY_PAIRS": 0,
 "PRIMARY_RESULT": "NOT_REACHED",
 "ENDPOINT_VALUES_RETAINED_FOR_CONFIRMATION": "none",

 "PILOT_OUTCOMES_CLASSIFIED_AS": "DEVELOPMENTAL_PILOT_DIAGNOSTIC",
 "PILOT_DETAIL": PILOTS,
 "PILOT_SUMMARY": {"admissible_pairs_produced": 0, "archives_written": 0,
                   "endpoint_values_computed": 0, "arm_instances_consumed": 2.3},
 "DEVELOPMENTAL_PILOT_DIAGNOSTIC_MAY_NOT_ENTER": [
   "OMLDCT02 power", "OMLDCT02 seed selection", "OMLDCT02 thresholds",
   "OMLDCT02 paired analysis", "any confirmatory estimate"],
 "AND_THEIR_SEEDS_ARE_EXCLUDED_FROM_OMLDCT02": True,

 "A_SECOND_DEFECT_FOUND_DURING_CLOSURE": {
   "what": "two of the four digests OMLDCT01 recorded are not recomputable from the committed "
           "repository: METHODS_HASH (21 candidate serialisations fail) and SEED_SET_HASH (72 fail). "
           "A third, the durability record's FREEZE_HASH, holds the master freeze FILE digest under "
           "a key the master freeze uses for a digest of its own CONTENT.",
   "root_cause": "digests produced by inline heredoc scripts that were never committed.",
   "consequence_for_OMLDCT02": "section 5 of the successor launcher requires committed generators "
                               "and distinct labels. That defect does not survive."},

 "WHAT_IS_NOT_LOST": "no scientific result is compromised, because none exists. Zero confirmatory "
                     "pairs were ever produced and zero endpoint values were ever computed.",
 "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "X_LAWSPEC_BASELINE": "UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
}

REUSABLE = [
 {"asset": "human five-line decision addendum",
  "files": ["OMLDCT01/out/OMLDCT01_HUMAN_DECISION_ADDENDUM.json",
            "OMLDCT01/out/OMLDCT01_HUMAN_DECISION_ADDENDUM.md"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "the five decisions are the owner's, taken with FRESH_WORLD_COUNT_AT_DECISION = 0 and "
         "OUTCOMES_ACCESSED = none. They are untouched by the invalidity, which is about sequencing."},
 {"asset": "exact Pratt sign-flip implementation",
  "files": ["OMLDCT01/code/omldct01_analysis.py", "OMLDCT01/code/omldct01_selftest.py",
            "OMLDCT01/out/OMLDCT01_FIVE_LINE_SELF_TEST.json"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "ten deterministic self-test cases, no scientific trajectory. Code, not evidence."},
 {"asset": "second independent E3 classifier",
  "files": ["OMLDCT01/code/omldct01_e3_b.py"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "written after the pilots but reading none of them; qualified against archives that predate "
         "OMLDCT01 entirely."},
 {"asset": "fixtures and the qualification harness",
  "files": ["OMLDCT01/code/omldct01_e3_qualify.py",
            "OMLDCT01/out/OMLDCT01_E3_QUALIFICATION_FIXTURES.json"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "hand-built and random configurations only."},
 {"asset": "locked-daughter reconstruction qualification",
  "files": ["OMLDCT01/out/OMLDCT01_E3_QUALIFICATION.json",
            "OMLDCT01/out/OMLDCT01_E3_CLASSIFIER_B_22_WORLDS.json"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "22 developmental LAW_C removal worlds and 4 negative controls, all from LDFMA01 and "
         "earlier. It must be REBOUND in OMLDCT02 C1, not inherited by reference."},
 {"asset": "Windows durability chain",
  "files": ["OMLDCT01/out/OMLDCT01_C3_DURABILITY.json",
            "OMLDCT01/out/OMLDCT01_PRE_RUN_DURABILITY.json"],
  "status": "REUSABLE_IMPLEMENTATION_EVIDENCE",
  "why": "the chain that carries the repository is infrastructure, not a scientific claim."},
 {"asset": "the master freeze, the seed manifest and the methods closure",
  "files": ["OMLDCT01/out/OMLDCT01_MASTER_FREEZE.json", "OMLDCT01/out/OMLDCT01_SEED_MANIFEST.json",
            "OMLDCT01/out/OMLDCT01_METHODS_CLOSURE.json"],
  "status": "NOT_AUTHORITATIVE_FOR_OMLDCT02",
  "why": "the freeze postdates scientific-scale execution and the seed list is contaminated by "
         "outcome-informed retirement. OMLDCT02 builds its own."},
]

DISPOSITION = {
 "MISSION": "OMLDCT01",
 "SECTION": "final disposition",
 "GENERATED_UTC": None,
 "OMLDCT01_FINAL_DISPOSITION": "OMLDCT01_TECHNICALLY_INVALID",
 "DECIDED_BY": "Tommy Lepesteur, owner adjudication, final",
 "NO_SOFTER_STRING_WAS_INVENTED": True,
 "OMLDCT01_CURRENT_TIP": TIP,
 "SCIENTIFIC_PARENT": "LDFMA01 — LOCKED-DAUGHTER-FAILURE-MECHANISM-ARBITRATION-01",
 "SCIENTIFIC_PARENT_TIP": "2101b301a2444a4a825a6cd338a8db7334c53c9f",
 "PARENT_HANDOFF_SHA256": "e3ec4b929069a794b648feffc9b7b5d9315a7b96a74711fcd99746f931523029",
 "PARENT_HANDOFF_BYTES_NEVER_REWRITTEN": True,
 "PRIMARY_CONFIRMATORY_PAIRS": 0,
 "PRIMARY_RESULT": "NOT_REACHED",
 "NEW_SCIENTIFIC_WORLDS_ENTERING_ANY_RECORD": 0,
 "INTENTIONAL_COMMITS_USED": 5, "MAX_INTENTIONAL_COMMITS": 5,
 "REUSABLE_ASSETS": REUSABLE,
 "SUCCESSOR": "OMLDCT02 — ONE-MATCHED-LOCKED-DAUGHTER-CONTROL-TEST-02",
 "SUCCESSOR_AUTHORISED_ONCE": True, "SECOND_CLEAN_RESTART": "forbidden",
 "THE_DESIGN_IS_UNCHANGED": "no endpoint, parameter, law, alpha, direction, combination rule, "
                            "zero treatment, minimum pair count or resource ceiling moves.",
 "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "X_LAWSPEC_BASELINE": "UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
}

def main():
    u = datetime.datetime.now(datetime.timezone.utc).isoformat()
    INCIDENT["GENERATED_UTC"] = u; DISPOSITION["GENERATED_UTC"] = u
    json.dump(INCIDENT, open(f"{O}/OMLDCT01_PRE_C2_INCIDENT.json", "w"), indent=1)
    json.dump(DISPOSITION, open(f"{O}/OMLDCT01_FINAL_DISPOSITION.json", "w"), indent=1)
    print("OMLDCT01_FINAL_DISPOSITION =", DISPOSITION["OMLDCT01_FINAL_DISPOSITION"])
    print("PRE_C2_SCIENTIFIC_SCALE_TRAJECTORIES =", INCIDENT["PRE_C2_SCIENTIFIC_SCALE_TRAJECTORIES"])
    print("PRIMARY_CONFIRMATORY_PAIRS =", INCIDENT["PRIMARY_CONFIRMATORY_PAIRS"])

if __name__ == "__main__":
    main()
