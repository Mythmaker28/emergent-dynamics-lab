"""HIDDEN EVALUATOR for the Boolean-network world. FULLY PRIVILEGED. No head may import from this module.

Two INDEPENDENT paths to every causal graph, exactly as in the Game-of-Life library (D-054):
  DECLARED   -- read off the wiring (op/src arrays).
  MEASURED   -- read off INTERVENTIONS: clamp a whole component to 0 and watch the declared output cells.
They must agree edge-for-edge, or the circuit is REJECTED, not patched. A declared graph the dynamics does not
realize is not a ground truth; it is a comment.
"""

from __future__ import annotations

import numpy as np

from .engine import step, OFF
from .circuits import Machine, settled, SETTLE, output_trace

# TWO INTERVENTIONS, AND THE DISTINCTION IS SUBSTRATE-DEEP.
#
# In Game of Life an ablation is DESTRUCTIVE: the matter is gone and does not come back, so a brief clear has a
# PERMANENT effect. In a Boolean network a clamp is REVERSIBLE: release it and the component works again. A
# 6-step clamp therefore measures nothing but a transient, and my first evaluator duly found that every effect
# was transient and no component was needed for anything.
#
#   ABLATION -- clamp to 0 for the WHOLE window. This is the analogue of destruction: the component is held out
#               of the circuit for as long as we watch. It measures the causal GRAPH.
#   PULSE    -- clamp to 0 for ONE step. It distinguishes MEMORY from FEED-FORWARD: a transient perturbation of a
#               cycle has a PERMANENT effect; a feed-forward path forgets it.
#
# And clamping to 0 is ASSIGNMENT, not deletion. In the De Morgan gate the internal cells carry the INVERTED
# signal, so a 0-clamp on them asserts "the inverted signal is 0", i.e. "the signal is 1" -- and on release it
# produces a spurious 1. Holding the clamp for the whole window removes that artefact entirely.
HOLD = 6          # PULSE length (memory probe)
OBS = 96          # observation window; every comparison uses EXACTLY this length.
                  # MEASURED: the furthest channel needs ~55 steps for a clock perturbation to reach its output
                  # (33 bus + 6 channel + 1 gate + 14 output wire). At OBS = 48 the effect fell OUTSIDE the
                  # window and the evaluator reported that the clock does not reach the third output. An
                  # observation window shorter than the causal path length does not measure absence of an edge;
                  # it measures impatience.


def _trace(m: Machine, clamp_cells=None, hold=None, steps=OBS):
    cur = settled(m)
    hold = steps if hold is None else hold          # default = ABLATION (held for the whole window)
    out = []
    for k in range(steps):
        cl = {c: 0 for c in clamp_cells} if (clamp_cells and k < hold) else None
        cur = step(cur, SETTLE + k, cl)
        out.append(tuple(int(cur.state[r, c]) for (r, c) in m.out_cells))
    return out


def measured_graph(m: Machine) -> dict:
    """Ablate each component; record which declared outputs move, and after how long."""
    base = _trace(m)
    edges, delays, kinds = [], {}, {}
    for name, cells in m.components.items():
        if not cells:
            continue
        tr = _trace(m, clamp_cells=cells)          # ABLATION: held for the whole window
        for j in range(len(m.out_cells)):
            b = [x[j] for x in base]
            a = [x[j] for x in tr]
            d = [i for i in range(len(b)) if a[i] != b[i]]
            if d:
                edges.append((name, f"out{j}"))
                delays[f"{name}->out{j}"] = int(d[0])
                # PERSISTENT if the difference is still present in the tail (memory / permanent change)
                tail = [i for i in d if i >= len(b) - 8]
                kinds[f"{name}->out{j}"] = "PERSISTENT" if tail else "TRANSIENT"
    return {"edges": sorted(set(edges)), "delays": delays, "kinds": kinds,
            "baseline": base}


