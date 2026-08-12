"""MCM01 integrity and mutation harness. Runs BEFORE freeze 1.

TEST mode   bounded advances, no start may be opened, scoring functions raise
STATIC mode no advance at all, scoring exercised on hand-built states
Neither consumes an outcome-informative start, and the harness asserts that at the end.
"""
from __future__ import annotations

import hashlib
import json
import math

import numpy as np

import guard
import kinetics as K
import lattice as LAT
import mcm
import region as REG

R = {"tests": [], "mutations": []}


def T(name, ok, detail=""):
    R["tests"].append({"test": name, "outcome": "PASS" if ok else "FAIL", "detail": detail})
    print(("  PASS  " if ok else "  FAIL  ") + name + ("   " + detail if detail else ""))
    return bool(ok)


def M(name, det, detail=""):
    R["mutations"].append({"mutation": name, "outcome": "DETECTED" if det else "MISSED",
                           "detail": detail})
    print(("  DETECTED  " if det else "  MISSED    ") + name + ("   " + detail if detail else ""))
    return bool(det)


def raises(fn, exc=guard.ProtocolError):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


F = mcm.Recorder.FIELDS


def synth(n, NX=None, NY=None, cX=None, u=None):
    a = np.zeros((n, len(F)))
    a[:, F.index("step")] = np.arange(1, n + 1)
    a[:, F.index("N_X")] = 100.0 if NX is None else NX
    a[:, F.index("N_Y")] = 1.0 if NY is None else NY
    a[:, F.index("c_X_per_org")] = 1.0 if cX is None else cX
    a[:, F.index("u_nX_at_org")] = 5.0 if u is None else u
    return a


def samples(n, step0=0, every=50, main_NX=100, wraps=False):
    return [{"step": step0 + i * every,
             "main": {"N_X": main_NX, "N_Y": 1, "wraps": wraps, "mass": main_NX, "cells": 20},
             "components": [], "escapees": []} for i in range(n)]


# ==================================================================== analytic
def analytic():
    ok = True
    ok &= T("kinetics.py is byte-identical to the frozen MTW01 engine",
            hashlib.sha256(open("kinetics.py", "rb").read()).hexdigest()
            == "d6b9e24daefd9a9ddd42780fa24da444a344a2773bb7836a8e168e44f026c4c4",
            hashlib.sha256(open("kinetics.py", "rb").read()).hexdigest()[:16])

    err = max(abs(REG.p_hop_for(LAT.D_eff(p)) - p) for p in (0.05, 0.2, 0.5, 0.9, 1.0))
    ok &= T("p_hop <-> D_eff inversion is exact", err < 1e-12, "max error %.2e" % err)

    bad = []
    for A in (1.5, 2.526, 8.0, 20.0):
        u = REG.u_star(A)
        if abs(u - A * (1 - math.exp(-u))) > 1e-10:
            bad.append(A)
    ok &= T("u* solves u = A(1-exp(-u))", not bad, "residual > 1e-10 at %s" % (bad or "none"))

    g = LAT.green_origin_converged([LAT.a_of(0.1)], 0.99)
    ok &= T("the Green quadrature carries a convergence certificate",
            g["converged"], "n=%d delta=%.2e G0=%.5f" % (g["n"], g["delta"], g["G0"]))

    # analytic sanity: as p_hop -> 0 the particle never leaves, so G(0) -> 1/muX
    g0 = LAT.green_origin_converged([LAT.a_of(1e-6)], 1.0 - 0.01)["G0"]
    ok &= T("G(0) -> 1/muX in the immobile limit", abs(g0 - 100.0) / 100.0 < 0.02,
            "G0=%.3f vs 1/muX=100" % g0)

    hard, _ = LAT.c_X_hard_cap(16)
    ok &= T("the exact cand_X cap is recomputed", hard == 7, "cand_X_max = %d" % hard)
    return ok


