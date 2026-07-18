"""CRD-02 substrate constructions. ADDITIVE ONLY. The v00 freeze and the CRD-01 freeze are not touched.

CRD-01's prospective split reserved slow / persistent / transient responses. CRD-02's split must reserve
combinations that instrument has NEVER seen, so the topologies below are new: third-order cascades, underdamped
(oscillatory) responses, hidden state, sign inversion, and multi-timescale paths.
"""
from __future__ import annotations

from .engine import DRIVE, LINEAR, Spec
from .systems import _blank, _set
from .decomp import base  # noqa: F401  (re-exported: the CRD-00/01 base is the same reference system)


def _copy(b: Spec, name) -> Spec:
    """Spec has no .copy(); the arrays must be deep-copied or every construction mutates the base in place."""
    s = Spec(**{**b.__dict__})
    s.name = name
    s.W, s.TAU = b.W.copy(), b.TAU.copy()
    s.T_site, s.C, s.bias, s.x0, s.K_site = (b.T_site.copy(), b.C.copy(), b.bias.copy(),
                                             b.x0.copy(), b.K_site.copy())
    s.kinds = tuple(b.kinds)
    return s


def _path(s, site, w, Tx, src=DRIVE, delay=0):
    s.kinds = _set(s.kinds, site, LINEAR)
    s.W[site, src] = 1.0
    s.TAU[site, src] = delay
    s.T_site[site] = Tx
    s.C[site] = w
    return s


def plus_cascade3(name, b: Spec, w: float, T1=10.0, T2=10.0, T3=10.0) -> Spec:
    """THIRD-ORDER. drive -> 3 -> 4 -> 5, read out at 5 only. Three poles: slow rise, long tail."""
    s = _copy(b, name)
    _path(s, 3, 0.0, T1)
    _path(s, 4, 0.0, T2, src=3)
    _path(s, 5, w, T3, src=4)
    s.meta = {"topology": "cascade3", "order": 3, "w": w, "T": (T1, T2, T3)}
    return s


def plus_underdamped(name, b: Spec, w: float, T=14.0, k=0.55) -> Spec:
    """UNDERDAMPED. Sites 3,4 cross-coupled with OPPOSITE signs -> a rotation in (x3,x4): ringing.
    The response overshoots and CHANGES SIGN, which is exactly what a peak-only estimator gets wrong."""
    s = _copy(b, name)
    _path(s, 3, w, T)
    _path(s, 4, 0.0, T)
    s.W[3, 4] = -k          # cross-coupling of opposite sign on the two arms
    s.W[4, 3] = +k          # -> complex pole pair -> damped oscillation
    s.meta = {"topology": "underdamped", "order": 2, "w": w, "k": k}
    return s


def plus_hidden(name, b: Spec, w: float, Th=30.0, Tv=6.0) -> Spec:
    """HIDDEN STATE. Site 4 is a slow integrator that is NEVER read out (C[4] = 0). It drives the observed
    site 3. The persistent difference lives in a variable the observer cannot see."""
    s = _copy(b, name)
    _path(s, 4, 0.0, Th)            # hidden: C = 0
    s.W[4, 4] = 1.0                 # integrator: the probe leaves a PERMANENT change in a HIDDEN variable
    _path(s, 3, w, Tv, src=4)       # observed only through site 3
    s.meta = {"topology": "hidden", "order": 2, "w": w, "hidden_site": 4}
    return s


def plus_signflip(name, b: Spec, w: float, Tx=8.0) -> Spec:
    """SIGN INVERSION. Same magnitude, opposite sign. An energy-only estimator is blind to this."""
    s = _copy(b, name)
    _path(s, 3, -abs(w), Tx)
    s.meta = {"topology": "signflip", "order": 1, "w": -abs(w)}
    return s


def plus_multiscale(name, b: Spec, w: float, Tf=3.0, Ts=60.0, split=0.5) -> Spec:
    """MULTI-TIMESCALE. Two parallel paths, fast and slow, summed at the readout."""
    s = _copy(b, name)
    _path(s, 3, w * split, Tf)
    _path(s, 4, w * (1.0 - split), Ts)
    s.meta = {"topology": "multiscale", "order": 1, "w": w, "T": (Tf, Ts)}
    return s


def plus_feedback(name, b: Spec, w: float, Tx=12.0, g=0.6) -> Spec:
    """FEEDBACK. Site 3 feeds site 4 which feeds back into 3 with positive gain -> slow effective timescale."""
    s = _copy(b, name)
    _path(s, 3, w, Tx)
    _path(s, 4, 0.0, Tx, src=3)
    s.W[3, 4] = g
    s.meta = {"topology": "feedback", "order": 2, "w": w, "g": g}
    return s
