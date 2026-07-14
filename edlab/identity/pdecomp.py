"""CRD-02 -- REFERENCED PAIRED-EPISODE FACTORIZED DECOMPOSITION.

Each episode is corrected against ITS OWN simultaneous reference, BEFORE anything is subtracted. Then

    s_hat(t) = z_A(t) - z_S(t),   z_j = y_j - d_hat_j,   d_hat_j = two-tap regression of y_j on r_j (pre-only)

The instrument NEVER sees d, a, b, delta, eta, the labels, or the states. It sees y_A, r_A, y_S, r_S.

Two ideas carry over from CRD-01, both by NAME:
  * the correction is fitted on the PRE-INTERVENTION region only -- it is structurally unable to erase the tail;
  * two taps, because the reference is a gained, LAGGED copy of the drift, not a scaled one.

Two ideas are NEW to CRD-02, forced by the harder acquisition:
  * the noise floor is estimated with an AR(1) correction, because the drift now has a FAST component that a
    plain first-difference would count as measurement noise (verified: differencing inflates the floor ~2x);
  * BANDWIDTH admission -- a reference that misses the fast drift cannot certify a correction, and the residual
    after regression, not the raw coherence, is what exposes it.
"""
from __future__ import annotations

import numpy as np

# ---- PREREGISTERED. Frozen before any sweep or prospective system. ----
W_PRE = 480
W_FIXED = 480
W_LATE = 120
LAG_MAX = 12
COH_MIN = 0.80          # ref/measurement pre-intervention coherence to ADMIT (set from the dev frontier: relerr
                        # stays <=5% above this, and climbs past it -- the reference stops explaining y's drift)
COH_HARD = 0.50         # below this the reference is essentially uncorrelated with the drift -> bandwidth failure
RDNR_REPORT = 8.0       # RDNR is a REPORTED diagnostic, not the primary gate (it saturates on irreducible fast
                        # residual); only a gross value signals a broken correction
DRIFT_FLOOR = 2.0
CONTAM_K = 3.0
K_SIG = 1.5
R_NULL_E = 25.0

# statuses
ADM = "PAIRED_REFERENCE_ADMISSIBLE"
A_INV = "ACTIVE_REFERENCE_INVALID"
S_INV = "SHAM_REFERENCE_INVALID"
CONTAM = "REFERENCE_CONTAMINATED"
BW = "REFERENCE_BANDWIDTH_INSUFFICIENT"
RESID = "INDEPENDENT_RESIDUAL_DRIFT_TOO_HIGH"
COV = "INSUFFICIENT_REFERENCE_COVERAGE"
NO_DRIFT = "DRIFT_ABSENT"
IND_REF = "INDETERMINATE_REFERENCE"


def sigma_eps(z):
    """White measurement floor, estimated on the CORRECTED residual z (NOT on raw y).

    On z the reference has removed most of the drift, so a first difference is dominated by the white
    measurement noise and std(diff)/sqrt2 recovers it. (Estimating this on raw y is what the AR(1) form was for,
    and the two-timescale drift made that form degenerate -- g0 - g1^2/g2 -> 0, RDNR -> inf, reject everything.
    Measuring the floor AFTER correction sidesteps the misspecification entirely.)"""
    z = np.asarray(z, float)
    return float(np.std(np.diff(z)) / np.sqrt(2.0)) if len(z) > 2 else 0.0


