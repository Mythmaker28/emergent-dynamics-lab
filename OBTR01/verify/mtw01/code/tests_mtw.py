"""MTW01 integrity and mutation harness. Runs BEFORE the freeze, so that fixing a failure never
invalidates a freeze; the freeze is then taken over the tested bytes.

Two mechanically separated phases:

  TEST mode   — engine invariants. Bounded advances only; guard.MAX_TEST_STEPS caps the TOTAL
                across the whole harness, and every scoring function raises if called. A
                full-horizon arm here is a RuntimeError. This is the mechanical form of the
                correction recorded in MINCORE_SCOPE_CORRECTION_ADDENDUM section 6.
  STATIC mode — observable, gate and verdict code, exercised on hand-built states. No advance of
                any kind is possible: guard.advance raises.

Neither phase consumes an outcome-informative start, and the harness asserts that at the end.
"""
from __future__ import annotations

import ast
import json
import math

import numpy as np

import guard
import mtw
import observe
from mtw import ALL_OCC, Spec, World, fresh_world, seed_one_organiser, spec_with

RESULTS = {"tests": [], "mutations": [], "ast": []}


def T(name, ok, detail=""):
    RESULTS["tests"].append({"test": name, "outcome": "PASS" if ok else "FAIL",
                             "detail": detail})
    print(("  PASS  " if ok else "  FAIL  ") + name + ("   " + detail if detail else ""))
    return ok


def M(name, detected, detail=""):
    RESULTS["mutations"].append({"mutation": name,
                                 "outcome": "DETECTED" if detected else "MISSED",
                                 "detail": detail})
    print(("  DETECTED  " if detected else "  MISSED    ") + name +
          ("   " + detail if detail else ""))
    return detected


def raises(fn, exc=guard.ProtocolError):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


# ==================================================================== AST checks (no execution)
FORBIDDEN_REDUCTIONS = {"mean", "sum", "max", "min", "argmax", "argmin", "std", "var",
                        "ptp", "cumsum", "prod", "average", "median"}
OPERATORS = ("_diffuse", "_react", "_decay", "_feed_and_outflow", "free", "occ")
# write-only diagnostics: a reduction may write into these, and no rate may ever read them
DIAGNOSTIC_ATTRS = {"removed_waste", "H3_exact", "H3_kk"}


