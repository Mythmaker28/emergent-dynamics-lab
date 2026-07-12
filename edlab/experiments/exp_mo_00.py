"""EXP-MO-00 -- substrate qualification for the motile polar-field substrate."""

from __future__ import annotations

import numpy as np

from ..substrates.motile_polar.engine import MotilePolarSpec, MPState, MotilePolarEngine
from ..substrates.motile_polar.observables import MPDetectionSpec, MPPhenotypeSpec, detect, retention
from ..substrates.reaction_diffusion.engine import TracerSpec

TRACER = TracerSpec(n_spatial=4, n_temporal=8, tau_feed=60)
DET = MPDetectionSpec()
PHE = MPPhenotypeSpec()
SPEC = MotilePolarSpec()


def seed_state(spec: MotilePolarSpec, tracer: TracerSpec, seed: int, *, polarized: bool = True) -> MPState:
    """A coherent polar disc of active material in a full nutrient bath. The SEED provides the symmetry breaking;
    the forcing provably cannot (see the homogeneity null)."""
    rng = np.random.default_rng(seed)
    n = spec.size
    rho = np.zeros((n, n))
    py = np.zeros((n, n))
    px = np.zeros((n, n))
    cy, cx = rng.integers(n // 4, 3 * n // 4, size=2)
    ys, xs = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    d = np.sqrt((((ys - cy + n // 2) % n) - n // 2) ** 2 + (((xs - cx + n // 2) % n) - n // 2) ** 2)
    disc = d <= 5.0
    rho[disc] = 1.0
    rho += 0.01 * rng.random((n, n))
    th = rng.uniform(0, 2 * np.pi)
    p0 = np.sqrt(spec.a / spec.b)
    if polarized:
        py[disc] = p0 * np.sin(th)
        px[disc] = p0 * np.cos(th)
    else:                                   # incoherent control: same |p|, random directions
        ang = rng.uniform(0, 2 * np.pi, size=disc.sum())
        py[disc] = p0 * np.sin(ang)
        px[disc] = p0 * np.cos(ang)
    R = np.full((n, n), spec.R0)
    C = np.zeros((tracer.n_cohorts, n, n))
    # initial-origin SPATIAL cohorts: partition by quadrant, so sum_c C == rho exactly
    for c in range(tracer.n_spatial):
        q = ((ys * tracer.n_spatial) // n) % tracer.n_spatial
        C[c] = np.where(q == c, rho, 0.0)
    return MPState(rho, py, px, R, C, 0)


def qualify() -> dict:
    eng = MotilePolarEngine(SPEC, TRACER)
    out: dict = {}

    # 1. cohort invariant sum_c C == rho, exactly, at every step
    s = seed_state(SPEC, TRACER, 1)
    worst = 0.0
    for _ in range(300):
        s = eng.step(s)
        worst = max(worst, float(np.abs(s.C.sum(0) - s.rho).max()))
        assert np.isfinite(s.rho).all() and np.isfinite(s.R).all(), 'engine diverged'
    out["cohort_partition_max_rel_error"] = worst / max(1e-12, float(s.rho.sum()))

    # 2. EXACT CLOSED LIMIT: F = g0 = k = 0 conserves total rho
    csp = MotilePolarSpec(F=0.0, g0=0.0, k=0.0)
    ce = MotilePolarEngine(csp, TRACER)
    cs = seed_state(csp, TRACER, 2)
    m0 = float(cs.rho.sum())
    for _ in range(300):
        cs = ce.step(cs)
    out["closed_limit_rel_mass_drift"] = abs(float(cs.rho.sum()) - m0) / m0
    out["closed_limit_is_closed"] = csp.is_closed

    # 3. HOMOGENEITY NULL: a uniform state stays EXACTLY uniform -> the forcing cannot impose a pattern
    n = SPEC.size
    u = MPState(np.full((n, n), 0.5), np.zeros((n, n)), np.zeros((n, n)), np.full((n, n), SPEC.R0),
                np.concatenate([np.full((1, n, n), 0.5), np.zeros((TRACER.n_cohorts - 1, n, n))]), 0)
    for _ in range(200):
        u = eng.step(u)
    out["homogeneity_null_rho_ptp"] = float(np.ptp(u.rho))
    out["homogeneity_null_R_ptp"] = float(np.ptp(u.R))

    # 4. PASSIVE TRACERS: perturbing cohorts must not change rho, p or R by a single bit
    s1 = seed_state(SPEC, TRACER, 3)
    s2 = s1.copy()
    s2.C = s2.C[::-1].copy()                       # relabel cohorts arbitrarily
    for _ in range(150):
        s1 = eng.step(s1)
        s2 = eng.step(s2)
    out["tracers_passive_rho_identical"] = bool(np.array_equal(s1.rho, s2.rho))
    out["tracers_passive_p_identical"] = bool(np.array_equal(s1.py, s2.py) and np.array_equal(s1.px, s2.px))

    # 5. POLARITY CAUSALLY DRIVES TRANSPORT: v0 = 0 must freeze the centroid
    zs = MotilePolarSpec(v0=0.0)
    ze = MotilePolarEngine(zs, TRACER)
    z = seed_state(zs, TRACER, 4)
    e0 = detect(z, DET, PHE)
    for _ in range(300):
        z = ze.step(z)
    e1 = detect(z, DET, PHE)
    if e0 and e1:
        b0 = max(e0, key=lambda e: e.size)
        b1 = max(e1, key=lambda e: e.size)
        d = b1.centroid - b0.centroid
        d -= zs.size * np.round(d / zs.size)
        out["v0_zero_displacement"] = float(np.linalg.norm(d))
    else:
        out["v0_zero_displacement"] = None

    # 6. MOTILITY + PERSISTENCE + TURNOVER with the polarized seed
    s = seed_state(SPEC, TRACER, 5)
    snaps = eng.simulate(s, 900, 30)
    track = []
    for sn in snaps:
        es = detect(sn, DET, PHE)
        track.append(max(es, key=lambda e: e.size) if es else None)
    alive = [e for e in track if e is not None]
    out["persist_fraction"] = len(alive) / len(track)
    if len(alive) >= 2:
        path = 0.0
        for i in range(1, len(alive)):
            d = alive[i].centroid - alive[i - 1].centroid
            d -= SPEC.size * np.round(d / SPEC.size)
            path += float(np.linalg.norm(d))
        out["path_length"] = path
        out["mean_speed_cells_per_step"] = path / (900.0)
        out["polar_order_mean"] = float(np.mean([e.polar_order for e in alive]))
        ms = [retention(alive[i].cohort_mass, alive[i + 6].cohort_mass) for i in range(len(alive) - 6)]
        out["min_M_lag6"] = float(min(ms)) if ms else None

    # 7. INCOHERENT seed (same |p|, random directions) -- the substrate must NOT sustain it the same way
    si = seed_state(SPEC, TRACER, 5, polarized=False)
    isn = eng.simulate(si, 900, 30)
    itr = [detect(x, DET, PHE) for x in isn]
    ia = [max(e, key=lambda z: z.size) for e in itr if e]
    out["incoherent_persist_fraction"] = len(ia) / len(itr)
    if len(ia) >= 2:
        path = 0.0
        for i in range(1, len(ia)):
            d = ia[i].centroid - ia[i - 1].centroid
            d -= SPEC.size * np.round(d / SPEC.size)
            path += float(np.linalg.norm(d))
        out["incoherent_mean_speed"] = path / 900.0
        out["incoherent_polar_order_mean"] = float(np.mean([e.polar_order for e in ia]))
    return out
