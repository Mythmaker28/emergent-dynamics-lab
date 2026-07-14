"""THE CTRANS COMPONENT LIBRARY and the CONSTRUCTION-DECLARED CHALLENGE MATRIX.

Everything in this file is PRIVILEGED GROUND TRUTH. The instrument never imports it for anything but the observable.

TWO IDENTIFIABILITY FACTS, DISCOVERED WHILE BUILDING THIS AND WORTH STATING BEFORE THE CODE:

1.  A PURELY STATIC OUTPUT OFFSET IS NOT IDENTIFIABLE under an affine readout nuisance. If the readout may be
    `u = a*y + b` with `b` unknown, then a hidden state whose ONLY effect is to add a constant to the output is
    EXACTLY what `b` absorbs. No instrument can recover it, and one that claimed to would be reading its own
    normalization. So the bistable memory here is not wired to add a constant: it is wired THROUGH A SATURATING
    READOUT, where its state moves the operating point and therefore changes the system's INCREMENTAL CAUSAL GAIN.
    Hidden state is detectable exactly insofar as it changes the RESPONSE. That is not a workaround. It is the
    honest boundary of what a response fingerprint can see.

2.  THE CONTINUOUS DEVIATION IS NOT BLIND TO INVERSION, AND THE BOOLEAN ONE WAS. The Boolean fingerprint needed an
    ABSOLUTE channel because its deviation was `obs != bas` -- a XOR, which throws away direction, so AND and XOR
    deviated on identical steps and scored d = 0.0000. Here the deviation `r(t) = u_probe(t) - u_base(t)` is a
    SIGNED REAL. An inverted output gives `-r`. Direction is already carried, and the `sign_flip` DIFFERENCE case
    proves it. The continuous representation is simpler than the Boolean one for a reason, not by neglect.

THE ADDRESS SPACE IS FIXED. Every system has all six sites whether it uses them or not, so the rich battery is
IDENTICAL for every system. A system with no memory still has address 4; clamping it simply does nothing. An
address is where you may put a pipette, not a statement about what is there. A battery whose LENGTH depended on
which components a system happens to contain would be an adaptive probe wearing a fixed probe's coat.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .engine import (N_SITES, DRIVE, SUPPLY, INTERNAL, LINEAR, SAT, BIST, DEADSITE, Spec,
                     SUBSTEPS, SUBSTEPS_FINE)

G0 = 1.0e-3          # the output gain scale. Puts the observable at the droplet's magnitude.
SIG0 = 1.0e-5        # the nominal measurement-noise scale, in native observable units.
                     # Gives a peak SNR of ~118 on the largest probe: a realistic optical readout,
                     # not a fantasy one. The NULL distance is noise-standardized and therefore
                     # sigma-INVARIANT, so this choice does not flatter the continuity side.

DRIFT_FRAC = 0.10    # THE SLOW DRIFT IS DEFINED AS A FRACTION OF THE NOISE, NOT AS AN ABSOLUTE.
# ------------------------------------------------------------------------------------------------------------
# That is not cosmetic. The instrument standardizes every response by the channel's own measured noise scale, so
# the NULL distance between two independent measurements of the SAME system is O(1) in those units and -- if and
# only if every stochastic term scales with sigma -- is EXACTLY INDEPENDENT OF sigma. A tolerance calibrated on
# development noise then transfers to a noise regime it has never seen, by construction rather than by luck.
#
# Pin the drift to an absolute value instead and that invariance quietly dies: a quiet channel would carry
# relatively more drift than a loud one, the null distribution would move with sigma, and the frozen continuity
# radius would be wrong on exactly the prospective systems it was supposed to survive.
# ------------------------------------------------------------------------------------------------------------


def _blank(name, sigma=SIG0, drift_frac=DRIFT_FRAC, **kw) -> Spec:
    """A system in which every internal address exists and every one of them is inert."""
    return Spec(
        name=name,
        kinds=(None, None, DEADSITE, DEADSITE, DEADSITE, DEADSITE),
        W=np.zeros((N_SITES, N_SITES)),
        TAU=np.zeros((N_SITES, N_SITES), dtype=int),
        T_site=np.array([1.0, 1.0, 8.0, 8.0, 8.0, 8.0]),
        K_site=np.ones(N_SITES),
        bias=np.zeros(N_SITES),
        C=np.zeros(N_SITES),
        g_out=G0, k_out=0.0,
        x0=np.zeros(N_SITES),
        sigma=sigma, drift_sigma=drift_frac * sigma,
        **kw)


# ---------------------------------------------------------------- topologies
def leak(name, tau=0, T=8.0, gain=1.0, sign=+1, site=2, k_out=0.0, **kw) -> Spec:
    """drive -(delay tau)-> a leaky site -> readout. The minimal transducer."""
    s = _blank(name, **kw)
    s.kinds = _set(s.kinds, site, LINEAR)
    s.W[site, DRIVE] = 1.0
    s.TAU[site, DRIVE] = tau
    s.T_site[site] = T
    s.C[site] = sign * gain
    s.k_out = k_out
    s.meta = {"topology": "leak", "tau": tau, "T": T, "gain": gain, "sign": sign, "site": site}
    return s


def cascade(name, tau=0, T2=6.0, T3=10.0, gain=1.0, k_out=0.0, **kw) -> Spec:
    """drive -> site2 -> site3 -> readout. A different LATENCY STRUCTURE, not merely a different delay."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.W[3, 2] = 1.0
    s.T_site[2], s.T_site[3] = T2, T3
    s.C[3] = gain
    s.k_out = k_out
    s.meta = {"topology": "cascade", "tau": tau, "T2": T2, "T3": T3, "gain": gain}
    return s


