"""ROUTE_E_EXCHANGE_THROUGHPUT_CAUSAL_PROGRAM_07 -- operator gates and full instrumentation.

Production engine / detector / advance_passive_tracer used UNCHANGED (via od_core).

------------------------------------------------------------------------------------------
STRUCTURAL FACT THAT REORGANISES THE WHOLE PROGRAM
------------------------------------------------------------------------------------------
The parent (DEV_05) sink eligibility predicate is

        i in MASK   AND   i in TRACK   AND   m[i] >= THRESH

`detect_components` builds components from `occupied = state.m >= spec.matter_threshold`,
with matter_threshold == THRESH. Therefore every cell of every detected component already
satisfies m >= THRESH, and the third conjunct is IMPLIED BY the second. It is dead code.

Consequence: "the sink is starved because of the 0.45 threshold gate" is NOT a hypothesis --
it is a tautology restating the track gate. The eligibility of the sink is set by
        |MASK cap TRACK| and the matter standing there,
i.e. by MASK REGISTRATION, not by a threshold. This module therefore parameterises the
operator by three INDEPENDENT gates and measures all of them at every event.

  GATE_MASK    FROZEN    downstream half of C256, frozen at t256      (parent)
               COMOVING  downstream half of the CURRENT track C_t
               TRACKALL  the entire current track
  GATE_TRACK   True      target must belong to the tracked component  (parent)
               False     target may be any lattice site in the mask
  GATE_THRESH  True      target must carry m >= THRESH                (parent, redundant
                         under GATE_TRACK, binding only when GATE_TRACK is False)

SPREAD families are orthogonal to the gates:
  ORDERED     drain eligible cells one at a time in frozen priority order        (parent)
  MULTISITE   spread the quota proportionally over every eligible cell

Source placement families -- a LOCALITY LADDER at matched mass, to ask whether the coupling
gain needs upstream locality or merely generic replenishment:
  SINKSIDE    into the sink's own cells                    (distance 0, futile-cycle extreme)
  INTERFACE   upstream half of C256, inside the track      (parent)
  DISPERSED   proportionally over the whole track EXCEPT the sink mask
The overlapping placement SINKSIDE is order-dependent BY CONSTRUCTION (the sink drains matter
the source has just written). That is measured in fixture 6, declared, and is the reason the
canonical order is SINK_FIRST -- the parent's order -- in every arm.
"""
from __future__ import annotations
import math
from collections import deque
import numpy as np

from od_core import (THRESH, MMAX, comps, largest_bounded, cells_of, nbrs, fhash, advect,
                     LatticeBondState, LatticeBondEngine, graph_distance, AXES)

TOL = 1e-12
COHORTS = ("core", "inter", "bnd", "amb", "fre")
INCUMBENT = ("core", "inter", "bnd")

MASK_GATES = ("FROZEN", "COMOVING", "TRACKALL")
SPREADS = ("ORDERED", "MULTISITE")
SOURCE_PLACEMENTS = ("SINKSIDE", "INTERFACE", "DISPERSED")


class Gate:
    """A sink eligibility rule. `PARENT` reproduces DEV_05 exactly."""
    __slots__ = ("mask", "track", "thresh", "spread", "name")

    def __init__(self, name, mask="FROZEN", track=True, thresh=True, spread="ORDERED"):
        assert mask in MASK_GATES and spread in SPREADS
        self.name, self.mask, self.track, self.thresh, self.spread = \
            name, mask, bool(track), bool(thresh), spread

    def as_dict(self):
        return {"name": self.name, "GATE_MASK": self.mask, "GATE_TRACK": self.track,
                "GATE_THRESH": self.thresh, "SPREAD": self.spread}


PARENT_GATE = Gate("PARENT")


# ===================================================================== depth
def depth_partition(cells, L):
    """BOUNDARY = depth 1 from outside, INTERMEDIATE = 2, CORE >= 3. Frozen at t256."""
    inside = set(cells)
    d, q = {}, deque()
    for i in inside:
        if any(n not in inside for n in nbrs(i, L)):
            d[i] = 1
            q.append(i)
    while q:
        i = q.popleft()
        for n in nbrs(i, L):
            if n in inside and n not in d:
                d[n] = d[i] + 1
                q.append(n)
    return ({i for i in inside if d.get(i, 99) >= 3},
            {i for i in inside if d.get(i, 99) == 2},
            {i for i in inside if d.get(i, 99) == 1})


