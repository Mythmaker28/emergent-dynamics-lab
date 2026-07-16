from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_analysis_module():
    path = Path(__file__).with_name("reconcile_v4_1.py")
    spec = importlib.util.spec_from_file_location("reconcile_v4_1", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def approx(value: float, tolerance: float = 1e-12):
    class Approx:
        def __eq__(self, other):
            return abs(float(other) - value) <= tolerance

    return Approx()


def test_headline_values_and_classifications():
    results = json.loads((ROOT / "headline_results_v4_1.json").read_text(encoding="utf-8"))
    deep = results["longitudinal"]["deep"]
    assert deep["h1"]["world_grouped_point_r2"] == approx(0.69469387421633)
    assert deep["h2"]["world_grouped_point_r2"] == approx(-1.1183408783037767)
    assert results["observed_counts"] == {
        "records": 36,
        "original_worlds": 3,
        "histories": 12,
        "survived": 36,
        "lost": 0,
        "recorded_switches": 0,
        "deep_M_at_or_below_0_25": 34,
    }
    with (ROOT / "numerical_reconciliation.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["classification"] for row in rows} <= {
        "UNCHANGED", "CORRECTED", "WITHDRAWN"
    }
    assert any(
        row["quantity"] == "h1 deep headline"
        and row["classification"] == "WITHDRAWN"
        for row in rows
    )


def test_outer_folds_never_mix_an_original_world(monkeypatch):
    module = load_analysis_module()
    worlds = np.repeat(np.array([101, 102, 103]), 4)
    histories = np.tile(np.arange(4), 3)
    x = np.column_stack([worlds, histories]).astype(float)
    y = (histories + 0.1 * worlds).astype(float)
    calls = []

    def guarded_predict(x_train, y_train, x_test, ridge_lambda=1.0):
        train_worlds = set(x_train[:, 0].astype(int))
        test_worlds = set(x_test[:, 0].astype(int))
        assert train_worlds.isdisjoint(test_worlds)
        calls.append((train_worlds, test_worlds))
        return np.full(len(x_test), y_train.mean())

    monkeypatch.setattr(module, "ridge_predict", guarded_predict)
    prediction, fold_scores = module.grouped_oof(x, y, worlds)
    assert len(calls) == 3
    assert len(fold_scores) == 3
    assert np.isfinite(prediction).all()


def test_fixed_prediction_world_resampling_does_not_refit(monkeypatch):
    module = load_analysis_module()
    y = np.array([0.0, 1.0, 0.5, 1.5, 1.0, 2.0])
    prediction = np.array([0.1, 0.9, 0.6, 1.4, 0.8, 1.9])
    worlds = np.repeat(np.array([1, 2, 3]), 2)

    def forbidden_fit(*args, **kwargs):
        raise AssertionError("world-block uncertainty must not retrain")

    monkeypatch.setattr(module, "ridge_predict", forbidden_fit)
    summary = module.exact_world_block_interval(y, prediction, worlds)
    assert summary["ordered_resamples"] == 27
    assert len(summary["percentile_2_5_50_97_5"]) == 3


def test_claim_ledger_complete_and_boundary_clean():
    ledger = json.loads((ROOT / "claim_ledger_v4_1.json").read_text(encoding="utf-8"))
    assert [claim["id"] for claim in ledger["claims"]] == [
        f"C{index:02d}" for index in range(1, 13)
    ]
    manuscript = (ROOT / "ORGANIZATIONAL_MEMORY_V4_1_RECONCILIATION.md").read_text(
        encoding="utf-8"
    )
    sections = manuscript.split("## ")
    protected = "\n".join(
        section
        for section in sections
        if section.startswith("Abstract")
        or section.startswith("4. Results")
        or section.startswith("7. Conclusion")
    )
    assert "CONFIRM-02" not in protected
    assert not any(str(seed) in protected for seed in range(54000, 55000))
    assert "active reconstruction" not in protected.lower()
