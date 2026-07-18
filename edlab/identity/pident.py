"""CRD-03 -- REDUNDANTLY-REFERENCED, SIGNED-INTERVENTION IDENTIFIABILITY INSTRUMENT.

The theorem this instrument is built around (established on development ground truth, see docs/CRD03_PROTOCOL.md):

  With passive references r_i = a_i*d + kappa_i*s and measurement y = s + a*d, the ONLY drift-free signals are
  z_i = y - alpha_i*r_i = s*(1 - alpha_i*kappa_i), with alpha_i = a/a_i from the s=0 pre-window. The reference
  disagreement r_i - (a_i/a_j) r_j is a LINEAR COMBINATION of the z_i (proved symbolically). Consequences:

    * The response SHAPE is always identifiable.
    * DIFFERENTIAL contamination (the z_i disagree) is identifiable to kappa ~ 0.002, and under 'at most one
      reference contaminated' the AGREEING pair is clean and recovers |s| exactly.
    * COMMON-MODE contamination (kappa_i proportional to a_i, so every z_i attenuates identically) is EXACTLY
      unidentifiable AND undetectable by any passive-reference scheme. It requires an absolute-scale anchor.

So this instrument DETECTS and CORRECTS differential contamination (fixing CRD-02's single-reference floor of
kappa~0.15 down to ~0.01), and ABSTAINS-BY-DECLARATION on the common-mode direction rather than reporting a
confident attenuated number. Signed interventions remove drift for the odd component and expose an even component
for nonlinear responses; they do not resolve common-mode contamination.
"""
from __future__ import annotations

import numpy as np

# ---- PREREGISTERED. Frozen before any sweep or prospective system. ----
W_PRE = 480
W_FIXED = 480
W_LATE = 120
DISAGREE_CLEAN = 0.045      # pairwise drift-free disagreement below this = channels AGREE (clean baseline ~0.02)
DISAGREE_FLAG = 0.045       # a pair above this disagrees -> contamination present
DIVERSITY_MIN = 0.15        # min relative spread of drift couplings for references to be non-collinear
COND_MAX = 12.0             # observation-matrix condition number above this -> ill-conditioned -> abstain
K_SIG = 1.5
R_NULL_E = 25.0
COMP_NULL_K = 3.0           # complementary-probe response over its null band -> non-null -> contaminated region

# statuses
IDENT = "REFERENCE_SYSTEM_IDENTIFIABLE"
CORR = "REFERENCE_CONTAMINATION_CORRECTED"
DET = "REFERENCE_CONTAMINATION_DETECTED"
ILL = "REFERENCE_MIXTURE_ILL_CONDITIONED"
SIGNV = "SIGNED_CONTRACT_VIOLATED"
COMPN = "COMPLEMENTARY_PROBE_NON_NULL"
SCALE = "ABSOLUTE_SCALE_UNAVAILABLE"
IND = "INDETERMINATE_REFERENCE_CONTAMINATION"


def _odd_even(yP, yM):
    """Signed decomposition. Odd = (y(+u)-y(-u))/2 (drift cancels, s_odd survives); even = (y(+u)+y(-u))/2."""
    return (yP - yM) / 2.0, (yP + yM) / 2.0


def _calib(yP, yM, rP, rM):
    """alpha_i = a/a_i from the s=0 pre-window, pooled over signs and repeats. Drift couplings only -- no truth."""
    n = rP.shape[1]
    al = []
    yv = np.concatenate([yP[:, :W_PRE].ravel(), yM[:, :W_PRE].ravel()])
    yv = yv - yv.mean()
    for i in range(n):
        rv = np.concatenate([rP[:, i, :W_PRE].ravel(), rM[:, i, :W_PRE].ravel()])
        rv = rv - rv.mean()
        al.append(float(yv @ rv) / float(rv @ rv) if rv @ rv > 0 else 0.0)
    return np.array(al)


def _coupling_diversity(al):
    """References are useful only if their drift couplings differ. alpha_i = a/a_i, so spread of 1/alpha_i."""
    inv = 1.0 / np.where(np.abs(al) > 1e-9, al, 1e-9)
    return float(np.std(inv) / (np.abs(np.mean(inv)) + 1e-30))


