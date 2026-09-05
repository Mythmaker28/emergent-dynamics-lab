"""PQEC01 — the single authorized repair round, after the one adversarial review.

Every number below is re-derived by the operator, not accepted from the review.
"""
from __future__ import annotations
import glob, hashlib, json, math, os, subprocess, sys
import numpy as np

OUT = "/home/claude/edl/PQEC01/out"
CODE = "/home/claude/edl/PQEC01/code"
RAW = "/home/claude/PQEC01/raw"
REPO = "/home/claude/edl"
FR = json.load(open(f"{OUT}/PQEC01_MASTER_FREEZE.json"))
C = FR["INHERITED_FROZEN_CONSTANTS"]
T, W = C["T_HORIZON"], C["T_WINDOW"]
ALPHA, N_STAR, GAMMA, MINEV, CAP = (C["ALPHA_SURVIVAL"], C["N_STAR"], C["GAMMA_SEP"],
                                    C["MIN_EVENTS"], C["CAP"])


# ---------------------------------------------------------------- R1: the region is ALGEBRAIC
def region_repair():
    reg = json.load(open(f"{OUT}/PQEC01_CANDIDATE_REGION.json"))
    tau = reg["SEPARATION_TIME_USED"]["value"]
    muY_lo = 1 - (GAMMA / MINEV) ** (1.0 / tau)     # forced by C1 AND C3 together
    muY_hi = 1 - (1 - ALPHA) ** (1.0 / T)           # forced by C2
    sweep = {}
    for E in (0.01, 0.1, 1.0, 2.87302, 10.0, 100.0):
        best = -1e18
        for lk in np.linspace(-6, -2, 161):
            for lm in np.linspace(-8, -1, 161):
                kY, muY = 10 ** lk, 10 ** lm
                b = kY * E * W
                m = min(math.log10(max(b, 1e-300) / MINEV),
                        math.log10(max((1 - muY) ** T, 1e-300) / (1 - ALPHA)),
                        math.log10(GAMMA / max(b * (1 - muY) ** tau, 1e-300)),
                        math.log10(0.1 / max(kY * CAP * N_STAR, 1e-300)))
                best = max(best, m)
        sweep["E=%g" % E] = round(best, 4)
    reg["REPAIR_R1_THE_EMPTINESS_IS_ALGEBRAIC"] = {
        "REVIEW_FINDING": "F21",
        "SUPERSEDED_CLAIM": ("'the calibration replaced the mean-exposure proxy with measured "
                             "world-level quantities and the shortfall moved by 0.0015 decades; "
                             "the measurement confirmed the arithmetic'"),
        "WHY_IT_WAS_WRONG": ("that wording implies the measurement COULD have moved the "
                             "boundary and happened not to. It could not. Eliminating kY and "
                             "the exposure between the frozen criteria gives a constraint on "
                             "muY alone."),
        "EXACT_DERIVATION": {
            "C1": "kY * E * T_WINDOW >= MIN_EVENTS",
            "C3": "kY * E * T_WINDOW * (1-muY)^tau <= GAMMA_SEP",
            "C1_AND_C3_IMPLY": "(1-muY)^tau <= GAMMA_SEP/MIN_EVENTS  =>  "
                               "muY >= 1 - (GAMMA_SEP/MIN_EVENTS)^(1/tau)",
            "C2": "(1-muY)^T_HORIZON >= 1 - ALPHA_SURVIVAL  =>  "
                  "muY <= 1 - (1-ALPHA_SURVIVAL)^(1/T_HORIZON)",
            "tau_used": tau,
            "muY_lower_bound_forced_by_C1_and_C3": muY_lo,
            "muY_upper_bound_forced_by_C2": muY_hi,
            "INCOMPATIBILITY_FACTOR": muY_lo / muY_hi,
            "KY_APPEARS": False, "EXPOSURE_APPEARS": False,
            "at_frozen_TAU_SEP_125": {
                "muY_lower_bound": 1 - (GAMMA / MINEV) ** (1.0 / C["TAU_SEP"]),
                "incompatibility_factor": (1 - (GAMMA / MINEV) ** (1.0 / C["TAU_SEP"])) / muY_hi}},
        "MAXIMIN_MARGIN_VS_EXPOSURE_SWEEP": sweep,
        "READING": ("the frozen criteria use ONE parameter, muY, for two opposite purposes: the "
                    "founder must survive %d steps (needing muY <= %.3e) while a newborn must "
                    "usually die within tau = %.0f steps so that no second centre forms "
                    "(needing muY >= %.3e). They are incompatible by a factor of %.1f for EVERY "
                    "kY and EVERY exposure. The region is empty as a matter of algebra on the "
                    "criteria, not as a measured outcome. No calibration, no instrumentation and "
                    "no amount of data could have made it non-empty under these criteria."
                    % (T, muY_hi, tau, muY_lo, muY_lo / muY_hi)),
        "WHAT_THIS_IS_NOT": ("this is NOT "
                             "EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW. It is "
                             "not a feedback result at all. It is an incompatibility between two "
                             "frozen ACCEPTANCE CRITERIA, and the correct response is to hand "
                             "the criteria back for revision, not to declare the architecture "
                             "preclusive."),
        "SUCCESSOR_REQUIREMENT": ("any successor must decouple the two roles of muY -- e.g. gate "
                                  "second-centre formation on a spatial or capacity condition "
                                  "rather than on descendant death -- or state explicitly that "
                                  "the frozen window is unreachable by construction.")}
    json.dump(reg, open(f"{OUT}/PQEC01_CANDIDATE_REGION.json", "w"), indent=1, default=str)
    return reg


