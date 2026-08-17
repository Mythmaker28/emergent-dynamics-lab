"""MYQBD01 FINAL SEAL — the corrections record. Every superseded value, old -> new, in one place.

The MASTER FREEZE is NOT touched. A freeze that is edited after the fact is not a freeze; the
corrections are recorded alongside it and name exactly what they supersede.
"""
from __future__ import annotations
import json

OUT = "/home/claude/MYQBD01/out"

C = [
 {"ID": "C-F16", "finding": "F16", "file": "MYQBD01_FEEDBACK_BOUND.json -> FEEDBACK",
  "field": "DETERMINISTIC_PERTURBATION_BOUND.one_Y_birth.recovery_rate_per_step",
  "OLD": 0.2, "NEW": 0.35573502919515165,
  "why": ("phi = 0.20 is the _exchange OFFER rate, not the effective replenishment rate: the "
          "cell also loses SY to a hypergeometric removal and gains SY by diffusion. Measured "
          "by regressing d(nSY) on (S0 - nSY) over the 14 static arms, steps 2000-10999."),
  "sd_over_static_arms": 0.01347266465065013, "ratio_new_over_old": 1.7786751459757582,
  "direction": "CONSERVATIVE: recovery is FASTER than claimed, so the first-birth error is "
               "SMALLER than the pre-seal record stated"},
 {"ID": "C-F17", "finding": "F17", "file": "MYQBD01_FEEDBACK_BOUND.json -> FEEDBACK",
  "field": "DETERMINISTIC_PERTURBATION_BOUND.one_Y_birth.as_fraction_of_mean_nSY",
  "OLD": "-1/0.985048 = -101.52% (unconditional mean nSY)",
  "NEW": "-1/1.814057 = -55.13% (conditional on cand_Y >= 1)",
  "why": ("a Y birth is possible only when cand_Y = min(nSY, free) >= 1. The unconditional mean "
          "is the wrong denominator; conditional on a birth being possible the organiser cell "
          "holds 1.814057 SY on average (E[cand_Y | cand_Y>=1] = 1.777084)."),
  "direction": "CONSERVATIVE: the depletion is smaller than claimed"},
 {"ID": "C-F08", "finding": "F08", "file": "MYQBD01_FEEDBACK_BOUND.json -> SPATIAL",
  "field": "SUBSTEP_LEDGERS_ARE_SCALAR (key renamed to LEDGER_CONTENTS)",
  "OLD": "'these carry step, sub-step index and scalar organiser-cell counts'",
  "NEW": ("source_substep_ledger is (44000,6) = (step, species_index, org_y_before, "
          "org_x_before, org_y_after, org_x_after): 4 of 6 columns are lattice coordinates. It "
          "records 1038 organiser moves over 373 distinct cells in the arm inspected."),
  "why": "the label was factually wrong",
  "direction": ("STRENGTHENS: because the organiser trajectory IS recorded, Q_ORGANISER is the "
                "FOUNDER's exact lineage exposure in the mobile branch too, not only the static "
                "branch. The gap is descendants, not motion.")},
 {"ID": "C-F09/F23", "finding": "F09, F23", "file": "myqbd01_spatial_feedback.py -> §12",
  "field": "Q_POSITION_RECOVERABLE_FOR_A_SEPARATED_DESCENDANT",
  "OLD": "hardcoded literal False, from 1 of 28 archives with 0 key contents inspected",
  "NEW": ("DERIVED over all 28 archives: key sets identical, no array of shape (T,L,L) in any "
          "arm, all 220 `frames` decoded and every value asserted scalar, and an information "
          "budget showing the archive is ~49x too small to carry the field"),
  "why": "a load-bearing boolean returned as a literal is not evidence, even when it is right",
  "direction": "NEUTRAL on the value, decisive on the evidence"},
 {"ID": "C-F10", "finding": "F10", "file": "myqbd01_spatial_feedback.py -> §12 WHY",
  "field": "the stated reason Q_POSITION is unavailable",
  "OLD": "'a mobile descendant that separates occupies a DIFFERENT cell whose (nX,nSY,free) is "
         "not recorded' (non-recording)",
  "NEW": ("with kY = 0 no Y birth occurs in ANY arm: N_Y == 1 at all 308000 recorded steps "
          "across all 28 archives. A separated descendant does not merely go unrecorded -- it "
          "never exists."),
  "why": "the decisive fact sat in §13 and never entered §12",
  "direction": "STRENGTHENS the disposition"},
 {"ID": "C-F20/F21", "finding": "F20, F21", "file": "MYQBD01_DISCOVERY_REGION.json",
  "field": "STRUCTURAL_PRECLUSION_CHECK framing and witness",
  "OLD": "'the MOST FAVOURABLE admissible environment (Q sustained at Q_MAX)'; c_box = 3 "
         "described as 'near the mean organiser-cell candidate pool'",
  "NEW": ("framing dropped (the witness uses exposure 12, not Q_MAX = 28); measured mean "
          "cand_Y_at_org = 0.961651 recorded, so c = 3 is 3.12x it; and a THIRD witness added at "
          "the arms' OWN measured magnitudes: R = 1.000163936 > 1"),
  "why": "non-preclusion must not rest on an inflated pool",
  "direction": "STRENGTHENS: non-preclusion now holds at the measured environment"},
 {"ID": "C-F25", "finding": "F25", "file": "myqbd01_regions.py -> requirements",
  "field": "NO_TARGET_DERIVED_Y_OUTCOME",
  "OLD": "hardcoded literal True with a comment; 0 AST data-access checks existed",
  "NEW": ("DERIVED by myqbd01_seal_audits.target_derived_audit(): AST walk of all 8 modules, "
          "129 data-access keys collected from Subscript and .index() positions only, 0 "
          "outcome-descriptor accesses, 1 container read (`frames`) disclosed with its "
          "justification"),
  "why": "the requirement asserted a check that did not exist",
  "direction": "NEUTRAL on the value, decisive on the evidence"},
 {"ID": "C-F27/F30", "finding": "F27, F30", "file": "myqbd01_regions.py -> requirements",
  "field": "SCIENTIFIC_RUNS_USED_ZERO / the zero-run ground",
  "OLD": "a literal, resting on a sentinel claimed to be 'aggregated over ALL ANALYSIS "
         "PROCESSES' but installed in 1 of 8 modules",
  "NEW": ("DERIVED by a static import proof: no MYQBD01 module imports any engine module, so "
          "none could construct or step a World, whatever a runtime counter says"),
  "why": "the coverage claim was false; the conclusion needed a ground that does not depend on it",
  "direction": "STRENGTHENS: the ground is now stronger than the one claimed"},
 {"ID": "C-F05", "finding": "F05", "file": "MYQBD01_TEMPORAL_DEPENDENCE.json (reported summary)",
  "field": "'IAT ~7-9'",
  "OLD": "IAT ~7-9, reported as branch means only",
  "NEW": ("estimator-dependent AND heavy-tailed. Operator's initial-positive-sequence estimator: "
          "mobile mean 8.4277, max 24.5556 (M__seed9300015); static mean 7.1756, max 9.7186 "
          "(S__seed9300009). Reviewer's overlapping-pair variant: mobile mean 9.1967, max "
          "35.335. Same outlier arm, different magnitude."),
  "why": ("a bare branch mean hides a single arm at 3-4x it. Neither estimate is canonised; the "
          "divergence is itself the finding, and the successor must freeze one estimator."),
  "direction": ("CONSERVATIVE: a larger IAT means LESS independent information per arm, which "
                "supports the insufficiency disposition rather than undermining it")},
 {"ID": "C-F13/F15", "finding": "F13, F15", "file": "MYQBD01_TWO_Y_OPERATOR.json",
  "field": "the counterexample scale and conditions 7-8",
  "OLD": "non-independence demonstrated at kY = 0.05 and 0.20, i.e. 1250x and 5000x admissible; "
         "conditions 7 and 8 stated without magnitude",
  "NEW": ("magnitudes at the admissible kY = 4e-5 recorded: relative variance gap -1.6e-4, "
          "support-excess probability 9.8e-15, quenched-vs-scalar relative gap 2.05e-4. "
          "NOT_IDENTIFIABLE rests on the SPATIAL ground, not on the branching-process gap."),
  "why": "a demonstration at 1250x the mission's own scale is a rhetorical scale",
  "direction": "WEAKENS two supporting arguments; the classification is unaffected"},
 {"ID": "C-F02/F03", "finding": "F02, F03", "file": "MYQBD01_Q_PHASE_MAP.json",
  "field": "ENGINE_Y_BIRTH provenance and the step-label convention",
  "OLD": "cites kinetics.py:117/119/120; no step-label convention recorded",
  "NEW": ("the executed engine is WorldOBTC (engine_obtc.py:162/165/166); kinetics.py lines are "
          "INHERITED_EQUIVALENT, not executed. series[:,0] is post-increment 1..11000 while all "
          "four ledgers label the same physical sub-step pre-increment 0..10999."),
  "why": "citing an inherited site as the executed one, and an undocumented off-by-one convention",
  "direction": "NEUTRAL: the event-phase identity itself is unaffected (F01 refuted the attack)"},
]

