"""THE TAIL-AWARE CONTINUOUS CAUSAL FINGERPRINT — EXP-GT-CONTINUOUS-FINGERPRINT-01.

    Version 00 asked:  "IS THE SIGNAL STILL MOVING?"
    It should have asked:  "CAN THE UNOBSERVED REMAINDER STILL CHANGE THE VERDICT?"

Those are different questions and v00 died of the difference. It measured `P_cascade` at a distance of 64.15
against a separation radius of 23.36 -- strongly separated -- and then REFUSED TO SAY SO, because the tail was
still moving by 5.3% of peak against a frozen 5% threshold. The true settling time was 108 inside a 160-sample
window. The window was long enough. The system was decidable. The instrument abstained anyway.

A FABRICATED ABSTENTION IS EXACTLY AS DISHONEST AS A FABRICATED CERTAINTY. It just looks like caution.

RAISING THE 5% THRESHOLD IS FORBIDDEN and would not even work: control T4 is a pair whose observed distance is
33.97 -- comfortably DIFFERENT to any threshold-based guard -- and whose answer is nevertheless still outside the
window. A bigger threshold gets T4 confidently, catastrophically wrong.

---------------------------------------------------------------------------------------------------------------
WHAT THIS FILE CHANGES, AND WHAT IT REFUSES TO TOUCH.

CHANGED:  the in-flight guard, and the verdict logic that reads it.
PRESERVED, byte-for-byte, by IMPORT rather than by copy:  the probe battery, the acquisition, the NSRC
representation, the noise calibration, sigma_hat, the lambda-quotient for noise-scale estimator uncertainty, the
max-over-probes aggregation, coverage, responsiveness, baseline stability, the identical-battery requirement, the
common-noise-channel refusal, and EQUIVALENCE_CLASS_ONLY.

v00's six frozen files are NOT modified. Its freeze manifest still verifies byte-for-byte. That record has to
survive, because it is the evidence that v00 failed honestly.
---------------------------------------------------------------------------------------------------------------

THE METHOD: BRACKET THE EVENTUAL DISTANCE. DO NOT MODEL THE TAIL.

A flexible tail model can fit anything, and a thing that fits anything has certified nothing. So no curve is
fitted to the response. Instead, on the DIFFERENCE trace of the pair -- which is the only thing the verdict
depends on -- three block means and one ripple give a bounded geometric extrapolation, and the verdict is read
off a BRACKET rather than a point:

    D_hi <= r_continuity  ->  INDISTINGUISHABLE   (no continuation can push them apart)
    D_lo >= r_separation  ->  DIFFERENT           (no continuation can pull them together)
    otherwise             ->  INDETERMINATE_IN_FLIGHT   (the remainder could still decide it, so we do not)

A block whose tail is not a bounded relaxation gets d_lo = 0, d_hi = inf and forces abstention on its own. There
is no fraction threshold and no knob.
"""

from __future__ import annotations

import math

import numpy as np

from . import cfingerprint as F0                       # THE PRESERVED CORE. Imported, never copied, never edited.
from ..substrates.ctrans.manifests01 import D_MAX, TAU_MAX

# ---------------------------------------------------------------- the DECLARED TAIL CONTRACT
L_MAX = 480.0          # 6 * TAU_MAX. The longest extension over which a remainder may be buried.
LVL_K = 5.0            # LEVEL-CHECK bar, in units of the level-difference noise. CALIBRATED ON NOISE-ONLY BLOCKS
RIP_K = 3.0            # RIPPLE-CHECK bar, in units of the white-noise scale.        (288 blocks, no labels used):
                       #   level  statistic on noise: mean +0.31, max 3.49  -> bar 5.0
                       #   ripple statistic on noise: mean +0.61, max 2.23  -> bar 3.0
                       # These bars decide OUT-OF-CONTRACT. They must be high enough that 64 blocks x 108 pairs of
                       # pure noise never trip one, or the instrument calls a system unbounded because it looked at
                       # it too many times.
RIP_NOISE_K = 2.5      # the ripple of a PURE-NOISE tail: max|x| over ~25 samples is ~2.5 sigma.
BOUND_K = 2.0          # the UPPER CONFIDENCE MULTIPLIER on the per-sub-block decrement, used to BOUND the
                       # remainder. It is NOT the same number as the check bar and must not be.
                       #
                       # I first used the check bar (6 sigma) for both. A 6-sigma upper bound on a decrement whose
                       # noise is 0.6 inflates the remaining-movement bound to ~15 noise units ON PURE NOISE --
                       # comparable to the 22-unit remainder the T4 case exists to detect. The bound drowned the
                       # thing it was bounding. A CHECK wants a high bar (it must not fire by accident across
                       # thousands of blocks); a BOUND wants an ordinary one (it must not be so conservative that
                       # it is uninformative). Conflating them is not conservatism, it is noise.
