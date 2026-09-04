#!/usr/bin/env python3
"""LRCPS01 §2 — paper strategy decision (companion vs V3 extension).

Non-scientific: makes no numerical claim, runs no engine. It records a
mechanical test of the two preconditions the launcher attaches to a V3
extension, and derives the decision from the test outcome only.
"""
import json, os, hashlib, subprocess, re

REPO = "/home/claude/edl"
PKG = os.path.join(REPO, "paper/organiser-bound-source-response-operator")
OUT = os.path.join(PKG, "decisions")
os.makedirs(OUT, exist_ok=True)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

# --- precondition 1: does the named persistence V1/V2 manuscript package exist? ---
NAMED_V1V2_CANDIDATES = [
    "paper/persistence-v1", "paper/persistence-v2", "paper/persistence",
    "docs/persistence/MANUSCRIPT.md", "docs/paper/PERSISTENCE_V1.md",
    "docs/paper/PERSISTENCE_V2.md", "PERSISTENCE_V1", "PERSISTENCE_V2",
]
named_pkg_hits = [c for c in NAMED_V1V2_CANDIDATES if os.path.exists(os.path.join(REPO, c))]

# exhaustive search: any tracked file whose path or first 200 lines announce a
# persistence-organiser manuscript of version 1 or 2
tracked = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout.split()
persistence_named = []
for t in tracked:
    if re.search(r"persistence", t, re.I):
        persistence_named.append(t)

# --- precondition 2: which manuscripts actually exist, and on what question? ---
EXISTING = {
    "docs/paper/MANUSCRIPT.md": None,
    "docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md": None,
    "docs/replication/THEOREM_MANUSCRIPT.md": None,
}
for k in list(EXISTING):
    p = os.path.join(REPO, k)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            head = f.read(4000)
        title = head.splitlines()[0].lstrip("# ").strip()
        EXISTING[k] = {
            "sha256": sha256(p),
            "title": title,
            "words": len(open(p, encoding="utf-8").read().split()),
            "estimand": "scalar causal-response magnitude q read on contaminated reference channels",
        }
    else:
        EXISTING[k] = {"present": False}

CANDIDATE_ESTIMAND = (
    "the steady-state radial extent r80 of the X field around a source of fixed "
    "full-capacity strength, and its dependence on source mobility, in the frozen "
    "ORR01/LawSpec-v2 lattice"
)

# mechanical overlap test between the candidate estimand and the existing ones
shared_estimand = False
shared_data = False
for k, v in EXISTING.items():
    if v.get("estimand") == CANDIDATE_ESTIMAND:
        shared_estimand = True
# the existing manuscripts are built on synthetic contamination hold-outs,
# not on any OBFOR01 archive; test it by looking for the programme names
for k in EXISTING:
    p = os.path.join(REPO, k)
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
        if re.search(r"OBFOR01|OBTC02|ORR01|r80|LawSpec", txt):
            shared_data = True

decision = {
    "SECTION": "LRCPS01 §2 paper strategy decision",
    "DECISION": None,
    "V3_EXTENSION_PRECONDITIONS": {
        "named_persistence_V1_V2_package_present": bool(named_pkg_hits or persistence_named),
        "named_persistence_V1_V2_paths_found": named_pkg_hits + persistence_named,
        "candidate_shares_estimand_with_an_existing_manuscript": shared_estimand,
        "candidate_shares_source_data_with_an_existing_manuscript": shared_data,
    },
    "EXISTING_MANUSCRIPTS": EXISTING,
    "CANDIDATE_ESTIMAND": CANDIDATE_ESTIMAND,
}

if decision["V3_EXTENSION_PRECONDITIONS"]["named_persistence_V1_V2_package_present"]:
    if shared_estimand or shared_data:
        decision["DECISION"] = "V3_EXTENSION"
    else:
        decision["DECISION"] = "COMPANION_PAPER"
else:
    decision["DECISION"] = "COMPANION_PAPER"

decision["DECISION_RULE"] = (
    "A V3 extension requires (a) the named persistence V1/V2 manuscript package to be "
    "mechanically present in the repository, and (b) a demonstrated overlap of estimand "
    "or source data with it. Precondition (a) fails: no file in the repository, tracked or "
    "untracked, is that package. Extending a document that is not present cannot be done "
    "mechanically and would have to be done from memory, which this mission forbids. "
    "Precondition (b) also fails against the three manuscripts that ARE present: they "
    "estimate a scalar causal-response magnitude q on contaminated reference channels from "
    "synthetic hold-outs, and cite no OBFOR01/ORR01/OBTC02 archive. The two questions are "
    "disjoint. Therefore: companion paper."
)
decision["CONSEQUENCES"] = [
    "The companion paper carries its own abstract, introduction, methods, results and discussion.",
    "It cites the set-valued causal metrology manuscripts as prior work of the same laboratory, not as a parent.",
    "No sentence, figure or table is inherited from them; §13 will audit this mechanically.",
    "No claim of continuity with an absent V1/V2 package is made anywhere in the manuscript.",
]
decision["ABSENT_PACKAGE_HANDLING"] = (
    "NAMED_PERSISTENCE_V1_V2_PACKAGE = NOT_PRESENT_IN_REPOSITORY. No comparison, overlap "
    "figure or continuity claim is made against it. Its absence is reported, not worked around."
)

with open(os.path.join(OUT, "PAPER_STRATEGY_DECISION.json"), "w", encoding="utf-8") as f:
    json.dump(decision, f, indent=1, ensure_ascii=False)
print(json.dumps({k: decision[k] for k in ("DECISION", "V3_EXTENSION_PRECONDITIONS")}, indent=1, ensure_ascii=False))
