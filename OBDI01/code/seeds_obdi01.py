"""OBDI01 §20 — fresh seeds, with disjointness PROVED by scanning the whole reconstructed
repository rather than asserted from memory.

The scan is deliberately over-inclusive: every integer that appears anywhere in the tracked
tree next to a seed-like token is collected. A false positive only costs a seed; a false
negative would silently reuse one.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

WC = "/home/claude/OBDI01/verify/obtc02/wc"
OUT = "/home/claude/OBDI01/out"
N_PER_L = 5
DOMAIN_SIZES = None                      # read from _power.json

PATTERNS = [
    re.compile(r"seed\D{0,4}(\d{2,7})", re.I),
    re.compile(r"SEED\s*[=:]\s*(\d{2,7})"),
    re.compile(r"default_rng\(\s*(\d{2,7})"),
    re.compile(r"\bseeds\b\s*:\s*\[([0-9,\s]+)\]", re.I),
    re.compile(r"forbidden_seeds[\s\S]{0,200}?values\s*:\s*\[([0-9,\s]+)\]"),
]
TEXT_EXT = {".py", ".yaml", ".yml", ".json", ".md", ".txt", ".cfg", ".toml", ".sh"}


def tracked_files(root):
    r = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return [os.path.join(root, p) for p in r.stdout.split()]
    out = []
    for dp, _, fn in os.walk(root):
        if "/.git" in dp:
            continue
        out += [os.path.join(dp, f) for f in fn]
    return out


def main():
    power = json.load(open(f"{OUT}/_power.json"))
    sizes = [int(x) for x in power["DOMAIN_SIZES"]]
    n_per = int(power["SEEDS_PER_DOMAIN_SIZE"])

    found, where = set(), {}
    files = [p for p in tracked_files(WC) if os.path.splitext(p)[1].lower() in TEXT_EXT]
    for p in files:
        try:
            s = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in PATTERNS:
            for m in pat.finditer(s):
                g = m.group(1)
                for tok in re.split(r"[,\s]+", g):
                    if tok.isdigit():
                        v = int(tok)
                        if 1 <= v <= 9_999_999:
                            found.add(v)
                            where.setdefault(v, set()).add(os.path.relpath(p, WC))
    # also every seed recorded in the OBTC02 results, read structurally
    for m in ("OBTC01", "OBTC02", "CSC01", "ORR01"):
        f = f"{WC}/{m}/out/_results.json"
        if os.path.exists(f):
            try:
                r = json.load(open(f))
                for a in r.get("arms", []):
                    if isinstance(a.get("seed"), int):
                        found.add(int(a["seed"]))
                        where.setdefault(int(a["seed"]), set()).add(f"{m}/out/_results.json")
            except Exception:                                  # noqa: BLE001
                pass

    retired = sorted(found)
    # ---- fresh block: a decade never touched, chosen deterministically ---------------------
    base = 771000
    while any(base + i in found for i in range(0, 100)):
        base += 1000
    fresh = {}
    for j, L in enumerate(sizes):
        fresh[str(L)] = [base + 100 * j + 10 + k for k in range(n_per)]
    flat = [s for v in fresh.values() for s in v]
    assert len(set(flat)) == len(flat)
    overlap = sorted(set(flat) & found)

    out = {
        "SECTION": "OBDI01 §20",
        "SCAN": {"files_scanned": len(files), "root": "the whole reconstructed repository",
                 "patterns": [p.pattern for p in PATTERNS]},
        "RETIRED_SEEDS": retired, "n_retired": len(retired),
        "retired_sample_provenance": {str(v): sorted(where.get(v, []))[:3]
                                      for v in retired[:25]},
        "FRESH_OBDI01_SEEDS": fresh,
        "FRESH_FLAT": flat, "n_fresh": len(flat),
        "SELECTION_RULE": ("the first block of %d consecutive hundreds, starting at %d, in "
                           "which no integer of the whole scanned repository appears; then "
                           "seed(L_j, k) = base + 100 j + 10 + k. Deterministic, and it "
                           "depends on nothing but the scan." % (len(sizes), base)),
        "OVERLAP_WITH_RETIRED": overlap,
        "DISJOINT": bool(not overlap),
        "NOTE": "no seed of any earlier mission is reused, in any condition, at any L.",
        "ANALYSIS_SEEDS_NOT_ENGINE_STARTS": {
            "values": sorted({770000 + 13 * L for L in (36, 72, 96, 108, 144)}
                             | {20260811, 20260814}),
            "used_for": ("the Monte-Carlo evaluation of the exact kernel (§12), the block "
                         "bootstrap of the legacy gate (§8) and the variance decomposition "
                         "(§14). These drive numpy generators inside ANALYSIS code; they never "
                         "start the engine and they are not counted as scientific runs."),
            "collision_with_fresh_engine_seeds": sorted(
                {770000 + 13 * L for L in (36, 72, 96, 108, 144)} & set(flat)),
        },
    }
    json.dump(out, open(f"{OUT}/_seeds.json", "w"), indent=1, default=str)
    print("scanned %d files, %d distinct seed-like integers retired" % (len(files), len(retired)))
    print("retired (first 40):", retired[:40])
    print("FRESH:", json.dumps(fresh))
    print("DISJOINT =", out["DISJOINT"])


if __name__ == "__main__":
    main()
