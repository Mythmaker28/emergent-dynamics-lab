"""EXP-GT-00 -- ground-truth metrology for dynamic identity, on a Game-of-Life computational hierarchy.

The DISCOVERY OBSERVER receives ONLY raw cell-state trajectories.
The EVALUATOR retains the hidden ground truth: component locations, causal graph, memory contents, inputs,
outputs and program identity. It is NEVER passed to the observer.
"""

from __future__ import annotations

import numpy as np

from ..substrates.life.engine import blank, place, run, GLIDER_SE
from ..substrates.life.circuits import (build, simulate, output_series, Circuit,
                                        EATER_ROW, OUT_ROW, READ_FROM, _glider_track_col, H, W)

EATER_OFF = (-4, -3)                # FROZEN, verified: absorbs the stream and survives (positive control fires)
ARCH_TRAIN = ((5, 45, 85, 125),)                     # training architecture
ARCH_HELD_OUT = ((5, 50, 95, 140), (10, 46, 82, 118))  # HELD-OUT architectures (different spacings/layouts)
PROGRAMS = [(1, 1, 1, 1), (1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 0, 0), (0, 0, 1, 1), (1, 0, 0, 1), (0, 1, 1, 0)]


def make(arch, program) -> Circuit:
    return build(list(arch), list(program), eater_offsets={i: EATER_OFF for i in range(len(program))})


# ------------------------------------------------------------------ THE FROZEN DISCOVERY OBSERVER
# Sees ONLY frames. Uses the INTRINSIC axes set by the dynamics (glider propagation is +y+x), never the lab frame.
# EXCLUDED: absolute position (centroid removed), absolute orientation (intrinsic axes), total mass (normalized),
# entity count, radius, tracker ID.
U = np.array([1.0, 1.0]) / np.sqrt(2)      # intrinsic propagation axis
V = np.array([1.0, -1.0]) / np.sqrt(2)     # intrinsic transverse axis
N_BINS = 24
V_RANGE = (-90.0, 90.0)
FREQS = np.arange(1, 9)


def _persistent_sites(frames) -> np.ndarray:
    """Cells alive in >= 90% of frames: the still-life skeleton = the circuit's COMPONENTS (guns' stable parts,
    eaters). This is the observer's only window onto internal architecture, and it is inferred, not given."""
    stack = np.stack(frames).astype(np.float32)
    return (stack.mean(0) >= 0.9).astype(np.uint8)


def observe(frames) -> np.ndarray:
    fr = frames[READ_FROM:]
    pers = _persistent_sites(fr)
    ys, xs = np.nonzero(pers)
    if len(ys) == 0:
        prof = np.zeros(N_BINS)
    else:
        p = np.stack([ys, xs], 1).astype(float)
        p -= p.mean(0)                                  # TRANSLATION-INVARIANT
        v = p @ V                                        # project onto the INTRINSIC transverse axis
        prof, _ = np.histogram(v, bins=N_BINS, range=V_RANGE)
        prof = prof / (prof.sum() + 1e-9)                # MASS-INVARIANT
    pop = np.array([float(f.sum()) for f in fr])
    pop = (pop - pop.mean()) / (pop.std() + 1e-9)
    spec = np.abs(np.fft.rfft(pop))[FREQS]
    spec = spec / (np.linalg.norm(spec) + 1e-9)
    out = output_series(fr)
    o = (out - out.mean()) / (out.std() + 1e-9) if out.std() > 1e-9 else out * 0
    ac = np.array([float(np.corrcoef(o[:-l], o[l:])[0, 1]) if len(o) > l + 2 and o.std() > 1e-9 else 0.0
                   for l in (30, 60, 90)])
    ac = np.nan_to_num(ac)
    return np.concatenate([prof * 3.0, spec, ac])


