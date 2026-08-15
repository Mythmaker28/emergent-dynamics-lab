"""PMCR01 §7-§8 — the three nested regions, and the independence / identifiability gates.

Region A  ABSTRACT_Y_INTERVAL        symbolic inequalities, code reachability ignored
Region B  EXECUTABLE_Y_INTERVAL      restricted to what the scheduler can realise
Region C  ROBUST_REACHABLE_Y_REGION  category-A inputs only, all seven conditions

Everything is exact arithmetic on the frozen point. Extinction is not estimated: it is the
T-fold iterate of the offspring pgf, f^{(T)}(0), computed to machine precision.
"""
from __future__ import annotations

import json
import math

import numpy as np

OUT = "/home/claude/PMCR01/out"

# ---- category-A constants, all read from the frozen manifest or derived from the exact kernel
CAP = 16
Q_MAX = 28                      # exhaustively enumerated in pmcr01_operator.admissible_Q
Q_INF = 0                       # infimum over the admissible set
T_HORIZON = 11000
T_WINDOW = 9000
D_REL = 0.05                    # 2 * q(1-q), q = p_hop/4
CORE_R = 5.0
TAU_SEP = CORE_R ** 2 / (4.0 * D_REL)          # 125.0 steps to separate by one core radius

# generous thresholds, chosen to FAVOUR finding a window
ALPHA_SURVIVAL = 0.5            # the lineage must be present at T with probability >= 1/2
N_STAR = 10.0                   # Y may reach ten and still be a numerical minority of N_X ~ 117
GAMMA_SEP = 0.5                 # at most half an expected separated second centre
MIN_EVENTS = 1.0                # a control that fires less than once per horizon is a formality


def pgf(z, c, p, m):
    return (m + (1.0 - m) * z) * ((1.0 - p * (1.0 - m) * (1.0 - z)) ** c)


def extinction_by(T, c, p, m):
    """f^{(T)}(0), exactly. Iterating a scalar map is not a simulation."""
    q = 0.0
    for _ in range(T):
        q = pgf(q, c, p, m)
    return q


def evaluate(beta, m, c, T=T_HORIZON, tau=TAU_SEP):
    """beta = c*p is the per-step mean number of Y births from one Y."""
    p = beta / c
    if p > 1.0:
        return None
    R = (1.0 - m) * (1.0 + beta)
    eps = R - 1.0
    # sum_{t<T} R^t and R^T, guarded against float overflow. Anything that overflows is
    # astronomically dominating and fails C2 by many orders of magnitude; INF records that
    # honestly instead of crashing.
    log_pow = T * math.log(R) if R > 0 else -math.inf
    if log_pow > 300 * math.log(10):
        nT, cum = math.inf, math.inf
    elif abs(R - 1.0) < 1e-15:
        nT, cum = 1.0, float(T)
    else:
        nT = math.exp(log_pow)
        cum = (nT - 1.0) / (R - 1.0)
    births = beta * cum
    deaths = m * cum
    n_sep = births * (1.0 - m) ** tau
    surv = 1.0 - extinction_by(T, c, p, m)
    return {"beta": beta, "muY": m, "c": c, "p": p, "R": R, "epsilon": eps,
            "E_nY_at_T": nT, "E_births": births, "E_deaths": deaths,
            "E_separated_second_centres": n_sep, "survival_to_T": surv,
            "C1_SURVIVES": surv >= 1.0 - ALPHA_SURVIVAL,
            "C2_BOUNDED_MINORITY": nT <= N_STAR,
            "C3_SINGLE_SOURCE": n_sep <= GAMMA_SEP,
            "C4_BIRTH_CONTROL_ACTIVE": births >= MIN_EVENTS,
            "C5_DEATH_CONTROL_ACTIVE": deaths >= MIN_EVENTS,
            "C6_ADMISSIBLE": 0.0 < m < 1.0 and beta > 0.0 and p <= 1.0}


def scan(c):
    betas = np.concatenate([np.logspace(-8, 0, 161)])
    mus = np.concatenate([np.logspace(-8, -0.05, 159)])
    inside, best = [], None
    counts = {k: 0 for k in ("C1_SURVIVES", "C2_BOUNDED_MINORITY", "C3_SINGLE_SOURCE",
                             "C4_BIRTH_CONTROL_ACTIVE", "C5_DEATH_CONTROL_ACTIVE",
                             "C6_ADMISSIBLE")}
    n = 0
    for b in betas:
        for m in mus:
            r = evaluate(float(b), float(m), c)
            if r is None:
                continue
            n += 1
            for k in counts:
                counts[k] += int(r[k])
            ok = all(r[k] for k in counts)
            if ok:
                inside.append(r)
            if best is None or sum(r[k] for k in counts) > best["n_satisfied"]:
                best = {**r, "n_satisfied": sum(r[k] for k in counts)}
    return {"c": c, "grid_points": n, "n_inside": len(inside),
            "per_condition_satisfied": counts,
            "REGION_NONEMPTY": len(inside) > 0,
            "best_point_found": best,
            "examples_inside": inside[:5]}


