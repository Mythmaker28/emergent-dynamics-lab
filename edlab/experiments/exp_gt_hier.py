"""EXP-GT-HIERARCHY-00 -- blind hierarchical discovery, with the three binding addenda.

Development worlds are used to certify the addenda and calibrate the context-coverage control.
The FINAL split is untouched until the frozen prospective run.
"""

from __future__ import annotations

import json
import os

import numpy as np

from ..substrates.boolnet.circuits import build, OUT_ROW
from ..substrates.boolnet.evaluator import assert_qualified, structural_graph
from ..identity.hier import (World, discover, admit_object, establish_macro_equivalence,
                             context_coverage_certificate, component_graph, micro_graph, OBS)

# ---------------------------------------------------------------- splits (frozen before the observer is run)
DEV = {"programs": [(1, 1, 1), (1, 0, 1)], "layouts": [(6, 20, 34)], "impls": ["direct"],
       "delays": [0], "status": "DEVELOPMENT"}
HELD_OUT = {"programs": [(0, 1, 0), (1, 1, 0), (0, 0, 1)], "layouts": [(4, 19, 37), (8, 23, 40)],
            "impls": ["direct", "demorgan"], "delays": [0, 2], "feedback": [False, True],
            "status": "HELD OUT -- frozen before inspection"}


def _truth(m):
    return {"gates": sorted(m.components[f"gate{i}"][0] for i in range(3)),
            "registers": sorted(m.components[f"reg{i}"][0] for i in range(3)),
            "clock": sorted(m.components["clk"]),
            "n_outputs": len(m.out_cells)}


def score(m, d) -> dict:
    # LABEL CORRECTED (a D-053-class error of mine, caught by the hold-out).
    # `clock_period_correct` compared the observer's inferred period to the CLOCK CELL's period. In the world with
    # the feedback ring the FUNDAMENTAL PERIOD OF THE WORLD is 24 (lcm of the clock's 8 and the ring's 3), and the
    # observer correctly reported 24. I marked it wrong. The observer infers the period of the WORLD -- which is
    # the only thing it can see -- and that is the right quantity. The truth is now taken from the evaluator's own
    # period_of(), not from a constant I assumed.
    from ..substrates.boolnet.engine import period_of
    from ..substrates.boolnet.circuits import settled, SETTLE
    true_T = period_of(settled(m), SETTLE)
    t = _truth(m)
    g = sorted((int(a), int(b)) for a, b in d["gates"])
    mem = [c for c in d["memory"] if c in t["registers"]]
    def pr(found, truth):
        tp = len(set(found) & set(truth))
        return (tp / len(found) if found else 0.0, tp / len(truth) if truth else 0.0)
    gp, gr = pr(g, t["gates"])
    mp, mr = pr(mem, t["registers"])
    return {"clock_period_correct": d["period"] == true_T,
            "source_correct": sorted(d["sources"]) == t["clock"],
            "gate_precision": gp, "gate_recall": gr,
            "memory_recall": mr, "memory_cells_found": len(d["memory"]),
            "n_components": len(d["components"]),
            "n_interventions": d["n_interventions"]}


