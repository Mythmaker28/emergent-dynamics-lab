"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — frozen LOW-DIMENSIONAL access scopes (supersedes the 03C E/G flattening).

Red-team blocker B3: the 03C `turnover_scope_features.extract_scope_bundle` persisted E and G as full
8 x 64 x 64 = 32768-predictor field stacks. Against the minimum 51 outer-training rows that is a predictor/row
ratio of 642, so L-vs-E/G loss comparisons mixed radically different model capacities and could not support a
local-vs-distributed conclusion. This module replaces the DECODER representation of the environment/global scopes
with FROZEN, physically-interpretable, low-dimensional features (<= 24 per scope), selected WITHOUT consulting any
causal outcome. Raw fields are still persisted (compressed) for future work, but they are NOT the decoder input.

Coherent scope set (matches PRESEAL_CANDIDATE_PROTOCOL_03E and TASK 4):
  L   target memory only ...................... 11 features (unchanged from 03C)
  N   geometric-nearest neighbour memory ....... 11 features (unchanged)
  P   target + ordered neighbours memory ....... 33 features (unchanged)
  B   target body/environment baseline ......... 8 features (unchanged)
  E   LOCAL environment, target memory MASKED ... 24 features: 8 fields x 3 fixed radial annuli around the target,
                                                  with target m1/m2 zeroed on the target mask.
  Gm  GLOBAL world, target memory REMOVED ....... 18 features: occupied-cell global mean + std of 8 fields (m1/m2
                                                  computed with the target region zeroed) + up_ref + occupied fraction.
  Gf  GLOBAL world, target memory INCLUDED ...... 18 features: same summary WITHOUT zeroing the target (DIAGNOSTIC
                                                  only; nests L, so L is NOT required to beat Gf).

Frozen geometry (no outcome consultation, no learned parameters): annulus edges (periodic distance) and field order
are constants below. Every feature is a deterministic per-world reduction; the outer analysis still learns scaling on
training worlds only.

Detectability (what these features CAN and CANNOT see):
  CAN detect: presence of own-dose information carried by the coarse radial profile of the fields/memory around the
              target (E), and by occupied-cell global field summaries (Gm/Gf). This is sufficient to test whether the
              *own-dose signal* is recoverable from the environment/global state at a resolution comparable to L.
  CANNOT detect: fine spatial patterns below the 3-annulus / global-summary resolution, non-radial structure, or
              phase information. A distributed code that hides own-dose ONLY in high-frequency spatial detail would be
              invisible here — this is stated as a frozen limitation, not silently assumed absent.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Sequence

import numpy as np

# reuse the unchanged, audited L/N/P/B extractors + helpers
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_sf03c", Path(__file__).resolve().parent / "turnover_scope_features.py")
_sf03c = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_sf03c)  # type: ignore
memory_features = _sf03c.memory_features
body_features = _sf03c.body_features
periodic_distance = _sf03c.periodic_distance
MEMORY_FEATURE_NAMES = _sf03c.MEMORY_FEATURE_NAMES
BODY_FEATURE_NAMES = _sf03c.BODY_FEATURE_NAMES

SCOPE_VERSION = "TURNOVER-LPEG-03E-v1"
FIELD_NAMES = ("rho", "u_intensive", "v_intensive", "c", "N", "uptake", "m1", "m2")
ANNULUS_EDGES = (0.0, 6.0, 12.0, 24.0)          # 3 fixed radial annuli (periodic distance, cells) — FROZEN
N_ANNULI = len(ANNULUS_EDGES) - 1
OCC_THRESHOLD = 0.30                             # occupied-cell definition for global summaries (rho > 0.30)


def _fields(state) -> np.ndarray:
    rho_safe = np.maximum(state.rho, 1e-12)
    return np.stack([state.rho, state.U / rho_safe, state.V / rho_safe, state.c, state.N, state.uptake,
                     state.Mf[0] / rho_safe, state.Mf[1] / rho_safe]).astype(np.float64, copy=False)


def _radial_index(centroid, size) -> np.ndarray:
    ys, xs = np.mgrid[0:size, 0:size]
    dy = np.minimum(np.abs(ys - centroid[0]), size - np.abs(ys - centroid[0]))
    dx = np.minimum(np.abs(xs - centroid[1]), size - np.abs(xs - centroid[1]))
    return np.hypot(dy, dx)


def environment_local_features(state, region_i: np.ndarray, centroid) -> np.ndarray:
    """E: 8 fields x 3 fixed radial annuli around the target, target m1/m2 masked to 0. 24 features."""
    size = int(state.rho.shape[0])
    fields = _fields(state).copy()
    region_i = np.asarray(region_i, dtype=bool)
    fields[6, region_i] = 0.0                     # mask target's own m1
    fields[7, region_i] = 0.0                     # mask target's own m2
    r = _radial_index([int(round(centroid[0])) % size, int(round(centroid[1])) % size], size)
    feats = []
    for f in range(8):
        for a in range(N_ANNULI):
            sel = (r >= ANNULUS_EDGES[a]) & (r < ANNULUS_EDGES[a + 1])
            feats.append(float(fields[f][sel].mean()) if sel.any() else 0.0)
    return np.asarray(feats, dtype=float)


