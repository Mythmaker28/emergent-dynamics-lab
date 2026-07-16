"""Atomic hash-chained finite-state execution ledger for turnover PRESEAL 03G."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path

from turnover_raw_schema_03g import (
    atomic_write_json,
    canonical_bytes,
    validate_feasibility_projection,
)

LEDGER_SCHEMA = "LCI-TURNOVER-LEDGER-03G-v1"
LEDGER_NAME = "execution_ledger_03g.jsonl"
ANCHOR_NAME = "execution_ledger_03g.anchor.json"
LOCK_NAME = "execution_ledger_03g.lock"
GENESIS = "0" * 64

STATES = (
    "CREATED",
    "AUTHORIZED",
    "PRIMARY_RUNNING",
    "PRIMARY_CLOSED",
    "RESERVE_DECIDED",
    "RESERVE_RUNNING",
    "FAMILY_CLOSED",
    "ANALYZED",
    "CERTIFIED",
)
TRANSITIONS = {
    ("CREATED", "AUTHORIZE"): "AUTHORIZED",
    ("AUTHORIZED", "START_PRIMARY"): "PRIMARY_RUNNING",
    ("PRIMARY_RUNNING", "CLOSE_PRIMARY"): "PRIMARY_CLOSED",
    ("PRIMARY_CLOSED", "DECIDE_RESERVE"): "RESERVE_DECIDED",
    ("RESERVE_DECIDED", "START_RESERVE"): "RESERVE_RUNNING",
    ("RESERVE_DECIDED", "CLOSE_FAMILY"): "FAMILY_CLOSED",
    ("RESERVE_RUNNING", "CLOSE_FAMILY"): "FAMILY_CLOSED",
    ("FAMILY_CLOSED", "RECORD_ANALYSIS"): "ANALYZED",
    ("ANALYZED", "CERTIFY"): "CERTIFIED",
}


class LedgerError(RuntimeError):
    pass


def _entry_hash(prev_hash: str, payload: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + b"\n" + canonical_bytes(payload)).hexdigest()


def _read_entries(run_dir: Path) -> list[dict]:
    path = run_dir / LEDGER_NAME
    if not path.exists():
        return []
    entries = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise LedgerError(f"invalid ledger JSON at line {line_no}") from exc
    return entries


@contextlib.contextmanager
def _exclusive_lock(run_dir: Path):
    """Cross-platform advisory lock released automatically if the process dies."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / LOCK_NAME
    with open(path, "a+b") as fh:
        if fh.tell() == 0:
            fh.write(b"\0")
            fh.flush()
        fh.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fh.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _anchor(entries: list[dict]) -> dict:
    last = entries[-1]
    return {
        "schema": LEDGER_SCHEMA,
        "seq": int(last["seq"]),
        "tip_hash": last["entry_hash"],
        "state": last["new_state"],
        "terminal": last["new_state"] == "CERTIFIED",
    }


def _write_anchor(run_dir: Path, entries: list[dict]) -> None:
    atomic_write_json(run_dir / ANCHOR_NAME, _anchor(entries), overwrite=True)


def verify(run_dir, *, require_state: str | None = None) -> dict:
    run_dir = Path(run_dir)
    entries = _read_entries(run_dir)
    if not entries:
        raise LedgerError("ledger is absent or empty")
    prev = GENESIS
    state = None
    for index, entry in enumerate(entries):
        if entry.get("schema") != LEDGER_SCHEMA or entry.get("seq") != index:
            raise LedgerError(f"ledger schema/sequence break at {index}")
        if entry.get("prev_hash") != prev:
            raise LedgerError(f"ledger chain break at {index}")
        body = {key: value for key, value in entry.items() if key != "entry_hash"}
        if _entry_hash(prev, body) != entry.get("entry_hash"):
            raise LedgerError(f"ledger tamper at {index}")
        if index == 0:
            if entry.get("event") != "CREATE" or entry.get("old_state") is not None:
                raise LedgerError("ledger genesis must be CREATE")
            if entry.get("new_state") != "CREATED":
                raise LedgerError("ledger genesis must enter CREATED")
        else:
            if entry.get("old_state") != state:
                raise LedgerError(f"ledger state discontinuity at {index}")
            event = entry.get("event")
            new_state = entry.get("new_state")
            if event in {"SEED_STARTED", "SEED_RESUMED", "SEED_COMPLETED"}:
                if new_state != state or state not in {"PRIMARY_RUNNING", "RESERVE_RUNNING"}:
                    raise LedgerError(f"seed event invalid in state {state}")
            elif TRANSITIONS.get((state, event)) != new_state:
                raise LedgerError(f"invalid transition {state} --{event}--> {new_state}")
        state = entry["new_state"]
        prev = entry["entry_hash"]
    anchor_path = run_dir / ANCHOR_NAME
    if not anchor_path.exists():
        raise LedgerError("ledger anchor is absent")
    anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
    expected = _anchor(entries)
    if anchor != expected:
        raise LedgerError("ledger truncation or stale/tampered anchor detected")
    if require_state is not None and state != require_state:
        raise LedgerError(f"ledger state is {state}, required {require_state}")
    return {
        "verified": True,
        "entries": len(entries),
        "tip_hash": prev,
        "state": state,
        "terminal": state == "CERTIFIED",
    }


