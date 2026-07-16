"""Non-simulation unit tests for the turnover PRESEAL 03C reconciliation."""
from __future__ import annotations

import copy
import importlib.util
import inspect
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


statistics = load("turnover_statistics_test", "turnover_statistics.py")
scopes = load("turnover_scope_features_test", "turnover_scope_features.py")
events = load("turnover_event_evidence_test", "turnover_event_evidence.py")
runner = load("turnover_prospective_runner_test", "turnover_prospective_runner.py")
analyzer = load("turnover_ownership_analyze_test", "turnover_ownership_analyze.py")


class DummyState:
    def __init__(self, size: int = 16):
        yy, xx = np.mgrid[0:size, 0:size]
        self.rho = 1.0 + 0.01 * yy
        self.U = self.rho * (0.2 + 0.001 * xx)
        self.V = self.rho * (0.1 + 0.001 * yy)
        self.c = 0.3 + 0.002 * xx
        self.N = 0.8 + 0.002 * yy
        self.uptake = 0.01 + 0.0001 * (xx + yy)
        self.Mf = np.zeros((2, size, size), dtype=float)


def block(size: int, r0: int, r1: int, c0: int, c1: int) -> np.ndarray:
    mask = np.zeros((size, size), dtype=bool)
    mask[r0:r1, c0:c1] = True
    return mask


def feasibility_record(seed: int, valid: bool, endpoint_value: float = 0.0) -> dict:
    return {
        "seed": seed,
        "feasibility": {
            "eligible": True,
            "deep_reached": valid,
            "rest_assay_valid": valid,
            "deep_assay_valid": valid,
            "valid": valid,
            "reason": None if valid else "feasibility_only",
        },
        "labels": {"own_dose": [endpoint_value] * 3},
        "endpoints": {"arbitrary_outcome": endpoint_value},
    }


class GroupedInferenceTests(unittest.TestCase):
    def test_outer_worlds_are_disjoint_and_bootstrap_does_not_refit(self):
        groups = np.repeat(np.arange(6), 3)
        y = np.tile(np.array([0.1, 0.2, 0.3]), 6) + 0.01 * groups
        X = np.column_stack([y, y**2, np.sin(y)])

        calls = {"n": 0}
        original = statistics._ridge_predict

        def counted(*args, **kwargs):
            calls["n"] += 1
            return original(*args, **kwargs)

        statistics._ridge_predict = counted
        try:
            outer = statistics.outer_lowo_predictions(X, y, groups)
            self.assertEqual(calls["n"], 6)
            for fold in outer.audit:
                self.assertEqual(fold["intersection"], [])
                self.assertTrue(set(fold["train_worlds"]).isdisjoint(fold["test_worlds"]))
            losses = statistics.original_world_losses(y, outer)
            statistics.fixed_fold_bootstrap([losses[w]["skill"] for w in sorted(losses)], reps=200)
            self.assertEqual(calls["n"], 6, "fixed-fold bootstrap must never retrain")
        finally:
            statistics._ridge_predict = original

    def test_all_scope_models_use_the_same_label_and_original_groups(self):
        groups = np.repeat(np.arange(6), 3)
        y = np.tile(np.array([0.1, 0.2, 0.3]), 6)
        base = np.column_stack([y, y**2])
        matrices = {
            "L": base,
            "N": base[:, ::-1],
            "P": np.column_stack([base, base]),
            "E": np.column_stack([base, np.zeros_like(base)]),
            "G": np.column_stack([base, base, base]),
            "B": np.ones((len(y), 2)),
        }
        result = statistics.evaluate_scope_models(matrices, y, groups)
        self.assertEqual(result["label"], "own cumulative dose for every scope and comparator")
        self.assertEqual(result["uncertainty_unit"], "fixed original-world fold losses")


class ScopePersistenceTests(unittest.TestCase):
    def test_scope_extraction_is_label_free_and_masks_target_memory_in_E(self):
        self.assertNotIn("dose", inspect.signature(scopes.extract_scope_bundle).parameters)
        state = DummyState()
        regions = [
            block(16, 2, 6, 2, 6),
            block(16, 2, 6, 10, 14),
            block(16, 10, 14, 6, 10),
        ]
        centroids = [(3.5, 3.5), (3.5, 11.5), (11.5, 7.5)]
        for i, region in enumerate(regions):
            state.Mf[0, region] = (i + 1) * state.rho[region] * 0.1
            state.Mf[1, region] = (i + 1) * state.rho[region] * 0.05
        bundle = scopes.extract_scope_bundle(state, regions, centroids)
        self.assertFalse(bundle["label_fields_present"])
        self.assertEqual(len(bundle["json_scopes"]["L"][0]), 11)
        self.assertEqual(len(bundle["json_scopes"]["P"][0]), 33)
        target_mask = bundle["arrays"]["target_mask_0"].astype(bool)
        E = bundle["arrays"]["E_target_0"]
        G = bundle["arrays"]["G_target_0"]
        self.assertTrue(np.all(E[6:, target_mask] == 0.0))
        self.assertGreater(float(np.abs(G[6:, target_mask]).sum()), 0.0)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scope.npz"
            meta = scopes.persist_scope_bundle(path, bundle)
            loaded = scopes.load_scope_arrays(path, meta["sha256"])
            self.assertTrue(np.array_equal(loaded["E_target_0"], E))

    def test_analysis_joins_one_own_dose_label_to_every_scope(self):
        state = DummyState()
        regions = [
            block(16, 2, 6, 2, 6),
            block(16, 2, 6, 10, 14),
            block(16, 10, 14, 6, 10),
        ]
        centroids = [(3.5, 3.5), (3.5, 11.5), (11.5, 7.5)]
        for i, region in enumerate(regions):
            state.Mf[0, region] = (i + 1) * state.rho[region] * 0.1
            state.Mf[1, region] = (i + 1) * state.rho[region] * 0.05

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            old_root = analyzer.ROOT
            analyzer.ROOT = tmp_root
            try:
                records = []
                for seed in (1, 2, 3):
                    bundle = scopes.extract_scope_bundle(state, regions, centroids)
                    sidecar = tmp_root / f"seed_{seed}.npz"
                    meta = scopes.persist_scope_bundle(sidecar, bundle)
                    meta["path"] = sidecar.name
                    records.append(
                        {
                            "seed": seed,
                            "feasibility": {"valid": True},
                            "labels": {"own_dose": [0.01 * seed, 0.02 * seed, 0.03 * seed]},
                            "scope_bundle": meta,
                        }
                    )
                matrices, y, groups, audit = analyzer.build_analysis_matrices({"records": records})
                self.assertEqual(set(matrices), {"L", "N", "P", "E", "G", "B"})
                self.assertEqual(y.tolist(), [0.01, 0.02, 0.03, 0.02, 0.04, 0.06, 0.03, 0.06, 0.09])
                self.assertEqual(groups.tolist(), [1, 1, 1, 2, 2, 2, 3, 3, 3])
                self.assertTrue(all(row["label_name_for_all_scopes"] == "own cumulative dose" for row in audit))
            finally:
                analyzer.ROOT = old_root


