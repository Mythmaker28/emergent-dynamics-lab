"""MYQBD01 FINAL REPAIR — operator and feedback certificates A5, A6, A7, A8.

Runs under the final-repair runtime guard. Exact arithmetic over already-committed arrays and
the committed engine source. No engine execution.
"""
from __future__ import annotations

import glob
import json
import math
import os
import subprocess
import sys
from math import comb

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myqbd01_repair_guard as GUARD                                          # noqa: E402
GUARD.install()

RAW = "/home/claude/OBFOR01/raw"
OUT = "/home/claude/edl/MYQBD01/out"
REPO = "/home/claude/edl"
BURN_IN, HORIZON = 2000, 11000
KY_ADM = 4e-5                       # the first-birth discovery scale
MUY_ADM = 1.9511206603301160e-06    # inherited MTW01 scale


def arms(pat):
    for p in sorted(glob.glob(os.path.join(RAW, pat))):
        z = np.load(p, allow_pickle=True)
        f = [str(x) for x in z["fields"]]
        yield os.path.basename(p)[:-4], f, z["series"][BURN_IN:HORIZON]


def col(f, s, name):
    return s[:, f.index(name)].astype(float)


# ============================ A5 — scalar reduction scope ================================
def repair_a5():
    clamp_steps, total_steps, nx_max, quench, scalar = 0, 0, 0.0, [], []
    for a, f, s in arms("M__*.npz"):
        nX, q, cy = col(f, s, "u_nX_at_org"), col(f, s, "Q"), col(f, s, "cand_Y_at_org")
        p = KY_ADM * nX * 1.0
        clamp_steps += int((p >= 1.0).sum())
        total_steps += p.size
        nx_max = max(nx_max, float(nX.max()))
        # quenched (path-wise) growth exponent, exact per step
        R_t = (1 - MUY_ADM) * (1 + cy * np.minimum(1.0, p))
        quench.append(float(np.mean(np.log(R_t))))
        scalar.append(float(KY_ADM * q.mean() - MUY_ADM))
    qm, sm = float(np.mean(quench)), float(np.mean(scalar))
    rel = (qm - sm) / sm
    nx_needed = 1.0 / KY_ADM
    return {
        "SECTION": "MYQBD01 REPAIR A5 — scope of beta = kY * E[Q]",
        "CLAMP_CHECK": {
            "steps_examined": total_steps, "clamp_active_steps": clamp_steps,
            "max_nX_at_org_observed": nx_max,
            "nX_required_to_clamp_at_kY_4e-5": nx_needed,
            "headroom_factor": nx_needed / max(nx_max, 1e-12),
            "CLAMP_NEVER_ACTIVE": clamp_steps == 0,
            "reading": ("p = min(1, kY*nX*nY) clamps only at nX >= %.0f. The largest organiser "
                        "nX observed anywhere in the mobile branch is %.0f, a factor %.0f below "
                        "that. The reduction is therefore in the strictly unclamped regime."
                        % (nx_needed, nx_max, nx_needed / max(nx_max, 1e-12)))},
        "CONDITIONS_7_AND_8_MAGNITUDE": {
            "what_they_claimed": ("that temporal correlation (7) and the arithmetic-mean vs "
                                  "multiplicative-growth gap (8) invalidate the scalar "
                                  "reduction"),
            "quenched_growth_exponent_mean_t_log_R_t": qm,
            "scalar_reduction_kY_EQ_minus_muY": sm,
            "absolute_gap": qm - sm, "relative_gap": rel,
            "reviewer_reported_relative_gap": 2.05e-4,
            "REPRODUCED": abs(abs(rel) - 2.05e-4) < 5e-6,
            "CORRECTION": ("the effect is ~2e-4 RELATIVE at the admissible scale -- four orders "
                           "below the quantities it was said to invalidate. Calling conditions "
                           "7 and 8 grounds for insufficiency was over-pessimistic. They are "
                           "recorded with their magnitude and no longer carry the "
                           "classification.")},
        "SCALAR_Q_REDUCTION_STATUS":
            "EXACT_FOR_FIRST_BIRTH_IN_ONE_Y_UNCLAMPED_REGIME__"
            "INSUFFICIENT_FOR_COMPLETE_TWO_Y_SPATIAL_WINDOW",
        "WHAT_THE_INSUFFICIENCY_NOW_RESTS_ON": [
            "missing descendant-position exposure Q_POSITION(x,t) (A4)",
            "the shared-pool two-Y structure, which is not a sum of independent one-Y laws (A6)",
            "SY feedback uncontrolled beyond the first birth (A7)",
            "the absence of any two-Y environment ledger in the archives"],
        "WHAT_IT_NO_LONGER_RESTS_ON": [
            "exaggerated first-birth approximation error from temporal correlation (~2e-4)",
            "the arithmetic-mean vs multiplicative-growth gap at admissible kY (~2e-4)"],
    }


