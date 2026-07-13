"""THE ACTIVE CAUSAL OBSERVER. It does not run a schedule. It asks questions.

    Do not ask every possible question. Ask the smallest number of legal questions that force the remaining causal
    explanations apart -- and know when the world does not permit them to be separated.

Three things are structurally different from every observer before it.

1. IT PLANS. It holds a VERSION SPACE of hypotheses, finds where they disagree, enumerates admissible interventions,
   PREDICTS what each would show under each hypothesis, and executes the one that would eliminate the most. An
   intervention whose outcome is identical under every surviving hypothesis is INADMISSIBLE -- it is not caution,
   it is waste. The plan is therefore a function of the world, and two worlds with different ambiguities receive
   different sequences. That is the falsifiable claim, and it is measured.

2. IT CANNOT FABRICATE A HISTORY. Every feature is a provenance-complete Row (see `provenance.py`), whose source
   samples are RE-READ from the exact episode and timestamp they claim, and compared. The window is computed from
   the longest inferred lag -- `required_window` -- and sampling begins at `max(margin, max_lag)`, not at a
   constant chosen in advance. D-067 died because a constant was chosen in advance.

3. IT MAY NOT ASSERT HIDDEN STATE TO ESCAPE ITS OWN IGNORANCE. `FINITE_STATE` requires that every row be
   provenance-valid, that the window cover every tested lag, and that no finite-history model explain the data. A
   contradiction produced by MISSING HISTORY yields `INSUFFICIENT_HISTORY` -- never `FINITE_STATE`. The retired
   observer called twelve combinational gates state machines because its own index had wrapped.
"""

from __future__ import annotations

import itertools

import numpy as np

from .hier import World
from .provenance import (run_episode, pulse_episode, extract, assert_rows_valid, required_window,
                         ProvenanceError, _idx)

MAX_SOURCES = 5
MAX_HISTORY = 6
SETTLE_MARGIN = 32
MAX_LAG = 80
MAX_EPISODES = 24            # a budget; exhausting it without resolution is INDETERMINATE, not a guess


# ====================================================================== structural phase (provenance-checked)
def micrograph(world: World, cells, period, contexts, world_id) -> dict:
    ctxs = [({}, "base")] + ([({c: 0 for c in contexts}, "ctx0"), ({c: 1 for c in contexts}, "ctx1")]
                            if contexts else [])
    T = period + 2
    children = {c: set() for c in cells}
    pol, cond = {}, {}
    n_int = 0
    for bg, name in ctxs:
        base = run_episode(world, world_id, f"mg-{name}", bg, T)
        for p in cells:
            for t in range(period):
                v = 1 - base.sample(p, t)
                try:
                    ep = pulse_episode(world, world_id, f"mg-{name}-{p}-{t}", p, v, t, T, bg=bg or None)
                except ProvenanceError:
                    continue
                n_int += 1
                for (r, c) in zip(*np.nonzero(ep.grid[t + 1] != base.grid[t + 1])):
                    q = (int(r), int(c))
                    if q == p or q not in children:
                        continue
                    children[p].add(q)
                    cond.setdefault((p, q), set()).add(name)
                    pol.setdefault((p, q), set()).add(1 if int(ep.grid[t + 1][r, c]) == v else 0)
    parents = {c: set() for c in cells}
    for p, ch in children.items():
        for q in ch:
            parents[q].add(p)
    return {"children": children, "parents": parents, "pol": pol, "cond": cond, "n_interventions": n_int}


def classify(mg, cells) -> dict:
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


def regions(mg, kind, cells) -> list:
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


def ancestry(tap, mg, roots) -> dict:
    dist, pol_, frontier = {tap: 0}, {tap: 1}, [tap]
    rootset, hit = set(roots), {}
    while frontier:
        nxt = []
        for u in frontier:
            if u in rootset:
                hit.setdefault(u, {"lag": dist[u], "pol": pol_[u]})
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


