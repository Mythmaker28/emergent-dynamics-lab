"""EXP-RD-03: (A) observer-ONLY sensitivity at fixed physics; (B) causal-boundary nested support sweep.

EXP-RD-02's sensitivity test was INVALID: changing the cadence also moved the enrollment time t*, so it perturbed
the physics/enrollment, not just the observer. (It also passed `tracker_scale`, which never enters the causal
readout at all -- a no-op. Both defects are disclosed, and RD-02's eliminations are withdrawn.)

PART A fixes this: ONE physical trajectory per unit, FIXED pre-intervention state, FIXED t* (from the frozen
reference cadence), FIXED branches. Branch snapshots are stored once at the FINEST cadence; the observer is then
varied OFFLINE by subsampling that same stored trajectory and by varying the readout site radius. Nothing physical
changes.

PART B tests the CAUSAL BOUNDARY: a Gray-Scott entity may include its U-depletion field and RD halo, not just the
detected V mask. Nested supports are defined MECHANISTICALLY from the law's own diffusion length
ell = sqrt(Du / F) (cells; dx=dt=1): S0 = detected mask; S1 = mask + 2-cell halo; S2 = mask + ceil(ell);
S3 = mask + ceil(2*ell). U, V AND all passive temporal cohorts inside the support are translated TOGETHER.
No post-hoc halo tuning: the radii follow from (Du, F) alone.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..substrates.reaction_diffusion.engine import RDEngine, RDState
from ..substrates.reaction_diffusion.observables import (
    RDDetectionSpec, RDPhenotypeSpec, detect_rd_entities, rd_material_retention, rd_phenotype_continuity,
)
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_rd_00 import rates
from .exp_rd_00b import rd_state_t
from .exp_rd_01 import EXPRD01Config, TRACER, rd_law_from_halton
from .exp_rd_02 import FROZEN_LAWS, DELTA, WARMUP_SNAP, HORIZON, SITE_RADIUS, ORGANIZED_P, TURNOVER_M, \
    PLACEBO_MARGIN, LAGS, DET, PHE, wilson

REF_CADENCE = 50                      # frozen reference cadence: defines t* ONCE, for ALL observer settings
FINE_CADENCE = 25                     # branches are stored at this cadence; observers subsample it OFFLINE
OBS_CADENCES = (25, 50, 100)          # offline observation cadences (denominators stated per setting)
OBS_SITE_SCALES = (0.8, 1.0, 1.2)     # observer readout site radius scales
SWEEP_SEEDS = tuple(range(13001, 13005))   # 4 UNSEEN seeds per law for the support sweep
PROVISIONAL = [(1, 12007), (7, 12007), (11, 12003), (14, 12001), (14, 12006), (14, 12008)]  # RD-02 6/90


def _disk_offsets(r: int) -> list[tuple[int, int]]:
    out = []
    ri = int(np.ceil(r))
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            if dy * dy + dx * dx <= r * r + 1e-9:
                out.append((dy, dx))
    return out


def dilate_periodic(mask: np.ndarray, r: float) -> np.ndarray:
    if r <= 0:
        return mask.copy()
    out = mask.copy()
    for dy, dx in _disk_offsets(r):
        out |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


def support_radii(law_index: int) -> dict[str, float]:
    """Nested supports from the law's OWN diffusion length ell = sqrt(Du/F) (cells). No tuning."""
    spec, _ = rd_law_from_halton(law_index, EXPRD01Config().size)
    ell = float(np.sqrt(spec.Du / spec.F))
    return {"S0_mask": 0.0, "S1_small_halo": 2.0,
            "S2_one_diffusion_length": float(np.ceil(ell)),
            "S3_two_diffusion_lengths": float(np.ceil(2 * ell)), "ell": ell}


def _swap_support(st: RDState, support: np.ndarray, dy: int, dx: int) -> RDState:
    """Translate U, V and ALL passive cohorts inside `support` together (conservative swap with the target site)."""
    n = st.U.shape[0]
    ys, xs = np.nonzero(support)
    ty, tx = (ys + dy) % n, (xs + dx) % n
    U = st.U.copy(); V = st.V.copy(); CU = st.CU.copy(); CV = st.CV.copy()
    U[ys, xs] = st.U[ty, tx]; U[ty, tx] = st.U[ys, xs]
    V[ys, xs] = st.V[ty, tx]; V[ty, tx] = st.V[ys, xs]
    CU[:, ys, xs] = st.CU[:, ty, tx]; CU[:, ty, tx] = st.CU[:, ys, xs]
    CV[:, ys, xs] = st.CV[:, ty, tx]; CV[:, ty, tx] = st.CV[:, ys, xs]
    return RDState(U, V, CU, CV, st.step)


