"""OBDI01 §15-§16 — the principal outcome (a simultaneous acceptance region) and the locked
secondary endpoint.

NO SCIENTIFIC THRESHOLD IS WRITTEN IN THIS FILE. Every number comes from
`obdi01_protocol.yaml`, which is generated in §15 and frozen before any arm is run.

The evaluator is deliberately blind to the arm order and to the seeds: it consumes arm-level
summaries and returns a verdict. It cannot stop a run, and it is called once, at the end.
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = os.path.join(HERE, "obdi01_protocol.yaml")

SHAPE_STATS = ("Rg", "r80", "organiser_to_core")


def load(path=SPEC_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def spec_sha256(path=SPEC_PATH):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ------------------------------------------------------------------ radial profile machinery
def radial_bins(edges):
    """Bin index of a toroidal distance: [0,1), [1,2), ... , [max, inf)."""
    e = np.asarray(edges, float)
    return lambda d: np.clip(np.searchsorted(e, d, side="right") - 1, 0, len(e) - 1)


def empirical_radial(field, oy, ox, edges):
    """Mass distribution of X over toroidal-distance bins measured from the organiser."""
    L = field.shape[0]
    i = np.arange(L)
    dy = np.minimum(np.abs(i - oy), L - np.abs(i - oy)).astype(float)
    dx = np.minimum(np.abs(i - ox), L - np.abs(i - ox)).astype(float)
    d = np.sqrt(dy[:, None] ** 2 + dx[None, :] ** 2)
    b = radial_bins(edges)(d)
    h = np.bincount(b.ravel(), weights=field.ravel().astype(float), minlength=len(edges))
    s = h.sum()
    return h / s if s > 0 else h


def predicted_radial(profile, edges):
    """The same binning applied to the EXACT stationary profile of the operator."""
    L = profile.shape[0]
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    b = radial_bins(edges)(d)
    h = np.bincount(b.ravel(), weights=profile.ravel(), minlength=len(edges))
    return h / h.sum()


def total_variation(p, q):
    return float(0.5 * np.abs(np.asarray(p, float) - np.asarray(q, float)).sum())


# ------------------------------------------------------------------ weighted slope
def wls_slope(x, y, w):
    """Weighted least squares slope and its standard error, weights w = 1 / var(y)."""
    x, y, w = map(lambda a: np.asarray(a, float), (x, y, w))
    sw = w.sum()
    xb = (w * x).sum() / sw
    sxx = (w * (x - xb) ** 2).sum()
    if sxx <= 0:
        return float("nan"), float("inf")
    b = (w * (x - xb) * y).sum() / sxx
    return float(b), float(1.0 / np.sqrt(sxx))


# ------------------------------------------------------------------ the principal outcome
def evaluate_principal(spec, by_L):
    """`by_L[L]` carries, for one domain size:
         values[stat] : list of arm-level medians
         density      : list of arm-level mean N_X / L^2
         winding      : (n_frames_with_winding, n_frames) pooled over the arms
         profile_TV   : list of arm-level total-variation distances
    """
    po = spec["principal_outcome"]
    c = float(po["multiplicity"]["critical_value_c"])
    pred = spec["predictions"]
    sd_pre = spec["power"]["prereg_sd"]
    Ls = sorted(int(k) for k in by_L)
    logL = np.log(Ls)

    out = {"critical_value_c": c, "components": {}}

    # ---- A : shape invariance ------------------------------------------------------------
    A = {}
    margin = float(po["components"]["A_shape_invariance"]["margin"])
    for s in SHAPE_STATS:
        ys, ws, detail = [], [], {}
        for L in Ls:
            v = np.asarray(by_L[L]["values"][s], float)
            v = v[np.isfinite(v)]
            n = len(v)
            mean = float(v.mean())
            sd_real = float(v.std(ddof=1)) if n > 1 else float("inf")
            sd_used = max(sd_real, float(sd_pre.get(s, 0.0)))
            se_mean = sd_used / np.sqrt(max(n, 1))
            p = float(pred[str(L)][s])
            ys.append(np.log(mean) - np.log(p))
            ws.append((mean / se_mean) ** 2)               # 1 / var(log mean)
            detail[str(L)] = {"n_arms": n, "mean": mean, "sd_realised": sd_real,
                              "sd_used": sd_used, "se_of_mean": se_mean,
                              "predicted": p, "log_ratio": float(np.log(mean) - np.log(p)),
                              "relative_deviation": float(mean / p - 1.0)}
        b, se = wls_slope(logL, ys, ws)
        upper = abs(b) + c * se
        A[s] = {"beta": b, "se": se, "abs_beta_plus_c_se": upper, "margin": margin,
                "PASS": bool(np.isfinite(upper) and upper <= margin),
                "excludes_H_sublinear": bool(np.isfinite(b) and abs(b - 0.5) > c * se),
                "excludes_H_linear": bool(np.isfinite(b) and abs(b - 1.0) > c * se),
                "per_L": detail}
    out["components"]["A_shape_invariance"] = {
        "by_statistic": A, "PASS": bool(all(A[s]["PASS"] for s in SHAPE_STATS))}

    # ---- B : density exponent ------------------------------------------------------------
    marg = float(po["components"]["B_density_exponent"]["margin"])
    ys, ws, detail = [], [], {}
    for L in Ls:
        v = np.asarray(by_L[L]["density"], float)
        v = v[np.isfinite(v)]
        n = len(v)
        mean = float(v.mean())
        sd = float(v.std(ddof=1)) if n > 1 else float("inf")
        se = sd / np.sqrt(max(n, 1))
        ys.append(np.log(mean))
        ws.append((mean / se) ** 2 if se > 0 else 1e12)
        detail[str(L)] = {"n_arms": n, "mean_density": mean, "sd": sd,
                          "predicted_density": float(pred[str(L)]["density"]),
                          "mean_N_X": mean * L * L}
    g, se_g = wls_slope(logL, ys, ws)
    upper = abs(g + 2.0) + c * se_g
    out["components"]["B_density_exponent"] = {
        "gamma": g, "se": se_g, "deviation_from_minus_2": abs(g + 2.0),
        "abs_dev_plus_c_se": upper, "margin": marg,
        "PASS": bool(np.isfinite(upper) and upper <= marg),
        "excludes_H_fill": bool(np.isfinite(g) and abs(g - 0.0) > c * se_g),
        "excludes_H_sublinear": bool(np.isfinite(g) and abs(g + 1.0) > c * se_g),
        "per_L": detail}

    # ---- C : no true winding -------------------------------------------------------------
    tol = float(po["components"]["C_no_true_winding"]["tolerance"])
    cdet, cok = {}, True
    for L in Ls:
        nw, nf = by_L[L]["winding"]
        f = nw / max(nf, 1)
        ok = bool(f <= tol)
        cok &= ok
        cdet[str(L)] = {"frames_with_winding": int(nw), "frames": int(nf), "fraction": f,
                        "tolerance": tol, "PASS": ok}
    out["components"]["C_no_true_winding"] = {"per_L": cdet, "PASS": bool(cok)}

    # ---- D : profile compatibility -------------------------------------------------------
    need = int(po["components"]["D_profile_compatibility"]["arms_required"])
    env = po["components"]["D_profile_compatibility"]["envelope_by_L"] or {}
    ddet, dok = {}, True
    for L in Ls:
        thr = float(env.get(str(L), {}).get("quantile_value", float("nan")))
        tv = [float(t) for t in by_L[L]["profile_TV"]]
        n_ok = sum(1 for t in tv if np.isfinite(thr) and t <= thr)
        ok = bool(n_ok >= need)
        dok &= ok
        ddet[str(L)] = {"threshold": thr, "arms_within": n_ok, "arms_required": need,
                        "TV_by_arm": tv, "PASS": ok}
    out["components"]["D_profile_compatibility"] = {"per_L": ddet, "PASS": bool(dok)}

    out["DOMAIN_INVARIANCE_REGION_PASS"] = bool(
        out["components"]["A_shape_invariance"]["PASS"]
        and out["components"]["B_density_exponent"]["PASS"]
        and out["components"]["C_no_true_winding"]["PASS"]
        and out["components"]["D_profile_compatibility"]["PASS"])
    return out


# ------------------------------------------------------------------ the locked secondary
def evaluate_secondary(spec, arms):
    """The legacy D gate, exactly as OBTC02 defined it. Reported, never used to decide."""
    abs_b, frac_b, req = 12.8, 0.35, 0.95
    rows, by_L = [], {}
    for a in arms:
        L = int(a["L"])
        bound = min(abs_b, frac_b * L)
        r = np.asarray(a["r80_organiser_frames"], float)
        r = r[np.isfinite(r)]
        f = float(np.mean(r <= bound)) if len(r) else 0.0
        rows.append({"tag": a["tag"], "L": L, "bound": bound, "fraction": f,
                     "frames": int(len(r)), "PASS": bool(f >= req)})
        by_L.setdefault(L, []).append(rows[-1])
    return {"definition": spec["secondary_endpoint"]["definition"],
            "status": spec["secondary_endpoint"]["status"],
            "required_fraction": req, "per_arm": rows,
            "passing_by_L": {str(L): sum(1 for r in v if r["PASS"]) for L, v in by_L.items()},
            "arms_by_L": {str(L): len(v) for L, v in by_L.items()},
            "LEGACY_D_GATE_ON_FRESH_SEEDS": {
                str(L): "%d/%d arms pass" % (sum(1 for r in v if r["PASS"]), len(v))
                for L, v in by_L.items()}}
