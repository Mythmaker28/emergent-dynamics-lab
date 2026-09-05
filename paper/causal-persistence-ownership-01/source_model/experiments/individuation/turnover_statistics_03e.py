"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — repaired frozen ownership + causal-expression inference (supersedes 03C).

Red-team blockers B2 / STAT-01/02/03: the 03C `turnover_statistics.evaluate_scope_models` had no within-world
permutation ownership null, no causal-expression gate, and declared `primary_gate_pass` from the local-storage
decoder alone (and used G-full incoherently). This module adds, all FROZEN before prospective data:

  G-OWN-PERM        L own-dose held-out skill exceeds a WITHIN-WORLD dose permutation null (frozen p < 0.05).
  G-LOCAL-EXCLUSION L has strictly lower held-out loss than N, E, Gm (world-level target-memory-removed) AND B;
                    each paired Student-t lower 95% bound > 0. (NOT "L beats G-full": G-full nests L, so it is a
                    non-gating diagnostic — G-INCREMENT.)
  G-CAUSAL          paired original-world causal-expression gate at deep turnover (own > 0, > sham, > neighbour,
                    lambda_plus-only ablation collapse, fixed-mask directional consistency).
  PRIMARY PASS      = G-OWN-PERM AND G-LOCAL-EXCLUSION AND G-CAUSAL (a positive feeding contrast alone is NOT enough).

