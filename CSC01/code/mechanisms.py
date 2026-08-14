"""CSC01 §9-11 — the candidate cohesion mechanisms and the deterministic selection rule.

The rule is stated in full and applied mechanically. It reads only STRUCTURAL properties of each
candidate — how many parameters it adds, how many operators it touches, whether it changes
transport, whether it can create matter, whether it preserves the meaning of the pre-declared
controls, whether it admits an exact single-cell analysis. It reads no measurement, no outcome
and no score, so the selection cannot be steered by a result.
"""
from __future__ import annotations

CANDIDATES = {
    "C0_NO_CHANGE": {
        "operator": None,
        "law": "the balanced chemostat of ORR01 LawSpec v2, unchanged",
        "physical_reading": "the reference. A point source, free diffusion, a constant death "
                            "rate, and a chemostat that renews the medium without changing "
                            "occupancy.",
        "new_parameters": 0, "operators_modified": 0,
        "modifies_transport": False, "can_create_matter_away_from_the_source": False,
        "preserves_control_meanings": True, "exact_single_cell_analysis": True,
        "role": "reference arm; it is not a candidate for selection",
    },
    "C1_ADHESIVE_TRANSPORT": {
        "operator": "_diffuse",
        "law": "p_hop_X(cell) = p_hop_X * (1 - eps) ** (n_X(cell) - 1)",
        "physical_reading": "reversible binding between like molecules: a molecule surrounded "
                            "by its own kind moves less.",
        "new_parameters": 1, "operators_modified": 1,
        "modifies_transport": True, "can_create_matter_away_from_the_source": False,
        "preserves_control_meanings": True, "exact_single_cell_analysis": True,
    },
    "C2_LOCAL_AUTOCATALYSIS": {
        "operator": "_react",
        "law": "p_X(cell) = min(1, kX * n_X * (n_Y + kappa * n_X))",
        "physical_reading": "the cluster catalyses its own production.",
        "new_parameters": 1, "operators_modified": 1,
        "modifies_transport": False, "can_create_matter_away_from_the_source": True,
        "preserves_control_meanings": False,
        "why_controls_break": "the pre-declared control NO_ORGANISER rests on the fact that "
                              "n_Y == 0 forbids the appearance of X. Under C2 a seeded X "
                              "population grows with no organiser at all, so the control no "
                              "longer isolates what it was declared to isolate.",
        "exact_single_cell_analysis": True,
    },
    "C3_NEIGHBOUR_PROTECTED_DECAY": {
        "operator": "_decay",
        "law": "mu_X(cell) = mu_X * (1 - lambda) ** m(cell),  m = the number of X molecules in "
               "the four neighbouring cells",
        "physical_reading": "mutual stabilisation: a molecule with more neighbours of its own "
                            "kind is degraded more slowly. Nothing is created; a death is only "
                            "made less likely.",
        "new_parameters": 1, "operators_modified": 1,
        "modifies_transport": False, "can_create_matter_away_from_the_source": False,
        "preserves_control_meanings": True, "exact_single_cell_analysis": True,
    },
    "C4_MATRIX_CONFINEMENT": {
        "operator": "_diffuse",
        "law": "p_hop_X(cell) = p_hop_X * (1 - eps) ** n_WX(cell)",
        "physical_reading": "the population secretes a matrix — its own waste — which slows it "
                            "down where it has been.",
        "new_parameters": 1, "operators_modified": 1,
        "modifies_transport": True, "can_create_matter_away_from_the_source": False,
        "preserves_control_meanings": True, "exact_single_cell_analysis": True,
    },
}

RULE = [
    ("S1", "fewest NEW free parameters", lambda c: c["new_parameters"]),
    ("S2", "fewest engine operators modified", lambda c: c["operators_modified"]),
    ("S3", "does NOT modify transport, so that the inherited first-passage bounds and the "
           "MTW01 minority window survive unmodified", lambda c: int(c["modifies_transport"])),
    ("S4", "cannot create matter away from the declared source",
     lambda c: int(c["can_create_matter_away_from_the_source"])),
    ("S5", "preserves the meaning of every pre-declared control",
     lambda c: int(not c["preserves_control_meanings"])),
    ("S6", "admits an exact single-cell analysis",
     lambda c: int(not c["exact_single_cell_analysis"])),
]


def select():
    """Lexicographic minimisation over the rule, applied to every candidate except the
    reference. Returns (winner, table, unique)."""
    pool = {k: v for k, v in CANDIDATES.items() if v.get("role") is None}
    table = []
    for k, v in pool.items():
        table.append({"candidate": k, "scores": {s: f(v) for s, _, f in RULE},
                      "vector": [f(v) for _, _, f in RULE]})
    table.sort(key=lambda r: r["vector"])
    best = table[0]["vector"]
    tied = [r["candidate"] for r in table if r["vector"] == best]
    return table[0]["candidate"], table, len(tied) == 1


# ---------------------------------------------------------------- the passive calibration rule
CALIBRATION = {
    "parameter": "lambda",
    "target": "a molecule sitting at the MEDIAN neighbour count observed in the C0 reference "
              "must have exactly HALF the death rate of an isolated molecule",
    "equation": "(1 - lambda) ** m_star = 1/2   =>   lambda = 1 - 2 ** (-1 / m_star)",
    "m_star": "the median number of X molecules in the four neighbouring cells, over the X "
              "molecules of the main component, measured in the PASSIVE ASSAY",
    "passive_assay": "arms run under C0 — the unchanged balanced chemostat — on their own "
                     "seeds, from which ONLY the structural statistic m_star is read. No gate "
                     "verdict, no PASS, no classification and no compactness statistic of the "
                     "assay enters the choice of lambda.",
    "why_this_is_outcome_independent": "m_star is a property of the reference state's geometry, "
                                       "fixed before any arm of the mechanism is run. The "
                                       "factor 1/2 is declared here, in advance, and is not "
                                       "tuned.",
    "failure_mode": "if m_star == 0 the equation has no solution and the mission stops with "
                    "COHESION_CALIBRATION_FAIL.",
    "assay_seeds": [6301, 6302, 6303, 6304],
}
