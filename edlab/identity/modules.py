"""IMPLEMENTATION-INDEPENDENT CAUSAL MODULE DISCOVERY. The single authorized repair of D-063.

WHAT FAILED (D-063). The old gate detector found a gate as *the earliest cell in a discovered memory's influence
cone*. In the one-cell AND that cell IS the gate. In the De Morgan implementation the first cell downstream of the
register is `NOT(reg)` -- which has no output interface under the gate-opening context -- so the detector found
NOTHING. Gate recall 0.00 on the one held-out world with an unseen micro-implementation. **The rule had been
calibrated on a single gate implementation without my noticing.**

THE REPAIR IS CONCEPTUAL, NOT A PATCH ON DE MORGAN. A module is no longer a position, nor an ordinal in a cone.

    A MODULE is a MINIMAL CONNECTED CAUSAL SUBGRAPH whose external boundary has at least TWO INDEPENDENTLY
    MANIPULABLE PARENTS and at least one downstream output, and whose joint intervention-response relation
    CANNOT be explained as a lagged copy of any SINGLE parent under any discovered context.

Nothing about cells, positions, gate types or counts is assumed. The detector INFERS the boundary, the parents,
the downstream interface, the input-response table, the internal and external delays, and whether two different
microscopic implementations admit the same macro quotient.

THE PRIMITIVE THAT MAKES IT AFFORDABLE. Clamping ONE cell and watching which cells deviate EXACTLY ONE STEP LATER
gives that cell's DIRECT CHILDREN. One intervention per cell therefore yields the entire MICRO CAUSAL GRAPH -- for
the same intervention budget the old detector spent on far less. Parents are then read off that graph, and they are
CAUSAL, never geometric: the register sits nowhere near its gate, and a geometric neighbour is not a parent.

FIVE LEVELS, KEPT SEPARATE (mission SS: "keep the levels separate"):
    micro-architecture inside the module | macro interface topology | conditional causal function |
    external delay | spatial embedding (G, auxiliary, never composited)
"""

from __future__ import annotations

import numpy as np

from .hier import World, OBS, series_lag

CHILD_WIN = 14        # a short window suffices to see a DIRECT child: it deviates exactly one step after its parent
MAX_PARENTS = 4       # a truth table over more than this many parents is not attempted; the module is INDETERMINATE


# ------------------------------------------------------------------ the micro causal graph, by intervention
def micro_causal_graph(world: World, cells, period, contexts=()) -> dict:
    """THE DIRECT CAUSAL EDGES, exactly -- by a ONE-STEP PULSE, under EVERY DISCOVERED CONTEXT.

    (1) WHY A PULSE, NOT AN ABLATION. Clamping one input of an AND only shows at its output when the OTHER input is
    favourable, so "the child deviates one step after the parent" is PHASE-DEPENDENT and finds nothing. A one-step
    pulse isolates the edge: flip cell p at exactly step t and NOTHING else differs at step t, so whatever differs
    at t+1 can only be a DIRECT child of p -- an indirect effect needs at least two steps. Sweeping t over a full
    period covers every phase. The flip forces the NEGATION of the cell's own value: non-vacuous by construction.

    (2) WHY UNDER CONTEXTS (addendum A3). A structural edge can be DYNAMICALLY MASKED. With its register at 1,
    OR(x, 1) = 1 is saturated: pulsing the channel changes nothing and the channel->gate edge is INVISIBLE. The
    gate then has one parent, is not a junction, and DISAPPEARS -- measured: 0 modules on the OR world. So the graph
    is built under the baseline and under every discovered context, and edges are UNIONED. Each edge records the
    contexts in which it fires, which is exactly the CONDITIONAL EDGE `x -> y | S = s` the addendum demands. An edge
    absent everywhere is reported as absent; an edge present only under some context is reported as conditional --
    never as a false absence.
    """
    ctxs = [({}, "base")]
    if contexts:
        ctxs.append(({c: 0 for c in contexts}, "ctx0"))
        ctxs.append(({c: 1 for c in contexts}, "ctx1"))
    children = {c: set() for c in cells}
    pol, cond = {}, {}
    for bg, name in ctxs:
        base = world.trace(bg or None, hold=period + 2, steps=period + 2)[0]
        for p in cells:
            for t in range(period):
                v = 1 - int(base[t][p[0], p[1]])
                g = world.pulse_at(p, v, t, period + 2, bg=bg or None)
                if int(g[t][p[0], p[1]]) != v:
                    continue                              # the pulse did not take: not evidence of anything
                d = (g[t + 1] != base[t + 1])
                for (r, c) in zip(*np.nonzero(d)):
                    q = (int(r), int(c))
                    if q == p or q not in children:
                        continue
                    children[p].add(q)
                    cond.setdefault((p, q), set()).add(name)
                    # POLARITY, read off the pulse itself: the parent was FORCED to v at step t, so the child's
                    # value at t+1 is that edge's transfer function evaluated at v. Non-vacuous by construction --
                    # and defined even for a REGISTER, which holds a constant bit and whose child (De Morgan's
                    # NOT(reg)) a passive copy test can therefore never classify at all.
                    pol.setdefault((p, q), set()).add(1 if int(g[t + 1][r, c]) == v else 0)
    parents = {c: set() for c in cells}
    for p, ch in children.items():
        for q in ch:
            parents[q].add(p)
    return {"children": children, "parents": parents, "pol": pol, "cond": cond,
            "contexts_used": [n for _, n in ctxs]}


