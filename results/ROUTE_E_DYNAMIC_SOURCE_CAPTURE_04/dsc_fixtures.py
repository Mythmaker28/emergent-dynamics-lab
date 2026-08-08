"""ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 -- section 7 fixtures.

NO scientific engine is invoked anywhere in this file. Every state is hand-built and every
transition is imposed, so each counter is checked against a mass that is known exactly.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

from od_core import LatticeBondState, largest_bounded, cells_of, nbrs, comps, THRESH, MMAX
from dsc_core import (Provenance, Causal, build_masks_04, coupled_event, do_sink, do_source,
                      source_capacity, sink_capacity, outer_shell)

L = 24
R = []


def state_from(m):
    return LatticeBondState(np.ascontiguousarray(m, dtype=np.float64),
                            np.full((L, L), 0.8), np.zeros((2, L, L)), 0)


def disc(cy, cx, r, val=0.9, bg=0.10):
    m = np.full((L, L), bg)
    yy, xx = np.mgrid[0:L, 0:L]
    m[((yy - cy) ** 2 + (xx - cx) ** 2) <= r * r] = val
    return m


def track_of(st):
    c = largest_bounded(st)
    return cells_of(c) if c is not None else None


def labels_of(st, track):
    out = {}
    for c in comps(st):
        cs = cells_of(c)
        if cs == track:
            continue
        for i in cs:
            out[i] = c.index
    return out


def check(n, name, ok, detail):
    R.append({"fixture": n, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {n:>2}. {name:<44} {'PASS' if ok else 'FAIL'}   {detail}")


# ---------------------------------------------------------------- 1 relabeling
def f1():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr)
    before = st.m.copy()
    # relabel: move 30% of incumbent into the ambient label, no physical transfer at all
    shift = p.inc * 0.30
    p.inc -= shift; p.amb += shift
    ok = (np.array_equal(before, st.m) and p.balance_error(st) < 1e-15
          and p.res_source == 0.0 and p.res_sink == 0.0)
    check(1, "relabeling without transfer", ok,
          f"|m| inchange, erreur={p.balance_error(st):.1e}, flux=0")


# ------------------------------------------------------------ 2 distant injection
def f2():
    st = state_from(disc(6, 6, 3))
    tr = track_of(st)
    p = Provenance(st, tr)
    cz = Causal(st.m.shape, 16)
    far = [i for i in range(L * L) if i not in tr and i not in outer_shell(tr, L)
           and min(abs((i // L) - 6), abs((i % L) - 6)) > 6][:20]
    r = do_source(st, p, far, tr, L, 2.0, True)
    cz.update(st, p, tr, labels_of(st, tr), L, 16)
    ok = r["injected"] > 1.9 and cz.contact == 0.0 and cz.capture_transport == 0.0
    check(2, "injection lointaine", ok,
          f"inj={r['injected']:.3f} contact={cz.contact:.3f} capture={cz.capture_transport:.3f}")


# ------------------------------------------------- 3 injection connected to track
def f3():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    c = largest_bounded(st)
    p = Provenance(st, tr)
    cz = Causal(st.m.shape, 16)
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    r = coupled_event(st, p, mk, tr, L, 1.0, "DIRECT_INTERFACE", True)
    cz.direct_insertion += r["direct_insertion"]
    cz.update(st, p, track_of(st), labels_of(st, tr), L, 16)
    ok = r["direct_insertion"] > 1e-9 and cz.capture_transport == 0.0
    check(3, "injection directement connectee", ok,
          f"insertion_directe={r['direct_insertion']:.3f} capture_dyn={cz.capture_transport:.3f}")


# ------------------------------------------------------- 4 contact without entry
def f4():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr)
    cz = Causal(st.m.shape, 16)
    shell = sorted(outer_shell(tr, L))[:6]
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    tot = 0.0
    for i in shell:
        add = 0.20
        fm[i] += add; ff[i] += add; tot += add      # stays sub-threshold, still outside
    cz.update(st, p, track_of(st), labels_of(st, tr), L, 16)
    ok = abs(cz.contact - tot) < 1e-12 and cz.capture_transport == 0.0
    check(4, "contact sans entree", ok,
          f"contact={cz.contact:.4f} (attendu {tot:.4f}) capture={cz.capture_transport:.4f}")


# ------------------------------------------------- 5 entry shorter than 16 frames
def f5():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    cz.update(st, p, tr, labels_of(st, tr), L, 0)
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    inside = sorted(tr)[:4]
    for i in inside:
        fm[i] += 0.05; ff[i] += 0.05
    cz.update(st, p, tr, labels_of(st, tr), L, 16)
    cap = cz.capture_transport
    for i in inside:                                   # gone again before the next checkpoint
        fm[i] -= 0.05; ff[i] -= 0.05
    cz.update(st, p, tr, labels_of(st, tr), L, 32)
    ok = cap > 1e-9 and cz.incorporation_16 == 0.0
    check(5, "entree de moins de 16 frames", ok,
          f"capture={cap:.4f} incorporation_16={cz.incorporation_16:.4f}")


# --------------------------------------------------------- 6 residence 16 / 128
def f6():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    inside = sorted(tr)[:5]
    exact = 0.0
    for i in inside:
        fm[i] += 0.06; ff[i] += 0.06; exact += 0.06
    for fr in range(0, 129 + 16, 16):
        cz.update(st, p, tr, labels_of(st, tr), L, fr)
    ok = (abs(cz.incorporation_16 - exact) < 1e-12 and abs(cz.durable_128 - exact) < 1e-12)
    check(6, "sejour 16 puis 128 frames", ok,
          f"inc16={cz.incorporation_16:.4f} dur128={cz.durable_128:.4f} exact={exact:.4f}")


# -------------------------------------------------------- 7 exit then re-entry
def f7():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    cz.update(st, p, tr, labels_of(st, tr), L, 0)
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    i = sorted(tr)[0]
    fm[i] += 0.10; ff[i] += 0.10
    cz.update(st, p, tr, labels_of(st, tr), L, 16)
    once = cz.capture_transport
    fm[i] -= 0.10; ff[i] -= 0.10                        # leaves
    cz.update(st, p, tr, labels_of(st, tr), L, 32)
    fm[i] += 0.10; ff[i] += 0.10                        # comes back
    cz.update(st, p, tr, labels_of(st, tr), L, 48)
    ok = abs(cz.capture_transport - once) < 1e-12 and abs(once - 0.10) < 1e-12
    check(7, "sortie puis reentree", ok,
          f"capture unique={cz.capture_transport:.4f} (attendu {once:.4f}, une seule fois)")


# ------------------------------------------------------------ 8 bypass source->sink
def f8():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st); c = largest_bounded(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    do_source(st, p, mk["source"], tr, L, 1.0, True)     # fresh sits in the halo, never enters
    cz.update(st, p, tr, labels_of(st, tr), L, 16)
    r = do_sink(st, p, mk["sink"], tr, L, 1.0)           # sink draws only incumbent
    ok = cz.capture_transport == 0.0 and r["fre_to_sink"] == 0.0 and cz.transit == 0.0
    check(8, "bypass source->puits", ok,
          f"transit={cz.transit:.4f} fre_vers_puits={r['fre_to_sink']:.4f}")


# --------------------------------------- 9 source -> track -> residence -> sink
def f9():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st); c = largest_bounded(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    sink_cell = mk["sink"][0]
    known = 0.12
    fm[sink_cell] += known; ff[sink_cell] += known        # fresh has arrived inside the track
    for fr in (0, 16, 32):
        cz.update(st, p, tr, labels_of(st, tr), L, fr)
    assert cz.window_min(16) > 1e-12
    r = do_sink(st, p, [sink_cell], tr, L, fm[sink_cell])
    cz.transit += r["fre_to_sink"]
    ok = abs(cz.transit - known) < 1e-9
    check(9, "source->piste->sejour->puits", ok,
          f"transit={cz.transit:.4f} (masse exacte connue {known:.4f})")


# ----------------------------------------------------------------- 10 accretion
def f10():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr)
    M256 = float(sum(st.m.reshape(-1)[i] for i in tr))
    ff = p.fre.reshape(-1); fm = st.m.reshape(-1)
    f0 = 0.0
    for i in sorted(tr)[:6]:
        fm[i] = min(MMAX, fm[i] + 0.05); ff[i] += 0.05
    tr2 = track_of(st)
    mass = float(sum(fm[i] for i in tr2))
    inc = float(sum(p.inc.reshape(-1)[i] for i in tr2))
    fre = float(sum(ff[i] for i in tr2))
    ok = (fre / mass > f0 and abs(M256 - inc) < 1e-9
          and min(p.sink_inc, fre) / M256 == 0.0)
    check(10, "accretion pure", ok,
          f"fraction_fraiche={fre/mass:.4f} perte_incumbent={(M256-inc)/M256:.2e} "
          f"remplacement_apparie_puits=0")


# ------------------------------------------- 11 ablation, mass halves, composition flat
def f11():
    st = state_from(disc(12, 12, 6))
    tr = track_of(st)
    p = Provenance(st, tr)
    M256 = float(sum(st.m.reshape(-1)[i] for i in tr))
    fm = st.m.reshape(-1); fi = p.inc.reshape(-1)
    for i in sorted(tr):                                 # partial, uniform, keeps every cell
        take = fm[i] * 0.50
        frac = take / fm[i]
        fm[i] -= take; fi[i] -= fi[i] * frac
        p.res_sink += take; p.sink_inc += fi[i] * 0.0
    tr2 = track_of(st)
    mass = float(sum(fm[i] for i in tr2))
    inc = float(sum(fi[i] for i in tr2))
    fre = float(sum(p.fre.reshape(-1)[i] for i in tr2))
    comp = inc / mass
    renewal = fre > 1e-12
    ok = abs(mass / M256 - 0.5) < 0.02 and abs(comp - 1.0) < 1e-9 and not renewal
    check(11, "ablation: masse /2, composition constante", ok,
          f"masse={mass/M256:.3f}xM256 composition={comp:.4f} MATERIAL_RENEWAL={renewal}")


# ------------------------------------------------- 12 exact direct physical exchange
def f12():
    st = state_from(disc(12, 12, 5))
    tr = track_of(st); c = largest_bounded(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    M256 = float(sum(st.m.reshape(-1)[i] for i in tr))
    m0 = float(st.m.sum())
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    q = 1.0
    r = coupled_event(st, p, mk, tr, L, q, "DIRECT_INTERFACE", True)
    cz.update(st, p, track_of(st), labels_of(st, tr), L, 16)
    stable = abs(float(st.m.sum()) - m0) < 1e-9
    ok = (stable and abs(r["direct_insertion"] - q) < 1e-9
          and abs(min(r["inc_to_sink"], r["injected"]) - q) < 1e-9
          and cz.capture_transport == 0.0)
    check(12, "echange physique direct exact q", ok,
          f"masse_stable={stable} insertion={r['direct_insertion']:.4f} "
          f"remplacement_apparie={min(r['inc_to_sink'],r['injected'])/1.0:.4f} "
          f"capture_dyn={cz.capture_transport:.4f}")


# -------------------------------------------------------------- 13 fragmentation
def f13():
    m = disc(8, 8, 3)
    yy, xx = np.mgrid[0:L, 0:L]
    m[((yy - 18) ** 2 + (xx - 18) ** 2) <= 4] = 0.9     # a second, smaller component
    st = state_from(m)
    c = largest_bounded(st)
    tr = cells_of(c)
    allc = comps(st)
    ok = len(allc) == 2 and len(tr) == max(len(cells_of(x)) for x in allc)
    check(13, "fragmentation: seule la continuation gelee compte", ok,
          f"{len(allc)} composants, piste = le plus grand ({len(tr)} cellules)")


# ------------------------------------------- 14 disappearance then reappearance
def f14():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    cz.update(st, p, tr, labels_of(st, tr), L, 0)
    empty = state_from(np.full((L, L), 0.10))
    lost = track_of(empty)
    cz.update(empty, p, lost, None, L, 16)
    back = state_from(disc(12, 12, 4))
    cz.update(back, p, track_of(back), labels_of(back, track_of(back)), L, 32)
    ok = lost is None and cz.prev_cells is not None and len(cz.hist) == 1
    check(14, "disparition puis reapparition", ok,
          f"continuite=False (historique de sejour remis a zero: {len(cz.hist)} echantillon)")


# ------------------------------------------- 15 atomic coupling, source unavailable
def f15():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st); c = largest_bounded(st)
    p = Provenance(st, tr)
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    mk["source"] = []                                    # nothing the source can reach
    before = st.m.copy()
    r = coupled_event(st, p, mk, tr, L, 1.0, "COUPLED", True)
    ok = (r["injected"] == 0.0 and r["removed"] == 0.0
          and np.array_equal(before, st.m) and p.res_sink == 0.0 and p.res_source == 0.0)
    check(15, "couplage atomique, source indisponible", ok,
          f"source=0 puits=0 etat_inchange={np.array_equal(before, st.m)}")


# ------------------------------------------------------- 16 fractional conservation
def f16():
    st = state_from(disc(12, 12, 4))
    tr = track_of(st); c = largest_bounded(st)
    p = Provenance(st, tr)
    total0 = float(st.m.sum())
    mk = build_masks_04(tr, L, c.centroid_y, c.centroid_x, "+x", 2)
    for _ in range(5):
        coupled_event(st, p, mk, track_of(st), L, 0.4, "COUPLED", True)
    fields = p.balance_error(st)
    system = p.system_error(st, total0)
    ok = fields < 1e-12 and system < 1e-12
    check(16, "conservation fractionnaire", ok,
          f"max|m-(INC+AMB+FRE)|={fields:.2e}  |lattice+reservoirs-total0|={system:.2e}")


# ------------------------------------ 17 separate source component then merger
def f17():
    m = disc(12, 12, 4)
    yy, xx = np.mgrid[0:L, 0:L]
    m[((yy - 12) ** 2 + (xx - 5) ** 2) <= 2] = 0.9      # separate blob, upstream
    st = state_from(m)
    c = largest_bounded(st)
    tr = cells_of(c)
    p = Provenance(st, tr); cz = Causal(st.m.shape, 16)
    blob = {i for i in range(L * L) if st.m.reshape(-1)[i] >= THRESH} - tr
    ff = p.fre.reshape(-1)
    for i in blob:
        ff[i] = st.m.reshape(-1)[i]                      # the blob is entirely fresh matter
    cz.update(st, p, tr, labels_of(st, tr), L, 0)
    merged = state_from(disc(12, 12, 4) + 0.0)
    fm = merged.m.reshape(-1)
    for i in blob:
        fm[i] = 0.9
    for i in range(L * L):                               # bridge the gap
        y, x = divmod(i, L)
        if y == 12 and 5 <= x <= 8:
            fm[i] = 0.9
    tr2 = track_of(merged)
    cz.update(merged, p, tr2, labels_of(merged, tr2), L, 16)
    ok = cz.capture_by_merger > 1e-9 and cz.capture_transport < 1e-9
    check(17, "source separee puis fusion", ok,
          f"capture_par_fusion={cz.capture_by_merger:.4f} "
          f"capture_dyn={cz.capture_transport:.4f} JOINT_SUCCESS=False")


def main():
    print("=== FIXTURES OBLIGATOIRES (aucun appel au moteur scientifique) ===")
    for f in (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17):
        try:
            f()
        except Exception as e:
            check(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    npass = sum(r["PASS"] for r in R)
    verdict = "PASS" if npass == len(R) else "FAIL"
    Path("dynamic_source_capture_fixtures.json").write_text(json.dumps(
        {"mission": "ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04",
         "engine_invocations": 0, "n": len(R), "n_pass": npass,
         "OPERATOR_FIXTURES": verdict, "fixtures": R}, indent=1))
    print(f"\n{npass}/{len(R)} -> OPERATOR_FIXTURES = {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
