"""EXP-RD-00: qualification of the OPEN reaction-diffusion substrate + positive/negative measurement controls."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.reaction_diffusion.engine import (GrayScottSpec, RDEngine, RDState, laplacian,
                                                    laplacian_reference)
from ..substrates.reaction_diffusion.observables import (
    RDDetectionSpec, RDPhenotypeSpec, detect_rd_entities, to_entity_observation,
    rd_material_retention, rd_phenotype_continuity,
)
from .exp_fl_00 import _cohort_grid

G_SPATIAL = 8                      # verified tracer resolution (D-024), + 1 FEED cohort
N_COHORTS = G_SPATIAL + 1
DET = RDDetectionSpec(); PHE = RDPhenotypeSpec()


def rd_state(spec: GrayScottSpec, seed: int, n_patches: int = 3, patch: int = 12,
             noise: float = 0.02) -> RDState:
    """Standard Gray-Scott seeding: U=1, V=0 background; square patches at U=0.5, V=0.25 plus small noise."""
    n = spec.size
    rng = np.random.default_rng(seed)
    U = np.ones((n, n)); V = np.zeros((n, n))
    for _ in range(n_patches):
        cy, cx = rng.integers(0, n, 2)
        ys = (np.arange(cy, cy + patch)) % n; xs = (np.arange(cx, cx + patch)) % n
        U[np.ix_(ys, xs)] = 0.5; V[np.ix_(ys, xs)] = 0.25
    U = np.clip(U + noise * rng.normal(size=(n, n)), 0.0, 1.0)
    V = np.clip(V + noise * rng.normal(size=(n, n)), 0.0, 1.0)
    band = _cohort_grid(n, G_SPATIAL)
    CU = np.zeros((N_COHORTS, n, n)); CV = np.zeros((N_COHORTS, n, n))
    for c in range(G_SPATIAL):
        CU[c] = U * (band == c); CV[c] = V * (band == c)      # cohort G = FEED, starts empty
    return RDState(U, V, CU, CV)


def rates(spec: GrayScottSpec, st: RDState):
    prod = st.U * st.V * st.V
    rem = (spec.F + spec.k) * st.V
    act = prod - rem + spec.Dv * laplacian(st.V)              # dV/dt
    return prod, rem, act


# ---------------------------------------------------------------- measurement controls (positive / negative)

def build_control_snapshots(*, active: bool, n: int = 96, n_snapshots: int = 31):
    """Scripted control. Fixed V blob (persistent phenotype) whose cohort composition turns over.
    active=True  -> a genuine dissipative organization: nonzero production/removal/activity (throughput).
    active=False -> STATIC-FLUX NULL: identical geometry and identical cohort turnover, but ZERO rates
                    (a frozen / externally imposed pattern that does no work)."""
    yy, xx = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    cy = cx = n / 2.0
    r2 = (yy - cy) ** 2 + (xx - cx) ** 2
    V = 0.8 * np.exp(-r2 / (2 * 7.0 ** 2))
    U = 1.0 - V
    out = []
    for s in range(n_snapshots):
        cc = np.arange(N_COHORTS)
        d = np.minimum((cc - s) % N_COHORTS, (s - cc) % N_COHORTS)
        w = np.exp(-0.5 * (d / 1.0) ** 2); w = w / w.sum()
        CV = V[None] * w[:, None, None]
        CU = U[None] * w[:, None, None]
        if active:
            prod = U * V * V; rem = 0.06 * V; act = prod - rem
        else:
            prod = np.zeros_like(V); rem = np.zeros_like(V); act = np.zeros_like(V)
        out.append((s, float(s), U.copy(), V.copy(), CU, CV, prod, rem, act))
    return out


def run_control_through_stack(snaps) -> dict[str, Any]:
    trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=snaps[0][3].shape[0])
    ents_by_track: dict[int, list] = {}
    prod_l = []; act_l = []; n_ent = []
    for (s, t, U, V, CU, CV, prod, rem, act) in snaps:
        fes = detect_rd_entities(U, V, CV, prod, rem, act, snapshot_step=s, time=t, detection=DET, phenotype_spec=PHE)
        n_ent.append(len(fes))
        for e in fes:
            prod_l.append(e.phenotype.raw["production"]); act_l.append(abs(e.phenotype.raw["activity"]))
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s, time=t)
        by = {e.local_index: e for e in fes}
        for to in tracked:
            ents_by_track.setdefault(to.track_id, []).append(by[to.entity.local_index])
    if not ents_by_track:
        return {"n_tracks": 0, "P_max": 0.0, "M_min": 1.0, "n_probe": 0,
                "mean_production": 0.0, "mean_activity": 0.0, "single_entity": all(c == 1 for c in n_ent)}
    main = max(ents_by_track, key=lambda k: len(ents_by_track[k]))
    fes = ents_by_track[main]
    Ps = []; Ms = []; probe = 0
    for lag in (1, 3, 6):
        for i in range(len(fes) - lag):
            p = rd_phenotype_continuity(fes[i].phenotype, fes[i + lag].phenotype)
            m = rd_material_retention(fes[i].cohort_mass, fes[i + lag].cohort_mass)
            Ps.append(p); Ms.append(m)
            if p > 0.8 and m < 0.5:
                probe += 1
    return {"n_tracks": len(ents_by_track), "main_obs": len(fes), "single_entity": all(c == 1 for c in n_ent),
            "P_max": float(max(Ps)) if Ps else 0.0, "P_min": float(min(Ps)) if Ps else 0.0,
            "M_min": float(min(Ms)) if Ms else 1.0, "n_probe": probe,
            "mean_production": float(np.mean(prod_l)) if prod_l else 0.0,
            "mean_activity": float(np.mean(act_l)) if act_l else 0.0}


# ---------------------------------------------------------------- qualification gate

def qualify() -> dict[str, Any]:
    open_spec = GrayScottSpec(F=0.025, k=0.055)   # spot-forming regime: discrete, trackable dissipative structures
    closed_spec = GrayScottSpec(F=0.0, k=0.0)

    # (1) OPENNESS: from a NON-EQUILIBRIUM uniform state the homogeneous feed must grow the total material.
    #     (Starting from U+V==1 everywhere would sit on the fixed point and hide the source/sink.)
    n0 = open_spec.size
    probe = RDState(np.full((n0, n0), 0.5), np.zeros((n0, n0)),
                    np.zeros((N_COHORTS, n0, n0)), np.zeros((N_COHORTS, n0, n0)))
    probe.CU[0] = probe.U.copy()
    sp = RDEngine(open_spec).simulate(probe, 200, 50)
    open_drift = abs(sp[-1].total() - sp[0].total()) / sp[0].total()
    so = RDEngine(open_spec).simulate(rd_state(open_spec, 1), 400, 50)
    # (2) EXACT CLOSED LIMIT: F=k=0 conserves U+V exactly
    sc = RDEngine(closed_spec).simulate(rd_state(closed_spec, 1), 400, 50)
    closed_drift = max(abs(s.total() - sc[0].total()) / sc[0].total() for s in sc)
    # (3) HOMOGENEITY NULL: the forcing is spatially homogeneous -> a uniform state stays uniform forever,
    #     so the forcing CANNOT impose a spatial pattern.
    n = open_spec.size
    uni = RDState(np.full((n, n), 0.5), np.full((n, n), 0.25),
                  np.zeros((N_COHORTS, n, n)), np.zeros((N_COHORTS, n, n)))
    uni.CU[0] = uni.U.copy(); uni.CV[0] = uni.V.copy()
    su = RDEngine(open_spec).simulate(uni, 400, 100)
    homog = max(float(np.ptp(s.U)) + float(np.ptp(s.V)) for s in su)
    # (4) tracer partition + FEED cohort growth
    part = max(max(float(np.max(np.abs(s.CU.sum(0) - s.U))), float(np.max(np.abs(s.CV.sum(0) - s.V)))) for s in so)
    feed_growth = float(so[-1].CU[-1].sum() + so[-1].CV[-1].sum())
    # (5) tracers passive: zeroing cohorts must not change U,V
    z = rd_state(open_spec, 1); z.CU = np.zeros_like(z.CU); z.CV = np.zeros_like(z.CV)
    sz = RDEngine(open_spec).simulate(z, 400, 50)
    tracer_inv = max(float(np.max(np.abs(a.U - b.U))) + float(np.max(np.abs(a.V - b.V))) for a, b in zip(so, sz))
    # (6) determinism + nonnegativity
    so2 = RDEngine(open_spec).simulate(rd_state(open_spec, 1), 400, 50)
    det_err = max(float(np.max(np.abs(a.V - b.V))) for a, b in zip(so, so2))
    nonneg = min(min(float(s.U.min()), float(s.V.min())) for s in so)
    # (7) reference-path agreement (two independent Laplacian implementations)
    X = so[-1].V
    refpath = float(np.max(np.abs(laplacian(X) - laplacian_reference(X))))
    # (8) detector/tracker on REAL open RD dynamics
    eng = RDEngine(open_spec); trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=open_spec.size)
    snaps = eng.simulate(rd_state(open_spec, 2), 4000, 50)
    lens = []
    for s in snaps:
        p, r, a = rates(open_spec, s)
        fes = detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                 detection=DET, phenotype_spec=PHE)
        trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
    max_track = max((len(v) for v in trk.tracks.values()), default=0)
    # (9) POSITIVE control (active dissipative organization) and (10) NEGATIVE control (static-flux null)
    pos = run_control_through_stack(build_control_snapshots(active=True))
    neg = run_control_through_stack(build_control_snapshots(active=False))
    recognized = pos["P_max"] > 0.8 and pos["M_min"] < 0.5 and pos["n_probe"] > 0 and pos["n_tracks"] >= 1
    separated = (pos["mean_production"] > 1e-4 and pos["mean_activity"] > 1e-4
                 and neg["mean_production"] < 1e-9 and neg["mean_activity"] < 1e-9)
    checks = {
        "openness_material_not_conserved": open_drift > 1e-3,
        "exact_closed_limit_conserves": closed_drift < 1e-9,
        "homogeneity_null_no_imposed_pattern": homog < 1e-12,
        "tracer_partition": part < 1e-9,
        "feed_cohort_grows": feed_growth > 0.0,
        "tracers_passive": tracer_inv == 0.0,
        "determinism": det_err == 0.0,
        "nonnegativity": nonneg >= -1e-12,
        "reference_path_agreement": refpath <= 1e-12,
        "detector_tracker_on_real_dynamics": max_track >= 3,
        "positive_control_recognized": bool(recognized),
        "negative_control_separated": bool(separated),
    }
    return {"checks": checks, "passed": all(checks.values()),
            "metrics": {"open_drift": open_drift, "closed_drift": closed_drift, "homogeneity_ptp": homog,
                        "tracer_partition_err": part, "feed_cohort_mass": feed_growth,
                        "tracer_invariance": tracer_inv, "determinism": det_err, "min_field": nonneg,
                        "refpath": refpath, "max_track_len": max_track},
            "positive_control": pos, "negative_control": neg}
