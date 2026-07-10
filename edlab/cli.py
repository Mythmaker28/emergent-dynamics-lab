"""Command-line entry points for reproducible validation and experiments."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from .experiments.baseline import BaselineConfig, run_baseline
from .validation.forces import validate_force_paths
from .validation.nulls import (
    id_permutation_null,
    static_motif_material_flux_null,
    tracker_cadence_sensitivity_null,
)


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edlab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-forces")
    subparsers.add_parser("nulls")
    baseline = subparsers.add_parser("baseline")
    baseline.add_argument("--output", type=Path, required=True)
    baseline.add_argument("--experiment-id", required=True)
    baseline.add_argument("--laws", type=int, default=12)
    baseline.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    baseline.add_argument("--particles", type=int, default=64)
    baseline.add_argument("--steps", type=int, default=600)
    baseline.add_argument("--cadences", type=int, nargs="+", default=[10, 30, 60])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate-forces":
        result = asdict(validate_force_paths())
    elif args.command == "nulls":
        result = [
            asdict(id_permutation_null()),
            asdict(static_motif_material_flux_null()),
            asdict(tracker_cadence_sensitivity_null()),
        ]
    else:
        config = BaselineConfig(
            n_laws=args.laws,
            seeds=tuple(args.seeds),
            n_particles=args.particles,
            steps=args.steps,
            snapshot_cadences=tuple(args.cadences),
        )
        result = run_baseline(
            output_dir=args.output,
            experiment_id=args.experiment_id,
            git_commit=_git_head(),
            config=config,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
