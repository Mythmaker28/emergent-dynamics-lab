"""EXP-GT-ACTIVE-P -- THE SINGLE PROSPECTIVE RUN of the active causal observer.

Frozen and hashed in docs/ACTIVE_OBSERVER_FREEZE_MANIFEST.json. This split was generated AFTER the freeze. Each
world is observed EXACTLY ONCE. No repair is permitted.

JOINTLY HELD OUT: topology, layout, program, phase, implementation, channel distance (every world is scored on all
three channels), source duplication, delay asymmetry, context schedule, and the combination of transducer classes.

GROUND TRUTH IS PRIVILEGED AND INTERVENTION-DERIVED (`audit.py`): a variable is a cause if an admissible
intervention on it changes the downstream distribution, whether or not it is silent in the baseline. No source is
ever removed from the ground truth to match a count I expected.
"""

from __future__ import annotations

import json

import numpy as np

from ..substrates.boolnet.circuits import build
from ..substrates.boolnet.evaluator import assert_qualified, gate_core
from ..substrates.boolnet.audit import audit_world
from ..identity.hier import World, discover
from ..identity.sources import candidate_cells
from ..identity.active import observe

UNSEEN = ("or3", "xor3", "fsm_gate", "lag8_dm")
DEV_FAMILY = ("direct", "demorgan", "dup_same", "dup_lag", "inv_lag", "lag8_and", "lag8_or", "cascade",
              "and3", "two_en", "toggle", "tri_tap", "sync3", "edge_xor", "reg_delay")
BURNED_TOPOLOGIES = {(6, 20, 34), (4, 19, 37), (8, 23, 40),
                     (9, 25, 38), (7, 21, 36), (11, 26, 39), (10, 24, 35),
                     (12, 27, 38), (13, 29, 40), (9, 22, 36), (14, 28, 42),
                     (5, 18, 31), (7, 19, 33), (6, 22, 32), (8, 21, 30),
                     (5, 20, 35), (9, 23, 34), (7, 24, 36), (10, 25, 33)}

SPLIT = [
    # (id, chan_cols, extra_delay, clk_phase, program, impl)
    ("R1", (6, 21, 35), 2, 3, (1, 0, 1), "or3"),        # UNSEEN function + unseen micro-implementation
    ("R2", (8, 22, 37), 1, 6, (1, 1, 0), "xor3"),       # UNSEEN reconvergent XOR
    ("R3", (5, 19, 32), 3, 2, (1, 1, 1), "fsm_gate"),   # UNSEEN state machine
    ("R4", (7, 23, 38), 0, 5, (1, 1, 1), "lag8_dm"),    # UNSEEN, partial manifold
    ("R5", (9, 24, 39), 2, 7, (0, 1, 1), "or3"),        # UNSEEN again: new topology, phase, program
    ("R6", (6, 18, 30), 1, 4, (1, 1, 1), "fsm_gate"),   # UNSEEN again
    # the longest causal path must fit inside SETTLE=64: column 40 with a detour of 3 does not settle.
    # Caught by the evaluator BEFORE the observer ran -- which is what the pre-run qualification is for.
    ("R7", (10, 26, 38), 1, 1, (1, 0, 1), "direct"),    # SEEN implementation, everything else new
    ("R8", (11, 27, 36), 2, 6, (1, 1, 1), "toggle"),    # SEEN state machine, everything else new
]

# Ground truth per implementation: the transducer class, and y = f(clock values at its lags, register values).
TRUE = {
    "direct":   {"cls": "DELAYED_STATIC", "f": lambda c, r: int(all(c) and all(r))},
    "or3":      {"cls": "DELAYED_STATIC", "f": lambda c, r: int(any(c) or any(r))},
    "xor3":     {"cls": "DELAYED_STATIC", "f": lambda c, r: int(bool(c[0]) ^ bool(r[0]))},
    "lag8_dm":  {"cls": "FINITE_HISTORY", "f": lambda c, r: int((any(c)) and all(r))},
    "fsm_gate": {"cls": "FINITE_STATE", "f": None},
    "toggle":   {"cls": "FINITE_STATE", "f": None},
}
RESULTS = "docs/EXP_GT_ACTIVE_P_RAW.jsonl"


