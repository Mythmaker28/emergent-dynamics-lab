"""EXP-GT-CONTINUOUS-FINGERPRINT-02 -- horizon sweep, resolution certificate, development. DEV DATA ONLY."""
from __future__ import annotations
import hashlib, json, math, os, sys, time
import numpy as np
from ..identity import cfingerprint as F0, cfingerprint02 as F2
from ..substrates.ctrans import engine as E, manifests01 as M
from ..substrates.ctrans import tails as T

OUT = os.path.join("results", "EXP-GT-CFP02-DEV")
CACHE = os.path.join("results", "_cfp02_cache")
GRID = (160, 240, 320, 480, 640)      # PREREGISTERED, committed at 44121e9
K_MARGIN = 3.0                        # PREREGISTERED
SAFETY, SEP_FACTOR = 2.0, 3.0         # unchanged calibration rule: radii from the NULL alone
NONNULL = ("V_silent_dead", "V_silent_sat", "V_noisy", "V_drifty", "V_lowcov", "V_nonsettle", "V_slow_oos")

_IHASH = hashlib.sha256(open("edlab/identity/cfingerprint02.py", "rb").read()).hexdigest()[:12]


def spec_fp(s):
    """The cache key carries EVERY system parameter AND the instrument hash. v01 keyed on the NAME alone and
    silently served a stale re-parameterised system. A cache that can answer a question it was never asked is not
    a cache, it is a bug."""
    h = hashlib.sha256()
    for k in ("kinds", "g_out", "k_out", "sigma", "drift_sigma", "drift_tau", "substeps", "unit_a", "unit_b",
              "t_shift", "blocked"):
        h.update(repr(getattr(s, k)).encode())
    for k in ("W", "TAU", "T_site", "K_site", "bias", "C", "x0"):
        h.update(np.asarray(getattr(s, k)).tobytes())
    return h.hexdigest()[:16]


def channel(spec):
    def measure(probes, T_, seeds):
        ok = np.array([p.target not in spec.blocked for p in probes])
        u = np.full((len(probes), T_), np.nan)
        idx = [i for i, o in enumerate(ok) if o]
        if idx:
            sub = E.simulate(spec, [probes[i] for i in idx], T_, np.asarray(seeds)[idx])["u"]
            for j, i in enumerate(idx):
                u[i] = sub[j]
        return u, ok
    return measure


def acq(spec, arm, seed0, W, **kw):
    os.makedirs(CACHE, exist_ok=True)
    key = "%s_%s_%d_W%d_%s%s" % (spec_fp(spec), arm, seed0, W, _IHASH,
                                 "_q8" if kw.get("quantize_uint8") else "")
    fp = os.path.join(CACHE, key + ".npz")
    if os.path.exists(fp):
        z = np.load(fp, allow_pickle=True)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    a = F2.acquire(channel(spec), arm, seed0, W, **kw)
    np.savez_compressed(fp, **{k: np.asarray(v, dtype=object) if k == "probes" else np.asarray(v)
                               for k, v in a.items()})
    return a


def say(*a):
    print(*a); sys.stdout.flush()


# ---------------------------------------------------------------- PRIVILEGED: decision-relevance of a remainder
W_SETTLED = 1400          # the horizon at which every in-contract response is complete (>> 5*TAU_MAX + D_MAX)


def _nf_delta(a, b, dev):
    """The NOISE-FREE difference of the two systems' deviation responses to the FULL battery, in units of the
    channel's own declared noise. No instrument code, no sigma_hat, no representation, no thresholds."""
    out = []
    for (nm, tgt, kind, amp, hold) in F0.battery("limited"):
        p = [E.Probe("b", -1, "none", 0, 0, 10 ** 9), E.Probe(nm, tgt, kind, amp, hold, F0.T_PROBE)]
        ra = np.diff(E.observe_noise_free(dev[a], p, F0.T_PROBE + W_SETTLED + 8), axis=0)[0]
        rb = np.diff(E.observe_noise_free(dev[b], p, F0.T_PROBE + W_SETTLED + 8), axis=0)[0]
        sa = abs(dev[a].unit_a) * dev[a].sigma * math.sqrt(2.0 / F0.N_REPEAT)
        sb = abs(dev[b].unit_a) * dev[b].sigma * math.sqrt(2.0 / F0.N_REPEAT)
        out.append(ra[F0.T_PROBE:] / sa - rb[F0.T_PROBE:] / sb)
    return out


