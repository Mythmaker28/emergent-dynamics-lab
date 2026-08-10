"""FSCMA00 Sections 10 (B) + 11 -- LOCKED SEALED STAGE TWO: the environmental arm, then the
mode-transfer arithmetic. 6 starts, closing the LOCKED budget at 24 of 60.

The orientation used below was derived in stage A from CARRIER_1 outcomes only, and written to
disk before this file ran. Nothing here refits it.
"""
from __future__ import annotations
import sys, json, time
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z
import domc_core as K

OUT = "/home/claude/sweep/FSCMA00"
CKD = "/home/claude/sweep/WSFSCRP00/checkpoints"
LA = json.load(open(f"{OUT}/fscma_locked_carrier.json"))
S58 = json.load(open(f"{OUT}/FSCMA00_S5_S8.json"))
PROBE = json.load(open(f"{OUT}/fscma_probe_raw.json"))
CAR = json.load(open("/home/claude/sweep/WSFSCRP00/wsfscrp_q01.json"))["Q1"]
LED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
LOCKED = [tuple(x) for x in LED["roles"]["LOCKED_DEV_EVALUATION"]]
T = len(Z.W)
SW = np.array([float(w) ** 0.5 for w in Z.W])
BSW = {int(s) for s, o in S58["S5_AB_quotient"]["orientation"].items() if o == "swap"}
LSW = {int(s) for s, o in LA["orientation"].items() if o == "swap"}
STARTS = {"n": LA["engine_starts"]["n"], "log": list(LA["engine_starts"]["log"])}


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)
    assert STARTS["n"] <= 60


# ------------------------------------------------------------------- 6 environmental starts
erows = []
t0 = time.time()
for seed, geom in LOCKED:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    B = Z.B_of(st0, MA, MB)
    sh = [q for q in LA["rows"] if q["seed"] == seed]
    start(f"LOCKED_SHAM_REUSE_{seed}")           # the sham fork is re-derived, one start
    sham = Z.run_arm(st0, lambda s: s.copy(), MA, MB, B)
    start(f"LOCKED_ENV_PRIMARY_{seed}")
    arm = Z.run_arm(st0, lambda s: K._perturb_N(s, 0.5), MA, MB, B)
    dA = [arm["qA"][j] - sham["qA"][j] for j in range(T)]
    dB = [arm["qB"][j] - sham["qB"][j] for j in range(T)]
    A_bu = sum((Z.W[j] * (abs(dA[j]) + abs(dB[j])) for j in range(T)), Fr(0))
    erows.append({"seed": seed, "geometry": geom, "arm": "ENV_PRIMARY", "A_bu": str(A_bu),
                  "structural_zero_r0": (arm["q0"][0] - sham["q0"][0] == 0
                                         and arm["q0"][1] - sham["q0"][1] == 0),
                  "dA": [str(x) for x in dA], "dB": [str(x) for x in dB]})
    print("  %5d %-4s ENV_PRIMARY A=%.3e r0=0:%s [%.0fs]"
          % (seed, geom, float(A_bu), erows[-1]["structural_zero_r0"], time.time() - t0), flush=True)

ALLROWS = LA["rows"] + erows

# ------------------------------------------------------------------- coordinates
def wv(a, b, seed, sw):
    if seed in sw:
        a, b = b, a
    return np.concatenate([np.array([float(Fr(x)) for x in a]) * SW,
                           np.array([float(Fr(x)) for x in b]) * SW])


def ssh(a, b, seed, sw):
    if seed in sw:
        a, b = b, a
    A = [Fr(x) for x in a]
    Bv = [Fr(x) for x in b]
    Es = sum((Z.W[j] * (A[j] + Bv[j]) ** 2 for j in range(T)), Fr(0))
    Ed = sum((Z.W[j] * (A[j] - Bv[j]) ** 2 for j in range(T)), Fr(0))
    return float(Es / (Es + Ed))


BC = np.array([wv(r["dA"], r["dB"], r["seed"], BSW) for r in CAR])                 # BASIS carrier
BE = np.array([wv(r["dA"], r["dB"], r["seed"], BSW) for r in PROBE["rows"]
               if r["arm"] == "ENV_PRIMARY"])                                      # BASIS env
BE2 = np.array([wv(r["dA"], r["dB"], r["seed"], BSW) for r in PROBE["rows"]
                if r["arm"] == "ENV_SECONDARY"])
LC = np.array([wv(r["dA"], r["dB"], r["seed"], LSW) for r in LA["rows"]])          # LOCKED carrier
LE = np.array([wv(r["dA"], r["dB"], r["seed"], LSW) for r in erows])               # LOCKED env

MUC = BC.mean(0)
_, svc, VC = np.linalg.svd(BC - MUC, full_matrices=False)
MUE = BE.mean(0)
_, sve, VE = np.linalg.svd(BE - MUE, full_matrices=False)


