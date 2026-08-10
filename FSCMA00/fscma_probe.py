"""FSCMA00 Section 9 -- PROBE. The only phase of this programme that starts the engine so far.

FROZEN BUDGET (written in fscma_s58.py before any outcome existed): 6 SHAM + 6 ENV_PRIMARY
(+0.50*N0) + 6 ENV_SECONDARY (+0.25*N0) + 1 SHAM replicate on the gauge founder = 19 starts,
against MAX_PROBE_ENGINE_STARTS = 24.

The reader, engine, endpoint, grid and weights are inherited from WSFSCRP00 unchanged
(FIXED_SUPPORT_READER_CHANGE = false). The gauge (which founders have their two channels
exchanged) was frozen in Section 5 from CARRIER data only, before this file ran.
"""
from __future__ import annotations
import sys, json, hashlib, time
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
S58 = json.load(open(f"{OUT}/FSCMA00_S5_S8.json"))
GAUGE_MAP = S58["S5_AB_quotient"]["orientation"]
LED = json.load(open("/home/claude/sweep/WSFSCRP00/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
BASIS = [tuple(x) for x in LED["roles"]["TRAIN_SELECTION"]]
GAUGE_FOUNDER = int(sorted(int(s) for s in GAUGE_MAP)[0])
STARTS = {"n": 0, "log": [], "discarded_pre_outcome": 1,
          "discarded_note": "one PROBE_SHAM start was consumed and thrown away by a crash in a "
                            "diagnostic line (Z.dsum on a 2-D array) BEFORE that arm was scored "
                            "or recorded. Pre-outcome infrastructure retry 1 of 6."}
ARMS = {"ENV_PRIMARY": 0.5, "ENV_SECONDARY": 0.25}


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)
    assert STARTS["n"] <= 24, "PROBE cap exceeded"


rows, q0 = [], []
t_start = time.time()
for seed, geom in BASIS:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    B = Z.B_of(st0, MA, MB)
    src = Z.full_sha(st0)

    start(f"PROBE_SHAM_{seed}")
    sham = Z.run_arm(st0, lambda s: s.copy(), MA, MB, B)
    if seed == GAUGE_FOUNDER:                       # determinism re-check in THIS environment
        start(f"PROBE_SHAM_REPLICATE_{seed}")
        sh2 = Z.run_arm(Z.load(f"{CKD}/f_{seed}_{geom}.npz"), lambda s: s.copy(), MA, MB, B)
        q0.append({"seed": seed, "sham_replicate_identical":
                   bool(sham["qA"] == sh2["qA"] and sham["qB"] == sh2["qB"]
                        and sham["end_sha"] == sh2["end_sha"])})

    for nm, amp in ARMS.items():
        pre = st0.copy()
        post = K._perturb_N(st0.copy(), amp)
        touched = sorted({f for f in Z.FIELDS
                          if not np.array_equal(
                              np.ascontiguousarray(np.asarray(getattr(pre, f))).tobytes(),
                              np.ascontiguousarray(np.asarray(getattr(post, f))).tobytes())})
        dN = Z.dsum(post.N.ravel()) - Z.dsum(pre.N.ravel())
        start(f"PROBE_{nm}_{seed}")
        arm = Z.run_arm(st0, lambda s, a=amp: K._perturb_N(s, a), MA, MB, B)
        dA = [arm["qA"][j] - sham["qA"][j] for j in range(len(Z.W))]
        dB = [arm["qB"][j] - sham["qB"][j] for j in range(len(Z.W))]
        r0 = (arm["q0"][0] - sham["q0"][0], arm["q0"][1] - sham["q0"][1])
        A_bu = sum((Z.W[j] * (abs(dA[j]) + abs(dB[j])) for j in range(len(Z.W))), Fr(0))
        G_bu = sum((Z.W[j] * (abs(sham["qA"][j] - sham["q0"][0])
                              + abs(sham["qB"][j] - sham["q0"][1])) for j in range(len(Z.W))), Fr(0))
        rho_med = Z.dmedian(st0.rho[np.nonzero(MA | MB)])
        ETA = max(Fr(1, 10 ** 12), Fr(1, 100) * G_bu, Fr(1, 100) * rho_med / B)
        rows.append({"seed": seed, "geometry": geom, "arm": nm, "amp": amp,
                     "touched_fields": touched, "delta_total_N_exact": str(dN),
                     "structural_zero_r0": (r0[0] == 0 and r0[1] == 0),
                     "source_bytes_unchanged": Z.full_sha(st0) == src,
                     "A_bu": str(A_bu), "G_bu": str(G_bu), "ETA_bu": str(ETA),
                     "A_over_ETA": float(A_bu / ETA), "passes": A_bu > ETA,
                     "dA": [str(x) for x in dA], "dB": [str(x) for x in dB]})
        print("  %5d %-4s %-14s A=%.3e ETA=%.3e ratio=%6.2f r0=0:%s touched=%s dSumN=%.1f  [%.0fs]"
              % (seed, geom, nm, float(A_bu), float(ETA), float(A_bu / ETA),
                 rows[-1]["structural_zero_r0"], touched, float(dN), time.time() - t_start),
              flush=True)

json.dump({"gauge_orientation": GAUGE_MAP, "gauge_founder": GAUGE_FOUNDER,
           "determinism": q0, "rows": rows, "engine_starts": STARTS},
          open(f"{OUT}/fscma_probe_raw.json", "w"), indent=1)
print("\ndeterminism recheck:", q0)
print("PROBE starts:", STARTS["n"], "of 24")
