import numpy as np
from dataclasses import replace
from edlab.substrates.chemotaxis.engine import ChemoEngine, CHState
from edlab.substrates.chemotaxis.diagnostics import (radius_of_gyration, participation_ratio,
                                                     entity_radius_of_gyration, r7_diagnostics)
from edlab.experiments.exp_ch_00 import chemo_law, seed_state, TRACER


def test_global_rg_cannot_detect_compact_multispot():
    """A priori proof that the GLOBAL Rg criterion cannot fire: 30 PERFECTLY compact spots score the same as a
    uniform field. This is why Rg is measured PER ENTITY."""
    n = 64
    ys, xs = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    rng = np.random.default_rng(0)
    rho = np.zeros((n, n))
    for _ in range(30):
        cy, cx = rng.integers(0, n, 2)
        d = np.sqrt((((ys - cy + n // 2) % n) - n // 2) ** 2 + (((xs - cx + n // 2) % n) - n // 2) ** 2)
        rho = np.maximum(rho, (d <= 2.0).astype(float))
    uni = np.full((n, n), rho.mean())
    assert radius_of_gyration(rho) > 20 and radius_of_gyration(uni) > 20      # indistinguishable
    assert participation_ratio(rho) < 0.15 and participation_ratio(uni) > 0.99  # PR DOES separate
    e_rg, e_n = entity_radius_of_gyration(rho, 0.5)
    assert e_rg < 3.0 and e_n > 0                                             # per-entity Rg DOES separate


def test_density_bound_is_an_invariant():
    sp = chemo_law(2)
    eng = ChemoEngine(sp, TRACER)
    st = seed_state(sp, TRACER, 5001)
    for _ in range(500):
        st = eng.step(st)
        assert st.rho.min() >= -1e-12
        assert st.rho.max() <= sp.rho_max + 1e-9      # volume-filling bound holds for flux AND growth


def test_cohorts_partition_rho_exactly_and_are_passive_and_deterministic():
    sp = chemo_law(2)
    eng = ChemoEngine(sp, TRACER)
    a = seed_state(sp, TRACER, 7001)
    b = seed_state(sp, TRACER, 7001)
    b.C = b.C[::-1].copy()
    for _ in range(200):
        a = eng.step(a)
        b = eng.step(b)
        assert np.abs(a.C.sum(0) - a.rho).max() < 1e-12
    assert np.array_equal(a.rho, b.rho) and np.array_equal(a.c, b.c) and np.array_equal(a.N, b.N)


def test_exact_closed_limit_conserves_mass():
    sp = replace(chemo_law(2), g0=0.0, k=0.0)
    assert sp.is_closed
    eng = ChemoEngine(sp, TRACER)
    st = seed_state(sp, TRACER, 7002)
    m0 = st.rho.sum()
    for _ in range(300):
        st = eng.step(st)
    assert abs(st.rho.sum() - m0) / m0 < 1e-13


def test_uniform_state_stays_exactly_uniform():
    sp = chemo_law(2)
    eng = ChemoEngine(sp, TRACER)
    n = sp.size
    C = np.concatenate([np.full((1, n, n), 0.25), np.zeros((TRACER.n_cohorts - 1, n, n))])
    u = CHState(np.full((n, n), 0.25), np.zeros((n, n)), np.full((n, n), sp.N0), C, 0)
    for _ in range(200):
        u = eng.step(u)
    assert np.ptp(u.rho) == 0.0 and np.ptp(u.c) == 0.0 and np.ptp(u.N) == 0.0


def test_cohesion_is_caused_by_the_chemotactic_field():
    """chi0 = 0 removes chemotaxis: localization MUST fail. Cohesion is caused, not assumed."""
    sp = chemo_law(2)
    z = replace(sp, chi0=0.0)
    for spec, want in ((sp, True), (z, False)):
        eng = ChemoEngine(spec, TRACER)
        st = seed_state(spec, TRACER, 5001)
        for _ in range(2000):
            st = eng.step(st)
        assert r7_diagnostics(st, spec.rho_max)["localized"] is want
