"""BLIND HIERARCHICAL DISCOVERY for the Boolean-network world. EXP-GT-HIERARCHY-00.

THE OBSERVER RECEIVES ONLY: raw binary cell trajectories; the grid dimensions; the coordinates and times of ITS
OWN interventions and their results; and the declared I/O interface (which cells are outputs).

IT NEVER RECEIVES: a bounding box, component positions, the NUMBER of components, channel locations, the clock
period, program bits, the causal graph, or the DEPTH of the hierarchy. Nothing in this module imports from the
evaluator, and no count is hard-coded at any rung.

THREE ADDENDA ARE BINDING HERE (docs/HIERARCHY_ADDENDA.md):
  A1  admission and atomicity are SCALE-RELATIVE. Nested substructure is EXPECTED of a composite, not penalised.
      A sub-part disqualifies its parent only if it leaks an EXTERNAL interface the parent does not have.
  A2  architecture is MULTI-SCALE: micro / component / circuit / machine. Two implementations are DIFFERENT at
      micro and may be SAME at macro ONLY if the observer itself establishes functional + interface + delay
      equivalence. The evaluator never grants the quotient.
  A3  structure is CONTEXT-DEPENDENT. Edges are conditional (X -> Y | S=1). Contexts are DISCOVERED, never given.
      A structural graph is COMPLETE only after a context-coverage certificate; otherwise it is
      STRUCTURAL_GRAPH_INCOMPLETE -- never a false absence.
"""

from __future__ import annotations

import itertools

import numpy as np

from ..substrates.boolnet.engine import step

OBS = 96              # every comparison uses EXACTLY this window
SETTLE = 64
PULSE = 1             # a ONE-step clamp: the memory probe
OBS_MEM = OBS         # window for the memory pulse -- the FULL window, and it must be.
                      # MEASURED: at OBS_MEM = 48 the observer declared eight BUS cells to be memory. They are
                      # not. A one-step blip injected on the bus takes ~47 steps to travel the bus, down the far
                      # channel, through its gate and down the output wire -- so it ARRIVES inside the tail and a
                      # LATE TRANSIENT LOOKS PERMANENT. The permanence test is only valid on a window longer than
                      # the LONGEST CAUSAL PATH PLUS the transient. Impatience does not measure memory.
MAX_PERIOD = 64


# ------------------------------------------------------------------ the observer's only access to the world
class World:
    """The information barrier, made a class so it cannot be bypassed by accident."""

    def __init__(self, net, out_cells):
        self._net = net
        self.out_cells = tuple(out_cells)          # the declared I/O interface
        self.H, self.W = net.H, net.W
        self.n_interventions = 0

    def _settled(self):
        if getattr(self, "_s0", None) is None:
            cur = self._net
            for k in range(SETTLE):
                cur = step(cur, k)
            self._s0 = cur
        return self._s0

    def trace(self, clamp=None, hold=OBS, steps=OBS):
        """clamp = {(r,c): v}. hold = how many steps it is held (OBS = ABLATION, 1 = PULSE)."""
        if clamp:
            self.n_interventions += 1
        cur = self._settled()
        grids, outs = [], []
        for k in range(steps):
            cl = clamp if (clamp and k < hold) else None
            cur = step(cur, SETTLE + k, cl)
            grids.append(cur.state.copy())
            outs.append(tuple(int(cur.state[r, c]) for (r, c) in self.out_cells))
        return np.stack(grids), outs

    def raw(self, steps=OBS):
        return self.trace()[0]

    def pulse_at(self, cell, value, at_step, steps, bg=None):
        """Force `cell` to `value` at EXACTLY one step, against a background context `bg` held for the whole window.
        The only way to isolate a DIRECT causal edge: an indirect effect needs at least two steps, so whatever
        deviates one step later is a direct child and nothing else. The pulse OVERRIDES bg at its own step, so a
        context variable can itself be pulsed."""
        self.n_interventions += 1
        cur = self._settled()
        grids = []
        for k in range(steps):
            cl = dict(bg) if bg else {}
            if k == at_step:
                cl[cell] = value
            cur = step(cur, SETTLE + k, cl or None)
            grids.append(cur.state.copy())
        return np.stack(grids)


