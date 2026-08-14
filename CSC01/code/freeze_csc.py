"""CSC01 §16 — the freeze. Executed BEFORE the first confirmation start."""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import gatelib as GL             # noqa: E402
import guard_csc as GC           # noqa: E402
import mechanisms as M           # noqa: E402

CODE = "/home/claude/CSC01/code"
OUT = "/home/claude/CSC01/out"
CORE = ("localization_gate.yaml", "gatelib.py", "lawspec_v3.py", "protocol_csc.py",
        "spatial.py", "nulls.py", "null_n3b.py", "mechanisms.py", "guard_csc.py",
        "calibrate.py", "audit_csc.py", "replay.py", "autopsy.py", "run_autopsy.py",
        "stage_a.py", "tests_csc.py", "_n1_table.json")
DOCS = ("_provenance.json", "_calibration.json", "_audit.json", "_stage_a.json",
        "_decisions.json", "_null_n3b.json", "_tests_stage_a.json",
        "CSC01_AUTOPSY_PREPLAN.md", "CSC01_APPEND_ONLY_CORRECTIONS.md",
        "CSC01_INHERITANCE_NOTE.md")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    code = {f: sha(os.path.join(CODE, f)) for f in CORE if os.path.exists(os.path.join(CODE, f))}
    docs = {f: sha(os.path.join(OUT, f)) for f in DOCS if os.path.exists(os.path.join(OUT, f))}
    h = hashlib.sha256()
    for f in sorted(code):
        h.update(f.encode())
        h.update(code[f].encode())
    methods_core = h.hexdigest()
    cal = json.load(open(f"{OUT}/_calibration.json"))
    aud = json.load(open(f"{OUT}/_audit.json"))
    prov = json.load(open(f"{OUT}/_provenance.json"))
    dec = json.load(open(f"{OUT}/_decisions.json"))
    sa = json.load(open(f"{OUT}/_stage_a.json"))
    winner, table, unique = M.select()
    spec = GL.load()
    out = {
        "FREEZE": 1,
        "frozen_before": "the first confirmation start of CSC01",
        "METHODS_CORE_HASH": methods_core,
        "code_sha256": code, "doc_sha256": docs,
        "gate_spec_sha256": GL.spec_sha256(),
        "gate_spec": spec,
        "mechanism_selection": {"winner": winner, "unique": unique, "table": table,
                                "rule": [(s, d) for s, d, _ in M.RULE]},
        "calibration": {"m_star": cal["m_star"], "lambda": cal["lambda"],
                        "mu_eff_at_m_star": cal["mu_eff_at_m_star"],
                        "ell_X_isolated": cal["ell_X_isolated"],
                        "ell_X_at_m_star": cal["ell_X_at_m_star"],
                        "STATUS": cal["STATUS"], "seeds": cal["rule"]["assay_seeds"]},
        "PROTOCOL_ADVERSARIAL_AUDIT": aud["PROTOCOL_ADVERSARIAL_AUDIT"],
        "GATE_SINGLE_SOURCE_OF_TRUTH": "PASS" if aud["GATE_SINGLE_SOURCE_OF_TRUTH"] else "FAIL",
        "ONLINE_POSTHOC_SYNTHETIC_AGREEMENT":
            "PASS" if aud["ONLINE_POSTHOC_SYNTHETIC_AGREEMENT"] else "FAIL",
        "PROVENANCE_STATUS": prov["PROVENANCE_STATUS"],
        "VERDICT_QUESTION_A": sa["VERDICT_QUESTION_A"],
        "C5_SCOPE": dec["section_6_C5_scope"]["C5_SCOPE"],
        "INTRINSIC_LOCALIZATION_MECHANISM":
            dec["section_7_intrinsic_mechanism"]["INTRINSIC_LOCALIZATION_MECHANISM"],
        "ROUTE": dec["section_8_route"]["ROUTE"],
        "starts_before_this_freeze": {k: GC.used(k) for k in GC.CAPS},
        "starts_before_this_freeze_note":
            "the calibration assay is the only class consumed before the freeze; it is passive "
            "and reads one structural statistic. raw_replay is non-scientific by declaration.",
        "H3_STATUS": "NOT_TESTED",
        "REPRODUCTION_STATUS": "NOT_TESTED",
    }
    json.dump(out, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)
    print("METHODS_CORE_HASH = %s" % methods_core)
    print("gate spec sha256  = %s" % out["gate_spec_sha256"])
    print("mechanism         = %s (unique = %s)" % (winner, unique))
    print("lambda            = %.6f  from m_star = %d" % (cal["lambda"], cal["m_star"]))
    print("audit             = %s" % out["PROTOCOL_ADVERSARIAL_AUDIT"])
    print("files frozen      = %d code, %d docs" % (len(code), len(docs)))


if __name__ == "__main__":
    main()
