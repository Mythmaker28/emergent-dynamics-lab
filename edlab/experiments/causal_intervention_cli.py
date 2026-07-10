"""Thin reproducible entry point for ALIAS-INTERVENTION-COREV0 (frozen CausalConfig)."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from .causal_intervention import CausalConfig, run_causal_experiment


def _git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="edlab-causal")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--experiment-id", required=True)
    p.add_argument("--protocol-sha", default="UNFROZEN")
    args = p.parse_args(argv)
    summary = run_causal_experiment(
        output_dir=args.output, experiment_id=args.experiment_id,
        git_commit=_git_head(), config=CausalConfig(), protocol_sha=args.protocol_sha,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
