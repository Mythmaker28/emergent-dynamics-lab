"""MCM01 instrumentation: the exact c_X recorder, per-component logging, and the temporal gates.

THE KINETICS ARE NOT TOUCHED. `kinetics.py` is byte-identical to `MTW01/code/mtw.py`
(sha256 d6b9e24d…f026c4c4), which carries the MINCORE species set, reaction scheme, candidate
rule, decay, feed, outflow and update order unchanged. `RecWorld` subclasses it and overrides
`_react` and `_decay` ONLY to read the state immediately before and immediately after each
sub-step. The recorder draws no random number and writes no field, so the law of the process is
unchanged; `tests_mcm.py` proves this by comparing state hashes with and without it.

THE EXACT DEFINITION OF c_X
---------------------------
`_react` computes, per cell,  cand_X = min(n[SX], max(free, 0))  with free = CAP - occupancy,
and then draws  births_X ~ Binomial(cand_X, min(1, kX*nX*nY)).

    c_X(t) := cand_X evaluated at the organiser's cell, at the reaction sub-step of step t

It is therefore literally the `n` parameter of the binomial draw the engine is about to make at
the only cell where body molecules can be created. It is an integer, it is per step, it is
strictly local (one cell), and it is read, not modelled. With several organiser cells the
recorder reports both the sum over those cells and the value per organiser.
"""
from __future__ import annotations

import math

import numpy as np

import kinetics as K
from kinetics import ALL_OCC

SPECIES_ORDER = ("X", "Y", "SX", "SY", "WX", "WY")


# ==================================================================== the recorder
class Recorder:
    """Write-only. Reads the world, never modifies it, never consumes randomness."""

    FIELDS = ("step", "N_X", "N_Y", "N_SX", "N_SY", "N_WX", "N_WY",
              "n_org_cells", "c_X_total", "c_X_per_org", "u_nX_at_org", "nSX_at_org",
              "nSY_at_org", "nW_at_org", "free_at_org", "p_X_at_org",
              "expected_births_X", "accepted_births_X", "deaths_X",
              "cand_Y_at_org", "Q", "source_on",
              "O_total", "free_total", "flux_in", "flux_out", "occ_delta",
              "free_at_source_mean", "displaced_total")

    def __init__(self):
        self.rows = []
        self._pending = None

    # ---- called at the top of _react, on the post-diffusion pre-reaction state
    def pre_react(self, w):
        sp = w.sp
        nX, nY, nSX, nSY = w.n["X"], w.n["Y"], w.n["SX"], w.n["SY"]
        free = np.maximum(w.free(), 0)
        m = nY > 0
        k = int(m.sum())
        if k:
            cx = np.minimum(nSX[m], free[m])                 # EXACTLY the engine's cand_X
            cy = np.minimum(nSY[m], free[m])
            px = np.minimum(1.0, sp.kX * nX[m] * nY[m])
            row = {"n_org_cells": k,
                   "c_X_total": float(cx.sum()), "c_X_per_org": float(cx.sum() / nY[m].sum()),
                   "u_nX_at_org": float(nX[m].sum() / k), "nSX_at_org": float(nSX[m].mean()),
                   "nSY_at_org": float(nSY[m].mean()), "free_at_org": float(free[m].mean()),
                   "nW_at_org": float((w.n["WX"][m] + w.n["WY"][m]).mean()),
                   "p_X_at_org": float(px.mean()),
                   "expected_births_X": float((cx * px).sum()),
                   "cand_Y_at_org": float(cy.sum()),
                   "Q": float((nX[m] * cy).sum()),
                   "source_on": float((nX[m] >= 1).any())}
        else:
            row = {"n_org_cells": 0, "c_X_total": 0.0, "c_X_per_org": 0.0, "u_nX_at_org": 0.0,
                   "nSX_at_org": 0.0, "nSY_at_org": 0.0, "free_at_org": 0.0, "nW_at_org": 0.0,
                   "p_X_at_org": 0.0, "expected_births_X": 0.0, "cand_Y_at_org": 0.0,
                   "Q": 0.0, "source_on": 0.0}
        row["_NX_before_react"] = int(nX.sum())
        self._pending = row

    def post_react(self, w):
        self._pending["accepted_births_X"] = int(w.n["X"].sum()) - self._pending.pop(
            "_NX_before_react")

    def pre_decay(self, w):
        self._pending["_NX_before_decay"] = int(w.n["X"].sum())

    def post_decay(self, w):
        self._pending["deaths_X"] = self._pending.pop("_NX_before_decay") - int(w.n["X"].sum())

    def close_step(self, w):
        r = self._pending
        r["step"] = int(w.step)
        for s, key in (("X", "N_X"), ("Y", "N_Y"), ("SX", "N_SX"), ("SY", "N_SY"),
                       ("WX", "N_WX"), ("WY", "N_WY")):
            r[key] = int(w.n[s].sum())
        occ = w.occ()
        r["O_total"] = int(occ.sum())
        r["free_total"] = int(np.maximum(w.sp.CAP - occ, 0).sum())
        r["flux_in"] = int(getattr(w, "flux_in", 0))
        r["flux_out"] = int(getattr(w, "flux_out", 0))
        r["occ_delta"] = int(getattr(w, "_last_occ_delta", 0))
        r["free_at_source_mean"] = float(np.maximum(w.sp.CAP - occ, 0).mean())
        r["displaced_total"] = int(sum(getattr(w, "displaced", {}).values()))
        self.rows.append([r.get(f, 0.0) for f in self.FIELDS])
        self._pending = None

    def array(self):
        return np.asarray(self.rows, dtype=np.float64)

    def col(self, name):
        return self.array()[:, self.FIELDS.index(name)]