class AuthorizationAndFamilyTests(unittest.TestCase):
    def test_exact_primary_reserve_and_hard_cap(self):
        self.assertEqual(runner.PRIMARY_SEEDS, tuple(range(54001, 54051)))
        self.assertEqual(runner.RESERVE_SEEDS, tuple(range(54051, 54097)))
        self.assertEqual(len(set(runner.ALL_SEEDS)), 96)
        self.assertEqual(runner.MIN_VALID_WORLDS, 18)
        self.assertEqual(runner.TOTAL_HARD_CAP, 96)

    def test_reserve_activation_is_feasibility_only_and_outcome_blinded(self):
        records = [
            feasibility_record(seed, valid=(seed < 54011), endpoint_value=float(seed))
            for seed in runner.PRIMARY_SEEDS
        ]
        first = runner.reserve_activation(records)
        self.assertTrue(first["active"])
        self.assertEqual(first["valid_worlds"], 10)
        self.assertEqual(first["next_reserve_seed"], 54051)
        self.assertEqual(first["endpoint_fields_used"], [])

        changed = copy.deepcopy(records)
        for record in changed:
            record["labels"]["own_dose"] = [1e99, -1e99, np.nan]
            record["endpoints"]["arbitrary_outcome"] = {"anything": "changed"}
        self.assertEqual(first, runner.reserve_activation(changed))

        enough = [feasibility_record(seed, valid=(seed < 54019)) for seed in runner.PRIMARY_SEEDS]
        self.assertFalse(runner.reserve_activation(enough)["active"])

    def test_lambda_plus_only_ablation_preserves_lambda_minus_and_all_other_params(self):
        intact = runner.MCParams(lam_plus=0.25, lam_minus=0.15, **runner.C1C)
        self.assertEqual(runner.MEM_ABLATE_PLUS.lam_plus, 0.0)
        for field in intact.__dataclass_fields__:
            if field != "lam_plus":
                self.assertEqual(getattr(intact, field), getattr(runner.MEM_ABLATE_PLUS, field))


class EventEvidenceTests(unittest.TestCase):
    def _split_record(self):
        size = 16
        parent = block(size, 4, 12, 4, 12)
        left = block(size, 4, 12, 4, 7)
        right = block(size, 4, 12, 9, 12)
        rho = np.ones((size, size))
        record, state = events.start_event("SPLIT", 0, 10, [parent], [left, right], rho)
        return record, state, left, right, rho

    def test_fission_and_transient_fragmentation_are_distinct(self):
        record, state, left, right, rho = self._split_record()
        for step in range(11, 16):
            events.append_followup(record, state, step, [left, right], rho)
        self.assertEqual(events.finalize(record)["classification"], "FISSION")

        record, state, left, right, rho = self._split_record()
        merged = left | right
        for step in range(11, 16):
            events.append_followup(record, state, step, [merged], rho)
        self.assertEqual(events.finalize(record)["classification"], "TRANSIENT_FRAGMENTATION")

    def test_merge_loss_and_death_are_distinct(self):
        size = 16
        a = block(size, 3, 7, 3, 7)
        b = block(size, 3, 7, 9, 13)
        merged = block(size, 2, 8, 2, 14)
        rho = np.ones((size, size))
        rec, _ = events.start_event("MERGED", 0, 5, [a, b], [merged], rho)
        self.assertEqual(events.finalize(rec)["classification"], "MERGE")

        rec, state = events.start_event("LOST", 0, 5, [a], [], rho)
        for step in range(6, 11):
            events.append_followup(rec, state, step, [], rho)
        self.assertEqual(events.finalize(rec)["classification"], "LOSS")

        rec, state = events.start_event("LOST", 0, 5, [a], [], rho)
        dead_rho = np.zeros_like(rho)
        for step in range(6, 11):
            events.append_followup(rec, state, step, [], dead_rho)
        self.assertEqual(events.finalize(rec)["classification"], "DEATH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
