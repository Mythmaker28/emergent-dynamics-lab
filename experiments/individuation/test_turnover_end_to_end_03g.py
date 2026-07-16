"""Production-path integration tests for turnover PRESEAL 03G. No engine and no 54xxx seed."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import turnover_analyzer_03g as analyzer
import turnover_ledger_03g as ledger
import turnover_raw_schema_03g as raw
import turnover_runner_03g as runner
import turnover_scope_features_03g as scopes

SAFE_SEEDS = list(range(61001, 61019))
PROTECTED = (
    "experiments/individuation/turnover_runner_03g.py",
    "experiments/individuation/turnover_ledger_03g.py",
    "experiments/individuation/turnover_raw_schema_03g.py",
    "experiments/individuation/turnover_engine_03g.py",
    "experiments/individuation/turnover_scope_features_03g.py",
    "experiments/individuation/turnover_statistics_03g.py",
    "experiments/individuation/turnover_analyzer_03g.py",
    "docs/individuation/TURNOVER_DECISION_TREE_03G.json",
    "docs/individuation/TURNOVER_RAW_SCHEMA_03G.json",
    "docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03G.txt",
)


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", "--path", str(path.relative_to(ROOT)), str(path)],
        cwd=ROOT,
        text=True,
    ).strip()


def protected_files() -> dict:
    return {
        rel: {"git_blob": git_blob(ROOT / rel), "sha256": raw.sha256_file(ROOT / rel)}
        for rel in PROTECTED
    }


def seed_plan(seeds: list[int], minimum: int) -> dict:
    return {
        "primary": {"first": seeds[0], "last": seeds[-1], "count": len(seeds)},
        "reserve": {"first": 0, "last": -1, "count": 0},
        "total_hard_cap": len(seeds),
        "minimum_valid_worlds": minimum,
    }


class Fixture:
    def __init__(self, root: Path, name: str, seeds: list[int], minimum: int, style: str):
        self.root = root
        self.dir = root / name
        self.dir.mkdir()
        self.run_rel = str(self.dir.relative_to(ROOT) / "run").replace("\\", "/")
        self.manifest_path = self.dir / "manifest.json"
        self.seal_path = self.dir / "seal.json"
        self.auth_path = self.dir / "authorization.json"
        self.style = style
        self.seeds = seeds
        self.minimum = minimum
        self._write()

    def _write(self):
        lock = "docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03G.txt"
        manifest = {
            "schema": "LCI-TURNOVER-EXECUTION-MANIFEST-03G-v1",
            "mode": "SYNTHETIC_TEST",
            "watermark": "DEV/EXPLORATORY/SYNTHETIC_TEST - NOT A SCIENTIFIC RESULT",
            "canonical_run_directory": self.run_rel,
            "seed_plan": seed_plan(self.seeds, self.minimum),
            "authorization": {
                "required_phrase": "DEV TEST AUTHORIZATION - NOT PROSPECTIVE"
            },
            "analysis": {
                "decision_tree": "docs/individuation/TURNOVER_DECISION_TREE_03G.json",
                "permutation_reps": 1000,
            },
            "environment": {
                "lock": lock,
                "lock_sha256": raw.sha256_file(ROOT / lock),
                "runtime": runner.runtime_environment(),
            },
            "protected_files": protected_files(),
        }
        raw.atomic_write_json(self.manifest_path, manifest)
        manifest_sha = raw.sha256_file(self.manifest_path)
        manifest_blob = git_blob(self.manifest_path)
        seal = {
            "schema": "LCI-TURNOVER-SEAL-03G-v1",
            "mode": "SYNTHETIC_TEST",
            "execution_manifest": {
                "path": str(self.manifest_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": manifest_sha,
                "git_blob": manifest_blob,
            },
            "protected_files": manifest["protected_files"],
            "environment_lock_sha256": manifest["environment"]["lock_sha256"],
            "family_sha256": runner.family_sha256(manifest),
            "watermark": manifest["watermark"],
        }
        raw.atomic_write_json(self.seal_path, seal)
        seal_sha = raw.sha256_file(self.seal_path)
        auth = {
            "schema": "LCI-TURNOVER-DEV-AUTHORIZATION-03G-v1",
            "dev_authorized": True,
            "prospective_authorized": False,
            "authorization_id": f"DEV-{self.dir.name}",
            "approved_by": "DEV TEST FIXTURE - NOT A HUMAN AUTHORIZATION",
            "approved_at_utc": "2026-07-16T00:00:00Z",
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
            "family_sha256": runner.family_sha256(manifest),
            "canonical_run_directory": self.run_rel,
            "approval_phrase": manifest["authorization"]["required_phrase"],
        }
        raw.atomic_write_json(self.auth_path, auth)

    @property
    def run_dir(self) -> Path:
        return ROOT / self.run_rel

    def execute(self, **kwargs):
        return runner.execute_pipeline(
            self.manifest_path,
            self.seal_path,
            self.auth_path,
            seed_executor=synthetic_executor(self.style),
            **kwargs,
        )


def causal_battery(passes: bool) -> dict:
    k = 3
    own = 0.20 if passes else 0.0
    neighbour = 0.02 if passes else 0.0
    plus = 0.02 if passes else 0.0
    intact = {"tracked": [1.0] * k, "fixed": [1.0] * k}
    erase = []
    erase_plus = []
    for erased in range(k):
        erase.append(
            {
                "tracked": [
                    1.0 - (own if target == erased else neighbour) for target in range(k)
                ],
                "fixed": [1.0 - (own if target == erased else 0.0) for target in range(k)],
            }
        )
        erase_plus.append(
            {
                "tracked": [
                    0.3 - (plus if target == erased else 0.0) for target in range(k)
                ]
            }
        )
    return {
        "intact": intact,
        "sham": {"tracked": [1.0] * k},
        "erase": erase,
        "ablate_plus": {"tracked": [0.3] * k},
        "erase_ablate_plus": erase_plus,
    }


def scope_values(seed: int, style: str) -> tuple[dict, list[float]]:
    rng = np.random.default_rng(seed)
    y = rng.uniform(0.01, 0.07, 3)

    def noise(rows: int, cols: int):
        return rng.normal(0.0, 1.0, (rows, cols))

    local_signal = style in {"A", "C"}
    distributed_signal = style == "F"
    local = noise(3, 11)
    if local_signal:
        local[:, 0] = y + rng.normal(0.0, 1e-5, 3)
    nearest = noise(3, 11)
    far = noise(3, 11)
    environment = noise(3, 24)
    global_minus = noise(3, 18)
    if distributed_signal:
        environment[:, 0] = y + rng.normal(0.0, 1e-5, 3)
    body = noise(3, 8)
    values = {
        "L": local.tolist(),
        "N": nearest.tolist(),
        "P": np.concatenate([local, nearest, far], axis=1).tolist(),
        "E": environment.tolist(),
        "Gm": global_minus.tolist(),
        "Gf": np.concatenate([local, global_minus], axis=1).tolist(),
        "B": body.tolist(),
    }
    return values, y.tolist()


def synthetic_executor(style: str):
    def execute(seed: int, context: dict) -> dict:
        valid = style != "E"
        values, dose = scope_values(seed, style)
        causal = style in {"A", "B"}
        battery = causal_battery(causal)
        return {
            "schema": raw.RAW_SCHEMA,
            "mode": context["mode"],
            "watermark": context["watermark"],
            "seed": seed,
            "world_id": seed,
            "bindings": context["bindings"],
            "feasibility": {
                "eligible": True,
                "deep_reached": valid,
                "rest_assay_valid": valid,
                "deep_assay_valid": valid,
                "valid": valid,
                "reason": None if valid else "synthetic_feasibility_failure",
            },
            "scientific": {
                "histories": {
                    "phase_amplitudes": [[value / 2, value / 2] for value in dose],
                    "own_dose": dose,
                    "order_secondary": [0.0, 0.0, 0.0],
                    "primary_coordinate": "own cumulative dose / m-plus",
                },
                "target_ids": [0, 1, 2],
                "target_centroids": [[0.0, 0.0], [0.0, 24.0], [24.0, 0.0]],
                "g0": {"rest_valid": valid, "deep_valid": valid},
                "material_tracer": {"trajectory": [], "deep_M": [0.2, 0.2, 0.2], "tracer_base": 100},
                "tracking_event_evidence": [],
                "scopes": None
                if not valid
                else {
                    "schema": scopes.SCOPE_VERSION,
                    "dims": scopes.DIMS,
                    "feature_names": {},
                    "gated_scopes": ["L", "N", "E", "Gm", "B"],
                    "diagnostic_scopes": ["P", "Gf"],
                    "Gf_definition": "exact concatenation of L followed by G-minus-target",
                    "Gf_L_slice": [0, 11],
                    "neighbour_order": [[1, 2], [0, 2], [0, 1]],
                    "values": values,
                    "label_fields_present": False,
                    "diagnostic_cohorts_present": False,
                },
                "causal_intervention_battery": {
                    "rest": battery if valid else None,
                    "deep": battery if valid else None,
                },
                "lambda_plus_only_control": {
                    "lam_plus": 0.0,
                    "lam_minus": 0.15,
                    "rest": None,
                    "deep": None,
                },
                "censoring_reason": None if valid else "synthetic_feasibility_failure",
                "snapshot_time": 100 if valid else None,
            },
        }

    return execute


class EndToEnd03GTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=ROOT, prefix=".turnover03g-tests-")
        cls.root = Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def new_fixture(self, name: str, style: str, *, seeds=None, minimum=18):
        return Fixture(self.root, name, seeds or SAFE_SEEDS, minimum, style)

    def test_all_A_to_F_fixtures_use_production_runner_validator_and_analyzer(self):
        observed = {}
        for outcome in "ABCDEF":
            seeds = SAFE_SEEDS if outcome != "E" else SAFE_SEEDS[:3]
            fixture = self.new_fixture(f"outcome-{outcome}", outcome, seeds=seeds)
            result = fixture.execute()
            certificate = json.loads(
                (fixture.run_dir / result["analysis"]["path"]).read_text(encoding="utf-8")
            )
            observed[outcome] = certificate["outcome"]
            self.assertEqual(certificate["outcome"], outcome)
            self.assertTrue(certificate["numbers_trace_to_raw_sha256"])
        self.assertEqual(observed, {letter: letter for letter in "ABCDEF"})

    def test_seal_code_analysis_family_environment_and_authorization_tamper_fail_closed(self):
        cases = []
        fixture = self.new_fixture("tamper-seal", "E", seeds=SAFE_SEEDS[:1])
        seal = json.loads(fixture.seal_path.read_text())
        seal["family_sha256"] = "0" * 64
        raw.atomic_write_json(fixture.seal_path, seal, overwrite=True)
        cases.append(fixture)

        fixture = self.new_fixture("incomplete-seal", "E", seeds=SAFE_SEEDS[:1])
        seal = json.loads(fixture.seal_path.read_text())
        seal["protected_files"].pop("experiments/individuation/turnover_analyzer_03g.py")
        raw.atomic_write_json(fixture.seal_path, seal, overwrite=True)
        cases.append(fixture)

        fixture = self.new_fixture("tamper-code", "E", seeds=SAFE_SEEDS[:1])
        manifest = json.loads(fixture.manifest_path.read_text())
        manifest["protected_files"]["experiments/individuation/turnover_runner_03g.py"]["sha256"] = "0" * 64
        raw.atomic_write_json(fixture.manifest_path, manifest, overwrite=True)
        self._reseal_and_reauthorize(fixture)
        cases.append(fixture)

        fixture = self.new_fixture("tamper-analysis", "E", seeds=SAFE_SEEDS[:1])
        manifest = json.loads(fixture.manifest_path.read_text())
        manifest["protected_files"]["experiments/individuation/turnover_analyzer_03g.py"]["git_blob"] = "0" * 40
        raw.atomic_write_json(fixture.manifest_path, manifest, overwrite=True)
        self._reseal_and_reauthorize(fixture)
        cases.append(fixture)

        fixture = self.new_fixture("tamper-family", "E", seeds=SAFE_SEEDS[:1])
        manifest = json.loads(fixture.manifest_path.read_text())
        manifest["seed_plan"]["minimum_valid_worlds"] = 99
        raw.atomic_write_json(fixture.manifest_path, manifest, overwrite=True)
        cases.append(fixture)

        fixture = self.new_fixture("tamper-auth", "E", seeds=SAFE_SEEDS[:1])
        auth = json.loads(fixture.auth_path.read_text())
        auth["seal_sha256"] = "0" * 64
        raw.atomic_write_json(fixture.auth_path, auth, overwrite=True)
        cases.append(fixture)

        for case in cases:
            with self.assertRaises(runner.ExecutionError, msg=case.dir.name):
                case.execute()

        fixture = self.new_fixture("wrong-env", "E", seeds=SAFE_SEEDS[:1])
        wrong = runner.runtime_environment()
        wrong["python"] = "0.0.0"
        with self.assertRaises(runner.ExecutionError):
            fixture.execute(actual_environment=wrong)

    def _reseal_and_reauthorize(self, fixture: Fixture):
        manifest = json.loads(fixture.manifest_path.read_text())
        seal = {
            "schema": "LCI-TURNOVER-SEAL-03G-v1",
            "mode": manifest["mode"],
            "execution_manifest": {
                "path": str(fixture.manifest_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": raw.sha256_file(fixture.manifest_path),
                "git_blob": git_blob(fixture.manifest_path),
            },
            "protected_files": manifest["protected_files"],
            "environment_lock_sha256": manifest["environment"]["lock_sha256"],
            "family_sha256": runner.family_sha256(manifest),
            "watermark": manifest["watermark"],
        }
        raw.atomic_write_json(fixture.seal_path, seal, overwrite=True)
        auth = json.loads(fixture.auth_path.read_text())
        auth.update(
            {
                "seal_sha256": raw.sha256_file(fixture.seal_path),
                "execution_manifest_sha256": raw.sha256_file(fixture.manifest_path),
                "execution_manifest_git_blob": git_blob(fixture.manifest_path),
                "runner_git_blob": manifest["protected_files"][
                    "experiments/individuation/turnover_runner_03g.py"
                ]["git_blob"],
                "analyzer_git_blob": manifest["protected_files"][
                    "experiments/individuation/turnover_analyzer_03g.py"
                ]["git_blob"],
                "family_sha256": runner.family_sha256(manifest),
            }
        )
        raw.atomic_write_json(fixture.auth_path, auth, overwrite=True)

    def test_second_fresh_refused_and_explicit_resume_is_idempotent(self):
        fixture = self.new_fixture("replay", "E", seeds=SAFE_SEEDS[:2])
        fixture.execute()
        with self.assertRaises(ledger.LedgerError):
            fixture.execute()
        resumed = fixture.execute(resume=True)
        self.assertEqual(resumed["status"], "already_certified")

    def test_interrupted_seed_resumes_without_overwriting_completed_raw(self):
        fixture = self.new_fixture("resume", "E", seeds=SAFE_SEEDS[:2])
        calls = {"n": 0}

        def interrupted(seed, context):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("synthetic interruption")
            return synthetic_executor("E")(seed, context)

        with self.assertRaises(RuntimeError):
            runner.execute_pipeline(
                fixture.manifest_path,
                fixture.seal_path,
                fixture.auth_path,
                seed_executor=interrupted,
            )
        result = runner.execute_pipeline(
            fixture.manifest_path,
            fixture.seal_path,
            fixture.auth_path,
            resume=True,
            seed_executor=interrupted,
        )
        self.assertEqual(result["ledger"]["state"], "CERTIFIED")
        self.assertEqual(len(list((fixture.run_dir / "raw").glob("*.json"))), 2)

    def test_invalid_transition_wrong_seed_reorder_truncation_and_raw_tamper_are_rejected(self):
        fixture = self.new_fixture("integrity", "E", seeds=SAFE_SEEDS[:2])
        fixture.execute()
        with self.assertRaises(ledger.LedgerError):
            ledger.transition(fixture.run_dir, "START_PRIMARY")

        ledger_path = fixture.run_dir / ledger.LEDGER_NAME
        anchor_path = fixture.run_dir / ledger.ANCHOR_NAME
        original_ledger = ledger_path.read_bytes()
        original_anchor = anchor_path.read_bytes()
        lines = ledger_path.read_text().splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        ledger_path.write_text("\n".join(lines) + "\n")
        with self.assertRaises(ledger.LedgerError):
            ledger.verify(fixture.run_dir)
        ledger_path.write_bytes(original_ledger)
        anchor_path.write_bytes(original_anchor)

        lines = ledger_path.read_text().splitlines()
        ledger_path.write_text("\n".join(lines[:-1]) + "\n")
        with self.assertRaises(ledger.LedgerError):
            ledger.verify(fixture.run_dir)
        ledger_path.write_bytes(original_ledger)
        anchor_path.write_bytes(original_anchor)

        manifest = json.loads((fixture.run_dir / "raw_manifest_03g.json").read_text())
        raw_path = fixture.run_dir / manifest["entries"][0]["path"]
        original_raw = raw_path.read_bytes()
        raw_path.write_bytes(original_raw + b" ")
        with self.assertRaises(raw.RawSchemaError):
            raw.validate_raw_manifest(manifest, fixture.run_dir)
        raw_path.write_bytes(original_raw)

    def test_wrong_seed_mixed_schema_duplicate_world_and_reserve_blinding(self):
        run_dir = self.root / "ledger-unit"
        binding = {"x": 1}
        ledger.initialize(run_dir, binding, resume=False)
        ledger.transition(run_dir, "AUTHORIZE")
        ledger.transition(run_dir, "START_PRIMARY")
        with self.assertRaises(ledger.LedgerError):
            ledger.record_seed_started(run_dir, 99999, SAFE_SEEDS[0])

        fixture = self.new_fixture("mixed-schema", "E", seeds=SAFE_SEEDS[:2])
        fixture.execute()
        manifest = json.loads((fixture.run_dir / "raw_manifest_03g.json").read_text())
        manifest["entries"][0]["schema"] = "OLD"
        with self.assertRaises(raw.RawSchemaError):
            raw.validate_raw_manifest(manifest, fixture.run_dir)

        fixture = self.new_fixture("duplicate-content", "A")
        first_values = scope_values(SAFE_SEEDS[0], "A")[0]

        def duplicate_executor(seed, context):
            record = synthetic_executor("A")(seed, context)
            if seed == SAFE_SEEDS[1]:
                record["scientific"]["scopes"]["values"]["L"] = first_values["L"]
            return record

        with self.assertRaises(ValueError):
            runner.execute_pipeline(
                fixture.manifest_path,
                fixture.seal_path,
                fixture.auth_path,
                seed_executor=duplicate_executor,
            )

        fixture = self.new_fixture("reserve-fields", "E", seeds=SAFE_SEEDS[:2])
        fixture.execute()
        decision = [
            event for event in ledger.entries(fixture.run_dir) if event["event"] == "DECIDE_RESERVE"
        ][0]
        self.assertEqual(decision["outcome_fields_used"], [])
        self.assertEqual(
            set(decision["fields_used"]),
            set(raw.FEASIBILITY_FIELDS),
        )

    def test_G_full_exactly_nests_L_and_dimensions_are_frozen(self):
        values, _ = scope_values(SAFE_SEEDS[0], "A")
        self.assertEqual(scopes.DIMS, {"L": 11, "N": 11, "P": 33, "B": 8, "E": 24, "Gm": 18, "Gf": 29})
        self.assertTrue(
            np.array_equal(
                np.asarray(values["Gf"], dtype=np.float64)[:, :11],
                np.asarray(values["L"], dtype=np.float64),
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
