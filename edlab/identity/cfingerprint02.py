"""RESOLUTION-CERTIFIED TAIL-AWARE CONTINUOUS FINGERPRINT — EXP-GT-CONTINUOUS-FINGERPRINT-02.

    v00 asked  "is the signal still moving?"         and abstained on a decidable cascade.
    v01 asked  "can the remainder change the verdict?"  and could not SEE a remainder of 8.25 through a noise
               floor of 7.40.
    v02 must first ask  "WHAT IS THE SMALLEST REMAINDER THIS BATTERY CAN SEE AT ALL?"  -- and refuse to freeze
               until that number is certified against the remainders it has to detect.

THE NON-OBVIOUS POINT, AND THE REASON THIS IS AN EXPERIMENT AND NOT A PATCH.

A longer window is NOT automatically better. Both terms of the bound move with W, and they move the SAME WAY:

    B_noise(W)  falls   -- L grows, sd ~ 1/sqrt(L), and the amplification rho_max/(1-rho_max) collapses
    B_signal(W) falls   -- the true remaining envelope decays as exp(-W/tau): a longer window leaves LESS outside

So the ratio that matters can PEAK AND THEN DEGRADE. Raising W until the numbers look nice would be the same
unexamined reflex that produced the last two instruments. The horizon is SWEPT over a preregistered grid, the
ratio is MEASURED, and the SMALLEST admissible horizon is taken.

WHAT IS INHERITED, AND WHAT IS NAMED. v01 died in part because it imported v00's admission wholesale and silently
re-imported v00's dead in-flight guard with it. So the one check being replaced is NAMED here: `in_flight_frac` is
never consulted. Coverage, responsiveness, baseline stability, the identical-battery requirement and the
common-noise-channel refusal are the preserved core.

WHAT CHANGES, AND IS THEREFORE DECLARED: the OBSERVATION HORIZON, and with it the episode length. That makes v02 a
BROADER instrument than v00/v01, and the claim is bounded accordingly.
"""

from __future__ import annotations

import math

import numpy as np

from . import cfingerprint as F0
from ..substrates.ctrans.engine import Probe
from ..substrates.ctrans.manifests01 import D_MAX, TAU_MAX

T_TAIL0 = F0.D_HOLD + D_MAX          # 84. Settling may not be ASSESSED before the declared delay horizon (T5).
L_MAX_FACTOR = 6.0                   # the longest extension, in units of TAU_MAX, over which a remainder is buried
# OUT-OF-CONTRACT BARS, CALIBRATED ON NOISE-ONLY BLOCKS **PER HORIZON**. They are NOT constants.
# I first carried v01's W=160 values (5.0 / 3.0) across the whole grid, and at W>=240 EVERY pair -- including the
# NULL, a system against ITSELF -- came back OUT OF CONTRACT. The reason is the SLOW DRIFT: over a long tail region
# the sub-block means wander with the OU baseline, while `sd` is derived from the WHITE noise by differencing and
# therefore does not see drift at all. The level statistic's noise-only maximum grows 2.07 -> 7.20 -> 8.00 ->
# 15.11 -> 26.95 across the grid. A bar calibrated at one horizon is meaningless at another.
_BARS = {160: (3.0, 3.0), 240: (9.0, 4.0), 320: (10.0, 5.0), 480: (19.0, 5.0), 640: (34.0, 6.0)}


def bars(W: int):
    return _BARS[min(_BARS, key=lambda w: abs(w - W))]
BOUND_K = 2.0                        # upper-confidence multiplier on the decrement, used to BOUND (not to check).
RIP_NOISE_K = 2.5                    # the ripple of a pure-noise tail: max|x| over a sub-block is ~2.5 sigma.

SETTLED = "DECIDABLE_SETTLED"
SLOW_TAIL = "DECIDABLE_SLOW_TAIL"
IN_FLIGHT = "INDETERMINATE_IN_FLIGHT"
INDIST, DIFFERENT, INDETERMINATE = F0.INDIST, F0.DIFFERENT, F0.INDETERMINATE
EQUIVALENCE_CLASS_ONLY = "EQUIVALENCE_CLASS_ONLY"


def episode_len(W: int) -> int:
    """The episode must contain the pre-probe segment, the probe, every phase offset and the whole horizon."""
    return F0.T_PROBE + max(F0.PHASES) + W + 8


def sub_block_len(W: int) -> int:
    return (W - T_TAIL0) // 3


