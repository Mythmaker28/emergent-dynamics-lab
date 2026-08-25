"""OMLDCT02 — classifier A, rebound.

Classifier A is LDFMA01's third independent reconstruction, ldfma01_raw. This file is an ADAPTER,
not a reimplementation: every scientific stage — components, centroid, the strict link rule, the
running-identity trace — is A's own code, called here. What this file adds is only the extraction of
the two OMLDCT02 endpoints from A's trace.

A's audit() cannot be used directly, because it is built around the removal ledger and a SHAM arm
by construction has no removal. The adapter therefore takes t_m and the locked-daughter cell set as
INPUTS, exactly as the fork runner supplies them to both arms, and reads no ledger.

Window convention, inherited from A and stated rather than rediscovered:

    duration = end - t_m           rows t_m+1 .. end        (t_m EXCLUDED)
    exposure = sum of nY over      rows t_m   .. end        (t_m INCLUDED)

The asymmetry is deliberate. The archive writes a cell row AFTER the step, so occupancy on row t is
the population a decay at step t+1 acts on; an exposure window starting at row t_m is the correct
driver for events at steps t_m+1..end+1, and it is the convention under which LDFMA01's Poisson map
read 5.809 predicted against 5 observed.
"""
from __future__ import annotations
import os, sys

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
os.environ.setdefault("LDFMA01_REPO", REPO)
sys.path.insert(0, os.path.join(REPO, "LDFMA01", "code"))
import ldfma01_raw as A          # the frozen classifier: components_bfs, centroid, link, World.trace

CLASSIFIER_A_SOURCE = os.path.join(REPO, "LDFMA01", "code", "ldfma01_raw.py")

def e3(path, t_m, daughter_cells):
    """Returns A's values for the two endpoints. Every stage below is A's code."""
    w = A.World(path)                                   # A's archive reader and component builder
    ev, ids_at, named_at, lvl_at, nattempt = w.trace()  # A's running-identity trace
    t_m = int(t_m)
    dset = frozenset((int(a), int(b)) for a, b in daughter_cells)
    groups = w.groups.get(t_m)
    if not groups:
        return {"OK": False, "REASON": "NO_COMPONENT_AT_t_m", "t_m": t_m}
    hit = [j for j in range(len(groups)) if w.gcells[t_m][j] == dset]
    if len(hit) != 1:
        return {"OK": False, "REASON": "LEDGER_DAUGHTER_CELLS_ARE_NOT_EXACTLY_ONE_COMPONENT_AT_t_m",
                "t_m": t_m, "n_matching_components": len(hit)}
    did = ids_at[t_m][hit[0]]
    e = ev[did]
    steps = [t for t in range(t_m, w.T) if did in ids_at.get(t, ())]
    last = max(steps) if steps else t_m
    life = e["end"] - t_m
    pstep = 0; hist = {}; mn = 10 ** 9; mx = 0
    for t in steps:
        j = ids_at[t].index(did); v = int(w.gnY[t][j])
        pstep += v; hist[v] = hist.get(v, 0) + 1; mn = min(mn, v); mx = max(mx, v)
    if last >= w.T - 1:
        term = "REACHED_THE_WINDOW_HORIZON"
    else:
        nx = w.cens.get(last + 1)
        if not nx: term = "NO_COMPONENT_AT_THE_NEXT_STEP"
        else:
            j = ids_at[last].index(did)
            term = A.link_reason(w.cens[last], nx).get(j, "UNCLASSIFIED")
    return {"OK": True, "t_m": t_m, "interval_end": e["end"],
            "E3_DURATION": life, "E3_EXPOSURE": pstep,
            "identity_termination_type": term,
            "n_rows_in_interval": len(steps),
            "contiguous": len(steps) == (last - t_m + 1),
            "min_nY": (mn if steps else None), "max_nY": (mx if steps else None),
            "nY_histogram": {str(k): v for k, v in sorted(hist.items())},
            "L": A.L, "CORE_R": A.CORE_R}