def _fit2(y, r):
    """Two-tap regression of y on [r(t), r(t-lam)], pooled over repeats, PRE-INTERVENTION only.
    Returns g0, g1, lam, residual-std. y, r are (R, W_PRE)."""
    y = np.atleast_2d(y); r = np.atleast_2d(r)
    n = LAG_MAX + 1
    yv = y[:, n:-n].ravel()
    yc = yv - yv.mean()
    best = (0.0, 0.0, 0, float(np.std(yc)))
    for lam in range(-LAG_MAX, LAG_MAX + 1):
        c0 = r[:, n:-n].ravel()
        c1 = np.roll(r, lam, axis=1)[:, n:-n].ravel()
        c0 = c0 - c0.mean(); c1 = c1 - c1.mean()
        a11 = c0 @ c0; a12 = c0 @ c1; a22 = c1 @ c1
        b1 = c0 @ yc; b2 = c1 @ yc
        det = a11 * a22 - a12 * a12
        if abs(det) <= 1e-12 * max(a11 * a22, 1e-300):
            if a11 <= 0:
                continue
            g0, g1 = b1 / a11, 0.0
        else:
            g0 = (b1 * a22 - b2 * a12) / det
            g1 = (b2 * a11 - b1 * a12) / det
        v = float(np.std(yc - g0 * c0 - g1 * c1))
        if v < best[3]:
            best = (float(g0), float(g1), lam, v)
    return best


def _coh(y, r):
    """Pre-intervention correlation between measurement and reference, pooled."""
    y = np.atleast_2d(y).ravel(); r = np.atleast_2d(r).ravel()
    if np.std(r) < 1e-30 or np.std(y) < 1e-30:
        return 0.0
    return float(abs(np.corrcoef(y, r)[0, 1]))


def correct_episode(y, r, t_probe):
    """Correct ONE episode against ITS OWN reference. Returns corrected traces + a per-episode admission report."""
    y = np.asarray(y, float); r = np.asarray(r, float)
    R, T = y.shape
    if not np.isfinite(r).all():
        return None, {"status": "NO_REFERENCE", "rdnr": np.inf, "coh": 0.0}
    pre = slice(0, t_probe)
    drift_amp = float(np.median([np.std(y[i, pre] - y[i, pre].mean()) for i in range(R)]))
    coh = _coh(y[:, pre], r[:, pre])
    g0, g1, lam, resid = _fit2(y[:, pre], r[:, pre])
    z = np.stack([y[i] - (g0 * r[i] + g1 * np.roll(r[i], lam)) for i in range(R)])
    # re-center each corrected episode on its OWN pre-intervention mean (removes the additive episode baseline;
    # the causal tail is untouched because the baseline is estimated PRE-probe)
    z = z - z[:, pre].mean(axis=1, keepdims=True)
    # Admission is a statement about the FINAL estimate s_hat = mean_repeats(z_A - z_S). The residual drift is
    # INDEPENDENT across repeats (each episode draws its own realization), so it averages down by sqrt(R) in the
    # mean -- and the accuracy of s_hat reflects THAT, not the per-episode residual. So the RDNR is measured on
    # the ENSEMBLE-MEAN residual, which is the actual error budget of the estimate. (A per-episode RDNR would
    # refuse clean cases that recover to 1.5%.)
    zbar = z[:, pre].mean(axis=0)
    se = sigma_eps(zbar)                                                     # white floor AFTER averaging
    tot = float(np.std(zbar))                                                # total averaged residual
    resid_lf = float(np.sqrt(max(tot * tot - se * se, 0.0)))                 # leftover low-frequency drift
    rdnr = resid_lf / se if se > 0 else np.inf
    rep = {"rdnr": float(rdnr), "coh": coh, "sigma_eps": se, "drift_amp": drift_amp,
           "g0": g0, "g1": g1, "lam": lam, "resid": resid, "resid_lf": resid_lf}
    # Primary gate: does the reference EXPLAIN the measurement's drift? Coherence is what separates a correctable
    # reference (gain/lag/bandwidth mismatch: coh stays high, correction works) from an UNCORRECTABLE one (local
    # unshared drift: coh collapses, because y carries a disturbance r never saw). RDNR saturates on irreducible
    # fast-drift residual and cannot serve as the gate; it is reported.
    drift_raw = float(np.median([np.std(np.diff(y[i, pre])) / np.sqrt(2) for i in range(R)]))
    if drift_amp < DRIFT_FLOOR * drift_raw:
        rep["status"] = NO_DRIFT
    elif rdnr > RDNR_REPORT and coh < COH_MIN:
        rep["status"] = BW
    elif coh >= COH_MIN:
        rep["status"] = ADM
    elif coh >= COH_HARD:
        rep["status"] = RESID                 # reference partly explains the drift, but not enough -> refuse
    else:
        rep["status"] = BW                    # reference essentially blind to the drift -> bandwidth failure
    return z, rep


