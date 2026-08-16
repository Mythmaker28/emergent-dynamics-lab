"""PMCR01 repair §1 — the machine-readable repair matrix over EVERY reviewed finding.

Every DEFECT_CONFIRMED is either repaired mechanically (A) or left unrepaired with a stated
load-bearing reason (B). A cosmetic rewrite does not count as repair where the defect concerns
the scientific disposition. The review files themselves are never modified.
"""
from __future__ import annotations

import hashlib
import json

REVIEW = "/home/claude/PMCR01/review"
OUT = "/home/claude/PMCR01/out"

R = {
    "F1": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_channels.py (FILES + observe.py)",
                       "pmcr01_map.py (CHANNEL_EXECUTION_PATH / "
                       "MEASUREMENT_AND_INSTRUMENTATION_PATH, ABSENT class qualified)",
                       "pmcr01_regions.py (REPAIR_F1 addendum to the predeclared-bound block)",
                       "pmcr01_repair_q.py (new: full Q verification)",
                       "pmcr01_repair_apply.py (new: repaired logic + disposition)",
                       "PMCR01_FINAL_DISPOSITION.json", "PMCR01_FINAL_REPORT.md",
                       "PMCR01_Q_INSTRUMENTATION_EVIDENCE.json (new)",
                       "HANDOFF_MINIMAL_Y_CHANNEL_ARCHITECTURE_DESIGN_01.md (superseded)",
                       "HANDOFF_MINORITY_Y_Q_BOUND_DERIVATION_01.md (new)"],
        pre="E[Q] 'is a property of the realized cloud measure, not of the LawSpec' and 'does "
            "not exist without measuring the realized cloud'; therefore the smallest missing "
            "capability is a new conserved Y-precursor species and "
            "STOP__ARCHITECTURE_CHANGE_REQUIRED.",
        post="E[Q] is INSTRUMENTED AND RECORDED by the existing architecture "
             "(ORR01/code/observe.py lines 55, 59, 69; field index 20; all 28 delivered arms; "
             "0 missing values). MEASUREMENT_AVAILABILITY = CONFIRMED. What is missing is a "
             "PROSPECTIVELY FROZEN bound, not the measurement. ARCHITECTURE_CHANGE_NECESSITY = "
             "NOT_ESTABLISHED; disposition weakened to "
             "EXISTING_ARCHITECTURE_WINDOW_NOT_YET_PROSPECTIVELY_LOCATED.",
        verify="python3 pmcr01_repair_q.py",
        result="observer committed and on-disk == HEAD blob; 28/28 arms contain Q; 308000 "
               "frames; static mean 2.369048, mobile mean 3.169730, complete 2.769389; "
               "observed pooled max 28 == derived Q_max 28; 0 NaN"),
    "F2": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (build_checklist)",
                       "PMCR01_FINAL_DISPOSITION.json"],
        pre="ROBUST_REGION_POSITIVE_WIDTH = bool(C['NONEMPTY']) computed from mobile-only scans "
            "(scan(c) defaults tau=TAU_SEP=125) while the narrative claimed a branch-independent "
            "ground.",
        post="replaced by PROSPECTIVELY_QUALIFIED_REGION_LOCATED, computed from the "
             "branch-independent transport question (is there a frozen ex-ante Q bound?). Both "
             "branches are reported separately under BRANCH_SEPARATED_REGIONS with an explicit "
             "SCOPE_RULE; the static non-empty counter-region is preserved.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "print(d['CHECKLIST_COMPUTED']['PROSPECTIVELY_QUALIFIED_REGION_LOCATED'])\"",
        result="the flag is branch-independent; MOBILE and STATIC reported separately and never "
               "averaged"),
    "F3": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (build_checklist, "
                       "no_target_derived_input_computed)", "PMCR01_FINAL_DISPOSITION.json"],
        pre="NO_TARGET_DERIVED_INPUT: True and INDEPENDENCE_OR_ALIAS_STATUS_RESOLVED: True were "
            "hardcoded literals; FOUR_PROPOSITIONS held four hardcoded booleans.",
        post="every checklist item now carries source / calculation / observed_value / "
             "threshold_or_rule / result. NO_TARGET_DERIVED_INPUT is computed by an AST scan "
             "that distinguishes a data access from prose. FOUR_PROPOSITIONS carries a source "
             "per item.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "print(all(set(v)>={'source','calculation','observed_value','threshold_or_rule',"
               "'result'} for v in d['CHECKLIST_COMPUTED'].values()))\"",
        result="all 10 items structured and computed. The computed scan initially returned "
               "False on three prose mentions of 'r80'; the check was corrected to AST-based "
               "(not the threshold relaxed) and then returned True on zero data accesses."),
    "F4": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (admissibility_audit)",
                       "PMCR01_FINAL_DISPOSITION.json"],
        pre="NO_GUARD_REFUSES_A_NONZERO_kY_OR_muY derived from a scan of ast.Assert/ast.Raise "
            "nodes; the analysed files contain ZERO such nodes, so the empty result was a "
            "vacuous truth.",
        post="replaced by an audit of the mechanisms that could actually bound the parameters: "
             "constructor copy, the min(1, .) clamp, the Bernoulli domain on muY, conditional "
             "short-circuits, the manifest choice, branch-dependent p_hop_Y, CAP preservation "
             "and the mutation oracles. A VACUITY POSITIVE CONTROL against guard_obtc.py (8 "
             "Assert/Raise nodes) proves the searcher can find raises when they exist.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "a=d['F4_ADMISSIBILITY_AUDIT'];print(a['assert_or_raise_node_counts'],"
               "a['VACUITY_POSITIVE_CONTROL']['assert_or_raise_nodes'])\"",
        result="engine files 0 nodes; positive control 8 nodes; NO_RUNTIME_VALIDATION_EXISTS "
               "established from mechanisms, not from an empty search"),
    "F5": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (exact_mobile_shortfall)",
                       "PMCR01_FINAL_DISPOSITION.json", "PMCR01_FINAL_REPORT.md"],
        pre="the mobile shortfall headline was 13.2x, a single closed-form corner using the "
            "loose substitution S ~ 1/m.",
        post="the exact maximum survival over the real feasible set C2..C6 is reported as the "
             "headline; the closed form is demoted to an illustration and labelled MOBILE-only.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "print(d['BRANCH_SEPARATED_REGIONS']['MOBILE']['exact_shortfall']"
               "['EXACT_SHORTFALL_FACTOR'])\"",
        result="exact max survival 4.537e-06 -> shortfall 110213x, not 13.2x. The direction was "
               "always AGAINST this mission's own case."),
    "F6": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (q_max_by_nY, capacity_limited_chain)",
                       "PMCR01_FINAL_DISPOSITION.json"],
        pre="'the single-Y branching overstates growth, so the 87-point static counter-region "
            "is an optimistic upper bound' -- asserted qualitatively; admissible_Q(CAP, nY) was "
            "never called with nY != 1.",
        post="Q_max(nY) published for nY = 1..16 (28, 24, 21, 18, 15, 12, 10, 8, 6, 4, 3, 2, 1, "
             "0, 0, 0) and an exact capacity-limited 17-state chain evaluated at the static box "
             "edge. The mitigation as written is WITHDRAWN: the correction is negligible and "
             "the counter-region survives the occupancy invariant essentially intact.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "print(d['F6_CAPACITY_LIMITED_CHECK']"
               "['exact_capacity_limited_chain_at_the_static_box_edge'])\"",
        result="survival 0.9341 and E[nY(T)] 7.60 under the capacity-limited chain against "
               "0.894 and <= 10 unconstrained; Q_max reaches 0 at nY = 14"),
    "F7": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_repair_apply.py (FOUR_PROPOSITIONS)",
                       "PMCR01_FINAL_DISPOSITION.json"],
        pre="FOUR_PROPOSITIONS.WHY_THEY_ARE_NOT_INTERCHANGEABLE said the fourth 'is answered "
            "negatively, on three independent grounds', contradicting DISPOSITION_RESTS_ON.",
        post="rewritten: the repaired answer is NOT_YET_LOCATED on ONE branch-independent "
             "operational ground -- the absence of a prospectively frozen Q bound -- and is "
             "explicitly not a proof of non-existence.",
        verify="grep -c 'three independent grounds' PMCR01_FINAL_DISPOSITION.json",
        result="0 occurrences remain"),
    "F8": dict(
        accepted=True, mode="A_REPAIRED_MECHANICALLY",
        files_changed=["pmcr01_sentinel.py (all_mission_output_roots, raw_dir_witness, report)",
                       "pmcr01_oracles.py (RAW_DIRS = None)",
                       "pmcr01_repair_apply.py (SENTINEL_AGGREGATED)"],
        pre="the witness watched three directories chosen by the audited party, one of which "
            "(OBDI02/raw) is empty and could never fire; the sentinel report was per-process; "
            "NEW_PHYSICS_ARRAYS_WRITTEN was not reported.",
        post="the roots are DISCOVERED by glob over /home/claude/*/raw and /home/claude/*/out "
             "(29 roots); npz counts are tracked per root; NEW_PHYSICS_ARRAYS_WRITTEN is "
             "reported; the sentinel is aggregated over all analysis processes.",
        verify="python3 -c \"import json;d=json.load(open('PMCR01_FINAL_DISPOSITION.json'));"
               "print(d['SENTINEL_AGGREGATED'])\"",
        result="29 roots watched; construct/advance/starts/seeds/new-npz all 0 across all "
               "processes; ALL_ZERO_EVERYWHERE true"),
}

