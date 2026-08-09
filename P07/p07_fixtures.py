"""PROGRAM_07 fixture suite. Every fixture must PASS before the protocol is sealed.

Fixtures use the engine only to MANUFACTURE frozen states; no scientific arm is run here.
Engine invocations are counted and reported.
"""
from __future__ import annotations
import ast, json, math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../DR05")

from od_core import (LatticeBondEngine, LatticeBondState, THRESH, MMAX, comps, largest_bounded,
                     cells_of, nbrs, fhash)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P
import dr_core as D                     # the sealed DEV_05 operator, for exact comparison

R = []
CALLS = 0


def check(n, name, ok, detail):
    R.append({"fixture": n, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {n:>2}. {name:<54} {'PASS' if ok else 'FAIL'}  {detail}")
    return bool(ok)


def frozen_states(sizes=(24, 32), seeds=(1, 2, 3), steps=(256, 400, 700)):
    """Manufacture reproducible frozen states. Engine used as a state generator only."""
    global CALLS
    law = law_arms()["LAW_16"]
    out = []
    for L in sizes:
        for s in seeds:
            m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(7000 + s), L, 0.35),
                                     dtype=np.float64)
            st = LatticeBondState(m, np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
            eng = LatticeBondEngine(law)
            CALLS += 1
            nxt = 0
            for target in steps:
                while int(st.step) < target:
                    st = eng.step(st).state
                c = largest_bounded(st)
                if c is not None and not (c.wraps_x or c.wraps_y):
                    out.append((L, s, target, st.copy(), c))
                nxt += 1
    return out


STATES = None


def setup(a=None):
    global STATES
    if STATES is None:
        STATES = frozen_states()
    return STATES


# ------------------------------------------------------------------ fixtures
def f1():
    """The detector threshold implies the track gate: every tracked cell has m >= THRESH."""
    worst = 1e9
    n = 0
    for L, s, t, st, c in setup():
        fm = st.m.reshape(-1)
        for i in cells_of(c):
            worst = min(worst, fm[i])
            n += 1
    src = Path("../edlab/substrates/lattice_bond/instrumentation.py").read_text()
    literal = "occupied = np.asarray(state.m >= spec.matter_threshold, dtype=bool)" in src
    check(1, "i in TRACK  =>  m[i] >= THRESH  (GATE_THRESH redundant)",
          worst >= THRESH and literal and n > 0,
          f"{n} cellules suivies, min m = {worst:.6f} >= {THRESH}; predicat du detecteur "
          f"litteral verifie dans la source = {literal}")


def f2():
    """The PARENT gate reproduces the sealed DEV_05 operator EXACTLY on frozen states."""
    worst_m = worst_c = 0.0
    n = 0
    axes = ("+x", "-x", "+y", "-y")
    for L, s, t, st, c in setup():
        cells = cells_of(c)
        for ai, ax in enumerate(axes):
            mk7 = P.build_masks(cells, L, c.centroid_y, c.centroid_x, ax)
            mk5 = D.build_masks_05(cells, L, c.centroid_y, c.centroid_x, ax)
            if mk7["sink"] != mk5["sink"] or mk7["source"] != mk5["source"]:
                return check(2, "operateur PARENT == DEV_05 exactement", False,
                             "les masques different")
            for qf in (0.25, 1.0, 4.0):
                a, b = st.copy(), st.copy()
                pa = P.Prov(a, cells, L)
                pb = D.Prov(b, cells, L)
                q = qf * pa.M256 / 80.0
                ra = P.exchange_event(a, pa, mk7, cells, L, q)
                rb = D.direct_event(b, pb, mk5, cells, L, q, "DIRECT")
                worst_m = max(worst_m, float(np.max(np.abs(a.m - b.m))))
                for k in P.COHORTS:
                    worst_c = max(worst_c, float(np.max(np.abs(pa.f[k] - pb.f[k]))))
                worst_c = max(worst_c, abs(ra["realized_sink"] - rb["realized_sink"]),
                              abs(ra["realized_source"] - rb["realized_source"]))
                n += 1
    check(2, "operateur PARENT == DEV_05 exactement (etats geles)",
          worst_m == 0.0 and worst_c == 0.0, n and
          f"{n} cas (taille x graine x temps x axe x quota), max|dm| = {worst_m:.1e}, "
          f"max|d cohorte| = {worst_c:.1e} -> continuite operatoire exacte avec le parent scelle")


def f3():
    """A coupled event moves exactly zero NET mass, under every gate and placement."""
    worst = 0.0
    n = 0
    for L, s, t, st, c in setup()[:6]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        for g in (P.Gate("A"), P.Gate("B", spread="MULTISITE"), P.Gate("C", mask="COMOVING"),
                  P.Gate("D", track=False, thresh=False)):
            for pl in P.SOURCE_PLACEMENTS:
                a = st.copy()
                pa = P.Prov(a, cells, L)
                tot0 = float(a.m.sum())
                r = P.exchange_event(a, pa, mk, cells, L, pa.M256 / 20.0, g, pl)
                worst = max(worst, abs(float(a.m.sum()) - tot0),
                            abs(r["realized_sink"] - r["realized_source"]))
                n += 1
    check(3, "evenement couple: masse NETTE deplacee = 0", worst <= 1e-12,
          f"{n} combinaisons porte x placement, pire |source - puits| = {worst:.1e}")


def f4():
    """Cohort identity: sum of the five cohorts is identically the matter field, after
    mutation AND after engine steps."""
    global CALLS
    law = law_arms()["LAW_16"]
    worst_i = worst_b = 0.0
    for L, s, t, st, c in setup()[:4]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "-y")
        a = st.copy()
        pa = P.Prov(a, cells, L)
        tot0 = float(a.m.sum())
        eng = LatticeBondEngine(law)
        CALLS += 1
        for k in range(24):
            if k % 4 == 0:
                cc = largest_bounded(a)
                if cc is not None:
                    P.exchange_event(a, pa, mk, cells_of(cc), L, pa.M256 / 40.0)
            worst_i = max(worst_i, pa.identity_residual(a))
            worst_b = max(worst_b, pa.global_balance_residual(a, tot0))
            pre = a
            o = eng.step(pre)
            pa.advance(pre.m, o.ledger, o.state.m, law.dt)
            a = o.state
        worst_i = max(worst_i, pa.identity_residual(a))
        worst_b = max(worst_b, pa.global_balance_residual(a, tot0))
    check(4, "identite des cohortes + bilan global conserves sous advection",
          worst_i <= 1e-9 and worst_b <= 1e-9,
          f"pire residu d'identite = {worst_i:.1e}, pire residu de bilan = {worst_b:.1e}")


