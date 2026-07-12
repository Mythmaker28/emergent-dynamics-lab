"""R8 identity gates (A: diversity, B: predictive identity, C: causal identity).

Every metric here must first pass SYNTHETIC MUST-PASS and MUST-FAIL cases (tests/test_r8_gates.py) proving it can
both fire and fail. Four times this session I wrote a criterion that could not fire; this module exists so that
cannot happen again.

FORBIDDEN identity features (R8-B): absolute position, total mass, absolute orientation, tracker ID. Phenotypes fed
to these gates must already be invariant to translation and rotation.
"""

from __future__ import annotations

import numpy as np

MARGIN_A = 2.0        # R8-A: between-entity distance must exceed within-entity drift by this FACTOR
MARGIN_C = 0.25       # R8-C: identity-specific recovery, intact minus scrambled, absolute


def within_entity_drift(traj: np.ndarray) -> float:
    """Mean phenotype distance between successive observations OF THE SAME entity: how much identity 'wobbles'.
    traj: (T, F)."""
    if traj.shape[0] < 2:
        return 0.0
    d = np.linalg.norm(np.diff(traj, axis=0), axis=1)
    return float(d.mean())


def between_entity_distance(trajs: list[np.ndarray]) -> float:
    """Mean phenotype distance between DIFFERENT entities, compared at matched times."""
    if len(trajs) < 2:
        return 0.0
    T = min(t.shape[0] for t in trajs)
    ds = []
    for i in range(len(trajs)):
        for j in range(i + 1, len(trajs)):
            ds.append(np.linalg.norm(trajs[i][:T] - trajs[j][:T], axis=1).mean())
    return float(np.mean(ds))


def r8a_diversity(trajs: list[np.ndarray], margin: float = MARGIN_A) -> dict:
    """R8-A. Entities must be more different from EACH OTHER than each is from ITSELF over time."""
    drift = float(np.mean([within_entity_drift(t) for t in trajs]))
    between = between_entity_distance(trajs)
    ratio = between / (drift + 1e-12)
    return {"within_entity_drift": drift, "between_entity_distance": between,
            "separation_ratio": ratio, "margin": margin, "passes": bool(ratio > margin)}


def r8b_predictive_identity(early: list[np.ndarray], late: list[np.ndarray]) -> dict:
    """R8-B. Frozen 1-NN rule fitted ONLY on EARLY states. Each LATE observation is assigned to the entity whose
    EARLY prototype is nearest. Accuracy must beat chance. Constituent turnover happens between early and late."""
    protos = np.stack([e.mean(axis=0) for e in early])              # fitted on early states ONLY
    n = len(late)
    correct = 0
    total = 0
    for true_id, lt in enumerate(late):
        for obs in lt:
            pred = int(np.argmin(np.linalg.norm(protos - obs, axis=1)))
            correct += int(pred == true_id)
            total += 1
    acc = correct / total if total else 0.0
    chance = 1.0 / n if n else 0.0
    return {"accuracy": acc, "chance": chance, "n_entities": n, "n_observations": total,
            "passes": bool(total > 0 and acc > chance + 0.25)}


def r8c_causal_identity(source: np.ndarray, intact: list[np.ndarray], scrambled: list[np.ndarray],
                        others: list[np.ndarray], margin: float = MARGIN_C) -> dict:
    """R8-C. PRIMARY OUTCOME = identity-specific recovery, NOT entity presence.

    A recovered entity counts as 'the source' only if its phenotype is nearer to the SOURCE prototype than to any
    other entity's prototype. Intact cargo must recover source identity at a rate exceeding scrambled cargo by
    `margin`. A scrambled cargo that reconstructs a generic entity but a DIFFERENT identity is a null success at
    entity-presence and a FAILURE at identity -- which is exactly the discrimination this gate exists to make.
    """
    protos = np.stack([source] + list(others))

    def rate(obs_list):
        if not obs_list:
            return 0.0
        hits = 0
        for o in obs_list:
            hits += int(int(np.argmin(np.linalg.norm(protos - o, axis=1))) == 0)
        return hits / len(obs_list)

    ri, rs = rate(intact), rate(scrambled)
    return {"intact_source_identity_rate": ri, "scrambled_source_identity_rate": rs,
            "difference": ri - rs, "margin": margin, "passes": bool((ri - rs) > margin)}