def decision_relevant(a, b, dev, W, r_cont, r_sep):
    """PRIVILEGED and INSTRUMENT-INDEPENDENT. Is the pair's verdict at horizon W different from its verdict once
    the response has fully settled? If so, the unseen remainder is DECISION-RELEVANT and the instrument MUST be
    able to see it."""
    ds = _nf_delta(a, b, dev)
    dW = max(float(np.sqrt(np.mean(d[:W] ** 2))) for d in ds)
    dS = max(float(np.sqrt(np.mean(d[:W_SETTLED] ** 2))) for d in ds)
    side = lambda x: (0 if x <= r_cont else (2 if x >= r_sep else 1))
    return {"d_W": dW, "d_settled": dS, "relevant": side(dW) != side(dS),
            "side_W": side(dW), "side_settled": side(dS)}


def radii(dev, W, nulls):
    ns = []
    for n in nulls:
        i = list(dev).index(n)
        A = acq(dev[n], "limited", M.DEV_SEED_BASE + 3000 * i, W)
        B = acq(dev[n], "limited", M.DEV_SEED_BASE + 3000 * i + 1500, W)
        d = F2.distance_bracket(A, B, tail_noise=1e9)["d_obs"]     # point distance; the guard is irrelevant here
        if np.isfinite(d):
            ns.append(d)
    q = float(np.quantile(ns, 0.999))
    return SAFETY * q, SEP_FACTOR * SAFETY * q, ns


def b_noise(dev, W):
    """B_noise(W): the MAX of the raw remaining-envelope statistic over NOISE-ONLY blocks. No label consulted."""
    vals = []
    for nm in ("V_silent_dead", "V_silent_sat", "V_leak"):
        i = list(dev).index(nm)
        A = acq(dev[nm], "limited", M.DEV_SEED_BASE + 3000 * i, W)
        B = acq(dev[nm], "limited", M.DEV_SEED_BASE + 3000 * i + 1500, W)
        for p in range(A["Z"].shape[0]):
            for k in range(A["Z"].shape[1]):
                vals.append(F2.raw_B(A["Z"][p, k] - B["Z"][p, k], W)["B"])
    v = np.array(vals)
    return {"max": float(v.max()), "q999": float(np.quantile(v, .999)), "mean": float(v.mean()), "n": len(v)}


def b_signal(dev, a, b, W):
    """The instrument's MEASURED remaining envelope for a pair, on the block that carries the verdict."""
    ia, ib = list(dev).index(a), list(dev).index(b)
    A = acq(dev[a], "limited", M.DEV_SEED_BASE + 3000 * ia, W)
    B = acq(dev[b], "limited", M.DEV_SEED_BASE + 3000 * ib + 1500, W)
    br = F2.distance_bracket(A, B, tail_noise=1e9)
    top = max(br["blocks"], key=lambda x: x["d"])
    d = A["Z"][top["probe"], top["phase"]] - br["lam"] * B["Z"][top["probe"], (top["phase"] + br["shift"]) % 4]
    return {"B": F2.raw_B(d, W)["B"], "d_obs": br["d_obs"],
            "B_max_over_blocks": max(x["B"] for x in br["blocks"])}


# ---------------------------------------------------------------- NESTED PREFIXES (the correct T7/T8 substrate)
def prefix(A: dict, W: int) -> dict:
    """A nested PREFIX of one long acquisition: same noise realization, same interventions, window truncated.

    THIS IS THE ONLY HONEST WAY TO VARY THE WINDOW, AND MEASURING WHY WAS WORTH THE TROUBLE.

    A prefix of a long episode is NOT the same thing as a separately simulated short episode with the same seed.
    The engine draws the measurement noise `eta` (T samples) and THEN the drift innovations from the same RNG
    stream, so the drift sequence depends on T: change the episode length and the drift changes from sample zero.
    Measured: max|Z_long[:320] - Z_short(320)| = 6.48, on a system compared with ITSELF.

    v01's T7 and T8 compared separately simulated noisy episodes as though they differed only in length. They
    differed in their noise. Those controls were measuring the RNG, and their verdicts meant nothing.
    """
    P, K, WL = A["Z"].shape
    assert W <= WL, "a prefix cannot be longer than the acquisition"
    Z = A["Z"][:, :, :W]
    n_resp = int(sum(float(np.nanmax(np.abs(Z[p, k]))) >= F0.Z_DET
                     for p in range(P) for k in range(K) if not A["missing"][p, k]))
    n_valid = int((~A["missing"]).sum())
    return {**A, "Z": Z, "W": W, "n_responded": n_resp, "responsive": n_resp / max(n_valid, 1)}
