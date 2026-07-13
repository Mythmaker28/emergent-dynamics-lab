"""EXP-GT-02 -- INSTRUMENT REPAIR. Observability contract + coverage-certified blind probes + phase matching.

Protocol: docs/experiments/EXP_GT_02_PROTOCOL.md (SHA ca9a0c5a76fb77aab67d5bb5f8083231d0a2bcf1), frozen first.
Observer v2 (exp_gt_01.py) and its failures are preserved unchanged.

Every head can output SAME / DIFFERENT / INDETERMINATE. Correct abstention is a PASS; fabricating a relation the
data cannot support is a FAILURE. No scalar composite, ever.
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.engine import place, run, step as life_step, GLIDER_SE
from ..substrates.life.circuits import build, output_series, Circuit, EATER_ROW, OUT_ROW, H, W
from .exp_gt_00 import EATER_OFF

SETTLE = 400            # every configuration is re-settled to a common, fully-established state before probing
PROBE_LEN = 280         # a pulse at INJECT_ROW needs 4*(70-21) = 196 steps to reach the output line
INJECT_ROW = 21         # UPSTREAM of the gates
DELETE_ROW = 55         # DOWNSTREAM of the gates, UPSTREAM of the output
SCAN_LO, SCAN_HI = 20, 200      # exhaustive stride-1 blind scan; no component labels, positions or bits are used
TILE = 5
TILE_HOLD = 8           # >= 2 glider periods: no clock phase can hide a stream from the deletion probe
CLOCK = 30              # the gun period; fingerprints are accumulated over a COMPLETE clock period


def make(arch, program) -> Circuit:
    return build(list(arch), list(program), eater_offsets={i: EATER_OFF for i in range(len(program))})


def settle(c: Circuit) -> np.ndarray:
    g = c.grid.copy()
    for _ in range(SETTLE):
        g = life_step(g)
    return g


def _out_sum(g0: np.ndarray, steps: int = PROBE_LEN) -> float:
    return float(output_series(run(g0, steps)).sum())


def blind_scan(settled: np.ndarray) -> dict:
    """COVERAGE-CERTIFIED blind probing. Exhaustive stride-1. No hidden labels are consulted anywhere.

    INJECTION (upstream): a standardized glider pulse. It is ABSORBED iff its diagonal meets a gate ->
        columns with ZERO output change mark GATED channels.
    DELETION (downstream): a blind 5x5 tile cleared for 8 consecutive steps (>= 2 glider periods, so no clock
        phase can hide a stream) -> the output DROPS iff a live stream passes -> marks OPEN channels.
    """
    base = _out_sum(settled)
    inj_absorbed, del_open = [], []
    for col in range(SCAN_LO, SCAN_HI):
        g = settled.copy()
        place(g, GLIDER_SE, INJECT_ROW, col)
        if abs(_out_sum(g) - base) < 1e-9:
            inj_absorbed.append(col)                  # the pulse never arrived: a GATE lies on this diagonal
        # BUGFIX (disclosed): the deletion arm must be summed over the SAME NUMBER OF FRAMES as the baseline.
        # The first draft summed 272 frames against a 281-frame baseline, so the output "dropped" at EVERY column
        # -- including empty space. That is an accounting artefact, not a signal, and it made the probe fire
        # everywhere. Both arms now cover exactly PROBE_LEN + 1 frames.
        g = settled.copy()
        frames = [g.copy()]
        for t in range(PROBE_LEN):
            if t < TILE_HOLD:
                g[DELETE_ROW:DELETE_ROW + TILE, col:col + TILE] = 0
            g = life_step(g)
            frames.append(g.copy())
        rest = float(output_series(frames).sum())
        if rest < base - 1e-9:
            del_open.append(col)                      # a live stream passed through: an OPEN channel
    return {"base": base, "gated_cols": inj_absorbed, "open_cols": del_open}


def _cluster(cols, gap=6):
    out, cur = [], []
    for c in sorted(cols):
        if cur and c - cur[-1] > gap:
            out.append(int(np.mean(cur))); cur = []
        cur.append(c)
    if cur:
        out.append(int(np.mean(cur)))
    return out


def read_memory(scan: dict) -> dict:
    """Channels = gated loci UNION open loci, ordered by transverse coordinate -> LAYOUT-INVARIANT memory word."""
    gated = _cluster(scan["gated_cols"])
    open_ = _cluster(scan["open_cols"])
    chans = sorted([(c, 0) for c in gated] + [(c, 1) for c in open_])
    return {"n_channels": len(chans), "word": tuple(b for _, b in chans),
            "channel_cols": tuple(c for c, _ in chans), "gated": gated, "open": open_}