NOT_REPAIRABLE = [
 {"ID": "N-F31", "finding": "F31",
  "what": ("MYQBD01_MASTER_FREEZE.{md,json} was committed in the SAME commit (decfda5) as "
           "MYQBD01_ARM_LEVEL_Q_SUMMARIES.{csv,json} and MYQBD01_TEMPORAL_DEPENDENCE.json. "
           "Independent Git checkpoints separating the freeze from the statistics: 0."),
  "why_not_repairable": ("separating them retroactively would require rewriting inherited "
                         "history, which this program forbids. Editing the freeze after the "
                         "fact would be worse than the defect."),
  "why_not_load_bearing": ("the freeze's own text declares the mission response-informed and "
                           "developmental and explicitly disclaims blinding, and all 28 arms are "
                           "classified POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC. No claim in the "
                           "record depends on the freeze predating the access."),
  "successor_requirement": ("PQEC01 must commit its freeze ALONE, in its own commit, before any "
                            "module that reads trajectory values is run, and record that commit "
                            "hash inside the freeze.")},
 {"ID": "N-F28", "finding": "F28",
  "what": ("observe.seed_one_organiser is a fourth seeding entry point and is not patched by "
           "the sentinel (kinetics, lawspec_v2 and engine_obtc are)."),
  "why_not_repairable": ("the sentinel lives in the inherited PMCR01 tree, which this mission "
                         "may not rewrite."),
  "why_not_load_bearing": ("no MYQBD01 module imports observe -- or any engine module -- as the "
                           "static import proof shows, so the unpatched entry point was "
                           "unreachable from this mission's code."),
  "successor_requirement": "patch all four entry points and name four in the comment."},
 {"ID": "N-F29", "finding": "F29",
  "what": ("the filesystem witness globs at depth 2 and does not watch the repository tree; 13 "
           "directories matching /home/claude/edl/*/out are unwatched."),
  "why_not_repairable": "same inherited-tree constraint.",
  "why_not_load_bearing": ("superseded as a ground by the static import proof, which does not "
                           "depend on filesystem watching at all."),
  "successor_requirement": "glob recursively and record the depth in the scope note."},
]