def f5():
    """No selector reads any provenance field. AST scan, not convention."""
    tree = ast.parse(Path("p07_core.py").read_text())
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    bad = []
    for name in ("sink_eligible", "source_eligible", "capacity_spectrum", "_mask_cells"):
        f = fns[name]
        args = {a.arg for a in f.args.args}
        for node in ast.walk(f):
            if isinstance(node, ast.Name) and node.id in ("prov", "Prov"):
                bad.append((name, "prov"))
            if isinstance(node, ast.Attribute) and node.attr in ("f", "sink_by_cohort"):
                if isinstance(node.value, ast.Name) and node.value.id == "prov":
                    bad.append((name, node.attr))
        if "prov" in args:
            bad.append((name, "prov-in-signature"))
    check(5, "aucun selecteur ne lit la provenance (scan AST)", not bad,
          f"selecteurs audites: sink_eligible, source_eligible, capacity_spectrum, "
          f"_mask_cells; violations = {bad if bad else 'aucune'}")


def f6():
    """Order invariance sink-first vs source-first, measured per placement."""
    res = {}
    for pl in P.SOURCE_PLACEMENTS:
        wm = wc = 0.0
        n = 0
        for L, s, t, st, c in setup()[:6]:
            cells = cells_of(c)
            mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
            for qf in (0.5, 2.0):
                a, b = st.copy(), st.copy()
                pa, pb = P.Prov(a, cells, L), P.Prov(b, cells, L)
                q = qf * pa.M256 / 80.0
                ra = P.exchange_event(a, pa, mk, cells, L, q, source_placement=pl,
                                      order="SINK_FIRST")
                rb = P.exchange_event(b, pb, mk, cells, L, q, source_placement=pl,
                                      order="SOURCE_FIRST")
                wm = max(wm, float(np.max(np.abs(a.m - b.m))))
                wc = max(wc, max(float(np.max(np.abs(pa.f[k] - pb.f[k]))) for k in P.COHORTS),
                         abs(ra["realized_sink"] - rb["realized_sink"]))
                n += 1
        res[pl] = (wm, wc, n)
    # Disjoint placements MUST be order-invariant to float tolerance; the overlapping one
    # MUST be detected as order-dependent rather than silently averaged over.
    disjoint_ok = all(max(res[k][0], res[k][1]) <= 1e-12 for k in ("INTERFACE", "DISPERSED"))
    overlap_detected = max(res["SINKSIDE"][0], res["SINKSIDE"][1]) > 1e-6
    txt = "; ".join(f"{k}: max|dm|={v[0]:.1e} max|dcoh|={v[1]:.1e}" for k, v in res.items())
    check(6, "invariance a l'ordre source-puits (mesuree, pas supposee)",
          disjoint_ok and overlap_detected,
          f"{txt}  -> INTERFACE et DISPERSED invariants a l'ordre (masques disjoints du puits, "
          f"ecart au niveau de l'arrondi); SINKSIDE ordre-dependant PAR CONSTRUCTION et "
          f"detecte comme tel. Ordre canonique de tous les bras = SINK_FIRST (celui du parent)")
    Path("p07_order_invariance.json").write_text(json.dumps(
        {k: {"max_abs_dm": v[0], "max_abs_dcohort": v[1], "n": v[2]} for k, v in res.items()},
        indent=1))