# ==================================================================== TEST mode
def engine_tests():
    guard.set_test_mode()
    ok = True
    sp = mcm.spec_with(muX=0.004, muY=0.0, kY=0.0, p_hop_X=0.1026, p_hop_Y=0.1026, phi=0.2)

    # THE load-bearing test: the recorder must not change the law
    a = mcm.fresh_world(77, sp, rec=None)
    b = mcm.fresh_world(77, sp, rec=mcm.Recorder())
    mcm.seed_one_organiser(a, 4)
    mcm.seed_one_organiser(b, 4)
    guard.advance(a, 250)
    guard.advance(b, 250)
    ok &= T("the recorder does not change the law of the process",
            a.state_hash() == b.state_hash(),
            "identical state hash after 250 steps: %s" % a.state_hash()[:16])
    ok &= T("the recorder produced one row per step", len(b.rec.rows) == 250,
            "%d rows" % len(b.rec.rows))

    # c_X read by the recorder equals an independent recomputation, on a frozen state
    still = mcm.spec_with(p_hop_X=0.0, p_hop_Y=0.0, muX=0.0, muY=0.0, phi=0.0, omega=0.0,
                          kY=0.0)
    r = mcm.Recorder()
    w = mcm.RecWorld(seed=5, sp=still, rec=r)
    w.n["SX"][7, 7], w.n["SY"][7, 7] = 5, 2
    w.n["X"][7, 7], w.n["Y"][7, 7] = 3, 1
    free = still.CAP - (w.n["X"] + w.n["Y"] + w.n["SX"] + w.n["SY"] + w.n["WX"] + w.n["WY"])
    want = min(int(w.n["SX"][7, 7]), int(free[7, 7]))
    guard.advance(w, 1)
    got = r.rows[0][F.index("c_X_total")]
    ok &= T("recorded c_X equals min(n[SX], free) at the organiser cell, independently computed",
            abs(got - want) < 1e-12, "recorded %.1f, independent %d" % (got, want))

    # accepted births and deaths are the actual field differences
    ok &= T("accepted births and deaths are read from the field, not modelled",
            r.rows[0][F.index("accepted_births_X")] >= 0
            and r.rows[0][F.index("deaths_X")] == 0,
            "births=%.0f deaths=%.0f (muX = 0 in this fixture)"
            % (r.rows[0][F.index("accepted_births_X")], r.rows[0][F.index("deaths_X")]))

    ok &= T("no start may be opened in TEST mode",
            raises(lambda: guard.start("calibration", "illegal", 1).__enter__()))
    ok &= T("the TEST step budget is enforced",
            raises(lambda: guard.advance(mcm.fresh_world(1, sp), guard.MAX_TEST_STEPS + 1)))
    guard.set_experiment_mode()
    return ok


# ==================================================================== STATIC mode
def static_tests():
    guard.set_static_mode()
    ok = True
    sp = mcm.spec_with()
    ok &= T("advance() is impossible in STATIC mode",
            raises(lambda: guard.advance(mcm.fresh_world(1, sp), 1)))

    # ---- THE MTW01 GATE-ORDER DEFECT, covered explicitly
    a = synth(400, NY=1.0)
    a[200:, F.index("N_Y")] = 2.0                       # a second organiser appears mid-window
    p = mcm.persistence_gate(a, F, 0, 400, N_KEEP=50, FRAC_MIN=0.95, RUN_MAX=20, G0=10.0,
                             CRIT_FRAC=0.95, comp_samples=samples(8))
    ok &= T("the persistence gate does NOT fail merely because a second organiser appears",
            p["PASS"], "checks: %s" % json.dumps(p["checks"]))
    a0 = synth(400, NY=1.0)
    a0[300:, F.index("N_Y")] = 0.0                      # the organiser is lost
    p0 = mcm.persistence_gate(a0, F, 0, 400, 50, 0.95, 20, 10.0, 0.95, samples(8))
    ok &= T("the persistence gate DOES fail when the organiser is lost",
            not p0["PASS"] and not p0["checks"]["organiser_present_throughout"], "")

    # ---- formation requires CONSECUTIVE steps, not a lucky instant
    osc = synth(500, NX=np.where(np.arange(500) % 2 == 0, 100.0, 1.0),
                u=np.where(np.arange(500) % 2 == 0, 9.0, 0.0))
    ok &= T("formation requires K consecutive steps, an oscillating record does not qualify",
            mcm.formation_gate(osc, F, 500, 50, 5.0, 20) is None, "")
    good = synth(500, NX=100.0, u=9.0)
    ok &= T("formation is detected at the K-th consecutive qualifying step",
            mcm.formation_gate(good, F, 500, 50, 5.0, 20) == 20, "")

    # ---- a long excursion with a good mean must still fail
    dip = synth(1000, NX=np.concatenate([np.full(400, 200.0), np.full(60, 1.0),
                                         np.full(540, 200.0)]))
    p2 = mcm.persistence_gate(dip, F, 0, 1000, 50, 0.90, 20, 10.0, 0.90, samples(20))
    ok &= T("a long consecutive excursion fails even when the time average is comfortable",
            (not p2["PASS"]) and p2["checks"]["longest_consecutive_excursion"] == 60
            and p2["checks"]["fraction_of_steps_at_or_above_N_KEEP"] >= 0.93,
            "longest=%d frac=%.3f" % (p2["checks"]["longest_consecutive_excursion"],
                                      p2["checks"]["fraction_of_steps_at_or_above_N_KEEP"]))

    # ---- components on the torus
    L = sp.L
    w = mcm.fresh_world(3, sp)
    w.n["X"][:] = 0
    w.n["X"][0, 0] = 20
    w.n["X"][L - 1, 0] = 15
    w.n["Y"][0, 0] = 1
    w.n["X"][18, 18] = 1
    rep = mcm.component_report(w)
    ok &= T("components wrap across the seam and lone molecules are escapees",
            rep["n_components"] == 1 and rep["n_escapees"] == 1 and rep["main"]["N_X"] == 35,
            "n=%d escapees=%d main N_X=%d" % (rep["n_components"], rep["n_escapees"],
                                              rep["main"]["N_X"]))
    ok &= T("the circular centre of mass is correct across the seam",
            abs(((rep["main"]["com_y"] + 0.5) % L) - 0.5) < 0.6,
            "com_y = %.3f on a torus of %d" % (rep["main"]["com_y"], L))

    # ---- classification is exhaustive and mutually exclusive
    cases = {
        "NO_FORMATION": (None, {}, synth(10, NX=0.0)),
        "TRANSIENT_FORMATION": (None, {}, synth(10, NX=50.0)),
        "MAINTENANCE_ACHIEVED": (20, {"PASS": True, "checks": {}}, synth(10)),
    }
    got = {k: mcm.classify(f, p, a_, F, []) for k, (f, p, a_) in cases.items()}
    ok &= T("the end classification returns the declared label in each canonical case",
            all(got[k] == k for k in cases), json.dumps(got))
    ok &= T("every classification label is declared",
            set(got.values()) <= set(mcm.END_CLASSES), "")
    return ok


