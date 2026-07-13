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


def viable(m: Machine) -> tuple:
    """POSITIVE CONTROL: every channel whose program bit is 1 must actually carry the clock to its output;
    every channel whose bit is 0 must be silent. NEGATIVE CONTROL is the bit-0 case -- a criterion that cannot
    fail is not a criterion."""
    tr = _trace(m)
    live = []
    for j in range(len(m.out_cells)):
        col = [x[j] for x in tr]
        live.append(any(col) and not all(col))          # a real square wave, not a stuck line
    expect = [bool(b) for b in m.program]
    return live == expect, {"live": live, "expected_from_program": expect}


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
    active_decl = {(n, o) for (n, o) in decl_pairs if m.program[int(o[3:])] != 0}
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