class RecWorld(K.World):
    def __init__(self, L=None, seed=0, sp=K.Spec, rec=None):
        super().__init__(L=L, seed=seed, sp=sp)
        self.rec = rec

    def _react(self):
        if self.rec is not None:
            self.rec.pre_react(self)
        super()._react()
        if self.rec is not None:
            self.rec.post_react(self)

    def _decay(self):
        if self.rec is not None:
            self.rec.pre_decay(self)
        super()._decay()
        if self.rec is not None:
            self.rec.post_decay(self)

    def _one_step(self):
        super()._one_step()
        if self.rec is not None:
            self.rec.close_step(self)


def spec_with(**over):
    d = dict(K.Spec.as_dict())
    d.update(over)
    return type("SpecVariant", (K.Spec,), d)


def fresh_world(seed, sp, rec=None, L=None):
    w = RecWorld(L=L, seed=seed, sp=sp, rec=rec)
    w.n["SX"][:] = sp.S0
    w.n["SY"][:] = sp.S0
    return w


def seed_one_organiser(w, x_seed):
    """One organiser at the centre of the torus with x_seed body molecules in the same cell.
    Nothing is copied, no boundary is drawn, no cell is divided."""
    c = w.L // 2
    w.n["Y"][c, c] = 1
    w.n["X"][c, c] = int(x_seed)
    return (c, c)


# ==================================================================== components, on a torus
def components_torus(mask):
    L = mask.shape[0]
    lab = -np.ones(mask.shape, dtype=np.int64)
    comps = []
    for y0 in range(L):
        for x0 in range(L):
            if not mask[y0, x0] or lab[y0, x0] >= 0:
                continue
            cid = len(comps)
            lab[y0, x0] = cid
            stack, cells = [(y0, x0)], []
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    na, nb = (a + da) % L, (b + db) % L
                    if mask[na, nb] and lab[na, nb] < 0:
                        lab[na, nb] = cid
                        stack.append((na, nb))
            comps.append(cells)
    return comps, lab


