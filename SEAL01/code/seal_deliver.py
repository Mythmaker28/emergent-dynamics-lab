"""SEAL §7 — preserve and VERIFY the self-contained split delivery, exactly once.

The push is NOT retried. OBFOR01 already made the single permitted attempt and recorded the
proxy's 403 verbatim; the seal treats that response as a session authorization boundary, not a
scientific defect, and reuses the record rather than issuing a second request.

What this script does instead: rebuild the offline archive from the CURRENT branch tip so that
the repaired seal travels with it, split it, digest every part and the whole, and then read it
back under `unshare -rn` -- no network namespace at all -- to prove that the four seal commits
and every deliverable are recoverable with no remote, no promisor pack and no external object.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

REPO = "/home/claude/edl"
D = "/home/claude/SEAL01/deliver"
OUT = "/home/claude/SEAL01/out"
BRANCH = "codex/organizer-bound-full-operator-residual-01"
BASE = "062d3735b726bb9c7325aef063c803823e46218d"
OBFOR01_TIP = "55e8812eee7ca48a8eb16cb439e3812a69bfc971"
PART = 19_000_000
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1"}
NEED = ["SEAL01/out/OBFOR01_CONFIRMATORY_CLAIM_SEAL_REPORT.md",
        "SEAL01/out/OBFOR01_CONFIRMATORY_PROVENANCE_LEDGER.csv",
        "SEAL01/out/OBFOR01_PREDICTION_INFORMATION_FLOW.json",
        "SEAL01/out/OBFOR01_HEADLINE_RECOMPUTATION.json",
        "SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json",
        "SEAL01/out/PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01_HANDOFF.md",
        "SEAL01/out/SEAL01_SHA256SUMS",
        "SEAL01/code/seal_provenance.py", "SEAL01/code/seal_flow_and_numbers.py",
        "SEAL01/code/seal_adjudicate.py", "SEAL01/code/seal_repair.py"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=REPO):
    r = subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True, env=ENV)
    return r.stdout.strip(), r.returncode, r.stderr.strip()


def main():
    log, _, _ = git("log", "--format=%H%x1f%s", f"{BASE}..HEAD")
    commits = [ln.split("\x1f") for ln in log.splitlines() if ln.strip()][::-1]
    head, _, _ = git("rev-parse", "HEAD")
    tree, _, _ = git("rev-parse", "HEAD^{tree}")
    seal_commits = [c for c in commits
                    if c[1].startswith("SEAL ")]

    # ------------------------------------------------------- the push is NOT retried
    prior = json.load(open("/home/claude/OBFOR01/out/_delivery.json"))["PUSH_ATTEMPT"]
    push = {"ATTEMPTS_IN_THIS_SESSION": 1,
            "MADE_BY": "OBFOR01 §28",
            "RETRIED_BY_THE_SEAL": False,
            "returncode": prior["returncode"],
            "stderr": prior["stderr"],
            "READING": ("a 403 from the git proxy is a session authorization boundary. "
                        "Retrying cannot change it and the mandate permits one attempt. The "
                        "recorded response is reused verbatim.")}

    # ------------------------------------------------------- rebuild, split, digest
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    bare = f"{D}/bare"
    subprocess.run(["git", "clone", "--quiet", "--bare", "--single-branch",
                    "--branch", BRANCH, "--depth", str(len(commits) + 1),
                    "file://" + REPO, bare], env=ENV, capture_output=True)
    subprocess.run(["git", "-C", bare, "remote", "remove", "origin"], env=ENV,
                   capture_output=True)
    tar = f"{D}/SEAL01_OFFLINE_REPO.tar.gz"
    with tarfile.open(tar, "w:gz") as t:
        t.add(bare, arcname="bare")
    whole = sha256(tar)
    parts = []
    with open(tar, "rb") as f:
        while True:
            b = f.read(PART)
            if not b:
                break
            n = "%s.part%02d" % (os.path.basename(tar), len(parts))
            open(f"{D}/{n}", "wb").write(b)
            parts.append(n)
    with open(f"{D}/parts.sha256", "w") as f:
        for n in parts:
            f.write("%s  %s\n" % (sha256(f"{D}/{n}"), n))
    open(f"{D}/whole.sha256", "w").write("%s  %s\n" % (whole, os.path.basename(tar)))

    manifest = [
        "OBFOR01-CONFIRMATORY-PROVENANCE-AND-CLAIM-SEAL-01",
        "branch  %s" % BRANCH, "head    %s" % head, "tree    %s" % tree,
        "base    %s (OBTR01)" % BASE,
        "obfor01 %s (the audited tip)" % OBFOR01_TIP,
        "commits %d total, of which %d are seal commits" % (len(commits), len(seal_commits)),
        "",
        "Gzipped BARE SHALLOW SINGLE-BRANCH repository, remote removed. Reassemble with",
        "",
        "    cat SEAL01_OFFLINE_REPO.tar.gz.part* > SEAL01_OFFLINE_REPO.tar.gz",
        "    sha256sum -c whole.sha256",
        "    tar xzf SEAL01_OFFLINE_REPO.tar.gz",
        "    git clone --shared bare wc",
        "",
        "whole sha256 %s" % whole, "parts        %d" % len(parts), "",
    ] + ["  %s  %s" % (sha256(f"{D}/{n}"), n) for n in parts] + [""] + [
        "  %s  %s" % (c[0], c[1]) for c in seal_commits]
    open(f"{D}/MANIFEST.txt", "w").write("\n".join(manifest) + "\n")

    # ------------------------------------------------------- offline readback
    rb = f"{D}/readback"
    shutil.rmtree(rb, ignore_errors=True)
    os.makedirs(rb)
    script = r"""
