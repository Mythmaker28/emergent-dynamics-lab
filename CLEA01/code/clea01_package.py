"""CLEA01 — the Windows durability package, built by committed code.

This exists because the checker's finding against me was that seven CLEA01 artefacts had no
committed generating script — the OMLDCT01 failure mode recurring in a mission run by the person
who wrote the module built to prevent it. That finding stands for those seven. It does not get to
recur for the durability step, so the durability step is this file.

What it builds, all from git objects and never from the working tree:

  CLEA01_FINAL_INCREMENT.bundle   exactly BASE..TIP for the branch. BASE is the OMLDCT02 terminal
                                  tip, which is the ref carried by OMLDCT02_FINAL_FULL.bundle
                                  already on Windows. The increment is therefore restorable there
                                  with no network and no container.
  CLEA01_FINAL_EVIDENCE_CAPSULE.tar        `git archive HEAD CLEA01` — the tree AS COMMITTED.
  CLEA01_FINAL_SHA256SUMS         plain `sha256sum` format, verifiable by any tool.
  CLEA01_FINAL_EXTERNAL_MANIFEST.json  what the package is, digested by the parent's canonical rule.

A full bundle is NOT built. The repository pack is ~571 MiB (the TLMR01 archives), far past the
bridge's per-file ceiling. The increment plus the already-durable OMLDCT02 full bundle covers the
same history; the manifest names that prerequisite explicitly rather than leaving it implied.
"""
from __future__ import annotations
import datetime as _dt
import json, os, subprocess, sys

REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
OUT = os.environ.get("CLEA01_PKG", "/home/claude/clea01_pkg")
BASE = "84000ff3a67fd4e550934313019decda05219da0"      # OMLDCT02 C5, the parent's terminal tip

sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H                             # noqa: E402


