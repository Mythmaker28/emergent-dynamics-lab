"""MYQBD01 FINAL REPAIR — runtime zero-run guard (review finding A12/F27/F28/F29).

The ORIGINAL runtime sentinel was installed in 1 of 8 modules, missed a fourth seeding entry
point (`observe.seed_one_organiser`), and used a depth-2 filesystem glob that never watched the
repository tree. This guard replaces it FOR THE REPAIR SCRIPTS ONLY. It does not, and cannot,
retroactively improve the original run's coverage — that is reported separately and honestly.

What it does:
  * patches EVERY known World constructor and scheduler step in the engine tree;
  * patches ALL FOUR module-level seeding entry points, including observe.seed_one_organiser;
  * wraps subprocess.run / Popen / check_output and records every command;
  * takes a RECURSIVE filesystem inventory (no depth limit) of every physics array under every
    mission, repository and delivery root.

A guarded call does not merely increment a counter: it RAISES. A scientific run during a repair
round is a hard error, not a statistic.

NOTE ON THE STATIC PROOF: this module is REPAIR INFRASTRUCTURE, not an analysis module. It is
the only file in the mission that imports the engine at all, and it does so solely in order to
patch it. The static import proof is computed over the ANALYSIS modules and reports this module
separately; conflating the two would be exactly the kind of overstated coverage claim the review
caught.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

for _p in ("/home/claude/ORR01/code", "/home/claude/OBTC02/code", "/home/claude/OBFOR01/code"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

COUNTERS = {"ENGINE_CONSTRUCT_CALLS": 0, "ENGINE_ADVANCE_CALLS": 0,
            "SCIENTIFIC_WORLD_STARTS": 0, "SCIENTIFIC_SEEDS_OPENED": 0,
            "NEW_PHYSICS_ARRAYS_WRITTEN": 0}
PATCHED = {"world_constructors": [], "scheduler_steps": [], "seeding_entry_points": []}
SUBPROCESS_LOG = []
_BASELINE = {}
ARRAY_EXT = (".npz", ".npy")
# every mission, repository and delivery root, walked RECURSIVELY with no depth limit
ROOTS = ["/home/claude"]
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


class ZeroRunViolation(RuntimeError):
    pass


def _deny(kind, label):
    def guarded(*a, **k):
        COUNTERS[kind] += 1
        if kind == "ENGINE_CONSTRUCT_CALLS":
            COUNTERS["SCIENTIFIC_WORLD_STARTS"] += 1
        if kind == "SCIENTIFIC_SEEDS_OPENED":
            pass
        raise ZeroRunViolation(
            "ZERO-RUN VIOLATION: %s was called via %s during a repair round. "
            "NEW_SCIENTIFIC_ENGINE_RUNS = 0 is mandatory." % (label, kind))
    return guarded


def install():
    """Patch every engine entry point reachable in this interpreter."""
    mods = {}
    for name in ("kinetics", "lawspec_v2", "engine_obtc", "observe"):
        try:
            mods[name] = __import__(name)
        except Exception as e:                                    # pragma: no cover
            PATCHED.setdefault("import_failures", []).append("%s: %s" % (name, e))
    # --- world constructors and scheduler steps, on EVERY World class found ---
    for mname, mod in mods.items():
        for attr in dir(mod):
            obj = getattr(mod, attr, None)
            if isinstance(obj, type) and hasattr(obj, "_one_step") and hasattr(obj, "__init__"):
                obj.__init__ = _deny("ENGINE_CONSTRUCT_CALLS", "%s.%s.__init__" % (mname, attr))
                PATCHED["world_constructors"].append("%s.%s.__init__" % (mname, attr))
                obj._one_step = _deny("ENGINE_ADVANCE_CALLS", "%s.%s._one_step" % (mname, attr))
                PATCHED["scheduler_steps"].append("%s.%s._one_step" % (mname, attr))
                for extra in ("_react", "_react_core", "step", "advance", "run"):
                    if hasattr(obj, extra):
                        setattr(obj, extra,
                                _deny("ENGINE_ADVANCE_CALLS", "%s.%s.%s" % (mname, attr, extra)))
                        PATCHED["scheduler_steps"].append("%s.%s.%s" % (mname, attr, extra))
    # --- ALL FOUR module-level seeding entry points ---
    for mname, mod in mods.items():
        if hasattr(mod, "seed_one_organiser"):
            setattr(mod, "seed_one_organiser",
                    _deny("SCIENTIFIC_SEEDS_OPENED", "%s.seed_one_organiser" % mname))
            PATCHED["seeding_entry_points"].append("%s.seed_one_organiser" % mname)
    # --- subprocess audit ---
    for fn in ("run", "Popen", "check_output", "call", "check_call"):
        orig = getattr(subprocess, fn, None)
        if orig is None:
            continue

        def wrap(orig=orig, fn=fn):
            def w(*a, **k):
                cmd = a[0] if a else k.get("args")
                SUBPROCESS_LOG.append({"fn": fn, "cmd": cmd if isinstance(cmd, str)
                                       else [str(x) for x in (cmd or [])]})
                return orig(*a, **k)
            return w
        setattr(subprocess, fn, wrap())
    _BASELINE.update(_inventory())
    return {"PATCHED": PATCHED, "BASELINE_ARRAYS": len(_BASELINE)}


def _inventory():
    """Recursive, no depth limit, every physics array under every root."""
    inv = {}
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(ARRAY_EXT):
                    p = os.path.join(dirpath, fn)
                    try:
                        st = os.stat(p)
                        inv[p] = (st.st_size, st.st_mtime_ns)
                    except OSError:
                        pass
    return inv


def report():
    now = _inventory()
    created = sorted(set(now) - set(_BASELINE))
    modified = sorted(p for p in set(now) & set(_BASELINE) if now[p] != _BASELINE[p])
    COUNTERS["NEW_PHYSICS_ARRAYS_WRITTEN"] = len(created) + len(modified)
    engine_cmds = [s for s in SUBPROCESS_LOG
                   if any(t in " ".join(s["cmd"] if isinstance(s["cmd"], list) else [s["cmd"]])
                          for t in ("run_obfor01", "protocol_obtc", "kinetics", "engine_obtc",
                                    "lawspec_v2"))]
    return {
        "GUARD": "MYQBD01 final-repair runtime guard",
        "COUNTERS": dict(COUNTERS),
        "PATCH_COVERAGE": {
            "world_constructors": sorted(set(PATCHED["world_constructors"])),
            "scheduler_steps": sorted(set(PATCHED["scheduler_steps"])),
            "seeding_entry_points": sorted(set(PATCHED["seeding_entry_points"])),
            "seeding_entry_points_count": len(set(PATCHED["seeding_entry_points"])),
            "ALL_FOUR_SEEDING_ENTRY_POINTS_PATCHED":
                len(set(PATCHED["seeding_entry_points"])) == 4},
        "FILESYSTEM_WITNESS": {
            "MODE": "os.walk, RECURSIVE, NO DEPTH LIMIT",
            "ROOTS": ROOTS, "SKIPPED_DIR_NAMES": sorted(SKIP_DIRS),
            "ARRAYS_AT_BASELINE": len(_BASELINE), "ARRAYS_NOW": len(now),
            "CREATED": created, "MODIFIED": modified},
        "SUBPROCESS_AUDIT": {"calls": len(SUBPROCESS_LOG),
                             "engine_invoking_calls": engine_cmds,
                             "NO_ENGINE_SUBPROCESS": len(engine_cmds) == 0},
        "VERDICT": {
            "ENGINE_CONSTRUCT_CALLS": COUNTERS["ENGINE_CONSTRUCT_CALLS"],
            "ENGINE_ADVANCE_CALLS": COUNTERS["ENGINE_ADVANCE_CALLS"],
            "SCIENTIFIC_WORLD_STARTS": COUNTERS["SCIENTIFIC_WORLD_STARTS"],
            "SCIENTIFIC_SEEDS_OPENED": COUNTERS["SCIENTIFIC_SEEDS_OPENED"],
            "NEW_PHYSICS_ARRAYS_WRITTEN": COUNTERS["NEW_PHYSICS_ARRAYS_WRITTEN"],
            "ALL_ZERO": all(v == 0 for v in COUNTERS.values())},
    }


def selftest():
    """Positive control: the guard must actually fire. Prove it, do not assume it."""
    import kinetics as K
    fired = []
    for label, fn in (("World.__init__", lambda: K.World(L=4)),
                      ("seed_one_organiser", lambda: K.seed_one_organiser(None))):
        try:
            fn()
            fired.append({"entry": label, "RAISED": False})
        except ZeroRunViolation:
            fired.append({"entry": label, "RAISED": True})
        except Exception as e:
            fired.append({"entry": label, "RAISED": False, "other": type(e).__name__})
    # the self-test deliberately trips the counters; reset them so the witness stays clean
    before = dict(COUNTERS)
    for k in COUNTERS:
        COUNTERS[k] = 0
    return {"POSITIVE_CONTROL": fired,
            "ALL_ENTRY_POINTS_RAISED": all(f["RAISED"] for f in fired),
            "counters_during_selftest": before,
            "counters_reset_after_selftest": dict(COUNTERS)}


if __name__ == "__main__":
    print(json.dumps(install(), indent=1, default=str)[:600])
    print(json.dumps(selftest(), indent=1, default=str))
    print(json.dumps(report()["VERDICT"], indent=1))
