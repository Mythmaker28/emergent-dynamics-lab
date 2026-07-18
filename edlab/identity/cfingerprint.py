"""THE CONTINUOUS-OBSERVABLE CAUSAL RESPONSE FINGERPRINT. A fixed coordinate system, not an observer.

    A measurement coordinate system must not adapt to the entity being compared.

This is NOT a patch to the Boolean fingerprint. It inherits none of its qualification. `EXP-GT-FINGERPRINT-00`
passed prospectively for BINARY observables; on a continuous float of order 1e-3 that instrument is not merely
inaccurate, it is UNDEFINED (D-073). Cast to uint8 and every system collapses to zero. Compare by exact float
inequality and every system differs from its own later self. This file supplies the things that were missing --
a continuous response representation, a noise model, a tolerance, a normalization, a metric -- and those are not
adapters. They are the definition of a new instrument, and it must earn its own PASS from scratch.

STRUCTURAL SEPARATION FROM GROUND TRUTH. This module never imports the substrate's systems or its evaluator. It
receives a MEASUREMENT CALLABLE and nothing else. It cannot read a spec, a topology, a hidden state or a label,
because it is never handed one. That is not a promise; it is the type signature.

---------------------------------------------------------------------------------------------------------------
THE ONE IDEA. STANDARDIZE BY THE NOISE, NOT BY THE SIGNAL.

    u -> a*u + b   rescales the response AND the noise by the same a.       (a change of UNITS)
    gain -> 2*gain rescales the response and LEAVES THE NOISE ALONE.        (a change of the WORLD)

So z(t) = (deviation) / (measured noise scale) is EXACTLY invariant to the first and EXACTLY sensitive to the
second. Every other choice I tried fails one of those two:

    * normalize by the response's own RMS -> unit-invariant, but GAIN VANISHES.        (control L7: false SAMENESS)
    * do not normalize at all              -> gain survives, but a change of units is a DIFFERENCE. (false DIFFERENCE)
    * exact float inequality               -> everything differs from itself.          (control L1: false DIFFERENCE)
    * cast to a small integer type         -> everything is identical to everything.   (control L2: false SAMENESS)

AND THE PRICE, STATED PLAINLY. If the noise scale is ALSO free, there is no scale left to calibrate against, and
absolute gain becomes UNIDENTIFIABLE -- a halved noise floor and a doubled gain are then literally the same
observation. That is a theorem about the nuisance group, not a bug. The noise scale is therefore DECLARED, not
inferred: `compare()` REFUSES a pair that is not declared to sit on a common noise channel. Control L8 removes the
refusal and the false difference walks straight in.
---------------------------------------------------------------------------------------------------------------

WHAT MAY ENTER THE FINGERPRINT
    noise-standardized, probe-onset-aligned, time-resolved deviation of the DECLARED OBSERVABLE
    the SIGNED deviation -- so, unlike the Boolean XOR-deviation, it is NOT blind to output inversion
    persistence: does a TRANSIENT probe leave a PERMANENT mark, judged only once the response has SETTLED
    coverage, responsiveness, baseline stability -- recorded explicitly, never silently

WHAT MAY NOT
    topology labels; hidden state; implementation identity; parameter values; system class; solver settings;
    tracker ids; anything the privileged evaluator knows. Control L5 puts a label back in and the false
    difference reappears -- which is the only reason to believe the exclusion was doing any work.

ALIGNMENT. Rows are aligned to the PROBE ONSET -- the time WE applied the probe, which we know because we applied
it. Not to the response onset. The Boolean instrument aligned to the RESPONSE onset to stop an unknown internal
latency leaking into its distance; here latency is part of the ACCESSIBLE FUNCTION and must survive into the
representation, and aligning to an exogenous landmark keeps it there without leaking anything. Every window is
therefore the same length for every system, and the Boolean instrument's padding hazard cannot arise.

THE PHASE QUOTIENT. A global carrier shift CYCLICALLY PERMUTES the phase rows. The Boolean instrument quotiented
by SORTING the rows -- exact for discrete symbols. For CONTINUOUS rows a canonical ordering is DISCONTINUOUS: two
nearly-equal rows swap under noise and the representation jumps. So the quotient is taken by MINIMIZING OVER THE
GROUP instead, with ONE shift for the whole fingerprint (a per-probe shift would be extra freedom the nuisance
does not have). Control L6 restores the lexicographic sort and the false difference reappears.

THE FINGERPRINT NEVER SAYS SAME.
"""

