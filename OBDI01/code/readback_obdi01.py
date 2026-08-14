"""OBDI01 §28 — offline readback of the split delivery.

Run under `unshare -rn` with GIT_NO_LAZY_FETCH=1: the parts are reassembled in a fresh
directory, every digest is recomputed, the archive is expanded, the bare repository is read,
and a working copy is checked out and compared with the recorded tree hash. No network exists
inside this namespace, so nothing can silently come from a remote.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBDI01/deliver"
V = "/home/claude/OBDI01/verify/obdi01"
OUT = "/home/claude/OBDI01/out"
BRANCH = "codex/organizer-bound-domain-invariance-01"
HEAD = "7fb672d41cb896fa241688eae2809df4c40020ff"
TREE = "0199786909fd6c15afae044969027d0baf49f333"
BOUNDARY = "bb7fea748560ce8489d18ca64973f95e907ec382"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=None):
    r = subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True, env=ENV)
    return r.stdout.strip(), r.returncode


def main():
    shutil.rmtree(V, ignore_errors=True)
    os.makedirs(V)
    parts = sorted(p for p in os.listdir(D) if ".part" in p)
    recorded = {ln.split()[1].split("/")[-1]: ln.split()[0]
                for ln in open(f"{D}/parts.sha256").read().strip().splitlines()}
    whole_recorded = open(f"{D}/whole.sha256").read().split()[0]

    per_part = {}
    with open(f"{V}/reassembled.tar.gz", "wb") as out:
        for p in parts:
            d = sha256(f"{D}/{p}")
            per_part[p] = {"sha256": d, "matches_recorded": d == recorded.get(p),
                           "bytes": os.path.getsize(f"{D}/{p}")}
            with open(f"{D}/{p}", "rb") as f:
                shutil.copyfileobj(f, out)
    whole = sha256(f"{V}/reassembled.tar.gz")

    with tarfile.open(f"{V}/reassembled.tar.gz") as t:
        t.extractall(V)
    bare = f"{V}/bare10"

    tip, _ = git("rev-parse", BRANCH, cwd=bare)
    tree, _ = git("rev-parse", "%s^{tree}" % BRANCH, cwd=bare)
    shallow = [ln.strip() for ln in open(f"{bare}/shallow")] if os.path.exists(
        f"{bare}/shallow") else []
    ncommits, _ = git("rev-list", "--count", BRANCH, cwd=bare)
    fsck, rc = git("fsck", "--no-progress", cwd=bare)
    subprocess.run(["git", "clone", "--quiet", "--shared", bare, f"{V}/wc"], env=ENV,
                   capture_output=True)
    wtree, _ = git("rev-parse", "HEAD^{tree}", cwd=f"{V}/wc")
    porcelain, _ = git("status", "--porcelain", cwd=f"{V}/wc")
    nfiles, _ = git("ls-files", cwd=f"{V}/wc")
    nfiles = len(nfiles.split())
    remotes, _ = git("remote", "-v", cwd=bare)
    promisor = [f for f in os.listdir(os.path.join(bare, "objects", "pack"))
                if f.endswith(".promisor")] if os.path.isdir(
        os.path.join(bare, "objects", "pack")) else []

    # the mission's own artefacts must be present and readable in the checked-out copy
    need = ["OBDI01/out/OBDI01_FINAL_REPORT.md", "OBDI01/out/_freeze.json",
            "OBDI01/out/_results.json", "OBDI01/out/_arms.json", "OBDI01/out/_evidence.json",
            "OBDI01/out/_tests.json", "OBDI01/code/obdi01_protocol.yaml",
            "OBDI01/out/obdi01_domain_invariance.png", "OBDI01/out/obdi01_exponents.png"]
    present = {n: os.path.exists(os.path.join(V, "wc", n)) for n in need}
    raws = [f for f in os.listdir(os.path.join(V, "wc", "OBDI01", "raw"))] \
        if os.path.isdir(os.path.join(V, "wc", "OBDI01", "raw")) else []

    # the freeze inside the delivered copy must still describe the delivered code
    frz = json.load(open(os.path.join(V, "wc", "OBDI01/out/_freeze.json")))
    # a METHODS_CORE file is either OBDI01's own or one INHERITED from OBTC02 at its canonical
    # location; the readback resolves both and records which, so the inheritance is explicit
    roots = [("OBDI01/code", "own"), ("OBTC02/code", "inherited from OBTC02")]
    bad, where = [], {}
    for n, d in frz["METHODS_CORE_FILES"].items():
        hit = None
        for r, lab in roots:
            q = os.path.join(V, "wc", r, n)
            if os.path.exists(q) and sha256(q) == d:
                hit = "%s (%s)" % (r, lab)
                break
        where[n] = hit
        if hit is None:
            bad.append(n)

    # the LawSpec module itself is NOT in any mission's freeze manifest - a coverage gap
    # inherited from OBTC02. It cannot be added retroactively, so it is verified here instead:
    # the delivered bytes are compared with the bytes delivered by OBTC02.
    lawspec = {}
    for n in ("lawspec_v2.py", "observe.py"):
        a = os.path.join(V, "wc", "ORR01/code", n)
        b = os.path.join("/home/claude/OBDI01/verify/obtc02/wc", "ORR01/code", n)
        da = sha256(a) if os.path.exists(a) else None
        db = sha256(b) if os.path.exists(b) else None
        lawspec[n] = {"delivered_sha256": da, "obtc02_delivery_sha256": db,
                      "IDENTICAL": bool(da is not None and da == db)}

    res = {
        "SECTION": "OBDI01 §28 — offline readback",
        "parts": per_part, "n_parts": len(parts),
        "whole_sha256": whole, "whole_recorded": whole_recorded,
        "WHOLE_MATCHES": whole == whole_recorded,
        "ALL_PARTS_MATCH": all(v["matches_recorded"] for v in per_part.values()),
        "branch": BRANCH, "tip": tip, "tip_expected": HEAD, "TIP_MATCHES": tip == HEAD,
        "tree": tree, "tree_expected": TREE, "TREE_MATCHES": tree == TREE,
        "working_copy_tree": wtree, "WORKING_COPY_TREE_MATCHES": wtree == TREE,
        "shallow_boundary": shallow, "BOUNDARY_IS_OBTC02_HEAD": shallow == [BOUNDARY],
        "commits_carried": int(ncommits or 0),
        "fsck_clean": rc == 0 and "missing" not in fsck.lower(),
        "porcelain_empty": porcelain == "", "files_in_working_copy": nfiles,
        "remotes": remotes, "promisor_packs": promisor,
        "mandatory_artifacts_present": present,
        "ALL_MANDATORY_ARTIFACTS_PRESENT": all(present.values()),
        "raw_archives_delivered": sorted(raws), "n_raw": len(raws),
        "freeze_still_describes_delivered_code": not bad,
        "code_files_not_matching_freeze": bad,
        "methods_core_resolved_at": where,
        "LAWSPEC_COVERAGE_GAP": {
            "files": lawspec,
            "note": ("lawspec_v2.py and observe.py define the law and the recorder but appear "
                     "in NO mission's freeze manifest - a coverage gap inherited from OBTC02 "
                     "and not repairable after the fact. They are therefore verified here by "
                     "comparison with the bytes OBTC02 itself delivered, which turns "
                     "LAWSPEC_DIFF_FROM_OBTC02 = NONE from an assertion into a check."),
            "ALL_IDENTICAL": bool(all(v["IDENTICAL"] for v in lawspec.values()))},
    }
    res["READBACK_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS" if all(
        [res["WHOLE_MATCHES"], res["ALL_PARTS_MATCH"], res["TIP_MATCHES"], res["TREE_MATCHES"],
         res["WORKING_COPY_TREE_MATCHES"], res["BOUNDARY_IS_OBTC02_HEAD"], res["fsck_clean"],
         res["porcelain_empty"], res["ALL_MANDATORY_ARTIFACTS_PRESENT"],
         res["freeze_still_describes_delivered_code"], not promisor,
         res["LAWSPEC_COVERAGE_GAP"]["ALL_IDENTICAL"]])
        else "SELF_CONTAINED_SPLIT_DELIVERY_FAIL")
    json.dump(res, open(f"{OUT}/_readback.json", "w"), indent=1, default=str)
    for k in ("n_parts", "ALL_PARTS_MATCH", "WHOLE_MATCHES", "TIP_MATCHES", "TREE_MATCHES",
              "WORKING_COPY_TREE_MATCHES", "BOUNDARY_IS_OBTC02_HEAD", "commits_carried",
              "fsck_clean", "porcelain_empty", "files_in_working_copy", "promisor_packs",
              "ALL_MANDATORY_ARTIFACTS_PRESENT", "n_raw",
              "freeze_still_describes_delivered_code", "READBACK_STATUS"):
        print("%-42s %s" % (k, res[k]))


if __name__ == "__main__":
    main()
