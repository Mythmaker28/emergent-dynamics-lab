"""OBDI01 §11-§13 — the four scaling hypotheses, the parameter-free finite-size predictions
at every candidate domain size, and the deterministic choice of the third domain size.

STATUS DISCIPLINE (kept separate throughout, never merged):

  UNBLOCKED_DISCRETE_KERNEL      = EXACT
      the stationary profile of the source-transport-decay operator on the L x L torus,
      obtained by DFT inversion of n_hat(k) = 1 / (1 - (1-mu) phi(k)). No approximation, no
      continuum limit, no fitted constant.

  SAMPLED_CLOUD_STATISTICS      = EXACT_LAW__MONTE_CARLO_EVALUATION
      statistics that are functionals of a FINITE sample drawn from that exact law (radius of
      gyration about the cloud's own Frechet centre, r80 in the cloud frame, winding of the
      support). The law is exact; only its functional is evaluated by sampling, and the Monte
      Carlo error is reported.

  FULL_CAPACITY_CONSTRAINED_OPERATOR = APPROXIMATE_WITH_EMPIRICAL_ERROR
      the engine also refuses hops into full cells. The refusal rate is MEASURED in OBTC02 and
      quoted as an empirical error term. It is NOT converted into a rigorous bound.

No engine start anywhere in this file.
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import metrics_obtc as M          # noqa: E402
import nulls_obtc as NU           # noqa: E402
import protocol_obtc02 as PC      # noqa: E402
import source_operator as OP      # noqa: E402

OUT = "/home/claude/OBDI01/out"
CANDIDATES = (36, 72, 96, 108, 144)
MANDATORY = (36, 72)
THIRD_POOL = (96, 108, 144)
L_REF = 1024                      # stand-in for the infinite lattice: mass beyond L/2 < 1e-300
N2_DRAWS = 3000
CORE_R = 3.0

# ---------------------------------------------------------------- OBTC02 empirical anchors
RES = json.load(open("/home/claude/OBDI01/verify/obtc02/wc/OBTC02/out/_results.json"))
HEALTHY_P = ["P/seed9102", "P/seed9103", "P/seed9104", "P/seed9105", "P/seed9106"]
D_ARMS = ["D/seed9501", "D/seed9502", "D/seed9503"]


def arms(tags):
    return [a for a in RES["arms"] if a["tag"] in tags]


HYPOTHESES = {
    "H_bound": {
        "statement": "the cloud has an intrinsic size fixed by the operator; as L grows the "
                     "radius converges to its infinite-lattice value and the population stays "
                     "constant, so the DENSITY falls as 1/L^2",
        "r_of_L": "r(L) -> r_inf, with a computable finite-L correction from the periodic "
                  "images; exponent alpha = d log r / d log L -> 0",
        "alpha": 0.0, "density_exponent": -2.0,
        "winding_frequency": "-> 0 super-exponentially in L",
        "predicted_by": "the frozen source-transport-decay operator, no free parameter"},
    "H_linear": {
        "statement": "the cloud is a fixed fraction of the domain: it has no intrinsic size and "
                     "simply rescales with the box",
        "r_of_L": "r(L) = c L, alpha = 1", "alpha": 1.0, "density_exponent": 0.0,
        "winding_frequency": "bounded away from 0",
        "predicted_by": "none: it is the alternative the domain axis must exclude"},
    "H_sublinear": {
        "statement": "the cloud grows without bound but more slowly than the box",
        "r_of_L": "r(L) = c L^alpha with 0 < alpha < 1; the reference sub-case is the diffusive "
                  "alpha = 1/2", "alpha": 0.5, "density_exponent": -1.0,
        "winding_frequency": "-> 0 but only polynomially",
        "predicted_by": "none: an unbounded-but-slower alternative"},
    "H_fill": {
        "statement": "the cloud occupies the whole torus: the population scales with the area, "
                     "the density is constant and winding becomes typical",
        "r_of_L": "r(L) -> the radius of a uniform distribution on the torus, alpha = 1",
        "alpha": 1.0, "density_exponent": 0.0,
        "winding_frequency": "-> 1",
        "predicted_by": "none: the failure mode the NO_GLOBAL_FILLING condition guards"},
}


def uniform_torus_radii(L, qs=(0.5, 0.8, 0.9)):
    """The H-fill reference: r_q of a uniform distribution on the L x L torus, measured about
    a point. Exact by enumeration of the toroidal distance field."""
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2).ravel()
    d.sort()
    return {q: float(d[int(np.floor(q * (len(d) - 1)))]) for q in qs}


def exact_block(op, L, ref):
    """UNBLOCKED_DISCRETE_KERNEL = EXACT."""
    stat, rel = op.static_profile(L), op.relative_profile(L)
    rs, rr = op._radii(stat), op._radii(rel)
    m2s, m2r = op._second_moment(stat), op._second_moment(rel)
    return {
        "STATUS": "EXACT",
        "static_source": {"r50": rs[0.5], "r80": rs[0.8], "r90": rs[0.9],
                          "second_moment": m2s, "rms": float(np.sqrt(m2s))},
        "organiser_frame": {"r50": rr[0.5], "r80": rr[0.8], "r90": rr[0.9],
                            "second_moment": m2r, "rms": float(np.sqrt(m2r))},
        "mass_beyond_L_over_2": float(op._tail_mass(rel)),
        "mass_beyond_reference_radius_12.8": float(_mass_beyond(rel, 12.8)),
        "periodic_image_correction": {
            "reference_L": L_REF,
            "second_moment_at_L": m2r, "second_moment_at_reference": ref["m2r"],
            "relative_deficit": (ref["m2r"] - m2r) / ref["m2r"],
            "r80_at_L": rr[0.8], "r80_at_reference": ref["r80r"],
            "r80_relative_deficit": (ref["r80r"] - rr[0.8]) / ref["r80r"],
            "meaning": "the torus truncates the tail of the exact profile; under H_bound the "
                       "measured radius must therefore INCREASE slightly with L and saturate, "
                       "not stay exactly constant. This correction is a prediction, not a "
                       "nuisance.",
            "caveat": "r80 of the EXACT profile is a quantile over lattice distances and is "
                      "therefore quantised: it can be identical at two L although the "
                      "underlying profile differs. The SECOND MOMENT is the sensitive "
                      "finite-size probe and is the one used for the correction."},
        "L_over_ell_relative": L / op.ell_rel,
    }


def _mass_beyond(prof, r):
    L = prof.shape[0]
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    return float(prof[d > r].sum())


def _n2_full(n_draws, seed, L, N_X, op):
    """The frozen N2 sampler, but reporting the FULL frame — including the topological winding
    test and the organiser-frame radius, which `nulls_obtc.SHAPE` does not expose. The frozen
    module is called, never edited: only the reporting is widened here."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_draws):
        f, org = NU.n2_generative(rng, L, N_X, op.qX, op.qY, op.mu)
        fr, _ = M.frame(f, np.zeros_like(f), CORE_R)
        cy, cx = M.frechet_centre(f)
        fr["organiser_to_core"] = float(np.hypot(M.wdist1(org[0] - cy, L),
                                                 M.wdist1(org[1] - cx, L)))
        fr["r80_organiser"] = M.radii(f, org[0], org[1])[0.8]
        rows.append(fr)
    keys = [k for k in rows[0] if isinstance(rows[0][k], (int, float, bool, np.integer,
                                                          np.floating, np.bool_))]
    return {k: np.array([float(r[k]) for r in rows], float) for k in keys}


