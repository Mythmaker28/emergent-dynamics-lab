"""EXP-GT-FINGERPRINT-00 -- THE SINGLE PROSPECTIVE RUN. Frozen; hashed; run once; no repair.

The probe battery, fingerprint construction, normalization, response windows, matching statistic, radii, abstention
rules, equivalence-class rules and both access definitions were FROZEN and hashed BEFORE this split existed
(docs/FINGERPRINT_FREEZE_MANIFEST.json).

JOINTLY HELD OUT: implementation, topology, layout, phase, redundant-lag structure, replacement mechanism,
context schedule.

DECLARED LIMITATION OF THIS SPLIT, stated before the run and not hidden afterwards: seven of the ten systems use
implementations never fingerprinted (and_or, xnor_and, direct_buf, or3, edge_xor, tri_tap, dup_lag). The two
STATE systems (P_STATE = fsm_gate, P_LATCH = reg_delay) reuse DEVELOPMENT implementations, because the substrate
contains no state machine that development did not use, and I will not add one to the world generator AFTER the
instrument was frozen. Their topology, layout, phase and pairing are new; their implementation is not. The
hidden-state result therefore tests the battery's generalization, NOT its generalization to an unseen state
machine, and it may not be quoted as the latter.

Both arms are scored. THE LIMITED ARM MUST QUALIFY ON ITS OWN: a rich-access pass cannot authorize transfer after
a limited-access failure.
"""

from __future__ import annotations

import json
import os
import pickle

import numpy as np

from ..substrates.boolnet.circuits import build
from ..substrates.boolnet.evaluator import assert_qualified
from ..substrates.boolnet.fpworld import FPWorld, probe_cells, swapped_trajectory
from ..identity.fingerprint import acquire, canonical, distance, compare

RADII = {"rich": {"r_c": 0.0075, "r_s": 0.0226}, "droplet": {"r_c": 0.015, "r_s": 0.0451}}
_DISK = ".cache_fp_p"
RESULTS = "docs/EXP_GT_FP_P_RAW.json"

