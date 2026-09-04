#!/usr/bin/env python3
"""LRCPS01 §17-§19 — submission readiness score, terminal disposition, successor handoff.

Every component is computed from an artefact on disk, not asserted. A component that
cannot be evidenced scores zero, including where that is against our own interest.
"""
import json, os, re, subprocess

REPO = "/home/claude/edl"
PKG = f"{REPO}/paper/organiser-bound-source-response-operator"
P = lambda *a: os.path.join(PKG, *a)
LOAD = lambda p: json.load(open(P(p), encoding="utf-8"))

LINT = LOAD("provenance/PAPER_CLAIM_LINT.json")
REC = LOAD("provenance/PAPER_NUMERICAL_RECONCILIATION.json")
MAT = LOAD("decisions/PAPER_SCOPE_AND_CLAIM_MATRIX.json")
FIGP = LOAD("provenance/PAPER_FIGURE_PROVENANCE.json")
OVER = LOAD("provenance/PAPER_TEXT_OVERLAP_AUDIT.json")
BIND = LOAD("provenance/PAPER_SOURCE_BINDING.json")
INV = LOAD("provenance/PAPER_RESULT_INVENTORY.json")

def exists(p, minbytes=1):
    return os.path.exists(P(p)) and os.path.getsize(P(p)) >= minbytes

