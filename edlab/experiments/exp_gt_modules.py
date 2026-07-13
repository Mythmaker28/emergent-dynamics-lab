"""EXP-GT-MODULES -- the DEVELOPMENT certificate for implementation-independent causal module discovery.

This is the qualification bar for the single authorized repair of D-063. It is built on DEVELOPMENT circuits only.
The burned De Morgan held-out world is NOT certification evidence here: `demorgan` appears below as a *development*
implementation deliberately rebuilt in the development family, and no threshold or rule is tuned on any held-out
answer. Nothing in this file may be relaxed to make a case pass.

WHAT FAILED (D-063). The old gate detector defined a gate as *the earliest cell in a discovered memory's influence
cone*. That is a POSITION, not a computation. On the one held-out world with an unseen micro-implementation, gate
recall was 0.00. The rule had been calibrated on a single implementation without my noticing.

THE REPAIR. A module is a MINIMAL CONNECTED CAUSAL SUBGRAPH whose external boundary has at least two independently
manipulable parents and one or more outputs, and whose joint intervention-response relation cannot be explained as
a lagged copy of any single parent under any discovered context. Boundary, parents, outputs, truth table, delays
and quotient are all INFERRED by intervention. None is received.

EVERY case must fire on a known control: the positives on gates, the negatives on wires, inert decoration,
geometric adjacency and coincident correlation. A detector that only ever says YES has not been tested.
"""

from __future__ import annotations

import numpy as np

from ..substrates.boolnet.circuits import build
from ..substrates.boolnet.evaluator import assert_qualified, gate_core
from ..identity.hier import World, discover
from ..identity.modules import (discover_modules, candidate_cells, macro_quotient,
                                truth_table, MAX_PARENTS)

AND, OR, XOR = (0, 0, 0, 1), (0, 1, 1, 1), (0, 1, 1, 0)
FN = {AND: "AND", OR: "OR", XOR: "XOR"}

# the development module family. `demorgan` is REBUILT here as a development circuit; the held-out world that
# burned it is not consulted, and no rule below is conditioned on it.
IMPLS = ("direct", "direct_buf", "demorgan", "nand2", "xor_or", "or_gate", "xor_gate", "single_parent")
# NEVER used or inspected during the repair; they exist only for the single prospective run:
HELD_OUT_IMPLS = ("and_or", "xnor_and")


def run_one(program=(1, 1, 1), impl="direct", decoy=False, extra_delay=0):
    m = build(program=program, impl=impl, decoy=decoy, extra_delay=extra_delay)
    assert_qualified(m)                       # the machine must WORK before it is allowed to be evidence
    d = discover(m)
    w = World(m.net, m.out_cells)
    cells = candidate_cells(w, d["contexts"])
    r = discover_modules(w, cells, d["contexts"], d["period"])
    # BOUNDARY ground truth is the gate CORE, not the layout grouping: `direct_buf`'s two buffers CONDUCT,
    # they do not compute, and an observer reporting the AND alone is RIGHT, not short by two cells.
    r["truth_gate0"] = gate_core(m, 0)
    r["machine"] = m
    r["disc"] = d
    r["world"] = w
    return r


def gate_of(r):
    hit = [mm for mm in r["modules"] if r["truth_gate0"] & set(mm["cells"])]
    return hit[0] if hit else None


def fn_of(g):
    return FN.get(tuple(v for _, v in g["truth_table"]), g["truth_table"]) if g and g["truth_table"] else None


