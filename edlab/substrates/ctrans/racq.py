"""CRD-03 -- REDUNDANT-REFERENCE + SIGNED-INTERVENTION ACQUISITION.

CRD-02 failed on one identifiability fact: with ONE passive reference r = a1*d + kappa*s, a contaminated reference
makes the estimate s_hat = s*(1 - alpha*kappa), which is indistinguishable from a smaller true response. Five
single-reference detectors could not cross that floor. This file adds information through the ACQUISITION, not the
estimator, in two ways the CRD-03 theorem shows are the only ones that help:

  REDUNDANT references with DIFFERENT drift couplings a_i. The drift-free channel z_i = y - alpha_i*r_i =
  s*(1 - alpha_i*kappa_i). If the references are contaminated DIFFERENTLY, the z_i DISAGREE, and (under
  'at most one contaminated') the agreeing pair is clean and recovers s exactly. If they are contaminated in
  COMMON MODE (kappa_i proportional to a_i), every z_i is attenuated identically, they agree, and the attenuation
  is EXACTLY unidentifiable -- provably, no passive-reference scheme can see it.

  SIGNED interventions +u, -u. Drift is even under the sign flip; the causal response has a known odd part. The
  odd combination (y(+u) - y(-u))/2 removes the drift with NO reference at all, and the even part is retained for
  nonlinear responses. Signs do not resolve common-mode contamination (the odd channel is still s_odd*(1-alpha k)).

Nothing here touches engine.py (v00 freeze) or the droplet. The engine is run NOISE-FREE and the measurement is
composed on top: references, drift, contamination, noise, signs are all declared, never inferred from truth.
"""
from __future__ import annotations

import hashlib

import numpy as np

from .engine import Probe, Spec, observe_noise_free

TAU_SLOW = 500.0
TAU_FAST = 9.0


def ou(T, sigma, tau, rng):
    """Blocked-vectorised OU (matches the literal recurrence to 1e-15; see CRD-02 pacq)."""
    if sigma == 0.0:
        return np.zeros(T)
    phi = float(np.exp(-1.0 / tau))
    e = rng.normal(0.0, sigma, T)
    e[0] = 0.0
    L = max(1, int(20.0 * tau))
    x = np.zeros(T)
    carry = 0.0
    kf = np.arange(L, dtype=float)
    pos = np.power(phi, kf)
    neg = np.power(phi, -kf)
    for b in range(0, T, L):
        blk = e[b:b + L].copy()
        n = len(blk)
        blk[0] += phi * carry
        xb = pos[:n] * np.cumsum(blk * neg[:n])
        x[b:b + n] = xb
        carry = xb[-1]
    return x


def _drift(T, drift_sigma, f_fast, rng):
    slow = ou(T, drift_sigma, TAU_SLOW, rng)
    fast = ou(T, drift_sigma * f_fast, TAU_FAST, rng)
    return slow + fast


class RContract:
    """DECLARED redundant-reference acquisition contract. Frozen before the prospective run.

    couplings : per-reference drift coupling a_i (DISTINCT couplings are what make contamination identifiable).
    kappa     : per-reference causal contamination kappa_i (r_i = a_i*d + kappa_i*s). 0 = clean.
    hysteresis: if !=0, the response depends on intervention order -> the signed contract is violated on purpose.
    even_frac : fraction of the response that is EVEN in u (nonlinear); 0 = purely odd (linear).
    """

    def __init__(self, couplings=(0.8, 1.5, 1.15), kappa=(0.0, 0.0, 0.0),
                 a=1.0, drift_sigma=2.0e-5, f_fast=0.35, eps=1.0e-5, xi=1.0e-5,
                 loc=0.0, hysteresis=0.0, even_frac=0.0, comp_kappa=0.0, name="A_dual"):
        self.couplings = tuple(couplings)
        self.kappa = tuple(kappa)
        self.a, self.drift_sigma, self.f_fast = a, drift_sigma, f_fast
        self.eps, self.xi, self.loc = eps, xi, loc
        self.hysteresis, self.even_frac, self.comp_kappa = hysteresis, even_frac, comp_kappa
        self.name = name

    def meta(self):
        return {k: getattr(self, k) for k in ("couplings", "kappa", "a", "drift_sigma", "f_fast",
                                              "eps", "xi", "loc", "hysteresis", "even_frac", "comp_kappa", "name")}

    def key(self):
        return hashlib.sha256(repr(sorted(self.meta().items())).encode()).hexdigest()[:16]


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
    key = (_shash(spec), probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset, T)
    if key not in _SIG:
        nul = Probe("b", -1, "none", 0.0, 0, 10 ** 9)
        p = Probe(probe.name, probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset)
        y = observe_noise_free(spec, [nul, p], T)
        _SIG[key] = (y[0].copy(), y[1].copy())
    return _SIG[key]


