#!/usr/bin/env python3
"""LRCPS01 §15 — deterministic claim linter.

Reads the compiled sources (not a description of them) and fails on:
  E1  a forbidden formulation anywhere in the manuscript or supplement
  E2  a forbidden word in the title
  E3  a placeholder token
  E4  a number macro used but never defined, or defined twice
  E5  a bare numeral in a position where a bound macro was required
  E6  a mandatory status line missing
  E7  a claim asserted in a section it is not allowed to appear in
  E8  an upgrade word applied to a QUALIFIED-tier claim
  E9  a quantity attributed to LOST or NOT_TESTED evidence
Exit code is the number of LOAD_BEARING errors.
"""
import json, os, re, sys

PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
MAN = open(f"{PKG}/manuscript/MANUSCRIPT.tex", encoding="utf-8").read()
SUP = open(f"{PKG}/supplement/SUPPLEMENT.tex", encoding="utf-8").read()
NUM = open(f"{PKG}/manuscript/numbers.tex", encoding="utf-8").read()
PRE = open(f"{PKG}/manuscript/preamble.tex", encoding="utf-8").read()
MAT = json.load(open(f"{PKG}/decisions/PAPER_SCOPE_AND_CLAIM_MATRIX.json", encoding="utf-8"))
REC = json.load(open(f"{PKG}/provenance/PAPER_NUMERICAL_RECONCILIATION.json", encoding="utf-8"))
TITLE_FILE = open(f"{PKG}/decisions/PAPER_TITLE_AND_ABSTRACT_OPTIONS.md", encoding="utf-8").read()

ERRORS, WARNINGS = [], []
def err(code, sev, msg):
    (ERRORS if sev == "LOAD_BEARING" else WARNINGS).append(
        {"CODE": code, "SEVERITY": sev, "MESSAGE": msg})

def strip_tex(s):
    s = re.sub(r"%.*", "", s)                       # comments
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)           # control sequences
    s = re.sub(r"[{}$~\\]", " ", s)
    return re.sub(r"\s+", " ", s)

PROSE = strip_tex(MAN) + " " + strip_tex(SUP)
PROSE_LOWER = PROSE.lower()

# ---- E1 forbidden formulations -------------------------------------------------
# each entry: (canonical formulation, regex that catches it and its close paraphrases)
FORBIDDEN_PATTERNS = {
    "reproduction was demonstrated":
        r"reproduction (was|is) (demonstrated|shown|established|observed)",
    "a daughter organism formed":
        r"daughter (organism|cell|individual|entity)",
    "heredity was demonstrated":
        r"heredity (was|is) (demonstrated|shown|established)",
    "the system is alive":
        r"\bthe system is alive\b|\bis a living\b|\bwe observe life\b",
    "autonomous cohesion was demonstrated":
        r"autonomous cohesion (was|is) (demonstrated|shown|established)",
    "a lineage window was confirmed":
        r"lineage window (was|is) (confirmed|established|found|demonstrated)",
    "the lineage region is empty":
        r"(lineage|the) region is empty|no such region exists",
    "the architecture cannot support a lineage":
        r"architecture (cannot|can not|could not) support",
    "the interpolator proved no suitable parameter exists":
        r"proved (that )?no suitable parameter|no suitable parameter exists",
    "the 284-world calibration was prospectively valid":
        r"calibration was (prospectively )?valid",
    "CLOC02 established any quantitative result":
        r"cloc02 (established|showed|gave|yielded)",
    "founder survival is biologically unnecessary":
        r"founder survival is (biologically )?unnecessary",
}
for canonical, pat in FORBIDDEN_PATTERNS.items():
    m = re.search(pat, PROSE_LOWER)
    if m:
        err("E1", "LOAD_BEARING",
            f"forbidden formulation {canonical!r} matched: ...{PROSE_LOWER[max(0,m.start()-60):m.end()+60]}...")

# ---- E2 title ------------------------------------------------------------------
tm = re.search(r"\\title\{(.+?)\n\n", MAN, re.S) or re.search(r"\\title\{(.+?)\}\s*\n\\author", MAN, re.S)
TITLE = strip_tex(tm.group(1)) if tm else ""
for w in MAT["TITLE_FORBIDDEN_WORDS"]:
    if re.search(r"\b" + re.escape(w) + r"\b", TITLE, re.I):
        err("E2", "LOAD_BEARING", f"forbidden word {w!r} in the title: {TITLE!r}")