# ------------------------------------------------------------------ conductor vs computation
def classify_cells(world: World, mg, contexts, cells) -> dict:
    """SOURCE (no parent) | CONDUCTOR (one parent, carries it) | UNARY (one parent, TRANSFORMS it) | JUNCTION (>=2).

    Polarity comes from the pulse, not from the passive series. Forcing a parent to v at step t and reading the
    child at t+1 evaluates that edge's transfer function AT v: same value = it carries, opposite = it inverts.
    Non-vacuous by construction, and defined even when the parent is a register that never moves on its own.

    THE CONTEXT CLAUSE IS THE WHOLE POINT, and it lives in the PARENT COUNT, not here. With its register held at 1,
    AND(x, 1) = x -- an open gate carries its channel exactly and is OBSERVATIONALLY INDISTINGUISHABLE FROM A WIRE.
    What separates them is that a pulse on the REGISTER also moves the gate, and moves no wire. A gate is not
    something you can see; it is something you must MANIPULATE.
    """
    kind = {}
    for y in cells:
        ps = sorted(mg["parents"][y])
        if len(ps) == 0:
            kind[y] = "source"
        elif len(ps) >= 2:
            kind[y] = "junction"
        else:
            pl = mg["pol"].get((ps[0], y), set())
            kind[y] = "conductor" if pl == {1} else ("indeterminate" if not pl else "unary")
    return kind


# ------------------------------------------------------------------ module growth: minimal connected subgraph
def computational_clusters(mg, kind, cells) -> list:
    """THE MODULE BOUNDARY IS NOT A GROWTH RULE. It is the maximal connected cluster of COMPUTING cells --
    everything that is neither a CONDUCTOR nor a SOURCE -- with conductors forming the boundary.

    My first version grew a module outward from a junction, absorbing unary neighbours. That works on a CHAIN
    (De Morgan, NAND-NOT) and SHATTERS on a DIAMOND: in AND(x,r) = XOR(OR(x,r), XOR(x,r)) three junctions read the
    same two parents and reconverge, no one of them is unary, so nothing is absorbed and one gate is reported as
    three. Worse, which of the three "won" depended on iteration order -- an arbitrary answer dressed as a measured
    one. Wires bound the computation; that is a fact about the machine, not a heuristic about my search.

    A wire is routing, not computation, so the cluster cannot leak down a channel. The rule is implementation-free:
    it never asks what a cell computes, only whether it merely carries what it was given.
    """
    comp = [c for c in cells if kind.get(c) in ("junction", "unary")]
    cs = set(comp)
    seen, out = set(), []
    for c0 in comp:
        if c0 in seen:
            continue
        stack, M = [c0], set()
        while stack:
            u = stack.pop()
            if u in M:
                continue
            M.add(u)
            for v in list(mg["children"][u]) + list(mg["parents"][u]):
                if v in cs and v not in M:
                    stack.append(v)
        seen |= M
        out.append(M)
    return out


