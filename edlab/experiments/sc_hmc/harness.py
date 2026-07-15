"""Core harness: frozen-physics simulation primitives + a 2-bin PASSIVE pulse-chase tracer.

The pulse-chase tracer NEVER enters rho/U/V/c/N. It only re-bins the already-passive cohort field C so
that, from the label time t0, C[0] = material present at t0 and C[1] = material fed after t0. Because the
engine advects, feeds and decays C exactly alongside rho and C never feeds back, tracer choice cannot
change physics (verified empirically in capability.py: bit-identical rho/U/V under any tracer).
"""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.engine import ScaffoldEngine, SCState
from ...substrates.scaffold.observables import detect, SCEntity
from . import config as C


# --------------------------------------------------------------------------------------------------
class PulseChaseTracer:
    """Duck-typed replacement for TracerSpec: 2 passive bins. All growth after t0 feeds bin 1 (new)."""
    n_spatial = 1
    n_temporal = 1
    tau_feed = 1

    @property
    def n_cohorts(self) -> int:
        return 2

    def active_feed_cohort(self, step: int) -> int:
        return 1  # new (post-t0) material


class NoisyForcingEngine(ScaffoldEngine):
    """ARM C stochastic ceiling: bounded i.i.d. noise on the EXTERNAL fields (N, c) only.

    The frozen engine is deterministic; two exact clones would never diverge. To define a genuine
    reproducibility/stochastic baseline we perturb only the environment (nutrient + attractant) with
    small independent multiplicative noise. rho, U, V are never touched directly.
    """

    def __init__(self, spec, tracer, rng: np.random.Generator, sigma: float = C.CLONE_NOISE_SIGMA):
        super().__init__(spec, tracer)
        self.rng = rng
        self.sigma = sigma

    def step(self, st: SCState) -> SCState:
        out = super().step(st)
        shp = out.N.shape
        out.N = out.N * np.exp(self.sigma * self.rng.standard_normal(shp))
        out.c = out.c * np.exp(self.sigma * self.rng.standard_normal(shp))
        return out


# --------------------------------------------------------------------------------------------------
def frozen_engine(tracer=None) -> ScaffoldEngine:
    return ScaffoldEngine(C.SPEC, tracer if tracer is not None else C.TRACER)


def pulse_chase_engine() -> ScaffoldEngine:
    return ScaffoldEngine(C.SPEC, PulseChaseTracer())


def warmup(seed: int, internal: str = None, steps: int = None) -> SCState:
    """Self-organize an entity from a random internal state under the frozen physics."""
    internal = C.INTERNAL_INIT if internal is None else internal
    steps = C.WARMUP if steps is None else steps
    eng = frozen_engine()
    st = C.seed_state(C.SPEC, C.TRACER, seed, internal)
    for _ in range(steps):
        st = eng.step(st)
    return st


def relabel_pulse_chase(st: SCState) -> SCState:
    """Collapse the cohort field into 2 passive bins at t0: bin0 = all current material (labelled)."""
    out = st.copy()
    rho = out.rho
    out.C = np.stack([rho.copy(), np.zeros_like(rho)])  # bin0 labelled, bin1 empty
    return out


def advance(eng: ScaffoldEngine, st: SCState, steps: int) -> SCState:
    cur = st
    for _ in range(steps):
        cur = eng.step(cur)
    return cur


def trajectory(eng: ScaffoldEngine, st: SCState, steps: int, cadence: int) -> list[SCState]:
    out = [st.copy()]
    cur = st
    for t in range(1, steps + 1):
        cur = eng.step(cur)
        if t % cadence == 0:
            out.append(cur.copy())
    return out


def entities(st: SCState) -> list[SCEntity]:
    return detect(st, C.DET, C.SPEC.rho_max)


def largest_entity(st: SCState) -> SCEntity | None:
    es = entities(st)
    return max(es, key=lambda e: e.size) if es else None


def entity_mask(st: SCState, e: SCEntity) -> np.ndarray:
    m = np.zeros(st.rho.shape, dtype=bool)
    m[e.cells[:, 0], e.cells[:, 1]] = True
    return m


def material_continuity(e: SCEntity) -> float:
    """M(t0,t): mass-weighted fraction of the entity's material that descends from t0 (pulse-chase).

    Requires a 2-bin pulse-chase cohort layout (bin0 = labelled). Returns labelled / total.
    """
    cm = np.asarray(e.cohort_mass, dtype=float)
    tot = cm.sum()
    return float(cm[0] / tot) if tot > 0 else 1.0


def labelled_unlabelled(e: SCEntity) -> tuple[float, float]:
    cm = np.asarray(e.cohort_mass, dtype=float)
    return float(cm[0]), float(cm[1:].sum())