# What the gate's FUNCTION implies for a channel's output, given its program bit. `live` means a real square wave
# (the clock reaches the output); not-live means a stuck line, whether stuck high or stuck low.
#   AND(clk, p): out = clk if p=1, else 0        -> live iff p = 1
#   OR (clk, p): out = 1  if p=1, else clk       -> live iff p = 0     (STUCK HIGH when p=1 -- not dead: saturated)
#   XOR(clk, p): out = ~clk if p=1, else clk     -> live ALWAYS
# My first bar hardcoded the AND row and so declared the OR and XOR machines BROKEN when they were working exactly
# as built. A ground-truth check that only knows one gate is not ground truth; it is a hidden assumption.
_LIVE_IF = {
    "direct": lambda b: bool(b), "direct_buf": lambda b: bool(b), "demorgan": lambda b: bool(b),
    "nand2": lambda b: bool(b), "single_parent": lambda b: True,   # AND(clk,clk) = clk: always live, program-blind
    "xor_or": lambda b: bool(b), "and_or": lambda b: bool(b), "xnor_and": lambda b: bool(b),   # all compute AND
    # the source-transducer development family: every one of these is dead when its register(s) hold 0, and
    # carries a genuine square wave when they hold 1 -- except the TOGGLE, whose output flips on every clock-high
    # and is therefore ALIVE regardless of the program. Its register is not wired to it at all.
    "dup_same": lambda b: bool(b), "dup_lag": lambda b: bool(b), "inv_lag": lambda b: bool(b),
    "lag15_or": lambda b: bool(b), "lag15_xor": lambda b: bool(b),
    "lag8_and": lambda b: bool(b), "lag8_or": lambda b: bool(b), "cascade": lambda b: bool(b),
    "tri_tap": lambda b: bool(b), "sync3": lambda b: bool(b),
    "edge_xor": lambda b: bool(b), "reg_delay": lambda b: bool(b),
    "and3": lambda b: bool(b), "two_en": lambda b: bool(b), "toggle": lambda b: True,
    "or_gate": lambda b: not bool(b), "xor_gate": lambda b: True,
}


def viable(m: Machine) -> tuple:
    """POSITIVE CONTROL: every channel the gate's function says must carry the clock to its output does so.
    NEGATIVE CONTROL: every channel it says must be a stuck line IS one -- a criterion that cannot fail is not a
    criterion. The expectation comes from the gate's function AND the program, never from the program alone."""
    tr = _trace(m)
    live = []
    for j in range(len(m.out_cells)):
        col = [x[j] for x in tr]
        live.append(any(col) and not all(col))          # a real square wave, not a stuck line
    f = _LIVE_IF[m.impl]
    expect = [f(b) for b in m.program]
    return live == expect, {"live": live, "expected": expect, "impl": m.impl, "program": tuple(m.program)}


