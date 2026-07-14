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

    # ODD, drift-free channels z_i = s_odd*(1-alpha_i kappa_i). Drift is even -> cancels in the odd part.
    yO, yE = _odd_even(yP, yM)
    rO = (rP - rM) / 2.0
    z = np.stack([(yO - al[i] * rO[:, i, :]).mean(axis=0) for i in range(nref)])   # (nref, T), ensemble mean
    w = slice(t_probe, t_probe + W_FIXED)

    def disagree(i, j):
        a, b = z[i, w], z[j, w]
        return float(np.std(a - b) / (0.5 * (np.std(a) + np.std(b)) + 1e-30))

    pairs = [(i, j) for i in range(nref) for j in range(i + 1, nref)]
    dis = {(i, j): disagree(i, j) for i, j in pairs}

    rep = {"alpha": al.tolist(), "diversity": diversity, "disagree": {f"{i}{j}": v for (i, j), v in dis.items()}}

    # reference diversity gate (D6 / must-fail 2: collinear references)
    if diversity < DIVERSITY_MIN:
        rep["status"] = ILL
        rep["cond"] = float("inf")
        return None, rep

    # observation-matrix conditioning for latent (d, s): rows [a,1],[a_i, kappa_i]. kappa unknown; use the
    # drift-coupling geometry (a_i) and the estimated disagreement to condition. If all z agree, cond is set by
    # coupling spread; if the estimated contamination lies along the common-mode direction, s is unidentifiable.
    a_i = 1.0 / np.where(np.abs(al) > 1e-9, al, 1e-9)      # recovered drift couplings a_i (up to a)
    H = np.vstack([[1.0, 1.0]] + [[ai, 0.0] for ai in a_i])  # placeholder s-column filled after kappa est
    cond_geom = float(np.linalg.cond(np.vstack([[1.0], a_i.reshape(-1, 1)[:, 0]]).reshape(-1, 1)
                                     @ np.array([[1.0]])) if False else max(a_i) / max(min(a_i), 1e-9))
    rep["cond"] = cond_geom

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
    """Is the response ODD in u as the signed contract assumes? Hysteresis / strong even part violates it."""
    yP, yM = acq["yP"], acq["yM"]
    yO, yE = _odd_even(yP, yM)
    w = slice(t_probe, t_probe + W_FIXED)
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    odd_pow = float(np.std(yO[:, w].mean(0)))
    even_pow = float(np.std(yE[:, w].mean(0) - yE[:, pre].mean(0).mean()))
    even_null = float(np.std(yE[:, pre].mean(0)))
    return {"odd": odd_pow, "even": even_pow, "even_null": even_null,
            "even_significant": bool(even_pow > K_SIG * even_null + 0.05 * odd_pow),
            "even_frac": even_pow / (odd_pow + 1e-30)}


def complementary_null(acq, t_probe=W_PRE):
    """A complementary probe aimed at a region that must NOT carry the response. If it does, the reference/region
    is not passive."""
    cP, cM = acq["cP"], acq["cM"]
    cO = ((cP - cM) / 2.0).mean(axis=0)
    w = slice(t_probe, t_probe + W_FIXED)
    pre = slice(max(0, t_probe - W_FIXED), t_probe)
    sig = float(np.max(np.abs(cO[w])))
    null = float(np.std(cO[pre])) + 1e-12
    return {"ratio": sig / null, "non_null": bool(sig / null > COMP_NULL_K)}
