"""Bounded intervention battery on the ONLY external handles: nutrient N and attractant c.

A causal-response profile is the entity's reaction to a perturbation MEASURED AGAINST a matched,
unperturbed control clone evolved with the identical engine. The control clone is also the K10
intervention-null: with no perturbation the perturbed-minus-control profile must be ~0.
"""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.engine import SCState, ScaffoldEngine
from . import config as C
from . import harness as H


def _perturb(st: SCState, field: str, op: str, amp: float) -> SCState:
    out = st.copy()
    f = getattr(out, field)
    if op == "add":
        f = f + amp * (C.SPEC.N0 if field == "N" else 1.0)
    elif op == "mul":
        f = f * amp
    else:
        raise ValueError(op)
    setattr(out, field, np.clip(f, 0.0, None))
    return out


def _features(st: SCState) -> np.ndarray:
    """Behavioural + coarse geometric observables of the largest entity (for a response profile)."""
    e = H.largest_entity(st)
    if e is None:
        return np.array([0.0, 0.0, 0.0, 0.0])
    return np.array([e.specific_uptake, e.rg, e.mass, e.mean_sig], dtype=float)


def run_intervention(eng: ScaffoldEngine, st0: SCState, field: str, op: str, amp: float,
                     horizon: int = None, cadence: int = 20) -> dict:
    """Return sampled control features, perturbed features, and their difference profile."""
    horizon = C.RESPONSE_HORIZON if horizon is None else horizon
    # matched control (no perturbation)
    ctrl = st0.copy()
    pert = _perturb(st0, field, op, amp)
    ctrl_feat, pert_feat = [], []
    for t in range(1, horizon + 1):
        ctrl = eng.step(ctrl)
        # hold the perturbation for PULSE_STEPS, then release (free evolution)
        if t <= C.PULSE_STEPS:
            pert = _perturb(pert, field, op, amp) if t > 1 else pert
        pert = eng.step(pert)
        if t % cadence == 0:
            ctrl_feat.append(_features(ctrl))
            pert_feat.append(_features(pert))
    ctrl_feat = np.asarray(ctrl_feat)
    pert_feat = np.asarray(pert_feat)
    diff = pert_feat - ctrl_feat
    return {"control": ctrl_feat, "perturbed": pert_feat, "diff": diff}


def response_profile(eng: ScaffoldEngine, st0: SCState, horizon: int = None,
                     cadence: int = 20) -> np.ndarray:
    """Concatenated difference profile over the whole frozen battery -> one causal-response vector."""
    parts = []
    for name, p in C.INTERVENTIONS:
        r = run_intervention(eng, st0, p["field"], p["op"], p["amp"], horizon, cadence)
        parts.append(r["diff"].reshape(-1))
    return np.concatenate(parts) if parts else np.array([])


def response_by_family(eng: ScaffoldEngine, st0: SCState, horizon: int = None,
                       cadence: int = 20) -> dict:
    """Per-intervention response vectors (keeps families separate; no compositing)."""
    out = {}
    for name, p in C.INTERVENTIONS:
        r = run_intervention(eng, st0, p["field"], p["op"], p["amp"], horizon, cadence)
        out[name] = r["diff"].reshape(-1)
    return out
