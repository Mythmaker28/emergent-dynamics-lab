"""COMMON-MODE ACQUISITION — EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-01.

CRD-00 died on one sentence, and it is worth repeating before any code:

    A SHAM THAT SHARES A DISTRIBUTION DOES NOT SHARE A DISTURBANCE.

The frozen engine gives every episode its OWN drift realization. Subtracting one such episode from another is
unbiased in expectation and useless per pair: y_A carries d_A, the sham carries d_S, and d_A != d_S.

So this file changes the ACQUISITION CONTRACT, not the estimators. It does NOT touch `engine.py` (whose sha256 is
part of the v00 freeze). It runs the engine NOISE-FREE -- which is deterministic and needs no RNG -- and then
COMPOSES the measurement itself:

    y_A(t) = s_A(t) + a_A * d(t - delta_A) + b_A * n_A(t) + eps_A(t)      ACTIVE  (receives the intervention)
    y_C(t) = s_C(t) + a_C * d(t - delta_C) + b_C * n_C(t) + eps_C(t)      CONTROL (receives none)

  d(t)          ONE SHARED common-mode drift realization, seen by BOTH channels
  a_A, a_C      channel couplings to it            (a mismatch is the frontier, not a bug)
  delta_A/C     coupling lags
  n_A, n_C      INDEPENDENT residual drifts        (the part that is NOT shared -- b=0 is perfect common mode)
  eps_A, eps_C  independent measurement noise

The DEFAULT REGIME IS HEAVY DRIFT (drift_sigma = 2e-5 against eps = 1e-5), because that is the regime that killed
CRD-00. A contract that only works when the drift is already negligible would be testing nothing.

The privileged evaluator knows d, a, delta, b. THE INSTRUMENT RECEIVES ONLY y_A AND y_C. It never sees the drift,
the couplings, the labels or the states.
"""

from __future__ import annotations

import numpy as np

from .engine import Spec, Probe, observe_noise_free


def ou(T, sigma, tau, rng):
    """One Ornstein-Uhlenbeck realization. Shared by both channels when the contract says so."""
    if sigma == 0.0:
        return np.zeros(T)
    phi = float(np.exp(-1.0 / tau))
    e = rng.normal(0.0, sigma, T)
    e[0] = 0.0
    # x[t] = sum_{k<=t} phi^(t-k) e[k] = phi^t * cumsum(e[k] * phi^-k). Exact, and vectorised.
    # phi^-k grows like exp(T/tau); at T=1000, tau=500 that is e^2 = 7.4, so the conditioning is harmless.
    # Guarded anyway -- an unstable fast path that quietly returns garbage is worse than a slow correct one.
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
        y[:k] = x[0]
        y[k:] = x[:-k]
    else:
        y[k:] = x[-1]
        y[:k] = x[-k:]
    return y


class CMContract:
    """The DECLARED common-mode acquisition contract. Frozen before the prospective run."""

    def __init__(self, a_A=1.0, a_C=1.0, delta_A=0, delta_C=0, b_A=0.0, b_C=0.0,
                 drift_sigma=2.0e-5, drift_tau=500.0, eps=1.0e-5, kappa_C=0.0, name="A_simultaneous"):
        self.a_A, self.a_C = a_A, a_C
        self.delta_A, self.delta_C = delta_A, delta_C
        self.b_A, self.b_C = b_A, b_C           # INDEPENDENT residual drift amplitudes (the frontier axis)
        self.drift_sigma, self.drift_tau = drift_sigma, drift_tau
        self.eps = eps
        self.kappa_C = kappa_C                  # CONTROL CONTAMINATION: the control leaks this much response
        self.name = name

    def meta(self):
        return {k: getattr(self, k) for k in ("a_A", "a_C", "delta_A", "delta_C", "b_A", "b_C",
                                              "drift_sigma", "drift_tau", "eps", "kappa_C", "name")}


def acquire_pair(spec: Spec, probe: Probe, T: int, seed: int, C: CMContract, sign: int = +1):
    """ONE active/control pair sharing ONE drift realization.

    `sign` = -1 flips the intervention amplitude: that is CONTRACT C (intervention reversal), for which the drift
    is common to both polarities and the CAUSAL part changes sign -- so the drift cancels with no control channel
    at all, provided the response is odd in u. It is NOT odd for a saturating or bistable system, and that is a
    declared scope limit rather than a surprise.
    """
    nul = Probe("base", -1, "none", 0.0, 0, 10 ** 9)
    p = Probe(probe.name, probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset)
    y = observe_noise_free(spec, [nul, p], T)      # deterministic: s_C (no intervention) and s_A (with it)
    sC, sA = y[0], y[1]
    rng = np.random.default_rng(seed)
    d = ou(T, C.drift_sigma, C.drift_tau, rng)                     # THE SHARED REALIZATION
    nA = ou(T, C.drift_sigma, C.drift_tau, rng) if C.b_A else np.zeros(T)
    nC = ou(T, C.drift_sigma, C.drift_tau, rng) if C.b_C else np.zeros(T)
    eA = rng.normal(0.0, C.eps, T)
    eC = rng.normal(0.0, C.eps, T)
    # CONTROL CONTAMINATION: the control channel picks up a fraction of the causal response it must not have.
    sC_eff = sC + C.kappa_C * (sA - sC)
    yA = sA + C.a_A * _lag(d, C.delta_A) + C.b_A * nA + eA
    yC = sC_eff + C.a_C * _lag(d, C.delta_C) + C.b_C * nC + eC
    return {"yA": yA, "yC": yC,
            "PRIV": {"sA": sA, "sC": sC, "d": d, "causal": sA - sC}}      # PRIVILEGED. Never handed to the instrument.


