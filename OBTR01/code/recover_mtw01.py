"""OBTR01 §4 (addendum) — recover the MTW01 artefacts, which are ABSENT from the delivered
repository, and verify them against digests that were frozen before this mission began.

The chain has to be stated precisely, because the whole use of these files depends on it:

  * `MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md` §C-2 is INSIDE the delivered repository. It
    records `MTW01/out/_window.json` with sha256 `3a1b7ae5...216342` and names commit `85ba2d8`.
  * `MCM01/out/MCM01_FINAL_REPORT.md` independently names the same commit.
  * Neither file is modified here, and neither was written by this mission.

So the digest is a PRE-EXISTING commitment. A file found outside the repository that reproduces
it bit for bit cannot have been fabricated to fit, and is admissible as a historical source.

What these files may be used for is limited on purpose: they reconstruct the historical
QUESTION (§5, §13). They never supply a threshold, a margin, a prediction or a disposition for
OBTR01. Every quantity OBTR01 asserts is rederived from the qualified LawSpec.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess

SRC = "/home/claude/MTW01"
SUMS = "/home/claude/MTW01_SHA256SUMS"
BUNDLE = "/home/claude/MTW01_gen2_branch.bundle"
DST = "/home/claude/OBTR01/verify/mtw01"
WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    # ---------------------------------------------------------------- the frozen commitment
    corr = open(f"{WC}/MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md").read()
    rep = open(f"{WC}/MCM01/out/MCM01_FINAL_REPORT.md").read()
    committed_prefix, committed_suffix = "3a1b7ae5", "216342"
    commitment_present = (committed_prefix in corr and committed_suffix in corr)
    commit_in_corr = "85ba2d8" in corr
    commit_in_report = "85ba2d8" in rep
    mtw01_dir_in_repo = os.path.isdir(f"{WC}/MTW01")

    # ---------------------------------------------------------------- verify every file
    declared = {}
    for line in open(SUMS):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        h, _, name = line.partition("  ")
        declared[name.strip()] = h.strip()

    results, mismatched, absent = {}, [], []
    for name, want in sorted(declared.items()):
        p = os.path.join(SRC, name) if not name.startswith("MTW01_") else \
            os.path.join("/home/claude", name)
        if not os.path.exists(p):
            absent.append(name)
            continue
        got = sha256(p)
        results[name] = {"recorded": want, "actual": got, "match": got == want}
        if got != want:
            mismatched.append(name)

    window_digest = results.get("out/_window.json", {}).get("actual")
    window_matches_C2 = bool(window_digest
                             and window_digest.startswith(committed_prefix)
                             and window_digest.endswith(committed_suffix))

    # ---------------------------------------------------------------- the bundle head
    heads = subprocess.run(("git", "bundle", "list-heads", BUNDLE),
                           capture_output=True, text=True).stdout.strip().splitlines()
    head_ids = [h.split()[0] for h in heads if h.strip()]
    head_matches = any(h.startswith("85ba2d8") for h in head_ids)

    # ---------------------------------------------------------------- copy, then re-verify
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(DST, exist_ok=True)
    copied = []
    for name in sorted(declared):
        if name.startswith("MTW01_"):
            continue
        s = os.path.join(SRC, name)
        if not os.path.exists(s):
            continue
        d = os.path.join(DST, name)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        copied.append(name)
    recopy_bad = [n for n in copied if sha256(os.path.join(DST, n)) != declared[n]]

    ok = bool(commitment_present and commit_in_corr and commit_in_report
              and window_matches_C2 and head_matches
              and not mismatched and not absent and not recopy_bad)

    out = {
        "SECTION": "OBTR01 §4 addendum",
        "WHY_THIS_IS_NEEDED": ("MTW01 owns the historical temporal question this mission must "
                               "rederive, and its directory is absent from the delivered "
                               "repository."),
        "MTW01_DIRECTORY_PRESENT_IN_THE_DELIVERED_REPOSITORY": mtw01_dir_in_repo,
        "FROZEN_COMMITMENT": {
            "source": "MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md section C-2, inside the "
                      "delivered repository, written before this mission",
            "digest_prefix_recorded": committed_prefix,
            "digest_suffix_recorded": committed_suffix,
            "commitment_text_present": commitment_present,
            "commit_named_in_the_corrections": commit_in_corr,
            "same_commit_named_independently_in_MCM01_FINAL_REPORT": commit_in_report,
        },
        "WINDOW_JSON": {"sha256_recomputed": window_digest,
                        "REPRODUCES_THE_FROZEN_COMMITMENT": window_matches_C2},
        "BUNDLE": {"path": os.path.basename(BUNDLE), "sha256": sha256(BUNDLE),
                   "heads": heads, "head_ids": head_ids,
                   "HEAD_IS_THE_COMMIT_NAMED_BY_MCM01": head_matches},
        "CHECKSUM_MANIFEST": {"files_declared": len(declared),
                              "files_verified": len(results),
                              "files_mismatched": mismatched,
                              "files_absent": absent,
                              "ALL_MATCH": not mismatched and not absent},
        "COPY": {"destination": DST, "files_copied": len(copied),
                 "files_whose_digest_changed_after_copy": recopy_bad},
        "ADMISSIBLE_USE": ("reconstruction of the historical question and of the symbols it "
                           "used (OBTR01 §5, §13). NOT admissible as the source of any "
                           "threshold, margin, prediction or disposition of this mission."),
        "STATUS": ("HISTORICAL_ARTEFACTS_RECOVERED_AND_DIGEST_VERIFIED" if ok
                   else "HISTORICAL_ARTEFACTS_NOT_VERIFIED"),
        "PER_FILE": results,
    }
    json.dump(out, open(f"{OUT}/_mtw01_recovery.json", "w"), indent=1)

    print("MTW01 directory inside the delivered repository : %s" % mtw01_dir_in_repo)
    print("frozen commitment present in MCM01 C-2          : %s (commit named in corrections "
          "%s, in final report %s)" % (commitment_present, commit_in_corr, commit_in_report))
    print("_window.json sha256                             : %s" % window_digest)
    print("reproduces the frozen commitment                : %s" % window_matches_C2)
    print("bundle head                                     : %s -> matches 85ba2d8 %s"
          % (head_ids, head_matches))
    print("manifest                                        : %d/%d verified, %d mismatched, "
          "%d absent" % (len(results), len(declared), len(mismatched), len(absent)))
    print("copied to verify/mtw01                          : %d files, %d changed after copy"
          % (len(copied), len(recopy_bad)))
    print("STATUS = %s" % out["STATUS"])


if __name__ == "__main__":
    main()