def _append_locked(run_dir: Path, event: str, new_state: str, body: dict) -> dict:
    entries = _read_entries(run_dir)
    if not entries:
        raise LedgerError("cannot append before atomic ledger creation")
    old_state = entries[-1]["new_state"]
    prev = entries[-1]["entry_hash"]
    payload = {
        "schema": LEDGER_SCHEMA,
        "seq": len(entries),
        "prev_hash": prev,
        "event": event,
        "old_state": old_state,
        "new_state": new_state,
        **body,
    }
    payload["entry_hash"] = _entry_hash(
        prev, {key: value for key, value in payload.items() if key != "entry_hash"}
    )
    path = run_dir / LEDGER_NAME
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    entries.append(payload)
    _write_anchor(run_dir, entries)
    return payload


def _binding_from_genesis(entry: dict) -> dict:
    return entry["binding"]


def initialize(run_dir, binding: dict, *, resume: bool) -> dict:
    """Create one canonical ledger atomically, or explicitly resume the same binding."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / LEDGER_NAME
    with _exclusive_lock(run_dir):
        if path.exists():
            if not resume:
                raise LedgerError("canonical execution already exists; use explicit resume")
            status = verify(run_dir)
            first = _read_entries(run_dir)[0]
            if _binding_from_genesis(first) != binding:
                raise LedgerError("resume binding mismatch")
            return {"mode": "resume", **status}
        if resume:
            raise LedgerError("cannot resume: canonical ledger does not exist")
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise LedgerError("second fresh start refused") from exc
        payload = {
            "schema": LEDGER_SCHEMA,
            "seq": 0,
            "prev_hash": GENESIS,
            "event": "CREATE",
            "old_state": None,
            "new_state": "CREATED",
            "binding": binding,
        }
        payload["entry_hash"] = _entry_hash(
            GENESIS, {key: value for key, value in payload.items() if key != "entry_hash"}
        )
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        _write_anchor(run_dir, [payload])
        return {"mode": "fresh", "state": "CREATED", "tip_hash": payload["entry_hash"]}


def transition(run_dir, event: str, body: dict | None = None) -> dict:
    run_dir = Path(run_dir)
    with _exclusive_lock(run_dir):
        status = verify(run_dir)
        new_state = TRANSITIONS.get((status["state"], event))
        if new_state is None:
            raise LedgerError(f"invalid transition from {status['state']} using {event}")
        return _append_locked(run_dir, event, new_state, body or {})


def entries(run_dir) -> list[dict]:
    verify(run_dir)
    return _read_entries(Path(run_dir))


def completed_seed_events(run_dir) -> list[dict]:
    return [entry for entry in entries(run_dir) if entry["event"] == "SEED_COMPLETED"]


def completed_seeds(run_dir) -> set[int]:
    return {int(entry["seed"]) for entry in completed_seed_events(run_dir)}


def incomplete_seed(run_dir) -> int | None:
    active = None
    done = completed_seeds(run_dir)
    for entry in entries(run_dir):
        if entry["event"] in {"SEED_STARTED", "SEED_RESUMED"}:
            active = int(entry["seed"])
        elif entry["event"] == "SEED_COMPLETED" and int(entry["seed"]) == active:
            active = None
    if active in done:
        return None
    return active


def _phase_for_state(state: str) -> str:
    if state == "PRIMARY_RUNNING":
        return "primary"
    if state == "RESERVE_RUNNING":
        return "reserve"
    raise LedgerError(f"seeds cannot run in state {state}")


def record_seed_started(run_dir, seed: int, expected_seed: int) -> dict:
    run_dir = Path(run_dir)
    with _exclusive_lock(run_dir):
        status = verify(run_dir)
        phase = _phase_for_state(status["state"])
        if int(seed) != int(expected_seed):
            raise LedgerError(f"wrong {phase} seed order: {seed} != {expected_seed}")
        if seed in completed_seeds(run_dir):
            raise LedgerError(f"seed {seed} already completed")
        active = incomplete_seed(run_dir)
        if active is not None and active != seed:
            raise LedgerError(f"seed {active} is incomplete; cannot start {seed}")
        event = "SEED_RESUMED" if active == seed else "SEED_STARTED"
        return _append_locked(run_dir, event, status["state"], {"phase": phase, "seed": int(seed)})


def record_seed_completed(
    run_dir,
    seed: int,
    raw_entry: dict,
    feasibility_projection: dict,
) -> dict:
    validate_feasibility_projection(feasibility_projection)
    if int(feasibility_projection["seed"]) != int(seed):
        raise LedgerError("feasibility projection seed mismatch")
    run_dir = Path(run_dir)
    with _exclusive_lock(run_dir):
        status = verify(run_dir)
        phase = _phase_for_state(status["state"])
        if seed in completed_seeds(run_dir):
            raise LedgerError(f"seed {seed} already completed")
        if incomplete_seed(run_dir) != int(seed):
            raise LedgerError(f"seed {seed} has no matching started/resumed event")
        return _append_locked(
            run_dir,
            "SEED_COMPLETED",
            status["state"],
            {
                "phase": phase,
                "seed": int(seed),
                "raw": raw_entry,
                "feasibility_projection": feasibility_projection,
            },
        )


def assert_primary_complete(run_dir, primary: list[int]) -> None:
    completed = completed_seeds(run_dir)
    missing = [seed for seed in primary if seed not in completed]
    if missing:
        raise LedgerError(f"cannot close primary; missing seeds: {missing}")
    reserve_done = [entry["seed"] for entry in completed_seed_events(run_dir) if entry["phase"] == "reserve"]
    if reserve_done:
        raise LedgerError("reserve seeds ran before primary closure")
    if incomplete_seed(run_dir) is not None:
        raise LedgerError("cannot close primary with an incomplete seed")


def close_primary(run_dir, primary: list[int]) -> dict:
    assert_primary_complete(run_dir, primary)
    return transition(run_dir, "CLOSE_PRIMARY", {"primary_seeds": list(primary)})


def reserve_decision(run_dir, minimum_valid_worlds: int, reserve: list[int]) -> dict:
    if verify(run_dir)["state"] != "PRIMARY_CLOSED":
        raise LedgerError("reserve decision requires PRIMARY_CLOSED")
    primary_events = [e for e in completed_seed_events(run_dir) if e["phase"] == "primary"]
    valid = sum(bool(e["feasibility_projection"]["valid"]) for e in primary_events)
    active = valid < int(minimum_valid_worlds) and bool(reserve)
    body = {
        "active": active,
        "valid_worlds_after_primary": valid,
        "minimum_valid_worlds": int(minimum_valid_worlds),
        "next_reserve_seed": int(reserve[0]) if active else None,
        "fields_used": [
            "seed",
            "eligible",
            "deep_reached",
            "rest_assay_valid",
            "deep_assay_valid",
            "valid",
            "reason",
        ],
        "outcome_fields_used": [],
    }
    transition(run_dir, "DECIDE_RESERVE", body)
    return body


def assert_family_closable(
    run_dir,
    primary: list[int],
    reserve: list[int],
    minimum_valid_worlds: int,
) -> None:
    all_events = completed_seed_events(run_dir)
    by_seed = {int(e["seed"]): e for e in all_events}
    missing_primary = [seed for seed in primary if seed not in by_seed]
    if missing_primary:
        raise LedgerError(f"family missing primary seeds: {missing_primary}")
    decisions = [e for e in entries(run_dir) if e["event"] == "DECIDE_RESERVE"]
    if len(decisions) != 1:
        raise LedgerError("family requires exactly one reserve decision")
    decision = decisions[0]
    reserve_done = [int(e["seed"]) for e in all_events if e["phase"] == "reserve"]
    if reserve_done != reserve[: len(reserve_done)]:
        raise LedgerError("reserve seeds are not an ascending prefix")
    total_valid = sum(bool(e["feasibility_projection"]["valid"]) for e in all_events)
    if decision["active"]:
        if total_valid < minimum_valid_worlds and reserve_done != reserve:
            raise LedgerError("reserve family closed before threshold or hard cap")
        if total_valid >= minimum_valid_worlds:
            first_reaching = None
            count = sum(
                bool(e["feasibility_projection"]["valid"])
                for e in all_events
                if e["phase"] == "primary"
            )
            for index, seed in enumerate(reserve_done):
                count += bool(by_seed[seed]["feasibility_projection"]["valid"])
                if count >= minimum_valid_worlds:
                    first_reaching = index + 1
                    break
            if first_reaching != len(reserve_done):
                raise LedgerError("reserve execution continued after reaching minimum valid worlds")
    elif reserve_done:
        raise LedgerError("reserve seeds ran despite inactive reserve decision")
    if incomplete_seed(run_dir) is not None:
        raise LedgerError("cannot close family with an incomplete seed")


def close_family(
    run_dir,
    primary: list[int],
    reserve: list[int],
    minimum_valid_worlds: int,
    raw_manifest_entry: dict,
) -> dict:
    assert_family_closable(run_dir, primary, reserve, minimum_valid_worlds)
    return transition(run_dir, "CLOSE_FAMILY", {"raw_manifest": raw_manifest_entry})


def record_analysis(run_dir, analysis_entry: dict) -> dict:
    return transition(run_dir, "RECORD_ANALYSIS", {"analysis": analysis_entry})


def certify(run_dir, certificate_entry: dict) -> dict:
    return transition(run_dir, "CERTIFY", {"certificate": certificate_entry})
