"""One-time exact-byte export from recovered Git; never execute a simulation.

Ordinary readers use the committed data/ and run reproduce.py; this exporter is
only needed to recreate the source capsule from the documented recovered refs.
"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
COMMIT = "06fd9524f5c7ffb329ee850a10bd9959f2f0bde5"
SNAP = REPO / "audit/edl-flagship-01/candidate_b"


def blob(path):
    return subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=REPO)


def main():
    data = HERE / "data"
    data.mkdir(exist_ok=True)
    rows = []
    # Preserve all frozen documentation, raw records and the original independent
    # raw-only implementation. Exclude old manuscript prose from the new input set.
    original = json.loads((SNAP / "SNAPSHOT_MANIFEST.json").read_text())
    chosen = [r for r in original if r["path"].startswith(("results/", "docs/"))]
    chosen += [r for r in original if r["path"].endswith("independent_crosscheck_03m.py")]
    for row in chosen:
        content = (SNAP / row["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == row["sha256"]
        dest = data / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        rows.append({"path": dest.relative_to(HERE).as_posix(), "source_path": row["path"],
                     "source_commit": COMMIT, "bytes": len(content), "sha256": row["sha256"]})
    raw = json.loads((data / "results/LCI-TURNOVER-PROSPECTIVE-03G/raw/seed_54001.json").read_text())
    protected = raw["bindings"]["code_sha256"]
    tree = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", COMMIT], cwd=REPO).decode().splitlines())
    todo = list(protected)
    # Include imports used by the frozen engine and initialization; source-only,
    # including dynamic local-file imports. No importing or execution here.
    done = set()
    while todo:
        path = todo.pop()
        if path in done or path not in tree:
            continue
        done.add(path)
        content = blob(path)
        sha = hashlib.sha256(content).hexdigest()
        raw_binding_match = None
        if path in protected:
            # The Windows runner bound working-file SHA as well as Git blob ID.
            # Some historical worktree files had CRLF while their Git blobs had LF.
            # Keep Git bytes and explicitly verify this deterministic EOL relation.
            bound_blob = raw["bindings"]["code_git_blobs"][path]
            exact_blob = subprocess.check_output(["git", "cat-file", "blob", bound_blob], cwd=REPO)
            assert content == exact_blob, path
            crlf_sha = hashlib.sha256(content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()
            assert protected[path] in (sha, crlf_sha), path
            raw_binding_match = "exact Git bytes" if sha == protected[path] else "Git LF bytes converted to Windows CRLF"
        dest = HERE / "source_model" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        rows.append({"path": dest.relative_to(HERE).as_posix(), "source_path": path,
                     "source_commit": COMMIT, "bytes": len(content), "sha256": sha,
                     "protected_in_raw_binding": path in protected,
                     "raw_working_file_sha256": protected.get(path),
                     "raw_binding_match": raw_binding_match})
        if not path.endswith(".py"):
            continue
        parts = path.split("/")[:-1]
        for node in ast.walk(ast.parse(content.decode("utf-8-sig"))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.replace(".", "/") for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = parts[:len(parts) - node.level + 1] if node.level else []
                stem = "/".join(prefix + (node.module.split(".") if node.module else []))
                names = [stem] + [stem + "/" + a.name for a in node.names]
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.endswith(".py"):
                possible = "/".join(parts + [node.value])
                if possible in tree:
                    todo.append(possible)
            for name in names:
                for candidate in [name + ".py", name + "/__init__.py"]:
                    if candidate in tree:
                        todo.append(candidate)
                for i in range(1, len(name.split("/"))):
                    todo.append("/".join(name.split("/")[:i]) + "/__init__.py")
    manifest = {"source_commit": COMMIT, "protected_files": len(protected),
                "files": sorted(rows, key=lambda r: r["path"]),
                "scope": "Exact raw JSON and provenance documents; source-only protected code and static/dynamic-local import closure. No engine execution."}
    (HERE / "INPUT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"files": len(rows), "protected": len(protected), "source_closure": len(done), "bytes": sum(r["bytes"] for r in rows)}))


if __name__ == "__main__":
    main()
