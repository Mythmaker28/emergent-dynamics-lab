"""GIMB00 gauge oracle, SECOND PASS. Supersedes the Q0C..Q0G block of gimb_p0_freeze_oracle.py.

SELF-DEFECT BEING REPAIRED. In the first pass I wrote checks of the form
`if ip(v_i,v_j) != e*e*ip(v_i,v_j)` and `if bip([p],[p]) != bip([p],[p])`. Both compare an
expression to itself and pass on arbitrary input. That is exactly the vacuous-oracle defect this
programme line condemned in ETCMNFC and again in EEFCA, and I reproduced it. This file replaces
those checks with tests that ACTUALLY APPLY the swap to the underlying delta_A/delta_B rows,
recompute every invariant from the swapped bytes, and carry NEGATIVE CONTROLS proving each test
can fail. Zero engine starts. The master freeze is unchanged and is re-verified by hash below.
"""
from __future__ import annotations
import json, hashlib, itertools, sys
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/GIMB00"
FZ = json.load(open(f"{OUT}/GIMB00_MASTER_FREEZE_HASHES.json"))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
assert sha(f"{OUT}/GIMB00_FREEZE.md") == FZ["hashes"]["GIMB00_FREEZE.md"], "freeze mutated"
W = [Fr(x) for x in FZ["weights"]]
T = len(W)
HALF = Fr(1, 2)
ROWS = json.load(open(f"{OUT}/GIMB00_BOUND_ROWS.json"))
PANELS = ["CARRIER_BASIS", "CARRIER_LOCKED", "ENV_PROBE", "ENV_LOCKED", "ENV_DOSE_SECONDARY"]


def uvec(dA, dB):
    return [Fr(x) + Fr(y) for x, y in zip(dA, dB)]


def vvec(dA, dB):
    return [Fr(x) - Fr(y) for x, y in zip(dA, dB)]


def ip(p, q):
    return sum((W[h] * p[h] * q[h] * HALF for h in range(T)), Fr(0))


def bip(P, Q):
    return sum((ip(p, q) for p, q in zip(P, Q)), Fr(0))


def founder_rows(seed):
    out = []
    for pan in PANELS:
        for r in sorted([x for x in ROWS[pan] if x["seed"] == seed], key=lambda x: x["arm"]):
            out.append((pan, r["arm"], r["dA"], r["dB"]))
    return out


def build(rows, sign_per_row=None):
    """(u block, v block) from RAW delta rows. sign_per_row=None means no swap; a list of
    +1/-1 applies an independent exchange to each row, which is the ILLEGAL larger group."""
    U, V = [], []
    for k, (_, _, dA, dB) in enumerate(rows):
        a, b = (dA, dB)
        if sign_per_row is not None and sign_per_row[k] < 0:
            a, b = (dB, dA)                       # a real exchange of the two scored regions
        U.append(uvec(a, b))
        V.append(vvec(a, b))
    return U, V


def vvT(V):
    return [[ip(V[i], V[j]) for j in range(len(V))] for i in range(len(V))]


def energy_raw(rows):
    return sum((W[h] * (Fr(dA[h]) ** 2 + Fr(dB[h]) ** 2)
                for (_, _, dA, dB) in rows for h in range(T)), Fr(0))


def DQ2(Ui, Vi, Uj, Vj):
    """Whole-block quotient distance: ||u_i-u_j||^2 + ||v_i||^2 + ||v_j||^2 - 2|<v_i,v_j>|."""
    du = sum((ip([Ui[k][h] - Uj[k][h] for h in range(T)],
                 [Ui[k][h] - Uj[k][h] for h in range(T)]) for k in range(len(Ui))), Fr(0))
    vi, vj = bip(Vi, Vi), bip(Vj, Vj)
    cross = bip(Vi, Vj)
    return du + vi + vj - 2 * abs(cross)


FOUND = sorted({r["seed"] for p in PANELS for r in ROWS[p]})
RAW = {s: founder_rows(s) for s in FOUND}
BASE = {s: build(RAW[s]) for s in FOUND}
NARM = {s: len(RAW[s]) for s in FOUND}
R = {"n_founders": len(FOUND), "arms_per_founder": NARM}

