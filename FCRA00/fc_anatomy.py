"""FCRA00 Commit 5 (part 1) -- order-statistic diagnostic + residual anatomy
(intercept / carrier-common-centered / carrier-differential) + channel-time table + ancestry
influence. One legal g* gauge throughout. No engine import."""
from __future__ import annotations
import json, hashlib, math, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FCRA00"; SQDT = "/home/claude/sweep/SQDT00"; FSQ = "/home/claude/sweep/FSQBT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FRZ = json.load(open(f"{OUT}/FCRA00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FCRA00_MASTER_FREEZE.md") == FRZ["hashes"]["FCRA00_MASTER_FREEZE.md"]

H = [40 * i for i in range(1, 11)]; DT = Fr(1, 10); PH = [Fr(h) * DT for h in H]
_v = [Fr(0)] * 10; _v[0] = (PH[1] - PH[0]) / 2; _v[-1] = (PH[-1] - PH[-2]) / 2
for j in range(1, 9): _v[j] = (PH[j + 1] - PH[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]; T = 10
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]

def reader(npz):
    d = np.load(npz); vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0: B = sum((Fr(float(x)) for x in row), Fr(0))
        XA.append(sum((Fr(float(row[i])) for i in range(len(row)) if fa[i]), Fr(0)) / B)
        XB.append(sum((Fr(float(row[i])) for i in range(len(row)) if fb[i]), Fr(0)) / B)
    return XA, XB, B
DECODE = {v: k for k, v in json.load(open(f"{FSQ}/OPAQUE_ACTIVE_LABEL_MAP_LOCK.json"))["decode_map_SEALED"].items()}
SH = json.load(open(f"{FSQ}/FRESH_SHAM_SERIES_AND_HASHES.json"))
THR = {r["did"]: r for r in json.load(open(f"{FSQ}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))["thresholds"]}
BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"); mu = BN["mu"]; P2 = BN["P2"]; Qp = np.eye(20) - P2
sign = json.load(open(f"{FSQ}/FROZEN_P2_TRANSFER_REPORT.json"))["gauge_signs"]

rows = []
for oid in sorted(DECODE):
    did, arm = DECODE[oid].split("|"); XA, XB, B = reader(f"{FSQ}/active_raw/{oid}.npz")
    SA = [Fr(x) for x in SH[did]["XA"]]; SB = [Fr(x) for x in SH[did]["XB"]]
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]; dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    z = np.zeros(20)
    for h in range(T):
        z[h] = sw[h] * (float(dA[h]) + float(dB[h])); z[T + h] = sign[did] * sw[h] * (float(dA[h]) - float(dB[h]))
    rows.append({"did": did, "arm": arm, "z": z})
BLK = sorted({r["did"] for r in rows}); n = 24
byd = {}
for i, r in enumerate(rows): byd.setdefault(r["did"], {})[r["arm"]] = i

# q[b,o] = (I-P2)(z-mu)
q = {}
for i, r in enumerate(rows):
    q[(r["did"], r["arm"])] = Qp @ (r["z"] - mu)
alpha = 1 / 24.0
qlist = [q[(r["did"], r["arm"])] for r in rows]
E_OUT_TOTAL = sum(float(x @ x) for x in qlist) * alpha
Q_BAR = sum(qlist) / 24.0
E_OUT_INTERCEPT = float(Q_BAR @ Q_BAR)
E_OUT_CENTERED = sum(float((x - Q_BAR) @ (x - Q_BAR)) for x in qlist) * alpha
id1 = abs(E_OUT_TOTAL - (E_OUT_INTERCEPT + E_OUT_CENTERED))

# carrier-common / differential
C = {}; D = {}
for did in BLK:
    q1 = q[(did, "CARRIER_1")]; q2 = q[(did, "CARRIER_2")]
    C[did] = (q1 + q2) / math.sqrt(2); D[did] = (q2 - q1) / math.sqrt(2)
C_BAR = sum(C.values()) / 12.0
E_COMMON_TOTAL = sum(float(C[b] @ C[b]) for b in BLK) * alpha
E_COMMON_CENTERED = sum(float((C[b] - C_BAR) @ (C[b] - C_BAR)) for b in BLK) * alpha
E_DIFFERENTIAL_TOTAL = sum(float(D[b] @ D[b]) for b in BLK) * alpha
E_OUT_INTERCEPT_via_C = 0.5 * float(C_BAR @ C_BAR)
id2 = abs(E_OUT_TOTAL - (E_COMMON_TOTAL + E_DIFFERENTIAL_TOTAL))
id3 = abs(E_COMMON_TOTAL - (E_OUT_INTERCEPT + E_COMMON_CENTERED))
id4 = abs(E_OUT_INTERCEPT - E_OUT_INTERCEPT_via_C)
# exclusive three-way
EXCL = {"INTERCEPT": E_OUT_INTERCEPT, "COMMON_CENTERED": E_COMMON_CENTERED, "DIFFERENTIAL": E_DIFFERENTIAL_TOTAL}
id5 = abs(E_OUT_TOTAL - sum(EXCL.values()))

def frac(x): return x / E_OUT_TOTAL

# channel-time table: per output coordinate (u_h gauge-invariant A+B, v_h A-B) contribution to E_OUT_TOTAL
ct = {"u_channel_A_plus_B": {}, "v_channel_A_minus_B": {}}
for h in range(T):
    ct["u_channel_A_plus_B"][H[h]] = sum(float(x[h] ** 2) for x in qlist) * alpha
    ct["v_channel_A_minus_B"][H[h]] = sum(float(x[T + h] ** 2) for x in qlist) * alpha
ct_sum = sum(ct["u_channel_A_plus_B"].values()) + sum(ct["v_channel_A_minus_B"].values())
id6 = abs(ct_sum - E_OUT_TOTAL)

# leave-one-ancestry influence for the aggregates
infl = {}
for drop in BLK:
    keep = [i for i, r in enumerate(rows) if r["did"] != drop]
    ql = [qlist[i] for i in keep]; a = 1.0 / len(keep)
    tot = sum(float(x @ x) for x in ql) * a; qb = sum(ql) / len(keep); inter = float(qb @ qb)
    infl[drop] = {"E_OUT_TOTAL_minus": tot, "INTERCEPT_minus": inter,
                  "DIFFERENTIAL_minus": sum(float(D[b] @ D[b]) for b in BLK if b != drop) / len(keep)}
tot_range = [min(infl[b]["E_OUT_TOTAL_minus"] for b in BLK), max(infl[b]["E_OUT_TOTAL_minus"] for b in BLK)]

# order statistic diagnostic
from math import comb
Pk = {k: Fr(comb(15 - k, 3), comb(16, 4)) for k in range(0, 13)}
order = {"P_K0": str(Pk[0]), "E_K": "12/5", "P_K3": str(Pk[3]), "P_Kge3": str(sum((Pk[k] for k in range(3, 13)), Fr(0))),
         "checks": {"P_K0==1/4": Pk[0] == Fr(1, 4), "P_K3==11/91": Pk[3] == Fr(11, 91),
                    "P_Kge3==11/28": sum((Pk[k] for k in range(3, 13)), Fr(0)) == Fr(11, 28),
                    "E_K==12/5": sum((k * Pk[k] for k in range(13)), Fr(0)) == Fr(12, 5)}}

anat = {
    "gauge": "frozen residual-optimal g* (matches committed)",
    "identities_max_abs_error": {"total=intercept+centered": id1, "total=common+diff": id2,
                                 "common=intercept+common_centered": id3, "intercept two ways": id4,
                                 "exclusive three-way": id5, "channel-time sum": id6},
    "E_OUT_TOTAL": E_OUT_TOTAL,
    "exclusive_three_way": {"INTERCEPT": E_OUT_INTERCEPT, "COMMON_CENTERED": E_COMMON_CENTERED, "DIFFERENTIAL": E_DIFFERENTIAL_TOTAL},
    "exclusive_fractions": {"INTERCEPT": frac(E_OUT_INTERCEPT), "COMMON_CENTERED": frac(E_COMMON_CENTERED), "DIFFERENTIAL": frac(E_DIFFERENTIAL_TOTAL)},
    "E_COMMON_TOTAL": E_COMMON_TOTAL, "E_DIFFERENTIAL_TOTAL": E_DIFFERENTIAL_TOTAL,
    "E_COMMON_TOTAL_fraction": frac(E_COMMON_TOTAL), "E_DIFFERENTIAL_TOTAL_fraction": frac(E_DIFFERENTIAL_TOTAL),
    "reading": "INTERCEPT is a transported-mean failure, not a new dimension; common dominance is not "
               "carrier specificity; a 12/12 direct contrast does not imply a material outside-P2 "
               "differential component.",
    "leave_one_ancestry_influence_E_OUT_TOTAL_range": tot_range,
    "ancestry_influence": infl,
}
json.dump(anat, open(f"{OUT}/CARRIER_COMMON_DIFFERENTIAL_ANATOMY.json", "w"), indent=1, default=str)
json.dump({"E_OUT_TOTAL": E_OUT_TOTAL, "E_OUT_INTERCEPT": E_OUT_INTERCEPT, "E_OUT_CENTERED": E_OUT_CENTERED,
           "INTERCEPT_fraction": frac(E_OUT_INTERCEPT), "identity_error": id1,
           "reading": "intercept fraction of the outside-P2 energy; a transported-mean shift, not a new dimension"},
          open(f"{OUT}/AFFINE_INTERCEPT_ANATOMY.json", "w"), indent=1, default=str)
json.dump({"channel_time": ct, "sum_equals_E_OUT_TOTAL_error": id6,
           "note": "per output-coordinate contribution to E_OUT_TOTAL; u = gauge-invariant A+B, v = A-B; "
                   "coordinates already carry sqrt(w_h) (not re-weighted); site maps restricted to the "
                   "committed reader support"},
          open(f"{OUT}/CHANNEL_TIME_RESIDUAL_TABLE.json", "w"), indent=1, default=str)
json.dump({"leave_one_ancestry_out": infl, "E_OUT_TOTAL_range": tot_range,
           "note": "no block dropped for exceeding the tube; influence reported for every aggregate"},
          open(f"{OUT}/ANCESTRY_INFLUENCE_REPORT.json", "w"), indent=1, default=str)
open(f"{OUT}/FOUR_VS_TWELVE_ORDER_STATISTIC_DIAGNOSTIC.md", "w").write(
    "# FOUR_VS_TWELVE_ORDER_STATISTIC_DIAGNOSTIC\n\n"
    "The frozen tube = max of **four** true-LOBO out-of-sample calibration scores; the fresh gate "
    "required **all twelve** future scores below it. Under the hypothetical that four calibration and "
    "twelve future scores are continuous and exchangeable, with K = #future above the max of four:\n\n"
    "    P(K=k) = C(15-k,3)/C(16,4)\n    P(K=0) = 1/4    E[K] = 12/5 = 2.4\n"
    "    P(K=3) = 11/91 = 0.120879…    P(K>=3) = 11/28 = 0.392857…\n\n"
    f"Exact checks: {json.dumps(order['checks'])}.\n\n"
    "`FROZEN_ALL_BLOCK_GATE = FAILED_AS_PREDECLARED`; `UNIFORM_FIXED_PANEL_CONTAINMENT = NOT_QUALIFIED`; "
    "`POPULATION_P2_NONTRANSFER = INCONCLUSIVE_FROM_THIS_GATE_ALONE`. Observing 3/12 exceedances is "
    "unremarkable under exchangeability (P(K>=3)=11/28). The tube is never replaced after seeing the "
    "twelve scores; this reference never retroactively passes T4. The calibration folds use "
    "three-block fold-specific fits while fresh scores use the full frozen object, and exchangeability "
    "across the two panels is not established -- so this is an interpretation diagnostic, not a p-value.\n")
print("identities max error:", max(id1, id2, id3, id4, id5, id6))
print("E_OUT_TOTAL=%.4e  INTERCEPT=%.4e (%.1f%%)  COMMON_CENTERED=%.4e (%.1f%%)  DIFFERENTIAL=%.4e (%.1f%%)"
      % (E_OUT_TOTAL, E_OUT_INTERCEPT, 100 * frac(E_OUT_INTERCEPT), E_COMMON_CENTERED, 100 * frac(E_COMMON_CENTERED),
         E_DIFFERENTIAL_TOTAL, 100 * frac(E_DIFFERENTIAL_TOTAL)))
print("E_COMMON_TOTAL fraction=%.3f  E_DIFFERENTIAL_TOTAL fraction=%.3f" % (frac(E_COMMON_TOTAL), frac(E_DIFFERENTIAL_TOTAL)))
print("order statistic checks:", order["checks"])
