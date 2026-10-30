import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from edlab.cli import _git_scope_clean

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")


def _git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True)


@pytest.fixture
def repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # A GIT_DIR inherited from a hook would point git at another repository,
    # and user or system configuration could change rename detection.
    for name in [key for key in os.environ if key.startswith("GIT_")]:
        monkeypatch.delenv(name)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)
    _git("init", "-q")
    _git("config", "user.name", "t")
    _git("config", "user.email", "t@t")
    _git("config", "commit.gpgsign", "false")
    _git("config", "status.renames", "true")
    # "tmpout/x" without its first three characters is "out/x": the
    # rename-into-output case below needs a source path of that shape.
    for name, text in (("out/a", "alpha\nbeta\n"), ("tmpout/x", "gamma\ndelta\n")):
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_text(text, encoding="utf-8")
    _git("add", "-A")
    _git("commit", "-q", "-m", "init")
    return tmp_path


def _rename_inside_output() -> None:
    _git("mv", "out/a", "out/b")


def _worktree_rename_inside_output() -> None:
    Path("out/a").rename("out/b")
    _git("add", "--intent-to-add", "out/b")


def _copy_inside_output() -> None:
    _git("config", "status.renames", "copies")
    shutil.copyfile("out/a", "out/b")
    with open("out/a", "a", encoding="utf-8") as handle:
        handle.write("epsilon\n")
    _git("add", "out/a", "out/b")


def _rename_into_output_from_outside() -> None:
    _git("mv", "tmpout/x", "out/x")


def _rename_out_of_output() -> None:
    _git("mv", "out/a", "tmpout/a")


def _untracked_inside_output() -> None:
    Path("out/new").write_text("new\n", encoding="utf-8")


def _modified_outside_output() -> None:
    Path("tmpout/x").write_text("changed\n", encoding="utf-8")


# Expected verdict: True when every changed path, including the source path of
# a rename or copy, lies inside the output directory.
CASES: dict[str, tuple[Callable[[], None], bool]] = {
    "rename-inside-output": (_rename_inside_output, True),
    "worktree-rename-inside-output": (_worktree_rename_inside_output, True),
    "copy-inside-output": (_copy_inside_output, True),
    "rename-into-output-from-outside": (_rename_into_output_from_outside, False),
    "rename-out-of-output": (_rename_out_of_output, False),
    "untracked-inside-output": (_untracked_inside_output, True),
    "modified-outside-output": (_modified_outside_output, False),
}


@pytest.mark.parametrize(("change", "expected"), CASES.values(), ids=CASES)
def test_git_scope_clean_checks_both_paths_of_a_rename_or_copy(
    repository: Path, change: Callable[[], None], expected: bool
) -> None:
    assert _git_scope_clean(repository / "out")
    change()
    assert _git_scope_clean(repository / "out") is expected
