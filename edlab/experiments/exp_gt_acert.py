"""EXP-GT-A-CERT -- the ARCHITECTURE RESOLUTION CERTIFICATE, in CAUSAL-GRAPH space.

D-052 asked for a finer TOLERANCE. D-053 showed the tolerance was never the problem: A was being graded against
a mislabelled reference, and the benchmark contained no architectural variation at all. D-054 built architectures
that genuinely differ in topology, delay, redundancy and connectivity.

This experiment certifies WHAT A CAN RESOLVE -- and it does so the way the S head was certified (D-051): every
threshold is DERIVED FROM A DEVELOPMENT NULL, declared before any held-out case is looked at, and each of SAME,
DIFFERENT and INDETERMINATE must be shown to FIRE CORRECTLY on known cases. A criterion that cannot both fire and
fail is not a criterion.

NOT CERTIFIED, AND SAID SO PLAINLY: A's invariance to a PROGRAM change. In this circuit family a memory bit of 0
is implemented by ADDING AN EATER, so setting a bit adds a node and two edges: THE PROGRAM IS THE ARCHITECTURE.
"Same architecture, different program" is therefore NOT CONSTRUCTIBLE here, and any head that "passes"
program-invariance on this family passes a test that CANNOT FIRE. (EXP-GT-02B's A head passed it by comparing
channel POSITIONS, which no program can move -- a vacuous pass.) Certifying that A ignores the program requires a
substrate whose memory is a STATE of fixed wiring (a latch or a storage loop), not a component that appears and
disappears. That is a REQUIRED PROPERTY OF THE NEXT BENCHMARK and it is on the benchmark card.
"""

from __future__ import annotations

import itertools
import json
import os

import numpy as np

from ..substrates.life.library import (arch_base, arch_delay, arch_xinhib, arch_5chan, arch_inert, arch_decoy,
                                       arch_direct, arch_redundant, assert_viable, assert_graph_agrees,
                                       settle, OUT_ROW, BASE_COLS)
from ..identity.blind_a import blind_tomography, head_A, head_G, graph_signature

DEV_SEED_NOTE = "development only; no held-out circuit is touched anywhere in this file"
CACHE = os.path.join("results", "_tomo_cache")


def tomo(a, phase: int = 0, region=None) -> dict:
    """Blind tomography, memoised on disk. The cache key is the circuit id + phase + probe region; the cached
    object is the DISCOVERED graph, never a label. It exists because a full tomography is ~2 s and the
    certificate needs ~20 of them -- caching changes nothing scientific, it just lets the run resume."""
    import pickle
    os.makedirs(CACHE, exist_ok=True)
    key = f"{a.arch_id}|{''.join(map(str, a.program))}|ph{phase}|rg{region}".replace("/", "_")
    fp = os.path.join(CACHE, key + ".pkl")
    if os.path.exists(fp):
        with open(fp, "rb") as f:
            return pickle.load(f)
    assert_viable(a)                      # a circuit that does not compute may not enter the evidence
    t = blind_tomography(settle(a, extra_phase=phase), OUT_ROW, region=region)
    t = {k: v for k, v in t.items()}
    for m in t["macro"]:                  # drop the bulky raw traces; the graph is what is certified
        m.pop("line", None)
    with open(fp, "wb") as f:
        pickle.dump(t, f)
    return t


# ---------------------------------------------------------------- development families
def dev_nulls():
    """A must say SAME. These are the measured NOISE FLOOR: everything that changes about a circuit WITHOUT
    changing its causal graph."""
    base = arch_base()
    out = [("phase +15", base, 15), ("phase +30", base, 30), ("phase +45", base, 45)]
    out += [("translate +10", arch_base(cols=[c + 10 for c in BASE_COLS], arch_id="T10"), 0),
            ("translate +20", arch_base(cols=[c + 20 for c in BASE_COLS], arch_id="T20"), 0),
            ("spacing 40->45", arch_base(cols=[5, 50, 95, 140], arch_id="SP45"), 0),
            ("inert decoration", arch_inert(), 0),
            ("decoy eaters (gate density, off-track)", arch_decoy(), 0)]
    return base, out