# ============================ A6 — two-Y law over the admissible domain ==================
def _binom_pmf(n, p):
    return np.array([comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)])


def _two_y_point(c, kY, nX):
    """Exact executable law (shared pool) vs the naive sum of two independent one-Y laws."""
    p2 = min(1.0, kY * nX * 2)            # the engine draws ONE binomial with nY = 2
    p1 = min(1.0, kY * nX * 1)
    shared = _binom_pmf(c, p2)            # support 0..c
    one = _binom_pmf(c, p1)
    naive = np.convolve(one, one)         # support 0..2c
    ks, kn = np.arange(c + 1), np.arange(2 * c + 1)
    m_s, m_n = float((ks * shared).sum()), float((kn * naive).sum())
    v_s = float((ks ** 2 * shared).sum() - m_s ** 2)
    v_n = float((kn ** 2 * naive).sum() - m_n ** 2)
    pad = np.concatenate([shared, np.zeros(c)])
    tv = 0.5 * float(np.abs(pad - naive).sum())
    excess = float(naive[c + 1:].sum())   # mass the naive law puts on IMPOSSIBLE outcomes
    return {"c": c, "kY": kY, "nX": nX, "p_one_Y": p1, "p_two_Y": p2,
            "clamp_active": bool(kY * nX * 2 >= 1.0),
            "support_shared": [0, c], "support_naive": [0, 2 * c],
            "mean_shared": m_s, "mean_naive": m_n,
            "mean_absolute_gap": m_s - m_n,
            "mean_relative_gap": (m_s - m_n) / m_n if m_n else 0.0,
            "variance_shared": v_s, "variance_naive": v_n,
            "variance_relative_gap": (v_s - v_n) / v_n if v_n else 0.0,
            "total_variation_distance": tv,
            "P_naive_puts_mass_on_impossible_outcomes": excess}


def repair_a6():
    cy, nx = [], []
    for a, f, s in arms("M__*.npz"):
        cy.append(col(f, s, "cand_Y_at_org").mean())
        nx.append(col(f, s, "u_nX_at_org").mean())
    cand_mean, nX_mean = float(np.mean(cy)), float(np.mean(nx))
    src = subprocess.run(("git", "show", "HEAD:OBTC02/code/engine_obtc.py"), cwd=REPO,
                         capture_output=True, text=True).stdout
    one_draw = "cand = np.minimum(self.n[res], free0)" in src and \
               "births = rng.binomial(np.maximum(cand, 0), p)" in src

    admissible = [_two_y_point(c, KY_ADM, nX) for c in (1, 2, 3, 7)
                  for nX in (4, round(nX_mean, 6))]
    demo = [_two_y_point(3, 0.05, 4), _two_y_point(3, 0.20, 4)]
    a3 = _two_y_point(3, KY_ADM, 4)
    return {
        "SECTION": "MYQBD01 REPAIR A6 — two-Y law, evaluated over the ADMISSIBLE domain",
        "STRUCTURE_VERIFIED_AT_SOURCE": {
            "single_binomial_draw_from_a_shared_pool": one_draw,
            "evidence": ("engine_obtc._react_core draws ONE rng.binomial(min(nSY, free0), "
                         "min(1, kY*nX*nY)) per species per step. Two co-located Y raise nY to 2 "
                         "inside p; they do not each draw their own binomial."),
            "TWO_Y_SHARED_POOL_NONINDEPENDENT": True},
        "CORRECTION_F15": (
            "the pre-seal counterexample used kY = 0.05 and 0.20, i.e. 1250x and 5000x the "
            "admissible 4e-5. Those points are retained below ONLY as a structural illustration "
            "and are no longer offered as quantitative evidence about the frozen candidate "
            "region."),
        "ADMISSIBLE_DOMAIN_POINTS": admissible,
        "REPRESENTATIVE_ADMISSIBLE_POINT_c3_nX4": a3,
        "REVIEWER_NUMBERS_CHECK": {
            "variance_relative_gap_reported": -1.6e-4,
            "variance_relative_gap_computed": a3["variance_relative_gap"],
            "support_excess_probability_reported": 9.8e-15,
            "support_excess_probability_computed":
                a3["P_naive_puts_mass_on_impossible_outcomes"],
            "REPRODUCED": (abs(a3["variance_relative_gap"] + 1.6e-4) < 1e-5
                           and abs(a3["P_naive_puts_mass_on_impossible_outcomes"] - 9.8e-15)
                           < 5e-16)},
        "ILLUSTRATIVE_ONLY_ABOVE_SCALE_POINTS": demo,
        "MEASURED_MAGNITUDES": {"mean_cand_Y_at_org_mobile": cand_mean,
                                "mean_u_nX_at_org_mobile": nX_mean},
        "CONCLUSION":
            "MEAN_ONLY_EQUIVALENCE_TO_HIGH_ACCURACY_IN_UNCLAMPED_ADMISSIBLE_REGIME__"
            "BUT_EXACT_SUPPORT_AND_DEPENDENCE_ARE_NOT_GALTON_WATSON",
        "READING": (
            "in the unclamped admissible regime 2*p1 = p2 exactly, so the two laws share a mean "
            "to machine precision; they differ in variance by ~1.6e-4 relative and the naive "
            "independent sum puts ~1e-14 of its mass on outcomes the engine cannot produce. The "
            "non-independence is mathematically real and structurally decisive -- the process is "
            "not Galton-Watson, so no branching-process persistence theory applies -- but it is "
            "NOT numerically large at admissible rates, and the pre-seal presentation implied "
            "otherwise."),
        "WHY_THE_MISSING_DESCENDANT_ENVIRONMENT_REMAINS_LOAD_BEARING": (
            "the shared-pool correction is small ONLY while the two Y are CO-LOCATED and the "
            "pool is the organiser's. The moment a descendant separates, its exposure is a "
            "different cell's (nX, nSY, free) -- an unrecorded quantity, not a small correction "
            "to a recorded one. A6 being numerically benign therefore does not rescue the "
            "region: A4 does the load-bearing work, and A4 fails."),
    }


