"""EXP-GT-HIER-R -- THE SINGLE PROSPECTIVE RUN of the repaired discovery architecture.

PREREGISTERED. The observer (`edlab/identity/modules.py`, `hier.py`, `admission.py`) is FROZEN and hashed in
docs/MODULE_DISCOVERY_SPEC.md. This split is generated AFTER that freeze and is run EXACTLY ONCE. If it fails,
the discovery architecture is RETIRED -- no second repair cycle, no threshold adjustment, no new template.

JOINTLY HELD OUT (all six at once, so no factor can be read off another):
  topology              channel columns never used in development
  layout                detour lengths (extra_delay) never used in development
  phase                 clk_phase != 0; development ran ENTIRELY at clk_phase = 0
  program               register contents unseen
  module implementation `and_or` and `xnor_and`, NEVER used or inspected during the repair
  intervention schedule follows the inferred period at the new phase, so every clamp lands at a new clock offset

Ground truth is computed from the WIRING (op/src) by a path independent of the observer's interventions -- the
two-independent-paths rule. Evaluator labels never enter the observer path.

NO COMPOSITE SCORE. Every metric is reported separately, including the ones that fail.
"""

from __future__ import annotations

import json

import numpy as np

from ..substrates.boolnet.circuits import build, H, W
from ..substrates.boolnet.evaluator import assert_qualified, gate_core
from ..identity.hier import World, discover
from ..identity.modules import discover_modules, candidate_cells, macro_quotient

AND, OR, XOR = (0, 0, 0, 1), (0, 1, 1, 1), (0, 1, 1, 0)
FN = {AND: "AND", OR: "OR", XOR: "XOR"}
TRUE_FN = {"direct": "AND", "direct_buf": "AND", "demorgan": "AND", "nand2": "AND", "xor_or": "AND",
           "and_or": "AND", "xnor_and": "AND", "or_gate": "OR", "xor_gate": "XOR"}
UNSEEN = ("and_or", "xnor_and")          # never used or inspected during the repair

# ---------------------------------------------------------------- THE PREREGISTERED SPLIT (frozen before running)
SPLIT = [
    # (arch_id, chan_cols, extra_delay, clk_phase, program, impl, decoy)
    # TOPOLOGIES ARE UNSEEN: development and the burned hold-outs used (6,20,34), (4,19,37) and (8,23,40); no
    # triple below reuses one. LAYOUT: the detour length varies per world. PHASE: every world runs at clk_phase
    # != 0 while development ran ENTIRELY at clk_phase = 0. The decoy-bearing worlds keep their channels clear of
    # columns 45-50, where the decoration sits -- otherwise the decoy would overwrite an output wire, which is the
    # exact defect the FIRST decoy had. The longest causal path must also fit inside SETTLE = 64, a frozen
    # substrate constant: `xnor_and` is the deepest gate in the library, so its detour is bounded accordingly.
    # All eight are checked by `assert_qualified` (evaluator only) BEFORE the observer is run even once.
    ("P1", (9, 25, 38), 2, 3, (1, 0, 1), "and_or", False),        # UNSEEN implementation
    ("P2", (7, 21, 36), 4, 5, (0, 1, 1), "xnor_and", False),      # UNSEEN implementation
    ("P3", (11, 26, 39), 1, 7, (1, 1, 0), "and_or", "cross"),     # UNSEEN + geometric-neighbour decoy
    ("P4", (10, 24, 35), 4, 1, (0, 0, 1), "xnor_and", "active"),  # UNSEEN + active inert decoration
    ("P5", (12, 27, 38), 3, 6, (1, 1, 1), "demorgan", False),     # seen impl, everything else new
    ("P6", (13, 29, 40), 2, 2, (0, 1, 0), "direct", False),       # seen impl, everything else new
    ("P7", (9, 22, 36), 4, 4, (1, 0, 0), "or_gate", False),       # a DIFFERENT function, everything else new
    ("P8", (14, 28, 42), 1, 5, (0, 0, 0), "xor_gate", False),     # different function, all-zero program
]


