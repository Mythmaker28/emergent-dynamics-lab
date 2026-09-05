"""OMLDCT02 — the frozen forbidden-seed set.

The first version of the seed generator harvested the forbidden set from the repository at
generation time. It was NOT reproducible, and the reason is worth recording: once the generator had
written OMLDCT02_SEED_MANIFEST.json, that file sat in the repository with its own seeds under keys
containing the word 'seed', so the next run treated OMLDCT02's own seeds as forbidden and produced a
completely different list. A self-poisoning harvest.

Caught before C1, and fixed structurally rather than patched: the harvest is now its own committed
step producing its own frozen artefact, the harvest excludes OMLDCT02's own directory by rule, and
the seed generator reads the frozen file instead of re-scanning. Both steps are then idempotent.
"""
from __future__ import annotations
import json, os, re, sys, datetime

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H

SEED_SPACE = 1 << 32
SEED_KEY = re.compile(r"seed", re.I)
FNAME_SEED = re.compile(r"(?:_s|seed)(\d{1,10})")
EXCLUDED_SUBTREES = ("/.git", "/OMLDCT02")
EXCLUSION_RULE = ("the harvest covers everything the programme ran BEFORE OMLDCT02, so OMLDCT02's "
                  "own subtree is excluded by rule. Including it would make the harvest depend on "
                  "its own output, which is exactly the defect this file was written to remove.")

def _walk(node, out):
    stack = [(None, node)]
    while stack:
        key, v = stack.pop()
        if isinstance(v, dict):
            for k, w in v.items(): stack.append((k, w))
        elif isinstance(v, list):
            for w in v: stack.append((key, w))
        elif isinstance(v, int) and not isinstance(v, bool):
            if key and SEED_KEY.search(key) and 0 <= v < SEED_SPACE: out.add(v)

def harvest(extra_files=()):
    by_source = {"repository filenames": set(), "json seed keys": set()}
    n_json = 0
    for root, dirs, files in os.walk(REPO):
        rel = "/" + os.path.relpath(root, REPO).replace(os.sep, "/")
        if rel == "/.": rel = "/"
        if any(rel == e or rel.startswith(e + "/") for e in EXCLUDED_SUBTREES):
            dirs[:] = []; continue
        dirs[:] = [d for d in dirs
                   if not any((rel.rstrip("/") + "/" + d) == e for e in EXCLUDED_SUBTREES)]
        for f in files:
            m = FNAME_SEED.search(f)
            if m:
                v = int(m.group(1))
                if 0 <= v < SEED_SPACE: by_source["repository filenames"].add(v)
            if f.endswith(".json"):
                n_json += 1
                try:
                    with open(os.path.join(root, f)) as fh: doc = json.load(fh)
                except Exception: continue
                _walk(doc, by_source["json seed keys"])
    for ef in extra_files:
        if os.path.exists(ef):
            with open(ef) as fh:
                s = {int(x) for x in fh.read().split() if x.isdigit() and int(x) < SEED_SPACE}
            by_source[os.path.basename(ef)] = s
    return by_source, n_json

def main():
    dev = os.path.join(REPO, "OMLDCT02", "work", "DEVICE_ARCHIVE_SEEDS.txt")
    by_source, n_json = harvest([dev])
    allsee = sorted(set().union(*by_source.values()))
    doc = {
     "MISSION": "OMLDCT02", "SECTION": "frozen forbidden-seed set",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "GENERATOR": "OMLDCT02/code/omldct02_forbidden_seeds.py",
     "WHY_THIS_IS_A_SEPARATE_FROZEN_STEP": __doc__.strip(),
     "RULE": "a deliberate superset. Every integer in [0, 2**32) under any key containing 'seed' in "
             "any JSON in the repository, every _s<digits> or seed<digits> token in any filename in "
             "the repository, and every such token in every .npz filename on the Windows device. "
             "Over-excluding costs nothing; under-excluding would let OMLDCT02 reuse a seed whose "
             "outcome is already known somewhere in the programme.",
     "EXCLUDED_SUBTREES": list(EXCLUDED_SUBTREES), "EXCLUSION_RULE": EXCLUSION_RULE,
     "JSON_FILES_SCANNED": n_json,
     "COUNT_BY_SOURCE": {k: len(v) for k, v in by_source.items()},
     "SIZE": len(allsee),
     "FORBIDDEN_SEEDS": allsee,
    }
    doc["FORBIDDEN_SET_HASH"] = H.canonical_digest(allsee)
    doc["FORBIDDEN_SET_HASH_RULE"] = "H.canonical_digest of the ascending list of distinct integers."
    json.dump(doc, open(f"{REPO}/OMLDCT02/out/OMLDCT02_FORBIDDEN_SEEDS.json", "w"), indent=1)
    print("size", doc["SIZE"], "by source", doc["COUNT_BY_SOURCE"], f"({n_json} json scanned)")
    print("FORBIDDEN_SET_HASH =", doc["FORBIDDEN_SET_HASH"])

if __name__ == "__main__":
    main()