# ============================ A7 — feedback certificates ================================
def repair_a7():
    yaml_txt = subprocess.run(("git", "show", "HEAD:OBTC02/code/obtc02_protocol.yaml"), cwd=REPO,
                              capture_output=True, text=True).stdout
    pt, inb = {}, False
    for ln in yaml_txt.splitlines():
        if ln.startswith("point:"):
            inb = True
            continue
        if inb:
            if ln and not ln.startswith(" "):
                break
            if ":" in ln:
                k, v = ln.strip().split(":", 1)
                pt[k.strip()] = v.strip()
    S0, phi, kY_arch = int(pt["S0"]), float(pt["phi"]), float(pt["kY"])

    # --- three conditionings, mobile branch ---
    un, poss, real, cyc = [], [], [], []
    for a, f, s in arms("M__*.npz"):
        nsy, cy = col(f, s, "nSY_at_org"), col(f, s, "cand_Y_at_org")
        un.append(nsy.mean())
        m = cy >= 1
        poss.append(nsy[m].mean())
        cyc.append(cy[m].mean())
        # birth-realised weighting: P(>=1 birth) = 1-(1-p)^cand, exact, at admissible kY
        nX = col(f, s, "u_nX_at_org")
        p = np.minimum(1.0, KY_ADM * nX)
        w = 1.0 - (1.0 - p) ** cy
        real.append(float((nsy * w).sum() / w.sum()) if w.sum() > 0 else float("nan"))
    U, P, R_, C = (float(np.mean(x)) for x in (un, poss, real, cyc))

    # --- effective SY mean reversion, measured on the STATIC arms (fixed organiser cell) ---
    slopes, ac1 = [], []
    for a, f, s in arms("S__*.npz"):
        y = col(f, s, "nSY_at_org")
        d, x = np.diff(y), (S0 - y[:-1])
        slopes.append(float(np.dot(x - x.mean(), d - d.mean())
                            / np.dot(x - x.mean(), x - x.mean())))
        ac1.append(float(np.corrcoef(y[:-1], y[1:])[0, 1]))
    rate, sd = float(np.mean(slopes)), float(np.std(slopes, ddof=1))

    return {
        "SECTION": "MYQBD01 REPAIR A7 — feedback certificates, regenerated",
        "ARCHIVE_PARAMETERS_FROM_THE_LOADED_SPEC": {"S0": S0, "phi": phi, "kY": kY_arch,
                                                    "source": "obtc02_protocol.yaml point block"},
        "SY_MEAN_REVERSION": {
            "NOMINAL_EXCHANGE_PHI": phi,
            "MEASURED_EFFECTIVE_RATE": rate, "SD_OVER_14_STATIC_ARMS": sd,
            "RATIO_MEASURED_OVER_NOMINAL": rate / phi,
            "per_arm_slopes": slopes, "lag1_autocorr_per_arm": ac1,
            "reviewer_reported": {"value": 0.355735, "sd": 0.013473, "ratio": 1.78},
            "REPRODUCED": abs(rate - 0.355735) < 5e-5,
            "WHY_THEY_DIFFER": (
                "phi = %.2f is the rate at which _exchange OFFERS a refill toward S0 = %d, i.e. "
                "the parameter of Binomial(max(S0 - nSY, 0), phi). The observed relaxation of "
                "nSY at a cell is not that offer alone: the cell ALSO receives SY by diffusion "
                "from its neighbours and loses SY to the hypergeometric removal that _exchange "
                "applies across {SX, SY, WX, WY}. The measured effective mean reversion is the "
                "NET of all three channels, and it is %.2fx the offer rate. Substituting phi "
                "for it -- as the pre-seal certificate did -- understates how fast the "
                "perturbation is erased." % (phi, S0, rate / phi)),
            "DIRECTION_OF_THE_ERROR": "CONSERVATIVE: recovery is faster than was certified, so "
                                      "the true first-birth perturbation is SMALLER"},
        "DEPLETION_BY_ONE_Y_BIRTH": {
            "delta_nSY_local": -1,
            "UNCONDITIONAL_MEAN_DEPLETION": {
                "mean_nSY_at_org": U, "depletion_fraction": 1.0 / U,
                "status": "SUPERSEDED as the headline figure: it divides by an average that "
                          "includes steps where no birth is possible at all"},
            "CONDITIONAL_ON_BIRTH_POSSIBLE_DEPLETION": {
                "conditioning_event": "cand_Y = min(nSY, free) >= 1",
                "mean_nSY_given_event": P, "mean_cand_Y_given_event": C,
                "depletion_fraction": 1.0 / P,
                "reviewer_reported_pct": 55.1, "computed_pct": 100.0 / P,
                "REPRODUCED": abs(100.0 / P - 55.1) < 0.2,
                "status": "THE HEADLINE FIGURE"},
            "CONDITIONAL_ON_BIRTH_REALIZED_DEPLETION": {
                "weighting": "P(at least one Y birth at the cell) = 1 - (1-p)^cand_Y, exact at "
                             "kY = %.0e" % KY_ADM,
                "mean_nSY_given_realized": R_, "depletion_fraction": 1.0 / R_,
                "computed_pct": 100.0 / R_,
                "note": ("identifiable only as an exposure-weighted conditional: kY = 0 in the "
                         "archives, so no birth was ever realised and this cannot be measured "
                         "directly. It is reported as a derived weighting, not as an "
                         "observation.")},
            "steps_to_erase_one_unit_at_the_measured_rate": 1.0 / rate},
        "DOWNSTREAM_BOUND": {
            "FIRST_BIRTH": ("controlled: the perturbation is -1 SY against a conditional pool of "
                            "%.6f (%.1f%%), erased at %.6f per step (~%.1f steps)."
                            % (P, 100.0 / P, rate, 1.0 / rate)),
            "SECOND_BIRTH_AND_BEYOND": ("NOT controlled: the archives carry kY = 0, so no "
                                        "sequence of births was ever observed and the compounding "
                                        "of depletion across a persisting lineage cannot be "
                                        "bounded from them."),
            "TWO_Y_COLOCATED": "not controlled: the pool is shared and depletes twice as fast",
            "TWO_Y_SEPARATED": ("not boundable at all: the descendant's cell exposure is "
                                "unrecorded (A4)"),
            "STATUS": "FROZEN_ENVIRONMENT_FEEDBACK_NOT_FULLY_CONTROLLED",
            "WHAT_THIS_SUPPORTS": "prospective calibration",
            "WHAT_THIS_DOES_NOT_PROVE": "structural preclusion"},
    }