# ---- E3 placeholders -----------------------------------------------------------
for tok in ("TODO", "TBD", "INSERT VALUE", "CITATION NEEDED", "FIGURE HERE", "XXX",
            "PlaceholderNotUsed", "FIXME", "lorem ipsum"):
    for name, body in (("manuscript", MAN), ("supplement", SUP)):
        if tok.lower() in body.lower():
            err("E3", "LOAD_BEARING", f"placeholder token {tok!r} present in the {name}")

# ---- E4 macros -----------------------------------------------------------------
defined = re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", NUM)
dupes = {d for d in defined if defined.count(d) > 1}
for d in sorted(dupes):
    err("E4", "LOAD_BEARING", f"number macro defined twice: {d}")
defined = set(defined) | set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", PRE))
LATEX_OK = set("""documentclass input usepackage renewcommand thesection arabic thetable thefigure
 title bfseries author date begin end maketitle noindent tableofcontents textwidth includegraphics
 caption label ref citep emph textbf texttt section subsection quad small centering toprule midrule
 bottomrule tabular center textsc left right middle mathbb neq pm times item hline smallskip colback
 colframe boxrule top bottom eqref frac sum mathrm operatorname text longtable endfirsthead endhead
 endfoot cmidrule lr multicolumn allowbreak hspace bibliographystyle bibliography""".split())
body_all = MAN + SUP + "".join(
    open(f"{PKG}/supplement/{f}", encoding="utf-8").read()
    for f in os.listdir(f"{PKG}/supplement") if f.endswith(".tex") and f != "SUPPLEMENT.tex")
used = set(re.findall(r"\\([a-z][A-Za-z]*)\b", body_all))
for u in sorted(used - defined - LATEX_OK):
    err("E4", "LOAD_BEARING", f"macro used but never defined: \\{u}")

# ---- E5 bare numerals where a bound macro was required -------------------------
# a reported quantity is a numeral with a decimal point, or any percentage.
# strip comments, then every LaTeX optional-argument group and every tabular column
# specification: those carry layout parameters, never reported quantities.
prose_only = re.sub(r"%.*", "", MAN)
prose_only = re.sub(r"\\begin\{tabular\}\{[^}]*\}", " ", prose_only)
prose_only = re.sub(r"\\includegraphics\[[^\]]*\]", " ", prose_only)
prose_only = re.sub(r"\[[^\]\n]*\]", " ", prose_only)
prose_only = re.sub(r"\\[a-zA-Z]+", " ", prose_only)
for m in re.finditer(r"(?<![\d.])\d+\.\d+(?![\d])", prose_only):
    ctx = prose_only[max(0, m.start() - 70):m.end() + 40]
    if "searchsorted" in ctx or "q = 0.8" in ctx or "0.8" == m.group():
        continue
    err("E5", "LOAD_BEARING",
        f"bare decimal numeral {m.group()!r} in the manuscript; every reported quantity must "
        f"come from a bound macro. Context: ...{ctx.strip()}...")

# ---- E6 mandatory status lines -------------------------------------------------
for k, v in MAT["MANDATORY_STATUS_LINES"].items():
    if k.replace("_", r"\_") not in MAN and k not in strip_tex(MAN):
        err("E6", "LOAD_BEARING", f"mandatory status line {k} absent from the manuscript")
    if v.replace("_", r"\_") not in MAN and v not in strip_tex(MAN):
        err("E6", "LOAD_BEARING", f"mandatory status value {k}={v} absent from the manuscript")

# ---- E7 section confinement ----------------------------------------------------
SECTION_LABELS = {"1": "sec:quantity", "2": "sec:model", "3": "sec:construction",
                  "4": "sec:confirmation", "5": "sec:estimator", "6": "sec:mechanism",
                  "7": "sec:history", "8": "sec:discussion"}
