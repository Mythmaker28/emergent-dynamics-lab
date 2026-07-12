"""EXP-RD-04: matched-null false-positive floor + prospective law-14 replication.

Protocol: docs/experiments/EXP_RD_04_PROTOCOL.md (SHA c08a2cc6b1d8233c75db5352b1728a6944f2cd7d), frozen first.
No new laws, no threshold changes, no composites, no post-hoc null redesign.
"""

from __future__ import annotations

from math import comb, sqrt
from typing import Any

import numpy as np

from ..substrates.reaction_diffusion.engine import RDState
from ..substrates.reaction_diffusion.observables import detect_rd_entities, rd_material_retention, \
    rd_phenotype_continuity
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_rd_00 import rates
from .exp_rd_02 import DET, PHE, DELTA, HORIZON, SITE_RADIUS, ORGANIZED_P, TURNOVER_M, PLACEBO_MARGIN, LAGS, wilson
from .exp_rd_03 import REF_CADENCE, FINE_CADENCE, OBS_CADENCES, OBS_SITE_SCALES, enroll_reference, _swap_support

LAW = 14                                    # frozen from the preceding stage. NO new laws.
SEEDS = tuple(range(14001, 14041))          # 40 entirely unseen seeds
MARGIN = 0.10                               # predeclared absolute margin over the null floor
NULL_ARMS = ("NULL_SC", "NULL_NE", "NULL_NE_M")
ARMS = ("INTACT",) + NULL_ARMS


# ---------------------------------------------------------------- cargo constructions
def scramble_cargo(st: RDState, sup: np.ndarray, rng: np.random.Generator) -> RDState:
    """NULL-SC: permute cells INSIDE the support; the SAME permutation for U, V, CU, CV.

    Preserves EXACTLY: total U mass, total V mass, every per-cohort mass, and the full multiset of per-cell
    (U, V, cohort) tuples inside the support. Destroys ONLY the internal spatial organization.
    """
    ys, xs = np.nonzero(sup)
    p = rng.permutation(len(ys))
    out = RDState(st.U.copy(), st.V.copy(), st.CU.copy(), st.CV.copy(), st.step)
    out.U[ys, xs] = st.U[ys[p], xs[p]]
    out.V[ys, xs] = st.V[ys[p], xs[p]]
    out.CU[:, ys, xs] = st.CU[:, ys[p], xs[p]]
    out.CV[:, ys, xs] = st.CV[:, ys[p], xs[p]]
    return out


def non_entity_source(st: RDState, sup: np.ndarray, rng: np.random.Generator) -> np.ndarray | None:
    """A translate of the SAME support geometry onto a region containing no detected entity."""
    n = st.U.shape[0]
    for _ in range(400):
        dy, dx = int(rng.integers(0, n)), int(rng.integers(0, n))
        cand = np.roll(np.roll(sup, dy, 0), dx, 1)
        if cand.sum() != sup.sum():
            continue
        if float(st.V[cand].mean()) < DET.threshold * 0.5 and not np.any(cand & sup):
            return cand
    return None


def mass_match(st: RDState, src: np.ndarray, ref: np.ndarray) -> tuple[RDState, dict[str, float]]:
    """NULL-NE-M: rescale the non-entity cargo so total U mass, total V mass and cohort COMPOSITION equal the
    intact cargo's. Rescaling is NON-CONSERVATIVE by construction; the injected/removed mass is returned."""
    out = RDState(st.U.copy(), st.V.copy(), st.CU.copy(), st.CV.copy(), st.step)
    uS, vS = float(st.U[src].sum()), float(st.V[src].sum())
    uR, vR = float(st.U[ref].sum()), float(st.V[ref].sum())
    su = uR / uS if uS > 1e-12 else 0.0
    sv = vR / vS if vS > 1e-12 else 0.0
    out.U[src] = st.U[src] * su
    out.V[src] = st.V[src] * sv
    # cohort COMPOSITION of the intact cargo, imposed on the rescaled non-entity cargo
    fU = st.CU[:, ref].sum(axis=1); fU = fU / fU.sum() if fU.sum() > 1e-12 else fU
    fV = st.CV[:, ref].sum(axis=1); fV = fV / fV.sum() if fV.sum() > 1e-12 else fV
    out.CU[:, src] = fU[:, None] * out.U[src][None, :]
    out.CV[:, src] = fV[:, None] * out.V[src][None, :]
    return out, {"u_scale": su, "v_scale": sv,
                 "delta_U_mass_injected": uR - uS, "delta_V_mass_injected": vR - vS}


# ---------------------------------------------------------------- readout (detections cached; observers are offline)
def _detections(spec, snaps: list[RDState]):
    out = []
    for s in snaps:
        p, r, a = rates(spec, s)
        out.append((s, detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                          detection=DET, phenotype_spec=PHE)))
    return out


def _score(spec, dets, phi, old_c, new_c, *, cadence: int, site_scale: float) -> dict[str, Any]:
    step = cadence // FINE_CADENCE
    sub = [d for i, d in enumerate(dets) if (i + 1) % step == 0]
    radius = SITE_RADIUS * site_scale
    n = spec.size
    newP, oldP, ents = [], [], []
    for _s, fes in sub:
        def near(site):
            return [e for e in fes
                    if float(np.linalg.norm(minimum_image(np.asarray(e.centroid) - site, n))) <= radius]
        nn, oo = near(new_c), near(old_c)
        newP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in nn), default=0.0))
        oldP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in oo), default=0.0))
        ents.append(max(nn, key=lambda e: e.size) if nn else None)
    cont = False
    valid = [e for e in ents if e is not None]
    for lag in LAGS:
        for i in range(len(valid) - lag):
            if rd_material_retention(valid[i].cohort_mass, valid[i + lag].cohort_mass) < TURNOVER_M:
                cont = True
    return {"n_post": len(sub),
            "frac_new": float(np.mean([p > ORGANIZED_P for p in newP])) if sub else 0.0,
            "frac_old": float(np.mean([p > ORGANIZED_P for p in oldP])) if sub else 0.0,
            "cont": bool(cont)}


