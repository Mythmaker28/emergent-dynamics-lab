"""CRD-01 -- FACTORIZED CAUSAL RESPONSE DECOMPOSITION UNDER A COMMON-MODE ACQUISITION CONTRACT.

CRD-00 failed on Z-17 -- a slow response under heavy drift -- by quoting a drift excursion as a causal peak
(E_trans overstated 7.1x, A_peak 422.7 against a true ~97). The diagnosis was NOT an estimator defect:

    A SHAM WITH THE SAME VARIANCE BUT AN INDEPENDENT REALIZATION IS UNBIASED IN EXPECTATION AND USELESS PER PAIR.

So this instrument does not tune CRD-00's estimators. It CHANGES WHAT IS ACQUIRED and then adds exactly one thing:
THE RIGHT TO REFUSE ON DRIFT GROUNDS (`INDETERMINATE_DRIFT`). Everything else is inherited, deliberately and by name.

  drift proxy      c_r(t) = y_C(r,t) - mean_r y_C(r,t)      built from the CONTROL CHANNEL ALONE.
                   It cannot leak the causal response, because the control never receives the intervention.
  correction       r_corr(r,t) = [y_A(r,t) - y_C(r,t)] - g_hat * c_r(t - lam_hat)
  fitting region   PRE-INTERVENTION ONLY. g_hat and lam_hat are estimated where the causal response IS ZERO
                   BY CONSTRUCTION. A correction fitted on the causal tail can subtract the signal; this one
                   is structurally unable to.
  noise floor      sigma_eps = std(diff(r_pre)) / sqrt(2). The drift is smooth (tau ~ 500) so differencing
                   annihilates it; the measurement noise is white so differencing preserves it. This estimator
                   is drift-immune BY CONSTRUCTION -- it is not a fitted constant.

ADMISSION is then a single, physically meaningful question: AFTER correction, is the residual common mode down at
the measurement-noise floor -- i.e. inside the bands the sham already covers? Not "is the correlation high".
"""

from __future__ import annotations

import numpy as np

# ---- PREREGISTERED. Frozen before any sweep, any frontier, any prospective system. ----
W_FIXED = 480      # resolution contract, inherited from CFP-02 (horizon certified against tau_max)
W_PRE = 480        # PRE-INTERVENTION BASELINE == ANALYSIS WINDOW. Not a convenience: a common-mode certificate
                   # earned on a short window where the drift has barely developed does not transfer to a long
                   # window where it has. Certify the rejection over the SAME duration you will trust it for.
W_LATE = 120       # late window for P_inf
LAG_MAX = 12       # relative-delay search for the common-mode coupling
RDNR_ADMIT = 1.5   # residual drift <= ~1.1 sigma_eps  -> ADMISSIBLE
RDNR_PARTIAL = 4.0 # 1.5 < RDNR <= 4.0                 -> PARTIAL (reported, NOT used for verdicts)
DRIFT_FLOOR = 2.0  # channel drift below 2 sigma_eps   -> DRIFT_ABSENT (common mode is moot, not failed)
CONTAM_K = 3.0     # control's probe-dependence, post vs pre -> CONTROL_CONTAMINATED
K_SIG = 1.5        # inherited from CRD-00 (crossing factor over the band)
DWELL = 12         # inherited from CRD-00 (onset must be HELD, not touched)
R_NULL_E = 25.0    # inherited from CRD-00
R_AMB_A = 3.0      # inherited from CRD-00

ADMISSIBLE = "COMMON_MODE_ADMISSIBLE"
PARTIAL = "COMMON_MODE_PARTIAL"
NOT_ESTAB = "COMMON_MODE_NOT_ESTABLISHED"
CONTAM = "CONTROL_CONTAMINATED"
NO_DRIFT = "DRIFT_ABSENT"


def sigma_eps(x):
    """White-noise floor, immune to smooth drift by construction."""
    return float(np.std(np.diff(x)) / np.sqrt(2.0)) if len(x) > 2 else 0.0