# ================================================================ acquisition (horizon-parameterised)
def acquire(measure, arm: str, seed0: int, W: int, quantize_uint8: bool = False, n_repeat: int = None) -> dict:
    """The PRESERVED NSRC pipeline, with the horizon as a parameter instead of a module constant.

    Reimplemented rather than imported because v00's `acquire` hard-codes T_OBS = 304 and v00's file is FROZEN --
    its hashes are the evidence that it failed honestly, and they must keep verifying. Everything the pipeline
    does is the v00 core: one independent baseline per probe episode, deviation averaged over repeats, offset
    detrend on the pre-probe segment, division by the channel's own measured noise scale.
    """
    T = episode_len(W)
    R = F0.N_REPEAT if n_repeat is None else n_repeat
    probes = F0.battery(arm)
    P, K = len(probes), len(F0.PHASES)

    eps, meta = [], []
    for r in range(R):
        for pi, (nm, tgt, kind, amp, hold) in enumerate(probes):
            for ki, ph in enumerate(F0.PHASES):
                eps.append(Probe("base", -1, "none", 0.0, 0, 10 ** 9)); meta.append(("base", r, pi, ki))
                eps.append(Probe(nm, tgt, kind, amp, hold, F0.T_PROBE + ph)); meta.append(("probe", r, pi, ki))
    u, ok = measure(eps, T, np.arange(seed0, seed0 + len(eps)))
    if quantize_uint8:
        u = np.nan_to_num(u).astype(np.uint8).astype(float)   # MUST-FAIL: the cast at the ADC, on the raw float

    base, rows = {}, {}
    for i, (t, r, pi, ki) in enumerate(meta):
        (base if t == "base" else rows.setdefault((pi, ki), {}))[
            (r, pi, ki) if t == "base" else r] = (u[i] if t == "base" else (u[i], ok[i]))

    Z = np.full((P, K, W), np.nan)
    missing = np.zeros((P, K), dtype=bool)
    raw, pre_pool = {}, []
    for pi in range(P):
        for ki, ph in enumerate(F0.PHASES):
            onset = F0.T_PROBE + ph
            got = rows[(pi, ki)]
            if not all(got[r][1] for r in range(R)):
                missing[pi, ki] = True
                continue
            dev = np.mean([got[r][0][onset - F0.W_PRE:onset + W] - base[(r, pi, ki)][onset - F0.W_PRE:onset + W]
                           for r in range(R)], axis=0)
            raw[(pi, ki)] = dev
            pre_pool.append(dev[:F0.W_PRE])
    if not pre_pool:
        return {"Z": Z, "missing": missing, "coverage": 0.0, "responsive": 0.0, "arm": arm, "W": W,
                "sigma_hat": float("nan"), "baseline_stability": float("nan"), "n_responded": 0}

    sigma_hat = F0._diff_sigma(np.concatenate(pre_pool))
    if not np.isfinite(sigma_hat) or sigma_hat <= 0:
        sigma_hat = float(np.std(np.concatenate(pre_pool))) or 1e-300
    resid, n_resp = [], 0
    for (pi, ki), dev in raw.items():
        d = dev - np.median(dev[:F0.W_PRE])
        resid.append(d[:F0.W_PRE])
        z = d[F0.W_PRE:] / sigma_hat
        Z[pi, ki] = z
        n_resp += int(float(np.nanmax(np.abs(z))) >= F0.Z_DET)
    n_valid = int((~missing).sum())
    return {"Z": Z, "missing": missing, "arm": arm, "W": W, "sigma_hat": sigma_hat,
            "coverage": n_valid / (P * K), "responsive": n_resp / max(n_valid, 1), "n_responded": n_resp,
            "baseline_stability": float(np.sqrt(np.mean(np.concatenate(resid) ** 2)) / sigma_hat),
            "probes": [p[0] for p in probes]}


# ================================================================ the tail bound
def raw_B(delta: np.ndarray, W: int, tau_max: float = TAU_MAX):
    """The remaining-envelope statistic, WITHOUT the settled/unbounded verdict. This is the quantity whose NOISE
    FLOOR the resolution certificate measures, and whose SIGNAL the certificate must clear by a factor k."""
    L = sub_block_len(W)
    tail = delta[T_TAIL0:T_TAIL0 + 3 * L]
    b1, b2, b3 = tail[:L], tail[L:2 * L], tail[2 * L:]
    mu1, mu2, mu3 = float(b1.mean()), float(b2.mean()), float(b3.mean())
    sig = float(np.std(np.diff(tail)) / math.sqrt(2.0))
    sd = sig * math.sqrt(2.0 / L)
    d1, d2 = abs(mu2 - mu1), abs(mu3 - mu2)
    rip2, rip3 = float(np.max(np.abs(b2 - mu2))), float(np.max(np.abs(b3 - mu3)))
    rm = math.exp(-L / tau_max)
    B = (d2 + BOUND_K * sd) * rm / (1.0 - rm) + max(0.0, rip3 - RIP_NOISE_K * sig)
    return {"B": B, "mu3": mu3, "d1": d1, "d2": d2, "rip2": rip2, "rip3": rip3, "sig": sig, "sd": sd,
            "rho_max": rm, "L": L}


