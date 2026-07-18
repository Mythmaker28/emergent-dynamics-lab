"""TAIL FAMILIES for EXP-GT-CONTINUOUS-FINGERPRINT-01.

ADDITIVE ONLY. Nothing in `engine.py`, `systems.py`, `manifests.py`, `evaluator.py` or `cfingerprint.py` is
touched, because those six files carry the sha256 of the v00 freeze and that record must remain verifiable. Every
family below is hosted by the UNCHANGED engine -- verified before a line of this file was written.

WHY THESE FAMILIES. Version 00 died on a single conflation:

    "the signal is still moving"   !=   "the unobserved remainder can still change the verdict"

`P_cascade`'s tail was moving by 5.3% of peak against a frozen 5% threshold, so v00 abstained -- on a pair it had
already separated by 64.15 against a radius of 23.36. To attack that honestly the benchmark needs tails that vary
along the axis that actually matters: **how much of the eventual answer is still outside the window.**
"""

from __future__ import annotations

import numpy as np

from .engine import DRIVE, SUPPLY, LINEAR, Spec
from .systems import _blank, _set, G0, SIG0


def first_order(name, tau=0, T=8.0, gain=1.0, sign=+1, **kw) -> Spec:
    """A clean exponential decay. The tail is over almost as soon as it starts."""
    s = _blank(name, **kw)
    s.kinds = _set(s.kinds, 2, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.T_site[2] = T
    s.C[2] = sign * gain
    s.meta = {"topology": "first_order", "tail": "first_order", "T": T, "tau": tau, "gain": gain}
    return s


def cascade_n(name, Ts=(6.0, 18.0), tau=0, gain=1.0, **kw) -> Spec:
    """N leaky sites in series. Second order (and, prospectively, THIRD) -- the tail that killed version 00.

    A cascade's relaxation is a SUM of exponentials, so its late tail decays more slowly than any single one of its
    time constants suggests. That is the entire reason a threshold calibrated on first-order transients does not
    transfer to it."""
    s = _blank(name, **kw)
    sites = [2, 3, 4][:len(Ts)]
    prev = DRIVE
    for i, (site, T) in enumerate(zip(sites, Ts)):
        s.kinds = _set(s.kinds, site, LINEAR)
        s.W[site, prev] = 1.0
        if i == 0:
            s.TAU[site, DRIVE] = tau
        s.T_site[site] = T
        prev = site
    s.C[sites[-1]] = gain
    s.meta = {"topology": "cascade%d" % len(Ts), "tail": "cascade%d" % len(Ts),
              "Ts": list(Ts), "tau": tau, "gain": gain}
    return s


def underdamped(name, k=6.0, T2=6.0, T3=10.0, gain=1.0, tau=0, **kw) -> Spec:
    """Complex poles: a RINGING relaxation. Its envelope decays while the signal itself keeps changing sign.

    A guard that asks "is the signal still moving?" answers YES here at almost every sample, forever, and abstains
    on a system whose remaining energy is negligible. A guard that asks "can the remainder change the verdict?"
    does not care that it is ringing -- only how loudly."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.W[2, 3] = -k
    s.W[3, 2] = 1.0
    s.T_site[2], s.T_site[3] = T2, T3
    s.C[2] = gain
    s.meta = {"topology": "underdamped", "tail": "underdamped", "k": k, "T2": T2, "T3": T3, "gain": gain}
    return s


def multiscale(name, T_fast=4.0, w_fast=1.0, T_slow=30.0, w_slow=0.10, tau=0, gain=1.0, **kw) -> Spec:
    """Two PARALLEL paths: a fast one that dominates the peak and a slow one that dominates the tail.

    `w_slow` is the knob the whole experiment turns on. Small -> a long tail that is real but cannot move the
    verdict (DECIDABLE_SLOW_TAIL). Large -> a long tail carrying enough of the answer that truncating it is
    truncating the conclusion (INDETERMINATE_IN_FLIGHT)."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.T_site[2] = T_fast
    s.C[2] = gain * w_fast
    s.W[3, DRIVE] = 1.0
    s.TAU[3, DRIVE] = tau
    s.T_site[3] = T_slow
    s.C[3] = gain * w_slow
    s.meta = {"topology": "multiscale", "tail": "multiscale", "T_fast": T_fast, "w_fast": w_fast,
              "T_slow": T_slow, "w_slow": w_slow, "gain": gain}
    return s


def delayed_second(name, d2=55, T1=5.0, T2=6.0, w2=0.9, gain=1.0, **kw) -> Spec:
    """A fast component, then a FLAT PLATEAU, then a SECOND component arriving at transport delay `d2`.

    THIS IS THE TRAP, AND IT IS DELIBERATE. In the plateau the response is not moving at all. Any guard that stops
    as soon as the local derivative goes quiet will declare the response finished, compute a fingerprint on half a
    response, and hand back a confident verdict about a system it has not finished listening to.

    The declared DELAY HORIZON is the only defence: no causal component can arrive later than (probe end + D_MAX),
    so settling may not even be ASSESSED before then. Control T5 runs the naive guard and watches it walk in."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.T_site[2] = T1
    s.C[2] = gain
    s.W[3, DRIVE] = 1.0
    s.TAU[3, DRIVE] = d2                 # the second cause arrives LATE, but WITHIN the declared horizon
    s.T_site[3] = T2
    s.C[3] = gain * w2
    s.meta = {"topology": "delayed_second", "tail": "delayed_second", "d2": d2, "w2": w2, "gain": gain}
    return s


def nonsettling(name, k=0.15, T=8.0, gain=1.0, **kw) -> Spec:
    """A response that NEVER settles. The self-decay is cancelled (W[i,i] = 1), leaving an undamped oscillator, so
    the transient neither dies nor converges. Measured: late/early tail energy ratio ~1.04.

    There is no bound to be had here and the instrument must say so. This is the honest INDETERMINATE_IN_FLIGHT."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, 2] = 1.0                      # cancels the -x term: an integrator, not a leak
    s.W[3, 3] = 1.0
    s.W[2, 3] = -k
    s.W[3, 2] = 1.0
    s.W[2, DRIVE] = 1.0
    s.T_site[2] = s.T_site[3] = T
    s.C[2] = gain
    s.meta = {"topology": "nonsettling", "tail": "nonsettling", "k": k, "T": T, "gain": gain}
    return s


def out_of_contract_slow(name, T=90.0, gain=1.0, **kw) -> Spec:
    """Relaxation slower than the DECLARED TAU_MAX. Not a defect of the instrument -- outside its declared domain.
    The instrument must refuse it by CONTRACT, not by accident."""
    s = first_order(name, T=T, gain=gain, **kw)
    s.meta = {"topology": "out_of_contract_slow", "tail": "out_of_contract_slow", "T": T}
    return s
