"""DOMC — the CROSS_ENV rival arm, analysed with the SEALED estimator.

Declared honestly: the `CROSS_ENV` arm and its interpretation rule are in the sealed protocol
(`arms.CROSS_ENV`, `rivals.H_ENVIRONMENT`), and the estimator used below is the sealed
`crossing()` function of `domc_analyse.py`, imported unmodified. What is not in the sealed file
is one line of the driver loop that calls it with `iv="CROSS_ENV"`. Rather than edit a sealed
file to add that line -- which would silently break its hash -- the call is made from here. No
estimator, threshold, margin or rule is changed.
"""
from __future__ import annotations
import sys, json
sys.path.insert(0, "/home/claude/sweep")
import domc_analyse as A

if __name__ == "__main__":
    geom = sys.argv[1] if len(sys.argv) > 1 else "FAR"
    split = sys.argv[2] if len(sys.argv) > 2 else "PROSP"
    pair = sys.argv[3] if len(sys.argv) > 3 else "cc-00"
    B = A.load(geom, split, pair)
    out = {"geometry": geom, "split": split, "pair": pair, "blocks": len(B),
           "estimator": "domc_analyse.crossing, imported unmodified from the sealed file"}
    for when in ("t0", "turn"):
        out[f"CROSS_ENV_{when}"] = A.crossing(B, when, "CROSS_ENV")
    json.dump(out, open(f"domc_env_{geom}_{split}_{pair}.json", "w"), indent=1, default=str)
    for when in ("t0", "turn"):
        v = out[f"CROSS_ENV_{when}"]
        print(f"[{when}] CROSS_ENV  transfer = {v['PRIMARY_median_transfer_fraction']} "
              f"CI = {v['PRIMARY_transfer_ci95']}  "
              f"sign = {v['PRIMARY_sign_test_transfer_positive']}  "
              f"displacement = {v['median_displacement']}  "
              f"sham = {v.get('median_mechanical_floor_CROSS_SHAM')}")
