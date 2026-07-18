"""THE PRIVILEGED GROUND-TRUTH EVALUATOR. THE SECOND PATH TO TRUTH.

    THIS FILE MUST NEVER IMPORT edlab.identity.cfingerprint. THE WHOLE POINT IS THAT IT CANNOT.

Truth has two paths in this benchmark, and a case is scored only if they agree:

    PATH 1  CONSTRUCTION-DECLARED   -- the label written in manifests.py from the system that was BUILT, committed
                                       before the instrument existed.
    PATH 2  PRIVILEGED EVALUATION   -- this file. It drives the engine directly, noise-free, with a DENSE RANDOM
                                       input ensemble that is NOT the fingerprint's battery, and decides by exact
                                       trace comparison at solver tolerance.

If they disagree, the CASE IS REJECTED BEFORE SCORING. A benchmark whose labels are wrong cannot fail an
instrument; it can only slander one.

WHAT THIS FILE SHARES WITH THE INSTRUMENT, DECLARED HONESTLY AND EXHAUSTIVELY:
    * the DECLARED MEASUREMENT CONTRACT -- the cyclic carrier-shift nuisance, the observation horizon W_EVAL, and
      the DECLARED noise scale sigma. It must. "The window is too short", "the response is under the noise", and
      "these two sit on a common channel" are claims ABOUT A CONTRACT, and you cannot adjudicate them without one.

WHAT IT SHARES WITH THE INSTRUMENT: NOTHING ELSE.
    No probe battery. No sigma-HAT (it uses the DECLARED sigma; the instrument must estimate one). No block
    structure. No detrending. No scale band. No radii. No coverage floor. No max-over-blocks aggregation. No
    verdict rule. It drives 48 RANDOM inputs and compares raw traces; the instrument drives 8 or 16 FIXED probes
    and compares a noise-standardized representation. If they agree, that agreement is evidence. If they shared a
    metric, it would be a tautology.

A CORRECTION THIS FILE HAD TO MAKE TO ITSELF. The residual was originally a FREE GLOBAL AFFINE FIT of B onto A.
That absorbed a doubled gain (a = 2) and an inverted sign (a = -1) as though they were changes of units, and
certified two of the benchmark's flagship DIFFERENCE cases as EQUIVALENT. The two-path check caught it -- which is
exactly what the two-path check is for. See `_contract_residual`. Classified: evaluator / ground-truth failure.
"""

from __future__ import annotations

import numpy as np

from .engine import DRIVE, INTERNAL, P_CLK, Probe, Spec, observe_noise_free, simulate

# ---------------------------------------------------------------- privileged constants (NOT instrument constants)
T_EVAL = 320           # the privileged episode length
W_EVAL = 160           # the DECLARED observation horizon. Shared with the instrument, and declared to be.
T0_EVAL = 128          # when the privileged inputs begin
N_RANDOM = 48          # dense random input ensemble size
T_LONG = 1600          # the horizon on which SETTLING TIME is measured (see response_profile)

# TOL_REL: the MEASURED RK4(h=.25) vs RK4(h=.125) disagreement is ~6e-9 (leak) to ~2e-7 (bistable). This sits well
# above the worst of them and four orders BELOW any genuine difference. Measured, not hoped -- and re-measured by
# solver_convergence() in the development certificate, because a tolerance nobody checks is a wish.
TOL_REL = 1.0e-5
SHIFT_GROUP = (0, 3, 6, 9)     # the declared cyclic carrier-shift group (P_CLK / 4)

SILENT_FRAC = 1.0e-3   # SILENT if the largest accessible response is below this fraction of the readout scale
SNR_FLOOR = 3.0        # below this TRUE snr the channel cannot read the system at all
SETTLE_FRAC = 0.99     # settled = the step response has reached this fraction of its asymptote
DRIFT_RATIO_MAX = 0.5  # a baseline whose drift excursion exceeds this fraction of the response is nonstationary

PRIV_EQUIVALENT = "PRIV_EQUIVALENT"
PRIV_DIFFERENT = "PRIV_DIFFERENT"
PRIV_SILENT = "PRIV_SILENT"

_TCACHE = {}
_PCACHE = {}


