"""COMPONENT LIBRARY V2 -- circuits that can express the three questions Game of Life could not ask.

  1A PROGRAM != ARCHITECTURE. A REGISTER holds a bit (`next = we ? data : self`). With `we = 0` it holds its
     INITIAL value forever. The PROGRAM is the registers' initial contents; the WIRING NEVER CHANGES. Four
     programs, ONE graph. In Game of Life a memory bit was an eater that had to be ADDED, so setting a bit added a
     node and two edges -- the program WAS the architecture, and a program-invariance test could not fire.

  1B FEEDBACK. The register's self-loop IS a directed causal cycle: its next state depends on its own state.
     Break that edge (clamp the self input) and the memory is destroyed. A ring of inverters gives a second,
     oscillating cycle. In Game of Life the component->component dependency graph had edges OUT of guns and NONE
     INTO any gun, and a cycle needs an edge into a source.

  1C HELD-OUT IMPLEMENTATION. One function, two microscopically distinct realisations:
        DIRECT:   g = AND(sig, reg)
        DEMORGAN: g = NOT( OR( NOT sig, NOT reg ) )      -- three extra cells, three extra steps of latency
     Different cells, different microtrajectories, different persistent-cell sets, IDENTICAL logical function.
     The latency differs by construction, so this is a clean A_TAU change with A_TOPO held fixed -- exactly the
     distinction the whole ontology exists to make.

EVERYTHING HERE IS EVALUATOR-ONLY. The observer receives the raw binary grid and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .engine import Net, OFF, WIRE, CLK, NOT, AND, OR, XOR, REG, CONST1, run, step, period_of

H, W = 24, 64
OUT_ROW = 22                 # the declared I/O interface: the observer is told the output row, nothing else
CLK_PERIOD = 8


@dataclass
class Machine:
    net: Net
    program: tuple                       # HIDDEN: the registers' initial contents
    components: dict                     # HIDDEN: name -> list of (r,c) cells
    declared_edges: tuple                # HIDDEN: (src_component, dst_component, delay)
    out_cells: tuple                     # the declared output cells (part of the I/O interface)
    arch_id: str = ""
    impl: str = "direct"
    meta: dict = field(default_factory=dict)


def _idx(r, c):
    return r * W + c


def build(program=(1, 0, 1), chan_cols=(6, 20, 34), impl="direct", extra_delay=0,
          feedback=False, decoy=False, arch_id="M") -> Machine:
    """One fixed architecture. `program` is the registers' INITIAL CONTENTS -- it does not touch the wiring.

    Layout, per channel at column cc:
        row 1        the clock bus (a horizontal wire chain from the clock source)
        rows 2..7    the signal channel: a vertical wire chain, one cell per step of delay
        (4, cc+2)    the REGISTER holding program bit i -- OFF the channel column, so nothing collides
        row 8+d      the GATE: AND(channel, register)   [or its De Morgan twin]
        rows ..22    the output wire, down to the declared output row
    """
    op = np.full((H, W), OFF, dtype=int)
    src = np.full((H, W, 3), -1, dtype=int)
    st = np.zeros((H, W), dtype=np.uint8)
    comps, edges = {}, []

    op[1, 1] = CLK
    comps["clk"] = [(1, 1)]
    bus = [(1, c) for c in range(2, max(chan_cols) + 2)]
    for (r, c) in bus:
        op[r, c] = WIRE
        src[r, c, 0] = _idx(1, c - 1)
    comps["bus"] = bus
    edges.append(("clk", "bus", 1))

    # write-enable held LOW. This cell exists in EVERY program: the registers HOLD their initial value forever,
    # so the PROGRAM is a STATE of fixed wiring, not a change to it.
    comps["we"] = [(20, 1)]                          # an OFF cell reads as 0

    for i, cc in enumerate(chan_cols):
        # ---- REGISTER (program bit i). Self-loop: next = we ? data : self  -> a genuine directed CYCLE.
        rr = (4, cc + 2)
        op[rr] = REG
        src[rr[0], rr[1], 0] = _idx(20, 1)           # we = 0
        src[rr[0], rr[1], 1] = _idx(20, 1)           # data (unused while we = 0)
        st[rr] = program[i]                          # <<-- THE PROGRAM
        comps[f"reg{i}"] = [rr]
        edges.append((f"reg{i}", f"reg{i}", 1))      # THE CYCLE

        # ---- signal channel: one cell per step of delay.
        #      A DELAY EDIT is a DETOUR, not a longer drop. My first version pushed the gate DOWN by
        #      `extra_delay` rows and thereby SHORTENED the output wire by the same amount -- the total latency
        #      was unchanged and the "delay edit" edited nothing. The qualification bar caught it: base and
        #      +delay3 both measured clk->out0 = 26. A criterion that cannot fire is not a criterion, and a
        #      delay edit that does not change the delay is not an edit.
        #      The detour jogs sideways at rows 5-6 and returns, adding EXACTLY 2*extra_delay cells while the
        #      gate stays at row 8 and the output wire keeps its length. A_TOPO fixed; A_TAU moved.
        chan = []
        op[2, cc] = WIRE
        src[2, cc, 0] = _idx(1, cc)
        chan.append((2, cc))
        for r in (3, 4):
            op[r, cc] = WIRE
            src[r, cc, 0] = _idx(r - 1, cc)
            chan.append((r, cc))
        prev = (4, cc)
        d = extra_delay
        if d:
            for k in range(1, d + 1):                     # out along row 5
                cell = (5, cc + k)
                op[cell] = WIRE
                src[cell[0], cell[1], 0] = _idx(*prev)
                chan.append(cell)
                prev = cell
            for k in range(d, -1, -1):                    # back along row 6
                cell = (6, cc + k)
                op[cell] = WIRE
                src[cell[0], cell[1], 0] = _idx(*prev)
                chan.append(cell)
                prev = cell
        else:
            for r in (5, 6):
                op[r, cc] = WIRE
                src[r, cc, 0] = _idx(*prev)
                chan.append((r, cc))
                prev = (r, cc)
        op[7, cc] = WIRE
        src[7, cc, 0] = _idx(*prev)
        chan.append((7, cc))
        comps[f"chan{i}"] = chan
        edges.append(("bus", f"chan{i}", 1))

        gy = 8
        if impl == "direct":
            op[gy, cc] = AND
            src[gy, cc, 0] = _idx(gy - 1, cc)
            src[gy, cc, 1] = _idx(*rr)
            gcells = [(gy, cc)]
            glat = 1
        else:                                        # DE MORGAN: NOT(OR(NOT s, NOT r)) -- 4 cells, 3 steps latency
            op[gy, cc] = NOT
            src[gy, cc, 0] = _idx(gy - 1, cc)
            op[gy, cc + 1] = NOT
            src[gy, cc + 1, 0] = _idx(*rr)
            op[gy + 1, cc] = OR
            src[gy + 1, cc, 0] = _idx(gy, cc)
            src[gy + 1, cc, 1] = _idx(gy, cc + 1)
            op[gy + 2, cc] = NOT
            src[gy + 2, cc, 0] = _idx(gy + 1, cc)
            gcells = [(gy, cc), (gy, cc + 1), (gy + 1, cc), (gy + 2, cc)]
            glat = 3
        comps[f"gate{i}"] = gcells
        edges.append((f"chan{i}", f"gate{i}", glat))
        edges.append((f"reg{i}", f"gate{i}", glat))

        gout = gcells[-1]
        outw = []
        for r in range(gout[0] + 1, OUT_ROW + 1):
            op[r, cc] = WIRE
            src[r, cc, 0] = _idx(r - 1, cc)
            outw.append((r, cc))
        comps[f"out{i}"] = outw
        edges.append((f"gate{i}", f"out{i}", len(outw)))
        edges.append((f"out{i}", f"out{i}", 1))      # the output wire is itself on the path to the output

    if feedback:
        ring = [(15, 55), (16, 55), (17, 55)]        # a ring of 3 inverters: a SECOND, oscillating cycle
        for k, (r, c) in enumerate(ring):
            op[r, c] = NOT
            src[r, c, 0] = _idx(*ring[(k - 1) % 3])
        st[ring[0]] = 1
        comps["ring"] = ring
        edges.append(("ring", "ring", 3))

    if decoy:
        # causally INERT: fed by nothing, driving nothing -- AND placed clear of every channel column.
        # (my first decoy sat at cols 2-7 and OVERWROTE channel 0's output wire at column 6. The functional
        #  positive control caught it: channel 0 went dead. Decoration that breaks the machine is not decoration.)
        dec = [(18, 45 + k) for k in range(6)]
        for k, (r, c) in enumerate(dec):
            op[r, c] = WIRE
            src[r, c, 0] = _idx(r, c - 1) if k else -1
        comps["decoy"] = dec

    net = Net(H, W, op, src, CLK_PERIOD, st)
    outs = tuple((OUT_ROW, cc) for cc in chan_cols)
    return Machine(net, tuple(program), comps, tuple(edges), outs, arch_id=arch_id, impl=impl,
                   meta={"chan_cols": tuple(chan_cols), "extra_delay": extra_delay,
                         "feedback": feedback, "decoy": decoy})


SETTLE = 64


def settled(m: Machine):
    cur = m.net
    for k in range(SETTLE):
        cur = step(cur, k)
    return cur


def output_trace(m: Machine, steps=64, t0=SETTLE, clamp_fn=None):
    """The declared I/O interface: the values of the output cells over time."""
    cur = settled(m)
    tr = []
    for k in range(steps):
        cl = clamp_fn(k) if clamp_fn else None
        cur = step(cur, t0 + k, cl)
        tr.append(tuple(int(cur.state[r, c]) for (r, c) in m.out_cells))
    return tr
