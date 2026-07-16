"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 3 tests for the bijective periodic tracker (DEV).

Seven scenarios required by the mission: periodic translation, periodic wrapping, crossing without fusion,
synthetic merge, synthetic split, loss, ambiguity. Masks are supplied directly (full-grid periodic booleans),
so the tests exercise the ASSIGNMENT / CENSORSHIP logic (not the detector). Run: python .../test_bijective_tracker.py
"""
import numpy as np
from importlib import util as _u
_s = _u.spec_from_file_location("bt", "experiments/individuation/bijective_tracker.py")
bt = _u.module_from_spec(_s); _s.loader.exec_module(bt)
ALIVE, LOST, MERGED, SPLIT, AMBIGUOUS = bt.ALIVE, bt.LOST, bt.MERGED, bt.SPLIT, bt.AMBIGUOUS
N = 32

def disk(cy, cx, r):
    ys, xs = np.mgrid[0:N, 0:N]
    dy = np.minimum(np.abs(ys - cy), N - np.abs(ys - cy)); dx = np.minimum(np.abs(xs - cx), N - np.abs(xs - cx))
    return (dy * dy + dx * dx) <= r * r

def block(r0, r1, c0, c1):
    m = np.zeros((N, N), bool); m[r0:r1, c0:c1] = True; return m

results = []
def check(name, cond, detail=""):
    results.append((name, cond, detail)); print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

# 1) PERIODIC TRANSLATION: one blob moves right, wraps around; must stay ALIVE, never censored.
t = bt.BijectiveTracker(); t.seed([disk(16, 4, 4)], 0)
for k in range(1, 25):
    t.update([disk(16, (4 + 2 * k) % N, 4)], k)
check("periodic_translation_stays_alive", t.summary()["alive"] == 1 and t.tracks[0].status == ALIVE, t.summary().__str__())

# 2) PERIODIC WRAPPING: a blob straddling the boundary (one periodic mask) must remain ONE ALIVE track (not SPLIT).
t = bt.BijectiveTracker(); t.seed([disk(16, 0, 4)], 0)   # centred on the seam -> wraps both edges
for k in range(1, 8):
    t.update([disk(16, 0, 4)], k)
check("periodic_wrap_not_split", t.tracks[0].status == ALIVE, t.tracks[0].status)

# 3) CROSSING WITHOUT FUSION: two blobs cross in x on different rows, never one component; both ALIVE, no swap.
t = bt.BijectiveTracker(); seeds = t.seed([disk(13, 6, 2), disk(19, 26, 2)], 0)
idA, idB = seeds[0].id, seeds[1].id
for k in range(1, 15):
    ax = (6 + 1.5 * k); bx = (26 - 1.5 * k)
    t.update([disk(13, int(ax) % N, 2), disk(19, int(bx) % N, 2)], k)
alive_ids = {tr.id for tr in t.tracks if tr.status == ALIVE}
check("crossing_no_fusion_both_alive", alive_ids == {idA, idB}, f"alive={alive_ids}")

# 4) SYNTHETIC MERGE: two blobs approach and become ONE mask; BOTH tracks censored MERGED at that frame.
t = bt.BijectiveTracker(); s = t.seed([disk(16, 12, 3), disk(16, 20, 3)], 0)
t.update([disk(16, 13, 3), disk(16, 19, 3)], 1)                 # still two, closer
ev = t.update([disk(16, 16, 6)], 2)                             # fused into one big blob
check("synthetic_merge_both_censored",
      all(tr.status == MERGED for tr in t.tracks), [tr.status for tr in t.tracks])
check("merge_event_at_frame2", set(ev.values()) == {MERGED}, ev)
# no revival afterwards
t.update([disk(16, 16, 6)], 3)
check("merged_never_revived", all(tr.status == MERGED for tr in t.tracks), [tr.status for tr in t.tracks])

# 5) SYNTHETIC SPLIT: one blob divides into two masks; track censored SPLIT.
t = bt.BijectiveTracker(); t.seed([block(12, 20, 12, 20)], 0)  # 8x8 block
ev = t.update([block(12, 20, 12, 15), block(12, 20, 17, 20)], 1)  # two halves, each ~3/8 of track
check("synthetic_split_censored", t.tracks[0].status == SPLIT, t.tracks[0].status)

# 6) LOSS: the component disappears (only a far, non-overlapping blob remains) -> LOST.
t = bt.BijectiveTracker(); t.seed([disk(16, 16, 3)], 0)
ev = t.update([disk(28, 28, 2)], 1)                            # no overlap with the seed
check("loss_censored_lost", t.tracks[0].status == LOST, t.tracks[0].status)

# 7) AMBIGUITY: track overlaps two comps ~equally, each < split_frac but >= theta and within margin -> AMBIGUOUS.
t = bt.BijectiveTracker(theta=0.10, split_frac=0.30, ambiguity_margin=0.05)
t.seed([block(10, 20, 10, 20)], 0)                             # 100-cell track
# comp1 = 20 cells (0.20), comp2 = 18 cells (0.18): both < 0.30 (not split), diff 0.02 < margin
ev = t.update([block(10, 12, 10, 20), block(14, 16, 10, 19)], 1)
check("ambiguity_censored", t.tracks[0].status == AMBIGUOUS, f"{t.tracks[0].status} ev={ev}")

# invariant: one-to-one — no component assigned to >1 alive track across a random stress sequence
rng = np.random.default_rng(0); t = bt.BijectiveTracker(); t.seed([disk(8, 8, 3), disk(24, 24, 3)], 0)
ok_bijective = True
for k in range(1, 30):
    comps = [disk(int(8 + rng.integers(-2, 3)) % N, int(8 + rng.integers(-2, 3)) % N, 3),
             disk(int(24 + rng.integers(-2, 3)) % N, int(24 + rng.integers(-2, 3)) % N, 3)]
    t.update(comps, k)
    masks = [tr.mask.tobytes() for tr in t.tracks if tr.status == ALIVE]
    if len(masks) != len(set(masks)): ok_bijective = False
check("one_to_one_invariant_never_shared_component", ok_bijective)

npass = sum(1 for _, c, _ in results if c)
print(f"\n{npass}/{len(results)} checks PASS")
import sys; sys.exit(0 if npass == len(results) else 1)
