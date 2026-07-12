"""EXP-MA-00: R7 + R8-A/R8-B on the multistable active-droplet substrate. NO law map. NO GATE-0."""

from __future__ import annotations

import numpy as np

from ..substrates.multistable.engine import MultiSpec, MAState, MultiEngine
from ..substrates.multistable.observables import MADetectionSpec, detect
from ..substrates.chemotaxis.diagnostics import participation_ratio, entity_radius_of_gyration, THRESHOLD_BAND
from ..substrates.reaction_diffusion.engine import TracerSpec
from .baseline import halton_point

TRACER = TracerSpec(n_spatial=4, n_temporal=8, tau_feed=200)
DET = MADetectionSpec()
N_POINTS = 32
T_STAR = 2000
WINDOW = 1000
CADENCE = 100
PR_MAX = 0.15
RG_MAX = 8.0
OCC_MAX = 0.15
BOX = {"chi0": (2.0, 12.0), "D_rho": (0.05, 0.30), "D_c": (0.20, 1.00), "s": (0.05, 0.40),
       "delta": (0.02, 0.20), "g0": (0.02, 0.20), "k": (0.01, 0.10), "F": (0.01, 0.10),
       "lam": (0.5, 6.0)}


def ma_law(i: int) -> MultiSpec:
    h = halton_point(i + 1, len(BOX))
    return MultiSpec(**{nm: lo + (hi - lo) * float(h[j]) for j, (nm, (lo, hi)) in enumerate(BOX.items())})


def seed_state(sp: MultiSpec, tr: TracerSpec, seed: int) -> MAState:
    """Near-uniform low-density mixture of A and B + noise. Droplets and their internal morphology must both be
    SELF-organized. The A:B ratio is drawn per seed, so different seeds may settle into different internal states."""
    rng = np.random.default_rng(seed)
    n = sp.size
    rho = np.clip(0.25 * sp.rho_max + 0.02 * rng.standard_normal((n, n)), 0.0, sp.rho_max)
    fA = float(rng.uniform(0.35, 0.65))
    A = np.clip(rho * fA + 0.03 * rng.standard_normal((n, n)), 0.0, None)
    B = np.clip(rho - A, 0.0, None)
    tot = A + B
    C = np.zeros((tr.n_cohorts, n, n))
    ys = np.arange(n)[:, None] * np.ones((1, n))
    for q in range(tr.n_spatial):
        C[q] = np.where(((ys * tr.n_spatial) // n) % tr.n_spatial == q, tot, 0.0)
    return MAState(A, B, np.zeros((n, n)), np.full((n, n), sp.N0), C, 0)


def r7(st: MAState, rho_max: float) -> dict:
    rho = st.rho
    n = rho.shape[0]
    pr = participation_ratio(rho)
    occ = {t: float((rho > t * rho_max).mean()) for t in THRESHOLD_BAND}
    ergs = {t: entity_radius_of_gyration(rho, t * rho_max)[0] for t in THRESHOLD_BAND}
    ents = detect(st, DET, rho_max)
    mass = float(rho.sum())
    localized = bool(mass > 1e-3 and pr <= PR_MAX
                     and all(v <= RG_MAX for v in ergs.values())
                     and all(v <= OCC_MAX for v in occ.values()))
    return {"pr": pr, "occ": occ, "entity_rg": ergs, "mass": mass,
            "n_entities": len(ents), "localized": localized}


def r7_unit(law_index: int, seed: int) -> dict:
    sp = ma_law(law_index)
    eng = MultiEngine(sp, TRACER)
    st = seed_state(sp, TRACER, seed)
    for _ in range(T_STAR):
        st = eng.step(st)
        if not np.isfinite(st.A).all():
            return {"law_index": law_index, "seed": seed, "diverged": True, "localized": False}
    d0 = r7(st, sp.rho_max)
    snaps = eng.simulate(st, WINDOW, CADENCE)[1:]
    ds = [r7(s, sp.rho_max) for s in snaps]
    ents = detect(st, DET, sp.rho_max)
    phen = [e.phenotype.tolist() for e in ents]
    return {"law_index": law_index, "seed": seed, "diverged": False,
            "localized_at_t_star": d0["localized"],
            "localized_all_window": bool(d0["localized"] and all(d["localized"] for d in ds)),
            "pr": d0["pr"], "n_entities": d0["n_entities"], "mass": d0["mass"],
            "entity_phenotypes": phen, "f_A": [e.f_A for e in ents],
            "spec": {k: getattr(sp, k) for k in BOX}}


R8_SEEDS = tuple(range(7101, 7109))     # 8 entirely unseen seeds (screen used 6001; EXP-CH used 5001-5005/7001-7002)
R8_WINDOW = 1200
R8_CADENCE = 100


def identity_trajectory(law_index: int, seed: int, lam_override: float | None = None) -> list[list[float]]:
    """Phenotype trajectory of the LARGEST entity of one seed = one candidate INDIVIDUAL under the frozen law."""
    from dataclasses import replace
    sp = ma_law(law_index)
    if lam_override is not None:
        sp = replace(sp, lam=lam_override)
    eng = MultiEngine(sp, TRACER)
    st = seed_state(sp, TRACER, seed)
    for _ in range(T_STAR):
        st = eng.step(st)
    traj = []
    for s in eng.simulate(st, R8_WINDOW, R8_CADENCE):
        es = detect(s, DET, sp.rho_max)
        if not es:
            continue
        traj.append(max(es, key=lambda e: e.size).phenotype.tolist())
    return traj


def r8_ab(law_index: int, lam_override: float | None = None) -> dict:
    """R8-A (diversity) and R8-B (predictive identity) on entirely unseen seeds.
    lam_override=0.0 is the built-in NEGATIVE CONTROL: demixing off -> one entity type -> both gates MUST fail."""
    import numpy as _np
    from ..identity.gates import r8a_diversity, r8b_predictive_identity
    trajs = []
    for sd in R8_SEEDS:
        t = identity_trajectory(law_index, sd, lam_override)
        if len(t) >= 6:
            trajs.append(_np.asarray(t))
    if len(trajs) < 3:
        return {"law_index": law_index, "lam_override": lam_override, "n_entities": len(trajs),
                "insufficient": True}
    T = min(t.shape[0] for t in trajs)
    trajs = [t[:T] for t in trajs]
    h = T // 2
    a = r8a_diversity(trajs)
    b = r8b_predictive_identity([t[:h] for t in trajs], [t[h:] for t in trajs])
    return {"law_index": law_index, "lam_override": lam_override, "n_entities": len(trajs),
            "n_obs_per_entity": T, "insufficient": False, "R8A": a, "R8B": b}
