"""SPATIALLY EMBEDDED BOOLEAN NETWORK -- the second ground-truth world (Phase 1D).

CHOSEN, NOT DEFAULTED TO. The Game-of-Life library cannot express three properties the mission requires, and one
preregistered development cycle confirmed it (D-062):
  * PROGRAM != ARCHITECTURE -- a GoL memory bit is an EATER that is ADDED or REMOVED, so setting a bit adds a node
    and two edges. The program IS the architecture.
  * FEEDBACK -- in every measured tomography the component->component dependency graph has edges OUT of guns and
    NONE INTO any gun. A cycle needs an edge into a source. Guns are sources. There is no cycle, and two
    mutually-inhibiting glider streams do not latch: annihilation is symmetric, so both go off.
  * HELD-OUT IMPLEMENTATION -- every candidate absorber either destroys its neighbour in context or is a reactive
    seed whose declared component is empty at settle.

The mission is explicit: do not weaken the requirements to remain in Game of Life. So the world changes.

WHAT IS PRESERVED, and it is everything that matters: a discrete synchronous microscopic state; signals that
PROPAGATE and therefore have velocities and delays; a clock; spatial embedding; stationary components; exact hidden
ground truth; and clamp interventions. The causal ontology (A_TOPO / A_TAU / G / S / F / L / M, never composited),
the observability contract, the admission layer and the phase-quotient discipline all carry over verbatim.

WHAT IS GAINED:
  * MEMORY IS A STATE OF FIXED WIRING. A register cell holds a bit: next = we ? data : self. The wiring never
    changes; the PROGRAM is the registers' initial contents. Same graph, four programs.
  * FEEDBACK IS REAL. The register's self-loop IS a directed cycle. Break the edge and the recurrence dies.
  * DELAY IS PATH LENGTH. A signal advances one cell per step, so re-routing a wire is a pure A_TAU edit with
    A_TOPO fixed -- the cleanest possible separation of timing from topology.

THE OBSERVER SEES ONLY THE BINARY CELL GRID. Types, wiring, ops, register contents and the graph are EVALUATOR-ONLY
and are never passed to any head.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ---- cell ops (EVALUATOR-ONLY; the observer never sees these)
OFF, WIRE, CLK, NOT, AND, OR, XOR, REG, CONST1 = range(9)
OP_NAMES = {OFF: "off", WIRE: "wire", CLK: "clk", NOT: "not", AND: "and", OR: "or",
            XOR: "xor", REG: "reg", CONST1: "const1"}


@dataclass
class Net:
    """A spatially embedded Boolean network. `op` and `src` are HIDDEN ground truth."""
    H: int
    W: int
    op: np.ndarray                      # (H,W) int   -- the cell's operation
    src: np.ndarray                     # (H,W,3) int -- flat indices of up to 3 inputs, -1 = unused
    period: int = 8                     # clock period
    state: np.ndarray = None            # (H,W) uint8 -- the ONLY thing the observer ever sees
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.state is None:
            self.state = np.zeros((self.H, self.W), dtype=np.uint8)

    def copy(self):
        return Net(self.H, self.W, self.op.copy(), self.src.copy(), self.period,
                   self.state.copy(), dict(self.meta))


def step(net: Net, t: int, clamp=None) -> Net:
    """One synchronous update. `clamp` is a dict {(r,c): value} -- the observer's ONLY way to intervene."""
    H, W = net.H, net.W
    s = net.state.reshape(-1).astype(np.int8)
    op = net.op.reshape(-1)
    src = net.src.reshape(-1, 3)
    nxt = np.zeros_like(s)

    def val(i):
        return s[i] if i >= 0 else 0

    for i in range(H * W):
        o = op[i]
        if o == OFF:
            nxt[i] = 0
        elif o == CONST1:
            nxt[i] = 1
        elif o == CLK:
            nxt[i] = 1 if ((t + 1) % net.period) < (net.period // 2) else 0
        elif o == WIRE:
            nxt[i] = val(src[i, 0])
        elif o == NOT:
            nxt[i] = 1 - val(src[i, 0])
        elif o == AND:
            nxt[i] = val(src[i, 0]) & val(src[i, 1])
        elif o == OR:
            nxt[i] = val(src[i, 0]) | val(src[i, 1])
        elif o == XOR:
            nxt[i] = val(src[i, 0]) ^ val(src[i, 1])
        elif o == REG:
            # THE MEMORY. next = we ? data : self.  The SELF input is a genuine directed CYCLE, and it is what
            # makes the program a STATE of fixed wiring rather than a change to the wiring.
            we, data = val(src[i, 0]), val(src[i, 1])
            nxt[i] = data if we else s[i]
    out = net.copy()
    out.state = nxt.reshape(H, W).astype(np.uint8)
    if clamp:
        for (r, c), v in clamp.items():
            out.state[r, c] = v
    return out


def run(net: Net, steps: int, t0: int = 0, clamp_fn=None):
    """Returns the list of RAW STATE GRIDS. This is the only thing the observer is ever given."""
    frames = [net.state.copy()]
    cur = net
    for k in range(steps):
        cl = clamp_fn(k) if clamp_fn else None
        cur = step(cur, t0 + k, cl)
        frames.append(cur.state.copy())
    return frames


def settle(net: Net, steps: int) -> Net:
    cur = net
    for k in range(steps):
        cur = step(cur, k)
    return cur


def period_of(net: Net, t0: int, max_p: int = 64) -> int:
    """The EXACT fundamental period of the settled trajectory (smallest, so no harmonic can be reported)."""
    ref = net.state.copy()
    cur = net
    for p in range(1, max_p + 1):
        cur = step(cur, t0 + p - 1)
        if np.array_equal(cur.state, ref):
            return p
    raise AssertionError("boolnet: no exact period -- the circuit is not settled")
