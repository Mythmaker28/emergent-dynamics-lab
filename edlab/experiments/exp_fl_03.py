"""EXP-FL-03: multi-seed causal replication of the FROZEN diagnostic survivors {2,16,40,59}.

Everything from EXP-FL-02 is frozen (mechanism, laws, P/M, thresholds, displacement, branches). Two STRENGTHENINGS
(both make the audit STRICTER, never looser):
  (1) CONTINUED TURNOVER: a re-established structure must keep exchanging constituents in the post-window
      (frozen field M < 0.5 at a frozen lag) -- a temporarily frozen lump does NOT count.
  (2) the corrected PLACEBO criterion is preserved (PERTURBED must exceed PLACEBO by MARGIN).
Explicit denominators: the post-intervention window is HORIZON steps at the frozen cadence -> N_POST snapshots;
every "fraction organized" is out of N_POST. Non-enrolled seeds are CENSORED and reported, never dropped.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..substrates.flow_lenia.engine import flow_field
from ..substrates.flow_lenia.engine_throughput import ThroughputEngine, ThroughputState
from ..substrates.flow_lenia.observables import (
    FieldDetectionSpec, FieldPhenotypeSpec, detect_field_entities, field_material_retention, phenotype_continuity,
)
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_fl_02 import (EXPFL02Config, G_SPATIAL, _displace_mass, throughput_law_from_halton, throughput_state)

FROZEN_LAWS = (2, 16, 40, 59)
CAUSAL_SEEDS = tuple(range(9601, 9613))     # 12 UNSEEN causal seeds per law
DELTA = (20, 20)                            # frozen displacement (cells)
HORIZON = 150                               # frozen post-intervention horizon (steps)
CADENCE = 10                                # frozen snapshot cadence -> N_POST = 15 snapshots
N_POST = HORIZON // CADENCE                 # EXPLICIT DENOMINATOR for every reported fraction
SITE_RADIUS = 12.0                          # frozen "at site" radius (cells)
ORGANIZED_P = 0.8                           # frozen probe P threshold (unchanged)
TURNOVER_M = 0.5                            # frozen probe M threshold (unchanged)
PLACEBO_MARGIN = 0.25                       # corrected placebo criterion (frozen)
WARMUP_SNAPSHOTS = 8


def causal_unit(law_index: int, seed: int, cfg: EXPFL02Config | None = None,
                cadence: int = CADENCE, tracker_scale: float = 1.0) -> dict[str, Any]:
    cfg = cfg or EXPFL02Config()
    spec, tspec = throughput_law_from_halton(law_index, on=True)
    eng = ThroughputEngine(spec, tspec)
    det = FieldDetectionSpec(cfg.threshold, cfg.min_cells)
    phe = FieldPhenotypeSpec(cfg.length_scale, cfg.speed_scale)

    snaps = eng.simulate(throughput_state(spec, tspec, seed), cfg.steps, cadence)
    star = None
    for s in snaps[WARMUP_SNAPSHOTS:]:
        F, _ = flow_field(s.A, spec, eng._fK)
        fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                    detection=det, phenotype_spec=phe)
        if fes:
            big = max(fes, key=lambda e: e.size)
            if big.size >= 3 * cfg.min_cells:
                star = (s, big); break
    if star is None:
        return {"law_index": law_index, "seed": seed, "enrolled": False, "reason": "no_candidate_structure"}
    s_star, cand = star
    phi_star = cand.phenotype
    old_c = np.asarray(cand.centroid)
    new_c = (old_c + np.array(DELTA)) % spec.size
    res0 = float(cand.cohort_mass[G_SPATIAL:].sum() / max(cand.cohort_mass.sum(), 1e-12))

    n_post = HORIZON // cadence

    def run_branch(A0, C0):
        st = ThroughputState(A0.copy(), s_star.R.copy(), C0.copy(), s_star.cohorts_R.copy())
        out = eng.simulate(st, HORIZON, cadence)[1:]      # exclude t=0; denominator = actual snapshot count
        newP = []; oldP = []; new_track = []
        for s in out:
            F, _ = flow_field(s.A, spec, eng._fK)
            fes = detect_field_entities(s.A, F, s.cohorts_A, snapshot_step=s.step, time=float(s.step),
                                        detection=det, phenotype_spec=phe)
            def near(site):
                return [e for e in fes if float(np.linalg.norm(
                    minimum_image(np.asarray(e.centroid) - site, spec.size))) <= SITE_RADIUS]
            nn = near(new_c); oo = near(old_c)
            newP.append(max((phenotype_continuity(phi_star, e.phenotype) for e in nn), default=0.0))
            oldP.append(max((phenotype_continuity(phi_star, e.phenotype) for e in oo), default=0.0))
            if nn:
                new_track.append(max(nn, key=lambda e: e.size))
            else:
                new_track.append(None)
        denom = len(newP)          # EXPLICIT denominator actually used (may differ from HORIZON//cadence)
        # CONTINUED TURNOVER on the re-established new-site structure (frozen M, frozen lags)
        cont = False; minM_post = 1.0; res_end = None
        valid = [(i, e) for i, e in enumerate(new_track) if e is not None]
        for lag in cfg.lag_indices:
            for k in range(len(valid) - lag):
                i, ea = valid[k]; j, eb = valid[k + lag]
                m = field_material_retention(ea.cohort_mass, eb.cohort_mass)
                minM_post = min(minM_post, m)
                if m < TURNOVER_M:
                    cont = True
        if valid:
            last = valid[-1][1]
            res_end = float(last.cohort_mass[G_SPATIAL:].sum() / max(last.cohort_mass.sum(), 1e-12))
        return {"n_post": denom,
                "frac_new_organized": float(np.mean([p > ORGANIZED_P for p in newP])),
                "frac_old_organized": float(np.mean([p > ORGANIZED_P for p in oldP])),
                "continued_turnover": bool(cont), "min_M_post": float(minM_post),
                "reservoir_frac_end": res_end}

    cells = cand.cells
    A_c, C_c = s_star.A, s_star.cohorts_A
    A_s, C_s = _displace_mass(s_star.A, s_star.cohorts_A, cells, 0, 0)
    A_p, C_p = _displace_mass(s_star.A, s_star.cohorts_A, cells, DELTA[0], DELTA[1])
    occ = np.zeros_like(s_star.A, dtype=bool); occ[cells[:, 0], cells[:, 1]] = True
    ys, xs = np.nonzero(~occ & (s_star.A > 0))
    k = min(len(cells), len(ys))
    A_pl, C_pl = _displace_mass(s_star.A, s_star.cohorts_A, np.stack([ys[:k], xs[:k]], 1), DELTA[0], DELTA[1])
    sham_ok = bool(np.array_equal(A_s, A_c) and np.array_equal(C_s, C_c))

    B = {"CONTROL": run_branch(A_c, C_c), "SHAM": run_branch(A_s, C_s),
         "PERTURBED": run_branch(A_p, C_p), "PLACEBO": run_branch(A_pl, C_pl)}
    P = B["PERTURBED"]; PL = B["PLACEBO"]
    reestablished = P["frac_new_organized"] > 0.5
    exceeds_placebo = (P["frac_new_organized"] - PL["frac_new_organized"]) > PLACEBO_MARGIN
    occupancy = P["frac_old_organized"] > 0.5
    audited = bool(sham_ok and reestablished and exceeds_placebo and (not occupancy) and P["continued_turnover"])
    if not reestablished:
        cls = "destroyed_or_no_reestablishment"
    elif not exceeds_placebo:
        cls = "placebo_failure"
    elif occupancy:
        cls = "occupancy_alias"
    elif not P["continued_turnover"]:
        cls = "frozen_lump"           # re-established but stops turning over -> trivial translation-covariance
    else:
        cls = "AUDITED"
    return {"law_index": law_index, "seed": seed, "enrolled": True, "t_star": int(s_star.step),
            "cand_cells": int(len(cells)), "reservoir_frac_at_t_star": res0,
            "sham_equals_control": sham_ok, "n_post_denominator": n_post,
            "branches": B, "classification": cls, "audited": audited}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
