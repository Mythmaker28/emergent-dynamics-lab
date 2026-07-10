"""Auditable, conservative non-overlap lock for scheduled research runs."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_LOCK = Path(".runtime/scheduled_task.lock")


class ActiveRunError(RuntimeError):
    pass


def read_lock(path: Path = DEFAULT_LOCK) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def acquire_lock(
    *,
    run_id: str,
    task_identity: str,
    starting_head: str,
    active_experiment_id: str,
    path: Path = DEFAULT_LOCK,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "task_identity": task_identity,
        "start_timestamp": datetime.now(timezone.utc).isoformat(),
        "starting_head": starting_head,
        "active_experiment_id": active_experiment_id,
        "hostname": socket.gethostname(),
        "creator_pid": os.getpid(),
        "policy": "conservative: never clear by age alone; verify owner before release",
    }
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as exc:
        existing = read_lock(path)
        raise ActiveRunError(
            f"SKIPPED_DUE_TO_ACTIVE_RUN: existing lock={existing}"
        ) from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return payload


def release_lock(*, run_id: str, path: Path = DEFAULT_LOCK) -> None:
    existing = read_lock(path)
    if existing is None:
        raise FileNotFoundError(f"no active lock at {path}")
    if existing.get("run_id") != run_id:
        raise ActiveRunError(
            f"refusing to release lock owned by {existing.get('run_id')!r}"
        )
    path.unlink()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("--run-id", required=True)
    acquire.add_argument("--task-identity", required=True)
    acquire.add_argument("--starting-head", required=True)
    acquire.add_argument("--experiment", default="NONE")
    acquire.add_argument("--path", type=Path, default=DEFAULT_LOCK)
    status = subparsers.add_parser("status")
    status.add_argument("--path", type=Path, default=DEFAULT_LOCK)
    release = subparsers.add_parser("release")
    release.add_argument("--run-id", required=True)
    release.add_argument("--path", type=Path, default=DEFAULT_LOCK)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "acquire":
            result = acquire_lock(
                run_id=args.run_id,
                task_identity=args.task_identity,
                starting_head=args.starting_head,
                active_experiment_id=args.experiment,
                path=args.path,
            )
        elif args.command == "status":
            result = read_lock(args.path)
        else:
            release_lock(run_id=args.run_id, path=args.path)
            result = {"released": True, "run_id": args.run_id}
    except (ActiveRunError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
