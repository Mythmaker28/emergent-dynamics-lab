"""FSCMA00 Sections 5-8. ZERO engine starts. All decisions frozen before the first probe outcome.

5. A/B QUOTIENT. The endpoint pair is UNORDERED, canonicalised per founder by sorted site-id
   lists, so there is no a-priori convention linking founder b's channel A to founder b''s. A
   single affine family across founders is meaningless until an orientation is chosen. Global
   gauge: the lexicographically first BASIS founder is fixed no_swap; the other five are
   enumerated exhaustively (2^5 = 32); the winner minimises the exact weighted residual of the
   one-mode model. Screening is float; the winner-vs-runner-up decision is certified exactly.
6. PROTOCOL FREEZE: carrier sentinels, environmental operators, gate definitions.
7. PANEL, CONTAMINATION AND THE FROZEN WORST-CASE START-ACCOUNTING MATRIX.
8. AFFINE FAMILY S1 = {mu + a*phi1} fitted on the oriented carrier BASIS, with its tube gates.
"""
from __future__ import annotations
import sys, json, hashlib, itertools
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np

OUT = "/home/claude/sweep/FSCMA00"
PAR = "/home/claude/sweep/WSFSCRP00"
LED = json.load(open(f"{PAR}/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json"))
Q01 = json.load(open(f"{PAR}/wsfscrp_q01.json"))
U = Q01["Q1"]
T = 10
PHYS = [Fr(40 * i) * Fr(1, 10) for i in range(1, 11)]
v = [Fr(0)] * T
v[0] = (PHYS[1] - PHYS[0]) / 2
v[T - 1] = (PHYS[T - 1] - PHYS[T - 2]) / 2
for j in range(1, T - 1):
    v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(v, Fr(0)) for x in v]
SW = np.array([float(w) ** 0.5 for w in W])
A = [[Fr(x) for x in u["dA"]] for u in U]
B = [[Fr(x) for x in u["dB"]] for u in U]
SEED = [u["seed"] for u in U]
FAM = [u["superfamily"].split("_")[0] for u in U]
BASIS = sorted({s for s in SEED})
GAUGE = BASIS[0]
FREE = BASIS[1:]
R = {}

# =====================================================================================
# 5. A/B QUOTIENT
# =====================================================================================
def oriented(swapset):
    """Return the 12x20 float matrix under a given set of swapped founders."""
    rows = []
    for k in range(len(U)):
        a, b = A[k], B[k]
        if SEED[k] in swapset:
            a, b = b, a
        rows.append([float(x) for x in a] + [float(x) for x in b])
    M = np.array(rows)
    return np.concatenate([M[:, :T] * SW, M[:, T:] * SW], axis=1)


def resid_float(swapset):
    X = oriented(swapset)
    Xc = X - X.mean(0, keepdims=True)
    s = np.linalg.svd(Xc, compute_uv=False)
    return float(np.sum(s ** 2) - s[0] ** 2), float(s[0] ** 2 / np.sum(s ** 2))


configs = []
for bits in itertools.product([0, 1], repeat=len(FREE)):
    sw = frozenset(f for f, b in zip(FREE, bits) if b)
    r, share = resid_float(sw)
    configs.append({"swapped": sorted(sw), "residual": r, "lam1_share": share})
configs.sort(key=lambda c: c["residual"])
best, runner = configs[0], configs[1]


# ---- exact certification of the winner against the runner-up -------------------------
def gram_exact(swapset):
    rows = []
    for k in range(len(U)):
        a, b = (B[k], A[k]) if SEED[k] in swapset else (A[k], B[k])
        rows.append(list(a) + list(b))
    n = len(rows)
    mu = [sum((rows[k][j] for k in range(n)), Fr(0)) / n for j in range(2 * T)]
    Xc = [[rows[k][j] - mu[j] for j in range(2 * T)] for k in range(n)]
    ww = W + W
    return [[sum((ww[j] * Xc[k][j] * Xc[l][j] for j in range(2 * T)), Fr(0)) for l in range(n)]
            for k in range(n)]


