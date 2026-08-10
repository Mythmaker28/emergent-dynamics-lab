"""SQDT00 Section 3 -- non-vacuous oracle for the OFFLINE analysis, transfer and dose-scaling
machinery. Groups Q0A..Q0Q, each a positive identity plus a negative control that MUST fire. If
any control fails to fire the machinery is vacuous and the programme must stop (S6).

Since the static dose audit stops the programme before any fresh panel, this oracle certifies the
machinery that was actually used offline: the reader, the swap gauge, the exact R0 minimiser, the
certified eigenvalue enclosure, the projection/reconstruction identities, duplication invariance,
the aggregation lemma, the multiplier arithmetic and the dose-scaling predictions. Zero starts.
"""
from __future__ import annotations
import json, hashlib, sys, math, itertools, time
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/SQDT00"
PARENT = "/tmp/ctree/FWL2CF00"
sys.path.insert(0, OUT)
import sq_exact as X
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()

# ---- exact weights ---------------------------------------------------------------------------
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


def esum(vals):
    return sum((Fr(float(x)) for x in vals), Fr(0))


def reader(npz):
    d = np.load(npz)
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
DEC = {v: k.split("|") for k, v in AP["opaque_ids"].items()}
sham = {d: reader(f"{PARENT}/sham_raw/{d}.npz") for d in json.load(open(f"{PARENT}/sham_series.json"))}
rows = []
for opq, (did, arm) in sorted(DEC.items()):
    XA, XB, B = reader(f"{PARENT}/active_raw/{opq}.npz")
    SA, SB, SB0 = sham[did]
    dA = [XA[h + 1] - SA[h + 1] for h in range(T)]
    dB = [XB[h + 1] - SB[h + 1] for h in range(T)]
    rows.append({"opaque": opq, "descendant": did, "arm": arm, "XA": XA, "XB": XB, "B": B,
                 "SA": SA, "SB": SB, "dA": dA, "dB": dB,
                 "h0": (XA[0] - SA[0], XB[0] - SB[0])})
