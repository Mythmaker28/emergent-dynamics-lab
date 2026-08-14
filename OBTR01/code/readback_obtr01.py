"""OBTR01 §29 — offline readback of the split delivery, and a harness replay from it.

Run under `unshare -rn` with GIT_NO_LAZY_FETCH=1: no network exists inside the namespace, so
nothing can arrive from a remote. The readback reassembles the parts, checks every digest,
extracts the bare repository, clones a working copy from it, and then REPLAYS the mission's own
analysis from that working copy, comparing the replayed numbers with the delivered artefacts.
A delivery that cannot reproduce its own conclusions is not a delivery.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile

D = "/home/claude/OBTR01/deliver"
V = "/home/claude/OBTR01/verify/obtr01"
OUT = "/home/claude/OBTR01/out"
BRANCH = "codex/organizer-bound-timescale-rederivation-01"
BASE = "ad8f6bfb939ddb9a5b3b5c66155a3fdf118b2b29"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}

NEED = [
    "OBTR01/out/OBTR01_FINAL_REPORT.md", "OBTR01/out/OBTR01_APPEND_ONLY_NOTES.md",
    "OBTR01/out/_provenance.json", "OBTR01/out/_mtw01_recovery.json",
    "OBTR01/out/_obdi02_deviation_closure.json", "OBTR01/out/_portability.json",
    "OBTR01/out/_corrections.json", "OBTR01/out/_kernels_operator.json",
    "OBTR01/out/_observables.json", "OBTR01/out/_timescales.json",
    "OBTR01/out/_capacity.json", "OBTR01/out/_historical_raw.json",
    "OBTR01/out/_window_rederivation.json", "OBTR01/out/_freeze.json",
    "OBTR01/out/_delivery.json", "OBTR01/out/SHA256SUMS",
    "OBTR01/out/obtr01_timescale_rederivation.png",
    "OBTR01/code/kernels_obtr01.py", "OBTR01/code/corrections_obtr01.py",
    "OBTR01/code/timescales_obtr01.py", "OBTR01/code/window_obtr01.py",
    "OBTR01/code/freeze_obtr01.py",
    "OBTR01/verify/mtw01/out/_window.json",
    "OBDCA01/out/OBDCA01_FINAL_REPORT.md", "OBDI02/out/_freeze.json",
    "OBDI02/out/_results.json", "OBTC02/out/_results.json",
]


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
    recorded = {ln.split()[1]: ln.split()[0]
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
    miss_out, _, _ = git("rev-list", "--objects", "--missing=print", "HEAD", cwd=bare)
    miss = [ln for ln in miss_out.splitlines() if ln.startswith("?")]
    _, fsck_rc, fsck_err = git("fsck", "--full", "--no-progress", cwd=bare)
    remotes, _, _ = git("remote", "-v", cwd=bare)
    shallow = (open(f"{bare}/shallow").read().strip()
               if os.path.exists(f"{bare}/shallow") else "")
    n_commits, _, _ = git("rev-list", "--count", f"{BASE}..HEAD", cwd=bare)

    subprocess.run(["git", "clone", "--quiet", "--shared", bare, f"{V}/wc"], env=ENV,
                   capture_output=True)
    wc = f"{V}/wc"
    wc_tree, _, _ = git("rev-parse", "HEAD^{tree}", cwd=wc)
    porcelain, _, _ = git("status", "--porcelain", cwd=wc)
    present = {n: os.path.exists(f"{wc}/{n}") for n in NEED}
    n_files = sum(len(f) for _, _, f in os.walk(wc) if ".git" not in _)

    # ---------------------------------------------------------------- harness replay
    replay = {}
    delivered = {n: json.load(open(f"{wc}/OBTR01/out/{n}"))
                 for n in ("_corrections.json", "_timescales.json", "_freeze.json",
                           "_window_rederivation.json", "_kernels_operator.json")
                 if os.path.exists(f"{wc}/OBTR01/out/{n}")}

    env2 = {**ENV, "PYTHONPATH": f"{wc}/OBTR01/code"}
    r = subprocess.run(
        ["python3", "-c", (
            "import sys, json, math\n"
            "sys.path.insert(0, %r)\n"
            "from kernels_obtr01 import one_step_kernel, relative_kernel, Operator, moments\n"
            "from corrections_obtr01 import mean_exit_time_discrete, c3_qmax\n"
            "q = 0.10263340389897246 / 4.0\n"
            "mu = 0.004\n"
            "K = one_step_kernel(q)\n"
            "m = moments(K)\n"
            "R = relative_kernel(q, q)\n"
            "op = Operator(q, q, mu, 36)\n"
            "fp, _ = mean_exit_time_discrete(R, 5.0)\n"
            "print(json.dumps({'a_per_axis': m['var_y'], 'mass': m['mass'],\n"
            "                  'a_rel': moments(R)['var_y'], 'G0': op.green_zero(),\n"
            "                  'lambda_max': float(op.eigenvalues().max()),\n"
            "                  'tau_shape_torus': op.shape_relaxation_time()['tau_shape'],\n"
            "                  'fp_relative': fp,\n"
            "                  'Q_max': c3_qmax()['EXACT_over_the_full_capacity_space']"
            "['Q_max']}))\n"
        ) % (f"{wc}/OBTR01/code",)],
        capture_output=True, text=True, env=env2, cwd=wc)
    try:
        got = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        got = {"error": r.stderr[-800:]}

    tau = delivered.get("_timescales.json", {})
    ker = delivered.get("_kernels_operator.json", {})
    corr = delivered.get("_corrections.json", {})
    want = {
        "a_per_axis": ker.get("KERNELS", {}).get("MOMENTS", {}).get("var_y"),
        "mass": ker.get("KERNELS", {}).get("MOMENTS", {}).get("mass"),
        "a_rel": ker.get("KERNELS", {}).get("RELATIVE_KERNEL", {}).get(
            "a_relative_closed_form"),
        "G0": ker.get("OPERATOR", {}).get("UNBLOCKED_LINEAR_OPERATOR", {}).get(
            "green_zero_relative_walk"),
        "lambda_max": ker.get("OPERATOR", {}).get("UNBLOCKED_LINEAR_OPERATOR", {}).get(
            "lambda_max"),
        "tau_shape_torus": tau.get("EIGHT_TIMESCALES", {}).get("TAU_SHAPE", {}).get(
            "TORUS_VARIANT", {}).get("value"),
        "fp_relative": tau.get("EIGHT_TIMESCALES", {}).get("TAU_FP_RELATIVE", {}).get("value"),
        "Q_max": corr.get("C3_Q_MAX", {}).get("EXACT_over_the_full_capacity_space", {}).get(
            "Q_max"),
    }
    for k, w in want.items():
        g = got.get(k)
        replay[k] = {"delivered": w, "replayed": g,
                     "MATCHES": (w is not None and g is not None
                                 and abs(float(g) - float(w)) <= 1e-9 * max(1.0, abs(float(w))))}
    replay_ok = all(v["MATCHES"] for v in replay.values())

    res = {
        "SECTION": "OBTR01 §29 — offline readback and harness replay",
        "parts": per_part, "n_parts": len(parts),
        "ALL_PARTS_MATCH": all(v["MATCHES"] for v in per_part.values()),
        "whole_sha256": whole, "whole_recorded": whole_recorded,
        "WHOLE_MATCHES": whole == whole_recorded,
        "tip": tip, "tree": tree, "working_copy_tree": wc_tree,
        "TREE_MATCHES": tree == wc_tree,
        "missing_objects": miss, "ZERO_MISSING_OBJECTS": not miss,
        "fsck_returncode": fsck_rc, "fsck_stderr": fsck_err, "FSCK_CLEAN": fsck_rc == 0,
        "remotes": remotes, "NO_REMOTE": remotes == "",
        "shallow_boundary": shallow, "BOUNDARY_IS_THE_OBDCA01_HEAD": shallow == BASE,
        "commits_since_the_base": int(n_commits or 0),
        "AT_LEAST_EIGHT_COMMITS": int(n_commits or 0) >= 8,
        "porcelain": porcelain, "PORCELAIN_EMPTY": porcelain == "",
        "files_in_working_copy": n_files,
        "mandatory_artifacts": present,
        "ALL_MANDATORY_ARTIFACTS_PRESENT": all(present.values()),
        "HARNESS_REPLAY": replay, "HARNESS_REPLAY_REPRODUCES_THE_DELIVERED_NUMBERS": replay_ok,
        "READBACK_STATUS": None,
    }
    res["READBACK_STATUS"] = ("SELF_CONTAINED_SPLIT_DELIVERY_PASS"
                              if all([res["ALL_PARTS_MATCH"], res["WHOLE_MATCHES"],
                                      res["TREE_MATCHES"], res["ZERO_MISSING_OBJECTS"],
                                      res["FSCK_CLEAN"], res["NO_REMOTE"],
                                      res["BOUNDARY_IS_THE_OBDCA01_HEAD"],
                                      res["PORCELAIN_EMPTY"],
                                      res["ALL_MANDATORY_ARTIFACTS_PRESENT"],
                                      res["AT_LEAST_EIGHT_COMMITS"], replay_ok])
                              else "SELF_CONTAINED_SPLIT_DELIVERY_FAIL")
    json.dump(res, open(f"{OUT}/_readback.json", "w"), indent=1, default=str)

    for k in ("ALL_PARTS_MATCH", "WHOLE_MATCHES", "TREE_MATCHES", "ZERO_MISSING_OBJECTS",
              "FSCK_CLEAN", "NO_REMOTE", "BOUNDARY_IS_THE_OBDCA01_HEAD", "PORCELAIN_EMPTY",
              "ALL_MANDATORY_ARTIFACTS_PRESENT", "AT_LEAST_EIGHT_COMMITS"):
        print("%-38s %s" % (k, res[k]))
    print("%-38s %d" % ("commits_since_the_base", res["commits_since_the_base"]))
    print("%-38s %d" % ("files_in_working_copy", n_files))
    missing_art = [k for k, v in present.items() if not v]
    if missing_art:
        print("MISSING ARTEFACTS: %s" % missing_art)
    print()
    print("HARNESS REPLAY, recomputed from the delivered working copy:")
    for k, v in replay.items():
        print("  %-18s delivered %-22s replayed %-22s %s"
              % (k, v["delivered"], v["replayed"], "MATCH" if v["MATCHES"] else "DIFFER"))
    print()
    print("READBACK_STATUS = %s" % res["READBACK_STATUS"])


if __name__ == "__main__":
    main()
