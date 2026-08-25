# OMLDCT01 — HUMAN DECISION ADDENDUM

Additive. The LDFMA01 parent handoff is **not** mutated or rewritten; its bytes stand as committed
(`e3ec4b92…`). These five lines complete it, and they were frozen **before world 1**.

```
FRESH_WORLD_COUNT_AT_DECISION   = 0
BASE_SEEDS_CONSUMED_AT_DECISION = 0
OUTCOMES_ACCESSED               = none
```

```
PRIMARY_AND_COPRIMARY_COMBINATION = AND_WITH_CONCORDANT_DIRECTION
ZERO_DIFFERENCE_TREATMENT         = PRATT_EXACT_SIGN_FLIP
MINIMUM_VALID_PAIR_COUNT          = 41
TECHNICALLY_INVALID_RULE          = ANY_LOAD_BEARING_PAIR_OR_CAMPAIGN_INTEGRITY_FAILURE_INVALIDATES;
                                    PURE_SCIENTIFIC_UNDER_ACCRUAL_WITHOUT_TECHNICAL_FAILURE_MAPS_TO
                                    INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS
NULL_RESULT_INTERPRETATION        = INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT
```

The handoff had already frozen the endpoints, the statistic, the direction, the alpha and the sign
convention. These five add how the endpoints combine, what happens to zero differences, how many
pairs are required, what invalidates a pair or the campaign, and what a non-rejection may be called.

`FIVE_LINE_DECISION_SELF_TEST = PASS` — ten deterministic cases, no scientific trajectory. Pratt is
shown to differ from plain Wilcoxon on a six-pair case (p = 0.625 vs 0.875); all-zero differences
give p = 1 exactly; 40 valid pairs return `INSUFFICIENT` however strong the effect.
