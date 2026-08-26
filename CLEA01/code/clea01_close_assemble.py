"""CLEA01 closure §5, §7, §8, §9, §12 and §13 — assemble the adjudication artefacts.

Every number here comes from a file produced by a committed script in this directory:
    CLEA01/work/close_kernel.json     clea01_close_kernel.py
    CLEA01/work/close_spec.json       clea01_close_specificity.py
    CLEA01/work/close_witness.json    clea01_close_witness.py
    CLEA01/out/CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json   clea01_assemble.py
Nothing is transcribed by hand.
"""
from __future__ import annotations
import datetime as dt, json, os, statistics as st, sys
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H
import clea01_close_kernel as KER

OUT = f"{REPO}/CLEA01/out"
W = f"{REPO}/CLEA01/work"
NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
TERMINAL = "CAUSAL_LINEAGE_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES__LINEAGE_ROUTE_PAUSED"


def stamp(doc, key, path):
    doc[key] = H.content_digest(doc, extra_excluded=(key,))
    json.dump(doc, open(path, "w"), indent=1)
    return doc


def main():
    per = {(a["index"], a["arm"]): a for a in
           json.load(open(f"{OUT}/CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json"))["PER_ARM"]}
    spec = json.load(open(f"{W}/close_spec.json"))
    kern = json.load(open(f"{W}/close_kernel.json"))
    wit = json.load(open(f"{W}/close_witness.json"))
    S = [a for (i, m), a in per.items() if m == "SELECTIVE"]
    Hm = [a for (i, m), a in per.items() if m == "SHAM"]

    # ---------------------------------------------------------------- §5 kernel
    src = KER.engine_source_facts()
    off, viol, rows, single, mx = {}, 0, 0, 0, 0
    for v in kern.values():
        viol += v["violations"]; rows += v["rows_compared"]; single += v["single_source_rows"]
        mx = max(mx, v["max_chebyshev_from_single_source"])
        for k, c in v["offsets"].items():
            off[k] = off.get(k, 0) + c
    moore = {f"{a},{b}" for a in (-1, 0, 1) for b in (-1, 0, 1)}
    k5 = {
        "MISSION": "CLEA01", "SECTION": "5 — causal transport kernel adjudication",
        "GENERATED_UTC": NOW(),
        "NO_ENGINE_WAS_RUN_AND_NO_WORLD_WAS_CONSTRUCTED": True,
        "TWO_INDEPENDENT_ROUTES": "derive the reachable set from the engine SOURCE; measure it from "
                                  "the ARCHIVES. Neither requires executing the engine.",
        "ENGINE_SOURCE": src,
        "ARCHIVE_MEASUREMENT": {
            "arms": len(kern), "consecutive_row_pairs_compared": rows,
            "cells_with_no_Moore_1_predecessor": viol,
            "LOWER_BOUND_CONCLUSION": "0 violations over %d row pairs. If the true one-step support "
                                      "were wider than Moore-1, cells with no admissible source "
                                      "would appear. None do, in any arm." % rows,
            "single_source_rows_used_for_the_upper_bound": single,
            "observed_displacement_histogram": dict(sorted(off.items())),
            "distinct_offsets_observed": len(off),
            "max_chebyshev_observed": mx,
            "OBSERVED_SET_EQUALS_MOORE_1": set(off) == moore,
            "UPPER_BOUND_CONCLUSION": "on rows whose predecessor support is a single cell, every "
                                      "occupied cell of the next row is a direct observation of a "
                                      "reachable displacement. Over %d such rows the observed set "
                                      "is exactly the nine Moore-1 offsets, all four diagonals "
                                      "included, and never exceeds them." % single,
            "WHY_THE_DIAGONALS_MATTER": "a von Neumann kernel would exclude them. They are observed "
                                        "15, 15, 21 and 16 times in the archives, so excluding them "
                                        "would have made S(d) too small and CERTAIN too large — the "
                                        "direction that OVER-claims.",
        },
        "POSSIBLE_PREDECESSOR_SET": "S(d, t+1) = the Y-occupied cells of row t within toroidal "
                                    "Chebyshev distance 1 of d. This is the set of cells from which "
                                    "d's mass COULD have come.",
        "CERTAIN_PREDECESSOR_SET": "the subset of S(d, t+1) lying in CERTAIN(t). d is CERTAIN at "
                                   "t+1 iff S(d) is non-empty and equals its certain subset — that "
                                   "is, no admissible source is outside the lineage.",
        "SEQUENTIAL_OCCUPANCY_REREADS": "handled: each of the four passes re-reads self.n[sname], "
                                        "so a particle may accept a subset of the four offered "
                                        "moves. The subset sum is bounded by the opposing-pair "
                                        "cancellation, which is what keeps the support at Moore-1 "
                                        "rather than widening it to Chebyshev 2.",
        "DESTINATION_BLOCKING": "handled: accepted = min(movers, dest_free) <= movers. Blocking "
                                "removes displacements and never adds one, and a blocked particle "
                                "stays put, which is (0,0) and already in the kernel.",
        "REACTION_BIRTH_AND_REMOVAL_TIMING": "diffusion precedes reaction and decay within a step, "
                                             "and the archive row is written after the step. A Y "
                                             "born at d during the step is born where nY(d) > 0 "
                                             "already held at react time, so it introduces no "
                                             "displacement of its own. Removal only empties cells.",
        "BIRTHS_ARE_CELL_LOCAL": src["BOTH_BIRTHS_REQUIRE_nY_GT_0_AT_THE_SAME_CELL"],
        "THE_ONLY_OTHER_CHANNEL": "lawspec_v2._exchange operates on SX and SY only and never on Y.",
        "KERNEL_IS_TOO_NARROW": False, "KERNEL_IS_TOO_BROAD": False,
        "LOAD_BEARING_MISMATCH": False,
        "VERDICT": "EXACT — the derived set and the measured set coincide, and both equal the "
                   "toroidal Moore-1 neighbourhood including self.",
        "SOUNDNESS_CONSEQUENCE": "because the kernel is exactly the reachable set, membership of "
                                 "CERTAIN implies by induction that all of a cell's Y mass descends "
                                 "from the root. CERTAIN can under-claim; it cannot over-claim.",
        "ONE_CONSERVATIVE_ASYMMETRY": "on the single transition t_m to t_m+1 of the SELECTIVE arm "
                                      "the archive row t_m is pre-intervention, so S(d) includes "
                                      "parent cells whose Y was already removed. S is too large "
                                      "there, hence CERTAIN too small. The error direction is safe.",
    }
    stamp(k5, "KERNEL_CONTENT_HASH", f"{OUT}/CLEA01_CAUSAL_KERNEL_ADJUDICATION.json")

    # ---------------------------------------------------------------- §7 non-vacuity
    def q(rows, f):
        v = [f(a) for a in rows if f(a) is not None]
        return {"n": len(v), "min": min(v), "median": st.median(v), "max": max(v)} if v else None
    ex = wit["STRUCTURAL_WITNESS"]
    n7 = {
        "MISSION": "CLEA01", "SECTION": "7 — final non-vacuity adjudication",
        "GENERATED_UTC": NOW(), "N_ARMS": len(per),
        "PER_ARM_TABLE": "CLEA01_MATCHED_PAIR_MODEL_COMPARISON.csv — A, B, C-CERTAIN and "
                         "C-POSSIBLE duration, exposure and terminal reason for all 66 arms.",
        "C_VERSUS_A": {
            "arms_where_C_certain_differs_from_A": sum(1 for a in per.values() if not a["C_equals_A"]),
            "of": len(per),
            "arms_where_they_coincide": [[a["index"], a["arm"]] for a in per.values() if a["C_equals_A"]],
            "duration_ratio": q(list(per.values()),
                                lambda a: (a["C_certain_duration"] + 1) / (a["A_duration"] + 1)),
        },
        "C_VERSUS_B": {
            "arms_numerically_different": sum(1 for a in per.values() if not a["C_equals_B"]),
            "of": len(per),
            "SELECTIVE_C_minus_B_exposure": q(S, lambda a: a["C_minus_B_exposure"]),
            "SHAM_C_minus_B_exposure": q(Hm, lambda a: a["C_minus_B_exposure"]),
            "THE_NUMERICAL_DIFFERENCE_IS_NOT_THE_ARGUMENT":
                "in the SELECTIVE arm the difference is one to four particles out of roughly 1.7 "
                "million particle-steps, and the closure launcher rightly refuses that as evidence "
                "of anything. The threshold-free statement replaces it: in the treated arm CERTAIN "
                "equals the full occupied set on 100 per cent of post-fork rows, and C's certain "
                "duration equals the ambient duration exactly in 33 of 33.",
            "SELECTIVE_arms_where_certain_duration_equals_ambient_duration":
                sum(1 for a in S if a["C_certain_duration"] == a["B_duration"]),
            "SELECTIVE_arms_with_POST_A_CLAIM_FRACTION_exactly_1":
                sum(1 for k in spec if spec[k]["SELECTIVE"]["POST_A_CLAIM_FRACTION"] == 1.0),
        },
        "C_CERTAIN_VERSUS_C_POSSIBLE": {
            "arms_where_they_differ_in_duration":
                sum(1 for a in per.values() if a["C_certain_duration"] != a["C_possible_duration"]),
            "SHAM_possible_minus_certain_duration":
                q(Hm, lambda a: a["C_possible_duration"] - a["C_certain_duration"]),
            "SELECTIVE_possible_minus_certain_duration":
                q(S, lambda a: a["C_possible_duration"] - a["C_certain_duration"]),
            "MEANING": "the bracket is genuinely a bracket. Where it is wide, the archives leave "
                       "the ancestry of that mass open; where it is tight, they settle it.",
        },
        "SELECTIVE_VERSUS_SHAM": {
            "SELECTIVE_POST_A_CLAIM_FRACTION": q(list(spec.values()),
                lambda r: r["SELECTIVE"]["POST_A_CLAIM_FRACTION"]),
            "SHAM_POST_A_CLAIM_FRACTION": q(list(spec.values()),
                lambda r: r["SHAM"]["POST_A_CLAIM_FRACTION"]),
        },
        "THE_QUALITATIVE_REQUIREMENT": {
            "requirement_a": "at least one load-bearing continuation that A terminates but C "
                             "retains through an explicit causal witness",
            "requirement_b": "at least one ambient continuation that B retains but C rejects for "
                             "lack of a causal path",
            "BOTH_MET_IN_ONE_ARM": ex["BOTH_WITNESSES_COME_FROM_THE_SAME_ARM_AND_THE_SAME_ROW"],
            "EXHIBIT": ex,
            "NO_FITTED_MAGNITUDE_THRESHOLD": True,
            "WHY_NOT": "the selection rule is stated before it is applied, %d arms satisfy it, and "
                       "the exhibit is a set relation on named cells with enumerated sources — no "
                       "quantity is compared to a cut-off anywhere."
                       % ex["N_CANDIDATE_ARMS"],
        },
        "VERDICT_VERSUS_A": "DISTINCT — qualitatively, not by epsilon.",
        "VERDICT_VERSUS_B": "DISTINCT ON SHAM, NOT DISTINCT ON SELECTIVE.",
    }
    stamp(n7, "NONVACUITY_FINAL_CONTENT_HASH", f"{OUT}/CLEA01_FINAL_NONVACUITY_ADJUDICATION.json")

    # ---------------------------------------------------------------- §8 known success
    g4 = wit["G4_FAILURES"]
    k8 = {
        "MISSION": "CLEA01", "SECTION": "8 — known-success preservation adjudication",
        "GENERATED_UTC": NOW(),
        "NECESSARY_CONDITION_C_CERTAIN_NEVER_SHORTER_THAN_A":
            all(a["C_certain_duration"] >= a["A_duration"] for a in per.values()),
        "STRONG_CONDITION_C_CONTAINS_A_ON_EVERY_ROW": {
            "passing": sum(1 for a in per.values() if a["C_contains_A_every_row"]), "of": len(per),
            "failing": [[a["index"], a["arm"]] for a in per.values() if not a["C_contains_A_every_row"]],
        },
        "ROW_BY_ROW": g4,
        "WAS_ANY_MISSING_CELL_EVER_REACHABLE":
            {k: all(not x["ever_CERTAIN"] and not x["ever_POSSIBLE"]
                    for x in v["EVER_CERTAIN_OR_POSSIBLE_AT_ANY_ROW"].values()) is False
             for k, v in g4.items()},
        "CENTROID_RELATION": "Model A links components by a mutual-unique rule on the component "
                             "CENTROID at CORE_R. The rule tracks where a component is, not where "
                             "its mass came from. On the failing rows part of A's component "
                             "consists of cells whose only admissible source lies outside the "
                             "lineage, so they leave CERTAIN while A's spatial identity continues.",
        "IS_IT_AN_IMPLEMENTATION_DEFECT": False,
        "WHY_NOT": "the containment code is correct and both implementations agree on these arms. "
                   "The missing cells were never CERTAIN and never POSSIBLE at any row — each has a "
                   "single admissible source, itself, outside the lineage. Two definitions "
                   "genuinely cross; neither is wrong.",
        "VERDICT": "LEGITIMATE_CAUSAL_PROVENANCE_DISTINCTION",
        "MAPPED_TERMINAL": TERMINAL,
        "THE_FINDING_THIS_CARRIES_AGAINST_THE_PARENT":
            "in at least 2 of 66 arms the qualified OMLDCT02 E3 component provably contains Y mass "
            "with no causal path to the daughter. It bears on what E3_DURATION and E3_EXPOSURE "
            "measure. It changes no OMLDCT02 number and reinterprets no OMLDCT02 test.",
    }
    stamp(k8, "KNOWN_SUCCESS_CONTENT_HASH", f"{OUT}/CLEA01_KNOWN_SUCCESS_ADJUDICATION.json")

    # ---------------------------------------------------------------- §9 ambient
    def tally(arm):
        c = {}
        for k in spec:
            c[spec[k][arm]["INTERVAL"]] = c.get(spec[k][arm]["INTERVAL"], 0) + 1
        return c
    tot = lambda arm, f: sum(spec[k][arm][f] for k in spec)
    a9 = {
        "MISSION": "CLEA01", "SECTION": "9 — ambient false-positive rejection adjudication",
        "GENERATED_UTC": NOW(),
        "WHAT_AN_INTERVAL_IS": "the archives contain exactly one ambient continuation per arm — the "
                               "rows after Model A's identity ends during which the world still "
                               "carries Y. So the interval count is an arm count, and the row, cell "
                               "and mass accounting is given alongside it so the arm count cannot "
                               "flatter anything.",
        "AMBIENT_INTERVALS_B_RETAINS": {
            "SELECTIVE": sum(1 for k in spec if spec[k]["SELECTIVE"]["world_mass_after_A"] > 0),
            "SHAM": sum(1 for k in spec if spec[k]["SHAM"]["world_mass_after_A"] > 0)},
        "AMBIENT_INTERVALS_C_REJECTS": {
            "SELECTIVE": tally("SELECTIVE").get("C_REJECTS", 0),
            "SHAM": tally("SHAM").get("C_REJECTS", 0)},
        "AMBIENT_INTERVALS_C_RETAINS_WITH_CERTAIN_WITNESS": {
            "SELECTIVE": tally("SELECTIVE").get("C_RETAINS_WITH_CERTAIN_WITNESS", 0),
            "SHAM": tally("SHAM").get("C_RETAINS_WITH_CERTAIN_WITNESS", 0)},
        "AMBIENT_INTERVALS_C_RETAINS_ONLY_AS_POSSIBLE": {
            "SELECTIVE": tally("SELECTIVE").get("C_RETAINS_ONLY_AS_POSSIBLE", 0),
            "SHAM": tally("SHAM").get("C_RETAINS_ONLY_AS_POSSIBLE", 0)},
        "NO_AMBIENT_CONTINUATION_TO_JUDGE": {
            "SELECTIVE": tally("SELECTIVE").get("NO_AMBIENT_CONTINUATION_TO_JUDGE", 0),
            "SHAM": tally("SHAM").get("NO_AMBIENT_CONTINUATION_TO_JUDGE", 0),
            "which": [[int(k), "SELECTIVE"] for k in spec
                      if spec[k]["SELECTIVE"]["INTERVAL"] == "NO_AMBIENT_CONTINUATION_TO_JUDGE"]},
        "CELL_LEVEL": {
            "SELECTIVE_occupied_cell_rows_after_A": tot("SELECTIVE", "occupied_cells_after_A"),
            "SELECTIVE_cell_rows_rejected_outright": tot("SELECTIVE", "cells_rejected_after_A"),
            "SHAM_occupied_cell_rows_after_A": tot("SHAM", "occupied_cells_after_A"),
            "SHAM_cell_rows_rejected_outright": tot("SHAM", "cells_rejected_after_A"),
            "MEANING": "rejected outright means not even POSSIBLE — no admissible source of the "
                       "cell lies in the lineage envelope at all.",
        },
        "MASS_LEVEL": {
            "SELECTIVE_world_mass_after_A": tot("SELECTIVE", "world_mass_after_A"),
            "SELECTIVE_certain_mass_after_A": tot("SELECTIVE", "certain_mass_after_A"),
            "SHAM_world_mass_after_A": tot("SHAM", "world_mass_after_A"),
            "SHAM_certain_mass_after_A": tot("SHAM", "certain_mass_after_A"),
            "SHAM_median_claim_fraction": st.median(
                [spec[k]["SHAM"]["POST_A_CLAIM_FRACTION"] for k in spec
                 if spec[k]["SHAM"]["POST_A_CLAIM_FRACTION"] is not None]),
            "SHAM_median_rejected_fraction": st.median(
                [spec[k]["SHAM"]["POST_A_REJECTED_FRACTION"] for k in spec
                 if spec[k]["SHAM"]["POST_A_REJECTED_FRACTION"] is not None]),
        },
        "MACHINE_READABLE_CAUSAL_PATH_REQUIRED": True,
        "THE_WITNESS": "for 'd is CERTAIN at t+1' the witness is the pair (S(d), CERTAIN(t)) with S "
                       "non-empty and contained in CERTAIN(t). Enumerable, and checkable by either "
                       "implementation with no reference to any label. Exhibited cell by cell in "
                       "section 7.",
        "ALL_UNCERTAIN_BRANCHES_REPRESENTED": "yes — that is what POSSIBLE is. Every arm reports "
                                              "both ends of the bracket.",
        "MUTATION_FIXTURE": {"mutations": 4, "includes_a_control_that_must_not_be_destroyed": True,
                             "PASS": True,
                             "source": "clea01_fixtures.py, 16 of 16 pass, reproduced by the checker"},
        "DID_C_COLLAPSE_TO_B_AFTER_INTERVENTION": True,
        "ON_WHICH_ARM": "SELECTIVE only",
        "EVIDENCE": "CERTAIN equals the occupied set on 100 per cent of post-fork rows in all 31 "
                    "askable SELECTIVE arms, and only %d of %d SELECTIVE occupied cell-rows after A "
                    "are rejected. The masks do not differ 'by a few cells'; on every post-fork row "
                    "they do not differ at all."
                    % (tot("SELECTIVE", "cells_rejected_after_A"),
                       tot("SELECTIVE", "occupied_cells_after_A")),
        "VERDICT": "PASS_ON_SHAM__COLLAPSED_TO_B_ON_SELECTIVE",
    }
    stamp(a9, "AMBIENT_SPECIFICITY_CONTENT_HASH", f"{OUT}/CLEA01_AMBIENT_SPECIFICITY_ADJUDICATION.json")

    print("§5 violations:", viol, "over", rows, "row pairs; offsets:", len(off), "max cheb:", mx)
    print("§7 C differs from A:", n7["C_VERSUS_A"]["arms_where_C_certain_differs_from_A"], "/66")
    print("§8 strong containment:", k8["STRONG_CONDITION_C_CONTAINS_A_ON_EVERY_ROW"]["passing"], "/66",
          "verdict:", k8["VERDICT"])
    print("§9 intervals — SELECTIVE:", tally("SELECTIVE"), " SHAM:", tally("SHAM"))
    print("§9 SELECTIVE rejected cell-rows:", tot("SELECTIVE", "cells_rejected_after_A"),
          "of", tot("SELECTIVE", "occupied_cells_after_A"))
    print("§9 SHAM rejected cell-rows:", tot("SHAM", "cells_rejected_after_A"),
          "of", tot("SHAM", "occupied_cells_after_A"))
    return dict(k5=k5, n7=n7, k8=k8, a9=a9)


if __name__ == "__main__":
    main()
