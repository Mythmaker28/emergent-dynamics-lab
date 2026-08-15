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

D = "/home/claude/OBFOR01/deliver"
V = "/home/claude/OBFOR01/verify/obfor01"
OUT = "/home/claude/OBFOR01/out"
BRANCH = "codex/organizer-bound-full-operator-residual-01"
BASE = "062d3735b726bb9c7325aef063c803823e46218d"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}

NEED = [
    "OBFOR01/out/OBFOR01_FINAL_REPORT.md", "OBFOR01/out/OBFOR01_APPEND_ONLY_NOTES.md",
    "OBFOR01/out/_provenance.json", "OBFOR01/out/_observables_exact.json",
    "OBFOR01/out/_residual.json", "OBFOR01/out/_m6.json", "OBFOR01/out/_mechanisms.json",
    "OBFOR01/out/_freeze.json", "OBFOR01/out/_validation.json",
    "OBFOR01/out/_adjudication.json", "OBFOR01/out/_delivery.json",
    "OBFOR01/out/SHA256SUMS", "OBFOR01/out/obfor01_operator_residual.png",
    "OBFOR01/code/residual_obfor01.py", "OBFOR01/code/m6_obfor01.py",
    "OBFOR01/code/run_obfor01.py", "OBFOR01/code/freeze_obfor01.py",
    "OBFOR01/code/adjudicate_obfor01.py",
    "OBFOR01/raw/S__seed9300000.npz", "OBFOR01/raw/M__seed9300014.npz",
    "OBTR01/out/OBTR01_FINAL_REPORT.md", "OBTR01/out/_freeze.json",
    "OBTC02/out/_results.json", "OBDI02/out/_results.json",
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
    delivered = {n: json.load(open(f"{wc}/OBFOR01/out/{n}"))
                 for n in ("_residual.json", "_m6.json", "_freeze.json",
                           "_adjudication.json", "_mechanisms.json")
                 if os.path.exists(f"{wc}/OBFOR01/out/{n}")}

    env2 = {**ENV, "PYTHONPATH": f"{wc}/OBFOR01/code"}
    r = subprocess.run(
        ["python3", "-c", (
            "import sys, json, numpy as np\n"
            "sys.path.insert(0, %r); sys.path.insert(0, %r)\n"
            "sys.path.insert(0, %r); sys.path.insert(0, %r)\n"
            "from kernels_obtr01 import Operator\n"
            "import metrics_obtc as M\n"
            "q = 0.10263340389897246/4.0; mu = 0.004; L = 36\n"
            "def pop(mob):\n"
            "    op = Operator(q, q if mob else 0.0, mu, L); pr = op.stationary_profile()\n"
            "    i = np.arange(L); d1 = np.minimum(i, L-i).astype(float)\n"
            "    d = np.sqrt(d1[:,None]**2 + d1[None,:]**2)\n"
            "    o = np.argsort(d.ravel(), kind='stable')\n"
            "    dd, ww = d.ravel()[o], pr.ravel()[o]; cw = np.cumsum(ww)/ww.sum()\n"
            "    return float(dd[int(np.searchsorted(cw, 0.8, side='left'))])\n"
            "import json, os\n"
            "val = json.load(open(%r))\n"
            "arms = [a for a in val['ARMS'] if not a['EXTINCT']]\n"
            "S = [a['r80_median'] for a in arms if a['condition']=='S']\n"
            "Mo = [a['r80_median'] for a in arms if a['condition']=='M']\n"
            "print(json.dumps({'pop_static': pop(False), 'pop_mobile': pop(True),\n"
            "  'fresh_static_median': float(np.mean(S)), 'fresh_mobile_median': float(np.mean(Mo)),\n"
            "  'fresh_ratio': float(np.mean(Mo)/np.mean(S)), 'n_arms': len(arms)}))\n"
        ) % (f"{wc}/OBTR01/code", f"{wc}/OBTC02/code", f"{wc}/ORR01/code",
             f"{wc}/OBFOR01/code", f"{wc}/OBFOR01/out/_validation.json")],
        capture_output=True, text=True, env=env2, cwd=wc)
    try:
        got = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        got = {"error": r.stderr[-800:]}
    adj = delivered.get("_adjudication.json", {})
    res = delivered.get("_residual.json", {})
    want = {
        "pop_static": res.get("PREDICTED", {}).get("static_r80"),
        "pop_mobile": res.get("PREDICTED", {}).get("mobile_r80"),
        "fresh_static_median": adj.get("OBSERVED", {}).get("S_median", {}).get("mean"),
        "fresh_mobile_median": adj.get("OBSERVED", {}).get("M_median", {}).get("mean"),
        "fresh_ratio": (adj.get("ENDPOINTS", {})
                        .get("MOBILE_STATIC_RATIO_COMPATIBILITY", {}).get("observed")),
        "n_arms": adj.get("TECHNICAL", {}).get("arms_analysable"),
    }
    for k, w in want.items():
        g = got.get(k)
        replay[k] = {"delivered": w, "replayed": g,
                     "MATCHES": (w is not None and g is not None
                                 and abs(float(g) - float(w)) <= 1e-9 * max(1.0, abs(float(w))))}
    replay_ok = all(v["MATCHES"] for v in replay.values())

    res = {
        "SECTION": "OBFOR01 §28 — offline readback and harness replay",
        "parts": per_part, "n_parts": len(parts),
        "ALL_PARTS_MATCH": all(v["MATCHES"] for v in per_part.values()),
        "whole_sha256": whole, "whole_recorded": whole_recorded,
        "WHOLE_MATCHES": whole == whole_recorded,
        "tip": tip, "tree": tree, "working_copy_tree": wc_tree,
        "TREE_MATCHES": tree == wc_tree,
        "missing_objects": miss, "ZERO_MISSING_OBJECTS": not miss,
        "fsck_returncode": fsck_rc, "fsck_stderr": fsck_err, "FSCK_CLEAN": fsck_rc == 0,
        "remotes": remotes, "NO_REMOTE": remotes == "",
        "shallow_boundary": shallow, "BOUNDARY_IS_THE_OBTR01_HEAD": shallow == BASE,
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
                                      res["BOUNDARY_IS_THE_OBTR01_HEAD"],
                                      res["PORCELAIN_EMPTY"],
                                      res["ALL_MANDATORY_ARTIFACTS_PRESENT"],
                                      res["AT_LEAST_EIGHT_COMMITS"], replay_ok])
                              else "SELF_CONTAINED_SPLIT_DELIVERY_FAIL")
    json.dump(res, open(f"{OUT}/_readback.json", "w"), indent=1, default=str)

    for k in ("ALL_PARTS_MATCH", "WHOLE_MATCHES", "TREE_MATCHES", "ZERO_MISSING_OBJECTS",
              "FSCK_CLEAN", "NO_REMOTE", "BOUNDARY_IS_THE_OBTR01_HEAD", "PORCELAIN_EMPTY",
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