def pairwise_frontier(c):
    """Which conditions are jointly satisfiable, pair by pair, and which pair is fatal."""
    keys = ("C1_SURVIVES", "C2_BOUNDED_MINORITY", "C3_SINGLE_SOURCE",
            "C4_BIRTH_CONTROL_ACTIVE", "C5_DEATH_CONTROL_ACTIVE")
    betas = np.logspace(-8, 0, 121)
    mus = np.logspace(-8, -0.05, 119)
    pts = [evaluate(float(b), float(m), c) for b in betas for m in mus]
    pts = [r for r in pts if r is not None and r["C6_ADMISSIBLE"]]
    out = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k1, k2 = keys[i], keys[j]
            out["%s & %s" % (k1, k2)] = sum(1 for r in pts if r[k1] and r[k2])
    triples = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            for k in range(j + 1, len(keys)):
                t = (keys[i], keys[j], keys[k])
                triples[" & ".join(t)] = sum(1 for r in pts if all(r[x] for x in t))
    return {"pairs": out, "triples": {k: v for k, v in triples.items() if v == 0},
            "n_points": len(pts)}


def closed_form_bound():
    """The frontier without any grid, from three of the conditions.

        C5 (death active)    m * S >= 1                     S = sum_t E[nY(t)]
        C3 (single source)   beta * S * (1-m)^tau <= gamma
        supercritical        beta > m/(1-m) > m,  so beta/m > 1

        dividing C3 by C5:   (beta/m) (1-m)^tau <= gamma   =>   (1-m)^tau <= gamma
                             =>  m >= 1 - gamma^(1/tau)

        C2 (bounded)         R^T <= N*   =>   eps = R - 1 <= ln(N*)/T

        near-critical survival from one founder (Kolmogorov):
                             survival ~ 2 eps / sigma^2,  sigma^2 ~ beta + m ~ 2m
                             =>  survival <~ eps / m  <=  [ln(N*)/T] / [1 - gamma^(1/tau)]
    """
    m_min = 1.0 - GAMMA_SEP ** (1.0 / TAU_SEP)
    eps_max = math.log(N_STAR) / T_HORIZON
    surv_max = eps_max / m_min
    return {
        "muY_lower_bound_forced_by_C3_and_C5": m_min,
        "epsilon_upper_bound_forced_by_C2": eps_max,
        "SURVIVAL_CEILING": surv_max,
        "REQUIRED_BY_C1": 1.0 - ALPHA_SURVIVAL,
        "C1_CAN_BE_MET": surv_max >= 1.0 - ALPHA_SURVIVAL,
        "APPROXIMATE_FORM": "survival <= ln(N*) * tau_sep / (T * ln(1/gamma))",
        "approximate_value": math.log(N_STAR) * TAU_SEP / (T_HORIZON * math.log(1 / GAMMA_SEP)),
        "READING": ("the same muY has to be LARGE, so that a newborn dies before it can "
                    "separate into a second source, and SMALL, so that the lineage itself "
                    "survives the horizon. There is one muY. The ceiling is set by the ratio "
                    "of the separation time to the horizon and does not depend on kY at all."),
    }


def region_without_activity_conditions(c=4):
    """If C4 and C5 are dropped -- if the two controls are not required to fire even once in
    the horizon -- what is left? This is the inherited warning 'a structural zero is not a
    small number', made quantitative."""
    betas = np.logspace(-8, 0, 161)
    mus = np.logspace(-8, -0.05, 159)
    inside = []
    for b in betas:
        for m in mus:
            r = evaluate(float(b), float(m), c)
            if r is None or not r["C6_ADMISSIBLE"]:
                continue
            if r["C1_SURVIVES"] and r["C2_BOUNDED_MINORITY"] and r["C3_SINGLE_SOURCE"]:
                inside.append(r)
    if not inside:
        return {"NONEMPTY": False}
    bmax = max(r["beta"] for r in inside)
    mmax = max(r["muY"] for r in inside)
    ev = max(r["E_births"] for r in inside)
    dv = max(r["E_deaths"] for r in inside)
    return {
        "NONEMPTY": True, "n_points": len(inside),
        "max_beta_inside": bmax, "max_muY_inside": mmax,
        "max_expected_births_over_the_whole_horizon": ev,
        "max_expected_deaths_over_the_whole_horizon": dv,
        "READING": ("dropping the activity conditions does leave points. At every one of them "
                    "the expected number of Y births over the ENTIRE 11000-step horizon is at "
                    "most %.3g and the expected number of Y deaths at most %.3g. No Y event "
                    "occurs. This set is the frozen point kY = muY = 0 wearing a different "
                    "label, and calling it a window would be exactly the error the inherited "
                    "handoff warns against: a structural zero is not a small number."
                    % (ev, dv)),
    }


