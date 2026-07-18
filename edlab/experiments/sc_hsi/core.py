"""Descriptors: privileged HIDDEN state h(U,V), ACCESSIBLE snapshot X, and attractor labeling.

Separation is strict: X contains only externally accessible quantities (geometry, external fields N/c,
uptake behaviour). h contains the privileged internal organization (U,V phenotype + mean sigma). The
hidden state is used only as an explanatory/ground-truth variable in this existence assay.
"""
from __future__ import annotations

import numpy as np
from scipy.cluster.vq import kmeans2, whiten

from ..sc_hmc import harness as H
from ..sc_hmc import axes as AX


def hidden_descriptor(st, e=None) -> np.ndarray:
    """h: privileged internal organization = phenotype [het, n_dom, interface, radial_u, janus] + mean_sig."""
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(6)
    return np.concatenate([np.asarray(e.phenotype, float), [e.mean_sig]])


def snapshot_descriptor(st, e=None) -> np.ndarray:
    """X: accessible instantaneous phenotype = geometry(5) + external fields mean_c,mean_N(2) + uptake(1)."""
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(8)
    geo = AX.p1_geometry(st, e)[:5]
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    ext = np.array([float(st.c[ys, xs].mean()), float(st.N[ys, xs].mean())])
    return np.concatenate([geo, ext, [e.specific_uptake]])


def attractor_coords(st, e=None) -> np.ndarray:
    """Coarse coordinates on which generic attractor classes live: mean_sig, heterogeneity, n_domains."""
    e = H.largest_entity(st) if e is None else e
    if e is None:
        return np.zeros(3)
    return np.array([e.mean_sig, float(e.phenotype[0]), float(e.phenotype[1])])


def fit_attractors(coords: np.ndarray, k: int, seed: int = 7):
    """Frozen k-means on development attractor coordinates. Returns (centers, std, mean) for labeling."""
    mu = coords.mean(0); sd = coords.std(0) + 1e-9
    Z = (coords - mu) / sd
    centers, _ = kmeans2(Z, k, seed=seed, minit="++", missing="raise")
    return {"centers": centers, "mu": mu, "sd": sd}


def label_attractor(coords: np.ndarray, model: dict) -> np.ndarray:
    Z = (np.atleast_2d(coords) - model["mu"]) / model["sd"]
    d = np.linalg.norm(Z[:, None, :] - model["centers"][None, :, :], axis=2)
    return d.argmin(1)