# ====================================================================== ACTIVE source independence
def dissociate(world: World, a, b, mg, roots, period, world_id, trace) -> dict:
    """SEEK a dissociating intervention; do not merely tabulate a baseline. Identical time series are not proof of
    common source, and different time series are not proof of independence. Only a dissociation is proof."""
    if a == b:
        return {"verdict": "SAME_SOURCE_DIFFERENT_TAPS", "why": "one cell"}
    ra, rb = set(ancestry(a, mg, roots)), set(ancestry(b, mg, roots))
    if not ra or not rb:
        return {"verdict": "UNRESOLVED", "why": "ancestry reaches no root"}
    if ra == rb and len(ra) == 1:
        return {"verdict": "SAME_SOURCE_DIFFERENT_TAPS", "why": f"both trace to the single root {sorted(ra)[0]}"}
    if ra & rb:
        return {"verdict": "COMMON_CAUSE", "why": f"ancestries share {sorted(ra & rb)}"}
    # ACTIVELY look for the two dissociations. We stop at the FIRST that works: further pulses would be waste.
    T = period + 2
    base = run_episode(world, world_id, f"di-base-{a}-{b}", {}, T)
    moved = {}
    for (x, y) in ((a, b), (b, a)):
        for t in range(period):
            v = 1 - base.sample(x, t)
            try:
                ep = pulse_episode(world, world_id, f"di-{x}-{t}", x, v, t, T)
            except ProvenanceError:
                continue
            trace.append({"purpose": f"dissociate {x} from {y}", "kind": "pulse", "cell": list(x),
                          "value": v, "at": t})
            x_moved = not np.array_equal(ep.grid[:, x[0], x[1]], base.grid[:, x[0], x[1]])
            y_intact = np.array_equal(ep.grid[:, y[0], y[1]], base.grid[:, y[0], y[1]])
            if x_moved and y_intact:
                moved[(x, y)] = True
                break                                    # ASKED AND ANSWERED. Do not keep asking.
    if moved.get((a, b)) and moved.get((b, a)):
        return {"verdict": "INDEPENDENT", "why": "each was moved while the other's history was preserved"}
    if moved:
        return {"verdict": "DETERMINISTIC_TRANSFORM", "why": "only one of the two could be moved alone"}
    return {"verdict": "OBSERVATIONALLY_EQUIVALENT",
            "why": "no admissible intervention separated them: they may be one process or two that this "
                   "repertoire cannot tell apart"}


# ====================================================================== lags, with a window that fits
def source_lags(world: World, s, out_cell, period, contexts, world_id, const_series) -> dict:
    T = required_window(MAX_LAG, period, SETTLE_MARGIN)
    bgs = [({}, "base")] + [({c: v for c in contexts}, f"ctx{v}") for v in (0, 1)]
    lags, firsts, persistent = set(), [], False
    for bg, nm in bgs:
        base = run_episode(world, world_id, f"lag-{nm}", bg, T)
        for t in range(period):
            v = 1 - base.sample(s, t)
            try:
                ep = pulse_episode(world, world_id, f"lag-{nm}-{s}-{t}", s, v, t, T, bg=bg or None)
            except ProvenanceError:
                continue
            devs = [k - t for k in range(t + 1, min(t + MAX_LAG + 1, T))
                    if ep.sample(out_cell, k) != base.sample(out_cell, k)]
            if not devs:
                continue
            firsts.append(min(devs))
            if len(devs) > 2 * MAX_HISTORY:
                persistent = True
            else:
                lags |= set(devs)
    if persistent or const_series:
        return {"lags": [min(firsts)] if firsts else [], "persistent": True}
    return {"lags": sorted(l for l in lags if 1 <= l <= MAX_LAG), "persistent": False}