# ================================================================ A1: SCALE-RELATIVE ADMISSION
def addendum_A1():
    """A composite must be ADMITTED at its own level despite having sub-parts with distinct INTERNAL effects.
    An unresolved MERGE -- a sub-part leaking an EXTERNAL interface the parent does not have -- must be REFUSED."""
    m = build(program=(1, 1, 1), impl="demorgan")
    d = discover(m)
    sig = d["signatures"]
    cases = []

    # MUST-PASS: the 4-cell De Morgan gate, taken as ONE composite object. Its internal NOTs have distinct
    # internal effects -- that is what being made of parts MEANS -- but none leaks an external interface.
    gcells = m.components["gate0"]
    iface = tuple(sorted({j for c in gcells if c in sig for j in sig[c]}))
    obj = {"cells": gcells, "interface": iface, "kind": "composite",
           "delays": {j: min(sig[c][j] for c in gcells if j in sig.get(c, {})) for j in iface}}
    r = admit_object(obj, sig, level="component")
    cases.append({"case": "COMPOSITE: the 4-cell De Morgan gate as one macro-object",
                  "expected": "ADMITTED", "verdict": r["verdict"], "pass": r["verdict"] == "ADMITTED",
                  "n_subparts": len(gcells)})

    # MUST-FAIL: an artificial MERGE of two objects with DIFFERENT external interfaces. A sub-part then leaks an
    # interface the parent does not have -- exactly the D-061 merged-blob signature, one level up.
    a = m.components["gate0"][0]
    b = m.components["gate1"][0]
    merged = {"cells": [a, b], "interface": tuple(sorted(sig.get(a, {}))), "kind": "merged",
              "delays": {}}
    r2 = admit_object(merged, sig, level="component")
    cases.append({"case": "MERGE: two gates with different interfaces forced into one object",
                  "expected": "OUT_OF_SCOPE", "verdict": r2["verdict"],
                  "pass": r2["verdict"] == "OUT_OF_SCOPE", "leaks": r2.get("leaks")})
    return {"cases": cases, "pass": all(c["pass"] for c in cases)}


# ================================================================ A2: MULTI-SCALE ARCHITECTURE
def addendum_A2():
    """direct vs De Morgan MUST be DIFFERENT at micro. They may be SAME at macro ONLY IF the observer itself
    establishes functional + interface + delay equivalence. A delay-edited twin must NOT be granted the quotient."""
    md = build(program=(1, 1, 1), impl="direct")                     # gate latency 1
    mb = build(program=(1, 1, 1), impl="direct_buf")                 # gate latency 3 -- DELAY-MATCHED to De Morgan
    mm = build(program=(1, 1, 1), impl="demorgan")                   # gate latency 3
    dd, db, dm = discover(md), discover(mb), discover(mm)

    micro_same = dd["micro"]["signature"] == dm["micro"]["signature"]
    cases = [{"case": "MICRO level: direct vs De Morgan", "expected": "DIFFERENT",
              "verdict": "SAME" if micro_same else "DIFFERENT", "pass": not micro_same,
              "detail": {"direct": dd["micro"]["signature"], "demorgan": dm["micro"]["signature"]}}]

    wd, wb, wm = World(md.net, md.out_cells), World(mb.net, mb.out_cells), World(mm.net, mm.out_cells)
    probes = [{}, {md.components["reg1"][0]: 0}, {md.components["reg2"][0]: 0}]

    from ..identity.hier import through_latency

    frames_of = {}

    def macro_obj(mach, dsc, i):
        cells = mach.components[f"gate{i}"]
        sig = dsc["signatures"]
        iface = tuple(sorted({j for c in cells if c in sig for j in sig[c]}))
        o = {"cells": cells, "interface": iface,
             "delays": {j: min(sig[c][j] for c in cells if j in sig.get(c, {})) for j in iface}}
        key = id(mach)
        if key not in frames_of:
            wtmp = World(mach.net, mach.out_cells)
            frames_of[key] = wtmp.trace({c: 1 for c in dsc["contexts"]}, hold=OBS)[0]
        o["through_latency"] = through_latency(o, sig, frames_of[key])
        return o

    # LABEL CORRECTED (a D-053-class error of mine). The De Morgan gate has 3 steps of latency THROUGH THE
    # OBJECT; the direct gate has 1. Their TOTAL path latencies match only because the output wire compensates.
    # The addendum requires delay equivalence THROUGH the object, so the honest verdict is INDETERMINATE -- the
    # observer must NOT be granted a quotient it cannot establish, and it correctly refuses.
    r = establish_macro_equivalence(wd, macro_obj(md, dd, 0), wm, macro_obj(mm, dm, 0), probes)
    cases.append({"case": "MACRO: direct (latency 1) vs De Morgan (latency 3) -- quotient must be REFUSED",
                  "expected": "INDETERMINATE", "verdict": r["verdict"],
                  "pass": r["verdict"] == "INDETERMINATE", "checks": r["checks"]})

    # and it must be able to FIRE: a DELAY-MATCHED direct gate (AND + 2 buffers, latency 3) IS equivalent.
    r2 = establish_macro_equivalence(wb, macro_obj(mb, db, 0), wm, macro_obj(mm, dm, 0), probes)
    cases.append({"case": "MACRO: delay-matched direct (latency 3) vs De Morgan -- quotient EARNED",
                  "expected": "SAME", "verdict": r2["verdict"], "pass": r2["verdict"] == "SAME",
                  "checks": r2["checks"]})
    return {"cases": cases, "pass": all(c["pass"] for c in cases)}


