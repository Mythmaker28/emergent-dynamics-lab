"""Real C1c scientific seed executor used by both DEV and future prospective turnover 03G."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cc = _load("_turnover_cc_03g", "causal_confirm.py")
nm = _load("_turnover_nm_03g", "nonmerging_confirm.py")
dev = _load("_turnover_dev_03g", "turnover_dev_runner.py")
scopes = _load("_turnover_scopes_03g", "turnover_scope_features_03g.py")

from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MCParams
from edlab.substrates.scaffold.observables import detect

K = cc.K
DET = C.DET
C1C = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)
MEM_ABLATE_PLUS = MCParams(lam_plus=0.0, lam_minus=0.15, **C1C)


def _json_safe(value):
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    return value


def _battery(state, centroids, regions, intact, full_ablation, plus_ablation) -> dict:
    empty = cc.empty_patch_mask(state, centroids)
    return {
        "intact": nm.measure(state, centroids, intact, None),
        "sham": nm.measure(state, centroids, intact, empty),
        "ablate_full": nm.measure(state, centroids, full_ablation, None),
        "ablate_plus": nm.measure(state, centroids, plus_ablation, None),
        "erase": [nm.measure(state, centroids, intact, regions[index]) for index in range(K)],
        "erase_ablate_full": [
            nm.measure(state, centroids, full_ablation, regions[index]) for index in range(K)
        ],
        "erase_ablate_plus": [
            nm.measure(state, centroids, plus_ablation, regions[index]) for index in range(K)
        ],
    }


def _storage(seed: int, engine) -> dict | None:
    state = cc.seed_world(seed)
    for _ in range(cc.WARM):
        state = engine.step(state)
    targets = cc.pick(sorted(detect(state, DET), key=lambda entity: -entity.size))
    if len(targets) < K:
        return None
    centroids = [entity.centroid for entity in targets]
    sigmas = [max(3.0, entity.rg * 0.8) for entity in targets]
    patches = [cc.patch(*centroids[index], sigmas[index]) for index in range(K)]
    rng = np.random.default_rng(seed)
    phase_amplitudes = [
        (float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI)))
        for _ in range(K)
    ]
    written = state.copy()
    for phase in (0, 1):
        for _ in range(cc.PHASE):
            for index in range(K):
                written.N = written.N + phase_amplitudes[index][phase] * patches[index]
            written = engine.step(written)
    for _ in range(cc.SETTLE):
        written = engine.step(written)
    return {
        "state": written.copy(),
        "centroids": [[float(value) for value in centroid] for centroid in centroids],
        "phase_amplitudes": [list(pair) for pair in phase_amplitudes],
        "own_dose": [float(a + b) for a, b in phase_amplitudes],
        "order_secondary": [float(b - a) for a, b in phase_amplitudes],
    }


def _blank_science(reason: str | None) -> dict:
    return {
        "histories": {
            "phase_amplitudes": [],
            "own_dose": [],
            "order_secondary": [],
            "primary_coordinate": "own cumulative dose / m-plus",
        },
        "target_ids": [],
        "target_centroids": [],
        "g0": {"rest_valid": False, "deep_valid": False},
        "material_tracer": {"trajectory": [], "deep_M": None, "tracer_base": None},
        "tracking_event_evidence": [],
        "scopes": None,
        "causal_intervention_battery": {"rest": None, "deep": None},
        "lambda_plus_only_control": {
            "lam_plus": 0.0,
            "lam_minus": 0.15,
            "rest": None,
            "deep": None,
        },
        "censoring_reason": reason,
        "snapshot_time": None,
    }


def execute_real_seed(seed: int, context: dict) -> dict:
    """Run the actual engine path. The caller must validate seal/auth/environment first."""
    intact = cc.build(cc.MEM_INTACT)
    full_ablation = cc.build(cc.MEM_ABLATE)
    plus_ablation = cc.build(MEM_ABLATE_PLUS)
    stored = _storage(seed, intact)
    if stored is None:
        feasibility = {
            "eligible": False,
            "deep_reached": False,
            "rest_assay_valid": False,
            "deep_assay_valid": False,
            "valid": False,
            "reason": "fewer_than_three_geometrically_eligible_targets",
        }
        scientific = _blank_science(feasibility["reason"])
    else:
        state = stored["state"]
        centroids = stored["centroids"]
        regions, _ = cc.region_masks(state, centroids)
        rest = _battery(state, centroids, regions, intact, full_ablation, plus_ablation)
        rest_valid = bool(
            all(
                branch["branch_valid"]
                for branch in [rest["intact"], rest["sham"], *rest["erase"]]
            )
        )
        turnover = dev.turnover(state, centroids, regions, intact, record=True)
        scientific = _blank_science(None)
        scientific.update(
            {
                "histories": {
                    "phase_amplitudes": stored["phase_amplitudes"],
                    "own_dose": stored["own_dose"],
                    "order_secondary": stored["order_secondary"],
                    "primary_coordinate": "own cumulative dose / m-plus",
                },
                "target_ids": list(range(K)),
                "target_centroids": centroids,
                "g0": {"rest_valid": rest_valid, "deep_valid": False},
                "material_tracer": {
                    "trajectory": turnover["traj"],
                    "deep_M": turnover["deep"]["M"] if turnover["deep"] is not None else None,
                    "tracer_base": turnover["base"],
                },
                "tracking_event_evidence": turnover["event_evidence"],
                "causal_intervention_battery": {"rest": rest, "deep": None},
                "lambda_plus_only_control": {
                    "lam_plus": 0.0,
                    "lam_minus": 0.15,
                    "rest": {
                        "ablate_plus": rest["ablate_plus"],
                        "erase_ablate_plus": rest["erase_ablate_plus"],
                    },
                    "deep": None,
                },
            }
        )
        if turnover["deep"] is None:
            reason = "turnover_cap_or_censor"
            if turnover["first_censor"]:
                reason = "tracker_event:" + ";".join(
                    f"{target}:{value[1]}@{value[0]}"
                    for target, value in turnover["first_censor"].items()
                )
            feasibility = {
                "eligible": True,
                "deep_reached": False,
                "rest_assay_valid": rest_valid,
                "deep_assay_valid": False,
                "valid": False,
                "reason": reason,
            }
            scientific["censoring_reason"] = reason
        else:
            deep = turnover["deep"]
            bundle = scopes.extract_scope_bundle_03g(
                deep["S"], deep["regs"], deep["cents"]
            )
            scope_payload = scopes.json_scope_payload(bundle)
            deep_battery = _battery(
                deep["S"],
                deep["cents"],
                deep["regs"],
                intact,
                full_ablation,
                plus_ablation,
            )
            deep_valid = bool(
                all(
                    branch["branch_valid"]
                    for branch in [
                        deep_battery["intact"],
                        deep_battery["sham"],
                        *deep_battery["erase"],
                    ]
                )
            )
            feasibility = {
                "eligible": True,
                "deep_reached": True,
                "rest_assay_valid": rest_valid,
                "deep_assay_valid": deep_valid,
                "valid": bool(rest_valid and deep_valid),
                "reason": None if rest_valid and deep_valid else "assay_geometry_invalid",
            }
            scientific.update(
                {
                    "scopes": scope_payload,
                    "g0": {"rest_valid": rest_valid, "deep_valid": deep_valid},
                    "causal_intervention_battery": {
                        "rest": rest,
                        "deep": deep_battery,
                    },
                    "lambda_plus_only_control": {
                        "lam_plus": 0.0,
                        "lam_minus": 0.15,
                        "rest": {
                            "ablate_plus": rest["ablate_plus"],
                            "erase_ablate_plus": rest["erase_ablate_plus"],
                        },
                        "deep": {
                            "ablate_plus": deep_battery["ablate_plus"],
                            "erase_ablate_plus": deep_battery["erase_ablate_plus"],
                        },
                    },
                    "censoring_reason": None,
                    "snapshot_time": int(deep["step"]),
                }
            )
    record = {
        "schema": context["raw_schema"],
        "mode": context["mode"],
        "watermark": context["watermark"],
        "seed": int(seed),
        "world_id": int(seed),
        "bindings": context["bindings"],
        "feasibility": feasibility,
        "scientific": scientific,
    }
    return _json_safe(record)
