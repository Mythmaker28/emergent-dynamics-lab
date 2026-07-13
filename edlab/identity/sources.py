"""THE SOURCE-TRANSDUCER OBSERVER. Conceptually new (EXP-GT-SOURCE-TRANSDUCER-00). Not a repair of D-065.

WHY THE PREVIOUS DESIGN HAD TO GO. It defined a module's inputs as the wires crossing its boundary. But a boundary
is a thing I drew; a cause is a thing the world has. In `xnor_and` two of the three boundary wires carried the SAME
signal at different delays -- a re-timing buffer and the channel it copies. The observer clamped them
independently, which asks the world a question it cannot answer ("what if this wire disagreed with its own
source?"), got a three-input table that reduces to nothing, and said so with complete confidence.

    THE OBJECT IS NO LONGER A BOX WITH WIRES.

    It is a TRANSDUCER from a minimal set of INDEPENDENT CAUSAL SOURCES -- and their HISTORIES -- to an output,
    measured ONLY on the joint source histories the world can actually realize.

FOUR THINGS ARE NOW KEPT APART THAT WERE PREVIOUSLY ONE:

    SPATIAL FRONTIER   every conductor crossing the candidate region. Observable geometry. NOT an interface.
    BOUNDARY TAP      a signal seen on one frontier conductor. Several taps may be one source, delayed or inverted.
    INDEPENDENT SOURCE a process no admissible intervention can change *through another source*. A ROOT.
    REACHABLE MANIFOLD the joint source histories the dynamics can actually produce. Everything else is fiction.

THE CENTRAL MOVE. Interventions are applied to SOURCES, never to taps. A tap is a consequence; clamping it
fabricates a world. A source is a cause; clamping it interrogates this one. Every row of every table below was
GENERATED, and the assertion `assert_manifold_generated` refuses any row that was not.
"""

from __future__ import annotations

import itertools

import numpy as np

from .hier import World, OBS

MAX_LAG = 64          # a source influence arriving later than this is not attributed to that source. The clock
                      # reaches the FURTHEST channel only after crossing the whole bus: at MAX_LAG = 24 the clock
                      # simply vanished as a source for every channel but the first, and the observer reported
                      # one-source transducers. A horizon shorter than the causal path does not measure absence.
MAX_HISTORY = 6       # the longest lag window the transducer search will consider before abstaining
MAX_SOURCES = 5       # beyond this the joint source assignment is not enumerated: INDETERMINATE, not a guess
SETTLE_MARGIN = 32    # samples before this are discarded: an intervention's transient is not its function


