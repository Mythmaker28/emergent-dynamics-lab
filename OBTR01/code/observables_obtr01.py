"""OBTR01 §9 — population-robust observables for the organiser-bound cloud.

OBDCA01 proved that |C - Y| is population-confounded: C is an empirical centre of N molecules,
so E||C_hat - C*||^2 = tr(Sigma)/N and the Rice law makes E|C - Y| RISE as N falls, with no
change in the underlying mechanism. The mandate therefore forbids |C - Y| in any primary
outcome of this mission, and requires observables whose expectation does not move with N.

The design rule used here, stated once:

    a statistic is population-robust if it is a PER-PARTICLE MEAN, or an exactly debiased
    function of per-particle means. A simple random subsample of the molecules is then an
    unbiased estimator of the full-population value, EXACTLY and at every N, because the
    subsample mean of an exchangeable population is unbiased under sampling without
    replacement. Norms of noisy vectors are not of this form and are biased upward.

Each candidate is checked against that rule analytically, and then demonstrated on the REAL
recorded final fields of 171 arms by reducing only the molecule count and keeping the geometry,
the source and the organiser exactly as the engine produced them. |C - Y| and |m| are kept in
the demonstration as NEGATIVE CONTROLS, so the contrast is shown rather than asserted.

This section consumes no scientific run: it reads delivered trajectories only.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")
sys.path.insert(0, "/home/claude/OBTR01/code")

import metrics_obtc as M                                    # noqa: E402
from kernels_obtr01 import Operator                         # noqa: E402

# ---------------------------------------------------------------- pre-registered constants
RADIAL_GRID = (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 13.0)
PROFILE_WEIGHTS = tuple(1.0 for _ in RADIAL_GRID)
SUBSAMPLE_TARGETS = (3, 5, 8, 12, 20, 30, 50, 80, 120)
N_REPLICATES = 60
RNG_SEED = 20260814


def wd(d, L):
    d = np.abs(d) % L
    return np.minimum(d, L - d)


# ---------------------------------------------------------------- the observables
def observables(field, oy, ox, L, ref_cdf=None, u=None):
    """Every quantity here is computed from the molecule positions of ONE configuration."""
    ys, xs = np.nonzero(field)
    if len(ys) == 0:
        return None
    pts = np.repeat(np.stack([ys, xs], 1), field[ys, xs], axis=0).astype(float)
    N = len(pts)
    dy = wd(pts[:, 0] - oy, L)
    dx = wd(pts[:, 1] - ox, L)
    # signed toroidal offsets, needed for the directional statistic
    sy = ((pts[:, 0] - oy + L / 2) % L) - L / 2
    sx = ((pts[:, 1] - ox + L / 2) % L) - L / 2
    d2 = dy * dy + dx * dx
    d = np.sqrt(d2)

    out = {"N": N}
    # O1 --- mean per-particle squared distance to the SOURCE
    out["M2"] = float(d2.mean())
    # O2 --- source-centred radial distribution on the frozen grid
    out["F"] = [float((d <= r).mean()) for r in RADIAL_GRID]
    # O4 --- population
    out["N_X"] = N
    # O5 --- directional shift: a SIGNED projection of the mean offset, never its norm
    m = np.array([sy.mean(), sx.mean()])
    out["m"] = [float(m[0]), float(m[1])]
    if u is not None:
        u = np.asarray(u, float)
        nu = np.hypot(*u)
        out["P_projection"] = float(m @ u / nu) if nu > 0 else None
    # NEGATIVE CONTROLS, reported and never primary
    out["abs_m"] = float(np.hypot(*m))
    cy, cx = M.frechet_centre(field)
    out["abs_C_minus_Y"] = float(np.hypot(wd(cy - oy, L), wd(cx - ox, L)))
    # O3 --- debiased profile distance, only defined against a reference CDF
    if ref_cdf is not None:
        out["W2_plugin"] = float(sum(w * (f - g) ** 2 for w, f, g
                                     in zip(PROFILE_WEIGHTS, out["F"], ref_cdf)))
    return out


def debias_W2(F_sub, ref_cdf, n, N):
    """Cramer-von-Mises-type profile distance with the sampling variance removed EXACTLY.

    For a simple random subsample of size n drawn without replacement from N molecules with
    realised proportion p_N at radius r,
            E[F_n] = p_N ,   Var[F_n] = ((N - n)/(N - 1)) p_N (1 - p_N) / n
    so subtracting the unbiased variance estimate ((N-n)/(N-1)) F_n(1-F_n)/(n-1) from the
    squared deviation leaves an unbiased estimator of (p_N - F*)^2. No fit, no tuning."""
    if n < 2 or N < 2:
        return None
    fpc = (N - n) / (N - 1.0)
    tot = 0.0
    for w, f, g in zip(PROFILE_WEIGHTS, F_sub, ref_cdf):
        tot += w * ((f - g) ** 2 - fpc * f * (1.0 - f) / (n - 1.0))
    return float(tot)


# ---------------------------------------------------------------- reference profile
def reference_cdf(L, mu, q, mobile=True):
    """The operator's exact stationary radial CDF on the frozen grid, from the resolvent."""
    op = Operator(q, q if mobile else 0.0, mu, L)
    prof = op.stationary_profile()
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    dist = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    return [float(prof[dist <= r].sum()) for r in RADIAL_GRID]