# ------------------------------------------------------------------ rung 1-4: micro-patterns, clock, channels
def infer_period(frames, max_p=MAX_PERIOD) -> int:
    """The SMALLEST exact period of the settled trajectory. Harmonics cannot be reported by construction."""
    for p in range(1, max_p + 1):
        if len(frames) > 2 * p and all(np.array_equal(frames[i], frames[i + p])
                                       for i in range(len(frames) - p)):
            return p
    raise AssertionError("no exact period: the world is not settled")


def cell_classes(frames, T):
    """RUNG 1: classify every cell by its OWN time series over one period. No labels, no interventions."""
    A = frames[:T]
    cls = {}
    for r in range(frames.shape[1]):
        for c in range(frames.shape[2]):
            s = tuple(int(x) for x in A[:, r, c])
            if not any(s):
                cls[(r, c)] = "silent"
            elif all(s):
                cls[(r, c)] = "constant_high"
            else:
                cls[(r, c)] = "oscillating"
    return cls


def propagation(frames, T, cls):
    """RUNG 2-3: signal velocity and channels, from OBSERVATION alone.

    A cell that COPIES a neighbour reproduces that neighbour's series shifted by exactly one step. Finding those
    pairs gives cell-to-cell causal edges -- the MICRO architecture -- with no intervention at all. (It cannot see
    gates, whose output is a function of two inputs; those need interventions.)"""
    A = frames
    edges = []
    for (r, c), k in cls.items():
        if k != "oscillating":
            continue
        s = A[1:, r, c]
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = r + dr, c + dc
            if not (0 <= rr < A.shape[1] and 0 <= cc < A.shape[2]):
                continue
            if cls.get((rr, cc)) != "oscillating":
                continue
            if np.array_equal(s, A[:-1, rr, cc]):
                edges.append(((rr, cc), (r, c)))    # (rr,cc) -> (r,c) with lag 1
    return edges


# ------------------------------------------------------------------ rung 7: MEMORY, by the transient/permanent test
def memory_cells(world: World, cls, base_out) -> list:
    """THE MEMORY SIGNATURE, and nothing else in the world produces it:

        a TRANSIENT perturbation with a PERMANENT effect.

    Pulse every non-silent cell for ONE step. If the output is still deviating at the END of the window, the cell
    holds state -- it is on a causal CYCLE. A feed-forward path forgets."""
    mem = []
    for (r, c), k in cls.items():
        # EVERY cell is pulsed, including SILENT ones. A register holding 0 is SILENT -- pulse it to 1 and, because
        # its next state is its OWN state, it LATCHES at 1 forever. My first version skipped silent cells and would
        # have missed every zero-bit of the program. A memory that happens to be holding 0 is still a memory.
        for v in (0, 1):
            _, out = world.trace({(r, c): v}, hold=PULSE, steps=OBS_MEM)
            b = base_out[:OBS_MEM]
            if out == b:
                continue                             # the pulse changed nothing: not evidence of anything
            # PERMANENT = still deviating over the LAST FULL PERIOD, not merely at some late step.
            late = any(out[i] != b[i] for i in range(OBS_MEM - 8, OBS_MEM))
            if late:
                mem.append((r, c))
                break
    return sorted(set(mem))


# ------------------------------------------------------------------ rung 5-6, 9-12: ablation signatures
def ablation_signatures(world: World, cls, base_out, context=None):
    """ABLATION = clamp for the WHOLE window (a clamp is reversible; a brief one measures only a transient).
    Returns, per cell, the set of (output, first-deviation-delay) it controls, under the given CONTEXT."""
    ctx = {c: 1 for c in (context or [])}
    cand = {p for p, k in cls.items() if k != "silent"}
    if ctx:
        grids, base_out = world.trace(ctx, hold=OBS)
        # A CELL THAT IS SILENT IN THE BASELINE NEED NOT BE SILENT UNDER THE CONTEXT. A register holding 0 is
        # silent; open the gates and it -- and the whole channel behind it -- comes alive. Restricting the probe
        # to baseline-active cells therefore hides exactly the structure the context exists to reveal, and it did:
        # reg1 came back with an EMPTY interface. The candidate set is the union over baseline AND context.
        act = grids.any(0)
        cand |= {(r, c) for r, c in zip(*np.nonzero(act))}
        cand |= set(context or [])
    sig = {}
    for (r, c) in sorted(cand):
        cl = dict(ctx)
        cl[(r, c)] = 0
        _, out = world.trace(cl, hold=OBS)
        tg = {}
        for j in range(len(world.out_cells)):
            d = [i for i in range(OBS) if out[i][j] != base_out[i][j]]
            if d:
                tg[j] = d[0]
        if tg:
            sig[(r, c)] = tg
    return sig, base_out