# ---------------------------------------------------------------- the certificate
def certificate() -> dict:
    cases, R = [], {}

    def case(name, ok, detail=""):
        cases.append({"case": name, "PASS": bool(ok), "detail": detail})

    for impl in IMPLS:
        R[impl] = run_one(impl=impl)

    # ---- MUST PASS: a ONE-CELL two-input gate is recognized, boundary exact.
    g = gate_of(R["direct"])
    case("MP1 one-cell gate recognized",
         g is not None and set(g["cells"]) == R["direct"]["truth_gate0"] and g["n_parents"] == 2
         and fn_of(g) == "AND",
         f"cells={g and len(g['cells'])} parents={g and g['n_parents']} fn={fn_of(g)}")

    # ---- MUST PASS: MULTI-CELL gates are recognized, boundary exact, function recovered.
    for impl, n in (("demorgan", 4), ("nand2", 3), ("xor_or", 3)):
        g = gate_of(R[impl])
        case(f"MP2 multi-cell gate recognized ({impl})",
             g is not None and set(g["cells"]) == R[impl]["truth_gate0"] and len(g["cells"]) == n
             and g["n_parents"] == 2 and fn_of(g) == "AND",
             f"cells={g and len(g['cells'])}/{n} parents={g and g['n_parents']} fn={fn_of(g)}")

    # ---- MUST PASS: the EXTERNAL FUNCTION is recovered despite an UNFAMILIAR INTERNAL IMPLEMENTATION.
    #      Four microscopically different machines; one macro function. This is the whole point of the repair.
    fns = {i: fn_of(gate_of(R[i])) for i in ("direct", "direct_buf", "demorgan", "nand2", "xor_or")}
    sizes = {i: len(gate_of(R[i])["cells"]) for i in fns if gate_of(R[i])}
    case("MP3 external function recovered across implementations",
         set(fns.values()) == {"AND"} and len(set(sizes.values())) > 1,
         f"fns={fns} micro sizes={sizes}")

    # ---- MUST PASS: the MACRO QUOTIENT is EARNED, and reported LEVEL BY LEVEL.
    q1 = macro_quotient(gate_of(R["demorgan"]), gate_of(R["nand2"]))
    case("MP4a quotient earned: demorgan == nand2 (macro SAME, micro DIFFERENT)",
         q1["timed"] == "SAME" and q1["untimed"] == "SAME" and q1["micro"] == "DIFFERENT",
         f"timed={q1['timed']} untimed={q1['untimed']} micro={q1['micro']}")
    q2 = macro_quotient(gate_of(R["direct"]), gate_of(R["demorgan"]))
    case("MP4b same function, DIFFERENT delay -> untimed SAME, timed DIFFERENT (not INDETERMINATE)",
         q2["untimed"] == "SAME" and q2["timed"] == "DIFFERENT"
         and gate_of(R["direct"])["internal_delay"] != gate_of(R["demorgan"])["internal_delay"],
         f"untimed={q2['untimed']} timed={q2['timed']} "
         f"lat {gate_of(R['direct'])['internal_delay']} vs {gate_of(R['demorgan'])['internal_delay']}")

    # ---- MUST PASS: a RECONVERGENT implementation is ONE module, and its TRUE SUB-STRUCTURE is reported.
    #      AND(x,r) = XOR(OR(x,r), XOR(x,r)): three junctions reading the same two parents. The observer must
    #      report ONE macro object computing AND, and -- at the finer scale, earned separately -- the OR and the
    #      two XORs it is actually built from. Both levels are true; neither is granted by a label (addendum A2).
    g = gate_of(R["xor_or"])
    subs = sorted(fn_of(sm) for sm in R["xor_or"]["submodules"] if set(sm["cells"]) <= set(g["cells"]))
    case("MP10 reconvergent gate: ONE macro module, and its true micro sub-structure",
         g is not None and set(g["cells"]) == R["xor_or"]["truth_gate0"] and fn_of(g) == "AND"
         and subs == ["OR", "XOR", "XOR"],
         f"macro fn={fn_of(g)} cells={len(g['cells'])} | micro sub-modules={subs}")
    q4 = macro_quotient(gate_of(R["direct"]), g)
    case("MP4c reconvergent AND == one-cell AND at the untimed macro level, DIFFERENT timed",
         q4["untimed"] == "SAME" and q4["timed"] == "DIFFERENT" and q4["micro"] == "DIFFERENT",
         f"untimed={q4['untimed']} timed={q4['timed']} micro={q4['micro']} "
         f"lat {gate_of(R['direct'])['internal_delay']} vs {g['internal_delay']}")

    # ---- MUST PASS: a DIFFERENT function is not quotiented away.
    q3 = macro_quotient(gate_of(R["or_gate"]), gate_of(R["xor_gate"]))
    case("MP5 different function NOT quotiented (or != xor)",
         q3["untimed"] == "DIFFERENT" and fn_of(gate_of(R["or_gate"])) == "OR"
         and fn_of(gate_of(R["xor_gate"])) == "XOR",
         f"or={fn_of(gate_of(R['or_gate']))} xor={fn_of(gate_of(R['xor_gate']))} untimed={q3['untimed']}")

    # ---- MUST PASS: IDENTICAL SHORT-TERM OUTPUT, DIFFERENT TRUTH TABLE.
    #      At program 000 the OR and XOR worlds emit BYTE-IDENTICAL output traces. Passive observation cannot tell
    #      them apart at any length. Only MANIPULATING the discovered register context separates them.
    m_or = build(program=(0, 0, 0), impl="or_gate")
    m_xo = build(program=(0, 0, 0), impl="xor_gate")
    t_or = np.array(World(m_or.net, m_or.out_cells).trace()[1])
    t_xo = np.array(World(m_xo.net, m_xo.out_cells).trace()[1])
    identical = bool(np.array_equal(t_or, t_xo))
    r_or, r_xo = run_one(program=(0, 0, 0), impl="or_gate"), run_one(program=(0, 0, 0), impl="xor_gate")
    f_or, f_xo = fn_of(gate_of(r_or)), fn_of(gate_of(r_xo))
    case("MP6 identical passive output, different truth table -> separated by context manipulation",
         identical and f_or == "OR" and f_xo == "XOR",
         f"output traces identical={identical}; recovered fns: or={f_or} xor={f_xo}")

    # ---- MUST PASS: a CONDITIONAL edge is discovered by manipulating context, not assumed absent.
    #      With its register at 1, OR(x,1) is SATURATED: the channel->gate edge is dynamically MASKED and invisible
    #      in the baseline. It is recovered ONLY under the discovered context, and it is reported as CONDITIONAL.
    g_or = gate_of(R["or_gate"])
    cond = R["or_gate"]["micro"]["cond"]
    j = [c for c in g_or["cells"]][0]
    in_edges = {p: sorted(cond[(p, j)]) for p in R["or_gate"]["micro"]["parents"][j]}
    masked = [p for p, ctx in in_edges.items() if "base" not in ctx]
    case("MP7 conditional edge discovered by context manipulation (masked in baseline)",
         len(masked) >= 1 and g_or["n_parents"] == 2,
         f"edges into the OR gate: {in_edges}  masked-in-baseline={len(masked)}")

    # ---- MUST FAIL (the detector must say NO): a CASCADE with only ONE EFFECTIVE PARENT.
    #      AND(x, x) has TWO incoming wires and ONE parent. A detector that COUNTS edges calls it a gate.
    case("MF1 coincident correlation rejected (AND(x,x): 2 edges, 1 effective parent)",
         len(R["single_parent"]["modules"]) == 0,
         f"modules found = {len(R['single_parent']['modules'])} (must be 0)")

    # ---- MUST FAIL: an ACTIVE, clock-correlated, DECORATIVE subgraph that computes nothing.
    r_act = run_one(decoy="active")
    dec = set(r_act["machine"].components["decoy_active"])
    seen = [c for c in dec if c in r_act["kind"]]
    touch = [mm for mm in r_act["modules"] if dec & set(mm["cells"])]
    case("MF2 active inert decoration rejected (seen, alive, correlated -- and not a module)",
         len(seen) == len(dec) and len(touch) == 0 and {r_act["kind"][c] for c in seen} == {"conductor"}
         and len(r_act["modules"]) == 3,
         f"decoy cells in candidate set={len(seen)}/{len(dec)} kinds={sorted({r_act['kind'][c] for c in seen})} "
         f"modules touching={len(touch)} real gates still found={len(r_act['modules'])}")

    # ---- MUST FAIL: GEOMETRIC ADJACENCY IS NOT PARENTHOOD.
    r_x = run_one(decoy="cross")
    cx = r_x["machine"].components["decoy_cross"]
    mid = cx[-1]                                   # the cell with three active neighbours carrying three channels
    touch = [mm for mm in r_x["modules"] if set(cx) & set(mm["cells"])]
    case("MF3 wire junction rejected (3 active geometric neighbours, 1 causal parent)",
         mid in r_x["kind"] and r_x["kind"][mid] == "conductor"
         and len(r_x["micro"]["parents"][mid]) == 1 and len(touch) == 0 and len(r_x["modules"]) == 3,
         f"kind={r_x['kind'].get(mid)} causal parents={len(r_x['micro']['parents'].get(mid, []))} "
         f"modules touching={len(touch)} real gates still found={len(r_x['modules'])}")

    # ---- MUST FAIL: pure WIRE chains are never modules.
    wires = sum(1 for k in R["direct"]["kind"].values() if k == "conductor")
    in_mod = {c for mm in R["direct"]["modules"] for c in mm["cells"]}
    wire_in_mod = [c for c, k in R["direct"]["kind"].items() if k == "conductor" and c in in_mod]
    case("MF4 wires never absorbed into a module",
         len(wire_in_mod) == 0 and wires > 50,
         f"{wires} conductors, {len(wire_in_mod)} of them inside a module (must be 0)")

    # ---- MUST PASS: ABSTAIN when parent coverage is UNRESOLVED. A detector that always answers is not calibrated.
    r0 = R["direct"]
    fake = {"parents": [(2, c) for c in range(MAX_PARENTS + 2)], "outputs": [(9, 6)]}
    tt = truth_table(r0["world"], set(), fake, r0["disc"]["contexts"])
    case("MP8 INDETERMINATE when parent coverage is unresolved (no false certainty)",
         tt["table"] is None and "parent coverage" in tt["why"],
         f"verdict={tt.get('why')}")

    # ---- MUST PASS: SCALE-RELATIVE ADMISSION preserved -- the module is atomic at its own scale, and its
    #      sub-parts do not leak an external interface the module does not have.
    g = gate_of(R["demorgan"])
    leaks = [c for c in g["cells"]
             if not (set(R["demorgan"]["micro"]["children"][c]) - set(g["cells"]))
             <= set(g["interface"]["outputs"])]
    case("MP9 scale-relative admission preserved (no sub-part leaks an external interface)",
         len(leaks) == 0,
         f"{len(g['cells'])} internal cells, {len(leaks)} leaking an interface the module lacks (must be 0)")

    n_pass = sum(c["PASS"] for c in cases)
    return {"cases": cases, "n_pass": n_pass, "n": len(cases), "QUALIFIED": n_pass == len(cases)}


def main():
    cert = certificate()
    print("EXP-GT-MODULES -- DEVELOPMENT CERTIFICATE (implementation-independent causal module discovery)")
    print("=" * 104)
    for c in cert["cases"]:
        print(f"  [{'PASS' if c['PASS'] else 'FAIL'}] {c['case']}")
        print(f"         {c['detail']}")
    print("=" * 104)
    print(f"  {cert['n_pass']}/{cert['n']}   QUALIFIED = {cert['QUALIFIED']}")
    return cert


if __name__ == "__main__":
    main()
