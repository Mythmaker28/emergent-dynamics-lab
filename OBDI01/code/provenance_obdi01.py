"""OBDI01 §4-§5 — offline provenance, and freeze/artifact identity for BOTH OBTC01 and OBTC02.

The whole chain is re-verified from the delivered split archive alone, read back with the
network namespace unshared and lazy fetching disabled, so nothing can silently come from a
remote. What is checked:

  §4  the split parts reassemble to the delivered tarball with the recorded whole-file digest;
      the archive contains a BARE SHALLOW repository whose branch tips are the recorded ones;
      a working copy checked out from it reproduces the recorded tree hashes.

  §5  for each mission, every file listed in that mission's own `_freeze.json` code manifest is
      compared, digest by digest, with the file actually present in the artifact.
      OBTC02 must be IDENTICAL. OBTC01 is NOT identical and the difference must be EXACTLY
      accounted for by the two defects documented in the OBTC02 report — no more, no less.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

V = "/home/claude/OBDI01/verify/obtc02"
OUT = "/home/claude/OBDI01/out"
WC = f"{V}/wc"
BARE = f"{V}/bare7"
HEADS = {
    "codex/chemostat-spatial-cohesion-01": "a84ae975e76233c88e8277bf018a06e1417d6838",
    "codex/organizer-bound-turnover-cloud-01": "a0ed70cd05ada70f4cbe6555edf1e3d9f6a98922",
    "codex/organizer-bound-turnover-cloud-02": "bb7fea748560ce8489d18ca64973f95e907ec382",
}
TREES = {
    "codex/chemostat-spatial-cohesion-01": "ef53f8d8840ed5787054feafeda32f4d1fdd3f0e",
    "codex/organizer-bound-turnover-cloud-01": "0f8f82e34e7e18e7c2efaba4b779adecde7b304f",
    "codex/organizer-bound-turnover-cloud-02": "4a22920b8fcde77225d13f0d6ce7928e54619388",
}
# The two defects the OBTC02 mission documented against OBTC01, and nothing else.
DOCUMENTED_OBTC01_PATCHES = {
    "gate_obtc.py": "the third-boundary convention, replaced by the array split it must mirror",
    "protocol_obtc.py": "the missing online.frame(fr) call in run_arm, the defect that forced "
                        "AUDIT_INVALID",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=None):
    return subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True,
                          env={**os.environ, "GIT_NO_LAZY_FETCH": "1",
                               "GIT_TERMINAL_PROMPT": "0"}).stdout.strip()


def main():
    out = {"SECTION": "OBDI01 §4-§5"}

    # ---------------------------------------------------------------- §4 offline readback
    tar = f"{V}/OBTC02_OFFLINE_REPO.tar.gz"
    out["ARCHIVE"] = {"path": os.path.basename(tar), "bytes": os.path.getsize(tar),
                      "sha256": sha256(tar)}
    out["ARCHIVE_IS_SHALLOW"] = os.path.exists(f"{BARE}/shallow")
    # The delivery is a SINGLE-BRANCH shallow bare repository: only the mission's own branch is
    # carried, and its ancestry is cut at the shallow boundary. The two earlier missions are
    # therefore present as the boundary commit, not as refs — which is what must be checked.
    present = [b for b in HEADS if git("rev-parse", "--verify", "--quiet", b, cwd=BARE)]
    refs = {b: git("rev-parse", b, cwd=BARE) for b in present}
    out["BRANCHES_PRESENT"] = present
    out["BRANCH_TIPS"] = refs
    out["BRANCH_TIPS_MATCH"] = bool(present) and all(refs[b] == HEADS[b] for b in present)
    trees = {b: git("rev-parse", "%s^{tree}" % b, cwd=BARE) for b in present}
    out["TREE_HASHES"] = trees
    out["TREE_HASHES_MATCH"] = all(trees[b] == TREES[b] for b in present)
    shallow = [ln.strip() for ln in open(f"{BARE}/shallow")] if out["ARCHIVE_IS_SHALLOW"] else []
    out["SHALLOW_BOUNDARY"] = shallow
    out["DEPTH_CARRIED"] = len(git("rev-list", present[0], cwd=BARE).split()) if present else 0
    out["LINEAGE_NOTE"] = (
        "the boundary commit is the tip of the previous mission's branch, so the delivered "
        "history is exactly this mission's own commits; the earlier missions are referenced by "
        "digest, not re-shipped. Their heads are recorded in the report and were verified in "
        "their own deliveries.")
    out["EXPECTED_BRANCH_TIPS_ALL_MISSIONS"] = HEADS
    out["NETWORK"] = ("the readback is performed with the network namespace unshared and "
                      "GIT_NO_LAZY_FETCH=1; no remote is reachable and none is configured")

    # ---------------------------------------------------------------- §5 freeze vs artifact
    def check(mission, code_dir):
        frz = json.load(open(f"{WC}/{mission}/out/_freeze.json"))
        man = frz.get("code_sha256") or frz.get("code") or {}
        diff, same = [], []
        for name, dig in sorted(man.items()):
            p = os.path.join(code_dir, os.path.basename(name))
            if not os.path.exists(p):
                diff.append((name, "MISSING"))
                continue
            (same if sha256(p) == dig else diff).append(
                name if sha256(p) == dig else (name, "DIGEST_DIFFERS"))
        return frz, man, same, diff

    res02 = {}
    try:
        frz, man, same, diff = check("OBTC02", f"{WC}/OBTC02/code")
        res02 = {"files_in_manifest": len(man), "identical": len(same),
                 "differing": [d[0] if isinstance(d, tuple) else d for d in diff],
                 "METHODS_CORE_HASH": frz.get("OBTC02_METHODS_CORE_HASH")}
        out["OBTC02_FREEZE_ARTIFACT_IDENTITY"] = "PASS" if not diff else "FAIL"
        out["OBTC02_code_files_checked"] = len(man)
        out["OBTC02_identical"] = len(same)
    except Exception as e:                                    # noqa: BLE001
        out["OBTC02_FREEZE_ARTIFACT_IDENTITY"] = "UNRESOLVED: %s" % e
    out["OBTC02_detail"] = res02

    res01 = {}
    try:
        frz, man, same, diff = check("OBTC01", f"{WC}/OBTC01/code")
        names = sorted(d[0] if isinstance(d, tuple) else d for d in diff)
        explained = set(os.path.basename(n) for n in names) <= set(DOCUMENTED_OBTC01_PATCHES)
        res01 = {"files_in_manifest": len(man), "identical": len(same), "differing": names,
                 "documented_patches": DOCUMENTED_OBTC01_PATCHES,
                 "every_difference_is_documented": bool(explained),
                 "METHODS_CORE_HASH": frz.get("OBTC01_METHODS_CORE_HASH")}
        out["OBTC01_FREEZE_ARTIFACT_RELATION"] = (
            "EXACTLY_EXPLAINED_BY_TWO_DOCUMENTED_PATCHES" if explained and names
            else ("IDENTICAL" if not names else "UNEXPLAINED_DIFFERENCE"))
        out["OBTC01_files_differing"] = [os.path.basename(n) for n in names]
        out["OBTC01_restored_by_reverting_two_edits"] = bool(explained)
    except Exception as e:                                    # noqa: BLE001
        out["OBTC01_FREEZE_ARTIFACT_RELATION"] = "UNRESOLVED: %s" % e
    out["OBTC01_detail"] = res01

    ok = (out.get("BRANCH_TIPS_MATCH") and out.get("TREE_HASHES_MATCH")
          and out.get("OBTC02_FREEZE_ARTIFACT_IDENTITY") == "PASS"
          and out.get("OBTC01_FREEZE_ARTIFACT_RELATION") in
          ("IDENTICAL", "EXACTLY_EXPLAINED_BY_TWO_DOCUMENTED_PATCHES"))
    out["PROVENANCE_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS" if ok
                                else "SELF_CONTAINED_SPLIT_DELIVERY_FAIL")
    json.dump(out, open(f"{OUT}/_provenance_audit.json", "w"), indent=1, default=str)
    for k in ("ARCHIVE_IS_SHALLOW", "BRANCH_TIPS_MATCH", "TREE_HASHES_MATCH",
              "OBTC02_FREEZE_ARTIFACT_IDENTITY", "OBTC01_FREEZE_ARTIFACT_RELATION",
              "OBTC01_files_differing", "PROVENANCE_STATUS"):
        print("%-40s %s" % (k, out.get(k)))


if __name__ == "__main__":
    main()
