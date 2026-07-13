"""EXP-GT-01 -- FACTORIZED ground-truth identity metrology (A / S / F / L / M). Heads are NEVER collapsed.

Protocol: docs/experiments/EXP_GT_01_PROTOCOL.md (SHA d3ac99b316a235207422519fd36978034ee42f97), frozen first.
EXP-GT-00's observer and results are preserved unchanged (edlab/experiments/exp_gt_00.py).
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.engine import blank, place, run, step as life_step, GLIDER_SE, EATER1
from ..substrates.life.circuits import (build, simulate, output_series, Circuit, EATER_ROW, READ_FROM,
                                        _glider_track_col, H, W, STEPS)
from .exp_gt_00 import EATER_OFF, make, ARCH_TRAIN, ARCH_HELD_OUT

# ---- replacement implementations: functionally equivalent, MICROSCOPICALLY DISTINCT ----
IMPL_DEV = 24          # development: the relief eater sits 24 rows downstream
IMPL_HELD_OUT = 12     # HELD-OUT implementation, never used in development.
# NOTE (disclosed): my first held-out value was 36, which puts the relief at row 71 -- BELOW the output line at
# row 70. Gliders then cross the output before being absorbed and assertion (iii) fails. The assertion caught a
# broken implementation, which is what assertions are for. Both reliefs must sit upstream of OUT_ROW.


def handoff_run(c: Circuit, channel: int, downstream: int, t_install: int = 260, t_remove: int = 300,
                steps: int = STEPS):
    """E1 -- FUNCTION-PRESERVING HANDOFF (the real Ship-of-Theseus gate).

    A glider translates (+1,+1) every 4 steps, so an eater that absorbs at (ey, ex) also absorbs at
    (ey+d, ex+d): the relief is a *functionally equivalent, microscopically distinct* implementation of the gate.
    The relief is INSTALLED BEFORE the incumbent is REMOVED, so the gate is never unmanned and the output is
    identical at every timestep -- no silent interval.
    """
    site = next((s for s in c.eater_sites if s[0] == channel), None)
    if site is None:
        raise ValueError("channel carries no component to hand off")
    _, ey, ex = site
    ny, nx = ey + downstream, ex + downstream
    g = c.grid.copy()
    frames = [g.copy()]
    for t in range(1, steps + 1):
        g = life_step(g)
        if t == t_install:
            place(g, EATER1, ny, nx)                       # relief installed FIRST
        if t == t_remove:
            g[ey:ey + 4, ex:ex + 4] = 0                    # incumbent removed; gate never unmanned
        frames.append(g.copy())
    return frames, (ey, ex), (ny, nx)


def damage_repair_run(c: Circuit, channel: int, gap: int = 40, t0: int = 260, steps: int = STEPS):
    """E2 -- DAMAGE AND REPAIR. Function BREAKS (gliders leak) and is then restored. NOT the Ship-of-Theseus gate."""
    site = next((s for s in c.eater_sites if s[0] == channel), None)
    _, ey, ex = site
    g = c.grid.copy()
    frames = [g.copy()]
    for t in range(1, steps + 1):
        g = life_step(g)
        if t == t0:
            g[ey:ey + 4, ex:ex + 4] = 0
        if t == t0 + gap:
            g[ey:ey + 4, ex:ex + 4] = 0
            place(g, EATER1, ey, ex)
        frames.append(g.copy())
    return frames


# ---------------------------------------------------------------- THE OBSERVER (raw cells + blinded actions only)
PROBE_ROW = EATER_ROW - 14           # upstream of every gate
PROBE_COLS = tuple(range(20, W - 60, 20))   # BLINDED candidate sites: a bare grid, no labels, no knowledge
FP_STEPS = 480      # a pulse injected at PROBE_ROW (21) needs 4*(70-21) = 196 steps to reach the output line.
                    # 480 gives ample margin; running the full 700 for every probe was pure waste.


def _out(frames):
    return output_series(frames)


def causal_fingerprint(grid: np.ndarray) -> dict:
    """Blinded counterfactual micro-perturbation: inject a standardized pulse at each UNLABELED candidate site and
    record its TIME-LAGGED influence on the output. No component positions, labels, program bits or causal graph."""
    base = _out(run(grid, FP_STEPS))
    infl, lat = [], []
    for col in PROBE_COLS:
        g = grid.copy()
        if 0 < PROBE_ROW < H - 5 and 0 < col < W - 5:
            place(g, GLIDER_SE, PROBE_ROW, col)
        d = _out(run(g, FP_STEPS)) - base
        mag = float(np.abs(d).sum())
        nz = np.nonzero(np.abs(d) > 0)[0]
        infl.append(mag)
        lat.append(float(nz[0]) if len(nz) else -1.0)
    infl = np.array(infl)
    lat = np.array(lat)
    active = infl > (0.15 * infl.max() if infl.max() > 0 else 1e9)     # channels that CAUSALLY reach the output
    return {"influence": infl, "latency": lat, "active": active,
            "n_causal": int(active.sum()),
            "latencies_active": np.sort(lat[active]) if active.any() else np.array([]),
            "passive_out": base}


def persistent_skeleton(frames) -> np.ndarray:
    stack = np.stack(frames[READ_FROM:]).astype(np.float32)
    return (stack.mean(0) >= 0.9).astype(np.uint8)


# ---------------------------------------------------------------- THE FIVE HEADS (never combined)
def head_A(f1, f2) -> float:
    """Causal ARCHITECTURE: how many causal channels, and with what propagation latencies."""
    a, b = f1["latencies_active"], f2["latencies_active"]
    if len(a) != len(b):
        return 1.0
    if len(a) == 0:
        return 0.0
    return float(np.abs(a - b).mean() / 100.0)


def head_S(f1, f2) -> float:
    """PROGRAM / MEMORY: WHICH candidate sites causally reach the output. A pulse into a gated channel is absorbed
    and never arrives; into an open channel it does. This reads the memory word WITHOUT being told the bits."""
    return float(np.mean(f1["active"] != f2["active"]))


def head_F(f1, f2) -> float:
    """FUNCTIONAL I/O: the passive output signature an external observer sees, without injecting anything."""
    a, b = f1["passive_out"], f2["passive_out"]
    n = min(len(a), len(b))
    d = np.abs(a[:n].sum() - b[:n].sum()) / (max(a[:n].sum(), b[:n].sum()) + 1e-9)
    return float(d)


def head_M(sk1, sk2) -> float:
    """MICROSCOPIC / MATERIAL: which cells actually implement the components. E1 MUST change this."""
    inter = float((sk1 & sk2).sum())
    union = float((sk1 | sk2).sum())
    return 1.0 - inter / (union + 1e-9)


def head_L(frames1_last: np.ndarray, frames2_first: np.ndarray) -> dict:
    """HISTORICAL LINEAGE: is there one continuous causal run connecting the two windows?
    Decidable ONLY by continuity. For an EXACT COPY at the same phase the trajectories are literally identical and
    L is NOT identifiable -- the head must REPORT INDETERMINACY, not guess."""
    continues = bool(np.array_equal(life_step(frames1_last), frames2_first))
    identical = bool(np.array_equal(frames1_last, frames2_first))
    return {"continuous": continues, "identifiable": not identical,
            "verdict": "same-lineage" if (continues and not identical) else
                       ("INDETERMINATE (exact copy: trajectories identical)" if identical else "different-lineage")}
