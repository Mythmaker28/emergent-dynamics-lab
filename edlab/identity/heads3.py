"""The V3 factorized observer: A_TOPO, A_TAU, G, S, F, L, M. Reported SEPARATELY. NEVER composited."""

from __future__ import annotations

import numpy as np

from ..substrates.life.fast import step
from ..substrates.life.library import OUT_ROW, settle, run_from, Arch
from .blind_a3 import (cached_tomography, head_A_TOPO, head_A_TAU, head_G, infer_period, OBS)

FFT_WIN = 120


# --------------------------------------------------------------------------- F
def f_signature(g0, out_nodes) -> dict:
    """PER-OUTPUT-NODE |FFT| magnitude. Per-node, not on the total line: a delay edit shifts ONE channel in time,
    changing the superposition on the total line while leaving every channel's own behaviour identical. Read on
    the total line, F would move on a pure delay edit -- and F would then be reporting a TIMING-ARCHITECTURE
    change, which is A_TAU's job. |FFT| discards phase, so this is cyclic-phase-invariant BY CONSTRUCTION."""
    frames = run_from(g0, OBS)
    line = np.stack([f[OUT_ROW] for f in frames]).astype(float)
    sig = {}
    for j, (lo, hi) in enumerate(out_nodes):
        s = line[-FFT_WIN:, lo:hi + 1].sum(1)
        m = np.abs(np.fft.rfft(s))
        sig[j] = m / (np.linalg.norm(m) + 1e-12)
    return sig


def head_F(s1, s2) -> str:
    if sorted(s1) != sorted(s2):
        return "DIFFERENT"
    return "SAME" if all(float(np.linalg.norm(s1[j] - s2[j])) <= 0.05 for j in s1) else "DIFFERENT"


# --------------------------------------------------------------------------- M
def stationary_cells(g0) -> set:
    T = infer_period(g0)
    acc = np.zeros(g0.shape, float)
    g = g0.copy()
    for _ in range(T):
        acc += g
        g = step(g)
    return {(int(r), int(c)) for r, c in zip(*np.nonzero(acc / T >= 0.25))}


def head_M(g1, g2, tol=0.98) -> str:
    """M is DELIBERATELY allowed to differ while A, S, F and L stay SAME. That combination IS the Ship of
    Theseus, and a scalar observer had no way to say it -- it said 'different individual' (D-048)."""
    a, b = stationary_cells(g1), stationary_cells(g2)
    if not a and not b:
        return "INDETERMINATE"
    j = len(a & b) / max(1, len(a | b))
    return "SAME" if j >= tol else "DIFFERENT"


# --------------------------------------------------------------------------- L (PRESERVED EXACTLY from D-052)
def head_L(w1, w2) -> str:
    if all(np.array_equal(x, y) for x, y in zip(w1, w2)):
        return "INDETERMINATE"        # observationally identical: lineage is not identifiable, and saying so is
    if np.array_equal(step(w1[-1]), w2[0]):      # the only honest answer
        return "SAME"
    return "DIFFERENT"


# --------------------------------------------------------------------------- S (certified probe, D-051)
def head_S(g1, g2) -> str:
    """The CERTIFIED stride-1 blind injection/deletion probe (D-051), PRESERVED EXACTLY. Not re-derived, not
    retuned. It reads the memory word; two circuits with the same word score SAME."""
    from ..experiments.exp_gt_02 import blind_scan, read_memory
    w1, w2 = read_memory(blind_scan(g1)), read_memory(blind_scan(g2))
    if w1["n_channels"] != w2["n_channels"]:
        return "DIFFERENT"
    return "SAME" if w1["word"] == w2["word"] else "DIFFERENT"


# --------------------------------------------------------------------------- the frozen observer
class ObserverV3:
    """FROZEN at EXP-GT-03R. Every constant was DERIVED on development data and is declared here.

      A_TOPO : causal topology, modulo isomorphism. NO delays, NO geometry enter it.
      A_TAU  : edge-delay structure vs the inferred clock. Compared ONLY after the topology matches.
      G      : layout. Auxiliary. NEVER composited. G is NOT identity.
      S      : the certified D-051 probe, preserved exactly.
      F      : per-node |FFT| over 2 exact periods.
      L      : continuity of the observed run; INDETERMINATE on observationally identical data.
      M      : Jaccard of the constituting (stationary) matter.
    """
    TAU_TOL = 0.0                 # DERIVED from the independent phase null (Certificate V2). NOT a free parameter.
    FROZEN_AT = "EXP-GT-03R, 2026-07-14"

    def tomo(self, a: Arch, phase: int = 0, region=None):
        return cached_tomography(settle(a, extra_phase=phase), OUT_ROW, region=region)

    def compare(self, a1: Arch, a2: Arch, ph1=0, ph2=0, with_S=False) -> dict:
        t1, t2 = self.tomo(a1, ph1), self.tomo(a2, ph2)
        g1, g2 = settle(a1, extra_phase=ph1), settle(a2, extra_phase=ph2)
        r = {"A_TOPO": head_A_TOPO(t1, t2),
             "A_TAU": head_A_TAU(t1, t2, self.TAU_TOL),
             "G": head_G(t1, t2),
             "F": head_F(f_signature(g1, t1["out_nodes"]), f_signature(g2, t2["out_nodes"])),
             "M": head_M(g1, g2)}
        if with_S:
            r["S"] = head_S(g1, g2)
        r["_t1"], r["_t2"] = t1, t2
        return r
