"""FSCMA00 Section 9 (cont.) -- scoring the PROBE against the two PREREGISTERED predictions.
Offline. Zero engine starts. The gauge, the carrier family and both thresholds were frozen
before fscma_probe.py ran."""
from __future__ import annotations
import json, sys
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/FSCMA00"
PAR = "/home/claude/sweep/WSFSCRP00"
PRED = json.load(open(f"{OUT}/FSCMA00_RANK_CEILING_AND_PREDICTION.json"))["G_preregistered_prediction"]
S58 = json.load(open(f"{OUT}/FSCMA00_S5_S8.json"))
PR = json.load(open(f"{OUT}/fscma_probe_raw.json"))
CAR = json.load(open(f"{PAR}/wsfscrp_q01.json"))["Q1"]

T = 10
PHYS = [Fr(40 * i) * Fr(1, 10) for i in range(1, 11)]
v = [Fr(0)] * T
v[0] = (PHYS[1] - PHYS[0]) / 2
v[T - 1] = (PHYS[T - 1] - PHYS[T - 2]) / 2
for j in range(1, T - 1):
    v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(v, Fr(0)) for x in v]
SW = np.array([float(w) ** 0.5 for w in W])
SWAP = {int(s) for s, o in S58["S5_AB_quotient"]["orientation"].items() if o == "swap"}


def cell(rec):
    a = [Fr(x) for x in rec["dA"]]
    b = [Fr(x) for x in rec["dB"]]
    if rec["seed"] in SWAP:
        a, b = b, a
    return a, b


def wvec(a, b):
    return np.concatenate([np.array([float(x) for x in a]) * SW,
                           np.array([float(x) for x in b]) * SW])


def sum_share(a, b):
    s = [a[j] + b[j] for j in range(T)]
    d = [a[j] - b[j] for j in range(T)]
    Es = sum((W[j] * s[j] * s[j] for j in range(T)), Fr(0))
    Ed = sum((W[j] * d[j] * d[j] for j in range(T)), Fr(0))
    return Es / (Es + Ed)


# --------------------------------------------------------------- carrier reference (BASIS)
CR = [cell(r) for r in CAR]
XC = np.array([wvec(a, b) for a, b in CR])
MU = XC.mean(0)
XCc = XC - MU
_, sv, VT = np.linalg.svd(XCc, full_matrices=False)
car_ss = [float(sum_share(a, b)) for a, b in CR]

# --------------------------------------------------------------- environmental cells
ENV = [r for r in PR["rows"]]
ER = [cell(r) for r in ENV]
XE = np.array([wvec(a, b) for a, b in ER])
env_ss = [float(sum_share(a, b)) for a, b in ER]


def off_against(X, k):
    """Off-family fraction of each row of X against the affine family mu + span(VT[:k]),
    both fitted on the CARRIER BASIS only. Same definition as the BASIS tube gate."""
    P = VT[:k]
    D = X - MU
    R = D - (D @ P.T) @ P
    return np.linalg.norm(R, axis=1) / np.linalg.norm(D, axis=1)


res = {"gauge_orientation": S58["S5_AB_quotient"]["orientation"],
       "carrier_reference": {"n_cells": len(CR), "singular_values": sv.tolist()},
       "P1_common_mode": {}, "P2_off_family": {}, "dose": {}, "amplitude": {}}

# ---- P1 --------------------------------------------------------------------------------
thr = PRED["P1_common_mode"]["carrier_sum_share_max"]
p1 = {"threshold_env_sum_share_gt": thr,
      "carrier_sum_share": {"min": min(car_ss), "max": max(car_ss),
                            "median": float(np.median(car_ss))},
      "env_per_cell": [{"seed": ENV[i]["seed"], "arm": ENV[i]["arm"],
                        "sum_share": env_ss[i]} for i in range(len(ENV))],
      "env_sum_share_min": min(env_ss), "env_sum_share_max": max(env_ss),
      "all_env_above_carrier_max": bool(min(env_ss) > thr),
      "separation_factor": float(min(env_ss) / thr)}
p1["VERDICT"] = "P1_CONFIRMED" if p1["all_env_above_carrier_max"] else "P1_REFUTED"
res["P1_common_mode"] = p1

# ---- P2 --------------------------------------------------------------------------------
p2 = {"threshold_OFF_gt": 0.10, "per_k": {}}
for k in (1, 2, 3, 4):
    oc, oe = off_against(XC, k), off_against(XE, k)
    p2["per_k"][k] = {
        "carrier_OFF_max": float(oc.max()), "carrier_OFF_min": float(oc.min()),
        "carrier_O_energy": float(np.sum((XC - MU - ((XC - MU) @ VT[:k].T) @ VT[:k]) ** 2)
                                  / np.sum((XC - MU) ** 2)),
        "env_OFF_min": float(oe.min()), "env_OFF_max": float(oe.max()),
        "env_per_cell": [{"seed": ENV[i]["seed"], "arm": ENV[i]["arm"], "OFF": float(oe[i])}
                         for i in range(len(ENV))],
        "all_env_above_0.10": bool(oe.min() > 0.10),
        "carrier_tube_holds_at_this_k": bool(oc.max() < 0.10)}
