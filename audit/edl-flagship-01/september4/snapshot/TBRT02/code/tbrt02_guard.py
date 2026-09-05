"""TBRT02 — the pre-C2 scientific-scale execution guard.

OMLDCT01 died because four full-scale trajectories preceded its master freeze. Nothing in the code
stopped them; attention was supposed to, and did not. This replaces attention. It reads git, not the
working tree, so an uncommitted freeze cannot open the gate and a freeze edited after C2 closes it.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_hashes as H          # noqa: E402

C2_TOKEN = "TBRT02_C2_MASTER_FREEZE_COMMITTED"
FREEZE_PATH = "TBRT02/out/TBRT02_MASTER_FREEZE.json"
SEED_MANIFEST = "TBRT02/out/TBRT02_SEED_MANIFEST.json"
NEED = 250
MAX_FIXTURE_L = 5
SCALE_RULE = ("a construction is SCIENTIFIC-SCALE when L > 5, or horizon >= NEED = 250, or the seed "
              "appears in the TBRT02 seed manifest. The three are OR-ed: any one makes the "
              "construction capable of producing a candidate admissible triple, or spends a frozen "
              "seed, and both are forbidden before a committed C2.")


class PreC2ScientificScaleRefused(RuntimeError):
    pass


def _git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)


def manifest_seeds():
    p = os.path.join(REPO, SEED_MANIFEST)
    if not os.path.exists(p):
        return set()
    d = json.load(open(p))
    return ({s["seed"] for s in d.get("BASE_SEEDS", [])}
            | {s["seed"] for s in d.get("RESERVE_SEEDS", [])})


def c2_state():
    r = _git("log", "--format=%H%x1f%B%x1e", "HEAD")
    if r.returncode != 0:
        return {"C2_COMMITTED": False, "reason": "git log failed"}
    commit = None
    for rec in r.stdout.split("\x1e"):
        if not rec.strip():
            continue
        h, _, body = rec.strip().partition("\x1f")
        if C2_TOKEN in body:
            commit = h.strip()
            break
    if not commit:
        return {"C2_COMMITTED": False, "reason": f"no commit on HEAD carries {C2_TOKEN}"}
    blob = _git("show", f"{commit}:{FREEZE_PATH}")
    if blob.returncode != 0:
        return {"C2_COMMITTED": False, "C2_COMMIT": commit,
                "reason": f"the token commit does not contain {FREEZE_PATH}"}
    committed = blob.stdout
    lp = os.path.join(REPO, FREEZE_PATH)
    live = open(lp).read() if os.path.exists(lp) else None
    same = (live is not None
            and H.canonical_digest(json.loads(live)) == H.canonical_digest(json.loads(committed)))
    return {"C2_COMMITTED": True, "C2_COMMIT": commit,
            "FREEZE_MATCHES_THE_COMMITTED_ONE": bool(same),
            "committed_freeze_sha256": hashlib.sha256(committed.encode()).hexdigest()}


def is_scientific_scale(L, horizon, seed):
    return bool((L is not None and L > MAX_FIXTURE_L) or horizon >= NEED
                or (seed is not None and seed in manifest_seeds()))


def assert_allowed(L, horizon, seed, what=""):
    if not is_scientific_scale(L, horizon, seed):
        return {"ALLOWED": True, "SCIENTIFIC_SCALE": False}
    st = c2_state()
    if not st["C2_COMMITTED"]:
        raise PreC2ScientificScaleRefused(
            f"REFUSED: {what} is scientific-scale (L={L}, horizon={horizon}) and no committed C2 "
            f"exists. {st.get('reason')}. {SCALE_RULE}")
    if not st.get("FREEZE_MATCHES_THE_COMMITTED_ONE"):
        raise PreC2ScientificScaleRefused(
            f"REFUSED: {what} is scientific-scale and the working-tree freeze does not match the "
            f"one committed at {st['C2_COMMIT']}.")
    return {"ALLOWED": True, "SCIENTIFIC_SCALE": True, "C2_COMMIT": st["C2_COMMIT"]}


if __name__ == "__main__":
    print(json.dumps(c2_state(), indent=1))
    print("manifest seeds:", len(manifest_seeds()))
    try:
        assert_allowed(L=36, horizon=11000, seed=None, what="self-test")
        print("GATE: OPEN")
    except PreC2ScientificScaleRefused as e:
        print("GATE: CLOSED —", str(e)[:120])