from __future__ import annotations

import numpy as np

from ..substrates.ctrans.engine import DRIVE, SUPPLY, INTERNAL, Probe

# ================================================================ FROZEN CONSTANTS (identical for every system)
T_OBS = 304            # every episode is exactly this long, for every system, in both arms
T_PROBE = 128          # nominal probe onset; the phase offset is added to it
W_PRE = 96             # the PRE-PROBE segment. Before the onset the probe episode and its baseline are identical
                       # by construction, so their difference there is PURE NOISE + DRIFT and nothing else. That
                       # is what makes a label-free, per-system noise estimate possible at all.
W_RESP = 160           # the response window. It MUST outlast the longest response in development: the slowest
                       # development system settles in 74 samples and the longest prospective one in ~129. A
                       # window shorter than the response records a still-arriving response as a permanent mark --
                       # D-067, arriving from the other end of the trace. Control L3 shortens it on purpose.
PHASES = (0, 3, 6, 9)  # probe at every phase of the carrier (P_CLK=12). These tile the declared cyclic group Z_4.
N_REPEAT = 16          # independent repeats, AVERAGED. Declared, frozen, and identical for every system.
# ---------------------------------------------------------------------------------------------------------------
# CHOSEN ON DEVELOPMENT, AND ONLY AFTER THE SCALE QUOTIENT MADE IT MEAN ANYTHING.
#
# Before the lambda quotient, raising R made the instrument WORSE: the null grew with R because it was dominated
# by (sigma_hat estimator error x signal), and the signal grows as sqrt(R). Measured null at R=4/8/16 under the
# MEAN aggregator: 5.2 / 9.4 / 25.8. More data made the thing blinder, which is exactly the signature of an
# artefact rather than a measurement.
#
# With the estimator error quotiented out, the null is PURE NOISE and R-INVARIANT (3.70 / 4.29 / 4.12) while the
# genuine differences grow as sqrt(R) (21.0 / 29.9 / 42.5 -- ratios 1.42 and 2.02, i.e. exactly sqrt(2) and 2).
# Only then does averaging buy separation instead of buying nothing.
#
# R = 16 clears the PREDECLARED separation radius by 1.72x. R = 8 clears it by only 1.16x, which will not survive
# the 1.2x-1.6x noisier channels reserved for the prospective split. R = 16 it is, and it is frozen here.
# ---------------------------------------------------------------------------------------------------------------
TAIL = 40              # persistence is judged on the last TAIL samples, long after any transient
SETTLE_BLOCK = 40      # the block before the tail, used to ask whether the response is STILL MOVING

Z_DET = 8.0            # a row RESPONDED if max|z| exceeds this. CALIBRATED ON NOISE ONLY, NOT ON LABELS.
# ---------------------------------------------------------------------------------------------------------------
# I first set this to 5.0, reasoning "five sigma". It was wrong, and it was wrong in the most embarrassing possible
# direction: sigma_hat measures the WHITE noise (a MAD/std of FIRST DIFFERENCES, which annihilates drift by
# design), but z's actual excursion over a 160-sample window also contains the SLOW DRIFT. So "5 sigma_hat" is
# only about 3 real standard deviations of the thing it is thresholding.
#
# MEASURED on systems that CANNOT respond (g_out = 0, so every row is pure noise): max|z| per row has mean 3.67,
# median 3.55, MAX 5.25, and 3% of rows exceed 5.0. A SILENT SYSTEM WAS THEREFORE SCORING 1/32 "RESPONSES",
# passing the responsiveness check, and being handed a confident DIFFERENT verdict against a system it cannot even
# hear. Silence was being read as evidence.
#
# 8.0 is 1.5x the largest excursion ever observed on a noise-only row. It is derived from the NOISE-ONLY
# distribution and from nothing else -- no label, no difference pair, was consulted.
# ---------------------------------------------------------------------------------------------------------------
COVERAGE_FLOOR = 0.5   # below this fraction of probes actually applied, no distance verdict may be issued
BASELINE_MAX = 3.0     # rms(detrended pre-probe) / sigma_hat. Above this the baseline is WANDERING, not noisy.
IN_FLIGHT_MAX = 0.25   # if more than this fraction of responding rows are still moving at the window's end, the
                       # window is too short FOR THIS SYSTEM and the instrument must refuse rather than guess.
