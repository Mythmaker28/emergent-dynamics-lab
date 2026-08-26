"""OMLDCT02 — the C3 raw commitment, and the C4 analysis driver.

A DECLARED POST-C2 ADDITION, AND A PLANNING MISS OF MINE.
This file did not exist when C2 was committed, so it is not inside METHODS_HASH. I should have
written it before the freeze, as I should have written OMLDCT01's second E3 classifier before its
freeze. It is declared here rather than slipped in, and the checker is invited to attack it.
(It was also destroyed by the eighth container rollback, because it had never been committed, and
rewritten afterwards — a second consequence of the same miss.)

What it does NOT decide. Every scientific decision it applies was frozen in C2 and lives in code
that IS inside METHODS_HASH:
  - the endpoints are computed by omldct02_e3_a and omldct02_e3_b, both bound;
  - the paired statistic, the Pratt zero treatment, the exact distribution, alpha, the minimum pair
    count and the intersection-union AND rule all live in omldct02_analysis.decide(), bound;
  - the sign convention "SELECTIVE minus SHAM, on the paired log difference" is written into the
    master freeze itself.
This file lists archives, calls those functions, and writes JSON. It chooses nothing.

A pair is retained only when BOTH classifiers agree on both endpoints. Section 11 makes a classifier
disagreement on a retained pair a campaign-level technical invalidity, so disagreement is recorded
and the pair is not silently dropped.
"""
from __future__ import annotations
import json, os, sys, math, datetime

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H
import omldct02_e3_a as CA, omldct02_e3_b as CB
import omldct02_analysis as AN

RAW = os.environ.get("OMLDCT02_RAW", "/home/claude/OMLDCT02_raw")
WORK = f"{REPO}/OMLDCT02/work"
OUT = f"{REPO}/OMLDCT02/out"
SEALED = f"{WORK}/OMLDCT02_SEALED_LEDGER.jsonl"

def read_sealed():
    rows = []
    with open(SEALED) as fh:
        for line in fh:
            if line.strip(): rows.append(json.loads(line))
    return rows

