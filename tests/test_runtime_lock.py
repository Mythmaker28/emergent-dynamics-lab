import json
from pathlib import Path

import pytest

from edlab.runtime_lock import (
    ActiveRunError,
    UnreadableLockError,
    acquire_lock,
    main,
    read_lock,
    release_lock,
)


def test_lock_is_atomic_conservative_and_owner_checked(tmp_path: Path) -> None:
    path = tmp_path / "scheduled_task.lock"
    acquired = acquire_lock(
        run_id="RUN-A",
        task_identity="test",
        starting_head="abc",
        active_experiment_id="EXP",
        path=path,
    )
    assert acquired["run_id"] == "RUN-A"
    assert read_lock(path)["active_experiment_id"] == "EXP"
    with pytest.raises(ActiveRunError, match="SKIPPED_DUE_TO_ACTIVE_RUN"):
        acquire_lock(
            run_id="RUN-B",
            task_identity="test",
            starting_head="def",
            active_experiment_id="EXP",
            path=path,
        )
    with pytest.raises(ActiveRunError):
        release_lock(run_id="RUN-B", path=path)
    release_lock(run_id="RUN-A", path=path)
    assert not path.exists()


def _cli(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_cli_round_trip_prints_json_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = str(tmp_path / "scheduled_task.lock")
    acquire = ["acquire", "--run-id", "RUN-A", "--task-identity", "test"]
    code, out, _ = _cli([*acquire, "--starting-head", "abc", "--path", path], capsys)
    assert code == 0
    assert json.loads(out)["run_id"] == "RUN-A"
    assert json.loads(out)["active_experiment_id"] == "NONE"
    code, out, _ = _cli(["status", "--path", path], capsys)
    assert code == 0
    assert json.loads(out)["run_id"] == "RUN-A"
    code, out, _ = _cli(["release", "--run-id", "RUN-A", "--path", path], capsys)
    assert code == 0
    assert json.loads(out) == {"released": True, "run_id": "RUN-A"}
    code, out, _ = _cli(["status", "--path", path], capsys)
    assert code == 0
    assert json.loads(out) is None


def test_cli_refusals_exit_two_and_leave_the_lock_in_place(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "scheduled_task.lock"
    acquire_lock(
        run_id="RUN-A",
        task_identity="test",
        starting_head="abc",
        active_experiment_id="EXP",
        path=path,
    )
    before = path.read_bytes()
    acquire = ["acquire", "--run-id", "RUN-B", "--task-identity", "test"]
    code, out, err = _cli(
        [*acquire, "--starting-head", "def", "--path", str(path)], capsys
    )
    assert (code, out) == (2, "")
    assert err.startswith("SKIPPED_DUE_TO_ACTIVE_RUN")
    code, out, err = _cli(["release", "--run-id", "RUN-B", "--path", str(path)], capsys)
    assert (code, out) == (2, "")
    assert "refusing to release lock owned by 'RUN-A'" in err
    assert path.read_bytes() == before
    release_lock(run_id="RUN-A", path=path)
    code, out, err = _cli(["release", "--run-id", "RUN-A", "--path", str(path)], capsys)
    assert (code, out) == (2, "")
    assert err.startswith("no active lock")


# An empty file is what a concurrent reader sees between the O_EXCL create and
# the JSON write, and what a holder killed in that window leaves behind.
UNREADABLE_LOCKS = {
    "empty": b"",
    "truncated": b'{"run_id": "RUN-A"',
    "not-utf8": b"\xff\xfe",
    "not-an-object": b"[]",
    "null": b"null",
}


@pytest.mark.parametrize("content", UNREADABLE_LOCKS.values(), ids=UNREADABLE_LOCKS)
def test_unreadable_lock_is_held_and_never_released(
    tmp_path: Path, content: bytes
) -> None:
    path = tmp_path / "scheduled_task.lock"
    path.write_bytes(content)
    with pytest.raises(UnreadableLockError):
        read_lock(path)
    with pytest.raises(ActiveRunError, match="^SKIPPED_DUE_TO_ACTIVE_RUN"):
        acquire_lock(
            run_id="RUN-B",
            task_identity="test",
            starting_head="def",
            active_experiment_id="EXP",
            path=path,
        )
    with pytest.raises(ActiveRunError):
        release_lock(run_id="RUN-A", path=path)
    assert path.read_bytes() == content


@pytest.mark.parametrize("content", UNREADABLE_LOCKS.values(), ids=UNREADABLE_LOCKS)
def test_cli_reports_unreadable_lock_with_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: bytes
) -> None:
    path = tmp_path / "scheduled_task.lock"
    path.write_bytes(content)
    acquire = ["acquire", "--run-id", "RUN-B", "--task-identity", "test"]
    code, out, err = _cli(
        [*acquire, "--starting-head", "def", "--path", str(path)], capsys
    )
    assert (code, out) == (2, "")
    assert err.startswith("SKIPPED_DUE_TO_ACTIVE_RUN")
    for command in (["status"], ["release", "--run-id", "RUN-A"]):
        code, out, err = _cli([*command, "--path", str(path)], capsys)
        assert (code, out) == (2, "")
        assert "unreadable lock" in err
    assert path.read_bytes() == content