def probe_response(c: Circuit, n_probe: int = 4) -> np.ndarray:
    """COUNTERFACTUAL validity, not visual similarity: inject a test glider into each channel's track and record
    how the OUTPUT changes. A representation that merely looks similar cannot fake this."""
    base = output_series(simulate(c))[READ_FROM:].sum()
    resp = []
    for i in range(n_probe):
        g = c.grid.copy()
        if i < len(c.gun_cols):
            row = EATER_ROW - 12
            col = _glider_track_col(c.gun_cols[i], row)
            if 0 < row < H - 5 and 0 < col < W - 5:
                place(g, GLIDER_SE, row, col)
        d = output_series(run(g, 700))[READ_FROM:].sum()
        resp.append((d - base) / (abs(base) + 1.0))
    return np.array(resp)


# ------------------------------------------------------------------ the five challenge classes
def replaced_run(c: Circuit, n_swaps: int = 3, steps: int = 700, gap: int = 6):
    """(e) PROGRESSIVE MICRO-COMPONENT REPLACEMENT under continuous function.

    CORRECTION (disclosed): my first version deleted an eater and re-placed an identical one at the SAME phase,
    which restores the exact grid -- 0/701 frames differed. It was a SILENT NO-OP and the challenge could not fire.
    The replacement must actually perturb the trajectory. It now removes the component, lets the channel run OPEN
    for `gap` steps (gliders genuinely leak through -- the component IS gone), then installs a fresh identical one.
    Function continues throughout (the other channels never stop); the material is replaced; identity must survive.
    """
    from ..substrates.life.engine import EATER1, step as life_step
    frames = [c.grid.copy()]
    g = c.grid.copy()
    sites = list(c.eater_sites)
    every = steps // (n_swaps + 1)
    pending: list[tuple[int, int, int]] = []
    for t in range(1, steps + 1):
        g = life_step(g)
        if sites and t % every == 0:
            i, ey, ex = sites[(t // every - 1) % len(sites)]
            g[ey:ey + 4, ex:ex + 4] = 0                 # component REMOVED -- the channel is now open
            pending.append((t + gap, ey, ex))
        for (tt, ey, ex) in list(pending):
            if t == tt:
                g[ey:ey + 4, ex:ex + 4] = 0
                place(g, EATER1, ey, ex)                # a FRESH identical component is installed
                pending.remove((tt, ey, ex))
        frames.append(g.copy())
    return frames


def challenge_suite() -> dict:
    A0 = ARCH_TRAIN[0]
    rep = {}
    for prog in PROGRAMS:
        rep[("A0", prog)] = observe(simulate(make(A0, prog)))
    for A in ARCH_HELD_OUT:
        for prog in PROGRAMS:
            rep[(f"H{A[1]}", prog)] = observe(simulate(make(A, prog)))
    # (d) exact copy with reset history: rebuilt from scratch, identical, no shared history
    copy_rep = observe(simulate(make(A0, (1, 0, 1, 0))))
    # (e) progressive micro-component replacement under continuous function
    swap_rep = observe(replaced_run(make(A0, (1, 0, 1, 0))))
    out = {}
    def d(a, b):
        return float(np.linalg.norm(a - b))
    ref = rep[("A0", (1, 0, 1, 0))]
    out["d_copy_reset_history"] = d(ref, copy_rep)                       # (d) must be ~0
    out["d_component_replacement"] = d(ref, swap_rep)                    # (e) must be small
    out["d_same_arch_diff_program_same_output"] = d(ref, rep[("A0", (0, 1, 0, 1))])   # (c) must be LARGE
    out["d_same_arch_diff_program_other"] = d(ref, rep[("A0", (1, 1, 0, 0))])         # (a)/(c) must be LARGE
    out["d_same_arch_diff_output"] = d(ref, rep[("A0", (1, 1, 1, 1))])                # (a) must be LARGE
    out["d_diff_arch_same_program"] = d(ref, rep[("H50", (1, 0, 1, 0))])              # (b) must be > 0
    out["reps"] = {f"{k[0]}|{''.join(map(str,k[1]))}": v.tolist() for k, v in rep.items()}
    return out