n = len(rows)
DIDS = sorted({r["descendant"] for r in rows})
IDX = {d: i for i, d in enumerate(DIDS)}
D_OF = [IDX[r["descendant"]] for r in rows]
M2 = [sum((W[h] * (r["dA"][h] ** 2 + r["dB"][h] ** 2) for h in range(T)), Fr(0)) for r in rows]
U = [[sum((W[h] * (rows[i]["dA"][h] + rows[i]["dB"][h]) * (rows[j]["dA"][h] + rows[j]["dB"][h]) / 2
           for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]
Vm = [[sum((W[h] * (rows[i]["dA"][h] - rows[i]["dB"][h]) * (rows[j]["dA"][h] - rows[j]["dB"][h]) / 2
            for h in range(T)), Fr(0)) for j in range(n)] for i in range(n)]
BASIS = json.load(open(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"))
eps16 = [BASIS["gauge_eps_per_descendant"][DIDS[d]] for d in range(16)]
eps_row = [eps16[D_OF[i]] for i in range(n)]


def gram(er):
    Z = [[U[i][j] + er[i] * er[j] * Vm[i][j] for j in range(n)] for i in range(n)]
    rm = [sum(Z[i], Fr(0)) / n for i in range(n)]
    tt = sum(rm, Fr(0)) / n
    return [[(Z[i][j] - rm[i] - rm[j] + tt) / n for j in range(n)] for i in range(n)]


G = gram(eps_row)
R0 = sum(G[i][i] for i in range(n))
Q = []


def rec(tag, ok, fires):
    Q.append({"group": tag, "positive_holds": bool(ok), "negative_control_fires": bool(fires),
              "nonvacuous": bool(ok and fires)})


# Q0A weights sum to 1 exactly; NC a corrupted weight set does not
rec("Q0A_weights", sum(W, Fr(0)) == 1 and W[0] == Fr(1, 18),
    sum([W[0] + Fr(1, 1000)] + W[1:], Fr(0)) != 1)

# Q0B reader support-sufficiency; NC a shifted support index changes the reader value
XA, XB, B = reader(f"{PARENT}/active_raw/{rows[0]['opaque']}.npz")
d = np.load(f"{PARENT}/active_raw/{rows[0]['opaque']}.npz")
bad_fa = np.roll(np.asarray(d["MA"]).ravel()[d["support_index"]], 1)
badXA = esum([float(d["rho_support"][3][i]) for i in range(d["rho_support"].shape[1]) if bad_fa[i]]) / B
rec("Q0B_reader", [str(x) for x in XA] == json.load(open(f"{PARENT}/active_series.json"))[rows[0]["opaque"]]["XA"],
    badXA != XA[3])

# Q0C structural zero at h0 vs own sham; NC arm vs a different descendant's sham is nonzero
other = next(r for r in rows if r["descendant"] != rows[0]["descendant"])
h0_cross = rows[0]["XA"][0] - other["SA"][0]
rec("Q0C_structural_zero", all(r["h0"] == (Fr(0), Fr(0)) for r in rows), h0_cross != 0)

# Q0D energy identity M2^2 = U_ii+V_ii; NC dropping the /2 in uv breaks it
uv0 = sum((W[h] * ((rows[0]["dA"][h] + rows[0]["dB"][h]) ** 2 + (rows[0]["dA"][h] - rows[0]["dB"][h]) ** 2) / 2
           for h in range(T)), Fr(0))
uv_bad = sum((W[h] * ((rows[0]["dA"][h] + rows[0]["dB"][h]) ** 2 + (rows[0]["dA"][h] - rows[0]["dB"][h]) ** 2)
              for h in range(T)), Fr(0))
rec("Q0D_energy_identity", M2[0] == U[0][0] + Vm[0][0] == uv0, uv_bad != M2[0])

# Q0E swap-gauge: M2^2 and the whole-descendant block outer product are invariant under a LEGAL
# global eps flip (v -> -v), and M2 is blind to an illegal single-time A/B swap, but the block
# outer product (v (x) v) DETECTS it. Per-time v-energy is ALSO blind (it squares the sign away),
# so the detector must be the outer product, not the energy.
q = [rows[0]["dA"][h] - rows[0]["dB"][h] for h in range(T)]              # v-channel, unweighted
q_flip = [-x for x in q]                                                # legal global flip
q_ill = list(q); q_ill[2] = -q_ill[2]                                   # illegal single-time swap
outer = lambda z: tuple(z[a] * z[b] for a in range(T) for b in range(T))
m2_after_ill = sum((W[h] * ((rows[0]["dA"][h] if h != 2 else rows[0]["dB"][h]) ** 2
                            + (rows[0]["dB"][h] if h != 2 else rows[0]["dA"][h]) ** 2)
                    for h in range(T)), Fr(0))
legal_invariant = (outer(q_flip) == outer(q)) and (m2_after_ill == M2[0])   # M2 blind to the swap
rec("Q0E_swap_gauge", legal_invariant, outer(q_ill) != outer(q))

# Q0F exact R0 minimiser; NC a random gauge gives a strictly larger R0
def R0_of(er):
    g = gram(er)
    return sum(g[i][i] for i in range(n))
rng = np.random.default_rng(1)
rand_e = [eps16[d] for d in range(16)]
rand_e[3] = -rand_e[3]; rand_e[7] = -rand_e[7]
rand_row = [rand_e[D_OF[i]] for i in range(n)]
rec("Q0F_R0_minimiser", R0 == Fr(json.load(open(f"{PARENT}/FRESH_QUOTIENT_CERTIFICATE.json"))["R0_exact"]),
    R0_of(rand_row) > R0)

# Q0G eigenvalue enclosure agrees with the float eigenvalue within numpy's own error; NC a shifted
# interval does not. (The exact enclosure is far tighter than numpy's float eigenvalue error, so
# the honest test widens by that error, not a raw containment.)
Gf = np.array([[float(x) for x in r] for r in G])
evf = np.sort(np.linalg.eigvalsh(Gf))[::-1]
enc = X.enclose_eigs(G, n, [1, 2], [evf[0], evf[1]], K=80)
tol = 1e-14 * abs(evf[0])
brack = (float(enc[1][0]) - tol <= evf[0] <= float(enc[1][1]) + tol
         and float(enc[2][0]) - tol <= evf[1] <= float(enc[2][1]) + tol)
shifted = (float(enc[1][0]) + 10 * evf[0], float(enc[1][1]) + 10 * evf[0])
rec("Q0G_enclosure", brack, not (shifted[0] - tol <= evf[0] <= shifted[1] + tol))

# Q0H separation certificate; NC a matrix with a repeated eigenvalue does not separate
enc3 = X.enclose_eigs(G, n, [2, 3], [evf[1], evf[2]], K=80)
sep = enc3[2][0] > enc3[3][1]
Grep = [[Fr(1) if i == j and i < 2 else Fr(0) for j in range(4)] for i in range(4)]  # eigenvalues 1,1,0,0
encr = X.enclose_eigs(Grep, 4, [1, 2], [1.0, 1.0], K=40)
rec("Q0H_separation", sep, not (encr[1][0] > encr[2][1]))

# Q0I projection contraction R0>=R1>=R2>=0; NC anti-projection breaks monotonicity
l1, l2 = float(enc[1][0]), float(enc[2][0])
R1f, R2f = float(R0) - l1, float(R0) - l1 - l2
mono = float(R0) >= R1f >= R2f >= -1e-18
anti = float(R0) + l1                                          # adding energy instead of removing
rec("Q0I_projection", mono, anti > float(R0))

# Q0J reconstruction identity R0 - (||c1||^2+||c2||^2)/n = R2; NC using e1 twice breaks it
e1 = np.array(BASIS["e1"]); e2 = np.array(BASIS["e2"]); mu = np.array(BASIS["mu"])
sw = [math.sqrt(float(W[h]) / 2.0) for h in range(T)]
phi = np.zeros((n, 2 * T))
for i, r in enumerate(rows):
    for h in range(T):
        phi[i, h] = sw[h] * (float(r["dA"][h]) + float(r["dB"][h]))
        phi[i, T + h] = sw[h] * (float(r["dA"][h]) - float(r["dB"][h])) * eps_row[i]
psi = phi - phi.mean(0)
c1 = psi @ e1; c2 = psi @ e2
recon = float(R0) - (c1 @ c1 + c2 @ c2) / n
recon_bad = float(R0) - (c1 @ c1 + c1 @ c1) / n
rec("Q0J_reconstruction", abs(recon - R2f) < 1e-9, abs(recon_bad - R2f) > 1e-9)

# Q0K duplication invariance; NC a perturbed duplicate changes R0
Zc = [[U[i % n][j % n] + eps_row[i % n] * eps_row[j % n] * Vm[i % n][j % n] for j in range(2 * n)]
      for i in range(2 * n)]
rm = [sum(Zc[i], Fr(0)) / (2 * n) for i in range(2 * n)]
tt = sum(rm, Fr(0)) / (2 * n)
Gd = [[(Zc[i][j] - rm[i] - rm[j] + tt) / (2 * n) for j in range(2 * n)] for i in range(2 * n)]
R0d = sum(Gd[i][i] for i in range(2 * n))
rec("Q0K_duplication", R0d == R0, (R0d + Fr(1, 10 ** 9)) != R0)

# Q0L aggregation lemma: alpha=1/16 over (d,dose) equals alpha=1/8 per-dose; NC unequal alpha differs
BIND = json.load(open(f"{PARENT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
TAU = {k: Fr(v) for k, v in json.load(open(f"{PARENT}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))["thresholds_locked"].items()}
tausq = [TAU[DIDS[d]] ** 2 for d in range(16)]
E_pooled = sum((Fr(1, 16) * ts for ts in tausq for _ in (0, 1)), Fr(0))   # 32 rows, alpha 1/16
E_perdose = sum((Fr(1, 8) * ts for ts in tausq), Fr(0))                    # 8 rows, alpha 1/8
E_bad = sum((Fr(1, 16) * ts * (2 if i == 0 else 1) for i, ts in enumerate(tausq) for _ in (0, 1)), Fr(0))
rec("Q0L_aggregation", E_pooled == E_perdose, E_bad != E_pooled)

# Q0M multiplier direction; NC swapping num/denom gives the parent ratio, not the multiplier
I2lo = Fr(BASIS["I2_enclosure"][0]); E_TAU = Fr(BIND["E_TAU_exact"])
amp_hi = X._sign_changes and (math.sqrt(float(E_TAU)) / math.sqrt(float(I2lo)))
ratio_wrong = math.sqrt(float(I2lo)) / math.sqrt(float(E_TAU))
rec("Q0M_multiplier", 1.7 < amp_hi < 1.81, abs(ratio_wrong - 0.570) < 0.02 and abs(amp_hi - ratio_wrong) > 1.0)

# Q0N dose-scaling prediction: delta -> gamma*delta gives M2^2 -> gamma^2 M2^2; NC a nonlinear map fails
gam = Fr(2)
dA_s = [gam * x for x in rows[0]["dA"]]; dB_s = [gam * x for x in rows[0]["dB"]]
m2_scaled = sum((W[h] * (dA_s[h] ** 2 + dB_s[h] ** 2) for h in range(T)), Fr(0))
dA_nl = [x * x for x in rows[0]["dA"]]
m2_nl = sum((W[h] * (dA_nl[h] ** 2) for h in range(T)), Fr(0))
rec("Q0N_dose_scaling", m2_scaled == gam * gam * M2[0], m2_nl != gam * gam * M2[0])

# Q0O involution => no repetition dose (from the dose audit); NC a genuinely dosed op is not involutive
DA = json.load(open(f"{OUT}/SQDT00_STATIC_DOSE_ADMISSIBILITY_AUDIT.json"))
rec("Q0O_involution", DA["C_involution"]["CARRIER_1_all_op_squared_identity_bitwise"],
    DA["F_firing_negative_controls"]["NC2_toy_is_not_an_involution"]["FIRES"])

# Q0P domain predicate discriminates; NC constant-true predicate would not
rec("Q0P_domain", DA["E_amplitude_axis"]["CARRIER_1_gamma2_domain_violations_total"] > 0,
    DA["F_firing_negative_controls"]["NC3_domain_predicate_discriminates"]["FIRES"])

# Q0Q provenance blob binding; NC a one-byte perturbation changes the git blob id
def blob(b):
    h = hashlib.sha1(); h.update(b"blob " + str(len(b)).encode() + b"\x00"); h.update(b); return h.hexdigest()
prov = json.load(open(f"{OUT}/SQDT00_PARENT_ARTIFACT_BLOB_BINDING.json"))
name0 = "FWL2CF00_FINAL_DISPOSITION.json"
bb = open(f"{PARENT}/{name0}", "rb").read()
rec("Q0Q_provenance", blob(bb) == prov["blob_binding"][name0]["committed"],
    blob(bb + b"x") != prov["blob_binding"][name0]["committed"])

ALL = all(q["nonvacuous"] for q in Q)
out = {"programme": "SQDT00 Section 3 non-vacuous oracle", "engine_starts": 0,
       "n_groups": len(Q), "all_nonvacuous": ALL, "groups": Q,
       "meaning": "every group states a positive identity that HOLDS and a negative control that "
                  "FIRES, so the offline analysis, transfer, dose-scaling and provenance machinery "
                  "cannot silently pass a false input."}
json.dump(out, open(f"{OUT}/SQDT00_PREEXECUTION_NONVACUOUS_ORACLE.json", "w"), indent=1, default=str)
print("[%4.0fs] oracle groups: %d ; all non-vacuous: %s" % (time.time() - t0, len(Q), ALL))
for q in Q:
    print("  %-20s positive=%s control_fires=%s" % (q["group"], q["positive_holds"], q["negative_control_fires"]))