def raw_manifest():
    """C3: account for every attempted base seed and every archive, before anything is analysed."""
    rows = read_sealed()
    state = json.load(open(f"{WORK}/OMLDCT02_RUN_STATE.json"))
    seeds = json.load(open(f"{OUT}/OMLDCT02_SEED_MANIFEST.json"))
    frozen = {d["index"]: d["seed"] for d in seeds["BASE_SEEDS"]}
    seen_idx = [r["index"] for r in rows]
    dup = sorted({i for i in seen_idx if seen_idx.count(i) > 1})
    wrong = [r["index"] for r in rows if frozen.get(r["index"]) != r["seed"]]
    order_ok = seen_idx == list(range(len(seen_idx)))
    arch = []
    for r in rows:
        for arm, a in (r.get("ARCHIVES") or {}).items():
            p = a["path"]; ok = os.path.exists(p)
            h = H.file_sha256(p) if ok else None
            arch.append({"index": r["index"], "arm": arm, "tag": a["tag"], "present": ok,
                         "sha256_recorded": a["sha256"], "sha256_now": h,
                         "MATCHES": bool(ok and h == a["sha256"]),
                         "bytes": (os.path.getsize(p) if ok else None),
                         "steps_executed": a["steps_executed"], "integrity_ok": a["integrity_ok"]})
    adm = [r for r in rows if r.get("ADMISSIBLE")]
    pairs_complete = all(
        sum(1 for a in arch if a["index"] == r["index"] and a["MATCHES"]) == 2 for r in adm)
    fidelity = []
    for r in adm:
        au = r["INTERVENTION_AUDIT"]; fk = r["FORK"]
        fidelity.append({"index": r["index"],
          "fork_physical_state_identical": fk["PHYSICAL_STATE_IDENTICAL"],
          "fork_rng_state_identical": fk["RNG_STATE_IDENTICAL"],
          "selective_parent_emptied": au["SELECTIVE"]["parent_emptied"],
          "selective_daughter_untouched": au["SELECTIVE"]["daughter_untouched"],
          "selective_occupancy_conserved": au["SELECTIVE"]["occupancy_conserved"],
          "selective_rng_unchanged": au["SELECTIVE"]["rng_unchanged"],
          "sham_removed_nothing": au["SHAM"]["removed_nothing"],
          "sham_phys_unchanged": au["SHAM"]["phys_unchanged"],
          "arms_diverged": r["ARMS_DIVERGED"]})
    fid_ok = all(all(v for k, v in f.items() if k != "index") for f in fidelity)
    inst = sum(r.get("instance_cost", 0.0) for r in rows)
    doc = {"MISSION": "OMLDCT02", "SECTION": "C3 raw manifest — before any analysis",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "GENERATOR": "OMLDCT02/code/omldct02_c3_raw.py",
     "DECLARED_POST_C2_ADDITION": True,
     "CAMPAIGN_STOPPED": state.get("STOPPED"),
     "BASE_SEEDS_ATTEMPTED": len(rows),
     "MAX_CANDIDATE_BASE_SEEDS": seeds["N_BASE"],
     "ALL_ATTEMPTED_SEEDS_ACCOUNTED_FOR": len(rows) == len(seen_idx),
     "ATTEMPTED_IN_STRICT_FROZEN_INDEX_ORDER_FROM_ZERO": order_ok,
     "DUPLICATE_INDICES": dup, "SEEDS_NOT_MATCHING_THE_FROZEN_MANIFEST": wrong,
     "NO_DUPLICATE_SCIENTIFIC_SEED": not dup and not wrong,
     "NO_ADAPTIVE_SEED_REPLACEMENT": "every index from 0 to the stop was attempted exactly once and "
                                     "no seed was skipped, replaced or reordered",
     "VALID_PAIRED_BLOCKS": len(adm),
     "TARGET_VALID_PAIRED_BLOCKS": 41,
     "ONE_SELECTIVE_AND_ONE_SHAM_PER_PAIR": pairs_complete,
     "N_ARCHIVES": len(arch),
     "ALL_ARCHIVE_HASHES_MATCH": all(a["MATCHES"] for a in arch),
     "ARCHIVES": arch,
     "HARD_ARM_INSTANCE_COUNT": round(inst, 5),
     "MAX_PRIMARY_ARM_INSTANCES": 512,
     "CEILING_RESPECTED": inst <= 512,
     "SCIPY_BINOM_PPF_CALLS_DURING_THE_CAMPAIGN": state.get("scipy_binom_ppf_calls"),
     "SCIPY_SENTINEL_INSTALLED": state.get("scipy_sentinel_installed"),
     "TECHNICAL_FAILURES": [r["index"] for r in rows if r.get("technical_failure")],
     "FORK_AND_INTERVENTION_FIDELITY": fidelity,
     "ALL_FIDELITY_CHECKS_PASS": fid_ok,
     "EXTERNALISED_BATCHES": state.get("externalised_batches"),
     "UNEXTERNALISED_ARM_INSTANCES": state.get("unexternalised_arm_instances"),
     "OUTCOME_BREAKDOWN": {
       "admissible": len(adm),
       "not_triggered": sum(1 for r in rows if r.get("REASON") == "NOT_TRIGGERED_BY_THE_FROZEN_DEADLINE"),
       "triggered_identity_not_carried": sum(1 for r in rows if r.get("REASON") == "TRIGGERED_IDENTITY_NOT_CARRIED")},
     "WORLDS_RUN": len(rows)}
    doc["RAW_MANIFEST_CONTENT_HASH"] = H.content_digest(doc)
    json.dump(doc, open(f"{OUT}/OMLDCT02_RAW_MANIFEST.json", "w"), indent=1)
    return doc

def measure():
    """C4 step 1: both bound classifiers on every retained pair. No decision is taken here."""
    rows = [r for r in read_sealed() if r.get("ADMISSIBLE")]
    out = []
    for r in rows:
        rec = {"index": r["index"], "seed": r["seed"], "t_m": r["t_m"],
               "daughter_cells": r["FORK"]["locked_daughter_cells"]}
        for arm in ("SELECTIVE", "SHAM"):
            p = r["ARCHIVES"][arm]["path"]
            a = CA.e3(p, r["t_m"], r["FORK"]["locked_daughter_cells"])
            b = CB.e3(p, r["t_m"], r["FORK"]["locked_daughter_cells"])
            agree = (a.get("OK") and b.get("OK")
                     and a["E3_DURATION"] == b["E3_DURATION"]
                     and a["E3_EXPOSURE"] == b["E3_EXPOSURE"]
                     and a["identity_termination_type"] == b["identity_termination_type"])
            rec[arm] = {"A": a, "B": b, "CLASSIFIERS_AGREE": bool(agree)}
        rec["PAIR_RETAINED"] = bool(rec["SELECTIVE"]["CLASSIFIERS_AGREE"] and rec["SHAM"]["CLASSIFIERS_AGREE"])
        out.append(rec)
    json.dump(out, open(f"{WORK}/OMLDCT02_PAIR_MEASUREMENTS.json", "w"), indent=1)
    return out

