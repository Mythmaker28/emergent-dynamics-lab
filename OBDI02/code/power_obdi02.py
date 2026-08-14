"""OBDI02 §9 — power analysis centred on the estimand that actually failed, |C - Y|.

The OBDI01 arms are used ONLY as historical design data: their per-size dispersion of the
frozen per-seed summary. No OBDI01 arm enters any OBDI02 outcome.

Two things are computed for every candidate n:

  ANALYTIC   power = 2 * Phi(delta / se(beta) - c) - 1 under beta = 0, with se(beta) from the
             design matrix and the assumed per-size coefficient of variation.

  SIMULATED  the whole pipeline is replayed: per-size arm summaries are drawn, the frozen
             estimator is applied, the frozen TOST rule is evaluated. The simulation ALSO
             propagates the uncertainty of the historical variance estimates — the per-size CV
             is itself drawn from its chi-square sampling law given the OBDI01 degrees of
             freedom — because sizing a design on a variance estimated from four arms and
             pretending it is known is exactly the error that produced OBDI01.
"""
from __future__ import annotations

import json
import math

import numpy as np
import yaml

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"
SIZES = (36, 72, 96)
STAT = "organiser_to_core"
DRAWS = 20000
ALPHA_TOST = 0.05                       # one-sided level of each of the two one-sided tests
EXTINCTION_P = None                     # measured below from the whole mission chain


def z_one_sided(a):
    lo, hi = 0.0, 12.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if 1.0 - 0.5 * (1.0 + math.erf(m / math.sqrt(2.0))) > a:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def design_se(cv_by_L, n_by_L):
    """se of the WLS slope of log(mean summary) on log L, with var(log mean_L) = cv_L^2 / n_L."""
    x = np.array([math.log(L) for L in SIZES])
    w = np.array([n_by_L[L] / cv_by_L[L] ** 2 for L in SIZES], float)
    xb = (w * x).sum() / w.sum()
    return float(1.0 / math.sqrt((w * (x - xb) ** 2).sum()))


def analytic_power(delta, cv, n, c):
    se = design_se(cv, {L: n for L in SIZES})
    if se <= 0:
        return 1.0, 0.0
    return max(0.0, 2.0 * phi(delta / se - c) - 1.0), se