# ================================================================ provenance
class Prov:
    """Five mutually exclusive cohorts whose sum is identically the matter field.
    No credit field, no age field, no per-cell counter of any kind."""
    __slots__ = ("f", "res_source", "res_sink", "sink_by_cohort", "M256", "cells256")

    def __init__(self, state, cells256, L):
        core, inter, bnd = depth_partition(cells256, L)
        self.f = {c: np.zeros_like(state.m) for c in COHORTS}
        fl = {c: self.f[c].reshape(-1) for c in COHORTS}
        fm = state.m.reshape(-1)
        inside = set(cells256)
        for i in range(state.m.size):
            if i in core:
                fl["core"][i] = fm[i]
            elif i in inter:
                fl["inter"][i] = fm[i]
            elif i in bnd:
                fl["bnd"][i] = fm[i]
            elif i not in inside:
                fl["amb"][i] = fm[i]
        self.res_source = 0.0
        self.res_sink = 0.0
        self.sink_by_cohort = {c: 0.0 for c in COHORTS}
        self.cells256 = frozenset(int(i) for i in cells256)
        self.M256 = float(sum(fm[i] for i in cells256))

    def identity_residual(self, state):
        s = sum(self.f[c] for c in COHORTS)
        return float(np.max(np.abs(state.m - s)))

    def global_balance_residual(self, state, total0):
        return abs(float(state.m.sum()) + self.res_sink - self.res_source - total0)

    def advance(self, pre, ledger, post, dt):
        for c in COHORTS:
            self.f[c] = advect(self.f[c], pre, ledger, post, dt)

    def mass_in(self, cells, cohort):
        fl = self.f[cohort].reshape(-1)
        return float(sum(fl[i] for i in cells))

    def incumbent_in(self, cells):
        return sum(self.mass_in(cells, c) for c in INCUMBENT)


# =========================================================== eligibility
def _mask_cells(gate, masks, track, state, L):
    """The site set the sink is allowed to consider, BEFORE the track/thresh gates.
    COMOVING/TRACKALL are derived from `track`, the component the caller already detected:
    no second detector call, and the semantics are exactly 'the current tracked component'."""
    if gate.mask == "FROZEN":
        return masks["sink"]
    cells = sorted(int(i) for i in track)
    if not cells:
        return []
    if gate.mask == "TRACKALL":
        return cells
    proj = masks["proj"]
    off = float(np.mean([proj[i] for i in cells]))         # re-centre on the CURRENT track
    return sorted([i for i in cells if proj[i] - off > 0.0], key=lambda i: (-proj[i], i))


def sink_eligible(fm, cand, track, gate):
    """Sites the sink may draw from and the mass it may take from each.
    Reads ONLY the matter field, the mask and the current track. No provenance."""
    out = []
    for i in cand:
        if gate.track and i not in track:
            continue
        take = fm[i]
        if gate.thresh and take < THRESH:
            continue
        if take > TOL:
            out.append((i, take))
    return out


def source_eligible(fm, mask, track, gated=True):
    return [(i, MMAX - fm[i]) for i in mask
            if (i in track or not gated) and fm[i] < MMAX - TOL]


def capacity_spectrum(state, masks, track, L):
    """Zero-perturbation measurement. For ONE pre-event state, the eligible sink capacity
    under every gate combination, so that the binding constraint is observed rather than
    assumed. Nothing here mutates anything."""
    fm = state.m.reshape(-1)
    out = {}
    combos = {
        "PARENT":            Gate("PARENT"),
        "FROZEN_UNTRACKED":  Gate("x", track=False, thresh=True),
        "FROZEN_ANY":        Gate("x", track=False, thresh=False),
        "COMOVING":          Gate("x", mask="COMOVING"),
        "TRACKALL":          Gate("x", mask="TRACKALL"),
    }
    for k, g in combos.items():
        cand = _mask_cells(g, masks, track, state, L)
        el = sink_eligible(fm, cand, track, g)
        out[f"CAP_{k}"] = float(sum(t for _, t in el))
        out[f"NEL_{k}"] = len(el)
    frozen = masks["sink"]
    reg = [i for i in frozen if i in track]
    out["MASK_REGISTRATION"] = len(reg) / len(frozen) if frozen else None
    out["n_mask_frozen"] = len(frozen)
    out["n_mask_registered"] = len(reg)
    # exact, signed decomposition of the parent's shortfall against the co-moving ideal
    out["SHORTFALL_DEREGISTRATION"] = out["CAP_FROZEN_UNTRACKED"] - out["CAP_PARENT"]
    out["SHORTFALL_SUBTHRESHOLD"] = out["CAP_FROZEN_ANY"] - out["CAP_FROZEN_UNTRACKED"]
    out["HEADROOM_COMOVING"] = out["CAP_COMOVING"] - out["CAP_PARENT"]
    out["HEADROOM_TRACKALL"] = out["CAP_TRACKALL"] - out["CAP_PARENT"]
    return out


