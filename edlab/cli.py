"""Command-line entry points for reproducible validation and experiments."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from .experiments.analyze_streaming import analyze_streaming_screen
from .experiments.baseline import BaselineConfig, run_baseline
from .experiments.streaming import run_streaming_screen
from .validation.forces import validate_force_paths
from .validation.nulls import (
    id_permutation_null,
    sparse_lookalike_alias_null,
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


def _git_scope_clean(output_dir: Path) -> bool:
    repository = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    ).resolve()
    output = output_dir.resolve()
    try:
        allowed_prefix = output.relative_to(repository).as_posix()
    except ValueError:
        allowed_prefix = ""
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    for entry in status.split(b"\0"):
        if not entry:
            continue
        path = entry[3:].decode("utf-8", errors="surrogateescape").replace("\\", "/")
        if allowed_prefix and (
            path == allowed_prefix or path.startswith(f"{allowed_prefix}/")
        ):
            continue
        return False
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edlab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-forces")
    subparsers.add_parser("nulls")
    baseline = subparsers.add_parser("baseline")
    baseline.add_argument("--output", type=Path, required=True)
    baseline.add_argument("--experiment-id", required=True)
    baseline.add_argument("--laws", type=int, default=12)
    baseline.add_argument("--law-indices", type=int, nargs="+")
    baseline.add_argument("--kind", choices=("baseline", "holdout"), default="baseline")
    baseline.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    baseline.add_argument("--particles", type=int, default=64)
    baseline.add_argument("--steps", type=int, default=600)
    baseline.add_argument("--cadences", type=int, nargs="+", default=[10, 30, 60])
    streaming = subparsers.add_parser("stream-screen")
    streaming.add_argument("--output", type=Path, required=True)
    streaming.add_argument("--experiment-id", required=True)
    streaming.add_argument("--laws", type=int, required=True)
    streaming.add_argument("--seeds", type=int, nargs="+", required=True)
    streaming.add_argument("--particles", type=int, default=64)
    streaming.add_argument("--steps", type=int, default=600)
    streaming.add_argument("--cadences", type=int, nargs="+", default=[10, 30, 60])
    streaming.add_argument("--reservoir-size", type=int, default=100_000)
    analysis = subparsers.add_parser("analyze-stream-screen")
    analysis.add_argument("--output", type=Path, required=True)
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
            asdict(sparse_lookalike_alias_null()),
        ]
    elif args.command == "baseline":
        config = BaselineConfig(
            n_laws=args.laws,
            law_indices=None if args.law_indices is None else tuple(args.law_indices),
            experiment_kind=args.kind,
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
    elif args.command == "stream-screen":
        git_scope_clean = _git_scope_clean(args.output)
        if not git_scope_clean:
            raise RuntimeError(
                "stream-screen requires a clean Git scope outside its output directory"
            )
        config = BaselineConfig(
            n_laws=args.laws,
            experiment_kind="baseline",
            seeds=tuple(args.seeds),
            n_particles=args.particles,
            steps=args.steps,
            snapshot_cadences=tuple(args.cadences),
        )
        result = run_streaming_screen(
            output_dir=args.output,
            experiment_id=args.experiment_id,
            git_commit=_git_head(),
            config=config,
            reservoir_size=args.reservoir_size,
            git_scope_clean=git_scope_clean,
        )
    else:
        git_scope_clean = _git_scope_clean(args.output)
        if not git_scope_clean:
            raise RuntimeError(
                "analyze-stream-screen requires a clean Git scope outside its output directory"
            )
        result = analyze_streaming_screen(
            args.output,
            analysis_git_commit=_git_head(),
            analysis_git_scope_clean=git_scope_clean,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
