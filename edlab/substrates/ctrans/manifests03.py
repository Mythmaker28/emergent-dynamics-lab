"""v03 DEVELOPMENT PARTITION: FIT / CALIBRATION / CHALLENGE. Committed BEFORE any predictor is fitted.

THREE DISJOINT SETS. No system, parameter tuple, seed or acquisition appears in more than one. The sealed v01
prospective split is separate from all three and is not touched.

THE PARAMETER GRIDS ARE DISJOINT FROM THE SEALED SPLIT ON EVERY AXIS. The prospective grid uses
tau in {12,38,52}, T in {5,9,15,24,50,66,77}, gain in {1.6,2.8}, slow-tau in {50,66,77}. Nothing here reuses any of
them, and the THIRD-ORDER CASCADE -- the topology reserved to the prospective split alone -- appears NOWHERE in
development.
"""
from __future__ import annotations
from . import systems as S
from . import tails as T
from .manifests01 import Case, INDIST, DIFFERENT, INDETERMINATE, CONTINUITY, DIFFERENCE, FALSE_SAMENESS, \
    FALSE_DIFFERENCE, ABSTAIN, DEV_SIGMA, TAU_MAX, D_MAX

FIT_SEED = 300_000
CAL_SEED = 400_000
CHL_SEED = 500_000          # all disjoint from v01 dev (2xx) and the sealed prospective split (8xx)
SG = DEV_SIGMA              # 1.0e-5


def fit_systems() -> dict:
    """FIT SET -- the predictor is fitted here and NOWHERE else. tau {3,7}, T {3,7,11,22,36,55}, gain {0.7,1.3}."""
    b = T.first_order("F_leak", tau=3, T=7.0, gain=1.3, sigma=SG)
    return {
        "F_leak": b,
        "F_leak_dead": S.dead_site("F_leak_dead", b, x0_5=0.5),
        "F_leak_units": S.with_units("F_leak_units", b, a=600.0, b=0.2),
        "F_leak_g": T.first_order("F_leak_g", tau=3, T=7.0, gain=2.4, sigma=SG),
        "F_leak_sgn": T.first_order("F_leak_sgn", tau=3, T=7.0, gain=1.3, sign=-1, sigma=SG),
        "F_leak_slow": T.first_order("F_leak_slow", tau=3, T=22.0, gain=1.3, sigma=SG),
        "F_delay": T.first_order("F_delay", tau=30, T=7.0, gain=1.3, sigma=SG),
        "F_casc": T.cascade_n("F_casc", Ts=(7.0, 22.0), tau=3, gain=1.3, sigma=SG),
        "F_under": T.underdamped("F_under", k=7.0, T2=7.0, T3=11.0, gain=1.3, sigma=SG),
        "F_mw": T.multiscale("F_mw", T_fast=3.0, T_slow=35.0, w_slow=0.20, gain=1.3, sigma=SG),
        "F_ms": T.multiscale("F_ms", T_fast=3.0, T_slow=48.0, w_slow=1.10, gain=1.3, sigma=SG),
        "F_ms2": T.multiscale("F_ms2", T_fast=3.0, T_slow=58.0, w_slow=1.10, gain=1.3, sigma=SG),
        "F_d2": T.delayed_second("F_d2", d2=42, T1=3.0, T2=7.0, w2=0.8, gain=1.3, sigma=SG),
        "F_supply": S.supply_cause("F_supply", b, w_s=0.8, site=3, T=11.0, gain=0.7),
    }


