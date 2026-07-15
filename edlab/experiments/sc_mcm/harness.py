"""Harness for the multi-channel readout: engine, warmup, histories, and a MULTI-AXIS response vector
that exposes both channels (uptake for m_plus; mean attractant c for m_minus)."""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.observables import detect
from ..sc_iom.engine import IOMState
from ..sc_iom import harness as IOMH
from .engine import MultiChannelMemoryEngine, MCParams
from . import config as C


def seed_mc(seed, mem=None):
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    k = (mem or C.MC).n_comp
    Mf = np.zeros((k, C.SPEC.size, C.SPEC.size))
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, Mf, 0)


def mc_engine(mem=None):
    return MultiChannelMemoryEngine(C.SPEC, mem or C.MC, C.TRACER)


def warmup(seed, mem=None, steps=None):
    eng = mc_engine(mem); st = seed_mc(seed, mem)
    for _ in range(C.WARMUP if steps is None else steps):
        st = eng.step(st)
    return st


apply_history = IOMH.apply_history
advance = IOMH.advance
largest = IOMH.largest
entities = IOMH.entities
entity_mask = IOMH.entity_mask


def entity_memory(st, e=None):
    return IOMH.entity_memory(st, e)   # (m1, m2)


def entity_pm(st, e=None):
    m = entity_memory(st, e)
    return np.array([m[0] + m[1], m[0] - m[1]])   # (m_plus, m_minus)


def apply_cont_history(eng, st, p1, p2):
    """Two independent phase nutrient-drives (p1 early, p2 late), matched to the memory's two timescales:
    the SLOW component integrates ~ (p1+p2) and the FAST component tracks ~ p2, so (p1,p2) map to two
    independent memory coordinates. This is the natural high-cardinality history family for a 2-mode memory."""
    T = C.HIST_STEPS // 2
    cur = st.copy()
    for p in (p1, p2):
        for _ in range(T):
            cur.N = cur.N + p
            cur = eng.step(cur)
    return advance(eng, cur, C.SETTLE)


def _feat(st):
    e = largest(st)
    if e is None:
        return np.zeros(5)
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    mean_c = float(st.c[ys, xs].mean())
    return np.array([e.size, e.rg, e.specific_uptake, e.mass, mean_c])


def response_vector(eng, st):
    from ..sc_hmc import interventions as INT
    field, op, amp, dur = C.PROBE
    cur = st.copy(); out = []
    for t in range(1, C.PROBE_HORIZON + 1):
        if t <= dur:
            cur = INT._perturb(cur, field, op, amp)
        cur = eng.step(cur)
        if t % C.PROBE_CADENCE == 0:
            out.append(_feat(cur))
    return np.asarray(out) / np.array(C.RESP_SCALE)


def erase_memory(st):
    out = st.copy(); out.Mf = np.zeros_like(out.Mf); return out


def D(a, b):
    m = min(len(a), len(b))
    return float(np.linalg.norm((a[:m] - b[:m]).ravel()) / np.sqrt(m)) if m else 0.0