def threshold_sensitivity():
    """How far would the thresholds, or the geometry, have to move to open the region?

        survival <= ln(N*) tau_sep / (T ln(1/gamma))  >=  1 - alpha
        =>  tau_sep / T  >=  (1-alpha) ln(1/gamma) / ln(N*)
    """
    rows = []
    for N in (2.0, 10.0, 100.0):
        for g in (0.5, 1.0 - 1e-9, 0.1):
            for a in (0.5, 0.9):
                need = (1 - a) * math.log(1 / g) / math.log(N) if g < 1 else 0.0
                rows.append({"N_star": N, "gamma_sep": g, "alpha": a,
                             "required_tau_sep_over_T": need,
                             "actual_tau_sep_over_T": TAU_SEP / T_HORIZON,
                             "OPENS": TAU_SEP / T_HORIZON >= need})
    geom = {str(d): {"tau_sep_steps": d * d / (4 * D_REL),
                     "tau_sep_over_T": (d * d / (4 * D_REL)) / T_HORIZON}
            for d in (1.0, 2.5, 5.0, 6.082762530298219, 8.54400374531753)}
    need_ref = 0.5 * math.log(1 / GAMMA_SEP) / math.log(N_STAR)
    return {
        "ROWS": rows, "SEPARATION_GEOMETRY": geom,
        "REQUIRED_RATIO_AT_THE_DECLARED_THRESHOLDS": need_ref,
        "ACTUAL_RATIO": TAU_SEP / T_HORIZON,
        "SHORTFALL_FACTOR": need_ref / (TAU_SEP / T_HORIZON),
        "ONLY_DEGENERATE_ROWS_OPEN": (
            "the only threshold combinations that open the region are those with gamma -> 1, "
            "i.e. those that ACCEPT one expected separated second centre. That is not a "
            "relaxation of a threshold, it is abandoning the single-source requirement and "
            "with it the qualified environment. The closest NON-degenerate miss is "
            "N* = 100, gamma = 0.5, alpha = 0.9 -- allow a hundred organisers and demand only "
            "a 10 %% survival probability -- and it still fails by a factor 1.33."),
        "WHAT_WOULD_HAVE_TO_CHANGE": {
            "shorten_the_horizon_to_steps": TAU_SEP / need_ref,
            "and_the_burn_in_is": 2000,
            "horizon_would_be_below_the_burn_in": (TAU_SEP / need_ref) < 2000,
            "or_slow_the_Y_transport_by_factor": need_ref / (TAU_SEP / T_HORIZON),
            "required_D_rel": D_REL * (TAU_SEP / T_HORIZON) / need_ref,
            "required_p_hop_Y_approx": 4 * (D_REL * (TAU_SEP / T_HORIZON) / need_ref) / 2,
            "BUT": ("p_hop_Y is not a manifest field. protocol_obtc02.spec_for sets it to "
                    "PT['p_hop'], the same number as p_hop_X. Slowing the Y transport slows "
                    "the X transport by the same factor and moves the control baseline, which "
                    "this mission forbids."),
        },
    }


