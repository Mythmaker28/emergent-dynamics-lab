import numpy as np
from edlab.substrates.reaction_diffusion.engine import RDState
from edlab.experiments.exp_rd_04 import scramble_cargo, mass_match, mcnemar_exact, newcombe_diff


def _st(seed=0, n=16, c=3):
    r = np.random.default_rng(seed)
    return RDState(r.random((n, n)), r.random((n, n)), r.random((c, n, n)), r.random((c, n, n)), 0)


def test_scrambled_cargo_matches_every_low_order_statistic_exactly():
    st = _st()
    sup = np.zeros((16, 16), dtype=bool); sup[3:8, 3:8] = True
    sc = scramble_cargo(st, sup, np.random.default_rng(7))
    assert np.isclose(sc.U[sup].sum(), st.U[sup].sum())          # total U mass
    assert np.isclose(sc.V[sup].sum(), st.V[sup].sum())          # total V mass
    assert np.allclose(sc.CU[:, sup].sum(1), st.CU[:, sup].sum(1))   # per-cohort mass
    assert np.allclose(sc.CV[:, sup].sum(1), st.CV[:, sup].sum(1))
    assert np.allclose(np.sort(sc.V[sup]), np.sort(st.V[sup]))   # full multiset of per-cell values
    assert not np.array_equal(sc.V[sup], st.V[sup])              # organization IS destroyed
    assert np.array_equal(sc.V[~sup], st.V[~sup])                # nothing outside the support is touched


def test_mass_match_equalises_mass_and_composition_and_reports_non_conservation():
    st = _st(1)
    ref = np.zeros((16, 16), dtype=bool); ref[2:6, 2:6] = True
    src = np.zeros((16, 16), dtype=bool); src[10:14, 10:14] = True
    out, meta = mass_match(st, src, ref)
    assert np.isclose(out.U[src].sum(), st.U[ref].sum())
    assert np.isclose(out.V[src].sum(), st.V[ref].sum())
    fr = st.CV[:, ref].sum(1); fr = fr / fr.sum()
    fo = out.CV[:, src].sum(1); fo = fo / fo.sum()
    assert np.allclose(fr, fo)                                    # cohort composition matched
    assert "delta_U_mass_injected" in meta and "delta_V_mass_injected" in meta   # non-conservation reported


def test_mcnemar_exact_and_newcombe():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(6, 0) < 0.05          # 6 discordant, all one way -> significant
    assert mcnemar_exact(3, 3) == 1.0
    lo, hi = newcombe_diff(10, 40, 0, 120)
    assert lo > 0.10 and hi < 1.0