def _circular_stats(idx, wts, L):
    """Centre of mass and spread on a circle, via the angular mean. Exact on a torus."""
    th = 2.0 * math.pi * idx / L
    c = float((wts * np.cos(th)).sum())
    s = float((wts * np.sin(th)).sum())
    com = (math.atan2(s, c) % (2.0 * math.pi)) * L / (2.0 * math.pi)
    Rbar = math.hypot(c, s) / max(wts.sum(), 1e-12)
    circ_var = 1.0 - Rbar
    return com, circ_var


ESCAPEE_MAX_MASS = 2          # a component carrying no organiser and total mass <= this


def component_report(w):
    """Full per-component record. Every field is read from the state, none is reconstructed."""
    L = w.L
    nX, nY = w.n["X"], w.n["Y"]
    occupied = (nX + nY) > 0
    comps, lab = components_torus(occupied)
    out, escapees = [], []
    for cid, cells in enumerate(comps):
        ys = np.array([c[0] for c in cells])
        xs = np.array([c[1] for c in cells])
        cx_ = nX[ys, xs].astype(float)
        cy_ = nY[ys, xs].astype(float)
        mass = float(cx_.sum() + cy_.sum())
        wts = cx_ + cy_
        comy, vary = _circular_stats(ys, wts, L)
        comx, varx = _circular_stats(xs, wts, L)
        # extent measured on the torus, from the circular centre of mass
        dy = np.minimum(np.abs(ys - comy), L - np.abs(ys - comy))
        dx = np.minimum(np.abs(xs - comx), L - np.abs(xs - comx))
        rad = float(np.sqrt(((dy ** 2 + dx ** 2) * wts).sum() / max(wts.sum(), 1e-12)))
        ext = float(max(dy.max(), dx.max()) * 2.0 + 1.0)
        rec = {"id": cid, "cells": len(cells), "N_X": int(cx_.sum()), "N_Y": int(cy_.sum()),
               "mass": mass, "density": mass / max(len(cells), 1),
               "com_y": comy, "com_x": comx, "radius_of_gyration": rad,
               "extent": ext, "circular_variance_y": vary, "circular_variance_x": varx,
               "gap_to_own_periodic_image": float(L - ext),
               "wraps": bool(ext >= L * 0.5)}
        (escapees if (rec["N_Y"] == 0 and mass <= ESCAPEE_MAX_MASS) else out).append(rec)
    out.sort(key=lambda r: -r["mass"])
    return {"components": out, "escapees": escapees,
            "n_components": len(out), "n_escapees": len(escapees), "n_raw": len(comps),
            "main": out[0] if out else None,
            "N_X_total": int(nX.sum()), "N_Y_total": int(nY.sum()),
            "free_total": int(np.maximum(w.free(), 0).sum()),
            "N_SX_total": int(w.n["SX"].sum()), "N_SY_total": int(w.n["SY"].sum()),
            "step": int(w.step)}


# ==================================================================== the temporal gates
def formation_gate(rec_arr, F, T_FORM_MAX, N_FORM, U_FORM, K_FORM):
    """The cloud must reach N_X >= N_FORM and u >= U_FORM for K_FORM CONSECUTIVE steps, before
    T_FORM_MAX. Returns the step at which formation completes, or None."""
    NX = rec_arr[:, F.index("N_X")]
    U = rec_arr[:, F.index("u_nX_at_org")]
    ok = (NX >= N_FORM) & (U >= U_FORM)
    run = 0
    for i in range(min(len(ok), int(T_FORM_MAX))):
        run = run + 1 if ok[i] else 0
        if run >= K_FORM:
            return i + 1                                   # step index (1-based, = w.step)
    return None