def analyse(acq, t_probe=W_PRE):
    """Full identifiability analysis of one probe's signed, redundantly-referenced acquisition."""
    yP, yM, rP, rM = acq["yP"], acq["yM"], acq["rP"], acq["rM"]
    R, nref, T = rP.shape
    al = _calib(yP, yM, rP, rM)
    diversity = _coupling_diversity(al)

    # ODD, drift-free channels z_i = s_odd*(1-alpha_i kappa_i). The odd part (y+ - y-)/2 removes the baseline sC
    # (even in u) and the references remove the drift. The residual drift (d+ - d-)/2 is further suppressed by the
    # per-reference correction. Signed recovery targets the ODD response; ARM B's even part is a diagnostic.
    yO = (yP - yM) / 2.0
    rO = (rP - rM) / 2.0
    z = np.stack([(yO - al[i] * rO[:, i, :]).mean(axis=0) for i in range(nref)])   # (nref, T) ensemble mean
    w = slice(t_probe, t_probe + W_FIXED)

    def disagree(i, j):
        a, b = z[i, w], z[j, w]
        return float(np.std(a - b) / (0.5 * (np.std(a) + np.std(b)) + 1e-30))

    pairs = [(i, j) for i in range(nref) for j in range(i + 1, nref)]
    dis = {(i, j): disagree(i, j) for i, j in pairs}
    a_i = 1.0 / np.where(np.abs(al) > 1e-9, al, 1e-9)      # recovered drift couplings a_i (up to a)
    rep = {"alpha": al.tolist(), "diversity": diversity, "cond": float(max(a_i) / max(min(a_i), 1e-9)),
           "disagree": {f"{i}{j}": v for (i, j), v in dis.items()}}

    # reference diversity gate (D6 / must-fail 2: collinear references)
    if diversity < DIVERSITY_MIN:
        rep["status"] = ILL
        rep["cond"] = float("inf")
        return None, rep

    # NULL-RESPONSE GATE: a probe that does not excite the system carries no response. Its z is noise, and
    # noise-level "disagreement" is not contamination. Detect via odd-signal SNR against the pre-window.
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    sig_amp = float(np.median([np.std(z[i, w]) for i in range(nref)]))
    null_amp = float(np.median([np.std(z[i, pre]) for i in range(nref)])) + 1e-30
    if sig_amp < 2.0 * null_amp:
        rep["status"] = IDENT
        rep["null_response"] = True
        return np.median(z, axis=0), rep

    # RECOVERY PRINCIPLE: contamination ATTENUATES (kappa_i>=0, alpha_i>0 => |z_i| = |s|*(1-alpha_i kappa_i) <= |s|),
    # so the LARGEST-amplitude drift-free channel is the LEAST contaminated, and equals |s| exactly if any
    # reference is clean. This locates the clean set without assuming which references are clean.
    amp = np.array([float(np.std(z[i, w])) for i in range(nref)])
    istar = int(np.argmax(amp))                          # least-contaminated channel
    clean = [j for j in range(nref) if (j == istar or disagree(istar, j) < DISAGREE_CLEAN)]
    s_hat = np.median(z[clean], axis=0)
    maxdis = max(dis.values())
    rep["amp"] = amp.tolist()
    rep["clean_set"] = clean

    if maxdis < DISAGREE_CLEAN:
        # every channel agrees -> all clean OR common-mode (proportional) contamination -- indistinguishable.
        # s_hat is then a rigorous LOWER BOUND on |s| (contamination can only attenuate). Reported as such.
        rep["status"] = IDENT
        rep["common_mode_caveat"] = True
        rep["amplitude_is_lower_bound"] = True
        return s_hat, rep
    if len(clean) >= 2 and len(clean) < nref:
        # a strict subset agrees at the largest amplitude -> the rest are contaminated and LOCATED.
        # s_hat is EXACT under the declared contract "at least one reference in the clean set is uncontaminated"
        # (guaranteed if fewer than the full set are contaminated and couplings differ); a rigorous LOWER BOUND
        # otherwise. It is never a confident attenuated value presented as exact.
        rep["status"] = CORR
        rep["contaminated_ref"] = [k for k in range(nref) if k not in clean]
        rep["amplitude_is_lower_bound"] = True
        rep["exact_under_contract"] = True
        return s_hat, rep
    if len(clean) >= 2:
        rep["status"] = DET
        rep["amplitude_is_lower_bound"] = True
        return s_hat, rep
    # only the singleton stands at the top with everyone disagreeing -> cannot certify it is clean
    rep["status"] = IND
    return None, rep