def tail_bound(delta: np.ndarray, W: int, tail_noise: float, tau_max: float = TAU_MAX) -> dict:
    """Contract CHECKED, never fitted. The rate is not estimated -- the contract declares the slowest admissible
    relaxation, and the checks merely verify the system honours it. A tail that does not is OUT OF CONTRACT and
    gets no bound at all; the instrument will not invent one."""
    q = raw_B(delta, W, tau_max)
    L, rm, sig, sd = q["L"], q["rho_max"], q["sig"], q["sd"]
    LVL_K, RIP_K = bars(W)
    if q["d2"] > rm * q["d1"] + LVL_K * sd * math.sqrt(1.0 + rm ** 2):
        return {"status": IN_FLIGHT, "K": 0.0, "B": q["B"],
                "why": "the LEVEL is not decaying as fast as the declared TAU_MAX=%.0f. OUT OF CONTRACT." % tau_max}
    if q["rip3"] > rm * q["rip2"] + RIP_K * sig:
        return {"status": IN_FLIGHT, "K": 0.0, "B": q["B"],
                "why": "the RIPPLE is not damping as fast as the declared TAU_MAX. An oscillation that does not "
                       "decay has no remainder bound."}
    B = q["B"]
    if B <= tail_noise:
        return {"status": SETTLED, "delta_inf": q["mu3"], "B": B, "K": 0.0,
                "why": "remaining envelope %.2f is at or below the certified noise floor %.2f" % (B, tail_noise)}
    Kext = tau_max * math.log(max(B, 1.0))
    if Kext > L_MAX_FACTOR * tau_max:
        return {"status": IN_FLIGHT, "K": Kext, "B": B,
                "why": "burying a remainder of %.1f needs %.0f samples, beyond the declared L_MAX" % (B, Kext)}
    return {"status": SLOW_TAIL, "delta_inf": q["mu3"], "B": B, "K": Kext,
            "why": "bounded relaxation: envelope %.1f about a level of %.1f, extension %.0f" % (B, q["mu3"], Kext)}


def distance_bracket(A: dict, B: dict, tail_noise: float, guard: str = "bound") -> dict:
    W = A["W"]
    ZA, ZB = A["Z"], B["Z"]
    P, K, _ = ZA.shape
    valid = (~A["missing"]) & (~B["missing"])
    band = F0.SCALE_BAND
    best = (math.inf, None, None)
    for s in range(K):
        pr = [(ZA[i, k], ZB[i, (k + s) % K]) for i in range(P) for k in range(K)
              if valid[i, k] and valid[i, (k + s) % K]]
        if not pr:
            continue
        num = sum(float(np.dot(a, b)) for a, b in pr)
        den = sum(float(np.dot(b, b)) for a, b in pr)
        lam = float(np.clip(num / den, 1 - band, 1 + band)) if (band > 0 and den > 0) else 1.0
        d = max(float(np.sqrt(np.mean((a - lam * b) ** 2))) for a, b in pr)
        if d < best[0]:
            best = (d, s, lam)
    d_obs, s, lam = best
    if s is None:
        return {"d_obs": float("nan"), "D_lo": 0.0, "D_hi": math.inf, "status": IN_FLIGHT, "blocks": []}
    blocks, D_lo, D_hi, any_fl, any_slow = [], 0.0, 0.0, False, False
    for i in range(P):
        for k in range(K):
            k2 = (k + s) % K
            if not (valid[i, k] and valid[i, k2]):
                continue
            delta = ZA[i, k] - lam * ZB[i, k2]
            db = float(np.sqrt(np.mean(delta ** 2)))
            if guard == "none":
                tb, lo, hi = {"status": SETTLED, "B": 0.0}, db, db
            else:
                tb = tail_bound(delta, W, tail_noise)
                if tb["status"] == IN_FLIGHT:
                    lo, hi, any_fl = 0.0, math.inf, True
                else:
                    Kx, di, Bv = tb["K"], tb.get("delta_inf", 0.0), tb["B"]
                    if Kx <= 0:
                        lo = hi = db
                    else:
                        rlo, rhi = max(0.0, abs(di) - Bv), abs(di) + Bv
                        lo = math.sqrt((W * db ** 2 + Kx * rlo ** 2) / (W + Kx))
                        hi = math.sqrt((W * db ** 2 + Kx * rhi ** 2) / (W + Kx))
                    any_slow |= (tb["status"] == SLOW_TAIL)
            D_lo, D_hi = max(D_lo, lo), max(D_hi, hi)
            blocks.append({"probe": i, "phase": k, "d": db, "lo": lo, "hi": hi, "tail": tb["status"],
                           "B": tb.get("B", 0.0)})
    return {"d_obs": d_obs, "D_lo": D_lo, "D_hi": D_hi, "shift": s, "lam": lam, "blocks": blocks,
            "status": IN_FLIGHT if any_fl else (SLOW_TAIL if any_slow else SETTLED)}


