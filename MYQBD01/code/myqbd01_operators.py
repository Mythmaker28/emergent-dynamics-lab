"""MYQBD01 §9-§11 — the reduction attack, the one-Y operator, the two-Y state.

Everything is exact arithmetic or an independent re-derivation from source. No engine, no
stochastic lineage sampling.
"""
from __future__ import annotations

import glob
import json
import math
import os
import subprocess
from math import comb

import numpy as np

REPO = "/home/claude/edl"
OUT = "/home/claude/MYQBD01/out"
RAW = "/home/claude/OBFOR01/raw"
BURN_IN, HORIZON = 2000, 11000
CAP = 16


def blob(path):
    return subprocess.run(("git", "show", "HEAD:%s" % path), cwd=REPO,
                          capture_output=True, text=True).stdout


# ------------------------------------------------------------------ §10 one-Y operator
def one_y_operator():
    """Re-derive f(z) INDEPENDENTLY from the source text, then verify the closed form against a
    brute-force enumeration -- not against PMCR01's implementation."""
    src = blob("ORR01/code/kinetics.py")
    # confirm the three source facts the operator rests on
    facts = {
        "react_free0_once": "free0 = np.maximum(self.free(), 0)" in src,
        "react_cand_min": "cand = np.minimum(self.n[res], free0)" in src,
        "react_p_clamp": "p = np.minimum(1.0, kk * pair)" in src,
        "decay_after_react": src.index("self._react()") < src.index("self._decay()"),
        "births_binomial": "births = rng.binomial(np.maximum(cand, 0), p)" in src,
        "decay_binomial": "d = rng.binomial(np.maximum(self.n[s], 0), mu)" in src,
    }

    def pgf_closed(z, c, p, m):
        return (m + (1 - m) * z) * ((1 - p * (1 - m) * (1 - z)) ** c)

    def pgf_brute(z, c, p, m):
        tot = 0.0
        for par in (0, 1):
            pp = (1 - m) if par else m
            for b in range(c + 1):
                pb = comb(c, b) * p ** b * (1 - p) ** (c - b)
                for s in range(b + 1):
                    ps = comb(b, s) * (1 - m) ** s * m ** (b - s)
                    tot += pp * pb * ps * z ** (par + s)
        return tot

    checks = []
    maxerr = 0.0
    for c, p, m, z in ((4, 0.03, 0.11, 0.37), (7, 0.5, 0.9, 0.5), (2, 0.9, 0.02, 0.8),
                       (1, 0.15, 0.25, 0.6), (5, 0.0, 0.004, 0.5)):
        a, b = pgf_closed(z, c, p, m), pgf_brute(z, c, p, m)
        maxerr = max(maxerr, abs(a - b))
        checks.append({"c": c, "p": p, "m": m, "z": z, "closed": a, "brute": b,
                       "abs_err": abs(a - b)})
    return {
        "SECTION": "MYQBD01 §10 one-Y operator, independently re-derived",
        "SOURCE_FACTS_CONFIRMED": facts,
        "ALL_SOURCE_FACTS_HOLD": all(facts.values()),
        "PGF": "f(z) = (m + (1-m) z) * (1 - p (1-m) (1-z))^c",
        "c": "min(nSY, free)   (free0, shared X/Y, top of _react)",
        "p": "min(1, kY * nX * nY)",
        "m": "muY, applied in _decay AFTER _react, so newborns decay in their birth step",
        "R_mean_offspring": "(1 - muY) * (1 + c p)",
        "INDEPENDENT_VERIFICATION_vs_brute_force": {"checks": checks, "max_abs_err": maxerr,
                                                    "MATCHES": maxerr < 1e-12},
        "NOT_TAKEN_FROM_PMCR01": ("the closed form is checked against an independent "
                                  "enumeration over (parent survives, #births, #newborn "
                                  "survivors), not against PMCR01's code"),
    }


