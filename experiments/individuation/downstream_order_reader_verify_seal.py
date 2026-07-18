"""Independent engine-free verifier for DOWNSTREAM-ORDER-READER-01 sealing.

This module uses the Python standard library only.  It must never import the
prospective runner, the scientific contract, NumPy, SciPy, or an engine.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Mapping


SCHEMA = "DOWNSTREAM-ORDER-READER-01-MANIFEST-v1"
MODE = "PROSPECTIVE_HUMAN_SEALED"
ACCEPTED = "5ae98861b00f62cde78858234dd03ef4a47f549c"
BRANCH = "codex/downstream-order-reader-prospective-seal-00"
SEEDS = list(range(58001, 58049))
MANIFEST_RELATIVE = "docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json"
AUDIT_RELATIVE = "docs/individuation/DOWNSTREAM_ORDER_READER_01_NAMESPACE_AUDIT.json"
PREREG_RELATIVE = (
    "docs/individuation/"
    "DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_PREREGISTRATION_CANDIDATE.md"
)
PREREG_SHA256 = "3041c0853c9e3ab244442b4e17e94fe706276450df8280bb20dda8c31c8dfaee"
EXPECTED_DESIGN = {
    "histories": ["H_L_EARLY", "H_L_LATE", "H_H_EARLY", "H_H_LATE"],
    "source_lam_minus": {"zero": 0.0, "intact": 0.15},
    "ramp_arms": {"minus": -1, "sham": 0, "plus": 1},
    "settle_steps": 40,
    "source_expression_steps": 1,
    "response_steps": 1,
    "ramp_epsilon_c": 0.01,
    "core_radius": 10,
    "response_lam_minus": 0.15,
    "up_ref_zero": True,
}
EXPECTED_CLASSIFICATIONS = [
    "PREDICTED_ATTENUATION",
    "OPPOSITE_SIGN_FUNCTIONAL_ACCESS",
    "NO_ACCESS_ESTABLISHED",
    "EQUIVALENT_AT_DECLARED_SCALE",
    "MANIPULATION_INVALID",
    "UNRESOLVED",
]
PROHIBITED_IMPORT_PREFIXES = (
    "edlab",
    "numpy",
    "scipy",
    "experiments.individuation.downstream_order_reader_prospective",
    "experiments.individuation.downstream_order_reader_contract",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(repo: Path, *args: str, binary: bool = False):
    result = subprocess.run(
        ["git", *args], cwd=repo, check=False, capture_output=True, text=not binary,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode() if binary else result.stderr
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr.strip()}")
    return result.stdout if binary else result.stdout.strip()


def no_prohibited_imports(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return not any(
        name == prefix or name.startswith(prefix + ".")
        for name in imported for prefix in PROHIBITED_IMPORT_PREFIXES
    )


def no_placeholder(value) -> bool:
    if isinstance(value, str):
        return "<SEED_" not in value
    if isinstance(value, Mapping):
        return all(no_placeholder(key) and no_placeholder(item) for key, item in value.items())
    if isinstance(value, list):
        return all(no_placeholder(item) for item in value)
    return True


def verify(manifest_path: Path) -> dict:
    manifest_path = manifest_path.resolve()
    repo = Path(git(manifest_path.parent, "rev-parse", "--show-toplevel"))
    expected_manifest_path = (repo / MANIFEST_RELATIVE).resolve()
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    audit_path = repo / AUDIT_RELATIVE
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    slots = manifest.get("world_slots", [])
    seeds = [slot.get("seed") for slot in slots]
    world_ids = [slot.get("world_id") for slot in slots]
    output = repo / manifest.get("output_locations", {}).get(
        "prospective_run_directory", "__MISSING_OUTPUT_BINDING__"
    )
    checks: dict[str, bool] = {}

    checks["manifest_exact_path"] = manifest_path == expected_manifest_path
    checks["schema_and_mode"] = manifest.get("schema") == SCHEMA and manifest.get("mode") == MODE
    checks["accepted_code_commit"] = manifest.get("accepted_parent") == ACCEPTED
    checks["required_branch"] = (
        manifest.get("required_branch") == BRANCH and git(repo, "branch", "--show-current") == BRANCH
    )
    checks["accepted_commit_is_ancestor"] = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ACCEPTED, "HEAD"], cwd=repo, check=False,
        capture_output=True,
    ).returncode == 0
    checks["working_tree_clean"] = git(repo, "status", "--porcelain", "--untracked-files=all") == ""
    checks["exact_48_world_ids"] = (
        len(world_ids) == 48 and world_ids == [f"W{index:03d}" for index in range(1, 49)]
    )
    checks["exact_48_unique_selected_seeds"] = seeds == SEEDS and len(set(seeds)) == 48
    checks["no_placeholder"] = no_placeholder(manifest)
    checks["namespace_audit_pass"] = (
        audit.get("status") == "PASS"
        and audit.get("selected_seeds") == SEEDS
        and audit.get("selected_seed_checks", {}).get("semantic_assignments_before_seal") == 0
        and audit.get("prospective_world_initialized") is False
    )
    checks["scientific_design_exact"] = manifest.get("design") == EXPECTED_DESIGN
    checks["scientific_unit_and_family_rules"] = (
        manifest.get("statistical_unit") == "original source world"
        and manifest.get("branches_and_arms_increase_n") is False
        and manifest.get("fixed_maximum_source_worlds") == 48
        and manifest.get("minimum_complete_worlds") == 18
        and manifest.get("adaptive_extension_after_outcomes") is False
        and manifest.get("no_extension_replacement_or_early_scientific_stop") is True
    )
    science = manifest.get("scientific_contract", {})
    checks["primary_and_inference_exact"] = (
        science.get("sole_primary_estimand") == "delta_A_O"
        and science.get("interval") == "two-sided 95% original-world Student-t"
        and science.get("directional_sign_rule") == "ceil(0.75*n_complete)"
        and science.get("numerical_floor") == "raw-derived delta_num"
        and science.get("body_geometry_correction") is False
    )
    checks["no_margins_or_equivalence_claim"] = (
        manifest.get("equivalence_margin") is None
        and science.get("m_A") is None
        and science.get("m_0") is None
        and science.get("equivalence_claim_authorized") is False
    )
    checks["six_classifications_exact"] = science.get("scientific_classifications") == EXPECTED_CLASSIFICATIONS
    checks["secondary_controls_exact"] = science.get("secondary_only") == [
        "direct source susceptibility calibration",
        "lam_minus=0 order response",
    ]
    checks["authorization_separate_and_absent"] = (
        manifest.get("execution_authorized") is False
        and manifest.get("human_review", {}).get("status") == "APPROVED_FOR_SEALING_NOT_EXECUTION"
        and manifest.get("execution_authorization", {}).get("status") == "REQUIRED_NOT_PRESENT"
        and manifest.get("execution_authorization", {}).get("repository_authorization_file") is None
    )
    checks["prospective_output_absent"] = not output.exists()
    checks["zero_engine_world_initialization"] = (
        manifest.get("sealing_attestation", {}).get("engine_initialized") is False
        and manifest.get("sealing_attestation", {}).get("worlds_initialized") == 0
        and not any(name.startswith(PROHIBITED_IMPORT_PREFIXES) for name in sys.modules)
    )
    checks["verifier_imports_no_runner_or_engine"] = no_prohibited_imports(Path(__file__).resolve())
    checks["preregistration_hash_frozen"] = (
        manifest.get("frozen_preregistration", {}).get("path") == PREREG_RELATIVE
        and manifest.get("frozen_preregistration", {}).get("sha256") == PREREG_SHA256
        and sha256_file(repo / PREREG_RELATIVE) == PREREG_SHA256
    )
    bound_files = manifest.get("bound_files", {})
    hash_matches = []
    committed_matches = []
    for relative, expected_hash in bound_files.items():
        local = repo / relative
        hash_matches.append(local.is_file() and sha256_file(local) == expected_hash)
        try:
            committed = git(repo, "show", f"HEAD:{relative}", binary=True)
        except RuntimeError:
            committed_matches.append(False)
        else:
            committed_matches.append(local.read_bytes() == committed)
    checks["all_bound_file_hashes_match"] = bool(bound_files) and all(hash_matches)
    checks["local_and_committed_bound_artifacts_identical"] = bool(bound_files) and all(committed_matches)
    commands = manifest.get("future_commands", {})
    checks["exact_commands_use_sealed_manifest"] = (
        MANIFEST_RELATIVE in commands.get("seal_verification", "")
        and MANIFEST_RELATIVE in commands.get("prospective_execution_after_authorization", "")
        and "--authorization" in commands.get("prospective_execution_after_authorization", "")
    )
    checks["manifest_hash_not_self_asserted"] = "manifest_sha256" not in manifest

    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema": "DOWNSTREAM-ORDER-READER-01-SEAL-VERIFICATION-v1",
        "status": "PASS" if not failures else "FAIL",
        "verdict": "SEALED_READY_FOR_EXECUTION_REVIEW" if not failures else "REVISE_SEAL",
        "manifest_path": MANIFEST_RELATIVE,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "selected_namespace": "58001-58048",
        "selected_seed_count": len(seeds),
        "bound_file_count": len(bound_files),
        "checks": checks,
        "failures": failures,
        "engine_imported_by_verifier": False,
        "worlds_initialized_by_verifier": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