def source_cells(cls, prop, sig, mem):
    """Cells that COPY NOBODY yet drive the world: the SOURCES (here, the clock)."""
    has_parent = {dst for (_s, dst) in prop}
    return sorted(c for c in sig if c not in has_parent and c not in mem and cls.get(c) == "oscillating")


def gate_cells(world: World, mem, sig, base_grids):
    """RUNG 5-6: INTERACTION LOCI and GATES -- found by INTERVENTION, because observation CANNOT find them.

    A wire is a lag-1 copy of a neighbour. So is an AND gate whose other input happens to be held at 1:
    AND(x, 1) = x. **An open gate is observationally indistinguishable from a wire.** My first detector looked for
    cells that copy nobody and duly found the clock -- a source -- and none of the gates. Observation alone cannot
    see a gate; only a counterfactual can.

    A GATE is where a SIGNAL path and a MEMORY path MEET. So: clamp each discovered memory cell and take the
    EARLIEST cell in its influence cone that is not the memory cell itself. That cell is the interaction locus."""
    gates = set()
    for mc in mem:
        for v in (0, 1):
            grids, _ = world.trace({mc: v}, hold=OBS)
            diff = (grids != base_grids)
            if not diff.any():
                continue
            first = {}
            for t in range(diff.shape[0]):
                for (r, c) in zip(*np.nonzero(diff[t])):
                    cell = (int(r), int(c))
                    # a MEMORY cell is never a gate. The write-enable's influence cone begins at the REGISTERS
                    # themselves, so without this the observer proposes a register as an interaction locus.
                    if cell not in first and cell != mc and cell not in mem:
                        first[cell] = t
            if not first:
                continue
            t0 = min(first.values())
            for cell, t in first.items():
                if t == t0 and cell in sig:
                    gates.add(cell)
    return sorted(gates)


def refine_components(comps, gates, mem, sig, prop):
    """Split each interface group at its GATES and MEMORY cells. A wire RUN is then a maximal chain of conducting
    cells; the gate is its own component; the register is its own. No count is assumed anywhere: the partition is
    read off the propagation graph and the interface, not off a number."""
    out = []
    for o in comps:
        cells = set(o["cells"])
        special = [c for c in cells if c in gates or c in mem]
        rest = cells - set(special)
        for c in special:
            out.append({"cells": [c], "interface": o["interface"], "kind": "gate" if c in gates else "memory",
                        "delays": {j: sig[c][j] for j in sig.get(c, {})}})
        # connected runs of the remaining conducting cells
        rem = set(rest)
        while rem:
            seed = rem.pop()
            grp, fr = [seed], [seed]
            while fr:
                (r, cc) = fr.pop()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    n = (r + dr, cc + dc)
                    if n in rem:
                        rem.discard(n)
                        grp.append(n)
                        fr.append(n)
            ds = {}
            for j in o["interface"]:
                vals = [sig[x][j] for x in grp if j in sig.get(x, {})]
                if vals:
                    ds[j] = min(vals)
            out.append({"cells": sorted(grp), "interface": o["interface"], "kind": "wire_run", "delays": ds})
    return out


# ------------------------------------------------------------------ A1: SCALE-RELATIVE object proposal
def propose_components(sig, mem):
    """RUNG 6/12: propose COMPONENTS -- maximal causally-coherent cell groups. No count is assumed.

    Cells are grouped by their EXTERNAL INTERFACE (the SET of outputs they control), then split into spatially
    connected pieces. A wire chain shares one interface and forms one connected run; its delay GRADIENT along the
    chain is the signal's velocity. A gate sits at the head of its channel and is separated because it is where
    two interfaces meet. Memory cells are their own components (their signature is unique).
    """
    groups = {}
    for cell, tg in sig.items():
        key = ("mem",) + tuple(sorted(tg)) if cell in mem else tuple(sorted(tg))
        groups.setdefault(key, []).append(cell)
    comps = []
    for key, cells in groups.items():
        rem = set(cells)
        while rem:
            seed = rem.pop()
            grp = [seed]
            frontier = [seed]
            while frontier:
                (r, c) = frontier.pop()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    n = (r + dr, c + dc)
                    if n in rem:
                        rem.discard(n)
                        grp.append(n)
                        frontier.append(n)
            comps.append({"cells": sorted(grp), "interface": tuple(k for k in key if not isinstance(k, str)),
                          "is_memory": key[0] == "mem" if key and isinstance(key[0], str) else False,
                          "delays": {j: min(sig[x][j] for x in grp) for j in sig[seed]}})
    return comps


