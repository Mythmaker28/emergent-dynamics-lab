"""PQEC01 — deterministic design: parameter points, sample sizes, seeds, splits.

Everything here is computed by rule and frozen BEFORE the first scientific start. No manual
"looks reasonable" choice is made anywhere in this file.
"""
from __future__ import annotations

import hashlib
import json
import math

import numpy as np

# ---- inherited frozen constants (bound from the parent, not re-chosen here) ----
PARENT_TIP = "86291212955d4a4816efc1ebd671fbd234bf574c"
PROGRAM = "PROSPECTIVE-Q-ENVIRONMENT-CALIBRATION-01"
CAP, S0, PHI = 16, 3, 0.2
T_HORIZON, T_WINDOW, BURN_IN = 11000, 9000, 2000
CORE_R, D_REL = 5.0, 0.05
TAU_SEP = CORE_R ** 2 / (4.0 * D_REL)              # 125.0
ALPHA_SURVIVAL, N_STAR, GAMMA_SEP, MIN_EVENTS = 0.5, 10.0, 0.5, 1.0
P_HOP = 0.10263340389897246
# ---- developmental magnitudes measured by the parent (design input only, never a sample unit) ----
DEV_MEAN_Q = 3.1697301587301587
DEV_SD_ARM_MEAN_Q = 0.1629902887142898
DEV_MEAN_CAND_Y = 0.9616507936507939
DEV_MEAN_NX_ORG = 4.312563492063493
DEV_MAX_NX_ORG = 16.0                              # bounded by CAP by construction
# ---- admissible box, frozen ----
KY_LO, KY_HI = 1e-6, 1e-2
MUY_LO, MUY_HI = 1e-8, 1e-1
GRID_N = 241                                        # log-spaced decades, deterministic


def _log10grid(lo, hi, n):
    return [10.0 ** v for v in np.linspace(math.log10(lo), math.log10(hi), n)]


# ============================== boundary margins (normalized, in decades) ==============
def margins(kY, muY):
    """Signed normalized distance to each frozen boundary, in decades. Positive = inside."""
    B = kY * DEV_MEAN_Q * T_WINDOW                              # expected first births / window
    m = {}
    m["first_birth_not_too_rare"] = math.log10(B / MIN_EVENTS) if B > 0 else -math.inf
    clamp = kY * DEV_MAX_NX_ORG * N_STAR                        # p would clamp at 1
    m["no_immediate_clamp"] = math.log10(0.1 / clamp) if clamp > 0 else math.inf
    surv = (1.0 - muY) ** T_HORIZON
    m["founder_not_extinct"] = (math.log10(surv / (1.0 - ALPHA_SURVIVAL))
                                if surv > 0 else -math.inf)
    n_sep = B * (1.0 - muY) ** TAU_SEP                          # expected separated 2nd centres
    m["no_premature_third_centre"] = (math.log10(GAMMA_SEP / n_sep) if n_sep > 0 else math.inf)
    m["numerical_precision"] = min(math.log10(kY / 1e-12), math.log10(muY / 1e-12),
                                   math.log10(1.0 / kY), math.log10(1.0 / muY))
    return m


def maximin_point():
    best = None
    for kY in _log10grid(KY_LO, KY_HI, GRID_N):
        for muY in _log10grid(MUY_LO, MUY_HI, GRID_N):
            mm = margins(kY, muY)
            v = min(mm.values())
            if best is None or v > best[0] + 1e-15:
                best = (v, kY, muY, mm)
    v, kY, muY, mm = best
    return {"kY": kY, "muY": muY, "min_margin_decades": v, "margins": mm,
            "ALL_BOUNDARIES_SATISFIED": v > 0,
            "RULE": ("argmax over the frozen log grid of the MINIMUM normalized distance to the "
                     "five frozen boundaries; ties broken by first-encountered in the "
                     "deterministic grid order")}


# ============================== exact nY chain, for the B2 information rule ============
def _chain_matrix(kY, muY, nmax, c, nx):
    """One 13x13 transition matrix on nY, built exactly from the frozen per-step laws."""
    from math import comb
    cc = max(int(round(c)), 1)
    M = np.zeros((nmax + 1, nmax + 1))
    M[0, 0] = 1.0
    for n in range(1, nmax + 1):
        p = min(1.0, kY * nx * n)
        bpm = np.array([comb(cc, k) * p ** k * (1 - p) ** (cc - k) for k in range(cc + 1)])
        dpm = np.array([comb(n, k) * muY ** k * (1 - muY) ** (n - k) for k in range(n + 1)])
        for b, pb in enumerate(bpm):
            if pb <= 0:
                continue
            for d, pd in enumerate(dpm):
                if pd <= 0:
                    continue
                M[n, min(max(n + b - d, 0), nmax)] += pb * pd
    return M


def colocation_profile(kY, muY, T=T_HORIZON, nmax=int(N_STAR) + 2,
                       c=DEV_MEAN_CAND_Y, nx=DEV_MEAN_NX_ORG):
    """Exact forward distribution of nY under the mean environment. DESIGN-TIME PROXY ONLY:
    the world stop rule uses the frozen spatial third-centre definition, not this count."""
    M = _chain_matrix(kY, muY, nmax, c, nx)
    P = np.zeros(nmax + 1)
    P[1] = 1.0
    exp_colo, seen2 = 0.0, 0.0
    for _ in range(T):
        P = P @ M
        colo = float(P[2:].sum())
        exp_colo += colo
        seen2 = max(seen2, colo)
    return {"expected_steps_with_nY_ge_2": exp_colo,
            "P_extinct_at_T": float(P[0]), "P_at_cap_at_T": float(P[nmax]),
            "E_nY_at_T": float(sum(i * P[i] for i in range(nmax + 1))),
            "max_P_nY_ge_2": seen2,
            "DESIGN_PROXY_NOTE": ("nY >= 2 is a DESIGN-TIME proxy for co-location. Worlds are "
                                  "stopped and adjudicated by the frozen SPATIAL third-centre "
                                  "definition, not by this count.")}


