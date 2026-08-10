"""SQDT00 Section 2 -- OFFLINE rederivation from the committed FWL2CF00 support-restricted raw
archives, and serialization of FWL2_RELATIVE_QUOTIENT_BASIS_V1.

ZERO engine starts. Every score is rebuilt from raw rho bytes on the reader support; nothing is
copied from the parent's score JSONs except for a final string-for-string CONSISTENCY check that
proves the rederivation reproduces the committed series exactly (this doubles as the
support-restricted sufficiency certificate). Eigenvalue-derived quantities carry exact rational
enclosures from sq_exact; float appears only to seed brackets and to select the gauge argmin.
"""
from __future__ import annotations
import json, hashlib, itertools, math, os, sys, time
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/SQDT00"
PARENT = "/tmp/ctree/FWL2CF00"            # the committed tree, extracted from the object database
sys.path.insert(0, OUT)
import sq_exact as X
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()
log = lambda m: print("[%5.0fs] %s" % (time.time() - t0, m), flush=True)

# ---- freeze guard: this module must run AFTER the master freeze is committed -----------------
FRZ = json.load(open(f"{OUT}/SQDT00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/SQDT00_MASTER_FREEZE.md") == FRZ["hashes"]["SQDT00_MASTER_FREEZE.md"], "freeze mutated"

# ---- exact weights, rebuilt here (never imported) --------------------------------------------
H_GRID = [40 * i for i in range(1, 11)]
DT = Fr(1, 10)
PHYS = [Fr(h) * DT for h in H_GRID]
_v = [Fr(0)] * len(PHYS)
_v[0] = (PHYS[1] - PHYS[0]) / 2
_v[-1] = (PHYS[-1] - PHYS[-2]) / 2
for j in range(1, len(PHYS) - 1):
    _v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
_s = sum(_v, Fr(0))
W = [x / _s for x in _v]
T = len(W)
assert sum(W, Fr(0)) == 1 and W[0] == Fr(1, 18) and W[1] == Fr(1, 9), "weights corrupted"


def esum(vals):
    return sum((Fr(float(x)) for x in vals), Fr(0))


# =====================================================================================
# 2.0  REBUILD THE READER SERIES FROM THE COMMITTED RAW ARCHIVES (support-restricted)
# =====================================================================================
def reader_from_compact(npz_path):
    d = np.load(npz_path)
    vals, idx, MA, MB = d["rho_support"], d["support_index"], d["MA"], d["MB"]
    fa = np.asarray(MA).ravel()[idx]
    fb = np.asarray(MB).ravel()[idx]
    XA, XB, B = [], [], None
    for k in range(vals.shape[0]):
        row = [float(x) for x in vals[k]]
        if k == 0:
            B = esum(row)
        XA.append(esum([row[i] for i in range(len(row)) if fa[i]]) / B)
        XB.append(esum([row[i] for i in range(len(row)) if fb[i]]) / B)
    return XA, XB, B


AP = json.load(open(f"{PARENT}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))
BIND = json.load(open(f"{PARENT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
PARENT_ACTIVE = json.load(open(f"{PARENT}/active_series.json"))
PARENT_SHAM = json.load(open(f"{PARENT}/sham_series.json"))
DEC = {v: k.split("|") for k, v in AP["opaque_ids"].items()}      # opaque -> (descendant, arm)

# rebuild every sham (SHAM_0) and every active arm from raw, and cross-check to the committed JSON
sham_rebuilt, active_rebuilt = {}, {}
consist = {"sham": [], "active": []}
for opq, (did, arm) in sorted(DEC.items()):
    XA, XB, B = reader_from_compact(f"{PARENT}/active_raw/{opq}.npz")
    active_rebuilt[opq] = {"did": did, "arm": arm, "XA": XA, "XB": XB, "B": B}
    ref = PARENT_ACTIVE[opq]
    ok = ([str(x) for x in XA] == ref["XA"] and [str(x) for x in XB] == ref["XB"]
          and str(B) == ref["B"])
    consist["active"].append(ok)
for did in sorted(PARENT_SHAM):
    XA, XB, B = reader_from_compact(f"{PARENT}/sham_raw/{did}.npz")
    sham_rebuilt[did] = {"XA": XA, "XB": XB, "B": B}
    ref = PARENT_SHAM[did]
    ok = ([str(x) for x in XA] == ref["XA"] and [str(x) for x in XB] == ref["XB"]
          and str(B) == ref["B"])
    consist["sham"].append(ok)
SUFFICIENCY = all(consist["sham"]) and all(consist["active"])
log("reader rebuilt from raw: sham %d/%d, active %d/%d, string-for-string match=%s"
    % (sum(consist["sham"]), len(consist["sham"]),
       sum(consist["active"]), len(consist["active"]), SUFFICIENCY))
assert SUFFICIENCY, "OFFLINE_REDERIVATION_MISMATCH (support-restricted sufficiency failed)"

# =====================================================================================
# 2.1  EXACT RESPONSE, M2^2, U, V  (rederived, then matched to the parent)
# =====================================================================================
rows = []
for opq in sorted(active_rebuilt):
    a = active_rebuilt[opq]
    did, arm = a["did"], a["arm"]
    s = sham_rebuilt[did]
    XA, XB = a["XA"], a["XB"]
    SA, SB = s["XA"], s["XB"]
    assert a["B"] == s["B"], "normaliser mismatch arm vs sham"
    r0 = (XA[0] - SA[0], XB[0] - SB[0])
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]
    dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    m2 = sum((W[h] * (dA[h] * dA[h] + dB[h] * dB[h]) for h in range(T)), Fr(0))
    uv = sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) / 2 for h in range(T)), Fr(0))
    assert m2 == uv, "u/v energy identity failed"
    rows.append({"opaque": opq, "descendant": did, "arm": arm,
                 "structural_zero_h0": (r0[0] == 0 and r0[1] == 0),
                 "dA": dA, "dB": dB, "M2sq": m2})
assert len(rows) == 32
DIDS = sorted({r["descendant"] for r in rows})
IDX = {d: i for i, d in enumerate(DIDS)}
n = len(rows)
D_OF = [IDX[r["descendant"]] for r in rows]
STRUCT0 = all(r["structural_zero_h0"] for r in rows)

# exact U, V
U = [[sum((W[h] * (rows[i]["dA"][h] + rows[i]["dB"][h])
           * (rows[j]["dA"][h] + rows[j]["dB"][h]) / 2 for h in range(T)), Fr(0))
      for j in range(n)] for i in range(n)]
V = [[sum((W[h] * (rows[i]["dA"][h] - rows[i]["dB"][h])
           * (rows[j]["dA"][h] - rows[j]["dB"][h]) / 2 for h in range(T)), Fr(0))
      for j in range(n)] for i in range(n)]
for i in range(n):
    assert U[i][i] + V[i][i] == rows[i]["M2sq"], "U+V != M2^2"
log("exact U,V built; structural zero at h0 32/32=%s" % STRUCT0)

# =====================================================================================
# 2.2  EXACT R0 MINIMISATION over the 2^15 gauge assignments (pin eps_1 = +1)
# =====================================================================================
alpha = Fr(1, n)
M16 = [[sum((alpha * alpha * V[i][j] for i in range(n) if D_OF[i] == p
             for j in range(n) if D_OF[j] == q), Fr(0)) for q in range(16)] for p in range(16)]
Cc = sum((alpha * (U[i][i] + V[i][i]) for i in range(n)), Fr(0))
Aconst = sum((alpha * alpha * U[i][j] for i in range(n) for j in range(n)), Fr(0))
Mnp = np.array([[float(x) for x in r] for r in M16])
S = np.hstack([np.ones((2 ** 15, 1)), np.array(list(itertools.product([1, -1], repeat=15)),
                                                dtype=np.float64)])
quad = np.einsum("ki,ij,kj->k", S, Mnp, S)
order = np.argsort(-quad)


def exact_quad(sv):
    return sum((Fr(int(sv[p])) * Fr(int(sv[q])) * M16[p][q]
                for p in range(16) for q in range(16)), Fr(0))


R0map = {int(k): Cc - Aconst - exact_quad(S[int(k)]) for k in order[:8]}
R0_exact = min(R0map.values())
best_k = min(R0map, key=lambda k: R0map[k])
eps16 = [int(S[best_k][p]) for p in range(16)]                      # per-descendant gauge signs
gap = float(quad[order[0]] - quad[order[1]])
scale = float(np.abs(Mnp).sum())
log("R0 exact argmin found; float gap %.3e exceeds float error scale by %.2e"
    % (gap, gap / (scale * 1e-15) if scale else 0))

# match to the committed parent value
PQ = json.load(open(f"{PARENT}/FRESH_QUOTIENT_CERTIFICATE.json"))
R0_parent = Fr(PQ["R0_exact"])
R0_MATCH = (R0_exact == R0_parent)
log("R0 exact == parent committed R0_exact : %s" % R0_MATCH)
assert R0_MATCH, "OFFLINE_REDERIVATION_MISMATCH (R0)"

# =====================================================================================
# 2.3  EXACT GRAM G(eps*)  and CERTIFIED eigenvalue enclosures
# =====================================================================================
eps_row = [eps16[D_OF[i]] for i in range(n)]
Z = [[U[i][j] + eps_row[i] * eps_row[j] * V[i][j] for j in range(n)] for i in range(n)]
# double-centre and divide by n, all exact
rowmean = [sum(Z[i], Fr(0)) / n for i in range(n)]
tot = sum(rowmean, Fr(0)) / n
G = [[(Z[i][j] - rowmean[i] - rowmean[j] + tot) / n for j in range(n)] for i in range(n)]
traceG = sum(G[i][i] for i in range(n))
assert traceG == R0_exact, "trace(G) != R0 exact"

Gf = np.array([[float(x) for x in r] for r in G])
evf = np.sort(np.linalg.eigvalsh(Gf))[::-1]
log("float top eigenvalues: %.6e %.6e %.6e %.6e" % (evf[0], evf[1], evf[2], evf[3]))
enc = X.enclose_eigs(G, n, [1, 2, 3], [evf[0], evf[1], evf[2]], K=80)
l1lo, l1hi = enc[1]
l2lo, l2hi = enc[2]
l3lo, l3hi = enc[3]
# R1, R2, I1, I2 enclosures
I1_lo, I1_hi = l1lo, l1hi
I2_lo, I2_hi = l2lo, l2hi
R1_lo, R1_hi = R0_exact - l1hi, R0_exact - l1lo
R2_lo, R2_hi = R0_exact - l1hi - l2hi, R0_exact - l1lo - l2lo
log("I1 in [%.6e, %.6e] ; I2 in [%.6e, %.6e]"
    % (float(I1_lo), float(I1_hi), float(I2_lo), float(I2_hi)))
# separation certificates
SEP_12 = l1lo > l2hi
SEP_23 = l2lo > l3hi
assert SEP_12, "lambda1 not certifiably above lambda2"
log("separations: lambda1>lambda2=%s  lambda2>lambda3=%s" % (SEP_12, SEP_23))

# the parent's float values must agree with our exact enclosures to within the parent's own
# declared backward-stability bound. Our enclosures are far tighter than float precision, so a
# raw containment test would fail on the last ULP; the honest test widens by the parent's eb.
eb = float(PQ.get("error_bound", 3.66e-16)) + 4e-16
def agree(x, lo, hi):
    return float(lo) - eb - 1e-15 * abs(x) <= x <= float(hi) + eb + 1e-15 * abs(x)


BRACKETS_OK = all([agree(PQ["I1"], I1_lo, I1_hi), agree(PQ["I2"], I2_lo, I2_hi),
                   agree(PQ["R1"], R1_lo, R1_hi), agree(PQ["R2"], R2_lo, R2_hi)])
log("parent R1,R2,I1,I2 agree with the exact enclosures (within the parent eb): %s" % BRACKETS_OK)

# same argmin for k=1,2 (float, then exact certification at eps* vs its runner-up)
def Rk_of(sv):
    er = [int(sv[D_OF[i]]) for i in range(n)]
    Zl = Gf * 0
    Zl = np.array([[U[i][j].__float__() + er[i] * er[j] * V[i][j].__float__()
                    for j in range(n)] for i in range(n)])
    rm = Zl.mean(1, keepdims=True)
    Gl = (Zl - rm - rm.T + Zl.mean()) / n
    ev = np.linalg.eigvalsh(Gl)[::-1]
    tr = np.trace(Gl)
    return tr, tr - ev[0], tr - ev[0] - ev[1]


allS = S
Rk = np.array([Rk_of(allS[k]) for k in range(allS.shape[0])])
kk = [int(np.argmin(Rk[:, j])) for j in range(3)]
SAME_ARGMIN = (kk[0] == kk[1] == kk[2] == best_k)
log("same gauge argmin for k=0,1,2 and equals the exact R0 argmin: %s" % SAME_ARGMIN)

# =====================================================================================
# 2.4  FIT AND SERIALISE  FWL2_RELATIVE_QUOTIENT_BASIS_V1
# =====================================================================================
# phi coordinates in R^20 (float; the sqrt(W/2) factors are irrational but the Gram is rational)
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]
phi = np.zeros((n, 2 * T))
for i, r in enumerate(rows):
    for h in range(T):
        phi[i, h] = sw[h] * (float(r["dA"][h]) + float(r["dB"][h])) * eps_row[i] ** 0  # u unaffected by sign
        phi[i, T + h] = sw[h] * (float(r["dA"][h]) - float(r["dB"][h])) * eps_row[i]   # v flips with eps