TAIL_NOISE = 9.0       # a remaining envelope at or below this is NOISE, not an unresolved cause. It is
                       # the SAME quantity B the bound computes, measured on blocks that CANNOT contain a signal:
                       # 288 noise-only blocks give B mean 3.76, q99.9 7.39, MAX 7.40. TAIL_NOISE = 9.0 is 1.2x the
                       # largest value the bound ever produces on pure noise. No label was consulted.
                       #
                       # THIS NUMBER IS ALSO THE INSTRUMENT'S RESOLUTION FLOOR, AND IT IS WHAT KILLS VERSION 01.
                       # A remainder whose envelope is below 9.0 is, to this bound, indistinguishable from nothing.
                       # The T4 near-boundary pair -- built so that a real ~10% of its difference energy lies
                       # BEYOND the window -- produces a measured envelope of 8.25. It sits INSIDE the floor. The
                       # bound cannot see it, calls it SETTLED, and returns a confident DIFFERENT on a pair whose
                       # answer is still partly outside the window. See the development certificate.
                       #
                       # AN EARLIER VERSION GATED ON THE TAIL'S *ACTIVITY* -- how much it varies INSIDE the window
                       # -- AND THAT WAS EXACTLY BACKWARDS. The slower a relaxation is, the FLATTER it looks in the
                       # window, and the MORE remainder it carries. The T4 pair's tail varies by ~4 noise units
                       # in-window while carrying a ~22-unit remainder; an activity gate waved it through as
                       # "settled" and the instrument returned a confident DIFFERENT on a pair whose answer was
                       # still entirely outside the window. The gate must be on the REMAINING ENVELOPE, which is
                       # what the bound is for.

# ---------------------------------------------------------------------------------------------------------------
# A DECLARED LIMIT OF THE CONTRACT CHECK, MEASURED AND NOT HIDDEN.
#
# The out-of-contract test compares a per-sub-block decay factor against rho_max = exp(-L/TAU_MAX). For TAU_MAX=80
# and L=25 that is 0.732. A system at tau = 130 -- well outside the contract -- decays at 0.825. The two differ by
# 0.09 per sub-block, while the noise on the decrement that carries them is comparable. MEASURED: the check cannot
# separate tau = 130 from tau = 80 in the limited arm at any SNR this substrate produces.
#
#     THE CHECK RELIABLY DETECTS  tau  >~  2.5 * TAU_MAX.  IN THE BAND (TAU_MAX, ~2.5*TAU_MAX) A SYSTEM MAY BE
#     SILENTLY ACCEPTED AS IN-CONTRACT, AND THE BOUND -- WHICH ASSUMES tau <= TAU_MAX -- IS THEN TOO TIGHT.
#
# This is a soundness limit, not a tuning choice, and it is stated here rather than discovered later by someone
# else. The benchmark's out-of-contract systems are placed DECISIVELY outside (tau >= 3.5 * TAU_MAX) so that the
# check is testing what it can actually do; the band itself is reported as UNVERIFIED SCOPE.
# ---------------------------------------------------------------------------------------------------------------

T_TAIL0 = F0.D_HOLD + D_MAX     # 24 + 60 = 84.
# ---------------------------------------------------------------------------------------------------------------
# THE DELAY HORIZON, AND WHY SETTLING MAY NOT BE ASSESSED BEFORE IT.
#
# No causal component may arrive later than (probe end + D_MAX) -- that is what D_MAX DECLARES. So before t = 84
# the response may be perfectly flat and still have a second cause on the way. A guard that stops as soon as the
# local derivative goes quiet stops in that plateau, computes a fingerprint on half a response, and hands back a
# confident verdict about a system it has not finished listening to. That is control T5, and the ONLY defence is
# to refuse to assess settling until the declared horizon has elapsed. It is not a tunable. It is the contract.
# ---------------------------------------------------------------------------------------------------------------

SETTLED = "DECIDABLE_SETTLED"
SLOW_TAIL = "DECIDABLE_SLOW_TAIL"
IN_FLIGHT = "INDETERMINATE_IN_FLIGHT"

