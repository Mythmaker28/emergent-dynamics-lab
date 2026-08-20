# FTCTR01 — REDERIVATION DE L'HORLOGE FONCTIONNELLE A DEUX CENTRES

**Statut de l'enregistrement : RECONSTRUIT** apres le retour en arriere du conteneur.
Chaque valeur ci-dessous est **recalculee depuis la source**, aucune n'est recopiee.

`NEW_ENGINE_RUNS = 0` — `NEW_WORLD_CONSTRUCTIONS = 0` — `NEW_SEEDS = 0` — `NEW_PARAMETER_POINTS = 0`

## 1. L'horloge de separation, exacte

| Quantite | Valeur |
|---|---|
| Variance de deplacement par axe et par pas | 0.0500000000 |
| `a_X` gele | 0.05 — **identique** |
| `D_relative` derive / gele | 0.0500000000 / 0.05 — **identique** |
| Etats transitoires / absorbants | 81 / 1215 |
| `E[tau]` methode A (solve lineaire) | 147.41803682844846 |
| `E[tau]` methode B (somme de survie) | 147.41803682844696 |
| Ecart entre methodes | 1.51e-12 — **accord** |
| Ecart-type (deux methodes, accord) | 105.4560703991 |
| Mediane / IQR | 118 / 74–190 |
| `TAU_SEP` gele | 125.0 |
| Rapport exact/gele | 1.1793442946 |
| Sous-estimation | **17.934 %** du gele (15.207 % de l'exact) |

## 2. Confrontation au dossier observe

| Quantite | n | mediane | moyenne | ecart-type | z vs exact |
|---|---|---|---|---|---|
| Delai de separation (`first_S` − premiere naissance) | 34 | 111 | 144.08823529412 | 112.85425507131 | -0.1720 |
| Franchissement `max_pair_dist > CORE_R` | 34 | 111 | 141.97058823529 | 112.40928606473 | — |

Sur 88 mondes, 34 atteignent deux centres spatiaux. L'attente exacte est **compatible** avec le dossier.

## 3. L'horloge de maturation — le resultat principal

| Quantite | Valeur |
|---|---|
| Temps de e-folding du champ X (exact) | 249.49966599831 |
| conforme a la valeur gelee | True |
| `N_X` stationnaire mesure (60 mondes PQEC01) | 149.07913 (ecart-type 63.54054) |
| Niveaux `pre_removal_level` des 3 bras R d'OBTC02 | [116.64, 101.14, 113.83] |

**Temps de maturation en fonction de la fraction de reponse choisie** (`t(f) = ln(1-f)/ln(1-muX)`) :

| fraction de reponse `f` | pas depuis le vide | facteur de deficit vs `H_HOLD` |
|---|---|---|
| 0.5000 | 172.93999 | **10.8087** |
| 0.6321 (un e-folding) | 249.49967 | **15.5937** |
| 0.8000 | 401.55422 | **25.0971** |
| 0.9000 | 574.49421 | **35.9059** |
| 0.9500 | 747.43420 | **46.7146** |
| 0.9900 | 1148.98842 | **71.8118** |

| Quantite | Valeur |
|---|---|
| `H_HOLD` employe par FLCR01 | 16.0 |
| Fraction du nuage X construite en `H_HOLD` pas | **6.2115 %** |
| **`SHORTFALL_FACTOR`** | **25.0971** |
| `P(episode S >= un e-folding)` sur 380 episodes | 0.155263 |

## 4. Audit du seuil historique « 101 naissances X acceptees »

La valeur 101.14 est le `pre_removal_level` d'**un seul bras** (`R/seed9302`) du test de dependance causale a la source d'OBTC02. Les trois bras R donnent [116.64, 101.14, 113.83] (moyenne 110.53667). Ce n'etait pas un seuil derive et il n'est pas defendable comme tel.

`AUDIT = NOT_DEFENSIBLE_AS_A_THRESHOLD__IT_IS_A_SINGLE_ARM_OBSERVATION`

## 5. Les six echelles de temps, distinguees

### `T_GEOMETRIC_FORMATION`

first step at which the toroidal min-image distance between two Y exceeds CORE_R = 5.0, i.e. the step the FLCR01 classifier first returns state S.

`STATUS = DERIVED_EXACTLY_AND_CONFIRMED_AGAINST_THE_RECORD`

### `T_X_MATURATION`

steps for a NEW centre to build its X cloud from empty to the level an established organiser holds.

`STATUS = DERIVED__BUT_THE_TARGET_LEVEL_IS_NOT_YET_A_QUALIFIED_THRESHOLD`

### `T_FUNCTIONAL_TWO_CENTRE`

T_GEOMETRIC_FORMATION + T_X_MATURATION — the step at which BOTH centres hold a matured X response, not merely a spatial separation.

`STATUS = NOT_MEASURED_IN_ANY_EXISTING_RECORD`

### `T_FUNCTIONAL_HOLD`

duration for which the two matured centres must both persist.

`STATUS = UNDERSPECIFIED_BY_MORE_THAN_AN_ORDER_OF_MAGNITUDE`

### `T_THIRD_CENTRE`

step at which a third spatial centre appears (classifier state P) after state S was reached.

`STATUS = MEASURED__ORDERING_RELATIVE_TO_FUNCTION_IS_NOT_YET_DEFINED`

### `T_LINEAGE_EXTINCTION`

step at which Y reaches zero (classifier state E).

`STATUS = MEASURED_PER_WORLD_IN_THE_PQEC01_RECORD__NOT_A_LIMITING_TIMESCALE_AT_THIS_POINT`

## 6. Ce que ceci n'etablit pas

- `H3_STATUS = NOT_TESTED`
- `REPRODUCTION_STATUS = NOT_TESTED`
- `HEREDITY_STATUS = NOT_TESTED`
- `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`
- `X_LAWSPEC_BASELINE = UNCHANGED`
- `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`
- `FOUNDER_SURVIVAL_GATE = rejected (inherited from FLCR01, unchanged)`
- `PARTICLE_GENEALOGY_REQUIRED = false (inherited from FLCR01, unchanged)`

## 7. Ecarts par rapport a l'execution detruite

- **SD_tau** — enregistre : `104.0536` ; reconstruit : `105.45607039909953`. the reconstructed value is confirmed by two independent exact methods (linear solve of (I-Q)m2 = 1 + 2 Q m1, and the survival identity E[t^2] = sum_t (2t+1) P(tau>t)) which agree to machine precision; the earlier figure is superseded
- **maturation_build_time** — enregistre : `451.6 steps / SHORTFALL 28.2` ; reconstruit : `401.55422159731904`. the earlier figure pinned maturation to ONE implicit response fraction (101/120.845 = 0.8358). That is exactly the step the mission forbids taking silently. This reconstruction reports the maturation time as an explicit function of the chosen response fraction f. Even at the most permissive f = 0.50 the shortfall factor is 10.8087, and at f = 0.80 it is 25.0971. The conclusion — H_HOLD = 16 is short by at least an order of magnitude — holds for EVERY f on the grid and does not depend on the choice.
- **z_scores** — enregistre : `[-0.187, -0.305]` ; reconstruit : `[-0.17204413385908762, -0.2825728354686396]`. both are far inside 2 sigma; the qualitative conclusion (exact clock consistent with the record) is unchanged

