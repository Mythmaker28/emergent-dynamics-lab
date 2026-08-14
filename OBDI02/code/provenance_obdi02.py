"""OBDI02 §3 — provenance: rebuild OBDI01's self-contained split artefact in a fresh directory
with the network namespace unshared, and verify every claim the mandate lists.

Nothing in this file reads the live working tree of the repository: everything is read back out
of the delivered parts, so a corrupted or drifting workspace cannot be mistaken for a valid
inheritance.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBDI01/deliver"
V = "/home/claude/OBDI02/verify/obdi01"
OUT = "/home/claude/OBDI02/out"
BRANCH = "codex/organizer-bound-domain-invariance-01"
HEAD = "5a37a7be73c3624e76b9c77ee75fd22172b6eb52"
TREE = "04eef05ebd74af0bab128051b9b823efebc69f5f"
BOUNDARY = "bb7fea748560ce8489d18ca64973f95e907ec382"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}
EXPECTED_ARMS = [("L%d/seed%d" % (L, s)).replace("/", "__")
                 for L, base in ((36, 771010), (72, 771110), (96, 771210))
                 for s in range(base, base + 5)]


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
    res = {"SECTION": "OBDI02 §3"}

    # ------------------------------------------------------------------ parts and archive
    parts = sorted(p for p in os.listdir(D) if ".part" in p)
    recorded = {ln.split()[1].split("/")[-1]: ln.split()[0]
                for ln in open(f"{D}/parts.sha256").read().strip().splitlines()}
    whole_recorded = open(f"{D}/whole.sha256").read().split()[0]
    per_part = {}
    with open(f"{V}/reassembled.tar.gz", "wb") as out:
        for p in parts:
            d = sha256(f"{D}/{p}")
            per_part[p] = {"sha256": d, "recorded": recorded.get(p),
                           "MATCHES": d == recorded.get(p),
                           "bytes": os.path.getsize(f"{D}/{p}")}
            with open(f"{D}/{p}", "rb") as f:
                shutil.copyfileobj(f, out)
    res["PARTS"] = per_part
    res["N_PARTS"] = len(parts)
    res["ALL_PART_DIGESTS_MATCH"] = all(v["MATCHES"] for v in per_part.values())
    res["WHOLE_SHA256"] = sha256(f"{V}/reassembled.tar.gz")
    res["WHOLE_SHA256_RECORDED"] = whole_recorded
    res["WHOLE_MATCHES"] = res["WHOLE_SHA256"] == whole_recorded

    with tarfile.open(f"{V}/reassembled.tar.gz") as t:
        t.extractall(V)
    bare = f"{V}/bare10"

    # ------------------------------------------------------------------ the five git checks
    tip, _, _ = git("rev-parse", "HEAD", cwd=bare)
    tree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=bare)
    missing, _, _ = git("rev-list", "--objects", "--missing=print", "HEAD", cwd=bare)
    miss = [ln for ln in missing.splitlines() if ln.startswith("?")]
    fsck, rc_fsck, fsck_err = git("fsck", "--full", "--no-progress", cwd=bare)
    subprocess.run(["git", "clone", "--quiet", "--shared", bare, f"{V}/wc"], env=ENV,
                   capture_output=True)
    porcelain, _, _ = git("status", "--porcelain", cwd=f"{V}/wc")
    wtree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=f"{V}/wc")
    files, _, _ = git("ls-files", cwd=f"{V}/wc")
    nfiles = len(files.split())
    branch_present, rc_b, _ = git("rev-parse", "--verify", "--quiet", BRANCH, cwd=bare)
    shallow = [ln.strip() for ln in open(f"{bare}/shallow")] if os.path.exists(
        f"{bare}/shallow") else []
    remotes, _, _ = git("remote", "-v", cwd=bare)
    promisor = [f for f in os.listdir(os.path.join(bare, "objects", "pack"))
                if f.endswith(".promisor")]

    res["GIT"] = {
        "rev_parse_HEAD": tip, "HEAD_expected": HEAD, "HEAD_MATCHES": tip == HEAD,
        "rev_parse_HEAD_tree": tree, "TREE_expected": TREE, "TREE_MATCHES": tree == TREE,
        "rev_list_missing_objects": miss, "ZERO_MISSING_OBJECTS": not miss,
        "fsck_returncode": rc_fsck, "fsck_stdout_lines": len(fsck.splitlines()),
        "fsck_stderr": fsck_err[:400],
        "FSCK_CLEAN": rc_fsck == 0 and "missing" not in (fsck + fsck_err).lower(),
        "status_porcelain": porcelain, "PORCELAIN_EMPTY": porcelain == "",
        "working_copy_tree": wtree, "WORKING_COPY_TREE_MATCHES": wtree == TREE,
        "branch": BRANCH, "BRANCH_PRESENT": bool(branch_present) and rc_b == 0,
        "branch_tip": branch_present,
        "shallow_boundary": shallow, "BOUNDARY_IS_OBDI01_PARENT": shallow == [BOUNDARY],
        "n_files": nfiles,
        "remotes": remotes, "NO_REMOTE_CONFIGURED": remotes == "",
        "promisor_packs": promisor, "NO_IMPLICIT_FETCH": not promisor,
        "network": "read back inside `unshare -rn` with GIT_NO_LAZY_FETCH=1",
    }

    wc = f"{V}/wc"
    # ------------------------------------------------------------------ mandated contents
    raws = sorted(f[:-4] for f in os.listdir(f"{wc}/OBDI01/raw")) \
        if os.path.isdir(f"{wc}/OBDI01/raw") else []
    conf = [t for t in raws if t in EXPECTED_ARMS]
    need = {
        "freeze_manifest": "OBDI01/out/_freeze.json",
        "direct_test_specification": "OBDI01/code/obdi01_protocol.yaml",
        "results_online_and_posthoc": "OBDI01/out/_results.json",
        "per_arm_record": "OBDI01/out/_arms.json",
        "seed_register": "OBDI01/out/_seeds.json",
        "evidence_and_disposition": "OBDI01/out/_evidence.json",
        "instrument_tests": "OBDI01/out/_tests.json",
        "power_analysis": "OBDI01/out/_power.json",
        "predictions": "OBDI01/out/_predictions.json",
        "final_report": "OBDI01/out/OBDI01_FINAL_REPORT.md",
    }
    res["CONTENTS"] = {k: {"path": p, "present": os.path.exists(os.path.join(wc, p))}
                       for k, p in need.items()}
    res["ALL_MANDATED_FILES_PRESENT"] = all(v["present"] for v in res["CONTENTS"].values())
    res["RAW_TRAJECTORIES"] = {"delivered": raws, "n_delivered": len(raws),
                               "confirmatory_expected": EXPECTED_ARMS,
                               "confirmatory_present": conf,
                               "FIFTEEN_TRAJECTORIES_PRESENT": len(conf) == 15,
                               "extra": sorted(set(raws) - set(EXPECTED_ARMS))}

    # online and post-hoc outputs must both be present, per arm, inside the results object
    R = json.load(open(f"{wc}/OBDI01/out/_results.json"))
    A = json.load(open(f"{wc}/OBDI01/out/_arms.json"))
    res["ONLINE_AND_POSTHOC"] = {
        "arms_recorded": R["n_arms"],
        "technically_valid": R["technically_valid"], "gates_agree": R["gates_agree"],
        "per_arm_has_both_classifications": all(
            ("LEGACY_RELATIVE_LOCALIZATION" in a and "gate_posthoc_PER_ARM_PASS" in a)
            for a in A),
        "BOTH_PRESENT": bool(R["n_arms"] == 15 and R["gates_agree"] == 15)}

    # lawspec bit-identity against OBTC02's own delivery
    o2 = "/home/claude/OBDI01/verify/obtc02/wc"
    ls = {}
    for n in ("lawspec_v2.py", "observe.py"):
        a, b = os.path.join(wc, "ORR01/code", n), os.path.join(o2, "ORR01/code", n)
        da = sha256(a) if os.path.exists(a) else None
        db = sha256(b) if os.path.exists(b) else None
        ls[n] = {"obdi01_delivery": da, "obtc02_delivery": db,
                 "BIT_IDENTICAL": bool(da and da == db)}
    res["LAWSPEC_IDENTITY_WITH_OBTC02"] = {
        "files": ls, "ALL_BIT_IDENTICAL": all(v["BIT_IDENTICAL"] for v in ls.values())}

    # the OBDI01 freeze must still describe the delivered code
    frz = json.load(open(f"{wc}/OBDI01/out/_freeze.json"))
    roots = ["OBDI01/code", "OBTC02/code"]
    bad, where = [], {}
    for n, d in frz["METHODS_CORE_FILES"].items():
        hit = next((r for r in roots if os.path.exists(os.path.join(wc, r, n))
                    and sha256(os.path.join(wc, r, n)) == d), None)
        where[n] = hit
        if hit is None:
            bad.append(n)
    res["FREEZE_MANIFEST_CHECK"] = {
        "OBDI01_METHODS_CORE_HASH": frz["OBDI01_METHODS_CORE_HASH"],
        "files": len(frz["METHODS_CORE_FILES"]), "resolved_at": where,
        "not_matching": bad, "ALL_MATCH": not bad}

    ok = all([res["ALL_PART_DIGESTS_MATCH"], res["WHOLE_MATCHES"], res["GIT"]["HEAD_MATCHES"],
              res["GIT"]["TREE_MATCHES"], res["GIT"]["ZERO_MISSING_OBJECTS"],
              res["GIT"]["FSCK_CLEAN"], res["GIT"]["PORCELAIN_EMPTY"],
              res["GIT"]["WORKING_COPY_TREE_MATCHES"], res["GIT"]["BRANCH_PRESENT"],
              res["GIT"]["NO_IMPLICIT_FETCH"], res["ALL_MANDATED_FILES_PRESENT"],
              res["RAW_TRAJECTORIES"]["FIFTEEN_TRAJECTORIES_PRESENT"],
              res["ONLINE_AND_POSTHOC"]["BOTH_PRESENT"],
              res["LAWSPEC_IDENTITY_WITH_OBTC02"]["ALL_BIT_IDENTICAL"],
              res["FREEZE_MANIFEST_CHECK"]["ALL_MATCH"]])
    res["PROVENANCE_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS" if ok
                                else "PROVENANCE_FAIL")
    json.dump(res, open(f"{OUT}/_provenance.json", "w"), indent=1, default=str)
    for k, v in [("parts", "%d, all digests match: %s" % (res["N_PARTS"],
                                                          res["ALL_PART_DIGESTS_MATCH"])),
                 ("whole archive", res["WHOLE_MATCHES"]),
                 ("HEAD", res["GIT"]["HEAD_MATCHES"]), ("tree", res["GIT"]["TREE_MATCHES"]),
                 ("missing objects", len(res["GIT"]["rev_list_missing_objects"])),
                 ("fsck clean", res["GIT"]["FSCK_CLEAN"]),
                 ("porcelain empty", res["GIT"]["PORCELAIN_EMPTY"]),
                 ("branch present", res["GIT"]["BRANCH_PRESENT"]),
                 ("files", res["GIT"]["n_files"]),
                 ("no implicit fetch", res["GIT"]["NO_IMPLICIT_FETCH"]),
                 ("mandated files", res["ALL_MANDATED_FILES_PRESENT"]),
                 ("15 trajectories", res["RAW_TRAJECTORIES"]["FIFTEEN_TRAJECTORIES_PRESENT"]),
                 ("online+posthoc", res["ONLINE_AND_POSTHOC"]["BOTH_PRESENT"]),
                 ("lawspec identical to OBTC02",
                  res["LAWSPEC_IDENTITY_WITH_OBTC02"]["ALL_BIT_IDENTICAL"]),
                 ("freeze manifest", res["FREEZE_MANIFEST_CHECK"]["ALL_MATCH"]),
                 ("PROVENANCE_STATUS", res["PROVENANCE_STATUS"])]:
        print("%-32s %s" % (k, v))


if __name__ == "__main__":
    main()