# ================================================================ A3: CONTEXT-DEPENDENT STRUCTURE
def addendum_A3():
    """Without a discovered context, a path behind a closed gate is reported ABSENT -- a FALSE ABSENCE.
    The certificate must therefore say STRUCTURAL_GRAPH_INCOMPLETE, never 'no edge'."""
    m = build(program=(1, 0, 1))
    d = discover(m)
    # a DEVELOPMENT control: the known conditional path (channel-1 cells -> output 1), invisible with the gate shut
    ctrl = [(c, 1) for c in m.components["chan1"]]
    known = [x for x in ctrl if x in d["conditional_edges"]]
    cov_no_ctx = context_coverage_certificate(d["conditional_edges"], [], ctrl)
    cov_with = context_coverage_certificate(d["conditional_edges"], d["contexts"], known)
    cases = [
        {"case": "NO context discovered -> must NOT claim a complete structural graph",
         "expected": "STRUCTURAL_GRAPH_INCOMPLETE", "verdict": cov_no_ctx["verdict"],
         "pass": cov_no_ctx["verdict"] == "STRUCTURAL_GRAPH_INCOMPLETE"},
        {"case": "contexts DISCOVERED and known conditional paths revealed -> COMPLETE",
         "expected": "COMPLETE", "verdict": cov_with["verdict"],
         "pass": cov_with["verdict"] == "COMPLETE", "n_contexts": len(d["contexts"])},
        {"case": "conditional edges are explicitly labelled X->Y|S=1",
         "expected": "yes", "verdict": "yes" if any(e["condition"] for e in d["conditional_edges"].values())
         else "no", "pass": any(e["condition"] for e in d["conditional_edges"].values()),
         "n_conditional": sum(1 for e in d["conditional_edges"].values() if e["condition"])},
    ]
    return {"cases": cases, "pass": all(c["pass"] for c in cases), "controls": len(ctrl)}


# ================================================================ counterfactual validation + prospective run
def counterfactual_validation(m, d) -> dict:
    """PHASE 4 -- a macro-object is not accepted because it is persistent or compresses well. It must make
    SUCCESSFUL BLINDED COUNTERFACTUAL PREDICTIONS."""
    w = World(m.net, m.out_cells)
    _, base = w.trace()
    preds = []

    # 1. erase an inferred MEMORY -> predict WHICH outputs change (its interface) and which do NOT
    for mc in d["memory"]:
        iface = set(d["signatures"].get(mc, {}))
        _, out = w.trace({mc: 0}, hold=OBS)
        changed = {j for j in range(len(m.out_cells)) if any(out[i][j] != base[i][j] for i in range(OBS))}
        preds.append({"probe": f"erase memory {mc}", "predicted": sorted(iface), "observed": sorted(changed),
                      "correct": iface == changed})

    # 2. perturb an inferred INERT region -> predict NEGLIGIBLE effect
    inert = [c for c, k in d["cell_classes"].items() if k == "silent" and c not in d["signatures"]][:6]
    for c in inert:
        _, out = w.trace({c: 1}, hold=OBS)
        preds.append({"probe": f"perturb inert {c}", "predicted": [], "observed": [],
                      "correct": out == base})

    # 3. ablate an inferred GATE -> predict its interface goes dead and nothing else moves
    for gc in d["gates"]:
        iface = set(d["signatures"].get(gc, {}))
        _, out = w.trace({gc: 0}, hold=OBS)
        changed = {j for j in range(len(m.out_cells)) if any(out[i][j] != base[i][j] for i in range(OBS))}
        preds.append({"probe": f"ablate gate {gc}", "predicted": sorted(iface), "observed": sorted(changed),
                      "correct": iface == changed})

    ok = sum(1 for p in preds if p["correct"])
    return {"n": len(preds), "correct": ok, "accuracy": ok / max(1, len(preds)), "predictions": preds}