def _response(spec, probe, T, sign, C):
    """The causal response to a signed intervention, with declared odd/even split and optional hysteresis.

    Pure-odd (even_frac=0): response scales with sign. Even part: added symmetric component (same for +/-u).
    Hysteresis: the +u and -u responses acquire an order-dependent offset the signed contract cannot cancel."""
    sC, sPos = signals(spec, probe, T, +1)
    base_resp = sPos - sC                       # response to +u (odd carrier)
    odd = sign * base_resp
    even = C.even_frac * np.abs(base_resp)      # even in u -> same sign for +u and -u
    hyst = C.hysteresis * np.cumsum(base_resp) / max(np.max(np.abs(np.cumsum(base_resp))), 1e-30) * np.max(np.abs(base_resp))
    return odd + even + (hyst if sign > 0 else 0.0), sC


def episode(spec, probe, T, seed, C: RContract, sign: int = 1):
    """ONE probed episode: measurement y and N simultaneous references, all sharing THIS episode's drift."""
    resp, sC = _response(spec, probe, T, sign, C)
    s = resp                                    # accessible causal response (relative to baseline sC)
    rng = np.random.default_rng(seed)
    d = _drift(T, C.drift_sigma, C.f_fast, rng)
    n_loc = _drift(T, C.drift_sigma, C.f_fast, rng) if C.loc else np.zeros(T)
    y = sC + s + C.a * d + C.loc * n_loc + rng.normal(0.0, C.eps, T)
    refs = []
    for ai, ki in zip(C.couplings, C.kappa):
        refs.append(ai * d + ki * s + rng.normal(0.0, C.xi, T))
    a_comp = 1.0                                       # complementary channel's DECLARED drift coupling (fixed)
    comp = C.comp_kappa * s + a_comp * d + rng.normal(0.0, C.xi, T)   # complementary "null" probe channel
    return {"y": y, "refs": np.array(refs), "comp": comp, "s_true": s, "sC": sC, "d": d}


def _null_probe(probe):
    return Probe(probe.name, probe.target, "none", 0.0, 0, probe.onset)


def acquire(spec, probe, T, seeds, C: RContract):
    """Redundant-reference signed acquisition. For every seed, THREE separate episodes (independent drift):
       +u (active), 0 (unprobed, for the baseline-removing difference-in-differences), -u (ARM B diagnostic)."""
    nul = _null_probe(probe)
    P, U, M = [], [], []
    for k in seeds:
        P.append(episode(spec, probe, T, k, C, +1))
        U.append(episode(spec, nul, T, k ^ 0x1111, C, +1))         # unprobed: SEPARATE drift realization
        M.append(episode(spec, probe, T, k ^ 0x5163, C, -1))       # -u: SEPARATE drift realization
    def stack(key, arr):
        return np.array([e[key] for e in arr])
    out = {"yP": stack("y", P), "yU": stack("y", U), "yM": stack("y", M),
           "rP": np.array([e["refs"] for e in P]), "rU": np.array([e["refs"] for e in U]),
           "rM": np.array([e["refs"] for e in M]),
           "cP": stack("comp", P), "cM": stack("comp", M),
           "sP": stack("s_true", P), "sM": stack("s_true", M)}      # s_true PRIVILEGED
    return out