# ------------------------------------------------------------------ the mission's OWN framing
def evaluate_division_framing(beta, m, c, T=T_HORIZON, tau=TAU_SEP):
    """The inherited handoff does NOT ask for a single source held forever. Its §3.5 names

        LOWER_BOUND_FOR_MINOR_Y_PERSISTENCE
        UPPER_BOUND_PREVENTING_PREMATURE_THIRD_CENTER
        SEPARATION_OR_REORGANIZATION_TIMESCALE

    i.e. one division is ALLOWED and a THIRD centre must not appear before the first two have
    separated. Evaluating only the stricter single-source framing would be judging the mission
    against a question it never asked, so both are computed and both are reported."""
    p = beta / c
    if p > 1.0:
        return None
    R = (1.0 - m) * (1.0 + beta)
    log_pow = T * math.log(R) if R > 0 else -math.inf
    if log_pow > 300 * math.log(10):
        nT, cum = math.inf, math.inf
    elif abs(R - 1.0) < 1e-15:
        nT, cum = 1.0, float(T)
    else:
        nT = math.exp(log_pow)
        cum = (nT - 1.0) / (R - 1.0)
    births = beta * cum
    deaths = m * cum
    surv = 1.0 - extinction_by(T, c, p, m)
    newborn_reaches_separation = (1.0 - m) ** tau
    third_before_separation = 2.0 * beta * tau * newborn_reaches_separation
    return {"beta": beta, "muY": m, "c": c, "R": R, "epsilon": R - 1.0,
            "E_nY_at_T": nT, "E_births": births, "E_deaths": deaths,
            "survival_to_T": surv,
            "P_newborn_survives_to_separate": newborn_reaches_separation,
            "E_third_centre_before_separation": third_before_separation,
            "D1_PERSISTS": surv >= 1.0 - ALPHA_SURVIVAL,
            "D2_DIVIDES_AT_LEAST_ONCE": births >= MIN_EVENTS,
            "D3_NO_THIRD_BEFORE_SEPARATION": third_before_separation <= GAMMA_SEP,
            "D4_STILL_A_MINORITY_AT_T": nT <= N_STAR,
            "D5_DEATH_CONTROL_ACTIVE": deaths >= MIN_EVENTS,
            "D6_ADMISSIBLE": 0.0 < m < 1.0 and beta > 0.0 and p <= 1.0}


def scan_division_framing(c=4):
    keys = ("D1_PERSISTS", "D2_DIVIDES_AT_LEAST_ONCE", "D3_NO_THIRD_BEFORE_SEPARATION",
            "D4_STILL_A_MINORITY_AT_T", "D5_DEATH_CONTROL_ACTIVE", "D6_ADMISSIBLE")
    betas = np.logspace(-8, 0, 161)
    mus = np.logspace(-8, -0.05, 159)
    inside, n = [], 0
    counts = {k: 0 for k in keys}
    for b in betas:
        for m in mus:
            r = evaluate_division_framing(float(b), float(m), c)
            if r is None:
                continue
            n += 1
            for k in keys:
                counts[k] += int(r[k])
            if all(r[k] for k in keys):
                inside.append(r)
    box = None
    if inside:
        box = {"beta_min": min(r["beta"] for r in inside),
               "beta_max": max(r["beta"] for r in inside),
               "muY_min": min(r["muY"] for r in inside),
               "muY_max": max(r["muY"] for r in inside)}
        box["beta_decades"] = math.log10(box["beta_max"] / box["beta_min"])
        box["muY_decades"] = math.log10(box["muY_max"] / box["muY_min"])
    return {"c": c, "grid_points": n, "n_inside": len(inside),
            "per_condition_satisfied": counts, "NONEMPTY": bool(inside),
            "BOUNDING_BOX": box, "examples": inside[:4],
            "WHAT_IT_WOULD_PRODUCE": (
                "a state with two or more spatially separated organisers" if inside else None)}


def qualified_environment_check():
    """Even a non-empty division region has to be checked against the environment the parent
    actually qualified. That environment is single-organiser BY CONSTRUCTION."""
    return {
        "THE_PARENT_QUALIFIED": ("a CONDITIONAL source-transport-decay operator for three "
                                 "observables of an ORGANIZER_BOUND_SOURCE cloud, with "
                                 "exactly one organiser"),
        "OBSERVABLE_LAYER": ("metrics_obtc.frame resolves the organiser as oy[0], ox[0] from "
                             "np.nonzero(nY). With two organisers it silently reports one of "
                             "them, chosen by row-major order, and r80_organiser is measured "
                             "about that arbitrary centre."),
        "FROZEN_GATES_AFFECTED": ["SOURCE_ATTACHMENT (median core-to-organiser, unwrapped "
                                  "position correlation)",
                                  "RELATIVE_LOCALIZATION (r80 about THE organiser's cell)",
                                  "CORE_CONTINUITY", "MODEL_PREDICTION_COMPATIBILITY"],
        "X_SOURCE_MULTIPLICITY": ("p_X = min(1, kX nX nY) = 1 exactly at kX = 1.0 for any "
                                  "nX nY >= 1, so every separated organiser is a full-strength "
                                  "X source. Two organisers is not a perturbation of one; it "
                                  "is a two-source problem."),
        "CONSEQUENCE": ("any parameter region that succeeds in producing a persisting Y "
                        "lineage produces a state for which the parent's qualification, the "
                        "inherited observables and every frozen gate are undefined. The "
                        "qualification chain does not extend to it."),
    }