def ast_checks():
    src = open("mtw.py").read()
    tree = ast.parse(src)
    cls = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "World"][0]
    fns = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}

    # 1. no lattice-wide reduction anywhere a rate is computed
    bad = []
    for name in OPERATORS:
        fn = fns[name]
        hazard_ranges = []
        for node in ast.walk(fn):
            if isinstance(node, ast.If) and "hazard_armed" in ast.dump(node.test):
                hazard_ranges.append((node.lineno, node.end_lineno))
        # a reduction is permitted ONLY when its value is written into a declared write-only
        # diagnostic accumulator and never read back by any rate
        diag_ranges = []
        for node in ast.walk(fn):
            if (isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Attribute)
                    and node.target.attr in DIAGNOSTIC_ATTRS):
                diag_ranges.append((node.lineno, node.end_lineno))
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in FORBIDDEN_REDUCTIONS):
                ok_here = (any(a <= node.lineno <= b for a, b in hazard_ranges)
                           or any(a <= node.lineno <= b for a, b in diag_ranges))
                if not ok_here:
                    bad.append("%s:%d:.%s()" % (name, node.lineno, node.func.attr))
    ok1 = T("no lattice-wide reduction enters any rate",
            not bad, "offending tokens: %s" % (bad or "none"))
    RESULTS["ast"].append({"check": "reductions", "offenders": bad})

    # 1b. the diagnostic accumulators are write-only inside every operator
    reads = []
    for name in OPERATORS + ("_one_step",):
        for node in ast.walk(fns[name]):
            if (isinstance(node, ast.Attribute) and node.attr in DIAGNOSTIC_ATTRS
                    and isinstance(node.ctx, ast.Load)):
                reads.append("%s:%d:%s" % (name, node.lineno, node.attr))
    ok1b = T("the diagnostic accumulators are write-only in every operator", not reads,
             "declared write-only: %s ; reads found: %s"
             % (sorted(DIAGNOSTIC_ATTRS), reads or "none"))

    # 2. every .any() is a pure branch guard on a provably null operation
    anys, bad_any = [], []
    for name in OPERATORS:
        for node in ast.walk(fns[name]):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "any"):
                anys.append("%s:%d" % (name, node.lineno))
    for name in OPERATORS:
        for node in ast.walk(fns[name]):
            if isinstance(node, ast.If):
                continue
        # an .any() outside an If test would be an offender
        for node in ast.walk(fns[name]):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.Return)):
                for sub in ast.walk(node):
                    if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                            and sub.func.attr == "any"):
                        bad_any.append("%s:%d" % (name, sub.lineno))
    ok2 = T("every .any() is only a branch guard, never a rate",
            not bad_any, "any() sites: %s ; offenders: %s" % (anys, bad_any or "none"))

    # 3. no clone, child, division or copy operator anywhere in the engine
    forbidden = ("clone", "child", "divide", "division", "split_cell", "duplicate_cell",
                 "make_offspring", "copy_organism")
    defs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    off = [d for d in defs if any(f in d.lower() for f in forbidden)]
    ok3 = T("no clone, child or division operator is defined", not off,
            "definitions: %s ; offenders: %s" % (len(defs), off or "none"))

    # 4. World exposes no public advance: guard.advance is the only path
    ok4 = T("World exposes no public advance()",
            "advance" not in fns and "_one_step" in fns,
            "methods: %s" % sorted(fns))

    # 5. the frozen update order
    body = fns["_one_step"].body
    order = []
    for st in body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
            f = st.value.func
            if isinstance(f, ast.Attribute):
                order.append(f.attr if f.attr != "_diffuse"
                             else "_diffuse(%s)" % ast.literal_eval(st.value.args[0]))
    want = ["_diffuse(X)", "_diffuse(Y)", "_diffuse(SX)", "_diffuse(SY)", "_react", "_decay",
            "_feed_and_outflow"]
    ok5 = T("the frozen update order is unchanged", order == want, "order = %s" % order)
    return all([ok1, ok1b, ok2, ok3, ok4, ok5])


