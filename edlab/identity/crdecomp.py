"""FACTORIZED CAUSAL RESPONSE DECOMPOSITION — EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00.

    The old scalar was  D_W = sqrt( (1/W) * integral |delta_r|^2 ).
    The 1/W is the bug. It sends every finite transient to zero as the window grows, while a persistent
    difference is untouched. One number was being asked to carry two quantities of different kind.

THE OUTPUT IS A PROFILE AND IT STAYS A PROFILE:

    R(x,y) = ( E_trans , P_inf , A_peak , L_onset , T_recovery , C , U )

THERE IS NO COMPOSITE. No w1*E + w2*P + ... , no learned weighting, no Pareto rank, no hidden scalar ordering.
Each axis carries its own estimator, its own uncertainty and its own falsifier, and each may independently return
ESTIMATED / LOWER_BOUND_ONLY / INDETERMINATE / OUT_OF_SCOPE. A PARTIAL PROFILE IS A VALID RESULT.

THERE IS STILL NO SAME. A limited-access collision returns EQUIVALENCE_CLASS_ONLY.

THE TWO REPAIRS THAT MATTER:

1. E_trans IS AN INTEGRAL, NOT A MEAN.  sum_t (delta_r - P_inf)^2.  It does not dilute; it CONVERGES. Extending
   the window can only add to it, so its window verdict is honest: ESTIMATED once the transient has died inside the
   window, LOWER_BOUND_ONLY while it has not.

2. THE PERSISTENT PART IS SUBTRACTED BEFORE THE ENERGY IS TAKEN. Without that subtraction the energy of a
   persistent difference DIVERGES linearly with the window, which is not a fact about the systems -- it is the same
   confusion the old scalar made, wearing the opposite sign.

NOISE AND DRIFT ARE DEBIASED FROM A MATCHED SHAM CHANNEL -- baseline episodes with identical duration, timing,
horizon, sampling and noise/drift generator, differing ONLY in the absence of intervention amplitude. Drift is
never estimated by fitting away the active tail, because the active tail is the thing being measured.
"""

from __future__ import annotations

import math

import numpy as np

from . import cfingerprint as F0
from ..substrates.ctrans.engine import Probe

W_FIXED = 480          # contains every declared in-contract transient (the broadest settles by ~242)
W_LATE = 120           # the late window on which the persistent component is estimated
K_SIG = 1.5            # detection multiplier -- but NOT in units of a white-noise sigma. See below.
# ---------------------------------------------------------------------------------------------------------------
# EVERY BAND IS SET BY WHAT THE SHAM CHANNEL ITSELF EVER DOES, AND MY FIRST VERSION GOT THIS BADLY WRONG.
#
# I estimated the noise on the late-window MEAN as std(sham)/sqrt(W_LATE). That assumes the samples are
# INDEPENDENT. They are not: the slow drift is correlated, so the mean wanders far more than sqrt(n) predicts.
# MEASURED on pairs that CANNOT have a persistent difference -- a system against ITSELF -- |P_hat| reached 29.7
# of those fake "sigmas" on the null and 104 on the drifting system. The instrument would have reported a
# confident PERSISTENT CAUSAL DIFFERENCE between a system and itself, which is precisely how drift gets promoted
# to physics.
#
# So no band is derived from a white-noise sigma. Each is taken from the EMPIRICAL DISTRIBUTION OF THE MATCHED
# SHAM ACROSS BLOCKS -- same duration, timing, horizon, sampling and noise/drift generator, differing ONLY in the
# absence of intervention amplitude:
#
#     A_noise = max over blocks of  max|sham|                 (the biggest excursion the sham EVER makes)
#     P_noise = max over blocks of |mean(sham, late window)|  (the biggest late level the sham EVER reaches)
#     E_noise = max over blocks of  sum(sham^2)               (the energy of pure nothing)
#
# A causal component must EXCEED WHAT NOTHING-AT-ALL PRODUCES, by the margin K_SIG. That is the whole rule, it
# needs no distributional assumption, and it is drift-aware by construction because the drift is IN the sham.
# ---------------------------------------------------------------------------------------------------------------
DWELL = 12             # a band crossing must be held this long. One noisy sample is not an onset, nor a recovery.
R_NULL_E = 25.0        # ENERGY RATIO E_raw/E_sham below which there is NO causal transient. CALIBRATED ON PAIRS
                       # THAT CANNOT CONTAIN ONE (a system against itself): null max 3.83, silent 2.46, and the
                       # heavily DRIFTING system 20.13. Pooled max 20.13; frozen at 1.25x = 25.0. No label used.
                       # For contrast, the ratios of pairs that DO contain a transient: 2574 (pure transient),
                       # 272 (slow response, no drift), 96 (slow response under HEAVY drift). The separation is
                       # real, and it is what lets drift and a slow causal response be told apart at all.
