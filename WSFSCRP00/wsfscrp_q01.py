"""WSFSCRP00 Q0 (oracle and support exactness) + Q1 (material two-channel signal).
TRAIN_SELECTION only. Locked founders and the locked environmental superfamily stay unopened."""
from __future__ import annotations
import sys, os, json, hashlib
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import wsfscrp_core as Z
import domc_core as K, ppai_core as P
import etcmnfc_core as EC          # ONLY for the conservative Mf[0] transposition operator

OUT = "/home/claude/sweep/WSFSCRP00"
CKD = f"{OUT}/checkpoints"
LED = json.load(open(f"{OUT}/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
TRAIN = [tuple(x) for x in LED["roles"]["TRAIN_SELECTION"]]
STARTS = {"n": LED["engine_starts"]["n"], "log": list(LED["engine_starts"]["log"])}
OPHASH = hashlib.sha256(open("/home/claude/sweep/ETCMNFC/etcmnfc_core.py", "rb").read()).hexdigest()
ROWS, Q0 = [], []


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)


def sham(s):
    return s.copy()


def make_ops(st0, MA, MB):
    """Two TRAIN superfamilies. One canonical sentinel instance each, frozen before outcomes."""
    K.set_geometry("FAR")   # geometry only affects K.read_sites; the operator uses explicit masks
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st0, mem)
    ids_a = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    ids_b = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ids_a, ids_b)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    return {
        "S1_CONSERVATIVE_CARRIER_REDISTRIBUTION":
            (lambda s: EC.transpose(s, I, J), {"n_pairs": len(I), "max_cardinality": int(M)}),
        "S2_NONCONSERVATIVE_CARRIER_TRANSFORMATION":
            (lambda s: P.state_cross(s), {"instance": "intensive_reflection"}),
    }


for seed, geom in TRAIN:
    st0 = Z.load(f"{CKD}/f_{seed}_{geom}.npz")
    mk = np.load(f"{CKD}/m_{seed}_{geom}.npz")
    MA, MB = mk["MA"], mk["MB"]
    B = Z.B_of(st0, MA, MB)
    mask_sha0 = hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest()

    # ---- Q0: full-horizon sham vs sham, from identical immutable checkpoint bytes
    start(f"Q0_SHAM1_{seed}"); s1 = Z.run_arm(st0, sham, MA, MB, B)
    start(f"Q0_SHAM2_{seed}"); s2 = Z.run_arm(Z.load(f"{CKD}/f_{seed}_{geom}.npz"), sham, MA, MB, B)
    sham_det = (s1["qA"] == s2["qA"] and s1["qB"] == s2["qB"]
                and s1["end_sha"] == s2["end_sha"])
    # ---- Q0: reload vs uninterrupted (the founder object still in memory vs a fresh reload)
    reload_ok = Z.full_sha(Z.load(f"{CKD}/f_{seed}_{geom}.npz")) == Z.full_sha(st0)
    # ---- Q0: masks immutable across the whole run
    mask_sha1 = hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest()
    Q0.append({"seed": seed, "geometry": geom,
               "full_horizon_sham_vs_sham_identical": bool(sham_det),
               "reload_equals_source_bytes": bool(reload_ok),
               "masks_immutable": mask_sha0 == mask_sha1,
               "B_positive": B > 0,
               "rho_finite": bool(np.isfinite(st0.rho).all())})

    ops = make_ops(st0, MA, MB)
    for sf, (op, meta) in ops.items():
        # domain / touch-set precondition check, per unit, before execution
        pre = st0.copy()
        post = op(st0.copy())
        touched = {f for f in Z.FIELDS
                   if not np.array_equal(np.asarray(getattr(pre, f)).view(np.uint8),
                                         np.asarray(getattr(post, f)).view(np.uint8))}
        dom_ok = bool((np.abs(post.Mf[0]) <= post.rho + 0.0).all()
                      and (post.Mf[0][post.rho <= 1e-4] == 0.0).all())
        rho_untouched = "rho" not in touched
        start(f"Q1_{seed}_{sf}")
        arm = Z.run_arm(st0, op, MA, MB, B)
        dA = [arm["qA"][j] - s1["qA"][j] for j in range(len(Z.W))]
        dB = [arm["qB"][j] - s1["qB"][j] for j in range(len(Z.W))]
        r0 = (arm["q0"][0] - s1["q0"][0], arm["q0"][1] - s1["q0"][1])
        A_bu = sum((Z.W[j] * (abs(dA[j]) + abs(dB[j])) for j in range(len(Z.W))), Fr(0))
        G_bu = sum((Z.W[j] * (abs(s1["qA"][j] - s1["q0"][0]) + abs(s1["qB"][j] - s1["q0"][1]))
                    for j in range(len(Z.W))), Fr(0))
        rho_med = Z.dmedian(st0.rho[np.nonzero(MA | MB)])
        ETA_SCI = Fr(1, 100) * rho_med / B
        ETA = max(Fr(1, 10**12), Fr(1, 100) * G_bu, ETA_SCI)
        ROWS.append({"seed": seed, "geometry": geom, "superfamily": sf, "meta": meta,
                     "touched_fields": sorted(touched), "rho_untouched_at_t0": rho_untouched,
                     "domain_ok": dom_ok,
                     "structural_zero_r0": (r0[0] == 0 and r0[1] == 0),
                     "A_bu": str(A_bu), "G_bu": str(G_bu), "ETA_bu": str(ETA),
                     "A_over_ETA": float(A_bu / ETA), "passes": A_bu > ETA,
                     "dA": [str(x) for x in dA], "dB": [str(x) for x in dB]})
        print(f"{seed} {geom} {sf.split('_')[0]}: A={float(A_bu):.3e} ETA={float(ETA):.3e} "
              f"ratio={float(A_bu/ETA):.2f} pass={A_bu > ETA} r0=0:{r0[0]==0 and r0[1]==0} "
              f"touched={sorted(touched)}", flush=True)

n_pass = sum(r["passes"] for r in ROWS)
print(f"\nQ0 sham-determinism: {sum(q['full_horizon_sham_vs_sham_identical'] for q in Q0)}/{len(Q0)}")
print(f"Q1 material signal: {n_pass}/12 sentinel cells")
if ROWS:
    rr = [r["A_over_ETA"] for r in ROWS]
    print(f"margin above ETA: min {min(rr):.2f}x  max {max(rr):.2f}x")
json.dump({"operator_code_sha256": OPHASH, "Q0": Q0, "Q1": ROWS,
           "engine_starts": STARTS, "q1_pass_count": n_pass},
          open(f"{OUT}/wsfscrp_q01.json", "w"), indent=1)
print("STARTS:", STARTS["n"])