def predeclared_category_B_bounds():
    """The launcher allows 'a rigorously predeclared distribution or bound over category B'.
    Such bounds exist, frozen in obtc02_protocol.yaml before any of the runs now inherited.
    This asks, honestly, how far they get."""
    return {
        "AVAILABLE_PREDECLARED_BOUNDS": {
            "gate.FREE_CAPACITY_PRESERVED.mean_free_at_organiser_min": 0.5,
            "gate.NO_KINETIC_FREEZE.mean_births_per_step_min": 0.1,
            "gate.NO_KINETIC_FREEZE.mean_deaths_per_step_min": 0.1,
            "gate.POPULATION_STATIONARY.N_X_min": 20,
        },
        "WHAT_THEY_LEGITIMATELY_GIVE": {
            "E_free_at_the_organiser_cell_geq": 0.5,
            "E_min_nSX_free_at_the_organiser_cell_geq": 0.1,
            "P_nX_at_the_organiser_cell_geq_1": 0.1 / CAP,
            "E_N_X_geq": 25.0,
            "why_the_births_bound_reads_that_way": (
                "p_X = min(1, kX nX nY) = 1 exactly at kX = 1.0 whenever nX nY >= 1, so the "
                "mean accepted X births per step IS E[min(nSX, free)] on the steps where the "
                "organiser cell holds at least one X; and since at most CAP births can occur "
                "in a cell, 0.1 <= CAP * P(nX_org >= 1)"),
        },
        "WHAT_THEY_DO_NOT_GIVE": (
            "a numerical lower bound on E[Q] = E[nX * min(nSY, free)] AT THE ORGANISER'S OWN "
            "CELL. They locate the global X population, the free capacity at the organiser and "
            "the X-substrate candidate count; none locates the product of the co-located X "
            "count with the Y-substrate candidate count."),
        "THEREFORE": {
            "E_Q_IS_STRICTLY_POSITIVE": True,
            "basis": "P(nX_org >= 1) >= %.5f from a frozen predeclared threshold" % (0.1 / CAP),
            "E_Q_IS_NUMERICALLY_LOCATED": False,
            "CONSEQUENCE_FOR_THE_REGION": (
                "the lower boundary of the (kY, muY) region is known to be strictly positive "
                "and is NOT located. Condition 2 asks the next-generation criterion to exceed "
                "the persistence boundary WITH NUMERICAL MARGIN. A margin is a number. This "
                "one does not exist without measuring the realized cloud, which is precisely "
                "the measurement that made the parent's own prediction CONDITIONAL."),
        },
        "UPPER_BOUNDARY_IS_UNAFFECTED": "beta <= Q_max kY = 28 kY needs no measurement at all",
    }


def regions():
    A = {
        "NAME": "ABSTRACT_Y_INTERVAL",
        "STATEMENT": "R = (1-muY)(1 + Q kY) > 1  <=>  Q kY > muY/(1-muY)",
        "TREATING_Q_AS_A_FREE_POSITIVE_REAL": True,
        "NONEMPTY": True,
        "for_any_muY_in_0_1_there_is_a_kY": True,
        "STATUS": "EXPLANATORY ONLY. It ignores that Q is an integer functional of a cell "
                  "state the LawSpec does not determine.",
        "HISTORICAL_INTERVAL_NOT_REUSED": "(0, 1.787e-4) is inherited from a different, "
                                          "non-portable point and is not used as evidence",
    }
    B = {
        "NAME": "EXECUTABLE_Y_INTERVAL",
        "kY_admissible_range": "[0, inf); p is clamped by min(1, .), so kY > 1/(nX nY) only "
                               "saturates",
        "muY_admissible_range": "[0, 1]; it is a Bernoulli probability in rng.binomial",
        "Q_range_from_the_admissible_set": [Q_INF, Q_MAX],
        "beta_range_certifiable_from_category_A": ["0", "%d * kY" % Q_MAX],
        "UPPER_BOUNDARY_IS_CERTIFIABLE": True,
        "why_upper": "beta <= Q_max kY = 28 kY holds for every admissible cell state",
        "LOWER_BOUNDARY_IS_CERTIFIABLE": False,
        "why_lower": ("beta >= something positive requires E[Q] > 0, i.e. a positive lower "
                      "bound on nX * min(nSY, free) AT THE ORGANISER'S OWN CELL. The "
                      "admissible set contains Q = 0 (60.1 % of admissible cell states), so "
                      "the infimum over the set is 0. A positive value is a property of the "
                      "realized measure, not of the LawSpec."),
        "THIS_IS_THE_INHERITED_LIMITATION": (
            "the parent seal certified MARGINAL_DENSITY_CLOSURE = NOT_CLOSED and had to "
            "MEASURE the birth-flux law. E[Q] is the same kind of object. Placing the lower "
            "boundary of the minority window on it would make the window CONDITIONAL on a "
            "category-B measurement, which this mission forbids as load-bearing."),
        "NONEMPTY_AS_A_ONE_SIDED_SET": True,
        "IS_A_WINDOW": False,
    }
    return A, B


