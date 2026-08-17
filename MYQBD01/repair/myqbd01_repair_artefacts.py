"""MYQBD01 FINAL REPAIR — artefact consolidation (§12, §13, §14, §15, §17).

Merges the repaired evidence into the delivered artefacts, separates the three commit roles,
discloses the freeze defect, and reports zero-run compliance in three honest parts.
"""
from __future__ import annotations

import ast
import csv
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myqbd01_repair_guard as GUARD                                         # noqa: E402
GUARD.install()

OUT = "/home/claude/edl/MYQBD01/out"
CODE = "/home/claude/edl/MYQBD01/code"
REPAIR = "/home/claude/edl/MYQBD01/repair"
REPO = "/home/claude/edl"
FREEZE_COMMIT = "decfda575000775b1d49025af64636f6b2e97037"
PRE_REPAIR_TIP = "f88147a3b5603aa2c301061c495fdd87200b3b55"
ENGINE_MODULES = {"kinetics", "engine_obtc", "lawspec_v2", "observe", "protocol_obtc02",
                  "protocol_obtc", "run_obfor01", "metrics_obtc", "guard_obtc"}


def J(name):
    return json.load(open(os.path.join(OUT, name)))


def W(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), "w"), indent=1, default=str)


# ---------------------------------------------------------------- §12 zero-run, three parts
def zero_run_report():
    analysis = sorted(glob.glob(os.path.join(CODE, "*.py")))
    infra = sorted(glob.glob(os.path.join(REPAIR, "*.py")))
    offenders, per_mod = [], {}
    for path in analysis:
        tree = ast.parse(open(path).read())
        imp = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                imp |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                imp.add(n.module.split(".")[0])
        bad = sorted(imp & ENGINE_MODULES)
        per_mod[os.path.basename(path)] = bad
        if bad:
            offenders.append(os.path.basename(path))
    g = GUARD.report()
    return {
        "SECTION": "MYQBD01 zero-run compliance, reported in three separable parts",
        "ORIGINAL_RUNTIME_SENTINEL_COVERAGE": {
            "STATUS": "INCOMPLETE",
            "defects_acknowledged": [
                "installed in 1 of 8 analysis modules, not 'all analysis processes' as commit "
                "decfda5 claimed",
                "observe.seed_one_organiser -- a full re-implementation, not a delegator -- was "
                "never patched; 3 of 4 module-level seeding entry points were covered",
                "the filesystem witness globbed /home/claude/*/raw and /home/claude/*/out at "
                "depth 2, so it never watched the repository tree (13 directories match "
                "/home/claude/edl/*/out)"],
            "NOT_RETROACTIVELY_CLAIMED": ("this coverage cannot be improved after the fact and "
                                          "is not presented as if it had been")},
        "RETROSPECTIVE_STATIC_ZERO_RUN_PROOF": {
            "STATUS": "PASS" if not offenders else "FAIL",
            "METHOD": "AST import analysis of every MYQBD01 ANALYSIS module; independent of any "
                      "runtime counter",
            "analysis_modules": len(per_mod), "per_module_engine_imports": per_mod,
            "modules_importing_an_engine": offenders,
            "NO_WORLD_CONSTRUCTION_POSSIBLE": not offenders,
            "WHY_THIS_IS_DECISIVE": ("a module that never imports kinetics, lawspec_v2, "
                                     "engine_obtc, observe, a protocol or a runner cannot "
                                     "construct a World, call _one_step, seed an organiser or "
                                     "continue a checkpoint, whatever any counter reports."),
            "INFRASTRUCTURE_EXCEPTION_DECLARED": {
                "modules": [os.path.basename(p) for p in infra
                            if "guard" in os.path.basename(p)],
                "reading": ("the repair guard is the ONE file that imports the engine, and it "
                            "does so solely to patch every entry point so that a call raises. "
                            "It is repair infrastructure, not analysis. Counting it inside the "
                            "analysis set would be the same overstated-coverage error the "
                            "review caught.")}},
        "FINAL_REPAIR_RUNTIME_GUARDS": {
            "STATUS": "PASS" if g["VERDICT"]["ALL_ZERO"] else "FAIL",
            "PATCH_COVERAGE": g["PATCH_COVERAGE"],
            "FILESYSTEM_WITNESS": {k: v for k, v in g["FILESYSTEM_WITNESS"].items()
                                   if k != "CREATED" or True},
            "SUBPROCESS_AUDIT": g["SUBPROCESS_AUDIT"],
            "POSITIVE_CONTROL": ("the guard's selftest calls World(...) and seed_one_organiser "
                                 "and requires BOTH to raise; a guard that cannot be shown to "
                                 "fire is not evidence."),
            "COUNTERS": g["COUNTERS"]},
        "REQUIRED_FINAL_VALUES": g["COUNTERS"],
        "ALL_REQUIRED_ZERO": g["VERDICT"]["ALL_ZERO"],
        "HOW_COMPLIANCE_IS_ESTABLISHED": (
            "by the combined retrospective STATIC import proof and the recursive filesystem "
            "witness -- NOT by the original incomplete runtime sentinel alone."),
        "A_RUN_IS_NOT_DEFINED_BY_LATTICE_SIZE_OR_SEED_NUMBER": (
            "any World construction, scheduler advance, seeding call or new physics array counts, "
            "regardless of L or of how large the seed integer is."),
    }