def persistence_gate(rec_arr, F, t0, T_MAINT, N_KEEP, FRAC_MIN, RUN_MAX, G0, CRIT_FRAC,
                     comp_samples):
    """Evaluated over the whole window [t0, t0 + T_MAINT). Not a single instant, and not only a
    time average: the longest consecutive excursion below threshold is bounded too."""
    lo, hi = int(t0), int(t0 + T_MAINT)
    if len(rec_arr) < hi:
        return {"PASS": False, "reason": "window truncated: %d rows, need %d"
                % (len(rec_arr), hi), "checks": {}}
    seg = rec_arr[lo:hi]
    NX = seg[:, F.index("N_X")]
    NY = seg[:, F.index("N_Y")]
    CX = seg[:, F.index("c_X_per_org")]
    below = NX < N_KEEP
    longest, run = 0, 0
    for b in below:
        run = run + 1 if b else 0
        longest = max(longest, run)
    crit = CX * G0
    samples = [s for s in comp_samples if lo <= s["step"] < hi]
    main_ok = all(s["main"] is not None and s["main"]["N_X"] >= N_KEEP * 0.5 for s in samples)
    wrap_ok = all(not (s["main"] or {}).get("wraps", True) for s in samples)
    checks = {
        "never_extinct": bool((NX > 0).all()),
        "organiser_present_throughout": bool((NY >= 1).all()),
        "fraction_of_steps_at_or_above_N_KEEP": float((~below).mean()),
        "fraction_ok": bool((~below).mean() >= FRAC_MIN),
        "longest_consecutive_excursion": int(longest),
        "excursion_ok": bool(longest <= RUN_MAX),
        "fraction_of_steps_with_cX_G0_above_1": float((crit > 1.0).mean()),
        "criticality_ok": bool((crit > 1.0).mean() >= CRIT_FRAC),
        "main_component_carries_the_mass": bool(main_ok),
        "no_wrap_around_contact": bool(wrap_ok),
        "n_component_samples": len(samples),
    }
    hard = ("never_extinct", "organiser_present_throughout", "fraction_ok", "excursion_ok",
            "criticality_ok", "main_component_carries_the_mass", "no_wrap_around_contact")
    return {"PASS": bool(all(checks[k] for k in hard)), "checks": checks,
            "stats": {"N_X_min": float(NX.min()), "N_X_median": float(np.median(NX)),
                      "N_X_mean": float(NX.mean()), "N_X_max": float(NX.max()),
                      "c_X_min": float(CX.min()), "c_X_q05": float(np.quantile(CX, 0.05)),
                      "c_X_q25": float(np.quantile(CX, 0.25)),
                      "c_X_median": float(np.median(CX)), "c_X_mean": float(CX.mean()),
                      "c_X_G0_median": float(np.median(crit))}}


END_CLASSES = ("NO_FORMATION", "TRANSIENT_FORMATION", "MAINTENANCE_ACHIEVED",
               "MATERIAL_COLLAPSE", "ORGANISATION_LOST", "BOUNDARY_ARTEFACT",
               "PROTOCOL_VIOLATION", "ENGINE_ERROR", "UNCLASSIFIABLE")


def classify(formed_at, pers, rec_arr, F, comp_samples):
    """Exhaustive, mutually exclusive, evaluated in a fixed order."""
    if formed_at is None:
        NX = rec_arr[:, F.index("N_X")]
        return "NO_FORMATION" if NX.max() < 2 else "TRANSIENT_FORMATION"
    if pers.get("PASS"):
        return "MAINTENANCE_ACHIEVED"
    c = pers.get("checks", {})
    if not c:
        return "UNCLASSIFIABLE"
    if not c.get("no_wrap_around_contact", True):
        return "BOUNDARY_ARTEFACT"
    if not c.get("organiser_present_throughout", True):
        return "ORGANISATION_LOST"
    if not c.get("never_extinct", True):
        return "MATERIAL_COLLAPSE"
    if not (c.get("fraction_ok", True) and c.get("excursion_ok", True)):
        return "TRANSIENT_FORMATION"
    if not c.get("criticality_ok", True):
        return "MATERIAL_COLLAPSE"
    if not c.get("main_component_carries_the_mass", True):
        return "ORGANISATION_LOST"
    return "UNCLASSIFIABLE"
