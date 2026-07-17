# DOWNSTREAM-ORDER-READER-01 — frozen claim and classification table

The statistical unit is the original source world. `CI` below is the two-sided 95% Student-t interval for the
original-world `delta_A_O` values. `delta_num` is the largest complete-world propagated numerical bound. A
direction converges when at least `ceil(0.75*n_complete)` world signs agree.

| Outcome | Frozen condition | Permitted interpretation |
|---|---|---|
| `PREDICTED_ATTENUATION` | all gates valid; `CI.lower > delta_num`; positive sign convergence | Downstream causal access in the preregistered attenuation direction under this probe. |
| `OPPOSITE_SIGN_FUNCTIONAL_ACCESS` | all gates valid; `CI.upper < -delta_num`; negative sign convergence | Downstream causal access, while falsifying the predicted attenuation direction. Never absence or manipulation failure. |
| `NO_ACCESS_ESTABLISHED` | all gates valid; `CI` intersects `[-delta_num,+delta_num]`; neither sign converges; no scientific equivalence margin | The experiment does not establish access. This is not evidence of absence or equivalence. |
| `EQUIVALENT_AT_DECLARED_SCALE` | all gates valid; an independently justified pre-outcome margin `m_0 > delta_num` exists; entire `CI` is inside `[-m_0,+m_0]` | Equivalence only at that declared scientific scale. |
| `MANIPULATION_INVALID` | any clone, schedule, ramp, logger, mask, manifest or other mechanical invariant fails | No scientific sign interpretation. |
| `UNRESOLVED` | interval/sign rules conflict, controls are incompatible, numerical failure occurs, or the valid-world floor is missed | The unique scientific distinction cannot be made. Never convert to absence. |

This package freezes `equivalence_margin=null`; therefore `EQUIVALENT_AT_DECLARED_SCALE` is deliberately
unreachable unless humans independently justify and reseal a margin before outcomes.

Administrative run dispositions are orthogonal to the six scientific conclusions:

| Run disposition | Trigger | Scientific classification |
|---|---|---|
| `SCIENTIFIC_CLASSIFIED` | at least 18 complete worlds and all global gates pass | one of the applicable six outcomes |
| `FEASIBILITY_FAIL` | fewer than 18 complete original worlds after all 48 fixed source worlds | `UNRESOLVED` |
| `NUMERICAL_FAILURE` | any nonfinite value or numerical/reproduction gate failure | `UNRESOLVED` |
| `MANIPULATION_INVALID` | mechanical kill switch | `MANIPULATION_INVALID` |

Precedence is administrative safety first: numerical failure, then manipulation invalidity, then complete-world
floor, then the scientific interval/sign rules. `lam_minus=0` order response and direct source susceptibility are
secondary and have no precedence over the primary interaction.
