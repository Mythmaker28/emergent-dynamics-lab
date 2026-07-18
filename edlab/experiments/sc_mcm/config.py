"""PREREGISTERED config for EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00.
Writing frozen from IOM-00; only readout params (lam_plus, lam_minus) are new. New families.
Histories are gentler than IOM-00 (amp 0.03, T=60) so the entity stays LOCALIZED (IOM-00's amp 0.06
saturates attractant c -> disperses the droplet); they still write reproducible temporal order."""
from __future__ import annotations

from .engine import MCParams
from ..sc_iom import config as IOM

SPEC = IOM.SPEC; TRACER = IOM.TRACER; DET = IOM.DET; seed_state = IOM.seed_state
WARMUP = IOM.WARMUP; SETTLE = IOM.SETTLE
PROBE = IOM.PROBE; PROBE_HORIZON = IOM.PROBE_HORIZON; PROBE_CADENCE = IOM.PROBE_CADENCE
TURNOVER_STEPS = IOM.TURNOVER_STEPS; M_LOW = IOM.M_LOW
CLONE_NOISE_SIGMA = IOM.CLONE_NOISE_SIGMA; N_CLONE = IOM.N_CLONE

MC = MCParams()   # lam_plus=0.25 (IOM dose channel), lam_minus=0.15 (new order channel)

# gentler matched-dose histories that keep the entity localized
AMP = 0.03
T = 60
HISTORIES = {
    "H1": [("N", T, AMP, 0.0), ("c", T, 0.0, AMP)],
    "H2": [("c", T, 0.0, AMP), ("N", T, AMP, 0.0)],
    "H3": [("N", T // 3, AMP, 0.0), ("c", T // 3, 0.0, AMP)] * 3,
    "H4": [("0", 2 * T, 0.0, 0.0)],
}

# --- new disjoint families ---------------------------------------------------------------------
DEV_TRAJ = tuple(range(32000, 32016))
PROSP_TRAJ = tuple(range(33000, 33012))
CONT_SEEDS = {"dev": (32100, 32101, 32102, 32103), "prospective": (33100, 33101, 33102, 33103)}
N_CONT = {"dev": 16, "prospective": 12}
HIST_STEPS = 2 * T
CONT_AMP_RANGE = (0.005, 0.025)     # dose dimension (net nutrient -> m_plus)
CONT_ORDER_RANGE = (0.0, 1.0)       # order dimension (orthogonal to dose)

# --- readout parameter grid (only NEW params; writing NOT retuned) ------------------------------
PARAM_GRID = [dict(lam_plus=lp, lam_minus=lm) for lp in (0.15, 0.25, 0.30) for lm in (0.05, 0.15, 0.25)]

RESP_SCALE = (5.0, 1.0, 0.01, 5.0, 0.05)   # [size, rg, uptake, mass, mean_c]

G_ORDER_RATIO = 1.5
G_RESP_DIM = 1.3
G_INDIV_AUC = 0.70
G_TWO_DIMS_R2 = 0.5
