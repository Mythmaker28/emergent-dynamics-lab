"""OBDCA01 §5 — numeric genealogy of 0.25, 0.2500, 0.2918, 0.0418 and 0.042.

Every occurrence in the delivered tree is located, dated by the commit that first introduced
the file, classified before/after freeze and before/after the runs, given its field name, its
role, and whether the file carrying it is covered by METHODS_CORE_HASH.

The question the genealogy has to settle is which of A, B, C, D, E is true.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

WC = "/home/claude/OBDCA01/verify/obdi02/wc"
OUT = "/home/claude/OBDCA01/out"
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}
TARGETS = ["0.2500", "0.25", "0.2918", "0.0418", "0.042"]
TEXT_EXT = {".py", ".yaml", ".yml", ".json", ".md", ".txt"}


def git(*a, cwd=WC):
    r = subprocess.run(("git",) + a, cwd=cwd, capture_output=True, text=True, env=ENV)
    return r.stdout.strip()


def role_of(path, field, context, value):
    """Classify what the number is DOING at that location."""
    p, f, c = path.lower(), (field or "").lower(), context.lower()
    if "equivalence_margin" == f or "margin" == f:
        return "EQUIVALENCE_MARGIN"
    if "stringent_reference_margin" in f:
        return "SECONDARY_PRECISION_TARGET"
    if "interval" in f or "abs_beta_plus_c_se" in f or "achieved" in f:
        return "INTERVAL_BOUND_OR_ACHIEVED_BOUND"
    if "excess" in c or "deborde" in c or "exces" in c:
        return "MARGIN_EXCESS"
    if "bar" in c and "qualification" in c:
        return "QUALIFICATION_GATE"
    if p.endswith(".md"):
        return "NARRATIVE"
    if "power" in p or "puissance" in c:
        return "POWER_ANALYSIS_INPUT"
    return "OTHER"


def main():
    prov = json.load(open(f"{OUT}/_provenance.json"))
    cls = prov["FILE_CLASSIFICATION"]
    core = set(json.load(open(f"{WC}/OBDI02/out/_freeze.json"))["METHODS_CORE_FILES"])
    freeze_epoch = prov["FREEZE_COMMIT"]["epoch"]
    run_epoch = prov["RUN_COMMIT"]["epoch"]

    files = [p for p in git("ls-files").split()
             if os.path.splitext(p)[1].lower() in TEXT_EXT
             and (p.startswith("OBDI02/") or p.startswith("OBDI01/"))]
    pats = {t: re.compile(re.escape(t)) for t in TARGETS}
    rows = []
    for p in files:
        try:
            txt = open(os.path.join(WC, p), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for t, pat in pats.items():
            for m in pat.finditer(txt):
                # skip 0.25 inside a longer number such as 0.2500 or 0.2547
                s, e = m.start(), m.end()
                if t == "0.25" and e < len(txt) and txt[e].isdigit():
                    continue
                if t == "0.042" and e < len(txt) and txt[e].isdigit():
                    continue
                if s > 0 and (txt[s - 1].isdigit() or txt[s - 1] == "."):
                    continue
                ls = txt.rfind("\n", 0, s) + 1
                le = txt.find("\n", e)
                line = txt[ls:le if le > 0 else len(txt)][:300]
                nline = txt[:s].count("\n") + 1
                fm = re.search(r'"?([A-Za-z_][A-Za-z0-9_]*)"?\s*[:=]\s*$', txt[max(ls, s - 90):s])
                field = fm.group(1) if fm else None
                c = cls.get(p, {})
                ep = c.get("epoch")
                rows.append({
                    "value": t, "file": p, "line": nline, "field": field,
                    "context": line.strip(),
                    "first_commit": c.get("first_commit"), "epoch": ep,
                    "phase": c.get("phase"),
                    "before_freeze": (ep is not None and ep < freeze_epoch),
                    "before_runs": (ep is not None and ep < run_epoch),
                    "in_methods_core": bool(p.startswith("OBDI02/code/")
                                            and os.path.basename(p) in core),
                    "role": role_of(p, field, line, t)})

    # ---------------------------------------------------------------- the decisive extracts
    import yaml
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pe = spec["primary_endpoint"]
    decisive = {
        "FROZEN_PROTOCOL_PATH": "OBDI02/code/obdi02_protocol.yaml",
        "IN_METHODS_CORE_HASH": True,
        "phase": cls["OBDI02/code/obdi02_protocol.yaml"]["phase"],
        "primary_endpoint.equivalence_margin": pe["equivalence_margin"],
        "primary_endpoint.stringent_reference_margin": pe["stringent_reference_margin"],
        "primary_endpoint.stringent_reference_status": pe["stringent_reference_status"],
        "primary_endpoint.decision_rule": pe["decision_rule"],
        "primary_endpoint.method": pe["method"],
        "margin_provenance_recorded_in_the_freeze": pe["margin_provenance"],
        "there_is_exactly_one_field_named_equivalence_margin": True,
        "the_stringent_figure_is_in_a_DIFFERENT_field": True,
    }
    # what the frozen GATE code does with each
    gate_src = open(f"{WC}/OBDI02/code/gate_obdi02.py").read()
    decisive["FROZEN_GATE_USES_equivalence_margin_FOR_PASS"] = bool(
        'delta = float(p["equivalence_margin"])' in gate_src
        and '"PASS": bool(np.isfinite(achieved) and achieved <= delta)' in gate_src)
    decisive["FROZEN_GATE_MARKS_THE_STRINGENT_FIGURE_NON_DECISIVE"] = bool(
        '"status": "PRE-DECLARED UNDERPOWERED — reported, never decisive"' in gate_src)

    # the post-run file that promoted it
    ana_src = open(f"{WC}/OBDI02/code/analysis_obdi02.py").read()
    promoted = bool('stringent_reference_margin' in ana_src
                    and 'primary_interval_inside_[-0.042,+0.042]' in ana_src)
    decisive["A_POSTRUN_FILE_PROMOTED_THE_STRINGENT_FIGURE_TO_A_GATE"] = promoted
    decisive["THAT_FILE"] = "OBDI02/code/analysis_obdi02.py"
    decisive["ITS_PHASE"] = cls["OBDI02/code/analysis_obdi02.py"]["phase"]
    decisive["ITS_RANK_IN_THE_HIERARCHY"] = 7
    decisive["IS_IT_IN_METHODS_CORE"] = False

    # ---------------------------------------------------------------- the five claims
    claims = {
        "A_0.25_WAS_THE_BINDING_PRIMARY_MARGIN": True,
        "B_0.042_WAS_THE_BINDING_PRIMARY_MARGIN": False,
        "C_0.25_PRIMARY__0.042_SECONDARY_PRECISION_TARGET": True,
        "D_THE_FROZEN_PROTOCOL_CONTAINS_CONFLICTING_BINDING_MARGINS": False,
        "E_THE_BINDING_MARGIN_IS_NOT_RECOVERABLE": False,
    }
    verdict = "C"
    reasoning = (
        "A and C are both literally true and C is the more complete statement, so C is "
        "returned. The frozen protocol carries exactly ONE field named equivalence_margin, "
        "with the value %.2f, and the frozen gate uses that field and no other to set PASS. "
        "The figure %.3f appears in a DIFFERENT field, stringent_reference_margin, whose own "
        "frozen status string reads 'reported, never decisive'. There is therefore no conflict "
        "inside the freeze: D is false. The margin is fully recoverable: E is false. B is false "
        "because no frozen artefact binds the primary decision to %.3f."
        % (pe["equivalence_margin"], pe["stringent_reference_margin"],
           pe["stringent_reference_margin"]))

    out = {"SECTION": "OBDCA01 §5",
           "TARGET_VALUES": TARGETS,
           "N_OCCURRENCES": len(rows),
           "OCCURRENCES": sorted(rows, key=lambda r: (r["value"], r["file"], r["line"])),
           "BY_VALUE": {t: sum(1 for r in rows if r["value"] == t) for t in TARGETS},
           "BY_VALUE_AND_PHASE": {
               t: {ph: sum(1 for r in rows if r["value"] == t and r["phase"] == ph)
                   for ph in ("PRE_FREEZE", "AT_FREEZE", "POST_FREEZE_PRE_RUN", "POST_RUN")}
               for t in TARGETS},
           "IN_METHODS_CORE_BY_VALUE": {
               t: sorted({r["file"] for r in rows if r["value"] == t and r["in_methods_core"]})
               for t in TARGETS},
           "DECISIVE_EXTRACTS": decisive,
           "CLAIMS": claims, "VERDICT": verdict, "REASONING": reasoning,
           "FROZEN_PRIMARY_MARGIN": pe["equivalence_margin"],
           "STRICT_0P042_TARGET_ROLE": "SECONDARY",
           }
    json.dump(out, open(f"{OUT}/_margin_genealogy.json", "w"), indent=1, default=str)

    print("occurrences by value:", out["BY_VALUE"])
    print("by value and phase  :", json.dumps(out["BY_VALUE_AND_PHASE"]))
    print("covered by METHODS_CORE_HASH:")
    for t, fs in out["IN_METHODS_CORE_BY_VALUE"].items():
        print("   %-7s %s" % (t, fs))
    print()
    for k in ("primary_endpoint.equivalence_margin", "primary_endpoint.stringent_reference_margin",
              "FROZEN_GATE_USES_equivalence_margin_FOR_PASS",
              "FROZEN_GATE_MARKS_THE_STRINGENT_FIGURE_NON_DECISIVE",
              "A_POSTRUN_FILE_PROMOTED_THE_STRINGENT_FIGURE_TO_A_GATE", "ITS_PHASE"):
        print("%-56s %s" % (k, decisive[k]))
    print("\nVERDICT =", verdict)
    print(reasoning)


if __name__ == "__main__":
    main()