def simulate(delta, cv_hat, df, n, c, beta_true=0.0, draws=DRAWS, seed=1,
             propagate_variance=True, p_ext=0.0):
    """Full-pipeline simulation, including estimation of the per-size sd from the arms
    themselves and, optionally, the historical uncertainty of the assumed CV."""
    rng = np.random.default_rng(seed)
    x = np.array([math.log(L) for L in SIZES])
    ok = 0
    n_eff_log = []
    for _ in range(draws):
        cv = {}
        for L in SIZES:
            if propagate_variance:
                # the true CV is unknown; draw it from the sampling law of the historical sd
                s2 = cv_hat[L] ** 2 * df[L] / rng.chisquare(df[L])
                cv[L] = math.sqrt(s2)
            else:
                cv[L] = cv_hat[L]
        ys, ws, nn = [], [], []
        for L in SIZES:
            k = n
            if p_ext > 0:
                k = int(rng.binomial(n, 1.0 - p_ext))
                if k < 2:
                    k = 2
            mu = beta_true * math.log(L)
            v = rng.normal(mu, cv[L], size=k)            # log-scale arm summaries
            m = float(v.mean())
            s = float(v.std(ddof=1))
            ys.append(m)
            ws.append(k / max(s, 1e-9) ** 2)
            nn.append(k)
        ys, ws = np.array(ys), np.array(ws)
        xb = (ws * x).sum() / ws.sum()
        sxx = (ws * (x - xb) ** 2).sum()
        b = (ws * (x - xb) * ys).sum() / sxx
        se = 1.0 / math.sqrt(sxx)
        if abs(b) + c * se <= delta:
            ok += 1
        n_eff_log.append(sum(nn))
    return ok / draws, float(np.mean(n_eff_log))


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI01/code/obdi01_protocol.yaml"))
    A = json.load(open(f"{WC}/OBDI01/out/_arms.json"))
    au = json.load(open(f"{OUT}/_equivalence_audit.json"))
    frozen_margin = au["MARGIN_DISCREPANCY"]["THE_FROZEN_PROTOCOL_STATES"]
    mandate_margin = au["MARGIN_DISCREPANCY"]["MANDATE_STATES_THE_FROZEN_MARGIN_IS"]
    c = z_one_sided(ALPHA_TOST)                       # 1.6449 : the 90 % two-sided interval

    # ---------------------------------------------------------------- historical dispersion
    hist = {}
    for L in SIZES:
        v = np.array([a["summary"][STAT] for a in A if a["L"] == L
                      and np.isfinite(a["summary"][STAT])], float)
        lv = np.log(v)
        hist[L] = {"n_arms": int(len(v)), "mean": float(v.mean()),
                   "sd_raw": float(v.std(ddof=1)),
                   "cv_raw": float(v.std(ddof=1) / v.mean()),
                   "sd_of_log": float(lv.std(ddof=1)), "df": int(len(v) - 1)}
    cv_hat = {L: hist[L]["sd_of_log"] for L in SIZES}
    df = {L: hist[L]["df"] for L in SIZES}
    cv_max = max(cv_hat.values())
    cv_worst = {L: cv_max for L in SIZES}

    # extinction rate across the whole chain, used as a design input, never as an outcome
    ext = {"OBTC02_P_L36": (1, 6), "OBDI01_L36": (0, 5), "OBDI01_L72": (1, 5),
           "OBDI01_L96": (0, 5)}
    n_ext = sum(a for a, _ in ext.values())
    n_tot = sum(b for _, b in ext.values())
    p_ext = n_ext / n_tot

    # ---------------------------------------------------------------- the curve
    grid = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 70, 85, 100, 120, 150, 200, 260]
    curve = {}
    for n in grid:
        pa_opt, se_opt = analytic_power(mandate_margin, cv_hat, n, c)
        pa_wst, se_wst = analytic_power(mandate_margin, cv_worst, n, c)
        curve[n] = {
            "se_beta_optimistic_heteroscedastic": se_opt,
            "se_beta_conservative_homoscedastic": se_wst,
            "analytic_power_delta_0.042_optimistic": pa_opt,
            "analytic_power_delta_0.042_conservative": pa_wst,
            "analytic_power_delta_0.25_conservative":
                analytic_power(frozen_margin, cv_worst, n, c)[0],
        }
    # simulation only where it matters, it is expensive
    for n in (10, 15, 20, 25, 30, 40, 50, 60, 70, 85, 100, 120, 150, 200, 260):
        curve[n]["simulated_power_delta_0.042"] = simulate(
            mandate_margin, cv_hat, df, n, c, 0.0, draws=4000, seed=100 + n,
            propagate_variance=True, p_ext=p_ext)[0]
        curve[n]["simulated_power_delta_0.25"] = simulate(
            frozen_margin, cv_hat, df, n, c, 0.0, draws=4000, seed=200 + n,
            propagate_variance=True, p_ext=p_ext)[0]

    def smallest(key, target=0.90):
        for n in grid:
            if curve[n].get(key, 0.0) >= target:
                return n
        return None

    n_req_042 = smallest("simulated_power_delta_0.042")
    n_req_025 = smallest("simulated_power_delta_0.25")

    # ---------------------------------------------------------------- error rates and edges
    n_probe = n_req_042 or 260
    err = {
        "type_I_at_the_boundary_beta_eq_delta": simulate(
            mandate_margin, cv_hat, df, n_probe, c, mandate_margin, draws=8000, seed=11,
            p_ext=p_ext)[0],
        "type_I_at_beta_eq_minus_delta": simulate(
            mandate_margin, cv_hat, df, n_probe, c, -mandate_margin, draws=8000, seed=12,
            p_ext=p_ext)[0],
        "power_at_beta_0": simulate(mandate_margin, cv_hat, df, n_probe, c, 0.0, draws=8000,
                                    seed=13, p_ext=p_ext)[0],
        "power_at_beta_half_delta": simulate(mandate_margin, cv_hat, df, n_probe, c,
                                             0.5 * mandate_margin, draws=8000, seed=14,
                                             p_ext=p_ext)[0],
        "wrongly_declares_equivalence_under_H_sublinear_beta_0.5": simulate(
            mandate_margin, cv_hat, df, n_probe, c, 0.5, draws=4000, seed=15, p_ext=p_ext)[0],
        "wrongly_declares_equivalence_under_H_linear_beta_1.0": simulate(
            mandate_margin, cv_hat, df, n_probe, c, 1.0, draws=4000, seed=16, p_ext=p_ext)[0],
    }

    # ---------------------------------------------------------------- cost
    SEC = {36: 29.0, 72: 60.0, 96: 92.0}                # measured in OBDI01
    cost = {n: sum(SEC[L] * n for L in SIZES) for n in grid}

    out = {
        "SECTION": "OBDI02 §9",
        "ESTIMAND": "beta_CY, the log-log slope of the arm-level median of |C - Y| divided by "
                    "the operator's exact finite-size prediction",
        "PER_SEED_SUMMARY": "median over the in-window frames — INHERITED FROM OBDI01, not "
                            "re-chosen; see _summary_choice.json for the comparison that "
                            "justified keeping it",
        "FORMULA": ("se(beta) = [ sum_L w_L (log L - xbar_w)^2 ]^(-1/2)  with  "
                    "w_L = n_L / cv_L^2 ; power = 2 Phi(delta/se - c) - 1 under beta = 0 ; "
                    "c = z_(1-alpha) = %.4f for alpha = %.2f one-sided, i.e. the 90 %% "
                    "two-sided interval a TOST at 5 %% requires" % (c, ALPHA_TOST)),
        "ASSUMPTIONS": [
            "the seed is the independent unit; the 180 frames of an arm produce one number",
            "the per-size dispersion of log(summary) is the OBDI01 realised one, and its own "
            "sampling uncertainty is propagated through a chi-square draw on df = n_arms - 1",
            "extinctions occur independently at the chain-wide historical rate and remove an "
            "arm from the conditional analysis",
            "the source-bound model sets beta = 0 exactly: the prediction divided out already "
            "carries the finite-size correction",
        ],
        "HISTORICAL_DISPERSION": hist,
        "cv_of_log_by_L": cv_hat, "cv_conservative_used": cv_max,
        "EXTINCTION_RATE_USED": {"events": ext, "extinct": n_ext, "arms": n_tot, "p": p_ext},
        "MARGINS": {"mandate_margin": mandate_margin, "obdi01_frozen_margin": frozen_margin},
        "critical_value_c": c, "tost_alpha_one_sided": ALPHA_TOST,
        "POWER_CURVE": curve,
        "REQUIRED_N_PER_SIZE": {"delta_0.042": n_req_042, "delta_0.25": n_req_025,
                                "target_power": 0.90},
        "ERROR_RATES_AT_THE_REQUIRED_N": {"n_per_size": n_probe, **err},
        "COST_SECONDS_BY_N": cost,
        "COST_AT_REQUIRED_N": {"delta_0.042": cost.get(n_req_042),
                               "delta_0.25": cost.get(n_req_025)},
    }
    json.dump(out, open(f"{OUT}/_power.json", "w"), indent=1, default=str)

    print("historical dispersion of log |C-Y| by L (arm level)")
    for L in SIZES:
        print("  L=%-3d n=%d  mean=%.4f  sd(log)=%.4f  cv=%.4f  df=%d"
              % (L, hist[L]["n_arms"], hist[L]["mean"], hist[L]["sd_of_log"],
                 hist[L]["cv_raw"], hist[L]["df"]))
    print("\nextinction rate used in the design: %d/%d = %.4f" % (n_ext, n_tot, p_ext))
    print("c = %.4f (90 %% two-sided interval, TOST at alpha = 0.05 one-sided)\n" % c)
    print("%-5s %-10s %-11s %-11s %-11s %-11s %s"
          % ("n/L", "se(beta)", "an.0.042", "sim.0.042", "an.0.25", "sim.0.25", "cost"))
    for n in grid:
        v = curve[n]
        print("%-5d %-10.5f %-11.4f %-11s %-11.4f %-11s %.0f s"
              % (n, v["se_beta_optimistic_heteroscedastic"],
                 v["analytic_power_delta_0.042_optimistic"],
                 ("%.4f" % v["simulated_power_delta_0.042"])
                 if "simulated_power_delta_0.042" in v else "-",
                 v["analytic_power_delta_0.25_conservative"],
                 ("%.4f" % v["simulated_power_delta_0.25"])
                 if "simulated_power_delta_0.25" in v else "-",
                 cost[n]))
    print("\nsmallest n per size for 90 %% power:  delta=0.042 -> %s    delta=0.25 -> %s"
          % (n_req_042, n_req_025))
    print("error rates at n = %d per size:" % n_probe)
    for k, v in err.items():
        print("   %-58s %.4f" % (k, v))


if __name__ == "__main__":
    main()
