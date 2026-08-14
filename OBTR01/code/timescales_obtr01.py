"""OBTR01 §10-§11 — the eight timescales of the organiser-bound cloud, and their relations.

Every value below is a closed form or an exact discrete solve in the QUALIFIED LawSpec. None is
fitted, and none is taken from a previous mission's report.

The classification the mandate asks for is not decoration. Six of the eight timescales turn out
to be driven by the single parameter mu_X, so they agree with one another to a fraction of a
percent NO MATTER WHAT THE SYSTEM DOES. Reporting that agreement as a finding would be an
error, and §26 depends on the distinction, so each relation is classified by its ALGEBRA:

  EXACT_IDENTITY                     the two expressions are the same expression
  ASYMPTOTIC_IDENTITY                they agree to leading order in a stated small parameter
  APPROXIMATE_NUMERICAL_COINCIDENCE  the numbers are close at this point but the expressions
                                     are unrelated, so the agreement carries no information
  NOT_EQUAL                          they differ, with the exact factor given
  UNRESOLVED                         the artefacts do not decide it
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import yaml

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, "/home/claude/OBTR01/code")

from kernels_obtr01 import Operator, relative_kernel, one_step_kernel   # noqa: E402
from corrections_obtr01 import mean_exit_time_discrete                  # noqa: E402


def survival_to_radius(K, radius, mu):
    """P(a molecule reaches the circle of radius `radius` before dying), started at the source.

    h(x) = (1 - mu) sum_z K(z) h(x + z) inside, h = 1 outside. Solved exactly, same discrete
    Poisson machinery as the exit time, with the mortality folded into the operator."""
    R = int(math.ceil(radius))
    sites = [(y, x) for y in range(-R, R + 1) for x in range(-R, R + 1)
             if y * y + x * x <= radius * radius]
    idx = {s: i for i, s in enumerate(sites)}
    n = len(sites)
    A = np.eye(n)
    b = np.zeros(n)
    s = 1.0 - mu
    for site, i in idx.items():
        for (dy, dx), p in K.items():
            t = (site[0] + dy, site[1] + dx)
            j = idx.get(t)
            if j is None:
                b[i] += s * p                      # stepped out and survived: absorbed at 1
            else:
                A[i, j] -= s * p
    h = np.linalg.solve(A, b)
    return float(h[idx[(0, 0)]]), n


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt, an = spec["point"], None
    import gate_obtc02 as _  # noqa: F401  (kept out of the path; analytic block read below)
    an = yaml.safe_load(open(f"{WC}/OBTC02/code/obtc02_protocol.yaml")).get("analytic", {})

    L, mu = int(pt["L"]), float(pt["muX"])
    q = pt["p_hop"] / 4.0
    a_X = 2 * q * (1 - q)
    D_X = q * (1 - q)
    a_rel, D_rel = 2 * a_X, a_X                    # both organiser and molecule move
    D_Y = D_X                                      # p_hop_Y = p_hop_X at the qualified point
    ell_X = math.sqrt(D_X / mu)
    ell_rel = math.sqrt(D_rel / mu)
    core_R = float(an.get("core_radius_cells", 5.0))

    op = Operator(q, q, mu, L)
    Krel = relative_kernel(q, q)
    KX = one_step_kernel(q)

    # ---------------------------------------------------------------- the eight timescales
    tau_lifetime = (1.0 - mu) / mu                       # E[S], S ~ Geometric on {0,1,...}
    tau_efold = -1.0 / math.log(1.0 - mu)                # e-folding of a geometric decay
    tau_mass_on = tau_efold
    tau_source_off = tau_efold
    tau_turnover = 1.0 / mu                              # N* / B with N* = B / mu
    tau_follow = tau_lifetime                            # the cloud is a mixture of ages S
    tau_shape_intrinsic = ell_rel ** 2 / D_rel           # time to diffuse one cloud radius
    shape_mode = op.shape_relaxation_time()
    tau_shape_torus = shape_mode["tau_shape"]

    fp_rel, n_rel = mean_exit_time_discrete(Krel, core_R)
    fp_rel_ell, _ = mean_exit_time_discrete(Krel, ell_rel)
    fp_src, n_src = mean_exit_time_discrete(one_step_kernel(q), ell_rel)
    surv_core, _ = survival_to_radius(Krel, core_R, mu)
    surv_ell, _ = survival_to_radius(Krel, ell_rel, mu)

    TAU = {
        "TAU_LIFETIME": {
            "value": tau_lifetime,
            "closed_form": "(1 - mu_X) / mu_X",
            "derivation": "_decay draws Binomial(n, mu) per step, so the age of a molecule is "
                          "Geometric on {0, 1, ...} with success probability mu and mean "
                          "(1 - mu)/mu. Independent of position and of the neighbourhood.",
            "driven_by": "mu_X"},
        "TAU_MASS_ON": {
            "value": tau_mass_on,
            "closed_form": "-1 / ln(1 - mu_X)",
            "derivation": "with a source of constant mean intensity B switched on at t = 0, "
                          "N(t) = (B/mu)(1 - (1-mu)^t); the approach to N* is geometric with "
                          "ratio (1 - mu), whose e-folding is -1/ln(1 - mu).",
            "driven_by": "mu_X"},
        "TAU_SHAPE": {
            "value": tau_shape_intrinsic,
            "closed_form": "ell_rel^2 / D_rel = 1 / mu_X",
            "derivation": "the time for a molecule to diffuse one localisation length of the "
                          "relative walk. NOTE that ell_rel is DEFINED as sqrt(D_rel/mu), so "
                          "this is 1/mu identically; see the relations table.",
            "driven_by": "mu_X (through the definition of ell_rel)",
            "TORUS_VARIANT": {
                "value": tau_shape_torus, "L": L,
                "closed_form": "-1 / ln(lambda_1 / lambda_0), lambda_k the operator spectrum",
                "lambda_1_over_lambda_0": shape_mode["ratio"],
                "meaning": "relaxation of the SLOWEST non-uniform mode of the torus, which is "
                           "a property of the finite domain and not of the cloud",
                "driven_by": "L and a_rel"}},
        "TAU_FOLLOW": {
            "value": tau_follow,
            "closed_form": "(1 - mu_X) / mu_X",
            "derivation": "a molecule alive at t was born at t - S at the organiser's position "
                          "then, so the cloud's mean offset from the current organiser is the "
                          "organiser's own displacement over a Geometric(mu) lag. The optimal "
                          "tracking lag is therefore E[S].",
            "driven_by": "mu_X"},
        "TAU_SOURCE_OFF": {
            "value": tau_source_off,
            "closed_form": "-1 / ln(1 - mu_X)",
            "derivation": "after the source is removed, N(t) = N(0)(1 - mu)^t exactly; no "
                          "transport term enters because decay is per particle and uniform.",
            "driven_by": "mu_X",
            "frozen_analytic_value": an.get("source_off_e_folding_steps")},
        "TAU_TURNOVER": {
            "value": tau_turnover,
            "closed_form": "N_X* / E[B] = 1 / mu_X",
            "derivation": "at stationarity E[B] = mu N*, so the time to replace the standing "
                          "population once is N*/E[B] = 1/mu, whatever B is. The chemostat's "
                          "supply cancels.",
            "driven_by": "mu_X"},
        "TAU_FP_RELATIVE": {
            "value": fp_rel,
            "at_radius": core_R, "interior_sites": n_rel,
            "closed_form": "exact discrete solve of (I - P_rel) T = 1 on the disc",
            "continuum_comparison": core_R ** 2 / (4 * D_rel),
            "excess_over_the_continuum_law": fp_rel / (core_R ** 2 / (4 * D_rel)) - 1.0,
            "at_ell_rel": {"radius": ell_rel, "value": fp_rel_ell},
            "survival_to_that_radius": surv_core,
            "survival_to_ell_rel": surv_ell,
            "derivation": "mean first passage of the molecule-organiser relative coordinate "
                          "from co-location to the core radius, with no mortality; the "
                          "survival figures give the fraction that get there before dying.",
            "driven_by": "D_rel and the chosen radius. At the qualified point the radius is "
                          "itself a multiple of ell_X, so this too reduces to a multiple of "
                          "1/mu_X: see TIMESCALE_COLLAPSE."},
        "TAU_SOURCE_SEPARATION": {
            "value": fp_src,
            "at_radius": ell_rel, "interior_sites": n_src,
            "closed_form": "exact discrete solve for the ORGANISER's own walk",
            "continuum_comparison": ell_rel ** 2 / (4 * D_Y),
            "derivation": "the time for the SOURCE itself to move one cloud radius away from "
                          "where it was. In the qualified LawSpec there is never a second "
                          "organiser, so the historical reading of this name -- the time for "
                          "two organisers to separate -- has no referent and is recorded in "
                          "§5 as INVALID_IN_QUALIFIED_LAWSPEC. What is defined here is the "
                          "single-organiser analogue, and it is a different quantity.",
            "HISTORICAL_READING": "INVALID_IN_QUALIFIED_LAWSPEC",
            "driven_by": "D_Y and the chosen radius. Same caveat as TAU_FP_RELATIVE: the "
                          "radius is a multiple of ell_X, so this also reduces to 1/(2 mu_X)."},
    }

    # ---------------------------------------------------------------- §11 relations
    def rel(a, b, kind, why, exact_factor=None):
        va = TAU[a]["value"] if a in TAU else a
        vb = TAU[b]["value"] if b in TAU else b
        d = {"left": a, "right": b, "value_left": va, "value_right": vb,
             "ratio": va / vb, "CLASSIFICATION": kind, "reason": why}
        if exact_factor is not None:
            d["exact_factor"] = exact_factor
            d["ratio_matches_the_exact_factor"] = abs(va / vb - exact_factor) < 1e-12
        return d

    R = [
        rel("TAU_LIFETIME", "TAU_FOLLOW", "EXACT_IDENTITY",
            "both are E[S] for the same Geometric(mu_X) age. Not two facts about the system: "
            "one fact, written twice. The cloud follows the source with exactly the lag that "
            "its material survives.", 1.0),
        rel("TAU_MASS_ON", "TAU_SOURCE_OFF", "EXACT_IDENTITY",
            "both are the e-folding of the same geometric factor (1 - mu_X). Switching the "
            "source on and switching it off relax at the same rate because the operator is "
            "linear in the mass and the decay term is the same in both directions.", 1.0),
        rel("TAU_SHAPE", "TAU_TURNOVER", "EXACT_IDENTITY",
            "ell_rel is DEFINED as sqrt(D_rel/mu_X), so ell_rel^2/D_rel is 1/mu_X identically. "
            "This has a consequence that must not be missed: 'the cloud radius agrees with the "
            "diffusion-decay prediction' is NOT an independent check on the lifetime, because "
            "the radius is constructed from it.", 1.0),
        rel("TAU_TURNOVER", "TAU_LIFETIME", "NOT_EQUAL",
            "1/mu against (1 - mu)/mu: an exact factor (1 - mu_X), one step of difference. "
            "They are not the same quantity even though they differ by 0.4 % here.",
            1.0 / (1.0 - mu)),
        rel("TAU_MASS_ON", "TAU_TURNOVER", "ASYMPTOTIC_IDENTITY",
            "-1/ln(1 - mu) = 1/mu - 1/2 + O(mu). The two agree to leading order in mu_X and "
            "differ by half a step here, which is why -1/ln(1-mu) = %.4f sits between "
            "(1-mu)/mu = %.1f and 1/mu = %.1f." % (tau_efold, tau_lifetime, tau_turnover)),
        rel("TAU_LIFETIME", "TAU_MASS_ON", "ASYMPTOTIC_IDENTITY",
            "same expansion; the gap is O(1) steps against a scale of O(1/mu)."),
        rel("TAU_FP_RELATIVE", "TAU_SHAPE", "NOT_EQUAL",
            "the exact continuum factor is 1/2, not 1: core_R^2/(4 D_rel) = 1/(2 mu_X) against "
            "ell_rel^2/D_rel = 1/mu_X. The measured ratio %.4f exceeds 1/2 by the lattice "
            "boundary layer at radius %.1f. They are different quantities, but -- contrary to "
            "the naive reading -- they are not INDEPENDENT quantities: both are rational "
            "multiples of 1/mu_X once the radius is measured in cloud radii."
            % (fp_rel / tau_shape_intrinsic, core_R), 0.5),
        rel("TAU_SOURCE_SEPARATION", "TAU_SHAPE", "NOT_EQUAL",
            "the ratio is the coherence number chi^2/4. It is the physically decisive "
            "comparison of this section: see COHERENCE below."),
        rel("TAU_FP_RELATIVE", "TAU_SOURCE_SEPARATION", "ASYMPTOTIC_IDENTITY",
            "not a coincidence, and not two independent numbers. The frozen core radius is "
            "core_R = 2 ell_X EXACTLY (5.0 = 2 x 2.5) and ell_rel = sqrt(2) ell_X, while "
            "D_rel = 2 D_X = 2 D_Y. Substituting, BOTH continuum first passages reduce to the "
            "same expression: core_R^2/(4 D_rel) = ell_X^2/(2 D_X) = 1/(2 mu_X) = %.1f, and "
            "ell_rel^2/(4 D_Y) = ell_X^2/(2 D_X) = 1/(2 mu_X) = %.1f. The %.2f %% gap between "
            "the discrete values is the lattice boundary layer alone, which is larger at the "
            "smaller radius." % (1 / (2 * mu), 1 / (2 * mu),
                                 100 * abs(fp_rel / fp_src - 1))),
    ]

    chi = math.sqrt(4.0 * D_Y / mu) / ell_X
    coherence = {
        "chi": chi,
        "definition": "sqrt(4 D_Y / mu_X) / ell_X, the organiser's wander over one "
                      "body-molecule lifetime measured in cloud radii",
        "TAU_SOURCE_SEPARATION_over_TAU_SHAPE": fp_src / tau_shape_intrinsic,
        "READING": ("the source moves one cloud radius in about %.0f steps while the cloud "
                    "needs about %.0f steps to relax its shape. The source is therefore NOT "
                    "quasi-static on the cloud's own timescale: chi = %.2f cloud radii per "
                    "molecule lifetime. This is why the relative kernel, with a_rel = a_X + "
                    "a_Y, is the correct transport operator and why a static-source profile "
                    "would misdescribe the cloud." % (fp_src, tau_shape_intrinsic, chi)),
        "STATUS": "SOURCE_IS_NOT_QUASI_STATIC" if chi > 1 else "SOURCE_IS_QUASI_STATIC",
    }

    mu_family = ["TAU_LIFETIME", "TAU_MASS_ON", "TAU_SHAPE", "TAU_FOLLOW", "TAU_SOURCE_OFF",
                 "TAU_TURNOVER"]
    vals = [TAU[k]["value"] for k in mu_family]
    # every timescale, expressed in units of 1/mu_X
    in_units = {k: TAU[k]["value"] * mu for k in TAU}
    in_units["TAU_SHAPE.TORUS_VARIANT"] = tau_shape_torus * mu
    collapse = {
        "TIMESCALES_DRIVEN_BY_mu_X_ALONE": mu_family,
        "values": {k: TAU[k]["value"] for k in mu_family},
        "spread_max_over_min": max(vals) / min(vals),
        "ALL_EIGHT_IN_UNITS_OF_ONE_OVER_mu": in_units,
        "THE_STRONGER_STATEMENT": (
            "it is not six of eight. Every radius that appears naturally in this system is a "
            "multiple of the localisation length, and ell^2 = D/mu_X by definition, so every "
            "natural first passage r^2/(4D) is itself a multiple of 1/mu_X. At the qualified "
            "point core_R = 2 ell_X exactly and both first passages reduce to 1/(2 mu_X). "
            "SEVEN of the eight timescales are therefore fixed rational multiples of 1/mu_X, "
            "and the eighth -- the torus mode -- is a property of the domain, not of the "
            "cloud. The qualified point has ONE timescale."),
        "SEVEN_ARE_MULTIPLES_OF_ONE_OVER_mu": {
            k: round(v, 6) for k, v in in_units.items() if k != "TAU_SHAPE.TORUS_VARIANT"},
        "THE_ONLY_ESCAPE": (
            "a radius fixed in LATTICE units rather than in cloud radii. Since ell_X = %.1f "
            "sites, the discrete corrections are O(1/r) and reach %.0f %% at r = ell_rel, so "
            "the lattice is the one source of a genuinely independent number here -- and it is "
            "a geometric artefact, not a dynamical scale." % (
                ell_X, 100 * (fp_src / (ell_rel ** 2 / (4 * D_Y)) - 1))),
        "GENUINELY_INDEPENDENT_DIMENSIONLESS_NUMBERS": {
            "ell_X_in_lattice_sites": ell_X, "L_over_ell_relative": L / ell_rel,
            "chi": chi,
            "note": "all three are geometry or a ratio of transport constants; none is a time"},
        "DEGREES_OF_FREEDOM_AS_TIMESCALES": 1,
        "WHY_THIS_MATTERS": (
            "an experiment that observes these timescales agreeing has learned nothing: at "
            "fixed mu_X the agreement cannot fail, because it is arithmetic. Any claim that "
            "formation, relaxation, turnover and first passage 'separate' or 'coincide' in "
            "this LawSpec is a statement about the choice of parameters, not about the system."),
        "CONSEQUENCE_FOR_ANY_FUTURE_DESIGN": (
            "separating the timescales requires moving mu_X and p_hop INDEPENDENTLY, so that "
            "ell_X changes in lattice units. Moving along the curve ell = sqrt(D/mu) = const "
            "changes nothing this section can distinguish, and neither does changing L, which "
            "moves only the torus mode."),
    }

    out = {"SECTION": "OBTR01 §10-§11",
           "QUALIFIED_CONSTANTS": {"L": L, "mu_X": mu, "q": q, "a_X": a_X, "D_X": D_X,
                                   "a_relative": a_rel, "D_relative": D_rel, "D_Y": D_Y,
                                   "ell_X": ell_X, "ell_relative": ell_rel,
                                   "core_radius_cells": core_R},
           "EIGHT_TIMESCALES": TAU, "RELATIONS": R, "COHERENCE": coherence,
           "TIMESCALE_COLLAPSE": collapse,
           "FROZEN_CROSS_CHECK": {
               "frozen_source_off_e_folding": an.get("source_off_e_folding_steps"),
               "rederived_here": tau_source_off,
               "MATCHES": abs(tau_source_off
                              - float(an.get("source_off_e_folding_steps", 0))) < 1e-9,
               "frozen_optimal_lag": an.get("optimal_lag_steps"),
               "rederived_TAU_FOLLOW": tau_follow,
               "LAG_MATCHES": abs(tau_follow - float(an.get("optimal_lag_steps", 0))) < 1e-9,
               "frozen_ell_relative": an.get("ell_relative"), "rederived_ell_relative": ell_rel,
               "ELL_MATCHES": abs(ell_rel - float(an.get("ell_relative", 0))) < 1e-12}}
    json.dump(out, open(f"{OUT}/_timescales.json", "w"), indent=1, default=str)

    print("%-24s %12s   %s" % ("TIMESCALE", "steps", "driven by"))
    print("-" * 78)
    for k, v in TAU.items():
        print("%-24s %12.4f   %s" % (k, v["value"], v["driven_by"]))
    print("%-24s %12.4f   %s" % ("  TAU_SHAPE.torus", tau_shape_torus, "L and a_rel"))
    print()
    print("RELATIONS")
    for r in R:
        print("  %-22s vs %-22s ratio %10.6f   %s"
              % (r["left"], r["right"], r["ratio"], r["CLASSIFICATION"]))
    print()
    print("COHERENCE  chi = %.4f  ->  %s" % (chi, coherence["STATUS"]))
    print("  source moves one cloud radius in %.1f steps; cloud relaxes in %.1f"
          % (fp_src, tau_shape_intrinsic))
    print("  survival to the core radius %.4f ; to ell_rel %.4f" % (surv_core, surv_ell))
    print()
    print("COLLAPSE   the six mu-driven timescales spread by only %.3f %%"
          % (100 * (collapse["spread_max_over_min"] - 1)))
    print("           in units of 1/mu_X:")
    for k, v in collapse["ALL_EIGHT_IN_UNITS_OF_ONE_OVER_mu"].items():
        print("             %-28s %.6f" % (k, v))
    print("           timescale degrees of freedom at the qualified point: %d"
          % collapse["DEGREES_OF_FREEDOM_AS_TIMESCALES"])
    print()
    f = out["FROZEN_CROSS_CHECK"]
    print("cross-check against the frozen analytic block: source-off %s, lag %s, ell %s"
          % (f["MATCHES"], f["LAG_MATCHES"], f["ELL_MATCHES"]))


if __name__ == "__main__":
    main()
