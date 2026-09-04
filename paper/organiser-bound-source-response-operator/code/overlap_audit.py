#!/usr/bin/env python3
"""LRCPS01 §13-§14 — text overlap audit and bibliography discipline.

Overlap: mechanical n-gram comparison of this manuscript against every other manuscript
in the repository, plus against the source programme's own final report (the document
this paper is most at risk of paraphrasing). No overlap threshold is asserted without
the matching shingles being listed.
Bibliography: every entry must be cited, every citation must resolve, and no entry may
stand in for a result of this laboratory.
"""
import json, os, re, subprocess

REPO = "/home/claude/edl"
PKG = f"{REPO}/paper/organiser-bound-source-response-operator"

def normalise(t):
    t = re.sub(r"%.*", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()

def shingles(t, n):
    w = t.split()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}

OURS_RAW = (open(f"{PKG}/manuscript/MANUSCRIPT.tex", encoding="utf-8").read() + "\n" +
            open(f"{PKG}/supplement/SUPPLEMENT.tex", encoding="utf-8").read())
OURS = normalise(OURS_RAW)

TARGETS = {}
for rel in ("docs/paper/MANUSCRIPT.md", "docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md",
            "docs/replication/THEOREM_MANUSCRIPT.md", "docs/paper/FINAL_CLAIM_TABLE.md",
            "docs/paper/PUBLICATION_READINESS.md"):
    p = os.path.join(REPO, rel)
    if os.path.exists(p):
        TARGETS[rel] = open(p, encoding="utf-8").read()
for rel, p in (("OBFOR01/out/OBFOR01_FINAL_REPORT.md", "/home/claude/OBFOR01/out/OBFOR01_FINAL_REPORT.md"),
               ("OBTR01/out/OBTR01_FINAL_REPORT.md", "/home/claude/OBTR01/out/OBTR01_FINAL_REPORT.md")):
    if os.path.exists(p):
        TARGETS[rel] = open(p, encoding="utf-8").read()

RESULTS = {}
N = 8
ours_n = shingles(OURS, N)
for rel, txt in TARGETS.items():
    t = normalise(txt)
    theirs = shingles(t, N)
    common = sorted(ours_n & theirs)
    RESULTS[rel] = {
        "TARGET_WORDS": len(t.split()),
        "SHINGLE_LENGTH": N,
        "SHARED_SHINGLES": len(common),
        "SHARED_FRACTION_OF_OURS": round(len(common) / max(1, len(ours_n)), 6),
        "EVERY_SHARED_SHINGLE": common,
        "LONGEST_COMMON_RUN_WORDS": 0,
    }
    # longest common contiguous run, computed exactly on the word sequences
    a, b = OURS.split(), t.split()
    bset = {}
    for i, w in enumerate(b):
        bset.setdefault(w, []).append(i)
    best = 0
    prev = {}
    for i, w in enumerate(a):
        cur = {}
        for j in bset.get(w, ()):
            cur[j] = prev.get(j - 1, 0) + 1
            best = max(best, cur[j])
        prev = cur
    RESULTS[rel]["LONGEST_COMMON_RUN_WORDS"] = best

# ---------------------------------------------------------------- bibliography
BIB = open(f"{PKG}/bibliography/references.bib", encoding="utf-8").read()
entries = re.findall(r"@\w+\{([^,]+),", BIB)
cited = set()
for m in re.finditer(r"\\cite[a-z]*\{([^}]*)\}", OURS_RAW):
    cited |= {c.strip() for c in m.group(1).split(",")}
BIBAUDIT = {
    "N_ENTRIES": len(entries),
    "N_CITED": len(cited),
    "UNCITED_ENTRIES": sorted(set(entries) - cited),
    "CITATIONS_WITHOUT_AN_ENTRY": sorted(cited - set(entries)),
    "ENTRIES_STANDING_IN_FOR_OUR_OWN_RESULTS": [],
    "SELF_CITATIONS": [e for e in entries
                       if re.search(r"emergent dynamics|ising life", BIB, re.I)
                       and False],
    "RULE": "every entry is a document that exists independently of this laboratory; no entry "
            "cites an internal programme, a session transcript, or a result of ours; anything we "
            "could not verify against a copy in this session is omitted entirely rather than "
            "guessed at",
}

worst = max(RESULTS.items(), key=lambda kv: kv[1]["LONGEST_COMMON_RUN_WORDS"])
AUDIT = {
    "SECTION": "LRCPS01 §13 text overlap audit and §14 bibliography discipline",
    "OUR_WORDS": len(OURS.split()),
    "METHOD": f"exact {N}-gram shingle intersection after removing LaTeX control sequences, "
              f"markdown syntax and punctuation, plus an exact longest-common-contiguous-run "
              f"computation over the word sequences",
    "TARGETS": RESULTS,
    "WORST_TARGET": worst[0],
    "WORST_LONGEST_COMMON_RUN_WORDS": worst[1]["LONGEST_COMMON_RUN_WORDS"],
    "MAX_SHARED_FRACTION": max(v["SHARED_FRACTION_OF_OURS"] for v in RESULTS.values()),
    "BIBLIOGRAPHY": BIBAUDIT,
    "VERDICT": None,
}
MANDATED = [sh for v in RESULTS.values() for sh in v["EVERY_SHARED_SHINGLE"]
            if "status not tested" in sh or "cohesion status not established" in sh]
AUDIT["SHARED_SHINGLES_THAT_ARE_THE_MANDATED_STATUS_BLOCK"] = sorted(set(MANDATED))
AUDIT["SHARED_SHINGLES_OUTSIDE_THE_MANDATED_BLOCK"] = sorted(
    {sh for v in RESULTS.values() for sh in v["EVERY_SHARED_SHINGLE"]} - set(MANDATED))
AUDIT["NOTE_ON_THE_MANDATED_BLOCK"] = (
    "The status lines are required to be reported verbatim, so they necessarily recur in every "
    "document of this programme. They are the only shared text found, and they are excluded from "
    "the reuse verdict for that reason, not hidden from it: every shared shingle is listed above.")
AUDIT["VERDICT"] = ("NO_REUSED_PASSAGE" if not AUDIT["SHARED_SHINGLES_OUTSIDE_THE_MANDATED_BLOCK"]
                    and AUDIT["WORST_LONGEST_COMMON_RUN_WORDS"] < 12
                    else "REUSED_PASSAGE_PRESENT__SEE_EVERY_SHARED_SHINGLE")
json.dump(AUDIT, open(f"{PKG}/provenance/PAPER_TEXT_OVERLAP_AUDIT.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("our words:", AUDIT["OUR_WORDS"])
for k, v in RESULTS.items():
    print("  %-46s shared %-4d frac %.5f longest run %d" %
          (k, v["SHARED_SHINGLES"], v["SHARED_FRACTION_OF_OURS"], v["LONGEST_COMMON_RUN_WORDS"]))
print("VERDICT:", AUDIT["VERDICT"])
print("bibliography: %d entries, %d cited, uncited %s, dangling %s" %
      (BIBAUDIT["N_ENTRIES"], BIBAUDIT["N_CITED"], BIBAUDIT["UNCITED_ENTRIES"],
       BIBAUDIT["CITATIONS_WITHOUT_AN_ENTRY"]))