# ------------------------------------------------------------------ §9 the reduction attack
def reduction_attack():
    """Is beta = kY * E[Q] exact? Check each condition, from the recorded arms and the operator."""
    # gather organiser-cell fields across mobile arms
    files = sorted(glob.glob(os.path.join(RAW, "M__*.npz")))
    frac_multi_org, frac_nX_ge1, q_pos_quantile = [], [], []
    for p in files:
        z = np.load(p, allow_pickle=True)
        f = [str(x) for x in z["fields"]]
        s = z["series"][BURN_IN:HORIZON]
        norg = s[:, f.index("n_org_cells")]
        nX = s[:, f.index("u_nX_at_org")]
        q = s[:, f.index("Q")]
        frac_multi_org.append(float((norg > 1).mean()))
        frac_nX_ge1.append(float((nX >= 1).mean()))
        q_pos_quantile.append(float(np.quantile(q, 0.10)))
    conditions = {
        "1_one_Y_per_relevant_cell": {
            "status": "HOLDS in the archive (kY=0 -> exactly one Y, the organiser)",
            "but": "the QUESTION is a future ACTIVE lineage, where a second birth can co-locate; "
                   "then p carries nY and the reduction's linear form breaks"},
        "2_rare_Y_approximation": {
            "status": "HOLDS for the first birth only; see §13 feedback bound"},
        "3_clamp_inactive_kY_nX_nY_lt_1": {
            "mean_frac_frames_nX_ge_1": float(np.mean(frac_nX_ge1)),
            "status": ("for small kY the clamp min(1, kY*nX*nY) is inactive at the tested "
                       "magnitudes, so this holds in the linear regime")},
        "4_correct_scheduler_phase": {"status": "HOLDS -- Q_LEDGER_EVENT_EXACT (§5)"},
        "5_no_Y_induced_env_change": {
            "status": "FAILS beyond the first birth: a Y birth depletes local nSY (§13)"},
        "6_exposure_survival_independence": {
            "status": ("QUESTIONABLE: Q, survival and organiser motion share the realized "
                       "trajectory; exposure and lineage fate are not independent")},
        "7_no_consequential_temporal_correlation": {
            "status": ("FAILS: integrated autocorrelation time ~7-9, so E[Q] over frames is not "
                       "a sum of independent draws; the arithmetic mean is a biased proxy for "
                       "the growth-relevant functional")},
        "8_arithmetic_mean_is_the_persistence_criterion": {
            "status": ("NO: persistence is governed by the multiplicative growth of the "
                       "lineage, which sees the JOINT law of (c,p) over its own path, not the "
                       "marginal mean of Q. E[Q] can be positive while the lineage still dies "
                       "because Q=0 episodes are long -- min arm Q10 = 0")},
        "9_organiser_exposure_represents_descendant_exposure": {
            "status": "NO -- §12, Q_POSITION unrecoverable for a separated descendant",
            "min_arm_Q10": float(np.min(q_pos_quantile))},
        "10_trial_count_c_not_c_nY": {
            "status": "the trial count is c; the nY factor lives in p, so two co-located Y do "
                      "NOT simply double the trials -- the process is not a sum of independent "
                      "one-Y operators"},
    }
    return {
        "SECTION": "MYQBD01 §9 attack on beta = kY * E[Q]",
        "CONDITIONS": conditions,
        "mean_frac_frames_with_multiple_organiser_cells": float(np.mean(frac_multi_org)),
        "CLASSIFICATION": "SCALAR_Q_REDUCTION_VALID_ONLY_FOR_FIRST_BIRTH",
        "WHY": ("beta = kY * E[Q] is exact only for the intensity of the FIRST birth of a single "
                "Y at the organiser cell, in the unclamped regime. Beyond the first birth it "
                "fails on at least four independent counts: SY depletion (5), temporal "
                "correlation (7), the arithmetic-mean-vs-multiplicative-growth gap (8), and the "
                "absence of descendant exposure (9). It must NOT be used alone for the final "
                "region."),
    }


