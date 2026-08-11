"""FCDDH00 HOLDOUT_FIXED_AXIS_SCORER_V1.

Scores the untouched hold-out panel with the axis serialized from the discovery panel. It is
structurally incapable of fitting, centering, rotating, rescaling, orienting or choosing an axis
from hold-out rows:

  * it imports NOTHING from DISCOVERY_AXIS_TRAINER_V1 and nothing from any historical direction;
  * it contains no eigendecomposition, no SVD, no PCA, no covariance, no optimizer, no argmin
    over an axis, no threshold selection and no model comparison;
  * `load_axis` refuses any vector that is not read back byte-for-byte from the committed
    serialization, and refuses to normalise, re-orient or rescale it;
  * `score` raises if asked to center, whiten or re-sign;
  * the ONLY search it performs is the finite exhaustive enumeration of the inherited linked A/B
    gauge under the immutable parent-P2 residual criterion, which is label-blind and axis-blind
    and returns the COMPLETE co-optimal orbit.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

import fh_core as FC

_FORBIDDEN = ("fit", "pca", "svd", "eig", "center", "whiten", "reorient", "rescale")


class FrozenAxis:
    __slots__ = ("v", "sha256", "source", "estimand", "axis_space", "meta")

    def __init__(self, v, sha256, meta):
        self.v = tuple(float(t) for t in v)
        self.sha256 = sha256
        self.source = meta["SOURCE"]
        self.estimand = meta["ESTIMAND"]
        self.axis_space = meta["AXIS_SPACE"]
        self.meta = meta

    def __setattr__(self, k, val):
        if k in FrozenAxis.__slots__ and hasattr(self, k):
            raise PermissionError("the hold-out axis is immutable")
        object.__setattr__(self, k, val)


def load_axis(npz_path, json_path):
    """Read back the committed axis byte-for-byte. No normalisation, no reorientation."""
    raw = open(npz_path, "rb").read()
    d = np.load(npz_path)
    meta = json.load(open(json_path))
    if meta["SOURCE"] != "TWELVE_NEW_CROSSED_DISCOVERY_ANCESTRIES":
        raise PermissionError("axis SOURCE is not the FCDDH00 discovery panel")
    if meta["AXIS_SPACE"] != "OUTSIDE_PARENT_P2__CARRIER_DIFFERENTIAL":
        raise PermissionError("axis space mismatch")
    if meta["ESTIMAND"] != "ALLOCATION_AVERAGED_NEAR_MINUS_FAR_X_CARRIER":
        raise PermissionError("axis estimand mismatch")
    v_npz = [float(t) for t in d["v_D"]]
    v_json = [float(t) for t in meta["v_D"]]
    if v_npz != v_json:
        raise PermissionError("axis disk round-trip disagreement between npz and json")
    if hashlib.sha256(raw).hexdigest() != meta["npz_sha256"]:
        raise PermissionError("axis npz hash mismatch")
    return FrozenAxis(v_npz, hashlib.sha256(raw).hexdigest(), meta)


def score_block(axis: FrozenAxis, x_iv, center=None, rescale=None, reorient=None):
    if center is not None or rescale is not None or reorient is not None:
        raise PermissionError("centering, rescaling and reorientation are forbidden on hold-out")
    return FC.dot_float(list(axis.v), x_iv)


def pair_margins(axis: FrozenAxis, d_near, d_far):
    """p[b,aN,aF; v] = <v, d[NEAR,aN] - d[FAR,aF]> for the four cross-orbit pairings."""
    out = {}
    for aN in (0, 1):
        for aF in (0, 1):
            diff = FC.vec_sub(d_near[aN], d_far[aF])
            out[(aN, aF)] = FC.dot_float(list(axis.v), diff)
    return out


def block_success(p, apair, axis_norm_upper):
    """J[b;v] = 1 iff all four lower(p) > upper(A_PAIR); m[b;v] = the worst certified margin.

    A_PAIR is inflated by the certified upper bound on ||v||, so the Cauchy-Schwarz step
    |<v,w>| <= ||v|| ||w|| stays rigorous under float64 unit-norm rounding.
    """
    verdicts, margins = {}, {}
    for key, piv in p.items():
        bound = (apair[key] * FC.Iv.exact(axis_norm_upper)).round_out()
        verdicts[key] = FC.certified_verdict(piv, bound)
        margins[key] = (piv - bound).round_out()
    J = 1 if all(v == "PASS" for v in verdicts.values()) else 0
    m = min(margins.values(), key=lambda iv: iv.lo)
    return J, m, verdicts, margins


def enumerate_linked_gauge(parent, rows_uv):
    """The ONE permitted finite search: the inherited linked A/B gauge of ONE descendant, under
    the immutable parent-P2 residual criterion. Label-blind, axis-blind. Returns the complete
    co-optimal orbit."""
    (u1, v1), (u2, v2) = rows_uv
    D = FC.gauge_statistic(parent, u1, v1, u2, v2)
    s, coopt = FC.gauge_sign(D)
    orbit = [+1, -1] if coopt else [s]
    return s, coopt, orbit, D