def lam1_bracket(G, iters=70):
    n = len(G)

    def nb(t):
        M = [[G[i][j] - (t if i == j else Fr(0)) for j in range(n)] for i in range(n)]
        neg = 0
        for i in range(n):
            p = M[i][i]
            if p == 0:
                return None
            if p < 0:
                neg += 1
            for r in range(i + 1, n):
                f = M[r][i] / p
                if f:
                    for c in range(i, n):
                        M[r][c] -= f * M[i][c]
        return neg

    def cnt(t):
        for k in range(40):
            r = nb(t if k == 0 else t - Fr(1, 10 ** 40) * k)
            if r is not None:
                return r
        raise RuntimeError

    tr = sum(G[i][i] for i in range(n))
    lo, hi = Fr(0), tr * 2 + 1
    for _ in range(iters):
        mid = (lo + hi) / 2
        if cnt(mid) <= n - 1:
            lo = mid
        else:
            hi = mid
    return lo, hi, tr


gb = gram_exact(frozenset(best["swapped"]))
gr = gram_exact(frozenset(runner["swapped"]))
l1b, h1b, trb = lam1_bracket(gb)
l1r, h1r, trr = lam1_bracket(gr)
res_best_hi = trb - l1b          # upper bound on the winner's residual
res_run_lo = trr - h1r           # lower bound on the runner-up's residual
strict = res_best_hi < res_run_lo
R["S5_AB_quotient"] = {
    "why": "the endpoint pair is unordered and canonicalised per founder by sorted site-id "
           "lists; channel A of one founder has no a-priori relation to channel A of another. "
           "Fitting one affine family across founders requires an orientation first.",
    "gauge": {"fixed_founder": GAUGE, "fixed_to": "no_swap",
              "reason": "lexicographically first BASIS founder; fixing one founder removes the "
                        "global sign degeneracy, which is not identifiable and never will be."},
    "enumeration": {"n_free_founders": len(FREE), "n_configurations": len(configs),
                    "objective": "exact weighted residual of the one-mode model, "
                                 "trace(G) - lambda_1(G)"},
    "winner": best, "runner_up": runner,
    "exact_certificate": {
        "winner_residual_upper_bound": str(res_best_hi),
        "runner_up_residual_lower_bound": str(res_run_lo),
        "strictly_separated": bool(strict),
        "relative_gap": float((res_run_lo - res_best_hi) / res_best_hi) if strict else None},
    "VERDICT": ("AB_QUOTIENT_IDENTIFIED" if strict else "A_B_QUOTIENT_NONIDENTIFIABLE"),
    "orientation": {str(s): ("swap" if s in best["swapped"] else "no_swap") for s in BASIS},
}
SWAP = frozenset(best["swapped"])

# =====================================================================================
# 8. AFFINE FAMILY on the oriented carrier BASIS
# =====================================================================================
X = oriented(SWAP)
MU = X.mean(0)
Xc = X - MU
_, sv, vt = np.linalg.svd(Xc, full_matrices=False)
PHI1 = vt[0]
a_bf = Xc @ PHI1
RESID = Xc - np.outer(a_bf, PHI1)
off1 = np.linalg.norm(RESID, axis=1) / np.linalg.norm(Xc, axis=1)
off1_unc = np.linalg.norm(RESID, axis=1) / np.linalg.norm(X, axis=1)
O_BASIS = float(np.sum(RESID ** 2) / np.sum(Xc ** 2))
cells = [{"seed": SEED[k], "superfamily": FAM[k], "a": float(a_bf[k]),
          "OFF1_centered": float(off1[k]), "OFF1_uncentered": float(off1_unc[k])}
         for k in range(len(U))]
R["S8_affine_family"] = {
    "model": "S1 = { mu + a * phi1 }, one free scalar a per cell, fitted on the 12 oriented "
             "carrier BASIS cells in the sqrt(w)-weighted two-channel coordinate.",
    "definitions": {
        "OFF1_centered": "||r - mu - a*phi1||_w / ||r - mu||_w  -- the STRICT reading, and the "
                         "one the gate uses. It asks what fraction of a cell's DEVIATION from "
                         "the common response is unexplained by the single mode.",
        "OFF1_uncentered": "||r - mu - a*phi1||_w / ||r||_w -- reported only because it is the "
                           "flattering reading; it is not gated on.",
        "O_BASIS": "total unexplained centered energy fraction = 1 - lambda_1/trace(G)"},
    "gates": {"O_BASIS_lt_0.05": bool(O_BASIS < 0.05),
              "all_OFF1_lt_0.10": bool(all(off1 < 0.10)),
              "O_BASIS": O_BASIS, "OFF1_max": float(off1.max()), "OFF1_min": float(off1.min())},
    "cells": cells,
    "mu": MU.tolist(), "phi1": PHI1.tolist(),
    "singular_values": sv.tolist(),
}
R["S8_affine_family"]["BASIS_TUBE_PASS"] = bool(O_BASIS < 0.05 and all(off1 < 0.10))

