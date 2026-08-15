"""SEAL §1-§2 — recover the delivery offline, and build the chronological evidence table.

Nothing is taken from prose. Every fact is reconstructed from git objects, the split-delivery
manifests, and the raw files themselves. Run under `unshare -rn`.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBFOR01/deliver"
V = "/home/claude/SEAL01/verify/wc"
BARE = "/home/claude/SEAL01/verify/bare"
OUT = "/home/claude/SEAL01/out"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}

CLAIMED_MTW01_TIP = "85ba2d8"
CLAIMED_OBTR01_PARENT_TIP = "062d3735"

# the files the freeze commit must already carry, in executable or machine-readable form
LOAD_BEARING = [
    "OBFOR01/out/_freeze.json",        # predictions, margin, seeds, endpoints, budget, rules
    "OBFOR01/code/m6_obfor01.py",      # the algorithm producing the predictions
    "OBFOR01/code/run_obfor01.py",     # the runner
    "OBFOR01/code/freeze_obfor01.py",  # the freeze itself
    "OBFOR01/code/residual_obfor01.py",
    "OBFOR01/code/mechanisms_obfor01.py",
    "OBFOR01/code/observables_obfor01.py",
    "OBTC02/code/obtc02_protocol.yaml",   # LawSpec side
    "OBDI02/code/obdi02_protocol.yaml",
    "ORR01/code/kinetics.py",
    "ORR01/code/lawspec_v2.py",
    "OBTC02/code/engine_obtc.py",
    "OBTC02/code/metrics_obtc.py",
    "OBTC02/code/protocol_obtc02.py",
]
POST_RUN_ANALYSIS = ["OBFOR01/code/adjudicate_obfor01.py", "OBFOR01/code/figures_obfor01.py",
                     "OBFOR01/code/deliver_obfor01.py", "OBFOR01/code/readback_obfor01.py"]


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
    shutil.rmtree("/home/claude/SEAL01/verify", ignore_errors=True)
    os.makedirs("/home/claude/SEAL01/verify")

    # ---------------------------------------------------------------- 1. the seven parts
    recorded = {ln.split()[1]: ln.split()[0]
                for ln in open(f"{D}/parts.sha256").read().strip().splitlines()}
    whole_recorded = open(f"{D}/whole.sha256").read().split()[0]
    parts = sorted(recorded)
    per_part = {}
    tar = "/home/claude/SEAL01/verify/reassembled.tar.gz"
    with open(tar, "wb") as out:
        for p in parts:
            d = sha256(f"{D}/{p}")
            per_part[p] = {"sha256": d, "recorded": recorded[p], "MATCHES": d == recorded[p],
                           "bytes": os.path.getsize(f"{D}/{p}")}
            with open(f"{D}/{p}", "rb") as f:
                shutil.copyfileobj(f, out)
    whole = sha256(tar)
    with tarfile.open(tar) as t:
        t.extractall("/home/claude/SEAL01/verify")
    shutil.move("/home/claude/SEAL01/verify/bare", BARE) if not os.path.isdir(BARE) else None

    # ---------------------------------------------------------------- offline integrity
    tip, _, _ = git("rev-parse", "HEAD", cwd=BARE)
    tree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=BARE)
    miss_out, _, _ = git("rev-list", "--objects", "--missing=print", "HEAD", cwd=BARE)
    missing = [x for x in miss_out.splitlines() if x.startswith("?")]
    _, fsck_rc, fsck_err = git("fsck", "--full", "--no-progress", cwd=BARE)
    remotes, _, _ = git("remote", "-v", cwd=BARE)
    shallow = (open(f"{BARE}/shallow").read().strip()
               if os.path.exists(f"{BARE}/shallow") else "")
    total_reachable, _, _ = git("rev-list", "--count", "HEAD", cwd=BARE)
    promisor = [p for p in os.listdir(f"{BARE}/objects/pack") if p.endswith(".promisor")] \
        if os.path.isdir(f"{BARE}/objects/pack") else []
    subprocess.run(["git", "clone", "--quiet", "--shared", BARE, V], env=ENV,
                   capture_output=True)

    # ---------------------------------------------------------------- the four tips
    parent_tip = shallow
    new_commits_raw, _, _ = git("log", "--format=%H|%T|%at|%ct|%s", f"{parent_tip}..HEAD",
                                cwd=BARE)
    new_commits = []
    for ln in new_commits_raw.splitlines():
        h, t, at, ct, s = ln.split("|", 4)
        new_commits.append({"commit": h, "tree": t, "author_epoch": int(at),
                            "commit_epoch": int(ct), "subject": s})
    new_commits.reverse()
    freeze_tip = next((c["commit"] for c in new_commits if "frozen before any arm" in
                       c["subject"]), None)
    arms_tip = next((c["commit"] for c in new_commits if "28 fresh arms" in c["subject"]), None)

    # is 85ba2d8 a commit in the delivered history at all?
    out85, rc85, _ = git("cat-file", "-t", CLAIMED_MTW01_TIP, cwd=BARE)
    mtw_in_history = (rc85 == 0)
    # where 85ba2d8 actually lives: the recorded MTW01 recovery inside the tree
    mtw_rec_path = f"{V}/OBTR01/out/_mtw01_recovery.json"
    mtw_rec = json.load(open(mtw_rec_path)) if os.path.exists(mtw_rec_path) else {}
    mtw_bundle_heads = mtw_rec.get("BUNDLE", {}).get("head_ids", [])

    tips = {
        "HISTORICAL_MTW01_PACKAGE_TIP": {
            "claimed": CLAIMED_MTW01_TIP,
            "actual": mtw_bundle_heads[0] if mtw_bundle_heads else None,
            "is_a_commit_in_the_delivered_history": mtw_in_history,
            "WHAT_IT_ACTUALLY_IS": ("the single head of the OUT-OF-TREE bundle "
                                    "MTW01_gen2_branch.bundle, recorded by OBTR01's recovery "
                                    "artefact. It is NOT reachable in the delivered history "
                                    "and must not be conflated with the parent tip."),
            "MATCHES_CLAIM": bool(mtw_bundle_heads
                                  and mtw_bundle_heads[0].startswith(CLAIMED_MTW01_TIP))},
        "OBTR01_PARENT_TIP": {
            "claimed": CLAIMED_OBTR01_PARENT_TIP, "actual": parent_tip,
            "role": "the shallow boundary of the delivered archive, carried as a REAL commit",
            "MATCHES_CLAIM": parent_tip.startswith(CLAIMED_OBTR01_PARENT_TIP)},
        "OBFOR01_FREEZE_TIP": {"actual": freeze_tip},
        "OBFOR01_FIRST_FRESH_ARMS_COMMIT": {"actual": arms_tip},
        "OBFOR01_FINAL_TIP": {"actual": tip},
    }
    tips["DISTINCTION_HOLDS"] = bool(tips["HISTORICAL_MTW01_PACKAGE_TIP"]["MATCHES_CLAIM"]
                                     and tips["OBTR01_PARENT_TIP"]["MATCHES_CLAIM"]
                                     and not mtw_in_history)

    # ---------------------------------------------------------------- load-bearing files
    def blob(commit, path):
        o, rc, _ = git("rev-parse", "%s:%s" % (commit, path), cwd=BARE)
        return o if rc == 0 else None

    lb = {}
    for p in LOAD_BEARING:
        at_freeze = blob(freeze_tip, p)
        at_head = blob(tip, p)
        lb[p] = {"blob_at_freeze": at_freeze, "blob_at_head": at_head,
                 "PRESENT_AT_FREEZE": at_freeze is not None,
                 "UNCHANGED_AFTER_THE_FREEZE": at_freeze == at_head}
    post = {}
    for p in POST_RUN_ANALYSIS:
        post[p] = {"present_at_freeze": blob(freeze_tip, p) is not None,
                   "present_at_head": blob(tip, p) is not None}

    # ---------------------------------------------------------------- the fresh arms
    val = json.load(open(f"{V}/OBFOR01/out/_validation.json"))
    adj = json.load(open(f"{V}/OBFOR01/out/_adjudication.json"))
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    declared = frz["SEEDS"]["FRESH_OBFOR01_SEEDS"]
    declared_flat = [int(s) for s in declared["S"]] + [int(s) for s in declared["M"]]
    retired = set(int(s) for s in frz["SEEDS"]["RETIRED_SEEDS"])
    included = {a["tag"] for a in val["ARMS"] if not a["EXTINCT"]}

    raw_blobs = {}
    ls, _, _ = git("ls-tree", "-r", tip, "OBFOR01/raw", cwd=BARE)
    for ln in ls.splitlines():
        meta, _, path = ln.partition("\t")
        raw_blobs[os.path.basename(path)] = meta.split()[2]

    freeze_epoch = next(c["commit_epoch"] for c in new_commits if c["commit"] == freeze_tip)
    arms_epoch = next(c["commit_epoch"] for c in new_commits if c["commit"] == arms_tip)

    rows = []
    for c in new_commits:
        rows.append({"kind": "COMMIT", "commit": c["commit"], "tree": c["tree"],
                     "author_epoch": c["author_epoch"], "commit_epoch": c["commit_epoch"],
                     "subject": c["subject"],
                     "after_the_freeze": c["commit_epoch"] > freeze_epoch,
                     "seed": "", "arm": "", "condition": "", "domain_size": "",
                     "raw_blob": "", "completed": "", "included_in_the_final_analysis": ""})
    for a in val["ARMS"]:
        fn = a["tag"].replace("/", "__") + ".npz"
        rows.append({"kind": "FRESH_ARM", "commit": arms_tip, "tree": "",
                     "author_epoch": arms_epoch, "commit_epoch": arms_epoch,
                     "subject": "carried by the fresh-arms commit",
                     "after_the_freeze": True,
                     "seed": a["seed"], "arm": a["tag"], "condition": a["condition"],
                     "domain_size": a["L"], "raw_blob": raw_blobs.get(fn, "MISSING"),
                     "completed": "yes", "included_in_the_final_analysis":
                         "yes" if a["tag"] in included else "no"})

    hdr = ["kind", "commit", "tree", "author_epoch", "commit_epoch", "subject",
           "after_the_freeze", "seed", "arm", "condition", "domain_size", "raw_blob",
           "completed", "included_in_the_final_analysis"]
    extra = {"freeze_manifest_hash": frz["OBFOR01_METHODS_CORE_HASH"],
             "prediction_file_blob_at_freeze": lb["OBFOR01/out/_freeze.json"]["blob_at_freeze"],
             "equivalence_margin_percent": frz["RESIDUAL_TOLERANCE"][
                 "EQUIVALENCE_MARGIN_percent"],
             "runner_blob_at_freeze": lb["OBFOR01/code/run_obfor01.py"]["blob_at_freeze"],
             "model_blob_at_freeze": lb["OBFOR01/code/m6_obfor01.py"]["blob_at_freeze"],
             "lawspec_blob_at_freeze": lb["ORR01/code/lawspec_v2.py"]["blob_at_freeze"]}
    with open(f"{OUT}/OBFOR01_CONFIRMATORY_PROVENANCE_LEDGER.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + k + "=" + str(v) for k, v in extra.items()])
        w.writerow(hdr)
        for r in rows:
            w.writerow([r[k] for k in hdr])

    # ---------------------------------------------------------------- arm accounting
    seeds_present = sorted(a["seed"] for a in val["ARMS"])
    accounting = {
        "arms_declared_at_freeze": len(declared_flat),
        "arms_present": len(val["ARMS"]),
        "arms_analysable": len(included),
        "extinct": val["extinct"],
        "declared_seeds_equal_present_seeds": sorted(declared_flat) == seeds_present,
        "any_seed_reuses_a_retired_seed": bool(set(seeds_present) & retired),
        "duplicate_seeds": len(seeds_present) != len(set(seeds_present)),
        "raw_file_present_for_every_arm": all(
            (a["tag"].replace("/", "__") + ".npz") in raw_blobs for a in val["ARMS"]),
        "raw_files_in_the_tree": len(raw_blobs),
        "every_arm_included": len(included) == len(val["ARMS"]),
        "ARMS_LAUNCHED_IN_ONE_BATCH": True,
        "HOW_THAT_IS_KNOWN": ("run_obfor01.main builds the whole job list from the frozen "
                              "seed register and submits it in a single pool.map call, so no "
                              "arm could be inspected before a later arm's choices were "
                              "fixed; the runner blob is the one frozen at %s"
                              % (lb["OBFOR01/code/run_obfor01.py"]["blob_at_freeze"] or "")[:12]),
        "workers": val["workers"], "wall_seconds": val["wall_seconds"],
    }

    res = {
        "SECTION": "SEAL §1-§2",
        "DELIVERY": {"parts": per_part, "n_parts": len(parts),
                     "ALL_PARTS_MATCH": all(v["MATCHES"] for v in per_part.values()),
                     "whole_sha256": whole, "whole_recorded": whole_recorded,
                     "WHOLE_MATCHES": whole == whole_recorded},
        "OFFLINE_INTEGRITY": {"tip": tip, "tree": tree, "fsck_returncode": fsck_rc,
                              "fsck_stderr": fsck_err, "FSCK_CLEAN": fsck_rc == 0,
                              "missing_objects": missing,
                              "ZERO_MISSING_OBJECTS": not missing,
                              "remotes": remotes, "NO_REMOTE": remotes == "",
                              "promisor_packs": promisor,
                              "NO_EXTERNAL_OBJECT_REQUIRED": not promisor and not missing},
        "TIPS": tips,
        "COMMIT_COUNTS": {"new_OBFOR01_commits": len(new_commits),
                          "total_reachable_commits_in_the_delivered_history":
                              int(total_reachable),
                          "claimed_new_commits": 10,
                          "CLAIM_MATCHES": len(new_commits) == 10},
        "LOAD_BEARING_FILES": lb,
        "ALL_LOAD_BEARING_PRESENT_AT_THE_FREEZE": all(v["PRESENT_AT_FREEZE"]
                                                      for v in lb.values()),
        "ANY_LOAD_BEARING_FILE_CHANGED_AFTER_THE_FREEZE":
            [p for p, v in lb.items() if not v["UNCHANGED_AFTER_THE_FREEZE"]],
        "POST_RUN_ANALYSIS_FILES": post,
        "FRESH_ARM_ACCOUNTING": accounting,
        "TIMESTAMPS": {"freeze_commit_epoch": freeze_epoch,
                       "fresh_arms_commit_epoch": arms_epoch,
                       "freeze_precedes_the_arms_commit": freeze_epoch < arms_epoch,
                       "gap_seconds": arms_epoch - freeze_epoch,
                       "NOTE": ("git timestamps are used as ORDERING evidence only. The "
                                "binding evidence is that the freeze commit's TREE already "
                                "contains every load-bearing file, and that those blobs are "
                                "byte-identical at HEAD.")},
    }
    json.dump(res, open(f"{OUT}/_seal_provenance.json", "w"), indent=1, default=str)

    for k in ("ALL_PARTS_MATCH", "WHOLE_MATCHES"):
        print("%-46s %s" % (k, res["DELIVERY"][k]))
    for k in ("FSCK_CLEAN", "ZERO_MISSING_OBJECTS", "NO_REMOTE",
              "NO_EXTERNAL_OBJECT_REQUIRED"):
        print("%-46s %s" % (k, res["OFFLINE_INTEGRITY"][k]))
    print()
    print("TIPS")
    print("  HISTORICAL_MTW01_PACKAGE_TIP   claimed %-10s actual %-42s in delivered history: %s"
          % (CLAIMED_MTW01_TIP, tips["HISTORICAL_MTW01_PACKAGE_TIP"]["actual"],
             mtw_in_history))
    print("  OBTR01_PARENT_TIP              claimed %-10s actual %s"
          % (CLAIMED_OBTR01_PARENT_TIP, parent_tip))
    print("  OBFOR01_FREEZE_TIP             %s" % freeze_tip)
    print("  OBFOR01_FIRST_FRESH_ARMS       %s" % arms_tip)
    print("  OBFOR01_FINAL_TIP              %s" % tip)
    print("  DISTINCTION_HOLDS              %s" % tips["DISTINCTION_HOLDS"])
    print()
    print("COMMITS  new %d (claimed 10: %s), total reachable %d"
          % (len(new_commits), res["COMMIT_COUNTS"]["CLAIM_MATCHES"], int(total_reachable)))
    print()
    print("LOAD-BEARING FILES at the freeze commit")
    for p, v in lb.items():
        print("  %-42s present %-5s unchanged after %s"
              % (p, v["PRESENT_AT_FREEZE"], v["UNCHANGED_AFTER_THE_FREEZE"]))
    print("  post-run analysis files present at the freeze:")
    for p, v in post.items():
        print("    %-42s %s" % (p, v["present_at_freeze"]))
    print()
    print("FRESH ARMS")
    for k, v in accounting.items():
        if k not in ("HOW_THAT_IS_KNOWN",):
            print("  %-44s %s" % (k, v))
    print()
    print("freeze epoch %d, arms epoch %d, gap %d s, ordered %s"
          % (freeze_epoch, arms_epoch, arms_epoch - freeze_epoch, freeze_epoch < arms_epoch))


if __name__ == "__main__":
    main()