def main():
    rec = {"SECTION": "MYQBD01 FINAL SEAL — corrections record",
           "THE_MASTER_FREEZE_IS_NOT_EDITED": ("a freeze that is edited after the fact is not a "
                                               "freeze. Every correction below is recorded "
                                               "ALONGSIDE the freeze and names exactly what it "
                                               "supersedes."),
           "REPAIR_ROUNDS_USED": 1, "REPAIR_COMMITS_USED": 1,
           "CORRECTIONS": C, "NOT_REPAIRABLE": NOT_REPAIRABLE,
           "DISPOSITION_BEFORE": "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED",
           "DISPOSITION_AFTER": "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED",
           "NET_EFFECT": ("of the 11 corrections, 4 STRENGTHEN the disposition's grounds "
                          "(C-F08, C-F10, C-F20/F21, C-F27/F30), 3 move a number in the "
                          "CONSERVATIVE direction (C-F16, C-F17, C-F05), 2 replace a literal by "
                          "a derivation without changing its value (C-F09/F23, C-F25), and 2 "
                          "weaken supporting arguments the classification never rested on "
                          "(C-F13/F15, C-F02/F03). None moves the disposition.")}
    json.dump(rec, open(f"{OUT}/MYQBD01_SEAL_CORRECTIONS.json", "w"), indent=1, default=str)
    md = ["# MYQBD01 — corrections applied in the single seal repair round", "",
          "> The MASTER FREEZE is not edited. " + rec["THE_MASTER_FREEZE_IS_NOT_EDITED"], "",
          "## Superseded values", ""]
    for c in C:
        md += ["### %s (review %s)" % (c["ID"], c["finding"]),
               "- **where** `%s` -> `%s`" % (c["file"], c["field"]),
               "- **was** %s" % c["OLD"], "- **now** %s" % c["NEW"],
               "- **why** %s" % c["why"], "- **direction** %s" % c["direction"], ""]
    md += ["## Confirmed but NOT repairable here", ""]
    for x in NOT_REPAIRABLE:
        md += ["### %s (review %s)" % (x["ID"], x["finding"]), "- **what** %s" % x["what"],
               "- **why not repairable** %s" % x["why_not_repairable"],
               "- **why not load-bearing** %s" % x["why_not_load_bearing"],
               "- **successor must** %s" % x["successor_requirement"], ""]
    md += ["## Net effect", "", rec["NET_EFFECT"], ""]
    open(f"{OUT}/MYQBD01_SEAL_CORRECTIONS.md", "w").write("\n".join(md) + "\n")
    print("corrections:", len(C), "| not repairable:", len(NOT_REPAIRABLE))


if __name__ == "__main__":
    main()
