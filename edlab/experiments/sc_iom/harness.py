"""Harness: seed IOMState (memory=0), warm up, apply experience histories, read memory + causal response.
Reuses the frozen detector (IOMState is duck-compatible: has rho, sigma(), C, uptake)."""
from __future__ import annotations

import numpy as np

from ...substrates.scaffold.observables import detect
from ...substrates.scaffold.engine import ScaffoldEngine
from .engine import MemoryScaffoldEngine, IOMState, MemParams
from . import config as C


def seed_iom(seed: int, mem: MemParams = None) -> IOMState:
    s = C.seed_state(C.SPEC, C.TRACER, seed, "random")
    k = (mem or C.MEM).n_comp
    Mf = np.zeros((k, C.SPEC.size, C.SPEC.size))     # ALL entities start with memory 0 (no tag)
    return IOMState(s.rho, s.U, s.V, s.c, s.N, s.C, s.uptake, Mf, 0)


def mem_engine(mem: MemParams = None) -> MemoryScaffoldEngine:
    return MemoryScaffoldEngine(C.SPEC, mem or C.MEM, C.TRACER)


def frozen_engine() -> ScaffoldEngine:
    return ScaffoldEngine(C.SPEC, C.TRACER)


def warmup(seed: int, mem: MemParams = None, steps: int = None) -> IOMState:
    eng = mem_engine(mem)
    st = seed_iom(seed, mem)
    for _ in range(C.WARMUP if steps is None else steps):
        st = eng.step(st)
    return st


def apply_history(eng, st: IOMState, history) -> IOMState:
    cur = st.copy()
    for label, steps, dN, dc in history:
        for _ in range(steps):
            if dN:
                cur.N = cur.N + dN
            if dc:
                cur.c = cur.c + dc
            cur = eng.step(cur)
    return cur


def advance(eng, st: IOMState, steps: int) -> IOMState:
    cur = st.copy()
    for _ in range(steps):
        cur = eng.step(cur)
    return cur


def entities(st):
    return detect(st, C.DET, C.SPEC.rho_max)


def largest(st):
    es = entities(st)
    return max(es, key=lambda e: e.size) if es else None


def entity_mask(st, e):
    m = np.zeros(st.rho.shape, dtype=bool)
    m[e.cells[:, 0], e.cells[:, 1]] = True
    return m


def entity_memory(st, e=None) -> np.ndarray:
    """Mass-weighted mean memory over the largest entity -> (m1, m2). Privileged diagnostic only."""
    e = largest(st) if e is None else e
    if e is None:
        return np.zeros(st.Mf.shape[0])
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    w = st.rho[ys, xs]
    m = st.mem()
    return np.array([np.average(m[k][ys, xs], weights=w) for k in range(m.shape[0])])


def entity_memory_field(st, e=None, grid=4) -> np.ndarray:
    """Coarse spatial memory descriptor over the entity (grid x grid x n_comp), centroid-aligned,
    for dimensionality/individuation analysis. Privileged diagnostic only; never an identity tag."""
    e = largest(st) if e is None else e
    if e is None:
        return np.zeros(grid * grid * st.Mf.shape[0])
    n = st.rho.shape[0]
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    cen = e.centroid
    dy = ((ys - cen[0] + n / 2) % n - n / 2); dx = ((xs - cen[1] + n / 2) % n - n / 2)
    rgy = max(dy.max() - dy.min(), 1e-6); rgx = max(dx.max() - dx.min(), 1e-6)
    gy = np.clip(((dy - dy.min()) / rgy * grid).astype(int), 0, grid - 1)
    gx = np.clip(((dx - dx.min()) / rgx * grid).astype(int), 0, grid - 1)
    m = st.mem()
    out = []
    for k in range(m.shape[0]):
        acc = np.zeros((grid, grid)); cnt = np.zeros((grid, grid))
        vals = m[k][ys, xs]
        for a, b, val in zip(gy, gx, vals):
            acc[a, b] += val; cnt[a, b] += 1
        out.append((acc / np.maximum(cnt, 1)).ravel())
    return np.concatenate(out)
