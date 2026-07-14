"""PREREGISTERED frozen configuration for EXP-SC-HISTORY-MATERIAL-CONTINUITY-00.

Everything that could be tuned lives here and is committed BEFORE the prospective split is inspected.
The physics is imported unchanged from the frozen EXP-SC line (exp_sc_00 / exp_sc_00b).
"""
from __future__ import annotations

from dataclasses import replace

# Frozen substrate objects (unchanged physics). We deliberately import the SAME objects the frozen
# EXP-SC-00B line used, so this experiment cannot silently re-parameterize the droplet.
from ..exp_sc_00 import SPEC as _SPEC_DEFAULT, TRACER, DET, seed_state, T_STAR  # noqa: F401

BETA = 0.10                        # selected prospectively in EXP-SC-00B; NOT retuned here
SPEC = replace(_SPEC_DEFAULT, beta=BETA)

# --- timing (steps) ---------------------------------------------------------------------------
WARMUP = T_STAR                    # 2000: entity self-organizes; history begins
T0_AFTER_WARMUP = 0                # pulse-chase label applied immediately after warmup
CHECKPOINT = 700                   # t_c: "present" where counterfactual arms are built (steps after t0)
EARLY_OFFSET = 350                 # "own earlier" reference response measured at t_c - EARLY_OFFSET
RESPONSE_HORIZON = 120             # steps over which an intervention response profile is recorded
RECOVERY_HORIZON = 200             # steps to test return to pre-perturbation regime (P5)
TURNOVER_PROBE_STEPS = (200, 400, 600, 700)   # M(t0,t) sampled here; material half-life ~ 268 steps

# --- material-continuity band (preregistered) -------------------------------------------------
# ln2/(k*dt) = ln2/(0.02588*0.1) ~ 268 steps half-life. By t_c=700, expected M ~ 2^-2.6 ~ 0.16.
M_LOW = 0.35                       # "substantial material replacement": M(t0,t_c) <= M_LOW
M_HIGH = 0.80                      # a "high material overlap" reference for the material-only trap

# --- organizational-axis continuity margins (defined on DEVELOPMENT only) ----------------------
# An axis "remains within the continuous-history regime" if its distance to the entity's own earlier
# value is <= (median within-history distance + AXIS_MARGIN_K * MAD) measured on development arms H.
AXIS_MARGIN_K = 3.0
MIN_AXES_WITHIN = 3                # >= 3 of 6 axes must remain within-regime for the positive pattern

# --- intervention battery (bounded; uses ONLY external handles N and c) ------------------------
# amplitudes are multiplicative/additive perturbations held for PULSE_STEPS steps then released.
PULSE_STEPS = 5
INTERVENTIONS = (
    ("N_boost",   {"field": "N", "op": "add", "amp": 0.50}),
    ("N_deprive", {"field": "N", "op": "mul", "amp": 0.30}),
    ("c_boost",   {"field": "c", "op": "add", "amp": 0.50}),
    ("c_suppress",{"field": "c", "op": "mul", "amp": 0.30}),
)

# --- ARM C stochastic ceiling: the frozen engine is deterministic, so ARM C injects independent,
# bounded multiplicative noise on the two EXTERNAL forcing fields only (never on rho/U/V). ---------
CLONE_NOISE_SIGMA = 0.01           # 1% i.i.d. lognormal-ish noise on N and c replenishment per step

# --- development / prospective split (seed-stratified; committed before tuning) ----------------
# distinct, disjoint seed pools. Internal initial state is always "random" so organization must
# self-organize (as in the frozen R8 line), except where an arm deliberately imposes a state.
DEV_SEEDS = tuple(range(9401, 9413))          # 12 development seeds
PROSPECTIVE_SEEDS = tuple(range(9501, 9517))  # 16 held-out prospective seeds (never inspected pre-freeze)
UNRELATED_SEEDS = tuple(range(9601, 9613))    # pool for ARM U (unrelated but phenotype-matched)

INTERNAL_INIT = "random"

# stratification axes recorded per record (for split balance + reporting)
STRATA = ("seed", "checkpoint_age", "material_band", "internal_regime", "intervention_family")

GRID = SPEC.size  # 64