def random_inputs(arm: str, seed: int, n: int = N_RANDOM) -> list:
    """A DENSE RANDOM ADMISSIBLE INPUT ENSEMBLE. Deliberately NOT the fingerprint's battery.

    The battery is eight or sixteen fixed probes. This is forty-eight random ones -- random targets, random signs,
    random amplitudes spanning and EXCEEDING the battery's range, random onsets, random durations. If two systems
    agree here and the battery says they differ, the battery is inventing a difference. If they DISAGREE here and
    the battery says they are indistinguishable, that is a FALSE SAMENESS and must be reported as one -- which is
    the entire reason this ensemble is richer than the thing it audits.
    """
    rng = np.random.default_rng(seed)
    targets = [0, 1] + ([] if arm == "limited" else list(INTERNAL))
    out = []
    for i in range(n):
        tgt = int(rng.choice(targets))
        ext = tgt in (0, 1)
        kind = str(rng.choice(["step", "pulse"])) if ext else "clamp"
        amp = float(rng.uniform(-1.6, 1.6))
        if abs(amp) < 0.15:
            amp = 0.15 if amp >= 0 else -0.15
        hold = 1 if kind == "pulse" else int(rng.integers(1, 40))
        onset = T0_EVAL + int(rng.integers(0, P_CLK))
        out.append(Probe("rand%d" % i, tgt, kind, amp, hold, onset))
    return out


def _traces(spec: Spec, arm: str, seed: int, shift: int = 0) -> np.ndarray:
    """Noise-free accessible traces over the random ensemble, with every input onset shifted by `shift`.

    Memoised on the system's NAME. Deterministic and noise-free, so the cache changes nothing scientific: it is
    the same number, computed once. Names are unique per system by construction in manifests.py."""
    key = (spec.name, arm, seed, shift)
    if key in _TCACHE:
        return _TCACHE[key]
    probes = [q for q in random_inputs(arm, seed) if q.target not in spec.blocked]
    if shift:
        probes = [Probe(p.name, p.target, p.kind, p.amp, p.hold, p.onset + shift) for p in probes]
    base = Probe("base", -1, "none", 0.0, 0, 10 ** 9)
    y = observe_noise_free(spec, [base] + probes, T_EVAL)
    lo = T0_EVAL + shift
    out = y[:, lo:lo + W_EVAL]
    _TCACHE[key] = out
    return out


def _contract_residual(spec_a, YA: np.ndarray, spec_b, YB: np.ndarray) -> float:
    """The residual between two systems' RESPONSES, expressed in units of THEIR OWN DECLARED NOISE FLOOR.

    THIS FUNCTION USED TO BE A FREE AFFINE FIT, AND THE FREE AFFINE FIT WAS WRONG. It solved for the best global
    (a, b) mapping B's traces onto A's and reported what was left. That absorbed a DOUBLED GAIN (a = 2) and an
    INVERTED SIGN (a = -1) as though they were changes of units, and duly certified `D_leak` EQUIVALENT to
    `D_leak_gain2` and to `D_leak_sign` -- two of the benchmark's flagship DIFFERENCE cases.

    The two-path check caught it, which is the entire reason the two-path check exists. A BENCHMARK WHOSE TRUTH
    PATH IS WRONG CANNOT FAIL AN INSTRUMENT; IT CAN ONLY SLANDER ONE. Classified: evaluator / ground-truth failure.

    The error was conceptual, not clerical, and it is the SAME error the measurement-contract theorem describes:

        Under a FREE output scale there is no scale left to reference, and gain is genuinely unidentifiable.
        Under the DECLARED CONTRACT the noise floor is COMMON AND FIXED, so `a` is NOT free -- it is PINNED.

    So the scale is not fitted. It is taken from the contract: each response is divided by that channel's own
    declared noise scale `unit_a * sigma`, which is precisely the scale the instrument ESTIMATES as sigma_hat.
    A change of units multiplies the response and the noise by the same `a` and cancels exactly. A change of GAIN
    multiplies the response and leaves the noise alone, and therefore survives -- as it must.

    The offset `b` and the operating point cancel identically, because these are DEVIATIONS: probe minus baseline.
    Nothing is fitted here at all. There is no least squares left in this function, and that is the point.
    """
    ra = (YA[1:] - YA[0][None, :]) / (abs(spec_a.unit_a) * spec_a.sigma)
    rb = (YB[1:] - YB[0][None, :]) / (abs(spec_b.unit_b * 0 + spec_b.unit_a) * spec_b.sigma)
    scale = float(np.sqrt(np.mean(ra ** 2)))
    if scale < 1e-300:
        return 0.0 if float(np.sqrt(np.mean((ra - rb) ** 2))) < 1e-300 else np.inf
    return float(np.sqrt(np.mean((ra - rb) ** 2)) / scale)


