"""EXP-GT-SOURCE -- DEVELOPMENT CERTIFICATE for the source-transducer observer.

Development circuits ONLY. The burned `xnor_and` prospective worlds are DIAGNOSTIC_ONLY and are not consulted:
the failure that retired the previous design is reproduced here ABSTRACTLY, by circuits built from scratch
(`dup_same`, `cascade`), so that the fix is shown to address the CLASS of error and not the instance of it.

EVERY criterion must be shown able to FIRE, to FAIL, and to ABSTAIN. A detector that only ever says YES has not
been tested; one that only ever says "I don't know" has not been built.
"""

from __future__ import annotations

import numpy as np

from ..substrates.boolnet.circuits import build
from ..substrates.boolnet.evaluator import assert_qualified, gate_core
from ..identity.hier import World, discover
from ..identity.sources import (discover_transducers, quotient, classify_pair, ancestry,
                                candidate_cells, MAX_SOURCES, identify)

AND2 = {(0, 0): 0, (1, 0): 0, (0, 1): 0, (1, 1): 1}

# the development family. `and_or` / `xnor_and` (the burned prospective implementations) appear NOWHERE.
DEV = ("direct", "direct_buf", "demorgan", "nand2", "xor_or", "or_gate", "xor_gate", "single_parent",
       "dup_same", "dup_lag", "inv_lag", "lag15_or", "lag15_xor", "lag8_and", "lag8_or",
       "cascade", "and3", "two_en", "toggle")

_CACHE = {}
_DISK = ".cache_source"


def run_one(impl, program=(1, 1, 1), decoy=False):
    """Results are cached ON DISK. The observer is deterministic and blind, so re-running a development world is a
    re-computation, not a second look: nothing about the answer depends on how many calls it took to get it."""
    import os, pickle
    key = (impl, program, decoy)
    if key in _CACHE:
        return _CACHE[key]
    os.makedirs(_DISK, exist_ok=True)
    f = os.path.join(_DISK, f"{impl}_{''.join(map(str, program))}_{decoy}.pkl")
    if os.path.exists(f):
        with open(f, "rb") as fh:
            r = pickle.load(fh)
        _CACHE[key] = r
        return r
    m = build(program=program, impl=impl, decoy=decoy)
    assert_qualified(m)
    d = discover(m)
    w = World(m.net, m.out_cells)
    r = discover_transducers(w, candidate_cells(w, d["contexts"]), d["contexts"], d["period"])
    r["machine"], r["world"], r["disc"] = m, w, d
    with open(f, "wb") as fh:
        pickle.dump(r, fh)
    _CACHE[key] = r
    return r


def region_of(r, i=0, last=True):
    """the region containing the gate core; `last` picks the DOWNSTREAM one when a gate spans two regions."""
    core = gate_core(r["machine"], i)
    hits = [x for x in r["transducers"] if core & set(x["cells"])]
    return (hits[-1] if last else hits[0]) if hits else None


def tab(t):
    return t.get("transducer", {}).get("table")


