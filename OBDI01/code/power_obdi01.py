"""OBDI01 §13-§14 — variance decomposition, pre-freeze power analysis, and the deterministic
choice of the third domain size.

Uses ALL relevant OBTC02 arms, passing or not. "Relevant" means: a live cloud produced under
the UNMODIFIED law. That is P/seed9102..9106 (L=36) and D/seed9501..9503 (L=72) — the latter
including the two arms that FAILED the legacy gate. Excluded, with reasons recorded:
  P/seed9101  extinct, no cloud to measure;
  S/*         p_hop_Y = 0, a DIFFERENT law, so its variance is not the variance of this design;
  R/*         the source is removed at step 4000, so the window is not stationary;
  N/*         no organiser, no cloud.

No engine start.
"""
from __future__ import annotations

import json

import numpy as np

RAW = "/home/claude/OBDI01/verify/obtc02/wc/OBTC02/raw"
OUT = "/home/claude/OBDI01/out"
BURN_IN = 2000
STATS = ("Rg", "r80", "r80_organiser", "organiser_to_core")
RELEVANT = {36: ["P__seed9102", "P__seed9103", "P__seed9104", "P__seed9105", "P__seed9106"],
            72: ["D__seed9501", "D__seed9502", "D__seed9503"]}
EXCLUDED = {"P__seed9101": "extinct: no cloud to measure",
            "S__*": "p_hop_Y = 0 is a different law; its variance is not this design's",
            "R__*": "the source is removed at step 4000; the window is not stationary",
            "N__*": "no organiser and no cloud"}
ALPHA_FAMILY = 0.05
THIRD_POOL = (96, 108, 144)
M2_DEFICIT_NEGLIGIBLE = 1e-3      # frozen threshold for "the torus correction is negligible"


def frames(tag):
    z = np.load(f"{RAW}/{tag}.npz", allow_pickle=True)
    return [json.loads(s) for s in z["frames"] if json.loads(s)["step"] > BURN_IN]


