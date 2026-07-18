"""EXP-GT-CONTINUOUS-FINGERPRINT-03 -- development: fit, calibrate, gate. DEV DATA ONLY."""
from __future__ import annotations
import hashlib, json, math, os, sys
import numpy as np
from ..identity import cfingerprint as F0, cfingerprint02 as F2, cfingerprint03 as F3
from ..substrates.ctrans import engine as E, manifests03 as M3
from ..substrates.ctrans.engine import Probe

OUT = os.path.join("results", "EXP-GT-CFP03-DEV")
CACHE = os.path.join("results", "_cfp03_cache")
W = F3.W_FIXED           # 320
W_INF = 1400             # PREREGISTERED: all in-contract responses complete
ALPHA = F3.ALPHA
IH = hashlib.sha256(open("edlab/identity/cfingerprint03.py", "rb").read()).hexdigest()[:12]
BH = hashlib.sha256(repr(F0.battery("limited")).encode()).hexdigest()[:8]


def sfp(s):
    h = hashlib.sha256()
    for k in ("kinds", "g_out", "k_out", "sigma", "drift_sigma", "drift_tau", "substeps", "unit_a", "unit_b",
              "t_shift", "blocked"):
        h.update(repr(getattr(s, k)).encode())
    for k in ("W", "TAU", "T_site", "K_site", "bias", "C", "x0"):
        h.update(np.asarray(getattr(s, k)).tobytes())
    return h.hexdigest()[:16]


def channel(spec):
    def measure(probes, T, seeds):
        ok = np.array([p.target not in spec.blocked for p in probes])
        u = np.full((len(probes), T), np.nan)
        idx = [i for i, o in enumerate(ok) if o]
        if idx:
            sub = E.simulate(spec, [probes[i] for i in idx], T, np.asarray(seeds)[idx])["u"]
            for j, i in enumerate(idx):
                u[i] = sub[j]
        return u, ok
    return measure


def acq(spec, arm, seed0, w=W, **kw):
    """Content-addressed: system params + arm + seed + horizon + BATTERY hash + INSTRUMENT hash."""
    os.makedirs(CACHE, exist_ok=True)
    key = "%s_%s_%d_W%d_b%s_i%s%s" % (sfp(spec), arm, seed0, w, BH, IH, "_q8" if kw.get("quantize_uint8") else "")
    fp = os.path.join(CACHE, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = F3.acquire(channel(spec), arm, seed0, w, **kw)
    np.savez_compressed(fp, **{k: np.asarray(v) for k, v in a.items()})
    return a


# ---------------------------------------------------------------- PRIVILEGED eventual distance
_ZT = {}


def z_true(spec, arm="limited"):
    """The NOISE-FREE standardized response, at W_INF. PRIVILEGED.

    Uses the DECLARED noise scale (unit_a * sigma * sqrt(2/R)) -- never the instrument's sigma_hat, never its tail
    estimator, never a threshold. This is the answer key, and it is computed by a path the instrument cannot see."""
    k = (spec.name, arm)
    if k in _ZT:
        return _ZT[k]
    T = F0.T_PROBE + max(F0.PHASES) + W_INF + 8
    pr = F0.battery(arm)
    eps = [Probe("b", -1, "none", 0.0, 0, 10 ** 9)]
    for (nm, tgt, kind, amp, hold) in pr:
        for ph in F0.PHASES:
            eps.append(Probe(nm, tgt, kind, amp, hold, F0.T_PROBE + ph))
    keep = [i for i, p in enumerate(eps) if p.target not in spec.blocked or p.kind == "none"]
    y = E.observe_noise_free(spec, [eps[i] for i in keep], T)
    sig = abs(spec.unit_a) * spec.sigma * math.sqrt(2.0 / F0.N_REPEAT)
    Z = np.full((len(pr), len(F0.PHASES), W_INF), np.nan)
    miss = np.zeros((len(pr), len(F0.PHASES)), dtype=bool)
    pos = {i: j for j, i in enumerate(keep)}
    j = 1
    for pi in range(len(pr)):
        for ki, ph in enumerate(F0.PHASES):
            if j not in pos:
                miss[pi, ki] = True
            else:
                on = F0.T_PROBE + ph
                Z[pi, ki] = (y[pos[j]][on:on + W_INF] - y[0][on:on + W_INF]) / sig
            j += 1
    _ZT[k] = (Z, miss)
    return _ZT[k]


def D_inf(a, b, arm="limited"):
    ZA, mA = z_true(a, arm); ZB, mB = z_true(b, arm)
    P, K = ZA.shape[0], ZA.shape[1]
    valid = (~mA) & (~mB)
    best = math.inf
    for s in range(K):
        ds = [float(np.sqrt(np.mean((ZA[i, k] - ZB[i, (k + s) % K]) ** 2)))
              for i in range(P) for k in range(K) if valid[i, k] and valid[i, (k + s) % K]]
        if ds:
            best = min(best, max(ds))
    return best


def say(*a):
    print(*a); sys.stdout.flush()