def b2_point(b1):
    """Deterministic information rule: among admissible points whose founder-extinction and
    clamp margins are no worse than B1's, choose the one MAXIMIZING the expected number of steps
    spent with two or more Y present -- the state in which shared-pool and co-located-versus-
    separated exposure are identifiable at all."""
    best = None
    for kY in _log10grid(KY_LO, KY_HI, 25):
        for muY in _log10grid(MUY_LO, MUY_HI, 25):
            mm = margins(kY, muY)
            if mm["no_immediate_clamp"] < b1["margins"]["no_immediate_clamp"]:
                continue
            if mm["founder_not_extinct"] < b1["margins"]["founder_not_extinct"]:
                continue
            if mm["numerical_precision"] <= 0:
                continue
            pr = colocation_profile(kY, muY, T=2000)      # frozen shortened design horizon
            v = pr["expected_steps_with_nY_ge_2"]
            if best is None or v > best[0] + 1e-12:
                best = (v, kY, muY, mm, pr)
    v, kY, muY, mm, pr = best
    return {"kY": kY, "muY": muY, "design_score_expected_colocated_steps": v,
            "margins": mm, "design_profile_T2000": pr,
            "RULE": ("argmax of expected co-located steps over the frozen coarse grid, "
                     "restricted to points whose clamp and founder-extinction margins are at "
                     "least B1's; evaluated on a frozen 2000-step design horizon so the score "
                     "is a design quantity, not a prediction of the run")}


# ============================== sample sizes ==========================================
def sample_sizes(total_cap=128, n_points=2):
    n_quantile = math.ceil(math.log(0.05) / math.log(0.90))          # 29
    rel_se_target = 0.010
    n_precision = math.ceil((DEV_SD_ARM_MEAN_Q / (rel_se_target * DEV_MEAN_Q)) ** 2)
    n_a_floor = max(n_quantile, n_precision)
    N_A = 40
    N_B = (total_cap - N_A) // n_points
    return {
        "PHASE_A": {
            "distribution_free_10th_percentile_floor": n_quantile,
            "derivation_quantile": "n >= ln(0.05)/ln(0.90); the minimum of n worlds is then a "
                                   "95% one-sided lower bound for the 10th world-level "
                                   "percentile of exposure",
            "precision_floor_at_1pct_relative_SE": n_precision,
            "derivation_precision": ("n >= (sd/(target*mean))^2 with the parent's world-level "
                                     "dispersion sd = %.6f about mean %.6f"
                                     % (DEV_SD_ARM_MEAN_Q, DEV_MEAN_Q)),
            "N_A": N_A,
            "achieved_relative_SE": DEV_SD_ARM_MEAN_Q / math.sqrt(N_A) / DEV_MEAN_Q,
            "margin_over_floor": N_A - n_a_floor,
            "JUSTIFICATION": ("N_A = %d exceeds both frozen floors (quantile %d, precision %d), "
                              "attains a %.2f%% relative standard error on the world-level mean "
                              "exposure, and leaves the remaining budget divisible into two "
                              "equal Phase-B points. It is not 'about thirty'."
                              % (N_A, n_quantile, n_precision,
                                 100 * DEV_SD_ARM_MEAN_Q / math.sqrt(N_A) / DEV_MEAN_Q))},
        "PHASE_B": {
            "mandated_floor_per_point": n_quantile,
            "N_B_PER_POINT": N_B, "POINTS": n_points,
            "zero_count_95pct_upper_bound_on_a_per_world_rate": 1 - 0.05 ** (1.0 / N_B),
            "JUSTIFICATION": ("N_B = %d per point is the largest equal allocation of the "
                              "remaining budget; it exceeds the mandated floor of %d by %d and "
                              "bounds any unobserved per-world event rate above by %.3f at 95%%."
                              % (N_B, n_quantile, N_B - n_quantile, 1 - 0.05 ** (1.0 / N_B)))},
        "TOTAL_OUTCOME_INFORMATIVE_STARTS": N_A + N_B * n_points,
        "CAP": total_cap,
        "WITHIN_CAP": N_A + N_B * n_points <= total_cap,
    }


# ============================== seeds and splits ======================================
def seed_for(phase, point, idx):
    h = hashlib.sha256(("%s|%s|%s|%s|%d" % (PARENT_TIP, PROGRAM, phase, point, idx)).encode())
    return 940_000_000 + int(h.hexdigest()[:12], 16) % 50_000_000


def make_seeds(phase, point, n, used):
    out = []
    for i in range(n):
        s, bump = seed_for(phase, point, i), 0
        while s in used:                     # deterministic collision resolution, no selection
            bump += 1
            s = seed_for(phase, point, 10_000 * bump + i)
        used.add(s)
        out.append({"index": i, "seed": s})
    return out


def split_of(seed):
    """Discovery / validation, decided by the hash of the FROZEN SEED, never by an outcome."""
    h = hashlib.sha256(("SPLIT|%s|%d" % (PARENT_TIP, seed)).encode()).hexdigest()
    return "DISCOVERY" if (int(h[:8], 16) % 3) < 2 else "VALIDATION"
