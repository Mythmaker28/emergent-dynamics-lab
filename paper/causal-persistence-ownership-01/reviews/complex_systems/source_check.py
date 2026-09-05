"""Read-only scientific source check; no scientific engine imports or worlds."""
from pathlib import Path
from collections import Counter
import ast
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = Path(__file__).resolve().parents[2]
REVISION = "06fd9524f5c7ffb329ee850a10bd9959f2f0bde5"


def verified_inputs():
    """Prefer the portable paper; fail closed if its manifest is inconsistent."""
    manifest_path = PAPER / "INPUT_MANIFEST.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["source_commit"] != REVISION:
            raise ValueError("Unexpected paper source revision")
        for item in manifest["files"]:
            path = (PAPER / item["path"]).resolve()
            if not path.is_relative_to(PAPER.resolve()):
                raise ValueError("Manifest path escapes the paper directory")
            content = path.read_bytes()
            if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
                raise ValueError("Input integrity mismatch: " + item["path"])
        return {
            "mode": "STANDALONE_PAPER_INPUTS",
            "manifest_files_verified": len(manifest["files"]),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        }
    return {"mode": "AUDIT_SNAPSHOT_AND_PINNED_GIT", "manifest_files_verified": 0}


def main():
    inputs = verified_inputs()
    raw = (PAPER / "data/results/LCI-TURNOVER-PROSPECTIVE-03G/raw"
           if inputs["mode"] == "STANDALONE_PAPER_INPUTS"
           else ROOT / "audit/edl-flagship-01/candidate_b/results/LCI-TURNOVER-PROSPECTIVE-03G/raw")
    worlds = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(raw.glob("seed_*.json"))]
    if len(worlds) != 50:
        raise ValueError("Expected exactly 50 persisted prospective worlds")
    valid = [w for w in worlds if w["feasibility"]["valid"]]
    material = [m for w in valid for m in w["scientific"]["material_tracer"]["deep_M"]]
    refs = {
        "engine": "edlab/experiments/sc_mcm/engine.py",
        "scopes_03e": "experiments/individuation/turnover_scope_features_03e.py",
        "scopes_03g": "experiments/individuation/turnover_scope_features_03g.py",
        "scaffold": "edlab/substrates/scaffold/engine.py",
        "hmc_config": "edlab/experiments/sc_hmc/config.py",
        "memory_neighbour_mean": "edlab/experiments/sc_iom/engine.py",
        "causal_constants": "experiments/individuation/causal_confirm.py",
        "material_tracer": "experiments/individuation/material_tracer.py",
        "storage_history": "experiments/individuation/turnover_engine_03g.py",
        "initial_state": "edlab/experiments/exp_sc_00.py",
    }
    blobs = {}
    source = {}
    for label, path in refs.items():
        if inputs["mode"] == "STANDALONE_PAPER_INPUTS":
            content = (PAPER / "source_model" / path).read_bytes()
        else:
            content = subprocess.check_output(["git", "show", REVISION + ":" + path], cwd=ROOT)
        source[label] = content.decode("utf-8")
        blobs[label] = {"path": path, "revision": REVISION, "sha256": hashlib.sha256(content).hexdigest()}
    def defaults(label, classname):
        cls = next(n for n in ast.parse(source[label]).body if isinstance(n, ast.ClassDef) and n.name == classname)
        return {n.target.id: ast.literal_eval(n.value) for n in cls.body if isinstance(n, ast.AnnAssign)}
    scaffold = defaults("scaffold", "ScaffoldSpec")
    beta_node = next(n for n in ast.parse(source["hmc_config"]).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BETA" for t in n.targets))
    scaffold["beta"] = ast.literal_eval(beta_node.value)
    memory = defaults("engine", "MCParams")
    c1c = next(n for n in ast.parse(source["causal_constants"]).body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "C1c" for t in n.targets))
    memory.update({kw.arg: ast.literal_eval(kw.value) for kw in c1c.value.keywords})
    recorded_cross = [sum(p["M"]["cross"].values()) for w in valid for t in w["scientific"]["material_tracer"]["trajectory"] for p in t["per"] if p and p.get("M") and "cross" in p["M"]]
    ablation_branches_checked = 0
    invalid_ablation_branches = []
    for world in valid:
        for timing, battery in world["scientific"]["causal_intervention_battery"].items():
            for key in ("ablate_plus", "erase_ablate_plus", "ablate_full", "erase_ablate_full"):
                branches = battery[key] if isinstance(battery[key], list) else [battery[key]]
                for index, branch in enumerate(branches):
                    ablation_branches_checked += 1
                    if not branch["branch_valid"]:
                        invalid_ablation_branches.append({"seed": world["seed"], "timing": timing,
                                                         "branch": key, "index": index})
    result = {
        "inputs": inputs,
        "worlds": len(worlds), "valid_worlds": len(valid), "valid_seeds": [w["seed"] for w in valid],
        "invalid_reasons": dict(Counter(w["feasibility"]["reason"] for w in worlds if not w["feasibility"]["valid"])),
        "target_material_values": len(material), "min_own_snapshot_material_fraction": min(material),
        "max_own_snapshot_material_fraction": max(material), "mean_own_snapshot_material_fraction": sum(material) / len(material),
        "all_valid_targets_retain_positive_own_snapshot_material": all(m > 0 for m in material),
        "all_valid_targets_meet_quarter_bound": all(m <= 0.25 for m in material),
        "maximum_cross_target_fraction_at_recorded_frames": max(recorded_cross),
        "cross_target_observations": len(recorded_cross),
        "ablation_branches_checked_in_valid_worlds": ablation_branches_checked,
        "invalid_ablation_branches_in_valid_worlds": invalid_ablation_branches,
        "material_interpretation": "Own-mask snapshot label only. Unlabelled remainder may be fresh feed or initially outside target masks. Recorded frames are not necessarily exact deep snapshot.",
        "scaffold_parameters": scaffold, "memory_parameters": memory,
        "effective_memory_laplacian_coefficient": memory["D_m"] + memory["eta_t"] / 4,
        "source_blobs": blobs,
        "scope": "Persisted per-world scientific records and static code only; not engine reproduction.",
    }
    (OUT / "SOURCE_CHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"source_blobs", "invalid_reasons", "valid_seeds"}}, indent=2))


if __name__ == "__main__":
    main()
