"""LCI-CAUSAL-MERGE-INCIDENT-01 — Phase 3 corrected periodic ONE-TO-ONE tracker (DEV).

Fixes the non-bijective assignment in causal_confirm.py::measure_branch (which lets several tracks lock onto the
SAME component after physical fusion). Geometry only: consumes per-frame connected-component masks (full periodic
grid boolean arrays; wrapping is represented in the array). NEVER reads a history coordinate, memory field,
turnover fraction, or any outcome/future response.

Guarantees:
  - a component may be assigned to AT MOST one track (max-weight bipartite matching);
  - a track receives AT MOST one component;
  - EXPLICIT censorship at the first merge / split / ambiguity — the individual trajectory ENDS there;
  - NEVER a silent reassignment.

Crucial semantics (per mission): a one-to-one assignment does NOT "repair" a physical fusion. If two entities
become one component, BOTH trajectories are censored as MERGED — we do not keep one and drop the other silently,
and we do not pretend the merged blob is either original individual.

Statuses: ALIVE, LOST (no component >= theta), MERGED (>=2 tracks' best is one component),
          SPLIT (a track's mask covers >=2 components each >= split_frac), AMBIGUOUS (unresolvable near-tie).
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

ALIVE, LOST, MERGED, SPLIT, AMBIGUOUS = "ALIVE", "LOST", "MERGED", "SPLIT", "AMBIGUOUS"


class Track:
    __slots__ = ("id", "mask", "status", "born", "died", "assign_history")
    def __init__(self, tid, mask, step):
        self.id = tid; self.mask = mask; self.status = ALIVE
        self.born = step; self.died = None; self.assign_history = [(step, "seed")]

    def censor(self, status, step):
        self.status = status; self.died = step; self.assign_history.append((step, status))


def _ov(track_mask, comp_mask):
    """Fraction of the TRACK covered by the component (periodic-agnostic: masks are full-grid)."""
    tm = track_mask.sum()
    return float((track_mask & comp_mask).sum() / tm) if tm else 0.0


class BijectiveTracker:
    def __init__(self, theta=0.10, split_frac=0.30, ambiguity_margin=0.05):
        self.theta = theta                 # min overlap to keep a track (matches sealed TRACK_THETA)
        self.split_frac = split_frac       # a track covering >=2 comps each >= this => SPLIT
        self.ambiguity_margin = ambiguity_margin
        self.tracks = []
        self._next = 0

    def seed(self, comp_masks, step=0):
        for m in comp_masks:
            self.tracks.append(Track(self._next, m, step)); self._next += 1
        return list(self.tracks)

    def alive(self):
        return [t for t in self.tracks if t.status == ALIVE]

    def update(self, comp_masks, step):
        """Advance one frame. Returns dict of events {track_id: status}. Censored tracks are never revived."""
        A = self.alive()
        events = {}
        if not A:
            return events
        nC = len(comp_masks)
        if nC == 0:
            for t in A: t.censor(LOST, step); events[t.id] = LOST
            return events
        O = np.zeros((len(A), nC))
        for i, t in enumerate(A):
            for j, cm in enumerate(comp_masks):
                O[i, j] = _ov(t.mask, cm)

        # ---- (1) SPLIT: a track substantially spread over >=2 components ----
        split_ids = set()
        for i, t in enumerate(A):
            big = [j for j in range(nC) if O[i, j] >= self.split_frac]
            if len(big) >= 2:
                t.censor(SPLIT, step); events[t.id] = SPLIT; split_ids.add(i)

        # ---- (2) MERGE: >=2 tracks whose BEST component is the same one (with overlap>=theta) ----
        rem = [i for i in range(len(A)) if i not in split_ids]
        best = {}
        for i in rem:
            j = int(np.argmax(O[i]))
            if O[i, j] >= self.theta:
                best.setdefault(j, []).append(i)
        merged_ids = set()
        for j, claimants in best.items():
            if len(claimants) >= 2:
                for i in claimants:
                    A[i].censor(MERGED, step); events[A[i].id] = MERGED; merged_ids.add(i)

        # ---- (3) bipartite one-to-one match for the survivors ----
        surv = [i for i in rem if i not in merged_ids]
        merged_comps = set(best.keys()) & {j for j, c in best.items() if len(c) >= 2}
        avail_comps = [j for j in range(nC) if j not in merged_comps]
        if surv and avail_comps:
            sub = O[np.ix_(surv, avail_comps)]
            # ambiguity: a survivor whose top-2 available overlaps tie within margin AND both >= theta
            for r, i in enumerate(surv):
                row = np.sort(sub[r])[::-1]
                if len(row) >= 2 and row[0] >= self.theta and (row[0] - row[1]) < self.ambiguity_margin and row[1] >= self.theta:
                    A[i].censor(AMBIGUOUS, step); events[A[i].id] = AMBIGUOUS
            surv2 = [i for i in surv if A[i].status == ALIVE]
            if surv2:
                sub2 = O[np.ix_(surv2, avail_comps)]
                cost = -sub2
                ri, cj = linear_sum_assignment(cost)
                matched = set()
                for r, c in zip(ri, cj):
                    i = surv2[r]; j = avail_comps[c]
                    if sub2[r, c] >= self.theta:
                        A[i].mask = comp_masks[j]; A[i].assign_history.append((step, f"comp{j}")); matched.add(i)
                    else:
                        A[i].censor(LOST, step); events[A[i].id] = LOST
                for i in surv2:
                    if i not in matched and A[i].status == ALIVE:
                        A[i].censor(LOST, step); events[A[i].id] = LOST
        else:
            for i in surv:
                if A[i].status == ALIVE:
                    A[i].censor(LOST, step); events[A[i].id] = LOST
        return events

    def summary(self):
        from collections import Counter
        c = Counter(t.status for t in self.tracks)
        return dict(n_tracks=len(self.tracks), alive=c[ALIVE], lost=c[LOST],
                    merged=c[MERGED], split=c[SPLIT], ambiguous=c[AMBIGUOUS])