def feedback(name, k=0.5, T2=6.0, T3=10.0, gain=1.0, tau=0, k_out=0.0, **kw) -> Spec:
    """drive -> site2, site2 -> site3, site3 -(-k)-> site2. GENUINE FEEDBACK: an infinite impulse response."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.W[2, 3] = -k
    s.W[3, 2] = 1.0
    s.T_site[2], s.T_site[3] = T2, T3
    s.C[2] = gain
    s.k_out = k_out
    s.meta = {"topology": "feedback", "k": k, "T2": T2, "T3": T3, "gain": gain, "tau": tau}
    return s


def fir(name, taps=((0, 1.0), (5, -0.5), (10, 0.25)), T=2.0, gain=1.0, k_out=0.0, **kw) -> Spec:
    """A TAPPED DELAY LINE: the output is a function of a FINITE WINDOW of past drive. DELAYED STATIC -- no loop.

    Three fast leaky sites, each reading the drive at its own delay. Fast `T` makes each site track its tap, so the
    readout is (approximately) a finite impulse response. Contrast with `feedback`, whose response never truly
    terminates. Distinguishing these two is the 'genuine feedback versus delayed static' challenge."""
    s = _blank(name, **kw)
    sites = [2, 3, 4][:len(taps)]
    for site, (d, w) in zip(sites, taps):
        s.kinds = _set(s.kinds, site, LINEAR)
        s.W[site, DRIVE] = 1.0
        s.TAU[site, DRIVE] = d
        s.T_site[site] = T
        s.C[site] = gain * w
    s.k_out = k_out
    s.meta = {"topology": "fir", "taps": taps, "T": T, "gain": gain}
    return s


def satsys(name, tau=0, T=8.0, gain=1.0, k_out=1.2, **kw) -> Spec:
    """A leaky site read out through a SATURATING transducer, WITH ITS SMALL-SIGNAL GAIN MATCHED TO `leak`.

    The match is exact and analytic, not fitted. At the operating point the leaky site settles to the mean drive,
    so v0 = gain * DRIVE_BASE, and d/dv [tanh(k v)/k] = sech^2(k v0) there. Rescaling g_out by 1/sech^2(k v0)
    makes the FIRST derivative identical to the linear system's.

    So the two systems agree to first order and part company only at second order and beyond -- which is to say,
    ONLY WHEN PROBED HARD ENOUGH. A single-amplitude battery is blind to this by construction, and the
    amplitude-ladder diagnostic in the development certificate measures exactly how blind.
    """
    from .engine import DRIVE_BASE
    s = leak(name, tau=tau, T=T, gain=gain, k_out=k_out, **kw)
    v0 = gain * DRIVE_BASE
    s.g_out = G0 / (1.0 / np.cosh(k_out * v0) ** 2)
    s.meta = {"topology": "satsys", "tau": tau, "T": T, "gain": gain, "k_out": k_out,
              "small_signal_matched_at_v0": float(v0)}
    return s


def memory(name, mem0=+1.0, w_drive=0.55, T=8.0, Tm=5.0, gain=1.0, c_mem=1.0,
           k_out=250.0, tau=0, **kw) -> Spec:
    """A BISTABLE site (double well) read out through a SATURATION.

    The memory does NOT merely add a constant -- see the header. It shifts the operating point of the output
    tanh, and therefore changes the INCREMENTAL GAIN of the whole system's response to every probe. That is a
    hidden state a response fingerprint can legitimately see.

    A SMALL pulse perturbs it and it falls back into its well: RECOVERY.
    A LARGE pulse carries it across the separatrix at x = 0: a TRANSIENT probe leaves a PERMANENT mark. MEMORY.
    """
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, LINEAR), 4, BIST)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.T_site[2] = T
    s.C[2] = gain
    s.W[4, DRIVE] = w_drive          # the drive nudges the well, but the carrier alone must NEVER flip it
    s.bias[4] = -w_drive * 0.50      # centre the well about the drive's mean, so the baseline is bistable
    s.T_site[4] = Tm
    s.C[4] = c_mem
    s.x0[4] = mem0                   # THE HIDDEN STATE
    s.k_out = k_out
    s.meta = {"topology": "memory", "mem0": mem0, "w_drive": w_drive, "T": T, "Tm": Tm,
              "gain": gain, "c_mem": c_mem, "k_out": k_out}
    return s


def hidden_mode(name, base: Spec, c_h=1.2, T=9.0) -> Spec:
    """`base` PLUS an internal site that is UNREACHABLE from the external fields but FEEDS the readout.

    W[5,:] = 0, x0[5] = 0, so under EXTERNAL-ONLY probing site 5 stays at exactly zero for all time and contributes
    exactly nothing: the accessible behaviour is BIT-FOR-BIT that of `base`. Clamp address 5 -- which only RICH
    access can do -- and the output moves.

    THIS IS THE FALSE-SAMENESS CASE, and it is not a defect. Two systems that no admissible probe in the limited
    repertoire can separate form an EQUIVALENCE CLASS. Reporting them as SAME would be the defect.
    """
    s = Spec(**{**base.__dict__})
    s.name = name
    s.kinds = _set(base.kinds, 5, LINEAR)
    s.W = base.W.copy()              # row 5 stays all-zero: NOTHING drives it
    s.TAU = base.TAU.copy()
    s.T_site = base.T_site.copy()
    s.T_site[5] = T
    s.C = base.C.copy()
    s.C[5] = c_h                     # but it DOES feed the readout
    s.bias = base.bias.copy()
    s.x0 = base.x0.copy()
    s.x0[5] = 0.0                    # and it starts at rest, so it never leaves rest without an internal probe
    s.meta = {**base.meta, "topology": base.meta.get("topology") + "+hidden_mode", "c_h": c_h}
    return s


def supply_cause(name, base: Spec, w_s=0.9, site=3, T=7.0, gain=0.8) -> Spec:
    """`base` PLUS an INDEPENDENTLY CONTROLLABLE ADDITIONAL CAUSE: a path from the SUPPLY line to the readout."""
    s = Spec(**{**base.__dict__})
    s.name = name
    s.kinds = _set(base.kinds, site, LINEAR)
    s.W = base.W.copy()
    s.W[site, SUPPLY] = w_s
    s.TAU = base.TAU.copy()
    s.T_site = base.T_site.copy()
    s.T_site[site] = T
    s.C = base.C.copy()
    s.C[site] = gain
    s.bias = base.bias.copy()
    s.x0 = base.x0.copy()
    s.meta = {**base.meta, "topology": base.meta.get("topology") + "+supply_cause", "w_s": w_s}
    return s


def dead_site(name, base: Spec, x0_5=0.7) -> Spec:
    """`base` PLUS a genuinely EXTRA internal degree of freedom that is coupled to NOTHING and read by NOTHING.

    A different microscopic implementation -- a different internal state dimension, carrying a real decaying
    quantity -- with EXACTLY identical accessible behaviour under BOTH arms. The purest continuity case there is:
    the insides differ and there is no admissible probe, rich or limited, that can know it."""
    s = Spec(**{**base.__dict__})
    s.name = name
    s.kinds = _set(base.kinds, 5, DEADSITE)
    s.W, s.TAU = base.W.copy(), base.TAU.copy()
    s.T_site, s.C, s.bias = base.T_site.copy(), base.C.copy(), base.bias.copy()
    s.C[5] = 0.0
    s.x0 = base.x0.copy()
    s.x0[5] = x0_5
    s.meta = {**base.meta, "topology": base.meta.get("topology") + "+dead_site"}
    return s


def relocate(name, base: Spec, src=2, dst=3) -> Spec:
    """The SAME transfer function, built on a DIFFERENT INTERNAL ADDRESS.

    Limited access cannot tell (identical accessible behaviour, exactly). Rich access CAN: clamping address `src`
    moves one and not the other. Equivalence is relative to a repertoire -- declared per-arm, before the freeze,
    exactly as the Boolean benchmark had to do for `xor3`."""
    s = Spec(**{**base.__dict__})
    s.name = name
    perm = list(range(N_SITES))
    perm[src], perm[dst] = dst, src
    s.kinds = tuple(base.kinds[perm.index(i)] for i in range(N_SITES))
    s.W = base.W[np.ix_(perm, perm)].copy()
    s.TAU = base.TAU[np.ix_(perm, perm)].copy()
    s.T_site = base.T_site[perm].copy()
    s.K_site = base.K_site[perm].copy()
    s.bias = base.bias[perm].copy()
    s.C = base.C[perm].copy()
    s.x0 = base.x0[perm].copy()
    s.meta = {**base.meta, "topology": base.meta.get("topology") + "+relocated", "src": src, "dst": dst}
    return s


def silent_dead(name, **kw) -> Spec:
    """g_out = 0. The observable is baseline plus noise. It answers NOTHING, to any probe, in any arm."""
    s = leak(name, **kw)
    s.g_out = 0.0
    s.meta = {"topology": "silent_dead"}
    return s


def silent_saturated(name, **kw) -> Spec:
    """Driven so deep into the output tanh that its incremental gain is numerically nil. It CAN respond in
    principle; under this battery it does not, and an all-zero fingerprint is an ABSENCE OF EVIDENCE."""
    s = leak(name, T=8.0, gain=1.0, k_out=4000.0, **kw)
    s.bias[2] = 40.0
    s.meta = {"topology": "silent_saturated"}
    return s


def too_noisy(name, sigma_mult=60.0, **kw) -> Spec:
    """Its response is BELOW ITS OWN NOISE FLOOR. Not silent -- unreadable. The distinction matters: a system
    that would answer, measured on a channel that cannot hear it, is INDETERMINATE, not INDISTINGUISHABLE."""
    s = leak(name, sigma=SIG0 * sigma_mult, **kw)
    s.meta = {"topology": "too_noisy", "sigma_mult": sigma_mult}
    return s


def too_slow(name, T=70.0, **kw) -> Spec:
    """Its response has not finished when the window ends. It is IN FLIGHT, and an in-flight response mistaken for
    a permanent mark is exactly the D-067 error arriving from the other end of the trace."""
    s = leak(name, T=T, **kw)
    s.meta = {"topology": "too_slow", "T": T}
    return s


def too_drifty(name, drift_frac=8.0, **kw) -> Spec:
    """A baseline that wanders further than the response it is supposed to reference. NONSTATIONARY, outside the
    declared contract, and the instrument must say so rather than measure it anyway."""
    s = leak(name, drift_frac=drift_frac, **kw)
    s.meta = {"topology": "too_drifty", "drift_frac": drift_frac}
    return s


def feedback_sat(name, k=0.6, T2=9.0, T3=14.0, gain=1.5, tau=3, k_sat=1.4, k_out=0.0, **kw) -> Spec:
    """FEEDBACK AROUND A SATURATING ELEMENT. A topology that appears in the PROSPECTIVE split and NOWHERE in
    development: the loop gain now depends on the operating point, so the response is neither a clean IIR nor a
    clean saturation. It exists to make the prospective set structurally, not merely numerically, unseen."""
    s = _blank(name, **kw)
    s.kinds = _set(_set(s.kinds, 2, SAT), 3, LINEAR)
    s.W[2, DRIVE] = 1.0
    s.TAU[2, DRIVE] = tau
    s.W[2, 3] = -k
    s.W[3, 2] = 1.0
    s.K_site[2] = k_sat
    s.T_site[2], s.T_site[3] = T2, T3
    s.C[2] = gain
    s.k_out = k_out
    s.meta = {"topology": "feedback_sat", "k": k, "k_sat": k_sat, "T2": T2, "T3": T3, "gain": gain, "tau": tau}
    return s


# ---------------------------------------------------------------- declared NUISANCE transformations
def with_units(name, base: Spec, a: float, b: float) -> Spec:
    s = Spec(**{**base.__dict__});  s.name = name;  s.unit_a, s.unit_b = a, b
    s.meta = {**base.meta, "nuisance": f"units(a={a},b={b})"};  return s


def with_refined_solver(name, base: Spec) -> Spec:
    s = Spec(**{**base.__dict__});  s.name = name;  s.substeps = SUBSTEPS_FINE
    s.meta = {**base.meta, "nuisance": "solver_refinement"};  return s


def with_time_shift(name, base: Spec, k: int) -> Spec:
    """A GLOBAL shift of the carrier's time origin, by a multiple of P_CLK/n_phase. The declared phase nuisance is
    the CYCLIC GROUP this generates -- it permutes the battery's phase rows cyclically, and nothing else."""
    s = Spec(**{**base.__dict__});  s.name = name;  s.t_shift = 3 * k
    s.meta = {**base.meta, "nuisance": f"time_shift({3*k})"};  return s


def _set(kinds, i, k):
    z = list(kinds);  z[i] = k;  return tuple(z)


def access_restricted(name, base: Spec, blocked=(SUPPLY,)) -> Spec:
    """A system whose SUPPLY line (or drive) simply cannot be reached by the experimenter.

    The battery is UNCHANGED -- every system receives the same probes in the same order. What changes is that some
    of them DO NOT HAPPEN. They are recorded as MISSING and charged to COVERAGE. The forbidden move is to quietly
    substitute a different probe, or to score the absent response as a zero: a system that answered nothing because
    you never asked is not a system that answered nothing.
    """
    s = Spec(**{**base.__dict__})
    s.name = name
    s.blocked = tuple(blocked)
    s.meta = {**base.meta, "access": "restricted", "blocked": tuple(blocked)}
    return s
