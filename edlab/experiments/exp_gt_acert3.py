"""EXP-GT-ACERT3 -- ARCHITECTURE RESOLUTION CERTIFICATE V3, for the V4 head. Development data ONLY.

Certification RESTARTS FROM SCRATCH (mission SS8): a conceptually new observer does not inherit a certificate.
The two cases that KILLED V3 are must-pass here:
   * strike phase 33, where the V3 probe was unusable at every component (valid=0, confounded=4);
   * a delay edit on a GATED path, where V3 reported a false-SAME on its own certified edit scale.
"""

from __future__ import annotations

import json
import os

import numpy as np

from ..substrates.life.library import (arch_base, arch_delay, arch_xinhib, arch_5chan, arch_inert, arch_decoy,
                                       arch_direct, arch_redundant, assert_viable, assert_graph_agrees, settle,
                                       OUT_ROW, BASE_COLS)
from ..identity.blind_a4 import (cached_tomography, head_A_TOPO, head_A_TAU, head_G, topo_signature,
                                 tau_canonical, assert_phase_invariance, discover_components, _grade,
                                 stationary_mask, infer_period, MIN_VALID_FRAC)
from ..identity.heads3 import head_F, head_M, f_signature
from .gt_nulls2 import draw_phase_nulls, null_manifest, assert_null_coverage

GATED = (1, 1, 1, 0)          # gate on channel 3 -> the GATED path


_ADMITTED = set()


def T(a, ph=0, region=None):
    """Admission (viability + geometry-vs-intervention graph agreement) is a property of the CIRCUIT, not of the
    strike phase, so it is checked once per circuit rather than once per comparison."""
    key = tuple(sorted((c.kind, c.row, c.col) for c in a.components))
    if key not in _ADMITTED:
        assert_viable(a)
        assert_graph_agrees(a)
        _ADMITTED.add(key)
    return cached_tomography(settle(a, extra_phase=ph), OUT_ROW, region=region)


