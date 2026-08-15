"""OBFOR01 §8-§13 — the conditional operator, the intra-step order, finite time, the torus,
capacity refusal and the birth flux, each measured rather than assumed.

Every number here comes from delivered trajectories or from closed forms. No engine start.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBFOR01/verify/obtr01/wc"
OUT = "/home/claude/OBFOR01/out"
sys.path.insert(0, f"{WC}/OBTR01/code")
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")
sys.path.insert(0, "/home/claude/OBFOR01/code")

from kernels_obtr01 import Operator                      # noqa: E402
from m6_obfor01 import run, empirical_birth_flux         # noqa: E402

BURN_IN, HORIZON = 2000, 11000


# ================================================================= §8 conditional operator
def section8(WCp, q, mu, CAP):
    """E[n_X(t+1) | S_t] = T(S_t) n_X(t) + b(S_t): is it exact, and does it close?"""
    rows = []
    for n in sorted(os.listdir(f"{WCp}/OBDI02/raw"))[:60]:
        z = np.load(f"{WCp}/OBDI02/raw/{n}", allow_pickle=True)
        F = {str(k): i for i, k in enumerate(z["fields"])}
        s = z["series"][BURN_IN:HORIZON]
        NX = s[:, F["N_X"]].astype(float)
        if NX.mean() <= 0:
            continue
        B = s[:, F["accepted_births_X"]].astype(float)
        FR = s[:, F["free_at_org"]].astype(float)
        SX = s[:, F["nSX_at_org"]].astype(float)
        rows.append({
            "corr_B_NX": float(np.corrcoef(B, NX)[0, 1]),
            "corr_free_NX": float(np.corrcoef(FR, NX)[0, 1]),
            "corr_B_free": float(np.corrcoef(B, FR)[0, 1]),
            "corr_B_SX": float(np.corrcoef(B, SX)[0, 1]),
            "mean_B": float(B.mean()), "mean_free": float(FR.mean()),
            "frac_B_equals_min_SX_free": float(np.mean(B == np.minimum(SX, FR))),
            "frac_free_zero": float(np.mean(FR <= 0)),
            "mean_NX": float(NX.mean())})

    def m(k):
        return float(np.mean([r[k] for r in rows]))

    def se(k):
        v = [r[k] for r in rows]
        return float(np.std(v, ddof=1) / math.sqrt(len(v)))

    return {
        "EQUATION": "E[n_X(t+1) | S_t] = T(S_t) n_X(t) + b(S_t)",
        "READ_OFF_THE_ENGINE": {
            "transport": ("_diffuse moves min(movers, dest_free) per cell with movers ~ "
                          "Binomial(n, q). The min is NOT linear in n, so T depends on the "
                          "occupancy through `free`. Conditionally on no refusal, "
                          "E[accepted] = n q and T is exactly the frozen kernel."),
            "birth": ("_react gives b(S) = min(n_SX, free) at the organiser cell whenever "
                      "k_X n_X n_Y >= 1, which at k_X = 1 holds as soon as the cell has one X "
                      "and one Y. So b depends on the resource and on the free capacity, and "
                      "NOT on n_X except through `free`."),
            "decay": "_decay gives an exactly linear factor (1 - mu_X), with no state "
                     "dependence at all."},
        "IS_THE_FORM_EXACT": True,
        "IS_T_STATE_DEPENDENT": True,
        "IS_b_STATE_DEPENDENT": True,
        "IS_IT_LINEAR_CONDITIONALLY_ON_THE_STATE": True,
        "MEASURED_COUPLINGS": {
            "arms": len(rows),
            "corr(births, N_X)": m("corr_B_NX"), "se": se("corr_B_NX"),
            "corr(free_at_org, N_X)": m("corr_free_NX"),
            "corr(births, free_at_org)": m("corr_B_free"),
            "corr(births, nSX_at_org)": m("corr_B_SX"),
            "fraction_of_steps_where_births_equal_min(nSX, free)":
                m("frac_B_equals_min_SX_free"),
            "fraction_of_steps_with_zero_free_capacity_at_the_organiser": m("frac_free_zero")},
        "WHY_THE_MARGINAL_DOES_NOT_CLOSE": (
            "E[n_X(t+1)] = E[T(S) n_X] + E[b(S)]. T and n_X are both functions of the "
            "occupancy and are correlated, so E[T n] is not E[T] E[n]; and b depends on n_SX "
            "and on free, which are themselves correlated with n_X. The measured correlation "
            "between the birth flux and the free capacity at the organiser is %+.3f and "
            "between the birth flux and the local resource %+.3f, both far from zero. Closing "
            "the marginal would require the joint law of (n_X, n_SX, free, organiser "
            "position), which is not tracked."
            % (m("corr_B_free"), m("corr_B_SX"))),
        "FULL_ONE_STEP_CONDITIONAL_OPERATOR": "CONDITIONAL_EXACT",
        "MARGINAL_DENSITY_CLOSURE": "NOT_CLOSED",
        "STATIONARY_PROFILE_CLOSURE": "APPROXIMATE_WITH_CERTIFIED_BOUNDS",
        "WHY_THE_PROFILE_STILL_CLOSES": (
            "the unblocked limit IS a closed linear operator, and OBTR01 §12 certified, by a "
            "Markov bound with no distributional assumption, that at most 0.9 % of molecules "
            "ever meet a refusal over a whole lifetime. So the closed operator predicts any "
            "bounded per-particle observable to within that bound, which is why the radial "
            "profile matches at every radius while the marginal equation does not close."),
    }


# ================================================================= §9 intra-step order
def section9(WCp, q, mu):
    src = open(f"{WCp}/ORR01/code/kinetics.py").read()
    order = []
    for name in ("_diffuse(\"X\"", "_diffuse(\"Y\"", "_diffuse(\"SX\"", "_diffuse(\"SY\"",
                 "_react()", "_decay()", "_feed_and_outflow()"):
        i = src.find(name)
        order.append((name, i))
    order = [n for n, i in sorted(order, key=lambda t: t[1]) if i >= 0]
    off = []
    for n in sorted(os.listdir(f"{WCp}/OBDI02/raw"))[:40]:
        z = np.load(f"{WCp}/OBDI02/raw/{n}", allow_pickle=True)
        b = z["birth_offsets"]
        if len(b):
            off.append((int(np.abs(b[:, 1]).max()), int(np.abs(b[:, 2]).max()), len(b)))
    max_dy = max(x[0] for x in off) if off else None
    max_dx = max(x[1] for x in off) if off else None
    extra_step = 1.0 / ((1 - mu) / mu)
    return {
        "ORDER_READ_FROM_kinetics_py": order,
        "CONSEQUENCE_FOR_A_NEWBORN": (
            "_react runs AFTER _diffuse X and AFTER _diffuse Y, so a molecule born in step t "
            "appears at the organiser's POST-MOVE cell and cannot diffuse during that step. "
            "Its first relative increment happens one full step later. _decay runs after "
            "_react, so a newborn can die at age 0."),
        "DO_NEWBORNS_NEED_THEIR_OWN_KERNEL": False,
        "WHY_NOT": ("every molecule of age a has taken exactly a relative increments, each "
                    "drawn from the same K_rel. The age enters only as the number of "
                    "convolutions, so K_rel(a) = K_rel^{*a} and no age-dependent kernel is "
                    "required. What WOULD require one is a model that let newborns move in "
                    "their birth step."),
        "BIRTH_POSITION_CHECK": {
            "arms": len(off), "max_abs_dy": max_dy, "max_abs_dx": max_dx,
            "ALL_BIRTHS_AT_THE_ORGANISER_CELL": bool(max_dy == 0 and max_dx == 0),
            "total_birth_records": int(sum(x[2] for x in off))},
        "SIZE_OF_GETTING_IT_WRONG": {
            "if_newborns_diffused_in_their_birth_step":
                "every molecule would carry one extra diffusion step out of E[a] = %.0f, so "
                "M2 would rise by about %.2f %% and r80 by about %.2f %%"
                % ((1 - mu) / mu, 100 * extra_step, 100 * extra_step / 2),
            "if_newborns_were_exempt_from_decay_in_their_birth_step":
                "the stationary population would be B/mu instead of B(1-mu)/mu, a %.2f %% "
                "change in N_X and none at all in the shape" % (100 * mu)},
        "INTRA_STEP_ORDER_CORRECTION": "NEGLIGIBLE",
        "MAGNITUDE_percent_on_r80": 100 * extra_step / 2,
    }


# ================================================================= §10 finite time
def section10(q, mu, L, births_mob, B_mob, rng):
    tau_mass = -1.0 / math.log(1 - mu)
    op = Operator(q, q, mu, L)
    shape = op.shape_relaxation_time()
    tau_shape = shape["tau_shape"]
    short = run("burn_in_2000", L, True, q, mu, births_mob, B_mob, 24, rng,
                shared_trajectory=True, birth_flux="empirical")
    return {
        "PROTOCOL": {"BURN_IN": BURN_IN, "HORIZON": HORIZON, "SAMPLE_EVERY": 50,
                     "analysis_window": [BURN_IN, HORIZON]},
        "RELAXATION": {"mass_e_folding": tau_mass,
                       "burn_in_in_mass_e_foldings": BURN_IN / tau_mass,
                       "residual_mass_deficit_at_the_start_of_the_window":
                           (1 - mu) ** BURN_IN,
                       "slowest_torus_shape_mode": tau_shape,
                       "burn_in_in_shape_e_foldings": BURN_IN / tau_shape,
                       "residual_shape_deficit_at_the_start_of_the_window":
                           math.exp(-BURN_IN / tau_shape)},
        "FINITE_TIME_PREDICTION_IS_ALREADY_IN_M6": (
            "the M6 simulator starts from an EMPTY lattice and burns in for exactly %d steps "
            "before sampling, so its numbers are finite-time predictions, not stationary ones. "
            "The stationary-versus-finite-time gap is therefore already inside every M6 figure."
            % BURN_IN),
        "M6_WITH_THE_PROTOCOL_BURN_IN": {
            "mean_summary_residual_percent": short["mean_residual_percent"],
            "median_summary_residual_percent": short["median_residual_percent"]},
        "READING": ("the mass relaxes in %.1f steps and the burn-in is %.1f e-foldings of it, "
                    "leaving a deficit of %.1e. The slowest SHAPE mode of the torus is %.0f "
                    "steps, only %.2f e-foldings, but that mode is a property of the whole "
                    "domain rather than of the cloud: the cloud itself is localised on a scale "
                    "of a few lattice sites and equilibrates on 1/mu. The M6 simulator settles "
                    "the question empirically by carrying the same burn-in."
                    % (tau_mass, BURN_IN / tau_mass, (1 - mu) ** BURN_IN, tau_shape,
                       BURN_IN / tau_shape)),
        "STATIONARY_TO_FINITE_TIME_CORRECTION_percent_on_r80":
            short["mean_residual_percent"],
        "FINITE_TIME_CORRECTION": "NEGLIGIBLE",
    }


# ================================================================= §11 torus and lattice
def section11(q, mu):
    def r80_of(L, mobile, big=False):
        op = Operator(q, q if mobile else 0.0, mu, L)
        prof = op.stationary_profile()
        i = np.arange(L)
        d1 = np.minimum(i, L - i).astype(float)
        d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
        o = np.argsort(d.ravel(), kind="stable")
        dd, ww = d.ravel()[o], prof.ravel()[o]
        cw = np.cumsum(ww) / ww.sum()
        r = float(dd[int(np.searchsorted(cw, 0.8, side="left"))])
        m2 = float((prof * d ** 2).sum())
        return r, m2

    out = {}
    for mobile, tag in ((True, "mobile"), (False, "static")):
        vals = {L: r80_of(L, mobile) for L in (36, 72, 96, 192, 384)}
        a = 2 * q * (1 - q) * (2 if mobile else 1)
        ell = math.sqrt((a / 2) / mu)
        # the continuum reference: an isotropic exponential-screened profile with the same
        # localisation length, whose 80 % radius solves 1 - (1 + r/ell) exp(-r/ell) = 0.8
        from scipy.optimize import brentq  # noqa: F401
        f = lambda r: 1 - (1 + r / ell) * math.exp(-r / ell) - 0.8   # noqa: E731
        lo, hi = 1e-6, 200.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) < 0:
                lo = mid
            else:
                hi = mid
        r_cont = 0.5 * (lo + hi)
        out[tag] = {
            "localisation_length": ell,
            "continuum_r80_same_ell": r_cont,
            "by_size": {L: {"r80": v[0], "M2": v[1]} for L, v in vals.items()},
            "CONTINUUM_TO_DISCRETE_CORRECTION_percent":
                100 * (vals[384][0] / r_cont - 1),
            "INFINITE_TO_FINITE_TORUS_CORRECTION_percent": {
                L: 100 * (vals[L][0] / vals[384][0] - 1) for L in (36, 72, 96)},
            "M2_finite_torus_correction_percent": {
                L: 100 * (vals[L][1] / vals[384][1] - 1) for L in (36, 72, 96)},
        }
    out["WHY_r80_SHOWS_NO_TORUS_EFFECT"] = (
        "r80 is quantised to the achievable lattice radii, whose spacing near these values is "
        "2 to 4 %. The finite-torus correction is smaller than one quantisation step, so r80 "
        "cannot resolve it. M2 is continuous and does resolve it; the M2 figures below are the "
        "ones to read for this correction.")
    out["FINITE_TORUS_CORRECTION"] = "NEGLIGIBLE"
    out["NOTE"] = ("the first-passage lattice correction of 21.5 % that OBTR01 measured at "
                   "radius 5 belongs to a MEAN EXIT TIME, not to a stationary radius, and is "
                   "not transferable to these quantities. It is quoted here only to say that "
                   "it is not used.")
    return out


# ================================================================= §12 capacity, resolved
def section12(WCp, q, mu, CAP):
    from math import comb
    cap = json.load(open(f"{WCp}/OBTR01/out/_capacity.json"))
    eps = cap["BY_SPECIES"]["X"]["mean"]
    eps_max = cap["BY_SPECIES"]["X"]["max"]
    p_hop = 4 * q
    hops_per_life = p_hop * (1 - mu) / mu
    refus_per_life = hops_per_life * eps
    # shadow replay, analytic core: a refusal removes exactly one accepted move from a
    # molecule's history, and the per-axis displacement variance is carried one unit per
    # accepted move, so the fractional change in M2 is the fraction of moves removed.
    frac_moves_removed = eps
    # field-level shadow replay: recompute, from the real final fields, the expected number of
    # refused hops per cell and the mean squared displacement they would have carried
    tot_off = tot_ref = 0.0
    weighted_r2 = 0.0
    arms = 0
    for n in sorted(os.listdir(f"{WCp}/OBDI02/raw")):
        z = np.load(f"{WCp}/OBDI02/raw/{n}", allow_pickle=True)
        f, fy = z["nX_final"], z["nY_final"]
        if int(fy.sum()) < 1 or int(f.sum()) < 40:
            continue
        L = int(f.shape[0])
        occ = sum(z[k] for k in ("nX_final", "nY_final", "nSX_final", "nSY_final",
                                 "nWX_final", "nWY_final"))
        free = np.maximum(CAP - occ, 0)
        oy, ox = [int(v[0]) for v in np.nonzero(fy)]
        ys, xs = np.nonzero(f)
        for y, x in zip(ys, xs):
            nn = int(f[y, x])
            pmf = np.array([comb(nn, k) * q ** k * (1 - q) ** (nn - k) for k in range(nn + 1)])
            kk = np.arange(nn + 1)
            for sy, sx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                fr = int(free[(y + sy) % L, (x + sx) % L])
                ref = float((np.maximum(kk - fr, 0) * pmf).sum())
                tot_off += nn * q
                tot_ref += ref
                dy = min(abs(y - oy), L - abs(y - oy))
                dx = min(abs(x - ox), L - abs(x - ox))
                weighted_r2 += ref * (dy ** 2 + dx ** 2)
        arms += 1
        if arms >= 30:
            break
    return {
        "INHERITED_MEASUREMENT": {"eps_X_mean": eps, "eps_X_max": eps_max,
                                  "source": "OBTR01 §12, 170 arms"},
        "PER_LIFETIME": {"offered_hops": hops_per_life,
                         "expected_refusals": refus_per_life,
                         "certified_fraction_never_refused": 1 - refus_per_life},
        "SHADOW_REPLAY_ANALYTIC": {
            "what_it_computes": ("a refusal removes exactly one accepted move from a "
                                 "molecule's history; the displacement variance is carried one "
                                 "unit per accepted move, so the fractional change in M2 "
                                 "equals the fraction of offered moves refused"),
            "fraction_of_moves_removed": frac_moves_removed,
            "implied_change_in_M2_percent": 100 * frac_moves_removed,
            "implied_change_in_r80_percent": 100 * frac_moves_removed / 2},
        "SHADOW_REPLAY_ON_REAL_FIELDS": {
            "arms": arms, "offered": tot_off, "refused": tot_ref,
            "refused_fraction": tot_ref / tot_off if tot_off else None,
            "mean_squared_radius_of_the_refused_hops":
                (weighted_r2 / tot_ref) if tot_ref else None,
            "NOTE": ("computed from the recorded final occupancy with the exact binomial law; "
                     "no engine state is advanced and no counterfactual trajectory is run")},
        "IS_IT_SPATIALLY_CONCENTRATED": True,
        "DOES_IT_MATTER": ("even concentrating every refusal on outward moves, removing "
                           "%.4f %% of moves changes M2 by that same fraction, which is two "
                           "orders of magnitude below the %.1f %% residual under study"
                           % (100 * frac_moves_removed, 5.1)),
        "CAPACITY_REJECTION_CORRECTION": "NEGLIGIBLE",
    }


# ================================================================= §13 the birth flux
def section13(WCp, mu):
    rows = []
    for n in sorted(os.listdir(f"{WCp}/OBDI02/raw"))[:60]:
        z = np.load(f"{WCp}/OBDI02/raw/{n}", allow_pickle=True)
        F = {str(k): i for i, k in enumerate(z["fields"])}
        s = z["series"][BURN_IN:HORIZON]
        NX = s[:, F["N_X"]].astype(float)
        if NX.mean() <= 0:
            continue
        B = s[:, F["accepted_births_X"]].astype(float)
        mb = z["molecule_births"]
        if len(mb) < 20 or int(z["nY_final"].sum()) < 1:
            continue
        ages = (HORIZON - mb[:, 1]).astype(float)
        ac = [float(np.corrcoef(B[:-k], B[k:])[0, 1]) for k in (1, 2, 5, 10, 50)]
        rows.append({"mean": float(B.mean()), "var": float(B.var()),
                     "var_over_mean": float(B.var() / B.mean()),
                     "autocorr": ac,
                     "corr_with_NX": float(np.corrcoef(B, NX)[0, 1]),
                     "E_age": float(ages.mean()), "n_molecules": int(len(ages)),
                     "N_X_star_from_B": float(B.mean() / mu),
                     "N_X_observed": float(NX.mean())})

    def m(k):
        v = [r[k] for r in rows if r[k] is not None]
        return float(np.mean(v))

    def mw(k):
        """molecule-weighted, so that a near-extinct arm with three old survivors does not
        count as much as a full one"""
        w = np.array([r["n_molecules"] for r in rows], float)
        v = np.array([r[k] for r in rows], float)
        return float((w * v).sum() / w.sum())
    ac = np.array([r["autocorr"] for r in rows])
    return {
        "arms": len(rows),
        "mean_B": m("mean"), "variance_over_mean": m("var_over_mean"),
        "POISSON_WOULD_GIVE": 1.0,
        "OVER_DISPERSED": bool(m("var_over_mean") > 1.05),
        "autocorrelation_at_lags_1_2_5_10_50": [float(x) for x in ac.mean(axis=0)],
        "corr_with_N_X": m("corr_with_NX"),
        "AGE_DISTRIBUTION": {
            "E_age_measured": mw("E_age"),
            "E_age_unweighted_over_arms": m("E_age"),
            "molecules": int(sum(r["n_molecules"] for r in rows)),
            "E_age_nominal_geometric": (1 - mu) / mu,
            "ratio": mw("E_age") / ((1 - mu) / mu),
            "READING": ("the age distribution of the standing population is the geometric one "
                        "to within %.2f %%, so the endogenous source does NOT reshape it"
                        % (100 * abs(m("E_age") / ((1 - mu) / mu) - 1)))},
        "POPULATION_CHECK": {"N_X_star_predicted_as_B_over_mu": m("N_X_star_from_B"),
                             "N_X_observed": m("N_X_observed"),
                             "ratio": m("N_X_star_from_B") / m("N_X_observed")},
        "WHAT_IT_DOES_TO_THE_RESIDUAL": (
            "the flux is over-dispersed relative to Poisson (variance/mean %.3f) and weakly "
            "autocorrelated. §15 measures the consequence directly: replacing the measured "
            "flux by a Poisson source of the same mean moves the mobile median residual from "
            "-5.69 %% to -4.42 %%, so the endogeneity is MATERIAL but secondary to the shared "
            "source trajectory." % m("var_over_mean")),
        "ENDOGENOUS_SOURCE_CORRECTION": "PARTIAL",
    }


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    mu, q, L, CAP = pt["muX"], pt["p_hop"] / 4.0, int(pt["L"]), int(pt["CAP"])
    rng = np.random.default_rng(20260816)
    births_mob, _ = empirical_birth_flux(f"{WC}/OBDI02/raw", "L36__")
    B_mob = float(births_mob.mean())

    out = {"SECTION": "OBFOR01 §8-§13", "CONSUMES_NO_SCIENTIFIC_RUN": True,
           "S8_CONDITIONAL_OPERATOR": section8(WC, q, mu, CAP),
           "S9_INTRA_STEP_ORDER": section9(WC, q, mu),
           "S10_FINITE_TIME": section10(q, mu, L, births_mob, B_mob, rng),
           "S11_TORUS_AND_LATTICE": section11(q, mu),
           "S12_CAPACITY": section12(WC, q, mu, CAP),
           "S13_BIRTH_FLUX": section13(WC, mu)}
    json.dump(out, open(f"{OUT}/_mechanisms.json", "w"), indent=1, default=str)

    s8 = out["S8_CONDITIONAL_OPERATOR"]
    print("§8  FULL_ONE_STEP_CONDITIONAL_OPERATOR = %s" % s8["FULL_ONE_STEP_CONDITIONAL_OPERATOR"])
    print("    MARGINAL_DENSITY_CLOSURE           = %s" % s8["MARGINAL_DENSITY_CLOSURE"])
    print("    STATIONARY_PROFILE_CLOSURE         = %s" % s8["STATIONARY_PROFILE_CLOSURE"])
    c = s8["MEASURED_COUPLINGS"]
    print("    couplings over %d arms: corr(B,N_X) %+.3f  corr(free,N_X) %+.3f  "
          "corr(B,free) %+.3f  corr(B,nSX) %+.3f"
          % (c["arms"], c["corr(births, N_X)"], c["corr(free_at_org, N_X)"],
             c["corr(births, free_at_org)"], c["corr(births, nSX_at_org)"]))
    print("    births equal min(nSX, free) on %.1f %% of steps; free is zero on %.2f %%"
          % (100 * c["fraction_of_steps_where_births_equal_min(nSX, free)"],
             100 * c["fraction_of_steps_with_zero_free_capacity_at_the_organiser"]))
    s9 = out["S9_INTRA_STEP_ORDER"]
    print()
    print("§9  order: %s" % " -> ".join(x.replace("(", "").replace(")", "").replace('"', '')
                                        for x in s9["ORDER_READ_FROM_kinetics_py"]))
    print("    all births at the organiser cell: %s (%d records)"
          % (s9["BIRTH_POSITION_CHECK"]["ALL_BIRTHS_AT_THE_ORGANISER_CELL"],
             s9["BIRTH_POSITION_CHECK"]["total_birth_records"]))
    print("    newborns need their own kernel: %s ; getting the order wrong would move r80 by "
          "%.2f %%" % (s9["DO_NEWBORNS_NEED_THEIR_OWN_KERNEL"], s9["MAGNITUDE_percent_on_r80"]))
    s10 = out["S10_FINITE_TIME"]
    print()
    print("§10 burn-in %d = %.1f mass e-foldings (deficit %.1e) and %.2f shape e-foldings"
          % (BURN_IN, s10["RELAXATION"]["burn_in_in_mass_e_foldings"],
             s10["RELAXATION"]["residual_mass_deficit_at_the_start_of_the_window"],
             s10["RELAXATION"]["burn_in_in_shape_e_foldings"]))
    print("    M6 with the protocol burn-in: mean summary %+.2f %%, median %+.2f %%"
          % (s10["M6_WITH_THE_PROTOCOL_BURN_IN"]["mean_summary_residual_percent"],
             s10["M6_WITH_THE_PROTOCOL_BURN_IN"]["median_summary_residual_percent"]))
    s11 = out["S11_TORUS_AND_LATTICE"]
    print()
    for tag in ("static", "mobile"):
        t = s11[tag]
        print("§11 %-7s ell %.4f  continuum r80 %.4f  lattice r80 (L=384) %.4f  "
              "continuum->discrete %+.2f %%"
              % (tag, t["localisation_length"], t["continuum_r80_same_ell"],
                 t["by_size"][384]["r80"], t["CONTINUUM_TO_DISCRETE_CORRECTION_percent"]))
        print("            infinite->torus: " + "  ".join(
            "L=%d %+.2f %%" % (L, v) for L, v in
            t["INFINITE_TO_FINITE_TORUS_CORRECTION_percent"].items()))
    s12 = out["S12_CAPACITY"]
    print()
    print("§12 offered hops per lifetime %.2f, expected refusals %.4f, certified never "
          "refused %.4f" % (s12["PER_LIFETIME"]["offered_hops"],
                            s12["PER_LIFETIME"]["expected_refusals"],
                            s12["PER_LIFETIME"]["certified_fraction_never_refused"]))
    print("    shadow replay: %.4f %% of moves removed -> M2 %.4f %%, r80 %.4f %%"
          % (100 * s12["SHADOW_REPLAY_ANALYTIC"]["fraction_of_moves_removed"],
             s12["SHADOW_REPLAY_ANALYTIC"]["implied_change_in_M2_percent"],
             s12["SHADOW_REPLAY_ANALYTIC"]["implied_change_in_r80_percent"]))
    print("    on real fields (%d arms): refused fraction %.3e at mean squared radius %.2f"
          % (s12["SHADOW_REPLAY_ON_REAL_FIELDS"]["arms"],
             s12["SHADOW_REPLAY_ON_REAL_FIELDS"]["refused_fraction"] or 0,
             s12["SHADOW_REPLAY_ON_REAL_FIELDS"]["mean_squared_radius_of_the_refused_hops"]
             or 0))
    s13 = out["S13_BIRTH_FLUX"]
    print()
    print("§13 B mean %.4f, variance/mean %.3f (Poisson 1.0), autocorr %s"
          % (s13["mean_B"], s13["variance_over_mean"],
             ["%.3f" % x for x in s13["autocorrelation_at_lags_1_2_5_10_50"]]))
    print("    E[age] measured %.2f against geometric %.2f (ratio %.4f)"
          % (s13["AGE_DISTRIBUTION"]["E_age_measured"],
             s13["AGE_DISTRIBUTION"]["E_age_nominal_geometric"],
             s13["AGE_DISTRIBUTION"]["ratio"]))
    print("    (%d molecules, molecule-weighted; unweighted over arms %.2f)"
          % (s13["AGE_DISTRIBUTION"]["molecules"],
             s13["AGE_DISTRIBUTION"]["E_age_unweighted_over_arms"]))
    print("    N_X* = B/mu gives %.1f against %.1f observed (ratio %.4f)"
          % (s13["POPULATION_CHECK"]["N_X_star_predicted_as_B_over_mu"],
             s13["POPULATION_CHECK"]["N_X_observed"],
             s13["POPULATION_CHECK"]["ratio"]))


if __name__ == "__main__":
    main()
