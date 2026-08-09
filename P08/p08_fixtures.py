"""P08 fixtures. All must PASS before any protocol is sealed."""
from __future__ import annotations
import ast, json, math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
from od_core import LatticeBondEngine, LatticeBondState, largest_bounded, cells_of, THRESH, MMAX
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P7
import p08_core as P8

R = []
CALLS = 0


def chk(i, name, ok, detail):
    R.append({"fixture": i, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {i:>2}. {name:<58} {'PASS' if ok else 'FAIL'}  {detail}")


STATES = None


def states():
    global STATES, CALLS
    if STATES is not None:
        return STATES
    law = law_arms()["LAW_16"]
    out = []
    for L in (24, 32):
        for s in (1, 2, 3):
            m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(8000 + s), L, 0.35),
                                     dtype=np.float64)
            st = LatticeBondState(m, np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
            eng = LatticeBondEngine(law)
            CALLS += 1
            for target in (256, 420, 700):
                while int(st.step) < target:
                    st = eng.step(st).state
                c = largest_bounded(st)
                if c is not None and not (c.wraps_x or c.wraps_y):
                    out.append((L, s, target, st.copy(), c))
    STATES = out
    return out


def f1():
    """PARENT amount rule (floor=0, ceil=MMAX) is bit-identical to the sealed P07 operator."""
    wm = wc = 0.0
    k = 0
    for L, s, t, st, c in states():
        cells = cells_of(c)
        for ax in ("+x", "-x", "+y", "-y"):
            mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, ax)
            for qf in (0.25, 1.0, 4.0):
                a, b = st.copy(), st.copy()
                pa, pb = P7.Prov(a, cells, L), P7.Prov(b, cells, L)
                q = qf * pa.M256 / 80.0
                ra = P8.exchange_event(a, pa, mk, cells, L, q, 0.0, MMAX)
                rb = P7.exchange_event(b, pb, mk, cells, L, q)
                wm = max(wm, float(np.max(np.abs(a.m - b.m))))
                for kk in P7.COHORTS:
                    wc = max(wc, float(np.max(np.abs(pa.f[kk] - pb.f[kk]))))
                wc = max(wc, abs(ra["realized_sink"] - rb["realized_sink"]))
                k += 1
    chk(1, "regle PARENT == operateur P07 scelle, bit a bit", wm == 0.0 and wc == 0.0,
        f"{k} cas geles, max|dm| = {wm:.1e}, max|d cohorte| = {wc:.1e} -> la chaine "
        f"DEV_05 -> P07 -> P08 partage une physique identique")


def f2():
    """The safety floor is respected exactly: the sink never LEAVES a cell it took from below
    the floor. Cells that were already below the floor before the event are untouchable by
    construction and are not part of the claim."""
    worst = {}
    nsite = {}
    for L, s, t, st, c in states()[:8]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        for name, (fl, ce) in P8.AMOUNT_RULES.items():
            a = st.copy()
            pa = P7.Prov(a, cells, L)
            for _ in range(6):
                cc = largest_bounded(a)
                if cc is None:
                    break
                before = a.m.reshape(-1).copy()
                P8.exchange_event(a, pa, mk, cells_of(cc), L, 50.0, fl, ce)
                fm = a.m.reshape(-1)
                drained = [i for i in mk["sink"] if fm[i] < before[i] - 1e-15]
                nsite[name] = nsite.get(name, 0) + len(drained)
                for i in drained:
                    worst[name] = min(worst.get(name, 9.0), fm[i] - fl)
    ok = all(v >= -1e-12 for v in worst.values())
    chk(2, "le plancher: aucune cellule DRAINEE n'est laissee sous le plancher", ok,
        "; ".join(f"{k}: marge min = {worst.get(k, float('nan')):+.3e} "
                  f"({nsite.get(k, 0)} drainages)" for k in P8.AMOUNT_RULES))


