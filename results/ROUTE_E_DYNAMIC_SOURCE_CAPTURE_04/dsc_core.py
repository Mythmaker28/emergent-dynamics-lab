"""ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 -- provenance cohorts, causal counters, operators.

Production engine, detector and advance_passive_tracer used UNCHANGED (imported via od_core).
Nothing in edlab/ is modified by this module.

Two source filters live side by side, both versioned; the legacy one is NOT replaced:
  source_filter_legacy      -- verbatim reproduction of od_ops.do_event's source predicates
  source_filter_redesigned  -- legacy with P2 replaced by P2' (see below)

P2  (legacy):  `if any(n in track for n in nbrs(s,L)): continue`
P2' (new)   :  a track-adjacent site MAY receive matter, but only up to a value that keeps it
               STRICTLY sub-threshold (m < THRESH). It therefore stays detector-empty, the
               operator never creates a supra-threshold bridge to the component, and the
               empty gap between the source halo and the track survives the injection.
               Non-adjacent sites keep the legacy capacity MMAX - m.
This is the smallest source-side relaxation that leaves every prohibition of section 3 intact.
"""
from __future__ import annotations
import math
from collections import deque
import numpy as np

from od_core import (THRESH, MMAX, DET, comps, largest_bounded, cells_of, nbrs, fhash, advect,
                     LatticeBondState, LatticeBondEngine)
from od_core import graph_distance, AXES

EPS = 1e-9
CONS_TOL = 1e-9          # absolute algebraic ledger tolerance
NUM_TOL_REL = 1e-12      # numerical recomputation tolerance, relative to M256


# ===================================================================== cohorts
class Provenance:
    """Three passive tracer fields whose sum is identically the matter field.

    INC  = INCUMBENT_256, all matter inside C256 at t256          (sums to M256)
    AMB  = AMBIENT_256,   all matter elsewhere on the lattice at t256
    FRE  = FRESH_SOURCE,  external matter introduced by the operator after t256
    Per-event provenance fields are AGGREGATED into FRE: no endpoint of this mission
    resolves individual events, and 80 advected fields per trajectory is not affordable.
    Declared as PER_EVENT_PROVENANCE = AGGREGATED_INTO_FRESH_TOTAL.
    """

    __slots__ = ("inc", "amb", "fre", "credited", "res_sink", "res_source",
                 "sink_inc", "sink_amb", "sink_fre")

    def __init__(self, state, cells256):
        self.inc = np.zeros_like(state.m)
        self.amb = state.m.copy()
        f_inc, f_amb, f_m = self.inc.reshape(-1), self.amb.reshape(-1), state.m.reshape(-1)
        for i in cells256:
            f_inc[i] = f_m[i]
            f_amb[i] = 0.0
        self.fre = np.zeros_like(state.m)
        self.credited = np.zeros_like(state.m)   # absorbing per-cell capture credit
        self.res_source = 0.0                    # mass paid out of the external source
        self.res_sink = 0.0                      # mass received by the sink
        self.sink_inc = 0.0
        self.sink_amb = 0.0
        self.sink_fre = 0.0

    # -- exact algebraic identity, checked after every mutation and every engine step --
    def balance_error(self, state):
        return float(np.max(np.abs(state.m - (self.inc + self.amb + self.fre))))

    def system_error(self, state, total0):
        cur = float(state.m.sum()) + self.res_sink - self.res_source
        return abs(cur - total0)

    def advance(self, pre, ledger, post, dt):
        self.inc = advect(self.inc, pre, ledger, post, dt)
        self.amb = advect(self.amb, pre, ledger, post, dt)
        self.fre = advect(self.fre, pre, ledger, post, dt)