def admit_object(obj, sig, level="component") -> dict:
    """A1 -- SCALE-RELATIVE ADMISSION. Nested substructure is EXPECTED of a composite, not penalised.

    A sub-part disqualifies its parent ONLY IF it leaks an EXTERNAL interface at this level that the parent does
    not have. That is the merged-blob signature (D-061: the relief opened an output the whole blob left dead).
    A De Morgan gate's internal NOT has a different INTERNAL effect from the gate's -- and that is simply what it
    means to be made of parts."""
    parent_iface = set(obj["interface"])
    leaks = []
    for cell in obj["cells"]:
        child_iface = set(sig.get(cell, {}))
        extra = child_iface - parent_iface
        if extra:
            leaks.append({"cell": cell, "leaked_outputs": sorted(extra)})
    if leaks:
        return {"verdict": "OUT_OF_SCOPE", "level": level, "why": "a sub-part leaks an external interface the "
                "object does not have -- this is an unresolved MERGE, not a composite", "leaks": leaks}
    if not parent_iface:
        return {"verdict": "INERT", "level": level, "why": "no external causal interface"}
    return {"verdict": "ADMITTED", "level": level, "n_cells": len(obj["cells"]),
            "why": "resolvable and causally coherent at this level; nested substructure permitted"}


# ------------------------------------------------------------------ A3: CONTEXT-DEPENDENT structure
def discover_contexts(mem):
    """A3 -- contexts are DISCOVERED, never given. The candidates are the memory cells found at rung 7: the cells
    whose transient perturbation has a permanent effect. NO evaluator state enters here."""
    return list(mem)


def conditional_structural_graph(world: World, cls, base_out, contexts):
    """A3 -- edges are explicitly CONDITIONAL: X -> Y | S=1.

    Structure behind a closed gate is NOT identifiable from single interventions (D-062, measured). So probe under
    each discovered context (and under the empty context) and record the condition under which each edge appears.
    An edge seen with no context is unconditional."""
    edges = {}
    ctx_sets = [()] + [tuple(sorted(contexts))]
    for ctx in ctx_sets:
        sig, _ = ablation_signatures(world, cls, base_out, context=list(ctx))
        for cell, tg in sig.items():
            for j, d in tg.items():
                key = (cell, j)
                cond = "" if ctx == () else f"|ctx={len(ctx)}mem=1"
                if key not in edges:
                    edges[key] = {"delay": d, "condition": cond}
                elif edges[key]["condition"] and not cond:
                    edges[key] = {"delay": d, "condition": ""}      # unconditional beats conditional
    return edges


def context_coverage_certificate(edges, contexts, controls) -> dict:
    """A3 -- a structural graph may be declared COMPLETE only after enough discovered contexts have been explored
    to reveal the KNOWN CONDITIONAL PATHS ON DEVELOPMENT CONTROLS. Otherwise: STRUCTURAL_GRAPH_INCOMPLETE.

    `controls` is a list of (cell, output) pairs that a DEVELOPMENT control says must be reachable under SOME
    discovered context. It is a development-time calibration of the observer's completeness, never a held-out one,
    and it is used only to decide COMPLETE vs INCOMPLETE -- never to add an edge the observer did not find."""
    found = {(c, j) for (c, j) in edges}
    missing = [x for x in controls if x not in found]
    if not contexts:
        return {"verdict": "STRUCTURAL_GRAPH_INCOMPLETE", "why": "no context variable was discovered, so any "
                "path behind a closed gate would be reported as ABSENT -- a false absence",
                "missing_controls": missing}
    if missing:
        return {"verdict": "STRUCTURAL_GRAPH_INCOMPLETE", "n_contexts": len(contexts),
                "why": "known conditional paths were not revealed by the contexts explored",
                "missing_controls": missing}
    return {"verdict": "COMPLETE", "n_contexts": len(contexts), "n_edges": len(edges)}