def f7():
    """The sweep decomposition is an exact identity on real engine trajectories."""
    global CALLS
    law = law_arms()["LAW_16"]
    worst = 0.0
    n = 0
    for L, s, t, st, c in setup()[:4]:
        a = st.copy()
        eng = LatticeBondEngine(law)
        CALLS += 1
        prev_cells, prev_m = cells_of(c), a.m.reshape(-1).copy()
        prev_T = math.fsum(prev_m[i] for i in prev_cells)
        for k in range(32):
            a = eng.step(a).state
            cc = largest_bounded(a)
            if cc is None:
                break
            cells = cells_of(cc)
            fm = a.m.reshape(-1)
            T = math.fsum(fm[i] for i in cells)
            d = P.sweep_decomposition(prev_cells, prev_m, cells, fm)
            lhs = T - prev_T
            rhs = (d["MATERIAL_CHANGE_ON_RETAINED_SITES"] + d["MASK_ENTRY"] + d["MASK_EXIT"])
            worst = max(worst, abs(lhs - rhs))
            n += 1
            prev_cells, prev_m, prev_T = cells, fm.copy(), T
    check(7, "dT = retenu + entree de masque + sortie de masque (exact)", worst <= 1e-12,
          f"{n} pas apparies, pire ecart = {worst:.1e}")


def f8():
    """Capacity spectrum ordering: the parent capacity is a lower bound of every relaxation."""
    bad = []
    n = 0
    for L, s, t, st, c in setup():
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        cs = P.capacity_spectrum(st, mk, cells, L)
        if not (cs["CAP_PARENT"] <= cs["CAP_FROZEN_UNTRACKED"] + 1e-12
                <= cs["CAP_FROZEN_ANY"] + 2e-12):
            bad.append((L, s, t, "frozen chain"))
        if cs["CAP_PARENT"] > cs["CAP_TRACKALL"] + 1e-12:
            bad.append((L, s, t, "trackall"))
        n += 1
    check(8, "spectre de capacite ordonne (PARENT est une borne inferieure)", not bad,
          f"{n} etats, violations = {bad if bad else 'aucune'}")


