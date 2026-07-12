"""SYNTHETIC MUST-PASS / MUST-FAIL cases for the EXP-MA-00 morphological identity phenotype.
No metric is used on the substrate until it is proven here to fire on morphologies it must distinguish and to
collapse on a morphology it must call featureless."""

import numpy as np

from edlab.substrates.multistable.engine import MAState
from edlab.substrates.multistable.observables import MADetectionSpec, detect

DET = MADetectionSpec()
N = 48


def _droplet(kind: str, f_A: float = 0.5) -> MAState:
    ys, xs = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    d = np.sqrt((ys - 24.0) ** 2 + (xs - 24.0) ** 2)
    disc = d <= 8.0
    rho = np.where(disc, 0.8, 0.0)
    if kind == "mixed":
        phi = np.full((N, N), f_A)
    elif kind == "janus":
        phi = np.where(xs < 24, 0.95, 0.05)          # A left, B right
    elif kind == "core_shell":
        phi = np.where(d <= 4.0, 0.95, 0.05)         # A core, B shell
    elif kind == "two_domain":
        phi = np.where((d <= 4.0) & (xs < 24) | ((d > 4) & (d <= 6) & (xs > 26)), 0.95, 0.05)
    else:
        raise ValueError(kind)
    A = rho * phi
    B = rho * (1 - phi)
    C = np.stack([A + B] + [np.zeros((N, N))] * 11)
    return MAState(A, B, np.zeros((N, N)), np.ones((N, N)), C, 0)


def _phen(kind, f_A=0.5):
    e = detect(_droplet(kind, f_A), DET)
    assert len(e) == 1, f"{kind}: expected one droplet, got {len(e)}"
    return e[0]


def test_MUST_FAIL_mixed_droplet_has_no_morphology():
    """A perfectly mixed droplet must score ~zero demixing, whatever its bulk ratio -- and the metric must NOT be
    fooled by f_A (the old 'A > B' rule called a mixed droplet 'all A' or 'all B')."""
    for f in (0.35, 0.5, 0.65):
        e = _phen("mixed", f)
        assert e.phenotype[0] < 1e-6, (f, e.phenotype)      # demixing_index ~ 0
        assert e.phenotype[2] < 0.05                        # janus ~ 0
        assert e.phenotype[5] < 1e-6                        # interface ~ 0


def test_MUST_PASS_janus_and_core_shell_are_strongly_demixed():
    for kind in ("janus", "core_shell"):
        e = _phen(kind)
        assert e.phenotype[0] > 0.3, (kind, e.phenotype)    # demixing_index high


def test_MUST_PASS_morphologies_are_mutually_distinguishable():
    """The whole point of R8: these are different INDIVIDUALS under one law. Their phenotypes must separate, and
    each must separate from the featureless (mixed) droplet."""
    p = {k: _phen(k).phenotype for k in ("mixed", "janus", "core_shell", "two_domain")}
    ks = list(p)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            d = np.linalg.norm(p[ks[i]] - p[ks[j]])
            assert d > 0.2, (ks[i], ks[j], d, p[ks[i]], p[ks[j]])


def test_janus_is_off_centre_and_core_shell_is_concentric():
    """The two morphologies must be told apart by the RIGHT features: Janus by centroid separation, core-shell by
    radial moments -- not by accident."""
    j = _phen("janus").phenotype
    cs = _phen("core_shell").phenotype
    assert j[2] > 0.5 > cs[2]                    # janus_separation: large for Janus, ~0 for core-shell
    assert cs[3] < cs[4] - 0.1                   # core-shell: A sits at smaller radius than B
    assert abs(j[3] - j[4]) < 0.2                # Janus: A and B at the same mean radius


def test_phenotype_is_translation_and_rotation_invariant():
    """Forbidden features (position, absolute orientation) must not leak in."""
    base = _droplet("janus")
    e0 = detect(base, DET)[0]
    rolled = MAState(np.roll(base.A, (7, -5), (0, 1)), np.roll(base.B, (7, -5), (0, 1)),
                     base.c, base.N, np.roll(base.C, (7, -5), (1, 2)), 0)
    e1 = detect(rolled, DET)[0]
    assert np.allclose(e0.phenotype, e1.phenotype, atol=1e-9)          # translation
    rot = MAState(np.rot90(base.A), np.rot90(base.B), base.c, base.N,
                  np.stack([np.rot90(x) for x in base.C]), 0)
    e2 = detect(rot, DET)[0]
    assert np.allclose(e0.phenotype, e2.phenotype, atol=0.05)          # rotation