# =====================================================================================
# 6 + 7. PROTOCOL FREEZE, PANEL, CONTAMINATION, START ACCOUNTING
# =====================================================================================
MAN = json.load(open(f"{PAR}/WSFSCRP00_INTERVENTION_SUPERFAMILY_MANIFEST.json"))
locked = [tuple(x) for x in LED["roles"]["LOCKED_DEV_EVALUATION"]]
scored_seeds = sorted({r["seed"] for r in Q01["Q1"]} | {r["seed"] for r in Q01["Q0"]})
R["S6_protocol_freeze"] = {
    "carrier_sentinels": {
        "CARRIER_1": {"superfamily": MAN["TRAIN_SUPERFAMILY_1"]["id"],
                      "instance": MAN["TRAIN_SUPERFAMILY_1"]["canonical_sentinel_instance"],
                      "callable": "etcmnfc_core.transpose(st, I, J)"},
        "CARRIER_2": {"superfamily": MAN["TRAIN_SUPERFAMILY_2"]["id"],
                      "instance": MAN["TRAIN_SUPERFAMILY_2"]["canonical_sentinel_instance"],
                      "callable": "ppai_core.state_cross(st)"},
        "uniqueness_proof": [
            "The parent manifest names exactly one canonical_sentinel_instance per TRAIN "
            "superfamily, and no other instance appears anywhere in the parent's scored path.",
            "The parent's executable make_ops() constructs exactly two operators and no more.",
            "The parent's 12 scored cells are exactly 6 founders x these 2 sentinels.",
        ],
        "VERDICT": "PARENT_CARRIER_SENTINEL_IDENTITY_RESOLVED"},
    "environmental_operators": {
        "ENV_PRIMARY": {"callable": "domc_core._perturb_N(st, 0.5)", "amp": 0.5,
                        "algebra": "N <- clip(N + 0.5*N0, 0, None); additive, global, exact"},
        "ENV_SECONDARY": {"callable": "domc_core._perturb_N(st, 0.25)", "amp": 0.25,
                          "status": "statically admissible; execution decided by the frozen "
                                    "start-accounting matrix below"}},
    "sham": "identity copy, st.copy()",
    "endpoint": "inherited unchanged from WSFSCRP00: fixed t0 supports, B from raw baseline "
                "bytes, q_A/q_B, delta vs sham, trapezoid weights over physical time 4.0..40.0",
    "no_change_declarations": {"NEW_LAWSPEC": False, "ENGINE_EQUATION_CHANGE": False,
                               "NEW_STATE_VARIABLE_OR_TRACER": False,
                               "CHECKPOINT_TIME_CHANGE": False, "HORIZON_CHANGE": False,
                               "FIXED_SUPPORT_READER_CHANGE": False,
                               "DIRECT_RHO_INTERVENTION": False,
                               "DYNAMIC_COMPONENT_REDETECTION": False},
}
R["S7_panel"] = {
    "reuse_conditions": {
        "allocation_made_before_any_outcome":
            "roles were assigned in wsfscrp_gen.py by a salted hash of an OPAQUE founder id, in "
            "the same file that froze the queue, before any Q0/Q1 outcome existed",
        "locked_founders_never_scored": len(set(s for s, _ in locked) & set(scored_seeds)) == 0,
        "locked_ancestry_clusters": len({s for s, _ in locked}),
        "locked_geometry_classes": sorted({g for _, g in locked}),
        "parent_engine_starts_accounted": Q01["engine_starts"]["n"]},
    "panel": {"BASIS": [[s, g] for s, g in [tuple(x) for x in LED["roles"]["TRAIN_SELECTION"]]],
              "LOCKED": [[s, g] for s, g in locked]},
    "LABEL": "OUTCOME_UNSEEN_FEATURE_EXPOSED_FIXED_PANEL",
    "label_justification":
        "outcome-unseen: no scored quantity has ever been computed on a LOCKED founder. "
        "feature-exposed: their checkpoints, masks, support sizes and B values WERE computed and "
        "hashed by the parent during generation, so they are not naive states. The weaker of the "
        "two labels is the one that governs.",
}
R["S7_contamination_ledger"] = {
    "read_by_this_programme_so_far": [
        "parent archive + SHA256SUMS (49 entries, all verified)",
        "parent wsfscrp_q01.json: the FULL 12-cell TRAIN outcome matrix (BASIS; permitted)",
        "parent wsfscrp_q234.json: Q2/Q3/Q4 summaries (BASIS; permitted)",
        "parent ledgers and manifests (identifiers, roles, hashes)",
        "BASIS founder checkpoints and masks (6 founders)",
        "LOCKED founder IDENTIFIERS ONLY, from the role ledger",
    ],
    "not_read": [
        "LOCKED founder checkpoint or mask arrays -- no LOCKED .npz has been opened",
        "any project primary or held-out namespace; 62000-62009 remains unopened and unread",
    ],
    "orientation_was_fitted_on": "BASIS carrier cells only",
    "affine_family_was_fitted_on": "BASIS carrier cells only",
    "prediction_frozen_before": "any environmental engine start",
}
R["S7_frozen_start_accounting"] = {
    "frozen_before": "the first environmental outcome of this programme",
    "caps": {"MAX_PROBE_ENGINE_STARTS": 24, "MAX_LOCKED_ENGINE_STARTS": 60, "MAX_TOTAL": 84},
    "PROBE": {"SHAM_per_BASIS_founder": 1, "n_BASIS": 6, "sham": 6,
              "ENV_PRIMARY": 6, "ENV_SECONDARY": 6,
              "SHAM_REPLICATE_determinism_recheck_on_" + str(GAUGE): 1,
              "total": 19, "headroom": 24 - 19},
    "LOCKED": {"SHAM": 6, "CARRIER_1": 6, "CARRIER_2": 6, "ENV_PRIMARY": 6,
               "total": 24, "headroom": 60 - 24},
    "GRAND_TOTAL": 43, "grand_headroom": 84 - 43,
    "audit_starts": 0,
    "audit_note": "Phase 1 spent ZERO engine starts. The coordinate frame and the one-step "
                  "dependency matrix were established by parsing the engine source, which is a "
                  "statement about ALL states rather than about the one state a probe would "
                  "have tested. The operator audit applied operators to checkpoint bytes and "
                  "diffed them without stepping.",
    "worst_case_note": "these are worst-case counts: every listed arm is assumed to run. No "
                       "retry of a scored arm is budgeted, because MAX_POST_SCORED_OUTPUT_RETRIES "
                       "is 0. The headroom is reserved for pre-outcome infrastructure failures.",
    "VERDICT": "FROZEN_START_BUDGET_SUFFICIENT",
}

