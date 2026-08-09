"""ROUTE_E_SAFE_ACTUATION_AND_FEEDBACK_CAUSAL_PROGRAM_08 -- safe actuation and feedback.

Built on the SEALED p07_core (imported, never edited). The engine, detector and passive tracer
are the production ones, unmodified.

--------------------------------------------------------------------------------------------
WHAT THE P08 AUDIT ESTABLISHED, AND WHAT THIS MODULE IS FOR
--------------------------------------------------------------------------------------------
4036 / 4036 rejections in P07 fall in ONE category: the allowed support still holds matter
(median 24.2 units) but ALL of it below THRESH. Global exhaustion: 0 events. Supra-threshold
matter stranded outside the track: 0 events. The limit is therefore
LOCAL_SUBTHRESHOLD_INACCESSIBILITY_IN_A_FIXED_SUPPORT, and the operator creates it itself,
because the sink drains cells past the very threshold the detector uses to define the target.

The amount rule is reduced to TWO numbers, giving an exact 2x2 factorial:

    floor : the sink never takes a cell below `floor`      (self-erasure guard)
    ceil  : the source never fills a cell above `ceil`     (saturation guard)

    PARENT      (0.00, 1.00)   reproduces the sealed P07 operator exactly
    SINK_FLOOR  (0.50, 1.00)
    SRC_CAP     (0.00, 0.90)
    BOTH_SAFE   (0.50, 0.90)

WHEN (schedule) and WHERE (frozen masks) are held IDENTICAL across all four. Only AMOUNT
varies. The feedback phase varies only WHEN; the optional spatial phase varies only WHERE.

--------------------------------------------------------------------------------------------
ORACLE FIREWALL
--------------------------------------------------------------------------------------------
Every quantity a policy may read is computed here by `sensor_readout`, which touches ONLY the
matter field, the frozen geometry and the current detected track. It cannot see provenance,
the future, the terminal outcome, the seed, or cohort membership. An AST fixture enforces it.

--------------------------------------------------------------------------------------------
SHADOW TRACKERS
--------------------------------------------------------------------------------------------
A safety floor at THRESH + eps could keep cells alive for the DETECTOR without keeping the
object alive. Shadow readers at thresholds 0.40 / 0.45 / 0.50 / 0.55 / 0.60, plus the
distribution of m - THRESH inside the official track, are recorded at every checkpoint. The
official tracker stays frozen and remains the only one used for endpoints.
"""
from __future__ import annotations
import math
from collections import deque
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
from od_core import (THRESH, MMAX, comps, largest_bounded, cells_of, nbrs, fhash, advect,
                     LatticeBondState, LatticeBondEngine)
from edlab.substrates.lattice_bond.instrumentation import DetectorSpec, detect_components
import p07_core as P7

TOL = 1e-12
COHORTS = P7.COHORTS
INCUMBENT = P7.INCUMBENT
Prov = P7.Prov
Lineage = P7.Lineage
build_masks = P7.build_masks
depth_partition = P7.depth_partition
frame_metrics = P7.frame_metrics
sweep_decomposition = P7.sweep_decomposition

SHADOW_THRESHOLDS = (0.40, 0.45, 0.50, 0.55, 0.60)
EPS_FLOOR = 0.05                      # floor = THRESH + EPS_FLOOR = 0.50
H_HEADROOM = 0.10                     # ceil  = MMAX - H_HEADROOM = 0.90

AMOUNT_RULES = {
    "PARENT":     (0.00, 1.00),
    "SINK_FLOOR": (THRESH + EPS_FLOOR, 1.00),
    "SRC_CAP":    (0.00, MMAX - H_HEADROOM),
    "BOTH_SAFE":  (THRESH + EPS_FLOOR, MMAX - H_HEADROOM),
}


# ====================================================== eligibility with caps
def sink_eligible(fm, mask, track, floor):
    """Sites the sink may draw from, and how much it may take from each without pushing the
    cell below `floor`. Reads only the matter field, the frozen mask and the current track."""
    out = []
    for i in mask:
        if i not in track:
            continue
        take = fm[i] - floor
        if take > TOL:
            out.append((i, take))
    return out