# ---- The deterministic signal does NOT depend on the seed. Simulate it ONCE; compose the measurement per repeat.
_SIG = {}


def _spec_hash(spec: Spec) -> str:
    import hashlib
    h = hashlib.sha256()
    for f in ("kinds", "W", "TAU", "T_site", "K_site", "bias", "C", "g_out", "k_out", "x0",
              "sigma", "drift_sigma", "drift_tau", "substeps", "unit_a", "unit_b", "t_shift", "blocked"):
        v = getattr(spec, f, None)
        h.update(f.encode())
        h.update(np.asarray(v, dtype=object).astype(str).tobytes() if v is not None else b"None")
    return h.hexdigest()[:24]


def signals(spec: Spec, probe: Probe, T: int, sign: int = +1):
    # CONTENT-ADDRESSED, never name-addressed: v01 lost a day to a name-keyed cache serving a stale
    # re-parameterised system. The key is the numbers, not the label.
    key = (_spec_hash(spec), probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset, T)
    if key not in _SIG:
        nul = Probe("base", -1, "none", 0.0, 0, 10 ** 9)
        p = Probe(probe.name, probe.target, probe.kind, sign * probe.amp, probe.hold, probe.onset)
        y = observe_noise_free(spec, [nul, p], T)
        _SIG[key] = (y[0].copy(), y[1].copy())
    return _SIG[key]


def compose(sA, sC, seed: int, C: CMContract):
    """Compose ONE measurement pair from the deterministic signals and ONE SHARED drift realization."""
    T = len(sA)
    rng = np.random.default_rng(seed)
    d = ou(T, C.drift_sigma, C.drift_tau, rng)                 # THE SHARED REALIZATION
    nA = ou(T, C.drift_sigma, C.drift_tau, rng) if C.b_A else np.zeros(T)
    nC = ou(T, C.drift_sigma, C.drift_tau, rng) if C.b_C else np.zeros(T)
    eA = rng.normal(0.0, C.eps, T)
    eC = rng.normal(0.0, C.eps, T)
    sC_eff = sC + C.kappa_C * (sA - sC)
    yA = sA + C.a_A * _lag(d, C.delta_A) + C.b_A * nA + eA
    yC = sC_eff + C.a_C * _lag(d, C.delta_C) + C.b_C * nC + eC
    return yA, yC, d


def acquire(spec: Spec, probe: Probe, T: int, seeds, C: CMContract, sign: int = +1):
    """R repeats. FOUR SIMULTANEOUS CHANNELS per repeat, all sharing ONE drift realization d_r:

        yA  ACTIVE     receives the intervention
        yC  CONTROL-1  receives none. THE SUBTRAHEND.
        yD  CONTROL-2  receives none. THE DRIFT PROXY -- and it exists for a reason that cost a whole run:

              A proxy built from the SAME control you subtract shares that control's MEASUREMENT NOISE with the
              deviation you are correcting. The regression then fits eps against itself, g_hat runs to -1, and the
              "correction" INJECTS noise instead of removing drift. (Observed: g_hat = -1.008 on a drift-free
              system.) Two control channels share the drift and NOT the noise, so the regression sees only drift.

        yS  SHAM       identical acquisition, intervention amplitude ZERO. Calibrates the bands.

    Two simultaneous reference channels is an ordinary instrumentation request, not an oracle: neither channel is
    ever told the system's state, the intervention, or the drift.
    """
    sA, sC = signals(spec, probe, T, sign)
    YA, YC, YD, YS, DD = [], [], [], [], []
    for s in seeds:
        yA, yC, d = compose(sA, sC, s, C)
        yD = sC + C.a_C * _lag(d, C.delta_C) + (C.b_C * ou(T, C.drift_sigma, C.drift_tau,
                                                           np.random.default_rng(s ^ 0x5D2)) if C.b_C else 0.0) \
            + np.random.default_rng(s ^ 0xC0FFEE).normal(0.0, C.eps, T)   # SAME d, INDEPENDENT eps
        yS, _, _ = compose(sC, sC, s, C)
        YA.append(yA); YC.append(yC); YD.append(yD); YS.append(yS); DD.append(d)
    return (np.array(YA), np.array(YC), np.array(YD), np.array(YS),
            {"causal": sA - sC, "d": np.array(DD), "sA": sA, "sC": sC})   # PRIVILEGED
