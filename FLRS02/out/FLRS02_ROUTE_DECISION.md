# FLRS02 — DECISION DE ROUTE

`NEW_SCIENTIFIC_ENGINE_RUNS = 0` — `NEW_WORLD_CONSTRUCTIONS = 0` — `NEW_SEEDS = 0` — `NEW_TRAJECTORIES = 0` — `CHECKPOINT_CONTINUATIONS = 0`

## Disposition

```
FINAL_ROUTE_DISPOSITION = ONE_EXISTING_POINT_DIRECT_TEST_JUSTIFIED
SELECTED_POINT = B1
```

## 1. Le critere primaire et pourquoi

`f_primary = 0.6321205588`, soit `T_primary = 249.4996659983` pas.

Ce n'est pas une convention. Le spectre exact de l'operateur par pas `(1-muX)*Hop` montre que le mode de population `k=0` est le **mode le plus lent**, de taux exactement `-ln(1-muX)`. Le deuxieme mode a un e-folding de 209.734957 pas. Toute fonctionnelle locale positive du champ X relaxe donc au taux `muX` aux temps longs.

## 2. L'atlas ponctuel — le monde est l'unite

Intervalles de Clopper-Pearson exacts a 95 %. Aucune approximation normale n'est employee nulle part.

### B1 — `kY = 2.5118864315e-05`, `muY = 9.2611872813e-05`

| Probabilite | compte | n | estimation | IC 95 % exact |
|---|---|---|---|---|
| `P_FIRST_BIRTH` | 16 | 44 | 0.3636 | [0.2241, 0.5223] |
| `P_LINEAGE_NON_EXTINCTION` | 16 | 44 | 0.3636 | [0.2241, 0.5223] |
| `P_GEOMETRIC_TWO_CENTRES` | 16 | 44 | 0.3636 | [0.2241, 0.5223] |
| `P_FUNCTIONAL_MATURATION_T_50` | 15 | 44 | 0.3409 | [0.2049, 0.4992] |
| `P_FUNCTIONAL_MATURATION_T_primary` | 15 | 44 | 0.3409 | [0.2049, 0.4992] |
| `P_FUNCTIONAL_MATURATION_T_80` | 13 | 44 | 0.2955 | [0.1676, 0.4520] |
| `P_FUNCTIONAL_MATURATION_T_90` | 12 | 44 | 0.2727 | [0.1496, 0.4279] |
| `P_THIRD_BEFORE_FUNCTION` | 0 | 44 | 0.0000 | [0.0000, 0.0804] |
| `P_X_INTEGRITY` | 44 | 44 | 1.0000 | [0.9196, 1.0000] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_50` | 14 | 44 | 0.3182 | [0.1861, 0.4758] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_primary` | 13 | 44 | 0.2955 | [0.1676, 0.4520] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_80` | 9 | 44 | 0.2045 | [0.0980, 0.3530] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_90` | 6 | 44 | 0.1364 | [0.0517, 0.2735] |

Naissances : 16. Extinctions : 28. Atteignent S : 16. Atteignent P : 7. Echecs d'integrite : 0.

Delai de separation geometrique : mediane 101.0 pas (n=16). Duree maximale d'un episode S : 4624 pas.

Rapport de reponse X du centre le plus faible a `T_primary` : mediane 0.7396 (exigence 0.6321).

### B2 — `kY = 2.1544346900e-05`, `muY = 1.0000000000e-08`

