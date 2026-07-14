"""INDEPENDENT CLEAN-ROOM REIMPLEMENTATION of the CRD-03 method.

Written from docs/CRD03_PROTOCOL.md (the frozen scientific protocol) and the mathematical relations only.
It imports NO operational code: not pident, not racq, not exp_gt_crd03, not any historical instrument module.
It uses its own names, its own RNG interface, and its own tests.

Model (from the protocol):
    measurement   m(t) = q(t) + g0 * w(t)              q = causal response, w = environmental drift
    reference i   h_i(t) = g_i * w(t) + e_i * q(t)     e_i = contamination of reference i
    pre-window calibration (q = 0 there) gives  lam_i = g0/g_i
    drift-free    v_i(t) = m - lam_i * h_i = q * (1 - lam_i * e_i)

DEVIATION FROM THE HISTORICAL INSTRUMENT (deliberate, and the reason for this replication):
the historical recovery rule picks argmax_i |v_i| and calls it the cleanest channel. That is valid ONLY when
lam_i * e_i >= 0 for every i (contamination ATTENUATES). This module does NOT assume that. It reports the
BRACKET [min_i |v_i|, max_i |v_i|], which contains |q| whenever at least one reference is uncontaminated,
under EITHER sign, and it refuses to emit a point estimate unless a sign contract is supplied.
"""
from __future__ import annotations

import numpy as np

PRE_LEN = 480
WIN_LEN = 480
TAIL_LEN = 120
SPREAD_FLOOR = 0.045     # channels closer than this agree
DIVERSITY_FLOOR = 0.15


class Verdict:
    OK = "REFERENCES_CONSISTENT"
    LOCATED = "CONTAMINATION_LOCATED"
    ILLCOND = "MIXTURE_ILL_CONDITIONED"
    UNRESOLVED = "CONTAMINATION_UNRESOLVED"
    SIGN_UNKNOWN = "SIGN_CONTRACT_NOT_ESTABLISHED"


def _pre_slope(meas, refs):
    """lam_i = g0/g_i estimated on the pre-intervention window, where the response is zero by construction."""
    lam = []
    mv = np.concatenate([meas[0][:, :PRE_LEN].ravel(), meas[1][:, :PRE_LEN].ravel()])
    mv = mv - mv.mean()
    for i in range(refs[0].shape[1]):
        hv = np.concatenate([refs[0][:, i, :PRE_LEN].ravel(), refs[1][:, i, :PRE_LEN].ravel()])
        hv = hv - hv.mean()
        lam.append(float(mv @ hv / (hv @ hv)) if hv @ hv > 0 else 0.0)
    return np.array(lam)


def drift_free_channels(m_plus, m_minus, h_plus, h_minus):
    """Signed odd part removes baseline; per-reference correction removes drift. v_i = q_odd*(1 - lam_i e_i)."""
    lam = _pre_slope((m_plus, m_minus), (h_plus, h_minus))
    m_odd = (m_plus - m_minus) / 2.0
    h_odd = (h_plus - h_minus) / 2.0
    k = h_plus.shape[1]
    v = np.stack([(m_odd - lam[i] * h_odd[:, i, :]).mean(axis=0) for i in range(k)])
    return v, lam


def coupling_spread(lam):
    inv = 1.0 / np.where(np.abs(lam) > 1e-9, lam, 1e-9)
    return float(np.std(inv) / (np.abs(np.mean(inv)) + 1e-30))


def assess(m_plus, m_minus, h_plus, h_minus, onset=PRE_LEN, sign_contract=False):
    """Returns (bracket, point_or_None, report). Never emits a point estimate without a sign contract."""
    v, lam = drift_free_channels(m_plus, m_minus, h_plus, h_minus)
    k = v.shape[0]
    win = slice(onset, onset + WIN_LEN)
    pre = slice(max(0, onset - WIN_LEN), onset)
    rep = {"lam": lam.tolist(), "spread": coupling_spread(lam)}

    if rep["spread"] < DIVERSITY_FLOOR:
        rep["verdict"] = Verdict.ILLCOND
        return None, None, rep

    amp = np.array([float(np.std(v[i, win])) for i in range(k)])
    nul = np.array([float(np.std(v[i, pre])) for i in range(k)])
    if np.median(amp) < 2.0 * np.median(nul):          # nothing responded to this probe
        rep["verdict"] = Verdict.OK
        rep["null"] = True
        return (0.0, 0.0), np.median(v, axis=0), rep

    def spread(i, j):
        a, b = v[i, win], v[j, win]
        return float(np.std(a - b) / (0.5 * (np.std(a) + np.std(b)) + 1e-30))

    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    dis = {p: spread(*p) for p in pairs}
    rep["disagreement"] = {f"{i}{j}": d for (i, j), d in dis.items()}

    lo_i, hi_i = int(np.argmin(amp)), int(np.argmax(amp))
    bracket = (float(amp[lo_i]), float(amp[hi_i]))
    rep["bracket"] = bracket

    if max(dis.values()) < SPREAD_FLOOR:
        # every channel agrees: all clean OR common-mode contaminated (indistinguishable)
        rep["verdict"] = Verdict.OK
        rep["common_mode_possible"] = True
        point = np.median(v, axis=0) if sign_contract else None
        if not sign_contract:
            rep["verdict"] = Verdict.SIGN_UNKNOWN
        return bracket, point, rep

    # channels disagree -> at least one is contaminated. WITHOUT a sign contract we cannot say whether the
    # clean channel sits at the MAX (attenuating contamination) or the MIN (amplifying contamination).
    rep["verdict"] = Verdict.LOCATED
    if not sign_contract:
        rep["verdict"] = Verdict.SIGN_UNKNOWN
        rep["note"] = "clean channel is at an extreme, but which end is unresolved without sign(lam*e)>=0"
        return bracket, None, rep
    # sign contract asserted (lam_i*e_i >= 0 => contamination attenuates) -> clean channel is the MAX
    clean = [j for j in range(k) if j == hi_i or spread(hi_i, j) < SPREAD_FLOOR]
    if len(clean) < 2:
        rep["verdict"] = Verdict.UNRESOLVED
        return bracket, None, rep
    rep["clean_set"] = clean
    return bracket, np.median(v[clean], axis=0), rep


def components(q_hat, onset=PRE_LEN):
    """Factorized response components. Energy is an INTEGRAL (never a window mean: a mean dilutes transients)."""
    win = slice(onset, onset + WIN_LEN)
    tail = slice(onset + WIN_LEN - TAIL_LEN, onset + WIN_LEN)
    seg = q_hat[win]
    return {"energy": float(np.sum(seg * seg)),
            "peak": float(np.max(np.abs(seg))),
            "persistence": float(np.mean(q_hat[tail])),
            "latency": int(np.argmax(np.abs(seg)))}
