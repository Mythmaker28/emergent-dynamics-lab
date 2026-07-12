import numpy as np
from edlab.experiments.exp_rd_03 import dilate_periodic, support_radii, _swap_support, enroll_reference
from edlab.substrates.reaction_diffusion.engine import RDState


def test_supports_are_nested_and_mechanistic():
    for law in (1, 5, 7, 10, 11, 13, 14, 16, 19):
        r = support_radii(law)
        assert r["S0_mask"] == 0.0 < r["S1_small_halo"]
        assert r["S2_one_diffusion_length"] <= r["S3_two_diffusion_lengths"]
        assert abs(r["S2_one_diffusion_length"] - np.ceil(r["ell"])) < 1e-9
        m = np.zeros((32, 32), dtype=bool); m[10:14, 10:14] = True
        prev = dilate_periodic(m, 0)
        for k in ("S1_small_halo", "S2_one_diffusion_length", "S3_two_diffusion_lengths"):
            cur = dilate_periodic(m, r[k])
            assert cur.sum() >= m.sum()
        assert dilate_periodic(m, r["S3_two_diffusion_lengths"]).sum() >= \
               dilate_periodic(m, r["S2_one_diffusion_length"]).sum()


def test_zero_displacement_is_exact_no_op():
    rng = np.random.default_rng(0)
    st = RDState(rng.random((16, 16)), rng.random((16, 16)), rng.random((3, 16, 16)), rng.random((3, 16, 16)), 0)
    sup = np.zeros((16, 16), dtype=bool); sup[4:8, 4:8] = True
    out = _swap_support(st, sup, 0, 0)
    for a, b in ((out.U, st.U), (out.V, st.V), (out.CU, st.CU), (out.CV, st.CV)):
        assert np.array_equal(a, b)


def test_swap_is_conservative_and_moves_cohorts_with_matter():
    rng = np.random.default_rng(1)
    st = RDState(rng.random((16, 16)), rng.random((16, 16)), rng.random((3, 16, 16)), rng.random((3, 16, 16)), 0)
    sup = np.zeros((16, 16), dtype=bool); sup[2:5, 2:5] = True
    out = _swap_support(st, sup, 6, 6)
    assert np.isclose(out.U.sum(), st.U.sum()) and np.isclose(out.V.sum(), st.V.sum())
    assert np.isclose(out.CU.sum(), st.CU.sum()) and np.isclose(out.CV.sum(), st.CV.sum())
    assert np.array_equal(out.U[8:11, 8:11], st.U[2:5, 2:5])       # matter moved
    assert np.array_equal(out.CV[:, 8:11, 8:11], st.CV[:, 2:5, 2:5])  # cohorts moved WITH it


def test_enrollment_t_star_is_observer_independent():
    # the whole point of Part A: t* must not depend on the observation cadence
    _, _, s1, _ = enroll_reference(14, 12001)
    _, _, s2, _ = enroll_reference(14, 12001)
    assert s1.step == s2.step == 400
