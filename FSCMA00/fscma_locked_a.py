"""FSCMA00 Section 10 (A) -- LOCKED, SEALED STAGE ONE: sham + the two carrier sentinels.

The environmental arm is NOT run in this file and its outcome does not exist when the
orientation is derived. 18 starts of the frozen LOCKED budget of 24.

A structural prediction is frozen here, BEFORE the first LOCKED outcome, and it is falsifiable:
the BASIS gauge showed the canonical channel label is anti-aligned between the two founder
strata because make_founder assigns (HIST_H, HIST_L) on even seeds and (HIST_L, HIST_H) on odd
seeds while the queue makes even seeds FAR and odd seeds NEAR. If that is the mechanism, the
LOCKED even seeds must swap against the BASIS gauge founder and the LOCKED odd seeds must not.
"""
from __future__ import annotations
import sys, json, time
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z
import domc_core as K, ppai_core as P
import etcmnfc_core as EC

OUT = "/home/claude/sweep/FSCMA00"
CKD = "/home/claude/sweep/WSFSCRP00/checkpoints"
LED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
LOCKED = [tuple(x) for x in LED["roles"]["LOCKED_DEV_EVALUATION"]]
S58 = json.load(open(f"{OUT}/FSCMA00_S5_S8.json"))
GAUGE_FOUNDER = 64001                       # BASIS gauge, fixed no_swap in Section 5
STARTS = {"n": 0, "log": []}
SW = np.array([float(w) ** 0.5 for w in Z.W])
T = len(Z.W)

PREDICTION = {
    "frozen_before": "the first LOCKED engine start of this programme",
    "mechanism": "make_founder assigns (HIST_H, HIST_L) on even seeds and (HIST_L, HIST_H) on "
                 "odd seeds; the frozen queue makes even seeds FAR and odd seeds NEAR; both "
                 "geometries are symmetric about x = L/2 so the canonical smaller-site-id "
                 "channel is always the half-A site. Geometry class, history order and channel "
                 "label are therefore one axis, not three.",
    "P3_orientation": {
        "statement": "aligned against the BASIS gauge founder 64001 (odd/NEAR), every LOCKED "
                     "EVEN seed will require a swap and every LOCKED ODD seed will not",
        "predicted_swap": sorted([s for s, _ in LOCKED if s % 2 == 0]),
        "predicted_no_swap": sorted([s for s, _ in LOCKED if s % 2 == 1]),
        "falsifier": "any LOCKED founder whose sign alignment disagrees with its seed parity"},
}
json.dump(PREDICTION, open(f"{OUT}/FSCMA00_LOCKED_PREDICTION_FROZEN.json", "w"), indent=1)
print("P3 frozen: predicted swap", PREDICTION["P3_orientation"]["predicted_swap"],
      "| no_swap", PREDICTION["P3_orientation"]["predicted_no_swap"], "\n")


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)
    assert STARTS["n"] <= 60, "LOCKED cap exceeded"


def sentinels(st0, MA, MB):
    K.set_geometry("FAR")
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st0, mem)
    ida = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    idb = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ida, idb)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    return {"CARRIER_1": (lambda s: EC.transpose(s, I, J),
                          {"n_pairs": len(I), "max_cardinality": int(M)}),
            "CARRIER_2": (lambda s: P.state_cross(s), {"instance": "intensive_reflection"})}