# ---------------------------------------------------------------- §13 / §14 provenance
def provenance():
    def one(rev, path):
        return subprocess.run(("git", "log", "--format=%H", "-1", rev, "--", path), cwd=REPO,
                              capture_output=True, text=True).stdout.strip()
    freeze_c = one("HEAD", "MYQBD01/out/MYQBD01_MASTER_FREEZE.json")
    stats_c = one("HEAD", "MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.json")
    head = subprocess.run(("git", "rev-parse", "HEAD"), cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    mh = open(os.path.join(OUT, "MYQBD01_METHODS_HASH.txt")).read().strip()
    return {
        "SECTION": "MYQBD01 provenance — freeze chronology and the three distinct commit roles",
        "FREEZE": {
            "FREEZE_FILE_EXISTS": os.path.exists(os.path.join(OUT,
                                                              "MYQBD01_MASTER_FREEZE.json")),
            "INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT": freeze_c != stats_c,
            "freeze_first_committed_in": freeze_c,
            "arm_statistics_first_committed_in": stats_c,
            "independent_pre_statistics_checkpoints": 0,
            "NOT_REWRITTEN": ("history is not rewritten and no earlier checkpoint is invented"),
            "WHY_IT_DOES_NOT_OVERTURN_THE_RESULT": (
                "this mission is explicitly developmental -- all 28 arms are classified "
                "POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC and the freeze's own text declares the "
                "work response-informed and disclaims blinding -- and it reaches the "
                "CONSERVATIVE calibration disposition. A missing preregistration checkpoint can "
                "only inflate a positive claim; there is no positive claim here to inflate."),
            "WORDING_NOW_PROHIBITED": ["mechanically enforced preregistration",
                                       "independently committed before analysis",
                                       "blinded", "preregistered"],
            "METHODS_HASH_ROLE": {
                "value": mh,
                "IS": "a provenance record of the method text",
                "IS_NOT": "proof of an independent Git checkpoint"}},
        "COMMIT_ROLES": {
            "MASTER_FREEZE_AND_ANALYSIS_COMMIT": FREEZE_COMMIT,
            "PRE_REPAIR_REVIEWED_TIP": PRE_REPAIR_TIP,
            "POST_REPAIR_FINAL_TIP": "resolved after the single repair commit; see MANIFEST.txt",
            "CURRENT_HEAD_WHEN_WRITTEN": head,
            "DO_NOT_CONFLATE": ("decfda5 is the freeze+analysis commit, f88147a is the tip the "
                                "reviewer read, and the post-repair tip is a third thing. The "
                                "seal launcher's original reference to decfda5 as 'the "
                                "candidate' conflated the first two.")},
    }


# ---------------------------------------------------------------- §17 artefact regeneration
def main():
    a1 = J("MYQBD01_Q_PHASE_MAP_REPAIRED.json")
    a2 = J("MYQBD01_TEMPORAL_DEPENDENCE.json")
    a4 = J("MYQBD01_DESCENDANT_RECOVERABILITY_AUDIT.json")
    a10 = J("MYQBD01_DATA_ACCESS_AUDIT.json")
    ops = J("MYQBD01_TWO_Y_OPERATOR.json")
    fb = J("MYQBD01_FEEDBACK_BOUND.json")
    adj = J("MYQBD01_REVIEW_ADJUDICATION.json")

    # ---- phase map: keep the original, add the repaired executed-source section ----
    pm = J("MYQBD01_Q_PHASE_MAP.json")
    pm["REPAIRED_EXECUTED_SOURCE_CITATIONS"] = a1["EXECUTED_Y_BIRTH_SITE"]
    pm["REPAIRED_EXECUTED_CLASS_CHAIN"] = a1["EXECUTED_CLASS_CHAIN"]
    pm["REPAIRED_Q_WRITE_SITE"] = a1["Q_WRITE_SITE"]
    pm["CORRECTION_F02_EXECUTED_VS_INHERITED"] = a1["CORRECTION_F02"]
    pm["STEP_LABEL_CONVENTION"] = a1["STEP_LABEL_CONVENTION"]
    pm["OBSERVE_RECWORLD_NOTE"] = a1["OBSERVE_RECWORLD_NOTE"]
    pm["Q_LEDGER_STATUS"] = "EVENT_EXACT"
    pm["EVENT_PHASE_IDENTITY_UNCHANGED"] = a1["EVENT_PHASE_IDENTITY_UNCHANGED"]
    W("MYQBD01_Q_PHASE_MAP.json", pm)
    os.remove(os.path.join(OUT, "MYQBD01_Q_PHASE_MAP_REPAIRED.json"))

    # ---- arm-level summaries: add the full IAT panel ----
    per = {r["arm"]: r for r in a2["PER_ARM"]}
    rows = list(csv.DictReader(open(os.path.join(OUT,
                                                 "MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv"))))
    newcols = ["iat_overlapping_pair_IPS", "iat_geyer_IPS", "iat_first_negative", "iat_block500",
               "mean_Q_first_half", "mean_Q_second_half"]
    for r in rows:
        s = per.get(r["arm_id"], {})
        for c in newcols:
            r[c] = s.get(c, "")
        r["iat_estimator_named"] = "overlapping-pair initial-positive-sequence"
    with open(os.path.join(OUT, "MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    aj = J("MYQBD01_ARM_LEVEL_Q_SUMMARIES.json")
    aj["REPAIRED_IAT_PANEL"] = {"BRANCHES": a2["BRANCHES"], "PER_ARM": a2["PER_ARM"],
                                "HEAVY_TAIL_WITNESS": a2["HEAVY_TAIL_WITNESS"],
                                "ESTIMATOR_DEPENDENCE_IS_ITSELF_A_FINDING":
                                    a2["ESTIMATOR_DEPENDENCE_IS_ITSELF_A_FINDING"]}
    W("MYQBD01_ARM_LEVEL_Q_SUMMARIES.json", aj)

    zr = zero_run_report()
    pv = provenance()
    W("MYQBD01_ZERO_RUN_COMPLIANCE.json", zr)
    W("MYQBD01_PROVENANCE_AND_COMMIT_ROLES.json", pv)

    # ---- final disposition, with the mandated terminal vocabulary ----
    fd = J("MYQBD01_FINAL_DISPOSITION.json")
    fd.update({
        "REPAIR_ROUND": "single authorized round applied after the adversarial review",
        "Q_LEDGER_STATUS": "EVENT_EXACT",
        "SCALAR_Q_REDUCTION_STATUS": ops["A5_SCALAR_REDUCTION"]["SCALAR_Q_REDUCTION_STATUS"],
        "TWO_Y_OPERATOR_STATUS":
            "EXECUTABLE_LOCAL_LAW_DERIVED__"
            "FULL_SPATIOTEMPORAL_OPERATOR_NOT_IDENTIFIABLE_FROM_EXISTING_ARCHIVES",
        "MOBILE_DISCOVERY_REGION_STATUS": "NOT_DERIVABLE_FROM_EXISTING_ARCHIVES",
        "DESCENDANT_EXPOSURE_RECOVERABLE": "NO",
        "DESCENDANT_AUDIT_FLAGS": {
            "SOURCE_TRAJECTORY_POSITION_RESOLVED":
                a4["SOURCE_TRAJECTORY_POSITION_RESOLVED"],
            "FULL_LATTICE_ENVIRONMENT_PER_STEP": a4["FULL_LATTICE_ENVIRONMENT_PER_STEP"],
            "HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS":
                a4["HISTORICAL_DESCENDANT_TRAJECTORY_EXISTS"],
            "DESCENDANT_Q_POSITION_RECONSTRUCTIBLE":
                a4["DESCENDANT_Q_POSITION_RECONSTRUCTIBLE"],
            "DERIVED_OVER_ARCHIVES": a4["ARCHIVES_EXAMINED"]},
        "FROZEN_ENVIRONMENT_STATUS": fb["A7_FEEDBACK"]["DOWNSTREAM_BOUND"]["STATUS"],
        "STRUCTURAL_PRECLUSION_PROVED": fb["A8_NON_PRECLUSION"]["STRUCTURAL_PRECLUSION_PROVED"],
        "NO_TARGET_DERIVED_Y_OUTCOME": a10["NO_TARGET_DERIVED_Y_OUTCOME"],
        "TARGET_DERIVED_Y_OUTCOME_READS": a10["TARGET_DERIVED_Y_OUTCOME_READS"],
        "ZERO_RUN": zr["REQUIRED_FINAL_VALUES"],
        "INDEPENDENT_UNIT": "the arm (14 per branch); never the frame",
        "FINAL_DISPOSITION": "EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED",
        "SCIENTIFIC_RUNS_USED": 0,
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "HISTORICAL_WINDOW_STATUS": "NOT_PORTABLE",
        "NEXT_SCIENTIFIC_ELIGIBILITY": "PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01",
        "COMMIT_ROLES": pv["COMMIT_ROLES"],
        "FREEZE": {k: pv["FREEZE"][k] for k in ("FREEZE_FILE_EXISTS",
                                                "INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT")},
        "TOMMY_ACTION_REQUIRED": "NONE"})
    W("MYQBD01_FINAL_DISPOSITION.json", fd)

    # ---- review and repair ledger ----
    rr = J("MYQBD01_REVIEW_AND_REPAIR.json")
    rr["SEAL_REVIEW"] = {
        "REVIEW_ROOT": "/home/claude/MYQBD01/review/ (read-only; preserved by hash)",
        "FILES": {f: subprocess.run(("sha256sum",
                                     "/home/claude/edl/MYQBD01/review/" + f),
                                    capture_output=True, text=True).stdout.split()[0]
                  for f in ("MYQBD01_ADVERSARIAL_REVIEW.md",
                            "MYQBD01_ADVERSARIAL_REVIEW.json")},
        "VERDICT": "CANDIDATE_DISPOSITION_SUPPORTED",
        "COUNTS": {"LOAD_BEARING": 0, "SUBSTANTIVE": 15, "COSMETIC": 4, "ATTACKS_REFUTED": 10},
        "REVIEWS_OF_MYQBD01_OVERALL": 2,
        "SECOND_REVIEW_FORBIDDEN_AND_NOT_RUN": True}
    rr["SEAL_REPAIR"] = {
        "ROUNDS": 1, "COMMITS": 1,
        "ADJUDICATION_TALLY": adj["TALLY"],
        "REPAIRED_ATTACKS": ["A1", "A2", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A12"],
        "ARTEFACTS_REGENERATED": sorted(os.listdir(OUT)),
        "DISPOSITION_CHANGED": False}
    W("MYQBD01_REVIEW_AND_REPAIR.json", rr)

    W("MYQBD01_REPAIR_ZERO_RUN_WITNESS.json", GUARD.report())
    print("zero-run  : original=%s  static=%s  final-guards=%s  all-zero=%s"
          % (zr["ORIGINAL_RUNTIME_SENTINEL_COVERAGE"]["STATUS"],
             zr["RETROSPECTIVE_STATIC_ZERO_RUN_PROOF"]["STATUS"],
             zr["FINAL_REPAIR_RUNTIME_GUARDS"]["STATUS"], zr["ALL_REQUIRED_ZERO"]))
    print("guard     : %d world ctors, %d scheduler steps, %d/4 seeding entry points"
          % (len(GUARD.report()["PATCH_COVERAGE"]["world_constructors"]),
             len(GUARD.report()["PATCH_COVERAGE"]["scheduler_steps"]),
             GUARD.report()["PATCH_COVERAGE"]["seeding_entry_points_count"]))
    print("freeze    : FREEZE_FILE_EXISTS=%s  INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT=%s"
          % (pv["FREEZE"]["FREEZE_FILE_EXISTS"],
             pv["FREEZE"]["INDEPENDENT_PRE_OUTCOME_FREEZE_COMMIT"]))
    print("disposition:", fd["FINAL_DISPOSITION"])
    print("two-Y     :", fd["TWO_Y_OPERATOR_STATUS"])
    print("scalar    :", fd["SCALAR_Q_REDUCTION_STATUS"])


if __name__ == "__main__":
    main()
