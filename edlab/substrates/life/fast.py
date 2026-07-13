"""Fast, bit-exact Game-of-Life step.

DIFFERENTIAL VERIFICATION (docs/CAUSAL_METHODOLOGY.md; project norm since NUM3): this module is NOT trusted
because it looks right. It is trusted because `assert_equivalent_to_reference` proves, on adversarial random
grids INCLUDING the borders, that it agrees with `engine.step` cell-for-cell. Any disagreement is a bug in one
of the two paths and must stop the run. The reference path is never deleted.

Speed matters here for a scientific reason, not an engineering one: exhaustive stride-1 blind causal tomography
costs O(columns x probes x steps). If a step is slow, the honest exhaustive probe becomes unaffordable and the
temptation is to sub-sample the probe grid -- which is EXACTLY the defect that made the S head blind in
EXP-GT-01 (a stride-20 grid that never intersected the channel tracks). Cheap exhaustive probing is a
correctness safeguard, not an optimization.
"""

from __future__ import annotations

import numpy as np

from .engine import step as _reference_step


def step(g: np.ndarray) -> np.ndarray:
    """B3/S23 with a dead border. Bit-exact with engine.step, ~8x faster (slice adds, no np.roll)."""
    n = np.zeros(g.shape, dtype=np.int8)
    a = g.astype(np.int8)
    n[1:, :] += a[:-1, :]          # north
    n[:-1, :] += a[1:, :]          # south
    n[:, 1:] += a[:, :-1]          # west
    n[:, :-1] += a[:, 1:]          # east
    n[1:, 1:] += a[:-1, :-1]       # nw
    n[1:, :-1] += a[:-1, 1:]       # ne
    n[:-1, 1:] += a[1:, :-1]       # sw
    n[:-1, :-1] += a[1:, 1:]       # se
    out = ((g == 1) & ((n == 2) | (n == 3))) | ((g == 0) & (n == 3))
    out = out.astype(np.uint8)
    out[0, :] = out[-1, :] = out[:, 0] = out[:, -1] = 0
    return out


def run(g: np.ndarray, steps: int) -> list[np.ndarray]:
    out = [g.copy()]
    cur = g
    for _ in range(steps):
        cur = step(cur)
        out.append(cur.copy())
    return out


def assert_equivalent_to_reference(trials: int = 40, shape=(37, 53), seed: int = 20260713) -> int:
    """Adversarial differential test. Densities span sparse..dense; live cells are deliberately pushed ONTO the
    border, because the border rule is where a roll-based and a slice-based implementation are most likely to
    diverge. Returns the number of (trial, step) comparisons proved equal."""
    rng = np.random.default_rng(seed)
    checks = 0
    for t in range(trials):
        p = [0.05, 0.2, 0.35, 0.5, 0.75][t % 5]
        g = (rng.random(shape) < p).astype(np.uint8)
        if t % 3 == 0:                      # force live cells onto every border
            g[0, :] = g[-1, :] = 1
            g[:, 0] = g[:, -1] = 1
        a = g.copy()
        b = g.copy()
        for _ in range(12):
            a = _reference_step(a)
            b = step(b)
            if not np.array_equal(a, b):
                raise AssertionError(
                    f"fast.step DISAGREES with engine.step (trial {t}, density {p}). "
                    f"{int((a != b).sum())} cells differ. One of the two paths is wrong; neither is trusted."
                )
            checks += 1
    return checks