rows, q0 = [], []
t0 = time.time()
for seed, geom in LOCKED:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    B = Z.B_of(st0, MA, MB)
    src = Z.full_sha(st0)
    start(f"LOCKED_SHAM_{seed}")
    sham = Z.run_arm(st0, lambda s: s.copy(), MA, MB, B)
    q0.append({"seed": seed, "geometry": geom, "B_positive": B > 0,
               "rho_finite": bool(np.isfinite(st0.rho).all()),
               "mask_sites": [int(MA.sum()), int(MB.sum())]})
    for nm, (op, meta) in sentinels(st0, MA, MB).items():
        pre, post = st0.copy(), op(st0.copy())
        touched = sorted({f for f in Z.FIELDS
                          if not np.array_equal(
                              np.ascontiguousarray(np.asarray(getattr(pre, f))).tobytes(),
                              np.ascontiguousarray(np.asarray(getattr(post, f))).tobytes())})
        dom = bool((np.abs(post.Mf[0]) <= post.rho).all()
                   and (post.Mf[0][post.rho <= 1e-4] == 0.0).all())
        start(f"LOCKED_{nm}_{seed}")
        arm = Z.run_arm(st0, op, MA, MB, B)
        dA = [arm["qA"][j] - sham["qA"][j] for j in range(T)]
        dB = [arm["qB"][j] - sham["qB"][j] for j in range(T)]
        r0 = (arm["q0"][0] - sham["q0"][0], arm["q0"][1] - sham["q0"][1])
        A_bu = sum((Z.W[j] * (abs(dA[j]) + abs(dB[j])) for j in range(T)), Fr(0))
        G_bu = sum((Z.W[j] * (abs(sham["qA"][j] - sham["q0"][0])
                              + abs(sham["qB"][j] - sham["q0"][1])) for j in range(T)), Fr(0))
        ETA = max(Fr(1, 10 ** 12), Fr(1, 100) * G_bu,
                  Fr(1, 100) * Z.dmedian(st0.rho[np.nonzero(MA | MB)]) / B)
        rows.append({"seed": seed, "geometry": geom, "arm": nm, "meta": meta,
                     "touched_fields": touched, "domain_ok": dom,
                     "structural_zero_r0": (r0[0] == 0 and r0[1] == 0),
                     "source_bytes_unchanged": Z.full_sha(st0) == src,
                     "A_bu": str(A_bu), "ETA_bu": str(ETA), "A_over_ETA": float(A_bu / ETA),
                     "passes": A_bu > ETA, "dA": [str(x) for x in dA], "dB": [str(x) for x in dB]})
        print("  %5d %-4s %-9s A=%.3e ratio=%5.2f r0=0:%s dom=%s touched=%s [%.0fs]"
              % (seed, geom, nm, float(A_bu), float(A_bu / ETA),
                 rows[-1]["structural_zero_r0"], dom, touched, time.time() - t0), flush=True)

# ------------------------------------------------------------- orientation, from CARRIER_1 only
CAR = json.load(open("/home/claude/sweep/WSFSCRP00/wsfscrp_q01.json"))["Q1"]
BSW = {int(s) for s, o in S58["S5_AB_quotient"]["orientation"].items() if o == "swap"}


def wv(a, b):
    return np.concatenate([np.array([float(Fr(x)) for x in a]) * SW,
                           np.array([float(Fr(x)) for x in b]) * SW])


gref = [r for r in CAR if r["seed"] == GAUGE_FOUNDER
        and r["superfamily"].startswith("S1")][0]
ga, gb = (gref["dB"], gref["dA"]) if GAUGE_FOUNDER in BSW else (gref["dA"], gref["dB"])
REF = wv(ga, gb)
orient, checks = {}, []
for r in rows:
    if r["arm"] != "CARRIER_1":
        continue
    plain, swapd = wv(r["dA"], r["dB"]), wv(r["dB"], r["dA"])
    swap = float(swapd @ REF) > float(plain @ REF)
    orient[str(r["seed"])] = "swap" if swap else "no_swap"
    checks.append({"seed": r["seed"], "geometry": r["geometry"], "parity":
                   "even" if r["seed"] % 2 == 0 else "odd", "orientation": orient[str(r["seed"])],
                   "cos_plain": float(plain @ REF / (np.linalg.norm(plain) * np.linalg.norm(REF))),
                   "agrees_with_P3": (r["seed"] % 2 == 0) == swap})
P3 = all(c["agrees_with_P3"] for c in checks)
json.dump({"prediction": PREDICTION, "orientation": orient, "P3_checks": checks,
           "P3_CONFIRMED": bool(P3), "q0": q0, "rows": rows, "engine_starts": STARTS},
          open(f"{OUT}/fscma_locked_carrier.json", "w"), indent=1)
print("\norientation derived from CARRIER_1 only:", orient)
for c in checks:
    print("   %5d %-4s %-4s -> %-7s cos_plain=%+.4f  agrees with P3: %s"
          % (c["seed"], c["geometry"], c["parity"], c["orientation"], c["cos_plain"],
             c["agrees_with_P3"]))
print("P3_CONFIRMED:", P3, "| LOCKED starts so far:", STARTS["n"], "of 60")
