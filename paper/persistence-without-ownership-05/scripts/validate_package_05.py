#!/usr/bin/env python3
"""Static validation for the paper-05 package; never imports or runs the engine."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MANUSCRIPT = ROOT / "PERSISTENCE_WITHOUT_OWNERSHIP_05.tex"


def load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def prose_word_count(tex: str) -> int:
    """Approximate journal word count after removing LaTeX control material."""
    text = re.sub(r"(?m)(?<!\\)%.*$", " ", tex)
    text = re.sub(r"\\(?:cite\w*|ref|pageref|label|includegraphics|bibliography|bibliographystyle)(?:\[[^]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\begin\{(?:equation|align|table|tabular|longtable)\*?\}.*?\\end\{(?:equation|align|table|tabular|longtable)\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", text)
    text = re.sub(r"\$.*?\$", " ", text, flags=re.S)
    text = re.sub(r"[{}&_~^\\]", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def main() -> None:
    tex = MANUSCRIPT.read_text(encoding="utf-8")
    turnover = load_json("data/turnover_recomputed_05.json")
    confirm = load_json("data/confirm02_recomputed_05.json")
    v41 = load_json("data/v41_recomputed_05.json")
    refs = load_json("REFERENCE_VERIFICATION_05.json")
    sources = load_json("SOURCE_BINDINGS_05.json")
    registry = load_json("RAW_DATA_REGISTRY_05.json")

    words = prose_word_count(tex)
    assert 7000 <= words <= 9000, f"manuscript word count {words} outside 7000--9000"
    assert tex.count("\\includegraphics") == 8
    assert tex.count("Generating script:") == 8
    assert tex.count("Source artifact") >= 8
    assert tex.count("Sample unit:") == 8
    assert tex.count("$n$ worlds:") == 8
    assert tex.count("Status:") >= 8
    assert tex.count("Uncertainty:") >= 8

    assert turnover["n_raw_worlds"] == 50
    assert turnover["n_valid_worlds"] == 21
    assert turnover["outcome"] == "B"
    assert turnover["gates"] == {
        "DISTRIBUTED_ENV": False,
        "FEASIBILITY": True,
        "G_CAUSAL": True,
        "G_LOCAL_EXCLUSION": False,
        "G_OWN_PERM": True,
    }
    assert turnover["inputs"]["raw_manifest"]["reserve_seed_count"] == 0
    assert confirm["n_valid_worlds"] == 23
    assert all(confirm["gates"].values())
    assert abs(v41["checkpoints"]["deep"]["h1"]["world_grouped_r2"] - 0.69469387421633) < 1e-15
    assert v41["n_original_worlds"] == 3
    assert v41["recorded_switches"] == 0
    assert refs["failed_count"] == 0 and refs["verified_count"] == 30
    assert len(sources["sources"]) >= 17
    assert registry["no_new_simulation"] is True
    assert turnover["paper_recompute"]["seed_executed"] is False
    assert turnover["paper_recompute"]["engine_imported"] is False
    assert turnover["engine_imported"] is False
    assert confirm["seed_executed"] is False and confirm["engine_imported"] is False
    assert v41["seed_executed"] is False and v41["engine_imported"] is False

    assert git("branch", "--show-current") == "paper/persistence-without-ownership-05"
    assert git("merge-base", "--is-ancestor", "9cb996bb891f9a618e593f2f5c302f30210458de", "a8d6446fade6dbeb984e269fab27ddd5ebf75286") == ""
    paper_base = "a8d6446fade6dbeb984e269fab27ddd5ebf75286"
    assert git("merge-base", paper_base, "HEAD") == paper_base

    result = {
        "branch": git("branch", "--show-current"),
        "figures": 8,
        "manuscript_words": words,
        "new_experiment_executed": False,
        "references_failed": refs["failed_count"],
        "references_verified": refs["verified_count"],
        "seed_executed": False,
        "source_bindings": len(sources["sources"]),
        "status": "PASS",
        "turnover_outcome": turnover["outcome"],
        "turnover_valid_worlds": turnover["n_valid_worlds"],
    }
    (ROOT / "PACKAGE_VALIDATION_05.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