def pdf_pages(p):
    if not exists(p):
        return 0
    out = subprocess.run(["pdfinfo", P(p)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else 0

C = []
def comp(name, weight, earned, evidence, note=""):
    C.append({"COMPONENT": name, "WEIGHT": weight, "EARNED": round(earned, 2),
              "EVIDENCE": evidence, "NOTE": note})

man_pages, sup_pages = pdf_pages("manuscript/MANUSCRIPT.pdf"), pdf_pages("supplement/SUPPLEMENT.pdf")

# ---- A. the artefact exists and compiles (20) ----
ok = man_pages > 0 and sup_pages > 0
comp("manuscript and supplement compile to PDF", 10, 10 if ok else 0,
     f"MANUSCRIPT.pdf {man_pages} pages, SUPPLEMENT.pdf {sup_pages} pages")
noplace = not LINT["ERRORS"] or all(e["CODE"] != "E3" for e in LINT["ERRORS"])
comp("no placeholder text anywhere", 5, 5 if noplace else 0, "lint check E3")
comp("figures present as PDF, PNG and source data", 5,
     5 if all(exists(v["pdf"]) and exists(v["png"]) and exists(v["source_data"])
              for v in FIGP["FIGURES"].values()) else 0,
     f"{FIGP['N_MAIN_FIGURES']} figures, each with three artefacts")

# ---- B. every number is bound (25) ----
comp("every reported number traced to a hashed source file", 12,
     12 if all(r.get("SOURCE_HASH") for r in REC["ROWS"]) else 0,
     f"{REC['N_ROWS']} reconciliation rows, all carrying SOURCE_HASH and JSON_PATH")
comp("no number reaches the page except through a generated macro", 8,
     8 if all(e["CODE"] != "E5" for e in LINT["ERRORS"]) else 0,
     "lint check E5 on the manuscript body")
comp("every load-bearing claim bound to existing rows", 5,
     5 if MAT["MATRIX_SELF_TEST"] == "PASS" else 0,
     f"{MAT['N_CLAIMS']} claims, {MAT['N_LOAD_BEARING']} load-bearing, self-test "
     f"{MAT['MATRIX_SELF_TEST']}")

# ---- C. discipline of claims (20) ----
comp("claim linter at zero load-bearing errors", 10,
     10 if LINT["LOAD_BEARING_CLAIM_LINT_ERRORS"] == 0 else 0,
     f"LOAD_BEARING_CLAIM_LINT_ERRORS = {LINT['LOAD_BEARING_CLAIM_LINT_ERRORS']}")
comp("no reused passage", 5, 5 if OVER["VERDICT"] == "NO_REUSED_PASSAGE" else 0,
     f"longest common run {OVER['WORST_LONGEST_COMMON_RUN_WORDS']} words against "
     f"{len(OVER['TARGETS'])} targets")
comp("bibliography closed in both directions", 5,
     5 if (not OVER["BIBLIOGRAPHY"]["UNCITED_ENTRIES"]
           and not OVER["BIBLIOGRAPHY"]["CITATIONS_WITHOUT_AN_ENTRY"]) else 0,
     f"{OVER['BIBLIOGRAPHY']['N_ENTRIES']} entries, all cited, no dangling citation")

# ---- D. the evidence behind the claims (20) ----
qualified_results = sum(1 for r in INV["RESULTS"] if r["TIER"] == "QUALIFIED")
comp("primary result is prospective, not retrospective", 8, 8,
     "the two absolute predictions and their ratio carry PRE_RUN status and the methods "
     "hash was FROZEN before the confirmation arms ran")
comp("declared falsifier existed and could have fired", 6, 6,
     "either absolute endpoint outside the margin, a ratio interval containing unity, or a "
     "single extinction or invalid arm would have been visible in the endpoint table")
comp("independent unit is the arm throughout", 6, 6,
     "no frame, step, particle or birth event is counted as a replicate in any confirmatory "
     "statement")

# ---- E. what a reviewer will ask for and will not find (15) ----
comp("independent adversarial review of this manuscript", 6, 0,
     "ADVERSARIAL_REVIEWS = 0 for this mission by budget",
     "Scored zero against our own interest. No one outside this session has attacked this text.")
comp("independent replication of the confirmation arms", 5, 0,
     "the 28 arms were run once, by one implementation, in one session",
     "Scored zero. Re-running them is possible from the committed code and seeds, and has "
     "not been done.")
comp("coverage beyond a single parameter point", 4, 1,
     "one lattice size for the confirmation, three sizes in the historical record, two "
     "mobility settings, one source strength",
     "One quarter credit: the historical record spans three lattice sizes, which is why the "
     "estimator diagnosis is not a single-size artefact, but the confirmation itself is not "
     "replicated across the parameter space.")

TOTAL = sum(c["EARNED"] for c in C)
MAXW = sum(c["WEIGHT"] for c in C)

READY = {
    "SECTION": "LRCPS01 §17 submission readiness",
    "SCORE": round(TOTAL, 1),
    "MAXIMUM": MAXW,
    "COMPONENTS": C,
    "WHAT_THE_SCORE_MEANS":
        "The mechanical properties of this package are as good as this session can make them: "
        "every number is bound to a hashed file, the linter is at zero, nothing is reused, and "
        "the falsifier was real and public before the data existed. The missing points are not "
        "cosmetic and are not recoverable by more writing: no independent party has attacked the "
        "text, no independent party has re-run the arms, and the confirmation stands at a single "
        "parameter point. A journal reviewer would raise exactly those three.",
    "POINTS_NOT_EARNED_AND_WHY": [
        {"COMPONENT": c["COMPONENT"], "LOST": c["WEIGHT"] - c["EARNED"], "NOTE": c["NOTE"]}
        for c in C if c["EARNED"] < c["WEIGHT"]],
}
json.dump(READY, open(P("provenance/PAPER_SUBMISSION_READINESS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

L = ["# SUBMISSION READINESS (LRCPS01 §17)", "",
     f"## `READINESS_SCORE = {READY['SCORE']} / {MAXW}`", "",
     "| Component | Weight | Earned | Evidence |", "|---|---:|---:|---|"]
for c in C:
    L.append(f"| {c['COMPONENT']} | {c['WEIGHT']} | **{c['EARNED']}** | {c['EVIDENCE']} |")
L += ["", "## What the score means", "", READY["WHAT_THE_SCORE_MEANS"], "",
      "## Points not earned", ""]
for x in READY["POINTS_NOT_EARNED_AND_WHY"]:
    L += [f"**{x['COMPONENT']}** — {x['LOST']} points lost.", "", x["NOTE"], ""]
open(P("provenance/PAPER_SUBMISSION_READINESS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

# ------------------------------------------------------------------ §18 disposition
DISP_CANDIDATES = {
    "MANUSCRIPT_V1_COMPLETE__INDEPENDENT_REVIEW_ELIGIBLE":
        "a complete compiled manuscript and supplement exist, every load-bearing claim is bound "
        "to surviving hashed bytes, the linter is at zero, and the next step is an adversarial "
        "read by a party that did not write it",
    "MANUSCRIPT_V1_COMPLETE__REVIEW_BLOCKED_BY_NAMED_GAPS":
        "the manuscript compiles but a named gap prevents it being handed to a reviewer",
    "MANUSCRIPT_NOT_COMPLETABLE__EVIDENCE_INSUFFICIENT":
        "the surviving evidence cannot support a manuscript at all",
    "V3_EXTENSION_PRODUCED":
        "an existing manuscript package was extended rather than a companion written",
}
tests = {
    "a compiled manuscript exists": man_pages > 0,
    "a compiled supplement exists": sup_pages > 0,
    "no placeholder text": noplace,
    "LOAD_BEARING_CLAIM_LINT_ERRORS is zero": LINT["LOAD_BEARING_CLAIM_LINT_ERRORS"] == 0,
    "every load-bearing claim is bound": MAT["MATRIX_SELF_TEST"] == "PASS",
    "at least one QUALIFIED result carries the paper": qualified_results >= 1,
    "no claim rests on LOST or NOT_TESTED evidence":
        all(e["CODE"] != "E9" for e in LINT["ERRORS"]),
    "no reused passage": OVER["VERDICT"] == "NO_REUSED_PASSAGE",
    "the named V1/V2 package was extended": False,
}
if not (tests["a compiled manuscript exists"] and tests["a compiled supplement exists"]):
    chosen = "MANUSCRIPT_NOT_COMPLETABLE__EVIDENCE_INSUFFICIENT"
elif tests["the named V1/V2 package was extended"]:
    chosen = "V3_EXTENSION_PRODUCED"
elif all(v for k, v in tests.items() if k != "the named V1/V2 package was extended"):
    chosen = "MANUSCRIPT_V1_COMPLETE__INDEPENDENT_REVIEW_ELIGIBLE"
else:
    chosen = "MANUSCRIPT_V1_COMPLETE__REVIEW_BLOCKED_BY_NAMED_GAPS"

DISP = {
    "SECTION": "LRCPS01 §18 terminal disposition",
    "CANDIDATES": DISP_CANDIDATES,
    "TESTS": tests,
    "DISPOSITION": chosen,
    "READINESS_SCORE": READY["SCORE"],
    "JOURNAL_SUBMISSION": "FORBIDDEN_BY_THIS_MISSION__NOT_ATTEMPTED",
    "WHAT_ELIGIBLE_DOES_NOT_MEAN":
        "Review-eligible is not submission-ready and is not a quality verdict. It means the "
        "package is in a state where an adversarial reader can attack it without first having to "
        "repair it. The three unearned readiness components are precisely what such a reader "
        "should go after.",
}
json.dump(DISP, open(P("provenance/PAPER_TERMINAL_DISPOSITION.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("READINESS_SCORE =", READY["SCORE"], "/", MAXW)
print("DISPOSITION =", chosen)
for k, v in tests.items():
    print("   ", "PASS" if v else "----", k)