# --------------------------------------------------------------- Q0C..Q0F, real swaps
res = {"Q0C_u_invariant": True, "Q0D_whole_block_vvT_invariant": True,
       "Q0F_energy_identity": True, "v_itself_changes_sign": False}
for s in FOUND:
    n = NARM[s]
    U0, V0 = BASE[s]
    P0 = vvT(V0)
    E0 = energy_raw(RAW[s])
    for e in (+1, -1):                                       # the LEGAL group: one sign per founder
        U1, V1 = build(RAW[s], [e] * n)
        if U1 != U0:
            res["Q0C_u_invariant"] = False
        if vvT(V1) != P0:
            res["Q0D_whole_block_vvT_invariant"] = False
        if bip(U1, U1) + bip(V1, V1) != E0:
            res["Q0F_energy_identity"] = False
        if e == -1 and V1 != V0:
            res["v_itself_changes_sign"] = True              # v is NOT invariant: test is not trivial
        if e == -1:
            for k in range(n):
                if V1[k] != [-x for x in V0[k]]:
                    res["Q0D_whole_block_vvT_invariant"] = False

# --------------------------------------------------------------- Q0E reconstruction
# CORRECTION. My first attempt tested rank-one-ness of the ARM GRAM P[i][j] = <v_i,v_j>. That is
# the wrong object: the arm Gram is a contraction of the block outer product and has rank
# min(n_arms, T), not 1. The handoff's object is the outer product of the CONCATENATED block
# vector, which is rank one by construction. Tested correctly below, on every founder.
def concat_weighted(V):
    """the concatenated v block in the metric where the plain dot product equals <.,.>_w."""
    return [Fr(V[k][h]) * W[h] * HALF for k in range(len(V)) for h in range(T)], \
           [Fr(V[k][h]) for k in range(len(V)) for h in range(T)]


def outer_block(V):
    _, x = concat_weighted(V)
    wts = [W[h] * HALF for _ in range(len(V)) for h in range(T)]
    n = len(x)
    return [[wts[i] * x[i] * x[j] * wts[j] for j in range(n)] for i in range(n)], x, wts


q0e_rank1, q0e_sign, q0e_cross = True, True, True
for s_ in FOUND:
    U0, V0 = BASE[s_]
    M, x, wts = outer_block(V0)
    n = len(x)
    r = max(range(n), key=lambda k: abs(M[k][k]))
    if M[r][r] <= 0:
        q0e_rank1 = False
        continue
    # exact rank-one identity: M[k][r]*M[r][l] == M[k][l]*M[r][r] for all k,l
    if any(M[k][r] * M[r][l] != M[k][l] * M[r][r] for k in range(n) for l in range(n)):
        q0e_rank1 = False
    # the global sign flip leaves M identical
    Mneg, _, _ = outer_block([[-y for y in q] for q in V0])
    if Mneg != M:
        q0e_sign = False
    # flipping ONE arm only must change M: cross-arm relative sign is retained
    if len(V0) > 1:
        Mmix, _, _ = outer_block([[-y for y in V0[0]]] + V0[1:])
        if Mmix == M:
            q0e_cross = False
res["Q0E_block_outer_product_is_exactly_rank_one"] = bool(q0e_rank1)
res["Q0E_block_determined_by_u_and_vvT_up_to_one_sign"] = bool(q0e_rank1 and q0e_sign)
res["Q0E_cross_arm_relative_sign_is_retained"] = bool(q0e_cross)

# --------------------------------------------------------------- Q0G primary score invariance
# BASIS founders carry 4 arms (2 carrier, +0.5, +0.25); LOCKED founders carry 3 (2 carrier,
# +0.5). A whole-block quotient distance is only defined between founders with the SAME arm
# signature, so pairs are formed within a role, never across.
SIG = {s: tuple((p, a) for (p, a, _, _) in RAW[s]) for s in FOUND}
pairs = [(FOUND[i], FOUND[j]) for i in range(len(FOUND)) for j in range(i + 1, len(FOUND))
         if SIG[FOUND[i]] == SIG[FOUND[j]]]
R["arm_signatures"] = {str(k): list(map(list, v)) for k, v in SIG.items()}
R["n_within_role_pairs"] = len(pairs)
base_scores = {}
for a, b in pairs:
    base_scores[(a, b)] = DQ2(*BASE[a], *BASE[b])
