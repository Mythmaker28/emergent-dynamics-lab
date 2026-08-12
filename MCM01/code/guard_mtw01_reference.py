"""Mechanical enforcement of the start budget and of the test/experiment separation.

This module exists because of the MINCORE protocol-order violation recorded in
MINCORE_SCOPE_CORRECTION_ADDENDUM section 2.2: a full-horizon arm was executed inside an
integrity harness. There, "a bounded invariant check" and "an experimental arm" were
distinguished only by the intention of the author. Here they are distinguished by the code:

  * `advance()` is the ONLY way to move a world forward. mtw.World deliberately exposes
    `_one_step` and no public `advance`.
  * In EXPERIMENT mode every call must be inside an open `start()`, and starts are capped at
    MAX_STARTS. The ledger is incremented BEFORE the first step, not after the last.
  * In TEST mode no start may be opened at all, the total number of steps across the WHOLE
    harness is capped at MAX_TEST_STEPS, and every scoring function raises on call. A
    full-horizon arm inside the test harness is therefore a RuntimeError, not a judgement call.
"""
from __future__ import annotations

MAX_STARTS = 16                 # MAX_NEW_OUTCOME_INFORMATIVE_STARTS, TECHNICAL_RESERVE = 0
MAX_TEST_STEPS = 3000           # across the entire integrity harness, all worlds together

_mode = "EXPERIMENT"
_test_steps = 0
_open_start = None
LEDGER = {"count": 0, "log": []}


class ProtocolError(RuntimeError):
    pass


def set_test_mode():
    """Bounded advances allowed, no start may be opened, every scoring function raises."""
    global _mode
    _mode = "TEST"


def set_static_mode():
    """No advance of any kind is allowed; scoring functions may be exercised on hand-built
    states. This is how the observable and verdict code is tested without any trajectory."""
    global _mode
    _mode = "STATIC"


def set_experiment_mode():
    global _mode
    _mode = "EXPERIMENT"


def mode():
    return _mode


def assert_not_test_mode(what):
    if _mode == "TEST":
        raise ProtocolError(
            "%s is a scoring function and cannot be called in TEST mode. This is the "
            "mechanical form of the MINCORE correction." % what)


class start:
    """Context manager. Opening it consumes one outcome-informative start, immediately."""

    def __init__(self, kind, tag, planned_steps):
        self.kind, self.tag, self.planned = kind, tag, int(planned_steps)

    def __enter__(self):
        global _open_start
        if _mode == "TEST":
            raise ProtocolError("no start may be opened in TEST mode")
        if _open_start is not None:
            raise ProtocolError("a start is already open: %s" % (_open_start,))
        if LEDGER["count"] + 1 > MAX_STARTS:
            raise ProtocolError("STOP__BUDGET_EXCEEDED: %d starts already consumed"
                                % LEDGER["count"])
        LEDGER["count"] += 1
        LEDGER["log"].append({"n": LEDGER["count"], "kind": self.kind, "tag": self.tag,
                              "planned_steps": self.planned, "steps_used": 0})
        _open_start = self.tag
        return self

    def __exit__(self, *a):
        global _open_start
        _open_start = None
        return False


def advance(w, steps, per_step=None):
    """The only way to move a world. `per_step(w)` may return 'STOP' to exit early."""
    global _test_steps
    steps = int(steps)
    if _mode == "STATIC":
        raise ProtocolError("advance() is forbidden in STATIC mode")
    if _mode == "TEST":
        if _test_steps + steps > MAX_TEST_STEPS:
            raise ProtocolError(
                "TEST step budget exhausted: %d + %d > MAX_TEST_STEPS=%d. A full-horizon arm "
                "cannot be run inside the integrity harness."
                % (_test_steps, steps, MAX_TEST_STEPS))
        _test_steps += steps
    else:
        if _open_start is None:
            raise ProtocolError("advance() outside an open start")
    used = 0
    for _ in range(steps):
        w._one_step()
        used += 1
        if per_step is not None and per_step(w) == "STOP":
            break
    if _mode == "EXPERIMENT":
        LEDGER["log"][-1]["steps_used"] += used
    return used


def audit():
    """Recompute the total from the ledger itself and cross-check it against the log length.
    A mismatch is reported as a failure, never silently overwritten by a constant."""
    n_log = len(LEDGER["log"])
    ok = (n_log == LEDGER["count"]) and all(
        e["n"] == i + 1 for i, e in enumerate(LEDGER["log"]))
    return {"count": LEDGER["count"], "log_entries": n_log, "consistent": bool(ok),
            "max_starts": MAX_STARTS, "technical_reserve": 0,
            "test_steps_used": _test_steps, "max_test_steps": MAX_TEST_STEPS,
            "log": LEDGER["log"]}