def signed_consistency(acq, t_probe=W_PRE):
    """Is the response ODD in u? The EVEN part must be measured DRIFT-FREE, or residual drift (d+ + d- does not
    vanish across independent +/- episodes) masquerades as a sustained even component and false-flags clean
    linear responses. So the even part is reference-corrected: z_even = (y+ + y-)/2 - alpha_i*(r+ + r-)/2, drift
    removed the same way the odd channels remove it."""
    yP, yM, rP, rM = acq["yP"], acq["yM"], acq["rP"], acq["rM"]
    al = _calib(yP, yM, rP, rM)
    w = slice(t_probe, t_probe + W_FIXED)
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    yO = (yP - yM) / 2.0
    yEven = (yP + yM) / 2.0
    rEven = (rP + rM) / 2.0
    # drift-free even part: use the median over references of the corrected even signal
    zE = np.median(np.stack([(yEven - al[i] * rEven[:, i, :]).mean(0) for i in range(len(al))]), axis=0)
    odd_pow = float(np.std(yO[:, w].mean(0)))
    odd_null = float(np.std(yO[:, pre].mean(0))) + 1e-30
    even_pow = float(np.std(zE[w] - zE[pre].mean()))
    even_null = float(np.std(zE[pre])) + 1e-30
    responsive = odd_pow > 3.0 * odd_null
    ev = zE[w] - zE[pre].mean()
    # HYSTERESIS SIGNATURE: an order-dependent history offset accumulates like the INTEGRAL of the response,
    # so the even part correlates with cumsum(odd response). Residual drift (OU) and a static even nonlinearity
    # (which follows the response, not its integral) do not. This separates hysteresis from both.
    odd_mean = yO[:, w].mean(0)
    cum = np.cumsum(odd_mean - odd_mean.mean())
    cum = cum - cum.mean()
    evc = ev - ev.mean()
    denom = (np.std(evc) * np.std(cum) + 1e-30)
    hyst_corr = float(np.mean(evc * cum) / denom)          # correlation of even part with the response integral
    frac = even_pow / (odd_pow + 1e-30)
    sig = bool(frac > 0.25)
    return {"odd": odd_pow, "even": even_pow, "even_null": even_null, "responsive": responsive,
            "even_significant": bool(sig and responsive), "even_frac": frac, "hyst_corr": hyst_corr,
            "hysteretic": bool(responsive and frac > 0.25 and abs(hyst_corr) > 0.6)}

def complementary_null(acq, t_probe=W_PRE):
    """A complementary probe aimed at a region that must NOT carry the response. Its drift must be removed first
    (residual drift across independent +/- episodes is not a response), THEN a surviving probe-locked signal
    means the region is not passive. Drift-corrected against reference 0 (declared coupling a_comp = 1)."""
    cP, cM, rP, rM, yP, yM = acq["cP"], acq["cM"], acq["rP"], acq["rM"], acq["yP"], acq["yM"]
    al = _calib(yP, yM, rP, rM)
    # comp = comp_kappa*s + a_comp*d ; reference r0 = a_0*d + ... ; alpha0 = a/a_0, a_comp=1 => correct with 1/a_0
    inv_a0 = 1.0 / (1.0 / al[0]) if al[0] != 0 else 0.0     # a_0 = a/al[0]; scale so a_comp*d cancels
    cO = ((cP - cM) / 2.0).mean(0)
    r0O = ((rP[:, 0, :] - rM[:, 0, :]) / 2.0).mean(0)
    scale = float(np.dot(cO[:t_probe], r0O[:t_probe]) / (np.dot(r0O[:t_probe], r0O[:t_probe]) + 1e-30))  # pre-window
    cc = cO - scale * r0O                                   # drift-removed complementary odd signal
    w = slice(t_probe, t_probe + W_FIXED)
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    sig = float(np.std(cc[w]))
    null = float(np.std(cc[pre])) + 1e-12
    return {"ratio": sig / null, "non_null": bool(sig / null > COMP_NULL_K)}
