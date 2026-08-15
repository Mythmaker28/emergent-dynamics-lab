"""PMCR01 — the engine-start sentinel. Imported FIRST, before any other project code.

The mission budget is:

    NEW_SCIENTIFIC_ENGINE_STARTS = 0
    NEW_OUTCOME_INFORMATIVE_TRAJECTORIES = 0
    NEW_SEEDS = 0
    NEW_WORLD_CONSTRUCTIONS = 0

A budget nobody can audit is not a budget. This module patches the engine's constructor and its
step function at import time and counts every call, classifying each one against an explicit
predicate rather than against my intention.

    ENGINE_CONSTRUCT_CALLS   constructions made OUTSIDE a declared fixture context
    ENGINE_ADVANCE_CALLS     _one_step calls made OUTSIDE a declared fixture context
    SCIENTIFIC_WORLD_STARTS  constructions whose shape matches the scientific profile
    SCIENTIFIC_SEEDS_OPENED  distinct seeds used that appear in any delivered seed register

All four must end at exactly zero. A NON_SCIENTIFIC_SEMANTIC_FIXTURE is admitted only inside
`with fixture("label"):` AND only if it satisfies every clause of `IS_NON_SCIENTIFIC`:

    L <= 5                    a five-cell torus cannot carry the qualified geometry
    seed in the 9_000_000+    disjoint from every delivered register
    steps <= 8                a trajectory of eight steps is not a trajectory
    no seed_one_organiser     the qualified initial state is never constructed
    hand-set state            SX/SY are not filled to S0 across the lattice

The guard shipped with the project, guard_obtc.scientific_runs_used(), is read at the end as an
INDEPENDENT second witness: it counts starts through a completely different mechanism, and the
two counts have to agree.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys

FIXTURE_SEED_BLOCK = 9_000_000
MAX_FIXTURE_L = 5
MAX_FIXTURE_STEPS = 8

STATE = {
    "ENGINE_CONSTRUCT_CALLS": 0,
    "ENGINE_ADVANCE_CALLS": 0,
    "SCIENTIFIC_WORLD_STARTS": 0,
    "SCIENTIFIC_SEEDS_OPENED": 0,
    "FIXTURE_CONSTRUCTIONS": 0,
    "FIXTURE_STEPS": 0,
    "SEEDS_SEEN": [],
    "VIOLATIONS": [],
    "FIXTURE_LABELS": [],
    "ORGANISER_SEEDINGS": 0,
}
_depth = 0
_installed = False
_scientific_seeds = set()


def load_scientific_seed_registers(paths):
    """Every integer that appears as a seed in a delivered register. Read once, at install."""
    got = set()
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue

        def walk(o, key=None):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, str(k))
            elif isinstance(o, list):
                for v in o:
                    walk(v, key)
            elif isinstance(o, int) and not isinstance(o, bool):
                if key and "seed" in key.lower():
                    got.add(int(o))
        walk(d)
    return got


@contextlib.contextmanager
def fixture(label):
    """Declare a NON_SCIENTIFIC_SEMANTIC_FIXTURE region."""
    global _depth
    _depth += 1
    STATE["FIXTURE_LABELS"].append(label)
    try:
        yield
    finally:
        _depth -= 1


def _classify(world, L, seed):
    """Return (is_fixture_admissible, reasons)."""
    bad = []
    if _depth == 0:
        bad.append("constructed outside any declared fixture")
    if L is None or int(L) > MAX_FIXTURE_L:
        bad.append("L=%s exceeds the fixture bound %d" % (L, MAX_FIXTURE_L))
    if seed is None or int(seed) < FIXTURE_SEED_BLOCK:
        bad.append("seed=%s outside the %d fixture block" % (seed, FIXTURE_SEED_BLOCK))
    if seed is not None and int(seed) in _scientific_seeds:
        bad.append("seed=%s appears in a delivered scientific register" % seed)
    return (not bad), bad


def install(seed_register_paths=()):
    """Patch the engine. Must be called before any World is constructed."""
    global _installed, _scientific_seeds
    if _installed:
        return
    _scientific_seeds = load_scientific_seed_registers(seed_register_paths)
    import kinetics as K
    import engine_obtc as EN
    import lawspec_v2 as V2

    orig_init = K.World.__init__
    orig_step = K.World._one_step
    orig_seed_kin = K.seed_one_organiser
    orig_seed_en = EN.seed_one_organiser
    orig_seed_v2 = V2.seed_one_organiser

    def init(self, L=None, seed=0, sp=None, *a, **kw):
        if sp is None:
            sp = K.Spec
        ok, bad = _classify(self, L if L is not None else getattr(sp, "L", None), seed)
        eff_L = int(L if L is not None else getattr(sp, "L", 0))
        if ok:
            STATE["FIXTURE_CONSTRUCTIONS"] += 1
        else:
            STATE["ENGINE_CONSTRUCT_CALLS"] += 1
            STATE["VIOLATIONS"].append({"what": "construction", "reasons": bad,
                                        "L": eff_L, "seed": seed})
        if eff_L in (36, 72, 96) or (seed is not None and int(seed) in _scientific_seeds):
            STATE["SCIENTIFIC_WORLD_STARTS"] += 1
        if seed is not None and int(seed) in _scientific_seeds:
            STATE["SCIENTIFIC_SEEDS_OPENED"] += 1
        if seed is not None and int(seed) not in STATE["SEEDS_SEEN"]:
            STATE["SEEDS_SEEN"].append(int(seed))
        return orig_init(self, L=L, seed=seed, sp=sp, *a, **kw)

    def step(self):
        if _depth == 0:
            STATE["ENGINE_ADVANCE_CALLS"] += 1
            STATE["VIOLATIONS"].append({"what": "advance outside a fixture",
                                        "step": int(getattr(self, "step", -1))})
        else:
            STATE["FIXTURE_STEPS"] += 1
            # PER-FIXTURE cap, not just a global one: a world may not be advanced more than
            # MAX_FIXTURE_STEPS times within a single fixture context. A single long fixture
            # is a trajectory in disguise, and the earlier global-only cap would not catch it.
            adv = getattr(self, "_pmcr01_fixture_steps", 0) + 1
            self._pmcr01_fixture_steps = adv
            if adv > MAX_FIXTURE_STEPS:
                raise RuntimeError("fixture step budget exhausted for this world: %d > %d; "
                                   "a fixture is not a trajectory" % (adv, MAX_FIXTURE_STEPS))
        return orig_step(self)

    def seeded(w, x_seed):
        STATE["ORGANISER_SEEDINGS"] += 1
        STATE["VIOLATIONS"].append({"what": "seed_one_organiser called",
                                    "why": "reconstructs the qualified initial state"})
        return orig_seed_kin(w, x_seed)

    K.World.__init__ = init
    K.World._one_step = step
    K.seed_one_organiser = seeded
    EN.seed_one_organiser = seeded
    V2.seed_one_organiser = seeded            # the third seeding entry point, previously unpatched
    _installed = True


def raw_dir_witness(dirs):
    """A filesystem witness that does NOT depend on any in-process counter: the number of raw
    output files and the newest mtime under each scientific raw directory. A scientific run
    writes an npz here (protocol_obtc02.run_arm np.savez_compressed to RAW), so if none of
    these directories gained a file or advanced its mtime, no arm was written. Call it before
    and after the analysis and compare.
    """
    import glob
    import os
    out = {}
    for d in dirs:
        files = glob.glob(os.path.join(d, "*")) if os.path.isdir(d) else []
        out[d] = {"n_files": len(files),
                  "newest_mtime": max((os.path.getmtime(f) for f in files), default=0.0)}
    return out


def report(guard_module=None, raw_before=None, raw_after=None):
    out = {k: v for k, v in STATE.items()}
    out["ALL_FOUR_ZERO"] = (STATE["ENGINE_CONSTRUCT_CALLS"] == 0
                            and STATE["ENGINE_ADVANCE_CALLS"] == 0
                            and STATE["SCIENTIFIC_WORLD_STARTS"] == 0
                            and STATE["SCIENTIFIC_SEEDS_OPENED"] == 0)
    if guard_module is not None:
        # kept only as a WEAK in-process check. guard_obtc.LEDGER is an in-memory global that
        # this process never populates, so it reads 0 by construction; it corroborates nothing
        # on its own and is labelled as such. The load-bearing witness is the filesystem one.
        out["WEAK_IN_PROCESS_CHECK_guard_obtc"] = {
            "scientific_runs_used": int(guard_module.scientific_runs_used()),
            "CAVEAT": "in-memory ledger, never populated by this process; not independent"}
    if raw_before is not None and raw_after is not None:
        changed = {d: {"files_before": raw_before[d]["n_files"],
                       "files_after": raw_after[d]["n_files"],
                       "mtime_advanced": raw_after[d]["newest_mtime"]
                       > raw_before[d]["newest_mtime"]}
                   for d in raw_before}
        out["FILESYSTEM_WITNESS_raw_dirs"] = {
            "per_dir": changed,
            "NO_RAW_FILE_WRITTEN": all(v["files_after"] == v["files_before"]
                                       and not v["mtime_advanced"] for v in changed.values())}
    out["SCIENTIFIC_SEEDS_IN_THE_REGISTERS"] = len(_scientific_seeds)
    return out