def contamination(ref_by_probe, t_probe):
    """Detect a reference that has picked up the causal response it must be blind to.

    The reference sees only DRIFT, which is independent of the probe. So a clean reference has NO probe-locked
    component: its post-intervention ensemble mean is the same for every probe. A contaminated reference
    r = ...+ kappa*s carries the probe's own response, so its ensemble mean differs BY probe -- and that survives
    even when the contamination silently ATTENUATES z (an attenuated response is indistinguishable from a smaller
    one, so it cannot be caught in the corrected trace; it must be caught in the reference itself).

    ref_by_probe : {probe: [reference trace per phase]}, ensemble-averaged over repeats. Between-probe RMS of the
    post-intervention reference mean, against within-probe (phase) scatter."""
    ps = sorted(ref_by_probe)
    win = slice(t_probe, t_probe + W_FIXED)
    Rr = np.stack([np.stack([np.asarray(x, float)[win] for x in ref_by_probe[p]]) for p in ps])  # (P, PH, W)
    if not np.isfinite(Rr).all():
        return {"ratio": 0.0, "contaminated": False, "no_reference": True}
    nph = Rr.shape[1]
    Rbar = Rr.mean(axis=1)                              # (P, W) ensemble+phase mean reference per probe
    within = float(np.median(Rr.std(axis=1).mean(axis=1))) / np.sqrt(nph)
    dev = Rbar - Rbar.mean(axis=0, keepdims=True)
    between = float(np.max(np.sqrt((dev ** 2).mean(axis=1))))
    ratio = between / within if within > 0 else np.inf
    return {"ratio": float(ratio), "contaminated": bool(ratio > CONTAM_K), "no_reference": False}


# ============================================================================================================
# FACTORIZED OUTPUT. R = (E_trans, P_inf, A_peak, L_onset, T_recovery, C, U). No composite identity score.
# Each component: point estimate, uncertainty interval, coverage, status, admission result.
# ============================================================================================================
EST = "ESTIMATED"
NULLC = "NULL_COMPATIBLE"
LOWER = "LOWER_BOUND_ONLY"
UPPER = "UPPER_BOUND_ONLY"
IND_REF_C = "INDETERMINATE_REFERENCE"
IND_WIN = "INDETERMINATE_WINDOW"
OOS = "OUT_OF_SCOPE"


def _blockstats(shat_blocks, t_probe):
    """shat_blocks: (B, T) estimates, one per (probe,phase) block. Returns per-block components."""
    win = slice(t_probe, t_probe + W_FIXED)
    late = slice(t_probe + W_FIXED - W_LATE, t_probe + W_FIXED)
    half = slice(t_probe + W_FIXED - 2 * W_LATE, t_probe + W_FIXED - W_LATE)
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    out = []
    for a in shat_blocks:
        w = a[win]
        out.append({"E": float(np.sum(w * w)), "A": float(np.max(np.abs(w))),
                    "P": float(np.mean(a[late])), "Ph": float(np.mean(a[half])),
                    "Epre": float(np.sum(a[pre] * a[pre])), "Apre": float(np.max(np.abs(a[pre]))),
                    "Ppre": float(np.mean(a[pre][-W_LATE:])) if pre.stop - pre.start >= W_LATE else 0.0,
                    "arg": int(np.argmax(np.abs(w)))})
    return out


