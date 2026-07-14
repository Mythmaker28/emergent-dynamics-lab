"""CTRANS ENGINE -- a spatially embedded chain of continuous sites with a FLOAT observable of order 1e-3.

WHY THIS SUBSTRATE EXISTS. The frozen Boolean fingerprint (EXP-GT-FINGERPRINT-00) decides by Hamming distance over
uint8 symbols. The droplet's accessible observable is a continuous float of order 1e-3. Cast it to uint8 and every
system collapses to zero -- universal false SAMENESS. Compare it by exact float inequality and every system differs
from its own later self -- universal false DIFFERENCE. Neither is a measurement (D-073, PREFLIGHT_FAIL).

So a continuous instrument has to be BUILT, and a continuous instrument can only be qualified against a continuous
ground truth. This file is that ground truth, and it is deliberately the smallest thing that can host the actual
metrological problem:

    * a CONTINUOUS accessible observable, at the droplet's magnitude (~1e-3), so the uint8 collapse is real here;
    * MEASUREMENT NOISE and SLOW DRIFT, so "is this difference real?" is a genuine question;
    * INTEGER TRANSPORT DELAYS, so latency is real;
    * SATURATION, so amplitude matters and a one-amplitude battery is provably blind;
    * a BISTABLE site, so a TRANSIENT probe can leave a PERMANENT mark -- genuine hidden state;
    * an UNCONTROLLABLE-FROM-OUTSIDE site, so a genuine difference can be invisible to a limited repertoire.
      That last one is not a defect of the instrument. It is the false-sameness case, and it must be REPORTED as
      an equivalence class, never as identity.

SPATIAL EMBEDDING. Sites live on a 1-D chain of addresses. Site 0 is the exogenous DRIVE field, site 1 the local
SUPPLY line; both are external and perturbable by ANY repertoire. Sites 2..N-1 are internal and are perturbable
ONLY under rich access. An address is where you may put a pipette. It is not what the thing is: the engine never
tells the instrument what a site does, and the instrument never asks.

UNITS AND NOISE, AND WHY THE ORDER MATTERS.

    u(t) = a * ( y_true(t) + Y_BASE + eta(t) + delta(t) ) + b

`a`,`b` are the READOUT transform -- a change of the *measurement channel's* units, not of the system. It scales
the signal AND THE NOISE by the same `a`, because the noise is instrument noise expressed in whatever units the
instrument reports. A change of the *system's internal gain*, by contrast, scales `y_true` and LEAVES `eta` ALONE.

    THAT ASYMMETRY IS THE ONLY THING THAT MAKES THIS PROBLEM SOLVABLE.

Any statistic normalized by the measured NOISE SCALE is therefore exactly invariant to a change of units and
exactly sensitive to a change of gain. Normalize by the RESPONSE amplitude instead and gain differences vanish
along with the units -- see must-fail control L7, which does precisely that and manufactures false sameness.

INTEGRATION. RK4 at `substeps` per sample. Delays are read at SAMPLE resolution from the history buffer and held
constant across substeps, so refining the solver changes the ODE accuracy and NOTHING ELSE. Convergence between
SUBSTEPS=4 and SUBSTEPS=8 is asserted in tests to be ~1e-8 relative -- orders of magnitude below the noise floor
-- which is what licenses "solver refinement" as a declared nuisance rather than a hope.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------- FROZEN SUBSTRATE CONSTANTS
N_SITES = 6            # 0=DRIVE (external field), 1=SUPPLY (external line), 2..5 internal
DRIVE = 0
SUPPLY = 1
INTERNAL = (2, 3, 4, 5)

P_CLK = 12             # period of the exogenous carrier riding on the drive field
DRIVE_BASE = 0.50
DRIVE_AMP = 0.30
SUPPLY_BASE = 0.40

Y_BASE = 1.0e-3        # the observable's operating point -- the droplet's magnitude, on purpose
SUBSTEPS = 4           # RK4 substeps per sample (h = 0.25)
SUBSTEPS_FINE = 8      # the declared solver REFINEMENT (h = 0.125). A nuisance, not a difference.

LINEAR, SAT, BIST, DEADSITE = "LINEAR", "SAT", "BIST", "DEAD"


@dataclass
class Spec:
    """A ground-truth system. Everything here is PRIVILEGED. None of it is ever shown to the instrument."""
    name: str
    kinds: tuple                       # per-site dynamics kind, len N_SITES (sites 0,1 are driven, not integrated)
    W: np.ndarray                      # (N,N) coupling: dx_i <- W[i,j] * x_j(t - TAU[i,j])
    TAU: np.ndarray                    # (N,N) integer transport delays, in samples
    T_site: np.ndarray                 # (N,) time constants
    K_site: np.ndarray                 # (N,) saturation sharpness for SAT sites
    bias: np.ndarray                   # (N,) constant input
    C: np.ndarray                      # (N,) readout functional over sites
    g_out: float                       # OUTPUT GAIN. Part of the accessible function -- NOT a nuisance.
    k_out: float                       # output saturation sharpness (0 = linear readout)
    x0: np.ndarray                     # (N,) initial condition. For a BIST site this IS the hidden state.
    sigma: float                       # measurement-noise scale, in NATIVE observable units
    drift_sigma: float                 # per-step innovation of the slow OU baseline drift
    drift_tau: float = 500.0
    substeps: int = SUBSTEPS
    unit_a: float = 1.0                # readout transform: u = a*(y + noise + drift) + b
    unit_b: float = 0.0
    t_shift: int = 0                   # global time-origin shift of the carrier (the declared phase nuisance)
    blocked: tuple = ()                # addresses this system REFUSES to let you touch. A probe aimed at one of
                                       # them does not "return zero" -- it does not happen, and the instrument
                                       # must record it as MISSING and pay for it in COVERAGE.
    meta: dict = field(default_factory=dict)   # PRIVILEGED construction labels. Never read by the instrument.


def drive_field(t, spec: Spec):
    tt = np.asarray(t) + spec.t_shift
    return DRIVE_BASE + DRIVE_AMP * np.sin(2.0 * np.pi * tt / P_CLK)


def supply_field(t, spec: Spec):
    return SUPPLY_BASE + 0.0 * np.asarray(t, dtype=float)


# ---------------------------------------------------------------- probes
@dataclass
class Probe:
    """One admissible intervention. `target` is an ADDRESS, not a component identity."""
    name: str
    target: int                # site index
    kind: str                  # "step" (additive, external) | "pulse" (additive, 1 sample) | "clamp" (internal)
    amp: float
    hold: int
    onset: int                 # absolute sample at which the probe begins

    @property
    def external(self) -> bool:
        return self.target in (DRIVE, SUPPLY)


NULL_PROBE = Probe("baseline", -1, "none", 0.0, 0, 10 ** 9)


class VacuityError(AssertionError):
    """The probe did not take. Recorded as MISSING -- never as a zero response."""


class _Compiled:
    """The system's structure, compiled once per episode batch instead of re-walked 6x6 times per RK4 stage.

    The first version rebuilt the full (B,N,N) delayed-input tensor inside every RK stage with a nested Python
    loop over all 36 site pairs. It was correct and unusably slow. Nothing about the physics changed here; only
    the number of times Python is asked to walk a matrix that is mostly zeros. The instantaneous edges become ONE
    matmul; the delayed edges are gathered once per SAMPLE, because a delay is defined at sample resolution and
    cannot change inside a substep anyway.
    """

    def __init__(self, spec: Spec):
        self.T = spec.T_site
        self.K = spec.K_site
        self.bias = spec.bias[None, :]
        self.W_inst = np.where(spec.TAU == 0, spec.W, 0.0)
        self.delayed = [(i, j, int(spec.TAU[i, j])) for i in INTERNAL for j in range(N_SITES)
                        if spec.TAU[i, j] > 0 and spec.W[i, j] != 0.0]
        self.Wd = spec.W
        k = spec.kinds
        for i in INTERNAL:
            if k[i] not in (LINEAR, SAT, BIST, DEADSITE):
                raise ValueError(f"unknown site kind {k[i]!r} at site {i}")
        self.lin = np.array([i for i in INTERNAL if k[i] == LINEAR], dtype=int)
        self.sat = np.array([i for i in INTERNAL if k[i] == SAT], dtype=int)
        self.bis = np.array([i for i in INTERNAL if k[i] == BIST], dtype=int)
        self.dea = np.array([i for i in INTERNAL if k[i] == DEADSITE], dtype=int)

    def deriv(self, x, drv_delayed):
        drv = drv_delayed + x @ self.W_inst.T + self.bias
        dx = np.zeros_like(x)
        if len(self.lin):
            i = self.lin
            dx[:, i] = (-x[:, i] + drv[:, i]) / self.T[i]
        if len(self.sat):
            i = self.sat
            dx[:, i] = (-x[:, i] + np.tanh(self.K[i] * drv[:, i]) / self.K[i]) / self.T[i]
        if len(self.bis):
            i = self.bis
            dx[:, i] = (x[:, i] - x[:, i] ** 3 + drv[:, i]) / self.T[i]
        if len(self.dea):
            i = self.dea
            dx[:, i] = -x[:, i] / self.T[i]
        return dx


def _readout(x, spec: Spec):
    v = x @ spec.C
    if spec.k_out > 0:
        v = np.tanh(spec.k_out * v) / spec.k_out
    return spec.g_out * v


def simulate(spec: Spec, probes: list, T: int, seeds, swap_to: Spec = None, swap_at: int = -1) -> dict:
    """Simulate a BATCH of episodes of ONE system. One episode per entry of `probes`.

    Returns the ACCESSIBLE observable `u` (B,T) and -- for the PRIVILEGED evaluator only -- the noise-free
    `y_true` (B,T) and the full state history (T,B,N). The instrument receives `u` and nothing else.
    """
    seeds = np.asarray(seeds)
    B = len(probes)
    assert len(seeds) == B, "one measurement seed per episode"
    x = np.tile(spec.x0.astype(float), (B, 1))
    hist = np.zeros((T, B, N_SITES))
    y = np.zeros((T, B))
    took = np.zeros(B, dtype=bool)

    ext_add = np.zeros((T, B, N_SITES))
    clamp_on = np.zeros((T, B, N_SITES), dtype=bool)
    clamp_val = np.zeros((T, B, N_SITES))
    for b, p in enumerate(probes):
        if p.kind == "none":
            continue
        if p.target in spec.blocked:
            raise VacuityError("%s: address %d is not accessible on this system. A probe that cannot be "
                               "applied is MISSING, and missing is not zero." % (p.name, p.target))
        n = 1 if p.kind == "pulse" else p.hold
        lo, hi = p.onset, min(p.onset + n, T)
        if lo >= T:
            raise VacuityError(f"{p.name}: onset {lo} is outside the episode (T={T})")
        if p.kind in ("step", "pulse"):
            if p.target not in (DRIVE, SUPPLY):
                raise VacuityError(f"{p.name}: additive field probes only apply to external sites")
            ext_add[lo:hi, b, p.target] = p.amp
        elif p.kind == "clamp":
            if p.target in (DRIVE, SUPPLY):
                raise VacuityError(f"{p.name}: clamp probes are for INTERNAL addresses")
            clamp_on[lo:hi, b, p.target] = True
            clamp_val[lo:hi, b, p.target] = p.amp
        else:
            raise VacuityError(f"unknown probe kind {p.kind!r}")
        took[b] = True

    cur, swapped = spec, False
    comp = _Compiled(spec)
    tt = np.arange(T)
    dfield = drive_field(tt, spec)
    sfield = supply_field(tt, spec)
    any_clamp = bool(clamp_on.any())

    for t in range(T):
        if swap_to is not None and not swapped and t == swap_at:
            # SHIP OF THESEUS. The material is replaced mid-trajectory. The shared internal sites carry their
            # state across; sites the new implementation adds start from ITS x0.
            newx = np.tile(swap_to.x0.astype(float), (B, 1))
            keep = [i for i in INTERNAL if spec.kinds[i] != DEADSITE and swap_to.kinds[i] != DEADSITE]
            if keep:
                newx[:, keep] = x[:, keep]
            x, cur, swapped, comp = newx, swap_to, True, _Compiled(swap_to)

        x[:, DRIVE] = dfield[t] + ext_add[t, :, DRIVE]
        x[:, SUPPLY] = sfield[t] + ext_add[t, :, SUPPLY]
        if any_clamp:
            m = clamp_on[t]
            if m.any():
                x = np.where(m, clamp_val[t], x)
        hist[t] = x
        y[t] = _readout(x, cur)

        drv_d = np.zeros((B, N_SITES))
        for (i, j, d) in comp.delayed:
            drv_d[:, i] += comp.Wd[i, j] * hist[max(t - d, 0), :, j]
        h = 1.0 / cur.substeps
        for _ in range(cur.substeps):
            k1 = comp.deriv(x, drv_d)
            k2 = comp.deriv(x + 0.5 * h * k1, drv_d)
            k3 = comp.deriv(x + 0.5 * h * k2, drv_d)
            k4 = comp.deriv(x + h * k3, drv_d)
            x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    # THE MEASUREMENT. Noise and drift are INDEPENDENT PER EPISODE -- they do NOT cancel between a probe episode
    # and its baseline, because in a real experiment they do not. Sharing the seed between base and probe would
    # make the deviation trace noiseless and the entire noise calibration a fiction.
    eta = np.zeros((T, B))
    innov = np.zeros((T, B))
    for b in range(B):
        rng = np.random.default_rng(int(seeds[b]))
        if spec.sigma > 0:
            eta[:, b] = rng.normal(0.0, spec.sigma, T)
        if spec.drift_sigma > 0:
            innov[:, b] = rng.normal(0.0, spec.drift_sigma, T)
    phi = np.exp(-1.0 / spec.drift_tau)
    delta = np.zeros((T, B))
    for t in range(1, T):
        delta[t] = phi * delta[t - 1] + innov[t]
    u = spec.unit_a * (y + Y_BASE + eta + delta) + spec.unit_b

    return {"u": u.T, "y_true": y.T, "hist": hist, "took": took}


def observe(spec: Spec, probes: list, T: int, seeds) -> np.ndarray:
    """THE ONLY CHANNEL THE INSTRUMENT IS ALLOWED. A (B,T) float array. No state, no labels, no ground truth."""
    return simulate(spec, probes, T, seeds)["u"]


def observe_noise_free(spec: Spec, probes: list, T: int) -> np.ndarray:
    """PRIVILEGED. The exact ACCESSIBLE OBSERVABLE with sigma = 0 and drift = 0 -- units and offset INCLUDED.

    It must be the accessible observable, not the pre-readout signal. An evaluator that peeked at `y_true` would
    see through the unit transform and would be validating a world the instrument never gets to look at. The
    privileged path may remove the NOISE. It may not remove the READOUT.
    """
    q = Spec(**{**spec.__dict__, "sigma": 0.0, "drift_sigma": 0.0})
    return simulate(q, probes, T, np.zeros(len(probes), dtype=np.int64))["u"]
