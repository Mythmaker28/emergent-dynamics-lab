#!/usr/bin/env python3
"""LRCPS01 §16 — result inventory, provenance ledger, missing-evidence matrix, outline."""
import json, os, subprocess

PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
PROV = os.path.join(PKG, "provenance")
DEC = os.path.join(PKG, "decisions")
REC = json.load(open(os.path.join(PROV, "PAPER_NUMERICAL_RECONCILIATION.json"), encoding="utf-8"))
BIND = json.load(open(os.path.join(PROV, "PAPER_SOURCE_BINDING.json"), encoding="utf-8"))
MAT = json.load(open(os.path.join(DEC, "PAPER_SCOPE_AND_CLAIM_MATRIX.json"), encoding="utf-8"))
NAR = json.load(open(os.path.join(DEC, "PAPER_NARRATIVE_DECISION.json"), encoding="utf-8"))
BYLAB = {r["MANUSCRIPT_LABEL"]: r for r in REC["ROWS"]}

# ---------------------------------------------------------------- result inventory
RESULTS = [
    {"RESULT_ID": "A", "TITLE": "A frozen operator predicted the source-response radius before "
     "the confirming arms existed, and the arms met the prediction",
     "CLAIMS": ["A1", "A2", "A3", "A5"], "TIER": "QUALIFIED",
     "SECTIONS": ["3", "4"], "FIGURES": ["Fig1", "Fig2"],
     "INDEPENDENT_UNIT": "arm (seed)", "N_INDEPENDENT": 28,
     "FALSIFIER_THAT_DID_NOT_FIRE": "either absolute endpoint outside +/-2.9 %, or any of the "
     "15 radii disagreeing, or a single extinction or technically invalid arm"},
    {"RESULT_ID": "B", "TITLE": "The historical negative residual is dominated by the summary "
     "rule, and dispersion separates that account from the full construction",
     "CLAIMS": ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"], "TIER": "QUALIFIED",
     "SECTIONS": ["5"], "FIGURES": ["Fig3"],
     "INDEPENDENT_UNIT": "arm (seed)", "N_INDEPENDENT": 116,
     "FALSIFIER_THAT_DID_NOT_FIRE": "an estimator-only surrogate returning a positive or null "
     "median bias, or a mean summary as biased as the median"},
    {"RESULT_ID": "C", "TITLE": "Which ingredients the agreement depends on, and what remains open",
     "CLAIMS": ["C1", "C2", "C3", "C4", "C5", "C6"], "TIER": "QUALIFIED",
     "SECTIONS": ["6"], "FIGURES": ["Fig4"],
     "INDEPENDENT_UNIT": "arm (seed) for the measured couplings; analytic for the ablations",
     "N_INDEPENDENT": 57,
     "FALSIFIER_THAT_DID_NOT_FIRE": "an ablated construction sitting closer to the observation "
     "than the full one"},
    {"RESULT_ID": "D", "TITLE": "The lineage line of work, and what did not survive",
     "CLAIMS": ["D1", "D2"], "TIER": "LOST_DOCUMENTARY / NOT_TESTED",
     "SECTIONS": ["7"], "FIGURES": [],
     "INDEPENDENT_UNIT": "none — no quantity is carried", "N_INDEPENDENT": 0,
     "FALSIFIER_THAT_DID_NOT_FIRE": "not applicable; nothing is asserted"},
]
for r in RESULTS:
    labs = sorted({l for c in MAT["CLAIMS"] if c["CLAIM_ID"] in r["CLAIMS"]
                   for l in c["RECONCILIATION_LABELS"]})
    r["RECONCILIATION_LABELS"] = labs
    r["N_LABELS"] = len(labs)
    r["ALL_LABELS_BOUND"] = all(l in BYLAB for l in labs)
    r["SOURCE_FILES"] = sorted({BYLAB[l]["SOURCE_FILE"] for l in labs})

INV = {"SECTION": "LRCPS01 §16 result inventory",
       "PRIMARY_NARRATIVE": NAR["PRIMARY_NARRATIVE"],
       "N_RESULTS": len(RESULTS),
       "N_RESULTS_CARRYING_NUMBERS": sum(1 for r in RESULTS if r["N_LABELS"]),
       "RESULTS": RESULTS}
