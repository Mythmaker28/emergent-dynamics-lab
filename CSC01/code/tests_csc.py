"""CSC01 integrity harness. Runs in STATIC mode: no world is advanced, no start is opened.

Everything here is checked against an independent computation or against an exactly known
value, never against itself.
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import observe as OBS            # noqa: E402  the ORR01 pure-python torus labeller
import guard_csc as GC           # noqa: E402
import spatial as SP             # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"test": name, "PASS": bool(ok), "detail": str(detail)[:300]})
    print(("PASS  " if ok else "FAIL  ") + name + (("   " + str(detail)[:160]) if detail else ""))
    return bool(ok)


# ------------------------------------------------------------------ T1 differential labeller
def t1_components_match_orr01():
    rng = np.random.default_rng(20260814)
    worst = None
    for trial in range(60):
        L = 36
        p = rng.uniform(0.05, 0.6)
        mask = rng.random((L, L)) < p
        comps_ref, lab_ref = OBS.components_torus(mask)
        lab_new, sizes = SP.torus_components(mask)
        # same partition: compare the induced equivalence relation, not the label numbering
        ok = (lab_new >= 0).sum() == mask.sum() and len(comps_ref) == len(sizes)
        if ok:
            ref_sets = sorted(sorted(c) for c in comps_ref)
            new_sets = sorted(sorted(map(tuple, np.argwhere(lab_new == i).tolist()))
                              for i in range(len(sizes)))
            new_sets = [[tuple(c) for c in s] for s in new_sets]
            ok = ref_sets == new_sets
        if not ok:
            worst = {"trial": trial, "p": p, "n_ref": len(comps_ref), "n_new": len(sizes)}
            break
    return check("T1 torus labeller agrees with the ORR01 pure-python labeller on 60 random "
                 "masks", worst is None, worst or "")


# ------------------------------------------------------------------ T2 winding and percolation
def t2_winding():
    L = 36
    ok = True
    m = np.zeros((L, L), bool); m[7, :] = True                    # a full row: wraps in x
    lab, _ = SP.torus_components(m)
    wy, wx, v = SP.winding_vectors(m, lab, 0)
    ok &= (not wy) and wx and any(t[1] != 0 for t in v)
    m = np.zeros((L, L), bool); m[:, 11] = True                   # a full column: wraps in y
    lab, _ = SP.torus_components(m)
    wy, wx, v = SP.winding_vectors(m, lab, 0)
    ok &= wy and (not wx)
    m = np.zeros((L, L), bool); m[5:9, 5:9] = True                # a blob: no winding
    lab, _ = SP.torus_components(m)
    wy, wx, v = SP.winding_vectors(m, lab, 0)
    ok &= (not wy) and (not wx) and v == []
    m = np.zeros((L, L), bool)                                    # a blob straddling the seam
    m[np.ix_([34, 35, 0, 1], [34, 35, 0, 1])] = True
    lab, sizes = SP.torus_components(m)
    ok &= len(sizes) == 1 and sizes[0] == 16
    wy, wx, _ = SP.winding_vectors(m, lab, 0)
    ok &= (not wy) and (not wx)
    return check("T2 winding: full row wraps in x, full column in y, a blob never, a blob "
                 "across the seam is ONE component and does not wrap", ok)


# ------------------------------------------------------------------ T3 Frechet centre
def t3_frechet_centre():
    L = 36
    ok = True
    f = np.zeros((L, L)); f[np.ix_([34, 35, 0, 1, 2], [17, 18, 19])] = 1.0   # straddles the seam
    cy, cx, _ = SP.frechet_centre(f)
    ok &= (cy == 0 and cx == 18)
    f = np.zeros((L, L)); f[10, 10] = 7.0                                     # a point mass
    cy, cx, inert = SP.frechet_centre(f)
    ok &= (cy, cx) == (10, 10) and abs(inert) < 1e-12
    f = np.zeros((L, L)); f[3, 3] = 1.0; f[3, 21] = 1.0        # antipodal pair: degenerate for
    cy, cx, _ = SP.frechet_centre(f)                            # the angular mean, defined here
    ok &= cy == 3 and cx in (3, 12, 21, 30)                     # any of the tied minima
    ang = SP.angular_centre(np.array([3, 21]), np.array([1.0, 1.0]), L)
    ok &= np.isfinite(ang)
    return check("T3 Frechet centre exact on a seam-straddling mass, on a point mass, and "
                 "defined on an antipodal pair", ok, f"centre={(cy, cx)} angular_x={ang:.3f}")


# ------------------------------------------------------------------ T4 Rg against exact values
def t4_rg_exact():
    L = 36
    # uniform mass: E[d^2] per axis = (1/L) sum_k min(k, L-k)^2
    k = np.arange(L)
    e1 = float((np.minimum(k, L - k) ** 2).mean())
    exact_uniform = float(np.sqrt((2.0 * e1) / 2.0))
    f = np.ones((L, L))
    got = SP.rg_pairwise(f)
    ok = abs(got - exact_uniform) < 1e-9
    # a compact Gaussian blob: pairwise and centred forms must agree
    yy, xx = np.mgrid[0:L, 0:L]
    g = np.exp(-(((yy - 18.0) ** 2 + (xx - 18.0) ** 2) / (2 * 2.0 ** 2)))
    g[g < 1e-9] = 0.0
    cy, cx, _ = SP.frechet_centre(g)
    d = SP.dist_field(L, cy, cx)
    rg_centred = float(np.sqrt((g * d ** 2).sum() / g.sum()))
    rg_pair = SP.rg_pairwise(g)
    ok &= abs(rg_centred - rg_pair) / rg_centred < 0.02
    # two point masses distance 6 apart: Rg_pairwise = 3 exactly
    f2 = np.zeros((L, L)); f2[10, 10] = 1.0; f2[10, 16] = 1.0
    ok &= abs(SP.rg_pairwise(f2) - 3.0) < 1e-12
    return check("T4 Rg_pairwise: exact on uniform mass, equals the centred form on a compact "
                 "blob, exactly 3 for two masses 6 apart", ok,
                 f"uniform got={got:.9f} exact={exact_uniform:.9f} "
                 f"blob centred={rg_centred:.4f} pair={rg_pair:.4f}")


# ------------------------------------------------------------------ T5 geodesic diameter
def t5_geodesic():
    L = 36
    m = np.zeros((L, L), bool); m[5, 4:14] = True                 # a straight bar of 10 cells
    lab, _ = SP.torus_components(m)
    d, exact = SP.geodesic_diameter(lab, 0)
    ok = d == 9 and exact
    m = np.zeros((L, L), bool)                                    # an L-shaped path of 11 cells:
    m[5, 4:10] = True; m[5:11, 9] = True                          # (5,4)..(5,9) then (5,9)..(10,9)
    lab, _ = SP.torus_components(m)                               # 5 steps + 5 steps = 10 EDGES
    d2, _ = SP.geodesic_diameter(lab, 0)
    ok &= d2 == 10
    m = np.zeros((L, L), bool); m[5, :] = True                    # a full ring: diameter L/2
    lab, _ = SP.torus_components(m)
    d3, _ = SP.geodesic_diameter(lab, 0)
    ok &= d3 == L // 2
    return check("T5 geodesic diameter counts EDGES: bar of 10 cells -> 9, L-path of 11 cells "
                 "-> 10, full ring -> L/2", ok, f"{d} {d2} {d3}")


# ------------------------------------------------------------------ T6 radii and n_eff
def t6_radii_neff():
    L = 36
    f = np.zeros((L, L)); f[18, 18] = 10.0
    r = SP.radii_quantiles(f, 18, 18)
    ok = all(abs(v) < 1e-12 for v in r.values())
    f = np.zeros((L, L))                                          # a ring of radius 5
    yy, xx = np.mgrid[0:L, 0:L]
    d = np.sqrt((yy - 18.0) ** 2 + (xx - 18.0) ** 2)
    f[(d > 4.5) & (d < 5.5)] = 1.0
    r = SP.radii_quantiles(f, 18, 18)
    ok &= all(4.4 < v < 5.6 for v in r.values())
    ok &= abs(SP.effective_n([1, 1, 1, 1]) - 4.0) < 1e-12
    ok &= abs(SP.effective_n([10, 0.0001]) - 1.0) < 1e-3
    ok &= abs(SP.effective_n([5, 5]) - 2.0) < 1e-12
    return check("T6 radii of a point mass are 0, of a ring of radius 5 are ~5; N_eff is 4, 2 "
                 "and ~1 on the declared cases", ok)


# ------------------------------------------------------------------ T7 guard separation
def t7_guard():
    ok = True
    GC.set_static_mode()
    try:
        GC.advance(None, 1)
        ok = False
    except GC.ProtocolError:
        pass
    GC.set_experiment_mode()
    try:
        with GC.start("not_a_class", "x", 1):
            pass
        ok = False
    except GC.ProtocolError:
        pass
    ok &= "raw_replay" in GC.NON_SCIENTIFIC and "cost_probe" in GC.NON_SCIENTIFIC
    ok &= "confirmation" not in GC.NON_SCIENTIFIC and "calibration" not in GC.NON_SCIENTIFIC
    GC.set_static_mode()
    return check("T7 guard: STATIC forbids advance, undeclared classes are refused, raw_replay "
                 "is non-scientific and calibration/confirmation are not", ok)


# ------------------------------------------------------------------ T8 frame_report invariance
def t8_translation_invariance():
    """Every observable must be invariant under a rigid translation of the torus."""
    rng = np.random.default_rng(7)
    L = 36
    nX = np.zeros((L, L), np.int64)
    yy, xx = np.mgrid[0:L, 0:L]
    g = np.exp(-(((yy - 18.0) ** 2 + (xx - 18.0) ** 2) / (2 * 2.5 ** 2))) * 6
    nX = rng.poisson(g).astype(np.int64)
    nY = np.zeros((L, L), np.int64); nY[18, 18] = 1
    keys = ("r50", "r80", "r90", "Rg_pairwise", "main_mass_fraction", "n_eff_components",
            "n_components", "main_N_X", "main_geodesic_diameter", "organiser_to_centre",
            "core_fraction_within_2ellX", "Rg_ORR01_angular")
    a = SP.frame_report(nX, nY, 2.5)
    ok = True
    worst = ""
    for sy, sx in ((7, 0), (0, 13), (18, 18), (-5, 31)):
        b = SP.frame_report(np.roll(np.roll(nX, sy, 0), sx, 1),
                            np.roll(np.roll(nY, sy, 0), sx, 1), 2.5)
        for k in keys:
            va, vb = a[k], b[k]
            if isinstance(va, float) and np.isnan(va) and np.isnan(vb):
                continue
            if abs(float(va) - float(vb)) > 1e-9:
                ok = False
                worst = f"{k} {va} vs {vb} shift={(sy, sx)}"
    return check("T8 every frame observable is invariant under rigid translation of the torus",
                 ok, worst)


# ------------------------------------------------------------------ T9 known-answer states
def t9_known_states():
    L = 36
    ok = True
    nY = np.zeros((L, L), np.int64); nY[18, 18] = 1
    nX = np.zeros((L, L), np.int64); nX[17:20, 17:20] = 5        # one compact block
    r = SP.frame_report(nX, nY, 2.5)
    ok &= r["n_components"] == 1 and abs(r["main_mass_fraction"] - 1.0) < 1e-12
    ok &= r["r90"] <= 1.5 and not r["any_component_wraps"]
    nX2 = np.zeros((L, L), np.int64)                             # mass spread over the torus
    nX2[::4, ::4] = 5
    r2 = SP.frame_report(nX2, nY, 2.5)
    ok &= r2["n_eff_components"] > 40 and r2["r80"] > 10
    ok &= r2["Rg_pairwise"] > r["Rg_pairwise"] * 3
    return check("T9 a compact block gives one component, r90 <= 1.5; a spread field gives "
                 "N_eff > 40 and r80 > 10", ok,
                 f"block r90={r['r90']:.2f} Rg={r['Rg_pairwise']:.2f} ; "
                 f"spread N_eff={r2['n_eff_components']:.1f} r80={r2['r80']:.2f} "
                 f"Rg={r2['Rg_pairwise']:.2f}")


# ------------------------------------------------------------------ T10/T11 gate defects
class _Stub:
    """The minimum surface `observe.component_report` reads. No dynamics, no randomness."""

    def __init__(self, nX, nY, cap=16):
        self.L = nX.shape[0]
        self.n = {"X": nX, "Y": nY,
                  "SX": np.zeros_like(nX), "SY": np.zeros_like(nX),
                  "WX": np.zeros_like(nX), "WY": np.zeros_like(nX)}
        self.step = 0
        self._cap = cap

    def free(self):
        return self._cap - sum(self.n[k] for k in ("X", "Y", "SX", "SY", "WX", "WY"))


def t10_wrap_flag_is_an_extent_proxy():
    """CONSTRUCTIVE: a compact core with one thin filament trips the ORR01 `wraps` flag while
    the component does not wind at all."""
    L = 36
    nX = np.zeros((L, L), np.int64)
    nY = np.zeros((L, L), np.int64)
    nX[16:21, 16:21] = 4                      # a 5x5 core, 100 molecules, radius ~1.6
    nY[18, 18] = 1
    for x in range(21, 29):                   # a one-cell filament of single molecules
        nX[18, x] = 1
    w = _Stub(nX, nY)
    rep = OBS.component_report(w)
    main = rep["main"]
    lab, _ = SP.torus_components((nX + nY) > 0)
    cid = int(lab[18, 18])
    wy, wx, vecs = SP.winding_vectors((nX + nY) > 0, lab, cid)
    fr = SP.frame_report(nX, nY, 2.5)
    ok = bool(main["wraps"]) and (not wy) and (not wx) and vecs == []
    ok &= main["radius_of_gyration"] < 4.0            # the body of the component is compact
    ok &= fr["r80"] < 3.0
    return check("T10 CONSTRUCTIVE: the ORR01 `wraps` flag fires on a compact non-winding "
                 "component (extent proxy), while the exact winding test says no wrap", ok,
                 f"ORR01 wraps={main['wraps']} extent={main['extent']:.2f} "
                 f"Rg={main['radius_of_gyration']:.2f} true winding=({wy},{wx}) "
                 f"r80={fr['r80']:.2f}")


def t11_main_component_criterion_is_all_or_nothing():
    """CONSTRUCTIVE: a live, compact core of 48 molecules all within 2*ell_X of its centre fails
    the ORR01 criterion main_N_X >= N_KEEP/2 = 25 because a single empty cell splits it in two."""
    L = 36
    nX = np.zeros((L, L), np.int64)
    nY = np.zeros((L, L), np.int64)
    nX[17:19, 16:18] = 6                      # 24 molecules
    nX[17:19, 19:21] = 6                      # 24 molecules, one empty column between them
    nY[17, 16] = 1
    w = _Stub(nX, nY)
    rep = OBS.component_report(w)
    main = rep["main"]
    fr = SP.frame_report(nX, nY, 2.5)
    ok = (main["N_X"] == 24) and (24 < 50 * 0.5)                 # the ORR01 criterion fails
    ok &= fr["core_fraction_within_2ellX"] >= 0.99               # the core manifestly exists
    ok &= fr["r80"] <= 3.0 and int(nX.sum()) == 48
    return check("T11 CONSTRUCTIVE: a compact core of 48 molecules, entirely inside 2*ell_X, "
                 "fails the ORR01 all-or-nothing criterion main_N_X >= 25 because one empty "
                 "column splits it", ok,
                 f"ORR01 main_N_X={main['N_X']} threshold=25 | core fraction within 2*ell_X="
                 f"{fr['core_fraction_within_2ellX']:.3f} r80={fr['r80']:.2f} N_X={int(nX.sum())}")


def t12_n3_profile_is_exact():
    """The exact point-source null must reproduce its own analytic second moment,
       <r^2> = 2 a (1 - mu) / mu  with a = 2 q (1 - q), up to the torus truncation."""
    import nulls as NU
    L, p_hop, mu = 36, 0.10263340389897246, 0.004
    q = p_hop / 4.0
    a = 2 * q * (1 - q)
    prof = NU.n3_profile(L, p_hop, mu)
    d = SP.dist_field(L, 0, 0)
    got = float((prof * d ** 2).sum())
    analytic_infinite_lattice = 2 * a * (1 - mu) / mu
    ok = abs(got - analytic_infinite_lattice) / analytic_infinite_lattice < 0.05
    ok &= abs(prof.sum() - 1.0) < 1e-12 and (prof >= 0).all()
    ell = float(np.sqrt(a / 2.0 / mu))
    ok &= abs(ell - 2.5) < 1e-9
    return check("T12 the exact point-source null reproduces <r^2> = 2a(1-mu)/mu and "
                 "ell_X = sqrt(D/mu) = 2.5 exactly", ok,
                 f"<r^2> torus={got:.4f} analytic={analytic_infinite_lattice:.4f} "
                 f"D={a/2:.6f} ell_X={ell:.6f}")


def main():
    GC.set_static_mode()
    t1_components_match_orr01()
    t2_winding()
    t3_frechet_centre()
    t4_rg_exact()
    t5_geodesic()
    t6_radii_neff()
    t7_guard()
    t8_translation_invariance()
    t9_known_states()
    t10_wrap_flag_is_an_extent_proxy()
    t11_main_component_criterion_is_all_or_nothing()
    t12_n3_profile_is_exact()
    allp = all(r["PASS"] for r in RESULTS)
    print()
    print("tests run          %d" % len(RESULTS))
    print("SCIENTIFIC_RUNS_USED %d" % GC.scientific_runs_used())
    print("ALL_PASS = %s" % allp)
    json.dump({"results": RESULTS, "ALL_PASS": allp,
               "SCIENTIFIC_RUNS_USED": GC.scientific_runs_used()},
              open("/home/claude/CSC01/out/_tests_stage_a.json", "w"), indent=1)
    return 0 if allp else 1


if __name__ == "__main__":
    sys.exit(main())
