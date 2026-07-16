"""Hash-gated prospective runner for LCI-CAUSAL-TURNOVER-PRESEAL-03C.

This file is NOT an authorization. Execution requires a separate human-approval
JSON bound to the exact committed execution-manifest Git blob. The committed
approval template is deliberately unauthorized.

Seed plan:
  primary  54001..54050 (50 seeds; always completed after authorization)
  reserve  54051..54096 (46 seeds; sequential, feasibility-only activation)
  hard cap 96; minimum valid original worlds 18

`--selfcheck` is static: it does not instantiate an engine and cannot run a seed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from typing import Iterable

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cc = _load("cc", "causal_confirm.py")
nm = _load("nm", "nonmerging_confirm.py")
run = _load("run", "turnover_dev_runner.py")
sf = _load("sf", "turnover_scope_features.py")

from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
from edlab.experiments.sc_mcm.engine import MCParams

K = cc.K
DET = C.DET
C1C = dict(eta_w=0.015, eta_d1=0.35, eta_d2=0.006, k_exp=1.0)

PRIMARY_SEEDS = tuple(range(54001, 54051))
RESERVE_SEEDS = tuple(range(54051, 54097))
ALL_SEEDS = PRIMARY_SEEDS + RESERVE_SEEDS
MIN_VALID_WORLDS = 18
TOTAL_HARD_CAP = 96
MANIFEST_REL = "docs/individuation/TURNOVER_EXECUTION_MANIFEST_03C.json"
APPROVAL_TEMPLATE_REL = "docs/individuation/TURNOVER_EXECUTION_APPROVAL_TEMPLATE_03C.json"

# Primary manipulation check: lambda_plus is zero; lambda_minus and every other
# memory parameter are identical to the intact C1c configuration.
MEM_ABLATE_PLUS = MCParams(lam_plus=0.0, lam_minus=0.15, **C1C)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_blob_for_worktree_path(relative_path: str) -> str:
    absolute = ROOT / relative_path
    return _git("hash-object", f"--path={relative_path}", str(absolute))


def validate_execution_manifest(manifest_path: Path | None = None) -> tuple[dict, str]:
    manifest_path = manifest_path or ROOT / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_plan = manifest["seed_plan"]
    if expected_plan != {
        "primary": {"first": 54001, "last": 54050, "count": 50},
        "reserve": {"first": 54051, "last": 54096, "count": 46},
        "total_hard_cap": 96,
        "minimum_valid_worlds": 18,
    }:
        raise RuntimeError("execution manifest seed plan does not match frozen code constants")

    for relative_path, expected_blob in manifest["protected_git_blobs"].items():
        head_blob = _git("rev-parse", f"HEAD:{relative_path}")
        worktree_blob = git_blob_for_worktree_path(relative_path)
        if head_blob != expected_blob or worktree_blob != expected_blob:
            raise RuntimeError(
                f"protected artifact mismatch for {relative_path}: "
                f"HEAD={head_blob} worktree={worktree_blob} expected={expected_blob}"
            )
        if subprocess.run(["git", "diff", "--quiet", "--", relative_path], cwd=ROOT).returncode:
            raise RuntimeError(f"unstaged modification in protected artifact: {relative_path}")
        if subprocess.run(["git", "diff", "--cached", "--quiet", "--", relative_path], cwd=ROOT).returncode:
            raise RuntimeError(f"staged modification in protected artifact: {relative_path}")

    manifest_rel = str(manifest_path.relative_to(ROOT)).replace("\\", "/")
    manifest_blob = git_blob_for_worktree_path(manifest_rel)
    head_manifest_blob = _git("rev-parse", f"HEAD:{manifest_rel}")
    if manifest_blob != head_manifest_blob:
        raise RuntimeError("execution manifest working copy differs from the committed Git blob")
    return manifest, manifest_blob


def validate_human_approval(approval_path: Path, manifest: dict, manifest_blob: str) -> dict:
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("authorized") is not True:
        raise RuntimeError("prospective execution is NOT AUTHORIZED")
    if approval.get("one_execution_only") is not True:
        raise RuntimeError("approval must be explicitly limited to one execution")
    if approval.get("execution_manifest_git_blob") != manifest_blob:
        raise RuntimeError("approval is not bound to the exact execution-manifest Git blob")
    if approval.get("approval_phrase") != manifest["required_human_approval_phrase"]:
        raise RuntimeError("human approval phrase mismatch")
    for field in ("authorization_id", "approved_by", "approved_at_utc"):
        if not str(approval.get(field, "")).strip():
            raise RuntimeError(f"approval field is required: {field}")
    return approval


def feasibility_projection(record: dict) -> dict:
    """Outcome-blinded projection used by reserve activation.

    Endpoint values, labels, decoder outputs, causal contrasts, and scope
    features are unreachable from the returned object.
    """
    f = record["feasibility"]
    return {
        "seed": int(record["seed"]),
        "eligible": bool(f["eligible"]),
        "deep_reached": bool(f["deep_reached"]),
        "rest_assay_valid": bool(f["rest_assay_valid"]),
        "deep_assay_valid": bool(f["deep_assay_valid"]),
        "valid": bool(f["valid"]),
        "reason": f.get("reason"),
    }


def reserve_activation(records: Iterable[dict]) -> dict:
    views = [feasibility_projection(record) for record in records]
    by_seed = {view["seed"]: view for view in views}
    missing_primary = [seed for seed in PRIMARY_SEEDS if seed not in by_seed]
    reserve_done = sorted(seed for seed in by_seed if seed in RESERVE_SEEDS)
    expected_prefix = list(RESERVE_SEEDS[: len(reserve_done)])
    if reserve_done != expected_prefix:
        raise RuntimeError("reserve seeds must be executed in frozen ascending order")
    valid = sum(int(view["valid"]) for view in views)
    remaining = [seed for seed in RESERVE_SEEDS if seed not in by_seed]
    active = not missing_primary and valid < MIN_VALID_WORLDS and bool(remaining)
    return {
        "active": bool(active),
        "all_primary_complete": not missing_primary,
        "missing_primary": missing_primary,
        "valid_worlds": int(valid),
        "minimum_valid_worlds": MIN_VALID_WORLDS,
        "next_reserve_seed": int(remaining[0]) if active else None,
        "reserve_remaining": int(len(remaining)),
        "inputs_used": [
            "seed",
            "eligible",
            "deep_reached",
            "rest_assay_valid",
            "deep_assay_valid",
            "valid",
            "reason",
        ],
        "endpoint_fields_used": [],
        "outcome_blinded": True,
    }


def _storage_to_s0(seed: int, engine, rng: np.random.Generator) -> dict | None:
    state = cc.seed_world(seed)
    for _ in range(cc.WARM):
        state = engine.step(state)
    targets = cc.pick(sorted(detect(state, DET), key=lambda entity: -entity.size))
    if len(targets) < K:
        return None
    centroids = [entity.centroid for entity in targets]
    sigmas = [max(3.0, entity.rg * 0.8) for entity in targets]
    patches = [cc.patch(*centroids[i], sigmas[i]) for i in range(K)]
    histories = [
        (
            float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
            float(rng.uniform(cc.AMP_LO, cc.AMP_HI)),
        )
        for _ in range(K)
    ]
    dose = [first + second for first, second in histories]
    order = [second - first for first, second in histories]
    written = state.copy()
    for phase in (0, 1):
        for _ in range(cc.PHASE):
            for i in range(K):
                written.N = written.N + histories[i][phase] * patches[i]
            written = engine.step(written)
    for _ in range(cc.SETTLE):
        written = engine.step(written)
    return {
        "S0": written.copy(),
        "centroids": centroids,
        "dose": dose,
        "order": order,
        "histories": histories,
    }


def _battery(state, centroids, regions, intact_engine, full_ablation_engine, plus_ablation_engine) -> dict:
    empty = cc.empty_patch_mask(state, centroids)
    return {
        "intact": nm.measure(state, centroids, intact_engine, None),
        "sham": nm.measure(state, centroids, intact_engine, empty),
        "ablate_full": nm.measure(state, centroids, full_ablation_engine, None),
        "ablate_plus": nm.measure(state, centroids, plus_ablation_engine, None),
        "erase": [nm.measure(state, centroids, intact_engine, regions[j]) for j in range(K)],
        "erase_ablate_plus": [
            nm.measure(state, centroids, plus_ablation_engine, regions[j]) for j in range(K)
        ],
    }


def _battery_valid(battery: dict) -> bool:
    contrast = [battery["intact"], battery["sham"], *battery["erase"]]
    return bool(all(branch["branch_valid"] for branch in contrast))


def run_seed(seed: int, scope_directory: Path) -> dict:
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} is outside the sealed 54001..54096 family")
    intact = cc.build(cc.MEM_INTACT)
    full_ablation = cc.build(cc.MEM_ABLATE)
    plus_ablation = cc.build(MEM_ABLATE_PLUS)
    base = _storage_to_s0(seed, intact, np.random.default_rng(seed))
    if base is None:
        return {
            "seed": seed,
            "feasibility": {
                "eligible": False,
                "deep_reached": False,
                "rest_assay_valid": False,
                "deep_assay_valid": False,
                "valid": False,
                "reason": "fewer_than_three_geometrically_eligible_targets",
                "event_evidence": [],
            },
        }

    s0 = base["S0"]
    centroids = base["centroids"]
    regions0, _ = cc.region_masks(s0, centroids)
    rest = _battery(s0, centroids, regions0, intact, full_ablation, plus_ablation)
    rest_valid = _battery_valid(rest)
    turnover = run.turnover(s0, centroids, regions0, intact, record=True)
    if turnover["deep"] is None:
        reason = "turnover_cap_reached"
        if turnover["event_evidence"]:
            reason = ";".join(event["classification"] for event in turnover["event_evidence"])
        return {
            "seed": seed,
            "feasibility": {
                "eligible": True,
                "deep_reached": False,
                "rest_assay_valid": rest_valid,
                "deep_assay_valid": False,
                "valid": False,
                "reason": reason,
                "event_evidence": turnover["event_evidence"],
            },
            "labels": {"own_dose": base["dose"], "order_secondary": base["order"]},
            "endpoints": {"rest_behaviour": rest},
        }

    deep = turnover["deep"]
    deep_state = deep["S"]
    deep_regions = deep["regs"]
    deep_centroids = deep["cents"]

    # Feature extraction and persistence happen before any deep causal assay.
    scope_bundle = sf.extract_scope_bundle(deep_state, deep_regions, deep_centroids)
    scope_path = scope_directory / f"seed_{seed}_deep_scopes.npz"
    persisted_scope = sf.persist_scope_bundle(scope_path, scope_bundle)
    persisted_scope["path"] = os.path.relpath(scope_path, ROOT).replace("\\", "/")

    deep_battery = _battery(
        deep_state, deep_centroids, deep_regions, intact, full_ablation, plus_ablation
    )
    deep_valid = _battery_valid(deep_battery)
    valid = bool(rest_valid and deep_valid)
    return {
        "seed": seed,
        "feasibility": {
            "eligible": True,
            "deep_reached": True,
            "rest_assay_valid": rest_valid,
            "deep_assay_valid": deep_valid,
            "valid": valid,
            "reason": None if valid else "assay_geometry_invalid",
            "deep_step": int(deep["step"]),
            "deep_M": [float(value) for value in deep["M"]],
            "event_evidence": turnover["event_evidence"],
        },
        "labels": {"own_dose": base["dose"], "order_secondary": base["order"]},
        "scope_bundle": persisted_scope,
        "endpoints": {
            "histories": base["histories"],
            "rest_behaviour": rest,
            "deep_behaviour": deep_battery,
        },
    }


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def static_selfcheck() -> None:
    if len(PRIMARY_SEEDS) != 50 or len(RESERVE_SEEDS) != 46:
        raise RuntimeError("seed family count mismatch")
    if len(set(ALL_SEEDS)) != TOTAL_HARD_CAP or ALL_SEEDS != tuple(range(54001, 54097)):
        raise RuntimeError("seed family is not the exact contiguous hard cap")
    intact = MCParams(lam_plus=0.25, lam_minus=0.15, **C1C)
    for field in intact.__dataclass_fields__:
        if field == "lam_plus":
            continue
        if getattr(intact, field) != getattr(MEM_ABLATE_PLUS, field):
            raise RuntimeError(f"lambda_plus-only ablation changes {field}")
    manifest, manifest_blob = validate_execution_manifest()
    template = json.loads((ROOT / APPROVAL_TEMPLATE_REL).read_text(encoding="utf-8"))
    if template.get("authorized") is not False:
        raise RuntimeError("committed approval template must remain unauthorized")
    if template.get("execution_manifest_git_blob") != manifest_blob:
        raise RuntimeError("approval template is not bound to the exact manifest blob")
    if manifest["authorization_status"] != "AWAITING_EXPLICIT_HUMAN_APPROVAL":
        raise RuntimeError("manifest unexpectedly authorizes execution")
    print("STATIC SELF-CHECK OK — no engine instantiated; no seed executed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selfcheck", action="store_true")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--phase", choices=("primary", "reserve"))
    args = parser.parse_args()

    if args.selfcheck:
        static_selfcheck()
        return
    if args.authorization is None or args.output is None or args.phase is None:
        parser.error("--authorization, --output, and --phase are required for execution")

    manifest, manifest_blob = validate_execution_manifest()
    approval = validate_human_approval(args.authorization, manifest, manifest_blob)
    if args.output.exists():
        payload = json.loads(args.output.read_text(encoding="utf-8"))
    else:
        payload = {
            "schema": "LCI-TURNOVER-PROSPECTIVE-03C-v1",
            "execution_manifest_git_blob": manifest_blob,
            "authorization_id": approval["authorization_id"],
            "records": [],
            "activation_audit": [],
        }
    if payload["execution_manifest_git_blob"] != manifest_blob:
        raise RuntimeError("output belongs to a different execution manifest")
    if payload["authorization_id"] != approval["authorization_id"]:
        raise RuntimeError("output belongs to a different human authorization")

    records = payload["records"]
    done = {int(record["seed"]) for record in records}
    if len(done) > TOTAL_HARD_CAP:
        raise RuntimeError("hard cap exceeded")
    scope_directory = args.output.with_suffix("").with_name(args.output.stem + "_scopes")

    if args.phase == "primary":
        targets = [seed for seed in PRIMARY_SEEDS if seed not in done]
    else:
        activation = reserve_activation(records)
        payload["activation_audit"].append(activation)
        _atomic_json(args.output, payload)
        if not activation["active"]:
            raise RuntimeError(f"reserve not active: {activation}")
        targets = list(RESERVE_SEEDS)

    for seed in targets:
        if seed in done:
            continue
        if args.phase == "reserve":
            activation = reserve_activation(records)
            payload["activation_audit"].append(activation)
            if not activation["active"]:
                break
            if seed != activation["next_reserve_seed"]:
                continue
        record = run_seed(seed, scope_directory)
        records.append(record)
        done.add(seed)
        _atomic_json(args.output, payload)
        print(
            f"seed {seed}: eligible={record['feasibility']['eligible']} "
            f"valid={record['feasibility']['valid']}"
        )
        if args.phase == "reserve" and reserve_activation(records)["valid_worlds"] >= MIN_VALID_WORLDS:
            break


if __name__ == "__main__":
    main()