def source_eligible(fm, mask, track, ceil):
    """Sites the source may fill, and the room left below `ceil`."""
    out = []
    for i in mask:
        if i not in track:
            continue
        room = ceil - fm[i]
        if room > TOL:
            out.append((i, room))
    return out


def _ordered(elig, quota, L):
    """Frozen spread priority, bit-identical to DEV_05 / P07: two passes, the first refusing
    a site adjacent to one already chosen."""
    b = quota
    used, order = set(), []
    for strict in (True, False):
        for i, t in elig:
            if b <= TOL:
                break
            if i in used:
                continue
            if strict and any(nb in used for nb in nbrs(i, L)):
                continue
            order.append((i, t))
            used.add(i)
            b -= min(t, b)
        if b <= TOL:
            break
    return order


def apply_sink(state, prov, elig, quota, L):
    fm = state.m.reshape(-1)
    fl = {c: prov.f[c].reshape(-1) for c in COHORTS}
    removed = 0.0
    by = {c: 0.0 for c in COHORTS}
    sites = []
    b = quota
    for i, t in _ordered(elig, quota, L):
        if b <= TOL:
            break
        take = min(t, b)
        if take <= TOL:
            continue
        frac = take / fm[i]
        for c in COHORTS:
            d = fl[c][i] * frac
            fl[c][i] -= d
            by[c] += d
        fm[i] -= take
        removed += take
        b -= take
        sites.append(i)
    prov.res_sink += removed
    for c in COHORTS:
        prov.sink_by_cohort[c] += by[c]
    return removed, by, sites


def apply_source(state, prov, elig, quota):
    fm = state.m.reshape(-1)
    ff = prov.f["fre"].reshape(-1)
    injected = 0.0
    sites = []
    b = quota
    for i, room in elig:
        if b <= TOL:
            break
        add = min(b, room)
        if add <= TOL:
            continue
        fm[i] += add
        ff[i] += add
        injected += add
        b -= add
        sites.append(i)
    prov.res_source += injected
    return injected, sites


def exchange_event(state, prov, masks, track, L, planned, floor=0.0, ceil=MMAX, mode="COUPLED"):
    """Atomic coupled exchange. Both candidate sets are frozen on the same pre-event state.
    `floor` and `ceil` are the only knobs; everything else is the sealed P07 geometry."""
    fm = state.m.reshape(-1)
    m0 = state.m.copy()
    se = sink_eligible(fm, masks["sink"], track, floor)
    pe = source_eligible(fm, masks["source"], track, ceil)
    qs = math.fsum(t for _, t in se)
    qi = math.fsum(r for _, r in pe)
    base = {"n_sink_elig": len(se), "n_source_elig": len(pe),
            "sink_capacity": qs, "source_capacity": qi, "planned": planned,
            "removed_by_cohort": {c: 0.0 for c in COHORTS},
            "q_event": 0.0, "realized_sink": 0.0, "realized_source": 0.0,
            "n_sink_sites": 0, "n_source_sites": 0, "rejected": True,
            "reject_reason": "NONE", "bound_by": "NONE"}
    if mode == "SHAM":
        base["reject_reason"] = "SHAM"
        return base
    q = min(planned, qs, qi)
    if q <= TOL:
        base["reject_reason"] = ("NO_SINK_CAPACITY" if qs <= TOL else
                                 "NO_SOURCE_CAPACITY" if qi <= TOL else "NO_PLANNED_DOSE")
        return base
    removed, by, ss = apply_sink(state, prov, se, q, L)
    injected, ps = apply_source(state, prov, pe, removed)
    if abs(injected - removed) > 1e-9:
        raise AssertionError(f"ATOMICITY_BROKEN {removed} vs {injected}")
    base.update({"q_event": q, "realized_sink": removed, "realized_source": injected,
                 "removed_by_cohort": by, "n_sink_sites": len(ss), "n_source_sites": len(ps),
                 "rejected": False,
                 "bound_by": ("PLANNED" if abs(q - planned) < 1e-9 else
                              "SOURCE" if abs(q - qi) < 1e-9 else
                              "SINK" if abs(q - qs) < 1e-9 else "OTHER"),
                 "physical_state_delta": float(np.max(np.abs(state.m - m0)))})
    return base


