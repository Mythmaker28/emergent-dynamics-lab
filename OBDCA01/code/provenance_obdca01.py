"""OBDCA01 §3-§4 — provenance of the OBDI02 delivery, and the hierarchy of sources of truth.

The hierarchy is not assumed: each level is located in the repository, and each file is
classified by whether it existed BEFORE the freeze, between the freeze and the runs, or only
AFTER the runs. A file written after the runs cannot retroactively add a margin, a primary
outcome, a qualification condition, a disposition or a stopping rule; the classification is
what makes that rule enforceable rather than rhetorical.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBDI02/deliver"
V = "/home/claude/OBDCA01/verify/obdi02"
OUT = "/home/claude/OBDCA01/out"
BRANCH = "codex/organizer-bound-domain-invariance-02"
HEAD = "be09dde3c56212930b4848bb50df409b57e7d2d0"
TREE = "83b0592b1479e3715d44108a3cc6cf6d07c8e6fa"
BOUNDARY = "5a37a7be73c3624e76b9c77ee75fd22172b6eb52"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}


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
    res = {"SECTION": "OBDCA01 §3-§4"}

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
    whole = sha256(f"{V}/reassembled.tar.gz")
    with tarfile.open(f"{V}/reassembled.tar.gz") as t:
        t.extractall(V)
    bare, wc = f"{V}/bare", f"{V}/wc"
    subprocess.run(["git", "clone", "--quiet", "--shared", bare, wc], env=ENV,
                   capture_output=True)

    tip, _, _ = git("rev-parse", "HEAD", cwd=bare)
    tree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=bare)
    missing, _, _ = git("rev-list", "--objects", "--missing=print", "HEAD", cwd=bare)
    miss = [ln for ln in missing.splitlines() if ln.startswith("?")]
    fsck, rc, ferr = git("fsck", "--full", "--no-progress", cwd=bare)
    porcelain, _, _ = git("status", "--porcelain", cwd=wc)
    wtree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=wc)
    nfiles = len(git("ls-files", cwd=wc)[0].split())
    shallow = [ln.strip() for ln in open(f"{bare}/shallow")]
    remotes, _, _ = git("remote", "-v", cwd=bare)
    promisor = [f for f in os.listdir(os.path.join(bare, "objects", "pack"))
                if f.endswith(".promisor")]
    commits, _, _ = git("log", "--format=%H|%at|%s", "HEAD", "^" + BOUNDARY, cwd=bare)
    rows = [{"commit": c.split("|")[0], "epoch": int(c.split("|")[1]),
             "subject": c.split("|", 2)[2]} for c in reversed(commits.splitlines())]

    res["ARCHIVE"] = {"parts": per_part, "n_parts": len(parts),
                      "ALL_PART_DIGESTS_MATCH": all(v["MATCHES"] for v in per_part.values()),
                      "whole_sha256": whole, "whole_recorded": whole_recorded,
                      "WHOLE_MATCHES": whole == whole_recorded}
    res["GIT"] = {
        "rev_parse_HEAD": tip, "HEAD_MATCHES": tip == HEAD,
        "rev_parse_HEAD_tree": tree, "TREE_MATCHES": tree == TREE,
        "rev_list_missing": miss, "ZERO_MISSING_OBJECTS": not miss,
        "fsck_returncode": rc, "FSCK_CLEAN": rc == 0 and "missing" not in (fsck + ferr).lower(),
        "status_porcelain": porcelain, "PORCELAIN_EMPTY": porcelain == "",
        "working_copy_tree": wtree, "WORKING_COPY_TREE_MATCHES": wtree == TREE,
        "branch": BRANCH, "shallow_boundary": shallow,
        "BOUNDARY_IS_OBDI01_HEAD": shallow == [BOUNDARY],
        "n_files": nfiles, "remotes": remotes, "NO_REMOTE": remotes == "",
        "promisor_packs": promisor, "NO_IMPLICIT_FETCH": not promisor,
        "commits": rows, "n_commits": len(rows),
        "network": "reassembled and read inside unshare -rn with GIT_NO_LAZY_FETCH=1"}

    raw = sorted(os.listdir(f"{wc}/OBDI02/raw"))
    need = {
        "frozen_protocol": "OBDI02/code/obdi02_protocol.yaml",
        "freeze_manifest": "OBDI02/out/_freeze.json",
        "frozen_gate_code": "OBDI02/code/gate_obdi02.py",
        "frozen_runner": "OBDI02/code/run_obdi02.py",
        "frozen_worker": "OBDI02/code/worker_obdi02.py",
        "power_output": "OBDI02/out/_power.json",
        "plan_inputs": "OBDI02/out/_plan_inputs.json",
        "seed_register": "OBDI02/out/_seeds.json",
        "results": "OBDI02/out/_results.json",
        "arms": "OBDI02/out/_arms.json",
        "postrun_analysis_code": "OBDI02/code/analysis_obdi02.py",
        "postrun_evidence": "OBDI02/out/_evidence.json",
        "postrun_diagnostic": "OBDI02/out/_posthoc.json",
        "final_report": "OBDI02/out/OBDI02_FINAL_REPORT.md",
        "obdi01_protocol_for_margin_genealogy": "OBDI01/code/obdi01_protocol.yaml",
        "obdi01_results_for_margin_genealogy": "OBDI01/out/_results.json",
        "obdi01_report_for_margin_genealogy": "OBDI01/out/OBDI01_FINAL_REPORT.md",
        "obdi02_equivalence_audit": "OBDI02/out/_equivalence_audit.json",
    }
    res["CONTENTS"] = {k: {"path": p, "present": os.path.exists(os.path.join(wc, p))}
                       for k, p in need.items()}
    res["ALL_REQUIRED_PRESENT"] = all(v["present"] for v in res["CONTENTS"].values())
    res["RAW_TRAJECTORIES"] = {"n": len(raw), "ALL_138_PRESENT": len(raw) == 138}

    # ---------------------------------------------------------------- freeze reproduction
    frz = json.load(open(f"{wc}/OBDI02/out/_freeze.json"))
    code = f"{wc}/OBDI02/code"
    roots = ["OBDI02/code", "OBDI01/code", "OBTC02/code"]
    digests, bad, where = {}, [], {}
    for n, d in frz["METHODS_CORE_FILES"].items():
        hit = next((r for r in roots if os.path.exists(os.path.join(wc, r, n))
                    and sha256(os.path.join(wc, r, n)) == d), None)
        where[n] = hit
        digests[n] = d
        if hit is None:
            bad.append(n)
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode()); h.update(b"\0"); h.update(digests[n].encode()); h.update(b"\n")
    recomputed = h.hexdigest()
    res["METHODS_CORE_HASH_REPRODUCTION"] = {
        "recorded": frz["OBDI02_METHODS_CORE_HASH"], "recomputed_from_the_manifest": recomputed,
        "MATCHES": recomputed == frz["OBDI02_METHODS_CORE_HASH"],
        "files_resolved_at": where, "files_not_found_with_the_recorded_digest": bad,
        "ALL_FILES_PRESENT_WITH_THE_RECORDED_DIGEST": not bad,
        "spec_sha256_recorded": frz["spec_sha256"],
        "spec_sha256_recomputed": sha256(os.path.join(code, "obdi02_protocol.yaml")),
        "SPEC_MATCHES": frz["spec_sha256"] == sha256(os.path.join(code,
                                                                  "obdi02_protocol.yaml"))}
    del code

    # ---------------------------------------------------------------- §3 hierarchy
    def first_commit(path):
        out, _, _ = git("log", "--reverse", "--format=%H|%at", "--", path, cwd=wc)
        if not out:
            return None
        c, e = out.splitlines()[0].split("|")
        return {"commit": c, "epoch": int(e)}

    freeze_commit = next((r for r in rows if "§17" in r["subject"] or "freeze" in
                          r["subject"].lower()), None)
    run_commit = next((r for r in rows if "§16" in r["subject"]), None)
    tracked = git("ls-files", "OBDI02", cwd=wc)[0].split()
    classified = {}
    for p in tracked:
        fc = first_commit(p)
        if not fc:
            continue
        classified[p] = {
            "first_commit": fc["commit"][:12], "epoch": fc["epoch"],
            "phase": ("PRE_FREEZE" if freeze_commit and fc["epoch"] < freeze_commit["epoch"]
                      else ("AT_FREEZE" if freeze_commit and fc["commit"] ==
                            freeze_commit["commit"]
                            else ("POST_FREEZE_PRE_RUN"
                                  if run_commit and fc["epoch"] < run_commit["epoch"]
                                  else "POST_RUN"))),
            "in_methods_core": os.path.basename(p) in frz["METHODS_CORE_FILES"]
            and p.startswith("OBDI02/code/")}

    hierarchy = [
        {"rank": 1, "level": "machine-readable specification frozen before the runs",
         "path": "OBDI02/code/obdi02_protocol.yaml",
         "phase": classified.get("OBDI02/code/obdi02_protocol.yaml", {}).get("phase"),
         "in_methods_core": True},
        {"rank": 2, "level": "content covered by METHODS_CORE_HASH",
         "path": sorted(frz["METHODS_CORE_FILES"]), "in_methods_core": True},
        {"rank": 3, "level": "freeze manifest", "path": "OBDI02/out/_freeze.json",
         "phase": classified.get("OBDI02/out/_freeze.json", {}).get("phase"),
         "in_methods_core": False},
        {"rank": 4, "level": "timestamped pre-freeze plan",
         "path": ["OBDI02/out/_plan_inputs.json", "OBDI02/out/_power.json",
                  "OBDI02/out/_seeds.json", "OBDI02/out/_summary_choice.json"],
         "phase": classified.get("OBDI02/out/_plan_inputs.json", {}).get("phase")},
        {"rank": 5, "level": "frozen analysis code",
         "path": ["OBDI02/code/gate_obdi02.py", "OBDI02/code/run_obdi02.py",
                  "OBDI02/code/worker_obdi02.py"], "in_methods_core": True},
        {"rank": 6, "level": "final report", "path": "OBDI02/out/OBDI02_FINAL_REPORT.md",
         "phase": classified.get("OBDI02/out/OBDI02_FINAL_REPORT.md", {}).get("phase")},
        {"rank": 7, "level": "files reconstructed after the runs",
         "path": ["OBDI02/out/_evidence.json", "OBDI02/out/_posthoc.json",
                  "OBDI02/code/analysis_obdi02.py", "OBDI02/code/figures_obdi02.py"]},
        {"rank": 8, "level": "conversational summary", "path": "not an artefact"},
    ]
    postrun = sorted(p for p, v in classified.items() if v["phase"] == "POST_RUN")
    res["HIERARCHY"] = hierarchy
    res["FILE_CLASSIFICATION"] = classified
    res["FREEZE_COMMIT"] = freeze_commit
    res["RUN_COMMIT"] = run_commit
    res["FROZEN_PROTOCOL_SOURCE_OF_TRUTH"] = "OBDI02/code/obdi02_protocol.yaml"
    res["FROZEN_ANALYSIS_SOURCE_OF_TRUTH"] = ["OBDI02/code/gate_obdi02.py",
                                              "OBDI02/code/run_obdi02.py",
                                              "OBDI02/code/worker_obdi02.py"]
    res["POSTRUN_RECONSTRUCTED_FILES"] = postrun
    res["RULE"] = ("a file at rank 7 cannot add a margin, a primary outcome, a qualification "
                   "condition, a disposition or a stopping rule. It may only report, explain "
                   "or diagnose what ranks 1-5 already fixed.")

    ok = all([res["ARCHIVE"]["ALL_PART_DIGESTS_MATCH"], res["ARCHIVE"]["WHOLE_MATCHES"],
              res["GIT"]["HEAD_MATCHES"], res["GIT"]["TREE_MATCHES"],
              res["GIT"]["ZERO_MISSING_OBJECTS"], res["GIT"]["FSCK_CLEAN"],
              res["GIT"]["PORCELAIN_EMPTY"], res["GIT"]["WORKING_COPY_TREE_MATCHES"],
              res["GIT"]["NO_IMPLICIT_FETCH"], res["ALL_REQUIRED_PRESENT"],
              res["RAW_TRAJECTORIES"]["ALL_138_PRESENT"],
              res["METHODS_CORE_HASH_REPRODUCTION"]["MATCHES"],
              res["METHODS_CORE_HASH_REPRODUCTION"]["SPEC_MATCHES"],
              res["METHODS_CORE_HASH_REPRODUCTION"][
                  "ALL_FILES_PRESENT_WITH_THE_RECORDED_DIGEST"]])
    res["PROVENANCE_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS" if ok else "PROVENANCE_FAIL")
    json.dump(res, open(f"{OUT}/_provenance.json", "w"), indent=1, default=str)

    for k, v in [("parts", "%d, all match %s" % (res["ARCHIVE"]["n_parts"],
                                                 res["ARCHIVE"]["ALL_PART_DIGESTS_MATCH"])),
                 ("whole archive", res["ARCHIVE"]["WHOLE_MATCHES"]),
                 ("HEAD", res["GIT"]["HEAD_MATCHES"]), ("tree", res["GIT"]["TREE_MATCHES"]),
                 ("missing objects", len(miss)), ("fsck", res["GIT"]["FSCK_CLEAN"]),
                 ("porcelain empty", res["GIT"]["PORCELAIN_EMPTY"]),
                 ("files", nfiles), ("commits", len(rows)),
                 ("no implicit fetch", res["GIT"]["NO_IMPLICIT_FETCH"]),
                 ("138 trajectories", res["RAW_TRAJECTORIES"]["ALL_138_PRESENT"]),
                 ("required artefacts", res["ALL_REQUIRED_PRESENT"]),
                 ("METHODS_CORE_HASH reproduced",
                  res["METHODS_CORE_HASH_REPRODUCTION"]["MATCHES"]),
                 ("spec sha256 reproduced", res["METHODS_CORE_HASH_REPRODUCTION"]["SPEC_MATCHES"]),
                 ("PROVENANCE_STATUS", res["PROVENANCE_STATUS"])]:
        print("%-32s %s" % (k, v))
    print("\nfreeze commit :", freeze_commit["commit"][:12] if freeze_commit else None,
          "| run commit :", run_commit["commit"][:12] if run_commit else None)
    print("POST_RUN files (rank 7):")
    for p in postrun:
        print("   ", p)


if __name__ == "__main__":
    main()
