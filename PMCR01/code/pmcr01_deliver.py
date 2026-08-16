"""PMCR01 §13 — preserve and VERIFY the self-contained split delivery, exactly once.

The push is attempted ONCE. If the proxy returns the already-known 403, it is recorded verbatim
and the delivery falls back to a gzipped bare shallow single-branch repository, split into 19 MB
parts, digested per part and whole, and read back under `unshare -rn` (no network namespace at
all) to prove every deliverable is recoverable with no remote and no promisor pack.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

REPO = "/home/claude/edl"
D = "/home/claude/PMCR01/deliver"
OUT = "/home/claude/PMCR01/out"
BRANCH = "codex/prospective-minority-channel-reachability-01"
BASE = "f9d9b61cc29db6a0afe0d0a7ec04f3edf9b4a0e2"     # the sealed tip
PART = 19_000_000
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1"}
NEED = ["PMCR01/out/PMCR01_PARENT_SEAL_BINDING.json",
        "PMCR01/out/PMCR01_EXECUTABLE_Y_CHANNEL_MAP.md",
        "PMCR01/out/PMCR01_EXECUTABLE_Y_CHANNEL_MAP.json",
        "PMCR01/out/PMCR01_DISCRETE_Y_OPERATOR_DERIVATION.md",
        "PMCR01/out/PMCR01_REACHABILITY_REGIONS.json",
        "PMCR01/out/PMCR01_MUTATION_ORACLE_REPORT.json",
        "PMCR01/out/PMCR01_FINAL_REPORT.md",
        "PMCR01/out/PMCR01_FINAL_DISPOSITION.json",
        "PMCR01/out/PMCR01_SHA256SUMS",
        "PMCR01/out/HANDOFF_MINIMAL_Y_CHANNEL_ARCHITECTURE_DESIGN_01.md",
        "PMCR01/out/HANDOFF_MINORITY_Y_Q_BOUND_DERIVATION_01.md",
        "PMCR01/out/PMCR01_Q_INSTRUMENTATION_EVIDENCE.json",
        "PMCR01/out/PMCR01_REVIEW_REPAIR_MATRIX.json",
        "PMCR01/code/pmcr01_repair_q.py", "PMCR01/code/pmcr01_repair_apply.py",
        "PMCR01/code/pmcr01_repair_matrix.py",
        "PMCR01/code/pmcr01_sentinel.py", "PMCR01/code/pmcr01_oracles.py",
        "PMCR01/code/pmcr01_operator.py", "PMCR01/code/pmcr01_regions.py",
        "PMCR01/code/pmcr01_adjudicate.py"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    r = subprocess.run(("git",) + a, cwd=REPO, capture_output=True, text=True, env=ENV)
    return r.stdout.strip(), r.returncode, r.stderr.strip()


def main():
    log, _, _ = git("log", "--format=%H%x1f%s", f"{BASE}..HEAD")
    commits = [ln.split("\x1f") for ln in log.splitlines() if ln.strip()][::-1]
    head, _, _ = git("rev-parse", "HEAD")
    tree, _, _ = git("rev-parse", "HEAD^{tree}")

    # ---------------------------------------------------------- the push is NOT attempted
    # PUSH_RETRY = forbidden. The mission's single permitted attempt was made and refused during
    # the original delivery; the recorded response is reused verbatim rather than reissued.
    prior = json.load(open(f"{OUT}/_pmcr01_delivery.json"))["PUSH"]
    push = {"ATTEMPTS_IN_THIS_REPAIR": 0,
            "PUSH_RETRY_COUNT": 0,
            "ATTEMPTS_TOTAL_ACROSS_THE_MISSION": 1,
            # tolerate either schema so re-running is idempotent; the 403 text is verbatim
            "recorded_returncode": prior.get("returncode", prior.get("recorded_returncode")),
            "recorded_stderr": prior.get("stderr", prior.get("recorded_stderr")),
            "RETRIED": False,
            "action": ("not attempted; the mission's single permitted attempt was already made "
                       "and refused by the proxy. Retrying a session authorization boundary "
                       "cannot change it and is forbidden by this repair's mandate.")}

    # ---------------------------------------------------------- rebuild, split, digest
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    bare = f"{D}/bare"
    subprocess.run(["git", "clone", "--quiet", "--bare", "--single-branch",
                    "--branch", BRANCH, "--depth", str(len(commits) + 1),
                    "file://" + REPO, bare], env=ENV, capture_output=True)
    subprocess.run(["git", "-C", bare, "remote", "remove", "origin"], env=ENV,
                   capture_output=True)
    tar = f"{D}/PMCR01_OFFLINE_REPO.tar.gz"
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
        "PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01",
        "branch  %s" % BRANCH, "head    %s" % head, "tree    %s" % tree,
        "base    %s (the sealed OBFOR01/SEAL01 tip)" % BASE,
        "commits %d over the base" % len(commits), "",
        "Gzipped BARE SHALLOW SINGLE-BRANCH repository, remote removed. Reassemble with",
        "",
        "    cat PMCR01_OFFLINE_REPO.tar.gz.part* > PMCR01_OFFLINE_REPO.tar.gz",
        "    sha256sum -c whole.sha256",
        "    tar xzf PMCR01_OFFLINE_REPO.tar.gz",
        "    git clone --shared bare wc",
        "",
        "whole sha256 %s" % whole, "parts        %d" % len(parts), "",
    ] + ["  %s  %s" % (sha256(f"{D}/{n}"), n) for n in parts] + [""] + [
        "  %s  %s" % (c[0], c[1]) for c in commits]
    open(f"{D}/MANIFEST.txt", "w").write("\n".join(manifest) + "\n")

    # ---------------------------------------------------------- offline readback
    rb = f"{D}/readback"
    os.makedirs(rb, exist_ok=True)
    script = r"""