IN_FLIGHT_Z = 3.0      # absolute floor, in noise units
IN_FLIGHT_FRAC = 0.05  # ...and RELATIVE to the row's own response amplitude.
# ---------------------------------------------------------------------------------------------------------------
# THE IN-FLIGHT TEST MUST SCALE WITH THE RESPONSE, AND MY FIRST VERSION DID NOT.
#
# An absolute threshold of 3 noise units sounds conservative until the response is 500 noise units tall. A system
# with T=16 has fully decayed by the end of the window -- it sits at ~1% of its peak -- but 1% of 500 is 5, so the
# tail was still "moving by more than 3" and the instrument REFUSED a perfectly ordinary system as though its
# response had not finished. It declared D_leak_T16 INDETERMINATE, which is a fabricated abstention: exactly as
# dishonest as a fabricated certainty, and harder to notice because it looks like caution.
#
# A response is IN FLIGHT if it is still moving by a meaningful fraction OF ITSELF. Both bars must be cleared.
# ---------------------------------------------------------------------------------------------------------------

DETREND = "offset"     # "offset" | "linear". Frozen after the development comparison in exp_gt_cfp.py.
REPRESENTATION = "nsrc"    # the frozen response representation: Noise-Standardized Response Curve
PHASE_QUOTIENT = "cyclic"  # "cyclic" (group minimization) | "lexsort" (control L6)
AGGREGATE = "max"      # "max" | "mean" over probe blocks.
SCALE_BAND = 0.042     # +-4.2% == 3 x the MEASURED relative precision of sigma_hat (1.39% over 12 independent
                       # development acquisitions; theory for 3072 independent difference samples says 1.28%).
# ---------------------------------------------------------------------------------------------------------------
# THE INSTRUMENT MUST QUOTIENT BY ITS OWN ESTIMATOR'S UNCERTAINTY, NOT PRETEND THE ESTIMATOR IS EXACT.
#
# z = r / sigma_hat, and sigma_hat is MEASURED, so it carries a relative error eps ~ 1.4%. That error multiplies
# the ENTIRE standardized trace, injecting a term eps * z_signal into every comparison -- INCLUDING a system's
# comparison with ITSELF. With the signal at z ~ 250, a 2% disagreement between two sigma_hats manufactured a null
# distance of ~5 on the large-amplitude probes while the quiet probes sat at 1.8. The null was not noise. It was
# my own estimator, multiplied by the signal, and it grew with the number of repeats because the signal did.
#
# So the comparison minimizes over ONE COMMON SCALE FACTOR lambda, BOUNDED BY THE ESTIMATOR'S OWN CONFIDENCE
# INTERVAL. Inside the band it cancels the estimator error exactly. Outside it, it cannot reach: lambda is clipped
# to [0.958, 1.042] and cannot absorb a doubled gain, an inverted sign, or any other real difference.
#
# THE PRICE, DECLARED: gain differences SMALLER THAN ~4% ARE NOT RESOLVABLE BY THIS INSTRUMENT. That is not a bug
# to be papered over -- it is the direct consequence of the measurement-contract theorem. The unit factor `a` is
# knowable only through the noise floor, so the precision with which a GAIN can be resolved is bounded by the
# precision with which the NOISE can be measured. The bound is reported, not hidden.
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# THIS IS A LOGICAL POINT, NOT A TUNING KNOB, AND I GOT IT WRONG FIRST.
#
#   "INDISTINGUISHABLE UNDER THE REPERTOIRE"  ==  FOR EVERY admissible probe, the responses agree within noise.
#   Its negation                              ==  THERE EXISTS a probe on which they differ.
#
# A FOR-ALL is certified by its WORST case, not by its average. I first aggregated the per-probe block distances
# with a MEAN, copying the Boolean instrument. That mean DILUTES a difference that lives in only a few probes: the
# `supply_cause` pair differs on the two SUPPLY probes and is identical on the six DRIVE probes, so a real
# per-block separation of 21.8 was averaged down to 8.6 by twenty-four blocks of pure noise -- and the weakest
# genuine difference in the whole development set was an artefact of my own aggregator.
#
# The MAX raises the null a little (the largest of 32 noise blocks exceeds their mean). It raises a SPARSE
# difference enormously. That asymmetry is the entire point, and it is why the quantifier, not the convenience,
# decides the statistic.
# ---------------------------------------------------------------------------------------------------------------