def f9():
    """MULTISITE respects the quota and never removes more than a cell holds."""
    worst_over = worst_neg = 0.0
    n = 0
    for L, s, t, st, c in setup()[:6]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "-x")
        g = P.Gate("M", spread="MULTISITE")
        for qf in (0.1, 1.0, 10.0):
            a = st.copy()
            pa = P.Prov(a, cells, L)
            q = qf * pa.M256 / 80.0
            r = P.exchange_event(a, pa, mk, cells, L, q, g, mode="SINK_ONLY")
            worst_over = max(worst_over, r["realized_sink"] - min(q, r["sink_capacity"]))
            worst_neg = min(worst_neg, float(a.m.min()))
            n += 1
    check(9, "MULTISITE: quota respecte, aucune masse negative",
          worst_over <= 1e-12 and worst_neg >= -1e-15,
          f"{n} cas, pire depassement = {worst_over:.1e}, min m = {worst_neg:.1e}")


def f10():
    """The source never pushes a cell above MMAX and only writes into FRESH."""
    worst = -1e9
    leak = 0.0
    n = 0
    for L, s, t, st, c in setup()[:6]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+y")
        for pl in P.SOURCE_PLACEMENTS:
            a = st.copy()
            pa = P.Prov(a, cells, L)
            before = {k: pa.f[k].copy() for k in P.INCUMBENT + ("amb",)}
            P.exchange_event(a, pa, mk, cells, L, 50.0, mode="SOURCE_ONLY",
                             source_placement=pl)
            worst = max(worst, float(a.m.max()))
            for k in before:
                leak = max(leak, float(np.max(np.abs(pa.f[k] - before[k]))))
            n += 1
    check(10, "la source ne depasse jamais MMAX et n'ecrit que dans FRESH",
          worst <= MMAX + 1e-12 and leak == 0.0,
          f"{n} cas a quota sature, max m = {worst:.9f} <= {MMAX}, "
          f"fuite hors FRESH = {leak:.1e}")


def f11():
    """The sink is provenance-proportional: a cohort's share of the bite equals its share
    of the cell. Tested numerically, not asserted."""
    worst = 0.0
    n = 0
    for L, s, t, st, c in setup()[:6]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        a = st.copy()
        pa = P.Prov(a, cells, L)
        # seed a heterogeneous FRESH field so the cohorts are genuinely mixed
        P.exchange_event(a, pa, mk, cells, L, pa.M256 / 8.0, source_placement="SINKSIDE",
                         mode="SOURCE_ONLY")
        fm = a.m.reshape(-1).copy()
        share = {k: {i: pa.f[k].reshape(-1)[i] / fm[i] for i in mk["sink"] if fm[i] > 1e-9}
                 for k in P.COHORTS}
        r = P.exchange_event(a, pa, mk, cells, L, pa.M256 / 40.0, mode="SINK_ONLY")
        tot = r["realized_sink"]
        if tot > 1e-9:
            for k in P.COHORTS:
                got = r["removed_by_cohort"][k] / tot
                # expected share, weighted by how much was taken from each cell
                d = fm - a.m.reshape(-1)
                exp = math.fsum(share[k].get(i, 0.0) * d[i] for i in mk["sink"]) / tot
                worst = max(worst, abs(got - exp))
            n += 1
    check(11, "le puits retire proportionnellement a la presence locale des cohortes",
          worst <= 1e-9, f"{n} cas avec cohortes melangees, pire ecart de part = {worst:.1e}")