# systems built from implementations, topologies, phases and layouts NEVER used in fingerprint development
P = {
    # the AND equivalence class, on a NEW topology/phase, through implementations never fingerprinted
    "P_AND_a":   dict(impl="and_or", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    "P_AND_b":   dict(impl="xnor_and", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    "P_AND_c":   dict(impl="direct_buf", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    "P_AND_lay": dict(impl="and_or", program=(1, 1, 1), chan_cols=(9, 25, 39), clk_phase=6, extra_delay=2),
    # a different reachable function, same topology
    "P_OR":      dict(impl="or3", program=(0, 0, 0), chan_cols=(7, 22, 37), clk_phase=3),
    "P_XOR":     dict(impl="edge_xor", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    # genuine hidden state, on the new topology -- and a LATCH that is not a state machine
    "P_STATE":   dict(impl="fsm_gate", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    "P_LATCH":   dict(impl="reg_delay", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    # a redundant-lag structure never fingerprinted, and its clean twin
    "P_TRI":     dict(impl="tri_tap", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
    "P_DUPLAG":  dict(impl="dup_lag", program=(1, 1, 1), chan_cols=(7, 22, 37), clk_phase=3),
}

# EXPECTATIONS, DECLARED BEFORE THE RUN. Ground truth is the machines' reachable behaviour, not their labels.
CONT = [("P_AND_a", "P_AND_b", "two unseen AND implementations (and_or vs xnor_and)"),
        ("P_AND_a", "P_AND_c", "unseen AND vs a buffered AND"),
        ("P_AND_a", "P_AND_lay", "unseen AND: DIFFERENT layout, phase and detour")]
DIFF = [("P_AND_a", "P_XOR", "different reachable truth table"),
        ("P_AND_a", "P_STATE", "combinational vs genuine hidden state"),
        ("P_LATCH", "P_STATE", "a LATCH is not a state machine"),
        ("P_AND_a", "P_TRI", "different reachable function (three-lag AND)"),
        ("P_AND_a", "P_DUPLAG", "different reachable function (two-lag AND)")]
# distinguishable under RICH access; the droplet repertoire cannot reach the cause
COLL = [("P_AND_a", "P_OR", "OR(clk,0) = AND(clk,1). No droplet probe can step the register.")]


def machine(sid):
    kw = dict(P[sid])
    m = build(**{k: (list(v) if k == "chan_cols" else v) for k, v in kw.items()})
    assert_qualified(m)
    return m


def fp(sid, arm):
    os.makedirs(_DISK, exist_ok=True)
    f = os.path.join(_DISK, f"{sid}_{arm}.pkl")
    if os.path.exists(f):
        return pickle.load(open(f, "rb"))
    m = machine(sid)
    w = FPWorld(m.net, m.out_cells)
    acq = acquire(w, sid, probe_cells(m, 0, arm), m.out_cells[0], arm)
    pickle.dump(acq, open(f, "wb"))
    return acq


def run():
    res = {}
    for arm in ("rich", "droplet"):
        r_c, r_s = RADII[arm]["r_c"], RADII[arm]["r_s"]
        F = {sid: canonical(fp(sid, arm)) for sid in P}
        rows = []
        for kind, pairs in (("CONTINUITY", CONT), ("DIFFERENCE", DIFF), ("COLLISION", COLL)):
            for a, b, note in pairs:
                v = compare(F[a], F[b], r_c, r_s)
                exp = ("INDISTINGUISHABLE_UNDER_REPERTOIRE" if kind == "CONTINUITY" else
                       "DIFFERENT" if kind == "DIFFERENCE" else
                       ("DIFFERENT" if arm == "rich" else "INDISTINGUISHABLE_UNDER_REPERTOIRE"))
                rows.append({"arm": arm, "kind": kind, "a": a, "b": b, "note": note,
                             "distance": round(v["distance"], 4), "verdict": v["verdict"],
                             "expected": exp, "ok": v["verdict"] == exp,
                             "coverage": round(v["coverage"], 3)})
        res[arm] = {"rows": rows,
                    "responsive": {sid: round(F[sid]["responsive"], 3) for sid in P}}

    # E1: function-preserving replacement DURING one continuous trajectory, on an UNSEEN pair
    ma, mb = machine("P_AND_a"), machine("P_AND_b")
    sw = swapped_trajectory(ma, mb, t_swap=40, steps=160)
    for arm in ("rich", "droplet"):
        d = distance(canonical(fp("P_AND_a", arm)), canonical(fp("P_AND_b", arm)))
        res[arm]["e1"] = {"pre_post_distance": round(d, 4),
                          "within_continuity": d <= RADII[arm]["r_c"]}
    res["e1_trajectory"] = {"identical_before_swap": bool(sw["identical_before_swap"]),
                            "transient_steps": int(sw["transient_steps"]),
                            "uninterrupted_after": int(sw["uninterrupted_after"])}
    return res


def report(res):
    print("EXP-GT-FINGERPRINT-00 -- SINGLE PROSPECTIVE RUN (frozen battery, fresh systems, run once)")
    print("=" * 108)
    for arm in ("rich", "droplet"):
        rows = res[arm]["rows"]
        n_ok = sum(r["ok"] for r in rows)
        fd = [r for r in rows if r["kind"] == "CONTINUITY" and r["verdict"] == "DIFFERENT"]
        fs = [r for r in rows if r["kind"] == "DIFFERENCE"
              and r["verdict"] == "INDISTINGUISHABLE_UNDER_REPERTOIRE"]
        ind = [r for r in rows if r["verdict"] == "INDETERMINATE"]
        print(f"\n{arm.upper()} ARM   (radii r_c={RADII[arm]['r_c']}, r_s={RADII[arm]['r_s']})")
        print(f"  cases correct                      {n_ok}/{len(rows)}")
        print(f"  FALSE DIFFERENCE (equivalent -> DIFFERENT)      {len(fd)}    <-- must be 0")
        print(f"  FALSE SAMENESS   (different -> INDISTINGUISHABLE) {len(fs)}    <-- must be 0")
        print(f"  INDETERMINATE                      {len(ind)}")
        print(f"  E1 replacement: pre/post fingerprint distance {res[arm]['e1']['pre_post_distance']} "
              f"-> within continuity radius = {res[arm]['e1']['within_continuity']}")
        for r in rows:
            flag = "" if r["ok"] else "   <<<"
            print(f"    [{'ok ' if r['ok'] else 'BAD'}] {r['kind']:10s} {r['a']:9s} vs {r['b']:9s} "
                  f"d={r['distance']:.4f} -> {r['verdict']:34s} (expected {r['expected']}){flag}")
    t = res["e1_trajectory"]
    print(f"\nE1 CONTINUOUS TRAJECTORY: identical before the swap = {t['identical_before_swap']}; "
          f"bounded transient {t['transient_steps']} steps; uninterrupted from t={t['uninterrupted_after']}")

    ok_rich = all(r["ok"] for r in res["rich"]["rows"])
    ok_drop = all(r["ok"] for r in res["droplet"]["rows"])
    print("\n" + "=" * 108)
    print(f"  RICH ARM    {'PASS' if ok_rich else 'FAIL'}")
    print(f"  DROPLET ARM {'PASS' if ok_drop else 'FAIL'}    <-- must qualify INDEPENDENTLY")
    return ok_rich, ok_drop


def main():
    if os.path.exists(RESULTS):
        res = json.load(open(RESULTS))
        print("(replaying the recorded single run; the observer is deterministic and is not re-interrogated)\n")
    else:
        res = run()
        json.dump(res, open(RESULTS, "w"), indent=1, default=str)
    report(res)


if __name__ == "__main__":
    main()
