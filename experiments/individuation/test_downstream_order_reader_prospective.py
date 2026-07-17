import ast
import json
from pathlib import Path

import numpy as np
import pytest

from experiments.individuation import downstream_order_reader_contract as contract
from experiments.individuation import downstream_order_reader_prospective as runner
from experiments.individuation import downstream_order_reader_reproduce as reproduce


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TEMPLATE = REPO_ROOT / "docs" / "individuation" / "DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST_TEMPLATE.json"


def synthetic_world(value: float, index: int, *, complete=True, invalid=False, numerical=False):
    a_by_history = {
        "H_L_EARLY": value,
        "H_L_LATE": 0.0,
        "H_H_EARLY": value,
        "H_H_LATE": 0.0,
    }
    histories = {}
    for history_name, a_value in a_by_history.items():
        sources = {}
        for source in contract.SOURCE_LABELS:
            d_value = a_value if source == "zero" else 0.0
            j_values = {"minus": -d_value, "sham": 0.0, "plus": d_value}
            sources[source] = {
                "arms": {
                    label: {
                        "J_internal_x": float(j_value),
                        "flux_abs_sum": float(max(abs(j_value), 1.0)),
                        "n_internal_faces": 296,
                        "dt": 0.1,
                        "core_mass": 1.0,
                    }
                    for label, j_value in j_values.items()
                }
            }
        histories[history_name] = {"sources": sources}
    world = {
        "schema": contract.RAW_SCHEMA,
        "world_id": f"W{index:03d}",
        "seed": index,
        "complete_block": bool(complete),
        "manipulation_invalid": bool(invalid),
        "numerical_failure": bool(numerical),
        "histories": histories,
    }
    if complete:
        world.update(contract.recompute_world_contrast(world))
    return world


def family(values, *, complete_count=None):
    values = list(values)
    if complete_count is None:
        complete_count = len(values)
    return [
        synthetic_world(value, index + 1, complete=index < complete_count)
        for index, value in enumerate(values)
    ]


def test_exact_six_claim_outcomes_and_two_administrative_dispositions():
    assert contract.SCIENTIFIC_OUTCOMES == (
        "PREDICTED_ATTENUATION",
        "OPPOSITE_SIGN_FUNCTIONAL_ACCESS",
        "NO_ACCESS_ESTABLISHED",
        "EQUIVALENT_AT_DECLARED_SCALE",
        "MANIPULATION_INVALID",
        "UNRESOLVED",
    )
    assert contract.NONSCIENTIFIC_DISPOSITIONS == ("FEASIBILITY_FAIL", "NUMERICAL_FAILURE")

    positive = contract.classify_worlds(family([0.01] * 18))
    negative = contract.classify_worlds(family([-0.01] * 18))
    no_access = contract.classify_worlds(family([0.0] * 18))
    equivalent = contract.classify_worlds(
        family([(-1.0 if index % 2 else 1.0) * 1e-4 for index in range(18)]),
        equivalence_margin=1e-3,
    )
    invalid_worlds = family([0.01] * 18)
    invalid_worlds[7]["manipulation_invalid"] = True
    invalid = contract.classify_worlds(invalid_worlds)
    unresolved = contract.classify_worlds(family([1e-12] * 18))
    insufficient = contract.classify_worlds(family([0.01] * 48, complete_count=17))
    numerical_worlds = family([0.01] * 18)
    numerical_worlds[2]["numerical_failure"] = True
    numerical = contract.classify_worlds(numerical_worlds)

    assert positive["scientific_classification"] == "PREDICTED_ATTENUATION"
    assert negative["scientific_classification"] == "OPPOSITE_SIGN_FUNCTIONAL_ACCESS"
    assert no_access["scientific_classification"] == "NO_ACCESS_ESTABLISHED"
    assert equivalent["scientific_classification"] == "EQUIVALENT_AT_DECLARED_SCALE"
    assert invalid["scientific_classification"] == "MANIPULATION_INVALID"
    assert unresolved["scientific_classification"] == "UNRESOLVED"
    assert insufficient["run_disposition"] == "FEASIBILITY_FAIL"
    assert insufficient["scientific_classification"] == "UNRESOLVED"
    assert numerical["run_disposition"] == "NUMERICAL_FAILURE"
    assert numerical["scientific_classification"] == "UNRESOLVED"


def test_negative_access_is_not_absence_or_manipulation_failure():
    result = contract.classify_worlds(family([-0.005] * 18))
    assert result["scientific_classification"] == "OPPOSITE_SIGN_FUNCTIONAL_ACCESS"
    assert result["run_disposition"] == "SCIENTIFIC_CLASSIFIED"


def test_equivalence_is_disabled_without_an_independent_scientific_margin():
    worlds = family([(-1.0 if index % 2 else 1.0) * 1e-4 for index in range(18)])
    assert contract.classify_worlds(worlds)["scientific_classification"] == "NO_ACCESS_ESTABLISHED"
    delta_num = contract.classify_worlds(family([0.0] * 18))["delta_num"]
    with pytest.raises(ValueError, match="must exceed numerical resolution"):
        contract.classify_worlds(worlds, equivalence_margin=delta_num)


def test_numerical_floor_is_propagated_from_raw_face_sums_not_an_effect_margin():
    world = synthetic_world(0.01, 1)
    recomputed = contract.recompute_world_contrast(world)
    assert recomputed["delta_num_world"] > contract.CLOSED_IDENTITY_RESIDUAL
    assert recomputed["delta_num_world"] < 1e-8
    doubled = synthetic_world(0.01, 2)
    for history in doubled["histories"].values():
        for source in history["sources"].values():
            for arm in source["arms"].values():
                arm["flux_abs_sum"] *= 2.0
    assert contract.recompute_world_contrast(doubled)["delta_num_world"] > recomputed["delta_num_world"]