def admit(A, B, common_channel, enforce_channel=True):
    """The preserved core MINUS the one check v01/v02 replace. `in_flight_frac` is NOT consulted -- naming it is
    the whole lesson of v01, which inherited v00's dead guard by importing admission wholesale."""
    cov = min(A["coverage"], B["coverage"])
    if not np.array_equal(A["missing"], B["missing"]):
        return {"ok": False, "coverage": cov, "code": "INSUFFICIENT_COVERAGE",
                "why": "the two systems do not admit the same interventions: no common repertoire exists."}
    if enforce_channel and not common_channel:
        return {"ok": False, "coverage": cov, "code": "CONFOUNDED",
                "why": "not declared to sit on a common noise channel. Absolute gain is not identifiable when both "
                       "the readout scale and the noise scale are free."}
    if cov < F0.COVERAGE_FLOOR:
        return {"ok": False, "coverage": cov, "code": "INSUFFICIENT_COVERAGE",
                "why": "probe coverage %.2f below the frozen floor %.2f" % (cov, F0.COVERAGE_FLOOR)}
    for tag, S in (("left", A), ("right", B)):
        if S["responsive"] == 0.0:
            return {"ok": False, "coverage": cov, "code": "INSUFFICIENT_RESPONSIVENESS",
                    "why": "the %s system answered NOTHING. Silence is not a fingerprint." % tag}
        if S["baseline_stability"] > F0.BASELINE_MAX:
            return {"ok": False, "coverage": cov, "code": "OUT_OF_SCOPE",
                    "why": "the %s system's baseline WANDERS (%.1fx its white-noise scale). Nonstationary."
                           % (tag, S["baseline_stability"])}
    return {"ok": True, "coverage": cov, "code": "ADMITTED", "why": "admitted"}


def compare(A, B, r_cont, r_sep, tail_noise, common_channel=True, enforce_channel=True, guard="bound"):
    """The verdict is read off the BRACKET, never off the point estimate. THERE IS NO SAME."""
    adm = admit(A, B, common_channel, enforce_channel)
    br = distance_bracket(A, B, tail_noise, guard=guard)
    out = {"distance": br["d_obs"], "D_lo": br["D_lo"], "D_hi": br["D_hi"], "tail_status": br["status"],
           "coverage": adm["coverage"], "admitted": adm["ok"], "code": adm["code"]}
    if not adm["ok"]:
        return {**out, "verdict": INDETERMINATE, "why": adm["why"]}
    if br["status"] == IN_FLIGHT and guard != "none":
        return {**out, "verdict": INDETERMINATE, "code": IN_FLIGHT,
                "why": "at least one probe's tail is not a bounded relaxation. No bound exists and none is invented."}
    if br["D_hi"] <= r_cont:
        return {**out, "verdict": INDIST, "code": EQUIVALENCE_CLASS_ONLY, "equivalence_class_only": True,
                "why": "even the WORST admissible continuation keeps them inside the continuity radius "
                       "(D_hi=%.2f <= %.2f). An EQUIVALENCE CLASS relative to this repertoire, not an identity."
                       % (br["D_hi"], r_cont)}
    if br["D_lo"] >= r_sep:
        return {**out, "verdict": DIFFERENT,
                "why": "even the BEST admissible continuation cannot pull them together (D_lo=%.2f >= %.2f); the "
                       "tail is %s and cannot change the verdict." % (br["D_lo"], r_sep, br["status"])}
    return {**out, "verdict": INDETERMINATE, "code": IN_FLIGHT,
            "why": "the bracket [%.2f, %.2f] STRADDLES a decision boundary. The unseen remainder could still "
                   "decide this, so the instrument does not." % (br["D_lo"], br["D_hi"])}