Leak-free bootstrap and outer LOWO are reused verbatim from the audited `turnover_statistics.py`. A content-hash
duplicate-world guard rejects the disguised-duplicate leakage that a by-id disjointness check cannot see.
"""
from __future__ import annotations

import hashlib
import importlib.util as _ilu
import sys as _sys
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

_spec = _ilu.spec_from_file_location("_st03c", Path(__file__).resolve().parent / "turnover_statistics.py")
_st = _ilu.module_from_spec(_spec); _sys.modules["_st03c"] = _st; _spec.loader.exec_module(_st)  # type: ignore
outer_lowo_predictions = _st.outer_lowo_predictions
original_world_losses = _st.original_world_losses
t_interval = _st.t_interval
fixed_fold_bootstrap = _st.fixed_fold_bootstrap
evaluate_scope_models = _st.evaluate_scope_models
RIDGE_LAMBDA = _st.RIDGE_LAMBDA

PERM_REPS = 1000                 # frozen within-world permutation reps
PERM_SEED = 20260715
OWN_PERM_ALPHA = 0.05            # frozen ownership permutation threshold
COLLAPSE_FRACTION = 0.5          # mechanistic: removing the lambda_plus uptake channel must at least halve own


def _mean_skill(X, y, groups):
    outer = outer_lowo_predictions(X, y, groups)
    losses = original_world_losses(y, outer)
    return float(np.mean([losses[w]["skill"] for w in losses]))


def within_world_permutation_null(X, y, groups, reps=PERM_REPS, seed=PERM_SEED) -> dict:
    """Permute own-dose WITHIN each original world; recompute L held-out mean skill. Frozen p<0.05 ownership null."""
    X = np.asarray(X, float); y = np.asarray(y, float); groups = np.asarray(groups)
    obs = _mean_skill(X, y, groups)
    rng = np.random.default_rng(seed)
    idxby = {g: np.where(groups == g)[0] for g in np.unique(groups)}
    null = np.empty(reps)
    for r in range(reps):
        yp = y.copy()
        for g, ix in idxby.items():
            yp[ix] = y[ix][rng.permutation(len(ix))]
        null[r] = _mean_skill(X, yp, groups)
    p = float((np.sum(null >= obs) + 1) / (reps + 1))
    return {"observed_mean_skill": obs, "perm_null_p": p, "perm_null_95": float(np.percentile(null, 95)),
            "reps": reps, "alpha": OWN_PERM_ALPHA, "pass": bool(p < OWN_PERM_ALPHA),
            "method": "within-original-world dose permutation; L held-out mean skill; no coordinate switch"}


def content_hashes(matrix) -> list[str]:
    return [hashlib.sha256(np.ascontiguousarray(np.asarray(row, float)).tobytes()).hexdigest() for row in matrix]


def assert_no_duplicate_world_content(matrix_by_scope: Mapping[str, np.ndarray], groups) -> dict:
    """Reject a world duplicated under a NEW id (identical content, different group) — invisible to by-id disjointness.
    Two DIFFERENT groups whose full row-sets are identical are rejected; a same-id duplicate is allowed (it stays in
    one fold, which is safe). Uses the L scope (target memory) as the identity fingerprint."""
    groups = np.asarray(groups)
    L = np.asarray(matrix_by_scope["L"], float)
    sig = {}
    for g in np.unique(groups):
        rows = L[groups == g]
        h = hashlib.sha256(np.ascontiguousarray(rows[np.lexsort(rows.T)]).tobytes()).hexdigest()
        if h in sig and sig[h] != int(g):
            raise AssertionError(f"duplicate-world content: worlds {sig[h]} and {int(g)} have identical L rows "
                                 f"under different ids (disguised leakage rejected)")
        sig[h] = int(g)
    return {"n_worlds": int(len(np.unique(groups))), "unique_content_signatures": len(sig), "duplicate_content": False}


def evaluate_ownership_03e(matrices: Mapping[str, np.ndarray], own_dose, original_world) -> dict:
    """Coherent gated ownership. Gated scopes: L must beat N, E, Gm, B. Diagnostic (non-gating): P, Gf."""
    required = {"L", "N", "E", "Gm", "B"}
    missing = required - set(matrices)
    if missing:
        raise ValueError(f"missing frozen gated scope matrices: {sorted(missing)}")
    assert_no_duplicate_world_content(matrices, original_world)
    own_dose = np.asarray(own_dose, float); groups = np.asarray(original_world)

    scopes = ["L", "N", "E", "Gm", "B"] + [s for s in ("P", "Gf") if s in matrices]
    models, raw = {}, {}
    for s in scopes:
        outer = outer_lowo_predictions(matrices[s], own_dose, groups)
        lm = original_world_losses(own_dose, outer); worlds = sorted(lm)
        skills = [lm[w]["skill"] for w in worlds]
        models[s] = {"skill_t95": t_interval(skills), "skill_fixed_fold_bootstrap95": fixed_fold_bootstrap(skills)}
        raw[s] = {w: lm[w]["model_nmse"] for w in worlds}

    def paired(ref, comp):
        worlds = sorted(raw[ref]); scores = [raw[comp][w] - raw[ref][w] for w in worlds]  # +ve: ref lower loss
        return {"positive_means": f"{ref} lower held-out loss than {comp}", "t95": t_interval(scores),
                "fixed_fold_bootstrap95": fixed_fold_bootstrap(scores)}

    exclusion = {c: paired("L", c) for c in ("N", "E", "Gm", "B")}
    increment = {"P_over_L": paired("P", "L") if "P" in raw else None,
                 "Gf_over_L": paired("Gf", "L") if "Gf" in raw else None}

    perm = within_world_permutation_null(matrices["L"], own_dose, groups)
    g_local = {"L_information_lower_gt_zero": models["L"]["skill_t95"]["lower"] > 0.0,
               "L_over_N": exclusion["N"]["t95"]["lower"] > 0.0,
               "L_over_E": exclusion["E"]["t95"]["lower"] > 0.0,
               "L_over_Gm": exclusion["Gm"]["t95"]["lower"] > 0.0,
               "L_over_B": exclusion["B"]["t95"]["lower"] > 0.0}
    g_local["pass"] = bool(all(g_local.values()))
    return {"label": "own cumulative dose; geometric neighbour; leak-free LOWO; low-dim E/Gm",
            "G_OWN_PERM": perm, "models": models, "G_LOCAL_EXCLUSION": {**g_local, "detail": exclusion},
            "G_INCREMENT_diagnostic": increment,
            "gated_scopes": ["L", "N", "E", "Gm", "B"], "non_gating_diagnostics": ["P", "Gf"]}


def causal_expression_gate(deep_batteries: Sequence[dict], min_valid_worlds: int) -> dict:
    """Paired original-world causal-expression gate at deep turnover. Each battery has intact/sham/ablate_plus/
    erase[K]/erase_ablate_plus[K] with 'tracked' and 'fixed' K-vectors. Unit = original world (mean over targets)."""
    K = 3
    own, own_sham, own_neigh, own_fixed, own_ap = [], [], [], [], []
    for b in deep_batteries:
        A = b["intact"]["tracked"]; Af = b["intact"]["fixed"]; sh = b["sham"]["tracked"]
        er = b["erase"]; ap = b["ablate_plus"]["tracked"]; eap = b["erase_ablate_plus"]
        own.append(float(np.mean([A[i] - er[i]["tracked"][i] for i in range(K)])))
        own_sham.append(float(np.mean([(A[i] - er[i]["tracked"][i]) - (A[i] - sh[i]) for i in range(K)])))
        own_neigh.append(float(np.mean([(A[i] - er[i]["tracked"][i]) -
                          np.mean([A[i] - er[j]["tracked"][i] for j in range(K) if j != i]) for i in range(K)])))
        own_fixed.append(float(np.mean([Af[i] - er[i]["fixed"][i] for i in range(K)])))
        own_ap.append(float(np.mean([ap[i] - eap[i]["tracked"][i] for i in range(K)])))
    own = np.array(own)
    ci_own = t_interval(own); ci_sham = t_interval(own_sham); ci_neigh = t_interval(own_neigh)
    ci_fixed = t_interval(own_fixed); ci_ap = t_interval(own_ap)
    mean_own = float(own.mean())
    collapse = bool(ci_ap["upper"] < COLLAPSE_FRACTION * mean_own) if mean_own > 0 else False
    gate = {"n_worlds": len(deep_batteries), "min_valid_worlds": min_valid_worlds,
            "own_t95": ci_own, "own_minus_sham_t95": ci_sham, "own_minus_neigh_t95": ci_neigh,
            "own_fixed_t95": ci_fixed, "own_under_lambda_plus_ablation_t95": ci_ap,
            "collapse_fraction": COLLAPSE_FRACTION,
            "own_lower_gt_zero": ci_own["lower"] > 0.0,
            "own_gt_sham": ci_sham["lower"] > 0.0,
            "own_gt_neighbour": ci_neigh["lower"] > 0.0,
            "lambda_plus_ablation_collapse": collapse,
            "fixed_mask_direction_consistent": bool(ci_fixed["mean"] > 0.0),
            "enough_worlds": bool(len(deep_batteries) >= min_valid_worlds)}
    gate["pass"] = bool(gate["own_lower_gt_zero"] and gate["own_gt_sham"] and gate["own_gt_neighbour"]
                        and gate["lambda_plus_ablation_collapse"] and gate["fixed_mask_direction_consistent"]
                        and gate["enough_worlds"])
    return gate


def primary_gate(ownership: dict, causal: dict) -> dict:
    g_own_perm = bool(ownership["G_OWN_PERM"]["pass"])
    g_local = bool(ownership["G_LOCAL_EXCLUSION"]["pass"])
    g_causal = bool(causal["pass"])
    return {"G_OWN_PERM": g_own_perm, "G_LOCAL_EXCLUSION": g_local, "G_CAUSAL": g_causal,
            "primary_gate_pass": bool(g_own_perm and g_local and g_causal),
            "rule": "primary = G_OWN_PERM AND G_LOCAL_EXCLUSION AND G_CAUSAL (feeding contrast alone insufficient)"}
