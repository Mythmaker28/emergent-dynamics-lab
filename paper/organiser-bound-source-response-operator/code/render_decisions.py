#!/usr/bin/env python3
"""Render the §2/§3/§4 markdown companions directly from their JSON, so the two
representations cannot diverge."""
import json, os
PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
D = os.path.join(PKG, "decisions")
S = json.load(open(os.path.join(D, "PAPER_STRATEGY_DECISION.json"), encoding="utf-8"))
M = json.load(open(os.path.join(D, "PAPER_SCOPE_AND_CLAIM_MATRIX.json"), encoding="utf-8"))
N = json.load(open(os.path.join(D, "PAPER_NARRATIVE_DECISION.json"), encoding="utf-8"))

# ---------- §2 ----------
L = ["# PAPER STRATEGY DECISION (LRCPS01 §2)", "",
     f"**DECISION = `{S['DECISION']}`**", "",
     "## Preconditions tested for a V3 extension", ""]
for k, v in S["V3_EXTENSION_PRECONDITIONS"].items():
    L.append(f"- `{k}` = `{v}`")
L += ["", "## Rule applied", "", S["DECISION_RULE"], "",
      "## Manuscripts that are present in the repository", ""]
for k, v in S["EXISTING_MANUSCRIPTS"].items():
    if v.get("present") is False:
        L.append(f"- `{k}` — NOT PRESENT")
    else:
        L.append(f"- `{k}` — \"{v['title']}\" ({v['words']} words, sha256 `{v['sha256'][:16]}…`)")
        L.append(f"  - estimand: {v['estimand']}")
L += ["", "## Candidate estimand of this paper", "", S["CANDIDATE_ESTIMAND"], "",
      "The two estimands are disjoint: one is a scalar causal-response magnitude read on",
      "contaminated reference channels of a synthetic measurement model; the other is a spatial",
      "extent of a lattice field around a source. No datum, no figure and no theorem is shared.",
      "", "## Absent package", "", S["ABSENT_PACKAGE_HANDLING"], "",
      "## Consequences", ""]
L += [f"{i+1}. {c}" for i, c in enumerate(S["CONSEQUENCES"])]
open(os.path.join(D, "PAPER_STRATEGY_DECISION.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------- §3 ----------
L = ["# PAPER SCOPE AND CLAIM MATRIX (LRCPS01 §3)", "",
     f"Strategy: `{M['PAPER_STRATEGY']}`  ·  claims: **{M['N_CLAIMS']}**  ·  ",
     f"load-bearing: **{M['N_LOAD_BEARING']}**  ·  self-test: **{M['MATRIX_SELF_TEST']}**", "",
     "No manuscript prose may be written except in service of a claim listed here, and no",
     "claim may be stated above its wording ceiling.", "",
     "## Claim matrix", "",
     "| ID | Tier | Kind | Sections | Labels | Ceiling |",
     "|---|---|---|---|---|---|"]
for c in M["CLAIMS"]:
    L.append("| {} | `{}` | {} | {} | {} | {} |".format(
        c["CLAIM_ID"], c["EVIDENCE_TIER"], c["KIND"], " ".join(c["ALLOWED_SECTIONS"]),
        len(c["RECONCILIATION_LABELS"]), c["WORDING_CEILING"].replace("|", "\\|")))
L += ["", "## Claims in full", ""]
for c in M["CLAIMS"]:
    L += [f"### {c['CLAIM_ID']} — `{c['EVIDENCE_TIER']}` — {c['KIND']}", "",
          f"> {c['CLAIM_TEXT_CEILING']}", "",
          f"- allowed sections: {', '.join(c['ALLOWED_SECTIONS'])}",
          f"- reconciliation labels: {', '.join('`%s`' % x for x in c['RECONCILIATION_LABELS']) or '— (narrative only, no number permitted)'}",
          f"- wording ceiling: {c['WORDING_CEILING']}",
          f"- why not stronger: {c['WHY_NOT_STRONGER']}", ""]
L += ["## Status lines reported unconditionally", ""]
for k, v in M["MANDATORY_STATUS_LINES"].items():
    L.append(f"- `{k} = {v}`")
L += ["", "## Formulations forbidden anywhere in the paper", ""]
L += [f"- {x}" for x in M["FORBIDDEN_FORMULATIONS"]]
L += ["", "## Words forbidden in the title", "",
      ", ".join("`%s`" % w for w in M["TITLE_FORBIDDEN_WORDS"]), "",
      "## Explicitly out of scope", ""]
L += [f"- {x}" for x in M["CLAIMS_EXPLICITLY_OUT_OF_SCOPE"]]
L += ["", "## Independent unit", "", M["INDEPENDENT_UNIT_RULE"], ""]
open(os.path.join(D, "PAPER_SCOPE_AND_CLAIM_MATRIX.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------- §4 ----------
L = ["# PAPER NARRATIVE DECISION (LRCPS01 §4)", "",
     f"**PRIMARY = `{N['PRIMARY_NARRATIVE']}` — {N['PRIMARY_NARRATIVE_SENSE']}**", "",
     f"`PRIMARY_IS_OPERATOR_AND_MEASUREMENT = {N['PRIMARY_IS_OPERATOR_AND_MEASUREMENT']}`", "",
     "## Criteria", ""]
for k, v in N["CRITERIA"].items():
    L.append(f"- `{k}` — {v}")
L += ["", "## Scores", "",
      "| Narrative | " + " | ".join(N["CRITERIA"]) + " | Total |",
      "|---|" + "---|" * (len(N["CRITERIA"]) + 1)]
for c in N["CANDIDATES"]:
    L.append("| " + c["NARRATIVE_ID"] + " | " +
             " | ".join(str(c["SCORES"][k]) for k in N["CRITERIA"]) + f" | **{c['TOTAL']}** |")
L += ["", "## Reasoning", ""]
for c in N["CANDIDATES"]:
    L += [f"### {c['NARRATIVE_ID']} ({c['TOTAL']}/100) — {c['TITLE_SENSE']}", "",
          f"- claims carried: {', '.join(c['CLAIMS_CARRIED'])}",
          f"- tiers carried: {', '.join(c['TIERS_CARRIED'])}", "", c["NOTES"], ""]
L += ["## Structural consequence", ""]
L += [f"{i+1}. {x}" for i, x in enumerate(N["STRUCTURAL_CONSEQUENCE"])]
open(os.path.join(D, "PAPER_NARRATIVE_DECISION.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("rendered:", sorted(os.listdir(D)))
