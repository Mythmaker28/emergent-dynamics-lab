"""Canonical sealed authorization -> engine -> ledger -> raw -> analysis -> certificate chain for 03G."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

import turnover_analyzer_03g as analyzer
import turnover_ledger_03g as ledger
from turnover_raw_schema_03g import (
    RAW_SCHEMA,
    atomic_write_json,
    canonical_bytes,
    feasibility_projection,
    generate_raw_manifest,
    load_raw_record,
    sha256_file,
    write_raw_record,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PRODUCTION_MANIFEST = ROOT / "docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json"
PRODUCTION_SEAL = ROOT / "docs/individuation/FINAL_SEAL_MANIFEST_03G.json"


class ExecutionError(RuntimeError):
    pass


def _git_blob(path: Path, repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", "--path", str(path.relative_to(repo_root)), str(path)],
        cwd=repo_root,
        text=True,
    ).strip()


def _family(manifest: dict) -> tuple[list[int], list[int], int]:
    plan = manifest["seed_plan"]
    primary = list(range(int(plan["primary"]["first"]), int(plan["primary"]["last"]) + 1))
    reserve = list(range(int(plan["reserve"]["first"]), int(plan["reserve"]["last"]) + 1))
    if len(primary) != int(plan["primary"]["count"]) or len(reserve) != int(plan["reserve"]["count"]):
        raise ExecutionError("seed family count mismatch")
    if len(primary) + len(reserve) != int(plan["total_hard_cap"]):
        raise ExecutionError("seed family hard-cap mismatch")
    if len(set(primary + reserve)) != len(primary) + len(reserve):
        raise ExecutionError("seed family overlaps")
    return primary, reserve, int(plan["minimum_valid_worlds"])


def family_sha256(manifest: dict) -> str:
    primary, reserve, minimum = _family(manifest)
    return hashlib.sha256(
        canonical_bytes(
            {
                "primary": primary,
                "reserve": reserve,
                "hard_cap": len(primary) + len(reserve),
                "minimum_valid_worlds": minimum,
            }
        )
    ).hexdigest()


def runtime_environment() -> dict:
    packages = {}
    for package in ("numpy", "scipy", "matplotlib"):
        packages[package] = importlib.metadata.version(package)
    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "packages": packages,
    }


def _repo_instance(repo_root: Path, canonical_run_dir: Path) -> str:
    git_dir = subprocess.check_output(
        ["git", "rev-parse", "--git-dir"], cwd=repo_root, text=True
    ).strip()
    evidence = {
        "repo_root": str(repo_root.resolve()),
        "git_dir": str((repo_root / git_dir).resolve()),
        "canonical_run_dir": str(canonical_run_dir.resolve()),
        "host": socket.gethostname(),
    }
    return hashlib.sha256(canonical_bytes(evidence)).hexdigest()


def _validate_mode_and_family(manifest: dict) -> None:
    primary, reserve, _ = _family(manifest)
    all_seeds = primary + reserve
    if manifest["mode"] == "PROSPECTIVE":
        if all_seeds != list(range(54001, 54097)):
            raise ExecutionError("prospective family must be exactly 54001-54096")
    elif manifest["mode"] == "DEV_EXPLORATORY":
        if not all(50001 <= seed <= 50010 for seed in all_seeds):
            raise ExecutionError("DEV manifest contains a non-DEV seed")
        if not manifest["watermark"].startswith("DEV/EXPLORATORY"):
            raise ExecutionError("DEV manifest lacks mandatory watermark")
    elif manifest["mode"] != "SYNTHETIC_TEST":
        raise ExecutionError(f"unsupported execution mode: {manifest['mode']}")


def verify_seal_and_manifest(
    manifest_path: Path,
    seal_path: Path,
    *,
    repo_root: Path = ROOT,
) -> tuple[dict, dict, str, str]:
    """Fail closed before any engine module is imported or initialized."""
    manifest_path = manifest_path.resolve()
    seal_path = seal_path.resolve()
    if not seal_path.exists():
        raise ExecutionError(f"seal is absent: {seal_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "LCI-TURNOVER-EXECUTION-MANIFEST-03G-v1":
        raise ExecutionError("wrong 03G execution-manifest schema")
    if seal.get("schema") != "LCI-TURNOVER-SEAL-03G-v1":
        raise ExecutionError("wrong 03G seal schema")
    if seal.get("mode") != manifest.get("mode"):
        raise ExecutionError("seal/manifest mode mismatch")
    _validate_mode_and_family(manifest)
    manifest_sha = sha256_file(manifest_path)
    manifest_blob = _git_blob(manifest_path, repo_root)
    declared_manifest = seal.get("execution_manifest", {})
    if declared_manifest != {
        "path": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "sha256": manifest_sha,
        "git_blob": manifest_blob,
    }:
        raise ExecutionError("seal does not bind the exact execution manifest")
    if seal.get("family_sha256") != family_sha256(manifest):
        raise ExecutionError("seal family hash mismatch")
    protected = manifest.get("protected_files")
    if not isinstance(protected, dict) or not protected:
        raise ExecutionError("execution manifest has no protected files")
    protected_digest = hashlib.sha256(canonical_bytes(protected)).hexdigest()
    if "protected_files" in seal:
        if seal.get("protected_files") != protected:
            raise ExecutionError("seal protected-file set differs from execution manifest")
    elif seal.get("protected_files_sha256") != protected_digest:
        raise ExecutionError("seal protected-file map digest differs from execution manifest")
    for rel, expected in protected.items():
        path = repo_root / rel
        if not path.is_file():
            raise ExecutionError(f"protected file is absent: {rel}")
        actual = {"git_blob": _git_blob(path, repo_root), "sha256": sha256_file(path)}
        if actual != expected:
            raise ExecutionError(f"protected file mismatch: {rel}")
    lock_path = repo_root / manifest["environment"]["lock"]
    if sha256_file(lock_path) != manifest["environment"]["lock_sha256"]:
        raise ExecutionError("environment lock hash mismatch")
    if seal.get("environment_lock_sha256") != manifest["environment"]["lock_sha256"]:
        raise ExecutionError("seal environment lock mismatch")
    seal_sha = sha256_file(seal_path)
    return manifest, seal, seal_sha, manifest_blob


def verify_environment(manifest: dict, actual: dict | None = None) -> dict:
    actual = runtime_environment() if actual is None else actual
    expected = manifest["environment"]["runtime"]
    if actual != expected:
        raise ExecutionError(f"runtime environment mismatch: actual={actual}, expected={expected}")
    return actual


def validate_authorization(
    approval: dict,
    manifest: dict,
    seal_sha: str,
    manifest_sha: str,
    manifest_blob: str,
    canonical_run_dir: Path,
) -> None:
    expected_schema = (
        "LCI-TURNOVER-HUMAN-AUTHORIZATION-03G-v1"
        if manifest["mode"] == "PROSPECTIVE"
        else "LCI-TURNOVER-DEV-AUTHORIZATION-03G-v1"
    )
    if approval.get("schema") != expected_schema:
        raise ExecutionError("authorization schema mismatch")
    if manifest["mode"] == "PROSPECTIVE":
        if approval.get("authorized") is not True or approval.get("prospective_authorized") is not True:
            raise ExecutionError("prospective execution is not authorized")
    else:
        if approval.get("dev_authorized") is not True or approval.get("prospective_authorized") is not False:
            raise ExecutionError("DEV fixture cannot authorize prospective execution")
    expected = {
        "seal_sha256": seal_sha,
        "execution_manifest_sha256": manifest_sha,
        "execution_manifest_git_blob": manifest_blob,
        "runner_git_blob": manifest["protected_files"][
            "experiments/individuation/turnover_runner_03g.py"
        ]["git_blob"],
        "analyzer_git_blob": manifest["protected_files"][
            "experiments/individuation/turnover_analyzer_03g.py"
        ]["git_blob"],
        "environment_lock_sha256": manifest["environment"]["lock_sha256"],
        "family_sha256": family_sha256(manifest),
        "canonical_run_directory": manifest["canonical_run_directory"],
        "approval_phrase": manifest["authorization"]["required_phrase"],
    }
    for field, value in expected.items():
        if approval.get(field) != value:
            raise ExecutionError(f"authorization binding mismatch: {field}")
    for field in ("authorization_id", "approved_by", "approved_at_utc"):
        if not str(approval.get(field, "")).strip():
            raise ExecutionError(f"authorization field is required: {field}")


def _expected_next(completed: set[int], ordered: list[int]) -> int | None:
    for seed in ordered:
        if seed not in completed:
            return seed
    return None


def _raw_entry_from_existing(path: Path, run_dir: Path, mode: str) -> tuple[dict, dict]:
    record = load_raw_record(path, expected_mode=mode)
    entry = {
        "seed": int(record["seed"]),
        "world_id": int(record["world_id"]),
        "path": str(path.relative_to(run_dir)).replace("\\", "/"),
        "sha256": sha256_file(path),
        "schema": record["schema"],
        "valid": bool(record["feasibility"]["valid"]),
    }
    return record, entry


def _run_one(
    run_dir: Path,
    seed: int,
    expected_seed: int,
    context: dict,
    seed_executor: Callable[[int, dict], dict],
) -> dict:
    ledger.record_seed_started(run_dir, seed, expected_seed)
    path = run_dir / "raw" / f"seed_{seed}.json"
    if path.exists():
        record, raw_entry = _raw_entry_from_existing(path, run_dir, context["mode"])
    else:
        record = seed_executor(seed, context)
        raw_entry = write_raw_record(path, record)
        raw_entry["path"] = str(path.relative_to(run_dir)).replace("\\", "/")
    projection = feasibility_projection(record)
    ledger.record_seed_completed(run_dir, seed, raw_entry, projection)
    return projection


def _raw_manifest_from_ledger(run_dir: Path, mode: str, seal_sha: str) -> tuple[dict, dict]:
    entries = [entry["raw"] for entry in ledger.completed_seed_events(run_dir)]
    manifest = generate_raw_manifest(entries, mode=mode, seal_sha256=seal_sha)
    path = run_dir / "raw_manifest_03g.json"
    data = canonical_bytes(manifest) + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise ExecutionError("existing raw manifest differs from ledger-derived manifest")
    else:
        atomic_write_json(path, manifest, overwrite=False)
    return manifest, {
        "path": str(path.relative_to(run_dir)).replace("\\", "/"),
        "sha256": sha256_file(path),
        "n_records": manifest["n_records"],
        "n_valid_worlds": manifest["n_valid_worlds"],
    }


def execute_pipeline(
    manifest_path: Path,
    seal_path: Path,
    authorization_path: Path,
    *,
    resume: bool = False,
    seed_executor: Callable[[int, dict], dict] | None = None,
    repo_root: Path = ROOT,
    actual_environment: dict | None = None,
) -> dict:
    manifest, seal, seal_sha, manifest_blob = verify_seal_and_manifest(
        manifest_path, seal_path, repo_root=repo_root
    )
    manifest_sha = sha256_file(manifest_path)
    environment = verify_environment(manifest, actual_environment)
    run_dir = (repo_root / manifest["canonical_run_directory"]).resolve()
    approval = json.loads(Path(authorization_path).read_text(encoding="utf-8"))
    validate_authorization(
        approval,
        manifest,
        seal_sha,
        manifest_sha,
        manifest_blob,
        run_dir,
    )
    primary, reserve, minimum = _family(manifest)
    binding = {
        "authorization_id": approval["authorization_id"],
        "approved_by": approval["approved_by"],
        "approved_at_utc": approval["approved_at_utc"],
        "seal_sha256": seal_sha,
        "execution_manifest_sha256": manifest_sha,
        "execution_manifest_git_blob": manifest_blob,
        "family_sha256": family_sha256(manifest),
        "environment": environment,
        "environment_lock_sha256": manifest["environment"]["lock_sha256"],
        "code_git_blobs": {
            path: values["git_blob"] for path, values in manifest["protected_files"].items()
        },
        "code_sha256": {
            path: values["sha256"] for path, values in manifest["protected_files"].items()
        },
        "canonical_run_directory": str(run_dir),
        "repository_instance_evidence": _repo_instance(repo_root, run_dir),
        "mode": manifest["mode"],
    }
    start = ledger.initialize(run_dir, binding, resume=resume)
    state = ledger.verify(run_dir)["state"]
    if state == "CERTIFIED":
        return {"status": "already_certified", "run_dir": str(run_dir), **ledger.verify(run_dir)}
    if state == "CREATED":
        ledger.transition(run_dir, "AUTHORIZE", {"authorization_id": approval["authorization_id"]})
        state = "AUTHORIZED"
    if state == "AUTHORIZED":
        ledger.transition(run_dir, "START_PRIMARY", {"primary_seeds": primary})
        state = "PRIMARY_RUNNING"

    context = {
        "raw_schema": RAW_SCHEMA,
        "mode": "PROSPECTIVE" if manifest["mode"] == "PROSPECTIVE" else manifest["mode"],
        "watermark": manifest["watermark"],
        "bindings": {
            "seal_sha256": seal_sha,
            "execution_manifest_sha256": manifest_sha,
            "execution_manifest_git_blob": manifest_blob,
            "environment_lock_sha256": manifest["environment"]["lock_sha256"],
            "code_git_blobs": binding["code_git_blobs"],
            "code_sha256": binding["code_sha256"],
        },
    }
    if seed_executor is None:
        engine = importlib.import_module("turnover_engine_03g")
        seed_executor = engine.execute_real_seed

    if state == "PRIMARY_RUNNING":
        while True:
            completed = ledger.completed_seeds(run_dir)
            seed = _expected_next(completed, primary)
            if seed is None:
                break
            _run_one(run_dir, seed, seed, context, seed_executor)
        ledger.close_primary(run_dir, primary)
        state = "PRIMARY_CLOSED"
    if state == "PRIMARY_CLOSED":
        decision = ledger.reserve_decision(run_dir, minimum, reserve)
        state = "RESERVE_DECIDED"
    else:
        decisions = [entry for entry in ledger.entries(run_dir) if entry["event"] == "DECIDE_RESERVE"]
        decision = decisions[-1] if decisions else None

    if state == "RESERVE_DECIDED" and decision["active"]:
        ledger.transition(run_dir, "START_RESERVE", {"reserve_seeds": reserve})
        state = "RESERVE_RUNNING"
    if state == "RESERVE_RUNNING":
        while True:
            events = ledger.completed_seed_events(run_dir)
            valid = sum(bool(event["feasibility_projection"]["valid"]) for event in events)
            if valid >= minimum:
                break
            completed = {int(event["seed"]) for event in events}
            seed = _expected_next(completed, reserve)
            if seed is None:
                break
            _run_one(run_dir, seed, seed, context, seed_executor)
    state = ledger.verify(run_dir)["state"]
    if state in {"RESERVE_DECIDED", "RESERVE_RUNNING"}:
        _, manifest_entry = _raw_manifest_from_ledger(run_dir, context["mode"], seal_sha)
        ledger.close_family(run_dir, primary, reserve, minimum, manifest_entry)
        state = "FAMILY_CLOSED"
    if state == "FAMILY_CLOSED":
        manifest_for_analysis = dict(manifest)
        manifest_for_analysis["_repo_root"] = str(repo_root)
        result = analyzer.analyze(run_dir, manifest_for_analysis, seal_sha)
        ledger.record_analysis(
            run_dir,
            {
                **result["certificate_entry"],
                "report": result["report_entry"],
            },
        )
        state = "ANALYZED"
    if state == "ANALYZED":
        analysis_events = [
            entry for entry in ledger.entries(run_dir) if entry["event"] == "RECORD_ANALYSIS"
        ]
        ledger.certify(run_dir, analysis_events[-1]["analysis"])
    final = ledger.verify(run_dir, require_state="CERTIFIED")
    return {
        "status": "certified",
        "run_dir": str(run_dir),
        "ledger": final,
        "analysis": [
            entry for entry in ledger.entries(run_dir) if entry["event"] == "RECORD_ANALYSIS"
        ][-1]["analysis"],
        "start_mode": start["mode"],
    }


def static_selfcheck(manifest_path: Path = PRODUCTION_MANIFEST) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_mode_and_family(manifest)
    primary, reserve, minimum = _family(manifest)
    assert primary == list(range(54001, 54051))
    assert reserve == list(range(54051, 54097))
    assert minimum == 18
    assert manifest["authorization"]["required_phrase"].endswith(
        "FINAL_SEAL_SHA256=<FINAL_SEAL_SHA256>"
    )
    tree_path = ROOT / manifest["analysis"]["decision_tree"]
    analyzer.validate_decision_tree(json.loads(tree_path.read_text(encoding="utf-8")))
    print("03G STATIC SELF-CHECK PASS - complete runner path present; no engine imported; no seed run")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selfcheck", action="store_true")
    parser.add_argument("--manifest", type=Path, default=PRODUCTION_MANIFEST)
    parser.add_argument("--seal", type=Path, default=PRODUCTION_SEAL)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        static_selfcheck(args.manifest)
        return
    if args.authorization is None:
        parser.error("--authorization is required")
    result = execute_pipeline(
        args.manifest,
        args.seal,
        args.authorization,
        resume=args.resume,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
