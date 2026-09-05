"""PREREGISTERED configuration for EXP-SC-INDIVIDUAL-ORGANIZATIONAL-MEMORY-00.

Base scaffold physics FROZEN (imported from the frozen sc_hmc line). Only the memory extension
(MemParams) is new. New trajectory + history families; the HMC and HSI held-outs are NOT reused.
"""
from __future__ import annotations

from .engine import MemParams

from ..sc_hmc import config as HMC

SPEC = HMC.SPEC            # frozen ScaffoldSpec, beta=0.10, D_int=0.008
TRACER = HMC.TRACER
DET = HMC.DET
seed_state = HMC.seed_state
WARMUP = HMC.WARMUP       # 2000

MEM = MemParams()         # default (development-selected values live here)

# --- new disjoint families --------------------------------------------------------------------
DEV_TRAJ = tuple(range(30000, 30040))       # development substrate trajectories
PROSP_TRAJ = tuple(range(31000, 31032))     # prospective (reserved; unseen)

# --- experience protocols (phase = (label, steps, dN, dc): per-step additive boost to N and c) --
EXP_STEPS = 240                              # per full-history experience window
_A = EXP_STEPS // 2
AN = 0.06                                    # nutrient-phase boost
AC = 0.06                                    # attractant-phase boost
HISTORIES = {
    "H1": [("N", _A, AN, 0.0), ("c", _A, 0.0, AC)],
    "H2": [("c", _A, 0.0, AC), ("N", _A, AN, 0.0)],
    "H3":      [("N", _A // 3, AN, 0.0), ("c", _A // 3, 0.0, AC)] * 3,
    "H4":  [("0", EXP_STEPS, 0.0, 0.0)],
}
SETTLE = 120                                 # return to identical neutral env before readout
READOUT_DELAY = 60                           # steps after settle at which memory/response are read

# --- functional readout probe (frozen; matches HSI's most-informative bounded nutrient probe) ---
PROBE = ("N", "add", 0.50, 15)
PROBE_HORIZON = 120
PROBE_CADENCE = 30

# --- material turnover ------------------------------------------------------------------------
TURNOVER_STEPS = 700
M_LOW = 0.35

# --- clone ceiling ----------------------------------------------------------------------------
CLONE_NOISE_SIGMA = 0.01
N_CLONE = 4

# --- continuous-history individuation ---------------------------------------------------------
N_CONT_DEV = 40
N_CONT_PROSP = 32
CONT_PARAM_RANGES = {"order_frac": (0.0, 1.0), "amp": (0.03, 0.09),
                     "split": (0.3, 0.7), "npulse": (1, 4)}

# --- PREREGISTERED parameter grid (committed before selection; weakest-passing preferred) ------
PARAM_GRID = [
    dict(eta_w=w, eta_d1=0.03, eta_d2=d2, eta_t=0.01, D_m=0.01, lam_m=l)
    for w in (0.03, 0.05, 0.08)
    for d2 in (0.003, 0.001)
    for l in (0.15, 0.25)
]

# --- gate thresholds (frozen on dev) ----------------------------------------------------------
G_WRITE_SEP = 2.0            # history-writing: between-history memory sep / within-history spread
G_ORDER_SEP = 1.5           # A->B vs B->A memory separation / clone ceiling
G_READOUT_RATIO = 1.5       # causal readout: memory-different response / clone ceiling
G_ERASE_FRAC = 0.5          # erasure must remove >=50% of the readout effect
G_TRANSPLANT_FRAC = 0.4     # transplant must transfer >=40% of the response tendency
G_INDIV_AUC = 0.70          # individuation AUC (within-history < between-history)
G_TURNOVER_KEEP = 0.5       # fraction of readout effect retained after M<=M_LOW
BACKCOMPAT_TOL = 1e-12