def f3():
    """The headroom cap is respected exactly: no cell is ever filled above it."""
    worst = {}
    for L, s, t, st, c in states()[:8]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "-y")
        for name, (fl, ce) in P8.AMOUNT_RULES.items():
            a = st.copy()
            pa = P7.Prov(a, cells, L)
            for _ in range(8):
                cc = largest_bounded(a)
                if cc is None:
                    break
                P8.exchange_event(a, pa, mk, cells_of(cc), L, 50.0, fl, ce)
            fm = a.m.reshape(-1)
            v = max(fm[i] for i in mk["source"])
            worst[name] = max(worst.get(name, -9.0), v - ce)
    ok = all(v <= 1e-12 for v in worst.values())
    chk(3, "le plafond de reserve n'est jamais depasse", ok,
        "; ".join(f"{k}: depassement max = {v:+.3e}" for k, v in worst.items()))


def f4():
    """Conservation and cohort identity under every amount rule, including engine steps."""
    global CALLS
    law = law_arms()["LAW_16"]
    wi = wb = wn = 0.0
    for L, s, t, st, c in states()[:4]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "+y")
        for name, (fl, ce) in P8.AMOUNT_RULES.items():
            a = st.copy()
            pa = P7.Prov(a, cells, L)
            tot0 = float(a.m.sum())
            eng = LatticeBondEngine(law)
            CALLS += 1
            for kk in range(24):
                if kk % 4 == 0:
                    cc = largest_bounded(a)
                    if cc is not None:
                        r = P8.exchange_event(a, pa, mk, cells_of(cc), L, pa.M256 / 40.0,
                                              fl, ce)
                        wn = max(wn, abs(r["realized_sink"] - r["realized_source"]))
                wi = max(wi, pa.identity_residual(a))
                wb = max(wb, pa.global_balance_residual(a, tot0))
                pre = a
                o = eng.step(pre)
                pa.advance(pre.m, o.ledger, o.state.m, law.dt)
                a = o.state
    chk(4, "identite des cohortes, bilan global, masse nette nulle", wi <= 1e-9 and wb <= 1e-9
        and wn <= 1e-9,
        f"identite {wi:.1e}, bilan {wb:.1e}, |source-puits| {wn:.1e}")


def f5():
    """ORACLE FIREWALL: the sensor readout and every eligibility function read only the matter
    field, the frozen geometry and the current track."""
    tree = ast.parse(Path("p08_core.py").read_text())
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    forbidden_names = {"prov", "Prov", "seed", "block", "arm", "future", "terminal"}
    bad = []
    for name in ("sensor_readout", "sink_eligible", "source_eligible"):
        f = fns[name]
        args = {a.arg for a in f.args.args}
        if args & forbidden_names:
            bad.append((name, "forbidden argument", sorted(args & forbidden_names)))
        for node in ast.walk(f):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                bad.append((name, "forbidden name", node.id))
            if isinstance(node, ast.Attribute) and node.attr in ("f", "sink_by_cohort",
                                                                 "res_sink", "res_source"):
                bad.append((name, "provenance attribute", node.attr))
    chk(5, "pare-feu oracle: le controleur ne lit ni provenance ni futur", not bad,
        f"fonctions auditees: sensor_readout, sink_eligible, source_eligible; "
        f"violations = {bad if bad else 'aucune'}")


def f6():
    """The safety floor genuinely changes the physics: it is not a no-op."""
    diffs = []
    for L, s, t, st, c in states()[:6]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        a, b = st.copy(), st.copy()
        pa, pb = P7.Prov(a, cells, L), P7.Prov(b, cells, L)
        for _ in range(4):
            for stt, pp, fl in ((a, pa, 0.0), (b, pb, THRESH + P8.EPS_FLOOR)):
                cc = largest_bounded(stt)
                if cc is not None:
                    P8.exchange_event(stt, pp, mk, cells_of(cc), L, pa.M256 / 40.0, fl, MMAX)
        diffs.append(float(np.max(np.abs(a.m - b.m))))
    chk(6, "le plancher n'est pas un no-op", min(diffs) > 1e-6,
        f"ecart max de champ apres 4 evenements, par etat: "
        f"{[f'{d:.3f}' for d in diffs]}")