# ---------------------------------------------------------------- the demonstration
def arms():
    for mission in ("OBTC02", "OBDI01", "OBDI02"):
        d = f"{WC}/{mission}/raw"
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if n.endswith(".npz"):
                yield mission, n, f"{d}/{n}"


def main():
    import yaml
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    q, mu = pt["p_hop"] / 4.0, pt["muX"]
    rng = np.random.default_rng(RNG_SEED)
    ref = {}

    rows, used, skipped = [], [], {"no_organiser": 0, "too_few_molecules": 0}
    for mission, name, path in arms():
        z = np.load(path, allow_pickle=True)
        f, fy = z["nX_final"], z["nY_final"]
        L = int(f.shape[0])
        N = int(f.sum())
        if int(fy.sum()) < 1:
            skipped["no_organiser"] += 1
            continue
        if N < 100:
            skipped["too_few_molecules"] += 1
            continue
        oy, ox = [int(v[0]) for v in np.nonzero(fy)]
        if L not in ref:
            ref[L] = reference_cdf(L, mu, q)
        # a direction fixed by the ORGANISER's own recent motion, never by the cloud
        u = None
        try:
            fr = [json.loads(str(s)) for s in z["frames"][-3:]]
            u = (((fr[-1]["organiser_y"] - fr[0]["organiser_y"] + L / 2) % L) - L / 2,
                 ((fr[-1]["organiser_x"] - fr[0]["organiser_x"] + L / 2) % L) - L / 2)
            if u[0] == 0 and u[1] == 0:
                u = None
        except Exception:
            u = None
        full = observables(f, oy, ox, L, ref[L], u)
        used.append({"mission": mission, "file": name, "L": L, "N": N})

        ys, xs = np.nonzero(f)
        pts = np.repeat(np.stack([ys, xs], 1), f[ys, xs], axis=0).astype(int)
        for T in SUBSAMPLE_TARGETS:
            if T >= N:
                continue
            acc = {k: [] for k in ("M2", "abs_m", "abs_C_minus_Y", "m_y", "m_x",
                                   "P_projection", "W2_plugin", "W2_debiased")}
            accF = []
            for _ in range(N_REPLICATES):
                idx = rng.choice(N, size=T, replace=False)
                g = np.zeros_like(f)
                np.add.at(g, (pts[idx, 0], pts[idx, 1]), 1)
                o = observables(g, oy, ox, L, ref[L], u)
                acc["M2"].append(o["M2"])
                acc["abs_m"].append(o["abs_m"])
                acc["abs_C_minus_Y"].append(o["abs_C_minus_Y"])
                acc["m_y"].append(o["m"][0])
                acc["m_x"].append(o["m"][1])
                if o.get("P_projection") is not None:
                    acc["P_projection"].append(o["P_projection"])
                acc["W2_plugin"].append(o["W2_plugin"])
                w2d = debias_W2(o["F"], ref[L], T, N)
                if w2d is not None:
                    acc["W2_debiased"].append(w2d)
                accF.append(o["F"])
            row = {"mission": mission, "file": name, "L": L, "N_full": N, "N_sub": T,
                   "full": {"M2": full["M2"], "abs_m": full["abs_m"],
                            "abs_C_minus_Y": full["abs_C_minus_Y"],
                            "m_y": full["m"][0], "m_x": full["m"][1],
                            "P_projection": full.get("P_projection"),
                            "W2_plugin": full["W2_plugin"],
                            "W2_debiased": debias_W2(full["F"], ref[L], N, N)},
                   "sub_mean": {k: (float(np.mean(v)) if v else None)
                                for k, v in acc.items()},
                   "F_full": full["F"],
                   "F_sub_mean": [float(np.mean([r[i] for r in accF]))
                                  for i in range(len(RADIAL_GRID))]}
            rows.append(row)

    # ---------------------------------------------------------------- aggregate
    def ratio_of_means(key, T, signed=False):
        r = [x for x in rows if x["N_sub"] == T
             and x["full"].get(key) is not None and x["sub_mean"].get(key) is not None]
        if not r:
            return None
        num = float(np.mean([x["sub_mean"][key] for x in r]))
        den = float(np.mean([x["full"][key] for x in r]))
        d = {"n_arms": len(r), "mean_sub": num, "mean_full": den}
        if signed:
            d["mean_absolute_difference"] = float(np.mean(
                [abs(x["sub_mean"][key] - x["full"][key]) for x in r]))
            d["mean_signed_difference"] = float(np.mean(
                [x["sub_mean"][key] - x["full"][key] for x in r]))
        else:
            d["ratio_of_means"] = num / den if abs(den) > 1e-12 else None
        return d

    agg = {}
    for key, signed in (("M2", False), ("abs_C_minus_Y", False), ("abs_m", False),
                        ("m_y", True), ("m_x", True), ("P_projection", True),
                        ("W2_plugin", False), ("W2_debiased", False)):
        agg[key] = {T: ratio_of_means(key, T, signed) for T in SUBSAMPLE_TARGETS}

    # the CDF itself, radius by radius, at the smallest target
    Tmin = SUBSAMPLE_TARGETS[0]
    rmin = [x for x in rows if x["N_sub"] == Tmin]
    cdf_check = [{"radius": RADIAL_GRID[i],
                  "F_full": float(np.mean([x["F_full"][i] for x in rmin])),
                  "F_sub": float(np.mean([x["F_sub_mean"][i] for x in rmin]))}
                 for i in range(len(RADIAL_GRID))] if rmin else []

    def verdict(key, tol):
        vals = [v["ratio_of_means"] for v in agg[key].values()
                if v and v.get("ratio_of_means") is not None]
        return bool(vals and max(abs(v - 1.0) for v in vals) <= tol)

    out = {
        "SECTION": "OBTR01 §9",
        "CONSUMES_NO_SCIENTIFIC_RUN": True,
        "FORBIDDEN_IN_ANY_PRIMARY_OUTCOME": "|C - Y|",
        "DESIGN_RULE": ("a statistic is population-robust if it is a per-particle mean, or an "
                        "exactly debiased function of per-particle means. Subsampling an "
                        "exchangeable population without replacement is then unbiased at every "
                        "N. Norms of noisy vectors are not of that form."),
        "PRE_REGISTERED_CONSTANTS": {
            "RADIAL_GRID": list(RADIAL_GRID), "PROFILE_WEIGHTS": list(PROFILE_WEIGHTS),
            "SUBSAMPLE_TARGETS": list(SUBSAMPLE_TARGETS), "N_REPLICATES": N_REPLICATES,
            "RNG_SEED": RNG_SEED,
            "note": "frozen in this file before the demonstration was run, and hashed into "
                    "METHODS_CORE at §22"},
        "OBSERVABLES": {
            "O1_M2": {
                "definition": "M2 = (1/N) sum_i [ wd(y_i - y_Y, L)^2 + wd(x_i - x_Y, L)^2 ]",
                "centre": "the ORGANISER cell, never an estimated centre",
                "why_robust": "a per-particle mean; unbiased under subsampling at every N",
                "role": "PRIMARY_CANDIDATE"},
            "O2_radial_distribution": {
                "definition": "F(r) = (1/N) sum_i 1[ d_i <= r ] on the frozen radial grid",
                "why_robust": "each F(r) is a per-particle mean",
                "caveat": "QUANTILES of F are nonlinear functionals and are NOT unbiased at "
                          "small N; the distribution on a fixed grid is registered, the "
                          "quantiles are not",
                "role": "PRIMARY_CANDIDATE"},
            "O3_profile_distance": {
                "definition": "W2 = sum_k w_k [ (F(r_k) - F*(r_k))^2 - FPC * F(1-F)/(n-1) ]",
                "reference": "F*, the operator's exact stationary radial CDF from the "
                             "resolvent, no free parameter",
                "why_robust": "the squared deviation carries a sampling variance that grows "
                              "like 1/N; the subtracted term removes it exactly, so the "
                              "estimator is unbiased for the full-population value",
                "caveat": "the finite-population correction is exact for subsampling. On a "
                          "real frame the molecules are spatially correlated, so the plug-in "
                          "correction is a LOWER bound on the true sampling variance and W2 "
                          "remains slightly conservative. Recorded, not hidden.",
                "role": "PRIMARY_CANDIDATE"},
            "O4_N_X": {"definition": "the number of X molecules in the frame",
                       "why_robust": "it IS the population; it is never a denominator and "
                                     "never divided out of another statistic",
                       "role": "PRIMARY_CANDIDATE_AND_COVARIATE"},
            "O5_directional_shift": {
                "definition": "P = < m , u > / |u| with m = (1/N) sum_i (X_i - Y) the mean "
                              "signed toroidal offset and u the ORGANISER's own displacement "
                              "over the preceding frames",
                "why_robust": "m is a per-particle mean and u does not depend on the cloud, so "
                              "E[P] is exactly linear in E[m]. A signed projection has no Rice "
                              "inflation, which is precisely the defect of a norm.",
                "role": "PRIMARY_CANDIDATE"},
            "NEGATIVE_CONTROL_abs_C_minus_Y": {
                "definition": "the toroidal distance from the Frechet centre to the organiser",
                "status": "FORBIDDEN_AS_PRIMARY", "role": "NEGATIVE_CONTROL"},
            "NEGATIVE_CONTROL_abs_m": {
                "definition": "the NORM of the same mean offset whose projection is O5",
                "why_it_is_here": "it isolates the defect: m is robust, |m| is not, so the "
                                  "pathology is the norm and not the centring",
                "status": "FORBIDDEN_AS_PRIMARY", "role": "NEGATIVE_CONTROL"},
        },
        "DEMONSTRATION": {
            "source": "the REAL recorded final fields; only the molecule count is reduced",
            "arms_used": len(used), "arms_skipped": skipped,
            "by_mission": {m: sum(1 for u in used if u["mission"] == m)
                           for m in ("OBTC02", "OBDI01", "OBDI02")},
            "AGGREGATE": agg, "CDF_AT_THE_SMALLEST_TARGET": cdf_check},
        "VERDICTS": {
            "M2_IS_POPULATION_ROBUST": verdict("M2", 0.02),
            "W2_DEBIASED_IS_POPULATION_ROBUST": verdict("W2_debiased", 0.25),
            "W2_PLUGIN_IS_NOT": not verdict("W2_plugin", 0.25),
            "abs_C_minus_Y_IS_NOT": not verdict("abs_C_minus_Y", 0.10),
            "abs_m_IS_NOT": not verdict("abs_m", 0.10)},
    }
    json.dump(out, open(f"{OUT}/_observables.json", "w"), indent=1, default=str)

    print("arms used %d  %s   skipped %s" % (len(used), out["DEMONSTRATION"]["by_mission"],
                                             skipped))
    print()
    hdr = "%-6s %8s %8s %8s %10s %10s %10s" % ("N_sub", "M2", "|C-Y|", "|m|", "m_y", "W2plug",
                                               "W2deb")
    print(hdr)
    print("-" * len(hdr))
    for T in SUBSAMPLE_TARGETS:
        def g(k, f="ratio_of_means"):
            v = agg[k].get(T)
            return v.get(f) if v else None
        m2, cy, am = g("M2"), g("abs_C_minus_Y"), g("abs_m")
        my = agg["m_y"].get(T)
        wp, wdb = g("W2_plugin"), g("W2_debiased")
        print("%-6d %8s %8s %8s %10s %10s %10s"
              % (T,
                 "%.4f" % m2 if m2 else "-", "%.4f" % cy if cy else "-",
                 "%.4f" % am if am else "-",
                 "%+.4f" % my["mean_signed_difference"] if my else "-",
                 "%.3f" % wp if wp else "-", "%.3f" % wdb if wdb else "-"))
    print()
    for k, v in out["VERDICTS"].items():
        print("  %-38s %s" % (k, v))


if __name__ == "__main__":
    main()