# ================================================================ operations
def apply_sink(state, prov, elig, quota, gate, L):
    """Conservative and provenance-blind. Removal from a cell is PROPORTIONAL to each
    cohort's presence in that cell at the moment of removal."""
    fm = state.m.reshape(-1)
    fl = {c: prov.f[c].reshape(-1) for c in COHORTS}
    removed = 0.0
    by = {c: 0.0 for c in COHORTS}
    sites = []

    def bite(i, take):
        nonlocal removed
        if take <= TOL:
            return
        frac = take / fm[i]
        for c in COHORTS:
            d = fl[c][i] * frac
            fl[c][i] -= d
            by[c] += d
        fm[i] -= take
        removed += take
        sites.append(i)

    if gate.spread == "MULTISITE":
        tot = sum(t for _, t in elig)
        if tot > TOL:
            f = min(1.0, quota / tot)
            for i, t in elig:
                bite(i, t * f)
    else:
        b = quota
        used, ordered = set(), []
        for strict in (True, False):        # frozen spread priority, identical to DEV_05
            for i, t in elig:
                if b <= TOL:
                    break
                if i in used:
                    continue
                if strict and any(n in used for n in nbrs(i, L)):
                    continue
                ordered.append((i, t))
                used.add(i)
                b -= min(t, b)
            if b <= TOL:
                break
        b = quota
        for i, t in ordered:
            if b <= TOL:
                break
            take = min(t, b)
            bite(i, take)
            b -= take
    prov.res_sink += removed
    for c in COHORTS:
        prov.sink_by_cohort[c] += by[c]
    return removed, by, sites


def apply_source(state, prov, elig, quota, spread):
    """Blank external payload: matter only, into state.m and prov.f['fre'].
    n and b are never touched by the operator."""
    fm = state.m.reshape(-1)
    ff = prov.f["fre"].reshape(-1)
    injected = 0.0
    sites = []

    def put(i, add):
        nonlocal injected
        if add <= TOL:
            return
        fm[i] += add
        ff[i] += add
        injected += add
        sites.append(i)

    if spread == "MULTISITE":
        tot = sum(c for _, c in elig)
        if tot > TOL:
            f = min(1.0, quota / tot)
            for i, c in elig:
                put(i, c * f)
    else:
        b = quota
        for i, c in elig:
            if b <= TOL:
                break
            add = min(b, c)
            put(i, add)
            b -= add
    prov.res_source += injected
    return injected, sites


