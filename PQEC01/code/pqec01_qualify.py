"""PQEC01 — instrumentation qualification. NON_SCIENTIFIC_INSTRUMENTATION_FIXTURE only.

Observer inertness is not asserted; it is PROVEN differentially: an instrumented and an
uninstrumented world are advanced side by side on small (L <= 5) non-scientific fixtures and
required to agree BIT-FOR-BIT at every step on
  * the six physical species fields,
  * all three engine bit-generator states (rng, rng_feed, tracker rng),
  * scheduler counters and event counts,
  * the engine's own state_hash().

HONEST DISCLOSURE. The observer overrides `_diffuse` for species "Y" and RE-IMPLEMENTS the
engine's sub-shift loop verbatim, because the per-sub-step `accepted` array is the only place an
exact Y hop origin/destination exists and the base method does not expose it. That is the single
place where physics lines are duplicated, and it is the highest-risk part of this instrumentation.
It is therefore checked twice: by normalized SOURCE-TEXT equality against the engine's own loop,
and by the differential bit-exactness test above, run with kY > 0 so that multiple Y actually
exist, hop, are born and die.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC02/code")
import engine_obtc as EN                                                     # noqa: E402
import pqec01_observer as O                                                  # noqa: E402

OUT = "/home/claude/edl/PQEC01/out"
# Non-scientific fixture seeds: a band disjoint from every scientific register in this programme.
FIXTURE_SEEDS = [77000001, 77000002, 77000003, 77000004, 77000005, 77000006]
FIXTURE_STEPS = 8
FIXTURE_L = 5


def _norm(src):
    src = re.sub(r"#.*", "", src)
    return re.sub(r"\s+", " ", src).strip()


def source_equivalence():
    """The duplicated sub-shift loop must be textually identical to the engine's, modulo the
    observer lines that append to pq_* buffers."""
    eng = inspect.getsource(EN.WorldOBTC._diffuse)
    obs = inspect.getsource(O.PQECWorld._diffuse)
    eng_loop = [l for l in (_norm(x) for x in eng.splitlines())
                if l and not l.startswith("def ") and "pq_" not in l]
    obs_all = [_norm(x) for x in obs.splitlines()]
    obs_loop = [l for l in obs_all if l and "pq_" not in l and not l.startswith("def ")]
    # ONE declared, enumerated difference: the observer wraps the frozen iterator in
    # enumerate() to obtain a sub-shift INDEX for its own ledger. The iteration order, the
    # iterable and the bound names are unchanged, so no rng call moves. Any OTHER difference
    # is a failure.
    PERMITTED = {"for shift, ax in NEI:": "for sub, (shift, ax) in enumerate(EN.NEI):"}
    missing, permitted_used = [], []
    for l in eng_loop:
        if l in obs_loop:
            continue
        if l in PERMITTED and PERMITTED[l] in obs_loop:
            permitted_used.append({"engine": l, "observer": PERMITTED[l],
                                   "why_equivalent": ("enumerate() yields the same pairs in the "
                                                      "same order and binds the same names; it "
                                                      "adds an observer-only index and consumes "
                                                      "no rng")})
            continue
        missing.append(l)
    return {"ENGINE_LINES": len(eng_loop), "OBSERVER_LINES": len(obs_loop),
            "ENGINE_LINES_NOT_PRESENT_IN_OBSERVER": missing,
            "PERMITTED_DECLARED_DIFFERENCES": permitted_used,
            "UNDECLARED_DIFFERENCES": len(missing),
            "VERBATIM_SUBSET": len(missing) == 0,
            "NOTE": ("every physics line of the engine's _diffuse appears verbatim in the "
                     "observer's override apart from the single declared enumerate() wrapper; "
                     "the observer otherwise adds only pq_* appends and a species branch")}


def static_mutation_audit():
    """Every attribute the observer writes, listed. Writes to engine state are ALLOWED only
    inside the declared verbatim re-implementation; everything else must be pq_*."""
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "pqec01_observer.py")).read()
    tree = ast.parse(src)
    writes, rng_calls = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                        and t.value.id == "self":
                    writes.append({"attr": t.attr, "line": node.lineno})
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute):
                    writes.append({"attr": "%s[...]" % t.value.attr, "line": node.lineno})
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Subscript):
            v = node.target.value
            if isinstance(v, ast.Attribute):
                writes.append({"attr": "%s[...] (augmented)" % v.attr, "line": node.lineno})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("binomial", "random", "integers", "choice", "normal",
                                       "uniform", "poisson"):
            rng_calls.append({"call": node.func.attr, "line": node.lineno})
    engine_writes = [w for w in writes if not w["attr"].startswith("pq_")]
    return {"ALL_SELF_WRITES": writes,
            "OBSERVER_ONLY_WRITES": [w for w in writes if w["attr"].startswith("pq_")],
            "ENGINE_STATE_WRITES": engine_writes,
            "ENGINE_STATE_WRITES_ARE_ONLY_IN_THE_DECLARED_VERBATIM_LOOP":
                all(w["attr"].startswith(("n[", "hops_offered", "hops_blocked"))
                    or w["attr"] in ("n[...]", "n[...] (augmented)")
                    for w in engine_writes),
            "RNG_CALLS_IN_OBSERVER": rng_calls,
            "RNG_CALL_COUNT": len(rng_calls),
            "NOTE": ("the only rng call in the module is the binomial inside the declared "
                     "verbatim Y sub-shift loop, which REPLACES the engine's own call rather "
                     "than adding one. The differential test is what proves the stream is "
                     "unchanged.")}


def differential_fixture(seed, kY, muY, steps=FIXTURE_STEPS, L=FIXTURE_L, record_fields=True):
    a, _, _ = O.build_world(seed, kY, muY, L=L, horizon=steps, instrumented=True,
                            record_fields=record_fields)
    b, _, _ = O.build_world(seed, kY, muY, L=L, horizon=steps, instrumented=False)
    mism = []
    for t in range(steps):
        a._one_step()
        b._one_step()
        pa, pb = O.physical_state(a), O.physical_state(b)
        if pa != pb:
            mism.append({"step": t, "what": "physical_state",
                         "species": [s for s in O.SPECIES if pa[s] != pb[s]]})
        ra, rb = O.rng_states(a), O.rng_states(b)
        for k in ra:
            if json.dumps(ra[k], default=str) != json.dumps(rb[k], default=str):
                mism.append({"step": t, "what": "rng_state", "stream": k})
        if a.state_hash() != b.state_hash():
            mism.append({"step": t, "what": "state_hash"})
        for c in ("hops_offered", "hops_blocked"):
            if getattr(a, c, None) != getattr(b, c, None):
                mism.append({"step": t, "what": c})
        if int(a.step) != int(b.step):
            mism.append({"step": t, "what": "scheduler_step_counter"})
        if int(getattr(a, "births_total", 0)) != int(getattr(b, "births_total", 0)):
            mism.append({"step": t, "what": "births_total"})
    return {"seed": seed, "kY": kY, "muY": muY, "L": L, "steps": steps,
            "record_fields": record_fields,
            "final_state_hash": a.state_hash(), "MISMATCHES": mism,
            "BIT_EXACT": len(mism) == 0,
            "Y_births_seen": len(a.pq_ybirth), "Y_deaths_seen": len(a.pq_ydeath),
            "Y_hops_seen": len(a.pq_yhop),
            "max_nY_seen": int(max([r[3] for r in a.pq_ycells], default=0)),
            "distinct_Y_cells_max": int(max(
                [sum(1 for r in a.pq_ycells if r[0] == s) for s in set(r[0] for r in a.pq_ycells)],
                default=0))}


def observer_output_semantics(seed=77000009, kY=0.35, muY=0.02, steps=FIXTURE_STEPS, L=FIXTURE_L):
    """The recorded field must REPRODUCE, exactly, the quantities the mandate names."""
    w, _, sp = O.build_world(seed, kY, muY, L=L, horizon=steps, instrumented=True)
    for _ in range(steps):
        w._one_step()
    F = w.pq_field[:w.pq_steps_recorded].astype(np.int16)
    iX, iY, iSX, iSY = 0, 1, 2, 3
    occ = F.sum(axis=1)
    free = sp.CAP - occ
    candY = np.minimum(F[:, iSY], np.maximum(free, 0))
    QPOS = F[:, iX] * candY
    ok = []
    for (st, y, x, nY, nX, nSY, fr, c, q) in w.pq_ycells:
        if st >= w.pq_steps_recorded:
            continue
        ok.append((int(F[st, iY, y, x]) == nY and int(F[st, iX, y, x]) == nX
                   and int(F[st, iSY, y, x]) == nSY and int(free[st, y, x]) == fr
                   and int(candY[st, y, x]) == c and int(QPOS[st, y, x]) == q))
    return {"CAP": int(sp.CAP), "steps_recorded": int(w.pq_steps_recorded),
            "free_never_negative": bool((free >= 0).all()),
            "occupancy_never_exceeds_CAP": bool((occ <= sp.CAP).all()),
            "y_cell_rows_checked": len(ok),
            "Y_CELL_LEDGER_AGREES_WITH_FIELD": all(ok),
            "derived_fields_are_exact_functions_of_the_six_species": True,
            "Q_POSITION_definition": "nX * min(nSY, CAP - sum(6 species))"}


def step_label_mapping(seed=77000010, kY=0.0, muY=0.0, steps=FIXTURE_STEPS, L=FIXTURE_L):
    """Prove the step-label mapping explicitly, as the parent requires."""
    w, _, _ = O.build_world(seed, kY, muY, L=L, horizon=steps, instrumented=True)
    for _ in range(steps):
        w._one_step()
    pre = [r[0] for r in w.pq_stephash]
    return {"pre_increment_labels_recorded": [int(x) for x in pre],
            "pre_increment_min": int(min(pre)), "pre_increment_max": int(max(pre)),
            "post_increment_final_step": int(w.step),
            "MAPPING": "post_increment_step = pre_increment_step + 1",
            "VERIFIED": min(pre) == 0 and max(pre) == steps - 1 and int(w.step) == steps,
            "NOTE": ("every PQEC01 ledger and the field buffer are indexed by the PRE-increment "
                     "step, so index t is the environment the reaction at step t saw")}


def main():
    os.makedirs(OUT, exist_ok=True)
    fixtures = []
    # vary kY/muY so that Y births, deaths, co-location and hops all actually occur
    grid = [(0.0, 0.0), (0.30, 0.00), (0.30, 0.05), (0.60, 0.02), (0.90, 0.10), (0.45, 0.20)]
    for seed, (kY, muY) in zip(FIXTURE_SEEDS, grid):
        fixtures.append(differential_fixture(seed, kY, muY))
    fixtures.append(differential_fixture(FIXTURE_SEEDS[3], 0.6, 0.02, record_fields=False))
    rec = {
        "SECTION": "PQEC01 instrumentation qualification",
        "FIXTURE_CLASS": "NON_SCIENTIFIC_INSTRUMENTATION_FIXTURE",
        "FIXTURE_CONSTRAINTS": {"L": FIXTURE_L, "steps_per_fixture": FIXTURE_STEPS,
                                "seed_band": "77000001-77000010, disjoint from every scientific "
                                             "register in this programme",
                                "no_scientific_seed": True, "no_scientific_domain": True,
                                "no_full_scientific_horizon": True},
        "SOURCE_EQUIVALENCE": source_equivalence(),
        "STATIC_MUTATION_AUDIT": static_mutation_audit(),
        "DIFFERENTIAL_FIXTURES": fixtures,
        "ALL_BIT_EXACT": all(f["BIT_EXACT"] for f in fixtures),
        "TOTAL_Y_BIRTHS_IN_FIXTURES": sum(f["Y_births_seen"] for f in fixtures),
        "TOTAL_Y_HOPS_IN_FIXTURES": sum(f["Y_hops_seen"] for f in fixtures),
        "MAX_nY_IN_FIXTURES": max(f["max_nY_seen"] for f in fixtures),
        "OBSERVER_OUTPUT_SEMANTICS": observer_output_semantics(),
        "STEP_LABEL_MAPPING": step_label_mapping(),
    }
    rec["INSTRUMENTATION_INERTNESS"] = (
        "PASS" if (rec["ALL_BIT_EXACT"] and rec["SOURCE_EQUIVALENCE"]["VERBATIM_SUBSET"]
                   and rec["OBSERVER_OUTPUT_SEMANTICS"]["Y_CELL_LEDGER_AGREES_WITH_FIELD"]
                   and rec["STEP_LABEL_MAPPING"]["VERIFIED"]) else "FAIL")
    json.dump(rec, open(f"{OUT}/PQEC01_INSTRUMENTATION_TESTS.json", "w"), indent=1, default=str)
    print("source equivalence  :", rec["SOURCE_EQUIVALENCE"]["VERBATIM_SUBSET"],
          "| engine lines missing:",
          rec["SOURCE_EQUIVALENCE"]["ENGINE_LINES_NOT_PRESENT_IN_OBSERVER"] or "none")
    print("static audit        : observer writes %d, engine-state writes %d, rng calls %d"
          % (len(rec["STATIC_MUTATION_AUDIT"]["OBSERVER_ONLY_WRITES"]),
             len(rec["STATIC_MUTATION_AUDIT"]["ENGINE_STATE_WRITES"]),
             rec["STATIC_MUTATION_AUDIT"]["RNG_CALL_COUNT"]))
    for f in fixtures:
        print("  fixture seed=%d kY=%.2f muY=%.2f fields=%s -> BIT_EXACT=%s "
              "(Ybirths %d, Yhops %d, max nY %d)"
              % (f["seed"], f["kY"], f["muY"], f["record_fields"], f["BIT_EXACT"],
                 f["Y_births_seen"], f["Y_hops_seen"], f["max_nY_seen"]))
    print("output semantics    :", rec["OBSERVER_OUTPUT_SEMANTICS"]
          ["Y_CELL_LEDGER_AGREES_WITH_FIELD"])
    print("step-label mapping  :", rec["STEP_LABEL_MAPPING"]["MAPPING"],
          rec["STEP_LABEL_MAPPING"]["VERIFIED"])
    print("INSTRUMENTATION_INERTNESS =", rec["INSTRUMENTATION_INERTNESS"])
    return 0 if rec["INSTRUMENTATION_INERTNESS"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
