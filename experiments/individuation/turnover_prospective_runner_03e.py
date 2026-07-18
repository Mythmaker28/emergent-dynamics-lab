"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — repaired hash-gated prospective runner (supersedes 03C runner).

Wires the three repaired code blockers:
  B1  one-shot, hash-chained execution ledger + FINAL_SEAL binding  (turnover_execution_ledger)
  B2  repaired ownership + causal-expression gates                  (turnover_statistics_03e, used by analysis)
  B3  low-dimensional frozen E/Gm/Gf access features (<=24)          (turnover_scope_features_03e)

Fail-closed: requires an approval JSON bound to the exact FINAL_SEAL sha256 AND the execution-manifest blob. Refuses
any second FRESH execution once the canonical run ledger exists. `--selfcheck` is fully static: no engine, no seed,
no authorization consumed. NO 54xxx seed is executed by this repair.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _load(name: str, filename: str):
    import sys
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cc = _load("cc", "causal_confirm.py")
nm = _load("nm", "nonmerging_confirm.py")
run = _load("run", "turnover_dev_runner.py")
sf = _load("sf03e", "turnover_scope_features_03e.py")
ledger = _load("ledger", "turnover_execution_ledger.py")

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
MEM_ABLATE_PLUS = MCParams(lam_plus=0.0, lam_minus=0.15, **C1C)

MANIFEST_REL = "docs/individuation/TURNOVER_EXECUTION_MANIFEST_03E.json"
SEAL_REL = "docs/individuation/FINAL_SEAL_MANIFEST_03E.json"   # created ONLY by a future fresh sealing agent
APPROVAL_TEMPLATE_REL = "docs/individuation/TURNOVER_EXECUTION_APPROVAL_TEMPLATE_03E.json"
CODE_FILES = (
    "experiments/individuation/turnover_prospective_runner_03e.py",
    "experiments/individuation/turnover_statistics_03e.py",
    "experiments/individuation/turnover_scope_features_03e.py",
    "experiments/individuation/turnover_execution_ledger.py",
    "experiments/individuation/turnover_dev_runner.py",
    "experiments/individuation/causal_confirm.py",
    "experiments/individuation/nonmerging_confirm.py",
)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def code_hashes() -> dict:
    return {rel: _git("hash-object", str(ROOT / rel)) for rel in CODE_FILES}


def environment_hash() -> str:
    lock = (ROOT / "docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03E.txt")
    return ledger.sha256_file(lock) if lock.exists() else "ENV_LOCK_ABSENT"


def _battery(state, centroids, regions, intact_engine, full_ablation_engine, plus_ablation_engine) -> dict:
    empty = cc.empty_patch_mask(state, centroids)
    return {
        "intact": nm.measure(state, centroids, intact_engine, None),
        "sham": nm.measure(state, centroids, intact_engine, empty),
        "ablate_full": nm.measure(state, centroids, full_ablation_engine, None),
        "ablate_plus": nm.measure(state, centroids, plus_ablation_engine, None),
        "erase": [nm.measure(state, centroids, intact_engine, regions[j]) for j in range(K)],
        "erase_ablate_plus": [nm.measure(state, centroids, plus_ablation_engine, regions[j]) for j in range(K)],
    }


def _storage_to_s0(seed, engine, rng):
    state = cc.seed_world(seed)
    for _ in range(cc.WARM):
        state = engine.step(state)
    targets = cc.pick(sorted(detect(state, DET), key=lambda e: -e.size))
    if len(targets) < K:
        return None
    centroids = [e.centroid for e in targets]
    sigmas = [max(3.0, e.rg * 0.8) for e in targets]
    patches = [cc.patch(*centroids[i], sigmas[i]) for i in range(K)]
    hist = [(float(rng.uniform(cc.AMP_LO, cc.AMP_HI)), float(rng.uniform(cc.AMP_LO, cc.AMP_HI))) for _ in range(K)]
    written = state.copy()
    for phase in (0, 1):
        for _ in range(cc.PHASE):
            for i in range(K):
                written.N = written.N + hist[i][phase] * patches[i]
            written = engine.step(written)
    for _ in range(cc.SETTLE):
        written = engine.step(written)
    return {"S0": written.copy(), "centroids": centroids,
            "dose": [a + b for a, b in hist], "order": [b - a for a, b in hist]}