INDIST = "INDISTINGUISHABLE_UNDER_REPERTOIRE"
DIFFERENT = "DIFFERENT"
INDETERMINATE = "INDETERMINATE"

# amplitudes: a LADDER, not a single level. A one-amplitude battery is provably blind to saturation.
A_SMALL, A_LARGE, A_SUPPLY = 0.35, 1.80, 1.20
D_HOLD = 24


def battery(arm: str) -> list:
    """THE FIXED PROBE BATTERY. Identical kinds, amplitudes, durations, order and timing for EVERY system.

    The addresses are fixed by the LAYOUT, not by which components a system happens to contain -- a system with a
    memory site must not receive a longer battery than one without, or the battery is an adaptive probe wearing a
    fixed probe's coat. A system that cannot accept a probe does not get a substitute: the probe is MISSING, and
    it is charged to coverage.

    LIMITED arm  -- external fields only: the exogenous drive and the local supply line. This is the analogue of
                    the access a droplet actually permits. It is NOT a droplet arm and must not be called one.
    RICH arm     -- the above PLUS sustained clamps on every internal address. No droplet analogue exists.
    """
    probes = [
        ("drive_step_up_sm", DRIVE, "step", +A_SMALL, D_HOLD),
        ("drive_step_dn_sm", DRIVE, "step", -A_SMALL, D_HOLD),
        ("drive_step_up_lg", DRIVE, "step", +A_LARGE, D_HOLD),
        ("drive_step_dn_lg", DRIVE, "step", -A_LARGE, D_HOLD),
        ("drive_pulse_up", DRIVE, "pulse", +A_LARGE, 1),
        ("drive_pulse_dn", DRIVE, "pulse", -A_LARGE, 1),
        ("supply_step_up", SUPPLY, "step", +A_SUPPLY, D_HOLD),
        ("supply_pulse_up", SUPPLY, "pulse", +A_LARGE, 1),
    ]
    if arm == "rich":
        for s in INTERNAL:
            probes.append(("internal%d_clamp_hi" % s, s, "clamp", +1.0, D_HOLD))
            probes.append(("internal%d_clamp_lo" % s, s, "clamp", -1.0, D_HOLD))
    elif arm != "limited":
        raise ValueError("unknown arm %r (expected 'limited' or 'rich')" % arm)
    return probes


def _diff_sigma(x):
    """The channel's noise scale, from the FIRST DIFFERENCES of the pre-probe segment.

    Differencing annihilates any slow drift, so this estimates the fast part and is NOT inflated into uselessness
    by a wandering baseline -- which matters, because a drifting system must be caught by the BASELINE-STABILITY
    test and not quietly absorbed into a larger sigma_hat that then hides everything else.

    THE PRECISION OF THIS NUMBER IS A LOAD-BEARING QUANTITY, AND I LEARNED THAT THE HARD WAY.

    z = r / sigma_hat. A relative error `eps` in sigma_hat multiplies the WHOLE standardized trace, so it injects a
    term `eps * z_signal` into every comparison -- including the comparison of a system with ITSELF. With the
    signal at z ~ 250, a 5% error in sigma_hat manufactured a null distance of 4.9 on the large-amplitude probes
    while the quiet probes sat at 1.8. The null was not noise. It was my own estimator, multiplied by the signal.

    Two things fixed it, and both are structural rather than cosmetic:
      * INDEPENDENT BASELINE EPISODES per probe (see `acquire`), so the pooled pre-probe samples are actually
        independent instead of all sharing four common baselines;
      * the efficient STANDARD-DEVIATION estimator rather than a MAD, because there are no outliers here to be
        robust against and MAD throws away ~60% of the information for nothing.

    THE RESIDUAL IS AN HONEST LIMIT, NOT A BUG. The unit factor `a` is unknowable except through the noise scale,
    so the precision with which the instrument can resolve a GAIN difference is bounded by the precision of
    sigma_hat. That bound is reported, not hidden.
    """
    d = np.diff(x)
    return float(np.std(d) / np.sqrt(2.0))