R_AMB_A = 3.0          # PEAK: below 1.5x the sham's own worst excursion there is nothing; between 1.5x and 3x the
                       # drift and the response cannot be told apart and the axis returns INDETERMINATE rather
                       # than reporting a drift excursion as a causal peak.

ESTIMATED = "ESTIMATED"
LOWER_BOUND_ONLY = "LOWER_BOUND_ONLY"
UPPER_BOUND_ONLY = "UPPER_BOUND_ONLY"
INDETERMINATE = "INDETERMINATE"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
EQUIVALENCE_CLASS_ONLY = "EQUIVALENCE_CLASS_ONLY"
AXES = ("E_trans", "P_inf", "A_peak", "L_onset", "T_recovery")


def episode_len(W):
    return F0.T_PROBE + max(F0.PHASES) + W + 8


# ================================================================ acquisition (active + matched sham)
def acquire(measure, arm: str, seed0: int, W: int = W_FIXED, quantize_uint8: bool = False,
            no_sham: bool = False) -> dict:
    T = episode_len(W)
    R = F0.N_REPEAT
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
        u = np.nan_to_num(u).astype(np.uint8).astype(float)
    B, Pr = {}, {}
    for i, (t, r, pi, ki) in enumerate(meta):
        if t == "base":
            B[(r, pi, ki)] = u[i]
        else:
            Pr.setdefault((pi, ki), {})[r] = (u[i], ok[i])
    Z = np.full((P, K, W), np.nan)
    ZS = np.full((P, K, W), np.nan)
    miss = np.zeros((P, K), dtype=bool)
    raw, sham, pre = {}, {}, []
    h = R // 2
    for pi in range(P):
        for ki, ph in enumerate(F0.PHASES):
            on = F0.T_PROBE + ph
            g = Pr[(pi, ki)]
            if not all(g[r][1] for r in range(R)):
                miss[pi, ki] = True
                continue
            sl = slice(on - F0.W_PRE, on + W)
            raw[(pi, ki)] = np.mean([g[r][0][sl] - B[(r, pi, ki)][sl] for r in range(R)], axis=0)
            sham[(pi, ki)] = (np.mean([B[(r, pi, ki)][sl] for r in range(h)], axis=0)
                              - np.mean([B[(r, pi, ki)][sl] for r in range(h, R)], axis=0)) / math.sqrt(2.0)
            pre.append(raw[(pi, ki)][:F0.W_PRE])
    if not pre:
        return {"Z": Z, "Z_sham": ZS, "missing": miss, "coverage": 0.0, "responsive": 0.0, "arm": arm, "W": W,
                "sigma_hat": float("nan"), "baseline_stability": float("nan")}
    sh = F0._diff_sigma(np.concatenate(pre))
    if not np.isfinite(sh) or sh <= 0:
        sh = float(np.std(np.concatenate(pre))) or 1e-300
    resid, nr = [], 0
    for (pi, ki), d in raw.items():
        dd = d - np.median(d[:F0.W_PRE])
        resid.append(dd[:F0.W_PRE])
        Z[pi, ki] = dd[F0.W_PRE:] / sh
        s = sham[(pi, ki)]
        ZS[pi, ki] = (0.0 * s[F0.W_PRE:] if no_sham                      # MUST-FAIL: sham correction removed
                      else (s - np.median(s[:F0.W_PRE]))[F0.W_PRE:] / sh)
        nr += int(float(np.nanmax(np.abs(Z[pi, ki]))) >= F0.Z_DET)
    nv = int((~miss).sum())
    return {"Z": Z, "Z_sham": ZS, "missing": miss, "arm": arm, "W": W, "sigma_hat": sh,
            "coverage": nv / (P * K), "responsive": nr / max(nv, 1), "n_responded": nr,
            "baseline_stability": float(np.sqrt(np.mean(np.concatenate(resid) ** 2)) / sh)}


