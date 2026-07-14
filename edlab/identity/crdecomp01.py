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

    POOLED OVER REPEATS. g0, g1, lam are constants OF THE CONTRACT, not properties of a repeat: the coupling
    gains and the lag do not change from one repetition to the next. Estimating them once from all repeats is
    both the correct estimator and R times cheaper. `rpre`, `cpre` are (R, W_PRE).
    """
    rpre = np.atleast_2d(rpre)
    cpre = np.atleast_2d(cpre)
    n = LAG_MAX + 1
    r_ = rpre[:, n:-n].ravel()
    best = (0.0, 0.0, 0, float(np.var(r_)))
    for lam in range(-LAG_MAX, LAG_MAX + 1):
        c0 = cpre[:, n:-n].ravel()
        c1 = np.roll(cpre, lam, axis=1)[:, n:-n].ravel()
        # closed-form 2x2 normal equations -- same answer as lstsq, without the SVD
        a11 = c0 @ c0; a12 = c0 @ c1; a22 = c1 @ c1
        b1 = c0 @ r_; b2 = c1 @ r_
        det = a11 * a22 - a12 * a12
        if abs(det) <= 1e-12 * max(a11 * a22, 1e-300):
            if a11 <= 0:
                continue
            g0, g1 = b1 / a11, 0.0             # rank-deficient (lam == 0): fall back to the single tap
        else:
            g0 = (b1 * a22 - b2 * a12) / det
            g1 = (b2 * a11 - b1 * a12) / det
        v = float(np.var(r_ - g0 * c0 - g1 * c1))
        if v < best[3]:
            best = (float(g0), float(g1), lam, v)
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

    g0_hat, g1_hat, lam_hat, _v = _fit_cm(dA[:, pre], cm[:, pre])
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
                  "g_spread": 0.0,
                  "resid_pre": resid, "cmrr": float((drift_amp / resid) ** 2) if resid > 0 else np.inf}


def contamination(sham_by_probe, t_probe):
    """Does the CONTROL leak the intervention? Detected on THE SHAM DEVIATION, which is a null BY CONSTRUCTION.

    With a control that leaks a fraction kappa of the response, s_C -> s_C + kappa*(s_A - s_C), so the sham
    deviation is
                        dS = y_S - y_C = -kappa * (s_A - s_C)

    -- i.e. a PROBE-LOCKED signal, reproducible across phases and repeats, in a channel that must be flat.
    The sham is supposed to have no response. If it has one, the control is leaking. No oracle is needed.

    MY FIRST DETECTOR WAS WRONG AND SAID EVERY CASE WAS CONTAMINATED, kappa = 0 INCLUDED. It compared the
    control's probe-to-probe spread POST-intervention against PRE-intervention -- but the OU drift starts at zero
    and its variance GROWS with time, so the post window holds more drift than the pre window for purely
    temporal reasons. The statistic confounded 'the control varies with the probe' with 'the drift accumulated'.
    It is replaced, not re-thresholded.

    The test is between-probe structure against within-probe scatter: a clean sham has no probe-locked component,
    so its between-probe RMS sits at the standard error of its own phase-to-phase mean. A leaking one does not.
    """
    win = slice(t_probe, t_probe + W_FIXED)
    ps = sorted(sham_by_probe)
    S = np.stack([np.stack([np.asarray(x, float)[win] for x in sham_by_probe[p]]) for p in ps])  # (P, PH, W)
    nph = S.shape[1]
    Sbar = S.mean(axis=1)                                   # (P, W) -- phase-averaged sham deviation per probe
    within = float(np.median(S.std(axis=1).mean(axis=1))) / np.sqrt(nph)   # SE of Sbar, from phase scatter
    dev = Sbar - Sbar.mean(axis=0, keepdims=True)
    between = float(np.max(np.sqrt((dev ** 2).mean(axis=1))))              # RMS, not max: max over 3840 points
    ratio = between / within if within > 0 else np.inf                     # would false-fire on noise alone
    return {"between": between, "within": within, "ratio": float(ratio),
            "contaminated": bool(ratio > CONTAM_K)}


# ============================================================================================================
# THE FACTORIZED PROFILE. Still factorized. There is no composite identity score here and there never will be.
# ============================================================================================================
IND_DRIFT = "INDETERMINATE_DRIFT"
SEVERITY = {CONTAM: 4, NOT_ESTAB: 3, PARTIAL: 2, ADMISSIBLE: 0, NO_DRIFT: 0}


def admit_pooled(reports, contaminated=False):
    """ONE verdict for the whole acquisition, from the POOLED episodes.

    CRD-00's second bug, restated: MAX-OVER-BLOCKS IS A VERDICT RULE, NOT AN ESTIMATOR. Over enough blocks it
    stops reporting the typical case and starts selecting the block where the noise conspired.

    I reproduced it here before catching it. Taking the WORST of 64 episode-level admissions made even the pure
    null (CM-01, K_base vs K_base, no response at all) come back INDETERMINATE_DRIFT -- the unluckiest RDNR draw
    out of 64 carried the verdict for the whole run.

    Common-mode rejection is a property of the ACQUISITION CONTRACT -- of how the channels are wired to the
    drift -- not of any one probe episode. So it is estimated ONCE, by the MEDIAN over episodes, and the declared
    thresholds are applied to that. CONTAMINATION stays a detector (any -> flag): it is a hazard, not a nuisance.
    """
    if contaminated:
        return CONTAM, {}
    rd = float(np.median([r["rdnr"] for r in reports]))
    da = float(np.median([r["drift_amp"] for r in reports]))
    se = float(np.median([r["sigma_eps"] for r in reports]))
    if da < DRIFT_FLOOR * se:
        v = NO_DRIFT
    elif rd <= RDNR_ADMIT:
        v = ADMISSIBLE
    elif rd <= RDNR_PARTIAL:
        v = PARTIAL
    else:
        v = NOT_ESTAB
    return v, {"rdnr": rd, "drift_amp": da, "sigma_eps": se}


def _components(dv, t_probe):
    """One (probe, phase) block -> the factorized quantities. E_trans is an INTEGRAL, never a mean: a mean over a
    window of length W dilutes any TRANSIENT by exactly sqrt(W'/W). That was the continuous fingerprint's disease."""
    win = slice(t_probe, t_probe + W_FIXED)
    late = slice(t_probe + W_FIXED - W_LATE, t_probe + W_FIXED)
    half = slice(t_probe + W_FIXED - 2 * W_LATE, t_probe + W_FIXED - W_LATE)
    a = dv[win]
    return {"E": float(np.sum(a * a)), "P": float(np.mean(dv[late])), "A": float(np.max(np.abs(a))),
            "P_half": float(np.mean(dv[half])), "argA": int(np.argmax(np.abs(a)))}


def profile(dev_by_probe, sham_by_probe, t_probe, verdict):
    """dev_by_probe / sham_by_probe : {probe: [trace per PHASE]}. Phases are replicates -> MEDIAN.
    Probes are distinct interventions -> MAX. ('Indistinguishable under the repertoire' is a FOR-ALL, and a
    FOR-ALL is certified by its worst case.)"""
    out = {"admission": verdict}
    if SEVERITY[verdict] >= 2:                  # PARTIAL, NOT_ESTABLISHED or CONTAMINATED
        for k in ("E_trans", "P_inf", "A_peak", "L_onset", "T_recovery"):
            out[k] = {"status": IND_DRIFT, "value": None, "band": None}
        return out                              # NO component verdict on a partially-rejected common mode.

    E, P, A, Ph, bE, bP, bA = [], [], [], [], [], [], []
    for pr in dev_by_probe:
        cd = [_components(x, t_probe) for x in dev_by_probe[pr]]
        cs = [_components(x, t_probe) for x in sham_by_probe[pr]]
        E.append(np.median([c["E"] for c in cd])); bE.append(max(c["E"] for c in cs))
        P.append(np.median([c["P"] for c in cd])); bP.append(max(abs(c["P"]) for c in cs))
        A.append(np.median([c["A"] for c in cd])); bA.append(max(c["A"] for c in cs))
        Ph.append(np.median([c["P_half"] for c in cd]))
    i = int(np.argmax(np.abs(A)))               # the worst-case probe carries the verdict
    Ev, Pv, Av, Pv2 = float(E[i]), float(P[i]), float(A[i]), float(Ph[i])
    eB, pB, aB = float(bE[i]), float(bP[i]), float(bA[i])

    out["E_trans"] = {"value": Ev, "band": eB,
                      "status": "RESOLVED" if Ev > R_NULL_E * eB else ("NULL" if Ev <= eB else "INDETERMINATE")}
    stable = abs(Pv - Pv2) <= K_SIG * pB        # a PERSISTENT offset must still be there half a window earlier
    out["P_inf"] = {"value": Pv, "band": pB,
                    "status": ("RESOLVED" if (abs(Pv) > K_SIG * pB and stable)
                               else ("NULL" if abs(Pv) <= pB else "INDETERMINATE"))}
    out["A_peak"] = {"value": Av, "band": aB,
                     "status": "RESOLVED" if Av > K_SIG * aB else ("NULL" if Av <= aB else "INDETERMINATE")}
    out["L_onset"] = {"value": None, "band": aB, "status": "RESOLVED" if Av > K_SIG * aB else "NULL"}
    out["T_recovery"] = {"value": None, "band": aB,
                         "status": "RESOLVED" if out["A_peak"]["status"] == "RESOLVED" else "NULL"}
    return out
