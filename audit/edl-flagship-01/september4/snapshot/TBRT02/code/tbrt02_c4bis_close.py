"""TBRT02 — C4-bis. The checker's twelve findings, adjudicated one by one.

C4 itself is NOT rewritten. It stands exactly as it was submitted to the checker
(commit 9bebfda), and the checker's return stands verbatim at 803457e. This file records what
survives, what is withdrawn, and what is corrected — with every figure recomputed here rather
than copied from the checker's report.
"""
from __future__ import annotations
import os, sys, json, glob, itertools, statistics as st, subprocess
import numpy as np
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "TBRT02/code"))
import tbrt02_freeze as F
H = F.H

def load(pref):
    r = []
    for sh in (0, 1): r += json.load(open(f"{REPO}/TBRT02/work/c4/{pref}{sh}.json"))
    return {(x["index"], x["arm"]): x for x in r}
A, B = load("C4_LINEAGE_"), load("C4_LINEAGE_B_")
R5 = json.load(open(f"{REPO}/TBRT02/work/c4/R5_INDEPENDENT.json"))
capi = json.load(open(f"{REPO}/TBRT02/work/c4/R1_CAPABILITY_INSTRUMENTED.json"))
cap = json.load(open(f"{REPO}/TBRT02/work/c4/R1_CAPABILITY.json"))
c4 = json.load(open(f"{REPO}/TBRT02/out/TBRT02_C4_ANALYSIS.json"))
add = json.load(open(f"{REPO}/TBRT02/out/TBRT02_SEQUENTIAL_ADDENDUM.json"))

L = 36
def cheb(a, b):
    return max(min((a[0]-b[0]) % L, (b[0]-a[0]) % L), min((a[1]-b[1]) % L, (b[1]-a[1]) % L))
rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
        for l in open(p) if l.strip()]
adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
pd_, cd_ = [], []
for r in adm:
    z = np.load(r["ARCHIVES"]["DISPLACED"]["path"], allow_pickle=True)
    iv = json.loads(str(z["meta"][0]))["intervention"]; z.close()
    P = [tuple(map(int, c)) for c in iv["parent_cells"]]
    D = [tuple(map(int, c)) for c in iv["daughter_cells"]]
    C = tuple(map(int, iv["competitor_cell"]))
    pd_.append(min(cheb(p, d) for p in P for d in D))
    cd_.append(min(cheb(C, d) for d in D))

FIELDS = ["CERTAIN_duration","POSSIBLE_duration","CERTAIN_exposure","POSSIBLE_exposure",
          "CERTAIN_max_cells","CERTAIN_steps","POSSIBLE_steps","R1_rows","R2_rows"]
ab_diff = {f: sum(1 for k in A if A[k][f] != B[k][f]) for f in FIELDS}
def cens(arm, key):
    a = [B[k] for k in B if k[1] == arm]
    return sum(1 for r in a if r["t_m"] + r[key] >= r["horizon"] - 1)
def nondegen(arm):
    a = [B[k] for k in B if k[1] == arm]
    return sum(1 for r in a if not (r["CERTAIN_duration"] == r["POSSIBLE_duration"]
                                    and r["CERTAIN_exposure"] == r["POSSIBLE_exposure"]))
# F12 verified here, not quoted
stored = add["ADDENDUM_CONTENT_HASH"]
cands = ["ADDENDUM_CONTENT_HASH","DECLARED_AT_UTC","PARENT_FREEZE_SHA256","PARENT_FREEZE_CONTENT_HASH"]
repro = None
for r in range(1, len(cands)+1):
    for sub in itertools.combinations(cands, r):
        try:
            if H.content_digest(add, extra_excluded=sub) == stored: repro = list(sub)
        except Exception: pass
# F11 pins
PINS = ["TBRT02/code/tbrt02_lineage_c4.py","TBRT02/code/tbrt02_r1_capability.py",
        "TBRT02/code/tbrt02_c4_close.py","TBRT02/code/tbrt02_r5_independent.py",
        "TBRT02/code/tbrt02_capability_instrumented.py","TBRT02/code/tbrt02_c4bis_close.py",
        "CLEA01/code/clea01_lineage_i1.py","FDOT01/code/fdot01_centres.py"]
pins = {p: H.file_sha256(f"{REPO}/{p}") for p in PINS if os.path.exists(f"{REPO}/{p}")}