def exchange_event(state, prov, masks, track, L, planned, gate=PARENT_GATE,
                   source_placement="INTERFACE", order="SINK_FIRST", mode="COUPLED",
                   source_spread="ORDERED"):
    """Both candidate sets are frozen on the SAME pre-event state before either side mutates.

    mode COUPLED      q = min(planned, sink_capacity, source_capacity); both sides move q or
                      the whole event is rejected.
    mode SINK_ONLY    egress alone.   mode SOURCE_ONLY  ingress alone.   mode SHAM  nothing.
    """
    fm = state.m.reshape(-1)
    m_before = state.m.copy()
    cand = _mask_cells(gate, masks, track, state, L)
    if source_placement == "DISPERSED":
        blocked = set(masks["sink"])
        pmask = [i for i in sorted(track) if i not in blocked]
        source_spread = "MULTISITE"          # dispersed means diluted, by definition
    else:
        pmask = {"INTERFACE": masks["source"], "SINKSIDE": masks["sink"]}[source_placement]
    se = sink_eligible(fm, cand, track, gate)
    pe = source_eligible(fm, pmask, track)
    qs = float(sum(t for _, t in se))
    qi = float(sum(c for _, c in pe))

    base = {"n_sink_elig": len(se), "n_source_elig": len(pe),
            "sink_capacity": qs, "source_capacity": qi,
            "removed_by_cohort": {c: 0.0 for c in COHORTS},
            "q_event": 0.0, "realized_sink": 0.0, "realized_source": 0.0,
            "n_sink_sites": 0, "n_source_sites": 0, "physical_state_delta": 0.0,
            "atomic": True, "rejected": True, "reject_reason": "NONE"}

    if mode == "SHAM":
        base["reject_reason"] = "SHAM"
        return base
    q = {"COUPLED": min(planned, qs, qi), "SINK_ONLY": min(planned, qs),
         "SOURCE_ONLY": min(planned, qi)}[mode]
    if q <= TOL:
        base["reject_reason"] = ("NO_SINK_CAPACITY" if qs <= TOL else
                                 "NO_SOURCE_CAPACITY" if qi <= TOL else "NO_PLANNED_DOSE")
        return base

    removed, injected = 0.0, 0.0
    by = {c: 0.0 for c in COHORTS}
    ssites, psites = [], []
    if mode == "SOURCE_ONLY":
        injected, psites = apply_source(state, prov, pe, q, source_spread)
    elif mode == "SINK_ONLY":
        removed, by, ssites = apply_sink(state, prov, se, q, gate, L)
    elif order == "SINK_FIRST":
        removed, by, ssites = apply_sink(state, prov, se, q, gate, L)
        injected, psites = apply_source(state, prov, pe, removed, source_spread)
    else:
        injected, psites = apply_source(state, prov, pe, q, source_spread)
        removed, by, ssites = apply_sink(state, prov, se, injected, gate, L)
    if mode == "COUPLED" and abs(injected - removed) > 1e-9:
        raise AssertionError(f"ATOMICITY_BROKEN removed={removed} injected={injected}")

    base.update({"q_event": q, "realized_sink": removed, "realized_source": injected,
                 "removed_by_cohort": by, "n_sink_sites": len(ssites),
                 "n_source_sites": len(psites), "rejected": False,
                 "physical_state_delta": float(np.max(np.abs(state.m - m_before)))})
    return base


# ==================================================================== masks
def build_masks(cells, L, cy, cx, axis):
    dy, dx = AXES[axis]
    yy, xx = np.mgrid[0:L, 0:L]
    proj = ((yy - cy) * dy + (xx - cx) * dx).reshape(-1)
    return {"sink": sorted([i for i in cells if proj[i] > 0.0], key=lambda i: (-proj[i], i)),
            "source": sorted([i for i in cells if proj[i] < 0.0], key=lambda i: (proj[i], i)),
            "all": sorted(int(i) for i in cells), "axis": axis, "proj": proj}


# ============================================================== observables
def sweep_decomposition(prev_cells, prev_m, cells, m):
    """Exact identity  dT = MATERIAL_CHANGE_ON_RETAINED_SITES + MASK_ENTRY + MASK_EXIT.
    Separates matter that changed under a stationary tracker from matter the tracker
    swept over. `prev_m`/`m` are FLAT matter fields at the two times."""
    if prev_cells is None:
        return None
    ret = prev_cells & cells
    ent = cells - prev_cells
    exi = prev_cells - cells
    d_ret = math.fsum(m[i] - prev_m[i] for i in ret)
    d_ent = math.fsum(m[i] for i in ent)
    d_exi = -math.fsum(prev_m[i] for i in exi)
    uni = prev_cells | cells
    return {"MATERIAL_CHANGE_ON_RETAINED_SITES": d_ret, "MASK_ENTRY": d_ent,
            "MASK_EXIT": d_exi, "TRACKER_SWEEP": d_ent + d_exi,
            "n_retained": len(ret), "n_entered": len(ent), "n_exited": len(exi),
            "jaccard": len(ret) / len(uni) if uni else None}