# ====================================================================== ACTIVE manifold + transducer
def predict_rows(src_series: dict, regime: dict, feats, t_lo, T) -> set:
    """WHAT WOULD THIS EXPERIMENT SHOW? Computable EXACTLY and without running it, because the sources are ROOTS:
    under a regime, a clamped source is a constant and a free source is the series we already hold. This is what
    makes the planning genuine rather than decorative -- the observer knows the QUESTION each experiment asks
    before it pays for the answer."""
    out = set()
    for t in range(t_lo, T):
        key = []
        ok = True
        for (s, d) in feats:
            i = t - d
            if i < 0:
                ok = False
                break
            key.append(regime[s] if s in regime else int(src_series[s][i]))
        if ok:
            out.add(tuple(key))
    return out


def identify(world: World, sources, lagmap, out_cell, contexts, period, world_id, trace) -> dict:
    if len(sources) > MAX_SOURCES:
        return {"verdict": "OUT_OF_SCOPE", "why": f"{len(sources)} sources: the joint assignment is not enumerable"}

    # THE WINDOW MUST FIT EVERY LAG THE OBSERVER WILL TEST -- not merely the ones it first measured. The version
    # space widens each varying source's window up to MAX_HISTORY, so the widest hypothesis reaches max_lag +
    # MAX_HISTORY. Sizing the window from the measured lags alone left the widest hypotheses reading before the
    # start of their own episodes; they excluded rows, the exclusions pooled, and a long channel looked as though
    # it were starved of history when in fact I had simply not asked for enough of it.
    max_lag = max((max(lagmap[s]["lags"]) for s in sources if lagmap[s]["lags"]), default=1)
    max_lag_tested = max_lag + MAX_HISTORY
    T = required_window(max_lag_tested, period, SETTLE_MARGIN)
    t_lo = max(SETTLE_MARGIN, max_lag_tested)
    if t_lo >= T - period:
        return {"verdict": "INSUFFICIENT_HISTORY",
                "why": f"a lag of {max_lag} leaves no usable window inside T={T}"}

    const = [s for s in sources if lagmap[s]["persistent"] or lagmap[s]["const_series"]]
    vary = [s for s in sources if s not in const]

    # the source series we already hold, from the FREE episode -- the planner's model of the world's own drive
    free = run_episode(world, world_id, "free", {}, T)
    src_series = {s: free.grid[:, s[0], s[1]] for s in sources}

    # THE CANDIDATE QUESTIONS. Sustained regimes only: a one-step glitch is not an operating regime.
    candidates = []
    for assign in itertools.product((0, 1), repeat=len(const)):
        for vmode in ("free", 0, 1):
            reg = dict(zip(const, assign))
            if vmode != "free":
                for s in vary:
                    reg[s] = vmode
            candidates.append(reg)

    # THE VERSION SPACE: one hypothesis per lag-window. h = 0 is the measured lags; h > 0 widens each varying
    # source's window. A hypothesis is VIABLE while no source-history row it defines has produced two outputs.
    def feats_of(h):
        f = []
        for s in sources:
            L = lagmap[s]["lags"]
            if not L:
                continue
            if h == 0 or lagmap[s]["persistent"]:
                f += [(s, d) for d in L]
            else:
                d0 = min(L)
                f += [(s, d) for d in range(d0, d0 + h + 1)]
        return f

    hyps = {h: {"feats": feats_of(h), "table": {}, "viable": True} for h in range(MAX_HISTORY + 1)}
    episodes, executed = {}, []
    excluded = {h: 0 for h in hyps}                  # PER HYPOTHESIS. Pooling them blames the winner for the
    n_validated = 0                                  # starvation of models it never had to defend.

    def ingest(ep, h):
        ex = extract(ep, hyps[h]["feats"], out_cell, t_lo, T)
        excluded[h] += ex["n_excluded"]
        assert_rows_valid(ex["rows"], episodes)          # THE PAIR IS VERIFIED, NOT THE OUTPUT ALONE
        for r in ex["rows"]:
            prev = hyps[h]["table"].get(r.key)
            if prev is None:
                hyps[h]["table"][r.key] = r.out_value
            elif prev != r.out_value:
                hyps[h]["viable"] = False
                return False
        return True

    # ------------------------------------------------------------------ THE ACTIVE LOOP
    # The version space is refined LAZILY. Only the SIMPLEST viable hypothesis is worth spending an experiment on;
    # a wider history model matters only once the simpler one has been FALSIFIED. Scoring every hypothesis at once
    # made every question look informative and the observer bought all of them -- which is a schedule wearing the
    # costume of a plan.
    while len(executed) < MAX_EPISODES:
        live = [h for h in sorted(hyps) if hyps[h]["viable"]]
        if not live:
            break
        h0 = live[0]
        # EXPLORE: the question that would show the most rows this hypothesis has never seen.
        best, best_gain = None, 0
        for reg in candidates:
            if reg in executed:
                continue
            g = len(predict_rows(src_series, reg, hyps[h0]["feats"], t_lo, T) - set(hyps[h0]["table"]))
            if g > best_gain:
                best, best_gain = reg, g
        if best is not None:
            eid = f"explore{len(executed)}"
            ep = run_episode(world, world_id, eid, best, T)
            episodes[eid] = ep
            executed.append(dict(best))
            trace.append({"purpose": "explore the manifold", "kind": "sustained", "episode": eid,
                          "clamp": {str(k): v for k, v in best.items()},
                          "predicted_new_rows": best_gain, "hypothesis": f"h={h0}"})
            for h in [x for x in sorted(hyps) if hyps[x]["viable"]]:
                ingest(episodes[eid], h)
            continue

        # NOTHING LEFT TO EXPLORE. Every remaining question has an answer this hypothesis already claims to know.
        # That does not make them worthless -- it makes them a TEST. A model that has never predicted a regime it
        # has not seen has not been tested, only fitted.
        unseen = [reg for reg in candidates if reg not in executed]
        if not unseen:
            break
        reg = unseen[0]
        eid = f"validate{len(executed)}"
        pred_keys = predict_rows(src_series, reg, hyps[h0]["feats"], t_lo, T)
        ep = run_episode(world, world_id, eid, reg, T)
        episodes[eid] = ep
        executed.append(dict(reg))
        ex = extract(ep, hyps[h0]["feats"], out_cell, t_lo, T)
        excluded[h0] += ex["n_excluded"]
        assert_rows_valid(ex["rows"], episodes)
        wrong = [r for r in ex["rows"] if hyps[h0]["table"].get(r.key, r.out_value) != r.out_value]
        trace.append({"purpose": "VALIDATE by prediction on an unseen regime", "kind": "sustained", "episode": eid,
                      "clamp": {str(k): v for k, v in reg.items()},
                      "predicted_rows": len(pred_keys), "mispredicted": len(wrong), "hypothesis": f"h={h0}"})
        if wrong:
            hyps[h0]["viable"] = False                   # FALSIFIED on a regime it had never seen
            for h in [x for x in sorted(hyps) if hyps[x]["viable"]]:
                for e in episodes.values():
                    ingest(e, h)
            continue
        n_validated += 1
        break                                            # identified AND tested. Asking more would be waste.

    live = [h for h in sorted(hyps) if hyps[h]["viable"]]
    n_int = len(executed)

    if not live:
        # NO finite-history model works. Before claiming hidden state, prove it is not MY ignorance.
        starved = sum(excluded.values())
        if starved > 0:
            return {"verdict": "INSUFFICIENT_HISTORY", "n_interventions": n_int,
                    "why": f"{starved} rows lacked history inside their episode; a contradiction produced by "
                           f"missing history is not evidence of state"}
        return {"verdict": "IDENTIFIED", "class": "FINITE_STATE", "n_interventions": n_int,
                "feats": hyps[0]["feats"], "executed": executed,
                "why": f"every row was provenance-valid, the window covered every tested lag, and no history "
                       f"window up to {MAX_HISTORY} explains the output. The module remembers something the "
                       f"sources do not say."}

    h = live[0]
    feats, table = hyps[h]["feats"], hyps[h]["table"]
    n_poss = 1 << len(feats)
    cov = len(table) / n_poss
    lags = {s: sorted({d for (ss, d) in feats if ss == s}) for s in sources}
    multi = any(len(v) > 1 for v in lags.values())
    single = {s: v[0] for s, v in lags.items() if v}
    cls = (f"FINITE_HISTORY({h})" if (multi or h > 0) else
           ("STATIC" if len(set(single.values())) <= 1 else "DELAYED_STATIC"))
    verdict = "IDENTIFIED" if cov == 1.0 else "EQUIVALENCE_CLASS_ONLY"
    return {"verdict": verdict, "class": cls, "feats": feats, "table": table,
            "coverage": cov, "n_observed": len(table), "n_possible": n_poss,
            "complete": cov == 1.0, "lags": lags, "n_interventions": n_int,
            "executed": executed, "n_excluded": excluded[h],
            "n_candidates": len(candidates), "n_validated": n_validated,
            "why": ("" if cov == 1.0 else
                    "the rows that remain unobserved cannot be generated by any admissible sustained regime; "
                    "several functions agree on everything the world can show")}