def response_profile(spec: Spec, arm: str, seed: int = 7) -> dict:
    """WORLD-LEVEL properties, computed noise-free and INDEPENDENTLY of the instrument, so that the ABSTENTION
    categories get a second path too instead of resting on my say-so in the manifest."""
    key = (spec.name, arm, seed)
    if key in _PCACHE:
        return _PCACHE[key]
    Y = _traces(spec, arm, seed)
    base, resp = Y[0], Y[1:]
    max_resp = float(np.abs(resp - base[None, :]).max())

    # SETTLING TIME is a property of the WORLD, and it must be measured on a horizon LONG ENOUGH TO CONTAIN IT.
    # The first version estimated the asymptote from the tail of a 200-sample window. For a slow system the
    # response has not arrived by then, so it took 99% OF A VALUE STILL CLIMBING and reported t_settle = 182 for a
    # system whose true settling time is 507. It would have certified "not in flight" for a response that was
    # entirely in flight -- D-067's error, inside the very evaluator whose job is to catch it.
    if DRIVE in spec.blocked:
        t_settle = 0          # the drive cannot be stepped, so settling time is not defined on this system
    else:
        step = Probe("settle", DRIVE, "step", 1.0, T_LONG - T0_EVAL, T0_EVAL)
        nb = Probe("base", -1, "none", 0.0, 0, 10 ** 9)
        ys = observe_noise_free(spec, [nb, step], T_LONG)
        d = ys[1, T0_EVAL:] - ys[0, T0_EVAL:]
        asym = float(d[-50:].mean())
        if abs(asym) < 1e-15:
            t_settle = 0
        else:
            hit = np.nonzero(np.abs(d) >= SETTLE_FRAC * abs(asym))[0]
            t_settle = int(hit[0]) if len(hit) else 10 ** 6

    scale = abs(spec.unit_a) * spec.g_out
    silent = bool(max_resp < SILENT_FRAC * max(scale, 1e-300))
    snr = max_resp / max(abs(spec.unit_a) * spec.sigma, 1e-300)

    phi = np.exp(-1.0 / spec.drift_tau)
    drift_std = abs(spec.unit_a) * spec.drift_sigma * np.sqrt((1 - phi ** (2 * T_EVAL)) / (1 - phi ** 2))
    # A SILENT system has no response for the drift to be large RELATIVE TO. That ratio is 0/0, and reporting 1e300
    # as "nonstationary" would be my own arithmetic masquerading as a fact about the world.
    drift_ratio = float(drift_std / max_resp) if (not silent and max_resp > 0) else float("nan")

    n_all = len(random_inputs(arm, seed))
    n_ok = len([q for q in random_inputs(arm, seed) if q.target not in spec.blocked])
    out = {"max_response": max_resp, "silent": silent, "snr_true": float(snr),
           "blocked": tuple(spec.blocked), "admissible_frac": n_ok / max(n_all, 1),
           "t_settle": t_settle, "window": W_EVAL, "in_flight": bool(t_settle > W_EVAL),
           "drift_ratio": drift_ratio, "unreadable": bool(snr < SNR_FLOOR),
           "nonstationary": (bool(drift_ratio > DRIFT_RATIO_MAX) if not silent else False)}
    _PCACHE[key] = out
    return out