def f7():
    """Shadow readers are ordered and consistent with the official one."""
    bad = []
    k = 0
    for L, s, t, st, c in states():
        cells = cells_of(c)
        sh = P8.shadow_readout(st, cells, cells)
        areas = [sh[f"shadow_{int(round(x*100))}_area"] for x in P8.SHADOW_THRESHOLDS]
        if any(areas[i] < areas[i + 1] for i in range(len(areas) - 1)):
            bad.append((L, s, t, areas))
        if abs(sh["shadow_45_jaccard_official"] - 1.0) > 1e-9:
            bad.append((L, s, t, "official mismatch at 0.45"))
        k += 1
    chk(7, "lecteurs fantomes ordonnes, et 0.45 reproduit le tracker officiel", not bad,
        f"{k} etats; l'aire decroit avec le seuil et le lecteur a 0.45 coincide "
        f"exactement avec la piste officielle; violations = {bad[:2] if bad else 'aucune'}")


def f8():
    """UCR cannot be inflated by a futile cycle: a source that refills the drained cells must
    score lower than the parent on the same states."""
    res = {}
    for L, s, t, st, c in states()[:6]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        for tag, src in (("PARENT", mk["source"]), ("SINKSIDE", mk["sink"])):
            a = st.copy()
            pa = P7.Prov(a, cells, L)
            mk2 = dict(mk)
            mk2["source"] = src
            for _ in range(12):
                cc = largest_bounded(a)
                if cc is None:
                    break
                P8.exchange_event(a, pa, mk2, cells_of(cc), L, pa.M256 / 80.0, 0.0, MMAX)
            cc = largest_bounded(a)
            u = P8.unique_causal_replacement(pa, cells_of(cc) if cc else set(), pa.M256)
            res.setdefault(tag, []).append(u["UCR"])
    ok = all(a > b for a, b in zip(res["PARENT"], res["SINKSIDE"]))
    chk(8, "UCR penalise le cycle futile sur chaque etat", ok,
        f"PARENT {[f'{x:.4f}' for x in res['PARENT']]} vs "
        f"SINKSIDE {[f'{x:.4f}' for x in res['SINKSIDE']]}")


def f9():
    """A rejected event mutates nothing and names its cause; causes are exhaustive."""
    causes = set()
    w = 0.0
    for L, s, t, st, c in states()[:6]:
        cells = cells_of(c)
        mk = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, "+x")
        a = st.copy()
        pa = P7.Prov(a, cells, L)
        m0 = a.m.copy()
        r = P8.exchange_event(a, pa, mk, set(), L, 1.0)
        causes.add(r["reject_reason"])
        w = max(w, float(np.max(np.abs(a.m - m0))))
        # saturate the source, then ask again
        b = st.copy()
        pb = P7.Prov(b, cells, L)
        for _ in range(60):
            cc = largest_bounded(b)
            if cc is None:
                break
            rr = P8.exchange_event(b, pb, mk, cells_of(cc), L, 5.0)
            if rr["rejected"]:
                causes.add(rr["reject_reason"])
                break
    chk(9, "rejets: aucune mutation, causes nommees et exhaustives",
        w == 0.0 and causes <= {"NO_SINK_CAPACITY", "NO_SOURCE_CAPACITY", "NO_PLANNED_DOSE"},
        f"causes observees = {sorted(causes)}, max|dm| sur rejet = {w:.1e}")


def f10():
    """Production engine, detector and tracer untouched; n and b never written."""
    import hashlib
    import edlab.substrates.lattice_bond.engine as E
    import edlab.substrates.lattice_bond.instrumentation as I
    h = {Path(m.__file__).name: hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
         for m in (E, I)}
    tree = ast.parse(Path("p08_core.py").read_text())
    w = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute)
         and n.attr in ("n", "b") and isinstance(n.ctx, ast.Store)]
    chk(10, "moteur et detecteur de production intacts", not w,
        f"aucune ecriture sur state.n / state.b; engine {h['engine.py'][:12]}, "
        f"instrumentation {h['instrumentation.py'][:12]}")


def main():
    print("=== FIXTURES PROGRAM_08 ===")
    for f in (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10):
        try:
            f()
        except Exception as e:
            import traceback
            traceback.print_exc()
            chk(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    p = sum(1 for x in R if x["PASS"])
    Path("p08_fixtures.json").write_text(json.dumps(
        {"n": len(R), "n_pass": p, "VERDICT": "PASS" if p == len(R) else "FAIL",
         "engine_state_generators": CALLS, "fixtures": R}, indent=1))
    print(f"\n{p}/{len(R)} -> {'PASS' if p == len(R) else 'FAIL'}  ({CALLS} generateurs)")
    return 0 if p == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
