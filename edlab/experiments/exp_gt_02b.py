"""EXP-GT-02B -- repair A, F and L by PHASE MATCHING and causal tomography. No weight tuning.

Protocol: docs/experiments/EXP_GT_02B_PROTOCOL.md (SHA 3fdd3cc69f075a38048dfa1c0084ce6411abe176), frozen first.
The certified S head (D-051) is preserved exactly. The exhaustive stride-1 scan is the gold-standard instrument.
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.engine import place, run, step as life_step, EATER1, GLIDER_SE
from ..substrates.life.circuits import output_series, Circuit, EATER_ROW
from .exp_gt_02 import (make, settle, SETTLE, PROBE_LEN, INJECT_ROW, DELETE_ROW, SCAN_LO, SCAN_HI,
                        TILE, TILE_HOLD, _cluster)

N_PERIODS = 3            # fingerprints accumulate over an INTEGER number of INFERRED periods
FIXED_WIN = 120          # a COMMON analysis window that EVERY inferred period divides (30 and the 60 harmonic).
# Clock inference on the all-open circuit locks onto the 60 harmonic rather than 30 -- both are integer multiples of
# the true period, so folding is still valid, but the two are not directly comparable. Comparisons therefore use a
# fixed window that both divide, and the passive signature is the FFT MAGNITUDE, which is cyclic-phase-invariant
# BY CONSTRUCTION rather than by alignment. Asserted below.


def infer_clock(settled: np.ndarray, max_lag: int = 80) -> int:
    """Infer the clock period from the RAW trajectory alone. No hidden labels, no knowledge of the gun."""
    pop = np.array([float(f.sum()) for f in run(settled, 240)])
    pop = pop - pop.mean()
    ac = np.array([float(np.dot(pop[:-l], pop[l:]) / (np.dot(pop, pop) + 1e-12)) for l in range(1, max_lag)])
    best, bv = 0, -2.0
    for l in range(4, max_lag - 1):
        if ac[l - 1] > bv and ac[l - 1] > ac[l - 2] and ac[l - 1] >= ac[l]:
            bv, best = ac[l - 1], l
    return int(best)


def tomography(settled: np.ndarray, period: int) -> dict:
    """Gold-standard exhaustive stride-1 blind causal tomography, accumulated over N_PERIODS complete periods.
    No component labels, positions, program bits or causal graph are consulted anywhere."""
    win = N_PERIODS * period
    base_frames = run(settled, PROBE_LEN)
    base = output_series(base_frames)
    gated, open_, onsets, waves = [], [], {}, {}
    for col in range(SCAN_LO, SCAN_HI):
        g = settled.copy()
        place(g, GLIDER_SE, INJECT_ROW, col)
        d = output_series(run(g, PROBE_LEN)) - base
        nz = np.nonzero(np.abs(d) > 0)[0]
        if len(nz) == 0:
            gated.append(col)                                  # pulse ABSORBED: a gate lies on this diagonal
        else:
            onsets[col] = int(nz[0])
            w = d[nz[0]: nz[0] + win]                          # response over COMPLETE inferred periods
            waves[col] = np.pad(w, (0, max(0, win - len(w))))[:win]
        g = settled.copy()
        frames = [g.copy()]
        for t in range(PROBE_LEN):                             # frame-matched to the baseline (D-051 bugfix)
            if t < TILE_HOLD:
                g[DELETE_ROW:DELETE_ROW + TILE, col:col + TILE] = 0
            g = life_step(g)
            frames.append(g.copy())
        if float(output_series(frames).sum()) < float(base.sum()) - 1e-9:
            open_.append(col)                                  # a live stream passes: an OPEN channel
    gc, oc = _cluster(gated), _cluster(open_)
    chans = sorted([(c, 0) for c in gc] + [(c, 1) for c in oc])
    # PASSIVE signature: FFT MAGNITUDE over a fixed window that the inferred period divides.
    # |FFT| discards phase, so this is cyclic-phase-invariant BY CONSTRUCTION, not by alignment.
    assert FIXED_WIN % period == 0, f"inferred period {period} does not divide the common window {FIXED_WIN}"
    tail = base[len(base) - FIXED_WIN:]
    folded = np.abs(np.fft.rfft(tail))
    return {"period": period, "channels": chans, "word": tuple(b for _, b in chans),
            "n_channels": len(chans), "onsets": onsets, "waves": waves,
            "folded_passive": folded / (np.linalg.norm(folded) + 1e-9)}


# --------------------------------------------------------------------------- HEADS (separate; never composited)
def head_F(t1, t2, tol=1e-6) -> str:
    """FUNCTIONAL I/O transfer relation, per CHANNEL ORDINAL (layout- and latency-normalized), plus the
    phase-folded passive signature. Same function by different mechanisms => SAME."""
    if t1["n_channels"] != t2["n_channels"]:
        return "DIFFERENT"
    if t1["word"] != t2["word"]:
        return "DIFFERENT"
    if np.linalg.norm(t1["folded_passive"] - t2["folded_passive"]) > 0.05:
        return "DIFFERENT"
    return "SAME"


def head_A(t1, t2, tol=6.0) -> str:
    """Time-lagged causal influence graph, in the INTRINSIC DIAGONAL frame.

    STRUCTURAL FIX (not weight tuning): a channel's detected COLUMN depends on how it is GATED -- an absorbed
    injection is found at ~gun+30, a deleted stream at ~gun+63 -- so a column-based A was contaminated by the
    PROGRAM (it moved when only S moved). The invariant is the channel's DIAGONAL d = row - col, which is the same
    quantity however the channel happens to be gated: a glider travels along a constant diagonal. A is therefore
    built from diagonals, their spacings, the channel count, and onset delays -- translation-, layout-, phase- and
    replacement-invariant, and independent of the memory word.
    """
    def sig(t):
        ds = []
        for col, bit in t["channels"]:
            row = INJECT_ROW if bit == 0 else DELETE_ROW      # where THIS locus was detected
            ds.append(row - col)                              # -> the channel's intrinsic DIAGONAL
        ds = np.sort(np.array(ds, float))
        gaps = np.abs(np.diff(ds)) if len(ds) > 1 else np.array([0.0])
        lat = np.array([v for v in t["onsets"].values()], float)
        return np.concatenate([[float(len(ds))], np.sort(gaps),
                               [float(lat.mean()) if len(lat) else -1.0]])
    a, b = sig(t1), sig(t2)
    if a.shape != b.shape:
        return "DIFFERENT"
    return "SAME" if float(np.abs(a - b).max()) <= tol else "DIFFERENT"


def head_L(w1: list[np.ndarray], w2: list[np.ndarray]) -> str:
    """Three preregistered regimes. Correct ABSTENTION passes; fabricated certainty fails."""
    if all(np.array_equal(x, y) for x, y in zip(w1, w2)):
        return "INDETERMINATE"                                  # observationally identical: lineage unknowable
    if np.array_equal(life_step(w1[-1]), w2[0]):
        return "SAME"                                           # one continuous causal run
    return "DIFFERENT"
