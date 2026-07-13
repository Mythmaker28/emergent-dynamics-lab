"""SYNTHETIC MUST-PASS / MUST-FAIL cases for every R8 metric.

Four times this session a criterion was written that could not fire (a pooled null that could not produce the
outcome; a Nyquist-violating observer; a global Rg that scored 30 compact spots as uniform; a snapshot-indexed
turnover lag shorter than a material half-life). No R8 metric may be used on a substrate until it is proven here to
BOTH fire on a case it must accept AND fail on a case it must reject.
"""

import numpy as np

from edlab.identity.gates import (r8a_diversity, r8b_predictive_identity, r8c_causal_identity,
                                  within_entity_drift, between_entity_distance)

RNG = np.random.default_rng(0)
F = 5      # phenotype dimension
T = 20     # observations per entity


def _entity(mean, jitter, t=T):
    return np.asarray(mean)[None, :] + jitter * RNG.standard_normal((t, F))


# ----------------------------------------------------------------- R8-A diversity
def test_r8a_MUST_PASS_distinct_entities():
    """Three genuinely different entities, each stable over time -> the gate MUST fire."""
    trajs = [_entity([3, 0, 0, 0, 0], 0.10), _entity([0, 3, 0, 0, 0], 0.10), _entity([0, 0, 3, 0, 0], 0.10)]
    r = r8a_diversity(trajs)
    assert r["passes"], r
    assert r["separation_ratio"] > 2.0


def test_r8a_MUST_FAIL_interchangeable_entities():
    """The Gray-Scott / chemotaxis case: every entity is the same kind of thing -> the gate MUST reject."""
    trajs = [_entity([1, 1, 1, 1, 1], 0.30) for _ in range(3)]
    r = r8a_diversity(trajs)
    assert not r["passes"], r


def test_r8a_MUST_FAIL_when_drift_swamps_difference():
    """Entities differ, but each wanders more than they differ -> identity is not stable -> MUST reject."""
    trajs = [_entity([1, 0, 0, 0, 0], 3.0), _entity([0, 1, 0, 0, 0], 3.0), _entity([0, 0, 1, 0, 0], 3.0)]
    assert not r8a_diversity(trajs)["passes"]


def test_within_and_between_are_not_trivially_equal():
    a = _entity([2, 0, 0, 0, 0], 0.05)
    b = _entity([0, 2, 0, 0, 0], 0.05)
    assert between_entity_distance([a, b]) > 5 * within_entity_drift(a)


# ----------------------------------------------------------------- R8-B predictive identity
def test_r8b_MUST_PASS_identity_survives_turnover():
    """Prototypes fitted on EARLY states re-identify the SAME entities LATE, after constituent turnover
    (modelled as added noise + a common drift affecting all entities equally) -> MUST fire."""
    means = [[3, 0, 0, 0, 0], [0, 3, 0, 0, 0], [0, 0, 3, 0, 0]]
    early = [_entity(m, 0.15) for m in means]
    common_drift = np.array([0.4, 0.4, 0.4, 0.0, 0.0])          # turnover shifts everyone the same way
    late = [_entity(np.array(m) + common_drift, 0.25) for m in means]
    r = r8b_predictive_identity(early, late)
    assert r["passes"] and r["accuracy"] > 0.9, r


def test_r8b_MUST_FAIL_interchangeable_entities():
    """Identical entities -> a classifier cannot beat chance -> MUST reject."""
    early = [_entity([1, 1, 1, 1, 1], 0.3) for _ in range(3)]
    late = [_entity([1, 1, 1, 1, 1], 0.3) for _ in range(3)]
    r = r8b_predictive_identity(early, late)
    assert not r["passes"]
    assert abs(r["accuracy"] - r["chance"]) < 0.25


def test_r8b_MUST_FAIL_if_identity_is_lost_over_time():
    """Entities start distinct but relax to a common attractor by the late window -> identity not predictive."""
    means = [[3, 0, 0, 0, 0], [0, 3, 0, 0, 0], [0, 0, 3, 0, 0]]
    early = [_entity(m, 0.1) for m in means]
    late = [_entity([1, 1, 1, 0, 0], 0.3) for _ in means]        # all collapsed to the same state
    assert not r8b_predictive_identity(early, late)["passes"]