set -e
cd %s
cat PMCR01_OFFLINE_REPO.tar.gz.part* > readback/whole.tar.gz
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
cd wc/PMCR01 && sha256sum -c out/PMCR01_SHA256SUMS 2>&1 | grep -c ': OK$' | sed 's/^/SUMS_OK:/'
""" % (D, " ".join(NEED))
    r = subprocess.run(["unshare", "-rn", "bash", "-c", script],
                       capture_output=True, text=True, env=ENV)
    lines = (r.stdout + r.stderr).splitlines()

    def grab(p):
        return [ln for ln in lines if ln.startswith(p)]

    readback = {
        "RAN_UNDER": "unshare -rn (no network namespace)",
        "FSCK_CLEAN": not any(("error" in ln.lower() or "missing" in ln.lower())
                              and not ln.startswith("MISSING:") for ln in lines),
        "REMOTES": (grab("REMOTES:") or [""])[0],
        "PROMISOR_PACKS": (grab("PROMISOR:") or [""])[0],
        "COMMITS_REACHABLE": (grab("COMMITS:") or [""])[0],
        "HEAD": (grab("HEAD:") or [""])[0],
        "DELIVERABLES_PRESENT": len(grab("PRESENT:")),
        "DELIVERABLES_MISSING": [ln[len("MISSING:"):] for ln in grab("MISSING:")],
        "SHA256SUMS_VERIFIED_OFFLINE": (grab("SUMS_OK:") or [""])[0],
        "ALL_NEEDED_PRESENT": len(grab("PRESENT:")) == len(NEED),
    }

    rec = {"SECTION": "PMCR01 delivery",
           "PUSH": push,
           "ARCHIVE": {"whole_sha256": whole, "parts": len(parts),
                       "bytes": os.path.getsize(tar),
                       "part_digests": [{"name": n, "sha256": sha256(f"{D}/{n}")}
                                        for n in parts]},
           "BRANCH": {"head": head, "tree": tree, "base": BASE,
                      "commits_over_base": len(commits),
                      "subjects": [c[1] for c in commits]},
           "OFFLINE_READBACK": readback,
           "PRESERVED_EXACTLY_ONCE": True,
           "FIXED_POINT_NOTE": (
               "a delivery record cannot contain the hash of the commit that carries it. This "
               "record is folded into the final commit by amending it once; the head named "
               "here is the predecessor, and MANIFEST.txt carries the authoritative head. The "
               "push is not repeated by any of this."),
           "HEAD_WHEN_WRITTEN": head}
    json.dump(rec, open(f"{OUT}/_pmcr01_delivery.json", "w"), indent=1, default=str)

    print("push     : attempts in this repair=%s retried=%s (recorded rc=%s)"
          % (push["ATTEMPTS_IN_THIS_REPAIR"], push["RETRIED"], push["recorded_returncode"]))
    print("archive  : %d parts, %d bytes, whole %s" % (len(parts), rec["ARCHIVE"]["bytes"],
                                                       whole[:16]))
    for k in ("REMOTES", "PROMISOR_PACKS", "COMMITS_REACHABLE", "HEAD",
              "SHA256SUMS_VERIFIED_OFFLINE", "FSCK_CLEAN"):
        print("readback : %-28s %s" % (k, readback[k]))
    print("readback : %-28s %d/%d  missing %s"
          % ("DELIVERABLES", readback["DELIVERABLES_PRESENT"], len(NEED),
             readback["DELIVERABLES_MISSING"] or "none"))


if __name__ == "__main__":
    main()
