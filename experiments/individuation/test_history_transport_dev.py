from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.individuation import history_transport_dev as ht


def _raw():
    return json.loads(ht.RAW_PATH.read_text(encoding="utf-8"))


def _diagnostics():
    return json.loads(ht.DEEP_DIAGNOSTICS_PATH.read_text(encoding="utf-8"))


def test_seed_guard_refuses_non_dev_namespace():
    with pytest.raises(ValueError, match="50001-50010"):
        ht.validate_dev_seeds([50001, 54001])


def test_exact_continuous_assignment_is_reproducible():
    histories = ht.assigned_histories(50002)
    assert len(histories) == 3
    assert np.allclose(
        histories,
        [
            (0.029655115415661894, 0.015180720497586568),
            (0.022642502389778156, 0.00927556516958803),
            (0.025249067399080852, 0.02947578589649935),
        ],
        rtol=0.0,
        atol=1e-15,
    )


def test_assignment_gate_detects_no_categorical_randomization():
    assignment = ht.assignment_kind()
    assert assignment["outcome_independent"] is True
    assert assignment["categorical_randomization"] is False
    assert assignment["spatial_blocking_or_latin_square_implemented"] is False


def test_candidate_binary_labels_remain_rejected():
    raw = next(row for row in _raw() if row["seed"] == 50005)
    targets = [
        {
            "target": index,
            "dose": float(raw["dose"][index]),
            "order": float(raw["order"][index]),
        }
        for index in range(3)
    ]
    audit = ht._candidate_label_audits(targets)
    assert audit["dose_midpoint"]["status"].startswith("REJECTED")
    assert audit["order_sign"]["counts"] == {"A": 3, "B": 0}
    assert audit["within_world_extremes"]["status"].startswith("REJECTED")


def test_gate_failure_prevents_all_causal_estimands():
    result = ht.build_results(
        _raw(),
        _diagnostics(),
        [50002, 50004, 50005, 50007],
        reconstruct_confounds=False,
    )
    assert result["decision"] == "STOP-HISTORY-CONTRAST"
    assert result["audit_gate"]["gate_pass"] is False
    assert all(value is None for key, value in result["causal_estimands"].items() if key in {
        "delta_coupled", "delta_isolated", "transport_difference", "retention_ratio"
    })
    assert result["feeding_probe_executed"] is False
    assert result["future_feeding_fields_accessed"] is False


def test_first_stage_is_unavailable_without_assigned_A_B():
    result = ht.build_results(
        _raw(),
        _diagnostics(),
        [50002, 50004, 50005, 50007],
        reconstruct_confounds=False,
    )
    assert result["first_stage"]["categorical_H_A_vs_H_B_first_stage"] is None
    assert result["first_stage"]["reason"] == "no categorical histories were assigned"
    # The tempting midpoint split changes sign across worlds and is audit-only.
    values = result["first_stage"]["audit_only_retroactive_dichotomies_not_estimands"][
        "dose_midpoint_differences"
    ]
    assert any(value > 0 for value in values)
    assert any(value < 0 for value in values)