def enroll_reference(law_index: int, seed: int):
    """Enrol ONCE at the frozen reference cadence -> a FIXED t* used by every observer setting and every support."""
    cfg = EXPRD01Config()
    spec, _ = rd_law_from_halton(law_index, cfg.size)
    eng = RDEngine(spec, TRACER)
    cur = rd_state_t(spec, TRACER, seed)
    for t in range(0, cfg.steps + 1):
        if t % REF_CADENCE == 0 and t >= WARMUP_SNAP * REF_CADENCE:
            p, r, a = rates(spec, cur)
            fes = detect_rd_entities(cur.U, cur.V, cur.CV, p, r, a, snapshot_step=t, time=float(t),
                                     detection=DET, phenotype_spec=PHE)
            if fes:
                big = max(fes, key=lambda e: e.size)
                if big.size >= 3 * DET.min_cells:
                    return spec, eng, RDState(cur.U.copy(), cur.V.copy(), cur.CU.copy(), cur.CV.copy(), t), big
        if t == cfg.steps:
            break
        cur = eng.step(cur)
    return spec, eng, None, None


def _branch_snapshots(eng: RDEngine, state0: RDState) -> list[RDState]:
    return eng.simulate(state0, HORIZON, FINE_CADENCE)[1:]     # stored ONCE at the finest cadence


def _readout(spec, snaps: list[RDState], phi, old_c, new_c, *, cadence: int, site_scale: float) -> dict[str, Any]:
    """OFFLINE observer: subsample the SAME stored physical trajectory; vary only cadence and site radius."""
    step = cadence // FINE_CADENCE
    sub = [s for i, s in enumerate(snaps) if (i + 1) % step == 0]
    denom = len(sub)
    radius = SITE_RADIUS * site_scale
    n = spec.size
    newP = []; oldP = []; new_ents = []
    for s in sub:
        p, r, a = rates(spec, s)
        fes = detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                 detection=DET, phenotype_spec=PHE)
        def near(site):
            return [e for e in fes if float(np.linalg.norm(minimum_image(np.asarray(e.centroid) - site, n))) <= radius]
        nn = near(new_c); oo = near(old_c)
        newP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in nn), default=0.0))
        oldP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in oo), default=0.0))
        new_ents.append(max(nn, key=lambda e: e.size) if nn else None)
    cont = False; minM = 1.0
    valid = [e for e in new_ents if e is not None]
    for lag in LAGS:
        for i in range(len(valid) - lag):
            m = rd_material_retention(valid[i].cohort_mass, valid[i + lag].cohort_mass)
            minM = min(minM, m)
            if m < TURNOVER_M:
                cont = True
    return {"n_post": denom,
            "frac_new_organized": float(np.mean([p > ORGANIZED_P for p in newP])) if denom else 0.0,
            "frac_old_organized": float(np.mean([p > ORGANIZED_P for p in oldP])) if denom else 0.0,
            "continued_turnover": bool(cont), "min_M_post": float(minM)}


def _classify(P, PL, sham_ok):
    reest = P["frac_new_organized"] > 0.5
    exceeds = (P["frac_new_organized"] - PL["frac_new_organized"]) > PLACEBO_MARGIN
    occupancy = P["frac_old_organized"] > 0.5
    audited = bool(sham_ok and reest and exceeds and (not occupancy) and P["continued_turnover"])
    if not reest: cls = "destroyed_or_no_reestablishment"
    elif not exceeds: cls = "placebo_failure"
    elif occupancy: cls = "occupancy_alias"
    elif not P["continued_turnover"]: cls = "frozen_lump"
    else: cls = "AUDITED"
    return cls, audited