def sampled_block(op, L, N_X, seed):
    """SAMPLED_CLOUD_STATISTICS = EXACT_LAW__MONTE_CARLO_EVALUATION.

    Draws are produced by the operator's own generative law (the N2 sampler): an organiser
    walking with the engine's rule, molecules born at it, walking with the engine's rule and
    dying at rate mu. Nothing realised is used, no parameter is fitted."""
    d = _n2_full(N2_DRAWS, seed, L, int(round(N_X)), op)
    keys = ("Rg", "r50", "r80", "r90", "r80_organiser", "organiser_to_core", "any_winding",
            "core_fraction", "main_mass_fraction", "n_eff_components", "legacy_extent_proxy",
            "geodesic_diameter", "n_components")
    out = {"STATUS": "EXACT_LAW__MONTE_CARLO_EVALUATION", "draws": N2_DRAWS, "N_X_used": int(N_X)}
    for k in keys:
        if k not in d:
            continue
        v = np.asarray(d[k], float)
        v = v[np.isfinite(v)]
        if not len(v):
            continue
        out[k] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                  "mc_standard_error": float(v.std(ddof=1) / np.sqrt(len(v))),
                  "median": float(np.median(v)),
                  "q025": float(np.quantile(v, 0.025)), "q975": float(np.quantile(v, 0.975)),
                  "q005": float(np.quantile(v, 0.005)), "q995": float(np.quantile(v, 0.995))}
    # winding: report the frequency and an exact Clopper-Pearson-free statement of resolution
    if "any_winding" in d:
        w = np.asarray(d["any_winding"], float)
        k = int(w.sum())
        out["true_winding_frequency"] = {
            "observed": k / len(w), "successes": k, "draws": int(len(w)),
            "upper_95_if_zero": 1.0 - 0.05 ** (1.0 / len(w)) if k == 0 else None,
            "note": "if zero windings are drawn, only an upper bound is available at this "
                    "Monte Carlo size; the bound is stated, not a point value"}
    return out