def lag1(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 3 or x.std() == 0:
        return 0.0
    return float(np.clip(np.corrcoef(x[:-1], x[1:])[0, 1], -0.99, 0.99))


def n_eff(n, rho):
    """Effective sample size of a stationary AR(1)-like series for the mean."""
    return float(n * (1.0 - rho) / (1.0 + rho))


def se_of_median(rng, x, block=10, draws=1500):
    """Standard error of the ARM SUMMARY actually used (the median of the frame series),
    obtained by a block bootstrap that preserves the observed short-range dependence. This
    replaces the sd/sqrt(n_eff) proxy, which is the SE of the MEAN and would not be comparable
    with a median-based between-seed spread."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    nb = int(np.ceil(n / block))
    out = np.empty(draws)
    for d in range(draws):
        st = rng.integers(0, n, size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]) % n
        out[d] = np.median(x[idx.ravel()[:n]])
    return float(out.std(ddof=1))


def main():
    P = json.load(open(f"{OUT}/_predictions.json"))
    rng = np.random.default_rng(20260814)
    per = {}
    for L, tags in RELEVANT.items():
        for t in tags:
            fr = frames(t)
            d = {"L": L, "n_frames": len(fr)}
            for s in STATS:
                v = np.array([f.get(s, np.nan) for f in fr], float)
                v = v[np.isfinite(v)]
                rho = lag1(v)
                d[s] = {"median": float(np.median(v)), "mean": float(v.mean()),
                        "sd_within": float(v.std(ddof=1)), "rho1": rho,
                        "n_eff": n_eff(len(v), rho),
                        "se_of_arm_mean": float(v.std(ddof=1) / np.sqrt(n_eff(len(v), rho))),
                        "se_of_arm_median": se_of_median(rng, v)}
            nx = np.array([f["N_X"] for f in fr], float)
            d["N_X"] = {"mean": float(nx.mean()), "sd_within": float(nx.std(ddof=1)),
                        "rho1": lag1(nx)}
            d["winding_frames"] = int(sum(1 for f in fr if f["any_winding"]))
            per[t] = d

    # ---------------- variance decomposition: between-seed vs within-arm --------------------
    decomp = {}
    for s in STATS:
        by_L = {}
        for L, tags in RELEVANT.items():
            m = np.array([per[t][s]["median"] for t in tags])
            wi = np.array([per[t][s]["se_of_arm_median"] for t in tags])
            v_obs = float(m.var(ddof=1)) if len(m) > 1 else float("nan")
            v_wi = float((wi ** 2).mean())
            by_L[L] = {"arm_summary": "median over the 180 in-window frames",
                       "arm_values": m.tolist(), "n_arms": len(m),
                       "variance_of_arm_summaries": v_obs,
                       "mean_within_arm_sampling_variance": v_wi,
                       "between_seed_variance": max(v_obs - v_wi, 0.0),
                       "between_seed_sd": float(np.sqrt(max(v_obs - v_wi, 0.0))),
                       "total_sd_of_one_arm": float(np.sqrt(v_obs)),
                       "reading": ("a between-seed variance of 0 means NOT RESOLVABLE at this "
                                   "arm count — the arm-to-arm scatter is already accounted "
                                   "for by the within-arm sampling error — it does not mean "
                                   "the seeds are identical")}
        # pooled across L: the design uses the SAME law at every L, so a common sd is the
        # honest pre-freeze assumption; the larger of the two is taken, never the smaller.
        sds = [by_L[L]["total_sd_of_one_arm"] for L in by_L]
        decomp[s] = {"by_L": by_L, "pooled_sd_used": float(max(sds)),
                     "rule": "the LARGER of the observed per-L arm-level sd is used, so the "
                             "power calculation is conservative"}

    # ---------------- power ----------------------------------------------------------------
    # Under H_bound the predicted arm-level value at L is the operator's own finite-size
    # prediction. Under an alternative with exponent alpha the value is scaled by (L/36)^alpha.
    pred = {int(k): {"Rg": v["SAMPLED"]["Rg"]["mean"], "r80": v["SAMPLED"]["r80"]["mean"],
                     "r80_organiser": v["SAMPLED"]["r80_organiser"]["mean"],
                     "organiser_to_core": v["SAMPLED"]["organiser_to_core"]["mean"],
                     "m2_deficit": v["EXACT_KERNEL"]["periodic_image_correction"][
                         "relative_deficit"]}
            for k, v in P["per_L"].items()}

    def power(third, n_per_L, alt_alpha, stat="Rg", alpha_family=ALPHA_FAMILY):
        """Probability that the simultaneous region rejects H_bound when the truth has
        exponent alt_alpha. Normal approximation on the arm-level mean at each L; the family
        is the K = 3 domain sizes x the statistics actually gated, Sidak-corrected."""
        Ls = [36, 72, third]
        K = len(Ls)
        per_test = 1.0 - (1.0 - alpha_family) ** (1.0 / K)
        c = float(-np.sqrt(2) * _erfinv(per_test - 1.0)) if per_test < 1 else 0.0
        sd = decomp[stat]["pooled_sd_used"]
        det = 1.0
        for L in Ls:
            mu0 = pred[L][stat]
            mu1 = pred[36][stat] * (L / 36.0) ** alt_alpha
            se = sd / np.sqrt(n_per_L)
            delta = abs(mu1 - mu0) / se
            # P(|Z + delta| <= c) : probability this single test does NOT reject
            p_accept = 0.5 * (_erf((c - delta) / np.sqrt(2)) + _erf((c + delta) / np.sqrt(2)))
            det *= p_accept
        return 1.0 - det, c, per_test

    def _erf(x):
        return float(np.vectorize(_erf_scalar)(x)) if np.ndim(x) else _erf_scalar(x)

    def _erf_scalar(x):
        import math
        return math.erf(x)

    def _erfinv(y):
        # bisection: robust and dependency-free
        lo, hi = -10.0, 10.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if _erf_scalar(mid) < y:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    # smallest n giving >= 80 % power against H_linear (alpha = 1)
    n_power = None
    for n in range(1, 21):
        pw, _, _ = power(96, n, 1.0, "Rg")
        if pw >= 0.80:
            n_power = n
            break
    # estimability floor: the between-seed sd must itself be estimable to <= 40 % relative se
    n_est = min(n for n in range(2, 41) if 1.0 / np.sqrt(2.0 * (n - 1)) <= 0.40)
    n_adopted = max(n_power or 1, n_est)

    # ---------------- third domain size ----------------------------------------------------
    third_eval = {}
    for L in THIRD_POOL:
        pw_lin, c, per_test = power(L, n_adopted, 1.0, "Rg")
        pw_sub, _, _ = power(L, n_adopted, 0.5, "Rg")
        cost = 58.0 * (L / 72.0) ** 1.1 * n_adopted        # seconds, from the OBTC02 timings
        third_eval[str(L)] = {
            "power_vs_H_linear": pw_lin, "power_vs_H_sublinear": pw_sub,
            "m2_deficit": pred[L]["m2_deficit"],
            "torus_correction_negligible": bool(pred[L]["m2_deficit"]
                                                <= M2_DEFICIT_NEGLIGIBLE),
            "estimated_cost_seconds": cost, "cost_affordable": bool(cost <= 3600),
            "L_over_ell_relative": L / P["constants"]["ell_relative"],
            "L_over_r80_predicted": L / pred[L]["r80_organiser"],
            "ELIGIBLE": bool(pw_lin >= 0.80
                             and pred[L]["m2_deficit"] <= M2_DEFICIT_NEGLIGIBLE
                             and cost <= 3600)}
    eligible = [L for L in THIRD_POOL if third_eval[str(L)]["ELIGIBLE"]]
    third = min(eligible) if eligible else None

    underpowered = n_power is None
    out = {
        "SECTION": "OBDI01 §13-§14",
        "ARMS_USED": {str(L): tags for L, tags in RELEVANT.items()},
        "ARMS_EXCLUDED_WITH_REASON": EXCLUDED,
        "NOTE_ON_ARM_SELECTION": ("two of the three L=72 arms FAILED the legacy D gate and are "
                                  "nevertheless included: the mandate requires all relevant "
                                  "arms, not only the passing ones, precisely so that the "
                                  "variance is not underestimated by conditioning on success"),
        "per_arm": per,
        "variance_decomposition": decomp,
        "POWER_RULE": ("smallest n per domain size giving >= 80 % power against H_linear at a "
                       "family-wise level of 5 % under H_bound; if no n <= 20 achieves it, "
                       "DOMAIN_TEST_UNDERPOWERED"),
        "n_from_power": n_power,
        "ESTIMABILITY_FLOOR_RULE": ("the between-seed sd must itself be estimable with a "
                                    "relative standard error <= 40 pct, i.e. 1/sqrt(2(n-1)) "
                                    "<= 0.40; this is a SEPARATE requirement, stated openly, "
                                    "because the power rule alone would allow n = %s"
                                    % n_power),
        "n_from_estimability": int(n_est),
        "SEEDS_PER_DOMAIN_SIZE": int(n_adopted),
        "DOMAIN_TEST_UNDERPOWERED": bool(underpowered),
        "THIRD_DOMAIN_RULE": ("the SMALLEST candidate in {96, 108, 144} that simultaneously "
                              "(a) reaches >= 80 %% power against H_linear, (b) has a "
                              "second-moment periodic-image deficit <= %.0e, and (c) costs "
                              "under one hour of engine time in total"
                              % M2_DEFICIT_NEGLIGIBLE),
        "third_domain_evaluation": third_eval,
        "THIRD_DOMAIN_SIZE": third,
        "DOMAIN_SIZES": [36, 72, third],
        "TOTAL_CONFIRMATORY_ARMS": int(3 * n_adopted),
    }
    json.dump(out, open(f"{OUT}/_power.json", "w"), indent=1, default=str)

    print("variance decomposition (arm-level summaries)")
    for s in STATS:
        for L in (36, 72):
            b = decomp[s]["by_L"][L]
            print("  %-18s L=%-3d n=%d  sd_arm=%.4f  within=%.4f  between=%.4f"
                  % (s, L, b["n_arms"], b["total_sd_of_one_arm"],
                     np.sqrt(b["mean_within_arm_sampling_variance"]), b["between_seed_sd"]))
    print("\nn from power vs H_linear = %s ; estimability floor = %d ; ADOPTED n = %d"
          % (n_power, n_est, n_adopted))
    for L in THIRD_POOL:
        e = third_eval[str(L)]
        print("  L=%-4d power(H_linear)=%.4f power(H_sublinear)=%.4f  m2_deficit=%.2e (%s)  "
              "cost=%.0fs  ELIGIBLE=%s"
              % (L, e["power_vs_H_linear"], e["power_vs_H_sublinear"], e["m2_deficit"],
                 "negligible" if e["torus_correction_negligible"] else "NOT negligible",
                 e["estimated_cost_seconds"], e["ELIGIBLE"]))
    print("THIRD_DOMAIN_SIZE = %s   DOMAIN_SIZES = %s   arms = %d"
          % (third, out["DOMAIN_SIZES"], out["TOTAL_CONFIRMATORY_ARMS"]))


if __name__ == "__main__":
    main()
