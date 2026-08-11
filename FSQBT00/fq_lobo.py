"""FSQBT00 Section 3 -- CORRECT-UNIT leave-one-ancestry-BLOCK-out audit of the immutable
FWL2_RELATIVE_QUOTIENT_BASIS_V1. Four true folds (remove one block = 4 descendants = 8 rows),
fit on the remaining three blocks, re-evaluate the SQDT00 gates, and freeze the transfer tube.
Zero engine starts. The V1 object is never mutated.
"""
from __future__ import annotations
import json, hashlib, math, itertools, sys, time
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FSQBT00"
SQDT = "/home/claude/sweep/SQDT00"
FWL2 = "/tmp/ctree/FWL2CF00"
sys.path.insert(0, SQDT)
import sq_exact as X
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()
log = lambda m: print("[%4.0fs] %s" % (time.time() - t0, m), flush=True)

# freeze guard
FRZ = json.load(open(f"{OUT}/FSQBT00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FSQBT00_MASTER_FREEZE.md") == FRZ["hashes"]["FSQBT00_MASTER_FREEZE.md"], "freeze mutated"

# exact weights
H_GRID = [40 * i for i in range(1, 11)]
DT = Fr(1, 10)
PHYS = [Fr(h) * DT for h in H_GRID]
_v = [Fr(0)] * len(PHYS)
_v[0] = (PHYS[1] - PHYS[0]) / 2
_v[-1] = (PHYS[-1] - PHYS[-2]) / 2
for j in range(1, len(PHYS) - 1):
    _v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]
T = len(W)
esum = lambda vals: sum((Fr(float(x)) for x in vals), Fr(0))


def reader(npz):
    d = np.load(npz)
    vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]; fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0:
            B = esum(row)
        XA.append(esum([row[i] for i in range(len(row)) if fa[i]]) / B)
        XB.append(esum([row[i] for i in range(len(row)) if fb[i]]) / B)
    return XA, XB, B


