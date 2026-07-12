"""EXP-RD-02: frozen downstream chain for the 9 OPEN screening-permitted laws.

Order (frozen, no shortcuts): fresh-seed hold-out -> direct alias audit -> same-state matched-branch causal
intervention -> observer sensitivity -> adversarial re-audit. Nothing is a candidate until all pass.
Laws are FROZEN; never ranked, replaced or visually selected. Thresholds, tracer, P/M and mechanism unchanged.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.reaction_diffusion.engine import RDEngine, RDState
from ..substrates.reaction_diffusion.observables import (
    RDDetectionSpec, RDPhenotypeSpec, detect_rd_entities, to_entity_observation,
    rd_material_retention, rd_phenotype_continuity,
)
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_rd_00 import rates
from .exp_rd_00b import rd_state_t
from .exp_rd_01 import EXPRD01Config, TRACER, rd_law_from_halton, screen_one

FROZEN_LAWS = (1, 5, 7, 10, 11, 13, 14, 16, 19)     # FROZEN from D-030; no ranking/replacement/selection
HOLDOUT_SEEDS = (11001, 11002, 11003, 11004, 11005)  # unseen; frozen >=2/5 gate
CAUSAL_SEEDS = tuple(range(12001, 12011))            # 10 UNSEEN causal seeds per surviving law

# --- frozen causal parameters
DELTA = (20, 20)          # displacement (cells)
WARMUP_SNAP = 8           # enrol at the first snapshot after warmup with a structure of size >= 3*min_cells
HORIZON = 750             # post-intervention steps
CADENCE = 50              # -> N_POST = actual post snapshot count (stated explicitly per run)
SITE_RADIUS = 10.0
ORGANIZED_P = 0.8         # frozen
TURNOVER_M = 0.5          # frozen
PLACEBO_MARGIN = 0.25     # corrected placebo criterion (kept)
LAGS = (1, 3, 6)
DET = RDDetectionSpec(); PHE = RDPhenotypeSpec()


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def holdout_run(law_index: int, seed: int) -> dict[str, Any]:
    return screen_one(EXPRD01Config(), law_index, "OPEN", seed)


# ---------------------------------------------------------------- alias audit

def alias_audit(law_index: int, seed: int) -> dict[str, Any]:
    """Targets: fragmentation, dissolution/reformation, spatial occupancy, tracker churn."""
    cfg = EXPRD01Config()
    open_spec, _ = rd_law_from_halton(law_index, cfg.size)
    eng = RDEngine(open_spec, TRACER)
    snaps = eng.simulate(rd_state_t(open_spec, TRACER, seed), cfg.steps, cfg.cadence)
    trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=open_spec.size)
    per: dict[int, list] = {}
    n_ent = []
    for s in snaps:
        p, r, a = rates(open_spec, s)
        fes = detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                 detection=DET, phenotype_spec=PHE)
        n_ent.append(len(fes))
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by = {e.local_index: e for e in fes}
        for to in tracked:
            per.setdefault(to.track_id, []).append(by[to.entity.local_index])
    complex_tracks: set[int] = set()
    ev = {"split": 0, "merge": 0, "ambiguous_association": 0, "birth": 0, "disappearance": 0}
    for e in trk.events:
        ev[e.kind] = ev.get(e.kind, 0) + 1
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    # eligible track (clean, long, probe-positive)
    best = None
    for tid, fes in per.items():
        if tid in complex_tracks or len(fes) < cfg.enroll_min_obs:
            continue
        for lag in LAGS:
            for i in range(len(fes) - lag):
                p_ = rd_phenotype_continuity(fes[i].phenotype, fes[i + lag].phenotype)
                m_ = rd_material_retention(fes[i].cohort_mass, fes[i + lag].cohort_mass)
                if p_ > ORGANIZED_P and m_ < TURNOVER_M:
                    best = (tid, fes); break
            if best: break
        if best: break
    churn = ev["birth"] + ev["disappearance"]
    if best is None:
        return {"law_index": law_index, "seed": seed, "eligible": False,
                "n_tracks": len(per), "churn_events": churn, "mean_entities": float(np.mean(n_ent))}
    tid, fes = best
    mass = np.array([f.phenotype.raw["v_mass"] for f in fes])
    cents = np.array([f.centroid for f in fes])
    n = open_spec.size
    net = float(np.linalg.norm(minimum_image(cents[-1] - cents[0], n)))
    path = float(sum(np.linalg.norm(minimum_image(cents[i + 1] - cents[i], n)) for i in range(len(cents) - 1)))
    dissolution = bool(mass.min() / max(np.median(mass), 1e-12) < 0.35)
    stationary = bool(net < 3.0)
    return {"law_index": law_index, "seed": seed, "eligible": True, "track_obs": len(fes),
            "mass_median": float(np.median(mass)), "mass_cv": float(mass.std() / max(mass.mean(), 1e-12)),
            "mass_min_over_median": float(mass.min() / max(np.median(mass), 1e-12)),
            "net_displacement": net, "path_length": path,
            "n_tracks": len(per), "mean_entities": float(np.mean(n_ent)),
            "churn_events": churn, "split": ev["split"], "merge": ev["merge"],
            "ambiguous": ev["ambiguous_association"],
            "dissolution_alias": dissolution, "stationary_occupancy_suspect": stationary}


# ---------------------------------------------------------------- causal intervention

def _swap_cells(st: RDState, cells: np.ndarray, dy: int, dx: int) -> RDState:
    """Conservative displacement: SWAP the full local state (U,V,CU,CV) of `cells` with the cells shifted by
    (dy,dx). Zero displacement is an EXACT no-op (used for SHAM)."""
    n = st.U.shape[0]
    ys, xs = cells[:, 0], cells[:, 1]
    ty, tx = (ys + dy) % n, (xs + dx) % n
    U = st.U.copy(); V = st.V.copy(); CU = st.CU.copy(); CV = st.CV.copy()
    for A, B in ((U, st.U), (V, st.V)):
        A[ys, xs] = B[ty, tx]; A[ty, tx] = B[ys, xs]
    CU[:, ys, xs] = st.CU[:, ty, tx]; CU[:, ty, tx] = st.CU[:, ys, xs]
    CV[:, ys, xs] = st.CV[:, ty, tx]; CV[:, ty, tx] = st.CV[:, ys, xs]
    return RDState(U, V, CU, CV, st.step)


def causal_unit(law_index: int, seed: int, cadence: int = CADENCE, tracker_scale: float = 1.0) -> dict[str, Any]:
    cfg = EXPRD01Config()
    open_spec, _ = rd_law_from_halton(law_index, cfg.size)
    eng = RDEngine(open_spec, TRACER)
    st = rd_state_t(open_spec, TRACER, seed)
    # enrol
    cur = st; star = None
    for t in range(0, cfg.steps + 1):
        if t % cadence == 0 and t >= WARMUP_SNAP * cadence:
            p, r, a = rates(open_spec, cur)
            fes = detect_rd_entities(cur.U, cur.V, cur.CV, p, r, a, snapshot_step=t, time=float(t),
                                     detection=DET, phenotype_spec=PHE)
            if fes:
                big = max(fes, key=lambda e: e.size)
                if big.size >= 3 * DET.min_cells:
                    star = (RDState(cur.U.copy(), cur.V.copy(), cur.CU.copy(), cur.CV.copy(), t), big); break
        if t == cfg.steps:
            break
        cur = eng.step(cur)
    if star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False, "reason": "no_structure"}
    s_star, cand = star
    phi = cand.phenotype; old_c = np.asarray(cand.centroid)
    n = open_spec.size
    new_c = (old_c + np.array(DELTA)) % n
    trk_spec = TrackerSpec(8.0 * tracker_scale, 0.25)

    def branch(state0: RDState):
        out = eng.simulate(state0, HORIZON, cadence)[1:]
        denom = len(out)
        newP = []; oldP = []; new_ents = []
        for s in out:
            p, r, a = rates(open_spec, s)
            fes = detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                     detection=DET, phenotype_spec=PHE)
            def near(site):
                return [e for e in fes if float(np.linalg.norm(minimum_image(np.asarray(e.centroid) - site, n))) <= SITE_RADIUS]
            nn = near(new_c); oo = near(old_c)
            newP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in nn), default=0.0))
            oldP.append(max((rd_phenotype_continuity(phi, e.phenotype) for e in oo), default=0.0))
            new_ents.append(max(nn, key=lambda e: e.size) if nn else None)
        # CONTINUED TEMPORAL-COHORT TURNOVER of the re-established structure (frozen M, frozen lags)
        cont = False; minM = 1.0
        valid = [e for e in new_ents if e is not None]
        for lag in LAGS:
            for i in range(len(valid) - lag):
                m = rd_material_retention(valid[i].cohort_mass, valid[i + lag].cohort_mass)
                minM = min(minM, m)
                if m < TURNOVER_M:
                    cont = True
        return {"n_post": denom,
                "frac_new_organized": float(np.mean([p > ORGANIZED_P for p in newP])),
                "frac_old_organized": float(np.mean([p > ORGANIZED_P for p in oldP])),
                "continued_turnover": bool(cont), "min_M_post": float(minM)}

    cells = cand.cells
    ctrl = RDState(s_star.U.copy(), s_star.V.copy(), s_star.CU.copy(), s_star.CV.copy(), s_star.step)
    sham = _swap_cells(s_star, cells, 0, 0)
    pert = _swap_cells(s_star, cells, DELTA[0], DELTA[1])
    occ = np.zeros((n, n), dtype=bool); occ[cells[:, 0], cells[:, 1]] = True
    ys, xs = np.nonzero(~occ & (s_star.V > DET.threshold * 0.2))
    k = min(len(cells), len(ys))
    plac = _swap_cells(s_star, np.stack([ys[:k], xs[:k]], 1), DELTA[0], DELTA[1]) if k > 0 else ctrl
    sham_ok = bool(np.array_equal(sham.U, ctrl.U) and np.array_equal(sham.V, ctrl.V)
                   and np.array_equal(sham.CV, ctrl.CV))
    B = {"CONTROL": branch(ctrl), "SHAM": branch(sham), "PERTURBED": branch(pert), "PLACEBO": branch(plac)}
    P = B["PERTURBED"]; PL = B["PLACEBO"]
    reest = P["frac_new_organized"] > 0.5
    exceeds = (P["frac_new_organized"] - PL["frac_new_organized"]) > PLACEBO_MARGIN
    occupancy = P["frac_old_organized"] > 0.5
    audited = bool(sham_ok and reest and exceeds and (not occupancy) and P["continued_turnover"])
    if not reest:
        cls = "destroyed_or_no_reestablishment"
    elif not exceeds:
        cls = "placebo_failure"
    elif occupancy:
        cls = "occupancy_alias"
    elif not P["continued_turnover"]:
        cls = "frozen_lump"
    else:
        cls = "AUDITED"
    return {"law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
            "sham_equals_control": sham_ok, "n_post_denominator": P["n_post"],
            "branches": B, "classification": cls, "audited": audited}