def run_seed(seed: int, scope_directory: Path) -> dict:
    """Frozen per-seed run. Uses the LOW-DIM 03E scope extractor. NOT executed by this repair (guarded in main)."""
    if seed not in ALL_SEEDS:
        raise ValueError(f"seed {seed} outside sealed family")
    intact = cc.build(cc.MEM_INTACT)
    full_ablation = cc.build(cc.MEM_ABLATE)
    plus_ablation = cc.build(MEM_ABLATE_PLUS)
    base = _storage_to_s0(seed, intact, np.random.default_rng(seed))
    if base is None:
        return {"seed": seed, "feasibility": {"eligible": False, "deep_reached": False, "rest_assay_valid": False,
                                              "deep_assay_valid": False, "valid": False,
                                              "reason": "fewer_than_three_geometrically_eligible_targets"}}
    s0, centroids = base["S0"], base["centroids"]
    regions0, _ = cc.region_masks(s0, centroids)
    rest = _battery(s0, centroids, regions0, intact, full_ablation, plus_ablation)
    rest_valid = bool(all(b["branch_valid"] for b in [rest["intact"], rest["sham"], *rest["erase"]]))
    turnover = run.turnover(s0, centroids, regions0, intact, record=True)
    if turnover["deep"] is None:
        return {"seed": seed, "feasibility": {"eligible": True, "deep_reached": False, "rest_assay_valid": rest_valid,
                                              "deep_assay_valid": False, "valid": False, "reason": "turnover_cap_or_censor"},
                "labels": {"own_dose": base["dose"], "order_secondary": base["order"]}}
    deep = turnover["deep"]
    bundle = sf.extract_scope_bundle_03e(deep["S"], deep["regs"], deep["cents"])   # LOW-DIM E/Gm/Gf
    scope_path = scope_directory / f"seed_{seed}_deep_scopes.npz"
    persisted = sf.persist_scope_bundle_03e(scope_path, bundle)
    deep_battery = _battery(deep["S"], deep["cents"], deep["regs"], intact, full_ablation, plus_ablation)
    deep_valid = bool(all(b["branch_valid"] for b in [deep_battery["intact"], deep_battery["sham"], *deep_battery["erase"]]))
    return {"seed": seed,
            "feasibility": {"eligible": True, "deep_reached": True, "rest_assay_valid": rest_valid,
                            "deep_assay_valid": deep_valid, "valid": bool(rest_valid and deep_valid),
                            "reason": None if (rest_valid and deep_valid) else "assay_geometry_invalid",
                            "deep_step": int(deep["step"]), "deep_M": [float(m) for m in deep["M"]]},
            "labels": {"own_dose": base["dose"], "order_secondary": base["order"]},
            "scope_bundle": persisted,
            "endpoints": {"rest_behaviour": rest, "deep_behaviour": deep_battery}}


def feasibility_projection(record: dict) -> dict:
    f = record["feasibility"]
    return {"seed": int(record["seed"]), "eligible": bool(f["eligible"]), "deep_reached": bool(f["deep_reached"]),
            "rest_assay_valid": bool(f["rest_assay_valid"]), "deep_assay_valid": bool(f["deep_assay_valid"]),
            "valid": bool(f["valid"]), "reason": f.get("reason")}


def static_selfcheck() -> None:
    assert len(PRIMARY_SEEDS) == 50 and len(RESERVE_SEEDS) == 46
    assert ALL_SEEDS == tuple(range(54001, 54097)) and len(set(ALL_SEEDS)) == TOTAL_HARD_CAP
    intact = MCParams(lam_plus=0.25, lam_minus=0.15, **C1C)
    for field in intact.__dataclass_fields__:
        if field != "lam_plus":
            assert getattr(intact, field) == getattr(MEM_ABLATE_PLUS, field), f"lambda_plus-only changes {field}"
    # wiring: repaired modules import and expose the required entry points
    assert hasattr(sf, "extract_scope_bundle_03e") and hasattr(ledger, "start_or_resume") and hasattr(ledger, "validate_authorization")
    st = _load("st03e", "turnover_statistics_03e.py")
    assert hasattr(st, "evaluate_ownership_03e") and hasattr(st, "causal_expression_gate") and hasattr(st, "primary_gate")
    tree = json.loads((ROOT / "docs/individuation/TURNOVER_DECISION_TREE_03E.json").read_text(encoding="utf-8"))
    assert set(tree["outcomes"]) == {"A", "B", "C", "D", "E", "F"}
    print("STATIC SELF-CHECK OK — ledger + low-dim scopes + repaired gates + A-F tree wired; no engine; no seed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selfcheck", action="store_true")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--phase", choices=("primary", "reserve"))
    args = parser.parse_args()
    if args.selfcheck:
        static_selfcheck()
        return
    if not (ROOT / SEAL_REL).exists():
        raise SystemExit("⛔ NO FINAL_SEAL_MANIFEST_03E.json: this repair does not seal. A fresh sealing+audit agent "
                         "must create the seal after re-audit. Execution is refused.")
    if args.authorization is None or args.run_dir is None or args.phase is None:
        parser.error("--authorization, --run-dir, and --phase are required for execution")
    seal_sha = ledger.sha256_file(ROOT / SEAL_REL)
    manifest = json.loads((ROOT / MANIFEST_REL).read_text(encoding="utf-8"))
    manifest_blob = _git("hash-object", str(ROOT / MANIFEST_REL))
    approval = json.loads(args.authorization.read_text(encoding="utf-8"))
    ledger.validate_authorization(approval, seal_sha, manifest_blob, manifest["required_human_approval_phrase"])
    start = {"authorization_id": approval["authorization_id"], "final_seal_sha256": seal_sha,
             "execution_manifest_git_blob": manifest_blob, "code_hashes": code_hashes(),
             "environment_hash": environment_hash(), "seed_family": {"primary": "54001-54050", "reserve": "54051-54096"}}
    state = ledger.start_or_resume(args.run_dir, start)
    raise SystemExit(f"AUTHORIZED RUN INITIALIZED ({state['mode']}); this repair mission does NOT execute seeds. "
                     f"A fresh execution agent runs seeds only after independent re-audit of the seal.")


if __name__ == "__main__":
    main()