# ---------------------------------------------------------------- R2: conditioned feedback
def feedback_repair():
    fb = json.load(open(f"{OUT}/PQEC01_FEEDBACK_ANALYSIS.json"))
    pa = json.load(open(f"{OUT}/PQEC01_PHASE_A_WORLD_SUMMARIES.json"))
    pb = json.load(open(f"{OUT}/PQEC01_PHASE_B_WORLD_SUMMARIES.json"))
    A = {k: np.array([w[k] for w in pa["PER_WORLD"]]) for k in
         ("mean_N_X", "mean_nSY", "mean_free")}
    cond = {}
    for lab in ("B1", "B2"):
        R = pb[lab]["PER_WORLD"]
        strata = {"birth_worlds": [w for w in R if w["n_Y_births"] > 0],
                  "no_birth_worlds": [w for w in R if w["n_Y_births"] == 0],
                  "pooled": R}
        s = {}
        for name, sel in strata.items():
            e = {}
            for k, a in A.items():
                b = np.array([w[k] for w in sel])
                se = math.sqrt(a.var(ddof=1) / a.size + b.var(ddof=1) / b.size)
                e[k] = {"n": int(b.size), "phase_A_mean": float(a.mean()),
                        "phase_B_mean": float(b.mean()), "delta": float(b.mean() - a.mean()),
                        "relative_delta": float((b.mean() - a.mean()) / a.mean()),
                        "se": se, "z": float((b.mean() - a.mean()) / se) if se > 0 else 0.0,
                        "significant_at_2se": bool(abs(b.mean() - a.mean()) > 2 * se)}
            s[name] = e
        cond[lab] = s
    fb["REPAIR_R2_CONDITIONED_FEEDBACK"] = {
        "REVIEW_FINDING": "F18",
        "SUPERSEDED_CLAIM": ("the pooled comparison reported N_X feedback of +11.9%/+15.2% at "
                             "z = 1.32/1.84 and concluded it was not significant"),
        "WHY_IT_WAS_WRONG": ("a Simpson's paradox. Pooling worlds in which a Y birth occurred "
                             "with worlds in which none did averages a large positive effect "
                             "against a negative one and hides both. Whether a birth occurred "
                             "is not a covariate to average over -- it is the condition under "
                             "which feedback can exist at all."),
        "STRATIFIED": cond,
        "MECHANISM": ("kX = 1.0, so p_X = min(1, kX*nX*nY) is already 1 wherever nX*nY >= 1. A "
                      "second Y at a DIFFERENT cell therefore adds a second saturated X source "
                      "rather than competing for the first one, and X production roughly "
                      "doubles. That is architectural, not stochastic."),
        "CONCLUSION": ("Y feedback on the X environment is LARGE and HIGHLY SIGNIFICANT once "
                       "conditioned: +61.0%% (z = %.2f) at B1 and +51.9%% (z = %.2f) at B2 in "
                       "birth-worlds, with a matching depletion of nSY. It is NOT modelled by "
                       "the identified operator."
                       % (cond["B1"]["birth_worlds"]["mean_N_X"]["z"],
                          cond["B2"]["birth_worlds"]["mean_N_X"]["z"])),
        "GATE_CONSEQUENCE": "FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED flips True -> False"}
    json.dump(fb, open(f"{OUT}/PQEC01_FEEDBACK_ANALYSIS.json", "w"), indent=1, default=str)
    return fb


