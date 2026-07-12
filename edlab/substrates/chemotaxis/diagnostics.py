"""R7 localization diagnostics. THRESHOLD-INDEPENDENT first; the detector is only a supplementary check."""

from __future__ import annotations

import numpy as np

from .engine import CHState

THRESHOLD_BAND = (0.2, 0.3, 0.4, 0.5, 0.6)   # frozen band (x rho_max)
PR_MAX = 0.15
RG_MAX_FRAC = 0.125                          # L/8
OCC_MAX = 0.15
COMP_MAX = 0.15


def participation_ratio(rho: np.ndarray) -> float:
    """(sum rho)^2 / (L^2 * sum rho^2): the effective FRACTION of the domain carrying the mass.
    1.0 for a uniform field, -> 0 for a localized one. No threshold anywhere."""
    n = rho.size
    s1 = float(rho.sum())
    s2 = float((rho ** 2).sum())
    if s2 <= 0.0:
        return 0.0
    return (s1 * s1) / (n * s2)


def circular_centroid(rho: np.ndarray) -> np.ndarray:
    n = rho.shape[0]
    out = []
    for ax in (0, 1):
        w = rho.sum(axis=1 - ax)
        ang = np.arange(n) * (2 * np.pi / n)
        cm = float((w * np.cos(ang)).sum())
        sm = float((w * np.sin(ang)).sum())
        out.append((np.arctan2(sm, cm) % (2 * np.pi)) * n / (2 * np.pi))
    return np.asarray(out)


def radius_of_gyration(rho: np.ndarray) -> float:
    """Mass-weighted Rg about the circular-mean centroid, with minimum-image distances. Threshold-free."""
    n = rho.shape[0]
    tot = float(rho.sum())
    if tot <= 0:
        return float("inf")
    cen = circular_centroid(rho)
    ys, xs = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    dy = ys - cen[0]
    dy -= n * np.round(dy / n)
    dx = xs - cen[1]
    dx -= n * np.round(dx / n)
    return float(np.sqrt((rho * (dy ** 2 + dx ** 2)).sum() / tot))


def _label_periodic(mask: np.ndarray):
    from scipy import ndimage
    labl, k = ndimage.label(mask, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    if k == 0:
        return None, {}
    parent = list(range(k + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for a, b in ((labl[0, :], labl[-1, :]), (labl[:, 0], labl[:, -1])):
        m = (a > 0) & (b > 0)
        for u, v in zip(a[m], b[m]):
            union(int(u), int(v))
    root = np.zeros(k + 1, dtype=np.int64)
    for cid in range(1, k + 1):
        root[cid] = find(cid)
    merged = root[labl]
    groups: dict[int, np.ndarray] = {}
    for r in np.unique(merged[merged > 0]):
        groups[int(r)] = merged == r
    return merged, groups


def _largest_component(mask: np.ndarray) -> int:
    _m, g = _label_periodic(mask)
    return max((int(v.sum()) for v in g.values()), default=0)


def entity_radius_of_gyration(rho: np.ndarray, threshold: float) -> tuple[float, int]:
    """Rg of the LARGEST CONNECTED ENTITY about its own periodic centroid.

    CORRECTION (proven a priori, tests/test_chemotaxis.py::test_global_rg_cannot_detect_compact_multispot):
    a GLOBAL Rg measures the spread of the ENSEMBLE, not of an entity. A field of 30 PERFECTLY compact spots
    scores global Rg = 23.9 against 26.1 for a uniform field -- the global criterion cannot be passed by ANY
    multi-spot localized state however compact its entities are. It is a criterion that cannot fire. The
    localization question is about the ENTITY, so Rg is measured on the entity."""
    n = rho.shape[0]
    _m, groups = _label_periodic(rho > threshold)
    if not groups:
        return float("inf"), 0
    sel = max(groups.values(), key=lambda v: int(v.sum()))
    w = rho * sel
    tot = float(w.sum())
    if tot <= 0:
        return float("inf"), 0
    cen = circular_centroid(w)
    ys, xs = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    dy = ys - cen[0]; dy -= n * np.round(dy / n)
    dx = xs - cen[1]; dx -= n * np.round(dx / n)
    return float(np.sqrt((w * (dy ** 2 + dx ** 2)).sum() / tot)), int(sel.sum())


def r7_diagnostics(st: CHState, rho_max: float) -> dict:
    rho = st.rho
    n = rho.shape[0]
    pr = participation_ratio(rho)
    rg = radius_of_gyration(rho)
    occ = {}
    comp = {}
    ergs = {}
    esz = {}
    for t in THRESHOLD_BAND:
        m = rho > t * rho_max
        occ[t] = float(m.mean())
        comp[t] = _largest_component(m) / (n * n)
        e_rg, e_n = entity_radius_of_gyration(rho, t * rho_max)
        ergs[t] = e_rg
        esz[t] = e_n
    mass = float(rho.sum())
    localized = bool(
        mass > 1e-3                                        # not extinct
        and pr <= PR_MAX                                   # threshold-free (PR DOES separate: 0.095 vs 1.000)
        and all(v <= RG_MAX_FRAC * n for v in ergs.values())   # ENTITY Rg bounded at EVERY threshold in the band
        and all(v <= OCC_MAX for v in occ.values())        # sub-domain at EVERY threshold in the band
        and all(v <= COMP_MAX for v in comp.values())      # non-space-filling at EVERY threshold
    )
    return {"participation_ratio": pr, "radius_of_gyration_global": rg, "mass": mass,
            "entity_rg": ergs, "entity_size": esz,
            "occupancy": occ, "largest_component_frac": comp,
            "rho_max_observed": float(rho.max()), "localized": localized}