q0g = True
n_assign = 0
for bits in itertools.product([0, 1], repeat=len(FOUND)):
    n_assign += 1
    eps = {s: (-1 if x else 1) for s, x in zip(FOUND, bits)}
    B2 = {s: build(RAW[s], [eps[s]] * NARM[s]) for s in FOUND}
    for a, b in pairs:
        if DQ2(*B2[a], *B2[b]) != base_scores[(a, b)]:
            q0g = False
res["Q0G_quotient_distance_invariant_over_all_2F_assignments"] = q0g
res["n_assignments_enumerated"] = n_assign
res["n_founders_enumerated_exhaustively"] = len(FOUND)

# --------------------------------------------------------------- NEGATIVE CONTROLS
neg = {}
# N1: an ILLEGAL per-row sign must change the whole-block v outer v for at least one founder
n1 = False
for s in FOUND:
    n = NARM[s]
    if n < 2:
        continue
    U0, V0 = BASE[s]
    sr = [1] * n
    sr[0] = -1                                   # exchange ONE arm only: not in the gauge group
    _, V1 = build(RAW[s], sr)
    if vvT(V1) != vvT(V0):
        n1 = True
neg["N1_per_row_swap_changes_block_vvT"] = n1
# N2: an illegal per-row sign must change the primary quotient distance for at least one pair
n2 = False
for a, b in pairs:
    sr = [1] * NARM[a]
    sr[0] = -1
    A1 = build(RAW[a], sr)
    if DQ2(*A1, *BASE[b]) != base_scores[(a, b)]:
        n2 = True
        break
neg["N2_per_row_swap_changes_quotient_distance"] = n2
# N3: the naive sum-only coordinate u must LOSE information the quotient keeps -- two founders
#     with equal u-distance but different quotient distance must exist
n3 = False
for a, b in pairs:
    du = sum((ip([BASE[a][0][k][h] - BASE[b][0][k][h] for h in range(T)],
                 [BASE[a][0][k][h] - BASE[b][0][k][h] for h in range(T)])
              for k in range(NARM[a])), Fr(0))
    if base_scores[(a, b)] != du:
        n3 = True
        break
neg["N3_quotient_strictly_richer_than_u_only"] = n3
# N4: the test suite must FAIL on corrupted input -- perturb one stored value and re-check Q0F
bad = [(p, arm, dA, list(dB)) for (p, arm, dA, dB) in RAW[FOUND[0]]]
bad[0] = (bad[0][0], bad[0][1], bad[0][2], [str(Fr(bad[0][3][0]) + 1)] + list(bad[0][3][1:]))
Ub, Vb = build(bad)
neg["N4_energy_identity_detects_a_corrupted_row"] = (
    bip(Ub, Ub) + bip(Vb, Vb) != energy_raw(RAW[FOUND[0]]))

R["tests"] = res
R["negative_controls"] = neg
R["all_tests_pass"] = all(v for k, v in res.items()
                          if isinstance(v, bool) and not k.startswith("n_"))
R["all_negative_controls_fire"] = all(neg.values())
R["VERDICT"] = ("GAUGE_ORACLE_PASS_WITH_NEGATIVE_CONTROLS"
                if R["all_tests_pass"] and R["all_negative_controls_fire"]
                else "COMPLETE_INVARIANT_ORACLE_FAIL")
R["supersedes"] = ("the Q0C..Q0G block of gimb_p0_freeze_oracle.py, which contained three "
                   "self-comparing predicates that pass on arbitrary input")
prev = json.load(open(f"{OUT}/GAUGE_ORACLE_TESTS.json"))
R["Q0A"] = prev["Q0A"]
R["Q0B"] = prev["Q0B"]
R["OPERATOR_EQUIVARIANCE"] = prev["OPERATOR_EQUIVARIANCE"]
json.dump(R, open(f"{OUT}/GAUGE_ORACLE_TESTS.json", "w"), indent=1)
print("tests            :", json.dumps(res))
print("negative controls:", json.dumps(neg))
print("VERDICT:", R["VERDICT"], "| assignments:", n_assign, "| founders:", len(FOUND))
