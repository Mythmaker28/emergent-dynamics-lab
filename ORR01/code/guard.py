"""Mechanical enforcement of the MCM01 start budget and of the test/experiment separation.

Same three-mode design as MTW01 (which is the mechanical form of the MINCORE correction), with
one addition this mission requires: starts are counted PER CLASS, and each class has its own
cap. A calibration start can never be silently reclassified as a confirmation.

  TEST        bounded advances, no start may be opened, every scoring function raises
  STATIC      no advance of any kind, scoring may be exercised on hand-built states
  EXPERIMENT  every advance must sit inside an open start of a declared class
"""
from __future__ import annotations

# ------------------------------------------------------------------ frozen budget
CAPS = {
    "cost_probe": 2,        # timing only, on a provably non-scientific manifold (Y == 0)
    "confirmation": 12,     # 6 paired seeds x 2 arms (additive control, repaired LawSpec)
    "control": 8,           # the pre-declared controls
}
MAX_TEST_STEPS = 8000       # across the entire integrity harness, all worlds together

_mode = "EXPERIMENT"
_test_steps = 0
_open = None
LEDGER = {"log": [], "invalid": []}


class ProtocolError(RuntimeError):
    pass


def set_test_mode():
    global _mode
    _mode = "TEST"


def set_static_mode():
    global _mode
    _mode = "STATIC"


def set_experiment_mode():
    global _mode
    _mode = "EXPERIMENT"


def mode():
    return _mode


def assert_not_test_mode(what):
    if _mode == "TEST":
        raise ProtocolError("%s is a scoring function and cannot be called in TEST mode" % what)


def used(cls=None):
    if cls is None:
        return len(LEDGER["log"])
    return sum(1 for e in LEDGER["log"] if e["class"] == cls)


class start:
    """Context manager. Opening it consumes one start of `cls`, immediately and irrevocably."""

    def __init__(self, cls, tag, planned_steps):
        if cls not in CAPS:
            raise ProtocolError("undeclared start class %r" % cls)
        self.cls, self.tag, self.planned = cls, tag, int(planned_steps)

    def __enter__(self):
        global _open
        if _mode != "EXPERIMENT":
            raise ProtocolError("no start may be opened in %s mode" % _mode)
        if _open is not None:
            raise ProtocolError("a start is already open: %s" % (_open,))
        if used(self.cls) + 1 > CAPS[self.cls]:
            raise ProtocolError("STOP__BUDGET_EXCEEDED for class %r: %d already consumed of %d"
                                % (self.cls, used(self.cls), CAPS[self.cls]))
        LEDGER["log"].append({"n": len(LEDGER["log"]) + 1, "class": self.cls, "tag": self.tag,
                              "planned_steps": self.planned, "steps_used": 0, "valid": True})
        _open = (self.cls, self.tag)
        return self

    def __exit__(self, exc_type, *a):
        global _open
        if exc_type is not None:
            LEDGER["log"][-1]["valid"] = False
            LEDGER["log"][-1]["invalidated_by"] = repr(exc_type)
            LEDGER["invalid"].append(LEDGER["log"][-1])
        _open = None
        return False


def advance(w, steps, per_step=None):
    """The only way to move a world. kinetics.World exposes no public advance."""
    global _test_steps
    steps = int(steps)
    if _mode == "STATIC":
        raise ProtocolError("advance() is forbidden in STATIC mode")
    if _mode == "TEST":
        if _test_steps + steps > MAX_TEST_STEPS:
            raise ProtocolError("TEST step budget exhausted: %d + %d > %d"
                                % (_test_steps, steps, MAX_TEST_STEPS))
        _test_steps += steps
    elif _open is None:
        raise ProtocolError("advance() outside an open start")
    n = 0
    for _ in range(steps):
        w._one_step()
        n += 1
        if per_step is not None and per_step(w) == "STOP":
            break
    if _mode == "EXPERIMENT":
        LEDGER["log"][-1]["steps_used"] += n
    return n


def audit():
    by = {c: used(c) for c in CAPS}
    consistent = all(e["n"] == i + 1 for i, e in enumerate(LEDGER["log"]))
    return {"by_class": by, "caps": dict(CAPS), "total": len(LEDGER["log"]),
            "valid": sum(1 for e in LEDGER["log"] if e["valid"]),
            "invalid": len(LEDGER["invalid"]), "sequence_consistent": bool(consistent),
            "test_steps_used": _test_steps, "max_test_steps": MAX_TEST_STEPS,
            "log": LEDGER["log"]}
