#!/usr/bin/env python3
"""Compile the two paper PDFs with an externally installed Tectonic binary."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = REPO / "output" / "pdf"
SOURCES = [
    ROOT / "PERSISTENCE_WITHOUT_OWNERSHIP_05.tex",
    ROOT / "PERSISTENCE_WITHOUT_OWNERSHIP_05_SUPPLEMENT.tex",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tectonic", required=True, type=Path)
    args = parser.parse_args()
    assert args.tectonic.is_file(), args.tectonic
    OUT.mkdir(parents=True, exist_ok=True)
    built = []
    for source in SOURCES:
        subprocess.run(
            [str(args.tectonic), str(source.name), "--outdir", str(OUT), "--keep-logs"],
            cwd=ROOT,
            check=True,
        )
        pdf = OUT / source.with_suffix(".pdf").name
        assert pdf.is_file() and pdf.stat().st_size > 10_000
        built.append({"path": pdf.relative_to(REPO).as_posix(), "bytes": pdf.stat().st_size, "sha256": sha256(pdf)})
    print(json.dumps({"built": built}, indent=2))


if __name__ == "__main__":
    main()