def cal_systems() -> dict:
    """CALIBRATION SET -- UNTOUCHED until the predictor is fixed. tau {7,20}, T {14,28,42,70}, gain {1.8}."""
    b = T.first_order("C_leak", tau=7, T=14.0, gain=1.8, sigma=SG)
    return {
        "C_leak": b,
        "C_leak_dead": S.dead_site("C_leak_dead", b, x0_5=-0.3),
        "C_leak_units": S.with_units("C_leak_units", b, a=90.0, b=-0.1),
        "C_leak_g": T.first_order("C_leak_g", tau=7, T=14.0, gain=0.7, sigma=SG),
        "C_leak_sgn": T.first_order("C_leak_sgn", tau=7, T=14.0, gain=1.8, sign=-1, sigma=SG),
        "C_leak_slow": T.first_order("C_leak_slow", tau=7, T=28.0, gain=1.8, sigma=SG),
        "C_delay": T.first_order("C_delay", tau=20, T=14.0, gain=1.8, sigma=SG),
        "C_casc": T.cascade_n("C_casc", Ts=(11.0, 28.0), tau=7, gain=1.8, sigma=SG),
        "C_under": T.underdamped("C_under", k=9.0, T2=11.0, T3=14.0, gain=1.8, sigma=SG),
        "C_mw": T.multiscale("C_mw", T_fast=3.0, T_slow=42.0, w_slow=0.45, gain=1.8, sigma=SG),
        "C_ms": T.multiscale("C_ms", T_fast=3.0, T_slow=58.0, w_slow=0.80, gain=1.8, sigma=SG),
        "C_ms2": T.multiscale("C_ms2", T_fast=3.0, T_slow=72.0, w_slow=0.80, gain=1.8, sigma=SG),
        "C_d2": T.delayed_second("C_d2", d2=48, T1=3.0, T2=14.0, w2=0.5, gain=1.8, sigma=SG),
        "C_mem_p": S.memory("C_mem_p", mem0=+1.0, T=14.0, Tm=7.0, gain=1.8, k_out=1.1, sigma=SG),
    }


def challenge_systems() -> dict:
    """CHALLENGE SET -- gates and controls. Disjoint from FIT and CAL. Carries the HISTORICAL REGRESSIONS."""
    b = T.first_order("X_leak", tau=0, T=8.0, gain=1.0, sigma=SG)
    ms = T.multiscale("X_ms", T_fast=4.0, T_slow=45.0, w_slow=1.40, gain=1.0, sigma=SG)
    return {
        "X_leak": b,
        "X_leak_dead": S.dead_site("X_leak_dead", b, x0_5=0.6),
        "X_leak_units": S.with_units("X_leak_units", b, a=800.0, b=0.3),
        "X_leak_fine": S.with_refined_solver("X_leak_fine", b),
        "X_gain2": T.first_order("X_gain2", tau=0, T=8.0, gain=2.0, sigma=SG),
        "X_sign": T.first_order("X_sign", tau=0, T=8.0, gain=1.0, sign=-1, sigma=SG),
        "X_supply": S.supply_cause("X_supply", b, w_s=0.9, site=3, T=7.0, gain=0.8),
        "X_hidden": S.hidden_mode("X_hidden", b, c_h=1.2, T=9.0),
        "X_mem_p": S.memory("X_mem_p", mem0=+1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=SG),
        "X_mem_m": S.memory("X_mem_m", mem0=-1.0, T=8.0, Tm=5.0, gain=1.0, k_out=1.2, sigma=SG),
        # ---- HISTORICAL REGRESSIONS
        "R_leak_burned": T.first_order("R_leak_burned", tau=6, T=13.0, gain=1.5, sigma=1.2e-5),   # v00 P_leak
        "R_casc_burned": T.cascade_n("R_casc_burned", Ts=(7.0, 21.0), tau=2, gain=1.5, sigma=1.2e-5),  # v00 P_cascade
        "X_ms": ms,                                                                  # v01 T4, left
        "X_ms_g2": T.multiscale("X_ms_g2", T_fast=4.0, T_slow=45.0, w_slow=1.40, gain=2.0, sigma=SG),
        "X_ms_tail": T.multiscale("X_ms_tail", T_fast=4.0, T_slow=79.0, w_slow=1.40, gain=1.0, sigma=SG),  # v01 T4 right
        "X_oos": T.out_of_contract_slow("X_oos", T=300.0, gain=1.0, sigma=SG),       # v01 out-of-contract
        "X_nonsettle": T.nonsettling("X_nonsettle", k=0.15, T=8.0, gain=1.0, sigma=SG),
        "X_silent": S.silent_dead("X_silent", sigma=SG),
        "X_drifty": S.too_drifty("X_drifty", drift_frac=8.0, sigma=SG),              # OOD drift
        "X_noisy": S.too_noisy("X_noisy", sigma_mult=250.0),
        "X_lowcov": S.access_restricted("X_lowcov", S.supply_cause("X_lowcov_src", b, w_s=0.9, site=3,
                                                                   T=7.0, gain=0.8), blocked=(S.DRIVE,)),
        "X_loud": T.first_order("X_loud", tau=0, T=8.0, gain=1.0, sigma=SG * 4.0),
    }