# ------------------------------------------------------------------ PART A: observer-ONLY sensitivity
def observer_only_sensitivity(law_index: int, seed: int) -> dict[str, Any]:
    spec, eng, s_star, cand = enroll_reference(law_index, seed)
    if s_star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False}
    phi = cand.phenotype; old_c = np.asarray(cand.centroid); n = spec.size
    new_c = (old_c + np.array(DELTA)) % n
    mask = np.zeros((n, n), dtype=bool); mask[cand.cells[:, 0], cand.cells[:, 1]] = True
    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    sham = _swap_support(s_star, mask, 0, 0)
    pert = _swap_support(s_star, mask, DELTA[0], DELTA[1])
    occ = mask.copy()
    ys, xs = np.nonzero(~occ & (s_star.V > DET.threshold * 0.2))
    k = min(int(mask.sum()), len(ys))
    pmask = np.zeros((n, n), dtype=bool)
    if k > 0: pmask[ys[:k], xs[:k]] = True
    plac = _swap_support(s_star, pmask, DELTA[0], DELTA[1]) if k > 0 else ctrl
    sham_ok = bool(np.array_equal(sham.U, ctrl.U) and np.array_equal(sham.V, ctrl.V) and np.array_equal(sham.CV, ctrl.CV))
    snapsP = _branch_snapshots(eng, pert); snapsPL = _branch_snapshots(eng, plac)   # PHYSICS COMPUTED ONCE
    grid = {}
    for cad in OBS_CADENCES:
        for sc in OBS_SITE_SCALES:
            P = _readout(spec, snapsP, phi, old_c, new_c, cadence=cad, site_scale=sc)
            PL = _readout(spec, snapsPL, phi, old_c, new_c, cadence=cad, site_scale=sc)
            cls, aud = _classify(P, PL, sham_ok)
            grid[f"cad{cad}_site{sc}"] = {"audited": aud, "cls": cls, "denom": P["n_post"],
                                          "frac_new": P["frac_new_organized"], "frac_old": P["frac_old_organized"],
                                          "cont": P["continued_turnover"]}
    n_aud = sum(1 for v in grid.values() if v["audited"])
    return {"law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
            "sham_equals_control": sham_ok, "grid": grid, "n_settings": len(grid), "n_audited_settings": n_aud,
            "robust_all_settings": n_aud == len(grid)}


# ------------------------------------------------------------------ PART B: causal-boundary support sweep
def support_sweep(law_index: int, seed: int) -> dict[str, Any]:
    spec, eng, s_star, cand = enroll_reference(law_index, seed)
    if s_star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False}
    phi = cand.phenotype; old_c = np.asarray(cand.centroid); n = spec.size
    new_c = (old_c + np.array(DELTA)) % n
    mask = np.zeros((n, n), dtype=bool); mask[cand.cells[:, 0], cand.cells[:, 1]] = True
    radii = support_radii(law_index)
    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    sham = _swap_support(s_star, mask, 0, 0)
    sham_ok = bool(np.array_equal(sham.U, ctrl.U) and np.array_equal(sham.V, ctrl.V) and np.array_equal(sham.CV, ctrl.CV))
    out = {}
    for name in ("S0_mask", "S1_small_halo", "S2_one_diffusion_length", "S3_two_diffusion_lengths"):
        r = radii[name]
        sup = dilate_periodic(mask, r)
        pert = _swap_support(s_star, sup, DELTA[0], DELTA[1])
        # PLACEBO: a matched non-candidate support of the SAME cell count, displaced identically
        avail = (~sup) & (s_star.V > DET.threshold * 0.2)
        ys, xs = np.nonzero(avail)
        k = min(int(sup.sum()), len(ys))
        pmask = np.zeros((n, n), dtype=bool)
        if k > 0: pmask[ys[:k], xs[:k]] = True
        plac = _swap_support(s_star, pmask, DELTA[0], DELTA[1]) if k > 0 else ctrl
        P = _readout(spec, _branch_snapshots(eng, pert), phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)
        PL = _readout(spec, _branch_snapshots(eng, plac), phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)
        cls, aud = _classify(P, PL, sham_ok)
        out[name] = {"radius_cells": r, "support_cells": int(sup.sum()), "mask_cells": int(mask.sum()),
                     "classification": cls, "audited": aud, "n_post": P["n_post"],
                     "frac_new": P["frac_new_organized"], "frac_old": P["frac_old_organized"],
                     "placebo_frac_new": PL["frac_new_organized"], "cont_turnover": P["continued_turnover"]}
    return {"law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
            "sham_equals_control": sham_ok, "ell_cells": radii["ell"], "supports": out}