INDIST, DIFFERENT, INDETERMINATE = F0.INDIST, F0.DIFFERENT, F0.INDETERMINATE


def tail_bound(delta: np.ndarray, t_tail0: int = None, tau_max: float = None,
               tail_noise: float = None, l_max: float = None) -> dict:
    """Bound what the UNSEEN remainder of one probe block's difference trace can still do.

    NO DECAY RATE IS ESTIMATED, AND THAT IS THE WHOLE POINT.

    My first version fitted the rate: rho = (mu3-mu2)/(mu2-mu1), a ratio of two differences of noisy block means.
    On a quiet tail both differences ARE noise, the ratio is a ratio of two noises, and it exceeded the
    non-convergence threshold at random -- so the instrument declared perfectly ordinary systems UNBOUNDED and
    abstained on them. It read its own estimator's variance as the world refusing to settle.

    The contract already DECLARES the slowest admissible relaxation. So the rate is never estimated -- it is
    ASSUMED to be the worst the contract allows, and the contract is merely CHECKED:

        rho_max = exp(-L / TAU_MAX)     the most a level may still hold on to, per sub-block, and stay in contract

        CONTRACT CHECK   |d2| <= rho_max*|d1| + noise      the level is decaying at least as fast as TAU_MAX
        CONTRACT CHECK   rip3 <= rho_max*rip2 + noise      the RIPPLE is damping at least as fast (underdamped tails)
        WORST-CASE BOUND R = |d2|_eff * rho_max/(1-rho_max)          remaining level movement
                         B = R + rip3_eff                            remaining envelope

    Either check failing means the response is NOT a bounded relaxation within the declared domain: OUT OF
    CONTRACT, refused, and no bound invented. Noise is SUBTRACTED from both terms before they are used, so a tail
    that is merely noisy contributes an envelope of zero and is SETTLED -- which is what stops drift from being
    promoted to an unresolved cause (T6).
    """
    t0 = T_TAIL0 if t_tail0 is None else t_tail0
    tmax = TAU_MAX if tau_max is None else tau_max
    tn = TAIL_NOISE if tail_noise is None else tail_noise
    lmax = L_MAX if l_max is None else l_max

    tail = delta[t0:]
    L = len(tail) // 3
    if L < 4:
        return {"status": IN_FLIGHT, "K": 0.0, "lo": 0.0, "hi": math.inf,
                "why": "the window leaves no assessable tail after the declared delay horizon"}
    b1, b2, b3 = tail[:L], tail[L:2 * L], tail[2 * L:3 * L]
    mu1, mu2, mu3 = float(b1.mean()), float(b2.mean()), float(b3.mean())

    sig = float(np.std(np.diff(tail)) / math.sqrt(2.0))      # white-noise scale OF THE DIFFERENCE TRACE
    sem = sig / math.sqrt(L)                                 # noise on a sub-block mean
    sd = sem * math.sqrt(2.0)                                # noise std of a LEVEL DIFFERENCE (d1, d2)

    d1, d2 = abs(mu2 - mu1), abs(mu3 - mu2)
    rip2 = float(np.max(np.abs(b2 - mu2)))
    rip3 = float(np.max(np.abs(b3 - mu3)))
    rho_max = math.exp(-L / tmax)

    # THE CONTRACT CHECKS ARE NOISE-CALIBRATED STATISTICAL TESTS, NOT COMPARISONS OF TWO NOISY NUMBERS.
    # LVL_K and RIP_K are calibrated on NOISE-ONLY blocks (see the development certificate). A per-block test at a
    # nominal 4 sigma fires by chance across 64 blocks x 108 comparisons -- and the residual drift makes the block
    # means wander further than the white-noise estimate predicts, so "4 sigma" was not 4 sigma. The bars are set
    # from the observed noise-only distribution instead of from a normal table.
    lvl_bar = rho_max * d1 + LVL_K * sd * math.sqrt(1.0 + rho_max ** 2)
    if d2 > lvl_bar:
        return {"status": IN_FLIGHT, "K": 0.0, "lo": 0.0, "hi": math.inf, "d1": d1, "d2": d2,
                "why": "the LEVEL is not decaying as fast as the declared TAU_MAX=%.0f (|d2|=%.2f > %.2f). Slower "
                       "than the contract allows, or not relaxing at all. OUT OF CONTRACT." % (tmax, d2, lvl_bar)}
    rip_bar = rho_max * rip2 + RIP_K * sig
    if rip3 > rip_bar:
        return {"status": IN_FLIGHT, "K": 0.0, "lo": 0.0, "hi": math.inf, "rip2": rip2, "rip3": rip3,
                "why": "the RIPPLE is not damping as fast as the declared TAU_MAX (rip3=%.2f > %.2f). An "
                       "oscillation that does not decay has no remainder bound." % (rip3, rip_bar)}

    # ------------------------------------------------------------------------------------------------------
    # THE NOISE IS ADDED TO THE DECREMENT, NOT SUBTRACTED FROM IT. THIS IS THE WHOLE BOUND.
    #
    # I first wrote d2_eff = max(0, d2 - 4*sd), subtracting the noise. That is the direction that FLATTERS the
    # instrument, and it produced exactly the failure this whole version exists to prevent. The T4 pair's tail
    # sits at a LEVEL of 22 noise units and decays so slowly that its per-sub-block decrement (2.17) is barely
    # above the noise on that decrement (sd ~ 0.6). Subtracting the noise drove the decrement to zero, the
    # remaining movement to zero, and the instrument concluded "settled, remainder below the noise floor" -- about
    # a level of 22 that must eventually reach zero. It then returned a confident DIFFERENT on a pair whose answer
    # was still entirely outside the window.
    #
    # WHEN THE DECAY IS TOO SLOW TO RESOLVE ABOVE THE NOISE, THE HONEST INFERENCE IS THAT THE REMAINDER IS LARGE,
    # NOT THAT IT IS ZERO. So the UPPER confidence bound on the decrement is used, and the remaining movement is
    # bounded by the slowest relaxation the contract permits.
    # ------------------------------------------------------------------------------------------------------
    d2_up = d2 + BOUND_K * sd                        # UPPER bound on the per-sub-block decrement
    # The ripple is a MAX over 25 samples, so on a perfectly quiet tail it is already ~2.5 sigma of pure noise --
    # about 5 noise units of nothing. Left in, it dominated the bound and drowned the very remainders the bound
    # exists to find. Its own noise is subtracted, exactly as the level's is.
    rip3_eff = max(0.0, rip3 - RIP_NOISE_K * sig)
    R = d2_up * rho_max / (1.0 - rho_max)            # worst-case remaining level movement, at TAU_MAX
    B = R + rip3_eff                                 # worst-case remaining envelope about the observed level
    if B <= tn:
        return {"status": SETTLED, "delta_inf": mu3, "B": tn, "K": 0.0, "tau": tmax, "sig": sig,
                "why": "remaining envelope %.2f is at or below the noise floor %.2f -- nothing left out there that "
                       "could matter" % (B, tn)}
    K = tmax * math.log(max(B, 1.0))
    if K > lmax:
        return {"status": IN_FLIGHT, "K": K, "lo": 0.0, "hi": math.inf, "B": B,
                "why": "burying a remainder of %.1f needs %.0f samples, beyond the declared L_MAX=%.0f"
                       % (B, K, lmax)}
    return {"status": SLOW_TAIL, "delta_inf": mu3, "B": B, "K": K, "tau": tmax, "sig": sig,
            "why": "bounded relaxation: remaining envelope B=%.1f about a level of %.1f, extension K=%.0f"
                   % (B, mu3, K)}


