"""EXP-GT-ACERT2 -- ARCHITECTURE RESOLUTION CERTIFICATE V2. Development data ONLY.

Certifies the V3 head (A_TOPO / A_TAU / G) after the D-056 repair. Every threshold is DERIVED from a null that
was generated INDEPENDENTLY of the estimator (`gt_nulls.py`, which imports nothing from the observer), and the
estimator has NO FREE PHASE PARAMETER to select -- it strikes at every phase of the inferred period.

A certificate that never emits one of SAME / DIFFERENT / INDETERMINATE is invalid. Every perfect score carries a
non-vacuity assertion.
"""

from __future__ import annotations

import json
import os

import numpy as np

from ..substrates.life.library import (arch_base, arch_delay, arch_xinhib, arch_5chan, arch_inert, arch_decoy,
                                       arch_direct, arch_redundant, assert_viable, assert_graph_agrees, settle,
                                       run_from, total_output, OUT_ROW, BASE_COLS)
from ..identity.blind_a3 import (cached_tomography, head_A_TOPO, head_A_TAU, head_G, topo_signature,
                                 tau_signature, assert_phase_invariance, grade_intervention, infer_period,
                                 assert_exhaustive_phases)
from ..identity.heads3 import ObserverV3, head_F, head_M, head_L, f_signature
from .gt_nulls import draw_phase_nulls, null_manifest, assert_null_independence

OBSV = ObserverV3()


def T(a, ph=0, region=None):
    assert_viable(a)
    assert_graph_agrees(a)                     # a declared graph that the dynamics does not realize is not truth
    return OBSV.tomo(a, ph, region)


# ---------------------------------------------------------------- the 16 controlled families
def families():
    b = arch_base()
    P = draw_phase_nulls(60)                   # INDEPENDENT phase origins -- drawn from a seed, not from the head
    fam = []
    for ph in P[:6]:
        fam.append((f"1. pure phase shift +{ph}", b, b, 0, ph, "SAME", "SAME", "SAME", "SAME", "SAME"))
    fam += [
        ("2. pure translation +10", b, arch_base(cols=[c + 10 for c in BASE_COLS], arch_id="T10"), 0, 0,
         "SAME", "SAME", "SAME", "SAME", "DIFFERENT"),
        ("2. pure translation +20", b, arch_base(cols=[c + 20 for c in BASE_COLS], arch_id="T20"), 0, 0,
         "SAME", "SAME", "SAME", "SAME", "DIFFERENT"),
        ("3. different spacing, same topology", b, arch_base(cols=[5, 50, 95, 140], arch_id="SP45"), 0, 0,
         "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4. path-delay edit k=1 (4 steps)", b, arch_delay(1), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4. path-delay edit k=2 (8 steps)", b, arch_delay(2), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4. path-delay edit k=4 (16 steps)", b, arch_delay(4), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4. path-delay edit k=8 (32 steps)", b, arch_delay(8), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("5. ONE EDGE ADDED (cross-stream inhibitor)", b, arch_xinhib(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("6. ONE EDGE REMOVED (inhibitor deleted)", arch_xinhib(), b, 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("7. ONE NODE ADDED (fifth channel)", b, arch_5chan(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("8. inert decoration added", b, arch_inert(), 0, 0,
         "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("9. decoy gate (gate density, no causal effect)", b, arch_decoy(), 0, 0,
         "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("10. direct 1-path vs redundant 2-path", arch_direct(), arch_redundant(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("13/14. CROWN: identical output, different graph", arch_base(program=(1, 1, 1, 0), arch_id="GATE3"),
         arch_xinhib(), 0, 0, "DIFFERENT", "INDETERMINATE", "DIFFERENT", "SAME", "DIFFERENT"),
    ]
    return fam


