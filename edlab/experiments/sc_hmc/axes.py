"""Organizational axes P1-P6. Measured SEPARATELY. No composite scalar. No material labels enter any
organizational axis (axis independence, G8/K2): every feature below is a function of rho / U / V / c / N
geometry or dynamics only; the cohort field C is used solely for the material axis M elsewhere.

Each axis returns a fixed-length float vector. Continuity along an axis is the distance between the
entity's axis-vector now and its own earlier axis-vector, judged against a development-only regime.
"""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.engine import SCState
from ...substrates.scaffold.observables import detect
from . import config as C
from . import harness as H
from . import interventions as I


# ---------------------------------------------------------------------------------- P1 geometry
def p1_geometry(st: SCState, e=None) -> np.ndarray:
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(6)
    mask = H.entity_mask(st, e)
    n = st.rho.shape[0]
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    cen = e.centroid
    dy = ys - cen[0]; dy -= n * np.round(dy / n)
    dx = xs - cen[1]; dx -= n * np.round(dx / n)
    w = st.rho[ys, xs]
    # second-moment shape (rotation-invariant eigenvalues), compactness, radial spread
    Ixx = np.average(dy * dy, weights=w); Iyy = np.average(dx * dx, weights=w); Ixy = np.average(dy * dx, weights=w)
    tr = Ixx + Iyy; det = Ixx * Iyy - Ixy * Ixy
    disc = max(tr * tr / 4 - det, 0.0) ** 0.5
    l1, l2 = tr / 2 + disc, tr / 2 - disc
    aniso = float((l1 - l2) / (l1 + l2 + 1e-9))
    # perimeter (periodic 4-neighbour boundary) for compactness
    per = 0
    for ddy, ddx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        per += int((~mask[(ys + ddy) % n, (xs + ddx) % n]).sum())
    compact = float(e.size / (per + 1e-9))
    r = np.sqrt(dy * dy + dx * dx)
    core_frac = float(w[r <= e.rg].sum() / (w.sum() + 1e-9))
    return np.array([np.log(e.size + 1.0), e.rg, aniso, compact, core_frac, float((mask.sum() > 0))])


# ------------------------------------------------------------------------------- P2 internal state
def p2_internal(st: SCState, e=None) -> np.ndarray:
    """Privileged (U,V) organization: the ID-independent phenotype + bulk internal state."""
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(6)
    return np.concatenate([np.asarray(e.phenotype, dtype=float), [e.mean_sig]])


# ----------------------------------------------------------------------------------- P3 function
def p3_function(st: SCState, e=None) -> np.ndarray:
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(3)
    # specific uptake, uptake efficiency implied by internal state, mass throughput proxy
    eff = 1.0 + C.SPEC.beta * e.mean_sig
    return np.array([e.specific_uptake, e.specific_uptake / (eff + 1e-9), e.mass * e.specific_uptake])


# ------------------------------------------------------------------------------ P4 causal response
def p4_causal_response(st: SCState, eng=None) -> np.ndarray:
    """The frozen intervention battery's difference profile -> one causal-response vector.
    Deterministic given the state and the (frozen, deterministic) engine."""
    eng = H.pulse_chase_engine() if eng is None else eng
    return I.response_profile(eng, st, horizon=C.RESPONSE_HORIZON, cadence=30)


# ------------------------------------------------------------------------------------ P5 recovery
def p5_recovery(st: SCState, eng=None) -> np.ndarray:
    """Return-to-regime after a bounded perturbation, measured as RECONVERGENCE to a co-evolved
    control (scale-invariant features), NOT distance to a frozen baseline."""
    eng = H.pulse_chase_engine() if eng is None else eng

    def sinv(s):
        e = H.largest_entity(s)
        if e is None:
            return np.array([0.0, 0.0, 0.0])
        return np.array([e.specific_uptake, e.mean_sig, e.rg / (np.log(e.size + 1.0) + 1e-9)])

    ctrl = st.copy()
    pert = I._perturb(st, "N", "mul", 0.30)
    devs = []
    for t in range(1, C.RECOVERY_HORIZON + 1):
        ctrl = eng.step(ctrl)
        pert = eng.step(pert)
        if t % 10 == 0:
            devs.append(float(np.linalg.norm(sinv(pert) - sinv(ctrl))))
    devs = np.asarray(devs)
    peak = float(devs.max() + 1e-9)
    end = float(devs[-3:].mean())
    ratio = end / peak
    return np.array([ratio, peak, end])


# --------------------------------------------------------------------------------------- P6 path
def p6_path(traj: list[SCState]) -> np.ndarray:
    """Uninterrupted admissible-intermediate-state continuity from a stored trajectory. ID-free:
    a step is 'continuous' iff a detected successor exists within a bounded centroid jump AND the
    entity survives. Reported as (continuity fraction, max centroid jump, survival fraction)."""
    n = C.SPEC.size
    prev = None
    cont, jumps, alive = 0, [], 0
    steps = 0
    for st in traj:
        e = H.largest_entity(st)
        if e is None:
            prev = None
            continue
        alive += 1
        if prev is not None:
            d = np.asarray(e.centroid) - prev
            d -= n * np.round(d / n)
            jump = float(np.linalg.norm(d))
            jumps.append(jump)
            steps += 1
            if jump <= 6.0:
                cont += 1
        prev = np.asarray(e.centroid)
    frac = cont / steps if steps else 0.0
    return np.array([frac, max(jumps) if jumps else 0.0, alive / max(len(traj), 1)])


AXES = ("P1_geometry", "P2_internal", "P3_function", "P4_causal", "P5_recovery", "P6_path")


def all_static_axes(st: SCState) -> dict:
    """P1,P2,P3 are instantaneous; P4,P5 need the engine; P6 needs a trajectory (handled by caller)."""
    return {"P1_geometry": p1_geometry(st), "P2_internal": p2_internal(st), "P3_function": p3_function(st)}


def axis_distance(a: np.ndarray, b: np.ndarray, scale: np.ndarray = None) -> float:
    a = np.asarray(a, float); b = np.asarray(b, float)
    if scale is None:
        scale = np.ones_like(a)
    return float(np.linalg.norm((a - b) / (scale + 1e-9)))
