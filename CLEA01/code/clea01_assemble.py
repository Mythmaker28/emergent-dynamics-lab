"""CLEA01 — assemble sections 4, 5 and 7 from the completed sweeps. Reads results only."""
from __future__ import annotations
import json, os, sys, csv, statistics
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
import omldct02_hashes as H
W = f"{REPO}/CLEA01/work"; O = f"{REPO}/CLEA01/out"

def total_xbirths_after(path, t_m):
    z = np.load(path, allow_pickle=True); xb = z["xbirth"]; z.close()
    if xb.size == 0: return 0
    return int((xb[:, 0].astype(np.int64) > t_m).sum())

def load():
    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    by = {r["index"]: r for r in led if r.get("ADMISSIBLE")}
    meas = {m["index"]: m for m in json.load(open(f"{REPO}/OMLDCT02/work/OMLDCT02_PAIR_MEASUREMENTS.json"))}
    res = {}; spec = {}; g4 = {}
    for f in ("dev_results", "val_results"): res.update(json.load(open(f"{W}/{f}.json")))
    for f in ("dev_spec", "val_spec"): spec.update(json.load(open(f"{W}/{f}.json")))
    for f in ("dev_g4", "val_g4"): g4.update(json.load(open(f"{W}/{f}.json")))
    sm = json.load(open(f"{O}/CLEA01_SPLIT_MANIFEST.json"))
    split = {p["index"]: p["SPLIT"] for p in sm["PAIRS"]}
    return by, meas, res, spec, g4, split

def main():
    by, meas, res, spec, g4, split = load()
    rows = []
    for k in sorted(res, key=int):
        i = int(k)
        for arm in ("SELECTIVE", "SHAM"):
            c = res[k][arm]["C_impl1"]; c2 = res[k][arm]["C_impl2"]
            b = res[k][arm]["B"]; a = meas[i][arm]["A"]
            sp = spec[k][arm]; gg = g4[k][arm]
            tot_x = total_xbirths_after(by[i]["ARCHIVES"][arm]["path"], by[i]["t_m"])
            rows.append({
              "index": i, "arm": arm, "split": split[i], "t_m": by[i]["t_m"],
              "root_size": res[k]["root_size"],
              "A_duration": a["E3_DURATION"], "A_exposure": a["E3_EXPOSURE"],
              "A_terminal": a["identity_termination_type"],
              "B_duration": b["AMBIENT_duration"], "B_exposure": b["AMBIENT_exposure"],
              "B_terminal": b["AMBIENT_terminal"],
              "C_certain_duration": c["CERTAIN_duration"], "C_certain_exposure": c["CERTAIN_exposure"],
              "C_possible_duration": c["POSSIBLE_duration"], "C_possible_exposure": c["POSSIBLE_exposure"],
              "C_terminal": ("REACHED_THE_HORIZON"
                             if c["CERTAIN_duration"] >= b["AMBIENT_duration"]
                             and b["AMBIENT_terminal"] == "REACHED_THE_HORIZON"
                             else "CERTAIN_SET_EXHAUSTED"),
              "C_certain_split_rows": c["certain_split_rows"],
              "C_yb_certain": c["yb_certain"], "C_yd_certain": c["yd_certain"],
              "C_yb_possible": c["yb_possible"], "C_yd_possible": c["yd_possible"],
              "C_replacements_crossed": min(c["yb_certain"], c["yd_certain"]),
              "C_xb_certain": c["xb_certain"], "C_xb_possible": c["xb_possible"],
              "total_xbirths_after_t_m": tot_x,
              "C_downstream_X_fraction_certain": (c["xb_certain"] / tot_x) if tot_x else None,
              "C_downstream_X_fraction_possible": (c["xb_possible"] / tot_x) if tot_x else None,
              "POST_A_CLAIM_FRACTION": sp["POST_A_CLAIM_FRACTION"],
              "ambient_rows_claimed_after_A": sp["AMBIENT_ROWS_CLAIMED"],
              "implementations_agree": res[k][arm]["IMPLEMENTATIONS_AGREE"],
              "invariant_violations": c["n_invariant_violations"],
              "C_contains_A_every_row": gg.get("C_CONTAINS_A_ON_EVERY_ROW"),
              "C_equals_A": (c["CERTAIN_duration"] == a["E3_DURATION"] and c["CERTAIN_exposure"] == a["E3_EXPOSURE"]),
              "C_equals_B": (c["CERTAIN_duration"] == b["AMBIENT_duration"] and c["CERTAIN_exposure"] == b["AMBIENT_exposure"]),
              "C_minus_B_exposure": c["CERTAIN_exposure"] - b["AMBIENT_exposure"]})
    with open(f"{O}/CLEA01_MATCHED_PAIR_MODEL_COMPARISON.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # paired descriptive differences, per model, per pair
    pairs = []
    for i in sorted({r["index"] for r in rows}):
        s = next(r for r in rows if r["index"] == i and r["arm"] == "SELECTIVE")
        h = next(r for r in rows if r["index"] == i and r["arm"] == "SHAM")
        pairs.append({"index": i, "split": s["split"],
          "A_duration_diff": s["A_duration"] - h["A_duration"],
          "A_exposure_diff": s["A_exposure"] - h["A_exposure"],
          "B_duration_diff": s["B_duration"] - h["B_duration"],
          "B_exposure_diff": s["B_exposure"] - h["B_exposure"],
          "C_certain_duration_diff": s["C_certain_duration"] - h["C_certain_duration"],
          "C_certain_exposure_diff": s["C_certain_exposure"] - h["C_certain_exposure"],
          "C_downstream_X_fraction_S": s["C_downstream_X_fraction_certain"],
          "C_downstream_X_fraction_H": h["C_downstream_X_fraction_certain"],
          "claim_fraction_S": s["POST_A_CLAIM_FRACTION"], "claim_fraction_H": h["POST_A_CLAIM_FRACTION"]})
    json.dump({"MISSION": "CLEA01", "SECTION": "5 — matched pair model comparison, DEVELOPMENTAL ONLY",
      "NO_P_VALUE_IS_COMPUTED_ANYWHERE_IN_CLEA01": True,
      "THE_INDEPENDENT_UNIT_IS_THE_BASE_SEED": True,
      "OMLDCT02_PAIRED_STATISTICS_ARE_NOT_REINTERPRETED": True,
      "PER_ARM": rows, "PER_PAIR_DESCRIPTIVE_DIFFERENCES": pairs},
      open(f"{O}/CLEA01_MATCHED_PAIR_MODEL_COMPARISON.json", "w"), indent=1)
    # disagreement ledger
    with open(f"{O}/CLEA01_IDENTITY_DISAGREEMENT_LEDGER.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["index", "arm", "split", "A_duration", "B_duration", "C_certain_duration",
                    "A_exposure", "B_exposure", "C_certain_exposure", "C_differs_from_A",
                    "C_differs_from_B", "C_minus_B_exposure", "POST_A_CLAIM_FRACTION",
                    "C_contains_A_every_row"])
        for r in rows:
            w.writerow([r["index"], r["arm"], r["split"], r["A_duration"], r["B_duration"],
                        r["C_certain_duration"], r["A_exposure"], r["B_exposure"],
                        r["C_certain_exposure"], not r["C_equals_A"], not r["C_equals_B"],
                        r["C_minus_B_exposure"], r["POST_A_CLAIM_FRACTION"],
                        r["C_contains_A_every_row"]])
    return rows, pairs

if __name__ == "__main__":
    rows, pairs = main()
    print("arms:", len(rows), "pairs:", len(pairs))
