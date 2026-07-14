"""CRD-02 -- REFERENCED PAIRED-EPISODE ACQUISITION.

CRD-01 worked and could not be built. Its control channel was the SAME SYSTEM, simultaneously probed and
unprobed. No droplet can supply that: you cannot intervene and not intervene on one object at one time.

CRD-02 removes the twin. The active and sham episodes are SEPARATE IN TIME on the SAME object -- which is what a
real protocol does -- and each episode carries its OWN simultaneously recorded reference channel:

    ACTIVE   y_A(t) = s(t) + base_A + a_A*d_A(t-dA) + loc_A*n_A(t) + eps_A(t)
             r_A(t) = rbase_A     + b_A*B[d_A](t-eA) + kap_A*s(t)  + xi_A(t)

    SHAM     y_S(t) =        base_S + a_S*d_S(t-dS) + loc_S*n_S(t) + eps_S(t)
             r_S(t) = rbase_S     + b_S*B[d_S](t-eS) + kap_S*s(t)  + xi_S(t)

with  d_A  !=  d_S.  THE TWO EPISODES SEE DIFFERENT DRIFT REALIZATIONS. That is the whole point: CRD-00 died
because it subtracted an episode carrying d_S from one carrying d_A. Here nothing is subtracted until each
episode has been corrected AGAINST ITS OWN REFERENCE.

The reference is deliberately NOT a copy of the hidden drift. It has finite:

    coupling      b_j            (and it may mismatch a_j)
    delay         eta_j          (and it may mismatch delta_j)
    noise         xi
    BANDWIDTH     B[.]           -- the drift has a FAST component the reference can attenuate or miss entirely
    contamination kappa_j        -- the reference may pick up the causal response it is supposed to be blind to

and `loc_j` injects LOCAL drift that reaches y and NOT r: the part no reference can ever remove. Building a
perfect noiseless copy of d and calling it a sensor would be cheating, and it is the one thing this file refuses
to do.
"""
from __future__ import annotations

import hashlib

import numpy as np

from .engine import Probe, Spec, observe_noise_free

TAU_SLOW = 500.0
TAU_FAST = 9.0          # the fast component. A band-limited reference cannot see it.


def ou(T, sigma, tau, rng):
    if sigma == 0.0:
        return np.zeros(T)
    phi = float(np.exp(-1.0 / tau))
    e = rng.normal(0.0, sigma, T)
    e[0] = 0.0
    if T / tau > 30.0:
        x = np.zeros(T)
        for t in range(1, T):
            x[t] = phi * x[t - 1] + e[t]
        return x
    k = np.arange(T)
    return np.power(phi, k) * np.cumsum(e * np.power(phi, -k.astype(float)))


def _lag(x, k):
    if k == 0:
        return x
    y = np.empty_like(x)
    if k > 0:
        y[:k] = x[0]; y[k:] = x[:-k]
    else:
        y[k:] = x[-1]; y[:k] = x[-k:]
    return y


class PContract:
    """The DECLARED paired-episode acquisition contract. Frozen before the prospective run."""

    def __init__(self, a_A=1.0, a_S=1.0, b_A=1.0, b_S=1.0,
                 delta_A=0, delta_S=0, eta_A=0, eta_S=0,
                 drift_sigma=2.0e-5, f_fast=0.35, ref_fast_gain=1.0,
                 eps=1.0e-5, xi=1.0e-5,
                 loc_A=0.0, loc_S=0.0, kap_A=0.0, kap_S=0.0,
                 base_A=0.0, base_S=6.0e-4, order="P1", no_reference=False):
        self.__dict__.update(locals()); del self.__dict__["self"]

    def meta(self):
        return {k: v for k, v in self.__dict__.items()}

    def key(self):
        return hashlib.sha256(repr(sorted(self.meta().items())).encode()).hexdigest()[:16]