# the instrument gap F8 also raised, kept explicit rather than silently closed
UNREPAIRED_WITH_REASON = {
    "F8_residual_instrument_gap": {
        "what": "_diffuse / _react / _decay are still not individually instrumented by the "
                "sentinel, so a trajectory assembled from direct operator calls would not be "
                "counted as an advance.",
        "mode": "B_LEFT_UNREPAIRED_WITH_A_STATED_REASON",
        "reason": ("instrumenting the three operators would require patching methods that the "
                   "mutation oracles themselves drive through _one_step, and would change the "
                   "very code path under audit during the audit. The gap is closed by two "
                   "independent means instead: (i) a grep proving no PMCR01 code calls the "
                   "operators directly -- the sole match, pmcr01_map.py:21, is inside a "
                   "docstring; and (ii) the filesystem witness over 29 discovered output roots "
                   "showing NEW_PHYSICS_ARRAYS_WRITTEN = 0. The guarantee is therefore stated "
                   "with its exact scope rather than overclaimed."),
        "scope_statement": "the zero-run guarantee covers _one_step-mediated advances, and is "
                           "corroborated by a filesystem witness that is independent of every "
                           "in-process counter",
    }
}


def main():
    rev = json.load(open(f"{REVIEW}/PMCR01_ADVERSARIAL_REVIEW.json"))
    rows = []
    for f in rev["findings"]:
        fid = f["id"]
        rep = R.get(fid)
        row = {
            "finding_id": fid,
            "severity": f["severity"],
            "review_status": f["status"],
            "claim_attacked": f["claim_attacked"],
            "exact_files_and_lines_attacked": f["exact_evidence"][:600],
            "defect_accepted": bool(rep["accepted"]) if rep else None,
            "repair_mode": rep["mode"] if rep else "NOT_A_DEFECT__ATTACK_REFUTED",
            "exact_files_changed": rep["files_changed"] if rep else [],
            "exact_pre_repair_claim": rep["pre"] if rep else None,
            "exact_repaired_claim": rep["post"] if rep else None,
            "deterministic_verification_command": rep["verify"] if rep else
            f.get("settling_command_or_calculation"),
            "post_repair_result": rep["result"] if rep else
            "claim survived the attack; retained unchanged",
        }
        rows.append(row)

    confirmed = [r for r in rows if r["review_status"] == "DEFECT_CONFIRMED"]
    unhandled = [r["finding_id"] for r in confirmed
                 if r["repair_mode"] == "NOT_A_DEFECT__ATTACK_REFUTED"]
    out = {
        "SECTION": "PMCR01 repair §1 — review repair matrix",
        "REPAIR": "PMCR01-REVIEW-DRIVEN-Q-INSTRUMENTATION-REPAIR-01",
        "REVIEW_SOURCE": {
            "md": f"{REVIEW}/PMCR01_ADVERSARIAL_REVIEW.md",
            "json": f"{REVIEW}/PMCR01_ADVERSARIAL_REVIEW.json",
            "md_sha256": hashlib.sha256(
                open(f"{REVIEW}/PMCR01_ADVERSARIAL_REVIEW.md", "rb").read()).hexdigest(),
            "json_sha256": hashlib.sha256(
                open(f"{REVIEW}/PMCR01_ADVERSARIAL_REVIEW.json", "rb").read()).hexdigest(),
            "REVIEW_FILES_MODIFIED_BY_THIS_REPAIR": False},
        "reviewed_tip": rev["reviewed_tip"],
        "N_FINDINGS": len(rows),
        "N_DEFECTS_CONFIRMED": len(confirmed),
        "N_ATTACKS_REFUTED": sum(1 for r in rows if r["review_status"] == "ATTACK_REFUTED"),
        "N_PLAUSIBLE_UNRESOLVED": sum(1 for r in rows
                                      if r["review_status"] == "DEFECT_PLAUSIBLE"),
        "EVERY_CONFIRMED_DEFECT_HANDLED": not unhandled,
        "UNHANDLED_CONFIRMED_DEFECTS": unhandled,
        "MATRIX": rows,
        "LEFT_UNREPAIRED_WITH_A_LOAD_BEARING_REASON": UNREPAIRED_WITH_REASON,
        "COSMETIC_REWRITE_DISCLAIMER": (
            "F1 concerns the scientific disposition and was NOT closed by rewording: the "
            "disposition itself is changed, the checklist item is recomputed, the superseded "
            "handoff is retired and a different next mission is issued."),
    }
    json.dump(out, open(f"{OUT}/PMCR01_REVIEW_REPAIR_MATRIX.json", "w"), indent=1, default=str)
    print("findings=%d confirmed=%d refuted=%d plausible=%d ; every confirmed handled=%s"
          % (out["N_FINDINGS"], out["N_DEFECTS_CONFIRMED"], out["N_ATTACKS_REFUTED"],
             out["N_PLAUSIBLE_UNRESOLVED"], out["EVERY_CONFIRMED_DEFECT_HANDLED"]))
    for r in rows:
        if r["review_status"] == "DEFECT_CONFIRMED":
            print("  %-4s %-13s %s" % (r["finding_id"], r["severity"], r["repair_mode"]))


if __name__ == "__main__":
    main()