# ================================================================ the decomposition
def _lam(A, B, W):
    ZA, ZB = A["Z"][:, :, :W], B["Z"][:, :, :W]
    K = ZA.shape[1]
    valid = (~A["missing"]) & (~B["missing"])
    band = F0.SCALE_BAND
    best = (math.inf, 0, 1.0)
    for s in range(K):
        pr = [(ZA[i, k], ZB[i, (k + s) % K]) for i in range(ZA.shape[0]) for k in range(K)
              if valid[i, k] and valid[i, (k + s) % K]]
        if not pr:
            continue
        num = sum(float(np.dot(a, b)) for a, b in pr)
        den = sum(float(np.dot(b, b)) for a, b in pr)
        lam = float(np.clip(num / den, 1 - band, 1 + band)) if (band > 0 and den > 0) else 1.0
        d = max(float(np.sqrt(np.mean((a - lam * b) ** 2))) for a, b in pr)
        if d < best[0]:
            best = (d, s, lam)
    return best[1], best[2]


def _block_profile(dr, ds, W, bands, subtract_persistent=True, persist_last_sample_only=False):
    """The profile of ONE probe block. `dr` is the causal difference; `ds` is its MATCHED SHAM (no intervention).
    `bands` are the pair-level thresholds taken from the sham's own empirical distribution across blocks."""
    late = slice(W - W_LATE, W)
    A_band = K_SIG * bands["A_noise"]
    P_band = K_SIG * bands["P_noise"]
    sig = A_band                                   # the amplitude band; NOT a white-noise sigma
    sem = P_band / K_SIG

    # ---- P_inf. NOT a final sample: a mean over a declared late window, with a STABILITY CHECK between halves.
    if persist_last_sample_only:
        Ph, P_stat = float(dr[-1]), ESTIMATED          # MUST-FAIL control: a single final sample
    else:
        Ph = float(dr[late].mean())
        h1 = float(dr[W - W_LATE:W - W_LATE // 2].mean())
        h2 = float(dr[W - W_LATE // 2:].mean())
        P_stat = INDETERMINATE if abs(h1 - h2) > 2.0 * P_band else ESTIMATED
    P = Ph if abs(Ph) > P_band else 0.0
    Pu = P_band

    # ---- E_trans. AN INTEGRAL. Persistent part removed FIRST, then the sham's own energy debited.
    base = (dr - P) if subtract_persistent else dr
    E_raw = float((base ** 2).sum())
    E_sham = float((ds ** 2).sum())
    ratio = E_raw / max(E_sham, 1e-9)
    if ratio <= R_NULL_E:
        # nothing here that pure drift does not already produce. Reporting an energy would be reporting the drift.
        E, E_stat, Eu = 0.0, ESTIMATED, E_sham
    else:
        E = max(E_raw - E_sham, 0.0)                 # PER-BLOCK debit: this block's own sham, not a global max
        Eu = E_sham
        tail_live = float(np.abs(base[-DWELL:]).max()) > A_band
        E_stat = LOWER_BOUND_ONLY if tail_live else ESTIMATED
        # THE DEBIT IS UNBIASED, NOT EXACT. dr's drift and ds's drift are INDEPENDENT realizations of the same
        # process, so (E_raw - E_sham) carries an error of order E_sham. When that error is comparable to the
        # answer, the answer is not an answer: the drift and the causal energy cannot be separated, and the axis
        # says so instead of quoting a number it cannot defend.
        if E_sham > 0.5 * E:
            E_stat = INDETERMINATE

    # ---- A_peak. sup |dr|, against the sham's OWN maximum excursion.
    A = float(np.abs(dr).max())
    a_ratio = A / max(bands["A_noise"], 1e-9)
    if A <= A_band:
        A, A_stat = 0.0, ESTIMATED                   # below what nothing-at-all produces
    elif a_ratio <= R_AMB_A:
        A_stat = INDETERMINATE                       # drift and response are not separable here. Say so.
    else:
        A_stat = ESTIMATED

    # ---- L_onset. First crossing HELD for DWELL samples. One noisy sample is not an onset.
    over = np.abs(dr) > A_band
    L, L_stat = None, INDETERMINATE
    run = 0
    for t in range(W):
        run = run + 1 if over[t] else 0
        if run >= DWELL:
            L, L_stat = t - DWELL + 1, ESTIMATED
            break

    # ---- T_recovery. Return to the band about P, HELD for DWELL. Never a single sample.
    T, T_stat = None, INDETERMINATE
    if L is not None:
        pk = int(np.argmax(np.abs(dr)))
        inb = np.abs(dr - P) <= A_band
        run = 0
        for t in range(pk, W):
            run = run + 1 if inb[t] else 0
            if run >= DWELL:
                T, T_stat = t - DWELL + 1 - L, ESTIMATED
                break
        if T is None:
            T, T_stat = W - L, LOWER_BOUND_ONLY
    return {"E_trans": E, "E_stat": E_stat, "E_unc": Eu,
            "P_inf": P, "P_stat": P_stat, "P_unc": Pu,
            "A_peak": A, "A_stat": A_stat, "A_unc": A_band,
            "L_onset": L, "L_stat": L_stat, "T_recovery": T, "T_stat": T_stat}


def profile(A, B, W=None, **kw):
    """The FACTORIZED profile of a pair. Aggregated across probe blocks with the FOR-ALL logic (worst case)."""
    W = (A["W"] if W is None else W)
    s, lam = _lam(A, B, W)
    ZA, ZB, SA, SB = A["Z"], B["Z"], A["Z_sham"], B["Z_sham"]
    K = ZA.shape[1]
    valid = (~A["missing"]) & (~B["missing"])
    # ---- the SHAM BANDS: what a channel with no intervention in it ever manages to produce.
    pairs = []
    for i in range(ZA.shape[0]):
        for k in range(K):
            k2 = (k + s) % K
            if not (valid[i, k] and valid[i, k2]):
                continue
            pairs.append((ZA[i, k][:W] - lam * ZB[i, k2][:W], SA[i, k][:W] - lam * SB[i, k2][:W]))
    if not pairs:
        return {"coverage": 0.0, "n_blocks": 0}
    late = slice(W - W_LATE, W)
    bands = {"A_noise": max(float(np.abs(ds).max()) for _, ds in pairs),
             "P_noise": max(abs(float(ds[late].mean())) for _, ds in pairs),
             "E_noise": max(float((ds ** 2).sum()) for _, ds in pairs)}
    blocks = [_block_profile(dr, ds, W, bands, **kw) for dr, ds in pairs]
    # ------------------------------------------------------------------------------------------------------
    # PHASES ARE REPLICATES. PROBES ARE DISTINCT INTERVENTIONS. THE AGGREGATION MUST KNOW THE DIFFERENCE.
    #
    # I first aggregated every axis with a MAX over all 32 blocks -- the FOR-ALL logic inherited from the old
    # fingerprint. That is right for a VERDICT ("is there ANY probe on which they differ?") and WRONG for an
    # ESTIMATE ("how much?"). A max over 32 blocks is a maximum-of-noise selector: it picks the block where the
    # independent drift realizations in the causal trace and in its sham happened to conspire, and reports that
    # conspiracy as the answer. Measured: the transient energy of a slow response under heavy drift came out 7.7x
    # its privileged truth, and a drift excursion was quoted as a causal peak.
    #
    # The four carrier phases are REPLICATES of the same intervention, so they are combined with a MEDIAN -- which
    # is what kills the conspiracy. The eight probes are DIFFERENT interventions, so they are still combined with a
    # MAX, because "indistinguishable under the repertoire" remains a FOR-ALL over the repertoire.
    # ------------------------------------------------------------------------------------------------------
    nph = len(F0.PHASES)
    groups = [blocks[i:i + nph] for i in range(0, len(blocks), nph)] if len(blocks) % nph == 0 else [blocks]
    med = []
    for g in groups:
        m = {}
        for k in ("E_trans", "P_inf", "A_peak", "E_unc", "P_unc", "A_unc"):
            m[k] = float(np.median([b[k] for b in g]))
        for k in ("E_stat", "P_stat", "A_stat"):
            vals = [b[k] for b in g]
            m[k] = (INDETERMINATE if vals.count(INDETERMINATE) * 2 >= len(vals)
                    else (LOWER_BOUND_ONLY if LOWER_BOUND_ONLY in vals else ESTIMATED))
        for k in ("L_onset", "T_recovery"):
            v = [b[k] for b in g if b[k] is not None]
            m[k] = float(np.median(v)) if v else None
        for k in ("L_stat", "T_stat"):
            m[k] = ESTIMATED if any(b[k] == ESTIMATED for b in g) else INDETERMINATE
        med.append(m)
    blocks = med
    # THE VALUE AND ITS STATUS MUST COME FROM THE SAME BLOCK, AND MY FIRST VERSION LET THEM DIVERGE.
    # `max` picked the value from the loudest block while `worst` picked the status from a quorum of all of them,
    # so a DRIFT-CONTAMINATED block could donate a confident-looking peak of 427 while an untouched block donated
    # the word ESTIMATED. The instrument then reported a drift excursion as a causal peak -- which is exactly the
    # thing this programme exists to refuse. An axis now speaks with ONE block's voice: the one that carries it.
    def pick(key, stat_key):
        b = max(blocks, key=lambda x: abs(x[key]) if x[key] is not None else -1)
        return b[key], b[stat_key], b.get(key.split("_")[0][0] + "_unc", 0.0)
    worst = lambda key: (LOWER_BOUND_ONLY if any(b[key] == LOWER_BOUND_ONLY for b in blocks)
                         else (INDETERMINATE if all(b[key] == INDETERMINATE for b in blocks) else ESTIMATED))
    Ls = [b["L_onset"] for b in blocks if b["L_onset"] is not None]
    Ts = [b["T_recovery"] for b in blocks if b["T_recovery"] is not None]
    Ev, Es_, Eu = pick("E_trans", "E_stat")
    Av, As_, Au = pick("A_peak", "A_stat")
    Pv, Ps_, Pu = pick("P_inf", "P_stat")
    return {"E_trans": Ev, "E_stat": Es_, "E_unc": Eu,
            "P_inf": Pv, "P_stat": Ps_, "P_unc": Pu,
            "A_peak": Av, "A_stat": As_, "A_unc": Au,
            "L_onset": (min(Ls) if Ls else None),
            "L_stat": (ESTIMATED if Ls else INDETERMINATE),
            "T_recovery": (max(Ts) if Ts else None),
            "T_stat": worst("T_stat") if Ts else INDETERMINATE,
            "coverage": min(A["coverage"], B["coverage"]),
            "responsive": min(A["responsive"], B["responsive"]),
            "n_blocks": len(blocks), "lam": lam, "shift": s}


def admit(A, B, common_channel=True, enforce_channel=True):
    cov = min(A["coverage"], B["coverage"])
    if not np.array_equal(A["missing"], B["missing"]):
        return {"ok": False, "code": "INSUFFICIENT_COVERAGE",
                "why": "the two systems do not admit the same interventions: no common repertoire exists."}
    if enforce_channel and not common_channel:
        return {"ok": False, "code": "CONFOUNDED",
                "why": "not declared to sit on a common noise channel."}
    if cov < F0.COVERAGE_FLOOR:
        return {"ok": False, "code": "INSUFFICIENT_COVERAGE", "why": "coverage %.2f below floor" % cov}
    for tag, S in (("left", A), ("right", B)):
        if S["responsive"] == 0.0:
            return {"ok": False, "code": "INSUFFICIENT_RESPONSIVENESS",
                    "why": "the %s system answered nothing. Silence is not a response profile." % tag}
    # ------------------------------------------------------------------------------------------------------
    # THE INHERITED BASELINE_MAX REFUSAL IS DELIBERATELY *NOT* APPLIED HERE, AND NAMING THAT IS THE POINT.
    #
    # The old fingerprint refused any system whose baseline wandered, because it had no way to tell drift from a
    # slow causal response and abstaining was the only honest move available to it. This programme has a MATCHED
    # SHAM CHANNEL: every band is set by what a channel with NO INTERVENTION IN IT ever manages to produce, so
    # drift is handled ON THE AXES rather than at the door.
    #
    # Importing the old admission wholesale would have re-imposed the old refusal and thrown away the very
    # machinery this instrument exists to test -- which is exactly the mistake v01 made when it inherited v00's
    # dead in-flight guard by importing admission unexamined. Inheriting a core means inheriting its assumptions
    # unless you NAME the one you are replacing. Named.
    #
    # The cost is declared: a drifting system is now ADMITTED and must be defended on-axis. If the sham bands
    # cannot separate drift from response, the axis returns INDETERMINATE -- not a number.
    # ------------------------------------------------------------------------------------------------------
    return {"ok": True, "code": "ADMITTED", "why": "admitted (drift is handled on-axis by the sham bands)",
            "baseline_stability": max(A["baseline_stability"], B["baseline_stability"])}