# ============================================================ oracle firewall
def sensor_readout(state, masks, track, L, floor, ceil):
    """EVERYTHING a policy is allowed to read, and nothing else.

    Matter field, frozen geometry, current detected track. No provenance, no future, no
    terminal outcome, no seed, no cohort membership. Enforced by fixture 5 (AST scan)."""
    fm = state.m.reshape(-1)
    se = sink_eligible(fm, masks["sink"], track, floor)
    pe = source_eligible(fm, masks["source"], track, ceil)
    reg = (len([i for i in masks["sink"] if i in track]) / len(masks["sink"])
           if masks["sink"] else 0.0)
    return {"sink_capacity": math.fsum(t for _, t in se),
            "source_capacity": math.fsum(r for _, r in pe),
            "n_sink_elig": len(se), "n_source_elig": len(pe),
            "mask_registration": reg,
            "feasible_q": min(math.fsum(t for _, t in se), math.fsum(r for _, r in pe))}


# ============================================================= shadow readers
_SHADOW_SPECS = {t: DetectorSpec(matter_threshold=t, min_cells=3) for t in SHADOW_THRESHOLDS}


def shadow_readout(state, official_cells, cells256):
    """Pre-declared shadow readers. Never used for any endpoint; used only to decide whether a
    survival is an object surviving or a detector being satisfied."""
    out = {}
    fm = state.m.reshape(-1)
    for t, spec in _SHADOW_SPECS.items():
        cs = detect_components(state, spec, frame=int(state.step))
        bounded = [c for c in cs if not (c.wraps_x or c.wraps_y)]
        key = f"shadow_{int(round(t * 100))}"
        if not bounded:
            out[key + "_alive"] = False
            out[key + "_area"] = 0
            out[key + "_jaccard_official"] = 0.0
            out[key + "_jaccard_C256"] = 0.0
            continue
        c = sorted(bounded, key=lambda x: (-x.area, x.centroid_y, x.centroid_x, x.index))[0]
        cc = cells_of(c)
        out[key + "_alive"] = True
        out[key + "_area"] = c.area
        u = cc | official_cells
        out[key + "_jaccard_official"] = len(cc & official_cells) / len(u) if u else 0.0
        u2 = cc | cells256
        out[key + "_jaccard_C256"] = len(cc & cells256) / len(u2) if u2 else 0.0
    if official_cells:
        marg = sorted(fm[i] - THRESH for i in official_cells)
        k = len(marg)
        out["margin_min"] = marg[0]
        out["margin_q10"] = marg[max(0, k // 10 - 1)]
        out["margin_median"] = marg[k // 2]
        out["margin_frac_below_0.05"] = sum(1 for x in marg if x < 0.05) / k
        out["margin_frac_below_0.10"] = sum(1 for x in marg if x < 0.10) / k
    return out


# =============================================================== the endpoint
def unique_causal_replacement(prov, cells, M256):
    """UCR = min( incumbent removed by the sink and never re-counted ,
                  fresh mass still inside the tracked component ) / M256.

    Neither term can be inflated by re-injecting into a cell just drained: removal is
    proportional to local cohort presence, so a cell that has become fresh yields fresh;
    and fresh that is removed again is no longer retained."""
    inc = sum(prov.sink_by_cohort[c] for c in INCUMBENT)
    fresh = prov.mass_in(cells, "fre") if cells else 0.0
    return {"incumbent_removed_unique": inc, "fresh_retained": fresh,
            "UCR": min(inc, fresh) / M256, "inc_over_M256": inc / M256,
            "fresh_over_M256": fresh / M256}


def futile_fraction(prov):
    """Share of the sink's total take that was matter the source had itself injected."""
    tot = sum(prov.sink_by_cohort[c] for c in COHORTS)
    return (prov.sink_by_cohort["fre"] / tot) if tot > TOL else 0.0