# ============================================================ source selection
def _admissible_capacity(fm, s, track, L, redesigned):
    """Capacity of site s under the active filter. 0.0 means the site is rejected."""
    if s in track:                                    # never inject into the component
        return 0.0, "REJECT_INSIDE_TRACK"
    if fm[s] >= THRESH:                               # P1
        return 0.0, "REJECT_OCCUPIED"
    adj = any(n in track for n in nbrs(s, L))
    if adj:
        if not redesigned:                            # P2 legacy
            return 0.0, "REJECT_TRACK_ADJACENCY"
        cap = THRESH - fm[s] - EPS                    # P2' sub-threshold cap
        if cap <= 1e-12:
            return 0.0, "REJECT_CAPACITY"
        return cap, "ACCEPTED_SUBTHRESHOLD_ADJACENT"
    cap = MMAX - fm[s]                                # P3
    if cap <= 1e-12:
        return 0.0, "REJECT_CAPACITY"
    return cap, "ACCEPTED"


def source_capacity(fm, mask, track, L, redesigned):
    """Total mass the source side could deliver THIS event. Selection only, no mutation."""
    tot = 0.0
    for s in mask:
        c, _ = _admissible_capacity(fm, s, track, L, redesigned)
        tot += c
    return tot


def sink_capacity(fm, mask, track, L):
    """Total mass the sink side could remove THIS event (whole eligible cells)."""
    return float(sum(fm[i] for i in mask if i in track and fm[i] >= THRESH))


# ================================================================== operations
def do_sink(state, prov, mask, track, L, quota):
    """Distributed partial removal. Never empties a cell below threshold in one bite is NOT
    imposed: partial removal keeps every touched cell above threshold only where possible."""
    fm = state.m.reshape(-1)
    fi, fa, ff = prov.inc.reshape(-1), prov.amb.reshape(-1), prov.fre.reshape(-1)
    cands = [i for i in mask if i in track and fm[i] >= THRESH]
    # frozen priority: spread removals, avoid adjacent bites while non-adjacent ones remain
    chosen, used, b = [], set(), quota
    for strict in (True, False):
        for i in cands:
            if b <= 1e-12:
                break
            if i in used:
                continue
            if strict and any(n in used for n in nbrs(i, L)):
                continue
            chosen.append(i); used.add(i); b -= min(fm[i], b)
        if b <= 1e-12:
            break
    removed = inc_out = amb_out = fre_out = 0.0
    b = quota
    for i in chosen:
        if b <= 1e-12:
            break
        take = min(fm[i], b)
        frac = take / fm[i] if fm[i] > 0 else 0.0
        io, ao, fo = fi[i] * frac, fa[i] * frac, ff[i] * frac
        fm[i] -= take; fi[i] -= io; fa[i] -= ao; ff[i] -= fo
        removed += take; inc_out += io; amb_out += ao; fre_out += fo
        b -= take
    prov.res_sink += removed
    prov.sink_inc += inc_out; prov.sink_amb += amb_out; prov.sink_fre += fre_out
    return {"removed": removed, "inc_to_sink": inc_out, "amb_to_sink": amb_out,
            "fre_to_sink": fre_out}


def do_source(state, prov, mask, track, L, quota, redesigned):
    """Inject external matter into the halo. Returns injected mass and the reject taxonomy."""
    fm = state.m.reshape(-1); ff = prov.fre.reshape(-1); cr = prov.credited.reshape(-1)
    injected = 0.0; b = quota
    counts = {}
    sites = []
    for s in mask:
        if b <= 1e-12:
            counts["REJECT_QUOTA"] = counts.get("REJECT_QUOTA", 0) + 1
            continue
        cap, tag = _admissible_capacity(fm, s, track, L, redesigned)
        counts[tag] = counts.get(tag, 0) + 1
        if cap <= 1e-12:
            continue
        add = min(b, cap)
        fm[s] += add; ff[s] += add
        if s in track:      # unreachable under both filters; belt and braces
            cr[s] += add
        injected += add; b -= add
        sites.append((s, tag))
    prov.res_source += injected
    return {"injected": injected, "reject_counts": counts, "sites": sites}


