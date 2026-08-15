"""PMCR01 Gate 0 — the mandatory mutation oracles.

Every alleged channel is proved, not asserted, on a NON_SCIENTIFIC_SEMANTIC_FIXTURE:

    L = 3            a nine-cell torus; it cannot carry the qualified geometry
    seed >= 9e6      disjoint from every delivered seed register
    <= 8 steps       eight steps is not a trajectory
    hand-set state   seed_one_organiser is never called; SX/SY are not filled to S0

The oracles are DETERMINISTIC by construction, so no statistics are needed and no result rests
on a sample. Two independent witnesses are used for each channel:

  WITNESS 1 (hazard)  the world's generator is wrapped so that every (n, p) pair the scheduler
                      passes to `binomial` is captured AT THE POINT OF USE. Proving that the
                      p of the Y-birth call changes, and that no other captured argument does,
                      proves the manifest -> constructor -> scheduler link without inference.
  WITNESS 2 (delta)   the parameter is driven to a value that makes the event deterministic
                      (p = 1 or p = 0), so the resulting Y state delta is an identity, not a draw.

Then: X-side isolation, and exact reversal.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, "/home/claude/PMCR01/code")
import pmcr01_sentinel as SENT                            # noqa: E402

REPO = "/home/claude/edl"
OUT = "/home/claude/PMCR01/out"
EXEC_FILES = {
    "ORR01/code/kinetics.py": "/home/claude/ORR01/code/kinetics.py",
    "ORR01/code/lawspec_v2.py": "/home/claude/ORR01/code/lawspec_v2.py",
    "OBTC02/code/engine_obtc.py": "/home/claude/OBTC02/code/engine_obtc.py",
    "OBTC02/code/protocol_obtc02.py": "/home/claude/OBTC02/code/protocol_obtc02.py",
    "OBTC02/code/obtc02_protocol.yaml": "/home/claude/OBTC02/code/obtc02_protocol.yaml",
}
FIXTURE_SEED = 9_000_017
L_FIX = 3


# ------------------------------------------------------------------ committed-blob equivalence
def verify_on_disk_equals_committed():
    got = {}
    for repo_path, disk_path in EXEC_FILES.items():
        a = subprocess.run(("git", "rev-parse", "HEAD:%s" % repo_path), cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
        b = subprocess.run(("git", "hash-object", disk_path), cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
        got[repo_path] = {"blob_at_head": a, "blob_of_the_file_i_import": b, "IDENTICAL": a == b}
    return got


# ------------------------------------------------------------------ recording generator
class RecordingRNG:
    """Transparent wrapper. Records the arguments every operator passes, in call order."""

    def __init__(self, inner):
        self._inner = inner
        self.calls = []

    def binomial(self, n, p, size=None):
        self.calls.append({"fn": "binomial",
                           "n": np.asarray(n).astype(np.int64).tolist(),
                           "p": np.round(np.asarray(p, dtype=float), 15).tolist()})
        return self._inner.binomial(n, p) if size is None else self._inner.binomial(n, p, size)

    def hypergeometric(self, ng, nb, ns, size=None):
        self.calls.append({"fn": "hypergeometric"})
        return (self._inner.hypergeometric(ng, nb, ns) if size is None
                else self._inner.hypergeometric(ng, nb, ns, size))

    def random(self, *a, **k):
        self.calls.append({"fn": "random"})
        return self._inner.random(*a, **k)

    def __getattr__(self, k):
        return getattr(self._inner, k)


class ForcingRNG:
    """A DETERMINISTIC semantic generator: every Bernoulli trial succeeds when p > 0 and fails
    when p == 0. It is not a model of anything; it exists so that a state delta can be proved
    as an identity instead of estimated from a sample. Used only inside a fixture."""

    def __init__(self, inner):
        self._inner = inner
        self.calls = []

    def binomial(self, n, p, size=None):
        self.calls.append({"fn": "binomial",
                           "n": np.asarray(n).astype(np.int64).tolist(),
                           "p": np.round(np.asarray(p, dtype=float), 15).tolist()})
        n_a = np.asarray(n)
        p_a = np.asarray(p, dtype=float)
        return np.where(p_a > 0, n_a, 0).astype(np.int64)

    def hypergeometric(self, ng, nb, ns, size=None):
        self.calls.append({"fn": "hypergeometric"})
        return np.asarray(ns).astype(np.int64)

    def random(self, *a, **k):
        self.calls.append({"fn": "random"})
        return self._inner.random(*a, **k)

    def __getattr__(self, k):
        return getattr(self._inner, k)


# ------------------------------------------------------------------ the fixture
def build_fixture(EN, V2, over, cell=(1, 1), q=3, s=4, sx=2, record=True, force=False):
    """NON_SCIENTIFIC_SEMANTIC_FIXTURE: one hand-set cell on a nine-cell torus."""
    base = {"L": L_FIX, "CAP": 16, "S0": 3, "phi": 0.0, "omega": 0.0,
            "muX": 0.004, "muY": 0.0, "kX": 1.0, "kY": 0.0,
            "p_hop_X": 0.0, "p_hop_Y": 0.0}
    base.update(over)
    sp = V2.spec_with(**base)
    w = EN.WorldOBTC(L=L_FIX, seed=FIXTURE_SEED, sp=sp,
                     lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                     exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir")
    y, x = cell
    w.n["X"][y, x] = q
    w.n["Y"][y, x] = 1
    w.n["SY"][y, x] = s
    w.n["SX"][y, x] = sx
    if force:
        w.rng = ForcingRNG(w.rng)
        w.rng_feed = ForcingRNG(w.rng_feed)
    elif record:
        w.rng = RecordingRNG(w.rng)
        w.rng_feed = RecordingRNG(w.rng_feed)
    return w, sp


def snapshot(w):
    return {k: w.n[k].copy() for k in ("X", "Y", "SX", "SY", "WX", "WY")}


def delta(a, b):
    return {k: int(b[k].sum() - a[k].sum()) for k in a}


def state_sha(w):
    h = hashlib.sha256()
    for k in ("X", "Y", "SX", "SY", "WX", "WY"):
        h.update(k.encode())
        h.update(np.ascontiguousarray(w.n[k]).tobytes())
    return h.hexdigest()


def one_step_record(EN, V2, over, **kw):
    with SENT.fixture("mutation-oracle"):
        w, sp = build_fixture(EN, V2, over, **kw)
        before = snapshot(w)
        w._one_step()
        after = snapshot(w)
        return {"spec": {k: getattr(sp, k) for k in
                         ("kX", "kY", "muX", "muY", "phi", "S0", "CAP",
                          "p_hop_X", "p_hop_Y")},
                "delta": delta(before, after),
                "calls_main": w.rng.calls, "calls_feed": w.rng_feed.calls,
                "state_sha256": state_sha(w)}


# ------------------------------------------------------------------ oracles
def y_config(w):
    return np.ascontiguousarray(w.n["Y"]).tobytes()


CFG_SEEDS = tuple(9_000_100 + i for i in range(12))


def one_step_config(EN, V2, over):
    """The SET of Y configurations one step reaches, over twelve fixture seeds.

    Forcing every Bernoulli to succeed is useless for transport: _diffuse makes four sequential
    passes in the order (+1,0), (-1,0), (+1,1), (-1,1), so forcing all four returns the walker
    to its starting cell and hides the very effect under test. The honest statement is a
    UNIVERSAL on one side and an EXISTENTIAL on the other: with p_hop_Y = 0 the Y grid is
    invariant for EVERY seed, and with p_hop_Y > 0 at least one seed moves it."""
    grids, tot = [], set()
    for sd in CFG_SEEDS:
        with SENT.fixture("mutation-oracle-config"):
            global FIXTURE_SEED
            keep = FIXTURE_SEED
            FIXTURE_SEED = sd
            try:
                w, sp = build_fixture(EN, V2, over, record=False)
                w._one_step()
            finally:
                FIXTURE_SEED = keep
            g = w.n["Y"].tolist()
            if g not in grids:
                grids.append(g)
            tot.add(int(w.n["Y"].sum()))
    return {"Y_grid": grids, "n_distinct_configurations": len(grids),
            "Y_total": sorted(tot), "seeds": list(CFG_SEEDS),
            "INVARIANT_ACROSS_ALL_SEEDS": len(grids) == 1}


def two_step_x_hazard(EN, V2, over):
    """Does the perturbation reach the X branch in the NEXT step? p_X = min(1, kX*nX*nY), so a
    change in nY is a change in the X hazard one step later. This is the honest test of
    'can be varied without changing the X baseline'."""
    with SENT.fixture("mutation-oracle-2step"):
        w, sp = build_fixture(EN, V2, over)
        w._one_step()
        n1 = len(w.rng.calls)
        w._one_step()
        step2 = w.rng.calls[n1:]
        xb = [c for c in step2 if c["fn"] == "binomial"]
        return {"step2_binomial_arguments": xb, "n_calls_step2": len(step2)}


def oracle(EN, V2, name, field, off, on, expect, kind="count"):
    """off -> on -> off. Deterministic by construction."""
    a = one_step_record(EN, V2, {field: off})
    b = one_step_record(EN, V2, {field: on})
    c = one_step_record(EN, V2, {field: off})

    # which captured binomial arguments differ, and at which call index
    changed = []
    for i, (ca, cb) in enumerate(zip(a["calls_main"], b["calls_main"])):
        if ca != cb:
            changed.append({"call_index": i, "off": ca, "on": cb})
    only_after = min([c["call_index"] for c in changed], default=None)
    x_calls_a = a["calls_main"][:only_after] if only_after is not None else a["calls_main"]
    x_calls_b = b["calls_main"][:only_after] if only_after is not None else b["calls_main"]

    ca = one_step_config(EN, V2, {field: off})
    cb = one_step_config(EN, V2, {field: on})
    config_changed = (ca["Y_grid"] != cb["Y_grid"]
                      or ca["n_distinct_configurations"] != cb["n_distinct_configurations"])
    count_conserved = ca["Y_total"] == cb["Y_total"]

    x2a = two_step_x_hazard(EN, V2, {field: off})
    x2b = two_step_x_hazard(EN, V2, {field: on})
    x_next_step_changed = x2a["step2_binomial_arguments"] != x2b["step2_binomial_arguments"]

    if kind == "count":
        effect_ok = (a["delta"]["Y"] != b["delta"]["Y"]) and b["delta"]["Y"] == expect
    else:                                  # transport: the count MUST be conserved
        effect_ok = config_changed and count_conserved and b["delta"]["Y"] == expect

    return {
        "CHANNEL": name, "FIELD": field, "KIND": kind, "value_off": off, "value_on": on,
        "FIXTURE": "NON_SCIENTIFIC_SEMANTIC_FIXTURE",
        "1_HAZARD_CHANGED": bool(changed),
        "hazard_calls_that_changed": changed,
        "n_calls_recorded": len(a["calls_main"]),
        "2_Y_STATE_DELTA_CHANGED": a["delta"]["Y"] != b["delta"]["Y"],
        "Y_delta_off": a["delta"]["Y"], "Y_delta_on": b["delta"]["Y"],
        "expected_Y_delta_on": expect,
        "2_MATCHES_THE_DETERMINISTIC_EXPECTATION": b["delta"]["Y"] == expect,
        "2b_Y_SPATIAL_CONFIGURATION_CHANGED": config_changed,
        "2b_Y_COUNT_CONSERVED_BY_THIS_EVENT": count_conserved,
        "2_EFFECT_PROVED_FOR_THIS_KIND": effect_ok,
        "full_delta_off": a["delta"], "full_delta_on": b["delta"],
        "3_X_SIDE_ARGUMENTS_IDENTICAL_UPSTREAM_IN_THE_SAME_STEP": x_calls_a == x_calls_b,
        "3_X_DELTA_UNCHANGED_IN_THE_SAME_STEP": (a["delta"]["X"] == b["delta"]["X"]
                                                 and a["delta"]["WX"] == b["delta"]["WX"]),
        "3b_X_HAZARD_CHANGED_IN_THE_NEXT_STEP": x_next_step_changed,
        "3b_READING": ("p_X = min(1, kX*nX*nY) reads nY. Any channel that moves Y therefore "
                       "reaches the X branch one step later. Same-step isolation is not "
                       "independence."),
        "4_REVERSAL_EXACT": a["state_sha256"] == c["state_sha256"],
        "state_sha_off": a["state_sha256"], "state_sha_on": b["state_sha256"],
        "state_sha_reverted": c["state_sha256"],
        "PASS": bool(changed and effect_ok and a["state_sha256"] == c["state_sha256"]),
    }


def manifest_end_to_end(PC, V2, EN):
    """The full manifest -> spec_for -> Spec -> scheduler chain, exercised on the real function.
    PC.PT is a plain dict of manifest values; a fixture-scoped copy proves the copy is verbatim
    and that the value reaches the hazard."""
    got = {}
    saved = PC.PT
    try:
        for k, v in (("kY", 0.25), ("muY", 0.5)):
            PC.PT = {**saved, k: v, "L": L_FIX}
            sp = PC.spec_for(L=L_FIX)
            got[k] = {"manifest_value": v, "Spec_attribute": getattr(sp, k),
                      "VERBATIM": getattr(sp, k) == v,
                      "spec_for_reads_it_from_PT": True}
    finally:
        PC.PT = saved
    got["PT_RESTORED"] = PC.PT is saved
    got["p_hop_Y_IS_NOT_A_MANIFEST_FIELD"] = "p_hop_Y" not in saved
    got["p_hop_Y_IS_SET_IN_CODE_AS"] = "0.0 if immobile_organiser else PT['p_hop']"
    got["p_hop_Y_ALIASED_TO_p_hop_X"] = float(PC.spec_for(L=L_FIX).p_hop_Y) == float(
        PC.spec_for(L=L_FIX).p_hop_X)
    return got


def omega_is_inert(EN, V2):
    """Under the qualified LawSpec the v1 feed operator is bypassed; omega should be inert."""
    a = one_step_record(EN, V2, {"omega": 0.0, "phi": 0.2})
    b = one_step_record(EN, V2, {"omega": 0.9, "phi": 0.2})
    return {"CHANNEL": "omega under BALANCED_CHEMOSTAT",
            "state_sha_equal": a["state_sha256"] == b["state_sha256"],
            "hazards_identical": a["calls_main"] == b["calls_main"]
            and a["calls_feed"] == b["calls_feed"],
            "CLASS": "SCHEMA_ONLY_INERT",
            "why": ("_feed_and_outflow returns immediately after _exchange when lawspec is "
                    "LAWSPEC_V2_EXCHANGE, and _exchange never reads sp.omega")}


def y_is_never_exchangeable(V2):
    return {"EXCHANGEABLE_DEFAULT": list(V2.EXCHANGEABLE_DEFAULT),
            "EXCHANGEABLE_WITH_BODY": list(V2.EXCHANGEABLE_WITH_BODY),
            "Y_IN_ANY_DECLARED_POOL": ("Y" in V2.EXCHANGEABLE_DEFAULT
                                       or "Y" in V2.EXCHANGEABLE_WITH_BODY),
            "CONSEQUENCE": ("the chemostat can never remove a Y. The ONLY executable removal "
                            "of Y is the muY decay event and the declared organiser_off "
                            "intervention.")}


def main():
    equiv = verify_on_disk_equals_committed()
    if not all(v["IDENTICAL"] for v in equiv.values()):
        json.dump({"BLOB_EQUIVALENCE": equiv}, open(f"{OUT}/_oracles.json", "w"), indent=1)
        raise SystemExit("the files on disk are not the committed blobs; refusing to proceed")

    sys.path.insert(0, "/home/claude/ORR01/code")
    sys.path.insert(0, "/home/claude/OBTC02/code")
    SENT.install(seed_register_paths=[
        "/home/claude/OBFOR01/out/_freeze.json", "/home/claude/OBFOR01/out/_seeds.json",
        "/home/claude/OBTC02/out/_seeds.json", "/home/claude/OBDI02/out/_seeds.json"])
    import lawspec_v2 as V2
    import engine_obtc as EN
    import protocol_obtc02 as PC
    import guard_obtc as GD

    # q=3, s=4, sx=2, CAP=16 -> occ = 3+1+4+2 = 10, free = 6, cand_Y = min(4,6) = 4
    res = {
        "SECTION": "PMCR01 Gate 0 — mutation oracles",
        "BLOB_EQUIVALENCE": equiv,
        "FIXTURE": {"label": "NON_SCIENTIFIC_SEMANTIC_FIXTURE", "L": L_FIX,
                    "seed": FIXTURE_SEED, "cell": [1, 1],
                    "hand_set": {"X": 3, "Y": 1, "SY": 4, "SX": 2},
                    "derived": {"occupancy": 10, "free": 6, "cand_Y": 4, "cand_X": 2},
                    "steps_per_oracle": 1,
                    "seed_one_organiser_called": False},
        "ORACLES": [
            # kY: p_Y = min(1, kY*nX*nY) = min(1, 3*kY). kY = 1 -> p = 1 -> births = cand = 4
            oracle(EN, V2, "Y birth", "kY", 0.0, 1.0, expect=+4),
            # muY: with kY = 0 there is exactly one Y; muY = 1 kills it deterministically
            oracle(EN, V2, "Y death", "muY", 0.0, 1.0, expect=-1),
            # p_hop_Y: transport. Count is conserved, so the Y DELTA cannot change; the hazard
            # must. This is exactly why the oracle records arguments and not only outcomes.
            oracle(EN, V2, "Y transport", "p_hop_Y", 0.0, 1.0, expect=0, kind="transport"),
        ],
        "MANIFEST_TO_SCHEDULER": manifest_end_to_end(PC, V2, EN),
        "OMEGA": omega_is_inert(EN, V2),
        "Y_EXCHANGEABILITY": y_is_never_exchangeable(V2),
        "SENTINEL": SENT.report(GD),
    }
    json.dump(res, open(f"{OUT}/PMCR01_MUTATION_ORACLE_REPORT.json", "w"), indent=1,
              default=str)

    for o in res["ORACLES"]:
        print("%-12s %-9s %-9s off=%-4s on=%-4s | hazard %-5s | dY %+d->%+d (exp %+d) | "
              "cfg chg %-5s cnt cons %-5s | X same-step iso %-5s | X next-step chg %-5s | "
              "rev %-5s | PASS %s"
              % (o["CHANNEL"], o["FIELD"], o["KIND"], o["value_off"], o["value_on"],
                 o["1_HAZARD_CHANGED"], o["Y_delta_off"], o["Y_delta_on"],
                 o["expected_Y_delta_on"], o["2b_Y_SPATIAL_CONFIGURATION_CHANGED"],
                 o["2b_Y_COUNT_CONSERVED_BY_THIS_EVENT"],
                 o["3_X_SIDE_ARGUMENTS_IDENTICAL_UPSTREAM_IN_THE_SAME_STEP"],
                 o["3b_X_HAZARD_CHANGED_IN_THE_NEXT_STEP"],
                 o["4_REVERSAL_EXACT"], o["PASS"]))
    print("\nmanifest -> Spec verbatim: %s"
          % {k: v.get("VERBATIM") for k, v in res["MANIFEST_TO_SCHEDULER"].items()
             if isinstance(v, dict)})
    print("p_hop_Y is a manifest field: %s ; aliased to p_hop_X: %s"
          % (not res["MANIFEST_TO_SCHEDULER"]["p_hop_Y_IS_NOT_A_MANIFEST_FIELD"],
             res["MANIFEST_TO_SCHEDULER"]["p_hop_Y_ALIASED_TO_p_hop_X"]))
    print("omega inert under the qualified LawSpec: %s"
          % res["OMEGA"]["state_sha_equal"])
    print("Y in any exchangeable pool: %s" % res["Y_EXCHANGEABILITY"]["Y_IN_ANY_DECLARED_POOL"])
    s = res["SENTINEL"]
    print("\nSENTINEL  construct=%d advance=%d scientific_starts=%d scientific_seeds=%d "
          "| fixtures=%d fixture_steps=%d | ALL_FOUR_ZERO=%s"
          % (s["ENGINE_CONSTRUCT_CALLS"], s["ENGINE_ADVANCE_CALLS"],
             s["SCIENTIFIC_WORLD_STARTS"], s["SCIENTIFIC_SEEDS_OPENED"],
             s["FIXTURE_CONSTRUCTIONS"], s["FIXTURE_STEPS"], s["ALL_FOUR_ZERO"]))
    print("guard_obtc independent witness: %s" % s.get("INDEPENDENT_WITNESS_guard_obtc"))


if __name__ == "__main__":
    main()