def frame_metrics(state, prov, cells, L):
    """Fixed-frame quantities DEV_05 never saved: what the boundary-crossing question needs."""
    fm = state.m.reshape(-1)
    c256 = prov.cells256
    inter = c256 & cells
    per = 0
    for i in cells:
        per += sum(1 for n in nbrs(i, L) if n not in cells)
    return {"mass_in_frozen_C256": math.fsum(fm[i] for i in c256),
            "incumbent_in_frozen_C256": math.fsum(
                prov.f[c].reshape(-1)[i] for c in INCUMBENT for i in c256),
            "fresh_in_frozen_C256": math.fsum(prov.f["fre"].reshape(-1)[i] for i in c256),
            "mass_in_C256_cap_Ct": math.fsum(fm[i] for i in inter),
            "n_C256_cap_Ct": len(inter),
            "jaccard_C256_Ct": len(inter) / len(c256 | cells) if (c256 | cells) else None,
            "boundary_site_turnover": (len(cells - c256) + len(c256 - cells)) / len(c256),
            "perimeter": per, "area": len(cells)}


def track_of(state):
    return largest_bounded(state)


def scaffold(prov, cells, L):
    """Largest connected set of tracked cells whose INCUMBENT mass alone clears THRESH."""
    fl = [prov.f[c].reshape(-1) for c in INCUMBENT]
    keep = {i for i in cells if (fl[0][i] + fl[1][i] + fl[2][i]) >= THRESH}
    if not keep:
        return 0, 0.0
    seen, best_n, best_m = set(), 0, 0.0
    for s in keep:
        if s in seen:
            continue
        comp, q = [], deque([s])
        seen.add(s)
        while q:
            i = q.popleft()
            comp.append(i)
            for n in nbrs(i, L):
                if n in keep and n not in seen:
                    seen.add(n)
                    q.append(n)
        mm = math.fsum(fl[0][i] + fl[1][i] + fl[2][i] for i in comp)
        if len(comp) > best_n or (len(comp) == best_n and mm > best_m):
            best_n, best_m = len(comp), mm
    return best_n, best_m


class Lineage:
    __slots__ = ("prev_cells", "prev_label", "lost", "merger", "split", "reacq",
                 "first_failure_time", "first_failure_type", "continuous")

    def __init__(self):
        self.prev_cells = None
        self.prev_label = None
        self.lost = self.merger = self.split = self.reacq = False
        self.first_failure_time = None
        self.first_failure_type = "NONE"
        self.continuous = True

    def _fail(self, t, k):
        self.continuous = False
        if self.first_failure_time is None:
            self.first_failure_time, self.first_failure_type = t, k

    def update(self, state, t):
        allc = comps(state)
        label = {}
        for k, c in enumerate(allc):
            for i in cells_of(c):
                label[i] = k
        cur = track_of(state)
        if cur is None:
            if not self.lost:
                self._fail(t, "TRACK_LOST_OR_DISSOLVED")
            self.lost = True
            self.prev_cells, self.prev_label = None, label
            return None
        cells = cells_of(cur)
        if self.lost:
            self.reacq = True
            self._fail(t, "REACQUISITION")
        if cur.wraps_x or cur.wraps_y:
            self._fail(t, "WRAPPING")
        if self.prev_cells is not None and self.prev_label is not None:
            if len({self.prev_label[i] for i in cells if i in self.prev_label}) > 1:
                self.merger = True
                self._fail(t, "MERGER")
            if len({label[i] for i in self.prev_cells if i in label}) > 1:
                self.split = True
                self._fail(t, "SPLIT")
        self.prev_cells, self.prev_label = cells, label
        return cur


def snapshot(state, prov, L, M256, I0):
    c = track_of(state)
    if c is None:
        return {"track": False}
    cells = cells_of(c)
    fm = state.m.reshape(-1)
    T = math.fsum(fm[i] for i in cells)
    I = prov.incumbent_in(cells)
    F = prov.mass_in(cells, "fre")
    A = prov.mass_in(cells, "amb")
    sn, sm = scaffold(prov, cells, L)
    out = {"track": True, "cells": cells, "area": c.area, "cy": c.centroid_y,
           "cx": c.centroid_x, "wrap": bool(c.wraps_x or c.wraps_y),
           "T": T, "I": I, "F": F, "A": A,
           "I_over_I0": (I / I0) if I0 > 0 else float("nan"),
           "I_over_T": (I / T) if T > 0 else float("nan"),
           "F_over_M256": F / M256, "F_over_T": (F / T) if T > 0 else float("nan"),
           "A_over_M256": A / M256, "T_over_M256": T / M256,
           "scaffold_cells": sn, "scaffold_mass": sm}
    for k in INCUMBENT:
        out[f"{k}_in_track"] = prov.mass_in(cells, k)
    out.update(frame_metrics(state, prov, cells, L))
    return out
