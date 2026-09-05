"""TBRT02 — C4. The analysis, written after C3 and before any checker."""
from __future__ import annotations
import os, sys, json, statistics as st, subprocess
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "TBRT02/code"))
import tbrt02_freeze as F

def load(pref):
    r = []
    for sh in (0, 1):
        r += json.load(open(f"{REPO}/TBRT02/work/c4/{pref}{sh}.json"))
    return r

A, B = load("C4_LINEAGE_"), load("C4_LINEAGE_B_")
cap = json.load(open(f"{REPO}/TBRT02/work/c4/R1_CAPABILITY.json"))
frz = json.load(open(f"{REPO}/TBRT02/out/TBRT02_MASTER_FREEZE.json"))
add = json.load(open(f"{REPO}/TBRT02/out/TBRT02_SEQUENTIAL_ADDENDUM.json"))
c3  = json.load(open(f"{REPO}/TBRT02/out/TBRT02_C3_RAW_CLOSE.json"))

def split(R):
    by = {}
    for r in R: by.setdefault(r["arm"], []).append(r)
    for k in by: by[k].sort(key=lambda x: x["index"])
    return by

bA, bB = split(A), split(B)

def stats(v):
    return {"n": len(v), "min": min(v), "median": st.median(v), "mean": round(st.mean(v), 1), "max": max(v)}

def arm_block(by):
    out = {}
    for arm in ("SHAM", "SELECTIVE", "DISPLACED"):
        a = by[arm]
        out[arm] = {
            "CERTAIN_duration": stats([r["CERTAIN_duration"] for r in a]),
            "POSSIBLE_duration": stats([r["POSSIBLE_duration"] for r in a]),
            "CERTAIN_exposure": stats([r["CERTAIN_exposure"] for r in a]),
            "POSSIBLE_exposure": stats([r["POSSIBLE_exposure"] for r in a]),
            "CERTAIN_max_cells": stats([r["CERTAIN_max_cells"] for r in a]),
            "worlds_where_POSSIBLE_is_IDENTICAL_to_CERTAIN": sum(
                1 for r in a if r["CERTAIN_duration"] == r["POSSIBLE_duration"]
                and r["CERTAIN_exposure"] == r["POSSIBLE_exposure"]),
        }
    return out

DA, DB = bA["DISPLACED"], bB["DISPLACED"]
r1_A = sum(r["R1_FIRED"] for r in DA); r1_B = sum(r["R1_FIRED"] for r in DB)
r2_A = sum(r["R2_FIRED"] for r in DA); r2_B = sum(r["R2_FIRED"] for r in DB)
# internal consistency: in DISPLACED, is R2 exactly the complement of POSSIBLE==CERTAIN ?
ident_B = {r["index"] for r in DB if r["CERTAIN_duration"] == r["POSSIBLE_duration"]
           and r["CERTAIN_exposure"] == r["POSSIBLE_exposure"]}
r2set_B = {r["index"] for r in DB if r["R2_FIRED"]}

# paired, EXPLORATORY: CERTAIN duration, DISPLACED minus SHAM, by index
pair = {}
for arm in ("SELECTIVE", "DISPLACED"):
    d = [next(x for x in bB[arm] if x["index"] == r["index"])["CERTAIN_duration"] - r["CERTAIN_duration"]
         for r in bB["SHAM"]]
    pair[f"{arm}_minus_SHAM_CERTAIN_duration"] = {
        **stats(d), "n_positive": sum(1 for v in d if v > 0), "n_zero": sum(1 for v in d if v == 0),
        "n_negative": sum(1 for v in d if v < 0)}

