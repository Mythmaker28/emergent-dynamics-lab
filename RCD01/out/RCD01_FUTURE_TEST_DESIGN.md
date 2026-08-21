# RCD01 §10-§11 — CONCEPTION DU FUTUR TEST DE REPRODUCTION MINIMALE

`STATUS = DESIGNED_BUT_NOT_ELIGIBLE_UNTIL_THE_INTERVENTION_EXISTS`

**Bloqueur : `GLOBAL_ORGANISER_OFF_ONLY`**

## Les trois phases

1. **Phase 1** — run the exact frozen B1 law until the daughter reaches the frozen functional maturation event
2. **Phase 2** — at that frozen event step, apply the predeclared SELECTIVE parent-off intervention
3. **Phase 3** — test whether the daughter alone re-establishes and holds the qualified local X response for a physically derived hold interval

Intervalle de maintien en phase 3 : **250 pas**. the same T_PRIMARY_STEPS, one e-folding of the slowest mode of the X operator; using a shorter interval would let a decaying cloud pass

## Attaques contre la conception

**intervention specificity** — the intervention must be qualified first: bit-identical trajectories when not armed, occupancy conserved, no X touched, no resource touched, the untouched centre's cells provably unaffected. That qualification is the successor mission, not this test.

**causal interpretation** — a SHAM arm with identical scheduling and no removal, plus a GLOBAL organiser-off arm, separate daughter autonomy from the act of intervening and from generic resilience to any Y removal.

**selection bias from conditioning on a successful Phase 1** — the PRIMARY estimand is the population rate per independently seeded world, denominator = all seeded worlds. The conditional daughter-survival probability is reported as secondary and explicitly labelled conditional.

**post-selection denominator** — every seeded world counts, including those that never reach Phase 2; those are reproduction failures, not exclusions.

**fixed-horizon requirement** — identical horizon and identical stop rules for all arms, as in FDFLT01, except that the PREMATURE_THIRD_CENTRE stop must be reconsidered because it censors R3 by construction; changing it changes the estimand and must be declared, not slipped in.

**how failures before intervention count** — in the denominator, as failures. A world that never forms a materially reconstructed daughter has not reproduced.

**is a control intervention needed** — yes, two: SHAM and PRE_MATURATION_INTERVENTION. The latter tests that the maturation interval is doing work rather than the daughter being robust from birth.

**is a sham intervention needed** — yes. Without it, any difference could be the scheduling machinery rather than the removal.

## Estimandes

- **Primaire** : P(complete reproduction event per independently seeded world) = P(R0 and R1 and R2)
- Secondaire : P(daughter survives parent-off | functional materially-reconstructed daughter formed)

conditioning the denominator on worlds that reach Phase 2 estimates the CONDITIONAL daughter-independence probability, not the population reproduction rate. Both must be reported, with the population rate as the primary.

## Controles minimaux

- **SHAM** — identical scheduling and bookkeeping, no Y removed — separates the intervention from its timing
- **GLOBAL_ORGANISER_OFF** — the existing OBTC02 intervention — distinguishes daughter autonomy from any-Y-removal
- **PRE_MATURATION_INTERVENTION** — parent removed BEFORE the daughter matures — tests that the hold interval is doing work

Pourquoi pas davantage : a daughter-off symmetry control adds no discrimination once the parent/daughter label is tie-broken deterministically, and multiplying arms costs the budget it would need.

## Capacite de decision, binomiale exacte

Taux observe `P(R0 et R1)` = 0.130208, soit **33.3 mondes de phase 2 attendus sur 256**.

| survie fille supposee `q` | taux population | n requis vs `p0=0,05` | n requis vs `p0=0,02` | puissance a 256 (`p0=0,02`) |
|---|---|---|---|---|
| 1.00 | 0.1302 | 77 | 32 | 1.000 |
| 0.80 | 0.1042 | 140 | 40 | 1.000 |
| 0.60 | 0.0781 | 467 | 85 | 0.996 |
| 0.50 | 0.0651 | 1451 | 120 | 0.973 |
| 0.40 | 0.0521 | None | 195 | 0.862 |
| 0.30 | 0.0391 | None | 462 | 0.545 |
| 0.20 | 0.0260 | None | 3754 | 0.135 |

Contre un nul de 0,05 le test n'est decidable dans 256 mondes que si `q >= 0,80`. Contre un nul de 0,02 il l'est jusqu'a `q ~ 0,40`. **Le nul doit etre gele avant le premier monde, avec sa derivation**, exactement comme FDFLT01 a gele 0,10.

Aucune execution dans RCD01.