def acquire(measure, arm: str, seed0: int, detrend: str = None, quantize_uint8: bool = False,
            n_repeat: int = None, w_resp: int = None) -> dict:
    """Run the fixed battery through the measurement channel. `measure` is a callable and the ONLY thing this
    module is given: it cannot read a spec, a label or a hidden state, because it is never handed one.

        measure(probes, T, seeds) -> (u, ok)     u: (B,T) float, ok: (B,) bool
        a refused probe returns ok=False. It is MISSING. It is NOT a zero response.
    """
    detrend = DETREND if detrend is None else detrend
    W = W_RESP if w_resp is None else w_resp      # control L3 shortens this on purpose
    probes = battery(arm)
    P, K, R = len(probes), len(PHASES), (N_REPEAT if n_repeat is None else n_repeat)

    # ---- build every episode of every repeat as ONE batch: baselines first, then (probe, phase) episodes
    # ONE BASELINE PER PROBE EPISODE, not one per repeat. Sharing four baselines across all thirty-two probes
    # made every pre-probe segment carry the SAME baseline noise, so pooling them added no independent information
    # about the channel and sigma_hat was ~4x less precise than its sample count suggested. See `_diff_sigma`.
    eps, meta = [], []
    for r in range(R):
        for pi, (nm, tgt, kind, amp, hold) in enumerate(probes):
            for ki, ph in enumerate(PHASES):
                eps.append(Probe("base", -1, "none", 0.0, 0, 10 ** 9))
                meta.append(("base", r, pi, ki))
                eps.append(Probe(nm, tgt, kind, amp, hold, T_PROBE + ph))
                meta.append(("probe", r, pi, ki))
    seeds = np.arange(seed0, seed0 + len(eps))
    u, ok = measure(eps, T_OBS, seeds)
    if quantize_uint8:
        # CONTROL L2, APPLIED WHERE THE PREFLIGHT SAID IT BREAKS: at the ADC, on the RAW OBSERVABLE, before any
        # calibrated scaling. The droplet's uptake is a float of order 1e-3; cast it to uint8 and every sample is
        # 0. My first attempt applied the cast to the already-standardized z (which is O(100)) and of course it
        # survived -- a control that breaks the wrong thing tests nothing, and it reported FIRED = False, which is
        # the only reason I found it.
        u = np.nan_to_num(u).astype(np.uint8).astype(float)

    base, rows = {}, {}
    for i, (t, r, pi, ki) in enumerate(meta):
        if t == "base":
            base[(r, pi, ki)] = u[i]
        else:
            rows.setdefault((pi, ki), {})[r] = (u[i], ok[i])

    # ---- deviation traces, averaged over the declared repeats
    Z = np.full((P, K, W), np.nan)
    missing = np.zeros((P, K), dtype=bool)
    pre_pool, flags = [], {}
    raw = {}
    for pi in range(P):
        for ki, ph in enumerate(PHASES):
            onset = T_PROBE + ph
            lo, hi = onset - W_PRE, onset + W
            got = rows[(pi, ki)]
            if not all(got[r][1] for r in range(R)):
                missing[pi, ki] = True                    # the probe did not happen. MISSING, never zero.
                continue
            # r(t) = u_probe(t) - u_base(t). Before the onset both episodes are IDENTICAL deterministically, so the
            # pre-probe segment of r is pure noise + drift -- regardless of transients, regardless of the system.
            dev = np.mean([got[r][0][lo:hi] - base[(r, pi, ki)][lo:hi] for r in range(R)], axis=0)
            raw[(pi, ki)] = dev
            pre_pool.append(dev[:W_PRE])

    if not pre_pool:
        return {"Z": Z, "missing": missing, "coverage": 0.0, "responsive": 0.0, "arm": arm,
                "sigma_hat": float("nan"), "baseline_stability": float("nan"), "in_flight_frac": 0.0,
                "n_responded": 0, "probes": [p[0] for p in probes], "persistence": []}

    # ---- sigma_hat: ONE number, POOLED over every pre-probe segment. The noise scale is a property of the
    #      CHANNEL, not of the probe, and estimating it per-row would inject a few percent of estimator noise
    #      into every single block for no reason.
    sigma_hat = _diff_sigma(np.concatenate([p for p in pre_pool]))
    if not np.isfinite(sigma_hat) or sigma_hat <= 0:
        sigma_hat = float(np.std(np.concatenate(pre_pool))) or 1e-300

    # ---- detrend, standardize
    resid_pre = []
    n_resp, n_flight, pers = 0, 0, []
    for (pi, ki), dev in raw.items():
        idx = np.arange(len(dev), dtype=float)
        pre = dev[:W_PRE]
        if detrend == "linear":
            c = np.polyfit(idx[:W_PRE], pre, 1)
            trend = np.polyval(c, idx)
        else:
            trend = np.full_like(dev, np.median(pre))
        d = dev - trend
        resid_pre.append(d[:W_PRE])
        z = d[W_PRE:] / sigma_hat
        Z[pi, ki] = z
        peak = float(np.nanmax(np.abs(z)))
        responded = peak >= Z_DET
        n_resp += int(responded)
        if responded:
            tail = float(np.mean(z[-TAIL:]))
            prev = float(np.mean(z[-(TAIL + SETTLE_BLOCK):-TAIL]))
            in_flight = abs(tail - prev) > max(IN_FLIGHT_Z, IN_FLIGHT_FRAC * peak)
            n_flight += int(in_flight)
            # PERSISTENCE is only claimed once the response has SETTLED. A response still moving at the end of the
            # window is IN FLIGHT, and calling it a permanent mark is the error this whole programme keeps making.
            pers.append(int((not in_flight) and abs(tail) >= Z_DET))

    n_slots = P * K
    n_valid = int((~missing).sum())
    baseline_stability = float(np.sqrt(np.mean(np.concatenate(resid_pre) ** 2)) / sigma_hat)
    return {"Z": Z, "missing": missing, "arm": arm, "sigma_hat": sigma_hat,
            "coverage": n_valid / n_slots,
            # RESPONSIVENESS IS NOT COVERAGE. Every probe may land and the system may still say nothing. An
            # all-zero fingerprint would silently match every other silent system, and that is not an identity --
            # it is an absence of evidence, and it is reported as one.
            "responsive": n_resp / max(n_valid, 1), "n_responded": n_resp,
            "baseline_stability": baseline_stability,
            "in_flight_frac": n_flight / max(n_resp, 1),
            "persistence": pers, "probes": [p[0] for p in probes]}