def do_direct_interface(state, prov, sink_mask, source_mask, track, L, quota):
    """POSITIVE CONTROL. A real physical transfer reservoir->lattice and lattice->reservoir
    through FROZEN interface links that sit INSIDE the component. This is a genuine mass
    exchange, but it is DIRECT_OPERATOR_INSERTION by construction and can never be counted
    as DYNAMICS_MEDIATED_CAPTURE."""
    fm = state.m.reshape(-1)
    # how much can the interface accept / release this event
    in_sites = [i for i in source_mask if i in track and fm[i] < MMAX]
    out = do_sink(state, prov, sink_mask, track, L, quota)
    removed = out["removed"]
    ff = prov.fre.reshape(-1); cr = prov.credited.reshape(-1)
    injected = 0.0; b = removed
    for i in in_sites:
        if b <= 1e-12:
            break
        cap = MMAX - fm[i]
        if cap <= 1e-12:
            continue
        add = min(b, cap)
        fm[i] += add; ff[i] += add
        # The operator placed this mass INSIDE the component. Bump the absorbing capture
        # credit by the same amount so it can never be re-read as DYNAMICS_MEDIATED_CAPTURE.
        cr[i] += add
        injected += add; b -= add
    prov.res_source += injected
    out.update(injected=injected, direct_insertion=injected)
    return out


# ====================================================== atomic coupled event
def coupled_event(state, prov, masks, track, L, planned, mode, redesigned):
    """Select BOTH sides before mutating either. q = min(planned, q_source, q_sink)."""
    fm = state.m.reshape(-1)
    if mode == "SHAM":
        _ = sink_capacity(fm, masks["sink"], track, L)
        _ = source_capacity(fm, masks["source"], track, L, redesigned)
        return {"removed": 0.0, "injected": 0.0, "q_event": 0.0,
                "inc_to_sink": 0.0, "fre_to_sink": 0.0, "direct_insertion": 0.0,
                "flux_deficit": planned, "reject_counts": {}}
    if mode == "DIRECT_INTERFACE":
        qs = sink_capacity(fm, masks["sink"], track, L)
        qi = float(sum(MMAX - fm[i] for i in masks["source_interface"] if i in track))
        q = min(planned, qs, qi)
        if q <= 1e-12:
            return {"removed": 0.0, "injected": 0.0, "q_event": 0.0, "inc_to_sink": 0.0,
                    "fre_to_sink": 0.0, "direct_insertion": 0.0,
                    "flux_deficit": planned, "reject_counts": {}}
        r = do_direct_interface(state, prov, masks["sink"], masks["source_interface"],
                                track, L, q)
        r.update(q_event=q, flux_deficit=planned - min(r["removed"], r["injected"]),
                 reject_counts={})
        return r
    # COUPLED source+sink through the halo
    qs = sink_capacity(fm, masks["sink"], track, L)
    qi = source_capacity(fm, masks["source"], track, L, redesigned)
    q = min(planned, qs, qi)
    if q <= 1e-12:
        return {"removed": 0.0, "injected": 0.0, "q_event": 0.0, "inc_to_sink": 0.0,
                "fre_to_sink": 0.0, "direct_insertion": 0.0,
                "flux_deficit": planned, "reject_counts": {}}
    a = do_sink(state, prov, masks["sink"], track, L, q)
    b = do_source(state, prov, masks["source"], track, L, q, redesigned)
    a.update(injected=b["injected"], reject_counts=b["reject_counts"], q_event=q,
             direct_insertion=0.0,
             flux_deficit=planned - min(a["removed"], b["injected"]))
    return a