def _fit_cm(rpre, cpre):
    """TWO-TAP common-mode regression, fitted on the PRE-INTERVENTION region ONLY.

    The correction model must MATCH THE DECLARED ACQUISITION MODEL, and the acquisition model has a lag on EACH
    channel:  y_A carries a_A*d(t-delta_A), y_C carries a_C*d(t-delta_C). The proxy is a_C*d(t-delta_C), so

        residual drift = (a_A/a_C) * cm(t + delta_C - delta_A)  -  cm(t)

    which is a GAINED, LAGGED copy MINUS an un-lagged one. A single tap cannot express that: with delta_A=0 and
    delta_C=4 the residual is d(t) - d(t-4) ~ 4*d'(t), a DERIVATIVE, and one-tap regression returns g=0 and
    cancels nothing (observed: RDNR 1.67, lam_hat 0, common mode wrongly downgraded to PARTIAL).

    Two taps span exactly the declared model. This is not an extra degree of freedom bought to improve a number;
    it is the minimum basis in which the acquisition contract's own algebra closes.
    """
    n = LAG_MAX + 1
    best = (0.0, 0.0, 0, float(np.var(rpre[n:-n])))
    r_ = rpre[n:-n]
    for lam in range(-LAG_MAX, LAG_MAX + 1):
        c0 = cpre[n:-n]
        c1 = np.roll(cpre, lam)[n:-n]
        X = np.stack([c0, c1], axis=1)
        try:
            g, *_ = np.linalg.lstsq(X, r_, rcond=1e-8)
        except np.linalg.LinAlgError:
            continue
        v = float(np.var(r_ - X @ g))
        if v < best[3]:
            best = (float(g[0]), float(g[1]), lam, v)
    return best


def correct(yA, yC, yD, yS, t_probe):
    """The common-mode correction. Returns corrected active + sham deviations and the admission report.

    yA, yC, yD, yS : (R, T) active / control-1 / control-2 / sham. Each row is one repeat, and within a repeat all
    four channels SHARE ONE DRIFT REALIZATION. The proxy is built from yD, NOT from the yC we subtract -- see
    cmacq.acquire: a proxy sharing measurement noise with the deviation fits eps against itself.
    """
    yA, yC, yD, yS = (np.asarray(v, float) for v in (yA, yC, yD, yS))
    R, T = yA.shape
    cm = yD - yD.mean(axis=0, keepdims=True)     # drift proxy. Control-only: causal leakage is IMPOSSIBLE.
    dA = yA - yC                                 # active deviation (drift already partly cancelled by sharing)
    dS = yS - yC                                 # sham deviation: same acquisition, no intervention amplitude
    pre = slice(0, t_probe)

    se = float(np.median([sigma_eps(dA[r, pre]) for r in range(R)]))
    drift_amp = float(np.median([np.std(cm[r, pre]) for r in range(R)]))

    g0s, g1s, ls = [], [], []
    for r in range(R):
        g0, g1, lam, v = _fit_cm(dA[r, pre], cm[r, pre])
        g0s.append(g0); g1s.append(g1); ls.append(lam)
    g0_hat, g1_hat = float(np.median(g0s)), float(np.median(g1s))
    lam_hat = int(np.median(ls))
    if drift_amp < DRIFT_FLOOR * se:
        g0_hat = g1_hat = 0.0       # no drift to reject: correcting against a pure-noise proxy only INJECTS noise
        lam_hat = 0

    def _c(x, r):
        return x[r] - (g0_hat * cm[r] + g1_hat * np.roll(cm[r], lam_hat))

    A = np.stack([_c(dA, r) for r in range(R)])
    S = np.stack([_c(dS, r) for r in range(R)])

    resid = float(np.median([np.std(A[r, pre]) for r in range(R)]))
    rdnr = resid / se if se > 0 else np.inf

    if drift_amp < DRIFT_FLOOR * se:
        verdict = NO_DRIFT
    elif rdnr <= RDNR_ADMIT:
        verdict = ADMISSIBLE
    elif rdnr <= RDNR_PARTIAL:
        verdict = PARTIAL
    else:
        verdict = NOT_ESTAB
    return A, S, {"verdict": verdict, "rdnr": float(rdnr), "sigma_eps": se, "drift_amp": drift_amp,
                  "g0_hat": g0_hat, "g1_hat": g1_hat, "lam_hat": lam_hat,
                  "g_spread": float(np.std(g0s) + np.std(g1s)),
                  "resid_pre": resid, "cmrr": float((drift_amp / resid) ** 2) if resid > 0 else np.inf}


def contamination(yC_by_probe, t_probe):
    """Does the CONTROL respond to the probe? An honest control's baseline is probe-INDEPENDENT.

    Pre-intervention the control's ensemble mean is identical across probes (same episode, deterministic carrier).
    Post-intervention it stays identical -- UNLESS the control is leaking the intervention. So the probe-to-probe
    spread of the control's ensemble mean, POST versus PRE, is a contamination detector that needs NO oracle.
    """
    M = np.stack([np.asarray(v, float).mean(axis=0) for v in yC_by_probe])  # (P, T)
    dev = M - M.mean(axis=0, keepdims=True)
    T = M.shape[1]
    pre = float(np.abs(dev[:, :t_probe]).max())
    post = float(np.abs(dev[:, t_probe:min(T, t_probe + W_FIXED)]).max())
    return {"pre": pre, "post": post, "ratio": post / pre if pre > 0 else np.inf,
            "contaminated": bool(pre > 0 and post / pre > CONTAM_K)}