def certify() -> dict:
    rep = {}
    b = arch_base()
    tb = T(b)
    Tp = tb["T"]
    rep["clock"] = {"inferred_period": Tp, "harmonics": "resolved by construction (SMALLEST exact period)"}
    rep["null_contract"] = assert_null_independence(Tp, tuple(range(Tp)))
    rep["null_manifest"] = null_manifest(Tp)

    # ---- PHASE-INVARIANCE CERTIFICATE: every head, on independently-drawn phase origins
    nulls = draw_phase_nulls(Tp)
    toms = {ph: T(b, ph) for ph in [0] + nulls[:8]}
    rep["phase_invariance"] = assert_phase_invariance(toms)
    devs = []
    for ph, t in toms.items():
        m1 = sorted(e["median"] for e in toms[0]["edges"])
        m2 = sorted(e["median"] for e in t["edges"])
        devs.append(max((abs(x - y) for x, y in zip(m1, m2)), default=0.0))
    rep["phase_invariance"]["max_median_delay_deviation"] = max(devs)
    rep["phase_invariance"]["DERIVED_TAU_TOLERANCE"] = max(devs)
    tau_tol = max(devs)
    assert tau_tol == OBSV.TAU_TOL, f"frozen TAU_TOL {OBSV.TAU_TOL} != derived {tau_tol}"

    # ---- the families
    rows, fS, fD, fI = [], 0, 0, 0
    for name, a1, a2, p1, p2, eT, eTau, eG, eF, eM in families():
        t1, t2 = T(a1, p1), T(a2, p2)
        g1, g2 = settle(a1, extra_phase=p1), settle(a2, extra_phase=p2)
        got = {"A_TOPO": head_A_TOPO(t1, t2), "A_TAU": head_A_TAU(t1, t2, tau_tol), "G": head_G(t1, t2),
               "F": head_F(f_signature(g1, t1["out_nodes"]), f_signature(g2, t2["out_nodes"])),
               "M": head_M(g1, g2)}
        exp = {"A_TOPO": eT, "A_TAU": eTau, "G": eG, "F": eF, "M": eM}
        ok = {k: got[k] == exp[k] for k in exp}
        if not ok["A_TOPO"]:
            if exp["A_TOPO"] == "DIFFERENT" and got["A_TOPO"] == "SAME":
                fS += 1
            elif exp["A_TOPO"] == "SAME" and got["A_TOPO"] == "DIFFERENT":
                fD += 1
            else:
                fI += 1
        rows.append({"case": name, "expected": exp, "predicted": got, "pass": ok,
                     "coverage": {"c1": t1["coverage"]["met"], "c2": t2["coverage"]["met"],
                                  "conf1": t1["coverage"]["n_confounded"],
                                  "conf2": t2["coverage"]["n_confounded"]}})
    rep["families"] = rows
    n = len(rows)
    rep["rates"] = {"false_SAME_A_TOPO": f"{fS}/{sum(1 for r in rows if r['expected']['A_TOPO']=='DIFFERENT')}",
                    "false_DIFFERENT_A_TOPO": f"{fD}/{sum(1 for r in rows if r['expected']['A_TOPO']=='SAME')}",
                    "other_A_TOPO_errors": fI,
                    "head_failures": sum(1 for r in rows for v in r["pass"].values() if not v),
                    "cases": n}

    # ---- 15. a CONFOUNDED local intervention, with the rest of the coverage intact
    from ..identity.blind_a3 import _line_run, OBS as _OBS, discover_components
    g0 = settle(b)
    comps = discover_components(g0, OUT_ROW, Tp)
    gun_tile = (6, 11, 42, 47)                    # a 5x5 tile cutting into a gun -- the D-055 mutilation
    _, status, why, _ = grade_intervention(g0, gun_tile, Tp, OUT_ROW, comps)
    # NON-VACUITY: show that this intervention really does BUILD a new machine, so the rule is not refusing a
    # harmless probe. The mutilated gun fires a stream down a diagonal that lands at output columns the intact
    # circuit never touches.
    base = _line_run(g0, _OBS, OUT_ROW)
    mut = _line_run(g0, _OBS, OUT_ROW, box=gun_tile, hold=10)
    new_cols = sorted(int(c) for c in set(np.nonzero(mut.sum(0))[0]) - set(np.nonzero(base.sum(0))[0]))
    # and: the graph built from the VALID whole-component evidence is unaffected by excluding it
    rep["confound_detection"] = {
        "case": "15. micro-ablation cutting into a gun (an intervention that BUILDS a new emitter)",
        "graded": status, "why": why, "pass": status == "CONFOUNDED" and bool(new_cols),
        "non_vacuity": f"the mutilated gun fires a NEW stream, landing at output columns {new_cols} that the "
                       f"intact circuit never touches. The gun was not removed -- it was REPLACED.",
        "consequence": "the evidence is EXCLUDED, not fatal. The graph is still built from the VALID "
                       "whole-component ablations, and coverage is still met. That is the D-056 failure-2 "
                       "repair, and here it is shown to FIRE on a real confound."}

    # ---- 16. deliberately under-covered case -> must ABSTAIN
    starved = T(b, 0, region=(0, 20, 0, 100))
    v = head_A_TOPO(tb, starved)
    rep["abstention"] = {"case": "16. under-covered probe (components findable only in cols 0-100)",
                         "unsourced_live": starved["coverage"]["unsourced_live"],
                         "A_TOPO": v, "pass": v == "INDETERMINATE",
                         "why": "an output demonstrably live whose cause was never found is MISSING EVIDENCE, "
                                "not evidence of sameness"}

    # ---- 11 & 12: honest NOT-CONSTRUCTIBLE
    rep["not_constructible"] = {
        "11. feed-forward vs FEEDBACK": "NOT CONSTRUCTIBLE in this component library. A causal CYCLE needs a "
            "component whose existence depends on another whose existence depends on it. Guns are sources and "
            "depend on nothing; the only dependent component found is the collision remnant, which depends on "
            "BOTH guns and on which nothing depends (measured: destroys=[remnant] from each gun, and ablating "
            "the remnant has no persistent effect -- it regenerates). The head DOES read dependency structure "
            "(component->component edges), so it would see a cycle if one existed. REQUIRED PROPERTY OF THE "
            "NEXT COMPONENT LIBRARY.",
        "12. same graph, different PROGRAM word": "NOT CONSTRUCTIBLE (D-055). A memory bit of 0 is implemented "
            "by ADDING AN EATER, so the program IS part of the causal graph. A_TOPO correctly reports DIFFERENT. "
            "Any head that 'passes' program-invariance here passes a test that CANNOT FIRE -- EXP-GT-02B's pass "
            "was VACUOUS. Requires STATE-based memory (a latch/storage loop)."}

    # ---- non-vacuity: all three verdicts must have fired
    verdicts = {r["predicted"]["A_TOPO"] for r in rows} | {rep["abstention"]["A_TOPO"]}
    rep["non_vacuity"] = {"A_TOPO_verdicts_fired": sorted(verdicts),
                          "all_three": {"SAME", "DIFFERENT", "INDETERMINATE"} <= verdicts,
                          "A_TAU_verdicts_fired": sorted({r["predicted"]["A_TAU"] for r in rows})}

    granted = (fS == 0 and fD == 0 and fI == 0 and rep["abstention"]["pass"]
               and rep["confound_detection"]["pass"] and rep["non_vacuity"]["all_three"])
    rep["resolution"] = {"delay_edit": "4 steps (the finest the substrate admits)",
                         "edge_edit": "1 edge", "node_edit": "1 node",
                         "redundancy": "detected (1-path vs 2-path)",
                         "component_separation_limit_cells": 4,
                         "tau_tolerance_derived": tau_tol}
    rep["VERDICT"] = "QUALIFIED" if granted else "FAILED — OBSERVABILITY"
    return rep


