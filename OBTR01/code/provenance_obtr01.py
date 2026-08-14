"""OBDI02 §23 — offline readback of the split delivery, under `unshare -rn` with
GIT_NO_LAZY_FETCH=1: no network exists inside the namespace, so nothing can come from a remote.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBDCA01/deliver"
V = "/home/claude/OBTR01/verify/obdca01"
OUT = "/home/claude/OBTR01/out"
BRANCH = "codex/organizer-bound-domain-contract-audit-01"
HEAD = "ad8f6bfb939ddb9a5b3b5c66155a3fdf118b2b29"
TREE = "2a74bbd8178f994bacf2b1fd33b809c17c99f8cd"
BOUNDARY = "be09dde3c56212930b4848bb50df409b57e7d2d0"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}
NEED_OLD = ["OBDCA01/out/OBDCA01_FINAL_REPORT.md", "OBDCA01/out/_provenance.json",
        "OBDCA01/out/_margin_genealogy.json", "OBDCA01/out/_recompute.json",
        "OBDCA01/out/_construct_validity.json", "OBDCA01/out/_adjudication.json",
        "OBDCA01/out/_alternative_estimand_check.json", "OBDCA01/out/_delivery.json",
        "OBDCA01/out/SHA256SUMS", "OBDCA01/out/obdca01_contract_audit.png",
        "OBDI02/code/obdi02_protocol.yaml", "OBDI02/out/_freeze.json",
        "OBDI02/out/_results.json", "OBDI02/out/OBDI02_FINAL_REPORT.md",
        "OBDI01/out/OBDI01_FINAL_REPORT.md"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=None):
    r = subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True, env=ENV)
    return r.stdout.strip(), r.returncode, r.stderr.strip()


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
            per_part[p] = {"sha256": d, "MATCHES": d == recorded.get(p),
                           "bytes": os.path.getsize(f"{D}/{p}")}
            with open(f"{D}/{p}", "rb") as f:
                shutil.copyfileobj(f, out)
    whole = sha256(f"{V}/reassembled.tar.gz")
    with tarfile.open(f"{V}/reassembled.tar.gz") as t:
        t.extractall(V)
    bare = f"{V}/bare"

    tip, _, _ = git("rev-parse", "HEAD", cwd=bare)
    tree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=bare)
    missing, _, _ = git("rev-list", "--objects", "--missing=print", "HEAD", cwd=bare)
    miss = [ln for ln in missing.splitlines() if ln.startswith("?")]
    fsck, rc, ferr = git("fsck", "--full", "--no-progress", cwd=bare)
    subprocess.run(["git", "clone", "--quiet", "--shared", bare, f"{V}/wc"], env=ENV,
                   capture_output=True)
    wc = f"{V}/wc"
    wtree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=wc)
    porcelain, _, _ = git("status", "--porcelain", cwd=wc)
    nfiles = len(git("ls-files", cwd=wc)[0].split())
    shallow = [ln.strip() for ln in open(f"{bare}/shallow")] if os.path.exists(
        f"{bare}/shallow") else []
    remotes, _, _ = git("remote", "-v", cwd=bare)
    promisor = [f for f in os.listdir(os.path.join(bare, "objects", "pack"))
                if f.endswith(".promisor")]
    ncommits, _, _ = git("rev-list", "--count", "HEAD", cwd=bare)

    NEED = NEED_OLD + [
        "MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md", "MCM01/out/MCM01_FINAL_REPORT.md",
        "MCM01/code/region.py", "MCM01/code/lattice.py", "MCM01/out/_region.json",
        "MCM01/out/_freeze1.json", "CSC01/out/CSC01_FINAL_REPORT.md",
        "ORR01/code/lawspec_v2.py", "ORR01/code/kinetics.py",
        "OBTC01/out/OBTC01_FINAL_REPORT.md", "OBTC02/out/_results.json",
        "OBTC02/out/OBTC02_FINAL_REPORT.md", "OBDI01/out/_arms.json",
        "OBDCA01/out/OBDCA01_FINAL_REPORT.md", "OBDCA01/out/_adjudication.json",
        "OBDCA01/out/_recompute.json", "OBDCA01/out/_construct_validity.json"]
    present = {n: os.path.exists(os.path.join(wc, n)) for n in NEED}
    raws = {m: (len(os.listdir(os.path.join(wc, m, "raw")))
                if os.path.isdir(os.path.join(wc, m, "raw")) else 0)
            for m in ("OBTC02", "OBDI01", "OBDI02", "CSC01", "MCM01")}
    raw02 = os.listdir(os.path.join(wc, "OBDI02", "raw")) \
        if os.path.isdir(os.path.join(wc, "OBDI02", "raw")) else []
    raw01 = os.listdir(os.path.join(wc, "OBDI01", "raw")) \
        if os.path.isdir(os.path.join(wc, "OBDI01", "raw")) else []
    n_code = len([f for f in os.listdir(os.path.join(wc, "OBDCA01", "code"))
                  if f.endswith(".py")])

    frz = json.load(open(os.path.join(wc, "OBDI02/out/_freeze.json")))
    roots = [("OBDI02/code", "inherited from OBDI02"),
             ("OBDI01/code", "inherited from OBDI01"),
             ("OBTC02/code", "inherited from OBTC02")]
    bad, where = [], {}
    for n, d in frz["METHODS_CORE_FILES"].items():
        hit = None
        for r, lab in roots:
            q = os.path.join(wc, r, n)
            if os.path.exists(q) and sha256(q) == d:
                hit = "%s (%s)" % (r, lab)
                break
        where[n] = hit
        if hit is None:
            bad.append(n)

    lawspec = {}
    for n in ("lawspec_v2.py", "observe.py"):
        a = os.path.join(wc, "ORR01/code", n)
        b = os.path.join("/home/claude/OBDI02/verify/obdi01/wc", "ORR01/code", n)
        da = sha256(a) if os.path.exists(a) else None
        db = sha256(b) if os.path.exists(b) else None
        lawspec[n] = {"delivered": da, "parent_delivery": db,
                      "IDENTICAL": bool(da and da == db)}

    res = {
        "SECTION": "OBTR01 §4 — offline provenance readback of the inherited delivery",
        "parts": per_part, "n_parts": len(parts),
        "ALL_PARTS_MATCH": all(v["MATCHES"] for v in per_part.values()),
        "whole_sha256": whole, "whole_recorded": whole_recorded,
        "WHOLE_MATCHES": whole == whole_recorded,
        "tip": tip, "TIP_MATCHES": tip == HEAD,
        "tree": tree, "TREE_MATCHES": tree == TREE,
        "working_copy_tree": wtree, "WORKING_COPY_TREE_MATCHES": wtree == TREE,
        "missing_objects": miss, "ZERO_MISSING_OBJECTS": not miss,
        "fsck_returncode": rc, "fsck_stderr": ferr[:300],
        "FSCK_CLEAN": rc == 0 and "missing" not in (fsck + ferr).lower(),
        "porcelain": porcelain, "PORCELAIN_EMPTY": porcelain == "",
        "shallow_boundary": shallow, "BOUNDARY_IS_OBDI02_HEAD": shallow == [BOUNDARY],
        "commits_carried": int(ncommits or 0), "files_in_working_copy": nfiles,
        "remotes": remotes, "promisor_packs": promisor, "NO_IMPLICIT_FETCH": not promisor,
        "mandatory_artifacts": present,
        "ALL_MANDATORY_ARTIFACTS_PRESENT": all(present.values()),
        "raw_obdi02": len(raw02), "raw_obdi01": len(raw01),
        "raw_by_mission": raws,
        "ALL_138_TRAJECTORIES_DELIVERED": len(raw02) == 138,
        "methods_core_resolved_at": where, "code_files_not_matching_freeze": bad,
        "FREEZE_DESCRIBES_DELIVERED_CODE": not bad,
        "LAWSPEC_IDENTITY": {"files": lawspec,
                             "ALL_IDENTICAL": all(v["IDENTICAL"] for v in lawspec.values())},
    }
    res["READBACK_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS" if all(
        [res["ALL_PARTS_MATCH"], res["WHOLE_MATCHES"], res["TIP_MATCHES"], res["TREE_MATCHES"],
         res["WORKING_COPY_TREE_MATCHES"], res["ZERO_MISSING_OBJECTS"], res["FSCK_CLEAN"],
         res["PORCELAIN_EMPTY"], res["BOUNDARY_IS_OBDI02_HEAD"], res["NO_IMPLICIT_FETCH"],
         res["ALL_MANDATORY_ARTIFACTS_PRESENT"], res["ALL_138_TRAJECTORIES_DELIVERED"],
         res["FREEZE_DESCRIBES_DELIVERED_CODE"], res["LAWSPEC_IDENTITY"]["ALL_IDENTICAL"]])
        else "SELF_CONTAINED_SPLIT_DELIVERY_FAIL")
    json.dump(res, open(f"{OUT}/_provenance.json", "w"), indent=1, default=str)
    for k in ("n_parts", "ALL_PARTS_MATCH", "WHOLE_MATCHES", "TIP_MATCHES", "TREE_MATCHES",
              "WORKING_COPY_TREE_MATCHES", "ZERO_MISSING_OBJECTS", "FSCK_CLEAN",
              "PORCELAIN_EMPTY", "BOUNDARY_IS_OBDI02_HEAD", "commits_carried",
              "files_in_working_copy", "NO_IMPLICIT_FETCH", "ALL_MANDATORY_ARTIFACTS_PRESENT",
              "raw_obdi02", "ALL_138_TRAJECTORIES_DELIVERED", "FREEZE_DESCRIBES_DELIVERED_CODE",
              "READBACK_STATUS"):
        print("%-38s %s" % (k, res[k]))
    print("lawspec identical to the OBDI01 delivery:", res["LAWSPEC_IDENTITY"]["ALL_IDENTICAL"])


if __name__ == "__main__":
    main()