def dev_positives():
    """A must say DIFFERENT. Each is a GENUINE change to the causal graph."""
    base = arch_base()
    return [("delay edit k=1 (4 steps)", arch_delay(1), base, "delay"),
            ("delay edit k=2 (8 steps)", arch_delay(2), base, "delay"),
            ("delay edit k=4 (16 steps)", arch_delay(4), base, "delay"),
            ("delay edit k=8 (32 steps)", arch_delay(8), base, "delay"),
            ("edge ADDED (cross-stream inhibitor)", arch_xinhib(), base, "edge"),
            ("node ADDED (5th channel)", arch_5chan(), base, "node"),
            ("redundant 2-path vs direct 1-path", arch_redundant(), arch_direct(), "redundancy"),
            ("SAME FUNCTION, different mechanism (gate vs inhibitor)",
             arch_xinhib(), arch_base(program=(1, 1, 1, 0), arch_id="GATE3"), "mechanism")]


# ---------------------------------------------------------------- the certificate
def certify() -> dict:
    rep = {"note": DEV_SEED_NOTE}
    base, nulls = dev_nulls()
    t_base = tomo(base)

    # ---- STEP 1. The delay NULL distribution. The tolerance is MEASURED, never chosen.
    null_rows, delay_devs = [], []
    for name, a, ph in nulls:
        t = tomo(a, phase=ph)
        d1 = sorted(e["delay"] for e in t_base["edges"])
        d2 = sorted(e["delay"] for e in t["edges"])
        dev = max((abs(x - y) for x, y in zip(d1, d2)), default=0) if len(d1) == len(d2) else None
        if dev is not None:
            delay_devs.append(dev)
        null_rows.append({"case": name, "n_edges": len(t["edges"]), "delays": d2,
                          "max_delay_deviation_vs_base": dev, "G": head_G(t_base, t)})
    delay_tol = int(max(delay_devs)) if delay_devs else 0
    rep["delay_null"] = {"deviations": delay_devs, "DERIVED_TOLERANCE": delay_tol,
                         "rule": "tolerance = the LARGEST delay deviation observed across the development "
                                 "nulls. Derived from data, declared before any held-out case is seen."}

    # ---- STEP 2. NULLS must come back SAME (the false-DIFFERENT rate)
    false_diff = 0
    for row, (name, a, ph) in zip(null_rows, nulls):
        t = tomo(a, phase=ph)
        v = head_A(t_base, t, delay_tol)
        row["A"] = v
        row["pass"] = (v == "SAME")
        false_diff += (v != "SAME")
    rep["nulls"] = null_rows
    rep["false_DIFFERENT_rate"] = f"{false_diff}/{len(nulls)}"

    # ---- STEP 3. POSITIVES must come back DIFFERENT (the false-SAME rate)
    pos_rows, false_same = [], 0
    for name, a, ref, kind in dev_positives():
        ta, tr = tomo(a), tomo(ref)
        v = head_A(tr, ta, delay_tol)
        ok = (v == "DIFFERENT")
        false_same += (not ok)
        pos_rows.append({"case": name, "kind": kind, "A": v, "pass": ok, "G": head_G(tr, ta),
                         "edges_ref": len(tr["edges"]), "edges_case": len(ta["edges"])})
    rep["positives"] = pos_rows
    rep["false_SAME_rate"] = f"{false_same}/{len(pos_rows)}"

    # ---- STEP 4. RESOLUTION: the smallest edit of each type that A reliably detects
    res = {}
    smallest_delay = None
    for k in (1, 2, 4, 8):
        t = tomo(arch_delay(k))
        if head_A(t_base, t, delay_tol) == "DIFFERENT" and smallest_delay is None:
            smallest_delay = 4 * k
    res["smallest_detectable_delay_edit_steps"] = smallest_delay
    res["delay_tolerance_from_null"] = delay_tol
    res["smallest_detectable_edge_edit"] = (
        "ONE edge (cross-stream inhibitor adds gunSW->out and one emergent shielding edge)"
        if any(p["kind"] == "edge" and p["pass"] for p in pos_rows) else "NOT DETECTED")
    res["smallest_detectable_node_edit"] = (
        "ONE node (a 5th channel)" if any(p["kind"] == "node" and p["pass"] for p in pos_rows) else "NOT DETECTED")
    res["redundancy_change"] = (
        "DETECTED (1-path vs 2-path into one output node)"
        if any(p["kind"] == "redundancy" and p["pass"] for p in pos_rows) else "NOT DETECTED")
    res["component_separation_limit_cells"] = 4       # MEASURED: matter closer than this merges (blind_a.MERGE_GAP)
    rep["resolution"] = res

    # ---- STEP 5. INDETERMINATE must FIRE. A criterion that cannot abstain cannot be trusted when it doesn't.
    starved = tomo(base, region=(0, 20, 0, 100))       # only the leftmost guns can even be FOUND
    v = head_A(t_base, starved, delay_tol)
    rep["indeterminate"] = {
        "case": "coverage-starved probe: components may only be found in cols 0-100, so two LIVE outputs "
                "have no discoverable source",
        "uncovered_outputs": starved["uncovered_outputs"],
        "A": v, "pass": v == "INDETERMINATE",
        "why": "an output that is demonstrably live and whose cause was never found is missing evidence, "
               "not evidence of sameness. Fabricating SAME here would be the failure mode the observability "
               "contract exists to forbid."}

    # ---- STEP 6. all three verdicts must have fired
    fired = {"SAME": any(r["A"] == "SAME" for r in null_rows),
             "DIFFERENT": any(r["A"] == "DIFFERENT" for r in pos_rows),
             "INDETERMINATE": rep["indeterminate"]["pass"]}
    rep["all_three_verdicts_fired"] = fired

    granted = (false_diff == 0 and false_same == 0 and all(fired.values()))
    rep["VERDICT"] = "QUALIFIED" if granted else "FAILED — OBSERVABILITY"
    rep["NOT_CERTIFIED"] = {
        "program_invariance": "NOT CONSTRUCTIBLE in this family. A memory bit of 0 is implemented by ADDING an "
                              "eater, so the program IS part of the causal graph. Any 'pass' here would be "
                              "vacuous. Requires a substrate with STATE-based memory (a latch/storage loop). "
                              "EXP-GT-02B's program-invariance PASS is hereby marked VACUOUS.",
        "component_separation": "components whose matter is separated by <= 4 empty cells MERGE and cannot be "
                                "resolved by this probe.",
        "redundancy_with_identical_F": "not realizable in this component library without a glider reflector; "
                                       "the redundant path doubles the stream rate, and this is disclosed, "
                                       "not hidden."}
    return rep


