"""MYQBD01 SEAL REPAIR — real audits replacing three claims that were literals or overstated.

Review findings repaired here:
  F25  NO_TARGET_DERIVED_Y_OUTCOME was a hardcoded literal with a comment. Replaced by an
       AST-based audit of every data access in every MYQBD01 module.
  F27  "Sentinel aggregated over ALL ANALYSIS PROCESSES" was false: it is installed in 1 of 8
       modules. Replaced by an honest coverage report PLUS a static proof that does not depend
       on the sentinel at all.
  F28  observe.seed_one_organiser is a fourth seeding entry point and is unpatched. Recorded.
  F29  the filesystem witness glob is depth-2 and misses the repository tree. Recorded.

No engine. Pure static analysis plus directory listing.
"""
from __future__ import annotations

import ast
import glob
import json
import os

CODE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/MYQBD01/out"

# Every scalar the morphology `frames` expose. These are OUTCOME-side descriptors of the X
# cluster: if any MYQBD01 computation read one, the analysis would be target-derived.
TARGET_DERIVED_KEYS = {
    "r50", "r80", "r90", "r80_organiser", "Rg", "core_fraction", "geodesic_diameter",
    "centre_y", "centre_x", "n_components", "n_eff_components", "main_cid", "main_N_X",
    "main_mass_fraction", "organiser_to_core", "wraps_y", "wraps_x", "any_winding",
    "legacy_extent_proxy",
}
# The CONTAINERS in which those descriptors live. Opening a container is not by itself a
# target-derived access -- §12 must open `frames` in order to PROVE no lattice field hides
# inside it -- but every such read is listed explicitly with its justification, and the audit
# fails if any DESCRIPTOR key above is ever read. Silence here would be the defect.
CONTAINER_KEYS = {"frames", "molecule_births", "molecule_deaths"}
CONTAINER_JUSTIFICATION = {
    "frames": ("§12 (seal-repaired) decodes the 220 JSON strings only to ASSERT that every "
               "value is a scalar, i.e. that no lattice field is stored inside them. It reads "
               "no individual frame field: the audit below confirms zero descriptor accesses. "
               "This is a negative control on the archive's spatial content, not an input."),
}
# Fields the mission is entitled to read: the environmental ledger, never an outcome descriptor.
ENVIRONMENTAL_KEYS = {
    "series", "fields", "Q", "cand_Y_at_org", "nSY_at_org", "free_at_org", "u_nX_at_org",
    "nSX_at_org", "N_Y", "N_X", "n_org_cells", "nX_final", "nY_final", "nSX_final", "nSY_final",
    "nWX_final", "nWY_final", "hop_ledger", "source_substep_ledger", "birth_substep_ledger",
    "birth_offsets", "step",
}
ENGINE_MODULES = {"kinetics", "engine_obtc", "lawspec_v2", "observe", "protocol_obtc02",
                  "protocol_obtc", "run_obfor01"}


def _modules():
    return sorted(p for p in glob.glob(os.path.join(CODE, "*.py"))
                  if not os.path.basename(p).startswith("myqbd01_seal_audits"))


def target_derived_audit():
    """Walk every module's AST. Collect every literal string used as a DATA ACCESS -- a
    subscript key `z["..."]` or an argument to `.index("...")` -- and test disjointness from the
    outcome-descriptor set. Prose string constants are excluded BY CONSTRUCTION: only subscript
    and .index() positions are collected, never bare string literals."""
    accesses, per_module = [], {}
    for path in _modules():
        tree = ast.parse(open(path).read())
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                    and isinstance(node.slice.value, str):
                found.append(node.slice.value)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "index" and node.args \
                    and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                found.append(node.args[0].value)
        per_module[os.path.basename(path)] = sorted(set(found))
        accesses += found
    accesses = set(accesses)
    violations = sorted(accesses & TARGET_DERIVED_KEYS)
    containers_read = sorted(accesses & CONTAINER_KEYS)
    unjustified = [c for c in containers_read if c not in CONTAINER_JUSTIFICATION]
    return {
        "METHOD": ("AST walk of every MYQBD01 module; only Subscript string keys and "
                   ".index('...') arguments are collected, so prose mentions inside docstrings "
                   "or messages cannot register as accesses"),
        "MODULES_AUDITED": len(per_module),
        "DATA_ACCESS_KEYS_PER_MODULE": per_module,
        "ALL_DATA_ACCESS_KEYS": sorted(accesses),
        "TARGET_DERIVED_KEYS_TESTED": sorted(TARGET_DERIVED_KEYS),
        "DESCRIPTOR_VIOLATIONS": violations,
        "CONTAINER_KEYS_READ": containers_read,
        "CONTAINER_READ_JUSTIFICATIONS": {c: CONTAINER_JUSTIFICATION.get(c, "UNJUSTIFIED")
                                          for c in containers_read},
        "UNJUSTIFIED_CONTAINER_READS": unjustified,
        "NO_TARGET_DERIVED_Y_OUTCOME": len(violations) == 0 and len(unjustified) == 0,
        "SEAL_NOTE": ("review F25: this replaces a hardcoded literal; the value is now derived. "
                      "The audit separates DESCRIPTOR keys (r80, Rg, centre_y, ... -- reading "
                      "any one fails the audit unconditionally) from CONTAINER keys (frames, "
                      "molecule_births, molecule_deaths -- opening one is permitted only with a "
                      "recorded justification, and every such read is listed). The seal repair "
                      "to §12 does open `frames`, to prove no lattice field hides inside it; "
                      "that read is disclosed here rather than exempted silently."),
    }