def certificate() -> dict:
    cases = []

    def case(name, ok, detail=""):
        cases.append({"case": name, "PASS": bool(ok), "detail": detail})

    R = {i: run_one(i) for i in DEV}

    # ================================================================ SOURCES, NOT TAPS  (the reason for the redesign)
    # (8) A TWO-INPUT GATE WITH THREE BOUNDARY TAPS. One source arrives twice, through two equal-length buffers.
    #     The retired observer counted three independent inputs here and measured a table off the manifold.
    t = region_of(R["dup_same"])
    case("S1 three taps, TWO sources (the D-065 failure, abstractly)",
         t["n_taps"] == 3 and t["n_sources"] == 2 and tab(t) == AND2
         and t["transducer"]["coverage"] == 1.0,
         f"taps={t['n_taps']} sources={t['n_sources']} table={tab(t)} coverage={t['transducer']['coverage']}")

    # and the quotient it could not do: an unfamiliar three-tap implementation IS the one-cell AND.
    q = quotient(region_of(R["direct"]), t)
    case("S2 the 3-tap AND is the SAME macro transducer as the 1-cell AND",
         q["UNTIMED_TRANSDUCER"] == "SAME" and q["SOURCE_INTERFACE"] == "SAME"
         and q["TIMED_TRANSDUCER"] == "DIFFERENT" and q["MICRO_ARCHITECTURE"] == "DIFFERENT",
         f"iface={q['SOURCE_INTERFACE']} untimed={q['UNTIMED_TRANSDUCER']} "
         f"timed={q['TIMED_TRANSDUCER']} micro={q['MICRO_ARCHITECTURE']}")

    # (2) the two duplicate taps are classified as ONE source -- though pulsing either leaves the other untouched.
    tp = region_of(R["dup_same"])["tap_pairs"]
    same = [v for v in tp.values() if v["verdict"] == "SAME_SOURCE_DIFFERENT_TAP"]
    case("S3 SAME_SOURCE_DIFFERENT_TAP fires (two taps, one cause)",
         len(same) == 1, f"{len(same)} tap pair(s) traced to a single root")

    # (16) FOUR microscopically different machines, ONE macro transducer.
    fams = ("direct", "direct_buf", "demorgan", "nand2", "xor_or", "dup_same")
    q_all = {i: quotient(region_of(R["direct"]), region_of(R[i])) for i in fams[1:]}
    sizes = {i: len(region_of(R[i])["cells"]) for i in fams}
    case("S4 same macro transducer across microscopically distinct implementations",
         all(v["UNTIMED_TRANSDUCER"] == "SAME" for v in q_all.values())
         and all(tab(region_of(R[i])) == AND2 for i in fams) and len(set(sizes.values())) > 1,
         f"untimed={ {i: v['UNTIMED_TRANSDUCER'] for i, v in q_all.items()} } micro sizes={sizes}")

    # ================================================================ HISTORY
    # (3) one source entering at two lags -> the output depends on its PAST.
    t = region_of(R["dup_lag"])
    lags = t["lags"][sorted(t["lags"], key=lambda s: -len(t["lags"][s]))[0]]
    case("S5 one source, TWO lags: a finite-history transducer",
         t["n_sources"] == 2 and len(lags) == 2 and t["transducer"]["class"].startswith("FINITE_HISTORY")
         and t["transducer"]["coverage"] == 1.0,
         f"sources={t['n_sources']} clock lags={lags} class={t['transducer']['class']} "
         f"coverage={t['transducer']['coverage']}")

    # (4) direct and INVERTED-delayed taps of one source: still one source.
    t = region_of(R["inv_lag"])
    case("S6 direct + inverted-delayed taps are still ONE source",
         t["n_sources"] == 2 and any(len(v) == 2 for v in t["lags"].values()),
         f"sources={t['n_sources']} lags={list(t['lags'].values())}")

    # (9) IDENTICAL current inputs, DIFFERENT histories, DIFFERENT outputs. No static table may be emitted.
    t = region_of(R["toggle"])
    tr = t["transducer"]
    case("S7 stateful module -> FINITE_STATE, and NO truth table is invented",
         tr["class"] == "FINITE_STATE" and "table" not in tr and tr["ambiguous_rows"] > 0,
         f"class={tr['class']} ambiguous source-history rows={tr.get('ambiguous_rows')} table={tr.get('table')}")

    # ================================================================ INDEPENDENCE
    # (5)(7) two registers holding the SAME bit -- byte-identical baseline series -- are TWO sources.
    t = region_of(R["and3"])
    regs = [s for s in t["sources"] if t["lags"][s] and len(t["lags"][s]) == 1]
    w = R["and3"]["world"]
    ser = w.trace(None, hold=96, steps=96)[0]
    r0, r1 = (4, 8), (4, 9)
    identical = bool(np.array_equal(ser[:, r0[0], r0[1]], ser[:, r1[0], r1[1]]))
    verdicts = {v["verdict"] for v in t["independence"].values()}
    case("S8 three sources; two registers with IDENTICAL baseline series stay INDEPENDENT",
         t["n_sources"] == 3 and identical and verdicts == {"INDEPENDENT_SOURCES"}
         and t["transducer"]["coverage"] == 1.0,
         f"sources={t['n_sources']} the two registers' baseline series identical={identical} "
         f"verdicts={sorted(verdicts)}")

    # (6) two taps of the COMMON HIDDEN CLOCK, each independently manipulable downstream through its own enable.
    t = region_of(R["two_en"])
    case("S9 common hidden clock + two independent enables: 3 sources, clock at 2 lags",
         t["n_sources"] == 3 and any(len(v) == 2 for v in t["lags"].values())
         and all(v["verdict"] == "INDEPENDENT_SOURCES" for v in t["independence"].values()),
         f"taps={t['n_taps']} sources={t['n_sources']} lags={list(t['lags'].values())}")

    # DEPENDENT_COMMON_CAUSE must be able to fire: one tap is a FUNCTION of the other's cause and more.
    t = region_of(R["cascade"], last=True)
    dep = [v for v in t["tap_pairs"].values() if v["verdict"] == "DEPENDENT_COMMON_CAUSE"]
    case("S10 DEPENDENT_COMMON_CAUSE fires (a tap that is a function of another tap's source)",
         len(dep) == 1 and t["n_sources"] == 2 and tab(t) == AND2,
         f"{len(dep)} dependent tap pair; traced to {t['n_sources']} sources; table={tab(t)}")

    # UNRESOLVED must be able to fire: a world in which no admissible pulse separates two candidates.
    class _Deaf:
        """a world whose interventions never take. The honest answer there is 'I could not tell', not a guess."""
        def trace(self, *a, **k):
            n = k.get("steps", 10)
            return np.zeros((n, 24, 64), dtype=np.uint8), None
        def pulse_at(self, cell, v, t, steps, bg=None):
            return np.zeros((steps, 24, 64), dtype=np.uint8)      # the clamp never takes
    mg_fake = {"parents": {(0, 0): set(), (0, 1): set()}, "pol": {}}
    v = classify_pair(_Deaf(), (0, 0), (0, 1), mg_fake, [(0, 0), (0, 1)], 8)
    case("S11 UNRESOLVED fires when no intervention separates two candidates",
         v["verdict"] == "UNRESOLVED", f"verdict={v['verdict']} ({v['why']})")

    # ================================================================ THE REACHABLE MANIFOLD
    # (11)(12) two taps of one source separated by EXACTLY ONE CLOCK PERIOD. Under every sustained source regime
    #          they carry the SAME value: half the manifold cannot be produced. AND and OR agree on all of it.
    ta, to = region_of(R["lag8_and"]), region_of(R["lag8_or"])
    q = quotient(ta, to)
    case("S12 partial manifold reported honestly (coverage 0.5, not rounded up)",
         ta["transducer"]["coverage"] == 0.5 and to["transducer"]["coverage"] == 0.5
         and ta["transducer"]["n_observed"] == 4 and ta["transducer"]["n_possible"] == 8,
         f"observed {ta['transducer']['n_observed']}/{ta['transducer']['n_possible']} rows")
    case("S13 identical on the manifold, different off it -> INDETERMINATE, NOT 'SAME'",
         q["UNTIMED_TRANSDUCER"] == "INDETERMINATE" and q["TIMED_TRANSDUCER"] == "INDETERMINATE"
         and tab(ta) == tab(to),
         f"untimed={q['UNTIMED_TRANSDUCER']} tables identical={tab(ta) == tab(to)} why={q['why']}")

    # and the mirror image: where the world CAN show the difference, the observer must SEE it, not abstain.
    q2 = quotient(region_of(R["lag15_or"]), region_of(R["lag15_xor"]))
    case("S14 a difference the world CAN produce is found, not abstained from (no false abstention)",
         q2["UNTIMED_TRANSDUCER"] == "DIFFERENT"
         and region_of(R["lag15_or"])["transducer"]["coverage"] == 1.0,
         f"untimed={q2['UNTIMED_TRANSDUCER']} coverage={region_of(R['lag15_or'])['transducer']['coverage']} "
         f"(these two have BYTE-IDENTICAL free-running outputs; only clamping the source separates them)")

    # different functions are not quotiented away
    q3 = quotient(region_of(R["or_gate"]), region_of(R["xor_gate"]))
    case("S15 different functions stay DIFFERENT (or != xor)",
         q3["UNTIMED_TRANSDUCER"] == "DIFFERENT", f"untimed={q3['UNTIMED_TRANSDUCER']}")

    # ================================================================ NEGATIVES: it must be able to say NO
    # (1) a cascade whose output depends on ONE effective source: AND(x, x) is a wire wearing a hat.
    sp = R["single_parent"]
    core = gate_core(sp["machine"], 0)
    case("S16 coincident correlation rejected: AND(x,x) is no transducer",
         not any(core & set(x["cells"]) for x in sp["transducers"]),
         f"{len(sp['transducers'])} regions in the whole world; none contains the fake gate")

    # (14) an ACTIVE, clock-correlated decoration that computes nothing.
    ra = run_one("direct", decoy="active")
    dec = set(ra["machine"].components["decoy_active"])
    seen = [c for c in dec if c in ra["kind"]]
    case("S17 active clock-correlated decoration rejected (seen, alive -- and not a transducer)",
         len(seen) == len(dec) and not any(dec & set(x["cells"]) for x in ra["transducers"])
         and {ra["kind"][c] for c in seen} == {"conductor"},
         f"{len(seen)}/{len(dec)} decoy cells in the candidate set, all conductors, 0 regions")

    # (13) a wire bundle with many frontier crossings and ONE causal source.
    rc = run_one("direct", decoy="cross")
    cx = rc["machine"].components["decoy_cross"]
    case("S18 wire bundle: 3 active geometric neighbours, one causal source, no transducer",
         rc["kind"].get(cx[-1]) == "conductor"
         and not any(set(cx) & set(x["cells"]) for x in rc["transducers"]),
         f"kind={rc['kind'].get(cx[-1])}, 0 regions on the bundle")

    # ================================================================ ABSTENTION, CALIBRATED
    # too many sources to enumerate a joint assignment: abstain, do not guess.
    t = region_of(R["direct"])
    fake = {(0, c): {"lags": [1], "persistent": True, "const_series": True} for c in range(MAX_SOURCES + 2)}
    tr = identify(R["direct"]["world"], list(fake), fake, t["out_cell"], R["direct"]["disc"]["contexts"], 8)
    case("S19 INDETERMINATE when the joint source assignment is not enumerable",
         tr["class"] == "INDETERMINATE" and "sources" in tr["why"], f"{tr['why']}")

    # (10) a context-gated path: with its register at 0 the channel is severed; the edge is still found.
    r0 = run_one("direct", program=(0, 0, 0))
    t = region_of(r0)
    case("S20 context-gated path recovered with the gate held shut by the program",
         t is not None and t["n_sources"] == 2 and tab(t) == AND2 and t["transducer"]["coverage"] == 1.0,
         f"program 000: sources={t and t['n_sources']} table={tab(t)}")

    n = sum(c["PASS"] for c in cases)
    return {"cases": cases, "n_pass": n, "n": len(cases), "QUALIFIED": n == len(cases)}


def main():
    c = certificate()
    print("EXP-GT-SOURCE -- DEVELOPMENT CERTIFICATE (source-transducer observer)")
    print("=" * 104)
    for x in c["cases"]:
        print(f"  [{'PASS' if x['PASS'] else 'FAIL'}] {x['case']}")
        print(f"         {x['detail']}")
    print("=" * 104)
    print(f"  {c['n_pass']}/{c['n']}   QUALIFIED = {c['QUALIFIED']}")
    return c


if __name__ == "__main__":
    main()