def privileged_compare(a: Spec, b: Spec, arm: str, seed: int = 7) -> dict:
    """Are these two systems separable by ANY admissible input, up to the declared nuisance group?"""
    pa = response_profile(a, arm, seed)
    pb = response_profile(b, arm, seed)
    if pa["silent"] or pb["silent"]:
        return {"verdict": PRIV_SILENT, "residual": None, "left": pa, "right": pb,
                "why": "at least one system produces no accessible response to any admissible input"}
    if tuple(a.blocked) != tuple(b.blocked):
        # The two systems do not even admit the SAME inputs. There is no common repertoire to compare them on,
        # and pretending otherwise would compare a system's response to one probe with another's response to a
        # different probe. That is not a comparison; it is a category error with a number attached.
        return {"verdict": PRIV_SILENT, "residual": None, "left": pa, "right": pb,
                "why": "the two systems do not admit the same interventions (blocked=%s vs %s): there is no "
                       "common repertoire on which a comparison is even defined" % (a.blocked, b.blocked)}
    YA = _traces(a, arm, seed)
    best, best_s = np.inf, None
    for s in SHIFT_GROUP:
        r = _contract_residual(a, YA, b, _traces(b, arm, seed, shift=s))
        if r < best:
            best, best_s = r, s
    return {"verdict": PRIV_EQUIVALENT if best <= TOL_REL else PRIV_DIFFERENT,
            "residual": float(best), "shift": best_s, "tol": TOL_REL, "left": pa, "right": pb,
            "why": "best relative residual %.3e, responses expressed in units of each channel's own DECLARED "
                   "noise floor and quotiented by the cyclic carrier shift, against a solver tolerance of %.0e"
                   % (best, TOL_REL)}


def solver_convergence(spec: Spec, arm: str = "limited", seed: int = 7) -> float:
    """THE NUMBER THAT LICENSES "SOLVER REFINEMENT IS A NUISANCE". Not a hope; a measurement."""
    fine = Spec(**{**spec.__dict__, "substeps": 8})
    fine.name = spec.name + "__fine_probe"
    Y1, Y2 = _traces(spec, arm, seed), _traces(fine, arm, seed)
    s = float(np.sqrt(np.mean((Y1 - Y1.mean()) ** 2)))
    return float(np.sqrt(np.mean((Y1 - Y2) ** 2)) / max(s, 1e-300))


def theseus_replacement(base: Spec, replacement: Spec, t_swap: int, T: int = T_EVAL,
                        arm: str = "limited", seed: int = 7) -> dict:
    """THE SHIP OF THESEUS, MEASURED AND REPORTED EXACTLY.

    D-073 corrected the Boolean version of this claim: "behaviour uninterrupted" was WITHDRAWN, because the
    accessible output deviated on exactly one step (t=53, channel 2), and the reported "14 steps" was the SPAN from
    replacement to the last deviating sample, not fourteen deviating samples.

    That correction is preserved here BY CONSTRUCTION: this function reports the NUMBER OF DEVIATING SAMPLES and
    the SPAN as two separate fields with two separate names, so that they cannot be conflated again by anyone --
    including me.
    """
    probes = random_inputs(arm, seed, n=8)
    nb = Probe("base", -1, "none", 0.0, 0, 10 ** 9)
    q_base = Spec(**{**base.__dict__, "sigma": 0.0, "drift_sigma": 0.0})
    q_repl = Spec(**{**replacement.__dict__, "sigma": 0.0, "drift_sigma": 0.0})
    z = np.zeros(9, dtype=np.int64)
    ref = simulate(q_base, [nb] + probes, T, z)["u"]
    swp = simulate(q_base, [nb] + probes, T, z, swap_to=q_repl, swap_at=t_swap)["u"]
    scale = max(abs(base.unit_a) * base.g_out, 1e-300)
    dev = np.abs(swp - ref) / scale
    eps = 1e-9
    mask = dev > eps
    idx = np.nonzero(mask.any(0))[0]
    post = idx[idx >= t_swap]
    return {"t_swap": t_swap, "eps_rel": eps,
            "n_deviating_samples": int(mask.any(0).sum()),
            "deviating_sample_times": [int(i) for i in idx],
            "last_deviating_sample": (int(post[-1]) if len(post) else None),
            "span_from_swap_to_last_deviation": (int(post[-1] - t_swap + 1) if len(post) else 0),
            "max_relative_deviation": float(dev.max()),
            "NOTE": "n_deviating_samples and span_from_swap_to_last_deviation are DIFFERENT QUANTITIES. "
                    "Conflating them is the D-073 error, and it is why they have different names here."}