def assert_qualified(m: Machine) -> dict:
    """The library qualification bar (COMPONENT_LIBRARY_V2_SPEC SS 'Qualification bar')."""
    from .engine import period_of
    s = settled(m)
    p = period_of(s, SETTLE)                                        # (6) exactly periodic
    ok, det = viable(m)                                            # (1)(2) positive AND negative functional control
    if not ok:
        raise AssertionError(f"{m.arch_id}: functional control FAILED {det}")
    mg = measured_graph(m)

    # (5) two independent paths must agree, at the level of COMPONENT -> OUTPUT reachability
    declared = set()
    for (a, b, _d) in m.declared_edges:
        declared.add((a, b))
    # transitively close the declared wiring to component->output reachability
    reach = {}
    for (a, b) in declared:
        reach.setdefault(a, set()).add(b)
    def outs_of(n, seen=None):
        seen = seen or set()
        if n in seen:
            return set()
        seen.add(n)
        r = set()
        for t in reach.get(n, ()):
            if t.startswith("out"):
                r.add(t)
            else:
                r |= outs_of(t, seen)
        return r
    decl_pairs = {(n, o) for n in m.components for o in outs_of(n)}
    meas_pairs = set(mg["edges"])
    # a component with program bit 0 has its gate closed, so its channel cannot reach the output -- the
    # ACTIVE-influence graph is program-dependent while the STRUCTURAL graph is not. Compare the ACTIVE one.
    # THE ACTIVE-INFLUENCE GRAPH IS PROGRAM-DEPENDENT; THE STRUCTURAL ONE IS NOT (D-053, restated here).
    # When program bit j is 0 the gate output is constantly 0, so NOTHING upstream -- not the clock, not the
    # channel, not the register, not the gate itself -- has any measurable effect on output j. Every edge into
    # out_j is severed. That is not a defect of the benchmark: it is the very distinction A_TOPO must be read
    # off the STRUCTURAL graph to avoid, and here the two are separable BY CONSTRUCTION for the first time.
    # WHICH declared edges are ACTIVE is a fact about the GATE'S FUNCTION and the program bit -- edge by edge,
    # not output by output. My first bar wrote `program[j] != 0`, which is the AND row of the table and nothing
    # else, and it duly declared the OR and XOR machines broken when they were working exactly as built.
    #
    #   AND(clk, p)  p=1: out = clk. Ablating clk, the channel, the gate OR the register all kill it -> ALL active.
    #                p=0: out = 0 forever. Nothing upstream moves it, not even the gate -> NO edge is active.
    #   OR (clk, p)  p=1: out = 1 forever, SATURATED. Clamping the clock changes nothing (1 or clk = 1), so the
    #                     clock is severed; but clamping the REGISTER to 0 re-opens the channel, and clamping the
    #                     GATE to 0 kills the output -> ONLY gate and register are active.
    #                p=0: out = clk. Clock, channel and gate are active; clamping the register to 0 is VACUOUS
    #                     (it already holds 0) -> the register edge is NOT measurable here. Absence of a vacuous
    #                     intervention's effect is not absence of an edge; it is absence of an experiment.
    #   XOR(clk, p)  p=1: out = ~clk -- everything upstream is active, the register included (clamping it flips
    #                     the polarity back).
    #                p=0: out = clk; the register clamp is again vacuous.
    #   AND(x, x)    the register is not wired to it at all: signal path only, at every program bit.
    def _active(n, j):
        b = int(m.program[j])
        is_reg, is_gate, is_out = n == f"reg{j}", n == f"gate{j}", n == f"out{j}"
        # the OUTPUT WIRE is DOWNSTREAM of the gate, so the gate's saturation cannot sever it: whenever the output
        # is not already constant 0, clamping its own wire to 0 moves it. It belongs with the gate, not with the
        # signal path. (Grouping it with the clock is what produced measured-only=[('out0','out0')] on the
        # saturated OR machine -- the evaluator denying an edge it had itself just measured.)
        downstream = is_gate or is_out
        if m.impl in ("direct", "direct_buf", "demorgan", "nand2", "xor_or", "and_or", "xnor_and",
                      "dup_same", "dup_lag", "inv_lag", "lag15_or", "lag15_xor", "lag8_and", "lag8_or",
                      "cascade", "and3", "two_en",
                      "tri_tap", "sync3", "edge_xor", "reg_delay"):
            return b == 1                              # p=0: out is constant 0; every clamp-to-0 is vacuous
        if m.impl == "toggle":
            return not (is_reg or n == f"reg2{j}")     # the register is not an input to a toggle
        if m.impl == "or_gate":
            return (is_reg or downstream) if b == 1 else (not is_reg)
        if m.impl == "xor_gate":
            return True if b == 1 else (not is_reg)
        if m.impl == "single_parent":
            return not is_reg                          # the register is not wired to AND(x, x) at all
        raise AssertionError(f"no ground-truth activity rule for impl {m.impl!r}")
    active_decl = {(n, o) for (n, o) in decl_pairs if _active(n, int(o[3:]))}
    missing = sorted(active_decl - meas_pairs)
    extra = sorted(meas_pairs - active_decl)
    if missing or extra:
        raise AssertionError(f"{m.arch_id}: declared and measured graphs DISAGREE. "
                             f"declared-only={missing} measured-only={extra}")

    # (3) intervention non-vacuity: every clamped component must actually have been holding a 1 at some point
    nv = {}
    cur = settled(m)
    hist = []
    for k in range(OBS):
        cur = step(cur, SETTLE + k)
        hist.append(cur.state.copy())
    for name, cells in m.components.items():
        nv[name] = bool(any(h[r, c] for h in hist[:HOLD] for (r, c) in cells))
    return {"period": p, "functional_control": det, "graph_paths_agree": True,
            "measured_edges": mg["edges"], "delays": mg["delays"], "kinds": mg["kinds"],
            "intervention_nonvacuity": nv, "window": OBS}