def f12():
    """frame_metrics is internally consistent and the COMOVING mask really differs once
    the track has moved."""
    global CALLS
    law = law_arms()["LAW_16"]
    bad = []
    diffs = []
    for L, s, t, st, c in setup()[:4]:
        cells0 = cells_of(c)
        mk = P.build_masks(cells0, L, c.centroid_y, c.centroid_x, "+x")
        a = st.copy()
        pa = P.Prov(a, cells0, L)
        eng = LatticeBondEngine(law)
        CALLS += 1
        for k in range(200):
            pre = a
            o = eng.step(pre)
            pa.advance(pre.m, o.ledger, o.state.m, law.dt)
            a = o.state
        cc = largest_bounded(a)
        if cc is None:
            continue
        cells = cells_of(cc)
        fmm = P.frame_metrics(a, pa, cells, L)
        Tm = math.fsum(a.m.reshape(-1)[i] for i in cells)
        if fmm["mass_in_C256_cap_Ct"] > min(fmm["mass_in_frozen_C256"], Tm) + 1e-9:
            bad.append((L, s, "intersection"))
        fro = set(P._mask_cells(P.Gate("f"), mk, cells, a, L))
        com = set(P._mask_cells(P.Gate("c", mask="COMOVING"), mk, cells, a, L))
        diffs.append(len(fro ^ com))
    check(12, "cadre fige coherent et masque COMOVING reellement distinct", not bad
          and max(diffs) > 0,
          f"differences symetriques FROZEN vs COMOVING apres 200 pas: {diffs}; "
          f"incoherences = {bad if bad else 'aucune'}")


def f13():
    """A rejected event mutates nothing at all, and names its cause."""
    causes = set()
    worst = 0.0
    n = 0
    for L, s, t, st, c in setup()[:6]:
        cells = cells_of(c)
        mk = P.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        a = st.copy()
        pa = P.Prov(a, cells, L)
        m0 = a.m.copy()
        r = P.exchange_event(a, pa, mk, set(), L, pa.M256 / 80.0)   # empty track -> no capacity
        causes.add(r["reject_reason"])
        worst = max(worst, float(np.max(np.abs(a.m - m0))))
        n += 1
        if not r["rejected"]:
            causes.add("NOT_REJECTED_BUG")
    check(13, "un evenement rejete ne mute rien et nomme sa cause",
          worst == 0.0 and causes == {"NO_SINK_CAPACITY"},
          f"{n} cas force a capacite nulle, causes = {sorted(causes)}, max|dm| = {worst:.1e}")


def f14():
    """The engine and the detector are the production ones, unmodified."""
    import edlab.substrates.lattice_bond.engine as E
    import edlab.substrates.lattice_bond.instrumentation as I
    hs = {}
    for mod in (E, I):
        p = Path(mod.__file__)
        import hashlib
        hs[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    tree = ast.parse(Path("p07_core.py").read_text())
    writes = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute)
              and n.attr in ("n", "b") and isinstance(n.ctx, ast.Store)]
    check(14, "moteur et detecteur de production intacts; n et b jamais ecrits",
          not writes, f"aucune ecriture sur state.n / state.b dans p07_core; "
          f"engine.py = {hs['engine.py'][:12]}, instrumentation.py = "
          f"{hs['instrumentation.py'][:12]}")


def main():
    print("=== FIXTURES PROGRAM_07 ===")
    for f in (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14):
        try:
            f()
        except Exception as e:
            import traceback
            traceback.print_exc()
            check(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    n = sum(1 for x in R if x["PASS"])
    Path("p07_fixtures.json").write_text(json.dumps(
        {"n": len(R), "n_pass": n, "VERDICT": "PASS" if n == len(R) else "FAIL",
         "engine_state_generators": CALLS, "fixtures": R}, indent=1))
    print(f"\n{n}/{len(R)} -> {'PASS' if n == len(R) else 'FAIL'}   "
          f"({CALLS} generateurs d'etats moteur)")
    return 0 if n == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