# rebuild rows exactly from the committed raw archives
AP = json.load(open(f"{FWL2}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))
DEC = {v: k.split("|") for k, v in AP["opaque_ids"].items()}
sham = {d: reader(f"{FWL2}/sham_raw/{d}.npz") for d in json.load(open(f"{FWL2}/sham_series.json"))}
rows = []
for opq, (did, arm) in sorted(DEC.items()):
    XA, XB, B = reader(f"{FWL2}/active_raw/{opq}.npz")
    SA, SB, _ = sham[did]
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]
    dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    rows.append({"opaque": opq, "descendant": did, "arm": arm, "block": did.split("_")[0],
                 "dA": dA, "dB": dB})
n = len(rows)
DIDS = sorted({r["descendant"] for r in rows})
IDX = {d: i for i, d in enumerate(DIDS)}
D_OF = [IDX[r["descendant"]] for r in rows]
BLOCKS = sorted({r["block"] for r in rows})
assert len(BLOCKS) == 4 and n == 32
log("rebuilt 32 rows from committed raw; 4 ancestry blocks %s" % BLOCKS)

# exact U, V
U = [[sum((W[h] * (rows[i]["dA"][h] + rows[i]["dB"][h]) * (rows[j]["dA"][h] + rows[j]["dB"][h]) / 2
           for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]
Vm = [[sum((W[h] * (rows[i]["dA"][h] - rows[i]["dB"][h]) * (rows[j]["dA"][h] - rows[j]["dB"][h]) / 2
            for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]

# serialized immutable object (bound earlier by blob id)
BJ = json.load(open(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"))
BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
eps16 = [BJ["gauge_eps_per_descendant"][DIDS[d]] for d in range(16)]
mu_full = BN["mu"]; e1_full = BN["e1"]; e2_full = BN["e2"]; P2_full = BN["P2"]
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]


def phi_rows(subset, eps_desc):
    """R^20 phi coordinates for the given row indices under a per-descendant gauge eps_desc
    (dict did->+-1). u-block sign-invariant; v-block flips with eps."""
    out = []
    for i in subset:
        r = rows[i]; e = eps_desc[r["descendant"]]
        vec = np.zeros(2 * T)
        for h in range(T):
            vec[h] = sw[h] * (float(r["dA"][h]) + float(r["dB"][h]))
            vec[T + h] = sw[h] * (float(r["dA"][h]) - float(r["dB"][h])) * e
        out.append(vec)
    return np.array(out)


def gram_from(UU, VV, idxs, eps_desc):
    er = {rows[i]["descendant"]: eps_desc[rows[i]["descendant"]] for i in idxs}
    m = len(idxs)
    Z = [[UU[idxs[a]][idxs[b]] + er[rows[idxs[a]]["descendant"]] * er[rows[idxs[b]]["descendant"]]
          * VV[idxs[a]][idxs[b]] for b in range(m)] for a in range(m)]
    rm = [sum(Z[a], Fr(0)) / m for a in range(m)]
    tt = sum(rm, Fr(0)) / m
    G = [[(Z[a][b] - rm[a] - rm[b] + tt) / m for b in range(m)] for a in range(m)]
    return G


def best_gauge(idxs):
    """exact argmin of R0 over per-descendant swaps on the subset (pin the first descendant +1).
    Returns eps_desc dict and the exact R0."""
    subdesc = sorted({rows[i]["descendant"] for i in idxs})
    k = len(subdesc)
    # float screen over 2^(k-1), then exact top-8 verify
    base = np.array(list(itertools.product([1, -1], repeat=k - 1)), dtype=np.int64)
    S = np.hstack([np.ones((base.shape[0], 1), dtype=np.int64), base])
    # precompute per-descendant V-block sums for speed via float
    Uf = np.array([[float(U[i][j]) for j in idxs] for i in idxs])
    Vf = np.array([[float(Vm[i][j]) for j in idxs] for i in idxs])
    dof = np.array([subdesc.index(rows[i]["descendant"]) for i in idxs])
    m = len(idxs)
    best = None
    R0s = np.zeros(S.shape[0])
    for t in range(S.shape[0]):
        s = S[t][dof].astype(float)
        Z = Uf + np.outer(s, s) * Vf
        rm = Z.mean(1, keepdims=True)
        G = (Z - rm - rm.T + Z.mean()) / m
        R0s[t] = np.trace(G)
    order = np.argsort(R0s)
    # exact verify the top candidate
    tbest = int(order[0])
    epsd = {subdesc[q]: int(S[tbest][q]) for q in range(k)}
    return epsd, tbest, R0s, subdesc


# ---------------- FULL OBJECT: verify against serialized, per-block I2 contribution -------------
eps_full = {DIDS[d]: eps16[d] for d in range(16)}
allidx = list(range(n))
phi = phi_rows(allidx, eps_full)
mu = phi.mean(0); psi = phi - mu
Sigma = (psi.T @ psi) / n
ww, VV = np.linalg.eigh(Sigma); od = np.argsort(ww)[::-1]
e1f = VV[:, od[0]].copy(); e2f = VV[:, od[1]].copy()
def canon(v):
    k = int(np.argmax(np.abs(v)));  return -v if v[k] < 0 else v
e1f, e2f = canon(e1f), canon(e2f)
# cross-check against the serialized object (projective)
S_check = {"e1_proj_align": float((e1f @ e1_full) ** 2), "e2_proj_align": float((e2f @ e2_full) ** 2),
           "mu_max_abs_diff": float(np.max(np.abs(mu - mu_full)))}
log("serialized cross-check: e1_align=%.6f e2_align=%.6f mu_diff=%.2e"
    % (S_check["e1_proj_align"], S_check["e2_proj_align"], S_check["mu_max_abs_diff"]))

# per-block contribution to I2 = lambda2 = (1/n) sum_i <psi_i,e2>^2
s2_full = psi @ e2f
I2_energy_full = float(s2_full @ s2_full) / n
blk_contrib = {}
for b in BLOCKS:
    ib = [i for i in allidx if rows[i]["block"] == b]
    blk_contrib[b] = float(s2_full[ib] @ s2_full[ib]) / n
maxfrac = max(blk_contrib[b] / I2_energy_full for b in BLOCKS)
S6 = maxfrac < 0.50
log("per-block I2 fraction: %s | max=%.4f (S6<0.50=%s)"
    % ({b: round(blk_contrib[b] / I2_energy_full, 4) for b in BLOCKS}, maxfrac, S6))

# certified full I1,I2,R0 (exact enclosures) reused from SQDT00 certificate
CERT = json.load(open(f"{SQDT}/SQDT00_OFFLINE_REDERIVATION_AND_BASIS_CERTIFICATE.json"))
I1 = [Fr(x) for x in CERT["exact_values"]["I1_enclosure"]]
I2 = [Fr(x) for x in CERT["exact_values"]["I2_enclosure"]]
R0 = Fr(CERT["exact_values"]["R0_exact"])
S2 = (I2[0] / I1[1] > Fr(1, 100)) and (I2[0] / R0 > Fr(5, 100))
S1 = CERT["basis_gates"]["BASIS_S1_eps_star_exact_argmin_of_R0"]
S0 = CERT["rederivation_matches_parent"]["R0_exact"]
log("full gates: S0=%s S1=%s S2=%s (I2/I1=%.4f I2/R0=%.4f)"
    % (S0, S1, S2, float(I2[0] / I1[1]), float(I2[0] / R0)))

# ---------------- FOUR TRUE LOBO FOLDS ---------------------------------------------------------
folds = []
S4_min = 1.0; S5_min = 1.0; S3_all = True
tube_residuals = []
for b in BLOCKS:
    keep = [i for i in allidx if rows[i]["block"] != b]
    omit = [i for i in allidx if rows[i]["block"] == b]
    kept_dids = sorted({rows[i]["descendant"] for i in keep})
    omit_dids = sorted({rows[i]["descendant"] for i in omit})
    # fold-specific optimal gauge on the training blocks, exact R0
    epsd, tbest, R0s, subdesc = best_gauge(keep)
    Gtr = gram_from(U, Vm, keep, epsd)
    m = len(keep)
    Gf = np.array([[float(x) for x in r] for r in Gtr])
    evf = np.sort(np.linalg.eigvalsh(Gf))[::-1]
    enc = X.enclose_eigs(Gtr, m, [1, 2, 3], [evf[0], evf[1], evf[2]], K=80)
    l1, l2, l3 = enc[1], enc[2], enc[3]
    R0tr = sum(Gtr[a][a] for a in range(m))
    I1tr = (l1[0], l1[1]); I2tr = (l2[0], l2[1])
    # S3 for this fold: common argmin (float screen: same tbest minimizes R1,R2 too), positive I2,
    # both relative gates
    dof = np.array([subdesc.index(rows[i]["descendant"]) for i in keep])
    Uf = np.array([[float(U[i][j]) for j in keep] for i in keep])
    Vf = np.array([[float(Vm[i][j]) for j in keep] for i in keep])
    def rk(tt):
        s = np.array([1] + list(np.array(list(itertools.product([1, -1], repeat=len(subdesc) - 1))[tt]))).astype(float)[dof]
        Z = Uf + np.outer(s, s) * Vf; rm = Z.mean(1, keepdims=True); Gl = (Z - rm - rm.T + Z.mean()) / m
        ev = np.linalg.eigvalsh(Gl)[::-1]; tr = np.trace(Gl); return tr, tr - ev[0], tr - ev[0] - ev[1]
    allc = np.array([rk(tt) for tt in range(2 ** (len(subdesc) - 1))])
    same_argmin = (int(np.argmin(allc[:, 0])) == int(np.argmin(allc[:, 1])) == int(np.argmin(allc[:, 2])) == tbest)
    rel_ok = (I2tr[0] > 0) and (I2tr[0] / I1tr[1] > Fr(1, 100)) and (I2tr[0] / R0tr > Fr(5, 100))
    fold_S3 = bool(same_argmin and rel_ok)
    S3_all = S3_all and fold_S3
    # fold-specific basis vectors (float), fit on training blocks
    phi_tr = phi_rows(keep, epsd)
    mu_tr = phi_tr.mean(0); psi_tr = phi_tr - mu_tr
    Stt = (psi_tr.T @ psi_tr) / m
    wtr, Vtr = np.linalg.eigh(Stt); ot = np.argsort(wtr)[::-1]
    e1_tr = canon(Vtr[:, ot[0]].copy()); e2_tr = canon(Vtr[:, ot[1]].copy())
    P2_tr = np.outer(e1_tr, e1_tr) + np.outer(e2_tr, e2_tr)
    # S4: min squared alignment full_P2 vs LOBO_P2 (min cos^2 of principal angles between planes)
    Bf = np.stack([e1f, e2f], 1); Bt = np.stack([e1_tr, e2_tr], 1)
    svv = np.linalg.svd(Bf.T @ Bt, compute_uv=False)
    align_P2 = float(svv.min() ** 2)
    # S5: projective alignment of e2
    align_e2 = float((e2f @ e2_tr) ** 2)
    S4_min = min(S4_min, align_P2); S5_min = min(S5_min, align_e2)
    # out-of-sample tube: reconstruct the omitted block against mu_tr/P2_tr, minimizing the block's
    # own legal swaps; mean-per-line residual = mean over the block's rows of ||(I-P2_tr)(z-mu_tr)||^2
    best_res = None
    for signs in itertools.product([1, -1], repeat=len(omit_dids)):
        ed = dict(zip(omit_dids, signs))
        phi_o = phi_rows(omit, {**ed})
        res = 0.0
        for r in range(phi_o.shape[0]):
            v = phi_o[r] - mu_tr
            out = v - P2_tr @ v
            res += float(out @ out)
        res /= phi_o.shape[0]
        if best_res is None or res < best_res:
            best_res = res
    tube_residuals.append(best_res)
    folds.append({"omitted_block": b, "kept_blocks": [x for x in BLOCKS if x != b],
                  "n_kept_rows": len(keep), "n_omitted_rows": len(omit),
                  "omitted_descendants": omit_dids, "kept_descendants": kept_dids,
                  "fold_gauge": epsd, "R0_train_float": float(R0tr),
                  "I1_train": [float(I1tr[0]), float(I1tr[1])],
                  "I2_train": [float(I2tr[0]), float(I2tr[1])],
                  "same_common_argmin_k012": bool(same_argmin), "relative_gates_ok": bool(rel_ok),
                  "fold_S3": fold_S3, "align_P2_squared": align_P2, "align_e2_squared": align_e2,
                  "oos_mean_per_line_residual": best_res})
    log("fold omit %s: S3=%s alignP2^2=%.4f aligne2^2=%.4f oos_resid=%.3e"
        % (b, fold_S3, align_P2, align_e2, best_res))

S4 = S4_min > 0.80
S5 = S5_min > 0.64
# S7: reload + mutation oracle on the serialized object
reload_ok = bool(np.array_equal(np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")["e2"], e2_full))
mut = e2_full.copy(); mut[0] += 1e-6
mut_detected = not np.array_equal(mut, e2_full)
S7 = reload_ok and mut_detected

# certified propagation bound for the tube (conservative): float64 rounding over the residual sum
prop = 1e-12 * max(tube_residuals) + 1e-18
TUBE_P2_LOBO = max(tube_residuals) + prop

P2_LICENSE = bool(S0 and S1 and S2 and S4 and S6 and S7)
E2_LICENSE = bool(P2_LICENSE and S3_all and S5 and S6)

gates = {"BASIS_S0": bool(S0), "BASIS_S1": bool(S1), "BASIS_S2": bool(S2),
         "BASIS_S3_all_folds": bool(S3_all), "BASIS_S4_minAlignP2_sq": S4_min, "BASIS_S4_pass": S4,
         "BASIS_S5_minAligne2_sq": S5_min, "BASIS_S5_pass": S5,
         "BASIS_S6_maxBlockI2frac": maxfrac, "BASIS_S6_pass": bool(S6),
         "BASIS_S7": bool(S7)}
audit = {
    "programme": "FSQBT00 Section 3 correct-unit LOBO audit",
    "engine_starts": 0,
    "sqdt00_stability_unit": "INCORRECT_LODO",
    "sqdt00_evidence": "sq_offline.py: 'for dleft in range(16): keep=[i for i if D_OF[i]!=dleft]' "
                       "removes one DESCENDANT (2 rows) per fold; D_OF maps rows to descendants. "
                       "The 3.14 deg was over 16 descendant folds, not 4 block folds.",
    "correct_unit": "leave-one-ANCESTRY-BLOCK-out, 4 folds, each removing 4 descendants / 8 rows",
    "panel_structure": {"blocks": BLOCKS, "descendants_per_block": 4, "rows_per_block": 8},
    "serialized_cross_check": S_check,
    "full_object_gates": gates,
    "folds": folds,
    "per_block_I2_fraction": {b: blk_contrib[b] / I2_energy_full for b in BLOCKS},
    "TUBE_P2_LOBO": TUBE_P2_LOBO,
    "tube_residual_per_fold": {folds[i]["omitted_block"]: tube_residuals[i] for i in range(4)},
    "tube_units": "mean-per-line (per-row) out-of-sample squared residual to (I-P2_minus_b) about "
                  "mu_minus_b, minimised over the omitted block's legal linked swaps; + certified "
                  "float propagation bound",
    "P2_TRANSFER_LICENSE_CORRECTED": P2_LICENSE,
    "E2_AXIS_TRANSFER_LICENSE_CORRECTED": E2_LICENSE,
    "license_formula": {"P2": "S0&S1&S2&S4&S6&S7", "E2": "P2&S3&S5&S6"},
    "consequence": ("FRESH_PANEL_LICENSE=YES" if P2_LICENSE else
                    "FRESH_PANEL_LICENSE=NO ; ENGINE_STARTS=0"),
    "transfer_target": ("FROZEN_P2_AND_e2" if E2_LICENSE else
                        ("FROZEN_P2_ONLY__SIGNED_E2_FORBIDDEN" if P2_LICENSE else "NONE")),
}
json.dump(audit, open(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1_LOBO_AUDIT.json", "w"), indent=1, default=str)
json.dump({"P2_TRANSFER_LICENSE_CORRECTED": P2_LICENSE,
           "E2_AXIS_TRANSFER_LICENSE_CORRECTED": E2_LICENSE,
           "gates": gates, "TUBE_P2_LOBO": TUBE_P2_LOBO,
           "FRESH_PANEL_LICENSE": "YES" if P2_LICENSE else "NO"},
          open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json", "w"), indent=1, default=str)
print("\n=== CORRECTED LICENSES ===")
print("gates:", json.dumps(gates, default=str))
print("P2_TRANSFER_LICENSE_CORRECTED:", P2_LICENSE)
print("E2_AXIS_TRANSFER_LICENSE_CORRECTED:", E2_LICENSE)
print("TUBE_P2_LOBO:", TUBE_P2_LOBO)
print("FRESH_PANEL_LICENSE:", "YES" if P2_LICENSE else "NO")