p2["VERDICT_at_k1"] = "P2_CONFIRMED" if p2["per_k"][1]["all_env_above_0.10"] else "P2_REFUTED"
p2["smallest_k_with_carrier_tube"] = next((k for k in (1, 2, 3, 4)
                                           if p2["per_k"][k]["carrier_tube_holds_at_this_k"]), None)
kk = p2["smallest_k_with_carrier_tube"]
p2["VERDICT_at_carrier_tube_k"] = (
    None if kk is None else
    ("P2_CONFIRMED" if p2["per_k"][kk]["all_env_above_0.10"] else "P2_REFUTED"))
res["P2_off_family"] = p2

# ---- dose linearity, and amplitude ------------------------------------------------------
byseed = {}
for i, r in enumerate(ENV):
    byseed.setdefault(r["seed"], {})[r["arm"]] = i
dose = []
for s, d in byseed.items():
    i1, i2 = d["ENV_PRIMARY"], d["ENV_SECONDARY"]
    r1, r2 = XE[i1], XE[i2]
    ratio = float(np.linalg.norm(r1) / np.linalg.norm(r2))
    cos = float(r1 @ r2 / (np.linalg.norm(r1) * np.linalg.norm(r2)))
    dose.append({"seed": s, "norm_ratio_0.50_over_0.25": ratio, "cosine": cos})
res["dose"] = {"per_founder": dose,
               "median_norm_ratio": float(np.median([d["norm_ratio_0.50_over_0.25"] for d in dose])),
               "min_cosine": float(min(d["cosine"] for d in dose)),
               "reading": "a ratio near 2 with cosine near 1 means the environmental response is "
                          "an amplitude family along ONE direction: linear in dose, one mode."}
res["amplitude"] = {
    "carrier_A_bu_range": [min(float(Fr(r["A_bu"])) for r in CAR),
                           max(float(Fr(r["A_bu"])) for r in CAR)],
    "env_A_bu_range": [min(float(Fr(r["A_bu"])) for r in ENV),
                       max(float(Fr(r["A_bu"])) for r in ENV)],
    "env_over_carrier_median": float(np.median([float(Fr(r["A_bu"])) for r in ENV])
                                     / np.median([float(Fr(r["A_bu"])) for r in CAR])),
}

# ---- branch label -----------------------------------------------------------------------
if p1["VERDICT"] == "P1_CONFIRMED" and p2["VERDICT_at_k1"] == "P2_CONFIRMED":
    res["BRANCH"] = "H2_SECOND_MODE_CANDIDATE"
elif p2["VERDICT_at_k1"] == "P2_REFUTED":
    res["BRANCH"] = "H1_INLINE_CANDIDATE"
else:
    res["BRANCH"] = "MIXED__SEE_REPORT"
json.dump(res, open(f"{OUT}/FSCMA00_PROBE_SCORED.json", "w"), indent=1)

print("P1 common mode: carrier sum_share max = %.4f (threshold)" % thr)
print("   env sum_share range [%.4f, %.4f]  -> %s (separation x%.1f)"
      % (p1["env_sum_share_min"], p1["env_sum_share_max"], p1["VERDICT"], p1["separation_factor"]))
print("\nP2 off-family (family fitted on carrier BASIS only)")
for k in (1, 2, 3, 4):
    q = p2["per_k"][k]
    print("   k=%d carrier OFF max=%.4f (tube holds: %s)  env OFF [%.4f, %.4f]  all>0.10: %s"
          % (k, q["carrier_OFF_max"], q["carrier_tube_holds_at_this_k"],
             q["env_OFF_min"], q["env_OFF_max"], q["all_env_above_0.10"]))
print("   smallest k with a valid carrier tube:", kk,
      "-> verdict there:", p2["VERDICT_at_carrier_tube_k"])
print("\ndose: median |r(0.50)|/|r(0.25)| = %.4f  min cosine = %.6f"
      % (res["dose"]["median_norm_ratio"], res["dose"]["min_cosine"]))
print("amplitude: carrier A in [%.3e, %.3e], env A in [%.3e, %.3e], median ratio %.1fx"
      % (*res["amplitude"]["carrier_A_bu_range"], *res["amplitude"]["env_A_bu_range"],
         res["amplitude"]["env_over_carrier_median"]))
print("\nBRANCH:", res["BRANCH"])