def test_historical_complete_rate_is_used_only_for_fixed_capacity_sensitivity():
    result = contract.binomial_feasibility_sensitivity()
    assert result["historical_rate"] == pytest.approx(17 / 24)
    assert result["clopper_pearson_95"] == pytest.approx(
        [0.48905218610649925, 0.8738479114923199]
    )
    assert result["fixed_maximum_source_worlds"] == 48
    assert result["minimum_complete_worlds"] == 18
    assert result["probability_meeting_minimum_at_cp_lower_rate"] == pytest.approx(0.958474711734761)
    assert result["uniform_prior_posterior_predictive_probability"] == pytest.approx(0.9969717592826155)
    assert result["posterior_predictive_complete_world_quantiles"] == {
        "0.025": 22, "0.05": 24, "0.5": 34, "0.95": 41, "0.975": 43,
    }
    assert result["effect_power_computed"] is False
    assert result["adaptive_extension_allowed"] is False


def test_seedless_manifest_validates_and_execution_refuses_before_output_creation(tmp_path):
    manifest, _ = runner.load_manifest(TEMPLATE, require_execution=False)
    assert all(str(slot["seed"]).startswith("<SEED_") for slot in manifest["world_slots"])
    output = tmp_path / "must-not-exist"
    with pytest.raises(RuntimeError, match="not human sealed"):
        runner.run_sealed_family(TEMPLATE, output)
    assert not output.exists()


def sealed_mock_manifest(tmp_path: Path) -> Path:
    manifest = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    manifest.update(
        mode=runner.SEALED_MODE,
        execution_authorized=True,
        human_review={"status": "APPROVED_FOR_EXECUTION", "reviewer": "SYNTHETIC_TEST", "date": None},
        namespace_audit={"status": "PASS", "evidence": "SYNTHETIC_TEST_ONLY_NO_WORLD_INITIALIZATION"},
    )
    # Values exist only in pytest's temporary mock manifest; no simulator is imported or called.
    for index, slot in enumerate(manifest["world_slots"], start=1):
        slot["seed"] = index
    path = tmp_path / "synthetic-sealed-manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_atomic_resume_skips_completed_prefix_and_prevents_duplicate_worlds(tmp_path):
    manifest_path = sealed_mock_manifest(tmp_path)
    output = tmp_path / "mock-raw"
    calls = []

    def interrupted_executor(slot, _manifest):
        calls.append(slot["world_id"])
        if len(calls) == 6:
            raise RuntimeError("synthetic interruption")
        return {
            "schema": contract.RAW_SCHEMA,
            "world_id": slot["world_id"],
            "seed": slot["seed"],
            "complete_block": False,
            "manipulation_invalid": False,
            "numerical_failure": False,
        }

    with pytest.raises(RuntimeError, match="synthetic interruption"):
        runner.run_sealed_family(manifest_path, output, executor=interrupted_executor)
    assert calls == [f"W{index:03d}" for index in range(1, 7)]
    assert len(list((output / "worlds").glob("W*.json"))) == 5

    resumed_calls = []

    def resumed_executor(slot, _manifest):
        resumed_calls.append(slot["world_id"])
        return {
            "schema": contract.RAW_SCHEMA,
            "world_id": slot["world_id"],
            "seed": slot["seed"],
            "complete_block": False,
            "manipulation_invalid": False,
            "numerical_failure": False,
        }

    results = runner.run_sealed_family(manifest_path, output, executor=resumed_executor)
    assert resumed_calls[0] == "W006"
    assert resumed_calls[-1] == "W048"
    assert results["classification"]["run_disposition"] == "FEASIBILITY_FAIL"
    assert results["classification"]["scientific_classification"] == "UNRESOLVED"

    duplicate_path = output / "worlds" / "W002.json"
    duplicate = json.loads(duplicate_path.read_text(encoding="utf-8"))
    duplicate["seed"] = 1
    duplicate_path.write_text(json.dumps(duplicate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="seed/slot mismatch|duplicate"):
        runner.run_sealed_family(manifest_path, output, executor=resumed_executor)


def test_raw_only_reproducer_matches_contract_and_imports_no_runner_or_engine(tmp_path):
    manifest_path = sealed_mock_manifest(tmp_path)
    manifest_sha = runner.sha256_file(manifest_path)
    raw_dir = tmp_path / "raw-positive"
    (raw_dir / "worlds").mkdir(parents=True)
    worlds = family([0.01] * 48)
    for world in worlds:
        world["manifest_sha256"] = manifest_sha
        path = raw_dir / "worlds" / f"{world['world_id']}.json"
        path.write_text(json.dumps(world, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    direct = contract.classify_worlds(worlds)
    independent = reproduce.reproduce(manifest_path, raw_dir)
    assert independent["classification"] == direct
    assert independent["all_stored_complete_world_contrasts_exact"] is True

    source = (HERE / "downstream_order_reader_reproduce.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("downstream_order_reader_prospective" in name for name in imported)
    assert not any("downstream_order_reader_contract" in name for name in imported)
    assert not any(name.startswith("edlab") for name in imported)
    assert not any("engine" in name for name in imported)


def test_prospective_module_defers_all_simulator_imports_until_scientific_executor():
    source = (HERE / "downstream_order_reader_prospective.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            top_level_imports.append(node.module or "")
    assert not any(name.startswith("edlab") for name in top_level_imports)
    assert not any("counterfactual_history_core_dev" in name for name in top_level_imports)
    assert not any("downstream_order_reader_instrumentation" in name for name in top_level_imports)