def _bracket(d_obs: float, W: int, K: float, delta_inf: float, B: float):
    """d_ext = sqrt((W*d_obs^2 + K*rho^2)/(W+K)) is MONOTONE in rho, so bracketing rho brackets d_ext.

    The bracket is INDEPENDENT of how the extension is sliced -- only its length K enters -- which is why this
    needs no assumption about what the world does after the window beyond "it relaxes, and by this much at most"."""
    if K <= 0:
        return d_obs, d_obs
    lo_rho = max(0.0, abs(delta_inf) - B)
    hi_rho = abs(delta_inf) + B
    lo = math.sqrt((W * d_obs ** 2 + K * lo_rho ** 2) / (W + K))
    hi = math.sqrt((W * d_obs ** 2 + K * hi_rho ** 2) / (W + K))
    return lo, hi


def distance_bracket(A: dict, B: dict, scale_band: float = None, guard: str = "bound",
                     t_tail0: int = None, tau_max: float = None) -> dict:
    """The observed distance, AND a bracket on what it becomes once the remainder is in.

    The shift and lambda are chosen exactly as the preserved core chooses them -- by minimizing the OBSERVED
    distance -- and the bound is then computed at that choice. Aggregation across blocks is the preserved MAX:
    'indistinguishable under the repertoire' is a FOR-ALL, and a for-all is certified by its worst case. The max of
    the per-block lower bounds is a valid lower bound on the max, and likewise for the upper. """
    band = F0.SCALE_BAND if scale_band is None else scale_band
    ZA, ZB = A["Z"], B["Z"]
    P, K_ph, W = ZA.shape
    valid = (~A["missing"]) & (~B["missing"])

    best = (math.inf, None, None)
    for s in range(K_ph):
        pr = [(ZA[i, k], ZB[i, (k + s) % K_ph]) for i in range(P) for k in range(K_ph)
              if valid[i, k] and valid[i, (k + s) % K_ph]]
        if not pr:
            continue
        num = sum(float(np.dot(a, b)) for a, b in pr)
        den = sum(float(np.dot(b, b)) for a, b in pr)
        lam = float(np.clip(num / den, 1.0 - band, 1.0 + band)) if (band > 0 and den > 0) else 1.0
        d = max(float(np.sqrt(np.mean((a - lam * b) ** 2))) for a, b in pr)
        if d < best[0]:
            best = (d, s, lam)
    d_obs, s, lam = best
    if s is None:
        return {"d_obs": float("nan"), "D_lo": 0.0, "D_hi": math.inf, "status": IN_FLIGHT, "blocks": []}

    blocks, D_lo, D_hi, any_flight, any_slow = [], 0.0, 0.0, False, False
    for i in range(P):
        for k in range(K_ph):
            k2 = (k + s) % K_ph
            if not (valid[i, k] and valid[i, k2]):
                continue
            delta = ZA[i, k] - lam * ZB[i, k2]
            db = float(np.sqrt(np.mean(delta ** 2)))
            if guard == "none":
                # CONTROL T9: no guard at all. The point estimate IS the verdict.
                tb = {"status": SETTLED, "delta_inf": 0.0, "B": 0.0, "K": 0.0}
                lo = hi = db
            else:
                tb = tail_bound(delta, t_tail0=t_tail0, tau_max=tau_max)
                if tb["status"] == IN_FLIGHT:
                    lo, hi = 0.0, math.inf
                    any_flight = True
                else:
                    lo, hi = _bracket(db, W, tb["K"], tb["delta_inf"], tb["B"])
                    any_slow |= (tb["status"] == SLOW_TAIL)
            D_lo, D_hi = max(D_lo, lo), max(D_hi, hi)
            blocks.append({"probe": i, "phase": k, "d": db, "lo": lo, "hi": hi, "tail": tb["status"],
                           "K": tb.get("K", 0.0), "tau": tb.get("tau", 0.0), "B": tb.get("B", 0.0)})
    status = IN_FLIGHT if any_flight else (SLOW_TAIL if any_slow else SETTLED)
    return {"d_obs": d_obs, "D_lo": D_lo, "D_hi": D_hi, "status": status, "shift": s, "lam": lam,
            "blocks": blocks}


