#!/usr/bin/env python3
"""LRCPS01 §4 — narrative decision. Three candidate narratives, scored against
five criteria that can each be settled from the claim matrix alone."""
import json, os

PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
M = json.load(open(os.path.join(PKG, "decisions/PAPER_SCOPE_AND_CLAIM_MATRIX.json"), encoding="utf-8"))
by_id = {c["CLAIM_ID"]: c for c in M["CLAIMS"]}

CRITERIA = {
    "QUALIFIED_SUPPORT": "every load-bearing claim of the narrative is tier QUALIFIED (0-30)",
    "PROSPECTIVITY": "the central claim was fixed before the confirming data existed (0-25)",
    "SELF_CONTAINMENT": "the narrative needs no lost, invalid or absent evidence (0-20)",
    "FALSIFIABILITY": "the narrative states a quantity that a reader could have seen fail (0-15)",
    "INDEPENDENCE_FROM_FORBIDDEN_LANGUAGE": "the narrative can be told without approaching any forbidden formulation (0-10)",
}

def score(nid, title, claims, s, notes):
    tiers = [by_id[c]["EVIDENCE_TIER"] for c in claims]
    return {
        "NARRATIVE_ID": nid,
        "TITLE_SENSE": title,
        "CLAIMS_CARRIED": claims,
        "TIERS_CARRIED": sorted(set(tiers)),
        "SCORES": s,
        "TOTAL": sum(s.values()),
        "NOTES": notes,
    }

N = [
    score("N1", "An operator that predicted a measurement, and the measurement that met it",
          ["A1", "A2", "A3", "A4", "B2", "B3", "C1"],
          {"QUALIFIED_SUPPORT": 30, "PROSPECTIVITY": 25, "SELF_CONTAINMENT": 20,
           "FALSIFIABILITY": 15, "INDEPENDENCE_FROM_FORBIDDEN_LANGUAGE": 10},
          "Every carried claim is QUALIFIED and recomputable from surviving hashed bytes. The "
          "central number was frozen before the 28 confirmation arms existed and would have "
          "failed visibly outside +/-2.9 %. Nothing in the telling comes near a forbidden term."),
    score("N2", "Why an apparently physical residual was an artefact of how we summarised",
          ["B1", "B2", "B3", "B4", "A1"],
          {"QUALIFIED_SUPPORT": 30, "PROSPECTIVITY": 8, "SELF_CONTAINMENT": 18,
           "FALSIFIABILITY": 12, "INDEPENDENCE_FROM_FORBIDDEN_LANGUAGE": 10},
          "Strong and fully bound, but retrospective: the artefact was diagnosed after the "
          "residuals were seen, and B4 shows it is a partial account. Excellent as the second "
          "result; too weak a spine for the paper because nothing was risked in advance."),
    score("N3", "A programme of work towards a lineage question and what it cost",
          ["D1", "D2", "A1"],
          {"QUALIFIED_SUPPORT": 4, "PROSPECTIVITY": 0, "SELF_CONTAINMENT": 0,
           "FALSIFIABILITY": 2, "INDEPENDENCE_FROM_FORBIDDEN_LANGUAGE": 3},
          "Carries two claims that are LOST_DOCUMENTARY and NOT_TESTED. It would be a paper "
          "about evidence that no longer exists, and it could not be told without repeatedly "
          "skirting the forbidden formulations. Rejected as a narrative; retained as one "
          "honest limitations section."),
]
N.sort(key=lambda x: -x["TOTAL"])

DEC = {
    "SECTION": "LRCPS01 §4 narrative decision",
    "CRITERIA": CRITERIA,
    "CANDIDATES": N,
    "PRIMARY_NARRATIVE": N[0]["NARRATIVE_ID"],
    "PRIMARY_NARRATIVE_SENSE": N[0]["TITLE_SENSE"],
    "PRIMARY_IS_OPERATOR_AND_MEASUREMENT": N[0]["NARRATIVE_ID"] == "N1",
    "SECONDARY_NARRATIVE": N[1]["NARRATIVE_ID"],
    "REJECTED_NARRATIVE": N[2]["NARRATIVE_ID"],
    "STRUCTURAL_CONSEQUENCE": [
        "Sections 3-4 carry N1 (construction, freeze, confirmation).",
        "Sections 5-6 carry N2 and the mechanism decomposition as the second result.",
        "Section 7 carries N3 as project history and limitation, with zero numbers.",
        "The abstract states N1 first and N2 second; N3 does not appear in the abstract.",
    ],
}
with open(os.path.join(PKG, "decisions/PAPER_NARRATIVE_DECISION.json"), "w", encoding="utf-8") as f:
    json.dump(DEC, f, indent=1, ensure_ascii=False)
for n in N:
    print(n["NARRATIVE_ID"], n["TOTAL"], n["TITLE_SENSE"][:60])
print("PRIMARY:", DEC["PRIMARY_NARRATIVE"], "| operator-and-measurement:", DEC["PRIMARY_IS_OPERATOR_AND_MEASUREMENT"])