def empirical_block():
    """FULL_CAPACITY_CONSTRAINED_OPERATOR = APPROXIMATE_WITH_EMPIRICAL_ERROR."""
    aa = arms(HEALTHY_P + D_ARMS)
    bx = [a["blocked_fraction"]["X"] for a in aa]
    by = [a["blocked_fraction"]["Y"] for a in aa]
    return {
        "STATUS": "APPROXIMATE_WITH_EMPIRICAL_ERROR",
        "transport_rejection_X": {"min": float(min(bx)), "max": float(max(bx)),
                                  "mean": float(np.mean(bx)), "n_arms": len(bx)},
        "transport_rejection_Y": {"min": float(min(by)), "max": float(max(by)),
                                  "mean": float(np.mean(by))},
        "interpretation": ("the exact kernel assumes transport is never refused. In OBTC02 the "
                           "refusal rate for X was at most %.2e per offered hop. This is an "
                           "OBSERVED rate on the domains actually run, not a bound, and it is "
                           "NOT extrapolated to larger L: at larger L the occupancy density is "
                           "held constant by the chemostat, so the rate is expected to be of "
                           "the same order, and the new runs will measure it."
                           % max(bx)),
        "NOT_A_BOUND": True,
    }


def main():
    sp36 = PC.spec_for(36)
    op = OP.Op(sp36)
    relref = op.relative_profile(L_REF)
    ref = {"m2r": op._second_moment(relref), "r80r": op._radii(relref)[0.8],
           "r50r": op._radii(relref)[0.5], "r90r": op._radii(relref)[0.9]}

    # population anchor, measured, NOT predicted by the operator
    nx36 = [a["aggregates"]["N_X_mean"] for a in arms(HEALTHY_P)]
    nx72 = [a["aggregates"]["N_X_mean"] for a in arms(D_ARMS)]
    pop = {
        "STATUS": "MEASURED_ANCHOR__NOT_PREDICTED_BY_THE_OPERATOR",
        "reason": ("N_X_stationary = B / mu, and B is the mean accepted births per step at the "
                   "organiser, set by the LOCAL resource concentration and the LOCAL free "
                   "capacity. The chemostat holds the OCCUPANCY DENSITY constant, so B is "
                   "expected to be independent of L; that expectation is a PREDICTION of this "
                   "mission, not an input."),
        "L36_healthy_P": {"values": nx36, "mean": float(np.mean(nx36)),
                          "sd": float(np.std(nx36, ddof=1))},
        "L72_D": {"values": nx72, "mean": float(np.mean(nx72)),
                  "sd": float(np.std(nx72, ddof=1))},
        "observed_ratio_L72_over_L36": float(np.mean(nx72) / np.mean(nx36)),
        "H_bound_predicts_ratio": 1.0,
        "H_fill_predicts_ratio": 4.0,
    }
    N_X_ANCHOR = float(np.mean(nx36 + nx72))

    per_L = {}
    for i, L in enumerate(CANDIDATES):
        ex = exact_block(op, L, ref)
        sm = sampled_block(op, L, N_X_ANCHOR, 770000 + 13 * L)
        unif = uniform_torus_radii(L)
        per_L[str(L)] = {
            "L": L,
            "EXACT_KERNEL": ex,
            "SAMPLED": sm,
            "H_fill_reference": {"r50": unif[0.5], "r80": unif[0.8], "r90": unif[0.9],
                                 "note": "radii of a UNIFORM cloud on this torus: the H_fill "
                                         "target the observed radius must not approach"},
            "H_linear_reference_r80": ex["organiser_frame"]["r80"] * L / 36.0,
            "H_sublinear_reference_r80": ex["organiser_frame"]["r80"] * np.sqrt(L / 36.0),
            "expected_population_under_H_bound": N_X_ANCHOR,
            "expected_density_under_H_bound": N_X_ANCHOR / L ** 2,
            "L_over_ell_relative": L / op.ell_rel,
            "L_over_r80_predicted": L / ex["organiser_frame"]["r80"],
        }
        print("L=%-4d m2_deficit=%.3e  r80_org=%.4f  Rg_pred=%.4f+-%.4f  r80_cloud=%.4f  "
              "d2org=%.4f  wind=%.5f  tail>L/2=%.2e  L/ell=%.2f  L/r80=%.2f"
              % (L, ex["periodic_image_correction"]["relative_deficit"],
                 sm["r80_organiser"]["mean"], sm["Rg"]["mean"], sm["Rg"]["sd"],
                 sm["r80"]["mean"], sm["organiser_to_core"]["mean"],
                 sm.get("true_winding_frequency", {}).get("observed", float("nan")),
                 ex["mass_beyond_L_over_2"], L / op.ell_rel,
                 L / ex["organiser_frame"]["r80"]), flush=True)

    out = {"SECTION": "OBDI01 §11-§12",
           "STATUS_LAYERS": {
               "UNBLOCKED_DISCRETE_KERNEL": "EXACT",
               "SAMPLED_CLOUD_STATISTICS": "EXACT_LAW__MONTE_CARLO_EVALUATION",
               "FULL_CAPACITY_CONSTRAINED_OPERATOR": "APPROXIMATE_WITH_EMPIRICAL_ERROR"},
           "HYPOTHESES": HYPOTHESES,
           "constants": {"ell_X": op.ell_X, "ell_relative": op.ell_rel, "a_X": op.aX,
                         "a_Y": op.aY, "a_relative": op.a_rel, "mu_X": op.mu,
                         "q_X": op.qX, "q_Y": op.qY},
           "infinite_lattice_reference": ref,
           "population_anchor": pop, "N_X_anchor_used": N_X_ANCHOR,
           "capacity_error": empirical_block(),
           "per_L": per_L}
    json.dump(out, open(f"{OUT}/_predictions.json", "w"), indent=1, default=str)
    print("\nN_X anchor %.2f   ratio L72/L36 = %.4f  (H_bound 1.0, H_fill 4.0)"
          % (N_X_ANCHOR, pop["observed_ratio_L72_over_L36"]))


if __name__ == "__main__":
    main()
