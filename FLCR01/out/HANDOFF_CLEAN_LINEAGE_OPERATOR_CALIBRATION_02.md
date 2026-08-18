# ISING LIFE LAB — HANDOFF
## CLEAN-LINEAGE-OPERATOR-CALIBRATION-02 (CLOC02)
## Identifier le sous-opérateur spatial à deux centres, proprement

> Produit par `FOUNDER-VERSUS-LINEAGE-CONTINUITY-RECONCILIATION-01`.
> Disposition parente : `LINEAGE_CRITERION_SUPPORTED__OPERATOR_NOT_IDENTIFIED_FROM_PQEC01`.
> **Ne pas exécuter dans la session FLCR01.**

```
PARENT_PROGRAM        = FOUNDER-VERSUS-LINEAGE-CONTINUITY-RECONCILIATION-01
PRIMARY_CRITERION     = TWO_CENTRE_FUNCTIONAL_CONTINUITY
SUPPORTING_CRITERION  = LINEAGE_NON_EXTINCTION
FOUNDER_SURVIVAL_GATE = REJECTED (unsatisfiable a priori AND scientifically wrong)
ARCHITECTURE_CHANGE   = forbidden
NEW_SPECIES           = forbidden
X_LAWSPEC_BASELINE    = UNCHANGED
TOMMY_ACTION_REQUIRED = NONE
```

## 1. Le composant d'opérateur manquant — nommé exactement

**Ce n'est pas un champ manquant.** Toutes les covariables nécessaires sont déjà enregistrées dans
les 128 archives PQEC01 : classe d'exposition de la cellule de naissance, `nX`/`nSY`/`free`/pool de
candidats **locaux à chaque cellule `Y` occupée**, déplacement relatif à la source, durée de
co-localisation, distance de séparation et nombre de centres — tous à chaque pas. Le handoff
précédent les appelait « instrumentation supplémentaire » ; c'était faux, et c'est corrigé ici.

Le composant manquant est :

```
LE SOUS-OPÉRATEUR SPATIAL À DEUX CENTRES, EN FONCTION DE (kY, muY)
  (a) taux de formation de centre        : O ou C  ->  S
  (b) taux de maintien / dissolution     : S -> S  et  S -> C, O
  (c) taux d'apparition d'un 3ᵉ centre   : S -> P
```

**Pourquoi il n'est pas identifié :** il a été mesuré en **exactement deux points** d'un plan à
deux dimensions. La chaîne de Markov exacte ne peut pas le fournir : elle **compte** les `Y`, elle
ne les **place** pas. Le déficit est la **couverture en mondes à travers le plan** — un problème de
conception, pas d'instrumentation.

Mesures parentes à battre, aux deux seuls points disponibles :

```
                       B1                    B2
L3 deux centres        0,364 ± 0,073         0,409 ± 0,074      (seuil 0,50 — échoue aux deux)
L4 maintien >= 16 pas  0,364                 0,409
L5 pas de 3e centre    0,841                 0,841
durée de maintien : n = 380 épisodes, médiane 16 pas, moyenne 244, q90 615, max 4999
délai séparation  : médiane 111 pas (TAU_SEP gelé = 125)
```

## 2. Conception exigée

- **Couverture du plan.** Au moins **cinq** points `(kY, muY)` couvrant la région de continuité de
  lignée dérivée (`kY ∈ [1,6×10⁻⁵ ; 5,6×10⁻⁴]`, `muY ∈ [10⁻⁸ ; 1,2×10⁻³]`), choisis par une règle
  déterministe gelée, avec un nombre de mondes par point **dérivé** de la précision requise sur
  `L3` — pas décrété.
- **La durée de maintien est fortement asymétrique** (médiane 16, max 4999). Geler un **quantile**
  comme `H_hold`, jamais une moyenne, et déclarer lequel avant tout run.
- **L'unité est le monde.** Jamais le pas, la cellule ou la ligne d'événement.

## 3. Discipline imposée par ce qui a échoué dans PQEC01

- **Committer et hacher, avant le premier départ** : moteur, observateur, **runner**, **analyseur**,
  seuils, portes et manifeste. PQEC01 n'a haché que la conception et l'observateur ; deux
  correctifs d'analyse ont dû suivre l'ouverture des sorties de validation, dont un qui a fait
  passer un test de `z = −14,32` à `z = +1,16`.
- **Aucun correctif post-validation.** Si l'analyseur est gelé et haché, la question ne se pose plus.
- **Pare-feu sans variable corrélée au résultat.** `bytes`, `runtime` et `steps_recorded` sont
  monotones en durée de vie du monde, et la durée de vie *est* le résultat : corrélation mesurée
  `0,9992`. N'exposer qu'un drapeau de complétion et une somme de contrôle.
- **Appliquer réellement la partition** découverte/validation, en Phase A comme en Phase B. Dans
  PQEC01 elle a été gelée puis jamais appliquée.
- **Ne jamais grouper là où une strate inverse le signe.** La rétroaction `Y → X` apparente varie de
  **+1,1 % à +66,7 %** selon la comparaison choisie.

## 4. Rétroaction — à concevoir pour être identifiable, pas à re-mesurer telle quelle

PQEC01 ne peut pas estimer proprement la rétroaction : la survenue d'une naissance n'est pas
randomisée — elle est elle-même une conséquence de l'exposition qui pilote la production de `X` —
et l'arrêt dépend du résultat. CLOC02 doit **concevoir** l'identifiabilité : fenêtres d'analyse
identiques par construction, arrêt indépendant du résultat ou censure explicitement modélisée, et
une comparaison pré-spécifiée entre configurations `Y` à exposition appariée.

## 5. Dispositions terminales admissibles

```
TWO_CENTRE_OPERATOR_IDENTIFIED_ACROSS_THE_LINEAGE_REGION
TWO_CENTRE_OPERATOR_NOT_IDENTIFIED__NAMED_COMPONENT_STILL_MISSING
LINEAGE_REGION_EMPTY_UNDER_MEASURED_SPATIAL_RATES
CALIBRATION_TECHNICALLY_INVALID
```

Seule la première autorise à préenregistrer un test de confirmation disjoint. Aucune ne permet une
revendication de reproduction, d'hérédité ou de vie.

## 6. Statuts à reporter inconditionnellement

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
TOMMY_ACTION_REQUIRED         = NONE
```
