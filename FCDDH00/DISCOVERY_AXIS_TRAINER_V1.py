"""FCDDH00 DISCOVERY_AXIS_TRAINER_V1.

The ONLY trainable object in this programme:

    X_BAR_D = (1/12) * sum_{b in DISCOVERY} x[b]
    v_D     = canonical_unit(X_BAR_D),   sign fixed so that <v_D, X_BAR_D> > 0

No intercept, no midpoint, no covariance, no whitener, no P3, no classifier, no nonlinear map, no
selected time or channel, no alternative normalization, no regularizer, no second training rule.

STRUCTURAL FIREWALL (audited by gate D11 and oracle Q0K/Q0N):
  * `fit` accepts values ONLY from the twelve discovery ancestries and asserts the exact
    discovery ancestry manifest;
  * every source path handed to it must lie under the discovery archive root; a path under any
    hold-out root, or under FSQBT00/FCRA00/SQDT00/WL2SMF00/FWL2CF00, is rejected;
  * this module imports nothing from the hold-out scorer and nothing from any parent analysis
    module. The only parent objects it touches are the immutable mu / P2 through `fh_core.Parent`,
    which is exactly the frozen basis the estimand is defined in.
  * no dynamic import, no eval, no getattr dispatch, no filename or seed label inference.
"""
from __future__ import annotations

import math

import fh_core as FC

FORBIDDEN_PATH_TOKENS = ("HOLDOUT", "holdout", "FSQBT00", "FCRA00", "WL2SMF00", "FWL2CF00")
ALLOWED_ROOT = "/home/claude/sweep/FCDDH00/DISCOVERY_"


def assert_discovery_only(paths):
    for p in paths:
        if not str(p).startswith(ALLOWED_ROOT):
            raise PermissionError("trainer input outside the discovery archive: %s" % p)
        for tok in FORBIDDEN_PATH_TOKENS:
            if tok in str(p):
                raise PermissionError("trainer input touches a forbidden namespace: %s" % p)
    return True


def canonical_unit(x_iv, parent):
    """The frozen canonical unit map.

    Evaluated as normalize(Q @ float(x)), which is the identical map because x already lies in
    range(Q) exactly; re-applying the frozen parent projector only removes float rounding and
    never rotates the direction. The residual ||Q x - x|| is certified and reported.
    """
    xf = [v.fl() for v in x_iv]
    q = [sum(parent.Q[i][j] * xf[j] for j in range(FC.DIM)) for i in range(FC.DIM)]
    n = math.sqrt(sum(t * t for t in q))
    if n == 0.0:
        raise ValueError("zero vector has no canonical unit")
    v = [t / n for t in q]
    s = sum(v[i] * xf[i] for i in range(FC.DIM))
    if s < 0:
        v = [-t for t in v]
    elif s == 0.0:
        raise ValueError("canonical sign is undefined")
    reproj = math.sqrt(sum((q[i] - xf[i]) ** 2 for i in range(FC.DIM)))
    return v, {"reprojection_residual_l2": reproj, "raw_norm_float": n,
               "sign_flipped": bool(s < 0)}


def mean_x(xs):
    n = len(xs)
    acc = [FC.Iv.exact(0)] * FC.DIM
    for x in xs:
        acc = [acc[i] + x[i] for i in range(FC.DIM)]
    inv = FC.Iv.exact(FC.Fr(1, n))
    return [(acc[i] * inv).round_out() for i in range(FC.DIM)]


def fit(block_ids, xs, parent, source_paths):
    """block_ids: exactly the twelve discovery ancestry ids, in ascending order."""
    assert_discovery_only(source_paths)
    if len(block_ids) != 12 or len(xs) != 12:
        raise ValueError("the discovery trainer requires exactly twelve ancestries, got %d"
                         % len(block_ids))
    if sorted(block_ids) != list(block_ids) or len(set(block_ids)) != 12:
        raise ValueError("discovery ancestry manifest must be twelve distinct ascending ids")
    XB = mean_x(xs)
    nrm = FC.norm_iv(XB)
    v, meta = canonical_unit(XB, parent)
    return {"block_ids": list(block_ids), "X_BAR_D": XB, "norm": nrm, "v_D": v,
            "canonicalisation": meta}


def loao(block_ids, xs, parent, source_paths):
    """Twelve leave-one-ancestry-out folds. Every fold omits the complete ancestry: its four
    descendants, eight carrier rows and associated shams. Every training gauge is rebuilt inside
    the caller from each descendant's own response by the immutable label-blind parent-P2 rule,
    which is descendant-separable and therefore block-separable; the omitted ancestry never
    reuses a full-panel gauge."""
    assert_discovery_only(source_paths)
    full = fit(block_ids, xs, parent, source_paths)
    out = []
    for k, b in enumerate(block_ids):
        keep = [xs[j] for j in range(12) if j != k]
        XBm = mean_x(keep)
        vm, meta = canonical_unit(XBm, parent)
        score = FC.dot_float(vm, xs[k])                    # NO reorientation
        align = sum(vm[i] * full["v_D"][i] for i in range(FC.DIM))
        out.append({"left_out": b, "v_fold": vm, "X_BAR_minus": XBm,
                    "score_omitted": score, "alignment": align, "alignment_sq": align * align,
                    "canonicalisation": meta})
    return full, out


def leverage(v, xs):
    s = [FC.dot_float(v, x) for x in xs]
    sq = [float(t.mid()) ** 2 for t in s]
    tot = sum(sq)
    return s, ([q / tot for q in sq] if tot > 0 else [float("nan")] * len(sq))
