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
    """One synchronous update, VECTORISED. `clamp` is a dict {(r,c): value} -- the observer's ONLY intervention.

    The reference implementation was a Python loop over every cell. It is kept below as `step_reference` and this
    path is proved bit-identical to it on adversarial random nets (`assert_equivalent_to_reference`). Speed is a
    CORRECTNESS matter, not an engineering one: blind memory discovery must PULSE EVERY CELL, and a probe too slow
    to run exhaustively is a probe that gets sub-sampled -- which is exactly what made the S head blind in
    EXP-GT-01.
    """
    s = net.state.reshape(-1).astype(np.int8)
    op = net.op.reshape(-1)
    src = net.src.reshape(-1, 3)
    a = np.where(src[:, 0] >= 0, s[src[:, 0]], 0)
    b = np.where(src[:, 1] >= 0, s[src[:, 1]], 0)
    # ASYMMETRIC DUTY CYCLE, and it is not cosmetic.
    # With a 50%-duty square wave, NOT(x) is EXACTLY x delayed by half a period. Inversion and delay become
    # indistinguishable, so the latency through a De Morgan gate reads 7 instead of 3 and the latency through a
    # plain AND reads 5 instead of 1. That is a genuine IDENTIFIABILITY TRAP built into the clock, not a bug in
    # the observer -- and the honest fix is to remove the degeneracy from the world rather than to paper over it
    # in the estimator. A 3-of-8 duty cycle makes NOT(x) a shift of nothing.
    clk = np.int8(1 if ((t + 1) % net.period) < 3 else 0)

    nxt = np.zeros_like(s)
    nxt[op == CONST1] = 1
    nxt[op == CLK] = clk
    m = op == WIRE
    nxt[m] = a[m]
    m = op == NOT
    nxt[m] = 1 - a[m]
    m = op == AND
    nxt[m] = a[m] & b[m]
    m = op == OR
    nxt[m] = a[m] | b[m]
    m = op == XOR
    nxt[m] = a[m] ^ b[m]
    m = op == REG                      # next = we ? data : self  -- the SELF term is the causal CYCLE
    nxt[m] = np.where(a[m].astype(bool), b[m], s[m])

    out = net.copy()
    out.state = nxt.reshape(net.H, net.W).astype(np.uint8)
    if clamp:
        for (r, c), v in clamp.items():
            out.state[r, c] = v
    return out


def step_reference(net: Net, t: int, clamp=None) -> Net:
    """The original cell-by-cell reference. Never deleted; it is the second independent path."""
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
            nxt[i] = 1 if ((t + 1) % net.period) < 3 else 0
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
            we, data = val(src[i, 0]), val(src[i, 1])
            nxt[i] = data if we else s[i]
    out = net.copy()
    out.state = nxt.reshape(H, W).astype(np.uint8)
    if clamp:
        for (r, c), v in clamp.items():
            out.state[r, c] = v
    return out


def assert_equivalent_to_reference(trials: int = 12, seed: int = 20260718) -> int:
    """DIFFERENTIAL VERIFICATION. The fast path is not trusted because it looks right; it is trusted because it
    is proved bit-identical to the reference on adversarial random nets, including every op and self-loops."""
    rng = np.random.default_rng(seed)
    checks = 0
    for _ in range(trials):
        H, W = 7, 9
        n = H * W
        op = rng.integers(0, 9, size=(H, W))
        src = rng.integers(-1, n, size=(H, W, 3))
        st = (rng.random((H, W)) < 0.4).astype(np.uint8)
        net = Net(H, W, op, src, 6, st)
        a, b = net.copy(), net.copy()
        for t in range(10):
            a = step(a, t)
            b = step_reference(b, t)
            if not np.array_equal(a.state, b.state):
                raise AssertionError("boolnet: vectorised step DISAGREES with the reference")
            checks += 1
    return checks


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