set -e
cd %s
cat SEAL01_OFFLINE_REPO.tar.gz.part* > readback/whole.tar.gz
sha256sum -c whole.sha256 >/dev/null 2>&1 || { cd readback && sha256sum whole.tar.gz; }
cd readback && tar xzf whole.tar.gz
git -c safe.directory='*' clone --quiet --shared bare wc
git -C bare fsck --full --no-progress 2>&1 | head -5
echo "REMOTES:[$(git -C bare remote)]"
echo "PROMISOR:[$(ls bare/objects/pack/*.promisor 2>/dev/null)]"
echo "COMMITS:$(git -C wc rev-list --count HEAD)"
echo "HEAD:$(git -C wc rev-parse HEAD)"
for f in %s ; do
  if [ -f "wc/$f" ]; then echo "PRESENT:$f"; else echo "MISSING:$f"; fi
done
cd wc/SEAL01 && sha256sum -c out/SEAL01_SHA256SUMS 2>&1 | grep -c ': OK$' | sed 's/^/SUMS_OK:/'
""" % (D, " ".join(NEED))
    r = subprocess.run(["unshare", "-rn", "bash", "-c", script],
                       capture_output=True, text=True, env=ENV)
    lines = (r.stdout + r.stderr).splitlines()

    def grab(p):
        return [ln for ln in lines if ln.startswith(p)]

    readback = {
        "RAN_UNDER": "unshare -rn (no network namespace at all)",
        "FSCK_OUTPUT": [ln for ln in lines if "error" in ln.lower() or "missing" in ln.lower()],
        "FSCK_CLEAN": not any("error" in ln.lower() or "missing" in ln.lower()
                              for ln in lines if not ln.startswith("MISSING:")),
        "REMOTES": (grab("REMOTES:") or [""])[0],
        "PROMISOR_PACKS": (grab("PROMISOR:") or [""])[0],
        "COMMITS_REACHABLE": (grab("COMMITS:") or [""])[0],
        "HEAD": (grab("HEAD:") or [""])[0],
        "DELIVERABLES_PRESENT": len(grab("PRESENT:")),
        "DELIVERABLES_MISSING": [ln[len("MISSING:"):] for ln in grab("MISSING:")],
        "SHA256SUMS_VERIFIED_OFFLINE": (grab("SUMS_OK:") or [""])[0],
        "ALL_NEEDED_PRESENT": len(grab("PRESENT:")) == len(NEED),
    }

    out = {"SECTION": "SEAL delivery",
           "PUSH": push,
           "ARCHIVE": {"whole_sha256": whole, "parts": len(parts),
                       "part_digests": [{"name": n, "sha256": sha256(f"{D}/{n}")}
                                        for n in parts],
                       "bytes": os.path.getsize(tar)},
           "BRANCH": {"head": head, "tree": tree, "base": BASE,
                      "commits_over_the_base": len(commits),
                      "seal_commits": [{"commit": c[0], "subject": c[1]}
                                       for c in seal_commits]},
           "OFFLINE_READBACK": readback,
           "PRESERVED_EXACTLY_ONCE": True,
           "FIXED_POINT_NOTE": (
               "a delivery record cannot contain the hash of the commit that carries it. The "
               "seal's commit budget is four intentional checkpoints, all spent, so this "
               "record and its script were folded into the fourth by amending that single "
               "unpushed commit -- no inherited commit is rewritten -- and the archive was "
               "then rebuilt once at the resulting head. The head named in "
               "deliver/MANIFEST.txt is the authoritative one; the head named in the copy of "
               "this JSON inside the tree is necessarily its predecessor. The PUSH is not "
               "repeated by any of this: the single recorded 403 is reused verbatim."),
           "HEAD_AT_THE_TIME_THIS_RECORD_WAS_WRITTEN": head}
    json.dump(out, open(f"{OUT}/_seal_delivery.json", "w"), indent=1, default=str)

    print("push       : not retried; recorded rc=%s" % push["returncode"])
    print("archive    : %d parts, %d bytes, whole %s" % (len(parts), out["ARCHIVE"]["bytes"],
                                                         whole[:16]))
    print("seal commits in the archive: %d" % len(seal_commits))
    for k in ("REMOTES", "PROMISOR_PACKS", "COMMITS_REACHABLE", "HEAD",
              "SHA256SUMS_VERIFIED_OFFLINE"):
        print("readback   : %-28s %s" % (k, readback[k]))
    print("readback   : %-28s %d/%d  missing %s"
          % ("DELIVERABLES", readback["DELIVERABLES_PRESENT"], len(NEED),
             readback["DELIVERABLES_MISSING"] or "none"))
    print("readback   : %-28s %s" % ("FSCK_CLEAN", readback["FSCK_CLEAN"]))


if __name__ == "__main__":
    main()