# ==================================================================== TEST mode: engine
def engine_tests():
    guard.set_test_mode()
    ok = True

    a, b = fresh_world(7), fresh_world(7)
    seed_one_organiser(a, 4)
    seed_one_organiser(b, 4)
    guard.advance(a, 60)
    guard.advance(b, 60)
    ok &= T("determinism conditional on the RNG seed", a.state_hash() == b.state_hash(),
            a.state_hash()[:16])

    w = fresh_world(11)
    seed_one_organiser(w, 4)
    mx = [0]
    guard.advance(w, 200, per_step=lambda ww: mx.__setitem__(0, max(mx[0], int(ww.occ().max()))))
    ok &= T("local capacity is never exceeded", mx[0] <= Spec.CAP,
            "max occupancy %d against CAP %d" % (mx[0], Spec.CAP))

    w = fresh_world(3)
    w.n["Y"][10, 10] = 3                                   # organisers, no body molecule
    guard.advance(w, 100)
    ok &= T("the X = 0 axis is invariant", int(w.n["X"].sum()) == 0,
            "N_X=%d N_Y=%d" % (int(w.n["X"].sum()), int(w.n["Y"].sum())))

    w = fresh_world(4)
    w.n["X"][10, 10] = 5                                   # body molecules, no organiser
    guard.advance(w, 100)
    ok &= T("the Y = 0 axis is invariant", int(w.n["Y"].sum()) == 0,
            "N_X=%d N_Y=%d" % (int(w.n["X"].sum()), int(w.n["Y"].sum())))

    w = fresh_world(5)
    guard.advance(w, 100)
    ok &= T("the empty organiser state is exact and absorbing",
            int(w.n["X"].sum()) == 0 and int(w.n["Y"].sum()) == 0,
            "N_X=%d N_Y=%d" % (int(w.n["X"].sum()), int(w.n["Y"].sum())))

    # pure diffusion on a torus conserves every species exactly and wraps
    pure = spec_with(muX=0.0, muY=0.0, kX=0.0, kY=0.0, phi=0.0, omega=0.0, S0=0)
    w = World(seed=9, sp=pure)
    w.n["X"][0, 0] = 12
    guard.advance(w, 100)
    reached = bool(w.n["X"][w.L - 1, :].sum() or w.n["X"][:, w.L - 1].sum())
    ok &= T("diffusion on the torus conserves particles exactly and wraps",
            int(w.n["X"].sum()) == 12 and reached,
            "N_X=%d, mass on the opposite edge: %s" % (int(w.n["X"].sum()), reached))

    # the hazard accumulator, checked against an independent hand computation.
    # p_hop = 0 makes diffusion a no-op, so the reaction sees exactly the hand-built state.
    still = spec_with(p_hop_X=0.0, p_hop_Y=0.0, muX=0.0, muY=0.0, phi=0.0, omega=0.0)
    w = World(seed=13, sp=still)
    w.n["X"][5, 5], w.n["Y"][5, 5], w.n["SY"][5, 5], w.n["SX"][5, 5] = 6, 1, 3, 2
    w.n["X"][9, 9], w.n["Y"][9, 9], w.n["SY"][9, 9] = 4, 2, 3
    free = still.CAP - (w.n["X"] + w.n["Y"] + w.n["SX"] + w.n["SY"] + w.n["WX"] + w.n["WY"])
    expect = 0.0
    for (yy, xx) in ((5, 5), (9, 9)):
        p = min(1.0, still.kY * int(w.n["X"][yy, xx]) * int(w.n["Y"][yy, xx]))
        c = min(int(w.n["SY"][yy, xx]), int(free[yy, xx]))
        expect += c * (-math.log1p(-p))
    w.hazard_armed = True
    guard.advance(w, 1)
    ok &= T("the cumulative hazard H3 equals -sum cand*ln(1-p) exactly",
            abs(w.H3_exact - expect) < 1e-15,
            "H3=%.17g expected=%.17g" % (w.H3_exact, expect))

    ok &= T("the test-mode step budget is enforced",
            raises(lambda: guard.advance(fresh_world(1), guard.MAX_TEST_STEPS + 1)),
            "an over-budget advance raises ProtocolError")
    ok &= T("no start may be opened in TEST mode",
            raises(lambda: guard.start("arm", "illegal", 10).__enter__()))
    ok &= T("gate_X cannot be called in TEST mode",
            raises(lambda: observe.gate_X(fresh_world(1), 2.5, 10, 3.0, 0.25, 6.0, 9.0)))
    ok &= T("arm_verdict cannot be called in TEST mode",
            raises(lambda: observe.arm_verdict({"outcome": "SEPARATED"}, 2.5, 5.0)))
    return ok


# ==================================================================== STATIC mode: observables
def _good_record():
    return {"outcome": "SEPARATED", "N_Y_at_separation": 2,
            "discs_at_separation": [{"centre": [10, 10], "N_X": 40, "N_Y": 1},
                                    {"centre": [10, 15], "N_X": 37, "N_Y": 1}]}