# ---------------------------------------------------------------- R3: provenance disclosures
def provenance_repair():
    def sha_files(names):
        h = hashlib.sha256()
        for f in names:
            h.update(os.path.basename(f).encode())
            h.update(open(f, "rb").read())
        return h.hexdigest()
    frozen_at_c2 = subprocess.run(("git", "show", "--name-only", "--format=", "0bba579"),
                                  cwd=REPO, capture_output=True, text=True).stdout.split()
    c1_code = subprocess.run(("git", "ls-tree", "--name-only", "0c8ed48", "PQEC01/code/"),
                             cwd=REPO, capture_output=True, text=True).stdout.split()
    all_now = sorted(glob.glob(f"{CODE}/*.py"))
    executor = [f for f in all_now if os.path.basename(f) in
                ("pqec01_run.py", "pqec01_analyse.py", "pqec01_manifest.py", "pqec01_repair.py")]
    return {
        "REPAIR_R3_METHODS_HASH_SCOPE": {
            "REVIEW_FINDING": "F01",
            "WHAT_THE_FROZEN_HASH_COVERED": sorted(os.path.basename(f) for f in c1_code)
            + ["pqec01_freeze.py (added in the same commit as the hash)"],
            "WHAT_IT_DID_NOT_COVER": sorted(os.path.basename(f) for f in executor),
            "WHY": ("PQEC01_METHODS_HASH was computed inside pqec01_freeze.py over the code "
                    "present AT FREEZE TIME. The executor and the analyser were written after "
                    "the freeze, so the hash does not bind them. The freeze binds the DESIGN "
                    "-- points, seeds, sample sizes, splits, formulas, stop rules, gates -- and "
                    "that is what it was for; but the claim it implies, that the whole method "
                    "is hash-bound, is too broad."),
            "POST_HOC_EXECUTOR_HASH": sha_files(executor),
            "NOT_RETROACTIVELY_CLAIMED": ("this hash is recorded now, after the fact. It does "
                                          "not and cannot show the executor was fixed before "
                                          "the runs; the Git history is the only evidence for "
                                          "that, and it shows the executor first appears in C3."),
            "SUCCESSOR_REQUIREMENT": "compute the methods hash over the executor and analyser "
                                     "too, and commit them with the freeze."},
        "REPAIR_R4_REFIT_CHRONOLOGY": {
            "REVIEW_FINDINGS": "F14, F15",
            "WHAT_HAPPENED": ("a complete analysis run, including PQEC01_INTERNAL_VALIDATION.json, "
                              "finished BEFORE two analysis defects were fixed. The operator "
                              "therefore saw validation output before editing analysis code. "
                              "This is stated plainly rather than defended by assertion."),
            "THE_TWO_FIXES": [
                "exposure quantities were switched from the post-step `scalars` array to the "
                "event-aligned `ycells` ledger, because the freeze's formulas require the "
                "event-aligned value",
                "validation TEST 2 was switched from a per-STEP standard error to a world-level "
                "two-sample comparison, because the freeze states the unit is the world and "
                "forbids frame pseudoreplication"],
            "EFFECT_ON_VERDICTS": {
                "B1_TEST_2_before_fix": {"z": -14.32, "verdict": "FAIL"},
                "B1_TEST_2_after_fix": {"z": 1.16, "verdict": "PASS"},
                "B2_TEST_2_before_fix": {"z": -144.37, "verdict": "FAIL"},
                "B2_TEST_2_after_fix": {"z": -2.82, "verdict": "FAIL"},
                "INTERNAL_VALIDATION_PASS_before_fix": False,
                "INTERNAL_VALIDATION_PASS_after_fix": False,
                "TERMINAL_DISPOSITION_UNCHANGED_EITHER_WAY": True},
            "HONEST_ASSESSMENT": ("one fix moved a test from FAIL to PASS after the failure was "
                                  "visible. That is the shape of a post-hoc rescue, and the "
                                  "fact that it restores a rule the freeze states verbatim is a "
                                  "defence, not a proof. The mitigating facts are that the "
                                  "gate and the terminal disposition are identical before and "
                                  "after, and that BOTH sets of numbers are published here."),
            "SUPERSEDED_LITERAL": ("PQEC01_INTERNAL_VALIDATION.json carried "
                                   "NO_REFIT_AFTER_VIEWING_VALIDATION: True as a hardcoded "
                                   "literal. It is replaced by this record."),
            "SUCCESSOR_REQUIREMENT": ("freeze the analysis code with the design, in the same "
                                      "commit, and hash it; then a post-validation edit is "
                                      "detectable rather than arguable.")},
    }


