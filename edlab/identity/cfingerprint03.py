"""DRIFT-AWARE RISK-CALIBRATED CONTINUOUS CAUSAL FINGERPRINT — EXP-GT-CONTINUOUS-FINGERPRINT-03.

    v00: "is the signal still moving?"                  -> abstained on a decidable cascade.
    v01: "can the remainder change the verdict?"        -> could not SEE a remainder of 8.25 through a floor of 7.40.
    v02: "certify the resolution, then choose W"        -> proved NO horizon works. The floor is DRIFT-limited and
                                                          the ratio is bounded above (~2.56) and non-monotone.
    v03: "bound the RISK, not the remainder."

THIS IS A RETREAT, AND IT IS DELIBERATE. v03 does not certify that the unseen continuation cannot change the
verdict. It PREDICTS the eventual distance and attaches a CONFORMALLY CALIBRATED INTERVAL to that prediction, and
it abstains whenever the interval touches a decision boundary. The guarantee is MARGINAL coverage under a DECLARED
distribution -- not a proof, not conditional, and not protection against arbitrary out-of-distribution systems.
Saying so plainly is part of the instrument.

TWO THINGS THE PREVIOUS THREE VERSIONS TAUGHT, BOTH BUILT IN HERE:

1. THE NOISE FLOOR IS DRIFT-LIMITED, AND `sd`-BY-DIFFERENCING IS BLIND TO DRIFT BY CONSTRUCTION. So the drift scale
   is measured from a MATCHED SHAM CHANNEL -- baseline episodes with identical duration, timing, horizon, sampling
   and noise/drift generator, differing ONLY in the absence of intervention amplitude. The active tail is never
   fitted away to estimate the drift underneath it.

2. A PREFIX OF A LONG EPISODE IS NOT A SHORT EPISODE WITH THE SAME SEED (the engine draws noise then drift from one
   RNG stream, so the drift sequence depends on T; measured 6.48 on a system compared with ITSELF). Every
   nested-prefix feature here slices ONE acquisition.

WHAT IS PRESERVED: the fixed battery, the NSRC representation, max-over-probes aggregation, the lambda-quotient,
unit invariance, coverage, responsiveness, the common-channel refusal, and EQUIVALENCE_CLASS_ONLY. THERE IS STILL
NO SAME.
"""

from __future__ import annotations

import math

import numpy as np

from . import cfingerprint as F0, cfingerprint02 as F2
from ..substrates.ctrans.engine import Probe

W_FIXED = 320          # the frozen horizon (v02's best; its resolution certificate is what says "no better exists")
ALPHA = 0.05           # PREREGISTERED

INDIST = F0.INDIST
IDENTIFIABLE_DIFFERENT = "IDENTIFIABLE_DIFFERENT"
INDETERMINATE_RISK_INTERVAL = "INDETERMINATE_RISK_INTERVAL"
EQUIVALENCE_CLASS_ONLY = "EQUIVALENCE_CLASS_ONLY"
OUT_OF_CALIBRATION_SCOPE = "OUT_OF_CALIBRATION_SCOPE"
INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"
INSUFFICIENT_RESPONSIVENESS = "INSUFFICIENT_RESPONSIVENESS"
CONFOUNDED = "CONFOUNDED"
OUT_OF_SCOPE = "OUT_OF_SCOPE"

FEATURES = ["D_W", "late_level", "late_slope", "tail_energy", "prefix_delta", "peak", "drift_scale",
            "margin_cont", "margin_sep"]


