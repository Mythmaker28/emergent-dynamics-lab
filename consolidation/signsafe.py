"""SIGN-SAFE REFERENCE IDENTIFICATION — EXP-GT-SIGN-SAFE-REFERENCE-IDENTIFICATION-00.

Independent instrument. Imports numpy only; not a patch of frozen CRD-03. It NEVER uses max-amplitude as an
implicit default. It computes the IDENTIFIED SET for the true response magnitude |q| given the drift-free
channels v_i = q(1 - alpha_i kappa_i) and a DECLARED contract, and emits a point ONLY when the identifying
assumptions are independently supplied.

Contracts (declared by the caller from independent evidence, never inferred from the amplitude ordering):
  clean_anchor : at least one reference is uncontaminated (identity unknown)
  sign         : 'attenuate' (alpha_i kappa_i >= 0), 'amplify' (<=0), or None (unknown)

Identified set for |q| (proved in docs/consolidation/SET_IDENTIFICATION_MANUSCRIPT.md):
  clean_anchor + channels agree      -> POINT               |q| = common value
  clean_anchor + disagree + sign     -> POINT               clean channel is the extreme picked by the sign
  clean_anchor + disagree + no sign  -> INTERVAL            |q| in [min|v|, max|v|]
  no anchor    + sign 'attenuate'    -> LOWER_BOUND_ONLY    |q| >= max|v|
  no anchor    + sign 'amplify'      -> UPPER_BOUND_ONLY    |q| <= min|v|
  no anchor    + no sign             -> NON_IDENTIFIABLE
  common-mode detected (all agree, no anchor) -> NON_IDENTIFIABLE (scale unrecoverable)
  coupling spread < floor            -> REFERENCE_MIXTURE_ILL_CONDITIONED
"""
from __future__ import annotations
import numpy as np

DIVERSITY_FLOOR = 0.15
AGREE_FLOOR = 0.045

POINT="POINT_IDENTIFIED"; INTERVAL="INTERVAL_IDENTIFIED"; LOWER="LOWER_BOUND_ONLY"
UPPER="UPPER_BOUND_ONLY"; SETID="SET_IDENTIFIED"; NONID="NON_IDENTIFIABLE"
NEEDSIGN="SIGN_CONTRACT_REQUIRED"; ILL="REFERENCE_MIXTURE_ILL_CONDITIONED"; OOS="OUT_OF_SCOPE"


def channel_amplitudes(v, win):
    return np.array([float(np.std(v[i, win])) for i in range(v.shape[0])])


def coupling_spread(lam):
    inv = 1.0/np.where(np.abs(lam)>1e-9, lam, 1e-9)
    return float(np.std(inv)/(np.abs(np.mean(inv))+1e-30))


def identify(v, lam, onset, win_len, clean_anchor=False, sign=None):
    """v:(m,T) drift-free channels; lam:(m,) pre-window slopes. Returns (status, identified_set, report)."""
    m = v.shape[0]
    win = slice(onset, onset+win_len)
    pre = slice(max(0,onset-win_len), onset)
    spread = coupling_spread(lam)
    rep = {"spread": spread, "clean_anchor": clean_anchor, "sign": sign, "m": m}
    if spread < DIVERSITY_FLOOR:
        return ILL, None, rep
    amp = channel_amplitudes(v, win)
    nul = channel_amplitudes(v, pre)
    if np.median(amp) < 2.0*np.median(nul):
        rep["null_response"]=True
        return POINT, (0.0, 0.0), rep         # no response to identify
    lo, hi = float(amp.min()), float(amp.max())
    rep["amp"]=amp.tolist(); rep["bracket"]=(lo,hi)
    # do the channels AGREE (common value) or DISAGREE (contamination located)?
    rel = (hi-lo)/(0.5*(hi+lo)+1e-30)
    agree = rel < AGREE_FLOOR
    rep["agree"]=bool(agree)
    if clean_anchor:
        if agree:
            return POINT, (0.5*(lo+hi), 0.5*(lo+hi)), rep     # all agree incl. the clean one
        if sign=="attenuate":
            return POINT, (hi, hi), rep        # clean channel is the largest (others attenuated)
        if sign=="amplify":
            return POINT, (lo, lo), rep        # clean channel is the smallest (others amplified)
        return INTERVAL, (lo, hi), rep         # clean channel is an extreme, which one is unknown
    # NO clean anchor
    if agree:
        # every channel equal -> all clean OR common-mode. Without an anchor the scale is unrecoverable.
        return NONID, None, rep
    if sign=="attenuate":
        return LOWER, (hi, np.inf), rep        # max|v| is a valid lower bound
    if sign=="amplify":
        return UPPER, (0.0, lo), rep           # min|v| is a valid upper bound
    return NONID, None, rep


def point_estimate(v, status, iset, onset, win_len):
    """Return a point trace ONLY for POINT status; else None (the instrument refuses a point)."""
    if status != POINT:
        return None
    win = slice(onset, onset+win_len)
    amp = channel_amplitudes(v, win)
    target = iset[0]
    i = int(np.argmin(np.abs(amp - target)))
    return v[i]