def off(X, MU, V, k):
    D = X - MU
    R = D - (D @ V[:k].T) @ V[:k]
    return np.linalg.norm(R, axis=1) / np.linalg.norm(D, axis=1)


res = {"orientation_BASIS": S58["S5_AB_quotient"]["orientation"],
       "orientation_LOCKED": LA["orientation"],
       "P3_CONFIRMED": LA["P3_CONFIRMED"], "P3_checks": LA["P3_checks"]}

# --- O_CARRIER : does the carrier mode structure transfer to unseen founders? -------------
res["O_CARRIER"] = {k: {"locked_OFF": off(LC, MUC, VC, k).tolist(),
                        "locked_OFF_max": float(off(LC, MUC, VC, k).max()),
                        "basis_OFF_max": float(off(BC, MUC, VC, k).max())} for k in (1, 2, 3, 4)}
# --- O_ENV : do the environmental cells stay outside the carrier family? ------------------
res["O_ENV"] = {k: {"locked_OFF": off(LE, MUC, VC, k).tolist(),
                    "locked_OFF_min": float(off(LE, MUC, VC, k).min()),
                    "basis_OFF_min": float(off(BE, MUC, VC, k).min())} for k in (1, 2, 3, 4)}
# --- J_ENV : does the ENVIRONMENTAL mode itself transfer out of sample? -------------------
res["J_ENV"] = {k: {"locked_OFF_vs_basis_env_family": off(LE, MUE, VE, k).tolist(),
                    "locked_OFF_max": float(off(LE, MUE, VE, k).max())} for k in (1, 2)}
# --- C_ENV : out-of-sample common-mode share ----------------------------------------------
lc_ss = [ssh(r["dA"], r["dB"], r["seed"], LSW) for r in LA["rows"]]
le_ss = [ssh(r["dA"], r["dB"], r["seed"], LSW) for r in erows]
res["C_ENV"] = {"locked_carrier_sum_share": {"min": min(lc_ss), "max": max(lc_ss)},
                "locked_env_sum_share": {"min": min(le_ss), "max": max(le_ss)},
                "separated_out_of_sample": bool(min(le_ss) > max(lc_ss)),
                "separation_factor": float(min(le_ss) / max(lc_ss))}
# --- stability of the environmental direction ---------------------------------------------
d_basis = BE.mean(0) / np.linalg.norm(BE.mean(0))
d_locked = LE.mean(0) / np.linalg.norm(LE.mean(0))
d_basis2 = BE2.mean(0) / np.linalg.norm(BE2.mean(0))
res["stability"] = {
    "cos_basis_env_vs_locked_env": float(d_basis @ d_locked),
    "cos_basis_env_primary_vs_secondary_dose": float(d_basis @ d_basis2),
    "cos_env_vs_carrier_leading_mode": float(abs(d_basis @ VC[0])),
    "carrier_singular_values_basis": svc.tolist(),
    "env_singular_values_basis": sve.tolist(),
    "env_within_set_spread": float(sve[0] / np.linalg.norm(BE.mean(0))),
}
# --- shares --------------------------------------------------------------------------------
allw = np.vstack([BC, BE, LC, LE])
res["shares"] = {
    "carrier_mode1_share_of_carrier_centered_energy": float(svc[0] ** 2 / np.sum(svc ** 2)),
    "carrier_mode2_share": float(svc[1] ** 2 / np.sum(svc ** 2)),
    "env_energy_over_carrier_energy":
        float(np.mean(np.sum(BE ** 2, 1)) / np.mean(np.sum(BC ** 2, 1))),
}
# --- LEARNABILITY: exact weighted L1, BASIS-fitted predictors on LOCKED cells --------------
def L1(pred, true_row):
    p = [Fr(float(x)) for x in pred]
    t = [Fr(x) for x in true_row]
    return sum((Z.W[j] * (abs(p[j] - t[j]) + abs(p[T + j] - t[T + j])) for j in range(T)), Fr(0))


def raw(r, sw):
    a, b = r["dA"], r["dB"]
    if r["seed"] in sw:
        a, b = b, a
    return [Fr(x) for x in a] + [Fr(x) for x in b]


UNW = 1.0 / np.concatenate([SW, SW])
basis_all = {"CARRIER_1": [r for r in CAR if r["superfamily"].startswith("S1")],
             "CARRIER_2": [r for r in CAR if r["superfamily"].startswith("S2")],
             "ENV_PRIMARY": [r for r in PROBE["rows"] if r["arm"] == "ENV_PRIMARY"]}
grand = np.mean([np.array([float(x) for x in raw(r, BSW)])
                 for g in basis_all.values() for r in g], 0)
