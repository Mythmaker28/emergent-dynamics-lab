"""Engine-free fail-closed tests for the prospective seal."""
import ast
import json
from pathlib import Path

import pytest

from experiments.individuation import downstream_order_reader_prospective as runner
from experiments.individuation import downstream_order_reader_verify_seal as verifier


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / verifier.MANIFEST_RELATIVE


def payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_sealed_manifest_is_exact_fixed_family_without_embedded_authorization():
    manifest = payload()
    runner.validate_manifest_payload(manifest, require_execution=True)
    assert [slot["seed"] for slot in manifest["world_slots"]] == list(range(58001, 58049))
    assert manifest["execution_authorized"] is False
    assert manifest["execution_authorization"]["status"] == "REQUIRED_NOT_PRESENT"
    assert manifest["no_extension_replacement_or_early_scientific_stop"] is True


@pytest.mark.parametrize("mutation,error", [
    (lambda value: value["world_slots"].__setitem__(47, dict(value["world_slots"][0])), "world slot identifiers/order|duplicate"),
    (lambda value: value["world_slots"][0].__setitem__("seed", "<SEED_001>"), "integer seed"),
    (lambda value: value["design"].__setitem__("response_steps", 2), "design binding"),
    (lambda value: value.__setitem__("minimum_complete_worlds", 17), "minimum complete-world"),
    (lambda value: value.__setitem__("equivalence_margin", 0.01), "no scientific equivalence"),
])
def test_manifest_mutations_fail_closed(mutation, error):
    manifest = payload()
    mutation(manifest)
    with pytest.raises(RuntimeError, match=error):
        runner.validate_manifest_payload(manifest, require_execution=True)


def test_external_authorization_must_bind_exact_manifest_bytes(tmp_path):
    manifest = payload()
    wrong = tmp_path / "authorization.json"
    wrong.write_text(json.dumps({
        "schema": runner.AUTHORIZATION_SCHEMA,
        "status": "APPROVED_FOR_EXECUTION",
        "manifest_sha256": "0" * 64,
        "approval_phrase": "wrong",
    }), encoding="utf-8")
    with pytest.raises(RuntimeError, match="does not exactly bind"):
        runner.validate_execution_authorization(
            wrong, manifest=manifest, manifest_sha256=runner.sha256_file(MANIFEST),
        )


def test_verifier_has_no_runner_engine_or_scientific_import():
    source = Path(verifier.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(
        name == prefix or name.startswith(prefix + ".")
        for name in imported for prefix in verifier.PROHIBITED_IMPORT_PREFIXES
    )
