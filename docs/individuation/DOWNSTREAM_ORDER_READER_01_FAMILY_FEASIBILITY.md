# DOWNSTREAM-ORDER-READER-01 — fixed family and complete-block feasibility

The historical `17/24` complete-world count is used only to budget a later family. It is not a downstream outcome,
effect estimate, prior scientific success probability, or seed-selection criterion.

## Sensitivity calculation

Observed logistics rate:

```text
p_hat = 17/24 = 0.7083333333
exact Clopper-Pearson 95% interval = [0.4890521861, 0.8738479115]
```

For a fixed `N=48` source worlds and floor `K=18` complete worlds:

| Assumption about valid-world rate | P(number complete >= 18) |
|---|---:|
| plug-in historical rate `17/24` | 0.999999604 |
| exact-interval lower rate `0.4890521861` | 0.958475101 |
| Beta-binomial posterior predictive, uniform Beta(1,1) sensitivity prior | 0.996972271 |

The Beta-binomial predictive quantiles for the number complete among 48 are:

```text
2.5%: 22; 5%: 24; median: 34; 95%: 41; 97.5%: 43.
```

The uniform prior is stated only as a sensitivity device; the exact lower-bound calculation gives the conservative
frequentist check. No effect-size power was calculated because no independent `m_A` exists. This is a capacity
calculation, not power to detect the scientific interaction.

## Frozen plan

- Maximum and planned family size: exactly 48 original source worlds.
- Minimum complete original worlds: 18.
- Run all 48 in the predeclared manifest order if later authorized.
- No outcome-triggered reserve, extension, replacement seed, early scientific stop or post-outcome change to 18.
- Ineligibility and survival are recorded without looking at source or face-flux outcomes.
- An incomplete world contributes to feasibility counts only and is never assigned a zero contrast.
- Fewer than 18 complete worlds after W048: `FEASIBILITY_FAIL` and scientific `UNRESOLVED`.

No future seed namespace was inspected, selected or reserved in producing this analysis.
