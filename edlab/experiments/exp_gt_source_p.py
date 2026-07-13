"""EXP-GT-SOURCE-P -- THE SINGLE PROSPECTIVE RUN of the source-transducer observer.

The observer is FROZEN and hashed in docs/SOURCE_TRANSDUCER_FREEZE_MANIFEST.json. This split was generated AFTER
that freeze. Each world is observed EXACTLY ONCE. If it fails, the design is RETIRED -- preserved, not patched --
and the failure is classified as source discovery / manifold identification / transducer inference / scope
calibration.

JOINTLY HELD OUT, all at once:
    topology                 channel triples used in no development world and in no burned split
    layout                   detour length
    phase                    clk_phase; development ran ENTIRELY at clk_phase = 0
    program                  register contents
    implementation           tri_tap, sync3, edge_xor, reg_delay -- never used or inspected during development
    delay asymmetry          tri_tap (3 lags), edge_xor (2 lags), reg_delay (a register in the delay path)
    source-duplication       tri_tap (3 taps of one source), sync3 (2 taps of one source)
    context schedule         the contexts are DISCOVERED, at a phase the observer has never run at
    intervention schedule    every clamp and pulse lands at a new clock offset

GROUND TRUTH IS COMPUTED FROM THE WIRING, by a path that never touches the observer -- and then CHECKED against a
second, independent path (a direct simulation with the true sources clamped). Two paths, or it is not ground truth.
"""

from __future__ import annotations

import json
import itertools

import numpy as np

from ..substrates.boolnet.circuits import build, settled, SETTLE, H, W
from ..substrates.boolnet.engine import step
from ..substrates.boolnet.evaluator import assert_qualified, gate_core
from ..identity.hier import World, discover, OBS
from ..identity.sources import discover_transducers, quotient, candidate_cells

UNSEEN = ("tri_tap", "sync3", "edge_xor", "reg_delay")
DEV_FAMILY = ("direct", "direct_buf", "demorgan", "nand2", "xor_or", "or_gate", "xor_gate", "single_parent",
              "dup_same", "dup_lag", "inv_lag", "lag15_or", "lag15_xor", "lag8_and", "lag8_or", "cascade",
              "and3", "two_en", "toggle")
BURNED_TOPOLOGIES = {(6, 20, 34), (4, 19, 37), (8, 23, 40),                       # development + old hold-outs
                     (9, 25, 38), (7, 21, 36), (11, 26, 39), (10, 24, 35),        # the burned D-065 split
                     (12, 27, 38), (13, 29, 40), (9, 22, 36), (14, 28, 42)}

# ---------------------------------------------------------------- THE PREREGISTERED SPLIT
SPLIT = [
    # (id, chan_cols, extra_delay, clk_phase, program, impl)
    ("Q1", (5, 18, 31), 1, 2, (1, 0, 1), "tri_tap"),      # UNSEEN: 4 taps, 2 causes, three lags
    ("Q2", (7, 19, 33), 2, 5, (0, 1, 1), "sync3"),        # UNSEEN: 4 taps, 3 causes, two identical registers
    ("Q3", (6, 22, 32), 3, 7, (1, 1, 0), "edge_xor"),     # UNSEEN: history is required
    ("Q4", (8, 21, 30), 1, 3, (1, 1, 1), "reg_delay"),    # UNSEEN: internal state, static interface
    ("Q5", (5, 20, 35), 2, 6, (0, 0, 1), "tri_tap"),      # UNSEEN again, new topology/phase/program
    ("Q6", (9, 23, 34), 0, 4, (1, 0, 0), "reg_delay"),    # UNSEEN again
    ("Q7", (7, 24, 36), 3, 1, (0, 1, 0), "direct"),       # SEEN implementation: everything else new
    ("Q8", (10, 25, 33), 1, 6, (1, 1, 1), "demorgan"),    # SEEN implementation: everything else new
]

# The GROUND-TRUTH transducer of each implementation, declared from its construction:
#   y = f(clock values at its lags, register values)
TRUE = {
    "direct":    {"n_src": 2, "n_clk_lags": 1, "cls": "DELAYED_STATIC",
                  "f": lambda c, r: int(all(c) and all(r))},
    "demorgan":  {"n_src": 2, "n_clk_lags": 1, "cls": "DELAYED_STATIC",
                  "f": lambda c, r: int(all(c) and all(r))},
    "tri_tap":   {"n_src": 2, "n_clk_lags": 3, "cls": "FINITE_HISTORY",
                  "f": lambda c, r: int(all(c) and all(r))},
    "sync3":     {"n_src": 3, "n_clk_lags": 1, "cls": "DELAYED_STATIC",
                  "f": lambda c, r: int(all(c) and all(r))},
    "edge_xor":  {"n_src": 2, "n_clk_lags": 2, "cls": "FINITE_HISTORY",
                  "f": lambda c, r: int((c[0] ^ c[1]) and all(r))},
    "reg_delay": {"n_src": 2, "n_clk_lags": 1, "cls": "DELAYED_STATIC",
                  "f": lambda c, r: int(all(c) and all(r))},
}


