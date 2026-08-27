"""TBRT02 — the forbidden set and the fresh seed manifest, in two idempotent steps.

Inherited lesson, not relearned: the harvest is its own step, it excludes TBRT02's own subtree BY
RULE, and the generator reads the frozen file instead of re-scanning. A harvest that reads its own
output forbids its own seeds on the second run and produces a different list.

TBRT01's 3080 seeds are now INSIDE the forbidden set, because TBRT01/out survived the rollback and
sits in the repository. TBRT02 must not reuse one.
"""
from __future__ import annotations
import hashlib, json, os, re, sys
import datetime as dt

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H          # noqa: E402

SEED_SPACE = 1 << 32
SEED_KEY = re.compile(r"seed", re.I)
FNAME_SEED = re.compile(r"(?:_s|seed)(\d{1,10})")
EXCLUDED_SUBTREES = ("/.git", "/TBRT02")
EXCLUSION_RULE = ("the harvest covers everything the programme ran BEFORE TBRT02, so TBRT02's own "
                  "subtree is excluded by rule and TBRT01's is NOT. Including TBRT02's own output "
                  "would make the harvest depend on itself.")
N_BASE = 3072
N_RESERVE = 8
DERIVATION = ("seeds are drawn deterministically from SHA-256 of "
              "f'TBRT02|{parent_tip}|{counter}', taking the low 32 bits of each digest, skipping "
              "any value in the frozen forbidden set or already drawn. No randomness, no choice.")


def _walk(node, out):
    stack = [(None, node)]
    while stack:
        key, v = stack.pop()
        if isinstance(v, dict):
            for k, w in v.items():
                stack.append((k, w))
        elif isinstance(v, list):
            for w in v:
                stack.append((key, w))
        elif isinstance(v, int) and not isinstance(v, bool):
            if key and SEED_KEY.search(key) and 0 <= v < SEED_SPACE:
                out.add(v)


def harvest():
    by_source = {"repository filenames": set(), "json seed keys": set(), "jsonl seed keys": set()}
    n_json = n_jsonl = 0
    for root, dirs, files in os.walk(REPO):
        rel = "/" + os.path.relpath(root, REPO).replace(os.sep, "/")
        if rel == "/.":
            rel = "/"
        if any(rel == e or rel.startswith(e + "/") for e in EXCLUDED_SUBTREES):
            dirs[:] = []
            continue
        for f in files:
            for m in FNAME_SEED.finditer(f):
                v = int(m.group(1))
                if 0 <= v < SEED_SPACE:
                    by_source["repository filenames"].add(v)
            p = os.path.join(root, f)
            try:
                if f.endswith(".json"):
                    _walk(json.load(open(p)), by_source["json seed keys"]); n_json += 1
                elif f.endswith(".jsonl"):
                    n_jsonl += 1
                    for line in open(p):
                        if line.strip():
                            _walk(json.loads(line), by_source["jsonl seed keys"])
            except Exception:
                pass
    forbidden = sorted(set().union(*by_source.values()))
    doc = {"MISSION": "TBRT02", "SECTION": "frozen forbidden seed set",
           "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
           "EXCLUDED_SUBTREES": list(EXCLUDED_SUBTREES), "EXCLUSION_RULE": EXCLUSION_RULE,
           "N_JSON_FILES_READ": n_json, "N_JSONL_FILES_READ": n_jsonl,
           "COUNTS_BY_SOURCE": {k: len(v) for k, v in by_source.items()},
           "N_FORBIDDEN": len(forbidden), "FORBIDDEN": forbidden}
    doc["FORBIDDEN_SET_HASH"] = H.canonical_digest(forbidden)
    doc["FORBIDDEN_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("FORBIDDEN_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/TBRT02/out/TBRT02_FORBIDDEN_SEEDS.json", "w"), indent=1)
    return doc


def generate(parent_tip):
    fb = json.load(open(f"{REPO}/TBRT02/out/TBRT02_FORBIDDEN_SEEDS.json"))
    forbidden = set(fb["FORBIDDEN"])
    seen, base, reserve, c = set(), [], [], 0
    while len(base) + len(reserve) < N_BASE + N_RESERVE:
        d = hashlib.sha256(f"TBRT02|{parent_tip}|{c}".encode()).hexdigest()
        v = int(d[-8:], 16)
        c += 1
        if v in forbidden or v in seen:
            continue
        seen.add(v)
        (base if len(base) < N_BASE else reserve).append({"index": len(base) + len(reserve),
                                                          "seed": v, "counter": c - 1})
    doc = {"MISSION": "TBRT02", "SECTION": "frozen seed manifest",
           "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
           "PARENT_TIP": parent_tip, "DERIVATION": DERIVATION,
           "N_BASE": len(base), "N_RESERVE": len(reserve), "COUNTERS_CONSUMED": c,
           "FORBIDDEN_SET_HASH": fb["FORBIDDEN_SET_HASH"], "N_FORBIDDEN": fb["N_FORBIDDEN"],
           "DISJOINT_FROM_THE_FORBIDDEN_SET":
               not (set(s["seed"] for s in base + reserve) & forbidden),
           "NO_DUPLICATE_WITHIN_THE_MANIFEST":
               len({s["seed"] for s in base + reserve}) == len(base) + len(reserve),
           "RESERVES_ARE_TECHNICAL_ONLY": "a technical retry reuses the identical seed and arm. A "
               "scientific non-trigger consumes its seed and is NEVER replaced.",
           "BASE_SEEDS": base, "RESERVE_SEEDS": reserve}
    doc["SEED_SET_HASH"] = H.canonical_digest([s["seed"] for s in base])
    doc["SEED_MANIFEST_CONTENT_HASH"] = H.content_digest(
        doc, extra_excluded=("SEED_MANIFEST_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/TBRT02/out/TBRT02_SEED_MANIFEST.json", "w"), indent=1)
    return doc


if __name__ == "__main__":
    if sys.argv[1] == "harvest":
        d = harvest()
        print("forbidden seeds:", d["N_FORBIDDEN"], " by source:", d["COUNTS_BY_SOURCE"])
        print("FORBIDDEN_SET_HASH =", d["FORBIDDEN_SET_HASH"])
    else:
        d = generate(sys.argv[2])
        print("base:", d["N_BASE"], "reserve:", d["N_RESERVE"], "counters:", d["COUNTERS_CONSUMED"])
        print("disjoint:", d["DISJOINT_FROM_THE_FORBIDDEN_SET"],
              " no dupes:", d["NO_DUPLICATE_WITHIN_THE_MANIFEST"])
        print("SEED_SET_HASH =", d["SEED_SET_HASH"])
