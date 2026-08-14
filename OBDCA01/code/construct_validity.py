"""OBDCA01 §10 — construct validity of |C - Y|.

Four independent probes, none of which starts the engine:

  10.1  the finite-sample error of the Frechet centre, derived and then checked numerically
  10.2  a synthetic assay built from the FROZEN source-transport law with NO domain effect at
        all, evaluated on a grid of imposed molecule counts
  10.3  raw-only downsampling of the REAL recorded fields
  10.4  a null in which the latent mechanism is strictly L-invariant and only the OBSERVED
        per-size population distributions are injected
  10.5  diagnostic conditional analyses

Everything here is diagnostic. None of it revises the frozen result.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

WC = "/home/claude/OBDCA01/verify/obdi02/wc"
OUT = "/home/claude/OBDCA01/out"
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")

import metrics_obtc as M       # noqa: E402
import nulls_obtc as NU        # noqa: E402
import protocol_obtc02 as PC   # noqa: E402
import source_operator as OP   # noqa: E402
import yaml                    # noqa: E402

SIZES = (36, 72, 96)


def wd(d, L):
    d = np.abs(np.asarray(d, float)) % L
    return np.minimum(d, L - d)


def slope(x, y, w):
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    xb = float((w * x).sum() / w.sum())
    sxx = float((w * (x - xb) ** 2).sum())
    return float((w * (x - xb) * y).sum() / sxx), float(sxx ** -0.5)


def fit_beta(vals_by_L, pred):
    x, y, w = [], [], []
    for L in SIZES:
        v = np.asarray([q for q in vals_by_L[L] if np.isfinite(q) and q > 0], float)
        if len(v) < 2:
            continue
        lv = np.log(v)
        x.append(math.log(L))
        y.append(float(lv.mean()) - math.log(pred[L]))
        w.append(len(v) / max(float(lv.std(ddof=1)), 1e-12) ** 2)
    if len(x) < 2:
        return float("nan")
    return slope(x, y, w)[0]


# ================================================================= 10.1
def part_10_1(per_arm):
    """E||C_hat - C*||^2 = tr(Sigma)/N for the empirical mean of N iid positions. On the torus
    the Frechet centre coincides with the empirical mean whenever the cloud does not wrap, and
    Rg^2 (the centre-free pairwise radius of gyration) EQUALS tr(Sigma). Both facts are checked
    numerically below rather than assumed."""
    rng = np.random.default_rng(11)
    # (i) does Rg^2 equal tr(Sigma) for the recorded fields?
    checks = []
    for tag in ("L36__seed8100000", "L72__seed8101000", "L96__seed8102000"):
        z = np.load(f"{WC}/OBDI02/raw/{tag}.npz", allow_pickle=True)
        f = z["nX_final"]
        L = f.shape[0]
        if f.sum() < 20:
            continue
        ys, xs = np.nonzero(f)
        cnt = f[ys, xs]
        pts = np.repeat(np.stack([ys, xs], 1), cnt, axis=0).astype(float)
        cy, cx = M.frechet_centre(f)
        dy = wd(pts[:, 0] - cy, L)
        dx = wd(pts[:, 1] - cx, L)
        tr_sigma = float((dy ** 2 + dx ** 2).mean())
        rg = float(M.rg_pairwise(f))
        checks.append({"tag": tag, "L": L, "N": int(f.sum()), "Rg_pairwise": rg,
                       "Rg_squared": rg ** 2, "tr_Sigma_about_the_centre": tr_sigma,
                       "ratio": rg ** 2 / tr_sigma})
    # (ii) Rice law: |C_hat - Y| when C* - Y has modulus mu and the centre error has per-axis
    #      sigma^2 = tr(Sigma) / (2 N)
    def rice_mean(mu, s):
        if s <= 0:
            return mu
        x = mu * mu / (2 * s * s)
        # Laguerre L_{1/2}(-x) via a stable series / asymptote
        if x < 30:
            k = np.arange(0, 200)
            terms = np.exp(k * np.log(max(x, 1e-300)) - np.array(
                [math.lgamma(i + 1) for i in k]))
            l12 = float((terms * np.array([math.gamma(1.5) / (math.gamma(1.5 - i)
                                                              * math.gamma(i + 1))
                                           if 1.5 - i > 0 else 0.0 for i in k])).sum()) \
                if False else None
        # numerically: E|Z| for Z ~ N((mu,0), s^2 I) by quadrature
        g = np.linspace(-8, 8, 2001)
        wgt = np.exp(-0.5 * g ** 2)
        wgt /= wgt.sum()
        a = mu + s * g[:, None]
        b = s * g[None, :]
        return float((np.sqrt(a ** 2 + b ** 2) * (wgt[:, None] * wgt[None, :])).sum())

    mu = 3.1239                                   # operator prediction of the true offset
    rg_typ = float(np.median([p["Rg"] for p in per_arm if np.isfinite(p["Rg"])]))
    curve = {}
    for N in (3, 5, 10, 20, 40, 60, 80, 100, 121, 160):
        s = math.sqrt(rg_typ ** 2 / (2.0 * N))
        curve[N] = {"sigma_per_axis": s, "E_abs_C_minus_Y": rice_mean(mu, s),
                    "inflation_vs_large_N": rice_mean(mu, s) / rice_mean(mu, math.sqrt(
                        rg_typ ** 2 / (2.0 * 1e6)))}
    del rng
    return {
        "DERIVATION": ("for N molecules drawn from a distribution with covariance Sigma, the "
                       "empirical mean has E||C_hat - C*||^2 = tr(Sigma)/N. On the torus the "
                       "Frechet centre coincides with the empirical mean while the cloud does "
                       "not wrap. The centre-free pairwise radius of gyration satisfies "
                       "Rg^2 = tr(Sigma), so the per-axis error of the centre is "
                       "sigma = Rg / sqrt(2 N)."),
        "STATUS": "EXACT FOR THE EMPIRICAL MEAN OF IID POSITIONS; APPROXIMATE FOR THE FRECHET "
                  "CENTRE ON A TORUS, AND ONLY WHILE THE CLOUD DOES NOT WRAP. It is NOT claimed "
                  "exact: the numerical checks below are what support it.",
        "ADDITIONAL_TERMS_NOT_MODELLED": [
            "temporal autocorrelation: successive frames are not independent, so the effective "
            "N over a window is not the number of molecules times the number of frames",
            "multimodality: with several components the Frechet centre is not near any of them",
            "the halo: the outer mass has larger leverage on the centre than the core",
            "lattice rounding of the centre, worth 1/12 per axis",
            "toroidal wrap, which breaks the mean-centre correspondence entirely"],
        "Rg_SQUARED_EQUALS_TR_SIGMA_CHECK": checks,
        "TYPICAL_Rg_USED": rg_typ, "TRUE_OFFSET_USED": mu,
        "E_ABS_C_MINUS_Y_BY_N": curve,
        "READING": ("at the typical population N = 121 the centre error inflates the measured "
                    "offset by %.1f %%; at N = 10 by %.1f %%; at N = 5 by %.1f %%. The metric "
                    "therefore rises when the population falls, with no change whatever in the "
                    "underlying attachment."
                    % (100 * (curve[121]["inflation_vs_large_N"] - 1),
                       100 * (curve[10]["inflation_vs_large_N"] - 1),
                       100 * (curve[5]["inflation_vs_large_N"] - 1)))}


# ================================================================= 10.2
def part_10_2(op, n_draws=600):
    """A synthetic assay with NO domain effect: the same source-transport law, the same
    organiser, the same Frechet centre, the same per-seed summary, and molecule counts imposed
    on a grid. Any dependence on L that appears here is an artefact of the measurement."""
    grid = [3, 5, 8, 12, 20, 30, 50, 80, 110, 140]
    res = {}
    for L in SIZES:
        per_N = {}
        for N in grid:
            rng = np.random.default_rng(900000 + 97 * L + N)
            d = np.empty(n_draws)
            for i in range(n_draws):
                f, org = NU.n2_generative(rng, L, N, op.qX, op.qY, op.mu)
                cy, cx = M.frechet_centre(f)
                d[i] = float(np.hypot(wd(cy - org[0], L), wd(cx - org[1], L)))
            per_N[N] = {"mean": float(d.mean()), "sd": float(d.std(ddof=1)),
                        "median": float(np.median(d)), "q90": float(np.quantile(d, 0.9))}
        res[L] = per_N
    # at fixed N the three sizes must agree: that is the assay's own control
    control = {N: {"means": [res[L][N]["mean"] for L in SIZES],
                   "max_relative_spread": float(
                       (max(res[L][N]["mean"] for L in SIZES)
                        - min(res[L][N]["mean"] for L in SIZES))
                       / np.mean([res[L][N]["mean"] for L in SIZES]))} for N in grid}
    return {"grid": grid, "draws_per_cell": n_draws, "by_L_and_N": res,
            "CONTROL_AT_FIXED_N": control,
            "NOTE": ("the assay contains no domain effect by construction: the same law is used "
                     "at every L. The control shows the residual spread between sizes at fixed "
                     "N, which is the assay's own noise floor.")}


# ================================================================= 10.3
def part_10_3(per_arm, n_rep=200):
    """Raw-only downsampling of the REAL recorded fields. The geometry, the source and the
    organiser are the ones the engine actually produced; only the number of molecules is
    reduced."""
    rng = np.random.default_rng(4242)
    targets = [3, 5, 8, 12, 20, 30, 50, 80]
    rows, used = [], []
    for p in per_arm:
        tag, L = p["tag"], p["L"]
        z = np.load(f"{WC}/OBDI02/raw/{tag.replace('/', '__')}.npz", allow_pickle=True)
        f, fy = z["nX_final"], z["nY_final"]
        N = int(f.sum())
        if N < 100 or int(fy.sum()) < 1:
            continue
        used.append({"tag": tag, "L": L, "N_full": N})
        ys, xs = np.nonzero(f)
        pts = np.repeat(np.stack([ys, xs], 1), f[ys, xs], axis=0).astype(int)
        oy, ox = [int(v[0]) for v in np.nonzero(fy)]
        cy0, cx0 = M.frechet_centre(f)
        d_full = float(np.hypot(wd(cy0 - oy, L), wd(cx0 - ox, L)))
        for T in targets:
            if T >= N:
                continue
            dd = np.empty(n_rep)
            for r in range(n_rep):
                idx = rng.choice(N, size=T, replace=False)
                g = np.zeros_like(f)
                np.add.at(g, (pts[idx, 0], pts[idx, 1]), 1)
                cy, cx = M.frechet_centre(g)
                dd[r] = float(np.hypot(wd(cy - oy, L), wd(cx - ox, L)))
            rows.append({"tag": tag, "L": L, "N_full": N, "N_sub": T,
                         "d_full": d_full, "mean_d_sub": float(dd.mean()),
                         "sd_d_sub": float(dd.std(ddof=1)),
                         "mean_displacement_of_the_centre": float(np.mean(
                             np.abs(dd - d_full))),
                         "inflation": float(dd.mean() / max(d_full, 1e-9))})
        if len(used) >= 24:
            break
    agg = {}
    for T in targets:
        r = [x for x in rows if x["N_sub"] == T]
        if r:
            agg[T] = {"n_arms": len(r), "mean_d_sub": float(np.mean([x["mean_d_sub"]
                                                                     for x in r])),
                      "mean_d_full": float(np.mean([x["d_full"] for x in r])),
                      "mean_inflation": float(np.mean([x["inflation"] for x in r])),
                      "mean_abs_displacement": float(np.mean(
                          [x["mean_displacement_of_the_centre"] for x in r]))}
    return {"arms_used": used, "n_arms_used": len(used), "replicates": n_rep,
            "targets": targets, "rows": rows, "AGGREGATE_BY_N": agg,
            "NOTE": "diagnostic only; the real geometry and the real source are preserved and "
                    "only the molecule count is reduced"}


# ================================================================= 10.4
def part_10_4(per_arm, assay, pred, n_rep=4000):
    """A null in which the latent mechanism is strictly invariant with L. Each simulated arm
    draws its population from the OBSERVED per-size distribution and its measured offset from
    the assay's conditional law at that population. If beta = 0.0822 is common here, the
    observed coefficient carries no information about L."""
    rng = np.random.default_rng(20260814)
    obs_N = {L: np.array([p["N_X_mean"] for p in per_arm if p["L"] == L
                          and p["N_X_mean"] > 0], float) for L in SIZES}
    n_arms = {L: int(sum(1 for p in per_arm if p["L"] == L)) for L in SIZES}
    grid = np.array(assay["grid"], float)

    def draw_offset(L, N):
        """conditional mean and sd interpolated on the assay grid, log-normal draw"""
        gm = np.array([assay["by_L_and_N"][L][int(g)]["mean"] for g in grid])
        gs = np.array([assay["by_L_and_N"][L][int(g)]["sd"] for g in grid])
        m = float(np.interp(N, grid, gm))
        s = float(np.interp(N, grid, gs))
        sig = math.sqrt(math.log1p((s / m) ** 2))
        mu = math.log(m) - 0.5 * sig * sig
        return float(rng.lognormal(mu, sig))

    betas = np.empty(n_rep)
    for r in range(n_rep):
        vals = {}
        for L in SIZES:
            k = n_arms[L]
            Ns = rng.choice(obs_N[L], size=k, replace=True)
            vals[L] = [draw_offset(L, float(N)) for N in Ns]
        betas[r] = fit_beta(vals, pred)
    b_obs = 0.0821948795
    p_ge = float(np.mean(betas >= b_obs))
    return {"replicates": n_rep, "observed_beta": b_obs,
            "null_mean": float(np.nanmean(betas)), "null_sd": float(np.nanstd(betas, ddof=1)),
            "null_quantiles": {q: float(np.nanquantile(betas, q))
                               for q in (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)},
            "P_beta_ge_observed": p_ge,
            "observed_N_X_distributions": {str(L): {"n": len(obs_N[L]),
                                                    "mean": float(obs_N[L].mean()),
                                                    "median": float(np.median(obs_N[L])),
                                                    "q10": float(np.quantile(obs_N[L], .1)),
                                                    "min": float(obs_N[L].min())}
                                           for L in SIZES},
            "CLASSIFICATION": ("typical" if p_ge > 0.25 else
                               ("plausible" if p_ge > 0.05 else
                                ("rare" if p_ge > 0.005 else "incompatible"))),
            "NOTE": ("the latent offset is IDENTICAL at every L by construction. Only the "
                     "observed population distributions differ between sizes. Any beta produced "
                     "here is pure measurement artefact.")}


# ================================================================= 10.5
def part_10_5(per_arm, pred):
    """Diagnostic conditional analyses. None of these is confirmatory."""
    rows = [p for p in per_arm if np.isfinite(p["summary_CY_route2"])
            and p["summary_CY_route2"] > 0 and p["N_X_mean"] > 0]
    y = np.array([math.log(p["summary_CY_route2"]) - math.log(pred[p["L"]]) for p in rows])
    xL = np.array([math.log(p["L"]) for p in rows])
    xN = np.array([math.log(p["N_X_mean"]) for p in rows])

    def ols(X, y):
        XtX = X.T @ X
        b = np.linalg.solve(XtX, X.T @ y)
        r = y - X @ b
        s2 = float(r @ r) / (len(y) - X.shape[1])
        cov = s2 * np.linalg.inv(XtX)
        return b, np.sqrt(np.diag(cov))

    X1 = np.column_stack([np.ones_like(xL), xL])
    b1, se1 = ols(X1, y)
    X2 = np.column_stack([np.ones_like(xL), xL, xN])
    b2, se2 = ols(X2, y)
    X3 = np.column_stack([np.ones_like(xL), xL, xN, xN ** 2])
    b3, se3 = ols(X3, y)

    # population-band restriction, defined on a threshold independent of the outcome
    band = [p for p in rows if p["N_X_mean"] >= 60]
    vb = {L: [p["summary_CY_route2"] for p in band if p["L"] == L] for L in SIZES}
    beta_band = fit_beta(vb, pred)

    # per-size medians of the arm summaries
    med = {L: float(np.median([p["summary_CY_route2"] for p in rows if p["L"] == L]))
           for L in SIZES}
    xs = np.array([math.log(L) for L in SIZES])
    ym = np.array([math.log(med[L]) - math.log(pred[L]) for L in SIZES])
    beta_med = float(((xs - xs.mean()) * ym).sum() / ((xs - xs.mean()) ** 2).sum())

    # leave-one-out influence on the frozen estimator
    base = fit_beta({L: [p["summary_CY_route2"] for p in rows if p["L"] == L] for L in SIZES},
                    pred)
    infl = []
    for i, p in enumerate(rows):
        keep = rows[:i] + rows[i + 1:]
        b = fit_beta({L: [q["summary_CY_route2"] for q in keep if q["L"] == L] for L in SIZES},
                     pred)
        infl.append({"tag": p["tag"], "L": p["L"], "N_X_mean": p["N_X_mean"],
                     "summary": p["summary_CY_route2"], "beta_without_it": b,
                     "delta_beta": b - base})
    infl.sort(key=lambda r: abs(r["delta_beta"]), reverse=True)

    corr = float(np.corrcoef(xN, np.array([math.log(p["summary_CY_route2"]) for p in rows]))[0, 1])
    return {
        "n_arms": len(rows),
        "model_L_only": {"beta_L": float(b1[1]), "se": float(se1[1])},
        "model_L_plus_logN": {"beta_L": float(b2[1]), "se_beta_L": float(se2[1]),
                              "coef_logN": float(b2[2]), "se_logN": float(se2[2]),
                              "t_logN": float(b2[2] / se2[2])},
        "model_L_plus_logN_quadratic": {"beta_L": float(b3[1]), "se_beta_L": float(se3[1])},
        "restricted_to_N_X_mean_ge_60": {"n_arms": len(band), "beta": beta_band,
                                         "n_by_L": {str(L): len(vb[L]) for L in SIZES}},
        "per_size_medians": {str(L): med[L] for L in SIZES},
        "beta_from_the_medians": beta_med,
        "corr_logN_log_offset": corr,
        "influence_top10": infl[:10],
        "max_abs_delta_beta_from_one_arm": float(abs(infl[0]["delta_beta"])) if infl else None,
        "NOTE": "post hoc, diagnostic, never confirmatory",
    }


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    rec = json.load(open(f"{OUT}/_recompute.json"))
    per_arm = rec["PER_ARM"]
    pred = {L: float(spec["predictions"][str(L)]["organiser_to_core"]) for L in SIZES}
    op = OP.Op(PC.spec_for(36))

    print("10.1 finite-sample error of the centre ...", flush=True)
    p1 = part_10_1(per_arm)
    print("10.2 synthetic assay conditioned on N_X ...", flush=True)
    p2 = part_10_2(op)
    print("10.3 raw-only downsampling ...", flush=True)
    p3 = part_10_3(per_arm)
    print("10.4 null with the observed population distributions ...", flush=True)
    p4 = part_10_4(per_arm, p2, pred)
    print("10.5 conditional diagnostics ...", flush=True)
    p5 = part_10_5(per_arm, pred)

    out = {"SECTION": "OBDCA01 §10", "FINITE_CENTRE_ERROR": p1, "SYNTHETIC_ASSAY": p2,
           "DOWNSAMPLING": p3, "POPULATION_NULL": p4, "CONDITIONAL_DIAGNOSTICS": p5}
    json.dump(out, open(f"{OUT}/_construct_validity.json", "w"), indent=1, default=str)

    print("\n10.1  Rg^2 vs tr(Sigma) ratios:",
          [round(c["ratio"], 4) for c in p1["Rg_SQUARED_EQUALS_TR_SIGMA_CHECK"]])
    print("      E|C-Y| by N :", {k: round(v["E_abs_C_minus_Y"], 3)
                                  for k, v in p1["E_ABS_C_MINUS_Y_BY_N"].items()})
    print("10.2  assay E|C-Y| at L=36/72/96 for N=5 :",
          [round(p2["by_L_and_N"][L][5]["mean"], 3) for L in SIZES],
          " for N=110 :", [round(p2["by_L_and_N"][L][110]["mean"], 3) for L in SIZES])
    print("      control max relative spread at fixed N:",
          {k: round(v["max_relative_spread"], 4) for k, v in p2["CONTROL_AT_FIXED_N"].items()})
    print("10.3  downsampling, %d real arms:" % p3["n_arms_used"])
    for T, v in p3["AGGREGATE_BY_N"].items():
        print("        N_sub=%-4d mean |C-Y| %.3f (full %.3f)  inflation x%.3f  "
              "mean centre displacement %.3f"
              % (T, v["mean_d_sub"], v["mean_d_full"], v["mean_inflation"],
                 v["mean_abs_displacement"]))
    print("10.4  null beta: mean %+.5f sd %.5f  q95 %+.5f q99 %+.5f   P(beta >= %.4f) = %.4f "
          "-> %s" % (p4["null_mean"], p4["null_sd"], p4["null_quantiles"][0.95],
                     p4["null_quantiles"][0.99], p4["observed_beta"], p4["P_beta_ge_observed"],
                     p4["CLASSIFICATION"]))
    print("10.5  beta_L alone %+.5f ; with log N_X %+.5f (t_logN = %.2f) ; band N>=60 %+.5f ; "
          "from medians %+.5f ; corr %.3f"
          % (p5["model_L_only"]["beta_L"], p5["model_L_plus_logN"]["beta_L"],
             p5["model_L_plus_logN"]["t_logN"], p5["restricted_to_N_X_mean_ge_60"]["beta"],
             p5["beta_from_the_medians"], p5["corr_logN_log_offset"]))
    print("      most influential arm:", p5["influence_top10"][0]["tag"],
          "delta beta %+.5f" % p5["influence_top10"][0]["delta_beta"])


if __name__ == "__main__":
    main()