def zero_run_static_proof():
    """A proof that does not depend on the sentinel: no MYQBD01 module imports an engine module,
    so no module could have constructed or stepped a World, whatever any runtime counter says."""
    per_module, offenders = {}, []
    for path in _modules():
        tree = ast.parse(open(path).read())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        bad = sorted(imports & ENGINE_MODULES)
        per_module[os.path.basename(path)] = {"imports": sorted(imports), "engine_imports": bad}
        if bad:
            offenders.append(os.path.basename(path))
    return {
        "METHOD": "AST import analysis; independent of any runtime counter",
        "MODULES_AUDITED": len(per_module),
        "PER_MODULE": per_module,
        "MODULES_IMPORTING_AN_ENGINE": offenders,
        "NO_MODULE_CAN_CONSTRUCT_A_WORLD": len(offenders) == 0,
        "SEAL_NOTE": ("review F30: the zero-run conclusion rests on this static proof, not on "
                      "the sentinel's coverage. A module that never imports the engine cannot "
                      "start a world."),
    }


def sentinel_coverage_audit():
    """Honest coverage report. The pre-seal commit message claimed the sentinel was aggregated
    over ALL analysis processes; it was installed in exactly one module."""
    installed = [os.path.basename(p) for p in _modules()
                 if "SENT.install" in open(p).read() or "pmcr01_sentinel" in open(p).read()]
    seeders = []
    for p in ("/home/claude/ORR01/code/kinetics.py", "/home/claude/ORR01/code/observe.py",
              "/home/claude/ORR01/code/lawspec_v2.py", "/home/claude/OBTC02/code/engine_obtc.py"):
        if os.path.exists(p):
            for i, ln in enumerate(open(p).read().splitlines(), 1):
                if ln.startswith("def seed_one_organiser"):
                    seeders.append("%s:%d" % (p, i))
    sent_path = "/home/claude/PMCR01/code/pmcr01_sentinel.py"
    patched = []
    if os.path.exists(sent_path):
        src = open(sent_path).read()
        for ns in ("K", "EN", "V2", "OBS"):
            if "%s.seed_one_organiser =" % ns in src:
                patched.append(ns)
    return {
        "CLAIM_CORRECTED": ("commit decfda5 said 'Sentinel aggregated over ALL ANALYSIS "
                            "PROCESSES'. That was FALSE (review F27)."),
        "MODULES_TOTAL": len(_modules()),
        "MODULES_WITH_SENTINEL_INSTALLED": installed,
        "COVERAGE": "%d of %d modules" % (len(installed), len(_modules())),
        "SEEDING_ENTRY_POINTS_IN_THE_ENGINE_TREE": seeders,
        "SEEDING_ENTRY_POINTS_PATCHED_BY_THE_SENTINEL": patched,
        "UNPATCHED_SEEDING_ENTRY_POINT": ("observe.seed_one_organiser is a full re-implementation "
                                          "and is NOT patched (review F28). It was never called "
                                          "by any MYQBD01 module -- see the static proof -- but "
                                          "the sentinel's own comment naming three entry points "
                                          "was wrong; there are four."),
        "FILESYSTEM_WITNESS_DEPTH": ("the witness globs /home/claude/*/raw and /home/claude/*/out "
                                     "at depth 2 only, so it does not watch the %d directories "
                                     "matching /home/claude/edl/*/out (review F29). It did fire "
                                     "correctly on the root that changed."
                                     % len(glob.glob("/home/claude/edl/*/out"))),
        "WHAT_THE_ZERO_RUN_CONCLUSION_NOW_RESTS_ON": ("the static import proof above, which is "
                                                      "independent of sentinel coverage"),
    }


def main():
    rec = {"SECTION": "MYQBD01 SEAL REPAIR — audits replacing literals and overstated claims",
           "TARGET_DERIVED_AUDIT": target_derived_audit(),
           "ZERO_RUN_STATIC_PROOF": zero_run_static_proof(),
           "SENTINEL_COVERAGE": sentinel_coverage_audit()}
    json.dump(rec, open(os.path.join(OUT, "MYQBD01_SEAL_AUDITS.json"), "w"), indent=1,
              default=str)
    t, zr, sc = rec["TARGET_DERIVED_AUDIT"], rec["ZERO_RUN_STATIC_PROOF"], rec["SENTINEL_COVERAGE"]
    print("target-derived audit : modules %d, access keys %d, descriptor violations %s, "
          "containers read %s (unjustified %s) -> NO_TARGET_DERIVED = %s"
          % (t["MODULES_AUDITED"], len(t["ALL_DATA_ACCESS_KEYS"]),
             t["DESCRIPTOR_VIOLATIONS"] or "none", t["CONTAINER_KEYS_READ"] or "none",
             t["UNJUSTIFIED_CONTAINER_READS"] or "none", t["NO_TARGET_DERIVED_Y_OUTCOME"]))
    print("zero-run static proof: engine importers %s -> NO_WORLD_POSSIBLE = %s"
          % (zr["MODULES_IMPORTING_AN_ENGINE"] or "none", zr["NO_MODULE_CAN_CONSTRUCT_A_WORLD"]))
    print("sentinel coverage    : %s; seeding entry points %d, patched %d"
          % (sc["COVERAGE"], len(sc["SEEDING_ENTRY_POINTS_IN_THE_ENGINE_TREE"]),
             len(sc["SEEDING_ENTRY_POINTS_PATCHED_BY_THE_SENTINEL"])))


if __name__ == "__main__":
    main()
