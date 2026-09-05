"""Canonical label-free L/N/P/E/G-minus-target/G-full/B scopes for PRESEAL 03G."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Sequence

import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load("_turnover_scope_03e_for_03g", "turnover_scope_features_03e.py")

SCOPE_VERSION = "TURNOVER-SCOPES-03G-v1"
L_SLICE = (0, 11)
DIMS = {"L": 11, "N": 11, "P": 33, "B": 8, "E": 24, "Gm": 18, "Gf": 29}


def extract_scope_bundle_03g(
    state,
    regions: Sequence[np.ndarray],
    centroids: Sequence[Sequence[float]],
) -> dict:
    """Return the frozen scope bundle.

    G-full is exactly ``concat(L, G-minus-target)``. Therefore
    ``Gf[:, 0:11]`` is byte-for-byte equal to L and Gf is diagnostic only.
    """
    old = base.extract_scope_bundle_03e(state, regions, centroids)
    js = old["json_scopes"]
    gf = []
    for local, global_minus in zip(js["L"], js["Gm"]):
        a = np.asarray(local, dtype=np.float64)
        b = np.asarray(global_minus, dtype=np.float64)
        gf.append(np.concatenate([a, b]).tolist())
    js["Gf"] = gf
    names = dict(old["feature_names"])
    names["Gf"] = [f"L::{name}" for name in names["L"]] + [
        f"Gm::{name}" for name in names["Gm"]
    ]
    return {
        **old,
        "schema": SCOPE_VERSION,
        "feature_names": names,
        "dims": dict(DIMS),
        "json_scopes": js,
        "gated_scopes": ["L", "N", "E", "Gm", "B"],
        "diagnostic_scopes": ["P", "Gf"],
        "Gf_definition": "exact concatenation of L followed by G-minus-target",
        "Gf_L_slice": list(L_SLICE),
    }


def validate_scope_bundle(bundle: dict) -> None:
    if bundle.get("schema") != SCOPE_VERSION:
        raise ValueError(f"wrong scope schema: {bundle.get('schema')}")
    if bundle.get("dims") != DIMS:
        raise ValueError(f"wrong frozen scope dimensions: {bundle.get('dims')}")
    js = bundle.get("json_scopes", {})
    for scope, dim in DIMS.items():
        rows = js.get(scope)
        if not isinstance(rows, list) or len(rows) != 3:
            raise ValueError(f"scope {scope} must contain exactly three target rows")
        arr = np.asarray(rows, dtype=np.float64)
        if arr.shape != (3, dim) or not np.isfinite(arr).all():
            raise ValueError(f"scope {scope} has invalid shape or non-finite values: {arr.shape}")
    gf = np.asarray(js["Gf"], dtype=np.float64)
    local = np.asarray(js["L"], dtype=np.float64)
    if not np.array_equal(gf[:, L_SLICE[0] : L_SLICE[1]], local):
        raise ValueError("G-full does not contain the exact L vector at its frozen slice")
    if bundle.get("label_fields_present") is not False:
        raise ValueError("scope extraction must remain label-free")
    if bundle.get("diagnostic_cohorts_present") is not False:
        raise ValueError("diagnostic cohort IDs must not enter decoder features")


def json_scope_payload(bundle: dict) -> dict:
    validate_scope_bundle(bundle)
    return {
        "schema": bundle["schema"],
        "dims": bundle["dims"],
        "feature_names": bundle["feature_names"],
        "gated_scopes": bundle["gated_scopes"],
        "diagnostic_scopes": bundle["diagnostic_scopes"],
        "Gf_definition": bundle["Gf_definition"],
        "Gf_L_slice": bundle["Gf_L_slice"],
        "neighbour_order": bundle["json_scopes"]["neighbour_order"],
        "values": {scope: bundle["json_scopes"][scope] for scope in DIMS},
        "label_fields_present": False,
        "diagnostic_cohorts_present": False,
    }