def independence_gates(scan_c4):
    return {
        "Y_BIRTH_CONTROL_IS_ACTIVE": {
            "verdict": True,
            "evidence": "mutation oracle kY 0 -> 1: hazard argument p changes 0 -> 1, Y delta "
                        "0 -> +4 = min(nSY, free) exactly, reversal bit-exact"},
        "Y_DEATH_OR_SURVIVAL_CONTROL_IS_ACTIVE": {
            "verdict": True,
            "evidence": "mutation oracle muY 0 -> 1: hazard argument p changes 0 -> 1, Y delta "
                        "0 -> -1, reversal bit-exact"},
        "CONTROLS_ARE_NOT_ALIASES": {
            "verdict": True,
            "evidence": "kY is read only in _react_core, muY only in _decay_core; they are "
                        "separate manifest fields copied verbatim by spec_for; perturbing one "
                        "leaves the other's captured hazard argument unchanged"},
        "CONTROLS_DO_NOT_ONLY_RESCALE_X": {
            "verdict": "PARTIAL",
            "evidence": ("p_X = min(1, kX nX nY) with kX = 1.0 is EXACTLY 1 for any nX nY >= "
                         "1, so changing nY does not rescale the per-cell X hazard at all. "
                         "What a second Y changes is the NUMBER of source cells, once it "
                         "separates. So the Y controls do not rescale X — they multiply the "
                         "source count, which is a stronger and worse coupling."),
            "same_step_isolation": True,
            "next_step_coupling": True},
        "PARAMETER_VALUES_ARE_ADMISSIBLE": {
            "verdict": True,
            "evidence": "no assert or raise anywhere in the executable path mentions kY, muY "
                        "or p_hop_Y; muY in [0,1] is a Bernoulli probability, kY >= 0 is "
                        "clamped by min(1, .)"},
        "OPERATOR_IS_IDENTIFIABLE_FROM_EXECUTABLE_SEMANTICS": {
            "verdict": False,
            "evidence": ("the one-step law is CONDITIONAL_EXACT given (nX, nSY, free) at the "
                         "Y's own cell, and every argument was verified against the "
                         "scheduler. But that cell state is produced BY the lineage: _react "
                         "creates X only where nX nY >= 1. The environment is endogenous, the "
                         "marginal does not close, and no scalar branching ratio is "
                         "identifiable without measuring the realized cloud.")},
        "ROBUST_REGION_HAS_POSITIVE_WIDTH": {
            "verdict": scan_c4["REGION_NONEMPTY"],
            "evidence": "see the scan and the closed-form ceiling"},
    }


def timescale_collapse():
    return {
        "Y_TIMESCALES_THE_ARCHITECTURE_EXPOSES": {
            "tau_Y_birth": "1 / (kY * Q)",
            "tau_Y_removal": "1 / muY",
            "tau_newborn_removal": "1 / muY",
            "tau_separation": "d^2 / (4 D_rel) = 5 d^2, set by p_hop",
        },
        "COLLAPSE_FOUND": True,
        "WHICH": "tau_newborn_removal == tau_Y_removal, identically",
        "WHY": ("_decay draws Binomial(n_Y, muY) over the whole Y field. It reads no age, no "
                "position, no contact and no lineage label. A newborn and the founder are "
                "exchangeable counts in the same array, so one parameter sets both clocks."),
        "WHY_IT_IS_FATAL_HERE": (
            "a minority window needs newborns removed FAST, so that a second source never "
            "separates, and the lineage removed SLOWLY, so that it survives the horizon. "
            "Those are two requirements on one number."),
        "SEPARATION_IS_ALSO_NOT_INDEPENDENT": (
            "p_hop_Y is not a manifest field. protocol_obtc02.spec_for sets it to 0.0 under "
            "the declared immobilisation intervention and otherwise to PT['p_hop'], the SAME "
            "value as p_hop_X. The separation clock cannot be moved without moving the X "
            "transport clock, which is the control baseline."),
        "CONTRAST_WITH_THE_X_SIDE": (
            "OBTR01 found seven of eight X timescales to be fixed rational multiples of "
            "1/muX. The Y side is not a repeat of that: tau_Y_birth and tau_Y_removal are "
            "genuinely two free parameters. The collapse here is different and narrower — it "
            "is the removal clock being shared between two ROLES, not two formulas sharing a "
            "parameter."),
    }