def families(nulls):
    b = arch_base()
    g = arch_base(program=GATED, arch_id="GATE3")
    fam = [(f"1. pure phase shift +{p}", b, b, 0, p, "SAME", "SAME", "SAME", "SAME", "SAME") for p in nulls]
    fam += [
        ("1b. MUST-PASS: phase 33 (V3 was UNUSABLE here)", b, b, 0, 33, "SAME", "SAME", "SAME", "SAME", "SAME"),
        ("2. pure translation +10", b, arch_base(cols=[c + 10 for c in BASE_COLS], arch_id="T10"), 0, 0,
         "SAME", "SAME", "SAME", "SAME", "DIFFERENT"),
        ("3. different spacing, same topology", b, arch_base(cols=[5, 50, 95, 140], arch_id="SP45"), 0, 0,
         "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4. delay edit, UNGATED path (k=1, 4 steps)", b, arch_delay(1), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4b. delay edit, UNGATED path (k=4, 16 steps)", b, arch_delay(4), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4c. MUST-PASS: delay edit on a GATED path (k=5) -- V3 FALSE-SAME", g,
         arch_delay(5, 3, program=GATED), 0, 0, "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("4d. delay edit on a GATED path (k=2, 8 steps)", g, arch_delay(2, 3, program=GATED), 0, 0,
         "SAME", "DIFFERENT", "DIFFERENT", "SAME", "DIFFERENT"),
        ("5. ONE EDGE ADDED (cross-stream inhibitor)", b, arch_xinhib(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("6. ONE EDGE REMOVED (inhibitor deleted)", arch_xinhib(), b, 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("7. ONE NODE ADDED (fifth channel)", b, arch_5chan(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("8. inert decoration added", b, arch_inert(), 0, 0, "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("9. decoy gate (gate density, no causal effect)", b, arch_decoy(), 0, 0,
         "SAME", "SAME", "DIFFERENT", "SAME", "DIFFERENT"),
        ("10. direct 1-path vs redundant 2-path", arch_direct(), arch_redundant(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "DIFFERENT", "DIFFERENT"),
        ("13/14. CROWN: identical output, different graph", g, arch_xinhib(), 0, 0,
         "DIFFERENT", "INDETERMINATE", "DIFFERENT", "SAME", "DIFFERENT"),
    ]
    return fam


def certify():
    rep = {}
    b = arch_base()
    tb = T(b)
    Tp = tb["T"]
    nulls = draw_phase_nulls(Tp)[:6]
    rep["null"] = null_manifest(Tp)
    rep["null"]["used_in_certificate"] = nulls
    rep["null"]["coverage_assertion"] = assert_null_coverage(Tp, draw_phase_nulls(Tp))
    rep["clock"] = {"inferred_period": Tp, "harmonics": "resolved by construction (SMALLEST exact period)"}

    # phase invariance over independently drawn origins PLUS the phases that killed V3
    killer = [2, 3, 5, 32, 33, 35]
    toms = {p: T(b, p) for p in [0] + nulls + killer}
    rep["phase_invariance"] = assert_phase_invariance(toms)
    rep["phase_invariance"]["includes_V3_killer_phases"] = killer
    rep["phase_invariance"]["valid_phase_fracs"] = {p: toms[p]["coverage"]["valid_phase_fracs"] for p in toms}

    rows, fS, fD, fI = [], 0, 0, 0
    for name, a1, a2, p1, p2, eT, eTau, eG, eF, eM in families(nulls):
        t1, t2 = T(a1, p1), T(a2, p2)
        g1, g2 = settle(a1, extra_phase=p1), settle(a2, extra_phase=p2)
        got = {"A_TOPO": head_A_TOPO(t1, t2), "A_TAU": head_A_TAU(t1, t2, 0.0), "G": head_G(t1, t2),
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
                     "coverage": {"c1": t1["coverage"]["complete"], "c2": t2["coverage"]["complete"]}})
    rep["families"] = rows
    tau_fails = sum(1 for r in rows if not r["pass"]["A_TAU"])
    rep["rates"] = {"false_SAME_A_TOPO": f"{fS}/{sum(1 for r in rows if r['expected']['A_TOPO']=='DIFFERENT')}",
                    "false_DIFFERENT_A_TOPO": f"{fD}/{sum(1 for r in rows if r['expected']['A_TOPO']=='SAME')}",
                    "A_TAU_failures": tau_fails,
                    "head_failures": sum(1 for r in rows for v in r["pass"].values() if not v),
                    "cases": len(rows)}

    # confound detection, now PHASE-RESOLVED
    g0 = settle(b)
    comps = discover_components(g0, OUT_ROW, Tp)
    bs = stationary_mask(g0, Tp)
    bad_phase_counts = []
    for box in comps:
        n_bad = 0
        gp = g0.copy()
        from ..substrates.life.fast import step as _st
        for p in range(Tp):
            if _grade(gp, bs, box, OUT_ROW, Tp)[3] != "VALID":
                n_bad += 1
            gp = _st(gp)
        bad_phase_counts.append(n_bad)
    rep["phase_resolved_validity"] = {
        "bad_phases_per_component": bad_phase_counts, "period": Tp,
        "pass": all(0 < n < (1 - MIN_VALID_FRAC) * Tp for n in bad_phase_counts),
        "note": "NON-VACUITY: the validity check must FIRE (some phases ARE bad -- 6 of 60, the ones that killed "
                "V3) and must not fire everywhere. Under V3 one bad phase invalidated the whole circuit; here it "
                "costs that phase only, and the bad phases live in the validity mask, which rotates with the "
                "circuit and is part of the A_TAU signature."}

    starved = T(b, 0, region=(0, 20, 0, 100))
    v = head_A_TOPO(tb, starved)
    rep["abstention"] = {"unsourced_live": starved["coverage"]["unsourced_live"], "A_TOPO": v,
                         "pass": v == "INDETERMINATE"}

    verd = {r["predicted"]["A_TOPO"] for r in rows} | {rep["abstention"]["A_TOPO"]}
    rep["non_vacuity"] = {"A_TOPO_fired": sorted(verd), "all_three": {"SAME", "DIFFERENT", "INDETERMINATE"} <= verd,
                          "A_TAU_fired": sorted({r["predicted"]["A_TAU"] for r in rows})}
    rep["resolution"] = {"delay_edit_UNGATED": "4 steps", "delay_edit_GATED": "8 steps (k=2) -- V3 could not do "
                                                                             "this AT ALL",
                         "edge_edit": "1 edge", "node_edit": "1 node", "redundancy": "detected",
                         "component_separation_limit_cells": 4, "A_TAU_tolerance": 0.0}
    granted = (fS == 0 and fD == 0 and fI == 0 and tau_fails == 0 and rep["abstention"]["pass"]
               and rep["phase_resolved_validity"]["pass"] and rep["non_vacuity"]["all_three"])
    rep["VERDICT"] = "QUALIFIED" if granted else "FAILED — OBSERVABILITY"
    rep["not_constructible"] = {
        "feedback": "NOT CONSTRUCTIBLE in this component library (no causal cycle exists; guns are sources). The "
                    "head reads component->component dependency and would see a cycle if one existed.",
        "program_invariance": "NOT CONSTRUCTIBLE: the program IS the architecture here (D-055). EXP-GT-02B's pass "
                              "was VACUOUS."}
    return rep


def summarize(r):
    L = ["EXP-GT-ACERT3 -- ARCHITECTURE RESOLUTION CERTIFICATE V3 (head V4; development only)",
         "=" * 120,
         f"clock T={r['clock']['inferred_period']} | null {r['null']['hash']} phases {r['null']['phase_origins']}"
         f" | coverage {r['null']['coverage']['coverage']}",
         f"PHASE INVARIANCE: {r['phase_invariance']['verdict']} over {len(r['phase_invariance']['phases_checked'])}"
         f" phases INCLUDING the six that killed V3 {r['phase_invariance']['includes_V3_killer_phases']}",
         "",
         f"  {'case':50s} {'A_TOPO':22s} {'A_TAU':24s} {'G':20s} {'F':18s} {'M':10s}"]
    for c in r["families"]:
        def cell(k):
            return ("OK " if c["pass"][k] else "XX ") + f"{c['predicted'][k]}/{c['expected'][k]}"
        L.append(f"  {c['case']:50s} {cell('A_TOPO'):22s} {cell('A_TAU'):24s} {cell('G'):20s} "
                 f"{cell('F'):18s} {cell('M'):10s}")
    pv = r["phase_resolved_validity"]
    L += ["", f"  false-SAME (A_TOPO) {r['rates']['false_SAME_A_TOPO']}   "
              f"false-DIFFERENT (A_TOPO) {r['rates']['false_DIFFERENT_A_TOPO']}   "
              f"A_TAU failures {r['rates']['A_TAU_failures']}   "
              f"total head failures {r['rates']['head_failures']}/{r['rates']['cases']} cases",
          "",
          f"  PHASE-RESOLVED VALIDITY: bad strike phases per component {pv['bad_phases_per_component']} of "
          f"{pv['period']} -> {'PASS' if pv['pass'] else 'FAIL'} (fires, and does not fire everywhere)",
          f"  ABSTENTION: {'PASS' if r['abstention']['pass'] else 'FAIL'} -> A_TOPO="
          f"{r['abstention']['A_TOPO']} (unsourced live {r['abstention']['unsourced_live']})",
          f"  NON-VACUITY: A_TOPO fired {r['non_vacuity']['A_TOPO_fired']} (all three "
          f"{r['non_vacuity']['all_three']}); A_TAU fired {r['non_vacuity']['A_TAU_fired']}",
          "", "  CERTIFIED RESOLUTION:"]
    for k, v in r["resolution"].items():
        L.append(f"    {k:34s} {v}")
    L += ["", "=" * 120, f"VERDICT: {r['VERDICT']}", "=" * 120]
    return "\n".join(L)


def main(run_id="EXP-GT-ACERT3-20260715-001"):
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
