"""Frozen, label-free L/N/P/E/G/B feature extraction for turnover PRESEAL 03C.

No function in this module accepts a history label. Labels are joined only by
the grouped analysis after the deep-snapshot feature bundle has been persisted.
Diagnostic cohort fields and IDs are excluded from every decoder feature.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Sequence

import numpy as np

MEMORY_FEATURE_NAMES = (
    "m1_mean",
    "m1_std",
    "m1_p10",
    "m1_p50",
    "m1_p90",
    "m2_mean",
    "m2_std",
    "m2_p10",
    "m2_p50",
    "m2_p90",
    "m1_minus_m2_std",
)
BODY_FEATURE_NAMES = (
    "cell_count",
    "rho_mass",
    "rho_mean",
    "rho_std",
    "u_intensive_mean",
    "v_intensive_mean",
    "N_mean",
    "c_mean",
)
WORLD_FIELD_NAMES = ("rho", "u_intensive", "v_intensive", "c", "N", "uptake", "m1", "m2")
SCOPE_VERSION = "TURNOVER-LPEG-03C-v1"


def periodic_distance(a: Sequence[float], b: Sequence[float], size: int) -> float:
    d = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    d = np.minimum(d, size - d)
    return float(np.hypot(*d))


def memory_features(state, mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    if not mask.any():
        raise ValueError("memory feature mask is empty")
    rho = np.maximum(state.rho[mask], 1e-12)
    m1 = state.Mf[0][mask] / rho
    m2 = state.Mf[1][mask] / rho
    values = []
    for field in (m1, m2):
        values.extend(
            [
                float(field.mean()),
                float(field.std()),
                float(np.percentile(field, 10)),
                float(np.percentile(field, 50)),
                float(np.percentile(field, 90)),
            ]
        )
    values.append(float((m1 - m2).std()))
    return np.asarray(values, dtype=float)


def body_features(state, mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    if not mask.any():
        raise ValueError("body feature mask is empty")
    rho = state.rho[mask]
    denom = np.maximum(rho, 1e-12)
    return np.asarray(
        [
            float(mask.sum()),
            float(rho.sum()),
            float(rho.mean()),
            float(rho.std()),
            float((state.U[mask] / denom).mean()),
            float((state.V[mask] / denom).mean()),
            float(state.N[mask].mean()),
            float(state.c[mask].mean()),
        ],
        dtype=float,
    )


def _world_fields(state) -> np.ndarray:
    rho_safe = np.maximum(state.rho, 1e-12)
    return np.stack(
        [
            state.rho,
            state.U / rho_safe,
            state.V / rho_safe,
            state.c,
            state.N,
            state.uptake,
            state.Mf[0] / rho_safe,
            state.Mf[1] / rho_safe,
        ]
    ).astype(np.float64, copy=False)


def _target_center(fields: np.ndarray, centroid: Sequence[float]) -> np.ndarray:
    size = fields.shape[-1]
    cy, cx = (int(np.rint(float(v))) % size for v in centroid)
    shift = (size // 2 - cy, size // 2 - cx)
    return np.roll(fields, shift=shift, axis=(-2, -1))


def extract_scope_bundle(state, regions: Sequence[np.ndarray], centroids: Sequence[Sequence[float]]) -> dict:
    """Extract exact scopes before any deep causal assay.

    L: target memory, 11 dimensions.
    N: geometric-nearest neighbour memory, same 11 definitions.
    P: target + nearest + farther neighbour memory, 33 dimensions.
    E: complete target-centred physical world with target m1/m2 cells zeroed.
    G: the same complete target-centred physical world without masking.
    B: target body/environment baseline, 8 dimensions.
    """
    if len(regions) != 3 or len(centroids) != 3:
        raise ValueError("the frozen protocol requires exactly three target droplets")
    size = int(state.rho.shape[0])
    if state.rho.shape != (size, size):
        raise ValueError("world grid must be square")

    regions = [np.asarray(r, dtype=bool) for r in regions]
    local = [memory_features(state, r) for r in regions]
    body = [body_features(state, r) for r in regions]
    fields = _world_fields(state)
    json_scopes = {"L": [], "N": [], "P": [], "B": [], "neighbour_order": []}
    arrays = {}

    for i in range(3):
        others = [j for j in range(3) if j != i]
        others.sort(key=lambda j: periodic_distance(centroids[i], centroids[j], size))
        near, far = others
        json_scopes["L"].append(local[i].tolist())
        json_scopes["N"].append(local[near].tolist())
        json_scopes["P"].append(np.concatenate([local[i], local[near], local[far]]).tolist())
        json_scopes["B"].append(body[i].tolist())
        json_scopes["neighbour_order"].append([int(near), int(far)])

        global_fields = fields.copy()
        environment_fields = fields.copy()
        environment_fields[6:, regions[i]] = 0.0
        arrays[f"G_target_{i}"] = _target_center(global_fields, centroids[i])
        arrays[f"E_target_{i}"] = _target_center(environment_fields, centroids[i])
        arrays[f"target_mask_{i}"] = _target_center(regions[i][None, ...].astype(np.uint8), centroids[i])[0]

    return {
        "schema": SCOPE_VERSION,
        "feature_names": {
            "L": list(MEMORY_FEATURE_NAMES),
            "N": list(MEMORY_FEATURE_NAMES),
            "P": [f"target::{n}" for n in MEMORY_FEATURE_NAMES]
            + [f"nearest::{n}" for n in MEMORY_FEATURE_NAMES]
            + [f"farther::{n}" for n in MEMORY_FEATURE_NAMES],
            "B": list(BODY_FEATURE_NAMES),
            "E_G_fields": list(WORLD_FIELD_NAMES),
        },
        "json_scopes": json_scopes,
        "arrays": arrays,
        "label_fields_present": False,
        "diagnostic_cohorts_present": False,
    }


def persist_scope_bundle(path: os.PathLike[str] | str, bundle: dict) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(tmp, **bundle["arrays"])
    os.replace(tmp, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "path": str(path),
        "sha256": digest,
        "schema": bundle["schema"],
        "feature_names": bundle["feature_names"],
        "json_scopes": bundle["json_scopes"],
        "label_fields_present": False,
        "diagnostic_cohorts_present": False,
    }


def load_scope_arrays(path: os.PathLike[str] | str, expected_sha256: str) -> dict[str, np.ndarray]:
    path = Path(path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"scope sidecar hash mismatch: {actual} != {expected_sha256}")
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}