# ============================ A8 — non-preclusion witnesses =============================
def _survival(c, p, m, T=HORIZON):
    """Survival probability after exactly T steps, iterating from s = 1."""
    s = 1.0
    for _ in range(T):
        s = -math.expm1(math.log1p(-(1 - m) * s) + c * math.log1p(-p * (1 - m) * s))
    return s


def _extinction_fixed_point(c, p, m, iters=2_000_000, tol=1e-18):
    """The ASYMPTOTIC extinction root eta* = f(eta*), f(z) = (m+(1-m)z)(1-p(1-m)(1-z))^c.

    This is a different quantity from the T-step survival above: eta* is the limit, the T-step
    value is where the iteration has got to after T steps. Reporting one as the other would be
    a category error, so both are published."""
    eta = 0.0
    for _ in range(iters):
        nxt = (m + (1 - m) * eta) * (1 - p * (1 - m) * (1 - eta)) ** c
        if abs(nxt - eta) < tol:
            eta = nxt
            break
        eta = nxt
    return eta


def repair_a8():
    q, cy, nx = [], [], []
    for a, f, s in arms("M__*.npz"):
        q.append(col(f, s, "Q").mean())
        cy.append(col(f, s, "cand_Y_at_org").mean())
        nx.append(col(f, s, "u_nX_at_org").mean())
    Q, C, X = float(np.mean(q)), float(np.mean(cy)), float(np.mean(nx))

    # representative diagnostic: R from the arms' OWN measured mean exposure
    R_rep = (1 - MUY_ADM) * (1 + KY_ADM * Q)
    margin = (R_rep - 1.0) / MUY_ADM
    # favourable in-box witness (atypical): c = 3, nX = 4 -> exposure 12
    p_fav = min(1.0, KY_ADM * 4)
    R_fav = (1 - MUY_ADM) * (1 + 3 * p_fav)
    surv_fav_T = _survival(3, p_fav, MUY_ADM)
    eta_fav = _extinction_fixed_point(3, p_fav, MUY_ADM)
    return {
        "SECTION": "MYQBD01 REPAIR A8 — non-preclusion witnesses, labelled by typicality",
        "LOGICAL_USE": "STRUCTURAL_PRECLUSION_NOT_PROVED. Nothing here qualifies a prospective "
                       "window.",
        "CLASSIFICATION_OF_BOTH_WITNESSES": "POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC",
        "REPRESENTATIVE_WITNESS": {
            "basis": "the 14 mobile arms' OWN measured mean exposure E[Q]",
            "mean_Q": Q, "kY": KY_ADM, "muY": MUY_ADM,
            "R_mean_offspring": R_rep, "R_minus_1": R_rep - 1.0,
            "margin_over_muY": margin,
            "supercritical": R_rep > 1.0,
            "reviewer_reported_R": 1.000124838,
            "REPRODUCED": abs(R_rep - 1.000124838) < 5e-9,
            "launcher_said_approximately_65x_margin": 65.0,
            "exact_margin_computed": margin,
            "NOTE": ("the launcher quoted the margin as approximately 65x; the exact value is "
                     "%.2fx. The approximation is reported rather than silently adopted."
                     % margin),
            "reading": ("at the arms' own measured exposure the one-Y lineage is supercritical "
                        "with a margin of %.1fx muY. This is the number that should carry the "
                        "non-preclusion conclusion, because it uses no inflated magnitude."
                        % margin)},
        "FAVOURABLE_WITNESS_ATYPICAL": {
            "c": 3, "nX": 4, "exposure_c_times_nX": 12,
            "R_mean_offspring": R_fav,
            "extinction_fixed_point_eta_star": eta_fav,
            "asymptotic_survival_1_minus_eta_star": 1.0 - eta_fav,
            "survival_after_exactly_T_steps": surv_fav_T,
            "T": HORIZON,
            "NOTE_TWO_DISTINCT_QUANTITIES": (
                "eta* is the ASYMPTOTIC extinction root of f(eta) = eta; the T-step value is "
                "where the iteration stands after %d steps, still above the limit because the "
                "process is only barely supercritical. Both are published so neither can be "
                "mistaken for the other." % HORIZON),
            "reviewer_reported_R": 1.000478048,
            "reviewer_reported_eta_star": 0.004063547247,
            "REPRODUCED_R": abs(R_fav - 1.000478048) < 5e-9,
            "REPRODUCED_ETA": abs(eta_fav - 0.004063547247) < 5e-10,
            "ATYPICALITY": {
                "measured_mean_cand_Y_at_org": C, "c_over_measured_pool": 3.0 / C,
                "measured_mean_Q": Q, "exposure_over_measured_Q": 12.0 / Q,
                "measured_mean_nX_at_org": X, "nX_used_over_measured": 4.0 / X},
            "LABEL": ("EXPLICITLY FAVOURABLE, NOT REPRESENTATIVE: its candidate pool is %.2fx "
                      "and its exposure %.2fx the measured means. Retained only to show the "
                      "operator admits a supercritical point at admissible (kY, muY); the "
                      "pre-seal framing 'the MOST FAVOURABLE admissible environment (Q sustained "
                      "at Q_MAX)' was wrong on its own terms, since Q_MAX = 28 and this witness "
                      "uses 12." % (3.0 / C, 12.0 / Q))},
        "STRUCTURAL_PRECLUSION_PROVED": False,
        "WHY_NOT": ("both witnesses are supercritical at admissible (kY, muY), and the "
                    "representative one uses only measured magnitudes. The obstruction to a "
                    "window is a MISSING LEDGER, which is not a proof of impossibility."),
    }


