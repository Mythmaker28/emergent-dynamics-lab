"""OBTR01 §29 — one push attempt, then the split self-contained delivery.

The push is attempted ONCE. If the proxy refuses, the response is recorded verbatim and the
delivery falls back to a gzipped bare shallow single-branch repository, split into 19 MB parts
with a digest per part and one for the whole, so that the branch can be reassembled and read
back with no network at all.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

REPO = "/home/claude/edl"
D = "/home/claude/OBFOR01/deliver"
OUT = "/home/claude/OBFOR01/out"
BRANCH = "codex/organizer-bound-full-operator-residual-01"
BASE = "062d3735b726bb9c7325aef063c803823e46218d"
PART = 19_000_000
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1"}


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
    commits = [{"commit": ln.split("\x1f")[0], "subject": ln.split("\x1f")[1]}
               for ln in log.splitlines() if ln.strip()][::-1]
    head, _, _ = git("rev-parse", "HEAD")
    tree, _, _ = git("rev-parse", "HEAD^{tree}")

    # ---------------------------------------------------------------- one push attempt
    # The mandate allows exactly ONE attempt. The archive has to be rebuilt after the delivery
    # record is committed, so this function runs more than once; the recorded response is
    # reused rather than the push being retried.
    prior = None
    if os.path.exists(f"{OUT}/_delivery.json"):
        prior = json.load(open(f"{OUT}/_delivery.json")).get("PUSH_ATTEMPT")
    if prior:
        push, rc, err, out = prior, prior["returncode"], prior["stderr"], prior["stdout"]
        push["note"] = "recorded on the first and only attempt; not retried on this rebuild"
    else:
        out, rc, err = git("push", "origin", BRANCH)
        push = {"attempts": 1, "returncode": rc, "stdout": out, "stderr": err,
                "action_taken": ("pushed" if rc == 0 else
                                 "one attempt only, response recorded verbatim, split "
                                 "delivery instead")}

    # ---------------------------------------------------------------- split delivery
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    bare = f"{D}/bare"
    # a file:// URL, not a path: git silently ignores --depth for local-path clones, which
    # would ship the whole history instead of this mission's commits plus the boundary.
    # depth is len(commits) + 1 so that the OBTR01 head is a REAL commit in the archive and
    # the diff this mission introduces is verifiable offline, not just asserted.
    subprocess.run(["git", "clone", "--quiet", "--bare", "--single-branch",
                    "--branch", BRANCH, "--depth", str(len(commits) + 1),
                    "file://" + REPO, bare], env=ENV, capture_output=True)
    subprocess.run(["git", "-C", bare, "remote", "remove", "origin"], env=ENV,
                   capture_output=True)
    tar = f"{D}/OBFOR01_OFFLINE_REPO.tar.gz"
    with tarfile.open(tar, "w:gz") as t:
        t.add(bare, arcname="bare")
    whole = sha256(tar)
    parts, i = [], 0
    with open(tar, "rb") as f:
        while True:
            b = f.read(PART)
            if not b:
                break
            n = "%s.part%02d" % (os.path.basename(tar), i)
            open(f"{D}/{n}", "wb").write(b)
            parts.append(n)
            i += 1
    with open(f"{D}/parts.sha256", "w") as f:
        for n in parts:
            f.write("%s  %s\n" % (sha256(f"{D}/{n}"), n))
    open(f"{D}/whole.sha256", "w").write("%s  %s\n" % (whole, os.path.basename(tar)))

    boundary, _, _ = git("rev-parse", "--short=40", BASE)
    shallow = ""
    if os.path.exists(f"{bare}/shallow"):
        shallow = open(f"{bare}/shallow").read().strip()

    manifest = [
        "OBFOR01 — ORGANIZER-BOUND-FULL-OPERATOR-RESIDUAL-01",
        "branch  %s" % BRANCH,
        "head    %s" % head,
        "tree    %s" % tree,
        "base    %s (OBTR01)" % BASE,
        "commits %d" % len(commits),
        "",
        "The archive is a gzipped BARE SHALLOW SINGLE-BRANCH repository with its remote",
        "removed, so nothing in it can be fetched from anywhere. Reassemble with",
        "",
        "    cat OBFOR01_OFFLINE_REPO.tar.gz.part* > OBFOR01_OFFLINE_REPO.tar.gz",
        "    sha256sum -c whole.sha256",
        "    tar xzf OBFOR01_OFFLINE_REPO.tar.gz",
        "    git clone --shared bare wc",
        "",
        "whole sha256 %s" % whole,
        "parts        %d" % len(parts),
        "",
    ] + ["  %s  %s" % (sha256(f"{D}/{n}"), n) for n in parts] + [
        "",
        "SCIENTIFIC_RUNS_USED = 28",
        "TOMMY_ACTION_REQUIRED = NONE",
    ]
    open(f"{D}/DELIVERY_MANIFEST.txt", "w").write("\n".join(manifest) + "\n")

    rec = {
        "SECTION": "OBFOR01 §28 — delivery record",
        "BRANCH": BRANCH, "BASE": BASE, "HEAD": head, "TREE": tree,
        "COMMITS": commits, "n_commits": len(commits),
        "MANDATED_SEPARATION_AT_LEAST_EIGHT": len(commits) >= 8,
        "PUSH_ATTEMPT": push,
        "ARTEFACT": {"whole_sha256": whole, "parts": len(parts),
                     "part_bytes": PART,
                     "bare_shallow_boundary": shallow,
                     "boundary_is_the_OBTR01_head": shallow == BASE},
        "SELF_REFERENCE_NOTE": ("this record cannot list the commit that carries it. It "
                                "enumerates every commit up to the one before, and the "
                                "readback in _readback.json counts the branch from the base "
                                "independently, so the two together cover the whole branch."),
        "NO_INHERITED_COMMIT_REWRITTEN": True,
        "NO_REBASE": True,
        "SCIENTIFIC_RUNS_USED": 28,
        "APPEND_ONLY_NOTE": ("this mission modifies no inherited artefact. The OBDI02 and "
                             "OBDCA01 reports, freezes, results and trajectories are read "
                             "only; every statement about them is added under "
                             "OBFOR01/out/OBFOR01_APPEND_ONLY_NOTES.md."),
    }
    json.dump(rec, open(f"{OUT}/_delivery.json", "w"), indent=1)

    print("commits on the branch: %d  (>= 8 required: %s)"
          % (len(commits), len(commits) >= 8))
    for c in commits:
        print("  %s  %s" % (c["commit"][:12], c["subject"][:96]))
    print()
    print("push attempt: returncode %d" % rc)
    for ln in (err or out).splitlines()[:4]:
        print("   %s" % ln)
    print()
    print("archive %s, %d parts, boundary %s (is OBTR01 head: %s)"
          % (whole[:16] + "...", len(parts), shallow[:12], shallow == BASE))


if __name__ == "__main__":
    main()
