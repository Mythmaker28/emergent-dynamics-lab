"""CLEA01 closure §13 and §14 — the terminal disposition, the final report and SHA256SUMS."""
from __future__ import annotations
import datetime as dt, json, os, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H
OUT = f"{REPO}/CLEA01/out"
TERMINAL = "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED"
VOCAB = ["DISTRIBUTED_CAUSAL_LINEAGE_OBJECT_IDENTIFIED__ONE_INTERVENTION_TEST_ELIGIBLE",
         "DISTRIBUTED_CAUSAL_LINEAGE_NOT_DISTINCT_FROM_LOCKED_COMPONENT__NO_NEW_EXPERIMENT",
         "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED",
         "CLEA01_TECHNICALLY_INVALID"]


def main():
    L = {n: json.load(open(f"{OUT}/{n}")) for n in os.listdir(OUT) if n.endswith(".json")}
    g = L["CLEA01_STRUCTURAL_GATES_FINAL.json"]
    a = L["CLEA01_CHECKER_ADJUDICATION.json"]
    s = L["CLEA01_CHECKER_SCOPE_AUDIT.json"]
    p = L["CLEA01_PARENT_RECOMPUTATION.json"]
    k = L["CLEA01_CAUSAL_KERNEL_ADJUDICATION.json"]
    hi = L["CLEA01_HIDDEN_INPUT_AUDIT.json"]
    nv = L["CLEA01_FINAL_NONVACUITY_ADJUDICATION.json"]
    ks = L["CLEA01_KNOWN_SUCCESS_ADJUDICATION.json"]
    am = L["CLEA01_AMBIENT_SPECIFICITY_ADJUDICATION.json"]
    ch = L["CLEA01_DEVELOPMENT_VALIDATION_CHRONOLOGY.json"]
    im = L["CLEA01_IMPLEMENTATION_INDEPENDENCE_ADJUDICATION.json"]
    ce = L["CLEA01_CAUSAL_EMERGENCE_FINAL_STATUS.json"]
    ex = nv["THE_QUALITATIVE_REQUIREMENT"]["EXHIBIT"]

    d = {
        "MISSION": "CLEA01", "SECTION": "final disposition",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "FINAL_DISPOSITION": TERMINAL,
        "TERMINAL_VOCABULARY": VOCAB, "NO_FIFTH_STRING_WAS_INVENTED": True,
        "WHY_NOT_THE_OTHER_THREE": {
            VOCAB[0]: "requires all ten gates. Three fail and two are not identifiable.",
            VOCAB[1]: "names the LOCKED COMPONENT. Model C differs from A in 62 of 66 arms, and one "
                      "exhibited arm carries a continuation A terminates after %d rows that C "
                      "retains for %d with enumerable witnesses. Choosing this string would put a "
                      "false statement in the record. C's failure is against B."
                      % (ex["A_duration"], ex["C_certain_duration"]),
            VOCAB[3]: "requires a confirmed load-bearing implementation, chronology or hidden "
                      "input/outcome defect. There is none: the parent's six numbers reproduce, "
                      "the split reproduces 33 of 33, the kernel is exact by two independent "
                      "routes, no forbidden archive key is touched at run time, and the checker "
                      "recorded LOAD_BEARING_DEFECT_COUNT = 0. Promoting a MATERIAL finding here "
                      "would manufacture invalidity.",
        },
        "GATES": {x["gate"]: x["VERDICT"] for x in g["GATES"]},
        "N_PASS": g["N_PASS"], "N_UNQUALIFIED_PASS": g["N_UNQUALIFIED_PASS"],
        "N_FAIL": g["N_FAIL"], "N_NOT_IDENTIFIABLE": g["N_NOT_IDENTIFIABLE"],
        "CHECKER_RETURN_STATUS": "PRESERVED_VERBATIM_BEFORE_ADJUDICATION",
        "CHECKER_RETURN_SHA256": a["CHECKER_RETURN_SHA256"],
        "CHECKERS_DISPATCHED": 1, "SECOND_CHECKER": "none", "REVIEW_CASCADE": "none",
        "LOAD_BEARING_DEFECT_COUNT": a["LOAD_BEARING_DEFECT_COUNT"],
        "N_ITEMS_ADJUDICATED": a["N_ITEMS_ADJUDICATED"],
        "CHECKER_SCOPE": {
            "modified_no_repository_file": s["MODIFIED_NO_REPOSITORY_FILE"],
            "ran_no_engine": s["RAN_NO_ENGINE"],
            "constructed_no_world": s["CONSTRUCTED_NO_WORLD"],
            "no_new_archive_anywhere": s["NO_NEW_ARCHIVE_ANYWHERE_AFTER_20_00"],
            "all_twelve_points_attacked": s["ALL_TWELVE_ATTACKED"],
            "exactly_one_verdict": s["EXACTLY_ONE_VERDICT_RETURNED"],
            "the_one_excess": "the checker ran in-memory engine trials, which the mandate forbade. "
                              "Recorded, not softened. It wrote no archive and nothing in the "
                              "terminal rests on it.",
        },
        "PARENT_FACTS_REPRODUCE": p["ALL_SIX_AGREE"],
        "OMLDCT02_PAIRED_HYPOTHESIS_REINTERPRETED": p["OMLDCT02_PAIRED_HYPOTHESIS_REINTERPRETED"],
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "OMLDCT02_PAIRED_STATISTICS": "DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT",
        "TRANSPORT_KERNEL": k["VERDICT"],
        "KERNEL_VIOLATIONS": k["ARCHIVE_MEASUREMENT"]["cells_with_no_Moore_1_predecessor"],
        "KERNEL_ROW_PAIRS_CHECKED": k["ARCHIVE_MEASUREMENT"]["consecutive_row_pairs_compared"],
        "FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY": hi["FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY"],
        "ONLINE_ID_USED_TO_DEFINE_ANCESTRY": hi["ONLINE_ID_USED_TO_DEFINE_ANCESTRY"],
        "MODEL_C_RECONSTRUCTABILITY": "YES__66_OF_66_ARMS__0_INVARIANT_VIOLATIONS",
        "MODEL_C_NONVACUITY_VERSUS_A": nv["VERDICT_VERSUS_A"],
        "MODEL_C_SPECIFICITY_VERSUS_B": nv["VERDICT_VERSUS_B"],
        "KNOWN_SUCCESS_PRESERVATION": ks["VERDICT"],
        "AMBIENT_SPECIFICITY": am["VERDICT"],
        "SPLIT_ASSIGNMENT_REPRODUCES": ch["ASSIGNMENT_REPRODUCES"],
        "IMPLEMENTATIONS_SCIENTIFICALLY_INDEPENDENT": im["SCIENTIFICALLY_INDEPENDENT"],
        "IMPLEMENTATIONS_EQUIVALENT_ENCODINGS": im["EQUIVALENT_ENCODINGS"],
        "CAUSAL_EMERGENCE_STATUS": "NOT_COMPUTED__STRUCTURAL_GATES_NOT_PASSED",
        "CAUSAL_EMERGENCE_SUBSTANTIVE_REASON": ce["SUBSTANTIVE_REASON"],
        "MODEL_SELECTED": "none", "MAX_SELECTED_IDENTITY_MODELS": 1,
        "HANDOFFS_WRITTEN": 0, "MAX_FUTURE_EXPERIMENTAL_HANDOFFS": 1,
        "FUTURE_INTERVENTION_ELIGIBILITY": "NOT_ELIGIBLE",
        "NEW_SCIENTIFIC_ENGINE_RUNS": 0, "NEW_WORLD_CONSTRUCTIONS": 0,
        "NEW_SEEDS": 0, "NEW_TRAJECTORIES": 0, "NEW_SCIENTIFIC_WORLDS_USED": 0,
        "NO_P_VALUE_WAS_COMPUTED_OR_INTERPRETED_ANYWHERE_IN_CLEA01": True,
        "WHAT_A_POSITIVE_RESULT_WOULD_HAVE_ESTABLISHED":
            "only that a distributed causal-lineage object is reconstructible and nontrivial in "
            "existing archives. Not reproduction.",
        "WHAT_THIS_RESULT_ESTABLISHES":
            "that such an object is reconstructible, provably sound, and qualitatively distinct "
            "from the locked spatial component — and that it cannot be identified as an individual "
            "from archives generated by an intervention which removes the only competing source of "
            "the substance it is made of. In the treated arm it rejects 0 of %d occupied cell-rows. "
            "The failure is a property of the intervention, not of the idea."
            % am["CELL_LEVEL"]["SELECTIVE_occupied_cell_rows_after_A"],
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
    }
    d["DISPOSITION_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("DISPOSITION_CONTENT_HASH",))
    json.dump(d, open(f"{OUT}/CLEA01_FINAL_DISPOSITION.json", "w"), indent=1)

    R = f"""# CLEA01 — FINAL REPORT

```
FINAL_DISPOSITION = {TERMINAL}
LOAD_BEARING_DEFECT_COUNT = {a['LOAD_BEARING_DEFECT_COUNT']}
NEW_SCIENTIFIC_WORLDS_USED = 0
```

## What was asked

Is the scientifically relevant individual (A) the locked spatial daughter, (B) the ambient
population, or (C) a distributed causal lineage rooted in the daughter? Answered by audit over the
66 existing OMLDCT02 paired archives, then closed by consuming one independent adversarial checker.
No world was run, no seed drawn, no parameter searched.

## The checker

Preserved verbatim before anything was acted on — `CLEA01/review/CLEA01_CHECKER_RAW.txt`,
sha256 `{a['CHECKER_RETURN_SHA256']}`, committed at C3 and unchanged since.
**{a['LOAD_BEARING_DEFECT_COUNT']} load-bearing defects.** Seventeen numbered findings, eight
MATERIAL, adjudicated here as {a['N_ITEMS_ADJUDICATED']} items, each exactly once.

The C3 record said ten corrections. That under-counted: four items were never adjudicated in
writing, one of them MATERIAL — finding 15, that no launcher existed anywhere in the repository, so
no checker could verify that the gate list, the section-8 gating rule or the four terminal strings
were faithfully transcribed. Both launchers are now committed under `CLEA01/launcher/`. That
finding is not merely adjudicated; it is closed.

One scope excess, self-declared by the checker and recorded rather than omitted: it ran in-memory
engine trials, which its mandate forbade. It wrote no archive anywhere, the 66 OMLDCT02 archives are
untouched, and nothing in the terminal rests on those trials — section 5 re-establishes the same
conclusion twice without running anything.

## The parent, unchanged

All six bound numbers reproduce from the sealed ledger and the runner's AST, without reading an
OMLDCT02 summary: 805 seeds attempted, 33 valid matched pairs against a minimum of 41,
510.56902 arm-instances against a ceiling of 512, 0 technical failures, 0 load-bearing defects.
`OMLDCT02_PAIRED_HYPOTHESIS_REINTERPRETED = false`. No p-value is computed or interpreted anywhere
in CLEA01; the only occurrences of the token family are in lists that forbid them.

## The kernel is exact, and now twice over

Derived from the engine source: the four frozen sub-shifts are (+y, −y, +x, −x), each pass re-reads
occupancy, and the subset sum over them is exactly {{−1,0,1}}² — computed here rather than asserted.
Measured from the archives: over **{k['ARCHIVE_MEASUREMENT']['consecutive_row_pairs_compared']:,}
consecutive row pairs, {k['ARCHIVE_MEASUREMENT']['cells_with_no_Moore_1_predecessor']} cells** lack a
Moore-1 predecessor, and on **{k['ARCHIVE_MEASUREMENT']['single_source_rows_used_for_the_upper_bound']:,}
single-source rows** the observed displacement set is exactly the nine Moore-1 offsets, all four
diagonals included, maximum Chebyshev 1. Too narrow would have shown as violations; too broad would
have shown as an offset outside the nine. Neither appears.

Consequence: CERTAIN is provably **sound**. It can under-claim; it cannot over-claim.

## Distinct from A — qualitatively, not by epsilon

The closure launcher refuses a difference of a few particles as evidence. It is not used. One arm,
selected by a rule stated before it was applied and satisfied by {ex['N_CANDIDATE_ARMS']} arms:

- **{ex['ARM_SELECTED']['index']} SHAM.** Model A's identity ends after **{ex['A_duration']} rows**.
  Model C's CERTAIN set runs **{ex['C_certain_duration']} rows**, every continuation carrying an
  enumerable witness — S(d) non-empty and wholly inside CERTAIN.
- On the same arm, Model C rejects **{ex['CELLS_REJECTED_OVER_THE_WHOLE_POST_A_WINDOW']:,} of
  {ex['OCCUPIED_CELLS_OVER_THE_WHOLE_POST_A_WINDOW']:,}** occupied cell-rows after A outright — not
  as uncertain, but as unreachable: no admissible source is even POSSIBLE.

Both halves of the requirement, one arm, one row.

## Not specific against B — and the number is zero

Across the SELECTIVE arms, of **{am['CELL_LEVEL']['SELECTIVE_occupied_cell_rows_after_A']:,}**
occupied cell-rows after Model A ends, Model C rejects
**{am['CELL_LEVEL']['SELECTIVE_cell_rows_rejected_outright']}**. In the same accounting on SHAM it
rejects **{am['CELL_LEVEL']['SHAM_cell_rows_rejected_outright']:,} of
{am['CELL_LEVEL']['SHAM_occupied_cell_rows_after_A']:,}**.

The masks do not "differ by a few cells" in the treated arm. On every post-fork row they do not
differ at all. That is not a defect in Model C: removing the parent leaves the daughter as the
world's only Y source, so "everything afterwards descends from the daughter" becomes true by
construction and explains nothing.

Interval accounting, per arm — SELECTIVE: {am['AMBIENT_INTERVALS_C_RETAINS_WITH_CERTAIN_WITNESS']['SELECTIVE']} retained with a
CERTAIN witness, {am['AMBIENT_INTERVALS_C_REJECTS']['SELECTIVE']} rejected,
{am['NO_AMBIENT_CONTINUATION_TO_JUDGE']['SELECTIVE']} with no continuation to judge.
SHAM: {am['AMBIENT_INTERVALS_C_RETAINS_WITH_CERTAIN_WITNESS']['SHAM']} retained,
{am['AMBIENT_INTERVALS_C_REJECTS']['SHAM']} rejected.

## The known success, and what it says about the parent

Strong containment passes {ks['STRONG_CONDITION_C_CONTAINS_A_ON_EVERY_ROW']['passing']} of 66,
failing at 402 SHAM and 518 SHAM. Republished row by row: every cell Model A carries and Model C
does not was **never CERTAIN and never POSSIBLE at any row**. Not ambiguous origin — no causal path
at all. Model A's CORE_R centroid rule tracks where a component is, not where its mass came from.

**In at least 2 of 66 arms the qualified OMLDCT02 E3 component provably contains Y mass with no
causal path to the daughter.** That bears on what `E3_DURATION` and `E3_EXPOSURE` measure. It
changes no OMLDCT02 number and reinterprets no OMLDCT02 test. It is recorded because the parent's
record does not contain it.

## The gates, scored honestly

```
G1  reconstructable ........................ PASS
G2  two implementations agree .............. PASS   (qualified: equivalent encodings)
G3  non-vacuous vs A and B ................. FAIL   (vs B, treated arm)
G4  preserves the known success ............ FAIL   (2 of 66)
G5  rejects ambient succession ............. NOT_IDENTIFIABLE
G6  explicit causal witness ................ PASS
G7  no future outcome defines ancestry ..... PASS
G8  validation: no unresolved contradiction  PASS   (qualified)
G9  meaningful under both arms ............. FAIL
G10 future intervention definable .......... NOT_IDENTIFIABLE
```

Two verdicts moved since the audit, both against my own model. G5 was counted as a pass while being
untestable on the arm that matters — the same thing G9 is failed for. G10 was "NOT_REACHED", which
describes my procedure rather than the object. The headline goes from six passes to five, of which
{g['N_UNQUALIFIED_PASS']} are unqualified.

The causal-emergence diagnostic is **NOT COMPUTED**, and not as an evasion: in the treated arm the
lineage and ambient macrostates are the same partition on every row, so the comparison is degenerate
exactly where it would matter.

## The two implementations

Not scientifically independent. They share
{im['WHAT_THEY_SHARE']['MEASURED_IDENTICAL_NON_TRIVIAL_LINES']} identical non-trivial lines and the
same predecessor definition; what differs is the propagation operator. Four routes — the literal
rule text, the set-subset test, the morphology form and a neighbour-counting form — agree on 4000
random configurations with 0 mismatches, and on all ten named structural cases. The morphology
identity is **conditional**: break the precondition CERTAIN ⊆ occ and 1721 of 2000 configurations
disagree. Agreement validates encoding consistency, not the causal assumption; that is closed by the
kernel derivation instead.

## What is not claimed

```
OMLDCT02_STATUS               = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED
OMLDCT02_PAIRED_STATISTICS    = DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

A positive CLEA01 result would have established only that a distributed causal-lineage object is
reconstructible and nontrivial in existing archives. It would not have established reproduction.

The route is **paused**, not closed, because the failure belongs to the intervention design and not
to the idea. No model was selected, no handoff was written, and nothing here authorises a successor.
"""
    open(f"{OUT}/CLEA01_FINAL_REPORT.md", "w").write(R)

    names = sorted(os.listdir(OUT))
    with open(f"{OUT}/SHA256SUMS", "w", newline="\n") as fh:
        for n in names:
            if n == "SHA256SUMS":
                continue
            fh.write(f"{H.file_sha256(f'{OUT}/{n}')}  {n}\n")
    print("FINAL_DISPOSITION =", TERMINAL)
    print("artefacts in out/:", len(names))
    return d


def sums_only():
    """regenerate SHA256SUMS alone, without restamping the disposition. Used as the last step of
    the closure so the sums cover the digest-verification file that is written after the report."""
    names = sorted(os.listdir(OUT))
    with open(f"{OUT}/SHA256SUMS", "w", newline="\n") as fh:
        for n in names:
            if n == "SHA256SUMS":
                continue
            fh.write(f"{H.file_sha256(f'{OUT}/{n}')}  {n}\n")
    print("SHA256SUMS regenerated over", len(names) - 1, "artefacts")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sums":
        sums_only()
    else:
        main()
