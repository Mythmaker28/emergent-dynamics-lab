"""MYQBD01 §1 — bind the REPAIRED PMCR01 parent, from machine-readable evidence only.

No pre-repair claim is resurrected. The complete SHA is resolved; never the abbreviation.
"""
from __future__ import annotations

import hashlib
import json
import subprocess

REPO = "/home/claude/edl"
P = "PMCR01/out"
OUT = "/home/claude/MYQBD01/out"
REPAIRED_TIP = "8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367"


def git(*a):
    r = subprocess.run(("git",) + a, cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode


def blob(path):
    o, rc = git("show", "HEAD:%s" % path)
    return o if rc == 0 else None


def blobid(path):
    o, _ = git("rev-parse", "HEAD:%s" % path)
    return o


def main():
    head, _ = git("rev-parse", "HEAD")
    disp = json.loads(blob(f"{P}/PMCR01_FINAL_DISPOSITION.json"))
    matrix = json.loads(blob(f"{P}/PMCR01_REVIEW_REPAIR_MATRIX.json"))
    qev = json.loads(blob(f"{P}/PMCR01_Q_INSTRUMENTATION_EVIDENCE.json"))

    # the repaired parent must be the base and must carry the repaired disposition
    base_ok = head == REPAIRED_TIP or subprocess.run(
        ("git", "merge-base", "--is-ancestor", REPAIRED_TIP, head),
        cwd=REPO).returncode == 0

    # bind every load-bearing source and raw-data hash we will rely on
    exec_files = ["ORR01/code/kinetics.py", "ORR01/code/lawspec_v2.py",
                  "ORR01/code/observe.py", "OBTC02/code/engine_obtc.py",
                  "OBTC02/code/protocol_obtc02.py", "OBTC02/code/obtc02_protocol.yaml"]
    src_hashes = {f: blobid(f) for f in exec_files}

    # the frozen PMCR01 persistence/timing thresholds, read from the parent regions artefact
    rg = json.loads(blob(f"{P}/PMCR01_REACHABILITY_REGIONS.json"))
    cu = rg["CONSTANTS_USED"]
    thresholds = {
        "T_HORIZON": cu["T_HORIZON"], "T_WINDOW": cu["T_WINDOW"],
        "TAU_SEP_MOBILE": cu["TAU_SEP"], "D_REL": cu["D_REL"], "CORE_R": cu["CORE_R"],
        "CAP": cu["CAP"], "Q_MAX": cu["Q_MAX"],
        "ALPHA_SURVIVAL": 0.5, "N_STAR": 10.0, "GAMMA_SEP": 0.5, "MIN_EVENTS": 1.0,
        "SOURCE": "PMCR01_REACHABILITY_REGIONS.json CONSTANTS_USED + evaluate() thresholds",
    }

    out = {
        "SECTION": "MYQBD01 §1 parent binding",
        "PARENT_PROGRAM": "PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01",
        "PARENT_REPAIRED_TIP_EXPECTED": REPAIRED_TIP,
        "PARENT_REPAIRED_TIP_RESOLVED_FULL": head,
        "BASE_IS_THE_REPAIRED_TIP": base_ok,
        "REPAIRED_FINAL_DISPOSITION": disp["REPAIRED_FINAL_DISPOSITION"],
        "ARCHITECTURE_CHANGE_NECESSITY": disp["ARCHITECTURE_CHANGE_NECESSITY"],
        "EXISTING_Q_INSTRUMENTATION": disp["EXISTING_Q_INSTRUMENTATION"],
        "NEXT_SCIENTIFIC_ELIGIBILITY": disp["NEXT_SCIENTIFIC_ELIGIBILITY"],
        "MYCAD01_STATUS": disp["MYCAD01_STATUS"]["STATUS"],
        "REVIEW_CONFIRMED_DEFECTS": matrix["N_DEFECTS_CONFIRMED"],
        "REVIEW_EVERY_CONFIRMED_HANDLED": matrix["EVERY_CONFIRMED_DEFECT_HANDLED"],
        "Q_OBSERVER_BLOB": src_hashes["ORR01/code/observe.py"],
        "Q_ARMS_CONTAINING_Q_reported": qev["RECOMPUTED_Q"]["N_ARMS_CONTAINING_Q"],
        "SOURCE_HASHES": src_hashes,
        "FROZEN_PMCR01_THRESHOLDS": thresholds,
        "DO_NOT_RESURRECT": ("no pre-repair claim that a new precursor, species or architecture "
                             "change is already required. ARCHITECTURE_CHANGE_NECESSITY is "
                             "NOT_ESTABLISHED and stays so unless an exact operator proves "
                             "structural impossibility in THIS mission."),
        "GATE": None,
    }
    out["GATE"] = ("PROCEED" if (base_ok
                                 and disp["NEXT_SCIENTIFIC_ELIGIBILITY"]
                                 == "MINORITY_Y_Q_BOUND_DERIVATION_01"
                                 and disp["EXISTING_Q_INSTRUMENTATION"] == "CONFIRMED")
                   else "STOP")
    json.dump(out, open(f"{OUT}/MYQBD01_PARENT_BINDING.json", "w"), indent=1, default=str)
    for k in ("PARENT_REPAIRED_TIP_RESOLVED_FULL", "BASE_IS_THE_REPAIRED_TIP",
              "REPAIRED_FINAL_DISPOSITION", "ARCHITECTURE_CHANGE_NECESSITY",
              "EXISTING_Q_INSTRUMENTATION", "NEXT_SCIENTIFIC_ELIGIBILITY", "GATE"):
        print("%-38s %s" % (k, out[k]))


if __name__ == "__main__":
    main()
