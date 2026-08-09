# ROUTE_E_DIRECT_EXCHANGE_FLUX_DECOMPOSITION_06 — rapport

**2026-08-09** · parent `29923e89abcb0ad20db660deee6cf949f3b81d25` ·
**0 appel moteur, 0 graine, 0 trajectoire** · tout provient des ledgers `DEV_05` ·
10/10 tests sans moteur · aucun artefact parent modifié.

---

## 1. Ce que le corrigendum change (détail dans `dev05_interpretive_corrigendum.md`)

`DECISION_CORRECTED = RATE_DEPENDENT_REPLACEMENT`. `DOSE_RANGE_INSUFFICIENT` ne vaut qu'à **L=32** ;
à L=24 la gamme n'est pas insuffisante, elle est **bornée par la rupture** entre Q400 et Q800.
`PLATEAU_ESTABLISHED = false`. L'opérateur : code `REIMPLEMENTED_PRESEAL`, instrumentation
`REDESIGNED`, sémantique physique `REDESIGNED_PRESEAL` **mais** démontrée identique sur états
gelés à 1,3·10⁻¹⁵ près, divergence dont la cause unique est isolée (bande de saturation 10⁻¹²
côté source ; en la retirant, l'écart tombe à 0,0 sur les 36 mêmes cas).

Vérifications de structure : `PAIR_IDENTITY = PASS` (110 paires vivantes, pire résidu
9,9·10⁻¹³) · `MATCHED_SHAM_HORIZONS = PASS` (le SHAM porte un instantané à chaque horizon
terminal) · `RISK_SET_HANDLING = PASS`.

## 2. Le mécanisme primaire : les événements sont **rejetés**

Le puits ne peut prendre que dans les cellules aval de `C256` encore dans la piste **et**
au-dessus du seuil 0,45. Cet ensemble éligible est minuscule — **médiane : 1 cellule par
événement** — et il s'épuise.

| taux de rejet d'événement | Q100 | Q200 | Q400 | Q800 | puits seul Q800 |
|---|---|---|---|---|---|
| L=24 | 0,000 | 0,000 | 0,175 | **0,406** | **0,948** |
| L=32 | 0,000 | 0,000 | 0,000 | **0,139** | **0,945** |

| retrait brut / M₂₅₆ | Q100 | Q200 | Q400 | Q800 | facteur pour ×8 de dose |
|---|---|---|---|---|---|
| L=24 | 0,287 | 0,403 | 0,625 | 0,672 | **×2,34** (29 % du linéaire) |
| L=32 | 0,236 | 0,297 | 0,415 | 0,699 | **×2,97** (37 % du linéaire) |

```
PRIMARY_MECHANISM = SIZE_NORMALIZED_FLUX_LIMIT
```

Multiplier la dose par 8 n'exécute pas 8× plus d'événements : à Q800/L=24, **260 événements sur
640 ne font rien du tout**. La dose planifiée n'est pas une dose délivrée.

**Et la source nourrit le puits.** Au calendrier Q800 identique, le bras couplé retire
**×1,63–1,65 plus** que le puits seul (0,676 vs 0,410 ; 0,701 vs 0,429) et n'est rejeté que
14–41 % du temps au lieu de 95 %. L'injection amont remonte les cellules aval au-dessus du seuil :
sans source, l'interface est morte après ~35 événements sur 640.

## 3. Décomposition appariée, bloc par bloc (médianes, fractions de M₂₅₆)

| L=24 | excès d'égression I | F présent | Δ ambiant | Δ masse totale | n |
|---|---|---|---|---|---|
| Q100 | 0,226 | 0,241 | **−0,005** | +0,004 | 9 |
| Q400 | 0,324 | 0,387 | **−0,021** | +0,039 | 9 |
| Q800 | 0,309 | 0,379 | **−0,020** | +0,051 | **2 (survivants)** |
| puits seul | 0,430 | 0,000 | **−0,123** | **−0,550** | 9 |

| L=32 | | | | | |
|---|---|---|---|---|---|
| Q100 | 0,207 | 0,205 | **−0,004** | −0,003 | 9 |
| Q800 | 0,339 | 0,399 | **−0,028** | +0,028 | 9 |
| puits seul | 0,451 | 0,000 | **−0,105** | −0,557 | 9 |
| source seule | **−0,130** | 0,446 | +0,083 | **+0,657** | 9 |

**`AMBIENT_DELTA` est négatif partout où la source agit.** L'ambiant n'assiste pas le turnover :
il est déplacé. `AMBIENT_ASSISTANCE = NOT_ESTABLISHED` — et un delta négatif ne prouve pas non
plus un remplacement causal de l'ambiant.

**La source seule *protège* l'incumbent** : excès d'égression **négatif** (−0,130), c'est-à-dire
plus d'incumbent retenu que le sham, pour une masse à 1,64. C'est de la croissance excessive avec
continuité (9/9 à L=32), pas une destruction ; à L=24 c'est une cohorte de rupture **9/9**.

## 4. Le destin des cohortes

| | washout F | part incumbent de la morsure | rétention terminale F | rétention de dérive |
|---|---|---|---|---|
| L=24 Q100 → Q800 | 0,002 → **0,219** | 0,962 → **0,714** | 0,834 → 0,575 | 0,905 → 1,003 |
| L=32 Q100 → Q800 | 0,000 → **0,263** | 0,979 → **0,668** | 0,877 → 0,574 | 0,932 → 1,003 |

`FRESH_SELF_WASHOUT_DOMINATED` est **soutenu mais second** : de Q100 à Q800, la limite de flux
coûte un facteur **2,7–3,4** et la baisse de la part incumbent un facteur **1,35–1,47**
supplémentaire. La rétention de dérive ≥ 0,90 partout : le washout est un phénomène de **phase
forcée**, pas de coast.

Les courbes de survie par cohorte `FRESH_EVENT` sont **impossibles** : `DEV_05` a agrégé les
provenances par événement en un champ `FRESH` unique (choix déclaré au protocole) et le ledger ne
porte aucune colonne par cohorte d'injection.

## 5. Cadence : le médiateur est mesuré à l'événement

À dose, quantum, premier et dernier temps de force **identiques** :

| morsure médiane du puits, par position dans la salve | 1 | 9 | 17 | 25 | 33 |
|---|---|---|---|---|---|
| burst (écart 4 pas), L=24 | **2,060** | 0,085 | 0,079 | 0,078 | 0,077 |
| uniforme (écart 16 pas), L=24 | 0,287 | 0,287 | 0,291 | 0,282 | 0,285 |
| burst, L=32 | **3,716** | 0,079 | 0,074 | 0,071 | 0,069 |
| uniforme, L=32 | 0,236 | 0,236 | 0,232 | 0,228 | 0,228 |

La capacité du puits s'effondre d'un facteur **24 à 47** dès le deuxième événement d'une salve et
ne se reconstitue pas en 4 pas ; elle se reconstitue intégralement en 16.

Différences appariées uniforme − burst à Q400, sur 9 blocs par taille :
`INCUMBENT_REMOVED_BY_SINK` **+9/9 aux deux tailles** · `FRESH_WASHOUT_FRACTION` **+9/9** ·
`FRESH_TERMINAL_RETENTION` **−9/9** · `CORE_256_SURVIVAL` **−9/9** · `I/I₀` −7/9 (L=24), **−9/9**
(L=32).

```
RATE_EFFECT_RELAXATION_COMPATIBLE
```

Et je **rejette** `RATE_EFFECT_SELF_WASHOUT_MEDIATED` : le washout va dans le sens **opposé** au
résultat — l'uniforme lave davantage sa propre source et obtient pourtant un meilleur turnover.
Le médiateur est la relaxation de capacité du puits, et ce lien est mesuré au niveau de
l'événement, pas inféré.

## 6. Échafaudage : présent, persistant, mais pas « noyau protégé »

`PERSISTENT_INCUMBENT_SCAFFOLD = true`, qualification **suivie dans le temps** : un amas incumbent
connecté non vide existe à **chaque pas échantillonné** dans **9/9 blocs de tous les bras**, y
compris `SINK_ONLY_Q800`.

Mais normalisée par la masse propre de chaque cohorte à `t256` — le noyau porte 63 % de `I₀`, la
coque 17 % — la survie donne :

| survie / masse t256 de la cohorte | CORE | INTER | BOUNDARY | CORE/BND |
|---|---|---|---|---|
| L=32 SHAM | 0,827 | 0,618 | 0,575 | **1,44×** |
| L=32 Q400 | 0,508 | 0,510 | 0,398 | 1,28× |
| L=32 Q800 | 0,421 | 0,464 | 0,369 | 1,14× |
| L=24 Q800 | 0,377 | 0,427 | 0,370 | **1,02×** |

Le forçage **aplatit** le gradient de profondeur, et le rapport est **maximal chez le SHAM**.
⇒ `EXCHANGEABLE_SHELL_WITH_PROTECTED_CORE = NOT_SUPPORTED`, `CORE_ACCESS_LIMITED = REJECTED`.

## 7. Ce que les données ne permettent toujours pas

L'opérateur couplé déplace une masse **nette exactement nulle** (pire |source − puits| =
4,3·10⁻¹⁴), donc toute variation de la masse suivie est dynamique **ou géométrique**. Or sous
forçage la piste **se translate de 4,5 à 6,3 cellules** entre `t256` et l'horizon, contre **0,08**
pour le SHAM — conséquence directe d'une géométrie qui retire en aval et ajoute en amont.

```
PHYSICAL_BOUNDARY_CROSSING_STATUS = NOT_RECONSTRUCTIBLE_FROM_SAVED_RAW
```

`mass_inside_frozen_C256`, `C256_to_Ct_overlap` et `boundary_site_turnover` n'ont jamais été
sauvegardés. L'ambiant qui apparaît dans la piste ne peut donc pas être séparé de la piste qui
balaie de l'ambiant immobile. Aucune assimilation n'est inférée d'une hausse de `A`.

La rupture à L=24 Q800 est un **événement de connectivité, pas un seuil de composition** : les 7
blocs perdus l'étaient entre t=7696 et 10880 à des compositions (`I/I₀` 0,36–0,42, `F/T`
0,37–0,43) indiscernables des 2 survivants (0,368/0,403 et 0,399/0,353).

```
ROUTE_E_VERDICT = NONE   ·   AUTONOMOUS_RENEWAL = NOT_TESTED
IDENTITY / INDIVIDUATION / LIFE = NOT_ESTABLISHED   ·   GENERALIZATION_BEYOND_LAW_16 = false
ORGANIZATION_PRESERVATION = NOT_TESTED
```