# ------------------------------------------------------------------ A2: MULTI-SCALE architecture
def micro_graph(prop_edges, sig):
    """MICRO level: cell-to-cell edges, from observation (copy-with-lag-1) plus the ablation interface."""
    return {"n_cells_with_interface": len(sig), "n_cell_edges": len(prop_edges),
            "signature": (len(sig), len(prop_edges))}


def component_graph(comps):
    """COMPONENT / CIRCUIT level: the graph over discovered components. Isomorphism-invariant: components enter
    only through their interface (the SET of outputs they control) and their delays -- never their position."""
    rows = []
    for o in comps:
        if not o["interface"]:
            continue
        rows.append((tuple(sorted(o["interface"])), o.get("kind", "mem" if o.get("is_memory") else "wire_run"),
                     tuple(sorted(o["delays"].items()))))
    return {"n_components": len(rows), "signature": tuple(sorted(rows))}


def series_lag(frames, a, b, max_lag=16):
    """The exact lag L with series(b)[t] = series(a)[t-L]. Phase-invariant by construction: it aligns the SIGNALS,
    it does not time an event."""
    sa = frames[:, a[0], a[1]]
    sb = frames[:, b[0], b[1]]
    for L in range(0, max_lag + 1):
        if L == 0:
            if np.array_equal(sa, sb):
                return 0
        elif np.array_equal(sa[:-L], sb[L:]):
            return L
    return None


def through_latency(obj, sig, frames=None):
    """The latency THROUGH an object -- measured by SERIES ALIGNMENT, never by an ablation ONSET.

    AN ONSET IS NOT A DELAY. The onset is the first step at which the ablated output differs from the baseline,
    and with a square-wave clock that depends on the PHASE, not on the path length. MEASURED: the three cells of
    a delay-matched buffered gate gave onsets 17 / 17 / 12, so the "latency through the object" came out as 6
    instead of 3 -- and the observer refused a quotient it should have earned. This is the same disease that
    killed A-head V2 and V3 in the Game-of-Life world, in a new substrate: a phase-contaminated timing estimate
    wearing the costume of a causal delay.

    Under a context that opens the gates, AND(x, 1) = x, so an object's output cell is an exact lagged COPY of
    its input cell. The lag between the object's input-side and output-side cells IS its latency, and it is
    invariant to the clock phase because it aligns the signals rather than timing an event.
    """
    if frames is None:
        out = {}
        for j in obj["interface"]:
            ons = [sig[c][j] for c in obj["cells"] if j in sig.get(c, {})]
            if ons:
                out[j] = max(ons) - min(ons) + 1
        return tuple(sorted(out.items()))
    cells = [c for c in obj["cells"] if c in sig]
    if not cells:
        return ()
    j = sorted(obj["interface"])[0]

    # POLARITY. With a 50%-duty clock, NOT(x) is INDISTINGUISHABLE from x delayed by half a period -- a genuine
    # identifiability trap of a symmetric square wave. Aligning two INTERNAL cells of a De Morgan gate, one of
    # which carries the INVERTED signal, therefore returned a lag of 6 for an object whose true latency is 3.
    # The object AS A WHOLE is non-inverting (that is what "implements AND" means), so we align its EXTERNAL
    # neighbours instead: the cell that feeds it and the cell it feeds. Polarity confounds vanish, because both
    # of those carry the un-inverted signal.
    inside = set(obj["cells"])
    nbrs = set()
    for (r, c) in inside:
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            n = (r + dr, c + dc)
            if n not in inside and n in sig and j in sig[n]:
                nbrs.add(n)
    if len(nbrs) < 2:
        return ()
    # ORDER THE NEIGHBOURS BY SERIES ALIGNMENT, NOT BY ONSET. The ablation onset is phase-quantized -- the three
    # cells of a buffered gate all reported onsets of 17/17/12 -- so it cannot even ORDER them reliably. The lag
    # that aligns two signals can. u leads v by exactly the path length through the object plus one wire step.
    best = None
    for a in nbrs:
        for b in nbrs:
            if a == b:
                continue
            L = series_lag(frames, a, b)
            if L is not None and L >= 1 and (best is None or L < best):
                best = L                      # the SMALLEST positive alignment: aliases are larger by a period
    return () if best is None else (("latency", best - 1),)