# ====================================================================== the observer
def observe(world: World, cells, contexts, period, world_id="W") -> dict:
    trace = []
    mg = micrograph(world, cells, period, contexts, world_id)
    kind = classify(mg, cells)
    roots = sorted(c for c in cells if not mg["parents"][c])
    T0 = period + 2
    out = []
    for M in regions(mg, kind, cells):
        taps = sorted({p for y in M for p in mg["parents"][y] if p not in M})
        outs = sorted({y for y in M if any(c not in M for c in mg["children"][y])})
        if not taps or not outs:
            continue
        y = outs[0]
        tap_pairs = {(a, b): dissociate(world, a, b, mg, roots, period, world_id, trace)
                     for a, b in itertools.combinations(taps, 2)}
        eq = {}
        for t in taps:
            for r, info in ancestry(t, mg, roots).items():
                eq.setdefault(r, []).append({"tap": t, "lag": info["lag"], "pol": info["pol"]})
        srcs = sorted(eq)
        if not srcs:
            out.append({"cells": sorted(M), "verdict": "INDETERMINATE", "why": "no root reached"})
            continue
        lagmap = {}
        base = run_episode(world, world_id, "base-const", {}, T0)
        for s in srcs:
            ser = base.grid[:, s[0], s[1]]
            const = bool(ser.min() == ser.max())
            L = source_lags(world, s, y, period, contexts, world_id, const)
            L["const_series"] = const
            lagmap[s] = L
        srcs = [s for s in srcs if lagmap[s]["lags"]]
        if not srcs:
            out.append({"cells": sorted(M), "verdict": "INDETERMINATE",
                        "why": "no source reaches the output at any measurable lag"})
            continue
        pairs = {(a, b): dissociate(world, a, b, mg, roots, period, world_id, trace)
                 for a, b in itertools.combinations(srcs, 2)}
        if any(v["verdict"] == "OBSERVATIONALLY_EQUIVALENT" for v in pairs.values()):
            out.append({"cells": sorted(M), "sources": srcs, "verdict": "CONFOUNDED",
                        "why": "two sources could not be dissociated by any admissible intervention",
                        "independence": pairs, "tap_pairs": tap_pairs})
            continue
        tr = identify(world, srcs, lagmap, y, contexts, period, world_id, trace)
        out.append({"cells": sorted(M), "out_cell": y, "taps": taps, "n_taps": len(taps),
                    "sources": srcs, "n_sources": len(srcs), "tap_classes": eq,
                    "independence": pairs, "tap_pairs": tap_pairs,
                    "transducer": tr, "verdict": tr["verdict"]})
    return {"micro": mg, "kind": kind, "roots": roots, "transducers": out, "trace": trace,
            "n_structural_interventions": mg["n_interventions"]}
