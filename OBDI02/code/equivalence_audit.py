"""OBDI02 §6 — audit of the equivalence test OBDI01 actually performed, and resolution of the
margin discrepancy carried by the OBDI02 mandate.

Two things are established here, both from the delivered artefacts:

  (1) WHAT THE FROZEN MARGIN WAS. The mandate states the frozen equivalence margin is 0.042.
      The frozen protocol says 0.25. The number 0.042 is the EXCESS of the OBDI01 interval over
      that margin. The OBDI01 report's French sentence "son intervalle d'equivalence deborde la
      marge gelee de 0.042" is grammatically ambiguous between "exceeds the frozen margin BY
      0.042" (what was meant, and what the arithmetic says) and "exceeds the frozen margin OF
      0.042". This is a defect of the OBDI01 report's prose and it is recorded as such.

  (2) WHETHER THE METHOD WAS SOUND. Nine specific checks, then a verdict from the four the
      mandate allows.

Nothing here revises any OBDI01 number. The recomputations below are DIAGNOSTIC: they say what
a differently specified test would have produced on the same data, which is information about
the instrument, not a new verdict.
"""
from __future__ import annotations

import json
import math

import numpy as np
import yaml

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"
MANDATE_MARGIN = 0.042


def wls_slope(x, y, w):
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    sw = w.sum()
    xb = (w * x).sum() / sw
    sxx = (w * (x - xb) ** 2).sum()
    b = (w * (x - xb) * y).sum() / sxx
    return float(b), float(1.0 / math.sqrt(sxx))