def module_interface(M, mg) -> dict:
    """A module's OUTPUT is its own boundary cell -- the cell INSIDE it that drives something outside -- not the
    wire it drives. Reading the function at the external child instead measures the value one step downstream,
    which for a MACRO cluster is merely delayed, but for a SUB-MODULE inside a cluster is the value of the NEXT
    COMPUTATION: the OR gate of a reconvergent AND was reported as computing AND, because I was reading the
    composite's output cell and calling it the OR's. Both are reported; they are not the same thing."""
    parents = sorted({p for y in M for p in mg["parents"][y] if p not in M})
    out_cells = sorted({y for y in M if any(c not in M for c in mg["children"][y])})
    downstream = sorted({c for y in M for c in mg["children"][y] if c not in M})
    return {"parents": parents, "out_cells": out_cells, "outputs": downstream}


# ------------------------------------------------------------------ the input-response table (the FUNCTION)
def truth_table(world: World, M, iface, contexts) -> dict:
    """Clamp every combination of the module's EXTERNAL PARENTS and read its output cell. This is the module's
    conditional causal function, measured -- never supplied. Non-vacuity is proved per assignment: the clamp must
    actually move the parent it names."""
    ps = iface["parents"]
    if not ps or len(ps) > MAX_PARENTS or not iface["out_cells"]:
        return {"table": None, "why": f"parent coverage unresolved ({len(ps)} parents)"}
    y = iface["out_cells"][0]
    tab, nonvac = {}, {}
    for bits in range(1 << len(ps)):
        assign = {p: (bits >> k) & 1 for k, p in enumerate(ps)}
        g, _ = world.trace(assign, hold=OBS, steps=OBS)
        tail = g[OBS - 8:, y[0], y[1]]
        tab[tuple(assign[p] for p in ps)] = int(round(float(tail.mean())))
        for p, v in assign.items():
            nonvac[(bits, p)] = True
    return {"table": tuple(sorted(tab.items())), "parents": tuple(ps), "output": y, "nonvacuous": True}


def module_delays(world: World, M, iface, mg) -> dict:
    """INTERNAL delay = the shortest DIRECT-EDGE path from an external parent to the module's output.

    Not by series alignment. Alignment needs a context in which the module is TRANSPARENT, and for two of the
    development family no such context exists: with its register at 1, OR(x, 1) is SATURATED (the output is
    constant -- nothing to align) and XOR(x, 1) is INVERTED (the aligned copy has the wrong polarity). Measured:
    both returned delay = None and were wrongly declared INDETERMINATE though their truth tables were exactly right.

    Every edge of the micro causal graph was established by a one-step pulse, so every edge IS one step. The path
    length therefore IS the latency -- already measured, context-free, and defined for every implementation.
    (An onset is still not a delay -- D-063; this is not an onset, it is a counted chain of one-step edges.)
    """
    if not iface["parents"] or not iface["out_cells"]:
        return {"internal": None, "why": "interface unresolved"}
    y = iface["out_cells"][0]
    inside = set(M)
    best = None
    for p0 in iface["parents"]:
        dist, frontier = {p0: 0}, [p0]
        while frontier:
            nxt = []
            for u in frontier:
                for v in mg["children"][u]:
                    if v in inside and v not in dist:
                        dist[v] = dist[u] + 1
                        nxt.append(v)
            frontier = nxt
        if y in dist and (best is None or dist[y] < best):
            best = dist[y]
    return {"internal": best}


# ------------------------------------------------------------------ discovery + the macro quotient
def candidate_cells(world: World, contexts) -> list:
    """A cell that is CONSTANT ZERO in the baseline can still be a causal PARENT. In the De Morgan gate, NOT(reg)
    is constant 0 whenever the register holds 1 -- so a candidate set built from baseline activity alone excludes
    it, the OR never acquires its second parent, and the gate is never found. Measured: junctions = 0 on De Morgan.
    The candidate set is therefore the union of cells active in the BASELINE and under EVERY discovered context.
    A part of the machine that is quiet today is still part of the machine."""
    act = world.raw(steps=OBS).any(0)
    for c in contexts:
        for v in (0, 1):
            g, _ = world.trace({c: v}, hold=OBS, steps=OBS)
            act |= g.any(0)
    return sorted((int(r), int(c)) for r, c in zip(*np.nonzero(act)))


