"""MYQBD01 FINAL SEAL §1 — bind the candidate by bytes.

Resolve the ACTUAL tip (the launcher's reported tip is checked, not trusted), hash the raw
arms, every MYQBD01 source and output, the parent tip, and record the two provenance facts
that must travel into the review verbatim.

No engine. Read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

REPO = "/home/claude/edl"
RAW = "/home/claude/OBFOR01/raw"
OUT = "/home/claude/MYQBD01/seal/out"
REPORTED = "decfda5"
PARENT_TIP = "8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367"


def git(*a, cwd=REPO):
    r = subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    head, _ = git("rev-parse", "HEAD")
    tree, _ = git("rev-parse", "HEAD^{tree}")
    branch, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    reported_full, rc = git("rev-parse", REPORTED)
    _, anc_rc = git("merge-base", "--is-ancestor", reported_full, head)
    after, _ = git("rev-list", "--count", "%s..HEAD" % reported_full)
    dirty, _ = git("status", "--porcelain")
    log, _ = git("log", "--format=%H %ad %s", "--date=iso", "%s..HEAD" % PARENT_TIP)

    # ---- freeze chronology: was the master freeze committed BEFORE detailed access? ----
    freeze_commit, _ = git("log", "--format=%H", "-1", "--",
                           "MYQBD01/out/MYQBD01_MASTER_FREEZE.json")
    detail_files = ["MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv",
                    "MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.json",
                    "MYQBD01/out/MYQBD01_TEMPORAL_DEPENDENCE.json",
                    "MYQBD01/out/MYQBD01_DISCOVERY_REGION.json"]
    detail_commits = {p: git("log", "--format=%H", "-1", "--", p)[0] for p in detail_files}
    same = {p: (c == freeze_commit) for p, c in detail_commits.items()}

    # ---- byte inventory ----
    raws = sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
    raw_digest = {f: {"sha256": sha256(os.path.join(RAW, f)),
                      "bytes": os.path.getsize(os.path.join(RAW, f))} for f in raws}
    code_dir = "/home/claude/MYQBD01/code"
    out_dir = "/home/claude/MYQBD01/out"
    code_digest = {f: sha256(os.path.join(code_dir, f))
                   for f in sorted(os.listdir(code_dir)) if f.endswith(".py")}
    out_digest = {f: sha256(os.path.join(out_dir, f)) for f in sorted(os.listdir(out_dir))}

    # tracked-vs-disk agreement for every MYQBD01 file in the tree
    tracked, _ = git("ls-files", "MYQBD01/")
    tracked = [t for t in tracked.splitlines() if t.strip()]
    mismatch, scratch_div = [], []
    for t in tracked:
        blob = subprocess.run(("git", "show", "HEAD:%s" % t), cwd=REPO,
                              capture_output=True).stdout
        # the AUTHORITATIVE copy is the one inside the repo working tree
        disk = os.path.join(REPO, t)
        if os.path.exists(disk):
            if open(disk, "rb").read() != blob:
                mismatch.append(t)
        else:
            mismatch.append(t + " (ABSENT_IN_REPO_WORKTREE)")
        # the SCRATCH copy (/home/claude/MYQBD01) is where the scripts ran; it is not
        # authoritative, but a divergence must be disclosed rather than silently ignored
        scr = os.path.join("/home/claude", t)
        if not os.path.exists(scr):
            scratch_div.append(t + " (ABSENT_IN_SCRATCH)")
        elif open(scr, "rb").read() != blob:
            scratch_div.append(t + " (DIFFERS_FROM_COMMITTED)")

    # committed checksum manifest, verified against the committed worktree
    sums = subprocess.run(["sha256sum", "-c", "out/MYQBD01_SHA256SUMS"],
                          cwd=os.path.join(REPO, "MYQBD01"), capture_output=True, text=True)
    sums_ok = sum(1 for ln in sums.stdout.splitlines() if ln.endswith(": OK"))
    sums_bad = [ln for ln in sums.stdout.splitlines() if not ln.endswith(": OK")]
    n_sums = len([ln for ln in open(os.path.join(REPO, "MYQBD01/out/MYQBD01_SHA256SUMS"))
                  if ln.strip()])

    # the delivery record names a pre-amend HEAD; is it reachable?
    deliv = json.loads(subprocess.run(("git", "show",
                                       "HEAD:MYQBD01/out/_myqbd01_delivery.json"),
                                      cwd=REPO, capture_output=True, text=True).stdout)
    hww = deliv.get("HEAD_WHEN_WRITTEN", "")
    hww_reachable = git("merge-base", "--is-ancestor", hww, head)[1] == 0 if hww else None

    rec = {
        "SECTION": "MYQBD01 FINAL SEAL §1 — candidate bound by bytes",
        "BRANCH": branch,
        "ACTUAL_TIP": head,
        "TREE": tree,
        "LAUNCHER_REPORTED_TIP": REPORTED,
        "LAUNCHER_REPORTED_TIP_FULL": reported_full,
        "REPORTED_TIP_IS_ANCESTOR_OF_ACTUAL": anc_rc == 0,
        "COMMITS_AFTER_REPORTED_TIP": int(after),
        "REPORTED_TIP_STATUS": ("STALE_BUT_ANCESTOR" if anc_rc == 0 and int(after) > 0
                                else "EXACT" if int(after) == 0 else "DIVERGENT"),
        "PROVENANCE_DISCLOSURE_1": (
            "The launcher's CANDIDATE_REPORTED_TIP = decfda5 is STALE. It is a true ancestor of "
            "the branch head, but %d commit(s) follow it. The candidate actually under review is "
            "%s, which additionally contains MYQBD01's own internal §19 adversarial review and "
            "its three cosmetic repairs. The seal is run against the ACTUAL tip." % (int(after), head)),
        "WORKING_TREE_CLEAN": dirty == "",
        "WORKING_TREE_ENTRIES": dirty.splitlines(),
        "PARENT_TIP": PARENT_TIP,
        "PARENT_TIP_IS_ANCESTOR": git("merge-base", "--is-ancestor", PARENT_TIP, head)[1] == 0,
        "COMMITS_OVER_PARENT": log.splitlines(),
        "FREEZE_CHRONOLOGY": {
            "MASTER_FREEZE_COMMIT": freeze_commit,
            "DETAIL_FILE_COMMITS": detail_commits,
            "FREEZE_COMMITTED_IN_SAME_COMMIT_AS_DETAIL": same,
            "FREEZE_HAS_ITS_OWN_PRIOR_COMMIT": not any(same.values()),
            "PROVENANCE_DISCLOSURE_2": (
                "The master freeze was WRITTEN before the detailed arm/temporal analysis was RUN "
                "(the mission's own execution order), but it was COMMITTED in the same commit as "
                "those detailed outputs. There is therefore NO independent Git checkpoint proving "
                "the freeze predates the detailed access. The freeze's own text already declares "
                "the mission response-informed and developmental and explicitly disclaims "
                "blinding, so no blinding claim rests on this; but the chronology is NOT "
                "cryptographically witnessed and must not be presented as if it were.")},
        "PRIOR_REVIEW_DISCLOSURE_3": (
            "MYQBD01's own §19 already consumed ONE adversarial review inside the candidate "
            "(recorded in MYQBD01_REVIEW_AND_REPAIR.json: concurring, 0 load-bearing defects, 3 "
            "cosmetic defects repaired). The review dispatched by THIS seal is therefore the "
            "SECOND adversarial review of MYQBD01 overall, run under the seal launcher's own "
            "separate budget of MAX_INDEPENDENT_REVIEWS = 1. It is not the first look at this "
            "material and must not be presented as one."),
        "RAW_ARMS": {"count": len(raws), "digests": raw_digest},
        "MYQBD01_SOURCES": code_digest,
        "MYQBD01_OUTPUTS": out_digest,
        "TRACKED_VS_REPO_WORKTREE_MISMATCHES": mismatch,
        "COMMITTED_SHA256SUMS": {"lines": n_sums, "verified_OK": sums_ok,
                                 "failures": sums_bad,
                                 "ALL_VERIFY": sums_ok == n_sums and not sums_bad},
        "SCRATCH_VS_COMMITTED_DIVERGENCE": {
            "entries": scratch_div,
            "NOTE": ("/home/claude/MYQBD01 is the SCRATCH tree the analysis scripts ran in; "
                     "/home/claude/edl/MYQBD01 is the COMMITTED copy and is authoritative. The "
                     "listed entries differ or are absent in scratch. MYQBD01_SHA256SUMS is "
                     "generated at the copy-into-repo step so it never existed in scratch; "
                     "_myqbd01_delivery.json in scratch is a LATER re-run of the delivery "
                     "script (it names the final head) while the committed blob necessarily "
                     "names its own pre-amend predecessor. Neither affects a scientific claim, "
                     "but both are disclosed rather than smoothed over.")},
        "DELIVERY_RECORD_FIXED_POINT": {
            "HEAD_WHEN_WRITTEN_in_committed_blob": hww,
            "IS_REACHABLE_FROM_ACTUAL_TIP": hww_reachable,
            "READING": ("the committed delivery record names %s, which is the ORPHANED "
                        "pre-amend object of the final commit. This is the documented "
                        "fixed-point behaviour (a record cannot contain the hash of the commit "
                        "that carries it); MANIFEST.txt in the offline archive carries the "
                        "authoritative head. It is a self-reference artefact, not a data "
                        "discrepancy." % hww)},
        "BYTES_BOUND": True,
    }
    json.dump(rec, open(os.path.join(OUT, "SEAL01_CANDIDATE_BINDING.json"), "w"),
              indent=1, default=str)
    print("branch            ", branch)
    print("ACTUAL_TIP        ", head)
    print("reported tip      ", REPORTED, "->", reported_full, rec["REPORTED_TIP_STATUS"],
          "(+%d commits)" % int(after))
    print("working tree clean", rec["WORKING_TREE_CLEAN"])
    print("parent ancestor   ", rec["PARENT_TIP_IS_ANCESTOR"])
    print("raw arms          ", len(raws))
    print("sources / outputs ", len(code_digest), "/", len(out_digest))
    print("repo mismatches   ", mismatch or "none")
    print("committed SUMS    ", "%d/%d OK" % (sums_ok, n_sums))
    print("scratch divergence", scratch_div or "none")
    print("delivery HEAD ref ", hww, "reachable:", hww_reachable)
    print("freeze own commit ", rec["FREEZE_CHRONOLOGY"]["FREEZE_HAS_ITS_OWN_PRIOR_COMMIT"])


if __name__ == "__main__":
    main()