json.dump(R, open(f"{OUT}/FSCMA00_S5_S8.json", "w"), indent=1, default=str)

print("S5 A/B quotient")
print("   gauge founder %d fixed no_swap; %d configurations" % (GAUGE, len(configs)))
print("   winner swapped:", best["swapped"], "residual=%.6e lam1_share=%.5f"
      % (best["residual"], best["lam1_share"]))
print("   runner  swapped:", runner["swapped"], "residual=%.6e" % runner["residual"])
print("   exact: winner_res_hi=%.6e < runner_res_lo=%.6e -> %s  (relative gap %.3f)"
      % (float(res_best_hi), float(res_run_lo), strict,
         R["S5_AB_quotient"]["exact_certificate"]["relative_gap"] or -1))
print("   VERDICT:", R["S5_AB_quotient"]["VERDICT"])
print("   orientation:", R["S5_AB_quotient"]["orientation"])
print("\nS8 affine family on the oriented carrier BASIS")
print("   singular values:", ["%.4e" % s for s in sv[:4]])
print("   O_BASIS = %.5f (gate <0.05: %s)   OFF1 in [%.4f, %.4f] (gate all <0.10: %s)"
      % (O_BASIS, O_BASIS < 0.05, off1.min(), off1.max(), bool(all(off1 < 0.10))))
for c in cells:
    print("      %5d %-3s a=%+.4e OFF1=%.4f" % (c["seed"], c["superfamily"], c["a"],
                                                c["OFF1_centered"]))
print("   BASIS_TUBE_PASS:", R["S8_affine_family"]["BASIS_TUBE_PASS"])
print("\nS6/S7 frozen. LOCKED never scored:",
      R["S7_panel"]["reuse_conditions"]["locked_founders_never_scored"],
      "| clusters:", R["S7_panel"]["reuse_conditions"]["locked_ancestry_clusters"],
      "| start budget:", R["S7_frozen_start_accounting"]["GRAND_TOTAL"], "of 84")