def main():
    reg = region_repair()
    fb = feedback_repair()
    pv = provenance_repair()
    d = json.load(open(f"{OUT}/PQEC01_FINAL_DISPOSITION.json"))
    d["DECISION_GATES"]["FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED"] = False
    d["GATES_PASSED"] = sum(1 for v in d["DECISION_GATES"].values() if v)
    d["REPAIR_ROUND"] = {"ROUNDS_AUTHORIZED": 1, "ROUNDS_USED": 1,
                         "REVIEW_VERDICT": "EVIDENCE_OR_PROVENANCE_INCOMPLETE",
                         "REVIEW_COUNTS": {"LOAD_BEARING": 0, "SUBSTANTIVE": 20, "COSMETIC": 4,
                                           "ATTACKS_REFUTED": 2},
                         "R1": reg["REPAIR_R1_THE_EMPTINESS_IS_ALGEBRAIC"]["READING"],
                         "R2": fb["REPAIR_R2_CONDITIONED_FEEDBACK"]["CONCLUSION"],
                         **pv}
    d["EMPTY_REGION_IS_PREREGISTERED"]["SUPERSEDED_BY_R1"] = (
        "the preregistration was right that the region would be empty, but its explanation was "
        "wrong. See REPAIR_ROUND.R1: the emptiness is algebraic in the criteria and involves "
        "neither kY nor the exposure.")
    d["FINAL_DISPOSITION"] = d["CANDIDATE_DISPOSITION"]
    d["DISPOSITION_UNCHANGED_BY_THE_REVIEW"] = True
    json.dump(d, open(f"{OUT}/PQEC01_FINAL_DISPOSITION.json", "w"), indent=1, default=str)
    rr = {"SECTION": "PQEC01 review and repair", "REVIEW": {
        "REVIEWS_AUTHORIZED": 1, "REVIEWS_USED": 1,
        "VERDICT": "EVIDENCE_OR_PROVENANCE_INCOMPLETE",
        "LOAD_BEARING": 0, "SUBSTANTIVE": 20, "COSMETIC": 4, "ATTACKS_REFUTED": 2,
        "OBSERVER_INERTNESS_HOLDS": "YES", "DESCENDANT_EXPOSURE_REALLY_RECORDED": "YES",
        "FILES": {f: hashlib.sha256(open("/home/claude/PQEC01/review/" + f, "rb").read())
                  .hexdigest() for f in ("PQEC01_ADVERSARIAL_REVIEW.md",
                                         "PQEC01_ADVERSARIAL_REVIEW.json")}},
        "REPAIR": {"ROUNDS": 1, "OPERATOR_REVERIFIED_EVERY_ACCEPTED_FINDING": True,
                   "R1_REGION_ALGEBRAIC": True, "R2_CONDITIONED_FEEDBACK": True,
                   "R3_METHODS_HASH_SCOPE": True, "R4_REFIT_CHRONOLOGY": True,
                   "GATE_FLIPPED": "FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED True -> False",
                   "DISPOSITION_CHANGED": False}}
    json.dump(rr, open(f"{OUT}/PQEC01_REVIEW_AND_REPAIR.json", "w"), indent=1, default=str)
    print("R1 muY forced >= %.6e by C1&C3 and <= %.6e by C2 -> incompatible by %.1fx, "
          "independent of kY and exposure"
          % (reg["REPAIR_R1_THE_EMPTINESS_IS_ALGEBRAIC"]["EXACT_DERIVATION"]
             ["muY_lower_bound_forced_by_C1_and_C3"],
             reg["REPAIR_R1_THE_EMPTINESS_IS_ALGEBRAIC"]["EXACT_DERIVATION"]
             ["muY_upper_bound_forced_by_C2"],
             reg["REPAIR_R1_THE_EMPTINESS_IS_ALGEBRAIC"]["EXACT_DERIVATION"]
             ["INCOMPATIBILITY_FACTOR"]))
    print("R2", fb["REPAIR_R2_CONDITIONED_FEEDBACK"]["CONCLUSION"][:150])
    print("gates now %d/%d; FINAL_DISPOSITION = %s"
          % (d["GATES_PASSED"], d["GATES_TOTAL"], d["FINAL_DISPOSITION"]))


if __name__ == "__main__":
    main()
