"""EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00 -- development. DEV DATA ONLY."""
from __future__ import annotations
import hashlib, json, math, os, sys
import numpy as np
from ..identity import cfingerprint as F0, crdecomp as CR
from ..substrates.ctrans import engine as E, manifests_crd as MC
from ..substrates.ctrans.engine import Probe

OUT = os.path.join("results", "EXP-GT-CRD00-DEV")
CACHE = os.path.join("results", "_crd_cache")
W = CR.W_FIXED
W_LONG = 1400
IH = hashlib.sha256(open("edlab/identity/crdecomp.py", "rb").read()).hexdigest()[:12]
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
    """Content-addressed on system params + arm + seed + horizon + battery hash + instrument hash."""
    os.makedirs(CACHE, exist_ok=True)
    key = "%s_%s_%d_W%d_b%s_i%s_%s" % (sfp(spec), arm, seed0, w, BH, IH,
                                       "_".join("%s%s" % (k, v) for k, v in sorted(kw.items())) or "x")
    fp = os.path.join(CACHE, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = CR.acquire(channel(spec), arm, seed0, w, **kw)
    np.savez_compressed(fp, **{k: np.asarray(v) for k, v in a.items()})
    return a


# ---------------------------------------------------------------- PRIVILEGED TRUTH (no instrument code)
_T = {}


def true_profile(a, b, arm="limited", w=W_LONG):
    """The exact profile from NOISE-FREE trajectories, standardized by the DECLARED noise scale.

    It uses no sigma_hat, no sham, no threshold and no estimator of the instrument. It is the answer key."""
    key = (a.name, b.name, arm, w)
    if key in _T:
        return _T[key]
    T = F0.T_PROBE + max(F0.PHASES) + w + 8
    pr = F0.battery(arm)
    eps = [Probe("b", -1, "none", 0.0, 0, 10 ** 9)]
    for (nm, tgt, kind, amp, hold) in pr:
        for ph in F0.PHASES:
            eps.append(Probe(nm, tgt, kind, amp, hold, F0.T_PROBE + ph))
    ok = [i for i, p in enumerate(eps) if p.target not in a.blocked and p.target not in b.blocked]
    ya = E.observe_noise_free(a, [eps[i] for i in ok], T)
    yb = E.observe_noise_free(b, [eps[i] for i in ok], T)
    sa = abs(a.unit_a) * a.sigma * math.sqrt(2.0 / F0.N_REPEAT)
    sb = abs(b.unit_a) * b.sigma * math.sqrt(2.0 / F0.N_REPEAT)
    Es, Ps, As = [], [], []
    j = 1
    for pi in range(len(pr)):
        for ph in F0.PHASES:
            if j >= len(ok):
                break
            on = F0.T_PROBE + ph
            ra = (ya[j] - ya[0])[on:on + w] / sa
            rb = (yb[j] - yb[0])[on:on + w] / sb
            d = rb - ra
            P = float(d[-200:].mean())
            Es.append(float(((d - P) ** 2).sum())); Ps.append(P); As.append(float(np.abs(d).max()))
            j += 1
    out = {"E_trans": max(Es), "P_inf": max(Ps, key=abs), "A_peak": max(As)}
    _T[key] = out
    return out


def say(*a):
    print(*a); sys.stdout.flush()