def static_tests():
    guard.set_static_mode()
    ok = True
    L = Spec.L

    ok &= T("advance() is impossible in STATIC mode",
            raises(lambda: guard.advance(fresh_world(1), 1)))

    ok &= T("torus distance wraps",
            observe.torus_dist((0, 0), (L - 1, 0), L) == 1.0
            and observe.torus_dist((0, 0), (L // 2, 0), L) == float(L // 2),
            "d((0,0),(%d,0)) = %.1f" % (L - 1, observe.torus_dist((0, 0), (L - 1, 0), L)))

    w = fresh_world(1)
    w.n["Y"][0, 0] = 1
    w.n["Y"][L - 2, 0] = 1
    ok &= T("organiser separation uses the wrapped distance",
            abs(observe.max_pair_separation(w) - 2.0) < 1e-12,
            "separation = %.3f (naive would be %d)" % (observe.max_pair_separation(w), L - 2))

    mask = np.zeros((L, L), dtype=bool)
    mask[0, :3] = True
    mask[L - 1, :3] = True                      # a band that crosses the boundary
    comps = observe.contact_components_torus(mask)
    ok &= T("contact components wrap across the torus seam", len(comps) == 1,
            "%d component(s), %d cells" % (len(comps), sum(len(c) for c in comps)))

    w = fresh_world(2)
    w.n["X"][10, 10] = 20
    w.n["Y"][10, 10] = 1
    w.n["X"][30, 30] = 1                        # a lone escapee, far away
    rep = observe.component_report(w)
    ok &= T("a lone body molecule is classified as an escapee, not a cluster",
            rep["n_components_excluding_escapees"] == 1 and rep["n_escapees"] == 1,
            json.dumps({k: rep[k] for k in ("n_components_raw",
                                            "n_components_excluding_escapees", "n_escapees")}))

    w = fresh_world(3)
    w.n["X"][0, 0] = 5
    w.n["X"][L - 1, 0] = 7                      # one site away across the seam
    w.n["X"][10, 10] = 100                      # far outside the disc
    nx, ny, msk = observe.disc_counts(w, (0, 0), 2.5)
    ok &= T("the organiser disc wraps and counts exactly", nx == 12 and ny == 0,
            "N_X in disc = %d (expected 12), disc cells = %d" % (nx, int(msk.sum())))

    w = fresh_world(4)
    w.n["X"][7, 7], w.n["Y"][7, 7], w.n["SY"][7, 7] = 5, 1, 3
    w.n["X"][20, 20] = 9                        # no organiser here: must not contribute
    free = w.free()
    want = int(w.n["X"][7, 7]) * min(int(w.n["SY"][7, 7]), int(free[7, 7]))
    ok &= T("realised Q reads the engine's own candidate rule",
            abs(observe.realised_Q(w) - want) < 1e-12,
            "Q = %.1f, independently computed %d" % (observe.realised_Q(w), want))

    good, v = observe.arm_verdict(_good_record(), 2.5, 5.0)
    ok &= T("a correct separation record passes the verdict", good, v)
    return ok


# ==================================================================== mutations, real path
def mutation_tests():
    guard.set_static_mode()
    ok = True
    L = Spec.L

    # --- mutations of the REAL verdict path
    r = _good_record()
    r["discs_at_separation"][0]["N_Y"] = 2
    ok &= M("both organisers end inside one disc", not observe.arm_verdict(r, 2.5, 5.0)[0],
            observe.arm_verdict(r, 2.5, 5.0)[1])

    r = _good_record()
    r["discs_at_separation"][1]["N_X"] = 1
    ok &= M("one organiser carries fewer body molecules than the minimum",
            not observe.arm_verdict(r, 2.5, 5.0)[0], observe.arm_verdict(r, 2.5, 5.0)[1])

    r = _good_record()
    r["discs_at_separation"][1]["N_X"] = 2
    r["discs_at_separation"][1]["N_Y"] = 1
    ok &= M("a component in which the organiser is not a minority",
            not observe.arm_verdict(r, 2.5, 5.0)[0], observe.arm_verdict(r, 2.5, 5.0)[1])

    r = _good_record()
    r["N_Y_at_separation"] = 3
    ok &= M("a third organiser present at separation",
            not observe.arm_verdict(r, 2.5, 5.0)[0], observe.arm_verdict(r, 2.5, 5.0)[1])

    r = _good_record()
    r["outcome"] = "CENSORED_NO_SEPARATION"
    ok &= M("a censored arm scored as a separation",
            not observe.arm_verdict(r, 2.5, 5.0)[0], observe.arm_verdict(r, 2.5, 5.0)[1])

    # --- mutations of the REAL constructor and gate path
    w = fresh_world(21)
    seed_one_organiser(w, 40)
    w.n["Y"][5, 5] = 1
    w.n["Y"][6, 6] = 1                                     # three organisers at the gate
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 20.0)
    ok &= M("three organisers are present when the window opens",
            (not g["PASS"]) and not g["checks"]["organiser_count_one_or_two"],
            str([k for k, v in g["checks"].items() if not v]))

    w = fresh_world(27)
    seed_one_organiser(w, 40)
    w.n["Y"][w.L // 2, w.L // 2] = 0                       # no organiser at all at the gate
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 20.0)
    ok &= M("no organiser is present when the window opens",
            (not g["PASS"]) and not g["checks"]["organiser_count_one_or_two"],
            str([k for k, v in g["checks"].items() if not v]))

    w = fresh_world(22)
    seed_one_organiser(w, 2)                               # no body cloud
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 20.0)
    ok &= M("no body cloud around the organiser", not g["PASS"],
            str([k for k, v in g["checks"].items() if not v]))

    w = fresh_world(23)
    w.n["Y"][2, 2] = 1
    w.n["X"][25, 25] = 60                                  # cloud detached from the organiser
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 20.0)
    ok &= M("the body cloud is not co-located with its organiser", not g["PASS"],
            str([k for k, v in g["checks"].items() if not v]))

    w = fresh_world(24)
    w.n["Y"][2, 2] = 1
    w.n["X"][:] = 1                                        # material fills the torus
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 20.0)
    ok &= M("the material fills the torus", not g["PASS"],
            str([k for k, v in g["checks"].items() if not v]))

    w = fresh_world(25)
    seed_one_organiser(w, 4)
    w.n["X"][w.L // 2, w.L // 2] = 40
    g = observe.gate_X(w, 2.5, 10, 3.0, 0.25, 6.0, 2.0)    # Q below the floor
    ok &= M("the core is too weak to adjudicate (Q below the floor)", not g["PASS"],
            str([k for k, v in g["checks"].items() if not v]))

    # --- a separation that has not actually happened
    w = fresh_world(26)
    w.n["Y"][10, 10] = 1
    w.n["Y"][10, 14] = 1                                   # 4.0 sites, below DELTA_SEP = 5.0
    ok &= M("two organisers closer than Delta_sep declared separated",
            observe.max_pair_separation(w) < 5.0,
            "separation = %.3f < 5.0" % observe.max_pair_separation(w))

    # --- the budget guard itself
    guard.set_experiment_mode()
    saved = (guard.LEDGER["count"], list(guard.LEDGER["log"]))
    guard.LEDGER["count"] = guard.MAX_STARTS
    ok &= M("a start beyond the declared budget",
            raises(lambda: guard.start("arm", "over", 1).__enter__()),
            "the %dth start raises" % (guard.MAX_STARTS + 1))
    guard.LEDGER["count"], guard.LEDGER["log"] = saved[0], saved[1]
    guard.set_static_mode()
    return ok


if __name__ == "__main__":
    print("--- AST checks")
    a = ast_checks()
    print("--- TEST mode: engine invariants")
    b = engine_tests()
    print("--- STATIC mode: observables")
    c = static_tests()
    print("--- STATIC mode: mutations on the real path")
    d = mutation_tests()
    aud = guard.audit()
    e = T("the harness consumed no outcome-informative start", aud["count"] == 0,
          "starts=%d, test steps used=%d of %d"
          % (aud["count"], aud["test_steps_used"], aud["max_test_steps"]))
    RESULTS["ledger_after_harness"] = aud
    RESULTS["ALL_PASS"] = bool(a and b and c and d and e)
    json.dump(RESULTS, open("/home/claude/MTW01/out/_integrity.json", "w"), indent=1)
    print("\nALL_PASS =", RESULTS["ALL_PASS"])