CHALLENGE_CASES = [
    Case("Y-01", "X_leak", "X_leak", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST}, "the NULL",
         tags=("null",)),
    Case("Y-02", "X_leak", "X_leak_dead", CONTINUITY, {"limited": INDIST, "rich": INDIST},
         "equivalent microimplementation", tags=("continuity",)),
    Case("Y-03", "X_leak", "X_leak_units", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "unit change u -> 800u + 0.3", tags=("units",)),
    Case("Y-04", "X_leak", "X_leak_fine", FALSE_DIFFERENCE, {"limited": INDIST, "rich": INDIST},
         "solver refinement", tags=("solver",)),
    Case("Y-05", "X_leak", "X_gain2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT}, "gain x2",
         tags=("gain",)),
    Case("Y-06", "X_leak", "X_sign", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT}, "sign inversion",
         tags=("sign",)),
    Case("Y-07", "X_leak", "X_supply", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "independently controllable additional cause", tags=("cause",)),
    Case("Y-08", "X_mem_p", "X_mem_m", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT}, "hidden state",
         tags=("hidden_state",)),
    Case("Y-09", "X_leak", "X_hidden", FALSE_SAMENESS, {"limited": INDIST, "rich": DIFFERENT},
         "limited-access collision -> EQUIVALENCE_CLASS_ONLY", tags=("collision",)),
    # ---- HISTORICAL REGRESSIONS (development only)
    Case("Y-10", "R_leak_burned", "R_casc_burned", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "THE v00 BURNED CASCADE. v00 measured 64.15 against a radius of 23.36 and abstained anyway. Its interval "
         "must lie ENTIRELY in the DIFFERENT region.", tags=("regression_v00", "must_classify")),
    Case("Y-11", "X_ms", "X_ms_tail", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "THE v01 T4 CASE. Its true eventual distance sits in the AMBIGUITY REGION between the radii, so the "
         "calibrated interval must cross a boundary and force abstention. v01 spoke here; v02 could not even see "
         "the remainder.", tags=("regression_v01_T4", "must_abstain")),
    Case("Y-12", "X_ms", "X_ms_g2", DIFFERENCE, {"limited": DIFFERENT, "rich": DIFFERENT},
         "HARMLESS SLOW TAIL: a strong long tail with a gain difference that dwarfs it. Must classify with a "
         "narrow interval.", tags=("slow_tail", "must_classify")),
    Case("Y-13", "X_oos", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "v01 out-of-contract slow tail (tau=300 >> TAU_MAX)", tags=("out_of_contract",)),
    Case("Y-14", "X_nonsettle", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "never settles", tags=("nonsettling",)),
    Case("Y-15", "X_silent", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "silent: no responsiveness", tags=("silent",)),
    Case("Y-16", "X_drifty", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "DRIFT FAR OUTSIDE THE CALIBRATED REGIME -> must return OUT_OF_CALIBRATION_SCOPE, never a confident "
         "prediction.", tags=("ood_drift",)),
    Case("Y-17", "X_noisy", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "below its own noise floor", tags=("noise",)),
    Case("Y-18", "X_lowcov", "X_leak", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "drive line unreachable: coverage below floor", tags=("coverage",)),
    Case("Y-19", "X_leak", "X_loud", ABSTAIN, {"limited": INDETERMINATE, "rich": INDETERMINATE},
         "measurement-contract violation: 4x noisier channel", common_channel=False, tags=("contract",)),
]
