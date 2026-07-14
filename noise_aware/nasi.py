"""NOISE-AWARE SET IDENTIFICATION -- EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00.

Independent instrument. numpy only. It NEVER converts a non-detection into an exact-zero claim.
Observes noisy channels y_i(t) = c_i * p(t) + n_i(t) with a KNOWN response profile p, where
    c_i = q * (1 - alpha_i kappa_i)          (signed channel response coefficient == v_i in the theorems)
estimates a *simultaneous* (1-alpha) confidence interval I_i for every c_i, then PROPAGATES those
intervals through the proved identifiability theorems (T6-A..E) under a DECLARED contract to obtain a
confidence SET Q for |q|.

Coverage argument (safe by construction): the T6 theorems are exact set inclusions of |q| in terms of the
noise-free magnitudes |c_i| (attenuate,no anchor: |q|>=max|c_i|; amplify,no anchor: |q|<=min|c_i|; clean
anchor: |q| in [min|c|,max|c|], pinned to an extreme by a sign contract; sparse s with m-s>=2: |q| = clean
majority common value). If the I_i are SIMULTANEOUS (family-wise) (1-alpha) CIs for the c_i, substituting
their endpoints into these monotone inequalities yields a set Q covering the true |q| with prob >= 1-alpha.
No step collapses Q to {0}; 0 is treated like any other value of |q|.

Exact zero is emitted ONLY through an independent STRUCTURAL contract (null_structural), never from a
threshold crossing, low SNR, or a non-significant test. Practical negligibility (Q subset [-dq,dq]) is
reported as PRACTICALLY_ZERO_WITHIN_MARGIN, explicitly NOT exact zero.

Two arms: ARM O (conditional) may receive externally DECLARED contracts (recorded with provenance);
ARM B (blind) receives no truth-derived metadata and returns a wider set or NON_IDENTIFIABLE if no
operational contract exists.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field

POINT="POINT_IDENTIFIED"; INTERVAL="INTERVAL_IDENTIFIED"
LOWER="LOWER_BOUND_ONLY"; UPPER="UPPER_BOUND_ONLY"
ZEROCOMP="ZERO_COMPATIBLE"; BELOWDET="BELOW_DETECTION_LIMIT"
PRACTZERO="PRACTICALLY_ZERO_WITHIN_MARGIN"; EXACTZERO="EXACT_ZERO_STRUCTURAL"
NONID="NON_IDENTIFIABLE"; NEEDSIGN="SIGN_CONTRACT_REQUIRED"; NEEDANCHOR="ANCHOR_CONTRACT_REQUIRED"
ILL="REFERENCE_MIXTURE_ILL_CONDITIONED"; LOWSNR="INSUFFICIENT_SNR"; OOS="OUT_OF_SCOPE"

EMITTING = {POINT, INTERVAL, LOWER, UPPER, ZEROCOMP, BELOWDET, PRACTZERO, EXACTZERO}
ABSTAIN  = {NONID, NEEDSIGN, NEEDANCHOR, ILL, LOWSNR, OOS}

DIVERSITY_FLOOR = 0.15
POINT_HALFWIDTH = 0.15
BOOT_B          = 399
BLOCK_FRAC      = 0.20
DRIFT_ORDER     = 1
SIMUL_INFLATE   = 1.12


@dataclass
class Contract:
    sign: str | None = None
    clean_anchor: bool = False
    sparsity_s: int | None = None
    null_structural: bool = False
    delta_q: float | None = None
    provenance: dict = field(default_factory=dict)


@dataclass
class Result:
    status: str
    qset: list
    zero_in: bool
    external_contract: dict
    diagnostics: dict = field(default_factory=dict)

    def contains(self, qmag: float, tol: float = 1e-9):
        if self.status in ABSTAIN:
            return None
        for lo, hi in self.qset:
            if lo - tol*max(1.0, abs(lo)) <= qmag <= hi + tol*max(1.0, abs(hi)):
                return True
        return False

    def width_rel(self, qmag: float):
        if self.status in ABSTAIN or not self.qset:
            return None
        lo = min(a for a, _ in self.qset); hi = max(b for _, b in self.qset)
        if not np.isfinite(hi):
            return None
        return float((hi - lo)/(abs(qmag) + 1e-12))


def _design(L, order=DRIFT_ORDER):
    tn = np.linspace(-1.0, 1.0, L)
    cols = [np.ones(L)]
    for d in range(1, order + 1):
        cols.append(tn**d)
    return np.column_stack(cols)


def _fit_setup(p, order=DRIFT_ORDER):
    L = p.shape[0]
    X = np.column_stack([p, _design(L, order)])
    XtX_inv = np.linalg.pinv(X.T @ X)
    A0 = (XtX_inv @ X.T)[0]
    h = np.clip(np.diag(X @ XtX_inv @ X.T), 0.0, 0.999)
    return X, A0, h


def channel_intervals(Y, p, alpha=0.05, rng=None, B=BOOT_B, order=None):
    """Simultaneous (family-wise, 1-alpha) CIs for the signed coefficients c_i.
    Studentized moving-block bootstrap with max-|t| simultaneity, over a design with polynomial DRIFT
    nuisance regressors (soak up OU / low-frequency drift). HC3 studentization (heteroscedasticity),
    block resampling (autocorrelation), SIMUL_INFLATE (finite-sample margin)."""
    if rng is None: rng = np.random.default_rng(0)
    if order is None: order = DRIFT_ORDER
    m, L = Y.shape
    X, A0, h = _fit_setup(p, order)
    c_hat = Y @ A0
    beta = np.linalg.pinv(X) @ Y.T
    R = Y - (X @ beta).T
    adj = R/(1.0 - h)[None, :]
    se = np.sqrt(((A0**2)[None, :]*adj**2).sum(axis=1)) + 1e-30
    # HAC-style effective-sample-size inflation from residual lag-1 autocorrelation (targets OU/AR1;
    # ~1.0 for white noise). rho pooled across channels for stability.
    r0 = R - R.mean(axis=1, keepdims=True)
    num = (r0[:, 1:]*r0[:, :-1]).sum(); den = (r0*r0).sum() + 1e-30
    rho = float(np.clip(num/den, 0.0, 0.9))
    eff = np.sqrt((1.0 + rho)/(1.0 - rho))
    se = se*eff
    b = max(3, int(round(BLOCK_FRAC*L)))
    n_blocks = int(np.ceil(L/b)); starts_max = L - b
    Tstar = np.empty(B)
    for r in range(B):
        st = rng.integers(0, starts_max + 1, size=n_blocks)
        idx = (st[:, None] + np.arange(b)[None, :]).ravel()[:L]
        Rb = R[:, idx]
        delta = Rb @ A0
        adjb = Rb/(1.0 - h)[None, :]
        seb = np.sqrt(((A0**2)[None, :]*adjb**2).sum(axis=1)) + 1e-30
        Tstar[r] = np.max(np.abs(delta)/seb)
    tstar = float(np.quantile(Tstar, 1.0 - alpha))*SIMUL_INFLATE
    return {"c_hat": c_hat, "se": se, "lo": c_hat - tstar*se, "hi": c_hat + tstar*se, "tstar": tstar, "b": b, "rho": rho}


def coupling_spread(lam):
    inv = 1.0/np.where(np.abs(lam) > 1e-9, lam, 1e-9)
    return float(np.std(inv)/(np.abs(np.mean(inv)) + 1e-30))


def _mag_interval(lo, hi):
    if lo > 0:  return (lo, hi)
    if hi < 0:  return (-hi, -lo)
    return (0.0, max(-lo, hi))


def _pin_status(lo, hi, zero_in):
    half = 0.5*(hi - lo); centre = 0.5*(hi + lo)
    rel = half/(abs(centre) + 1e-12)
    return POINT if ((not zero_in) and rel <= POINT_HALFWIDTH) else INTERVAL


def _largest_overlap_cluster(M):
    events = []
    for i, (a, b) in enumerate(M):
        events.append((a, 0, i)); events.append((b, 1, i))
    events.sort(key=lambda e: (e[0], e[1]))
    best = set(); cur = set()
    for x, typ, i in events:
        if typ == 0:
            cur.add(i)
            if len(cur) > len(best): best = set(cur)
        else:
            cur.discard(i)
    return best


def identify(Y, p, lam, contract, alpha=0.05, rng=None):
    if rng is None: rng = np.random.default_rng(0)
    m, L = Y.shape
    ext = {"sign": contract.sign, "clean_anchor": contract.clean_anchor,
           "sparsity_s": contract.sparsity_s, "null_structural": contract.null_structural,
           "provenance": dict(contract.provenance)}
    diag = {"m": int(m), "L": int(L)}

    if contract.null_structural:
        return Result(EXACTZERO, [(0.0, 0.0)], True, ext,
                      {**diag, "note": "exact zero by declared structural null contract (not from data)"})

    spread = coupling_spread(lam); diag["spread"] = spread
    if spread < DIVERSITY_FLOOR:
        return Result(ILL, [], False, ext, {**diag, "reason": "coupling spread below floor -> abstain/widen"})

    ci = channel_intervals(Y, p, alpha=alpha, rng=rng)
    diag.update({"c_hat": ci["c_hat"].tolist(), "se": ci["se"].tolist(),
                 "ci_lo": ci["lo"].tolist(), "ci_hi": ci["hi"].tolist(), "tstar": ci["tstar"]})
    M = [_mag_interval(lo, hi) for lo, hi in zip(ci["lo"], ci["hi"])]
    Mlo = np.array([a for a, _ in M]); Mhi = np.array([b for _, b in M])
    any_detected = bool(np.any(Mlo > 0.0))
    diag["M"] = [list(x) for x in M]; diag["any_detected"] = any_detected
    dq = contract.delta_q

    def finalize(qset, base_status):
        hi_all = max(b for _, b in qset)
        zero_in = any(a - 1e-12 <= 0.0 <= b + 1e-12 for a, b in qset)
        if dq is not None and np.isfinite(hi_all) and hi_all <= dq:
            return Result(PRACTZERO, qset, zero_in, ext,
                          {**diag, "delta_q": dq, "note": "Q subset [0,delta_q]; practical equivalence, NOT exact zero"})
        return Result(base_status, qset, zero_in, ext, diag)

    s = contract.sign
    if contract.clean_anchor:
        if s == "attenuate":
            lo = float(np.max(Mlo)); hi = float(np.max(Mhi))
            return finalize([(max(lo, 0.0), hi)], _pin_status(lo, hi, lo <= 0))
        if s == "amplify":
            det = Mlo > 0.0                     # genuine amplified channels are detected; exclude dropouts
            if det.any():
                lo = float(np.min(Mlo[det])); hi = float(np.min(Mhi[det]))
                return finalize([(max(lo, 0.0), hi)], _pin_status(lo, hi, lo <= 0))
            hi = float(np.sort(Mhi)[min(1, m-1)])   # none detected: drop one suspected dropout, loosest valid bound
            return Result(BELOWDET, [(0.0, hi)], True, ext, {**diag, "lod": hi,
                          "note": "clean-anchor amplify, no channel detected -> below detection limit; NOT exact zero"})
        lo = float(np.min(Mlo)); hi = float(np.max(Mhi))
        return finalize([(max(lo, 0.0), hi)], INTERVAL if any_detected else ZEROCOMP)

    if contract.sparsity_s is not None and (m - contract.sparsity_s) >= 2:
        cluster = _largest_overlap_cluster(M)
        if len(cluster) >= (m - contract.sparsity_s):
            lo = max(M[i][0] for i in cluster); hi = min(M[i][1] for i in cluster)
            if lo <= hi:
                return finalize([(max(lo, 0.0), hi)], _pin_status(lo, hi, lo <= 0))

    if s == "attenuate":
        Lb = float(np.max(Mlo))
        if Lb <= 0.0:
            return Result(ZEROCOMP, [(0.0, np.inf)], True, ext, {**diag, "note": "attenuate but all channels zero-compatible"})
        return finalize([(Lb, np.inf)], LOWER)
    if s == "amplify":
        det = Mlo > 0.0                          # |q| <= |c_i| for genuine channels; dropouts (zero-compat) excluded
        if det.any():
            Ub = float(np.min(Mhi[det]))
            return finalize([(0.0, Ub)], UPPER)
        Ub = float(np.sort(Mhi)[min(1, m-1)])    # none detected: drop one suspected dropout for the LOD bound
        return Result(BELOWDET, [(0.0, Ub)], True, ext,
                      {**diag, "lod": Ub, "note": "amplify, no channel detected -> below detection limit; NOT exact zero"})

    return Result(NONID, [], False, ext, {**diag, "reason": "no sign, no anchor: scale unrecoverable (T6-E)"})


def point_estimate(Y, p, result):
    if result.status != POINT or not result.qset:
        return None
    lo, hi = result.qset[0]
    return 0.5*(lo + hi)
