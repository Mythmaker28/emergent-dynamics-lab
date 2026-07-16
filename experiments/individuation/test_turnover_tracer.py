"""LCI-CAUSAL-TURNOVER-PREREG-03 — tracker / material-tracer / periodicity tests (DEV).

Falsifiable checks that the per-target passive material tracer is strictly observational, the bijective tracker is
one-to-one, and M_i has no feed-cohort periodicity artefact. Run:
    PYTHONPATH=. python experiments/individuation/test_turnover_tracer.py
"""
import importlib.util, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cc = _load("cc", "causal_confirm.py"); nm = _load("nm", "nonmerging_confirm.py")
bt = _load("bt", "bijective_tracker.py"); mt = _load("mt", "material_tracer.py")
from edlab.substrates.scaffold.observables import detect
from edlab.experiments.sc_mcm import config as C
K = cc.K; DET = C.DET

FAIL = []
def check(name, ok, extra=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {extra}")
    if not ok: FAIL.append(name)


def _to_snapshot(seed, warm):
    eng = cc.build(cc.MEM_INTACT); st = cc.seed_world(seed)
    for _ in range(warm): st = eng.step(st)
    T = cc.pick(sorted(detect(st, DET), key=lambda e: -e.size))
    return eng, st, [e.centroid for e in T]


def test_no_feedback(seed=50002, steps=850):
    eng, st, cents = _to_snapshot(seed, cc.WARM)
    reg0, _ = cc.region_masks(st, cents)
    a = st.copy(); b, base = mt.seed_tracers(st, reg0)
    worst = 0.0
    for _ in range(steps):
        a = eng.step(a); b = eng.step(b)
        worst = max(worst, max(float(np.abs(getattr(a, f) - getattr(b, f)).max())
                               for f in ["rho", "U", "V", "c", "N", "Mf", "uptake"]))
    check("tracer_strictly_observational_full_horizon", worst == 0.0, f"(max|Δ|={worst})")


def test_feed_collision_guard(seed=50002):
    eng, st, cents = _to_snapshot(seed, cc.WARM)
    reg0, _ = cc.region_masks(st, cents)
    _, base = mt.seed_tracers(st, reg0)
    hi = mt.assert_no_feed_collision(eng.tracer, base, 2000)
    check("feed_index_never_hits_tracer_cohort", hi < base, f"(max feed idx {hi} < base {base})")


def test_determinism(seed=50004, steps=300):
    eng, st, cents = _to_snapshot(seed, cc.WARM)
    reg0, _ = cc.region_masks(st, cents)
    def run():
        s, base = mt.seed_tracers(st, reg0)
        for _ in range(steps): s = eng.step(s)
        return s
    a, b = run(), run()
    worst = max(float(np.abs(getattr(a, f) - getattr(b, f)).max()) for f in ["rho", "Mf", "C"])
    check("two_run_byte_identical", worst == 0.0, f"(max|Δ|={worst})")


def test_M_monotone_no_periodicity(seed=50002, steps=600):
    eng, st, cents = _to_snapshot(seed, cc.WARM)
    reg0, _ = cc.region_masks(st, cents)
    s, base = mt.seed_tracers(st, reg0)
    tr = bt.BijectiveTracker(theta=nm.THETA); tr.seed([m.copy() for m in reg0], 0)
    Ms = {i: [] for i in range(K)}
    for t in range(1, steps + 1):
        s = eng.step(s); emasks = [cc.mask(e) for e in detect(s, DET)]; tr.update(emasks, t)
        if any(tr.tracks[i].status != bt.ALIVE for i in range(K)): break
        if t % 10 == 0:
            regs = [tr.tracks[i].mask for i in range(K)]
            mat = mt.read_material(s, base, regs)
            for i in range(K): Ms[i].append(mat[i]["M"])
    # feed cycle = n_temporal * tau_feed; per-target tracers must not oscillate with it
    up_jumps = max(int(np.sum(np.diff(np.array(v)) > 0.02)) for v in Ms.values() if len(v) > 1)
    decreasing = all(v[-1] < v[0] for v in Ms.values() if len(v) > 1)
    check("M_i_monotone_decreasing_no_feed_periodicity", up_jumps <= 1 and decreasing,
          f"(max up-jumps>0.02 = {up_jumps}; all decreasing = {decreasing})")


def test_bijective_one_to_one(seed=50001, steps=200):
    """Two tracks may never own the same component; a genuine fission must be censored SPLIT, not silently followed."""
    eng, st, cents = _to_snapshot(seed, cc.WARM)
    reg0, _ = cc.region_masks(st, cents)
    s, base = mt.seed_tracers(st, reg0)
    tr = bt.BijectiveTracker(theta=nm.THETA); tr.seed([m.copy() for m in reg0], 0)
    ever_shared = False; censored = set()
    for t in range(1, steps + 1):
        s = eng.step(s); comps = [cc.mask(e) for e in detect(s, DET)]
        ev = tr.update(comps, t)
        alive = [tr.tracks[i] for i in range(K) if tr.tracks[i].status == bt.ALIVE]
        # no component owned by >1 alive track
        for ci, cm in enumerate(comps):
            owners = sum(1 for tk in alive if int((tk.mask & cm).sum()) == int(tk.mask.sum()) and tk.mask.sum() > 0)
            if owners > 1: ever_shared = True
        censored |= set(ev)
    check("bijective_never_shared_component", not ever_shared)
    check("seed50001_fission_is_censored_not_followed", len(censored) > 0, f"(events on tracks {sorted(censored)})")


if __name__ == "__main__":
    print("=== turnover tracer / tracker / periodicity tests ===")
    test_no_feedback(); test_feed_collision_guard(); test_determinism()
    test_M_monotone_no_periodicity(); test_bijective_one_to_one()
    print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + ', '.join(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