json.dump(INV, open(os.path.join(PROV, "PAPER_RESULT_INVENTORY.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- provenance ledger
head = subprocess.run(["git", "-C", "/home/claude/edl", "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()
LEDGER = {
    "SECTION": "LRCPS01 §16 provenance ledger",
    "REPO_HEAD_AT_LEDGER_TIME": head,
    "BRANCH": BIND["REPO_BRANCH"],
    "EVIDENCE_TIERS": {
        "QUALIFIED": "recomputable from surviving hashed bytes and adjudicated in its own programme",
        "DEVELOPMENTAL": "recorded, but not run under a freeze that would let it carry a claim",
        "INVALID": "adjudicated technically invalid; may not support any statement",
        "LOST_DOCUMENTARY": "the programme ran, its narrative record exists elsewhere, its bytes do not",
        "NOT_TESTED": "no run in any surviving programme addresses it",
    },
    "PROGRAMMES": {k: {"STATUS": v["STATUS"], "raw_archives": v["raw_archives"],
                       "files_hashed": len(v.get("sha256", {}))}
                   for k, v in BIND["SOURCES"].items()},
    "PROGRAMMES_USED_FOR_NUMBERS": sorted({r["SOURCE_PROGRAM"] for r in REC["ROWS"]}),
    "SOURCE_FILES_USED_FOR_NUMBERS": REC["SOURCES"],
    "N_NUMERICAL_ROWS": REC["N_ROWS"],
    "ROWS_BY_SOURCE_FILE": {},
    "ROWS_BY_STATUS": {},
    "NUMBERS_TAKEN_FROM_PROSE": 0,
    "NUMBERS_TAKEN_FROM_CONVERSATION": 0,
    "NEW_SCIENTIFIC_ENGINE_RUNS": 0,
    "ADVERSARIAL_REVIEWS_RUN": 0,
}
for r in REC["ROWS"]:
    LEDGER["ROWS_BY_SOURCE_FILE"][r["SOURCE_FILE"]] = LEDGER["ROWS_BY_SOURCE_FILE"].get(r["SOURCE_FILE"], 0) + 1
    LEDGER["ROWS_BY_STATUS"][r["STATUS"]] = LEDGER["ROWS_BY_STATUS"].get(r["STATUS"], 0) + 1
json.dump(LEDGER, open(os.path.join(PROV, "PAPER_PROVENANCE_LEDGER.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- missing evidence matrix
MISSING = [
    ("CLOC02", "LOST", "closure of an earlier lineage-operator line",
     "the container was reset; no archive, no output, no code survives in this session",
     "nothing in this paper depends on it, and no number from it appears anywhere"),
    ("RSLOC03", "LOST", "a 284-world prospective calibration addressed to the lineage question",
     "same reset; the externalised capsule is not mounted back into this session",
     "Result D carries no number, no figure and no table; it was in any case adjudicated "
     "CALIBRATION_TECHNICALLY_INVALID, so it could not have carried one"),
    ("RIRA01", "LOST", "a zero-run route arbitration over the same question",
     "same reset", "its disposition is described in section 7 as project history only"),
    ("named persistence V1/V2 package", "NOT_PRESENT",
     "the manuscript package this paper was originally to extend",
     "no file in the repository, tracked or untracked, is that package",
     "the paper is a companion and makes no continuity claim against it"),
    ("OBDI02 / PMCR01 / MYQBD01 raw archives", "DOCUMENTARY_ONLY",
     "raw arms behind part of the historical record",
     "their directories carry no surviving raw archive in this session",
     "the historical residuals they contribute to are reported as a described record, never as "
     "confirmatory replicates; every confirmatory statement rests on the 28 fresh arms"),
    ("H3, reproduction, heredity, autonomous cohesion", "NOT_TESTED",
     "the biological questions of the wider project",
     "no surviving programme tests them",
     "reported as NOT_TESTED / NOT_ESTABLISHED in the abstract's scope line and in section 8"),
]
L = ["# MISSING EVIDENCE MATRIX (LRCPS01 §16)", "",
     "Everything a reader might expect this paper to contain and does not, why, and what the",
     "paper does instead. Nothing here is worked around; each row is reported.", "",
     "| Evidence | Status | What it was | Why it is not here | What the paper does instead |",
     "|---|---|---|---|---|"]
for a, b, c, d, e in MISSING:
    L.append(f"| {a} | `{b}` | {c} | {d} | {e} |")
L += ["", "## Consequence for the claim matrix", "",
      "No claim in the matrix draws on any row above. The four `LOST` and `NOT_PRESENT` rows",
      "support claims D1 and D2 only, which are narrative and carry no quantity.", ""]
open(os.path.join(PROV, "PAPER_MISSING_EVIDENCE_MATRIX.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------------------------------------------------------------- outline
OUTLINE = [
    ("1", "The problem: predicting the spatial response to a source in a discrete, capacity-limited medium",
     ["why a source-response length is the natural observable",
      "why a continuum reading is not available at this scale (C4)",
      "what would count as a prediction rather than a fit"], []),
    ("2", "Model and observable",
     ["the frozen kinetics and exchange law, event order, and the parameter point",
      "the definition of the reported radius and its three estimator properties",
      "the unit of analysis: the arm"], ["Fig1"]),
    ("3", "Construction of the operator and the freeze",
     ["the one-step conditional operator, exact given the state (C5)",
      "the three corrections that enter it, and the ones that were measured and dropped",
      "the equivalence margin, built from named terms before any arm ran (A1)",
      "instrumentation inertness (A5)"], []),
    ("4", "Prospective confirmation",
     ["28 fresh arms, 0 extinctions, 0 invalid (A2)",
      "both absolute endpoints and the ratio inside the margin (A2, A3)",
      "the whole radial profile, not only the summary (A4)",
      "the adjudicated disposition (C6)"], ["Fig2"]),
    ("5", "The summary rule, not the field, carried the historical residual",
     ["what the historical record showed (B1)",
      "a surrogate with no dynamics at all reproduces the sign and part of the size (B2)",
      "the mean rule is nearly unbiased (B3, B5)",
      "dispersion separates the surrogate from the construction (B4)"], ["Fig3"]),
    ("6", "What the agreement depends on",
     ["ablations: the shared trajectory and the endogenous flux (C1)",
      "the birth flux is over-dispersed (C2)",
      "capacity is not what limits this regime (C3)",
      "the continuum error (C4)"], ["Fig4"]),
    ("7", "Project history and what did not survive",
     ["the lineage line of work, named without a number (D1)",
      "what the loss means for what can and cannot be asserted (D2)"], []),
    ("8", "Discussion: what is established, what is bounded, what remains open",
     ["the marginal density equation does not close (C5)",
      "the qualification is bounded by one parameter point",
      "the mandatory status lines"], []),
]
L = ["# PAPER OUTLINE (LRCPS01 §16)", "",
     f"Primary narrative `{NAR['PRIMARY_NARRATIVE']}` — {NAR['PRIMARY_NARRATIVE_SENSE']}", "",
     "| § | Title | Claims | Figures |", "|---|---|---|---|"]
for n, t, pts, figs in OUTLINE:
    cs = sorted({c["CLAIM_ID"] for c in MAT["CLAIMS"] if n in c["ALLOWED_SECTIONS"]})
    L.append(f"| {n} | {t} | {', '.join(cs) or '—'} | {', '.join(figs) or '—'} |")
L += [""]
for n, t, pts, figs in OUTLINE:
    L += [f"## {n}. {t}", ""] + [f"- {p}" for p in pts] + [""]
L += ["## Supplement", "",
      "- S1 provenance, freeze hashes and the inertness check",
      "- S2 the operator, the event order and the exact observable definition",
      "- S3 the equivalence margin, term by term",
      "- S4 the 28 arms: seeds, final state hashes, ledger sizes",
      "- S5 endpoint arithmetic in full",
      "- S6 the estimator surrogate and the historical record by lattice size",
      "- S7 ablations, couplings, capacity and the continuum comparison",
      "- S8 the evidence tiers and the missing-evidence matrix", ""]
open(os.path.join(PROV, "PAPER_OUTLINE.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

print("results:", INV["N_RESULTS"], "carrying numbers:", INV["N_RESULTS_CARRYING_NUMBERS"])
print("all labels bound:", all(r["ALL_LABELS_BOUND"] for r in RESULTS))
print("rows by source file:", LEDGER["ROWS_BY_SOURCE_FILE"])
