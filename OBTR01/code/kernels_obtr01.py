"""OBTR01 §6.1, §7, §8 — the exact one-step displacement law, the relative kernel, and the
source-transport-decay operator, derived from the engine and validated four ways.

WHAT THE ENGINE ACTUALLY DOES (kinetics.World._diffuse, read verbatim):

    for shift, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):        # the frozen order
        n = self.n[sname]
        movers   = rng.binomial(max(n, 0), p_hop / 4)
        dest_free = roll(self.free(), -shift, axis=ax)
        accepted  = min(movers, max(dest_free, 0))
        self.n[sname] = n - accepted + roll(accepted, shift, axis=ax)

Four SEQUENTIAL passes per step, each acting on the field left by the previous one. Three
consequences that the historical `D = p_hop/4` convention missed:

  1. a molecule that moves +y in pass 1 is eligible to move -y in pass 2 and returns to its
     origin, so the per-axis displacement is a DIFFERENCE of two Bernoulli(q) variables;
  2. passes 3 and 4 act on the x axis after passes 1 and 2 acted on y, so a molecule may move
     on BOTH axes in one step: the one-step law has DIAGONAL support and factorises;
  3. acceptance is `min(movers, dest_free)` PER CELL, not per molecule: when capacity bites it
     truncates a whole batch, which is not a per-particle thinning.

The unblocked law is therefore a product measure with, per axis,
     P(+1) = q(1-q),  P(-1) = q(1-q),  P(0) = 1 - 2q(1-q),   q = p_hop/4
whence a = Var = 2q(1-q) and D = a/2 = q(1-q). NOT p_hop/4.
"""
from __future__ import annotations

import itertools
import json
import math
import sys

import numpy as np

WC = "/home/claude/OBTR01/verify/obdca01/wc"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, f"{WC}/ORR01/code")
sys.path.insert(0, f"{WC}/OBTC02/code")

# Imported from the VERIFIED offline working copy first, so that these names are already in
# sys.modules when protocol_obtc02 pushes its own /home/claude/... paths to the front of
# sys.path at import time. `_import_provenance` then records, for every module actually used,
# the file that was loaded and its digest, so the claim is checked rather than assumed.
import lawspec_v2 as V2         # noqa: E402
import observe as OBS           # noqa: E402
import engine_obtc as EN        # noqa: E402
import guard_obtc as GD         # noqa: E402
import source_operator as OP    # noqa: E402
import protocol_obtc02 as PC    # noqa: E402


def _import_provenance():
    import hashlib
    import os
    rec = {}
    for name, mod in (("lawspec_v2", V2), ("observe", OBS), ("engine_obtc", EN),
                      ("guard_obtc", GD), ("source_operator", OP), ("protocol_obtc02", PC)):
        f = os.path.abspath(mod.__file__)
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        rec[name] = {"file": f, "sha256": h, "inside_verified_working_copy": f.startswith(WC)}
    rec["ALL_FROM_VERIFIED_WORKING_COPY"] = all(
        v["inside_verified_working_copy"] for v in rec.values() if isinstance(v, dict))
    return rec


# ------------------------------------------------------------------ 1. exact enumeration
def axis_law(q):
    """Exact law of the displacement on ONE axis after the two passes of that axis."""
    return {+1: q * (1.0 - q), -1: (1.0 - q) * q, 0: (1.0 - q) ** 2 + q * q}


def one_step_kernel(q):
    """Exact unblocked one-step displacement law, by enumerating the four passes."""
    lawy, lawx = axis_law(q), axis_law(q)
    K = {}
    for dy, py in lawy.items():
        for dx, px in lawx.items():
            K[(dy, dx)] = py * px
    return K


def enumerate_four_passes(q):
    """Brute force over the 2^4 outcomes of the four Bernoulli draws, to confirm the algebra
    rather than assert it. Pass order is (+y, -y, +x, -x)."""
    K = {}
    for b in itertools.product((0, 1), repeat=4):
        p = 1.0
        for bit in b:
            p *= q if bit else (1.0 - q)
        dy = b[0] - b[1]
        dx = b[2] - b[3]
        K[(dy, dx)] = K.get((dy, dx), 0.0) + p
    return K