def admit(A: dict, B: dict, common_channel: bool, enforce_channel: bool = True) -> dict:
    """The PRESERVED admission core -- MINUS the one check version 01 exists to replace.

    I first called F0.admit() directly, and it quietly re-imposed VERSION 00'S IN-FLIGHT GUARD. The tail bound
    would compute D_lo = 57.70 against a separation radius of 22.12 for the burned regression pair -- proving the
    verdict could not change -- and the dead guard inside the inherited admission would refuse it anyway. Six of
    the eight development failures were that, including T1 itself.

    INHERITING A CORE MEANS INHERITING ITS BUGS UNLESS YOU NAME THE ONE YOU ARE REPLACING. Named here:
    `in_flight_frac` is NOT consulted. Everything else -- coverage, responsiveness, baseline stability, the
    identical-battery requirement, the common-noise-channel refusal -- is the v00 core, unchanged.
    """
    cov = min(A["coverage"], B["coverage"])
    if not np.array_equal(A["missing"], B["missing"]):
        return {"ok": False, "coverage": cov,
                "why": "the two systems do not admit the same interventions. There is no common repertoire on "
                       "which a comparison is even defined."}
    if enforce_channel and not common_channel:
        return {"ok": False, "coverage": cov,
                "why": "not declared to sit on a common noise channel. Absolute gain is not identifiable when both "
                       "the readout scale and the noise scale are free. REFUSED rather than guessed."}
    if cov < F0.COVERAGE_FLOOR:
        return {"ok": False, "coverage": cov,
                "why": "probe coverage %.2f below the frozen floor %.2f" % (cov, F0.COVERAGE_FLOOR)}
    for tag, S in (("left", A), ("right", B)):
        if S["responsive"] == 0.0:
            return {"ok": False, "coverage": cov,
                    "why": "the %s system answered NOTHING to every probe. Silence is not a fingerprint." % tag}
        if S["baseline_stability"] > F0.BASELINE_MAX:
            return {"ok": False, "coverage": cov,
                    "why": "the %s system's baseline WANDERS (%.1f x its white-noise scale). Nonstationary."
                           % (tag, S["baseline_stability"])}
    return {"ok": True, "coverage": cov, "why": "admitted"}