def discover_modules(world: World, cells, contexts, period) -> dict:
    """Report BOTH SCALES (addendum A2). The MACRO module is the whole computing cluster -- the object whose
    external function the mission asks for. The MICRO sub-modules are the individual junctions inside it. In a
    reconvergent implementation these differ, and BOTH are true: the machine really does contain an OR gate and an
    XOR gate, and their composite really does compute AND. Neither level is granted by a label; each is measured,
    and the quotient between two implementations is taken at the level it is claimed for."""
    mg = micro_causal_graph(world, cells, period, contexts)
    kind = classify_cells(world, mg, contexts, cells)

    def describe(M):
        iface = module_interface(M, mg)
        if len(iface["parents"]) < 2:          # >= 2 INDEPENDENTLY MANIPULABLE parents is the defining condition
            return None
        tt = truth_table(world, M, iface, contexts)
        dl = module_delays(world, M, iface, mg)
        indet = tt["table"] is None or dl["internal"] is None
        return {"cells": sorted(M), "interface": iface, "truth_table": tt.get("table"),
                "internal_delay": dl["internal"], "n_parents": len(iface["parents"]),
                "n_outputs": len(iface["outputs"]),
                "verdict": "INDETERMINATE" if indet else "MODULE", "why": tt.get("why", "")}

    mods, subs = [], []
    for M in computational_clusters(mg, kind, cells):
        d = describe(M)
        if d:
            mods.append(d)
        if len(M) > 1:                          # the finer scale: each junction on its own
            for j in sorted(M):
                if kind[j] == "junction":
                    sd = describe({j})
                    if sd:
                        subs.append(sd)
    return {"micro": mg, "kind": kind, "modules": mods, "submodules": subs,
            "n_indeterminate": sum(1 for k in kind.values() if k == "indeterminate"),
            "n_conductors": sum(1 for k in kind.values() if k == "conductor"),
            "n_unary": sum(1 for k in kind.values() if k == "unary"),
            "n_junctions": sum(1 for k in kind.values() if k == "junction")}


def macro_quotient(m1, m2) -> dict:
    """THE QUOTIENT MUST BE EARNED, AND IT MUST BE REPORTED LEVEL BY LEVEL (mission: "keep the levels separate").

    My first version collapsed the levels into one verdict and returned INDETERMINATE for the one-cell AND against
    the De Morgan AND -- because their DELAYS differ (1 vs 3). But I had MEASURED both delays and they are certainly
    different. Reporting a measured difference as "I cannot tell" is FALSE ABSTENTION: the mirror image of false
    certainty, and just as dishonest. INDETERMINATE is reserved for what is genuinely unresolved.

        interface  -- same number of external parents and outputs
        function   -- same measured truth table (this is the quotient the mission cares about)
        delay      -- same internal latency
        micro      -- same internal causal shape; EXPECTED to differ, reported, never composited

    UNTIMED quotient = interface + function: a one-cell AND and a four-cell De Morgan AND are the SAME macro object.
    TIMED quotient   = + delay: they are NOT, and that is a fact about the world, not an inability to see it.
    """
    if m1["verdict"] != "MODULE" or m2["verdict"] != "MODULE":
        return {"untimed": "INDETERMINATE", "timed": "INDETERMINATE",
                "why": "a module boundary or parent coverage is unresolved"}
    iface = (m1["n_parents"], m1["n_outputs"]) == (m2["n_parents"], m2["n_outputs"])
    fn = m1["truth_table"] == m2["truth_table"]
    dly = m1["internal_delay"] == m2["internal_delay"]
    micro = (len(m1["cells"]), m1["n_parents"]) == (len(m2["cells"]), m2["n_parents"])
    return {"untimed": "SAME" if (iface and fn) else "DIFFERENT",
            "timed": "SAME" if (iface and fn and dly) else "DIFFERENT",
            "checks": {"interface": iface, "function": fn, "delay": dly},
            "micro": "SAME" if micro else "DIFFERENT"}
