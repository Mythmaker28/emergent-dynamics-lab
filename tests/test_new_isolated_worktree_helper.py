from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPOSITORY_ROOT / "scripts" / "New-IsolatedWorktree.ps1"


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )


def git(repo: Path, *args: str, env: dict[str, str] | None = None, input_text: str | None = None) -> str:
    return run(["git", *args], cwd=repo, env=env, input_text=input_text).stdout.strip()


def powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if executable is None:
        pytest.skip("PowerShell is required for the Windows worktree helper")
    return executable


def make_fixture(tmp_path: Path, invalid_path: str) -> tuple[Path, str]:
    repo = tmp_path / "fixture"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Repository Hygiene Test")
    git(repo, "config", "user.email", "repository-hygiene@example.invalid")
    (repo / "ok.txt").write_text("materialized\n", encoding="utf-8")
    git(repo, "add", "ok.txt")
    git(repo, "commit", "-m", "normal base")
    parent = git(repo, "rev-parse", "HEAD")

    index_path = tmp_path / "fixture-index"
    fixture_env = os.environ.copy()
    fixture_env["GIT_INDEX_FILE"] = str(index_path)
    git(repo, "read-tree", parent, env=fixture_env)
    blob = git(repo, "hash-object", "-w", "--stdin", input_text="cache only\n")
    git(
        repo,
        "-c",
        "core.protectNTFS=false",
        "update-index",
        "--add",
        "--cacheinfo",
        f"100644,{blob},{invalid_path}",
        env=fixture_env,
    )
    tree = git(repo, "write-tree", env=fixture_env)
    commit = git(repo, "commit-tree", tree, "-p", parent, input_text="historical invalid path fixture\n")
    git(repo, "update-ref", "refs/heads/historical-invalid", commit)
    return repo, commit


def invoke_helper(repo: Path, target: Path, commit: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(HELPER),
            "-Repository",
            str(repo),
            "-Path",
            str(target),
            "-Commitish",
            commit,
        ],
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_helper_materializes_valid_files_and_preserves_full_index_tree(tmp_path: Path) -> None:
    invalid_path = "results/_tomo_cache/BASE|fixture|ph0.pkl"
    repo, commit = make_fixture(tmp_path, invalid_path)
    target = tmp_path / "historical-worktree"

    completed = invoke_helper(repo, target, commit)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "CREATED_WINDOWS_SAFE_WORKTREE" in completed.stdout
    assert (target / "ok.txt").read_text(encoding="utf-8") == "materialized\n"
    assert not (target / "results" / "_tomo_cache").exists()
    assert git(target, "status", "--porcelain=v1", "--untracked-files=all") == ""
    assert git(target, "write-tree") == git(repo, "rev-parse", f"{commit}^{{tree}}")
    skipped = [line[2:] for line in git(target, "-c", "core.quotepath=false", "ls-files", "-v").splitlines() if line.startswith("S ")]
    assert skipped == [invalid_path]


def test_helper_refuses_to_overwrite_existing_target(tmp_path: Path) -> None:
    repo, commit = make_fixture(tmp_path, "results/_tomo_cache/BASE|fixture|ph0.pkl")
    target = tmp_path / "occupied"
    target.mkdir()
    marker = target / "keep.txt"
    marker.write_text("do not overwrite\n", encoding="utf-8")

    completed = invoke_helper(repo, target, commit)

    assert completed.returncode != 0
    assert "Refusing to overwrite existing path" in completed.stderr
    assert marker.read_text(encoding="utf-8") == "do not overwrite\n"
    registered = git(repo, "worktree", "list", "--porcelain")
    assert str(target) not in registered


def test_helper_refuses_undocumented_invalid_path(tmp_path: Path) -> None:
    repo, commit = make_fixture(tmp_path, "docs/bad|name.txt")
    target = tmp_path / "rejected-worktree"

    completed = invoke_helper(repo, target, commit)

    assert completed.returncode != 0
    assert "undocumented Windows-invalid paths outside results/_tomo_cache" in completed.stderr
    assert not target.exists()


def test_helper_escapes_sparse_pattern_metacharacters(tmp_path: Path) -> None:
    invalid_path = "results/_tomo_cache/odd*fixture?.pkl"
    repo, commit = make_fixture(tmp_path, invalid_path)
    target = tmp_path / "metacharacter-worktree"

    completed = invoke_helper(repo, target, commit)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    skipped = [line[2:] for line in git(target, "-c", "core.quotepath=false", "ls-files", "-v").splitlines() if line.startswith("S ")]
    assert skipped == [invalid_path]
    assert git(target, "write-tree") == git(repo, "rev-parse", f"{commit}^{{tree}}")