# ================================================================ acquisition, with the matched sham channel
def acquire(measure, arm: str, seed0: int, W: int = W_FIXED, quantize_uint8: bool = False) -> dict:
    """The preserved NSRC pipeline PLUS a matched sham channel built from the baseline episodes alone.

    The sham costs no extra simulation: every active probe already has an independent baseline episode with the
    same duration, timing, horizon, sampling and noise/drift generator, differing only in the ABSENCE of
    intervention amplitude. Splitting those baselines in half and differencing gives a channel with the same
    averaging structure as the causal deviation and NO intervention in it at all. Its late block-means are what
    the drift actually does to this instrument -- which is the number v02's `sd` could not see.
    """
    T = F2.episode_len(W)
    R = F0.N_REPEAT
    probes = F0.battery(arm)
    P, K = len(probes), len(F0.PHASES)
    eps, meta = [], []
    for r in range(R):
        for pi, (nm, tgt, kind, amp, hold) in enumerate(probes):
            for ki, ph in enumerate(F0.PHASES):
                eps.append(Probe("base", -1, "none", 0.0, 0, 10 ** 9)); meta.append(("base", r, pi, ki))
                eps.append(Probe(nm, tgt, kind, amp, hold, F0.T_PROBE + ph)); meta.append(("probe", r, pi, ki))
    u, ok = measure(eps, T, np.arange(seed0, seed0 + len(eps)))
    if quantize_uint8:
        u = np.nan_to_num(u).astype(np.uint8).astype(float)

    B, Pr = {}, {}
    for i, (t, r, pi, ki) in enumerate(meta):
        if t == "base":
            B[(r, pi, ki)] = u[i]
        else:
            Pr.setdefault((pi, ki), {})[r] = (u[i], ok[i])

    Z = np.full((P, K, W), np.nan)
    ZS = np.full((P, K, W), np.nan)
    missing = np.zeros((P, K), dtype=bool)
    raw, sham, pre = {}, {}, []
    h = R // 2
    for pi in range(P):
        for ki, ph in enumerate(F0.PHASES):
            on = F0.T_PROBE + ph
            g = Pr[(pi, ki)]
            if not all(g[r][1] for r in range(R)):
                missing[pi, ki] = True
                continue
            sl = slice(on - F0.W_PRE, on + W)
            raw[(pi, ki)] = np.mean([g[r][0][sl] - B[(r, pi, ki)][sl] for r in range(R)], axis=0)
            # THE MATCHED SHAM: baselines only, split in half. Same averaging structure, no intervention.
            # Var of (mean of R/2) - (mean of R/2) is 2x that of the causal deviation, so divide by sqrt(2).
            sham[(pi, ki)] = (np.mean([B[(r, pi, ki)][sl] for r in range(h)], axis=0)
                              - np.mean([B[(r, pi, ki)][sl] for r in range(h, R)], axis=0)) / math.sqrt(2.0)
            pre.append(raw[(pi, ki)][:F0.W_PRE])
    if not pre:
        return {"Z": Z, "Z_sham": ZS, "missing": missing, "coverage": 0.0, "responsive": 0.0, "arm": arm,
                "W": W, "sigma_hat": float("nan"), "baseline_stability": float("nan"), "drift_scale": float("nan")}
    sh = F0._diff_sigma(np.concatenate(pre))
    if not np.isfinite(sh) or sh <= 0:
        sh = float(np.std(np.concatenate(pre))) or 1e-300
    resid, nresp = [], 0
    for (pi, ki), d in raw.items():
        dd = d - np.median(d[:F0.W_PRE])
        resid.append(dd[:F0.W_PRE])
        Z[pi, ki] = dd[F0.W_PRE:] / sh
        s = sham[(pi, ki)]
        ZS[pi, ki] = (s - np.median(s[:F0.W_PRE]))[F0.W_PRE:] / sh
        nresp += int(float(np.nanmax(np.abs(Z[pi, ki]))) >= F0.Z_DET)
    nv = int((~missing).sum())
    # DRIFT SCALE: the spread of LATE BLOCK MEANS in the sham channel. This is exactly the quantity v02's
    # differenced `sd` was blind to, and exactly the quantity that set its floor.
    L = F2.sub_block_len(W)
    bm = [float(ZS[p, k][F2.T_TAIL0 + j * L:F2.T_TAIL0 + (j + 1) * L].mean())
          for p in range(P) for k in range(K) for j in range(3) if not missing[p, k]]
    return {"Z": Z, "Z_sham": ZS, "missing": missing, "arm": arm, "W": W, "sigma_hat": sh,
            "coverage": nv / (P * K), "responsive": nresp / max(nv, 1), "n_responded": nresp,
            "baseline_stability": float(np.sqrt(np.mean(np.concatenate(resid) ** 2)) / sh),
            "drift_scale": float(np.std(bm)) if bm else float("nan")}


# ================================================================ the observable-prefix distance and its features
def _pair(A, B, W=None):
    W = A["W"] if W is None else W
    ZA, ZB = A["Z"][:, :, :W], B["Z"][:, :, :W]
    P, K = ZA.shape[0], ZA.shape[1]
    valid = (~A["missing"]) & (~B["missing"])
    band = F0.SCALE_BAND
    best = (math.inf, None, None)
    for s in range(K):
        pr = [(ZA[i, k], ZB[i, (k + s) % K]) for i in range(P) for k in range(K)
              if valid[i, k] and valid[i, (k + s) % K]]
        if not pr:
            continue
        num = sum(float(np.dot(a, b)) for a, b in pr)
        den = sum(float(np.dot(b, b)) for a, b in pr)
        lam = float(np.clip(num / den, 1 - band, 1 + band)) if (band > 0 and den > 0) else 1.0
        d = max(float(np.sqrt(np.mean((a - lam * b) ** 2))) for a, b in pr)
        if d < best[0]:
            best = (d, s, lam)
    return best


def D_W(A, B, W=None):
    return _pair(A, B, W)[0]


