"""PASSIVE, READ-ONLY reference observables for the frozen scaffold droplet substrate.

Every function here READS an SCState and returns a scalar. None of them writes to the state, adds a force, or
touches the governing equations (engine.py carries the v00-independent scaffold physics and is NOT imported for
mutation). This module exists to answer one question for CRD-03 transfer: does the droplet expose >=3 passive
references with DISTINCT couplings to environmental (nutrient) drift and a usable contamination gradient?

Design notes grounded in the physics (see docs/POD_INVENTORY.md):
  * N is the external nutrient field: fast diffusion (D_N=0.5), relaxation to N0. It is the natural carrier of
    ENVIRONMENTAL DRIFT. Spatial sub-samples of N are nearly COLLINEAR (N is well-mixed), so raw quadrant means
    do NOT provide diversity -- that is must-fail control #1, confirmed.
  * c is the attractant, PRODUCED by rho (c += s*rho). It therefore carries the droplet's own response ->
    high causal contamination kappa. Useful as a deliberately-contaminated reference, not a clean one.
  * uptake is the causal response itself (beta*sigma coupling) -> it is the QUANTITY, never a reference.
  * Diversity, if it exists, comes from reference TYPES with different transfer functions to the drift:
    the field value, its Laplacian (diffusion-filtered -> different bandwidth/gain), boundary flux, and the
    field measured where the droplet is ABSENT vs PRESENT (different contamination).
"""
from __future__ import annotations

import numpy as np


def _mask_lowrho(st, q=0.25):
    """Cells with the LEAST droplet mass -> the closest thing to a background/far-field region. Derived from the
    current rho observable only (no tracker identity, no historical IDs)."""
    thr = np.quantile(st.rho, q)
    return st.rho <= thr


def _mask_highrho(st, q=0.75):
    thr = np.quantile(st.rho, q)
    return st.rho >= thr


def N_global(st):            # global nutrient mean: tracks bulk drift, mild contamination (droplet depletes N)
    return float(st.N.mean())


def N_background(st):        # nutrient where the droplet is THINNEST: less local depletion -> lower contamination
    m = _mask_lowrho(st)
    return float(st.N[m].mean())


def N_core(st):             # nutrient where the droplet is THICKEST: strong local depletion -> high contamination
    m = _mask_highrho(st)
    return float(st.N[m].mean())


def N_laplacian(st):        # diffusion-filtered nutrient: different bandwidth/gain to the drift than the field mean
    lap = (np.roll(st.N, 1, -2) + np.roll(st.N, -1, -2) + np.roll(st.N, 1, -1) + np.roll(st.N, -1, -1) - 4.0 * st.N)
    return float(np.abs(lap).mean())


def N_flux(st):             # net nutrient gradient magnitude (boundary-flux proxy): a spatial-derivative channel
    gx = np.roll(st.N, -1, -2) - st.N
    gy = np.roll(st.N, -1, -1) - st.N
    return float(np.sqrt(gx ** 2 + gy ** 2).mean())


def c_global(st):           # attractant produced by the droplet: DELIBERATELY contaminated reference
    return float(st.c.mean())


def N_sectorTL(st):         # a spatial quadrant -- included to DEMONSTRATE collinearity (must-fail #1)
    n = st.N.shape[0] // 2
    return float(st.N[:n, :n].mean())


def N_sectorBR(st):
    n = st.N.shape[0] // 2
    return float(st.N[n:, n:].mean())


REFERENCES = {
    "N_global": N_global, "N_background": N_background, "N_core": N_core,
    "N_laplacian": N_laplacian, "N_flux": N_flux, "c_global": c_global,
    "N_sectorTL": N_sectorTL, "N_sectorBR": N_sectorBR,
}


def read_all(st):
    return {k: f(st) for k, f in REFERENCES.items()}


# --- the causal RESPONSE observable (the quantity CRD-03 decomposes, NOT a reference) ---
def response_uptake(st):
    """Specific uptake = nutrient consumed per unit droplet mass last step. This is the behavioural response the
    internal state drives through beta*sigma. It is the target quantity, never used as a reference."""
    return float(st.uptake.sum() / (st.rho.sum() + 1e-12))
