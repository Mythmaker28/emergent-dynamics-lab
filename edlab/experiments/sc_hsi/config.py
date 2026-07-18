"""PREREGISTERED frozen configuration for EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00.

Physics imported unchanged from the frozen sc_hmc line (which imports the frozen scaffold engine).
New disjoint trajectory families; the HMC prospective seeds 9501-9516 are NOT reused.
"""
from __future__ import annotations

from ..sc_hmc import config as HMC  # frozen SPEC (beta=0.10), TRACER, DET, seed_state, T_STAR

SPEC = HMC.SPEC
TRACER = HMC.TRACER
DET = HMC.DET
seed_state = HMC.seed_state
WARMUP = HMC.WARMUP  # 2000

# --- trajectory families (disjoint; new; HMC prospective 9501-9516 untouched) -----------------
DEV_TRAJ = tuple(range(20000, 20100))      # 100 development trajectories
PROSP_TRAJ = tuple(range(21000, 21032))    # 32 prospective trajectories (new reserved family)

# --- checkpoints (steps after warmup): several ages per trajectory ----------------------------
CHECKPOINT_AGES = (0, 300, 600, 900)       # t = 2000, 2300, 2600, 2900
CANONICAL_AGE = 600                        # age at which full states are stored + pairs are matched

# --- attractor analysis -----------------------------------------------------------------------
N_ATTRACTORS = 4                           # k-means on standardized (mean_sig, het, n_domains), frozen on dev

# --- matching (frozen on dev) -----------------------------------------------------------------
# snapshot-matched = accessible-X distance in the lowest SNAP_MATCH_Q quantile of cross-pairs;
# hidden-different = hidden-h distance in the highest HIDDEN_DIFF_Q quantile.
SNAP_MATCH_Q = 0.10
HIDDEN_DIFF_Q = 0.60
MAX_PAIRS_DEV = 60
MAX_PAIRS_PROSP = 40

# --- future-divergence --------------------------------------------------------------------------
DIV_HORIZON = 150
DIV_CADENCE = 30
CLONE_NOISE_SIGMA = 0.01                   # ARM C independent environmental noise (stochastic ceiling)
N_CLONE_REALIZATIONS = 4

# --- intervention grid (bounded; N and c only; preregistered) ----------------------------------
# (name, field, op, amp, duration)
PROBE_GRID = (
    ("N+0.5x5",  "N", "add", 0.50, 5),
    ("N+0.5x15", "N", "add", 0.50, 15),
    ("Nx0.3x5",  "N", "mul", 0.30, 5),
    ("Nx0.3x15", "N", "mul", 0.30, 15),
    ("c+0.5x5",  "c", "add", 0.50, 5),
    ("c+0.5x15", "c", "add", 0.50, 15),
    ("cx0.3x5",  "c", "mul", 0.30, 5),
    ("cx0.3x15", "c", "mul", 0.30, 15),
)
PROBE_HORIZON = 120
PROBE_CADENCE = 30

# --- gate thresholds (frozen on dev) ----------------------------------------------------------
G_INDIVIDUATION_AUC = 0.70                 # within-traj must beat same-attractor-between at AUC >= this
G_CAUSAL_RATIO = 1.5                       # hidden-different divergence / clone ceiling must exceed this
G_ACCESS_RATIO = 1.5                       # best probe hidden-discrimination / clone divergence
INTERNAL_INIT = "random"                   # organization self-organizes
