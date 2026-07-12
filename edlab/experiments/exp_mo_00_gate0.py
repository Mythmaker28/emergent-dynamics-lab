"""EXP-MO-00 / GATE-0: is organization load-bearing in the motile polar substrate?

Protocol: docs/experiments/EXP_MO_00_GATE0_PROTOCOL.md (SHA 503c7bec8929c585ff6ce1024b2190b2a50cc462).
Governed by docs/CAUSAL_METHODOLOGY.md R1-R6. Nulls are NEVER pooled. PLACEBO carries no eliminative weight.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..substrates.motile_polar.engine import MPState, MotilePolarEngine
from ..substrates.motile_polar.observables import MPEntity, detect, continuity, retention
from ..substrates.particle_dynamics.engine import minimum_image
from .exp_mo_00 import SPEC, TRACER, DET, PHE, seed_state
from .exp_rd_04 import newcombe_diff, mcnemar_exact
from .exp_rd_02 import wilson

DELTA = (18, 18)
T_STAR = 300                 # FIXED. NOT derived from any cadence (R6).
HORIZON = 300
FINE_CADENCE = 5
OBS_CADENCES = (5, 10, 15)
# SAMPLING-ADEQUACY CRITERION (declared from QUALIFICATION, not from any GATE-0 outcome):
# the reference pattern travels at 0.95 cells/step, so an observer is ADMISSIBLE only if it can resolve the
# trajectory: speed * cadence <= L/4 = 16 cells. 0.95*15 = 14.3 -> OK. The earlier cadences {25,50,100} are
# INADMISSIBLE (at cadence 100 the pattern wraps the 64-lattice 1.5x per snapshot: the tracker cannot follow ANY
# arm, so those settings measure nothing and would have failed every arm identically).
OBS_SITE_SCALES = (0.8, 1.0, 1.2)
OBS_GATE_SCALES = (0.8, 1.0, 1.2)
SITE_RADIUS = 10.0
TRACK_GATE_PER_STEP = 1.5    # cells/step. Derived from QUALIFICATION: the reference pattern travels at
                             # 0.95 cells/step (a traveling wave -- the PATTERN outruns the material, whose
                             # advective speed is capped at v0=0.55). A gate below the pattern speed cannot
                             # follow ANY arm: it is a broken instrument, not a discriminating one.
ORGANIZED_P = 0.8
TURNOVER_M = 0.5
MOTILITY_MIN = 0.25          # cells/step, frozen
LAGS = (1, 3, 6)
SEEDS = tuple(range(31001, 31031))   # fixed N = 30. FRESH: 30001 was burned on an instrument smoke test.
MARGIN = 0.25
ARMS = ("INTACT", "SCRAMBLED", "PLACEBO")


def _polar_order(py, px, w) -> float:
    mag = np.hypot(py, px)
    return float(np.hypot(np.average(py, weights=w), np.average(px, weights=w)) /
                 (np.average(mag, weights=w) + 1e-12))


def swap_support(st: MPState, sup: np.ndarray, dy: int, dx: int) -> MPState:
    """Translate rho, R, polarity and ALL passive cohorts inside `sup` together (conservative swap).
    Zero displacement is an EXACT no-op."""
    n = st.rho.shape[0]
    ys, xs = np.nonzero(sup)
    ty, tx = (ys + dy) % n, (xs + dx) % n
    # A swap between a set and its translate is conservative ONLY if the two are disjoint. If they overlap the map
    # is not a bijection, cells get double-written, and material is destroyed. Fail LOUDLY (R5); the caller censors.
    if (dy, dx) != (0, 0):
        shifted = np.roll(np.roll(sup, dy, 0), dx, 1)
        assert not np.any(shifted & sup), "support overlaps its own translate: displacement would not conserve mass"
    o = st.copy()
    for f_new, f_old in ((o.rho, st.rho), (o.py, st.py), (o.px, st.px), (o.R, st.R)):
        f_new[ys, xs] = f_old[ty, tx]
        f_new[ty, tx] = f_old[ys, xs]
    o.C[:, ys, xs] = st.C[:, ty, tx]
    o.C[:, ty, tx] = st.C[:, ys, xs]
    return o


def scramble(st: MPState, sup: np.ndarray, rng: np.random.Generator) -> MPState:
    """The DECISIVE null (R3). Three INDEPENDENT permutations inside the support:
      P1 -> (rho, all cohorts) jointly : preserves total material, per-cohort mass, rho multiset,
                                         and the exact cell-wise invariant sum_c C == rho
      P2 -> R                          : preserves total R and its multiset; DESTROYS the rho<->R correlation
      P3 -> |p| with directions redrawn uniformly : preserves the polarity-MAGNITUDE distribution exactly;
                                         DESTROYS coherent polarity and the rho<->p correlation
    Nothing else about the cargo differs from INTACT."""
    ys, xs = np.nonzero(sup)
    m = len(ys)
    o = st.copy()
    p1, p2, p3 = rng.permutation(m), rng.permutation(m), rng.permutation(m)
    o.rho[ys, xs] = st.rho[ys[p1], xs[p1]]
    o.C[:, ys, xs] = st.C[:, ys[p1], xs[p1]]
    o.R[ys, xs] = st.R[ys[p2], xs[p2]]
    mag = np.hypot(st.py[ys, xs], st.px[ys, xs])[p3]
    ang = rng.uniform(0.0, 2 * np.pi, size=m)
    o.py[ys, xs] = mag * np.sin(ang)
    o.px[ys, xs] = mag * np.cos(ang)
    return o


def assert_interventions(st: MPState, sup: np.ndarray, ctrl: MPState, sham: MPState,
                         intact: MPState, scram: MPState) -> dict[str, Any]:
    """R5: prove every intervention changed its intended variable. Fails LOUDLY."""
    ys, xs = np.nonzero(sup)
    w = st.rho[ys, xs] + 1e-12
    # SHAM is an exact bitwise no-op
    for f in ("rho", "py", "px", "R"):
        assert np.array_equal(getattr(sham, f), getattr(ctrl, f)), f"SHAM changed {f}"
    assert np.array_equal(sham.C, ctrl.C), "SHAM changed cohorts"
    # INTACT conserves total material and actually moved the cargo
    assert np.isclose(intact.rho.sum(), st.rho.sum()) and np.isclose(intact.R.sum(), st.R.sum())
    assert not np.array_equal(intact.rho, ctrl.rho), "INTACT did not move anything"
    # SCRAMBLED matches every declared invariant EXACTLY ...
    assert np.isclose(scram.rho[ys, xs].sum(), st.rho[ys, xs].sum()), "scramble changed total material"
    assert np.isclose(scram.R[ys, xs].sum(), st.R[ys, xs].sum()), "scramble changed total nutrient"
    assert np.allclose(scram.C[:, ys, xs].sum(1), st.C[:, ys, xs].sum(1)), "scramble changed per-cohort mass"
    assert np.allclose(np.sort(scram.rho[ys, xs]), np.sort(st.rho[ys, xs])), "scramble changed the rho multiset"
    mi = np.sort(np.hypot(st.py[ys, xs], st.px[ys, xs]))
    ms = np.sort(np.hypot(scram.py[ys, xs], scram.px[ys, xs]))
    assert np.allclose(mi, ms), "scramble changed the polarity-magnitude distribution"
    assert np.allclose(scram.C.sum(0), scram.rho), "scramble broke the cohort partition"
    # ... and provably DESTROYED the organization
    o_i = _polar_order(st.py[ys, xs], st.px[ys, xs], w)
    o_s = _polar_order(scram.py[ys, xs], scram.px[ys, xs], w)
    assert o_s < 0.5 * o_i, f"scramble failed to destroy coherent polarity ({o_s:.3f} vs {o_i:.3f})"
    ci = abs(float(np.corrcoef(st.rho[ys, xs], np.hypot(st.py[ys, xs], st.px[ys, xs]))[0, 1]))
    cs = abs(float(np.corrcoef(scram.rho[ys, xs], np.hypot(scram.py[ys, xs], scram.px[ys, xs]))[0, 1]))
    return {"polar_order_intact": o_i, "polar_order_scrambled": o_s,
            "rho_p_corr_intact": ci, "rho_p_corr_scrambled": cs,
            "organization_destroyed": bool(o_s < 0.5 * o_i)}


def _detections(eng: MotilePolarEngine, s0: MPState) -> list[tuple[int, list[MPEntity]]]:
    return [(sn.step, detect(sn, DET, PHE)) for sn in eng.simulate(s0, HORIZON, FINE_CADENCE)[1:]]


def _score(dets, phi_full, phi_blind, old_c, new_c, n, *, cadence, site_scale, gate_scale) -> dict[str, Any]:
    """Offline observer. Tracks the MOTILE entity from the destination."""
    step = cadence // FINE_CADENCE
    sub = [d for i, d in enumerate(dets) if (i + 1) % step == 0]
    radius = SITE_RADIUS * site_scale
    gate = TRACK_GATE_PER_STEP * cadence * gate_scale
    chain: list[MPEntity | None] = []
    last = None
    for _t, ents in sub:
        if last is None:
            # the entity is MOTILE: by the first post snapshot it may already have travelled one gate's worth
            near = [e for e in ents
                    if np.linalg.norm(minimum_image(np.asarray(e.centroid) - new_c, n)) <= radius + gate]
        else:
            near = [e for e in ents
                    if np.linalg.norm(minimum_image(np.asarray(e.centroid) - last, n)) <= gate]
        pick = max(near, key=lambda e: e.size) if near else None
        chain.append(pick)
        if pick is not None:
            last = np.asarray(pick.centroid)
    ok_full, ok_blind, old_hit = [], [], []
    for (_t, ents), e in zip(sub, chain):
        ok_full.append(bool(e is not None and continuity(phi_full, e.phenotype_full) > ORGANIZED_P))
        ok_blind.append(bool(e is not None and continuity(phi_blind, e.phenotype_blind) > ORGANIZED_P))
        old_hit.append(any(np.linalg.norm(minimum_image(np.asarray(x.centroid) - old_c, n)) <= radius
                           and continuity(phi_full, x.phenotype_full) > ORGANIZED_P for x in ents))
    alive = [e for e in chain if e is not None]
    path = 0.0
    for i in range(1, len(alive)):
        d = minimum_image(np.asarray(alive[i].centroid) - np.asarray(alive[i - 1].centroid), n)
        path += float(np.linalg.norm(d))
    speed = path / HORIZON if len(alive) >= 2 else 0.0
    turn = False
    for lag in LAGS:
        for i in range(len(alive) - lag):
            if retention(alive[i].cohort_mass, alive[i + lag].cohort_mass) < TURNOVER_M:
                turn = True
    d = len(sub)
    return {"n_post": d,
            "frac_full": float(np.mean(ok_full)) if d else 0.0,
            "frac_blind": float(np.mean(ok_blind)) if d else 0.0,
            "frac_old": float(np.mean(old_hit)) if d else 0.0,
            "speed": speed, "turnover": turn}


def _audited_robust(dets, phi_full, phi_blind, old_c, new_c, n, sham_ok) -> dict[str, Any]:
    grid = {}
    for cad in OBS_CADENCES:
        for ss in OBS_SITE_SCALES:
            for gs in OBS_GATE_SCALES:
                s = _score(dets, phi_full, phi_blind, old_c, new_c, n,
                           cadence=cad, site_scale=ss, gate_scale=gs)
                grid[f"c{cad}_s{ss}_g{gs}"] = bool(
                    sham_ok and s["frac_full"] > 0.5 and s["frac_blind"] > 0.5   # BOTH phenotypes
                    and s["frac_old"] <= 0.5 and s["speed"] > MOTILITY_MIN and s["turnover"])
    ref = _score(dets, phi_full, phi_blind, old_c, new_c, n, cadence=FINE_CADENCE, site_scale=1.0, gate_scale=1.0)
    return {"audited_robust": all(grid.values()), "n_settings": len(grid),
            "n_audited_settings": int(sum(grid.values())), "ref": ref}


def gate0_unit(seed: int) -> dict[str, Any]:
    eng = MotilePolarEngine(SPEC, TRACER)
    n = SPEC.size
    s = seed_state(SPEC, TRACER, seed)
    for _ in range(T_STAR):                       # FIXED t*, observer-independent
        s = eng.step(s)
    ents = detect(s, DET, PHE)
    if not ents:
        return {"seed": seed, "enrolled": False}
    cand = max(ents, key=lambda e: e.size)
    if cand.size < 3 * DET.min_cells:
        return {"seed": seed, "enrolled": False, "reason": "candidate too small"}

    sup = np.zeros((n, n), dtype=bool)
    sup[cand.cells[:, 0], cand.cells[:, 1]] = True
    # CENSORING RULE (forced by the frozen protocol's exact-conservation requirement, declared before any GATE-0
    # outcome was inspected -- the assertion fired on the very first unit). If the entity is large or elongated
    # enough that its support overlaps its own translate by DELTA, NO conservative displacement of it exists, so
    # the unit cannot be measured by any arm and is CENSORED. Censored units are reported with their denominator
    # and are excluded identically from every arm, so no arm is advantaged.
    if np.any(np.roll(np.roll(sup, DELTA[0], 0), DELTA[1], 1) & sup):
        return {"seed": seed, "enrolled": False, "reason": "support_overlaps_translate"}
    old_c = np.asarray(cand.centroid)
    new_c = (old_c + np.array(DELTA)) % n
    rng = np.random.default_rng(770000 + seed)

    ctrl = s.copy()
    sham = swap_support(s, sup, 0, 0)
    intact = swap_support(s, sup, *DELTA)
    scram = swap_support(scramble(s, sup, rng), sup, *DELTA)
    checks = assert_interventions(s, sup, ctrl, sham, intact, scram)
    sham_ok = True                                 # asserted above

    ys, xs = np.nonzero((~sup) & (s.rho > DET.threshold * 0.2))
    k = min(int(sup.sum()), len(ys))
    pm = np.zeros((n, n), dtype=bool)
    if k > 0:
        pm[ys[:k], xs[:k]] = True
    plac = swap_support(s, pm, *DELTA) if k > 0 else ctrl

    out: dict[str, Any] = {"seed": seed, "enrolled": True, "t_star": T_STAR,
                           "sham_equals_control": sham_ok, "checks": checks, "arms": {}}
    for name, st0 in (("INTACT", intact), ("SCRAMBLED", scram), ("PLACEBO", plac)):
        out["arms"][name] = _audited_robust(_detections(eng, st0), cand.phenotype_full, cand.phenotype_blind,
                                            old_c, new_c, n, sham_ok)
    return out