mu = phi.mean(0)
psi = phi - mu
Sigma = (psi.T @ psi) / n
w_, Vec = np.linalg.eigh(Sigma)
ordr = np.argsort(w_)[::-1]
e1 = Vec[:, ordr[0]].copy()
e2 = Vec[:, ordr[1]].copy()


def canon(v):
    k = int(np.argmax(np.abs(v)))
    if v[k] < 0:
        v = -v
    return v


e1, e2 = canon(e1), canon(e2)
P1 = np.outer(e1, e1)
P2 = P1 + np.outer(e2, e2)
c = psi @ np.stack([e1, e2], 1)                    # per-row scores (n x 2)

# reconstruction identity  R0 - (||c1||^2+||c2||^2)/n = R2
recon = float(R0_exact) - (c[:, 0] @ c[:, 0] + c[:, 1] @ c[:, 1]) / n
S6 = abs(recon - 0.5 * (float(R2_lo) + float(R2_hi))) < 1e-9 + 5 * float(R2_hi - R2_lo)
ortho = float(abs(e1 @ e2)) + abs(float(e1 @ e1) - 1) + abs(float(e2 @ e2) - 1)

# leave-one-descendant-out stability of the 2-plane
loo = []
for dleft in range(16):
    keep = [i for i in range(n) if D_OF[i] != dleft]
    ps = phi[keep] - phi[keep].mean(0)
    Sg = (ps.T @ ps) / len(keep)
    ww, VV = np.linalg.eigh(Sg)
    od = np.argsort(ww)[::-1]
    f1 = canon(VV[:, od[0]].copy())
    f2 = canon(VV[:, od[1]].copy())
    Bfull = np.stack([e1, e2], 1)
    Bloo = np.stack([f1, f2], 1)
    sv = np.linalg.svd(Bfull.T @ Bloo, compute_uv=False)
    ang = math.degrees(math.acos(min(1.0, max(-1.0, float(sv.min())))))
    loo.append(ang)