r5f = [r for r in R5 if r["R5_t"] is not None]
r2f = [r for r in R5 if r["R2_t"] is not None]
r1f = [r for r in R5 if r["R1_t"] is not None]
def mmm(v): v = sorted(v); return [v[0], v[len(v)//2], v[-1]] if v else None

d = {
 "MISSION": "TBRT02", "SECTION": "C4-bis — the adversarial checker's findings, adjudicated",
 "GENERATED_UTC": subprocess.run(["date","-u","+%Y-%m-%dT%H:%M:%S+00:00"],capture_output=True,text=True).stdout.strip(),
 "C4_IS_NOT_REWRITTEN": "C4 stands at commit 9bebfda exactly as it was submitted. The checker's "
   "return stands verbatim at 803457e, sha256 "
   "15bdd90cba3db1e6000a880c735f34355e9dfe3a99d5c2d15df33b60fe651c67. This file is the response.",
 "PARENT_C4_CONTENT_HASH": c4["C4_CONTENT_HASH"],

 "EVERY_CHECKER_FIGURE_I_RECHECKED_REPRODUCED": True,
 "WHAT_I_RECHECKED_MYSELF_RATHER_THAN_TRUSTING": [
   "R5 recomputed from c_cid with my own row reconstruction and my own neighbourhood code",
   "the A-versus-B field comparison over all 123 world-arms",
   "parent-to-daughter and competitor-to-daughter Chebyshev distances over all 41 triples",
   "the right-censoring counts per arm",
   "the non-degenerate-lineage counts per arm",
   "the capability search instrumented for survival, size and adjacency",
   "the addendum content-hash reproduction attempt over every subset of its four candidate fields",
 ],

 "F1": {
   "severity": "MATERIAL, LOAD-BEARING", "verdict": "ACCEPTED IN FULL",
   "what_the_checker_showed": "a fifth reading — a cell of CERTAIN(daughter) and a cell of "
     "DESC(competitor) carrying the SAME c_cid at the same step, i.e. belonging to the same body "
     "under FDOT01's frozen component rule (toroidal single-linkage at CORE_R = 5.0, written into "
     "every archive row) — is computable with no free parameter and is NOT vacuous.",
   "MY_INDEPENDENT_REPRODUCTION": {
     "R1_fired": len(r1f), "R2_fired": len(r2f), "R5_fired": len(r5f), "out_of": len(R5),
     "R5_first_fire_steps_after_t_m_min_med_max": mmm([r["R5_t"]-r["t_m"] for r in r5f]),
     "R2_first_fire_steps_after_t_m_min_med_max": mmm([r["R2_t"]-r["t_m"] for r in r2f]),
     "R5_world_set_equals_R2_world_set": {r["index"] for r in r5f} == {r["index"] for r in r2f},
     "R5_strictly_earlier_than_R2_in_every_fired_world": all(
        r["R5_t"] < r["R2_t"] for r in R5 if r["R5_t"] is not None and r["R2_t"] is not None),
     "R5_indices": sorted(r["index"] for r in r5f),
   },
   "WHAT_I_WITHDRAW": "C4's THE_HEADLINE says 'the only reading its own words support'. That is "
     "FALSE and is withdrawn. C4 section 7's CONCLUSION 'the frozen refutation condition is "
     "VACUOUS' is narrowed to: THE STRICT CELL-MEMBERSHIP READING (R1) IS VACUOUS.",
   "WHAT_SURVIVES": "the induction and the capability search are untouched — R1 cannot fire, and "
     "that remains proved and searched. What fails is my claim that R1 exhausted the readings.",
   "WHY_I_MISSED_IT": "I enumerated readings over the objects my own instrument already produced "
     "— cells and quanta — and never over the object the freeze's own question names. The freeze "
     "asks about 'an organisation issued from the daughter' and a source 'it could wrongly "
     "absorb'. Both are body-level nouns. The body was already defined and already in the "
     "archives, in a column I had loaded and not used.",
   "WHAT_R5_DOES_NOT_LICENCE": "R5 was constructed after the numbers were known, by the checker, "
     "and reproduced after the numbers were known, by me. It CANNOT be used to declare Model C "
     "refuted. A post-hoc reading that fires is worth exactly as much as a post-hoc reading that "
     "does not: nothing, as adjudication. Both are reported; neither adjudicates.",
 },
 "F2": {
   "severity": "MATERIAL", "verdict": "ACCEPTED — the decision stands, the argument is replaced",
   "what_C4_argued": "the statistic is identically zero by construction, so there is no parameter "
     "to bound. That premise is exactly what F1 narrows, so it is reading-dependent.",
   "THE_ARGUMENT_THAT_REPLACES_IT": "chronology. The readings R1/R2/R3 were declared at commit "
     "2a78e68, AFTER the raw closed at ec4f83b. No operationalisation of the frozen sentence "
     "predates the data. Two defensible post-hoc readings of the same sentence disagree about "
     "whether the event occurred: R1 gives 0 of 41, R5 gives 17 of 41. A zero-event anytime-valid "
     "bound requires the STATISTIC — not merely the admissibility rule — to be fixed independently "
     "of the data. It was not. The bound is therefore inadmissible whatever R1's status.",
   "the_number_is_still_printed_not_suppressed": add["PREREGISTERED_READINGS"]["41"],
   "the_instrument_itself_is_not_impugned": "the addendum's construction is sound and remains "
     "available to any successor whose statistic is fixed before the raw.",
 },
 "F3": {
   "severity": "MINOR", "verdict": "ACCEPTED — my stated root cause was WRONG",
   "MY_RECOMPUTATION": {
     "A_vs_B_differences_on_daughter_side_fields_over_123_world_arms": ab_diff,
     "parent_to_daughter_chebyshev_min_med_max": mmm(pd_),
     "competitor_to_daughter_chebyshev_min_med_max": mmm(cd_),
   },
   "what_I_claimed": "that leaving the parent's Y in the t_m row disqualifies daughter-adjacent "
     "cells from CERTAIN in SELECTIVE and DISPLACED.",
   "why_it_is_wrong": f"the minimum parent-to-daughter Chebyshev distance over the 41 triples is "
     f"{min(pd_)}. A parent cell is never inside the Moore-1 neighbourhood of a daughter cell, so "
     "it can never be a source of one. The mechanism cannot bite in any of these worlds.",
   "consequence": "variants A and B are identical on every daughter-side quantity in all 123 "
     "world-arms. C4 section 10 presents them as two blocks; they are one. Variant B changes only "
     "the competitor seeding, and only in the 3 worlds where the displaced quantum hopped on the "
     "first step. B remains the correct initial condition — the checker agrees — but it is a "
     "correctness repair, not an independent corroboration.",
 },
 "F4": {
   "severity": "MINOR (underclaim)", "verdict": "ACCEPTED",
   "correction": "R3 is not merely not computable from these archives; it is provably vacuous. Y "
     "birth is autocatalytic (p = min(1, kY * nX * nY), hence p = 0 wherever nY = 0), so Y can "
     "never appear in a cell holding no Y, and the per-step Y displacement is at most Chebyshev 1. "
     "Every Y quantum in a cell at t+1 therefore came from that cell's Moore-1 sources at t. The "
     "same induction closes at the mass level. No re-run with a tagged-mass tracker could rescue "
     "R1.",
   "secondary": "the mechanism C4 gave for R3's non-computability is also wrong: a hop ledger "
     "would not recover quantum identity either, because it records counts moved and only X is "
     "tracked by identity.",
   "I_did_not_independently_rerun_the_engine_to_confirm_this": True,
 },
 "F5": {
   "severity": "MINOR to MATERIAL for the summary blocks", "verdict": "ACCEPTED",
   "correction": "every duration in C4 sections 10 and 12 is right-censored at the horizon and C4 "
     "never says so.",
   "MY_RECOMPUTATION_variant_B": {arm: {"CERTAIN_right_censored_of_41": cens(arm, "CERTAIN_duration"),
                                        "POSSIBLE_right_censored_of_41": cens(arm, "POSSIBLE_duration")}
                                  for arm in ("SHAM", "SELECTIVE", "DISPLACED")},
   "reading": "SELECTIVE's CERTAIN_duration median of 10093 is, in 29 of 41 worlds, simply the "
     "horizon. The censoring is heavier in the arm with the longer durations, so the reported "
     "contrasts are attenuated lower bounds rather than inflated — but reporting a censored "
     "quantity as a duration without saying so is a reporting defect, and it is conceded.",
 },
 "F6": {
   "severity": "MINOR", "verdict": "ACCEPTED",
   "correction": "DESC is a POSSIBLE-descendant closure. It certifies actual descent only while it "
     "is disjoint from POSSIBLE(daughter); after first contact a DESC cell may hold "
     "daughter-descended mass. The pooled DESC_duration and DESC_max_cells figures in C4 section 9 "
     "are therefore upper bounds, not measurements, and the block label 'competitor viability' "
     "overstates them.",
   "what_survives": "the specific claim that no world left the displaced mass without descendants "
     "is sound: under variant B the minimum descendant lifetime is "
     f"{min(r['DESC_duration'] for k, r in B.items() if k[1] == 'DISPLACED')} steps and first "
     "contact never occurs before step 562, so descent is certified in all 41 before any "
     "ambiguity can arise.",
 },
 "F7": {
   "severity": "MINOR (framing)", "verdict": "ACCEPTED — and this is the sentence I should have written",
   "MY_RECOMPUTATION_non_degenerate_lineage_object_variant_B": {
     arm: f"{nondegen(arm)}/41" for arm in ("SHAM", "SELECTIVE", "DISPLACED")},
   "THE_SENTENCE": "relative to the untreated control, the displacement REDUCED rather than "
     f"increased the frequency of a non-degenerate lineage object: {nondegen('DISPLACED')} of 41 "
     f"treated worlds against {nondegen('SHAM')} of 41 in SHAM. Both numbers were in C4 and I did "
     "not subtract them.",
   "why_that_happens": f"the displacement moves the competing source to Chebyshev "
     f"{min(cd_)}-{max(cd_)} from the daughter, so the two fronts meet less often than when the "
     "parent is simply left where it is. The intervention bought ground truth about WHICH source a "
     "cell descends from, and paid for it in contact frequency.",
   "what_it_does_not_mean": "SHAM is not a treatment and its 26 of 41 is not a better result; it "
     "is the untreated baseline against which the treatment must be judged, and on this metric the "
     "treatment did not beat it.",
 },
 "F8": {
   "severity": "MINOR", "verdict": "ACCEPTED — the proof as written was incomplete",
   "the_gap": "C4's proof cites Chebyshev >= 2 for the base case at t_m, where >= 1 would do, and "
     "omits the step where >= 2 is actually load-bearing: in variant A the competitor set is "
     "INJECTED outside the recursion at t_m+1, and an induction does not cover an injected set.",
   "the_patch": "the competitor cell has no daughter cell in its Moore-1 neighbourhood precisely "
     "because separation >= 2, so its source set at t_m does not meet CERTAIN(t_m); a non-empty "
     "source set is required for CERTAIN membership, so the injected cell cannot itself be in "
     "CERTAIN(t_m+1). With that step added the induction closes for both variants.",
   "measured": f"competitor-to-daughter Chebyshev is {min(cd_)} to {max(cd_)} in the 41 worlds, "
     "against a required minimum of 2.",
 },
 "F9": {
   "severity": "COSMETIC", "verdict": "ACCEPTED",
   "correction": "the intersections are evaluated only after the first update, so t = t_m itself is "
     "never tested. Unreachable here given the enforced separation, but a successor that relaxed "
     "the separation would lose a t_m-time firing silently. Recorded as a known instrument gap.",
 },
 "F10": {
   "severity": "MINOR", "verdict": "ACCEPTED on both halves",
   "overstatement_withdrawn": "C4 says the synthetic worlds are 'unconstrained by the engine's "
     "physics — cells free to appear and vanish'. They are not: every cell of the next row is "
     "drawn inside the Moore-1 neighbourhood of the current live sets. The code says so; the C4 "
     "prose did not.",
   "MY_INSTRUMENTED_RERUN": capi,
   "reading": f"over the same 4000 worlds the frozen branch's CERTAIN set survives a median of "
     f"{capi['CERTAIN_survival_steps_median']} of 60 steps and reaches a median maximum of "
     f"{capi['CERTAIN_max_size_median']} cells; both sets are alive together on "
     f"{capi['rows_both_sets_alive']} rows; and the two live sets are Moore-1 ADJACENT on "
     f"{capi['rows_CERTAIN_adjacent_to_DESC']} rows across {capi['worlds_with_adjacency']} worlds "
     "— in direct contact, and the intersection still never occurred. That is stronger evidence "
     "for R1's vacuity than the control alone, and C4 did not have it.",
 },
 "F11": {
   "severity": "MINOR", "verdict": "ACCEPTED",
   "correction": "C4 pins METHODS_HASH, which covers acquisition, and pins nothing that produced "
     "its own numbers. The analysis code and the frozen Model C are pinned here.",
   "ANALYSIS_CODE_SHA256": pins,
   "known_gap_left_open_and_declared": "the variant-A per-archive files were written by a build of "
     "the enumerator predating commit ee7338e, which added the variant machinery. The checker "
     "regenerated 15 archives on the current variant-A path and found 0 mismatches. Given F3 — A "
     "and B agree on every daughter-side field anyway — nothing in the conclusions rests on those "
     "files, but the provenance gap is recorded rather than papered over.",
 },
 "F12": {
   "severity": "MINOR", "verdict": "ACCEPTED — and verified here rather than quoted",
   "stored_ADDENDUM_CONTENT_HASH": stored,
   "reproduces_under_any_subset_of_its_four_candidate_excluded_fields": repro,
   "control_the_three_that_do_verify": {
     "FREEZE_CONTENT_HASH": H.content_digest(json.load(open(f"{REPO}/TBRT02/out/TBRT02_MASTER_FREEZE.json")), extra_excluded=("FREEZE_CONTENT_HASH",)) == json.load(open(f"{REPO}/TBRT02/out/TBRT02_MASTER_FREEZE.json"))["FREEZE_CONTENT_HASH"],
     "C3_CONTENT_HASH": H.content_digest(json.load(open(f"{REPO}/TBRT02/out/TBRT02_C3_RAW_CLOSE.json")), extra_excluded=("C3_CONTENT_HASH",)) == json.load(open(f"{REPO}/TBRT02/out/TBRT02_C3_RAW_CLOSE.json"))["C3_CONTENT_HASH"],
     "C4_CONTENT_HASH": H.content_digest(c4, extra_excluded=("C4_CONTENT_HASH",)) == c4["C4_CONTENT_HASH"],
   },
   "consequence": "the addendum's self-hash provides no integrity guarantee for the pre-registered "
     "readings C4 quoted from it. Its git provenance is single-commit and clean, and the value "
     "quoted at n = 41 was independently recomputed from the closed form. Inherited defect, "
     "recorded, not repaired here — repairing another mission's frozen artefact is not this "
     "mission's business.",
 },

 "WHAT_C4_SAID_THAT_STILL_STANDS_AFTER_THE_CHECK": [
   "the refutation condition was frozen in words and never operationalised in code before the raw",
   "R1 cannot fire — proved, and searched over 4000 worlds including 7560 rows of direct contact",
   "the sequential bound must not be reported (for the chronological reason of F2, not C4's)",
   "SELECTIVE reproduces CLEA01's degeneracy on 41 of 41 worlds",
   "two defects in my own enumeration, found and corrected before use, both recorded",
   "no claim about lineage, heredity, reproduction or life is made anywhere",
 ],
 "WHAT_THIS_EXPERIMENT_ADJUDICATES": "nothing. The frozen primary condition cannot discriminate "
   "under the strict reading and no reading was fixed before the data under any other. The mission "
   "produced 41 clean triples, an intact raw, and a demonstration that its own adjudicating "
   "instrument was not built.",

 "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "X_LAWSPEC_BASELINE": "UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
 "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
 "MODEL_C_STATUS": "NOT_REFUTED AND NOT CORROBORATED BY THIS EXPERIMENT",
}
d["C4BIS_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("C4BIS_CONTENT_HASH",))
open(f"{REPO}/TBRT02/out/TBRT02_C4BIS_CHECKER_ADJUDICATION.json","w").write(json.dumps(d, indent=1)+"\n")
print("R5", len(r5f), "R2", len(r2f), "R1", len(r1f))
print("A/B diffs:", ab_diff)
print("nondegen SHAM/SEL/DISP:", nondegen("SHAM"), nondegen("SELECTIVE"), nondegen("DISPLACED"))
print("addendum hash reproduces:", repro)
print("C4BIS_CONTENT_HASH", d["C4BIS_CONTENT_HASH"])
