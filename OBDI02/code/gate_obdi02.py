"""OBDI02 §12-§13 — the primary equivalence endpoint, the population-support gate, the
extinction sensitivity, and the coherence guard-rails.

NO SCIENTIFIC THRESHOLD IS WRITTEN IN THIS FILE. Everything comes from `obdi02_protocol.yaml`,
frozen before the first arm.

The primary test is a TOST in its confidence-interval form: equivalence is declared only if the
WHOLE two-sided (1 - 2*alpha) interval for beta lies inside the margin. A point estimate near
zero does not qualify; excluding H_linear does not qualify; excluding H_sublinear does not
qualify.
"""
from __future__ import annotations

import hashlib
import math
import os

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(HERE, "obdi02_protocol.yaml")


def load(path=SPEC_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def spec_sha256(path=SPEC_PATH):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def z_one_sided(a):
    lo, hi = 0.0, 12.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        if 1.0 - 0.5 * (1.0 + math.erf(m / math.sqrt(2.0))) > a:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def wls_slope(x, y, w):
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    xb = (w * x).sum() / w.sum()
    sxx = (w * (x - xb) ** 2).sum()
    if sxx <= 0:
        return float("nan"), float("inf")
    return float((w * (x - xb) * y).sum() / sxx), float(1.0 / math.sqrt(sxx))


# ------------------------------------------------------------------ the estimator
def beta_cy(spec, by_L, values_key="summary_CY", use=None):
    """The frozen estimator: WLS slope of log(mean of analysable arm summaries at L) minus
    log(prediction at L), on log L, with weights n_L / sd_log_L^2."""
    pred = spec["predictions"]
    Ls = sorted(int(k) for k in by_L)
    x, y, w, detail = [], [], [], {}
    for L in Ls:
        v = np.asarray(by_L[L][values_key] if use is None else use[L], float)
        v = v[np.isfinite(v) & (v > 0)]
        n = len(v)
        if n < 2:
            continue
        lv = np.log(v)
        m = float(lv.mean())
        s = float(lv.std(ddof=1))
        p = math.log(float(pred[str(L)]["organiser_to_core"]))
        x.append(math.log(L))
        y.append(m - p)
        w.append(n / max(s, 1e-9) ** 2)
        detail[str(L)] = {"n_analysable": n, "mean_of_summaries": float(v.mean()),
                          "mean_of_log": m, "sd_of_log": s, "se_of_log_mean": s / math.sqrt(n),
                          "predicted": float(pred[str(L)]["organiser_to_core"]),
                          "log_ratio": m - p,
                          "relative_deviation": float(math.exp(m - p) - 1.0)}
    if len(x) < 2:
        return {"beta": float("nan"), "se": float("inf"), "per_L": detail,
                "sizes_used": len(x)}
    b, se = wls_slope(x, y, w)
    return {"beta": b, "se": se, "per_L": detail, "sizes_used": len(x)}


# ------------------------------------------------------------------ the primary endpoint
def evaluate_primary(spec, by_L):
    p = spec["primary_endpoint"]
    alpha = float(p["tost_alpha_one_sided"])
    c = z_one_sided(alpha)
    delta = float(p["equivalence_margin"])
    est = beta_cy(spec, by_L)
    lo, hi = est["beta"] - c * est["se"], est["beta"] + c * est["se"]
    achieved = abs(est["beta"]) + c * est["se"]
    out = {
        "NAME": p["name"], "estimand": p["estimand"],
        "method": p["method"], "tost_alpha_one_sided": alpha,
        "two_sided_interval_level": "%.1f %%" % (100 * (1 - 2 * alpha)),
        "critical_value_c": c, "equivalence_margin": delta,
        "beta": est["beta"], "se": est["se"],
        "interval": [lo, hi],
        "interval_inside_margin": bool(np.isfinite(lo) and lo > -delta and hi < delta),
        "achieved_equivalence_bound": achieved,
        "ACHIEVED_BOUND_MEANING": ("the smallest margin at which this data set would have "
                                   "declared equivalence"),
        "PASS": bool(np.isfinite(achieved) and achieved <= delta),
        "per_L": est["per_L"], "sizes_used": est["sizes_used"],
        "point_estimate_alone_is_not_sufficient": True,
        "excludes_H_sublinear_beta_0.5": bool(np.isfinite(est["se"])
                                              and abs(est["beta"] - 0.5) > c * est["se"]),
        "excludes_H_linear_beta_1.0": bool(np.isfinite(est["se"])
                                           and abs(est["beta"] - 1.0) > c * est["se"]),
    }
    # the mandate's stringent figure, declared underpowered in advance
    dm = float(p["stringent_reference_margin"])
    out["STRINGENT_REFERENCE"] = {
        "margin": dm, "PASS": bool(np.isfinite(achieved) and achieved <= dm),
        "declared_power_before_the_runs": float(p["stringent_reference_power"]),
        "status": "PRE-DECLARED UNDERPOWERED — reported, never decisive"}
    return out


# ------------------------------------------------------------------ population support
def evaluate_support(spec, by_L):
    g = spec["population_support_gate"]
    n_plan = int(spec["domain"]["SEEDS_PER_SIZE"])
    need = int(math.ceil(float(g["fraction_required"]) * n_plan))
    rows = {}
    ok = True
    for L in sorted(by_L):
        k = int(sum(1 for v in by_L[L]["summary_CY"] if np.isfinite(v) and v > 0))
        rows[str(L)] = {"arms_run": len(by_L[L]["summary_CY"]), "analysable": k,
                        "required": need, "planned": n_plan,
                        "notation": "%d/%d bras analysables ; seuil requis : %d/%d"
                                    % (k, n_plan, need, n_plan),
                        "PASS": bool(k >= need)}
        ok &= rows[str(L)]["PASS"]
    ks = [rows[k]["analysable"] for k in rows]
    return {"rule": g["rule"], "fraction_required": float(g["fraction_required"]),
            "required_per_size": need, "per_L": rows, "PASS": bool(ok),
            "extinctions_by_L": {k: rows[k]["arms_run"] - rows[k]["analysable"] for k in rows},
            "monotone_increase_with_L": bool(len(ks) >= 2 and all(
                a >= b for a, b in zip(ks, ks[1:]))) is False and bool(
                    all(a >= b for a, b in zip(ks, ks[1:])) is False),
            }


# ------------------------------------------------------------------ extinction sensitivity
def extinction_sensitivity(spec, by_L):
    """Conservative imputation: every extinct arm is given the WORST value consistent with the
    observed data at its size — first the maximum, then the minimum — and the primary test is
    re-run. Deleting an extinct arm as missing-at-random is forbidden; this is what replaces it.
    """
    out = {}
    for mode in ("max", "min"):
        use = {}
        for L in sorted(by_L):
            v = np.asarray(by_L[L]["summary_CY"], float)
            good = v[np.isfinite(v) & (v > 0)]
            if not len(good):
                use[L] = good
                continue
            fill = float(good.max() if mode == "max" else good.min())
            use[L] = np.where(np.isfinite(v) & (v > 0), v, fill)
        est = beta_cy(spec, by_L, use=use)
        c = z_one_sided(float(spec["primary_endpoint"]["tost_alpha_one_sided"]))
        d = float(spec["primary_endpoint"]["equivalence_margin"])
        out["impute_%s" % mode] = {
            "beta": est["beta"], "se": est["se"],
            "achieved_equivalence_bound": abs(est["beta"]) + c * est["se"],
            "PASS": bool(abs(est["beta"]) + c * est["se"] <= d)}
    out["RULE"] = ("an extinction is a SCIENTIFIC OUTCOME. It consumes its seed, it is never "
                   "replaced, and it is never deleted as a missing observation. The primary "
                   "analysis is conditional on the analysable arms; this sensitivity shows what "
                   "the same test gives when the extinct arms are forced to the least "
                   "favourable observed value.")
    out["ROBUST"] = bool(all(v["PASS"] for k, v in out.items() if k.startswith("impute_")))
    return out


# ------------------------------------------------------------------ coherence guard-rails
def evaluate_secondary(spec, by_L, arms):
    """Recomputed as secondary endpoints. They cannot create a pass; they can veto one."""
    s = spec["secondary_endpoints"]
    c = z_one_sided(float(spec["primary_endpoint"]["tost_alpha_one_sided"]))
    Ls = sorted(by_L)
    out = {}

    for stat in ("Rg", "r80"):
        est = beta_cy(spec, by_L, values_key="summary_" + stat)
        # the prediction key differs per statistic
        pred = spec["predictions"]
        x, y, w, det = [], [], [], {}
        for L in Ls:
            v = np.asarray(by_L[L]["summary_" + stat], float)
            v = v[np.isfinite(v) & (v > 0)]
            if len(v) < 2:
                continue
            lv = np.log(v)
            x.append(math.log(L))
            y.append(float(lv.mean()) - math.log(float(pred[str(L)][stat])))
            w.append(len(v) / max(float(lv.std(ddof=1)), 1e-9) ** 2)
            det[str(L)] = {"n": len(v), "mean": float(v.mean()),
                           "predicted": float(pred[str(L)][stat]),
                           "relative_deviation": float(v.mean() / float(pred[str(L)][stat]) - 1)}
        b, se = wls_slope(x, y, w) if len(x) >= 2 else (float("nan"), float("inf"))
        out["scaling_" + stat] = {
            "beta": b, "se": se, "achieved_bound": abs(b) + c * se, "per_L": det,
            "CONTRADICTS_BOUNDEDNESS": bool(np.isfinite(b) and b - c * se > float(
                s["material_contradiction"]["radius_scaling_beta_above"]))}
        del est

    # density exponent
    x, y, w, det = [], [], [], {}
    for L in Ls:
        v = np.asarray(by_L[L]["density"], float)
        v = v[np.isfinite(v)]
        if len(v) < 2 or (v <= 0).all():
            continue
        vv = v[v > 0]
        lv = np.log(vv)
        x.append(math.log(L))
        y.append(float(lv.mean()))
        w.append(len(vv) / max(float(lv.std(ddof=1)), 1e-9) ** 2)
        det[str(L)] = {"n": len(vv), "mean_density": float(vv.mean()),
                       "mean_N_X": float(vv.mean()) * L * L}
    g, seg = wls_slope(x, y, w) if len(x) >= 2 else (float("nan"), float("inf"))
    out["density_exponent"] = {
        "gamma": g, "se": seg, "per_L": det,
        "H_bound_predicts": -2.0,
        "CONTRADICTS_BOUNDEDNESS": bool(np.isfinite(g) and g + c * seg > float(
            s["material_contradiction"]["density_exponent_above"]))}

    # winding, profile, legacy gate, transport, population, turnover, free capacity
    wind = {str(L): {"frames_with_winding": int(sum(a["winding_frames"] for a in arms
                                                    if a["L"] == L)),
                     "frames": int(sum(a["window_frames"] for a in arms if a["L"] == L))}
            for L in Ls}
    for L in wind:
        wind[L]["fraction"] = wind[L]["frames_with_winding"] / max(wind[L]["frames"], 1)
    out["true_winding"] = {
        "per_L": wind, "tolerance": float(s["winding_tolerance"]),
        "CONTRADICTS_BOUNDEDNESS": bool(any(v["fraction"] > float(s["winding_tolerance"])
                                            for v in wind.values()))}

    prof = {}
    for L in Ls:
        thr = float(spec["profile_envelope"][str(L)]["quantile_value"])
        tv = [a["profile_TV"] for a in arms if a["L"] == L and np.isfinite(a["profile_TV"])]
        n_ok = sum(1 for t in tv if t <= thr)
        n_tot = sum(1 for a in arms if a["L"] == L)
        req = int(math.ceil(float(s["profile_fraction_required"]) * n_tot))
        prof[str(L)] = {"threshold": thr, "PASSING_ARMS": n_ok, "TOTAL_ARMS": n_tot,
                        "REQUIRED_PASSING_ARMS": req,
                        "notation": "%d/%d bras passent ; seuil requis : %d/%d"
                                    % (n_ok, n_tot, req, n_tot),
                        "PASS": bool(n_ok >= req)}
    out["radial_profile"] = {"per_L": prof,
                             "CONTRADICTS_BOUNDEDNESS": bool(any(not v["PASS"]
                                                                 for v in prof.values()))}

    leg = {}
    for L in Ls:
        rows = [a for a in arms if a["L"] == L]
        npass = sum(1 for a in rows if a["LEGACY_RELATIVE_LOCALIZATION"])
        leg[str(L)] = {"PASSING_ARMS": npass, "TOTAL_ARMS": len(rows),
                       "notation": "%d/%d bras passent" % (npass, len(rows)),
                       "failure_rate": 1 - npass / max(len(rows), 1)}
    out["legacy_D_gate"] = {"status": "SECONDARY_MISALIGNED_ENDPOINT", "per_L": leg,
                            "reported_even_if_it_fails": True}

    out["transport_rejection"] = {
        "max_X": float(max(a["blocked_fraction"]["X"] for a in arms)),
        "max_Y": float(max(a["blocked_fraction"]["Y"] for a in arms))}
    out["population"] = {str(L): float(np.mean([a["summary"]["N_X_mean"] for a in arms
                                                if a["L"] == L
                                                and a["summary"]["N_X_mean"] > 0]))
                         for L in Ls}
    out["occupancy_exactly_constant"] = bool(all(a["occupancy"]["exactly_constant"]
                                                 for a in arms))
    out["ANY_MATERIAL_CONTRADICTION"] = bool(
        out["scaling_Rg"]["CONTRADICTS_BOUNDEDNESS"]
        or out["scaling_r80"]["CONTRADICTS_BOUNDEDNESS"]
        or out["density_exponent"]["CONTRADICTS_BOUNDEDNESS"]
        or out["true_winding"]["CONTRADICTS_BOUNDEDNESS"]
        or out["radial_profile"]["CONTRADICTS_BOUNDEDNESS"])
    return out