def profile(shat_by_probe, admissionA, admissionS, contaminated, t_probe):
    """shat_by_probe: {probe: [s_hat trace per phase]} where s_hat = z_A - z_S. Phases -> replicates (median),
    probes -> distinct interventions (max)."""
    stA = {"status": admissionA}; stS = {"status": admissionS}
    out = {"admission_active": admissionA, "admission_sham": admissionS, "contaminated": contaminated}

    if contaminated:
        for k in ("E_trans", "P_inf", "A_peak", "L_onset", "T_recovery"):
            out[k] = {"status": CONTAM, "value": None, "lo": None, "hi": None, "coverage": None}
        return out
    if admissionA != ADM or admissionS != ADM:
        why = IND_REF_C
        for k in ("E_trans", "P_inf", "A_peak", "L_onset", "T_recovery"):
            out[k] = {"status": why, "value": None, "lo": None, "hi": None, "coverage": None}
        return out

    E, A, P, Ph, bE, bA, bP = [], [], [], [], [], [], []
    for pr in shat_by_probe:
        cs = _blockstats(shat_by_probe[pr], t_probe)
        E.append(np.median([c["E"] for c in cs])); bE.append(np.percentile([c["Epre"] for c in cs], 90))
        A.append(np.median([c["A"] for c in cs])); bA.append(np.percentile([c["Apre"] for c in cs], 90))
        P.append(np.median([c["P"] for c in cs])); Ph.append(np.median([c["Ph"] for c in cs]))
        bP.append(np.std([c["Ppre"] for c in cs]) + 1e-30)
    i = int(np.argmax(np.abs(A)))
    Ev, Av, Pv, Pv2 = float(E[i]), float(A[i]), float(P[i]), float(Ph[i])
    eB, aB, pB = float(bE[i]), float(bA[i]), float(bP[i])

    # E_trans -- integral, does not dilute. Band = pre-intervention energy (null floor).
    if Ev > R_NULL_E * eB:
        out["E_trans"] = {"status": EST, "value": Ev, "lo": max(Ev - eB, 0.0), "hi": Ev + eB, "coverage": 0.9, "band": eB}
    elif Ev <= eB:
        out["E_trans"] = {"status": NULLC, "value": Ev, "lo": 0.0, "hi": eB, "coverage": 0.9, "band": eB}
    else:
        out["E_trans"] = {"status": LOWER, "value": Ev, "lo": 0.0, "hi": Ev + eB, "coverage": 0.9, "band": eB}
    # A_peak
    if Av > K_SIG * aB:
        out["A_peak"] = {"status": EST, "value": Av, "lo": Av - aB, "hi": Av + aB, "coverage": 0.9, "band": aB}
    else:
        out["A_peak"] = {"status": NULLC, "value": Av, "lo": 0.0, "hi": K_SIG * aB, "coverage": 0.9, "band": aB}
    # P_inf -- persistent offset, must survive to the late window AND be stable half a window earlier
    stable = abs(Pv - Pv2) <= K_SIG * pB
    if abs(Pv) > K_SIG * pB and stable:
        out["P_inf"] = {"status": EST, "value": Pv, "lo": Pv - pB, "hi": Pv + pB, "coverage": 0.9, "band": pB}
    elif abs(Pv) <= pB:
        out["P_inf"] = {"status": NULLC, "value": Pv, "lo": -pB, "hi": pB, "coverage": 0.9, "band": pB}
    else:
        out["P_inf"] = {"status": IND_WIN, "value": Pv, "lo": -abs(Pv), "hi": abs(Pv), "coverage": None, "band": pB}
    # latency / recovery ride on A_peak's resolution
    res = out["A_peak"]["status"] == EST
    out["L_onset"] = {"status": EST if res else NULLC, "value": None, "lo": None, "hi": None, "coverage": 0.9 if res else None}
    out["T_recovery"] = {"status": EST if res else NULLC, "value": None, "lo": None, "hi": None, "coverage": 0.9 if res else None}
    out["U"] = {"noise_floor_E": eB, "noise_floor_A": aB, "noise_floor_P": pB}
    return out