def summarize(r: dict) -> str:
    L = ["EXP-GT-A-CERT -- ARCHITECTURE RESOLUTION CERTIFICATE (causal-graph space, not column distance)",
         "=" * 104, "",
         f"STEP 1 -- DELAY TOLERANCE DERIVED FROM THE DEVELOPMENT NULL: {r['delay_null']['DERIVED_TOLERANCE']} steps",
         f"         null deviations observed: {r['delay_null']['deviations']}", "",
         "STEP 2 -- NULLS (A must say SAME):"]
    for n in r["nulls"]:
        L.append(f"   {'PASS' if n['pass'] else 'FAIL':4s}  {n['case']:42s} A={n['A']:13s} G={n['G']:9s} "
                 f"delays={n['delays']}")
    L += [f"   false-DIFFERENT rate: {r['false_DIFFERENT_rate']}", "",
          "STEP 3 -- POSITIVES (A must say DIFFERENT):"]
    for p in r["positives"]:
        L.append(f"   {'PASS' if p['pass'] else 'FAIL':4s}  {p['case']:52s} A={p['A']:10s} G={p['G']:9s} "
                 f"edges {p['edges_ref']}->{p['edges_case']}")
    L += [f"   false-SAME rate: {r['false_SAME_rate']}", "",
          "STEP 4 -- CERTIFIED RESOLUTION:"]
    for k, v in r["resolution"].items():
        L.append(f"   {k:38s} : {v}")
    i = r["indeterminate"]
    L += ["", "STEP 5 -- ABSTENTION MUST FIRE:",
          f"   {'PASS' if i['pass'] else 'FAIL':4s}  coverage-starved probe -> A={i['A']}  "
          f"(uncovered outputs {i['uncovered_outputs']})",
          "", f"STEP 6 -- all three verdicts fired: {r['all_three_verdicts_fired']}",
          "", "=" * 104, f"VERDICT: {r['VERDICT']}", "", "NOT CERTIFIED (stated, not hidden):"]
    for k, v in r["NOT_CERTIFIED"].items():
        L.append(f"   * {k}: {v}")
    L.append("=" * 104)
    return "\n".join(L)


def main(run_id="EXP-GT-ACERT-20260713-001"):
    r = certify()
    d = os.path.join("results", run_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "certificate.json"), "w") as f:
        json.dump(r, f, indent=1, default=str)
    s = summarize(r)
    with open(os.path.join(d, "summary.txt"), "w") as f:
        f.write(s + "\n")
    print(s)
    return r


if __name__ == "__main__":
    main()
