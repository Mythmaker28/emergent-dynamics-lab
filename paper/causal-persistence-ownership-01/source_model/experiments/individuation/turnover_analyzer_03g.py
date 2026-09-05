"""Canonical closed-ledger raw-to-A/F verdict analyzer for turnover PRESEAL 03G."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import turnover_ledger_03g as ledger
import turnover_statistics_03g as statistics
from turnover_raw_schema_03g import (
    atomic_write_bytes,
    atomic_write_json,
    canonical_bytes,
    load_raw_record,
    sha256_file,
    validate_raw_manifest,
)

ANALYSIS_SCHEMA = "LCI-TURNOVER-ANALYSIS-CERTIFICATE-03G-v1"


class AnalysisError(RuntimeError):
    pass


def _resolve_in_run(run_dir: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = run_dir / path
    path = path.resolve()
    if run_dir.resolve() not in path.parents:
        raise AnalysisError(f"path escapes canonical run directory: {path}")
    return path


def _load_closed_raw(run_dir: Path) -> tuple[dict, list[dict], dict]:
    status = ledger.verify(run_dir)
    if status["state"] != "FAMILY_CLOSED":
        raise AnalysisError(f"analysis requires FAMILY_CLOSED, found {status['state']}")
    close_events = [entry for entry in ledger.entries(run_dir) if entry["event"] == "CLOSE_FAMILY"]
    if len(close_events) != 1:
        raise AnalysisError("ledger must contain exactly one family closure")
    manifest_entry = close_events[0]["raw_manifest"]
    manifest_path = _resolve_in_run(run_dir, manifest_entry["path"])
    if sha256_file(manifest_path) != manifest_entry["sha256"]:
        raise AnalysisError("raw manifest hash mismatch against ledger")
    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = validate_raw_manifest(raw_manifest, run_dir)
    return raw_manifest, records, status


def build_matrices(records: list[dict]) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    valid = [record for record in records if record["feasibility"]["valid"]]
    matrices = {scope: [] for scope in ("L", "N", "P", "E", "Gm", "Gf", "B")}
    labels = []
    groups = []
    for record in valid:
        scopes = record["scientific"]["scopes"]
        if scopes is None:
            raise AnalysisError(f"valid seed {record['seed']} has no scope payload")
        values = scopes["values"]
        dose = record["scientific"]["histories"]["own_dose"]
        if len(dose) != 3:
            raise AnalysisError("the frozen protocol requires three target labels per world")
        for target in range(3):
            for scope in matrices:
                matrices[scope].append(values[scope][target])
            labels.append(float(dose[target]))
            groups.append(int(record["world_id"]))
    arrays = {scope: np.asarray(rows, dtype=np.float64) for scope, rows in matrices.items()}
    y = np.asarray(labels, dtype=np.float64)
    original_world = np.asarray(groups, dtype=np.int64)
    if len(np.unique(original_world)) != len(valid):
        raise AnalysisError("duplicate world identifiers among valid raw records")
    return arrays, y, original_world


def _eval_expression(expression, gates: dict[str, bool]) -> bool:
    if isinstance(expression, str):
        if expression not in gates:
            raise AnalysisError(f"unknown gate in decision tree: {expression}")
        return bool(gates[expression])
    if not isinstance(expression, dict) or len(expression) != 1:
        raise AnalysisError(f"invalid decision expression: {expression!r}")
    operator, value = next(iter(expression.items()))
    if operator == "not":
        return not _eval_expression(value, gates)
    if operator == "all":
        return all(_eval_expression(item, gates) for item in value)
    if operator == "any":
        return any(_eval_expression(item, gates) for item in value)
    raise AnalysisError(f"unsupported decision operator: {operator}")


def select_outcome(tree: dict, gates: dict[str, bool]) -> tuple[str, dict]:
    outcomes = tree.get("outcomes", {})
    matched = [
        outcome
        for outcome, definition in outcomes.items()
        if _eval_expression(definition["expression"], gates)
    ]
    if len(matched) != 1:
        raise AnalysisError(f"decision tree must select exactly one outcome, matched={matched}")
    outcome = matched[0]
    if outcome not in tree.get("evaluation_precedence", []):
        raise AnalysisError(f"outcome {outcome} missing from frozen precedence")
    return outcome, outcomes[outcome]


def validate_decision_tree(tree: dict) -> None:
    if tree.get("schema") != "LCI-TURNOVER-DECISION-TREE-03G-v1":
        raise AnalysisError("wrong decision-tree schema")
    if set(tree.get("outcomes", {})) != set("ABCDEF"):
        raise AnalysisError("decision tree must define exactly outcomes A-F")
    if set(tree.get("evaluation_precedence", [])) != set("ABCDEF"):
        raise AnalysisError("decision precedence must contain exactly A-F")
    gate_names = ("FEASIBILITY", "G_OWN_PERM", "G_LOCAL_EXCLUSION", "G_CAUSAL", "DISTRIBUTED_ENV")
    seen = set()
    for bits in range(2 ** len(gate_names)):
        gates = {name: bool(bits & (1 << index)) for index, name in enumerate(gate_names)}
        try:
            outcome, _ = select_outcome(tree, gates)
        except AnalysisError:
            continue
        seen.add(outcome)
    if seen != set("ABCDEF"):
        raise AnalysisError(f"unreachable intended outcomes: {sorted(set('ABCDEF') - seen)}")


def _write_stable(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise AnalysisError(f"existing analysis artifact differs: {path}")
        return
    atomic_write_bytes(path, data, overwrite=False)


def analyze(run_dir, execution_manifest: dict, seal_sha256: str) -> dict:
    run_dir = Path(run_dir).resolve()
    raw_manifest, records, ledger_status = _load_closed_raw(run_dir)
    minimum = int(execution_manifest["seed_plan"]["minimum_valid_worlds"])
    n_valid = int(raw_manifest["n_valid_worlds"])
    tree_path = Path(execution_manifest["analysis"]["decision_tree"])
    if not tree_path.is_absolute():
        tree_path = Path(execution_manifest["_repo_root"]) / tree_path
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    validate_decision_tree(tree)

    ownership = None
    causal = None
    primary = None
    if n_valid >= minimum:
        matrices, own_dose, original_world = build_matrices(records)
        ownership = statistics.evaluate_ownership(
            matrices,
            own_dose,
            original_world,
            permutation_reps=int(execution_manifest["analysis"]["permutation_reps"]),
        )
        batteries = [
            record["scientific"]["causal_intervention_battery"]["deep"]
            for record in records
            if record["feasibility"]["valid"]
        ]
        causal = statistics.causal_expression_gate(batteries, minimum)
        primary = statistics.primary_gate(ownership, causal)
        gates = {
            "FEASIBILITY": True,
            "G_OWN_PERM": bool(ownership["G_OWN_PERM"]["pass"]),
            "G_LOCAL_EXCLUSION": bool(ownership["G_LOCAL_EXCLUSION"]["pass"]),
            "G_CAUSAL": bool(causal["pass"]),
            "DISTRIBUTED_ENV": bool(ownership["DISTRIBUTED_ENV"]["pass"]),
        }
    else:
        gates = {
            "FEASIBILITY": False,
            "G_OWN_PERM": False,
            "G_LOCAL_EXCLUSION": False,
            "G_CAUSAL": False,
            "DISTRIBUTED_ENV": False,
        }
    outcome, definition = select_outcome(tree, gates)
    raw_trace = [
        {
            "seed": int(entry["seed"]),
            "world_id": int(entry["world_id"]),
            "sha256": entry["sha256"],
            "valid": bool(entry["valid"]),
        }
        for entry in raw_manifest["entries"]
    ]
    certificate = {
        "schema": ANALYSIS_SCHEMA,
        "mode": execution_manifest["mode"],
        "watermark": execution_manifest["watermark"],
        "seal_sha256": seal_sha256,
        "ledger_tip_at_family_close": ledger_status["tip_hash"],
        "raw_manifest_sha256": sha256_file(
            _resolve_in_run(
                run_dir,
                [
                    entry
                    for entry in ledger.entries(run_dir)
                    if entry["event"] == "CLOSE_FAMILY"
                ][0]["raw_manifest"]["path"],
            )
        ),
        "raw_trace": raw_trace,
        "n_raw_worlds": len(records),
        "n_valid_worlds": n_valid,
        "minimum_valid_worlds": minimum,
        "gates": gates,
        "ownership": ownership,
        "causal": causal,
        "primary": primary,
        "outcome": outcome,
        "outcome_name": definition["name"],
        "authorized_wording": definition["authorized_wording"],
        "forbidden_claims": sorted(
            set(tree["global_forbidden_claims"]) | set(definition["forbidden_claims"])
        ),
        "active_reconstruction": {
            "observed": False,
            "future_hypothesis_only": bool(definition["active_reconstruction_future_only"]),
        },
        "numbers_trace_to_raw_sha256": True,
    }
    report = (
        f"# Turnover 03G result report\n\n"
        f"- Mode: `{certificate['mode']}`\n"
        f"- Watermark: **{certificate['watermark']}**\n"
        f"- Valid original worlds: {n_valid}/{len(records)} (minimum {minimum})\n"
        f"- Outcome: **{outcome} - {definition['name']}**\n\n"
        f"{definition['authorized_wording']}\n\n"
        f"Every numerical result in the machine-readable certificate is linked to the listed raw SHA-256 values.\n"
    ).encode("utf-8")
    analysis_dir = run_dir / "analysis"
    cert_path = analysis_dir / "analysis_certificate_03g.json"
    report_path = analysis_dir / "analysis_report_03g.md"
    cert_bytes = canonical_bytes(certificate) + b"\n"
    _write_stable(cert_path, cert_bytes)
    _write_stable(report_path, report)
    return {
        "certificate": certificate,
        "certificate_entry": {
            "path": str(cert_path.relative_to(run_dir)),
            "sha256": sha256_file(cert_path),
            "outcome": outcome,
        },
        "report_entry": {
            "path": str(report_path.relative_to(run_dir)),
            "sha256": sha256_file(report_path),
        },
    }
