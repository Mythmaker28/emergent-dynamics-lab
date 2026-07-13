"""The FROZEN factorized observer: A, S, F, L, M, G. Reported SEPARATELY. NEVER composited.

D-048 killed a scalar identity score: a single number was being asked five questions at once, and under component
replacement it said "different individual" because the MATERIAL changed. There is no composite here and there
never will be. `edlab/identity/gates.py` already forbids `theseus_score` / `memory_score`; this module keeps faith
with that.

Each head answers SAME / DIFFERENT / INDETERMINATE, and **correct abstention is a PASS**.
"""

from __future__ import annotations

import hashlib
import os
import pickle

import numpy as np

from ..substrates.life.fast import step
from ..substrates.life.library import OUT_ROW, PERIOD, settle, run_from, Arch
from .blind_a import blind_tomography, head_A, head_G, OBS

FFT_WIN = 120          # 2 grid periods -- an EXACT number, so the periodic average carries no sampling noise
F_TOL = 1e-6


# --------------------------------------------------------------------------- F: functional I/O relation
def f_signature(g0: np.ndarray, out_nodes) -> dict:
    """Per-OUTPUT-NODE |FFT| magnitude over a whole number of periods.

    PER-NODE, not on the total line: a delay edit shifts ONE channel in time, which changes the *superposition*
    on the total line while leaving every channel's own behaviour identical. Read on the total line, F would move
    on a pure delay edit -- and F would then be reporting an ARCHITECTURAL change, which is A's job.
    |FFT| discards phase, so this is cyclic-phase-invariant BY CONSTRUCTION, not by alignment."""
    frames = run_from(g0, OBS)
    line = np.stack([f[OUT_ROW] for f in frames]).astype(float)
    sig = {}
    for j, (lo, hi) in enumerate(out_nodes):
        s = line[-FFT_WIN:, lo:hi + 1].sum(1)
        m = np.abs(np.fft.rfft(s))
        sig[j] = m / (np.linalg.norm(m) + 1e-12)
    return sig


def head_F(s1: dict, s2: dict) -> str:
    if sorted(s1) != sorted(s2):
        return "DIFFERENT"                       # a different number of output channels is a different function
    for j in s1:
        if float(np.linalg.norm(s1[j] - s2[j])) > 0.05:
            return "DIFFERENT"
    return "SAME"


# --------------------------------------------------------------------------- M: material / microscopic continuity
def stationary_cells(g0: np.ndarray) -> set:
    """The matter that CONSTITUTES the machine (stationary), as opposed to the matter FLOWING through it."""
    acc = np.zeros(g0.shape, float)
    g = g0.copy()
    for _ in range(PERIOD):
        acc += g
        g = step(g)
    return {(int(r), int(c)) for r, c in zip(*np.nonzero(acc / PERIOD >= 0.25))}


def head_M(g1: np.ndarray, g2: np.ndarray, tol: float = 0.98) -> str:
    """Material continuity by Jaccard of the constituting matter. M is DELIBERATELY allowed to differ while A, S,
    F and L stay SAME -- that combination IS the Ship of Theseus, and a scalar observer had no way to say it."""
    a, b = stationary_cells(g1), stationary_cells(g2)
    if not a and not b:
        return "INDETERMINATE"
    j = len(a & b) / max(1, len(a | b))
    return "SAME" if j >= tol else "DIFFERENT"


# --------------------------------------------------------------------------- L: historical lineage
def head_L(w1: list, w2: list) -> str:
    """Three preregistered regimes (D-052, PRESERVED EXACTLY). Correct ABSTENTION passes; fabricated certainty
    fails. Two exact copies produce literally identical trajectories, so lineage is NOT identifiable from
    trajectories alone -- and saying so is the only honest answer."""
    if all(np.array_equal(x, y) for x, y in zip(w1, w2)):
        return "INDETERMINATE"                   # observationally identical: lineage is unknowable, full stop
    if np.array_equal(step(w1[-1]), w2[0]):
        return "SAME"                            # one continuous causal run
    return "DIFFERENT"


# --------------------------------------------------------------------------- the frozen observer
class FrozenObserver:
    """FROZEN at EXP-GT-03. Every constant below was DERIVED on development data and is declared here so that
    nothing can be silently retuned on a held-out case.

      A : blind interventional causal tomography, delay tolerance 0 (DERIVED: zero deviation across 8
          development nulls -- EXP-GT-A-CERT / D-055). Certified resolution: 4-step delay edit, 1 edge, 1 node.
      G : output-node SPACINGS (translation-invariant). Auxiliary. NEVER composited. G is NOT identity.
      F : per-node |FFT| magnitude over 2 exact periods.
      M : Jaccard of stationary (constituting) matter.
      L : continuity of the observed causal run; INDETERMINATE on observationally identical data.
      S : the certified stride-1 injection/deletion probe (D-051) is PRESERVED EXACTLY and is not re-derived here.
    """
    A_DELAY_TOL = 0          # DERIVED from the development null. NOT a free parameter.
    FROZEN_AT = "EXP-GT-03, 2026-07-13"

    CACHE = os.path.join("results", "_tomo_cache")

    def tomo(self, a: Arch, phase: int = 0):
        """Memoised on disk. The key is the circuit's COMPONENT SPEC + phase; the cached object is the DISCOVERED
        graph, never a label. Caching changes nothing scientific -- it lets a run resume."""
        os.makedirs(self.CACHE, exist_ok=True)
        spec = "|".join(f"{c.kind}@{c.row},{c.col}" for c in sorted(a.components, key=lambda c: (c.row, c.col)))
        key = hashlib.sha256(f"{spec}|ph{phase}".encode()).hexdigest()[:24]
        fp = os.path.join(self.CACHE, key + ".pkl")
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                return pickle.load(f)
        t = blind_tomography(settle(a, extra_phase=phase), OUT_ROW)
        with open(fp, "wb") as f:
            pickle.dump(t, f)
        return t

    def compare(self, a1: Arch, a2: Arch, ph1: int = 0, ph2: int = 0) -> dict:
        t1, t2 = self.tomo(a1, ph1), self.tomo(a2, ph2)
        g1, g2 = settle(a1, extra_phase=ph1), settle(a2, extra_phase=ph2)
        f1 = f_signature(g1, t1["out_nodes"])
        f2 = f_signature(g2, t2["out_nodes"])
        return {"A": head_A(t1, t2, self.A_DELAY_TOL),
                "G": head_G(t1, t2),
                "F": head_F(f1, f2),
                "M": head_M(g1, g2),
                "_t1": t1, "_t2": t2}
