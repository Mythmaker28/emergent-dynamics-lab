import numpy as np
from edlab.substrates.motile_polar.engine import MotilePolarSpec, MotilePolarEngine, advect
from edlab.substrates.motile_polar.observables import _components
from edlab.experiments.exp_mo_00 import seed_state, TRACER, SPEC, DET, PHE
from edlab.experiments.exp_mo_00_gate0 import scramble, swap_support, assert_interventions, _polar_order
from edlab.substrates.motile_polar.observables import detect


def _ref_components(mask):
    n = mask.shape[0]; lab = -np.ones((n, n), int); out = []
    for sy in range(n):
        for sx in range(n):
            if not mask[sy, sx] or lab[sy, sx] >= 0: continue
            cid = len(out); st = [(sy, sx)]; lab[sy, sx] = cid; cc = []
            while st:
                y, x = st.pop(); cc.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = (y + dy) % n, (x + dx) % n
                    if mask[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = cid; st.append((ny, nx))
            out.append(sorted(cc))
    return sorted(out)


def test_periodic_labeller_matches_reference_flood_fill():
    rng = np.random.default_rng(0)
    for _ in range(10):
        m = rng.random((32, 32)) < 0.25
        assert sorted([sorted(map(tuple, c)) for c in _components(m)]) == _ref_components(m)


def test_advection_is_mass_conserving_and_identical_across_fields():
    rng = np.random.default_rng(1)
    f = rng.random((3, 16, 16))
    vy, vx = rng.normal(0, .3, (16, 16)), rng.normal(0, .3, (16, 16))
    a = advect(f, vy, vx, 1.0)
    assert np.allclose(a.sum((1, 2)), f.sum((1, 2)))
    assert np.allclose(a[0] + a[1], advect((f[0] + f[1])[None], vy, vx, 1.0)[0])


def test_cohorts_partition_rho_exactly_and_are_passive():
    eng = MotilePolarEngine(SPEC, TRACER)
    s = seed_state(SPEC, TRACER, 11)
    t = s.copy(); t.C = t.C[::-1].copy()
    for _ in range(60):
        s = eng.step(s); t = eng.step(t)
        assert np.abs(s.C.sum(0) - s.rho).max() / s.rho.sum() < 1e-12
    assert np.array_equal(s.rho, t.rho) and np.array_equal(s.py, t.py) and np.array_equal(s.px, t.px)


def test_exact_closed_limit_conserves_material():
    sp = MotilePolarSpec(F=0.0, g0=0.0, k=0.0)
    assert sp.is_closed
    eng = MotilePolarEngine(sp, TRACER)
    s = seed_state(sp, TRACER, 12); m0 = s.rho.sum()
    for _ in range(100):
        s = eng.step(s)
    assert abs(s.rho.sum() - m0) / m0 < 1e-12


def test_homogeneous_state_stays_exactly_uniform():
    eng = MotilePolarEngine(SPEC, TRACER)
    n = SPEC.size
    C = np.concatenate([np.full((1, n, n), 0.5), np.zeros((TRACER.n_cohorts - 1, n, n))])
    from edlab.substrates.motile_polar.engine import MPState
    u = MPState(np.full((n, n), 0.5), np.zeros((n, n)), np.zeros((n, n)), np.full((n, n), SPEC.R0), C, 0)
    for _ in range(50):
        u = eng.step(u)
    assert np.ptp(u.rho) == 0.0 and np.ptp(u.R) == 0.0


def test_zero_displacement_is_exact_no_op():
    s = seed_state(SPEC, TRACER, 13)
    sup = np.zeros((SPEC.size, SPEC.size), dtype=bool); sup[10:16, 10:16] = True
    o = swap_support(s, sup, 0, 0)
    assert np.array_equal(o.rho, s.rho) and np.array_equal(o.R, s.R)
    assert np.array_equal(o.py, s.py) and np.array_equal(o.px, s.px) and np.array_equal(o.C, s.C)


def test_scramble_preserves_all_declared_invariants_and_destroys_organization():
    eng = MotilePolarEngine(SPEC, TRACER)
    s = seed_state(SPEC, TRACER, 14)
    for _ in range(300):
        s = eng.step(s)
    cand = max(detect(s, DET, PHE), key=lambda e: e.size)
    sup = np.zeros((SPEC.size, SPEC.size), dtype=bool)
    sup[cand.cells[:, 0], cand.cells[:, 1]] = True
    sc = scramble(s, sup, np.random.default_rng(5))
    ys, xs = np.nonzero(sup); w = s.rho[ys, xs] + 1e-12
    assert np.isclose(sc.rho[ys, xs].sum(), s.rho[ys, xs].sum())
    assert np.isclose(sc.R[ys, xs].sum(), s.R[ys, xs].sum())
    assert np.allclose(sc.C[:, ys, xs].sum(1), s.C[:, ys, xs].sum(1))
    assert np.allclose(np.sort(sc.rho[ys, xs]), np.sort(s.rho[ys, xs]))
    assert np.allclose(np.sort(np.hypot(sc.py[ys, xs], sc.px[ys, xs])),
                       np.sort(np.hypot(s.py[ys, xs], s.px[ys, xs])))
    assert np.allclose(sc.C.sum(0), sc.rho)                      # cell-wise partition survives
    assert _polar_order(sc.py[ys, xs], sc.px[ys, xs], w) < 0.5 * _polar_order(s.py[ys, xs], s.px[ys, xs], w)
    # and the full assertion battery used by the experiment passes
    assert_interventions(s, sup, s.copy(), swap_support(s, sup, 0, 0),
                         swap_support(s, sup, 18, 18), swap_support(sc, sup, 18, 18))