| Probabilite | compte | n | estimation | IC 95 % exact |
|---|---|---|---|---|
| `P_FIRST_BIRTH` | 18 | 44 | 0.4091 | [0.2634, 0.5675] |
| `P_LINEAGE_NON_EXTINCTION` | 44 | 44 | 1.0000 | [0.9196, 1.0000] |
| `P_GEOMETRIC_TWO_CENTRES` | 18 | 44 | 0.4091 | [0.2634, 0.5675] |
| `P_FUNCTIONAL_MATURATION_T_50` | 14 | 44 | 0.3182 | [0.1861, 0.4758] |
| `P_FUNCTIONAL_MATURATION_T_primary` | 14 | 44 | 0.3182 | [0.1861, 0.4758] |
| `P_FUNCTIONAL_MATURATION_T_80` | 13 | 44 | 0.2955 | [0.1676, 0.4520] |
| `P_FUNCTIONAL_MATURATION_T_90` | 12 | 44 | 0.2727 | [0.1496, 0.4279] |
| `P_THIRD_BEFORE_FUNCTION` | 0 | 44 | 0.0000 | [0.0000, 0.0804] |
| `P_X_INTEGRITY` | 44 | 44 | 1.0000 | [0.9196, 1.0000] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_50` | 14 | 44 | 0.3182 | [0.1861, 0.4758] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_primary` | 12 | 44 | 0.2727 | [0.1496, 0.4279] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_80` | 10 | 44 | 0.2273 | [0.1147, 0.3784] |
| `P_JOINT_FUNCTIONAL_SUCCESS_T_90` | 6 | 44 | 0.1364 | [0.0517, 0.2735] |

Naissances : 18. Extinctions : 0. Atteignent S : 18. Atteignent P : 7. Echecs d'integrite : 0.

Delai de separation geometrique : mediane 112.0 pas (n=18). Duree maximale d'un episode S : 4999 pas.

Rapport de reponse X du centre le plus faible a `T_primary` : mediane 0.8247 (exigence 0.6321).

## 3. Sensibilite a la fraction de reponse

| fraction | B1 succes conjoint | B1 IC bas | B2 succes conjoint | B2 IC bas | n requis (B1, prudent, p0=0.05) |
|---|---|---|---|---|---|
| `T_50` | 14/44 = 0.3182 | 0.1861 | 14/44 = 0.3182 | 0.1861 | 35 |
| `T_primary` | 13/44 = 0.2955 | 0.1676 | 12/44 = 0.2727 | 0.1496 | 39 |
| `T_80` | 9/44 = 0.2045 | 0.0980 | 10/44 = 0.2273 | 0.1147 | 183 |
| `T_90` | 6/44 = 0.1364 | 0.0517 | 6/44 = 0.1364 | 0.0517 | None |

`FUNCTIONAL_THRESHOLD_SENSITIVITY = STABLE_THROUGH_T_80__NOT_DECISION_CAPABLE_AT_T_90_WITHIN_192`

the joint success rate declines monotonically and without a sign change across the band (B1: 0.3182 -> 0.2955 -> 0.2045 -> 0.1364). What degrades is the POWER to separate the rate from a null inside the 192-world budget, not the sign or the magnitude of the effect. At T_90 no null above 0.015 is separable conservatively, so no claim may be made at T_90 from a 192-world experiment.

## 4. Reconstruction directe de la fonction

`CLASS = DIRECT_FUNCTION_RECONSTRUCTIBLE`

La reponse X locale de chaque centre est **mesuree**, pas inferee. the observed second-centre response at the operator-derived time EXCEEDS the operator's own predicted fraction at both points, so the timing criterion is conservative rather than permissive.

## 5. Selection du point

Regle : maximise the minimum 95% lower confidence margin across functional maturation, lineage survival, third-centre control and X integrity.

| fraction | marge minimale B1 | marge minimale B2 | vainqueur |
|---|---|---|---|
| `T_50` | 0.1861 | 0.1861 | TIE |
| `T_primary` | 0.1676 | 0.1496 | B1 |
| `T_80` | 0.0980 | 0.1147 | B2 |
| `T_90` | 0.0517 | 0.0517 | TIE |

**Mise en garde honnete.** B1 and B2 are statistically indistinguishable (13/44 vs 12/44 under the primary criterion). The frozen primary criterion selects B1; the ordering is not stable across the whole band (B2 wins at T_80, the two tie at T_50 and T_90). The selection is therefore a defensible tie-break, not a demonstrated superiority.

## 6. Capacite de decision (§9)

| exigence | constat | verdict |
|---|---|---|
| functional success observed in more than isolated exceptional worlds | 13 of 44 worlds at B1 under the primary criterion | **PASS** |
| the conclusion is not destroyed by moving from 50% to the canonical e-folding | joint success moves 14 -> 13 of 44 | **PASS** |
| third-centre-before-function risk is not dominant | 0 of 44 | **PASS** |
| X integrity is acceptable | 44 of 44 | **PASS** |
| no interpolation is required | B1 is an exact executable parameter point already run by PQEC01 (kY=2.5118864315e-05, muY=9.2611872813e-05) | **PASS** |
| no architecture modification is required | NOT_ESTABLISHED | **PASS** |
| a fresh disjoint experiment separates the rate from a null within <= 192 worlds | at B1 under the primary criterion, conservative planning (95% lower bound p1=0.1676) needs n=39 against p0=0.05 and n=152 against p0=0.10 | **PASS** |

## 7. Le seuil 0.50 n'est pas herite

`CLASSIFICATION = ARBITRARY_DEVELOPMENTAL_THRESHOLD`

FLRS02 does not inherit >= 0.50 and does not quietly substitute a new threshold. The future direct experiment is instead formulated as an exact binomial hypothesis test and the decision-capable region of candidate probabilities is reported in FLRS02_POWER_ANALYSIS.json.

## 8. Test d'architecture (§11)

`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`

- **kY_forces_P_before_function** — NOT_OBSERVED — 0 of 44 at both points
- **muY_needed_to_control_centres_destroys_continuity** — NOT_OBSERVED — at B2 muY is essentially zero, lineage non-extinction is 1.000, and no third centre precedes function. There is no point at which controlling extra centres costs lineage continuity.
- **X_integrity_collapses_where_two_centre_episodes_are_common** — NOT_OBSERVED — integrity holds in 88 of 88 Phase-B worlds

- the physical inadequacy of the retired 16-step hold is NOT evidence of architecture failure.

## 9. Deux calculateurs independants (§14)

`INDEPENDENT_REANALYSES_AGREE` — 0 desaccords sur les champs exigeant un accord exact.

## 10. Limites enregistrees

**the 128 PQEC01 worlds are POST_OUTCOME_DEVELOPMENTAL_DATA. They are not confirmation.**

- 14 of the 88 Phase-B worlds (7 per point) were terminated by the runner at PREMATURE_THIRD_CENTRE. This is outcome-dependent truncation: what would have followed the third centre is unobserved. It does not bias P_THIRD_BEFORE_FUNCTION, which is observed directly, but it censors later development.
- 28 of 44 B1 worlds went extinct; those are genuine failures and are counted in the denominator of 44.
- the PQEC01 DISCOVERY/VALIDATION split is pooled here because one world is the unit and the split was an internal PQEC01 device; per-point splits are B1 29/15 and B2 28/16.
- the weak-centre X ratio is self-normalising (weaker centre over stronger). The A0 control supplies an absolute single-centre reference (mean local X within CORE_R = 61.7175) but its spread is wide (sd 25.1790), so the ratio is used as the criterion and the absolute level only as a diagnostic.

## 11. Ce que ceci n'etablit pas

- `H3_STATUS = NOT_TESTED`
- `REPRODUCTION_STATUS = NOT_TESTED`
- `HEREDITY_STATUS = NOT_TESTED`
- `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`
- `X_LAWSPEC_BASELINE = UNCHANGED`
- `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`
- `FOUNDER_SURVIVAL_GATE = rejected`
- `PARTICLE_GENEALOGY_REQUIRED = false`