def establish_macro_equivalence(w1: World, o1, w2: World, o2, probe_inputs) -> dict:
    """A2 -- THE OBSERVER MUST EARN THE QUOTIENT. Two objects are the SAME macro-component only if IT establishes
    all three, by measurement:
        1. FUNCTIONAL equivalence  -- identical I/O over a probed input set;
        2. EXTERNAL INTERFACE equivalence -- the same in/out edges at the component level;
        3. DELAY equivalence       -- the same measured latency through the object.
    The evaluator never grants this. If any one fails, the macro verdict is INDETERMINATE, not SAME."""
    checks = {}
    f1 = [w1.trace(p, hold=OBS)[1] for p in probe_inputs]
    f2 = [w2.trace(p, hold=OBS)[1] for p in probe_inputs]
    checks["functional_equivalence"] = (f1 == f2)
    checks["interface_equivalence"] = (tuple(sorted(o1["interface"])) == tuple(sorted(o2["interface"])))
    # DELAY EQUIVALENCE IS MEASURED **THROUGH THE OBJECT**, not by where the object sits.
    # The per-output ablation ONSET tells you how far the object is from the output -- that is GEOMETRY (G).
    # The LATENCY THROUGH the object is the SPREAD of those onsets across its own cells: the input-side cell
    # fires later than the output-side cell by exactly the object's internal latency. Comparing onsets instead
    # would make two identical gates at different distances from the output look non-equivalent -- G leaking
    # into A_TAU, the very error this ontology exists to prevent.
    checks["delay_equivalence"] = (o1.get("through_latency") == o2.get("through_latency"))
    ok = all(checks.values())
    return {"verdict": "SAME" if ok else "INDETERMINATE", "checks": checks,
            "why": "" if ok else "the observer could not establish all three; the quotient is NOT granted"}


# ------------------------------------------------------------------ resumable discovery cache
import hashlib as _hl
import os as _os
import pickle as _pk

_DCACHE = _os.path.join("results", "_hier_cache")


def discover(m, controls=None) -> dict:
    """THE FULL LADDER, blind. `m` is a Machine; ONLY `m.net` and `m.out_cells` are ever touched, and only
    through the World barrier. Memoised on disk: nothing scientific changes, it lets a run resume."""
    _os.makedirs(_DCACHE, exist_ok=True)
    k = _hl.sha256(m.net.op.tobytes() + m.net.src.tobytes() + m.net.state.tobytes()
                   + str(m.out_cells).encode() + str(controls).encode()).hexdigest()[:24]
    fp = _os.path.join(_DCACHE, k + ".pkl")
    if _os.path.exists(fp):
        return _pk.load(open(fp, "rb"))

    w = World(m.net, m.out_cells)
    fr, base = w.trace()
    T = infer_period(fr)                                    # rung 4
    cls = cell_classes(fr, T)                               # rung 1
    prop = propagation(fr, T, cls)                          # rungs 2-3
    mem = memory_cells(w, cls, base)                        # rung 7
    ctxs = discover_contexts(mem)                           # A3: contexts are DISCOVERED
    sig, _ = ablation_signatures(w, cls, base, context=ctxs)   # rungs 5-6, 9-12, under an OPEN context
    coarse = propose_components(sig, mem)                   # rung 6/12: group by causal interface
    srcs = source_cells(cls, prop, sig, mem)                # sources: they copy nobody
    gates = gate_cells(w, mem, sig, fr)                     # rung 5-6: gates, by INTERVENTION (see docstring)
    comps = refine_components(coarse, gates, mem, sig, prop)
    adm = [admit_object(o, sig) for o in comps]             # A1: scale-relative admission
    cond = conditional_structural_graph(w, cls, base, ctxs)  # A3: conditional edges
    cov = context_coverage_certificate(cond, ctxs, controls or [])
    out = {"period": T, "cell_classes": cls, "propagation": prop, "memory": mem, "contexts": ctxs,
           "gates": gates, "sources": srcs, "coarse_components": coarse,
           "signatures": sig, "components": comps, "admission": adm, "conditional_edges": cond,
           "context_coverage": cov, "micro": micro_graph(prop, sig), "component_graph": component_graph(comps),
           "n_interventions": w.n_interventions}
    _pk.dump(out, open(fp, "wb"))
    return out