# ----------------------------------------------------------------- R8-C causal identity
def test_r8c_MUST_PASS_intact_keeps_identity_scrambled_loses_it():
    """The positive case: intact cargo reconstructs ITS OWN phenotype; scrambled cargo reconstructs a perfectly
    good entity -- but somebody else's. Entity PRESENCE is identical in both arms; IDENTITY is not."""
    src = np.array([3, 0, 0, 0, 0], float)
    others = [np.array([0, 3, 0, 0, 0], float), np.array([0, 0, 3, 0, 0], float)]
    intact = [src + 0.2 * RNG.standard_normal(F) for _ in range(20)]
    scrambled = [others[i % 2] + 0.2 * RNG.standard_normal(F) for i in range(20)]   # generic entity, WRONG identity
    r = r8c_causal_identity(src, intact, scrambled, others)
    assert r["passes"], r
    assert r["intact_source_identity_rate"] > 0.9 and r["scrambled_source_identity_rate"] < 0.1


def test_r8c_MUST_FAIL_single_attractor_substrate():
    """The Gray-Scott / chemotaxis case: only one kind of entity exists, so intact and scrambled cargo both
    reconstruct 'the source' at the same rate. The gate MUST reject -- this is the failure it exists to catch."""
    src = np.array([1, 1, 1, 1, 1], float)
    others = [np.array([1.02, 1.0, 0.98, 1.0, 1.0]), np.array([0.98, 1.0, 1.02, 1.0, 1.0])]
    intact = [src + 0.2 * RNG.standard_normal(F) for _ in range(30)]
    scrambled = [src + 0.2 * RNG.standard_normal(F) for _ in range(30)]
    r = r8c_causal_identity(src, intact, scrambled, others)
    assert not r["passes"], r
    assert abs(r["difference"]) < 0.25


def test_r8c_entity_presence_is_NOT_the_outcome():
    """Explicit guard: an arm in which entities are ALWAYS present but ALWAYS the wrong identity must score ZERO
    identity-recovery. Presence must never be mistaken for identity."""
    src = np.array([3, 0, 0, 0, 0], float)
    others = [np.array([0, 3, 0, 0, 0], float), np.array([0, 0, 3, 0, 0], float)]
    always_present_wrong_identity = [others[0] + 0.1 * RNG.standard_normal(F) for _ in range(20)]
    r = r8c_causal_identity(src, [], always_present_wrong_identity, others)
    assert r["scrambled_source_identity_rate"] == 0.0


# ----------------------------------------------------------------- O4' partial correlation (EXP-SC-00B)
from edlab.identity.gates import partial_correlation, partial_correlation_test   # noqa: E402


def test_partialcorr_MUST_PASS_genuine_effect_independent_of_controls():
    """Internal state genuinely drives future uptake, independently of size/mass -> the metric MUST fire."""
    rng = np.random.default_rng(1)
    n = 120
    Z = rng.normal(size=(n, 3))                       # mass, radius, density
    sig = rng.normal(size=n)                          # internal state, independent of morphology
    uptake = 1.5 * sig + 0.4 * Z[:, 0] + 0.3 * rng.normal(size=n)
    r = partial_correlation_test(uptake, sig, Z, n_perm=400, seed=2)
    assert r["passes"] and r["r_partial"] > 0.7, r


def test_partialcorr_MUST_FAIL_when_effect_is_entirely_a_morphology_confound():
    """THE decisive case. sig and uptake are correlated ONLY because both are driven by SIZE. A naive correlation
    fires; the partial correlation MUST NOT. This is what stops identity from being a proxy for body size."""
    rng = np.random.default_rng(3)
    n = 150
    size = rng.normal(size=n)
    sig = 2.0 * size + 0.3 * rng.normal(size=n)       # big droplets happen to be u-dominant
    uptake = 3.0 * size + 0.3 * rng.normal(size=n)    # big droplets happen to eat more
    Z = size[:, None]
    naive = float(np.corrcoef(uptake, sig)[0, 1])
    assert abs(naive) > 0.8                                        # the naive correlation DOES fire
    r = partial_correlation_test(uptake, sig, Z, n_perm=400, seed=4)
    assert not r["passes"], r                                       # the partial correlation MUST NOT
    assert abs(r["r_partial"]) < 0.3


def test_partialcorr_MUST_FAIL_when_there_is_no_effect():
    rng = np.random.default_rng(5)
    n = 120
    Z = rng.normal(size=(n, 3))
    sig = rng.normal(size=n)
    uptake = 0.8 * Z[:, 1] + rng.normal(size=n)
    assert not partial_correlation_test(uptake, sig, Z, n_perm=400, seed=6)["passes"]


def test_partialcorr_is_zero_when_x_is_constant():
    assert partial_correlation(np.arange(10.0), np.ones(10), np.zeros((10, 1))) == 0.0