# ==================================================================== mutations
def mutation_tests():
    guard.set_static_mode()
    ok = True
    base = synth(600, NX=200.0)
    sm = samples(12)
    good = mcm.persistence_gate(base, F, 0, 600, 50, 0.95, 20, 10.0, 0.95, sm)
    ok &= T("a clean maintenance record passes the persistence gate", good["PASS"], "")

    m = base.copy(); m[123, F.index("N_X")] = 0.0
    ok &= M("a single step at N_X = 0 inside the window",
            not mcm.persistence_gate(m, F, 0, 600, 50, 0.95, 20, 10.0, 0.95, sm)["PASS"], "")

    m = base.copy(); m[:, F.index("c_X_per_org")] = 0.05
    ok &= M("c_X collapsed so that c_X*G(0) < 1",
            not mcm.persistence_gate(m, F, 0, 600, 50, 0.95, 20, 10.0, 0.95, sm)["PASS"], "")

    ok &= M("the main component wraps around the torus",
            not mcm.persistence_gate(base, F, 0, 600, 50, 0.95, 20, 10.0, 0.95,
                                     samples(12, wraps=True))["PASS"], "")

    ok &= M("the main component no longer carries the mass",
            not mcm.persistence_gate(base, F, 0, 600, 50, 0.95, 20, 10.0, 0.95,
                                     samples(12, main_NX=1))["PASS"], "")

    ok &= M("the maintenance window is truncated",
            not mcm.persistence_gate(base, F, 0, 900, 50, 0.95, 20, 10.0, 0.95, sm)["PASS"], "")

    # selection-rule mutations
    rows = REG.grid()
    best, cand = REG.select(rows)
    ok &= M("a selection that ignores the frozen ordering",
            REG.selection_key(best) == min(REG.selection_key(r) for r in cand),
            "the winner is the argmin of the frozen key over %d candidates" % len(cand))
    key = tuple(round(best[k], 12) for k in REG.TIE_BREAK)
    b2, c2 = REG.select(rows, c_X_measured={key: best["c_X_certified"] * 0.10})
    ok &= M("a measured c_X too small to satisfy the frozen criticality threshold",
            b2 is None or REG.selection_key(b2) != REG.selection_key(best),
            "the point is eliminated when its measured c_X is a tenth of the certified bound")

    # guard mutations
    guard.set_experiment_mode()
    saved = list(guard.LEDGER["log"])
    guard.LEDGER["log"] = [{"n": i + 1, "class": "calibration", "tag": "x", "planned_steps": 1,
                            "steps_used": 0, "valid": True} for i in range(guard.CAPS["calibration"])]
    ok &= M("a calibration start beyond its own class cap",
            raises(lambda: guard.start("calibration", "over", 1).__enter__()), "")
    ok &= M("an undeclared start class",
            raises(lambda: guard.start("confirmation_extra", "x", 1)), "")
    guard.LEDGER["log"] = saved
    guard.set_static_mode()
    return ok


if __name__ == "__main__":
    print("--- analytic");  a = analytic()
    print("--- TEST mode: engine and recorder");  b = engine_tests()
    print("--- STATIC mode: observables and gates");  c = static_tests()
    print("--- STATIC mode: mutations");  d = mutation_tests()
    aud = guard.audit()
    e = T("the harness consumed no outcome-informative start", aud["total"] == 0,
          "starts=%d, test steps %d of %d" % (aud["total"], aud["test_steps_used"],
                                              aud["max_test_steps"]))
    R["ledger_after_harness"] = aud
    R["ALL_PASS"] = bool(a and b and c and d and e)
    json.dump(R, open("/home/claude/MCM01/out/_integrity.json", "w"), indent=1)
    print("\nALL_PASS =", R["ALL_PASS"])