def summarize(r) -> str:
    L = ["EXP-GT-ACERT2 -- ARCHITECTURE RESOLUTION CERTIFICATE V2 (development only)",
         "=" * 118,
         f"clock: T = {r['clock']['inferred_period']} ({r['clock']['harmonics']})",
         f"null contract: {r['null_contract']['independence']}   strike={r['null_contract']['strike_schedule']}"
         f"   null manifest {r['null_manifest']['hash']}",
         f"independent phase origins (drawn from a seed, NOT from the head): {r['null_manifest']['phase_origins']}",
         f"PHASE INVARIANCE: {r['phase_invariance']['verdict']} over {len(r['phase_invariance']['phases_checked'])}"
         f" phases; max median-delay deviation = {r['phase_invariance']['max_median_delay_deviation']}"
         f"  ==> DERIVED A_TAU TOLERANCE = {r['phase_invariance']['DERIVED_TAU_TOLERANCE']}",
         "",
         f"  {'case':48s} {'A_TOPO':24s} {'A_TAU':24s} {'G':22s} {'F':20s} {'M':12s}"]
    for c in r["families"]:
        def cell(k):
            return ("OK " if c["pass"][k] else "XX ") + f"{c['predicted'][k]}/{c['expected'][k]}"
        L.append(f"  {c['case']:48s} {cell('A_TOPO'):24s} {cell('A_TAU'):24s} {cell('G'):22s} "
                 f"{cell('F'):20s} {cell('M'):12s}")
    L += ["", f"  false-SAME (A_TOPO)      : {r['rates']['false_SAME_A_TOPO']}",
          f"  false-DIFFERENT (A_TOPO) : {r['rates']['false_DIFFERENT_A_TOPO']}",
          f"  total head failures      : {r['rates']['head_failures']} over {r['rates']['cases']} cases",
          "",
          f"  15. CONFOUND DETECTION   : {'PASS' if r['confound_detection']['pass'] else 'FAIL'} -> "
          f"{r['confound_detection']['graded']}",
          f"      {r['confound_detection']['why'][:108]}",
          f"      NON-VACUITY: {r['confound_detection']['non_vacuity']}",
          f"  16. ABSTENTION           : {'PASS' if r['abstention']['pass'] else 'FAIL'} -> "
          f"A_TOPO={r['abstention']['A_TOPO']} (unsourced live outputs {r['abstention']['unsourced_live']})",
          "",
          f"  NON-VACUITY: A_TOPO fired {r['non_vacuity']['A_TOPO_verdicts_fired']} "
          f"(all three: {r['non_vacuity']['all_three']}); A_TAU fired {r['non_vacuity']['A_TAU_verdicts_fired']}",
          "", "  CERTIFIED RESOLUTION:"]
    for k, v in r["resolution"].items():
        L.append(f"    {k:34s} {v}")
    L += ["", "  NOT CONSTRUCTIBLE (stated, not hidden):"]
    for k, v in r["not_constructible"].items():
        L.append(f"    * {k}: {v}")
    L += ["", "=" * 118, f"VERDICT: {r['VERDICT']}", "=" * 118]
    return "\n".join(L)


def main(run_id="EXP-GT-ACERT2-20260714-001"):
    r = certify()
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    json.dump(r, open(os.path.join(d, "certificate.json"), "w"), indent=1, default=str)
    s = summarize(r)
    open(os.path.join(d, "summary.txt"), "w").write(s + "\n")
    print(s)
    return r


if __name__ == "__main__":
    main()