def z(p):
    """two-sided (1-p) normal quantile by bisection."""
    lo, hi = 0.0, 12.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if 2.0 * (1.0 - 0.5 * (1.0 + math.erf(m / math.sqrt(2.0)))) > p:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI01/code/obdi01_protocol.yaml"))
    R = json.load(open(f"{WC}/OBDI01/out/_results.json"))
    A = json.load(open(f"{WC}/OBDI01/out/_arms.json"))
    po = spec["principal_outcome"]
    comp = R["PRINCIPAL"]["components"]
    d = comp["A_shape_invariance"]["by_statistic"]["organiser_to_core"]
    c_obdi01 = float(R["PRINCIPAL"]["critical_value_c"])
    frozen_margin = float(po["components"]["A_shape_invariance"]["margin"])
    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    pred = {L: float(spec["predictions"][str(L)]["organiser_to_core"]) for L in sizes}
    sd_prereg = float(spec["power"]["prereg_sd"]["organiser_to_core"])

    # ---------------------------------------------------------------- (1) the margin
    excess = d["abs_beta_plus_c_se"] - frozen_margin
    margin_finding = {
        "MANDATE_STATES_THE_FROZEN_MARGIN_IS": MANDATE_MARGIN,
        "THE_FROZEN_PROTOCOL_STATES": frozen_margin,
        "protocol_path": "principal_outcome.components.A_shape_invariance.margin",
        "protocol_justification": po["components"]["A_shape_invariance"][
            "margin_justification"],
        "spec_sha256_of_the_file_read": None,
        "WHERE_0_042_COMES_FROM": {
            "abs_beta_plus_c_se": d["abs_beta_plus_c_se"], "margin": frozen_margin,
            "excess": excess, "rounded": round(excess, 3),
            "identity": "0.2918 - 0.2500 = 0.0418 ~ 0.042"},
        "THE_AMBIGUOUS_SENTENCE": ("son intervalle d'equivalence deborde la marge gelee de "
                                   "0.042"),
        "READING_A": "exceeds the frozen margin BY 0.042  -> margin = 0.25   (arithmetically true)",
        "READING_B": "exceeds the frozen margin OF 0.042   -> margin = 0.042  (what the mandate read)",
        "WHICH_IS_CORRECT": "READING_A",
        "PROOF": ("0.042 cannot be the margin under which OBDI01 was evaluated: with a margin "
                  "of 0.042 the R_g component (|beta| + c.se = 0.0514) and the r80 component "
                  "(0.0862) would ALSO have failed, and OBDI01 reported them as passing. Only "
                  "a margin of 0.25 reproduces the reported verdict pattern PASS/PASS/FAIL."),
        "verdict_pattern_under_0_25": {
            s: (comp["A_shape_invariance"]["by_statistic"][s]["abs_beta_plus_c_se"] <= 0.25)
            for s in ("Rg", "r80", "organiser_to_core")},
        "verdict_pattern_under_0_042": {
            s: (comp["A_shape_invariance"]["by_statistic"][s]["abs_beta_plus_c_se"]
                <= MANDATE_MARGIN) for s in ("Rg", "r80", "organiser_to_core")},
        "DEFECT_OWNER": ("the OBDI01 report. Its French phrasing invited the misreading. This "
                         "is recorded as a reporting defect of OBDI01, not as an error of the "
                         "OBDI02 mandate."),
    }

    # ---------------------------------------------------------------- (2) nine checks
    per_L = d["per_L"]
    n_by_L = {L: per_L[str(L)]["n_arms"] for L in sizes}
    checks = {
        "was_it_a_TOST": {
            "answer": "NO — not in form, YES in logic",
            "detail": ("the frozen rule is |beta| + c.se(beta) <= delta, i.e. 'the whole "
                       "two-sided interval of half-width c.se lies inside +-delta'. That is "
                       "the confidence-interval formulation of a TOST, and it is exactly "
                       "equivalent to a TOST whose one-sided level is the tail beyond c. It is "
                       "not implemented as two one-sided t tests, and no p-value is produced.")},
        "interval_level": {
            "critical_value": c_obdi01,
            "two_sided_tail": float(po["multiplicity"]["per_test_alpha"]),
            "implied_interval": "%.2f %%" % (100 * (1 - po["multiplicity"]["per_test_alpha"])),
            "a_standard_TOST_at_alpha_0.05_uses": "a 90 pct two-sided interval, c = %.4f" % z(0.10),
            "ratio_of_half_widths": c_obdi01 / z(0.10),
            "answer": ("the interval used was 99.49 pct, not 90 pct. The half-width is %.2f times "
                       "that of a standard TOST at alpha = 0.05." % (c_obdi01 / z(0.10)))},
        "nominal_alpha": {
            "family_alpha": float(po["multiplicity"]["family_alpha"]),
            "per_test_alpha": float(po["multiplicity"]["per_test_alpha"]),
            "answer": ("nominal alpha = 0.05 FAMILY-WISE across K = %d tests, Sidak-corrected "
                       "to %.6f per test. OBDI01 itself recorded that an intersection-union "
                       "equivalence claim does NOT need that correction — and then applied it "
                       "anyway to the acceptance side."
                       % (po["multiplicity"]["K"], po["multiplicity"]["per_test_alpha"]))},
        "was_the_seed_the_independent_unit": {
            "answer": "YES",
            "detail": ("each arm contributes exactly one number (the median of its 180 frames) "
                       "and the standard error at each L is sd(arm medians)/sqrt(n_arms). No "
                       "frame count enters any variance.")},
        "were_frames_used_as_independent_observations": {
            "answer": "NO for the primary statistic",
            "detail": ("the only place a frame count enters a decision is component C, where "
                       "the observed count is exactly zero and no variance model is invoked. "
                       "Component D uses an envelope explicitly deflated to n_eff = 27 "
                       "independent frames precisely to avoid this error.")},
        "heteroscedasticity_between_sizes": {
            "answer": "ADDRESSED, THEN NEUTRALISED",
            "detail": ("weights w_L = (mean_L/se_L)^2 do model unequal variance, but the "
                       "frozen rule se_L = max(sd_realised, sd_prereg)/sqrt(n_L) replaced every "
                       "realised sd by the same pre-registered floor %.4f, so the weights "
                       "became nearly equal and the modelling had no effect." % sd_prereg),
            "sd_realised_by_L": {str(L): per_L[str(L)]["sd_realised"] for L in sizes},
            "sd_used_by_L": {str(L): per_L[str(L)]["sd_used"] for L in sizes},
            "floor_binding_everywhere": all(
                per_L[str(L)]["sd_used"] > per_L[str(L)]["sd_realised"] - 1e-12
                and per_L[str(L)]["sd_used"] == sd_prereg for L in sizes),
            "inflation_factor_by_L": {str(L): per_L[str(L)]["sd_used"]
                                      / per_L[str(L)]["sd_realised"] for L in sizes}},
        "raw_or_log_scale": {
            "answer": "LOG",
            "detail": "y = log(observed mean) - log(predicted), slope taken against log L"},
        "extinction_handling": {
            "answer": "NO PRE-SPECIFIED RULE",
            "detail": ("the gate filtered non-finite values with numpy.isfinite, which silently "
                       "dropped the extinct arm from the shape statistics while ADMITTING it "
                       "into the density statistic with the value 0. Two different implicit "
                       "treatments of the same event, neither of them declared."),
            "n_by_L": n_by_L, "planned_n": int(spec["domain"]["SEEDS_PER_SIZE"])},
        "balance_between_sizes": {
            "answer": "PLANNED BALANCED, REALISED UNBALANCED",
            "planned": "5 / 5 / 5", "realised": "%d / %d / %d" % tuple(n_by_L[L] for L in sizes)},
    }

    # ------------------------------------------------- diagnostic recomputations
    # (a) the frozen estimator, but with a standard TOST-90 interval
    xs = [math.log(L) for L in sizes]
    ys = [math.log(per_L[str(L)]["mean"]) - math.log(pred[L]) for L in sizes]
    w_frozen = [(per_L[str(L)]["mean"] / per_L[str(L)]["se_of_mean"]) ** 2 for L in sizes]
    b_f, se_f = wls_slope(xs, ys, w_frozen)
    # (b) same, with the REALISED sd instead of the pre-registered floor
    w_real = [(per_L[str(L)]["mean"]
               / (per_L[str(L)]["sd_realised"] / math.sqrt(per_L[str(L)]["n_arms"]))) ** 2
              for L in sizes]
    b_r, se_r = wls_slope(xs, ys, w_real)
    # (c) the arm as the unit: regression on all 15 points, HC-robust
    px, py = [], []
    for a in A:
        m = a["summary"]["organiser_to_core"]
        if np.isfinite(m):
            px.append(math.log(a["L"]))
            py.append(math.log(m) - math.log(pred[int(a["L"])]))
    px_a, py_a = np.array(px), np.array(py)
    xb = px_a.mean()
    sxx = ((px_a - xb) ** 2).sum()
    b_a = ((px_a - xb) * py_a).sum() / sxx
    resid = py_a - (py_a.mean() + b_a * (px_a - xb))
    se_hc = math.sqrt((((px_a - xb) ** 2) * resid ** 2).sum()) / sxx        # HC0
    dfree = len(px_a) - 2

    c90 = z(0.10)
    diag = {
        "LABEL": "DIAGNOSTIC ONLY — these do not revise the OBDI01 verdict",
        "frozen_estimator_frozen_interval": {
            "beta": d["beta"], "se": d["se"], "c": c_obdi01,
            "abs_beta_plus_c_se": d["abs_beta_plus_c_se"], "margin": frozen_margin,
            "PASS": bool(d["abs_beta_plus_c_se"] <= frozen_margin)},
        "frozen_estimator_TOST90_interval": {
            "beta": b_f, "se": se_f, "c": c90, "abs_beta_plus_c_se": abs(b_f) + c90 * se_f,
            "PASS_at_0.25": bool(abs(b_f) + c90 * se_f <= frozen_margin),
            "PASS_at_0.042": bool(abs(b_f) + c90 * se_f <= MANDATE_MARGIN)},
        "realised_variance_TOST90_interval": {
            "beta": b_r, "se": se_r, "c": c90, "abs_beta_plus_c_se": abs(b_r) + c90 * se_r,
            "PASS_at_0.25": bool(abs(b_r) + c90 * se_r <= frozen_margin),
            "PASS_at_0.042": bool(abs(b_r) + c90 * se_r <= MANDATE_MARGIN)},
        "arm_level_regression_HC0_TOST90": {
            "n_arms_used": int(len(px_a)), "df": dfree, "beta": float(b_a),
            "se_HC0": float(se_hc), "c": c90,
            "abs_beta_plus_c_se": float(abs(b_a) + c90 * se_hc),
            "PASS_at_0.25": bool(abs(b_a) + c90 * se_hc <= frozen_margin),
            "PASS_at_0.042": bool(abs(b_a) + c90 * se_hc <= MANDATE_MARGIN)},
        "reading": ("the frozen rule was conservative on three independent counts at once: a "
                    "99.49 %% interval instead of 90 %%, a variance floor that inflated every "
                    "standard error, and a multiplicity correction that an intersection-union "
                    "equivalence claim does not require. None of this makes the OBDI01 verdict "
                    "wrong — a conservative test that fails to establish equivalence has "
                    "failed to establish it. It makes the verdict UNINFORMATIVE about the "
                    "physics, which is exactly what DOMAIN_TEST_UNDERPOWERED records."),
    }

    verdict = "VALID_BUT_OVERCONSERVATIVE"
    out = {
        "SECTION": "OBDI02 §6",
        "MARGIN_DISCREPANCY": margin_finding,
        "NINE_CHECKS": checks,
        "DIAGNOSTIC_RECOMPUTATIONS": diag,
        "OBDI01_EQUIVALENCE_METHOD": verdict,
        "VERDICT_REASONING": (
            "the estimand is well defined and recoverable, the independent unit is the seed, "
            "the scale is logarithmic and the interval logic is a genuine equivalence rule. "
            "Nothing about it is MISALIGNED and nothing is UNRESOLVED. But the interval was "
            "built at 99.49 %% with a variance floor and a multiplicity correction that the "
            "claim did not need, so it could not have established equivalence at any plausible "
            "sample size. VALID_BUT_OVERCONSERVATIVE is the only one of the four allowed "
            "verdicts that fits."),
        "CONSEQUENCE_PER_MANDATE_SS6": (
            "the mandate provides that under this verdict the old endpoint stays SECONDARY and "
            "a correctly specified TOST may become primary on entirely fresh seeds, provided "
            "it is frozen before any run and presented as a targeted methodological redesign. "
            "OBDI02 takes that route."),
    }
    json.dump(out, open(f"{OUT}/_equivalence_audit.json", "w"), indent=1, default=str)

    print("MARGIN")
    print("  mandate says the frozen margin is        %.3f" % MANDATE_MARGIN)
    print("  the frozen protocol says                 %.3f" % frozen_margin)
    print("  0.042 is the EXCESS                      %.4f - %.4f = %.4f"
          % (d["abs_beta_plus_c_se"], frozen_margin, excess))
    print("  verdict pattern under 0.25               %s" % margin_finding[
        "verdict_pattern_under_0_25"])
    print("  verdict pattern under 0.042              %s" % margin_finding[
        "verdict_pattern_under_0_042"])
    print("\nNINE CHECKS")
    for k, v in checks.items():
        print("  %-42s %s" % (k, v["answer"]))
    print("\nDIAGNOSTIC (does not revise anything)")
    for k in ("frozen_estimator_frozen_interval", "frozen_estimator_TOST90_interval",
              "realised_variance_TOST90_interval", "arm_level_regression_HC0_TOST90"):
        v = diag[k]
        print("  %-38s beta=%+.4f se=%.4f  |b|+c.se=%.4f" % (k, v["beta"], v.get("se",
              v.get("se_HC0")), v["abs_beta_plus_c_se"]))
    print("\nOBDI01_EQUIVALENCE_METHOD = %s" % verdict)


if __name__ == "__main__":
    main()