d = {
 "MISSION": "TBRT02",
 "SECTION": "C4 — the analysis",
 "GENERATED_UTC": subprocess.run(["date","-u","+%Y-%m-%dT%H:%M:%S+00:00"],capture_output=True,text=True).stdout.strip(),
 "PARENT_C3_CONTENT_HASH": c3["C3_CONTENT_HASH"],
 "METHODS_HASH": frz["METHODS_HASH"],
 "N_TRIPLES": 41,

 "THE_HEADLINE": "the frozen refutation condition did not fire — and it COULD NOT HAVE. Under the "
   "only reading its own words support, the intersection it tests is empty by construction, for "
   "every possible sequence of rows. The zero is therefore uninformative, and the pre-registered "
   "sequential bound must not be read as evidence about the world.",

 "1_WHAT_WAS_FROZEN_IN_WORDS": frz["THE_REFUTATION_CONDITION_FROZEN_BEFORE_ANY_WORLD"],
 "2_IT_WAS_NEVER_OPERATIONALISED_IN_CODE": {
   "claim": "no file under TBRT02/code contained any procedure for the words absorb / refute / "
            "descendant before the campaign; the three fixtures certify the intervention mechanics "
            "(mass conservation, no randomness consumed, Chebyshev >= 2, determinism, refusal "
            "without capacity) and nothing about the enumeration.",
   "consequence": "the mapping from those words to an enumeration was made AFTER the raw was "
                  "closed at C3. That is a real degree of freedom. It was neutralised the only "
                  "honest way available: three readings were declared in "
                  "TBRT02/work/TBRT02_C4_ANALYSIS_NOTES.md, committed at 2a78e68, BEFORE any of "
                  "them was computed, and all are reported.",
   "notes_commit": "2a78e68",
 },
 "3_THE_THREE_READINGS": {
   "R1_strict": "CERTAIN(daughter) intersect DESC(competitor) — the frozen condition, literally",
   "R2_permissive": "POSSIBLE(daughter) intersect DESC(competitor)",
   "R3_quantum": "a Y quantum descended from the displaced mass occupying a CERTAIN cell — "
                 "NOT COMPUTABLE from the archives: schema TLMR01-ARCHIVE-1 carries no hop ledger "
                 "(no pq_yhop among its arrays), so quantum identity is not recoverable. Recorded "
                 "as not computable rather than silently dropped.",
   "DESC_definition": "the ANY-source closure from the competitor cell — the same rule the frozen "
                      "model calls POSSIBLE, applied to the competitor root.",
 },

 "4_TWO_DEFECTS_IN_MY_OWN_INSTRUMENT_FOUND_BEFORE_USE": {
   "first": "the competitor's descendant set was seeded at t_m, but the archive records the fork "
            "row BEFORE the intervention, so the destination cell is absent there. Symptom: the "
            "displaced mass appeared to die instantly in every world.",
   "second": "after seeding at t_m+1 instead, three worlds (85, 240, 347) still showed nothing. "
             "Cell-by-cell check: no ydeath row and an occupied Moore-1 neighbour — the quantum "
             "had HOPPED on the first step and the seeding lost it.",
   "root_cause": "the t_m row predates the intervention, so it lacks the displaced mass AND still "
                 "carries the parent's Y. The second half affects the frozen Model C as applied "
                 "here: in SELECTIVE and DISPLACED the parent cell counts as a source at the first "
                 "transition. Not an error in CLEA01, where the recorded row was the right start.",
   "resolution": "both variants computed side by side, neither chosen on its result.",
 },
 "5_THE_TWO_VARIANTS": {
   "A": "prev(t_m) = the recorded row, exactly as clea01_lineage_i1.run does",
   "B": "prev(t_m) = the row reconstructed to its post-intervention state from meta.intervention "
        "alone (parent_cells, competitor_cell, competitor_mass) — no free parameter",
   "B_reconstruction_audited_per_world": {
     "DISPLACED_mass_conserved_on_every_world": all(r["reconstruction_audit"]["MASS_CONSERVED"] for r in DB),
     "SHAM_rows_unchanged": all(r["reconstruction_audit"]["PARENT_Y_REMOVED"] == 0
                                and r["reconstruction_audit"]["placed_at_competitor"] == 0
                                for r in bB["SHAM"]),
     "parent_Y_removed_min_med_max": [min(r["reconstruction_audit"]["PARENT_Y_REMOVED"] for r in DB),
                                      st.median([r["reconstruction_audit"]["PARENT_Y_REMOVED"] for r in DB]),
                                      max(r["reconstruction_audit"]["PARENT_Y_REMOVED"] for r in DB)],
   },
   "THE_TWO_VARIANTS_AGREE_ON_EVERY_HEADLINE": (r1_A == r1_B == 0) and (r2_A == r2_B),
 },

 "6_R1_THE_FROZEN_CONDITION_ENUMERATED": {
   "variant_A_triples_fired": r1_A, "variant_B_triples_fired": r1_B,
   "variant_A_total_rows": sum(r["R1_rows"] for r in DA),
   "variant_B_total_rows": sum(r["R1_rows"] for r in DB),
   "OUT_OF": 41,
 },
 "7_WHY_THAT_ZERO_IS_NOT_EVIDENCE": {
   "proof": "let d be a cell at t+1. d in CERTAIN(t+1) requires S(d,t) non-empty and contained in "
            "CERTAIN(t). d in DESC(t+1) requires S(d,t) to meet DESC(t). Both together force some "
            "c in CERTAIN(t) intersect DESC(t). At t_m the two roots are disjoint, because the "
            "displacement enforces Chebyshev >= 2 from every daughter cell "
            "(MIN_SEPARATION_FROM_THE_DAUGHTER = 2, certified by fixture 4). By induction the "
            "intersection is empty at every step, for EVERY sequence of rows.",
   "adversarial_search": cap,
   "reading": "4000 synthetic worlds unconstrained by the engine's physics — cells free to appear "
              "and vanish — fired the frozen rule 0 times. The SAME search, with the daughter side "
              "relaxed from ALL-sources to ANY-source, fired "
              f"{cap['RELAXED_any_source_control']['fired']} times at a median of "
              f"{cap['RELAXED_any_source_control']['median_first_step']} steps. The search is "
              "demonstrably capable; the rule is not.",
   "CONCLUSION": "the frozen refutation condition is VACUOUS. CERTAIN is immune to contamination "
                 "BY DEFINITION — 'all ancestral paths lead to the root' cannot admit a foreign "
                 "path — so the condition tests the definition, not the world. The claim in "
                 "tbrt02_displace.py that the displacement makes Model C 'falsifiable instead of "
                 "merely self-consistent' is NOT established by this condition.",
 },
 "8_THE_SEQUENTIAL_READING_MUST_NOT_BE_USED": {
   "preregistered_value_at_n_41": add["PREREGISTERED_READINGS"]["41"],
   "formula_as_frozen": add["VERIFIED_THREE_INDEPENDENT_WAYS"]["closed_form"],
   "alpha": add["ALPHA"],
   "ITS_ONLY_VALIDITY_CONDITION_AS_FROZEN": add["SELECTION_BIAS_CAVEAT"]["the_only_validity_condition"],
   "WHY_IT_IS_WITHHELD": "the bound is a statement about a Bernoulli parameter that the statistic "
     "could in principle have detected. Here the statistic is identically zero by construction, so "
     "there is no parameter to bound. Reporting 'the per-triple absorption probability is at most "
     "7.05 per cent' would dress a tautology as a measurement. It is therefore NOT reported as a "
     "finding. The instrument itself is sound and remains available to any successor whose "
     "statistic can vary.",
 },

 "9_R2_WHAT_THE_DATA_DO_SAY": {
   "status": "SECONDARY AND NOT PRE-REGISTERED. Declared before computation, not before the raw.",
   "variant_A_triples_contaminated": r2_A, "variant_B_triples_contaminated": r2_B, "OUT_OF": 41,
   "first_contact_steps_after_t_m_variant_B": stats([r["R2_first_t"] - r["t_m"] for r in DB if r["R2_FIRED"]]),
   "internal_consistency": {
     "claim": "in DISPLACED, R2 fires exactly on the worlds where POSSIBLE is not identical to CERTAIN",
     "holds": (r2set_B == ({r['index'] for r in DB} - ident_B)),
   },
   "competitor_viability_variant_B": {
     "DESC_duration": stats([r["DESC_duration"] for r in DB]),
     "DESC_max_cells": stats([r["DESC_max_cells"] for r in DB]),
     "worlds_where_the_displaced_mass_left_no_descendant": sum(1 for r in DB if r["DESC_duration"] <= 1),
     "note": "under variant A three worlds looked dead on arrival; that was the seeding defect, "
             "not the world. Under B the minimum descendant lifetime is "
             f"{min(r['DESC_duration'] for r in DB)} steps.",
   },
 },
 "10_ARM_SUMMARIES": {"VARIANT_A": arm_block(bA), "VARIANT_B": arm_block(bB)},
 "11_THE_CLEA01_FAILURE_MODE_REPRODUCED": {
   "SELECTIVE": f"{arm_block(bB)['SELECTIVE']['worlds_where_POSSIBLE_is_IDENTICAL_to_CERTAIN']}/41 "
                "worlds have POSSIBLE identical to CERTAIN — removing the parent leaves the "
                "daughter as the only Y source, so everything descends from her and the lineage "
                "object explains nothing. This is precisely why CLEA01 closed, reproduced here "
                "without exception.",
   "SHAM": f"{arm_block(bB)['SHAM']['worlds_where_POSSIBLE_is_IDENTICAL_to_CERTAIN']}/41",
   "DISPLACED": f"{arm_block(bB)['DISPLACED']['worlds_where_POSSIBLE_is_IDENTICAL_to_CERTAIN']}/41",
   "WHAT_THE_DISPLACEMENT_ACTUALLY_BOUGHT": "in 17 of 41 worlds the competitor's descendants reach "
     "the daughter's POSSIBLE set, so the permissive lineage is no longer trivially the ambient "
     "population. In the remaining 24 the two fronts never meet within the horizon and the "
     "degeneracy CLEA01 identified persists. That is a partial repair, not a solved problem, and "
     "it is not what the frozen condition was adjudicating.",
 },
 "12_EXPLORATORY_PAIRED_CONTRASTS": {
   "status": "EXPLORATORY. The frozen primary adjudication is the refutation condition and nothing "
             "else. No error rate is claimed for anything in this block and no hypothesis is "
             "declared tested by it.",
   "variant_B_paired_by_index": pair,
 },

 "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "X_LAWSPEC_BASELINE": "UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
 "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
 "MODEL_C_STATUS": "NOT_REFUTED AND NOT CORROBORATED BY THIS EXPERIMENT — the adjudicating "
   "condition cannot discriminate. Its CERTAIN set remains sound by construction, which was never "
   "in question.",
 "NOTHING_HERE_ESTABLISHES_ANY_CLAIM_ABOUT_LINEAGE_IN_THE_WORLD": True,
}
d["C4_CONTENT_HASH"] = F.H.content_digest(d, extra_excluded=("C4_CONTENT_HASH",))
open(f"{REPO}/TBRT02/out/TBRT02_C4_ANALYSIS.json", "w").write(json.dumps(d, indent=1) + "\n")
print("R1", r1_A, r1_B, "| R2", r2_A, r2_B, "| variants agree:", d["5_THE_TWO_VARIANTS"]["THE_TWO_VARIANTS_AGREE_ON_EVERY_HEADLINE"])
print("R2 == complement of identical:", d["9_R2_WHAT_THE_DATA_DO_SAY"]["internal_consistency"]["holds"])
print("C4_CONTENT_HASH", d["C4_CONTENT_HASH"])