# ---------------------------------------------------------------- ground truth, from the WIRING (never from the observer)
def truth_of(m, i) -> dict:
    """Read the gate's boundary, parents, output, function and latency off op/src -- a path fully independent of
    the intervention-based observer. Disagreement between the two paths would reject the circuit, not the answer."""
    core = gate_core(m, i)
    src = m.net.src
    parents = sorted({(int(s) // W, int(s) % W) for c in core for s in src[c[0], c[1]] if s >= 0} - core)
    outs = sorted(c for c in core
                  if any((int(src[d[0], d[1], k]) // W, int(src[d[0], d[1], k]) % W) == c
                         for d in _all_cells(m) if d not in core
                         for k in range(3) if int(src[d[0], d[1], k]) >= 0))
    y = outs[0] if outs else None
    lat = None
    if y is not None:
        dist = {p: 0 for p in parents}
        frontier = list(parents)
        while frontier:
            nxt = []
            for u in frontier:
                for c in core:
                    if c in dist:
                        continue
                    if any((int(src[c[0], c[1], k]) // W, int(src[c[0], c[1], k]) % W) == u
                           for k in range(3) if int(src[c[0], c[1], k]) >= 0):
                        dist[c] = dist[u] + 1
                        nxt.append(c)
            frontier = nxt
        lat = dist.get(y)
    return {"core": core, "parents": parents, "out": y, "fn": TRUE_FN[m.impl], "latency": lat}


def _all_cells(m):
    if not hasattr(m, "_cellcache"):
        m._cellcache = [(r, c) for r in range(H) for c in range(W) if int(m.net.op[r, c]) != 0]
    return m._cellcache


# ---------------------------------------------------------------- the single run
RESULTS = "docs/EXP_GT_HIER_R_RAW.jsonl"


def run(only=None):
    """Each world is observed EXACTLY ONCE and its result APPENDED. Checkpointing per world does not weaken the
    single-run rule: the observer is frozen, the split is frozen, and no world is ever re-run."""
    rows, per_world = [], []
    for (aid, cols, ed, ph, prog, impl, dec) in SPLIT:
        if only and aid != only:
            continue
        m = build(program=prog, chan_cols=list(cols), impl=impl, extra_delay=ed,
                  decoy=dec, arch_id=aid, clk_phase=ph)
        assert_qualified(m)                                   # the world must WORK before it may be evidence

        w = World(m.net, m.out_cells)
        d = discover(m)                                       # BLIND: raw frames + interventions only
        cells = candidate_cells(w, d["contexts"])
        r = discover_modules(w, cells, d["contexts"], d["period"])

        for i in range(3):
            t = truth_of(m, i)
            got = next((mm for mm in r["modules"] if t["core"] & set(mm["cells"])), None)
            fn = FN.get(tuple(v for _, v in got["truth_table"])) if (got and got["truth_table"]) else None
            # conditional edge: is the channel->gate edge MASKED in the baseline, and did the observer still find it?
            chan_par = [p for p in t["parents"] if p not in m.components[f"reg{i}"]]
            found_chan = bool(got) and any(p in got["interface"]["parents"] for p in chan_par)
            ctxs = set()
            for p in chan_par:
                for c in t["core"]:
                    ctxs |= set(r["micro"]["cond"].get((p, c), set()))
            masked = bool(ctxs) and "base" not in ctxs
            # ground truth: for an AND the channel path is dead in the baseline when the bit is 0;
            # for an OR it is saturated away when the bit is 1.
            tf = t["fn"]
            expect_masked = (tf == "AND" and prog[i] == 0) or (tf == "OR" and prog[i] == 1)
            rows.append({
                "world": aid, "impl": impl, "unseen": impl in UNSEEN, "chan": i, "bit": prog[i],
                "found": got is not None,
                "boundary_exact": bool(got) and set(got["cells"]) == t["core"],
                "boundary_iou": (len(set(got["cells"]) & t["core"]) / len(set(got["cells"]) | t["core"]))
                                if got else 0.0,
                "parents_exact": bool(got) and set(got["interface"]["parents"]) == set(t["parents"]),
                "n_parents": got["n_parents"] if got else None,
                "out_exact": bool(got) and t["out"] in got["interface"]["out_cells"],
                "fn": fn, "fn_true": tf, "fn_correct": fn == tf,
                "delay": got["internal_delay"] if got else None, "delay_true": t["latency"],
                "delay_correct": bool(got) and got["internal_delay"] == t["latency"],
                "cond_found": found_chan, "cond_masked": masked, "cond_expect_masked": expect_masked,
                "cond_correct": found_chan and (masked == expect_masked),
                "verdict": got["verdict"] if got else "NOT_FOUND",
                "micro_cells": len(got["cells"]) if got else 0, "micro_true": len(t["core"]),
            })
        # the world's exact period, measured by the evaluator -- NOT `net.period * 3`, a formula I wrote from
        # memory of an older clock and which printed "true 24" against the observer's correct 8. That is the
        # D-053 error a third time: marking the observer wrong when it was right. Ground truth is computed, never
        # remembered.
        from ..substrates.boolnet.engine import period_of
        from ..substrates.boolnet.circuits import settled as _settled, SETTLE as _S
        per_world.append({"world": aid, "period": d["period"], "period_true": period_of(_settled(m), _S),
                          "n_modules": len(r["modules"]), "n_submodules": len(r["submodules"]),
                          "n_contexts": len(d["contexts"]), "interventions": w.n_interventions})
    return rows, per_world


def run_and_append(aid):
    rows, pw = run(only=aid)
    with open(RESULTS, "a") as f:
        f.write(json.dumps({"rows": rows, "per_world": pw}) + "\n")
    return rows, pw


def load_all():
    rows, pw = [], []
    for line in open(RESULTS):
        d = json.loads(line)
        rows += d["rows"]
        pw += d["per_world"]
    return rows, pw


def report(rows, per_world):
    def pct(sel, key):
        s = [r for r in sel if r[key] is not None]
        return (100.0 * sum(bool(r[key]) for r in s) / len(s)) if s else float("nan")

    groups = [("ALL", rows),
              ("UNSEEN implementations (and_or, xnor_and)", [r for r in rows if r["unseen"]]),
              ("seen implementations", [r for r in rows if not r["unseen"]])]
    print("EXP-GT-HIER-R -- SINGLE PROSPECTIVE RUN (frozen observer, fresh split, run once)")
    print("=" * 100)
    for name, sel in groups:
        if not sel:
            continue
        print(f"\n{name}   (n = {len(sel)} gates)")
        print(f"  gate recall (module found)          {pct(sel,'found'):6.1f} %")
        print(f"  boundary EXACT                      {pct(sel,'boundary_exact'):6.1f} %"
              f"   mean IoU {np.mean([r['boundary_iou'] for r in sel]):.3f}")
        print(f"  parent interface EXACT              {pct(sel,'parents_exact'):6.1f} %")
        print(f"  output interface EXACT              {pct(sel,'out_exact'):6.1f} %")
        print(f"  truth table / function correct      {pct(sel,'fn_correct'):6.1f} %")
        print(f"  internal delay correct              {pct(sel,'delay_correct'):6.1f} %")
        print(f"  conditional edge correct            {pct(sel,'cond_correct'):6.1f} %")
        print(f"  micro cell count exact              "
              f"{100.0*sum(r['micro_cells']==r['micro_true'] for r in sel)/len(sel):6.1f} %")
    print("\nABSTENTION / FALSE CERTAINTY")
    ind = [r for r in rows if r["verdict"] == "INDETERMINATE"]
    conf = [r for r in rows if r["verdict"] == "MODULE"]
    wrong_conf = [r for r in conf if not r["fn_correct"]]
    print(f"  confident answers                   {len(conf)}/{len(rows)}")
    print(f"  abstentions (INDETERMINATE)         {len(ind)}/{len(rows)}")
    print(f"  FALSE CERTAINTY (confident + wrong) {len(wrong_conf)}/{len(conf)}"
          f"   <-- must be 0")
    print("\nPER-WORLD")
    for p in per_world:
        print(f"  {p['world']}  period {p['period']} (true {p['period_true']})  modules {p['n_modules']}  "
              f"sub-modules {p['n_submodules']}  contexts {p['n_contexts']}  interventions {p['interventions']}")
    print("\nPER-GATE")
    for r in rows:
        flag = "" if (r["found"] and r["fn_correct"] and r["boundary_exact"]) else "   <<<"
        print(f"  {r['world']} ch{r['chan']} bit{r['bit']} {r['impl']:9s}"
              f"{' UNSEEN' if r['unseen'] else '       '} "
              f"cells {r['micro_cells']}/{r['micro_true']} fn {str(r['fn']):4s}/{r['fn_true']:3s} "
              f"lat {str(r['delay']):4s}/{str(r['delay_true']):4s} "
              f"par {'Y' if r['parents_exact'] else 'n'} cond {'Y' if r['cond_correct'] else 'n'} "
              f"{r['verdict']}{flag}")
    return {"rows": rows, "per_world": per_world}


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] != "report":
        rows, pw = run_and_append(sys.argv[1])
        print(f"{sys.argv[1]}: {len(rows)} gates recorded")
        return
    rows, per_world = load_all()
    out = report(rows, per_world)
    with open("docs/EXP_GT_HIER_R_RESULT.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    return out


if __name__ == "__main__":
    main()
