"""FLCR01 §1 — parent binding and the reproducibility ledger."""
from __future__ import annotations
import glob, hashlib, json, os, subprocess
REPO = "/home/claude/edl"; OUT = f"{REPO}/FLCR01/out"; RAW = "/home/claude/PQEC01/raw"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def git(*a): return subprocess.run(("git",)+a, cwd=REPO, capture_output=True, text=True).stdout.strip()
def main():
    os.makedirs(OUT, exist_ok=True)
    tip = git("rev-parse", "codex/prospective-q-environment-calibration-01")
    man = json.load(open(f"{REPO}/PQEC01/out/PQEC01_RAW_MANIFEST.json"))
    bad = [r["file"] for r in man["ARCHIVES"] if sha(os.path.join(RAW, r["file"])) != r["sha256"]]
    binding = {
        "SECTION": "FLCR01 §1 parent binding",
        "PARENT_PROGRAM": "PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01",
        "PARENT_BRANCH": "codex/prospective-q-environment-calibration-01",
        "PARENT_TIP_FULL": tip,
        "RESOLVED_NOT_TRUSTED": {"method": "git rev-parse on the parent branch",
                                 "matches_C5_recorded_tip": tip == "80735ad5e9775db051954ca4d05e258ee4fdf36a"},
        "THIS_BRANCH": "codex/founder-versus-lineage-continuity-reconciliation-01",
        "PQEC01_COMMITS": [{"sha": s.split()[0], "subject": " ".join(s.split()[1:])}
                           for s in git("log", "--format=%h %s",
                                        "86291212955d4a4816efc1ebd671fbd234bf574c..%s" % tip).splitlines()],
        "RAW_ARCHIVES": {"n": len(man["ARCHIVES"]), "all_checksums_match": len(bad) == 0,
                         "mismatches": bad, "total_bytes": man["TOTAL_BYTES"]},
        "REVIEW_BOUND": {f: sha(f"{REPO}/PQEC01/review/{f}") for f in
                         ("PQEC01_ADVERSARIAL_REVIEW.md", "PQEC01_ADVERSARIAL_REVIEW.json")},
        "PRESERVED_STATUS_DISTINCTION": {
            "PQEC01_RAW_EXPERIMENT_STATUS": "VALID_DEVELOPMENTAL_CALIBRATION_DATA",
            "PQEC01_PROSPECTIVE_CONFIRMATORY_STATUS": "NOT_ESTABLISHED",
            "PQEC01_OBSERVER_PHYSICS_STATUS": "INERTNESS_CONFIRMED",
            "PQEC01_DESCENDANT_DATA_STATUS": "REAL_AND_EVENT_ALIGNED",
            "PQEC01_OPERATOR_IDENTIFICATION_STATUS": "NOT_CONFIRMED",
            "STATEMENT": ("the 128 worlds are NOT discarded because the prospective chain "
                          "failed, and they are NOT presented as confirmatory because the "
                          "analysis and provenance were not completely frozen before outcomes. "
                          "They are valid developmental calibration data and nothing more.")},
        "NEW_SCIENTIFIC_RUNS": 0,
        "TOMMY_ACTION_REQUIRED": "NONE"}
    json.dump(binding, open(f"{OUT}/FLCR01_PARENT_BINDING.json", "w"), indent=1, default=str)
    # ---- reproducibility ledger: can every final JSON be regenerated from committed code? ----
    prod = {"PQEC01_REVIEW_CORRECTION_ADDENDUM.json": "FLCR01/code/flcr01_correct.py",
            "FLCR01_PARENT_BINDING.json": "FLCR01/code/flcr01_bind.py",
            "FLCR01_FOUNDER_CONTRADICTION.json": "FLCR01/code/flcr01_science.py",
            "FLCR01_STATE_OPERATOR.json": "FLCR01/code/flcr01_science.py",
            "FLCR01_CRITERION_MATRIX.json": "FLCR01/code/flcr01_science.py",
            "FLCR01_LINEAGE_REGIONS.json": "FLCR01/code/flcr01_science.py"}
    ledger = {
        "SECTION": "PQEC01 + FLCR01 reproducibility ledger",
        "EVERY_FLCR01_JSON_IS_PRODUCED_BY_COMMITTED_CODE": prod,
        "NO_HAND_EDITED_BLOCKS_IN_FLCR01": True,
        "PQEC01_HAND_EDIT_ACKNOWLEDGED": {
            "file": "PQEC01/out/PQEC01_FINAL_DISPOSITION.json",
            "what": ("four blocks were added by hand in C4 (MISSING_OBJECT_NAMED, "
                     "EMPTY_REGION_IS_PREREGISTERED, PHASE_A_DESIGN_DISPERSION_MISS, "
                     "POST_HOC_DESCRIPTIVE_X_ESTABLISHMENT) that the sealed code did not write"),
            "status_now": ("PQEC01's repair round moved the disposition-bearing content into "
                           "pqec01_repair.py; FLCR01 does not hand-edit any output, and this "
                           "addendum supersedes the hand-added narrative blocks"),
            "HISTORY_NOT_REWRITTEN": True},
        "PQEC01_SOURCE_HASHES": {os.path.basename(p): sha(p)
                                 for p in sorted(glob.glob(f"{REPO}/PQEC01/code/*.py"))},
        "FLCR01_SOURCE_HASHES": {os.path.basename(p): sha(p)
                                 for p in sorted(glob.glob(f"{REPO}/FLCR01/code/*.py"))},
        "PRE_FIX_ANALYSER_RECOVERED_FROM": "git blob at commit 7d97205",
        "RAW_DATA_UNCHANGED_SINCE_PQEC01": len(bad) == 0}
    json.dump(ledger, open(f"{OUT}/PQEC01_REPRODUCIBILITY_LEDGER.json", "w"), indent=1, default=str)
    print("parent tip", tip, "| matches C5:", binding["RESOLVED_NOT_TRUSTED"]["matches_C5_recorded_tip"])
    print("raw archives", binding["RAW_ARCHIVES"]["n"], "checksums all match:",
          binding["RAW_ARCHIVES"]["all_checksums_match"])
if __name__ == "__main__": main()