# ====================================================================== 1. the micro causal graph (measurement)
def micrograph(world: World, cells, period, contexts=()) -> dict:
    """Direct causal edges by ONE-STEP PULSE, under baseline and every discovered context, unioned.

    This is a MEASUREMENT primitive, not verdict logic: flip one cell at exactly step t and nothing else differs at
    step t, so whatever differs at t+1 is a direct child and nothing else. Polarity is read off the pulse itself --
    the parent was FORCED to v, so the child's value at t+1 is that edge's transfer function evaluated at v. Both
    facts are non-vacuous by construction. Edges are recorded WITH the contexts in which they fire, because a
    saturated gate masks a structural edge that is really there.
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
                    continue
                for (r, c) in zip(*np.nonzero(g[t + 1] != base[t + 1])):
                    q = (int(r), int(c))
                    if q == p or q not in children:
                        continue
                    children[p].add(q)
                    cond.setdefault((p, q), set()).add(name)
                    pol.setdefault((p, q), set()).add(1 if int(g[t + 1][r, c]) == v else 0)
    parents = {c: set() for c in cells}
    for p, ch in children.items():
        for q in ch:
            parents[q].add(p)
    return {"children": children, "parents": parents, "pol": pol, "cond": cond}


def classify(mg, cells) -> dict:
    """source (no parents) | conductor (one parent, carries it) | unary (one parent, transforms it) | junction."""
    kind = {}
    for y in cells:
        ps = sorted(mg["parents"][y])
        if not ps:
            kind[y] = "source"
        elif len(ps) >= 2:
            kind[y] = "junction"
        else:
            pl = mg["pol"].get((ps[0], y), set())
            kind[y] = "conductor" if pl == {1} else ("indeterminate" if not pl else "unary")
    return kind


def candidate_regions(mg, kind, cells) -> list:
    """PROPOSALS ONLY (mission SS2). The conductor-bounded computing cluster is retained as a way to PROPOSE where
    to look. It defines nothing: not the inputs, not the arity, not the truth-table axes, not equivalence. Those
    are inferred below, from sources. This is the one thing the retired design got right, demoted to its proper
    role -- a hypothesis about where a computation lives, not a claim about what it depends on."""
    comp = {c for c in cells if kind.get(c) in ("junction", "unary")}
    seen, out = set(), []
    for c0 in sorted(comp):
        if c0 in seen:
            continue
        stack, M = [c0], set()
        while stack:
            u = stack.pop()
            if u in M:
                continue
            M.add(u)
            for v in list(mg["children"][u]) + list(mg["parents"][u]):
                if v in comp and v not in M:
                    stack.append(v)
        seen |= M
        out.append(M)
    return out


def candidate_cells(world: World, contexts) -> list:
    """Cells active in the baseline OR under any discovered context. A cell that is constant zero today can still
    be a cause tomorrow: De Morgan's NOT(reg) is silent while the register holds 1, and a candidate set built from
    baseline activity alone would never see it. A part of the machine that is quiet is still part of the machine."""
    act = world.trace(None, hold=OBS, steps=OBS)[0].any(0)
    for c in contexts:
        for v in (0, 1):
            act |= world.trace({c: v}, hold=OBS, steps=OBS)[0].any(0)
    return sorted((int(r), int(c)) for r, c in zip(*np.nonzero(act)))


# ====================================================================== 2. source tracing
def roots_of(mg, cells) -> list:
    """A ROOT is a cell with no causal parent: a clock, a held register, an external input. Everything else in the
    machine is a consequence of these. They are the only things it is meaningful to intervene ON."""
    return sorted(c for c in cells if not mg["parents"][c])


def ancestry(tap, mg, roots) -> dict:
    """Trace one tap back through the micrograph to the roots that feed it, recording the shortest path length
    (a DELAY) and whether the chain inverts (a POLARITY). Geometric proximity is never consulted: a register
    sits nowhere near the gate it opens, and the wire next to a signal is not its cause."""
    dist, pol_, frontier = {tap: 0}, {tap: 1}, [tap]
    rootset = set(roots)
    hit = {}
    while frontier:
        nxt = []
        for u in frontier:
            if u in rootset:
                if u not in hit:
                    hit[u] = {"lag": dist[u], "pol": pol_[u]}
                continue
            for p in mg["parents"][u]:
                if p in dist or dist[u] + 1 > MAX_LAG:
                    continue
                carries = mg["pol"].get((p, u), {1}) == {1}
                dist[p] = dist[u] + 1
                pol_[p] = pol_[u] if carries else 1 - pol_[u]
                nxt.append(p)
        frontier = nxt
    return hit


def tap_equivalence(taps, mg, roots) -> dict:
    """SOURCE-TAP EQUIVALENCE CLASSES. Two taps belong to the same source when their ancestries reach the same
    root -- not when their series look alike. A delayed copy of X is X; two registers that happen to hold the same
    bit are two registers.

    This is the single fact whose absence retired the previous observer. It had three parents where the world has
    two causes."""
    anc = {t: ancestry(t, mg, roots) for t in taps}
    classes = {}
    for t in taps:
        for r, info in anc[t].items():
            classes.setdefault(r, []).append({"tap": t, "lag": info["lag"], "pol": info["pol"]})
    return {"ancestry": anc, "by_source": classes}


# ====================================================================== 3. source independence certificate
def classify_pair(world: World, s1, s2, mg, roots, period) -> dict:
    """Can an admissible intervention move ONE source while leaving the OTHER's history intact?

    Correlation is not dependence and synchronization is not identity. Two registers holding the same bit have
    IDENTICAL series in every baseline and are two sources; a wire and its own buffer have identical series up to a
    delay and are one. Only an intervention tells them apart, and only an intervention is allowed to.
    """
    if s1 == s2:
        return {"verdict": "SAME_SOURCE_DIFFERENT_TAP", "why": "one cell"}
    ra, rb = set(ancestry(s1, mg, roots)), set(ancestry(s2, mg, roots))
    if not ra or not rb:
        return {"verdict": "UNRESOLVED", "why": "ancestry reaches no root"}
    if ra == rb and len(ra) == 1:
        # TWO TAPS OF ONE CAUSE. A wire and its own buffer; a channel and its re-timed copy. Under intervention
        # they look INDEPENDENT -- pulsing one leaves the other untouched, because they are SIBLINGS, not parent
        # and child. That is precisely the illusion that retired the previous observer. Only ANCESTRY sees it.
        return {"verdict": "SAME_SOURCE_DIFFERENT_TAP", "why": f"both trace to the single root {sorted(ra)[0]}"}
    if ra & rb:
        return {"verdict": "DEPENDENT_COMMON_CAUSE",
                "why": f"ancestries share {sorted(ra & rb)}: one is a function of the other's cause and more"}
    # NOTE: World.raw() silently ignores its `steps` argument and always returns OBS frames. Comparing its output
    # against a short pulse trace can therefore NEVER be equal, and every source pair came back UNRESOLVED. The
    # retired observer's file is hashed and must stay byte-identical, so the fix lives here: use trace(), which
    # honours `steps`. A helper that quietly ignores what you asked it for is worse than one that refuses.
    n = period + 2
    base = world.trace(None, hold=n, steps=n)[0]
    moved_1_only = moved_2_only = False
    for t in range(period):
        for (a, b) in ((s1, s2), (s2, s1)):
            v = 1 - int(base[t][a[0], a[1]])
            g = world.pulse_at(a, v, t, n)
            if int(g[t][a[0], a[1]]) != v:
                continue                                     # vacuous: proves nothing, counts for nothing
            other_intact = np.array_equal(g[:, b[0], b[1]], base[:, b[0], b[1]])
            if other_intact:
                if (a, b) == (s1, s2):
                    moved_1_only = True
                else:
                    moved_2_only = True
    if moved_1_only and moved_2_only:
        return {"verdict": "INDEPENDENT_SOURCES", "why": "each was moved while the other's history was preserved"}
    if moved_1_only or moved_2_only:
        return {"verdict": "DEPENDENT_COMMON_CAUSE", "why": "only one of the two could be moved alone"}
    return {"verdict": "UNRESOLVED", "why": "no admissible intervention separated them"}


# ====================================================================== 4. source lags at the output
def source_lags(world: World, src, out_cell, period, contexts, const_series) -> dict:
    """At WHICH lags does this source reach that output? A pulse on the source at step t makes the output deviate
    at t + d for every d on a causal path. The SET of such d is the source's lag set: one entry per tap of the same
    source. Measured under the baseline and under every context, because a closed gate hides a lag that is there.

    A source whose own series never varies (a held register) has no history: its lag set collapses to its earliest
    influence. A source that varies (the clock) can enter at several lags, and each is a separate argument of the
    transducer -- the same cause, remembered for different lengths of time.
    """
    bgs = [None] + [{c: v for c in contexts} for v in (0, 1)]
    lags, firsts = set(), []
    persistent = False
    for bg in bgs:
        base = world.trace(bg, hold=OBS, steps=OBS)[0]
        for t in range(0, period):
            v = 1 - int(base[t][src[0], src[1]])
            g = world.pulse_at(src, v, t, min(t + MAX_LAG + 2, OBS), bg=bg)
            if int(g[t][src[0], src[1]]) != v:
                continue
            devs = [k - t for k in range(t + 1, len(g))
                    if int(g[k][out_cell[0], out_cell[1]]) != int(base[k][out_cell[0], out_cell[1]])]
            if not devs:
                continue
            firsts.append(min(devs))
            if len(devs) > 2 * MAX_HISTORY:
                persistent = True                    # a PERMANENT change: the source is a state, not a waveform
            else:
                lags |= set(devs)
    # A HELD SOURCE HAS NO HISTORY. Pulsing a register is PERMANENT -- it sticks -- so the output first deviates
    # whenever the channel next happens to be high, and that moment depends on the phase of the pulse. Unioning
    # those per-phase first-deviations gave the register a "lag set" of {1,2,3,4,5,6}: six arguments of a
    # transducer, all of them the same constant, none of them real. A source whose own series never moves enters
    # the output at exactly ONE lag -- the earliest at which it can be shown to matter at all.
    if persistent or const_series:
        return {"lags": [min(firsts)] if firsts else [], "persistent": True}
    return {"lags": sorted(l for l in lags if 1 <= l <= MAX_LAG), "persistent": False}


# ====================================================================== 5. the reachable manifold
def harvest(world: World, sources, lagmap, out_cell, contexts, period) -> dict:
    """GENERATE the reachable joint source histories. Nothing is assumed; every row below was produced by the
    world under an admissible intervention on SOURCES ONLY.

    The runs: every assignment of the CONSTANT sources (registers) to {0,1}, crossed with the VARYING source
    (clock) left FREE, clamped to 0, and clamped to 1. The free runs are what make the off-diagonal reachable:
    a source clamped to a constant can only ever show you (x, x) at two different lags, never (0, 1). Half the
    manifold of a delayed self-tap is invisible to clamping alone, and inventing it is exactly the sin.
    """
    const = [s for s in sources if lagmap[s]["persistent"] or lagmap[s]["const_series"]]
    vary = [s for s in sources if s not in const]
    runs = []
    for assign in itertools.product((0, 1), repeat=len(const)):
        cl = dict(zip(const, assign))
        for vmode in ("free", 0, 1):
            clamp = dict(cl)
            if vmode != "free":
                for s in vary:
                    clamp[s] = vmode
            g, _ = world.trace(clamp or None, hold=OBS, steps=OBS)
            # NON-VACUITY: every clamped source must actually be holding the value we asked for.
            for s, v in clamp.items():
                got = g[SETTLE_MARGIN:, s[0], s[1]]
                if not np.all(got == v):
                    raise AssertionError(
                        f"source clamp {s} -> {v} DID NOT TAKE (series {sorted(set(got.tolist()))}). "
                        f"An intervention that did not happen is not evidence.")
            runs.append({"clamp": dict(clamp), "vmode": vmode, "grid": g})
    # features: for each source, its value at each lag at which it reaches the output
    feats, rows = [], []
    for s in sources:
        for d in lagmap[s]["lags"]:
            feats.append((s, d))
    seen = {}
    for r in runs:
        g = r["grid"]
        for t in range(SETTLE_MARGIN, OBS):
            key = tuple(int(g[t - d][s[0], s[1]]) for (s, d) in feats)
            y = int(g[t][out_cell[0], out_cell[1]])
            rows.append({"key": key, "y": y, "run": len(seen)})
            seen.setdefault(key, set()).add(y)
    return {"feats": feats, "rows": rows, "observed": seen, "runs": runs,
            "n_possible": 1 << len(feats), "n_observed": len(seen)}


def assert_manifold_generated(man):
    """Every reported reachable state was ACTUALLY GENERATED. Nothing is extrapolated, interpolated or assumed."""
    if not man["observed"]:
        raise AssertionError("manifold is empty: no source assignment was generated")
    for k, ys in man["observed"].items():
        if not ys:
            raise AssertionError(f"manifold row {k} has no generated output")
    return True


# ====================================================================== 6. transducer identification
def identify(world: World, sources, lagmap, out_cell, contexts, period) -> dict:
    """The smallest predictive representation from independent source HISTORIES to the output.

    Model classes, in increasing complexity, and the first that is CONSISTENT wins:
        STATIC              one lag per source, output a function of the current source values
        DELAYED_STATIC      one lag per source, but the lags differ
        FINITE_HISTORY(h)   at least one source enters at several lags: the output depends on its past
        FINITE_STATE        no lag window up to MAX_HISTORY explains it: the module remembers something itself
    Consistency is the whole test: if one source-history row ever produced two different outputs, the class is too
    small and is rejected. That single check is what makes the answer falsifiable.

    COVERAGE is reported separately and never rounded up. If the world cannot produce every row, we do not have a
    truth table -- we have a PARTIAL one, and saying otherwise is inventing behaviour.
    """
    if len(sources) > MAX_SOURCES:
        return {"class": "INDETERMINATE", "why": f"{len(sources)} sources: joint assignment not enumerable"}
    man = harvest(world, sources, lagmap, out_cell, contexts, period)
    assert_manifold_generated(man)
    bad = {k: ys for k, ys in man["observed"].items() if len(ys) > 1}
    if bad:
        # the measured lags do not explain the output. Widen each varying source's window and try again.
        for h in range(1, MAX_HISTORY + 1):
            wide = {s: dict(lagmap[s]) for s in sources}
            for s in sources:
                if lagmap[s]["lags"] and not lagmap[s]["persistent"]:
                    d0 = min(lagmap[s]["lags"])
                    wide[s]["lags"] = list(range(d0, d0 + h + 1))
            m2 = harvest(world, sources, wide, out_cell, contexts, period)
            assert_manifold_generated(m2)
            if not any(len(ys) > 1 for ys in m2["observed"].values()):
                return {"class": f"FINITE_HISTORY({h})", "feats": m2["feats"],
                        "table": {k: next(iter(v)) for k, v in m2["observed"].items()},
                        "coverage": m2["n_observed"] / m2["n_possible"],
                        "n_observed": m2["n_observed"], "n_possible": m2["n_possible"],
                        "complete": m2["n_observed"] == m2["n_possible"], "lagmap": wide}
        return {"class": "FINITE_STATE",
                "why": (f"no lag window up to {MAX_HISTORY} explains the output: {len(bad)} source-history rows "
                        f"produced MORE THAN ONE output. The module remembers something the sources do not say."),
                "ambiguous_rows": len(bad), "feats": man["feats"]}
    lags = {s: lagmap[s]["lags"] for s in sources}
    multi = any(len(v) > 1 for v in lags.values())
    single = {s: v[0] for s, v in lags.items() if v}
    cls = ("FINITE_HISTORY(0)" if multi else
           ("STATIC" if len(set(single.values())) <= 1 else "DELAYED_STATIC"))
    return {"class": cls, "feats": man["feats"],
            "table": {k: next(iter(v)) for k, v in man["observed"].items()},
            "coverage": man["n_observed"] / man["n_possible"],
            "n_observed": man["n_observed"], "n_possible": man["n_possible"],
            "complete": man["n_observed"] == man["n_possible"], "lagmap": lagmap}


# ====================================================================== 7. discovery
def discover_transducers(world: World, cells, contexts, period) -> dict:
    mg = micrograph(world, cells, period, contexts)
    kind = classify(mg, cells)
    roots = roots_of(mg, cells)
    out = []
    for M in candidate_regions(mg, kind, cells):
        taps = sorted({p for y in M for p in mg["parents"][y] if p not in M})
        outs = sorted({y for y in M if any(c not in M for c in mg["children"][y])})
        if not taps or not outs:
            continue
        y = outs[0]
        eq = tap_equivalence(taps, mg, roots)
        srcs = sorted(eq["by_source"])
        if not srcs:
            out.append({"cells": sorted(M), "verdict": "INDETERMINATE",
                        "why": "no root source reached: the region's ancestry is unresolved"})
            continue
        lagmap = {}
        for s in srcs:
            ser = world.trace(None, hold=OBS, steps=OBS)[0][:, s[0], s[1]]
            const = bool(ser.min() == ser.max())
            L = source_lags(world, s, y, period, contexts, const)
            L["const_series"] = const
            lagmap[s] = L
        srcs = [s for s in srcs if lagmap[s]["lags"]]              # a root with no lag does not reach this output
        if not srcs:
            out.append({"cells": sorted(M), "verdict": "INDETERMINATE",
                        "why": "no source reaches the output at any measurable lag"})
            continue
        pairs = {}
        for a, b in itertools.combinations(srcs, 2):
            pairs[(a, b)] = classify_pair(world, a, b, mg, roots, period)
        tap_pairs = {(a, b): classify_pair(world, a, b, mg, roots, period)
                     for a, b in itertools.combinations(taps, 2)}
        if any(v["verdict"] == "UNRESOLVED" for v in pairs.values()):
            out.append({"cells": sorted(M), "sources": srcs, "verdict": "INDETERMINATE",
                        "why": "source independence UNRESOLVED", "independence": pairs})
            continue
        tr = identify(world, srcs, lagmap, y, contexts, period)
        n_taps = len(taps)
        rec = {"cells": sorted(M), "out_cell": y, "taps": taps, "n_taps": n_taps, "tap_pairs": tap_pairs,
               "sources": srcs, "n_sources": len(srcs), "tap_classes": eq["by_source"],
               "lags": {s: lagmap[s]["lags"] for s in srcs}, "independence": pairs,
               "transducer": tr, "verdict": "TRANSDUCER" if tr["class"] != "INDETERMINATE" else "INDETERMINATE"}
        # a region with ONE source that merely carries it is not a transducer, it is a wire wearing a hat
        if len(srcs) == 1 and tr.get("class") == "STATIC" and tr.get("complete"):
            tab = tr["table"]
            if tab == {(0,): 0, (1,): 1} or tab == {(0,): 1, (1,): 0}:
                rec["verdict"] = "CONDUCTOR_AT_MACRO"
        out.append(rec)
    return {"micro": mg, "kind": kind, "roots": roots, "transducers": out}


# ====================================================================== 8. the macro quotient, level by level
def quotient(a, b) -> dict:
    """Five verdicts, never composited (mission SS7). A measured difference is reported as DIFFERENT. Behaviour the
    world cannot produce is reported as INDETERMINATE. The two are not the same, and collapsing them -- in either
    direction -- is the failure this observer exists to avoid."""
    if a.get("verdict") not in ("TRANSDUCER",) or b.get("verdict") not in ("TRANSDUCER",):
        return {"SOURCE_INTERFACE": "INDETERMINATE", "UNTIMED_TRANSDUCER": "INDETERMINATE",
                "TIMED_TRANSDUCER": "INDETERMINATE", "MICRO_ARCHITECTURE": "INDETERMINATE",
                "why": "a transducer is unresolved"}
    ta, tb = a["transducer"], b["transducer"]
    iface = (a["n_sources"] == b["n_sources"]
             and sorted(len(v) for v in a["lags"].values()) == sorted(len(v) for v in b["lags"].values()))
    micro = "SAME" if len(a["cells"]) == len(b["cells"]) else "DIFFERENT"

    if not iface or ta["class"].split("(")[0] != tb["class"].split("(")[0]:
        return {"SOURCE_INTERFACE": "SAME" if iface else "DIFFERENT",
                "UNTIMED_TRANSDUCER": "DIFFERENT", "TIMED_TRANSDUCER": "DIFFERENT",
                "MICRO_ARCHITECTURE": micro,
                "why": "different source interface or model class"}

    # compare the functions ONLY where BOTH were observed. Where either is unobserved, we cannot speak.
    ka, kb = set(ta.get("table", {})), set(tb.get("table", {}))
    both, either = ka & kb, ka | kb
    disagree = [k for k in both if ta["table"][k] != tb["table"][k]]
    if disagree:
        untimed = "DIFFERENT"
    elif both == either and ta.get("complete") and tb.get("complete"):
        untimed = "SAME"                       # they agree, and there is nothing left to disagree about
    else:
        untimed = "INDETERMINATE"              # they agree ON EVERYTHING THE WORLD CAN SHOW -- and no further
    timed = ("SAME" if untimed == "SAME" and a["lags"] and
             sorted(map(tuple, a["lags"].values())) == sorted(map(tuple, b["lags"].values()))
             else ("DIFFERENT" if untimed in ("SAME", "DIFFERENT") else "INDETERMINATE"))
    return {"SOURCE_INTERFACE": "SAME", "UNTIMED_TRANSDUCER": untimed, "TIMED_TRANSDUCER": timed,
            "MICRO_ARCHITECTURE": micro,
            "coverage": (ta.get("coverage"), tb.get("coverage")),
            "why": ("agree on every reachable row; the rows that would separate them are UNREACHABLE"
                    if untimed == "INDETERMINATE" else "")}