def observer_only_sensitivity_support(law_index: int, seed: int, support_name: str) -> dict[str, Any]:
    """PART A observer-only sensitivity applied to a PART B support (same fixed physics / fixed t* discipline)."""
    spec, eng, s_star, cand = enroll_reference(law_index, seed)
    if s_star is None:
        return {"law_index": law_index, "seed": seed, "support": support_name, "enrolled": False}
    phi = cand.phenotype; old_c = np.asarray(cand.centroid); n = spec.size
    new_c = (old_c + np.array(DELTA)) % n
    mask = np.zeros((n, n), dtype=bool); mask[cand.cells[:, 0], cand.cells[:, 1]] = True
    sup = dilate_periodic(mask, support_radii(law_index)[support_name])
    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    sham_ok = bool(np.array_equal(_swap_support(s_star, sup, 0, 0).U, ctrl.U))
    pert = _swap_support(s_star, sup, DELTA[0], DELTA[1])
    avail = (~sup) & (s_star.V > DET.threshold * 0.2)
    ys, xs = np.nonzero(avail); k = min(int(sup.sum()), len(ys))
    pmask = np.zeros((n, n), dtype=bool)
    if k > 0: pmask[ys[:k], xs[:k]] = True
    plac = _swap_support(s_star, pmask, DELTA[0], DELTA[1]) if k > 0 else ctrl
    snapsP = _branch_snapshots(eng, pert); snapsPL = _branch_snapshots(eng, plac)
    grid = {}
    for cad in OBS_CADENCES:
        for sc in OBS_SITE_SCALES:
            P = _readout(spec, snapsP, phi, old_c, new_c, cadence=cad, site_scale=sc)
            PL = _readout(spec, snapsPL, phi, old_c, new_c, cadence=cad, site_scale=sc)
            cls, aud = _classify(P, PL, sham_ok)
            grid[f"cad{cad}_site{sc}"] = {"audited": aud, "cls": cls}
    n_aud = sum(1 for v in grid.values() if v["audited"])
    return {"law_index": law_index, "seed": seed, "support": support_name, "enrolled": True,
            "t_star": int(s_star.step), "n_settings": len(grid), "n_audited_settings": n_aud,
            "robust_all_settings": n_aud == len(grid), "grid": grid}


def ambient_alias_null(law_index: int, seed: int, support_name: str = "S0_mask") -> dict[str, Any]:
    """AMBIENT-SPOT NULL (EXP-RD-04 preview).

    Gray-Scott spots are near-identical and self-replicating: the lattice tends to fill with look-alikes.
    PLACEBO controls for *displacing something*; it never asks whether the CONTROL branch -- in which NOTHING
    is displaced -- also grows a phenotype-matching structure at the target site (old_centroid + DELTA).
    If it does, every 'causal re-establishment' is an ambient-field alias.
    """
    spec, eng, s_star, cand = enroll_reference(law_index, seed)
    if s_star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False}
    phi = cand.phenotype; old_c = np.asarray(cand.centroid); n = spec.size
    new_c = (old_c + np.array(DELTA)) % n
    mask = np.zeros((n, n), dtype=bool); mask[cand.cells[:, 0], cand.cells[:, 1]] = True
    sup = dilate_periodic(mask, support_radii(law_index)[support_name])
    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    pert = _swap_support(s_star, sup, DELTA[0], DELTA[1])
    C = _readout(spec, _branch_snapshots(eng, ctrl), phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)
    P = _readout(spec, _branch_snapshots(eng, pert), phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)
    return {"law_index": law_index, "seed": seed, "support": support_name, "enrolled": True,
            "control_frac_new_organized": C["frac_new_organized"],
            "perturbed_frac_new_organized": P["frac_new_organized"],
            "control_alias_fires": bool(C["frac_new_organized"] > 0.5),
            "perturbed_minus_control": P["frac_new_organized"] - C["frac_new_organized"],
            "n_post": C["n_post"]}
