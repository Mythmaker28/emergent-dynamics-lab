"""Authoritative prospective analysis for turnover PRESEAL 03C.

Consumes only the committed/frozen schema emitted by
turnover_prospective_runner.py. Every scope uses the same own cumulative-dose
label and the same outer leave-one-original-world-out folds.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stats = _load("turnover_statistics", "turnover_statistics.py")
sf = _load("turnover_scope_features", "turnover_scope_features.py")

MIN_VALID_WORLDS = 18


def build_analysis_matrices(payload: dict) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, list[dict]]:
    matrices = {scope: [] for scope in ("L", "N", "P", "E", "G", "B")}
    labels = []
    groups = []
    row_audit = []
    records = [record for record in payload["records"] if record["feasibility"]["valid"]]
    for record in records:
        seed = int(record["seed"])
        dose = record["labels"]["own_dose"]
        scope_meta = record["scope_bundle"]
        if scope_meta.get("label_fields_present") is not False:
            raise ValueError(f"scope bundle for seed {seed} contains label fields")
        sidecar = ROOT / scope_meta["path"]
        arrays = sf.load_scope_arrays(sidecar, scope_meta["sha256"])
        json_scopes = scope_meta["json_scopes"]
        for target in range(3):
            y = float(dose[target])
            labels.append(y)
            groups.append(seed)
            matrices["L"].append(json_scopes["L"][target])
            matrices["N"].append(json_scopes["N"][target])
            matrices["P"].append(json_scopes["P"][target])
            matrices["B"].append(json_scopes["B"][target])
            matrices["E"].append(arrays[f"E_target_{target}"].reshape(-1))
            matrices["G"].append(arrays[f"G_target_{target}"].reshape(-1))
            row_audit.append(
                {
                    "original_world": seed,
                    "target": target,
                    "label_name_for_all_scopes": "own cumulative dose",
                    "label_value": y,
                    "sidecar_sha256": scope_meta["sha256"],
                }
            )
    return (
        {scope: np.asarray(rows, dtype=float) for scope, rows in matrices.items()},
        np.asarray(labels, dtype=float),
        np.asarray(groups, dtype=int),
        row_audit,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.raw.read_text(encoding="utf-8"))
    matrices, own_dose, original_world, row_audit = build_analysis_matrices(payload)
    n_worlds = int(len(np.unique(original_world)))
    if n_worlds < 3:
        raise RuntimeError("fewer than three valid original worlds; grouped analysis is undefined")

    evaluation = stats.evaluate_scope_models(matrices, own_dose, original_world)
    powered = n_worlds >= MIN_VALID_WORLDS
    result = {
        "mission": "LCI-CAUSAL-TURNOVER-PRESEAL-03C",
        "status": "PROSPECTIVE_GROUPED_ANALYSIS" if powered else "INSUFFICIENT_VALID_WORLDS",
        "n_original_worlds": n_worlds,
        "n_target_rows": int(len(own_dose)),
        "minimum_valid_worlds": MIN_VALID_WORLDS,
        "same_label_every_scope": True,
        "label": "own cumulative dose",
        "feature_selection": "frozen before execution; no observed endpoint used",
        "evaluation": evaluation,
        "row_audit": row_audit,
        "primary_gate_interpretable": powered,
        "primary_gate_pass": bool(evaluation["local_storage_gate"]["pass"]) if powered else None,
        "claim_boundary": (
            "The gate concerns target-local informational storage versus neighbour, masked environment, "
            "and body baselines. G and P are access-scope comparisons and are not themselves local-storage proof."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"n_original_worlds={n_worlds} status={result['status']} "
        f"primary_gate_pass={result['primary_gate_pass']}"
    )


if __name__ == "__main__":
    main()
