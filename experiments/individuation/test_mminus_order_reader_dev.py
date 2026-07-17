from dataclasses import replace

import numpy as np
import pytest

from edlab.experiments.sc_iom.engine import IOMState
from edlab.experiments.sc_mcm import config as MCM_CONFIG
from experiments.individuation import causal_confirm as cc
from experiments.individuation import mminus_order_reader_dev as reader
from experiments.individuation import mminus_order_reader_reproduce as reproduce
from experiments.individuation.access_structure_operators import state_sha256
from experiments.individuation.turnover_diag_engine import DiagEngine


def synthetic_state() -> tuple[IOMState, np.ndarray]:
    n = MCM_CONFIG.SPEC.size
    yy, xx = np.ogrid[:n, :n]
    support = (yy - n // 2) ** 2 + (xx - n // 2) ** 2 <= 8**2
    rho = np.zeros((n, n), dtype=float)
    rho[support] = 0.45
    U = 0.30 * rho
    V = 0.20 * rho
    c = np.full((n, n), 0.1, dtype=float)
    N = np.full((n, n), 0.8, dtype=float)
    C = np.zeros((MCM_CONFIG.TRACER.n_cohorts, n, n), dtype=float)
    C[0] = rho
    uptake = np.zeros((n, n), dtype=float)
    Mf = np.zeros((2, n, n), dtype=float)
    Mf[0, support] = rho[support] * -0.05
    Mf[1, support] = rho[support] * 0.20
    return IOMState(rho, U, V, c, N, C, uptake, Mf, 100), support


def test_frozen_bindings_validate_without_generating_reader_output():
    manifest, rows = reader.validate_frozen_inputs()
    assert tuple(manifest["seeds"]) == reader.DEV_SEEDS
    assert tuple(seed for seed, row in rows.items() if row["complete_block"]) == reader.COMPLETE_SEEDS


def test_scalar_sign_is_positive_under_unchanged_early_minus_late_convention():
    result = reader.scalar_sign_derivation()
    assert result["components"]["m1"]["early_minus_late"] == pytest.approx(-4.6377041581e-06)
    assert result["components"]["m2"]["early_minus_late"] == pytest.approx(-2.9102795171e-05)
    assert result["m1_minus_m2_early_minus_late"] == pytest.approx(2.4465091013e-05)
    assert result["predicted_sign"] == "positive"


def test_zero_gain_reader_is_bit_identical_to_probe_disabled_engine():
    state, support = synthetic_state()
    base = DiagEngine(MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER, up_ref_zero=True).step(state.copy())
    engine = reader.ReaderGainClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        support=support, gain_fraction=0.0, driver=None,
    )
    sham = engine.step(state.copy())
    assert state_sha256(base) == state_sha256(sham)


def test_zero_gain_identity_includes_the_qualified_collar_clamp():
    state, support = synthetic_state()
    ring = np.zeros_like(support)
    ring[8, 8:20] = True
    ys, xs = np.where(ring)
    frame = reader.ns._read_ring_frame(state, ys, xs, (0, 0))
    base_driver = reader.ns.BoundaryDriver(ring.copy(), [frame], label="base")
    test_driver = reader.ns.BoundaryDriver(ring.copy(), [frame], label="reader")
    base_engine = reader.ns.NoSwapClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        driver=base_driver, up_ref_zero=True,
    )
    test_engine = reader.ReaderGainClampEngine(
        MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
        support=support, gain_fraction=0.0, driver=test_driver,
    )
    assert state_sha256(base_engine.step(state.copy())) == state_sha256(test_engine.step(state.copy()))