# ============================================ first-passage causal accounting
class Causal:
    """First-passage counters with ABSORBING per-cell credit fields. Exit and re-entry of the
    same matter is never counted twice, because a credit field only ever increases.

    Capture is split three ways, and only the first one feeds the primary endpoint:
      capture_transport -- fresh mass appearing in a cell that was ALREADY in the track.
                           The engine moved it there. This is DYNAMICS_MEDIATED_CAPTURE.
      capture_engulf    -- the track boundary expanded over a cell where fresh mass was
                           already standing. The matter did not move; the component grew.
      capture_by_merger -- the cell belonged to a DIFFERENT detected component at the
                           previous frame. Excluded from the primary signal by section 5.

    Residence uses a rolling-window MINIMUM of the fresh mass inside the track. min over
    [t-w, t] lower-bounds the mass continuously resident across that window, so
    INCORPORATION_16 / DURABLE_INCORPORATION_128 can only UNDERSTATE. Declared conservative.
    """

    __slots__ = ("contact", "capture_transport", "capture_engulf", "capture_by_merger",
                 "direct_insertion", "inc_egress", "transit_raw", "transit",
                 "incorporation_16", "durable_128", "prev_cells", "prev_labels",
                 "hist", "cad", "shell_credit")

    def __init__(self, shape, cadence):
        self.contact = 0.0
        self.capture_transport = 0.0
        self.capture_engulf = 0.0
        self.capture_by_merger = 0.0
        self.direct_insertion = 0.0
        self.inc_egress = 0.0
        self.transit_raw = 0.0
        self.transit = 0.0
        self.incorporation_16 = 0.0
        self.durable_128 = 0.0
        self.prev_cells = None
        self.prev_labels = None
        self.hist = deque()          # (frame, fresh_in_track)
        self.cad = cadence
        self.shell_credit = np.zeros(shape).reshape(-1)

    def window_min(self, frames):
        """Lower bound on fresh mass continuously inside the track over the last `frames`."""
        if not self.hist:
            return 0.0
        t = self.hist[-1][0]
        vals = [v for (f, v) in self.hist if f >= t - frames]
        span = self.hist[-1][0] - self.hist[0][0]
        if span < frames:
            return 0.0
        return min(vals) if vals else 0.0

    def update(self, state, prov, cells, labels, L, frame):
        """Called only at measurement checkpoints, i.e. after a full engine interval."""
        ff = prov.fre.reshape(-1); cr = prov.credited.reshape(-1)
        if cells is None:
            self.prev_cells = None; self.prev_labels = None
            self.hist.clear()
            return
        # -- contact: first passage of fresh matter onto the outer shell --
        for i in outer_shell(cells, L):
            new = ff[i] - self.shell_credit[i]
            if new > 1e-15:
                self.contact += new
                self.shell_credit[i] = ff[i]
        # -- capture: absorbing credit, three-way split --
        prev, plab = self.prev_cells, self.prev_labels
        for i in cells:
            new = ff[i] - cr[i]
            if new <= 1e-15:
                continue
            if prev is None or i in prev:
                self.capture_transport += new
            elif plab is not None and plab.get(i, -1) >= 0:
                self.capture_by_merger += new
            else:
                self.capture_engulf += new
            cr[i] = ff[i]
        # -- residence --
        f_in = float(sum(ff[i] for i in cells))
        self.hist.append((frame, f_in))
        while self.hist and self.hist[0][0] < frame - 128:
            self.hist.popleft()
        self.incorporation_16 = max(self.incorporation_16, self.window_min(16))
        self.durable_128 = max(self.durable_128, self.window_min(128))
        self.prev_cells = set(cells)
        self.prev_labels = labels


def outer_shell(cells, L):
    s = set()
    for i in cells:
        for n in nbrs(i, L):
            if n not in cells:
                s.add(n)
    return s


# ==================================================================== masks
def build_masks_04(cells, L, cy, cx, axis, gd_source):
    """Frozen at t256. sink = downstream half of C256; source halo = graph distance gd_source
    on the upstream side; interface = downstream-facing cells INSIDE C256 (positive control)."""
    dy, dx = AXES[axis]
    yy, xx = np.mgrid[0:L, 0:L]
    proj = ((yy - cy) * dy + (xx - cx) * dx).reshape(-1)
    gd = graph_distance(cells, L)
    sink = sorted([i for i in cells if proj[i] > 0.0], key=lambda i: (-proj[i], i))
    src = sorted([i for i in range(L * L) if gd[i] == gd_source and proj[i] < 0.0],
                 key=lambda i: (proj[i], i))
    interface = sorted([i for i in cells if proj[i] < 0.0], key=lambda i: (proj[i], i))
    return {"sink": sink, "source": src, "source_interface": interface,
            "gd_source": gd_source, "proj": proj, "gd": gd}