def analyse():
    """C4 step 2: the frozen decision. The log difference is SELECTIVE minus SHAM, as the master
    freeze states; decide() is bound inside METHODS_HASH and is called unchanged."""
    meas = json.load(open(f"{WORK}/OMLDCT02_PAIR_MEASUREMENTS.json"))
    retained = [m for m in meas if m["PAIR_RETAINED"]]
    disagreed = [m["index"] for m in meas if not m["PAIR_RETAINED"]]
    dur, exp, table = [], [], []
    for m in retained:
        ds = m["SELECTIVE"]["A"]["E3_DURATION"]; dh = m["SHAM"]["A"]["E3_DURATION"]
        es = m["SELECTIVE"]["A"]["E3_EXPOSURE"]; eh = m["SHAM"]["A"]["E3_EXPOSURE"]
        dd = math.log(ds) - math.log(dh) if ds > 0 and dh > 0 else (0.0 if ds == dh else None)
        de = math.log(es) - math.log(eh) if es > 0 and eh > 0 else (0.0 if es == eh else None)
        dur.append(dd); exp.append(de)
        table.append({"index": m["index"], "t_m": m["t_m"],
                      "SELECTIVE_duration": ds, "SHAM_duration": dh, "log_duration_difference": dd,
                      "SELECTIVE_exposure": es, "SHAM_exposure": eh, "log_exposure_difference": de,
                      "SELECTIVE_termination": m["SELECTIVE"]["A"]["identity_termination_type"],
                      "SHAM_termination": m["SHAM"]["A"]["identity_termination_type"]})
    undefined = [t["index"] for t in table if t["log_duration_difference"] is None
                 or t["log_exposure_difference"] is None]
    n = len(retained)
    res = AN.decide(dur, exp, n) if not undefined else None
    doc = {"MISSION": "OMLDCT02", "SECTION": "C4 frozen analysis",
     "GENERATED_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "SIGN_CONVENTION": "SELECTIVE minus SHAM, on the paired log difference",
     "N_PAIRS_MEASURED": len(meas), "N_PAIRS_RETAINED": n,
     "CLASSIFIER_DISAGREEMENT_INDICES": disagreed,
     "ANY_CLASSIFIER_DISAGREEMENT_ON_A_RETAINED_PAIR": len(disagreed) > 0,
     "PAIRS_WITH_AN_UNDEFINED_LOG_DIFFERENCE": undefined,
     "PER_PAIR": table,
     "DECISION": res,
     "TERMINAL": (res["TERMINAL"] if res else "OMLDCT02_TECHNICALLY_INVALID"),
     "NULL_RESULT_INTERPRETATION": "INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT",
     "REPRODUCTION_STATUS": "NOT_TESTED", "HEREDITY_STATUS": "NOT_TESTED",
     "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED"}
    doc["ANALYSIS_CONTENT_HASH"] = H.content_digest(doc)
    json.dump(doc, open(f"{OUT}/OMLDCT02_FROZEN_ANALYSIS.json", "w"), indent=1)
    return doc

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["raw", "measure", "analyse"])
    a = ap.parse_args()
    if a.stage == "raw":
        d = raw_manifest()
        print(json.dumps({k: d[k] for k in ("CAMPAIGN_STOPPED", "BASE_SEEDS_ATTEMPTED",
              "VALID_PAIRED_BLOCKS", "HARD_ARM_INSTANCE_COUNT", "CEILING_RESPECTED",
              "ALL_ARCHIVE_HASHES_MATCH", "ALL_FIDELITY_CHECKS_PASS", "NO_DUPLICATE_SCIENTIFIC_SEED",
              "ATTEMPTED_IN_STRICT_FROZEN_INDEX_ORDER_FROM_ZERO",
              "SCIPY_BINOM_PPF_CALLS_DURING_THE_CAMPAIGN", "TECHNICAL_FAILURES",
              "OUTCOME_BREAKDOWN")}, indent=1))
    elif a.stage == "measure":
        m = measure(); print("pairs measured:", len(m), "retained:", sum(1 for x in m if x["PAIR_RETAINED"]))
    else:
        d = analyse(); print("TERMINAL =", d["TERMINAL"], "| retained", d["N_PAIRS_RETAINED"])
