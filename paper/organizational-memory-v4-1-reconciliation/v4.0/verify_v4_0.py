"""Verify the preserved V4.0 snapshot against its canonical release manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "canonical"
MANIFEST = ROOT / "release" / "RELEASE_MANIFEST_V4.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_bytes())
    failures: list[str] = []
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        if not path.is_file():
            failures.append(f"MISSING {entry['path']}")
            continue
        if path.stat().st_size != entry["bytes"]:
            failures.append(
                f"SIZE {entry['path']} {path.stat().st_size} != {entry['bytes']}"
            )
        actual = sha256(path)
        if actual != entry["sha256"]:
            failures.append(f"SHA256 {entry['path']} {actual} != {entry['sha256']}")

    if failures:
        print("\n".join(failures))
        print(f"V4.0 SNAPSHOT VERIFICATION: FAIL ({len(failures)} issue(s))")
        return 1

    print(
        "V4.0 SNAPSHOT VERIFICATION: PASS "
        f"({len(manifest['files'])}/{len(manifest['files'])} manifest files)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