def _global_summary(state, region_i: np.ndarray | None) -> np.ndarray:
    """18 features: occupied-cell mean+std of 8 fields (target m1/m2 zeroed if region_i given) + up_ref + occ_frac."""
    fields = _fields(state).copy()
    if region_i is not None:
        region_i = np.asarray(region_i, dtype=bool)
        fields[6, region_i] = 0.0
        fields[7, region_i] = 0.0
    occ = state.rho > OCC_THRESHOLD
    feats = []
    if occ.any():
        for f in range(8):
            feats.append(float(fields[f][occ].mean()))
            feats.append(float(fields[f][occ].std()))
        up_alive = state.uptake[state.rho > 1e-4]
        feats.append(float(up_alive.mean()) if up_alive.size else 0.0)
        feats.append(float(occ.mean()))
    else:
        feats = [0.0] * 18
    return np.asarray(feats, dtype=float)


def extract_scope_bundle_03e(state, regions: Sequence[np.ndarray], centroids: Sequence[Sequence[float]]) -> dict:
    if len(regions) != 3 or len(centroids) != 3:
        raise ValueError("the frozen protocol requires exactly three target droplets")
    size = int(state.rho.shape[0])
    regions = [np.asarray(r, dtype=bool) for r in regions]
    local = [memory_features(state, r) for r in regions]
    body = [body_features(state, r) for r in regions]
    js = {k: [] for k in ("L", "N", "P", "B", "E", "Gm", "Gf", "neighbour_order")}
    raw_arrays = {}
    for i in range(3):
        others = sorted([j for j in range(3) if j != i],
                        key=lambda j: periodic_distance(centroids[i], centroids[j], size))
        near, far = others
        js["L"].append(local[i].tolist())
        js["N"].append(local[near].tolist())
        js["P"].append(np.concatenate([local[i], local[near], local[far]]).tolist())
        js["B"].append(body[i].tolist())
        js["E"].append(environment_local_features(state, regions[i], centroids[i]).tolist())
        js["Gm"].append(_global_summary(state, regions[i]).tolist())
        js["Gf"].append(_global_summary(state, None).tolist())
        js["neighbour_order"].append([int(near), int(far)])
        # raw fields for FUTURE work only (NOT decoder input): coarse 8x8 target-centred downsample (8x64=512, marked non-primary)
        f = _fields(state)
        cy, cx = int(round(centroids[i][0])) % size, int(round(centroids[i][1])) % size
        fc = np.roll(f, (size // 2 - cy, size // 2 - cx), axis=(-2, -1))
        raw_arrays[f"raw_coarse_target_{i}"] = fc.reshape(8, 8, size // 8, 8, size // 8).mean(axis=(2, 4)).astype(np.float32)
    ef = [f"{fld}::ann{a}" for fld in FIELD_NAMES for a in range(N_ANNULI)]
    gf = [f"{fld}::{stat}" for fld in FIELD_NAMES for stat in ("gmean", "gstd")] + ["up_ref", "occ_frac"]
    return {
        "schema": SCOPE_VERSION,
        "feature_names": {"L": list(MEMORY_FEATURE_NAMES), "N": list(MEMORY_FEATURE_NAMES),
                          "P": [f"{r}::{n}" for r in ("target", "nearest", "farther") for n in MEMORY_FEATURE_NAMES],
                          "B": list(BODY_FEATURE_NAMES), "E": ef, "Gm": gf, "Gf": gf},
        "dims": {"L": 11, "N": 11, "P": 33, "B": 8, "E": len(ef), "Gm": len(gf), "Gf": len(gf)},
        "gated_scopes": ["L", "N", "E", "Gm", "B"],
        "diagnostic_scopes": ["P", "Gf"],
        "json_scopes": js,
        "raw_arrays_are_future_work_only": True,
        "arrays": raw_arrays,
        "label_fields_present": False,
        "diagnostic_cohorts_present": False,
    }


def persist_scope_bundle_03e(path, bundle: dict) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(tmp, **bundle["arrays"])
    os.replace(tmp, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    out = {k: bundle[k] for k in ("schema", "feature_names", "dims", "gated_scopes", "diagnostic_scopes",
                                  "json_scopes", "raw_arrays_are_future_work_only",
                                  "label_fields_present", "diagnostic_cohorts_present")}
    out["path"] = str(path)
    out["sha256"] = digest
    return out