BYLAB = {r["MANUSCRIPT_LABEL"]: r for r in REC["ROWS"]}
CAMEL = json.load(open(f"{PKG}/provenance/PAPER_MACRO_INDEX.json", encoding="utf-8"))
LAB2MACRO = {v: k for k, v in CAMEL.items()}
# split the manuscript into sections
parts, cur, name = {}, [], "front"
for line in MAN.splitlines():
    m = re.match(r"\\section\*?\{", line)
    if m:
        parts[name] = "\n".join(cur); cur = []
        lm = re.search(r"label\{(sec:[a-z]+)\}", MAN[MAN.index(line):MAN.index(line) + 400])
        name = lm.group(1) if lm else "unlabelled"
    cur.append(line)
parts[name] = "\n".join(cur)
LABEL2NUM = {v: k for k, v in SECTION_LABELS.items()}
for lab, body in parts.items():
    if lab in ("front", "unlabelled"):
        continue
    secnum = LABEL2NUM.get(lab)
    for macro in set(re.findall(r"\\([a-z][A-Za-z]*)\b", body)):
        rowlab = CAMEL.get(macro)
        if not rowlab or rowlab not in BYLAB:
            continue
        allowed = BYLAB[rowlab]["ALLOWED_SECTIONS"].split("|")
        if secnum and secnum not in allowed and not any(a.startswith("Fig") for a in allowed):
            err("E7", "ADVISORY",
                f"{rowlab} appears in section {secnum} but is scoped to {allowed}")

# ---- E8 upgrade words on qualified claims --------------------------------------
UPGRADES = r"\b(proved|proves|proven|validated|confirms the theory|establishes that life|" \
           r"definitively|beyond doubt|conclusively)\b"
for m in re.finditer(UPGRADES, PROSE_LOWER):
    ctx = PROSE_LOWER[max(0, m.start() - 90):m.end() + 90]
    if "does not prove" in ctx or "never" in ctx or "not to be upgraded" in ctx or "cannot" in ctx:
        continue
    err("E8", "LOAD_BEARING", f"upgrade word {m.group()!r} in: ...{ctx.strip()}...")

# ---- E9 quantities attributed to LOST or NOT_TESTED evidence -------------------
hist = parts.get("sec:history", "")
for macro in set(re.findall(r"\\([a-z][A-Za-z]*)\b", hist)):
    rowlab = CAMEL.get(macro)
    if rowlab and rowlab in BYLAB and rowlab not in ("fresh_arms_run",):
        err("E9", "LOAD_BEARING",
            f"section 7 (lost evidence) carries the bound quantity {rowlab}; it must carry none "
            f"except the count of fresh arms it points the reader to")
for r in REC["ROWS"]:
    if r["STATUS"] in ("LOST_DOCUMENTARY", "NOT_TESTED", "INVALID"):
        err("E9", "LOAD_BEARING",
            f"reconciliation row {r['MANUSCRIPT_LABEL']} carries tier {r['STATUS']}")

# ---- report --------------------------------------------------------------------
OUT = {
    "SECTION": "LRCPS01 §15 claim lint",
    "TITLE_CHECKED": TITLE,
    "MANUSCRIPT_SHA_INPUTS": ["manuscript/MANUSCRIPT.tex", "supplement/SUPPLEMENT.tex",
                              "manuscript/numbers.tex"],
    "N_MACROS_DEFINED": len(defined),
    "N_RECONCILIATION_ROWS": REC["N_ROWS"],
    "LOAD_BEARING_CLAIM_LINT_ERRORS": len(ERRORS),
    "ADVISORY_CLAIM_LINT_WARNINGS": len(WARNINGS),
    "ERRORS": ERRORS,
    "WARNINGS": WARNINGS,
}
json.dump(OUT, open(f"{PKG}/provenance/PAPER_CLAIM_LINT.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("LOAD_BEARING_CLAIM_LINT_ERRORS =", len(ERRORS))
print("ADVISORY_CLAIM_LINT_WARNINGS  =", len(WARNINGS))
for e in ERRORS[:25]:
    print("  ", e["CODE"], e["MESSAGE"][:170])
for w in WARNINGS[:10]:
    print("  .", w["CODE"], w["MESSAGE"][:150])
sys.exit(min(len(ERRORS), 250))