learn = []
for r in ALLROWS:
    arm = r.get("arm")
    tr = raw(r, LSW)
    armmean = np.mean([np.array([float(x) for x in raw(q, BSW)]) for q in basis_all[arm]], 0)
    learn.append({"seed": r["seed"], "arm": arm,
                  "L_GRAND": float(L1(grand, tr)), "L_ARM": float(L1(armmean, tr))})
res["LEARNABILITY"] = {
    "definition": "exact weighted L1 of BASIS-fitted predictors evaluated on the outcome-unseen "
                  "LOCKED cells. L_GRAND ignores which operator was applied; L_ARM uses the "
                  "BASIS mean response of the SAME operator. Nothing is fitted on LOCKED.",
    "per_cell": learn,
    "median_L_ARM_over_L_GRAND": float(np.median([c["L_ARM"] / c["L_GRAND"] for c in learn])),
    "per_arm": {a: float(np.median([c["L_ARM"] / c["L_GRAND"] for c in learn if c["arm"] == a]))
                for a in ("CARRIER_1", "CARRIER_2", "ENV_PRIMARY")},
    "improves_in_every_cell": bool(all(c["L_ARM"] < c["L_GRAND"] for c in learn)),
}
k1 = res["O_CARRIER"][1]["locked_OFF_max"]
k2 = res["O_CARRIER"][2]["locked_OFF_max"]
res["INTERNAL_MODE_STATUS"] = {
    "carrier_needs_more_than_one_mode_out_of_sample": bool(k1 > 0.10),
    "locked_carrier_OFF_max_k1": k1, "locked_carrier_OFF_max_k2": k2,
    "verdict": "CARRIER_REPERTOIRE_INTERNAL_DIMENSION_AT_LEAST_2" if k1 > 0.10
               else "CARRIER_REPERTOIRE_CONSISTENT_WITH_ONE_AFFINE_MODE"}
res["MODE_ARBITRATION"] = {
    "H1_one_affine_family_transfers": False,
    "H2_environment_adds_a_mode": bool(res["O_ENV"][1]["locked_OFF_min"] > 0.10
                                       and res["C_ENV"]["separated_out_of_sample"]),
    "label": None}
res["MODE_ARBITRATION"]["label"] = (
    "H2_SECOND_MODE_CONFIRMED_HELD_OUT" if res["MODE_ARBITRATION"]["H2_environment_adds_a_mode"]
    else "H2_NOT_CONFIRMED")
res["engine_starts"] = STARTS
json.dump({"env_rows": erows, **res}, open(f"{OUT}/FSCMA00_LOCKED_RAW_CELL_SCORES.json", "w"), indent=1)

print("\n--- Section 11 -------------------------------------------------------------")
print("O_CARRIER (LOCKED carrier vs BASIS carrier family)")
for k in (1, 2, 3, 4):
    q = res["O_CARRIER"][k]
    print("   k=%d locked OFF max=%.4f | basis OFF max=%.4f" % (k, q["locked_OFF_max"], q["basis_OFF_max"]))
print("O_ENV (LOCKED env vs BASIS CARRIER family)")
for k in (1, 2, 3, 4):
    q = res["O_ENV"][k]
    print("   k=%d locked OFF min=%.4f | basis OFF min=%.4f" % (k, q["locked_OFF_min"], q["basis_OFF_min"]))
print("J_ENV (LOCKED env vs BASIS ENV family): k=1 OFF max=%.4f  k=2 OFF max=%.4f"
      % (res["J_ENV"][1]["locked_OFF_max"], res["J_ENV"][2]["locked_OFF_max"]))
print("C_ENV: locked carrier sum_share <= %.4f, locked env sum_share >= %.4f -> separated %s (x%.1f)"
      % (res["C_ENV"]["locked_carrier_sum_share"]["max"], res["C_ENV"]["locked_env_sum_share"]["min"],
         res["C_ENV"]["separated_out_of_sample"], res["C_ENV"]["separation_factor"]))
print("stability: cos(BASIS env, LOCKED env)=%.6f | cos(dose 0.50, 0.25)=%.6f | "
      "cos(env, carrier mode 1)=%.4f"
      % (res["stability"]["cos_basis_env_vs_locked_env"],
         res["stability"]["cos_basis_env_primary_vs_secondary_dose"],
         res["stability"]["cos_env_vs_carrier_leading_mode"]))
print("LEARNABILITY: median L_ARM/L_GRAND=%.4f, every cell improves: %s, per arm %s"
      % (res["LEARNABILITY"]["median_L_ARM_over_L_GRAND"],
         res["LEARNABILITY"]["improves_in_every_cell"],
         {k: round(v, 4) for k, v in res["LEARNABILITY"]["per_arm"].items()}))
print("INTERNAL_MODE_STATUS:", res["INTERNAL_MODE_STATUS"]["verdict"])
print("MODE_ARBITRATION:", res["MODE_ARBITRATION"]["label"])
print("engine starts LOCKED:", STARTS["n"], "of 60")
