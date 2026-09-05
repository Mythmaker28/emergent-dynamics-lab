"""OMLDCT02 — the pre-C2 scientific-scale execution guard.

OMLDCT01 died because four full-scale trajectories on frozen candidate seeds preceded its master
freeze. Nothing in the code stopped them; only my own attention was supposed to, and it did not.
This file is the mechanism that replaces attention.

Every construction that could produce a candidate admissible pair must pass through
`assert_allowed()`. Before a COMMITTED C2 exists, it raises. The check reads git, not the working
tree, so an uncommitted freeze file cannot open the gate, and a freeze edited after C2 closes it
again.
"""
from __future__ import annotations
import json, os, subprocess, sys

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H

C2_TOKEN = "OMLDCT02_C2_MASTER_FREEZE_COMMITTED"
FREEZE_PATH = "OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json"
SEED_MANIFEST = "OMLDCT02/out/OMLDCT02_SEED_MANIFEST.json"
NEED = 250                 # frozen maturation requirement
MAX_FIXTURE_L = 5          # section 7 allows deterministic worlds at L <= 5
MAX_FIXTURE_HORIZON = NEED - 1

SCALE_RULE = ("a construction is SCIENTIFIC-SCALE when L > 5, or horizon >= NEED = 250, or the seed "
              "appears in the OMLDCT02 seed manifest. The three conditions are OR-ed: any one of "
              "them makes the construction capable of producing a candidate admissible pair, or "
              "spends a frozen seed, and section 7 forbids both before a committed C2.")

class PreC2ScientificScaleRefused(RuntimeError):
    pass

def _git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)

def _manifest_seeds():
    p = os.path.join(REPO, SEED_MANIFEST)
    if not os.path.exists(p): return set()
    d = json.load(open(p))
    return {s["seed"] for s in d.get("BASE_SEEDS", [])} | {s["seed"] for s in d.get("RESERVE_SEEDS", [])}

def c2_state():
    """Returns a dict describing whether a committed C2 exists and whether the freeze still matches
    it. Reads git history, never the working tree alone."""
    r = _git("log", "--format=%H%x1f%B%x1e", "HEAD")
    if r.returncode != 0:
        return {"C2_COMMITTED": False, "reason": "git log failed: " + r.stderr.strip()[:200]}
    commit = None
    for rec in r.stdout.split("\x1e"):
        if not rec.strip(): continue
        h, _, body = rec.strip().partition("\x1f")
        if C2_TOKEN in body: commit = h.strip(); break
    if not commit:
        return {"C2_COMMITTED": False, "reason": f"no commit on HEAD carries the token {C2_TOKEN}"}
    blob = _git("show", f"{commit}:{FREEZE_PATH}")
    if blob.returncode != 0:
        return {"C2_COMMITTED": False, "C2_COMMIT": commit,
                "reason": f"the token commit does not contain {FREEZE_PATH}"}
    try:
        committed = json.loads(blob.stdout)
    except Exception as e:
        return {"C2_COMMITTED": False, "C2_COMMIT": commit, "reason": f"committed freeze unreadable: {e}"}
    wt = os.path.join(REPO, FREEZE_PATH)
    live_ok, live_hash = None, None
    if os.path.exists(wt):
        live = json.load(open(wt)); live_hash = H.content_digest(live)
        live_ok = live_hash == H.content_digest(committed)
    return {"C2_COMMITTED": True, "C2_COMMIT": commit,
            "COMMITTED_FREEZE_CONTENT_HASH": H.content_digest(committed),
            "WORKING_TREE_FREEZE_CONTENT_HASH": live_hash,
            "WORKING_TREE_MATCHES_COMMITTED_FREEZE": live_ok,
            "reason": "ok" if live_ok else "the working-tree freeze differs from the committed one"}

