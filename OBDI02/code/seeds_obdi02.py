"""OBDI02 §10 — retired seeds and fresh seeds.

The scan runs over the whole reconstructed repository, which contains every mission of the
chain: MINCORE, MTW01, MCM01, ORR01, CSC01, OBTC01, OBTC02, OBDI01. Every fresh seed is
assigned to its domain size BEFORE any run, and no replacement is permitted for any reason.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"
SIZES = (36, 72, 96)

PATTERNS = [
    re.compile(r"seed\D{0,4}(\d{2,9})", re.I),
    re.compile(r"SEED\s*[=:]\s*(\d{2,9})"),
    re.compile(r"default_rng\(\s*(\d{2,9})"),
    re.compile(r"\bseeds\b\s*:\s*\[([0-9,\s]+)\]", re.I),
    re.compile(r"forbidden_seeds[\s\S]{0,300}?values\s*:\s*\[([0-9,\s]+)\]"),
    re.compile(r"\"seed\"\s*:\s*(\d{2,9})"),
]
TEXT_EXT = {".py", ".yaml", ".yml", ".json", ".md", ".txt", ".cfg", ".toml", ".sh"}
MISSIONS = ("MINCORE", "MTW01", "MCM01", "ORR01", "CSC01", "OBTC01", "OBTC02", "OBDI01")


def tracked(root):
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
    pw = json.load(open(f"{OUT}/_plan_inputs.json"))
    n_per = int(pw["SEEDS_PER_SIZE"])

    found, where = set(), {}
    files = [p for p in tracked(WC) if os.path.splitext(p)[1].lower() in TEXT_EXT]
    for p in files:
        try:
            s = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in PATTERNS:
            for m in pat.finditer(s):
                for tok in re.split(r"[,\s]+", m.group(1)):
                    if tok.isdigit():
                        v = int(tok)
                        if 1 <= v <= 999_999_999:
                            found.add(v)
                            where.setdefault(v, set()).add(os.path.relpath(p, WC))
    for m in MISSIONS:
        f = f"{WC}/{m}/out/_results.json"
        if os.path.exists(f):
            try:
                r = json.load(open(f))
                for a in (r.get("arms") or []):
                    if isinstance(a.get("seed"), int):
                        found.add(int(a["seed"]))
                        where.setdefault(int(a["seed"]), set()).add(f"{m}/out/_results.json")
            except Exception:                                     # noqa: BLE001
                pass
    for f in (f"{WC}/OBDI01/out/_arms.json",):
        if os.path.exists(f):
            for a in json.load(open(f)):
                found.add(int(a["seed"]))
                where.setdefault(int(a["seed"]), set()).add("OBDI01/out/_arms.json")
    retired = sorted(found)

    # a block of consecutive integers untouched by the whole scan, chosen deterministically
    span = n_per * len(SIZES) + 200
    base = 8_100_000
    while any(base + i in found for i in range(span)):
        base += 100_000
    fresh = {str(L): [base + 1000 * j + k for k in range(n_per)]
             for j, L in enumerate(SIZES)}
    flat = [s for v in fresh.values() for s in v]
    assert len(set(flat)) == len(flat)
    overlap = sorted(set(flat) & found)

    per_mission = {}
    for m in MISSIONS:
        per_mission[m] = sorted({v for v in retired
                                 if any(w.startswith(m + "/") for w in where.get(v, ()))})

    out = {
        "SECTION": "OBDI02 §10",
        "SCAN": {"root": "the whole reconstructed OBDI01 delivery",
                 "files_scanned": len(files), "patterns": [p.pattern for p in PATTERNS],
                 "missions_covered": list(MISSIONS)},
        "RETIRED_SEEDS": retired, "n_retired": len(retired),
        "RETIRED_BY_MISSION": {k: v for k, v in per_mission.items() if v},
        "FRESH_OBDI02_SEEDS": fresh, "FRESH_FLAT": flat, "n_fresh": len(flat),
        "SEEDS_PER_SIZE": n_per,
        "SELECTION_RULE": ("the first block of %d consecutive integers from %d in which no "
                           "integer of the whole scanned repository appears, then "
                           "seed(L_j, k) = base + 1000 j + k. Deterministic, and dependent on "
                           "nothing but the scan." % (span, 8_100_000)),
        "OVERLAP_WITH_RETIRED": overlap, "DISJOINT": not overlap,
        "ASSIGNED_BEFORE_ANY_RUN": True,
        "NO_REPLACEMENT_RULE": ("no fresh seed may be replaced after an extinction, a "
                                "scientific failure, an atypical result, an engine crash or a "
                                "result close to the margin. A consumed seed stays consumed."),
    }
    json.dump(out, open(f"{OUT}/_seeds.json", "w"), indent=1, default=str)
    print("files scanned %d   retired seeds %d" % (len(files), len(retired)))
    print("retired by mission:", {k: len(v) for k, v in out["RETIRED_BY_MISSION"].items()})
    print("fresh: %d per size, base %d" % (n_per, flat[0]))
    for L in SIZES:
        v = fresh[str(L)]
        print("   L=%-3d %d..%d" % (L, v[0], v[-1]))
    print("DISJOINT =", out["DISJOINT"])


if __name__ == "__main__":
    main()