def _drift(T, C, rng):
    """Two-timescale drift. The reference sees the fast part only through `ref_fast_gain`."""
    slow = ou(T, C.drift_sigma, TAU_SLOW, rng)
    fast = ou(T, C.drift_sigma * C.f_fast, TAU_FAST, rng)
    d_true = slow + fast                              # what the MEASUREMENT sees
    d_ref = slow + C.ref_fast_gain * fast             # what the REFERENCE sees -- BAND-LIMITED
    return d_true, d_ref


_SIG = {}


def _shash(spec: Spec) -> str:
    h = hashlib.sha256()
    for f in ("kinds", "W", "TAU", "T_site", "K_site", "bias", "C", "g_out", "k_out", "x0",
              "sigma", "drift_sigma", "drift_tau", "substeps", "unit_a", "unit_b", "t_shift", "blocked"):
        v = getattr(spec, f, None)
        h.update(f.encode())
        h.update(np.asarray(v, dtype=object).astype(str).tobytes() if v is not None else b"None")
    return h.hexdigest()[:24]


def signals(spec: Spec, probe: Probe, T: int, sign: int = 1):
    """CONTENT-ADDRESSED. Deterministic, seed-free: the engine is run NOISE-FREE and composed afterwards."""
    key = (_shash(spec), probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset, T)
    if key not in _SIG:
        nul = Probe("b", -1, "none", 0.0, 0, 10 ** 9)
        p = Probe(probe.name, probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset)
        y = observe_noise_free(spec, [nul, p], T)
        _SIG[key] = (y[0].copy(), y[1].copy())
    return _SIG[key]        # (s_baseline, s_active)


def episode(sig_y, s_causal, T, seed, C, active: bool):
    """ONE episode: its measurement and its OWN simultaneous reference, sharing ONE drift realization.

    Different episodes get different seeds -> DIFFERENT DRIFT REALIZATIONS. That is not a limitation of the
    benchmark; it is the physical fact CRD-02 exists to survive.
    """
    rng = np.random.default_rng(seed)
    d_true, d_ref = _drift(T, C, rng)
    a, b = (C.a_A, C.b_A) if active else (C.a_S, C.b_S)
    dl, et = (C.delta_A, C.eta_A) if active else (C.delta_S, C.eta_S)
    loc, kap = (C.loc_A, C.kap_A) if active else (C.loc_S, C.kap_S)
    bs, rbs = (C.base_A, 0.0) if active else (C.base_S, 3.0e-4)
    n = ou(T, C.drift_sigma, TAU_SLOW, rng) if loc else np.zeros(T)   # LOCAL drift: reaches y, NEVER r
    y = sig_y + bs + a * _lag(d_true, dl) + loc * n + rng.normal(0.0, C.eps, T)
    r = rbs + b * _lag(d_ref, et) + kap * s_causal + rng.normal(0.0, C.xi, T)
    if C.no_reference:
        r = np.full(T, np.nan)          # D3 / must-fail 1: the CRD-00 design, with NO reference at all
    return y, r, d_true


def acquire_pair(spec: Spec, probe: Probe, T: int, seeds, C: PContract, sign: int = 1):
    """R repeats of ONE (active, sham) PAIR. Physically: the same object, probed then unprobed (or S-A-A-S)."""
    sC, sA = signals(spec, probe, T, sign)
    causal = sA - sC
    YA, RA, YS, RS, DA, DS = [], [], [], [], [], []
    for k in seeds:
        yA, rA, dA = episode(sA, causal, T, k, C, True)
        yS, rS, dS = episode(sC, causal, T, k ^ 0x9E3779B9, C, False)   # DIFFERENT SEED -> d_A != d_S
        YA.append(yA); RA.append(rA); YS.append(yS); RS.append(rS); DA.append(dA); DS.append(dS)
    return (np.array(YA), np.array(RA), np.array(YS), np.array(RS),
            {"causal": causal, "d_A": np.array(DA), "d_S": np.array(DS)})     # PRIVILEGED