# ---------------------------------------------------------------- ground truth path 1: the WIRING
def truth_sources(m, i) -> set:
    """Trace the gate core's external inputs back through op/src to cells with NO source. Never uses the observer."""
    core = gate_core(m, i)
    src = m.net.src
    seen, stack = set(), [c for c in core]
    roots = set()
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        ps = [(int(s) // W, int(s) % W) for s in src[u[0], u[1]] if s >= 0]
        # A self-loop is not a parent, and neither is an INERT RAIL. Each register's declared `src` points at the
        # write-enable cell, which is an OFF cell: constant 0, forever, in every world. Counting it as a parent
        # makes the register a non-root and the ground truth then reports ONE source where the machine has two.
        # A wire that never changes is not a cause; it is a boundary condition.
        ps = [p for p in ps if p != u and int(m.net.op[p]) != 0]
        if not ps and int(m.net.op[u]) != 0:
            roots.add(u)
        stack += [p for p in ps if p not in seen]
    return roots


# ---------------------------------------------------------------- ground truth path 2: DIRECT SIMULATION
def truth_table_by_simulation(m, i, srcs, lags, out_cell) -> dict:
    """Clamp the TRUE sources in a direct simulation and read the gate's output. Independent of the observer's
    code path, and of the observer's manifold. Disagreement rejects the ground truth, not the answer."""
    consts = [s for s in srcs if s != (1, 1)]
    tab = {}
    for assign in itertools.product((0, 1), repeat=len(consts)):
        for vmode in ("free", 0, 1):
            cl = dict(zip(consts, assign))
            if vmode != "free":
                cl[(1, 1)] = vmode
            cur = settled(m)
            grids = []
            for k in range(OBS):
                cur = step(cur, SETTLE + k, cl)
                grids.append(cur.state.copy())
            g = np.stack(grids)
            for t in range(32, OBS):
                key = tuple(int(g[t - d][s[0], s[1]]) for (s, d) in lags)
                tab.setdefault(key, set()).add(int(g[t][out_cell[0], out_cell[1]]))
    return {k: next(iter(v)) for k, v in tab.items() if len(v) == 1}


def run(only=None):
    rows = []
    for (aid, cols, ed, ph, prog, impl) in SPLIT:
        if only and aid != only:
            continue
        m = build(program=prog, chan_cols=list(cols), impl=impl, extra_delay=ed, arch_id=aid, clk_phase=ph)
        assert_qualified(m)                                  # the world must WORK before it may be evidence
        w = World(m.net, m.out_cells)
        d = discover(m)
        r = discover_transducers(w, candidate_cells(w, d["contexts"]), d["contexts"], d["period"])

        for i in range(3):
            core = gate_core(m, i)
            hits = [x for x in r["transducers"] if core & set(x["cells"])]
            got = hits[-1] if hits else None
            T = TRUE[impl]
            tsrc = truth_sources(m, i)
            row = {"world": aid, "impl": impl, "unseen": impl in UNSEEN, "chan": i, "bit": prog[i],
                   "found": got is not None,
                   "n_src_true": len(tsrc), "n_src": got["n_sources"] if got else None,
                   "src_exact": bool(got) and set(got["sources"]) == tsrc,
                   "cls_true": T["cls"], "cls": None, "cls_correct": False,
                   "coverage": None, "complete_true": True, "complete": None, "manifold_correct": False,
                   "fn_correct": False, "verdict": got["verdict"] if got else "NOT_FOUND",
                   "confident": False, "false_certainty": False,
                   "n_taps": got["n_taps"] if got else None}
            if got:
                tr = got["transducer"]
                cls = tr["class"].split("(")[0]
                row["cls"] = tr["class"]
                row["cls_correct"] = (cls == T["cls"])
                row["coverage"] = tr.get("coverage")
                row["complete"] = tr.get("complete")
                row["manifold_correct"] = (tr.get("complete") is True)      # all six are fully coverable
                # the CLOCK's lag count -- the source-duplication pattern, recovered
                clk_lags = got["lags"].get((1, 1), [])
                row["n_clk_lags"] = len(clk_lags)
                row["lags_correct"] = (len(clk_lags) == T["n_clk_lags"])
                if "table" in tr:
                    row["confident"] = True
                    feats = tr["feats"]
                    ok = True
                    for key, y in tr["table"].items():
                        c = [v for v, (s, _dd) in zip(key, feats) if s == (1, 1)]
                        rg = [v for v, (s, _dd) in zip(key, feats) if s != (1, 1)]
                        if T["f"](c, rg) != y:
                            ok = False
                    row["fn_correct"] = ok and row["src_exact"] and row["cls_correct"]
                    # SECOND, INDEPENDENT PATH: the same table by direct simulation of the wiring.
                    sim = truth_table_by_simulation(m, i, tsrc, feats, got["out_cell"])
                    agree = all(sim.get(k) == v for k, v in tr["table"].items() if k in sim)
                    row["two_paths_agree"] = bool(agree)
                    row["false_certainty"] = not (row["fn_correct"] and row["src_exact"])
            rows.append(row)
    return rows


RESULTS = "docs/EXP_GT_SOURCE_P_RAW.jsonl"


def run_and_append(aid):
    rows = run(only=aid)
    with open(RESULTS, "a") as f:
        f.write(json.dumps(rows) + "\n")
    return rows


def load_all():
    out = []
    for line in open(RESULTS):
        out += json.loads(line)
    return out


def wilson(k, n):
    """A 95% interval, so a small sample is not read as a large certainty."""
    if n == 0:
        return (float("nan"), float("nan"))
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def report(rows):
    print("EXP-GT-SOURCE-P -- SINGLE PROSPECTIVE RUN (frozen observer, fresh split, each world seen once)")
    print("=" * 104)

    def blk(name, sel):
        if not sel:
            return
        n = len(sel)
        print(f"\n{name}   (n = {n} transducers)")
        for label, key in (("region found", "found"),
                           ("independent-source COUNT correct", None),
                           ("source IDENTITIES exact", "src_exact"),
                           ("source-duplication (lag count) correct", "lags_correct"),
                           ("transducer CLASS correct", "cls_correct"),
                           ("reachable-manifold classification correct", "manifold_correct"),
                           ("FUNCTION on the reachable manifold correct", "fn_correct"),
                           ("two independent paths agree", "two_paths_agree")):
            if key is None:
                k = sum(1 for r in sel if r["n_src"] == r["n_src_true"])
            else:
                k = sum(1 for r in sel if r.get(key))
            lo, hi = wilson(k, n)
            print(f"  {label:44s} {100.0*k/n:6.1f} %   [{100*lo:5.1f}, {100*hi:5.1f}]")

    blk("ALL", rows)
    blk("UNSEEN implementations", [r for r in rows if r["unseen"]])
    blk("seen implementations", [r for r in rows if not r["unseen"]])

    conf = [r for r in rows if r["confident"]]
    fc = [r for r in rows if r["false_certainty"]]
    ind = [r for r in rows if not r["confident"]]
    print("\nABSTENTION / FALSE CERTAINTY")
    print(f"  confident answers (a table was emitted)   {len(conf)}/{len(rows)}")
    print(f"  abstentions (no table)                    {len(ind)}/{len(rows)}")
    print(f"  FALSE CERTAINTY (confident and wrong)     {len(fc)}/{len(rows)}    <-- PRIMARY BAR: must be 0")

    print("\nPER TRANSDUCER")
    for r in rows:
        bad = "" if (r["found"] and r["fn_correct"] and r["src_exact"] and r["cls_correct"]) else "   <<<"
        print(f"  {r['world']} ch{r['chan']} bit{r['bit']} {r['impl']:10s}"
              f"{' UNSEEN' if r['unseen'] else '       '} "
              f"taps {r['n_taps']} src {r['n_src']}/{r['n_src_true']} "
              f"lags {r.get('n_clk_lags')} {str(r['cls']):18s} cov {r['coverage']} "
              f"fn {'Y' if r['fn_correct'] else 'n'} 2paths {'Y' if r.get('two_paths_agree') else 'n'}{bad}")
    return rows


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] != "report":
        rows = run_and_append(sys.argv[1])
        print(f"{sys.argv[1]}: {len(rows)} transducers recorded")
        return
    report(load_all())


if __name__ == "__main__":
    main()
