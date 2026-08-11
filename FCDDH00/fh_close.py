"""FCDDH00 closure: decision matrix, manifest, SHA256SUMS scope and sums, verification report.

Schema frozen before construction. It only ASSEMBLES already-committed fields; it never
recomputes, reclassifies or selects a scientific verdict.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
CANON = [l.strip() for l in open(f"{HERE}/CANONICAL_FIELD_SCHEMA.txt") if l.strip()]

EXCLUDE_FROM_SUMS = {"SHA256SUMS"}
EXCLUDE_DIRS = {"_marks", "__pycache__"}


def jload(p, default=None):
    try:
        return json.load(open(os.path.join(HERE, p)))
    except Exception:
        return default


def decision_matrix():
    prov = jload("PARENT_PROVENANCE_BINDING.json", {})
    g1 = jload("G1_WITHIN_ANCESTRY_ELIGIBILITY_AUDIT.json", {})
    orc = jload("PREANALYSIS_ORACLE_REPORT.json", {})
    lic = jload("RANDOMIZATION_LICENSE.json", {})
    dpl = jload("FCDDH00_DISCOVERY_PANEL_LOCK.json", {})
    dth = jload("FCDDH00_DISCOVERY_THRESHOLD_LOCK.json", {})
    draw = jload("DISCOVERY_ACTIVE_RAW_MANIFEST.json", {})
    dg = jload("DISCOVERY_GATE_LADDER.json", {})
    hpl = jload("FCDDH00_HOLDOUT_PANEL_LOCK.json", {})
    hth = jload("FCDDH00_HOLDOUT_THRESHOLD_LOCK.json", {})
    hraw = jload("HOLDOUT_ACTIVE_RAW_MANIFEST.json", {})
    hg = jload("HOLDOUT_GATE_LADDER.json", {})
    dev = jload("_start_totals.json", {})

    NR = "NOT_REACHED_BY_PREDECLARED_STOP"
    m = {}
    m["FCDDH00_PROVENANCE_STATUS"] = prov.get("FCDDH00_PROVENANCE_STATUS", "UNRESOLVED")
    m["FCDDH00_G1_STATIC_ELIGIBILITY"] = g1.get("FCDDH00_G1_STATIC_ELIGIBILITY", "UNRESOLVED")
    m["FCDDH00_PREANALYSIS_ORACLE_STATUS"] = orc.get("FCDDH00_PREANALYSIS_ORACLE_STATUS", "UNRESOLVED")
    m["FCDDH00_RANDOMIZATION_LICENSE"] = str(lic.get("FCDDH00_RANDOMIZATION_LICENSE", "UNRESOLVED"))
    m["PROTOCOL_CONFORMITY_STATUS"] = dev.get("PROTOCOL_CONFORMITY_STATUS", "UNRESOLVED")
    m["RAW_EVIDENCE_COMPLETENESS_STATUS"] = dev.get("RAW_EVIDENCE_COMPLETENESS_STATUS", "UNRESOLVED")
    m["ENGINE_START_LEDGER_STATUS"] = dev.get("ENGINE_START_LEDGER_STATUS", "UNRESOLVED")
    m["DISCOVERY_CONSTRUCTION_STATUS"] = dpl.get("DISCOVERY_CONSTRUCTION_STATUS", NR)
    m["DISCOVERY_SHAM_STATUS"] = dth.get("DISCOVERY_SHAM_STATUS", NR)
    m["DISCOVERY_RAW_ACTIVE_STATUS"] = ("COMPLETE_96_OF_96" if draw.get("COMPLETE") else
                                        (f"INCOMPLETE_{draw.get('rows')}_OF_96" if draw else NR))
    m["DISCOVERY_PANEL_STATUS"] = ("SEALED_12_BLOCKS_48_DESCENDANTS" if dpl.get("PANEL_COMPLETE")
                                   else (dpl.get("DISCOVERY_CONSTRUCTION_STATUS", NR)))
    for k in ("DISCOVERY_CELL_MATERIALITY_STATUS", "DISCOVERY_DIRECT_CARRIER_CONTRAST_STATUS",
              "DISCOVERY_AXIS_IDENTIFIABILITY_STATUS", "DISCOVERY_AXIS_STABILITY_STATUS",
              "DISCOVERY_INTERACTION_ABSOLUTE_MATERIALITY_STATUS",
              "DISCOVERY_ALLOCATION_ORBIT_ROBUSTNESS_STATUS", "DISCOVERY_AXIS_SERIALIZATION_STATUS"):
        m[k] = dg.get(k, NR)
    m["HOLDOUT_CONSTRUCTION_STATUS"] = hpl.get("HOLDOUT_CONSTRUCTION_STATUS", NR)
    m["HOLDOUT_SHAM_STATUS"] = hth.get("HOLDOUT_SHAM_STATUS", NR)
    m["HOLDOUT_RAW_ACTIVE_STATUS"] = ("COMPLETE_128_OF_128" if hraw.get("COMPLETE") else
                                      (f"INCOMPLETE_{hraw.get('rows')}_OF_128" if hraw else NR))
    m["HOLDOUT_PANEL_STATUS"] = ("SEALED_16_BLOCKS_64_DESCENDANTS" if hpl.get("PANEL_COMPLETE")
                                 else hpl.get("HOLDOUT_CONSTRUCTION_STATUS", NR))
    for k in ("HOLDOUT_CELL_MATERIALITY_STATUS", "HOLDOUT_DIRECT_CARRIER_CONTRAST_STATUS",
              "HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS",
              "HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS",
              "HOLDOUT_ALLOCATION_AVERAGED_DIRECTION_SECONDARY_STATUS",
              "HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS",
              "HOLDOUT_ALLOCATION_ORBIT_ROBUSTNESS_STATUS",
              "P2_HOLDOUT_DESCENDANT_SCORE_STATUS", "P2_HOLDOUT_DESCENDANT_EXCEED_COUNT_OF_64",
              "P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16", "P2_HOLDOUT_GENERATOR_INTERVAL_LICENSE"):
        m[k] = hg.get(k, NR)
    m["FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS"] = "FAILED_AS_PREDECLARED"
    m["P2_POPULATION_TRANSFER_INTERPRETATION"] = "INCONCLUSIVE_FROM_THIS_GATE_ALONE"
    for k in ("DISCOVERY_CONSTRUCTION_STARTS", "DISCOVERY_SHAM_STARTS", "DISCOVERY_ACTIVE_STARTS",
              "HOLDOUT_CONSTRUCTION_STARTS", "HOLDOUT_SHAM_STARTS", "HOLDOUT_ACTIVE_STARTS",
              "OTHER_STARTS", "TOTAL_CHARGED_STARTS", "TOTAL_RAW_ADVANCE_SEQUENCES"):
        m[k] = dev.get(k, 0)
    missing = [f for f in CANON if f not in m]
    extra = [f for f in m if f not in CANON]
    assert not missing and not extra, "canonical schema violation: missing=%s extra=%s" % (missing, extra)
    return m


def top_level(m):
    if m["FCDDH00_PROVENANCE_STATUS"] != "PASS" or m["FCDDH00_G1_STATIC_ELIGIBILITY"] != "PASS":
        return "PARENT_PROVENANCE_OR_G1_ELIGIBILITY_UNRESOLVED__ZERO_STARTS"
    if m["FCDDH00_PREANALYSIS_ORACLE_STATUS"] != "PASS":
        return "PREANALYSIS_ORACLE_OR_LOCK_FAIL__ZERO_STARTS"
    if not str(m["DISCOVERY_CONSTRUCTION_STATUS"]).startswith("COMPLETE"):
        return "DISCOVERY_COMPLETE_FACTORIAL_PANEL_INCOMPLETE__ZERO_HOLDOUT_STARTS"
    if m["DISCOVERY_SHAM_STATUS"] != "COMPLETE" or not str(m["DISCOVERY_RAW_ACTIVE_STATUS"]).startswith("COMPLETE"):
        return "DISCOVERY_SHAM_OR_ACTIVE_PANEL_INCOMPLETE__NO_AXIS__ZERO_HOLDOUT_STARTS"
    if m["DISCOVERY_AXIS_SERIALIZATION_STATUS"] != "SERIALIZED":
        return "DISCOVERY_AXIS_NOT_LICENSED__ZERO_HOLDOUT_STARTS__FAILED_GATES=" + \
            str(m["DISCOVERY_AXIS_SERIALIZATION_STATUS"]).split("FAILED_GATES=")[-1]
    if not str(m["HOLDOUT_RAW_ACTIVE_STATUS"]).startswith("COMPLETE"):
        return "DISCOVERY_DIFFERENTIAL_AXIS_SERIALIZED__HOLDOUT_PANEL_INCOMPLETE__VALIDATION_NOT_EVALUABLE"
    r = m["HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS"]
    mat = m["HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS"]
    if r == "RANDOMIZED_HOLDOUT_VALIDATED":
        return ("HOLDOUT_COMPLETE__RANDOMIZED_DIFFERENTIAL_INTERACTION_VALIDATED__ABSOLUTELY_MATERIAL__FULL_ALLOCATION_ORBIT_ROBUST"
                if mat == "FIXED_DIRECTION_ABSOLUTELY_MATERIAL" else
                "HOLDOUT_COMPLETE__RANDOMIZED_DIFFERENTIAL_INTERACTION_VALIDATED__BELOW_ABSOLUTE_MATERIALITY")
    if r == "FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_LICENSED":
        return "HOLDOUT_COMPLETE__FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_LICENSED"
    if m["HOLDOUT_ALLOCATION_AVERAGED_DIRECTION_SECONDARY_STATUS"] == "PASS":
        return "HOLDOUT_COMPLETE__ALLOCATION_AVERAGED_DIRECTION_ONLY__PRIMARY_NOT_VALIDATED"
    if r == "NUMERICALLY_OR_GAUGE_UNRESOLVED":
        return "NUMERICALLY_OR_GAUGE_UNRESOLVED"
    return "HOLDOUT_COMPLETE__FIXED_DIFFERENTIAL_INTERACTION_NOT_VALIDATED"


def walk_files():
    out = []
    for dp, dn, fn in os.walk(HERE):
        dn[:] = [d for d in dn if d not in EXCLUDE_DIRS and not d.startswith("_marks")]
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), HERE)
            if rel in EXCLUDE_FROM_SUMS or rel.startswith("_marks/") or "__pycache__" in rel:
                continue
            if rel.startswith("_") and rel.endswith(".txt") and "parent_tip_blobs" in rel:
                continue
            out.append(rel)
    return sorted(out)


def main():
    m = decision_matrix()
    disp = top_level(m)
    json.dump({"FCDDH00_DECISION_MATRIX": m, "TOP_LEVEL_DISPOSITION": disp,
               "canonical_field_count": len(CANON)},
              open(f"{HERE}/FCDDH00_DECISION_MATRIX.json", "w"), indent=1)
    files = walk_files()
    json.dump({"scope": files, "excluded": sorted(EXCLUDE_FROM_SUMS) +
               ["_marks/**", "__pycache__/**", "the out-of-tree final git bundle", "git metadata"],
               "self_referential": False, "n_files": len(files)},
              open(f"{HERE}/SHA256SUMS_SCOPE.json", "w"), indent=1)
    files = json.load(open(f"{HERE}/SHA256SUMS_SCOPE.json"))["scope"]
    with open(f"{HERE}/SHA256SUMS", "w") as f:
        for rel in files:
            f.write("%s  %s\n" % (sha(os.path.join(HERE, rel)), rel))
    print("decision:", disp, "| files in scope:", len(files))
    return m, disp


if __name__ == "__main__":
    main()
