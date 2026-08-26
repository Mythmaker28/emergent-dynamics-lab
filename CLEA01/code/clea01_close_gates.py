"""CLEA01 closure §12 and §13 — recompute the ten gates after adjudication, and map the terminal.

Two gate verdicts change here, both AGAINST my own model, both because the checker's finding 12b was
right that "six pass, three fail" read softer than it was:

  G5 was counted inside N_PASS = 6 while being untestable on the arm the experiment is about. The
     closure launcher supplies NOT_IDENTIFIABLE as a verdict, which is what it actually is.
  G10 was recorded as NOT_REACHED, which is a statement about my procedure rather than about the
     object. It is NOT_IDENTIFIABLE: no intervention that selectively perturbs causal integration
     can be defined exactly against an object that coincides with the whole population in the
     treated arm.

The headline therefore moves from six passes to five. Nothing in the terminal changes.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H
OUT = f"{REPO}/CLEA01/out"
TERMINAL = "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED"
VOCAB = ["PASS", "FAIL", "NOT_IDENTIFIABLE", "TECHNICALLY_INVALID"]


def main():
    ker = json.load(open(f"{OUT}/CLEA01_CAUSAL_KERNEL_ADJUDICATION.json"))
    nv = json.load(open(f"{OUT}/CLEA01_FINAL_NONVACUITY_ADJUDICATION.json"))
    ks = json.load(open(f"{OUT}/CLEA01_KNOWN_SUCCESS_ADJUDICATION.json"))
    am = json.load(open(f"{OUT}/CLEA01_AMBIENT_SPECIFICITY_ADJUDICATION.json"))
    hi = json.load(open(f"{OUT}/CLEA01_HIDDEN_INPUT_AUDIT.json"))
    im = json.load(open(f"{OUT}/CLEA01_IMPLEMENTATION_INDEPENDENCE_ADJUDICATION.json"))
    ch = json.load(open(f"{OUT}/CLEA01_DEVELOPMENT_VALIDATION_CHRONOLOGY.json"))
    ad = json.load(open(f"{OUT}/CLEA01_CHECKER_ADJUDICATION.json"))
    m = ker["ARCHIVE_MEASUREMENT"]

    G = [
     {"gate": "G1", "requirement": "reconstructable in all 33 pairs",
      "VERDICT": "PASS", "UNQUALIFIED": True,
      "BASIS": "Model C was reconstructed on all 66 arms from cell coordinates, occupancy and the "
               "three event ledgers alone. %d consecutive row pairs carry %d cells without a "
               "Moore-1 predecessor." % (m["consecutive_row_pairs_compared"],
                                         m["cells_with_no_Moore_1_predecessor"])},
     {"gate": "G2", "requirement": "two implementations agree",
      "VERDICT": "PASS", "UNQUALIFIED": False,
      "BASIS": "66 of 66 arms agree on all 13 quantities, and four routes agree on 4000 random "
               "configurations with 0 mismatches.",
      "QUALIFICATION": "the two implementations are equivalent encodings, not scientifically "
                       "independent: they share %d identical non-trivial lines and the same "
                       "predecessor definition. G2 tests the propagation operator only. The "
                       "archive-reading conventions and event-label alignment are common-mode and "
                       "are closed instead by section 5."
                       % im["WHAT_THEY_SHARE"]["MEASURED_IDENTICAL_NON_TRIVIAL_LINES"]},
     {"gate": "G3", "requirement": "non-vacuous against both A and B",
      "VERDICT": "FAIL", "UNQUALIFIED": True,
      "BASIS": "against A it passes qualitatively — one arm exhibits a continuation A terminates at "
               "row %d that C retains for %d further rows with enumerable witnesses. Against B it "
               "fails in the treated arm, and now without any magnitude reading at all: of "
               "%d occupied cell-rows after A across the SELECTIVE arms, Model C rejects "
               "%d."
               % (nv["THE_QUALITATIVE_REQUIREMENT"]["EXHIBIT"]["A_ended_at_row"],
                  nv["THE_QUALITATIVE_REQUIREMENT"]["EXHIBIT"]["C_certain_duration"]
                  - nv["THE_QUALITATIVE_REQUIREMENT"]["EXHIBIT"]["A_duration"],
                  am["CELL_LEVEL"]["SELECTIVE_occupied_cell_rows_after_A"],
                  am["CELL_LEVEL"]["SELECTIVE_cell_rows_rejected_outright"]),
      "WHAT_CHANGED_SINCE_THE_AUDIT": "the FAIL was argued by magnitude — 'a few particles out of "
               "1.7 million'. That was a threshold in a record claiming none. It is replaced by a "
               "set identity and a zero count."},
     {"gate": "G4", "requirement": "preserves the known locked-daughter success",
      "VERDICT": "FAIL", "UNQUALIFIED": True,
      "BASIS": "the necessary condition holds 66 of 66; the strong containment form passes %d of "
               "66 and fails at 402 SHAM and 518 SHAM. Every cell A carries and C does not was "
               "never CERTAIN and never POSSIBLE at any row — no causal path at all."
               % ks["STRONG_CONDITION_C_CONTAINS_A_ON_EVERY_ROW"]["passing"],
      "IT_IS_NOT_AN_IMPLEMENTATION_DEFECT": True},
     {"gate": "G5", "requirement": "rejects unrelated ambient succession",
      "VERDICT": "NOT_IDENTIFIABLE", "UNQUALIFIED": True,
      "BASIS": "on SHAM the rule discriminates: %d of %d occupied cell-rows after A are rejected "
               "outright and the median rejected mass fraction is %.4f. On SELECTIVE the gate "
               "cannot be tested at all — the intervention removes the only other Y source, so "
               "there is no unrelated ambient succession to reject."
               % (am["CELL_LEVEL"]["SHAM_cell_rows_rejected_outright"],
                  am["CELL_LEVEL"]["SHAM_occupied_cell_rows_after_A"],
                  am["MASS_LEVEL"]["SHAM_median_rejected_fraction"]),
      "WHAT_CHANGED_SINCE_THE_AUDIT": "it was counted inside N_PASS = 6 while being untestable on "
               "the arm that matters — which is exactly what G9 is failed for. Counting it as a "
               "pass was inconsistent. It is NOT_IDENTIFIABLE."},
     {"gate": "G6", "requirement": "an explicit causal witness for every inherited interval",
      "VERDICT": "PASS", "UNQUALIFIED": True,
      "BASIS": "the witness is the pair (S(d), CERTAIN(t)), enumerable and label-free, exhibited "
               "cell by cell in section 7. In non-saturating arms alone the object crosses 37,944 "
               "split rows across 23 arms and 1,404 constituent replacements across 22 arms, each "
               "with a witness. The headline figures of 373,987 and 42,593 are degeneracy-inflated "
               "and are not used."},
     {"gate": "G7", "requirement": "no future outcome or online identifier defines ancestry",
      "VERDICT": "PASS", "UNQUALIFIED": True,
      "BASIS": "AST scan over every CLEA01 script in which string literals COUNT as use, plus a "
               "runtime probe wrapping numpy.load: both ancestry implementations request exactly "
               "%s and no forbidden key. FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY = %s, "
               "ONLINE_ID_USED_TO_DEFINE_ANCESTRY = %s."
               % (", ".join(hi["RUNTIME_ARCHIVE_KEYS_TOUCHED"]["clea01_lineage_i1"]),
                  hi["FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY"],
                  hi["ONLINE_ID_USED_TO_DEFINE_ANCESTRY"]),
      "WHAT_CHANGED_SINCE_THE_AUDIT": "the original basis stripped string literals and covered 2 of "
               "7 scripts, so it could not have detected a violation. The verdict was right for the "
               "wrong reason; it now has a basis that would fail if the claim were false."},
     {"gate": "G8", "requirement": "the validation set produces no new unresolvable contradiction",
      "VERDICT": "PASS", "UNQUALIFIED": False,
      "BASIS": "one contradiction, 402 SHAM, and it is resolved rather than left open: it is the "
               "centroid-versus-provenance difference recorded under G4. The other ten validation "
               "arms reproduce the development structure.",
      "QUALIFICATION": "the split encoding actually used is one of only two of six tested "
               "encodings that put this contradiction in VALIDATION at all. The choice went "
               "against me, but G8's flavour is the one split-dependent thing in the mission."},
     {"gate": "G9", "requirement": "the causal object remains meaningful under both arms",
      "VERDICT": "FAIL", "UNQUALIFIED": True,
      "BASIS": "under SHAM it is meaningful and specific. Under SELECTIVE it claims exactly 100 per "
               "cent of the post-A world in all 31 askable arms and rejects 0 of %d occupied "
               "cell-rows. 'The world is the daughter's lineage' is true there and explains "
               "nothing, because the intervention made it true."
               % am["CELL_LEVEL"]["SELECTIVE_occupied_cell_rows_after_A"]},
     {"gate": "G10", "requirement": "a future intervention that selectively perturbs causal "
                                    "integration without changing Y or X counts can be defined "
                                    "exactly",
      "VERDICT": "NOT_IDENTIFIABLE", "UNQUALIFIED": True,
      "BASIS": "such an intervention needs a target that is distinct from the ambient population in "
               "the arm being treated. In these archives it is not: post-fork, CERTAIN and the "
               "occupied set coincide on every row. The only arm where the object is distinct is "
               "the control, where an intervention cannot bear on the question.",
      "WHAT_CHANGED_SINCE_THE_AUDIT": "it was recorded as NOT_REACHED, which describes my procedure "
               "rather than the object. NOT_IDENTIFIABLE is a statement about the evidence."},
    ]

    npass = sum(1 for g in G if g["VERDICT"] == "PASS")
    nunq = sum(1 for g in G if g["VERDICT"] == "PASS" and g["UNQUALIFIED"])
    nfail = sum(1 for g in G if g["VERDICT"] == "FAIL")
    nni = sum(1 for g in G if g["VERDICT"] == "NOT_IDENTIFIABLE")

    gates = {
        "MISSION": "CLEA01", "SECTION": "12 — structural gates, final",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "VERDICT_VOCABULARY": VOCAB,
        "NO_GATE_IS_STATISTICAL": True,
        "NO_PERFORMANCE_THRESHOLD_IS_USED": True,
        "AND_THIS_TIME_THAT_CLAIM_IS_TRUE": "the audit asserted it while arguing G3 from a particle "
            "count. G3 now rests on a set identity and a zero rejection count, so no quantity is "
            "compared to a cut-off anywhere in the gate scoring.",
        "GATES": G,
        "N_PASS": npass, "N_UNQUALIFIED_PASS": nunq, "N_FAIL": nfail,
        "N_NOT_IDENTIFIABLE": nni, "N_TECHNICALLY_INVALID": 0,
        "FAILED_GATES": [g["gate"] for g in G if g["VERDICT"] == "FAIL"],
        "NOT_IDENTIFIABLE_GATES": [g["gate"] for g in G if g["VERDICT"] == "NOT_IDENTIFIABLE"],
        "CHANGED_SINCE_THE_AUDIT": {"G5": "PASS_ON_SHAM__NOT_TESTABLE -> NOT_IDENTIFIABLE",
                                    "G10": "NOT_REACHED -> NOT_IDENTIFIABLE",
                                    "headline": "six passes -> five",
                                    "direction": "both changes tighten the record against my own "
                                                 "model. Neither changes the terminal."},
        "ALL_TEN_PASS": False,
        "MODEL_C_SELECTED": False, "MAX_SELECTED_IDENTITY_MODELS": 1, "SELECTED": 0,
        "LOAD_BEARING_DEFECT_COUNT": ad["LOAD_BEARING_DEFECT_COUNT"],
        "SPLIT_ASSIGNMENT_REPRODUCES": ch["ASSIGNMENT_REPRODUCES"],
    }
    gates["GATES_FINAL_CONTENT_HASH"] = H.content_digest(gates, extra_excluded=("GATES_FINAL_CONTENT_HASH",))
    json.dump(gates, open(f"{OUT}/CLEA01_STRUCTURAL_GATES_FINAL.json", "w"), indent=1)

    ce = {
        "MISSION": "CLEA01", "SECTION": "12 — causal emergence, final status",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "STATUS": "NOT_COMPUTED",
        "PROCEDURAL_REASON": "the estimator is forbidden while any of G1 to G9 fails. Three do: "
                             "G3, G4 and G9.",
        "SUBSTANTIVE_REASON": "in the treated arm the lineage macrostate and the ambient macrostate "
                              "are the same partition on every post-fork row. A comparison between "
                              "them is degenerate exactly where it would matter, and could only be "
                              "run on the control arm, where the answer cannot bear on the "
                              "experiment.",
        "IT_WAS_NOT_COMPUTED_AS_A_RESCUE_METRIC": True,
        "NO_INFORMATION_ESTIMATOR_WAS_INTRODUCED": True,
        "WOULD_A_NUMBER_HAVE_HELPED": "no. Producing one under these conditions would create "
                                      "precisely the temptation the rule exists to remove.",
    }
    ce["CAUSAL_EMERGENCE_FINAL_CONTENT_HASH"] = H.content_digest(
        ce, extra_excluded=("CAUSAL_EMERGENCE_FINAL_CONTENT_HASH",))
    json.dump(ce, open(f"{OUT}/CLEA01_CAUSAL_EMERGENCE_FINAL_STATUS.json", "w"), indent=1)

    print(f"gates: PASS {npass} (unqualified {nunq}) | FAIL {nfail} | NOT_IDENTIFIABLE {nni}")
    for g in G:
        print(f"  {g['gate']:4s} {g['VERDICT']:18s} {'' if g['UNQUALIFIED'] else '(qualified)'}")
    return gates, ce


if __name__ == "__main__":
    main()