def _audited_robust(spec, dets_arm, dets_plac, phi, old_c, new_c, sham_ok: bool) -> dict[str, Any]:
    grid = {}
    for cad in OBS_CADENCES:
        for sc in OBS_SITE_SCALES:
            A = _score(spec, dets_arm, phi, old_c, new_c, cadence=cad, site_scale=sc)
            P = _score(spec, dets_plac, phi, old_c, new_c, cadence=cad, site_scale=sc)
            ok = bool(sham_ok and A["frac_new"] > 0.5 and (A["frac_new"] - P["frac_new"]) > PLACEBO_MARGIN
                      and A["frac_old"] <= 0.5 and A["cont"])
            grid[f"cad{cad}_site{sc}"] = ok
    ref = _score(spec, dets_arm, phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)
    return {"audited_robust": all(grid.values()), "n_settings_audited": sum(grid.values()),
            "ref_frac_new": ref["frac_new"], "ref_frac_old": ref["frac_old"], "ref_cont": ref["cont"],
            "n_post_ref": ref["n_post"]}


# ---------------------------------------------------------------- one matched unit
def matched_unit(seed: int, law_index: int = LAW) -> dict[str, Any]:
    spec, eng, s_star, cand = enroll_reference(law_index, seed)
    if s_star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False}
    n = spec.size
    phi = cand.phenotype
    old_c = np.asarray(cand.centroid)
    new_c = (old_c + np.array(DELTA)) % n
    sup = np.zeros((n, n), dtype=bool)
    sup[cand.cells[:, 0], cand.cells[:, 1]] = True
    rng = np.random.default_rng(900000 + seed)

    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    sham = _swap_support(s_star, sup, 0, 0)
    sham_ok = bool(np.array_equal(sham.U, ctrl.U) and np.array_equal(sham.V, ctrl.V)
                   and np.array_equal(sham.CU, ctrl.CU) and np.array_equal(sham.CV, ctrl.CV))

    # PLACEBO (unchanged from RD-02/03): matched non-candidate support, same cell count, same DELTA
    ys, xs = np.nonzero((~sup) & (s_star.V > DET.threshold * 0.2))
    k = min(int(sup.sum()), len(ys))
    pmask = np.zeros((n, n), dtype=bool)
    if k > 0:
        pmask[ys[:k], xs[:k]] = True
    plac = _swap_support(s_star, pmask, *DELTA) if k > 0 else ctrl

    # arms -- all from s*, same destination, same support geometry, same |DELTA|
    states = {"INTACT": _swap_support(s_star, sup, *DELTA),
              "NULL_SC": _swap_support(scramble_cargo(s_star, sup, rng), sup, *DELTA)}
    src = non_entity_source(s_star, sup, rng)
    meta: dict[str, Any] = {}
    if src is None:
        states["NULL_NE"] = None
        states["NULL_NE_M"] = None
    else:
        states["NULL_NE"] = _swap_support(s_star, src, *DELTA)
        mm, meta = mass_match(s_star, src, sup)
        states["NULL_NE_M"] = _swap_support(mm, src, *DELTA)

    # scrambled cargo must match the intact cargo's low-order statistics EXACTLY
    sc0 = scramble_cargo(s_star, sup, np.random.default_rng(1))
    match_ok = bool(np.isclose(sc0.U[sup].sum(), s_star.U[sup].sum())
                    and np.isclose(sc0.V[sup].sum(), s_star.V[sup].sum())
                    and np.allclose(sc0.CV[:, sup].sum(axis=1), s_star.CV[:, sup].sum(axis=1))
                    and np.allclose(np.sort(sc0.V[sup]), np.sort(s_star.V[sup])))

    dets_plac = _detections(spec, eng.simulate(plac, HORIZON, FINE_CADENCE)[1:])
    dets_ctrl = _detections(spec, eng.simulate(ctrl, HORIZON, FINE_CADENCE)[1:])
    ambient = _score(spec, dets_ctrl, phi, old_c, new_c, cadence=REF_CADENCE, site_scale=1.0)

    out: dict[str, Any] = {
        "law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
        "sham_equals_control": sham_ok, "scrambled_matches_intact_low_order_stats": match_ok,
        "ambient_target_control_frac_new": ambient["frac_new"],
        "ambient_alias_fires": bool(ambient["frac_new"] > 0.5),
        "non_entity_source_found": src is not None, "mass_match": meta, "arms": {},
    }
    for arm in ARMS:
        st = states[arm]
        if st is None:
            out["arms"][arm] = {"censored": True}
            continue
        dets = _detections(spec, eng.simulate(st, HORIZON, FINE_CADENCE)[1:])
        out["arms"][arm] = {"censored": False, **_audited_robust(spec, dets, dets_plac, phi, old_c, new_c, sham_ok)}
    return out


# ---------------------------------------------------------------- predeclared statistics
def newcombe_diff(k1: int, n1: int, k2: int, n2: int, z: float = 1.96) -> tuple[float, float]:
    """Newcombe hybrid-score 95% CI for p1 - p2 (independent proportions)."""
    l1, u1 = wilson(k1, n1, z)
    l2, u2 = wilson(k2, n2, z)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p1 - p2) - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p1 - p2) + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar: binomial(b; b+c, 0.5). b = intact-only successes, c = null-only successes."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)