def is_scientific_scale(L=None, horizon=None, seed=None):
    reasons = []
    if L is not None and L > MAX_FIXTURE_L: reasons.append(f"L = {L} exceeds the fixture limit {MAX_FIXTURE_L}")
    if horizon is not None and horizon >= NEED: reasons.append(f"horizon = {horizon} reaches NEED = {NEED}")
    if seed is not None and seed in _manifest_seeds(): reasons.append(f"seed {seed} is in the OMLDCT02 seed manifest")
    return (len(reasons) > 0), reasons

def assert_allowed(L=None, horizon=None, seed=None, what="construction"):
    """The gate. Call before ANY world construction. Returns a record; raises when refused."""
    sci, why = is_scientific_scale(L, horizon, seed)
    if not sci:
        return {"ALLOWED": True, "SCIENTIFIC_SCALE": False, "what": what, "L": L,
                "horizon": horizon, "gate": "not scientific-scale — no C2 required"}
    st = c2_state()
    if st["C2_COMMITTED"] and st.get("WORKING_TREE_MATCHES_COMMITTED_FREEZE") is not False:
        return {"ALLOWED": True, "SCIENTIFIC_SCALE": True, "what": what, "L": L,
                "horizon": horizon, "gate": "committed C2 present", "C2_COMMIT": st["C2_COMMIT"]}
    raise PreC2ScientificScaleRefused(
        f"REFUSED: {what} is scientific-scale ({'; '.join(why)}) and no valid committed C2 exists "
        f"({st.get('reason')}). Section 7 forbids this, and section 9 makes it "
        f"OMLDCT02_TECHNICALLY_INVALID.")

# --------------------------------------------------------------------------- fixtures for the guard
def self_test():
    """The guard itself is covered. Cases run against the REAL repository state, so the expectations
    are written as a function of whether a committed C2 exists right now."""
    st = c2_state(); have = bool(st["C2_COMMITTED"]) and st.get("WORKING_TREE_MATCHES_COMMITTED_FREEZE") is not False
    seeds = sorted(_manifest_seeds()); a_seed = seeds[0] if seeds else None
    rows = []
    def case(name, kw, expect_scale, expect_allowed):
        sci, why = is_scientific_scale(**kw)
        try:
            assert_allowed(**kw, what=name); allowed, err = True, None
        except PreC2ScientificScaleRefused as e:
            allowed, err = False, str(e)[:160]
        ok = (sci == expect_scale) and (allowed == expect_allowed)
        rows.append({"case": name, "kwargs": {k: v for k, v in kw.items()},
                     "scientific_scale": sci, "expected_scale": expect_scale,
                     "allowed": allowed, "expected_allowed": expect_allowed,
                     "why": why, "error": err, "PASS": ok})
    case("synthetic fixture, L=4 horizon=100", {"L": 4, "horizon": 100}, False, True)
    case("fixture at the L limit, L=5 horizon=249", {"L": 5, "horizon": 249}, False, True)
    case("one step over the L limit, L=6", {"L": 6, "horizon": 100}, True, have)
    case("one step over the horizon limit, horizon=250", {"L": 4, "horizon": 250}, True, have)
    case("full scale, L=36 horizon=11000", {"L": 36, "horizon": 11000}, True, have)
    case("full horizon at fixture L", {"L": 5, "horizon": 11000}, True, have)
    if a_seed is not None:
        case("a frozen manifest seed at fixture scale", {"L": 4, "horizon": 10, "seed": a_seed}, True, have)
        case("a non-manifest seed at fixture scale", {"L": 4, "horizon": 10, "seed": 1}, False, True)
    case("no arguments at all", {}, False, True)
    return rows, all(r["PASS"] for r in rows), st

if __name__ == "__main__":
    rows, ok, st = self_test()
    for r in rows: print(("PASS " if r["PASS"] else "FAIL ") + r["case"])
    print("C2_COMMITTED =", st["C2_COMMITTED"], "|", st.get("reason"))
    print("GUARD_SELF_TEST =", "PASS" if ok else "FAIL")