def moments(K):
    m1y = sum(dy * p for (dy, _), p in K.items())
    m1x = sum(dx * p for (_, dx), p in K.items())
    m2y = sum(dy * dy * p for (dy, _), p in K.items())
    m2x = sum(dx * dx * p for (_, dx), p in K.items())
    cross = sum(dy * dx * p for (dy, dx), p in K.items())
    return {"mass": sum(K.values()), "mean_y": m1y, "mean_x": m1x,
            "var_y": m2y - m1y ** 2, "var_x": m2x - m1x ** 2, "cov": cross - m1y * m1x,
            "second_moment_r2": m2y + m2x}


def phi_characteristic(q, ky, kx):
    a = 2.0 * q * (1.0 - q)
    return (1.0 - a * (1.0 - math.cos(ky))) * (1.0 - a * (1.0 - math.cos(kx)))


def phi_from_kernel(K, ky, kx):
    return sum(p * math.cos(dy * ky + dx * kx) for (dy, dx), p in K.items())


# ------------------------------------------------------------------ 2. engine Monte Carlo
def engine_displacement_law(p_hop, n_draws=4000, L=64, seed=13):
    """Measure the one-step law from the ENGINE itself, in TEST mode (no start is opened, no
    ledger entry is made, no scientific run is consumed). A single tagged molecule is placed on
    an otherwise empty lattice so capacity can never bite, and one step of `_diffuse` is taken.
    """
    GD.set_test_mode()
    rng = np.random.default_rng(seed)
    counts = {}
    sp = PC.spec_for(L)
    for _ in range(n_draws):
        w = EN.fresh_world(int(rng.integers(1, 2 ** 31)), sp,
                           lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                           exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir",
                           rec=OBS.Recorder(), track=False, organiser_off_at=None)
        for s in w.n:
            w.n[s][:] = 0
        y0, x0 = L // 2, L // 2
        w.n["X"][y0, x0] = 1
        w._diffuse("X", p_hop)
        ys, xs = np.nonzero(w.n["X"])
        assert len(ys) == 1 and w.n["X"].sum() == 1
        dy = int(ys[0]) - y0
        dx = int(xs[0]) - x0
        dy = (dy + L // 2) % L - L // 2
        dx = (dx + L // 2) % L - L // 2
        counts[(dy, dx)] = counts.get((dy, dx), 0) + 1
    GD.set_experiment_mode()
    return {k: v / n_draws for k, v in counts.items()}, n_draws


# ------------------------------------------------------------------ 3. the relative kernel
def relative_kernel(qX, qY):
    """delta = dX - dY. The two calls to _diffuse are consecutive and, in the unblocked limit,
    draw independent binomials, so the relative law is the correlation of the two kernels."""
    KX, KY = one_step_kernel(qX), one_step_kernel(qY)
    R = {}
    for (ay, ax), pa in KX.items():
        for (by, bx), pb in KY.items():
            d = (ay - by, ax - bx)
            R[d] = R.get(d, 0.0) + pa * pb
    return R


def relative_axis_variance(qX, qY):
    return 2.0 * qX * (1.0 - qX) + 2.0 * qY * (1.0 - qY)


# ------------------------------------------------------------------ 3bis. symmetries
def symmetry_tests(K, tol=1e-15):
    """The frozen pass order is (+y, -y, +x, -x). Nothing in it distinguishes a sign or an
    axis, so the law must be invariant under y -> -y, x -> -x and the axis swap. These are
    consequences of the algebra, so failing them would mean the algebra is wrong."""
    def g(d):
        return K.get(d, 0.0)
    return {
        "reflection_y": max(abs(g((dy, dx)) - g((-dy, dx))) for dy, dx in K),
        "reflection_x": max(abs(g((dy, dx)) - g((dy, -dx))) for dy, dx in K),
        "axis_swap": max(abs(g((dy, dx)) - g((dx, dy))) for dy, dx in K),
        "point_symmetry": max(abs(g((dy, dx)) - g((-dy, -dx))) for dy, dx in K),
        "ALL_WITHIN_TOL": bool(max(
            max(abs(g((dy, dx)) - g((-dy, dx))) for dy, dx in K),
            max(abs(g((dy, dx)) - g((dy, -dx))) for dy, dx in K),
            max(abs(g((dy, dx)) - g((dx, dy))) for dy, dx in K),
        ) <= tol),
    }


# ------------------------------------------------------------------ 3ter. diffusion convention
def engine_msd(p_hop, steps=400, walkers=240, L=128, seed=71):
    """The convention test proper. `a` is a PER-STEP per-axis variance, so the engine's MSD
    must grow as a * t on each axis, NOT as (p_hop/4) * t and not as 2 D t with D = p_hop/4.
    Measured on an otherwise empty lattice, in TEST mode, with the tracker off."""
    GD.set_test_mode()
    rng = np.random.default_rng(seed)
    sp = PC.spec_for(L)
    disp = []
    for _ in range(walkers):
        w = EN.fresh_world(int(rng.integers(1, 2 ** 31)), sp,
                           lawspec=V2.LAWSPEC_V2_EXCHANGE, rng_mode="split_feed_stream",
                           exchangeable=V2.EXCHANGEABLE_DEFAULT, insert_mode="reservoir",
                           rec=OBS.Recorder(), track=False, organiser_off_at=None)
        for s in w.n:
            w.n[s][:] = 0
        y0, x0 = L // 2, L // 2
        w.n["X"][y0, x0] = 1
        for _t in range(steps):
            w._diffuse("X", p_hop)
        ys, xs = np.nonzero(w.n["X"])
        assert len(ys) == 1
        dy = (int(ys[0]) - y0 + L // 2) % L - L // 2
        dx = (int(xs[0]) - x0 + L // 2) % L - L // 2
        disp.append((dy, dx))
    GD.set_experiment_mode()
    d = np.asarray(disp, float)
    msd_axis = float((d ** 2).mean())          # pooled over the two axes
    a = 2.0 * (p_hop / 4.0) * (1.0 - p_hop / 4.0)
    n = d.size                                  # walkers * 2 axes
    # variance of the per-axis mean square, for a sum of `steps` iid axis increments
    return {"steps": steps, "walkers": walkers, "axis_samples": n,
            "msd_per_axis_measured": msd_axis,
            "msd_per_axis_predicted_a_t": a * steps,
            "msd_per_axis_historical_p_hop_over_4_times_t": (p_hop / 4.0) * steps,
            "relative_error_vs_corrected": msd_axis / (a * steps) - 1.0,
            "relative_error_vs_historical": msd_axis / ((p_hop / 4.0) * steps) - 1.0,
            "se_of_msd": float(d.reshape(-1).var(ddof=1) / math.sqrt(n / 2.0)) if n > 2 else None,
            "z_vs_corrected": float((msd_axis - a * steps)
                                    / (np.std(d.reshape(-1) ** 2, ddof=1) / math.sqrt(n)))}


# ------------------------------------------------------------------ 4. the operator
class Operator:
    """rho_{t+1} = (1 - mu) K_rel rho_t + B_t delta_0, in the organiser frame."""

    def __init__(self, qX, qY, mu, L):
        self.qX, self.qY, self.mu, self.L = qX, qY, mu, int(L)
        self.a_rel = relative_axis_variance(qX, qY)
        self.a_X = 2.0 * qX * (1.0 - qX)

    def phi(self, a=None):
        a = self.a_rel if a is None else a
        L = self.L
        k = 2.0 * np.pi * np.arange(L) / L
        p1 = 1.0 - a * (1.0 - np.cos(k))
        return p1[:, None] * p1[None, :]

    def eigenvalues(self, a=None):
        """lambda(k) = (1 - mu) phi(k): the spectrum of the unblocked operator."""
        return (1.0 - self.mu) * self.phi(a)

    def resolvent_at_1(self, a=None):
        """(I - (1-mu) K)^{-1} in Fourier: the Green function of the stationary problem."""
        return 1.0 / (1.0 - self.eigenvalues(a))

    def stationary_profile(self, a=None):
        g = np.real(np.fft.ifft2(self.resolvent_at_1(a)))
        g = np.maximum(g, 0.0)
        return g / g.sum()

    def green_zero(self, a=None):
        """G(0): the expected number of visits to the origin, unit source, with mortality."""
        return float(np.real(np.fft.ifft2(self.resolvent_at_1(a)))[0, 0])

    def impulse_response(self, T, a=None):
        """rho_t for a single unit released at the origin at t = 0."""
        lam = self.eigenvalues(a)
        f = np.zeros((self.L, self.L))
        f[0, 0] = 1.0
        F = np.fft.fft2(f)
        out = []
        for t in range(T + 1):
            out.append(np.real(np.fft.ifft2(F * lam ** t)))
        return out

    def step_response_mass(self, T):
        """N(t) for a source of one unit per step switched on at t = 0: geometric partial sums."""
        r = 1.0 - self.mu
        return np.array([(1.0 - r ** (t + 1)) / (1.0 - r) for t in range(T + 1)])

    def mode_relaxation_times(self, a=None):
        lam = self.eigenvalues(a)
        with np.errstate(divide="ignore"):
            tau = -1.0 / np.log(np.clip(lam, 1e-300, 1 - 1e-16))
        return tau

    def shape_relaxation_time(self, a=None):
        """The SLOWEST non-uniform mode relative to the total mass decay: the shape relaxes at
        the rate of the second eigenvalue divided by the first."""
        lam = self.eigenvalues(a)
        lam0 = lam[0, 0]
        flat = np.sort(lam.ravel())[::-1]
        lam1 = flat[1]
        return {"lambda_0": float(lam0), "lambda_1": float(lam1),
                "ratio": float(lam1 / lam0),
                "tau_shape": float(-1.0 / math.log(lam1 / lam0))}


def main():
    spec = PC.SPEC
    p_hop = float(spec["point"]["p_hop"])
    mu = float(spec["point"]["muX"])
    L = int(spec["point"]["L"])
    qX = p_hop / 4.0
    qY = p_hop / 4.0            # p_hop_Y = p_hop in the qualified LawSpec

    # ---------------------------------------------------------------- §6.1 / §7
    K_alg = one_step_kernel(qX)
    K_enum = enumerate_four_passes(qX)
    same = all(abs(K_alg[k] - K_enum.get(k, 0.0)) < 1e-15 for k in K_alg) \
        and len(K_alg) == len(K_enum)
    m = moments(K_alg)
    K_eng, n_draws = engine_displacement_law(p_hop, n_draws=4000)
    tv = 0.5 * sum(abs(K_alg.get(k, 0.0) - K_eng.get(k, 0.0))
                   for k in set(K_alg) | set(K_eng))
    se = math.sqrt(0.25 / n_draws)

    ks = [(0.0, 0.0), (0.3, 0.0), (0.0, 1.1), (0.7, 2.2), (np.pi, np.pi)]
    phi_check = [{"k": k, "closed_form": phi_characteristic(qX, *k),
                  "from_kernel": phi_from_kernel(K_alg, *k),
                  "abs_diff": abs(phi_characteristic(qX, *k) - phi_from_kernel(K_alg, *k))}
                 for k in ks]

    R = relative_kernel(qX, qY)
    mR = moments(R)
    a_rel = relative_axis_variance(qX, qY)

    # the organiser is IMMOBILE under condition S: p_hop_Y = 0, so K_Y is the point mass and
    # the relative kernel collapses onto K_X. Both are frozen regimes and both are needed.
    R_static = relative_kernel(qX, 0.0)
    mR_static = moments(R_static)
    sym_X = symmetry_tests(K_alg)
    sym_R = symmetry_tests(R)
    msd = engine_msd(p_hop)

    # ---- independent implementation already frozen in OBTC02: source_operator.Op ----------
    sp_mobile = PC.spec_for(L, immobile_organiser=False)
    sp_static = PC.spec_for(L, immobile_organiser=True)
    op_mob, op_sta = OP.Op(sp_mobile), OP.Op(sp_static)
    independent = {
        "source": "OBTC02/code/source_operator.py, frozen before this mission",
        "a_X": {"here": 2 * qX * (1 - qX), "there": op_mob.aX,
                "abs_diff": abs(2 * qX * (1 - qX) - op_mob.aX)},
        "D_X": {"here": qX * (1 - qX), "there": op_mob.DX,
                "abs_diff": abs(qX * (1 - qX) - op_mob.DX)},
        "a_relative_mobile": {"here": a_rel, "there": op_mob.a_rel,
                              "abs_diff": abs(a_rel - op_mob.a_rel)},
        "a_relative_static": {"here": relative_axis_variance(qX, 0.0), "there": op_sta.a_rel,
                              "abs_diff": abs(relative_axis_variance(qX, 0.0) - op_sta.a_rel)},
        "p_hop_Y_mobile": float(sp_mobile.p_hop_Y),
        "p_hop_Y_static": float(sp_static.p_hop_Y),
        "frozen_analytic_block": spec.get("analytic", {}),
    }
    independent["AGREES_TO_MACHINE_PRECISION"] = bool(
        max(independent[k]["abs_diff"] for k in
            ("a_X", "D_X", "a_relative_mobile", "a_relative_static")) < 1e-15)

    kernels = {
        "SECTION": "OBTR01 §6.1, §7",
        "ENGINE_RULE": ("four sequential passes per step in the frozen order "
                        "(+y, -y, +x, -x); movers ~ Binomial(n, p_hop/4) per pass; "
                        "accepted = min(movers, dest_free) PER CELL"),
        "q": qX, "p_hop": p_hop,
        "HISTORICAL_CONVENTION_D_eq_p_hop_over_4": p_hop / 4.0,
        "CORRECTED_a_per_axis": 2.0 * qX * (1.0 - qX),
        "CORRECTED_D_eq_q_times_one_minus_q": qX * (1.0 - qX),
        "RATIO_historical_over_corrected": (p_hop / 4.0) / (qX * (1.0 - qX)),
        "ONE_STEP_LAW": {str(k): v for k, v in sorted(K_alg.items())},
        "SUPPORT_SIZE": len(K_alg),
        "HAS_DIAGONAL_SUPPORT": any(dy != 0 and dx != 0 for dy, dx in K_alg),
        "ALGEBRA_MATCHES_BRUTE_FORCE_ENUMERATION": bool(same),
        "MOMENTS": m,
        "MASS_IS_ONE": abs(m["mass"] - 1.0) < 1e-15,
        "AXES_INDEPENDENT_cov_zero": abs(m["cov"]) < 1e-18,
        "ENGINE_MONTE_CARLO": {"draws": n_draws, "law": {str(k): v for k, v in
                                                         sorted(K_eng.items())},
                               "total_variation_vs_exact": tv,
                               "one_sigma_of_a_cell": se,
                               "WITHIN_3_SIGMA": bool(tv < 3 * se * len(K_alg))},
        "CHARACTERISTIC_FUNCTION_CHECK": phi_check,
        "RELATIVE_KERNEL": {"support_size": len(R), "moments": mR,
                            "a_relative_closed_form": a_rel,
                            "a_relative_from_kernel": mR["var_y"],
                            "MATCHES": abs(a_rel - mR["var_y"]) < 1e-15},
        "RELATIVE_KERNEL_STATIC_ORGANISER": {
            "condition": "S: p_hop_Y = 0, the organiser is immobile",
            "support_size": len(R_static), "moments": mR_static,
            "a_relative_closed_form": relative_axis_variance(qX, 0.0),
            "COLLAPSES_ONTO_K_X": bool(
                max(abs(R_static.get(k, 0.0) - K_alg.get(k, 0.0))
                    for k in set(R_static) | set(K_alg)) < 1e-15)},
        "SYMMETRY_TESTS": {"K_X": sym_X, "K_relative": sym_R},
        "DIFFUSION_CONVENTION_TEST": msd,
        "INDEPENDENT_IMPLEMENTATION": independent,
        "IMPORT_PROVENANCE": _import_provenance(),
        "X_KERNEL_STATUS": "CONDITIONAL_EXACT",
        "ORGANIZER_KERNEL_STATUS": "CONDITIONAL_EXACT",
        "RELATIVE_KERNEL_STATUS": "CONDITIONAL_EXACT",
        "CONDITION": ("exact conditionally on no capacity refusal. `accepted = min(movers, "
                      "dest_free)` is a per-CELL truncation, so refusal is not a per-particle "
                      "thinning and cannot be absorbed into an effective q."),
        "INTRA_STEP_ORDER": ["_diffuse X", "_diffuse Y", "_diffuse SX", "_diffuse SY",
                             "_react", "_decay", "_exchange"],
        "WHY_THE_RELATIVE_KERNEL_IS_A_CORRELATION": (
            "X and Y diffuse in two consecutive calls that draw independent binomials; they "
            "interact only through `free()`, which is the capacity term. In the unblocked limit "
            "the two displacements are independent and the law of dX - dY is the correlation "
            "of the two kernels."),
    }

    # ---------------------------------------------------------------- §8 the operator
    op = Operator(qX, qY, mu, L)
    prof = op.stationary_profile()
    lam = op.eigenvalues()
    tau_modes = op.mode_relaxation_times()
    shape = op.shape_relaxation_time()
    imp = op.impulse_response(3)
    mass_imp = [float(f.sum()) for f in imp]
    step_mass = op.step_response_mass(4000)

    def radial(pr):
        Lx = pr.shape[0]
        i = np.arange(Lx)
        d1 = np.minimum(i, Lx - i).astype(float)
        d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
        return d, pr

    d, pr = radial(prof)
    order = np.argsort(d.ravel(), kind="stable")
    dd, ww = d.ravel()[order], pr.ravel()[order]
    cw = np.cumsum(ww)
    rq = {q: float(dd[int(np.searchsorted(cw, q, side="left"))]) for q in (0.5, 0.8, 0.9)}
    m2 = float((pr * d ** 2).sum())

    operator = {
        "SECTION": "OBTR01 §8",
        "EQUATION": "rho_{t+1} = (1 - mu_X) K_rel rho_t + B_t delta_0",
        "LINEARITY": {
            "is_B_t_exogenous": False,
            "what_B_t_depends_on": ("B_t = Binomial(cand, p) with cand = min(n_SX, free) at "
                                    "the organiser cell and p = min(1, kX n_X n_Y). At kX = 1 "
                                    "and n_X >= 1 the probability saturates at 1, so B_t is "
                                    "exactly min(n_SX, free) THERE. It depends on the local "
                                    "resource and on the local free capacity, and through free "
                                    "on n_X itself."),
            "CLASSIFICATION": "CONDITIONALLY_LINEAR",
            "why": ("the transport and decay parts are linear in rho. The source is a point "
                    "term whose intensity is a function of the local state, so the full process "
                    "is not linear; conditionally on the realised birth sequence B_t it is."),
        },
        "UNBLOCKED_LINEAR_OPERATOR": {
            "spectrum": "lambda(k) = (1 - mu) [1 - a(1 - cos k_y)][1 - a(1 - cos k_x)]",
            "a_relative": op.a_rel, "mu": mu, "L": L,
            "lambda_max": float(lam.max()), "lambda_min": float(lam.min()),
            "lambda_0_0": float(lam[0, 0]),
            "spectral_radius_equals_one_minus_mu": abs(float(lam.max()) - (1 - mu)) < 1e-15,
            "resolvent": "n_hat(k) = 1 / (1 - lambda(k))",
            "green_zero_relative_walk": op.green_zero(),
            "green_zero_X_walk_alone": Operator(qX, 0.0, mu, L).green_zero(),
            "stationary_profile_r50_r80_r90": rq,
            "stationary_second_moment": m2,
            "stationary_rms": math.sqrt(m2),
            "impulse_response_mass": mass_imp,
            "impulse_mass_is_geometric": [abs(mass_imp[t] - (1 - mu) ** t) < 1e-12
                                          for t in range(len(mass_imp))],
            "step_response_asymptote": float(step_mass[-1]),
            "step_response_asymptote_closed_form": 1.0 / mu,
            "mode_relaxation_time_max_finite": float(np.nanmax(tau_modes[np.isfinite(tau_modes)])),
            "SHAPE_MODE": shape,
        },
        "UNBLOCKED_SOURCE_RESPONSE_OPERATOR": "CONDITIONAL_EXACT",
        "FULL_SOURCE_RESPONSE_OPERATOR": "APPROXIMATE_WITH_EMPIRICAL_ERROR",
    }

    json.dump({"KERNELS": kernels, "OPERATOR": operator},
              open(f"{OUT}/_kernels_operator.json", "w"), indent=1, default=str)

    print("q = %.8f   historical D = p_hop/4 = %.8f   corrected D = q(1-q) = %.8f   ratio %.6f"
          % (qX, p_hop / 4, qX * (1 - qX), (p_hop / 4) / (qX * (1 - qX))))
    print("one-step law, %d support points, diagonal support: %s"
          % (len(K_alg), kernels["HAS_DIAGONAL_SUPPORT"]))
    for k in sorted(K_alg):
        print("   d=%-9s exact %.10f   engine %.10f" % (str(k), K_alg[k], K_eng.get(k, 0.0)))
    print("algebra == brute force enumeration : %s" % same)
    print("total variation exact vs engine    : %.5f  (1 sigma per cell %.5f)" % (tv, se))
    print("var per axis %.8f = a ; cov %.2e ; mass %.15f"
          % (m["var_y"], m["cov"], m["mass"]))
    print("characteristic function max |diff| : %.2e"
          % max(c["abs_diff"] for c in phi_check))
    print("relative kernel: support %d, a_rel closed form %.8f, from kernel %.8f"
          % (len(R), a_rel, mR["var_y"]))
    print("static-organiser relative kernel collapses onto K_X : %s"
          % kernels["RELATIVE_KERNEL_STATIC_ORGANISER"]["COLLAPSES_ONTO_K_X"])
    print("symmetries K_X max violation %.2e ; K_rel %.2e"
          % (max(sym_X[k] for k in ("reflection_y", "reflection_x", "axis_swap")),
             max(sym_R[k] for k in ("reflection_y", "reflection_x", "axis_swap"))))
    print("MSD/axis over %d steps: measured %.4f   a*t %.4f (err %+.3f %%)   "
          "historical (p_hop/4)*t %.4f (err %+.3f %%)   z = %+.2f"
          % (msd["steps"], msd["msd_per_axis_measured"], msd["msd_per_axis_predicted_a_t"],
             100 * msd["relative_error_vs_corrected"],
             msd["msd_per_axis_historical_p_hop_over_4_times_t"],
             100 * msd["relative_error_vs_historical"], msd["z_vs_corrected"]))
    print("independent implementation agrees to machine precision : %s"
          % independent["AGREES_TO_MACHINE_PRECISION"])
    print()
    print("spectrum lambda_max %.10f = 1 - mu %.10f" % (lam.max(), 1 - mu))
    print("G(0) relative walk %.6f   X-only walk %.6f   ratio %.4f"
          % (operator["UNBLOCKED_LINEAR_OPERATOR"]["green_zero_relative_walk"],
             operator["UNBLOCKED_LINEAR_OPERATOR"]["green_zero_X_walk_alone"],
             operator["UNBLOCKED_LINEAR_OPERATOR"]["green_zero_X_walk_alone"]
             / operator["UNBLOCKED_LINEAR_OPERATOR"]["green_zero_relative_walk"]))
    print("stationary r50/r80/r90 %s  rms %.4f" % (rq, math.sqrt(m2)))
    print("shape mode: lambda_1/lambda_0 = %.8f  tau_shape = %.2f"
          % (shape["ratio"], shape["tau_shape"]))
    print("impulse mass geometric:", operator["UNBLOCKED_LINEAR_OPERATOR"][
        "impulse_mass_is_geometric"])
    print("step response asymptote %.4f vs 1/mu %.4f"
          % (step_mass[-1], 1 / mu))


if __name__ == "__main__":
    main()
