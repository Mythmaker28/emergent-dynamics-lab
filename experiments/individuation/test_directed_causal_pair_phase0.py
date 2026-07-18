"""Contract tests for the outcome-blind DIRECTED-CAUSAL-PAIR-00 audit."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("pair_audit", HERE / "directed_causal_pair_phase0_audit.py")
assert SPEC and SPEC.loader
pair_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pair_audit)


class DirectedCausalPairPhase0Tests(unittest.TestCase):
    def test_toroidal_distance_wraps(self) -> None:
        self.assertAlmostEqual(pair_audit.toroidal_distance([63.0, 4.0], [1.0, 4.0]), 2.0)

    def test_pair_selection_is_initial_geometry_only(self) -> None:
        candidates = pair_audit.pair_candidates(
            [[0.0, 0.0], [1.0, 0.0], [31.0, 0.0]],
            [[0.0, 0.0], [32.0, 0.0], [1.0, 0.0]],
        )
        even = pair_audit.select_pair(candidates, 50002)
        odd = pair_audit.select_pair(candidates, 50003)
        self.assertEqual(even["target_indices"], [0, 2])
        self.assertEqual((even["target_A"], even["target_B"]), (0, 2))
        self.assertEqual((odd["target_A"], odd["target_B"]), (2, 0))

    def test_committed_audit_is_dev_only_and_outcome_blind(self) -> None:
        result = pair_audit.audit(REPO)
        self.assertFalse(result["new_seed_or_prospective_family_opened"])
        self.assertFalse(result["pair_feeding_outcomes_computed"])
        self.assertEqual(result["summary"]["n_eligible_pair_worlds"], 4)
        self.assertTrue(result["summary"]["all_selected_pairs_pass_available_endpoint_separation"])
        self.assertFalse(result["summary"]["pair_context_history_bearing_recipient_noswap_qualified"])
        self.assertEqual(result["summary"]["recommendation"], "REVISE")

    def test_generated_json_matches_committed_result(self) -> None:
        expected_path = REPO / "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json"
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(pair_audit.audit(REPO), expected)


if __name__ == "__main__":
    unittest.main()
