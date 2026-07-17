import json
from pathlib import Path

import numpy as np
import pytest

from experiments.individuation import counterfactual_history_mechanism_reconciliation as mr


def test_scalar_closed_form_matches_iteration_for_both_components():
    for eta_d in (mr.core.cc.MEM_INTACT.eta_d1, mr.core.cc.MEM_INTACT.eta_d2):
        for first, second in mr.core.HISTORIES.values():
            closed = mr.scalar_closed_form_component(first=first, second=second, eta_d=eta_d)
            iterative = mr.scalar_iterative_component(first=first, second=second, eta_d=eta_d)
            assert closed == pytest.approx(iterative, abs=1e-15, rel=1e-13)


def test_frozen_early_minus_late_convention_implies_positive_scalar_mminus_order():
    result = mr.scalar_sign_derivation()
    assert result["frozen_expected_order_sign"] == "negative"
    assert result["scalar_derived_order_sign"] == "positive"
    assert result["components"]["m2"]["factorial"]["order"] < 0
    assert abs(result["components"]["m2"]["factorial"]["order"]) > abs(
        result["components"]["m1"]["factorial"]["order"]
    )
    assert result["mminus"]["factorial"]["order"] > 0


def test_factorial_contrast_is_not_redefined():
    values = {"H_L_EARLY": 4.0, "H_L_LATE": 1.0, "H_H_EARLY": 8.0, "H_H_LATE": 2.0}
    got = mr.core.factorial_scalar(values)
    assert got == {"dose": 2.5, "order": 4.5, "interaction": 3.0}


def test_lowo_uses_one_prediction_per_original_world():
    X = np.asarray([[0.0], [1.0], [2.0], [30.0]])
    y = np.asarray([0.0, 1.0, 2.0, 30.0])
    got = mr._lowo_ridge(X, y)
    assert got["n_original_worlds"] == 4
    assert len(got["predictions"]) == 4
    assert len(got["training_mean_predictions"]) == 4
    assert got["training_mean_predictions"][3] == pytest.approx(1.0)


def test_new_seed_is_refused_before_world_execution(tmp_path: Path):
    with pytest.raises(ValueError, match="no new namespace"):
        mr.replay_seed(58001, tmp_path / "irrelevant.json")


def test_frozen_raw_has_exactly_17_original_world_rows():
    raw = mr.core.REPO_ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json"
    assert mr.sha256_file(raw) == mr.RAW_SHA256
    payload = json.loads(raw.read_text(encoding="utf-8"))
    complete = mr._raw_complete_worlds(payload)
    assert len(complete) == 17
    assert len({world["seed"] for world in complete}) == 17


def test_fixed_model_panels_are_nested_without_stepwise_selection():
    assert mr.MODEL_PANELS["mass_area"] == ("body_mass", "body_size")
    assert set(mr.MODEL_PANELS["mass_area"]) < set(mr.MODEL_PANELS["body_geometry"])
    assert set(mr.MODEL_PANELS["body_geometry"]) < set(mr.MODEL_PANELS["body_geometry_memory"])
    assert set(mr.MODEL_PANELS["body_geometry_memory"]) - set(mr.MODEL_PANELS["body_geometry"]) == {
        "mplus_mean", "mminus_mean"
    }