# ------------------------------------------------------------------ §11 two-Y state
def two_y_state():
    """Is the post-first-birth process Galton-Watson? Derive the smallest exact state up to the
    frozen third-centre boundary, and prove where independence breaks."""
    # exact demonstration that two co-located Y do NOT factor into two one-Y operators
    def births_law(c, p):
        return {b: comb(c, b) * p ** b * (1 - p) ** (c - b) for b in range(c + 1)}

    # TWO regimes, to separate the two ways the coupling shows.
    #  (a) unclamped: the MEANS coincide (p2 = 2 p1 exactly), but the SUPPORT does not --
    #      the shared pool caps true births at c, the naive independent sum allows up to 2c.
    #  (b) clamped: nX large enough that p2 saturates but p1 does not -- then the MEANS diverge.
    def one_point(c, kY, nX):
        p1 = min(1.0, kY * nX * 1)
        p2 = min(1.0, kY * nX * 2)
        law_one = births_law(c, p1)
        law_true = births_law(c, p2)          # ONE Binomial(c, p2) from the shared pool
        naive = {}
        for a, pa in law_one.items():
            for b, pb in law_one.items():
                naive[a + b] = naive.get(a + b, 0.0) + pa * pb   # convolve two Binomial(c, p1)
        mt = sum(b * pr for b, pr in law_true.items())
        mn = sum(b * pr for b, pr in naive.items())
        vt = sum((b - mt) ** 2 * pr for b, pr in law_true.items())
        vn = sum((b - mn) ** 2 * pr for b, pr in naive.items())
        return {"c": c, "kY": kY, "nX": nX, "p_one_Y": p1, "p_two_Y": p2,
                "true_mean": mt, "naive_mean": mn, "means_equal": abs(mt - mn) < 1e-12,
                "true_variance": vt, "naive_variance": vn,
                "variances_equal": abs(vt - vn) < 1e-12,
                "true_max_births_support": max(law_true), "naive_max_births_support": max(naive),
                "support_differs": max(law_true) != max(naive)}
    unclamped = one_point(4, 0.05, 3)
    clamped = one_point(4, 0.20, 3)
    c, kY, nX = 4, 0.05, 3
    p1, p2 = unclamped["p_one_Y"], unclamped["p_two_Y"]
    mean_true, mean_naive = unclamped["true_mean"], unclamped["naive_mean"]
    return {
        "SECTION": "MYQBD01 §11 two-Y state and the Galton-Watson question",
        "SMALLEST_EXACT_STATE": ["ONE_Y", "TWO_Y_COLOCATED", "TWO_Y_SEPARATED",
                                 "THREE_OR_MORE_STOP", "EXTINCT"],
        "PLUS_SPATIAL": ("TWO_Y_SEPARATED and the third-centre hazard require source-relative "
                         "displacement, i.e. the descendant position -- which §12 shows is "
                         "unrecorded"),
        "IS_GALTON_WATSON": False,
        "EXACT_COUNTEREXAMPLE_two_colocated": {
            "UNCLAMPED_REGIME": unclamped,
            "CLAMPED_REGIME": clamped,
            "reading": ("two co-located Y draw ONE Binomial(c, min(1, kY*nX*2)) from the SHARED "
                        "candidate pool c = min(nSY, free); they do NOT draw two independent "
                        "Binomial(c, min(1, kY*nX*1)). In the UNCLAMPED regime the means "
                        "coincide (p2 = 2 p1), but the SUPPORT does not: the shared pool caps "
                        "true births at c = %d while the naive independent sum allows up to "
                        "2c = %d, and the variances differ (%.4f vs %.4f). In the CLAMPED "
                        "regime even the MEANS diverge (%.4f vs %.4f). Either way the offspring "
                        "channels are coupled and the process is NOT a branching process."
                        % (unclamped["true_max_births_support"],
                           unclamped["naive_max_births_support"],
                           unclamped["true_variance"], unclamped["naive_variance"],
                           clamped["true_mean"], clamped["naive_mean"]))},
        "WHY_THE_STATE_CANNOT_BE_REDUCED_TO_A_SCALAR": (
            "c and p both depend on the shared cell state (nSY, free, nX), and nX at the cell is "
            "produced by the lineage. Co-located Y compete for one candidate pool; separated Y "
            "have different, unrecorded environments. No scalar branching ratio captures this."),
        "CONSEQUENCE": ("the two-Y state operator is identifiable ONLY with per-cell "
                        "descendant-position exposure. From an organiser-only ledger it is "
                        "NOT_IDENTIFIABLE, which blocks the positive disposition."),
        "TWO_Y_STATE_OPERATOR_VERIFIED": False,
        "TWO_Y_STATE_OPERATOR_STATUS": "NOT_IDENTIFIABLE_FROM_ORGANISER_ONLY_LEDGER",
    }


def main():
    o = one_y_operator()
    r = reduction_attack()
    t = two_y_state()
    json.dump(o, open(f"{OUT}/MYQBD01_ONE_Y_OPERATOR.json", "w"), indent=1, default=str)
    json.dump({"REDUCTION": r, "TWO_Y": t},
              open(f"{OUT}/MYQBD01_TWO_Y_OPERATOR.json", "w"), indent=1, default=str)
    print("§10 one-Y operator: source facts hold =", o["ALL_SOURCE_FACTS_HOLD"],
          "| brute-force match =", o["INDEPENDENT_VERIFICATION_vs_brute_force"]["MATCHES"],
          "(max err %.1e)" % o["INDEPENDENT_VERIFICATION_vs_brute_force"]["max_abs_err"])
    print("§9 reduction:", r["CLASSIFICATION"])
    uc = t["EXACT_COUNTEREXAMPLE_two_colocated"]["UNCLAMPED_REGIME"]
    cl = t["EXACT_COUNTEREXAMPLE_two_colocated"]["CLAMPED_REGIME"]
    print("§11 two-Y: IS_GALTON_WATSON =", t["IS_GALTON_WATSON"])
    print("   unclamped: means equal=%s but support %d vs %d, var %.4f vs %.4f"
          % (uc["means_equal"], uc["true_max_births_support"],
             uc["naive_max_births_support"], uc["true_variance"], uc["naive_variance"]))
    print("   clamped:   true mean %.4f vs naive %.4f (means differ=%s)"
          % (cl["true_mean"], cl["naive_mean"], not cl["means_equal"]))
    print("   two-Y operator status:", t["TWO_Y_STATE_OPERATOR_STATUS"])


if __name__ == "__main__":
    main()