def features(A, B, r_cont, r_sep, W=W_FIXED):
    """Auditable, label-free. Every one of these is a measurement, not a name."""
    d, s, lam = _pair(A, B, W)
    if s is None:
        return None
    ZA, ZB = A["Z"], B["Z"]
    K = ZA.shape[1]
    L = F2.sub_block_len(W)
    valid = (~A["missing"]) & (~B["missing"])
    lev, slo, ten, pk = [], [], [], []
    for i in range(ZA.shape[0]):
        for k in range(K):
            k2 = (k + s) % K
            if not (valid[i, k] and valid[i, k2]):
                continue
            dl = ZA[i, k][:W] - lam * ZB[i, k2][:W]
            t = dl[F2.T_TAIL0:F2.T_TAIL0 + 3 * L]
            m1 = float(t[:L].mean()); m3 = float(t[2 * L:].mean())
            lev.append(abs(m3)); slo.append(abs(m3 - m1) / (2.0 * L))
            ten.append(float(np.sqrt(np.mean((t - m3) ** 2)))); pk.append(float(np.max(np.abs(dl))))
    d_half = D_W(A, B, W // 2)
    return {"D_W": d, "late_level": float(np.mean(lev)), "late_slope": float(np.mean(slo)),
            "tail_energy": float(np.mean(ten)), "prefix_delta": d - d_half, "peak": float(np.mean(pk)),
            "drift_scale": 0.5 * (A["drift_scale"] + B["drift_scale"]),
            "margin_cont": d - r_cont, "margin_sep": d - r_sep}


# ================================================================ predictor + split conformal
class RiskModel:
    """Ridge on standardized features, fitted on the FIT SET; conformal quantile from the UNTOUCHED CAL SET."""

    def __init__(self, lam=1.0):
        self.lam = lam

    def fit(self, X, y):
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-12
        Xs = np.hstack([(X - self.mu) / self.sd, np.ones((len(X), 1))])
        A = Xs.T @ Xs + self.lam * np.eye(Xs.shape[1])
        A[-1, -1] -= self.lam                      # do not penalise the intercept
        self.w = np.linalg.solve(A, Xs.T @ y)
        return self

    def predict(self, X):
        Xs = np.hstack([(X - self.mu) / self.sd, np.ones((len(X), 1))])
        return Xs @ self.w

    def calibrate(self, Xc, yc, alpha=ALPHA):
        """SPLIT CONFORMAL. Residuals from data the predictor has never seen."""
        n = len(yc)
        need = math.ceil((n + 1) * (1 - alpha))
        if need > n:
            raise RuntimeError("INSUFFICIENT_CALIBRATION_RESOLUTION: n=%d cannot support alpha=%.2f "
                               "(need ceil((n+1)(1-alpha)) = %d <= n). ALPHA IS NOT CHANGED." % (n, alpha, need))
        r = np.abs(yc - self.predict(Xc))
        self.q = float(np.sort(r)[need - 1])
        self.n_cal, self.alpha = n, alpha
        return self.q

    def interval(self, x):
        p = float(self.predict(x[None, :])[0])
        return p - self.q, p, p + self.q


def in_scope(f, lo, hi):
    """OUT-OF-CALIBRATION-SCOPE. Confident extrapolation outside the fitted feature ranges is not caution, it is
    the same overreach in a new coat."""
    for k in FEATURES:
        if not (lo[k] <= f[k] <= hi[k]):
            return False, k
    return True, None


def verdict(A, B, model, f, r_cont, r_sep, lo, hi, common_channel=True, enforce_channel=True, use_conformal=True):
    """Repertoire-relative, risk-calibrated. THERE IS STILL NO SAME."""
    adm = F2.admit(A, B, common_channel, enforce_channel)
    if not adm["ok"]:
        return {"verdict": adm["code"], "why": adm["why"], "L": None, "U": None, "D_W": f["D_W"] if f else None}
    ok, bad = in_scope(f, lo, hi)
    if not ok:
        return {"verdict": OUT_OF_CALIBRATION_SCOPE, "D_W": f["D_W"], "L": None, "U": None,
                "why": "feature '%s' = %.3g lies outside the calibrated range [%.3g, %.3g]. The interval carries no "
                       "guarantee here, so none is offered." % (bad, f[bad], lo[bad], hi[bad])}
    x = np.array([f[k] for k in FEATURES])
    if use_conformal:
        L, p, U = model.interval(x)
    else:
        p = float(model.predict(x[None, :])[0]); L = U = p     # MUST-FAIL control: no calibration at all
    out = {"D_W": f["D_W"], "pred_D_inf": p, "L": L, "U": U, "width": U - L}
    if U < r_cont:
        return {**out, "verdict": INDIST, "code": EQUIVALENCE_CLASS_ONLY,
                "why": "the whole calibrated interval [%.2f, %.2f] lies below the continuity radius %.2f. An "
                       "EQUIVALENCE CLASS relative to this repertoire -- not an identity." % (L, U, r_cont)}
    if L > r_sep:
        return {**out, "verdict": IDENTIFIABLE_DIFFERENT,
                "why": "the whole calibrated interval [%.2f, %.2f] lies above the separation radius %.2f."
                       % (L, U, r_sep)}
    return {**out, "verdict": INDETERMINATE_RISK_INTERVAL,
            "why": "the calibrated interval [%.2f, %.2f] touches a decision boundary (r_cont=%.2f, r_sep=%.2f). "
                   "The risk of being wrong is not bounded below alpha here, so no verdict is issued."
                   % (L, U, r_cont, r_sep)}
