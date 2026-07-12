"""EXP-CH-01 / GATE-0: is the organization of a chemotactic aggregate load-bearing?

Protocol: docs/experiments/EXP_CH_01_GATE0_PROTOCOL.md (SHA 0c38ba199a4ba7b005b23c85fcf54ea981ff9371), frozen first.
Per law, never pooled. PRIMARY null = JOINT-SCRAMBLE (one permutation of the local tuples). PLACEBO carries no
eliminative weight (R2). Null arms are never pooled (R1).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..substrates.chemotaxis.engine import ChemoEngine, CHState
from ..substrates.chemotaxis.diagnostics import participation_ratio, entity_radius_of_gyration
from ..substrates.chemotaxis.observables import (CHDetectionSpec, CHPhenotypeSpec, detect, continuity,
                                                 retention, spatial_autocorr)
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_ch_00 import chemo_law, seed_state, TRACER
from .exp_rd_04 import newcombe_diff, mcnemar_exact
from .exp_rd_02 import wilson

FROZEN_LAWS = (2, 4, 5)
SEED_BLOCKS = {2: tuple(range(40001, 40041)), 4: tuple(range(41001, 41041)), 5: tuple(range(42001, 42041))}
DELTA = (16, 16)
T_STAR = 2000
HORIZON = 800
FINE_CADENCE = 50
OBS_CADENCES = (50, 100, 200)
OBS_SITE_SCALES = (0.8, 1.0, 1.2)
SITE_RADIUS = 8.0
ORGANIZED_P = 0.8
TURNOVER_M = 0.5
TURNOVER_LAG_STEPS = (400, 600)
# Declared in STEPS, not snapshots: a snapshot-indexed lag SHRINKS with cadence and can never fire at coarse
# cadence -- a criterion that cannot fire (the 4th of this class this session). Verified FIREABLE a priori on
# smoke seed 90001 (outside every GATE-0 block): the intact aggregate's cohort-Jaccard M at lag 400 steps is
# 0.330 / 0.195 / 0.156 for laws 2 / 4 / 5, all below the frozen 0.5. At lag 200 law 2 sits at 0.530 and could
# never pass. The material half-life is 268 / 190 / 166 steps, so the lag must span one.
PR_MAX = 0.15
RG_MAX = 8.0
MARGIN = 0.25
DET = CHDetectionSpec()
PHE = CHPhenotypeSpec()
ARMS = ("INTACT", "JOINT_SCRAMBLE", "INDEP_SCRAMBLE", "PLACEBO")
PRIMARY_NULL = "JOINT_SCRAMBLE"


def swap_support(st: CHState, sup: np.ndarray, dy: int, dx: int) -> CHState:
    n = st.rho.shape[0]
    if (dy, dx) != (0, 0):
        assert not np.any(np.roll(np.roll(sup, dy, 0), dx, 1) & sup), "source support overlaps its translate"
    ys, xs = np.nonzero(sup)
    ty, tx = (ys + dy) % n, (xs + dx) % n
    o = st.copy()
    for new, old in ((o.rho, st.rho), (o.c, st.c), (o.N, st.N)):
        new[ys, xs] = old[ty, tx]
        new[ty, tx] = old[ys, xs]
    o.C[:, ys, xs] = st.C[:, ty, tx]
    o.C[:, ty, tx] = st.C[:, ys, xs]
    return o


def joint_scramble(st: CHState, sup: np.ndarray, rng: np.random.Generator) -> CHState:
    """PRIMARY null. ONE permutation of the local TUPLES (rho, c, C_1..C_n) inside the support.
    The tuple is never broken, so local rho-c and rho-cohort associations are preserved EXACTLY;
    only POSITION changes. Gradients, neighbourhood correlations and global organization are destroyed."""
    ys, xs = np.nonzero(sup)
    p = rng.permutation(len(ys))
    o = st.copy()
    o.rho[ys, xs] = st.rho[ys[p], xs[p]]
    o.c[ys, xs] = st.c[ys[p], xs[p]]
    o.C[:, ys, xs] = st.C[:, ys[p], xs[p]]
    return o


def indep_scramble(st: CHState, sup: np.ndarray, rng: np.random.Generator) -> CHState:
    """SECONDARY null. Independent permutations for rho, c and the cohorts: additionally destroys the local
    rho-c / rho-cohort association. Reported SEPARATELY; never pooled with the primary null."""
    ys, xs = np.nonzero(sup)
    m = len(ys)
    o = st.copy()
    p1, p2 = rng.permutation(m), rng.permutation(m)
    o.rho[ys, xs] = st.rho[ys[p1], xs[p1]]
    o.C[:, ys, xs] = st.C[:, ys[p1], xs[p1]]      # cohorts follow rho, else the partition sum_c C == rho breaks
    o.c[ys, xs] = st.c[ys[p2], xs[p2]]            # c permuted INDEPENDENTLY of rho
    return o


def assert_unit(st, sup, ctrl, sham, intact, joint) -> dict[str, Any]:
    ys, xs = np.nonzero(sup)
    # (1) exact conservation under displacement
    assert np.isclose(intact.rho.sum(), st.rho.sum()) and np.isclose(intact.c.sum(), st.c.sum())
    assert np.isclose(joint.rho.sum(), st.rho.sum()) and np.isclose(joint.c.sum(), st.c.sum())
    # (3) SHAM is an exact bitwise no-op
    for f in ("rho", "c", "N"):
        assert np.array_equal(getattr(sham, f), getattr(ctrl, f)), f"SHAM changed {f}"
    assert np.array_equal(sham.C, ctrl.C)
    # (4) the scramble PRESERVED what it must
    sc = joint_scramble(st, sup, np.random.default_rng(1))
    assert np.isclose(sc.rho[ys, xs].sum(), st.rho[ys, xs].sum())
    assert np.isclose(sc.c[ys, xs].sum(), st.c[ys, xs].sum())
    assert np.allclose(sc.C[:, ys, xs].sum(1), st.C[:, ys, xs].sum(1))
    assert np.allclose(np.sort(sc.rho[ys, xs]), np.sort(st.rho[ys, xs]))
    assert np.allclose(np.sort(sc.c[ys, xs]), np.sort(st.c[ys, xs]))
    assert np.allclose(sc.C.sum(0), sc.rho)
    # (5) the scramble DESTROYED what it must: lag-1 spatial autocorrelation of rho AND c
    a_rho_i = spatial_autocorr(st.rho, sup)
    a_rho_s = spatial_autocorr(sc.rho, sup)
    a_c_i = spatial_autocorr(st.c, sup)
    a_c_s = spatial_autocorr(sc.c, sup)
    assert abs(a_rho_s) < 0.5 * abs(a_rho_i) + 1e-9, f"scramble did not destroy rho autocorr ({a_rho_s} vs {a_rho_i})"
    assert abs(a_c_s) < 0.5 * abs(a_c_i) + 1e-9, f"scramble did not destroy c autocorr ({a_c_s} vs {a_c_i})"
    return {"autocorr_rho_intact": a_rho_i, "autocorr_rho_scrambled": a_rho_s,
            "autocorr_c_intact": a_c_i, "autocorr_c_scrambled": a_c_s}


def _dets(eng, s0):
    return [(s, detect(s, DET, PHE)) for s in eng.simulate(s0, HORIZON, FINE_CADENCE)[1:]]


def _score(dets, phi, old_c, new_c, n, *, cadence, site_scale):
    step = cadence // FINE_CADENCE
    sub = [d for i, d in enumerate(dets) if (i + 1) % step == 0]
    rad = SITE_RADIUS * site_scale
    newP, oldP, ents, loc = [], [], [], []
    for s, es in sub:
        near = [e for e in es if np.linalg.norm(minimum_image(np.asarray(e.centroid) - new_c, n)) <= rad]
        old = [e for e in es if np.linalg.norm(minimum_image(np.asarray(e.centroid) - old_c, n)) <= rad]
        newP.append(max((continuity(phi, e.phenotype) for e in near), default=0.0))
        oldP.append(max((continuity(phi, e.phenotype) for e in old), default=0.0))
        pick = max(near, key=lambda e: e.size) if near else None
        ents.append(pick)
        loc.append(bool(pick is not None and pick.rg <= RG_MAX and participation_ratio(s.rho) <= PR_MAX))
    alive = [e for e in ents if e is not None]
    turn = False
    for lag_steps in TURNOVER_LAG_STEPS:
        j = max(1, lag_steps // cadence)                    # observer-independent: same physical lag at any cadence
        for i in range(len(alive) - j):
            if retention(alive[i].cohort_mass, alive[i + j].cohort_mass) < TURNOVER_M:
                turn = True
    d = len(sub)
    return {"n_post": d,
            "frac_new": float(np.mean([p > ORGANIZED_P for p in newP])) if d else 0.0,
            "frac_old": float(np.mean([p > ORGANIZED_P for p in oldP])) if d else 0.0,
            "frac_localized": float(np.mean(loc)) if d else 0.0, "turnover": bool(turn)}


def _audited_robust(dets, phi, old_c, new_c, n, sham_ok, ambient_clean):
    grid = {}
    for cad in OBS_CADENCES:
        for ss in OBS_SITE_SCALES:
            s = _score(dets, phi, old_c, new_c, n, cadence=cad, site_scale=ss)
            grid[f"c{cad}_s{ss}"] = bool(sham_ok and ambient_clean and s["frac_new"] > 0.5
                                         and s["frac_localized"] > 0.5 and s["frac_old"] <= 0.5 and s["turnover"])
    ref = _score(dets, phi, old_c, new_c, n, cadence=FINE_CADENCE, site_scale=1.0)
    return {"audited_robust": all(grid.values()), "n_audited_settings": int(sum(grid.values())),
            "n_settings": len(grid), "ref": ref}


def gate0_unit(law: int, seed: int) -> dict[str, Any]:
    sp = chemo_law(law)
    eng = ChemoEngine(sp, TRACER)
    n = sp.size
    st = seed_state(sp, TRACER, seed)
    for _ in range(T_STAR):
        st = eng.step(st)
    ents = detect(st, DET, PHE, sp.rho_max)
    if not ents:
        return {"law": law, "seed": seed, "enrolled": False, "reason": "no entity"}
    cand = max(ents, key=lambda e: e.size)
    sup = np.zeros((n, n), dtype=bool)
    sup[cand.cells[:, 0], cand.cells[:, 1]] = True
    if np.any(np.roll(np.roll(sup, DELTA[0], 0), DELTA[1], 1) & sup):
        return {"law": law, "seed": seed, "enrolled": False, "reason": "support_overlaps_translate"}

    old_c = np.asarray(cand.centroid)
    new_c = (old_c + np.array(DELTA)) % n
    phi = cand.phenotype
    rng = np.random.default_rng(660000 + 1000 * law + seed)

    ctrl = st.copy()
    sham = swap_support(st, sup, 0, 0)
    intact = swap_support(st, sup, *DELTA)
    joint = swap_support(joint_scramble(st, sup, rng), sup, *DELTA)
    indep = swap_support(indep_scramble(st, sup, rng), sup, *DELTA)
    checks = assert_unit(st, sup, ctrl, sham, intact, joint)

    ys, xs = np.nonzero((~sup) & (st.rho > DET.threshold * 0.2))
    k = min(int(sup.sum()), len(ys))
    pm = np.zeros((n, n), dtype=bool)
    if k > 0:
        pm[ys[:k], xs[:k]] = True
    plac = swap_support(st, pm, *DELTA) if k > 0 and not np.any(
        np.roll(np.roll(pm, DELTA[0], 0), DELTA[1], 1) & pm) else ctrl

    dctrl = _dets(eng, ctrl)
    amb = _score(dctrl, phi, old_c, new_c, n, cadence=FINE_CADENCE, site_scale=1.0)
    ambient_clean = amb["frac_new"] <= 0.5

    out: dict[str, Any] = {"law": law, "seed": seed, "enrolled": True, "t_star": T_STAR,
                           "sham_equals_control": True, "checks": checks,
                           "ambient_target_frac_new": amb["frac_new"], "ambient_clean": bool(ambient_clean),
                           "entity_size": cand.size, "entity_rg": cand.rg, "arms": {}}
    for name, s0 in (("INTACT", intact), ("JOINT_SCRAMBLE", joint), ("INDEP_SCRAMBLE", indep), ("PLACEBO", plac)):
        out["arms"][name] = _audited_robust(_dets(eng, s0), phi, old_c, new_c, n, True, ambient_clean)
    return out


def holm(pvals: dict[int, float]) -> dict[int, float]:
    """Holm-Bonferroni step-down adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj: dict[int, float] = {}
    prev = 0.0
    for i, (k, p) in enumerate(items):
        a = min(1.0, max(prev, (m - i) * p))
        adj[k] = a
        prev = a
    return adj
