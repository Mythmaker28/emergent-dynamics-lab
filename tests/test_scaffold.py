"""SYNTHETIC MUST-PASS / MUST-FAIL cases for every EXP-SC-00 metric, plus engine invariants."""

import numpy as np
from dataclasses import replace

from edlab.substrates.scaffold.engine import ScaffoldSpec, ScaffoldEngine, SCState
from edlab.substrates.scaffold.observables import SCDetectionSpec, detect
from edlab.experiments.exp_sc_00 import seed_state, TRACER, SPEC

DET = SCDetectionSpec()
N = 48


def _droplet(kind: str) -> SCState:
    ys, xs = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    d = np.sqrt((ys - 24.0) ** 2 + (xs - 24.0) ** 2)
    disc = d <= 8.0
    rho = np.where(disc, 0.8, 0.0)
    hi, lo = 1.6, 0.1
    if kind == "uniform_u":
        u = np.where(disc, hi, 0.0); v = np.where(disc, lo, 0.0)
    elif kind == "uniform_v":
        u = np.where(disc, lo, 0.0); v = np.where(disc, hi, 0.0)
    elif kind == "janus":
        u = np.where(disc & (xs < 24), hi, lo) * disc; v = np.where(disc & (xs < 24), lo, hi) * disc
    elif kind == "core_shell":
        u = np.where(disc & (d <= 4), hi, lo) * disc; v = np.where(disc & (d <= 4), lo, hi) * disc
    elif kind == "two_domain":
        m = disc & (((xs < 20) & (ys < 24)) | ((xs > 27) & (ys > 24)))
        u = np.where(m, hi, lo) * disc; v = np.where(m, lo, hi) * disc
    else:
        raise ValueError(kind)
    C = np.stack([rho] + [np.zeros((N, N))] * 11)
    return SCState(rho, rho * u, rho * v, np.zeros((N, N)), np.ones((N, N)), C, np.zeros((N, N)), 0)


def _p(kind):
    e = detect(_droplet(kind), DET)
    assert len(e) == 1
    return e[0]


def test_MUST_FAIL_uniform_interior_has_zero_internal_organization():
    """A droplet whose interior is uniform (all-u or all-v) must score ZERO internal heterogeneity, regardless of
    WHICH state it is in. Bulk state is composition, not organization."""
    for k in ("uniform_u", "uniform_v"):
        p = _p(k).phenotype
        assert p[0] < 1e-9, (k, p)          # internal_heterogeneity
        assert p[2] < 1e-9                  # interface_fraction
        assert p[4] < 1e-9                  # janus_sig


def test_MUST_PASS_structured_interiors_are_detected():
    for k in ("janus", "core_shell", "two_domain"):
        p = _p(k).phenotype
        assert p[0] > 0.3, (k, p)           # internal_heterogeneity fires


def test_MUST_PASS_internal_morphologies_are_mutually_distinguishable():
    ps = {k: _p(k).phenotype for k in ("uniform_u", "janus", "core_shell", "two_domain")}
    ks = list(ps)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            assert np.linalg.norm(ps[ks[i]] - ps[ks[j]]) > 0.2, (ks[i], ks[j])


def test_bulk_state_separates_uniform_u_from_uniform_v_only_in_the_SECONDARY_phenotype():
    """PRIMARY (organizational) must NOT distinguish all-u from all-v; SECONDARY (adds bulk state) MUST.
    This is the compositional/organizational split, made explicit and testable."""
    a, b = _p("uniform_u"), _p("uniform_v")
    assert np.allclose(a.phenotype, b.phenotype, atol=1e-8)
    assert abs(a.phenotype_sec[-1] - b.phenotype_sec[-1]) > 1.0
    assert a.mean_sig > 0.8 and b.mean_sig < -0.8


def test_phenotype_is_translation_and_rotation_invariant():
    base = _droplet("janus")
    e0 = detect(base, DET)[0]
    r = SCState(np.roll(base.rho, (6, -4), (0, 1)), np.roll(base.U, (6, -4), (0, 1)),
                np.roll(base.V, (6, -4), (0, 1)), base.c, base.N,
                np.roll(base.C, (6, -4), (1, 2)), base.uptake, 0)
    assert np.allclose(e0.phenotype, detect(r, DET)[0].phenotype, atol=1e-9)
    q = SCState(np.rot90(base.rho), np.rot90(base.U), np.rot90(base.V), base.c, base.N,
                np.stack([np.rot90(x) for x in base.C]), base.uptake, 0)
    assert np.allclose(e0.phenotype, detect(q, DET)[0].phenotype, atol=0.05)


def test_O3_internal_fields_alone_cannot_manufacture_an_entity():
    """MUST-FAIL case for the detector: violently structured u/v on a SUB-THRESHOLD scaffold -> no entity."""
    rng = np.random.default_rng(0)
    rho = np.full((N, N), 0.15)
    u = np.where(rng.random((N, N)) < 0.5, 2.0, 0.05)
    C = np.stack([rho] + [np.zeros((N, N))] * 11)
    st = SCState(rho, rho * u, rho * (2.05 - u), np.zeros((N, N)), np.ones((N, N)), C, np.zeros((N, N)), 0)
    assert detect(st, DET) == []


def test_uptake_observable_responds_to_internal_state_and_is_inert_at_beta_zero():
    """MUST-PASS / MUST-FAIL for the BEHAVIOURAL observable itself, before it is used in O4."""
    for spec, want_change in ((SPEC, True), (replace(SPEC, beta=0.0), False)):
        eng = ScaffoldEngine(spec, TRACER)
        base = _droplet("uniform_u")
        flip = base.copy(); flip.U, flip.V = base.V.copy(), base.U.copy()
        ups = []
        for s0 in (base, flip):
            s = s0.copy()
            for _ in range(20):
                s = eng.step(s)
            es = detect(s, DET, spec.rho_max)
            ups.append(float(np.mean([e.specific_uptake for e in es])) if es else 0.0)
        rel = abs(ups[1] - ups[0]) / (abs(ups[0]) + 1e-12)
        assert (rel > 0.10) is want_change, (spec.beta, ups, rel)


def test_engine_invariants():
    eng = ScaffoldEngine(SPEC, TRACER)
    st = seed_state(SPEC, TRACER, 3)
    for _ in range(150):
        st = eng.step(st)
        assert np.abs(st.C.sum(0) - st.rho).max() < 1e-12
        assert st.rho.max() <= SPEC.rho_max + 1e-9 and st.rho.min() >= -1e-12
    cl = replace(SPEC, g0=0.0, k=0.0)
    ce = ScaffoldEngine(cl, TRACER)
    cs = seed_state(cl, TRACER, 4)
    m0 = cs.rho.sum()
    for _ in range(200):
        cs = ce.step(cs)
    assert abs(cs.rho.sum() - m0) / m0 < 1e-13
