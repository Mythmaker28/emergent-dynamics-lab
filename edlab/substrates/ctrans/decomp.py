"""SUBSTRATE CONSTRUCTIONS FOR EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00.

ADDITIVE ONLY. `engine.py`, `systems.py`, `manifests.py`, `evaluator.py` and `cfingerprint.py` carry the sha256 of
the v00 freeze and are NOT touched. The historical branch stays byte-verifiable.

THE CONSTRUCTION THAT MAKES THIS BENCHMARK POSSIBLE.

The whole difficulty of grading a response-DIFFERENCE benchmark is that you rarely control the difference: you
build two systems and take what their subtraction gives you. Here the difference is built DIRECTLY.

    B = A + one extra PARALLEL PATH from the drive, read out with weight w.

Because the readout is linear in the sites, the accessible difference is EXACTLY that path's own response:

    delta_r(t)  =  w * x_path(t)

So the shape of the discrepancy is a design parameter, not an accident:

    LEAKY path (time constant Tx)   -> a rise-and-decay pulse.  ASYMPTOTE ZERO. A pure TRANSIENT difference.
    INTEGRATOR path (self-coupling  -> the probe leaves a PERMANENT STEP.        A pure PERSISTENT difference.
      W[i,i] = 1 cancels the -x term)
    DELAYED path (transport delay)  -> the same discrepancy, arriving later.     A pure LATENCY difference.

and, since energy scales as w^2 and peak scales as w, a single scalar `w` lets us build pairs with THE SAME
TRANSIENT ENERGY AND DIFFERENT PEAK, or THE SAME PEAK AND DIFFERENT DURATION -- the two controls that prove the
old scalar was conflating things it had no right to conflate.
"""

from __future__ import annotations

import numpy as np

from .engine import DRIVE, LINEAR, Spec
from .systems import _blank, _set, G0, SIG0


def base(name, T=8.0, gain=1.0, tau=0, sigma=SIG0, **kw) -> Spec:
    """The reference system. Every pair below is `base` versus `base + one extra path`."""
    s = _blank(name, sigma=sigma, **kw)
    s.kinds = _set(s.kinds, 2, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.T_site[2] = T
    s.C[2] = gain
    s.meta = {"topology": "base", "T": T, "gain": gain, "tau": tau}
    return s


def plus_path(name, b: Spec, w: float, Tx: float, delay: int = 0, persistent: bool = False,
              site: int = 3) -> Spec:
    """`b` PLUS one extra parallel path. The accessible difference is EXACTLY `w * x_path(t)`.

    `persistent=True` cancels the site's own decay (W[i,i] = 1), turning the leak into an INTEGRATOR: a bounded
    probe then leaves a PERMANENT step in the difference. That is a persistent discrepancy built on purpose, and
    it is the thing an RMS-over-window metric never dilutes -- which is precisely why it must have its own axis.
    """
    s = Spec(**{**b.__dict__})
    s.name = name
    s.kinds = _set(b.kinds, site, LINEAR)
    s.W, s.TAU = b.W.copy(), b.TAU.copy()
    s.T_site, s.C, s.bias, s.x0 = b.T_site.copy(), b.C.copy(), b.bias.copy(), b.x0.copy()
    s.K_site = b.K_site.copy()
    s.W[site, DRIVE] = 1.0
    s.TAU[site, DRIVE] = delay
    s.T_site[site] = Tx
    if persistent:
        s.W[site, site] = 1.0          # cancels -x : an integrator. The probe's effect never decays away.
    s.C[site] = w
    s.meta = {**b.meta, "extra_path": {"w": w, "Tx": Tx, "delay": delay, "persistent": persistent}}
    return s


def with_drift(name, b: Spec, frac: float) -> Spec:
    s = Spec(**{**b.__dict__})
    s.name = name
    s.drift_sigma = frac * b.sigma
    s.meta = {**b.meta, "drift_frac": frac}
    return s


def with_noise(name, b: Spec, mult: float) -> Spec:
    s = Spec(**{**b.__dict__})
    s.name = name
    s.sigma = b.sigma * mult
    s.drift_sigma = b.drift_sigma * mult
    s.meta = {**b.meta, "sigma_mult": mult}
    return s


def plus_spike(name, b: Spec, w: float, Tf: float = 1.0, Ts: float = 6.0, sites=(3, 4)) -> Spec:
    """An extra path that is a HIGH-PASS: a fast leak MINUS a slower one. Its response is a BRIEF BIPHASIC EDGE.

    WHY THIS EXISTS. A single leaky path cannot dissociate peak from energy: MEASURED across Tx from 1 to 64, its
    shape factor E/A^2 stays between 18 and 41, so a scaling weight buys you one constraint and the other follows.
    The best equal-energy peak ratio achievable was 1.36 -- not a control, a rounding error.

    Peak and energy only come apart when the SHAPE comes apart. This path is TALL AND BRIEF; `plus_broad` is SHORT
    AND LONG. Between them a single weight can equalise one axis and leave the other far apart, which is exactly
    what a factorized instrument must be made to prove."""
    s = Spec(**{**b.__dict__})
    s.name = name
    i, j = sites
    s.kinds = _set(_set(b.kinds, i, LINEAR), j, LINEAR)
    s.W, s.TAU = b.W.copy(), b.TAU.copy()
    s.T_site, s.C, s.bias, s.x0 = b.T_site.copy(), b.C.copy(), b.bias.copy(), b.x0.copy()
    s.K_site = b.K_site.copy()
    s.W[i, DRIVE] = 1.0; s.T_site[i] = Tf; s.C[i] = w
    s.W[j, DRIVE] = 1.0; s.T_site[j] = Ts; s.C[j] = -w
    s.meta = {**b.meta, "extra_path": {"kind": "spike", "w": w, "Tf": Tf, "Ts": Ts}}
    return s


def plus_broad(name, b: Spec, w: float, T1: float = 20.0, T2: float = 20.0, sites=(3, 4)) -> Spec:
    """An extra path that is a CASCADE: drive -> site -> site. Its response is a SMOOTH BROAD BUMP -- low peak,
    long duration, large integrated energy. The counterpart of `plus_spike`."""
    s = Spec(**{**b.__dict__})
    s.name = name
    i, j = sites
    s.kinds = _set(_set(b.kinds, i, LINEAR), j, LINEAR)
    s.W, s.TAU = b.W.copy(), b.TAU.copy()
    s.T_site, s.C, s.bias, s.x0 = b.T_site.copy(), b.C.copy(), b.bias.copy(), b.x0.copy()
    s.K_site = b.K_site.copy()
    s.W[i, DRIVE] = 1.0; s.T_site[i] = T1; s.C[i] = 0.0
    s.W[j, i] = 1.0;     s.T_site[j] = T2; s.C[j] = w
    s.meta = {**b.meta, "extra_path": {"kind": "broad", "w": w, "T1": T1, "T2": T2}}
    return s
