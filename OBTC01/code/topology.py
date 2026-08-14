"""OBTC01 §6.1 — a real topological winding test, implemented INDEPENDENTLY.

CSC01 tested winding by lifting the component into the universal cover with a BFS and looking
for a cell reached with two different lifts. This file uses a different algorithm entirely:

    TILE the pattern k x k times into a plain, NON-periodic array, label the tiling with an
    ordinary connected-component labeller, and ask whether a cell of the central copy is
    connected, in the tiling, to its own translate one period away.

    A component contains a non-contractible cycle winding in x  <=>  in the lift, a cell is
    connected to its translate by (0, L). Same for y with (L, 0).

The two algorithms share no code and no data structure. `tests_obtc.py` requires them to agree
on random masks, and the six declared configurations of the mandate are checked explicitly.

The old ORR01 indicator is kept, under its historical name only, so that its behaviour remains
inspectable and its difference from a real test remains measurable:

    LEGACY_EXTENT_PROXY = (2 * max(dy, dx) + 1) >= L / 2   measured from the angular centre.

It is not a topological test and must not enter any gate.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
TILES = 5                      # 5 x 5 copies: a winding path needs at most one period, with
                               # generous room for it to wander before closing


def winding_by_tiling(mask, labels, cid, tiles=TILES):
    """(wraps_y, wraps_x) for component `cid`, by lifting through a k x k tiling."""
    L = mask.shape[0]
    sub = (labels == cid)
    big = np.tile(sub, (tiles, tiles))
    lab, k = ndimage.label(big, structure=CROSS)
    if k == 0:
        return False, False
    c = tiles // 2
    ys, xs = np.nonzero(sub)
    if len(ys) == 0:
        return False, False
    y0, x0 = int(ys[0]), int(xs[0])
    home = lab[c * L + y0, c * L + x0]
    wy = bool(lab[(c + 1) * L + y0, c * L + x0] == home)
    wx = bool(lab[c * L + y0, (c + 1) * L + x0] == home)
    return wy, wx


def classify_component(mask, labels, cid, tiles=TILES):
    """The six configurations the mandate asks to distinguish."""
    L = mask.shape[0]
    sub = (labels == cid)
    wy, wx = winding_by_tiling(mask, labels, cid, tiles)
    ys, xs = np.nonzero(sub)
    touches_seam = bool(sub[0, :].any() and sub[L - 1, :].any()) or \
                   bool(sub[:, 0].any() and sub[:, L - 1].any())
    span_y = int(ys.max() - ys.min() + 1) if len(ys) else 0
    span_x = int(xs.max() - xs.min() + 1) if len(xs) else 0
    large_extent = bool(max(span_y, span_x) >= L * 0.5)
    if wy and wx:
        kind = "WINDING_BOTH"
    elif wy:
        kind = "WINDING_VERTICAL"
    elif wx:
        kind = "WINDING_HORIZONTAL"
    elif touches_seam:
        kind = "CROSSES_THE_GRAPHICAL_SEAM_ONLY"
    elif large_extent:
        kind = "LARGE_EXTENT_NO_WINDING"
    else:
        kind = "COMPACT_NO_WINDING"
    return {"kind": kind, "wraps_y": wy, "wraps_x": wx,
            "crosses_seam": touches_seam, "bounding_span_y": span_y,
            "bounding_span_x": span_x, "cells": int(sub.sum())}


def legacy_extent_proxy(nX, nY, cid_mask):
    """The ORR01 indicator, reproduced under its historical name. NOT a topological test."""
    L = nX.shape[0]
    ys, xs = np.nonzero(cid_mask)
    if len(ys) == 0:
        return {"LEGACY_EXTENT_PROXY": False, "extent": 0.0}
    w = (nX + nY)[ys, xs].astype(float)
    def ang(idx):
        th = 2.0 * np.pi * idx / L
        return (np.arctan2((w * np.sin(th)).sum(), (w * np.cos(th)).sum()) % (2 * np.pi)) \
               * L / (2 * np.pi)
    cy, cx = ang(ys), ang(xs)
    dy = np.minimum(np.abs(ys - cy) % L, L - np.abs(ys - cy) % L)
    dx = np.minimum(np.abs(xs - cx) % L, L - np.abs(xs - cx) % L)
    ext = 2.0 * max(dy.max(), dx.max()) + 1.0
    return {"LEGACY_EXTENT_PROXY": bool(ext >= L * 0.5), "extent": float(ext)}