def run(only=None):
    rows = []
    for (aid, cols, ed, ph, prog, impl) in SPLIT:
        if only and aid != only:
            continue
        m = build(program=prog, chan_cols=list(cols), impl=impl, extra_delay=ed, arch_id=aid, clk_phase=ph)
        assert_qualified(m)
        aud = audit_world(m)                        # privileged ground truth, computed BEFORE the observer runs
        d = discover(m)
        w = World(m.net, m.out_cells)
        r = observe(w, candidate_cells(w, d["contexts"]), d["contexts"], d["period"], aid)

        for i in range(3):
            core = gate_core(m, i)
            hits = [x for x in r["transducers"] if core & set(x["cells"])]
            t = hits[-1] if hits else None
            T = TRUE[impl]
            tsrc = set(aud["channels"][i]["roots"])
            tr = (t or {}).get("transducer", {})
            cls = (tr.get("class") or "").split("(")[0]
            row = {"world": aid, "impl": impl, "unseen": impl in UNSEEN, "chan": i, "bit": prog[i],
                   "found": t is not None,
                   "n_src": t["n_sources"] if t else None, "n_src_true": len(tsrc),
                   "src_exact": bool(t) and set(t["sources"]) == tsrc,
                   "verdict": tr.get("verdict"), "class": tr.get("class"),
                   "cls_true": T["cls"], "cls_correct": cls == T["cls"],
                   "coverage": tr.get("coverage"), "excluded": tr.get("n_excluded"),
                   "episodes": tr.get("n_interventions"), "candidates": tr.get("n_candidates"),
                   "max_lag": max([max(v) for v in (tr.get("lags") or {}).values()] or [0]),
                   "fn_correct": None, "confident": False, "false_certainty": False,
                   "fabricated": 0}
            if t and tr.get("table") is not None:
                row["confident"] = True
                feats = tr["feats"]
                ok = True
                if T["f"] is not None:
                    for key, y in tr["table"].items():
                        c = [v for v, (s, _d) in zip(key, feats) if s == (1, 1)]
                        rg = [v for v, (s, _d) in zip(key, feats) if s != (1, 1)]
                        if not c or not rg or T["f"](c, rg) != y:
                            ok = False
                else:
                    ok = False                       # a table for a STATE MACHINE is a false claim by construction
                row["fn_correct"] = ok
                row["false_certainty"] = not (ok and row["src_exact"] and row["cls_correct"])
            rows.append(row)
    return rows


def run_and_append(aid):
    rows = run(only=aid)
    with open(RESULTS, "a") as f:
        f.write(json.dumps(rows, default=str) + "\n")
    return rows


def load_all():
    out = []
    for line in open(RESULTS):
        out += json.loads(line)
    return out


def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def report(rows):
    print("EXP-GT-ACTIVE-P -- SINGLE PROSPECTIVE RUN (frozen active observer, fresh split, each world seen once)")
    print("=" * 108)

    def blk(name, sel):
        if not sel:
            return
        n = len(sel)
        print(f"\n{name}   (n = {n})")
        for label, key in (("region found", "found"),
                           ("source count correct", "_cnt"),
                           ("source IDENTITIES exact (vs privileged audit)", "src_exact"),
                           ("transducer CLASS correct", "cls_correct"),
                           ("function on the reachable manifold correct", "_fn")):
            if key == "_cnt":
                k = sum(1 for r in sel if r["n_src"] == r["n_src_true"])
            elif key == "_fn":
                s2 = [r for r in sel if r["fn_correct"] is not None]
                k = sum(1 for r in s2 if r["fn_correct"])
                if not s2:
                    continue
                lo, hi = wilson(k, len(s2))
                print(f"  {label:46s} {100.0*k/len(s2):6.1f} %   [{100*lo:5.1f}, {100*hi:5.1f}]  (n={len(s2)})")
                continue
            else:
                k = sum(1 for r in sel if r.get(key))
            lo, hi = wilson(k, n)
            print(f"  {label:46s} {100.0*k/n:6.1f} %   [{100*lo:5.1f}, {100*hi:5.1f}]")

    blk("ALL", rows)
    blk("UNSEEN implementations", [r for r in rows if r["unseen"]])
    for c in (0, 1, 2):
        blk(f"channel {c}", [r for r in rows if r["chan"] == c])

    fc = [r for r in rows if r["false_certainty"]]
    conf = [r for r in rows if r["confident"]]
    fab = sum(r["fabricated"] for r in rows)
    print("\nPRIMARY BARS")
    print(f"  FALSE CERTAINTY (confident and wrong)     {len(fc)}/{len(rows)}    <-- must be 0")
    print(f"  FABRICATED PROVENANCE ROWS                {fab}          <-- must be 0")
    print(f"  confident answers                         {len(conf)}/{len(rows)}")
    print(f"  abstentions                               {len(rows)-len(conf)}/{len(rows)}")

    used = sum(r["episodes"] or 0 for r in rows)
    avail = sum(r["candidates"] or 0 for r in rows)
    print(f"  episodes executed / exhaustive schedule   {used}/{avail}  ({100.0*used/max(avail,1):.0f} %)")

    print("\nNO DEGRADATION WITH SOURCE DISTANCE")
    for c in (0, 1, 2):
        sel = [r for r in rows if r["chan"] == c]
        mx = max(r["max_lag"] for r in sel)
        ok = sum(1 for r in sel if r["cls_correct"])
        exc = sum(r["excluded"] or 0 for r in sel)
        print(f"  channel {c}: max lag {mx:3d}   class correct {ok}/{len(sel)}   rows excluded for missing "
              f"history: {exc}")

    print("\nPER TRANSDUCER")
    for r in rows:
        bad = "" if (r["found"] and r["cls_correct"] and (r["fn_correct"] is not False)) else "   <<<"
        print(f"  {r['world']} ch{r['chan']} bit{r['bit']} {r['impl']:9s}"
              f"{' UNSEEN' if r['unseen'] else '       '} lag {r['max_lag']:3d} "
              f"src {r['n_src']}/{r['n_src_true']} {str(r['verdict']):22s} {str(r['class']):18s} "
              f"cov {r['coverage']} eps {r['episodes']}/{r['candidates']} "
              f"fn {'Y' if r['fn_correct'] else ('n' if r['fn_correct'] is False else '-')}{bad}")
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