def compare(A: dict, B: dict, r_continuity: float, r_separation: float, common_channel: bool = True,
            enforce_channel: bool = True, guard: str = "bound", **kw) -> dict:
    """The verdict is read off the BRACKET, never off the point estimate. THERE IS STILL NO SAME."""
    adm = admit(A, B, common_channel, enforce_channel)
    br = distance_bracket(A, B, guard=guard, **kw)
    out = {"distance": br["d_obs"], "D_lo": br["D_lo"], "D_hi": br["D_hi"], "tail_status": br["status"],
           "coverage": adm["coverage"], "admitted": adm["ok"]}
    if not adm["ok"]:
        return {**out, "verdict": INDETERMINATE, "why": adm["why"]}
    if br["status"] == IN_FLIGHT and guard != "none":
        # A SINGLE UNBOUNDED BLOCK IS NOT OUTVOTED BY WELL-BEHAVED ONES.
        # The whole representation assumes the response is CONTAINED in the window. If one probe's tail is not a
        # bounded relaxation, that assumption has failed FOR THIS SYSTEM, and a bound computed on the blocks that
        # happen to look convergent is a bound on a contract the system does not honour. The max-over-blocks
        # aggregation would happily certify DIFFERENT off one loud, well-behaved probe while another probe rings
        # forever. That is a verdict about a system the instrument does not cover.
        return {**out, "verdict": INDETERMINATE,
                "why": "at least one probe's tail is NOT a bounded relaxation (non-converging, or slower than the "
                       "declared TAU_MAX). There is no bound to be had and the instrument will not invent one."}
    if br["D_hi"] <= r_continuity:
        return {**out, "verdict": INDIST, "equivalence_class_only": True,
                "why": "even the WORST admissible continuation leaves them inside the continuity radius "
                       "(D_hi=%.2f <= %.2f). An EQUIVALENCE CLASS relative to this repertoire -- not an identity."
                       % (br["D_hi"], r_continuity)}
    if br["D_lo"] >= r_separation:
        return {**out, "verdict": DIFFERENT,
                "why": "even the BEST admissible continuation cannot pull them back together (D_lo=%.2f >= %.2f). "
                       "The tail is %s and it cannot change the verdict."
                       % (br["D_lo"], r_separation, br["status"])}
    return {**out, "verdict": INDETERMINATE,
            "why": "the bracket [%.2f, %.2f] STRADDLES a decision boundary (r_cont=%.2f, r_sep=%.2f). The unseen "
                   "remainder could still decide this, so the instrument does not."
                   % (br["D_lo"], br["D_hi"], r_continuity, r_separation)}


# ---------------------------------------------------------------- CONTROL-ONLY guard variants
def naive_derivative_settled(delta: np.ndarray, t_stop: int) -> bool:
    """CONTROL T5. The guard everyone writes first: 'the derivative has gone quiet, so the response is over.'

    Evaluated in the plateau BEFORE the declared delay horizon, it declares a half-heard response finished."""
    seg = delta[max(t_stop - 30, 0):t_stop]
    return float(np.max(np.abs(np.diff(seg)))) < 1.0


def v00_guard_in_flight(z: np.ndarray, tail: int = 40, block: int = 40,
                        z_abs: float = 3.0, frac: float = 0.05) -> bool:
    """CONTROL T10. Version 00's guard, restored verbatim: a row is 'still moving' if its tail block mean differs
    from the previous block's by more than max(3 noise units, 5% of its own peak). It abstains on slow tails whose
    remainder cannot possibly matter -- which is precisely how it died."""
    peak = float(np.max(np.abs(z)))
    if peak < F0.Z_DET:
        return False
    t = float(np.mean(z[-tail:]))
    p = float(np.mean(z[-(tail + block):-tail]))
    return abs(t - p) > max(z_abs, frac * peak)