def main():
    a5, a6, a7, a8 = repair_a5(), repair_a6(), repair_a7(), repair_a8()
    json.dump({"A5_SCALAR_REDUCTION": a5, "A6_TWO_Y": a6},
              open(f"{OUT}/MYQBD01_TWO_Y_OPERATOR.json", "w"), indent=1, default=str)
    json.dump({"A7_FEEDBACK": a7, "A8_NON_PRECLUSION": a8},
              open(f"{OUT}/MYQBD01_FEEDBACK_BOUND.json", "w"), indent=1, default=str)
    print("A5 clamp active steps %d / %d (never: %s); conditions 7-8 relative gap %.6e "
          "(reviewer 2.05e-4 reproduced: %s)"
          % (a5["CLAMP_CHECK"]["clamp_active_steps"], a5["CLAMP_CHECK"]["steps_examined"],
             a5["CLAMP_CHECK"]["CLAMP_NEVER_ACTIVE"],
             a5["CONDITIONS_7_AND_8_MAGNITUDE"]["relative_gap"],
             a5["CONDITIONS_7_AND_8_MAGNITUDE"]["REPRODUCED"]))
    r = a6["REPRESENTATIVE_ADMISSIBLE_POINT_c3_nX4"]
    print("A6 admissible c=3,nX=4: mean gap %.3e, var gap %.6e, TV %.3e, impossible-mass %.4e "
          "(reviewer reproduced: %s)"
          % (r["mean_relative_gap"], r["variance_relative_gap"],
             r["total_variation_distance"], r["P_naive_puts_mass_on_impossible_outcomes"],
             a6["REVIEWER_NUMBERS_CHECK"]["REPRODUCED"]))
    m = a7["SY_MEAN_REVERSION"]
    d = a7["DEPLETION_BY_ONE_Y_BIRTH"]
    print("A7 phi %.2f -> measured %.6f +- %.6f (ratio %.3f, reproduced: %s)"
          % (m["NOMINAL_EXCHANGE_PHI"], m["MEASURED_EFFECTIVE_RATE"],
             m["SD_OVER_14_STATIC_ARMS"], m["RATIO_MEASURED_OVER_NOMINAL"], m["REPRODUCED"]))
    print("   depletion: uncond %.2f%% | birth-possible %.2f%% | birth-realised %.2f%%"
          % (100 * d["UNCONDITIONAL_MEAN_DEPLETION"]["depletion_fraction"],
             d["CONDITIONAL_ON_BIRTH_POSSIBLE_DEPLETION"]["computed_pct"],
             d["CONDITIONAL_ON_BIRTH_REALIZED_DEPLETION"]["computed_pct"]))
    print("A8 representative R %.9f (margin %.2fx muY, reproduced: %s) | favourable R %.9f "
          "eta* %.12f (reproduced: %s/%s)"
          % (a8["REPRESENTATIVE_WITNESS"]["R_mean_offspring"],
             a8["REPRESENTATIVE_WITNESS"]["margin_over_muY"],
             a8["REPRESENTATIVE_WITNESS"]["REPRODUCED"],
             a8["FAVOURABLE_WITNESS_ATYPICAL"]["R_mean_offspring"],
             a8["FAVOURABLE_WITNESS_ATYPICAL"]["extinction_fixed_point_eta_star"],
             a8["FAVOURABLE_WITNESS_ATYPICAL"]["REPRODUCED_R"],
             a8["FAVOURABLE_WITNESS_ATYPICAL"]["REPRODUCED_ETA"]))
    print("GUARD", GUARD.report()["VERDICT"])


if __name__ == "__main__":
    main()
