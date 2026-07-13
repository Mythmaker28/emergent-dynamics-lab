"""Conway's Game of Life (B3/S23), exact, on a bounded grid with dead borders.

Ground-truth metrology substrate (EXP-GT-00). Deterministic, discrete, and completely known -- which is the point:
here we possess the truth (component locations, causal graph, memory contents, program identity) and can therefore
ask whether a discovery observer that sees ONLY raw cell states can recover identity. Any representation that cannot
pass here has no business being trusted on a droplet.
"""

from __future__ import annotations

import numpy as np


def step(g: np.ndarray) -> np.ndarray:
    n = np.zeros_like(g, dtype=np.int8)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            n += np.roll(np.roll(g, dy, 0), dx, 1).astype(np.int8)
    # dead border: rolling wraps, so zero the frame afterwards (patterns are kept away from the edge)
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


# ---------------------------------------------------------------- verified component library
GLIDER_SE = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]          # travels +y,+x (south-east), period 4, disp (1,1)
BLOCK = [(0, 0), (0, 1), (1, 0), (1, 1)]                       # still life
EATER1 = [(0, 0), (0, 1), (1, 0), (1, 2), (2, 2), (3, 2), (3, 3)]   # fishhook: absorbs a SE glider cleanly
GOSPER_GUN = [
    (0, 24),
    (1, 22), (1, 24),
    (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
    (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
    (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
    (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
    (6, 10), (6, 16), (6, 24),
    (7, 11), (7, 15),
    (8, 12), (8, 13),
]


def place(g: np.ndarray, cells, oy: int, ox: int) -> np.ndarray:
    for y, x in cells:
        g[oy + y, ox + x] = 1
    return g


def blank(h: int, w: int) -> np.ndarray:
    return np.zeros((h, w), dtype=np.uint8)
