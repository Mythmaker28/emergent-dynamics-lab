from __future__ import annotations

import ast
from pathlib import Path

from experiments.individuation import downstream_order_reader_null_mechanism_audit as audit


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs/individuation/DOWNSTREAM_ORDER_READER_01_NULL_MECHANISM_DECOMPOSITION_PLAN.md"
MODULE = ROOT / "experiments/individuation/downstream_order_reader_null_mechanism_audit.py"


def test_auditor_imports_no_runner_reproducer_or_engine():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any("downstream_order_reader_prospective" in name for name in imported)
    assert not any("downstream_order_reader_reproduce" in name for name in imported)
    assert not any(name == "edlab" or name.startswith("edlab.") for name in imported)


def test_zero_denominator_rule_is_explicit_and_non_cancellation():
    result = audit.cancellation_index([0.0, -0.0])
    assert result == {
        "signed_sum": 0.0,
        "absolute_sum": 0.0,
        "cancellation_index": 0.0,
        "cancellation_zero_denominator": True,
    }


def test_nonzero_cancellation_index_is_algebraic():
    result = audit.cancellation_index([2.0, -1.0])
    assert result["signed_sum"] == 1.0
    assert result["absolute_sum"] == 3.0
    assert result["cancellation_index"] == 1.0 / 3.0
    assert result["cancellation_zero_denominator"] is False


def test_real_immutable_raw_fails_closed_without_decomposition():
    report = audit.audit(ROOT, PLAN)
    assert report["status"] == "PASS_IMMUTABILITY_RAW_INSUFFICIENT"
    assert report["mechanistic_diagnosis"] == "RAW_INSUFFICIENT"
    assert report["roadmap_recommendation"] == "UNRESOLVED_RAW_INSUFFICIENT"
    assert report["n_raw_worlds"] == 48
    assert report["n_complete_worlds"] == 35
    assert len(report["world_rows"]) == 35
    assert report["decomposition_values_computed"] is False
    assert report["engine_or_runner_imported"] is False
    assert report["worlds_initialized_or_reconstructed"] == 0
    assert report["raw_availability"]["aggregate_J_flux_abs_count_and_hash_present"] is True
    assert report["raw_availability"]["source_core_c_values_available"] is False
    assert report["raw_availability"]["internal_face_values_available"] is False
    assert report["raw_availability"]["boundary_flux_values_available"] is False
    assert all(row["mechanism_status"] == "RAW_INSUFFICIENT" for row in report["world_rows"])