def test_symmetric_gain_has_exact_source_and_c_reversal_with_non_c_identity():
    state, support = synthetic_state()
    outputs = {}
    sources = {}
    weighted = None
    for label, fraction in zip(reader.GAIN_LABELS, reader.GAIN_FRACTIONS):
        engine = reader.ReaderGainClampEngine(
            MCM_CONFIG.SPEC, cc.MEM_INTACT, MCM_CONFIG.TRACER,
            support=support, gain_fraction=fraction, driver=None,
        )
        outputs[label] = engine.step(state.copy())
        sources[label] = engine.last_source_raw
        weighted = engine.last_weighted_mminus
    assert sources["plus"] - sources["sham"] == pytest.approx(
        sources["sham"] - sources["minus"], abs=reader.NUMERIC_ATOL, rel=reader.NUMERIC_RTOL
    )
    np.testing.assert_allclose(
        outputs["plus"].c - outputs["sham"].c,
        -(outputs["minus"].c - outputs["sham"].c), atol=1e-15, rtol=1e-13,
    )
    for field in reader.ns.STATE_FIELDS:
        if field != "c":
            assert np.array_equal(getattr(outputs["minus"], field), getattr(outputs["sham"], field))
            assert np.array_equal(getattr(outputs["plus"], field), getattr(outputs["sham"], field))
    chi = (sources["plus"] - sources["minus"]) / (2.0 * reader.EPSILON)
    analytic = MCM_CONFIG.SPEC.dt * MCM_CONFIG.SPEC.s * cc.MEM_INTACT.lam_minus * weighted
    assert chi == pytest.approx(analytic, abs=reader.NUMERIC_ATOL, rel=reader.NUMERIC_RTOL)


def test_lam_minus_zero_keeps_all_gain_arms_byte_identical():
    state, support = synthetic_state()
    mem = replace(cc.MEM_INTACT, lam_minus=0.0)
    hashes = []
    sources = []
    for fraction in reader.GAIN_FRACTIONS:
        engine = reader.ReaderGainClampEngine(
            MCM_CONFIG.SPEC, mem, MCM_CONFIG.TRACER,
            support=support, gain_fraction=fraction, driver=None,
        )
        output = engine.step(state.copy())
        hashes.append(state_sha256(output))
        sources.append(engine.last_source_raw)
    assert len(set(hashes)) == 1
    assert sources[0] == sources[1] == sources[2]


def test_reader_coefficients_are_the_preexisting_symmetric_grid():
    values = [cc.MEM_INTACT.lam_minus * (1.0 + fraction) for fraction in reader.GAIN_FRACTIONS]
    assert values == pytest.approx([0.05, 0.15, 0.25])


def test_factorial_contrasts_use_one_complete_block_not_arm_replicates():
    values = {"H_L_EARLY": 2.0, "H_L_LATE": 1.0, "H_H_EARLY": 5.0, "H_H_LATE": 3.0}
    assert reader._factorial(values) == {"dose": 2.5, "order": 1.5, "interaction": 1.0}


def test_noncomplete_or_external_seed_is_refused_before_engine_execution():
    with pytest.raises(RuntimeError, match="non-complete seed"):
        reader.run_seed(57002)
    with pytest.raises(RuntimeError, match="non-complete seed"):
        reader.run_seed(58001)


def test_raw_only_factorial_matches_runner_formula():
    values = {"H_L_EARLY": -2.0, "H_L_LATE": -3.0, "H_H_EARLY": 4.0, "H_H_LATE": 1.0}
    assert reproduce.factorial(values) == reader._factorial(values)


def test_raw_only_classification_uses_original_world_rows():
    rows = []
    for _ in range(17):
        rows.append({
            "manipulation_valid": True,
            "contrasts": {
                "deep_mminus": {"order": 0.003},
                "chi_raw": {"order": 0.002},
                "chi_per_core_mass": {"order": 0.0001},
                "chi_raw_lam_minus_zero": {"order": 0.0},
                "low_dose_order_raw": 0.001,
                "high_dose_order_raw": 0.003,
                "order_attenuation_fraction": 1.0,
            },
        })
    classification, summaries = reproduce.classify(rows)
    assert classification == "ORDER_READER_CANDIDATE"
    assert summaries["chi_order_raw"]["n_worlds"] == 17
