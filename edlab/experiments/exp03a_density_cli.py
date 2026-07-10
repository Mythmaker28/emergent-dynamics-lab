"""Reproducible entry point for the EXP03-A density-preference screen (frozen EXP03AConfig)."""

from __future__ import annotations

import argparse, csv, hashlib, json, platform, subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from .exp03a_density import EXP03AConfig, screen_records, assemble_summary


def _git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def write_screen(output_dir: Path, experiment_id: str, git_commit: str, protocol_sha: str,
                 cfg: EXP03AConfig, records: list[dict]) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cols = [k for k in records[0] if k != "pm_hist"]
    with (output_dir / "screen_runs.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(records)
    summary = assemble_summary(cfg, records)
    summary.update({"experiment_id": experiment_id, "git_commit": git_commit, "protocol_sha": protocol_sha})
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    paths = sorted(p for p in output_dir.iterdir() if p.is_file() and p.name != "manifest.json")
    def sha(p):
        d = hashlib.sha256()
        with open(p, "rb") as fh:
            for c in iter(lambda: fh.read(1 << 20), b""): d.update(c)
        return d.hexdigest()
    (output_dir / "manifest.json").write_text(json.dumps({
        "experiment_id": experiment_id, "git_commit": git_commit, "protocol_sha": protocol_sha,
        "code_version": "0.1.0", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": cfg.as_dict(), "dependencies": {"python": platform.python_version(), "numpy": version("numpy")},
        "output_sha256": {p.name: sha(p) for p in paths},
    }, indent=2, sort_keys=True))
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="edlab-exp03a")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--experiment-id", required=True)
    p.add_argument("--protocol-sha", default="UNFROZEN")
    args = p.parse_args(argv)
    cfg = EXP03AConfig()
    records = screen_records(cfg, range(cfg.n_laws))
    summary = write_screen(args.output, args.experiment_id, _git_head(), args.protocol_sha, cfg, records)
    print(json.dumps({"decision": summary["decision"],
                      "ON_permitted": summary["by_condition"]["ON"]["n_screening_permitted_laws"],
                      "OFF_permitted": summary["by_condition"]["OFF"]["n_screening_permitted_laws"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
