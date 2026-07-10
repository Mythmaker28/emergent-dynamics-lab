from pathlib import Path

import pytest

from edlab.runtime_lock import ActiveRunError, acquire_lock, read_lock, release_lock


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

