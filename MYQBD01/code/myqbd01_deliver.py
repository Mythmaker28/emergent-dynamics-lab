"""MYQBD01 §21 — self-contained offline delivery. The push is NOT attempted.

Repository authorization is not positively established (the proxy has refused every push across
this program with a 403). Per the mission mandate, this is recorded as
PUSH_NOT_ATTEMPTED__REPOSITORY_AUTHORIZATION_NOT_ESTABLISHED rather than issuing another
knowingly futile request. The delivery falls back to a gzipped bare shallow single-branch
repository, split, digested, and read back under `unshare -rn`.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

REPO = "/home/claude/edl"
D = "/home/claude/MYQBD01/deliver"
OUT = "/home/claude/MYQBD01/out"
BRANCH = "codex/minority-y-q-bound-derivation-01"
BASE = "8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367"     # the repaired PMCR01 tip
PART = 19_000_000
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1"}
NEED = ["MYQBD01/out/MYQBD01_MASTER_FREEZE.md", "MYQBD01/out/MYQBD01_MASTER_FREEZE.json",
        "MYQBD01/out/MYQBD01_PARENT_BINDING.json", "MYQBD01/out/MYQBD01_RAW_DATA_INVENTORY.json",
        "MYQBD01/out/MYQBD01_Q_PHASE_MAP.json",
        "MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv",
        "MYQBD01/out/MYQBD01_ARM_LEVEL_Q_SUMMARIES.json",
        "MYQBD01/out/MYQBD01_TEMPORAL_DEPENDENCE.json", "MYQBD01/out/MYQBD01_ONE_Y_OPERATOR.json",
        "MYQBD01/out/MYQBD01_TWO_Y_OPERATOR.json", "MYQBD01/out/MYQBD01_FEEDBACK_BOUND.json",
        "MYQBD01/out/MYQBD01_MOBILE_ARM_REGIONS.json", "MYQBD01/out/MYQBD01_DISCOVERY_REGION.json",
        "MYQBD01/out/MYQBD01_FINAL_DISPOSITION.json", "MYQBD01/out/MYQBD01_REVIEW_AND_REPAIR.json",
        "MYQBD01/out/MYQBD01_FINAL_REPORT.md",
        "MYQBD01/out/MYQBD01_Q_SEMANTICS_AND_PHASE_REPORT.md",
        "MYQBD01/out/MYQBD01_ENVIRONMENT_OPERATOR_AND_REGION_REPORT.md",
        "MYQBD01/out/HANDOFF_PROSPECTIVE_Q_ENVIRONMENT_CALIBRATION_01.md",
        "MYQBD01/out/MYQBD01_SHA256SUMS"]


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

    push = {"ATTEMPTED": False,
            "STATUS": "PUSH_NOT_ATTEMPTED__REPOSITORY_AUTHORIZATION_NOT_ESTABLISHED",
            "PUSH_RETRY_COUNT": 0,
            "reason": ("repository authorization is not positively established; the proxy has "
                       "refused every push across this program with a 403. Per §21, recording "
                       "this is preferable to another knowingly futile 403.")}

    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    bare = f"{D}/bare"
    subprocess.run(["git", "clone", "--quiet", "--bare", "--single-branch",
                    "--branch", BRANCH, "--depth", str(len(commits) + 1),
                    "file://" + REPO, bare], env=ENV, capture_output=True)
    subprocess.run(["git", "-C", bare, "remote", "remove", "origin"], env=ENV,
                   capture_output=True)
    tar = f"{D}/MYQBD01_OFFLINE_REPO.tar.gz"
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
        "MINORITY-Y-Q-BOUND-DERIVATION-01",
        "branch  %s" % BRANCH, "head    %s" % head, "tree    %s" % tree,
        "base    %s (the repaired PMCR01 tip)" % BASE,
        "commits %d over the base" % len(commits), "",
        "    cat MYQBD01_OFFLINE_REPO.tar.gz.part* > MYQBD01_OFFLINE_REPO.tar.gz",
        "    sha256sum -c whole.sha256 && tar xzf MYQBD01_OFFLINE_REPO.tar.gz",
        "    git clone --shared bare wc", "",
        "whole sha256 %s" % whole, "parts %d" % len(parts), "",
    ] + ["  %s  %s" % (sha256(f"{D}/{n}"), n) for n in parts] + [""] + [
        "  %s  %s" % (c[0], c[1]) for c in commits]
    open(f"{D}/MANIFEST.txt", "w").write("\n".join(manifest) + "\n")

    os.makedirs(f"{D}/readback", exist_ok=True)
    script = r"""
set -e
cd %s
cat MYQBD01_OFFLINE_REPO.tar.gz.part* > readback/whole.tar.gz
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
cd wc/MYQBD01 && sha256sum -c out/MYQBD01_SHA256SUMS 2>&1 | grep -c ': OK$' | sed 's/^/SUMS_OK:/'
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
    rec = {"SECTION": "MYQBD01 delivery", "PUSH": push,
           "ARCHIVE": {"whole_sha256": whole, "parts": len(parts),
                       "bytes": os.path.getsize(tar)},
           "BRANCH": {"head": head, "tree": tree, "base": BASE,
                      "commits_over_base": len(commits), "subjects": [c[1] for c in commits]},
           "OFFLINE_READBACK": readback, "PRESERVED_EXACTLY_ONCE": True,
           "FIXED_POINT_NOTE": ("this record cannot contain the hash of the commit that "
                                "carries it; it is folded into the final commit by amending, so "
                                "the in-tree head is the predecessor and MANIFEST.txt carries "
                                "the authoritative head."),
           "HEAD_WHEN_WRITTEN": head}
    json.dump(rec, open(f"{OUT}/_myqbd01_delivery.json", "w"), indent=1, default=str)
    print("push     : attempted=%s status=%s" % (push["ATTEMPTED"], push["STATUS"]))
    print("archive  : %d parts, %d bytes, whole %s" % (len(parts), rec["ARCHIVE"]["bytes"],
                                                       whole[:16]))
    for k in ("REMOTES", "PROMISOR_PACKS", "COMMITS_REACHABLE", "HEAD",
              "SHA256SUMS_VERIFIED_OFFLINE", "FSCK_CLEAN"):
        print("readback : %-28s %s" % (k, readback[k]))
    print("readback : DELIVERABLES %d/%d missing %s"
          % (readback["DELIVERABLES_PRESENT"], len(NEED),
             readback["DELIVERABLES_MISSING"] or "none"))


if __name__ == "__main__":
    main()