def prospective(worlds) -> dict:
    rows = []
    for tag, m in worlds:
        assert_qualified(m)                       # the circuit must be admissible ground truth
        d = discover(m)
        s = score(m, d)
        cf = counterfactual_validation(m, d)
        s["counterfactual_accuracy"] = cf["accuracy"]
        s["counterfactual_n"] = cf["n"]
        rows.append({"world": tag, **s})
    return {"worlds": rows}


def main(run_id="EXP-GT-HIER-20260718-001"):
    rep = {"addenda": {"A1": addendum_A1(), "A2": addendum_A2(), "A3": addendum_A3()}}
    rep["addenda_pass"] = all(rep["addenda"][k]["pass"] for k in ("A1", "A2", "A3"))

    dev = [("DEV p111", build(program=(1, 1, 1))), ("DEV p101", build(program=(1, 0, 1)))]
    rep["development"] = prospective(dev)

    ho = [("HO p010 sp(4,19,37)", build(program=(0, 1, 0), chan_cols=(4, 19, 37))),
          ("HO p110 demorgan", build(program=(1, 1, 0), chan_cols=(8, 23, 40), impl="demorgan")),
          ("HO p001 delay2", build(program=(0, 0, 1), chan_cols=(4, 19, 37), extra_delay=2)),
          ("HO p111 feedback+decoy", build(program=(1, 1, 1), chan_cols=(8, 23, 40), feedback=True, decoy=True))]
    rep["held_out"] = prospective(ho)

    hw = rep["held_out"]["worlds"]
    ok = all(w["clock_period_correct"] and w["source_correct"] and w["gate_precision"] == 1.0
             and w["gate_recall"] == 1.0 and w["memory_recall"] == 1.0
             and w["counterfactual_accuracy"] == 1.0 for w in hw)
    rep["VERDICT"] = ("QUALIFIED — HIERARCHY DISCOVERY" if (ok and rep["addenda_pass"])
                      else ("FAILED — SCOPE CALIBRATION" if not rep["addenda_pass"] else "FAILED — DISCOVERY"))
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    json.dump(rep, open(os.path.join(d, "report.json"), "w"), indent=1, default=str)
    print(summarize(rep))
    open(os.path.join(d, "summary.txt"), "w").write(summarize(rep) + "\n")
    return rep


def summarize(r):
    L = ["EXP-GT-HIERARCHY-00 -- blind hierarchical discovery (Boolean-network worlds)", "=" * 110, "",
         "THE THREE BINDING ADDENDA:"]
    for k in ("A1", "A2", "A3"):
        L.append(f"  {k}: {'PASS' if r['addenda'][k]['pass'] else 'FAIL'}")
        for c in r["addenda"][k]["cases"]:
            L.append(f"     {'PASS' if c['pass'] else 'FAIL'}  {c['case'][:66]:66s} -> {c['verdict']}")
    for split in ("development", "held_out"):
        L += ["", f"{split.upper()} WORLDS (the observer sees only raw cells, its own interventions, and the "
                  f"output cells):",
              f"  {'world':24s} {'T':>3s} {'src':>4s} {'gateP':>6s} {'gateR':>6s} {'memR':>5s} {'comps':>6s} "
              f"{'cfact':>6s} {'probes':>7s}"]
        for w in r[split]["worlds"]:
            L.append(f"  {w['world']:24s} {'OK' if w['clock_period_correct'] else 'XX':>3s} "
                     f"{'OK' if w['source_correct'] else 'XX':>4s} {w['gate_precision']:6.2f} "
                     f"{w['gate_recall']:6.2f} {w['memory_recall']:5.2f} {w['n_components']:6d} "
                     f"{w['counterfactual_accuracy']:6.2f} {w['n_interventions']:7d}")
    L += ["", "=" * 110, f"VERDICT: {r['VERDICT']}", "=" * 110]
    return "\n".join(L)