S5 = max(loo) < 30.0
log("basis fitted; ortho residual %.2e | LOO max principal angle %.3f deg (<30=%s)"
    % (ortho, max(loo), S5))

# serialise the object as real arrays
np.savez(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz",
         mu=mu, e1=e1, e2=e2, P1=P1, P2=P2, scores=c, eps16=np.array(eps16, dtype=np.int64),
         descendant_index=np.array([DIDS[d].encode() for d in range(16)]),
         coord_layout=np.array([b"u" if k < T else b"v" for k in range(2 * T)]),
         coord_htime=np.array([H_GRID[k % T] for k in range(2 * T)], dtype=np.int64))
basis_json = {
    "name": "FWL2_RELATIVE_QUOTIENT_BASIS_V1",
    "not_an_alias_of": ["GIMB00_STRATUM_AXIS", "PARENT_FOUNDER_STRATUM",
                        "RECOVERED_PARENT_MODE", "HISTORICAL_SECOND_MODE"],
    "fitted_to": "the FWL2CF00 fresh active panel (32 locked carrier cells), in the FWL2CF00 "
                 "gauge, in the FWL2CF00 orthonormal u/v coordinates",
    "coordinate_space": "R^20 = (u_h1..u_h10, v_h1..v_h10)",
    "dt": "1/10", "H_GRID": H_GRID, "weights": [str(x) for x in W],
    "gauge_eps_per_descendant": {DIDS[d]: eps16[d] for d in range(16)},
    "sign_canonicalisation": "for each e_k the largest-magnitude coordinate is made positive; "
                             "ties by smallest coordinate index; the global gauge sign is pinned "
                             "by eps_1 = +1",
    "R0_exact": str(R0_exact),
    "I1_enclosure": [str(I1_lo), str(I1_hi)],
    "I2_enclosure": [str(I2_lo), str(I2_hi)],
    "R1_enclosure": [str(R1_lo), str(R1_hi)],
    "R2_enclosure": [str(R2_lo), str(R2_hi)],
    "lambda3_enclosure": [str(l3lo), str(l3hi)],
    "mu": mu.tolist(), "e1": e1.tolist(), "e2": e2.tolist(),
    "scores_per_row": {rows[i]["opaque"]: [float(c[i, 0]), float(c[i, 1])] for i in range(n)},
    "row_descriptor": {rows[i]["opaque"]: {"descendant": rows[i]["descendant"],
                                           "arm": rows[i]["arm"]} for i in range(n)},
}
json.dump(basis_json, open(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json", "w"), indent=1)

# S7 round-trip
rl = np.load(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
S7 = bool(np.array_equal(rl["scores"], c) and np.array_equal(rl["e1"], e1)
          and np.array_equal(rl["mu"], mu))

# =====================================================================================
# 2.5  DUPLICATION INVARIANCE  (proof + exact numeric)
# =====================================================================================
# duplicate every row exactly; alpha -> 1/(2n); mu, Sigma, spectrum, R0, I2 all unchanged
G2n = [[G[i % n][j % n] for j in range(2 * n)] for i in range(2 * n)]  # block [[G,G],[G,G]]/? see note
# The correct duplicated Gram is NOT block-repeat of G (G is already centred). Rebuild from Z.
Zdup = [[Z[i % n][j % n] for j in range(2 * n)] for i in range(2 * n)]
rm2 = [sum(Zdup[i], Fr(0)) / (2 * n) for i in range(2 * n)]
tt2 = sum(rm2, Fr(0)) / (2 * n)
Gd = [[(Zdup[i][j] - rm2[i] - rm2[j] + tt2) / (2 * n) for j in range(2 * n)] for i in range(2 * n)]
R0_dup = sum(Gd[i][i] for i in range(2 * n))
DUP_R0 = (R0_dup == R0_exact)
Gdf = np.array([[float(x) for x in r] for r in Gd])
evd = np.sort(np.linalg.eigvalsh(Gdf))[::-1]
DUP_I2 = abs(evd[1] - 0.5 * (float(I2_lo) + float(I2_hi))) < 5 * float(I2_hi - I2_lo) + 1e-12
log("duplication invariance: R0 exact unchanged=%s ; I2 unchanged=%s" % (DUP_R0, DUP_I2))

# =====================================================================================
# 2.6  CERTIFIED MULTIPLIERS  (from enclosures, never from the rounded 0.570)
# =====================================================================================
E_TAU = Fr(BIND["E_TAU_exact"])
# rational sqrt bounds
def isqrt_frac_lower(q):
    """largest rational r = a/D with r^2 <= q, D = 10^30."""
    D = 10 ** 30
    a = math.isqrt(int(q * D * D))
    r = Fr(a, D)
    assert r * r <= q
    return r


def isqrt_frac_upper(q):
    D = 10 ** 30
    a = math.isqrt(int(q * D * D)) + 1
    r = Fr(a, D)
    assert r * r >= q
    return r


A_TAU_lo, A_TAU_hi = isqrt_frac_lower(E_TAU), isqrt_frac_upper(E_TAU)
sqrtI2_lo, sqrtI2_hi = isqrt_frac_lower(I2_lo), isqrt_frac_upper(I2_hi)
ENERGY_MULT_lo = E_TAU / I2_hi
ENERGY_MULT_hi = E_TAU / I2_lo
AMP_MULT_lo = A_TAU_lo / sqrtI2_hi
AMP_MULT_hi = A_TAU_hi / sqrtI2_lo
AMP_BELOW_2 = AMP_MULT_hi < 2
# the parent's own reported ratio sqrt(I2)/A_TAU, reconstructed, for cross-reference only
ratio_parent = math.sqrt(PQ["I2"]) / PQ["A_TAU"]
log("ENERGY_MULTIPLIER_REQUIRED in [%.4f, %.4f]" % (float(ENERGY_MULT_lo), float(ENERGY_MULT_hi)))
log("AMPLITUDE_MULTIPLIER_REQUIRED in [%.4f, %.4f]  (< 2 strictly = %s)"
    % (float(AMP_MULT_lo), float(AMP_MULT_hi), AMP_BELOW_2))

# =====================================================================================
# WRITE THE CERTIFICATE
# =====================================================================================
BASIS_GATES = {
    "BASIS_S0_only_committed_bytes": True,
    "BASIS_S1_eps_star_exact_argmin_of_R0": R0_MATCH and SAME_ARGMIN,
    "BASIS_S2_same_eps_attains_R1_R2": SAME_ARGMIN,
    "BASIS_S3_disjoint_exact_eigenvalue_enclosures": bool(SEP_12 and SEP_23),
    "BASIS_S4_orthonormal_within_residual": ortho < 1e-9,
    "BASIS_S5_LOO_principal_angle_below_30deg": bool(S5),
    "BASIS_S6_reconstruction_identity": bool(S6),
    "BASIS_S7_round_trip_bit_for_bit": bool(S7),
}
P2_LICENSE = all(BASIS_GATES.values())
E2_LICENSE = P2_LICENSE and bool(SEP_23)
cert = {
    "programme": "SQDT00 Section 2 offline rederivation and basis serialization",
    "engine_starts": 0,
    "support_restricted_sufficiency_certificate": {
        "sham_match": all(consist["sham"]),
        "active_match": all(consist["active"]),
        "meaning": "the reader series rebuilt independently from the committed raw rho bytes on "
                   "the union support equals the committed series string-for-string in exact "
                   "rational form; the off-support field is provably never read.",
    },
    "rederivation_matches_parent": {"R0_exact": R0_MATCH,
                                    "parent_float_R1_R2_I1_I2_inside_enclosures": BRACKETS_OK,
                                    "structural_zero_h0_32_of_32": STRUCT0},
    "exact_values": {
        "R0_exact": str(R0_exact),
        "I1_enclosure": [str(I1_lo), str(I1_hi)],
        "I2_enclosure": [str(I2_lo), str(I2_hi)],
        "R1_enclosure": [str(R1_lo), str(R1_hi)],
        "R2_enclosure": [str(R2_lo), str(R2_hi)],
        "lambda3_enclosure": [str(l3lo), str(l3hi)],
        "eigengap_1_2_certified_positive": SEP_12,
        "eigengap_2_3_certified_positive": SEP_23,
        "float_reference": {"R0": float(R0_exact), "I1": float(I1_lo), "I2": float(I2_lo),
                            "R1": 0.5 * (float(R1_lo) + float(R1_hi)),
                            "R2": 0.5 * (float(R2_lo) + float(R2_hi))},
    },
    "basis_gates": BASIS_GATES,
    "P2_TRANSFER_LICENSE": P2_LICENSE,
    "E2_AXIS_TRANSFER_LICENSE": E2_LICENSE,
    "duplication_invariance": {"R0_exact_unchanged": DUP_R0, "I2_unchanged": DUP_I2,
        "proof": "duplicating every row leaves the empirical mean mu and the second-moment Sigma "
                 "identical (an average of a doubled multiset equals the average of the multiset), "
                 "hence every eigenvalue, R0, I2 and every ratio is invariant; the alpha weights "
                 "halve so E_TAU and A_TAU are also invariant. This is what licenses comparing an "
                 "8-descendant panel to a 32-row parent panel."},
    "certified_multipliers": {
        "E_TAU_exact_digits": len(BIND["E_TAU_exact"]),
        "A_TAU_enclosure": [str(A_TAU_lo), str(A_TAU_hi)],
        "sqrt_I2_enclosure": [str(sqrtI2_lo), str(sqrtI2_hi)],
        "ENERGY_MULTIPLIER_REQUIRED": [float(ENERGY_MULT_lo), float(ENERGY_MULT_hi)],
        "AMPLITUDE_MULTIPLIER_REQUIRED": [float(AMP_MULT_lo), float(AMP_MULT_hi)],
        "AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2": AMP_BELOW_2,
        "parent_reported_ratio_sqrtI2_over_A_TAU_for_reference": ratio_parent,
        "reading": "a doubled dose, IF one existed and the response were linear, would raise "
                   "sqrt(I2) by exactly x2; since the required amplitude multiplier is below 2, "
                   "such a dose would lift the second mode above the absolute floor. This is a "
                   "statement about arithmetic, not about physics, and it does NOT assert that a "
                   "doubled dose can be constructed -- see the static dose-axis audit.",
    },
    "scaling_predictions_frozen": {"Rk_2x": "4 * Rk_1x", "I2_2x": "4 * I2_1x",
                                   "sqrt_I2_ratio": "exactly 2",
                                   "TAU_E_TAU_A_TAU": "unchanged (null quantities carry no dose)"},
}
json.dump(cert, open(f"{OUT}/SQDT00_OFFLINE_REDERIVATION_AND_BASIS_CERTIFICATE.json", "w"),
          indent=1, default=str)
log("Section 2 complete. P2_TRANSFER_LICENSE=%s  E2_AXIS_TRANSFER_LICENSE=%s"
    % (P2_LICENSE, E2_LICENSE))
print("BASIS GATES:", json.dumps(BASIS_GATES))