def structural_graph(m: Machine, context=None) -> dict:
    """THE STRUCTURAL GRAPH -- program-INDEPENDENT, and the reason this substrate exists.

    The ACTIVE-influence graph is program-dependent: with program bit j = 0 the gate is shut, so nothing upstream
    can reach output j and every edge into it vanishes. Read A_TOPO off THAT and a mere program change moves the
    architecture -- exactly the contamination that made program-invariance untestable in Game of Life (D-055).

    The fix is a RICHER INTERVENTION REPERTOIRE, not a cleverer statistic. Clamp each component to 0 AND to 1 and
    take the UNION of the effects. Forcing a shut register to 1 OPENS its gate, and the channel's influence on the
    output appears. What the observer recovers is then the WIRING -- which components CAN influence which -- and
    that is invariant to the program by construction.

    This is the counterfactual definition of structure: not "what does influence what", but "what COULD".

    AND A SINGLE-COMPONENT INTERVENTION IS NOT ENOUGH. Clamping a CHANNEL while its gate is shut does nothing at
    all -- the gate outputs 0 whatever the channel does -- so the path stays invisible. Measured: the union over
    single 0/1 clamps still gave 18 / 16 / 14 / 12 edges across the four programs. Structure behind a closed gate
    is simply NOT IDENTIFIABLE from single interventions.

    It IS identifiable from CONDITIONAL ones: hold a CONTEXT that opens the gates, then probe. That is not a
    trick; it is how a circuit is actually tested, and it is the substrate's honest answer to the question
    "which relations can be identified from which experiments".

    `context` = cells clamped to 1 for the whole window (the evaluator knows they are registers; a blind observer
    must DISCOVER them, as the cells whose clamping has a PERMANENT effect -- the memory signature).
    """
    base_ctx = _trace_ctx(m, context)
    edges = set()
    for name, cells in m.components.items():
        if not cells:
            continue
        for v in (0, 1):
            tr = _trace_ctx(m, context, {c: v for c in cells})
            for j in range(len(m.out_cells)):
                if any(tr[i][j] != base_ctx[i][j] for i in range(OBS)):
                    edges.add((name, f"out{j}"))
    return {"edges": sorted(edges), "context_cells": sorted(context or [])}


def _trace_ctx(m: Machine, context=None, probe=None):
    """Trace with a CONTEXT (cells held at 1) and optionally a PROBE clamp, both for the whole window."""
    cur = settled(m)
    cl = {}
    if context:
        cl.update({c: 1 for c in context})
    if probe:
        cl.update(probe)
    out = []
    for k in range(OBS):
        cur = step(cur, SETTLE + k, dict(cl) if cl else None)
        out.append(tuple(int(cur.state[r, c]) for (r, c) in m.out_cells))
    return out


# The declared component `gate{i}` is a LAYOUT grouping: for `direct_buf` it also contains two pure WIRE buffers,
# and for `xnor_and` two re-timing buffers. Those cells CONDUCT; they do not compute. The MINIMAL COMPUTING
# SUBGRAPH -- which is what a module IS -- excludes them, and an observer that reports the AND alone is RIGHT, not
# short by two cells. Scoring boundary quality against the layout grouping would penalise the correct answer, which
# is the D-053 error (marking the observer wrong when it was right). Ground truth for BOUNDARY is the gate core.
def gate_core(m: Machine, i: int) -> set:
    """The cells of gate{i} that COMPUTE: everything but the pure conductors."""
    from .engine import WIRE
    return {c for c in m.components[f"gate{i}"] if int(m.net.op[c]) != WIRE}
