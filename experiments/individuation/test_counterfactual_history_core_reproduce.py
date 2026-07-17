import hashlib
import json
from pathlib import Path

from experiments.individuation.counterfactual_history_core_reproduce import reproduce


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json"
REPRODUCTION = (
    ROOT / "docs" / "individuation" / "COUNTERFACTUAL_HISTORY_CORE_00_RAW_REPRODUCTION.json"
)
EXPECTED_RAW_SHA256 = "d4e6f2d9cedcc8b459973e10641b1b28d91b3b52315cbba36120640ef9386da6"


def test_raw_only_reproduction_matches_persisted_result_without_engine():
    raw_bytes = RAW.read_bytes()
    raw = json.loads(raw_bytes)
    reproduced = reproduce(raw)
    persisted = json.loads(REPRODUCTION.read_text(encoding="utf-8"))

    assert hashlib.sha256(raw_bytes).hexdigest() == EXPECTED_RAW_SHA256
    assert reproduced["pass"] is True
    assert reproduced["engine_initialized"] is False
    assert reproduced["prospective_execution_authorized"] is False
    assert reproduced["reproduced"]["conclusion"] == "NO_MEMORY_FIRST_STAGE"
    assert reproduced["reproduced"] == persisted["reproduced"]
    assert reproduced["comparisons"] == persisted["comparisons"]