def git(*a):
    return subprocess.run(("git", "-C", REPO) + a, capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    br = git("rev-parse", "--abbrev-ref", "HEAD")
    tip = git("rev-parse", "HEAD")
    commits = git("rev-list", "--reverse", f"{BASE}..{tip}").split()
    assert len(commits) == 5, f"CLEA01 closes at five commits, found {len(commits)}"

    inc = f"{OUT}/CLEA01_FINAL_INCREMENT.bundle"
    cap = f"{OUT}/CLEA01_FINAL_EVIDENCE_CAPSULE.tar"
    for p in (inc, cap):
        if os.path.exists(p):
            os.remove(p)
    git("bundle", "create", inc, f"{BASE}..{tip}", br)
    git("archive", "--format=tar", "-o", cap, "HEAD", "CLEA01")
    subprocess.run(("git", "-C", REPO, "bundle", "verify", inc), check=True,
                   capture_output=True, text=True)

    disp = json.load(open(f"{REPO}/CLEA01/out/CLEA01_FINAL_DISPOSITION.json"))
    gates = json.load(open(f"{REPO}/CLEA01/out/CLEA01_STRUCTURAL_GATES.json"))
    ver = json.load(open(f"{REPO}/CLEA01/out/CLEA01_DIGEST_VERIFICATION.json"))
    adj = json.load(open(f"{REPO}/CLEA01/out/CLEA01_CHECKER_ADJUDICATION.json"))

    for f in ("CLEA01_FINAL_REPORT.md", "CLEA01_FINAL_DISPOSITION.json"):
        with open(f"{OUT}/{f}", "wb") as w:
            w.write(open(f"{REPO}/CLEA01/out/{f}", "rb").read())
    with open(f"{OUT}/CLEA01_CHECKER_RAW.txt", "wb") as w:
        w.write(open(f"{REPO}/CLEA01/review/CLEA01_CHECKER_RAW.txt", "rb").read())

    package = ["CLEA01_FINAL_INCREMENT.bundle", "CLEA01_FINAL_EVIDENCE_CAPSULE.tar",
               "CLEA01_FINAL_REPORT.md", "CLEA01_FINAL_DISPOSITION.json",
               "CLEA01_CHECKER_RAW.txt"]
    sums = {f: H.file_sha256(f"{OUT}/{f}") for f in package}

    man = {
        "MISSION": "CLEA01",
        "SECTION": "final external manifest",
        "GENERATED_UTC": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "FINAL_DISPOSITION": disp["FINAL_DISPOSITION"],
        "NEW_SCIENTIFIC_WORLDS_USED": 0,
        "BRANCH": br,
        "TIP": tip,
        "COMMITS": {f"C{i+1}": c for i, c in enumerate(commits)},
        "INTENTIONAL_COMMITS": len(commits),
        "MAX_INTENTIONAL_COMMITS_AUDIT_LAUNCHER": 4,
        "C5_AUTHORISED_BY": "the closure launcher, which mandates seventeen further artefacts and "
                            "sets no commit cap. The audit launcher's cap of four applied to the "
                            "audit phase and C4 recorded NO_C5 under it; that is superseded, not "
                            "contradicted, and the supersession is stated rather than glossed.",
        "BUNDLE_PREREQ": f"{BASE} (the OMLDCT02 C5 terminal tip)",
        "BUNDLE_PREREQ_IS_ALREADY_DURABLE_ON_WINDOWS_AS":
            "OMLDCT02/OMLDCT02_FINAL_FULL.bundle",
        "CLEA01_FINAL_FULL_BUNDLE": "NOT_PRODUCED",
        "NO_FULL_BUNDLE_AND_WHY":
            "the closure launcher names CLEA01_FINAL_FULL.bundle. It cannot be produced through "
            "this session's only durable channel and the reason is measured, not asserted: the "
            "repository pack is 571.43 MiB (the TLMR01 scientific archives dominate it), the device "
            "bridge caps a committed file at 20 MB and a call at 100 MB, and a 124 MiB stage in the "
            "other direction already failed twice with a wall-clock timeout. A full bundle would "
            "therefore exist only inside a container that is discarded, which is the opposite of "
            "durability. What replaces it is exact rather than approximate: the increment below, "
            "plus the seven-bundle chain already on Windows, restores the tip byte-for-byte — "
            "verified, not claimed, in CLEA01_DURABILITY_RECORD.json.",
        "RESTORE_PROCEDURE": [
            "git clone OMLDCT02/OMLDCT02_FINAL_FULL.bundle edl",
            "git -C edl fetch ../CLEA01/CLEA01_FINAL_INCREMENT.bundle "
            "'refs/heads/*:refs/heads/*' --force",
            "git -C edl rev-parse " + tip + "   # must resolve",
            "or, without git at all: tar xf CLEA01_FINAL_EVIDENCE_CAPSULE.tar",
        ],
        "PACKAGE": sums,
        "GATES": {g["gate"]: g["VERDICT"] for g in gates["GATES"]},
        "N_GATES_PASS": gates["N_PASS"],
        "N_GATES_FAIL": gates["N_FAIL"],
        "N_GATES_NOT_REACHED": gates["N_NOT_REACHED"],
        "FAILED_GATES": gates["FAILED_GATES"],
        "MODEL_SELECTED": disp["MODEL_SELECTED"],
        "HANDOFFS_WRITTEN": disp["HANDOFFS_WRITTEN"],
        "CAUSAL_EMERGENCE_STATUS": disp["CAUSAL_EMERGENCE_STATUS"],
        "CHECKERS_DISPATCHED": 1,
        "LOAD_BEARING_DEFECT_COUNT": adj.get("LOAD_BEARING_DEFECT_COUNT"),
        "LAUNCHERS_COMMITTED": ["CLEA01/launcher/CLEA01_LAUNCHER_01_AUDIT.txt",
                                "CLEA01/launcher/CLEA01_LAUNCHER_02_CLOSURE.txt"],
        "CHECKER_RETURN_TXT_SHA256": H.file_sha256(
            f"{REPO}/CLEA01/review/CLEA01_CHECKER_RAW.txt"),
        "N_CONTENT_HASHES_CHECKED": ver["N_CHECKED"],
        "ALL_CONTENT_HASHES_REPRODUCE": ver["ALL_CONTENT_HASHES_REPRODUCE"],
        "DECLARED_DEFECT_CARRIED_FORWARD": ver["DECLARED_DEFECT"],
        "DISPOSITION_CONTENT_HASH": disp["DISPOSITION_CONTENT_HASH"],
        "OMLDCT02_STATUS": disp["OMLDCT02_STATUS"],
        "OMLDCT02_PAIRED_STATISTICS": disp["OMLDCT02_PAIRED_STATISTICS"],
        "H3_STATUS": "NOT_TESTED",
        "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED",
        "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED",
        "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS":
            "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
    }
    man["MANIFEST_CONTENT_HASH"] = H.content_digest(man, extra_excluded=("MANIFEST_CONTENT_HASH",))
    with open(f"{OUT}/CLEA01_FINAL_EXTERNAL_MANIFEST.json", "w") as w:
        json.dump(man, w, indent=1)
    sums["CLEA01_FINAL_EXTERNAL_MANIFEST.json"] = H.file_sha256(
        f"{OUT}/CLEA01_FINAL_EXTERNAL_MANIFEST.json")
    with open(f"{OUT}/CLEA01_FINAL_SHA256SUMS", "w", newline="\n") as w:
        for f in package + ["CLEA01_FINAL_EXTERNAL_MANIFEST.json"]:
            w.write(f"{sums[f]}  {f}\n")

    for f in sorted(os.listdir(OUT)):
        print(f"{os.path.getsize(OUT + '/' + f):>9}  {f}")
    print("TIP =", tip)
    print("MANIFEST_CONTENT_HASH =", man["MANIFEST_CONTENT_HASH"])
    return man


if __name__ == "__main__":
    main()