# ================================================================ the metric
def _block_rms(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def distance(A: dict, B: dict, representation: str = None, phase_quotient: str = None,
             aggregate: str = None, scale_band: float = None, contaminant=None) -> float:
    """The mean, over PROBE-PHASE BLOCKS, of each block's noise-standardized RMS difference, MINIMIZED over the
    declared cyclic phase group with ONE shift for the whole fingerprint.

    Per-block, so that no probe dominates by producing more samples than another. One shift, because a global
    carrier offset is ONE shift -- allowing a different shift per probe would hand the nuisance freedom the
    nuisance does not have, and would let genuinely different systems align themselves into agreement.
    """
    representation = REPRESENTATION if representation is None else representation
    phase_quotient = PHASE_QUOTIENT if phase_quotient is None else phase_quotient
    aggregate = AGGREGATE if aggregate is None else aggregate
    band = SCALE_BAND if scale_band is None else scale_band
    agg = (lambda v: float(np.max(v))) if aggregate == "max" else (lambda v: float(np.mean(v)))

    def _lam(pairs):
        """The single best common scale, CLIPPED to the estimator's confidence band. One lambda for the whole
        fingerprint -- a per-block lambda would be freedom the nuisance does not have and would let genuinely
        different systems rescale themselves into agreement, one probe at a time."""
        if band <= 0 or not pairs:
            return 1.0
        num = sum(float(np.dot(a, b)) for a, b in pairs)
        den = sum(float(np.dot(b, b)) for a, b in pairs)
        lam = num / den if den > 0 else 1.0
        return float(np.clip(lam, 1.0 - band, 1.0 + band))
    ZA, ZB = A["Z"], B["Z"]
    P, K, _W = ZA.shape
    valid = (~A["missing"]) & (~B["missing"])       # a block missing on EITHER side is not compared. Never zeroed.

    def prep(Z, i, k):
        z = Z[i, k]
        if representation == "nsrc":
            return z
        if representation == "resp_rms":
            # CONTROL L7. Normalize by the response's OWN amplitude instead of the noise. Unit-invariant, and
            # blind to gain: a system twice as loud becomes literally the same vector.
            s = np.sqrt(np.mean(z ** 2))
            return z / (s if s > 0 else 1.0)
        if representation == "ncc":
            z = z - z.mean()
            s = np.linalg.norm(z)
            return z / (s if s > 0 else 1.0)
        raise ValueError("unknown representation %r" % representation)

    if phase_quotient == "lexsort":
        # CONTROL L6. Canonicalize the phase rows by SORTING them, as the Boolean instrument did. Exact for
        # discrete symbols; DISCONTINUOUS for continuous ones -- two nearly-equal rows swap order under noise and
        # the representation jumps.
        ds = []
        for i in range(P):
            ka = sorted([tuple(prep(ZA, i, k)) for k in range(K) if valid[i, k]])
            kb = sorted([tuple(prep(ZB, i, k)) for k in range(K) if valid[i, k]])
            pr = [(np.array(ra), np.array(rb)) for ra, rb in zip(ka, kb)]
            lam = _lam(pr)
            for ra, rb in pr:
                ds.append(_block_rms(ra, lam * rb))
        d = agg(ds) if ds else float("nan")
    else:
        best = np.inf
        for s in range(K):
            pr = [(prep(ZA, i, k), prep(ZB, i, (k + s) % K))
                  for i in range(P) for k in range(K) if valid[i, k] and valid[i, (k + s) % K]]
            if pr:
                lam = _lam(pr)
                best = min(best, agg([_block_rms(a, lam * b) for a, b in pr]))
        d = best

    if contaminant is not None:
        # CONTROL L5. Append a FORBIDDEN descriptive coordinate -- a topology label, an implementation id -- as one
        # more block, weighted like any other. If the exclusion of description is doing real work, this must
        # manufacture a difference between systems whose every measured response is identical.
        ca, cb = contaminant
        d = float(np.mean([d, 0.0 if ca == cb else 100.0]))
    return d


def exact_float_distance(A: dict, B: dict) -> float:
    """CONTROL L1. Exact float inequality as the causal metric -- the fraction of samples that differ AT ALL.

    This is the second of the two naive mappings the preflight identified. It calls a system different from its own
    re-measurement, because two floats drawn from the same distribution are never bitwise equal."""
    ZA, ZB = A["Z"], B["Z"]
    valid = (~A["missing"]) & (~B["missing"])
    ds = [float((ZA[i, k] != ZB[i, k]).mean()) for i in range(ZA.shape[0]) for k in range(ZA.shape[1])
          if valid[i, k]]
    return float(np.mean(ds)) if ds else float("nan")


# ================================================================ admission + verdict. It never says SAME.
def admit(A: dict, B: dict, common_channel: bool, enforce_channel: bool = True) -> dict:
    """A verdict on a case the instrument cannot resolve is a FABRICATED CERTAINTY. Admission comes first."""
    cov = min(A["coverage"], B["coverage"])
    if not np.array_equal(A["missing"], B["missing"]):
        # INSUFFICIENT_INTERVENTION_ACCESS. The two systems did not receive the same battery: some probe landed on
        # one and not the other. The metric would silently fall back to the INTERSECTION of their batteries -- a
        # battery NEITHER system actually received -- and hand back a confident number computed on a repertoire
        # that never existed. That is an adaptive battery wearing a fixed battery's coat, and it is refused.
        return {"ok": False, "coverage": cov,
                "why": "the two systems do not admit the same interventions (%d vs %d probes refused). There is no "
                       "common repertoire on which a comparison is even defined."
                       % (int(A["missing"].sum()), int(B["missing"].sum()))}
    if enforce_channel and not common_channel:
        return {"ok": False, "why": "the two systems are NOT declared to sit on a common noise channel. Absolute "
                                    "gain is not identifiable when both the readout scale and the noise scale are "
                                    "free: a quieter channel and a louder system are the same observation. "
                                    "REFUSED rather than guessed.", "coverage": cov}
    if cov < COVERAGE_FLOOR:
        return {"ok": False, "why": "probe coverage %.2f is below the frozen floor %.2f. Some probes could not be "
                                    "applied at all; deciding on the ones that happened to land would be deciding "
                                    "on a battery neither system received." % (cov, COVERAGE_FLOOR),
                "coverage": cov}
    for tag, S in (("left", A), ("right", B)):
        if S["responsive"] == 0.0:
            return {"ok": False, "why": "the %s system answered NOTHING to every probe in this battery. Silence is "
                                        "not a fingerprint, and two silent systems are not the same system." % tag,
                    "coverage": cov}
        if S["baseline_stability"] > BASELINE_MAX:
            return {"ok": False, "why": "the %s system's baseline WANDERS (%.1f x its own white-noise scale, floor "
                                        "%.1f). It is nonstationary, which is outside the declared contract."
                                        % (tag, S["baseline_stability"], BASELINE_MAX), "coverage": cov}
        if S["in_flight_frac"] > IN_FLIGHT_MAX:
            return {"ok": False, "why": "%.0f%% of the %s system's responses are STILL MOVING when the window ends. "
                                        "The window is shorter than the response, and an in-flight response is not "
                                        "a permanent mark." % (100 * S["in_flight_frac"], tag), "coverage": cov}
    return {"ok": True, "why": "admitted", "coverage": cov}


def compare(A: dict, B: dict, r_continuity: float, r_separation: float, common_channel: bool = True,
            enforce_channel: bool = True, **kw) -> dict:
    """INDISTINGUISHABLE_UNDER_REPERTOIRE / DIFFERENT / INDETERMINATE.

    THERE IS NO SAME. Two systems that no admissible probe can separate form an EQUIVALENCE CLASS; calling them
    one individual is an assertion the measurement does not license, and this programme exists because that
    assertion is easy to make and hard to retract.
    """
    a = admit(A, B, common_channel, enforce_channel)
    d = distance(A, B, **kw)
    if not a["ok"]:
        return {"verdict": INDETERMINATE, "distance": d, "coverage": a["coverage"], "admitted": False,
                "why": a["why"]}
    if d <= r_continuity:
        return {"verdict": INDIST, "distance": d, "coverage": a["coverage"], "admitted": True,
                "equivalence_class_only": True,
                "why": "no admissible probe in this battery separated them. This is an EQUIVALENCE CLASS RELATIVE "
                       "TO THIS REPERTOIRE, not an identity, and not a claim that they are the same system."}
    if d >= r_separation:
        return {"verdict": DIFFERENT, "distance": d, "coverage": a["coverage"], "admitted": True,
                "why": "at least one probe response differs by more than the calibrated separation radius"}
    return {"verdict": INDETERMINATE, "distance": d, "coverage": a["coverage"], "admitted": True,
            "why": "distance %.4f lies between the frozen continuity radius %.4f and the separation radius %.4f"
                   % (d, r_continuity, r_separation)}
