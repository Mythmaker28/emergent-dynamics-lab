"""CSC01 start budget. Separate ledger from ORR01, separate caps, separate classes.

THE CLASS `raw_replay` IS NOT A SCIENTIFIC START.
A replay re-derives, bit for bit, a trajectory ORR01 already opened and already consumed. It
uses no new seed, opens no new branch of the process, and is admitted into the analysis ONLY
after `replay.verify` has proved the replayed series and final fields identical to the recorded
ones. It therefore adds no information beyond the recorded raw, and it is counted in its own
ledger line so that it can never be confused with a start.

`SCIENTIFIC_RUNS_USED` counts only: calibration, confirmation, control.
"""
from __future__ import annotations

CAPS = {
    "raw_replay": 40,        # NOT scientific: bit-exact re-derivation of consumed ORR01 starts
    "calibration": 8,        # passive assay, own seeds, outcome-independent
    "confirmation": 16,
    "control": 12,
    "cost_probe": 2,
}
NON_SCIENTIFIC = ("raw_replay", "cost_probe")
MAX_TEST_STEPS = 20000

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


def scientific_runs_used():
    return sum(1 for e in LEDGER["log"] if e["class"] not in NON_SCIENTIFIC)


class start:
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
                              "planned_steps": self.planned, "steps_used": 0, "valid": True,
                              "scientific": self.cls not in NON_SCIENTIFIC})
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
            "SCIENTIFIC_RUNS_USED": scientific_runs_used(),
            "non_scientific_classes": list(NON_SCIENTIFIC),
            "valid": sum(1 for e in LEDGER["log"] if e["valid"]),
            "invalid": len(LEDGER["invalid"]), "sequence_consistent": bool(consistent),
            "test_steps_used": _test_steps, "max_test_steps": MAX_TEST_STEPS,
            "log": LEDGER["log"]}
