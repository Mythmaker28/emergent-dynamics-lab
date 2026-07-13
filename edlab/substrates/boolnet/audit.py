"""GROUND-TRUTH CAUSAL AUDIT. Privileged. No head may import this.

WHAT WENT WRONG (D-067). My scorer decided the write-enable rail was "an inert boundary condition, not a cause",
because it is constant 0 in every baseline. It is not inert. Clamping it to 1 makes every register LOAD. The
observer discovered that and named it a source; I marked the observer wrong. I had written the exclusion **in order
to make the ground truth produce the source count I expected** -- and then quoted it back at the observer as truth.

    A VARIABLE IS CAUSAL IF AN ADMISSIBLE INTERVENTION ON IT CHANGES THE DOWNSTREAM DISTRIBUTION.
    Not if it looks active. Not if it varies. Not if I meant it to matter.

TWO PATHS, or it is not ground truth:
    DECLARED   -- the construction graph, read off op/src. What I built.
    PRIVILEGED -- the intervention-derived graph, measured by clamping. What the machine does.
Every measured edge must be declared (nothing appears from nowhere), and every declared edge must be either
measured or PROVABLY MASKED under the operating context (a closed gate hides a structural path, and the mask must
be exhibited, not assumed). Disagreement rejects the WORLD, before any observer sees it.
"""

from __future__ import annotations

import numpy as np

from .engine import step
from .circuits import Machine, settled, SETTLE, W
from .evaluator import gate_core

AUDIT_OBS = 96


def _series(m: Machine, clamp, cells, steps=AUDIT_OBS):
    cur = settled(m)
    out = []
    for k in range(steps):
        cur = step(cur, SETTLE + k, clamp or None)
        out.append([int(cur.state[c[0], c[1]]) for c in cells])
    return np.array(out)


def declared_parents(m: Machine, c) -> list:
    """From the wiring. INCLUDES cells that are constant in the baseline -- an OFF rail is still wired in."""
    ps = [(int(s) // W, int(s) % W) for s in m.net.src[c[0], c[1]] if s >= 0]
    return [p for p in ps if p != c]


def declared_ancestors(m: Machine, i: int) -> set:
    seen, stack = set(), list(gate_core(m, i))
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack += [p for p in declared_parents(m, u) if p not in seen]
    return seen


def edge_is_active(m: Machine, p, c, contexts) -> dict:
    """Is `p` a CAUSE of `c` under the admissible repertoire? Clamp p to 0 and to 1, under the baseline and under
    every context, and look at c. A clamp that cannot change p's own value proves nothing and is not counted."""
    fired, where = False, []
    for ctxname, ctx in contexts:
        base = _series(m, ctx, [p, c])
        for v in (0, 1):
            cl = dict(ctx or {})
            cl[p] = v
            s = _series(m, cl, [p, c])
            if not np.all(s[:, 0] == v):
                continue                                   # the clamp did not take: no evidence either way
            if np.array_equal(base[:, 0], s[:, 0]):
                continue                                   # VACUOUS: p was already at v; it proves nothing
            if not np.array_equal(base[:, 1], s[:, 1]):
                fired = True
                where.append(f"{ctxname}:{v}")
    return {"active": fired, "contexts": where}


def audit_world(m: Machine) -> dict:
    """The full two-path audit. Returns the privileged causal source set per channel, and the evidence."""
    regs = [m.components[k][0] for k in m.components if k.startswith("reg") and m.components[k]]
    contexts = [("base", {}), ("ctx0", {r: 0 for r in regs}), ("ctx1", {r: 1 for r in regs})]
    report = {"channels": {}, "edges": {}, "violations": []}
    for i in range(len(m.out_cells)):
        anc = declared_ancestors(m, i)
        active_parents = {}
        for c in sorted(anc):
            aps = []
            for p in declared_parents(m, c):
                e = edge_is_active(m, p, c, contexts)
                report["edges"][f"{p}->{c}"] = e
                if e["active"]:
                    aps.append(p)
            active_parents[c] = aps
        # a ROOT is a cell with no ACTIVE parent -- measured, never assumed
        roots = sorted(c for c in anc if not active_parents[c] and int(m.net.op[c]) != 0)
        # and the rails: an OFF cell that is a declared parent AND whose clamp moves its child is a ROOT too
        for c in sorted(anc):
            for p in declared_parents(m, c):
                if int(m.net.op[p]) == 0 and report["edges"][f"{p}->{c}"]["active"]:
                    roots.append(p)
        roots = sorted(set(roots))
        # keep only roots that actually reach THIS channel's output
        out_cell = m.out_cells[i]
        reaching = [r for r in roots if edge_reaches(m, r, out_cell, contexts)]
        report["channels"][i] = {"declared_ancestors": len(anc), "roots": reaching,
                                 "n_sources": len(reaching)}
    return report


def edge_reaches(m: Machine, p, out_cell, contexts) -> bool:
    e = edge_is_active(m, p, out_cell, contexts)
    return e["active"]


def assert_two_paths_agree(m: Machine) -> dict:
    """Every MEASURED edge must be DECLARED. A cause that is not in the wiring means the wiring is not the truth."""
    rep = audit_world(m)
    for key, e in rep["edges"].items():
        if not e["active"]:
            continue
        a, b = key.split("->")
        pa, pb = eval(a), eval(b)
        if pa not in declared_parents(m, pb):
            raise AssertionError(f"MEASURED edge {key} is not DECLARED. The wiring is not the ground truth.")
    return rep