def main():
    A, B = regions()
    scans = {c: scan(c) for c in (1, 4, 7)}
    cf = closed_form_bound()
    front = pairwise_frontier(4)

    C = {
        "NAME": "ROBUST_REACHABLE_Y_REGION",
        "INPUTS_USED": "category A only: CAP, S0, X_SEED, kX, the exact kernel constants, the "
                       "frozen horizon and the admissible-state enumeration",
        "CATEGORY_B_USED": "none as a load-bearing input; E[Q] is deliberately NOT used",
        "CATEGORY_C_USED": "none",
        "CONDITIONS": {
            "1_does_not_deterministically_vanish": "survival to T >= %.2f" % (1 - ALPHA_SURVIVAL),
            "2_exceeds_the_persistence_boundary_with_margin": "R > 1 and E[nY(T)] <= %g"
                                                              % N_STAR,
            "3_remains_minority_not_dominating": "expected separated second centres <= %g"
                                                 % GAMMA_SEP,
            "4_capacity_and_resource_assumptions_hold": "rare-Y linearisation, nY << CAP",
            "5_not_created_by_a_favourable_historical_trajectory": "no realized covariate used",
            "6_survives_the_admissibility_map": "0 < muY < 1, kY >= 0, p = min(1, kY nX nY)",
            "7_bounds_do_not_merely_touch": "both controls must fire at least once per horizon",
        },
        "THRESHOLDS_ARE_GENEROUS_ON_PURPOSE": (
            "survival only 1/2, ten organisers allowed, half an expected second centre "
            "allowed. Every threshold is set to make a window EASIER to find, so that an "
            "empty region is not an artefact of strictness."),
        "SCANS": scans,
        "CLOSED_FORM_CEILING": cf,
        "PAIRWISE_AND_TRIPLE_FRONTIER": front,
        "NONEMPTY": any(s["REGION_NONEMPTY"] for s in scans.values()),
        "WIDTH": 0.0 if not any(s["REGION_NONEMPTY"] for s in scans.values()) else None,
        "WITHOUT_THE_ACTIVITY_CONDITIONS": region_without_activity_conditions(),
        "DIVISION_FRAMING_THE_MISSIONS_OWN": {
            "WHY_IT_IS_COMPUTED": ("the inherited handoff names an upper bound preventing a "
                                   "PREMATURE THIRD centre, so one division is allowed. "
                                   "Judging the mission only against the stricter "
                                   "single-source framing would answer a question it never "
                                   "asked."),
            "SCAN": scan_division_framing(4),
            "TRANSPORT_TO_THE_ACTUAL_PARAMETERS": {
                "the_scan_is_in_beta_and_muY": True,
                "beta_equals_kY_times_Q_bar": True,
                "upper_boundary_in_kY_certifiable": "kY <= beta_max / 28",
                "lower_boundary_in_kY_certifiable": False,
                "why": ("no finite kY guarantees beta >= beta_min, because the infimum of Q "
                        "over the admissible cell-state set is 0"),
                "PREDECLARED_BOUNDS": predeclared_category_B_bounds()},
            "QUALIFIED_ENVIRONMENT_CHECK": qualified_environment_check()},
        "THRESHOLD_AND_GEOMETRY_SENSITIVITY": threshold_sensitivity(),
    }

    gates = independence_gates(scans[4])
    ts = timescale_collapse()

    out = {"SECTION": "PMCR01 §7-§8 — regions and gates",
           "REGION_A": A, "REGION_B": B, "REGION_C": C,
           "INDEPENDENCE_GATES": gates,
           "TIMESCALE_COLLAPSE": ts,
           "CONSTANTS_USED": {"CAP": CAP, "Q_MAX": Q_MAX, "T_HORIZON": T_HORIZON,
                              "T_WINDOW": T_WINDOW, "D_REL": D_REL, "CORE_R": CORE_R,
                              "TAU_SEP": TAU_SEP}}
    json.dump(out, open(f"{OUT}/PMCR01_REACHABILITY_REGIONS.json", "w"), indent=1, default=str)

    print("REGION A abstract    : nonempty = %s" % A["NONEMPTY"])
    print("REGION B executable  : upper boundary certifiable = %s ; lower = %s ; is a window "
          "= %s" % (B["UPPER_BOUNDARY_IS_CERTIFIABLE"], B["LOWER_BOUNDARY_IS_CERTIFIABLE"],
                    B["IS_A_WINDOW"]))
    print("\nREGION C robust, exact scan over (beta, muY), tau_sep = %.1f steps, T = %d:"
          % (TAU_SEP, T_HORIZON))
    for c, s in scans.items():
        print("  c=%d  grid %d  inside %d  nonempty %s" % (c, s["grid_points"], s["n_inside"],
                                                           s["REGION_NONEMPTY"]))
        for k, v in s["per_condition_satisfied"].items():
            print("        %-28s satisfied at %6d / %d points" % (k, v, s["grid_points"]))
        b = s["best_point_found"]
        print("        best point: beta=%.3g muY=%.3g R-1=%.3g survival=%.4f E[nY(T)]=%.3g "
              "sep=%.3g births=%.3g deaths=%.3g  (%d/6 conditions)"
              % (b["beta"], b["muY"], b["epsilon"], b["survival_to_T"], b["E_nY_at_T"],
                 b["E_separated_second_centres"], b["E_births"], b["E_deaths"],
                 b["n_satisfied"]))
    print("\nempty TRIPLES of conditions (no grid point satisfies all three):")
    for k in front["triples"]:
        print("   %s" % k)
    print("\nclosed-form ceiling, no grid:")
    for k, v in cf.items():
        if k not in ("READING", "APPROXIMATE_FORM"):
            print("   %-42s %s" % (k, v))
    print("   %s" % cf["APPROXIMATE_FORM"])
    print("\ngates:")
    for k, v in gates.items():
        print("   %-52s %s" % (k, v["verdict"]))
    print("\ntimescale collapse: %s -- %s" % (ts["COLLAPSE_FOUND"], ts["WHICH"]))
    w = C["WITHOUT_THE_ACTIVITY_CONDITIONS"]
    print("\nif C4 and C5 are dropped: nonempty=%s, but max expected births over 11000 steps "
          "= %.3g and max expected deaths = %.3g"
          % (w["NONEMPTY"], w.get("max_expected_births_over_the_whole_horizon", 0),
             w.get("max_expected_deaths_over_the_whole_horizon", 0)))
    t = C["THRESHOLD_AND_GEOMETRY_SENSITIVITY"]
    print("\nsensitivity: required tau_sep/T = %.4f, actual = %.4f, shortfall factor %.1fx"
          % (t["REQUIRED_RATIO_AT_THE_DECLARED_THRESHOLDS"], t["ACTUAL_RATIO"],
             t["SHORTFALL_FACTOR"]))
    print("   to open it: horizon would have to fall to %.0f steps (burn-in alone is 2000) "
          "or D_rel to %.5f (p_hop_Y ~ %.4f, but it is aliased to p_hop_X)"
          % (t["WHAT_WOULD_HAVE_TO_CHANGE"]["shorten_the_horizon_to_steps"],
             t["WHAT_WOULD_HAVE_TO_CHANGE"]["required_D_rel"],
             t["WHAT_WOULD_HAVE_TO_CHANGE"]["required_p_hop_Y_approx"]))
    nd = [r for r in t["ROWS"] if r["gamma_sep"] < 0.99]
    print("   opens under any NON-DEGENERATE threshold combination (gamma < 1): %s ; "
          "closest miss factor %.2f"
          % (any(r["OPENS"] for r in nd),
             min(r["required_tau_sep_over_T"] / r["actual_tau_sep_over_T"] for r in nd)))
    print("   the only rows that open have gamma -> 1, i.e. they accept a second centre")
    d = C["DIVISION_FRAMING_THE_MISSIONS_OWN"]["SCAN"]
    print("\nMISSION'S OWN DIVISION FRAMING (one division allowed, no third before separation):")
    for k, v in d["per_condition_satisfied"].items():
        print("   %-34s %6d / %d" % (k, v, d["grid_points"]))
    print("   NONEMPTY = %s ; inside = %d" % (d["NONEMPTY"], d["n_inside"]))
    if d["BOUNDING_BOX"]:
        b = d["BOUNDING_BOX"]
        print("   box: beta in [%.3g, %.3g] (%.2f decades) ; muY in [%.3g, %.3g] (%.2f decades)"
              % (b["beta_min"], b["beta_max"], b["beta_decades"], b["muY_min"], b["muY_max"],
                 b["muY_decades"]))


if __name__ == "__main__":
    main()
